"""Independent next exact-eight literal lift checker; no producer imports."""
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product,permutations
from pathlib import Path
import argparse,ast,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import audit_20260930_eight_count_profile_lift_third as base
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_exact_eight_next_lift'
prior=base.prior;shared=base.shared;codec=base.codec
need=codec.need;sha=codec.sha;key=codec.key;read=codec.read;save=codec.save;same=codec.same
RAW=base.RAW;LOCAL=base.LOCAL;FIXTURE=base.FIXTURE
PROFILE=D/'selected_profile.json';PLAN=ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_NEXT_LIFT.md'
SELECTION_PLAN=ROOT/'acceleration/theory_20260930_exact_eight_next_lift_plan.md'
ENCODING=B/'20260930_independent_review/exact_eight_next_lift/summary.json'
STATUSES=dict(audit='INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_ENCODING_PASS',calibrate='INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_OBJECT_CALIBRATION_PASS',sat='INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_SAT_OBJECT_PASS')
EXPECTED_CANDIDATE_SUMMARY='6cad750feb66e73dbeec98d818ca1a15b049105167c4cacce70e3a1071bd17dc'
EXPECTED_BLOCK_GATE='6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a'
PINS={RAW:base.PINS[RAW],LOCAL:base.PINS[LOCAL],FIXTURE:base.PINS[FIXTURE],
 Path(base.__file__):'076a6ae8a731bede8075334b8c40e9df480aaed52cc8214aa68bb70ccbda78a1',
 Path(prior.__file__):base.PINS[Path(prior.__file__)],Path(shared.__file__):base.PINS[Path(shared.__file__)],Path(codec.__file__):base.PINS[Path(codec.__file__)],
 ROOT/'acceleration/theory_20260930_exact_eight_next_lift.py':'473b4774650f43fbd51dc9387f006bf1b9626e70acfd80e4a3ab45c25ac04dff',
 ROOT/'acceleration/theory_20260930_exact_eight_next_lift_spec.md':'ef0f6cbc9688db47eea55ddcb97de0fca063b6eb3361827c28426926ccfe53fd',
 SELECTION_PLAN:'2bcfceed96539c62e8b7e877b4c248962bdef028d2751ff8f5d04c5c4245db3e'}
