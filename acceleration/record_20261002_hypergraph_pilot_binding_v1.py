"""Bind one exact non-SRG pilot graph; no trajectory/performance promotion."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/hypergraph_pilot_review01'
REVIEW=DIR+'/summary.json'
REVIEW_SHA='73b90ebea2c3685ab9f38622e37cba2349b51ba55204d39348d92434c05fcc51'
AUDIT='acceleration/results/20261002_independent_review/hypergraph_pilot01/summary.json'
AUDIT_SHA='3c640a1f7a2940d646ebd65deb0f7b84d0ad40b0bad6f923fc9127a69e35d4fa'
BASE='acceleration/results/20261002_hypergraph_pilot01'


def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def save(name,value):
    with (ROOT/name).open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')


def main():
    assert sha(REVIEW)==REVIEW_SHA and sha(AUDIT)==AUDIT_SHA
    review=json.loads((ROOT/REVIEW).read_bytes());audit=json.loads((ROOT/AUDIT).read_bytes())
    assert review['status']=='INDEPENDENT_HYPERGRAPH_PILOT01_SAVED_OBJECTS_PASS'
    assert review['exact_literal_best_diagnostics']['exact_energy']==3034 and review['target_resolution'] is False
    raw=BASE+'/native/best.adj';final=BASE+'/native/final.state';protocol=BASE+'/protocol.json'
    assert sha(raw)==review['raw_final_best_matrix_sha256']==audit['inputs_sha256'][raw]
    assert sha(final)==audit['inputs_sha256'][final]
    inputs=dict(audit['inputs_sha256']);inputs.update(review['inputs_sha256']);inputs.update({REVIEW:REVIEW_SHA,AUDIT:AUDIT_SHA})
    for name,digest in audit['outputs_sha256'].items():
        path=str(Path(AUDIT).parent/name).replace('\\','/');assert sha(path)==digest;inputs[path]=digest
    for which in ['current','best']:
        obj=audit['raw_final_matrices'][which];path=obj['independently_reconstructed_export'];assert sha(path)==obj['export_sha256'];inputs[path]=obj['export_sha256']
    source_protocol=json.loads((ROOT/protocol).read_bytes());inputs[protocol]=sha(protocol)
    statement=('The exact saved pilot01 best.adj is a symmetric binary zero-diagonal99-vertex14-regular point graph of231linear triples with pointdegree7, and its exact integer objective SRG_SQUARED_PAIR_RESIDUAL_V1 is E3034=E_lambda427+E_mu2607. The recorded full common-neighbor histograms are exact; this graph does not satisfy the target SRG matrix identity and provides no exclusion.')
    now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    object_report=dict(status='INDEPENDENT_PILOT01_LITERAL_BEST_OBJECT_CHECKED',timestamp=review['timestamp'],verifier=review['verifier'],producer=review['producer'],statement=statement,
        source_commit=review['source_commit'],producer_source_commit=source_protocol['source_commit'],source_configuration=source_protocol['options'],seed=99032010,
        inputs_sha256=inputs,raw_best_graph={'path':raw,'sha256':sha(raw)},raw_final_state={'path':final,'sha256':sha(final)},
        review_report={'path':REVIEW,'sha256':REVIEW_SHA},complete_saved_objects_report={'path':AUDIT,'sha256':AUDIT_SHA},
        exact_diagnostics=review['exact_literal_best_diagnostics'],verified_matrices=audit['raw_final_matrices'],target_resolution=False,new_exclusions=0,
        controls=review['calibrated_controls'],shared_components=review['source_review']['shared_components'],
        command=review['command'],cwd=review['cwd'],scope='One exact saved non-SRG graph and its point-triple representation; no whole-trajectory or graph-realizability inference from a relaxation.',
        creation={'script':source,'sha256':sha(source),'reason':'Exact scope-restriction and evidence binding of prior complete independent saved-object and literal matrix checks; no new scientific run.'})
    object_path=DIR+'/best_object_evidence.json';save(object_path,object_report);inputs[object_path]=sha(object_path)
    binding=dict(id='C-HYPERGRAPH-ANNEAL-PILOT01-SAVED-BEST-OBJECT',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description=object_report['scope'],unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Exact immutable native pilot01 artifacts and independently checked raw matrix/final labelled-triple state.',
                     'Finite one-seed pilot with seed99032010 and exact preserved temperatures/mixing/schedule in source_configuration.',
                     'Only saved graph properties are asserted; no performance, move-space connectivity, target automorphism or exhaustive coverage assumption.'],
        dependencies=[dict(id='C-HYPERGRAPH-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS',revision=1,relation='verification_dependency',reason='Calibrated independent adjacency-set/state/RNG and known-positive/corrupt fixtures; scientific sparse trajectory remains separately limited.')],
        dependency_reason='Engineering calibration supplies tested independent checking routines; full raw graph and matrix identity are checked separately here.',
        verifier=review['verifier'],producer=review['producer'],method='independent_artifact_check',created_at=now,updated_at=now,verification_timestamp=review['timestamp'],
        source_commit=review['source_commit'],producer_source_commit=source_protocol['source_commit'],source_configuration=source_protocol['options'],random_seed=99032010,
        command=review['command'],cwd=review['cwd'],inputs_sha256=inputs,report=object_path,report_sha256=sha(object_path),controls=review['calibrated_controls'],
        shared_components=review['source_review']['shared_components'],limitations=review['limitations']+['Native reported ending step20,000,000 is a counter observation; only2067anchored proposals of2247sparse records are fully independently replayed, with180unanchored gaps.',
            'Raw current.adj is MISSING in producer v1; exact independently reconstructed current and best matrices are preserved and equal the raw best.adj.','No independent controlled throughput comparison or general performance guarantee.'],
        artifact_availability='LOCAL_ONLY',retrieval='Exact raw matrix/final-state and hash-bound independent matrix/object reports at workspace paths; public availability requires a separate publication check.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Exact-r1 saved-object bookkeeping; original producer/checker/review bytes unchanged.'))
    target=DIR+'/claim_binding.json';save(target,binding)
    print(json.dumps({'path':target,'sha256':sha(target),'id':binding['id'],'revision':1,'evidence_report':object_path,'evidence_sha256':sha(object_path)}))


if __name__=='__main__':main()
