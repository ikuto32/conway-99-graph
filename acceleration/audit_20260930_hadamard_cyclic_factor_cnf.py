"""Independent literal cyclic domains, threshold clauses and all column caps."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
import audit_20260930_eight_full99_cnf_v1 as gates
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_six_prism_cyclic_cnf';RAW=B/'20260930_hadamard20_support/six_prism.json'
RAW_SHA='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
GATES_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save
def read(p):return json.loads(Path(p).read_bytes())

def reconstruct(raw):
    matching=[i^1 for i in range(12)];need(raw['matchings']==[matching]*3,'literal three standard matchings')
    c=[[int((i//12==j//12 and (i%12)^1==j%12) or (i//12!=j//12 and i%12==j%12)) for j in range(36)] for i in range(36)]
    need(c==raw['core_adjacency'],'complete six-prism core')
    neighbors=[{j for j,v in enumerate(row) if v} for row in c]
    gram=[[12*int(i==j)-c[i][j]-len(neighbors[i]&neighbors[j])+2-int(i//12==j//12) for j in range(36)] for i in range(36)]
    need(gram==raw['prescribed_Gram36'],'integer full Gram definition')
    l=raw['L'];need(len(l)==12 and all(len(r)==60 and all(type(v)is int and v in (0,1) for v in r) and sum(r)==30 for r in l),'binary coordinate support margins')
    supports=[tuple(a for a in range(12) if l[a][d]) for d in range(60)]
    need([list(s) for s in supports]==raw['support_columns'] and all(len(s)==6 and all(sum(a//2==b for a in s)==1 for b in range(6)) for s in supports),'one coordinate from each component')
    groups=[]
    for d,s in enumerate(supports):
        if s not in [x[0] for x in groups]:groups.append((s,[e for e,t in enumerate(supports) if t==s]))
    need(len(groups)==20 and all(len(cols)==3 for _,cols in groups),'twenty distinct supports, each three columns')
    words=[]
    for a in combinations(range(6),2):
        for b in combinations([j for j in range(6) if j not in a],2):words.append(tuple(0 if j in a else 1 if j in b else 2 for j in range(6)))
    words.sort();gauge=[w for w in words if w[0]==0];need(len(words)==90 and len(gauge)==30,'complete balanced phase-gauged domains')
    for w in words:
        normalized=tuple((v-w[0])%3 for v in w);need(normalized in gauge and sorted(tuple((v+r)%3 for v in w) for r in range(3))==sorted(tuple((v+r)%3 for v in normalized) for r in range(3)),'phase gauge permutes repeated columns')
    domains=[]
    for p,(coords,columns) in enumerate(groups):
        choices=[]
        for j,w in enumerate(gauge):
            rows=[[12*g+a for g in range(3) for a,t in zip(coords,w) if (t+r)%3==g] for r in range(3)]
            choices.append(dict(selector=1+30*p+j,choice_index=j,coloring=list(w),lifted_rows=rows,lifted_masks_hex=[format(sum(1<<i for i in s),'09x') for s in rows]))
        domains.append(dict(group=p,support_coordinates=list(coords),raw_columns=columns,choices=choices))
    pairs=[dict(coordinates=[a,b],containing_groups=[p for p,(s,_) in enumerate(groups) if a in s and b in s]) for a,b in combinations(range(12),2) if b!=(a^1)]
    need(len(pairs)==60 and all(len(p['containing_groups'])==5 for p in pairs),'every nonmatching coordinate pair in five base supports')
    return c,gram,l,domains,pairs

def scope_check(model,scope,raw):
    c,gram,l,domains,pairs=reconstruct(raw)
    need(scope['schema']=='FIXED_HADAMARD_SIX_PRISM_CYCLIC_FACTOR_SCOPE_V1','scope schema')
    for field,want in [('matchings',raw['matchings']),('core_adjacency',c),('target_gram36',gram),('L',l),('domains',domains),('coordinate_pairs',pairs),('first_coordinate_color',0),('within_group_phase_by_sorted_column',[0,1,2]),('extra_cyclic_factor_constraint',True),('arbitrary_fixedL_factors_covered',False),('all_D_unencoded',True),('target_graph',False),('no_target_automorphism_assumed',True)]:need(type(scope[field])is type(want) and scope[field]==want,'scope '+field)
    need(scope['raw_support']==key(RAW) and scope['raw_support_sha256']==RAW_SHA,'exact literal support binding')
    need(model['schema']=='HADAMARD_SIX_PRISM_CYCLIC_FACTOR_PREFIX_CNF_V1' and model['primary_selectors']==600 and model['domains']==domains and model['full_target_encoded'] is False,'primary scope and domain')
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json'),'scope identity')
    return domains,pairs,gram

def cap_table(left,right):
    maps=[];hist=Counter();forbidden=[]
    for x in left['choices']:
        masks=[set(s) for s in x['lifted_rows']];bits=0
        for j,y in enumerate(right['choices']):
            maximum=max(len(s&set(t)) for s in masks for t in y['lifted_rows']);hist[maximum]+=1
            if maximum>2:bits|=1<<j;forbidden.append(tuple(sorted([-x['selector'],-y['selector']])))
        maps.append(format(bits,'08x'))
    return maps,{str(k):v for k,v in sorted(hist.items())},forbidden

def check_cnf(model,scope,raw,path):
    domains,pairs,gram=scope_check(model,scope,raw);rows=model['counter_rows'];rowi=0;sections=[];forbidden_count=0;local_entries=0
    with Path(path).open('rb') as f:
        need(f.readline()==f"p cnf {model['variables']} {model['clauses']}\n".encode(),'exact CNF header')
        cursor=gates.ClauseCursor(f,model['variables']);audit=gates.GateAudit(cursor,600);first=1
        for domain in domains:audit.counter(rows[rowi],[x['selector'] for x in domain['choices']],1,True,dict(kind='group_exactone',group=domain['group']));rowi+=1
        sections.append(dict(kind='20group_exactone',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));first=cursor.count+1
        for pair in pairs:
            a,b=pair['coordinates']
            for difference in range(3):
                inputs=[]
                for p in pair['containing_groups']:
                    domain=domains[p];ia=domain['support_coordinates'].index(a);ib=domain['support_coordinates'].index(b)
                    for choice in domain['choices']:
                        delta=(choice['coloring'][ib]-choice['coloring'][ia])%3
                        if difference==0:
                            for g,h in product(range(3),repeat=2):
                                need(sum(int(12*g+a in r and 12*h+b in r) for r in choice['lifted_rows'])==int((h-g)%3==delta),'literal full-Gram local coefficient');local_entries+=1
                        if delta==difference:inputs.append(choice['selector'])
                audit.counter(rows[rowi],inputs,[1,2,2][difference],True,dict(kind='coordinate_difference_count',coordinates=[a,b],difference=difference));rowi+=1
        sections.append(dict(kind='180exact_difference_counts',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));first=cursor.count+1
        for index,(p,q) in enumerate(combinations(range(20),2)):
            start=cursor.count+1;maps,hist,clauses=cap_table(domains[p],domains[q]);cursor.consume(clauses);forbidden_count+=len(clauses)
            expected=dict(groups=[p,q],actual_column_pairs=[[d,e] for d in domains[p]['raw_columns'] for e in domains[q]['raw_columns']],forbidden_right_masks_hex=maps,maximum_overlap_histogram=hist,first_clause=start,clause_count=len(clauses))
            need(model['lifted_cap_relations'][index]==expected,'entire raw cap table and clause segment')
        sections.append(dict(kind='190all_lifted_cap_choice_relations',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));need(f.read()==b'','no extra clauses')
    need(len(model['lifted_cap_relations'])==190 and rowi==len(rows)==200,'exact complete populations')
    need(model['clause_sections']==sections and model['variables']==audit.top and model['clauses']==cursor.count,'all variables, clause ranges and totals')
    return dict(variables=audit.top,clauses=cursor.count,primary_selectors=600,onehot_rows=20,difference_equalities=180,group_pair_choice_checks=190*900,lifted_column_pair_checks=190*900*9,actual_column_pairs_covered=1770,withintriplet_pairs_automatically_disjoint=60,forbidden_choice_pairs=forbidden_count,literal_Gram_coefficient_checks=local_entries,clause_sections=sections)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reduction-gate',type=Path,required=True);ap.add_argument('--reduction-gate-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};started=time.monotonic()
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact identity '+key(p));bindings[key(p)]=value
    try:
        pin(D/'summary.json','ef468795786fae63bdaa21e15fa3d81968b6a87e14d5ceb4076858cbdaa20190');prod=read(D/'summary.json')
        for p,h in {**prod['inputs_sha256'],**prod['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(args.reduction_gate,args.reduction_gate_sha256);reduction=read(args.reduction_gate);need(reduction['status']=='INDEPENDENT_HADAMARD_CYCLIC_FACTOR_REDUCTION_PASS','separate mathematical reduction review')
        need(RAW_SHA in json.dumps(reduction) and digest(D/'scope.json') in json.dumps(reduction),'reduction binds literal raw and scope')
        pin(Path(gates.__file__),GATES_SHA);pin(RAW,RAW_SHA);raw=read(RAW);model=read(D/'model.json');scope=read(D/'scope.json');counts=check_cnf(model,scope,raw,D/'instance.cnf')
        for k in ['variables','clauses','onehot_rows','difference_equalities','group_pair_choice_checks','lifted_column_pair_checks','actual_column_pairs_covered','withintriplet_pairs_automatically_disjoint','forbidden_choice_pairs','clause_sections']:need(prod[k]==counts[k],'producer count '+k)
        controls=gates.controls();rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(label)
            else:raise ValueError('accepted corrupted artifact '+label)
        for label in ['raw_L','core','all_factors','target_symmetry','deleted_choice','selector','lifted_phase','raw_column']:
            bad=deepcopy(scope)
            if label=='raw_L':bad['L'][0][0]^=1
            elif label=='core':bad['core_adjacency'][0][1]^=1
            elif label=='all_factors':bad['arbitrary_fixedL_factors_covered']=True
            elif label=='target_symmetry':bad['no_target_automorphism_assumed']=False
            elif label=='deleted_choice':bad['domains'][0]['choices'].pop()
            elif label=='selector':bad['domains'][0]['choices'][0]['selector']+=1
            elif label=='lifted_phase':bad['domains'][0]['choices'][0]['lifted_rows'].reverse()
            else:bad['domains'][0]['raw_columns'][0]+=1
            reject(label,lambda bad=bad:scope_check(model,bad,raw))
        left=scope['domains'][0];right=scope['domains'][1];maps,hist,cl=cap_table(left,right)
        need(sum(hist.values())==900,'complete positive cap inventory');bad=deepcopy(model);bad['counter_rows'][0]['bound']=2
        reject('counter_bound',lambda:check_cnf(bad,scope,raw,D/'instance.cnf'))
        bad=deepcopy(model);bad['lifted_cap_relations'][0]['forbidden_right_masks_hex'][0]='ffffffff'
        reject('cap_bitmap',lambda:check_cnf(bad,scope,raw,D/'instance.cnf'))
        save(out/'controls.json',dict(prefix_truth_controls=controls,fresh_artifact_corruptions_rejected=rejected,full_research_positive=None,full_research_positive_reason='No satisfying research factor is known; local controls and complete truth relations are disclosed separately.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_CYCLIC_FACTOR_CNF.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_FIXED_SUPPORT_CYCLIC_COLORING_CNF_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},counts=counts,verifier='/root/state_literature_audit',method='independent_literal_domain_and_truth_relation_CNF_check',shared_components=['Frozen independent GateAudit: full relation truth tables and prefix induction; Python standard library and tqdm.','No producer domain/encoder/decoder/solver imports.'],recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0,limitations=['One fixed six-prism L and additional cyclic three-column restriction; not all fixed-L factors.','Phase gauge is a column relabelling inside this family, not a target automorphism premise.','Residual D and full99 completion omitted.'],elapsed_seconds=time.monotonic()-started)
        save(out/'summary.json',report);save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-COLORING-CNF',revision=1,statement='The authenticated26360-variable122394-clause CNF is satisfiable exactly when the frozen six-prism coordinate support L admits a binary36x60 prescribed-Gram factor with all1770 column-pair caps and the explicitly prescribed cyclic fibre-triplet restriction, modulo the documented within-triplet phase normalization.',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope=report['limitations'][0],assumptions=['No nontrivial target automorphism is assumed.'],dependencies=[],dependency_note='Separate cyclic-reduction gate bound directly; parent must pin its eventual ledger ID/revision after registration.',evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],verifier=report['verifier'],method=report['method'],limitations=report['limitations'],created_at=now,updated_at=now));print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
