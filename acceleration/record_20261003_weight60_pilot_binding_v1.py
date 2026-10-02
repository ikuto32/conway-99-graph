"""Bind the exact independently checked weight60 pilot saved-object scope only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261003_independent_review/weight60_pilot01'
REPORT=BASE/'summary.json'
REPORT_SHA='a80ec86298ce13ae8fea44c118ebbe613dd4b55e4387ac49e39ec9b3d4cd40d2'
CAL=ROOT/'acceleration/results/20261003_independent_review/weight60_saved_calibration03/summary.json'
CAL_SHA='660e4c420fa7f3f35f8c7291a4100931a7881237f0112c42428d6df9fa1baa07'
SUP=ROOT/'acceleration/results/20261003_independent_review/weight60_pilot_supervisor01'


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def need(value,message):
    if not value:raise ValueError(message)


def main():
    need(sha(REPORT)==REPORT_SHA and sha(CAL)==CAL_SHA,'Frozen report/calibration')
    report=json.loads(REPORT.read_bytes());calibration=json.loads(CAL.read_bytes());receipt=json.loads((SUP/'summary.json').read_bytes())
    need(report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS','Independent complete checker PASS')
    need((report['saved_main_steps'],report['saved_state_files'],report['complete_integer_saved_current_best_objects'])==(101,103,206),'Exact saved population')
    need(report['full_anchored_proposals']==2147 and report['unanchored_records']==900 and report['sparse_records']==3047,'Exact sparse replay scope')
    need(report['target_zero_candidates']==0 and not report['first_selection_earliest_full_trajectory'],'No target or earliest-history promotion')
    need(receipt['command_exit_code']==0 and receipt['cleanup']['reaped']and receipt['cleanup']['job_active_zero_observed'],'Actual stopped contained independent checker')
    for name in ['final_current_diagnostics','final_best_diagnostics']:
        result=report[name];need(result['domain_valid']and not result['srg_valid']and(result['lambda_energy'],result['mu_energy'],result['weighted_energy'],result['identity_mismatches'])==(0,3608,3608,4934),'Exact partial final graph scope')
    need(report['first_lambda0_step']==29380701 and report['first_graph_diagnostics']['mu_energy']==4936,'Retained selectedsnapshot scope')
    files={**report['inputs_sha256'],**calibration['inputs_sha256']}
    files.update({(BASE/name).relative_to(ROOT).as_posix():expected for name,expected in report['outputs_sha256'].items()})
    files.update({(CAL.parent/name).relative_to(ROOT).as_posix():expected for name,expected in calibration['outputs_sha256'].items()})
    for path in [REPORT,CAL,SUP/'manifest.json',SUP/'summary.json',SUP/'progress.jsonl',Path(__file__)]:files[path.relative_to(ROOT).as_posix()]=sha(path)
    for path,expected in files.items():need(sha(ROOT/path)==expected,'Complete immutable raw/source/receipt closure '+path)
    helpers=['acceleration/audit_20261002_weight60_scalar_v1.py','acceleration/audit_20261002_hypergraph_controls_v2.py','acceleration/audit_20261002_hypergraph_weighted_controls_v1.py']
    now=datetime.now(timezone.utc).isoformat()
    binding=dict(id='C-HYPERGRAPH-WEIGHT60-V2-PILOT01-SAVED-OBJECTS',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For the one frozen seed99032060 fixed-objective F60=60E_lambda+E_mu pilot recorded as100,000,000 proposals, a separate implementation completely checked all103 saved state files and206 current/best whole-graph objects, the three raw99x99 matrices, all saved CN/component caches and immutable retained snapshot. The final current and best99-vertex14-regular point-line graphs have E_lambda=0, E_mu=3608 and F60=ordinaryE=3608: every one of693 edges has exactly one common neighbor, but4934 ordered entries fail the exact target SRG identity. The retained reported lambda0 snapshot records step29,380,701 and E_mu4936; its integrity is checked while earliest selection over the whole sparse-history trajectory remains UNKNOWN. Of3047 saved sparse records,2147 proposals receive complete anchored graph/RNG/rollback replay and900 records remain unanchored for full graph/history checks.',scope=dict(description='Exactly the frozen pilot01 saved artifacts and complete scalar graph checks; recorded100million-step metadata is not a complete trajectory replay. No global best, performance guarantee, exhaustive coverage or target resolution.',unrestricted_target=False,target_resolution='NONE'),assumptions=['Exact saved producer source/configuration/binary/plan/native and outer receipts/source-commit closure are pinned below.','E_lambda and E_mu are exact sums of squared common-neighbor residuals over unordered edge/nonedge pairs; F60=60E_lambda+E_mu and ordinaryE=E_lambda+E_mu are distinct objectives.','Every actual saved graph has99vertices and fourteen neighbors per vertex; generic controls are not target graphs.','Sparse selected trace gaps do not establish all intermediate graphs, the full native counters by independent replay, or earliest lambda0 over the whole trajectory.'],dependencies=[dict(id='C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Exact changed-source finite engineering controls and separately calibrated saved-object checker; no old weight6 execution approval transfer.')],created_at=now,updated_at=now,producer='/root/native_driver',verifier='/root/structural',method='independent_artifact_check',verification_timestamp=report['timestamp'],source_commit=report['source_commit'],command=report['command'],cwd=report['cwd'],tool_versions=report['tool_versions'],report=REPORT.relative_to(ROOT).as_posix(),report_sha256=REPORT_SHA,calibration=CAL.relative_to(ROOT).as_posix(),calibration_sha256=CAL_SHA,inputs_sha256=files,shared_components=[path+' SHA256 '+files[path]for path in helpers]+['Pinned standard-library integer scalar row-column multiplication checks all9801 entries per saved graph; producer incremental caches are not used for these scalar products.','Shared historical independent RNG/error/matrix and weight6 reader code is disclosed by its exact pins; native producer source is authenticated but not imported.'],saved_population=dict(raw_state_files=103,distinct_main_saved_steps=101,current_best_object_checks=206,object_unit='Saved object checks including duplicates; no unique-graph census claimed.',raw_complete_matrices=3,sparse_records=3047,complete_anchored_proposals=2147,unanchored_records=900),mathematical_scope=dict(final_current=report['final_current_diagnostics'],final_best=report['final_best_diagnostics'],retained_first=report['first_graph_diagnostics'],retained_first_reported_step=29380701,earliest_lambda0_full_trajectory='UNKNOWN',target_srg_graph=False,unrestricted_exclusions=0),execution_record=dict(native_reported_counters=report['native_observed_counters'],counter_basis='Recorded native/saved-state consistency only; not a complete independent100million-proposal replay.',independent_checker_elapsed_seconds=report['elapsed_seconds'],outer_elapsed_seconds=receipt['elapsed_seconds'],outer_cleanup=receipt['cleanup']),limitations=['The final nonedge CN histogram includes counts0,1,3,4,5,6, so this partial lambda1 graph is not srg(99,14,1,2).','No graph search coverage denominator, general performance, ergodicity, or global optimality is established.','No comparison of F60 with other objective versions is asserted.','Snapshot integrity does not prove the earliest full-history lambda0 event through unobserved gaps.','This checker does not prove all100million proposal transitions or validate producer cumulative counters by a full replay.','No target graph, nonexistence proof, peer review or external acceptance is claimed.'],availability='LOCAL_ONLY',retrieval='All raw saved states/matrices/source/control/calibration/native/outer/checker receipts are present at the exact bound repository paths. Public replay availability follows repository publication separately.',writer_source_sha256=sha(Path(__file__)),writer_command=[sys.executable,*sys.argv],ledger_mutations=0)
    path=BASE/'claim_binding.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    with (BASE/'binding_identity.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(dict(binding_sha256=sha(path),report_sha256=REPORT_SHA),stream,indent=2);stream.write('\n')


if __name__=='__main__':main()
