"""One-shot wave22 checkpoint/report derived from frozen ledger and run records."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'twentysecond_'+s+'_registration' for s in ('local_domains','encoding_and_seven','six_pairs_and_orbits','fifteen_proofs','four_union')]
def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with (ROOT/p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']};ids=[cid for d in REG for cid in read(d+'/summary.json')['new_claim_ids']]
    claims=[next(c for c in ledger['claims'] if c['id']==cid) for cid in ids];counts=Counter(c['status'] for c in ledger['claims'])
    assert len(ledger['claims'])==216 and len(ids)==len(set(ids))==10 and counts=={'VERIFIED':213,'CANDIDATE':2,'REFUTED':1}
    assert all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    assert (ROOT/REG[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    paths=dict(proofs=I+'hadamard_fifteen_profile_unsat_v2/summary.json',union=I+'hadamard_four_profile_union/summary.json',six=I+'hadamard_six_profile_arc_v3/summary.json',orbits=I+'hadamard_six_fibre_orbits/summary.json',seven=I+'hadamard_seven_exception_census/summary.json',marginals=I+'hadamard_seven_rank5_profiles/summary.json',transport=I+'hadamard_four_profile_proof_transport/summary.json',native=B+'hadamard_four_profile_native_campaign/summary.json',preparation=B+'twentysecond_preparation/summary.json')
    records={name:read(p) for name,p in paths.items()};proof=records['proofs'];union=records['union'];six=records['six'];orbit=records['orbits'];seven=records['seven'];marg=records['marginals'];native=records['native']
    assert proof['completed_proof_replays']==15 and proof['proof_bytes']==149571922 and proof['UNKNOWN']==proof['SAT']==0
    assert union['profile_population']==108 and union['local_exclusions']==12 and union['proof_orbit_members']==96 and union['proof_representatives']==16 and union['missing_profiles']==union['duplicate_coverage']==0
    assert six['profiles']==984 and six['combined_empty_profiles']==654 and six['nonempty_profiles']==330 and orbit['recorded_nonempty_orbits']==55
    assert seven['subset_population']==77520 and seven['remaining_necessary_subsets']==200 and marg['complete_cases']==200 and len(marg['positive_cases'])==38 and marg['labelled_feasible_marginal_profiles']==1608
    assert native['completed_attempts']==15 and native['unattempted_cases']==[] and native['stop_reason']=='ALL_SELECTED_CASES_ATTEMPTED'
    assert records['preparation']['status']=='TWENTYSECOND_PREPARATION_CLOSURE_PASS'
    evidence=set(paths.values())|{artifacts[a]['path'] for c in claims for a in c['evidence']}|{d+'/summary.json' for d in REG}|{B+'resume/twentysecond_raw_recovery.json',B+'resume/twentyfirst_publication_observation.json'}
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();snapshot=B+'resume/claims_at_twentysecond_milestone.yaml';checkpoint=B+'resume/twentysecond_milestone_checkpoint.json';report='docs/RESEARCH_20260930_TWENTYSECOND_WAVE.md'
    for p in (snapshot,checkpoint,report):assert not (ROOT/p).exists()
    command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat();proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED' if proc.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if proc.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    for channel,data in (('stdout',proc.stdout),('stderr',proc.stderr)):
        with (ROOT/(B+'resume/twentysecond_process_snapshot.'+channel+'.log')).open('xb') as f:f.write(data)
    with (ROOT/snapshot).open('xb') as f:f.write(raw)
    next_action='Independently gate and evaluate the remaining54 six-exception full-Gram profile representatives, preserving each complete outcome and proof; treat the separately checked first literal profile in the next milestone.'
    checkpoint_record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),writer_sha256=h('acceleration/record_20260930_twentysecond_checkpoint.py'),previous_report='docs/RESEARCH_20260930_TWENTYFIRST_WAVE.md',previous_checkpoint_sha256=h(B+'resume/twentyfirst_milestone_checkpoint.json'),claim_population=216,verified_clear=213,candidate_clear=2,refuted_clear=1,claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),new_verified_ids=ids,evidence_only_revision_changes=[],target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists.',necessary_unbalanced_counts=dict(at_least=6,scope='Literal fixed support, prescribed full integer Gram and all outside-column overlap caps.'),four_profile_union={k:union[k] for k in ('profile_population','local_exclusions','proof_representatives','proof_orbit_members','duplicate_coverage','missing_profiles')},native_batch=dict(selected=15,attempted=15,completed=15,SAT=0,UNSAT=15,UNKNOWN=0,complete_independent_proof_replays=15,proof_bytes=proof['proof_bytes'],wrapped_solver_wall_seconds=native['wrapped_solver_wall_seconds'],end_to_end_wall_seconds=native['end_to_end_wall_seconds'],scope='Fifteen literal fixed-support profile formulas; cross-group caps and residualD omitted.'),six_profile_screen=dict(labelled_profiles=984,relations=six['relations'],distinct_option_pairs=six['distinct_option_pairs'],checked_deletions=six['checked_deletions'],checked_surviving_supports=six['checked_surviving_supports'],Gram_pair_empty_profiles=six['Gram_pair_empty_profiles'],combined_empty_profiles=654,nonempty_profiles=330,all_profile_orbits=164,recorded_nonempty_orbits=55,scope='Both variants start with within-group cap-filtered domains. Nonempty AC outcomes are not joint/full-factor feasibility.'),seven_profile_screen=dict(subsets=77520,rank_counts=seven['rank_counts'],retained_kernel_subsets=200,marginal_empty_subsets=len(marg['zero_cases']),marginal_nonempty_subsets=38,labelled_marginal_profiles=1608,full_sequences=marg['complete_profile_sequences'],saved_layers=marg['saved_layers_checked'],saved_state_witnesses=marg['saved_state_witnesses_checked'],scope='Necessary integer/count relaxation only; positive counts do not establish local triples or factors.'),new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=h(snapshot),evidence_sha256={p:h(p) for p in sorted(evidence)},next_experiment=next_action,later_cohort='Six-profile literal CNF/native pilot, remaining54 preparation and all-triple descent are outside this frozen wave22 milestone.',execution=dict(observed_at=observed,command=command,exit_code=proc.returncode,state=state,stdout_sha256=h(B+'resume/twentysecond_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/twentysecond_process_snapshot.stderr.log'),scope='Fresh targeted CaDiCaL observation only; other process states UNKNOWN.'))
    save(checkpoint,checkpoint_record)
    table='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text=f'''# Twenty-second resumed milestone, 2026-09-30 JST

Ten independently checked claims were added since the [twenty-first milestone](RESEARCH_20260930_TWENTYFIRST_WAVE.md). Complete proofs and an exact coverage audit exclude the exactly-four-unbalanced family on one literal support. Together with prior results, any factor in this fixed-support Gram-plus-column-cap family must have at least six unbalanced groups. Conway-99 remains unresolved.

**As of:** {now}; source commit {source}. [Checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}); previous report: twenty-first milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; PR3 remains draft and unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** all fifteen selected formulas were independently reconstructed, attempted once and proved UNSAT. All 149,571,922 complete proof bytes were independently replayed. The union audit checks exactly 108 necessary profiles: 12 local exclusions and 96 disjoint members of 16 proof-excluded representative orbits, with no missing or multiply covered profile. The prior case0 proof supplies the sixteenth representative. No target automorphism is assumed.

For six exceptions, all 984 labelled profiles have nonempty individual local domains. Independent checking reconstructed all 12,648 relations over 12,846,624 option pairs, replayed 208,608 deletions and checked 815,040 surviving supports. The first pair relation empties 582 profiles; adding cross-group caps empties 654, including the 582, leaving 330 nonempty fixed points in 55 relabelling classes. Both stages start with within-group cap-filtered domains. The counts are overlapping stages, not additive coverage.

For seven exceptions, all 77,520 group subsets were checked. Necessary kernel conditions leave 200; complete marginal enumeration excludes 162 and leaves 38 with 1,608 labelled profiles. The independent path checked every one of 154,214 full sequences, 2,400 saved layers and 101,146 state witnesses. Positive marginal counts and AC fixed points do not establish full factors.

**Coverage:** zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains 216 claims: 213 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR. Registry totals are not a measure of Conway-99 solved.

**Best result:** a verified lower bound of six unbalanced groups, conditional on this one fixed support, its prescribed full integer Gram and outside-column overlap caps. No complete factor or target graph was produced in this milestone.

**Problems:** two AC checker metadata assumptions and the first fifteen-proof wrapper's manifest-field assumption were corrected in new versions; original failures remain. Recovery-helper v1 also stopped before writes on a manifest-field mismatch and is preserved. None changed producer evidence or thresholds. The fifteen raw models and proofs retain LOCAL_ONLY raw paths with public lossless recovery; the historical checker executable remains LOCAL_ONLY with public source/build provenance. Four older missing traces and earlier privacy omissions remain unchanged.

**Execution:** the fifteen native calls and complete proof replays finished. Targeted observation at {observed}: {state}. The aggregate wrapped-solver time was {native['wrapped_solver_wall_seconds']:.3f} seconds, versus {native['end_to_end_wall_seconds']:.3f} seconds end to end; these are one campaign's measurements. Later six-profile work and the all-triple heuristic are outside this frozen report.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}twentysecond_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTYSECOND_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT/report).open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claim_population=216,verified_clear=213,execution=state)))
if __name__=='__main__':main()
