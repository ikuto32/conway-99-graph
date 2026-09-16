"""Check a fixed-overlap integer Farkas certificate using full graph adjacency.

Only the Python standard library is used. No producer, optimization package,
compiled cut evaluator, or external graph builder is imported. Outer vertices
are ordered by the pair of root groups, then their two binary signs. The input
is a COMPLETE overlap assignment: absent overlapping and same-fibre edges are
fixed absent, while all 1,680 disjoint-support pairs may vary in [0, 1].
"""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


EXACT_STATUS = "EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int


def full_graph(candidate):
    labels = [(a, b) for a, b in combinations(range(14), 2) if a // 2 != b // 2]
    labels.sort(key=lambda pair: (pair[0] // 2, pair[1] // 2, pair))
    adjacency = [set() for _ in range(99)]

    def edge(u, v):
        adjacency[u].add(v)
        adjacency[v].add(u)

    for symbol in range(14):
        edge(0, symbol + 1)
    for symbol in range(0, 14, 2):
        edge(symbol + 1, symbol + 2)
    for vertex, label in enumerate(labels, 15):
        for symbol in label:
            edge(vertex, symbol + 1)
    pairs = candidate["overlap_edges_outer_zero_based"]
    require(type(pairs) is list and len(pairs) == 168, "Expected 168 overlap edges")
    seen = set()
    for pair in pairs:
        require(type(pair) is list and len(pair) == 2 and all(map(integer, pair)), "Invalid overlap edge")
        u, v = pair
        require(0 <= u < v < 84 and (u, v) not in seen, "Repeated or invalid overlap edge")
        seen.add((u, v))
        shared = {symbol // 2 for symbol in labels[u]} & {symbol // 2 for symbol in labels[v]}
        require(len(shared) == 1, "Edge is not between overlapping distinct supports")
        edge(u + 15, v + 15)
    require(Counter(map(len, adjacency)) == {14: 15, 6: 84}, "Incorrect partial degrees")
    for u, v in combinations(range(99), 2):
        require(len(adjacency[u] & adjacency[v]) <= (1 if v in adjacency[u] else 2),
                f"Partial common-neighbor cap failed at {u}, {v}")
    unknown = {
        (u + 15, v + 15) for u, v in combinations(range(84), 2)
        if not ({symbol // 2 for symbol in labels[u]} & {symbol // 2 for symbol in labels[v]})
    }
    require(len(unknown) == 1680, "Incorrect unknown edge domain")
    return adjacency, unknown


def graph_constraint(adjacency, unknown, kind, coordinate):
    """Derive one necessary equality/inequality from the actual 99-vertex graph.

    A root neighbor has its degree 14 already fixed. Its common-neighbor count
    with an outer vertex therefore gives an exact linear equality. For a pair
    of outer vertices, retain the known-known and known-unknown contributions,
    move its potential adjacency variable to the left, and discard the
    nonnegative unknown-unknown common-neighbor products. This gives a valid
    upper bound, with nonnegative multipliers only.
    """
    require(type(coordinate) is list and len(coordinate) == 2 and all(map(integer, coordinate)),
            "Invalid constraint coordinate")
    terms = Counter()
    if kind == "label_quota":
        outer, symbol = coordinate
        require(0 <= outer < 84 and 0 <= symbol < 14, "Invalid quota coordinate")
        u, v = outer + 15, symbol + 1
        rhs = (1 if v in adjacency[u] else 2) - len(adjacency[u] & adjacency[v])
        for w in adjacency[v]:
            pair = tuple(sorted((u, w)))
            if pair in unknown:
                terms[pair] += 1
    else:
        require(kind == "linear_pair_cap", "Unknown constraint kind")
        a, b = coordinate
        require(0 <= a < b < 84, "Invalid pair coordinate")
        u, v = a + 15, b + 15
        rhs = 2 - int(v in adjacency[u]) - len(adjacency[u] & adjacency[v])
        if (u, v) in unknown:
            terms[u, v] += 1
        for fixed, changing in ((u, v), (v, u)):
            for w in adjacency[fixed]:
                pair = tuple(sorted((changing, w)))
                if pair in unknown:
                    terms[pair] += 1
    require(rhs >= 0, "Input already violates a fixed pair cap")
    return terms, rhs


def audit(candidate_path, certificate_path):
    candidate_bytes = candidate_path.read_bytes()
    certificate_bytes = certificate_path.read_bytes()
    candidate, certificate = json.loads(candidate_bytes), json.loads(certificate_bytes)
    digest = sha256(candidate_bytes).hexdigest()
    require(certificate.get("candidate_sha256") == digest, "Candidate SHA256 does not match certificate")
    require(certificate.get("disjoint_block_totals_assumed", False) is False,
            "This checker certifies no disjoint compression totals")
    adjacency, unknown = full_graph(candidate)
    result = {
        "inputs_sha256": {str(candidate_path): digest, str(certificate_path): sha256(certificate_bytes).hexdigest()},
        "auditor_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "exposed_graph_edges": sum(map(len, adjacency)) // 2,
        "partial_pair_caps_checked": 4851,
        "disjoint_unknowns": len(unknown),
        "solver_or_producer_imported": False,
        "disjoint_block_totals_assumed": False,
    }
    if certificate.get("status") != EXACT_STATUS:
        result.update(status="NO_EXACT_CERTIFICATE_TO_AUDIT", producer_status=certificate.get("status"),
                      scope="Partial graph checked only; numerical solver status supplies no exact exclusion or completion witness.")
        return result
    coefficients = dict.fromkeys(unknown, 0)
    combined_rhs = 0
    group_counts = Counter()
    seen = set()
    for record in certificate["group_multipliers"]:
        kind, coordinate, multiplier = record["kind"], record["coordinate"], record["multiplier"]
        require(integer(multiplier) and multiplier != 0, "Expected nonzero integer multiplier")
        require(kind == "label_quota" or multiplier > 0, "Pair-cap multiplier must be positive")
        terms, rhs = graph_constraint(adjacency, unknown, kind, coordinate)
        key = kind, tuple(coordinate)
        require(key not in seen, "Duplicate constraint multiplier")
        seen.add(key)
        combined_rhs += multiplier * rhs
        for pair, multiplicity in terms.items():
            coefficients[pair] += multiplier * multiplicity
        group_counts[kind] += 1
    upper_seen = set()
    for record in certificate["edge_upper_bound_multipliers"]:
        pair, multiplier = record["edge"], record["multiplier"]
        require(type(pair) is list and len(pair) == 2 and all(map(integer, pair)), "Invalid upper-bound edge")
        require(integer(multiplier) and multiplier > 0, "Upper-bound multiplier must be a positive integer")
        global_pair = tuple(value + 15 for value in pair)
        require(global_pair in unknown and global_pair not in upper_seen, "Unknown or duplicate upper-bound edge")
        upper_seen.add(global_pair)
        coefficients[global_pair] += multiplier
        combined_rhs += multiplier
    require(all(value >= 0 for value in coefficients.values()), "Combined left side has a negative coefficient")
    require(combined_rhs < 0, "Combined right side is not negative")
    require(integer(certificate["combined_rhs"]) and certificate["combined_rhs"] == combined_rhs,
            "Recorded combined RHS differs from independently derived RHS")
    result.update(
        status="INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS", group_counts=dict(group_counts),
        upper_bound_count=len(upper_seen), positive_coefficients=sum(value > 0 for value in coefficients.values()),
        minimum_coefficient=min(coefficients.values()), maximum_coefficient=max(coefficients.values()),
        combined_rhs=combined_rhs,
        scope="Exact contradiction for the necessary linear [0,1] disjoint-edge completion system of this complete overlap assignment, with same-fibre edges absent. No global E0 or Conway exclusion.",
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Output already exists; use a fresh output path")
    result = audit(args.candidate, args.certificate)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
