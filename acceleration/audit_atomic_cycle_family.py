"""Independent complete-set check of the atomic matching-cycle subfamily.

Enumerates endpoint perfect matchings/bijections and tests cycle connectivity;
does not use the Rust ordered/oriented old-edge construction. Actual 99-vertex
Python set neighborhoods check all affected pair constraints in every final.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations
import json
from math import comb, factorial
from pathlib import Path
import time

from audit_certificate import full_graph, integer, require

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def canonical(u, v):
    return (u,v) if u < v else (v,u)


def edge_set(value, count):
    require(type(value) is list and len(value) == count, 'Wrong edge-list length')
    require(all(type(e) is list and len(e) == 2 and all(map(integer,e)) and
                0 <= e[0] < e[1] < 84 for e in value), 'Invalid canonical edge')
    result = frozenset(map(tuple,value))
    require(len(result) == count, 'Repeated edge')
    return result


def all_matchings(vertices):
    if not vertices:
        yield ()
        return
    u = vertices[0]
    for i in range(1,len(vertices)):
        v = vertices[i]
        rest = vertices[1:i] + vertices[i+1:]
        for matching in all_matchings(rest):
            yield (canonical(u,v),) + matching


def one_cycle(old, new):
    if old & new:
        return False
    graph = defaultdict(set)
    for u,v in old | new:
        graph[u].add(v); graph[v].add(u)
    if any(len(row) != 2 for row in graph.values()):
        return False
    reached, todo = set(), [next(iter(graph))]
    while todo:
        u = todo.pop()
        if u in reached:
            continue
        reached.add(u); todo.extend(graph[u]-reached)
    return len(reached) == len(graph)


def enumerate_family(candidate, sizes):
    adjacency, _ = full_graph(candidate)
    original = edge_set(candidate['overlap_edges_outer_zero_based'],168)
    labels = [{(s-1)//2:(s-1)%2 for s in adjacency[u+15] if 1 <= s <= 14} for u in range(84)]
    supports = [set(row) for row in labels]
    classes = defaultdict(list)
    for u,v in sorted(original):
        common = supports[u] & supports[v]
        require(len(common) == 1, 'Wrong overlap support')
        group = next(iter(common))
        su,sv = labels[u][group],labels[v][group]
        label = 'cross' if su != sv else f'same_{su}'
        classes[group,label].append((u,v))
    require(len(classes) == 21, 'Missing matching class')
    for (group,label),edges in classes.items():
        expected = 12 if label == 'cross' else 6
        require(len(edges) == expected and set(Counter(u for e in edges for u in e).values()) == {1},
                'Class is not the required perfect matching')
    legal, by_class = {}, []
    pair_checks = 0
    for size in sizes:
        for (group,label),edges in sorted(classes.items()):
            counts = dict(root_group=group,matching_class=label,cycle_size=size,raw_cycles=0,
                          support_rejected=0,cap_rejected=0,legal_cycles=0)
            for selected in combinations(edges,size):
                removed = frozenset(selected)
                vertices = sorted(u for edge in removed for u in edge)
                if label == 'cross':
                    left = [u for u in vertices if labels[u][group] == 0]
                    right = [u for u in vertices if labels[u][group] == 1]
                    replacements = (tuple(canonical(u,v) for u,v in zip(left,p)) for p in permutations(right))
                else:
                    replacements = all_matchings(vertices)
                for replacement in replacements:
                    added = frozenset(replacement)
                    if not one_cycle(removed,added):
                        continue
                    counts['raw_cycles'] += 1
                    if any(len(supports[u] & supports[v]) != 1 for u,v in added):
                        counts['support_rejected'] += 1
                        continue
                    require(not (added & original), 'New class edge unexpectedly already present')
                    changed = [u+15 for u in vertices]
                    rows = adjacency.copy()
                    for u in changed:
                        rows[u] = set(rows[u])
                    for u,v in removed:
                        rows[u+15].remove(v+15); rows[v+15].remove(u+15)
                    for u,v in added:
                        rows[u+15].add(v+15); rows[v+15].add(u+15)
                    valid = True
                    for u in changed:
                        for v in range(99):
                            if u == v:
                                continue
                            pair_checks += 1
                            if len(rows[u] & rows[v]) > (1 if v in rows[u] else 2):
                                valid = False; break
                        if not valid:
                            break
                    if not valid:
                        counts['cap_rejected'] += 1
                        continue
                    for u in changed:
                        require(len(rows[u]) == 6, 'Changed degree')
                        for symbol in range(1,15):
                            if (symbol-1)//2 in supports[u-15]:
                                require(len(rows[u] & rows[symbol]) == (1 if symbol in rows[u] else 2),
                                        'Own-label quota violated')
                    signature = (tuple(sorted(removed)),tuple(sorted(added)))
                    require(signature not in legal, 'Independent enumeration duplicated a move')
                    legal[signature] = (group,label,size)
                    counts['legal_cycles'] += 1
            expected_raw = comb(12,size)*factorial(size-1) if label == 'cross' else comb(6,size)*2**(size-1)*factorial(size-1)
            require(counts['raw_cycles'] == expected_raw, 'Independent raw-count formula mismatch')
            by_class.append(counts)
    return original,legal,by_class,pair_checks


def audit(candidate, native):
    require(native['status'] == 'COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION', 'Wrong native status')
    require(native['cycle_size'] in ('3','4','both'), 'Wrong cycle-size mode')
    sizes = [3,4] if native['cycle_size'] == 'both' else [int(native['cycle_size'])]
    original,expected,counts,pair_checks = enumerate_family(candidate,sizes)
    require(type(native['moves']) is list and type(native['overlap_candidates']) is list and
            len(native['moves']) == len(native['overlap_candidates']), 'Misaligned native output')
    actual = set()
    for move,final in zip(native['moves'],native['overlap_candidates']):
        size = move['cycle_size']
        require(type(size) is int and size in sizes, 'Wrong move size')
        removed,added = edge_set(move['removed'],size),edge_set(move['added'],size)
        require(removed <= original and not added & original, 'Invalid edge toggles')
        signature = (tuple(sorted(removed)),tuple(sorted(added)))
        require(signature in expected, 'Native move missing from independent legal family')
        require(signature not in actual, 'Duplicate native move')
        actual.add(signature)
        require(expected[signature] == (move['root_group'],move['matching_class'],size), 'Wrong matching metadata')
        cycle = move['alternating_cycle']
        require(type(cycle) is list and len(cycle) == 2*size and all(map(integer,cycle)) and
                len(set(cycle)) == 2*size and all(0 <= u < 84 for u in cycle), 'Invalid alternating cycle')
        cycle_removed = frozenset(canonical(cycle[2*i],cycle[2*i+1]) for i in range(size))
        cycle_added = frozenset(canonical(cycle[2*i+1],cycle[(2*i+2)%(2*size)]) for i in range(size))
        require((cycle_removed,cycle_added) == (removed,added), 'Cycle encoding mismatch')
        result = edge_set(final,168)
        require(result == (original-removed)|added, 'Wrong native final candidate')
        require(final == [list(e) for e in sorted(result)], 'Unsorted native final candidate')
    require(actual == set(expected), 'Native family is incomplete')
    require(sorted(native['by_class'],key=lambda x:(x['cycle_size'],x['root_group'],x['matching_class'])) ==
            sorted(counts,key=lambda x:(x['cycle_size'],x['root_group'],x['matching_class'])), 'Per-class count mismatch')
    require(native['raw_cycles'] == sum(c['raw_cycles'] for c in counts), 'Raw total mismatch')
    require(native['legal_cycles'] == len(expected), 'Legal total mismatch')
    return dict(status='INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS',cycle_size=native['cycle_size'],
                raw_cycles=native['raw_cycles'],legal_cycles=len(expected),by_class=counts,
                changed_pair_constraints_checked=pair_checks,initial_full99_pair_caps_checked=4851,
                method='Recursive endpoint perfect matchings / bipartite bijections; independent connected-cycle test; Python set neighborhoods on every affected row pair; exact legal-move set equality.',
                scope='Completeness only within the stated single-matching single-cycle subfamily and selected sizes. No star-domain/AC or graph-completion claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    require(not args.out.exists(),'Preserve prior audit')
    candidate,native = [json.loads(p.read_bytes()) for p in (args.candidate,args.native)]
    tokens = args.input.read_text(encoding='ascii').split()
    require(len(tokens) == 338 and tokens[:2] == ['C99OVERLAPS1','1'],'Wrong native input shape')
    input_edges = [list(map(int,tokens[i:i+2])) for i in range(2,338,2)]
    require(edge_set(input_edges,168) == edge_set(candidate['overlap_edges_outer_zero_based'],168), 'Candidate/input mismatch')
    started = time.perf_counter()
    result = audit(candidate,native)
    result['elapsed_seconds'] = time.perf_counter()-started
    sources = [args.candidate,args.input,args.native,Path(__file__),ROOT/'acceleration/audit_certificate.py',
               ROOT/'acceleration/overlap_cycle_neighbors.rs',ROOT/'acceleration/build/overlap_cycle_neighbors.exe']
    result['inputs_sha256'] = {key(p):digest(p) for p in sources}
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','by_class')}))


if __name__ == '__main__':
    main()
