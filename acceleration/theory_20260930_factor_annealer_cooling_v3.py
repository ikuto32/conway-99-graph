"""Bounded cooling resumes of frozen audited states; no self-approval."""
from datetime import datetime, timezone
from hashlib import file_digest
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v3.py'
EXE = ROOT/'acceleration/build/factor_permutation_anneal_20260930_v2.exe'
SPEC = Path(__file__).with_name('theory_20260930_factor_annealer_cooling_v3_spec.md')
GATE = None
GATE_SHA = None
STATE_GATE = ROOT/'acceleration/results/20260930_independent_review/factor_annealer_pilot/summary.json'
STATE_GATE_SHA = '97858230f5e777d601554e51184f0cb3b57ce6d39ed022a3850005b49c27fdd5'
OLD = ROOT/'acceleration/results/20260930_factor_annealer_pilot'
STARTS = {
    'shift6': (OLD/'shift6_T1/checkpoint_00007.json', '9ed5a9ddd01ec5bcb7d9ad1449db23ae32c04b6aacaca76a1df02da90b45015e', 20260930),
    'six_prism': (OLD/'six_prism_T1/checkpoint_00007.json', '0f1bcbd56baa32ccf078af4ce445db9e9fcb4487074ebb8316733699cb83ed5d', 20260931),
}


def need(ok, message):
    if not ok: raise ValueError(message)


def digest(path):
    with Path(path).open('rb') as stream: return file_digest(stream, 'sha256').hexdigest()


def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def read(path): return json.loads(Path(path).read_bytes())


def timestamp(): return datetime.now(timezone.utc).isoformat()


