"""Small mocked supervisor-close controls; no real proc, native or signal call."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'acceleration/run_compute_command_v2.py'
SOURCE_SHA = '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17'
OLD = ROOT/'acceleration/run_compute_command.py'
OLD_SHA = '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, row):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(row, stream, indent=2, allow_nan=False)
        stream.write('\n')


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


class FakeDeadline:
    def __init__(self, remaining):
        self.initial, self.elapsed = remaining, 0

    def status(self):
        return dict(elapsed_seconds=self.elapsed, remaining_seconds=round(self.initial-self.elapsed, 9))

    def advance(self, amount):
        self.elapsed = round(self.elapsed+amount, 9)


class FakeStat:
    def __init__(self, item):
        self.item, self.parent = item, SimpleNamespace(name=str(item['pid']))

    def read_text(self):
        if self.item.get('unreadable'):
            raise OSError('synthetic unreadable stat')
        if self.item.get('bad_stat'):
            return 'synthetic malformed stat'
        fields = ['0']*20
        fields[0], fields[1], fields[2], fields[3], fields[19] = self.item['state'], '1', '4242', '4242', '123'
        return str(self.item['pid'])+' (synthetic) '+' '.join(fields)

    def exists(self):
        return True


def windows_body(path):
    node = next(row for row in ast.parse(path.read_text()).body if isinstance(row, ast.ClassDef) and row.name == 'LocalTree')
    close = next(row for row in node.body if isinstance(row, ast.FunctionDef) and row.name == 'close')
    need(isinstance(close.body[0], ast.If), 'WINDOWS_BRANCH_SHAPE')
    return [ast.dump(row, include_attributes=False) for row in close.body[0].body]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Ten small mocked cleanup/Windows-AST cases, no real proc or native call')
    need(sha(SOURCE) == SOURCE_SHA and sha(OLD) == OLD_SHA, 'SOURCE_PINS')
    spec = importlib.util.spec_from_file_location('cleanup_poll_v2_mocked', SOURCE)
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    fixtures = [
        dict(label='initial_empty', frames=[[]], remaining=2, reaped=True, scans=1, empty=True),
        dict(label='zombie_only', frames=[[dict(pid=5000, state='Z')]], remaining=2, reaped=True, scans=1, empty=True),
        dict(label='live_then_empty', frames=[[dict(pid=5000, state='D')], []], remaining=2, reaped=True, scans=2, empty=True),
        dict(label='unreadable_then_empty', frames=[[dict(pid=5000, unreadable=True)], []], remaining=2, reaped=True, scans=2, empty=True),
        dict(label='bad_stat_then_empty', frames=[[dict(pid=5000, bad_stat=True)], []], remaining=2, reaped=True, scans=2, empty=True),
        dict(label='persistent_live_budget', frames=[[dict(pid=5000, state='D')]], remaining=0.14, reaped=True, scans=3, empty=False),
        dict(label='persistent_unknown_budget', frames=[[dict(pid=5000, unreadable=True)]], remaining=0.14, reaped=True, scans=3, empty=False),
        dict(label='leader_not_reaped', frames=[[]], remaining=0.08, reaped=False, scans=1, empty=True),
        dict(label='leader_wait_clamped', frames=[[]], remaining=0.08, reaped=True, scans=1, empty=True)
    ]
    save(out/'fixtures.json', fixtures)
    results = []
    for fixture in fixtures:
        need(not deadline.status()['stop_required'], 'CALIBRATION_DEADLINE')
        case_out = out/fixture['label']
        case_out.mkdir()
        fake = FakeDeadline(fixture['remaining'])
        scans, kills, waits, sleeps = [], [], [], []

        def glob(_path, pattern):
            need(pattern == '[0-9]*/stat', 'MOCK_PROC_SCOPE')
            index = min(len(scans), len(fixture['frames'])-1)
            scans.append(index)
            return [FakeStat(item) for item in fixture['frames'][index]]

        def wait(timeout):
            waits.append(timeout)
            if not fixture['reaped']:
                fake.advance(timeout)
                raise subprocess.TimeoutExpired('synthetic_guard', timeout)
            return -9

        def sleep(amount):
            sleeps.append(amount)
            fake.advance(amount)

        tree = producer.LocalTree.__new__(producer.LocalTree)
        tree.windows, tree.pid, tree.streams = False, 4242, []
        tree.process = SimpleNamespace(wait=wait)
        tree.cleanup_observations = case_out/'linux_cleanup_observations.jsonl'
        with patch.object(producer.os, 'killpg', lambda pid, sig: kills.append([pid, int(sig)])), \
             patch.object(producer.Path, 'glob', glob), patch.object(producer.time, 'sleep', sleep):
            actual = tree.close('SYNTHETIC_STOP', fake)
        need(kills == [[4242, 9]], 'EXACT_GROUP_SIGNAL')
        need(waits == [min(5, fixture['remaining'])], 'LEADER_WAIT_DEADLINE_BOUND')
        need(actual['reaped'] is fixture['reaped'] and actual['job_active_zero_observed'] is fixture['empty'], 'TRUTHFUL_CLEANUP_FLAGS')
        need(actual['cleanup_observation_count'] == fixture['scans'] == len(scans), 'EXPECTED_SCAN_COUNT')
        need(all(0 <= amount <= 0.02 for amount in sleeps) and fake.elapsed <= fixture['remaining'], 'NO_DEADLINE_EXTENSION')
        need(bool(actual['cleanup_errors']) is (not fixture['reaped'] or not fixture['empty']), 'TRUTHFUL_UNMET_ERRORS')
        written = [json.loads(line) for line in tree.cleanup_observations.read_text().splitlines()]
        need(written == actual['cleanup_observations'], 'COMPLETE_SAVED_SCANS')
        results.append(dict(label=fixture['label'], kill_calls=kills, leader_wait_timeouts=waits,
                            sleeps=sleeps, simulated_elapsed_seconds=fake.elapsed, actual=actual))
    need(windows_body(OLD) == windows_body(SOURCE), 'WINDOWS_BRANCH_UNCHANGED')
    results.append(dict(label='windows_branch_ast_preserved', identical=True))
    need(len(results) == 10, 'CALIBRATION_POPULATION')
    save(out/'summary.json', dict(status='AUTHOR_LINUX_CLEANUP_V2_SYNTHETIC_CONTROLS_PASS',
         timestamp=datetime.now(timezone.utc).isoformat(), complete_synthetic_cases=10,
         expected_unmet_cleanup_cases=3, results=results, elapsed_seconds=deadline.status()['elapsed_seconds'],
         inputs_sha256={str(path.relative_to(ROOT)): sha(path) for path in [SOURCE, OLD, Path(__file__).resolve()]},
         fixtures_sha256=sha(out/'fixtures.json'), actual_proc_read=False, real_signal_calls=0, native_calls=0,
         scientific_launched=False, independent_approval=False,
         limitation='Same-author mocked control path; no kernel or live containment guarantee. ROOT raw/source review required'))


if __name__ == '__main__':
    main()
