"""Clean arithmetic replay; no producer imports, solver, or numeric eigenvalues."""
from fractions import Fraction as R
from itertools import combinations
from pathlib import Path
import hashlib
import json


def mul(left, right):
    result = [[R(0) for _ in right[0]] for _ in left]
    for i, row in enumerate(left):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(right[k]):
                    result[i][j] += value*other
    return result


def transpose(matrix):
    return list(map(list, zip(*matrix)))


def psd_rank(matrix):
    # Exact symmetric Schur elimination. Every nonzero pivot must be positive;
    # a remaining zero diagonal must have an entirely zero row/column.
    a = [[R(x) for x in row] for row in matrix]
    rank = 0
    while a:
        pivot = next((i for i in range(len(a)) if a[i][i] != 0), None)
        if pivot is None:
            assert all(x == 0 for row in a for x in row)
            return rank
        assert a[pivot][pivot] > 0
        indices = [i for i in range(len(a)) if i != pivot]
        a = [[a[i][j]-a[i][pivot]*a[pivot][j]/a[pivot][pivot] for j in indices] for i in indices]
        rank += 1
    return rank


def main():
    path = Path('scratch_next_degree_covariance_control.json')
    parent = Path('scratch_resume_integral_compression.json')
    cert = json.loads(path.read_text())
    data = json.loads(parent.read_text())
    assert cert['input_sha256'] == hashlib.sha256(parent.read_bytes()).hexdigest()
    c = data['C']
    supports = list(combinations(range(7), 2))
    assert list(map(tuple, data['supports'])) == supports
    ell = [[int(g in support) for g in range(7)] for support in supports]
    inv = [[R(int(i == j), 5)-R(1, 60) for j in range(7)] for i in range(7)]
    h = mul(mul(ell, inv), transpose(ell))
    pi = [[R(int(i == j))-h[i][j] for j in range(21)] for i in range(21)]
    assert mul(pi, pi) == pi
    assert sum(pi[i][i] for i in range(21)) == 14
    fixed = [[R(8, 3)-8*h[i][j] for j in range(21)] for i in range(21)]
    t = [[R(c[i][j])-fixed[i][j] for j in range(21)] for i in range(21)]
    t2 = mul(t, t)
    assert transpose(c) == c and all(c[i][i] == 0 for i in range(21))
    assert mul(c, ell) == [[16-8*v for v in row] for row in ell]
    assert mul(t, pi) == t
    assert all(sum(x*x for x in c[i]) == 132 for i in range(21))
    assert all(t2[i][i] == 4 for i in range(21))
    assert sum(t2[i][i] for i in range(21)) == 84 < 100
    delta = [[R(3, 2)*pi[i][j]-t[i][j]-t2[i][j]/4 for j in range(21)] for i in range(21)]
    assert all(delta[i][i] == 0 for i in range(21))
    for name, expected in [('Pi', pi), ('T', t), ('Delta', delta)]:
        assert [[R(x) for x in row] for row in cert[name]] == expected
    assert mul(delta, pi) == delta
    total = [[R(0) for _ in range(21)] for _ in range(21)]
    raw_total = [[R(0) for _ in range(21)] for _ in range(21)]
    records = []
    for fi, entry in enumerate(cert['covariances']):
        assert entry['source'] == fi
        sig = [[R(x) for x in row] for row in entry['Sigma']]
        assert transpose(sig) == sig and all(x == 0 for x in sig[fi])
        u = [pi[i][fi] for i in range(21)]
        q = [[pi[i][j]-R(3, 2)*u[i]*u[j] for j in range(21)] for i in range(21)]
        assert mul(q, q) == q and sum(q[i][i] for i in range(21)) == 13
        qdq = mul(mul(q, delta), q)
        assert sig == [[R(31, 13)*q[i][j]+qdq[i][j]/18 for j in range(21)] for i in range(21)]
        assert mul(sig, ell) == [[0]*7 for _ in range(21)]
        assert mul(sig, q) == sig
        assert sum(sig[i][i] for i in range(21)) == 31
        rank = psd_rank(sig)
        assert rank == 13
        assert psd_rank([[sig[i][j]-R(349, 468)*q[i][j] for j in range(21)] for i in range(21)]) == 13
        for i in range(21):
            for j in range(21):
                total[i][j] += sig[i][j]
                raw_total[i][j] += sig[i][j]+R(c[fi][i]*c[fi][j], 4)
        assert sum(R(x*x, 4) for x in c[fi])+31 == 64
        # Independently confirm the companion strict Schur bound on each
        # already audited concrete degree quartet (these are separate lifts).
        witness = json.loads(Path(f'scratch_resume_uniform_fibre_incidence_f{fi}_q16.json').read_text())
        ds = witness['degree_rows']
        assert [sum(row[j] for row in ds) for j in range(21)] == c[fi]
        assert all(sum(x*x for x in row) == 16 for row in ds)
        dd = mul(ds, transpose(ds))
        k = [[12 if i == j else 2 if (i ^ j) == 3 else 1 for j in range(4)] for i in range(4)]
        assert psd_rank([[4*k[i][j]-dd[i][j]-7*int(i == j) for j in range(4)] for i in range(4)]) == 4
        targets = [(a, b, s, t) for a, b in supports if (a, b) != supports[fi]
                   for s in range(2) for t in range(2)]
        signs = [[(1 if (a == group and s == 0) or (b == group and t == 0) else
                   -1 if (a == group and s == 1) or (b == group and t == 1) else 0)
                  for a, b, s, t in targets] for group in range(7)]
        sign_gram = mul(signs, transpose(signs))
        assert sign_gram == [[(20 if a in supports[fi] else 24) if a == b else 0
                             for b in range(7)] for a in range(7)]
        assert all(sum(row[k] for k, target in enumerate(targets) if target[:2] == support) == 0
                   for row in signs for support in supports if support != supports[fi])
        records.append({'source': fi, 'covariance_rank': rank, 'trace': 31,
                        'strict_lower_bound_audited': '349/468 * Q_F',
                        'concrete_quartet_Schur_minus_7I_rank': 4,
                        'real_incidence_residual_space_dimension': 80-20-7})
    gram = [[48*int(i == j)+32-c[i][j]-8*len(set(supports[i]) & set(supports[j]))
             for j in range(21)] for i in range(21)]
    assert raw_total == gram
    assert total == [[R(x) for x in row] for row in cert['sum_covariance']]
    assert sum(total[i][i] for i in range(21)) == 651
    assert R(1, 25)+R(31, 33) == R(808, 825) < 1
    report = {'status': 'INDEPENDENT_EXACT_CONDITIONAL_COVARIANCE_CONTROL_AUDIT_PASS',
              'certificate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'input_sha256': hashlib.sha256(parent.read_bytes()).hexdigest(),
              'all_global_Gram_entries_checked': 441,
              'source_covariance_count': 21, 'source_covariance_trace': 31,
              'total_covariance_trace': 651, 'source_covariance_rank': 13,
              'actual_four_row_centered_covariance_rank_limit': 3,
              'records': records,
              'solver_used': False, 'producer_imported': False,
              'scope': 'Exact rational PSD moment control and Schur-slack lemma only. No integral D, bounded row realization, simultaneous binary fibre lift, adjacency B, positive E0 bound, or Conway resolution.'}
    Path('scratch_next_degree_covariance_control_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'records'}, indent=2))


if __name__ == '__main__':
    main()
