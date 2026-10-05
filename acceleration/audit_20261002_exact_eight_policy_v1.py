"""Independent new native-driver calibration and complete exact-eight proof audit v1."""
from __future__ import annotations

import argparse
import ast
import copy
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline
import audit_20261002_policy_drat_core_v1 as core

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / 'acceleration/native_20261002_exact_eight_budget_v1.py'
SPEC = DRIVER.with_name(DRIVER.stem + '_spec.md')
ENV = ROOT / 'acceleration/native_budget_env_v1'
NATIVE = ROOT / 'build/research-cadical195/source/build/cadical'
NATIVE_SHA = '021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'
CODE = [DRIVER, SPEC, ROOT / 'acceleration/command_deadline.py', ROOT / 'acceleration/run_compute_command.py', ENV / 'pyproject.toml', ENV / 'uv.lock']
LIMITS = {'address_space_bytes': 4294967296, 'proof_file_bytes': 268435456, 'conflicts_per_attempt': 1000000, 'seed': 0, 'kill_grace_seconds': 5, 'aggregate_retained_artifact_bytes': 68719476736, 'next_attempt_artifact_reserve_bytes': 1073741824, 'host_free_reserve_bytes': 34359738368, 'ext4_free_reserve_bytes': 2147483648, 'maximum_cases': 64, 'sequential': True, 'automatic_retry': False, 'automatic_resume': False}
CLAIM = 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-LITERAL-PROFILE-EXCLUSIONS'


def unique_pairs(pairs):
    data = {}
    for name, value in pairs:
        core.require(name not in data, 'duplicate JSON key ' + name)
        data[name] = value
    return data


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs)


def path(name):
    core.require(isinstance(name, str) and name and '\\' not in name, 'literal POSIX artifact path')
    rel = Path(name)
    core.require(not rel.is_absolute() and '..' not in rel.parts, 'repository artifact path')
    p = (ROOT / name).resolve()
    core.require(p.is_relative_to(ROOT) and core.key(p) == name, 'canonical repository artifact path')
    return p


def linux(p):
    return '/mnt/' + str(p.resolve())[0].lower() + str(p.resolve())[2:].replace('\\', '/')


def same_json(left, right):
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def check_assignment(text, variables, clauses):
    tokens = []
    for line in text.splitlines():
        if line.startswith('v '):
            tokens.extend(line.split()[1:])
    core.require(tokens and tokens[-1] == '0' and tokens.count('0') == 1, 'complete unique native assignment terminator')
    vals = [int(token) for token in tokens[:-1]]
    core.require(len(vals) == variables and {abs(value) for value in vals} == set(range(1, variables + 1)), 'complete exact native assignment')
    bits = {abs(value): value > 0 for value in vals}
    core.require(all(any(bits[abs(value)] == (value > 0) for value in row) for row in clauses), 'independent raw assignment satisfies every clause')
    return bits


