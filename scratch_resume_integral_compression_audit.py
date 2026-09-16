"""Independent, solver-free exact audit of an endpoint compression.

Only reads emitted C, reconstructs the algebra, and uses rational arithmetic.
No discovery/solver modules are imported.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, column))
             for column in zip(*b)] for row in a]


def trans(a):
    return list(map(list, zip(*a)))


def main():
    path = Path('scratch_resume_integral_compression.json')
    raw = path.read_bytes()
    data = json.loads(raw)
    supports = list(combinations(range(7), 2))
    assert data['supports'] == [list(s) for s in supports]
    c = data['C']
    assert len(c) == 21 and all(len(row) == 21 for row in c)
    assert all(type(x) is int for row in c for x in row)
    ell = [[int(g in support) for g in range(7)] for support in supports]
    for i in range(21):
        assert c[i][i] == 0 and sum(c[i]) == 48
        for j in range(21):
            assert c[i][j] == c[j][i]
            if i != j:
                assert c[i][j] in ((1, 2) if set(supports[i]) & set(supports[j]) else (3, 4))
    cl = mul(c, ell)
    assert cl == [[16-8*value for value in row] for row in ell]
    c2 = mul(c, c)
    trc2 = sum(c2[i][i] for i in range(21))
    assert trc2 == 2772
    # L^T L = 5I+J, inverse (I-J/12)/5.
    lt = trans(ell)
    assert mul(lt, ell) == [[5*int(i == j)+1 for j in range(7)] for i in range(7)]
    h = mul(mul(ell, [[Q(int(i == j), 5)-Q(1, 60) for j in range(7)]
                      for i in range(7)]), lt)
    pi = [[int(i == j)-h[i][j] for j in range(21)] for i in range(21)]
    cbar = [[Q(8, 3)-8*h[i][j] for j in range(21)] for i in range(21)]
    delta = [[c[i][j]-cbar[i][j] for j in range(21)] for i in range(21)]
    zero = [[0]*7 for _ in range(21)]
    assert mul(delta, ell) == zero
    assert mul(pi, delta) == delta and mul(delta, pi) == delta
    assert sum(delta[i][i] for i in range(21)) == 0
    assert sum(x*x for row in delta for x in row) == 84
    assert mul(h, h) == h and mul(pi, pi) == pi
    assert sum(h[i][i] for i in range(21)) == 7
    assert sum(pi[i][i] for i in range(21)) == 14
    # Every eigenvalue of real symmetric delta has square <= ||delta||_F^2.
    # Since 84<100, all cycle eigenvalues t obey -10<t<10.
    # This lies strictly in [-16,12]; 192-4t-t^2 > 52 on this range.
    assert 84 < 100 and 192-4*10-100 == 52
    llt = mul(ell, lt)
    g = [[48*int(i == j)+32-c[i][j]-8*llt[i][j]
          for j in range(21)] for i in range(21)]
    k4 = [[4*g[i][j]-c2[i][j] for j in range(21)] for i in range(21)]
    delta2 = mul(delta, delta)
    assert k4 == [[192*pi[i][j]-4*delta[i][j]-delta2[i][j]
                  for j in range(21)] for i in range(21)]
    assert mul(k4, ell) == zero
    trk4 = sum(k4[i][i] for i in range(21))
    assert trk4 == 2604
    result = {
        'status': 'INDEPENDENT_INTEGRAL_E0_ZERO_COMPRESSION_AUDIT_PASS',
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'matrix_size': 21, 'E0': 0, 'trace_C_squared': trc2,
        'cycle_trace': 0, 'cycle_square_trace': 84,
        'spectral_proof': '||C-Cbar||_F^2=84<100, hence -10<t<10 strictly inside [-16,12].',
        'K4_trace': trk4, 'K4_rank': 14,
        'K4_positive_eigenvalues_lower_bound_strict': 52,
        'scope': 'Simultaneous symmetric integral compression meets row identities, sharp rounding bound, and full compression PSD. No integral D or adjacency B asserted.'
    }
    Path('scratch_resume_integral_compression_audit.json').write_text(
        json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
