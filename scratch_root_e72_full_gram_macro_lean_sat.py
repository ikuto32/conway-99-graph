"""Lean support-specific exact SAT for canonical E72 full-Gram macros.

This version reuses ``build_shared_cnf`` so ordinary fibres and all overlap
blocks incident with them are constants.  It selector-gates only exceptional
internal states and the complete exceptional block-total profile.  Thus no
vertex-level overlap graph is enumerated and the exact CNF is substantially
smaller than the unrestricted 817k-variable formulation.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import coordinates, verify
from scratch_incremental_local_exact_sat import build_shared_cnf
import scratch_root_e72_full_gram_macro_sat as generic
from scratch_root_e73_q4_port_census import FIBRE_STATES


def normalized_source(row: dict, source_row_index: int) -> dict:
    return {
        "input_path": str(generic.PORT),
        "selection": {"source_row_index": source_row_index},
        "support_form": f"E72-source{source_row_index}-full-Gram-macro",
        "supports_in_fibre_order": tuple(
            tuple(item["support"]) for item in row["exceptional_supports"]
        ),
        # build_shared_cnf requires a nonempty representative list only to
        # construct optional complete assumptions.  Those assumptions are
        # deliberately ignored; our macro selectors below fix the local data.
        "representatives": [{
            "branch_index": 0,
            "representative_id": "unused-empty-placeholder",
            "orbit_size": 1,
            "present_edges": frozenset(),
        }],
    }


def build(source_row_index: int, redundant_bp: bool = False) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    row, port_raw = generic.select_row(source_row_index)
    state_orbits, orbit_audit = generic.state_orbit_audit(row)
    branches, macro_audit = generic.canonical_macros(
        source_row_index, row, state_orbits
    )
    assert branches
    source = normalized_source(row, source_row_index)
    clauses, edge, edge_variables, full_variables, unused, shared_meta = build_shared_cnf(source)
    assert len(unused) == 1
    assert unused[0]["positive_assumptions"] == 0

    labels, label_index, canonical_variables, _canonical_edge = coordinates()
    assert canonical_variables == full_variables
    exceptional_supports = source["supports_in_fibre_order"]
    fibres = {
        support: tuple(
            label_index[generic.local_label(support, bits)] for bits in generic.BITS
        )
        for support in generic.SUPPORTS
    }
    selectors = list(range(
        shared_meta["variables"] + 1,
        shared_meta["variables"] + 1 + len(branches),
    ))
    clauses.append(selectors)
    pool = IDPool(start_from=selectors[-1] + 1)

    # BP already implies these 84*(3+7) equalities.  Re-exposing them is a
    # logically redundant propagation layer: failed partial neighbourhoods
    # become visible without resolving across fourteen overlapping BP rows.
    redundant_started = len(clauses)
    redundant_top_started = pool.top
    redundant_equalities = 0

    def add_redundant_exact(expressions, wanted):
        nonlocal redundant_equalities
        expressions = tuple(expressions)
        fixed = sum(value is True for value in expressions)
        literals = [value for value in expressions if type(value) is int]
        target = wanted - fixed
        assert 0 <= target <= len(literals)
        if literals:
            clauses.extend(CardEnc.equals(
                lits=literals, bound=target, vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses)
        else:
            assert target == 0
        redundant_equalities += 1

    for u in (range(84) if redundant_bp else ()):
        label = labels[u]
        all_values = [edge(u, v) for v in range(84) if v != u]
        shared_values = [
            edge(u, v) for v, other in enumerate(labels)
            if u != v and set(label) & set(other)
        ]
        disjoint_values = [
            edge(u, v) for v, other in enumerate(labels)
            if u != v and not (set(label) & set(other))
        ]
        assert len(all_values) == 83 and len(shared_values) == 22 and len(disjoint_values) == 61
        add_redundant_exact(all_values, 12)
        add_redundant_exact(shared_values, 2)
        add_redundant_exact(disjoint_values, 10)
        support_groups = {symbol // 2 for symbol in label}
        for group in range(7):
            values = [
                edge(u, v) for v, other in enumerate(labels)
                if u != v and any(symbol // 2 == group for symbol in other)
            ]
            assert len(values) in (23, 24)
            add_redundant_exact(values, 2 if group in support_groups else 4)
    assert redundant_equalities == (840 if redundant_bp else 0)
    redundant_clauses = len(clauses) - redundant_started
    redundant_auxiliary_variables = pool.top - redundant_top_started

    branch_rows = []
    for branch, selector in zip(branches, selectors):
        before_clauses = len(clauses)
        before_top = pool.top
        internal_literals = []
        positive_internal = 0
        for support, deficit, state_index in zip(
            exceptional_supports,
            (int(item["deficit"]) for item in row["exceptional_supports"]),
            branch["state_indices"],
        ):
            fibre = fibres[support]
            chosen = {
                tuple(sorted(pair))
                for pair in FIBRE_STATES[deficit][state_index]["edges"]
            }
            assert len(chosen) == 4 - deficit
            for left, right in generic.PAIR_POSITIONS:
                variable = edge(fibre[left], fibre[right])
                assert type(variable) is int
                literal = variable if (left, right) in chosen else -variable
                internal_literals.append(literal)
                positive_internal += literal > 0
                clauses.append([-selector, literal])
        assert len(internal_literals) == 6 * len(exceptional_supports)

        cardinality_clauses = 0
        for left_index, right_index, target in branch["all_exceptional_block_totals"]:
            left = exceptional_supports[left_index]
            right = exceptional_supports[right_index]
            literals = tuple(edge(u, v) for u in fibres[left] for v in fibres[right])
            assert all(type(value) is int for value in literals)
            assert len(literals) == len(set(literals)) == 16
            encoded = CardEnc.equals(
                lits=list(literals), bound=target, vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
            clauses.extend([-selector, *clause] for clause in encoded)
            cardinality_clauses += len(encoded)
        branch = dict(branch)
        branch.update({
            "selector": selector,
            "internal_literal_implications": len(internal_literals),
            "positive_internal_edges": positive_internal,
            "block_cardinality_equalities": len(branch["all_exceptional_block_totals"]),
            "block_cardinality_encoding_clauses": cardinality_clauses,
            "gated_clauses": len(clauses) - before_clauses,
            "auxiliary_variables": pool.top - before_top,
        })
        branch_rows.append(branch)

    variables = max(selectors[-1], pool.top)
    cnf_path = Path(f"scratch_root_e72_source{source_row_index}_lean_full_gram_macro.cnf")
    temporary = cnf_path.with_suffix(cnf_path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    temporary.replace(cnf_path)
    cnf_audit = generic.cnf_audit(cnf_path)
    assert cnf_audit["declared_variables"] == variables
    assert cnf_audit["declared_clauses"] == len(clauses)
    cnf_audit["sha256"] = generic.sha256(cnf_path)

    fixed_true_full_variables = []
    for (u, v), full_variable in sorted(full_variables.items()):
        value = edge(u, v)
        if value is True:
            fixed_true_full_variables.append(full_variable)
        elif value is False:
            continue
        else:
            assert type(value) is int and edge_variables[(u, v)] == value
    assert len(fixed_true_full_variables) == shared_meta["ordinary_c4_fibre_count"] * 4

    result = {
        "status": "BUILD_COMPLETE",
        "model": "lean selector-gated exact E72 full-Gram macro CNF",
        "source_row_index": source_row_index,
        "source": str(generic.PORT),
        "source_sha256": generic.sha256(generic.PORT),
        "partition": row["partition"],
        "compression_orbit_index": row["compression_orbit_index"],
        "support_orbit_size": row["support_orbit_size"],
        "exceptional_supports": row["exceptional_supports"],
        "state_orbit_audit": orbit_audit,
        "macro_audit": macro_audit,
        "shared_exact_cnf_meta": shared_meta,
        "unused_placeholder_assumptions_applied": False,
        "selector_at_least_one_clauses": 1,
        "redundant_BP_consequence_layer_enabled": redundant_bp,
        "redundant_BP_consequence_equalities": redundant_equalities,
        "redundant_BP_consequence_clauses": redundant_clauses,
        "redundant_BP_consequence_auxiliary_variables": redundant_auxiliary_variables,
        "macro_branches": len(branch_rows),
        "branches": branch_rows,
        "edge_variables": len(edge_variables),
        "fixed_true_full_edge_variables": fixed_true_full_variables,
        "cnf": str(cnf_path),
        "cnf_audit": cnf_audit,
        "overlap_graphs_enumerated": 0,
        "direct_99_vertex_verification_on_sat": True,
        "claim_boundary": (
            "This exact CNF covers the full-Gram-passing canonical macros for one "
            "E72 source row. Upstream census and Gram completeness remain separate."
        ),
    }
    build_path = Path(f"scratch_root_e72_source{source_row_index}_lean_full_gram_macro_build.json")
    generic.atomic_json(build_path, result)
    return result


def translate_sat_model(source_row_index: int, model) -> set[int]:
    row, _raw = generic.select_row(source_row_index)
    source = normalized_source(row, source_row_index)
    _clauses, edge, edge_variables, full_variables, _unused, _meta = build_shared_cnf(source)
    positive_model = {literal for literal in model if literal > 0}
    answer = {
        full_variables[key] for key, variable in edge_variables.items()
        if variable in positive_model
    }
    for key, full_variable in full_variables.items():
        if edge(*key) is True:
            answer.add(full_variable)
    return answer


def solve(source_row_index: int, conflicts: int, per_branch: bool,
          redundant_bp: bool, output: Path | None) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_doc = build(source_row_index, redundant_bp=redundant_bp)
    build_path = Path(f"scratch_root_e72_source{source_row_index}_lean_full_gram_macro_build.json")
    cnf_path = Path(build_doc["cnf"])
    mode = "branches" if per_branch else "aggregate"
    if output is None:
        output = Path(
            f"scratch_root_e72_source{source_row_index}_lean_full_gram_macro_{mode}_"
            + (f"c{conflicts}.json" if conflicts else "terminal.json")
        )
    started = time.monotonic()
    formula = CNF(from_file=str(cnf_path))
    loaded = time.monotonic()
    solver = Solver(name="cadical195", bootstrap_with=formula.clauses)
    solver_loaded = time.monotonic()
    records = []
    verified_solution = None
    try:
        selected = build_doc["branches"] if per_branch else [None]
        for item in selected:
            assumptions = [item["selector"]] if item is not None else []
            before = solver.accum_stats()
            branch_started = time.monotonic()
            if conflicts:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited(assumptions=assumptions, expect_interrupt=True)
            else:
                answer = solver.solve(assumptions=assumptions)
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            record = {
                "macro_branch_index": item["macro_branch_index"] if item is not None else None,
                "selector": item["selector"] if item is not None else None,
                "labelled_state_matching_coverage": (
                    item["labelled_state_matching_coverage"] if item is not None
                    else build_doc["macro_audit"]["passing_labelled_state_matching_coverage"]
                ),
                "status": status,
                "solve_seconds": round(time.monotonic() - branch_started, 6),
                "stats_delta": {
                    key: int(after.get(key, 0)) - int(before.get(key, 0))
                    for key in sorted(set(before) | set(after))
                },
                "stats_cumulative": after,
            }
            if answer is False and assumptions:
                core = tuple(solver.get_core() or ())
                assert core and set(core) <= set(assumptions)
                record["assumption_core"] = list(core)
            elif answer is True:
                positive = translate_sat_model(source_row_index, solver.get_model())
                verification = verify(positive)
                assert verification["ok"], "SAT model failed direct 99-vertex verification"
                record["direct_99_vertex_verification"] = {
                    key: value for key, value in verification.items() if key != "edges"
                }
                record["positive_full_edge_variables"] = sorted(positive)
                verified_solution = verification
            records.append(record)
            partial = make_result(
                source_row_index, conflicts, per_branch, build_doc, build_path,
                cnf_path, started, loaded, solver_loaded, records, verified_solution,
            )
            generic.atomic_json(output, partial)
            print(json.dumps({
                "macro_branch_index": record["macro_branch_index"],
                "status": status,
                "coverage": record["labelled_state_matching_coverage"],
                "solve_seconds": record["solve_seconds"],
                "conflicts": record["stats_delta"].get("conflicts"),
            }, sort_keys=True), flush=True)
            if verified_solution is not None:
                generic.atomic_json(
                    Path(f"scratch_root_e72_source{source_row_index}_lean_verified_solution.json"),
                    verified_solution,
                )
                break
    finally:
        solver.delete()
    result = make_result(
        source_row_index, conflicts, per_branch, build_doc, build_path, cnf_path,
        started, loaded, solver_loaded, records, verified_solution,
    )
    generic.atomic_json(output, result)
    return result


def make_result(source_row_index, conflicts, per_branch, build_doc, build_path,
                cnf_path, started, loaded, solver_loaded, records, verified_solution):
    expected = build_doc["macro_branches"] if per_branch else 1
    complete = len(records) == expected or verified_solution is not None
    status = (
        "SAT" if verified_solution is not None
        else "UNSAT" if complete and all(row["status"] == "UNSAT" for row in records)
        else "UNKNOWN" if complete else "IN_PROGRESS"
    )
    return {
        "status": status,
        "model": build_doc["model"],
        "mode": "per_branch" if per_branch else "aggregate",
        "source_row_index": source_row_index,
        "build": str(build_path),
        "build_sha256": generic.sha256(build_path),
        "cnf": str(cnf_path),
        "cnf_sha256": generic.sha256(cnf_path),
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget_per_call": conflicts or None,
        "parse_seconds": round(loaded - started, 6),
        "solver_load_seconds": round(solver_loaded - loaded, 6),
        "checkpoint_complete": complete,
        "completed_calls": len(records),
        "macro_branches": build_doc["macro_branches"],
        "direct_unsat": sum(row["status"] == "UNSAT" for row in records),
        "unknown": sum(row["status"] == "UNKNOWN" for row in records),
        "sat": sum(row["status"] == "SAT" for row in records),
        "terminal_labelled_state_matching_coverage": (
            sum(row["labelled_state_matching_coverage"] for row in records if row["status"] in ("UNSAT", "SAT"))
            if per_branch else (
                build_doc["macro_audit"]["passing_labelled_state_matching_coverage"]
                if records and records[0]["status"] in ("UNSAT", "SAT") else 0
            )
        ),
        "total_labelled_state_matching_coverage": build_doc["macro_audit"]["passing_labelled_state_matching_coverage"],
        "records": records,
        "verified_99_vertex_solution": verified_solution is not None,
        "formal_proof_certificate": None,
        "claim_boundary": "UNSAT is computational until an external proof is checked.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-row-index", type=int, required=True)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--per-branch", action="store_true")
    parser.add_argument("--conflicts", type=int, default=100000)
    parser.add_argument("--redundant-bp", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.build:
        result = build(args.source_row_index, redundant_bp=args.redundant_bp)
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "macro_branches": result["macro_branches"],
            "coverage": result["macro_audit"]["passing_labelled_state_matching_coverage"],
            "variables": result["cnf_audit"]["declared_variables"],
            "clauses": result["cnf_audit"]["declared_clauses"],
        }, sort_keys=True))
    elif args.solve or args.per_branch:
        result = solve(
            args.source_row_index, args.conflicts, args.per_branch,
            args.redundant_bp, args.output,
        )
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "mode": result["mode"],
            "direct_unsat": result["direct_unsat"],
            "unknown": result["unknown"],
            "sat": result["sat"],
            "terminal_coverage": result["terminal_labelled_state_matching_coverage"],
            "total_coverage": result["total_labelled_state_matching_coverage"],
        }, sort_keys=True))
    else:
        parser.error("choose --build, --solve, or --per-branch")


if __name__ == "__main__":
    main()
