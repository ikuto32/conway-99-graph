"""Bounded candidate pairwise AC screen; complete literal seven-profile universe."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
DOMAIN_ROOT=B/'20260930_hadamard_seven_profile_local_domains'
PROFILES=DOMAIN_ROOT/'profiles.jsonl.gz';RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
SPEC=Path(__file__).with_name('theory_20260930_hadamard_seven_profile_arc_spec.md')
PINS={PROFILES:'88d5e572fe280a70b51e0dd2785378d73300e6873a7db788072bcbca8ef256ae',DOMAIN_ROOT/'summary.json':'eb06d98f0e5fab055d07f8bea55e42132e35a340f82d72fad85adf0d175f04f7',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',B/'20260930_independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',B/'20260930_independent_review/hadamard_seven_rank5_profiles/summary.json':'a5d5ac4d966077ceda4b19382bc4ddc5f85b7b812ab3bf01352260c74b2cb93d'}
DOMAIN_GATE_STATUS='INDEPENDENT_SEVEN_EXCEPTION_LOCAL_DOMAIN_FILTER_PASS'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def gzsave(p,x):
    with Path(p).open('xb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as g:g.write(json.dumps(x,separators=(',',':')).encode()+b'\n')
def gzread(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def pin_inputs(args):
    for path,h in PINS.items():need(sha(path)==h,'input pin '+key(path))
    need(sha(args.domain_gate)==args.domain_gate_sha256,'independent domain gate exact hash')
    gate=read(args.domain_gate);need(gate['status']==DOMAIN_GATE_STATUS,'independent seven-domain gate passed')
    for path in (PROFILES,DOMAIN_ROOT/'summary.json',RAW,LOCAL):
        need(gate['inputs_sha256'][key(path)]==sha(path),'gate directly binds raw domain population '+key(path))
    return {key(p):sha(p) for p in [*PINS,Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml',args.domain_gate]}
def raw_inputs():
    raw=read(RAW);local=read(LOCAL)
    with gzip.open(PROFILES,'rt',encoding='utf-8') as f:profiles=[json.loads(line) for line in f]
    need(len(profiles)==1608 and len({p['id'] for p in profiles})==1608,'complete distinct1608 profiles')
    need(all(len(p['group_ids'])==len(p['local_domains'])==7 and p['group_ids']==sorted(set(p['group_ids'])) and not p['normalization_used_for_filtering'] for p in profiles),'literal seven-domain population without quotient')
    groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)))
    need(len(groups)==20 and len(local['survivors'])==31110,'frozen support/catalogue shape')
    return raw,local,profiles,groups

def inventory(out,inputs,started):
    raw,local,profiles,groups=raw_inputs();words=local['words'];triples=local['survivors'];catalog=defaultdict(list)
    for i,t in enumerate(triples):catalog[tuple(sum(words[w][a]==f for w in t) for a in range(6) for f in range(3))].append(i)
    endpoints=[];ep_lookup={};relations=[];rel_lookup={};profile_records=[];checked={};feature_keys=set()
    for pi,p in enumerate(profiles):
        need(p['profile_sha256']==digest(dict(groups=p['group_ids'],deviations=p['coordinate_fibre_deviations'])),'profile raw hash')
        ids=[]
        for side,ref in enumerate(p['local_domains']):
            path=ROOT/ref['path'];need(ref['group']==p['group_ids'][side],'group side mapping')
            if ref['sha256'] not in checked:
                need(sha(path)==ref['sha256'],'domain input identity');domain=read(path)
                need(catalog[tuple(domain['count_signature'])]==domain['local_survivor_indices'],'complete individual domain ranks');checked[ref['sha256']]=domain
            domain=checked[ref['sha256']];g=ref['group'];want=[1+p['coordinate_fibre_deviations'][a][f][side] for a in groups[g] for f in range(3)]
            need(domain['count_signature']==want and domain['count']==ref['count']==len(domain['local_survivor_indices']),'literal profile to domain')
            endpoint=(g,ref['sha256'])
            if endpoint not in ep_lookup:
                ep_lookup[endpoint]=len(endpoints);endpoints.append(dict(index=len(endpoints),group=g,support=groups[g],domain_path=ref['path'],domain_sha256=ref['sha256'],count=domain['count'],local_survivor_indices=domain['local_survivor_indices']))
                feature_keys.update((g,i) for i in domain['local_survivor_indices'])
            ids.append(ep_lookup[endpoint])
        pairs=[]
        for left,right in combinations(range(7),2):
            epair=(ids[left],ids[right]);need(endpoints[epair[0]]['group']<endpoints[epair[1]]['group'],'ascending groups')
            if epair not in rel_lookup:
                rel_lookup[epair]=len(relations);relations.append(dict(index=len(relations),endpoints=epair,option_pairs=endpoints[epair[0]]['count']*endpoints[epair[1]]['count']))
            pairs.append(dict(sides=[left,right],relation=rel_lookup[epair]))
        need(len(ids)==7 and len(pairs)==21,'all seven endpoints and21 pairs')
        profile_records.append(dict(index=pi,id=p['id'],profile_sha256=p['profile_sha256'],rank5_case=p['rank5_case'],groups=p['group_ids'],endpoints=ids,pairs=pairs))
        need(time.monotonic()-started<30,'inventory cooperative30-second allocation')
    products=sum(r['option_pairs'] for r in relations)
    estimate=len(feature_keys)*8192+sum(4096+64*(endpoints[r['endpoints'][0]]['count']+endpoints[r['endpoints'][1]]['count']) for r in relations)+len(profiles)*8192
    permitted=products<=50000000 and max(e['count'] for e in endpoints)<=150 and estimate<=512*1024**2
    result=dict(schema='SEVEN_PROFILE_ARC_INVENTORY_V1',inputs_sha256=inputs,profiles=profile_records,endpoints=endpoints,relations=relations,labelled_profiles=1608,profile_pair_uses=1608*21,unique_endpoints=len(endpoints),unique_relations=len(relations),unique_lifted_choices=len(feature_keys),distinct_option_pair_products=products,conservative_cache_estimate_bytes=estimate,ordinary_resource_gate_pass=permitted,resource_limits=dict(cache_estimate_bytes=512*1024**2,option_pairs=50000000,maximum_domain=150),normalization_used=False)
    save(out/'inventory.json',result);save(out/'summary.json',dict(status='CANDIDATE_SEVEN_PROFILE_ARC_RESOURCE_INVENTORY',inputs_sha256=inputs,inventory_sha256=sha(out/'inventory.json'),**{k:result[k] for k in ('labelled_profiles','profile_pair_uses','unique_endpoints','unique_relations','unique_lifted_choices','distinct_option_pair_products','conservative_cache_estimate_bytes','ordinary_resource_gate_pass')},elapsed_seconds=time.monotonic()-started,solver_calls=0))
    print(json.dumps(read(out/'summary.json')))

def feature(columns,gram):
    counts=Counter();one=occupied=double=0;n=len(gram)
    for mask in columns:
        rows=[i for i in range(n) if mask>>i&1]
        for i in rows:counts[i,i]+=1
        for i,j in combinations(rows,2):counts[i,j]+=1
    for (i,j),value in counts.items():
        need(value<=gram[i][j],'individual contribution exceeds prescribed Gram')
        if i==j:continue
        bit=1<<(i*n+j)
        if gram[i][j]==1:one|=bit
        elif gram[i][j]==2:
            occupied|=bit
            if value==2:double|=bit
        else:need(False,'unsupported positive offdiagonal bound')
    return dict(columns=columns,counts=counts,one=one,occupied=occupied,double=double)
def gram_fast(a,b):return not(a['one']&b['one'] or a['double']&b['occupied'] or b['double']&a['occupied'])
def gram_literal(a,b,g):return all(a['counts'].get((i,j),0)+b['counts'].get((i,j),0)<=g[i][j] for i in range(len(g)) for j in range(i,len(g)))
def cap_fast(a,b):return all((u&v).bit_count()<=2 for u in a['columns'] for v in b['columns'])
def cap_literal(a,b,n):return all(sum(bool(u>>i&1) and bool(v>>i&1) for i in range(n))<=2 for u in a['columns'] for v in b['columns'])
def ac(sizes,tables):
    masks=[(1<<n)-1 for n in sizes];removed=[];change=True
    while change:
        change=False
        for left in range(len(sizes)):
            for right in range(len(sizes)):
                if left==right:continue
                for option in range(sizes[left]):
                    if masks[left]>>option&1 and not(tables[left,right][option]&masks[right]):
                        removed.append(dict(left=left,right=right,option=option,right_domain_mask=hex(masks[right])));masks[left]&=~(1<<option);change=True
    witnesses=[]
    for left in range(len(sizes)):
        for right in range(len(sizes)):
            if left==right:continue
            support=[]
            for option in range(sizes[left]):
                if masks[left]>>option&1:
                    valid=tables[left,right][option]&masks[right];need(valid!=0,'fixed point support');support.append([option,(valid&-valid).bit_length()-1])
            witnesses.append(dict(sides=[left,right],supports=support))
    return dict(final_masks=list(map(hex,masks)),final_sizes=[m.bit_count() for m in masks],empty=any(m==0 for m in masks),deletions=removed,support_witnesses=witnesses)
def replay(sizes,tables,result):
    masks=[(1<<n)-1 for n in sizes]
    for d in result['deletions']:
        l,r,i=d['left'],d['right'],d['option'];need(masks[l]>>i&1 and hex(masks[r])==d['right_domain_mask'] and not(tables[l,r][i]&masks[r]),'literal deletion witness');masks[l]&=~(1<<i)
    need(list(map(hex,masks))==result['final_masks'],'final deletion masks')
    for w in result['support_witnesses']:
        l,r=w['sides'];need([i for i,j in w['supports']]==[i for i in range(sizes[l]) if masks[l]>>i&1],'all surviving choice supports')
        for i,j in w['supports']:need(masks[r]>>j&1 and tables[l,r][i]>>j&1,'saved literal support')
def transpose(forward,n):
    backward=[0]*n
    for i,mask in enumerate(forward):
        for j in range(n):
            if mask>>j&1:backward[j]|=1<<i
    return backward

def controls():
    f=read(FIXTURE)['factor60x180'];g=[[sum(x*y for x,y in zip(a,b)) for b in f] for a in f];cols=[sum(f[i][d]<<i for i in range(60)) for d in range(180)];parts=[feature(cols[3*i:3*i+3],g) for i in range(8)]
    for a,b in combinations(parts,2):need(gram_fast(a,b)==gram_literal(a,b,g) and gram_fast(a,b) and cap_fast(a,b)==cap_literal(a,b,60) and cap_fast(a,b),'genuine243 Gram/cap positive')
    need(not cap_fast(parts[0],parts[0]),'duplicated column corruption')
    modified=dict(parts[0]);modified['one']|=parts[1]['one'];need(not gram_fast(modified,parts[1]),'corrupt target-one mask')
    # All 16^3 binary-domain triangle relations, exhaustive actual joint solutions.
    joint=0
    for bits in product(range(16),repeat=3):
        tables={}
        for (i,j),mask in zip(combinations(range(3),2),bits):
            rows=[(mask>>(2*k))&3 for k in range(2)];tables[i,j]=rows;tables[j,i]=transpose(rows,2)
        result=ac([2]*3,tables);replay([2]*3,tables,result)
        for values in product(range(2),repeat=3):
            if all(tables[i,j][values[i]]>>values[j]&1 for i,j in combinations(range(3),2)):
                need(all(int(result['final_masks'][i],16)>>values[i]&1 for i in range(3)),'AC cannot remove actual solution');joint+=1
    tables={(i,j):[3,3] for i in range(7) for j in range(7) if i!=j};positive=ac([2]*7,tables);need(not positive['empty'],'seven-domain positive');replay([2]*7,tables,positive)
    corrupt=json.loads(json.dumps(positive));corrupt['support_witnesses'][0]['supports'][0][1]=2
    try:replay([2]*7,tables,corrupt)
    except ValueError:pass
    else:raise ValueError('corrupt support accepted')
    tables[0,1]=[0,0];tables[1,0]=[0,0];negative=ac([2]*7,tables);need(negative['empty'],'seven-domain empty relation');replay([2]*7,tables,negative)
    corrupt=json.loads(json.dumps(negative));corrupt['deletions'][0]['right_domain_mask']='0x0'
    try:replay([2]*7,tables,corrupt)
    except ValueError:pass
    else:raise ValueError('corrupt deletion accepted')
    return dict(actual_srg243_pairs=28,synthetic_binary_triangle_relations=4096,actual_joint_solution_controls=joint,synthetic_seven_domain_cases=2,rejected_controls=['duplicate_column','occupied_mask','wrong_support','wrong_deletion_neighbor_mask'],research_factor_positive=False)

def screen(args,out,inputs,started):
    need(sha(args.inventory)==args.inventory_sha256,'inventory hash');inv=read(args.inventory);need(inv['inputs_sha256']==inputs and inv['ordinary_resource_gate_pass'],'frozen inventory/source/resource gate')
    inputs={**inputs,key(args.inventory):args.inventory_sha256};raw,local,profiles,groups=raw_inputs();gram=raw['prescribed_Gram36'];need(all(gram[i][i]==10 for i in range(36)),'pair diagonal upper bound six<=ten')
    save(out/'controls.json',controls());eps=inv['endpoints'];relation_refs=[];profile_refs=[];cache={};features={};relation_tables={};literal_samples=0
    if args.resume_checkpoint:
        need(args.resume_checkpoint_sha256 is not None and sha(args.resume_checkpoint)==args.resume_checkpoint_sha256,'resume checkpoint pin');prior=read(args.resume_checkpoint);need(prior['inputs_sha256']==inputs,'same source/spec/inventory on resume');relation_refs=prior['completed_relations'];profile_refs=prior['completed_profiles']
        need([r['index'] for r in relation_refs]==list(range(len(relation_refs))) and [r['index'] for r in profile_refs]==list(range(len(profile_refs))),'completed prefix')
        for r in relation_refs+profile_refs:need(sha(ROOT/r['path'])==r['sha256'],'completed artifact hash')
    else:need(args.resume_checkpoint_sha256 is None,'resume hash without path')
    (out/'relations').mkdir();(out/'profiles').mkdir()
    def lifted(ep):
        index=ep['index']
        if index not in cache:
            need(sha(ROOT/ep['domain_path'])==ep['domain_sha256'],'domain raw unchanged');result=[]
            for li in ep['local_survivor_indices']:
                k=(ep['group'],li)
                if k not in features:
                    cols=[sum(1<<(12*local['words'][w][pos]+a) for pos,a in enumerate(ep['support'])) for w in local['survivors'][li]];features[k]=feature(cols,gram)
                result.append(features[k])
            cache[index]=result
        return cache[index]
    stop='COMPLETE'
    for r in tqdm(inv['relations'][len(relation_refs):],desc='Distinct seven-profile relations',mininterval=1):
        if time.monotonic()-started>=180:stop='PARTIAL_UNKNOWN';break
        a,b=(lifted(eps[i]) for i in r['endpoints']);gm=[];both=[];ng=nb=0
        for i,left in enumerate(a):
            rowg=rowb=0
            for j,right in enumerate(b):
                good=gram_fast(left,right);cap=cap_fast(left,right)
                if i<2 and j<2:
                    need(good==gram_literal(left,right,gram) and cap==cap_literal(left,right,36),'actual-domain fast/literal calibration');literal_samples+=1
                if good:rowg|=1<<j;ng+=1
                if good and cap:rowb|=1<<j;nb+=1
            gm.append(rowg);both.append(rowb)
        value=dict(index=r['index'],endpoints=r['endpoints'],option_pairs=r['option_pairs'],gram_compatible=ng,combined_compatible=nb,gram_forward=list(map(hex,gm)),combined_forward=list(map(hex,both)))
        path=out/'relations'/f'relation_{r["index"]:05d}.json.gz';gzsave(path,value);relation_refs.append(dict(index=r['index'],path=key(path),sha256=sha(path),option_pairs=r['option_pairs'],gram_compatible=ng,combined_compatible=nb))
        with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(stage='relation',**relation_refs[-1]))+'\n')
    if len(relation_refs)==len(inv['relations']):
        for p in tqdm(inv['profiles'][len(profile_refs):],desc='Literal seven-profile AC',mininterval=1):
            if time.monotonic()-started>=180:stop='PARTIAL_UNKNOWN';break
            sizes=[eps[i]['count'] for i in p['endpoints']];tg={};tb={}
            for pair in p['pairs']:
                ri=pair['relation'];l,r=pair['sides']
                if ri not in relation_tables:
                    value=gzread(ROOT/relation_refs[ri]['path']);relation_tables[ri]=([int(s,16) for s in value['gram_forward']],[int(s,16) for s in value['combined_forward']])
                rowsg,rowsb=relation_tables[ri];tg[l,r]=rowsg;tb[l,r]=rowsb;tg[r,l]=transpose(rowsg,sizes[r]);tb[r,l]=transpose(rowsb,sizes[r])
            gram_ac=ac(sizes,tg);both_ac=ac(sizes,tb);replay(sizes,tg,gram_ac);replay(sizes,tb,both_ac)
            value=dict(index=p['index'],id=p['id'],profile_sha256=p['profile_sha256'],raw_profile=profiles[p['index']],endpoint_indices=p['endpoints'],relations=[relation_refs[x['relation']] for x in p['pairs']],initial_domain_sizes=sizes,gram_ac=gram_ac,gram_caps_ac=both_ac,scope='Necessary pairwise screen only; no joint seven-choice or full-factor conclusion.')
            path=out/'profiles'/f'profile_{p["index"]:04d}.json.gz';gzsave(path,value);profile_refs.append(dict(index=p['index'],id=p['id'],rank5_case=p['rank5_case'],path=key(path),sha256=sha(path),gram_empty=gram_ac['empty'],combined_empty=both_ac['empty'],gram_final_sizes=gram_ac['final_sizes'],combined_final_sizes=both_ac['final_sizes']))
            with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(stage='profile',**profile_refs[-1]))+'\n')
    if len(profile_refs)<1608:stop='PARTIAL_UNKNOWN'
    checkpoint=dict(schema='SEVEN_PROFILE_ARC_CHECKPOINT_V1',inputs_sha256=inputs,completed_relations=relation_refs,completed_profiles=profile_refs,stop_state=stop,automatic_resume=False)
    save(out/'checkpoint.json',checkpoint);case_counts={}
    for c in sorted({p['rank5_case'] for p in inv['profiles']}):
        selected=[p for p in profile_refs if p['rank5_case']==c];case_counts[str(c)]=dict(completed=len(selected),Gram_empty=sum(p['gram_empty'] for p in selected),Gram_caps_empty=sum(p['combined_empty'] for p in selected),unresolved=sum(not p['combined_empty'] for p in selected))
    summary=dict(status='CANDIDATE_SEVEN_EXCEPTION_PROFILE_ARC_SCREEN',completion=stop,inputs_sha256=inputs,checkpoint_path=key(out/'checkpoint.json'),checkpoint_sha256=sha(out/'checkpoint.json'),frozen_profiles=1608,completed_profiles=len(profile_refs),pending_profiles=1608-len(profile_refs),unique_relations=len(inv['relations']),completed_relations=len(relation_refs),completed_distinct_option_products=sum(r['option_pairs'] for r in relation_refs),Gram_empty_profiles=sum(p['gram_empty'] for p in profile_refs),Gram_caps_empty_profiles=sum(p['combined_empty'] for p in profile_refs),unresolved_complete_profiles=sum(not p['combined_empty'] for p in profile_refs),by_rank5_case=case_counts,literal_pair_samples_this_allocation=literal_samples,elapsed_seconds_this_allocation=time.monotonic()-started,wall_cap_seconds=180,normalization_used=False,native_solver_calls=0,independent_approval=False,target_resolution=False,availability='LOCAL_ONLY',limitations=['Both variants start with within-group cap-filtered complete local domains; Gram-pair results are not Gram-only-family exclusions.','No fibre-orbit diagnostic is used for pruning.','Every nonempty fixed point is only a necessary pairwise condition.','An empty profile is conditional on fixed support/full Gram/Ycaps.','Incomplete or unattempted profiles remain UNKNOWN.'])
    summary['outputs_sha256']={key(p):sha(p) for p in out.iterdir() if p.is_file()};save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);a_inventory=a=sub.add_parser('inventory');a.add_argument('--out',type=Path,required=True);a_screen=a=sub.add_parser('screen');a.add_argument('--out',type=Path,required=True);a.add_argument('--inventory',type=Path,required=True);a.add_argument('--inventory-sha256',required=True);a.add_argument('--resume-checkpoint',type=Path);a.add_argument('--resume-checkpoint-sha256');
    for parser in (a_inventory,a_screen):
        parser.add_argument('--domain-gate',type=Path,required=True);parser.add_argument('--domain-gate-sha256',required=True)
    args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        inputs=pin_inputs(args);save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,mode=args.mode,resource_limit_seconds=30 if args.mode=='inventory' else 180,solver_calls=0,independent_approval=False))
        if args.mode=='inventory':inventory(out,inputs,started)
        else:screen(args,out,inputs,started)
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),solver_calls=0));raise
if __name__=='__main__':main()
