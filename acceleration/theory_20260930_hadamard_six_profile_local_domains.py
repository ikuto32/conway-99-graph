"""Candidate complete local-domain filter of labelled six-exception marginals."""
from collections import defaultdict,Counter
from datetime import datetime,timezone
from itertools import permutations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
DP=B/'20260930_hadamard_six_rank4_dp/summary.json'
LOCAL_GATE=B/'20260930_independent_review/hadamard_four_group_local_screen/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',DP:'e315a3261b2aee326142d1ad83ca828041b0f39907f54a5b51d4d11d33e7e53b',LOCAL_GATE:'ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def load_states(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:return {tuple(s):n for s,n,p in map(json.loads,f)}
def profile_path(records,layers):
    indices=[]
    for layer in layers:
        lookup=defaultdict(list)
        for state,count in layer.items():lookup[state[:-1]].append((state[-1],count))
        indices.append(lookup)
    def visit(a,state):
        if a<0:
            need(state==(0,0,0,0,0),'backtracking exact initial state');yield ();return
        total=0
        for choice_index,choice in enumerate(records[a]['choices']):
            previous=tuple(x-y for x,y in zip(state[:-1],choice['projection']))
            for activity,count in indices[a][previous]:
                if activity|choice['activity_mask']!=state[-1]:continue
                prior=previous+(activity,);total+=count
                for path in visit(a-1,prior):yield path+(choice_index,)
        need(total==layers[a+1][state],'every predecessor count matches saved DP state')
    return visit(11,(0,0,0,0,63))
