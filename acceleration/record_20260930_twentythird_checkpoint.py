"""One-shot wave23 checkpoint/report derived from frozen ledger and verified runs."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, subprocess, sys, yaml
ROOT=Path(__file__).resolve().parents[1]; B='acceleration/results/20260930_'; I=B+'independent_review/'
REG=[B+'twentythird_'+s+'_registration' for s in ('base_results','fiftyfour_proofs','seven_and_coordinates','six_union','seven_normalization')]
GATES={
 'proofs':('hadamard_fiftyfour_profile_proofs','01cfb489e617f16f9c1773e7f10a579de018d87af39738427f52352593d53ee0'),
 'union':('hadamard_six_profile_union','6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df'),
 'seven':('hadamard_seven_profile_arc','eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d'),
 'orbits':('hadamard_seven_fibre_orbits','930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f'),
 'eight':('hadamard_eight_exception_census','95176ae42241c3745fe1e017fbeca3798b04bc49f1113455605c3ed928e204f6'),
 'coordinates':('coordinate_marginal_domains','9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39'),
 'descent':('hadamard_all_triple_descent','d16968f418a7fac753d20941e33571378054d3493a2f845b65019bf41107d36d'),
 'transport':('hadamard_fiftyfour_proof_transport','84d033953ecd02215e4f090a1386bbb577a3bbe5f1be93044d782ca355059553')}
def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with (ROOT/p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();assert hashlib.sha256(raw).hexdigest()=='58c016225a6d55933f6db7b99eb729c32b379dac034e04e79657001eee51714b'
    ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[cid for d in REG for cid in read(d+'/summary.json')['new_claim_ids']]
    claims=[next(c for c in ledger['claims'] if c['id']==cid) for cid in ids];counts=Counter(c['status'] for c in ledger['claims'])
    assert len(ledger['claims'])==229 and len(ids)==len(set(ids))==13 and counts=={'VERIFIED':226,'CANDIDATE':2,'REFUTED':1}
    assert all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    assert (ROOT/REG[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    paths={k:I+d+'/summary.json' for k,(d,_) in GATES.items()}
    for k,(_,pin) in GATES.items():assert h(paths[k])==pin
    paths.update(native=B+'hadamard_six_profile_batch_campaign/summary.json',preparation=B+'twentythird_preparation/summary.json',raw_recovery=B+'resume/twentythird_raw_recovery.json')
    records={k:read(p) for k,p in paths.items()};proof=records['proofs'];union=records['union'];seven=records['seven'];orbit=records['orbits'];eight=records['eight'];coord=records['coordinates'];descent=records['descent'];native=records['native']
    assert proof['completed_proof_replays']==54 and proof['proof_bytes']==555334934 and proof['UNKNOWN']==proof['SAT_pending_separate_review']==0
    assert union['profile_population']==984 and union['AC_exclusions']==654 and union['proof_orbit_members']==330 and union['proof_representatives']==55 and union['missing_profiles']==union['duplicate_coverage']==0
    assert union['authenticated_complete_proof_bytes']==563744101
    assert seven['profiles']==1608 and seven['combined_empty_profiles']==312 and seven['nonempty_profiles']==1296 and orbit['orbits']==268 and orbit['combined_nonempty_orbits']==216
    assert eight['population']==125970 and eight['retained']==4184
    assert coord['coordinates']==12 and coord['full_bounded_vectors_checked']==12582912 and coord['integer_vectors']==291 and coord['ordered_fibre_profiles']==2226
    assert descent['checked_checkpoints']==408 and descent['checked_logged_updates']==8000 and descent['minimum_logged_score']==296
    assert native['completed_attempts']==54 and native['unattempted_profiles']==[] and native['stop_reason']=='ALL_SELECTED_PROFILES_ATTEMPTED'
    assert records['preparation']['status']=='TWENTYTHIRD_PREPARATION_CLOSURE_PASS'
    assert records['raw_recovery']['models']==55 and records['raw_recovery']['proofs']==54 and len(records['raw_recovery']['records'])==109 and all(r['action']=='RESTORED_MISSING' for r in records['raw_recovery']['records'])
    evidence=set(paths.values())|{artifacts[a]['path'] for c in claims for a in c['evidence']}|{d+'/summary.json' for d in REG}|{B+'resume/twentysecond_publication_observation.json'}
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();snapshot=B+'resume/claims_at_twentythird_milestone.yaml';checkpoint=B+'resume/twentythird_milestone_checkpoint.json';report='docs/RESEARCH_20260930_TWENTYTHIRD_WAVE.md'
    for p in (snapshot,checkpoint,report):assert not (ROOT/p).exists()
    command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat();proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED' if proc.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if proc.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    for channel,data in (('stdout',proc.stdout),('stderr',proc.stderr)):
        with (ROOT/(B+'resume/twentythird_process_snapshot.'+channel+'.log')).open('xb') as f:f.write(data)
    with (ROOT/snapshot).open('xb') as f:f.write(raw)
    next_action='Build and independently audit the exact joint coordinate/local-signature count model with a separately authenticated at-least-seven-unbalanced-group extension; use it to test necessary count feasibility beyond fixed exception lists.'
    checkpoint_record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),writer_sha256=h('acceleration/record_20260930_twentythird_checkpoint.py'),previous_report='docs/RESEARCH_20260930_TWENTYSECOND_WAVE.md',previous_checkpoint_sha256=h(B+'resume/twentysecond_milestone_checkpoint.json'),claim_population=229,verified_clear=226,candidate_clear=2,refuted_clear=1,claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),new_verified_ids=ids,evidence_only_revision_changes=[],target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists.',necessary_unbalanced_counts=dict(at_least=7,scope='Literal fixed support, prescribed full integer Gram and all outside-column overlap caps.'),six_profile_union={k:union[k] for k in ('profile_population','AC_exclusions','proof_representatives','proof_orbit_members','duplicate_coverage','missing_profiles','authenticated_complete_proof_bytes')},native_batch=dict(selected=54,attempted=54,completed=54,SAT=0,UNSAT=54,UNKNOWN=0,complete_independent_proof_replays=54,proof_bytes=proof['proof_bytes'],wrapped_solver_wall_seconds=native['wrapped_solver_wall_seconds'],end_to_end_wall_seconds=native['end_to_end_wall_seconds'],scope='54 literal fixed-support profile formulas; cross-group caps and residualD omitted.'),separate_literal_pilot=dict(selected=1,attempted=1,completed=1,UNSAT=1,complete_independent_proof_replays=1,proof_bytes=8409167),seven_profile_screen=dict(labelled_profiles=seven['profiles'],relations=seven['relations'],distinct_option_pairs=seven['distinct_option_pairs'],checked_deletions=seven['checked_deletions'],checked_surviving_supports=seven['checked_surviving_supports'],Gram_pair_empty_profiles=seven['Gram_pair_empty_profiles'],combined_empty_profiles=seven['combined_empty_profiles'],nonempty_profiles=seven['nonempty_profiles'],all_profile_orbits=orbit['orbits'],combined_empty_orbits=orbit['combined_empty_orbits'],combined_nonempty_orbits=orbit['combined_nonempty_orbits'],scope='Both predicates start with within-group cap-filtered domains. Nonempty outcomes are not joint/full-factor feasibility.'),eight_subset_screen=dict(subsets=eight['population'],rank_counts=eight['rank_counts'],class_counts=eight['class_counts'],retained_kernel_subsets=eight['retained'],scope='Necessary prescribed-Gram integer-count conditions only.'),coordinate_domains={k:coord[k] for k in ('coordinates','full_bounded_vectors_checked','integer_vectors','ordered_pairs','ordered_fibre_profiles','scope')},saved_descent={k:descent[k] for k in ('checked_checkpoints','checked_checkpoint_objects','checked_logged_updates','minimum_logged_score','objective_version','minimum_candidate_evaluations_verified','intermediate_rng_replay','scope')},raw_recovery=dict(models=55,proofs=54,originals=109,restored_to_fresh_tree=109,identity_only=True),new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=h(snapshot),evidence_sha256={p:h(p) for p in sorted(evidence)},next_experiment=next_action,later_cohort='Joint count-master preflight, formula construction and all later native evaluations are outside this frozen wave23 milestone.',execution=dict(observed_at=observed,command=command,exit_code=proc.returncode,state=state,stdout_sha256=h(B+'resume/twentythird_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/twentythird_process_snapshot.stderr.log'),scope='Fresh targeted CaDiCaL observation only; other process states UNKNOWN.'))
    save(checkpoint,checkpoint_record)
    table='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text=f'''# Twenty-third resumed milestone, 2026-09-30 JST

Thirteen independently checked claims were added since the [twenty-second milestone](RESEARCH_20260930_TWENTYSECOND_WAVE.md). Complete proof replay and a disjoint coverage audit exclude exactly six unbalanced groups on one literal support. Together with prior exclusions, a factor in this fixed-support Gram-plus-column-cap family needs at least seven unbalanced groups. Conway-99 remains unresolved.

**As of:** {now}; source commit {source}. [Checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}); previous report: twenty-second milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; PR3 remains draft and unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** all 54 newly selected formulas were independently reconstructed, attempted once and proved UNSAT. All 555,334,934 complete proof bytes were independently replayed. The separate literal pilot adds one checked proof of 8,409,167 bytes. The exact union covers 984 necessary profiles: 654 pair-screen exclusions and 330 disjoint images of 55 proof-excluded representatives, with no missing or multiply covered profile. No target automorphism is assumed.

For seven exceptions, every one of 1,608 profiles has nonempty individual local domains. Independent checking reconstructed all 24,732 relations over 37,784,232 option pairs, replayed 351,630 deletions and checked 3,487,644 surviving supports. The first pair predicate empties 276 profiles; adding cross-group caps empties 312, including those 276, leaving 1,296 nonempty fixed points. Both start with within-group cap-filtered domains. Complete relabelling verification gives 268 six-member orbits, of which 52 are excluded and 216 remain unresolved. These overlapping stages are not additive coverage.

For eight exceptions, all 125,970 subsets were checked; necessary kernel conditions retain 4,184. A separate coordinate-domain audit directly checked all 12,582,912 bounded vectors across twelve coordinates, confirming 291 integer vectors and 2,226 ordered three-fibre profiles. These are necessary domains, without established cross-coordinate or full-factor feasibility.

Four all-triple descent chains completed 8,000 updates. Independent review checked 408 checkpoints and all logged score transitions. The smallest saved full squared Frobenius Gram error is exactly 296, with 37 outside-column cap violations, under objective FIXED_L_FULL_GRAM_FROBENIUS_SQUARED_V1. This objective is lower-is-better on the fixed-support local-triple domain and is not comparable with earlier cross-Gram permutation scores. Review did not establish move optimality or replay all intermediate random choices. No factor or exclusion follows from this experiment.

**Coverage:** zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains 229 claims: 226 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR. Registry totals are not a measure of Conway-99 solved.

**Best result:** a verified lower bound of seven unbalanced groups, conditional on this one fixed support, its prescribed full integer Gram and all outside-column overlap caps. No complete factor or target graph was produced.

**Problems:** seven-profile AC v1 refused its allocation before screening; separately preregistered v2 raised the memory limit from 512MiB to 768MiB. Its first invocation reached its 180-second limit before classifying any profiles, then an explicit authenticated resume completed all cases. Both records and the allocation deviation remain. All 55 raw models and 54 campaign proofs retain LOCAL_ONLY original paths with lossless public recovery; a fresh-tree test restored all 109. The historical checker executable remains LOCAL_ONLY with public source/build provenance. Four older missing traces and prior privacy omissions remain unchanged.

**Execution:** the 54-call campaign, separate literal pilot and complete proof replays finished. Targeted observation at {observed}: {state}. The campaign took {native['wrapped_solver_wall_seconds']:.3f} wrapped-solver seconds and {native['end_to_end_wall_seconds']:.3f} seconds end to end; these are one campaign's measurements. Later joint count-master work is outside this frozen report.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}twentythird_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTYTHIRD_WAVE_V2.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT/report).open('x',encoding='utf8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claim_population=229,verified_clear=226,execution=state)))
if __name__=='__main__':main()
