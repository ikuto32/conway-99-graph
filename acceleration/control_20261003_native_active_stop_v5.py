"""Finite Linux live-stop evidence; no execution on import and no scientific input."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SAT = ROOT/'acceleration/run_20261003_unrestricted_native_v2.sh'
SAT_SHA = '309a36d272ce292dc4484bd25ee1cf9c9093a63d99eee12a1329fcb64f8f17f8'
CADICAL = ROOT/'build/research-cadical195/source/build/cadical'
CADICAL_SHA = '021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'
MIXED = ROOT/'acceleration/results/20261003_hypergraph_ternary_mixed_build01/hypergraph_ternary_mixed'
MIXED_SHA = '56e0ecf4295f72a51c58a6957da2d4e32787a2514e38866e41172eb79738cf09'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, row):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(row, stream, indent=2)
        stream.write('\n')


def process(pid):
    try:
        directory = Path('/proc')/str(pid)
        fields = (directory/'stat').read_text().rsplit(')', 1)[1].split()
        status = dict(line.split(':', 1) for line in (directory/'status').read_text().splitlines() if ':' in line)
        return dict(pid=int(pid), ppid=int(fields[1]), pgid=int(fields[2]), session=int(fields[3]),
                    state=fields[0], start_ticks=int(fields[19]),
                    real_uid=int(status['Uid'].split()[0]), effective_uid=int(status['Uid'].split()[1]),
                    comm=(directory/'comm').read_text().strip())
    except (OSError, ValueError, IndexError, KeyError):
        return None


def snapshot():
    return {int(p.name): row for p in Path('/proc').glob('[0-9]*') if p.is_dir()
            for row in [process(int(p.name))] if row is not None}


def observation_context():
    return dict(schema='LINUX_PROC_IDENTITY_CONTEXT_V1',
                boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                pid_namespace=os.readlink('/proc/self/ns/pid'),
                clock_ticks_per_second=os.sysconf('SC_CLK_TCK'))


def check_context(row):
    need(type(row) is dict and set(row) == {'schema', 'boot_id', 'pid_namespace', 'clock_ticks_per_second'}, 'CONTEXT_SCHEMA')
    need(row['schema'] == 'LINUX_PROC_IDENTITY_CONTEXT_V1'
         and type(row['boot_id']) is str
         and re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', row['boot_id']) is not None
         and type(row['pid_namespace']) is str and re.fullmatch(r'pid:\[[0-9]+\]', row['pid_namespace']) is not None
         and type(row['clock_ticks_per_second']) is int and row['clock_ticks_per_second'] > 0, 'CONTEXT_SCHEMA')


def check_process(row, current=False):
    need(type(row) is dict and set(row) == {'pid', 'ppid', 'pgid', 'session', 'state', 'start_ticks', 'real_uid', 'effective_uid', 'comm'}, 'PROCESS_SCHEMA')
    need(all(type(row[key]) is int for key in ['pid', 'ppid', 'pgid', 'session', 'start_ticks', 'real_uid', 'effective_uid'])
         and row['pid'] > 0 and row['ppid'] >= 0
         and (row['pgid'] >= 0 and row['session'] >= 0 if current else row['pgid'] > 0 and row['session'] > 0)
         and row['start_ticks'] >= 0 and row['real_uid'] >= 0 and row['effective_uid'] >= 0
         and type(row['state']) is str and row['state'] in ['R', 'S', 'D', 'Z', 'T', 't', 'X', 'x', 'K', 'W', 'P', 'I']
         and type(row['comm']) is str and bool(row['comm']), 'PROCESS_SCHEMA')


def assessment(saved_context, current_context, guard, known, rows, unreadable_pids):
    # Pure metadata comparison, also used by synthetic controls. No /proc or child call.
    check_context(saved_context)
    check_context(current_context)
    check_process(guard)
    need(guard['pid'] == guard['pgid'] == guard['session'] and guard['comm'] == 'timeout'
         and guard['effective_uid'] == guard['real_uid'] == 1000, 'ORIGINAL_GUARD_IDENTITY')
    need(type(known) is list and known and all(type(key) is list and len(key) == 2
         and all(type(value) is int for value in key) and key[0] > 0 and key[1] >= 0 for key in known), 'KNOWN_IDENTITY_SCHEMA')
    identities = {tuple(key) for key in known}
    need(len(identities) == len(known) and (guard['pid'], guard['start_ticks']) in identities, 'KNOWN_IDENTITY_SCHEMA')
    need(type(rows) is list and type(unreadable_pids) is list
         and all(type(pid) is int and pid > 0 for pid in unreadable_pids), 'CURRENT_SNAPSHOT_SCHEMA')
    for row in rows:
        check_process(row, current=True)
    need(len({row['pid'] for row in rows}) == len(rows), 'CURRENT_SNAPSHOT_SCHEMA')
    selected = [row for row in rows if (row['pid'], row['start_ticks']) in identities]
    live = [row for row in selected if row['state'] != 'Z']
    numeric_group_live = [row for row in rows if row['pgid'] == guard['pgid'] and row['state'] != 'Z']
    leader = next((row for row in rows if row['pid'] == guard['pid']), None)
    stage = None
    original_live = numeric_group_live
    new_live = []
    if saved_context != current_context:
        generation, stage = 'UNKNOWN_CONTEXT_CHANGED', 'CONTEXT_CHANGED_UNKNOWN'
    elif unreadable_pids:
        generation, stage = 'UNKNOWN_UNREADABLE_PROC_OBJECTS', 'PROC_OBSERVATION_UNKNOWN'
    elif leader is not None and leader['start_ticks'] != guard['start_ticks']:
        if leader['pgid'] == guard['pgid']:
            generation = 'NUMERIC_GROUP_REUSED_NEW_LEADER'
            original_live, new_live = [], numeric_group_live
        elif numeric_group_live:
            generation, stage = 'UNKNOWN_LEADER_PID_REUSED_WITH_GROUP_MEMBERS', 'GROUP_GENERATION_UNKNOWN'
        else:
            generation = 'LEADER_PID_REUSED_NO_CURRENT_GROUP'
    elif leader is not None:
        need(leader['pgid'] == guard['pgid'] and leader['session'] == guard['session'], 'ORIGINAL_GUARD_CURRENT_IDENTITY')
        generation = 'ORIGINAL_LEADER_IDENTITY_PRESENT'
    elif numeric_group_live:
        generation = 'LEADER_ABSENT_WITH_LIVE_GROUP_MEMBERS'
    else:
        generation = 'NO_CURRENT_LIVE_GROUP_MEMBERS'
    if stage is None and (live or original_live):
        stage = 'LIVE_PROCESS_AFTER_STOP'
    return dict(context_matched=saved_context == current_context, group_generation=generation,
                current_group_leader=leader, selected_current_objects=selected, selected_live=live,
                numeric_group_live=numeric_group_live, original_generation_group_live=original_live,
                new_generation_group_live=new_live, unreadable_pids=unreadable_pids,
                no_selected_live_observed=None if generation.startswith('UNKNOWN') else not live,
                no_original_generation_group_live_observed=None if generation.startswith('UNKNOWN') else not original_live,
                veto_stage=stage)


def saved_identity(launch, ready, records):
    need(type(launch) is dict and type(ready) is dict and type(records) is list and records, 'SAVED_OBJECT_SCHEMA')
    need(launch.get('schema') == 'NATIVE_ACTIVE_STOP_CASE_V3' and ready.get('schema') == 'NATIVE_ACTIVE_STOP_LIVE_READY_V3', 'V3_CONTEXT_REQUIRED')
    context, guard = launch['observation_context'], launch['original_guard']
    check_context(context)
    check_process(guard)
    check_context(ready['observation_context'])
    check_process(ready['original_guard'])
    need(type(ready['observed_euid']) is int and ready['observed_euid'] == 1000
         and type(ready['original_group']) is int and ready['original_group'] == guard['pgid']
         and type(launch['original_group']) is int and launch['original_group'] == guard['pgid'], 'READY_UID_GROUP')
    need(ready['observation_context'] == context and ready['original_guard'] == guard, 'SAVED_CONTEXT_IDENTITY')
    need(type(ready['first_live_elapsed']) in [int, float] and type(ready['last_live_elapsed']) in [int, float]
         and math.isfinite(ready['first_live_elapsed']) and math.isfinite(ready['last_live_elapsed'])
         and 0 <= ready['first_live_elapsed'] <= ready['last_live_elapsed']
         and ready['last_live_elapsed']-ready['first_live_elapsed'] >= 1, 'READY_LIVE_INTERVAL')
    known = {(guard['pid'], guard['start_ticks'])}
    for record in records:
        need(type(record) is dict and type(record['children']) is list, 'SAVED_OBJECT_SCHEMA')
        check_context(record['observation_context'])
        check_process(record['original_guard'])
        need(record['observation_context'] == context and record['original_guard'] == guard, 'SAVED_CONTEXT_IDENTITY')
        for row in [record['worker']] + record['children']:
            check_process(row)
            need(row['pgid'] == guard['pgid'] and row['effective_uid'] == 1000, 'SAVED_GROUP_UID')
            known.add((row['pid'], row['start_ticks']))
    need(type(ready['live_children']) is list and ready['live_children'], 'READY_OBSERVED_IDENTITY')
    for row in ready['live_children']:
        check_process(row)
        need((row['pid'], row['start_ticks']) in known and row['pgid'] == guard['pgid']
             and row['effective_uid'] == 1000 and row['state'] != 'Z', 'READY_OBSERVED_IDENTITY')
    return context, guard, [list(key) for key in sorted(known)]


def descendants(rows, start):
    included = {start}
    while True:
        extra = {pid for pid, row in rows.items() if row['ppid'] in included}
        if extra <= included:
            break
        included |= extra
    return [rows[pid] for pid in sorted(included) if pid in rows]


def fixture(path):
    # PH(49 pigeons,48 holes), exact syntactic generic CNF; no target encoding.
    pigeons, holes = 49, 48
    clauses = []
    variable = lambda p, h: p*holes+h+1
    for p in range(pigeons):
        clauses.append([variable(p, h) for h in range(holes)])
        for h in range(holes):
            for k in range(h+1, holes):
                clauses.append([-variable(p, h), -variable(p, k)])
    for h in range(holes):
        for p in range(pigeons):
            for q in range(p+1, pigeons):
                clauses.append([-variable(p, h), -variable(q, h)])
    need(len(clauses) == 111769, 'FIXTURE_COUNT')
    with path.open('x', encoding='ascii', newline='\n') as stream:
        stream.write(f'p cnf {pigeons*holes} {len(clauses)}\n')
        for clause in clauses:
            stream.write(' '.join(map(str, clause))+' 0\n')
    return dict(variables=pigeons*holes, clauses=len(clauses), sha256=sha(path), bytes=path.stat().st_size)


def descendant(out):
    need(sys.platform.startswith('linux') and os.geteuid() == 1000, 'LINUX_UID')
    # Ordinary offspring, no setsid or setpgid; inherited group is intentionally tested.
    child = subprocess.Popen(['/usr/bin/sleep', '30'])
    save(out/'descendant_ready.json', dict(schema='ORDINARY_SLEEP_OFFSPRING_V1', timestamp=stamp(),
         parent=process(os.getpid()), child=process(child.pid), new_session_requested=False))
    child.wait()


def worker(args):
    need(sys.platform.startswith('linux') and os.geteuid() == 1000, 'LINUX_UID')
    deadline = CommandDeadline(args.seconds, allocation_reason='Finite active-stop case; preprocessing and native child share this invocation')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = args.supervision_out.resolve()/'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    need(manifest['source_sha256'] == sha(ROOT/'acceleration/run_compute_command_v2.py')
         and manifest['automatic_retry'] is False and manifest['cwd'] == str(ROOT), 'SUPERVISOR_IDENTITY')
    guard = process(os.getpgrp())
    context = observation_context()
    check_context(context)
    need(os.getpgrp() != os.getpid() and guard is not None and guard['comm'] == 'timeout', 'LIVE_OUTER_GUARD')
    check_process(guard)
    need(guard['pid'] == guard['pgid'] == guard['session'] and guard['real_uid'] == guard['effective_uid'] == 1000, 'LIVE_OUTER_GUARD')
    need(SAT_SHA == sha(SAT) and CADICAL_SHA == sha(CADICAL) and MIXED_SHA == sha(MIXED), 'BINARY_SOURCE_PINS')
    if args.profile == 'sat':
        formula = out/'fixture.cnf'
        info = fixture(formula)
        checksums = out/'inputs.sha256'
        with checksums.open('x', encoding='ascii', newline='\n') as stream:
            for path in [formula, SAT, CADICAL]:
                stream.write(f'{sha(path)}  {path.relative_to(ROOT).as_posix()}\n')
        command = ['/usr/bin/bash', str(SAT), str(formula), str(out/'proof.drat'), str(checksums), '10']
        expected_comm, required_live_count = 'cadical', 2
    elif args.profile == 'descendant':
        info = dict(scope='ordinary parent plus sleep30 offspring; no scientific calculation')
        command = ['/usr/bin/prlimit', '--as=536870912:536870912', '--fsize=134217728:134217728', '--core=0:0',
                   '/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', '10s',
                   sys.executable, str(SELF), 'descendant', '--out', str(out)]
        expected_comm, required_live_count = 'sleep', 3
    else:
        info = dict(scope='cube12 generic engineering fixture; same foreground/prlimit binary launch shape; science wrapper not executed')
        command = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', '10s',
                   '/usr/bin/prlimit', '--as=2147483648:2147483648', '--fsize=1073741824:1073741824', '--core=0:0', str(MIXED),
                   '--out', str(out/'native'), '--fixture', 'cube12', '--seconds', '9', '--seed', '991003',
                   '--steps', '1099511627776', '--mix-steps', '0', '--schedule-steps', '1099511627776',
                   '--temperature-start', '0', '--temperature-end', '0', '--verify-every', '4096',
                   '--checkpoint-every', '1099511627776', '--checkpoint-seconds', '0.5', '--trace-prefix', '1', '--trace-stride', '0']
        expected_comm, required_live_count = 'hypergraph_tern', 2
    save(out/'launch.json', dict(schema='NATIVE_ACTIVE_STOP_CASE_V3', timestamp=stamp(), profile=args.profile,
         command=command, worker=process(os.getpid()), original_group=os.getpgrp(), fixture=info,
         original_guard=guard, observation_context=context,
         supervisor_manifest_sha256=sha(manifest_path), source_sha256=sha(SELF), seconds=args.seconds,
         tools_sha256={path: sha(path) for path in ['/usr/bin/timeout', '/usr/bin/prlimit', '/usr/bin/bash']},
         scientific_launched=False, target_input_read=False, independent_approval=False))
    with (out/'native.stdout.log').open('xb') as stdout, (out/'native.stderr.log').open('xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        need(os.getpgid(child.pid) == os.getpgrp(), 'IMMEDIATE_CHILD_GROUP')
        first_live = None
        ready_saved = False
        with (out/'observations.jsonl').open('x', encoding='utf8', newline='\n') as stream:
            while True:
                rows = snapshot()
                observed = descendants(rows, child.pid)
                live = [row for row in observed if row['state'] != 'Z']
                record = dict(timestamp=stamp(), elapsed_seconds=deadline.status()['elapsed_seconds'],
                              observation_context=context, original_guard=guard,
                              worker=process(os.getpid()), children=observed, observed_child_exit_code=child.poll())
                stream.write(json.dumps(record)+'\n')
                stream.flush()
                need(all(row['pgid'] == os.getpgrp() and row['effective_uid'] == 1000 for row in live), 'DESCENDANT_GROUP_UID')
                present = any(row['comm'].startswith(expected_comm) for row in live)
                if present and len(live) >= required_live_count:
                    first_live = record['elapsed_seconds'] if first_live is None else first_live
                    if not ready_saved and record['elapsed_seconds']-first_live >= 1:
                        save(out/'live_ready.json', dict(schema='NATIVE_ACTIVE_STOP_LIVE_READY_V3',
                             timestamp=stamp(), profile=args.profile, first_live_elapsed=first_live,
                             original_guard=guard, observation_context=context,
                             last_live_elapsed=record['elapsed_seconds'], original_group=os.getpgrp(),
                             live_children=live, observed_euid=os.geteuid(), independent_approval=False))
                        ready_saved = True
                need(child.poll() is None, 'NATIVE_FINISHED_BEFORE_SUPERVISOR_STOP')
                need(not deadline.status()['stop_required'], 'WORKER_FINISHED_BEFORE_SUPERVISOR_STOP')
                time.sleep(0.1)


def observe(args):
    # Producer metadata only; separate ROOT/checker must authenticate and approve.
    need(sys.platform.startswith('linux'), 'LINUX_OBSERVATION')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cases = args.case_root.resolve()
    records = [json.loads(line) for line in (cases/'observations.jsonl').read_text().splitlines()]
    need(records and (cases/'live_ready.json').is_file(), 'ACTUAL_READY_OBSERVATIONS')
    ready = json.loads((cases/'live_ready.json').read_bytes())
    launch_path = cases/'launch.json'
    launch = json.loads(launch_path.read_bytes())
    context, guard, known = saved_identity(launch, ready, records)
    current_context = observation_context()
    rows, unreadable = [], []
    for directory in Path('/proc').glob('[0-9]*'):
        row = process(int(directory.name))
        if row is not None:
            rows.append(row)
        elif directory.exists():
            unreadable.append(int(directory.name))
    closing_context = observation_context()
    save(out/'raw_snapshot.json', dict(schema='NATIVE_ACTIVE_STOP_RAW_SNAPSHOT_V1', timestamp=stamp(),
         observer=process(os.getpid()), saved_context=context, current_context=current_context,
         closing_context=closing_context, original_guard=guard, known_identities=known,
         current_rows=rows, unreadable_pids=unreadable, independent_approval=False))
    try:
        result = assessment(context, current_context, guard, known, rows, unreadable)
        if current_context != closing_context:
            result.update(group_generation='UNKNOWN_CONTEXT_CHANGED_DURING_SNAPSHOT',
                          veto_stage='CONTEXT_CHANGED_DURING_SNAPSHOT_UNKNOWN',
                          no_selected_live_observed=None, no_original_generation_group_live_observed=None)
        save(out/'observation.json', dict(schema='NATIVE_ACTIVE_STOP_AFTER_OBSERVATION_V3', timestamp=stamp(),
             observer=process(os.getpid()), case_root=str(cases), observed_identities=len(known),
             saved_context=context, current_context=current_context, closing_context=closing_context,
             original_guard=guard, assessment=result, raw_snapshot_sha256=sha(out/'raw_snapshot.json'),
             inputs_sha256={str(path.relative_to(ROOT)): sha(path) for path in [launch_path, cases/'observations.jsonl', cases/'live_ready.json']},
             independent_approval=False, limitation='Finite exact observed PID/starttime/group population; no universal descendant or global absence claim'))
        need(result['veto_stage'] is None, result['veto_stage'])
    except Exception as error:
        save(out/'veto.json', dict(schema='NATIVE_ACTIVE_STOP_POST_VETO_V1', timestamp=stamp(),
             error_type=type(error).__name__, stage=str(error), raw_snapshot_sha256=sha(out/'raw_snapshot.json'),
             independent_approval=False, further_launch_authorized=False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['worker', 'descendant', 'observe'])
    parser.add_argument('--profile', choices=['sat', 'descendant', 'mixed'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--supervision-out', type=Path)
    parser.add_argument('--case-root', type=Path)
    parser.add_argument('--seconds', type=float)
    args = parser.parse_args()
    if args.mode == 'descendant':
        descendant(args.out.resolve())
    elif args.mode == 'observe':
        need(args.case_root is not None, 'CASE_ROOT_REQUIRED')
        observe(args)
    else:
        need(args.profile is not None and args.supervision_out is not None and args.seconds is not None, 'WORKER_ARGS')
        worker(args)


if __name__ == '__main__':
    main()
