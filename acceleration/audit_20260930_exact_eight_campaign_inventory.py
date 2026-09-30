"""Independent finite domains and recipe dimensions; no producer imports."""
import argparse, copy, gzip, hashlib, itertools as it, json, math, platform, sys, time, traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'acceleration'; B=A/'results'; I=B/'20260930_independent_review'
SRC=Path(__file__).resolve(); SPEC=SRC.with_name(SRC.stem+'_spec.md'); DOC=ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_CAMPAIGN_INVENTORY.md'
INV=B/'20260930_exact_eight_population_inventory_v2/summary.json'
POP=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json'
RAW=B/'20260930_hadamard20_support/six_prism.json'; LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
ENC=I/'exact_eight_campaign/summary.json'; COVER=I/'exact_eight_campaign_coverage_v2/summary.json'
PINS={INV:'8cb37b82158b59168187622287234e920466819401168a0a43628bb53860e3a3',POP:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',ENC:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',COVER:'f6b468e80410caaedbbb88ce02cef79e0a693168df0eb9134d8d4d8e62b96223'}
def need(x,m):
    if not x: raise ValueError(m)
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def packed(x):return json.dumps(x,separators=(',',':'),sort_keys=True).encode()
def gzsave(p,x):
    with p.open('xb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as z:z.write(packed(x)+b'\n')
def equal(a,b,m):need(a==b,m)
def shape(c):
    need(len(c)==12 and all(len(r)==20 and all(len(t)==3 and all(type(v)is int and 0<=v<=3 for v in t) for t in r)for r in c),'literal count shape')
def canonical(c):
    shape(c);v=bytes(v for row in c for t in row for v in t)
    return min(bytes(v[i+p[f]] for i in range(0,720,3)for f in range(3))for p in it.permutations(range(3)))
def dimensions(sizes):
    need(len(sizes)==20 and all(type(n)is int and n>=2 for n in sizes),'complete positive domains')
    s=sum(sizes);channels=60*9*5*2
    onehot=sum(2+4*(n-2)+2 for n in sizes)
    cc=180*(math.comb(10,2)+1)+360*(math.comb(10,3)+math.comb(10,9))
    return dict(selectors=s,variables=s+sum(n-1 for n in sizes)+channels,clauses=onehot+45*s+channels+cc)
def regenerate():
    words=[]
    for z in it.combinations(range(6),2):
        for o in it.combinations([a for a in range(6)if a not in z],2):words.append(tuple(0 if a in z else 1 if a in o else 2 for a in range(6)))
    words.sort();need(len(set(words))==90,'90 words')
    pairs=list(it.combinations(range(6),2));diag=sum(1<<(9*k+4*f)for k in range(15)for f in range(3))
    masks=[sum(1<<(9*k+3*w[a]+w[b])for k,(a,b)in enumerate(pairs))for w in words]
    overlaps=[[sum(x==y for x,y in zip(u,v))for v in words]for u in words]
    triples=[];cap_only=0;extras=[];classes=defaultdict(list)
    for a,b,c in it.combinations(range(90),3):
        if max(overlaps[a][b],overlaps[a][c],overlaps[b][c])>2:continue
        cap_only+=1;x,y,z=masks[a],masks[b],masks[c]
        if (((x&y)|(x&z)|(y&z))&diag)or(x&y&z):extras.append([a,b,c]);continue
        t=[a,b,c];sig=tuple(sum(words[j][p]==f for j in t)for p in range(6)for f in range(3))
        classes[sig].append(len(triples));triples.append(t)
    equal(cap_only,35700,'cap-only population');equal(len(triples),31110,'complete predicate population');equal(len(classes),6061,'count classes')
    # All-option coefficient-sum identity, independently literal over15x9 cells.
    for t in triples:
        total=0
        for a,b in pairs:
            counts=[0]*9
            for j in t:counts[3*words[j][a]+words[j][b]]+=1
            need(all(n<= (1 if f==h else 2)for n,(f,h)in zip(counts,it.product(range(3),repeat=2))),'local Gram bounds')
            total+=sum(int(n>=1)+int(n>=2)for n in counts)
        equal(total,45,'weighted-channel incidence sum')
    balanced=classes[(1,)*18];equal(len(balanced),150,'balanced size')
    for i in balanced:equal([words[j][0]for j in triples[i]],[0,1,2],'sorted normalization gives first-coordinate identity')
    return words,triples,dict(classes),extras
def domains(c,groups,classes):
    shape(c)
    for a in range(12):
        for g,support in enumerate(groups):equal(sum(c[a][g]),3 if a in support else 0,'support counts')
        for f in range(3):equal(sum(c[a][g][f]for g in range(20)),10,'row margins')
    result=[]
    for g,support in enumerate(groups):
        sig=tuple(v for a in support for v in c[a][g]);need(sig in classes,'complete available local signature')
        ids=classes[sig];result.append(dict(group=g,signature=list(sig),local_survivor_indices=ids,size=len(ids),balanced=sig==(1,)*18))
    equal(sum(not r['balanced']for r in result),8,'eight exceptions');return result
def or_clauses(z,xs):return [[z,-x]for x in xs]+[[-z,*xs]]
def onehot(n):
    xs=list(range(1,n+1));ps=list(range(n+1,2*n));cs=[[ps[0],-xs[0]],[-ps[0],xs[0]]]
    for j in range(1,n-1):cs.extend([[ps[j],-ps[j-1]],[ps[j],-xs[j]],[-ps[j],ps[j-1],xs[j]],[-ps[j-1],-xs[j]]])
    return cs+[[ps[-1],xs[-1]],[-ps[-1],-xs[-1]]]
def sat(cs,v):return all(any(v[abs(x)-1]==(x>0)for x in row)for row in cs)
def cnf_line(line,v):
    t=[int(x)for x in line.split()];need(t and t[-1]==0 and t[:-1]and all(x and abs(x)<=v for x in t[:-1]),'DIMACS clause syntax and IDs')
def controls():
    rows=Counter();bad=[]
    for n in range(2,7):
        cs=onehot(n);equal(len(cs),4*n-4,'small onehot size')
        for v in it.product([False,True],repeat=2*n-1):
            equal(sat(cs,v),sum(v[:n])==1 and all(v[n+j]==any(v[:j+1])for j in range(n-1)),'small prefix truth');rows['prefix']+=1
    for n in range(6):
        for v in it.product([False,True],repeat=n+1):equal(sat(or_clauses(n+1,list(range(1,n+1))),v),v[-1]==any(v[:-1]),'OR exact truth');rows['OR']+=1
    for k in [1,2]:
        cs=[[-x for x in t]for t in it.combinations(range(1,11),k+1)]+[list(t)for t in it.combinations(range(1,11),11-k)]
        equal(len(cs),46 if k==1 else 130,'exact count size')
        for v in it.product([False,True],repeat=10):equal(sat(cs,v),sum(v)==k,'exact count truth');rows['count']+=1
    def reject(name,fn):
        try:fn()
        except(ValueError,AssertionError,KeyError,IndexError,TypeError):bad.append(name);return
        raise ValueError('accepted corruption '+name)
    for name,line in [('missing zero','1 -2'),('interior zero','1 0 2 0'),('overflow','11 0'),('empty','0')]:reject(name,lambda line=line:cnf_line(line,10))
    reject('missing domain',lambda:dimensions([150]*19));reject('singleton domain',lambda:dimensions([1]+[150]*19))
    return dict(truth_cases=dict(rows),rejected=bad),reject
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        p=p.resolve();name=key(p);need('hadamard_oriented_unknown/process.stdout.log'not in name,'protected path');v=sha(p);need(h is None or h==v,'hash '+name);pins[name]=v
    try:
        for p,h in PINS.items():pin(p,h)
        for p in[SRC,SPEC,DOC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        summary=read(INV)
        for name,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/name,h)
        equal(summary['status'],'CANDIDATE_EXACT_EIGHT_ALL792_RESOURCE_DOMAIN_INVENTORY_COMPLETE','candidate status')
        eg=read(ENC);cg=read(COVER);equal(eg['status'],'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','actual12 prior encoding');equal(cg['status'],'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_COVERAGE_TRANSPORT_PASS','complete population gate')
        for p in[POP,RAW,LOCAL]:equal(cg['inputs_sha256'][key(p)],PINS[p],'prior raw population premise')
        ctl,reject=controls();words,triples,classes,extras=regenerate();local=read(LOCAL)
        equal(local['words'],[list(w)for w in words],'all raw words');equal(local['survivors'],triples,'all raw local ranks')
        reject('cap-only false positive',lambda:need([0,5,42]in triples,'cap-only is not full predicate'))
        need([0,5,42]in extras,'explicit cap-only counterexample');ctl['cap_only_false_positives']=len(extras)
        reject('missing local triple',lambda:equal(local['survivors'][:-1],triples,'complete triples'));reject('duplicate local triple',lambda:equal(local['survivors']+[triples[0]],triples,'unique triples'))
        raw=read(RAW);L=raw['L'];groups=list(dict.fromkeys(tuple(a for a in range(12)if L[a][j])for j in range(60)))
        need(len(groups)==20 and all(len(g)==6 and len({a//2 for a in g})==6 for g in groups),'literal supports')
        equal(Counter(sum(a in s and b in s for s in groups)for a,b in it.combinations(range(12),2)),Counter({5:60,0:6}),'five-group pair incidence')
        pop=read(POP);equal(len(pop['records']),792,'all792 population');expected=[];hist=Counter();dh=Counter();occ=Counter();ids=set()
        for i,r in enumerate(pop['records']):
            equal(r['case_index'],i,'stable case order');c=r['raw_representative']['counts'];can=canonical(c);flat=bytes(v for row in c for t in row for v in t);equal(can,flat,'canonical raw counts');digest=hashlib.sha256(flat).hexdigest()
            equal(r['full_count_profile_sha256'],digest,'count digest');equal(r['case_id'],'exact_eight_'+digest,'case ID');need(r['case_id']not in ids,'unique population');ids.add(r['case_id'])
            ds=domains(c,groups,classes);equal([d['group']for d in ds if not d['balanced']],r['raw_representative']['exceptional_groups'],'literal exceptions');sizes=[d['size']for d in ds];di=dimensions(sizes)
            expected.append(dict(case_id=r['case_id'],case_index=i,subset_index=r['subset_index'],full_count_profile_sha256=digest,domains=ds,initial_domain_sizes=sizes,computed_formula_dimensions=di,dimension_status='computed from frozen schema; no new formula built'))
            hist[tuple(di.values())]+=1;dh.update(sizes);occ.update(tuple(d['signature'])for d in ds)
        equal(read(INV.parent/'records.json'),dict(complete=True,records=expected),'all792 complete inventory records')
        equal(read(INV.parent/'signature_classes.json'),dict(records=[dict(signature=list(s),local_survivor_indices=v,campaign_group_occurrences=occ[s])for s,v in sorted(classes.items())]),'all6061 full classes and occurrences')
        dist=[dict(selectors=s,estimated_variables=v,estimated_clauses=c,cases=n)for(s,v,c),n in sorted(hist.items())]
        equal(summary['formula_dimension_distribution'],dist,'all dimension classes');equal(summary['group_domain_size_distribution'],{str(k):v for k,v in sorted(dh.items())},'all group-domain sizes')
        for field,k in [('sum_estimated_variables','variables'),('sum_estimated_clauses','clauses')]:equal(summary[field],sum(r['computed_formula_dimensions'][k]for r in expected),'total estimates')
        # Mutation tests traverse actual domain/count checks rather than producer metadata.
        damaged=copy.deepcopy(pop['records'][0]['raw_representative']['counts']);damaged[0][0][0]+=1;reject('count marginal corruption',lambda:domains(damaged,groups,classes))
        reject('rank list omission',lambda:equal(expected[0]['domains'][0]['local_survivor_indices'][:-1],expected[0]['domains'][0]['local_survivor_indices'],'ranks'))
        wrong=copy.deepcopy(expected[0]);wrong['computed_formula_dimensions']['variables']+=1;reject('wrong variable formula',lambda:equal(wrong['computed_formula_dimensions'],dimensions(wrong['initial_domain_sizes']),'variables'))
        wrong=copy.deepcopy(expected[0]);wrong['computed_formula_dimensions']['clauses']-=1;reject('wrong clause formula',lambda:equal(wrong['computed_formula_dimensions'],dimensions(wrong['initial_domain_sizes']),'clauses'))
        measured=[];ms=read(INV.parent/'measurements.json');equal(len(ms['records']),16,'12 plus4 measurements');equal(ms['performance_extrapolation'],False,'no extrapolation')
        for record in ms['records']:
            folder=ROOT/record['folder'];model=read(folder/'model.json');scope=read(folder/'scope.json');ds=domains(scope['coordinate_group_fibre_counts'],groups,classes);sizes=[d['size']for d in ds];di=dimensions(sizes)
            for name in['summary.json','model.json','scope.json','instance.cnf']:need(key(folder/name)in pins,'measured artifact directly authenticated')
            for d,sd in zip(model['domains'],ds):
                equal(len(d['choices']),sd['size'],'actual domain cardinality');expected_triples={tuple(triples[j])for j in sd['local_survivor_indices']};actual=[]
                for option in d['choices']:
                    tri=tuple(words.index(tuple(w))for w in option['colour_words']);need(list(tri)==sorted(tri),'actual normalized words');actual.append(tri)
                    equal(option['lifted_rows'],[[12*w[p]+a for p,a in enumerate(groups[d['group']])]for w in option['colour_words']],'actual literal lifted rows')
                need(len(set(actual))==len(actual)and set(actual)==expected_triples,'actual entire domain not pruned')
            equal(model['primary_selectors'],di['selectors'],'actual selectors');equal(model['variables'],di['variables'],'actual vars');equal(model['clauses'],di['clauses'],'actual clauses')
            equal(model['variable_populations'],dict(selectors=di['selectors'],onehot_prefixes=di['selectors']-20,weighted_threshold_channels=5400),'actual variable section counts')
            equal(model['clause_populations'],dict(onehot=4*di['selectors']-80,channels=45*di['selectors']+5400,counts=55080),'actual clause section counts')
            count=0
            with(folder/'instance.cnf').open('rb')as f:
                equal(f.readline(),f"p cnf {di['variables']} {di['clauses']}\n".encode(),'actual DIMACS header')
                for line in f:cnf_line(line,di['variables']);count+=1
            equal(count,di['clauses'],'every actual clause line');cid='exact_eight_'+hashlib.sha256(canonical(scope['coordinate_group_fibre_counts'])).hexdigest()
            calculated=dict(label=record['label'],folder=record['folder'],actual_sizes=sizes,measured_formula_dimensions=di,actual_cnf_bytes=(folder/'instance.cnf').stat().st_size,actual_model_bytes=(folder/'model.json').stat().st_size,canonical_case_id=cid,in_all792=cid in ids,raw_formula_built_before_inventory=True)
            equal(record,calculated,'every measured value');measured.append(calculated)
        equal(sum(r['label']=='first12'for r in measured),12,'actual first12');equal(sum(r['label']=='historical literal calibration'for r in measured),4,'four historical controls')
        first12=[r['canonical_case_id']for r in measured if r['label']=='first12'];equal(first12,pop['first_batch_case_ids'],'actual12 exact case selection')
        need(len(hist)==16 and min(s for s,v,c in hist)==1978 and max(s for s,v,c in hist)==2184,'finite size endpoints')
        ctl.update(complete_triples=31110,signature_classes=6061,balanced_normalization=150,all_option_weighted_sums_checked=31110)
        save(out/'controls.json',ctl);save(out/'measured_files.json',dict(records=measured,new_semantic_clause_audit=False,prior_full12_clause_gate=key(ENC)))
        gzsave(out/'independent_inventory.json.gz',dict(records=[{k:v for k,v in r.items()if k!='domains'}for r in expected],domain_records_checked=15840,complete_class_ranklists_checked=6061))
        elapsed=time.monotonic()-start;need(elapsed<180,'bounded audit allocation');stamp=datetime.now(timezone.utc).isoformat()
        result=dict(status='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_INVENTORY_PASS',created_at=stamp,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},cases=792,initial_domains=15840,signature_classes=6061,local_triples=31110,formula_dimension_distribution=dist,group_domain_size_distribution=dict(sorted(dh.items())),sum_estimated_variables=summary['sum_estimated_variables'],sum_estimated_clauses=summary['sum_estimated_clauses'],actual_formula_measurements=16,actual_first12=12,historical_controls=4,new_formula_builds=0,native_calls=0,elapsed_seconds=elapsed,method='Independent placement-word enumeration and bit-plane full local predicate; exact complete domain comparisons; analytic component dimension derivation; actual DIMACS syntax/count/header and full model-domain checks.',shared_components=['Only Python standard library; raw catalogue/count inputs and prior independent population/actual12 gates. No repository imports.'],limitations=['Unbuilt formula dimensions are recipe estimates, not measured artifacts.','Actual first12 full clause semantics rely on separately pinned encoding gate; this audit checks domains/dimensions/lines.','No performance, proof-size, factor-existence, exclusion or whole-target conclusion.'],artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',result)
        binding=dict(claim_id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-DOMAIN-INVENTORY',revision=1,status_recommendation='VERIFIED',kind='mathematical result',basis='COMPUTED',statement='The authenticated complete792 canonical exactly-eight count tables have the complete initial local domains recorded in the frozen inventory, with16 selector-size classes S from1978 to2184. For the frozen weighted-threshold recipe their formula dimensions are V=2S+5380 and C=49S+60400; the12 saved campaign formulas and four named historical builds match the independently derived dimensions and complete initial domains.',scope='Finite complete domain inventory and conditional recipe dimensions on the literal fixed support; actual saved formula measurements are distinguished from unbuilt estimates. No performance or feasibility claim.',assumptions='Authenticated literal support, complete count population, full local Gram upper bounds and within-group column caps; equal-support column normalization only.',dependencies=[dict(claim_id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIBRE-COVERAGE',revision=1,relation='coverage'),dict(claim_id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='uses_result')],verifier='Independent state_literature_audit checker; no producer imports',method=result['method'],created_at=stamp,updated_at=stamp,verification=dict(status=result['status'],report=key(out/'summary.json'),report_sha256=sha(out/'summary.json'),source=key(SRC),source_sha256=sha(SRC)),evidence=[key(INV),key(out/'summary.json'),key(DOC)],artifact_availability='LOCAL_ONLY',limitations=result['limitations'])
        save(out/'claim_binding.json',binding);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=elapsed)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
