"""Metadata-only exact-r1 binding after separate universal/raw verification."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/record_20261003_triangle_image_weight5_binding_v1.py'
SPEC = 'acceleration/record_20261003_triangle_image_weight5_binding_v1_spec.md'
CLAIM = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT'
REPORT = 'acceleration/results/20261003_independent_review/weight5_full02/summary.json'
REPORT_SHA = 'dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2'
CAL = 'acceleration/results/20261003_independent_review/weight5_calibration01/summary.json'
CAL_SHA = 'f8d31fdbdafc31314d79b3be1e17934477dcd65286f07ab5e28ace9d8423c99a'
PROOF = 'acceleration/audit_20261003_triangle_image_weight5_v1_proof.md'
PROOF_SHA = '8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee'
DIRECT_DIRS = [
    'acceleration/results/20261003_triangle_image_weight5_controls01',
    'acceleration/results/20261003_triangle_image_weight5_controls_supervision01',
    'acceleration/results/20261003_independent_review/weight5_calibration01',
    'acceleration/results/20261003_independent_review/weight5_calibration_supervision01',
    'acceleration/results/20261003_independent_review/weight5_full01',
    'acceleration/results/20261003_independent_review/weight5_full_supervision01',
    'acceleration/results/20261003_independent_review/weight5_full02',
    'acceleration/results/20261003_independent_review/weight5_full_supervision02',
]


def need(value, diagnostic):
    if not value:
        raise ValueError(diagnostic)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact-r1 metadata binding from preserved universal/raw checks;20save reserve,no math replay or ledger/index mutation')
    out = (ROOT / args.out).resolve()
    need(out.is_relative_to(ROOT), 'Workspace output')
    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    def pin(name, wanted=None):
        need(deadline.status()['remaining_seconds'] > 20, 'Metadata serialization reserve')
        h = sha(ROOT / name)
        need(wanted is None or h == wanted, 'Exact recorded identity ' + name)
        pins[name] = h
        return h
    try:
        protected = {name: sha(ROOT / name) for name in ['CLAIMS.yaml', '.git/index']}
        pin(REPORT, REPORT_SHA)
        pin(CAL, CAL_SHA)
        pin(PROOF, PROOF_SHA)
        report = json.loads((ROOT / REPORT).read_bytes())
        cal = json.loads((ROOT / CAL).read_bytes())
        need(report['status'] == 'INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS'
             and report['verifier'] == '/root/checkpoint_audit' and report['producer'] == '/root/structural'
             and report['method'] == 'independent_derivation' and report['universal_derivation_checked'] is True,
             'Separate actual theorem/raw verification')
        need((report['positive_fixtures'], report['complete_triangle_combinations'],
              report['unordered_fixture_paths'], report['distinct_separate_fixture_path_words'],
              report['complete_small_image_coefficient_masks'], report['actual_saved_strict_negative_controls'])
             == (7,62,23,14,234,17), 'Exact independently checked finite populations')
        need(report['target_unordered_paths'] == 24948 and report['target_weight5_lower_count'] == 12474
             and report['character_normalization']['denominator'] == 71510670
             and report['new_exclusions'] == 0 and report['rank_bound_claimed'] is False
             and report['target_resolution'] == 'NONE', 'Exact lower bound/no target promotion')
        need(cal['positive_fixtures'] == 7 and cal['strict_negative_controls'] == 21
             and cal['producer_outputs_checked'] is False, 'Separate pre-full calibration')
        for evidence in [cal, report]:
            for name, h in evidence['inputs_sha256'].items():
                need(name not in pins or pins[name] == h, 'Consistent evidence closure')
                pin(name, h)
        for name in [SOURCE, SPEC, 'docs/COMPUTE_POLICY.md', 'acceleration/compute_policy.json']:
            pin(name)
        for directory in DIRECT_DIRS:
            for path in sorted((ROOT / directory).rglob('*')):
                if path.is_file():
                    pin(path.relative_to(ROOT).as_posix())
        now = datetime.now(timezone.utc).isoformat()
        observations = dict(role='Protected before/after metadata execution state; not immutable theorem dependencies',
                            sha256=protected, unchanged_during_command=True)
        verification_details = [
            dict(claim_id=CLAIM, claim_revision=1, verifier='/root/checkpoint_audit',
                 method='independent_derivation', audit_path=REPORT, audit_sha256=REPORT_SHA,
                 written_audit=PROOF, written_audit_sha256=PROOF_SHA, timestamp=report['timestamp'],
                 outcome='PASS', scope='Complete universal triangle-path inverse and exact target character inequality; all seven frozen tiny raw fixtures checked separately',
                 command=report['command'], cwd=report['cwd'], python=report['python'],
                 artifact_hashes=report['inputs_sha256'], shared_components=report['shared_components']),
            dict(claim_id=CLAIM, claim_revision=1, verifier='/root/checkpoint_audit',
                 method='independent_artifact_check', audit_path=CAL, audit_sha256=CAL_SHA,
                 timestamp=cal['timestamp'], outcome='PASS', scope='Seven independent positive fixtures and21 precise corrupted checking controls; producer output not inspected',
                 command=cal['command'], cwd=cal['cwd'], python=cal['python'],
                 artifact_hashes=cal['inputs_sha256'], shared_components=cal['shared_components']),
        ]
        binding = dict(id=CLAIM, revision=1, claim_revision=1, kind='mathematical result',
                       basis=['DERIVED'], status='VERIFIED', review_state='CLEAR',
                       statement=report['statement'],
                       scope=dict(description='Universal necessary triangle-path weight5 image lower bound under adjacent-pair common-neighbor uniqueness, with unrestricted Conway99 conditional corollary and exact all-weight character inequality. No existence, rank or exclusion conclusion.',
                                  unrestricted_target=True, target_resolution='NONE'),
                       assumptions=['Finite simple graph; every adjacent pair has exactly one common neighbor; B contains every actual triangle once.',
                                    'The target corollary assumes a complete binary symmetric zero-diagonal99x99 adjacency matrix satisfying A^2=12I-A+2J exactly. Target existence remains UNKNOWN; no automorphism, prism, fixed-profile or rank upper-bound assumption.'],
                       dependencies=[], producer='/root/structural', verifier='/root/checkpoint_audit',
                       method='independent_derivation', verification_timestamp=report['timestamp'],
                       report=REPORT, report_sha256=REPORT_SHA, written_audit=PROOF,
                       written_audit_sha256=PROOF_SHA, created_at=now, updated_at=now,
                       source_commit=report['source_commit_context'],
                       source_commit_role='Actual saved producer/checker context; new source/proof bytes are independently hash-pinned and may have been uncommitted in that context.',
                       inputs_sha256=pins, command=report['command'], working_directory=report['cwd'],
                       tool_versions=dict(python=report['python'], dependency_lock='uv.lock'),
                       controls=dict(pre_full=dict(path=CAL,sha256=CAL_SHA,positive_fixtures=7,strict_negative_controls=21,producer_outputs_inspected=False),
                                     actual_raw=dict(path=REPORT,sha256=REPORT_SHA,positive_fixtures=7,complete_three_triangle_combinations=62,unordered_paths=23,separate_fixture_supports=14,complete_small_image_coefficient_masks=234,saved_strict_negative_controls=17,
                                                     every_inverse_fiber_checked=True,actual_k7_three_intersection_paths_checked=True)),
                       recorded_validation=dict(universal_written_inverse=True,finite_agreement_used_as_universal_proof=False,
                                                character_orthogonality_and_zero_constant_rederived=True,target_unordered_paths=24948,target_weight5_lower_count=12474,
                                                exact_character_denominator=71510670,complete_normalized_weights=99,new_exclusions=0),
                       supplemental_verification_records=verification_details,
                       shared_components=report['shared_components'], limitations=report['limitations'],
                       target_resolution='NONE', premise_state='UNKNOWN', rank_bound_claimed=False,
                       definitions=dict(P='sum_{t in complete actual T} sum_{unordered{u,v}subset t}(r_u-1)(r_v-1)',
                                        B='Binary vertex-by-complete-actual-triangle incidence matrix',
                                        C='ker_GF2(B transpose)', A_w='Number of C words of Hamming weightw',
                                        K5='sum_{s=0}^5(-1)^s binom(w,s)binom(n-w,5-s), out-of-range binomials zero',
                                        zero_word_convention='M=1+sum_{w>0}A_w; shifted RHS=binom(n,5)-lower_count includes A0=1'),
                       known_failed_attempt=dict(path='acceleration/results/20261003_independent_review/weight5_full01/failure.json',
                                                 scope='Identity-stage veto before raw reconstruction: message-copied producer hash had65rather than64hex; unchanged source succeeded only in separately authorizedfull02',
                                                 mathematical_refutation=False),
                       availability='LOCAL_ONLY', retrieval='Exact repository workspace paths and saved commands; public replay availability requires separate immutable publication confirmation.',
                       unavailable_information=dict(external_review=None,external_review_reason='No external peer review recorded',
                                                    novelty=None,novelty_reason='No target-wide literature/novelty audit',
                                                    formalization=None,formalization_reason='Written complete proof and exact finite checking; no proof-assistant artifact',
                                                    random_seed=None,random_seed_reason='Deterministic complete tiny enumerations; no random generation',
                                                    cpu_model=None,cpu_model_reason='Not captured for these bounded tiny exact checks; no performance claim'),
                       historical_protected_execution_state=observations, metadata_only=True,
                       writer_source_sha256=pins[SOURCE], writer_command=[sys.executable,*sys.argv],
                       ledger_mutations=0,index_mutations=0,mathematical_replays=0,scientific_invocations=0)
        save(out / 'claim_binding_schema2.json', binding)
        need(all(sha(ROOT / name) == h for name,h in protected.items()), 'Protected ledger/index unchanged')
        save(out / 'summary.json', dict(status='EXACT_WEIGHT5_PATH_LOWER_COUNT_R1_BINDING_RECORDED',
                                       timestamp=now,claim_id=CLAIM,claim_revision=1,
                                       binding_sha256=sha(out/'claim_binding_schema2.json'),
                                       report_sha256=REPORT_SHA,full_direct_input_records=len(pins),
                                       ledger_mutations=0,index_mutations=0,mathematical_replays=0,
                                       scientific_invocations=0,python=platform.python_version(),
                                       deadline=deadline.status()))
        print('EXACT_WEIGHT5_PATH_LOWER_COUNT_R1_BINDING_RECORDED')
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,
                                    mathematical_replays=0,ledger_mutations=0,index_mutations=0,
                                    deadline=deadline.status()))
        raise


if __name__ == '__main__':
    main()
