"""Pure integer full-adjacency validation and small known-SRG controls.

This producer-side validation path is not independent review of a discovery.
"""
from itertools import combinations


def validate(adjacency, n, degree, lam, mu):
    errors = []
    if type(adjacency) is not list or len(adjacency) != n or any(type(row) is not list or len(row) != n for row in adjacency):
        return {"valid": False, "reason": "shape", "vertices_checked": 0, "pairs_checked": 0}
    if any(type(x) is not int or x not in (0, 1) for row in adjacency for x in row):
        return {"valid": False, "reason": "nonbinary", "vertices_checked": 0, "pairs_checked": 0}
    for u in range(n):
        if adjacency[u][u] != 0:
            errors.append(["diagonal", u])
        if sum(adjacency[u]) != degree:
            errors.append(["degree", u, sum(adjacency[u])])
    for u, v in combinations(range(n), 2):
        if adjacency[u][v] != adjacency[v][u]:
            errors.append(["asymmetry", u, v])
        common = sum(adjacency[u][w] * adjacency[v][w] for w in range(n))
        target = lam if adjacency[u][v] else mu
        if common != target:
            errors.append(["common", u, v, common, target])
    return {"valid": not errors, "parameters": [n, degree, lam, mu], "vertices_checked": n,
            "pairs_checked": n * (n - 1) // 2, "error_count": len(errors), "first_errors": errors[:12],
            "arithmetic": "Python exact integers", "independent_review": False}


def controls():
    fixtures = []
    specifications = [
        ("pentagon", [5, 2, 0, 1], lambda u, v: (u - v) % 5 in (1, 4)),
        ("rook3", [9, 4, 1, 2], lambda u, v: u // 3 == v // 3 or u % 3 == v % 3),
        ("clebsch", [16, 5, 0, 2], lambda u, v: (u ^ v).bit_count() in (1, 4)),
    ]
    pairs = list(combinations(range(5), 2))
    specifications += [("petersen", [10, 3, 0, 1], lambda u, v: not set(pairs[u]) & set(pairs[v])),
                       ("triangular5", [10, 6, 3, 4], lambda u, v: bool(set(pairs[u]) & set(pairs[v])))]
    for name, parameters, edge in specifications:
        n = parameters[0]
        adjacency = [[int(u != v and edge(u, v)) for v in range(n)] for u in range(n)]
        positive = validate(adjacency, *parameters)
        assert positive["valid"]
        corrupted = []
        for kind in ("loop", "edge_flip", "asymmetry", "nonbinary"):
            bad = [row.copy() for row in adjacency]
            if kind == "loop":
                bad[0][0] = 1
            elif kind == "edge_flip":
                bad[0][1] = bad[1][0] = 1 - bad[0][1]
            elif kind == "asymmetry":
                bad[0][1] = 1 - bad[0][1]
            else:
                bad[0][1] = 2
            checked = validate(bad, *parameters)
            assert not checked["valid"]
            corrupted.append({"kind": kind, "adjacency": bad, "result": checked})
        fixtures.append({"name": name, "parameters": parameters, "adjacency": adjacency,
                         "positive": positive, "corrupted": corrupted})
    return {"status": "PRODUCER_FULL_SRG_CONTROLS_PASS", "fixtures": fixtures,
            "known_valid_99_target_fixture_available": False,
            "known_valid_99_target_fixture_null_reason": "No verified target graph is available; calibration uses five known SRGs with their own parameters.",
            "independent_review": False}
