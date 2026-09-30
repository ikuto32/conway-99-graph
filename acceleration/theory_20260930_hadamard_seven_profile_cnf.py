"""Candidate first literal seven-exception full-Gram CNF, build only."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import theory_20260930_hadamard_four_profile_cnf as shared
ROOT=shared.ROOT;B=ROOT/'acceleration/results';RAW=shared.RAW;LOCAL=shared.LOCAL;BASE=shared.BASE
DOM=B/'20260930_hadamard_seven_profile_local_domains';PROFILES=DOM/'profiles.jsonl.gz'
ORBIT=B/'20260930_independent_review/hadamard_seven_fibre_orbits';SPEC=Path(__file__).with_name('theory_20260930_hadamard_seven_profile_cnf_spec.md')
EXPECTED_PROFILE='rank5_07_profile_0001'
EXPECTED_DIGEST='9344a387f8d178d3271f1dc817479f6a4747f7a55f3bea9d69bbc68b465b2510'
PINS={Path(shared.__file__):'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',Path(shared.__file__).with_name('theory_20260930_hadamard_four_profile_cnf_spec.md'):'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',BASE:'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',ROOT/'acceleration/theory_20260930_hadamard_six_profile_cnf.py':'cac3d732f9045b32b77648acfb246f3a6c842724ec232bd10321806bb079ca0a',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',PROFILES:'88d5e572fe280a70b51e0dd2785378d73300e6873a7db788072bcbca8ef256ae',DOM/'summary.json':'eb06d98f0e5fab055d07f8bea55e42132e35a340f82d72fad85adf0d175f04f7',B/'20260930_independent_review/hadamard_seven_profile_local_domains/summary.json':'764918cdb953f10f378304db4448000a8eee9b8e721e750fc62870df98fdbe2d',ORBIT/'summary.json':'930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f',ORBIT/'independent_orbits.json':'c6d3343b0319bf1e1971a488f5c08a3afcf50443ae01e725f951374cffffb12e',B/'20260930_independent_review/hadamard_seven_profile_arc/summary.json':'eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d',shared.FIXTURE:shared.PINS[shared.FIXTURE],shared.FIXTURE_GATE:shared.PINS[shared.FIXTURE_GATE]}
need=shared.need;sha=shared.sha;key=shared.key;read=shared.read;save=shared.save

def profile_digest(p):return hashlib.sha256(json.dumps(dict(groups=p['group_ids'],deviations=p['coordinate_fibre_deviations']),separators=(',',':'),sort_keys=True).encode()).hexdigest()
def validate_margins(scope,counts):
    rows=[]
    for a in range(12):
        for f in range(3):
            value=sum(counts[g][scope['groups'][g].index(a)][f] for g in range(20) if a in scope['groups'][g]);need(value==10,'literal profile margin ten');rows.append(dict(coordinate=a,fibre=f,total=value))
    return rows
def prepare(h,profile):
    raw=read(RAW);local=read(LOCAL);base=h.scope_from_raw(raw);words=local['words'];triples=local['survivors'];groups=base['groups'];need(profile_digest(profile)==profile['profile_sha256'],'raw profile identity');need(len(profile['group_ids'])==7,'exact seven exceptional groups')
    scope=dict(schema='FIXED_HADAMARD_SEVEN_EXCEPTION_PROFILE_SCOPE_V1',selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],profile_universe_path=key(PROFILES),profile_universe_sha256=PINS[PROFILES],raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=base['core_adjacency36'],prescribed_Gram36=base['prescribed_Gram36'],L12x60=base['L12x60'],groups=groups,group_columns=base['group_columns'],coordinate_pairs=base['coordinate_pairs'],exceptional_groups=profile['group_ids'],coordinate_fibre_deviations=profile['coordinate_fibre_deviations'],initial_domain_references=profile['local_domains'],balanced_groups=[g for g in range(20) if g not in profile['group_ids']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in one literal seven-exception count profile, retaining all initial local domains and within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced groups first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.')
    catalog=defaultdict(list)
    for li,t in enumerate(triples):catalog[tuple(sum(words[w][a]==f for w in t) for a in range(6) for f in range(3))].append(li)
    balanced=h.local_options();domains=[];selector=1;counts=[]
    for g,support in enumerate(groups):
        if g in profile['group_ids']:
            side=profile['group_ids'].index(g);ref=profile['local_domains'][side];need(ref['group']==g and sha(ROOT/ref['path'])==ref['sha256'],'bound initial domain');domain=read(ROOT/ref['path']);want=[[1+profile['coordinate_fibre_deviations'][a][f][side] for f in range(3)] for a in support];signature=tuple(x for row in want for x in row);ids=catalog[signature]
            need(list(signature)==domain['count_signature'] and ids==domain['local_survivor_indices'] and len(ids)==ref['count'],'complete initial domain, no AC reduction')
            choices=[dict(choice_index=i,local_survivor_index=li,word_indices=triples[li],colour_words=[words[w] for w in triples[li]]) for i,li in enumerate(ids)];kind='exceptional_sorted_local_triple'
        else:want=[[1]*3 for a in support];choices=[dict(choice_index=c['choice_index'],colour_words=c['colour_words'],coordinate_permutations=c['coordinate_permutations']) for c in balanced];kind='balanced_normalized_triple'
        need(choices,'nonempty initial group domain')
        for choice in choices:
            choice['selector']=selector;selector+=1;choice['lifted_rows']=[[12*w[pos]+a for pos,a in enumerate(support)] for w in choice['colour_words']]
            need([[sum(w[pos]==f for w in choice['colour_words']) for f in range(3)] for pos in range(6)]==want,'exact chosen count vector')
            need(all(len(set(c))==6 for c in choice['lifted_rows']) and all(len(set(c)&set(d))<=2 for c,d in combinations(choice['lifted_rows'],2)),'within-group cap domain')
            for column in choice['lifted_rows']:need(all(scope['prescribed_Gram36'][a][b]!=0 for a,b in combinations(column,2)),'all omitted zero Gram entries vanish')
        domains.append(dict(group=g,support=support,columns=scope['group_columns'][g],kind=kind,fixed_counts=want,choices=choices));counts.append(want)
    scope['derived_row_margins']=validate_margins(scope,counts)
    damaged=json.loads(json.dumps(counts));damaged[0][0][0]+=1
    try:validate_margins(scope,damaged)
    except ValueError:pass
    else:raise ValueError('changed profile count accepted')
    return scope,domains
def decode(assignment,model_path,scope_path,cnf_path):
    decoded=shared.decode(assignment,model_path,scope_path,cnf_path);scope=read(scope_path);decoded['selected_profile_id']=scope['selected_profile_id'];decoded['selected_profile_sha256']=scope['selected_profile_sha256'];return decoded
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profile-id',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    try:
        for path,h in PINS.items():need(sha(path)==h,'input/source pin '+key(path));inputs[key(path)]=h
        norm=read(ORBIT/'summary.json');need(norm['status']=='INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_FIBRE_NORMALIZATION_PASS','independent selection gate')
        orbit_records=read(ORBIT/'independent_orbits.json')['orbits'];survivors=sorted((r for r in orbit_records if not r['Gram_caps_empty']),key=lambda r:r['representative_id']);need(len(survivors)==216,'verified survivor population')
        chosen=survivors[0];need(chosen['representative_id']==args.profile_id==EXPECTED_PROFILE,'preregistered lexicographically first nonempty representative')
        with gzip.open(PROFILES,'rt',encoding='utf-8') as f:profiles=[json.loads(line) for line in f]
        matches=[p for p in profiles if p['id']==args.profile_id];need(len(matches)==1,'explicit unique literal profile');profile=matches[0]
        need(profile_digest(profile)==profile['profile_sha256']==EXPECTED_DIGEST,'frozen literal deviation values');need(profile['group_ids']==[0,1,4,7,8,9,19]and [r['count']for r in profile['local_domains']]==[48,48,48,21,48,48,48],'frozen complete initial domain sizes')
        for ref in profile['local_domains']:need(sha(ROOT/ref['path'])==ref['sha256'],'selected full domain');inputs[ref['path']]=ref['sha256']
        for path in (Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml'):inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(cooperative_build_seconds=120,solver_calls=0),selection_rule='Lexicographically first of216 independently reviewed nonempty seven-profile orbit representatives. Selection only; formula encodes one literal profile and retains all initial domains.',shared_components=['Adapted frozen generic six-profile producer prepare/decode.','Unchanged generic four-profile producer build/decode/gadget controls and its dynamically loaded balanced producer helper.','These are producer reuse, not independent verification.']))
        save(out/'selection.json',dict(profile_id=profile['id'],profile_sha256=profile['profile_sha256'],selected_orbit=chosen,nonempty_representative_population=[r['representative_id']for r in survivors],selection_rule='Lexicographically smallest literal profile ID.',selection_gate_path=key(ORBIT/'summary.json'),selection_gate_sha256=PINS[ORBIT/'summary.json'],formula_uses_orbit_pruning=False,formula_uses_AC_pruned_domains=False))
        h=shared.helper();save(out/'gadget_controls.json',shared.controls(h));save(out/'selected_profile.json',profile)
        scope,domains=prepare(h,profile);scope['selected_profile_artifact_sha256']=sha(out/'selected_profile.json');scope['selection_artifact_path']=key(out/'selection.json');scope['selection_artifact_sha256']=sha(out/'selection.json');scope['normalization_used_for_experiment_selection']=True;save(out/'scope.json',scope)
        model,clauses=shared.build(h,scope,domains);model['schema']='FIXED_HADAMARD_SEVEN_EXCEPTION_PROFILE_WEIGHTED_THRESHOLD_CNF_V1';model['scope_sha256']=sha(out/'scope.json')
        need(model['primary_selectors']==2259 and model['variables']==9898 and model['clauses']==171091,'preregistered dimensions from complete initial domains');save(out/'model.json',model)
        with (out/'instance.cnf').open('x',encoding='ascii',newline='\n') as f:
            f.write(f"p cnf {model['variables']} {model['clauses']}\n")
            for clause in clauses:f.write(' '.join(map(str,clause))+' 0\n')
        with (out/'model.json').open('rb') as source,(out/'model.json.gz').open('xb') as target:
            with gzip.GzipFile(filename='',mode='wb',fileobj=target,mtime=0) as packed:
                for chunk in iter(lambda:source.read(1048576),b''):packed.write(chunk)
        check=hashlib.sha256();recovered=0
        with gzip.open(out/'model.json.gz','rb') as f:
            for chunk in iter(lambda:f.read(1048576),b''):check.update(chunk);recovered+=len(chunk)
        need(check.hexdigest()==sha(out/'model.json')and recovered==(out/'model.json').stat().st_size,'exact lossless model recovery');need((out/'model.json.gz').stat().st_size<10*1024**2,'public-size model gzip')
        save(out/'model_package.json',dict(raw_path=key(out/'model.json'),raw_sha256=sha(out/'model.json'),raw_bytes=recovered,gzip_path=key(out/'model.json.gz'),gzip_sha256=sha(out/'model.json.gz'),gzip_bytes=(out/'model.json.gz').stat().st_size,recovery='gzip.decompress; verify raw SHA256/length.',artifact_availability='LOCAL_ONLY',public_size_ready=True))
        need(time.monotonic()-start<120,'cooperative build allocation');save(out/'profile_controls.json',dict(all36_margins_checked=True,all_domain_choices_zero_Gram_checked=True,changed_profile_count_rejected=True,independent_approval=False))
        result=dict(status='CANDIDATE_SEVEN_PROFILE_FULL_GROUPED_GRAM_CNF_BUILT',selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variables=model['variables'],clauses=model['clauses'],selectors=model['primary_selectors'],balanced_groups=13,balanced_choices_per_group=150,exceptional_groups=7,exceptional_initial_choices_per_group=[len(d['choices']) for d in domains if d['kind'].startswith('exceptional')],weighted_Gram_cells=540,weighted_threshold_channels=5400,within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,arc_pruning_used=False,orbit_coverage_used=False,normalization_used_for_experiment_selection=True,elapsed_seconds=time.monotonic()-start,independent_approval=False,solver_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY',scope=scope['scope'])
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=inputs));raise
if __name__=='__main__':main()
