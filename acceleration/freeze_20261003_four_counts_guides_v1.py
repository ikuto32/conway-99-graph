"""Freeze two unexecuted guide commands, then observe sanitized local resources."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/theory_20261003_incidence_four_low_counts_lp_v2.py'
SPEC = 'acceleration/theory_20261003_incidence_four_low_counts_lp_v2_spec.md'
SOURCE_SHA = '6f08f7c91a947fd866fdd9aec7c2a5df700b29f7fcdf7c59ef539f35b9ecb002'
SPEC_SHA = '2e3c43365138083555cb440f39c85eaccd162e71fbfb33bc958d2acabf96cd2a'
GATE = 'acceleration/results/20261003_independent_review/four_counts_lp_calibration01/summary.json'
GATE_SHA = '15a870349f39da25ff53da630ab2850076aad7fca6efebeafdae13c0f08a888e'
LOW = 'acceleration/results/20261003_independent_review/incidence_low_weights01/summary.json'
LOW_SHA = '626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd'
N5 = 'acceleration/results/20261003_independent_review/weight5_full02/summary.json'
N5_SHA = 'dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2'
DOMAINS = {'even13': list(range(36, 61, 2)), 'divisible4_seven': list(range(36, 61, 4))}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Small read-only hash closure and exact command metadata; no solver or registry edit')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_WORKSPACE_OUTPUT')
    out.mkdir(parents=True)
    pins = {SOURCE: SOURCE_SHA, SPEC: SPEC_SHA, GATE: GATE_SHA, LOW: LOW_SHA, N5: N5_SHA}
    gate = json.loads((ROOT / GATE).read_bytes())
    need(gate['status'] == 'INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_LP_CHECKER_V2_CALIBRATION_PASS' and gate['verifier'] == '/root' and gate['full_producer_output_inspected'] is False and gate['approved_weight_domains'] == DOMAINS, 'EXACT_NEW_CHECKER_GATE')
    for path, expected in gate['inputs_sha256'].items():
        need(path not in pins or pins[path] == expected, 'CONSISTENT_CLOSURE_PIN')
        pins[path] = expected
    for relative in [
        'acceleration/results/20261003_incidence_four_low_counts_plan01/plan.json',
        'acceleration/results/20261003_incidence_four_low_counts_plan02/failure.json',
        'acceleration/results/20261003_incidence_four_low_counts_plan03/plan.json',
        'acceleration/results/20261003_incidence_four_low_counts_plan03/calibration_count_deviation.json',
        'acceleration/results/20261003_incidence_four_counts_even13_controls01/summary.json',
        'acceleration/results/20261003_incidence_four_counts_even13_controls01/controls.json',
        'acceleration/results/20261003_incidence_four_counts_div4_controls01/summary.json',
        'acceleration/results/20261003_incidence_four_counts_div4_controls01/controls.json',
        'acceleration/results/20261003_wave39_availability_calibration_supervision01/summary.json',
        Path(__file__).relative_to(ROOT).as_posix(),
    ]:
        pins[relative] = digest(ROOT / relative)
    for variant in ['even13', 'div4']:
        folder = f'acceleration/results/20261003_incidence_four_counts_{variant}_controls_supervision01'
        for filename in ['summary.json', 'manifest.json', 'stdout.log', 'stderr.log']:
            relative = f'{folder}/{filename}'
            pins[relative] = digest(ROOT / relative)
        receipt = json.loads((ROOT / folder / 'summary.json').read_bytes())
        need(receipt['command_exit_code'] == 0 and receipt['cleanup']['reaped'] and receipt['cleanup']['job_active_zero_observed'], 'AUTHOR_CONTROL_TERMINAL')
    for relative, expected in pins.items():
        need(not Path(relative).is_absolute() and '..' not in Path(relative).parts and len(expected) == 64, 'LITERAL_CLOSURE_PATH')
        need(digest(ROOT / relative) == expected, 'PIN_CHANGED:' + relative)
        need(not deadline.status()['stop_required'], 'METADATA_DEADLINE')
    commands = []
    for domain, weights in DOMAINS.items():
        short = 'even13' if domain == 'even13' else 'div4'
        output = f'acceleration/results/20261003_incidence_four_counts_{short}_guide01'
        supervision = f'acceleration/results/20261003_incidence_four_counts_{short}_guide_supervision01'
        need(not (ROOT / output).exists() and not (ROOT / supervision).exists(), 'GUIDE_OUTPUT_ALREADY_EXISTS')
        worker = [
            (ROOT / 'build/research-venv/Scripts/python.exe').as_posix(),
            (ROOT / SOURCE).as_posix(), '--mode', 'guide', '--weight-domain', domain,
            '--seconds', '90', '--source-sha256', SOURCE_SHA, '--protocol-sha256', SPEC_SHA,
            '--low-weight-audit', (ROOT / LOW).as_posix(), '--low-weight-audit-sha256', LOW_SHA,
            '--weight5-audit', (ROOT / N5).as_posix(), '--weight5-audit-sha256', N5_SHA,
            '--checker-calibration', (ROOT / GATE).as_posix(), '--checker-calibration-sha256', GATE_SHA,
            '--out', (ROOT / output).as_posix(),
        ]
        need(len(worker) == 26 and all(type(word) is str for word in worker), 'EXACT_26_ARGUMENTS')
        supervisor = [
            'uv', 'run', '--locked', '--offline', '--cache-dir', '.uv-cache-20260917',
            'acceleration/run_compute_command.py', '--seconds', '120', '--shutdown-reserve-seconds', '10',
            '--allocation-reason', f'ONE {domain} conditional four-low-count 99-column tiny LP guide; prior comparable 7/13-row guides below1s support90worker/30native/30internal serialization reserve; no retry',
            '--success-criterion', f'Save all{99 * len(weights)} exact coefficient pairs, one floating guide and ALL THREE fixed rational lifts; complete99 nonnegative dual coordinates and every{len(weights)} inequality for any candidate bound, otherwise UNKNOWN with raw failures',
            '--verification-criterion', 'Producer cannot approve; ROOT new polynomial-product checking path f72133 and pre-output gate15a870 must reconstruct every exact raw coefficient/dual/inequality/bound and actual corruption controls; no generic-code/optimum/nonexistence claim',
            '--out', supervision, '--', *worker,
        ]
        commands.append(dict(weight_domain=domain, nonzero_weights=weights, worker_argv=worker, supervisor_argv=supervisor, output=output, supervision=supervision, authorization=None, authorization_reason='ROOT will review final plan and fresh sanitized observation; this metadata command launches no guide'))
    source_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, timeout=3).strip()
    uv_version = subprocess.check_output(['uv', '--version'], cwd=ROOT, text=True, timeout=3).strip()
    plan = dict(schema='CONCRETE_FOUR_LOW_COUNTS_GUIDE_COMMANDS_V1', timestamp=datetime.now(timezone.utc).isoformat(), source_commit=source_commit,
                source_commit_limitation='Working producer/checker/metadata sources separately hashed; not asserted committed in source_commit',
                workspace=ROOT.as_posix(), environment={'UV_PROJECT_ENVIRONMENT': 'build/research-venv'}, python=sys.version, uv=uv_version,
                status='FROZEN_UNEXECUTED_PENDING_ROOT_ADMISSION', guides=commands, lower_word_counts={'3': 231, '4': 2079, '5': 12474, '6': 24486},
                exact_lift_denominator_limits=[1000, 1000000, 1000000000], selection='Attempt all three fixed lifts; preserve every positive and failed lift; choose smallest exact certified upper bound, no optimum claim',
                per_invocation=dict(outer_seconds=120, worker_seconds=90, native_solver_seconds=30, internal_serialization_reserve_seconds=30, outer_shutdown_guard_seconds=10, solver_calls=1, retries=0, solver_seed=0, threads=1),
                numerical_thresholds=dict(primal_dual_feasibility=1e-10, numerical_small_matrix=1e-12, float_only_truncate_absolute_less_than=1e-11, exact_coefficients_truncated=False),
                mathematical_scope='Conditional target triangle-kernel size bounds using independently derived necessary weight domains and image counts; no generic-code theorem, nonzero-kernel premise, rank upper bound, optimum or target resolution.',
                independent_checker_gate=GATE, independent_checker_gate_sha256=GATE_SHA, inputs_sha256=dict(sorted(pins.items())),
                author_control_deviation='Declared author140/actual139 literal character cells preserved in ed8f deviation; independent ROOT included n=0 boundary for140. Neither author run is promoted to140.',
                guides_started=0, ledger_mutations=0, index_mutations=0, target_resolution='NONE')
    save(out / 'plan.json', plan)
    # Inspect after the plan exists. Classify only fixed public names; never emit arbitrary arguments.
    powershell = r'''
$known = @('freeze_20261003_four_counts_guides_v1.py','audit_20261003_wave39_availability_v2.py','audit_20261003_root_focused_saved_objects_v4.py','run_compute_command.py')
$os = Get-CimInstance Win32_OperatingSystem
$items = @()
foreach ($p in (Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','pythonw.exe','uv.exe') })) {
  $labels = @($known | Where-Object { $p.CommandLine -and $p.CommandLine.Contains($_) })
  $items += [pscustomobject]@{pid=[int]$p.ProcessId;parent_pid=[int]$p.ParentProcessId;name=$p.Name;working_set_bytes=[uint64]$p.WorkingSetSize;classification=$(if($labels.Count){'RECOGNIZED_PUBLIC_LABEL'}else{'UNKNOWN_SCOPE'});public_labels=$labels;private_arguments_emitted=$false}
}
[pscustomobject]@{timestamp=[DateTimeOffset]::UtcNow.ToString('o');free_physical_bytes=[uint64]$os.FreePhysicalMemory*1024;total_visible_bytes=[uint64]$os.TotalVisibleMemorySize*1024;python_uv_processes=$items;scientific_running_inferred=$false;observation_scope='Windows python/uv by CIM; Linux and other executables not inspected; unknown scope remains explicit'} | ConvertTo-Json -Depth 6 -Compress
'''
    resource = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-NonInteractive', '-Command', powershell], cwd=ROOT, text=True, timeout=min(12, deadline.status()['remaining_seconds'] - 3)))
    resource['plan_sha256'] = digest(out / 'plan.json')
    resource['metadata_worker_author'] = '/root/structural'
    resource['reported_native_availability_receipt'] = 'acceleration/results/20261003_wave39_availability_calibration_supervision01/summary.json'
    resource['guide_authorization'] = None
    resource['guide_authorization_reason'] = 'Resource snapshot and final plan are for ROOT review, not admission.'
    save(out / 'resources.json', resource)
    save(out / 'summary.json', dict(status='GUIDE_PLAN_AND_READONLY_RESOURCES_SAVED_NO_GUIDES', timestamp=datetime.now(timezone.utc).isoformat(), plan_sha256=digest(out / 'plan.json'), resources_sha256=digest(out / 'resources.json'), complete_closure_hashes_checked=len(pins), guides_started=0, ledger_mutations=0, index_mutations=0, deadline=deadline.status()))
    print(json.dumps(dict(plan_sha256=digest(out / 'plan.json'), resources_sha256=digest(out / 'resources.json'), summary_sha256=digest(out / 'summary.json'), guides_started=0)))


if __name__ == '__main__':
    main()
