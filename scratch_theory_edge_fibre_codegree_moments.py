"""Exact edge-fibre codegree decomposition and moment boundary.

For a graph edge e with triangle T(e), this proves and audits

    H_e = 12-q(T(e))+d_e,       0 <= 2d_e <= q(T(e)),

then derives integer lower/upper bounds for the edge part of the global
fibre-block collision count.  Only already-audited identities and finite
small-graph/local-state calculations are used; no order-eight classes are
regenerated.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path


OUTPUT = Path("scratch_theory_edge_fibre_codegree_moments.json")
INPUTS = (
    Path("scratch_theory_root_flag_union_audit.json"),
    Path("scratch_theory_root_yyt_augmented_relation.json"),
    Path("scratch_theory_root_yyt_order8_shadow.json"),
    Path("scratch_theory_global_fibre_block_gram.json"),
    Path("scratch_root_order8_e0_lower_bound_boundary.json"),
)

TRIANGLES = 231
EDGES = 693
NONEDGES = 4158
MAX_T = 8316
PAIR_INCIDENCES = 12474


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def choose2(value: int) -> int:
    return value * (value - 1) // 2


def minimum_choose2_sum(total: int, cells: int) -> int:
    quotient, remainder = divmod(total, cells)
    return cells * choose2(quotient) + remainder * quotient


def minimum_square_sum(total: int, cells: int) -> int:
    return 2 * minimum_choose2_sum(total, cells) + total


def maximum_choose2_sum(total: int, cells: int, cap: int) -> int:
    full, remainder = divmod(total, cap)
    assert full <= cells and (full < cells or remainder == 0)
    return full * choose2(cap) + choose2(remainder)


def maximum_square_sum(total: int, cells: int, cap: int) -> int:
    return 2 * maximum_choose2_sum(total, cells, cap) + total


def graph_mask(edges: set[tuple[int, int]], order: int) -> int:
    normalized = {tuple(sorted(edge)) for edge in edges}
    return sum(
        1 << bit
        for bit, pair in enumerate(itertools.combinations(range(order), 2))
        if pair in normalized
    )


def canonical_mask(edges: set[tuple[int, int]], order: int) -> int:
    answer = 1 << math.comb(order, 2)
    for permutation in itertools.permutations(range(order)):
        moved = {
            tuple(sorted((permutation[x], permutation[y]))) for x, y in edges
        }
        answer = min(answer, graph_mask(moved, order))
    return answer


def finite_role_audit() -> dict[str, object]:
    # Triangular prism: triangles 012 and 345, matching i--i+3.
    prism_edges = {
        (0, 1), (0, 2), (1, 2),
        (3, 4), (3, 5), (4, 5),
        (0, 3), (1, 4), (2, 5),
    }
    side_roles: dict[tuple[int, int], list[int]] = {
        tuple(sorted(edge)): []
        for edge in prism_edges
        if (edge[0] < 3) == (edge[1] < 3)
    }
    for root in range(6):
        opposite = range(3, 6) if root < 3 else range(0, 3)
        edge = tuple(sorted(vertex for vertex in opposite
                            if vertex % 3 != root % 3))
        assert len(edge) == 2
        side_roles[edge].append(root)
    assert len(side_roles) == 6
    assert all(len(roots) == 1 for roots in side_roles.values())
    assert sorted(root for roots in side_roles.values() for root in roots) == list(range(6))

    # The induced seven-vertex diagonal motif.  Vertex 0 is the unique
    # degree-four root; 5--6 is the unique edge in its nonneighbour set.
    h_delta_edges = {
        (0, 1), (0, 2), (1, 2),
        (0, 3), (0, 4), (3, 4),
        (1, 5), (3, 5), (2, 6), (4, 6), (5, 6),
    }
    degrees = [sum(vertex in edge for edge in h_delta_edges) for vertex in range(7)]
    assert degrees == [4, 3, 3, 3, 3, 3, 3]
    root_nonneighbours = {vertex for vertex in range(7)
                          if vertex != 0 and tuple(sorted((0, vertex))) not in h_delta_edges}
    assert root_nonneighbours == {5, 6}
    assert tuple(sorted(root_nonneighbours)) in h_delta_edges
    h_delta_mask = canonical_mask(h_delta_edges, 7)
    assert h_delta_mask == 120568

    return {
        "triangular_prism_canonical_mask": canonical_mask(prism_edges, 6),
        "side_root_for_each_triangle_edge": {
            f"{edge[0]}-{edge[1]}": roots[0]
            for edge, roots in sorted(side_roles.items())
        },
        "each_prism_supplies_one_side_root_to_each_of_its_six_triangle_edges": True,
        "H_delta_canonical_mask": h_delta_mask,
        "H_delta_degree_sequence": degrees,
        "intrinsic_root": 0,
        "intrinsic_diagonal_chord": [5, 6],
    }


def local_state_table() -> list[dict[str, int]]:
    rows = []
    for q in range(13):
        p = 12 - q
        for d in range(q // 2 + 1):
            h = p + d
            collision = choose2(h)
            increment = p * d + choose2(d)
            assert collision == choose2(p) + increment
            assert 2 * d <= q and 0 <= h <= 12
            assert choose2(d) <= increment
            assert increment <= 10 * d - 3 * choose2(d)
            assert collision <= 66 - d
            rows.append({
                "q": q,
                "p=12-q": p,
                "d": d,
                "H_e": h,
                "binom(H_e,2)": collision,
                "increment_over_binom(p,2)": increment,
                "augmented_offdiagonal_column_mass": 66 - d,
            })
    assert len(rows) == 49
    return rows


def triangle_record(q: int, d_values: tuple[int, int, int]) -> dict[str, object]:
    p = 12 - q
    assert 0 <= q <= 12
    assert all(0 <= d <= q // 2 for d in d_values)
    h_values = tuple(p + d for d in d_values)
    return {"q": q, "d": d_values, "h": h_values}


def bundle_construction(total: int) -> list[dict[str, object]] | None:
    """Construct a local (q,d)-relaxation attaining the exact K_edge floor."""
    assert 0 <= total <= MAX_T
    records: list[dict[str, object]] = []
    if total <= 7623:
        base, high_edges = divmod(total, EDGES)
        assert 0 <= base <= 11
        high_counts = [3] * (high_edges // 3)
        if high_edges % 3:
            high_counts.append(high_edges % 3)
        high_counts.extend([0] * (TRIANGLES - len(high_counts)))
        q = 12 - base
        for index, high_count in enumerate(high_counts):
            h = tuple([base + 1] * high_count + [base] * (3 - high_count))
            local_q = q
            if q % 2 and index == 0:
                # Flip the parity of sum_T q(T) without changing the three h's.
                local_q = q + 1
            p = 12 - local_q
            d_values = tuple(value - p for value in h)
            records.append(triangle_record(local_q, d_values))
    elif total <= 8313:
        excess = total - 7623
        residue = excess % 3
        if residue == 0:
            all_twelve = excess // 3
            correction = None
        elif residue == 1:
            all_twelve = (excess + 2) // 3
            correction = (0, 0, 1)  # h=(10,10,11), cost gap two.
        else:
            all_twelve = (excess + 1) // 3
            correction = (0, 1, 1)  # h=(10,11,11), cost gap one.
        records.extend(triangle_record(0, (0, 0, 0)) for _ in range(all_twelve))
        if correction is not None:
            records.append(triangle_record(2, correction))
        records.extend(
            triangle_record(2, (1, 1, 1))
            for _ in range(TRIANGLES - len(records))
        )
    elif total in (8314, 8315):
        return None
    else:
        assert total == 8316
        records = [triangle_record(0, (0, 0, 0)) for _ in range(TRIANGLES)]

    assert len(records) == TRIANGLES
    q_sum = sum(int(record["q"]) for record in records)
    assert q_sum % 2 == 0
    assert sum(sum(record["h"]) for record in records) == total
    return records


def bundle_collision_minimum(total: int) -> int | None:
    if total in (8314, 8315):
        return None
    baseline = minimum_choose2_sum(total, EDGES)
    if total <= 7623 or total == 8316:
        return baseline
    residue = (total - 7623) % 3
    return baseline + ((3 - residue) % 3)


def summarize_records(records: list[dict[str, object]]) -> dict[str, int]:
    q_sum = sum(int(record["q"]) for record in records)
    assert q_sum % 2 == 0
    n3 = 3 * q_sum // 2
    q2 = sum(int(record["q"]) ** 2 for record in records)
    d_star = sum(sum(record["d"]) for record in records)
    edge_sum = sum(sum(record["h"]) for record in records)
    k_edge = sum(choose2(h) for record in records for h in record["h"])
    return {"n3": n3, "Q2": q2, "D_star": d_star,
            "T": edge_sum, "K_edge": k_edge}


def moment_bounds(n3: int, q2: int, d_star: int, total: int) -> dict[str, int]:
    base = Fraction(45738 - 23 * n3) + Fraction(3 * q2, 2)
    correction = Fraction(45738 + n3) - Fraction(3 * q2, 2)
    assert base.denominator == correction.denominator == 1
    base = int(base)
    correction = int(correction)
    d_collision_min = minimum_choose2_sum(d_star, EDGES)
    d_collision_max = maximum_choose2_sum(d_star, EDGES, 6)
    bundle = bundle_collision_minimum(total)
    assert bundle is not None
    lower = max(base + d_collision_min, bundle)
    upper_candidates = {
        "q_Q2_D_upper": base + 10 * d_star - 3 * d_collision_min,
        "H_e_cap_12_upper": maximum_choose2_sum(total, EDGES, 12),
        "augmented_column_mass_upper": 45738 - d_star,
        "bad_mate_Q2_upper": correction + d_collision_max,
    }
    return {
        "prism_base": base,
        "bad_mate_correction_total": correction,
        "lower": lower,
        "upper": min(upper_candidates.values()),
        **upper_candidates,
    }


def main() -> None:
    inputs = {str(path): sha256(path) for path in INPUTS}
    loaded = {str(path): json.loads(path.read_text(encoding="utf-8")) for path in INPUTS}
    assert loaded[str(INPUTS[0])]["status"] == "TRIANGLE_FLAG_UNION_IDENTITY_FINITE_AUDIT_PASS"
    assert loaded[str(INPUTS[1])]["status"] == "AUGMENTED_FLAG_RELATION_AND_BAD_MATE_CAPACITY_PASS"
    assert loaded[str(INPUTS[2])]["status"] == "YYT_ORDER8_SHADOW_AND_FROZEN_SPAN_AUDIT_COMPLETE"
    assert loaded[str(INPUTS[3])]["status"] == "GLOBAL_FIBRE_BLOCK_GRAM_IDENTITIES_AND_BOUNDARY_COMPLETE"
    assert loaded[str(INPUTS[4])]["status"] == "ORDER8_E0_POSITIVE_LOWER_BOUND_BOUNDARY_PASS"

    role_audit = finite_role_audit()
    states = local_state_table()

    q_moment_ranges = []
    for n3_value in range(0, 4159, 3):
        q_sum = 2 * n3_value // 3
        q2_minimum = minimum_square_sum(q_sum, TRIANGLES)
        q2_maximum = maximum_square_sum(q_sum, TRIANGLES, 12)
        assert q2_minimum <= q2_maximum
        assert q2_minimum % 2 == q2_maximum % 2 == q_sum % 2
        if n3_value in (0, 3, 2079, 4158):
            q_moment_ranges.append({
                "n3": n3_value,
                "sum_q": q_sum,
                "Q2_min": q2_minimum,
                "Q2_max": q2_maximum,
            })

    # Exhaust all possible total edge mass.  The construction certifies the
    # claimed minimum, while convexity/cap 12 gives the matching lower bound.
    unreachable = []
    strengthened = []
    global_combined_values = []
    construction_checks = 0
    samples = []
    for total in range(MAX_T + 1):
        records = bundle_construction(total)
        predicted = bundle_collision_minimum(total)
        if records is None:
            assert predicted is None
            unreachable.append(total)
            continue
        summary = summarize_records(records)
        assert summary["T"] == total
        assert summary["K_edge"] == predicted
        bounds = moment_bounds(summary["n3"], summary["Q2"],
                               summary["D_star"], total)
        assert bounds["lower"] <= summary["K_edge"] <= bounds["upper"]
        old_edge_floor = minimum_choose2_sum(total, EDGES)
        if predicted > old_edge_floor:
            strengthened.append({
                "T": total,
                "extra": predicted - old_edge_floor,
            })
        nonedge_floor = minimum_choose2_sum(PAIR_INCIDENCES - total, NONEDGES)
        global_combined_values.append((predicted + nonedge_floor, total))
        construction_checks += 1
        if total in (0, 1, 1386, 2079, 4158, 7623, 7624, 7625,
                     7626, 8313, 8316):
            samples.append({**summary, **bounds,
                            "K_nonedge_integer_floor": nonedge_floor,
                            "combined_collision_floor": predicted + nonedge_floor})

    assert construction_checks == 8315
    assert unreachable == [8314, 8315]
    assert len(strengthened) == 460
    assert strengthened[0] == {"T": 7624, "extra": 2}
    assert strengthened[-1] == {"T": 8312, "extra": 1}
    least_combined = min(value for value, _ in global_combined_values)
    least_combined_T = [total for value, total in global_combined_values
                        if value == least_combined]
    assert least_combined == 10395
    assert least_combined_T == list(range(1386, 2080))

    augmented = loaded[str(INPUTS[1])]
    endpoint = augmented["wave159_boundary_evaluation"]
    assert endpoint["n3"] == 4158
    assert endpoint["D_star"] == 0
    assert endpoint["Q2_forced_at_endpoint"] == 33264
    beta_edge = Fraction(endpoint["beta_e"])
    beta_nonedge = Fraction(endpoint["beta_n"])
    assert beta_edge + beta_nonedge == 45738
    endpoint_records = bundle_construction(0)
    assert endpoint_records is not None
    endpoint_summary = summarize_records(endpoint_records)
    assert endpoint_summary == {
        "n3": 4158, "Q2": 33264, "D_star": 0, "T": 0, "K_edge": 0,
    }
    h0_nonedge_collision = NONEDGES * choose2(3)
    assert h0_nonedge_collision == 12474 >= least_combined

    shadow = loaded[str(INPUTS[2])]["shadow_coefficients"]
    result = {
        "status": "EDGE_FIBRE_CODEGREE_MOMENT_DECOMPOSITION_AND_BOUNDARY_PASS",
        "inputs": inputs,
        "parameters": {"triangles": TRIANGLES, "edges": EDGES,
                       "nonedges": NONEDGES},
        "finite_role_audit": role_audit,
        "edgewise_decomposition": {
            "definitions": {
                "q(T)": "12-a3(T)",
                "p_e": "number of prism/side roots for e",
                "d_e": "number of H_delta diagonal roots whose chord is e",
                "H_e": "number of roots whose fibre contains both endpoints of e",
            },
            "identities": [
                "p_e=a3(T(e))=12-q(T(e))",
                "H_e=p_e+d_e=12-q(T(e))+d_e",
                "0<=d_e<=floor(q(T(e))/2)",
                "sum_e p_e=6P=8316-2n3",
                "sum_e d_e=D_*=n3-z11/4",
                "sum_e H_e=T=8316-2n3+D_*",
            ],
            "d_bound_proof": (
                "For e=T\\{u}, d_e is the number of entries equal to two in "
                "column (T,u) of Y.  Its column sum is q(T), so 2d_e<=q(T)."
            ),
            "local_state_count": len(states),
            "local_states": states,
            "sharp_edge_codegree_cap": 12,
        },
        "K_edge_exact_and_moment_bounds": {
            "exact": (
                "K_edge=45738-23n3+(3/2)Q2+"
                "sum_e[(12-q(T(e)))d_e+binom(d_e,2)]"
            ),
            "definitions": [
                "Q2=sum_T q(T)^2",
                "cmin(S,m)=minimum sum of binom(x_i,2) over m nonnegative integers of sum S",
                "cmax6(S,693)=maximum sum of binom(x_i,2) with 0<=x_i<=6 and sum S",
            ],
            "lower": (
                "K_edge>=45738-23n3+(3/2)Q2+cmin(D_*,693), "
                "and independently K_edge>=bundle_min(T)"
            ),
            "upper_family": [
                "K_edge<=45738-23n3+(3/2)Q2+10D_*-3cmin(D_*,693)",
                "K_edge<=cmax12(T,693)",
                "K_edge<=45738-D_*",
                "K_edge<=45738+n3-(3/2)Q2+cmax6(D_*,693)",
            ],
            "odd_q_capacity_refinement": (
                "D_*<=n3-(3/2)O_q, where O_q is the number of triangles with odd q(T)"
            ),
            "q_moment_region": {
                "sum_q": "2n3/3",
                "n3_congruence_and_range": "n3 is a multiple of 3 in [0,4158]",
                "Q2_interval": (
                    "sqmin(2n3/3,231)<=Q2<=sqmax_cap12(2n3/3,231)"
                ),
                "parity": "Q2 congruent to sum_q modulo 2, hence Q2 is even",
                "n3_values_checked": 1387,
                "samples": q_moment_ranges,
            },
        },
        "exact_three_edge_bundle_floor": {
            "formula": (
                "bundle_min(T)=cmin(T,693) for T<=7623 and T=8316; "
                "for 7624<=T<=8313 add (3-((T-7623) mod 3)) mod 3; "
                "T=8314,8315 are locally impossible"
            ),
            "reason": (
                "An edge can have H_e=12 only when q=0,d=0, hence all three "
                "edges of that triangle have H=12.  Explicit q,d constructions "
                "attain every stated value and the stated correction."
            ),
            "T_values_checked": construction_checks,
            "unreachable_T": unreachable,
            "values_strictly_stronger_than_unbundled_cmin": len(strengthened),
            "first_stronger": strengthened[0],
            "last_stronger": strengthened[-1],
        },
        "order8_shadow_connection": {
            "augmented_column": (
                "For e, Yhat has p_e prism singleton roots, q(T) good flag "
                "occurrences, and d_e doubled roots; its offdiagonal root-pair "
                "mass is 66-d_e."
            ),
            "relational_domination": [
                "K_edge_adjacent_root_pairs<=beta_e",
                "K_edge_nonadjacent_root_pairs<=beta_n",
            ],
            "beta_e_order8_nonzero_coefficients": shadow["ordered_edge"]["nonzero_order8_coefficients"],
            "beta_n_order8_nonzero_coefficients": shadow["ordered_nonedge"]["nonzero_order8_coefficients"],
            "beta_sum": "beta_e+beta_n=45738-D_*",
            "bad_mate_total": "R_e+R_n=45738+n3-(3/2)Q2",
            "scope": (
                "The domination is one-sided.  The shadow also counts singleton "
                "good roots that are not fibre roots for e, so it gives no lower "
                "bound on K_edge."
            ),
        },
        "combined_with_global_collision": {
            "old_global_bound": "K_fb=K_edge+K_nonedge>=10395",
            "bundle_plus_nonedge_integer_floor_minimum": least_combined,
            "equality_T_interval": [min(least_combined_T), max(least_combined_T)],
            "strict_improvement_of_absolute_bound": False,
            "positive_T_consequence": False,
            "strict_n3_upper_bound": False,
            "sample_relaxation_points": samples,
        },
        "exact_boundary": {
            "n3": 4158,
            "z11": 16632,
            "q(T)_all_triangles": 12,
            "Q2": 33264,
            "D_star": 0,
            "T": 0,
            "K_edge": 0,
            "H0_nonedge_collision": h0_nonedge_collision,
            "K_fb_at_H0": h0_nonedge_collision,
            "beta_e": str(beta_edge),
            "beta_n": str(beta_nonedge),
            "all_scalar_and_order8_shadow_constraints_pass": True,
            "factorization_caveat": (
                "H0 and the Wave159 order-eight point are exact relaxation "
                "controls, not a binary rooted-fibre factorization or a graph."
            ),
        },
        "conclusion": (
            "The edgewise identity gives a conceptual proof of H_e<=12 and "
            "some high-T integer refinements, but neither improves the absolute "
            "K_fb floor nor forces T>0 or n3<4158.  A stronger argument must "
            "couple the selected prism/double-root set to the order-eight shadow "
            "from below, or constrain nonedge fibre collisions."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT),
        "status": result["status"],
        "local_states": len(states),
        "unreachable_T": unreachable,
        "combined_floor": least_combined,
        "positive_T": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
