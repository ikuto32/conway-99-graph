"""Exact necessary eight-group census; discovery, not independent approval."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, islice, product
from math import comb
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
import theory_20260930_hadamard_six_exception_census as base
ROOT=base.ROOT; RAW=base.RAW; POPULATION=comb(20,8); CHUNK=2000
PINS=dict(base.PINS)
PINS[Path(base.__file__)]= 'ac4e0a273dbbadbfaa4828dee2d8130582e1dd371f35f7ef2ec4d8203bc35d93'
need=base.need;sha=base.sha;key=base.key;save=base.save

def classify(cert,common_count):
    rank=cert['rank'];basis=cert['integer_null_basis']
    if rank==8:return 'EXCLUDED_FULL_COLUMN_RANK',list(range(8))
    forced=[i for i in range(8) if all(v[i]==0 for v in basis)]
    if forced:return 'EXCLUDED_FORCED_BALANCED_GROUP',forced
    if rank==7:
        c=basis[0]
        need(sum(c)==0 and all(c),'primitive full-support augmented kernel')
        if max(map(abs,c))>=2:return 'EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT',[]
        need(all(abs(x)==1 for x in c),'remaining primitive coefficients are signs')
        if common_count<=1:return 'EXCLUDED_ONE_DIMENSIONAL_SMALL_COMMON_SUPPORT',[]
        return 'RETAINED_ONE_DIMENSIONAL_SIGN_KERNEL',[]
    return 'RETAINED_HIGHER_DIMENSION_KERNEL',[]

def controls():
    old=base.controls()
    columns=[(0,)*6,*[tuple(int(i==j) for i in range(6)) for j in range(6)],(1,)*6]
    odd=[[1]*8]+[[v[j] for v in columns] for j in range(6)]
    oc=base.certificate(odd);need(oc['rank']==7 and classify(oc,0)[0]=='EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT','large coefficient control')
    full=[[int(i==j) for j in range(8)] for i in range(8)]
    need(classify(base.certificate(full),0)[0]=='EXCLUDED_FULL_COLUMN_RANK','full rank control')
    cube=list(product(range(2),repeat=3))
    retained=[[1]*8]+[[v[j] for v in cube] for j in range(3)]
    rc=base.certificate(retained);need(rc['rank']==4 and classify(rc,0)[0]=='RETAINED_HIGHER_DIMENSION_KERNEL','retained kernel control')
    columns=[tuple(v)+(0,) for v in cube[:7]]+[(0,0,0,1)]
    zero=[[1]*8]+[[v[j] for v in columns] for j in range(4)]
    zc=base.certificate(zero);need(classify(zc,0)[0]=='EXCLUDED_FORCED_BALANCED_GROUP' and classify(zc,0)[1]==[7],'forced balanced coordinate')
    cycle=[[1]*8]+[[int(j in (i,(i+1)%8)) for j in range(8)] for i in range(8)]
    cc=base.certificate(cycle);need(cc['rank']==7,'sign kernel rank')
    for common in (0,1):need(classify(cc,common)[0]=='EXCLUDED_ONE_DIMENSIONAL_SMALL_COMMON_SUPPORT','common support exclusion')
    need(classify(cc,2)[0]=='RETAINED_ONE_DIMENSIONAL_SIGN_KERNEL','sign kernel retained at two common coordinates')
    b=base.bezout(oc['integer_null_basis'][0]);bad=oc['integer_null_basis'][0].copy();bad[0]+=1
    need(any(sum(x*y for x,y in zip(row,bad)) for row in odd),'corrupted null rejected')
    need(base.det(oc['minor'])!=oc['determinant']+1,'corrupt minor rejected')
    return dict(shared_rank_controls=old,large_coefficient_kernel=oc,retained=rc,forced_balanced=zc,sign_kernel=cc,large_coefficient_Bezout=b,new_corruptions_rejected=2,independent_approval=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume-checkpoint',type=Path);ap.add_argument('--resume-checkpoint-sha256');args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT),'output inside repository');out.mkdir(parents=True,exist_ok=False)
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'frozen input '+key(path))
        inputs={key(p):s for p,s in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_suffix('.md').with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),inputs_sha256=inputs,limits=dict(enumeration_seconds=240,chunk_subsets=CHUNK,native_calls=0),population=POPULATION))
        save(out/'controls.json',controls())
        raw=json.loads(RAW.read_bytes());groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)));need(len(groups)==20,'twenty distinct supports')
        H=[[1]*20]+[[int(a in group) for group in groups] for a in range(12)]
        save(out/'global_marginal_matrix.json',dict(groups=groups,matrix=H,global_certificate=base.certificate(H)))
        chunks=[];completed=0;rank_counts=Counter();class_counts=Counter();remaining=[]
        if args.resume_checkpoint:
            need(args.resume_checkpoint_sha256 and sha(args.resume_checkpoint)==args.resume_checkpoint_sha256,'explicit resume pin')
            state=json.loads(args.resume_checkpoint.read_bytes());need(state['inputs_sha256']==inputs and state['population']==POPULATION,'same source/population')
            chunks=state['chunks'];expected=iter(combinations(range(20),8))
            for chunk in chunks:
                path=ROOT/chunk['path'];need(sha(path)==chunk['sha256'],'prior chunk hash')
                count=0
                with gzip.open(path,'rt',encoding='utf-8') as stream:
                    for line in stream:
                        row=json.loads(line);need(row['index']==completed and row['groups']==list(next(expected)),'exact completed prefix')
                        completed+=1;count+=1;rank_counts[row['certificate']['rank']]+=1;class_counts[row['classification']]+=1
                        if row['classification'].startswith('RETAINED'):remaining.append(row)
                need(count==chunk['count'],'prior chunk count')
            need(completed==state['completed'],'checkpoint prefix length')
        else:need(args.resume_checkpoint_sha256 is None,'resume hash requires path')
        sequence=islice(combinations(range(20),8),completed,None);start=time.monotonic();bar=tqdm(total=POPULATION,initial=completed,desc='Eight-group exact ranks',mininterval=1)
        stopped=False
        while completed<POPULATION:
            first=completed;path=out/f'subsets_{first:05d}.jsonl.gz'
            with path.open('xb') as rawstream:
                with gzip.GzipFile(filename='',fileobj=rawstream,mode='wb',mtime=0) as stream:
                    for ids in islice(sequence,CHUNK):
                        common=sorted(set.intersection(*(set(groups[g]) for g in ids)))
                        cert=base.certificate([[row[g] for g in ids] for row in H]);category,forced=classify(cert,len(common))
                        row=dict(index=completed,groups=list(ids),common_coordinates=common,certificate=cert,classification=category,forced_balanced_local_positions=forced)
                        if cert['rank']==7:row['primitive_Bezout']=base.bezout(cert['integer_null_basis'][0])
                        stream.write((json.dumps(row,separators=(',',':'))+'\n').encode());completed+=1;rank_counts[cert['rank']]+=1;class_counts[category]+=1
                        if category.startswith('RETAINED'):remaining.append(row)
                        bar.update(1)
            chunks.append(dict(path=key(path),sha256=sha(path),count=completed-first,first_index=first))
            save(out/f'checkpoint_{completed:05d}.json',dict(status='EIGHT_GROUP_EXACT_CENSUS_PREFIX',inputs_sha256=inputs,population=POPULATION,completed=completed,chunks=chunks,elapsed_enumeration_seconds=time.monotonic()-start))
            if time.monotonic()-start>=240 and completed<POPULATION:stopped=True;break
        bar.close();save(out/'remaining_candidates.json',dict(count=len(remaining),records=remaining,scope='Necessary subsets only; none asserted feasible.'))
        summary=dict(status='CANDIDATE_EIGHT_EXCEPTION_CENSUS_PREFIX' if stopped else 'CANDIDATE_COMPLETE_EIGHT_EXCEPTION_CENSUS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},population=POPULATION,completed=completed,rank_counts=dict(sorted(rank_counts.items())),class_counts=dict(sorted(class_counts.items())),remaining_necessary_subsets=len(remaining),elapsed_enumeration_seconds=time.monotonic()-start,scope='Exactly eight exceptional groups on one literal support; necessary Gram marginals only.',independent_approval=False,target_resolution=False,native_solver_calls=0,artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
