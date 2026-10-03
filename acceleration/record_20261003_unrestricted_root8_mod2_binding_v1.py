"""Metadata-only binding of ROOT's existing independent scalar report."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261003_independent_review/root8_mod2_full01'
REPORT=BASE/'summary.json'
REPORT_SHA='410e7e4dd7f4e9caff1f9eb8b349a35afd24808e44826e7d1dc89d4a0b7249c2'
CAL=ROOT/'acceleration/results/20261003_independent_review/root8_mod2_calibration01/summary.json'
CAL_SHA='d0238a17825e7fe23aa438c6f2f45a1cf26d470f64aa0f79c2524fc4d6900af2'
RUN=ROOT/'acceleration/results/20261003_root8_gf2_screen01'
NECESSITY=ROOT/'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/summary.json'
NECESSITY_BINDING=NECESSITY.with_name('claim_binding_schema2.json')
NB_SHA='45e8878f0addc74b92a75d3a70af30bca2923f9407e4fdb5969e031d2a89bdd2'


def digest(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    need(digest(REPORT)==REPORT_SHA and digest(CAL)==CAL_SHA and digest(NECESSITY_BINDING)==NB_SHA,'Exact accepted ROOT report/preoutput calibration/necessary-encoding binding')
    report=json.loads(REPORT.read_bytes());cal=json.loads(CAL.read_bytes());producer=json.loads((RUN/'summary.json').read_bytes());manifest=json.loads((RUN/'manifest.json').read_bytes())
    need(report['status']=='INDEPENDENT_UNRESTRICTED_ROOT8_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS'and report['verifier']=='/root'and report['producer']=='/root/structural','Separate authored ROOT verifier and exact report')
    need((report['normalization_rows_checked'],report['complete_scalar_primal_row_checks'],report['profile_population'],report['excluded_profiles'],report['compatible_profiles'],report['positive_controls'],report['strict_negative_controls'])==(86434,345736,651,0,651,5,16),'Exact report scope, not new verification')
    need(report['rank_asserted']is False and len(producer['complete_component_primals'])==4 and not producer['nonzero_affine_relation_certificates'],'Four explicit primals and no rank/exclusion')
    full_sup=ROOT/'acceleration/results/20261003_independent_review/root8_mod2_full_supervision01';receipt=json.loads((full_sup/'summary.json').read_bytes())
    need(receipt['command_exit_code']==0 and receipt['cleanup']['reaped']and receipt['cleanup']['job_active_zero_observed'],'Actual ROOT successful verification receipt')
    pins={**report['inputs_sha256'],**manifest['inputs_sha256'],**cal['inputs_sha256']}
    for name,expected in producer['outputs_sha256'].items():pins[(RUN/name).relative_to(ROOT).as_posix()]=expected
    folders=[RUN,BASE,CAL.parent,full_sup,ROOT/'acceleration/results/20261003_independent_review/root8_mod2_calibration_supervision01',ROOT/'acceleration/results/20261003_root8_gf2_calibration01',ROOT/'acceleration/results/20261003_root8_gf2_calibration_supervisor01',ROOT/'acceleration/results/20261003_root8_gf2_screen_supervisor01',ROOT/'acceleration/results/20261003_root8_gf2_candidate_metadata_supervisor01']
    for folder in folders:
        need(folder.is_dir(),'Actual evidence folder '+str(folder))
        for path in folder.rglob('*'):
            if path.is_file():pins[path.relative_to(ROOT).as_posix()]=digest(path)
    extras=[NECESSITY,NECESSITY_BINDING,ROOT/'acceleration/results/20261003_root8_gf2_windows_observation01.json',ROOT/'acceleration/results/20261003_root8_gf2_control_metadata01.json',ROOT/'acceleration/results/20261003_root8_gf2_source_metadata01.json',Path(__file__),ROOT/'docs/CANDIDATE_20261003_TRIANGLE_INCIDENCE_GRIESMER_V1.md']
    for path in extras:pins[path.relative_to(ROOT).as_posix()]=digest(path)
    for name,expected in pins.items():need(digest(ROOT/name)==expected,'Metadata identity authentication '+name)
    now=datetime.now(timezone.utc).isoformat()
    binding=dict(
        id='C-UNRESTRICTED-ROOTED8-CONTENT-DIVIDED-GF2-FOUR-PRIMALS',revision=1,claim_revision=1,
        statement='For the pinned23334-column86434-row unrestricted rooted-eight necessary count operator, a separate dense-integer/scalar checker reconstructed every original row by combining duplicate column coefficients and dividing its positive content over all coefficients and four affine RHS components. It verified four complete23334-coordinate binary primal vectors for constant,c,a,b against all345736 scalar component equations modulo2. These vectors establish literal content-divided mod2 compatibility for each of the651 recorded primary integer profiles0<=c<=2,0<=a<=20,0<=2b<=18+c; zero profiles are excluded. No rank, nonnegative integer count solution or graph realization is established.',
        kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description='Only exact primitive-row reconstruction and four literal GF2 primal certificates for one pinned unrestricted necessary model and its frozen651primary-profile population. Integer row division preserves exact equations; finite-field consistency is necessary only.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Exact integer coefficients/gcd/content reconstruction precedes modulo2 checking.','The separately checked rooted8 necessary model and complete local catalogue are reused, not rederived by this parity checker.','Content divides all four affine components, so each recorded integer-profile equation has an exact equivalent divided row.'],
        dependencies=[dict(id='C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING',revision=1,relation='verification_dependency',reason='Independent complete necessary-encoding reconstruction supplies the target interpretation; scalar certificate checking does not rederive it.')],
        created_at=now,updated_at=now,producer='/root/structural',verifier='/root',method='independent_artifact_check',verification_timestamp=report['timestamp'],
        source_commit=manifest['source_commit'],source_commit_role='Actual producing invocation base commit; new working producer/protocol source bytes are pinned separately and their Git presence is not inferred.',
        verifier_source_commit=None,verifier_source_commit_null_reason='Original ROOT endpoint report did not record a Git commit; exact checker/environment hashes and actual command are preserved.',
        command=report['command'],cwd=report['cwd'],producer_python=manifest['python_version'],
        verifier_tool_versions=None,verifier_tool_versions_null_reason='Original ROOT report did not record exact runtime version strings; locked environment and Python executable command are retained.',
        report=REPORT.relative_to(ROOT).as_posix(),report_sha256=REPORT_SHA,pre_output_calibration=CAL.relative_to(ROOT).as_posix(),pre_output_calibration_sha256=CAL_SHA,inputs_sha256=pins,
        shared_components=report['shared_components']+['The independent checker imports only the pinned deadline helper and Python standard library; it imports no producer code or bitset elimination/rank algorithm.'],
        recorded_validation=dict(normalization_rows=86434,component_scalar_row_checks=345736,binary_vectors=4,coordinates_per_vector=23334,profiles=651,compatible_profiles=651,excluded_profiles=0,positive_controls=5,strict_negative_controls=16,actual_fullwidth_coordinate_flip_rejected=True,content_census=producer['content_census']),
        failed_full_attempts=None,failed_full_attempts_null_reason='No failed full attempt is recorded for this new root8 GF2 producer or endpoint checker; earlier root7 relative-argument failure remains in its separate historical claim.',
        limitations=report['limitations']+['No new mathematical check or independent approval is performed by this metadata writer; status reflects the accepted ROOT report and explicit parent instruction, pending ROOT binding review.','No target graph, general nonexistence result or target-wide graph-coverage denominator is claimed.','The separately preserved candidate Griesmer note is metadata-pinned only and is not a premise of this GF2 result.'],
        availability='LOCAL_ONLY',retrieval='Raw normalized rows, four binary vectors, all651 outcomes, preoutput producer/checker controls, exact sources and actual completed receipts exist at bound repository paths; publication is separately recorded.',
        metadata_only=True,writer_source_sha256=digest(Path(__file__)),writer_command=[sys.executable,*sys.argv],ledger_mutations=0)
    path=BASE/'claim_binding.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    with(BASE/'binding_identity.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(dict(binding_sha256=digest(path),report_sha256=REPORT_SHA,metadata_only=True,candidate_griesmer_note_sha256=digest(extras[-1])),stream,indent=2);stream.write('\n')


if __name__=='__main__':main()
