"""Bind independently completed finite weight60 V2 audit; no ledger mutation."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT='acceleration/results/20261002_independent_review/weight60_controls01/summary.json'
REPORT_SHA='05a8c1e5b0d2df3d937cd1ab47961b17ff37ec2f3d9952a5db0feaf5178ac9f3'
CAL='acceleration/results/20261002_independent_review/weight60_scalar_calibration01/summary.json'
CAL_SHA='a0a7d9f59528e4b44954ff3ba2fff9e7930dc6a010517516e1a68b3f30429815'
ID='C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS'


def sha(name):
    with(ROOT/name).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA and sha(CAL)==CAL_SHA
    report=json.loads((ROOT/REPORT).read_bytes());cal=json.loads((ROOT/CAL).read_bytes())
    assert report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS'and cal['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SCALAR_V1_CALIBRATION_PASS'
    wanted=dict(native_calls_observed=57,successful_calls_completely_replayed=29,strict_negative_calls_checked=28,full_proposals=20992,all_saved_intermediate_checkpoints=328,pair_table_records=2494,overlap_valid=1303,overlap_accepted=592,overlap_rejected=711)
    assert all(report[k]==v for k,v in wanted.items())
    pins={**report['inputs_sha256'],**cal['inputs_sha256'],REPORT:REPORT_SHA,CAL:CAL_SHA}
    detail='acceleration/results/20261002_independent_review/weight60_controls01/checked_controls.json';pins[detail]=report['outputs_sha256']['checked_controls.json']
    caldetail='acceleration/results/20261002_independent_review/weight60_scalar_calibration01/checked_controls.json';pins[caldetail]=sha(caldetail)
    for directory in['acceleration/results/20261002_independent_review/weight60_controls_supervisor01','acceleration/results/20261002_independent_review/weight60_scalar_calibration_supervisor01']:
        for suffix in['manifest.json','summary.json']:pins[directory+'/'+suffix]=sha(directory+'/'+suffix)
    failed='acceleration/results/20261002_hypergraph_weight60_controls01/failure.json';pins[failed]=sha(failed)
    manifest=json.loads((ROOT/'acceleration/results/20261002_hypergraph_weight60_controls02/controls_manifest.json').read_bytes());assert pins[failed]==manifest['prior_failed_version']['sha256']
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__).relative_to(ROOT).as_posix())
    for name,digest in pins.items():assert sha(name)==digest,name
    outer_name='acceleration/results/20261002_independent_review/weight60_controls_supervisor01/summary.json';outer=json.loads((ROOT/outer_name).read_bytes())
    assert outer['command_exit_code']==0 and outer['cleanup']['reaped']and outer['cleanup']['job_active_zero_observed']
    now=datetime.now(timezone.utc).isoformat()
    binding=dict(id=ID,revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',
      statement='For exactly the57 frozen fixed-weight60 exclusive-selected-point swap engineV2 engineering calls, a separate implementation checked29 complete successful paths and28 designated malformed-input rejections; all20,992proposals,328saved intermediate states,2,494integer pair-cost records,complete current/best/first rawgraphs and CN/component caches,graph-domain preservation,RNG/schedule/acceptance and rejected-trade rollback,oldweight6 graph-selector imports with new counters/config/RNG,and five whole256 versus split73+183 rawstate/firstsnapshot/matrix/trace identities. The1,303valid overlapping-triple proposals include592accepted and711rejected cases. Complete finite traces establish the first observed current E_lambda0 selection and exact retained snapshot independently of bestF60 on these paths, under the recorded1e-12 temperature tolerance and strictly separated probabilistic decisions.',
      scope=dict(description='Exactly57 finite ENGINEERING native calls and raw artifacts for the declared99/9/12point domains; complete finite replay only. No general trajectory, ergodicity, performance, scientific-pilot outcome, graph existence or unrestricted exclusion is claimed.',unrestricted_target=False,target_resolution='NONE'),
      assumptions=['Exact frozen source/spec/config/binary/build/rawcontrols and supported command/cleanup receipts identified in inputs_sha256.','The fixed objective is F60=60E_lambda+E_mu; current/best records and ordinaryE remain different metrics.','Complete graph construction/full pair-count/category rescoring is independent of producer incremental8toggle caches; prior independent RNG/error/matrix and weight6 parser bytes are disclosed.','Recorded heuristic temperatures use absolute tolerance1e-12 and required acceptance separation>1e-12; actual minimum0.0002820146563534687.','Generic9/12point controls, including cube12E_lambda0/E_mu48, are never99target certificates.'],
      dependencies=[dict(id='C-HYPERGRAPH-WEIGHTED-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Pinned separately checked prior weight6 reader/raw import identities only; its old execution gate does not approve changedweight60V2.'),dict(id='C-HYPERGRAPH-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Earlier independent RNG/error/matrix checking methods are reused with exact source pins; no old execution approval transfer.')],
      created_at=now,updated_at=now,producer='/root/native_driver',verifier='/root/structural',method='independent_artifact_check',verification_timestamp=report['timestamp'],source_commit=report['source_commit'],producer_source_commit=report['producer_source_commit'],command=report['command'],cwd=report['cwd'],python=report['tool_versions']['python'],report=REPORT,report_sha256=REPORT_SHA,inputs_sha256=pins,shared_components=report['shared_components'],
      verification=dict(bound_claim_id=ID,bound_claim_revision=1,outcome='PASS',method='independent_artifact_check',exact_raw_artifacts='Complete immutable report hash mapping and checked_controls.json.',counts=wanted,complete_finite_trajectory_paths=29,whole_split_families=5,independent_positive_and_corrupted_controls=True,minimum_acceptance_margin=report['minimum_acceptance_margin']),
      pre_output_calibration=dict(path=CAL,sha256=CAL_SHA,scope='Different-author scorer/state/overlap/firststep/matrix controls before full57finite replay; no scientific output checked.',control_count=cal['controls']),
      execution=dict(verifier_seconds=report['elapsed_seconds'],supervisor_seconds=outer['elapsed_seconds'],observed_exit_code=0,reaped=True,empty_windows_job_observed=True,currently_running=False),
      historical_failure=dict(path=failed,sha256=pins[failed],statement='Frozen old disjoint-kernelV1 controls failed a predeclared late-lambda0 prism fixture after25positive calls;27negative calls were unattempted. The oldsource/rawreceipts remain preserved.',scope='Engineering control failure only; no broad dualgraph catalogue/class-invariance diagnosis is approved by this binding.'),
      artifacts=[dict(path=name,sha256=digest,availability='LOCAL_ONLY',retrieval='Existing shared checkout; publication closure is separate and pending.')for name,digest in pins.items()],artifact_availability='LOCAL_ONLY',artifact_availability_reason='No fresh publication replay was performed by this verifier.',
      limitations=['Finite calibration does not prove general trajectory correctness, ergodicity, throughput or search-space coverage.','Earliestfirstlambda0 is checked only over the complete finite control paths; sparse scientific gaps requireUNKNOWN history.','Native compiler is authenticated by source/binary/build hash and receipt, not independently rebuilt.','Producer cubic dualgraph diagnosis enumeration is preserved/hashbound but not independently exhaustively checked here.','No full scientific trajectory, pilot outcome, target graph/nonexistence proof, novelty or external peerreview claim.'],external_review=None,external_review_null_reason='Internal independent finite artifact checking only.',overall_search_coverage='UNKNOWN; no validated denominator.')
    p=ROOT/'acceleration/results/20261002_independent_review/weight60_controls01/claim_binding.json'
    with p.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(id=ID,revision=1,path=p.relative_to(ROOT).as_posix(),sha256=sha(p.relative_to(ROOT).as_posix()))))


if __name__=='__main__':main()