def main():
    global GATE, GATE_SHA
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--gate', type=Path, required=True); ap.add_argument('--gate-sha256', required=True)
    args = ap.parse_args(); GATE = args.gate.resolve(); GATE_SHA = args.gate_sha256
    need(digest(GATE) == GATE_SHA and digest(STATE_GATE) == STATE_GATE_SHA, 'exact independent gates')
    gate, state_gate = read(GATE), read(STATE_GATE)
    need(gate['status'] == 'INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS', 'calibration gate status')
    need(state_gate['status'] == 'INDEPENDENT_FACTOR_ANNEALER_PILOT_SAVED_STATES_PASS', 'old saved-state independent status')
    sources = [ENGINE, EXE, ROOT/'acceleration/factor_permutation_anneal_20260930_v2.cu',
        ROOT/'acceleration/build_factor_permutation_anneal_20260930_v2.ps1',
        ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v3_spec.md']
    for path in sources: need(gate['inputs_sha256'][key(path)] == digest(path), 'unchanged calibrated source/binary '+key(path))
    for path, expected, seed in STARTS.values():
        need(digest(path) == expected and state_gate['inputs_sha256'][key(path)] == expected, 'audited exact initial checkpoint')
        need(len(read(path)['chains']) == 16, 'exact sixteen resumed chains')
    need(shutil.disk_usage(ROOT).free > 10*1024**3, 'host free-space budget')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    cases = [dict(core=core, temperature=t, label=core+'_T'+str(t).replace('.', '_'),
        seed=STARTS[core][2], chains=16, chunks=16, steps=1024, seconds=120,
        supervisor_seconds=120, maximum_new_proposals=262144) for core in STARTS for t in (0.25, 0)]
    failed = ROOT/'acceleration/results/20260930_factor_annealer_cooling/summary.json'
    diagnosis = ROOT/'acceleration/results/20260930_factor_annealer_resume_diagnosis/summary.json'
    need(digest(failed) == '0a82e3c77809f7001afc37a701d2a479fe015fe365ebcbf8ec143f53342fb13a', 'preserved failed v2 attempt')
    need(digest(diagnosis) == '69e38afd2753d6e0bd7f1c1f4ebd3a4f3994b751f468c15fd5b588741028c89e', 'preserved exact diagnosis')
    inputs = [Path(__file__), SPEC, *sources, GATE, STATE_GATE, failed, diagnosis, ROOT/'uv.lock', ROOT/'pyproject.toml', *[x[0] for x in STARTS.values()]]
    bindings = {key(p): digest(p) for p in inputs}
    save(out/'manifest.json', dict(timestamp=timestamp(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        uv_version=subprocess.check_output(['uv', '--version'], text=True).strip(), inputs_sha256=bindings,
        objective='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1', planned_cases=cases,
        maximum_new_proposals=1048576, distinct_resumed_chains=32, new_chain_initializations=0,
        old_permutations_best_rng_and_counters_preserved=True,
        numerical_acceptance='Floating-point exp acceptance guides search; exact integer score/deltas.',
        gpu=subprocess.check_output(['nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.free', '--format=csv'], text=True),
        cpu=platform.processor(), seed_semantics='CLI seeds recorded but resumed state entirely replaces initialization.',
        target_resolution=False, independent_approval=False, no_engine_or_old_artifact_changes=True,
        protocol_deviation='Explicit new v3 retry after v2 failed before any native proposal on JSON list/tuple comparison. Original failed run remains unchanged; same initial T1 checkpoints and research budget.'))
    resumes = {core: value[0] for core, value in STARTS.items()}; blocked = set(); zero_reported = False; records = []
    for case in cases:
        core, label = case['core'], case['label']
        if zero_reported or core in blocked:
            record = dict(case=case, stage='SKIPPED', reason='E0 awaits independent review' if zero_reported else 'Previous cooling stage failed or hit its resource limit')
            save(out/(label+'.receipt.json'), record); records.append(record); continue
        resume = resumes[core]; before = read(resume); initial_proposals = sum(s['proposals'] for s in before['chains'])
        initial_best = min(s['best_score'] for s in before['chains']); directory = out/label
        command = [sys.executable, str(ENGINE), 'run', '--out', str(directory), '--core', core,
            '--independent-gate', str(GATE), '--independent-gate-sha256', GATE_SHA, '--resume', str(resume)]
        for field in ('seed', 'temperature', 'chains', 'chunks', 'steps', 'seconds'): command += ['--'+field, str(case[field])]
        save(out/(label+'.manifest.json'), dict(timestamp=timestamp(), case=case, command=command,
            resume_path=key(resume), resume_sha256=digest(resume), initial_proposal_total=initial_proposals,
            initial_best_reported_score=initial_best, preserved_chain_states=16, manifest_sha256=digest(out/'manifest.json')))
        print(json.dumps(dict(state='COOLING_STAGE_LAUNCHING', case=label, resume=key(resume), initial_best=initial_best)), flush=True)
        start = time.monotonic(); expired = False; cleanup = None
        with (out/(label+'.stdout.log')).open('xb') as stdout, (out/(label+'.stderr.log')).open('xb') as stderr:
            process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
            save(out/(label+'.launch.json'), dict(timestamp=timestamp(), pid=process.pid, command=command, owned_process_tree=True))
            try: process.wait(timeout=120)
            except subprocess.TimeoutExpired:
                expired = True
                kill_command = ['taskkill', '/PID', str(process.pid), '/T', '/F']
                killed = subprocess.run(kill_command, capture_output=True, text=True, timeout=10)
                cleanup = dict(command=kill_command, exit_code=killed.returncode, stdout=killed.stdout, stderr=killed.stderr)
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: cleanup['process_exit_observed'] = False
        record = dict(case=case, command=command, pid=process.pid, actual_exit_code=process.poll(),
            supervisor_expired=expired, cleanup=cleanup, wall_seconds=time.monotonic()-start,
            stage='COMPLETED' if not expired and process.returncode == 0 else 'STOPPED_RESOURCE_LIMIT' if expired else 'ERROR',
            resume_path=key(resume), resume_sha256=digest(resume), initial_proposal_total=initial_proposals,
            initial_best_reported_score=initial_best, completed_chunks=0, observed_new_proposals=0)
        checkpoints = sorted(directory.glob('checkpoint_*.json')) if directory.exists() else []
        if checkpoints:
            last = checkpoints[-1]; after = read(last); best = min(s['best_score'] for s in after['chains'])
            need(len(after['chains']) == 16, 'chain count preserved')
            increment = sum(s['proposals'] for s in after['chains'])-initial_proposals
            need(0 <= increment <= 262144 and increment == len(checkpoints)*16*1024, 'exact saved proposal increments')
            need(best <= initial_best, 'historical best preserved across resume')
            record.update(completed_chunks=len(checkpoints), observed_new_proposals=increment,
                last_checkpoint=key(last), last_checkpoint_sha256=digest(last), final_best_reported_score=best)
            zero_reported = best == 0
            resumes[core] = last
        if record['stage'] == 'COMPLETED':
            summary = read(directory/'summary.json')
            need(summary['completed_chunks'] == record['completed_chunks'], 'engine saved-chunk agreement')
            record.update(summary=key(directory/'summary.json'), summary_sha256=digest(directory/'summary.json'))
        else:
            blocked.add(core)
            record['unsaved_inflight_proposals'] = None
            record['unsaved_inflight_proposals_null_reason'] = 'An abnormal or terminated native chunk may not have saved its exact final counter.'
        save(out/(label+'.receipt.json'), record); records.append(record)
        print(json.dumps(dict(state=record['stage'], case=label, completed_chunks=record['completed_chunks'],
            observed_new_proposals=record['observed_new_proposals'], best=record.get('final_best_reported_score'))), flush=True)
    need(all(digest(ROOT/p) == h for p, h in bindings.items()), 'all frozen initial inputs remain unchanged')
    summary = dict(status='CANDIDATE_FACTOR_ANNEALER_COOLING_COMPLETED', timestamp=timestamp(),
        manifest_sha256=digest(out/'manifest.json'), cases=records,
        attempted_stages=sum(r['stage'] != 'SKIPPED' for r in records), completed_stages=sum(r['stage'] == 'COMPLETED' for r in records),
        errors=sum(r['stage'] == 'ERROR' for r in records), resource_stops=sum(r['stage'] == 'STOPPED_RESOURCE_LIMIT' for r in records),
        skipped_stages=sum(r['stage'] == 'SKIPPED' for r in records),
        completed_new_proposals=sum(r.get('observed_new_proposals', 0) for r in records), maximum_new_proposals=1048576,
        distinct_resumed_chains=32, new_chain_initializations=0, zero_reported=zero_reported,
        independent_object_audit_required=True, independent_approval=False, target_resolution=False,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        limitations=['Scores are producer-reported until independent exact raw recomputation.', 'Positive scores are not bounds or exclusions.',
            'The same chains continue across temperatures; stage-chain counts overlap.', 'No residual adjacency search was performed.'])
    save(out/'summary.json', summary)
    print(json.dumps(dict(summary=key(out/'summary.json'), sha256=digest(out/'summary.json'), zero_reported=zero_reported)), flush=True)


if __name__ == '__main__': main()
