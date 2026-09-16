"""Solver-free E71 census of pointwise equitability-kernel versus port states.

For every integral PSD full-Gram profile retained by the E0=71 catalogue,
reconstruct C and K4=16 W^T W.  A vertex's scaled fibre-degree residual

    rho_x(F)=4 deg(x,F)-C[G,F],  x in fibre G,

must lie in row(K4).  For a fixed exceptional fibre G={g,h}, its internal
edges and the two group matching choices X_g,X_h determine all same/overlap
coordinates of its four degree rows.  Whether these rows extend to row(K4)
and sum to zero is therefore an exact binary relation R_G(X_g,X_h).

The seven group choices form a tiny binary CSP.  Empty CSP means that the
macro cannot be the rooted neighbourhood of an SRG, without enumerating its
full matching product or running a 99-vertex SAT solver.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast
import scratch_theory_e71_defect_rank_probe as defect


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
OUTPUT = Path("scratch_theory_e71_equitable_kernel_port_census.json")
SUPPORTS = defect.SUPPORTS


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def general_row_patterns(C, K4, exceptional):
    exceptional_global = [SUPPORTS.index(support) for support in exceptional]
    KE = [[K4[left][right] for right in exceptional_global]
          for left in exceptional_global]
    dimension = defect.rank(KE)
    assert dimension == defect.rank(K4)
    basis = defect.independent_rows(KE, dimension)
    pivots = next(
        columns for columns in itertools.combinations(range(len(exceptional)), dimension)
        if defect.rank([[basis[row][column] for column in columns]
                        for row in range(dimension)]) == dimension
    )
    pivot_transpose = [[basis[row][column] for row in range(dimension)]
                       for column in pivots]
    ordinary_global = [index for index in range(21)
                       if index not in exceptional_global]
    by_source = []
    for source, G in enumerate(SUPPORTS):
        baseline = [C[source][target] for target in exceptional_global]
        allowed = [tuple(4 * degree - baseline[column] for degree in range(5))
                   for column in pivots]
        patterns = []
        for pivot_values in itertools.product(*allowed):
            coefficients = defect.solve_square(pivot_transpose, pivot_values)
            residual = [sum(coefficients[row] * basis[row][column]
                            for row in range(dimension))
                        for column in range(len(exceptional))]
            if any(value.denominator != 1 for value in residual):
                continue
            residual = tuple(map(int, residual))
            degrees = []
            for value, total in zip(residual, baseline):
                numerator = value + total
                if numerator % 4 or not 0 <= numerator // 4 <= 4:
                    break
                degrees.append(numerator // 4)
            else:
                ordinary_degrees = []
                for target in ordinary_global:
                    assert C[source][target] % 4 == 0
                    ordinary_degrees.append(C[source][target] // 4)
                if sum(degrees) + sum(ordinary_degrees) == 12:
                    patterns.append({
                        "exceptional_degrees": degrees,
                        "scaled_W_row_on_exceptional": list(residual),
                        "pivot_scaled_W_coordinates": list(pivot_values),
                    })
        assert len({tuple(row["exceptional_degrees"]) for row in patterns}) == len(patterns)
        by_source.append({
            "source_support": list(G),
            "patterns": patterns,
            "pattern_count": len(patterns),
        })
    return dimension, pivots, by_source


def fibre_vertices(geometry, fibre):
    return tuple(index for index, value in enumerate(geometry.fibre_index)
                 if value == fibre)


def fixed_rows_for_fibre(geometry, mask, exceptional, source):
    adjacency = defect.mask_adjacency(
        len(geometry.vertices), geometry.pair_positions, mask
    )
    G = exceptional[source]
    rows = []
    for vertex in fibre_vertices(geometry, source):
        row = {}
        for target, F in enumerate(exceptional):
            if source == target or set(G) & set(F):
                row[target] = defect.degree_to_fibre(
                    adjacency, vertex, target, geometry.fibre_index
                )
        rows.append(row)
    return tuple(rows)


def fibre_extension_count(pattern_row, fixed):
    patterns = pattern_row["patterns"]
    candidates = [
        tuple(index for index, pattern in enumerate(patterns)
              if all(pattern["exceptional_degrees"][target] == value
                     for target, value in fixed[vertex].items()))
        for vertex in range(4)
    ]
    if any(not values for values in candidates):
        return 0
    count = 0
    for selected in itertools.product(*candidates):
        if all(sum(patterns[index]["scaled_W_row_on_exceptional"][column]
                   for index in selected) == 0
               for column in range(len(patterns[0]["scaled_W_row_on_exceptional"]))):
            count += 1
    return count


def relation_for_fibre(geometry, internal, exceptional, source, domains, patterns):
    left_group, right_group = exceptional[source]
    left_domain, right_domain = domains[left_group], domains[right_group]
    allowed_left = [0] * len(left_domain)
    signature_cache = {}
    configurations_histogram = Counter()
    for left_index, left in enumerate(left_domain):
        for right_index, right in enumerate(right_domain):
            fixed = fixed_rows_for_fibre(
                geometry, internal | left.mask | right.mask, exceptional, source
            )
            key = tuple(tuple(sorted(row.items())) for row in fixed)
            if key not in signature_cache:
                configuration_count = fibre_extension_count(patterns, fixed)
                signature_cache[key] = bool(configuration_count)
                configurations_histogram[configuration_count] += 1
            if signature_cache[key]:
                allowed_left[left_index] |= 1 << right_index
    allowed_right = [0] * len(right_domain)
    for left_index, mask in enumerate(allowed_left):
        for right_index in range(len(right_domain)):
            if (mask >> right_index) & 1:
                allowed_right[right_index] |= 1 << left_index
    return {
        "groups": [left_group, right_group],
        "allowed": {left_group: allowed_left, right_group: allowed_right},
        "allowed_pairs": sum(mask.bit_count() for mask in allowed_left),
        "possible_pairs": len(left_domain) * len(right_domain),
        "distinct_fixed_degree_signatures": len(signature_cache),
        "configuration_count_histogram": dict(sorted(configurations_histogram.items())),
    }


def solve_binary_csp(domains, relations):
    live0 = [(1 << len(domain)) - 1 for domain in domains]
    neighbors = defaultdict(list)
    for relation in relations:
        left, right = relation["groups"]
        neighbors[left].append((right, relation))
        neighbors[right].append((left, relation))
    stats = Counter()

    def allowed_mask(relation, source, option):
        return relation["allowed"][source][option]

    def propagate(live, queue):
        queue = deque(queue)
        while queue:
            source, target, relation = queue.popleft()
            stats["arc_revisions"] += 1
            target_live = live[target]
            revised = 0
            work = live[source]
            while work:
                low = work & -work
                option = low.bit_length() - 1
                if allowed_mask(relation, source, option) & target_live:
                    revised |= low
                work ^= low
            if revised == live[source]:
                continue
            live[source] = revised
            if not revised:
                return False
            for other, other_relation in neighbors[source]:
                if other != target:
                    queue.append((other, source, other_relation))
        return True

    initial_queue = []
    for relation in relations:
        left, right = relation["groups"]
        initial_queue.extend(((left, right, relation), (right, left, relation)))
    if not propagate(live0, initial_queue):
        return False, stats, None

    def visit(live):
        stats["search_nodes"] += 1
        candidates = [group for group, mask in enumerate(live)
                      if mask.bit_count() > 1]
        if not candidates:
            return live
        group = min(candidates, key=lambda value: live[value].bit_count())
        work = live[group]
        while work:
            low = work & -work
            work ^= low
            child = list(live)
            child[group] = low
            queue = [(other, group, relation)
                     for other, relation in neighbors[group]]
            if propagate(child, queue):
                answer = visit(child)
                if answer is not None:
                    return answer
        return None

    witness = visit(live0)
    return witness is not None, stats, (
        None if witness is None
        else [mask.bit_length() - 1 for mask in witness]
    )


def profile_key(row):
    return (
        int(row["source_row_index"]),
        int(row["state_orbit_number"]),
        int(row["signature_stabilizer_orbit_number"]),
    )


def analyze_profile(entry, profile, source, geometry, oriented, domains, internal):
    exceptional, _exceptional_index, C, _C0, Z = defect.build_compression(entry, profile)
    incidence = [[int(group in support) for group in range(7)] for support in SUPPORTS]
    LLt = defect.matmul(incidence, defect.transpose(incidence))
    C2 = defect.matmul(C, C)
    Z2 = defect.matmul(Z, Z)
    K4 = [[192 * int(i == j) + 128 - 4 * C[i][j] - 32 * LLt[i][j] - C2[i][j]
           for j in range(21)] for i in range(21)]
    assert K4 == [[28 * Z[i][j] - Z2[i][j] for j in range(21)]
                  for i in range(21)]
    dimension, pivots, patterns = general_row_patterns(C, K4, exceptional)
    pattern_by_support = {tuple(row["source_support"]): row for row in patterns}
    relations = [
        relation_for_fibre(
            geometry, internal, exceptional, local, domains,
            pattern_by_support[support],
        )
        for local, support in enumerate(exceptional)
    ]
    pair_difference_certificates = []
    for source_local, relation in enumerate(relations):
        if relation["allowed_pairs"]:
            continue
        G = exceptional[source_local]
        global_G = SUPPORTS.index(G)
        known_targets = [local for local, F in enumerate(exceptional)
                         if local == source_local or set(G) & set(F)]
        left_group, right_group = relation["groups"]
        for left_target, right_target in itertools.combinations(known_targets, 2):
            global_left = SUPPORTS.index(exceptional[left_target])
            global_right = SUPPORTS.index(exceptional[right_target])
            if C[global_G][global_left] != C[global_G][global_right]:
                continue
            if any(K4[row][global_left] != K4[row][global_right]
                   for row in range(21)):
                continue
            incidence_pairs = set()
            for left_choice in domains[left_group]:
                for right_choice in domains[right_group]:
                    fixed = fixed_rows_for_fibre(
                        geometry, internal | left_choice.mask | right_choice.mask,
                        exceptional, source_local,
                    )
                    incidence_pairs.add((
                        tuple(row[left_target] for row in fixed),
                        tuple(row[right_target] for row in fixed),
                    ))
            if incidence_pairs and all(left != right for left, right in incidence_pairs):
                pair_difference_certificates.append({
                    "source_support": list(G),
                    "left_target_support": list(exceptional[left_target]),
                    "right_target_support": list(exceptional[right_target]),
                    "equal_block_total": C[global_G][global_left],
                    "kernel_vector": "e_left-e_right",
                    "distinct_port_incidence_pair_count": len(incidence_pairs),
                    "all_port_incidence_pairs_violate_forced_equality": True,
                })
    feasible, stats, witness = solve_binary_csp(domains, relations)
    return {
        "parameter": profile["parameter"],
        "Z_rank": int(profile["Z_rank"]),
        "K4_rank": dimension,
        "pivot_exceptional_indices": list(pivots),
        "pattern_count_by_exceptional_fibre": [
            pattern_by_support[support]["pattern_count"] for support in exceptional
        ],
        "relations": [{
            "support": list(exceptional[local]),
            "groups": relation["groups"],
            "allowed_pairs": relation["allowed_pairs"],
            "possible_pairs": relation["possible_pairs"],
            "distinct_fixed_degree_signatures": relation[
                "distinct_fixed_degree_signatures"
            ],
            "configuration_count_histogram": relation["configuration_count_histogram"],
        } for local, relation in enumerate(relations)],
        "passes_kernel_port_CSP": feasible,
        "simple_equal_degree_kernel_certificates": pair_difference_certificates,
        "group_choice_witness": witness,
        "CSP_stats": dict(stats),
    }


def main():
    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    entries = {
        profile_key(entry): entry
        for entry in catalog["macro_entries"]
        if entry["signature_stabilizer_canonical"]
    }
    profiles_by_key = defaultdict(list)
    for profile in mining["profile_rows"]["71"]:
        profiles_by_key[profile_key(profile)].append(profile)
    assert set(profiles_by_key) <= set(entries)

    fast.configure_generic(fast.PRESETS["e71gram"])
    _port, grouped = fast.input_rows(fast.PRESETS["e71gram"])
    sources = {int(source["source_row_index"]): source
               for rows in grouped.values() for source, _count in rows}
    rows = []
    for number, key in enumerate(sorted(profiles_by_key), 1):
        entry = entries[key]
        source = sources[key[0]]
        geometry = fast.RowGeometry(source)
        oriented = fast.oriented_assignment(geometry, entry["state_indices"])
        internal = fast.internal_mask(geometry, oriented)
        assert internal == int(entry["internal_mask_hex"], 16)
        domains = defect.exact_signature_domains(fast, geometry, oriented, entry)
        profile_rows = [analyze_profile(
            entry, profile, source, geometry, oriented, domains, internal
        ) for profile in profiles_by_key[key]]
        passes = any(profile["passes_kernel_port_CSP"] for profile in profile_rows)
        rows.append({
            "key": list(key),
            "source_row_index": key[0],
            "Q": int(entry["Q"]),
            "coverage": int(entry["signature_orbit_labelled_coverage"]),
            "profile_count": len(profile_rows),
            "profiles": profile_rows,
            "macro_passes_some_full_Gram_profile_kernel_port_CSP": passes,
        })
        if number % 20 == 0:
            print(json.dumps({
                "processed": number,
                "macros": len(profiles_by_key),
                "passing": sum(row[
                    "macro_passes_some_full_Gram_profile_kernel_port_CSP"
                ] for row in rows),
            }), flush=True)

    rejected = [row for row in rows
                if not row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]]
    retained = [row for row in rows
                if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]]
    rejected_with_simple = [
        row for row in rejected
        if all(profile["simple_equal_degree_kernel_certificates"]
               for profile in row["profiles"])
    ]
    result = {
        "status": "EXACT_E71_EQUITABLE_KERNEL_PORT_CENSUS_COMPLETE",
        "inputs": {
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(MINING): hashlib.sha256(mining_raw).hexdigest().upper(),
        },
        "method": (
            "Exact row(K4) integer degree patterns; one binary relation per "
            "exceptional support; seven-variable AC-3/backtracking CSP."
        ),
        "summary": {
            "input_full_Gram_viable_canonical_macros": len(rows),
            "input_full_Gram_profiles": sum(row["profile_count"] for row in rows),
            "input_coverage": sum(row["coverage"] for row in rows),
            "rejected_macros": len(rejected),
            "rejected_coverage": sum(row["coverage"] for row in rejected),
            "retained_macros": len(retained),
            "retained_coverage": sum(row["coverage"] for row in retained),
            "rejected_source_rows": len({row["source_row_index"] for row in rejected}),
            "rejected_macros_with_simple_equal_degree_kernel_certificate": len(
                rejected_with_simple
            ),
            "rejected_coverage_with_simple_equal_degree_kernel_certificate": sum(
                row["coverage"] for row in rejected_with_simple
            ),
            "rejected_macros_requiring_general_rowspace_CSP": (
                len(rejected) - len(rejected_with_simple)
            ),
            "rejected_coverage_requiring_general_rowspace_CSP": (
                sum(row["coverage"] for row in rejected)
                - sum(row["coverage"] for row in rejected_with_simple)
            ),
            "rank_histogram_profiles": dict(Counter(
                str(profile["K4_rank"]) for row in rows for profile in row["profiles"]
            )),
            "Q_histogram_rejected_coverage": dict(Counter(
                {str(q): sum(row["coverage"] for row in rejected if row["Q"] == q)
                 for q in sorted({row["Q"] for row in rejected})}
            )),
        },
        "source2601_control": {
            "rows": [row for row in rows if row["source_row_index"] == 2601],
            "all_rejected": all(not row[
                "macro_passes_some_full_Gram_profile_kernel_port_CSP"
            ] for row in rows if row["source_row_index"] == 2601),
        },
        "source724_Q2_control": [
            row for row in rows if row["source_row_index"] == 724 and row["Q"] == 2
        ],
        "rows": rows,
        "claim_boundary": (
            "A sound one-root necessary filter.  Passing profiles are not claimed "
            "realizable; unresolved disjoint blocks and SRG pair equations are not "
            "included in this CSP."
        ),
    }
    # Correct the compact Q histogram (Counter(dict) would retain values but is
    # needlessly opaque in JSON).
    result["summary"]["Q_histogram_rejected_coverage"] = {
        str(q): sum(row["coverage"] for row in rejected if row["Q"] == q)
        for q in sorted({row["Q"] for row in rejected})
    }
    assert result["summary"]["input_coverage"] == 58_556_416
    assert result["summary"]["rejected_coverage"] + result["summary"][
        "retained_coverage"
    ] == result["summary"]["input_coverage"]
    assert result["source2601_control"]["all_rejected"]
    assert len(result["source724_Q2_control"]) == 1
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
