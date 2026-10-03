"""Independent written proof review and exact raw controls for the lower Gram lemma."""
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'acceleration/results/20260930_independent_review/closed28_lower_lemma'

def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()

def solve(a, b):
    rows = [[F(x) for x in row] + [F(v)] for row,v in zip(a,b)]
    n = len(a)
    for i in range(n):
        k = next(k for k in range(i,n) if rows[k][i])
        rows[i], rows[k] = rows[k], rows[i]
        pivot = rows[i][i]
        rows[i] = [x/pivot for x in rows[i]]
        for k in range(n):
            if k != i:
                f = rows[k][i]
                rows[k] = [x-f*y for x,y in zip(rows[k],rows[i])]
    return [r[-1] for r in rows]

def check(case, inverse=False):
    rows = [int(x,16) for x in case['adjacency_rows_hex']]
    assert len(rows)==28 and all(0<=x<2**28 for x in rows)
    a = [[(rows[i]>>j)&1 for j in range(28)] for i in range(28)]
    assert all(a[i][i]==0 for i in range(28))
    assert all(a[i][j]==a[j][i] for i in range(28) for j in range(28))
    v,u=case['centers_local']; assert v!=u and a[v][u]==0
    for center in (v,u):
        assert sum(a[center])==14
        assert all(sum(a[center][k]*a[x][k] for k in range(28))==2-a[center][x] for x in range(28) if x!=center)
    r=[x for x in range(28) if x not in (v,u)]
    n=[a[v][i] for i in r]; m=[a[u][i] for i in r]
    t=[x+y for x,y in zip(n,m)]; c=[x-1 for x in t]; d=[x-y for x,y in zip(n,m)]
    assert all(x in (1,2) for x in t)
    assert sum(x*x for x in t)==32 and sum(x*x for x in c)==2
    assert sum(x*y for x,y in zip(t,c))==4
    b=[[a[i][j] for j in r] for i in r]
    assert all(sum(row)<=3 for row in b)
    M=[[b[i][j]+4*(i==j) for j in range(26)] for i in range(26)]
    assert all(sum(M[i][j]*t[j] for j in range(26))==7*t[i]-4*c[i] for i in range(26))
    assert all(sum(M[i][j]*d[j] for j in range(26))==3*d[i] for i in range(26))
    kernel=[a[v][i]-a[u][i]-3*(i==v)+3*(i==u) for i in range(28)]
    assert any(kernel) and all(sum((a[i][j]+4*(i==j))*kernel[j] for j in range(28))==0 for i in range(28))
    # Exact coefficient identity M-I = signless Laplacian + diag(3-degree).
    assert all(M[i][j]-(i==j)==(sum(b[i]) if i==j else b[i][j])+(3-sum(b[i]))*(i==j) for i in range(26) for j in range(26))
    if not inverse: return None
    invc=solve(M,c); invt=solve(M,t)
    rr=sum(x*y for x,y in zip(c,invc)); tt=sum(x*y for x,y in zip(t,invt))
    assert 0<rr<=2 and tt==(240+16*rr)/49 and 4-tt/2>=F(60,49)
    assert tt!=(239+16*rr)/49  # deliberately corrupted numerator
    return {'r':str(rr),'t_inverse_t':str(tt),'positive_schur_eigenvalue':str(4-tt/2)}

def main():
    OUT.mkdir(exist_ok=False)
    proof=ROOT/'acceleration/theory_20260930_closed28_lower_gram_redundancy.md'
    assert digest(proof)=='2b998ef3fbdc32c4b53ddf705f36ad65c46b8645ef5773c0dca6bf1673f5acd6'
    inputs=[proof,Path(__file__),ROOT/'uv.lock']; count=0; exact=[]; first=None
    for p in sorted((ROOT/'acceleration/results/20260930_closed28_sos').glob('center_*.json')):
        inputs.append(p)
        for case in json.loads(p.read_bytes())['cases']:
            result=check(case,count<4)
            if result:exact.append(result)
            if first is None:first=case
            count+=1
    assert count==2688 and len(exact)==4
    bad=dict(first,centers_local=[0,1])
    try:check(bad)
    except AssertionError:pass
    else:raise AssertionError('Adjacent-center corruption accepted')
    assert F(240+16*2,49)==F(272,49)<8 and 4-F(272,98)==F(60,49)>0
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),
        'status':'INDEPENDENT_CLOSED28_LOWER_GRAM_LEMMA_PASS','recommendation':'VERIFIED',
        'claim_id':'C-CLOSED-TWO-NEIGHBORHOOD-LOWER-GRAM-REDUNDANCY','claim_revision':1,
        'statement':'For every finite simple graph H with vertex set N[v] union N[u], where v and u are nonadjacent of degree 14 and each center c has common-neighbor count 2-adjacency(c,x) with every other vertex x, A(H)+4I is positive semidefinite of rank 27, with kernel spanned by 1_N(v)-1_N(u)-3(e_v-e_u).',
        'scope':'Universal conditional theorem on two complete nonadjacent neighborhoods with the stated exact center equalities; no additional pair caps assumed.',
        'kind':'mathematical result','basis':['DERIVED'],'dependencies':[],
        'verifier':'/root independent algebraic review, separate exact Python Fraction checking path',
        'inputs_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in inputs},
        'written_audit':'The center equalities give Bn=2j-n and Bm=2j-m on 26 residual vertices. With t=n+m>=j, B has degree at most 3. Therefore M=B+4I>=I by its signless-Laplacian identity. With c=t-j, Mt=7t-4c and c.c=2 imply r=c^T M^-1 c<=2 and t^T M^-1 t=(240+16r)/49<=272/49<8. In the 2x2 Schur complement 4I-C^T M^-1 C, the difference direction is zero since M(n-m)=3(n-m), n.(n-m)=12 and m.(n-m)=-12. The sum direction has eigenvalue 4-t^T M^-1 t/2>=60/49>0. Congruence with positive definite M proves PSD and rank 27. Solving the difference direction yields exactly the stated nonzero kernel. All steps use exact identities; no sampled eigenvalue premise.',
        'controls':{'all_raw_hypotheses_and_identities_checked':count,'exact_fraction_inverse_controls':exact,'adjacent_center_corruption_rejected':True,'wrong_numerator_rejected':True},
        'shared_components':['Python standard library exact integers and Fraction; raw fixtures shared with producer. No producer imports.'],
        'limitations':['The theorem proves redundancy of this necessary PSD test under its hypotheses, not graph extendability.','Only 2688 saved raw examples were computationally checked; universality rests on the reviewed proof.','Original domain generation and floating-point spectra are not independently replayed here.','No target resolution or external peer review.']}
    p=OUT/'summary.json'
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'sha256':digest(p),'raw_cases':count}))

if __name__=='__main__':main()
