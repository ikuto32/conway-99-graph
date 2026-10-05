"""Immutable exact-r1 binding for the independently derived rooted8 operator."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/rooted8_model01'
REPORT=DIR+'/summary.json'
REPORT_SHA='e3158fe17f4a83e5231c90f72c912e5ef37cd6ddc3ce6300f0c6861f9d0ffc4e'


def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_ROOTED8_MARKED_UNIVERSAL5_PRODUCT_MODEL_PASS'
    assert [report[k] for k in ['variables','rows','nonzeros','free_deletions_checked','every_lower_isomorphism_checks']]==[23019,85874,968172,121518,4789399]
    assert report['target_resolution'] is False and report['new_exclusions']==0 and report['prismfree_premise_established'] is False
    inputs=dict(report['inputs_sha256']);inputs[REPORT]=REPORT_SHA
    for name,digest in report['outputs_sha256'].items():path=DIR+'/'+name;assert sha(path)==digest;inputs[path]=digest
    now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    binding=dict(id='C-PRISMFREE-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING',revision=1,claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=report['statement'],
        scope=dict(description=report['scope']+' All85,874 equations include the pinned11,749-row root7 operator,70,297 newly reconstructed marked-extension equations and3,828 universal-root5 upper-pair product identities. Counts refer to actual unordered free subsets at a fixed ordered nonedge, with no automorphism division.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Hypothetical simple srg(99,14,1,2) and an actual ordered nonadjacent pair of its vertices.',
            'No induced triangular prism anywhere in the hypothetical target; this premise remains UNKNOWN.',
            'Pinned independently checked universal rooted5 counts, conditional rooted6 affine integer domain, complete conditional rooted8 catalogue and inherited root7 necessary operator.',
            'Finite free-label symmetries normalize rooted flags/marks only; no target automorphism, equal profiles at distinct roots or arbitrary fixed root7 witness is assumed.'],
        dependencies=report['dependencies'],dependency_reason='Exact lower counts, inherited necessary equations and complete finite flag coordinates are pinned; new marked transports and all overlap/collision/product coefficients are separately reconstructed by this audit.',
        premise_state=dict(no_induced_triangular_prism='UNKNOWN',reason='Only a conditional necessary count operator is established, with no graph realization or absence theorem.'),
        verifier=report['verifier'],producer=report['producer'],method='independent_derivation_and_complete_artifact_checking',created_at=now,updated_at=now,verification_timestamp=report['timestamp'],
        source_commit=report['source_commit'],command=report['command'],cwd=report['cwd'],python=report['python'],inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,controls=report['controls'],
        shared_components=report['shared_components'],limitations=report['limitations'],artifact_availability='LOCAL_ONLY',retrieval='Exact frozen workspace inputs/output hashes; public availability requires separate lossless recovery/publication checks.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Exact-r1 bookkeeping only; immutable audit/operator bytes unchanged and no solver, certificate or exclusion is promoted.'))
    target=DIR+'/claim_binding.json'
    with (ROOT/target).open('x',encoding='utf8',newline='\n') as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(path=target,sha256=sha(target),id=binding['id'],revision=1)))


if __name__=='__main__':main()
