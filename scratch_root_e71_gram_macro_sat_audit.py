"""Independent file-level audit of an E71 selector-gated exact SAT build."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from scratch_general_exact_sat import coordinates
import scratch_root_e71_gram_macro_sat as producer


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-row-index", type=int, required=True)
    parser.add_argument("--conflicts", type=int, default=10_000)
    args = parser.parse_args()
    source = args.source_row_index
    manifest_path = producer.MANIFEST
    build_path = Path(f"scratch_root_e71_source{source}_gram_macro_build.json")
    smoke_path = Path(
        f"scratch_root_e71_source{source}_gram_macro_aggregate_c{args.conflicts}.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    build = json.loads(build_path.read_text(encoding="utf-8"))
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    cnf_path = Path(build["cnf"])
    port, catalog, rows = producer.load_inputs()
    row = rows[source]
    raw = [item for item in catalog["macro_entries"]
           if int(item["source_row_index"]) == source]
    canonical = [item for item in raw if item["signature_stabilizer_canonical"]]
    labels, label_index, full_variables, _edge = coordinates()

    assert manifest["status"] == "E71_GRAM_MACRO_TO_EXACT_SAT_MANIFEST_PASS"
    assert manifest["catalog_macro_entries"] == 193
    assert manifest["canonical_selector_branches"] == 180
    assert manifest["labelled_state_matching_coverage"] == 61_112_320
    assert build["status"] == "E71_EXACT_SELECTOR_CNF_BUILD_AUDIT_PASS"
    assert build["source_row_index"] == source
    assert build["inputs"]["port_sha256"] == sha256(producer.PORT)
    assert build["inputs"]["catalog_sha256"] == sha256(producer.CATALOG)
    assert build["inputs"]["manifest_sha256"] == sha256(manifest_path)
    assert build["cnf_audit"]["sha256"] == sha256(cnf_path)
    assert smoke["build_sha256"] == sha256(build_path)
    assert smoke["cnf_sha256"] == sha256(cnf_path)

    raw_coverage = sum(int(item["labelled_state_matching_coverage"]) for item in raw)
    canonical_coverage = sum(int(item["signature_orbit_labelled_coverage"])
                             for item in canonical)
    assert raw_coverage == canonical_coverage == build["encoded_selector_coverage"]
    assert len(canonical) == build["canonical_selector_branches"]
    assert len(build["branches"]) == len(canonical)
    assert len({item["branch_fingerprint_sha256"] for item in build["branches"]}) == len(canonical)

    exceptional = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    expected_overlap_pairs = {
        pair for pair in itertools.combinations(range(len(exceptional)), 2)
        if set(exceptional[pair[0]]) & set(exceptional[pair[1]])
    }
    expected_implications = set()
    for entry, encoded in zip(canonical, build["branches"]):
        assert encoded["state_orbit_number"] == entry["state_orbit_number"]
        assert encoded["signature_stabilizer_orbit_number"] == entry[
            "signature_stabilizer_orbit_number"
        ]
        chosen = {
            tuple(sorted((label_index[tuple(sorted(map(int, left)))],
                          label_index[tuple(sorted(map(int, right)))])))
            for left, right in entry["internal_edges"]
        }
        positive = set(encoded["positive_internal_edge_variables"])
        negative = set(encoded["negative_internal_edge_variables"])
        assert positive.isdisjoint(negative)
        assert len(positive | negative) == 6 * len(exceptional)
        assert set(encoded["positive_internal_full_edge_variables"]) == {
            full_variables[pair] for pair in chosen
        }
        assert set(encoded["negative_internal_full_edge_variables"]) == {
            full_variables[min(u, v), max(u, v)]
            for support in exceptional
            for u, v in itertools.combinations(
                [index for index, label in enumerate(labels)
                 if producer.label_support(label) == support], 2
            )
            if (min(u, v), max(u, v)) not in chosen
        }
        assert len(positive) == sum(
            4 - int(item["deficit"]) for item in row["exceptional_supports"]
        )
        selector = int(encoded["selector"])
        expected_implications.update((-selector, variable) for variable in positive)
        expected_implications.update((-selector, -variable) for variable in negative)
        block_pairs = {
            (int(item["left_exceptional_index"]), int(item["right_exceptional_index"]))
            for item in encoded["overlap_blocks"]
        }
        assert block_pairs == expected_overlap_pairs
        assert encoded["overlap_block_cardinality_equalities"] == len(expected_overlap_pairs)

    ordinary = set(producer.SUPPORTS) - set(exceptional)
    expected_fixed = set()
    for support in ordinary:
        vertices = [u for u, label in enumerate(labels) if producer.label_support(label) == support]
        for u, v in itertools.combinations(vertices, 2):
            bits_u = {symbol // 2: symbol % 2 for symbol in labels[u]}
            bits_v = {symbol // 2: symbol % 2 for symbol in labels[v]}
            if sum(bits_u[group] != bits_v[group] for group in support) == 1:
                expected_fixed.add(full_variables[min(u, v), max(u, v)])
    assert expected_fixed == set(build["fixed_true_full_edge_variables"])
    assert len(expected_fixed) == 4 * (21 - len(exceptional))

    selectors = tuple(int(item["selector"]) for item in build["branches"])
    selector_positive = Counter()
    selector_negative = Counter()
    exact_clause_counts = Counter()
    declared_variables = declared_clauses = actual_clauses = maximum_variable = 0
    with cnf_path.open("r", encoding="ascii") as handle:
        for raw_line in handle:
            fields = raw_line.split()
            if not fields:
                continue
            if fields[0] == "p":
                assert fields[:2] == ["p", "cnf"]
                declared_variables, declared_clauses = map(int, fields[2:])
                continue
            body = tuple(map(int, fields[:-1]))
            assert fields[-1] == "0" and 0 not in body
            actual_clauses += 1
            if body:
                maximum_variable = max(maximum_variable, max(map(abs, body)))
            exact_clause_counts[body] += 1
            for selector in selectors:
                selector_positive[selector] += body.count(selector)
                selector_negative[selector] += body.count(-selector)
    assert actual_clauses == declared_clauses == build["cnf_audit"]["declared_clauses"]
    assert declared_variables == build["cnf_audit"]["declared_variables"]
    assert maximum_variable <= declared_variables
    assert exact_clause_counts[selectors] == 1
    for left, right in itertools.combinations(selectors, 2):
        assert exact_clause_counts[-left, -right] == 1
    assert all(exact_clause_counts[clause] >= 1 for clause in expected_implications)
    for encoded in build["branches"]:
        selector = int(encoded["selector"])
        assert selector_positive[selector] == 1
        assert selector_negative[selector] == (
            int(encoded["gated_clauses"]) + len(selectors) - 1
        )

    assert smoke["source_row_index"] == source and smoke["mode"] == "aggregate"
    assert smoke["total_selector_coverage"] == canonical_coverage
    assert smoke["verified_99_vertex_solution"] == smoke["submission_written"]
    if smoke["status"] == "SAT":
        assert smoke["verified_99_vertex_solution"]
        assert Path("submission.txt").is_file()
    else:
        assert not smoke["submission_written"]

    result = {
        "status": "E71_EXACT_SELECTOR_CNF_FILE_AUDIT_PASS",
        "source_row_index": source,
        "inputs": {
            "manifest": str(manifest_path), "manifest_sha256": sha256(manifest_path),
            "build": str(build_path), "build_sha256": sha256(build_path),
            "cnf": str(cnf_path), "cnf_sha256": sha256(cnf_path),
            "smoke": str(smoke_path), "smoke_sha256": sha256(smoke_path),
        },
        "catalog_macro_entries": len(raw),
        "canonical_selector_branches": len(canonical),
        "raw_coverage": raw_coverage,
        "canonical_coverage": canonical_coverage,
        "selector_exactly_one_clause_verified": True,
        "selector_negative_gating_occurrences_verified": True,
        "complete_internal_edge_assignments_verified": True,
        "overlap_block_partition_and_targets_verified": True,
        "ordinary_C4_fixed_full_edge_mapping_verified": True,
        "fixed_ordinary_edges": len(expected_fixed),
        "cnf_variables": declared_variables,
        "cnf_clauses": declared_clauses,
        "smoke_status": smoke["status"],
        "smoke_conflicts": smoke["records"][0]["stats_delta"].get("conflicts"),
        "direct_99_vertex_verification_required_if_sat": True,
        "submission_written": smoke["submission_written"],
    }
    output = Path(f"scratch_root_e71_source{source}_gram_macro_file_audit.json")
    producer.atomic_json(output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
