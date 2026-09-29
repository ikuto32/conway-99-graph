"""Independent raw integer check; no discovery/elimination code imported."""
from datetime import datetime, timezone
from hashlib import sha256
import copy
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GRAPH = 'acceleration/results/20260930_rook_free_internal_independent_certificate/independent_full59.json'
CERT = 'acceleration/results/20260930_rook_free_internal_gram/result.json'
OUT = 'acceleration/results/20260930_independent_review/rook_original_gram.json'


def h(path):
    return sha256((ROOT / path).read_bytes()).hexdigest()


def check(a, v, expected):
    n = len(a)
    assert n and len(v) == n and all(type(x) is int for x in v)
    assert type(expected) is int
    assert all(len(row) == n for row in a)
    assert all(type(a[i][j]) is int and a[i][j] in (0, 1)
               and a[i][j] == a[j][i] and (i != j or a[i][j] == 0)
               for i in range(n) for j in range(n))
    direct = sum(v[i] * v[j] * (27 * (i == j) - 9 * a[i][j] + 1)
                 for i in range(n) for j in range(n))
    edgewise = 27 * sum(x*x for x in v) + sum(v)**2 - 18 * sum(
        v[i]*v[j] for i in range(n) for j in range(i+1, n) if a[i][j])
    assert direct == edgewise == expected and direct < 0
    return direct


def polynomial_identity():
    # Independent exact multiplication in basis I,A,J, using A^2=12I-A+2J,
    # AJ=JA=14J and J^2=99J. Degree 14 follows from the diagonal identity.
    table = [[(1,0,0),(0,1,0),(0,0,1)],
             [(0,1,0),(12,-1,2),(0,0,14)],
             [(0,0,1),(0,0,14),(0,0,99)]]
    g = (27,-9,1)
    square = [sum(g[i]*g[j]*table[i][j][k] for i in range(3)
                  for j in range(3)) for k in range(3)]
    assert square == [63*x for x in g]
    return square


def main():
    a = json.loads((ROOT / GRAPH).read_bytes())['adjacency_full59']
    c = json.loads((ROOT / CERT).read_bytes())
    test = next(t for t in c['tests'] if t['matrix'] == '27I-9A+J')['result']
    v, q = test['integer_negative_vector'], test['quadratic_value']
    assert len(a) == 59
    result = check(a, v, q)
    assert test['support'] == [i for i, x in enumerate(v) if x]
    square = polynomial_identity()
    controls = []
    # K5 has a deliberately negative all-ones Gram direction: eigenvalue -4.
    k5 = [[int(i != j) for j in range(5)] for i in range(5)]
    assert check(k5, [1]*5, -20) == -20
    controls.append({'case': 'known_negative_K5_direction', 'outcome': 'ACCEPTED'})
    rook9 = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    bad_graph = copy.deepcopy(a); bad_graph[0][1] ^= 1
    bad_cases = [('wrong_quadratic_value', a, v, q-1),
                 ('truncated_vector', a, v[:-1], q),
                 ('zero_direction', a, [0]*59, q),
                 ('asymmetric_graph', bad_graph, v, q),
                 ('PSD_rook9_constant_direction', rook9, [1]*9, -1),
                 ('PSD_rook9_difference_direction', rook9, [1,-1]+[0]*7, -1)]
    for name, aa, vv, qq in bad_cases:
        try:
            check(aa, vv, qq)
        except AssertionError:
            controls.append({'case': name, 'outcome': 'REJECTED'})
        else:
            raise AssertionError(name)
    out = dict(status='INDEPENDENT_RAW59_NEGATIVE_GRAM_PASS', recommendation='VERIFIED',
               timestamp=datetime.now(timezone.utc).isoformat(),
               source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
               command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),
               verifier='/root independent raw-matrix checking path',
               method='Literal integer double sum and separate undirected edge sum; no producer imports',
               inputs_sha256={p:h(p) for p in [GRAPH,CERT,Path(__file__).relative_to(ROOT).as_posix(),'uv.lock']},
               claim_id='C-ROOK-LOCAL59-NEGATIVE-GRAM-EXCLUSION',claim_revision=1,
               statement='The exact labelled 59-vertex graph bound by this report cannot be an induced subgraph of any srg(99,14,1,2).',
               scope='One exact induced graph; no other local witness, rook-containing graph, or unrestricted target is excluded.',
               quadratic_value=result,support_size=sum(bool(x) for x in v),matrix='27I-9A+J',
               polynomial_square_coefficients_I_A_J=square,
               mathematical_derivation='The target diagonal gives degree 14, hence AJ=JA=14J. With J^2=99J, exact expansion gives G^2=63G. Symmetry implies 63*x^T*G*x=||G*x||^2>=0. Restriction to any induced principal submatrix is PSD. The displayed negative integer direction contradicts that necessity for this one graph.',
               rank_derivation='trace(G)=99*28=2772 and G^2=63G imply rank(G)=2772/63=44; rank is not used for this exclusion.',
               controls=controls,
               shared_components=['Python integer arithmetic and standard library; input raw graph produced by a separate independent SAT decoder'],
               limitations=['No claim about the second A+4I producer certificate.', 'No graph automorphism or universal induced-rook assumption.', 'Internal review only; no external peer review.', 'The local SAT construction remains valid for its weaker constraints.'])
    with (ROOT/OUT).open('x',encoding='utf-8') as f:
        json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({'status':out['status'],'quadratic_value':result,'audit_sha256':h(OUT)}))


if __name__ == '__main__':
    main()
