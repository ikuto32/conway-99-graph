"""Formal coverage bridge for all three source-332 Gram profiles."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


BUILD = Path("scratch_root_e72_source332_parametric_profiles_build.json")
SOURCE_CNF = Path("scratch_root_e72_source332_parametric_profiles.cnf")
PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
INDEPENDENT = Path(
    "scratch_theory_e72_source332_parametric_gram_independent_audit.json"
)
OUTPUT = Path("scratch_root_e72_source332_parametric_profiles_formal_audit.json")
TAGS = ("tminus1", "t0", "tplus1")
PARAMETERS = (-1, 0, 1)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_header_and_body(path):
    with Path(path).open("rb") as handle:
        header = handle.readline()
        body = handle.read()
    fields = header.split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    return int(fields[2]), int(fields[3]), header, body


def main():
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    parametric = json.loads(PARAMETRIC.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    assert build["status"] == "BUILD_COMPLETE"
    assert build["source_row_index"] == 332
    assert build["canonical_macros"] == 1
    assert build["macro_labelled_coverage"] == 131_072
    assert build["profile_branch_count"] == 3
    assert build["profile_parameters"] == list(PARAMETERS)
    assert build["exactly_one_selector_clauses"] == 4
    assert all(build["checks"].values())
    assert parametric["feasible_parameter_count"] == 3
    assert [int(row["parameter"]) for row in parametric["feasible_parameters"]] == list(PARAMETERS)
    assert independent["status"] == "INDEPENDENT_EXACT_VERIFIED"
    assert independent["feasible_parameters"] == list(PARAMETERS)

    selectors = build["selectors"]
    assert len(selectors) == len(set(selectors)) == 3
    source_variables, source_clauses, _source_header, source_body = (
        read_header_and_body(SOURCE_CNF)
    )
    assert source_variables == build["cnf_audit"]["declared_variables"]
    assert source_clauses == build["cnf_audit"]["declared_clauses"]
    assert sha256(SOURCE_CNF) == build["cnf_audit"]["sha256"]
    tail = source_body.splitlines()[-4:]
    assert tail == [
        (" ".join(map(str, selectors)) + " 0").encode(),
        *(
            f"-{left} -{right} 0".encode()
            for left, right in itertools.combinations(selectors, 2)
        ),
    ]

    profile_rows = []
    checker_hash = None
    checker_commit = None
    for index, (tag, parameter, selector) in enumerate(
        zip(TAGS, PARAMETERS, selectors)
    ):
        meta_path = Path(f"scratch_root_e72_source332_profile_{tag}_drup.json")
        drat_path = Path(f"scratch_root_e72_source332_profile_{tag}_drat_audit.json")
        derived_path = Path(f"scratch_root_e72_source332_profile_{tag}.cnf")
        proof_path = Path(f"scratch_root_e72_source332_profile_{tag}.drup")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        drat = json.loads(drat_path.read_text(encoding="utf-8"))
        assert meta["status"] == "UNSAT_PROOF_EMITTED_UNCHECKED"
        assert meta["gram_profile_index"] == index
        assert meta["parameter_t"] == parameter
        assert meta["selector_unit"] == selector
        assert meta["macro_labelled_coverage_shared_across_profiles"] == 131_072
        assert meta["coverage_not_claimed_for_single_profile"]
        assert meta["build_sha256"] == sha256(BUILD)
        assert meta["source_cnf_sha256"] == sha256(SOURCE_CNF)
        derived_variables, derived_clauses, _header, derived_body = (
            read_header_and_body(derived_path)
        )
        assert derived_variables == source_variables
        assert derived_clauses == source_clauses + 1
        assert derived_body == source_body + f"{selector} 0\n".encode()
        assert meta["cnf_sha256"] == sha256(derived_path)
        assert meta["proof_sha256"] == sha256(proof_path)
        assert meta["terminal_empty_clause_present"]
        assert drat["status"] == "DRAT_VERIFIED" and drat["ok"] is True
        assert drat["return_code"] == 0 and "s VERIFIED" in drat["transcript"]
        assert drat["cnf_sha256"] == sha256(derived_path)
        assert drat["proof_sha256"] == sha256(proof_path)
        assert drat["producer_metadata_sha256"] == sha256(meta_path)
        if checker_hash is None:
            checker_hash = drat["checker_sha256"]
            checker_commit = drat["checker_upstream_commit"]
        else:
            assert drat["checker_sha256"] == checker_hash
            assert drat["checker_upstream_commit"] == checker_commit
        profile_rows.append({
            "gram_profile_index": index,
            "parameter_t": parameter,
            "selector": selector,
            "derived_cnf": str(derived_path),
            "derived_cnf_sha256": sha256(derived_path),
            "proof": str(proof_path),
            "proof_sha256": sha256(proof_path),
            "proof_lines": meta["proof_lines"],
            "proof_solve_seconds": meta["solve_seconds"],
            "drat_audit": str(drat_path),
            "drat_audit_sha256": sha256(drat_path),
            "drat_status": "DRAT_VERIFIED",
            "drat_check_seconds": drat["elapsed_seconds"],
        })

    profiles = build["profiles"]
    assert [row["parameter_t"] for row in profiles] == list(PARAMETERS)
    for left, right in itertools.combinations(profiles, 2):
        left_totals = {
            tuple(row[:2]): row[2]
            for row in left["disjoint_exceptional_block_totals"]
        }
        right_totals = {
            tuple(row[:2]): row[2]
            for row in right["disjoint_exceptional_block_totals"]
        }
        assert left_totals.keys() == right_totals.keys()
        assert any(left_totals[key] != right_totals[key] for key in left_totals)

    output = {
        "status": "FORMAL_AUDIT_PASS",
        "scope": "E72 source332 sole canonical macro, all integral PSD Gram profiles",
        "source_row_index": 332,
        "partition_index": 30,
        "Q": 6,
        "canonical_macro_count": 1,
        "macro_labelled_coverage": 131_072,
        "profile_branch_count": 3,
        "profile_parameters": list(PARAMETERS),
        "profile_coverage_is_partition_not_sum": True,
        "coverage_accounting": {
            "single_macro_coverage": 131_072,
            "formal_excluded_coverage": 131_072,
            "incorrect_triple_sum_explicitly_rejected": 393_216,
        },
        "exact_profile_completeness": {
            "affine_Gram_family_dimension": 1,
            "integral_range_PSD_cases": list(PARAMETERS),
            "independent_exact_parametric_audit": str(INDEPENDENT),
            "independent_exact_parametric_audit_sha256": sha256(INDEPENDENT),
            "all_cases_encoded": True,
            "no_other_cases_feasible": True,
        },
        "selector_partition": {
            "selectors": selectors,
            "source_CNF_tail": [line.decode() for line in tail],
            "exactly_one_syntactically_encoded": True,
            "profiles_pairwise_distinct_by_exact_block_cardinality": True,
        },
        "source_formula": {
            "build": str(BUILD),
            "build_sha256": sha256(BUILD),
            "cnf": str(SOURCE_CNF),
            "cnf_sha256": sha256(SOURCE_CNF),
            "variables": source_variables,
            "clauses": source_clauses,
        },
        "profiles": profile_rows,
        "checker": {
            "sha256": checker_hash,
            "upstream_commit": checker_commit,
        },
        "checks": {
            "three_profiles_exactly_all_integral_PSD_cases": True,
            "exactly_one_profile_selector": True,
            "profile_sets_pairwise_disjoint": True,
            "each_derived_payload_byte_identical_plus_selector_unit": True,
            "all_three_DRUP_hashes_bound": True,
            "all_three_proofs_externally_verified": True,
            "coverage_counted_once": True,
        },
        "logical_conclusion": (
            "The sole source332 canonical macro has no exact rooted SRG "
            "completion in any of its three exhaustive Gram profiles."
        ),
        "claim_boundary": (
            "This audit formally covers the three profile selector CNFs. "
            "Upstream macro/catalog and affine-Gram completeness are separately "
            "audited and hash-bound here."
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": output["status"],
        "profiles": len(profile_rows),
        "coverage": output["macro_labelled_coverage"],
        "drat": [row["drat_status"] for row in profile_rows],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
