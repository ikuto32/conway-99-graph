"""Exact-r1 immutable binding for completed conditional finite rooted8 coverage."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/rooted8_catalogue01'
REPORT=DIR+'/summary.json'
REPORT_SHA='c763a3929b0c857167e7ec618078ed207aedd213a6bf74939cc856f1e5ed4a59'


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_COMPLETE_CONDITIONAL_ROOTED8_CATALOGUE_PASS'
    assert [report[k] for k in ['parent_classes','labelled_augmentation_attempts','complete_conditional_rooted_classes','exact_labelled_image_checks']]==[2750,352000,20253,14582160]
    assert report['target_resolution'] is False and report['new_exclusions']==0 and report['prismfree_premise_established'] is False
    inputs=dict(report['inputs_sha256']);inputs[REPORT]=REPORT_SHA
    now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    binding=dict(id='C-PRISMFREE-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE',revision=1,claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=report['statement'],
        scope=dict(description=report['scope']+' Every finite simple rooted8 graph with fixed ordered nonedge, local common-neighbor caps1/2 and no induced triangular prism belongs to exactly one recorded free-label orbit; this is applicable to a target only under that explicit unestablished premise.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Simple finite graphs with fixed ordered nonadjacent roots satisfy local adjacent/nonadjacent common-neighbor caps1/2 and contain no induced triangular prism.',
            'Pinned independently checked complete rooted7 nonedge catalogue provides the parent coverage premise.',
            'Only permutations of the six free labels define flag coordinates; no target automorphism or equality of counts at distinct roots is assumed.'],
        dependencies=report['dependencies'],dependency_reason='Deleting any free vertex maps every admissible prism-free rooted8 flag to a covered prism-free rooted7 flag; all128 neighborhoods of every2750 parent are independently covered.',
        premise_state=dict(no_induced_triangular_prism='UNKNOWN',reason='Only finite conditional catalogue completeness is proved; no target prism absence theorem is established.'),
        verifier=report['verifier'],producer=report['producer'],method='independent_derivation_and_complete_artifact_checking',created_at=now,updated_at=now,verification_timestamp=report['timestamp'],
        source_commit=report['source_commit'],command=report['command'],cwd=report['cwd'],python=report['python'],inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,controls=report['controls'],
        shared_components=['Python exact integer bit/array operations, SHA-256, locked uv runtime and supported deadline/supervisor; no producer or prior catalogue enumeration implementation imported.'],
        limitations=report['limitations'],artifact_availability='LOCAL_ONLY',retrieval='Exact frozen workspace paths and report input hashes; public availability requires a separate publication audit.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Exact-r1 bookkeeping only; no ordinary/product encoding, certificate, exclusion or target approval.'))
    target=DIR+'/claim_binding.json'
    with (ROOT/target).open('x',encoding='utf8',newline='\n') as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(path=target,sha256=sha(target),id=binding['id'],revision=1)))


if __name__=='__main__':main()
