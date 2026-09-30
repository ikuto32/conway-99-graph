"""Complete native-free initial-domain inventory; no repository-code imports."""
import argparse,copy,hashlib,json,time,traceback
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B=A/'results';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
MANIFEST=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json';GATE=B/'20260930_independent_review/exact_eight_campaign/summary.json';BATCH=B/'20260930_exact_eight_first12_cnfs/summary.json';RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
PINS={MANIFEST:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',GATE:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',BATCH:'3f7abda7d7e12a6babaf48c6c690f85bf1db69e6401098f2ece9a881b1772136',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',A/'theory_20260930_exact_eight_campaign.py':'9ebd87fea886f45fc916ad8afb9dc212fa089f760d4b96e55082926baef02c57',A/'theory_20260930_hadamard_four_profile_cnf.py':'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f'}
HIST={
'20260930_eight_count_profile_lift':('995a7f7666865482a19229f89d8224650f6ddaea25b5ca2fd0f7d792919e7d16','8342a2c4e45af5f92e1e36a3e61b3d5f299f79ad9dd6320d84618c4645d6373b','a7bd6776b6a5e54857a703bbbdc95fe433a1274e5c592484c0d990fdf4adefa4'),
'20260930_eight_count_profile_lift_second':('f0f365365ef4ced6c5f547c23fb364048ca2c413a457c1c3f8f8c98d07786c0e','652225f2bf156a4bb1a92979504ec810bba3277137b889059f227d0c035f2afc','14ad4ae64706db50e473f0ffa90bbdb8ce552dece5e1468ab066998ef71b7a32'),
'20260930_eight_count_profile_lift_third':('69eb50b0cb780b58df71283195a84fcf50a5b9ea627d3e879aa5131abc4404b6','4f5eedcd74eb2c5d44a6955f80b9d8cfb8899949bcfeb31a5aafd56adc8260e2','0a821d08532ece7d99bc5917a61af8dd0338379ab73a83c3687cbdf5ea480634'),
'20260930_exact_eight_next_lift':('6cad750feb66e73dbeec98d818ca1a15b049105167c4cacce70e3a1071bd17dc','d8a05714c5297495c2a2d28835bd0c41de90a956162f998158dea39f78cf04b1','91084af7baa7041e6f66ce9cdcfb00b72eebce07389a5d0e160209457438109d')}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def need(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def flat(c):return tuple(v for row in c for triple in row for v in triple)
def images(v):return [tuple(v[k+p[f]]for k in range(0,720,3)for f in range(3))for p in permutations(range(3))]
def dims(sizes):
    need(len(sizes)==20 and all(type(s)is int and s>=2 for s in sizes),'domain sizes');s=sum(sizes);return dict(selectors=s,variables=2*s+5380,clauses=49*s+60400)
def catalogue(local):
    words=local['words'];need(words==[list(w)for w in product(range(3),repeat=6)if all(w.count(f)==2 for f in range(3))],'all90 words')
    overlaps={(i,j):sum(a==b for a,b in zip(words[i],words[j]))for i,j in combinations(range(90),2)}
    cells=[[(a,b,w[a],w[b])for a,b in combinations(range(6),2)]for w in words]
    triples=[];overlap_only_rejections=0
    for t in combinations(range(90),3):
        if not all(overlaps[x,y]<=2 for x,y in combinations(t,2)):continue
        observed=Counter(cell for i in t for cell in cells[i])
        if any(n>(1 if f==h else 2)for(a,b,f,h),n in observed.items()):overlap_only_rejections+=1;continue
        triples.append(list(t))
    need(overlap_only_rejections>0,'column-overlap-only false-positive control')
    need(triples==local['survivors']and len(triples)==31110,'all31110 complete local Gram/Y-cap triples')
    classes=defaultdict(list)
    for i,t in enumerate(triples):classes[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
    wi={tuple(w):i for i,w in enumerate(words)};normalized=[]
    for rest in product(tuple(permutations(range(3))),repeat=5):
        ps=((0,1,2),)+rest;rows=[tuple(p[c]for p in ps)for c in range(3)]
        if all(all(row.count(f)==2 for f in range(3))for row in rows):normalized.append(tuple(sorted(wi[row]for row in rows)))
    need(len(normalized)==len(set(normalized))==150 and set(normalized)=={tuple(triples[i])for i in classes[(1,)*18]},'balanced normalization bijection')
    need(len(classes)==6061,'complete signature catalogue');return words,triples,dict(classes)
def domain_record(counts,groups,classes):
    need(len(counts)==12 and all(len(row)==20 and all(len(t)==3 and all(type(x)is int and 0<=x<=3 for x in t)for t in row)for row in counts),'count shape and bounds')
    for a in range(12):
        for g,s in enumerate(groups):need(sum(counts[a][g])==(3 if a in s else 0),'support count')
        for f in range(3):need(sum(counts[a][g][f]for g in range(20))==10,'row margins')
    result=[]
    for g,s in enumerate(groups):
        signature=tuple(x for a in s for x in counts[a][g]);ids=classes.get(signature,[]);need(ids,'nonempty exact initial class');result.append(dict(group=g,signature=list(signature),local_survivor_indices=ids,size=len(ids),balanced=signature==(1,)*18))
    need(sum(not r['balanced']for r in result)==8,'exactly eight exceptions');return result
def validate_case(record,groups,classes):
    c=record['raw_representative']['counts'];v=flat(c);need(len(v)==720 and v==min(images(v)),'canonical full counts');digest=hashlib.sha256(bytes(v)).hexdigest();need(record['full_count_profile_sha256']==digest and record['case_id']=='exact_eight_'+digest,'case digest')
    ds=domain_record(c,groups,classes);need([r['group']for r in ds if not r['balanced']]==record['raw_representative']['exceptional_groups'],'exception list');return ds
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={};controls=[]
    def pin(p,w=None):
        v=sha(p);need(w is None or v==w,'pin '+key(p));bindings[key(p)]=v
    def reject(name,fn):
        try:fn()
        except (ValueError,AssertionError,IndexError,KeyError):controls.append(dict(name=name,rejected=True));return
        raise ValueError('corruption accepted '+name)
    try:
        for p,v in PINS.items():pin(p,v)
        for p in[Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        for p in[A/'theory_20260930_exact_eight_population_inventory.py',A/'theory_20260930_exact_eight_population_inventory_spec.md',B/'20260930_exact_eight_population_inventory/failure.json',B/'20260930_exact_eight_population_inventory/correction.json']:pin(p)
        gate=read(GATE);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','encoding premise')
        for p in[MANIFEST,BATCH,RAW,LOCAL]:need(gate['inputs_sha256'].get(key(p))==PINS[p],'direct gate binding')
        raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));need(len(groups)==20 and all(len(s)==6 and len({a//2 for a in s})==6 for s in groups),'matching-free support groups')
        local=read(LOCAL);words,triples,classes=catalogue(local);u=read(MANIFEST);need(u['universe_size']==len(u['records'])==792 and not u['historical_profiles_subtracted']and not u['prior_exclusions_used'],'complete un-subtracted universe')
        need([(r['subset_index'],r['full_count_profile_sha256'])for r in u['records']]==sorted((r['subset_index'],r['full_count_profile_sha256'])for r in u['records']),'exact order');need(len({r['case_id']for r in u['records']})==792,'unique case ids')
        records=[];hist=Counter();group_hist=Counter();bysign=Counter()
        for i,r in enumerate(u['records']):
            need(r['case_index']==i,'case index');domains=validate_case(r,groups,classes);sizes=[d['size']for d in domains];size=dims(sizes);hist[tuple(size.values())]+=1;group_hist.update(sizes);bysign.update(tuple(d['signature'])for d in domains)
            records.append(dict(case_id=r['case_id'],case_index=i,subset_index=r['subset_index'],full_count_profile_sha256=r['full_count_profile_sha256'],domains=domains,initial_domain_sizes=sizes,computed_formula_dimensions=size,dimension_status='computed from frozen schema; no new formula built'))
        byid={r['case_id']:r for r in records};measurements=[]
        def measure(folder,label,expected=None):
            for name in['summary.json','scope.json','model.json','instance.cnf']:pin(folder/name)
            model=read(folder/'model.json');scope=read(folder/'scope.json');ds=domain_record(scope['coordinate_group_fibre_counts'],groups,classes);sizes=[d['size']for d in ds];computed=dims(sizes);need([len(d['choices'])for d in model['domains']]==sizes,'actual initial size calibration')
            for g,d in enumerate(model['domains']):
                if not ds[g]['balanced']:need([c['local_survivor_index']for c in d['choices']]==ds[g]['local_survivor_indices'],'actual complete exceptional rank list')
            need({k:model['primary_selectors']if k=='selectors'else model[k]for k in computed}==computed,'measured model dimensions')
            with(folder/'instance.cnf').open('rb')as f:header=f.readline();lines=sum(1 for _ in f)
            need(header==f"p cnf {computed['variables']} {computed['clauses']}\n".encode()and lines==computed['clauses'],'actual CNF header/body line count')
            canonical=hashlib.sha256(bytes(min(images(flat(scope['coordinate_group_fibre_counts']))))).hexdigest();cid='exact_eight_'+canonical
            if expected:need(expected['case_id']==cid and expected['initial_domain_sizes']==sizes,'campaign raw measured identity')
            row=dict(label=label,folder=key(folder),actual_sizes=sizes,measured_formula_dimensions=computed,actual_cnf_bytes=(folder/'instance.cnf').stat().st_size,actual_model_bytes=(folder/'model.json').stat().st_size,canonical_case_id=cid,in_all792=cid in byid,raw_formula_built_before_inventory=True);measurements.append(row)
        batch=read(BATCH)
        for r in batch['records']:
            for entry in r['files'].values():pin(ROOT/entry['path'],entry['sha256'])
            measure((ROOT/r['files']['model.json']['path']).parent,'first12',byid[r['case_id']])
        for name,hashes in HIST.items():
            folder=B/name
            for file,h in zip(['summary.json','scope.json','model.json'],hashes):pin(folder/file,h)
            measure(folder,'historical literal calibration')
        damaged=copy.deepcopy(u['records'][0]);damaged['raw_representative']['counts'][0][0][0]+=1;reject('changed count',lambda:validate_case(damaged,groups,classes))
        damaged2=copy.deepcopy(u['records'][0]);damaged2['full_count_profile_sha256']='0'*64;reject('changed digest',lambda:validate_case(damaged2,groups,classes))
        for label,bad in [('missing local triple',local['survivors'][:-1]),('duplicate local triple',local['survivors']+[local['survivors'][0]])]:
            x=dict(local,survivors=bad);reject(label,lambda x=x:catalogue(x))
        reject('nineteen domain sizes',lambda:dims([150]*19));reject('zero domain size',lambda:dims([0]+[150]*19))
        positive=dims([48]*8+[150]*12);need(positive==dict(selectors=2184,variables=9748,clauses=167416),'known positive dimensions');reject('wrong variable count',lambda:need(positive['variables']==9749,'wrong V'));reject('wrong clause count',lambda:need(positive['clauses']==167415,'wrong C'))
        expected=records[0]['domains'][0]['local_survivor_indices'];reject('missing rank',lambda:need(expected[:-1]==expected,'rank'));reject('duplicate rank',lambda:need(expected+[expected[0]]==expected,'rank'))
        reject('malformed header',lambda:need(b'p cnf 9748 167415\n'==b'p cnf 9748 167416\n','header'))
        save(out/'records.json',dict(complete=True,records=records));save(out/'signature_classes.json',dict(records=[dict(signature=list(s),local_survivor_indices=ids,campaign_group_occurrences=bysign[s])for s,ids in sorted(classes.items())]));save(out/'measurements.json',dict(records=measurements,performance_extrapolation=False));save(out/'controls.json',dict(rejections=controls,balanced_bijection=150,complete_local_triples=31110,examined_triples=117480))
        elapsed=time.monotonic()-start;need(elapsed<120,'120s inventory bound');save(out/'summary.json',dict(status='CANDIDATE_EXACT_EIGHT_ALL792_RESOURCE_DOMAIN_INVENTORY_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=bindings,outputs_sha256={key(p):sha(p)for p in out.iterdir()},complete=True,cases=792,formula_dimension_distribution=[dict(selectors=s,estimated_variables=v,estimated_clauses=c,cases=n)for(s,v,c),n in sorted(hist.items())],group_domain_size_distribution=dict(sorted(group_hist.items())),sum_estimated_variables=sum(r['computed_formula_dimensions']['variables']for r in records),sum_estimated_clauses=sum(r['computed_formula_dimensions']['clauses']for r in records),built_first12_measurements=12,historical_measurements=4,new_formula_builds=0,native_calls=0,independent_approval=False,elapsed_seconds=elapsed,scope='All792 exact initial domains and frozen-schema dimension estimates, calibrated against16 existing literal build records. Historical records may overlap; no outcome subtraction or performance inference.'))
        print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),distribution=[dict(selectors=s,variables=v,clauses=c,cases=n)for(s,v,c),n in sorted(hist.items())],seconds=elapsed)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=bindings,new_formula_builds=0,native_calls=0));raise
if __name__=='__main__':main()
