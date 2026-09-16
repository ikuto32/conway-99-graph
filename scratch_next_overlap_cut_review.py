"""Independent exact review of the cut semantics; no solver or cut imports."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json


def main():
    cert_path = Path('scratch_next_overlap_farkas.json')
    map_path = Path('scratch_next_overlap_semantic_map.json')
    cut_path = Path('scratch_next_overlap_cut.py')
    cert = json.loads(cert_path.read_bytes())
    metadata = json.loads(map_path.read_bytes())
    # Build labels from fourteen symbols, independently of the evaluator's
    # seven-group Cartesian-product loop.
    labels = [pair for pair in combinations(range(14), 2) if pair[0]//2 != pair[1]//2]
    labels.sort(key=lambda p: (p[0]//2, p[1]//2, p[0]%2, p[1]%2))
    support = [set(a//2 for a in pair) for pair in labels]
    edges = [pair for pair in combinations(range(84), 2) if support[pair[0]].isdisjoint(support[pair[1]])]
    assert len(edges) == 1680
    assert metadata['edge_variables'] == [[i+1, *pair] for i, pair in enumerate(edges)]
    alpha = [[0]*14 for _ in range(84)]
    beta = [[0]*84 for _ in range(84)]
    kinds = Counter()
    for key, value in cert['group_multipliers'].items():
        assert type(value) is int and value != 0
        group = metadata['groups'][int(key)]
        u, v = group['coordinate']
        assert type(u) is int and type(v) is int and 0 <= u < 84
        if group['kind'] == 'label_quota':
            assert group['equality'] is True and 0 <= v < 14
            alpha[u][v] += value
        else:
            assert group['kind'] == 'linear_pair_cap'
            assert group['equality'] is False and u < v < 84 and value > 0
            beta[u][v] += value
            beta[v][u] += value
        kinds[group['kind']] += 1
    gamma = [0]*1680
    for key, value in cert['edge_upper_bound_multipliers'].items():
        assert type(value) is int and value > 0 and 1 <= int(key) <= 1680
        gamma[int(key)-1] = value

    def evaluate_direct(known):
        row = [set() for _ in range(84)]
        for u, v in known:
            assert 0 <= u < v < 84 and len(support[u] & support[v]) == 1
            row[u].add(v)
            row[v].add(u)
        q = [[(1 if s//2 in support[u] else 2)-sum(s in labels[v] for v in row[u])
              for s in range(14)] for u in range(84)]
        r = {(u, v): 2-len(set(labels[u]) & set(labels[v]))-int(v in row[u])-len(row[u] & row[v])
             for u, v in combinations(range(84), 2)}
        rhs = sum(gamma)+sum(alpha[u][s]*q[u][s] for u in range(84) for s in range(14))
        rhs += sum(beta[u][v]*r[u, v] for u, v in combinations(range(84), 2))
        coefficients = []
        for i, (a, b) in enumerate(edges):
            w = gamma[i]+sum(alpha[a][s] for s in labels[b])+sum(alpha[b][s] for s in labels[a])+beta[a][b]
            w += sum(beta[a][u] for u in row[b])+sum(beta[b][u] for u in row[a])
            coefficients.append(w)
        lower = sum(min(0, w) for w in coefficients)
        assert sum(w for w in coefficients if w < 0) == lower
        for numerator in (0, 1, 2):
            assert numerator*sum(coefficients) >= 2*lower
        return rhs-lower, rhs, lower, coefficients, row, q, r

    original = set(map(tuple, json.loads(Path('scratch_resume_overlap_lift.json').read_bytes())['overlap_edges_outer_zero_based']))
    scored = evaluate_direct(original)
    assert scored[:3] == (-807, -807, 0)
    assert {str(i+1): str(w) for i, w in enumerate(scored[3]) if w} == cert['nonzero_edge_coefficients']
    # Exhaust the128 sign permutations and their group composition, but do
    # not duplicate the parent's128 score evaluations.
    label_index = {pair: i for i, pair in enumerate(labels)}
    permutations = []
    for mask in range(128):
        p = [label_index[tuple(sorted(s ^ ((mask >> (s//2)) & 1) for s in pair))] for pair in labels]
        assert sorted(p) == list(range(84))
        assert all(support[x] == support[p[x]] for x in range(84))
        permutations.append(p)
    for a in range(128):
        for b in range(128):
            assert all(permutations[a][permutations[b][x]] == permutations[a ^ b][x] for x in range(84))
    previous = json.loads(Path('scratch_next_overlap_cut_signs.json').read_bytes())
    records = []
    for old in previous['records']:
        mask = old['flip_mask']
        p = permutations[mask]
        image = {tuple(sorted((p[u], p[v]))) for u, v in original}
        score, rhs, lower, coefficients, row, q, r = evaluate_direct(image)
        assert score == old['score'] and (score < 0) == old['rejected_by_one_fixed_cut']
        # Covariance of each underlying semantic constraint, in contrast to
        # invariance of its fixed-multiplier combination.
        for u in range(84):
            for s in range(14):
                sp = s ^ ((mask >> (s//2)) & 1)
                assert q[p[u]][sp] == scored[5][u][s]
        for u, v in combinations(range(84), 2):
            assert r[tuple(sorted((p[u], p[v])))] == scored[6][u, v]
        no_gamma_score = rhs-sum(gamma)-sum(min(0, w-gamma[i]) for i, w in enumerate(coefficients))
        assert no_gamma_score <= score
        records.append({'flip_mask': mask, 'score': score, 'rhs': rhs, 'box_lower': lower,
                        'optional_no_upper_multiplier_score': no_gamma_score})
    # Generic algebra check on unrelated complete overlap assignments,
    # including invalid dense assignments. These are semantic unit controls,
    # not possible SRGs or solver candidates.
    overlaps = [pair for pair in combinations(range(84), 2) if len(support[pair[0]] & support[pair[1]]) == 1]
    cases = [set(), set(overlaps), {pair for i, pair in enumerate(overlaps) if (37*i+11)%101 < 17}]
    pair_identities = quota_identities = 0
    for case_number, known in enumerate(cases):
        score, rhs, lower, coefficients, row, q, r = evaluate_direct(known)
        xx = [[0]*84 for _ in range(84)]
        for i, (u, v) in enumerate(edges):
            # Twice a nonnegative box variable; includes0,1/2,1.
            xx[u][v] = xx[v][u] = (i*17+case_number)%3
        bb = [[xx[u][v]+2*int(v in row[u]) for v in range(84)] for u in range(84)]
        for u, v in combinations(range(84), 2):
            linear_twice = xx[u][v]+sum(xx[v][w] for w in row[u])+sum(xx[u][w] for w in row[v])
            left = 4*r[u, v]-2*linear_twice
            right = 4*(2-len(set(labels[u]) & set(labels[v])))-2*bb[u][v]
            right -= sum(bb[u][w]*bb[w][v] for w in range(84))
            right += sum(xx[u][w]*xx[w][v] for w in range(84))
            assert left == right
            pair_identities += 1
        for u in range(84):
            for symbol in range(14):
                lhs = 2*q[u][symbol]-sum(xx[u][v] for v in range(84) if symbol in labels[v])
                rhsq = 2*(1 if symbol//2 in support[u] else 2)-sum(bb[u][v] for v in range(84) if symbol in labels[v])
                assert lhs == rhsq
                quota_identities += 1
        assert sum(w*xx[u][v] for w, (u, v) in zip(coefficients, edges)) >= 2*lower
    report = {'status': 'INDEPENDENT_ARBITRARY_COMPLETE_OVERLAP_CUT_REVIEW_PASS',
              'group_multiplier_kinds': dict(kinds), 'disjoint_edge_variables': 1680,
              'original_score': -807, 'compared_fixed_cut_sign_controls': records,
              'sign_group_actions_checked': 128, 'sign_group_compositions_checked': 128*128,
              'generic_pair_cap_algebra_identities_checked': pair_identities,
              'generic_label_quota_algebra_identities_checked': quota_identities,
              'solver_used': False, 'base_cut_imported': False,
              'scope': 'Sound for a complete overlap0/1 assignment with all same-fibre edges absent. Not a safe partial-prefix pruning rule. Current artifact/index provenance verified; no C totals used.',
              'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cert_path, map_path, cut_path, Path(__file__))}}
    Path('scratch_next_overlap_cut_review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'sha256'}, indent=2))


if __name__ == '__main__':
    main()
