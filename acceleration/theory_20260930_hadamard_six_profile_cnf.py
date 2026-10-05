"""Candidate generic literal six-exception profile CNF; no solver on import/build."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
import theory_20260930_hadamard_four_profile_cnf as shared
ROOT=shared.ROOT;B=ROOT/'acceleration/results';RAW=shared.RAW;LOCAL=shared.LOCAL;BASE=shared.BASE
DOM=B/'20260930_hadamard_six_profile_local_domains';PROFILES=DOM/'profiles.jsonl.gz'
ORBIT=B/'20260930_hadamard_six_fibre_orbits';SPEC=Path(__file__).with_name('theory_20260930_hadamard_six_profile_cnf_spec.md')
PINS={Path(shared.__file__):'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',Path(shared.__file__).with_name('theory_20260930_hadamard_four_profile_cnf_spec.md'):'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',BASE:'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',PROFILES:'221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0',DOM/'summary.json':'b402b07d6d34776a9c54c8dc3905a37ac5e9cf880a7ce98283c788f3627c7809',B/'20260930_independent_review/hadamard_six_profile_local_domains/summary.json':'976e673b02c8742503a33d091e6ddf4650c13289e25fd859cb7854deb0174235',ORBIT/'summary.json':'ccba6e3aa029f1053039da2e31cb50eaca51e553cdf654b0a4d2e569970d651c',ORBIT/'first_surviving_profile.json':'720ea549dc720693fb0809dbac1d49960ee7c6b6e1b5d5e53342aa61c863999f',shared.FIXTURE:shared.PINS[shared.FIXTURE],shared.FIXTURE_GATE:shared.PINS[shared.FIXTURE_GATE]}
need=shared.need;sha=shared.sha;key=shared.key;read=shared.read;save=shared.save
def profile_digest(p):return hashlib.sha256(json.dumps(dict(groups=p['group_ids'],deviations=p['coordinate_fibre_deviations']),separators=(',',':'),sort_keys=True).encode()).hexdigest()
def validate_margins(scope,counts):
    rows=[]
    for a in range(12):
        for f in range(3):
            value=sum(counts[g][scope['groups'][g].index(a)][f] for g in range(20) if a in scope['groups'][g]);need(value==10,'literal profile margin ten');rows.append(dict(coordinate=a,fibre=f,total=value))
    return rows
def prepare(h,profile):
    raw=read(RAW);local=read(LOCAL);base=h.scope_from_raw(raw);words=local['words'];triples=local['survivors'];groups=base['groups'];need(profile_digest(profile)==profile['profile_sha256'],'raw profile identity');need(len(profile['group_ids'])==6,'exact six exceptional groups')
    scope=dict(schema='FIXED_HADAMARD_SIX_EXCEPTION_PROFILE_SCOPE_V1',selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],profile_universe_path=key(PROFILES),profile_universe_sha256=PINS[PROFILES],raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=base['core_adjacency36'],prescribed_Gram36=base['prescribed_Gram36'],L12x60=base['L12x60'],groups=groups,group_columns=base['group_columns'],coordinate_pairs=base['coordinate_pairs'],exceptional_groups=profile['group_ids'],coordinate_fibre_deviations=profile['coordinate_fibre_deviations'],initial_domain_references=profile['local_domains'],balanced_groups=[g for g in range(20) if g not in profile['group_ids']],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in one literal six-exception count profile, retaining all initial local domains and within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced groups first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.')
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
    ap=argparse.ArgumentParser();ap.add_argument('--profile-id',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,h in PINS.items():need(sha(path)==h,'input/source pin '+key(path))
        with gzip.open(PROFILES,'rt',encoding='utf-8') as f:profiles=[json.loads(line) for line in f]
        matches=[p for p in profiles if p['id']==args.profile_id];need(len(matches)==1,'explicit unique literal profile');profile=matches[0];inputs={key(p):d for p,d in PINS.items()}
        for ref in profile['local_domains']:need(sha(ROOT/ref['path'])==ref['sha256'],'selected full domain');inputs[ref['path']]=ref['sha256']
        for path in (Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml'):inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(cooperative_build_seconds=120,solver_calls=0),selection_rule='Explicit literal profile ID; no AC-pruned domains or orbit coverage premise.',shared_components=['Frozen generic four-profile producer build/decode/gadget controls and its balanced producer helper. These are producer reuse, not independent verification.']))
        h=shared.helper();control=shared.controls(h);save(out/'gadget_controls.json',control);save(out/'selected_profile.json',profile);scope,domains=prepare(h,profile);scope['selected_profile_artifact_sha256']=sha(out/'selected_profile.json');save(out/'scope.json',scope);model,clauses=shared.build(h,scope,domains);model['schema']='FIXED_HADAMARD_SIX_EXCEPTION_PROFILE_WEIGHTED_THRESHOLD_CNF_V1';model['scope_sha256']=sha(out/'scope.json');save(out/'model.json',model)
        with (out/'instance.cnf').open('x',encoding='ascii',newline='\n') as f:
            f.write(f"p cnf {model['variables']} {model['clauses']}\n")
            for clause in clauses:f.write(' '.join(map(str,clause))+' 0\n')
        with (out/'model.json').open('rb') as source,(out/'model.json.gz').open('xb') as target:
            with gzip.GzipFile(filename='',mode='wb',fileobj=target,mtime=0) as packed:
                for chunk in iter(lambda:source.read(1048576),b''):packed.write(chunk)
        check=hashlib.sha256();recovered=0
        with gzip.open(out/'model.json.gz','rb') as f:
            for chunk in iter(lambda:f.read(1048576),b''):check.update(chunk);recovered+=len(chunk)
        need(check.hexdigest()==sha(out/'model.json') and recovered==(out/'model.json').stat().st_size,'lossless model recovery')
        save(out/'model_package.json',dict(raw_path=key(out/'model.json'),raw_sha256=sha(out/'model.json'),raw_bytes=recovered,gzip_path=key(out/'model.json.gz'),gzip_sha256=sha(out/'model.json.gz'),gzip_bytes=(out/'model.json.gz').stat().st_size,recovery='gzip.decompress; verify raw SHA256/length.'))
        need(time.monotonic()-start<120,'cooperative build allocation');save(out/'profile_controls.json',dict(all36_margins_checked=True,all_domain_choices_zero_Gram_checked=True,changed_profile_count_rejected=True,independent_approval=False))
        result=dict(status='CANDIDATE_SIX_PROFILE_FULL_GROUPED_GRAM_CNF_BUILT',selected_profile_id=profile['id'],selected_profile_sha256=profile['profile_sha256'],inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variables=model['variables'],clauses=model['clauses'],selectors=model['primary_selectors'],balanced_groups=14,balanced_choices_per_group=150,exceptional_groups=6,exceptional_initial_choices_per_group=[len(d['choices']) for d in domains if d['kind'].startswith('exceptional')],weighted_Gram_cells=540,weighted_threshold_channels=5400,within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,arc_pruning_used=False,orbit_coverage_used=False,elapsed_seconds=time.monotonic()-start,independent_approval=False,solver_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY',scope=scope['scope'])
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
