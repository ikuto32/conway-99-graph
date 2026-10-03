"""Candidate joint count master inventory, no mathematical solver/imported producer."""
from collections import defaultdict
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import argparse, copy, gzip, hashlib, json, platform, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'
GATE=B/'20260930_independent_review/coordinate_marginal_domains/summary.json'
SUMMARY=B/'20260930_hadamard_coordinate_marginal_domains/summary.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
LOCAL_GATE=B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json'
RAW=B/'20260930_hadamard20_support/six_prism.json'
SIX=B/'20260930_hadamard_six_profile_local_domains/profiles.jsonl.gz'
PINS={GATE:'9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39',SUMMARY:'3382d4f11eeba3259300ae0e8361b434afc671353e3a2a83823668de63b0410f',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',LOCAL_GATE:'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',SIX:'221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0'}

def need(ok,message):
    if not ok:raise ValueError(message)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def signature(words,triple):return tuple(sum(words[t][a]==f for t in triple) for a in range(6) for f in range(3))
def table_check(counts,groups,coordinates,signatures):
    need(len(counts)==12 and all(len(c)==20 for c in counts),'count shape')
    selected=[]
    for a in range(12):
        need(all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v) for v in counts[a]),'integer count bounds')
        choices=[x['full20_count_signature'] for x in coordinates[a]['ordered_three_fibre_choices']]
        need(counts[a] in choices,'complete coordinate domain membership')
        selected.append(choices.index(counts[a]))
    group_ids=[]
    for g,support in enumerate(groups):
        s=tuple(x for a in support for x in counts[a][g])
        need(all(sum(s[3*j+f] for j in range(6))==6 for f in range(3)),'group/fibre quota six')
        need(s in signatures,'local count signature membership')
        group_ids.append(signatures.index(s))
    return dict(coordinate_choice_indices=selected,group_signature_indices=group_ids,
                exceptional_groups=[g for g,s in enumerate(groups) if any(counts[a][g]!=[1,1,1] for a in s)],counts=counts,full_factor=False)

