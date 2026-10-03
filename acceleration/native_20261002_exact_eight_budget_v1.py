"""Linux-only, policy-aware exact-eight producer v1; no research on import.

Run through run_compute_command.py INSIDE Linux. This producer never promotes
an outcome. Mathematical gates authenticate the old formula bytes; a separate
new driver gate is mandatory for research. Historical launchers are not used.
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

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SPEC = Path(__file__).with_name(Path(__file__).stem + '_spec.md')
ENV = ROOT / 'acceleration/native_budget_env_v1'
NATIVE = ROOT / 'build/research-cadical195/source/build/cadical'
NATIVE_SHA = '021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'
UNIVERSE = ROOT / 'acceleration/results/20260930_exact_eight_campaign_preparation/campaign_manifest.json'
UNIVERSE_SHA = 'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba'
LIMITS = dict(address_space_bytes=4*1024**3, proof_file_bytes=256*1024**2,
              conflicts_per_attempt=1000000, seed=0, kill_grace_seconds=5,
              aggregate_retained_artifact_bytes=64*1024**3,
              next_attempt_artifact_reserve_bytes=1024**3,
              host_free_reserve_bytes=32*1024**3, ext4_free_reserve_bytes=2*1024**3,
              maximum_cases=64, sequential=True, automatic_retry=False,
              automatic_resume=False)
CODE = [Path(__file__), SPEC, ROOT/'acceleration/command_deadline.py',
        ROOT/'acceleration/run_compute_command.py', ENV/'pyproject.toml', ENV/'uv.lock']


def need(value, message):
    if not value:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def repository_path(name):
    need(isinstance(name, str) and name and '\\' not in name, 'literal POSIX repository path')
    candidate = Path(name)
    need(not candidate.is_absolute() and '..' not in candidate.parts, 'repository path cannot escape')
    path = (ROOT/candidate).resolve()
    need(path.is_relative_to(ROOT) and key(path) == name, 'canonical repository path')
    return path


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, data):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def progress(path, data):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data) + '\n', encoding='utf8')
    os.replace(temporary, path)


def check_time(deadline, reserve=0):
    status = deadline.status()
    need(not status['stop_required'] and status['remaining_seconds'] > reserve,
         'not completed within the allocated budget; deadline/reassessment/reserve reached')
    return status


def sha(path, deadline=None):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            if deadline is not None:
                check_time(deadline, 10)
            digest.update(block)
    return digest.hexdigest()


def pin(path, expected, bindings, deadline):
    need(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected), 'explicit SHA256')
    name = key(path)
    if name not in bindings:
        bindings[name] = sha(path, deadline)
    need(bindings[name] == expected, 'hash identity ' + name)


def observe():
    """Current Linux observations only; zombies cannot compute."""
    rows = []
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            fields = path.read_text().rsplit(')', 1)[1].split()
            if fields[0] == 'Z':
                continue
            raw = (path.parent/'cmdline').read_bytes().split(b'\0')
            argv = [part.decode('utf8', errors='replace') for part in raw if part]
            if argv and Path(argv[0]).name.lower() in {'cadical', 'drat-trim', 'drat-trim.exe'}:
                rows.append(dict(pid=int(path.parent.name), ppid=int(fields[1]),
                                 process_group=int(fields[2]), state=fields[0], command=argv))
        except (OSError, ValueError, IndexError):
            continue
    return dict(timestamp=stamp(), matching_processes=rows, zero_live_matching_observed=not rows,
                scope='Linux /proc snapshot for exact cadical/drat-trim basenames; no cross-host claim')


def resources(workspace):
    mount = subprocess.check_output(['/usr/bin/findmnt', '--target', str(workspace), '--output',
                                     'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], text=True)
    host = shutil.disk_usage(ROOT).free
    ext4 = shutil.disk_usage(workspace).free
    need('ext4' in mount.split(), 'proof workspace must be observed ext4')
    return dict(timestamp=stamp(), host_free_bytes=host, ext4_free_bytes=ext4,
                filesystem_observation=mount.strip(),
                pass_reserves=host >= LIMITS['host_free_reserve_bytes'] and
                ext4 >= LIMITS['ext4_free_reserve_bytes'])


def supervision(args, bindings, deadline):
    need(sys.platform.startswith('linux'), 'supervision and native work must run inside Linux')
    path = args.supervision_out.resolve()/'manifest.json'
    data = read(path)
    pin(ROOT/'acceleration/run_compute_command.py', data['source_sha256'], bindings, deadline)
    need(data['seconds'] <= 21600 and data['seconds'] >= args.seconds + 10,
         'producer sub-allocation must fit inside larger enclosing invocation')
    need(data['cumulative_across_commands'] is False and data['automatic_retry'] is False,
         'per-invocation supervisor policy')
    pgid = os.getpgid(0)
    leader = [part.decode() for part in (Path('/proc')/str(pgid)/'cmdline').read_bytes().split(b'\0') if part]
    need(leader and Path(leader[0]).name == 'timeout' and '--signal=KILL' in leader,
         'live outer native timeout process-group guard required')
    need(str(Path(__file__).resolve()) in data['command'] or key(Path(__file__)) in data['command'],
         'supervisor command names this exact worker')
    return dict(manifest_path=key(path), manifest_sha256=sha(path, deadline),
                invocation_id=data['invocation_id'], outer_seconds=data['seconds'],
                producer_seconds=args.seconds, process_group=pgid, guard_argv=leader,
                boundary='Producer is a contained sub-allocation; outer deadline includes uv setup and all descendants')


def authenticate(args, bindings, deadline):
    for path in CODE:
        bindings[key(path)] = sha(path, deadline)
    pin(NATIVE, NATIVE_SHA, bindings, deadline)
    if args.mode == 'controls':
        return [], []
    required = ['selection', 'batch_summary', 'encoding_gate', 'object_gate']
    for field in required:
        path = getattr(args, field)
        need(path is not None, field + ' is required')
        pin(path.resolve(), getattr(args, field + '_sha256'), bindings, deadline)
    pin(UNIVERSE, UNIVERSE_SHA, bindings, deadline)
    selection, batch = read(args.selection), read(args.batch_summary)
    encoding, objects = read(args.encoding_gate), read(args.object_gate)
    ids = selection['ordered_case_ids']
    records = batch['records']
    need(1 <= len(ids) <= 64 and len(ids) == len(set(ids)), 'distinct explicit one-to64 cases')
    need(batch['status'] == 'CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE' and
         batch['completed_formulas'] == len(ids) and not batch['pending_case_ids'] and
         batch['native_calls'] == 0 and batch['selected_case_ids'] == ids == [r['case_id'] for r in records],
         'complete unchanged exact explicit formula preparation')
    need(selection['campaign_manifest_path'] == key(UNIVERSE) and
         selection['campaign_manifest_sha256'] == UNIVERSE_SHA, 'fixed universe identity')
    for report, status in [(encoding, 'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'),
                           (objects, 'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_OBJECT_CALIBRATION_PASS')]:
        need(report['status'] == status and report['selected_case_ids'] == ids and
             report['complete_formulas'] == len(ids) and
             report['batch_summary_path'] == key(args.batch_summary) and
             report['batch_summary_sha256'] == args.batch_summary_sha256 and
             report['selection_path'] == key(args.selection) and
             report['selection_sha256'] == args.selection_sha256, 'exact historical mathematical gate scope')
    need(objects['inputs_sha256'][key(args.encoding_gate)] == args.encoding_gate_sha256,
         'object calibration uses same encoding gate')
    approved = {row['case_id']: row for row in encoding['checked_cases']}
    need(set(approved) == set(ids) and len(approved) == len(ids), 'all selected literal encodings checked')
    universe = {row['case_id']: row for row in read(UNIVERSE)['records']}
    need(len(universe) == 792, 'frozen792 literal universe')
    for record in tqdm(records, desc='Reauthenticate selected exact formulas', mininterval=1):
        cid = record['case_id']
        need(cid in universe and record['case_index'] == universe[cid]['case_index'] and
             cid == 'exact_eight_' + record['full_count_profile_sha256'], 'stable case identity')
        for descriptor in record['files'].values():
            path = repository_path(descriptor['path'])
            pin(path, descriptor['sha256'], bindings, deadline)
            need(path.stat().st_size == descriptor['bytes'], 'prepared artifact exact length')
        for name, field in [('instance.cnf', 'cnf'), ('model.json', 'model'), ('scope.json', 'scope'),
                            ('selected_profile.json', 'profile')]:
            descriptor = record['files'][name]
            need(approved[cid][field+'_path'] == descriptor['path'] and
                 approved[cid][field+'_sha256'] == descriptor['sha256'] and
                 encoding['inputs_sha256'][descriptor['path']] == descriptor['sha256'] and
                 objects['inputs_sha256'][descriptor['path']] == descriptor['sha256'],
                 'formula identity in both old mathematical gates')
        scope = read(repository_path(record['files']['scope.json']['path']))
        need(scope['campaign_case_id'] == cid and scope['within_group_column_caps_encoded'] and
             not any(scope[field] for field in ['cross_group_column_caps_encoded', 'residual_D_encoded',
                                               'arc_pruning_used', 'orbit_coverage_used', 'target_graph']),
             'fixed-support Gram scope and explicitly omitted constraints')
        with repository_path(record['files']['instance.cnf']['path']).open('rb') as stream:
            need(stream.readline() == f"p cnf {record['variables']} {record['clauses']}\n".encode(),
                 'actual exact DIMACS dimensions')
    if args.mode == 'research':
        need(args.driver_gate is not None, 'new independently calibrated driver gate required')
        pin(args.driver_gate, args.driver_gate_sha256, bindings, deadline)
        driver = read(args.driver_gate)
        need(driver['status'] == 'INDEPENDENT_EXACT_EIGHT_POLICY_NATIVE_DRIVER_PASS', 'new driver calibration PASS')
        for path in CODE + [NATIVE]:
            need(driver['inputs_sha256'].get(key(path)) == bindings[key(path)], 'new gate binds changed execution source')
    return ids, records


def native_command(cnf, proof, seconds):
    return ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{seconds:.6f}s',
            '/usr/bin/prlimit', '--as=4294967296:4294967296', '--fsize=268435456:268435456',
            '--core=0:0', str(NATIVE), '--no-binary', '--seed=0', '-c', '1000000', str(cnf), str(proof)]


def classify(code, text, proof_bytes):
    statuses = [line.strip() for line in text.splitlines() if line.startswith('s ')]
    conflicts = re.findall(r'^c\s+conflicts:\s*([\d,]+)', text, re.M)
    last = int(conflicts[-1].replace(',', '')) if conflicts else None
    if code == 20 and statuses == ['s UNSATISFIABLE'] and proof_bytes is not None and 0 < proof_bytes < LIMITS['proof_file_bytes']:
        kind = 'UNSAT_TRACE_PENDING_COMPLETE_REPLAY'
    elif code == 10 and statuses == ['s SATISFIABLE']:
        kind = 'SAT_RAW_OBJECT_PENDING_REVIEW'
    elif code == 124:
        kind = 'UNKNOWN_WALL_LIMIT'
    elif code == 153 or proof_bytes is not None and proof_bytes >= LIMITS['proof_file_bytes']:
        kind = 'UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'
    elif code == 0 and last is not None and last >= LIMITS['conflicts_per_attempt']:
        kind = 'UNKNOWN_CONFLICT_LIMIT'
    else:
        kind = 'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'
    return dict(interpretation=kind, actual_exit_code=code, native_status_lines=statuses,
                observed_conflicts=last, observed_conflicts_null_reason=None if last is not None else
                'Counter absent from raw native output.', mathematical_approval=False)


def execute(command, folder, deadline, progress_path, label):
    started = time.monotonic()
    code, stopped = None, None
    with (folder/'solver.stdout.log').open('xb') as stdout, (folder/'solver.stderr.log').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        last = -float('inf')
        try:
            need(os.getpgid(process.pid) == os.getpgid(0), 'child must remain in enclosing Linux process group')
            while process.poll() is None:
                status = deadline.status()
                if status['stop_required'] or status['remaining_seconds'] <= 20:
                    stopped = 'PRODUCER_DEADLINE_OR_REASSESSMENT'
                    process.terminate()
                    try:
                        process.wait(timeout=6)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break
                if time.monotonic() - last >= 10:
                    observation = observe()
                    progress(progress_path, dict(timestamp=stamp(), phase='native', case=label,
                        solver_pid=process.pid, current_processes=observation, **status))
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
    after = observe()
    receipt = dict(schema='EXACT_EIGHT_POLICY_NATIVE_RECEIPT_V1', timestamp=stamp(), command=command,
        cwd=str(ROOT), actual_exit_code=code, wall_seconds=time.monotonic()-started,
        solver_guard_pid=process.pid, process_group=os.getpgid(0), producer_stop_reason=stopped,
        reaped=True, processes_after=after, limits=LIMITS,
        stdout=key(folder/'solver.stdout.log'), stdout_sha256=sha(folder/'solver.stdout.log', deadline),
        stderr=key(folder/'solver.stderr.log'), stderr_sha256=sha(folder/'solver.stderr.log', deadline),
        mathematical_approval=False)
    save(folder/'solver.receipt.json', receipt)
    need(after['zero_live_matching_observed'], 'native process state not empty; no further launches')
    return receipt


def one_case(args, record, out, deadline, bindings, requested=None):
    folder = out/f"case_{record['case_index']:04d}"
    folder.mkdir()
    before = observe()
    save(folder/'processes_before.json', before)
    need(before['zero_live_matching_observed'], 'live solver/checker prevents new launch')
    workspace = Path(tempfile.mkdtemp(prefix=f"conway99-policy-v1-{record['case_index']:04d}-", dir='/tmp'))
    resource = resources(workspace)
    save(folder/'workspace.json', dict(path=str(workspace), timestamp=stamp(), deletion_requested=False,
                                     availability='LOCAL_ONLY', future_availability='UNKNOWN'))
    save(folder/'resources.json', resource)
    need(resource['pass_reserves'], 'host/ext4 reserve before native work')
    cnf = repository_path(record['files']['instance.cnf']['path'])
    pin(cnf, record['files']['instance.cnf']['sha256'], bindings, deadline)
    check_time(deadline, 35)
    seconds = deadline.child_seconds(requested or args.case_seconds, reserve_seconds=35)
    proof = workspace/'proof.drat'
    command = native_command(cnf, proof, seconds)
    launch = dict(schema='EXACT_EIGHT_POLICY_NATIVE_LAUNCH_V1', timestamp=stamp(),
        case_id=record['case_id'], case_index=record['case_index'], attempt_id=args.attempt_id,
        command=command, native_wall_limit_seconds=seconds, requested_case_seconds=requested or args.case_seconds,
        deadline_before_launch=deadline.status(), cnf=record['files']['instance.cnf'],
        ext4_proof=str(proof), limits=LIMITS, numerical_acceptance='Exact CNF only; no floating-point threshold')
    save(folder/'launch.json', launch)
    print(json.dumps(dict(state='POLICY_NATIVE_LAUNCH', case_id=record['case_id'], seconds=seconds)), flush=True)
    receipt = execute(command, folder, deadline, out/'progress.json', record['case_id'])
    copied = None
    if proof.is_file():
        need(proof.stat().st_size <= LIMITS['proof_file_bytes'], 'proof file limit')
        destination = folder/'proof.drat'
        digest = hashlib.sha256()
        with proof.open('rb') as source, destination.open('xb') as target:
            for block in iter(lambda: source.read(1048576), b''):
                check_time(deadline, 10)
                target.write(block)
                digest.update(block)
        copied = dict(path=key(destination), sha256=digest.hexdigest(), bytes=destination.stat().st_size,
                      linux_original_path=str(proof), source_sha256=sha(proof, deadline),
                      availability='LOCAL_ONLY', complete_proof=False)
        need(copied['sha256'] == copied['source_sha256'], 'full raw proof copy equality')
    outcome = classify(receipt['actual_exit_code'], (folder/'solver.stdout.log').read_text(errors='replace'),
                       copied['bytes'] if copied else None)
    row = dict(schema='EXACT_EIGHT_POLICY_NATIVE_CASE_V1', timestamp=stamp(), case_id=record['case_id'],
        case_index=record['case_index'], attempt_id=args.attempt_id, formula=record,
        launch_path=key(folder/'launch.json'), launch_sha256=sha(folder/'launch.json', deadline),
        native_receipt_path=key(folder/'solver.receipt.json'),
        native_receipt_sha256=sha(folder/'solver.receipt.json', deadline), native_receipt=receipt,
        raw_proof=copied, outcome=outcome, native_calls=1, independent_approval=False,
        target_resolution=False, target_graph=False,
        limitations=['A literal fixed-support Gram instance only; cross-group caps and residualD omitted.',
                     'Raw UNSAT requires complete independent proof replay; SAT requires independent raw assignment decoding.'])
    save(folder/'summary.json', row)
    return dict(case_id=record['case_id'], case_index=record['case_index'],
                summary_path=key(folder/'summary.json'), summary_sha256=sha(folder/'summary.json', deadline),
                interpreted_result=outcome['interpretation'], actual_exit_code=receipt['actual_exit_code'],
                wrapped_wall_seconds=receipt['wall_seconds'], allocated_native_wall_seconds=seconds,
                ext4_trace_bytes=copied['bytes'] if copied else None)


def controls(args, out, deadline, bindings):
    rows = []
    for index, (label, raw) in enumerate([
        ('tiny_sat', b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n'),
        ('tiny_unsat', b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n')]):
        path = out/(label+'.cnf')
        path.write_bytes(raw)
        record = dict(case_id=label, case_index=index,
                      files={'instance.cnf': dict(path=key(path), sha256=sha(path), bytes=len(raw))})
        rows.append(one_case(args, record, out, deadline, bindings, requested=10))
    folder = out/'timeout_control'
    folder.mkdir()
    command = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', '0.200000s',
               sys.executable, '-c', 'import time; time.sleep(30)']
    save(folder/'launch.json', dict(command=command, expected_exit_code=124,
                                  purpose='Native foreground timeout; no scientific search'))
    receipt = execute(command, folder, deadline, out/'progress.json', 'timeout_control')
    return rows, dict(path=key(folder/'solver.receipt.json'), sha256=sha(folder/'solver.receipt.json'),
                      actual_exit_code=receipt['actual_exit_code'])


def run(args):
    need(args.attempt_id and re.fullmatch('[A-Za-z0-9_-]+', args.attempt_id), 'safe explicit attempt ID')
    need(re.fullmatch('[0-9a-f]{40}', args.source_commit), 'caller records exact source commit')
    need(math.isfinite(args.case_seconds) and 0 < args.case_seconds <= args.seconds - 35, 'explicit case allocation')
    # One immutable internal deadline for every producer phase and all retries
    # (there are no retries). Outer supervisor separately enforces the full command.
    deadline = CommandDeadline(args.seconds, allocation_reason=args.allocation_reason)
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'saved outputs remain in existing repository')
    out.mkdir(parents=True, exist_ok=False)
    rows, ids, bindings, stop = [], [], {}, 'PREPARATION'
    try:
        supervisor = supervision(args, bindings, deadline)
        ids, records = authenticate(args, bindings, deadline)
        manifest = dict(schema='EXACT_EIGHT_POLICY_NATIVE_BATCH_V1', timestamp=stamp(),
            mode=args.mode, source_commit=args.source_commit, source_commit_provenance='Caller-supplied exact commit; source hashes bind working files.',
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            platform=platform.platform(), tqdm_version=__import__('tqdm').__version__, inputs_sha256=bindings,
            limits=LIMITS, producer_seconds=args.seconds, requested_case_seconds=args.case_seconds,
            allocation_reason=args.allocation_reason, supervision=supervisor, selected_case_ids=ids,
            attempt_id=args.attempt_id, independent_approval=False, target_resolution=False,
            historical_gate_reuse='Rehash gate bytes and selected formula artifacts; do not rerun or rehash whole historical20k input closure. Historical execution approval is not transferred.',
            success_criterion='Preserve exact selected case receipts/raw proof bytes or raw SAT assignment, stop safely, and retain checkpoints.',
            verification_criterion='Separate new driver calibration; independent complete DRAT replay or raw SAT-factor checking with exact scope.',
            automatic_retry=False, automatic_resume=False)
        save(out/'manifest.json', manifest)
        timeout = None
        if args.mode == 'preflight':
            stop = 'PREFLIGHT_COMPLETE_NO_SOLVER_CALLS'
        elif args.mode == 'controls':
            rows, timeout = controls(args, out, deadline, bindings)
            stop = 'ENGINEERING_CONTROLS_COMPLETE_PENDING_INDEPENDENT_REVIEW'
        else:
            stop = 'ALL_EXPLICITLY_SELECTED_CASES_ATTEMPTED'
            for record in tqdm(records, desc='Policy-aware native exact-eight', mininterval=1):
                check_time(deadline, 35)
                host = sum(path.stat().st_size for path in out.rglob('*') if path.is_file())
                ext4 = sum(row['ext4_trace_bytes'] or 0 for row in rows)
                need(host+ext4+LIMITS['next_attempt_artifact_reserve_bytes'] <= LIMITS['aggregate_retained_artifact_bytes'],
                     'aggregate retained artifact reserve')
                row = one_case(args, record, out, deadline, bindings)
                rows.append(row)
                save(out/f'checkpoint_{len(rows):02d}.json', dict(timestamp=stamp(), case_records=rows,
                    selected_case_ids=ids, pending_case_ids=ids[len(rows):], independent_approval=False,
                    target_resolution=False, automatic_resume=False))
                if row['interpreted_result'] != 'UNSAT_TRACE_PENDING_COMPLETE_REPLAY':
                    stop = row['interpreted_result']
                    break
        summary = dict(schema='EXACT_EIGHT_POLICY_NATIVE_BATCH_RESULT_V1', timestamp=stamp(),
            status='POLICY_NATIVE_OUTPUTS_PENDING_INDEPENDENT_VERIFICATION', mode=args.mode,
            manifest_path=key(out/'manifest.json'), manifest_sha256=sha(out/'manifest.json', deadline),
            selected_case_ids=ids, case_records=rows, attempted_evaluations=len(rows),
            completed_evaluations=len(rows), pending_case_ids=ids[len(rows):],
            native_calls=len(rows), timeout_control=timeout, stop_reason=stop,
            producer_elapsed_seconds=deadline.status()['elapsed_seconds'], limits=LIMITS,
            mathematical_exclusions_asserted=0, independent_approval=False, target_resolution=False,
            automatic_resume=False, unmet_requirements=['Independent outcome/proof review'],
            overall_search_coverage='UNKNOWN; no validated target-wide denominator')
        save(out/'summary.json', summary)
        print(json.dumps(dict(status=summary['status'], stop_reason=stop, attempted=len(rows),
                              summary_sha256=sha(out/'summary.json', deadline))), flush=True)
        return 0
    except BaseException as error:
        save(out/'failure.json', dict(timestamp=stamp(), error=repr(error), case_records=rows,
            selected_case_ids=ids, pending_case_ids=ids[len(rows):], stop_reason=stop,
            producer_elapsed_seconds=deadline.status()['elapsed_seconds'],
            unfinished_description='not completed within the allocated budget',
            unmet_requirements=['Complete selected evaluation and independent review'],
            independent_approval=False, mathematical_exclusions_asserted=0, automatic_resume=False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['controls', 'preflight', 'research'])
    for name in ['out', 'supervision-out']:
        parser.add_argument('--'+name, type=Path, required=True)
    for name in ['selection', 'batch-summary', 'encoding-gate', 'object-gate', 'driver-gate']:
        parser.add_argument('--'+name, type=Path)
        parser.add_argument('--'+name+'-sha256')
    for name in ['attempt-id', 'source-commit', 'allocation-reason']:
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--case-seconds', type=float, required=True)
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise InterruptedError(f'Producer received signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(run(args))


if __name__ == '__main__':
    main()
