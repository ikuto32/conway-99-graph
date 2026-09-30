"""Freeze six independently checked claims and two completed native outcomes."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
import yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
def h(p):
    with(ROOT/p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,value):
    with(ROOT/p).open('x',encoding='utf-8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--next-experiment',required=True);args=ap.parse_args()
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']}
    registrations=[B+'seventeenth_'+name+'_registration/summary.json'for name in ['cyclic','model_projection']]
    ids=[cid for p in registrations for cid in read(p)['new_claim_ids']];claims=[c for cid in ids for c in ledger['claims']if c['id']==cid]
    assert len(ids)==len(set(ids))==len(claims)==6 and len(ledger['claims'])==171
    assert all(c['revision']==1 and c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    assert (ROOT/(B+'seventeenth_model_projection_registration/CLAIMS.after.yaml')).read_bytes()==raw
    checked=read(I+'hadamard_cyclic_unsat/summary.json');unknown=read(I+'hadamard_prism_ordered_native_outcome/summary.json')
    assert checked['native_outcome']['result']=='UNSAT' and checked['proof']['complete_independent_replay']
    assert unknown['outcome']['recorded_outcome']=='UNKNOWN_GNU_TIMEOUT_SIGTERM'and not unknown['trace']['complete_independent_UNSAT_replay']
    census=read(I+'hadamard_triplicate_counts_v2/summary.json');assert census['status']=='INDEPENDENT_HADAMARD_TRIPLICATE_PROJECTIONS_PASS'
    catalog=B+'seventeenth_artifact_packaging/catalog.json';assert read(B+'seventeenth_artifact_packaging/summary.json')['status'].endswith('_PASS')
    evidence={artifacts[aid]['path']for c in claims for aid in c['evidence']}
    evidence.update(registrations+[I+'hadamard_prism_ordered_native_outcome/summary.json',catalog,B+'seventeenth_artifact_packaging/summary.json'])
    pins={p:h(p)for p in sorted(evidence)}
    snapshot=B+'resume/claims_at_seventeenth_milestone.yaml';checkpoint=B+'resume/seventeenth_milestone_checkpoint.json';report_path='docs/RESEARCH_20260930_SEVENTEENTH_WAVE.md'
    assert all(not(ROOT/p).exists()for p in [snapshot,checkpoint,report_path,B+'resume/seventeenth_process_snapshot.stdout.log',B+'resume/seventeenth_process_snapshot.stderr.log'])
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat()
    process=subprocess.run(command,cwd=ROOT,capture_output=True)
    state='CADICAL_PROCESS_OBSERVED'if process.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if process.returncode==1 else'UNKNOWN_OBSERVATION_ERROR'
    for channel,content in [('stdout',process.stdout),('stderr',process.stderr)]:
        with(ROOT/(B+'resume/seventeenth_process_snapshot.'+channel+'.log')).open('xb')as stream:stream.write(content)
    with(ROOT/snapshot).open('xb')as stream:stream.write(raw)
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_SIXTEENTH_WAVE.md',
        previous_checkpoint_sha256=h(B+'resume/sixteenth_milestone_checkpoint.json'),claim_population=171,verified_clear=169,candidate_clear=2,
        claim_status_counts=dict(Counter(c['status']for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state']for c in ledger['claims'])),
        new_verified_ids=ids,evidence_only_revision_changes=[],target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists.',
        native=dict(distinct_models=2,attempts=2,completed_attempts=2,SAT=0,UNSAT=1,UNKNOWN=1,checked_complete_proofs=1,
            cyclic=checked['native_outcome'],cyclic_proof=checked['proof'],broader=unknown['outcome'],broader_trace=unknown['trace'],
            scope='One extra cyclic subclass excluded; broader all-colouring model of the same fixed support unresolved.'),
        projection=census['counts'],new_full_factors=0,complete99_graphs=0,new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=h(snapshot),evidence_sha256=pins,next_experiment=args.next_experiment,
        execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,
            stdout_sha256=h(B+'resume/seventeenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/seventeenth_process_snapshot.stderr.log'),
            scope='The two seventeenth native attempts are completed. Any later research is outside this checkpoint.'))
    save(checkpoint,record)
    rows='\n'.join('| `'+c['id']+'` r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    report=f'''# Seventeenth resumed milestone, 2026-09-30 JST

Six independently checked claims were added since the [sixteenth milestone](RESEARCH_20260930_SIXTEENTH_WAVE.md). A complete replayable proof excludes one cyclic coloring subclass of the remaining fixed Hadamard support. A broader model without the cyclic restriction ended UNKNOWN. Exact marginal and local-triple checks establish why the tested projections do not justify imposing that restriction.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{checkpoint}), [ledger snapshot](../{snapshot}); previous report: sixteenth milestone.

**Verdict:** target resolution UNKNOWN. No independently validated 99-vertex graph or general nonexistence proof exists in this repository. No target resolution is under external review; this is not a worldwide literature verdict. Draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** two distinct native models were each attempted once. The cyclic model has 26,360 variables and 122,394 clauses. Its UNSAT result has a 29,697,087-byte trace, independently replayed completely against the exact formula with positive and corrupted controls. The semantic reduction and every clause were checked independently. This excludes only the explicitly imposed cyclic triplet construction, not all factors on its support or core.

The broader ordered model retains all 90 coloring options for each of 60 columns before ordering, with 595,464 variables and 3,336,642 clauses. Every clause was independently checked, including the 163,800 ordering clauses and all column caps. Ordering only relabels identical-support columns; no target automorphism is assumed. Its sole attempt stopped at the 300-second wall guard with wrapper exit 124, after 525,037 conflicts. The 350,457,856-byte partial trace and execution receipts were independently checked. This UNKNOWN result excludes nothing.

The independent complete local census considers all 117,480 increasing triples from 90 balanced words. Exactly 31,110 satisfy the local Gram upper bounds and column caps; 150 have color counts (1,1,1) at all six coordinates, and 30 are cyclic. These nested populations are not added. All 12 saved marginal matrices have exact rational rank 6; their nonconstant integer witnesses have 120 separately checked local realizations. Those realizations need not agree globally. Whether full Gram feasibility forces balanced triplets remains UNKNOWN.

**Coverage:** one cyclic subclass excluded; zero new whole-support, core or unrestricted exclusions. The previous four-of-five selected support exclusions remain unchanged. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains 171 claims: 169 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** a complete exact certificate for the specified cyclic subclass, plus an independently approved broader encoding. No full 36-by-60 factor or new comparable target-wide bound was obtained.

**Problems:** the broader search timed out. The first independent projection checker used an incorrect raw field name and failed before mathematical checking; its original source and failure are preserved with the corrected independent audit. Local counterexamples refute only the stated projection-level implications. Lossless packages preserve the complete cyclic proof and large inputs; the incomplete broader trace remains LOCAL_ONLY. No numerical zero or timeout is promoted to a certificate.

**Execution:** both cohort native attempts completed. Fresh observation at {observed}: `{state}`. Exact logs are bound in the checkpoint. Later MIP or coupled-count work requires separate receipts and is outside these counts. The user's continuation instruction remains active.

**Next experiment:** {args.next_experiment}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{catalog}), [replay guide](REPRODUCING_20260930_SEVENTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with(ROOT/report_path).open('x',encoding='utf-8',newline='\n')as stream:stream.write(report)
    print(json.dumps(dict(claims=171,new_claims=6,verified=169,UNSAT=1,UNKNOWN=1,target_resolution='UNKNOWN',observed_native_state=state)))
if __name__=='__main__':main()
