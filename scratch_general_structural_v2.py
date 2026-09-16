"""Small exact enumerations for second-order support constraints.

No graph search is performed.  The DP enumerates support multiplicities of
the 12 neighbours of one outer vertex.  Their support multigraph on seven
groups has degree sequence (2,2,4,4,4,4,4); the multiplicity of the vertex's
own support is its same-fibre degree a in {0,1,2}.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
import itertools
import json
import math


GROUP_EDGES = tuple(itertools.combinations(range(7), 2))
OWN = GROUP_EDGES.index((0, 1))


def spectral_square_upper(total_fibre_edges: int) -> float:
    """Upper bound for tr(compression^2), exact for real Ritz values."""
    wanted_sum = total_fibre_edges / 2
    best = -math.inf
    # At a vertex of the box/sum polytope at most one of 14 values is interior.
    for negatives in range(14):
        positives = 13 - negatives
        residual = wanted_sum - 3 * positives + 4 * negatives
        if -4 <= residual <= 3:
            best = max(best, 168 + 9 * positives + 16 * negatives + residual**2)
    if wanted_sum == 42:
        best = max(best, 168 + 14 * 9)
    assert best > -math.inf
    return best


def min_overlap_square(nodes, deficits):
    """Exact min sum m_ij^2 with overlap row sums 4*deficit_i."""
    pairs = [
        (i, j)
        for i, j in itertools.combinations(range(len(nodes)), 2)
        if set(GROUP_EDGES[nodes[i]]) & set(GROUP_EDGES[nodes[j]])
    ]
    demands = tuple(4 * value for value in deficits)

    @lru_cache(None)
    def visit(position, residual):
        if position == len(pairs):
            return 0 if not any(residual) else math.inf
        i, j = pairs[position]
        answer = math.inf
        for value in range(min(residual[i], residual[j]) + 1):
            next_residual = list(residual)
            next_residual[i] -= value
            next_residual[j] -= value
            answer = min(answer, value * value + visit(position + 1, tuple(next_residual)))
        return answer

    return visit(0, demands)


def relaxed_min_disjoint_deviation_square(nodes, deficits):
    """Safe lower bound on sum x_ij^2 for m_ij=4-x_ij.

    Rows outside the exceptional fibres are deliberately left unconstrained,
    so this can only underestimate the true symmetric disjoint-block cost.
    Unmet exceptional-row demand is sent on distinct edges to outside nodes.
    """
    pairs = [
        (i, j)
        for i, j in itertools.combinations(range(len(nodes)), 2)
        if not (set(GROUP_EDGES[nodes[i]]) & set(GROUP_EDGES[nodes[j]]))
    ]
    demands = tuple(2 * value for value in deficits)

    @lru_cache(None)
    def visit(position, used):
        if position == len(pairs):
            if any(used[i] > demands[i] for i in range(len(nodes))):
                return math.inf
            # Each remaining unit can use a distinct edge to a relaxed outside row.
            return sum(demands[i] - used[i] for i in range(len(nodes)))
        i, j = pairs[position]
        answer = math.inf
        limit = min(demands[i] - used[i], demands[j] - used[j])
        for value in range(limit + 1):
            next_used = list(used)
            next_used[i] += value
            next_used[j] += value
            answer = min(answer, value * value + visit(position + 1, tuple(next_used)))
        return answer

    return visit(0, (0,) * len(nodes))


def continuous_disjoint_deviation_square(nodes, deficits):
    """Real least-norm bound satisfying every disjoint-block row equation.

    For the unsigned incidence matrix H of KG(7,2), H H^T has eigenvalues
    20, 6, and 11 on dimensions 1, 6, and 14.  Dropping integrality and edge
    bounds is a safe relaxation of the actual deviations x_ij = 4-m_ij.
    """
    b = [0] * 21
    for node, deficit in zip(nodes, deficits):
        b[node] = 2 * deficit
    total = sum(b)
    group_sums = [
        sum(value for value, support in zip(b, GROUP_EDGES) if group in support)
        for group in range(7)
    ]
    norm = sum(value * value for value in b)
    weight_j = Fraction(total * total, 21)
    weight_group = Fraction(
        7 * sum(value * value for value in group_sums) - 4 * total * total,
        35,
    )
    weight_residual = Fraction(norm) - weight_j - weight_group
    assert min(weight_j, weight_group, weight_residual) >= 0
    return weight_j / 20 + weight_group / 6 + weight_residual / 11


def deficit_partitions(total, maximum=4):
    def generate(remaining, ceiling):
        if remaining == 0:
            yield ()
            return
        for first in range(min(ceiling, remaining, maximum), 0, -1):
            for tail in generate(remaining - first, first):
                yield (first,) + tail

    return list(generate(total, maximum))


def high_edge_compression_audit(max_deficit=4):
    rows = []
    for total_deficit in range(0, max_deficit + 1):
        edge_total = 84 - total_deficit
        spectral_d_square_upper = 16 * spectral_square_upper(edge_total)
        for partition in deficit_partitions(total_deficit):
            best = math.inf
            witness = None
            # Equal deficit values are indistinguishable.  Enumerating permutations
            # of a support subset is tiny for total deficit <= 4.
            for nodes in itertools.combinations(range(21), len(partition)):
                for deficits in set(itertools.permutations(partition)):
                    overlap = min_overlap_square(nodes, deficits)
                    if overlap == math.inf:
                        continue
                    disjoint_deviation = continuous_disjoint_deviation_square(nodes, deficits)
                    diagonal = 4 * (
                        (21 - len(deficits)) * 16
                        + sum((4 - value) ** 2 for value in deficits)
                    )
                    # Ordered off-diagonal entries have factor two.  The all-e=4
                    # disjoint baseline is 3360; sum x over its 105 edges is D.
                    total_d_square_lower = (
                        diagonal
                        + 2 * overlap
                        + 3360
                        - 16 * total_deficit
                        + 2 * disjoint_deviation
                    )
                    if total_d_square_lower < best:
                        best = total_d_square_lower
                        witness = {
                            "supports": [GROUP_EDGES[node] for node in nodes],
                            "deficits": deficits,
                            "overlap_square": overlap,
                            "continuous_disjoint_deviation_square": str(disjoint_deviation),
                        }
            rows.append(
                {
                    "total_deficit": total_deficit,
                    "total_fibre_edges": edge_total,
                    "deficit_partition": partition,
                    "continuous_D_square_lower": None if best == math.inf else str(best),
                    "spectral_D_square_upper": spectral_d_square_upper,
                    "excluded_even_after_relaxation": best > spectral_d_square_upper,
                    "minimizer": witness,
                }
            )
    return rows


def collision_spectrum(own_multiplicity: int):
    target = (2, 2, 4, 4, 4, 4, 4)

    @lru_cache(None)
    def visit(position: int, residual: tuple[int, ...]):
        if position == len(GROUP_EDGES):
            return frozenset((0,)) if not any(residual) else frozenset()
        u, v = GROUP_EDGES[position]
        choices = (own_multiplicity,) if position == OWN else range(min(residual[u], residual[v], 4) + 1)
        values = set()
        for multiplicity in choices:
            if multiplicity > residual[u] or multiplicity > residual[v]:
                continue
            remaining = list(residual)
            remaining[u] -= multiplicity
            remaining[v] -= multiplicity
            for tail in visit(position + 1, tuple(remaining)):
                values.add(multiplicity * (multiplicity - 1) // 2 + tail)
        return frozenset(values)

    values = sorted(visit(0, target))
    assert values
    return values


def fibre_external_collision_rows():
    # (name, e_F, internal sum_{x in F} C(deg_F(x),2))
    types = (
        ("empty", 0, 0),
        ("one_side", 1, 0),
        ("one_diagonal", 1, 0),
        ("two_opposite_sides", 2, 0),
        ("two_adjacent_sides", 2, 1),
        ("two_diagonals", 2, 0),
        ("three_sides_P4", 3, 2),
        ("four_sides_C4", 4, 4),
    )
    rows = []
    for name, edges, internal in types:
        external_incidence = 48 - 2 * edges
        external_collisions = 8 - edges - internal
        distributions = []
        # m_i is the number of the 80 outside vertices with i neighbours in F.
        for m4 in range(81):
            for m3 in range(81 - m4):
                for m2 in range(81 - m4 - m3):
                    if m2 + 3 * m3 + 6 * m4 != external_collisions:
                        continue
                    m1 = external_incidence - 2 * m2 - 3 * m3 - 4 * m4
                    m0 = 80 - m1 - m2 - m3 - m4
                    if min(m0, m1) >= 0:
                        distributions.append([m0, m1, m2, m3, m4])
        rows.append(
            {
                "type": name,
                "edges": edges,
                "internal_collisions": internal,
                "external_incidence": external_incidence,
                "external_collision_budget": external_collisions,
                "outside_degree_distribution_count": len(distributions),
                "outside_degree_distributions_m0_to_m4": distributions,
            }
        )
    return rows


def main():
    spectra = {str(a): collision_spectrum(a) for a in range(3)}
    rows = fibre_external_collision_rows()
    compression_rows = high_edge_compression_audit()
    result = {
        "one_vertex_support_multigraph": {
            "degree_sequence": [2, 2, 4, 4, 4, 4, 4],
            "collision_values_by_own_fibre_degree": spectra,
        },
        "fibre_external_common_neighbour_budgets": rows,
        "fixed_B_counts_from_spectrum": {
            "triangles": 140,
            "four_cycles": 1071,
            "trace_B3": 840,
            "trace_B4": 31752,
        },
        "fibre_compression": {
            "dimension": 21,
            "fixed_eigenvalues": {"12": 1, "-2": 6},
            "remaining_Ritz_values": 14,
            "remaining_interval": [-4, 3],
            "remaining_sum": "(C+Q)/2",
            "high_edge_audit": compression_rows,
            "largest_edge_total_not_excluded_by_relaxed_audit": max(
                row["total_fibre_edges"]
                for row in compression_rows
                if not row["excluded_even_after_relaxation"]
            ),
            "rigorously_excluded_edge_totals": sorted(
                {
                    row["total_fibre_edges"]
                    for row in compression_rows
                    if all(
                        other["excluded_even_after_relaxation"]
                        for other in compression_rows
                        if other["total_fibre_edges"] == row["total_fibre_edges"]
                    )
                }
            ),
            "rigorous_conclusion": "C+Q is not 81, 82, or 83; the audit permits both C+Q <= 80 and C+Q = 84",
            "warning": "E0=84 (deficit zero) is spectrally feasible and is excluded only by the separate computational canonical-fibre search, not by this audit",
        },
    }
    with open("scratch_general_structural_v2.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
