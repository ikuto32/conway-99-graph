"""Narrow exact-r1 binding of one saved non-SRG weighted-pilot graph."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02'
REPORT=DIR+'/summary.json'
REPORT_SHA='6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0'
BASE='acceleration/results/20261002_hypergraph_weighted_pilot02'


def sha(name):
    with (ROOT/name).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(name,value):
    with (ROOT/name).open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def main():
    assert sha(REPORT)==REPORT_SHA;report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_PASS' and report['target_resolution'] is False
    assert [report[k] for k in ['saved_state_files','saved_unique_steps','complete_integer_saved_objects','sparse_selected_records','full_anchored_proposals_replayed','unreplayed_sparse_records','target_zero_candidates']]==[22,21,44,2247,2067,180,0]
    diagnostic=report['final_best_diagnostics'];assert [diagnostic[k] for k in ['weighted_energy','base_energy','lambda_energy','mu_energy','identity_mismatch_count']]==[3801,3486,63,3423,4814]
    assert diagnostic['domain_valid'] is True and diagnostic['srg_valid'] is False and diagnostic['ordered_entries_checked']==9801
    inputs=dict(report['inputs_sha256']);inputs[REPORT]=REPORT_SHA
    for name,digest in report['outputs_sha256'].items():path=DIR+'/'+name;assert sha(path)==digest;inputs[path]=digest
    best=BASE+'/native/best.adj';state=BASE+'/native/final.state';protocol_path=BASE+'/protocol.json'
    assert sha(best)==report['raw_final_matrices']['best']['sha256']==inputs[best] and sha(state)==inputs[state]
    protocol=json.loads((ROOT/protocol_path).read_bytes());source=Path(__file__).relative_to(ROOT).as_posix();now=datetime.now(timezone.utc).isoformat()
    statement=('The exact saved weightedpilot02 best.adj is a symmetric binary zero-diagonal99-vertex14-regular point graph of231linear triples with pointdegree7. Its exact fixed objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1 is F3801=6*E_lambda63+E_mu3423; its ordinary residual is E3486=63+3423. The recorded adjacent/nonadjacent common-neighbor histograms are exact, and4,814 ordered matrix entries violate the target identity. This graph is not an SRG and provides no exclusion.')
    evidence=dict(status='INDEPENDENT_WEIGHTED_PILOT02_LITERAL_BEST_OBJECT_CHECKED',timestamp=report['timestamp'],verifier=report['verifier'],producer=report['producer'],statement=statement,source_commit=report['source_commit'],producer_source_commit=protocol['source_commit'],source_configuration=protocol['options'],seed=99032023,
        inputs_sha256=inputs,raw_best_graph={'path':best,'sha256':sha(best)},raw_final_state={'path':state,'sha256':sha(state)},complete_saved_objects_report={'path':REPORT,'sha256':REPORT_SHA},exact_diagnostics=diagnostic,verified_final_matrices=report['raw_final_matrices'],
        scope='One exact saved non-SRG graph and labelled-triple representation with fixed objective/component diagnostics; no whole trajectory or performance guarantee.',target_resolution=False,new_exclusions=0,
        controls='Newv2saved-object calibration503a9a55d02823f2016e5a7053f6644f0c11d9b0981ef28368f854777a2e5d2c, complete weighted engineering464a90e4093194ac59c4bdba3c19da661f7eabde52806307b37dbd33a7249f57 and scalar matrix/adjacency-set agreement.',
        shared_components=report['shared_components'],command=report['command'],cwd=report['cwd'],creation=dict(script=source,sha256=sha(source),reason='Narrow exact saved-object evidence binding; no new scientific computation.'))
    evidence_path=DIR+'/best_object_evidence.json';save(evidence_path,evidence);inputs[evidence_path]=sha(evidence_path)
    binding=dict(id='C-HYPERGRAPH-WEIGHTED-ANNEAL-PILOT02-SAVED-BEST-OBJECT',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description=evidence['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=['Exact immutable native weightedpilot02 best matrix/final labelled-triple state and complete hash-bound independent saved-object audit.',
            'One fixed newseed99032023 imported the prior unweightedpilot01 best graph and reset counters/configuration/RNG; preserved source_configuration identifies this run.',
            'Fixed F6E_lambda+E_mu and ordinaryE are distinct objectives; F improvement does not imply ordinaryE improvement.'],
        dependencies=[dict(id='C-HYPERGRAPH-WEIGHTED-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Complete calibrated independent weighted graph/state/RNG checking helpers; sparse scientific replay is separately limited.')],
        dependency_reason='Engineering calibration supports the independent object checking path; this claim binds one exact raw graph, not the producer trajectory.',
        verifier=report['verifier'],producer=report['producer'],method='independent_artifact_check',created_at=now,updated_at=now,verification_timestamp=report['timestamp'],source_commit=report['source_commit'],producer_source_commit=protocol['source_commit'],source_configuration=protocol['options'],random_seed=99032023,
        command=report['command'],cwd=report['cwd'],inputs_sha256=inputs,report=evidence_path,report_sha256=sha(evidence_path),controls=evidence['controls'],shared_components=report['shared_components'],
        limitations=report['limitations']+['Native reported20,000,000 proposals are saved counter observations; only2,067 complete-anchor proposals of2,247selected records were independently replayed and180gaps remain unchecked.',
            'Both raw final current and best matrices are present and fully checked; the one-graph statement refers precisely to raw best.adj.',
            'Compared with the imported starting graph, exactF5169 fell to3801 while exactordinaryE3034 rose to3486; no controlled performance or target progress percentage is inferred.',
            'Failedsetup01 exited on outer manifest pin mismatch before native launch and is preserved separately; it is not a completed scientific graph evaluation.'],
        artifact_availability='LOCAL_ONLY',retrieval='Exact raw graph/finalstate and hash-bound complete independent reports at workspace paths; public availability requires a separate publication check.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Narrow exact-r1 bookkeeping only; original producer/checker/calibration bytes unchanged.'))
    target=DIR+'/claim_binding.json';save(target,binding);print(json.dumps(dict(path=target,sha256=sha(target),id=binding['id'],revision=1,evidence=evidence_path,evidence_sha256=sha(evidence_path))))


if __name__=='__main__':main()
