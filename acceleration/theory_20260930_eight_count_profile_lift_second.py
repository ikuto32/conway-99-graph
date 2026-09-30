"""Candidate full-Gram lift of the second checked eight-exception count profile."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import theory_20260930_hadamard_four_profile_cnf as shared
ROOT=shared.ROOT;B=ROOT/'acceleration/results';RAW=shared.RAW;LOCAL=shared.LOCAL
PROFILE=B/'20260930_independent_review/count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json';GATE=PROFILE.parent/'summary.json';SPEC=Path(__file__).with_name('theory_20260930_eight_count_profile_lift_second_spec.md')
PREVIOUS=ROOT/'acceleration/theory_20260930_eight_count_profile_lift.py'
PINS={PREVIOUS:'323bdedb0ad8e635cf40c9b2843e24b3960780dd2132b059c951590eec248963',PROFILE:'7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0',GATE:'7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',Path(shared.__file__):'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',Path(shared.__file__).with_name('theory_20260930_hadamard_four_profile_cnf_spec.md'):'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',shared.BASE:'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',shared.FIXTURE:shared.PINS[shared.FIXTURE],shared.FIXTURE_GATE:shared.PINS[shared.FIXTURE_GATE]}
need=shared.need;sha=shared.sha;key=shared.key;read=shared.read;save=shared.save
EXPECTED_DIGEST='086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17'

def margins(groups,counts):
    records=[]
    for a in range(12):
        for f in range(3):
            n=sum(counts[g][groups[g].index(a)][f]for g in range(20)if a in groups[g]);need(n==10,'literal row margin10');records.append(dict(coordinate=a,fibre=f,total=n))
    return records

def check_within(rows):
    need(len(rows)==3 and all(len(x)==6 and len(set(x))==6 for x in rows),'three six-entry columns')
    need(all(len(set(x)&set(y))<=2 for x,y in combinations(rows,2)),'all within-group caps')

def check_zero(rows,gram):
    need(all(gram[a][b]!=0 for column in rows for a,b in combinations(column,2)),'all automatic zero Gram entries')

def prepare(h,p):
    base=h.scope_from_raw(read(RAW));groups=base['groups'];catalog=read(LOCAL);words=catalog['words'];triples=catalog['survivors'];counts=p['coordinate_group_fibre_counts'];exceptional=p['exceptional_groups'];expected=p['local_survivor_indices_by_group'];by_signature=defaultdict(list)
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'literal count table shape/bounds')
    for a in range(12):
        for g,support in enumerate(groups):need(sum(counts[a][g])==(3 if a in support else 0),'raw support coordinate totals')
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=p['coordinate_fibre_deviations']),sort_keys=True,separators=(',',':')).encode()).hexdigest();need(digest==p['profile_sha256'],'literal profile digest')
    actual_exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)];need(actual_exceptional==exceptional and len(exceptional)==p['exception_count'],'actual arbitrary exception list')
    for ti,t in enumerate(triples):by_signature[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(ti)
    scope=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_SCOPE_V1',source_count_profile_path=key(PROFILE),source_count_profile_sha256=PINS[PROFILE],source_count_gate_path=key(GATE),source_count_gate_sha256=PINS[GATE],selected_profile_id='count_master_second_native_sat_after_six_cuts',selected_profile_sha256=digest,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=base['core_adjacency36'],prescribed_Gram36=base['prescribed_Gram36'],L12x60=base['L12x60'],groups=groups,group_columns=base['group_columns'],coordinate_pairs=base['coordinate_pairs'],exceptional_groups=exceptional,coordinate_fibre_deviations=p['coordinate_fibre_deviations'],coordinate_group_fibre_counts=counts,balanced_groups=[g for g in range(20)if g not in exceptional],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in this one literal count profile and full initial local domains, with within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.')
    balanced=h.local_options();domains=[];rank_lists=[];selector=1;wanted_counts=[]
    for g,support in enumerate(groups):
        want=[counts[a][g]for a in support];signature=tuple(x for row in want for x in row);ids=by_signature[signature];need(ids==expected[g]and ids,'complete original initial signature class')
        if g in exceptional:choices=[dict(choice_index=i,local_survivor_index=ti,word_indices=triples[ti],colour_words=[words[w]for w in triples[ti]])for i,ti in enumerate(ids)];kind='exceptional_sorted_local_triple'
        else:need(signature==(1,)*18 and len(ids)==150,'balanced class');choices=[dict(choice_index=c['choice_index'],colour_words=c['colour_words'],coordinate_permutations=c['coordinate_permutations'])for c in balanced];kind='balanced_normalized_triple'
        for c in choices:
            c['selector']=selector;selector+=1;c['lifted_rows']=[[12*w[pos]+a for pos,a in enumerate(support)]for w in c['colour_words']]
            need([[sum(w[pos]==f for w in c['colour_words'])for f in range(3)]for pos in range(6)]==want,'all literal option counts')
            check_within(c['lifted_rows'])
            check_zero(c['lifted_rows'],scope['prescribed_Gram36'])
        domains.append(dict(group=g,support=support,columns=scope['group_columns'][g],kind=kind,fixed_counts=want,choices=choices));wanted_counts.append(want);rank_lists.append(dict(group=g,count_signature=list(signature),local_survivor_indices=ids,count=len(ids)))
    scope['derived_row_margins']=margins(groups,wanted_counts)
    damaged=json.loads(json.dumps(wanted_counts));damaged[0][0][0]+=1
    try:margins(groups,damaged)
    except ValueError:pass
    else:raise ValueError('changed profile accepted')
    for g in range(20):
        for ids in [rank_lists[g]['local_survivor_indices'][:-1],rank_lists[g]['local_survivor_indices']+[rank_lists[g]['local_survivor_indices'][0]]]:need(ids!=expected[g],'missing/extra domain control')
    try:check_within([list(range(6))]*3)
    except ValueError:pass
    else:raise ValueError('overlap corruption accepted')
    zero=next((a,b)for a in range(36)for b in range(a+1,36)if scope['prescribed_Gram36'][a][b]==0)
    try:check_zero([list(zero)],scope['prescribed_Gram36'])
    except ValueError:pass
    else:raise ValueError('zero-Gram corruption accepted')
    return scope,domains,rank_lists

def decode(assignment,model_path,scope_path,cnf_path):
    result=shared.decode(assignment,model_path,scope_path,cnf_path);scope=read(scope_path);result['selected_profile_sha256']=scope['selected_profile_sha256'];result['selected_profile_id']=scope['selected_profile_id'];return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    try:
        for p,h in PINS.items():need(sha(p)==h,'pin '+key(p));pins[key(p)]=h
        for p in [Path(__file__),SPEC,shared.BASE.with_name(shared.BASE.stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        need(read(GATE)['status']=='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_NATIVE_SAT_OUTCOME_PASS','literal count-object gate');need(read(GATE)['outputs_sha256'][key(PROFILE)]==PINS[PROFILE],'independent gate binds raw count object');p=read(PROFILE);need(p['profile_sha256']==EXPECTED_DIGEST and p['exceptional_groups']==[1,3,5,11,13,15,18,19],'preregistered literal selection')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(cooperative_seconds=120,planning_memory_bytes=1024**3,solver_calls=0),selection='Exactly the independently checked second native count-master witness after six orbit cuts; not WLOG or an orbit census.',shared_components=['Unchanged four-profile weighted-threshold build/decode/gadget controls.','Its frozen dynamically loaded balanced producer helpers and generic243 fixture.','Adapted first literal eight-count producer; this source derives all new domain sizes.','All are producer reuse, not independent checking.']))
        h=shared.helper();save(out/'gadget_controls.json',shared.controls(h));scope,domains,ranks=prepare(h,p);initial_counts=[len(d['choices'])for d in domains if d['group']in p['exceptional_groups']];need(len(initial_counts)==8 and len(scope['balanced_groups'])==12,'literal eight-exception/twelve-balanced split');save(out/'selected_profile.json',p);save(out/'initial_domains.json',dict(records=ranks,all_initial=True,AC_pruning_used=False));scope['selected_profile_artifact_sha256']=sha(out/'selected_profile.json');scope['initial_domains_path']=key(out/'initial_domains.json');scope['initial_domains_sha256']=sha(out/'initial_domains.json');save(out/'scope.json',scope)
        model,clauses=shared.build(h,scope,domains);model['schema']='LITERAL_COUNT_PROFILE_FULL_GRAM_WEIGHTED_CNF_V1';model['scope_sha256']=sha(out/'scope.json');selector_count=12*150+sum(initial_counts);need((model['primary_selectors'],model['variables'],model['clauses'])==(selector_count,2*selector_count+5380,49*selector_count+60400),'dimensions from actual initial domain sizes');save(out/'model.json',model)
        with(out/'instance.cnf').open('x',encoding='ascii',newline='\n')as f:
            f.write(f"p cnf {model['variables']} {model['clauses']}\n")
            for c in clauses:f.write(' '.join(map(str,c))+' 0\n')
        with(out/'model.json').open('rb')as src,(out/'model.json.gz').open('xb')as target:
            with gzip.GzipFile(filename='',fileobj=target,mode='wb',mtime=0)as packed:
                for block in iter(lambda:src.read(1024**2),b''):packed.write(block)
        recovered=hashlib.sha256();length=0
        with gzip.open(out/'model.json.gz','rb')as f:
            for block in iter(lambda:f.read(1024**2),b''):recovered.update(block);length+=len(block)
        need(recovered.hexdigest()==sha(out/'model.json')and length==(out/'model.json').stat().st_size and(out/'model.json.gz').stat().st_size<10*1024**2,'complete public model recovery')
        save(out/'model_package.json',dict(raw_path=key(out/'model.json'),raw_sha256=sha(out/'model.json'),raw_bytes=length,gzip_path=key(out/'model.json.gz'),gzip_sha256=sha(out/'model.json.gz'),gzip_bytes=(out/'model.json.gz').stat().st_size,recovery_identity=True))
        save(out/'profile_controls.json',dict(all20_initial_rank_lists_checked=True,all36_margins_checked=True,all_options_zero_Gram_and_within_caps_checked=True,changed_profile_rejected=True,missing_and_extra_initial_domain_rejected=True,missing_and_extra_checks=40,overlapping_local_columns_rejected=True,zero_Gram_pair_rejected=True,full_research_factor_positive=False));need(time.monotonic()-start<120,'120-second allocation')
        summary=dict(status='CANDIDATE_SECOND_LITERAL_EIGHT_COUNT_PROFILE_FULL_GRAM_CNF_BUILT',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},selected_profile_sha256=EXPECTED_DIGEST,variables=model['variables'],clauses=model['clauses'],selectors=model['primary_selectors'],balanced_groups=12,balanced_choices_per_group=150,exceptional_groups=p['exceptional_groups'],exceptional_initial_domain_counts=initial_counts,Gram_cells=540,within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,orbit_coverage_used=False,AC_pruning_used=False,elapsed_seconds=time.monotonic()-start,solver_calls=0,native_calls=0,independent_approval=False,target_resolution=False,artifact_availability='LOCAL_ONLY',scope=scope['scope']);save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