def verify_profile(group_ids,groups,H,records,path):
    deviations=[records[a]['choices'][path[a]]['fibres'] for a in range(12)]
    totals=[[0]*6 for _ in range(3)];activity=0
    for a,profile in enumerate(deviations):
        need(all(sum(profile[f][i] for f in range(3))==0 for i in range(6)),'local fibre sum')
        for f,v in enumerate(profile):
            need(all((-1<=v[i]<=2) if a in groups[i] else v[i]==0 for i in range(6)),'support and count bounds');need(all(sum(x*y for x,y in zip(row,v))==0 for row in H),'literal kernel')
            for i,x in enumerate(v):totals[f][i]+=x
        activity|=sum(1<<i for i in range(6) if any(profile[f][i] for f in range(3)))
    need(activity==63 and all(x==0 for row in totals for x in row),'exactly six active with global quotas')
    return deviations,digest(dict(groups=group_ids,deviations=deviations))
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,d in PINS.items():need(sha(path)==d,'input pin '+key(path))
        inputs={key(p):d for p,d in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_six_profile_local_domains_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(seconds=120,native_solver_calls=0),scope='Initial domains already impose within-groupYcaps; no cross-group tests.'))
        raw=read(RAW);local=read(LOCAL);dp=read(DP);words=local['words'];triples=local['survivors'];need(len(triples)==31110,'complete local catalogue');catalog=defaultdict(list)
        for index,tri in enumerate(triples):catalog[tuple(sum(words[w][pos]==f for w in tri) for pos in range(6) for f in range(3))].append(index)
        balanced=(1,)*18;need(len(catalog[balanced])==150,'balanced150 positive');unbalanced=next((s,ids[0]) for s,ids in catalog.items() if s!=balanced);need(unbalanced[1] in catalog[unbalanced[0]],'actual unbalanced positive')
        corrupted=list(balanced);corrupted[0]+=1;need(not catalog[tuple(corrupted)],'changed count sum rejected');corrupted[0]=4;need(not catalog[tuple(corrupted)],'count4 rejected')
        save(out/'controls.json',dict(balanced_domain_count=150,unbalanced_count_signature=unbalanced[0],unbalanced_local_survivor_index=unbalanced[1],rejected_controls=['changed_coordinate_count_sum','count4'],scope='Local triple positives only.'))
        allgroups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)));domainout=out/'domains';domainout.mkdir();saved_domains={};case_results=[];all_hashes=set();canonical=Counter();total=excluded=0
        with (out/'profiles.jsonl.gz').open('xb') as rawstream:
            with gzip.GzipFile(filename='',mode='wb',fileobj=rawstream,mtime=0) as stream:
                for case in tqdm(dp['cases'],desc='Six-exception labelled profiles',mininterval=1):
                    need(case['complete'],'no incomplete DPcase used')
                    expected=case['exactly_six_marginal_profile_sequences']
                    if not expected:continue
                    receipts=[];layers=[{(0,0,0,0,0):1}]
                    for cp in case['checkpoints']:
                        path=ROOT/cp['path'];need(sha(path)==cp['sha256'],'checkpoint pin');receipt=read(path);statepath=ROOT/receipt['state_path'];need(sha(statepath)==receipt['state_sha256'],'complete layer pin');receipts.append(receipt);layers.append(load_states(statepath))
                    need(len(layers)==13 and layers[-1].get((0,0,0,0,63))==expected,'complete final DPcount')
                    dompath=(ROOT/case['checkpoints'][0]['path']).parent/'domains.json';need(sha(dompath)==receipts[0]['domain_sha256'],'domain bytes');domain=read(dompath);records=domain['records'];groups=[allgroups[g] for g in case['groups']];H=domain['global_kernel_H']
                    paths=sorted(profile_path(records,layers));need(len(paths)==expected and len(set(paths))==expected,'complete unique backtracking')
                    removed=0;domain_hist=Counter();casehashes=[]
                    for pi,path in enumerate(paths):
                        dev,profilehash=verify_profile(case['groups'],groups,H,records,path);need(profilehash not in all_hashes,'globally unique labelled deviations');all_hashes.add(profilehash);casehashes.append(profilehash)
                        refs=[]
                        for side,g in enumerate(case['groups']):
                            signature=tuple(1+dev[a][f][side] for a in groups[side] for f in range(3));ids=catalog.get(signature,[])
                            if signature not in saved_domains:
                                domain_id=digest(list(signature));pathout=domainout/f'{domain_id}.json';save(pathout,dict(count_signature=list(signature),local_catalog_path=key(LOCAL),local_catalog_sha256=PINS[LOCAL],local_survivor_indices=ids,count=len(ids)));saved_domains[signature]=dict(path=key(pathout),sha256=sha(pathout),count=len(ids))
                            refs.append(dict(group=g,**saved_domains[signature]));domain_hist[len(ids)]+=1
                        empty=[r['group'] for r in refs if r['count']==0];removed+=bool(empty);excluded+=bool(empty);total+=1
                        images=[]
                        for perm in permutations(range(3)):
                            transformed=[[row[perm[f]] for f in range(3)] for row in dev];images.append(dict(fibre_pullback=list(perm),profile_sha256=digest(dict(groups=case['groups'],deviations=transformed))))
                        ch=min(x['profile_sha256'] for x in images);canonical[ch]+=1
                        record=dict(id=f"rank4_{case['case']:02d}_profile_{pi:04d}",rank4_case=case['case'],group_ids=case['groups'],choice_path=path,profile_sha256=profilehash,coordinate_fibre_deviations=dev,local_domains=refs,empty_groups=empty,retained_by_individual_local_domains=not empty,global_fibre_images=images,canonical_profile_sha256=ch,normalization_used_for_filtering=False)
                        stream.write((json.dumps(record,separators=(',',':'))+'\n').encode());need(time.monotonic()-start<120,'declared allocation')
                    save(out/f'case_{case["case"]:02d}_profile_hashes.json',dict(case=case['case'],profile_hashes=casehashes));result=dict(case=case['case'],groups=case['groups'],expected=expected,backtracked=len(paths),unique=len(casehashes),empty_local_domain_profiles=removed,retained_profiles=expected-removed,domain_size_histogram=dict(sorted(domain_hist.items())));case_results.append(result);save(out/f'case_{case["case"]:02d}_checkpoint.json',result)
        need(total==984 and len(all_hashes)==984,'entire frozen984 profile universe');need(all(x['profile_sha256'] in all_hashes for x in images),'last diagnostic action closure')
        save(out/'diagnostic_fibre_orbits.json',dict(canonical_hash_population=dict(sorted(canonical.items())),orbit_count=len(canonical),used_for_coverage_or_pruning=False,independent_general_normalization_review_required=True))
        summary=dict(status='CANDIDATE_COMPLETE_SIX_EXCEPTION_LOCAL_DOMAIN_FILTER',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},cases=case_results,labelled_profiles=984,completed_profiles=total,unique_profile_hashes=len(all_hashes),unique_local_count_domains=len(saved_domains),profiles_with_empty_local_domain=excluded,retained_profiles=total-excluded,diagnostic_fibre_orbits=len(canonical),fibre_orbit_sizes=dict(Counter(canonical.values())),independent_approval=False,native_solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start,scope='Marginal profiles filtered only by individual local triples with within-groupYcaps; retained is not simultaneous Gram/caps/factor feasibility.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256','cases')}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
