"""Freeze wave21 verified results before the separate fifteen-case campaign."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'twentyfirst_'+s+'_registration'for s in['structural','normalization','joint_and_five','six_and_case0','proof_and_marginals']]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[cid for d in REG for cid in read(d+'/summary.json')['new_claim_ids']]
    claims=[next(c for c in ledger['claims']if c['id']==cid)for cid in ids]
    assert len(ids)==len(set(ids))==12 and len(ledger['claims'])==206
    assert all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'and c['revision']==1 for c in claims)
    assert(ROOT/REG[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    counts=Counter(c['status']for c in ledger['claims']);assert counts=={'VERIFIED':203,'CANDIDATE':2,'REFUTED':1}
    proofpath=I+'hadamard_case0_profile_unsat/summary.json';proof=read(proofpath)
    jointpath=I+'four_group_joint_v2/summary.json';joint=read(jointpath)
    sixpath=I+'hadamard_six_rank4_profiles/summary.json';six=read(sixpath)
    evidence={artifacts[a]['path']for c in claims for a in c['evidence']}
    evidence.update([proofpath,jointpath,sixpath,I+'case0_model_transport/summary.json',B+'twentyfirst_packaging_preparation/summary.json',B+'resume/twentyfirst_model_recovery.json'])
    evidence.update(d+'/summary.json'for d in REG)
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    snapshot=B+'resume/claims_at_twentyfirst_milestone.yaml';checkpoint=B+'resume/twentyfirst_milestone_checkpoint.json';report='docs/RESEARCH_20260930_TWENTYFIRST_WAVE.md'
    for p in[snapshot,checkpoint,report]:assert not(ROOT/p).exists()
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15)
    state='CADICAL_PROCESS_OBSERVED'if proc.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if proc.returncode==1 else'UNKNOWN_OBSERVATION_ERROR'
    for channel,content in[('stdout',proc.stdout),('stderr',proc.stderr)]:
        with(ROOT/(B+'resume/twentyfirst_process_snapshot.'+channel+'.log')).open('xb')as f:f.write(content)
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    next_action='Independently gate and run the fifteen remaining full-Gram four-exception profile representatives, one attempt per formula; preserve and independently check every outcome and complete proof.'
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_TWENTIETH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/twentieth_milestone_checkpoint.json'),
      claim_population=206,verified_clear=203,candidate_clear=2,refuted_clear=1,claim_status_counts=dict(counts),claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),new_verified_ids=ids,evidence_only_revision_changes=[],
      target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target resolution artifact exists.',
      necessary_unbalanced_counts=dict(at_least=4,exactly_five_excluded=True,scope='Literal fixed support and prescribed Gram only.'),
      four_group_screen=dict(global_quartets=4845,necessary_quartets=14,labelled_profiles=108,locally_excluded_profiles=12,nonempty_AC_profiles=96,fibre_orbits=18,nonempty_fibre_orbits=16,scope='Exactly four exceptional groups, prescribed Gram plus column caps.'),
      partial_enumeration=dict(selected_profiles=96,complete_profiles=35,partial_profiles=1,unattempted_profiles=60,checked_intervals=1263,checked_tuples=7335060,raw_witnesses=36,independent_gate=jointpath),
      first_residual_psd=dict(rank=29,nullity=7,remaining_columns_constructed=0,scope='One exact saved twelve-column partial object.'),
      six_group_screen=dict(subsets=38760,rank_counts={'6':35587,'5':3164,'4':9},retained_rank4_subsets=9,independently_enumerated_coordinate_sequences=121869,DP_layers=108,excluded_rank4_cases=[2,6,7],remaining_group_subsets=6,labelled_marginal_profiles=984,scope='Full-Gram necessary marginals only; no quadratic Gram or Y-cap feasibility.'),
      case0_native=dict(attempted=1,completed=1,outcome='UNSAT',variables=10564,clauses=187408,conflicts=12232,native_wall_seconds=1.82,native_cpu_seconds=1.08,complete_independent_proof_replay=True,proof_bytes=9139513,proof_sha256='01ee3198778714f32bf0e7e0c4a89ab3d29ecceb088ccf392ee0e2749418d07d',independent_gate=proofpath,scope='Literal case0 profile with within-group caps; cross-group caps and D omitted.'),
      new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,
      coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=h(snapshot),evidence_sha256={p:h(p)for p in sorted(evidence)},next_experiment=next_action,
      later_cohort='The remaining15 encodings/native campaign, six-profile local-domain filter and coordinate-input relabelling diagnostic belong to wave22.',
      execution=dict(observed_at=observed,command=command,exit_code=proc.returncode,state=state,stdout_sha256=h(B+'resume/twentyfirst_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/twentyfirst_process_snapshot.stderr.log'),scope='Fresh targeted native census; completed wave21 runs separate from later preparation.'))
    save(checkpoint,record)
    table='\n'.join('| '+c['id']+' r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    text=f'''# Twenty-first resumed milestone, 2026-09-30 JST

Twelve independently checked claims were added since the [twentieth milestone](RESEARCH_20260930_TWENTIETH_WAVE.md). The fixed support requires at least four unbalanced groups and forbids exactly five. One exactly-four profile is excluded by a complete proof; six-group marginal screening leaves six group subsets with984 labelled marginal profiles. No full factor or target resolution follows.

**As of:** {now}; source commit {source}. [Checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}); previous report: twentieth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** all4,845 group quartets were checked. Fourteen necessary quartets yield108 labelled profiles; the complete local-cap screen excludes12 and leaves96 nonempty pairwise fixed points. Global fibre relabelling gives18 size-six orbits,16 with nonempty screens, without assuming any target automorphism.

The bounded joint search completed35 profiles and one partial prefix, leaving60 unattempted. Independent checking reconstructed every one of7,335,060 saved tuples over1,263 intervals and all36 first raw witnesses. The first residual Gram is exactly PSD with rank29/nullity7. None supplies the remaining48 columns.

All38,760 six-group subsets were checked:35,587 have rank6,3,164 rank5 and nine rank4. Exact integer marginal arguments exclude the rank5/6 cases. Direct independent enumeration of121,869 coordinate-profile sequences checks all108 DP layers and excludes three rank4 cases, leaving six with984 labelled marginal profiles. Marginal feasibility does not establish quadratic Gram feasibility.

The single native case0 attempt used10,564 variables and187,408 clauses and returned UNSAT after12,232 conflicts,1.82 native wall seconds and1.08 CPU seconds. Its complete9,139,513-byte trace was independently replayed against the exact CNF. This is a literal-profile exclusion, with within-group caps and no cross-group cap or residualD encoding. Any relabelled transfer uses the separately checked normalization.

**Coverage:** zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The frozen ledger has206 claims:203 VERIFIED/CLEAR,2 CANDIDATE/CLEAR and1 REFUTED/CLEAR. Counts of profiles, subsets and partial objects are different populations and are not summed.

**Best result:** exact scoped nonexistence results for small unbalanced-group counts and one full-Gram profile, with complete proof and finite certificates. The unrestricted target remains open in this repository.

**Problems:** the first joint enumerator's positive control used the research diagonal cap instead of the243-fixture diagonal. It failed before research enumeration; the corrected version and original failure are preserved. The120-second enumeration checkpoint is deliberately incomplete. The large raw case0 model remains LOCAL_ONLY at its raw path with public lossless recovery; the original checker executable is also LOCAL_ONLY with public source/build provenance. Earlier missing traces and private-process omissions remain unchanged.

**Execution:** the case0 native call and proof replay completed. Targeted census at {observed}: {state}. The fifteen-case campaign is outside this checkpoint; no continuing solver execution is implied.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}twentyfirst_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTYFIRST_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with(ROOT/report).open('x',encoding='utf8',newline='\n')as f:f.write(text)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claim_population=206,verified_clear=203,execution=state)))
if __name__=='__main__':main()

