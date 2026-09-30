"""Independent complete fixed-support ordered-coloring CNF audit."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,io,json,platform,subprocess,sys,time
from hashlib import sha256
from tqdm import tqdm
import audit_20260930_eight_full99_cnf_v1 as gates
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_prism_ordered_cnf';RAW=B/'20260930_hadamard20_support/six_prism.json'
RAW_SHA='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
ORDER=B/'20260930_independent_review/hadamard_six_prism_column_order/summary.json'
ORDER_SHA='0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2'
GATES_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save
def read(p):return json.loads(Path(p).read_bytes())

def reconstruct(raw):
    ms=[[a^1 for a in range(12)]for _ in range(3)];need(raw['matchings']==ms,'three standard perfect matchings')
    c=[[int((i//12==j//12 and (i%12)^1==j%12)or(i//12!=j//12 and i%12==j%12))for j in range(36)]for i in range(36)];need(c==raw['core_adjacency'],'literal cubic core')
    nbs=[{j for j,v in enumerate(row)if v}for row in c]
    gram=[[12*int(i==j)-c[i][j]-len(nbs[i]&nbs[j])+2-int(i//12==j//12)for j in range(36)]for i in range(36)];need(gram==raw['prescribed_Gram36'],'literal prescribed integer Gram')
    l=raw['L'];need(len(l)==12 and all(len(row)==60 and all(type(v)is int and v in (0,1)for v in row)and sum(row)==30 for row in l),'binary support and margins')
    supports=[[a for a in range(12)if l[a][d]]for d in range(60)];need(supports==raw['support_columns']and all(len(s)==6 for s in supports),'every raw support column')
    domains=[];all_balanced=0
    for d,coords in enumerate(supports):
        options=[]
        for first in combinations(coords,2):
            remaining=[a for a in coords if a not in first]
            for second in combinations(remaining,2):
                third=[a for a in remaining if a not in second];groups=[first,second,third];rows=sorted(12*g+a for g,pair in enumerate(groups)for a in pair);all_balanced+=1
                if any(gram[i][j]==0 for i,j in combinations(rows,2)):continue
                word=[next(g for g,pair in enumerate(groups)if a in pair)for a in coords];options.append(dict(fibres_by_sorted_coordinate=word,rows=rows,row_mask_hex=format(sum(1<<i for i in rows),'09x')))
        options.sort(key=lambda x:x['fibres_by_sorted_coordinate']);need(len(options)==90 and options==raw['column_colour_options'][d],'all90 options retained by exact Gram-zero filter')
        domains.append(dict(column=d,support_coordinates=coords,choices=[dict(selector=1+90*d+j,option_index=j,**op)for j,op in enumerate(options)]))
    need(all_balanced==5400,'all60x90 balanced options')
    groups=[]
    for d,s in enumerate(supports):
        if not any(s==supports[group[0]]for group in groups):groups.append([e for e,t in enumerate(supports)if t==s])
    need(len(groups)==20 and all(len(g)==3 for g in groups),'all identical-support groups')
    return c,gram,l,supports,domains,groups

def exact_order_clause_segment(cursor,left,right):
    start=cursor.count+1
    for j in range(90):
        cursor.consume([tuple(sorted([-left[j]['selector'],-right[k]['selector']]))for k in range(j+1)])
    need(cursor.count-start+1==4095,'all weak-descending rank pairs forbidden')
    return start,cursor.count-start+1

def scope_check(model,scope,raw):
    c,gram,l,supports,domains,columns=reconstruct(raw);records=[];pairs=[]
    for i,cols in enumerate(columns):
        rows=[x['rows']for x in domains[cols[0]]['choices']]
        records.append(dict(group=i,columns=cols,support=supports[cols[0]],option_count=90,option_row_sets_sha256=sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),allowed_rank_order='Strictly increasing saved lexicographic option index along these ascending column labels.'))
        pairs.extend([[cols[0],cols[1]],[cols[1],cols[2]]])
    need(scope['schema']=='FIXED_HADAMARD_SIX_PRISM_ORDERED_COLORING_SCOPE_V1' and scope['core_name']=='six_prism','fixed scope identity')
    for field,want in [('matchings',raw['matchings']),('core_adjacency',c),('target_gram36',gram),('L',l),('support_columns',supports),('domains',domains),('identical_support_groups',records),('adjacent_order_pairs',pairs),('strictly_increasing_option_rank',True),('cyclic_colour_constraint',False),('canonical_C0_prescribed',False),('target_graph',False),('residual_D',False),('other_supports_covered',False),('no_target_automorphism_assumed',True),('column_sum_per_fibre',2),('row_sum',10),('all_distinct_column_overlap_caps',2),('complete_Gram',True),('cross_matchings','identity')]:need(type(scope[field])is type(want)and scope[field]==want,'scope '+field)
    need(scope['source_raw_support']==key(RAW)and scope['source_raw_support_sha256']==RAW_SHA,'raw support identity')
    need(scope['ordering_gate_path']==key(ORDER)and scope['ordering_gate_sha256']==ORDER_SHA,'independent normalization identity')
    need(scope['domain_filter']=='All90 balanced fibre assignments minus every choice containing any full-Gram-zero rowpair, including crossfibre zeros.','precise complete zero pruning')
    need(model['schema']=='FIXED_HADAMARD_PRISM_ORDERED_COLOR_SELECTOR_PREFIX_CNF_V1'and model['primary_selectors']==5400 and model['domains']==domains,'exact5400 primary selectors')
    need(model['scope_path']==key(D/'scope.json')and model['scope_sha256']==digest(D/'scope.json'),'model scope binding')
    need(model['no_product_variables']is True and model['solver_calls']==0,'no missing product auxiliaries or producer outcome')
    return domains,gram,pairs

def pair_expectation(left,right,start):
    forbidden=[];clauses=[];allowed=0
    for x in left:
        s=frozenset(x['rows']);bits=0
        for j,y in enumerate(right):
            if len(s.intersection(y['rows']))>2:clauses.append(tuple(sorted([-x['selector'],-y['selector']])));bits|=1<<j
            else:allowed+=1
        forbidden.append(format(bits,'x'))
    return dict(forbidden_right_masks_hex=forbidden,tested_choice_pairs=8100,allowed_choice_pairs=allowed,forbidden_choice_pairs=len(clauses),first_clause=start,clause_count=len(clauses)),clauses

def check_cnf(model,scope,raw,path):
    domains,gram,pairs=scope_check(model,scope,raw);rows=model['counter_rows'];rowi=0;sections=[];forbidden=0
    with Path(path).open('rb')as f:
        need(f.readline()==f"p cnf {model['variables']} {model['clauses']}\n".encode(),'literal complete CNF header')
        cursor=gates.ClauseCursor(f,model['variables']);audit=gates.GateAudit(cursor,5400);start=1
        for domain in domains:audit.counter(rows[rowi],[x['selector']for x in domain['choices']],1,True,dict(kind='column_exactly_one',column=domain['column']));rowi+=1
        sections.append(dict(kind='60column_exactone',first_clause=start,last_clause=cursor.count,count=cursor.count-start+1));start=cursor.count+1
        memberships=[(x['selector'],frozenset(x['rows']))for d in domains for x in d['choices']]
        for i in tqdm(range(36),desc='Independent complete Gram threshold rows'):
            for j in range(i,36):
                inputs=[v for v,s in memberships if i in s and j in s];audit.counter(rows[rowi],inputs,gram[i][j],True,dict(kind='full_Gram',rows=[i,j]));rowi+=1
        sections.append(dict(kind='666exactGram_uppertriangle',first_clause=start,last_clause=cursor.count,count=cursor.count-start+1));start=cursor.count+1
        for index,(d,e)in enumerate(tqdm(list(combinations(range(60),2)),desc='Independent all raw column-cap pairs')):
            expected,clauses=pair_expectation(domains[d]['choices'],domains[e]['choices'],cursor.count+1);expected={'columns':[d,e],**expected};need(model['column_cap_pairs'][index]==expected,'complete cap table '+str((d,e)));cursor.consume(clauses);forbidden+=len(clauses)
        sections.append(dict(kind='1770columncap_forbidden_option_pairs',first_clause=start,last_clause=cursor.count,count=cursor.count-start+1));base=cursor.count;start=cursor.count+1
        for index,(d,e)in enumerate(pairs):
            first,count=exact_order_clause_segment(cursor,domains[d]['choices'],domains[e]['choices']);expected=dict(columns=[d,e],left_option_ranks=list(range(90)),right_forbidden_ranks='0..left inclusive',first_clause=first,clause_count=count)
            need(model['strict_order_pairs'][index]==expected,'complete rank-order record')
        sections.append(dict(kind='40strict_adjacent_order_pairs',first_clause=start,last_clause=cursor.count,count=cursor.count-start+1));need(f.read()==b'','no extra or omitted CNF clauses')
    need(rowi==len(rows)==726 and len(model['column_cap_pairs'])==1770 and len(model['strict_order_pairs'])==40,'complete finite populations')
    need(model['base_clause_count']==base and model['ordered_suffix_clause_count']==cursor.count-base==163800,'exact suffix count')
    need(model['clauses']==cursor.count and model['variables']==audit.top and model['clause_sections']==sections,'all auxiliary IDs and clause ranges')
    return dict(variables=audit.top,clauses=cursor.count,primary_selectors=5400,exact_one_rows=60,Gram_equality_rows=666,distinct_column_pairs=1770,tested_choice_pairs=1770*8100,forbidden_choice_pairs=forbidden,identical_support_groups=20,adjacent_order_pairs=40,ordered_suffix_clauses=163800,base_clause_count=base,clause_sections=sections)

def controls(model,scope,raw):
    prefix=gates.controls();rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('accepted corrupted artifact '+label)
    for label in ['cyclic_restriction','changed_L','changed_core','deleted_option','wrong_selector','order_pair','weak_order','target_symmetry']:
        bad=deepcopy(scope)
        if label=='cyclic_restriction':bad['cyclic_colour_constraint']=True
        elif label=='changed_L':bad['L'][0][0]^=1
        elif label=='changed_core':bad['core_adjacency'][0][1]^=1
        elif label=='deleted_option':bad['domains'][0]['choices'].pop()
        elif label=='wrong_selector':bad['domains'][0]['choices'][0]['selector']+=1
        elif label=='order_pair':bad['adjacent_order_pairs'][0].reverse()
        elif label=='weak_order':bad['strictly_increasing_option_rank']=False
        else:bad['no_target_automorphism_assumed']=False
        reject(label,lambda bad=bad:scope_check(model,bad,raw))
    left=scope['domains'][0]['choices'];right=scope['domains'][20]['choices'];segment=b''.join(f"{-left[j]['selector']} {-right[k]['selector']} 0\n".encode()for j in range(90)for k in range(j+1))
    cursor=gates.ClauseCursor(io.BytesIO(segment),model['variables']);exact_order_clause_segment(cursor,left,right);need(cursor.count==4095,'positive complete strict-order segment')
    reject('order_missing_equal_rank',lambda:exact_order_clause_segment(gates.ClauseCursor(io.BytesIO(segment.split(b'\n',1)[1]),model['variables']),left,right))
    reject('order_wrong_sign',lambda:exact_order_clause_segment(gates.ClauseCursor(io.BytesIO(segment.replace(b'-1 ',b'1 ',1)),model['variables']),left,right))
    truth=0
    forbidden={(j,k)for j in range(90)for k in range(j+1)}
    for j,k in product(range(90),repeat=2):need(((j,k)not in forbidden)==(j<k),'complete strict-order truth');truth+=1
    expected,clauses=pair_expectation(left,right,1);need(expected['allowed_choice_pairs']+len(clauses)==8100,'positive complete cap relation')
    bad={**expected,'forbidden_choice_pairs':-1};reject('wrong_cap_count',lambda:need(bad==pair_expectation(left,right,1)[0],'cap metadata'))
    return dict(prefix_truth_controls=prefix,strict_order_truth_cases=truth,strict_order_positive_clauses=4095,corruptions_rejected=rejected,research_factor_positive=None,research_factor_positive_null_reason='No complete research factor is known; local truth controls are not research SAT.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};start=time.monotonic()
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact identity '+key(p));bindings[key(p)]=value
    try:
        pin(D/'summary.json',args.summary_sha256);producer=read(D/'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(ORDER,ORDER_SHA);order=read(ORDER);need(order['status']=='INDEPENDENT_HADAMARD_SIX_PRISM_IDENTICAL_SUPPORT_ORDER_PASS','exact normalization gate')
        for p,h in {**order['inputs_sha256'],**order['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(Path(gates.__file__),GATES_SHA);pin(RAW,RAW_SHA);raw=read(RAW);model=read(D/'model.json');scope=read(D/'scope.json')
        save(out/'controls.json',controls(model,scope,raw));counts=check_cnf(model,scope,raw,D/'instance.cnf')
        for field in ['variables','clauses','primary_selectors','exact_one_rows','Gram_equality_rows','distinct_column_pairs','tested_choice_pairs','forbidden_choice_pairs','identical_support_groups','adjacent_order_pairs','ordered_suffix_clauses','clause_sections']:need(producer[field]==counts[field],'producer count '+field)
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PRISM_ORDERED_CNF.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();limitations=['One exact six-prism Hadamard support only, modulo independently verified identical-support column sorting.','No cyclic relation or target automorphism is assumed.','Other supports, residual D and target resolution are outside scope.'];report=dict(status='INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_CNF_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},counts=counts,verifier='/root/state_literature_audit',method='independent_domain_and_complete_truth_relation_CNF_reconstruction',shared_components=['Frozen independent prime-implicate/threshold checker; Python standard library and tqdm.','No producer domain, encoder, decoder or solver imports.'],recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0,limitations=limitations,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',report);save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SIX-PRISM-ORDERED-COLORING-CNF',revision=1,statement=f"The authenticated{counts['variables']}-variable{counts['clauses']}-clause CNF is satisfiable exactly when the frozen six-prism coordinate support L admits a binary36x60 prescribed-Gram factor with all1770 column-pair caps, modulo sorting the three columns in each identical-support group by their distinct option ranks.",kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope=limitations[0],assumptions=['No nontrivial target automorphism is assumed.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-IDENTICAL-SUPPORT-ORDER-NORMALIZATION',revision=1,relation='normalization'),dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='verification_dependency')],evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],verifier=report['verifier'],method=report['method'],limitations=limitations,created_at=now,updated_at=now));print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
