"""Independent raw-record audit of observed Linux process-group containment controls."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'acceleration/results/20261002_independent_review'


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    pins = {}
    def load(p):
        with p.open('rb') as stream:
            pins[p.resolve().relative_to(ROOT).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
        return json.loads(p.read_bytes())
    def pin(p):
        with p.open('rb') as stream:
            pins[p.resolve().relative_to(ROOT).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    try:
        observed = load(BASE / 'linux_descendants_observation01/observation.json')
        need(observed['live_rows'] == [] and all(row['state'] == 'Z' for row in observed['rows']), 'fresh exact group live-empty observation')
        rows = []
        for mode, stem, budget in [('success', 'linux_descendants_success02', 45), ('timeout', 'linux_descendants_timeout01', 5)]:
            started = load(BASE / stem / 'started.json')
            supervision = BASE / ('linux_descendants_success_supervision02' if mode == 'success' else 'linux_descendants_timeout_supervision01')
            manifest = load(supervision / 'manifest.json')
            summary = load(supervision / 'summary.json')
            for log in ['stdout.log', 'stderr.log', 'progress.jsonl']:
                pin(supervision / log)
            need(started['mode'] == mode and started['same_group_observed'] is True and started['parent_group'] == started['child_group'], 'actual parent/descendant same group')
            need(started['child_pid'] != started['parent_pid'] and started['parent_group'] in observed['groups'], 'separate spawned child and freshly inspected group')
            need(manifest['seconds'] == budget and manifest['cumulative_across_commands'] is False and manifest['automatic_retry'] is False, 'per-command independent allowance')
            need(summary['invocation_id'] == manifest['invocation_id'], 'same containing invocation')
            need(summary['cleanup']['reaped'] is True and summary['cleanup']['job_active_zero_observed'] is True and summary['cleanup']['cleanup_errors'] == [] and summary['cleanup']['process_group_live_pids'] == [], 'actual reaped group live-empty cleanup')
            if mode == 'success':
                complete = load(BASE / stem / 'completed.json')
                need(complete['child_exit_code'] == 0 and complete['child_reaped'] is True, 'successful child reaped')
                need(summary['status'] == 'COMMAND_COMPLETED_VERIFICATION_PENDING' and summary['command_exit_code'] == 0, 'success control actual exit')
            else:
                need(started['requested_child_seconds'] == 60, 'long-lived timeout child fixture')
                need(summary['status'] == 'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET' and summary['stop_reason'] == 'COMMAND_TIME_LIMIT' and summary['cleanup']['actual_exit_code'] == -9 and summary['elapsed_seconds'] < 5, 'actual allocated timeout stops whole observed group')
                need(not (BASE / stem / 'completed.json').exists(), 'timeout did not complete ordinary fixture')
            rows.append({'mode': mode, 'started_path': (BASE / stem / 'started.json').relative_to(ROOT).as_posix(), 'child_pid': started['child_pid'], 'group': started['parent_group'], 'supervision_summary_path': (supervision / 'summary.json').relative_to(ROOT).as_posix(), 'outcome': 'PASS'})
        need(set(observed['groups']) == {row['group'] for row in rows}, 'exact observation covers both tested groups')
        for filename in ['command_deadline.py', 'run_compute_command.py', 'control_20261002_linux_descendants_v1.py', Path(__file__).name]:
            pin(ROOT / 'acceleration' / filename)
        for supervision in ['linux_descendants_success_supervision02', 'linux_descendants_timeout_supervision01', 'linux_descendants_observation_supervision01']:
            source = json.loads((BASE / supervision / 'manifest.json').read_bytes())['source_sha256']
            need(source == pins['acceleration/run_compute_command.py'], 'unchanged exact supervisor code source')
        for name in ['pyproject.toml', 'uv.lock']:
            pin(ROOT / 'acceleration/native_budget_env_v1' / name)
        report = {'status': 'INDEPENDENT_LINUX_COMMAND_CONTAINMENT_PASS', 'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'command': [sys.executable, *sys.argv], 'cwd': str(ROOT), 'python': platform.python_version(), 'verifier': '/root/checkpoint_audit', 'inputs_sha256': pins, 'controls': rows, 'observed_live_matching_rows': observed['live_rows'], 'preserved_prelaunch_failure': {'attempt': 'linux_descendants_success_supervision01', 'observed_exit_code': 1, 'reason': 'WSL execvpe(/tmp/conway99-native-budget-v1-env/bin/python) failed: No such file or directory', 'worker_launched': False, 'artifact': None, 'artifact_null_reason': 'Failure occurred before supervisor launch; tool transcript is the original observation, no worker receipt exists.'}, 'scope': 'Successful spawned child and stopped 60-second spawned sleeper within the same current Linux invocation process group.', 'limitations': ['Two small local nonescaping fixture invocations only; no absolute or hard-real-time termination guarantee.', 'Worker observation uses /proc and OS process-group APIs; a fresh snapshot is required before future launches.', 'Native foreground case guard alone is not a descendant guard; the independently tested outer Linux supervisor supplies the containing boundary.', 'No mathematical search, exclusion, target resolution, cross-host or daemon escape guarantee.'], 'target_resolution': False}
        with (args.out / 'summary.json').open('x', encoding='utf8') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
        print(json.dumps({'status': report['status'], 'controls': len(rows)}))
    except BaseException as error:
        with (args.out / 'failure.json').open('x', encoding='utf8') as stream:
            json.dump({'error': repr(error), 'inputs_sha256': pins}, stream, indent=2)
        raise


if __name__ == '__main__':
    main()
