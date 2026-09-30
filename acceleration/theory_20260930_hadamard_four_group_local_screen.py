"""Producer exact local necessary screen; saved outcomes are candidates."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
CIRCUITS=B/'20260930_hadamard_four_group_circuits/circuits.json'
FEW=B/'20260930_independent_review/hadamard_few_exception_marginals/summary.json'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
FIXTURE_GATE=B/'20260930_independent_review/srg243_residual_fixture/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',CIRCUITS:'2696132295884d1294e4afaae4a2c68452a422eea84a113ff15a2fca9452047f',FEW:'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',FIXTURE_GATE:'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def feature(columns,gram):
    n=len(gram);counts={};one=occ=double=0
    for i in range(n):
        count=sum((col>>i)&1 for col in columns);need(count<=gram[i][i],'individual diagonal Gram cap')
        counts[(i,i)]=count
        for j in range(i+1,n):
            count=sum(((col>>i)&1)&((col>>j)&1) for col in columns)
            need(count<=gram[i][j],'individual offdiagonal Gram cap')
            if count:counts[(i,j)]=count
            bit=1<<(i*n+j)
            if gram[i][j]==1 and count:one|=bit
            elif gram[i][j]==2:
                if count:occ|=bit
                if count==2:double|=bit
            else:need(gram[i][j]==0 or gram[i][j] in (1,2),'target offdiag domain')
    return dict(columns=columns,counts=counts,one=one,occ=occ,double=double)
def gram_fast(left,right):
    return not(left['one']&right['one'] or left['double']&right['occ'] or right['double']&left['occ'])
def gram_literal(left,right,gram):
    return all(left['counts'].get((i,j),0)+right['counts'].get((i,j),0)<=gram[i][j] for i in range(len(gram)) for j in range(i,len(gram)))
def caps(left,right):return all((x&y).bit_count()<=2 for x in left['columns'] for y in right['columns'])
def profile_list(k):
    vectors=[(0,0,0)]+sorted(set(permutations((-1,0,1))))
    return [p for p in product(vectors,repeat=k) if any(any(v) for v in p) and all(sum(v[f] for v in p)==0 for f in range(3))]
def ac(domains,tables):
    masks=[(1<<len(d))-1 for d in domains];steps=[]
    changed=True
    while changed:
        changed=False
        for left in range(4):
            for right in range(4):
                if left==right:continue
                for index in range(len(domains[left])):
                    if masks[left]>>index&1 and not(tables[(left,right)][index]&masks[right]):
                        steps.append(dict(left=left,right=right,option_index=index,right_domain_mask=hex(masks[right])))
                        masks[left]&=~(1<<index);changed=True
    return dict(final_masks=[hex(x) for x in masks],final_domain_sizes=[x.bit_count() for x in masks],removals=steps,empty=any(x==0 for x in masks))
def controls():
    need(len(profile_list(1))==0 and len(profile_list(2))==6,'one/two-coordinate profiles')
    need(all(all(sum(v[f] for v in p)==0 for f in range(3)) for p in profile_list(3)),'three-coordinate conservation')
    f=read(FIXTURE)['factor60x180'];n=len(f);gram=[[sum(f[i][d]*f[j][d] for d in range(180)) for j in range(n)] for i in range(n)]
    columns=[sum(f[i][d]<<i for i in range(n)) for d in range(180)]
    parts=[feature(columns[3*j:3*j+3],gram) for j in range(8)]
    checked=0
    for i,j in combinations(range(8),2):
        need(gram_fast(parts[i],parts[j])==gram_literal(parts[i],parts[j],gram),'243 fast/literal Gram')
        need(gram_literal(parts[i],parts[j],gram) and caps(parts[i],parts[j]),'genuine243 distinct-column positive');checked+=1
    need(not caps(parts[0],parts[0]),'duplicated-column cap control')
    corrupt=dict(parts[0]);corrupt['one']=parts[0]['one']|parts[1]['one']
    need(not gram_fast(corrupt,parts[1]),'corrupt occupied target-one Gram mask')
    need(any(sum(v[f] for v in ((1,-1,0),(0,1,-1))) for f in range(3)),'uncancelled profile')
    toy=[list(range(2)) for _ in range(4)];tables={(i,j):[3,3] for i in range(4) for j in range(4) if i!=j}
    need(not ac(toy,tables)['empty'],'complete relation AC control');tables[(0,1)]=[0,0];need(ac(toy,tables)['empty'],'empty relation AC control')
    return dict(srg243_pair_controls=checked,srg243_input_sha256=PINS[FIXTURE],profile_counts={str(k):len(profile_list(k)) for k in (1,2,3)},rejected_controls=['duplicated_column','corrupt_Gram_mask','uncancelled_profile'],scope='Different-parameter243 positive and synthetic AC controls; no research factor.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'pin '+key(path))
        inputs={key(path):digest for path,digest in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_four_group_local_screen_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(seconds=120,native_solver_calls=0),independent_approval=False))
        save(out/'controls.json',controls())
        raw=read(RAW);local=read(LOCAL);gram=raw['prescribed_Gram36'];words=local['words'];triples=local['survivors'];need(len(triples)==31110,'catalog')
        groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)))
        signature_catalog=defaultdict(list)
        for index,tri in enumerate(triples):
            signature=tuple(sum(words[w][pos]==f for w in tri) for pos in range(6) for f in range(3));signature_catalog[signature].append(index)
        circuits=[c for c in read(CIRCUITS)['records'] if len(c['common_support'])>=2]
        cases=[(ci,c,pi,prof) for ci,c in enumerate(circuits) for pi,prof in enumerate(profile_list(len(c['common_support'])))]
        save(out/'profile_universe.json',dict(circuits=circuits,records=[dict(case=i,circuit_index=ci,profile_index=pi,profile=prof) for i,(ci,c,pi,prof) in enumerate(cases)],population=len(cases),normalization='No fibre or deviation-profile quotient.'))
        feature_cache={};results=[];attempted_pairs=literalchecks=0
        for case_index,(ci,c,pi,prof) in enumerate(tqdm(cases,desc='Four-exception local profiles',mininterval=1)):
            domains=[]
            for g,sign in zip(c['groups'],c['relation']):
                profile={a:prof[j] for j,a in enumerate(c['common_support'])}
                signature=tuple(1+sign*profile.get(a,(0,0,0))[f] for a in groups[g] for f in range(3))
                domain=signature_catalog.get(signature,[]);domains.append(domain)
                for local_index in domain:
                    cachekey=(g,local_index)
                    if cachekey not in feature_cache:
                        cols=[sum(1<<(12*words[w][pos]+a) for pos,a in enumerate(groups[g])) for w in triples[local_index]]
                        feature_cache[cachekey]=feature(cols,gram)
            tables_gram={};tables_all={};pair_records=[]
            for left,right in combinations(range(4),2):
                forward_g=[0]*len(domains[left]);backward_g=[0]*len(domains[right]);forward_all=forward_g.copy();backward_all=backward_g.copy();ng=nb=0
                for i,li in enumerate(domains[left]):
                    lf=feature_cache[(c['groups'][left],li)]
                    for j,ri in enumerate(domains[right]):
                        rf=feature_cache[(c['groups'][right],ri)];gok=gram_fast(lf,rf);bok=gok and caps(lf,rf);attempted_pairs+=1
                        if i<2 and j<2:
                            need(gok==gram_literal(lf,rf,gram),'sample fast versus literal full integer Gram');literalchecks+=1
                        if gok:forward_g[i]|=1<<j;backward_g[j]|=1<<i;ng+=1
                        if bok:forward_all[i]|=1<<j;backward_all[j]|=1<<i;nb+=1
                    need(time.monotonic()-start<120,'bounded profile census allocation')
                tables_gram[(left,right)]=forward_g;tables_gram[(right,left)]=backward_g;tables_all[(left,right)]=forward_all;tables_all[(right,left)]=backward_all
                pair_records.append(dict(sides=[left,right],population=len(domains[left])*len(domains[right]),gram_compatible=ng,gram_and_caps_compatible=nb,gram_forward_masks=[hex(x) for x in forward_g],both_forward_masks=[hex(x) for x in forward_all]))
            rec=dict(case=case_index,circuit_index=ci,profile_index=pi,groups=c['groups'],relation=c['relation'],common_support=c['common_support'],profile=prof,local_survivor_indices=domains,domain_sizes=list(map(len,domains)),pairs=pair_records,gram_ac=ac(domains,tables_gram),gram_caps_ac=ac(domains,tables_all),scope='Necessary pairwise screen over already local-cap-filtered domains; no simultaneous4-option witness asserted.')
            path=out/f'case_{case_index:03d}.json';save(path,rec);results.append(dict(case=case_index,path=key(path),sha256=sha(path),domain_sizes=rec['domain_sizes'],gram_ac_empty=rec['gram_ac']['empty'],gram_caps_ac_empty=rec['gram_caps_ac']['empty'],final_sizes=rec['gram_caps_ac']['final_domain_sizes']))
            with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(results[-1])+'\n')
        summary=dict(status='CANDIDATE_FOUR_EXCEPTION_LOCAL_PROFILE_SCREEN',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(f):sha(f) for f in out.iterdir() if f.is_file()},circuits=len(circuits),profile_cases=len(cases),completed_cases=len(results),case_summaries=results,option_pair_attempts=attempted_pairs,literal_Gram_samples=literalchecks,initial_empty_cases=sum(any(n==0 for n in r['domain_sizes']) for r in results),pair_gram_AC_empty=sum(r['gram_ac_empty'] for r in results),pair_gram_and_caps_AC_empty=sum(r['gram_caps_ac_empty'] for r in results),unresolved_cases=sum(not r['gram_caps_ac_empty'] for r in results),native_solver_calls=0,independent_approval=False,target_resolution=False,elapsed_seconds=time.monotonic()-start,scope='Exactly four exceptional groups on one fixed support, full prescribed Gram AND column caps necessary screen; no general support/target exclusion.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256','case_summaries')}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
