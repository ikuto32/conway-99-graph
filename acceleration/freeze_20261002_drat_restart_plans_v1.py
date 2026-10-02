"""Freeze reviewable original-prefix preparation and gated derivative-solver plans.

No parser, solver, checker or scientific search is launched by this source.
Exact input hashing is included in its explicit command deadline.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

import native_20261002_exact_eight_budget_v1 as shared
from command_deadline import CommandDeadline

ROOT = shared.ROOT
BASE = 'acceleration/results/20260930_unrestricted_full99_cnf/'
ORIGINAL = {
    'original_cnf': dict(path=BASE+'instance.cnf', sha256='7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138', bytes=84919934),
    'original_partial_proof': dict(path='acceleration/results/20260930_unrestricted_native_pilot/main/proof.drat', sha256='11abdc29b502b8b09d4dc6ac3e9f03fa7ea8947496bc8e538a5043d113272f22', bytes=346616832),
    'historical_native_receipt': dict(path='acceleration/results/20260930_unrestricted_native_pilot/main/solver.receipt.json', sha256='9a6a2a0bbfb35d8ccbda9aa09e7a47522ec6fc3d7ad8c48e045d47bcc599686e', bytes=1555),
    'encoding_gate': dict(path='acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json', sha256='2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58', bytes=15962),
    'model': dict(path=BASE+'model.json', sha256='77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e', bytes=122319858),
    'scope': dict(path='acceleration/results/20260930_unrestricted_full99_preflight_v2/scope.json', sha256='2359c7389b4bb23475cf9607a99c07060119976abff8bc70bbdb5d131ab1921d', bytes=307524),
}
PROFILE = 'PINNED_BACKWARD_UNSAT_SINGLE_COPY_IGNORE_SMALL_DELETE_V1'


def authenticate(descriptor, pins, deadline):
    path = shared.repository_path(descriptor['path'])
    shared.pin(path, descriptor['sha256'], pins, deadline)
    shared.need(path.stat().st_size == descriptor['bytes'], 'exact frozen artifact length')
    return path


def fresh_descriptor(path, pins, deadline):
    path = path.resolve()
    shared.need(path.is_relative_to(ROOT) and path.is_file(), 'repository artifact identity')
    identity = shared.sha(path, deadline)
    pins[shared.key(path)] = identity
    return dict(path=shared.key(path), sha256=identity, bytes=path.stat().st_size)


def preparation(args, out, pins, deadline):
    for role in ['original_cnf', 'original_partial_proof', 'historical_native_receipt', 'encoding_gate']:
        authenticate(ORIGINAL[role], pins, deadline)
    plan = dict(schema='DRAT_RESTART_PREPARATION_PLAN_V1', created_at=shared.stamp(), source_commit=args.source_commit,
        question='Recover the exact candidate active clause multiset after complete records of the preserved300-second unrestricted proof prefix, without repeating native inference.',
        scope='Original normalized unrestricted full99 CNF; derivative records are syntactic candidate state until independently checked. Prefix RAT/RUP validity and equisatisfiability are UNKNOWN.',
        success_criterion='Produce complete derivative restart.cnf and retained_prefix.drat; preserve exact original bytes and receipt; account for every kept/dropped byte and clause occurrence; bounded resource stop and independently reconstruct full state before native use.',
        falsification_criterion='Any internal malformed record, variable outside original universe, multiplicity/deletion mismatch, non-tail byte alteration, incorrect timeout/profile/source binding, or incomplete independent state reconstruction vetoes compute use.',
        independent_verification_criterion='Different implementation reconstructs every original/retained-proof clause occurrence under the pinned profile and compares the whole active multiset and prefix bytes, with positive/corrupted controls. A later UNSAT requires complete independent combined-prefix+new-proof replay against original CNF, never derivative-only proof.',
        baseline_and_uncertainty='Historical300-second original attempt returnedUNKNOWN and preserved346,616,832 proof bytes. Extraction reads431,536,766 input bytes once; expected hundreds of MB to few GiB parser memory has not been measured. Compare measured cost/state size with a newly allocated1800-second base run; no calibrated success likelihood or speedup is claimed.',
        checker_profile=PROFILE, original_variables=1186500, original_clauses=4136454,
        proposed_allocation=dict(outer_seconds=960, producer_seconds=900, parser_seconds=800,
            address_space_bytes=8*1024**3, host_free_reserve_bytes=32*1024**3, ext4_free_reserve_bytes=8*1024**3,
            rationale='One exact linear scan/state update over84.9MB CNF+346.6MB partialDRAT, with time for output/hash/checkpointing; measured progress may justify an earlier stop.'),
        partial_tail_policy='Keep original partial trace immutable; derivative drops only final unterminated raw record. Preserve all prior proof bytes/pivots; explicitly account for optional LF after an already complete EOF record.',
        acceptance='Exact integers and bytes; parser success and UNKNOWN suffix give no mathematical exclusion.',
        status='CANDIDATE', review_state='NEEDS_RECHECK', rat_rup_checked=False, equisatisfiability_asserted=False,
        target_resolution=False, automatic_retry=False, automatic_resume=False,
        **{role: ORIGINAL[role] for role in ['original_cnf', 'original_partial_proof', 'historical_native_receipt', 'encoding_gate']})
    shared.save(out/'preparation_plan.json', plan)
    return plan


def derivative(args, out, pins, deadline):
    shared.need(args.preparation_summary and args.preparation_summary_sha256 and
                args.state_gate and args.state_gate_sha256, 'independent actual-state gate prerequisites')
    shared.pin(args.preparation_summary, args.preparation_summary_sha256, pins, deadline)
    shared.pin(args.state_gate, args.state_gate_sha256, pins, deadline)
    prepared = shared.read(args.preparation_summary)
    gate = shared.read(args.state_gate)
    shared.need(prepared['schema'] == 'DRAT_RESTART_PREPARATION_OUTPUTS_V1' and prepared['mode'] == 'prepare' and
                prepared['rat_rup_checked'] is False and prepared['equisatisfiability_asserted'] is False and
                len(prepared['records']) == 1, 'actual candidate preparation, not controls')
    shared.need(gate['status'] == 'INDEPENDENT_DRAT_RESTART_ARTIFACT_V1_PASS' and
                gate['complete_active_multiset_checked'] is True and gate['complete_prefix_bytes_checked'] is True and
                gate['variables_unchanged'] is True, 'full independent actual-state reconstruction before native use')
    record = prepared['records'][0]
    descriptors = {Path(row['path']).name: row for row in record['outputs']}
    shared.need(set(descriptors) == {'restart.cnf', 'retained_prefix.drat', 'parser_summary.json'}, 'exact derivative outputs')
    for descriptor in descriptors.values():
        authenticate(descriptor, pins, deadline)
        shared.need(gate['inputs_sha256'].get(descriptor['path']) == descriptor['sha256'], 'actual-state gate exact derivative bytes')
    for role in ['original_cnf', 'original_partial_proof', 'encoding_gate', 'model', 'scope']:
        authenticate(ORIGINAL[role], pins, deadline)
    for role in ['original_cnf', 'original_partial_proof']:
        descriptor = ORIGINAL[role]
        shared.need(gate['inputs_sha256'].get(descriptor['path']) == descriptor['sha256'], 'state gate original identity')
    parser = shared.read(ROOT/descriptors['parser_summary.json']['path'])
    shared.need(parser['variables'] == 1186500 and parser['original_clauses'] == 4136454 and
                parser['profile'] == PROFILE and parser['status'] == 'CANDIDATE_RESTART_STATE', 'same original-variable state')
    config = dict(native_seconds=args.native_seconds, producer_seconds=args.producer_seconds,
        shutdown_reserve_seconds=args.shutdown_reserve_seconds, address_space_bytes=args.native_address_space_bytes,
        proof_file_bytes=args.proof_file_bytes, seed=args.seed, conflict_limit=None,
        conflict_limit_null_reason='Continue from saved clauses without inheriting historicalone-million conflict cutoff; hard wall-time/resource guards and live reassessment remain.',
        host_free_reserve_bytes=32*1024**3, ext4_free_reserve_bytes=8*1024**3,
        aggregate_retained_artifact_bytes=8*1024**3)
    shared.need(0 < config['native_seconds'] and config['native_seconds']+config['shutdown_reserve_seconds'] < config['producer_seconds'] <= 21550,
                'explicit bounded derivative solver allocation')
    inputs = [dict(role=role, **descriptor) for role, descriptor in [
        ('cnf', descriptors['restart.cnf']), ('model', ORIGINAL['model']), ('scope', ORIGINAL['scope']),
        ('original_cnf', ORIGINAL['original_cnf']), ('original_partial_proof', ORIGINAL['original_partial_proof']),
        ('retained_prefix', descriptors['retained_prefix.drat']), ('transform_record', descriptors['parser_summary.json'])]]
    original_bindings = {ORIGINAL[role]['path']: ORIGINAL[role]['sha256'] for role in ['original_cnf', 'model', 'scope']}
    state_bindings = {descriptor['path']: descriptor['sha256'] for descriptor in
                      [ORIGINAL['original_cnf'], ORIGINAL['original_partial_proof'], *descriptors.values()]}
    plan = dict(schema='POLICY_NATIVE_SINGLE_PLAN_V2', created_at=shared.stamp(), source_commit=args.source_commit,
        question='Can a new bounded proof-producing native attempt resolve the exact candidate restart state extracted from the historical unrestricted full99 partialDRAT?',
        scope='Candidate derivative active-clause multiset in the unchanged1,186,500-variable universe. Original full99 encoding is independently checked; derivative equivalence and prefix RAT validity remainUNKNOWN. No automorphism assumption. A derivative result alone is not a Conway-99 resolution.',
        selection_rule='Use exactly the whole independently reconstructed active multiset of all complete records from the preserved original300-second trace; do not select favorable learned clauses or omit failed cases.',
        success_criterion='Preserve a complete decoded raw SAT assignment or a complete UNSAT proof suffix, exact derivative/prefix/original identities and contained stopping observation. Any target claim must pass the independently declared original-input checks.',
        falsification_criterion='Unknown/live process state, resource/deadline stop, corrupted transformed state, invalid full combined proof, or SAT assignment failing original CNF/complete99 matrix vetoes promotion.',
        independent_verification_criterion='UNSAT: byte-authenticated retained-prefix+new-suffix complete DRAT replay against original full99 CNF, plus its independent encoding/normalization coverage. SAT: independently satisfy original CNF, decode full99 adjacency and check integer SRG identity. State gate checks syntax/multiset only; prefix validity remains explicit.',
        allocation_reason='A1800-second continuation can retain useful historicallearned clause state rather than repeating300seconds of inference. Actual extraction size/cost and native CPU/RSS/proof growth guide reassessment; reserve150seconds for possible2GiB transfer/hashing. This is not a calibrated success probability.',
        numerical_acceptance='EXACT_INTEGER_CNF_AND_RAW_PROOF_OR_COMPLETE_ASSIGNMENT',
        baseline_and_uncertainty='Original300-second attempt wasUNKNOWN with346.6MB incomplete trace. Fresh state reconstruction must complete before execution. Hard restart loses decision trail/activity/reconstruction witnesses and may be slower; any observed improvement is empirical, not a performance guarantee.',
        variables=parser['variables'], clauses=parser['active_clause_occurrences'], inputs=inputs,
        mathematical_gates=[dict(path=ORIGINAL['encoding_gate']['path'], sha256=ORIGINAL['encoding_gate']['sha256'],
            expected_status='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS', required_input_bindings=original_bindings,
            exact_scope='Original CNF/model/scope only; this historical gate does not bind or approve derivativeCNF.'),
            dict(path=shared.key(args.state_gate), sha256=args.state_gate_sha256,
            expected_status='INDEPENDENT_DRAT_RESTART_ARTIFACT_V1_PASS', required_input_bindings=state_bindings,
            exact_scope='Complete syntactic state/prefix reconstruction only; no RAT/equisatisfiability assertion.')],
        configuration=config, mathematical_status='CANDIDATE', prefix_rat_rup_status='UNKNOWN',
        derivative_equisatisfiability_status='UNKNOWN', target_resolution=False, automatic_retry=False, automatic_resume=False)
    shared.save(out/'derivative_solver_plan.json', plan)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['preparation', 'derivative'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--allocation-reason', required=True)
    for field in ['preparation-summary', 'state-gate']:
        parser.add_argument('--'+field, type=Path)
        parser.add_argument('--'+field+'-sha256')
    parser.add_argument('--native-seconds', type=float, default=1800)
    parser.add_argument('--producer-seconds', type=float, default=2050)
    parser.add_argument('--shutdown-reserve-seconds', type=float, default=150)
    parser.add_argument('--native-address-space-bytes', type=int, default=8*1024**3)
    parser.add_argument('--proof-file-bytes', type=int, default=2*1024**3)
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()
    shared.need(re.fullmatch('[0-9a-f]{40}', args.source_commit), 'explicit source commit')
    deadline = CommandDeadline(args.seconds, allocation_reason=args.allocation_reason)
    out = args.out.resolve()
    shared.need(out.is_relative_to(ROOT), 'existing repository immutable plan outputs')
    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    try:
        for path in [Path(__file__), *shared.CODE]:
            pins[shared.key(path)] = shared.sha(path, deadline)
        plan = preparation(args, out, pins, deadline) if args.mode == 'preparation' else derivative(args, out, pins, deadline)
        name = 'preparation_plan.json' if args.mode == 'preparation' else 'derivative_solver_plan.json'
        shared.save(out/'summary.json', dict(schema='DRAT_RESTART_PLAN_FREEZE_V1', timestamp=shared.stamp(),
            mode=args.mode, command=[sys.executable, *sys.argv], cwd=str(ROOT), source_commit=args.source_commit,
            inputs_sha256=pins, plan_path=shared.key(out/name), plan_sha256=shared.sha(out/name, deadline),
            plan_status='CANDIDATE', native_solver_calls=0, parser_calls=0, independent_approval=False,
            target_resolution=False, elapsed_seconds=deadline.status()['elapsed_seconds']))
        print(json.dumps(dict(plan_path=shared.key(out/name), plan_sha256=shared.sha(out/name, deadline))), flush=True)
    except BaseException as error:
        shared.save(out/'failure.json', dict(timestamp=shared.stamp(), error=repr(error), native_solver_calls=0,
            parser_calls=0, target_resolution=False, unfinished_description='not completed within the allocated budget'))
        raise


if __name__ == '__main__':
    main()
