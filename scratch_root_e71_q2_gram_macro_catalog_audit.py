"""Independent structural and coverage audit of the E71 Gram macro catalog."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
CENSUS = Path("scratch_root_e71_q2_gram_fast_expansion_signature_census.json")
PORT = Path("scratch_root_e71_q2_port_feasible_states.json")
COUNTS = Path("scratch_root_e71_q2_local_completion_counts.json")
SUPPORT_FILTER = Path("scratch_root_e71_unsigned_kernel_filter.json")
OUTPUT = Path("scratch_root_e71_q2_gram_macro_catalog_audit.json")
E72_CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
E72_CENSUS = Path("scratch_general_e72_q3_gram_fast_expansion_signature_census.json")
E72_ESTABLISHED_CATALOG_SHA256 = (
    "BED6A7F1258576E8028B6B17736FD91ED8E8D9A79D2E90FC744A07DAE14D6213"
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def row_key(row):
    return tuple(sorted(row["partition"], reverse=True)), row["compression_orbit_index"]


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    port = json.loads(PORT.read_text(encoding="utf-8"))
    counts = json.loads(COUNTS.read_text(encoding="utf-8"))
    support_filter = json.loads(SUPPORT_FILTER.read_text(encoding="utf-8"))
    assert catalog["status"] == census["status"] == "COMPLETE"
    assert catalog["model"] == "complete E0=71 support+overlap-Gram macro-branch catalog"
    assert catalog["inputs"] == [str(PORT), str(COUNTS), str(SUPPORT_FILTER)]
    assert catalog["signature_census_audit"]["sha256"] == sha256(CENSUS)

    passing_indices = {
        row["source_row_index"] for row in support_filter["rows"]
        if row["passes_exact_support_diagonal_psd_test"]
    }
    support_rows = [
        row for row in port["rows"]
        if row["locally_port_feasible_assignments"]
        and row["source_row_index"] in passing_indices
    ]
    assert len(support_rows) == 1_512
    assert sum(row["locally_port_feasible_assignments"] for row in support_rows) == 361_900
    support_keys = {row_key(row) for row in support_rows}
    assert len(support_keys) == len(support_rows)
    count_map = {row_key(row): row for row in counts["rows"]}
    assert support_keys <= count_map.keys()
    input_total = sum(
        count_map[key]["exact_overlap_completions"] for key in support_keys
    )
    assert input_total == 15_215_493_120
    assert census["summary"]["support_rows"] == len(support_rows)
    assert census["summary"]["input_overlap_completions"] == input_total
    assert census["summary"]["state_orbits"] == 14_607
    assert census["summary"]["nonempty_support_rows"] == 93
    assert census["summary"]["feasible_signature_products_on_state_representatives"] == 193
    assert census["summary"]["after_exact_overlap_Gram_filter"] == 61_112_320

    entries = catalog["macro_entries"]
    canonical = [row for row in entries if row["signature_stabilizer_canonical"]]
    assert len(entries) == 193
    assert len(canonical) == 180
    entry_keys = [
        (
            row["partition_index"], row["compression_orbit_index"],
            row["source_row_index"], row["state_orbit_number"],
            tuple(tuple(value) for value in row["overlap_block_totals"]),
        )
        for row in entries
    ]
    assert len(entry_keys) == len(set(entry_keys))
    assert all(row_key(row) in support_keys for row in entries)
    assert all(row["orbit_stabilizer_identity_verified"] for row in entries)
    for row in entries:
        matching_product = math.prod(
            group["matching_choice_count"]
            for group in row["group_signature_classes"]
        )
        assert matching_product == row["matching_completion_weight_per_state"]
        assert (
            row["labelled_state_matching_coverage"]
            == row["state_orbit_size"] * matching_product
        )
        assert (
            row["full_weighted_action_order"]
            == row["state_orbit_size"] * row["state_stabilizer_order"]
        )

    grouped = defaultdict(list)
    for row in entries:
        group_key = (
            row["source_row_index"], row["state_orbit_number"],
            row["signature_stabilizer_orbit_number"],
        )
        grouped[group_key].append(row)
    assert len(grouped) == len(canonical) == 180
    for rows in grouped.values():
        canonical_rows = [row for row in rows if row["signature_stabilizer_canonical"]]
        assert len(canonical_rows) == 1
        representative = canonical_rows[0]
        assert len(rows) == representative["signature_stabilizer_orbit_size"]
        assert all(
            row["signature_stabilizer_orbit_size"] == len(rows)
            and row["signature_orbit_labelled_coverage"]
            == representative["signature_orbit_labelled_coverage"]
            and row["signature_stabilizer_canonical_D"]
            == representative["signature_stabilizer_canonical_D"]
            for row in rows
        )
        assert representative["signature_orbit_labelled_coverage"] == sum(
            row["labelled_state_matching_coverage"] for row in rows
        )

    coverage = sum(row["labelled_state_matching_coverage"] for row in entries)
    canonical_coverage = sum(
        row["signature_orbit_labelled_coverage"] for row in canonical
    )
    assert coverage == canonical_coverage == 61_112_320
    q_histogram = Counter()
    canonical_q_histogram = Counter()
    for row in entries:
        q_histogram[row["Q"]] += row["labelled_state_matching_coverage"]
    for row in canonical:
        canonical_q_histogram[row["Q"]] += row["signature_orbit_labelled_coverage"]
    expected_q = Counter(
        {int(key): value for key, value in census["summary"]["Gram_Q_histogram"].items()}
    )
    assert q_histogram == canonical_q_histogram == expected_q
    nonempty_sources = {row["source_row_index"] for row in entries}
    census_nonempty_sources = {
        row["source_row_index"] for row in census["rows"]
        if row["after_exact_overlap_Gram_filter"]
    }
    assert nonempty_sources == census_nonempty_sources
    assert len(nonempty_sources) == 93

    # Regression guard: the generalized producer must retain the established
    # E72 macro payload and byte-level artifact hash used downstream.
    e72_catalog = json.loads(E72_CATALOG.read_text(encoding="utf-8"))
    e72_census = json.loads(E72_CENSUS.read_text(encoding="utf-8"))
    assert sha256(E72_CATALOG) == E72_ESTABLISHED_CATALOG_SHA256
    assert e72_catalog["model"] == "complete E0=72 support+overlap-Gram macro-branch catalog"
    e72_summary = e72_catalog["summary"]
    assert e72_summary["support_rows_before_overlap_Gram"] == 162
    assert e72_summary["state_orbits_before_overlap_Gram"] == 578
    assert e72_summary["Gram_feasible_macro_entries"] == 177
    assert e72_summary["macro_entries_mod_state_stabilizers"] == 163
    assert e72_summary["labelled_state_matching_coverage"] == 141_545_472
    assert e72_census["summary"]["input_overlap_completions"] == 596_148_224
    assert (
        e72_census["summary"]["after_exact_overlap_Gram_filter"]
        == e72_summary["labelled_state_matching_coverage"]
    )
    e72_entries = e72_catalog["macro_entries"]
    e72_keys = {
        (
            row["partition_index"], row["compression_orbit_index"],
            row["source_row_index"], row["state_orbit_number"],
            tuple(tuple(value) for value in row["overlap_block_totals"]),
        )
        for row in e72_entries
    }
    assert len(e72_entries) == len(e72_keys) == 177
    assert e72_summary["Q_histogram"] == e72_census["summary"]["Gram_Q_histogram"]

    output = {
        "status": "E71_GRAM_MACRO_CATALOG_AUDIT_PASS",
        "model": "independent E0=71 macro catalog structural/coverage audit",
        "inputs": {
            str(CATALOG): sha256(CATALOG),
            str(CENSUS): sha256(CENSUS),
            str(PORT): sha256(PORT),
            str(COUNTS): sha256(COUNTS),
            str(SUPPORT_FILTER): sha256(SUPPORT_FILTER),
            str(E72_CATALOG): sha256(E72_CATALOG),
            str(E72_CENSUS): sha256(E72_CENSUS),
        },
        "input_frontier": {
            "support_rows": len(support_rows),
            "port_feasible_state_assignments": 361_900,
            "exact_overlap_completions": input_total,
            "state_orbits": census["summary"]["state_orbits"],
        },
        "Gram_frontier": {
            "nonempty_support_rows": len(nonempty_sources),
            "macro_entries": len(entries),
            "macro_entries_mod_state_stabilizers": len(canonical),
            "labelled_state_matching_coverage": coverage,
            "Q_histogram": {str(key): value for key, value in sorted(q_histogram.items())},
        },
        "E72_regression": {
            "catalog_sha256": sha256(E72_CATALOG),
            "established_catalog_sha256": E72_ESTABLISHED_CATALOG_SHA256,
            "macro_entries": 177,
            "macro_entries_mod_state_stabilizers": 163,
            "labelled_state_matching_coverage": 141_545_472,
            "input_overlap_completions": 596_148_224,
            "byte_identical_artifact_preserved": True,
        },
        "checks": {
            "catalog_entries_have_distinct_global_keys": True,
            "all_state_orbit_stabilizer_identities": True,
            "all_signature_orbits_closed_and_partitioned": True,
            "one_canonical_entry_per_signature_orbit": True,
            "canonical_and_unquotiented_coverage_equal": True,
            "catalog_Q_histogram_matches_signature_census": True,
            "catalog_nonempty_source_set_matches_signature_census": True,
            "input_completion_total_matches_count_rows": True,
            "support_filter_intersection_reconstructed": True,
            "E72_catalog_regression_totals_unchanged": True,
            "E72_catalog_downstream_hash_preserved": True,
        },
        "claim_boundary": (
            "This audits macro materialization against the independently stored "
            "signature census and primary count inputs. It does not assert that "
            "any macro extends to a full 99-vertex SRG."
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], **output["Gram_frontier"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
