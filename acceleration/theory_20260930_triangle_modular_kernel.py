"""Exact bounded modular exploration; newly produced claims remain CANDIDATE."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def nullspace(a,p):
    a=np.array(a,dtype=np.int64)%p;original=a.copy();m,n=a.shape;row=0;pivots=[]
    for col in range(n):
        candidates=np.flatnonzero(a[row:,col])
        if not len(candidates):continue
        pivot=row+int(candidates[0]);a[[row,pivot]]=a[[pivot,row]];a[row]=(a[row]*pow(int(a[row,col]),-1,p))%p
        for i in range(m):
            if i!=row and a[i,col]:a[i]=(a[i]-int(a[i,col])*a[row])%p
        pivots.append(col);row+=1
        if row==m:break
    free=[j for j in range(n) if j not in pivots];basis=[]
    for j in free:
        v=np.zeros(n,dtype=np.int64);v[j]=1
        for i,k in enumerate(pivots):v[k]=-a[i,j]%p
        assert not np.any(original@v%p);basis.append(v)
    return np.array(basis,dtype=np.int64).reshape((len(free),n)),pivots

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    fixture=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
    assert digest(fixture)=='3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'
    raw=json.loads(fixture.read_bytes());c=np.array(raw['cubic_core60'],dtype=np.int64);f=np.array(raw['factor60x180'],dtype=np.int64);d=np.array(raw['residual180x180'],dtype=np.int64)
    n=20;rows=60;cols=180;r=np.zeros((rows,3),dtype=np.int64)
    for i in range(rows):r[i,i//n]=1
    k=n*np.eye(rows,dtype=np.int64)-c-c@c+2-r@r.T;h=2-f-c@f
    assert np.array_equal(f@f.T,k) and np.array_equal(f@d,h)
    assert np.array_equal(d@d+f.T@f,n*np.eye(cols,dtype=np.int64)-d+2)
    assert np.all(f.sum(axis=1)==18) and np.all(r.T@f==2)
    bad=h.copy();bad[0,0]+=1;assert not np.array_equal(f@d,bad)
    # Literal rook9 triangle gives three2-point fibres and an empty residual.
    rook=np.array([[int(i!=j and (i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)],dtype=np.int64)
    assert np.array_equal(rook@rook,2*np.eye(9,dtype=np.int64)-rook+2)
    triangle=[0,1,2];cells=[[x for x in range(9)if x not in triangle and rook[t,x]]for t in triangle]
    assert list(map(len,cells))==[2,2,2] and set(sum(cells,[]))==set(range(3,9))
    inputs=[Path(__file__),Path(__file__).with_name('theory_20260930_triangle_modular_kernel_spec.md'),fixture,ROOT/'docs/AUDIT_20260930_TARGET_MODULAR_RANKS.md',ROOT/'docs/DERIVATION_20260930_TRIANGLE39_GRAM_SOS.md',ROOT/'docs/DERIVATION_20260930_TRIANGLE_RESIDUAL60.md',ROOT/'external_conway99_research/attempts/wave58-cross-incidence-rank/derivation.md',ROOT/'uv.lock',ROOT/'pyproject.toml']
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,seed=20260930,maximum_attempts_per_prime=128,wall_limit_seconds=120,inputs_sha256={p.relative_to(ROOT).as_posix():digest(p)for p in inputs})
    save(out/'manifest.json',manifest);rng=random.Random(20260930);results=[]
    for p in (2,3):
        left,pivots=nullspace(f.T,p);assert not np.any(left@h%p)
        right,_=nullspace(np.vstack([f,np.ones(cols,dtype=np.int64)]),p)
        attempts=[];counterexample=None
        for trial in range(128):
            assert time.monotonic()-start<120,'frozen wall limit reached'
            for selection in range(100):
                coeff=np.array([rng.randrange(p)for _ in range(len(right))],dtype=np.int64);v=coeff@right%p
                if np.any(v) and int(v@v)%p==0:break
            else:raise AssertionError('no isotropic kernel vector in100 fixed draws')
            u=np.zeros(rows,dtype=np.int64)
            for g in range(3):
                values=[rng.randrange(p)for _ in range(n-1)];u[g*n:g*n+n]=values+[-sum(values)%p]
            ff=(f+u[:,None]*v[None,:])%p;hh=(2-ff-c@ff)%p
            assert not np.any((ff@ff.T-k)%p) and not np.any((ff.sum(axis=1)-18)%p) and not np.any((r.T@ff-2)%p)
            ll,pp=nullspace(ff.T,p);obstruction=ll@hh%p;indices=np.argwhere(obstruction)
            attempts.append(dict(trial=trial,modular_row_rank=len(pp),left_kernel_dimension=len(ll),mixed_kernel_failures=int(np.count_nonzero(obstruction))))
            if len(indices):
                i,j=map(int,indices[0]);w=ll[i];assert not np.any(w@ff%p) and int((w@hh)[j])%p!=0
                broken=w.copy();broken[0]=(broken[0]+1)%p;assert np.any(broken@ff%p)
                counterexample=dict(prime=p,trial=trial,parameter_family=[243,22,1,2],core=c.tolist(),factor=ff.tolist(),gram=k.tolist(),mixed_rhs=hh.tolist(),perturbation_u=u.tolist(),perturbation_v=v.tolist(),left_kernel_w=w.tolist(),failed_rhs_column=j,nonzero_residue=int((w@hh)[j])%p,binary_factor_claim=False,conway99_claim=False)
                save(out/f'counterexample_mod{p}.json',counterexample);break
        results.append(dict(prime=p,base_modular_row_rank=len(pivots),base_left_kernel_dimension=len(left),attempts=attempts,result='EXPLICIT_MODULAR_REDUNDANCY_COUNTEREXAMPLE_CANDIDATE'if counterexample else'NO_COUNTEREXAMPLE_IN_FROZEN128_PERTURBATIONS',counterexample=f'counterexample_mod{p}.json'if counterexample else None))
    save(out/'summary.json',dict(status='CANDIDATE_MODULAR_KERNEL_EXPLORATION_COMPLETED',timestamp=datetime.now(timezone.utc).isoformat(),results=results,controls=dict(exact243_gram_mixed_quadratic=True,rook9_empty_residual=True,changed_mixed_rhs_rejected=True),limitations=['No independent approval of this producer.','Finite-field perturbations are not claimed binary incidence factors.','A generalized parameter243 counterexample would not by itself refute any claim restricted specifically to parameter99.','No Conway99 factor, exclusion or rank novelty claimed.'],elapsed_seconds=time.monotonic()-start,inputs_sha256=manifest['inputs_sha256'],outputs_sha256={p.relative_to(ROOT).as_posix():digest(p)for p in out.iterdir()if p.is_file()}))
    print(json.dumps(dict(summary=str(out/'summary.json'),sha256=digest(out/'summary.json'),results=[dict(prime=x['prime'],result=x['result'],attempts=len(x['attempts']))for x in results])))

if __name__=='__main__':main()
