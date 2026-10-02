"""Independent generic single-instance producer v2 controls and raw outcome audit."""
from __future__ import annotations

import argparse
import ast
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline
import audit_20261002_policy_drat_core_v2 as core
from audit_20261002_exact_eight_policy_v2 import read, path, linux, check_assignment, same_json

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = ROOT / 'acceleration/native_20261002_budget_single_v2.py'
SINGLE_SPEC = PRODUCER.with_name(PRODUCER.stem + '_spec.md')
SHARED = ROOT / 'acceleration/native_20261002_exact_eight_budget_v1.py'
ENV = ROOT / 'acceleration/native_budget_env_v1'
NATIVE = ROOT / 'build/research-cadical195/source/build/cadical'
NATIVE_SHA = '021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'
CODE = [PRODUCER, SINGLE_SPEC, SHARED, SHARED.with_name(SHARED.stem + '_spec.md'), ROOT / 'acceleration/command_deadline.py', ROOT / 'acceleration/run_compute_command.py', ENV / 'pyproject.toml', ENV / 'uv.lock']


def check_case(descriptor, pin, config, mode):
    pin(path(descriptor['path']), descriptor['sha256'])
    record = read(path(descriptor['path']))
    core.require(record['schema'] == 'POLICY_NATIVE_SINGLE_CASE_V2' and record['native_calls'] == 1 and record['independent_approval'] is False and record['target_resolution'] is False, 'versioned unapproved raw single-instance outcome')
    pin(path(record['launch_path']), record['launch_sha256'])
    pin(path(record['receipt_path']), record['receipt_sha256'])
    launch = read(path(record['launch_path']))
    receipt = read(path(record['receipt_path']))
    core.require(launch['schema'] == 'POLICY_NATIVE_SINGLE_LAUNCH_V2' and receipt['schema'] == 'POLICY_NATIVE_SINGLE_RECEIPT_V2', 'new exact launch/receipt interface')
    actual = launch['configuration']
    if mode == 'calibrate':
        core.require({k: v for k, v in actual.items() if k != 'shutdown_reserve_seconds'} == {k: v for k, v in config.items() if k != 'shutdown_reserve_seconds'}, 'same planned execution options, shorter disclosed control shutdown reserve')
    else:
        core.require(actual == config, 'actual research exactly frozen configuration')
    core.require(receipt['configuration'] == actual, 'same resource configuration')
    cnf = path(launch['cnf_path'])
    pin(cnf, launch['cnf_sha256'])
    with cnf.open('rb') as stream:
        header = stream.readline().split()
    core.require(len(header) == 4 and header[:2] == [b'p', b'cnf'], 'exact actual DIMACS header')
    variables, clauses = int(header[2]), int(header[3])
    seconds = launch['native_wall_limit_seconds']
    core.require(seconds == receipt['native_wall_limit_seconds'] and 0 < seconds <= launch['requested_native_seconds'], 'exact dynamic native allocation')
    core.require(seconds + actual['shutdown_reserve_seconds'] - .1 <= launch['deadline_before_launch']['remaining_seconds'] and launch['deadline_before_launch']['stop_required'] is False, 'same-invocation native/transfer reserve')
    expected = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{seconds:.6f}s', '/usr/bin/prlimit', f"--as={config['address_space_bytes']}:{config['address_space_bytes']}", f"--fsize={config['proof_file_bytes']}:{config['proof_file_bytes']}", '--core=0:0', linux(NATIVE), '--no-binary', f"--seed={config['seed']}"]
    if config['conflict_limit'] is not None:
        expected += ['-c', str(config['conflict_limit'])]
    expected += [linux(cnf), launch['ext4_proof']]
    core.require(receipt['command'] == launch['command'] == expected, 'complete exact generic native command and resource guard')
    core.require(receipt['cwd'] == linux(ROOT) and receipt['reaped'] is True and receipt['processes_after']['zero_live_matching_observed'] is True and receipt['processes_after']['matching_processes'] == [], 'actually reaped generic worker and live-empty matching snapshot')
    for channel in ['stdout', 'stderr']:
        pin(path(receipt[channel]), receipt[channel + '_sha256'])
    text = path(receipt['stdout']).read_text(errors='replace')
    status = core.native_status(text, receipt['actual_exit_code'], variables, clauses)
    if status != 'UNKNOWN':
        core.require(receipt['producer_stop_reason'] is None, 'conclusive result is not interrupted')
        core.require('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text.splitlines(), 'actual exact solver version')
    raw = record['raw_proof']
    if raw is not None:
        proof = path(raw['path'])
        pin(proof, raw['sha256'])
        core.require(raw['sha256'] == raw['source_sha256'] and raw['bytes'] == proof.stat().st_size <= config['proof_file_bytes'] and raw['linux_original_path'] == launch['ext4_proof'], 'complete raw trace copy exact hash/source/size identity')
    else:
        proof = None
    core.require(descriptor['raw_outcome'] == record['raw_outcome'], 'identical terminal outcome')
    if status == 'UNSAT_COMPLETE_PROOF_PENDING':
        core.require(proof is not None and 0 < proof.stat().st_size < config['proof_file_bytes'] and record['raw_outcome'] == 'UNSAT_TRACE_PENDING_COMPLETE_REPLAY', 'uncapped complete proof trace required')
    elif status == 'SAT_COMPLETE_OBJECT_PENDING':
        core.require(record['raw_outcome'] == 'SAT_RAW_OBJECT_PENDING_INDEPENDENT_VALIDATION', 'SAT remains raw object pending')
    else:
        core.require(record['raw_outcome'] == 'UNKNOWN', 'nonconclusive outcome cannot promote')
    return {'cnf_path': core.key(cnf), 'cnf_sha256': launch['cnf_sha256'], 'variables': variables, 'clauses': clauses, 'native_status': status, 'actual_exit_code': receipt['actual_exit_code'], 'wall_seconds': receipt['wall_seconds'], 'allocated_native_wall_seconds': seconds, 'receipt_path': record['receipt_path'], 'receipt_sha256': record['receipt_sha256'], 'proof_path': core.key(proof) if proof else None, 'proof_sha256': raw['sha256'] if raw else None, 'proof_bytes': raw['bytes'] if raw else None, 'text': text}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['calibrate', 'outcomes'])
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--summary-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--containment-report', type=Path)
    parser.add_argument('--containment-report-sha256')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent generic driver controls/outcome exact artifact and complete proof checks including calibrated controls')
    started, pins, checked = time.monotonic(), {}, []
    def pin(p, expected=None):
        name = core.key(p)
        if name not in pins:
            pins[name] = core.sha(p)
        core.require(expected is None or pins[name] == expected, 'hash identity ' + name)
        return pins[name]
    try:
        pin(args.summary, args.summary_sha256)
        result = read(args.summary)
        pin(path(result['manifest_path']), result['manifest_sha256'])
        manifest = read(path(result['manifest_path']))
        core.require(result['schema'] == 'POLICY_NATIVE_SINGLE_BATCH_RESULT_V2' and manifest['schema'] == 'POLICY_NATIVE_SINGLE_BATCH_V2', 'new generic batch interface')
        core.require(result['mode'] == manifest['mode'] == ('controls' if args.mode == 'calibrate' else 'research'), 'actual intended mode')
        for name, expected in manifest['inputs_sha256'].items():
            pin(path(name), expected)
        for source in CODE + [NATIVE]:
            core.require(manifest['inputs_sha256'].get(core.key(source)) == pin(source), 'entire generic/shared versioned execution source closure')
        pin(NATIVE, NATIVE_SHA)
        for node in ast.walk(ast.parse(PRODUCER.read_text())):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            core.require(not any(name.startswith(('native_20260930', 'theory_')) for name in names), 'historical launcher/producer bypass absent')
        pin(path(manifest['plan_path']), manifest['plan_sha256'])
        plan = read(path(manifest['plan_path']))
        config = plan['configuration']
        core.require(plan['schema'] == 'POLICY_NATIVE_SINGLE_PLAN_V2' and config == manifest['configuration'] and plan['numerical_acceptance'] == 'EXACT_INTEGER_CNF_AND_RAW_PROOF_OR_COMPLETE_ASSIGNMENT', 'exact frozen numerical acceptance and configuration')
        core.require(config['conflict_limit'] is not None or isinstance(config['conflict_limit_null_reason'], str) and bool(config['conflict_limit_null_reason'].strip()), 'explicit reason for unavailable/no conflict cutoff')
        supervisor = manifest['supervision']
        pin(path(supervisor['manifest_path']), supervisor['manifest_sha256'])
        sm = read(path(supervisor['manifest_path']))
        ss_path = path(supervisor['manifest_path']).parent / 'summary.json'
        pin(ss_path)
        ss = read(ss_path)
        core.require(sm['invocation_id'] == ss['invocation_id'] == supervisor['invocation_id'], 'same enclosing Linux invocation')
        core.require(supervisor['producer_seconds'] == manifest['actual_producer_seconds'] and 0 < supervisor['producer_seconds'] + 10 <= sm['seconds'] <= 21600 and sm['cumulative_across_commands'] is False, 'single command allowance includes nested producer setup')
        core.require(ss['status'] == 'COMMAND_COMPLETED_VERIFICATION_PENDING' and ss['command_exit_code'] == 0 and ss['cleanup']['reaped'] is True and ss['cleanup']['job_active_zero_observed'] is True and ss['cleanup']['cleanup_errors'] == [] and ss['cleanup']['process_group_live_pids'] == [], 'outer Linux worker exited normally and group observed empty')
        core.require(supervisor['guard_argv'][0] == '/usr/bin/timeout' and '--signal=KILL' in supervisor['guard_argv'], 'actual outer native guard')
        provenance = core.authenticate(pin)
        proof_controls = core.controls(out, deadline)
        receipt_controls = core.status_controls()
        if args.mode == 'calibrate':
            core.require(len(result['case_records']) == result['native_calls'] == 2, 'two native truth controls')
            core.require(args.containment_report is not None and args.containment_report_sha256 is not None, 'outer Linux descendant controls required')
            pin(args.containment_report, args.containment_report_sha256)
            containment = read(args.containment_report)
            core.require(containment['status'] == 'INDEPENDENT_LINUX_COMMAND_CONTAINMENT_PASS', 'independent tested outer descendant guard')
            for name, expected in containment['inputs_sha256'].items():
                pin(path(name), expected)
            for filename in ['command_deadline.py', 'run_compute_command.py']:
                name = 'acceleration/' + filename
                core.require(containment['inputs_sha256'].get(name) == pins[name], 'same independently controlled deadline/supervisor')
        else:
            core.require(len(result['case_records']) == result['native_calls'] == 1, 'one exact planned research instance')
            for descriptor in plan['inputs']:
                p = path(descriptor['path'])
                pin(p, descriptor['sha256'])
                core.require(p.stat().st_size == descriptor['bytes'], 'exact input artifact length')
            for descriptor in plan['mathematical_gates']:
                gate_path = path(descriptor['path'])
                pin(gate_path, descriptor['sha256'])
                gate = read(gate_path)
                core.require(gate['status'] == descriptor['expected_status'], 'historical exact mathematical gate status')
                for name, expected in descriptor['required_input_bindings'].items():
                    core.require(gate['inputs_sha256'].get(name) == pins.get(name) == expected, 'historical gate bound to current selected mathematical inputs')
        for index, row in enumerate(result['case_records']):
            record = check_case(row, pin, config, args.mode)
            text = record.pop('text')
            if args.mode == 'calibrate':
                expected_cnf = b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n' if index == 0 else b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
                core.require(path(record['cnf_path']).read_bytes() == expected_cnf and record['allocated_native_wall_seconds'] == 10, 'exact independently known native truth fixture and disclosed shorter timer')
            else:
                cnf_input = next(item for item in plan['inputs'] if item['role'] == 'cnf')
                core.require(record['cnf_path'] == cnf_input['path'] and record['cnf_sha256'] == cnf_input['sha256'] and record['variables'] == plan['variables'] and record['clauses'] == plan['clauses'], 'exact planned research formula')
            if record['native_status'] == 'UNSAT_COMPLETE_PROOF_PENDING':
                record['complete_proof_replay'] = core.replay('native_control_unsat' if args.mode == 'calibrate' else 'complete_research_proof', path(record['cnf_path']), path(record['proof_path']), out, deadline, True)
                record['verification_outcome'] = 'UNSAT_EXACT_INSTANCE_VERIFIED'
            elif record['native_status'] == 'SAT_COMPLETE_OBJECT_PENDING' and args.mode == 'calibrate':
                core.require(check_assignment(text, 2, [(1, 2), (1, -2), (-1, 2)]) == {1: True, 2: True}, 'raw unique SAT truth independently exact checked')
                record['verification_outcome'] = 'SAT_CONTROL_VERIFIED'
            elif record['native_status'] == 'SAT_COMPLETE_OBJECT_PENDING':
                record['verification_outcome'] = 'SAT_COMPLETE_RAW_OBJECT_PENDING_INDEPENDENT_TARGET_VALIDATION'
            else:
                record['verification_outcome'] = 'UNKNOWN_NO_EXCLUSION'
            checked.append(record)
            core.save(out / f'outcome_{index:02d}.json', record)
        status = 'INDEPENDENT_POLICY_NATIVE_SINGLE_V2_DRIVER_PASS' if args.mode == 'calibrate' else 'INDEPENDENT_POLICY_NATIVE_SINGLE_V2_OUTCOME_AUDIT_PASS'
        for source in [Path(__file__), Path(core.__file__), ROOT / 'acceleration/audit_20261002_exact_eight_policy_v2.py', ROOT / 'uv.lock', ROOT / 'pyproject.toml']:
            pin(source)
        for label, version in manifest['tool_versions'].items():
            core.require(version['actual_exit_code'] == 0 and isinstance(version['stdout'], str) and bool(version['stdout'].strip()), 'observed successful tool version ' + label)
        report = {'status': status, 'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(), 'verifier': '/root/checkpoint_audit', 'producer': '/root/native_driver', 'native_execution_operator': '/root', 'inputs_sha256': pins, 'case_records': checked, 'tested_configuration': {k: v for k, v in config.items() if k not in {'native_seconds', 'producer_seconds', 'shutdown_reserve_seconds'}}, 'plan_path': manifest['plan_path'], 'plan_sha256': manifest['plan_sha256'], 'proof_controls': proof_controls, 'receipt_parser_corruptions': receipt_controls, 'checker_provenance': provenance, 'observed_native_tool_versions': manifest['tool_versions'], 'new_solver_calls': 0, 'target_resolution': False, 'artifact_availability': 'LOCAL_ONLY', 'elapsed_seconds': time.monotonic() - started, 'limitations': ['Native execution resources/options calibrated on exact two-variable control cases only; no solver performance or target feasibility inference.', 'An exact-instance UNSAT proof requires separately checked encoding equivalence and unrestricted coverage before a target-level interpretation.', 'A research SAT result remains a raw object pending separate exact target graph validation.', 'Historical mathematical gate bytes/direct inputs authenticated; their entire historical transitive closure is not rehashed.', 'Same trusted calibrated DRAT-trim implementation, shim/compiler/runtime and source authenticator; no formal/diverse checker or external peer review.']}
        core.save(out / 'summary.json', report)
        print(json.dumps({'status': status, 'summary_sha256': core.sha(out / 'summary.json')}), flush=True)
    except BaseException as error:
        core.save(out / 'failure.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'error': repr(error), 'inputs_sha256': pins, 'checked_records': checked, 'target_resolution': False})
        raise


if __name__ == '__main__':
    main()
