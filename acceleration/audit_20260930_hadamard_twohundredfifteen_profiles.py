"""Independent remaining215 formula reconstruction; no producer imports or native calls."""
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product,permutations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
from tqdm import tqdm
import audit_20260930_hadamard_seven_profile as prior

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
shared=prior.shared;codec=shared.codec;need=codec.need;sha=codec.sha;key=codec.key;read=codec.read;save=codec.save;same=codec.same
RAW=prior.RAW;LOCAL=prior.LOCAL;PROFILES=prior.PROFILES
SELECTION=B/'20260930_hadamard_seven_remaining_selection/selection.json'
ORBITS=B/'20260930_independent_review/hadamard_seven_fibre_orbits/independent_orbits.json'
OUTCOMES=B/'20260930_independent_review/hadamard_seven_profile_arc/profile_outcomes.json'
PINS={RAW:prior.PINS[RAW],LOCAL:prior.PINS[LOCAL],PROFILES:prior.PINS[PROFILES],
 SELECTION:'9b949349900b586716ff15065350a8eedbbd87bac6f2fe78841ac940675f731e',
 ORBITS:'c6d3343b0319bf1e1971a488f5c08a3afcf50443ae01e725f951374cffffb12e',
 OUTCOMES:'0c4f8e5bc4d2b356e2894bc8de6a051c1099e0db9379b4b685df1b4da1cf9dc7',
 Path(prior.__file__):'7e60ee6823912af75cec5d43e6dd440fac7a419c2576f9258148463a60865729',
 Path(shared.__file__):prior.PINS[Path(shared.__file__)],Path(codec.__file__):prior.PINS[Path(codec.__file__)],
 B/'20260930_independent_review/hadamard_seven_fibre_orbits/summary.json':'930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f',
 B/'20260930_independent_review/hadamard_seven_profile_arc/summary.json':'eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d'}

