"""Independent graph-classification audit of the E0=75 Gram obstruction.

Unlike ``scratch_theory_e75_gram_audit.py``, this file does not solve the
Gram diagonal linear systems and imports no project module.  It enumerates
the relevant unweighted support subgraphs of K7, classifies their unsigned
circulation spaces, and applies the elementary norm equalities proved for
the six possible graph types.
"""

from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_e75_gram_independent_audit.json")
EDGES = tuple(itertools.combinations(range(7), 2))


def rank(matrix):
    a = [[Fraction(value) for value in row] for row in matrix]
    if not a:
        return 0
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        scale = a[row][col]
        a[row] = [value / scale for value in a[row]]
        for i in range(len(a)):
            if i == row or not a[i][col]:
                continue
            scale = a[i][col]
            a[i] = [x - scale * y for x, y in zip(a[i], a[row])]
        row += 1
    return row


def graph_data(chosen):
    edges = [EDGES[index] for index in chosen]
    adjacency = [set() for _ in range(7)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    vertices = [u for u in range(7) if adjacency[u]]
    degrees = tuple(sorted((len(adjacency[u]) for u in vertices), reverse=True))
    colors = {}
    bipartite = True
    components = 0
    for seed in vertices:
        if seed in colors:
            continue
        components += 1
        colors[seed] = 0
        queue = deque([seed])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if v not in colors:
                    colors[v] = 1 - colors[u]
                    queue.append(v)
                elif colors[v] == colors[u]:
                    bipartite = False
    incidence = [[int(group in edge) for edge in edges] for group in range(7)]
    kernel_dimension = len(edges) - rank(incidence)
    # An edge is active in some kernel vector iff deleting its column does not
    # reduce the kernel dimension.
    active = []
    for deleted in range(len(edges)):
        reduced = [row[:deleted] + row[deleted + 1 :] for row in incidence]
        reduced_nullity = len(edges) - 1 - rank(reduced)
        active.append(reduced_nullity < kernel_dimension)
    return {
        "vertices": len(vertices),
        "degrees": degrees,
        "components": components,
        "bipartite": bipartite,
        "kernel_dimension": kernel_dimension,
        "all_edges_active": all(active),
    }


def type_name(m, data):
    key = (
        m,
        data["vertices"],
        data["degrees"],
        data["components"],
        data["bipartite"],
        data["kernel_dimension"],
        data["all_edges_active"],
    )
    names = {
        (4, 4, (2, 2, 2, 2), 1, True, 1, True): "C4",
        (5, 5, (2, 2, 2, 2, 2), 1, False, 0, False): "C5",
        (5, 4, (3, 3, 2, 2), 1, False, 1, False): "K4-e",
        (6, 6, (2, 2, 2, 2, 2, 2), 1, True, 1, True): "C6",
        (6, 6, (2, 2, 2, 2, 2, 2), 2, False, 0, False): "C3+C3",
        (6, 5, (4, 2, 2, 2, 2), 1, False, 1, True): "bowtie",
        (6, 5, (3, 3, 2, 2, 2), 1, False, 1, False): "C5+chord",
        (6, 5, (3, 3, 2, 2, 2), 1, True, 2, True): "K2,3",
        (6, 4, (3, 3, 3, 3), 1, False, 2, True): "K4",
    }
    assert key in names, key
    return names[key]


def weight_assignments(pattern):
    return sorted(set(itertools.permutations(pattern)))


def compatible_by_elementary_norm_rules(name, chosen, assignment):
    edge_values = {EDGES[index]: value for index, value in zip(chosen, assignment)}
    if name in {"C5", "K4-e", "C3+C3", "C5+chord"}:
        return False
    if name in {"C4", "C6", "bowtie"}:
        return len(set(assignment)) == 1
    if name == "K4":
        vertices = sorted(set(itertools.chain.from_iterable(edge_values)))
        return all(
            edge_values[tuple(sorted((a, b)))] == edge_values[tuple(sorted((c, d)))]
            for a, b, c, d in (
                (vertices[0], vertices[1], vertices[2], vertices[3]),
                (vertices[0], vertices[2], vertices[1], vertices[3]),
                (vertices[0], vertices[3], vertices[1], vertices[2]),
            )
        )
    if name == "K2,3":
        adjacency = {u: set() for edge in edge_values for u in edge}
        for u, v in edge_values:
            adjacency[u].add(v)
            adjacency[v].add(u)
        degree_two = [u for u, neighbours in adjacency.items() if len(neighbours) == 2]
        return all(
            edge_values[tuple(sorted((u, a)))] == edge_values[tuple(sorted((u, b)))]
            for u in degree_two
            for a, b in [tuple(adjacency[u])]
        )
    raise AssertionError(name)


def audit(pattern):
    graph_counts = Counter()
    weighted_tested = 0
    compatible = 0
    assignments = weight_assignments(pattern)
    for chosen in itertools.combinations(range(21), len(pattern)):
        data = graph_data(chosen)
        if 1 in data["degrees"]:
            continue
        name = type_name(len(pattern), data)
        graph_counts[name] += 1
        for assignment in assignments:
            weighted_tested += 1
            compatible += compatible_by_elementary_norm_rules(name, chosen, assignment)
    assert compatible == 0
    return {
        "deficit_multiset": list(pattern),
        "support_graph_type_counts_after_degree_one_filter": dict(sorted(graph_counts.items())),
        "distinct_weight_assignments_per_graph": len(assignments),
        "weighted_cases_checked": weighted_tested,
        "compatible_cases": compatible,
    }


def main():
    patterns = (
        (3, 2, 2, 2),
        (2, 2, 2, 2, 1),
        (2, 2, 2, 1, 1, 1),
    )
    rows = [audit(pattern) for pattern in patterns]
    result = {
        "status": "INDEPENDENT_GRAPH_CLASSIFICATION_VERIFIED",
        "imports_project_code": False,
        "rows": rows,
        "total_weighted_cases_after_degree_one_filter": sum(
            row["weighted_cases_checked"] for row in rows
        ),
        "total_compatible_cases": sum(row["compatible_cases"] for row in rows),
        "conclusion": "All Q>=6-capable deficit-9 support patterns violate vector circulation.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
