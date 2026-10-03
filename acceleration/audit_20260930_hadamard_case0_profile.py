"""Independent literal-domain, full-CNF and raw-factor checker for case0."""
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
PINS={D/'summary.json':'56a23f8ad3c959fe4cc674da836dc3fe06516ee6b02af53a1b323859e6864a7f',D/'instance.cnf':'2e949832491635b794e02b525ac983c0920d66cf91ee4e039564c5920008b22e',D/'model.json':'6705e33a26c332d093e3a2bff6dcd5dca276c6b50da2b24c61c7cbf891e0629c',D/'scope.json':'cd00a5e77575b7fd61604f1708a067bca4802f496108e86bd2847cee3c7549aa',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',CASE:'0b4f3c5ee3a51e83f40d3a2519f87e80d63842c6fcd4f4c125e808d11c44b7ab',FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 Path(shared.__file__):'cfddc6521887d6d44904ee7f2b92b0f189cfe5675b4f8d12d6df96ffe830e35c',Path(codec.__file__):'f572c91dc43f7208d34976b165c621c1b314e6963e437eaa475520ae1eb0add3',
 ROOT/'acceleration/theory_20260930_hadamard_case0_profile_cnf.py':'f8bee16361ab21bc3af5117691ec690e61ba9ad26bd50231c9616792af524455',ROOT/'acceleration/theory_20260930_hadamard_case0_profile_cnf_spec.md':'fb9b8573874a045518e99b3719b6512951fb4c8f1fd471fb4838a7f90aa029de',
 ROOT/'acceleration/native_20260930_hadamard_case0_profile.py':'c716f4b96def7954aa23aa953c72c6c6efa127f8123bb177e98b4fff2df26281',ROOT/'acceleration/native_20260930_hadamard_case0_profile_spec.md':'08e9a2f3f65c19de3c2c46ce785d7ab043291ababe14c2bbb6f23135f3d53639',
 ROOT/'acceleration/native_20260930_unrestricted_full99.py':'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',ROOT/'acceleration/native_20260930_proof_location.py':'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
 B/'20260930_independent_review/four_group_ac_calibration/summary.json':'6e53216e9d00ec8990217f80b84c3ed8cc1766d5eaae85c1fc3aead081b4ec6e'}

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
    need(case['case']==0 and case['groups']==[0,7,9,19] and case['relation']==[1,-1,-1,1] and case['common_support']==[2,4] and case['profile']==[[-1,0,1],[1,0,-1]],'literal case0')
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
    scope=dict(schema='FIXED_HADAMARD_CASE0_PROFILE_SCOPE_V1',raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],case_path=key(CASE),case_sha256=PINS[CASE],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=case['groups'],common_support=case['common_support'],circuit_relation=case['relation'],deviation_profile=case['profile'],balanced_groups=[g for g in range(20)if g not in case['groups']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,scope='All full prescribed-Gram factors in this literal four-exception profile with local column caps; cross-group caps and residualD omitted.',normalization='Balanced groups: first coordinate permutation identity. Exceptional groups: three words in increasing90-word-catalogue order. Both relabel only equal-support columns.',target_graph=False,derived_row_margins=margins)
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
    model=dict(schema='FIXED_HADAMARD_CASE0_PROFILE_WEIGHTED_THRESHOLD_CNF_V1',variables=10564,clauses=187408,primary_selectors=2592,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=2592,onehot_prefixes=2572,weighted_threshold_channels=5400),clause_populations=dict(onehot=10288,channels=122040,counts=55080),scope_sha256=PINS[D/'scope.json'])
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
    return dict(prefix_truth_cases=prefix_count,OR_truth_cases=OR_count,ten_bit_count_cases=2048,weighted_channel_cases=128,literal_triples_enumerated=117480,local_survivors=31110,rejected_corruptions=rejected,generic_positive='Authenticated SRG243 factor and reversed columns; not the research case0.',synthetic_positive='Full10564-ID/187408-clause codec only.',research_positive=None,research_positive_reason='No authenticated case0 factor exists in the inputs.'),text,synthetic

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();value=sha(p);need(h is None or value==h,'input identity '+key(p));pins[key(p)]=value
    try:
        for p,h in PINS.items():pin(p,h)
        prod=read(D/'summary.json')
        for p,h in {**prod['inputs_sha256'],**prod['outputs_sha256']}.items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_CASE0_PROFILE.md')
        scope,model,clauses=derive(read(RAW),read(CASE),catalogue())
        need(same(scope,read(D/'scope.json')) and same(model,read(D/'model.json')),'all independently reconstructed scope/model fields')
        need(codec.cnf_bytes(clauses,10564)==(D/'instance.cnf').read_bytes(),'every actual clause and exact header')
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate_sha256,'explicit encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);gate=read(args.encoding_gate)
            need(gate['status']=='INDEPENDENT_HADAMARD_CASE0_PROFILE_ENCODING_PASS','case0 encoding gate status')
            for p in[RAW,D/'scope.json',D/'model.json',D/'instance.cnf',Path(__file__)]:need(gate['inputs_sha256'][key(p)]==pins[key(p)],'same encoding inputs/source')
        control,text,synthetic=controls(scope,model,clauses);save(out/'controls.json',control);(out/'synthetic_native.log').write_text(text,encoding='ascii');(out/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,10564))
        if args.mode=='sat':
            need(args.assignment and args.native_output,'raw complete SAT artifacts');pin(args.assignment);pin(args.native_output);vals=codec.assignment(read(args.assignment)['assignment'],10564)
            need(vals==codec.native(args.native_output.read_text(encoding='utf-8'),10564),'all native/JSON values agree');decoded=None
            if args.decoded:pin(args.decoded);decoded=read(args.decoded)
            obj=object_check(vals,model,scope,clauses,decoded);save(out/'independent_Gram_factor.json',obj)
        ts=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,solver_calls=0))
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The frozen10564-variable187408-clause CNF is equivalent, modulo relabelling columns within each identical-support triple, to a binary36x60 factor on the pinned six-prism Hadamard support with the full prescribed integer Gram, literal case0 count profile, and within-triple column caps. All150 choices for each of16 balanced groups and all48 initial choices for each of4 exceptional groups are included; auxiliaries have unique extensions.',scope='Only this fixed support and literal profile: exceptional groups0,7,9,19, circuit signs1,-1,-1,1, common coordinates2,4, deviations[-1,0,1] and[1,0,-1]. Cross-group column caps and residualD are omitted.',assumptions=['Pinned core/support.','Exactly the recorded count profile and within-triple column caps.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN',revision=1,relation='verification_dependency',reason='Case identification and preserved initial domain records; all initial options independently re-enumerated, no AC pruning or orbit coverage used.')],verifier='/root/eight_domain_audit',producer='/root/state_literature_audit',method='Complete117480 local-triple enumeration; raw-core Gram and literal row-set coefficient reconstruction; every187408 CNF clause; exact truth/positive/corrupt controls.',shared_components=['Frozen independent balanced-v2 core/Gram/raw-factor/clause helpers and independent oriented-triples native/JSON codec.','Raw support, case, and genuine243 fixture.','No producer imports or producer clause generation called.'],limitations=['No target-wide normalization or graph automorphism assumption.','No research SAT/UNSAT result; cross-group caps diagnostics cannot establish residual completion.'],artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='Internal independent check only.',created_at=ts,updated_at=ts,inputs_sha256=pins,evidence_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}))
        status={'audit':'INDEPENDENT_HADAMARD_CASE0_PROFILE_ENCODING_PASS','calibrate':'INDEPENDENT_HADAMARD_CASE0_PROFILE_OBJECT_CALIBRATION_PASS','sat':'INDEPENDENT_HADAMARD_CASE0_PROFILE_SAT_OBJECT_PASS'}[args.mode]
        save(out/'summary.json',dict(status=status,timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},variables=10564,clauses=187408,selectors=2592,balanced_groups=16,exceptional_groups=4,options_per_balanced_group=150,options_per_exceptional_group=48,exact_cell_rows=540,controls=control,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,scope=scope['scope']));print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
