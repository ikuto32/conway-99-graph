"""Read-only closure and sanitized Windows observation for one frozen guide."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'acceleration/results/20261003_incidence_four_low_counts_guide_plan04/plan.json'
PLAN_SHA = '934277e3fd742762aa2a9bd8c2d346dd72bed53e6f3f8330ecedeabaf86d0a7b'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--weight-domain', choices=['even13', 'divisible4_seven'], required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    deadline = CommandDeadline(a.seconds, allocation_reason='85 small static identity checks and read-only CIM metadata; no scientific worker')
    out = a.out.resolve()
    if not out.is_relative_to(ROOT) or out.exists() or sha(ROOT / PLAN) != PLAN_SHA:
        raise ValueError('FRESH_OUTPUT_EXACT_PLAN')
    out.mkdir(parents=True)
    plan = json.loads((ROOT / PLAN).read_bytes())
    checked = {}
    for path, expected in plan['inputs_sha256'].items():
        if sha(ROOT / path) != expected or deadline.status()['stop_required']:
            raise ValueError('PIN_OR_METADATA_DEADLINE:' + path)
        checked[path] = expected
    command = next(c for c in plan['guides'] if c['weight_domain'] == a.weight_domain)
    if (ROOT / command['output']).exists() or (ROOT / command['supervision']).exists():
        raise ValueError('GUIDE_ALREADY_ATTEMPTED')
    powershell = r'''
$known=@('admit_20261003_four_counts_guides_v1.py','audit_20261003_wave39_availability_v2.py','audit_20261003_root_focused_saved_objects_v4.py','run_compute_command.py')
$os=Get-CimInstance Win32_OperatingSystem
$items=@()
foreach($p in (Get-CimInstance Win32_Process|Where-Object{$_.Name -in @('python.exe','pythonw.exe','uv.exe')})){
 $labels=@($known|Where-Object{$p.CommandLine -and $p.CommandLine.Contains($_)})
 $items += [pscustomobject]@{pid=[int]$p.ProcessId;parent_pid=[int]$p.ParentProcessId;name=$p.Name;working_set_bytes=[uint64]$p.WorkingSetSize;classification=$(if($labels.Count){'RECOGNIZED_PUBLIC_LABEL'}else{'UNKNOWN_SCOPE'});public_labels=$labels;private_arguments_emitted=$false}
}
[pscustomobject]@{timestamp=[DateTimeOffset]::UtcNow.ToString('o');free_physical_bytes=[uint64]$os.FreePhysicalMemory*1024;total_visible_bytes=[uint64]$os.TotalVisibleMemorySize*1024;python_uv_processes=$items;scope='Windows python/uv only; Linux/other executable process states not inspected'}|ConvertTo-Json -Depth 6 -Compress
'''
    observation = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-NonInteractive', '-Command', powershell], cwd=ROOT, text=True, timeout=12))
    unknown = [r for r in observation['python_uv_processes'] if r['classification'] == 'UNKNOWN_SCOPE']
    metadata_receipt = 'acceleration/results/20261003_wave39_availability_supervision01/summary.json'
    receipt = json.loads((ROOT / metadata_receipt).read_bytes())
    # Native availability is metadata, not a scientific-worker claim.
    record = dict(schema='FOUR_COUNTS_GUIDE_READONLY_ADMISSION_V1', timestamp=datetime.now(timezone.utc).isoformat(), reporter='/root/structural',
                  plan=PLAN, plan_sha256=PLAN_SHA, weight_domain=a.weight_domain, frozen_worker_argv=command['worker_argv'], frozen_supervisor_argv=command['supervisor_argv'],
                  input_sha256=checked, checked_hashes=len(checked), observer_source_sha256=sha(Path(__file__)), observation=observation,
                  unknown_python_uv_processes=len(unknown), recognized_processes=len(observation['python_uv_processes'])-len(unknown),
                  readonly_native_availability_receipt=dict(path=metadata_receipt, sha256=sha(ROOT / metadata_receipt), exit_code=receipt['command_exit_code'], reaped=receipt['cleanup']['reaped'], job_empty=receipt['cleanup']['job_active_zero_observed']),
                  authority='ROOT explicitly authorized exactly ONE invocation per domain after plan04 and gate15a870 review; this observer does not add authority.',
                  status='PINNED_NO_UNKNOWN_WINDOWS_PYTHON_UV' if not unknown else 'PAUSE_UNKNOWN_PROCESS_SCOPE',
                  limitations=['Observation is finite/current Windows Python/uv metadata, not a general or cross-host worker guarantee.', 'No guide launched by this command, no mathematical approval, no ledger/index mutation.'], deadline=deadline.status())
    with (out / 'admission.json').open('x', encoding='utf8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=record['status'], admission_sha256=sha(out / 'admission.json'), free_physical_bytes=observation['free_physical_bytes'], unknown=len(unknown), guides_launched=0)))
    if unknown:
        raise ValueError('UNKNOWN_PYTHON_UV_SCOPE')


if __name__ == '__main__':
    main()
