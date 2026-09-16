"""Independent standard-library replay of one exact four-row partial graph."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys


def audit_one(source_index=0):
    inp = Path(f'scratch_resume_uniform_fibre_incidence_f{source_index}_q16.json')
    cp = Path('scratch_resume_integral_compression.json')
    w = json.loads(inp.read_text())
    cdata = json.loads(cp.read_text())
    assert w['input_sha256'] == hashlib.sha256(cp.read_bytes()).hexdigest()
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    fi = w['source_index']
    assert fi == source_index
    source = supports[fi]
    source_indices = list(range(4*fi, 4*fi+4))
    ns = list(map(set, w['outer_neighbor_indices']))
    assert len(ns) == 4
    degrees = []
    for row in ns:
        assert len(row) == 12 and all(0 <= y < 84 and y//4 != fi for y in row)
        quotas = Counter(label for y in row for label in labels[y])
        assert all(quotas[label] == (1 if label//2 in source else 2) for label in range(14))
        d = [sum(y//4 == f for y in row) for f in range(21)]
        assert sum(v*v for v in d) == 16
        degrees.append(d)
    assert degrees == w['degree_rows']
    assert [sum(d[f] for d in degrees) for f in range(21)] == cdata['C'][fi]
    intersections = []
    for p, q in combinations(range(4), 2):
        outer = len(ns[p] & ns[q])
        root = len(set(labels[source_indices[p]]) & set(labels[source_indices[q]]))
        assert outer == 2-root
        intersections.append({'source_corners': [p, q], 'outer': outer, 'first_layer': root})
    loads = [sum(y in row for row in ns) for y in range(84)]
    assert sum(loads) == 48 and sum(v*v for v in loads) == 64
    characters = [(1, 1, 1, 1), (1, 1, -1, -1),
                  (1, -1, 1, -1), (1, -1, -1, 1)]
    signed = [[sum(char[p]*int(y in ns[p]) for p in range(4)) for y in range(84)]
              for char in characters]
    signed_gram = [[sum(x*y for x, y in zip(a, b)) for b in signed] for a in signed]
    assert signed_gram == [[([64, 40, 40, 48][a] if a == b else 0) for b in range(4)]
                           for a in range(4)]
    adj = [set() for _ in range(99)]
    def edge(u, v):
        assert u != v
        adj[u].add(v)
        adj[v].add(u)
    for u in range(1, 15):
        edge(0, u)
    for a in range(7):
        edge(1+2*a, 2+2*a)
    for y, label in enumerate(labels):
        for a in label:
            edge(y+15, a+1)
    for p, row in enumerate(ns):
        for y in row:
            edge(source_indices[p]+15, y+15)
    assert sum(map(len, adj))//2 == 237
    assert all(len(adj[u]) == 14 for u in list(range(15)) + [y+15 for y in source_indices])
    checked = 0
    for u, v in combinations(range(99), 2):
        assert len(adj[u] & adj[v]) <= (1 if v in adj[u] else 2)
        checked += 1
    # Independent parity obstruction for every quartet from the old orbit:
    # doubled matching vanishes mod 2; four hub-stars sum to a K5 cut.
    cut_sizes = sorted({sum((u in part) != (v in part) for u, v in combinations(range(5), 2))
                        for size in range(6) for part in combinations(range(5), size)})
    assert cut_sizes == [0, 4, 6]
    sharp_odd_counts = []
    for f, support in enumerate(supports):
        values = [cdata['C'][f][g] for g, other in enumerate(supports) if set(support).isdisjoint(other)]
        assert Counter(values) == Counter({3: 8, 4: 2})
        sharp_odd_counts.append(sum(v%2 for v in values))
    assert set(sharp_odd_counts) == {8}
    report = {'status': 'INDEPENDENT_SINGLE_FIBRE_INCIDENCE_CONTROL_AND_TEMPLATE_PARITY_AUDIT_PASS',
              'witness_sha256': hashlib.sha256(inp.read_bytes()).hexdigest(),
              'compression_sha256': hashlib.sha256(cp.read_bytes()).hexdigest(),
              'source_support': list(source), 'exposed_edges': 237,
              'partial_pair_caps_checked': checked, 'exact_label_quotas_checked': 56,
              'exact_source_pair_intersections': intersections,
              'incoming_source_load_square_sum': sum(v*v for v in loads),
              'signed_incidence_character_gram': signed_gram,
              'separately_imposed_outgoing_degree_row_square_sums': [16]*4,
              'old_template_quartet_disjoint_odd_counts_possible': cut_sizes,
              'sharp_compression_disjoint_odd_counts': sharp_odd_counts,
              'scope': 'One fibre exact positive partial-incidence control, not a graph. Old 30-template obstruction excludes that restricted construction only, not C or E0=0.',
              'producer_imported': False, 'solver_used_by_audit': False}
    return report


def main():
    if '--all' not in sys.argv:
        report = audit_one()
        Path('scratch_resume_uniform_fibre_incidence_audit.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(report, indent=2))
        return
    manifest = json.loads(Path('scratch_resume_uniform_fibre_incidence_all.json').read_text())
    assert manifest['status'] == 'COMPLETE' and len(manifest['records']) == 21
    records = []
    by_vertex = [None] * 84
    drows = []
    supports = list(combinations(range(7), 2))
    c = json.loads(Path('scratch_resume_integral_compression.json').read_text())['C']
    for fi, item in enumerate(manifest['records']):
        assert item['source_index'] == fi
        path = Path(f'scratch_resume_uniform_fibre_incidence_f{fi}_q16.json')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        assert item['status'] in ('OPTIMAL', 'FEASIBLE')
        record = audit_one(fi)
        records.append(record)
        cert = json.loads(path.read_text())
        for p, row in enumerate(cert['outer_neighbor_indices']):
            by_vertex[4*fi+p] = set(row)
        drows.extend(cert['degree_rows'])
    mismatches = [[x, y] for x, y in combinations(range(84), 2)
                  if (y in by_vertex[x]) != (x in by_vertex[y])]
    g = [[sum(row[a]*row[b] for row in drows) for b in range(21)] for a in range(21)]
    target = [[48*int(a == b)+32-c[a][b]-8*len(set(supports[a]) & set(supports[b]))
               for b in range(21)] for a in range(21)]
    gram_discrepancies = [[a, b, g[a][b]-target[a][b]] for a in range(21) for b in range(a, 21)
                         if g[a][b] != target[a][b]]
    report = {'status': 'INDEPENDENT_ALL_21_SEPARATE_FIBRE_CONTROLS_AUDIT_PASS',
              'records': records, 'partial_pair_caps_checked': 21*4851,
              'exact_label_quotas_checked': 21*56, 'source_pair_intersections_checked': 21*6,
              'combined_directed_row_reciprocity_mismatch_count': len(mismatches),
              'first_reciprocity_mismatches': mismatches[:10],
              'combined_directed_degree_gram_bad_upper_entries': len(gram_discrepancies),
              'combined_directed_degree_gram_discrepancies': gram_discrepancies,
              'scope': 'Every fibre separately lifts to an exact four-row partial graph. Chosen lifts are not synchronized; listed reciprocity/Gram mismatches explicitly prevent graph claims.'}
    Path('scratch_resume_uniform_fibre_incidence_all_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('records', 'combined_directed_degree_gram_discrepancies')}, indent=2))


if __name__ == '__main__':
    main()
