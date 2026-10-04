"""SOURCE ONLY: exact reference for a proposed residue objective and line trade.

No optimizer, executable controls, RNG, native state adapter or approval gate.
This discovery/reference implementation cannot independently approve itself.
"""

from collections import Counter
from itertools import combinations


class ReferenceError(ValueError):
    def __init__(self, stage, detail=""):
        self.stage = stage
        super().__init__(stage + (": " + detail if detail else ""))


def need(condition, stage, detail=""):
    if not condition:
        raise ReferenceError(stage, detail)


def integer(value):
    return type(value) is int


def pair(u, v):
    return (u, v) if u < v else (v, u)


def raw_graph(n, point_degree, ordered_triples):
    """Reconstruct every literal pair independently of any cached graph score."""
    need(integer(n) and 3 <= n <= 99, "DOMAIN_ORDER")
    need(integer(point_degree) and 0 < 2 * point_degree < n, "DOMAIN_DEGREE")
    need(type(ordered_triples) is list and 3 * len(ordered_triples) == n * point_degree,
         "DOMAIN_LINE_POPULATION")
    counts = [0] * n
    adjacency = [[0] * n for _ in range(n)]
    for row in ordered_triples:
        need(type(row) is list and len(row) == 3 and all(integer(x) for x in row),
             "DOMAIN_LINE_INTEGERS")
        need(all(0 <= x < n for x in row), "DOMAIN_VERTEX_RANGE")
        need(len(set(row)) == 3, "DOMAIN_DISTINCT_LINE_POINTS")
        for x in row:
            counts[x] += 1
        for u, v in combinations(row, 2):
            need(adjacency[u][v] == 0, "DOMAIN_LINEAR_PAIR_MULTIPLICITY")
            adjacency[u][v] = adjacency[v][u] = 1
    need(all(x == point_degree for x in counts), "DOMAIN_POINT_REGULARITY")
    return adjacency


def literal_matrix(adjacency, degree):
    n = len(adjacency)
    need(integer(degree) and type(adjacency) is list and 3 <= n <= 99,
         "MATRIX_DIMENSIONS")
    need(all(type(row) is list and len(row) == n for row in adjacency),
         "MATRIX_DIMENSIONS")
    for u in range(n):
        need(adjacency[u][u] == 0 and integer(adjacency[u][u]), "MATRIX_DIAGONAL")
        need(all(integer(x) and x in (0, 1) for x in adjacency[u]), "MATRIX_BINARY")
        need(sum(adjacency[u]) == degree, "MATRIX_REGULARITY")
        for v in range(u):
            need(adjacency[u][v] == adjacency[v][u], "MATRIX_SYMMETRY")
    return n


def common_neighbors(adjacency, u, v):
    # Deliberately direct integer scalar sum, not a native bitmask/cache import.
    return sum(adjacency[u][z] * adjacency[v][z] for z in range(len(adjacency)))


def pair_cost(common, adjacent):
    need(integer(common) and common >= 0 and integer(adjacent) and adjacent in (0, 1),
         "PAIR_COST_DOMAIN")
    residual = common + adjacent - 2
    return dict(residue=residual % 3, f3=int(residual % 3 != 0),
                e_lambda=residual * residual if adjacent else 0,
                e_mu=residual * residual if not adjacent else 0)


def scalar_weight(n, degree):
    # The target constant preserves the earlier conservative, written bound.
    return 819820 if (n, degree) == (99, 14) else n * (n - 1) // 2 * degree * degree + 1


