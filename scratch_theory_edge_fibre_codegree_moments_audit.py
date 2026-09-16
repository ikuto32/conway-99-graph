"""Independent replay of the edge fibre-codegree moment calculation."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path


SOURCE = Path("scratch_theory_edge_fibre_codegree_moments.json")
OUTPUT = Path("scratch_theory_edge_fibre_codegree_moments_audit.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def choose2(x: int) -> int:
    return x * (x - 1) // 2


def balanced_collision(total: int, bins: int) -> int:
    low, high_count = divmod(total, bins)
    return (bins - high_count) * choose2(low) + high_count * choose2(low + 1)


def packed_collision(total: int, bins: int, cap: int) -> int:
    full, remainder = divmod(total, cap)
    assert full <= bins and (full < bins or remainder == 0)
    return full * choose2(cap) + choose2(remainder)


def canonical_mask(edges: set[tuple[int, int]], order: int) -> int:
    pairs = tuple(itertools.combinations(range(order), 2))
    answer = 1 << len(pairs)
    for permutation in itertools.permutations(range(order)):
        moved = {tuple(sorted((permutation[x], permutation[y]))) for x, y in edges}
        value = sum(1 << bit for bit, pair in enumerate(pairs) if pair in moved)
        answer = min(answer, value)
    return answer


def necessary_bundle_floor(total: int) -> int | None:
    """Minimize using only cap 12 and '12 entries occur in triples'."""
    if total in (8314, 8315):
        return None
    best = None
    for number_twelve in range(0, 694, 3):
        remaining_count = 693 - number_twelve
        remaining_sum = total - 12 * number_twelve
        if remaining_sum < 0 or remaining_sum > 11 * remaining_count:
            continue
        value = number_twelve * choose2(12) + balanced_collision(
            remaining_sum, remaining_count
        ) if remaining_count else number_twelve * choose2(12)
        best = value if best is None else min(best, value)
    return best


def claimed_bundle_floor(total: int) -> int | None:
    if total in (8314, 8315):
        return None
    baseline = balanced_collision(total, 693)
    if total <= 7623 or total == 8316:
        return baseline
    residue = (total - 7623) % 3
    return baseline + ((3 - residue) % 3)


def main() -> None:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    assert data["status"] == "EDGE_FIBRE_CODEGREE_MOMENT_DECOMPOSITION_AND_BOUNDARY_PASS"
    for path, digest in data["inputs"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest().upper() == digest

    # Rebuild the two finite role graphs without using producer helpers.
    prism_edges = {
        (0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5),
        (0, 3), (1, 4), (2, 5),
    }
    side_edges = []
    for root in range(6):
        target_half = (3, 4, 5) if root < 3 else (0, 1, 2)
        omitted = root + 3 if root < 3 else root - 3
        side_edges.append(tuple(x for x in target_half if x != omitted))
    assert len({tuple(sorted(edge)) for edge in side_edges}) == 6
    assert set(map(tuple, map(sorted, side_edges))) == {
        edge for edge in prism_edges if (edge[0] < 3) == (edge[1] < 3)
    }
    h_delta_edges = {
        (0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4),
        (1, 5), (3, 5), (2, 6), (4, 6), (5, 6),
    }
    degrees = [sum(vertex in edge for edge in h_delta_edges) for vertex in range(7)]
    assert sorted(degrees) == [3, 3, 3, 3, 3, 3, 4]
    assert canonical_mask(h_delta_edges, 7) == 120568

    # Exhaust all 49 local (q,d) states and every stated pointwise bound.
    rebuilt = []
    for q in range(13):
        for d in range(q // 2 + 1):
            p = 12 - q
            h = p + d
            increment = p * d + choose2(d)
            assert choose2(h) == choose2(p) + increment
            assert 2 * d <= q
            assert increment >= choose2(d)
            assert increment <= 10 * d - 3 * choose2(d)
            assert choose2(h) <= 66 - d
            rebuilt.append((q, d, h, choose2(h)))
    assert len(rebuilt) == 49
    stored = [(row["q"], row["d"], row["H_e"], row["binom(H_e,2)"])
              for row in data["edgewise_decomposition"]["local_states"]]
    assert rebuilt == stored

    # Independent first/second q-moment envelope over 231 cells of cap 12.
    q_region = data["K_edge_exact_and_moment_bounds"]["q_moment_region"]
    assert q_region["n3_values_checked"] == 1387
    q_samples = {row["n3"]: row for row in q_region["samples"]}
    for n3 in range(0, 4159, 3):
        q_sum = 2 * n3 // 3
        q2_min = 2 * balanced_collision(q_sum, 231) + q_sum
        q2_max = 2 * packed_collision(q_sum, 231, 12) + q_sum
        assert q2_min <= q2_max
        assert q2_min % 2 == q2_max % 2 == 0
        if n3 in q_samples:
            assert q_samples[n3] == {
                "n3": n3, "sum_q": q_sum,
                "Q2_min": q2_min, "Q2_max": q2_max,
            }

    # Independently minimize with the necessary triple-12 property.  The
    # producer supplies explicit local q,d constructions, so equality of this
    # lower calculation with its formula certifies exactness.
    checked = 0
    unreachable = []
    stronger = []
    combined = []
    for total in range(8317):
        lower = necessary_bundle_floor(total)
        formula = claimed_bundle_floor(total)
        assert lower == formula
        if formula is None:
            unreachable.append(total)
            continue
        ordinary = balanced_collision(total, 693)
        if formula > ordinary:
            stronger.append((total, formula - ordinary))
        nonedge = balanced_collision(12474 - total, 4158)
        combined.append((formula + nonedge, total))
        checked += 1
    assert checked == 8315
    assert unreachable == [8314, 8315]
    assert len(stronger) == 460
    assert stronger[0] == (7624, 2) and stronger[-1] == (8312, 1)
    minimum = min(value for value, _ in combined)
    equality = [total for value, total in combined if value == minimum]
    assert minimum == 10395 and equality == list(range(1386, 2080))

    # Direct aggregate formulas on every producer sample.
    for sample in data["combined_with_global_collision"]["sample_relaxation_points"]:
        n3, q2, d_star, total = (
            sample["n3"], sample["Q2"], sample["D_star"], sample["T"]
        )
        base = Fraction(45738 - 23 * n3) + Fraction(3 * q2, 2)
        correction = Fraction(45738 + n3) - Fraction(3 * q2, 2)
        assert base.denominator == correction.denominator == 1
        cmin_d = balanced_collision(d_star, 693)
        cmax_d = packed_collision(d_star, 693, 6)
        lower = max(int(base) + cmin_d, claimed_bundle_floor(total))
        upper = min(
            int(base) + 10 * d_star - 3 * cmin_d,
            packed_collision(total, 693, 12),
            45738 - d_star,
            int(correction) + cmax_d,
        )
        assert lower == sample["lower"] and upper == sample["upper"]
        assert lower <= sample["K_edge"] <= upper

    # Endpoint and frozen order-eight-shadow boundary.
    endpoint = data["exact_boundary"]
    assert endpoint["n3"] == 4158 and endpoint["z11"] == 16632
    assert endpoint["Q2"] == 231 * 12 * 12
    assert endpoint["D_star"] == endpoint["T"] == endpoint["K_edge"] == 0
    beta_e, beta_n = Fraction(endpoint["beta_e"]), Fraction(endpoint["beta_n"])
    assert beta_e + beta_n == 45738
    assert endpoint["K_fb_at_H0"] == 4158 * choose2(3) == 12474
    assert endpoint["K_fb_at_H0"] >= minimum

    result = {
        "status": "EDGE_FIBRE_CODEGREE_MOMENT_INDEPENDENT_AUDIT_PASS",
        "input": {str(SOURCE): hashlib.sha256(raw).hexdigest().upper()},
        "all_upstream_hashes_verified": True,
        "prism_and_H_delta_roles_independently_enumerated": True,
        "local_q_d_states_checked": len(rebuilt),
        "q_first_second_moment_region_checked_n3_values": 1387,
        "T_values_checked": checked,
        "unreachable_T": unreachable,
        "bundle_floor_stronger_T_count": len(stronger),
        "combined_absolute_collision_floor": minimum,
        "combined_equality_T_interval": [min(equality), max(equality)],
        "strict_improvement_over_10395": False,
        "endpoint_T_zero_order8_shadow_boundary_verified": True,
        "conclusion": (
            "The edgewise codegree identity and every integer bound replay. "
            "They sharpen only the high-T profile and leave the exact T=0 "
            "relaxation boundary feasible."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT), "status": result["status"],
        "T_checked": checked, "combined_floor": minimum,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
