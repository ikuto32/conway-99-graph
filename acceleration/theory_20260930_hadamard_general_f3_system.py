"""Candidate producer for the preregistered general balanced GF(3) screen.

No solver, import-time execution, independent approval, or shortened nogoods.
The frozen first-branch elimination routine is shared producer code.
"""
from itertools import combinations
import theory_20260930_hadamard_f3_phases as linear


def build(raw, projection):
    supports = [[a for a in range(12) if raw['L'][a][d]] for d in range(60)]
    groups = []
    for support in supports:
        if support not in groups:
            groups.append(support)
    linear.need(len(groups) == 20 and all(supports.count(s) == 3 for s in groups), '20 triple supports')
    patterns = projection['selected_group_parity_patterns']
    linear.need(len(patterns) == 20 and all(len(p) == 6 and p[0] == 0 and all(type(x) is int and x in (0, 1) for x in p) and sum(p) in (0, 3) for p in patterns), 'normalized constant/mixed patterns')
    signs = [[1 if x == 0 else 2 for x in p] for p in patterns]
    variables = [dict(index=6*g+i, group=g, position=i, coordinate=a, sign=signs[g][i]) for g, support in enumerate(groups) for i, a in enumerate(support)]
    rows, functionals, pairs = [], [], []

    def form(terms):
        result = [0]*120
        for index, coefficient in terms:
            result[index] = (result[index] + coefficient) % 3
        return result

    def equation(kind, terms, dependencies, **metadata):
        rows.append(dict(index=len(rows), kind=kind, coefficients=form(terms), rhs=0,
                         parity_dependency_groups=dependencies, **metadata))

    for g in range(20):
        equation('column_gauge', [(6*g, 1)], [], group=g)
    for g in range(20):
        if not any(patterns[g]):
            equation('local_constant_sum', [(6*g+i, 1) for i in range(6)], [g], group=g, positions=list(range(6)))
        else:
            for sign in (1, 2):
                positions = [i for i in range(6) if signs[g][i] == sign]
                linear.need(len(positions) == 3, 'mixed sign population')
                equation('local_same_sign_sum', [(6*g+i, 1) for i in positions], [g], group=g, sign=sign, positions=positions)
                for i, j in combinations(positions, 2):
                    functionals.append(dict(index=len(functionals), kind='local_same_sign_distinct',
                        coefficients=form([(6*g+j, 1), (6*g+i, -1)]), required='nonzero in GF(3)',
                        group=g, positions=[i, j], parity_dependency_groups=[g]))
    for a, b in combinations(range(12), 2):
        if a ^ 1 == b:
            continue
        incident = [g for g, support in enumerate(groups) if a in support and b in support]
        linear.need(len(incident) == 5, 'five incident groups')
        relative = []
        for g in incident:
            i, j = groups[g].index(a), groups[g].index(b)
            sign = signs[g][i]*signs[g][j] % 3
            relative.append(dict(group=g, positions=[i, j], relative_sign=sign,
                relative_phase_coefficients=form([(6*g+j, 1), (6*g+i, -sign)])))
        odd = [r for r in relative if r['relative_sign'] == 2]
        even = [r for r in relative if r['relative_sign'] == 1]
        linear.need(len(odd) in (0, 3), 'necessary parity count zero or three')
        for label, part in [('odd', odd), ('even', even)]:
            equation('pair_'+label+'_phase_sum', [(i, c) for r in part for i, c in enumerate(r['relative_phase_coefficients']) if c],
                     incident, coordinates=[a, b], groups=[r['group'] for r in part])
        pairs.append(dict(coordinates=[a, b], incident_groups=incident, relative_maps=relative))
    mixed = sum(any(p) for p in patterns)
    linear.need(len(rows) == 160+mixed and len(functionals) == 6*mixed and len(pairs) == 60, 'complete general populations')
    return dict(schema='GENERAL_BALANCED_GF3_PHASE_SYSTEM_V1', field=3, variables=variables, groups=groups,
        patterns=patterns, signs=signs, rows=rows, pair_records=pairs,
        necessary_nonzero_functionals=functionals, mixed_groups=mixed, constant_groups=20-mixed,
        one_fixed_parity_branch=True, Ycaps_encoded=False, residual_D_encoded=False,
        rejection_rule='First mixed-group same-sign difference contained in the equation row space; no pair inequalities used.')


def screen(system):
    matrix = [row['coefficients'] for row in system['rows']]
    certificate = linear.rref(matrix, 120)
    # Direct construction checks do not constitute independent verification.
    linear.need(all(linear.dot(row, vector) == 0 for row in matrix for vector in certificate['nullspace_basis']), 'producer nullspace products')
    obstruction = None
    attempted = 0
    for condition in system['necessary_nonzero_functionals']:
        attempted += 1
        if any(linear.dot(condition['coefficients'], v) for v in certificate['nullspace_basis']):
            continue
        remainder = condition['coefficients'][:]
        weights = [0]*len(matrix)
        for i, pivot in enumerate(certificate['pivots']):
            coefficient = remainder[pivot]
            if coefficient:
                remainder = [(x-coefficient*y) % 3 for x, y in zip(remainder, certificate['rref'][i], strict=True)]
                weights = [(x+coefficient*y) % 3 for x, y in zip(weights, certificate['row_transform'][i], strict=True)]
        linear.need(not any(remainder) and all(sum(weights[j]*matrix[j][i] for j in range(len(matrix))) % 3 == condition['coefficients'][i] for i in range(120)), 'literal producer row-space certificate')
        obstruction = dict(condition=condition, row_combination=weights,
            identity='row_combination times all ordered equation rows equals the required-nonzero functional in GF(3)')
        break
    return dict(schema='GENERAL_BALANCED_GF3_PHASE_SCREEN_V1', status='CANDIDATE_PHASE_OBSTRUCTION' if obstruction else 'UNKNOWN_LINEAR_SCREEN',
        rank=certificate['rank'], nullity=certificate['nullity'], linear_certificate=certificate,
        obstruction=obstruction, functionals_attempted=attempted,
        complete_nonlinear_feasibility=False, independent_approval=False,
        mathematical_nogood_generated=False, shortened_nogood_generated=False)
