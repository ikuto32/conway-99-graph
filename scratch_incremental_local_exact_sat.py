"""Incremental exact SAT lift for local exceptional-fibre representatives.

The CNF is built once for one fixed set of exceptional supports.  Unlike the
older per-representative builders, every candidate edge

* inside an exceptional fibre, and
* between two overlapping exceptional fibres

is a SAT variable.  A local representative is selected only by a complete
set of positive/negative assumptions on those variables.  All disjoint
support blocks, all BP=PA0 equations, and all 3486 outer-pair equalities are
shared by every branch and loaded into one incremental CaDiCaL instance.

Input schema
------------
The default input is ``scratch_general_e77_local_reps.json``.  A normalized
record has ``supports_in_fibre_order``, ``local_vertex_order``, and
``representatives``.  Each representative supplies either
``present_edges_outer_indices_zero_based`` or ``local_graph_edges``.  A file
may contain that record directly, under ``record``, or in ``records`` (select
with ``--record-index``).  An E76 representative generator can therefore use
the same schema without changing this encoder.

There are deliberately no redundant support-aggregate rows in this model.
UNSAT answers are computational unless accompanied by a separately checked
proof certificate; this script does not generate one and never writes
``submission.txt``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import coordinates, verify


DEFAULT_INPUT = Path("scratch_general_e77_local_reps.json")
DEFAULT_OUTPUT = Path("scratch_incremental_e77_exact_sat.json")
GROUPS = tuple(range(7))
ALL_SUPPORTS = tuple(itertools.combinations(GROUPS, 2))


def select_record(document, record_index):
    if "record" in document:
        if record_index not in (None, 0):
            raise ValueError("a singleton 'record' input only accepts --record-index 0")
        return document["record"], {"container": "record", "record_index": 0}
    if "records" in document:
        if record_index is None:
            if len(document["records"]) != 1:
                raise ValueError("input has multiple records; pass --record-index")
            record_index = 0
        return document["records"][record_index], {
            "container": "records", "record_index": record_index
        }
    if all(key in document for key in (
        "supports_in_fibre_order", "local_vertex_order", "representatives"
    )):
        if record_index not in (None, 0):
            raise ValueError("a direct record only accepts --record-index 0")
        return document, {"container": "direct", "record_index": 0}
    raise ValueError("input does not contain a normalized local representative record")


def labels_to_outer_edges(raw_edges, label_index):
    answer = []
    for raw_left, raw_right in raw_edges:
        left = tuple(raw_left)
        right = tuple(raw_right)
        if left not in label_index or right not in label_index:
            raise ValueError(f"unknown outer label in local edge: {left}, {right}")
        answer.append(tuple(sorted((label_index[left], label_index[right]))))
    return answer


def normalize_source(path, record_index=None):
    document = json.loads(path.read_text(encoding="utf-8"))
    raw, selection = select_record(document, record_index)
    labels, label_index, _full_variables, _full_edge = coordinates()
    supports = tuple(tuple(sorted(map(int, support))) for support in raw["supports_in_fibre_order"])
    if len(supports) != len(set(supports)):
        raise ValueError("exceptional supports are not distinct")
    if not supports or any(support not in ALL_SUPPORTS for support in supports):
        raise ValueError("invalid exceptional support")
    exceptional = frozenset(supports)
    outer_supports = tuple(
        tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels
    )
    expected_local_vertices = {
        u for u, support in enumerate(outer_supports) if support in exceptional
    }
    supplied_local_vertices = {
        int(item["outer_index_zero_based"]) for item in raw["local_vertex_order"]
    }
    if supplied_local_vertices != expected_local_vertices:
        raise ValueError("local_vertex_order is not exactly the exceptional-fibre union")
    for item in raw["local_vertex_order"]:
        outer = int(item["outer_index_zero_based"])
        if tuple(item["symbol_label"]) != tuple(labels[outer]):
            raise ValueError("local vertex label/index mismatch")

    representatives = []
    for branch_index, representative in enumerate(raw["representatives"]):
        if "present_edges_outer_indices_zero_based" in representative:
            edges = [
                tuple(sorted(map(int, edge)))
                for edge in representative["present_edges_outer_indices_zero_based"]
            ]
        elif "local_graph_edges" in representative:
            edges = labels_to_outer_edges(representative["local_graph_edges"], label_index)
        else:
            raise ValueError(f"representative {branch_index} has no supported edge field")
        if len(edges) != len(set(edges)) or any(u == v for u, v in edges):
            raise ValueError(f"representative {branch_index} has duplicate/loop edges")
        representatives.append({
            "branch_index": branch_index,
            "representative_id": representative.get(
                "representative_id", representative.get("representative_index", branch_index)
            ),
            "orbit_size": representative.get(
                "orbit_size", representative.get("multiplicity_in_enumeration")
            ),
            "present_edges": frozenset(edges),
        })
    if not representatives:
        raise ValueError("input has no representatives")
    return {
        "input_path": str(path),
        "selection": selection,
        "support_form": raw.get("support_form"),
        "supports_in_fibre_order": supports,
        "local_graph_count": raw.get("local_graph_count"),
        "declared_orbit_count": raw.get(
            "orbit_count_direct", raw.get("surviving_local_orbits", len(representatives))
        ),
        "representatives": representatives,
    }


def build_shared_cnf(source):
    """Build one support-specific CNF and all complete branch assumptions."""
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, _label_index, full_variables, _full_edge = coordinates()
    supports = tuple(
        tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels
    )
    signs = tuple(
        {symbol // 2: symbol % 2 for symbol in label} for label in labels
    )
    fibres = {
        support: tuple(u for u, value in enumerate(supports) if value == support)
        for support in ALL_SUPPORTS
    }
    assert all(len(vertices) == 4 for vertices in fibres.values())
    exceptional = frozenset(source["supports_in_fibre_order"])
    ordinary = frozenset(set(ALL_SUPPORTS) - set(exceptional))
    local_vertices = frozenset(
        u for support in exceptional for u in fibres[support]
    )

    pool = IDPool(start_from=1)
    edge_variables = {}
    local_edge_variables = {}
    disjoint_edge_variables = {}
    local_same_candidates = 0
    local_overlap_blocks = set()
    disjoint_blocks = set()
    for u, v in itertools.combinations(range(84), 2):
        A, B = supports[u], supports[v]
        key = (u, v)
        local = (
            (A == B and A in exceptional)
            or (A != B and bool(set(A) & set(B)) and A in exceptional and B in exceptional)
        )
        disjoint = not (set(A) & set(B))
        if not (local or disjoint):
            continue
        variable = pool.id(("edge", u, v))
        edge_variables[key] = variable
        if local:
            local_edge_variables[key] = variable
            if A == B:
                local_same_candidates += 1
            else:
                local_overlap_blocks.add(tuple(sorted((A, B))))
        else:
            disjoint_edge_variables[key] = variable
            disjoint_blocks.add(tuple(sorted((A, B))))
    assert len(disjoint_blocks) == 105
    assert len(disjoint_edge_variables) == 105 * 16
    assert local_same_candidates == len(exceptional) * 6

    def edge(u, v):
        if u == v:
            return False
        if u > v:
            u, v = v, u
        key = (u, v)
        if key in edge_variables:
            return edge_variables[key]
        A, B = supports[u], supports[v]
        if A == B:
            assert A in ordinary
            return sum(
                signs[u][group] != signs[v][group] for group in A
            ) == 1
        if set(A) & set(B):
            # Any overlap block incident with an ordinary C4 is zero.
            assert A in ordinary or B in ordinary
            return False
        raise AssertionError("every disjoint-support edge must be a variable")

    # Every representative fixes every local candidate, including absences.
    branch_assumptions = []
    local_candidates = frozenset(local_edge_variables)
    for representative in source["representatives"]:
        present = representative["present_edges"]
        if not present <= local_candidates:
            bad = sorted(present - local_candidates)
            raise ValueError(
                f"branch {representative['branch_index']} has non-local edges: {bad[:4]}"
            )
        assumptions = tuple(
            variable if key in present else -variable
            for key, variable in sorted(local_edge_variables.items())
        )
        positive = sum(value > 0 for value in assumptions)
        if positive != len(present):
            raise AssertionError("present local edge count mismatch")
        assignment_word = " ".join(map(str, assumptions)).encode("ascii")
        branch_assumptions.append({
            "branch_index": representative["branch_index"],
            "representative_id": representative["representative_id"],
            "orbit_size": representative["orbit_size"],
            "assumptions": assumptions,
            "assumption_count": len(assumptions),
            "positive_assumptions": positive,
            "negative_assumptions": len(assumptions) - positive,
            "assumption_sha256": hashlib.sha256(assignment_word).hexdigest().upper(),
        })

    clauses = []

    def exactly_one(literals):
        literals = list(literals)
        assert literals and all(type(value) is int for value in literals)
        clauses.append(literals)
        clauses.extend([-a, -b] for a, b in itertools.combinations(literals, 2))

    def at_most_one(literals):
        literals = list(literals)
        assert literals and all(type(value) is int for value in literals)
        clauses.extend([-a, -b] for a, b in itertools.combinations(literals, 2))

    # Exact ordinary-C4 consequences on all disjoint blocks.  Low-low blocks
    # remain unrestricted here.
    high_high_blocks = 0
    high_low_blocks = 0
    low_low_blocks = 0
    exact_one_rows = 0
    exact_one_columns = 0
    for A, B in sorted(disjoint_blocks):
        if A in ordinary and B in ordinary:
            high_high_blocks += 1
            for u in fibres[A]:
                exactly_one(edge(u, v) for v in fibres[B])
                exact_one_rows += 1
            for v in fibres[B]:
                # Row exactness supplies four edges, so column <=1 already
                # makes every column exact while avoiding redundant at-least.
                at_most_one(edge(u, v) for u in fibres[A])
                exact_one_columns += 1
        elif A in ordinary or B in ordinary:
            high_low_blocks += 1
            high, low = (A, B) if A in ordinary else (B, A)
            for v in fibres[low]:
                exactly_one(edge(u, v) for u in fibres[high])
                exact_one_columns += 1
        else:
            low_low_blocks += 1

    cardinality_equalities = 0
    empty_clauses = 0

    def add_exact(expressions, wanted):
        nonlocal cardinality_equalities, empty_clauses
        expressions = tuple(expressions)
        fixed = sum(value is True for value in expressions)
        literals = [value for value in expressions if type(value) is int]
        target = wanted - fixed
        cardinality_equalities += 1
        if target < 0 or target > len(literals):
            clauses.append([])
            empty_clauses += 1
        elif not literals:
            if target:
                clauses.append([])
                empty_clauses += 1
        else:
            clauses.extend(CardEnc.equals(
                lits=literals,
                bound=target,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses)

    # BP=PA0: all exact symbol quotas for every outer vertex.
    bp_equalities = 0
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            add_exact(
                [
                    edge(u, v)
                    for v, other in enumerate(labels)
                    if u != v and symbol in other
                ],
                wanted=1 if symbol in own or (symbol ^ 1) in own else 2,
            )
            bp_equalities += 1
    assert bp_equalities == 84 * 14

    product_variables = 0
    direct_product_terms = 0
    constant_product_terms = 0
    pair_target_histogram = CounterLike({1: 0, 2: 0})
    for u, v in itertools.combinations(range(84), 2):
        expressions = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            left = edge(u, w)
            right = edge(v, w)
            if left is False or right is False:
                continue
            if left is True and right is True:
                expressions.append(True)
                constant_product_terms += 1
            elif left is True:
                expressions.append(right)
                direct_product_terms += 1
            elif right is True:
                expressions.append(left)
                direct_product_terms += 1
            elif left == right:
                expressions.append(left)
                direct_product_terms += 1
            else:
                helper = pool.id(("and", u, v, w))
                # Equality requires both directions: helper <-> left & right.
                clauses.extend((
                    [-left, -right, helper],
                    [left, -helper],
                    [right, -helper],
                ))
                expressions.append(helper)
                product_variables += 1
        target = 2 - len(set(labels[u]) & set(labels[v]))
        pair_target_histogram[target] += 1
        add_exact(expressions, target)
    outer_pair_equalities = 84 * 83 // 2
    assert sum(pair_target_histogram.values()) == outer_pair_equalities == 3486

    meta = {
        "model": "shared exact local-representative CNF",
        "input": source["input_path"],
        "input_selection": source["selection"],
        "support_form": source["support_form"],
        "exceptional_supports": [list(support) for support in source["supports_in_fibre_order"]],
        "exceptional_fibre_count": len(exceptional),
        "ordinary_c4_fibre_count": len(ordinary),
        "local_vertex_count": len(local_vertices),
        "representative_count": len(branch_assumptions),
        "shared_build_count": 1,
        "incremental_solver_instance_count": 1,
        "local_edge_variables": len(local_edge_variables),
        "local_same_edge_variables": local_same_candidates,
        "local_overlap_blocks": len(local_overlap_blocks),
        "local_overlap_edge_variables": len(local_overlap_blocks) * 16,
        "disjoint_edge_variables": len(disjoint_edge_variables),
        "all_edge_variables": len(edge_variables),
        "disjoint_blocks": len(disjoint_blocks),
        "ordinary_ordinary_permutation_blocks": high_high_blocks,
        "ordinary_exceptional_one_sided_blocks": high_low_blocks,
        "exceptional_exceptional_unrestricted_disjoint_blocks": low_low_blocks,
        "exact_one_rows": exact_one_rows,
        "at_most_one_columns": exact_one_columns,
        "redundant_support_aggregate_rows": 0,
        "bp_equalities": bp_equalities,
        "outer_pair_equalities": outer_pair_equalities,
        "pair_target_histogram": dict(pair_target_histogram),
        "product_variables": product_variables,
        "direct_product_terms": direct_product_terms,
        "constant_product_terms": constant_product_terms,
        "cardinality_equalities": cardinality_equalities,
        "empty_clauses_before_assumptions": empty_clauses,
        "variables": pool.top,
        "clauses": len(clauses),
        "branch_assumption_summaries": [
            {key: value for key, value in row.items() if key != "assumptions"}
            for row in branch_assumptions
        ],
        "soundness_boundary": (
            "all local values are assumptions; no support-aggregate strengthening; "
            "UNSAT has no independently checked proof certificate"
        ),
    }
    return clauses, edge, edge_variables, full_variables, branch_assumptions, meta


class CounterLike(dict):
    """Tiny integer counter kept dependency-free and JSON-order-stable."""

    def __missing__(self, key):
        return 0


def stats_delta(before, after):
    return {
        key: after.get(key, 0) - before.get(key, 0)
        for key in sorted(set(before) | set(after))
    }


def selected_full_edges(model, edge, full_variables):
    positive = {literal for literal in model or () if literal > 0}
    return {
        identifier
        for pair, identifier in full_variables.items()
        if edge(*pair) is True
        or (type(edge(*pair)) is int and edge(*pair) in positive)
    }


def reference_statuses():
    paths = (
        Path("scratch_general_e77_exact_sat_portfolio.json"),
        Path("scratch_e77_sat_exact_portfolio.json"),
    )
    output = []
    for path in paths:
        if not path.exists():
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        rows = document.get("records", [])
        statuses = {
            int(row["branch_index"]): row["status"]
            for row in rows if "branch_index" in row
        }
        output.append({
            "path": str(path),
            "overall_status": document.get("status"),
            "branch_statuses": statuses,
        })
    return output


def atomic_write_json(path, document):
    """Replace a checkpoint only after the complete JSON has reached disk."""
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def result_status(records, branch_count):
    if any(row["status"] == "SAT" for row in records):
        return "SAT"
    if len(records) < branch_count:
        return "IN_PROGRESS"
    if all(row["status"] in ("UNSAT", "COVERED_UNSAT") for row in records):
        return "UNSAT"
    return "UNKNOWN"


def make_result(
    source, meta, references, records, build_seconds, load_seconds,
    conflict_budget, solver_session_count,
):
    branch_count = meta["representative_count"]
    complete = len(records) == branch_count
    reference_matches = [
        row["matches_all_available_references"]
        for row in records
        if row["matches_all_available_references"] is not None
    ]
    return {
        "model": "single-instance incremental exact SAT over local representatives",
        "solver": "CaDiCaL 1.9.5 via PySAT assumptions",
        "input": source["input_path"],
        "input_selection": source["selection"],
        "support_form": source["support_form"],
        "build_seconds": round(build_seconds, 6),
        "solver_load_seconds": round(load_seconds, 6),
        "conflict_budget_per_branch": conflict_budget or None,
        "status": result_status(records, branch_count),
        "checkpoint_complete": complete,
        "completed_branch_count": len(records),
        "next_branch_index": None if complete else len(records),
        "solver_session_count": solver_session_count,
        "direct_solver_calls": sum(
            row.get("resolution") == "CADICAL" for row in records
        ),
        "direct_solver_unsat_count": sum(
            row["status"] == "UNSAT" for row in records
        ),
        "core_covered_unsat_count": sum(
            row["status"] == "COVERED_UNSAT" for row in records
        ),
        "unknown_count": sum(row["status"] == "UNKNOWN" for row in records),
        "all_available_reference_statuses_match": (
            all(reference_matches) if reference_matches else None
        ),
        "shared_cnf_meta": meta,
        "reference_portfolios": references,
        "records": records,
        "claim_boundary": (
            "The CNF and assumption coverage are exact and reusable.  CaDiCaL UNSAT "
            "answers have no emitted independently checked proof certificates."
        ),
    }


def solve_incrementally(source, conflict_budget=0, checkpoint_path=None, resume=False):
    build_started = time.monotonic()
    clauses, edge, _edge_variables, full_variables, branches, meta = build_shared_cnf(source)
    build_seconds = time.monotonic() - build_started
    from pysat.solvers import Solver

    load_started = time.monotonic()
    solver = Solver(name="cadical195", bootstrap_with=clauses)
    load_seconds = time.monotonic() - load_started
    # E77 is the only input for which the two historical portfolios are a
    # meaningful cross-check.  Reusing their branch numbers for E76 would be
    # a false comparison.
    references = reference_statuses() if source["support_form"] == "E77-orbit22" else []
    records = []
    solver_session_count = 1
    if resume and checkpoint_path is not None and Path(checkpoint_path).exists():
        previous = json.loads(Path(checkpoint_path).read_text(encoding="utf-8"))
        previous_meta = previous.get("shared_cnf_meta", {})
        if previous.get("support_form") != source["support_form"]:
            raise ValueError("resume checkpoint support_form mismatch")
        if previous_meta.get("exceptional_supports") != meta["exceptional_supports"]:
            raise ValueError("resume checkpoint exceptional supports mismatch")
        prior_summaries = previous_meta.get("branch_assumption_summaries", [])
        current_summaries = meta["branch_assumption_summaries"]
        if [row.get("assumption_sha256") for row in prior_summaries] != [
            row.get("assumption_sha256") for row in current_summaries
        ]:
            raise ValueError("resume checkpoint branch assumptions mismatch")
        records = list(previous.get("records", []))
        if [row.get("branch_index") for row in records] != list(range(len(records))):
            raise ValueError("resume checkpoint is not a completed branch prefix")
        if len(records) > len(branches):
            raise ValueError("resume checkpoint has too many branch records")
        solver_session_count = int(previous.get("solver_session_count", 1)) + 1
    try:
        for branch in branches[len(records):]:
            started = time.monotonic()
            branch_literals = frozenset(branch["assumptions"])
            covers = [
                prior for prior in records
                if prior.get("assumption_core")
                and frozenset(prior["assumption_core"]) <= branch_literals
            ]
            record = {
                key: value for key, value in branch.items() if key != "assumptions"
            }
            if covers:
                cover = min(covers, key=lambda row: len(row["assumption_core"]))
                core = tuple(cover["assumption_core"])
                record.update({
                    "status": "COVERED_UNSAT",
                    "logical_status": "UNSAT",
                    "resolution": "ASSUMPTION_CORE_CONTAINMENT",
                    "solve_seconds": round(time.monotonic() - started, 6),
                    "solver_session_index": solver_session_count,
                    "incremental_stats_delta": {},
                    "incremental_stats_cumulative": solver.accum_stats(),
                    "formal_proof_certificate": None,
                    "assumption_core_size": len(core),
                    "assumption_core_positive": sum(value > 0 for value in core),
                    "assumption_core_negative": sum(value < 0 for value in core),
                    "assumption_core": list(core),
                    "covered_by_branch_index": cover["branch_index"],
                    "core_containment_checked": True,
                })
                status = "COVERED_UNSAT"
            else:
                before = solver.accum_stats()
                if conflict_budget > 0:
                    solver.conf_budget(conflict_budget)
                    answer = solver.solve_limited(
                        assumptions=list(branch["assumptions"]), expect_interrupt=True
                    )
                else:
                    answer = solver.solve(assumptions=list(branch["assumptions"]))
                elapsed = time.monotonic() - started
                after = solver.accum_stats()
                status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
                record.update({
                    "status": status,
                    "logical_status": status,
                    "resolution": "CADICAL",
                    "solve_seconds": round(elapsed, 6),
                    "solver_session_index": solver_session_count,
                    "incremental_stats_delta": stats_delta(before, after),
                    "incremental_stats_cumulative": after,
                    "formal_proof_certificate": None,
                })
                if answer is False:
                    core = tuple(solver.get_core() or ())
                    assert set(core) <= set(branch["assumptions"])
                    record.update({
                        "assumption_core_size": len(core),
                        "assumption_core_positive": sum(value > 0 for value in core),
                        "assumption_core_negative": sum(value < 0 for value in core),
                        "assumption_core": list(core),
                    })
                elif answer is True:
                    selected = selected_full_edges(solver.get_model(), edge, full_variables)
                    checked = verify(selected)
                    record["verification"] = {
                        key: value for key, value in checked.items() if key != "edges"
                    }
                    record["verified_srg"] = bool(checked["ok"])
            expected = [
                reference["branch_statuses"].get(record["branch_index"])
                for reference in references
                if record["branch_index"] in reference["branch_statuses"]
            ]
            record["reference_statuses"] = expected
            record["matches_all_available_references"] = (
                all(value == record["logical_status"] for value in expected)
                if expected else None
            )
            records.append(record)
            partial = make_result(
                source, meta, references, records, build_seconds, load_seconds,
                conflict_budget, solver_session_count,
            )
            if checkpoint_path is not None:
                atomic_write_json(checkpoint_path, partial)
            print(json.dumps({
                "event": "branch_complete",
                "support_form": source["support_form"],
                "branch_index": record["branch_index"],
                "completed": len(records),
                "total": len(branches),
                "status": status,
                "solve_seconds": record["solve_seconds"],
                "conflicts": record["incremental_stats_delta"].get("conflicts"),
            }, sort_keys=True), flush=True)
    finally:
        solver.delete()
    return make_result(
        source, meta, references, records, build_seconds, load_seconds,
        conflict_budget, solver_session_count,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--record-index", type=int)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--conflict-budget", type=int, default=0)
    parser.add_argument(
        "--resume", action="store_true",
        help="continue after the completed prefix already stored in --output",
    )
    args = parser.parse_args()

    source = normalize_source(args.input, args.record_index)
    if args.build_only:
        started = time.monotonic()
        clauses, _edge, _variables, _full, branches, meta = build_shared_cnf(source)
        result = {
            "model": "build-only shared exact local-representative CNF",
            "build_seconds": round(time.monotonic() - started, 6),
            "shared_cnf_meta": meta,
            "branch_count": len(branches),
            "clauses_recount": len(clauses),
        }
    else:
        result = solve_incrementally(
            source,
            max(0, args.conflict_budget),
            checkpoint_path=args.output,
            resume=args.resume,
        )
    atomic_write_json(args.output, result)
    print(json.dumps({
        "status": result.get("status", "BUILD_ONLY"),
        "output": str(args.output),
        "build_seconds": result["build_seconds"],
        "variables": result["shared_cnf_meta"]["variables"],
        "clauses": result["shared_cnf_meta"]["clauses"],
        "local_edge_variables": result["shared_cnf_meta"]["local_edge_variables"],
        "records": [
            {
                "branch_index": row["branch_index"],
                "status": row["status"],
                "solve_seconds": row["solve_seconds"],
            }
            for row in result.get("records", [])
        ],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