WITNESSES=[('first','count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('second','count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('third','count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
GATE=None
static_closure=base.static_closure

def counts_vector(counts):
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'strict full count table')
    return bytes(x for row in counts for v in row for x in v)
def images(v):return {bytes(v[k+p[f]]for k in range(0,720,3)for f in range(3))for p in permutations(range(3))}

def selection_check(candidate,pin):
    global GATE
    s=read(D/'selection.json');GATE=ROOT/s['block_gate_path']
    need(EXPECTED_BLOCK_GATE and s['block_gate_sha256']==EXPECTED_BLOCK_GATE,'frozen block gate contract');pin(GATE,EXPECTED_BLOCK_GATE);gate=read(GATE)
    need(gate['status']=='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS','complete independent block gate')
    sp=ROOT/s['block_summary_path'];pin(sp,s['block_summary_sha256']);need(gate['inputs_sha256'].get(key(sp))==s['block_summary_sha256'],'authenticated complete block summary');bs=read(sp)
    need(bs['complete'] and bs['representatives_checked']==792 and bs['complete_profile_pair_tests']==47520,'all792-by60 tests')
    for name,h in bs['outputs_sha256'].items():pin(ROOT/name,h);need(gate['inputs_sha256'].get(name)==h,'all block outputs authenticated')
    path=sp.parent/'surviving_representatives.json.gz';need(key(path)==s['survivor_path'] and sha(path)==s['survivor_sha256'],'exact survivor input')
    with gzip.open(path,'rt',encoding='utf8')as f:sur=json.load(f)
    need(sur['complete'],'complete survivor list');ordered=sorted(sur['records'],key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']))
    historical=set();old=[]
    for label,folder,h in WITNESSES:
        wp=B/f'20260930_independent_review/{folder}/independent_count_profile.json';pin(wp,h);ims=images(counts_vector(read(wp)['coordinate_group_fibre_counts']));historical.update(ims)
        old.append(dict(label=label,path=key(wp),sha256=h,canonical_full_count_sha256=hashlib.sha256(min(ims)).hexdigest(),distinct_images=len(ims)))
    eligible=[];seen=set()
    for r in ordered:
        v=counts_vector(r['counts']);dg=hashlib.sha256(v).hexdigest();need(dg==r['canonical_fibre_profile_sha256'] and v==min(images(v)) and dg not in seen,'unique literal canonical survivor');seen.add(dg)
        if v not in historical:eligible.append(r)
    need(eligible,'formula requires nonempty predeclared selection')
    expected=dict(rule='First (subset_index, canonical_fibre_profile_sha256) outside all three historical full count-table fibre orbits.',plan_sha256=PINS[SELECTION_PLAN],block_gate_path=key(GATE),block_gate_sha256=EXPECTED_BLOCK_GATE,block_summary_path=key(sp),block_summary_sha256=sha(sp),survivor_path=key(path),survivor_sha256=sha(path),historical_profiles=old,ordered_survivors=[dict(subset_index=r['subset_index'],canonical_fibre_profile_sha256=r['canonical_fibre_profile_sha256'])for r in ordered],eligible=[dict(subset_index=r['subset_index'],canonical_fibre_profile_sha256=r['canonical_fibre_profile_sha256'])for r in eligible],selected=eligible[0])
    need(same(s,expected),'entire deterministic selection metadata');selected=eligible[0];profile=read(PROFILE)
    need(profile['coordinate_group_fibre_counts']==selected['counts'] and profile['full_count_profile_sha256']==selected['canonical_fibre_profile_sha256'] and profile['selected_subset_index']==selected['subset_index'],'selected exact literal profile')
    need(profile['source_selection_path']==key(D/'selection.json') and profile['source_selection_sha256']==sha(D/'selection.json'),'profile binds selection')
    need(candidate['selected_full_count_sha256']==selected['canonical_fibre_profile_sha256'] and candidate['selected_subset_index']==selected['subset_index'],'summary selection identity')
    PINS[PROFILE]=sha(PROFILE);PINS[GATE]=EXPECTED_BLOCK_GATE
    return selected,expected

def derive(raw,p):
    words,triples,balanced=prior.catalogue();index=defaultdict(list)
    for i,t in enumerate(triples):index[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
    L=raw['L'];C=raw['core_adjacency'];K=shared.gram_from_core(C,12)
    need(C==[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and i%12^1==j%12))for j in range(36)]for i in range(36)]and K==raw['prescribed_Gram36'],'literal core/Gram')
    supports=[[a for a in range(12)if L[a][d]]for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    columns=[[d for d,s in enumerate(supports)if s==g]for g in groups];pairs=[list(x)for x in combinations(range(12),2)if x[0]^1!=x[1]]
    need(len(groups)==20 and all(len(s)==6 and len(ds)==3 and all(sum(a in s for a in(m,m+1))==1 for m in range(0,12,2))for s,ds in zip(groups,columns)),'literal support triples')
    counts=p['coordinate_group_fibre_counts'];exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)]
    need(exceptional==p['exceptional_groups']and len(exceptional)==p['exception_count']==8,'exact arbitrary count-table exception list')
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'integer count-table shape')
    need(all(counts[a][g]==[0,0,0]for g,s in enumerate(groups)for a in range(12)if a not in s),'off-support counts vanish')
    deviations=[[[counts[a][g][f]-int(a in groups[g])for g in exceptional]for f in range(3)]for a in range(12)]
    need(deviations==p['coordinate_fibre_deviations'],'raw deviations from literal counts')
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(digest==p['profile_sha256'] and hashlib.sha256(counts_vector(counts)).hexdigest()==p['full_count_profile_sha256'],'literal profile digest')
    domains=[];ranks=[];nextid=1
    for g,s in enumerate(groups):
        wanted=[counts[a][g]for a in s];signature=tuple(sum(wanted,[]));ids=index.get(signature,[])
        need(ids and ids==p['local_survivor_indices_by_group'][g],'complete raw count class')
        if g in exceptional:
            need(len(ids)>0,'complete nonempty exceptional class');options=[dict(choice_index=j,local_survivor_index=i,word_indices=triples[i],colour_words=[words[w]for w in triples[i]])for j,i in enumerate(ids)];kind='exceptional_sorted_local_triple'
        else:
            need(signature==(1,)*18 and len(ids)==150,'all150 balanced choices');options=deepcopy(balanced);kind='balanced_normalized_triple'
        for option in options:
            option['selector']=nextid;nextid+=1;option['lifted_rows']=[[12*f+a for a,f in zip(s,w)]for w in option['colour_words']]
            need([[sum(w[a]==f for w in option['colour_words'])for f in range(3)]for a in range(6)]==wanted,'literal option counts')
            need(all(len(set(u)&set(v))<=2 for u,v in combinations(option['lifted_rows'],2)),'literal within-triplicate cap')
            need(all(K[a][b]>0 for rows in option['lifted_rows']for a,b in combinations(rows,2)),'every prescribed zero entry absent')
        domains.append(dict(group=g,support=s,columns=columns[g],kind=kind,fixed_counts=wanted,choices=options));ranks.append(dict(group=g,count_signature=list(signature),local_survivor_indices=ids,count=len(ids)))
    margins=[dict(coordinate=a,fibre=f,total=sum(counts[a][g][f]for g in range(20)))for a in range(12)for f in range(3)]
    S=nextid-1;need(all(x['total']==10 for x in margins),'all36 exact margins')
    need(all(K[12*f+a][12*z+b]==0 for a in range(12)for b in range(12)for f,z in product(range(3),repeat=2)if (a==b and f!=z)or a^1==b),'all90 omitted offdiagonal Gram entries zero')
    scope=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_SCOPE_V1',source_count_profile_path=key(PROFILE),source_count_profile_sha256=PINS[PROFILE],source_count_gate_path=key(GATE),source_count_gate_sha256=PINS[GATE],selected_profile_id='exact_eight_first_block_survivor_outside_three_historical_orbits',selected_profile_sha256=digest,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=exceptional,coordinate_fibre_deviations=deviations,coordinate_group_fibre_counts=counts,balanced_groups=[g for g in range(20)if g not in exceptional],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in this one literal count profile and full initial local domains, with within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.',derived_row_margins=margins,selected_profile_artifact_sha256=PINS[PROFILE],initial_domains_path=key(D/'initial_domains.json'),initial_domains_sha256=sha(D/'initial_domains.json'))
    scope.update(source_count_gate_role='Independent complete block population gate; the new selected profile is deterministically derived, not a separately approved artifact.',selection_path=key(D/'selection.json'),selection_sha256=sha(D/'selection.json'),selected_full_count_sha256=p['full_count_profile_sha256'])
    clauses=[];prefixes=[];cells=[];nextvar=nextid
    def append(cs):
        meta=dict(first_clause=len(clauses)+1,clause_count=len(cs));clauses.extend(cs);return meta
    for dom in domains:
        xs=[o['selector']for o in dom['choices']];ps=list(range(nextvar,nextvar+len(xs)-1));nextvar+=len(ps);prefixes.append(dict(group=dom['group'],selectors=xs,prefixes=ps,**append(shared.onehot_clauses(xs,ps))))
    for a,b in pairs:
        incident=[dom for dom in domains if a in dom['support']and b in dom['support']];need(len(incident)==5,'five literal incident supports')
        for f,z in product(range(3),repeat=2):
            contributions=[]
            for dom in incident:
                coeff=[sum(12*f+a in rows and 12*z+b in rows for rows in o['lifted_rows'])for o in dom['choices']];need(set(coeff)<={0,1,2},'integer coefficient range');channels=[]
                for threshold in(1,2):
                    xs=[o['selector']for o,n in zip(dom['choices'],coeff)if n>=threshold];v=nextvar;nextvar+=1;channels.append(dict(threshold=threshold,variable=v,selectors=xs,**append(shared.or_clauses(v,xs))))
                contributions.append(dict(group=dom['group'],coefficients=coeff,channels=channels))
            xs=[c['variable']for g in contributions for c in g['channels']];bound=K[12*f+a][12*z+b];need(bound==(1 if f==z else 2),'actual Gram target')
            cells.append(dict(coordinates=[a,b],fibres=[f,z],bound=bound,group_contributions=contributions,count_inputs=xs,**append(shared.count_clauses(xs,bound))))
    onehot=sum(r['clause_count']for r in prefixes);card=sum(r['clause_count']for r in cells)
    need(nextvar==2*S+5381 and len(clauses)==49*S+60400,'domain-derived complete formula dimensions')
    model=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_WEIGHTED_CNF_V1',variables=nextvar-1,clauses=len(clauses),primary_selectors=S,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=S,onehot_prefixes=S-20,weighted_threshold_channels=5400),clause_populations=dict(onehot=onehot,channels=len(clauses)-onehot-card,counts=card),scope_sha256=PINS[D/'scope.json'])
    return scope,model,clauses,dict(records=ranks,all_initial=True,AC_pruning_used=False)

