"""Narrow metadata bindings of an independently checked exact dual and consequence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20261003_independent_review/incidence_code_dual_full01'
REPORT=BASE/'summary.json'
REPORT_SHA='ca60194f888e4aa8f97792e26e7196b09ac720e4dd683c479a22faf8f4a8a816'
CAL=ROOT/'acceleration/results/20261003_independent_review/incidence_code_dual_calibration01/summary.json'
CAL_SHA='ddc4e106ac0cd8bb504e3514f0d330162aa41d0e9bd773039436736500cd2342'
RUN=ROOT/'acceleration/results/20261003_incidence_code_lp02'
GRIESMER=ROOT/'acceleration/results/20261003_independent_review/incidence_griesmer01/claim_binding.json'
GRIESMER_SHA='4e018e2be2705f4684b31266797571d0eaab1eeb5ce15603d4765a77265e4848'

def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')

def main():
    need(sha(REPORT)==REPORT_SHA and sha(CAL)==CAL_SHA and sha(GRIESMER)==GRIESMER_SHA,'Exact independent result/preoutput calibration/weight derivation binding')
    report=json.loads(REPORT.read_bytes());cal=json.loads(CAL.read_bytes());producer=json.loads((RUN/'summary.json').read_bytes())
    need(report['status']=='INDEPENDENT_INCIDENCE_CODE_COMPLETE_DUAL_V1_PASS'and report['producer']=='/root'and report['verifier']=='/root/structural','Independent producer/verifier roles')
    need((report['complete_coefficients_checked'],report['complete_nonnegative_dual_coordinates_checked'],report['complete_weight_inequalities_checked'],report['maximum_linear_dimension'],report['conditional_incidence_rank_lower'])==(1287,99,13,23,76),'Narrow complete recorded scope')
    pins={**report['inputs_sha256'],**cal['inputs_sha256']}
    folders=[BASE,CAL.parent,RUN,ROOT/'acceleration/results/20261003_incidence_code_lp01',ROOT/'acceleration/results/20261003_incidence_code_lp_supervision01',ROOT/'acceleration/results/20261003_incidence_code_lp_supervision02',ROOT/'acceleration/results/20261003_independent_review/incidence_code_dual_calibration_supervision01',ROOT/'acceleration/results/20261003_independent_review/incidence_code_dual_full_supervision01']
    for folder in folders:
        need(folder.is_dir(),'Preserved evidence folder '+str(folder))
        for path in folder.rglob('*'):
            if path.is_file():pins[path.relative_to(ROOT).as_posix()]=sha(path)
    for path in [Path(__file__),GRIESMER,ROOT/'acceleration/audit_20261003_incidence_griesmer_v1.md',ROOT/'acceleration/theory_20261003_incidence_code_lp_v1.py',ROOT/'acceleration/theory_20261003_incidence_code_lp_v1_spec.md',ROOT/'acceleration/run_compute_command.py']:
        pins[path.relative_to(ROOT).as_posix()]=sha(path)
    for name,expected in pins.items():need(sha(ROOT/name)==expected,'Exact identity authentication '+name)
    now=datetime.now(timezone.utc).isoformat()
    common=dict(revision=1,claim_revision=1,kind='mathematical result',status='VERIFIED',review_state='CLEAR',created_at=now,updated_at=now,producer='/root',verifier='/root/structural',verification_timestamp=report['timestamp'],source_commit=producer['source_commit'],source_commit_role='Actual numerical producer base commit, with new working source bytes separately hash pinned; Git presence is not inferred.',command=report['command'],cwd=report['cwd'],report=REPORT.relative_to(ROOT).as_posix(),report_sha256=REPORT_SHA,pre_output_calibration=CAL.relative_to(ROOT).as_posix(),pre_output_calibration_sha256=CAL_SHA,inputs_sha256=pins,shared_components=report['shared_components'],exact_size_upper=report['exact_size_upper'],maximum_linear_dimension=23,conditional_incidence_rank_lower=76,optimum_asserted=False,rank_upper_assumed=False,target_resolution='NONE',novelty=None,novelty_null_reason='No novelty audit or general literature-status search was performed.',external_review=None,external_review_null_reason='Internal independent artifact and written derivation checks only; external/peer review is not recorded.',verifier_tool_versions=None,verifier_tool_versions_null_reason='Original independent report records executable and locked environment hashes but no exact runtime version strings; none are invented.',producer_tool_versions=dict(python=producer['python'],highspy=producer['highspy'],numpy=producer['numpy']),availability='LOCAL_ONLY',retrieval='Complete99-coordinate rational dual,13x99 exact model, positive/corrupted controls, written character derivation, preserved V1 failure and V2 actual receipts are at bound repository paths; public package status is separately maintained.',failed_producer_attempt=dict(scope='Earlier V1 attempt exited before numerical run at non-OK passModel assertion; failed controls/exact model/source/receipt bytes are preserved.',result='FAILED_BEFORE_NUMERICAL_GUIDE',refuted=False,original_non_OK_status=None,original_non_OK_status_null_reason='V1 did not save the returned passModel status; no value is invented.'),metadata_only=True,writer_source_sha256=sha(Path(__file__)),writer_command=[sys.executable,*sys.argv],ledger_mutations=0)
    code=dict(common,id='C-BINARY-CODE-LENGTH99-EVEN36TO60-RATIONAL-DUAL-SIZE-BOUND',basis=['DERIVED','COMPUTED'],method='independent_artifact_check',
        statement='For every binary linear code C of length99, including the zero code, whose nonzero Hamming weights are contained in{36,38,40,42,44,46,48,50,52,54,56,58,60}, its cardinality is at most86920436866892624754510357784136/6261965357389189817043215, strictly less than2^24, and therefore dim(C)<=23. This exact upper bound follows from the pinned complete rational MacWilliams-character dual and does not assert optimality.',
        scope=dict(description='Universal binary linear code statement on one precise length/allowed-weight domain. Independent character derivation establishes interpretation; full rational artifact checking supplies one exact bound. No target incidence hypothesis is needed for this code theorem.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['C is a binary linear code of length99; every nonzero word has one of the13 stated even weights.','No minimum dimension, rank upper bound, incidence structure or automorphism is assumed.'],dependencies=[],
        written_derivation=report['written_derivation'],recorded_validation=dict(complete_model_coefficients=1287,nonnegative_rational_dual_coordinates=99,full_weight_inequalities=13,exact_power_of_two_comparison=True,preoutput_small_character_checks=140,preoutput_positive_fixtures=5,preoutput_strict_negative_controls=7,actual_strict_corruption_controls=4),
        limitations=['A feasible exact rational dual is enough; numerical truncated coefficients and solver status are not mathematical evidence. The independent checker uses every full exact coefficient.','The bound is an upper bound on size, not a construction, an optimal code bound or a graph nonexistence theorem.','Weight and length assumptions are part of the quantified statement; no hypothetical target is assumed to exist.','Metadata writer adds no new mathematical check; status refers to the separate completed checker and written derivation.'])
    save(BASE/'code_size_claim_binding.json',code)
    rank=dict(common,id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER76',basis=['DERIVED'],method='independent_derivation',
        statement='For every99x99 binary symmetric zero-diagonal matrix A satisfying A^2=12I-A+2J exactly over the integers, let B be the99x231 binary vertex-by-triangle incidence matrix containing every actual triangle exactly once. Then rank_GF(2)(B)>=76, equivalently dim_GF(2)ker(B^T)<=23. This conditional implication establishes neither existence nor nonexistence of such A.',
        scope=dict(description='Universal conditional rank lower bound for the unrestricted target. Its triangle-kernel even-weight36..60 premise is separately independently derived, then the exact generic code bound and rank-nullity are applied.',unrestricted_target=True,target_resolution='NONE'),
        assumptions=['The exact target integer identity, binary/symmetric/zero-diagonal domain and complete literal triangle incidence hold; existence of such A is UNKNOWN.','No automorphism, prism-absence condition, lower kernel dimension or rank upper bound is assumed.'],
        dependencies=[dict(id='C-BINARY-CODE-LENGTH99-EVEN36TO60-RATIONAL-DUAL-SIZE-BOUND',revision=1,relation='uses_result',reason='The exact code-size bound gives kernel dimension at most23.'),dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67',revision=1,relation='uses_result',reason='ONLY the independently established even kernel-weight36..60 derivation in its pinned written proof is reused; the numerical rank67 conclusion is not the premise of rank76.')],
        premise_state='UNKNOWN',written_derivation=report['written_derivation'],weight_premise_written_audit='acceleration/audit_20261003_incidence_griesmer_v1.md',
        recorded_validation=dict(weight_derivation='Target edge-unique triangles give7-regular support, exact outside first/second moments and integer Cauchy interval36..60; separate written ROOT audit and calibrated complete rook fixture.',code_bound_application='Complete independent exact dual impliesdim(kernel)<=23; binary rank-nullity gives99-23=76.',rank_upper_bound_assumed=False),
        limitations=['Conditional implication only; a lower rank bound supplies no contradiction or target result.','The separately refuted generic codomain-isotropy upper-rank lemma is not a dependency or premise.','The code-size bound and weight-premise proof have separate precise scopes; finite calibration alone is not the universal proof.','No novelty, external review or target-wide graph-coverage measure is established.','Metadata writer adds no new mathematical check; status refers to the separate completed checker and written derivation.'])
    save(BASE/'incidence_rank_claim_binding.json',rank)
    save(BASE/'binding_identities.json',dict(code_size_binding_sha256=sha(BASE/'code_size_claim_binding.json'),incidence_rank_binding_sha256=sha(BASE/'incidence_rank_claim_binding.json'),report_sha256=REPORT_SHA,metadata_only=True,ledger_mutations=0))

if __name__=='__main__':main()
