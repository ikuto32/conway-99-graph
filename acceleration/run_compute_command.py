"""Per-command computation supervision. No cumulative allowance or research on import."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import ctypes
import hashlib
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]


def save(path, data):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


class LocalTree:
    """Local Windows Job or Linux group; remote/WSL transport is not containment."""
    def __init__(self, command, cwd, out, seconds):
        self.windows = os.name == 'nt'
        self.streams = []
        if self.windows:
            if any(Path(arg).name.lower() in {'wsl', 'wsl.exe', 'ssh', 'ssh.exe'} for arg in command):
                raise ValueError('Run supervision inside the compute OS; transport is not containment')
            from run_20260930_exact_eight_four_builds_v2 import SuspendedTree
            self.tree = SuspendedTree(command, cwd, out / 'stdout.log', out / 'stderr.log')
            try:
                self.tree.resume(seconds)
            except BaseException:
                self.tree.request_stop('RELEASE_FAILURE')
                self.tree.cleanup()
                raise
            self.pid = int(self.tree.pi.dwProcessId)
        else:
            guard = shutil.which('timeout')
            if not sys.platform.startswith('linux') or guard is None:
                raise ValueError('Linux with GNU timeout or Windows Job containment required')
            self.streams = [(out / 'stdout.log').open('xb'), (out / 'stderr.log').open('xb')]
            # Native guard survives supervisor failure; internal children share it.
            wrapped = [guard, '--signal=KILL', f'{seconds:.6f}s', *command]
            try:
                self.process = subprocess.Popen(wrapped, cwd=cwd, stdout=self.streams[0],
                                                stderr=self.streams[1], start_new_session=True)
            except BaseException:
                for stream in self.streams:
                    stream.close()
                raise
            self.pid = self.process.pid

    def poll(self):
        return self.tree.poll() if self.windows else self.process.poll()

    def resources(self):
        if self.windows:
            from build_20260930_exact_eight_parallel_batch import Accounting, ExtendedLimit
            accounting, memory = Accounting(), ExtendedLimit()
            api, job = self.tree.api, self.tree.job
            job.check(api.QueryInformationJobObject(job.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None))
            job.check(api.QueryInformationJobObject(job.handle, 9, ctypes.byref(memory), ctypes.sizeof(memory), None))
            return dict(active_processes=accounting.ActiveProcesses,
                        cpu_seconds=(accounting.TotalUserTime + accounting.TotalKernelTime) / 10**7,
                        peak_job_memory_bytes=memory.PeakJobMemoryUsed,
                        gpu_utilization=None, gpu_unavailable_reason='Supply device-specific metrics in the progress JSON when applicable')
        return dict(active_processes=None, cpu_seconds=None, peak_job_memory_bytes=None,
                    unavailable_reason='No portable live whole-group resource accounting; supply workload metrics in progress JSON',
                    gpu_utilization=None, gpu_unavailable_reason='Supply device-specific metrics in the progress JSON when applicable')

    def close(self, reason):
        if self.windows:
            self.tree.request_stop(reason)
            return self.tree.cleanup()
        try:
            os.killpg(self.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        code = self.process.wait(timeout=5)
        # Observe live members, excluding zombies which cannot compute.
        live = []
        for path in Path('/proc').glob('[0-9]*/stat'):
            try:
                fields = path.read_text().rsplit(')', 1)[1].split()
                if int(fields[2]) == self.pid and fields[0] != 'Z':
                    live.append(int(path.parent.name))
            except (OSError, ValueError, IndexError):
                continue
        for stream in self.streams:
            stream.close()
        return dict(reaped=True, job_active_zero_observed=not live, actual_exit_code=code,
                    cleanup_errors=[] if not live else ['Live Linux process-group members remain'],
                    process_group_live_pids=live)


def review_evidence(row, invocation, elapsed):
    required = ['observations', 'remaining_cost', 'benefit_and_alternatives', 'uncertainty']
    if row.get('invocation_id') != invocation or any(not isinstance(row.get(k), str) or not row[k].strip() for k in required):
        raise ValueError('Review must identify this invocation and record diagnostics, cost, alternatives and uncertainty')
    observed = row.get('observed_at_elapsed_seconds')
    if isinstance(observed, bool) or not isinstance(observed, (float, int)) or not math.isfinite(observed) or not 0 <= elapsed - observed <= 60:
        raise ValueError('Review observation must be recent and cannot be from the future')
    probability = row.get('success_probability')
    if probability is not None:
        if isinstance(probability, bool) or not isinstance(probability, (float, int)) or not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('Invalid probability')
        if not row.get('calibration_evidence'):
            raise ValueError('A probability requires calibration evidence')
        if probability < .05 and row.get('decision') == 'continue' and not row.get('low_probability_continuation_reason'):
            raise ValueError('Below 5% requires review justification, not an automatic stop')
    if row.get('decision') not in {'continue', 'stop', 'change_method'}:
        raise ValueError('Review decision required')
    return row


def run(args):
    if not args.command:
        raise ValueError('A command is required after --')
    if args.command[0] == '--':
        args.command = args.command[1:]
    if not args.command:
        raise ValueError('Empty command')
    if not args.success_criterion.strip() or not args.verification_criterion.strip():
        raise ValueError('Predeclared success and independent verification criteria required')
    reserve = args.shutdown_reserve_seconds
    if not math.isfinite(reserve) or not 0 < reserve < args.seconds:
        raise ValueError('Shutdown reserve must fit inside this command allocation')
    deadline = CommandDeadline(args.seconds, allocation_reason=args.allocation_reason,
                               review_interval_seconds=args.reassessment_seconds)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    invocation = uuid.uuid4().hex
    manifest = dict(schema_version=1, invocation_id=invocation, timestamp=datetime.now(timezone.utc).isoformat(),
                    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    command=args.command, cwd=str(args.cwd.resolve()), seconds=args.seconds,
                    allocation_reason=args.allocation_reason, success_criterion=args.success_criterion,
                    verification_criterion=args.verification_criterion,
                    reassessment_seconds=args.reassessment_seconds, shutdown_reserve_seconds=reserve,
                    cumulative_across_commands=False, automatic_retry=False,
                    process_scope='Local non-escaping process tree only; remote/daemonized compute is unsupported')
    save(out / 'manifest.json', manifest)
    tree = None
    cleanup = None
    reason = 'LAUNCH_FAILED'
    code = None
    error = None
    review_digest = None
    last_heartbeat = -float('inf')
    try:
        allowed = deadline.child_seconds(args.seconds, reserve_seconds=reserve)
        if allowed <= 0:
            raise ValueError('No time remains to launch')
        tree = LocalTree(args.command, args.cwd.resolve(), out, allowed)
        while True:
            status = deadline.status()
            elapsed = status['elapsed_seconds']
            if args.review_json and args.review_json.exists():
                raw = args.review_json.read_bytes()
                if len(raw) > 65536:
                    raise ValueError('Review exceeds 64KiB')
                sha = hashlib.sha256(raw).hexdigest()
                if sha != review_digest:
                    row = review_evidence(json.loads(raw), invocation, elapsed)
                    review_digest = sha
                    with (out / 'reviews.jsonl').open('a', encoding='utf8') as stream:
                        stream.write(json.dumps(row) + '\n')
                    if row['decision'] != 'continue':
                        reason = 'REVIEW_' + row['decision'].upper()
                        break
                    deadline.review(evidence=json.dumps(row))
                    status = deadline.status()
            code = tree.poll()
            if code is not None:
                reason = 'COMMAND_EXITED'
                break
            if status['remaining_seconds'] <= reserve:
                reason = 'COMMAND_TIME_LIMIT'
                break
            if status['review_due']:
                reason = 'REASSESSMENT_REQUIRED'
                break
            if elapsed - last_heartbeat >= 30:
                progress = None
                progress_error = 'No workload progress file supplied'
                if args.progress_json:
                    try:
                        if args.progress_json.stat().st_size > 65536:
                            raise ValueError('Progress exceeds 64KiB')
                        progress = json.loads(args.progress_json.read_bytes())
                        progress_error = None
                    except (OSError, ValueError) as ex:
                        progress_error = str(ex)
                heartbeat = dict(**status, timestamp=datetime.now(timezone.utc).isoformat(),
                                 resources=tree.resources(), workload_progress=progress,
                                 progress_unavailable_reason=progress_error)
                with (out / 'progress.jsonl').open('a', encoding='utf8') as stream:
                    stream.write(json.dumps(heartbeat) + '\n')
                print(json.dumps(dict(invocation_id=invocation, **status)), flush=True)
                last_heartbeat = elapsed
            time.sleep(min(.1, max(.001, status['remaining_seconds'] - reserve)))
    except BaseException as ex:
        reason = 'SUPERVISION_ERROR'
        error = repr(ex)
    finally:
        if tree is not None:
            try:
                cleanup = tree.close(reason)
            except BaseException as ex:
                cleanup = dict(reaped=False, job_active_zero_observed=False, cleanup_errors=[repr(ex)])
    observed = deadline.status()
    contained = cleanup is not None and cleanup.get('reaped') and cleanup.get('job_active_zero_observed') and not cleanup.get('cleanup_errors')
    completed = reason == 'COMMAND_EXITED' and code == 0 and contained and not observed['deadline_reached']
    result = dict(invocation_id=invocation, status='COMMAND_COMPLETED_VERIFICATION_PENDING' if completed else 'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET',
                  stop_reason=reason, command_exit_code=code, error=error, cleanup=cleanup,
                  elapsed_seconds=observed['elapsed_seconds'], deadline_reached=observed['deadline_reached'],
                  hard_limit_observed=observed['elapsed_seconds'] <= args.seconds and contained,
                  guarantees='Only the observed process outcome; no scientific correctness/completeness/optimality claim',
                  verification_pending=True, unmet_requirements=[args.verification_criterion] + ([] if completed else [args.success_criterion]),
                  unfinished_description=None if completed else 'not completed within the allocated budget',
                  preserved_outputs=str(out), cumulative_across_commands=False, automatic_resume=False)
    save(out / 'summary.json', result)
    print(json.dumps(result), flush=True)
    return 0 if completed else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--allocation-reason', required=True)
    parser.add_argument('--success-criterion', required=True)
    parser.add_argument('--verification-criterion', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cwd', type=Path, default=ROOT)
    parser.add_argument('--reassessment-seconds', type=float, default=1800)
    parser.add_argument('--shutdown-reserve-seconds', type=float, default=5)
    parser.add_argument('--progress-json', type=Path)
    parser.add_argument('--review-json', type=Path)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    raise SystemExit(run(parser.parse_args()))


if __name__ == '__main__':
    main()
