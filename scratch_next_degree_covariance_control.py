"""Exact rational conditional covariance control for any sharp E0=0 C.

This is a PSD moment control, not an integer D or an adjacency matrix.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import hashlib
import json


def product(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in columns] for row in a]


def encode(a):
    return [[str(x) for x in row] for row in a]


def main():
    inp = Path('scratch_resume_integral_compression.json')
    data = json.loads(inp.read_text())
    supports = list(combinations(range(7), 2))
    assert list(map(tuple, data['supports'])) == supports
    c = data['C']
    intersection = [[len(set(a) & set(b)) for b in supports] for a in supports]
    pi = [[F(2, 3) if a == b else F(-2, 15) if intersection[a][b] else F(1, 15)
           for b in range(21)] for a in range(21)]
    cbar = [[F(0) if a == b else F(8, 5) if intersection[a][b] else F(16, 5)
             for b in range(21)] for a in range(21)]
    t = [[F(c[a][b])-cbar[a][b] for b in range(21)] for a in range(21)]
    t2 = product(t, t)
    assert product(pi, pi) == pi and product(t, pi) == t
    assert all(t[a][a] == 0 and t2[a][a] == 4 for a in range(21))
    assert sum(t2[a][a] for a in range(21)) == 84
    delta = [[F(3, 2)*pi[a][b]-t[a][b]-t2[a][b]/4 for b in range(21)] for a in range(21)]
    assert all(delta[a][a] == 0 for a in range(21))
    assert product(delta, pi) == delta
    covariances = []
    q_sum = [[F(0) for _ in range(21)] for _ in range(21)]
    sig_sum = [[F(0) for _ in range(21)] for _ in range(21)]
    for source in range(21):
        u = [pi[a][source] for a in range(21)]
        du = [delta[a][source] for a in range(21)]
        q = [[pi[a][b]-F(3, 2)*u[a]*u[b] for b in range(21)] for a in range(21)]
        sig = [[F(31, 13)*q[a][b]+delta[a][b]/18-(u[a]*du[b]+du[a]*u[b])/12
                for b in range(21)] for a in range(21)]
        assert all(x == 0 for x in sig[source])
        assert sum(sig[a][a] for a in range(21)) == 31
        assert all(sum(sig[a][b] for b in range(21) if g in supports[b]) == 0
                   for a in range(21) for g in range(7))
        for a in range(21):
            for b in range(21):
                q_sum[a][b] += q[a][b]
                sig_sum[a][b] += sig[a][b]
        covariances.append({'source': source, 'Sigma': encode(sig)})
    c2 = product(c, c)
    g = [[48*int(a == b)+32-c[a][b]-8*intersection[a][b] for b in range(21)] for a in range(21)]
    target = [[F(g[a][b])-F(c2[a][b], 4) for b in range(21)] for a in range(21)]
    assert sig_sum == target
    assert q_sum == [[F(39, 2)*value for value in row] for row in pi]
    lower = F(31, 13)-F(59, 36)
    assert lower == F(349, 468) > 0
    result = {'status': 'EXACT_SHARP_COMPRESSION_CONDITIONAL_PSD_COVARIANCE_CONTROL',
              'input_sha256': hashlib.sha256(inp.read_bytes()).hexdigest(),
              'Pi': encode(pi), 'T': encode(t), 'Delta': encode(delta),
              'covariances': covariances, 'sum_covariance': encode(sig_sum),
              'covariance_rank_per_source': 13, 'covariance_trace_per_source': 31,
              'strict_PSD_lower_coefficient_on_Q': str(lower),
              'source_raw_second_moment_trace': 64,
              'scope': 'Rational PSD conditional moments only. Actual four-row centered covariance has rank at most3, and actual rows are bounded nonnegative integers. Neither such rows nor adjacency reciprocity are supplied.'}
    Path('scratch_next_degree_covariance_control.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('Pi', 'T', 'Delta', 'covariances', 'sum_covariance')}, indent=2))


if __name__ == '__main__':
    main()
