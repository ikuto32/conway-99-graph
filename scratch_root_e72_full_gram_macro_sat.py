"""Direct exact SAT for a full-Gram E72 macro row, without overlap enumeration.

The unrestricted rooted CNF is augmented with the exact ordinary-C4 support
consequences.  Each canonical macro branch gets a selector; that selector
gates every exceptional internal edge literal and an exact cardinality for
every exceptional--exceptional 4x4 block.  The overlap totals come from the
complete macro catalog and the disjoint totals from the independently derived
full Gram matrix.  A single at-least-one selector clause covers all branches.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

from scratch_general_exact_sat import CNF_PATH, coordinates, verify
import scratch_general_e72_q3_fast_expansion as fast
from scratch_root_e73_q4_port_census import FIBRE_STATES


PORT = Path("scratch_general_e72_q3_port_feasible_states.json")
CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FULL_GRAM = Path("scratch_theory_e72_macro_full_gram.json")
BASE_META = Path("scratch_general_exact_build.json")
GROUPS = tuple(range(7))
SUPPORTS = tuple(itertools.combinations(GROUPS, 2))
BITS = tuple(itertools.product((0, 1), repeat=2))
PAIR_POSITIONS = tuple(itertools.combinations(range(4), 2))
SIDES = frozenset(
    pair for pair in PAIR_POSITIONS
    if sum(BITS[pair[0]][axis] != BITS[pair[1]][axis] for axis in (0, 1)) == 1
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def local_label(support, bits):
    return tuple(sorted((2 * support[0] + bits[0], 2 * support[1] + bits[1])))


def cnf_audit(path: Path) -> dict:
    declared_variables = declared_clauses = None
    actual_clauses = unit_clauses = maximum_variable = 0
    with path.open("rb") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith(b"c"):
                continue
            if line.startswith(b"p"):
                fields = line.split()
                assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
                declared_variables, declared_clauses = map(int, fields[2:])
                continue
            literals = tuple(map(int, line.split()))
            assert literals and literals[-1] == 0 and 0 not in literals[:-1]
            actual_clauses += 1
            unit_clauses += len(literals) == 2
            if len(literals) > 1:
                maximum_variable = max(maximum_variable, max(map(abs, literals[:-1])))
    assert declared_variables is not None and actual_clauses == declared_clauses
    assert maximum_variable <= declared_variables
    return {
        "declared_variables": declared_variables,
        "declared_clauses": declared_clauses,
        "actual_clauses": actual_clauses,
        "unit_clauses": unit_clauses,
        "maximum_variable_seen": maximum_variable,
    }


def select_row(source_row_index: int) -> tuple[dict, bytes]:
    raw = PORT.read_bytes()
    document = json.loads(raw)
    matches = [
        row for row in document["rows"]
        if int(row.get("source_row_index", -1)) == source_row_index
    ]
    assert len(matches) == 1
    row = matches[0]
    assert row["locally_port_feasible_assignments"] == len(row["feasible_state_indices"])
    return row, raw


def state_orbit_audit(row: dict) -> tuple[tuple[dict, ...], dict]:
    geometry = fast.RowGeometry(row)
    raw_orbits = fast.state_orbits(row, geometry)
    orbits = tuple({
        "state_orbit_number": index,
        "state_indices": list(item["state_indices"]),
        "internal_mask_hex": hex(item["internal_mask"]),
        "state_orbit_size": item["weight"],
        "state_stabilizer_order": len(item["stabilizer"]),
        "Q": item["Q"],
    } for index, item in enumerate(raw_orbits))
    assert sum(item["state_orbit_size"] for item in orbits) == row["locally_port_feasible_assignments"]
    assert all(
        len(geometry.actions)
        == item["state_orbit_size"] * item["state_stabilizer_order"]
        for item in orbits
    )
    return orbits, {
        "feasible_labelled_states": row["locally_port_feasible_assignments"],
        "effective_weighted_actions": len(geometry.actions),
        "full_weighted_stabilizer": geometry.full_stabilizer,
        "state_orbits": len(orbits),
        "state_orbit_size_histogram": {
            str(key): value for key, value in sorted(
                Counter(item["state_orbit_size"] for item in orbits).items()
            )
        },
        "weighted_Q_histogram": {
            str(key): value for key, value in sorted(
                Counter({
                    q: sum(item["state_orbit_size"] for item in orbits if item["Q"] == q)
                    for q in {item["Q"] for item in orbits}
                }).items()
            )
        },
        "closure_partition_and_orbit_stabilizer_identities_verified": True,
    }


def canonical_macros(source_row_index: int, row: dict, state_orbits) -> tuple[list[dict], dict]:
    catalog_raw = CATALOG.read_bytes()
    catalog = json.loads(catalog_raw)
    all_entries = [
        item for item in catalog["macro_entries"]
        if int(item["source_row_index"]) == source_row_index
    ]
    canonical = [item for item in all_entries if item["signature_stabilizer_canonical"]]
    gram_raw = FULL_GRAM.read_bytes()
    gram = json.loads(gram_raw)
    gram_rows = [
        item for item in gram["rows"]
        if int(item["source_row_index"]) == source_row_index
    ]
    gram_by_key = {
        (item["state_orbit_number"], item["signature_stabilizer_orbit_number"]): item
        for item in gram_rows if item["signature_stabilizer_canonical"]
    }
    assert len(gram_by_key) == len(canonical)
    orbit_by_number = {item["state_orbit_number"]: item for item in state_orbits}
    branches = []
    rejected = []
    for entry in canonical:
        key = (entry["state_orbit_number"], entry["signature_stabilizer_orbit_number"])
        full = gram_by_key[key]
        state = orbit_by_number[entry["state_orbit_number"]]
        assert entry["state_indices"] == state["state_indices"]
        assert entry["state_orbit_size"] == state["state_orbit_size"]
        assert entry["state_stabilizer_order"] == state["state_stabilizer_order"]
        assert full["signature_orbit_labelled_coverage"] == entry["signature_orbit_labelled_coverage"]
        if not full["passes_full_unique_gram_checks"]:
            rejected.append({"key": list(key), "coverage": entry["signature_orbit_labelled_coverage"]})
            continue
        assert full["unique"] and full["solution_dimension"] == 0
        totals = {}
        overlap_rows = []
        disjoint_rows = []
        for left, right, raw_value in entry["overlap_block_totals"]:
            pair = (int(left), int(right))
            assert pair not in totals
            value = int(raw_value)
            totals[pair] = value
            overlap_rows.append([*pair, value])
        for left, right, raw_value in full["disjoint_exceptional_block_totals"]:
            pair = (int(left), int(right))
            assert pair not in totals
            value = int(raw_value)
            totals[pair] = value
            disjoint_rows.append([*pair, value])
        exceptional_count = len(row["exceptional_supports"])
        expected_pairs = set(itertools.combinations(range(exceptional_count), 2))
        assert set(totals) == expected_pairs
        supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
        assert all(set(supports[left]) & set(supports[right]) for left, right, _ in overlap_rows)
        assert all(not (set(supports[left]) & set(supports[right])) for left, right, _ in disjoint_rows)
        assert all(0 <= value <= 16 for value in totals.values())
        branches.append({
            "macro_branch_index": len(branches),
            "state_orbit_number": entry["state_orbit_number"],
            "signature_stabilizer_orbit_number": entry["signature_stabilizer_orbit_number"],
            "state_indices": entry["state_indices"],
            "Q": entry["Q"],
            "state_orbit_size": entry["state_orbit_size"],
            "state_stabilizer_order": entry["state_stabilizer_order"],
            "signature_stabilizer_orbit_size": entry["signature_stabilizer_orbit_size"],
            "labelled_state_matching_coverage": entry["signature_orbit_labelled_coverage"],
            "overlap_block_totals": overlap_rows,
            "disjoint_block_totals": disjoint_rows,
            "all_exceptional_block_totals": [
                [left, right, totals[(left, right)]] for left, right in sorted(totals)
            ],
        })
    signatures = {
        (tuple(branch["state_indices"]), tuple(tuple(row) for row in branch["all_exceptional_block_totals"]))
        for branch in branches
    }
    assert len(signatures) == len(branches)
    return branches, {
        "macro_catalog": str(CATALOG),
        "macro_catalog_sha256": hashlib.sha256(catalog_raw).hexdigest().upper(),
        "full_gram": str(FULL_GRAM),
        "full_gram_sha256": hashlib.sha256(gram_raw).hexdigest().upper(),
        "all_catalog_entries_for_source": len(all_entries),
        "canonical_catalog_entries_for_source": len(canonical),
        "full_gram_canonical_rows_for_source": len(gram_by_key),
        "full_gram_passing_macro_branches": len(branches),
        "full_gram_rejected_macro_branches": len(rejected),
        "full_gram_rejected": rejected,
        "passing_labelled_state_matching_coverage": sum(
            branch["labelled_state_matching_coverage"] for branch in branches
        ),
        "rejected_labelled_state_matching_coverage": sum(item["coverage"] for item in rejected),
        "all_block_total_profiles_complete_and_distinct": True,
    }


def exactly_one(literals) -> list[list[int]]:
    literals = tuple(literals)
    assert len(literals) == 4 and len(set(literals)) == 4
    return [list(literals)] + [
        [-left, -right] for left, right in itertools.combinations(literals, 2)
    ]


def build(source_row_index: int) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    row, port_raw = select_row(source_row_index)
    state_orbits, orbit_audit = state_orbit_audit(row)
    branches, macro_audit = canonical_macros(source_row_index, row, state_orbits)
    assert branches

    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    base_audit = cnf_audit(CNF_PATH)
    assert sha256(CNF_PATH) == base_meta["cnf_sha256"]
    assert base_audit["declared_variables"] == base_meta["variables"]
    assert base_audit["declared_clauses"] == base_meta["clauses"]
    assert base_audit["unit_clauses"] == 0

    _labels, index, _variables, edge = coordinates()
    exceptional_supports = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    exceptional = frozenset(exceptional_supports)
    ordinary = frozenset(set(SUPPORTS) - set(exceptional_supports))
    fibres = {
        support: tuple(index[local_label(support, bits)] for bits in BITS)
        for support in SUPPORTS
    }

    added_clauses = []
    ordinary_internal_units = 0
    for support in sorted(ordinary):
        fibre = fibres[support]
        for left, right in PAIR_POSITIONS:
            variable = edge(fibre[left], fibre[right])
            added_clauses.append([variable if (left, right) in SIDES else -variable])
            ordinary_internal_units += 1

    ordinary_overlap_zero_blocks = 0
    disjoint_block_types = Counter()
    ordinary_disjoint_exact_one_rows = 0
    for left, right in itertools.combinations(SUPPORTS, 2):
        common = bool(set(left) & set(right))
        if common and not (left in exceptional and right in exceptional):
            for u in fibres[left]:
                for v in fibres[right]:
                    added_clauses.append([-edge(u, v)])
            ordinary_overlap_zero_blocks += 1
        if common:
            continue
        kind = (
            "ordinary_ordinary" if left in ordinary and right in ordinary
            else "ordinary_exceptional" if left in ordinary or right in ordinary
            else "exceptional_exceptional"
        )
        disjoint_block_types[kind] += 1
        # Exact ordinary-C4 consequence used by the shared builder: every
        # vertex on the other side has exactly one neighbour in an ordinary
        # fibre.  For ordinary/ordinary, encode one direction exactly and the
        # other direction at-most-one (four edges already follow).
        if left in ordinary:
            for v in fibres[right]:
                added_clauses.extend(exactly_one(edge(u, v) for u in fibres[left]))
                ordinary_disjoint_exact_one_rows += 1
        if right in ordinary:
            for u in fibres[left]:
                literals = tuple(edge(u, v) for v in fibres[right])
                if left in ordinary:
                    added_clauses.extend(
                        [-a, -b] for a, b in itertools.combinations(literals, 2)
                    )
                else:
                    added_clauses.extend(exactly_one(literals))
                    ordinary_disjoint_exact_one_rows += 1
    assert sum(disjoint_block_types.values()) == 105

    selectors = list(range(
        base_audit["declared_variables"] + 1,
        base_audit["declared_variables"] + 1 + len(branches),
    ))
    added_clauses.append(selectors)
    pool = IDPool(start_from=selectors[-1] + 1)
    branch_summaries = []
    for branch, selector in zip(branches, selectors):
        before_clauses = len(added_clauses)
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
                tuple(sorted(pair)) for pair in FIBRE_STATES[deficit][state_index]["edges"]
            }
            assert len(chosen) == 4 - deficit
            for left, right in PAIR_POSITIONS:
                variable = edge(fibre[left], fibre[right])
                literal = variable if (left, right) in chosen else -variable
                internal_literals.append(literal)
                positive_internal += literal > 0
                added_clauses.append([-selector, literal])
        assert len(internal_literals) == len(exceptional_supports) * 6
        assert positive_internal == sum(4 - int(item["deficit"]) for item in row["exceptional_supports"])

        cardinality_clauses = 0
        target_histogram = Counter()
        for left_index, right_index, target in branch["all_exceptional_block_totals"]:
            left = exceptional_supports[left_index]
            right = exceptional_supports[right_index]
            literals = tuple(
                edge(u, v) for u in fibres[left] for v in fibres[right]
            )
            assert len(literals) == len(set(literals)) == 16
            encoded = CardEnc.equals(
                lits=list(literals), bound=target, vpool=pool, encoding=EncType.seqcounter
            ).clauses
            for clause in encoded:
                added_clauses.append([-selector, *clause])
            cardinality_clauses += len(encoded)
            target_histogram[target] += 1
        branch.update({
            "selector": selector,
            "internal_literal_implications": len(internal_literals),
            "positive_internal_edges": positive_internal,
            "block_cardinality_equalities": len(branch["all_exceptional_block_totals"]),
            "block_target_histogram": {
                str(key): value for key, value in sorted(target_histogram.items())
            },
            "block_cardinality_encoding_clauses": cardinality_clauses,
            "gated_clauses": len(added_clauses) - before_clauses,
            "auxiliary_variables": pool.top - before_top,
        })
        branch_summaries.append(branch)

    variables = max(selectors[-1], pool.top)
    clause_count = base_audit["declared_clauses"] + len(added_clauses)
    cnf_path = Path(f"scratch_root_e72_source{source_row_index}_full_gram_macro.cnf")
    temporary = cnf_path.with_suffix(cnf_path.suffix + f".{os.getpid()}.tmp")
    with CNF_PATH.open("rb") as source, temporary.open("wb") as target:
        old_header = source.readline().split()
        assert old_header == [
            b"p", b"cnf", str(base_audit["declared_variables"]).encode("ascii"),
            str(base_audit["declared_clauses"]).encode("ascii"),
        ]
        target.write(f"p cnf {variables} {clause_count}\n".encode("ascii"))
        shutil.copyfileobj(source, target, length=1 << 20)
        for clause in added_clauses:
            target.write((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
    temporary.replace(cnf_path)
    derived_audit = cnf_audit(cnf_path)
    assert derived_audit["declared_variables"] == variables
    assert derived_audit["declared_clauses"] == clause_count
    derived_audit["sha256"] = sha256(cnf_path)

    result = {
        "status": "BUILD_COMPLETE",
        "model": "selector-gated full exact E72 full-Gram macro CNF",
        "source_row_index": source_row_index,
        "source": str(PORT),
        "source_sha256": hashlib.sha256(port_raw).hexdigest().upper(),
        "partition": row["partition"],
        "compression_orbit_index": row["compression_orbit_index"],
        "support_orbit_size": row["support_orbit_size"],
        "exceptional_supports": row["exceptional_supports"],
        "exceptional_fibres": len(exceptional),
        "ordinary_c4_fibres": len(ordinary),
        "state_orbit_audit": orbit_audit,
        "macro_audit": macro_audit,
        "unrestricted_base_cnf": str(CNF_PATH),
        "unrestricted_base_cnf_sha256": sha256(CNF_PATH),
        "unrestricted_base_cnf_audit": base_audit,
        "historical_portfolio_branch_units_applied": False,
        "ordinary_internal_unit_clauses": ordinary_internal_units,
        "ordinary_overlap_zero_blocks": ordinary_overlap_zero_blocks,
        "disjoint_block_types": dict(disjoint_block_types),
        "ordinary_disjoint_exact_one_rows": ordinary_disjoint_exact_one_rows,
        "selector_at_least_one_clauses": 1,
        "macro_branches": len(branch_summaries),
        "branches": branch_summaries,
        "added_clauses": len(added_clauses),
        "cnf": str(cnf_path),
        "cnf_audit": derived_audit,
        "overlap_graphs_enumerated": 0,
        "direct_99_vertex_verification_on_sat": True,
        "claim_boundary": (
            "This formula covers only the full-Gram-passing canonical macro branches "
            f"recorded for E72 source row {source_row_index}. Upstream census and Gram "
            "exhaustiveness are external assumptions until separately formalized."
        ),
    }
    build_path = Path(f"scratch_root_e72_source{source_row_index}_full_gram_macro_build.json")
    atomic_json(build_path, result)
    return result


def solve(source_row_index: int, conflicts: int, output: Path | None) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_doc = build(source_row_index)
    build_path = Path(f"scratch_root_e72_source{source_row_index}_full_gram_macro_build.json")
    cnf_path = Path(build_doc["cnf"])
    if output is None:
        output = Path(
            f"scratch_root_e72_source{source_row_index}_full_gram_macro_"
            + (f"c{conflicts}.json" if conflicts else "terminal.json")
        )
    started = time.monotonic()
    formula = CNF(from_file=str(cnf_path))
    loaded = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        if conflicts:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited(expect_interrupt=True)
        else:
            answer = solver.solve()
        solved = time.monotonic()
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    verification = None
    selected_macros = []
    if answer is True:
        positive = {literal for literal in model if 0 < literal <= 3486}
        verification = verify(positive)
        assert verification["ok"], "SAT assignment failed direct 99-vertex verification"
        model_set = set(model)
        selected_macros = [
            branch["macro_branch_index"] for branch in build_doc["branches"]
            if branch["selector"] in model_set
        ]
        assert selected_macros
        solution = {key: value for key, value in verification.items()}
        solution["selected_macro_branches"] = selected_macros
        atomic_json(Path(f"scratch_root_e72_source{source_row_index}_verified_solution.json"), solution)
    result = {
        "status": status,
        "model": build_doc["model"],
        "source_row_index": source_row_index,
        "build": str(build_path),
        "build_sha256": sha256(build_path),
        "cnf": str(cnf_path),
        "cnf_sha256": sha256(cnf_path),
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget": conflicts or None,
        "termination": "solver_answer" if answer is not None else "conflict_budget",
        "parse_seconds": round(loaded - started, 6),
        "solve_seconds": round(solved - loaded, 6),
        "solver_stats": stats,
        "macro_branches": build_doc["macro_branches"],
        "labelled_state_matching_coverage": build_doc["macro_audit"]["passing_labelled_state_matching_coverage"],
        "selected_macro_branches": selected_macros,
        "direct_99_vertex_verification": (
            {key: value for key, value in verification.items() if key != "edges"}
            if verification is not None else None
        ),
        "formal_proof_certificate": None,
        "claim_boundary": (
            "UNSAT is computational until this exact CNF has an externally checked proof."
        ),
    }
    atomic_json(output, result)
    return result


def solve_per_branch(source_row_index: int, conflicts: int, output: Path | None) -> dict:
    """Probe each macro selector separately in one incremental solver."""
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_doc = build(source_row_index)
    build_path = Path(f"scratch_root_e72_source{source_row_index}_full_gram_macro_build.json")
    cnf_path = Path(build_doc["cnf"])
    if output is None:
        output = Path(
            f"scratch_root_e72_source{source_row_index}_full_gram_macro_branches_"
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
        for branch in build_doc["branches"]:
            selector = branch["selector"]
            before = solver.accum_stats()
            branch_started = time.monotonic()
            if conflicts:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited(assumptions=[selector], expect_interrupt=True)
            else:
                answer = solver.solve(assumptions=[selector])
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            record = {
                "macro_branch_index": branch["macro_branch_index"],
                "state_orbit_number": branch["state_orbit_number"],
                "signature_stabilizer_orbit_number": branch["signature_stabilizer_orbit_number"],
                "Q": branch["Q"],
                "labelled_state_matching_coverage": branch["labelled_state_matching_coverage"],
                "selector": selector,
                "status": status,
                "solve_seconds": round(time.monotonic() - branch_started, 6),
                "stats_delta": {
                    key: int(after.get(key, 0)) - int(before.get(key, 0))
                    for key in sorted(set(before) | set(after))
                },
                "stats_cumulative": after,
                "formal_proof_certificate": None,
            }
            if answer is False:
                core = tuple(solver.get_core() or ())
                assert core and set(core) <= {selector}
                record["assumption_core"] = list(core)
            elif answer is True:
                model = solver.get_model()
                positive = {literal for literal in model if 0 < literal <= 3486}
                verification = verify(positive)
                assert verification["ok"], "SAT assignment failed direct 99-vertex verification"
                record["direct_99_vertex_verification"] = {
                    key: value for key, value in verification.items() if key != "edges"
                }
                record["positive_edge_variables"] = sorted(positive)
                verified_solution = verification
            records.append(record)
            partial = branch_result(
                source_row_index, conflicts, build_doc, build_path, cnf_path,
                started, loaded, solver_loaded, records, verified_solution,
            )
            atomic_json(output, partial)
            print(json.dumps({
                "macro_branch_index": record["macro_branch_index"],
                "state_orbit_number": record["state_orbit_number"],
                "signature_orbit_number": record["signature_stabilizer_orbit_number"],
                "coverage": record["labelled_state_matching_coverage"],
                "status": status,
                "solve_seconds": record["solve_seconds"],
                "conflicts": record["stats_delta"].get("conflicts"),
            }, sort_keys=True), flush=True)
            if verified_solution is not None:
                atomic_json(
                    Path(f"scratch_root_e72_source{source_row_index}_verified_solution.json"),
                    verified_solution,
                )
                break
    finally:
        solver.delete()
    result = branch_result(
        source_row_index, conflicts, build_doc, build_path, cnf_path,
        started, loaded, solver_loaded, records, verified_solution,
    )
    atomic_json(output, result)
    return result


def branch_result(source_row_index, conflicts, build_doc, build_path, cnf_path,
                  started, loaded, solver_loaded, records, verified_solution):
    complete = len(records) == build_doc["macro_branches"] or verified_solution is not None
    status = (
        "SAT" if verified_solution is not None
        else "UNSAT" if complete and all(row["status"] == "UNSAT" for row in records)
        else "UNKNOWN" if complete else "IN_PROGRESS"
    )
    return {
        "status": status,
        "model": build_doc["model"] + " (incremental selector branches)",
        "source_row_index": source_row_index,
        "build": str(build_path),
        "build_sha256": sha256(build_path),
        "cnf": str(cnf_path),
        "cnf_sha256": sha256(cnf_path),
        "solver": "CaDiCaL 1.9.5 via PySAT assumptions",
        "conflict_budget_per_branch": conflicts or None,
        "parse_seconds": round(loaded - started, 6),
        "solver_load_seconds": round(solver_loaded - loaded, 6),
        "checkpoint_complete": complete,
        "completed_branches": len(records),
        "macro_branches": build_doc["macro_branches"],
        "direct_unsat": sum(row["status"] == "UNSAT" for row in records),
        "unknown": sum(row["status"] == "UNKNOWN" for row in records),
        "sat": sum(row["status"] == "SAT" for row in records),
        "terminal_labelled_state_matching_coverage": sum(
            row["labelled_state_matching_coverage"] for row in records
            if row["status"] in ("UNSAT", "SAT")
        ),
        "total_labelled_state_matching_coverage": build_doc["macro_audit"]["passing_labelled_state_matching_coverage"],
        "records": records,
        "verified_99_vertex_solution": verified_solution is not None,
        "formal_proof_certificate": None,
        "claim_boundary": "UNSAT branches are computational until an external proof is checked.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-row-index", type=int, required=True)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--per-branch", action="store_true")
    parser.add_argument("--conflicts", type=int, default=100000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.per_branch:
        result = solve_per_branch(args.source_row_index, args.conflicts, args.output)
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "direct_unsat": result["direct_unsat"],
            "unknown": result["unknown"],
            "sat": result["sat"],
            "terminal_coverage": result["terminal_labelled_state_matching_coverage"],
            "total_coverage": result["total_labelled_state_matching_coverage"],
        }, sort_keys=True), flush=True)
    elif args.solve:
        result = solve(args.source_row_index, args.conflicts, args.output)
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "macro_branches": result["macro_branches"],
            "coverage": result["labelled_state_matching_coverage"],
            "solve_seconds": result["solve_seconds"],
            "conflicts": result["solver_stats"].get("conflicts"),
        }, sort_keys=True), flush=True)
    elif args.build:
        result = build(args.source_row_index)
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "macro_branches": result["macro_branches"],
            "coverage": result["macro_audit"]["passing_labelled_state_matching_coverage"],
            "variables": result["cnf_audit"]["declared_variables"],
            "clauses": result["cnf_audit"]["declared_clauses"],
        }, sort_keys=True), flush=True)
    else:
        parser.error("choose --build, --solve, or --per-branch")


if __name__ == "__main__":
    main()
