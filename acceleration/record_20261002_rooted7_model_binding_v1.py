"""Immutable exact-r1 binding for conditional necessary rooted7 encoding."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/rooted7_model01'
REPORT=DIR+'/summary.json'
REPORT_SHA='df0a614a76d4cc6365468993c9cb7b2ad836484946e00da059977642b37db76f'


def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_ROOTED7_MARKED_REROOT_NECESSARY_MODEL_PASS' and report['target_resolution'] is False and report['new_exclusions']==0
    assert [report[k] for k in ['variables','rows','nonzeros','every_lower_isomorphism_checks','reroot_union_collision_choices']]==[2766,11749,86129,402422,31148]
    inputs=dict(report['inputs_sha256']);inputs[REPORT]=REPORT_SHA
    for name,digest in report['outputs_sha256'].items():path=DIR+'/'+name;assert sha(path)==digest;inputs[path]=digest
    now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    binding=dict(id='C-PRISMFREE-ROOTED7-MARKED-REROOT-NECESSARY-ENCODING',revision=1,claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=report['statement'],
        scope=dict(description=report['scope']+' Applies per actual ordered primary nonedge only under the explicit prism-free premise; satisfying these rows is not sufficient for graph realization.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Hypothetical simple srg(99,14,1,2) with an actual ordered primary nonedge.',
                     'No induced triangular prism anywhere in the hypothetical target; this premise remains UNKNOWN.',
                     'Pinned independently checked complete conditional rooted7 catalogue, conditional rooted6 edge rigidity, and conditional rooted6 nonedge affine integer domain.',
                     'Only finite free-label automorphisms of each induced flag normalize marks; no target automorphism or equality among distinct nonedge-root profiles is assumed.'],
        dependencies=report['dependencies'],dependency_reason='The exact verified source/results provide the complete flag coordinates and conditional lower counts; this new audit independently derives all marked, reroot, collision and aggregate coefficients.',
        premise_state=dict(no_induced_triangular_prism='UNKNOWN',reason='Necessary model implication is conditional; no absence theorem or target exclusion is established.'),
        verifier=report['verifier'],producer=report['producer'],method='independent_derivation',created_at=now,updated_at=now,verification_timestamp=report['timestamp'],
        source_commit=report['source_commit'],command=report['command'],cwd=report['cwd'],python=report['python'],inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,
        controls=report['controls'],shared_components=report['shared_components'],limitations=report['limitations'],artifact_availability='LOCAL_ONLY',
        retrieval='Exact frozen workspace paths and hash-bound independent reconstruction; public availability requires separate publication metadata audit.',
        binding_creation=dict(script=source,sha256=sha(source),scope='Exact-r1 conditional encoding bookkeeping only; original report/operator bytes unchanged.'))
    target=DIR+'/claim_binding.json'
    with (ROOT/target).open('x',encoding='utf8',newline='\n') as f:json.dump(binding,f,indent=2);f.write('\n')
    print(json.dumps({'path':target,'sha256':sha(target),'id':binding['id'],'revision':1}))


if __name__=='__main__':main()
