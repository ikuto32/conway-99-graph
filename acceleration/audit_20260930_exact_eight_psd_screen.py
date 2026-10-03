"""Exact integer certificate audit, independent of PSD producer elimination."""
from pathlib import Path
from itertools import combinations, product
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from math import gcd, lcm, prod
import argparse, copy, gzip, hashlib, json, sys, time
import yaml

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
DIR=B+'exact_eight_psd_screen/';SUMMARY=DIR+'summary_001.json'
SURV=B+'exact_eight_block_screen/surviving_representatives.json.gz'
RAW=B+'hadamard20_support/six_prism.json';FIXTURE=B+'srg243_residual_fixture/triangle_blocks.json'
SNAP=B+'twentyseventh_psd_candidate_registration/CLAIMS.after.yaml'
CID='C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN'
DOC='docs/AUDIT_20260930_EXACT_EIGHT_PSD_SCREEN.md'
PINS={SUMMARY:'7f60e486053bfe4b824b277691445e73ed3c468ab3ccdc4676db622b7d674207',SURV:'2cf8ab222d5dd220381fdc14bd225438c173aea40d895353e02f752bc537de5f',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',SNAP:'0caa7b49f9a8c2e6e8d17a53d2f097b8d56a1610fd48fa9a56ec28ed662b8df9',I+'exact_eight_block_screen/summary.json':'6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a',I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e','acceleration/theory_20260930_exact_eight_psd_screen.py':'f552e55db7a21d6fde4093b6b800d141c6540f5496dc2180d8cc5c4678d81916','acceleration/theory_20260930_exact_eight_psd_screen_spec.md':'afc5e6e1903f6c1dedb82b5cb18fdb2f9506b6b2811f69d497b6ded47039dc41'}
INPUTS={}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def path(p):
    p=str(p).replace('\\','/');need(p!=I+'hadamard_oriented_unknown/process.stdout.log' and 'PROMPT.md' not in p and not p.startswith('tools/'),'protected path')
    q=(ROOT/p).resolve();need(q.is_relative_to(ROOT),'path escape');return q
def sha(p):
    q=path(p)
    with q.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    INPUTS[q.relative_to(ROOT).as_posix()]=h;return h
