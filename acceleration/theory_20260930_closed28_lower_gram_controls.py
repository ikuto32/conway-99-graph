"""Exact producer controls for a candidate lower-Gram redundancy derivation."""
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def calculate(A,centers):
    need(len(A) == 28 and all(len(row) == 28 and all(type(x) is int and x in (0,1) for x in row) for row in A),'binary28')
    need(all(A[i][i] == 0 for i in range(28)) and all(A[i][j] == A[j][i] for i in range(28) for j in range(28)),'simple symmetric')
    v,u = centers
    need(v != u and A[v][u] == 0 and sum(A[v]) == sum(A[u]) == 14,'nonadjacent degree14centers')
    need(all(sum(A[a][k]*A[x][k] for k in range(28)) == 2-A[a][x] for a in centers for x in range(28) if x != a),'exact center equalities')
    R = [i for i in range(28) if i not in centers]
    n,m = [A[v][i] for i in R],[A[u][i] for i in R]
    t,d = [x+y for x,y in zip(n,m)],[x-y for x,y in zip(n,m)]
    c = [x-1 for x in t]
    need(all(x in (1,2) for x in t) and sum(c) == 2,'closed union and common neighbors')
    B = [[A[i][j] for j in R] for i in R]
    need(max(map(sum,B)) <= 3,'remaining degree bound')
    M = [[B[i][j]+4*int(i==j) for j in range(26)] for i in range(26)]
    need(all(sum(M[i][j]*t[j] for j in range(26)) == 7*t[i]-4*c[i] for i in range(26)),'Mt exact identity')
    need(all(sum(M[i][j]*d[j] for j in range(26)) == 3*d[i] for i in range(26)),'Md exact identity')
    need(sum(x*x for x in t) == 32 and sum(x*x for x in c) == 2 and sum(x*y for x,y in zip(c,t)) == 4,'exact scalar constants')
    kernel = [0]*28;kernel[v]=-3;kernel[u]=3
    for i,x in zip(R,d):kernel[i]=x
    need(all(sum((A[i][j]+4*int(i==j))*kernel[j] for j in range(28)) == 0 for i in range(28)),'exact claimed kernel')
    return M,t,c


def solve(M,rhs):
    matrix = [[Fraction(x) for x in row]+[Fraction(y)] for row,y in zip(M,rhs)]
    n=len(M)
    for col in range(n):
        pivot=next(i for i in range(col,n) if matrix[i][col])
        matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
        factor=matrix[col][col];matrix[col]=[x/factor for x in matrix[col]]
        for row in range(n):
            if row != col and matrix[row][col]:
                factor=matrix[row][col];matrix[row]=[a-factor*b for a,b in zip(matrix[row],matrix[col])]
    return [row[-1] for row in matrix]


def main():
    out=ROOT/'acceleration/results/20260930_closed28_lower_gram_derivation'
    out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'acceleration/results/20260930_closed28_sos/center_00.json'
    cases=json.loads(source.read_bytes())['cases']
    first=cases[0];A=[[int(int(row,16)>>j&1) for j in range(28)] for row in first['adjacency_rows_hex']]
    M,t,c=calculate(A,first['centers_local'])
    bad=[row.copy() for row in A];v=first['centers_local'][0];w=next(i for i in range(28) if bad[v][i])
    bad[v][w]=bad[w][v]=0
    try:calculate(bad,first['centers_local'])
    except ValueError:corruption_rejected=True
    else:raise ValueError('corrupted center edge accepted')
    exact=[]
    for case in cases[:4]:
        A=[[int(int(row,16)>>j&1) for j in range(28)] for row in case['adjacency_rows_hex']]
        M,t,c=calculate(A,case['centers_local'])
        inverse_c,inverse_t=solve(M,c),solve(M,t)
        r=sum(x*y for x,y in zip(c,inverse_c));q=sum(x*y for x,y in zip(t,inverse_t))
        need(q == (240+16*r)/49 and r <= 2 and q <= Fraction(272,49),'exact inverse identity/bound')
        need(q != (240+15*r)/49,'wrong coefficient control')
        exact.append(dict(original_id=case['original_id'],r=str(r),t_inverse_t=str(q),sum_schur_eigenvalue=str(4-q/2)))
    for case in cases:
        A=[[int(int(row,16)>>j&1) for j in range(28)] for row in case['adjacency_rows_hex']]
        calculate(A,case['centers_local'])
    paths=[Path(__file__),Path(__file__).with_name('theory_20260930_closed28_lower_gram_redundancy.md'),source,ROOT/'uv.lock',
           ROOT/'acceleration/results/20260930_independent_review/local_redundancy_v2/closed_gram_lemma.json']
    report=dict(status='CANDIDATE_DERIVATION_PENDING_INDEPENDENT_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
                statement='Under the recorded closed nonadjacent degree14two-center equalities, A(H)+4I is PSD with rank27 and the displayed one-dimensional kernel; no extra all-pair caps are required.',
                inputs_sha256={key(p):digest(p) for p in paths},exact_raw_identity_cases=len(cases),exact_fraction_inverse_cases=exact,
                controls=dict(known_raw_positive_fixture_accepted=True,deleted_center_edge_rejected=corruption_rejected,wrong_r_coefficient_rejected=True),
                bounds=dict(t_inverse_t_maximum='272/49',nonzero_schur_eigenvalue_minimum='60/49'),
                independent_review=None,independent_review_null_reason='This is discovery-agent mathematical derivation and producer calibration only; separate review is required',
                limitations=['Only32raw examples and4fractional inverses were calibrated, not all2688graphs.',
                             'The proposed universal proof is the written algebra, not finite-example agreement.','No target existence, nonexistence, extendability, or external review.'],
                target_resolution=False)
    path=out/'summary.json'
    with path.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(path),exact_inverse_cases=exact)))


if __name__=='__main__':main()
