"""Independent exact audit of the four E72 open-frontier defect exclusions."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast
import scratch_theory_e71_defect_rank_probe as defect


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
CENSUS = Path("scratch_theory_e72_open_defect_rank_census.json")
OUTPUT = Path("scratch_theory_e72_open_defect_rank_exclusion_audit.json")
REJECTED_KEYS = {(171, 0, 0), (1095, 0, 0), (1095, 0, 1), (1119, 0, 0)}
SUPPORTS = defect.SUPPORTS


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def key(row):
    return (
        int(row["source_row_index"]),
        int(row["state_orbit_number"]),
        int(row["signature_stabilizer_orbit_number"]),
    )


def k4_for(entry, profile):
    exceptional, _index, C, _C0, Z = defect.build_compression(entry, profile)
    incidence = [[int(group in support) for group in range(7)]
                 for support in SUPPORTS]
    LLt = defect.matmul(incidence, defect.transpose(incidence))
    C2 = defect.matmul(C, C)
    Z2 = defect.matmul(Z, Z)
    K4 = [[192 * int(i == j) + 128 - 4 * C[i][j]
           - 32 * LLt[i][j] - C2[i][j] for j in range(21)]
          for i in range(21)]
    assert K4 == [[28 * Z[i][j] - Z2[i][j] for j in range(21)]
                  for i in range(21)]
    return exceptional, C, K4


def fixed_degree_vector(geometry, mask, local_source, local_target):
    adjacency = defect.mask_adjacency(
        len(geometry.vertices), geometry.pair_positions, mask
    )
    vertices = [index for index, fibre in enumerate(geometry.fibre_index)
                if fibre == local_source]
    return tuple(defect.degree_to_fibre(
        adjacency, vertex, local_target, geometry.fibre_index
    ) for vertex in vertices)


def audit_pair_difference(entry, profile, source, census_profile):
    exceptional, C, K4 = k4_for(entry, profile)
    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    internal = fast.internal_mask(geometry, oriented)
    domains = defect.exact_signature_domains(fast, geometry, oriented, entry)
    audited = []
    for certificate in census_profile["simple_equal_degree_kernel_certificates"]:
        G = tuple(certificate["source_support"])
        left = tuple(certificate["left_target_support"])
        right = tuple(certificate["right_target_support"])
        global_G = SUPPORTS.index(G)
        global_left = SUPPORTS.index(left)
        global_right = SUPPORTS.index(right)
        vector = [0] * 21
        vector[global_left], vector[global_right] = 1, -1
        assert defect.matvec(K4, vector) == [0] * 21
        assert C[global_G][global_left] == C[global_G][global_right]

        local_G = exceptional.index(G)
        local_left = exceptional.index(left)
        local_right = exceptional.index(right)
        group_left, group_right = G
        observed = set()
        for left_choice in domains[group_left]:
            for right_choice in domains[group_right]:
                mask = internal | left_choice.mask | right_choice.mask
                pair = (
                    fixed_degree_vector(geometry, mask, local_G, local_left),
                    fixed_degree_vector(geometry, mask, local_G, local_right),
                )
                observed.add(pair)
                assert pair[0] != pair[1]
        audited.append({
            "source_support": list(G),
            "target_supports": [list(left), list(right)],
            "equal_block_total": C[global_G][global_left],
            "distinct_port_incidence_pairs": len(observed),
            "port_incidence_pairs": [
                [list(left_degrees), list(right_degrees)]
                for left_degrees, right_degrees in sorted(observed)
            ],
            "all_violate_pointwise_equality": True,
        })
    assert audited
    return audited


def audit_source171_internal_parity(entry, profile, source):
    exceptional, C, K4 = k4_for(entry, profile)
    exceptional_global = [SUPPORTS.index(support) for support in exceptional]
    KE = [[K4[left][right] for right in exceptional_global]
          for left in exceptional_global]
    assert defect.rank(KE) == defect.rank(K4) == 2
    basis = defect.independent_rows(KE, 2)
    pivots = next(
        columns for columns in itertools.combinations(range(len(exceptional)), 2)
        if defect.rank([[basis[row][column] for column in columns]
                        for row in range(2)]) == 2
    )
    pivot_transpose = [[basis[row][column] for row in range(2)]
                       for column in pivots]

    source_local = exceptional.index((0, 1))
    source_global = SUPPORTS.index((0, 1))
    baseline = [C[source_global][target] for target in exceptional_global]
    ordinary = [target for target in range(21)
                if target not in exceptional_global]
    patterns = set()
    allowed = [tuple(4 * degree - baseline[column] for degree in range(5))
               for column in pivots]
    for pivot_values in itertools.product(*allowed):
        coefficients = defect.solve_square(pivot_transpose, pivot_values)
        residual = [sum(coefficients[row] * basis[row][column]
                        for row in range(2))
                    for column in range(len(exceptional))]
        if any(value.denominator != 1 for value in residual):
            continue
        degrees = []
        for value, total in zip(residual, baseline):
            numerator = int(value) + total
            if numerator % 4 or not 0 <= numerator // 4 <= 4:
                break
            degrees.append(numerator // 4)
        else:
            ordinary_degrees = [C[source_global][target] // 4
                                for target in ordinary]
            if sum(degrees) + sum(ordinary_degrees) == 12:
                patterns.add(tuple(degrees))
    expected = {
        (0, 2, 0, 0, 1, 1, 0, 0),
        (2, 0, 0, 0, 0, 0, 1, 1),
    }
    assert patterns == expected

    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    internal = fast.internal_mask(geometry, oriented)
    internal_degrees = fixed_degree_vector(
        geometry, internal, source_local, source_local
    )
    assert internal_degrees == (1, 1, 1, 1)
    assert {pattern[source_local] for pattern in patterns} == {0, 2}
    return {
        "support": [0, 1],
        "K4_rank": 2,
        "pivot_exceptional_indices": list(pivots),
        "all_integer_bounded_row_patterns": [list(row) for row in sorted(patterns)],
        "allowed_internal_degrees": [0, 2],
        "macro_internal_degree_vector": list(internal_degrees),
        "contradiction": "each macro vertex has internal degree 1",
    }


def main() -> None:
    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    census_raw = CENSUS.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    census = json.loads(census_raw)
    entries = {key(row): row for row in catalog["macro_entries"]
               if row["signature_stabilizer_canonical"] and key(row) in REJECTED_KEYS}
    profiles = {key(row): row for row in mining["profile_rows"]["72"]
                if key(row) in REJECTED_KEYS}
    assert set(entries) == set(profiles) == REJECTED_KEYS
    census_rows = {tuple(row["key"]): row for row in census["rows"]
                   if not row["passes_some_full_Gram_profile_kernel_port_CSP"]}
    assert set(census_rows) == REJECTED_KEYS

    fast.configure_generic(fast.PRESETS["e72gram"])
    _port, grouped = fast.input_rows(fast.PRESETS["e72gram"])
    sources = {int(row["source_row_index"]): row
               for rows in grouped.values() for row, _count in rows
               if int(row["source_row_index"]) in {171, 1095, 1119}}
    results = []
    for macro_key in sorted(REJECTED_KEYS):
        entry = entries[macro_key]
        profile = profiles[macro_key]
        census_profile = census_rows[macro_key]["profiles"][0]
        if macro_key[0] == 171:
            certificate = audit_source171_internal_parity(
                entry, profile, sources[macro_key[0]]
            )
            certificate_type = "rank_two_integer_row_internal_parity"
        else:
            certificate = audit_pair_difference(
                entry, profile, sources[macro_key[0]], census_profile
            )
            certificate_type = "kernel_pair_difference_port_incidence"
        results.append({
            "key": list(macro_key),
            "Q": int(entry["Q"]),
            "coverage": int(entry["signature_orbit_labelled_coverage"]),
            "certificate_type": certificate_type,
            "certificate": certificate,
        })

    assert sum(row["coverage"] for row in results) == 61_440
    result = {
        "status": "INDEPENDENT_E72_OPEN_DEFECT_RANK_EXCLUSIONS_PASS",
        "inputs": {
            str(CATALOG): sha256(catalog_raw),
            str(MINING): sha256(mining_raw),
            str(CENSUS): sha256(census_raw),
        },
        "identity": "K4=16W^TW=28Z-Z^2",
        "excluded_macros": len(results),
        "excluded_source_rows": 3,
        "excluded_labelled_coverage": 61_440,
        "rows": results,
        "method": (
            "Independent exact K4 reconstruction. Source171 enumerates its "
            "complete bounded integral rank-two row set; sources1095/1119 "
            "replay sparse kernel vectors and every relevant port incidence."
        ),
        "SAT_or_SMT_used": False,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), "status": result["status"],
                      "excluded_labelled_coverage": 61_440}, sort_keys=True))


if __name__ == "__main__":
    main()
