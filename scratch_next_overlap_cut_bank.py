"""Reuse five audited capacity inequalities on complete overlap assignments.

Coordinates are semantic outer-vertex/label indices. Omitting nonnegative
upper-bound multipliers strengthens the box-corrected necessary score.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json


HERE = Path(__file__).resolve().parent
LABELS = tuple((2*a+s, 2*b+t) for a, b in combinations(range(7), 2)
               for s in range(2) for t in range(2))
SUPPORTS = tuple(frozenset(label//2 for label in pair) for pair in LABELS)
EDGES = tuple((u, v) for u, v in combinations(range(84), 2) if not SUPPORTS[u] & SUPPORTS[v])
PAIRS = tuple(combinations(range(84), 2))


def load_cuts():
    review = json.loads((HERE/'scratch_next_overlap_cut_review.json').read_bytes())
    assert review['status'] == 'INDEPENDENT_ARBITRARY_COMPLETE_OVERLAP_CUT_REVIEW_PASS'
    for name in ('scratch_next_overlap_semantic_map.json', 'scratch_next_overlap_farkas.json'):
        assert review['sha256'][name] == hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    metadata = json.loads((HERE/'scratch_next_overlap_semantic_map.json').read_bytes())
    original = json.loads((HERE/'scratch_next_overlap_farkas.json').read_bytes())
    assert metadata['edge_variables'] == [[i+1, u, v] for i, (u, v) in enumerate(EDGES)]
    specifications = [('original', {
        'group_multipliers': [dict(kind=metadata['groups'][int(i)]['kind'],
                                  coordinate=metadata['groups'][int(i)]['coordinate'], multiplier=value)
                              for i, value in original['group_multipliers'].items()],
        'edge_upper_bound_multipliers': [dict(edge=EDGES[int(i)-1], multiplier=value)
                                         for i, value in original['edge_upper_bound_multipliers'].items()],
    })]
    for i in range(4):
        path = HERE/f'scratch_next_overlap_alternatives_r{i}_farkas.json'
        audit = json.loads(path.with_name(path.stem+'_audit.json').read_bytes())
        assert audit['status'] == 'INDEPENDENT_ALTERNATIVE_INTEGER_FARKAS_AUDIT_PASS'
        assert audit['inputs_sha256'][path.name] == hashlib.sha256(path.read_bytes()).hexdigest()
        specifications.append((f'alternative{i}', json.loads(path.read_bytes())))
    compiled = []
    for name, specification in specifications:
        alpha = [[0]*14 for _ in range(84)]
        beta = [[0]*84 for _ in range(84)]
        gamma = dict.fromkeys(EDGES, 0)
        seen = set()
        for group in specification['group_multipliers']:
            kind, (u, v), value = group['kind'], group['coordinate'], group['multiplier']
            assert type(value) is int and (kind, u, v) not in seen
            seen.add((kind, u, v))
            if kind == 'label_quota':
                assert 0 <= u < 84 and 0 <= v < 14
                alpha[u][v] = value
            else:
                assert kind == 'linear_pair_cap' and 0 <= u < v < 84 and value >= 0
                beta[u][v] = beta[v][u] = value
        for bound in specification['edge_upper_bound_multipliers']:
            edge, value = tuple(bound['edge']), bound['multiplier']
            assert edge in gamma and type(value) is int and value >= 0
            gamma[edge] += value
        constant = sum(alpha[u][s]*(1 if s//2 in SUPPORTS[u] else 2)
                       for u in range(84) for s in range(14))
        constant += sum(beta[u][v]*(2-len(set(LABELS[u]) & set(LABELS[v]))) for u, v in PAIRS)
        base = { (u, v): sum(alpha[u][s] for s in LABELS[v])
                        + sum(alpha[v][s] for s in LABELS[u]) + beta[u][v]
                 for u, v in EDGES }
        compiled.append(dict(name=name, alpha=alpha, beta=beta, gamma=gamma,
                             constant=constant, base=base))
    return compiled


def evaluate(known, cut, include_upper=False):
    rows = [set() for _ in range(84)]
    for u, v in known:
        assert type(u) is int and type(v) is int and 0 <= u < v < 84
        assert len(SUPPORTS[u] & SUPPORTS[v]) == 1
        rows[u].add(v)
        rows[v].add(u)
    alpha, beta = cut['alpha'], cut['beta']
    rhs = cut['constant']
    for u, v in known:
        rhs -= sum(alpha[u][s] for s in LABELS[v])+sum(alpha[v][s] for s in LABELS[u])+beta[u][v]
    rhs -= sum(beta[u][v]*len(rows[u] & rows[v]) for u, v in PAIRS)
    lower = 0
    for u, v in EDGES:
        coefficient = cut['base'][u, v] + sum(beta[u][a] for a in rows[v]) + sum(beta[v][a] for a in rows[u])
        if include_upper:
            coefficient += cut['gamma'][u, v]
        lower += min(0, coefficient)
    if include_upper:
        rhs += sum(cut['gamma'].values())
    return {'score': rhs-lower, 'combined_rhs': rhs, 'box_lower_bound': lower}


def main():
    paths = [HERE/'scratch_resume_overlap_lift.json']
    paths += [HERE/f'scratch_next_overlap_alternatives_r{i}.json' for i in range(4)]
    cuts = load_cuts()
    matrix, upper_matrix = [], []
    for path in paths:
        known = frozenset(map(tuple, json.loads(path.read_bytes())['overlap_edges_outer_zero_based']))
        row, upper_row = [], []
        for cut in cuts:
            plain, upper = evaluate(known, cut), evaluate(known, cut, include_upper=True)
            assert plain['score'] <= upper['score']
            row.append(plain['score'])
            upper_row.append(upper['score'])
        matrix.append(row)
        upper_matrix.append(upper_row)
    assert [upper_matrix[i][i] for i in range(5)] == [-807, -819, -793, -796, -797]
    from scratch_next_overlap_cut import evaluate as original_evaluate
    from scratch_next_overlap_cut_orbit import transform
    original = frozenset(map(tuple, json.loads(paths[0].read_bytes())['overlap_edges_outer_zero_based']))
    for mask in [0, 1, 2, 4, 8, 16, 32, 64]:
        image = transform(original, mask)
        assert evaluate(image, cuts[0], include_upper=True)['score'] == original_evaluate(image)['score']
    result = {
        'status': 'FIVE_COORDINATE_CAPACITY_CUTS_CROSS_EVALUATED',
        'row_assignments': [path.name for path in paths],
        'column_cuts': [cut['name'] for cut in cuts],
        'scores_without_upper_multipliers': matrix,
        'scores_with_upper_multipliers': upper_matrix,
        'original_evaluator_sign_controls_matched': 8,
        'inputs_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        'scope': 'Finite evaluations of necessary cuts for complete E0=0 overlap assignments. Negative rejects, nonnegative gives no feasibility evidence. No global exclusion.',
    }
    (HERE/'scratch_next_overlap_cut_bank.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
