"""Prepared gated literal exact-eight lift adapter, no native solver."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import permutations,combinations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import theory_20260930_hadamard_four_profile_cnf as shared
ROOT=shared.ROOT;B=ROOT/'acceleration/results';RAW=shared.RAW;LOCAL=shared.LOCAL
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md');PLAN=ROOT/'acceleration/theory_20260930_exact_eight_next_lift_plan.md';PROFILE=None;GATE=None
PREVIOUS=ROOT/'acceleration/theory_20260930_eight_count_profile_lift_third.py'
PINS={PREVIOUS:'59cf7df0013dc62b79812b784a15a7e9b42ee101510f5a94db0dcfa998812767',PREVIOUS.with_name(PREVIOUS.stem+'_spec.md'):'b6386f66bb570df301a766ce4e59f389850e3adcbf11cb959c614fcd0a5b221f',PLAN:'2bcfceed96539c62e8b7e877b4c248962bdef028d2751ff8f5d04c5c4245db3e',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',Path(shared.__file__):'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',Path(shared.__file__).with_name('theory_20260930_hadamard_four_profile_cnf_spec.md'):'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',shared.BASE:'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',shared.FIXTURE:shared.PINS[shared.FIXTURE],shared.FIXTURE_GATE:shared.PINS[shared.FIXTURE_GATE]}
WITNESSES=[('first','count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('second','count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('third','count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
need=shared.need;sha=shared.sha;key=shared.key;read=shared.read;save=shared.save

def flattened(counts):return tuple(x for row in counts for t in row for x in t)
def fibre_images(v):return {tuple(v[k+p[f]]for k in range(0,len(v),3)for f in range(3))for p in permutations(range(3))}

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
    scope=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_SCOPE_V1',source_count_profile_path=key(PROFILE),source_count_profile_sha256=PINS[PROFILE],source_count_gate_path=key(GATE),source_count_gate_sha256=PINS[GATE],selected_profile_id='exact_eight_first_block_survivor_outside_three_historical_orbits',selected_profile_sha256=digest,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=base['core_adjacency36'],prescribed_Gram36=base['prescribed_Gram36'],L12x60=base['L12x60'],groups=groups,group_columns=base['group_columns'],coordinate_pairs=base['coordinate_pairs'],exceptional_groups=exceptional,coordinate_fibre_deviations=p['coordinate_fibre_deviations'],coordinate_group_fibre_counts=counts,balanced_groups=[g for g in range(20)if g not in exceptional],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in this one literal count profile and full initial local domains, with within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.')
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
    global PROFILE,GATE
    ap=argparse.ArgumentParser();ap.add_argument('--block-gate',type=Path,required=True);ap.add_argument('--block-gate-sha256',required=True);ap.add_argument('--block-summary',type=Path,required=True);ap.add_argument('--block-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or v==h,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        for p in [Path(__file__),SPEC,shared.BASE.with_name(shared.BASE.stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        GATE=args.block_gate.resolve();pin(GATE,args.block_gate_sha256);gate=read(GATE);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS','complete independent block gate');pin(args.block_summary,args.block_summary_sha256);need(gate['inputs_sha256'][key(args.block_summary)]==args.block_summary_sha256,'gate binds full block summary');summary=read(args.block_summary);need(summary['complete']and summary['representatives_checked']==792 and summary['complete_profile_pair_tests']==47520,'full792x60 block coverage')
        for name,h in summary['outputs_sha256'].items():pin(ROOT/name,h);need(gate['inputs_sha256'].get(name)==h,'gate direct block output '+name)
        survivor_path=args.block_summary.resolve().parent/'surviving_representatives.json.gz';need(key(survivor_path)in summary['outputs_sha256'],'survivor binding')
        with gzip.open(survivor_path,'rt',encoding='utf-8')as f:survivors=json.load(f)
        need(survivors['complete'],'complete block-survivor list');historical=set();old=[]
        for label,folder,h in WITNESSES:
            p=B/f'20260930_independent_review/{folder}/independent_count_profile.json';pin(p,h);v=flattened(read(p)['coordinate_group_fibre_counts']);images=fibre_images(v);historical.update(images);old.append(dict(label=label,path=key(p),sha256=h,canonical_full_count_sha256=hashlib.sha256(bytes(min(images))).hexdigest(),distinct_images=len(images)))
        ordered=sorted(survivors['records'],key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']));need(len({r['canonical_fibre_profile_sha256']for r in ordered})==len(ordered),'distinct ordered survivors');eligible=[]
        for r in ordered:
            v=flattened(r['counts']);need(len(v)==720 and v==min(fibre_images(v))and hashlib.sha256(bytes(v)).hexdigest()==r['canonical_fibre_profile_sha256'],'literal canonical representative')
            if v not in historical:eligible.append(r)
        selection=dict(rule='First (subset_index, canonical_fibre_profile_sha256) outside all three historical full count-table fibre orbits.',plan_sha256=PINS[PLAN],block_gate_path=key(GATE),block_gate_sha256=args.block_gate_sha256,block_summary_path=key(args.block_summary),block_summary_sha256=args.block_summary_sha256,survivor_path=key(survivor_path),survivor_sha256=sha(survivor_path),historical_profiles=old,ordered_survivors=[dict(subset_index=r['subset_index'],canonical_fibre_profile_sha256=r['canonical_fibre_profile_sha256'])for r in ordered],eligible=[dict(subset_index=r['subset_index'],canonical_fibre_profile_sha256=r['canonical_fibre_profile_sha256'])for r in eligible],selected=None if not eligible else eligible[0]);save(out/'selection.json',selection)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(seconds=120,native_calls=0),shared_components=['Copied frozen third-lift domain preparation, adapted only to gated generic literal selection.','Frozen weighted four-profile producer build/decode and balanced helper.','Producer reuse, not independent checking.']))
        if not eligible:
            save(out/'summary.json',dict(status='CANDIDATE_NO_NEW_BLOCK_SURVIVOR_FOR_FROZEN_RULE',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},native_calls=0,formula_built=False,independent_approval=False));return
        chosen=eligible[0];counts=chosen['counts'];raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)];need(exceptional==chosen['exceptional_groups']and len(exceptional)==8,'actual eight exceptions');local=read(LOCAL);words=local['words'];triples=local['survivors'];classes=defaultdict(list)
        for i,t in enumerate(triples):classes[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
        deviations=[[[counts[a][g][f]-int(a in groups[g])for g in exceptional]for f in range(3)]for a in range(12)];compact=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest();ranks=[classes[tuple(x for a in s for x in counts[a][g])]for g,s in enumerate(groups)];need(all(ranks),'all original classes nonempty');p=dict(coordinate_group_fibre_counts=counts,coordinate_fibre_deviations=deviations,exceptional_groups=exceptional,exception_count=8,local_survivor_indices_by_group=ranks,profile_sha256=compact,full_count_profile_sha256=chosen['canonical_fibre_profile_sha256'],selected_subset_index=chosen['subset_index'],source_selection_path=key(out/'selection.json'),source_selection_sha256=sha(out/'selection.json'));PROFILE=out/'selected_profile.json';save(PROFILE,p);PINS[PROFILE]=sha(PROFILE);PINS[GATE]=args.block_gate_sha256
        h=shared.helper();save(out/'gadget_controls.json',shared.controls(h));scope,domains,records=prepare(h,p);scope['source_count_gate_role']='Independent complete block population gate; the new selected profile is deterministically derived, not a separately approved artifact.';scope['selection_path']=key(out/'selection.json');scope['selection_sha256']=sha(out/'selection.json');scope['selected_full_count_sha256']=chosen['canonical_fibre_profile_sha256'];save(out/'initial_domains.json',dict(records=records,all_initial=True,AC_pruning_used=False));scope['selected_profile_artifact_sha256']=sha(PROFILE);scope['initial_domains_path']=key(out/'initial_domains.json');scope['initial_domains_sha256']=sha(out/'initial_domains.json');save(out/'scope.json',scope)
        model,clauses=shared.build(h,scope,domains);model['schema']='LITERAL_COUNT_PROFILE_FULL_GRAM_WEIGHTED_CNF_V1';model['scope_sha256']=sha(out/'scope.json');S=sum(len(d['choices'])for d in domains);need((model['primary_selectors'],model['variables'],model['clauses'])==(S,2*S+5380,49*S+60400),'actual domain-derived dimensions');save(out/'model.json',model)
        with(out/'instance.cnf').open('x',encoding='ascii',newline='\n')as f:
            f.write(f"p cnf {model['variables']} {model['clauses']}\n")
            for c in clauses:f.write(' '.join(map(str,c))+' 0\n')
        with(out/'model.json').open('rb')as f,(out/'model.json.gz').open('xb')as packed:
            with gzip.GzipFile(fileobj=packed,mode='wb',filename='',mtime=0)as g:
                for block in iter(lambda:f.read(1048576),b''):g.write(block)
        recovered=hashlib.sha256();n=0
        with gzip.open(out/'model.json.gz','rb')as f:
            for block in iter(lambda:f.read(1048576),b''):recovered.update(block);n+=len(block)
        need(recovered.hexdigest()==sha(out/'model.json')and n==(out/'model.json').stat().st_size and(out/'model.json.gz').stat().st_size<10*1024**2,'complete public model recovery');save(out/'model_package.json',dict(raw_path=key(out/'model.json'),raw_sha256=sha(out/'model.json'),raw_bytes=n,gzip_path=key(out/'model.json.gz'),gzip_sha256=sha(out/'model.json.gz'),gzip_bytes=(out/'model.json.gz').stat().st_size,recovery_identity=True));need(time.perf_counter()-start<120,'120-second cooperative build')
        result=dict(status='CANDIDATE_EXACT_EIGHT_NEXT_LITERAL_FULL_GRAM_LIFT_BUILT',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},selected_profile_sha256=compact,selected_full_count_sha256=chosen['canonical_fibre_profile_sha256'],selected_subset_index=chosen['subset_index'],exceptional_groups=exceptional,initial_domain_sizes=[len(d['choices'])for d in domains],selectors=S,variables=model['variables'],clauses=model['clauses'],scope=scope['scope'],cross_group_column_caps_encoded=False,residual_D_encoded=False,AC_pruning_used=False,orbit_coverage_used=False,native_calls=0,independent_approval=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items()if k not in['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
