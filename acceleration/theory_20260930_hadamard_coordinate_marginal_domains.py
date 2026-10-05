"""Candidate complete bounded integer marginal domains; no own approval."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time, traceback
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
MARGINAL=B/'20260930_independent_review/hadamard_few_exception_marginals/summary.json'
OLD=B/'20260930_hadamard_triplicate_counts/marginal_certificates.json'
OLDGATE=B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',MARGINAL:'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',OLDGATE:'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    with p.open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')

def reduction(matrix):
    m=len(matrix);n=len(matrix[0]);A=[[Fraction(x)for x in r]for r in matrix];E=[[Fraction(i==j)for j in range(m)]for i in range(m)];pivots=[];row=0
    for column in range(n):
        pivot=next((i for i in range(row,m)if A[i][column]),None)
        if pivot is None:continue
        A[row],A[pivot]=A[pivot],A[row];E[row],E[pivot]=E[pivot],E[row]
        scale=A[row][column];A[row]=[x/scale for x in A[row]];E[row]=[x/scale for x in E[row]]
        for i in range(m):
            if i!=row and A[i][column]:
                scale=A[i][column];A[i]=[x-scale*y for x,y in zip(A[i],A[row])];E[i]=[x-scale*y for x,y in zip(E[i],E[row])]
        pivots.append(column);row+=1
        if row==m:break
    need([[sum(E[i][k]*matrix[k][j]for k in range(m))for j in range(n)]for i in range(m)]==A,'literal row-transform identity')
    free=[j for j in range(n)if j not in pivots]
    basis=[]
    for f in free:
        v=[Fraction(0)]*n;v[f]=1
        for i,p in enumerate(pivots):v[p]=-A[i][f]
        need(all(sum(x*y for x,y in zip(r,v))==0 for r in matrix),'rational kernel basis')
        basis.append(v)
    return dict(rank=len(pivots),pivot_columns=pivots,free_columns=free,rref=[[str(x)for x in r]for r in A],left_transform=[[str(x)for x in r]for r in E],kernel_basis=[[str(x)for x in v]for v in basis]),A

def enumerate_vectors(matrix):
    certificate,R=reduction(matrix);n=len(matrix[0]);free=certificate['free_columns'];pivots=certificate['pivot_columns'];trials=[];vectors=[]
    for assignment in product(range(-1,3),repeat=len(free)):
        v=[Fraction(0)]*n
        for j,value in zip(free,assignment):v[j]=value
        for i,j in enumerate(pivots):v[j]=-sum(R[i][f]*v[f]for f in free)
        nonintegral=[j for j,x in enumerate(v)if x.denominator!=1]
        outbounds=[j for j,x in enumerate(v)if x < -1 or x > 2]
        accepted=not(nonintegral or outbounds)
        if accepted:
            iv=tuple(map(int,v));need(all(sum(x*y for x,y in zip(r,iv))==0 for r in matrix),'accepted literal kernel vector');vectors.append(iv)
        trials.append(dict(free_values=list(assignment),recovered_rational_vector=list(map(str,v)),accepted=accepted,nonintegral_positions=nonintegral,out_of_bounds_positions=outbounds))
    vectors.sort();need(len(vectors)==len(set(vectors)),'injective full enumeration')
    return certificate,trials,vectors

def validate_vector(matrix,v):
    need(len(v)==len(matrix[0])and all(type(x)is int and -1<=x<=2 for x in v),'bounded integer vector')
    need(all(sum(x*y for x,y in zip(row,v))==0 for row in matrix),'literal marginal equations')

def controls():
    matrices=[[[1,1,1]],[[1,0,0],[0,1,0],[0,0,1]],[[0,0,0]],[[1,2,0],[0,1,1]],[[1,1,1,1],[1,0,1,0]]];checks=[]
    for matrix in matrices:
        cert,trials,vectors=enumerate_vectors(matrix)
        brute=[v for v in product(range(-1,3),repeat=len(matrix[0]))if all(sum(x*y for x,y in zip(row,v))==0 for row in matrix)]
        need(vectors==brute,'small full brute-force agreement');checks.append(dict(matrix=matrix,rank=cert['rank'],free_trials=len(trials),full_trials=4**len(matrix[0]),vectors=[list(x)for x in vectors]))
    need((1,-1,0)in enumerate_vectors([[1,1,1]])[2],'nonzero positive kernel')
    rejected=[]
    for name,v in [('kernel',[1,0,0]),('bounds',[3,-3,0]),('Boolean',[True,-1,0]),('shape',[0,0])]:
        try:validate_vector([[1,1,1]],v)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted corrupted vector '+name)
    return dict(positive_controls=checks,rejected_corruptions=rejected,scope='Producer calibration only, no independent approval.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    try:
        for p,h in PINS.items():need(sha(p)==h,'frozen input '+key(p));pins[key(p)]=h
        oldgate=read(OLDGATE);need(sha(OLD)==oldgate['inputs_sha256'][key(OLD)],'old first-witness artifact identity');pins[key(OLD)]=sha(OLD)
        previous=['acceleration/theory_20260930_hadamard_triplicate_counts.py','acceleration/theory_20260930_hadamard_triplicate_counts_spec.md','acceleration/theory_20260930_hadamard_six_rank4_dp.py','acceleration/theory_20260930_hadamard_seven_rank5_dp.py']
        for name in previous+[key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md')),'uv.lock','pyproject.toml']:pins[name]=sha(ROOT/name)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limits=dict(seconds=60,coordinates=12,maximum_free_trials_per_coordinate=256,maximum_pair_trials_per_coordinate=65536,native_calls=0),independent_approval=False))
        save(out/'overlap_review.json',dict(inspected_sources=previous,findings=['triplicate_counts explicitly breaks at first nonzero {-1,0,1}^10 kernel witness; no complete bounded domain.','six_rank4_dp and seven_rank5_dp enumerate only nominated6/7-group subsets, not all20 arbitrary exceptions.'],search_coverage='Current Hadamard-labelled Python/spec sources inspected by rg and direct reads; not a claim about every historical branch or external literature.',new_population='All bounded ten-incident-group integer vectors for all12 coordinates, and their complete ordered zero-sum fibre triples.'))
        save(out/'controls.json',controls())
        raw=read(RAW);groups=list(dict.fromkeys(tuple(i for i in range(12)if raw['L'][i][d])for d in range(60)));need(len(groups)==20,'twenty raw groups')
        H=[[1]*20]+[[int(a in g)for g in groups]for a in range(12)]
        save(out/'global_matrix.json',dict(groups=[list(g)for g in groups],matrix=H))
        previous_matrices=read(OLD);old_records=previous_matrices['records']if isinstance(previous_matrices,dict)and'records'in previous_matrices else previous_matrices['marginals']if isinstance(previous_matrices,dict)and'marginals'in previous_matrices else previous_matrices
        records=[];complete=True
        for a in tqdm(range(12),desc='Complete coordinate marginal domains',mininterval=1):
            if time.perf_counter()-start>=60:complete=False;break
            incident=[g for g,s in enumerate(groups)if a in s];matrix=[[r[g]for g in incident]for r in H];need(len(incident)==10,'ten incident groups')
            cert,trials,vectors=enumerate_vectors(matrix);need(cert['rank']==6 and len(cert['free_columns'])==4 and len(trials)==256,'rank6/free4 finite complete domain')
            lookup={v:i for i,v in enumerate(vectors)};need((0,)*10 in lookup,'balanced zero included')
            old=old_records[a];need(old['coordinate']==a and old['groups']==incident and tuple(old['kernel_witness'])in lookup,'previous first witness included')
            vector_records=[]
            for i,v in enumerate(vectors):
                full=[0]*20
                for g,x in zip(incident,v):full[g]=x
                need(all(sum(x*y for x,y in zip(row,full))==0 for row in H),'full20 literal marginal embedding')
                vector_records.append(dict(index=i,local_vector=list(v),full20_vector=full,incident_counts=[1+x for x in v],free_values=[v[j]for j in cert['free_columns']]))
            choices=[];attempted_pairs=0
            for i,v0 in enumerate(vectors):
                if time.perf_counter()-start>=60:raise TimeoutError('pair enumeration reached frozen60second allocation; current coordinate incomplete')
                for j,v1 in enumerate(vectors):
                    attempted_pairs+=1;v2=tuple(-x-y for x,y in zip(v0,v1))
                    if v2 not in lookup:continue
                    indices=[i,j,lookup[v2]];full=[vector_records[k]['full20_vector']for k in indices];counts=[[1+full[f][g]if g in incident else 0 for f in range(3)]for g in range(20)]
                    need(all(sum(counts[g])==(3 if g in incident else 0)and all(0<=x<=3 for x in counts[g])for g in range(20)),'all exact fibre count signatures')
                    choices.append(dict(index=len(choices),vector_indices=indices,full20_deviations=full,incident_group_count_signature=[counts[g]for g in incident],full20_count_signature=counts,activity_mask=sum(1<<g for g in range(20)if any(full[f][g]for f in range(3)))))
            path=out/f'coordinate_{a:02d}.json';payload=dict(coordinate=a,incident_groups=incident,restricted_global_matrix=matrix,row_labels=['leading_one',*range(12)],rref_certificate=cert,free_projection_trials=trials,integer_vectors=vector_records,ordered_three_fibre_choices=choices,vector_count=len(vectors),ordered_pair_trials=attempted_pairs,choice_count=len(choices),activity_size_histogram=dict(Counter(x['activity_mask'].bit_count()for x in choices)),complete=True)
            save(path,payload);records.append(dict(coordinate=a,path=key(path),sha256=sha(path),rank=6,free_dimension=4,free_projection_trials=256,vector_count=len(vectors),ordered_pair_trials=attempted_pairs,choice_count=len(choices),bytes=path.stat().st_size))
            save(out/f'checkpoint_{a:02d}.json',dict(completed_coordinates=a+1,records=records,inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start))
        summary=dict(status='CANDIDATE_COMPLETE_COORDINATE_INTEGER_MARGINAL_DOMAINS'if complete else'CANDIDATE_COORDINATE_INTEGER_MARGINAL_PREFIX',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},records=records,completed_coordinates=len(records),full_coordinate_population=12,full_vector_universe_per_coordinate=4**10,projection_trials=sum(r['free_projection_trials']for r in records),ordered_pair_trials=sum(r['ordered_pair_trials']for r in records),total_integer_vectors=sum(r['vector_count']for r in records),total_ordered_fibre_choices=sum(r['choice_count']for r in records),elapsed_seconds=time.perf_counter()-start,scope='Complete individual coordinate marginal domains and ordered three-fibre count profiles on fixed support, arbitrary exception counts. No coupling between coordinates, no local word triples or full factor.',independent_approval=False,target_resolution=False,native_calls=0,artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in('inputs_sha256','outputs_sha256','records')}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start));raise

if __name__=='__main__':main()
