"""Targeted endpoint-label compatibility study at the T=0 boundary.

This file deliberately does *not* enumerate order-nine graphs.  It reads the
frozen 916 order-eight masks, counts one specified eight-vertex wedge motif,
and constructs a finite signed-relation control for the equations in one row
of M^2=21M.  The control is a boundary certificate, not a global projector and
not an srg(99,14,1,2).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, deque
from pathlib import Path

OUTPUT = Path("scratch_theory_k_triangle_endpoint_compatibility.json")
ENDPOINT = Path("scratch_theory_e0_zero_triangle_flag_relation.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def graph_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for bit, (left, right) in enumerate(itertools.combinations(range(order), 2)):
        if mask & (1 << bit):
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def triangles(rows: tuple[int, ...]) -> tuple[tuple[int, int, int], ...]:
    answer = []
    for triple in itertools.combinations(range(len(rows)), 3):
        if all(rows[left] & (1 << right)
               for left, right in itertools.combinations(triple, 2)):
            answer.append(triple)
    return tuple(answer)


def unmatched(rows: tuple[int, ...], left: tuple[int, ...],
              right: tuple[int, ...]) -> int | None:
    """Return the unmatched vertex of left for one matching of two cross edges."""

    if set(left) & set(right):
        return None
    degrees_left = [sum(bool(rows[v] & (1 << w)) for w in right) for v in left]
    degrees_right = [sum(bool(rows[w] & (1 << v)) for v in left) for w in right]
    if sorted(degrees_left) != [0, 1, 1] or sorted(degrees_right) != [0, 1, 1]:
        return None
    return left[degrees_left.index(0)]


def overlapping_k_wedges(mask: int) -> tuple[int, int]:
    """Count same/different-centre-colour K-wedges whose union has order 8."""

    rows = graph_rows(mask, 8)
    tris = triangles(rows)
    same = different = 0
    for centre in tris:
        for first, second in itertools.combinations(tris, 2):
            if first == centre or second == centre:
                continue
            if set(centre) & set(first) or set(centre) & set(second):
                continue
            if len(set(first) | set(second)) != 5:
                continue
            if len(set(centre) | set(first) | set(second)) != 8:
                continue
            endpoint_first = unmatched(rows, centre, first)
            endpoint_second = unmatched(rows, centre, second)
            if endpoint_first is None or endpoint_second is None:
                continue
            if endpoint_first == endpoint_second:
                same += 1
            else:
                different += 1
    return same, different


def bipartite_realization(left: tuple[int, ...], right: tuple[int, ...],
                          left_degrees: dict[int, int],
                          right_degrees: dict[int, int],
                          forbidden: set[tuple[int, int]] | None = None
                          ) -> set[tuple[int, int]]:
    """Exact simple bipartite b-matching, returned with globally sorted ends."""

    forbidden = forbidden or set()
    assert sum(left_degrees.values()) == sum(right_degrees.values())
    source = ("source", -1)
    sink = ("sink", -1)
    residual: dict[tuple[str, int], dict[tuple[str, int], int]] = {}

    def arc(a: tuple[str, int], b: tuple[str, int], capacity: int) -> None:
        residual.setdefault(a, {})[b] = capacity
        residual.setdefault(b, {}).setdefault(a, 0)

    for vertex in left:
        arc(source, ("L", vertex), left_degrees[vertex])
    for vertex in right:
        arc(("R", vertex), sink, right_degrees[vertex])
    for a in left:
        for b in right:
            edge = tuple(sorted((a, b)))
            if edge not in forbidden:
                arc(("L", a), ("R", b), 1)
    value = 0
    while True:
        parents = {source: None}
        queue = deque([source])
        while queue and sink not in parents:
            node = queue.popleft()
            for target, capacity in residual[node].items():
                if capacity > 0 and target not in parents:
                    parents[target] = node
                    queue.append(target)
        if sink not in parents:
            break
        node = sink
        amount = sum(left_degrees.values())
        while parents[node] is not None:
            previous = parents[node]
            amount = min(amount, residual[previous][node])
            node = previous
        node = sink
        while parents[node] is not None:
            previous = parents[node]
            residual[previous][node] -= amount
            residual[node][previous] += amount
            node = previous
        value += amount
    assert value == sum(left_degrees.values())
    answer = set()
    for a in left:
        for b in right:
            if residual.get(("R", b), {}).get(("L", a), 0):
                answer.add(tuple(sorted((a, b))))
    assert Counter(a for edge in answer for a in edge if a in left) == Counter(
        {a: degree for a, degree in left_degrees.items() if degree}
    )
    assert Counter(a for edge in answer for a in edge if a in right) == Counter(
        {a: degree for a, degree in right_degrees.items() if degree}
    )
    return answer


def three_triangle_local_scan() -> dict[str, object]:
    """Only the 18^3 pairwise K configurations on three fixed triangles."""

    blocks = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    block_pairs = tuple(itertools.combinations(range(3), 2))
    choices = []
    for a, b in block_pairs:
        pair_choices = []
        for ua in blocks[a]:
            for ub in blocks[b]:
                va = tuple(v for v in blocks[a] if v != ua)
                vb = tuple(v for v in blocks[b] if v != ub)
                for ordering in itertools.permutations(vb):
                    pair_choices.append((ua, ub, tuple(zip(va, ordering))))
        assert len(pair_choices) == 18
        choices.append(pair_choices)
    histogram = Counter()
    examples = {}
    for selection in itertools.product(*choices):
        rows = [0] * 9
        graph_edges = [edge for block in blocks
                       for edge in itertools.combinations(block, 2)]
        for _, _, matching in selection:
            graph_edges.extend(matching)
        for a, b in graph_edges:
            rows[a] |= 1 << b
            rows[b] |= 1 << a
        colours = [[] for _ in blocks]
        for (a, b), (ua, ub, _) in zip(block_pairs, selection):
            colours[a].append(ua)
            colours[b].append(ub)
        compatible_corners = sum(a == b for a, b in colours)
        local_ok = all(
            (rows[a] & rows[b]).bit_count()
            <= (1 if rows[a] & (1 << b) else 2)
            for a, b in itertools.combinations(range(9), 2)
        )
        if not local_ok:
            histogram[(compatible_corners, "local_upper_fails")] += 1
            continue
        tris = triangles(tuple(rows))
        prism = False
        for first, second in itertools.combinations(tris, 2):
            if set(first) & set(second):
                continue
            if all(sum(bool(rows[v] & (1 << w)) for w in second) == 1
                   for v in first) and all(
                       sum(bool(rows[w] & (1 << v)) for v in first) == 1
                       for w in second):
                prism = True
                break
        outcome = "contains_prism" if prism else "local_upper_and_prism_free"
        histogram[(compatible_corners, outcome)] += 1
        if not prism and compatible_corners not in examples:
            examples[compatible_corners] = {
                "rows": rows,
                "endpoint_colours": colours,
                "edges": [list(edge) for edge in sorted(
                    tuple(sorted(edge)) for edge in graph_edges)],
            }
    assert sum(histogram.values()) == 18**3
    assert set(examples) == {0, 1, 2}
    assert histogram[(3, "contains_prism")] == 108
    assert histogram[(3, "local_upper_and_prism_free")] == 0
    return {
        "specified_triangles": [list(block) for block in blocks],
        "specified_K_pair_count": 3,
        "pair_matching_choices": 18,
        "complete_labeled_assignments": 18**3,
        "ambient_H9_census": False,
        "histogram": [
            {"same_endpoint_corners": count, "outcome": outcome,
             "labeled_assignments": value}
            for (count, outcome), value in sorted(histogram.items())
        ],
        "prism_free_local_controls": {
            str(count): example for count, example in sorted(examples.items())
        },
        "conclusion": (
            "For a K triangle, local lambda/mu upper caps plus prism absence "
            "allow 0, 1, or 2 equal-endpoint corners; they exclude 3. "
            "These nine-vertex controls do not impose all 231 projector rows "
            "or completion to a 99-vertex graph."
        ),
    }


def circulant_edges(vertices: tuple[int, ...], differences: tuple[int, ...]
                    ) -> set[tuple[int, int]]:
    size = len(vertices)
    answer = set()
    for index, vertex in enumerate(vertices):
        for difference in differences:
            target = vertices[(index + difference) % size]
            answer.add(tuple(sorted((vertex, target))))
    return answer


def local_signed_relation_control() -> dict[str, object]:
    """Build a 231-point relation with the endpoint row profile.

    Only the centre row/column of M^2=21M is imposed.  This is exactly the
    amount needed to test whether that localized equation forces a K triangle
    through the centre.
    """

    centre = 0
    plus_shell = tuple(range(1, 33))
    zero_shell = tuple(range(33, 195))
    minus_shell = tuple(range(195, 231))
    plus_edges: set[tuple[int, int]] = set()
    minus_edges: set[tuple[int, int]] = set()

    plus_edges.update((centre, vertex) for vertex in plus_shell)
    minus_edges.update((centre, vertex) for vertex in minus_shell)

    # The + shell and - shell each carry a 13-regular + relation.
    plus_edges |= circulant_edges(plus_shell, tuple(range(1, 7)) + (16,))
    plus_edges |= circulant_edges(minus_shell, tuple(range(1, 7)) + (18,))

    # Every A--C pair is nonzero: degrees (+,-)=(18,18) on A and
    # (16,16) on C.
    ac_plus = bipartite_realization(
        plus_shell, minus_shell,
        {v: 18 for v in plus_shell}, {v: 16 for v in minus_shell},
    )
    ac_all = {tuple(sorted(edge)) for edge in itertools.product(plus_shell,
                                                                 minus_shell)}
    plus_edges |= ac_plus
    minus_edges |= ac_all - ac_plus

    # A--B minus degrees are 18 on A, and 4^90 3^72 on B.
    b_mA = {v: 4 if index < 90 else 3
            for index, v in enumerate(zero_shell)}
    ab_minus = bipartite_realization(
        plus_shell, zero_shell,
        {v: 18 for v in plus_shell}, b_mA,
    )
    minus_edges |= ab_minus

    # C--B plus degrees are 3 on C and 1^108 0^54 on B.
    b_pC = {v: 1 if index < 108 else 0
            for index, v in enumerate(zero_shell)}
    cb_plus = bipartite_realization(
        minus_shell, zero_shell,
        {v: 3 for v in minus_shell}, b_pC,
    )
    plus_edges |= cb_plus

    # The centre-row equation at a B vertex is m_C=m_A+p_C.
    b_mC = {v: b_mA[v] + b_pC[v] for v in zero_shell}
    cb_minus = bipartite_realization(
        minus_shell, zero_shell,
        {v: 19 for v in minus_shell}, b_mC,
        forbidden=cb_plus,
    )
    minus_edges |= cb_minus

    # B--B plus: start 32-regular and delete a matching on the 108 vertices
    # having p_C=1, leaving degrees 31^108 32^54.
    bb_plus = circulant_edges(zero_shell, tuple(range(1, 17)))
    removed_plus_matching = {
        tuple(sorted((zero_shell[2 * index], zero_shell[2 * index + 1])))
        for index in range(54)
    }
    assert removed_plus_matching <= bb_plus
    bb_plus -= removed_plus_matching
    plus_edges |= bb_plus

    # B--B minus degrees are 27^90,29^18,30^54.  The alternating
    # 81+81 split balances each degree class and admits a simple b-matching
    # avoiding the already chosen + relation.
    bb_left, bb_right = zero_shell[::2], zero_shell[1::2]
    bb_degrees = {v: 36 - b_mA[v] - b_mC[v] for v in zero_shell}
    bb_minus = bipartite_realization(
        bb_left, bb_right,
        {v: bb_degrees[v] for v in bb_left},
        {v: bb_degrees[v] for v in bb_right},
        forbidden=bb_plus,
    )
    minus_edges |= bb_minus

    assert not plus_edges & minus_edges
    matrix = [[0] * 231 for _ in range(231)]
    for vertex in range(231):
        matrix[vertex][vertex] = 4
    for left, right in plus_edges:
        matrix[left][right] = matrix[right][left] = 1
    for left, right in minus_edges:
        matrix[left][right] = matrix[right][left] = -1

    profiles = []
    for vertex, row in enumerate(matrix):
        profile = Counter(row)
        assert profile == Counter({0: 162, -1: 36, 1: 32, 4: 1})
        profiles.append(profile)
    centre_products = [sum(matrix[centre][k] * matrix[k][vertex]
                           for k in range(231)) for vertex in range(231)]
    assert centre_products == [21 * value for value in matrix[centre]]

    # There is no - relation inside the centre's - shell, hence no K triangle
    # through the centre.  Give those 36 incident edges three endpoint colours.
    centre_colour_classes = [list(minus_shell[start:start + 12])
                             for start in (0, 12, 24)]
    same_colour_pairs = sum(len(block) * (len(block) - 1) // 2
                            for block in centre_colour_classes)
    centre_k_triangles = sum(
        matrix[left][right] == -1
        for left, right in itertools.combinations(minus_shell, 2)
    )
    same_relation_histogram = Counter()
    for block in centre_colour_classes:
        for left, right in itertools.combinations(block, 2):
            same_relation_histogram[matrix[left][right]] += 1
    assert same_colour_pairs == 198 and centre_k_triangles == 0

    # Explicitly record that the control is not a full projector.
    mismatch_count = 0
    mismatch_maximum = 0
    for left in range(231):
        for right in range(left, 231):
            product = sum(matrix[left][k] * matrix[k][right]
                          for k in range(231))
            residual = product - 21 * matrix[left][right]
            if residual:
                mismatch_count += 1
                mismatch_maximum = max(mismatch_maximum, abs(residual))
    assert mismatch_count > 0

    return {
        "vertex_count": 231,
        "centre": centre,
        "shells": {
            "M_plus_1": list(plus_shell),
            "M_zero": list(zero_shell),
            "M_minus_1_K_neighbors": list(minus_shell),
        },
        "plus_relation_edges": [list(edge) for edge in sorted(plus_edges)],
        "minus_relation_K_edges": [list(edge) for edge in sorted(minus_edges)],
        "relation_edge_counts": {
            "plus": len(plus_edges), "minus_K": len(minus_edges),
            "zero": 231 * 230 // 2 - len(plus_edges) - len(minus_edges),
        },
        "every_row_offdiagonal_profile": {"plus": 32, "zero": 162,
                                           "minus_K": 36},
        "centre_row_M2_equals_21M": True,
        "full_M2_equals_21M": False,
        "full_projector_residual_upper_triangle_nonzero_count": mismatch_count,
        "full_projector_residual_maximum_absolute_entry": mismatch_maximum,
        "centre_endpoint_colour_classes": centre_colour_classes,
        "centre_same_colour_wedges": same_colour_pairs,
        "centre_same_colour_relation_histogram": {
            str(key): value for key, value in sorted(same_relation_histogram.items())
        },
        "K_triangles_through_centre": centre_k_triangles,
        "compatible_K_triangles_through_centre": 0,
    }


def main() -> None:
    endpoint = json.loads(ENDPOINT.read_text(encoding="utf-8"))
    wave147 = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    masks8 = tuple(map(int, wave147["class_streams"]["8"]["canonical_masks"]))
    counts8 = {int(mask): int(count) for mask, count in
               wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(masks8) == len(set(masks8)) == len(counts8) == 916
    assert set(masks8) == set(counts8)
    assert endpoint["endpoint"]["sum_E0"] == 0
    assert endpoint["triangle_projector_and_quotient"]["K_simple_regular_degree"] == 36

    weighted_same = weighted_different = 0
    active = []
    for mask in masks8:
        same, different = overlapping_k_wedges(mask)
        if same or different:
            active.append([mask, counts8[mask], same, different])
            weighted_same += counts8[mask] * same
            weighted_different += counts8[mask] * different

    triangles_count = 231
    same_per_triangle = 3 * (12 * 11 // 2)
    different_per_triangle = (36 * 35 // 2) - same_per_triangle
    total_same = triangles_count * same_per_triangle
    total_different = triangles_count * different_per_triangle
    assert 0 <= weighted_same <= total_same
    assert 0 <= weighted_different <= total_different

    control = local_signed_relation_control()
    three_triangle_scan = three_triangle_local_scan()
    result = {
        "status": "T0_ENDPOINT_K_TRIANGLE_COMPATIBILITY_LOCAL_BOUNDARY_PASS",
        "scope": {
            "conditional_endpoint": "sum_r E0(r)=0",
            "frozen_order8_classes_read": 916,
            "frozen_order8_classes_regenerated": False,
            "ambient_order9_census_generated": False,
            "R1_extension_attempted": False,
            "submission_txt_written": False,
        },
        "inputs_sha256": {str(path): sha256(path)
                          for path in (ENDPOINT, WAVE147, WAVE163)},
        "endpoint_label_counting": {
            "K_vertices": triangles_count,
            "K_degree": 36,
            "endpoint_colours_per_K_vertex": 3,
            "edges_of_each_endpoint_colour": 12,
            "same_colour_wedges_per_K_vertex": same_per_triangle,
            "same_colour_wedges_global": total_same,
            "different_colour_wedges_per_K_vertex": different_per_triangle,
            "different_colour_wedges_global": total_different,
            "closed_same_colour_identity": (
                "C_same=sum_{K-triangles Delta} c(Delta), where c(Delta) is "
                "the number of its same-endpoint-colour corners"
            ),
            "X_triangle_free_consequence": "c(Delta)<=2 for every K triangle",
            "therefore": "C_same<=2*tau_K",
        },
        "frozen_order8_overlap_count": {
            "motif": (
                "unordered K-wedge (U,T,V), centred at T, with T disjoint "
                "from U,V and |U intersect V|=1; split by equality of the "
                "two unmatched endpoints in T"
            ),
            "active_frozen_classes": len(active),
            "active_rows_mask_count_role_multiplicities": active,
            "universal_same_overlap_identity": (
                "x8[57358896]=sum_r D(r)=n3-z11/4; the unique same-colour "
                "overlap role is precisely a pair of X-neighbours with a "
                "common unmatched outer point, hence one Y[r,beta]=2 event"
            ),
            "same_colour_overlapping_outer_triangles": weighted_same,
            "different_colour_overlapping_outer_triangles": weighted_different,
            "same_colour_pairwise_disjoint_outer_triangles": total_same - weighted_same,
            "different_colour_pairwise_disjoint_outer_triangles": (
                total_different - weighted_different
            ),
            "interpretation": (
                "The frozen order-eight layer fixes only the overlapping-outer-"
                "triangle part.  Whether a pairwise-disjoint same-colour wedge "
                "closes by a K edge is an order-nine datum."
            ),
        },
        "M2_edge_equation": {
            "for_a_K_edge_TU": (
                "a-b-c+d=-13, with a,b the +1/-1 relations from U into "
                "P(T), c,d the +1/-1 relations from U into K(T)\\{U}"
            ),
            "K_triangles_on_edge": "d",
            "positive_lower_bound_on_d_from_this_equation": None,
        },
        "exact_local_control": control,
        "targeted_three_triangle_scan": three_triangle_scan,
        "claim_boundary": {
            "endpoint_excluded": False,
            "K_triangle_forced_by_centre_row_M2_plus_all_row_profiles": False,
            "full_M2_implication_tested": False,
            "compatible_triangle_forced_by_tested_local_conditions": False,
            "reason": (
                "The exact control has the complete 4,+1,0,-1 row alphabet "
                "at all 231 points and satisfies the full centre row of "
                "M^2=21M, but has d=0 and hence no K triangle through that "
                "centre.  Frozen H8 data only removes/counts union-order-eight "
                "wedges; closure of the remaining disjoint wedges has union "
                "order nine."
            ),
            "qualification": (
                "The control intentionally fails other rows of M^2=21M and "
                "is not claimed to be a global integral projector, flag graph, "
                "or SRG completion."
            ),
            "smallest_missing_constraint": (
                "A cross-centre/order-nine constraint coupling the three "
                "endpoint partitions on a K triangle, or simultaneous validity "
                "of non-centre rows of M^2=21M with those partitions."
            ),
        },
    }
    save(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "overlap_same": weighted_same,
        "disjoint_same": total_same - weighted_same,
        "overlap_different": weighted_different,
        "local_control_K_triangles_at_centre": control["K_triangles_through_centre"],
        "full_projector_residual_nonzero": control[
            "full_projector_residual_upper_triangle_nonzero_count"
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
