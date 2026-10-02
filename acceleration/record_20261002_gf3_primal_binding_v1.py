"""Bind the already completed independent ORIGINAL-GF3 primal check; no ledger edit."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_independent_review/gf3_full_artifact01'
REPORT=BASE+'/summary.json'
REPORT_SHA='5ea4c3115e06c748baf23122f9b7d0c8d8260000787fa377daea8f4d6cf95d08'
ID='C-PRISMFREE-ROOTED8-ORIGINAL-LITERAL-GF3-THREE-PRIMALS'


def sha(path):
    with(ROOT/path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes());assert report['status']=='INDEPENDENT_ORIGINAL_LITERAL_GF3_THREE_PRIMALS_V1_PASS'
    assert report['literal_result']==dict(complete_vectors=3,scalar_raw_row_component_checks=257622)
    assert report['profile_domain']['population']==210 and report['profile_domain']['excluded_profiles']==0
    pins={**report['inputs_sha256'],REPORT:REPORT_SHA}
    for path,wanted in pins.items():assert sha(path)==wanted,path
    calibration='acceleration/results/20261002_independent_review/gf3_endpoint_calibration01/summary.json';cal=json.loads((ROOT/calibration).read_bytes())
    assert sha(calibration)=='da9ee10677ef26cd0dd5c6a1272c98f12d05b6d52a7f2f676d85d85f58ea215b' and cal['full_scientific_output_inspected']is False
    now=datetime.now(timezone.utc).isoformat();casepath='acceleration/results/20261002_rooted8_gf3_solve01/input_case.json';case=json.loads((ROOT/casepath).read_bytes())
    artifacts=[]
    for rec in report['primal_vectors']:
        artifacts.append(dict(component='constant'if rec['label']=='const'else rec['label'],path=rec['path'],sha256=rec['sha256'],ternary_coordinates=rec['trits'],bytes=(ROOT/rec['path']).stat().st_size,availability='LOCAL_ONLY'))
    checkpoint='acceleration/results/20261002_rooted8_gf3_solve01/solve/checkpoint.bin';cp=report['artifact_availability'][checkpoint]
    outer='acceleration/results/20261002_independent_review/gf3_full_artifact_supervision01/summary.json';outerreport=json.loads((ROOT/outer).read_bytes())
    assert outerreport['command_exit_code']==0 and outerreport['cleanup']['reaped']and outerreport['cleanup']['job_active_zero_observed']
    binding=dict(id=ID,revision=1,claim_revision=1,kind='construction',basis=['COMPUTED','DERIVED'],status='VERIFIED',review_state='CLEAR',
      statement='For the exact frozen23019-column85874-row rooted8 ORIGINAL integer operator, the three recorded complete ternary vectors x_const,x_a,x_b satisfy respectively all constant,a,b affine RHS components modulo3. Consequently for every integer pair(a,b), x_const+(a mod3)*x_a+(b mod3)*x_b, reduced coordinatewise modulo3, solves that fixed literal operator. In particular all210 frozen profiles a=0..20,b=0..9 survive this modular consistency test, with zero exclusions.',
      scope=dict(description='Complete literal modular consistency certificate for one pinned local count operator. No rank, integer/nonnegative feasibility, root or graph realization, unrestricted target exclusion or target resolution.',unrestricted_target=False,target_resolution='NONE',profile_population=dict(unit='integer parameter pair',a_inclusive=[0,20],b_inclusive=[0,9],count=210,excluded=0),prism_free_target_interpretation='Conditional necessary graph model only; global prism absence remains UNKNOWN. Literal modular statement concerns the pinned matrix itself.'),
      assumptions=['Use exactly the frozen ORIGINAL signed integer operator, variable ordering and affine RHS ordering; repeated literal terms are summed exactly.','Interpret linear combinations over F3, not as integer nonnegative flag counts.','Positive row contents1,2,4 and normalized literal stream are independently checked identity evidence; primal verification uses ORIGINAL coefficients without division.','Any graph-level interpretation requires the independently checked conditional necessary encoding and UNKNOWN global no-induced-prism premise; no target automorphism.'],
      dependencies=[dict(id='C-PRISMFREE-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING',revision=1,relation='uses_result'),dict(id='C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN',revision=1,relation='coverage')],
      dependency_reason='Dependencies supply conditional graph interpretation and210profile population; original scalar certificate validity is directly bound to raw operator and vectors.',
      created_at=now,updated_at=now,source_commit=report['source_commit'],producer='/root/native_driver',verifier='/root/structural',method='independent_artifact_check',verification_timestamp=report['timestamp'],report=REPORT,report_sha256=REPORT_SHA,
      command=report['command'],cwd=report['cwd'],python=report['python_version'],inputs_sha256=pins,
      pre_output_calibration=dict(path=calibration,sha256=sha(calibration),full_output_inspected=False,fixture_operators=5,positive_complete_primal_sets=4,positive_original_row_relations=1,specific_corrupt_controls=len(cal['negative_controls'])),
      certificate_artifacts=artifacts,
      normalization=dict(raw_model='acceleration/results/20261002_rooted8_universal5_product_model02/model.json',raw_model_sha256=pins['acceleration/results/20261002_rooted8_universal5_product_model02/model.json'],rows=85874,columns=23019,literal_term_occurrences=968172,content_counts=case['content_counts'],input_case=casepath,input_case_sha256=sha(casepath),normalized_literal_jsonl=case['normalized_literal_rows'],normalized_literal_jsonl_sha256=case['normalized_literal_jsonl_sha256'],sparse_original_mod3_input=case['sparse_rows'],sparse_original_mod3_input_sha256=case['sparse_rows_sha256'],independently_checked='Every raw/content/divided literal hash and exact raw/divided roundtrip, normalized/originalmod3 sparse bytes, complete streams/content census; every primal scalar sum uses original signed coefficients.',availability='LOCAL_ONLY',retrieval='Current shared checkout contains exact raw paths. Public availability is not claimed before independent publication closure.'),
      verification=dict(bound_claim_id=ID,bound_claim_revision=1,raw_rows_checked_per_vector=85874,exact_scalar_row_component_checks=257622,actual_supported_coordinate_changed=0,actual_corruption_diagnostic='ENDPOINT_ORIGINAL_PRIMAL_SCALAR_ROW',shared_components=['Separate independently calibrated scalar checker698eb9bb... and endpoint checkerb57176cc...; no native/producer code imports.','Python exact integers/math.gcd, locked uv environment, deadline and contained supervisor.','Raw mathematical operator previously produced by structural but independently reconstructed by checkpoint_audit; this new modular discovery is produced by native_driver.'],command_and_full_hashes='The pinned immutable report contains exact command/cwd/environment and all checked identities.'),
      execution=dict(verifier_seconds=report['elapsed_seconds'],supervisor_seconds=outerreport['elapsed_seconds'],supervisor_summary=outer,supervisor_summary_sha256=sha(outer),observed_exit_code=0,reaped=True,empty_windows_job_observed=True,currently_running=False),
      resume_checkpoint=dict(path=checkpoint,sha256=cp['sha256'],bytes=cp['bytes'],availability='LOCAL_ONLY',retrieval='Current local checkout; same-source Linux little-endian GF3_PRIMAL_CP_V1 format. No automatic resume authorized.',mathematical_certificate_required=False,checked='Full audit checked hash/bytes only; no full checkpoint basis/DAG/rank validation. Three complete raw primal vectors suffice for the stated modular claim.'),
      artifacts=[dict(path=path,sha256=digest,availability='LOCAL_ONLY',retrieval='Current shared checkout; publication closure/recovery report separate.')for path,digest in pins.items()],
      limitations=['No full-operator rank or completeness-of-relations claim.','Modulo3 primal vectors do not certify integer/nonnegative count feasibility or graph realization.','No target graph/nonexistence proof; graph necessity remains conditional on UNKNOWN global prism absence.','No novelty, peer/external review or new public artifact availability claim.'],
      external_review=None,external_review_null_reason='Internal independent raw artifact check only.',overall_search_coverage='UNKNOWN; no validated denominator.')
    path=ROOT/BASE/'claim_binding.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(id=ID,revision=1,path=path.relative_to(ROOT).as_posix(),sha256=sha(path.relative_to(ROOT)),checkpoint_bytes=cp['bytes'])))


if __name__=='__main__':main()
