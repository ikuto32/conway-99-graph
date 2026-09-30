"""Direct integer congruence checking, independent of producer Schur elimination."""
import argparse, copy, hashlib, json, platform, subprocess, sys
from datetime import datetime, timezone
from fractions import Fraction
from math import lcm
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_first_partial_psd'
PART=B/'20260930_hadamard_four_group_joint_v2/case_000/first_witness.json'
RAW=B/'20260930_hadamard20_support/six_prism.json'
OBJECT=B/'20260930_independent_review/four_group_partial12_object/summary.json'
PINS={D/'summary.json':'df2b1b58ac311c435b5d89356c36e326a2cdc635a196bca4097f07cc9a75405d',D/'certificate.json':'d63b345e717205e32d2d48b02c77d9964b24e1be769afc8f6f82a09456cfff0b',PART:'b4973edd9d4cbf2ca965b36ccfa9cb22515e81a68315368c772487b57b6e7b9d',OBJECT:'8a48a303d687f48c3a84b2427b303a16a32f16e336677e194c4b7b19eafb5fe1'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def det_mod(a,p):
    a=[[v%p for v in row] for row in a];d=1
    for i in range(len(a)):
        k=next((k for k in range(i,len(a)) if a[k][i]),None)
        if k is None:return 0
        if k!=i:a[i],a[k]=a[k],a[i];d=-d
        q=a[i][i];d=d*q%p;inv=pow(q,-1,p)
        for k in range(i+1,len(a)):
            t=a[k][i]*inv%p
            for j in range(i,len(a)):a[k][j]=(a[k][j]-t*a[i][j])%p
    return d%p
def verify(matrix,cert):
    n=len(matrix);need(all(len(row)==n for row in matrix) and all(matrix[i][j]==matrix[j][i] for i in range(n) for j in range(n)),'symmetric raw matrix')
    need(cert['psd'] is True and cert['rank']==len(cert['steps']),'positive certificate rank')
    basis=[list(map(Fraction,s['basis'])) for s in cert['steps']]+[list(map(Fraction,v)) for v in cert['null_basis']]
    need(len(basis)==n and all(len(v)==n for v in basis),'complete square rational basis')
    pivots=[Fraction(s['pivot']) for s in cert['steps']]+[Fraction(0)]*len(cert['null_basis'])
    need(all(v>0 for v in pivots[:cert['rank']]),'strictly positive recorded pivots')
    scales=[lcm(*(v.denominator for v in row)) for row in basis]
    Z=[[int(x*s) for x in row] for row,s in zip(basis,scales,strict=True)]
    d=[v*s*s for v,s in zip(pivots,scales,strict=True)];need(all(v.denominator==1 for v in d),'integer diagonal after row scaling');d=list(map(int,d))
    left=[[sum(Z[i][k]*matrix[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):need(sum(left[i][k]*Z[j][k] for k in range(n))==(d[i] if i==j else 0),'every literal integer congruence entry')
    determinants=[dict(prime=p,determinant=det_mod(Z,p)) for p in [1000000007,1000000009,998244353]]
    need(any(r['determinant'] for r in determinants),'basis invertibility certified modulo a prime')
    return dict(integer_basis=Z,row_scales=scales,integer_diagonal=d,rank=sum(v!=0 for v in d),dimension=n,basis_determinants_mod_primes=determinants,identity='Z R Z^T = diag(integer_diagonal)',nullity=d.count(0))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or v==h,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        s=read(D/'summary.json')
        for p,h in {**s['inputs_sha256'],**s['outputs_sha256']}.items():pin(ROOT/p,h)
        raw=read(RAW);F=read(PART)['factor36x12'];C=raw['core_adjacency']
        K=[[12*int(i==j)+2-C[i][j]-sum(C[i][k]*C[k][j] for k in range(36))-int(i//12==j//12) for j in range(36)] for i in range(36)]
        R=[[K[i][j]-sum(F[i][d]*F[j][d] for d in range(12)) for j in range(36)] for i in range(36)]
        cert=read(D/'certificate.json');need(cert['input_partial_sha256']==PINS[PART] and cert['raw_residual_Gram36']==R==read(PART)['residual_Gram36'],'raw residual identity')
        checked=verify(R,cert);need(checked['rank']==29 and checked['nullity']==7,'exact outcome')
        write(out/'independent_congruence.json',dict(raw_residual=R,**checked))
        controls=read(D/'controls.json');small=verify([[1,1,0],[1,1,0],[0,0,0]],controls['small_positive']);need(small['rank']==1,'singular positive')
        fixture=read(B/'20260930_srg243_residual_fixture/triangle_blocks.json')['factor60x180']
        good=[[sum(fixture[i][d]*fixture[j][d] for d in range(12,180)) for j in range(60)] for i in range(60)]
        need(good==controls['srg243_residual'],'genuine243 remaining168 columns')
        generic=verify(good,controls['srg243_certificate']);need(generic['rank']==controls['srg243_rank'],'generic exact rank')
        rejected=[]
        def reject(name,m,c):
            try:verify(m,c)
            except(ValueError,KeyError,IndexError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        bad=copy.deepcopy(cert);bad['steps'][0]['pivot']='9';reject('changed_pivot',R,bad)
        bad=copy.deepcopy(cert);bad['steps'][0]['basis'][0]='2';reject('changed_basis',R,bad)
        bad=copy.deepcopy(cert);bad['null_basis'][0][0]=str(Fraction(bad['null_basis'][0][0])+1);reject('changed_null_vector',R,bad)
        bad=copy.deepcopy(cert);bad['rank']-=1;reject('wrong_rank',R,bad)
        bad=copy.deepcopy(cert);bad['null_basis'][0]=bad['null_basis'][1][:];reject('dependent_basis',R,bad)
        wrong=copy.deepcopy(R);wrong[0][0]-=20;reject('indefinite_matrix',wrong,cert)
        wrong=copy.deepcopy(R);wrong[0][1]+=1;reject('nonsymmetric_matrix',wrong,cert)
        write(out/'controls.json',dict(singular_positive_rank=small['rank'],genuine243_rank=generic['rank'],genuine243_residual_columns=168,corruptions_rejected=rejected))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_FIRST_PARTIAL_PSD.md']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();write(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,native_solver_calls=0))
        binding=dict(id='C-FIXED-HADAMARD-FIRST-PARTIAL12-RESIDUAL-PSD',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For the exact saved case0 twelve-column partial object, the36x36 residual prescribed Gram matrix is positive semidefinite of rank29 and nullity7 over the rationals/reals, as established by the saved invertible integer congruence to a diagonal matrix with29positive and7zero entries.',scope='This one hash-bound partial object and its exact residual matrix only.',assumptions=['The literal fixed prescribed Gram and twelve-column matrix; no unknown remaining columns are assumed.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-PARTIAL12-CENSUS',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Direct integer matrix congruence multiplication after denominator clearing; nonsingular integer basis certified by nonzero modular determinant. No Schur-elimination replay or producer imports.',shared_components=['Raw producer rational basis and pivot artifacts, Python exact rational/integer arithmetic.','Previously independent partial-object check; no producer code imports.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Workspace evidence pending parent publication.',external_review=None,external_review_reason='No external review asserted.',limitations=['PSD does not establish a binary48-column factor or any residual graph completion.','No other enumerated partial object has its PSD certified by this single-object report.','Producer recursive coefficient metadata is not replayed; the independently sufficient full congruence identity is checked instead.'],created_at=ts,updated_at=ts)
        write(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_FIRST_PARTIAL12_RESIDUAL_PSD_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},rank=29,nullity=7,exact_congruence_entries=1296,basis_invertible=True,corruptions_rejected=len(rejected),native_solver_calls=0,target_resolution=False)
        write(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
