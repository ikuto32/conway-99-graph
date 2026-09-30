"""Frozen six-case construction pilot; no independent approval is performed here."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v2.py'
SPEC = Path(__file__).with_name('theory_20260930_factor_annealer_pilot_spec.md')
EXE = ROOT/'acceleration/build/factor_permutation_anneal_20260930_v2.exe'


def digest(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def rel(p):
    return p.resolve().relative_to(ROOT).as_posix()


def save(p, value):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', type=Path, required=True)
    ap.add_argument('--gate-sha256', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    gatepath = a.gate.resolve()
    assert digest(gatepath) == a.gate_sha256
    gate = json.loads(gatepath.read_bytes())
    assert gate['status'] == 'INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS'
    for p in [ENGINE, EXE, ROOT/'acceleration/factor_permutation_anneal_20260930_v2.cu',
              ROOT/'acceleration/build_factor_permutation_anneal_20260930_v2.ps1',
              ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v2_spec.md']:
        assert gate['inputs_sha256'][rel(p)] == digest(p), rel(p)
    assert shutil.disk_usage(ROOT).free > 10*1024**3
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cases = [dict(core=core, seed=seed, temperature=t, chains=16, chunks=8, steps=1024, seconds=120,
                  label=core+'_T'+str(t).replace('.', '_'))
             for core, seed in [('shift6', 20260930), ('six_prism', 20260931)] for t in (1, 3.25, 8)]
    inputs = [Path(__file__), SPEC, ENGINE, EXE, gatepath, ROOT/'uv.lock', ROOT/'pyproject.toml']
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
        inputs_sha256={rel(p):digest(p) for p in inputs}, cases=cases, planned_cases=6,
        maximum_proposals=786432, maximum_initialized_chains=96,
        gpu=subprocess.check_output(['nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.free', '--format=csv'], text=True),
        cpu=platform.processor(), objective='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1',
        numerical_acceptance='double exp heuristic; integer score and deltas', target_resolution=False)
    save(out/'manifest.json', manifest)
    records = []
    zero_reported = False
    for case in tqdm(cases, desc='Frozen annealer cases'):
        if zero_reported:
            records.append(dict(case=case, stage='SKIPPED', reason='Earlier E0 report awaiting independent object audit'))
            continue
        directory = out/case['label']
        command = [sys.executable, str(ENGINE), 'run', '--out', str(directory), '--core', case['core'],
                   '--independent-gate', str(gatepath), '--independent-gate-sha256', a.gate_sha256]
        for k in ['seed','temperature','chains','chunks','steps','seconds']:
            command += ['--'+k, str(case[k])]
        start = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=200)
        for label, content in [('stdout',result.stdout), ('stderr',result.stderr)]:
            with (out/(case['label']+'.'+label+'.log')).open('xb') as f:
                f.write(content)
        record = dict(case=case, command=command, exit_code=result.returncode, wall_seconds=time.monotonic()-start,
                      stage='COMPLETED' if result.returncode == 0 else 'ERROR', summary=None)
        if result.returncode == 0:
            summary = json.loads((directory/'summary.json').read_bytes())
            record.update(summary=rel(directory/'summary.json'), summary_sha256=digest(directory/'summary.json'),
                          completed_chunks=summary['completed_chunks'], reported_best_score=summary['best_score'])
            zero_reported = summary['best_score'] == 0
        save(out/(case['label']+'.receipt.json'), record)
        records.append(record)
        tqdm.write(f"{case['label']}: {record['stage']}, reported E={record.get('reported_best_score')}")
    save(out/'summary.json', dict(status='CANDIDATE_TWO_CORE_ANNEALER_PILOT_COMPLETED',
        timestamp=datetime.now(timezone.utc).isoformat(), manifest_sha256=digest(out/'manifest.json'),
        attempted_cases=sum(r['stage'] != 'SKIPPED' for r in records),
        completed_cases=sum(r['stage'] == 'COMPLETED' for r in records),
        error_cases=sum(r['stage'] == 'ERROR' for r in records), skipped_cases=sum(r['stage'] == 'SKIPPED' for r in records),
        cases=records, independent_object_audit_required=True, target_resolution=False,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.'))
    print(json.dumps(dict(summary=rel(out/'summary.json'), sha256=digest(out/'summary.json'))))


if __name__ == '__main__':
    main()
