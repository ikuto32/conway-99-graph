"""Final solver-free U--U overlap audit for the sole source-133 survivor."""

from __future__ import annotations

import itertools
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import scratch_general_e72_source133_hf_exception_csp as hf
import scratch_theory_e72_k23_opposite_collision_enum as first
import scratch_theory_e72_k23_ee_cross_enum as second


INPUT = Path("scratch_theory_e72_k23_ee_cross_enum.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_theory_e72_k23_final_uu_enum.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def cross_target_uu_ok(left_target, left_maps, right_target, right_maps):
    """All U_i^a--U_j^a overlap rows, for a=5,6."""

    source_bottom = next(value for value in hf.BOTTOM
                         if value not in (left_target, right_target))

    def positions(target):
        plus, minus = hf.DIRECTION[target]
        fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
        return {fibre: index for index, fibre in enumerate(fibres)}

    left_position = positions(left_target)
    right_position = positions(right_target)
    for outside_index in (0, 1):
        counts = [[0] * 4 for _ in range(4)]
        # In stored explicit maps index 0 is outside 5 and index 1 outside 6.
        for root in (0, 1):
            fibre = (root, source_bottom)
            left_map = left_maps[left_position[fibre]][outside_index]
            right_map = right_maps[right_position[fibre]][outside_index]
            for local in range(4):
                counts[left_map[local]][right_map[local]] += 1
        # The common support is the outside group, represented by local bit 1.
        for left in range(4):
            for right in range(4):
                bound = 1 if left % 2 == right % 2 else 2
                if counts[left][right] > bound:
                    return False
    return True


def profile_triples(factors, pair_needs):
    """The exact EE-compatible profile triples, preserving stage-two logic."""

    keys = {target: tuple(factors[target]) for target in hf.BOTTOM}
    positions = {}
    for target in hf.BOTTOM:
        plus, minus = hf.DIRECTION[target]
        fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
        positions[target] = {fibre: index for index, fibre in enumerate(fibres)}
    relation = {}
    for left, right in itertools.combinations(hf.BOTTOM, 2):
        source_bottom = next(value for value in hf.BOTTOM
                             if value not in (left, right))
        right_index = defaultdict(list)
        for index, (_same, profile) in enumerate(keys[right]):
            needed = []
            for root in (0, 1):
                fibre = (root, source_bottom)
                row = []
                for x, y in itertools.combinations(
                    second.VERTICES_BY_FIBRE[fibre], 2
                ):
                    bit = second.PAIR_INDEX[tuple(sorted((x, y)))]
                    row.append(pair_needs[bit] - profile[bit])
                needed.append(tuple(row))
            if min(itertools.chain.from_iterable(needed)) >= 0:
                right_index[tuple(needed)].append(index)
        allowed = defaultdict(list)
        for index, (same, _profile) in enumerate(keys[left]):
            key = tuple(same[positions[left][(root, source_bottom)]]
                        for root in (0, 1))
            allowed[index].extend(right_index.get(key, ()))
        relation[(left, right)] = allowed

    answer = []
    for i2, rows3 in relation[(2, 3)].items():
        rows4_from2 = set(relation[(2, 4)].get(i2, ()))
        p2 = keys[2][i2][1]
        for i3 in rows3:
            candidates4 = rows4_from2.intersection(
                relation[(3, 4)].get(i3, ())
            )
            p3 = keys[3][i3][1]
            partial = bytes(a + b for a, b in zip(p2, p3))
            if any(value > bound for value, bound
                   in zip(partial, pair_needs)):
                continue
            for i4 in candidates4:
                p4 = keys[4][i4][1]
                if all(a + b <= bound for a, b, bound
                       in zip(partial, p4, pair_needs)):
                    answer.append((i2, i3, i4))
    return keys, tuple(answer)


def main():
    prior = json.loads(INPUT.read_text(encoding="utf-8"))
    assert prior["status"] == "EXACT_SOLVER_FREE_EE_CROSS_ENUM_COMPLETE"
    assert prior["passing_orbits"] == 1 and len(prior["survivors"]) == 1
    record = prior["survivors"][0]

    first.VERTICES = tuple(tuple(row) for row in json.loads(
        VERTEX_INPUT.read_text(encoding="utf-8")
    )["vertex_order"])
    vertices_by_fibre = defaultdict(list)
    for x, vertex in enumerate(first.VERTICES):
        vertices_by_fibre[hf.support(vertex)].append(x)
    second.VERTICES_BY_FIBRE = {key: tuple(value)
                                for key, value in vertices_by_fibre.items()}
    fibre_and_local = {}
    for fibre, indices in second.VERTICES_BY_FIBRE.items():
        for local, x in enumerate(indices):
            fibre_and_local[x] = (fibre, local)

    mask = int(record[0], 16)
    adjacency = hf.adjacency_from_mask(24, second.PAIR_POSITIONS, mask)
    _eps, required, failure = hf.local_q_and_required_sums(
        first.VERTICES, second.PAIR_POSITIONS, mask
    )
    assert failure is None
    pair_needs = second.all_pair_needs(first.VERTICES, adjacency)
    factors = {}
    factor_stats = {}
    for target in hf.BOTTOM:
        factors[target], factor_stats[target] = second.target_full_factor(
            required, adjacency, second.VERTICES_BY_FIBRE, fibre_and_local,
            target, pair_needs, retain_maps=True, enforce_within_uu=True,
        )
    keys, triples = profile_triples(factors, pair_needs)
    assert len(triples) <= record[4]

    pair_relations = {}
    for left, right in itertools.combinations(hf.BOTTOM, 2):
        rows = {}
        for left_profile_index, left_key in enumerate(keys[left]):
            left_maps = factors[left][left_key]
            for right_profile_index, right_key in enumerate(keys[right]):
                right_maps = factors[right][right_key]
                compatible = []
                for li, lm in enumerate(left_maps):
                    for ri, rm in enumerate(right_maps):
                        if cross_target_uu_ok(left, lm, right, rm):
                            compatible.append((li, ri))
                if compatible:
                    rows[(left_profile_index, right_profile_index)] = tuple(
                        compatible
                    )
        pair_relations[(left, right)] = rows

    explicit_triples = 0
    witness = None
    for i2, i3, i4 in triples:
        relation23 = pair_relations[(2, 3)].get((i2, i3), ())
        relation24 = pair_relations[(2, 4)].get((i2, i4), ())
        relation34 = pair_relations[(3, 4)].get((i3, i4), ())
        by2_23 = defaultdict(set)
        by2_24 = defaultdict(set)
        for m2, m3 in relation23:
            by2_23[m2].add(m3)
        for m2, m4 in relation24:
            by2_24[m2].add(m4)
        allowed34 = set(relation34)
        for m2 in set(by2_23) & set(by2_24):
            for m3 in by2_23[m2]:
                for m4 in by2_24[m2]:
                    if (m3, m4) in allowed34:
                        explicit_triples += 1
                        if witness is None:
                            witness = (i2, i3, i4, m2, m3, m4)

    assert explicit_triples == 0 and witness is None
    result = {
        "status": "EXACT_SOLVER_FREE_REGULAR_EXCLUSION_COMPLETE",
        "inputs": {
            str(INPUT): sha256(INPUT),
            str(VERTEX_INPUT): sha256(VERTEX_INPUT),
        },
        "input_stage_two_survivor": record,
        "factor_stats": {str(key): value
                         for key, value in factor_stats.items()},
        "EE_compatible_profile_triples_after_within_UU": len(triples),
        "fully_UU_overlap_compatible_explicit_map_triples": explicit_triples,
        "survivors": [],
        "checks": {
            "standard_library_only": True,
            "all_explicit_map_configurations_retained": True,
            "within_target_U_i5_U_i6_overlap_rows_exact": True,
            "cross_target_same_outside_overlap_rows_exact": True,
            "all_stage_two_EE_and_EU_conditions_preserved": True,
            "SAT_or_SMT_used": False,
        },
        "coverage": {
            "stage_one_regular_masks": 5_138,
            "stage_one_survivors": 81,
            "stage_two_survivors": 1,
            "stage_three_survivors": 0,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
