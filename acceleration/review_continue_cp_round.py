"""No-process controls for the single-round continuation orchestrator."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

import continue_cp_round as driver

ROOT = Path(__file__).resolve().parents[1]
R = ROOT/'acceleration/results'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    checkpoint = R/'20260916_cp_cross_checkpoint.json'
    expected = '8f800f9c507107822a573a7a27253ea8c29d68ea4dbc178bf1bbb0e871ca9251'
    priors = [R/name/'summary.json' for name in ('20260916_cp_matching_search', '20260916_cp_matching_round2',
                                               '20260916_cp_matching_round3', '20260916_cp_cross_search')]
    source = ROOT/'acceleration/continue_cp_round.py'
    hashes = {driver.key(p): driver.digest(p) for p in [checkpoint, source, Path(__file__), *priors]}
    require(hashes[driver.key(checkpoint)] == expected, 'Control checkpoint changed')
    started, records, processes = time.perf_counter(), [], []
    common = ['continue_cp_round', '--previous-checkpoint', str(checkpoint), '--previous-sha256', expected]
    for path in priors:
        common.extend(['--previous-summary', str(path)])

    def forbidden(*_args, **_kwargs):
        processes.append('CALLED')
        raise AssertionError('No process may launch during preflight controls')

    def run(name, kind, overrides=(), positive=False, existing=False):
        out = args.out if existing else args.out/(name+'_must_not_exist')
        before = sorted(str(p.relative_to(args.out)) for p in args.out.rglob('*'))
        argv = [*common, '--kind', kind, '--out', str(out), *overrides]
        if positive:
            argv.append('--validate-only')
        captured = io.StringIO()
        try:
            with patch.object(sys, 'argv', argv), patch.object(driver.subprocess, 'run', side_effect=forbidden), redirect_stdout(captured):
                driver.main()
        except ValueError as exc:
            require(not positive, 'Positive control failed: '+str(exc))
            record = dict(name=name, kind=kind, expected='REJECT', observed='REJECT', reason=str(exc))
        else:
            require(positive, 'Invalid CLI accepted')
            result = json.loads(captured.getvalue())
            require(result['status'] == 'ONE_CP_ROUND_READ_ONLY_PREFLIGHT_PASS' and result['processes_launched'] == 0
                    and result['output_created'] is False, 'Invalid preflight result')
            manifest = result['manifest']
            require(len(manifest['previous_summaries']) == 4 and manifest['rounds'] == 1 and
                    manifest['marks_goal_complete'] is False and len(manifest['steps']) == (6 if kind == 'same' else 8),
                    'Wrong one-round command plan')
            require(manifest['previous_checkpoint_references_verified'] == 2578 and
                    manifest['initial_numeric_merit'] == json.loads(checkpoint.read_bytes())['current_best']['best_numeric_merit'],
                    'Wrong checkpoint derivation')
            names = [step['name'] for step in manifest['steps']]
            require(names[-4:] == ['search', 'search_audit', 'adoption', 'checkpoint'], 'Wrong audited pipeline ordering')
            search_command = manifest['steps'][-4]['command']
            require(search_command.count('--previous-summary') == 4 and '--gpu-source' in search_command
                    and '--gpu-audit' in search_command and '--extra-report' in manifest['steps'][-1]['command'],
                    'Lost priors/GPU binding/run manifest')
            record = dict(name=name, kind=kind, expected='PASS', observed='PASS',
                          previous_checkpoint_references_verified=manifest['previous_checkpoint_references_verified'],
                          all_preflight_files_verified=manifest['all_preflight_files_verified'],
                          initial_candidate=manifest['initial_candidate_path'], initial_phase1=manifest['initial_phase1_path'],
                          initial_numeric_merit=manifest['initial_numeric_merit'], previous_summary_count=4,
                          stages=names, frozen_tool_count=len(driver.FROZEN_SHA256))
        require(not processes and sorted(str(p.relative_to(args.out)) for p in args.out.rglob('*')) == before,
                'Preflight mutated output or launched a process')
        if not existing:
            require(not out.exists(), 'Invalid/validate-only output created')
        records.append(dict(**record, processes_launched=0, output_mutations=0))

    for kind in ('same', 'cross'):
        run('bad_sha_'+kind, kind, ['--previous-sha256', '0'*64])
        run('existing_out_'+kind, kind, existing=True)
        run('valid_plan_'+kind, kind, positive=True)
    require(all(driver.digest(ROOT/name) == expected_hash for name, expected_hash in hashes.items()), 'Bound source changed')
    report = dict(status='ONE_CP_ROUND_READ_ONLY_PREFLIGHT_CONTROLS_PASS', inputs_sha256=hashes,
                  positive_controls=2, negative_controls=4, records=records, processes_launched=0,
                  driver_output_mutations=0, actual_rounds_run=0, elapsed_seconds=time.perf_counter()-started,
                  scope='Both complete command plans are validated from the real cross checkpoint. Wrong SHA and existing-root paths are rejected before mutation. No GPU, native generator, auditor subprocess or LP ran.')
    driver.save(args.out/'report.json', report)
    print(json.dumps({k: report[k] for k in ('status', 'positive_controls', 'negative_controls', 'processes_launched', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
