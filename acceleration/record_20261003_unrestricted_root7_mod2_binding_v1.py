"""Metadata-only binding of ROOT's independent report; no mathematical checking here."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261003_independent_review/root7_mod2_full02'
REPORT=BASE/'summary.json'
CAL=ROOT/'acceleration/results/20261003_independent_review/root7_mod2_calibration01/summary.json'
CAL_SHA='ab4dccea6b2d541b0907d6a19d8a5df55b37f015fc64ad39882feff59e3e8c5a'
RUN=ROOT/'acceleration/results/20261003_rooted7_unrestricted_gf2_screen01'
NECESSITY=ROOT/'acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/summary.json'
NECESSITY_SHA='e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70'


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def need(value,message):
    if not value:raise ValueError(message)


def main():
    report=json.loads(REPORT.read_bytes());calibration=json.loads(CAL.read_bytes());manifest=json.loads((RUN/'manifest.json').read_bytes());producer=json.loads((RUN/'summary.json').read_bytes())
    need(report['status']=='INDEPENDENT_UNRESTRICTED_ROOT7_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS'and report['verifier']=='/root'and report['producer']=='/root/structural','Root-authored exact report and roles')
    need(sha(CAL)==CAL_SHA and sha(NECESSITY)==NECESSITY_SHA,'Independent pre-output calibration and necessary-model pins')
    need((report['normalization_rows_checked'],report['complete_scalar_primal_row_checks'],report['profile_population'],report['excluded_profiles'],report['compatible_profiles'])==(11769,47076,651,0,651),'Root exact recorded scope')
    need(not report['rank_asserted']and report['positive_controls']==3 and report['strict_negative_controls']==16,'No new rank approval or controls claimed')
    full_sup=ROOT/'acceleration/results/20261003_independent_review/root7_mod2_full_supervision02'
    receipt=json.loads((full_sup/'summary.json').read_bytes());need(receipt['command_exit_code']==0 and receipt['cleanup']['reaped']and receipt['cleanup']['job_active_zero_observed'],'Recorded successful contained ROOT verification')
    files={**manifest['inputs_sha256'],**calibration['inputs_sha256'],**report['inputs_sha256']}
    for name,expected in producer['outputs_sha256'].items():files[(RUN/name).relative_to(ROOT).as_posix()]=expected
    folders=[RUN,CAL.parent,BASE,ROOT/'acceleration/results/20261003_rooted7_unrestricted_gf2_calibration01',ROOT/'acceleration/results/20261003_rooted7_unrestricted_gf2_calibration_supervisor01',ROOT/'acceleration/results/20261003_rooted7_unrestricted_gf2_screen_supervisor01',ROOT/'acceleration/results/20261003_independent_review/root7_mod2_calibration_supervision01',ROOT/'acceleration/results/20261003_independent_review/root7_mod2_full_supervision01',full_sup]
    for folder in folders:
        need(folder.is_dir(),'Existing immutable run folder '+str(folder))
        for path in folder.iterdir():
            if path.is_file():files[path.relative_to(ROOT).as_posix()]=sha(path)
    for path in [NECESSITY,NECESSITY.with_name('claim_binding.json'),Path(__file__)]:files[path.relative_to(ROOT).as_posix()]=sha(path)
    for path,expected in files.items():need(sha(ROOT/path)==expected,'Authenticated metadata evidence identity '+path)
    now=datetime.now(timezone.utc).isoformat();binding=dict(id='C-UNRESTRICTED-ROOTED7-CONTENT-DIVIDED-GF2-FOUR-PRIMALS',revision=1,claim_revision=1,statement='For the exact2810-column11769-row unrestricted rooted-seven necessary count operator, an independently authored dense-integer/scalar checker reconstructed every original row by combining duplicate columns and dividing its positive content over all coefficients and four affine RHS components, and verified four complete2810-coordinate binary vectors for constant,c,a,b against all47076 scalar component equations modulo2. These explicit vectors establish literal content-divided mod2 compatibility for every one of the651 recorded primary integer profiles0<=c<=2,0<=a<=20,0<=2b<=18+c. Zero profiles are excluded; no rank, nonnegative integer count solution or graph realization is established.',kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',scope=dict(description='Only exact primitive-row reconstruction and four literal GF2 primal certificates for the pinned unrestricted necessary model, with the complete651-profile population classified. Integer row division preserves exact equations; finite-field consistency is necessary only.',unrestricted_target=False,target_resolution='NONE'),assumptions=['All coefficients, row contents and scalar checks use exact integer arithmetic before reduction modulo2.','The independently checked prior raw model is necessary for hypothetical target counts; that necessity is reused rather than rederived by this parity checker.','Every four-component row content divides its constant,c,a,b coefficients, so division preserves each exact integer profile equation.'],dependencies=[dict(id='C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING',revision=1,relation='verification_dependency',reason='Pinned independently reconstructed necessary-model semantics supplies the interpretation; literal mod2 certificates do not rederive this encoding.')],created_at=now,updated_at=now,producer='/root/structural',verifier='/root',method='independent_artifact_check',verification_timestamp=report['timestamp'],source_commit=manifest['source_commit'],source_commit_role='Recorded producing invocation base commit; producer source bytes are separately pinned.',verifier_source_commit=None,verifier_source_commit_null_reason='The original independent ROOT report did not record a Git commit; exact checker source and environment hashes and actual argv are preserved without inventing one.',command=report['command'],cwd=report['cwd'],producer_python=manifest['python_version'],verifier_tool_versions=None,verifier_tool_versions_null_reason='Exact runtime versions were not recorded in the original ROOT report; locked uv environment and literal Python executable argv are retained.',report=REPORT.relative_to(ROOT).as_posix(),report_sha256=sha(REPORT),pre_output_calibration=CAL.relative_to(ROOT).as_posix(),pre_output_calibration_sha256=CAL_SHA,inputs_sha256=files,shared_components=report['shared_components']+['Independent checker imports only the pinned deadline helper and standard library; no producer code, bitset elimination or rank algorithm is imported.'],recorded_validation=dict(normalization_rows=11769,component_scalar_row_checks=47076,binary_vectors=4,coordinates_per_vector=2810,profiles=651,compatible_profiles=651,excluded_profiles=0,positive_controls=3,strict_negative_controls=16,actual_fullwidth_coordinate_flip_rejected=True,content_census=producer['content_census']),failed_attempt_preserved=dict(path='acceleration/results/20261003_independent_review/root7_mod2_full_supervision01',recorded_exit=1,deadline_reached=False,argument_form='Original relative --run and --calibration argv preserved in manifest; successful02 uses absolute argv.',error_text=None,error_text_null_reason='No failure report or captured exact stderr was saved in the original full01 output directory; raw supervisor and argv records are preserved.',claim_refuted=False),limitations=report['limitations']+['No new mathematical check or independent approval is performed by this metadata writer; status reflects ROOT report and explicit parent instruction, pending ROOT binding review.','Successful absolute-argv02 does not erase the failed relative-argv01 command.','No exhaustive graph coverage denominator, target graph or general nonexistence result is claimed.'],availability='LOCAL_ONLY',retrieval='All raw normalized rows, vectors, all651 outcomes, producer/pre-output checker calibrations, successful and failed actual receipts and exact source bytes exist at bound repository paths; public availability follows publication separately.',metadata_only=True,writer_source_sha256=sha(Path(__file__)),writer_command=[sys.executable,*sys.argv],ledger_mutations=0)
    path=BASE/'claim_binding.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    with(BASE/'binding_identity.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(dict(binding_sha256=sha(path),report_sha256=sha(REPORT),metadata_only=True),stream,indent=2);stream.write('\n')


if __name__=='__main__':main()