def object_check(values,model,scope,clauses,decoded=None):
    codec.all_clauses(clauses,values);F=[[0]*60 for _ in range(36)];selected=[];profiles=[]
    for dom in model['domains']:
        active=[o for o in dom['choices']if values[o['selector']]];need(len(active)==1,'one selected local option');o=active[0];selected.append(o['selector'])
        for d,rows in zip(dom['columns'],o['lifted_rows']):
            for row in rows:F[row][d]=1
        counts=[[sum(F[12*f+a][d]for d in dom['columns'])for f in range(3)]for a in dom['support']];need(counts==dom['fixed_counts'],'raw selected literal count class')
        need(all(sum(F[r][d]*F[r][e]for r in range(36))<=2 for d,e in combinations(dom['columns'],2)),'within-triplicate raw caps');profiles.append(dict(group=dom['group'],counts=counts))
    checks=shared.raw_factor(F,scope['core_adjacency36'],12,scope['L12x60']);order,canon=shared.canonical(F,12)
    obj=dict(factor=F,L=scope['L12x60'],selected_selector_ids=selected,actual_group_profiles=profiles,canonical_column_order=order,canonical_factor=canon,core_adjacency=scope['core_adjacency36'],target_gram=scope['prescribed_Gram36'],checks=checks,Gram_factor=True,factor_also_passes_column_caps=not checks['column_cap_violations'],factor_also_passes_mixed_caps=not checks['mixed_cap_violations'],target_graph=False,residual_D=None,profile_is_additional_assumption=True,model_sha256=PINS[D/'model.json'],scope_sha256=PINS[D/'scope.json'],independent_approval=False,selected_profile_id=scope['selected_profile_id'],selected_profile_sha256=scope['selected_profile_sha256'])
    if decoded is not None:need(same(obj,decoded),'complete independent decoder agreement')
    return obj

