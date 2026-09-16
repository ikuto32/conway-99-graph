"""Independent manifest/coverage audit for the E71 kernel-port census.

This audit deliberately does not re-run the comparatively expensive finite CSP.
It checks that every full-Gram profile is represented exactly once under its
canonical macro, that the labelled coverage is a disjoint partition, and that
all reported rejection/control summaries follow from the stored per-profile
certificates.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
CENSUS = Path("scratch_theory_e71_equitable_kernel_port_census.json")
OUTPUT = Path("scratch_theory_e71_equitable_kernel_port_census_audit.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def key(row):
    return (
        int(row["source_row_index"]),
        int(row["state_orbit_number"]),
        int(row["signature_stabilizer_orbit_number"]),
    )


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def main() -> None:
    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    census_raw = CENSUS.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    census = json.loads(census_raw)

    assert census["status"] == "EXACT_E71_EQUITABLE_KERNEL_PORT_CENSUS_COMPLETE"
    assert census["inputs"][str(CATALOG)] == sha256(catalog_raw)
    assert census["inputs"][str(MINING)] == sha256(mining_raw)

    canonical = {
        key(row): row for row in catalog["macro_entries"]
        if row["signature_stabilizer_canonical"]
    }
    profiles_by_key = defaultdict(list)
    for profile in mining["profile_rows"]["71"]:
        profiles_by_key[key(profile)].append(profile)
    rows = {tuple(row["key"]): row for row in census["rows"]}
    assert len(rows) == len(census["rows"])
    assert set(rows) == set(profiles_by_key)
    assert set(rows) <= set(canonical)

    for macro_key, row in rows.items():
        entry = canonical[macro_key]
        source_profiles = profiles_by_key[macro_key]
        assert row["source_row_index"] == macro_key[0]
        assert row["Q"] == int(entry["Q"])
        assert row["coverage"] == int(entry["signature_orbit_labelled_coverage"])
        assert row["profile_count"] == len(source_profiles) == len(row["profiles"])
        stored_parameters = sorted(profile["parameter"] for profile in row["profiles"])
        source_parameters = sorted(profile["parameter"] for profile in source_profiles)
        assert stored_parameters == source_parameters
        stored_pass = any(profile["passes_kernel_port_CSP"]
                          for profile in row["profiles"])
        assert stored_pass == row[
            "macro_passes_some_full_Gram_profile_kernel_port_CSP"
        ]
        for profile in row["profiles"]:
            assert profile["K4_rank"] == profile["Z_rank"]
            assert len(profile["relations"]) == int(
                source_profiles[0]["exceptional_supports"]
            )
            for relation in profile["relations"]:
                assert 0 <= relation["allowed_pairs"] <= relation["possible_pairs"]
            if profile["passes_kernel_port_CSP"]:
                assert profile["group_choice_witness"] is not None
            else:
                assert profile["group_choice_witness"] is None

    rejected = [row for row in rows.values()
                if not row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]]
    retained = [row for row in rows.values()
                if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]]
    simple = [row for row in rejected if all(
        profile["simple_equal_degree_kernel_certificates"]
        for profile in row["profiles"]
    )]
    general = [row for row in rejected if row not in simple]
    empty_relation_rejections = [row for row in rejected if all(
        any(relation["allowed_pairs"] == 0 for relation in profile["relations"])
        for profile in row["profiles"]
    )]

    computed = {
        "input_full_Gram_viable_canonical_macros": len(rows),
        "input_full_Gram_profiles": sum(row["profile_count"] for row in rows.values()),
        "input_coverage": sum(row["coverage"] for row in rows.values()),
        "rejected_macros": len(rejected),
        "rejected_coverage": sum(row["coverage"] for row in rejected),
        "retained_macros": len(retained),
        "retained_coverage": sum(row["coverage"] for row in retained),
        "rejected_source_rows": len({row["source_row_index"] for row in rejected}),
        "rejected_macros_with_simple_equal_degree_kernel_certificate": len(simple),
        "rejected_coverage_with_simple_equal_degree_kernel_certificate": sum(
            row["coverage"] for row in simple
        ),
        "rejected_macros_requiring_general_rowspace_CSP": len(general),
        "rejected_coverage_requiring_general_rowspace_CSP": sum(
            row["coverage"] for row in general
        ),
        "rank_histogram_profiles": dict(Counter(
            str(profile["K4_rank"])
            for row in rows.values() for profile in row["profiles"]
        )),
        "Q_histogram_rejected_coverage": {
            str(q): sum(row["coverage"] for row in rejected if row["Q"] == q)
            for q in sorted({row["Q"] for row in rejected})
        },
    }
    assert computed == census["summary"]
    assert computed["input_coverage"] == 58_556_416
    assert computed["rejected_coverage"] + computed["retained_coverage"] == (
        computed["input_coverage"]
    )

    source2601 = [row for row in rows.values() if row["source_row_index"] == 2601]
    source724_q2 = [row for row in rows.values()
                    if row["source_row_index"] == 724 and row["Q"] == 2]
    assert len(source2601) == 2 and all(row in rejected for row in source2601)
    assert sum(row["coverage"] for row in source2601) == 262_144
    assert len(source724_q2) == 1 and source724_q2[0] in retained

    result = {
        "status": "INDEPENDENT_E71_KERNEL_PORT_CENSUS_MANIFEST_AUDIT_PASS",
        "inputs": {
            str(CATALOG): sha256(catalog_raw),
            str(MINING): sha256(mining_raw),
            str(CENSUS): sha256(census_raw),
        },
        "verified_summary": computed,
        "rejected_macros_with_an_empty_individual_fibre_relation": len(
            empty_relation_rejections
        ),
        "source2601": {
            "macro_count": len(source2601),
            "excluded_coverage": sum(row["coverage"] for row in source2601),
        },
        "source724_Q2": {
            "macro_count": len(source724_q2),
            "retained_by_kernel_port_CSP": True,
        },
        "scope": (
            "Independent hashes, one-to-one macro/profile manifest, labelled "
            "coverage partition, and stored certificate/control consistency. "
            "The finite rowspace CSP itself is independently audited for source2601."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result["verified_summary"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
