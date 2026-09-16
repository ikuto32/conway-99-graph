"""Independent replay audit for the fixed-control E0=0 T-fit witness.

The input fit JSON contains a bounded CP-SAT witness, but no optimality proof.
This script does not import the search implementation.  It reconstructs the
84 signed points, D, T, B, Q and the full residual matrix directly, then
checks the structural constraints and records exact trace/commutator bounds.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTROL = ROOT / "scratch_theory_e0_zero_hypergraph_point_control.json"
FIT = ROOT / "scratch_theory_e0_zero_hypergraph_t_fit.json"
OUTPUT_JSON = ROOT / "scratch_theory_e0_zero_hypergraph_t_fit_audit.json"
OUTPUT_MD = ROOT / "scratch_theory_e0_zero_hypergraph_t_fit_audit.md"
EXPECTED_CONTROL_SHA256 = "C669C983B65BDBF8F5445B99D3847DDEF8FC91DEAB990343ECE53AFD214F1CA2"
EXPECTED_FIT_SHA256 = "BA120E4BE7645AE9113766F94F8D10CED79A1500BFDA04F983542B1605CC6263"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


SUPPORTS = tuple(itertools.combinations(range(7), 2))
POINTS = tuple(
    (g, h, a, b)
    for g, h in SUPPORTS
    for a, b in itertools.product((0, 1), repeat=2)
)
POINT_INDEX = {point: index for index, point in enumerate(POINTS)}
FLIPS = ((1, 0), (0, 1), (1, 1))


def support(point: tuple[int, int, int, int]) -> tuple[int, int]:
    return point[:2]


def symbols(point: tuple[int, int, int, int]) -> frozenset[tuple[int, int]]:
    g, h, a, b = point
    return frozenset(((g, a), (h, b)))


def q_value(left: int, right: int) -> int:
    if left == right:
        return 0
    return len(symbols(POINTS[left]) & symbols(POINTS[right]))


def flip(point: tuple[int, int, int, int], delta: tuple[int, int]) -> tuple[int, int, int, int]:
    g, h, a, b = point
    return (g, h, a ^ delta[0], b ^ delta[1])


def edge_set_from_blocks(blocks: tuple[tuple[int, int, int], ...]) -> set[tuple[int, int]]:
    return {
        tuple(sorted(pair))
        for block in blocks
        for pair in itertools.combinations(block, 2)
    }


def adjacency(edges: set[tuple[int, int]]) -> list[set[int]]:
    rows = [set() for _ in POINTS]
    for left, right in edges:
        rows[left].add(right)
        rows[right].add(left)
    return rows


def triangle_list(edges: set[tuple[int, int]]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        triple
        for triple in itertools.combinations(range(len(POINTS)), 3)
        if all(tuple(sorted(pair)) in edges for pair in itertools.combinations(triple, 2))
    )


def relation_name(left: int, right: int, d_edges: set[tuple[int, int]], t_edges: set[tuple[int, int]]) -> str:
    pair = (left, right)
    if pair in d_edges:
        return "D_edge"
    if pair in t_edges:
        return "T_edge"
    if support(POINTS[left]) == support(POINTS[right]):
        return "same_fibre_nonedge_Q" + str(q_value(left, right))
    return "other_nonedge_Q" + str(q_value(left, right))


def audit() -> dict[str, object]:
    require(sha256(CONTROL) == EXPECTED_CONTROL_SHA256, "control hash drift")
    require(sha256(FIT) == EXPECTED_FIT_SHA256, "fit witness hash drift")
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    fit = json.loads(FIT.read_text(encoding="utf-8"))
    require(control["status"] == "SIGNED_POINT_CONTROL_FOUND", "control status")
    require(fit["status"] == "FIXED_D_T_FIT_FEASIBLE", "fit status")

    blocks = tuple(
        tuple(sorted(POINT_INDEX[tuple(point)] for point in block))
        for block in control["selected_signed_blocks"]
    )
    require(len(blocks) == len(set(blocks)) == 140, "140 distinct D blocks")
    d_edges = edge_set_from_blocks(blocks)
    require(len(d_edges) == 420, "linear D edge set")
    d_adj = adjacency(d_edges)
    require({len(row) for row in d_adj} == {10}, "D degree 10")
    require(all(q_value(*edge) == 0 for edge in d_edges), "D exact-symbol disjointness")

    # U is reconstructed, rather than trusted from the control JSON: it is the
    # selected D relation with one common support label and opposite signs.
    u_edges = {
        edge
        for edge in d_edges
        if len(set(support(POINTS[edge[0]])) & set(support(POINTS[edge[1]]))) == 1
    }
    u_adj = adjacency(u_edges)
    require(len(u_edges) == 84 and {len(row) for row in u_adj} == {2}, "U 2-factor")

    t_edges = {tuple(sorted(edge)) for edge in map(tuple, fit["selected_T_edges"])}
    require(len(t_edges) == 84, "T edge count")
    require(not (d_edges & t_edges), "T/D edge disjointness")
    require(
        all(
            q_value(*edge) == 1
            and support(POINTS[edge[0]]) != support(POINTS[edge[1]])
            for edge in t_edges
        ),
        "T relation",
    )
    t_adj = adjacency(t_edges)
    require({len(row) for row in t_adj} == {2}, "T degree 2")

    label_rows: dict[tuple[int, int], Counter[int]] = defaultdict(Counter)
    for left, right in t_edges:
        shared = symbols(POINTS[left]) & symbols(POINTS[right])
        require(len(shared) == 1, "unique T label")
        label = next(iter(shared))
        label_rows[label][left] += 1
        label_rows[label][right] += 1
    require(len(label_rows) == 14, "14 exact-label matchings")
    for label in itertools.product(range(7), (0, 1)):
        expected_points = {index for index, point in enumerate(POINTS) if label in symbols(point)}
        require(len(expected_points) == 12, "label fibre size")
        require(label_rows[label] == Counter({point: 1 for point in expected_points}), "label 1-factor")

    t_triangles = triangle_list(t_edges)
    require(not t_triangles, "T triangle-free")
    b_edges = d_edges | t_edges
    b_adj = adjacency(b_edges)
    require(len(b_edges) == 504 and {len(row) for row in b_adj} == {12}, "B is 12-regular")

    residual = [[0] * 84 for _ in range(84)]
    relation_values: dict[str, list[int]] = defaultdict(list)
    values = []
    for left, right in itertools.combinations(range(84), 2):
        value = (
            len(b_adj[left] & b_adj[right])
            + int((left, right) in b_edges)
            - (2 - q_value(left, right))
        )
        residual[left][right] = residual[right][left] = value
        values.append(value)
        relation_values[relation_name(left, right, d_edges, t_edges)].append(value)
    require([sum(row) for row in residual] == [0] * 84, "residual row sums")
    residual_l1 = sum(abs(value) for value in values)
    residual_f2 = sum(value * value for row in residual for value in row)
    require(residual_l1 == round(fit["solver"]["objective"]) == 2646, "objective replay")

    # Fixed-D coordinatewise baseline.  Adding T only adds adjacency/common-
    # neighbour terms, so every final residual entry is at least this entry.
    baseline = []
    for left, right in itertools.combinations(range(84), 2):
        baseline.append(
            len(d_adj[left] & d_adj[right])
            + int((left, right) in d_edges)
            - (2 - q_value(left, right))
        )
    positive_baseline_mass = sum(max(value, 0) for value in baseline)
    require(sum(baseline) == -1848 and positive_baseline_mass == 774, "baseline census")
    require(all(final >= initial for final, initial in zip(values, baseline)), "T monotonicity")
    # A 12-regular B has zero total off-diagonal residual.  Hence positive and
    # negative residual masses agree, giving the rigorous fixed-D L1 floor.
    require(sum(values) == 0, "final residual total")
    fixed_d_l1_floor = 2 * positive_baseline_mass
    require(residual_l1 >= fixed_d_l1_floor == 1548, "fixed-D L1 floor")

    d_triangles = triangle_list(d_edges)
    selected_block_triangles = set(blocks)
    require(selected_block_triangles <= set(d_triangles), "block triangles in D")
    outside_berge = set(d_triangles) - selected_block_triangles
    require(len(d_triangles) == 227 and len(outside_berge) == 87, "D triangle census")
    d_edge_surplus = sum(len(d_adj[left] & d_adj[right]) - 1 for left, right in d_edges)
    require(d_edge_surplus == 3 * len(outside_berge) == 261, "Berge surplus")

    b_triangles = triangle_list(b_edges)
    triangle_histogram = Counter(
        sum(tuple(sorted(pair)) in t_edges for pair in itertools.combinations(triangle, 2))
        for triangle in b_triangles
    )
    require(triangle_histogram.get(3, 0) == 0, "no T triangle in B")
    trace_be = 2 * sum(residual[left][right] for left, right in b_edges)
    require(trace_be == 6 * (len(b_triangles) - 140), "trace identity")
    require(trace_be >= 6 * len(outside_berge), "fixed-D trace floor")
    trace_bound = Fraction(trace_be * trace_be, 1008)
    berge_trace_bound = Fraction(len(outside_berge) ** 2, 28)

    q_adj = [
        {right for right in range(84) if right != left and q_value(left, right) == 1}
        for left in range(84)
    ]
    require({len(row) for row in q_adj} == {22}, "Q degree 22")
    commutator_f2 = 0
    residual_commutator_f2 = 0
    for left in range(84):
        for right in range(84):
            bq = sum(right in q_adj[middle] for middle in b_adj[left])
            qb = sum(right in b_adj[middle] for middle in q_adj[left])
            commutator = bq - qb
            be = sum(residual[middle][right] for middle in b_adj[left])
            eb = sum(residual[left][middle] for middle in b_adj[right])
            residual_commutator = be - eb
            require(commutator == residual_commutator, "[B,Q]=[B,E]")
            commutator_f2 += commutator * commutator
            residual_commutator_f2 += residual_commutator * residual_commutator
    require(commutator_f2 == residual_commutator_f2, "commutator norms")
    commutator_bound = Fraction(commutator_f2, 576)

    matching_traces = {}
    for delta in FLIPS:
        pairs = {
            tuple(sorted((index, POINT_INDEX[flip(point, delta)])))
            for index, point in enumerate(POINTS)
        }
        require(len(pairs) == 42, "matching pair count")
        matching_traces[str(delta)] = 2 * sum(residual[left][right] for left, right in pairs)

    candidate_t_edges = {
        pair
        for pair in itertools.combinations(range(84), 2)
        if q_value(*pair) == 1 and support(POINTS[pair[0]]) != support(POINTS[pair[1]])
    }
    candidate_t_triangles = sum(
        all(tuple(sorted(pair)) in candidate_t_edges for pair in itertools.combinations(triple, 2))
        for triple in itertools.combinations(range(84), 3)
    )
    require((len(candidate_t_edges), candidate_t_triangles) == (840, 2520), "search domain census")

    result = {
        "status": "FIXED_CONTROL_T_FIT_AUDIT_PASS",
        "sealed_inputs": {
            "point_control_sha256": sha256(CONTROL),
            "fit_witness_sha256": sha256(FIT),
        },
        "search_claim": {
            "solver_status": fit["solver"]["status"],
            "objective": fit["solver"]["objective"],
            "best_bound": fit["solver"]["best_bound"],
            "wall_seconds": fit["solver"]["wall_seconds"],
            "optimality_proved": fit["solver"]["status"] == "OPTIMAL",
            "boundary": "one fixed D/U control; bounded optimization; no universal exclusion",
        },
        "independent_domain_census": {
            "signed_points": len(POINTS),
            "D_blocks": len(blocks),
            "D_edges": len(d_edges),
            "U_edges": len(u_edges),
            "T_candidate_edges": len(candidate_t_edges),
            "T_candidate_triangles_forbidden": candidate_t_triangles,
            "exact_label_matching_rows": 14 * 12,
        },
        "witness": {
            "T_edges": len(t_edges),
            "T_degree": 2,
            "T_triangles": len(t_triangles),
            "B_edges": len(b_edges),
            "B_degree": 12,
            "B_triangles": len(b_triangles),
            "B_triangle_histogram_by_T_edges": {
                str(key): value for key, value in sorted(triangle_histogram.items())
            },
        },
        "entrywise_residual": {
            "definition": "E=B^2+B-(10I+2J-Q)",
            "unordered_entries": len(values),
            "bad_entries": sum(value != 0 for value in values),
            "L1_unordered": residual_l1,
            "Frobenius_square": residual_f2,
            "maximum_absolute": max(map(abs, values)),
            "signed_histogram": {str(key): value for key, value in sorted(Counter(values).items())},
            "row_sums": {"0": 84},
            "by_relation": {
                name: {
                    "entries": len(row),
                    "bad": sum(value != 0 for value in row),
                    "L1": sum(abs(value) for value in row),
                    "signed_histogram": {
                        str(key): count for key, count in sorted(Counter(row).items())
                    },
                }
                for name, row in sorted(relation_values.items())
            },
        },
        "fixed_control_obstructions": {
            "D_triangles": len(d_triangles),
            "selected_block_triangles": len(selected_block_triangles),
            "outside_Berge_triangles": len(outside_berge),
            "D_edge_noncancellable_surplus": d_edge_surplus,
            "D_edge_relation_statement": (
                "every D edge already has its selected block as the one allowed common neighbour; "
                "the 87 outside Berge triangles therefore contribute 3*87 positive residual units "
                "which adding T cannot cancel"
            ),
            "trace_B_times_E_floor": 6 * len(outside_berge),
            "T_zero_baseline": {
                "sum": sum(baseline),
                "positive_mass": positive_baseline_mass,
                "signed_histogram": {
                    str(key): value for key, value in sorted(Counter(baseline).items())
                },
            },
            "rigorous_unordered_L1_floor_for_this_D": fixed_d_l1_floor,
            "control_dependent": True,
        },
        "exact_identities_and_bounds": {
            "trace_identity": "tr(BE)=tr(B^3)-840=6*(triangles(B)-140)",
            "triangle_excess_decomposition": {
                "formula": (
                    "triangles(B)-140 = beta(D) + mixed_1T + mixed_2T + triangles(T)"
                ),
                "beta_D_outside_Berge": len(outside_berge),
                "mixed_1T": triangle_histogram.get(1, 0),
                "mixed_2T": triangle_histogram.get(2, 0),
                "triangles_T": triangle_histogram.get(3, 0),
                "sum": len(b_triangles) - 140,
            },
            "trace_B_times_E": trace_be,
            "trace_Cauchy_bound_on_Frobenius_square": {
                "formula": "||E||_F^2 >= tr(BE)^2/1008",
                "exact": f"{trace_bound.numerator}/{trace_bound.denominator}",
                "decimal": float(trace_bound),
            },
            "general_Berge_triangle_bound": {
                "formula": "||E||_F^2 >= beta(D)^2/28",
                "derivation": "tr(BE)>=6*beta(D) and tr(B^2)=1008",
                "value_for_fixed_D_exact": f"{berge_trace_bound.numerator}/{berge_trace_bound.denominator}",
                "necessary_when_E_is_zero": "beta(D)=0 and all mixed/T triangle counts are zero",
            },
            "commutator_identity": "[B,Q]=[B,E]",
            "Q_commutator_Frobenius_square": commutator_f2,
            "commutator_bound_on_Frobenius_square": {
                "formula": "||E||_F^2 >= ||[B,Q]||_F^2/576",
                "exact": f"{commutator_bound.numerator}/{commutator_bound.denominator}",
                "decimal": float(commutator_bound),
            },
            "matching_trace_residuals": matching_traces,
            "generality": (
                "the triangle decomposition, beta(D)^2/28 bound, trace identity and commutator inequality "
                "hold for every admissible 12-regular B=T+D; beta=87 and the other positive numerical "
                "diagnostics here use this fixed D and/or this fitted T"
            ),
        },
        "conclusion": (
            "The fixed control cannot satisfy the exact matrix equation for any T, already because its "
            "87 outside Berge triangles force tr(BE)>=522 (and its monotone baseline gives L1>=1548). "
            "Universally, exactness requires beta(D)=0 and forbids all mixed/T triangles; the observed "
            "beta=87 rejects only the explicit control, not the E0=0 layer in general."
        ),
    }
    return result


def markdown(result: dict[str, object]) -> str:
    search = result["search_claim"]
    residual = result["entrywise_residual"]
    fixed = result["fixed_control_obstructions"]
    exact = result["exact_identities_and_bounds"]
    witness = result["witness"]
    return f"""# E0=0 fixed-control T-fit independent audit