def inspect_record(row, pin, mode, approved):
    pin(path(row['summary_path']), row['summary_sha256'])
    record = read(path(row['summary_path']))
    cid = record['case_id']
    core.require(cid == row['case_id'] and record['case_index'] == row['case_index'], 'summary exact case identity')
    core.require(record['native_calls'] == 1 and record['independent_approval'] is False and record['target_resolution'] is False, 'raw producer outcome unpromoted')
    formula = record['formula']
    descriptor = formula['files']['instance.cnf']
    cnf = path(descriptor['path'])
    pin(cnf, descriptor['sha256'])
    core.require(cnf.stat().st_size == descriptor['bytes'], 'actual CNF length')
    with cnf.open('rb') as stream:
        header = stream.readline().decode('ascii').strip().split()
    core.require(len(header) == 4 and header[:2] == ['p', 'cnf'], 'literal CNF header')
    variables, clauses = int(header[2]), int(header[3])
    if mode == 'proofs':
        expected = approved[cid]
        core.require(descriptor['path'] == expected['cnf_path'] and descriptor['sha256'] == expected['cnf_sha256'] and variables == expected['variables'] and clauses == expected['clauses'], 'launched exactly independently checked literal formula')
    pin(path(record['launch_path']), record['launch_sha256'])
    pin(path(record['native_receipt_path']), record['native_receipt_sha256'])
    launch = read(path(record['launch_path']))
    receipt = read(path(record['native_receipt_path']))
    core.require(same_json(receipt, record['native_receipt']), 'identical raw receipt embedded in case summary')
    core.require(launch['case_id'] == cid and launch['case_index'] == row['case_index'], 'launch exact identity')
    seconds = launch['native_wall_limit_seconds']
    core.require(isinstance(seconds, (int, float)) and 0 < seconds <= launch['requested_case_seconds'] and seconds == row['allocated_native_wall_seconds'], 'dynamic explicit per-case allocation')
    available = launch['deadline_before_launch']['remaining_seconds']
    core.require(seconds + 34.99 <= available and launch['deadline_before_launch']['stop_required'] is False, 'sub-allocation reserves same invocation deadline')
    expected_command = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{seconds:.6f}s', '/usr/bin/prlimit', '--as=4294967296:4294967296', '--fsize=268435456:268435456', '--core=0:0', linux(NATIVE), '--no-binary', '--seed=0', '-c', '1000000', linux(cnf), launch['ext4_proof']]
    core.require(receipt['command'] == launch['command'] == expected_command, 'exact policy-aware native command')
    core.require(receipt['limits'] == launch['limits'] == LIMITS, 'all exact declared resource limits')
    core.require(receipt['cwd'] == linux(ROOT), 'actual Linux workspace')
    core.require(receipt['reaped'] is True and receipt['processes_after']['zero_live_matching_observed'] is True and receipt['processes_after']['matching_processes'] == [], 'native solver actually reaped and matching process snapshot empty')
    core.require(receipt['producer_stop_reason'] is None, 'no unrecorded producer deadline stop')
    for field in ['stdout', 'stderr']:
        pin(path(receipt[field]), receipt[field + '_sha256'])
    text = path(receipt['stdout']).read_text(errors='replace')
    status = core.native_status(text, receipt['actual_exit_code'], variables, clauses)
    if status != 'UNKNOWN':
        core.require('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text.splitlines(), 'actual pinned native solver version')
        core.require("c setting conflict limit to 1000000 conflicts (due to '1000000')" in text.splitlines(), 'configured actual conflict cap')
    raw = record['raw_proof']
    proof = None
    if raw is not None:
        proof = path(raw['path'])
        pin(proof, raw['sha256'])
        core.require(raw['sha256'] == raw['source_sha256'] and raw['bytes'] == proof.stat().st_size and raw['bytes'] == row['ext4_trace_bytes'], 'whole saved proof byte identity')
        core.require(raw['linux_original_path'] == launch['ext4_proof'] and 0 <= raw['bytes'] <= LIMITS['proof_file_bytes'], 'actual native proof source and file cap')
    if status == 'UNSAT_COMPLETE_PROOF_PENDING':
        core.require(proof is not None and 0 < proof.stat().st_size < LIMITS['proof_file_bytes'] and row['interpreted_result'] == 'UNSAT_TRACE_PENDING_COMPLETE_REPLAY', 'complete trace required for UNSAT')
    elif status == 'SAT_COMPLETE_OBJECT_PENDING':
        core.require(row['interpreted_result'] == 'SAT_RAW_OBJECT_PENDING_REVIEW', 'SAT must remain object pending')
    else:
        core.require(row['interpreted_result'].startswith('UNKNOWN_'), 'UNKNOWN cannot promote')
    return {'case_id': cid, 'case_index': row['case_index'], 'cnf_path': core.key(cnf), 'cnf_sha256': descriptor['sha256'], 'variables': variables, 'clauses': clauses, 'proof_path': core.key(proof) if proof else None, 'proof_sha256': raw['sha256'] if raw else None, 'proof_bytes': raw['bytes'] if raw else None, 'native_status': status, 'receipt_path': record['native_receipt_path'], 'receipt_sha256': record['native_receipt_sha256'], 'allocated_native_wall_seconds': seconds, 'text': text}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['calibrate', 'proofs'])
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--summary-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--containment-report', type=Path)
    parser.add_argument('--containment-report-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent complete raw artifact and exact DRAT checking, including controls and every replay')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    checked = []
    started = time.monotonic()
    def pin(p, expected=None):
        p = Path(p).resolve()
        name = core.key(p)
        if name not in pins:
            pins[name] = core.sha(p)
        core.require(expected is None or pins[name] == expected, 'hash mismatch ' + name)
        return pins[name]
    try:
        pin(args.summary, args.summary_sha256)
        result = read(args.summary)
        pin(path(result['manifest_path']), result['manifest_sha256'])
        manifest = read(path(result['manifest_path']))
        core.require(result['schema'] == 'EXACT_EIGHT_POLICY_NATIVE_BATCH_RESULT_V1' and manifest['schema'] == 'EXACT_EIGHT_POLICY_NATIVE_BATCH_V1', 'new versioned receipt interface')
        core.require(result['mode'] == manifest['mode'] == ('controls' if args.mode == 'calibrate' else 'research'), 'actual expected native mode')
        core.require(result['limits'] == manifest['limits'] == LIMITS, 'exact current native limits')
        for name, expected in manifest['inputs_sha256'].items():
            pin(path(name), expected)
        for p in CODE + [NATIVE]:
            core.require(manifest['inputs_sha256'].get(core.key(p)) == pin(p), 'entire changed execution code/env/tool source bound')
        pin(NATIVE, NATIVE_SHA)
        imports = ast.walk(ast.parse(DRIVER.read_text()))
        for node in imports:
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            core.require(not any(n.startswith(('native_20260930', 'theory_')) for n in names), 'historical launcher/producer import bypass')
        supervisor = manifest['supervision']
        pin(path(supervisor['manifest_path']), supervisor['manifest_sha256'])
        sm = read(path(supervisor['manifest_path']))
        ss_path = path(supervisor['manifest_path']).parent / 'summary.json'
        pin(ss_path)
        ss = read(ss_path)
        core.require(sm['invocation_id'] == ss['invocation_id'] == supervisor['invocation_id'], 'same containing invocation')
        core.require(sm['seconds'] == supervisor['outer_seconds'] and supervisor['producer_seconds'] == manifest['producer_seconds'] and 0 < manifest['producer_seconds'] + 10 <= sm['seconds'] <= 21600, 'per-invocation nested allocations')
        core.require(ss['status'] == 'COMMAND_COMPLETED_VERIFICATION_PENDING' and ss['command_exit_code'] == 0 and ss['cleanup']['reaped'] is True and ss['cleanup']['job_active_zero_observed'] is True and ss['cleanup']['cleanup_errors'] == [], 'containing Linux command complete with empty observed group')
        core.require(ss['cleanup'].get('process_group_live_pids') == [], 'actual Linux group observation')
        core.require(supervisor['guard_argv'][0] == '/usr/bin/timeout' and '--signal=KILL' in supervisor['guard_argv'], 'actual native outer process-group guard')
        provenance = core.authenticate(pin)
        proof_controls = core.controls(out, deadline)
        parser_controls = core.status_controls()
        approved = {}
        if args.mode == 'proofs':
            # The driver manifest explicitly records every mathematical gate and
            # exact selected formula hash; identify the frozen encoding gate by
            # its status, not by trusting producer classifications.
            gates = []
            for name in manifest['inputs_sha256']:
                if name.endswith('/summary.json') and 'batch05_cnfs_v3/' in name:
                    candidate = read(path(name))
                    if candidate.get('status') == 'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS':
                        gates.append(candidate)
            core.require(len(gates) == 1, 'one exact frozen batch05 encoding gate')
            encoding = gates[0]
            ids = encoding['selected_case_ids']
            core.require(len(ids) == len(set(ids)) == 64 and ids == result['selected_case_ids'] == manifest['selected_case_ids'], 'full exact batch05 ordered population')
            approved = {row['case_id']: row for row in encoding['checked_cases']}
            core.require(len(approved) == 64, 'complete independently reconstructed encoding inventory')
        else:
            core.require(result['selected_case_ids'] == manifest['selected_case_ids'] == [], 'controls are no research population')
            core.require(len(result['case_records']) == 2 and [r['case_id'] for r in result['case_records']] == ['tiny_sat', 'tiny_unsat'], 'exact two native truth controls')
        for row in result['case_records']:
            checked_row = inspect_record(row, pin, args.mode, approved)
            text = checked_row.pop('text')
            if checked_row['native_status'] == 'UNSAT_COMPLETE_PROOF_PENDING':
                replay = core.replay(f'case_{checked_row["case_index"]:04d}_complete', path(checked_row['cnf_path']), path(checked_row['proof_path']), out, deadline, True)
                checked_row['verification_outcome'] = 'UNSAT_VERIFIED'
                checked_row['complete_independent_replay'] = replay
            elif checked_row['native_status'] == 'SAT_COMPLETE_OBJECT_PENDING' and args.mode == 'calibrate':
                values = check_assignment(text, 2, [(1, 2), (1, -2), (-1, 2)])
                core.require(values == {1: True, 2: True}, 'independent tiny SAT unique assignment')
                checked_row['verification_outcome'] = 'SAT_CONTROL_VERIFIED'
            elif checked_row['native_status'] == 'SAT_COMPLETE_OBJECT_PENDING':
                raise ValueError('SAT raw factor requires separately calibrated independent complete factor decoding; do not promote')
            else:
                checked_row['verification_outcome'] = 'UNKNOWN'
            checked.append(checked_row)
            core.save(out / f'case_{checked_row["case_index"]:04d}.json', checked_row)
        core.require(result['attempted_evaluations'] == result['completed_evaluations'] == result['native_calls'] == len(checked), 'actual completed attempt counts')
        if args.mode == 'calibrate':
            timeout = result['timeout_control']
            pin(path(timeout['path']), timeout['sha256'])
            receipt = read(path(timeout['path']))
            core.require(timeout['actual_exit_code'] == receipt['actual_exit_code'] == 124 and receipt['reaped'] is True and receipt['processes_after']['zero_live_matching_observed'] is True, 'actual foreground native timeout control')
            core.require(receipt['command'][:5] == ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', '0.200000s'], 'exact actual timeout fixture command')
            for channel in ['stdout', 'stderr']:
                pin(path(receipt[channel]), receipt[channel + '_sha256'])
            core.require(args.containment_report is not None and args.containment_report_sha256 is not None, 'independent outer Linux descendant containment control required')
            pin(args.containment_report, args.containment_report_sha256)
            containment = read(args.containment_report)
            core.require(containment['status'] == 'INDEPENDENT_LINUX_COMMAND_CONTAINMENT_PASS', 'independent outer group control PASS')
            for name, expected in containment['inputs_sha256'].items():
                pin(path(name), expected)
            for name in ['acceleration/command_deadline.py', 'acceleration/run_compute_command.py']:
                core.require(containment['inputs_sha256'].get(name) == pins[name], 'exact supervisor/deadline independently controlled')
            status = 'INDEPENDENT_EXACT_EIGHT_POLICY_NATIVE_DRIVER_PASS'
        else:
            ids = result['selected_case_ids']
            core.require([r['case_id'] for r in checked] == ids[:len(checked)] and result['pending_case_ids'] == ids[len(checked):], 'exact attempted prefix and pending suffix')
            for source in [Path(__file__), Path(core.__file__)]:
                pin(source)
            all_unsat = len(checked) == 64 and all(r['verification_outcome'] == 'UNSAT_VERIFIED' for r in checked)
            status = 'INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS' if all_unsat else 'INDEPENDENT_EXACT_EIGHT_POLICY_OUTCOMES_PASS'
            if all_unsat:
                core.save(out / 'claim_binding.json', {
                    'id': CLAIM, 'revision': 1, 'kind': 'exclusion', 'basis': ['DERIVED', 'COMPUTED'], 'status': 'VERIFIED', 'review_state': 'CLEAR',
                    'statement': 'For each of the exact 64 ordered literal count profiles selected by the frozen batch05 selection on the fixed six-prism Hadamard support, no binary 36x60 factor satisfies that literal full integer Gram and the encoded within-triplicate column caps; every exact raw CNF has a complete independently replayed DRAT proof.',
                    'scope': {'description': 'Only the exact 64 literal batch05 profiles on one fixed support; cross-triplicate caps and residualD are omitted.', 'unrestricted_target': False, 'target_resolution': 'NONE'},
                    'assumptions': ['Frozen six-prism Hadamard support and complete literal initial local domains.', 'No target automorphism is assumed.'],
                    'dependencies': [{'id': 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-GRAM-ENCODINGS', 'revision': 1, 'relation': 'encoding_equivalence'}],
                    'verifier': '/root/checkpoint_audit', 'method': 'independent_artifact_check', 'claim_revision': 1,
                    'inputs_sha256': pins, 'case_records': checked, 'complete_proof_replays': 64,
                    'shared_components': ['The preserved independently authenticated DRAT-trim binary, reviewed Windows portability shim, compiler/runtime and authentication helper.', 'Historical independent raw-clause reconstruction supplies encoding equivalence; the new native producer is not imported or trusted for UNSAT.'],
                    'controls': {'proof': proof_controls, 'native_receipt_parser': parser_controls},
                    'limitations': ['No whole-support or unrestricted target nonexistence claim.', 'No automatic relabelling expansion, union or target-wide denominator.', 'Full raw proof evidence remains LOCAL_ONLY unless separately published and replayed from that package.', 'No formal verification, diverse checker or external peer review asserted.'],
                    'artifact_availability': 'LOCAL_ONLY', 'created_at': datetime.now(timezone.utc).isoformat(), 'updated_at': datetime.now(timezone.utc).isoformat(),
                })
        for source in [Path(__file__), Path(core.__file__)]:
            pin(source)
        summary = {'status': status, 'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(), 'verifier': '/root/checkpoint_audit', 'method': 'independent_artifact_check', 'inputs_sha256': pins, 'case_records': checked, 'proof_controls': proof_controls, 'native_receipt_parser_controls': parser_controls, 'checker_provenance': provenance, 'completed_proof_replays': sum(r['verification_outcome'] == 'UNSAT_VERIFIED' for r in checked), 'proof_bytes': sum(r['proof_bytes'] for r in checked if r['verification_outcome'] == 'UNSAT_VERIFIED'), 'claim_id': CLAIM if status == 'INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS' else None, 'claim_revision': 1 if status == 'INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS' else None, 'new_solver_calls': 0, 'target_resolution': False, 'artifact_availability': 'LOCAL_ONLY', 'elapsed_seconds': time.monotonic() - started, 'limitations': ['Exact recorded restricted scope only.', 'Raw decoded research SAT factors require a separate complete independent path and halt this checker before promotion.', 'Historical mathematical gates are authenticated reused review; complete20k archive hashes are not recalculated.']}
        core.save(out / 'summary.json', summary)
        print(json.dumps({'status': status, 'completed_proof_replays': summary['completed_proof_replays'], 'summary_sha256': core.sha(out / 'summary.json')}), flush=True)
    except BaseException as error:
        core.save(out / 'failure.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'error': repr(error), 'inputs_sha256': pins, 'completed_checked_records': checked, 'target_resolution': False, 'unmet_requirements': ['Complete independent exact artifact checking']})
        raise


if __name__ == '__main__':
    main()
