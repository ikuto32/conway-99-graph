"""Freeze reviewed claims and completed finite phase work, not later cohorts."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
REG=[B+'nineteenth_'+s+'_registration' for s in ['selected_lift','general_phase','premise_collection','matrix_form','phase_batch','case01']]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[cid for directory in REG for cid in read(directory+'/summary.json')['new_claim_ids']]
    claims=[c for cid in ids for c in ledger['claims'] if c['id']==cid]
    assert len(ids)==len(set(ids))==len(claims)==10 and len(ledger['claims'])==188
    assert all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' and c['revision']==1 for c in claims)
    assert (ROOT/REG[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    batch_path=I+'hadamard_parity_phase_batch_outcome/summary.json';enum_path=I+'hadamard_phase_case01_enumeration/summary.json'
    batch=read(batch_path);enumeration=read(enum_path)
    assert batch['status']=='INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OUTCOME_PASS'
    assert enumeration['status']=='INDEPENDENT_HADAMARD_CASE01_COMPLETE_PHASE_ENUMERATION_PASS'
    evidence={artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    evidence.update([batch_path,enum_path,I+'hadamard_general_f3_phase_necessity/unsearched_cnf_execution_decision.json',B+'nineteenth_packaging_preparation/summary.json'])
    evidence.update(d+'/summary.json' for d in REG)
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    snapshot=B+'resume/claims_at_nineteenth_milestone.yaml';checkpoint=B+'resume/nineteenth_milestone_checkpoint.json'
    report='docs/RESEARCH_20260930_NINETEENTH_WAVE.md'
    for p in [snapshot,checkpoint,report]:assert not(ROOT/p).exists()
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();process=subprocess.run(command,cwd=ROOT,capture_output=True)
    state='CADICAL_PROCESS_OBSERVED' if process.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    for channel,content in [('stdout',process.stdout),('stderr',process.stderr)]:
        with(ROOT/(B+'resume/nineteenth_process_snapshot.'+channel+'.log')).open('xb')as f:f.write(content)
    with(ROOT/snapshot).open('xb')as f:f.write(raw)
    statuses=Counter(c['status'] for c in ledger['claims']);reviews=Counter(c['review_state'] for c in ledger['claims'])
    verified=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']);assert verified==186
    next_action='Independently audit and then run the grouped full balanced-Gram encoding on this fixed support, covering constant and mixed local groups together; test any decoded factor against exact Gram and outside-column conditions before residual completion.'
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_EIGHTEENTH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/eighteenth_milestone_checkpoint.json'),
        claim_population=len(ledger['claims']),verified_clear=verified,candidate_clear=2,claim_status_counts=dict(statuses),claim_review_counts=dict(reviews),new_verified_ids=ids,evidence_only_revision_changes=[],
        target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target resolution artifact exists.',
        batch_counts=batch['counts'],batch_elapsed_seconds=batch['batch_elapsed_seconds'],enumeration=dict(frozen_universe=2187,completed_vectors=2187,local_survivors=0,first_failure_counts={'mixed_phase_distinctness':1611,'constant_phase_multiplicity':576},independent_gate=enum_path),
        new_exact_selected_parity_exclusions=4,reduction_orders=12,distinct_overlapping_reduced_exclusions=11,minimum_recorded_fixed_patterns=14,union_cardinality=None,union_cardinality_null_reason='No checked union calculation.',
        new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,
        missing_batch_trace_files=4,missing_trace_scope='Three SAT learned traces and one UNKNOWN partial trace. Historical identities retained. No mathematical claim uses these traces as proof.',
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=h(snapshot),evidence_sha256={p:h(p) for p in sorted(evidence)},next_experiment=next_action,
        later_cohort='Oriented-triple encoding/native pilot, signed-graph diagnostic and full balanced-Gram source preparation are outside this frozen wave; their saved records govern their status.',
        execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,stdout_sha256=h(B+'resume/nineteenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/nineteenth_process_snapshot.stderr.log'),scope='Fresh native census only; completed four-attempt batch is separate from later-cohort preparation.'))
    save(checkpoint,record)
    table='\n'.join('| `'+c['id']+'` r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text=f'''# Nineteenth resumed milestone, 2026-09-30 JST

Ten independently checked claims were added since the [eighteenth milestone](RESEARCH_20260930_EIGHTEENTH_WAVE.md). Exact phase arguments exclude four specified balanced parity assignments and give eleven overlapping exclusions that leave some groups free. No full factor or target graph was found.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{checkpoint}), [frozen ledger](../{snapshot}); previous report: eighteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
{table}

**Work completed:** the second parity assignment's 240-variable rational lift has a checked uniform primal, but exact GF(3) phase equations forbid its integer coloring lift. A general balanced-phase necessity theorem and a matrix formulation were independently derived. The all-mixed signed-Gram identity does not establish universal phase rank.

One greedy premise reduction keeps fourteen of twenty patterns fixed. Twelve recorded reduction orders produce eleven distinct overlapping clauses, with fourteen to seventeen fixed patterns. No global minimum or union size is established.

The finite sampler attempted four native calls: three distinct SAT projections were completely checked, followed by one UNKNOWN outcome at the conflict setting. Two projections have literal phase contradiction certificates. The third has rank113/nullity7 and no individually vanishing mixed difference. Independent enumeration of all2,187 vectors then rejects every vector:1,611 first fail mixed-group distinctness and576 first fail constant-group multiplicity. No research vector reaches the pair, full-Gram or outside-cap stages. The earlier linear-screen and projection claims remain valid within their narrower scopes.

**Coverage:** the four newly excluded complete assignments are distinct; the reduced pattern families overlap and are not added as disjoint graph counts. Zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger has188 claims:186 VERIFIED/CLEAR and two CANDIDATE/CLEAR. These are claim counts, not a fraction of Conway99 solved.

**Best result:** exact independently checkable phase exclusions, including one exhaustive seven-dimensional finite phase universe and reductions fixing as few as fourteen local patterns. Balance and the single six-prism support remain extra restrictions. No comparable target-wide bound follows.

**Problems:** the fourth native attempt was UNKNOWN. All four deferred batch traces are now MISSING despite successful historical stat/hash receipts; the later failed archive and independent availability observations are preserved. Their loss cause is UNKNOWN. No UNSAT proof or mathematical exclusion depends on those traces. The matrix checker first used an incorrect metadata key, and the finite enumerator had two setup failures before evaluating any vectors. All original sources/failures and corrected versions remain available. The prepared second-branch lift CNF was cancelled before solving after the exact phase obstruction.

**Execution:** all four batch attempts and all finite enumerations completed. Native census at {observed}: `{state}`. The later oriented-triple pilot and grouped full-Gram formulation belong to the next cohort. No ongoing solver work is implied by this report.

**Next experiment:** {next_action}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}nineteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_NINETEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with(ROOT/report).open('x',encoding='utf8',newline='\n')as f:f.write(text)
    print(json.dumps(dict(checkpoint=checkpoint,sha256=h(checkpoint),claim_population=188,verified_clear=186,execution=state)))
if __name__=='__main__':main()
