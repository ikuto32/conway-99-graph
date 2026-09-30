"""Independent full 4^10 integer enumeration, not the producer free-coordinate path."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
import numpy as np
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';DATA=B/'20260930_hadamard_coordinate_marginal_domains'
RAW=B/'20260930_hadamard20_support/six_prism.json';SUMMARY=DATA/'summary.json'
PINS={SUMMARY:'3382d4f11eeba3259300ae0e8361b434afc671353e3a2a83823668de63b0410f',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def universe(n):
    labels=np.arange(4**n,dtype=np.int32)
    return ((labels[:,None]//(4**np.arange(n,dtype=np.int32))[None,:])%4-1).astype(np.int16)
def brute(m,u):
    good=np.all(u@np.asarray(m,dtype=np.int16).T==0,axis=1)
    return sorted(tuple(int(x) for x in row) for row in u[good])
def scalar_good(v,m):return all(-1<=x<=2 for x in v) and all(sum(x*y for x,y in zip(v,row))==0 for row in m)
def rational_rank(a):
    rows=[list(map(Fraction,row)) for row in a];rank=0
    for col in range(len(rows[0])):
        at=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if at is None:continue
        rows[rank],rows[at]=rows[at],rows[rank];pivot=rows[rank][col];rows[rank]=[x/pivot for x in rows[rank]]
        for i in range(rank+1,len(rows)):
            scale=rows[i][col]
            if scale:rows[i]=[x-scale*y for x,y in zip(rows[i],rows[rank])]
        rank+=1
        if rank==len(rows):break
    return rank
def check_certificate(m,c):
    r=[[Fraction(x) for x in row] for row in c['rref']];e=[[Fraction(x) for x in row] for row in c['left_transform']]
    nr,nc=len(m),len(m[0]);rank=c['rank'];piv=c['pivot_columns'];free=c['free_columns']
    need(len(r)==len(e)==nr and all(len(row)==nc for row in r) and all(len(row)==nr for row in e),'certificate dimensions')
    need(rational_rank(e)==nr,'invertible exact left transform')
    need([[sum(e[i][k]*m[k][j] for k in range(nr)) for j in range(nc)] for i in range(nr)]==r,'exact left-transform identity')
    need(piv==sorted(set(piv)) and free==[i for i in range(nc) if i not in piv] and len(piv)==rank,'pivot/free partition')
    need(all(r[i][j]==int(i==k) for k,j in enumerate(piv) for i in range(nr)),'identity pivot columns')
    need(all(all(x==0 for x in row) for row in r[rank:]) and all(all(r[i][j]==0 for j in range(p)) for i,p in enumerate(piv)),'reduced echelon rows')
    basis=[[Fraction(x) for x in row] for row in c['kernel_basis']]
    need(len(basis)==nc-rank and all(len(v)==nc for v in basis),'complete null basis dimensions')
    need(rational_rank(basis)==nc-rank and all(all(sum(x*y for x,y in zip(row,v))==0 for row in m) for v in basis),'exact complete independent null basis')
    return r,piv,free
def expected_choices(vectors,incident):
    index={v:i for i,v in enumerate(vectors)};answer=[]
    for i,v0 in enumerate(vectors):
        for j,v1 in enumerate(vectors):
            v2=tuple(-a-b for a,b in zip(v0,v1))
            if v2 not in index:continue
            local=[v0,v1,v2];full=[[0]*20 for _ in range(3)]
            for f in range(3):
                for k,g in enumerate(incident):full[f][g]=local[f][k]
            counts=[[full[f][g]+int(g in incident) for f in range(3)] for g in range(20)]
            mask=sum(1<<g for g in range(20) if any(full[f][g] for f in range(3)))
            answer.append(dict(index=len(answer),vector_indices=[i,j,index[v2]],full20_deviations=full,incident_group_count_signature=[counts[g] for g in incident],full20_count_signature=counts,activity_mask=mask))
    return answer
def check_vectors(record,actual,incident,free):
    expected=[]
    for i,v in enumerate(actual):
        full=[0]*20
        for g,x in zip(incident,v):full[g]=x
        expected.append(dict(index=i,local_vector=list(v),full20_vector=full,incident_counts=[x+1 for x in v],free_values=[v[j] for j in free]))
    need(record==expected,'complete independently enumerated vectors and literal embeddings')
def controls():
    tiny=universe(3);need(len({tuple(v) for v in tiny})==64,'base4 vector universe bijection')
    for bits in product((0,1),repeat=9):
        m=[list(bits[3*i:3*i+3]) for i in range(3)]
        need(brute(m,tiny)==[v for v in product(range(-1,3),repeat=3) if scalar_good(v,m)],'512 scalar/array complete controls')
    m=[[1,1,0]];v=brute(m,tiny);need((1,-1,2) in v and (0,0,0) in v,'known bounded kernel positives');rejected=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,IndexError,KeyError):rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    for name,bad in [('bound',[3,-3,0]),('kernel',[1,1,0])]:reject(name,lambda bad=bad:need(scalar_good(bad,m),'invalid vector'))
    incident=[0,4,9];free=[1,2];rows=[]
    for i,x in enumerate(v):
        full=[0]*20
        for g,a in zip(incident,x):full[g]=a
        rows.append(dict(index=i,local_vector=list(x),full20_vector=full,incident_counts=[a+1 for a in x],free_values=[x[j] for j in free]))
    check_vectors(rows,v,incident,free)
    for name,alter in [('missing_vector',lambda x:x.pop()),('duplicated_vector',lambda x:x.append(x[0])),('off_support',lambda x:x[0]['full20_vector'].__setitem__(2,1)),('wrong_count',lambda x:x[0]['incident_counts'].__setitem__(0,4))]:
        bad=deepcopy(rows);alter(bad);reject(name,lambda bad=bad:check_vectors(bad,v,incident,free))
    choices=expected_choices(v,incident);need(choices,'local ordered triple positives');bad=deepcopy(choices);bad[0]['full20_deviations'][0][0]+=1;reject('changed_three_fibre_tuple',lambda:need(bad==expected_choices(v,incident),'complete triple equality'))
    return dict(binary_3x3_matrices=512,each_literal_vector_universe=64,known_positive_vectors=[[1,-1,2],[0,0,0]],synthetic_ordered_profiles=len(choices),corruptions_rejected=rejected,controls_are_marginal_objects_not_target_factors=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic();pins={}
    def pin(p,want):
        need(sha(p)==want,'hash '+key(p));pins[key(p)]=want
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(SUMMARY)
        for field in ('inputs_sha256','outputs_sha256'):
            for name,h in summary[field].items():pin(ROOT/name,h)
        for p in (Path(__file__),ROOT/'docs/AUDIT_20260930_COORDINATE_MARGINAL_DOMAINS.md',ROOT/'uv.lock',ROOT/'pyproject.toml'):pin(p,sha(p))
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),numpy=np.__version__,inputs_sha256=pins,limit_seconds=180,complete_universe_per_coordinate=4**10,producer_imports=False))
        save(out/'controls.json',controls());raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][j]) for j in range(60)));H=[[1]*20]+[[int(a in g) for g in groups] for a in range(12)]
        need(read(DATA/'global_matrix.json')==dict(groups=[list(g) for g in groups],matrix=H),'global matrix from literal support');u=universe(10);records=[];trial_total=0;pair_total=0
        for a in tqdm(range(12),desc='Independent full4^10 marginal enumeration',mininterval=1):
            ref=summary['records'][a];path=ROOT/ref['path'];pin(path,ref['sha256']);d=read(path);incident=[i for i,g in enumerate(groups) if a in g];m=[[row[i] for i in incident] for row in H]
            need(d['coordinate']==a and len(incident)==10 and d['incident_groups']==incident and d['restricted_global_matrix']==m and d['complete'],'literal coordinate scope')
            r,piv,free=check_certificate(m,d['rref_certificate']);need(len(piv)==6 and len(free)==4,'rank and dimension');actual=brute(m,u);check_vectors(d['integer_vectors'],actual,incident,free)
            trials=d['free_projection_trials'];need([t['free_values'] for t in trials]==[list(x) for x in product(range(-1,3),repeat=4)],'complete256 projected trials')
            accepted=[]
            for t in trials:
                v=list(map(Fraction,t['recovered_rational_vector']));need(len(v)==10 and [v[j] for j in free]==list(map(Fraction,t['free_values'])) and all(sum(x*y for x,y in zip(row,v))==0 for row in m),'literal trial kernel/free identity')
                non=[i for i,x in enumerate(v) if x.denominator!=1];bad=[i for i,x in enumerate(v) if x< -1 or x>2]
                need(t['nonintegral_positions']==non and t['out_of_bounds_positions']==bad and t['accepted']==(not non and not bad),'trial exact acceptance')
                if t['accepted']:accepted.append(tuple(map(int,v)))
            need(sorted(accepted)==actual,'projection trials cover independently brute-forced domain');wanted=expected_choices(actual,incident);need(d['ordered_three_fibre_choices']==wanted,'all ordered triples and embeddings')
            hist=dict(sorted(Counter(x['activity_mask'].bit_count() for x in wanted).items()));need(d['activity_size_histogram']=={str(k):v for k,v in hist.items()},'activity counts')
            need(d['vector_count']==ref['vector_count']==len(actual) and d['choice_count']==ref['choice_count']==len(wanted) and d['ordered_pair_trials']==ref['ordered_pair_trials']==len(actual)**2,'actual totals')
            cp=read(DATA/f'checkpoint_{a:02d}.json');need(cp['completed_coordinates']==a+1 and cp['records']==summary['records'][:a+1] and cp['inputs_sha256']==summary['inputs_sha256'],'immutable completed prefix')
            records.append(dict(coordinate=a,full_vectors_checked=4**10,integer_vectors=len(actual),ordered_pairs=len(actual)**2,ordered_fibre_profiles=len(wanted)));trial_total+=len(trials);pair_total+=len(actual)**2;need(time.monotonic()-started<180,'audit allocation')
        need(summary['completed_coordinates']==12 and summary['projection_trials']==trial_total==3072 and summary['ordered_pair_trials']==pair_total==7561,'complete summary totals');need(sum(x['integer_vectors'] for x in records)==summary['total_integer_vectors']==291 and sum(x['ordered_fibre_profiles'] for x in records)==summary['total_ordered_fibre_choices']==2226,'total checked finite domains')
        # Certificate corruption controls use a genuine raw coordinate after successful checking.
        corrupt=[];m=read(DATA/'coordinate_00.json')['restricted_global_matrix'];c=read(DATA/'coordinate_00.json')['rref_certificate']
        for name,field in [('left_transform','left_transform'),('reduced_matrix','rref'),('null_basis','kernel_basis')]:
            bad=deepcopy(c);bad[field][0][0]=str(Fraction(bad[field][0][0])+1)
            try:check_certificate(m,bad)
            except ValueError:corrupt.append(name)
            else:raise ValueError('certificate corruption accepted')
        save(out/'records.json',dict(coordinates=records,certificate_corruptions_rejected=corrupt));now=datetime.now(timezone.utc).isoformat();scope='Complete individual-coordinate integer/count relaxation on one fixed support, with arbitrary exception counts; no cross-coordinate coupling, local word-triple existence, full Gram factor or target graph.'
        shared=['Literal support and previously independently derived marginal equations.','Python integer/Fraction arithmetic and NumPy exact int16 matrix products; no producer imports or free-variable enumeration used for domain completeness.'];limits=[scope,'The291 vector and2226 profile totals count coordinate-specific domains; they are not globally compatible assignments.']
        binding=dict(id='C-FIXED-HADAMARD-COMPLETE-COORDINATE-MARGINAL-DOMAINS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For each of the12 coordinates of the pinned six-prism support, the complete ten-incident-group bounded integer kernel domain and all ordered three-fibre tuples summing to zero are exactly the saved tables. The coordinate-specific domains contain291 integer vectors in total and2226 ordered three-fibre profiles. Completeness was independently checked against all4^10 bounded vectors for every coordinate, with exact raw embeddings, count signatures and rank-six certificates.',scope=scope,assumptions=['Pinned literal support and the separately derived necessary integer marginal equations; deviations lie in[-1,2] on incident groups and vanish elsewhere.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],verifier='/root',producer='/root/eight_domain_audit',checking_method='Complete independent base4 enumeration in the original ten variables, exact scalar controls, all ordered vector pairs and rational certificate checks.',shared_components=shared,limitations=limits,artifact_hashes=pins,created_at=now,updated_at=now)
        save(out/'claim_binding.json',binding);result=dict(status='INDEPENDENT_COMPLETE_COORDINATE_MARGINAL_DOMAINS_PASS',timestamp=now,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},coordinates=12,full_bounded_vectors_checked=12*4**10,integer_vectors=291,ordered_pairs=pair_total,ordered_fibre_profiles=2226,records=records,scope=scope,shared_components=shared,limitations=limits,elapsed_seconds=time.monotonic()-started,target_resolution=False,native_calls=0)
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256','records')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
