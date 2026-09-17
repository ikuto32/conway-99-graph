"""Exact producer calibration for the conditional eighteen-cell rook encoding."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import platform
import subprocess
import sys
import numpy as np

OUT=Path('acceleration/results/20260917_rook_regular_set')


def digest(p): return sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')


def characteristic(matrix):
    a=np.array(matrix,dtype=object);n=len(a);power=np.eye(n,dtype=object)
    traces=[];coeff=[1]
    for k in range(1,n+1):
        power=power@a;traces.append(sum(power[i,i] for i in range(n)))
        value=sum(coeff[k-i]*traces[i-1] for i in range(1,k+1))
        assert value%k==0;coeff.append(-value//k)
    return list(map(int,coeff))


def polynomial(factors):
    result=[1]
    for root,count in factors:
        for _ in range(count):
            nxt=[0]*(len(result)+1)
            for i,c in enumerate(result):nxt[i]+=c;nxt[i+1]-=root*c
            result=nxt
    return result


def main():
    OUT.mkdir(exist_ok=True);assert not any(OUT.iterdir())
    paths=[Path(__file__),Path('docs/THEORY_20260917_ROOK_REGULAR_SET.md'),Path('uv.lock')]
    save(OUT/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        inputs_sha256={str(p):digest(p) for p in paths},versions=dict(python=platform.python_version(),numpy=np.__version__),
        scope='Conditional on induced rook9; exact block identity and quotient compatibility only. No target exclusion or assumption of automorphism.',
        calibration='Known-valid rook9, exact integer characteristic polynomials, ten deterministic binary90x90 H block-residual identities. These finite controls do not prove the universal derivation.',
        limits='Ten calibration masks and two quotient polynomials, no search or solver.',random_seed=None,random_seed_null_reason='Deterministic modular formulas, no PRNG.'))
    vertices=[(r,c) for r in range(3) for c in range(3)]
    b=np.array([[int(i!=j and (a[0]==z[0] or a[1]==z[1])) for j,z in enumerate(vertices)]for i,a in enumerate(vertices)],dtype=np.int64)
    assert np.array_equal(b@b,2*np.eye(9,dtype=np.int64)-b+2*np.ones((9,9),dtype=np.int64))
    t=np.kron(np.eye(9,dtype=np.int64),np.ones((1,10),dtype=np.int64))
    q=2*np.ones((9,9),dtype=np.int64)-b-np.eye(9,dtype=np.int64)
    quotient=np.block([[b,10*np.eye(9,dtype=np.int64)],[np.eye(9,dtype=np.int64),q]])
    assert characteristic(q)==polynomial([(13,1),(-2,4),(1,4)])
    assert characteristic(quotient)==polynomial([(14,1),(3,9),(-4,8)])
    records=[]
    for case in range(10):
        h=np.zeros((90,90),dtype=np.int64)
        for i in range(90):
            for j in range(i+1,90):
                h[i,j]=h[j,i]=int(((i+3)*(j+7)+case*(i+j+1))%(11+case)<case)
        a=np.block([[b,t],[t.T,h]])
        residual=a@a-12*np.eye(99,dtype=np.int64)+a-2*np.ones((99,99),dtype=np.int64)
        cross=t@h-q@t
        lower=h@h-12*np.eye(90,dtype=np.int64)+h-2*np.ones((90,90),dtype=np.int64)+t.T@t
        assert not np.any(residual[:9,:9])
        assert np.array_equal(residual[:9,9:],cross) and np.array_equal(residual[9:,:9],cross.T)
        assert np.array_equal(residual[9:,9:],lower)
        corrupted=lower.copy();corrupted[0,0]+=1
        assert not np.array_equal(residual[9:,9:],corrupted)
        records.append(dict(case=case,edges=int(h.sum()//2),full_residual_nonzeros=int(np.count_nonzero(residual)),block_identity=True,corrupted_identity_rejected=True))
    artifact=dict(B=b.tolist(),T=t.tolist(),Q=q.tolist(),eighteen_cell_quotient=quotient.tolist(),Q_characteristic=characteristic(q),quotient_characteristic=characteristic(quotient))
    save(OUT/'exact_matrices.json',artifact)
    save(OUT/'summary.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='CANDIDATE_CONDITIONAL_ENCODING',known_valid_rook9=True,calibration_records=records,
        exact_eighteen_cell_eigenvalue_multiplicities={'14':1,'3':9,'-4':8},remaining_target_multiplicities={'3':45,'-4':36},spectral_contradiction=False,
        independent_review_pending=True,unrestricted_target_resolution=False,matrices_sha256=digest(OUT/'exact_matrices.json')))
    print(json.dumps(dict(status='CANDIDATE',calibrations=len(records),spectral_contradiction=False)))


if __name__=='__main__':main()
