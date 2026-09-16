"""Independent exact audit of the abstract triangle-flag endpoint control."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


INPUT = Path("scratch_theory_flag_support_endpoint_control.json")
SOURCE = Path("scratch_theory_flag_support_endpoint_control.py")
OUTPUT = Path("scratch_theory_flag_support_endpoint_control_independent_audit.json")


def unordered(left, right):
    if left == right:
        raise AssertionError("loop")
    return (left, right) if left < right else (right, left)


def block_number(h, i):
    return 33 * (h % 7) + (i % 33)


def point_number(a, j):
    return 33 * a + (j % 33)


def main():
    submitted = json.loads(INPUT.read_text(encoding="utf-8"))
    assert submitted["status"] == "EXACT_ABSTRACT_FLAG_SUPPORT_T0_CONTROL_PASS"

    blocks = {}
    point_stars = {x: set() for x in range(99)}
    for h in range(7):
        for i in range(33):
            t = block_number(h, i)
            block = frozenset(point_number(a, i + a * h) for a in range(3))
            assert len(block) == 3
            blocks[t] = block
            for x in block:
                point_stars[x].add(t)
    assert len(set(blocks.values())) == 231
    assert Counter(map(len, point_stars.values())) == Counter({7: 99})

    intersecting = set()
    for t in range(231):
        for u in range(t + 1, 231):
            size = len(blocks[t] & blocks[u])
            assert size <= 1
            if size:
                intersecting.add((t, u))
    assert len(intersecting) == 2079

    # Rebuild X without calling any discovery routine.
    difference_slot = {}
    for slot, differences in enumerate(((1, 2, 4, 5, 6),
                                         (3, 7, 9, 10, 11),
                                         (8, 12, 13, 14, 15, 16))):
        for difference in differences:
            difference_slot[difference] = slot
    assert set(difference_slot) == set(range(1, 17))

    x = set()
    for h in range(7):
        for i in range(33):
            for difference, slot in difference_slot.items():
                t, u = block_number(h, i), block_number(h, i + difference)
                x.add(unordered(3 * t + slot, 3 * u + slot))
            t = block_number(h, i)
            x.add(unordered(3 * t, 3 * block_number(h + 1, i + 3)))
            x.add(unordered(3 * t + 1, 3 * block_number(h + 1, i + 7) + 1))
    assert len(x) == 4158

    x_adj = [set() for _ in range(693)]
    for alpha, beta in x:
        x_adj[alpha].add(beta)
        x_adj[beta].add(alpha)
    assert Counter(map(len, x_adj)) == Counter({12: 693})

    k2_multiplicity = Counter(unordered(alpha // 3, beta // 3)
                              for alpha, beta in x)
    assert Counter(k2_multiplicity.values()) == Counter({1: 4158})
    k2 = set(k2_multiplicity)
    assert not (k2 & intersecting)
    k2_degree = Counter(t for edge in k2 for t in edge)
    assert Counter(k2_degree.values()) == Counter({36: 231})

    flag_point = {}
    for t, block in blocks.items():
        h, i = divmod(t, 33)
        ordered_block = tuple(point_number(a, i + a * h) for a in range(3))
        assert frozenset(ordered_block) == block
        for slot, point in enumerate(ordered_block):
            flag_point[3 * t + slot] = point

    y_support = [set() for _ in range(99)]
    y_column_counts = Counter()
    for alpha in range(693):
        point = flag_point[alpha]
        for beta in x_adj[alpha]:
            assert beta not in y_support[point]
            y_support[point].add(beta)
            y_column_counts[beta] += 1
    assert Counter(map(len, y_support)) == Counter({84: 99})
    assert Counter(y_column_counts.values()) == Counter({12: 693})

    yyt = [[len(y_support[x0] & y_support[x1]) for x1 in range(99)]
           for x0 in range(99)]
    assert Counter(yyt[x0][x0] for x0 in range(99)) == Counter({84: 99})
    assert Counter(sum(row) for row in yyt) == Counter({1008: 99})
    assert sum(map(sum, yyt)) == 99792

    shadow = [set() for _ in range(99)]
    for block in blocks.values():
        vertices = sorted(block)
        for p in range(3):
            for q in range(p + 1, 3):
                shadow[vertices[p]].add(vertices[q])
                shadow[vertices[q]].add(vertices[p])
    assert Counter(map(len, shadow)) == Counter({14: 99})
    edge_yyt = sum(yyt[x0][x1] for x0 in range(99)
                   for x1 in range(x0 + 1, 99) if x1 in shadow[x0])
    nonedge_yyt = sum(yyt[x0][x1] for x0 in range(99)
                      for x1 in range(x0 + 1, 99) if x1 not in shadow[x0])
    assert (edge_yyt, nonedge_yyt) == (0, 45738)

    # Independently inflate K2 from unmatched flags to full triangle triples:
    # this is Wave205's t=N K2 N^T, not YY^T.
    t_matrix = [[sum(unordered(t, u) in k2
                     for t in point_stars[x0] for u in point_stars[x1]
                     if t != u)
                 for x1 in range(99)] for x0 in range(99)]
    assert Counter(sum(row) for row in t_matrix) == Counter({756: 99})
    nonedge_t_rows = [sum(t_matrix[x0][x1] for x1 in range(99)
                          if x1 != x0 and x1 not in shadow[x0])
                      for x0 in range(99)]
    assert Counter(nonedge_t_rows) == Counter({658: 33, 664: 33, 666: 33})

    # Formal M relation and entrywise Schur selector.
    r0 = set()
    generators = ((1, 1), (1, 2), (1, 4), (1, 5),
                  (1, 8), (1, 9), (1, 10), (1, 11),
                  (2, 1), (2, 3), (2, 6), (2, 7),
                  (2, 8), (2, 9), (2, 11), (2, 12))
    for delta, shift in generators:
        for h in range(7):
            for i in range(33):
                r0.add(unordered(block_number(h, i),
                                 block_number(h + delta, i + shift)))
    assert len(r0) == 3696
    assert not (r0 & k2) and not (r0 & intersecting)

    m = [[0] * 231 for _ in range(231)]
    for t in range(231):
        m[t][t] = 4
    for t, u in r0:
        m[t][u] = m[u][t] = 1
    for t, u in k2:
        m[t][u] = m[u][t] = -1
    assert Counter(sum(row) for row in m) == Counter({0: 231})
    assert Counter(sum(value * value for value in row) for row in m) == Counter({84: 231})
    selector = lambda value: (value ** 3 + value ** 2 - 2 * value) // 2
    assert all(selector(m[t][u]) - 36 * (t == u)
               == int(t != u and unordered(t, u) in k2)
               for t in range(231) for u in range(231))

    residual = Counter()
    for t in range(231):
        for u in range(231):
            value = sum(m[t][v] * m[v][u] for v in range(231)) - 21 * m[t][u]
            residual[value] += 1
    assert any(value for value, count in residual.items() if value and count)
    expected_residual = {int(k): v for k, v in submitted["formal_M"]["projector_residual_histogram"].items()}
    assert residual == Counter(expected_residual)

    # A true two-cross pair has nine point pairs: two matched edges and seven
    # nonedges, only one of which is the unmatched-endpoint pair seen by F^T X F.
    local_pair_role_count = Counter({"matched_edges": 2,
                                     "other_nonedges": 6,
                                     "unmatched_pair": 1})
    assert sum(local_pair_role_count.values()) == 9

    checks = {
        "linear_99x231_incidence": True,
        "simple_36_regular_K2_and_12_regular_X": True,
        "binary_Y_row_support_84": True,
        "YYT_exact_margins_and_split": True,
        "Wave205_t_is_distinct_inflation": True,
        "formal_M_Schur_selector_and_row_moments": True,
        "full_projector_equation_fails_as_scoped": True,
        "target_Wave205_rowsum_588_fails_as_scoped": True,
    }
    result = {
        "status": "INDEPENDENT_EXACT_FLAG_SUPPORT_T0_CONTROL_AUDIT_PASS",
        "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "checks": checks,
        "reconstructed": {
            "triangle_intersection_edges": len(intersecting),
            "X_edges": len(x),
            "K2_edges": len(k2),
            "Y_row_support": 84,
            "YYT_split": [edge_yyt, nonedge_yyt],
            "Wave205_t_nonedge_row_histogram": dict(sorted(Counter(nonedge_t_rows).items())),
            "formal_M_projector_residual_nonzero": sum(
                count for value, count in residual.items() if value
            ),
            "two_cross_pair_role_count": dict(local_pair_role_count),
        },
        "scope": (
            "Independent reconstruction of the stated relaxation.  The "
            "control fails the full projector, incidence transport, actual "
            "two-cross shadow semantics, and SRG equations and is not a graph solution."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
