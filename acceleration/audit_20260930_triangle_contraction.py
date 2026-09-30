"""Independent conditional triangle contraction and genuine243 block controls."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'acceleration/results/20260930_triangle_contraction'
def need(x,s):
    if not x:raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def structural(d,triangles,degree):
    n=len(d);m=len(triangles);need(n==3*m and all(len(row)==n for row in d),'square dimension')
    need(all(type(v)is int and v in [0,1] for row in d for v in row),'literal binary D')
    nb=[{j for j,v in enumerate(row) if v} for row in d]
    need(all(i not in nb[i] and len(nb[i])==degree and all((j in nb[i])==(i in nb[j]) for j in range(n)) for i in range(n)),'simple regular D')
    need(all(len(t)==3 for t in triangles) and sorted(sum(triangles,[]))==list(range(n)),'complete disjoint triple partition')
    sets=list(map(set,triangles));owner={i:p for p,t in enumerate(sets) for i in t}
    need(all(t-{i}<=nb[i] for t in sets for i in t),'actual clique triangles')
    r=[[int(owner[i]==p) for p in range(m)] for i in range(n)]
    w=[[int(bool(nb[i]&t)) if owner[i]!=p else 0 for p,t in enumerate(sets)] for i in range(n)]
    need(all(len(nb[i]&t)<=1 for i in range(n) for p,t in enumerate(sets) if owner[i]!=p),'outside triangle neighborhood bound')
    need(all(sum(row)==degree-2 for row in w) and all(sum(row[p] for row in w)==3*(degree-2) for p in range(m)),'W exact margins')
    b=[[sum(int(j in nb[i]) for i in t for j in u) if p!=q else 0 for q,u in enumerate(sets)] for p,t in enumerate(sets)]
    need(all(b[p][p]==0 and sum(b[p])==3*(degree-2) and all(0<=b[p][q]<=3 and b[p][q]==b[q][p] for q in range(m)) for p in range(m)),'B exact margins and caps')
    wt=[[sum(row[p]*row[q] for row in w) for q in range(m)] for p in range(m)]
    literal=[[sum(len(nb[i]&nb[j])+int(j in nb[i]) for i in t for j in u) for u in sets] for t in sets]
    need(literal==[[18*int(p==q)+5*b[p][q]+wt[p][q] for q in range(m)] for p in range(m)],'all literal contraction entries')
    return dict(R=r,W=w,B=b,WtW=wt,literal_contracted_D2_plus_D=literal)

def factor_checks(f,c,d,triangles,k):
    n=len(d);h=len(f);m=len(triangles);need(all(len(row)==n and all(type(v)is int and v in [0,1] for v in row) for row in f),'literal factor')
    need(all(sum(row)==k-4 for row in f) and all(sum(row[j] for row in f)==6 for j in range(n)),'factor margins')
    cols=[{i for i,row in enumerate(f) if row[j]} for j in range(n)];dn=[{j for j,v in enumerate(row) if v} for row in d]
    for i in range(n):
        for j in range(n):need(len(cols[i]&cols[j])+len(dn[i]&dn[j])+d[i][j]==(k-2)*int(i==j)+2,'exact raw residual equation')
    result=structural(d,triangles,k-6);t=[[sum(row[y] for y in tri) for tri in triangles] for row in f]
    need(all(v in [0,1] for row in t for v in row),'disjoint actual triangle factor columns')
    need(all(sum(row)==k-4 for row in t) and all(sum(row[p] for row in t)==18 for p in range(m)),'T margins')
    tt=[[sum(row[p]*row[q] for row in t) for q in range(m)] for p in range(m)]
    need(all(tt[p][q]+5*result['B'][p][q]+result['WtW'][p][q]==(3*k-24)*int(p==q)+18 for p in range(m) for q in range(m)),'exact generalized aggregated target equation')
    fw=[[sum(f[i][y]*result['W'][y][p] for y in range(n)) for p in range(m)] for i in range(h)]
    rhs=[[6-3*t[i][p]-sum(c[i][j]*t[j][p] for j in range(h)) for p in range(m)] for i in range(h)]
    need(fw==rhs,'exact generalized mixed contraction')
    return dict(**result,T=t,TtT=tt,FW=fw,vertices=n,triangles=m,degree=k-6,factor_rows=h,parameter_k=k)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact pin '+key(p));bindings[key(p)]=value
    try:
        pin(D/'summary.json','5740258d9d703f0afe75e46ac54cc6e0fe9fe7785ffa8608ac5d7170b71603a3');prod=read(D/'summary.json')
        for p,h in {**prod['inputs_sha256'],**prod['outputs_sha256']}.items():pin(ROOT/p,h)
        raw=read(ROOT/'acceleration/results/20260930_independent_review/identity_p_triangle_partition/residual60_control.json')
        control=structural(raw['D'],raw['triangles'],8);need(control==read(D/'raw_contraction.json'),'independent raw structural contraction reproduction')
        save(out/'structural60_recheck.json',control)
        fixture=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json';pin(fixture,'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439')
        fg=ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json';pin(fg,'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e')
        f=read(fixture);need(f['cross12']==list(range(20)),'known243 identity crosses')
        outside=f['original_outside_vertices'];loc={v:i for i,v in enumerate(outside)}
        def digits(v):return [(v//3**i)%3 for i in range(5)]
        a,b=f['original_triangle'][:2];direction=[(y-x)%3 for x,y in zip(digits(a),digits(b))]
        def translate(v,t):return sum(((x+t*y)%3)*3**i for i,(x,y) in enumerate(zip(digits(v),direction)))
        remaining=set(outside);partition=[]
        while remaining:
            v=min(remaining);triple=[translate(v,t) for t in range(3)];need(len(set(triple))==3 and set(triple)<=remaining,'literal residual parallel-class orbit')
            partition.append([loc[u] for u in triple]);remaining.difference_update(triple)
        full=factor_checks(f['factor60x180'],f['cubic_core60'],f['residual180x180'],partition,22)
        save(out/'known243_positive.json',dict(label='Actual known243 block fixture; not99',partition_original_ids=[[outside[i] for i in t] for t in partition],partition_residual_ids=partition,contraction=full))
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(label)
            else:raise ValueError('accepted corrupt control '+label)
        for label in ['loop','asymmetry','missing_edge']:
            d=deepcopy(raw['D'])
            if label=='loop':d[0][0]=1
            else:
                j=next(i for i,v in enumerate(d[0]) if v);d[0][j]=0
                if label=='missing_edge':d[j][0]=0
            reject(label,lambda d=d:structural(d,raw['triangles'],8))
        bad=deepcopy(raw['triangles']);bad[0][0]=bad[1][0];reject('duplicate_partition',lambda:structural(raw['D'],bad,8))
        badf=deepcopy(f['factor60x180']);badf[0][0]^=1
        reject('factor_entry',lambda:factor_checks(badf,f['cubic_core60'],f['residual180x180'],partition,22))
        reject('243_as99_parameter',lambda:factor_checks(f['factor60x180'],f['cubic_core60'],f['residual180x180'],partition,14))
        badc=deepcopy(f['cubic_core60']);badc[0][1]^=1
        reject('mixed_core_entry',lambda:factor_checks(f['factor60x180'],badc,f['residual180x180'],partition,22))
        need(any(control['literal_contracted_D2_plus_D'][p][q]!=18*int(p==q)+4*control['B'][p][q]+control['WtW'][p][q] for p in range(20) for q in range(20)),'coefficient4 corrupted identity rejected');rejected.append('coefficient4')
        need(all(sum(control['WtW'][p][q] for q in range(20) if q!=p)==90 for p in range(20)),'structural60 sumL90')
        save(out/'controls.json',dict(known243=dict(raw_residual_entries=32400,aggregate_entries=3600,mixed_entries=3600,partition_triangles=60,residual_degree=16,W_column_weight=42),structural60=dict(contraction_entries=400,triangles=20,degree=8,W_column_weight=18,has_F=False),corruptions_rejected=rejected))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_CONTRACTION.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_IDENTITY_P_RESIDUAL_TRIANGLE_CONTRACTION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},verifier='/root/state_literature_audit',method='independent_derivation_and_exact_artifact_check',shared_components=['Python standard library only; no producer imports.','Previously independently validated243 raw fixture and earlier independently checked conditional partition premise.'],scope='Actual identity-P target completions and their actual residual triangle partition only.',recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',target_resolution=False,limitations=['No99factor or completion is produced.','A chosen cyclic or other predetermined partition is not asserted WLOG.','The243 controls use residual degree16 and60triangles, not the99parameters.','New capacity-floor corollary is separately CANDIDATE pending parent review.'])
        save(out/'summary.json',report)
        claim=dict(id='C-IDENTITY-P-RESIDUAL-TRIANGLE-CONTRACTION',revision=1,statement='For every actual SRG(99,14,1,2) completion in the identity-cross triangle-root family and its actual residual triangle partition R, T=FR and W=DR-2R satisfy binary W with row6/column18, B=R^TW symmetric with zero diagonal entries0..3 and row18, T^TT+5B+W^TW=18I+18J and FW=6J-(C+3I)T; T is binary with row10/column18.',kind='mathematical result',basis=['DERIVED'],recommendation='VERIFIED',review_state='CLEAR',scope=report['scope'],assumptions=['No nontrivial target automorphism is assumed.','R is an actual residual-D triangle partition, not a prescribed arbitrary cover.'],dependencies=[dict(id='C-IDENTITY-P-COMPLETION-THIRTYTHREE-TRIANGLE-PARTITION',revision=1,relation='premise'),dict(id='C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE',revision=1,relation='uses_result'),dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',revision=1,relation='verification_dependency')],evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],verifier=report['verifier'],method=report['method'],limitations=report['limitations'],created_at=now,updated_at=now)
        save(out/'claim_binding.json',claim)
        save(out/'capacity_floor_candidate.json',dict(status='CANDIDATE',statement='For every binary36x20 T with row10 and column18, each row of the off-diagonal capacities floor((18-T_p^TT_q)/5) sums at least21, so its individual18-degree capacity check is redundant.',proof='The19 numerators are nonnegative integers summing19*18-(18*10-18)=180. Their residues modulo5 sum a multiple of5 at most19*4=76, hence at most75. The sum of floors is at least(180-75)/5=21.',scope='Pure margin consequence only; does not settle simultaneous bounded-degree feasibility.',independent_approval=False,source_doc='docs/AUDIT_20260930_TRIANGLE_CONTRACTION.md'))
        print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),binding_sha256=digest(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
