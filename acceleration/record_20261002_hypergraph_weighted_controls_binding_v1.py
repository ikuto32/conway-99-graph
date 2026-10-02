"""Exact-r1 immutable finite engineering claim binding for weighted controls."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/hypergraph_weighted_controls01'
REPORT=DIR+'/summary.json'
REPORT_SHA='464a90e4093194ac59c4bdba3c19da661f7eabde52806307b37dbd33a7249f57'


def sha(name):
    with (ROOT/name).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_ANNEAL_V1_CONTROLS_PASS' and report['target_resolution'] is False
    assert [report[k] for k in ['native_calls_observed','successful_calls_completely_replayed','rejected_corrupt_calls','full_proposals','admissible_proposals_full_rescored','all_saved_intermediate_checkpoints','pair_table_records']]==[32,16,16,19456,10189,304,1376]
    detail=DIR+'/checked_controls.json';assert sha(detail)==report['outputs_sha256']['checked_controls.json'];checked=json.loads((ROOT/detail).read_bytes())
    inputs=dict(report['inputs_sha256']);inputs.update({REPORT:REPORT_SHA,detail:sha(detail)});now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    statement=('For the32 frozen fixed-weight hypergraph engine v1 engineering calls with F=6E_lambda+E_mu, an independent adjacency-set implementation completely checked16 successful raw trajectories (19,456 proposed trades,10,189 admissible proposed graphs,304 saved intermediate checkpoints), exact integer weighted/base/category scores, deltas, common-neighbor caches, graph domain, counters and RNG; all1,376 pair-cost records; both complete current/best matrix exports; exact current/best v1 graph import selection/reset/new RNG; both fresh and imported whole256 versus split73+183 raw-state and trace identities; and16 native malformed-input rejections with matching independent failure stages and exact native diagnostics, under the recorded floating heuristic tolerance and margin controls.')
    binding=dict(id='C-HYPERGRAPH-WEIGHTED-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description=report['scope']+' This is finite engineering calibration only: no general trajectory, throughput, ergodicity, graph realization, exhaustive coverage or target outcome is asserted.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Exact frozen changed weighted source/code/spec/build/binary/environment, raw controls and command/cleanup receipt hashes recorded in inputs_sha256.',
            'Complete adjacency-set component rescoring and independently calibrated prior unweighted domain/RNG helpers; no weighted discovery producer imported.',
            'Heuristic temperature absolute tolerance1e-12 and strict worsening-decision margin>1e-12; minimum observed0.00011329031347125443.',
            'Native reported controls use only the declared99/9 linear-hypergraph domains; the9-vertex exact positive control is not a99-target graph.'],
        dependencies=[dict(id='C-HYPERGRAPH-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Previously independent unweighted domain/RNG helpers and exact raw v1 import object are reused; the old execution gate does not approve the changed weighted source.')],
        dependency_reason='Pinned independent prior helper/raw import calibration only; the new weighted objective/parser/complete finite trajectories are separately checked.',
        verifier=report['verifier'],producer=report['producer'],method='independent_artifact_check',created_at=now,updated_at=now,verification_timestamp=report['timestamp'],source_commit=report['source_commit'],producer_source_commit=report['producer_source_commit'],
        command=report['command'],cwd=report['cwd'],python=report['tool_versions']['python'],inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,controls=checked['checking_controls'],shared_components=report['shared_trusted_components'],
        statement_evidence=dict(native_calls=32,complete_successful_trajectories=16,negative_native_calls=16,full_proposals=19456,admissible_full_rescored=10189,saved_intermediate_checkpoints=304,pair_cost_records=1376,
             exact_negative_native_stderr_required=True,all_raw_current_best_matrices_checked=True,fresh_and_imported_complete_split_resumes=True,detail=detail),
        limitations=report['limitations'],unknowns=dict(performance=None,performance_null_reason='No controlled timing comparison or performance claim.',ergodicity=None,ergodicity_null_reason='Move-space connectivity not established.'),
        artifact_availability='LOCAL_ONLY',retrieval='Exact frozen workspace paths; immutable public retrieval requires a separate publication audit.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Exact-r1 engineering bookkeeping only; original raw controls/report bytes unchanged.'))
    target=DIR+'/claim_binding.json'
    with (ROOT/target).open('x',encoding='utf8',newline='\n') as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(path=target,sha256=sha(target),id=binding['id'],revision=1)))


if __name__=='__main__':main()
