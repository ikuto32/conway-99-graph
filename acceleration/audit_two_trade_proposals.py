"""Independently replay every intermediate and final two-trade proposal.

Uses Python set neighborhoods for all 99 vertices; imports no native producer
or search driver. This checks saved proposals, not coverage or sampling quality.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import full_graph, integer, require

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def graph_check(edges):
    adjacency, _ = full_graph({'overlap_edges_outer_zero_based': edges})
    for u in range(15, 99):
        own_groups = {(s-1)//2 for s in adjacency[u] if 1 <= s <= 14}
        require(len(own_groups) == 2, 'Wrong outer support')
        for s in range(1, 15):
            if (s-1)//2 in own_groups:
                expected = 1 if s in adjacency[u] else 2
                require(len(adjacency[u] & adjacency[s]) == expected,
                        f'Own-label quota failed at outer {u-15}, symbol {s-1}')


def edge_set(value, expected):
    require(type(value) is list and len(value) == expected, 'Wrong edge list length')
    require(all(type(e) is list and len(e) == 2 and all(map(integer,e)) and
                0 <= e[0] < e[1] < 84 for e in value), 'Invalid canonical edge')
    result = set(map(tuple, value))
    require(len(result) == expected, 'Duplicate edge')
    return result


def audit(candidate, proposal):
    original = edge_set(candidate['overlap_edges_outer_zero_based'], 168)
    graph_check([list(e) for e in sorted(original)])
    require(proposal['status'] == 'BOUNDED_TWO_TRADE_PROPOSALS', 'Wrong proposal status')
    paths, finals = proposal['trade_paths'], proposal['overlap_candidates']
    require(type(paths) is list and type(finals) is list and len(paths) == len(finals), 'Misaligned paths')
    require(proposal['returned_candidates'] == len(finals) <= proposal['sample_limit'], 'Wrong candidate count')
    seen, net_removed_counts = set(), []
    for index, (path, final) in enumerate(zip(paths, finals)):
        require(type(path) is list and len(path) == 2, 'Every path must contain exactly two trades')
        current = set(original)
        for step, trade in enumerate(path):
            removed, added = edge_set(trade['removed'], 2), edge_set(trade['added'], 2)
            old_vertices = [u for e in removed for u in e]
            new_vertices = [u for e in added for u in e]
            require(len(set(old_vertices)) == 4 and sorted(old_vertices) == sorted(new_vertices),
                    'Trade does not preserve the four endpoint degrees')
            require(removed <= current and not (added & current), 'Trade toggles the wrong edges')
            current = (current - removed) | added
            require(len(current) == 168, 'Trade changed edge count')
            graph_check([list(e) for e in sorted(current)])
        expected = edge_set(final, 168)
        require(final == [list(e) for e in sorted(expected)], 'Final candidate not canonically sorted')
        require(current == expected, f'Final mismatch at proposal {index}')
        net_removed = len(original-current)
        require(net_removed >= 3, 'Path collapses to at most one two-edge trade')
        net_removed_counts.append(net_removed)
        signature = tuple(sorted(current))
        require(signature not in seen, 'Repeated final graph')
        seen.add(signature)
    return dict(status='INDEPENDENT_TWO_TRADE_REPLAY_PASS', candidates=len(finals),
                graph_states_checked=1+2*len(finals),
                full99_pair_caps_checked=(1+2*len(finals))*4851,
                exact_own_label_quotas_checked=(1+2*len(finals))*336,
                net_removed_counts=net_removed_counts,
                scope='All saved intermediate/final partial graphs and two-step paths independently checked. No domain/AC claim, sampling uniformity or exhaustive coverage claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--proposals', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior audit')
    candidate, proposal = [json.loads(p.read_bytes()) for p in (args.candidate, args.proposals)]
    tokens = args.input.read_text(encoding='ascii').split()
    require(len(tokens) == 338 and tokens[:2] == ['C99OVERLAPS1','1'], 'Wrong native input shape')
    native_edges = [list(map(int,tokens[i:i+2])) for i in range(2,338,2)]
    require(edge_set(native_edges,168) == edge_set(candidate['overlap_edges_outer_zero_based'],168),
            'Native input/candidate association mismatch')
    result = audit(candidate, proposal)
    paths = [args.candidate, args.input, args.proposals, Path(__file__),
             ROOT/'acceleration/audit_certificate.py', ROOT/'acceleration/overlap_two_neighbors.rs',
             ROOT/'acceleration/build/overlap_two_neighbors.exe']
    result['inputs_sha256'] = {key(p):digest(p) for p in paths}
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','net_removed_counts')}))


if __name__ == '__main__':
    main()
