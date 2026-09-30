"""Candidate exact residual PSD diagnostic on a single saved partial factor."""
from datetime import datetime, timezone
from fractions import Fraction
from functools import reduce
from math import gcd,lcm
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
PARTIAL=B/'20260930_hadamard_four_group_joint_v2/case_000/first_witness.json'
RAW=B/'20260930_hadamard20_support/six_prism.json'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS={PARTIAL:'b4973edd9d4cbf2ca965b36ccfa9cb22515e81a68315368c772487b57b6e7b9d',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def integer_vector(v):
    den=lcm(*(x.denominator for x in v));values=[int(x*den) for x in v];g=reduce(gcd,map(abs,values));return [x//g for x in values]
def quad(a,v):return sum(v[i]*a[i][j]*v[j] for i in range(len(a)) for j in range(len(a)))
def decompose(a):
    n=len(a);need(all(len(r)==n for r in a) and all(a[i][j]==a[j][i] for i in range(n) for j in range(n)),'symmetric square input')
    s=[[Fraction(x) for x in row] for row in a];basis=[[Fraction(i==j) for j in range(n)] for i in range(n)];active=list(range(n));steps=[]
    while active:
        negative=next((i for i in active if s[i][i]<0),None)
        if negative is not None:
            v=integer_vector(basis[negative]);q=quad(a,v);need(q<0,'negative diagonal certificate')
            return dict(psd=False,integer_negative_vector=v,exact_quadratic=q,steps=steps,reason='negative_congruence_diagonal')
        positive=next((i for i in active if s[i][i]>0),None)
        if positive is None:
            pair=next(((i,j) for i in active for j in active if i<j and s[i][j]),None)
            if pair:
                i,j=pair;sign=1 if s[i][j]>0 else -1;v=integer_vector([x-sign*y for x,y in zip(basis[i],basis[j])]);q=quad(a,v);need(q<0,'zero diagonal offdiagonal certificate')
                return dict(psd=False,integer_negative_vector=v,exact_quadratic=q,steps=steps,reason='zero_diagonal_nonzero_cross')
            return dict(psd=True,rank=len(steps),steps=steps,null_basis=[[str(x) for x in basis[i]] for i in active])
        p=positive;others=[i for i in active if i!=p];pivot=s[p][p]
        coeff={i:s[p][i]/pivot for i in others}
        steps.append(dict(pivot_index=p,pivot=str(pivot),basis=[str(x) for x in basis[p]],coefficients={str(i):str(v) for i,v in coeff.items()}))
        for i in others:
            basis[i]=[x-coeff[i]*y for x,y in zip(basis[i],basis[p])]
        old={i:s[p][i] for i in others}
        for i in others:
            for j in others:s[i][j]-=old[i]*old[j]/pivot
        active=others
    return dict(psd=True,rank=len(steps),steps=steps,null_basis=[])
def gram(f):return [[sum(x*y for x,y in zip(row,other)) for other in f] for row in f]
def controls():
    positive=decompose([[1,1,0],[1,1,0],[0,0,0]]);need(positive['psd'] and positive['rank']==1,'singular positive control')
    negatives=[]
    for a in [[[-1,0],[0,1]],[[0,1],[1,0]]]:
        c=decompose(a);need(not c['psd'] and quad(a,c['integer_negative_vector'])==c['exact_quadratic']<0,'indefinite controls');need(quad(a,[0,0])>=0 and c['exact_quadratic']!=c['exact_quadratic']+1,'corrupt vector/value rejected');negatives.append(c)
    f=read(FIXTURE)['factor60x180'];g=gram(f);e=gram([r[:12] for r in f]);residual=[[g[i][j]-e[i][j] for j in range(60)] for i in range(60)]
    need(residual==gram([r[12:] for r in f]),'genuine243 literal remaining168 factor')
    c=decompose(residual);need(c['psd'],'genuine243 residual PSD')
    return dict(small_positive=positive,negative_controls=negatives,srg243_rank=c['rank'],srg243_residual= residual,srg243_certificate=c,scope='Different-parameter positive control, no research construction.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'pin '+key(path))
        inputs={key(path):digest for path,digest in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_first_partial_psd_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limit_seconds=120))
        save(out/'controls.json',controls());partial=read(PARTIAL);f=partial['factor36x12'];target=read(RAW)['prescribed_Gram36'];contribution=gram(f)
        residual=[[target[i][j]-contribution[i][j] for j in range(36)] for i in range(36)];need(residual==partial['residual_Gram36'],'independent literal saved residual equality')
        certificate=decompose(residual);save(out/'certificate.json',dict(input_partial_sha256=PINS[PARTIAL],raw_residual_Gram36=residual,**certificate,scope='This exact twelve-column partial object only; independent review pending.'))
        save(out/'summary.json',dict(status='CANDIDATE_SINGLE_PARTIAL_RESIDUAL_PSD_DIAGNOSTIC',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},residual_psd=certificate['psd'],exact_negative_quadratic=certificate.get('exact_quadratic'),null_reason=None if not certificate['psd'] else 'No negative certificate; exact positive congruence decomposition saved.',elapsed_seconds=time.monotonic()-start,independent_approval=False,native_solver_calls=0,target_resolution=False))
        print(json.dumps(dict(psd=certificate['psd'],q=certificate.get('exact_quadratic'),elapsed_seconds=time.monotonic()-start)))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
