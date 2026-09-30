"""Independent proof and controls for the proposed individual-capacity redundancy."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
SOURCE = B+'independent_review/triangle_contraction/capacity_floor_candidate.json'
GATE = B+'independent_review/triangle_contraction/summary.json'
OUT = ROOT/(B+'independent_review/triangle_capacity_floor')


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def capacities(matrix):
    if len(matrix)!=36 or any(len(row)!=20 or any(type(x)!=int or x not in (0,1) for x in row) for row in matrix):
        raise ValueError('exact binary36x20 domain')
    if any(sum(row)!=10 for row in matrix) or any(sum(row[j] for row in matrix)!=18 for j in range(20)):
        raise ValueError('exact row10 column18 margins')
    values=[]
    for p in range(20):
        dots=[sum(row[p]*row[q] for row in matrix) for q in range(20) if q!=p]
        assert sum(dots)==162 and all(0<=x<=18 for x in dots)
        values.append(sum((18-x)//5 for x in dots))
    return values


def main():
    assert digest(GATE)=='5b190d159e2fc2b681dc52be1083d2f74f402c86f1305b7acdaf58435fcdc96a'
    candidate=json.loads((ROOT/SOURCE).read_bytes())
    assert candidate['status']=='CANDIDATE' and not candidate['independent_approval']
    OUT.mkdir(parents=True,exist_ok=False)
    now=datetime.now(timezone.utc).isoformat()
    proof='''For an arbitrary binary36x20 matrix T with row sum10 and column sum18, fix p.
The sum over q != p of T_p dot T_q equals sum_r T_rp*(10-T_rp)=18*9=162.
Each dot product is between0 and18. Set a_q=18-T_p dot T_q. There are19
nonnegative integer a_q with sum180. Euclidean division gives a_q=5b_q+r_q,
0<=r_q<=4, hence 5*sum b_q=180-sum r_q>=180-76=104.
The left side is a multiple of5, therefore it is at least105 and sum b_q>=21.
In particular the separate test sum capacities>=18 is always passed. This
does not exhibit a simultaneous symmetric bounded-degree matrix, a factor,
a residual graph or a Conway99 graph; no tightness over actual matrices is claimed.
'''
    (OUT/'independent_proof.txt').write_text(proof,encoding='utf-8',newline='\n')
    # Separate finite arithmetic check: dynamic optimization of every19-term
    # bounded integer sequence by total, without using the residue argument.
    dp={0:0}; layers=[dp]
    for _ in range(19):
        nxt={}
        for total,cost in dp.items():
            for number in range(19):
                s=total+number
                if s<=180:nxt[s]=min(nxt.get(s,10**9),cost+number//5)
        dp=nxt;layers.append(dp)
    assert dp[180]==21
    random_source=random.Random(20260930)
    controls=[]
    for case in range(256):
        matrix=[]
        for _ in range(18):
            selected=set(random_source.sample(range(20),10))
            row=[int(i in selected) for i in range(20)]
            matrix.extend([row,[1-x for x in row]])
        values=capacities(matrix);assert min(values)>=21
        controls.append(dict(matrix=matrix,row_capacity_sums=values))
    bad=[]
    template=controls[0]['matrix']
    tests=[template[:-1], [row[:-1] for row in template]]
    for column,value in [(0,2),(1,True),(2,1-template[0][2])]:
        matrix=[row[:] for row in template];matrix[0][column]=value;tests.append(matrix)
    # Keep row sum10 but corrupt the column margins.
    matrix=[row[:] for row in template];one=matrix[0].index(1);zero=matrix[0].index(0)
    matrix[0][one],matrix[0][zero]=0,1;tests.append(matrix)
    for i,matrix in enumerate(tests):
        try:capacities(matrix)
        except ValueError as error:bad.append(dict(case=i,error=str(error)))
        else:raise AssertionError('accepted corrupted margin fixture')
    outputs={'dynamic_program.json':dict(domain='19 integers each0..18, sum180',layers=layers,minimum_floor_sum=21),
        'positive_controls.json':controls,'corruptions.json':bad}
    for name,value in outputs.items():(OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    statement='For every binary36x20 matrix T with each row sum10 and each column sum18, each of the20 off-diagonal capacity sums sum_{q!=p} floor((18-T_p^T T_q)/5) is at least21; consequently each separate degree18 row-capacity test is redundant.'
    report=dict(status='INDEPENDENT_TRIANGLE_INDIVIDUAL_CAPACITY_REDUNDANCY_PASS',created_at=now,updated_at=now,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=sys.version,random_seed=20260930,
        inputs_sha256={p:digest(p) for p in [SOURCE,GATE,Path(__file__).resolve().relative_to(ROOT).as_posix(),'uv.lock']},
        outputs_sha256={p.relative_to(ROOT).as_posix():digest(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()},
        claim_id='C-TRIANGLE-CONTRACTION-INDIVIDUAL-CAPACITY-REDUNDANCY',claim_revision=1,
        statement=statement,kind='mathematical result',basis=['DERIVED'],recommendation='VERIFIED',review_state='CLEAR',
        scope='Every matrix with the stated binary dimensions and margins; application to the conditional residual-triangle capacities only.',
        dependencies=[dict(id='C-IDENTITY-P-RESIDUAL-TRIANGLE-CONTRACTION',revision=1,relation='uses_result')],
        assumptions=['No existence of a target completion or nontrivial automorphism is assumed.'],
        verifier='/root',method='independent_derivation',shared_components=['The producer candidate statement and previously independent contraction theorem are read; no producer calculation is imported.'],
        controls=dict(exact_arithmetic_DP_minimum=21,positive_matrices=256,checked_row_capacities=5120,corruptions_rejected=len(bad)),
        limitations=['The independent written proof, not the finite controls, establishes the universal result.',
            'No tightness over actual binary matrices is claimed; the broader integer-sequence domain has minimum21.',
            'Simultaneous symmetric degree feasibility and actual residual equations remain unresolved.'],
        artifact_availability='LOCAL_ONLY',target_resolution='UNKNOWN',external_review=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],sha256=digest((OUT/'summary.json').relative_to(ROOT)))))


if __name__=='__main__':main()
