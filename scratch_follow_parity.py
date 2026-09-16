"""Exact characteristic-two degree-Gram control, not integer degree rows."""
from itertools import combinations
from pathlib import Path
import hashlib
import json


def multiply_rows(a, b):
    result = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length()-1]
            row ^= bit
        result.append(value)
    return result


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            i = row.bit_length()-1
            if i in pivots:
                row ^= pivots[i]
            else:
                pivots[i] = row
                break
    return len(pivots)


def main():
    path = Path('scratch_resume_integral_compression.json')
    data = json.loads(path.read_bytes())
    supports = list(combinations(range(7), 2))
    c = [sum((value%2) << i for i, value in enumerate(row)) for row in data['C']]
    c2 = multiply_rows(c, c)
    target = [a ^ b for a, b in zip(c, c2)]
    remaining = target[:]
    wedges = []
    while any(remaining):
        options = []
        for i, j in combinations(range(21), 2):
            if (remaining[i] >> j) & 1:
                a, b = remaining[i], remaining[j]
                zeros = [f for f in range(21) if not ((a | b) >> f) & 1]
                options.append((len(zeros), -i, -j, a, b, zeros))
        assert options
        _, ni, nj, a, b, zeros = max(options)
        assert zeros, 'This decomposition failed; it is not a parity obstruction.'
        before = rank(remaining)
        for i in range(21):
            if (a >> i) & 1:
                remaining[i] ^= b
            if (b >> i) & 1:
                remaining[i] ^= a
        assert rank(remaining) == before-2
        wedges.append({'pivot': [-ni, -nj], 'a': a, 'b': b, 'eligible_sources': zeros})
    assigned = {}
    def match(i, seen):
        for source in wedges[i]['eligible_sources']:
            if source in seen:
                continue
            seen.add(source)
            if source not in assigned or match(assigned[source], seen):
                assigned[source] = i
                return True
        return False
    for i in range(len(wedges)):
        assert match(i, set()), 'Source assignment failed; no parity exclusion follows.'
    # The repeated C rows add zero to the Gram in characteristic two and
    # provide a less sparse control than (0,0,0,C_F).
    d = []
    for source in range(21):
        if source in assigned:
            wedge = wedges[assigned[source]]
            a, b = wedge['a'], wedge['b']
            wedge['source'] = source
            quartet = [a, b, a ^ b, c[source]]
        else:
            quartet = [c[source], c[source], 0, c[source]]
        d.extend(quartet)
    before_correction = d[:]
    column_weights = [sum((row >> f) & 1 for row in d) for f in range(21)]
    assert all(weight%2 == 0 for weight in column_weights)
    h = sum(((weight//2)%2) << f for f, weight in enumerate(column_weights))
    eligible = [f for f in range(21) if not ((h >> f) & 1) and d[4*f] == d[4*f+1]]
    assert eligible
    correction_source = min(eligible, key=lambda f: ((d[4*f] ^ h).bit_count(), f))
    d[4*correction_source] ^= h
    d[4*correction_source+1] ^= h
    assert all(sum((row >> f) & 1 for row in d)%4 == 0 for f in range(21))
    cp = [d[4*f] ^ d[4*f+1] ^ d[4*f+2] ^ d[4*f+3] for f in range(21)]
    gram = [sum((sum(((row >> a) & 1)*((row >> b) & 1) for row in d)%2) << b for b in range(21)) for a in range(21)]
    assert cp == c and gram == c
    ell = [sum((1 << i) for i, support in enumerate(supports) if g in support) for g in range(7)]
    assert all(row.bit_count()%2 == 0 for row in d)
    assert all((row & column).bit_count()%2 == 0 for row in d for column in ell)
    assert all(not ((row >> (x//4)) & 1) for x, row in enumerate(d))
    j = (1 << 21)-1
    kg = [sum((1 << i) for i, other in enumerate(supports) if set(support).isdisjoint(other)) for support in supports]
    assert multiply_rows(kg, kg) == kg and rank(kg) == 14
    assert multiply_rows(c, kg) == c
    report = {'status': 'EXACT_PARITY_DEGREE_GRAM_CONTROL',
              'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'supports': supports, 'C_mod2_rows': c, 'A_CplusCsquare_rows': target,
              'wedges': wedges, 'D_mod2_rows': d,
              'quadratic_correction': {'row_addend': h, 'source': correction_source,
                                       'corrected_rows': [4*correction_source, 4*correction_source+1],
                                       'uncorrected_D_rank': rank(before_correction),
                                       'uncorrected_column_weights': column_weights},
              'column_weights': [sum((row >> f) & 1 for row in d) for f in range(21)],
              'ranks': {'C_mod2': rank(c), 'CplusCsquare_mod2': rank(target), 'D_mod2': rank(d),
                        'even_cycle_space': rank(kg)},
              'row_weight_histogram': {str(w): sum(row.bit_count() == w for row in d) for w in sorted({row.bit_count() for row in d})},
              'row_weights_above_integer_degree12': [x for x, row in enumerate(d) if row.bit_count() > 12],
              'scope': 'Binary residues of D only, satisfying all stated mod2 linear/Gram/own-zero conditions. Not integer degree12 rows, no q16 restriction, no binary adjacency B, and no E0 bound.'}
    Path('scratch_follow_parity.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('supports', 'C_mod2_rows', 'A_CplusCsquare_rows', 'wedges', 'D_mod2_rows')}, indent=2))


if __name__ == '__main__':
    main()
