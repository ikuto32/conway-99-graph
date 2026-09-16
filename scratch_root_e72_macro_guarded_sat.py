"""Lift selected E72 Gram macros directly into the exact 99-graph CNF.

Each canonical macro fixes all 21 internal four-vertex fibre graphs and the
total number of edges in every cross-fibre 4-by-4 block.  Branch-specific
clauses are guarded by a selector, allowing many macros to share one loaded
copy of the unrestricted exact rooted CNF.  This is a search/checkpoint tool;
terminal UNSAT remains computational until a selector CNF proof is emitted
and independently checked.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import CNF_PATH, coordinates, verify


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FULL_GRAM = Path("scratch_theory_e72_macro_full_gram.json")
PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
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


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def local_label(support, bits):
    return tuple(sorted((2 * support[0] + bits[0], 2 * support[1] + bits[1])))


def macro_key(entry):
    return (
        int(entry["partition_index"]),
        int(entry["compression_orbit_index"]),
        int(entry["source_row_index"]),
        int(entry["state_orbit_number"]),
        int(entry["signature_stabilizer_orbit_number"]),
    )


def load_macros(source_rows: set[int]):
    catalog_raw = CATALOG.read_bytes()
    gram_raw = FULL_GRAM.read_bytes()
    parametric_raw = PARAMETRIC.read_bytes()
    catalog = json.loads(catalog_raw)
    gram = json.loads(gram_raw)
    parametric = json.loads(parametric_raw)
    gram_by_key = {
        macro_key(row): row for row in gram["rows"]
        if row["signature_stabilizer_canonical"]
    }
    selected = [
        entry for entry in catalog["macro_entries"]
        if entry["signature_stabilizer_canonical"]
        and int(entry["source_row_index"]) in source_rows
    ]
    assert selected
    assert len({macro_key(entry) for entry in selected}) == len(selected)
    branches = []
    impossible = []
    for macro_index, entry in enumerate(selected):
        key = macro_key(entry)
        assert key in gram_by_key
        gram_row = gram_by_key[key]
        if gram_row["unique"]:
            if not gram_row["passes_full_unique_gram_checks"]:
                impossible.append({
                    "macro_index": macro_index,
                    "key": list(key),
                    "coverage": int(entry["signature_orbit_labelled_coverage"]),
                    "reason": "unique Gram has invalid disjoint block total or PSD",
                })
                continue
            profiles = [gram_row["disjoint_exceptional_block_totals"]]
        else:
            assert int(entry["source_row_index"]) == 332
            assert parametric["macro"]["source_row_index"] == 332
            assert parametric["feasible_parameter_count"] == 3
            profiles = [
                row["disjoint_exceptional_block_totals"]
                for row in parametric["feasible_parameters"]
            ]
        for profile_index, disjoint in enumerate(profiles):
            branches.append({
                "branch_index": len(branches),
                "macro_index": macro_index,
                "gram_profile_index": profile_index,
                "gram_profile_count": len(profiles),
                "key": list(key),
                "entry": entry,
                "disjoint_exceptional_block_totals": disjoint,
            })
    return branches, impossible, {
        "catalog_sha256": hashlib.sha256(catalog_raw).hexdigest().upper(),
        "full_gram_sha256": hashlib.sha256(gram_raw).hexdigest().upper(),
        "parametric_sha256": hashlib.sha256(parametric_raw).hexdigest().upper(),
        "selected_canonical_macros": len(selected),
        "selected_labelled_coverage": sum(
            int(entry["signature_orbit_labelled_coverage"]) for entry in selected
        ),
        "gram_impossible_macros": len(impossible),
        "gram_impossible_labelled_coverage": sum(row["coverage"] for row in impossible),
        "sat_profile_branches": len(branches),
    }


def chosen_internal_edges(entry):
    exceptional = {
        tuple(item["support"]): int(item["deficit"])
        for item in entry["exceptional_supports"]
    }
    chosen = {
        tuple(sorted((tuple(left), tuple(right))))
        for left, right in entry["internal_edges"]
    }
    expected_exceptional_edges = sum(4 - value for value in exceptional.values())
    assert len(chosen) == expected_exceptional_edges
    for edge_pair in chosen:
        supports = {
            tuple(sorted(symbol // 2 for symbol in endpoint))
            for endpoint in edge_pair
        }
        assert len(supports) == 1 and next(iter(supports)) in exceptional
    for support in SUPPORTS:
        if support in exceptional:
            continue
        vertices = tuple(local_label(support, bits) for bits in BITS)
        for left, right in SIDES:
            chosen.add(tuple(sorted((vertices[left], vertices[right]))))
    assert len(chosen) == expected_exceptional_edges + 4 * (21 - len(exceptional))
    return chosen


def complete_block_targets(entry, disjoint_profile):
    exceptional_supports = tuple(
        tuple(item["support"]) for item in entry["exceptional_supports"]
    )
    exceptional_index = {support: index for index, support in enumerate(exceptional_supports)}
    exceptional = frozenset(exceptional_supports)
    overlap = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in entry["overlap_block_totals"]
    }
    disjoint = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in disjoint_profile
    }
    targets = {}
    for left, right in itertools.combinations(SUPPORTS, 2):
        intersect = bool(set(left) & set(right))
        if left in exceptional and right in exceptional:
            pair = tuple(sorted((exceptional_index[left], exceptional_index[right])))
            table = overlap if intersect else disjoint
            assert pair in table
            target = table[pair]
        else:
            # If delta_F=0 then the PSD Gram row Z_F* vanishes.  Hence an
            # overlapping block has D=0 and a disjoint block has D=4.
            target = 0 if intersect else 4
        assert 0 <= target <= 16
        targets[(left, right)] = target
    assert len(targets) == 210

    # Aggregate degree consistency: internal edges count twice and every
    # cross-block edge once, giving four vertices of degree 12 per fibre.
    deficits = {
        tuple(item["support"]): int(item["deficit"])
        for item in entry["exceptional_supports"]
    }
    for support in SUPPORTS:
        internal = 4 - deficits.get(support, 0)
        cross = sum(
            target for pair, target in targets.items() if support in pair
        )
        assert 2 * internal + cross == 48
    return targets


def build_guarded_formula(source_rows: set[int], include_ordinary_disjoint: bool = False):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    assert sha256(CNF_PATH) == meta["cnf_sha256"]
    assert int(meta["variables"]) > 3486
    formula = CNF(from_file=str(CNF_PATH))
    assert formula.nv == meta["variables"]
    assert len(formula.clauses) == meta["clauses"]
    labels, index, variables, edge = coordinates()
    del labels
    assert len(variables) == 3486
    fibres = {
        support: tuple(index[local_label(support, bits)] for bits in BITS)
        for support in SUPPORTS
    }
    branches, impossible, source_audit = load_macros(source_rows)
    pool = IDPool(start_from=formula.nv + 1)
    guarded_clause_count = 0
    branch_records = []
    selectors = []
    for branch in branches:
        entry = branch["entry"]
        selector = pool.id(("selector", branch["branch_index"]))
        selectors.append(selector)
        clause_start = guarded_clause_count
        chosen = chosen_internal_edges(entry)
        internal_positive = 0
        internal_variables = set()
        for support in SUPPORTS:
            fibre_labels = tuple(local_label(support, bits) for bits in BITS)
            fibre = fibres[support]
            for left, right in PAIR_POSITIONS:
                variable = edge(fibre[left], fibre[right])
                edge_pair = tuple(sorted((fibre_labels[left], fibre_labels[right])))
                literal = variable if edge_pair in chosen else -variable
                formula.append([-selector, literal])
                guarded_clause_count += 1
                internal_positive += literal > 0
                internal_variables.add(variable)
        assert len(internal_variables) == 126
        assert internal_positive == len(chosen)

        targets = complete_block_targets(
            entry, branch["disjoint_exceptional_block_totals"]
        )
        exceptional = frozenset(
            tuple(item["support"]) for item in entry["exceptional_supports"]
        )
        target_histogram = Counter()
        block_variables = set()
        skipped_ordinary_disjoint_blocks = 0
        auxiliary_before = pool.top
        cardinality_clauses = 0
        for (left_support, right_support), target in sorted(targets.items()):
            if (
                not include_ordinary_disjoint
                and not (set(left_support) & set(right_support))
                and (left_support not in exceptional or right_support not in exceptional)
            ):
                skipped_ordinary_disjoint_blocks += 1
                continue
            literals = tuple(
                edge(left, right)
                for left in fibres[left_support]
                for right in fibres[right_support]
            )
            assert len(literals) == len(set(literals)) == 16
            assert not (block_variables & set(literals))
            block_variables.update(literals)
            encoded = CardEnc.equals(
                lits=literals,
                bound=target,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
            for clause in encoded.clauses:
                formula.append([-selector, *clause])
            cardinality_clauses += len(encoded.clauses)
            guarded_clause_count += len(encoded.clauses)
            target_histogram[target] += 1
        constrained_blocks = 210 - skipped_ordinary_disjoint_blocks
        assert len(block_variables) == constrained_blocks * 16
        assert not (internal_variables & block_variables)
        if include_ordinary_disjoint:
            assert internal_variables | block_variables == set(variables.values())
        branch_records.append({
            "branch_index": branch["branch_index"],
            "macro_index": branch["macro_index"],
            "gram_profile_index": branch["gram_profile_index"],
            "gram_profile_count": branch["gram_profile_count"],
            "key": branch["key"],
            "source_row_index": int(entry["source_row_index"]),
            "partition_index": int(entry["partition_index"]),
            "Q": int(entry["Q"]),
            "selector": selector,
            "macro_labelled_coverage": int(entry["signature_orbit_labelled_coverage"]),
            "internal_positive_edges": internal_positive,
            "block_target_histogram": {
                str(key): value for key, value in sorted(target_histogram.items())
            },
            "constrained_cross_fibre_blocks": constrained_blocks,
            "skipped_ordinary_disjoint_blocks": skipped_ordinary_disjoint_blocks,
            "cardinality_clauses": cardinality_clauses,
            "guarded_clauses": guarded_clause_count - clause_start,
            "new_auxiliary_variables": pool.top - auxiliary_before,
        })
    assert len(selectors) == len(set(selectors)) == len(branch_records)
    audit = {
        "source_rows": sorted(source_rows),
        "unrestricted_base_cnf": str(CNF_PATH),
        "unrestricted_base_cnf_sha256": meta["cnf_sha256"],
        "base_variables": meta["variables"],
        "base_clauses": meta["clauses"],
        **source_audit,
        "guarded_clauses": guarded_clause_count,
        "total_variables": max(formula.nv, pool.top),
        "total_clauses_without_selector_disjunction": len(formula.clauses),
        "selectors_occur_only_negated_in_guarded_formula": True,
        "ordinary_disjoint_D4_blocks_explicitly_encoded": include_ordinary_disjoint,
        "all_3486_edge_variables_partitioned_per_branch": include_ordinary_disjoint,
        "all_210_cross_fibre_block_totals_known_theoretically_per_branch": True,
        "branches": branch_records,
        "gram_impossible": impossible,
    }
    return formula, audit


def stats_delta(before, after):
    return {
        key: int(after.get(key, 0)) - int(before.get(key, 0))
        for key in sorted(set(before) | set(after))
    }


def solve(source_rows: set[int], conflicts: int, output: Path,
          include_ordinary_disjoint: bool = False):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    started = time.monotonic()
    formula, audit = build_guarded_formula(source_rows, include_ordinary_disjoint)
    built = time.monotonic()
    solver = Solver(name="cadical195", bootstrap_with=formula.clauses)
    loaded = time.monotonic()
    records = []
    verified_solution = None
    try:
        for branch in audit["branches"]:
            before = solver.accum_stats()
            branch_started = time.monotonic()
            if conflicts:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited(
                    assumptions=[branch["selector"]], expect_interrupt=True
                )
            else:
                answer = solver.solve(assumptions=[branch["selector"]])
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            record = {
                **branch,
                "status": status,
                "solve_seconds": round(time.monotonic() - branch_started, 6),
                "stats_delta": stats_delta(before, after),
                "formal_proof_certificate": None,
            }
            if answer is False:
                core = solver.get_core() or []
                assert core == [branch["selector"]]
                record["assumption_core"] = core
            elif answer is True:
                model = solver.get_model()
                positive = {literal for literal in model if 0 < literal <= 3486}
                checked = verify(positive)
                record["direct_99_vertex_verification"] = {
                    key: value for key, value in checked.items() if key != "edges"
                }
                record["positive_edge_variables"] = sorted(positive)
                assert checked["ok"]
                verified_solution = checked
            records.append(record)
            checkpoint = make_result(
                audit, records, conflicts, started, built, loaded, verified_solution
            )
            atomic_json(output, checkpoint)
            print(json.dumps({
                "branch": branch["branch_index"],
                "source": branch["source_row_index"],
                "macro": branch["macro_index"],
                "profile": branch["gram_profile_index"],
                "status": status,
                "seconds": record["solve_seconds"],
                "conflicts": record["stats_delta"].get("conflicts", 0),
            }), flush=True)
            if verified_solution is not None:
                atomic_json(Path("scratch_root_e72_macro_verified_solution.json"), verified_solution)
                break
    finally:
        solver.delete()
    result = make_result(
        audit, records, conflicts, started, built, loaded, verified_solution
    )
    atomic_json(output, result)
    return result


def make_result(audit, records, conflicts, started, built, loaded, verified_solution):
    completed = len(records) == len(audit["branches"]) or verified_solution is not None
    status = (
        "SAT" if verified_solution is not None
        else "UNSAT" if completed and all(row["status"] == "UNSAT" for row in records)
        else "UNKNOWN" if completed else "IN_PROGRESS"
    )
    by_macro = defaultdict(list)
    for row in records:
        by_macro[row["macro_index"]].append(row["status"])
    excluded_macros = {
        int(row["macro_index"]) for row in audit["gram_impossible"]
    }
    for macro_index, statuses in by_macro.items():
        needed = next(
            row["gram_profile_count"]
            for row in records if row["macro_index"] == macro_index
        )
        if len(statuses) == needed and all(value == "UNSAT" for value in statuses):
            excluded_macros.add(macro_index)
    coverage_by_macro = {
        row["macro_index"]: row["macro_labelled_coverage"]
        for row in audit["branches"]
    }
    coverage_by_macro.update({
        int(row["macro_index"]): int(row["coverage"])
        for row in audit["gram_impossible"]
    })
    return {
        "status": status,
        "model": "guarded full-block direct exact-CNF lift of E72 Gram macros",
        "solver": "CaDiCaL 1.9.5 via PySAT assumptions",
        "conflict_budget_per_profile_branch": conflicts or None,
        "build_seconds": round(built - started, 6),
        "solver_load_seconds": round(loaded - built, 6),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "audit": audit,
        "completed_profile_branches": len(records),
        "profile_branch_count": len(audit["branches"]),
        "counts": dict(Counter(row["status"] for row in records)),
        "excluded_macros": len(excluded_macros),
        "excluded_labelled_coverage": sum(
            coverage_by_macro[index] for index in excluded_macros
        ),
        "records": records,
        "verified_99_vertex_solution": verified_solution is not None,
        "claim_boundary": (
            "Every active selector fixes a canonical E72 macro and all Gram-implied "
            "4-by-4 block totals in the unrestricted exact rooted CNF. UNSAT is "
            "computational until a proof-producing selector formula is checked."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sources", required=True,
        help="comma-separated source_row_index values",
    )
    parser.add_argument("--conflicts", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument(
        "--ordinary-disjoint", action="store_true",
        help="also encode the Gram-implied D=4 blocks incident with ordinary fibres",
    )
    args = parser.parse_args()
    source_rows = {int(value) for value in args.sources.split(",") if value.strip()}
    assert source_rows
    output = args.output or Path(
        "scratch_root_e72_macro_guarded_sources_"
        + "_".join(map(str, sorted(source_rows)))
        + f"_c{args.conflicts}.json"
    )
    if args.build_only:
        started = time.monotonic()
        _formula, audit = build_guarded_formula(source_rows, args.ordinary_disjoint)
        result = {
            "status": "BUILD_COMPLETE",
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "audit": audit,
        }
        atomic_json(output, result)
        print(json.dumps({
            "status": result["status"],
            "macros": audit["selected_canonical_macros"],
            "profiles": audit["sat_profile_branches"],
            "variables": audit["total_variables"],
            "clauses": audit["total_clauses_without_selector_disjunction"],
        }, sort_keys=True))
    else:
        result = solve(
            source_rows, args.conflicts, output, args.ordinary_disjoint
        )
        print(json.dumps({
            "status": result["status"],
            "counts": result["counts"],
            "excluded_macros": result["excluded_macros"],
            "excluded_labelled_coverage": result["excluded_labelled_coverage"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
