"""Exact three-profile full-SRG SAT lift for E72 source row 332.

The sole source-332 macro has a one-dimensional Gram family.  Exact
integrality/range/PSD leaves t=-1,0,1.  This builder emits one selector per
profile, enforces exactly one selector, and fixes every internal fibre edge
and all 210 cross-fibre block cardinalities under that selector.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import verify
import scratch_root_e72_macro_guarded_sat as guarded
import scratch_root_e72_full_gram_macro_sat as generic


SOURCE = 332
PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
INDEPENDENT = Path(
    "scratch_theory_e72_source332_parametric_gram_independent_audit.json"
)
CNF_OUTPUT = Path("scratch_root_e72_source332_parametric_profiles.cnf")
BUILD_OUTPUT = Path("scratch_root_e72_source332_parametric_profiles_build.json")
DEFAULT_RESULT = Path(
    "scratch_root_e72_source332_parametric_profiles_aggregate_c1000000.json"
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalized_profile(rows):
    return tuple(sorted(
        (int(left), int(right), int(value)) for left, right, value in rows
    ))


def build():
    formula, audit = guarded.build_guarded_formula(
        {SOURCE}, include_ordinary_disjoint=True
    )
    parametric = json.loads(PARAMETRIC.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    assert parametric["status"] == "EXACT_PARAMETRIC_ENUMERATION_COMPLETE"
    assert independent["status"] == "INDEPENDENT_EXACT_VERIFIED"
    assert parametric["macro"]["source_row_index"] == SOURCE
    assert parametric["macro"]["labelled_coverage"] == 131_072
    assert parametric["feasible_parameter_count"] == 3
    assert [int(row["parameter"]) for row in parametric["feasible_parameters"]] == [-1, 0, 1]
    assert independent["feasible_parameters"] == [-1, 0, 1]

    branches = audit["branches"]
    assert audit["selected_canonical_macros"] == 1
    assert audit["selected_labelled_coverage"] == 131_072
    assert audit["gram_impossible_macros"] == 0
    assert audit["sat_profile_branches"] == 3
    assert len(branches) == 3
    assert {row["macro_index"] for row in branches} == {0}
    assert [row["gram_profile_index"] for row in branches] == [0, 1, 2]
    assert {row["gram_profile_count"] for row in branches} == {3}
    assert {row["macro_labelled_coverage"] for row in branches} == {131_072}
    assert audit["ordinary_disjoint_D4_blocks_explicitly_encoded"]
    assert audit["all_3486_edge_variables_partitioned_per_branch"]
    assert all(row["constrained_cross_fibre_blocks"] == 210 for row in branches)
    assert all(row["skipped_ordinary_disjoint_blocks"] == 0 for row in branches)

    source_branches, source_impossible, source_audit = guarded.load_macros({SOURCE})
    assert not source_impossible
    assert source_audit["sat_profile_branches"] == 3
    assert len(source_branches) == 3

    profiles = []
    for branch, source_branch, exact in zip(
        branches, source_branches, parametric["feasible_parameters"]
    ):
        assert branch["branch_index"] == source_branch["branch_index"]
        assert branch["macro_index"] == source_branch["macro_index"]
        assert branch["gram_profile_index"] == source_branch["gram_profile_index"]
        assert branch["key"] == source_branch["key"]
        observed = normalized_profile(
            source_branch["disjoint_exceptional_block_totals"]
        )
        expected = normalized_profile(
            exact["disjoint_exceptional_block_totals"]
        )
        assert observed == expected
        targets = guarded.complete_block_targets(
            source_branch["entry"], observed
        )
        assert len(targets) == 210
        assert branch["block_target_histogram"] == {
            str(key): value for key, value in sorted(Counter(targets.values()).items())
        }
        profiles.append({
            "gram_profile_index": branch["gram_profile_index"],
            "parameter_t": int(exact["parameter"]),
            "selector": branch["selector"],
            "macro_labelled_coverage_not_additive": 131_072,
            "disjoint_exceptional_block_totals": [list(row) for row in observed],
            "block_target_histogram": branch["block_target_histogram"],
            "constrained_cross_fibre_blocks": branch[
                "constrained_cross_fibre_blocks"
            ],
            "guarded_clauses": branch["guarded_clauses"],
        })

    # Every pair of profiles gives a different exact cardinality to every
    # parametric disjoint block.  Thus their graph sets are pairwise disjoint.
    pairwise_differences = []
    for left, right in itertools.combinations(profiles, 2):
        left_map = {
            tuple(row[:2]): row[2]
            for row in left["disjoint_exceptional_block_totals"]
        }
        right_map = {
            tuple(row[:2]): row[2]
            for row in right["disjoint_exceptional_block_totals"]
        }
        assert left_map.keys() == right_map.keys()
        different = sorted(
            [*pair, left_map[pair], right_map[pair]]
            for pair in left_map if left_map[pair] != right_map[pair]
        )
        assert different
        pairwise_differences.append({
            "left_t": left["parameter_t"],
            "right_t": right["parameter_t"],
            "different_disjoint_blocks": len(different),
            "witness_block": different[0],
        })

    selectors = [row["selector"] for row in profiles]
    assert len(selectors) == len(set(selectors)) == 3
    # Exactly one profile.  At-most-one is theoretically redundant (different
    # exact block totals already conflict), but makes disjointness syntactic.
    formula.append(selectors)
    for left, right in itertools.combinations(selectors, 2):
        formula.append([-left, -right])
    exactly_one_clauses = 4
    assert formula.nv == audit["total_variables"]

    temporary = CNF_OUTPUT.with_suffix(
        CNF_OUTPUT.suffix + f".{os.getpid()}.tmp"
    )
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {formula.nv} {len(formula.clauses)}\n")
        for clause in formula.clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    temporary.replace(CNF_OUTPUT)
    cnf_audit = generic.cnf_audit(CNF_OUTPUT)
    assert cnf_audit["declared_variables"] == formula.nv
    assert cnf_audit["declared_clauses"] == len(formula.clauses)
    cnf_audit["sha256"] = sha256(CNF_OUTPUT)

    result = {
        "status": "BUILD_COMPLETE",
        "model": "source332 exact three-profile selector full-SRG CNF",
        "source_row_index": SOURCE,
        "macro_key": branches[0]["key"],
        "Q": branches[0]["Q"],
        "canonical_macros": 1,
        "macro_labelled_coverage": 131_072,
        "profile_branch_count": 3,
        "profile_parameters": [-1, 0, 1],
        "profile_coverage_semantics": (
            "The three profiles partition completions of one macro; coverage "
            "is 131072 once, not 3*131072."
        ),
        "selectors": selectors,
        "exactly_one_selector_clauses": exactly_one_clauses,
        "profiles": profiles,
        "pairwise_profile_difference_audit": pairwise_differences,
        "upstream": {
            "parametric_gram": str(PARAMETRIC),
            "parametric_gram_sha256": sha256(PARAMETRIC),
            "independent_parametric_audit": str(INDEPENDENT),
            "independent_parametric_audit_sha256": sha256(INDEPENDENT),
            "catalog_sha256": audit["catalog_sha256"],
            "full_gram_sha256": audit["full_gram_sha256"],
            "unrestricted_base_cnf": audit["unrestricted_base_cnf"],
            "unrestricted_base_cnf_sha256": audit[
                "unrestricted_base_cnf_sha256"
            ],
        },
        "guarded_formula_audit": audit,
        "cnf": str(CNF_OUTPUT),
        "cnf_audit": cnf_audit,
        "checks": {
            "all_three_integral_PSD_profiles_included": True,
            "no_other_integral_PSD_profiles": True,
            "profile_selectors_exactly_one": True,
            "profile_graph_sets_pairwise_disjoint": True,
            "macro_coverage_not_triple_counted": True,
            "all_internal_edges_fixed_per_profile": True,
            "all_210_cross_fibre_block_totals_fixed_per_profile": True,
            "all_3486_graph_edge_variables_partitioned_per_profile": True,
        },
        "claim_boundary": (
            "This build exactly lifts the three independently derived Gram "
            "profiles. Upstream macro and Gram completeness remain separate."
        ),
    }
    generic.atomic_json(BUILD_OUTPUT, result)
    return result


def solve(conflicts, output):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_started = time.monotonic()
    build_doc = build()
    built = time.monotonic()
    formula = CNF(from_file=str(CNF_OUTPUT))
    loaded = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        solver_loaded = time.monotonic()
        before = solver.accum_stats()
        if conflicts:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited(expect_interrupt=True)
        else:
            answer = solver.solve()
        after = solver.accum_stats()
        status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
        record = {
            "status": status,
            "solve_seconds": round(time.monotonic() - solver_loaded, 6),
            "stats_delta": {
                key: int(after.get(key, 0)) - int(before.get(key, 0))
                for key in sorted(set(before) | set(after))
            },
        }
        if answer is True:
            positive = {
                literal for literal in solver.get_model()
                if 0 < literal <= 3_486
            }
            verification = verify(positive)
            assert verification["ok"]
            active = [
                selector for selector in build_doc["selectors"]
                if selector in set(solver.get_model())
            ]
            assert len(active) == 1
            record["active_profile_selector"] = active[0]
            record["direct_99_vertex_verification"] = {
                key: value for key, value in verification.items() if key != "edges"
            }
            record["positive_edge_variables"] = sorted(positive)
    result = {
        "status": status,
        "model": build_doc["model"],
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget": conflicts or None,
        "build": str(BUILD_OUTPUT),
        "build_sha256": sha256(BUILD_OUTPUT),
        "cnf": str(CNF_OUTPUT),
        "cnf_sha256": sha256(CNF_OUTPUT),
        "macro_labelled_coverage": 131_072,
        "profile_branch_count": 3,
        "profile_parameters": [-1, 0, 1],
        "build_seconds": round(built - build_started, 6),
        "parse_seconds": round(loaded - built, 6),
        "solver_load_seconds": round(solver_loaded - loaded, 6),
        "elapsed_seconds": round(time.monotonic() - build_started, 6),
        "record": record,
        "formal_proof_certificate": None,
        "claim_boundary": (
            "UNSAT is computational until a proof-producing run is checked. "
            "SAT is accepted only after direct 99-vertex verification."
        ),
    }
    generic.atomic_json(output, result)
    print(json.dumps({
        "status": status,
        "coverage": 131_072,
        "profiles": 3,
        "solve_seconds": record["solve_seconds"],
        "conflicts": record["stats_delta"].get("conflicts", 0),
    }, sort_keys=True), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--conflicts", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    if args.build_only:
        result = build()
        print(json.dumps({
            "status": result["status"],
            "profiles": result["profile_branch_count"],
            "coverage": result["macro_labelled_coverage"],
            "variables": result["cnf_audit"]["declared_variables"],
            "clauses": result["cnf_audit"]["declared_clauses"],
        }, sort_keys=True))
    else:
        solve(args.conflicts, args.output)


if __name__ == "__main__":
    main()