def controls(groups,coords,sigs):
    balanced=[[[1,1,1] if a in support else [0,0,0] for support in groups] for a in range(12)]
    positives=[dict(name='all_balanced_counts',**table_check(balanced,groups,coords,sigs))]
    with gzip.open(SIX,'rt') as f:partial=json.loads(next(f))
    need(partial['id']=='rank4_00_profile_0000','frozen partial count control')
    nonzero=copy.deepcopy(balanced)
    for a in range(12):
        for i,g in enumerate(partial['group_ids']):
            for f in range(3):nonzero[a][g][f]+=partial['coordinate_fibre_deviations'][a][f][i]
    positives.append(dict(name=partial['id'],**table_check(nonzero,groups,coords,sigs)))
    rejected=[]
    for name in ['bound','coordinate_domain','shape','Boolean']:
        bad=copy.deepcopy(balanced)
        a=groups[0][0]
        if name=='bound':bad[a][0]=[4,-1,0]
        elif name=='coordinate_domain':bad[a][0]=[0,1,2]
        elif name=='shape':bad.pop()
        else:bad[a][0][0]=True
        try:table_check(bad,groups,coords,sigs)
        except ValueError:rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    # Tiny joint-table/channel control distinguishes separate domains from coupling.
    tiny_domains=[[(0,),(1,)],[(0,),(1,)]]
    accepted=[]
    for i,j in product(range(2),repeat=2):
        q0,q1=tiny_domains[0][i][0],tiny_domains[1][j][0]
        if q0==q1:accepted.append([i,j])
    need(accepted==[[0,0],[1,1]],'literal consistency controls')
    need(tuple([3,0,0]*6) not in sigs,'quota-violating signature absent')
    return dict(positive_count_profiles=positives,rejected_corruptions=rejected,
                tiny_channel_positive_pairs=accepted,quota_violating_signature_rejected=True,
                scope='Count-table positives, explicitly no full-Gram or complete factor positive.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        pins={}
        for path,digest in PINS.items():need(sha(path)==digest,'input '+key(path));pins[key(path)]=digest
        gate=read(GATE);need(gate['status']=='INDEPENDENT_COMPLETE_COORDINATE_MARGINAL_DOMAINS_PASS','coordinate gate')
        localgate=read(LOCAL_GATE);need(localgate['inputs_sha256'][key(LOCAL)]==sha(LOCAL),'local gate raw binding')
        source=Path(__file__);spec=source.with_name(source.stem+'_spec.md')
        for path in (source,spec,ROOT/'uv.lock',ROOT/'pyproject.toml'):pins[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limits=dict(seconds=60,memory_estimate_bytes=512*1024**2,native_calls=0)))
        raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)));need(len(groups)==20,'twenty supports')
        coordinates=[]
        for record in read(SUMMARY)['records']:
            path=ROOT/record['path'];need(sha(path)==record['sha256']==gate['inputs_sha256'][key(path)],'complete coordinate file');pins[key(path)]=sha(path);coordinates.append(read(path))
        need([c['coordinate'] for c in coordinates]==list(range(12)),'ordered complete coordinates')
        local=read(LOCAL);words=local['words'];triples=local['survivors'];need(len(triples)==31110,'full local catalogue')
        table=defaultdict(list)
        for i,t in enumerate(triples):
            sig=signature(words,t);need(all(sum(sig[3*j:3*j+3])==3 for j in range(6)) and all(sum(sig[3*j+f] for j in range(6))==6 for f in range(3)),'literal local quotas');table[sig].append(i)
        sigs=sorted(table);save(out/'local_signatures.json',dict(signatures=[dict(index=i,counts=list(s),local_survivor_indices=table[s],count=len(table[s])) for i,s in enumerate(sigs)],local_triples=31110))
        controls_result=controls(groups,coordinates,sigs);save(out/'controls.json',controls_result)
        projections={};channel_domains=[]
        for a,c in enumerate(coordinates):
            for g in c['incident_groups']:
                values=sorted(set(tuple(x['full20_count_signature'][g]) for x in c['ordered_three_fibre_choices']))
                projections[a,g]=set(values);channel_domains.append(dict(coordinate=a,group=g,values=[list(v) for v in values]))
        domains=[]
        for g,support in enumerate(groups):
            retained=[];removed=[]
            for i,s in enumerate(sigs):
                bad=next((j for j,a in enumerate(support) if s[3*j:3*j+3] not in projections[a,g]),None)
                if bad is None:retained.append(i)
                else:removed.append(dict(signature_index=i,first_bad_coordinate=support[bad],count=list(s[3*bad:3*bad+3])))
            need(retained,'nonempty group table');domains.append(dict(group=g,support=list(support),signature_indices=retained,unary_removed=removed,count=len(retained)))
        sizes=[c['choice_count'] for c in coordinates]+[d['count'] for d in domains]+[len(c['values']) for c in channel_domains]
        selectors=sum(sizes);aux=sum(n-1 for n in sizes if n>1);onehot_clauses=sum(1 if n==1 else 3*n-3 for n in sizes)
        implications=sum(c['choice_count']*len(c['incident_groups']) for c in coordinates)+sum(d['count']*6 for d in domains)
        inventory=dict(schema='ARBITRARY_EXCEPTION_COUNT_MASTER_PREFLIGHT_V1',groups=[list(s) for s in groups],coordinate_records=read(SUMMARY)['records'],group_domains=domains,channel_domains=channel_domains,unique_local_signatures=len(sigs),coordinate_choice_selectors=sum(c['choice_count'] for c in coordinates),group_signature_selectors=sum(d['count'] for d in domains),count_channel_variables=sum(len(c['values']) for c in channel_domains),onehot_domains=len(sizes),prefix_auxiliaries=aux,estimated_variables=selectors+aux,estimated_clauses=onehot_clauses+implications,onehot_clauses=onehot_clauses,implication_clauses=implications,exception_count_bound=None,scope='Exact joint coordinate-marginal/local-count-table feasibility only; inherited within-group caps, no full Gram/crosscaps/D.',inputs_sha256=pins)
        save(out/'inventory.json',inventory)
        inspected=['theory_20260930_hadamard_triplicate_counts.py','theory_20260930_hadamard_coordinate_marginal_domains.py','theory_20260930_hadamard_six_rank4_dp.py','theory_20260930_hadamard_seven_rank5_dp.py','theory_20260930_hadamard_six_profile_local_domains.py','theory_20260930_hadamard_seven_profile_local_domains.py']
        save(out/'overlap_review.json',dict(inspected_sources={p:sha(ROOT/'acceleration'/p) for p in inspected},conclusion='Existing sources enumerate separate coordinate domains or fixed exceptional-subset profiles; no jointly coupled arbitrary-exception table model found in these inspected sources.',limitations='Narrow repository audit only; no global novelty claim.'))
        need(time.monotonic()-start<60,'preflight wall allocation')
        summary=dict(status='CANDIDATE_COUNT_MASTER_PREFLIGHT_COMPLETE',inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},unique_local_signatures=len(sigs),coordinate_choices=inventory['coordinate_choice_selectors'],group_choices=inventory['group_signature_selectors'],channel_values=inventory['count_channel_variables'],estimated_variables=inventory['estimated_variables'],estimated_clauses=inventory['estimated_clauses'],group_domain_sizes=[d['count'] for d in domains],elapsed_seconds=time.monotonic()-start,native_calls=0,independent_approval=False,target_resolution=False,artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