Status: `{result['status']}`.

The sealed CP-SAT run supplied a **feasible**, not certified optimal, T: objective
`{search['objective']}`, solver lower bound `{search['best_bound']}`.  Independently replayed,
T has {witness['T_edges']} edges, degree {witness['T_degree']}, no triangle, and is the union
of the 14 required exact-label 1-factors.  B=T+D has {witness['B_edges']} edges and degree
{witness['B_degree']}.

## Direct residual

For `E=B^2+B-(10I+2J-Q)`, the witness has unordered L1
`{residual['L1_unordered']}`, `{residual['bad_entries']}` bad unordered entries, and
`||E||_F^2={residual['Frobenius_square']}`.  B has {witness['B_triangles']} triangles,
split by the number of T sides as `{witness['B_triangle_histogram_by_T_edges']}`.

## First unavoidable failure for this fixed D

D already has {fixed['D_triangles']} triangles: 140 selected-block triangles and
{fixed['outside_Berge_triangles']} outside Berge triangles.  Adding T cannot delete them.
Consequently

`tr(BE)=tr(B^3)-840=6*(triangles(B)-140) >= {fixed['trace_B_times_E_floor']}`.

The stronger coordinatewise fixed-D check starts at T=0 with positive residual mass
{fixed['T_zero_baseline']['positive_mass']}.  Every T contribution is nonnegative, while
every final 12-regular residual has total sum zero, so any T over this D obeys the rigorous
unordered L1 lower bound `{fixed['rigorous_unordered_L1_floor_for_this_D']}`.

