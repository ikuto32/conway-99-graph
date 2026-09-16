"""Pure-stdlib semantic compiler for exact no-gamma CP-SAT capacity cuts.

No solver or existing cut implementation is imported. Overlap and disjoint
variable ids are explicitly recorded, and product keys match generator
p_{u}_{v}_{w} names with u<v.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import hashlib
import json

LABELS = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
LABELS.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair[0]%2, pair[1]%2))
SUPPORT = [set(s//2 for s in pair) for pair in LABELS]
OVERLAP = [pair for pair in combinations(range(84), 2) if len(SUPPORT[pair[0]] & SUPPORT[pair[1]]) == 1]
DISJOINT = [pair for pair in combinations(range(84), 2) if not SUPPORT[pair[0]] & SUPPORT[pair[1]]]
OI = {pair: i+1 for i, pair in enumerate(OVERLAP)}
DI = {pair: i+1 for i, pair in enumerate(DISJOINT)}
ON = [set(v if u == x else u for u, v in OVERLAP if x in (u, v)) for x in range(84)]


def load_specifications():
    mapping = json.loads(Path('scratch_next_overlap_semantic_map.json').read_bytes())
    original = json.loads(Path('scratch_next_overlap_farkas.json').read_bytes())
    original_groups = [dict(kind=mapping['groups'][int(i)]['kind'],
                            coordinate=mapping['groups'][int(i)]['coordinate'], multiplier=value)
                       for i, value in original['group_multipliers'].items()]
    result = [('original', original_groups)]
    for i in range(4):
        data = json.loads(Path(f'scratch_next_overlap_alternatives_r{i}_farkas.json').read_bytes())
        result.append((f'alternative{i}', data['group_multipliers']))
    for _, groups in result:
        seen = set()
        for group in groups:
            kind, coordinate, weight = group['kind'], group['coordinate'], group['multiplier']
            u, v = coordinate
            assert type(u) is int and type(v) is int and type(weight) is int
            assert (kind, u, v) not in seen
            seen.add((kind, u, v))
            assert 0 <= u < 84
            if kind == 'label_quota':
                assert 0 <= v < 14
            else:
                assert kind == 'linear_pair_cap' and u < v < 84 and weight >= 0
    return result


def compile_cut(name, groups):
    constant = 0
    linear, products = Counter(), Counter()
    w_constant = [0]*1680
    w_linear = [Counter() for _ in DISJOINT]
    for group in groups:
        kind, (u, v), weight = group['kind'], group['coordinate'], group['multiplier']
        if kind == 'label_quota':
            symbol = v
            constant += weight*(1 if symbol//2 in SUPPORT[u] else 2)
            for other in range(84):
                if symbol not in LABELS[other]:
                    continue
                pair = tuple(sorted((u, other)))
                if pair in OI:
                    linear[OI[pair]] -= weight
                if pair in DI:
                    w_constant[DI[pair]-1] += weight
        else:
            constant += weight*(2-len(set(LABELS[u]) & set(LABELS[v])))
            if (u, v) in OI:
                linear[OI[u, v]] -= weight
            if (u, v) in DI:
                w_constant[DI[u, v]-1] += weight
            for center in sorted(ON[u] & ON[v]):
                products[u, v, center] -= weight
            # Symbolically expand KX+XK for this pair-cap only.
            for center in range(84):
                for known_end, unknown_end in ((u, v), (v, u)):
                    kp = tuple(sorted((known_end, center)))
                    xp = tuple(sorted((unknown_end, center)))
                    if kp in OI and xp in DI:
                        w_linear[DI[xp]-1][OI[kp]] += weight
    linear = [[i, value] for i, value in sorted(linear.items()) if value]
    products = [[u, v, center, value] for (u, v, center), value in sorted(products.items()) if value]
    assert all(value < 0 for _, _, _, value in products)
    affine = []
    modes = Counter()
    for i, (base, coefficients) in enumerate(zip(w_constant, w_linear)):
        terms = [[j, value] for j, value in sorted(coefficients.items()) if value]
        assert all(value > 0 for _, value in terms)
        lo, hi = base, base+sum(value for _, value in terms)
        mode = 'zero' if lo >= 0 else 'affine_negative' if hi <= 0 else 'exact_max'
        modes[mode] += 1
        affine.append({'disjoint_id': i+1, 'constant': base, 'terms': terms,
                       'w_lower': lo, 'w_upper': hi, 'z_upper': max(0, -lo), 'mode': mode})
    r_lower = constant+sum(min(0, value) for _, value in linear)+sum(value for *_, value in products)
    r_upper = constant+sum(max(0, value) for _, value in linear)
    summary = {'name': name, 'R_constant': constant, 'R_linear_terms': len(linear),
               'R_negative_product_terms': len(products),
               'w_affine_nonzero_terms': sum(len(row['terms']) for row in affine),
               'z_modes': dict(modes), 'R_bounds': [r_lower, r_upper],
               'w_global_bounds': [min(row['w_lower'] for row in affine), max(row['w_upper'] for row in affine)],
               'largest_z_domain_upper': max(row['z_upper'] for row in affine)}
    return {'name': name, 'R_constant': constant, 'R_linear': linear, 'R_products': products,
            'w_affine': affine, 'summary': summary}


def evaluate_compiled(cut, known):
    values = {OI[pair] for pair in known}
    rhs = cut['R_constant']+sum(weight for var, weight in cut['R_linear'] if var in values)
    exact_product_count = 0
    for u, v, center, weight in cut['R_products']:
        active = tuple(sorted((u, center))) in known and tuple(sorted((v, center))) in known
        rhs += weight*active
        exact_product_count += active
    coefficients = [row['constant']+sum(weight for var, weight in row['terms'] if var in values)
                    for row in cut['w_affine']]
    for row, value in zip(cut['w_affine'], coefficients):
        assert row['w_lower'] <= value <= row['w_upper']
        assert 0 <= max(0, -value) <= row['z_upper']
    assert cut['summary']['R_bounds'][0] <= rhs <= cut['summary']['R_bounds'][1]
    score = rhs+sum(max(0, -value) for value in coefficients)
    # The all-one setting is an admissible overestimate of every product.
    inflated_rhs = cut['R_constant']+sum(weight for var, weight in cut['R_linear'] if var in values)
    inflated_rhs += sum(weight for *_, weight in cut['R_products'])
    assert inflated_rhs <= rhs
    return score, rhs, coefficients


def evaluate_direct(groups, known):
    rows = [set() for _ in range(84)]
    for u, v in known:
        assert (u, v) in OI
        rows[u].add(v)
        rows[v].add(u)
    coefficients = [0]*1680
    rhs = 0
    for group in groups:
        kind, (u, v), weight = group['kind'], group['coordinate'], group['multiplier']
        if kind == 'label_quota':
            rhs += weight*((1 if v//2 in SUPPORT[u] else 2)-sum(v in LABELS[w] for w in rows[u]))
            for i, (a, b) in enumerate(DISJOINT):
                if (a == u and v in LABELS[b]) or (b == u and v in LABELS[a]):
                    coefficients[i] += weight
        else:
            rhs += weight*(2-len(set(LABELS[u]) & set(LABELS[v]))-int((u, v) in known)-len(rows[u] & rows[v]))
            if (u, v) in DI:
                coefficients[DI[u, v]-1] += weight
            for a, b in ((u, v), (v, u)):
                for w in rows[a]:
                    pair = tuple(sorted((b, w)))
                    if pair in DI:
                        coefficients[DI[pair]-1] += weight
    return rhs+sum(max(0, -value) for value in coefficients), rhs, coefficients


def main():
    specs = load_specifications()
    cuts = [compile_cut(name, groups) for name, groups in specs]
    all_generator_products = {(u, v, w) for u, v in combinations(range(84), 2) for w in ON[u] & ON[v]}
    assert len(all_generator_products) == 65520
    product_union = {(u, v, w) for cut in cuts for u, v, w, _ in cut['R_products']}
    assert product_union <= all_generator_products
    paths = [Path('scratch_resume_overlap_lift.json')]+[Path(f'scratch_next_overlap_alternatives_r{i}.json') for i in range(4)]
    assignments = [(path.name, set(map(tuple, json.loads(path.read_bytes())['overlap_edges_outer_zero_based']))) for path in paths]
    original = assignments[0][1]
    label_index = {pair: i for i, pair in enumerate(LABELS)}
    for mask in (1, 2, 4, 8, 16, 32, 64):
        permutation = [label_index[tuple(sorted(s ^ ((mask >> (s//2)) & 1) for s in pair))] for pair in LABELS]
        assignments.append((f'original_sign_{mask}', {tuple(sorted((permutation[u], permutation[v]))) for u, v in original}))
    evaluated = []
    for assignment_name, known in assignments:
        scores = []
        for cut, (_, groups) in zip(cuts, specs):
            compiled, direct = evaluate_compiled(cut, known), evaluate_direct(groups, known)
            assert compiled == direct
            scores.append(compiled[0])
        evaluated.append({'assignment': assignment_name, 'scores': scores})
    bank = json.loads(Path('scratch_next_overlap_cut_bank.json').read_bytes())
    assert [row['scores'] for row in evaluated[:5]] == bank['scores_without_upper_multipliers']
    review = json.loads(Path('scratch_next_overlap_cut_review.json').read_bytes())
    original_sign_scores = [evaluated[0]['scores'][0]]+[row['scores'][0] for row in evaluated[5:]]
    assert original_sign_scores == [row['optional_no_upper_multiplier_score'] for row in review['compared_fixed_cut_sign_controls']]
    semantic_inputs = [Path('scratch_next_overlap_farkas.json'),
                       Path('scratch_next_overlap_semantic_map.json'),
                       Path('scratch_next_overlap_farkas_audit.json')]
    for i in range(4):
        semantic_inputs.extend([Path(f'scratch_next_overlap_alternatives_r{i}_farkas.json'),
                                Path(f'scratch_next_overlap_alternatives_r{i}_farkas_audit.json')])
    semantic_inputs.extend([Path('scratch_next_overlap_cut_bank.json'),
                            Path('scratch_next_overlap_cut_review.json'), Path(__file__)])
    report = {'status': 'EXACT_NO_GAMMA_CAPACITY_POLYNOMIAL_COMPILER_CHECK_PASS',
              'overlap_variables': [[i+1, *pair] for i, pair in enumerate(OVERLAP)],
              'disjoint_variables': [[i+1, *pair] for i, pair in enumerate(DISJOINT)],
              'cuts': cuts, 'existing_generator_products': 65520,
              'products_used_by_five_cut_union': len(product_union),
              'checked_assignments': evaluated, 'evaluations_compared_entrywise': 60,
              'affine_coefficients_compared': 60*1680,
              'scope': 'Static exact coefficient compiler and finite arithmetic checks only. No CP-SAT model run, new overlap assignment, or graph feasibility claim.',
              'solver_used': False, 'cut_evaluator_imported': False,
              'input_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths+semantic_inputs}}
    compiled_path = Path('scratch_next_overlap_cut_compiled.json')
    compiled_path.write_text(json.dumps(report, separators=(',', ':'))+'\n')
    summary = {k: v for k, v in report.items() if k not in ('overlap_variables', 'disjoint_variables', 'cuts', 'input_sha256')}
    summary['cut_complexity'] = [cut['summary'] for cut in cuts]
    summary['input_sha256'] = report['input_sha256']
    summary['compiled_sha256'] = hashlib.sha256(compiled_path.read_bytes()).hexdigest()
    Path('scratch_next_overlap_cut_compile_check.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'checked_assignments'}, indent=2))


if __name__ == '__main__':
    main()
