"""Bind independently checked literal rational witnesses to exact claim r1.

Bookkeeping/hashing only; no producer import, solver, row-semantic promotion,
ledger mutation or git-index change. Preserve all original audit/run bytes.
"""
import argparse
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
DIR='acceleration/results/20261002_independent_review/rooted7_corner_witnesses01'
REPORT=DIR+'/summary.json'
REPORT_SHA='382459c568c8e5f9251746f60376e07c82ba981d1bab68ae2c0bc22790f04ca1'
MODEL_BIND='acceleration/results/20261002_independent_review/rooted7_model01/claim_binding.json'
MODEL_BIND_SHA='96d139186fd243a84831abb92d4d611cfe001043309719b998f563979a311b25'
MODEL_REPORT='acceleration/results/20261002_independent_review/rooted7_model01/summary.json'
MODEL_REPORT_SHA='df0a614a76d4cc6365468993c9cb7b2ad836484946e00da059977642b37db76f'
PRODUCER_MANIFEST='acceleration/results/20261002_rooted7_corner_certificates02/manifest.json'
PRODUCER_MANIFEST_SHA='06b2982ecdc68d6232eec7d2cc1190e41e6be441d83d8cc781db443e0371fdc3'


def need(value,message):
    if not value:raise ValueError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',type=float,required=True)
    parser.add_argument('--allocation-reason',required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason)
    pins={}
    def pin(name,wanted=None):
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'local raw artifact')
        h=hashlib.sha256()
        with path.open('rb')as f:
            for block in iter(lambda:f.read(8*1024**2),b''):
                need(deadline.status()['remaining_seconds']>10 and not deadline.status()['stop_required'],'not completed within allocated budget');h.update(block)
        digest=h.hexdigest();need(wanted is None or wanted==digest,'exact artifact SHA256 '+name);pins[name]=digest
        return json.loads(path.read_bytes())if path.suffix=='.json'else path
    report=pin(REPORT,REPORT_SHA)
    need(report['status']=='INDEPENDENT_ROOTED7_LITERAL_CORNERS_AND_BILINEAR_WITNESSES_V1_PASS' and report['verifier']=='/root/native_driver'
         and report['target_resolution']is False and report['mathematical_row_semantics_verified']is False,'literal-only independent report')
    need(report['model_dimensions']==dict(variables=2766,equations=11749,term_occurrences=86129),'exact literal dimensions')
    for name,digest in report['inputs_sha256'].items():pin(name,digest)
    for item in ['all210_witnesses','controls']:pin(report['evidence'][item],report['evidence'][item+'_sha256'])
    corners=report['corner_checks'];points=report['all210_point_checks']
    need([c['point']for c in corners]==[[0,0],[20,0],[0,9],[20,9]] and all(c['integer_coordinates'] and c['result']['nonnegative']
         and c['result']['rows_checked']==11749 and c['result']['row_mismatch_count']==0 for c in corners),'four exact integer corners')
    need([p['point']for p in points]==[[a,b]for a in range(21)for b in range(10)] and all(p['nonnegative']and p['row_mismatch_count']==0
         and p['rows_checked']==11749 for p in points),'all210 exact rational literal witnesses')
    need(report['integer_interpolated_point_count']==4 and report['rational_noninteger_interpolated_point_count']==206
         and report['integer_interpolated_points']==[[0,0],[0,9],[20,0],[20,9]],'integrality of named witnesses only')
    controls=json.loads((ROOT/report['evidence']['controls']).read_bytes())
    need(len(controls['arithmetic_controls'])==6 and all(c['expected_acceptance']==c['actual_acceptance']for c in controls['arithmetic_controls'])
         and len(controls['malformed_controls'])==6 and all(c['rejected']for c in controls['malformed_controls']),'saved complete calibrated controls')
    model=pin(MODEL_BIND,MODEL_BIND_SHA);pin(MODEL_REPORT,MODEL_REPORT_SHA)
    need(model['id']=='C-PRISMFREE-ROOTED7-MARKED-REROOT-NECESSARY-ENCODING' and model['revision']==1 and model['status']=='VERIFIED'
         and model['review_state']=='CLEAR' and model['inputs_sha256']['acceleration/results/20261002_rooted7_extension_model/model.json']==pins['acceleration/results/20261002_rooted7_extension_model/model.json'],'exact separately verified encoding r1 identity')
    producer=pin(PRODUCER_MANIFEST,PRODUCER_MANIFEST_SHA)
    for name,digest in producer['inputs_sha256'].items():pin(name,digest)
    for name in ['acceleration/results/20261002_independent_review/rooted7_corner_witnesses_supervision01/manifest.json',
                 'acceleration/results/20261002_independent_review/rooted7_corner_witnesses_supervision01/summary.json']:pin(name)
    source=Path(__file__).relative_to(ROOT).as_posix();pin(source)
    now=datetime.now(timezone.utc).isoformat()
    statement=('For the exact2766-coordinate11749-row integer affine system identified by model SHA21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595, the four supplied corner vectors at(a,b)=(0,0),(20,0),(0,9),(20,9) are nonnegative integer solutions. For every integer(a,b) in{0,...,20}x{0,...,9}, the recorded denominator180 bilinear interpolation of those corners is a nonnegative rational solution of all11749 literal rows. Exactly the four corner interpolation vectors are integral; the other206 recorded interpolation vectors are nonintegral.')
    binding=dict(id='C-ROOTED7-LITERAL-AFFINE-RATIONAL-WITNESS-RECTANGLE',revision=1,claim_revision=1,
        kind='construction',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description='Fixed literal affine system and210 explicit rational witness vectors only; use as a necessary relaxation of the target is conditional on the separately pinned prism-free encoding implication.',
                   unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Exact fixed input model and raw corner artifacts are immutable.','Affine rows are checked as literal integer terms/RHS, not reconstructed by this witness verifier.',
                     'Any interpretation as necessary SRG relations uses the independently checked encoding r1 and its explicit UNKNOWN no-induced-triangular-prism premise.'],
        dependencies=[dict(id='C-PRISMFREE-ROOTED7-MARKED-REROOT-NECESSARY-ENCODING',revision=1,relation='uses_result')],
        dependency_reason='Pins the precise fixed model and its separately verified conditional necessary interpretation; literal witness arithmetic does not need the prism-free premise.',
        verifier='/root/native_driver',producer='/root/structural',method='independent_artifact_check',
        created_at=now,updated_at=now,verification_timestamp=report['timestamp'],source_commit=report['source_commit'],producer_source_commit=producer['source_commit'],
        command=report['command'],cwd=report['cwd'],python=report['python'],inputs_sha256=pins,report=REPORT,report_sha256=REPORT_SHA,
        evidence=report['evidence'],controls=controls,shared_components=report['trusted_shared_components'],
        statement_evidence=dict(corner_vectors=4,interpolated_vectors=210,integer_interpolated_vectors=4,nonintegral_interpolated_vectors=206,
            coordinates_per_vector=2766,rows_per_vector=11749,scaled_denominator=180,
            bilinear_numerators=['(20-a)*(9-b)','a*(9-b)','(20-a)*b','a*b'],corner_order=[[0,0],[20,0],[0,9],[20,9]],
            every_recorded_coordinate_and_row_checked=True,no_lp_solver_or_producer_import=True),
        limitations=['Nonintegrality of one recorded witness does not imply integer infeasibility, nor does a rational witness establish integer feasibility at that point.',
                     'No graph construction, target exclusion, sufficient realization or unrestricted nonexistence proof.',
                     'The original witness report accurately records row-semantic verification as unavailable at that time; its bytes remain unchanged. A separate later encoding audit supplies the pinned conditional interpretation.',
                     'No new row-semantic derivation or expensive witness replay in this bookkeeping invocation.'],
        unknowns=dict(integer_feasibility_at_other206_points=None,integer_feasibility_null_reason='Only nonintegrality of the supplied interpolation witnesses is checked; existence of other integer solutions remains unresolved.',
            graph_realization=None,graph_realization_null_reason='Literal affine feasibility is not sufficient for graph realization.'),
        artifact_availability='LOCAL_ONLY',retrieval='Exact repository workspace paths and raw hashes; public replay requires a separate publication check.',
        binding_creation=dict(script=source,sha256=pins[source],command=[sys.executable,*sys.argv],cwd=str(ROOT),timestamp=now,
                              source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='Exact-r1 bookkeeping only; original independently authored producer/verifier evidence preserved.',deadline=deadline.status()))
    target=ROOT/DIR/'claim_binding.json'
    with target.open('x',encoding='utf8',newline='\n')as f:json.dump(binding,f,indent=2);f.write('\n')
    print(json.dumps(dict(path=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),id=binding['id'],revision=1)))


if __name__=='__main__':main()
