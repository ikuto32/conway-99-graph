"""Independent literal seven-profile checker, adapted independent case0 path; no producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
import audit_20260930_hadamard_balanced_gram_v2 as shared

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_seven_profile_cnf/profile_0001'
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';CASE=B/'20260930_hadamard_four_group_local_screen/case_000.json'
FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
codec=shared.codec;need=codec.need;sha=codec.sha;key=codec.key;read=codec.read;save=codec.save;same=codec.same
PROFILE=D/'selected_profile.json'
PROFILES=B/'20260930_hadamard_seven_profile_local_domains/profiles.jsonl.gz'
PINS={D/'summary.json':'0f86492f989073715ba99dec81112f74bc0dfb62ab7500211dfe7a746e5b5ac2',D/'instance.cnf':'1e70d0a3b3ab5bd07f333e76681d8db0ba278e00e5d9de5d81363ebfbae93dab',D/'model.json':'1d6d08565f6b418b4dfc5ac8cdbdb9017084bb43fc959c0f3887ab6cf4842a7f',D/'scope.json':'7f97de196259b48184c9ec85b584b28829f905d9fa682c42612e43cf2b511ca0',PROFILE:'f4ae28194a12c140990ce1fc851f6e196c814e5cd55e46e448d2670a2c6fcd4a',PROFILES:'88d5e572fe280a70b51e0dd2785378d73300e6873a7db788072bcbca8ef256ae',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 Path(shared.__file__):'cfddc6521887d6d44904ee7f2b92b0f189cfe5675b4f8d12d6df96ffe830e35c',Path(codec.__file__):'f572c91dc43f7208d34976b165c621c1b314e6963e437eaa475520ae1eb0add3',
 ROOT/'acceleration/audit_20260930_hadamard_case0_profile.py':'53e37572532b5a13970098528b4be1b3ab9ef5b07f06c86e29d06955457654e1',
 ROOT/'acceleration/theory_20260930_hadamard_seven_profile_cnf.py':'04e4682a8f805a3203f668ad8d431bf3b2a429879eaa9c67973f41863948f747',ROOT/'acceleration/theory_20260930_hadamard_seven_profile_cnf_spec.md':'31e42758ea21c92bc428f3f512c7bc124c61032bd756d4f76c55cf2762f8512a',
 ROOT/'acceleration/native_20260930_hadamard_seven_profile.py':'f491282ead4361d0d9c394e815bc621e48afd1ff70a25b2d6a27332af22ee0f7',ROOT/'acceleration/native_20260930_hadamard_seven_profile_spec.md':'8664ec79d146d2ecdd1b1805b20074a17680992fcb533261a48b2b8559ec1f9b',
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

def derive(raw,profile,catalog):
    words,triples,balanced=catalog;L=raw['L'];C=raw['core_adjacency'];K=shared.gram_from_core(C,12)
    need(C==[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and i%12^1==j%12))for j in range(36)]for i in range(36)] and K==raw['prescribed_Gram36'],'literal core and prescribed Gram')
    supports=[[a for a in range(12)if L[a][d]]for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    columns=[[d for d,s in enumerate(supports)if s==g]for g in groups];pairs=[list(p)for p in combinations(range(12),2)if p[0]^1!=p[1]]
    need(len(groups)==20 and all(len(s)==6 and len(ds)==3 and all(sum(a in s for a in(m,m+1))==1 for m in range(0,12,2))for s,ds in zip(groups,columns)),'all support groups')
    need(profile['id']=='rank5_07_profile_0001' and profile['group_ids']==[0,1,4,7,8,9,19],'literal seven-group profile')
    domains=[];nextid=1
    for g,s in enumerate(groups):
        wanted=[[1]*3 for a in s]
        if g in profile['group_ids']:
            side=profile['group_ids'].index(g)
            wanted=[[1+profile['coordinate_fibre_deviations'][a][f][side]for f in range(3)]for a in s]
            found=[i for i,tri in enumerate(triples)if [[sum(words[w][p]==f for w in tri)for f in range(3)]for p in range(6)]==wanted]
            ref=profile['local_domains'][side];initial=read(ROOT/ref['path'])
            need(ref['group']==g and sha(ROOT/ref['path'])==ref['sha256'] and found==initial['local_survivor_indices'] and len(found)==ref['count'] and ref['count'] in (21,48) and sum(wanted,[])==initial['count_signature'],'all literal initial seven-profile options')
            options=[dict(choice_index=j,local_survivor_index=i,word_indices=triples[i],colour_words=[words[w]for w in triples[i]])for j,i in enumerate(found)];kind='exceptional_sorted_local_triple'
        else:options=deepcopy(balanced);kind='balanced_normalized_triple'
        for option in options:
            option['selector']=nextid;nextid+=1;option['lifted_rows']=[[12*f+a for a,f in zip(s,w)]for w in option['colour_words']]
            need([[sum(w[p]==f for w in option['colour_words'])for f in range(3)]for p in range(6)]==wanted,'all local count profiles')
            need(all(len(set(u)&set(v))<=2 for u,v in combinations(option['lifted_rows'],2)),'local column caps')
        domains.append(dict(group=g,support=s,columns=columns[g],kind=kind,fixed_counts=wanted,choices=options))
    margins=[dict(coordinate=a,fibre=f,total=sum(dom['fixed_counts'][dom['support'].index(a)][f]for dom in domains if a in dom['support']))for a in range(12)for f in range(3)]
    need(nextid==2260 and all(r['total']==10 for r in margins),'selector count and all36 margins')
    scope=dict(schema='FIXED_HADAMARD_SEVEN_EXCEPTION_PROFILE_SCOPE_V1',selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],profile_universe_path=key(PROFILES),profile_universe_sha256=PINS[PROFILES],raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=profile['group_ids'],coordinate_fibre_deviations=profile['coordinate_fibre_deviations'],initial_domain_references=profile['local_domains'],balanced_groups=[g for g in range(20)if g not in profile['group_ids']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in one literal seven-exception count profile, retaining all initial local domains and within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced groups first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.',derived_row_margins=margins,selected_profile_artifact_sha256=PINS[PROFILE],selection_artifact_path=key(D/'selection.json'),selection_artifact_sha256=sha(D/'selection.json'),normalization_used_for_experiment_selection=True)

    clauses=[];prefixes=[];cells=[];nextvar=2260
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
    need(nextvar==9899 and len(clauses)==171091,'complete dimensions')
    model=dict(schema='FIXED_HADAMARD_SEVEN_EXCEPTION_PROFILE_WEIGHTED_THRESHOLD_CNF_V1',variables=9898,clauses=171091,primary_selectors=2259,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=2259,onehot_prefixes=2239,weighted_threshold_channels=5400),clause_populations=dict(onehot=8956,channels=107055,counts=55080),scope_sha256=PINS[D/'scope.json'])
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
    obj['selected_profile_id']=scope['selected_profile_id'];obj['selected_profile_sha256']=scope['selected_profile_sha256']
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
    reject('dropped_clause',lambda:need(codec.cnf_bytes(clauses[:-1],9898)==(D/'instance.cnf').read_bytes(),'raw complete bytes'))
    bad=deepcopy(clauses);bad[8956][0]*=-1;reject('flipped_channel_clause',lambda:need(codec.cnf_bytes(bad,9898)==(D/'instance.cnf').read_bytes(),'raw signed clauses'))
    lits=[i if i%2 else -i for i in range(1,9899)];vals=codec.assignment(lits,9898)
    text='c SYNTHETIC CODEC ONLY; NOT RESEARCH SAT\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,lits[i:i+113]))for i in range(0,len(lits),113))+' 0\n';need(codec.native(text,9898)==vals,'full native JSON codec')
    synthetic=[[lits[i%9898]]for i in range(171091)];codec.all_clauses(synthetic,vals)
    for name,bad in [('status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('terminal',text.replace(' 0\n','\n')),('duplicate',text.replace('v 1 -2','v 1 1')),('post_zero',text+'v 1\n'),('range',text.replace('v 1 -2','v 9899 -2'))]:reject('native_'+name,lambda bad=bad:codec.native(bad,9898))
    reject('missing_JSON',lambda:codec.assignment(lits[:-1],9898));reject('Boolean_JSON',lambda:codec.assignment([True,*lits[1:]],9898))
    synthetic[-1][0]*=-1;reject('false_clause',lambda:codec.all_clauses(synthetic,vals));synthetic[-1][0]*=-1
    return dict(prefix_truth_cases=prefix_count,OR_truth_cases=OR_count,ten_bit_count_cases=2048,weighted_channel_cases=128,literal_triples_enumerated=117480,local_survivors=31110,rejected_corruptions=rejected,generic_positive='Authenticated SRG243 factor and reversed columns; not the research seven-profile.',synthetic_positive='Full9898-ID/171091-clause codec only.',research_positive=None,research_positive_reason='No authenticated seven-profile factor exists in the inputs.'),text,synthetic

def main():
    import gzip,hashlib
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();actual=sha(p);need(h is None or actual==h,'input identity '+key(p));pins[key(p)]=actual
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D/'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_SEVEN_PROFILE_CNF.md')
        profile=read(PROFILE);population=[json.loads(line)for line in gzip.decompress(PROFILES.read_bytes()).splitlines()]
        need([p for p in population if p['id']==profile['id']]==[profile],'one exact literal profile from frozen universe')
        selection=read(D/'selection.json');pin(D/'selection.json');need(selection['profile_id']==profile['id'] and selection['profile_sha256']==profile['profile_sha256'] and selection['nonempty_representative_population']==sorted(selection['nonempty_representative_population']) and len(selection['nonempty_representative_population'])==216 and selection['nonempty_representative_population'][0]==profile['id'],'literal selection bookkeeping only')
        digest=hashlib.sha256(json.dumps(dict(groups=profile['group_ids'],deviations=profile['coordinate_fibre_deviations']),separators=(',',':'),sort_keys=True).encode()).hexdigest();need(digest==profile['profile_sha256'],'raw profile digest')
        for r in profile['local_domains']:pin(ROOT/r['path'],r['sha256'])
        scope,model,clauses=derive(read(RAW),profile,catalogue())
        need(same(scope,read(D/'scope.json'))and same(model,read(D/'model.json')),'every independently reconstructed scope/model field')
        need(codec.cnf_bytes(clauses,9898)==(D/'instance.cnf').read_bytes(),'every171091 raw clause and header')
        need(gzip.decompress((D/'model.json.gz').read_bytes())==(D/'model.json').read_bytes(),'complete model gzip identity')
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate_sha256,'explicit encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);gate=read(args.encoding_gate);need(gate['status']=='INDEPENDENT_HADAMARD_SEVEN_PROFILE_ENCODING_PASS','exact encoding gate')
            for p in[RAW,PROFILE,D/'scope.json',D/'model.json',D/'instance.cnf',Path(__file__),*[ROOT/r['path']for r in profile['local_domains']]]:need(gate['inputs_sha256'][key(p)]==pins[key(p)],'unchanged direct input/source')
        control,text,synthetic=controls(scope,model,clauses);save(out/'controls.json',control);(out/'synthetic_native.log').write_text(text,encoding='ascii');(out/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,9898))
        # Literal profile changes must fail even when they preserve the number of groups.
        changed=deepcopy(profile);changed['coordinate_fibre_deviations'][2][0][0]+=1
        try:derive(read(RAW),changed,catalogue())
        except ValueError:save(out/'profile_corruption.json',dict(changed_deviation_rejected=True))
        else:raise ValueError('changed seven-profile deviation accepted')
        if args.mode=='sat':
            need(args.assignment and args.native_output,'complete raw SAT files');pin(args.assignment);pin(args.native_output);vals=codec.assignment(read(args.assignment)['assignment'],9898)
            need(vals==codec.native(args.native_output.read_text(encoding='utf-8'),9898),'every native and JSON literal');decoded=None
            if args.decoded:pin(args.decoded);decoded=read(args.decoded)
            save(out/'independent_Gram_factor.json',object_check(vals,model,scope,clauses,decoded))
        ts=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0,shared_components=['Adapted independently authored six-profile/case0 reconstruction, frozen independent balanced-v2 exact helpers and oriented native/JSON codec.','No producer imports.','Producer candidate orbit/AC records are authenticated provenance only; this literal-profile encoding does not use their conclusions.']))
        if args.mode=='audit':save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-PROFILE0001-GRAM-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The frozen9898-variable171091-clause CNF is equivalent, modulo independent column relabellings within each identical-support triple, to a binary36x60 factor on the pinned six-prism Hadamard support with the full prescribed integer Gram, exact count profile rank5_07_profile_0001 (digest 9344a387f8d178d3271f1dc817479f6a4747f7a55f3bea9d69bbc68b465b2510), and within-triple column caps. It includes13 complete balanced domains of150 choices and7 complete initial exceptional domains of sizes48,48,48,21,48,48,48, with unique auxiliary extensions.',scope='Only this explicit seven-exception profile; cross-group column caps and residualD omitted. No AC reduction or orbit-coverage premise.',assumptions=['Pinned fixed core/support and the exact literal count profile.','Within-triple column caps.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='verification_dependency',reason='Only literal profile/domain identity; all initial options independently re-enumerated.')],verification_dependencies=[dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING',revision=1,relation='verification_dependency',reason='Reuse of independently authored checking path, newly reconstructed clauses and calibrated dimensions.')],verifier='/root',producer='/root/eight_domain_audit',method='Full local triple enumeration, literal row-set contribution reconstruction, all metadata/clause bytes, exact profile/margin and positive/corrupt controls.',trusted_components=['Frozen independent helpers disclosed in manifest.','Python exact integer arithmetic; no producer imports.'],limitations=['No SAT/UNSAT result from encoding verification.','A Gram factor is not a99-vertex solution; omitted cross caps and residual completion remain.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Internal independent audit only.',created_at=ts,updated_at=ts,inputs_sha256=pins,evidence_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}))
        status={'audit':'INDEPENDENT_HADAMARD_SEVEN_PROFILE_ENCODING_PASS','calibrate':'INDEPENDENT_HADAMARD_SEVEN_PROFILE_OBJECT_CALIBRATION_PASS','sat':'INDEPENDENT_HADAMARD_SEVEN_PROFILE_SAT_OBJECT_PASS'}[args.mode]
        save(out/'summary.json',dict(status=status,timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},variables=9898,clauses=171091,selectors=2259,selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],exceptional_groups=7,balanced_groups=13,initial_exceptional_domains=[48,48,48,21,48,48,48],balanced_options_per_group=150,controls=control,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,orbit_coverage_used=False,arc_pruning_used=False,scope=scope['scope']));print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
