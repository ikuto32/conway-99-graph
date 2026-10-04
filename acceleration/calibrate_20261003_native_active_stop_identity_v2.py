"""Synthetic same-author metadata controls only; no proc/native calls on import."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'acceleration/control_20261003_native_active_stop_v5.py'
# Filled by the frozen source hash below before the first execution.
SOURCE_SHA = 'f1912b882612aa954f339c98f84da648c6aa361b17d166ba43e22b245e840ff5'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, row):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(row, stream, indent=2, allow_nan=False)
        stream.write('\n')


def cases():
    context = dict(schema='LINUX_PROC_IDENTITY_CONTEXT_V1', boot_id='00000000-0000-0000-0000-000000000000',
                   pid_namespace='pid:[4026531836]', clock_ticks_per_second=100)
    guard = dict(pid=374, ppid=284, pgid=374, session=374, state='S', start_ticks=6040,
                 real_uid=1000, effective_uid=1000, comm='timeout')
    worker = dict(guard, pid=378, ppid=375, state='R', start_ticks=6057, comm='python3')
    native = dict(guard, pid=385, ppid=379, state='D', start_ticks=6109, comm='cadical')
    base = dict(saved_context=context, current_context=context, guard=guard,
                known=[[374, 6040], [378, 6057], [385, 6109]], rows=[], unreadable_pids=[])
    launch = dict(schema='NATIVE_ACTIVE_STOP_CASE_V3', observation_context=context, original_guard=guard, original_group=374)
    ready = dict(schema='NATIVE_ACTIVE_STOP_LIVE_READY_V3', observation_context=context, original_guard=guard,
                 original_group=374, observed_euid=1000, first_live_elapsed=0.3, last_live_elapsed=1.4,
                 live_children=[native])
    records = [dict(observation_context=context, original_guard=guard, worker=worker, children=[native])]
    saved = dict(launch=launch, ready=ready, records=records)
    result = []

    def add(label, stage=None, generation=None, changes=None, saved_changes=None):
        args = copy.deepcopy(saved if saved_changes is not None else base)
        if changes:
            changes(args)
        if saved_changes:
            saved_changes(args)
        result.append(dict(label=label, function='saved_identity' if saved_changes is not None else 'assessment',
                           args=args, expected_stage=stage, expected_generation=generation))

    add('empty_current', generation='NO_CURRENT_LIVE_GROUP_MEMBERS')
    add('original_zombies', generation='ORIGINAL_LEADER_IDENTITY_PRESENT',
        changes=lambda a: a.update(rows=[dict(guard, state='Z'), dict(native, state='Z')]))
    add('observer_numeric_group_reuse', generation='NUMERIC_GROUP_REUSED_NEW_LEADER',
        changes=lambda a: a.update(rows=[dict(guard, start_ticks=9399), dict(worker, start_ticks=9418)]))
    add('leader_pid_reused_other_group', generation='LEADER_PID_REUSED_NO_CURRENT_GROUP',
        changes=lambda a: a.update(rows=[dict(guard, start_ticks=9399, pgid=777, session=777)]))
    add('unrelated_live_group', generation='NO_CURRENT_LIVE_GROUP_MEMBERS',
        changes=lambda a: a.update(rows=[dict(native, pid=888, pgid=777, session=777)]))
    add('valid_saved_wire', saved_changes=lambda a: None)
    for field in ['pid', 'ppid', 'pgid', 'session', 'start_ticks', 'real_uid', 'effective_uid']:
        for label, value in [('bool', True), ('float', 1.0)]:
            add(f'guard_{field}_{label}', 'PROCESS_SCHEMA', changes=lambda a, key=field, v=value: a['guard'].update({key: v}))
    add('context_ticks_bool', 'CONTEXT_SCHEMA', changes=lambda a: a['current_context'].update(clock_ticks_per_second=True))
    add('context_ticks_float', 'CONTEXT_SCHEMA', changes=lambda a: a['current_context'].update(clock_ticks_per_second=100.0))
    add('context_bad_boot', 'CONTEXT_SCHEMA', changes=lambda a: a['current_context'].update(boot_id='missing'))
    add('context_bad_namespace', 'CONTEXT_SCHEMA', changes=lambda a: a['current_context'].update(pid_namespace=4026531836))
    add('guard_wrong_session', 'ORIGINAL_GUARD_IDENTITY', changes=lambda a: a['guard'].update(session=999))
    add('guard_wrong_uid', 'ORIGINAL_GUARD_IDENTITY', changes=lambda a: a['guard'].update(effective_uid=0))
    add('guard_wrong_comm', 'ORIGINAL_GUARD_IDENTITY', changes=lambda a: a['guard'].update(comm='bash'))
    add('duplicate_known', 'KNOWN_IDENTITY_SCHEMA', changes=lambda a: a['known'].append([374, 6040]))
    add('known_bool_pid', 'KNOWN_IDENTITY_SCHEMA', changes=lambda a: a['known'][0].__setitem__(0, True))
    add('known_float_ticks', 'KNOWN_IDENTITY_SCHEMA', changes=lambda a: a['known'][0].__setitem__(1, 6040.0))
    add('known_guard_missing', 'KNOWN_IDENTITY_SCHEMA', changes=lambda a: a['known'].pop(0))
    add('duplicate_snapshot_pid', 'CURRENT_SNAPSHOT_SCHEMA', changes=lambda a: a.update(rows=[guard, dict(guard)]))
    add('unreadable_proc_object', 'PROC_OBSERVATION_UNKNOWN', changes=lambda a: a.update(unreadable_pids=[999]))
    add('same_guard_identity_changed_group', 'ORIGINAL_GUARD_CURRENT_IDENTITY', changes=lambda a: a.update(rows=[dict(guard, pgid=999)]))
    for field, value in [('boot_id', '00000000-0000-0000-0000-000000000001'),
                         ('pid_namespace', 'pid:[4026531837]'), ('clock_ticks_per_second', 250)]:
        add(f'changed_{field}', 'CONTEXT_CHANGED_UNKNOWN',
            changes=lambda a, key=field, v=value: a.update(current_context=dict(a['current_context'], **{key: v})))
    add('original_guard_alive', 'LIVE_PROCESS_AFTER_STOP', changes=lambda a: a.update(rows=[guard]))
    add('original_native_alive', 'LIVE_PROCESS_AFTER_STOP', changes=lambda a: a.update(rows=[native]))
    add('known_native_escaped_group', 'LIVE_PROCESS_AFTER_STOP', changes=lambda a: a.update(rows=[dict(native, pgid=999, session=999)]))
    add('leader_absent_live_group_member', 'LIVE_PROCESS_AFTER_STOP', changes=lambda a: a.update(rows=[dict(native, pid=600, start_ticks=6200)]))
    add('zombie_guard_live_child', 'LIVE_PROCESS_AFTER_STOP', changes=lambda a: a.update(rows=[dict(guard, state='Z'), native]))
    add('reused_group_known_escaped_native', 'LIVE_PROCESS_AFTER_STOP', changes=lambda a: a.update(rows=[dict(guard, start_ticks=9399), dict(native, pgid=999, session=999)]))
    add('reused_leader_elsewhere_live_numeric_members', 'GROUP_GENERATION_UNKNOWN',
        changes=lambda a: a.update(rows=[dict(guard, start_ticks=9399, pgid=999, session=999), dict(native, pid=600, start_ticks=6200)]))
    add('saved_v1_without_context', 'V3_CONTEXT_REQUIRED', saved_changes=lambda a: a['launch'].update(schema='NATIVE_ACTIVE_STOP_CASE_V1'))
    add('saved_ready_uid_bool', 'READY_UID_GROUP', saved_changes=lambda a: a['ready'].update(observed_euid=True))
    add('saved_ready_group_bool', 'READY_UID_GROUP', saved_changes=lambda a: a['ready'].update(original_group=True))
    add('saved_launch_group_float', 'READY_UID_GROUP', saved_changes=lambda a: a['launch'].update(original_group=374.0))
    add('saved_guard_float_ticks', 'PROCESS_SCHEMA', saved_changes=lambda a: a['ready']['original_guard'].update(start_ticks=6040.0))
    add('saved_context_bool_ticks', 'CONTEXT_SCHEMA', saved_changes=lambda a: a['ready']['observation_context'].update(clock_ticks_per_second=True))
    add('saved_record_changed_context', 'SAVED_CONTEXT_IDENTITY',
        saved_changes=lambda a: a['records'][0].update(observation_context=dict(context, pid_namespace='pid:[4026531837]')))
    add('saved_unobserved_ready_native', 'READY_OBSERVED_IDENTITY', saved_changes=lambda a: a['ready'].update(live_children=[dict(native, pid=999)]))
    add('saved_short_ready_interval', 'READY_LIVE_INTERVAL', saved_changes=lambda a: a['ready'].update(last_live_elapsed=0.5))
    add('saved_bool_ready_interval', 'READY_LIVE_INTERVAL', saved_changes=lambda a: a['ready'].update(first_live_elapsed=False))
    # Exact original six-positive48-negative prefix is preserved above.
    unrelated = dict(pid=2, ppid=0, pgid=0, session=0, state='S', start_ticks=42,
                     real_uid=0, effective_uid=0, comm='init')
    add('current_unrelated_zero_group_and_session', generation='NO_CURRENT_LIVE_GROUP_MEMBERS',
        changes=lambda a: a.update(rows=[unrelated]))
    add('current_unrelated_zero_group', generation='NO_CURRENT_LIVE_GROUP_MEMBERS',
        changes=lambda a: a.update(rows=[dict(unrelated, session=777)]))
    add('current_unrelated_zero_session', generation='NO_CURRENT_LIVE_GROUP_MEMBERS',
        changes=lambda a: a.update(rows=[dict(unrelated, pgid=777)]))
    for field in ['pgid', 'session']:
        for label, value in [('bool_zero', False), ('float_zero', 0.0), ('negative', -1)]:
            add(f'current_{field}_{label}', 'PROCESS_SCHEMA',
                changes=lambda a, key=field, v=value: a.update(rows=[dict(unrelated, **{key: v})]))
        add(f'guard_{field}_zero', 'PROCESS_SCHEMA', changes=lambda a, key=field: a['guard'].update({key: 0}))
        add(f'saved_ready_native_{field}_zero', 'PROCESS_SCHEMA',
            saved_changes=lambda a, key=field: a['ready']['live_children'][0].update({key: 0}))
        add(f'original_guard_current_{field}_zero', 'ORIGINAL_GUARD_CURRENT_IDENTITY',
            changes=lambda a, key=field: a.update(rows=[dict(guard, **{key: 0})]))
    add('known_native_alive_zero_group_and_session', 'LIVE_PROCESS_AFTER_STOP',
        changes=lambda a: a.update(rows=[dict(native, pgid=0, session=0)]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Pure synthetic identity metadata calibration; no native or proc calls')
    if sha(SOURCE) != SOURCE_SHA:
        raise ValueError('SOURCE_PIN')
    spec = importlib.util.spec_from_file_location('active_stop_identity_v5', SOURCE)
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    fixtures = cases()
    save(out/'fixtures.json', fixtures)
    results = []
    for fixture in fixtures:
        if deadline.status()['stop_required']:
            raise ValueError('CALIBRATION_DEADLINE')
        actual_stage, actual_generation, returned = None, None, None
        try:
            returned = getattr(producer, fixture['function'])(**fixture['args'])
            if fixture['function'] == 'assessment':
                actual_stage, actual_generation = returned['veto_stage'], returned['group_generation']
            elif returned[2] != [[374, 6040], [378, 6057], [385, 6109]]:
                raise ValueError('SAVED_POSITIVE_IDENTITIES')
        except ValueError as error:
            actual_stage = str(error)
        if actual_stage != fixture['expected_stage'] or (fixture['expected_generation'] is not None
                                                       and actual_generation != fixture['expected_generation']):
            save(out/'failure.json', dict(fixture=fixture, actual_stage=actual_stage, actual_generation=actual_generation))
            raise ValueError('CALIBRATION_EXPECTED_STAGE')
        results.append(dict(label=fixture['label'], expected_stage=fixture['expected_stage'], actual_stage=actual_stage,
                            expected_generation=fixture['expected_generation'], actual_generation=actual_generation, returned=returned))
    positive = sum(row['expected_stage'] is None for row in fixtures)
    negative = len(fixtures)-positive
    if (positive, negative) != (9, 61):
        raise ValueError('CALIBRATION_POPULATION')
    save(out/'summary.json', dict(schema='NATIVE_ACTIVE_STOP_IDENTITY_SYNTHETIC_V2',
         status='AUTHOR_SYNTHETIC_METADATA_CONTROLS_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
         positive_cases=positive, precise_negative_cases=negative, results=results,
         preserved_original_positive_cases=6, preserved_original_precise_negative_cases=48,
         additional_positive_cases=3, additional_precise_negative_cases=13,
         inputs_sha256={str(SOURCE.relative_to(ROOT)): sha(SOURCE), str(Path(__file__).resolve().relative_to(ROOT)): sha(__file__)},
         fixture_sha256=sha(out/'fixtures.json'), elapsed_seconds=deadline.status()['elapsed_seconds'],
         proc_read=False, native_calls=0, scientific_launched=False, independent_approval=False,
         shared_author_note='Imports the exact producer pure identity helpers; ROOT must separately review all fixtures and results'))


if __name__ == '__main__':
    main()
