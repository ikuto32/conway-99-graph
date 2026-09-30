"""Independent literal eight-count-profile CNF/object audit; no producer imports."""
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,ast,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import audit_20260930_hadamard_seven_profile as prior

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_eight_count_profile_lift_second'
shared=prior.shared;codec=shared.codec;need=codec.need;sha=codec.sha;key=codec.key;read=codec.read;save=codec.save;same=codec.same
RAW=prior.RAW;LOCAL=prior.LOCAL;FIXTURE=prior.FIXTURE
PROFILE=B/'20260930_independent_review/count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json'
GATE=PROFILE.parent/'summary.json';PLAN=ROOT/'docs/AUDIT_20260930_EIGHT_COUNT_PROFILE_LIFT_SECOND.md'
ENCODING=B/'20260930_independent_review/eight_count_profile_lift_second/summary.json'
STATUSES=dict(audit='INDEPENDENT_SECOND_LITERAL_EIGHT_COUNT_PROFILE_ENCODING_PASS',calibrate='INDEPENDENT_SECOND_LITERAL_EIGHT_COUNT_PROFILE_OBJECT_CALIBRATION_PASS',sat='INDEPENDENT_SECOND_LITERAL_EIGHT_COUNT_PROFILE_SAT_OBJECT_PASS')
PINS={D/'summary.json':'f0f365365ef4ced6c5f547c23fb364048ca2c413a457c1c3f8f8c98d07786c0e',
 D/'instance.cnf':'dbd7b51dca52b69877888f88addc111f93f02ef52ddd58efebdc5c67e746bc87',D/'model.json':'14ad4ae64706db50e473f0ffa90bbdb8ce552dece5e1468ab066998ef71b7a32',D/'scope.json':'652225f2bf156a4bb1a92979504ec810bba3277137b889059f227d0c035f2afc',
 PROFILE:'7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0',GATE:'7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',
 RAW:prior.PINS[RAW],LOCAL:prior.PINS[LOCAL],FIXTURE:prior.PINS[FIXTURE],
 Path(prior.__file__):'7e60ee6823912af75cec5d43e6dd440fac7a419c2576f9258148463a60865729',Path(shared.__file__):prior.PINS[Path(shared.__file__)],Path(codec.__file__):prior.PINS[Path(codec.__file__)],
 ROOT/'acceleration/theory_20260930_eight_count_profile_lift_second.py':'b51b99d69bb48440ff145680f3c77ff58814605b4f01178375c7d041fbc14fe6',ROOT/'acceleration/theory_20260930_eight_count_profile_lift_second_spec.md':'0788df034b607e644b61fffb76e18ca9f70fff459c78247e9e3c868f34443427'}