def read(p):sha(p);return json.loads(path(p).read_bytes())
def bind(p,h):need(sha(p)==h,'hash '+str(p))
def gzread(p):
    sha(p)
    with gzip.open(path(p),'rt',encoding='utf8')as f:return json.load(f)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def savegz(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0)as z:z.write((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode())
def pack(x):
    q=Fraction(x);return[q.numerator,q.denominator]
def canonical_hash(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()

def gram(a):return[[sum(x*y for x,y in zip(r,s))for s in a]for r in a]
def necessary_identity(F):
    n=len(F);m=len(F[0]);need(m%3==0,'triplicate width')
    N=[[sum(row[j:j+3])for j in range(0,m,3)]for row in F];G=gram(F);NN=gram(N)
    R=[[3*G[i][j]-NN[i][j]for j in range(n)]for i in range(n)]
    diffs=[[row[g+a]-row[g+b]for g in range(0,m,3)for a,b in combinations(range(3),2)]for row in F]
    need(R==gram(diffs),'literal necessary pair-difference identity');return R

def literal_gram(raw):
    C=[[int((i//12==j//12 and (i%12)^1==j%12)or(i//12!=j//12 and i%12==j%12))for j in range(36)]for i in range(36)]
    C2=[[sum(C[i][k]*C[k][j]for k in range(36))for j in range(36)]for i in range(36)]
    G=[[12*int(i==j)-C[i][j]-C2[i][j]+2-int(i//12==j//12)for j in range(36)]for i in range(36)]
    need(C==raw['core_adjacency']and G==raw['prescribed_Gram36'],'raw core and Gram');return G

def check_certificate(M,certificate,expected_rank=None):
    n=len(M);need(all(len(row)==n for row in M)and all(M[i][j]==M[j][i]for i in range(n)for j in range(n)),'symmetric integer input')
    T=certificate['transform'];d=certificate['diagonal']
    need(len(T)==len(d)==n and all(len(r)==n for r in T),'certificate dimensions')
    for r in T:
        for x in r:need(isinstance(x,list)and len(x)==2 and all(type(v)is int for v in x)and x[1]>0 and gcd(*x)==1,'canonical rational transform')
    for i in range(n):
        need(T[i][i]==[1,1] and all(T[i][j][0]==0 for j in range(i)),'literal unit-upper transform invertibility')
        need(isinstance(d[i],list)and len(d[i])==2 and all(type(v)is int for v in d[i])and d[i][1]>0 and gcd(*d[i])==1,'canonical diagonal')
    scales=[lcm(*(T[i][j][1]for i in range(n)))for j in range(n)]
    columns=[[T[i][j][0]*(scales[j]//T[i][j][1])for i in range(n)]for j in range(n)]
    sparse=[[(i,x)for i,x in enumerate(c)if x]for c in columns]
    products=[[sum(M[i][k]*v for k,v in sparse[j])for i in range(n)]for j in range(n)]
    diag=[]
    for j in range(n):
        numerator=d[j][0]*scales[j]*scales[j];need(numerator%d[j][1]==0,'integer scaled diagonal');diag.append(numerator//d[j][1])
        for i in range(n):need(sum(v*products[j][k]for k,v in sparse[i])==(diag[j]if i==j else 0),'full integer congruence')
    need(all(x>=0 for x in diag),'negative diagonal')
    rank=sum(x>0 for x in diag);need(certificate['status']=='EXACT_RATIONAL_PSD'and certificate['rank']==rank,'claimed exact PSD/rank')
    if expected_rank is not None:need(rank==expected_rank,'expected rank')
    null=[columns[j]for j,x in enumerate(diag)if x==0]
    need(all(all(v==0 for v in products[j])for j,x in enumerate(diag)if x==0),'direct nullspace vectors')
    return dict(rank=rank,nullity=n-rank,integer_column_scales=scales,scaled_diagonal=diag,integer_nullvectors=null,determinant_T=1,determinant_U=str(prod(scales)),all_congruence_entries=n*n,producer_shears_used=False)

def controls():
    good=bad=0
    for a,b,c in product(range(-2,3),repeat=3):
        M=[[a,b],[b,c]];t=Fraction(-b,a)if a else Fraction(0)
        diagonal=[Fraction(a),Fraction(c)-Fraction(b*b,a)if a else Fraction(c)]
        cert=dict(transform=[[[1,1],pack(t)],[[0,1],[1,1]]],diagonal=[pack(x)for x in diagonal],status='EXACT_RATIONAL_PSD',rank=sum(x>0 for x in diagonal))
        expected=a>=0 and c>=0 and a*c>=b*b
        try:check_certificate(M,cert)
        except ValueError:actual=False;bad+=1
        else:actual=True;good+=1
        need(actual==expected,'complete2x2 principal-minor calibration')
    for bits in product(range(2),repeat=12):necessary_identity([list(bits[3*i:3*i+3])for i in range(4)])
    nontrivial=dict(transform=[[[1,1],[1,2]],[[0,1],[1,1]]],diagonal=[[2,1],[5,2]],status='EXACT_RATIONAL_PSD',rank=2)
    check_certificate([[2,-1],[-1,3]],nontrivial,2)
    return dict(symmetric_2x2_cases=125,PSD_positives=good,nonPSD_rejections=bad,binary_partition_identities=4096,rational_nontrivial_positive=1)

def reject(name,fn,record):
    try:fn()
    except(ValueError,KeyError,IndexError):record.append(name)
    else:raise ValueError('accepted corruption '+name)

def raw_profile(item,rep,G):
    counts=rep['counts'];need(item['counts']==counts,'raw count table')
    v=bytes(x for row in counts for triple in row for x in triple);dg=hashlib.sha256(v).hexdigest()
    need(len(v)==720 and dg==rep['canonical_fibre_profile_sha256']==item['canonical_fibre_profile_sha256'],'raw count digest')
    N=[[counts[a][g][f]for g in range(20)]for f in range(3)for a in range(12)]
    need(item['N36x20']==N and item['G36']==G,'literal N/G')
    NN=gram(N);M=[[3*G[i][j]-NN[i][j]for j in range(36)]for i in range(36)]
    need(item['R36']==M,'literal R');return N,M

def population(summary,reps):
    need(summary['completed']==summary['population']==792 and len(summary['results'])==792,'complete792')
    expected=[r['canonical_fibre_profile_sha256']for r in reps]
    need([r['canonical_fibre_profile_sha256']for r in summary['results']]==expected and len(set(expected))==792,'complete ordered population')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        for p,h in PINS.items():bind(p,h)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),path(DOC)]:sha(p.relative_to(ROOT).as_posix())
        summary=read(SUMMARY)
        for p,h in summary['inputs_sha256'].items():bind(p,h)
        block=read(I+'exact_eight_block_screen/summary.json');need(block['status']=='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS'and block['inputs_sha256'][SURV]==PINS[SURV],'population gate')
        reps=gzread(SURV);need(reps['complete'],'complete survivor stream');reps=sorted(reps['records'],key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']));population(summary,reps)
        snapshot=yaml.safe_load(path(SNAP).read_bytes());candidate=next(c for c in snapshot['claims']if c['id']==CID)
        need(candidate['revision']==1 and candidate['status']=='CANDIDATE'and candidate['verification']==[],'literal candidate r1')
        calibration=controls();fixture_R=necessary_identity(read(FIXTURE)['factor60x180']);calibration['genuine243_identity_entries']=len(fixture_R)**2
        G=literal_gram(read(RAW));records=[];rank_hist=Counter();sample=None
        for index,(ref,rep) in enumerate(zip(summary['results'],reps)):
            p=DIR+f'profile_{index:04d}.json.gz';need(ref['index']==index and ref['certificate_path']==p,'ordered literal certificate path');bind(p,ref['certificate_sha256']);item=gzread(p)
            need(item['index']==index and item['subset_index']==rep['subset_index'],'raw case identity')
            N,M=raw_profile(item,rep,G);exact=check_certificate(M,item['certificate'],22)
            need(ref['rank']==exact['rank']and ref['status']=='EXACT_RATIONAL_PSD','summary/certificate agreement')
            cp=read(DIR+f'checkpoint_{index+1:04d}.json')
            need(cp['completed']==index+1 and cp['population']==792 and cp['last_profile']==p and cp['last_profile_sha256']==INPUTS[p]and cp['inputs_sha256']==summary['inputs_sha256'],'checkpoint identity')
            records.append(dict(index=index,canonical_fibre_profile_sha256=ref['canonical_fibre_profile_sha256'],raw_certificate_path=p,raw_certificate_sha256=INPUTS[p],N_sha256=canonical_hash(N),G_sha256=canonical_hash(G),R_sha256=canonical_hash(M),**exact));rank_hist[exact['rank']]+=1
            if sample is None:sample=(item,rep,M)
        need(rank_hist=={22:792}and summary['rank_counts']=={'22':792}and summary['result_counts']=={'EXACT_RATIONAL_PSD':792},'all exact ranks/results')
        for name in ['manifest.json','attempt_001.json','controls_001.json']:read(DIR+name)
        corruptions=[];item,rep,M=sample
        for name,mut in [('matrix_entry',lambda m,c:m[0].__setitem__(0,m[0][0]+1)),('changed_upper_transform',lambda m,c:c['transform'][0].__setitem__(2,[0,1])),('singular_transform',lambda m,c:c['transform'][0].__setitem__(0,[0,1])),('lower_transform',lambda m,c:c['transform'][1].__setitem__(0,[1,1])),('diagonal',lambda m,c:c['diagonal'].__setitem__(0,[21,1])),('wrong_rank',lambda m,c:c.__setitem__('rank',23)),('negative_denominator',lambda m,c:c['transform'][0].__setitem__(0,[-1,-1]))]:
            mm=copy.deepcopy(M);cc=copy.deepcopy(item['certificate']);mut(mm,cc);reject(name,lambda:check_certificate(mm,cc,22),corruptions)
        damaged=copy.deepcopy(item);damaged['N36x20'][0][0]+=1;reject('raw_N',lambda:raw_profile(damaged,rep,G),corruptions)
        damaged=copy.deepcopy(item);damaged['counts'][0][0][0]+=1;reject('raw_counts',lambda:raw_profile(damaged,rep,G),corruptions)
        damaged=copy.deepcopy(summary);damaged['results'].pop();reject('missing_profile',lambda:population(damaged,reps),corruptions)
        damaged=copy.deepcopy(summary);damaged['results'][1]=copy.deepcopy(damaged['results'][0]);reject('duplicate_profile',lambda:population(damaged,reps),corruptions)
        bad=dict(transform=[[[1,1],[0,1]],[[0,1],[1,1]]],diagonal=[[-1,1],[1,1]],status='EXACT_RATIONAL_PSD',rank=2);reject('genuine_indefinite',lambda:check_certificate([[-1,0],[0,1]],bad),corruptions)
        savegz(out/'integer_congruence_checks.json.gz',dict(complete=True,records=records))
        save(out/'controls.json',dict(**calibration,corruptions_rejected=corruptions,fixture_scope='Own-Gram triplicate identity, not a research792 factor.'))
        stamp=datetime.now(timezone.utc).isoformat();need(time.monotonic()-started<120,'audit allocation')
        outputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(out.iterdir())if p.is_file()}
        result=dict(status='INDEPENDENT_EXACT_EIGHT_PSD_SCREEN_PASS',created_at=stamp,command=[sys.executable,*sys.argv],cwd=str(ROOT),claim_id=CID,claim_revision=2,canonical_profiles=792,PSD_profiles=792,excluded_profiles=0,rank_counts={'22':792},congruence_entries=792*36*36,literal_triangular_invertibility_checks=792,direct_integer_nullvectors=792*14,producer_operations_replayed=False,producer_imports=False,inputs_sha256=INPUTS,outputs_sha256=outputs,controls_rejected=len(corruptions),scope=candidate['scope']['description'],native_calls=0,ledger_changes=False,elapsed_seconds=time.monotonic()-started)
        save(out/'summary.json',result)
        binding=dict(id=CID,revision=2,previous_revision=1,kind=candidate['kind'],basis=candidate['basis'],status='VERIFIED',review_state='CLEAR',statement=candidate['statement'],scope=candidate['scope']['description'],assumptions=candidate['assumptions'],dependencies=candidate['dependencies'],created_at=candidate['created_at'],updated_at=stamp,verifier='/root/state_literature_audit',method='Independent raw integer N/G/R reconstruction; column denominator clearing; all integer congruence entries, literal unit-upper determinant and direct nullvectors. No producer imports or elimination replay.',inputs_sha256=INPUTS,evidence_sha256={**outputs,(out/'summary.json').relative_to(ROOT).as_posix():hashlib.sha256((out/'summary.json').read_bytes()).hexdigest()},revision_impact=dict(statement_changed=False,scope_changed=False,assumptions_changed=False,dependencies_changed=False,reason='Independent verification added to preserved producer-only candidate r1; no mathematical expansion.',candidate_snapshot=SNAP,candidate_snapshot_sha256=PINS[SNAP]),shared_components=['Python standard-library exact integers/rational parsing and PyYAML metadata parsing.','Prior block gate supplies complete population coverage; raw support/count data are authenticated premises.','Saved transforms are candidate witnesses, verified directly; producer shears/positive-result flag are not premises.'],controls=[calibration,dict(corruptions_rejected=corruptions)],limitations=['Necessary PSD/rank result only: no simultaneous factor or target existence, exclusion or residual completion.','Exactly792 canonical survivor profiles; previous three-profile PSD gate does not supply this new census.','No native solver or proof replay performed and no ledger status edited by reviewer.'],artifact_availability='LOCAL_ONLY')
        save(out/'claim_binding.json',binding);print(json.dumps({k:result[k]for k in ['status','canonical_profiles','rank_counts','congruence_entries','elapsed_seconds']}))
    except Exception as e:save(out/'failure.json',dict(error=repr(e),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-started));raise

if __name__=='__main__':main()
