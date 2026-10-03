"""One exact frozen SAT instance, native Linux budget supervision, producer v2.

No mathematical promotion, native search, or preparation on import. Frozen v1
helpers are shared explicitly; this new generic receipt/command needs a new gate.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

import native_20261002_exact_eight_budget_v1 as shared
from command_deadline import CommandDeadline
from run_compute_command import review_evidence

ROOT = shared.ROOT
SPEC = Path(__file__).with_name(Path(__file__).stem+'_spec.md')
CODE = [Path(__file__), SPEC, *shared.CODE]
CODE = list(dict.fromkeys(path.resolve() for path in CODE))


def finite(value, minimum, maximum, label):
    shared.need(not isinstance(value, bool) and isinstance(value, (int, float)) and
                math.isfinite(value) and minimum <= value <= maximum, label)
    return value


def integer(value, minimum, maximum, label):
    shared.need(type(value) is int and minimum <= value <= maximum, label)
    return value


def text(value, label):
    shared.need(isinstance(value, str) and value.strip(), label)
    return value


def validate_plan(plan):
    shared.need(plan['schema'] == 'POLICY_NATIVE_SINGLE_PLAN_V2', 'frozen single-instance plan schema')
    for field in ['question', 'scope', 'selection_rule', 'success_criterion', 'falsification_criterion',
                  'independent_verification_criterion', 'allocation_reason', 'numerical_acceptance',
                  'source_commit', 'baseline_and_uncertainty']:
        text(plan.get(field), 'required plan field '+field)
    shared.need(re.fullmatch('[0-9a-f]{40}', plan['source_commit']), 'plan exact source commit')
    shared.need(plan['numerical_acceptance'] == 'EXACT_INTEGER_CNF_AND_RAW_PROOF_OR_COMPLETE_ASSIGNMENT',
                'no floating point proof acceptance')
    config = plan['configuration']
    integer(config['address_space_bytes'], 256*1024**2, 32*1024**3, 'explicit bounded address space')
    integer(config['proof_file_bytes'], 1024, 8*1024**3, 'explicit bounded proof file')
    integer(config['seed'], 0, 2000000000, 'explicit native seed')
    if config['conflict_limit'] is None:
        text(config.get('conflict_limit_null_reason'), 'why no conflict cutoff')
    else:
        integer(config['conflict_limit'], 1, 2147483647, 'conflict cutoff')
    finite(config['native_seconds'], .001, 21500, 'explicit native allocation')
    finite(config['producer_seconds'], 40, 21550, 'explicit producer sub-allocation')
    finite(config['shutdown_reserve_seconds'], 10, 600, 'explicit shutdown/transfer reserve')
    shared.need(config['native_seconds'] + config['shutdown_reserve_seconds'] < config['producer_seconds'],
                'native allowance plus shutdown/transfer reserve')
    for field in ['host_free_reserve_bytes', 'ext4_free_reserve_bytes', 'aggregate_retained_artifact_bytes']:
        integer(config[field], 0, 128*1024**3, 'explicit resource guard '+field)
    shared.need(config['aggregate_retained_artifact_bytes'] >= 2*config['proof_file_bytes']+64*1024**2,
                'artifact ceiling includes both proof copies plus overhead')
    shared.need(type(plan['variables']) is int and plan['variables'] > 0 and
                type(plan['clauses']) is int and plan['clauses'] >= 0, 'exact planned DIMACS dimensions')
    inputs = plan['inputs']
    shared.need(type(inputs) is list and {row['role'] for row in inputs} >= {'cnf', 'model', 'scope'},
                'pin CNF, model and mathematical scope')
    shared.need(len({row['role'] for row in inputs}) == len(inputs), 'unique input roles')
    return config


def resources(workspace, config):
    mount = subprocess.check_output(['/usr/bin/findmnt', '--target', str(workspace), '--output',
                                     'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], text=True)
    shared.need('ext4' in mount.split(), 'native proof directory observed ext4')
    host, native = shutil.disk_usage(ROOT).free, shutil.disk_usage(workspace).free
    return dict(timestamp=shared.stamp(), host_free_bytes=host, ext4_free_bytes=native,
        filesystem_observation=mount.strip(), pass_reserves=host >= config['host_free_reserve_bytes'] and
        native >= config['ext4_free_reserve_bytes'])


def supervision(args, pins, deadline):
    shared.need(sys.platform.startswith('linux'), 'generic native supervision must be inside Linux')
    path = args.supervision_out.resolve()/'manifest.json'
    data = shared.read(path)
    shared.pin(ROOT/'acceleration/run_compute_command.py', data['source_sha256'], pins, deadline)
    shared.need(data['seconds'] <= 21600 and data['seconds'] >= args.seconds+10,
                'generic producer is a contained shorter allocation')
    shared.need(data['cumulative_across_commands'] is False and data['automatic_retry'] is False,
                'per-invocation supervisor policy')
    pgid = os.getpgid(0)
    leader = [part.decode() for part in (Path('/proc')/str(pgid)/'cmdline').read_bytes().split(b'\0') if part]
    shared.need(leader and Path(leader[0]).name == 'timeout' and '--signal=KILL' in leader,
                'observed enclosing GNU timeout group leader')
    shared.need(str(Path(__file__).resolve()) in data['command'] or shared.key(Path(__file__)) in data['command'],
                'supervisor names this exact generic worker')
    return dict(manifest_path=shared.key(path), manifest_sha256=shared.sha(path, deadline),
                invocation_id=data['invocation_id'], outer_seconds=data['seconds'],
                producer_seconds=args.seconds, process_group=pgid, guard_argv=leader,
                boundary='Outer command includes setup, all hashing/native computation and transfer')


def command(cnf, proof, config, seconds):
    argv = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{seconds:.6f}s',
            '/usr/bin/prlimit', f"--as={config['address_space_bytes']}:{config['address_space_bytes']}",
            f"--fsize={config['proof_file_bytes']}:{config['proof_file_bytes']}", '--core=0:0',
            str(shared.NATIVE), '--no-binary', f"--seed={config['seed']}"]
    if config['conflict_limit'] is not None:
        argv += ['-c', str(config['conflict_limit'])]
    return argv + [str(cnf), str(proof)]


def native_resources(observation):
    rows = []
    for process in observation['matching_processes']:
        try:
            folder = Path('/proc')/str(process['pid'])
            fields = (folder/'stat').read_text().rsplit(')', 1)[1].split()
            status = (folder/'status').read_text()
            peak = re.findall(r'^VmHWM:\s+(\d+) kB$', status, re.M)
            rows.append(dict(pid=process['pid'], cpu_seconds=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK'),
                resident_bytes=int(fields[21])*os.sysconf('SC_PAGE_SIZE'),
                peak_resident_bytes=int(peak[0])*1024 if peak else None))
        except (OSError, ValueError, IndexError):
            continue
    return dict(linux_native_processes=rows, gpu_utilization=None,
                gpu_unavailable_reason='CPU native SAT solver; no GPU workload',
                scope='Observed exact native/checker processes only; no whole-job accounting')


def tool_versions(deadline):
    rows = {}
    for label, argv in [('cadical', [str(shared.NATIVE), '--version']),
                        ('timeout', ['/usr/bin/timeout', '--version']),
                        ('prlimit', ['/usr/bin/prlimit', '--version']),
                        ('uv', ['/root/.local/bin/uv', '--version'])]:
        shared.check_time(deadline, 20)
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                                timeout=min(10, deadline.child_seconds(10, reserve_seconds=10)))
        shared.need(result.returncode == 0, 'observed tool version '+label)
        rows[label] = dict(command=argv, actual_exit_code=result.returncode,
                           stdout=result.stdout, stderr=result.stderr)
    return rows


def review(args, deadline, supervisor, digest, out):
    if not args.review_json or not args.review_json.exists():
        return digest, None
    raw = args.review_json.read_bytes()
    shared.need(len(raw) <= 65536, 'review size')
    current = hashlib.sha256(raw).hexdigest()
    if current == digest:
        return digest, None
    row = json.loads(raw)
    observed = row.get('observed_at_producer_elapsed_seconds')
    finite(observed, 0, 21600, 'producer observation timestamp')
    translated = {**row, 'observed_at_elapsed_seconds': observed}
    review_evidence(translated, supervisor['invocation_id'], deadline.status()['elapsed_seconds'])
    with (out/'producer_reviews.jsonl').open('a', encoding='utf8') as stream:
        stream.write(json.dumps(row)+'\n')
    if row['decision'] != 'continue':
        return current, 'REVIEW_'+row['decision'].upper()
    deadline.review(evidence=json.dumps(row))
    return current, None


def execute(args, cnf, folder, out, deadline, supervisor, config, requested):
    folder.mkdir()
    before = shared.observe()
    shared.save(folder/'processes_before.json', before)
    shared.need(before['zero_live_matching_observed'], 'observed live native/checker prevents launch')
    workspace = Path(tempfile.mkdtemp(prefix='conway99-single-v2-', dir='/tmp'))
    shared.save(folder/'workspace.json', dict(timestamp=shared.stamp(), path=str(workspace),
        availability='LOCAL_ONLY', future_availability='UNKNOWN', deletion_requested=False))
    observed_resources = resources(workspace, config)
    shared.save(folder/'resources.json', observed_resources)
    shared.need(observed_resources['pass_reserves'], 'prelaunch disk reserves')
    seconds = deadline.child_seconds(requested, reserve_seconds=config['shutdown_reserve_seconds'])
    proof = workspace/'proof.drat'
    argv = command(cnf, proof, config, seconds)
    launch = dict(schema='POLICY_NATIVE_SINGLE_LAUNCH_V2', timestamp=shared.stamp(), command=argv,
        cnf_path=shared.key(cnf), cnf_sha256=shared.sha(cnf, deadline), ext4_proof=str(proof),
        native_wall_limit_seconds=seconds, requested_native_seconds=requested,
        configuration=config, deadline_before_launch=deadline.status())
    shared.save(folder/'launch.json', launch)
    print(json.dumps(dict(state='POLICY_SINGLE_NATIVE_LAUNCH', label=folder.name, seconds=seconds)), flush=True)
    start, stop, digest, last = time.monotonic(), None, None, -float('inf')
    with (folder/'solver.stdout.log').open('xb') as stdout, (folder/'solver.stderr.log').open('xb') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
        try:
            shared.need(os.getpgid(process.pid) == os.getpgid(0), 'solver stays in outer process group')
            while process.poll() is None:
                digest, decision = review(args, deadline, supervisor, digest, out)
                status = deadline.status()
                if decision or status['stop_required'] or status['remaining_seconds'] <= 20:
                    stop = decision or 'PRODUCER_DEADLINE_OR_REASSESSMENT'
                    break
                if time.monotonic()-last >= 10:
                    observation = shared.observe()
                    shared.progress(out/'progress.json', dict(timestamp=shared.stamp(), phase='native',
                        label=folder.name, solver_guard_pid=process.pid,
                        current_processes=observation, resources=native_resources(observation), **status))
                    last = time.monotonic()
                time.sleep(.05)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=6)
                except subprocess.TimeoutExpired:
                    process.kill()
            code = process.wait(timeout=5)
    after = shared.observe()
    receipt = dict(schema='POLICY_NATIVE_SINGLE_RECEIPT_V2', timestamp=shared.stamp(), command=argv,
        cwd=str(ROOT), actual_exit_code=code, wall_seconds=time.monotonic()-start,
        producer_stop_reason=stop, solver_guard_pid=process.pid, process_group=os.getpgid(0),
        reaped=True, processes_after=after, configuration=config, native_wall_limit_seconds=seconds,
        stdout=shared.key(folder/'solver.stdout.log'), stdout_sha256=shared.sha(folder/'solver.stdout.log', deadline),
        stderr=shared.key(folder/'solver.stderr.log'), stderr_sha256=shared.sha(folder/'solver.stderr.log', deadline),
        mathematical_approval=False)
    shared.save(folder/'solver.receipt.json', receipt)
    shared.need(after['zero_live_matching_observed'], 'remaining native process; no future launch')
    copied = None
    if proof.is_file():
        shared.need(proof.stat().st_size <= config['proof_file_bytes'], 'actual proof size guard')
        destination, identity = folder/'proof.drat', hashlib.sha256()
        with proof.open('rb') as source, destination.open('xb') as target:
            for block in iter(lambda: source.read(1048576), b''):
                shared.check_time(deadline, 10)
                target.write(block)
                identity.update(block)
        copied = dict(path=shared.key(destination), sha256=identity.hexdigest(), bytes=destination.stat().st_size,
            linux_original_path=str(proof), source_sha256=shared.sha(proof, deadline),
            availability='LOCAL_ONLY', complete_proof=False)
        shared.need(copied['sha256'] == copied['source_sha256'], 'entire raw proof copy equality')
    output = (folder/'solver.stdout.log').read_text(errors='replace')
    statuses = [line.strip() for line in output.splitlines() if line.startswith('s ')]
    if code == 20 and statuses == ['s UNSATISFIABLE'] and copied and 0 < copied['bytes'] < config['proof_file_bytes'] and stop is None:
        result = 'UNSAT_TRACE_PENDING_COMPLETE_REPLAY'
    elif code == 10 and statuses == ['s SATISFIABLE'] and stop is None:
        result = 'SAT_RAW_OBJECT_PENDING_INDEPENDENT_VALIDATION'
    else:
        result = 'UNKNOWN'
    summary = dict(schema='POLICY_NATIVE_SINGLE_CASE_V2', timestamp=shared.stamp(),
        launch_path=shared.key(folder/'launch.json'), launch_sha256=shared.sha(folder/'launch.json', deadline),
        receipt_path=shared.key(folder/'solver.receipt.json'), receipt_sha256=shared.sha(folder/'solver.receipt.json', deadline),
        native_status_lines=statuses, raw_outcome=result, raw_proof=copied,
        native_calls=1, independent_approval=False, target_resolution=False, producer_stop_reason=stop,
        unfinished_description='not completed within the allocated budget' if result == 'UNKNOWN' else None,
        unmet_requirements=['Independent complete proof or raw object checking; encoding/coverage review for any target claim'])
    shared.save(folder/'summary.json', summary)
    return dict(path=shared.key(folder/'summary.json'), sha256=shared.sha(folder/'summary.json', deadline),
                raw_outcome=result, native_calls=1)


def run(args):
    raw_plan = args.plan.read_bytes()
    shared.need(hashlib.sha256(raw_plan).hexdigest() == args.plan_sha256, 'exact frozen plan bytes')
    plan = json.loads(raw_plan)
    config = validate_plan(plan)
    # Allocation starts before artifact hashing; the enclosing supervisor has
    # already started before this plan read/parse and uv setup.
    seconds = args.control_seconds if args.mode == 'controls' else config['producer_seconds']
    deadline = CommandDeadline(seconds, allocation_reason=plan['allocation_reason'])
    out = args.out.resolve()
    shared.need(out.is_relative_to(ROOT), 'existing repository outputs only')
    out.mkdir(parents=True, exist_ok=False)
    rows, pins = [], {}
    try:
        args.seconds = seconds
        supervisor = supervision(args, pins, deadline)
        for path in CODE:
            pins[shared.key(path)] = shared.sha(path, deadline)
        shared.pin(shared.NATIVE, shared.NATIVE_SHA, pins, deadline)
        shared.pin(args.plan, args.plan_sha256, pins, deadline)
        cnf = None
        if args.mode != 'controls':
            for record in plan['inputs']:
                path = shared.repository_path(record['path'])
                shared.pin(path, record['sha256'], pins, deadline)
                shared.need(path.stat().st_size == record['bytes'], 'frozen input size')
                if record['role'] == 'cnf':
                    cnf = path
            with cnf.open('rb') as stream:
                shared.need(stream.readline() == f"p cnf {plan['variables']} {plan['clauses']}\n".encode(), 'exact selected DIMACS header')
            shared.need(type(plan['mathematical_gates']) is list and plan['mathematical_gates'], 'explicit mathematical checking records')
            for descriptor in plan['mathematical_gates']:
                path = shared.repository_path(descriptor['path'])
                shared.pin(path, descriptor['sha256'], pins, deadline)
                gate = shared.read(path)
                shared.need(gate['status'] == descriptor['expected_status'], 'exact mathematical gate status')
                for name, identity in descriptor['required_input_bindings'].items():
                    shared.need(gate['inputs_sha256'].get(name) == identity and pins.get(name) == identity,
                                'mathematical gate binds exact selected input')
            if args.mode == 'research':
                shared.need(args.driver_gate is not None, 'new generic driver calibration required')
                shared.pin(args.driver_gate, args.driver_gate_sha256, pins, deadline)
                gate = shared.read(args.driver_gate)
                shared.need(gate['status'] == 'INDEPENDENT_POLICY_NATIVE_SINGLE_V2_DRIVER_PASS', 'new generic execution gate')
                for path in CODE+[shared.NATIVE]:
                    shared.need(gate['inputs_sha256'].get(shared.key(path)) == pins[shared.key(path)], 'new gate entire trusted source/tool closure')
                shared.need(gate['tested_configuration'] == {name: value for name, value in config.items()
                    if name not in {'native_seconds', 'producer_seconds', 'shutdown_reserve_seconds'}},
                    'controls calibrated same native execution options/resources; timer allocations differ explicitly')
        manifest = dict(schema='POLICY_NATIVE_SINGLE_BATCH_V2', timestamp=shared.stamp(), mode=args.mode,
            source_commit=plan['source_commit'], command=[sys.executable, *sys.argv], cwd=str(ROOT),
            python=platform.python_version(), platform=platform.platform(), tool_versions=tool_versions(deadline),
            native_calls_unit='Scientific/engineering CNF evaluations; metadata-only version probes are separate.', inputs_sha256=pins,
            plan_path=shared.key(args.plan), plan_sha256=args.plan_sha256, supervision=supervisor,
            configuration=config, actual_producer_seconds=seconds, independent_approval=False,
            target_resolution=False, historical_gate_reuse='Exact gate bytes and direct selected artifacts authenticated; no historical execution approval transferred.',
            automatic_retry=False, automatic_resume=False)
        shared.save(out/'manifest.json', manifest)
        if args.mode == 'controls':
            shared.need(args.control_seconds > 30, 'control wall allowance includes tiny native work and transfer')
            control_config = {**config, 'shutdown_reserve_seconds': min(config['shutdown_reserve_seconds'],
                                                                       args.control_seconds-25)}
            for label, raw in [('tiny_sat', b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n'),
                               ('tiny_unsat', b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n')]:
                path = out/(label+'.cnf')
                path.write_bytes(raw)
                rows.append(execute(args, path, out/label, out, deadline, supervisor, control_config, 10))
        elif args.mode == 'research':
            rows.append(execute(args, cnf, out/'instance', out, deadline, supervisor, config, config['native_seconds']))
        summary = dict(schema='POLICY_NATIVE_SINGLE_BATCH_RESULT_V2', timestamp=shared.stamp(),
            status='POLICY_SINGLE_OUTPUTS_PENDING_INDEPENDENT_VERIFICATION', mode=args.mode,
            manifest_path=shared.key(out/'manifest.json'), manifest_sha256=shared.sha(out/'manifest.json', deadline),
            case_records=rows, native_calls=sum(row['native_calls'] for row in rows),
            execution_state='COMPLETED' if args.mode == 'preflight' or rows and rows[-1]['raw_outcome'] != 'UNKNOWN' else 'STOPPED',
            target_resolution=False, mathematical_exclusions_asserted=0, independent_approval=False,
            producer_elapsed_seconds=deadline.status()['elapsed_seconds'], automatic_retry=False, automatic_resume=False,
            unmet_requirements=['Independent complete proof/raw object check and exact mathematical scope'],
            overall_search_coverage='UNKNOWN; no validated target-wide denominator')
        shared.save(out/'summary.json', summary)
        print(json.dumps(dict(status=summary['status'], native_calls=summary['native_calls'],
                              summary_sha256=shared.sha(out/'summary.json', deadline))), flush=True)
        return 0
    except BaseException as error:
        shared.save(out/'failure.json', dict(timestamp=shared.stamp(), error=repr(error), case_records=rows,
            mathematical_exclusions_asserted=0, target_resolution=False, independent_approval=False,
            producer_elapsed_seconds=deadline.status()['elapsed_seconds'], automatic_resume=False,
            unfinished_description='not completed within the allocated budget',
            unmet_requirements=['Completed exact evaluation and independent validation']))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls', 'preflight', 'research'])
    for name in ['out', 'supervision-out', 'plan']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--plan-sha256', required=True)
    parser.add_argument('--driver-gate', type=Path)
    parser.add_argument('--driver-gate-sha256')
    parser.add_argument('--review-json', type=Path)
    parser.add_argument('--control-seconds', type=float, default=100)
    args = parser.parse_args()
    shared.need(re.fullmatch('[0-9a-f]{64}', args.plan_sha256), 'exact plan SHA256')
    finite(args.control_seconds, 40, 1800, 'engineering-control allowance')
    def interrupted(signum, frame):
        raise InterruptedError(f'Generic producer received signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(run(args))


if __name__ == '__main__':
    main()
