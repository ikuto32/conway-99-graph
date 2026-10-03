"""Producer immutable remaining54 literal-profile selection; no solve."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
NORMAL=B/'20260930_independent_review/hadamard_six_fibre_orbits/summary.json';ARC=B/'20260930_independent_review/hadamard_six_profile_arc_v3/summary.json'
OUTCOMES=ARC.with_name('profile_outcomes.json');ORBITS=B/'20260930_hadamard_six_fibre_orbits/orbits.json';PROFILES=B/'20260930_hadamard_six_profile_local_domains/profiles.jsonl.gz'
PRIOR=B/'20260930_hadamard_six_profile_native_pilot/summary.json';OMIT='rank4_00_profile_0000'
PINS={NORMAL:'ea4289a741ed19231d88fec5d917428b3ffc2c497a116268c90344448b665109',ARC:'82be6d4389596959365d5551694f3e1361d0bc855405f2647a682784be1f34ba',OUTCOMES:'d3c49cfb080aa5a39beebdd7f39688fd2891288f2d1a79acbd44f83377334202',ORBITS:'f95592f6d31a9685367e1509eedb95417300a3304bae9acad754eae19f19fbce',PROFILES:'221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0',PRIOR:'598ed32fb7ef52554a94f088bde63406fa456f687a0060a1acd3af9c7105ae67'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def select(profiles,orbits,outcomes):
    need(len(profiles)==984 and len(outcomes)==984 and len(orbits)==164,'frozen finite populations');seen=set();survivors=[]
    for i,(p,o) in enumerate(zip(profiles,outcomes)):need(o['index']==i and o['id']==p['id'],'raw/audited profile identity')
    for orbit in orbits:
        members=orbit['members'];need(len(members)==6 and len(set(members))==6 and not seen.intersection(members),'disjoint size6 orbit');seen.update(members)
        ids=[profiles[i]['id'] for i in members];rep=min(ids);index=next(i for i in members if profiles[i]['id']==rep);need(rep==orbit['representative_id'] and index==orbit['representative_index'],'lexicographic representative')
        flags={outcomes[i]['combined_empty'] for i in members};need(len(flags)==1 and orbit['Gram_caps_empty']==next(iter(flags)),'independent classification covariance')
        if not next(iter(flags)):
            p=profiles[index];sizes=[r['count'] for r in p['local_domains']];s=14*150+sum(sizes);survivors.append(dict(profile_id=rep,profile_index=index,profile_sha256=p['profile_sha256'],groups=p['group_ids'],orbit_members=members,orbit_member_ids=ids,initial_domains=p['local_domains'],initial_domain_sizes=sizes,expected_selectors=s,expected_variables=2*s+5380,expected_clauses=49*s+60400))
    need(seen==set(range(984)),'complete orbit partition');survivors.sort(key=lambda r:r['profile_id']);need(len(survivors)==55 and sum(r['profile_id']==OMIT for r in survivors)==1,'all55 include exactly prior profile')
    remaining=[r for r in survivors if r['profile_id']!=OMIT];need(len(remaining)==54 and len({r['profile_id'] for r in remaining})==54,'exact remaining54');return survivors,remaining
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        for path,h in PINS.items():need(sha(path)==h,'input pin '+key(path))
        normal=read(NORMAL);arc=read(ARC);need(normal['status']=='INDEPENDENT_HADAMARD_SIX_EXCEPTION_FIBRE_NORMALIZATION_PASS' and arc['status']=='INDEPENDENT_SIX_EXCEPTION_PROFILE_ARC_SCREEN_PASS','independent gate statuses')
        for path in (ORBITS,PROFILES):need(normal['inputs_sha256'][key(path)]==PINS[path],'normalization exact raw input binding')
        need(arc['outputs_sha256'][key(OUTCOMES)]==PINS[OUTCOMES],'independent AC output binding')
        with gzip.open(PROFILES,'rt',encoding='utf-8') as f:profiles=[json.loads(line) for line in f]
        orbits=read(ORBITS)['orbits'];outcomes=read(OUTCOMES)['records'];all55,remaining=select(profiles,orbits,outcomes);rejected=[]
        for name in ('duplicate_member','wrong_representative','classification_mismatch'):
            bad_orbits=copy.deepcopy(orbits);bad_outcomes=copy.deepcopy(outcomes)
            if name=='duplicate_member':bad_orbits[0]['members'][1]=bad_orbits[0]['members'][0]
            elif name=='wrong_representative':bad_orbits[0]['representative_id']='not_a_profile'
            else:bad_outcomes[orbits[0]['members'][0]]['combined_empty']=not bad_outcomes[orbits[0]['members'][0]]['combined_empty']
            try:select(profiles,bad_orbits,bad_outcomes)
            except ValueError:rejected.append(name)
            else:raise ValueError('corrupted selection accepted')
        inputs={key(p):h for p,h in PINS.items()}
        for r in all55:
            for ref in r['initial_domains']:need(sha(ROOT/ref['path'])==ref['sha256'],'full initial domain identity');inputs[ref['path']]=ref['sha256']
        for p in (Path(__file__),Path(__file__).with_name('select_20260930_hadamard_six_remaining_profiles_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml'):inputs[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,wave=23,solver_calls=0))
        selection=dict(schema='REMAINING54_SIX_EXCEPTION_PROFILE_SELECTION_V1',inputs_sha256=inputs,all_surviving_representatives=all55,remaining_records=remaining,remaining_profile_ids=[r['profile_id'] for r in remaining],omitted_previously_attempted_profile=OMIT,omission_reason='Already built and natively attempted; not a mathematical exclusion premise.',prior_native_summary_path=key(PRIOR),prior_native_summary_sha256=PINS[PRIOR],prior_native_proof_validity_used=False,AC_pruning_of_local_domains=False,solver_calls=0,wave=23)
        save(out/'selection.json',selection);save(out/'controls.json',dict(valid_orbit_profiles=984,valid_surviving_orbits=55,rejected_controls=rejected));summary=dict(status='CANDIDATE_REMAINING54_PROFILE_SELECTION_FROZEN',selection_path=key(out/'selection.json'),selection_sha256=sha(out/'selection.json'),inputs_sha256=inputs,all_surviving_representatives=55,previously_attempted_omitted=1,selected_profiles=54,remaining_profile_ids=selection['remaining_profile_ids'],independent_approval=False,native_solver_calls=0,target_resolution=False,wave=23);save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='inputs_sha256'}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
