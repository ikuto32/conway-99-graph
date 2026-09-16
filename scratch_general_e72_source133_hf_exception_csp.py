"""Exact H/F plus exceptional-row q-recurrence CSP for source 133.

The input records already contain every exceptional--exceptional edge and
pass the induced-pair upper bound.  On the four regular macros, the theory
audit forces the two bottom--outside fibres U_i^5,U_i^6 to have types H,F
in one order.  This program also enforces the exceptional-vertex rows of

    (B + I) q = 12 c_0.

For fixed t-values on U_i^5 and U_i^6, every exceptional vertex in a fibre
disjoint from them chooses one neighbour in each U fibre.  The two chosen
t-values must have an exactly determined sum.  Conversely, the target
degrees in the four exceptional blocks incident with a U vertex are fixed
by its t-value.  The resulting finite problem factors by i and is checked
by exhaustive four-symbol maps, with memoization.  No ordinary-layer edge
needed by this CSP is relaxed or sampled.

This is a necessary local filter, not a construction of the remaining
ordinary graph.  Macro 4 is retained separately because its exceptional
fibres are not all matchings and the H/F theorem does not apply to it.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
THEORY = Path("scratch_theory_e72_k23_balance_audit.json")
OUTPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
REGULAR_MACROS = frozenset(range(4))
BOTTOM = (2, 3, 4)
OUTSIDE = (5, 6)

# Exact two-dimensional coordinates for u_2+u_3+u_4=0.  The cyclic
# directions agree with the convention in the theory note.
U = {2: (1, 0), 3: (0, 1), 4: (-1, -1)}
W = {
    2: (U[3][0] - U[4][0], U[3][1] - U[4][1]),
    3: (U[4][0] - U[2][0], U[4][1] - U[2][1]),
    4: (U[2][0] - U[3][0], U[2][1] - U[3][1]),
}
DIRECTION = {2: (3, 4), 3: (4, 2), 4: (2, 3)}

H_PATTERNS = tuple(sorted(set(itertools.permutations((-1, 0, 0, 1)))))
F_PATTERNS = tuple(sorted(set(itertools.permutations((-1, -1, 1, 1)))))
assert len(H_PATTERNS) == 12 and len(F_PATTERNS) == 6


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def add(left, right):
    return left[0] + right[0], left[1] + right[1]


def subtract(left, right):
    return left[0] - right[0], left[1] - right[1]


def scale(amount, value):
    return amount * value[0], amount * value[1]


def support(vertex):
    return tuple(sorted(symbol // 2 for symbol in vertex))


def adjacency_from_mask(vertex_count, pair_positions, mask):
    answer = [set() for _ in range(vertex_count)]
    while mask:
        low = mask & -mask
        bit = low.bit_length() - 1
        left, right = pair_positions[bit]
        answer[left].add(right)
        answer[right].add(left)
        mask ^= low
    return tuple(frozenset(row) for row in answer)


def signed_support_vector(fibre):
    root, bottom = fibre
    return scale(1 if root == 0 else -1, U[bottom])


def local_q_and_required_sums(vertices, pair_positions, mask):
    """Return q signs and exact T_j=t(U_j5)+t(U_j6) requirements."""

    adjacency = adjacency_from_mask(len(vertices), pair_positions, mask)
    c0 = tuple(signed_support_vector(support(vertex)) for vertex in vertices)
    q = tuple(
        (
            sum(c0[y][0] for y in adjacency[x]),
            sum(c0[y][1] for y in adjacency[x]),
        )
        for x in range(len(vertices))
    )
    eps = []
    required = {}
    for x, vertex in enumerate(vertices):
        fibre = support(vertex)
        _root, bottom = fibre
        if q[x] == W[bottom]:
            eps.append(1)
        elif q[x] == scale(-1, W[bottom]):
            eps.append(-1)
        else:
            raise AssertionError((vertex, q[x], W[bottom]))

        local_q_sum = (
            sum(q[y][0] for y in adjacency[x]),
            sum(q[y][1] for y in adjacency[x]),
        )
        residual = subtract(scale(12, c0[x]), add(q[x], local_q_sum))
        complement = tuple(value for value in BOTTOM if value != bottom)
        solutions = []
        for first in range(-2, 3):
            for second in range(-2, 3):
                value = add(scale(2 * first, W[complement[0]]),
                            scale(2 * second, W[complement[1]]))
                if value == residual:
                    solutions.append((first, second))
        if not solutions:
            return tuple(eps), None, {
                "vertex": list(vertex),
                "residual": list(residual),
                "complement_bottoms": list(complement),
                "reason": "NO_INTEGRAL_T_PAIR_IN_MINUS2_TO_2",
            }
        assert len(solutions) == 1, (vertex, residual, complement, solutions)
        for other_bottom, value in zip(complement, solutions[0]):
            required[(x, other_bottom)] = value
        # Strong exact consequence from the theory derivation.
        assert sorted(abs(value) for value in solutions[0]) == [1, 2]

    by_fibre = defaultdict(list)
    for x, value in enumerate(eps):
        by_fibre[support(vertices[x])].append(value)
    assert len(by_fibre) == 6
    assert all(sorted(row) == [-1, -1, 1, 1] for row in by_fibre.values())
    return tuple(eps), required, None


@lru_cache(maxsize=None)
def mappings_with_degrees(degrees):
    """All maps from four labelled sources with the prescribed target loads."""

    assert len(degrees) == 4 and sum(degrees) == 4
    answer = []
    for mapping in itertools.product(range(4), repeat=4):
        if tuple(mapping.count(target) for target in range(4)) == degrees:
            answer.append(mapping)
    assert answer
    return tuple(answer)


def collision_vector(mapping):
    """Six pair multiplicities created by one four-source map."""

    return tuple(int(mapping[left] == mapping[right])
                 for left, right in itertools.combinations(range(4), 2))


@lru_cache(maxsize=None)
def block_pair_domains(t5, t6, coefficient, required):
    """All collision signatures of exact maps to U_i^5 and U_i^6.

    One witness map pair is retained for every distinct six-entry collision
    vector.  This loses no information needed by the later exact same-fibre
    common-witness constraints.
    """

    degree5 = tuple(1 + coefficient * value for value in t5)
    degree6 = tuple(1 + coefficient * value for value in t6)
    answer = {}
    for mapping5 in mappings_with_degrees(degree5):
        collisions5 = collision_vector(mapping5)
        for mapping6 in mappings_with_degrees(degree6):
            if not all(t5[mapping5[x]] + t6[mapping6[x]] == required[x]
                       for x in range(4)):
                continue
            collisions6 = collision_vector(mapping6)
            signature = tuple(left + right
                              for left, right in zip(collisions5, collisions6))
            answer.setdefault(signature, (mapping5, mapping6))
    return tuple((signature, maps) for signature, maps in sorted(answer.items()))


def bottom_csp(vertices_by_fibre, required, bottom):
    """Enumerate feasible H/F t-patterns for U_bottom^5,U_bottom^6."""

    plus, minus = DIRECTION[bottom]
    source_fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
    source_rows = []
    for fibre in source_fibres:
        indices = vertices_by_fibre[fibre]
        row = tuple(required[(x, bottom)] for x in indices)
        side_sign = 1 if fibre[0] == 0 else -1
        direction_sign = 1 if fibre[1] == plus else -1
        coefficient = side_sign * direction_sign
        source_rows.append((fibre, coefficient, row))

    options = []
    for type5, patterns5, type6, patterns6 in (
        ("H", H_PATTERNS, "F", F_PATTERNS),
        ("F", F_PATTERNS, "H", H_PATTERNS),
    ):
        for t5 in patterns5:
            for t6 in patterns6:
                domains = []
                for fibre, coefficient, row in source_rows:
                    domain = block_pair_domains(t5, t6, coefficient, row)
                    if not domain:
                        break
                    domains.append((fibre, domain))
                else:
                    options.append({
                        "type5": type5,
                        "type6": type6,
                        "t5": t5,
                        "t6": t6,
                        "block_domains": tuple(domains),
                    })
    return tuple(options)


def requirement_key(vertices_by_fibre, required):
    rows = []
    for bottom in BOTTOM:
        for fibre in sorted(
            (fibre for fibre in vertices_by_fibre if bottom not in fibre)
        ):
            rows.append(tuple(required[(x, bottom)]
                              for x in vertices_by_fibre[fibre]))
    return tuple(rows)


def block_domain(option, fibre):
    return dict(option["block_domains"])[fibre]


def collision_compatible(left_domain, right_domain, target):
    right_signatures = {signature for signature, _maps in right_domain}
    for left_signature, left_maps in left_domain:
        complement = tuple(value - used
                           for value, used in zip(target, left_signature))
        if min(complement) < 0 or complement not in right_signatures:
            continue
        right_maps = dict(right_domain)[complement]
        return left_signature, left_maps, complement, right_maps
    return None


def same_fibre_pair_needs(vertices, adjacency, vertices_by_fibre):
    answer = {}
    for fibre, indices in vertices_by_fibre.items():
        row = []
        for left, right in itertools.combinations(indices, 2):
            target = 2 - len(set(vertices[left]) & set(vertices[right]))
            existing = int(right in adjacency[left]) + len(
                adjacency[left] & adjacency[right]
            )
            assert 0 <= existing <= target
            row.append(target - existing)
        assert sum(row) == 6
        answer[fibre] = tuple(row)
    return answer


def global_collision_csp(options_by_bottom, pair_needs):
    """Join the three bottom CSPs using exact same-fibre pair witnesses."""

    relation = {}
    for left_bottom, right_bottom in itertools.combinations(BOTTOM, 2):
        source_bottom = next(value for value in BOTTOM
                             if value not in (left_bottom, right_bottom))
        allowed = {}
        for left_index, left_option in enumerate(options_by_bottom[left_bottom]):
            mask = 0
            witnesses_by_right = {}
            for right_index, right_option in enumerate(
                options_by_bottom[right_bottom]
            ):
                fibre_witnesses = []
                for root in (0, 1):
                    fibre = (root, source_bottom)
                    witness = collision_compatible(
                        block_domain(left_option, fibre),
                        block_domain(right_option, fibre),
                        pair_needs[fibre],
                    )
                    if witness is None:
                        break
                    fibre_witnesses.append((fibre, witness))
                else:
                    mask |= 1 << right_index
                    witnesses_by_right[right_index] = tuple(fibre_witnesses)
            if mask:
                allowed[left_index] = (mask, witnesses_by_right)
        relation[(left_bottom, right_bottom)] = allowed

    options2 = options_by_bottom[2]
    options3 = options_by_bottom[3]
    options4 = options_by_bottom[4]
    count = 0
    first = None
    relation23 = relation[(2, 3)]
    relation24 = relation[(2, 4)]
    relation34 = relation[(3, 4)]
    for index2 in range(len(options2)):
        if index2 not in relation23 or index2 not in relation24:
            continue
        mask3 = relation23[index2][0]
        mask4 = relation24[index2][0]
        while mask3:
            low3 = mask3 & -mask3
            index3 = low3.bit_length() - 1
            mask3 ^= low3
            allowed34 = relation34.get(index3)
            if allowed34 is None:
                continue
            joint4 = mask4 & allowed34[0]
            count += joint4.bit_count()
            if first is None and joint4:
                index4 = (joint4 & -joint4).bit_length() - 1
                first = (index2, index3, index4)
    if first is None:
        return 0, None

    selected = {2: first[0], 3: first[1], 4: first[2]}
    edge_map_witnesses = []
    for left_bottom, right_bottom in itertools.combinations(BOTTOM, 2):
        left_index, right_index = selected[left_bottom], selected[right_bottom]
        pair_witnesses = relation[(left_bottom, right_bottom)][left_index][1][
            right_index
        ]
        for fibre, (_left_signature, left_maps,
                    _right_signature, right_maps) in pair_witnesses:
            edge_map_witnesses.append([
                list(fibre),
                left_bottom,
                list(left_maps[0]),
                list(left_maps[1]),
                right_bottom,
                list(right_maps[0]),
                list(right_maps[1]),
            ])
            # The exact T requirements have absolute values 1 and 2 at the
            # two complementary bottoms.  Thus the four selected U-neighbour
            # t-values contain respectively one and two nonzeros: exactly
            # three nonzero U neighbours at every exceptional vertex.
            left_option = options_by_bottom[left_bottom][left_index]
            right_option = options_by_bottom[right_bottom][right_index]
            for source_vertex in range(4):
                selected_t = (
                    left_option["t5"][left_maps[0][source_vertex]],
                    left_option["t6"][left_maps[1][source_vertex]],
                    right_option["t5"][right_maps[0][source_vertex]],
                    right_option["t6"][right_maps[1][source_vertex]],
                )
                assert sum(value != 0 for value in selected_t) == 3
    return count, {
        "option_indices_by_bottom": [selected[bottom] for bottom in BOTTOM],
        "edge_map_witnesses": edge_map_witnesses,
    }


def compact_option(option):
    return [
        option["type5"],
        list(option["t5"]),
        list(option["t6"]),
    ]


def run(limit=None) -> None:
    started = time.monotonic()
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    theory = json.loads(THEORY.read_text(encoding="utf-8"))
    assert theory["status"] == "EXACT_SUPPORT_ARITHMETIC_VERIFIED"
    assert theory["regular_macro_q_profile"]["forced_pairing"] == (
        "one H and one F for each bottom index"
    )
    vertices = tuple(tuple(vertex) for vertex in document["vertex_order"])
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    vertices_by_fibre = defaultdict(list)
    for x, vertex in enumerate(vertices):
        vertices_by_fibre[support(vertex)].append(x)
    vertices_by_fibre = {
        fibre: tuple(indices) for fibre, indices in vertices_by_fibre.items()
    }
    assert set(vertices_by_fibre) == {
        (root, bottom) for root in (0, 1) for bottom in BOTTOM
    }

    records = document["representatives"]
    if limit is not None:
        records = records[:limit]
    option_cache = {}
    joint_cache = {}
    survivors = []
    per_macro = defaultdict(Counter)
    failure_examples = []
    for number, record in enumerate(records):
        mask_hex, mass, q_value, macro = record
        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += mass
        if macro not in REGULAR_MACROS:
            stats["retained_nonregular_orbits"] += 1
            stats["retained_nonregular_mass"] += mass
            survivors.append([mask_hex, mass, q_value, macro, None])
            continue
        _eps, required, recurrence_failure = local_q_and_required_sums(
            vertices, pair_positions, int(mask_hex, 16)
        )
        if recurrence_failure is not None:
            stats["exception_recurrence_rejected_orbits"] += 1
            stats["exception_recurrence_rejected_mass"] += mass
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += mass
            if len(failure_examples) < 20:
                failure_examples.append({
                    "input_record_number": number,
                    "mask_hex": mask_hex,
                    "state_macro_number": macro,
                    "Q": q_value,
                    "failure": recurrence_failure,
                })
            continue
        key = requirement_key(vertices_by_fibre, required)
        if key not in option_cache:
            options_by_bottom = {
                bottom: bottom_csp(vertices_by_fibre, required, bottom)
                for bottom in BOTTOM
            }
            option_cache[key] = options_by_bottom
        options_by_bottom = option_cache[key]
        option_counts = tuple(len(options_by_bottom[bottom]) for bottom in BOTTOM)
        orientation_masks = tuple(
            (int(any(option["type5"] == "H"
                     for option in options_by_bottom[bottom]))
             | (2 * int(any(option["type5"] == "F"
                            for option in options_by_bottom[bottom]))))
            for bottom in BOTTOM
        )
        if not all(option_counts):
            stats["hf_map_rejected_orbits"] += 1
            stats["hf_map_rejected_mass"] += mass
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += mass
            if len(failure_examples) < 20:
                failure_examples.append({
                    "input_record_number": number,
                    "mask_hex": mask_hex,
                    "state_macro_number": macro,
                    "Q": q_value,
                    "bottom_option_counts": list(option_counts),
                    "failure": "NO_HF_MAP_ASSIGNMENT",
                })
            continue

        local_adjacency = adjacency_from_mask(
            len(vertices), pair_positions, int(mask_hex, 16)
        )
        pair_needs = same_fibre_pair_needs(
            vertices, local_adjacency, vertices_by_fibre
        )
        pair_key = (
            key,
            tuple(pair_needs[fibre] for fibre in sorted(pair_needs)),
        )
        if pair_key not in joint_cache:
            joint_cache[pair_key] = global_collision_csp(
                options_by_bottom, pair_needs
            )
        joint_count, joint_witness = joint_cache[pair_key]
        if joint_count:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += mass
            stats["sum_bottom_pattern_options"] += sum(option_counts)
            stats["sum_joint_bottom_option_triples"] += joint_count
            selected = joint_witness["option_indices_by_bottom"]
            witnesses = [
                compact_option(options_by_bottom[bottom][option_index])
                for bottom, option_index in zip(BOTTOM, selected)
            ]
            survivors.append([
                mask_hex,
                mass,
                q_value,
                macro,
                [
                    list(option_counts),
                    list(orientation_masks),
                    joint_count,
                    witnesses,
                    joint_witness["edge_map_witnesses"],
                ],
            ])
        else:
            stats["same_fibre_pair_exact_rejected_orbits"] += 1
            stats["same_fibre_pair_exact_rejected_mass"] += mass
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += mass
            if len(failure_examples) < 20:
                failure_examples.append({
                    "input_record_number": number,
                    "mask_hex": mask_hex,
                    "state_macro_number": macro,
                    "Q": q_value,
                    "bottom_option_counts": list(option_counts),
                    "failure": "NO_JOINT_SAME_FIBRE_PAIR_EXACT_ASSIGNMENT",
                })

    summary = {
        "input_records": len(records),
        "input_orbit_mass": sum(row[1] for row in records),
        "regular_input_orbits": sum(per_macro[m]["input_orbits"]
                                    for m in REGULAR_MACROS),
        "regular_input_mass": sum(per_macro[m]["input_mass"]
                                  for m in REGULAR_MACROS),
        "regular_passing_orbits": sum(per_macro[m]["passing_orbits"]
                                      for m in REGULAR_MACROS),
        "regular_passing_mass": sum(per_macro[m]["passing_mass"]
                                    for m in REGULAR_MACROS),
        "regular_rejected_orbits": sum(per_macro[m]["rejected_orbits"]
                                       for m in REGULAR_MACROS),
        "regular_rejected_mass": sum(per_macro[m]["rejected_mass"]
                                     for m in REGULAR_MACROS),
        "nonregular_macro4_retained_orbits": per_macro[4][
            "retained_nonregular_orbits"
        ],
        "nonregular_macro4_retained_mass": per_macro[4][
            "retained_nonregular_mass"
        ],
        "output_frontier_orbits": len(survivors),
        "output_frontier_mass": sum(row[1] for row in survivors),
        "distinct_requirement_CSPs_solved": len(option_cache),
        "distinct_joint_pair_CSPs_solved": len(joint_cache),
        "mapping_pair_cache": {
            "hits": block_pair_domains.cache_info().hits,
            "misses": block_pair_domains.cache_info().misses,
            "size": block_pair_domains.cache_info().currsize,
        },
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    complete = limit is None
    if complete:
        assert summary["input_records"] == 92_561
        assert summary["input_orbit_mass"] == 30_976_832
        assert summary["regular_input_orbits"] == 92_413
        assert summary["regular_input_mass"] == 30_938_816
        assert summary["nonregular_macro4_retained_orbits"] == 148
        assert summary["nonregular_macro4_retained_mass"] == 38_016
    result = {
        "status": "COMPLETE" if complete else "PARTIAL_PROBE",
        "model": (
            "source133 exact regular-macro H/F types, U target degrees, and "
            "all 24 exceptional-vertex (B+I)q=12c0 rows"
        ),
        "inputs": {
            str(INPUT): sha256(INPUT),
            str(THEORY): sha256(THEORY),
        },
        "record_fields": [
            "mask_hex", "labelled_orbit_size", "Q", "state_macro_number",
            "regular_CSP_detail_or_null",
        ],
        "regular_CSP_detail_fields": [
            "bottom_option_counts_(2,3,4)",
            "bottom_type_orientation_bitmasks_(2,3,4)",
            "joint_bottom_option_triple_count",
            "one_exact_t_witness_per_bottom",
            "twelve_exact_exception_to_U_map_witnesses",
        ],
        "witness_fields": [
            "type_on_U_i5", "t_on_U_i5_vertices", "t_on_U_i6_vertices",
            "(maps are stored in the following joint witness field)",
        ],
        "summary": summary,
        "per_macro": {
            str(macro): dict(sorted(stats.items()))
            for macro, stats in sorted(per_macro.items())
        },
        "failure_examples": failure_examples,
        "frontier": survivors,
        "checks": {
            "q_vectors_computed_directly_from_every_input_mask": True,
            "each_exceptional_fibre_eps_multiset_is_two_plus_two_minus": True,
            "each_exceptional_row_has_unique_integral_T_pair": True,
            "each_T_pair_has_absolute_values_one_and_two": True,
            "each_exceptional_vertex_has_exactly_three_nonzero_U_neighbours": True,
            "all_HF_t_patterns_exhausted": True,
            "all_four_symbol_maps_with_exact_target_degrees_exhausted": True,
            "all_same_exceptional_fibre_pair_witness_deficits_filled_exactly": True,
            "all_three_bottom_option_relations_joined_exactly": True,
            "macro4_not_subjected_to_regular_HF_assumption": True,
        },
        "claim_boundary": (
            "The frontier passes the H/F theorem, every exceptional row of "
            "the q recurrence, and exact same-exceptional-fibre pair witness "
            "counts.  The other ordinary rows, cross-fibre pair-upper checks, "
            "and full SRG SAT constraints remain to be imposed."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True),
          flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run(args.limit)


if __name__ == "__main__":
    main()
