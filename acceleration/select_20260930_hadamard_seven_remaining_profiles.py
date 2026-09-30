"""Frozen producer selection of215 remaining literal seven-profile formulas."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
N=B/'20260930_independent_review/hadamard_seven_fibre_orbits';A=B/'20260930_independent_review/hadamard_seven_profile_arc'
PROFILES=B/'20260930_hadamard_seven_profile_local_domains/profiles.jsonl.gz'
PROOF=B/'20260930_independent_review/hadamard_seven_profile_unsat/summary.json';OMIT='rank5_07_profile_0001'
PINS={N/'summary.json':'930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f',N/'independent_orbits.json':'c6d3343b0319bf1e1971a488f5c08a3afcf50443ae01e725f951374cffffb12e',A/'summary.json':'eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d',A/'profile_outcomes.json':'0c4f8e5bc4d2b356e2894bc8de6a051c1099e0db9379b4b685df1b4da1cf9dc7',PROFILES:'88d5e572fe280a70b51e0dd2785378d73300e6873a7db788072bcbca8ef256ae',PROOF:'ff0ce1b606f0fd8c96ba4b4d892943b86abf09c9bb3c32ed3db02702a9e516a2'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def select(profiles,orbits,outcomes):
    need(len(profiles)==len(outcomes)==1608 and len(orbits)==268,'frozen populations');seen=set();survivors=[]
    for i,(p,o) in enumerate(zip(profiles,outcomes,strict=True)):need(o['index']==i and o['id']==p['id'],'literal outcome identity')
    for orbit in orbits:
        members=orbit['members'];need(len(members)==len(set(members))==6 and not seen.intersection(members),'disjoint six-member orbits');seen.update(members)
        ids=[profiles[i]['id'] for i in members];rep=min(ids);idx=members[ids.index(rep)]
        need(rep==orbit['representative_id'] and idx==orbit['representative_index'] and ids==orbit['member_ids'],'literal representative/member map')
        flags={outcomes[i]['combined_empty'] for i in members};need(len(flags)==1 and orbit['Gram_caps_empty']==next(iter(flags)),'independent AC covariance')
        if not next(iter(flags)):
            p=profiles[idx];need(len(p['group_ids'])==7,'seven exceptional groups');sizes=[r['count'] for r in p['local_domains']];s=13*150+sum(sizes)
            survivors.append(dict(profile_id=rep,profile_index=idx,profile_sha256=p['profile_sha256'],groups=p['group_ids'],orbit_members=members,orbit_member_ids=ids,initial_domains=p['local_domains'],initial_domain_sizes=sizes,expected_selectors=s,expected_variables=2*s+5380,expected_clauses=49*s+60400))
    need(seen==set(range(1608)),'whole orbit population');survivors.sort(key=lambda r:r['profile_id']);need(len(survivors)==216 and sum(r['profile_id']==OMIT for r in survivors)==1,'exact216 plus one omitted')
    remaining=[r for r in survivors if r['profile_id']!=OMIT];need(len(remaining)==215,'exact215');return survivors,remaining
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        for p,h in PINS.items():need(sha(p)==h,'pin '+key(p))
        normal,arc,proof=read(N/'summary.json'),read(A/'summary.json'),read(PROOF)
        need(normal['status']=='INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_FIBRE_NORMALIZATION_PASS' and arc['status']=='INDEPENDENT_SEVEN_EXCEPTION_PROFILE_ARC_SCREEN_PASS','independent gates')
        need(normal['outputs_sha256'][key(N/'independent_orbits.json')]==PINS[N/'independent_orbits.json'] and arc['outputs_sha256'][key(A/'profile_outcomes.json')]==PINS[A/'profile_outcomes.json'] and normal['inputs_sha256'][key(PROFILES)]==PINS[PROFILES],'gate-to-raw binding')
        need(proof['status']=='INDEPENDENT_FIXED_HADAMARD_SEVEN_PROFILE0001_UNSAT_PASS' and proof['claim_id']=='C-FIXED-HADAMARD-SEVEN-EXCEPTION-PROFILE0001-EXCLUSION' and proof['proof']['complete_independent_replay'],'previous literal excluded')
        with gzip.open(PROFILES,'rt',encoding='utf8') as f:profiles=[json.loads(line) for line in f]
        orbits=read(N/'independent_orbits.json')['orbits'];outcomes=read(A/'profile_outcomes.json')['records'];allreps,remaining=select(profiles,orbits,outcomes);rejected=[]
        for name in ['duplicate_member','wrong_representative','classification_mismatch']:
            oo,rr=deepcopy(orbits),deepcopy(outcomes)
            if name=='duplicate_member':oo[0]['members'][1]=oo[0]['members'][0]
            elif name=='wrong_representative':oo[0]['representative_id']='missing'
            else:rr[oo[0]['members'][0]]['combined_empty']=not rr[oo[0]['members'][0]]['combined_empty']
            try:select(profiles,oo,rr)
            except ValueError:rejected.append(name)
            else:raise ValueError('accepted corrupt selection '+name)
        inputs={key(p):h for p,h in PINS.items()}
        for r in allreps:
            for ref in r['initial_domains']:need(sha(ROOT/ref['path'])==ref['sha256'],'complete initial domain identity');inputs[ref['path']]=ref['sha256']
        for p in [Path(__file__),Path(__file__).with_name('select_20260930_hadamard_seven_remaining_profiles_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,wave=24,solver_calls=0))
        selection=dict(schema='REMAINING215_SEVEN_EXCEPTION_PROFILE_SELECTION_V1',inputs_sha256=inputs,all_surviving_representatives=allreps,remaining_records=remaining,remaining_profile_ids=[r['profile_id'] for r in remaining],omitted_previously_proved_profile=OMIT,omission_reason='Exact literal independent complete proof already passed; no other formula is skipped.',prior_proof_summary_path=key(PROOF),prior_proof_summary_sha256=PINS[PROOF],AC_pruning_of_local_domains=False,solver_calls=0,wave=24)
        save(out/'selection.json',selection);save(out/'controls.json',dict(valid_orbit_profiles=1608,valid_surviving_orbits=216,rejected_controls=rejected))
        summary=dict(status='CANDIDATE_REMAINING215_PROFILE_SELECTION_FROZEN',selection_path=key(out/'selection.json'),selection_sha256=sha(out/'selection.json'),inputs_sha256=inputs,all_surviving_representatives=216,previously_proved_omitted=1,selected_profiles=215,remaining_profile_ids=selection['remaining_profile_ids'],independent_approval=False,native_solver_calls=0,target_resolution=False,wave=24)
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],selection_sha256=sha(out/'selection.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
