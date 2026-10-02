"""Bind completed independent warm saved-object report; no new graph checks."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261003_independent_review/weight60_warm01'
REPORT=BASE/'summary.json'
CAL=ROOT/'acceleration/results/20261003_independent_review/weight60_saved_calibration03/summary.json'
CAL_SHA='660e4c420fa7f3f35f8c7291a4100931a7881237f0112c42428d6df9fa1baa07'
SUP=ROOT/'acceleration/results/20261003_independent_review/weight60_warm_supervisor01'
RESET=ROOT/'acceleration/results/20261003_independent_review/weight60_reset_full01/summary.json'
RESET_SHA='23917a9077bbce46c0c1222403852cbf40925cf2749f333b0fd74e04bac45d21'
RESET_DRAFT=ROOT/'acceleration/results/20261003_weight60_reset_binding01/claim_binding_schema2_draft.json'
DRAFT_SHA='24bda9181cef4d872db8d1bb5e309b4c101cf9ce0b5489fc77faf730ddcab501'


def digest(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    need(digest(CAL)==CAL_SHA and digest(RESET)==RESET_SHA and digest(RESET_DRAFT)==DRAFT_SHA,'Exact unchanged pre-output calibration and separately accepted ROOT reset report/draft')
    report=json.loads(REPORT.read_bytes());cal=json.loads(CAL.read_bytes());reset=json.loads(RESET.read_bytes());receipt=json.loads((SUP/'summary.json').read_bytes())
    need(report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS'and report['verifier']=='/root/structural'and report['producer']=='/root/native_driver','Actual separate implementation endpoint check')
    need((report['saved_main_steps'],report['saved_state_files'],report['complete_integer_saved_current_best_objects'],report['sparse_records'],report['full_anchored_proposals'],report['unanchored_records'])==(101,103,206,3047,2147,900),'Exact tested populations')
    need(receipt['command_exit_code']==0 and receipt['cleanup']['reaped']and receipt['cleanup']['job_active_zero_observed'],'Actual completed contained checker')
    for name in ['final_current_diagnostics','final_best_diagnostics']:
        d=report[name];need(d['domain_valid']and not d['srg_valid']and(d['lambda_energy'],d['mu_energy'],d['weighted_energy'],d['identity_mismatches'])==(0,3480,3480,4764),'Exact checked final partial graph')
    need(report['first_lambda0_step']==0 and report['first_graph_diagnostics']['mu_energy']==3608 and report['first_graph_diagnostics']['lambda_energy']==0 and report['target_zero_candidates']==0,'Exact checked starting snapshot and no target zero')
    need(reset['status']=='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_V1_PASS','Separate ROOT exact reset verification reused')
    files={**report['inputs_sha256'],**cal['inputs_sha256'],**reset['inputs_sha256']}
    for folder,record in [(BASE,report),(CAL.parent,cal)]:
        for name,expected in record['outputs_sha256'].items():files[(folder/name).relative_to(ROOT).as_posix()]=expected
    extra=[REPORT,CAL,RESET,RESET_DRAFT,SUP/'manifest.json',SUP/'summary.json',SUP/'progress.jsonl',Path(__file__),ROOT/'acceleration/results/20261003_weight60_warm_freeze01/plan.json',ROOT/'acceleration/results/20261003_hypergraph_weight60_warm01/candidate_identity_record.json']
    for path in extra:files[path.relative_to(ROOT).as_posix()]=digest(path)
    for name,expected in files.items():need(digest(ROOT/name)==expected,'Exact independent report/raw/source/receipt closure '+name)
    now=datetime.now(timezone.utc).isoformat();helpers=['acceleration/audit_20261002_weight60_scalar_v1.py','acceleration/audit_20261002_hypergraph_controls_v2.py','acceleration/audit_20261002_hypergraph_weighted_controls_v1.py']
    binding=dict(
        id='C-HYPERGRAPH-WEIGHT60-V2-WARM01-SAVED-OBJECTS',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',
        statement='For one frozen same-V2 weight60 warm experiment at seed99032061, recorded as100,000,000 proposals with80,000,000-proposal cooling from8 to0.1 followed by20,000,000 cold proposals, a separate checking implementation completely validated103 saved state files,206 current/best99-vertex graph objects, the three raw99x99 matrices, exact saved caches/components/RNG/configuration and immutable retained snapshot. Final current and best14-regular point-line graphs have E_lambda=0,E_mu=3480,F60=ordinaryE=3480, exactly128 lower than the checked new step-zero lambda0 baseline3608. All693edges have one common neighbor, but4764ordered entries fail the target identity. The retained snapshot is exactly the independently checked reset state at newstep0 withmu3608; old pilot step29380701 is source provenance only. Of3047sparse records,2147proposals have full anchored graph/RNG/rollback replay and900remain unanchored; no complete transition history or global earliest selection is certified.',
        scope=dict(description='Only the one frozen warm01 saved artifacts and exact scalar checks with a directly checked starting/final objective comparison. Recorded proposal counters and schedule do not certify a complete trajectory, general improvement guarantee, global best, exhaustive coverage or target solution.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['All source/binary/configuration/reset/plan/native/outer/checker receipts and raw graph artifacts are pinned below.','E_lambda and E_mu are exact unordered pair squared common-neighbor residuals; F60=60E_lambda+E_mu and ordinaryE=E_lambda+E_mu. Both compared baseline/final objects haveE_lambda0, so their3480/3608 scores are comparable.','ROOT separately checked the graph-only reset; this audit directly verifies byte-identical native initial input and every saved graph.','The old RNG trajectory is not continued: the selected labelled graph is reused with newseed61/counters0/schedule and firstsnapshot0.','Sparse trace gaps do not establish all intermediate graphs or producer cumulative counters by complete replay.'],
        dependencies=[dict(id='C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Pinned unchanged native engine and independently calibrated saved-object checker.'),dict(id='C-HYPERGRAPH-WEIGHT60-V2-GRAPH-ONLY-SEED61-RESET',revision=1,relation='verification_dependency',reason='Exact ROOT reset report23917 establishes the new ordered initial graph/RNG/configuration/counters; draft ID must be registered/reviewed by ROOT with this binding before ledger ingestion.')],
        created_at=now,updated_at=now,producer='/root/native_driver',verifier='/root/structural',method='independent_artifact_check',verification_timestamp=report['timestamp'],source_commit=report['source_commit'],command=report['command'],cwd=report['cwd'],tool_versions=report['tool_versions'],
        report=REPORT.relative_to(ROOT).as_posix(),report_sha256=digest(REPORT),calibration=CAL.relative_to(ROOT).as_posix(),calibration_sha256=CAL_SHA,inputs_sha256=files,
        shared_components=[name+' SHA256 '+files[name]for name in helpers]+['Exact standard-library row-column integer multiplication checks every9801entry square; producer incremental CN caches are not used for these scalar products.','Shared independent RNG/state/weight6-reader helpers are pinned; native producer code is authenticated but not imported.','ROOT reset checker/source/calibration are reused as separately checked provenance/configuration evidence, not rediscovered by the saved-object checker.'],
        saved_population=dict(raw_state_files=103,distinct_main_saved_steps=101,current_best_object_checks=206,object_unit='Saved object checks including duplicates; not a unique graph census.',raw_complete_matrices=3,sparse_records=3047,complete_anchored_proposals=2147,unanchored_records=900),
        mathematical_scope=dict(final_current=report['final_current_diagnostics'],final_best=report['final_best_diagnostics'],retained_initial=report['first_graph_diagnostics'],retained_initial_step=0,source_pilot_first_step=29380701,source_pilot_first_role='Provenance only; not the new trajectory first-snapshot step.',exact_mu_reduction=128,full_trajectory_checked=False,global_earliest_selection='UNKNOWN',target_srg_graph=False,unrestricted_exclusions=0),
        execution_record=dict(native_reported_counters=report['native_observed_counters'],counter_basis='Recorded native/saved-state consistency only; not full100million-transition replay.',independent_checker_elapsed_seconds=report['elapsed_seconds'],outer_checker_elapsed_seconds=receipt['elapsed_seconds'],outer_checker_cleanup=receipt['cleanup']),
        limitations=['The final nonedge CN histogram includes0,1,3,4,5, so the lambda1 partial graph is not srg(99,14,1,2).','No complete-history/counter replay, global optimality, ergodicity or performance guarantee is established.','No new mathematical validation occurs in this metadata writer; report scope is unchanged, pending ROOT statement/registration review.','The reset ID/binding is a reviewed draft reference pending authoritative ROOT registration; this writer changes no ledger.','No target graph, nonexistence proof, peer review, external acceptance or validated target-wide coverage denominator is claimed.'],
        availability='LOCAL_ONLY',retrieval='All exact raw states/matrices/source/calibrations/reset and actual scientific/checker receipts are at the bound repository paths; public availability is recorded separately upon publication.',metadata_only=True,writer_source_sha256=digest(Path(__file__)),writer_command=[sys.executable,*sys.argv],ledger_mutations=0)
    path=BASE/'claim_binding.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    with(BASE/'binding_identity.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(dict(binding_sha256=digest(path),report_sha256=digest(REPORT),metadata_only=True),stream,indent=2);stream.write('\n')


if __name__=='__main__':main()
