"""Metadata-only rank86 binding V2; preserved V1 never executed."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SPEC = 'acceleration/record_20261003_triangle_rank86_binding_v2_spec.md'
REPORT = 'acceleration/results/20261003_independent_review/four_counts_lp_even13_full01/summary.json'
REPORT_SHA = '3cc0ae7fbd0d340c00a4b1e3b00221ef70df6767812b846875a9483413745674'
CAL = 'acceleration/results/20261003_independent_review/four_counts_lp_calibration01/summary.json'
CAL_SHA = '15a870349f39da25ff53da630ab2850076aad7fca6efebeafdae13c0f08a888e'
PROOF = 'acceleration/audit_20261003_triangle_kernel_four_counts_lp_v3.md'
PROOF_SHA = '17662bc4c8d63fb56bf6b64fd59bfe1509064a11c06279f9a40ba5a4869f9c54'
PRESERVED = [
    'acceleration/record_20261003_triangle_rank86_binding_v1.py',
    'acceleration/record_20261003_triangle_rank86_binding_v1_spec.md',
    'acceleration/results/20261003_incidence_four_low_counts_plan01/plan.json',
    'acceleration/results/20261003_incidence_four_low_counts_plan02/failure.json',
    'acceleration/results/20261003_incidence_four_low_counts_plan03/plan.json',
    'acceleration/results/20261003_incidence_four_low_counts_plan03/calibration_count_deviation.json',
    'acceleration/results/20261003_incidence_four_low_counts_guide_plan04/plan.json',
    'acceleration/results/20261003_incidence_four_low_counts_guide_plan04/resources.json',
    'acceleration/results/20261003_incidence_four_counts_even13_admission01/admission.json',
]
FOLDERS = [
    'acceleration/results/20261003_incidence_four_counts_even13_guide01',
    'acceleration/results/20261003_incidence_four_counts_even13_guide_supervision01',
    'acceleration/results/20261003_incidence_four_counts_even13_controls01',
    'acceleration/results/20261003_incidence_four_counts_even13_controls_supervision01',
    'acceleration/results/20261003_independent_review/four_counts_lp_even13_full01',
    'acceleration/results/20261003_independent_review/four_counts_lp_calibration01',
]


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    deadline = CommandDeadline(a.seconds, allocation_reason='Metadata authentication only; no mathematical replay, solver or live registry mutation')
    before = {path: sha(ROOT / path) for path in ['CLAIMS.yaml', '.git/index']}
    out = a.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_WORKSPACE_OUTPUT')
    out.mkdir(parents=True)
    pins = {REPORT: REPORT_SHA, CAL: CAL_SHA, PROOF: PROOF_SHA}
    need(all(sha(ROOT / path) == expected for path, expected in pins.items()), 'EXACT_ROOT_REPORT_CAL_PROOF_IDENTITIES')
    report = json.loads((ROOT / REPORT).read_bytes())
    cal = json.loads((ROOT / CAL).read_bytes())
    need(report['status'] == 'INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_COMPLETE_DUAL_V2_PASS'
         and report['weight_domain'] == 'even13' and report['verifier'] == '/root'
         and report['producer'] == '/root/structural' and report['method'] == 'independent_artifact_check'
         and report['complete_exact_coefficients_checked'] == 1287
         and report['complete_nonnegative_dual_coordinates_checked'] == 99
         and report['complete_exact_weight_inequalities_checked'] == 13
         and report['exact_size_upper'] == [97502464, 9739]
         and report['maximum_linear_dimension'] == 13
         and report['conditional_incidence_rank_lower'] == 86
         and report['actual_strict_corruption_controls'] == 10
         and report['target_resolution'] == 'NONE' and report['optimum_asserted'] is False,
         'NARROW_ALREADY_CHECKED_ROOT_REPORT')
    need(cal['status'] == 'INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_LP_CHECKER_V2_CALIBRATION_PASS'
         and cal['complete_small_literal_coefficients'] == 140
         and cal['full_producer_output_inspected'] is False, 'PREOUTPUT_CALIBRATION_REPORT')
    for record in [report, cal]:
        for path, expected in record['inputs_sha256'].items():
            need(path not in pins or pins[path] == expected, 'CONSISTENT_EXACT_EVIDENCE')
            pins[path] = expected
    for path in PRESERVED + [SPEC, Path(__file__).relative_to(ROOT).as_posix()]:
        pins[path] = sha(ROOT / path)
    for folder in FOLDERS:
        for path in (ROOT / folder).rglob('*'):
            if path.is_file():
                rel = path.relative_to(ROOT).as_posix()
                pins[rel] = sha(path)
    producer = json.loads((ROOT / 'acceleration/results/20261003_incidence_four_counts_even13_guide01/summary.json').read_bytes())
    for path, expected in producer['inputs_outputs_sha256'].items():
        need(path not in pins or pins[path] == expected, 'CONSISTENT_PRODUCER_RECORD')
        pins[path] = expected
    for path, expected in pins.items():
        need(path not in ['CLAIMS.yaml', '.git/index'] and not Path(path).is_absolute() and '..' not in Path(path).parts,
             'IMMUTABLE_EVIDENCE_NAMESPACE')
        need(sha(ROOT / path) == expected and not deadline.status()['stop_required'], 'IDENTITY_OR_METADATA_DEADLINE:' + path)
    now = datetime.now(timezone.utc).isoformat()
    binding = dict(
        id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86', revision=1, claim_revision=1,
        kind='mathematical result', basis=['DERIVED', 'COMPUTED'], status='VERIFIED', review_state='CLEAR',
        producer='/root/structural', verifier='/root', method='independent_artifact_check',
        created_at=now, updated_at=now, verification_timestamp=report['timestamp'],
        statement='For every 99x99 symmetric binary zero-diagonal matrix A satisfying A^2=12I-A+2J exactly over the integers, let B be the 99x231 binary vertex-by-triangle incidence matrix containing each actual triangle once, and let C=ker_GF(2)(B^T). Then |C|<=97502464/9739<2^14, so dim_GF(2)(C)<=13 and rank_GF(2)(B)>=86. This is a conditional necessary implication and asserts neither existence nor nonexistence of A.',
        scope=dict(description='Unrestricted target necessary triangle-incidence kernel size/rank bound, using its even nonzero weights 36..60 and image counts N3>=231,N4>=2079,N5>=12474,N6>=24486. Exact even13 certificate; no generic binary-code application or divided-by-four weight premise.', unrestricted_target=True, target_resolution='NONE'),
        assumptions=['Exact integer target identity and complete actual triangle incidence; target existence remains UNKNOWN.',
                     'The independently derived nonzero kernel weights are even and in 36..60; independently established image lower counts and binary character normalization apply.',
                     'No nonzero-kernel existence, minimum kernel dimension, rank upper bound, automorphism, prism absence or fixed rooted configuration.'],
        dependencies=[
            dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67', revision=1, relation='uses_result', reason='Only its independently checked even nonzero kernel-weight interval 36..60 is reused; rank67 is not a premise.'),
            dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS', revision=1, relation='uses_result', reason='Independently established N3,N4,N6 and sharp character normalization; the selected dual has support only at degree4 and degree5, so its nontrivial image-count use is N4.'),
            dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT', revision=1, relation='uses_result', reason='Independently established target N5>=12474 and exact degree5 character row. The later candidate strengthened C4 collision count is not used.')],
        report=REPORT, report_sha256=REPORT_SHA, written_audit=PROOF, written_audit_sha256=PROOF_SHA,
        command=report['command'], cwd=report['cwd'], source_commit=producer['source_commit'],
        source_commit_role='Observed actual producer source context; new working producer/checker/writer sources separately hash-pinned, not asserted committed.',
        exact_certificate=dict(path='acceleration/results/20261003_incidence_four_counts_even13_guide01/certificate.json',
                              sha256=pins['acceleration/results/20261003_incidence_four_counts_even13_guide01/certificate.json'],
                              upper=[97502464, 9739], nonzero_dual_by_degree={'4': [14631155, 9739], '5': [82861570, 9739]},
                              complete_dual_coordinates=99, complete_coefficients=1287, complete_weight_inequalities=13,
                              artifact_checked_by='/root', optimum_asserted=False),
        controls=dict(independent_preoutput=dict(report=CAL, sha256=CAL_SHA, literal_character_coefficients=140, known_rook_kernel_words=16,
                                                complete_selected_synthetic_coefficient_cells_both_domains=1980,
                                                actual_strict_corruptions=30, full_producer_output_inspected=False),
                      independent_actual=dict(report=REPORT, sha256=REPORT_SHA, actual_strict_corruptions=10),
                      author=dict(positive_exact_fixtures=2, actual_literal_character_coefficients=139, actual_strict_corruptions=12,
                                  declared_literal_character_coefficients=140, declaration_deviation='acceleration/results/20261003_incidence_four_low_counts_plan03/calibration_count_deviation.json',
                                  author_controls_are_independent_approval=False)),
        supplemental_verification_records=[dict(claim_id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86', revision=1, claim_revision=1,
                                   verifier='/root', producer='/root/structural', method='independent_artifact_check', timestamp=report['timestamp'],
                                   outcome='PASS', report=REPORT, report_sha256=REPORT_SHA,
                                   inputs_sha256=report['inputs_sha256'], command=report['command'], cwd=report['cwd'],
                                   versions=dict(python=report['python'], checker_implementation_version=report['checker_implementation_version'], gate_interface_version=report['gate_interface_version'],
                                                 producer_python=producer['python'], highspy=producer['highspy'], numpy=producer['numpy'], environment='uv.lock exact hashed dependency pins'),
                                   shared_components=report['shared_components'], independent_of_discovery_producer=True, external_review=False,
                                   scope='Selected complete even13 exact dual and conditional character derivation; all1287cells/99coordinates/13inequalities and10actual corruption controls.',
                                   artifact_hashes=dict(exact_model=pins['acceleration/results/20261003_incidence_four_counts_even13_guide01/exact_model.json'],
                                                        complete_dual=pins['acceleration/results/20261003_incidence_four_counts_even13_guide01/certificate.json']))],
        shared_components=report['shared_components'] + ['Producer uses original binomial sums and HiGHS as a floating guide; ROOT verifier uses separately authored polynomial products and exact rational checks, with no producer or optimizer import.', 'Shared Python integer/Fraction runtime and command_deadline helper are disclosed in pinned records.'],
        limitations=['Conditional necessary bound only; no target solution, general nonexistence, optimum, upper rank, nonzero-kernel existence or external acceptance.',
                     'All three frozen author rational lifts were saved; this claim promotes only the selected dual actually checked by ROOT.',
                     'The separate seven-weight domain reproduced the same bound but is not a premise or extra contribution to this claim.',
                     'Author protocol140 versus actual139 controls is preserved; ROOT independently covered140 including the missing zero-length boundary case.',
                     'Dependencies include the standalone N5 claim binding; ROOT must register dependencies before actual ledger insertion.'],
        availability='LOCAL_ONLY', retrieval='Pinned local repository paths; public availability is separate and no publication is asserted.',
        premise_state='UNKNOWN', target_resolution='NONE', novelty=None, novelty_null_reason='No comprehensive novelty audit.',
        external_review=None, external_review_null_reason='Internal independent checking only.', formalization=None,
        formalization_null_reason='Exact rational artifacts and ordinary complete written derivation; no proof-assistant artifact.',
        inputs_sha256=dict(sorted(pins.items())), metadata_only=True, mathematical_replays=0, scientific_invocations=0,
        ledger_mutations=0, index_mutations=0, writer_command=[sys.executable, *sys.argv], writer_source_sha256=sha(Path(__file__)),
        historical_protected_execution_state=dict(sha256=before, role='Read-only metadata observation; not theorem dependencies.'),
    )
    need(before == {path: sha(ROOT / path) for path in before}, 'NO_LIVE_LEDGER_OR_INDEX_CHANGE_DURING_METADATA')
    save(out / 'claim_binding_schema2.json', binding)
    save(out / 'summary.json', dict(status='METADATA_ONLY_RANK86_BINDING_SAVED', timestamp=now,
                                   binding_sha256=sha(out / 'claim_binding_schema2.json'), exact_authenticated_evidence=len(pins),
                                   mathematical_replays=0, ledger_mutations=0, index_mutations=0, deadline=deadline.status()))
    print(json.dumps(dict(binding_sha256=sha(out / 'claim_binding_schema2.json'), evidence=len(pins), metadata_only=True)))


if __name__ == '__main__':
    main()
