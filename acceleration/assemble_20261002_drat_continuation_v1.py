"""Preserve a new byte-authenticated proof chain; no proof correctness claim.

Complete independent DRAT replay must use the original CNF. Originals and
suffix remain unchanged. Run within the supported Linux command supervisor.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

import native_20261002_exact_eight_budget_v1 as shared
from command_deadline import CommandDeadline

ROOT = shared.ROOT


def supervision(args, pins, deadline):
    shared.need(sys.platform.startswith('linux'), 'proof chain assembly runs inside supervised Linux')
    path = args.supervision_out.resolve()/'manifest.json'
    data = shared.read(path)
    shared.pin(ROOT/'acceleration/run_compute_command.py', data['source_sha256'], pins, deadline)
    shared.need(data['seconds'] <= 21600 and data['seconds'] >= args.seconds+10 and
                data['automatic_retry'] is False and data['cumulative_across_commands'] is False,
                'per-command outer allowance includes hashes/copying')
    leader = [part.decode() for part in (Path('/proc')/str(os.getpgid(0))/'cmdline').read_bytes().split(b'\0') if part]
    shared.need(leader and Path(leader[0]).name == 'timeout' and '--signal=KILL' in leader and
                (str(Path(__file__).resolve()) in data['command'] or shared.key(Path(__file__)) in data['command']),
                'live supported enclosing native group guard and exact source')
    return dict(manifest_path=shared.key(path), manifest_sha256=shared.sha(path, deadline),
                invocation_id=data['invocation_id'], outer_seconds=data['seconds'], guard_argv=leader)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ['out', 'supervision-out', 'preparation-summary', 'suffix']:
        parser.add_argument('--'+field, type=Path, required=True)
    for field in ['preparation-summary-sha256', 'suffix-sha256', 'allocation-reason']:
        parser.add_argument('--'+field, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason=args.allocation_reason)
    out = args.out.resolve()
    shared.need(out.is_relative_to(ROOT), 'new existing-repository evidence directory')
    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    try:
        supervisor = supervision(args, pins, deadline)
        for path in [Path(__file__), *shared.CODE]:
            pins[shared.key(path)] = shared.sha(path, deadline)
        shared.pin(args.preparation_summary, args.preparation_summary_sha256, pins, deadline)
        shared.pin(args.suffix, args.suffix_sha256, pins, deadline)
        prepared = shared.read(args.preparation_summary)
        shared.need(prepared['schema'] == 'DRAT_RESTART_PREPARATION_OUTPUTS_V1' and
                    prepared['mode'] == 'prepare' and len(prepared['records']) == 1, 'actual preserved candidate prefix')
        plan = prepared['plan']
        original = shared.repository_path(plan['original_partial_proof']['path'])
        shared.pin(original, plan['original_partial_proof']['sha256'], pins, deadline)
        descriptors = {Path(row['path']).name: row for row in prepared['records'][0]['outputs']}
        prefix_descriptor = descriptors['retained_prefix.drat']
        prefix = shared.repository_path(prefix_descriptor['path'])
        metadata_path = shared.repository_path(descriptors['parser_summary.json']['path'])
        shared.pin(prefix, prefix_descriptor['sha256'], pins, deadline)
        shared.pin(metadata_path, descriptors['parser_summary.json']['sha256'], pins, deadline)
        metadata = shared.read(metadata_path)
        retained = metadata['retained_original_bytes']
        dropped = metadata['trailing_dropped_bytes']
        appended = bool(metadata['appended_boundary_newline'])
        shared.need(retained+dropped == original.stat().st_size == metadata['original_proof_bytes'] and
                    prefix.stat().st_size == retained+int(appended), 'exact kept/dropped/boundary accounting')
        with original.open('rb') as raw, prefix.open('rb') as saved:
            remaining = retained
            while remaining:
                shared.check_time(deadline, 20)
                amount = min(1048576, remaining)
                shared.need(raw.read(amount) == saved.read(amount), 'entire retained prefix equals original bytes')
                remaining -= amount
            shared.need(saved.read() == (b'\n' if appended else b''), 'only declared boundary LF may be added')
        if prefix.stat().st_size:
            with prefix.open('rb') as stream:
                stream.seek(-1, os.SEEK_END)
                shared.need(stream.read(1) == b'\n', 'prefix record boundary must be closed before suffix')
        destination, identity = out/'combined_candidate.drat', hashlib.sha256()
        rows = []
        with destination.open('xb') as target:
            for source in [prefix, args.suffix.resolve()]:
                size, component = 0, hashlib.sha256()
                with source.open('rb') as stream:
                    for block in iter(lambda: stream.read(1048576), b''):
                        shared.check_time(deadline, 15)
                        target.write(block)
                        identity.update(block)
                        component.update(block)
                        size += len(block)
                shared.need(component.hexdigest() == pins[shared.key(source)], 'component unchanged during assembly')
                rows.append(dict(path=shared.key(source), sha256=component.hexdigest(), bytes=size))
        shared.need(destination.stat().st_size == sum(row['bytes'] for row in rows), 'literal concatenation length')
        summary = dict(schema='CANDIDATE_DRAT_CONTINUATION_CHAIN_V1', timestamp=shared.stamp(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=pins, supervision=supervisor,
            original_cnf=plan['original_cnf'], original_partial_proof=plan['original_partial_proof'],
            retained_original_bytes=retained, trailing_dropped_bytes=dropped, appended_boundary_newline=appended,
            components=rows, combined=dict(path=shared.key(destination), sha256=identity.hexdigest(),
                bytes=destination.stat().st_size, availability='LOCAL_ONLY'),
            status='CANDIDATE_RAW_PROOF_CHAIN_PENDING_COMPLETE_ORIGINAL_CNF_REPLAY',
            proof_completeness='UNKNOWN; assembly does not interpret or approve proof steps',
            rat_rup_checked=False, independent_approval=False, mathematical_exclusions_asserted=0,
            target_resolution=False, automatic_resume=False,
            elapsed_seconds=deadline.status()['elapsed_seconds'],
            unmet_requirements=['Complete independent replay of combined bytes against original CNF, encoding/coverage audit for any target claim.'])
        shared.save(out/'summary.json', summary)
        print(json.dumps(dict(status=summary['status'], summary_sha256=shared.sha(out/'summary.json', deadline))), flush=True)
    except BaseException as error:
        shared.save(out/'failure.json', dict(timestamp=shared.stamp(), error=repr(error),
            independent_approval=False, target_resolution=False,
            unfinished_description='not completed within the allocated budget', automatic_resume=False))
        raise


if __name__ == '__main__':
    main()