More generally, writing `beta(D)` for the number of D-triangles outside the 140
selected blocks,

`triangles(B)-140 = beta(D) + mixed_1T + mixed_2T + triangles(T)`.

All four terms are nonnegative.  Thus every exact E0=0 candidate must have `beta(D)=0`
and no mixed or T triangle.  Cauchy--Schwarz also gives the general quantitative bound
`||E||_F^2 >= beta(D)^2/28`.  The rule is general; the value `beta(D)=87` is specific
to this control.

The replay also checks `[B,Q]=[B,E]`.  Cauchy--Schwarz gives
`||E||_F^2 >= {exact['trace_Cauchy_bound_on_Frobenius_square']['exact']}` for this witness;
the commutator gives `||E||_F^2 >= {exact['commutator_bound_on_Frobenius_square']['exact']}`.

## Boundary

This is a rigorous rejection of **one explicit D/U control only**.  The bounded CP-SAT
objective is not proved optimal, and none of the positive numerical bounds excludes all
E0=0 controls.  The trace and commutator formulas themselves are general necessary
identities for an admissible 12-regular B=T+D.
"""


def main() -> None:
    result = audit()
    atomic_write(OUTPUT_JSON, json.dumps(result, indent=2, sort_keys=True) + "\n")
    atomic_write(OUTPUT_MD, markdown(result))
    print(json.dumps({
        "status": result["status"],
        "objective": result["entrywise_residual"]["L1_unordered"],
        "fixed_D_L1_floor": result["fixed_control_obstructions"]["rigorous_unordered_L1_floor_for_this_D"],
        "trace_B_times_E": result["exact_identities_and_bounds"]["trace_B_times_E"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
