"""Independent partial-graph/path and compiled640-cut audit of the walk."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from scratch_next_overlap_alternatives_farkas_audit import build_graph
from scratch_next_overlap_cut_compile import evaluate_compiled


def main():
    path = Path('scratch_follow_overlap_walk.json')
    data = json.loads(path.read_bytes())
    source = Path(data['source'])
    assert sha256(source.read_bytes()).hexdigest() == data['source_sha256']
    known = frozenset(map(tuple, json.loads(source.read_bytes())['overlap_edges_outer_zero_based']))
    labels = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
    labels.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
    vertex_of = {pair: i for i, pair in enumerate(labels)}
    supports = [set(s//2 for s in pair) for pair in labels]
    cp = Path('scratch_resume_integral_compression.json')
    c = json.loads(cp.read_bytes())['C']
    for number, step in enumerate(data['steps'], 1):
        assert step['step'] == number
        removed, added = set(map(tuple, step['removed'])), set(map(tuple, step['added']))
        assert len(removed) == len(added) == 2 and removed <= known and not added & known
        assert Counter(v for edge in removed for v in edge) == Counter(v for edge in added for v in edge)
        before = Counter(tuple(sorted((u//4, v//4))) for u, v in removed)
        after = Counter(tuple(sorted((u//4, v//4))) for u, v in added)
        assert before == after
        known = known-removed | added
        adj, unknown = build_graph({'overlap_edges_outer_zero_based': sorted(known)})
        totals = Counter(tuple(sorted((u//4, v//4))) for u, v in known)
        for f, h in combinations(range(21), 2):
            if supports[4*f] & supports[4*h]:
                assert totals[f, h] == c[f][h]
        for u in range(84):
            for symbol in range(14):
                count = sum(symbol in labels[v-15] for v in adj[u+15] if v >= 15)
                assert count == 1 if symbol//2 in supports[u] else count <= 2
    assert sorted(known) == list(map(tuple, data['overlap_edges_outer_zero_based']))
    compiled_path = Path('scratch_next_overlap_cut_compiled.json')
    compiled = json.loads(compiled_path.read_bytes())
    expected_sha = 'f0f2a851b782f37ddd32e8d3af10da07c35f3ddd2b78a16448fd503fab13277d'
    assert sha256(compiled_path.read_bytes()).hexdigest() == expected_sha
    for name, digest in compiled['input_sha256'].items():
        assert sha256(Path(name).read_bytes()).hexdigest() == digest
    minima, score_count = [], 0
    for cut in compiled['cuts']:
        scores = []
        for mask in range(128):
            permutation = [vertex_of[tuple(s ^ ((mask >> (s//2)) & 1) for s in pair)] for pair in labels]
            assert sorted(permutation) == list(range(84))
            image = {tuple(sorted((permutation[u], permutation[v]))) for u, v in known}
            score = evaluate_compiled(cut, image)[0]
            assert score >= 0
            scores.append(score)
            score_count += 1
        minima.append(min(scores))
    assert minima == data['final_cut_scan']['cut_orbit_minima']
    result = {'status': 'INDEPENDENT_OVERLAP_WALK_AND_640_COMPILED_CUT_AUDIT_PASS',
              'candidate_sha256': sha256(path.read_bytes()).hexdigest(),
              'compiled_sha256': expected_sha, 'steps_verified': len(data['steps']),
              'partial_pair_caps_checked': 4851*len(data['steps']),
              'overlap_edges': 168, 'exposed_graph_edges': 357,
              'sign_conjugate_scores_checked': score_count, 'cut_orbit_minima': minima,
              'cut_bank_or_walk_producer_imported': False, 'solver_used': False,
              'scope': 'A complete overlap assignment passing640 necessary inequalities. Missing336 disjoint edges; no linear-completion witness or SRG.'}
    Path('scratch_follow_overlap_walk_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
