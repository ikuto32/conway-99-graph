"""Independent exact audit of the source-2601 kernel/port contradiction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
CENSUS = Path("scratch_theory_e71_equitable_kernel_port_census.json")
OUTPUT = Path("scratch_theory_e71_source2601_kernel_port_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))]
            for i in range(len(left))]


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def key(row):
    return (int(row["source_row_index"]), int(row["state_orbit_number"]),
            int(row["signature_stabilizer_orbit_number"]))


def compression(entry, profile):
    exceptional = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    index = {support: local for local, support in enumerate(exceptional)}
    deficit = {tuple(item["support"]): int(item["deficit"])
               for item in entry["exceptional_supports"]}
    overlap = {tuple(sorted((int(i), int(j)))): int(value)
               for i, j, value in entry["overlap_block_totals"]}
    disjoint = {tuple(sorted((int(i), int(j)))): int(value)
                for i, j, value in profile["disjoint_D"]}
    C = [[0] * 21 for _ in range(21)]
    C0 = [[0] * 21 for _ in range(21)]
    for i, F in enumerate(SUPPORTS):
        C[i][i] = 2 * (4 - deficit.get(F, 0))
        C0[i][i] = 8
        for j in range(i + 1, 21):
            G = SUPPORTS[j]
            meeting = bool(set(F) & set(G))
            base = 0 if meeting else 4
            C0[i][j] = C0[j][i] = base
            if F in index and G in index:
                pair = tuple(sorted((index[F], index[G])))
                value = (overlap if meeting else disjoint)[pair]
            else:
                value = base
            C[i][j] = C[j][i] = value
    assert all(sum(row) == 48 for row in C)
    return exceptional, C, C0


def filtered_domains(geometry, oriented, entry):
    by_group = fast.matching_choices(geometry, oriented, entry["state_indices"], {})
    gram = fast.GramSignatureFilter(geometry)
    expected = {int(row["group"]): tuple(map(int, row["block_counts"]))
                for row in entry["group_signature_classes"]}
    domains = tuple(tuple(choice for choice in by_group[group]
                          if gram.signature(group, choice) == expected[group])
                    for group in range(7))
    assert [len(domain) for domain in domains] == [
        int(row["matching_choice_count"]) for row in entry["group_signature_classes"]
    ]
    return domains


def block_degree_sequence(geometry, choice, source, target):
    vertices = tuple(index for index, fibre in enumerate(geometry.fibre_index)
                     if fibre == source)
    degrees = []
    for vertex in vertices:
        degrees.append(sum(
            1 for left, right in choice.edges
            if (left == vertex and geometry.fibre_index[right] == target)
            or (right == vertex and geometry.fibre_index[left] == target)
        ))
    return tuple(degrees)


def main():
    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    census_raw = CENSUS.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    census = json.loads(census_raw)
    entries = {key(entry): entry for entry in catalog["macro_entries"]
               if entry["signature_stabilizer_canonical"]
               and int(entry["source_row_index"]) == 2601}
    profiles = {key(row): row for row in mining["profile_rows"]["71"]
                if int(row["source_row_index"]) == 2601}
    assert entries.keys() == profiles.keys() and len(entries) == 2

    fast.configure_generic(fast.PRESETS["e71gram"])
    _port, grouped = fast.input_rows(fast.PRESETS["e71gram"])
    source = next(source for rows in grouped.values() for source, _count in rows
                  if int(source["source_row_index"]) == 2601)
    audited = []
    for macro_key in sorted(entries):
        entry = entries[macro_key]
        profile = profiles[macro_key]
        exceptional, C, C0 = compression(entry, profile)
        Z = [[C0[i][j] - C[i][j] for j in range(21)] for i in range(21)]
        incidence = [[int(group in support) for group in range(7)]
                     for support in SUPPORTS]
        LLt = matmul(incidence, transpose(incidence))
        C2 = matmul(C, C)
        Z2 = matmul(Z, Z)
        K4 = [[192 * int(i == j) + 128 - 4 * C[i][j]
               - 32 * LLt[i][j] - C2[i][j] for j in range(21)]
              for i in range(21)]
        assert K4 == [[28 * Z[i][j] - Z2[i][j] for j in range(21)]
                      for i in range(21)]
        # Exact annihilating polynomials: Z(Z-8I)(Z-9I)^2=0 and
        # K4(K4-160I)(K4-171I)^2=0.
        for matrix, roots in ((Z, (0, 8, 9, 9)), (K4, (0, 160, 171, 171))):
            product = [[int(i == j) for j in range(21)] for i in range(21)]
            for root in roots:
                factor = [[matrix[i][j] - root * int(i == j)
                           for j in range(21)] for i in range(21)]
                product = matmul(product, factor)
            assert all(value == 0 for row in product for value in row)

        A, D = (SUPPORTS.index(support) for support in ((0, 2), (1, 4)))
        kernel = [0] * 21
        kernel[A], kernel[D] = 1, -1
        assert matvec(K4, kernel) == [0] * 21

        geometry = fast.RowGeometry(source)
        oriented = fast.oriented_assignment(geometry, entry["state_indices"])
        assert fast.internal_mask(geometry, oriented) == int(entry["internal_mask_hex"], 16)
        domains = filtered_domains(geometry, oriented, entry)
        local = {support: exceptional.index(support)
                 for support in ((0, 2), (1, 4), (0, 4), (1, 2))}
        contradictions = []
        for G in ((0, 4), (1, 2)):
            global_G = SUPPORTS.index(G)
            assert C[global_G][A] == C[global_G][D] == 2
            target_records = []
            for F in ((0, 2), (1, 4)):
                group = next(iter(set(G) & set(F)))
                sequences = {block_degree_sequence(
                    geometry, choice, local[G], local[F]
                ) for choice in domains[group]}
                assert len(sequences) == 1
                target_records.append({
                    "target_support": list(F),
                    "group": group,
                    "degree_sequence": list(next(iter(sequences))),
                    "domain_size": len(domains[group]),
                })
            assert target_records[0]["degree_sequence"] != target_records[1]["degree_sequence"]
            contradictions.append({
                "source_support": list(G),
                "target_records": target_records,
                "forced_equality_violated": True,
            })
        audited.append({
            "key": list(macro_key),
            "Q": int(entry["Q"]),
            "coverage": int(entry["signature_orbit_labelled_coverage"]),
            "matching_products_per_state": int(entry["matching_completion_weight_per_state"]),
            "Z_spectrum": [8, 9, 9],
            "K4_spectrum": [160, 171, 171],
            "kernel": "e_{02}-e_{14}",
            "contradictions": contradictions,
        })

    rejected2601 = [row for row in census["rows"]
                    if int(row["source_row_index"]) == 2601]
    assert len(rejected2601) == 2
    assert all(not row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]
               for row in rejected2601)
    assert sum(row["coverage"] for row in audited) == 262_144
    result = {
        "status": "INDEPENDENT_SOURCE2601_KERNEL_PORT_EXCLUSION_PASS",
        "inputs": {
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(MINING): hashlib.sha256(mining_raw).hexdigest().upper(),
            str(CENSUS): hashlib.sha256(census_raw).hexdigest().upper(),
        },
        "identity": "K4=16W^TW=28Z-Z^2",
        "pointwise_consequence": (
            "(e_02-e_14) in ker(K4) and C[G,02]=C[G,14]=2 imply "
            "deg(x,02)=deg(x,14) for every x in G"
        ),
        "macros": audited,
        "excluded_labelled_coverage": 262_144,
        "scope": "independent finite exact audit; no numerical eigensolver or SAT",
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **{
        "status": result["status"],
        "macros": len(audited),
        "excluded_labelled_coverage": result["excluded_labelled_coverage"],
    }}, sort_keys=True))


if __name__ == "__main__":
    main()
