"""Freeze seven checked claims and completed eighteenth-cohort execution records."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
def h(p):
    with(ROOT/p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,value):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--registration',action='append',required=True);ap.add_argument('--next-experiment',required=True);args=ap.parse_args()
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw);artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[cid for directory in args.registration for cid in read(directory+'/summary.json')['new_claim_ids']]
    claims=[c for cid in ids for c in ledger['claims']if c['id']==cid]
    assert len(ids)==len(set(ids))==len(claims)==7 and len(ledger['claims'])==178
    assert all(c['revision']==1 and c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    assert(ROOT/args.registration[-1]/'CLAIMS.after.yaml').read_bytes()==raw
    mip=read(I+'hadamard_prism_binary_mip_execution/summary.json');assert mip['status'].endswith('_PASS')
    zero=read(I+'balanced_lift_zero_rows/summary.json');assert zero['status']=='INDEPENDENT_SELECTED_PARITY_LIFT_ZERO_ROW_EXCLUSION_PASS'
    sat=[]
    for name,gate in [('hadamard_balanced_parity','hadamard_balanced_parity_sat_v2'),('hadamard_parity_support_cuts','hadamard_parity_support_cuts_sat')]:
        outcome=read(B+name+'_native_pilot/summary.json');obj=read(I+gate+'/summary.json')
        assert outcome['actual_exit_code']==10 and obj['status'].endswith('_PASS')
        assert outcome['research_calls']==1 and not outcome['receipt']['outer_windows_guard_expired']
        log=(ROOT/(B+name+'_native_pilot/main/solver.stdout.log')).read_text()
        assert h(B+name+'_native_pilot/main/solver.stdout.log')==outcome['receipt']['stdout_sha256']
        counts=re.search(r'^c conflicts:\s+(\d+)',log,re.M);assert counts
        sat.append(dict(name=name,attempts=1,exit_code=10,independently_checked_projection=True,full_factor=False,
            conflicts=int(counts[1]),wrapper_wall_seconds=outcome['receipt']['wall_seconds'],object_gate=I+gate+'/summary.json',object_gate_sha256=h(I+gate+'/summary.json')))
    cancellation=read(B+'balanced_lift_lp_not_run/summary.json')
    catalog=B+'eighteenth_artifact_packaging/catalog.json';assert read(B+'eighteenth_artifact_packaging/summary.json')['status']=='EIGHTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    evidence={artifacts[aid]['path']for c in claims for aid in c['evidence']}
    evidence.update([p+'/summary.json'for p in args.registration]+[catalog,B+'eighteenth_artifact_packaging/summary.json',
        I+'hadamard_prism_binary_mip_execution/summary.json',I+'hadamard_parity_support_cuts_sat_outcome/summary.json',B+'balanced_lift_lp_not_run/summary.json'])
    snapshot=B+'resume/claims_at_eighteenth_milestone.yaml';checkpoint=B+'resume/eighteenth_milestone_checkpoint.json';report='docs/RESEARCH_20260930_EIGHTEENTH_WAVE.md'
    assert all(not(ROOT/p).exists()for p in [snapshot,checkpoint,report,B+'resume/eighteenth_process_snapshot.stdout.log',B+'resume/eighteenth_process_snapshot.stderr.log'])
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args'];observed=datetime.now(timezone.utc).isoformat()
    process=subprocess.run(command,cwd=ROOT,capture_output=True)
    state='CADICAL_PROCESS_OBSERVED'if process.returncode==0 else'NO_CADICAL_PROCESS_OBSERVED'if process.returncode==1 else'UNKNOWN_OBSERVATION_ERROR'
    for channel,content in [('stdout',process.stdout),('stderr',process.stderr)]:
        with(ROOT/(B+'resume/eighteenth_process_snapshot.'+channel+'.log')).open('xb')as stream:stream.write(content)
    with(ROOT/snapshot).open('xb')as stream:stream.write(raw)
    statuses=Counter(c['status']for c in ledger['claims']);reviews=Counter(c['review_state']for c in ledger['claims'])
    verified=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in ledger['claims']);assert verified==176
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_report='docs/RESEARCH_20260930_SEVENTEENTH_WAVE.md',
        previous_checkpoint_sha256=h(B+'resume/seventeenth_milestone_checkpoint.json'),claim_population=len(ledger['claims']),verified_clear=verified,candidate_clear=2,
        claim_status_counts=dict(statuses),claim_review_counts=dict(reviews),new_verified_ids=ids,evidence_only_revision_changes=[],
        target_resolution='UNKNOWN',external_review=None,external_review_null_reason='No target-resolution artifact exists.',
        native=dict(distinct_models=2,attempts=2,completed_attempts=2,SAT=2,UNSAT=0,UNKNOWN=0,checked_projection_objects=2,checked_full_factors=0,runs=sat),
        mip=dict(attempts=1,completed_attempts=1,UNKNOWN=1,result=mip['result'],exclusion=False),
        first_selected_lift=dict(result='EXACT_NONNEGATIVE_INFEASIBILITY',counts=zero['counts'],independent_gate=I+'balanced_lift_zero_rows/summary.json',
            zero_rows=[139,215,399,445,539,555],scope=zero['claim']['scope'],solver_calls=0),
        skipped_lp=cancellation,failed_cnf_builds=1,new_full_factors=0,complete99_graphs=0,new_selected_parity_exclusions=1,
        new_whole_support_exclusions=0,new_core_exclusions=0,new_unrestricted_exclusions=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',ledger_snapshot_sha256=h(snapshot),evidence_sha256={p:h(p)for p in sorted(evidence)},next_experiment=args.next_experiment,
        execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,stdout_sha256=h(B+'resume/eighteenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/eighteenth_process_snapshot.stderr.log'),
            scope='Both eighteenth native attempts and the MIP call completed; later selected-lift work is outside this checkpoint. No live claim about other processes.'))
    save(checkpoint,record)
    rows='\n'.join('| `'+c['id']+'` r1 | '+c['scope']['description']+' [Evidence](../'+artifacts[c['evidence'][0]]['path']+'). |'for c in claims)
    text=f'''# Eighteenth resumed milestone, 2026-09-30 JST

Seven independently checked claims were added since the [seventeenth milestone](RESEARCH_20260930_SEVENTEENTH_WAVE.md). Exact integer evidence excludes one selected balanced-parity lift. Sixty general necessary conditions reject that assignment, and a second independently checked parity assignment satisfies the strengthened formula. The separate direct MIP attempt ended UNKNOWN without a valid incumbent.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{checkpoint}), [ledger snapshot](../{snapshot}); previous report: seventeenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex graph or general nonexistence proof. No target resolution is under external review; this is not a worldwide literature verdict. Draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** two distinct parity formulas were each attempted once and each produced one completely checked projection witness. Both have 520 variables; the formulas have 4,481 and 4,541 clauses respectively. The first witness has sixteen mixed and four constant groups. The second has twenty mixed groups and sixty disagreement counts equal to three. Neither witness is a full Gram factor, cap-feasible factor or graph.

The first witness's exact lift relaxation has 312 variables and 560 equations. Six required rows have identically zero coefficients. An independent checker rebuilt all domains and coefficients and verified the literal dual with RHS product -1 and all column products zero. This excludes exactly one selected parity branch. No LP or SAT run was needed for that exclusion. The separately proved sixty necessary conditions apply to balanced factors on the same fixed support; balance remains an additional assumption.

The direct binary MIP encoding has 5,400 variables and 766 rows. Its one completed attempt reached its cooperative allocation without a valid incumbent, Gram object or lazy cut. The saved 120.25-second wrapper time explicitly exceeds the 120-second allocation by 0.25 seconds. No numerical status is a certificate or exclusion.

**Coverage:** one selected balanced-parity branch excluded; zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains {len(ledger['claims'])} claims: {verified} VERIFIED/CLEAR and two CANDIDATE/CLEAR. Counts of native SAT calls, MIP calls, failed builds and skipped LP work are separate populations.

**Best result:** an exact selected-branch obstruction, a general necessary cut for the balanced fixed-support family, and a new checked parity projection that survives all sixty cuts. No full factor or comparable target-wide bound was obtained.

**Problems:** the direct MIP run was inconclusive. The first parity object check failed on hexadecimal metadata formatting; the failed source, corrected checker, independent delta audit and new calibration are preserved. The initial selected-lift CNF build stopped at an empty-counter assertion; its partial output is retained, and the separate exact zero-row proof supplies the exclusion. The planned numerical LP was skipped before execution. The old parity witness remains valid for its original formula.

**Execution:** both cohort native attempts and the direct MIP call completed. Fresh native observation at {observed}: `{state}`. Later second-witness lift work is a separate cohort and requires its own receipts. The user's continuation instruction remains active.

**Next experiment:** {args.next_experiment}

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{catalog}), [replay guide](REPRODUCING_20260930_EIGHTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with(ROOT/report).open('x',encoding='utf8',newline='\n')as stream:stream.write(text)
    print(json.dumps(dict(claims=len(ledger['claims']),new_claims=7,verified=verified,native_SAT=2,MIP_UNKNOWN=1,target_resolution='UNKNOWN',observed_native_state=state)))
if __name__=='__main__':main()
