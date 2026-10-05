"""Independent fixed-L domains, complete threshold CNF, and cap coverage."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,io,json,platform,subprocess,sys,time
import audit_20260930_eight_full99_cnf_v1 as gates

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'acceleration/results/20260930_fixed_support_connected01_cnf'
RAW=ROOT/'acceleration/results/20260930_hadamard20_support/connected_01.json'
RAW_SHA='2e839fda408da18e3689ffef00de647644375a000d308f4ea306b2cbdfa37e49'
GATES_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'
need=gates.need;digest=gates.digest;key=gates.key;save=gates.save
def read(p):return json.loads(Path(p).read_bytes())

def raw_universe(raw):
    ms=raw['matchings'];need(len(ms)==3 and ms[0]==[i^1 for i in range(12)],'three matching vectors, standardM0')
    need(all(len(m)==12 and sorted(m)==list(range(12)) and all(m[i]!=i and m[m[i]]==i for i in range(12)) for m in ms),'perfect matching involutions')
    c=[[0]*36 for _ in range(36)]
    for g,a in product(range(3),range(12)):
        c[12*g+a][12*g+ms[g][a]]=1
        for h in range(3):
            if h!=g:c[12*g+a][12*h+a]=1
    need(c==raw['core_adjacency'],'literal identity-cross raw core')
    nb=[{j for j,v in enumerate(row) if v} for row in c]
    gram=[[12*int(i==j)-c[i][j]-len(nb[i]&nb[j])+2-int(i//12==j//12) for j in range(36)] for i in range(36)]
    need(gram==raw['prescribed_Gram36'],'independent integer prescribedGram')
    l=raw['L'];need(len(l)==12 and all(len(row)==60 and all(type(v)is int and v in (0,1) for v in row) and sum(row)==30 for row in l),'literal Lshape/margins')
    support=[[a for a in range(12) if l[a][y]] for y in range(60)];need(all(len(s)==6 for s in support) and support==raw['support_columns'],'literal six coordinates per column')
    domains=[];top=0;all_balanced=0;zero_rejected=0;mi_only=0
    for y,coords in enumerate(support):
        options=[]
        for first in combinations(coords,2):
            remaining=[a for a in coords if a not in first]
            for second in combinations(remaining,2):
                third=tuple(a for a in remaining if a not in second);groups=[first,second,third]
                rows=sorted(12*g+a for g,pair in enumerate(groups) for a in pair);all_balanced+=1
                if not any(c[g*12+p[0]][g*12+p[1]] for g,p in enumerate(groups)):mi_only+=1
                if any(gram[i][j]==0 for i,j in combinations(rows,2)):zero_rejected+=1;continue
                color=[next(g for g,pair in enumerate(groups) if a in pair) for a in coords]
                options.append(dict(fibres_by_sorted_coordinate=color,rows=rows,row_mask_hex=format(sum(1<<i for i in rows),'09x')))
        options.sort(key=lambda x:x['fibres_by_sorted_coordinate'])
        need(options==raw['column_colour_options'][y] and options,'complete retained raw domain')
        choices=[]
        for j,op in enumerate(options):top+=1;choices.append(dict(selector=top,option_index=j,**op))
        domains.append(dict(column=y,support_coordinates=coords,choices=choices))
    need((top,all_balanced,mi_only)==(4067,5400,4655),'frozen domain populations')
    return c,gram,l,support,domains,dict(all_balanced=all_balanced,zero_Gram_rejected=zero_rejected,retained=top,internal_matching_only=mi_only)

def scope_check(model,scope,raw):
    c,g,l,support,domains,counts=raw_universe(raw)
    need(scope['schema']=='FIXED_HADAMARD_SUPPORT_FACTOR_COLORING_SCOPE_V1' and scope['core_name']=='connected_01','fixed scope identity')
    for name,want in [('matchings',raw['matchings']),('core_adjacency',c),('target_gram36',g),('L',l),('support_columns',support),('domains',domains)]:need(scope[name]==want,'raw scope '+name)
    need(scope['source_raw_support']==key(RAW) and scope['source_raw_support_sha256']==RAW_SHA,'literal support pin')
    for name,want in [('cross_matchings','identity'),('column_sum_per_fibre',2),('row_sum',10),('all_distinct_column_overlap_caps',2),('complete_Gram',True),('canonical_C0_prescribed',False),('target_graph',False),('residual_D',False),('other_supports_covered',False),('no_target_automorphism_assumed',True)]:need(scope[name]==want and type(scope[name]) is type(want),'scope flag '+name)
    need(scope['domain_filter']=='All90 balanced fibre assignments minus every choice containing any full-Gram-zero rowpair, including crossfibre zeros.','explicit entailed domain pruning')
    need(model['schema']=='FIXED_SUPPORT_COLOR_SELECTOR_PREFIX_CNF_V1' and model['domains']==domains and model['primary_selectors']==4067,'all model primary variables')
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json'),'model scope binding')
    need(model['no_product_variables'] is True and model['solver_calls']==0,'no hidden product variables or result')
    return domains,g,counts

def check_cnf(model,scope,raw,path):
    domains,gram,domain_counts=scope_check(model,scope,raw);rows=model['counter_rows'];rowi=0;sections=[];cap_records=[];tested=0
    with Path(path).open('rb') as f:
        need(f.readline()==f"p cnf {model['variables']} {model['clauses']}\n".encode(),'entire CNF header')
        cursor=gates.ClauseCursor(f,model['variables']);audit=gates.GateAudit(cursor,4067);first=1
        for domain in domains:
            gates.GateAudit.counter(audit,rows[rowi],[v['selector'] for v in domain['choices']],1,True,dict(kind='column_exactly_one',column=domain['column']));rowi+=1
        sections.append(dict(kind='60column_exactone',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));first=cursor.count+1
        memberships=[[(choice['selector'],frozenset(choice['rows'])) for choice in domain['choices']] for domain in domains]
        for i in range(36):
            for j in range(i,36):
                inputs=[v for column in memberships for v,s in column if {i,j}<=s]
                audit.counter(rows[rowi],inputs,gram[i][j],True,dict(kind='full_Gram',rows=[i,j]));rowi+=1
        sections.append(dict(kind='666exactGram_uppertriangle',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1));first=cursor.count+1
        for index,(d,e) in enumerate(combinations(range(60),2)):
            begin=cursor.count+1;forbidden=[];allowed=0
            for left,s in memberships[d]:
                bits=0
                for j,(right,t) in enumerate(memberships[e]):
                    tested+=1
                    if len(s&t)>2:cursor.consume([tuple(sorted([-left,-right]))]);bits|=1<<j
                    else:allowed+=1
                forbidden.append(format(bits,'x'))
            expected=dict(columns=[d,e],forbidden_right_masks_hex=forbidden,tested_choice_pairs=len(memberships[d])*len(memberships[e]),allowed_choice_pairs=allowed,forbidden_choice_pairs=cursor.count-begin+1,first_clause=begin,clause_count=cursor.count-begin+1)
            need(model['column_cap_pairs'][index]==expected,'entire pair-cap witness/table/range');cap_records.append(expected)
        sections.append(dict(kind='1770columncap_forbidden_option_pairs',first_clause=first,last_clause=cursor.count,count=cursor.count-first+1))
        need(f.read()==b'','no extra or omitted raw clauses')
    need(rowi==len(rows)==726 and len(cap_records)==len(model['column_cap_pairs'])==1770,'complete row/pair population')
    need(model['clause_sections']==sections and model['variables']==audit.top and model['clauses']==cursor.count,'exact auxiliary universe and clause totals')
    return dict(variables=audit.top,clauses=cursor.count,primary_selectors=4067,exact_one_rows=60,Gram_rows=666,column_pairs=1770,tested_choice_pairs=tested,forbidden_choice_pairs=sum(r['forbidden_choice_pairs'] for r in cap_records),domain_counts=domain_counts,sections=sections)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--summary-sha256',required=True);ap.add_argument('--support-gate',type=Path,required=True);ap.add_argument('--support-gate-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};started=time.monotonic()
    def pin(p,h=None):
        value=digest(p);need(h is None or h==value,'artifact pin '+key(p));bindings[key(p)]=value
    try:
        pin(D/'summary.json',args.summary_sha256);prod=read(D/'summary.json')
        for p,h in {**prod['inputs_sha256'],**prod['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(args.support_gate,args.support_gate_sha256);support_gate=read(args.support_gate)
        need(support_gate['status'].startswith('INDEPENDENT_') and support_gate['status'].endswith('_PASS'),'completed independent support gate')
        need(RAW_SHA in json.dumps(support_gate),'gate directly binds selected raw support')
        pin(RAW,RAW_SHA);raw=read(RAW);pin(Path(gates.__file__),GATES_SHA)
        model=read(D/'model.json');scope=read(D/'scope.json');counts=check_cnf(model,scope,raw,D/'instance.cnf')
        for k in ['variables','clauses','primary_selectors','tested_choice_pairs','forbidden_choice_pairs']:need(prod[k]==counts[k],'actual producer result count '+k)
        controls=gates.controls();rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):rejected.append(label)
            else:raise ValueError('accepted corrupted artifact '+label)
        for label in ['wrong_L','wrong_core','different_support_coverage','symmetry_premise','deleted_domain_option','changed_selector']:
            bad=deepcopy(scope)
            if label=='wrong_L':bad['L'][0][0]^=1
            elif label=='wrong_core':bad['core_adjacency'][0][1]^=1
            elif label=='different_support_coverage':bad['other_supports_covered']=True
            elif label=='symmetry_premise':bad['no_target_automorphism_assumed']=False
            elif label=='deleted_domain_option':bad['domains'][0]['choices'].pop()
            else:bad['domains'][0]['choices'][0]['selector']+=1
            reject(label,lambda bad=bad:scope_check(model,bad,raw))
        # Direct one-hot relation and cap truth positives do not assert a research factor.
        positive=0
        for selected in range(3):
            options=[{0,1},{0,2},{1,2}]
            for i,j in product(range(3),repeat=2):need(sum(int(k==selected) for k,s in enumerate(options) if {i,j}<=s)==int({i,j}<=options[selected]),'one-hot linear contribution');positive+=1
        save(out/'controls.json',dict(prefix=controls,onehot_positives=positive,scope_corruptions_rejected=rejected,exploratory_failures=['Old helper filename lacked _v1 and did not exist; corrected path read.','Scout message used conceptual core_adjacency36/L12x60 labels; actual core_adjacency/L keys read after KeyError.'],plan_refinement='All zero-Gram pairs are sound exclusions, including cross-fibre zeros; initial Mi-only plan retained separately.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_FIXED_SUPPORT_COLORING.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_FIXED_SUPPORT_COLORING_CNF_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},counts=counts,verifier='/root/state_literature_audit',method='independent_artifact_check_and_independent_encoding_derivation',shared_components=['Frozen independent GateAudit truth-relation/threshold checker; Python standard library and tqdm.','No producer encoder, helper, decoder or solver imported.'],recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0,limitations=['Only one fixed connected01 core and L, including repeated support columns.','No residual D, full99graph or unrestricted support coverage.','No genuine full research factor positive is currently available.'],elapsed_seconds=time.monotonic()-started)
        save(out/'summary.json',report)
        save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-CONNECTED01-COLORING-CNF',revision=1,statement='The authenticated color-selector CNF is satisfiable exactly when the frozen connected01 core and binary coordinate support L admit a36x60binary factor with the complete prescribed integer Gram and all1770outside-column intersection caps at most2.',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='One fixed core and support; no other Hadamard or support choice is covered.',assumptions=['No nontrivial target automorphism is assumed.'],dependencies=[],dependency_note='Parent should pin existing support/core identities from their independently reviewed exact statement; no unverified theorem needed to enumerate a fixed literal family.',evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],verifier=report['verifier'],method=report['method'],limitations=report['limitations'],created_at=now,updated_at=now))
        print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
