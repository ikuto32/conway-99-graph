"""Metadata-only projection of ROOT's separately verified C4 count, no replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SOURCE='acceleration/record_20261003_weight5_c4_binding_v1.py'
SPEC='acceleration/record_20261003_weight5_c4_binding_v1_spec.md'
CID='C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT'
REPORT='acceleration/results/20261003_independent_review/weight5_c4_raw_full02/summary.json'
REPORT_SHA='75bf5f7adc8b082311b4ad786d46f53857960ea07c8cb58576c3a38d2bbce5a5'
CAL='acceleration/results/20261003_independent_review/weight5_c4_raw_calibration03/summary.json'
CAL_SHA='e4ba5e7dbe927ce2b3c60b80600bb8436d9e6b47de2a87af784e9157853c27bf'
PROOF='acceleration/audit_20261003_triangle_image_weight5_c4_v1.md'
PROOF_SHA='bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12'
STATEMENT='For every finite simple graph with exactly one common neighbor for each adjacent pair, the binary triangle-incidence image contains at least max(ceil(P/2), P-c4(G)) weight-five words, where P is the unordered three-triangle path count and c4(G) the induced four-cycle count. Consequently any srg(99,14,1,2) has N5>=22869 and its exact degree-five kernel-character shifted right-hand side is71500275.'
FOLDERS=[
 'acceleration/results/20261003_triangle_image_weight5_c4_controls_supervision01',
 'acceleration/results/20261003_triangle_image_weight5_c4_controls_supervision02',
 'acceleration/results/20261003_triangle_image_weight5_c4_controls_supervision03',
 'acceleration/results/20261003_triangle_image_weight5_c4_controls01',
 'acceleration/results/20261003_triangle_image_weight5_c4_controls02',
 'acceleration/results/20261003_independent_review/weight5_c4_raw_calibration_supervision03',
 'acceleration/results/20261003_independent_review/weight5_c4_raw_full_supervision01',
 'acceleration/results/20261003_independent_review/weight5_c4_raw_full_supervision02',
 'acceleration/results/20261003_independent_review/weight5_c4_raw_full02',
 'acceleration/results/20261003_independent_review/weight5_c4_raw_calibration03']
PLANS=['acceleration/plan_20261003_weight5_c4_controls_corrected_v1.json',
 'acceleration/plan_20261003_weight5_c4_v2_controls_v1.json',
 'acceleration/plan_20261003_weight5_c4_v2_controls_v2.json']

def need(ok,stage):
 if not ok:raise ValueError(stage)
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n')as stream:
  json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 deadline=CommandDeadline(a.seconds,allocation_reason='Metadata identity authentication and exact new C4 binding projection only; no mathematics/native/ledger replay;10second save reserve')
 out=a.out.resolve();need(out.is_relative_to(ROOT)and not out.exists(),'FRESH_WORKSPACE_OUTPUT');out.mkdir(parents=True)
 protected={path:sha(ROOT/path)for path in ['CLAIMS.yaml','.git/index']};pins={}
 def pin(name,wanted=None):
  need(deadline.status()['remaining_seconds']>10,'METADATA_SAVE_RESERVE');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'INPUT_BOUNDARY');actual=sha(path);need(wanted is None or actual==wanted,'EXACT_IDENTITY:'+name);need(name not in pins or pins[name]==actual,'STABLE_IDENTITY:'+name);pins[name]=actual
 try:
  for name,wanted in {REPORT:REPORT_SHA,CAL:CAL_SHA,PROOF:PROOF_SHA}.items():pin(name,wanted)
  report=json.loads((ROOT/REPORT).read_bytes());cal=json.loads((ROOT/CAL).read_bytes())
  need(report['status']=='INDEPENDENT_WEIGHT5_C4_COLLISION_COMPLETE_RAW_V1_PASS'and report['producer']=='/root/structural'and report['verifier']=='/root'and report['method']=='independent_derivation_and_complete_artifact_checking'and report['universal_derivation_checked']is True and report['producer_outputs_checked']is True and report['universal_statement']==STATEMENT and report['target_resolution']=='NONE','ACTUAL_INDEPENDENT_SCOPE')
  need([report[key]for key in ['complete_original_fixtures','complete_three_triangle_combinations','unordered_paths','separate_fixture_supports','complete_induced_c4s','complete_double_fibers','complete_small_image_coefficient_masks','complete_character_coefficients','complete_normalized_weights','actual_saved_strict_corruptions','strict_interface_corruptions','target_weight5_lower_count','target_character_rhs']]==[7,62,23,14,10,9,234,100,99,18,27,22869,71500275],'EXACT_RECORDED_COUNTS')
  need(cal['status']=='INDEPENDENT_WEIGHT5_C4_RAW_V1_CALIBRATION_PASS'and cal['producer_outputs_checked']is False and cal['strict_interface_corruptions']==27,'ACTUAL_PREOUTPUT_CALIBRATION')
  for saved in [report,cal]:
   for name,wanted in saved['inputs_sha256'].items():pin(name,wanted)
  for name in [SOURCE,SPEC,'pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py',*PLANS]:pin(name)
  for folder in FOLDERS:
   for path in sorted((ROOT/folder).rglob('*')):
    if path.is_file():pin(path.relative_to(ROOT).as_posix())
  now=datetime.now(timezone.utc).isoformat();shared=list(report['shared_components'])
  controls=dict(independent_preoutput=dict(path=CAL,sha256=CAL_SHA,original_fixtures=7,complete_three_triangle_combinations=62,complete_image_masks=234,literal_character_coefficients=100,normalized_character_weights=99,precise_interface_corruptions=27,producer_outputs_checked=False),independent_actual=dict(path=REPORT,sha256=REPORT_SHA,original_fixtures=7,complete_three_triangle_combinations=62,unordered_paths=23,separate_fixture_supports=14,induced_c4s=10,double_fibers=9,complete_image_masks=234,positive_relabelled_fixtures=1,paired_relabel_map_checked=True,precise_interface_corruptions=27,actual_saved_precise_corruptions=18,universal_statement_from_written_derivation=True,finite_controls_are_universal_proof=False))
  supplemental=dict(claim_id=CID,claim_revision=1,verifier='/root',method='independent_derivation',original_report_method=report['method'],method_projection_reason='Schema method records the independently written universal mathematical derivation. Original combined artifact-checking method is preserved verbatim and full raw counts remain explicit.',report=REPORT,report_sha256=REPORT_SHA,written_audit=PROOF,written_audit_sha256=PROOF_SHA,timestamp=report['timestamp'],outcome='PASS',scope='Complete universal conditional written C4-injection/target-count/character derivation, with every selected small raw fixture and saved negative checked independently.',inputs_sha256=report['inputs_sha256'],command=report['command'],cwd=report['cwd'],python=report['python'],shared_components=shared,independent_of_discovery_producer=True,external_review=False)
  binding=dict(id=CID,revision=1,claim_revision=1,kind='mathematical result',basis=['DERIVED'],status='VERIFIED',review_state='CLEAR',producer='/root/structural',verifier='/root',method='independent_derivation',statement=STATEMENT,scope=dict(description='Universal finite simple graph triangle-path double-fiber injection into induced four-cycles under exactly one common neighbor per adjacent pair, with conditional unrestricted target N5>=22869 and exact shifted degree5 character row. No existence, rank or exclusion conclusion.',unrestricted_target=True,target_resolution='NONE'),assumptions=['Finite simple graph with exactly one common neighbor for each adjacent pair; incidence contains every actual triangle once.','Target corollary additionally assumes the exact integer99vertex target identity; its existence remains UNKNOWN.','No automorphism, prism absence, rook absence, nonzero-kernel existence or upper-rank assumption.'],dependencies=[dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT',revision=1,relation='uses_result',reason='Only its pinned independently checked triangle-path inverse lemma (unique isolated support point, perfect-matching inverse, fiber multiplicity at most2) from written proof8844 is reused. The previous target lower12474 is not treated as the strengthened count.')],report=REPORT,report_sha256=REPORT_SHA,verification_timestamp=report['timestamp'],written_audit=PROOF,written_audit_sha256=PROOF_SHA,controls=controls,shared_components=shared,inputs_sha256=pins,supplemental_verification_records=[supplemental],mathematical_scope=dict(path_definition='Unordered three distinct actual triangles with pairwise intersection sizes0,1,1 and two distinct middle-triangle intersection points.',population_units='P counts unordered triangle paths; c4 counts induced four-vertex cycle sets; N5 counts distinct weight-five words in the binary triangle-incidence image.',character_definition='For n=|V|, C=ker_GF(2)(B^T), M=|C|, A_w=#weight-w words of C, K5(w)=sum_s(-1)^s binom(w,s)binom(n-w,5-s), with out-of-range binomials zero.',exact_character_implication='Let L=max(ceil(P/2),P-c4(G)). Then sum_(w>0) A_w*(L-K5(w)) <= binom(n,5)-L. For the target L=22869 and RHS71500275.',target_unordered_paths=24948,target_induced_c4s=2079,target_weight5_lower_count=22869,complete_character_coefficients=100,complete_normalized_weights=99),limitations=['Universal proof is the separate written inverse/injection/count/character derivation; finite fixtures challenge implementation and do not prove universality.','Conditional target count is necessary only; no rank bound, graph construction, rook exclusion, optimum or target nonexistence is asserted.','Metadata writer hashes immutable evidence; it does not rerun or approve discovery mathematics.','New exact ROOT-verifier/method/statement adapter and independent engineering review are required before registration; old N5 record is not replaced.','No external review, novelty or comprehensive literature-status assertion.'],unavailable_information=[dict(field='external_review',value=None,reason='No external review reported.'),dict(field='novelty',value=None,reason='No novelty audit performed.')],availability='LOCAL_ONLY',retrieval='Exact workspace paths and immutable independent raw report; publication has not been confirmed.',premise_state='UNKNOWN',target_resolution='NONE',created_at=now,updated_at=now,historical_protected_execution_state=protected,original_independent_report_method=report['method'],original_independent_report_statement_field='universal_statement',command=report['command'],cwd=report['cwd'],python=report['python'],source_commit_context=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_commit_limitation='New binding writer and working evidence are separately pinned; context HEAD is not claimed to contain every new file.')
  need(protected=={path:sha(ROOT/path)for path in protected},'PROTECTED_STATE_CHANGED');save(out/'claim_binding_schema2.json',binding)
  save(out/'summary.json',dict(status='METADATA_ONLY_C4_CLAIM_BINDING_SAVED',timestamp=now,author='/root/structural',claim_id=CID,claim_revision=1,binding_sha256=sha(out/'claim_binding_schema2.json'),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,mathematical_replays=0,ledger_mutations=0,index_mutations=0,scientific_launched=False,target_resolution='NONE',deadline=deadline.status()));print(json.dumps(dict(status='METADATA_ONLY_C4_CLAIM_BINDING_SAVED',binding_sha256=sha(out/'claim_binding_schema2.json'))))
 except BaseException as error:
  save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,protected_unchanged=protected=={path:sha(ROOT/path)for path in protected},outputs_preserved=True,mathematical_replays=0,ledger_mutations=0,index_mutations=0,deadline=deadline.status()));raise
if __name__=='__main__':main()