def controls(scope,model,clauses,out):
    rejected=[];truthcases=Counter();V=model['variables'];M=model['clauses']
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError,AssertionError):rejected.append(name);return
        raise ValueError('accepted corrupted control '+name)
    def truth(cs,vs):return all(any(vs[abs(v)]==(v>0)for v in row)for row in cs)
    for n in range(2,7):
        cs=shared.onehot_clauses(list(range(1,n+1)),list(range(n+1,2*n)))
        for bits in product((False,True),repeat=2*n-1):need(truth(cs,dict(enumerate(bits,1)))==(sum(bits[:n])==1 and all(bits[n+i]==any(bits[:i+1])for i in range(n-1))),'exact prefix truth');truthcases['prefix']+=1
    for n in range(6):
        cs=shared.or_clauses(n+1,list(range(1,n+1)))
        for bits in product((False,True),repeat=n+1):need(truth(cs,dict(enumerate(bits,1)))==(bits[-1]==any(bits[:-1])),'OR/empty truth');truthcases['OR']+=1
    for k in(1,2):
        cs=shared.count_clauses(list(range(1,11)),k)
        for bits in product((False,True),repeat=10):need(truth(cs,dict(enumerate(bits,1)))==(sum(bits)==k),'ten-flag count truth');truthcases['cardinality']+=1
    for n in (0,1,2):need(int(n>=1)+int(n>=2)==n,'weighted threshold identity')
    fixture=read(FIXTURE);F=fixture['factor60x180'];C=fixture['cubic_core60'];checks=shared.raw_factor(F,C,20);need(not checks['column_cap_violations']and not checks['mixed_cap_violations'],'genuine243 positive');shared.raw_factor([r[::-1]for r in F],C,20);shared.canonical(F,20)
    for name in('bit','bool','length','nonbinary'):
        bad=deepcopy(F)
        if name=='bit':bad[0][0]^=1
        elif name=='bool':bad[0][0]=bool(bad[0][0])
        elif name=='length':bad[0].pop()
        else:bad[0][0]=2
        reject('raw_'+name,lambda bad=bad:shared.raw_factor(bad,C,20))
    for name in('coefficient','second_channel','bound','prefix','missing_choice','lifted_row'):
        bad=deepcopy(model)
        if name=='coefficient':bad['pair_cell_counts'][0]['group_contributions'][0]['coefficients'][0]+=1
        elif name=='second_channel':bad['pair_cell_counts'][0]['group_contributions'][0]['channels'][1]['selectors'].append(1)
        elif name=='bound':bad['pair_cell_counts'][0]['bound']=2
        elif name=='prefix':bad['exact_one_prefix_rows'][0]['prefixes'][0]+=1
        elif name=='missing_choice':bad['domains'][1]['choices'].pop()
        else:bad['domains'][0]['choices'][0]['lifted_rows'][0][0]+=1
        reject(name,lambda bad=bad:need(same(bad,model),'whole reconstructed metadata'))
    for name in('cross_group_column_caps_encoded','arc_pruning_used','orbit_coverage_used'):
        bad=deepcopy(scope);bad[name]=True;reject(name,lambda bad=bad:need(same(bad,scope),'scope assumptions'))
    reject('dropped_actual_clause',lambda:need(codec.cnf_bytes(clauses[:-1],V)==(D/'instance.cnf').read_bytes(),'complete raw bytes'))
    bad=deepcopy(clauses);bad[model['clause_populations']['onehot']][0]*=-1;reject('signed_actual_clause',lambda:need(codec.cnf_bytes(bad,V)==(D/'instance.cnf').read_bytes(),'signed raw bytes'))
    local=[]
    for last in(False,True):
        selected={dom['choices'][-1 if last else 0]['selector']for dom in model['domains']};vals={i:i in selected for i in range(1,(V+1))};F=[[0]*60 for _ in range(36)]
        for dom in model['domains']:
            o=dom['choices'][-1 if last else 0]
            for d,rows in zip(dom['columns'],o['lifted_rows']):
                for r in rows:F[r][d]=1
            need([[sum(F[12*f+a][d]for d in dom['columns'])for f in range(3)]for a in dom['support']]==dom['fixed_counts'],'local-only decoded count positive')
        for row in model['exact_one_prefix_rows']:
            for i,v in enumerate(row['prefixes']):vals[v]=any(vals[x]for x in row['selectors'][:i+1])
        for cell in model['pair_cell_counts']:
            for g in cell['group_contributions']:
                for channel in g['channels']:vals[channel['variable']]=any(vals[x]for x in channel['selectors'])
        need(all(sum(row)==10 for row in F),'positive local margin control');reject('local_only_not_full_Gram_'+str(last),lambda:object_check(vals,model,scope,clauses));local.append(dict(selected=sorted(selected),factor=F,scope='Local counts/support/margins only, no fullGram claim'))
    save(out/'local_decode_controls.json',local)
    n=V;m=M;lits=[i if i%2 else -i for i in range(1,n+1)];vals=codec.assignment(lits,n);text='c SYNTHETIC CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,lits[i:i+113]))for i in range(0,n,113))+' 0\n';need(codec.native(text,n)==vals,'full signed native codec');synthetic=[[lits[i%n]]for i in range(m)];codec.all_clauses(synthetic,vals)
    for name,bad in [('status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('duplicate_status',text+'s SATISFIABLE\n'),('terminal',text.replace(' 0\n','\n')),('duplicate',text.replace('v 1 -2','v 1 1')),('post_zero',text+'v 1\n'),('range',text.replace('v 1 -2','v '+str(V+1)+' -2'))]:reject('native_'+name,lambda bad=bad:codec.native(bad,n))
    reject('missing_JSON',lambda:codec.assignment(lits[:-1],n));reject('Boolean_JSON',lambda:codec.assignment([True,*lits[1:]],n));reject('native_JSON_disagreement',lambda:need(codec.assignment([-lits[0],*lits[1:]],n)==vals,'native/JSON equality'));synthetic[-1][0]*=-1;reject('false_clause',lambda:codec.all_clauses(synthetic,vals));synthetic[-1][0]*=-1
    (out/'synthetic_native.stdout.log').write_text(text,encoding='ascii',newline='\n');save(out/'synthetic_assignment.json',dict(assignment=lits,research_SAT=False));(out/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,n))
    return dict(truth_cases=dict(truthcases),rejected_corruptions=rejected,generic_positive='Genuine independently authenticated SRG243 factor and reversed columns.',local_positive='First/last option for every domain: counts/support/margins only.',synthetic_positive=f'Full{V}-ID/{M}-clause codec only, no research factor.',research_factor_positive=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=list(STATUSES));ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--native-driver',type=Path);ap.add_argument('--native-driver-sha256');ap.add_argument('--native-spec',type=Path);ap.add_argument('--native-spec-sha256');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    need(EXPECTED_CANDIDATE_SUMMARY and EXPECTED_BLOCK_GATE,'candidate and block pins must be frozen before execution')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or h==v,'hash '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        pin(D/'summary.json',EXPECTED_CANDIDATE_SUMMARY);candidate=read(D/'summary.json')
        need(candidate['status']=='CANDIDATE_EXACT_EIGHT_NEXT_LITERAL_FULL_GRAM_LIFT_BUILT','exact candidate schema')
        for name,h in {**candidate['inputs_sha256'],**candidate['outputs_sha256']}.items():pin(ROOT/name,h)
        for name in ['instance.cnf','model.json','scope.json','initial_domains.json','selected_profile.json','selection.json']:PINS[D/name]=sha(D/name)
        pin(Path(__file__));pin(PLAN);checker_closure=static_closure(Path(__file__))
        for p in checker_closure:pin(p)
        need(all(not p.name.startswith(('theory_','native_'))for p in checker_closure),'no producer/native imports')
        chosen,selection=selection_check(candidate,pin);profile=read(PROFILE)
        scope,model,clauses,initial=derive(read(RAW),profile)
        expected_profile=dict(coordinate_group_fibre_counts=chosen['counts'],coordinate_fibre_deviations=scope['coordinate_fibre_deviations'],exceptional_groups=scope['exceptional_groups'],exception_count=8,local_survivor_indices_by_group=[r['local_survivor_indices']for r in initial['records']],profile_sha256=scope['selected_profile_sha256'],full_count_profile_sha256=chosen['canonical_fibre_profile_sha256'],selected_subset_index=chosen['subset_index'],source_selection_path=key(D/'selection.json'),source_selection_sha256=sha(D/'selection.json'))
        need(same(profile,expected_profile),'complete reconstructed selected profile');need(same(scope,read(D/'scope.json'))and same(model,read(D/'model.json'))and same(initial,read(D/'initial_domains.json')),'all reconstructed metadata fields')
        V=model['variables'];M=model['clauses'];S=model['primary_selectors'];sizes=[len(d['choices'])for d in model['domains']]
        need([candidate[k]for k in ['variables','clauses','selectors','initial_domain_sizes']]==[V,M,S,sizes],'all candidate dimensions')
        need(codec.cnf_bytes(clauses,V)==(D/'instance.cnf').read_bytes(),'complete actual clause bytes');need(gzip.decompress((D/'model.json.gz').read_bytes())==(D/'model.json').read_bytes(),'complete public model recovery bytes')
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate.resolve()==ENCODING.resolve()and args.encoding_gate_sha256,'explicit exact encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);eg=read(args.encoding_gate);need(eg['status']==STATUSES['audit'],'same encoding approved')
            for name,h in eg['inputs_sha256'].items():pin(ROOT/name,h)
        native_closure=[]
        if args.mode=='calibrate':
            need(args.native_driver and args.native_driver_sha256 and args.native_spec and args.native_spec_sha256,'explicit frozen native driver/spec');pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            ns=static_closure(args.native_driver)|{args.native_spec.resolve(),ROOT/'acceleration/theory_20260930_exact_eight_next_lift_spec.md',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'}
            for p in ns:pin(p)
            native_closure=sorted(map(key,ns))
        if args.mode in('audit','calibrate'):
            control=controls(scope,model,clauses,out);bad=deepcopy(selection);bad['selected']=None
            need(not same(bad,selection),'missing selection rejected');bad=deepcopy(profile);bad['local_survivor_indices_by_group'][0].pop();need(not same(bad,expected_profile),'incomplete selected class rejected')
            control['selection_controls']=['missing_selected_record','missing_initial_rank'];save(out/'controls.json',control)
        else:
            control=None;need(args.assignment and args.native_output,'complete raw SAT inputs');pin(args.assignment);pin(args.native_output);vals=codec.assignment(read(args.assignment)['assignment'],V);need(vals==codec.native(args.native_output.read_text(encoding='utf8'),V),'all native and JSON literals');decoded=None
            if args.decoded:pin(args.decoded);decoded=read(args.decoded)
            save(out/'independent_Gram_factor.json',object_check(vals,model,scope,clauses,decoded))
        stamp=datetime.now(timezone.utc).isoformat();need(time.perf_counter()-start<120,'120-second audit allocation')
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-NEXT-EXACT-EIGHT-LITERAL-GRAM-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=f'The complete {V}-variable, {M}-clause CNF is satisfiable iff the fixed six-prism Hadamard support admits a binary 36 by 60 factor with full prescribed integer Gram, literal full-count digest {profile["full_count_profile_sha256"]} and within-triplicate column caps, modulo independent equal-support column permutations. All {S} primary options are the complete initial count classes; auxiliary assignments are unique.',scope='One literal eight-exception profile selected by the frozen complete-block-survivor rule. Cross-group caps and residual D omitted; no other-profile exclusion or target automorphism.',assumptions=['Pinned complete local catalogue, fixed support and authenticated block-survivor population.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,relation='uses_result')],selection_gate_artifact=dict(path=key(GATE),sha256=EXPECTED_BLOCK_GATE),verifier='/root/structural_attack',producer='/root/eight_domain_audit',method='Independent catalogue/domain/selection/Gram/weighted-channel/complete-clause reconstruction and generic positive/corruption controls.',shared_components=['Frozen independent third-lift checking path and its independent seven/balanced/codec helpers, with fresh dynamic-domain reconstruction.','No producer or native imports.'],inputs_sha256=pins,limitations=['No native call, factor witness or exclusion asserted by encoding approval.','Cross-group caps and residual graph remain unencoded.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Independent internal review only.',created_at=stamp,updated_at=stamp))
        save(out/'summary.json',dict(status=STATUSES[args.mode],timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},variables=V,clauses=M,selectors=S,Gram_cells=540,literal_triples_enumerated=117480,local_survivors=31110,exceptional_groups=scope['exceptional_groups'],initial_domain_sizes=sizes,balanced_groups=12,balanced_choices=150,selected_full_count_sha256=profile['full_count_profile_sha256'],selected_compact_deviation_sha256=profile['profile_sha256'],controls=control,native_source_closure=native_closure,checker_source_closure=sorted(map(key,checker_closure)),elapsed_seconds=time.perf_counter()-start,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,residual_D_encoded=False,scope=scope['scope']))
        print(json.dumps(dict(status=STATUSES[args.mode],summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except Exception as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
