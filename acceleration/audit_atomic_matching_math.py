"""Check matching coordinates and abstract cycle counts without generator imports."""
import argparse
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations, permutations
import json
from math import comb, factorial
from pathlib import Path

from audit_certificate import full_graph, require


def all_matchings(vertices):
    if not vertices:
        yield ()
        return
    u = vertices[0]
    for i in range(1, len(vertices)):
        v = vertices[i]
        for tail in all_matchings(vertices[1:i] + vertices[i+1:]):
            yield tuple(sorted(((u, v),) + tail))


def connected_union(old, new):
    if set(old) & set(new):
        return False
    neighbors = {u: set() for edge in old for u in edge}
    for u, v in old + new:
        neighbors[u].add(v)
        neighbors[v].add(u)
    require(all(len(row) == 2 for row in neighbors.values()), "Union degree is not two")
    seen, stack = {0}, [0]
    while stack:
        for v in neighbors[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(neighbors)


def switch_distances(old):
    distances, queue = {old: 0}, deque([old])
    while queue:
        matching = queue.popleft()
        for first, second in combinations(matching, 2):
            a, b = first
            c, d = second
            rest = set(matching) - {first, second}
            for replacement in (((a, c), (b, d)), ((a, d), (b, c))):
                new = tuple(sorted(rest | {tuple(sorted(edge)) for edge in replacement}))
                if new not in distances:
                    distances[new] = distances[matching] + 1
                    queue.append(new)
    return distances


def permutation_single_cycle(perm):
    seen, u = set(), 0
    while u not in seen:
        seen.add(u)
        u = perm[u]
    return u == 0 and len(seen) == len(perm)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve previous math review")
    checkpoint_bytes = args.checkpoint.read_bytes()
    require(sha256(checkpoint_bytes).hexdigest() == "57ff51628e6fb2f44797a6d88f35fbee60e0aa4bc795f884337680d5dd3fb4f2",
            "Unexpected authoritative checkpoint")
    checkpoint = json.loads(checkpoint_bytes)
    candidate_path = Path(checkpoint["current_best"]["best_original_candidate_path"])
    raw = candidate_path.read_bytes()
    require(sha256(raw).hexdigest() == checkpoint["current_best"]["best_original_candidate_sha256"], "Candidate changed")
    candidate = json.loads(raw)
    adjacency, _ = full_graph(candidate)
    labels = [{v-1 for v in adjacency[u+15] if 1 <= v <= 14} for u in range(84)]
    edges = list(map(tuple, candidate["overlap_edges_outer_zero_based"]))
    buckets = {}
    for u, v in edges:
        shared = {s//2 for s in labels[u]} & {s//2 for s in labels[v]}
        require(len(shared) == 1, "K edge has no unique root matching")
        group = next(iter(shared))
        signs = [next(s%2 for s in labels[w] if s//2 == group) for w in (u, v)]
        kind = "cross" if signs[0] != signs[1] else "same_" + str(signs[0])
        buckets.setdefault((group, kind), []).append((u, v))
    require(len(buckets) == 21, "Expected21matching classes")
    for u in range(84):
        categories = Counter()
        for v in adjacency[u+15]:
            if v >= 15:
                for symbol in labels[v-15]:
                    if symbol//2 in {s//2 for s in labels[u]}:
                        categories[symbol] += 1
        expected = {symbol for s in labels[u] for symbol in (2*(s//2), 2*(s//2)+1)}
        require(set(categories) == expected and set(categories.values()) == {1}, "Own-label quota decomposition failed")
    coordinates = []
    for (group, kind), matching in sorted(buckets.items()):
        expected_vertices = {u for u in range(84) if any(s//2 == group and
                             (kind == "cross" or s%2 == int(kind[-1])) for s in labels[u])}
        degrees = Counter(u for edge in matching for u in edge)
        require(set(degrees) == expected_vertices and set(degrees.values()) == {1}, "Class not a perfect matching")
        require(len(matching) == (12 if kind == "cross" else 6), "Wrong matching size")
        coordinates.append(dict(root_group=group, matching_class=kind, edge_count=len(matching)))
    controls = []
    for k in (3, 4):
        old = tuple((2*i, 2*i+1) for i in range(k))
        abstract = list(all_matchings(tuple(range(2*k))))
        cycles = [matching for matching in abstract if connected_union(old, matching)]
        distances = switch_distances(old)
        require(set(distances) == set(abstract), "Switch graph does not enumerate all abstract matchings")
        same_expected = 2**(k-1)*factorial(k-1)
        require(len(cycles) == same_expected and {distances[matching] for matching in cycles} == {k-1},
                "Same-sign count or switch-distance formula failed")
        cross = [perm for perm in permutations(range(k)) if permutation_single_cycle(perm)]
        require(len(cross) == factorial(k-1), "Bipartite cycle count formula failed")
        raw_count = 14*comb(6, k)*same_expected + 7*comb(12, k)*len(cross)
        require(raw_count == (5320 if k == 3 else 30870), "Raw cycle family size mismatch")
        controls.append(dict(removed_edges=k, abstract_perfect_matchings=len(abstract),
                             same_sign_single_cycles=len(cycles), bipartite_single_cycles=len(cross),
                             minimum_two_edge_switches_for_each_single_cycle=k-1,
                             unrestricted_switch_distance_checked_by_complete_BFS=True,
                             raw_moves_in21coordinates=raw_count))
    result = dict(status="INDEPENDENT_MATCHING_DECOMPOSITION_AND_ABSTRACT_CYCLE_COUNT_PASS",
                  inputs_sha256={str(args.checkpoint): sha256(checkpoint_bytes).hexdigest(),
                                 str(candidate_path): sha256(raw).hexdigest()},
                  auditor_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  graph_auditor_sha256=sha256(Path(__file__).with_name("audit_certificate.py").read_bytes()).hexdigest(),
                  candidate_matching_classes=coordinates, all84_own_label_categories_checked=True,
                  abstract_controls=controls, producer_or_solver_imported=False,
                  theorem_premises="Within the legal current E0 representation, each outer vertex has four overlap neighbors and four own-label category caps of one. Their partition forces all four category counts to equal one.",
                  move_scope="Each single alternating2k-cycle preserves matching degree and own-label categories. Added-support legality and all full99 partial caps still require independent checks.",
                  merit_scope="Only reoptimized exact primal/dual intervals certify improvement. Frozen-X score is an upper bound and cannot exclude improvements when large; pure root-group/sign relabeling preserves optimum and is not structural progress.",
                  no_concrete_atomic_candidates_enumerated=True,
                  no_completion_or_general_nonexistence_claim=True)
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "controls": controls}))


if __name__ == "__main__":
    main()