def complete_score(adjacency, degree):
    n = literal_matrix(adjacency, degree)
    f3 = e_lambda = e_mu = 0
    residue_population = [0, 0, 0]
    for u, v in combinations(range(n), 2):
        cost = pair_cost(common_neighbors(adjacency, u, v), adjacency[u][v])
        f3 += cost["f3"]
        e_lambda += cost["e_lambda"]
        e_mu += cost["e_mu"]
        residue_population[cost["residue"]] += 1
    ordinary_energy = e_lambda + e_mu
    weight = scalar_weight(n, degree)
    return dict(f3=f3, ordinary_energy=ordinary_energy, e_lambda=e_lambda, e_mu=e_mu,
                scalar_weight=weight, scalar_score=weight * f3 + ordinary_energy,
                residue_population=residue_population)


def exclusive_swap(n, point_degree, ordered_triples, ti, tj, pi, pj):
    """Exact proposal feasibility; no acceptance decision or root freezing."""
    adjacency = raw_graph(n, point_degree, ordered_triples)
    m = len(ordered_triples)
    need(all(integer(x) for x in (ti, tj, pi, pj)), "MOVE_INDEX_INTEGERS")
    need(0 <= ti < m and 0 <= tj < m and 0 <= pi < 3 and 0 <= pj < 3,
         "MOVE_INDEX_RANGE")
    if ti == tj:
        return dict(valid=False, reason="SAME_LINE", candidate=None)
    left, right = ordered_triples[ti], ordered_triples[tj]
    x, y = left[pi], right[pj]
    if x in right or y in left:
        return dict(valid=False, reason="NONEXCLUSIVE_SELECTED_POINTS", candidate=None)
    aa = [left[i] for i in range(3) if i != pi]
    bb = [right[i] for i in range(3) if i != pj]
    removed = [pair(x, z) for z in aa] + [pair(y, z) for z in bb]
    added = [pair(y, z) for z in aa] + [pair(x, z) for z in bb]
    edge_counts = Counter({pair(u, v): 1 for u, v in combinations(range(n), 2)
                           if adjacency[u][v]})
    for edge in removed:
        edge_counts[edge] -= 1
    need(all(value >= 0 for value in edge_counts.values()), "MOVE_REMOVAL_PRESENT")
    if any(u == v or edge_counts[(u, v)] != 0 for u, v in added):
        return dict(valid=False, reason="NEW_PAIR_PRESENT_AFTER_REMOVAL", candidate=None)
    candidate = [row[:] for row in ordered_triples]
    candidate[ti][pi] = y
    candidate[tj][pj] = x
    next_adjacency = raw_graph(n, point_degree, candidate)
    signed_edges = Counter(added)
    signed_edges.subtract(removed)
    changed_edges = [[u, v, sign] for (u, v), sign in sorted(signed_edges.items()) if sign]
    changed_rows = sorted({u for u, v, sign in changed_edges} |
                          {v for u, v, sign in changed_edges})
    return dict(valid=True, reason="VALID_EXCLUSIVE_SWAP", candidate=candidate,
                removed_pairs=[list(p) for p in removed], added_pairs=[list(p) for p in added],
                net_changed_edges=changed_edges, changed_rows=changed_rows,
                adjacency=next_adjacency)


def affected_pair_delta(before, after, degree):
    """Reference affected-row calculation, to be checked against a separate scorer."""
    n = literal_matrix(before, degree)
    need(literal_matrix(after, degree) == n, "DELTA_SAME_DOMAIN")
    changed = {u for u in range(n) if before[u] != after[u]}
    pairs = [(u, v) for u, v in combinations(range(n), 2) if u in changed or v in changed]
    delta = dict(f3=0, e_lambda=0, e_mu=0)
    for u, v in pairs:
        old = pair_cost(common_neighbors(before, u, v), before[u][v])
        new = pair_cost(common_neighbors(after, u, v), after[u][v])
        for key in delta:
            delta[key] += new[key] - old[key]
    delta["ordinary_energy"] = delta["e_lambda"] + delta["e_mu"]
    delta["scalar_score"] = scalar_weight(n, degree) * delta["f3"] + delta["ordinary_energy"]
    return dict(changed_rows=sorted(changed), affected_unordered_pairs=len(pairs), delta=delta)
