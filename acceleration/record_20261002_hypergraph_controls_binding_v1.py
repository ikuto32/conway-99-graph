"""Immutable engineering claim binding; no scientific run or target approval."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/hypergraph_controls02'
REPORT=DIR+'/summary.json'
REPORT_SHA='81aa0427d80d66b45ae48d47cea98c02de02bc4ae096d5a0bcc688d6df2bacb3'


def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS' and report['target_resolution'] is False
    assert [report[k] for k in ['native_calls_observed','successful_calls_completely_replayed','rejected_corrupt_calls','full_proposals','admissible_proposals_full_rescored','all_saved_intermediate_checkpoints']]==[14,9,5,10752,5274,168]
    detail=DIR+'/checked_controls.json';assert sha(detail)==report['outputs_sha256']['checked_controls.json']
    inputs=dict(report['inputs_sha256']);inputs.update({REPORT:REPORT_SHA,detail:sha(detail)})
    now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    statement=('For the fourteen frozen hypergraph-annealer-v1 engineering calls, an independent adjacency-set implementation completely checked the nine successful raw trajectories (10,752 proposals; 5,274 admissible proposed graphs; 168 saved intermediate checkpoints), exact integer energies/deltas/common-neighbor caches/domain/counters/RNG, whole256 versus split73+183 byte and trace identity, and five native corrupted-checkpoint rejections with matching independent diagnostics, under the recorded floating heuristic tolerance and decision-margin controls.')
    binding=dict(id='C-HYPERGRAPH-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description=report['scope']+' No general trajectory, throughput, ergodicity, exhaustive coverage, or target result is asserted.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Exact frozen producer/code/environment/native binary/build, raw controls and receipt bytes identified by inputs_sha256.',
                     'Recorded finite controls only; source-free full adjacency-set rescoring and independently expanded SplitMix64/xoshiro256** arithmetic.',
                     'Floating temperature acceptance is heuristic, using absolute tolerance1e-12 and requiring every worsening probabilistic decision margin>1e-12; minimum observed margin0.0005679459568983612.'],
        dependencies=[],dependency_reason='Standalone finite engineering calibration; no mathematical graph existence, exclusion or move-space premise is used.',
        verifier=report['verifier'],producer=report['producer'],method='independent_artifact_check',created_at=now,updated_at=now,
        verification_timestamp=report['timestamp'],source_commit=report['source_commit'],producer_source_commit=report['producer_source_commit'],command=report['exact_argv'],cwd=report['working_directory'],
        python=report['tool_versions']['python'],inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,
        controls=json.loads((ROOT/detail).read_bytes())['checking_controls'],shared_components=report['shared_trusted_components'],
        statement_evidence=dict(native_calls=14,complete_successful_trajectories=9,negative_native_calls=5,full_proposals=10752,admissible_proposals_full_rescored=5274,saved_intermediate_checkpoints=168,
                               exact_negative_native_stderr_required=True,source='audit_20261002_hypergraph_controls_v2.py',detail=detail),
        limitations=report['limitations']+['A 9-vertex positive fixture is not a target99 certificate; all target99 control best energies remain strictly positive.',
                                          'The syntactic and numerical gate does not establish that all linear-hypergraph states are reachable by these trades.'],
        unknowns=dict(performance=None,performance_null_reason='No controlled throughput comparison or performance claim.',ergodicity=None,ergodicity_null_reason='Move-space connectivity not established.'),
        artifact_availability='LOCAL_ONLY',retrieval='Exact frozen workspace paths; public retrieval requires separate publication check.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Exact-r1 engineering bookkeeping only; original independent report remains unchanged.'))
    target=DIR+'/claim_binding.json'
    with (ROOT/target).open('x',encoding='utf8',newline='\n') as f:json.dump(binding,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=target,sha256=sha(target),id=binding['id'],revision=1)))


if __name__=='__main__':main()
