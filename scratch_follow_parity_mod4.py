"""One exact linear carry check for the explicit parity D; no graph solver."""
from itertools import combinations
from pathlib import Path
import hashlib
import json


def main():
    source = Path('scratch_follow_parity.json')
    data = json.loads(source.read_bytes())
    cp = Path('scratch_resume_integral_compression.json')
    c = json.loads(cp.read_bytes())['C']
    supports = list(combinations(range(7), 2))
    d = [[(row >> f) & 1 for f in range(21)] for row in data['D_mod2_rows']]
    variables = 84*21
    equations = []
    def add(indices, rhs, kind, coordinate):
        bits = 0
        for x, f in indices:
            bits ^= 1 << (21*x+f)
        equations.append({'bits': bits, 'rhs': rhs%2, 'kind': kind, 'coordinate': coordinate})
    for s in range(21):
        for f in range(21):
            delta = c[s][f]-sum(d[x][f] for x in range(4*s, 4*s+4))
            assert delta%2 == 0
            add([(x, f) for x in range(4*s, 4*s+4)], delta//2, 'source_sum', [s, f])
    for a, b in combinations(range(21), 2):
        gram = sum(row[a]*row[b] for row in d)
        target = 32-c[a][b]-8*len(set(supports[a]) & set(supports[b]))
        assert (target-gram)%2 == 0
        indices = [(x, b) for x in range(84) if d[x][a]]+[(x, a) for x in range(84) if d[x][b]]
        add(indices, (target-gram)//2, 'gram', [a, b])
    for x in range(84):
        for group in range(7):
            target = 2 if group in supports[x//4] else 4
            value = sum(d[x][f] for f in range(21) if group in supports[f])
            assert (target-value)%2 == 0
            add([(x, f) for f in range(21) if group in supports[f]], (target-value)//2, 'group_quota', [x, group])
        add([(x, f) for f in range(21)], (12-sum(d[x]))//2, 'row_sum', [x])
        add([(x, x//4)], 0, 'own_zero', [x])
    for f in range(21):
        add([(x, f) for x in range(84)], (48-sum(d[x][f] for x in range(84)))//2, 'column_sum', [f])
    pivots = {}
    conflict = None
    for i, equation in enumerate(equations):
        bits, rhs, proof = equation['bits'], equation['rhs'], 1 << i
        while bits:
            pivot = bits.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = (bits, rhs, proof)
                break
            old, oldrhs, oldproof = pivots[pivot]
            bits ^= old
            rhs ^= oldrhs
            proof ^= oldproof
        if not bits and rhs:
            conflict = [j for j in range(len(equations)) if (proof >> j) & 1]
            break
    report = {'status': 'MOD4_CARRY_LINEAR_SYSTEM_FEASIBLE' if conflict is None else 'THIS_PARITY_CONTROL_HAS_NO_MOD4_CARRY_LIFT',
              'parity_input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'variables': variables, 'equations': len(equations), 'coefficient_rank_reached': len(pivots),
              'scope': 'One prescribed parity D and its linear mod4 carry system. Failure is not a C or E0 exclusion; a feasible lift is residue data only, not integer degree12 rows or a graph.'}
    if conflict is not None:
        bits = rhs = 0
        for index in conflict:
            bits ^= equations[index]['bits']
            rhs ^= equations[index]['rhs']
        assert bits == 0 and rhs == 1
        report['conflict_equations'] = [{key: value for key, value in equations[i].items() if key != 'bits'} | {'index': i} for i in conflict]
    else:
        assignment = 0
        for pivot in sorted(pivots):
            bits, rhs, _ = pivots[pivot]
            if ((bits & assignment).bit_count()%2) ^ rhs:
                assignment |= 1 << pivot
        assert all((eq['bits'] & assignment).bit_count()%2 == eq['rhs'] for eq in equations)
        lift = [[d[x][f]+2*((assignment >> (21*x+f)) & 1) for f in range(21)] for x in range(84)]
        report['D_mod4'] = lift
    Path('scratch_follow_parity_mod4.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('D_mod4', 'conflict_equations')}, indent=2))


if __name__ == '__main__':
    main()