def static_closure(path):
    seen=set();pending=[path]
    while pending:
        p=pending.pop().resolve()
        if p in seen:continue
        seen.add(p)
        for node in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
            names=[v.name for v in node.names]if isinstance(node,ast.Import)else [node.module]if isinstance(node,ast.ImportFrom)and node.module else []
            for name in names:
                q=ROOT/'acceleration'/(name.split('.')[0]+'.py')
                if q.is_file():pending.append(q)
    return seen

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
    need(exceptional==p['exceptional_groups']==[1,3,5,11,13,15,18,19]and p['exception_count']==8,'exact arbitrary count-table exception list')
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'integer count-table shape')
    need(all(counts[a][g]==[0,0,0]for g,s in enumerate(groups)for a in range(12)if a not in s),'off-support counts vanish')
    deviations=[[[counts[a][g][f]-int(a in groups[g])for g in exceptional]for f in range(3)]for a in range(12)]
    need(deviations==p['coordinate_fibre_deviations'],'raw deviations from literal counts')
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(digest==p['profile_sha256']=='086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17','literal profile digest')
    domains=[];ranks=[];nextid=1
    for g,s in enumerate(groups):
        wanted=[counts[a][g]for a in s];signature=tuple(sum(wanted,[]));ids=index.get(signature,[])
        need(ids and ids==p['local_survivor_indices_by_group'][g],'complete raw count class')
        if g in exceptional:
            need(len(ids)==[21,48,21,48,48,48,21,21][exceptional.index(g)],'complete exceptional class');options=[dict(choice_index=j,local_survivor_index=i,word_indices=triples[i],colour_words=[words[w]for w in triples[i]])for j,i in enumerate(ids)];kind='exceptional_sorted_local_triple'
        else:
            need(signature==(1,)*18 and len(ids)==150,'all150 balanced choices');options=deepcopy(balanced);kind='balanced_normalized_triple'
        for option in options:
            option['selector']=nextid;nextid+=1;option['lifted_rows']=[[12*f+a for a,f in zip(s,w)]for w in option['colour_words']]
            need([[sum(w[a]==f for w in option['colour_words'])for f in range(3)]for a in range(6)]==wanted,'literal option counts')
            need(all(len(set(u)&set(v))<=2 for u,v in combinations(option['lifted_rows'],2)),'literal within-triplicate cap')
            need(all(K[a][b]>0 for rows in option['lifted_rows']for a,b in combinations(rows,2)),'every prescribed zero entry absent')
        domains.append(dict(group=g,support=s,columns=columns[g],kind=kind,fixed_counts=wanted,choices=options));ranks.append(dict(group=g,count_signature=list(signature),local_survivor_indices=ids,count=len(ids)))
    margins=[dict(coordinate=a,fibre=f,total=sum(counts[a][g][f]for g in range(20)))for a in range(12)for f in range(3)]
    need(nextid==2077 and all(x['total']==10 for x in margins),'2076 selectors and all36 exact margins')
    need(all(K[12*f+a][12*z+b]==0 for a in range(12)for b in range(12)for f,z in product(range(3),repeat=2)if (a==b and f!=z)or a^1==b),'all90 omitted offdiagonal Gram entries zero')
    scope=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_SCOPE_V1',source_count_profile_path=key(PROFILE),source_count_profile_sha256=PINS[PROFILE],source_count_gate_path=key(GATE),source_count_gate_sha256=PINS[GATE],selected_profile_id='count_master_second_native_sat_after_six_cuts',selected_profile_sha256=digest,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=exceptional,coordinate_fibre_deviations=deviations,coordinate_group_fibre_counts=counts,balanced_groups=[g for g in range(20)if g not in exceptional],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in this one literal count profile and full initial local domains, with within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.',derived_row_margins=margins,selected_profile_artifact_sha256=PINS[PROFILE],initial_domains_path=key(D/'initial_domains.json'),initial_domains_sha256=sha(D/'initial_domains.json'))
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
    need(nextvar==9533 and len(clauses)==162124,'complete formula dimensions')
    model=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_WEIGHTED_CNF_V1',variables=9532,clauses=len(clauses),primary_selectors=2076,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=2076,onehot_prefixes=2056,weighted_threshold_channels=5400),clause_populations=dict(onehot=onehot,channels=len(clauses)-onehot-card,counts=card),scope_sha256=PINS[D/'scope.json'])
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
    rejected=[];truthcases=Counter()
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
    reject('dropped_actual_clause',lambda:need(codec.cnf_bytes(clauses[:-1],9532)==(D/'instance.cnf').read_bytes(),'complete raw bytes'))
    bad=deepcopy(clauses);bad[model['clause_populations']['onehot']][0]*=-1;reject('signed_actual_clause',lambda:need(codec.cnf_bytes(bad,9532)==(D/'instance.cnf').read_bytes(),'signed raw bytes'))
    local=[]
    for last in(False,True):
        selected={dom['choices'][-1 if last else 0]['selector']for dom in model['domains']};vals={i:i in selected for i in range(1,9533)};F=[[0]*60 for _ in range(36)]
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
    n=9532;m=162124;lits=[i if i%2 else -i for i in range(1,n+1)];vals=codec.assignment(lits,n);text='c SYNTHETIC CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,lits[i:i+113]))for i in range(0,n,113))+' 0\n';need(codec.native(text,n)==vals,'full signed native codec');synthetic=[[lits[i%n]]for i in range(m)];codec.all_clauses(synthetic,vals)
    for name,bad in [('status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('duplicate_status',text+'s SATISFIABLE\n'),('terminal',text.replace(' 0\n','\n')),('duplicate',text.replace('v 1 -2','v 1 1')),('post_zero',text+'v 1\n'),('range',text.replace('v 1 -2','v 9533 -2'))]:reject('native_'+name,lambda bad=bad:codec.native(bad,n))
    reject('missing_JSON',lambda:codec.assignment(lits[:-1],n));reject('Boolean_JSON',lambda:codec.assignment([True,*lits[1:]],n));reject('native_JSON_disagreement',lambda:need(codec.assignment([-lits[0],*lits[1:]],n)==vals,'native/JSON equality'));synthetic[-1][0]*=-1;reject('false_clause',lambda:codec.all_clauses(synthetic,vals));synthetic[-1][0]*=-1
    (out/'synthetic_native.stdout.log').write_text(text,encoding='ascii',newline='\n');save(out/'synthetic_assignment.json',dict(assignment=lits,research_SAT=False));(out/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,n))
    return dict(truth_cases=dict(truthcases),rejected_corruptions=rejected,generic_positive='Genuine independently authenticated SRG243 factor and reversed columns.',local_positive='First/last option for every domain: counts/support/margins only.',synthetic_positive='Full9532-ID/162124-clause codec only, no research factor.',research_factor_positive=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=list(STATUSES));ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--native-driver',type=Path);ap.add_argument('--native-driver-sha256');ap.add_argument('--native-spec',type=Path);ap.add_argument('--native-spec-sha256');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or h==v,'hash '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        candidate=read(D/'summary.json')
        for name,h in {**candidate['inputs_sha256'],**candidate['outputs_sha256']}.items():pin(ROOT/name,h)
        pin(Path(__file__));pin(PLAN);checker_closure=static_closure(Path(__file__))
        for p in checker_closure:pin(p)
        need(all(not p.name.startswith(('theory_','native_'))for p in checker_closure),'no producer/native imports')
        need(read(GATE)['status']=='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_NATIVE_SAT_OUTCOME_PASS','raw independent count witness gate')
        need(read(PROFILE)==read(D/'selected_profile.json'),'unchanged complete selected count witness')
        scope,model,clauses,initial=derive(read(RAW),read(PROFILE));need(same(scope,read(D/'scope.json'))and same(model,read(D/'model.json'))and same(initial,read(D/'initial_domains.json')),'all reconstructed metadata fields')
        need(codec.cnf_bytes(clauses,9532)==(D/'instance.cnf').read_bytes(),'complete actual162124 clause bytes')
        need(gzip.decompress((D/'model.json.gz').read_bytes())==(D/'model.json').read_bytes(),'complete model recovery bytes')
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate.resolve()==ENCODING.resolve()and args.encoding_gate_sha256,'explicit exact encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);eg=read(args.encoding_gate);need(eg['status']==STATUSES['audit'],'approved same encoding')
            for name,h in eg['inputs_sha256'].items():pin(ROOT/name,h)
        native_closure=[]
        if args.mode=='calibrate':
            need(args.native_driver and args.native_driver_sha256 and args.native_spec and args.native_spec_sha256,'explicit frozen native source/spec calibration pins');pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            ns=static_closure(args.native_driver)|{args.native_spec.resolve(),ROOT/'acceleration/theory_20260930_eight_count_profile_lift_second_spec.md',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'}
            for p in ns:pin(p)
            native_closure=sorted(map(key,ns))
        if args.mode in('audit','calibrate'):control=controls(scope,model,clauses,out);save(out/'controls.json',control)
        else:
            control=None;need(args.assignment and args.native_output,'raw complete SAT inputs');pin(args.assignment);pin(args.native_output);vals=codec.assignment(read(args.assignment)['assignment'],9532);need(vals==codec.native(args.native_output.read_text(encoding='utf-8'),9532),'every native and JSON literal');decoded=None
            if args.decoded:pin(args.decoded);decoded=read(args.decoded)
            save(out/'independent_Gram_factor.json',object_check(vals,model,scope,clauses,decoded))
        stamp=datetime.now(timezone.utc).isoformat();need(time.perf_counter()-start<120,'120-second audit allocation')
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SECOND-EIGHT-COUNT-PROFILE-GRAM-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The complete9532-variable162124-clause CNF is satisfiable iff the pinned six-prism Hadamard support admits a binary36x60 factor with the full prescribed integer Gram, literal count-profile digest 086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17 and within-triplicate column caps, modulo independent permutations of each identical-support column triple. The eight exceptional domains retain21,48,21,48,48,48,21,21 options respectively and all twelve balanced domains retain150, with unique auxiliary assignments.',scope='One literal eight-exception count profile. Cross-group caps and residualD omitted; no orbit coverage or unrestricted conclusion.',dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency')],verifier='/root',producer='/root/eight_domain_audit',checking_method='Complete separately authored raw catalogue/count-class/Gram coefficient/metadata/clause reconstruction and exact positive/corrupt controls.',shared_components=['Frozen independent seven-profile catalogue enumeration.','Frozen independent balanced Gram/CNF routines and oriented native/JSON codecs.','No producer imports; Python exact integers.'],inputs_sha256=pins,limitations=['No native calls or SAT/UNSAT outcome.','Only literal-profile scope; outside caps/D remain.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Independent internal verification only.',created_at=stamp,updated_at=stamp))
        save(out/'summary.json',dict(status=STATUSES[args.mode],timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},variables=9532,clauses=162124,selectors=2076,Gram_cells=540,literal_triples_enumerated=117480,local_survivors=31110,exceptional_groups=8,exceptional_initial_domain_counts=[21,48,21,48,48,48,21,21],balanced_groups=12,balanced_choices=150,controls=control,native_source_closure=native_closure,checker_source_closure=sorted(map(key,checker_closure)),elapsed_seconds=time.perf_counter()-start,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,residual_D_encoded=False,scope=scope['scope']))
        print(json.dumps(dict(status=STATUSES[args.mode],summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except Exception as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
