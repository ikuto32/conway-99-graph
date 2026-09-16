"""Hash-bound, nonoverlapping coverage inventory for the E72 macro catalog."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
REMAINING = Path("scratch_general_e72_remaining_frontier_audit.json")
SMALL = Path("scratch_root_e72_q3_small_formal_audit.json")
SOURCE134 = Path("scratch_root_e72_source134_formal_audit.json")
SOURCE248 = Path("scratch_root_e72_source248_formal_audit.json")
SOURCE133_CHAIN = Path("scratch_root_e72_source133_solver_free_chain_audit.json")
SOURCE133_MACRO4 = Path("scratch_root_e72_source133_macro4_formal_audit.json")
BREADTH = Path("scratch_root_e72_full_gram_breadth_audit.json")
SOURCE630 = Path("scratch_root_e72_source630_lean_full_gram_macro_aggregate_c1000000.json")
SOURCE630_FORMAL = Path("scratch_root_e72_source630_formal_audit.json")
SOURCE150_NORM = Path("scratch_root_e72_source150_norm_collision_audit.json")
SOURCE150_RECURRENCE_FILTER = Path(
    "scratch_theory_e72_source150_fibre_recurrence_filter.json"
)
SOURCE150_RECURRENCE = Path("scratch_root_e72_source150_fibre_recurrence_audit.json")
SOURCE150_SYNC = Path(
    "scratch_root_e72_source150_synchronized_config_audit.json"
)
SOURCE150_SYNC_JOINT_M01 = Path(
    "scratch_theory_e72_source150_sync_joint_m01.json"
)
SOURCE150_M47_SHARDS = Path(
    "scratch_root_e72_source150_m47_shard_audit.json"
)
SOURCE150_M2_SHARDS = Path(
    "scratch_root_e72_source150_m2_shard_audit.json"
)
SOURCE150_M6_SHARDS = Path(
    "scratch_root_e72_source150_m6_shard_audit.json"
)
SOURCE150_M00_EXACT = Path(
    "scratch_root_e72_source150_m00_exact_audit.json"
)
SOURCE150_M31_SHARDS = Path(
    "scratch_root_e72_source150_m31_shard_audit.json"
)
SOURCE150_M10_JOINT_PRIMARY = Path(
    "scratch_root_e72_source150_small5_joint_primary_m10_complete_audit.json"
)
SOURCE150_M03_COMPLETE = Path(
    "scratch_root_e72_source150_m03_complete_audit.json"
)
SOURCE332_PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
SOURCE332_FORMAL = Path(
    "scratch_root_e72_source332_parametric_profiles_formal_audit.json"
)
OPEN_DEFECT_CENSUS = Path("scratch_theory_e72_open_defect_rank_census.json")
OPEN_DEFECT_AUDIT = Path(
    "scratch_theory_e72_open_defect_rank_exclusion_audit.json"
)
OUTPUT = Path("scratch_root_e72_complete_coverage_inventory.json")
REPORT = Path("scratch_root_e72_complete_coverage_inventory.md")

SMALL_SOURCES = {2, 8, 12, 27, 33, 39}
GLOBAL_COVERAGE = 141_545_472


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    remaining = json.loads(REMAINING.read_text(encoding="utf-8"))
    small = json.loads(SMALL.read_text(encoding="utf-8"))
    source134 = json.loads(SOURCE134.read_text(encoding="utf-8"))
    source248 = json.loads(SOURCE248.read_text(encoding="utf-8"))
    source133_chain = json.loads(SOURCE133_CHAIN.read_text(encoding="utf-8"))
    source133_macro4 = json.loads(SOURCE133_MACRO4.read_text(encoding="utf-8"))
    breadth = json.loads(BREADTH.read_text(encoding="utf-8"))
    source630 = json.loads(SOURCE630.read_text(encoding="utf-8"))
    source150_norm = json.loads(SOURCE150_NORM.read_text(encoding="utf-8"))
    source150_recurrence_filter = json.loads(
        SOURCE150_RECURRENCE_FILTER.read_text(encoding="utf-8")
    )
    source150_recurrence = json.loads(
        SOURCE150_RECURRENCE.read_text(encoding="utf-8")
    )
    source150_sync = json.loads(SOURCE150_SYNC.read_text(encoding="utf-8"))
    source150_sync_joint_m01 = json.loads(
        SOURCE150_SYNC_JOINT_M01.read_text(encoding="utf-8")
    )
    source150_m47_shards = json.loads(
        SOURCE150_M47_SHARDS.read_text(encoding="utf-8")
    )
    source150_m2_shards = json.loads(
        SOURCE150_M2_SHARDS.read_text(encoding="utf-8")
    )
    source150_m6_shards = json.loads(
        SOURCE150_M6_SHARDS.read_text(encoding="utf-8")
    )
    source150_m00_exact = json.loads(
        SOURCE150_M00_EXACT.read_text(encoding="utf-8")
    )
    source150_m31_shards = json.loads(
        SOURCE150_M31_SHARDS.read_text(encoding="utf-8")
    )
    source150_m10_joint_primary = json.loads(
        SOURCE150_M10_JOINT_PRIMARY.read_text(encoding="utf-8")
    )
    source150_m03_complete = json.loads(
        SOURCE150_M03_COMPLETE.read_text(encoding="utf-8")
    )
    source332_parametric = json.loads(
        SOURCE332_PARAMETRIC.read_text(encoding="utf-8")
    )
    open_defect_census = json.loads(
        OPEN_DEFECT_CENSUS.read_text(encoding="utf-8")
    )
    open_defect_audit = json.loads(
        OPEN_DEFECT_AUDIT.read_text(encoding="utf-8")
    )

    assert catalog["status"] == "COMPLETE"
    canonical = [entry for entry in catalog["macro_entries"]
                 if entry["signature_stabilizer_canonical"]]
    assert len(canonical) == catalog["summary"]["macro_entries_mod_state_stabilizers"] \
        == 163
    assert sum(entry["signature_orbit_labelled_coverage"] for entry in canonical) \
        == catalog["summary"]["labelled_state_matching_coverage"] \
        == GLOBAL_COVERAGE
    by_source_entries = defaultdict(list)
    for entry in canonical:
        by_source_entries[entry["source_row_index"]].append(entry)
    by_source_coverage = {
        source: sum(entry["signature_orbit_labelled_coverage"] for entry in entries)
        for source, entries in by_source_entries.items()
    }

    assert remaining["status"] == "EXACT_COVERAGE_VERIFIED"
    remaining_rows = {row["source_row_index"]: row
                      for row in remaining["source_rows"]}
    assert len(remaining_rows) == remaining["remaining_summary"]["source_rows"] == 64
    assert set(by_source_coverage) == SMALL_SOURCES | {134} | set(remaining_rows)
    assert sum(by_source_coverage[source] for source in SMALL_SOURCES) == 45_056
    assert by_source_coverage[134] == 101_593_088
    assert sum(by_source_coverage[source] for source in remaining_rows) == 39_907_328
    for source, row in remaining_rows.items():
        assert by_source_coverage[source] == row["Gram_macro_labelled_coverage"]

    assert small["status"] == "FORMAL_AUDIT_PASS"
    assert small["all_selector_proofs_drat_verified"]
    assert small["coverage"]["support_records"] == 3
    assert small["coverage"]["branches_formally_covered"] == 584
    assert small["coverage"]["labelled_local_graphs_covered"] == 24_576
    small_macro_coverage = remaining["excluded"][
        "small_formal_macro_crosscheck"
    ]["Gram_macro_labelled_coverage"]
    assert small_macro_coverage == 45_056

    assert source134["status"] == "FORMAL_AUDIT_PASS"
    assert source134["source_row_index"] == 134
    assert source134["labelled_state_matching_coverage"] == by_source_coverage[134]
    assert source134["selector_certificate"]["external_checker_status"] \
        == "DRAT_VERIFIED"

    assert source248["status"] == "FORMAL_AUDIT_PASS"
    assert source248["source_row_index"] == 248
    assert source248["labelled_state_matching_coverage"] == by_source_coverage[248] \
        == 28_344_320
    assert source248["certificate"]["external_checker_status"] == "DRAT_VERIFIED"

    assert source133_chain["status"] == "SOLVER_FREE_CHAIN_AUDIT_PASS"
    assert source133_chain["source_row_index"] == 133
    source133_regular = source133_chain["coverage_chain"]["catalog_macro_coverage"]
    assert source133_regular == 2_490_368
    assert source133_chain["coverage_chain"]["orbits"] == [5138, 81, 1, 0]
    assert source133_chain["coverage_chain"]["labelled_mass"] \
        == [1_129_056, 9_952, 16, 0]
    assert source133_macro4["status"] == "FORMAL_AUDIT_PASS"
    assert source133_macro4["certificate"]["external_checker_status"] \
        == "DRAT_VERIFIED"
    source133_nonregular = source133_macro4["catalog_labelled_coverage"]
    assert source133_nonregular == 12_288
    assert source133_regular + source133_nonregular \
        == by_source_coverage[133] == 2_502_656

    assert breadth["status"] == "BREADTH_AUDIT_PASS"
    breadth_sources = {row["source_row_index"] for row in breadth["rows"]}
    assert len(breadth_sources) == breadth["screened_source_rows"] == 23
    assert 630 not in breadth_sources and 133 not in breadth_sources \
        and 150 not in breadth_sources and 248 not in breadth_sources \
        and 332 not in breadth_sources
    assert all(row["latest_terminal_search"]["status"] == "UNSAT"
               for row in breadth["rows"])
    breadth_coverage = sum(by_source_coverage[source] for source in breadth_sources)
    assert breadth_coverage == breadth["screened_coverage"] \
        == breadth["latest_terminal_unsat_coverage"] == 5_939_200
    breadth_formal = sum(row["coverage"] for row in breadth["rows"]
                         if row["formal_certificate"] is not None)
    assert breadth_formal == breadth["formally_certified_coverage_at_audit_time"]
    breadth_computational_only = breadth_coverage - breadth_formal

    assert source630["status"] == "UNSAT"
    assert source630["source_row_index"] == 630
    assert source630["direct_unsat"] == 1
    assert source630["unknown"] == source630["sat"] == 0
    source630_coverage = source630["total_labelled_state_matching_coverage"]
    assert source630_coverage == source630["terminal_labelled_state_matching_coverage"] \
        == by_source_coverage[630] == 196_608
    source630_formal = None
    if SOURCE630_FORMAL.exists():
        source630_formal = json.loads(SOURCE630_FORMAL.read_text(encoding="utf-8"))
        assert source630_formal["status"] == "FORMAL_AUDIT_PASS"
        assert source630_formal["source_row_index"] == 630
        assert source630_formal["labelled_state_matching_coverage"] \
            == source630_coverage

    assert source150_norm["status"] == "SOURCE150_NORM_COLLISION_AUDIT_PASS"
    assert source150_norm["filter_result"]["rejected_local_orbits"] == 0
    assert source150_recurrence["status"] \
        == "SOURCE150_FIBRE_RECURRENCE_AUDIT_PASS"
    source150_total = by_source_coverage[150]
    assert source150_total == source150_recurrence["coverage"]["input_labelled_mass"] \
        == 2_244_608
    source150_recurrence_rejected = source150_recurrence[
        "coverage"
    ]["rejected_labelled_mass"]
    source150_recurrence_open = source150_recurrence[
        "coverage"
    ]["passing_labelled_mass"]
    assert source150_recurrence_rejected == 393_216
    assert source150_recurrence_open == 1_851_392
    assert source150_recurrence_rejected + source150_recurrence_open \
        == source150_total

    assert source150_sync["status"] \
        == "SOURCE150_SYNCHRONIZED_LOCALPAIR_AUDIT_PASS"
    synchronized = source150_sync["ordinary_local_pair_extension"]
    assert synchronized["input_local_orbits"] == 132
    assert synchronized["input_labelled_mass"] == 32_768
    assert synchronized["UNSAT_local_orbits"] == 132
    assert synchronized["UNSAT_labelled_mass"] == 32_768
    assert synchronized["SAT_local_orbits"] \
        == synchronized["UNKNOWN_local_orbits"] == 0
    assert synchronized["macro_3_0_UNSAT_mass"] \
        == synchronized["macro_8_0_UNSAT_mass"] == 16_384
    source150_sync_rejected = synchronized["UNSAT_labelled_mass"]
    assert source150_sync_joint_m01["status"] \
        == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    joint_m01_summary = source150_sync_joint_m01["summary"]
    assert joint_m01_summary["wanted_macros"] == [[0, 1]]
    assert joint_m01_summary["input_orbits"] == 234
    assert joint_m01_summary["input_mass"] \
        == joint_m01_summary["UNSAT_mass"] == 65_536
    assert joint_m01_summary["SAT_mass"] \
        == joint_m01_summary["UNKNOWN_mass"] == 0
    assert joint_m01_summary["status_histogram"] == {"UNSAT": 234}
    assert all(value for name, value in source150_sync_joint_m01["checks"].items()
               if name != "SAT_or_SMT_used")
    assert source150_sync_joint_m01["checks"]["SAT_or_SMT_used"] is False
    source150_sync_joint_m01_rejected = joint_m01_summary["UNSAT_mass"]
    source150_open_before_m47_shards = (
        source150_recurrence_open - source150_sync_rejected
        - source150_sync_joint_m01_rejected
    )
    assert source150_open_before_m47_shards == 1_753_088
    assert source150_m47_shards["status"] \
        == "SOURCE150_M47_EXACT_SHARD_AUDIT_PASS"
    assert source150_m47_shards["SAT_or_UNKNOWN_counted_as_excluded"] is False
    assert not source150_m47_shards["scope"]["this_is_not_a_full_macro_sweep"]
    source150_m47_shard_rejected = source150_m47_shards[
        "scope"
    ]["selected_coverage"]
    assert source150_m47_shard_rejected == 1_048_576
    assert source150_m47_shards["per_macro"] == {
        "4:0": {"orbits": 1056, "coverage": 524_288},
        "7:0": {"orbits": 1312, "coverage": 524_288},
    }
    assert source150_m2_shards["status"] \
        == "SOURCE150_M2_EXACT_SHARD_AUDIT_PASS"
    assert source150_m2_shards["macro"] == [2, 0]
    assert source150_m2_shards["local_graph_orbits"] == 576
    assert source150_m2_shards["all_catalog_orbits_excluded"] is True
    assert source150_m2_shards["SAT_or_UNKNOWN_counted_as_excluded"] is False
    source150_m2_shard_rejected = source150_m2_shards["labelled_coverage"]
    assert source150_m2_shard_rejected == 262_144
    assert source150_m6_shards["status"] \
        == "SOURCE150_M6_EXACT_SHARD_AGGREGATE_AUDIT_PASS"
    assert source150_m6_shards["macro"] == [6, 0]
    assert source150_m6_shards["excluded_orbits"] == 704
    assert source150_m6_shards["unresolved_orbits"] == 0
    assert source150_m6_shards["all_catalog_orbits_excluded"] is True
    assert source150_m6_shards["SAT_or_UNKNOWN_counted_as_excluded"] is False
    source150_m6_shard_rejected = source150_m6_shards[
        "excluded_labelled_coverage"
    ]
    assert source150_m6_shard_rejected == 262_144
    assert source150_m00_exact["status"] == "SOURCE150_M00_EXACT_AUDIT_PASS"
    assert source150_m00_exact["macro"] == [0, 0]
    assert source150_m00_exact["excluded_orbits"] == 45
    assert source150_m00_exact["unresolved_orbits"] == 0
    assert source150_m00_exact["all_catalog_orbits_excluded"] is True
    assert source150_m00_exact["SAT_or_UNKNOWN_counted_as_excluded"] is False
    source150_m00_rejected = source150_m00_exact[
        "excluded_labelled_coverage"
    ]
    assert source150_m00_rejected == 8_192
    assert source150_m31_shards["status"] \
        == "SOURCE150_M31_INDEPENDENT_EXACT_SHARD_AUDIT_PASS"
    assert source150_m31_shards["macro"] == [3, 1]
    assert source150_m31_shards["excluded_orbits"] == 396
    assert source150_m31_shards["unresolved_orbits"] == 0
    assert source150_m31_shards["all_catalog_orbits_excluded"] is True
    assert source150_m31_shards["SAT_or_UNKNOWN_counted_as_excluded"] is False
    assert source150_m31_shards["mode"][
        "ordinary_joint_map_pair_supplement_records"
    ] == [190, 347]
    source150_m31_shard_rejected = source150_m31_shards[
        "excluded_labelled_coverage"
    ]
    assert source150_m31_shard_rejected == 131_072
    # Immutable single-macro certificate: never credit mutable partial totals.
    m10 = source150_m10_joint_primary
    assert m10["status"] \
        == "SOURCE150_SINGLE_MACRO_JOINT_PRIMARY_INDEPENDENT_AUDIT_PASS"
    assert m10["source_row_index"] == 150 and m10["macro"] == [1, 0]
    assert m10["Q"] == 4 and m10["catalog_orbits"] == 96
    assert m10["status_histogram"] == {"UNSAT": 96, "SAT": 0, "UNKNOWN": 0}
    assert m10["status_mass"] == {"UNSAT": 8_192, "SAT": 0, "UNKNOWN": 0}
    assert m10["evidence_class"] == "exact_solver_free_finite_local_CSP"
    assert m10["DRAT_certificate_present"] is False
    assert m10["solver_or_runner_imported"] is False
    assert all(m10["coverage_checks"].values())
    assert m10["mode"] == {
        "ordinary_local_pair": True, "ordinary_local_pair_every_depth": True,
        "ordinary_joint_map": True, "node_cap": 0, "joint_map_node_cap": 0,
        "ordinary_joint_map_unknowns_relaxed_as_pass": 0, "projection": [],
    }
    for name, expected_hash in m10["inputs"].items():
        assert sha256(Path(name)) == expected_hash
    for name, field in (
        ("scratch_theory_e72_source150_synchronized_config_csp.py", "solver_sha256"),
        ("scratch_root_e72_source150_small5_joint_primary_runner.py", "runner_sha256"),
        ("scratch_root_e72_source150_small5_joint_primary_partial_audit.py", "audit_source_sha256"),
        ("scratch_root_e72_source150_small5_aggregate_audit.py", "foundation_sha256"),
    ):
        assert sha256(Path(name)) == m10[field]
    m10_shard_hashes = {row["path"]: row["sha256"] for row in m10["shards"]}
    assert len(m10_shard_hashes) == len(m10["shards"]) == 12
    for name, expected_hash in m10_shard_hashes.items():
        assert sha256(Path(name)) == expected_hash
    assert sorted(row["record_number"] for row in m10["records"]) == list(range(96))
    assert len({row["mask_hex"] for row in m10["records"]}) == 96
    for row in m10["records"]:
        assert row["status"] == "UNSAT" and row["Q"] == 4
        assert row["sha256"] == m10_shard_hashes[row["artifact"]]
    source150_m10_joint_primary_rejected = m10["catalog_coverage"]
    assert source150_m10_joint_primary_rejected \
        == sum(row["orbit_size"] for row in m10["records"]) == 8_192
    # Credit all 80 m03 orbits once only after every direct SAT survivor has
    # an exact UNSAT supplement. Neither partial mass nor the 448 supplement
    # mass is a separate inventory bucket.
    m03 = source150_m03_complete
    assert m03["status"] == "SOURCE150_M03_COMPLETE_INDEPENDENT_AUDIT_PASS"
    assert m03["source_row_index"] == 150 and m03["macro"] == [0, 3]
    assert m03["Q"] == 8 and m03["catalog_orbits"] == 80
    assert m03["catalog_coverage"] == 4_096
    assert m03["status_histogram"] == {"UNSAT": 80, "SAT": 0, "UNKNOWN": 0}
    assert m03["status_mass"] == {"UNSAT": 4_096, "SAT": 0, "UNKNOWN": 0}
    assert m03["direct_UNSAT_orbits"] == 69
    assert m03["supplement_UNSAT_orbits"] == 11
    assert m03["evidence_class"] \
        == "exact_solver_free_finite_local_CSP_plus_joint_map_supplement"
    assert m03["DRAT_certificate_present"] is False
    assert m03["solver_or_runner_imported"] is False
    assert all(m03["coverage_checks"].values())
    for name, expected_hash in m03["inputs"].items():
        assert sha256(Path(name)) == expected_hash
    direct_name = "scratch_theory_e72_source150_sync_localpair_everydepth_m03_full.json"
    for name, field in (
        (direct_name, "direct_result_sha256"),
        ("scratch_root_e72_source150_m03_everydepth_full_audit.json", "direct_audit_sha256"),
        ("scratch_theory_e72_source150_synchronized_config_csp.py", "solver_sha256"),
        ("scratch_root_e72_source150_m03_joint_supplement_runner.py", "supplement_runner_sha256"),
        ("scratch_root_e72_source150_m03_joint_supplement_audit.py", "auditor_sha256"),
    ):
        assert sha256(Path(name)) == m03[field]
    m03_artifact_hashes = {row["artifact"]: row["sha256"] for row in m03["records"]}
    assert len(m03_artifact_hashes) == 12
    m03_artifacts = {}
    for name, expected_hash in m03_artifact_hashes.items():
        assert sha256(Path(name)) == expected_hash
        document = json.loads(Path(name).read_text(encoding="utf-8"))
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        assert document["inputs"] == m03["inputs"]
        summary = document["summary"]
        assert summary["wanted_macros"] == [[0, 3]]
        assert summary["available_orbits_in_wanted_macros"] == 80
        assert summary["ordinary_local_pair_filter_enabled"] is True
        assert summary["ordinary_local_pair_every_depth_enabled"] is True
        assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
        assert summary["fixed_block_projection"] == []
        m03_artifacts[name] = document
    direct = m03_artifacts[direct_name]
    assert [row[0] for row in direct["results"]] == list(range(80))
    assert direct["summary"]["status_histogram"] == {"UNSAT": 69, "SAT": 11}
    assert direct["summary"]["UNSAT_mass"] == 3_648
    assert direct["summary"]["SAT_mass"] == 448
    assert direct["summary"]["UNKNOWN_mass"] == 0
    supplement_numbers = [11, 36, 38, 56, 57, 58, 59, 63, 65, 71, 74]
    assert [row[0] for row in direct["results"] if row[5] == "SAT"] == supplement_numbers
    assert [row["record_number"] for row in m03["records"]] == list(range(80))
    assert len({row["mask_hex"] for row in m03["records"]}) == 80
    mode_counts, mode_mass = Counter(), Counter()
    for row in m03["records"]:
        number, name = row["record_number"], row["artifact"]
        assert row["status"] == "UNSAT" and row["Q"] == 8
        assert row["sha256"] == m03_artifact_hashes[name]
        document = m03_artifacts[name]
        if number in supplement_numbers:
            assert row["evidence_mode"] == "joint_map_supplement"
            assert name == f"scratch_theory_e72_source150_sync_jointmap_m03_sat_r{number}.json"
            assert document["summary"]["explicit_record_selection"] == [number]
            assert document["summary"]["ordinary_joint_map_filter_enabled"] is True
            assert len(document["results"]) == 1
            original = document["results"][0]
        else:
            assert row["evidence_mode"] == "direct_everydepth_local_pair"
            assert name == direct_name
            original = direct["results"][number]
        assert original[:6] == [number, row["mask_hex"], row["orbit_size"], 8, [0, 3], "UNSAT"]
        mode_counts[row["evidence_mode"]] += 1
        mode_mass[row["evidence_mode"]] += row["orbit_size"]
    assert mode_counts == {"direct_everydepth_local_pair": 69, "joint_map_supplement": 11}
    assert mode_mass == {"direct_everydepth_local_pair": 3_648, "joint_map_supplement": 448}
    source150_m03_complete_rejected = m03["catalog_coverage"]
    assert sum(mode_mass.values()) == source150_m03_complete_rejected == 4_096
    source150_open = (
        source150_open_before_m47_shards - source150_m47_shard_rejected
        - source150_m2_shard_rejected - source150_m6_shard_rejected
        - source150_m00_rejected - source150_m31_shard_rejected
        - source150_m10_joint_primary_rejected
        - source150_m03_complete_rejected
    )
    assert source150_open == 28_672
    source150_rejected = (
        source150_recurrence_rejected + source150_sync_rejected
        + source150_sync_joint_m01_rejected
        + source150_m47_shard_rejected + source150_m2_shard_rejected
        + source150_m6_shard_rejected + source150_m00_rejected
        + source150_m31_shard_rejected
        + source150_m10_joint_primary_rejected
        + source150_m03_complete_rejected
    )
    assert source150_rejected + source150_open == source150_total

    source150_macro_coverage = {
        (entry["state_orbit_number"], entry["signature_stabilizer_orbit_number"]):
            entry["signature_orbit_labelled_coverage"]
        for entry in by_source_entries[150]
    }
    source150_macro_rows = []
    for key, coverage in sorted(source150_macro_coverage.items()):
        stats = source150_recurrence["coverage"]["fully_rejected_macro_orbits"]
        rejected = list(key) in stats
        recurrence_stats = source150_recurrence_filter["per_macro"][
            f"{key[0]}:{key[1]}"
        ]
        assert recurrence_stats["input_mass"] == coverage
        assert recurrence_stats.get("rejected_mass", 0) == (coverage if rejected else 0)
        assert recurrence_stats.get("passing_mass", 0) == (0 if rejected else coverage)
        if rejected:
            status = "EXACT_RECURRENCE_ENUM_REJECTED"
        elif key in {(3, 0), (8, 0)}:
            assert coverage == 16_384
            status = "EXACT_SYNCHRONIZED_LOCALPAIR_ENUM_REJECTED"
        elif key == (0, 1):
            assert coverage == 65_536
            status = "EXACT_SYNCHRONIZED_JOINT_MAP_ENUM_REJECTED"
        elif key in {(0, 0), (0, 3), (1, 0), (2, 0), (3, 1), (4, 0), (6, 0), (7, 0)}:
            status = "EXACT_SYNCHRONIZED_LOCAL_CSP_ENUM_REJECTED"
        else:
            status = "OPEN"
        shard_rejected = source150_m47_shards["per_macro"].get(
            f"{key[0]}:{key[1]}", {}
        ).get("coverage", 0)
        if key == (2, 0):
            shard_rejected += source150_m2_shard_rejected
        if key == (6, 0):
            shard_rejected += source150_m6_shard_rejected
        if key == (0, 0):
            shard_rejected += source150_m00_rejected
        if key == (3, 1):
            shard_rejected += source150_m31_shard_rejected
        if key == (1, 0):
            assert coverage == source150_m10_joint_primary_rejected
            shard_rejected += source150_m10_joint_primary_rejected
        if key == (0, 3):
            assert coverage == source150_m03_complete_rejected
            shard_rejected += source150_m03_complete_rejected
        fully_rejected = status.startswith("EXACT_")
        excluded_coverage = coverage if fully_rejected else shard_rejected
        source150_macro_rows.append({
            "macro": list(key),
            "coverage": coverage,
            "status": status,
            "excluded_coverage": excluded_coverage,
            "open_coverage": coverage - excluded_coverage,
        })
    assert sum(row["coverage"] for row in source150_macro_rows
               if row["status"] == "EXACT_RECURRENCE_ENUM_REJECTED") \
        == source150_recurrence_rejected
    assert sum(row["coverage"] for row in source150_macro_rows
               if row["status"]
               == "EXACT_SYNCHRONIZED_LOCALPAIR_ENUM_REJECTED") \
        == source150_sync_rejected
    assert sum(row["coverage"] for row in source150_macro_rows
               if row["status"]
               == "EXACT_SYNCHRONIZED_JOINT_MAP_ENUM_REJECTED") \
        == source150_sync_joint_m01_rejected
    assert sum(row["excluded_coverage"] for row in source150_macro_rows
               if row["status"]
        == "EXACT_SYNCHRONIZED_LOCAL_CSP_ENUM_REJECTED") \
        == (source150_m47_shard_rejected + source150_m2_shard_rejected
            + source150_m6_shard_rejected + source150_m00_rejected
            + source150_m31_shard_rejected + source150_m10_joint_primary_rejected
            + source150_m03_complete_rejected)
    assert sum(row["open_coverage"] for row in source150_macro_rows) \
        == source150_open

    assert source332_parametric["status"] == "EXACT_PARAMETRIC_ENUMERATION_COMPLETE"
    assert source332_parametric["macro"]["source_row_index"] == 332
    source332_coverage = source332_parametric["macro"]["labelled_coverage"]
    assert source332_coverage == by_source_coverage[332] == 131_072
    parameters = [int(row["parameter"])
                  for row in source332_parametric["feasible_parameters"]]
    assert parameters == [-1, 0, 1]
    source332_formal = None
    if SOURCE332_FORMAL.exists():
        source332_formal = json.loads(SOURCE332_FORMAL.read_text(encoding="utf-8"))
        assert source332_formal["status"] == "FORMAL_AUDIT_PASS"
        assert source332_formal["macro_labelled_coverage"] == source332_coverage
        assert source332_formal["profile_parameters"] == [-1, 0, 1]
        assert source332_formal["profile_branch_count"] == 3
        assert source332_formal["profile_coverage_is_partition_not_sum"] is True

    zero_bp_sources = set(remaining["zero_BP_source_rows"])
    assert zero_bp_sources == {162, 222, 253, 257, 345, 474}
    assert 162 in breadth_sources
    zero_bp_only_sources = zero_bp_sources - breadth_sources
    assert zero_bp_only_sources == {222, 253, 257, 345, 474}
    assert all(remaining_rows[source]["raw_BP_survivors"] == 0
               for source in zero_bp_only_sources)
    zero_bp_only_coverage = sum(by_source_coverage[source]
                                for source in zero_bp_only_sources)
    assert zero_bp_only_coverage == 65_536

    active_sources = {source for source, row in remaining_rows.items()
                      if row["raw_BP_survivors"] > 0}
    assigned_active = breadth_sources | {133, 150, 248, 332, 630}
    other_open_sources_before_defect = active_sources - assigned_active
    assert len(other_open_sources_before_defect) == 31
    other_open_coverage_before_defect = sum(
        by_source_coverage[source] for source in other_open_sources_before_defect
    )
    other_open_bp_mass_before_defect = sum(
        remaining_rows[source]["raw_BP_survivors"]
        for source in other_open_sources_before_defect
    )
    assert other_open_coverage_before_defect == 483_328
    assert other_open_bp_mass_before_defect == 421_888

    assert open_defect_census["status"] \
        == "EXACT_E72_OPEN_DEFECT_RANK_CENSUS_COMPLETE"
    assert open_defect_census["selection"]["canonical_macro_count"] == 59
    assert open_defect_census["selection"]["coverage"] \
        == source150_open_before_m47_shards + other_open_coverage_before_defect \
        == 2_236_416
    defect_rejected_rows = [
        row for row in open_defect_census["rows"]
        if not row["passes_some_full_Gram_profile_kernel_port_CSP"]
    ]
    defect_rejected_keys = {tuple(row["key"]) for row in defect_rejected_rows}
    assert defect_rejected_keys == {
        (171, 0, 0), (1095, 0, 0), (1095, 0, 1), (1119, 0, 0)
    }
    defect_rejected_sources = {key[0] for key in defect_rejected_keys}
    assert defect_rejected_sources == {171, 1095, 1119}
    assert defect_rejected_sources <= other_open_sources_before_defect
    defect_rejected_coverage = sum(row["coverage"]
                                   for row in defect_rejected_rows)
    assert defect_rejected_coverage == 61_440
    assert open_defect_audit["status"] \
        == "INDEPENDENT_E72_OPEN_DEFECT_RANK_EXCLUSIONS_PASS"
    assert open_defect_audit["excluded_labelled_coverage"] \
        == defect_rejected_coverage
    assert open_defect_audit["inputs"][str(OPEN_DEFECT_CENSUS)] \
        == sha256(OPEN_DEFECT_CENSUS)

    other_open_sources = (
        other_open_sources_before_defect - defect_rejected_sources
    )
    assert len(other_open_sources) == 28
    other_open_coverage = sum(by_source_coverage[source]
                              for source in other_open_sources)
    other_open_bp_mass = sum(remaining_rows[source]["raw_BP_survivors"]
                             for source in other_open_sources)
    assert other_open_coverage == 421_888
    assert other_open_bp_mass == 360_448
    other_open_rows = [{
        "source_row_index": source,
        "partition_index": remaining_rows[source]["partition_index"],
        "compression_orbit_index": remaining_rows[source]["compression_orbit_index"],
        "Q_values": sorted(map(int, remaining_rows[source]["Q_histogram"])),
        "macro_coverage": by_source_coverage[source],
        "BP_survivor_mass": remaining_rows[source]["raw_BP_survivors"],
        "local_graph_orbits": remaining_rows[source]["local_graph_orbits"],
    } for source in sorted(other_open_sources)]

    source332_closed = source332_formal is not None
    source630_is_formal = source630_formal is not None
    classified_nonopen = (
        small_macro_coverage + by_source_coverage[134]
        + by_source_coverage[248] + by_source_coverage[133]
        + breadth_coverage + source630_coverage + zero_bp_only_coverage
        + source150_rejected + defect_rejected_coverage
        + (source332_coverage if source332_closed else 0)
    )
    unresolved = (
        source150_open + other_open_coverage
        + (0 if source332_closed else source332_coverage)
    )
    assert classified_nonopen + unresolved == GLOBAL_COVERAGE

    drat_backed = (
        small_macro_coverage + by_source_coverage[134] + by_source_coverage[248]
        + source133_nonregular + breadth_formal
        + (source630_coverage if source630_is_formal else 0)
        + (source332_coverage if source332_closed else 0)
    )
    exact_executable_not_drat = (
        source133_regular + zero_bp_only_coverage + source150_rejected
        + defect_rejected_coverage
    )
    computational_terminal_not_formal = (
        breadth_computational_only
        + (0 if source630_is_formal else source630_coverage)
    )
    assert drat_backed + exact_executable_not_drat \
        + computational_terminal_not_formal == classified_nonopen

    source332_record = {
        "source_row_index": 332,
        "macro_coverage_counted_once": source332_coverage,
        "profile_parameters": parameters,
        "profile_branch_count": 3,
        "profile_coverage_is_partition_not_sum": True,
        "status": (
            "FORMAL_AUDIT_PASS" if source332_closed
            else "PENDING_THREE_PROFILE_FORMAL_BRIDGE"
        ),
        "formal_audit": str(SOURCE332_FORMAL) if source332_closed else None,
        "formal_audit_sha256": sha256(SOURCE332_FORMAL)
            if source332_closed else None,
    }

    input_paths = [
        CATALOG, REMAINING, SMALL, SOURCE134, SOURCE248, SOURCE133_CHAIN,
        SOURCE133_MACRO4, BREADTH, SOURCE630, SOURCE150_NORM,
        SOURCE150_RECURRENCE_FILTER, SOURCE150_RECURRENCE,
        SOURCE150_SYNC, SOURCE150_SYNC_JOINT_M01, SOURCE332_PARAMETRIC,
        SOURCE150_M47_SHARDS, SOURCE150_M2_SHARDS, SOURCE150_M6_SHARDS,
        SOURCE150_M00_EXACT, SOURCE150_M31_SHARDS, SOURCE150_M10_JOINT_PRIMARY,
        SOURCE150_M03_COMPLETE,
        OPEN_DEFECT_CENSUS, OPEN_DEFECT_AUDIT,
    ]
    if source630_is_formal:
        input_paths.append(SOURCE630_FORMAL)
    if source332_closed:
        input_paths.append(SOURCE332_FORMAL)

    buckets = [
        {"name": "small_partitions", "coverage": small_macro_coverage,
         "status": "DRAT_BACKED_VIA_AUDITED_LOCAL_CENSUS"},
        {"name": "source134", "coverage": by_source_coverage[134],
         "status": "DRAT_VERIFIED_FULL_EXACT_CNF"},
        {"name": "source248", "coverage": by_source_coverage[248],
         "status": "DRAT_VERIFIED_FULL_EXACT_CNF"},
        {"name": "source133_regular", "coverage": source133_regular,
         "status": "EXACT_SOLVER_FREE_ENUMERATION"},
        {"name": "source133_nonregular", "coverage": source133_nonregular,
         "status": "DRAT_VERIFIED_FULL_EXACT_CNF"},
        {"name": "breadth_formal", "coverage": breadth_formal,
         "status": "DRAT_VERIFIED_FULL_EXACT_CNF"},
        {"name": "breadth_computational_only",
         "coverage": breadth_computational_only,
         "status": "TERMINAL_CADICAL_UNSAT_NO_CHECKED_PROOF_YET"},
        {"name": "source630", "coverage": source630_coverage,
         "status": ("DRAT_VERIFIED_FULL_EXACT_CNF" if source630_is_formal
                    else "TERMINAL_CADICAL_UNSAT_NO_CHECKED_PROOF_YET")},
        {"name": "other_zero_BP_rows", "coverage": zero_bp_only_coverage,
         "status": "EXACT_LOCAL_BP_ENUMERATION_EMPTY"},
        {"name": "source150_recurrence_rejected",
         "coverage": source150_recurrence_rejected,
         "status": "EXACT_SOLVER_FREE_RECURRENCE_ENUMERATION"},
        {"name": "source150_synchronized_localpair_rejected",
         "coverage": source150_sync_rejected,
         "status": "EXACT_SOLVER_FREE_SYNCHRONIZED_LOCALPAIR_ENUMERATION"},
        {"name": "source150_synchronized_joint_map_m01_rejected",
         "coverage": source150_sync_joint_m01_rejected,
         "status": "EXACT_SOLVER_FREE_SYNCHRONIZED_JOINT_MAP_ENUMERATION"},
        {"name": "source150_m47_exact_shards_rejected",
         "coverage": source150_m47_shard_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_SHARDS"},
        {"name": "source150_m2_exact_shards_rejected",
         "coverage": source150_m2_shard_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_SHARDS"},
        {"name": "source150_m6_exact_shards_rejected",
         "coverage": source150_m6_shard_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_SHARDS"},
        {"name": "source150_m00_exact_rejected",
         "coverage": source150_m00_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_ENUMERATION"},
        {"name": "source150_m31_exact_shards_rejected",
         "coverage": source150_m31_shard_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_PLUS_JOINT_MAP_SUPPLEMENT"},
        {"name": "source150_m10_joint_primary_rejected",
         "coverage": source150_m10_joint_primary_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_JOINT_MAP_PRIMARY"},
        {"name": "source150_m03_complete_rejected",
         "coverage": source150_m03_complete_rejected,
         "status": "EXACT_SOLVER_FREE_LOCAL_CSP_PLUS_JOINT_MAP_SUPPLEMENT"},
        {"name": "source150_open", "coverage": source150_open,
         "status": "OPEN"},
        {"name": "open_frontier_defect_rank_rejected",
         "coverage": defect_rejected_coverage,
         "status": "EXACT_POINTWISE_KERNEL_PORT_ENUMERATION"},
        {"name": "source332", "coverage": source332_coverage,
         "status": source332_record["status"]},
        {"name": "other_active_open_rows", "coverage": other_open_coverage,
         "status": "OPEN"},
    ]
    assert sum(bucket["coverage"] for bucket in buckets) == GLOBAL_COVERAGE

    result = {
        "status": "COMPLETE_E72_COVERAGE_INVENTORY_PASS",
        "coverage_unit": (
            "rooted labelled state-and-matching macro coverage; support orbit "
            "size is not multiplied, following the catalog convention"
        ),
        "inputs": {str(path): sha256(path) for path in input_paths},
        "global": {
            "canonical_macro_orbits": len(canonical),
            "catalog_coverage": GLOBAL_COVERAGE,
            "classified_nonopen_coverage": classified_nonopen,
            "unresolved_or_pending_coverage": unresolved,
            "DRAT_backed_coverage": drat_backed,
            "exact_executable_non_DRAT_coverage": exact_executable_not_drat,
            "computational_terminal_UNSAT_without_checked_proof": (
                computational_terminal_not_formal
            ),
            "all_coverage_counted_exactly_once": True,
        },
        "buckets": buckets,
        "source150": {
            "input_coverage": source150_total,
            "norm_collision_filter": "PASS_ALL_NO_EXCLUSION",
            "recurrence_rejected_coverage": source150_recurrence_rejected,
            "recurrence_open_before_synchronized_localpair": (
                source150_recurrence_open
            ),
            "synchronized_localpair_additional_rejected_coverage": (
                source150_sync_rejected
            ),
            "synchronized_joint_map_m01_additional_rejected_coverage": (
                source150_sync_joint_m01_rejected
            ),
            "m47_exact_shard_additional_rejected_coverage": (
                source150_m47_shard_rejected
            ),
            "m2_exact_shard_additional_rejected_coverage": (
                source150_m2_shard_rejected
            ),
            "m6_exact_shard_additional_rejected_coverage": (
                source150_m6_shard_rejected
            ),
            "m00_exact_additional_rejected_coverage": (
                source150_m00_rejected
            ),
            "m31_exact_shard_additional_rejected_coverage": (
                source150_m31_shard_rejected
            ),
            "m10_joint_primary_additional_rejected_coverage": (
                source150_m10_joint_primary_rejected
            ),
            "m03_complete_additional_rejected_coverage": (
                source150_m03_complete_rejected
            ),
            "open_coverage": source150_open,
            "macro_rows": source150_macro_rows,
            "recurrence_audit": str(SOURCE150_RECURRENCE),
            "recurrence_audit_sha256": sha256(SOURCE150_RECURRENCE),
            "synchronized_localpair_audit": str(SOURCE150_SYNC),
            "synchronized_localpair_audit_sha256": sha256(SOURCE150_SYNC),
            "synchronized_joint_map_m01_result": str(SOURCE150_SYNC_JOINT_M01),
            "synchronized_joint_map_m01_result_sha256": sha256(
                SOURCE150_SYNC_JOINT_M01
            ),
            "m47_exact_shard_audit": str(SOURCE150_M47_SHARDS),
            "m47_exact_shard_audit_sha256": sha256(SOURCE150_M47_SHARDS),
            "m2_exact_shard_audit": str(SOURCE150_M2_SHARDS),
            "m2_exact_shard_audit_sha256": sha256(SOURCE150_M2_SHARDS),
            "m6_exact_shard_audit": str(SOURCE150_M6_SHARDS),
            "m6_exact_shard_audit_sha256": sha256(SOURCE150_M6_SHARDS),
            "m00_exact_audit": str(SOURCE150_M00_EXACT),
            "m00_exact_audit_sha256": sha256(SOURCE150_M00_EXACT),
            "m31_exact_shard_audit": str(SOURCE150_M31_SHARDS),
            "m31_exact_shard_audit_sha256": sha256(SOURCE150_M31_SHARDS),
            "m10_joint_primary_audit": str(SOURCE150_M10_JOINT_PRIMARY),
            "m10_joint_primary_audit_sha256": sha256(SOURCE150_M10_JOINT_PRIMARY),
            "m03_complete_audit": str(SOURCE150_M03_COMPLETE),
            "m03_complete_audit_sha256": sha256(SOURCE150_M03_COMPLETE),
        },
        "source133_complete_bridge": {
            "total_coverage": by_source_coverage[133],
            "regular_solver_free_coverage": source133_regular,
            "regular_orbit_chain": [5138, 81, 1, 0],
            "nonregular_DRAT_coverage": source133_nonregular,
            "complete": True,
        },
        "source332": source332_record,
        "open_frontier_defect_rank": {
            "input_open_coverage": open_defect_census["selection"]["coverage"],
            "rejected_source_rows": sorted(defect_rejected_sources),
            "rejected_macro_keys": [list(key)
                                    for key in sorted(defect_rejected_keys)],
            "rejected_coverage": defect_rejected_coverage,
            "independent_audit": str(OPEN_DEFECT_AUDIT),
            "independent_audit_sha256": sha256(OPEN_DEFECT_AUDIT),
        },
        "breadth": {
            "source_rows": len(breadth_sources),
            "total_terminal_coverage": breadth_coverage,
            "formally_certified_coverage": breadth_formal,
            "computational_only_coverage": breadth_computational_only,
        },
        "other_zero_BP_source_rows": sorted(zero_bp_only_sources),
        "other_zero_BP_coverage": zero_bp_only_coverage,
        "other_active_open_rows": other_open_rows,
        "claim_boundary": (
            "This is a coverage partition, not a nonexistence proof. Checked "
            "DRAT, exact executable enumeration, and un-certified terminal SAT "
            "solver results are kept separate. All remain conditional on their "
            "audited reduction/encoder bridges. OPEN or PENDING coverage supplies "
            "neither a graph nor evidence of satisfiability."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Complete E72 macro-coverage inventory",
        "",
        "Status: **COMPLETE_E72_COVERAGE_INVENTORY_PASS**.",
        "",
        f"The canonical catalog coverage {GLOBAL_COVERAGE:,} is counted exactly "
        "once. Evidence classes are deliberately not conflated.",
        "",
        "| bucket | coverage | status |",
        "|:---|---:|:---|",
    ]
    lines.extend(
        f"| {bucket['name']} | {bucket['coverage']:,} | {bucket['status']} |"
        for bucket in buckets
    )
    lines.extend([
        "",
        f"Classified non-open: {classified_nonopen:,}. Unresolved/pending: "
        f"{unresolved:,}. Of the non-open coverage, {drat_backed:,} is DRAT-backed, "
        f"{exact_executable_not_drat:,} is covered by exact executable finite "
        f"enumeration, and {computational_terminal_not_formal:,} currently has "
        "only a terminal CaDiCaL UNSAT result.",
        "",
        "Source150 is split without overlap: the recurrence audit rejects "
        f"{source150_recurrence_rejected:,}, synchronized local-pair enumeration "
        f"rejects a further {source150_sync_rejected:,}, the synchronized "
        f"joint-map `(0,1)` enumeration rejects {source150_sync_joint_m01_rejected:,}, "
        f"complete exact shards of `(4,0)` and `(7,0)` reject "
        f"{source150_m47_shard_rejected:,}, complete exact shards of `(2,0)` "
        f"reject another {source150_m2_shard_rejected:,}, and complete exact "
        f"shards of `(6,0)` reject another {source150_m6_shard_rejected:,}, "
        f"the complete exact `(0,0)` sweep rejects another "
        f"{source150_m00_rejected:,}, "
        f"the complete exact `(3,1)` shards plus two exact joint-map "
        f"supplements reject another {source150_m31_shard_rejected:,}, "
        f"the complete `(1,0)` joint-primary shards reject another "
        f"{source150_m10_joint_primary_rejected:,}, "
        f"the complete `(0,3)` sweep plus all eleven joint-map supplements "
        f"reject another {source150_m03_complete_rejected:,}, "
        f"and {source150_open:,} "
        "remains open. Source133 is "
        "complete via the regular 5,138 -> 81 -> 1 -> 0 solver-free chain plus "
        "the nonregular DRAT proof.",
        "",
        "The pointwise equitability-kernel/port census then rejects source "
        "rows 171, 1095, and 1119 (four macros, 61,440 coverage) by an "
        "independently replayed exact finite certificate.",
        "",
        ("Source332 has a completed three-profile formal bridge; its shared "
         "131,072 coverage is counted once, not three times."
         if source332_closed else
         "Source332 remains pending in this snapshot: t=-1,0,1 are three Gram "
         "profiles of the same 131,072 macro coverage, which is counted once."),
        "",
        "Boundary: this ledger is not a proof that the Conway 99-graph does not "
        "exist. Open/pending rows remain, and evidence classes retain their "
        "certificate qualifications.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "catalog_coverage": GLOBAL_COVERAGE,
        "classified_nonopen": classified_nonopen,
        "unresolved_or_pending": unresolved,
        "DRAT_backed": drat_backed,
        "source332": source332_record["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
