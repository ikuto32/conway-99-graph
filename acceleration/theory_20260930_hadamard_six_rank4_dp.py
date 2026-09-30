"""Candidate exact marginal DP for nine six-group rank-four kernels."""
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
CAND=B/'20260930_hadamard_six_exception_census/remaining_candidates.json'
CENSUS=B/'20260930_hadamard_six_exception_census/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',CAND:'b0829ec669dd63d1d894c66389e3210b6ecc937edd7e003f2d0df9413f0ba5b1',CENSUS:'42add93a6d929e244aa0f32d16083beabc47cc0f02fedccff33280131383b74f'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def determinant(a):
    if not a:return 1
    if len(a)==1:return a[0][0]
    return sum((-1)**j*a[0][j]*determinant([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))
def domain(groups,projection):
    size=len(groups);H=[[1]*size]+[[int(a in g) for g in groups] for a in range(12)];records=[]
    for a in range(12):
        incident=[i for i,g in enumerate(groups) if a in g];vectors=[]
        for values in product(range(-1,3),repeat=len(incident)):
            v=[0]*size
            for i,x in zip(incident,values):v[i]=x
            if all(sum(x*y for x,y in zip(row,v))==0 for row in H):vectors.append(tuple(v))
        lookup=set(vectors);choices=[]
        for v0 in vectors:
            for v1 in vectors:
                v2=tuple(-x-y for x,y in zip(v0,v1))
                if v2 not in lookup:continue
                activity=sum(1<<i for i in range(size) if v0[i] or v1[i] or v2[i])
                choices.append(dict(fibres=[v0,v1,v2],projection=[v[p] for v in (v0,v1) for p in projection],activity_mask=activity))
        need(any(not c['activity_mask'] for c in choices),'zero local profile included')
        records.append(dict(coordinate=a,incident_groups=incident,integer_kernel_vectors=vectors,choices=choices))
    return H,records
def validate_witness(groups,H,records,path,expected_mask):
    size=len(groups);total=[[0]*size for _ in range(3)];activity=0
    for a,index in enumerate(path):
        profile=records[a]['choices'][index]['fibres'];need(all(sum(profile[f][i] for f in range(3))==0 for i in range(size)),'local fibre sum')
        for f in range(3):
            v=profile[f];need(all((-1<=v[i]<=2) if a in groups[i] else v[i]==0 for i in range(size)),'literal incident count bounds');need(all(sum(x*y for x,y in zip(row,v))==0 for row in H),'literal global kernel')
            for i in range(size):total[f][i]+=v[i]
        activity|=sum(1<<i for i in range(size) if any(profile[f][i] for f in range(3)))
    need(all(x==0 for row in total for x in row),'global group-fibre quota');need(activity==expected_mask,'exact group activity');return dict(total_group_fibre_deviations=total,activity_mask=activity)
def advance(dp,choices,deadline):
    result={};transitions=0
    for pos,(state,(count,path)) in enumerate(sorted(dp.items())):
        if pos%2048==0 and time.monotonic()>=deadline:return None,transitions
        for index,c in enumerate(choices):
            dest=tuple(x+y for x,y in zip(state[:-1],c['projection']))+(state[-1]|c['activity_mask'],)
            if dest in result:old,first=result[dest];result[dest]=(old+count,first)
            else:result[dest]=(count,path+(index,))
            transitions+=1
    return result,transitions
def dump_states(p,dp):
    with p.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as stream:
            for state,(count,path) in sorted(dp.items()):stream.write((json.dumps([state,count,path],separators=(',',':'))+'\n').encode())
def load_states(p):
    with gzip.open(p,'rt',encoding='utf-8') as stream:return {tuple(s):(n,tuple(path)) for s,n,path in map(json.loads,stream)}
def controls(allgroups):
    groups=[allgroups[i] for i in (0,7,9,19)];H,records=domain(groups,[0]);dp={(0,0,0):(1,())}
    for row in records:dp,_=advance(dp,row['choices'],float('inf'))
    need(dp[(0,0,15)][0]==6 and dp[(0,0,0)][0]==1,'literal four-circuit six positive profiles')
    path=dp[(0,0,15)][1];checked=validate_witness(groups,H,records,path,15);bad=json.loads(json.dumps(records));a=next(i for i,j in enumerate(path) if records[i]['choices'][j]['activity_mask']);bad[a]['choices'][path[a]]['fibres'][0][0]+=1
    rejected=[]
    for name,rec,mask in [('changed_local_count',bad,15),('wrong_activity',records,7)]:
        try:validate_witness(groups,H,rec,path,mask)
        except ValueError:rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    broken=list(path);broken[a]=next(i for i,c in enumerate(records[a]['choices']) if not c['activity_mask'])
    try:validate_witness(groups,H,records,broken,15)
    except ValueError:rejected.append('uncancelled_global_quota')
    else:raise ValueError('uncancelled profile accepted')
    outside=next(i for i in range(12) if i not in groups[0]);bad2=json.loads(json.dumps(records));bad2[outside]['choices'][path[outside]]['fibres'][0][0]=1;bad2[outside]['choices'][path[outside]]['fibres'][1][0]=-1
    try:validate_witness(groups,H,bad2,path,15)
    except ValueError:rejected.append('off_support_deviation')
    else:raise ValueError('off-support accepted')
    return dict(groups=[0,7,9,19],ordered_profiles_exactly_four=6,balanced_profiles=1,positive_choice_path=path,positive_check=checked,rejected_controls=rejected,scope='Linear/count necessary marginal controls, no complete factor.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--resume',type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();deadline=start+120
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'input pin '+key(path))
        inputs={key(path):digest for path,digest in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_six_rank4_dp_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        old={}
        if args.resume:
            prior=read(args.resume/'summary.json');need(prior['inputs_sha256']==inputs,'resume source/input identity')
            for c in prior['cases']:old[c['case']]=c
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limit_seconds=120,resume=None if args.resume is None else str(args.resume),scope='Marginal integer/count relaxation only.'))
        raw=read(RAW);allgroups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)));save(out/'controls.json',controls(allgroups));cases=read(CAND)['records'];need(len(cases)==9,'nine frozen cases');prepared=[]
        for ci,c in enumerate(cases):
            groups=[allgroups[g] for g in c['groups']];cert=c['certificate'];H=[[1]*6]+[[int(a in g) for g in groups] for a in range(12)];minor=[[H[i][j] for j in cert['minor_columns']] for i in cert['minor_rows']];need(cert['rank']==4 and minor==cert['minor'] and determinant(minor)==cert['determinant']!=0,'rank4 minor')
            basis=cert['integer_null_basis'];need(len(basis)==2 and all(all(sum(x*y for x,y in zip(row,v))==0 for row in H) for v in basis),'two literal null vectors')
            projection=next((list(pair) for pair in combinations(range(6),2) if determinant([[basis[j][i] for j in range(2)] for i in pair])),None);need(projection is not None,'injective coordinate projection');pm=[[basis[j][i] for j in range(2)] for i in projection];pd=determinant(pm);need(pd!=0 and pd!=pd+1,'projection determinant/corrupt control')
            H,records=domain(groups,projection);caseout=out/f'case_{ci:02d}';caseout.mkdir();domains=caseout/'domains.json';save(domains,dict(case=ci,groups=c['groups'],global_kernel_H=H,projection_group_indices=projection,projection_matrix=pm,projection_determinant=pd,records=records));prepared.append((ci,c,groups,H,records,domains,caseout))
        counts=[dict(case=ci,groups=c['groups'],integer_vector_counts=[len(r['integer_kernel_vectors']) for r in recs],fibre_profile_counts=[len(r['choices']) for r in recs],domain_path=key(dom),domain_sha256=sha(dom)) for ci,c,groups,H,recs,dom,caseout in prepared];save(out/'domain_inventory.json',dict(cases=counts));print(json.dumps({'domain_counts':counts}),flush=True)
        results=[];stopped=False
        for ci,c,groups,H,records,domains,caseout in tqdm(prepared,desc='Rank4 marginal quota DP',mininterval=1):
            dp={(0,0,0,0,0):(1,())};checkpoints=[];done=-1
            if ci in old:
                for cp in old[ci]['checkpoints']:
                    path=ROOT/cp['path'];need(sha(path)==cp['sha256'],'prior checkpoint pin');receipt=read(path);need(receipt['domain_sha256']==sha(domains),'resume domain bytes');need(sha(ROOT/receipt['state_path'])==receipt['state_sha256'],'resume states pin');checkpoints.append(cp)
                if checkpoints:receipt=read(ROOT/checkpoints[-1]['path']);dp=load_states(ROOT/receipt['state_path']);done=receipt['coordinate']
            for a in range(done+1,12):
                nextdp,transitions=advance(dp,records[a]['choices'],deadline)
                if nextdp is None:save(caseout/f'incomplete_layer_{a:02d}.json',dict(coordinate=a,completed_source_states_unknown=True,attempted_transitions=transitions,restart_from_coordinate=done+1,status='UNKNOWN_RESOURCE_LIMIT'));stopped=True;break
                dp=nextdp;done=a;states=caseout/f'states_{a:02d}.jsonl.gz';dump_states(states,dp);cp=caseout/f'checkpoint_{a:02d}.json';save(cp,dict(case=ci,coordinate=a,domain_sha256=sha(domains),states=len(dp),profile_sequence_count=sum(v[0] for v in dp.values()),transitions=transitions,state_path=key(states),state_sha256=sha(states)));checkpoints.append(dict(path=key(cp),sha256=sha(cp)))
            complete=done==11;target=(0,0,0,0,63);count=dp.get(target,(0,None))[0] if complete else None;witness=None
            if complete and count:
                path=dp[target][1];witness=dict(choice_path=path,**validate_witness(groups,H,records,path,63));save(caseout/'first_witness.json',dict(groups=c['groups'],**witness))
            results.append(dict(case=ci,groups=c['groups'],complete=complete,completed_coordinate=done,checkpoints=checkpoints,exactly_six_marginal_profile_sequences=count,unknown_reason=None if complete else 'Declared cooperative allocation reached before a complete layer.',has_marginal_witness=bool(witness),status='COMPLETE' if complete else 'UNKNOWN_RESOURCE_LIMIT'));save(caseout/'summary.json',results[-1])
            if stopped:break
        summary=dict(status='CANDIDATE_SIX_RANK4_MARGINAL_DP_COMPLETE' if not stopped else 'CANDIDATE_SIX_RANK4_MARGINAL_DP_PARTIAL',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,cases=results,selected_cases=9,complete_cases=sum(c['complete'] for c in results),unattempted_cases=9-len(results),complete_empty_cases=sum(c['complete'] and c['exactly_six_marginal_profile_sequences']==0 for c in results),complete_nonempty_cases=sum(c['complete'] and c['exactly_six_marginal_profile_sequences']>0 for c in results),elapsed_seconds=time.monotonic()-start,independent_approval=False,native_solver_calls=0,target_resolution=False,scope='Necessary bounded integer marginal profiles only; no local triple/quadratic Gram/Ycap or actual factor feasibility.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','cases')}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