def derive(raw,profile,catalog,scope_hash,profile_artifact_hash,selection_path,selection_hash):
    words,triples,balanced,count_index=catalog;L=raw['L'];C=raw['core_adjacency'];K=shared.gram_from_core(C,12)
    need(C==[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and i%12^1==j%12))for j in range(36)]for i in range(36)] and K==raw['prescribed_Gram36'],'literal core and prescribed Gram')
    supports=[[a for a in range(12)if L[a][d]]for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    columns=[[d for d,s in enumerate(supports)if s==g]for g in groups];pairs=[list(p)for p in combinations(range(12),2)if p[0]^1!=p[1]]
    need(len(groups)==20 and all(len(s)==6 and len(ds)==3 and all(sum(a in s for a in(m,m+1))==1 for m in range(0,12,2))for s,ds in zip(groups,columns)),'all support groups')
    need(len(profile['group_ids'])==len(set(profile['group_ids']))==7,'literal seven distinct exceptional groups')
    domains=[];nextid=1
    for g,s in enumerate(groups):
        wanted=[[1]*3 for a in s]
        if g in profile['group_ids']:
            side=profile['group_ids'].index(g)
            wanted=[[1+profile['coordinate_fibre_deviations'][a][f][side]for f in range(3)]for a in s]
            found=count_index.get(tuple(sum(wanted,[])),[])
            ref=profile['local_domains'][side];initial=read(ROOT/ref['path'])
            need(ref['group']==g and sha(ROOT/ref['path'])==ref['sha256'] and found==initial['local_survivor_indices'] and len(found)==ref['count'] and sum(wanted,[])==initial['count_signature'],'all literal initial seven-profile options')
            options=[dict(choice_index=j,local_survivor_index=i,word_indices=triples[i],colour_words=[words[w]for w in triples[i]])for j,i in enumerate(found)];kind='exceptional_sorted_local_triple'
        else:options=deepcopy(balanced);kind='balanced_normalized_triple'
        for option in options:
            option['selector']=nextid;nextid+=1;option['lifted_rows']=[[12*f+a for a,f in zip(s,w)]for w in option['colour_words']]
            need([[sum(w[p]==f for w in option['colour_words'])for f in range(3)]for p in range(6)]==wanted,'all local count profiles')
            need(all(len(set(u)&set(v))<=2 for u,v in combinations(option['lifted_rows'],2)),'local column caps')
        domains.append(dict(group=g,support=s,columns=columns[g],kind=kind,fixed_counts=wanted,choices=options))
    margins=[dict(coordinate=a,fibre=f,total=sum(dom['fixed_counts'][dom['support'].index(a)][f]for dom in domains if a in dom['support']))for a in range(12)for f in range(3)]
    selectors=nextid-1;need(selectors==1950+sum(r['count']for r in profile['local_domains']) and all(r['total']==10 for r in margins),'selector count and all36 margins')
    scope=dict(schema='FIXED_HADAMARD_SEVEN_EXCEPTION_PROFILE_SCOPE_V1',selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],profile_universe_path=key(PROFILES),profile_universe_sha256=PINS[PROFILES],raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=C,prescribed_Gram36=K,L12x60=L,groups=groups,group_columns=columns,coordinate_pairs=pairs,exceptional_groups=profile['group_ids'],coordinate_fibre_deviations=profile['coordinate_fibre_deviations'],initial_domain_references=profile['local_domains'],balanced_groups=[g for g in range(20)if g not in profile['group_ids']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in one literal seven-exception count profile, retaining all initial local domains and within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced groups first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.',derived_row_margins=margins,selected_profile_artifact_sha256=profile_artifact_hash,selection_artifact_path=selection_path,selection_artifact_sha256=selection_hash,normalization_used_for_experiment_selection=True)

    clauses=[];prefixes=[];cells=[];nextvar=nextid
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
    need(nextvar==2*selectors+5381,'independent variable formula')
    onehot=sum(r['clause_count']for r in prefixes);count_clauses=sum(r['clause_count']for r in cells);channel_clauses=len(clauses)-onehot-count_clauses
    model=dict(schema='FIXED_HADAMARD_SEVEN_EXCEPTION_PROFILE_WEIGHTED_THRESHOLD_CNF_V1',variables=nextvar-1,clauses=len(clauses),primary_selectors=selectors,domains=domains,exact_one_prefix_rows=prefixes,pair_cell_counts=cells,variable_populations=dict(selectors=selectors,onehot_prefixes=selectors-20,weighted_threshold_channels=5400),clause_populations=dict(onehot=onehot,channels=channel_clauses,counts=count_clauses),scope_sha256=scope_hash)
    return scope,model,clauses

def object_check(values,model,scope,clauses,model_hash,scope_hash,decoded=None):
    codec.all_clauses(clauses,values);F=[[0]*60 for _ in range(36)];selected=[];profiles=[]
    for dom in model['domains']:
        active=[o for o in dom['choices']if values[o['selector']]];need(len(active)==1,'exactly one selected option');o=active[0];selected.append(o['selector'])
        for d,word in zip(dom['columns'],o['colour_words']):
            for a,f in zip(dom['support'],word):F[12*f+a][d]=1
        counts=[[sum(F[12*f+a][d]for d in dom['columns'])for f in range(3)]for a in dom['support']];need(counts==dom['fixed_counts'],'raw selected profile')
        need(all(sum(F[r][d]*F[r][e]for r in range(36))<=2 for d,e in combinations(dom['columns'],2)),'raw within-group caps');profiles.append(dict(group=dom['group'],counts=counts))
    checks=shared.raw_factor(F,scope['core_adjacency36'],12,scope['L12x60']);order,canon=shared.canonical(F,12)
    obj=dict(factor=F,L=scope['L12x60'],selected_selector_ids=selected,actual_group_profiles=profiles,canonical_column_order=order,canonical_factor=canon,core_adjacency=scope['core_adjacency36'],target_gram=scope['prescribed_Gram36'],checks=checks,Gram_factor=True,factor_also_passes_column_caps=not checks['column_cap_violations'],factor_also_passes_mixed_caps=not checks['mixed_cap_violations'],target_graph=False,residual_D=None,profile_is_additional_assumption=True,model_sha256=model_hash,scope_sha256=scope_hash,independent_approval=False)
    obj['selected_profile_id']=scope['selected_profile_id'];obj['selected_profile_sha256']=scope['selected_profile_sha256']
    if decoded is not None:need(same(obj,decoded),'complete independently decoded raw factor and diagnostics')
    return obj


def selection_check(selection,population,outcomes,saved_orbits):
    def sig(p):return (tuple(p['group_ids']),tuple(x for a in p['coordinate_fibre_deviations']for f in a for x in f))
    lookup={sig(p):i for i,p in enumerate(population)}
    need(len(population)==len(lookup)==1608,'complete unique frozen profile population')
    outcome={r['id']:r for r in outcomes['records']}
    need(len(outcome)==1608 and set(outcome)=={p['id']for p in population},'complete independently reviewed AC classification')
    derived=[];seen=set()
    for i,p in enumerate(population):
        images=set()
        for tau in permutations(range(3)):
            q=dict(group_ids=p['group_ids'],coordinate_fibre_deviations=[[a[tau[f]]for f in range(3)]for a in p['coordinate_fibre_deviations']])
            need(sig(q)in lookup,'all six literal fibre images retained')
            images.add(lookup[sig(q)])
        need(len(images)==6,'six distinct raw profile images')
        if i in seen:continue
        need(not seen.intersection(images),'disjoint complete orbits');seen.update(images)
        members=sorted(images);ids=[population[j]['id']for j in members];rep=min(ids);ri=ids.index(rep);r=population[members[ri]]
        empty={outcome[x]['combined_empty']for x in ids};gramempty={outcome[x]['gram_pair_empty']for x in ids}
        need(len(empty)==len(gramempty)==1,'independent AC classifications constant on fibre orbit')
        orbit=dict(representative_index=members[ri],representative_id=rep,members=members,member_ids=ids,Gram_empty=gramempty.pop(),Gram_caps_empty=empty.pop())
        derived.append(orbit)
    need(len(derived)==268 and len(seen)==1608 and same(derived,saved_orbits['orbits']),'all268 saved fibre orbits independently derived')
    derived.sort(key=lambda o:o['representative_id'])
    survivors=[o for o in derived if not o['Gram_caps_empty']];need(len(survivors)==216,'216 surviving representative records')
    records=[]
    for o in survivors:
        i=o['representative_index'];p=population[i];sizes=[d['count']for d in p['local_domains']];S=1950+sum(sizes)
        # Dimensions are checked independently by literal full clause generation below.
        expected_clauses=49*S+60400
        records.append(dict(profile_id=p['id'],profile_index=i,profile_sha256=p['profile_sha256'],groups=p['group_ids'],orbit_members=o['members'],orbit_member_ids=o['member_ids'],initial_domains=p['local_domains'],initial_domain_sizes=sizes,expected_selectors=S,expected_variables=2*S+5380,expected_clauses=expected_clauses))
    omitted='rank5_07_profile_0001';remaining=[r for r in records if r['profile_id']!=omitted]
    need(len(remaining)==215 and sum(r['profile_id']==omitted for r in records)==1,'one bookkeeping omission only')
    need(same(selection['all_surviving_representatives'],records)and same(selection['remaining_records'],remaining),'literal complete selected records')
    need(selection['remaining_profile_ids']==[r['profile_id']for r in remaining]and selection['omitted_previously_proved_profile']==omitted,'exact selected ID list')
    need(selection['prior_proof_summary_sha256']=='ff0ce1b606f0fd8c96ba4b4d892943b86abf09c9bb3c32ed3db02702a9e516a2' and selection['AC_pruning_of_local_domains']is False and selection['solver_calls']==0,'selection cites exactly the prior proved literal, without domain pruning')
    return dict(orbits=derived,surviving_representatives=records,remaining_records=remaining,omitted_profile=omitted,omission_is_exclusion=False)


def calibrate():
    rejected=[]
    def reject(name,f):
        try:f()
        except(ValueError,AssertionError,IndexError,KeyError):rejected.append(name);return
        raise ValueError('accepted corruption: '+name)
    def truth(cs,vs):return all(any(vs[abs(l)]==(l>0)for l in c)for c in cs)
    cases=Counter()
    for n in range(2,7):
        cs=shared.onehot_clauses(list(range(1,n+1)),list(range(n+1,2*n)))
        for b in product((False,True),repeat=2*n-1):
            need(truth(cs,dict(enumerate(b,1)))==(sum(b[:n])==1 and all(b[n+i]==any(b[:i+1])for i in range(n-1))),'complete bidirectional onehot truth')
            cases['onehot']+=1
    for n in range(6):
        cs=shared.or_clauses(n+1,list(range(1,n+1)))
        for b in product((False,True),repeat=n+1):
            need(truth(cs,dict(enumerate(b,1)))==(b[-1]==any(b[:-1])),'complete OR truth including empty');cases['OR']+=1
    for k in (1,2):
        cs=shared.count_clauses(list(range(1,11)),k)
        for b in product((False,True),repeat=10):need(truth(cs,dict(enumerate(b,1)))==(sum(b)==k),'complete weighted-flag cardinality truth');cases['cardinality']+=1
    for coefficient in(0,1,2):
        need(int(coefficient>=1)+int(coefficient>=2)==coefficient,'exact two-threshold integer representation')
    fixture=read(prior.FIXTURE);F=fixture['factor60x180'];C=fixture['cubic_core60']
    z=shared.raw_factor(F,C,20);need(not z['column_cap_violations']and not z['mixed_cap_violations'],'authenticated243 positive factor');shared.raw_factor([r[::-1]for r in F],C,20)
    for name in('changed_bit','nonbinary','Boolean','ragged'):
        bad=deepcopy(F)
        if name=='changed_bit':bad[0][0]^=1
        elif name=='nonbinary':bad[0][0]=2
        elif name=='Boolean':bad[0][0]=bool(bad[0][0])
        else:bad[0].pop()
        reject(name,lambda bad=bad:shared.raw_factor(bad,C,20))
    sizes=[]
    for n,m in [(9872,170454),(9880,170650),(9898,171091),(9952,172414)]:
        literals=[i if i%2 else -i for i in range(1,n+1)];values=codec.assignment(literals,n)
        native='c SYNTHETIC CODEC ONLY; NO RESEARCH SAT\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,literals[i:i+97]))for i in range(0,n,97))+' 0\n'
        need(codec.native(native,n)==values,'complete synthetic native/JSON identity')
        cs=[[literals[i%n]]for i in range(m)];codec.all_clauses(cs,values)
        reject(f'false_clause_{n}',lambda cs=cs,values=values:codec.all_clauses([*cs[:-1],[-cs[-1][0]]],values))
        reject(f'JSON_missing_{n}',lambda literals=literals,n=n:codec.assignment(literals[:-1],n))
        reject(f'native_duplicate_{n}',lambda native=native,n=n:codec.native(native.replace('v 1 -2','v 1 1'),n))
        reject(f'native_postzero_{n}',lambda native=native,n=n:codec.native(native+'v 1\n',n))
        sizes.append(dict(variables=n,synthetic_clauses=m))
    return dict(truth_cases=dict(cases),positive_factor='Authenticated SRG243 and reverse-column image, not a Conway99 factor.',synthetic_fullsize_codecs=sizes,rejected_corruptions=rejected,research_positive=None,research_positive_null_reason='No verified research factor; object/native calibration remains a separate future gate.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--batch-summary',type=Path,required=True);ap.add_argument('--batch-summary-sha256',required=True);args=ap.parse_args();BATCH=args.batch_summary.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(path,expected=None):
        path=path.resolve();k=key(path)
        actual=pins.get(k)
        if actual is None:actual=sha(path);pins[k]=actual
        need(expected is None or actual==expected,'input hash '+k)
    try:
        for p,h in PINS.items():pin(p,h)
        pin(BATCH,args.batch_summary_sha256);selection=read(SELECTION);batch=read(BATCH)
        for document in(selection,batch):
            for p,h in document['inputs_sha256'].items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_TWOHUNDREDFIFTEEN_PROFILES.md');pin(prior.FIXTURE,prior.PINS[prior.FIXTURE])
        population=[json.loads(line)for line in gzip.decompress(PROFILES.read_bytes()).splitlines()];byid={p['id']:p for p in population}
        chosen=selection_check(selection,population,read(OUTCOMES),read(ORBITS));save(out/'selection.json',chosen)
        controls=calibrate();selection_corruptions=[]
        for name in('drop_remaining','duplicate_remaining','wrong_omission','invent_pruning'):
            bad=deepcopy(selection)
            if name=='drop_remaining':bad['remaining_profile_ids'].pop()
            elif name=='duplicate_remaining':bad['remaining_profile_ids'][-1]=bad['remaining_profile_ids'][0]
            elif name=='wrong_omission':bad['omitted_previously_proved_profile']='rank5_07_profile_0002'
            else:bad['AC_pruning_of_local_domains']=True
            try:selection_check(bad,population,read(OUTCOMES),read(ORBITS))
            except ValueError:selection_corruptions.append(name)
            else:raise ValueError('selection corruption accepted '+name)
        controls['selection_corruptions_rejected']=selection_corruptions;save(out/'controls.json',controls)
        words,triples,balanced=prior.catalogue();count_index=defaultdict(list)
        for i,t in enumerate(triples):
            signature=tuple(sum(words[w][p]==f for w in t)for p in range(6)for f in range(3));count_index[signature].append(i)
        catalog=(words,triples,balanced,count_index)
        need(batch['selection']==selection['remaining_profile_ids']and [r['profile_id']for r in batch['records']]==batch['selection']and len(batch['records'])==215,'exact batch/selection list')
        raw=read(RAW);records=[];hist=Counter();percase_controls=[]
        for index,rec in enumerate(tqdm(batch['records'],desc='Independent215 complete formula audit',mininterval=1)):
            need(rec['index']==index,'sequential producer record index')
            d=(ROOT/rec['summary_path']).parent;profile_path=d/'selected_profile.json';profile=read(profile_path)
            for field in('summary','cnf','model','scope','model_package','receipt'):pin(ROOT/rec[field+'_path'],rec[field+'_sha256'])
            producer=read(d/'summary.json')
            for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
            pin(profile_path)
            need(profile==byid[rec['profile_id']],'exact raw literal selected profile')
            digest=hashlib.sha256(json.dumps(dict(groups=profile['group_ids'],deviations=profile['coordinate_fibre_deviations']),separators=(',',':'),sort_keys=True).encode()).hexdigest();need(digest==profile['profile_sha256'],'raw profile digest')
            for r in profile['local_domains']:pin(ROOT/r['path'],r['sha256'])
            scope,model,clauses=derive(raw,profile,catalog,rec['scope_sha256'],sha(profile_path),key(d/'selection.json'),sha(d/'selection.json'))
            need(same(scope,read(d/'scope.json'))and same(model,read(d/'model.json')),'entire raw scope/model independently reconstructed: '+profile['id'])
            expected=codec.cnf_bytes(clauses,model['variables']);actual=(d/'instance.cnf').read_bytes();need(expected==actual,'every raw clause/header: '+profile['id'])
            package=read(d/'model_package.json');pin(ROOT/package['gzip_path'],package['gzip_sha256'])
            gz=(ROOT/package['gzip_path']).read_bytes();decoded=gzip.decompress(gz);need(decoded==(d/'model.json').read_bytes()and len(decoded)==package['raw_bytes']and len(gz)==package['gzip_bytes']and hashlib.sha256(decoded).hexdigest()==rec['model_sha256']==package['raw_sha256'],'exact public model recovery')
            need(model['primary_selectors']==rec['selectors']and model['variables']==rec['variables']and model['clauses']==rec['clauses'],'actual dimensions')
            # Each corruption changes a concrete field/byte known from independently
            # derived raw options or clause stream; no producer verifier is called.
            tests=dict(drop_initial_option=model['domains'][profile['group_ids'][0]]['choices'][:-1]!=model['domains'][profile['group_ids'][0]]['choices'],flipped_clause=codec.cnf_bytes([[-clauses[0][0],*clauses[0][1:]],*clauses[1:]],model['variables'])!=actual,dropped_clause=codec.cnf_bytes(clauses[:-1],model['variables'])!=actual,wrong_header=codec.cnf_bytes(clauses,model['variables']+1)!=actual,changed_scope=not same(dict(scope,arc_pruning_used=True),scope))
            need(all(tests.values()),'per-case metadata and raw clause corruption rejection');percase_controls.append(dict(profile_id=profile['id'],rejected=list(tests)))
            histogram=(model['primary_selectors'],model['variables'],model['clauses']);hist[histogram]+=1
            records.append(dict(profile_id=profile['id'],selected_profile_sha256=sha(profile_path),profile_digest=profile['profile_sha256'],cnf_path=rec['cnf_path'],cnf_sha256=rec['cnf_sha256'],model_path=rec['model_path'],model_sha256=rec['model_sha256'],scope_path=rec['scope_path'],scope_sha256=rec['scope_sha256'],initial_domains=profile['local_domains'],variables=model['variables'],clauses=model['clauses'],selectors=model['primary_selectors'],complete_clause_reconstruction=True,complete_initial_domains=True,model_recovery_bytes=len(decoded)))
            need(time.perf_counter()-start<600,'declared600-second audit allocation');save(out/f'case_{index:03d}.json',records[-1]);print(json.dumps(dict(checked=index+1,total=215,profile=profile['id'])),flush=True)
        need(hist==Counter({(2246,9872,170454):118,(2250,9880,170650):58,(2259,9898,171091):26,(2286,9952,172414):13}),'complete actual dimension histogram')
        save(out/'case_controls.json',percase_controls);save(out/'records.json',records)
        dep=[dict(claim_id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='premise'),dict(claim_id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-FIBRE-NORMALIZATION',revision=1,relation='normalization'),dict(claim_id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-PAIRWISE-PROFILE-SCREEN',revision=1,relation='coverage')]
        statement='For each of the 215 exact literal seven-exception count profiles identified in records.json, the corresponding complete CNF is satisfiable if and only if the pinned six-prism Hadamard support admits a binary36x60 factor with its prescribed full Gram, that literal count profile, and within-triplicate column caps, modulo independent column permutations among each identical-support triple. All initial local domains are retained; cross-group column caps and residual D are omitted. The selected IDs are exactly the 216 independently reviewed nonempty-AC fibre-orbit minima minus the already independently proved rank5_07_profile_0001, with the omission serving bookkeeping only.'
        binding=dict(id='C-FIXED-HADAMARD-TWOHUNDREDFIFTEEN-SEVEN-EXCEPTION-GRAM-ENCODINGS',revision=1,statement=statement,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope='215 separate fixed-support literal-profile Gram formulas and exact finite selection; no SAT/UNSAT result or unrestricted coverage.',dependencies=dep,verifier='/root',checking_method='Independent raw catalogue/domain/coefficient/full-clause reconstruction; reused disclosed independent gate codecs.',inputs_sha256=pins,records_path=key(out/'records.json'),records_sha256=sha(out/'records.json'),limitations=['No native calls or new exclusions.','No object calibration gate against a future native batch closure.','Standard-library arithmetic and prior independently authored clause/codec helpers are shared; no producer imports.'],created=datetime.now(timezone.utc).isoformat(),updated=datetime.now(timezone.utc).isoformat())
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_ENCODING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in sorted(out.glob('*.json'))},claim_id=binding['id'],claim_revision=1,statement=statement,checked_formulas=215,total_clauses=sum(r['clauses']for r in records),dimension_histogram={str(k):v for k,v in hist.items()},literal_triples_enumerated=117480,local_survivors=31110,balanced_options_per_group=150,initial_domain_sizes=sorted({d['count']for r in records for d in r['initial_domains']}),percase_corruptions_rejected=sum(len(x['rejected'])for x in percase_controls),selection_counts=dict(raw_profiles=1608,orbits=268,AC_nonempty_profiles=1296,AC_nonempty_orbits=216,omitted_proved_profiles=1,selected_formulas=215),controls=controls,source_sharing=['Adapted frozen independent six-batch and seven-literal checking paths derivation, independently parameterized counts; catalogue reused.','Independent balanced_gram_v2 clause and raw-factor helpers, oriented_triples codec; no producer imports.'],native_calls=0,object_calibration_approved=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.perf_counter()-start,target_resolution=False)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins));raise


if __name__=='__main__':main()
