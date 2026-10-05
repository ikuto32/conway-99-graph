"""Independent fifteen-profile audit; adapted frozen independent case0 checker, no producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
import audit_20260930_hadamard_balanced_gram_v2 as shared

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_case0_profile_cnf'
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';CASE=B/'20260930_hadamard_four_group_local_screen/case_000.json'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
codec=shared.codec;need=codec.need;sha=codec.sha;key=codec.key;read=codec.read;save=codec.save;same=codec.same
BATCH=B/'20260930_hadamard_four_profile_cnfs/summary.json'
SELECTION=B/'20260930_independent_review/hadamard_remaining_profile_universe/summary.json'
SELECTION_SHA='dffd4d638ee0cfca637a6ae4ba1a5cff5d7cb40d50f0dad2a9dd8f3ac79853ec'
CASES=[6,12,18,24,30,36,42,48,51,72,78,84,90,96,102]
CURRENT_CASE=None
PINS={BATCH:'692f74a5bf3be681832978d2a0ec51ec373237d45f3df24ccf1c01cfb009584b',SELECTION:SELECTION_SHA,
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 Path(shared.__file__):'cfddc6521887d6d44904ee7f2b92b0f189cfe5675b4f8d12d6df96ffe830e35c',Path(codec.__file__):'f572c91dc43f7208d34976b165c621c1b314e6963e437eaa475520ae1eb0add3',
 ROOT/'acceleration/audit_20260930_hadamard_case0_profile.py':'53e37572532b5a13970098528b4be1b3ab9ef5b07f06c86e29d06955457654e1',
 ROOT/'acceleration/theory_20260930_hadamard_four_profile_cnf.py':'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',ROOT/'acceleration/theory_20260930_hadamard_four_profile_cnf_spec.md':'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',
 ROOT/'acceleration/native_20260930_hadamard_four_profile_batch.py':'ae88f70564cffad5988dcc224016de011bd378b508d233fb05c9bca76b6b5fed',ROOT/'acceleration/native_20260930_hadamard_four_profile_batch_spec.md':'07ed9014a9e31cdd2d1c2866e5dc9a68345b7daa69aefe1eb200f0f9a6af59ab',
 ROOT/'acceleration/native_20260930_unrestricted_full99.py':'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',ROOT/'acceleration/native_20260930_proof_location.py':'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854'}

def catalogue():
    words=[list(w)for w in product(range(3),repeat=6)if all(w.count(f)==2 for f in range(3))];survivors=[];balanced=[]
    for tri in combinations(range(90),3):
        ws=[words[i]for i in tri]
        if any(sum(x==y for x,y in zip(u,v))>2 for u,v in combinations(ws,2)):continue
        if any(any(n>(1 if f==g else 2)for(f,g),n in Counter((w[a],w[b])for w in ws).items())for a,b in combinations(range(6),2)):continue
        survivors.append(list(tri))
        if all(len({w[a]for w in ws})==3 for a in range(6)):
            balanced.append(dict(colour_words=ws,coordinate_permutations=[[w[a]for w in ws]for a in range(6)]))
    balanced.sort(key=lambda x:x['coordinate_permutations'])
    for i,x in enumerate(balanced):x['choice_index']=i
    local=read(LOCAL);need(words==local['words'] and survivors==local['survivors'] and len(survivors)==31110 and len(balanced)==150,'complete117480 literal triple enumeration')
    return words,survivors,balanced

def derive(raw,case,catalog):
    words,triples,balanced=catalog;L=raw['L'];C=raw['core_adjacency'];K=shared.gram_from_core(C,12)
    need(C==[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and i%12^1==j%12))for j in range(36)]for i in range(36)] and K==raw['prescribed_Gram36'],'literal core and prescribed Gram')
    supports=[[a for a in range(12)if L[a][d]]for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    columns=[[d for d,s in enumerate(supports)if s==g]for g in groups];pairs=[list(p)for p in combinations(range(12),2)if p[0]^1!=p[1]]
    need(len(groups)==20 and all(len(s)==6 and len(ds)==3 and all(sum(a in s for a in(m,m+1))==1 for m in range(0,12,2))for s,ds in zip(groups,columns)),'all support groups')
    need(case['case']==CURRENT_CASE and CURRENT_CASE in CASES and len(case['groups'])==4,'literal authenticated selected case')
    domains=[];nextid=1
    for g,s in enumerate(groups):
        wanted=[[1]*3 for a in s]
        if g in case['groups']:
            side=case['groups'].index(g);sign=case['relation'][side]
            for a,delta in zip(case['common_support'],case['profile']):wanted[s.index(a)]=[1+sign*x for x in delta]
            found=[i for i,tri in enumerate(triples)if [[sum(words[w][p]==f for w in tri)for f in range(3)]for p in range(6)]==wanted]
            need(found==case['local_survivor_indices'][side] and len(found)==48,'all initial exceptional options, no AC subset')
            options=[dict(choice_index=j,local_survivor_index=i,word_indices=triples[i],colour_words=[words[w]for w in triples[i]])for j,i in enumerate(found)];kind='exceptional_sorted_local_triple'
        else:options=deepcopy(balanced);kind='balanced_normalized_triple'
        for option in options:
            option['selector']=nextid;nextid+=1;option['lifted_rows']=[[12*f+a for a,f in zip(s,w)]for w in option['colour_words']]
            need([[sum(w[p]==f for w in option['colour_words'])for f in range(3)]for p in range(6)]==wanted,'all local count profiles')
            need(all(len(set(u)&set(v))<=2 for u,v in combinations(option['lifted_rows'],2)),'local column caps')
        domains.append(dict(group=g,support=s,columns=columns[g],kind=kind,fixed_counts=wanted,choices=options))
    margins=[dict(coordinate=a,fibre=f,total=sum(dom['fixed_counts'][dom['support'].index(a)][f]for dom in domains if a in dom['support']))for a in range(12)for f in range(3)]
    need(nextid==2593 and all(r['total']==10 for r in margins),'selector count and all36 margins')
    scope=dict(schema='FIXED_HADAMARD_FOUR_EXCEPTION_PROFILE_SCOPE_V1',selected_case=CURRENT_CASE,selection_path=key(SELECTION),selection_sha256=SELECTION_SHA,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],case_path=key(CASE),case_sha256=PINS[CASE],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=case['groups'],common_support=case['common_support'],circuit_relation=case['relation'],deviation_profile=case['profile'],balanced_groups=[g for g in range(20)if g not in case['groups']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,scope='All full prescribed-Gram factors in this literal four-exception profile with local column caps; cross-group caps and residualD omitted.',normalization='Balanced groups: first coordinate permutation identity. Exceptional groups: three words in increasing90-word-catalogue order. Both relabel only equal-support columns.',target_graph=False,derived_row_margins=margins)
    clauses=[];prefixes=[];cells=[];nextvar=2593
    def append(cs):
        meta=dict(first_clause=len(clauses)+1,clause_count=len(cs));clauses.extend(cs);return meta
    for dom in domains:
        xs=[o['selector']for o in dom['choices']];ps=list(range(nextvar,nextvar+len(xs)-1));nextvar+=len(ps)
        prefixes.append(dict(group=dom['group'],selectors=xs,prefixes=ps,**append(shared.onehot_clauses(xs,ps))))
    for a,b in pairs:
        incident=[dom for dom in domains if a in dom['support']and b in dom['support']];need(len(incident)==5,'each coordinate pair five incident groups')
        for f,z in product(range(3),repeat=2):
            contributions=[]
            for dom in incident:
                # Literal row-set intersections, separate from producer colour-word coefficient builder.
                coeff=[sum(12*f+a in rows and 12*z+b in rows for rows in option['lifted_rows'])for option in dom['choices']]
                need(set(coeff)<={0,1,2},'bounded integer contribution');channels=[]
                for threshold in(1,2):
                    xs=[o['selector']for o,n in zip(dom['choices'],coeff)if n>=threshold];v=nextvar;nextvar+=1
                    channels.append(dict(threshold=threshold,variable=v,selectors=xs,**append(shared.or_clauses(v,xs))))
                contributions.append(dict(group=dom['group'],coefficients=coeff,channels=channels))
            xs=[r['variable']for item in contributions for r in item['channels']];bound=1 if f==z else 2
            cells.append(dict(coordinates=[a,b],fibres=[f,z],bound=bound,group_contributions=contributions,count_inputs=xs,**append(shared.count_clauses(xs,bound))))
    need(nextvar==10565 and len(clauses)==187408,'complete dimensions')
    model=dict(schema='FIXED_HADAMARD_FOUR_EXCEPTION_PROFILE_WEIGHTED_THRESHOLD_CNF_V1',variables=10564,clauses=187408,primary_selectors=2592,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=2592,onehot_prefixes=2572,weighted_threshold_channels=5400),clause_populations=dict(onehot=10288,channels=122040,counts=55080),scope_sha256=PINS[D/'scope.json'])
    return scope,model,clauses

def object_check(values,model,scope,clauses,decoded=None):
    codec.all_clauses(clauses,values);F=[[0]*60 for _ in range(36)];selected=[];profiles=[]
    for dom in model['domains']:
        active=[o for o in dom['choices']if values[o['selector']]];need(len(active)==1,'exactly one selected option');o=active[0];selected.append(o['selector'])
        for d,word in zip(dom['columns'],o['colour_words']):
            for a,f in zip(dom['support'],word):F[12*f+a][d]=1
        counts=[[sum(F[12*f+a][d]for d in dom['columns'])for f in range(3)]for a in dom['support']];need(counts==dom['fixed_counts'],'raw selected profile')
        need(all(sum(F[r][d]*F[r][e]for r in range(36))<=2 for d,e in combinations(dom['columns'],2)),'raw within-group caps');profiles.append(dict(group=dom['group'],counts=counts))
    checks=shared.raw_factor(F,scope['core_adjacency36'],12,scope['L12x60']);order,canon=shared.canonical(F,12)
    obj=dict(factor=F,L=scope['L12x60'],selected_selector_ids=selected,actual_group_profiles=profiles,canonical_column_order=order,canonical_factor=canon,core_adjacency=scope['core_adjacency36'],target_gram=scope['prescribed_Gram36'],checks=checks,Gram_factor=True,factor_also_passes_column_caps=not checks['column_cap_violations'],factor_also_passes_mixed_caps=not checks['mixed_cap_violations'],target_graph=False,residual_D=None,profile_is_additional_assumption=True,model_sha256=PINS[D/'model.json'],scope_sha256=PINS[D/'scope.json'],independent_approval=False)
    if decoded is not None:need(same(obj,decoded),'complete independently decoded raw factor and diagnostics')
    return obj

def controls(scope,model,clauses):
    rejected=[]
    def reject(name,f):
        try:f()
        except(ValueError,AssertionError,IndexError,KeyError):rejected.append(name);return
        raise ValueError('corruption accepted: '+name)
    def truth(cs,vs):return all(any(vs[abs(x)]==(x>0)for x in c)for c in cs)
    prefix_count=0
    for n in range(2,7):
        cs=shared.onehot_clauses(list(range(1,n+1)),list(range(n+1,2*n)));seen=Counter()
        for bits in product((False,True),repeat=2*n-1):
            vs=dict(enumerate(bits,1));expected=sum(bits[:n])==1 and all(bits[n+i]==any(bits[:i+1])for i in range(n-1))
            need(truth(cs,vs)==expected,'bidirectional prefix truth');prefix_count+=1
            if expected:seen[bits[:n]]+=1
        need(len(seen)==n and set(seen.values())=={1},'unique prefix extension')
    OR_count=0
    for n in range(6):
        cs=shared.or_clauses(n+1,list(range(1,n+1)))
        for bits in product((False,True),repeat=n+1):need(truth(cs,dict(enumerate(bits,1)))==(bits[-1]==any(bits[:-1])),'OR including empty');OR_count+=1
    for bound in(1,2):
        cs=shared.count_clauses(list(range(1,11)),bound)
        for bits in product((False,True),repeat=10):need(truth(cs,dict(enumerate(bits,1)))==(sum(bits)==bound),'all ten-bit counts')
    cs=shared.onehot_clauses([1,2,3],[4,5])+shared.or_clauses(6,[2,3])+shared.or_clauses(7,[3])
    for bits in product((False,True),repeat=7):
        expected=sum(bits[:3])==1 and bits[3]==bits[0] and bits[4]==any(bits[:2]) and bits[5]==any(bits[1:3]) and bits[6]==bits[2]
        need(truth(cs,dict(enumerate(bits,1)))==expected,'weighted channel full truth')
        if expected:need(int(bits[5])+int(bits[6])==int(bits[1])+2*int(bits[2]),'exact weighted representation')
    reject('second_threshold_missing',lambda:need(truth(cs,{1:False,2:False,3:True,4:False,5:False,6:True,7:False}),'selected two requires q2'))
    fixture=read(FIXTURE);F=fixture['factor60x180'];C=fixture['cubic_core60'];checks=shared.raw_factor(F,C,20)
    need(not checks['column_cap_violations']and not checks['mixed_cap_violations'],'genuine243 positive');shared.raw_factor([r[::-1]for r in F],C,20);shared.canonical(F,20)
    for name in ['bit','bool','length','nonbinary']:
        bad=deepcopy(F)
        if name=='bit':bad[0][0]^=1
        elif name=='bool':bad[0][0]=bool(bad[0][0])
        elif name=='length':bad[0].pop()
        else:bad[0][0]=2
        reject('raw_'+name,lambda bad=bad:shared.raw_factor(bad,C,20))
    for name in ['coefficient','second_channel','bound','prefix','drop_initial_choice','lifted_row']:
        bad=deepcopy(model)
        if name=='coefficient':bad['pair_cell_counts'][0]['group_contributions'][0]['coefficients'][0]+=1
        elif name=='second_channel':bad['pair_cell_counts'][0]['group_contributions'][0]['channels'][1]['selectors'].append(1)
        elif name=='bound':bad['pair_cell_counts'][0]['bound']=2
        elif name=='prefix':bad['exact_one_prefix_rows'][0]['prefixes'][0]+=1
        elif name=='drop_initial_choice':bad['domains'][0]['choices'].pop()
        else:bad['domains'][0]['choices'][0]['lifted_rows'][0][0]+=1
        reject(name,lambda bad=bad:need(same(bad,model),'complete derived metadata'))
    bad=deepcopy(scope);bad['cross_group_column_caps_encoded']=True;reject('invent_cross_caps',lambda:need(same(bad,scope),'exact scope'))
    reject('dropped_clause',lambda:need(codec.cnf_bytes(clauses[:-1],10564)==(D/'instance.cnf').read_bytes(),'raw complete bytes'))
    bad=deepcopy(clauses);bad[10288][0]*=-1;reject('flipped_channel_clause',lambda:need(codec.cnf_bytes(bad,10564)==(D/'instance.cnf').read_bytes(),'raw signed clauses'))
    lits=[i if i%2 else -i for i in range(1,10565)];vals=codec.assignment(lits,10564)
    text='c SYNTHETIC CODEC ONLY; NOT RESEARCH SAT\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,lits[i:i+113]))for i in range(0,len(lits),113))+' 0\n';need(codec.native(text,10564)==vals,'full native JSON codec')
    synthetic=[[lits[i%10564]]for i in range(187408)];codec.all_clauses(synthetic,vals)
    for name,bad in [('status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('terminal',text.replace(' 0\n','\n')),('duplicate',text.replace('v 1 -2','v 1 1')),('post_zero',text+'v 1\n'),('range',text.replace('v 1 -2','v 10565 -2'))]:reject('native_'+name,lambda bad=bad:codec.native(bad,10564))
    reject('missing_JSON',lambda:codec.assignment(lits[:-1],10564));reject('Boolean_JSON',lambda:codec.assignment([True,*lits[1:]],10564))
    synthetic[-1][0]*=-1;reject('false_clause',lambda:codec.all_clauses(synthetic,vals));synthetic[-1][0]*=-1
    return dict(prefix_truth_cases=prefix_count,OR_truth_cases=OR_count,ten_bit_count_cases=2048,weighted_channel_cases=128,literal_triples_enumerated=117480,local_survivors=31110,rejected_corruptions=rejected,generic_positive='Authenticated SRG243 factor and reversed columns; not any research profile.',synthetic_positive='Full10564-ID/187408-clause codec only.',research_positive=None,research_positive_reason='No authenticated factor for these fifteen profiles exists in the inputs.'),text,synthetic

def main():
    global D,CASE,CURRENT_CASE
    import gzip
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--case',type=int);ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();value=sha(p);need(h is None or value==h,'input identity '+key(p));pins[key(p)]=value;PINS[p]=value
    try:
        for p,h in list(PINS.items()):pin(p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_FIFTEEN_PROFILES.md')
        batch=read(BATCH);selection=read(SELECTION)
        need(batch['selection']==selection['remaining_representatives']==CASES==[r['case']for r in batch['records']] and len(set(CASES))==15 and 0 not in CASES,'complete15 ordered representative universe')
        for p,h in batch['inputs_sha256'].items():pin(ROOT/p,h)
        # Authentication is aggregate even for one eventual SAT object.
        for rec in batch['records']:
            for kind in['summary','cnf','model','scope','model_package','receipt']:pin(ROOT/rec[kind+'_path'],rec[kind+'_sha256'])
            sub=read(ROOT/rec['summary_path']);need(sub['selected_case']==rec['case']and sub['variables']==10564 and sub['clauses']==187408,'per-case summary dimensions')
            for p,h in {**sub['inputs_sha256'],**sub['outputs_sha256']}.items():pin(ROOT/p,h)
            pack=read(ROOT/rec['model_package_path']);pin(ROOT/pack['gzip_path'],pack['gzip_sha256'])
            need(pack['raw_path']==rec['model_path']and pack['raw_sha256']==rec['model_sha256'],'scoped gzip recipe')
            recovered=gzip.decompress((ROOT/pack['gzip_path']).read_bytes());raw=(ROOT/rec['model_path']).read_bytes()
            need(recovered==raw and len(raw)==pack['raw_bytes']==pack['recovered_bytes']and len((ROOT/pack['gzip_path']).read_bytes())==pack['gzip_bytes'],'complete gzip literal identity')
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate_sha256,'explicit aggregate encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);gate=read(args.encoding_gate)
            need(gate['status']=='INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_ENCODING_PASS'and gate['selected_cases']==CASES,'exact fifteen encoding gate')
            direct=[RAW,BATCH,SELECTION,Path(__file__),*[ROOT/r[k+'_path']for r in batch['records']for k in['cnf','model','scope']]]
            for p in direct:need(gate['inputs_sha256'][key(p)]==pins[key(p)],'same encoding input/source '+key(p))
        if args.mode=='sat':need(args.case in CASES and args.assignment and args.native_output,'explicit selected case and complete SAT files')
        else:need(args.case is None,'aggregate audit cannot silently select only one case')
        catalog=catalogue();raw=read(RAW);records=[];all_controls=[]
        chosen=[r for r in batch['records']if args.mode!='sat'or r['case']==args.case]
        for index,rec in enumerate(chosen):
            CURRENT_CASE=rec['case'];D=(ROOT/rec['model_path']).parent;CASE=B/f'20260930_hadamard_four_group_local_screen/case_{CURRENT_CASE:03d}.json'
            need(key(CASE)in pins,'authenticated selected profile');scope,model,clauses=derive(raw,read(CASE),catalog)
            need(same(scope,read(ROOT/rec['scope_path']))and same(model,read(ROOT/rec['model_path'])),'complete independently derived case metadata')
            need(codec.cnf_bytes(clauses,10564)==(ROOT/rec['cnf_path']).read_bytes(),'every187408 actual clauses/header')
            # Fresh adversarial input checks in every case, not merely one batch sample.
            corrupt=[]
            for name in['drop48','wrong_coefficient','wrong_profile','wrong_case','wrong_signed_clause']:
                m=deepcopy(model);s=deepcopy(scope);cs=clauses
                if name=='drop48':next(d for d in m['domains']if d['group']in s['exceptional_groups'])['choices'].pop()
                elif name=='wrong_coefficient':m['pair_cell_counts'][0]['group_contributions'][0]['coefficients'][0]+=1
                elif name=='wrong_profile':s['deviation_profile'][0][0]+=1
                elif name=='wrong_case':s['selected_case']=0
                else:cs=deepcopy(clauses);cs[10288][0]*=-1
                try:need(same(m,model)and same(s,scope)and codec.cnf_bytes(cs,10564)==(ROOT/rec['cnf_path']).read_bytes(),'unmodified raw case reconstruction')
                except ValueError:corrupt.append(name)
                else:raise ValueError('accepted corruption '+name)
            all_controls.append(dict(case=CURRENT_CASE,rejected_corruptions=corrupt))
            if index==0:
                common,text,synthetic=controls(scope,model,clauses);save(out/'shared_controls.json',common);(out/'synthetic_native.log').write_text(text,encoding='ascii');(out/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,10564))
            if args.mode=='sat':
                pin(args.assignment);pin(args.native_output);vals=codec.assignment(read(args.assignment)['assignment'],10564);need(vals==codec.native(args.native_output.read_text(encoding='utf-8'),10564),'every10564 native/JSON literal')
                decoded=None
                if args.decoded:pin(args.decoded);decoded=read(args.decoded)
                obj=object_check(vals,model,scope,clauses,decoded);save(out/'independent_Gram_factor.json',obj)
            records.append(dict(case=CURRENT_CASE,cnf_path=rec['cnf_path'],cnf_sha256=rec['cnf_sha256'],model_path=rec['model_path'],model_sha256=rec['model_sha256'],scope_path=rec['scope_path'],scope_sha256=rec['scope_sha256'],variables=10564,clauses=187408,selectors=2592,exceptional_groups=scope['exceptional_groups'],initial_exceptional_domain_sizes=[len(d['choices'])for d in model['domains']if d['group']in scope['exceptional_groups']],balanced_groups=16,balanced_options_per_group=150,exact_Gram_cells=540))
            print(json.dumps(dict(state='INDEPENDENT_CASE_CHECKED',case=CURRENT_CASE,completed=index+1,total=len(chosen))),flush=True)
        save(out/'cases.json',records);save(out/'per_case_controls.json',all_controls)
        ts=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0,adapted_independent_source='acceleration/audit_20260930_hadamard_case0_profile.py',shared_components=['Frozen independent balanced-v2 core/Gram/raw-factor/clause helpers and oriented native/JSON codec.','Copied independently authored case0 reconstruction adapted to authenticated case and scope schemas.','No producer imports.']))
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-GRAM-ENCODINGS',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For each of the15 frozen case IDs6,12,18,24,30,36,42,48,51,72,78,84,90,96,102, its10564-variable187408-clause CNF is equivalent, up to independent column relabellings within equal-support triples, to a binary36x60 factor on the pinned six-prism Hadamard support with the complete prescribed integer Gram, exactly its recorded four-exception profile, and within-triple column caps. Each includes16 balanced domains of150 options and4 complete initial exceptional domains of48 options, with uniquely determined auxiliary extensions.',scope='Fifteen specified literal profiles; cross-group column caps and residualD omitted. The aggregate audit does not prove satisfiability, nonexistence, or coverage of unrestricted target graphs.',assumptions=['Pinned fixed core/support and each exact count profile.','Within-triple column caps.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN',revision=1,relation='verification_dependency',reason='Only raw case identities; all full48 initial domains independently reconstructed, no AC subset.')],verification_dependencies=[dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING',revision=1,relation='verification_dependency',reason='Frozen independently authored reconstruction and controls adapted to new cases; every new clause is checked again.')],verifier='/root/eight_domain_audit',producer='/root/state_literature_audit',method='Complete117480 raw local triple enumeration; literal row-set coefficients and all2,811,120 clause bytes reconstructed; per-case corruption controls; generic243 raw-factor and complete synthetic codec positives.',trusted_components=['Frozen independent helper code named in manifest.','Python standard library exact integer arithmetic.','No producer imports or native calls.'],limitations=['These profile restrictions are additional assumptions.','No native outcome is approved by this encoding gate.','A raw Gram factor would still need outside caps and residual completion.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending parent publication.',external_review=None,external_review_reason='Internal independent audit only.',created_at=ts,updated_at=ts,inputs_sha256=pins,evidence_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}))
        status={'audit':'INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_ENCODING_PASS','calibrate':'INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_OBJECT_CALIBRATION_PASS','sat':'INDEPENDENT_HADAMARD_FOUR_PROFILE_SAT_OBJECT_PASS'}[args.mode]
        save(out/'summary.json',dict(status=status,timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},selected_cases=CASES,checked_cases=[r['case']for r in records],formulas_checked=len(records),clauses_checked=187408*len(records),variables_per_formula=10564,clauses_per_formula=187408,controls=common,per_case_corruption_count=sum(len(r['rejected_corruptions'])for r in all_controls),all15_model_gzip_identities_checked=True,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,scope='Only the exact15 four-exception full-Gram profiles; neither unrestricted coverage nor residual completion.'));print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
