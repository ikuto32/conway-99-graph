"""Bounded E0=0 template-quartet control, not a graph search or exclusion."""
from collections import defaultdict
from itertools import combinations, combinations_with_replacement
import hashlib
import json
from pathlib import Path

SUPPORTS = tuple(combinations(range(7), 2))
INDEX = {x: i for i, x in enumerate(SUPPORTS)}


def templates(source):
    ans = []
    external = sorted(set(range(7)) - set(source))
    for hub in external:
        remaining = sorted(set(external) - {hub})
        for first in combinations(remaining, 2):
            second = tuple(sorted(set(remaining) - set(first)))
            d = [0] * 21
            for group, pair in zip(source, (first, second)):
                for other in pair:
                    d[INDEX[tuple(sorted((group, other)))]] = 1
                    d[INDEX[tuple(sorted((hub, other)))]] = 1
                d[INDEX[pair]] = 2
            ans.append(tuple(d))
    assert len(set(ans)) == 30
    return ans


def main():
    path = Path('scratch_resume_integral_compression.json')
    inp = json.loads(path.read_text())
    c = inp['C']
    records = []
    for fi, source in enumerate(SUPPORTS):
        rows = templates(source)
        pairs = defaultdict(list)
        for a, b in combinations_with_replacement(range(30), 2):
            total = tuple(x + y for x, y in zip(rows[a], rows[b]))
            if all(v <= cap for v, cap in zip(total, c[fi])):
                pairs[total].append((a, b))
        quads = set()
        for total, ab in pairs.items():
            complement = tuple(v - x for v, x in zip(c[fi], total))
            for a, b in ab:
                for cc, dd in pairs.get(complement, []):
                    quads.add(tuple(sorted((a, b, cc, dd))))
        records.append({'source': list(source), 'rows': rows,
                        'quartets': sorted(quads), 'count': len(quads)})
    result = {'status': 'BOUNDED_TEMPLATE_QUARTET_CONTROL_CHECK',
              'scope': 'Only the 30 prior symmetrized templates per source. Empty quartet domains are not a compression or graph exclusion.',
              'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'records': records}
    Path('scratch_resume_uniform_quartet_probe.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'quartet_counts': [r['count'] for r in records]}))


if __name__ == '__main__':
    main()
