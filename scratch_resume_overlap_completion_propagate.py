"""Elementary exact propagation certificate for the one fixed overlap lift."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json


def main():
    cp = Path('scratch_resume_integral_compression.json')
    lp = Path('scratch_resume_overlap_lift.json')
    c = json.loads(cp.read_bytes())['C']
    known = set(map(tuple, json.loads(lp.read_bytes())['overlap_edges_outer_zero_based']))
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    a = [[0]*84 for _ in range(84)]
    for u, v in combinations(range(84), 2):
        a[u][v] = a[v][u] = (-1 if not set(supports[u//4]) & set(supports[v//4])
                             else int((u, v) in known))
    linear = []
    for u in range(84):
        for symbol in range(14):
            linear.append(('quota', [u, symbol],
                           [(u, v) for v in range(84) if symbol in labels[v]],
                           1 if symbol//2 in supports[u//4] else 2))
    for f, h in combinations(range(21), 2):
        if not set(supports[f]) & set(supports[h]):
            linear.append(('block', [f, h],
                           [(u, v) for u in range(4*f, 4*f+4) for v in range(4*h, 4*h+4)], c[f][h]))
    events = []
    contradiction = None
    def assign(u, v, value, rule, index):
        nonlocal contradiction
        assert u != v
        if a[u][v] == -1:
            a[u][v] = a[v][u] = value
            events.append({'edge': sorted((u, v)), 'value': value, 'rule': rule, 'index': index})
        elif a[u][v] != value:
            contradiction = {'rule': rule, 'index': index, 'opposite_assignment': [u, v, value]}
    rounds = 0
    while contradiction is None:
        rounds += 1
        before = len(events)
        for rule, index, pairs, target in linear:
            lo = sum(a[u][v] == 1 for u, v in pairs)
            unknown = [(u, v) for u, v in pairs if a[u][v] == -1]
            hi = lo+len(unknown)
            if lo > target or hi < target:
                contradiction = {'rule': rule, 'index': index, 'lower': lo, 'upper': hi, 'target': target}
                break
            if lo == target or hi == target:
                for u, v in unknown:
                    assign(u, v, int(hi == target), rule, index)
        if contradiction:
            break
        for u, v in combinations(range(84), 2):
            target = 2-len(set(labels[u]) & set(labels[v]))
            lo = int(a[u][v] == 1)
            hi = int(a[u][v] != 0)
            possible = []
            for w in range(84):
                if a[u][w] == 1 and a[v][w] == 1:
                    lo += 1
                if a[u][w] != 0 and a[v][w] != 0:
                    hi += 1
                    possible.append(w)
            if lo > target or hi < target:
                contradiction = {'rule': 'pair', 'index': [u, v], 'lower': lo, 'upper': hi, 'target': target}
                break
            if lo == target:
                if a[u][v] == -1:
                    assign(u, v, 0, 'pair_lower', [u, v])
                for w in possible:
                    if a[u][w] == 1 and a[v][w] == -1:
                        assign(v, w, 0, 'pair_lower', [u, v])
                    elif a[v][w] == 1 and a[u][w] == -1:
                        assign(u, w, 0, 'pair_lower', [u, v])
            elif hi == target:
                if a[u][v] == -1:
                    assign(u, v, 1, 'pair_upper', [u, v])
                for w in possible:
                    if a[u][w] == -1:
                        assign(u, w, 1, 'pair_upper', [u, v])
                    if a[v][w] == -1:
                        assign(v, w, 1, 'pair_upper', [u, v])
            if contradiction:
                break
        if len(events) == before:
            break
    result = {'status': 'ELEMENTARY_CONTRADICTION' if contradiction else 'PROPAGATION_FIXED_POINT',
              'compression_sha256': hashlib.sha256(cp.read_bytes()).hexdigest(),
              'lift_sha256': hashlib.sha256(lp.read_bytes()).hexdigest(),
              'rounds': rounds, 'assignments': len(events),
              'assignment_histogram': dict(Counter(str(e['value']) for e in events)),
              'contradiction': contradiction, 'events': events,
              'scope': 'Only one fixed overlap partial graph and C. No exclusion of all E0=0 or all sharp compressions.'}
    Path('scratch_resume_overlap_completion_propagate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'events'}))


if __name__ == '__main__':
    main()
