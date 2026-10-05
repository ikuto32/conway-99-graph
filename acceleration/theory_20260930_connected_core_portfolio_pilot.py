"""Bounded four-core construction pilot; all mathematical outputs are candidates."""
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
ENGINE = ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v4.py'
SPEC = Path(__file__).with_name('theory_20260930_connected_core_portfolio_pilot_spec.md')
EXE = ROOT/'acceleration/build/factor_permutation_anneal_20260930_v2.exe'
DOMAIN = ROOT/'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json'
DOMAIN_SHA = 'efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4'
PORTFOLIO = ROOT/'acceleration/results/20260930_connected_identity_cores'
OBJECTIVE = 'TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'

def need(ok, message):
    if not ok: raise ValueError(message)

def digest(path):
    with Path(path).open('rb') as stream: return file_digest(stream, 'sha256').hexdigest()

def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def read(path): return json.loads(Path(path).read_bytes())
def timestamp(): return datetime.now(timezone.utc).isoformat()

def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--gate', type=Path, required=True)
    ap.add_argument('--gate-sha256', required=True)
    args = ap.parse_args(); gate_path = args.gate.resolve()
    need(digest(gate_path) == args.gate_sha256, 'wrapper independent gate digest')
    need(digest(DOMAIN) == DOMAIN_SHA, 'portfolio independent domain gate digest')
    gate, domain = read(gate_path), read(DOMAIN)
    need(gate['status'] == 'INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS', 'wrapper gate status')
    need(domain['status'] == 'INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS', 'portfolio domain gate status')
    native = [EXE, ROOT/'acceleration/factor_permutation_anneal_20260930_v2.cu',
        ROOT/'acceleration/build_factor_permutation_anneal_20260930_v2.ps1']
    raw_cores = [PORTFOLIO/f'core_{i:02d}.json' for i in range(4)]
    wrapper_inputs = [ENGINE, ENGINE.with_name('theory_20260930_factor_permutation_annealer_v4_spec.md'),
        *native, DOMAIN, PORTFOLIO/'summary.json', *raw_cores]
    for p in wrapper_inputs:
        need(gate['inputs_sha256'].get(key(p)) == digest(p), 'exact independently calibrated input '+key(p))
    for p in [PORTFOLIO/'summary.json', *raw_cores]:
        need(domain['inputs_sha256'].get(key(p)) == digest(p), 'exact independently checked selected core '+key(p))
    need(shutil.disk_usage(ROOT).free > 4*1024**3, 'host free-space budget')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    cases = [dict(core=f'connected_{i:02d}', core_index=i, temperature=t,
        label=f'connected_{i:02d}_T'+str(t).replace('.', '_'), seed=20260930+i,
        chains=16, chunks=8, steps=1024, seconds=120, supervisor_seconds=120,
        maximum_new_proposals=131072) for i in range(4) for t in (1, 0.25, 0)]
    inputs = [Path(__file__), SPEC, *wrapper_inputs, gate_path, ROOT/'uv.lock', ROOT/'pyproject.toml',
        PORTFOLIO/'selection_manifest.json', PORTFOLIO/'eligibility.json', PORTFOLIO/'stages.json']
    bindings = {key(p): digest(p) for p in inputs}
    save(out/'manifest.json', dict(timestamp=timestamp(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(ROOT), python=platform.python_version(),
        uv_version=subprocess.check_output(['uv', '--version'], text=True).strip(), inputs_sha256=bindings,
        objective=OBJECTIVE, planned_cases=cases, maximum_new_proposals=1572864,
        maximum_distinct_initialized_chains=64, maximum_stage_chain_endpoints=192,
        selection='The four frozen connected P=I cores selected by first eligible M2 in each M1 stage, then first four eligible stages.',
        numerical_acceptance='Floating-point exponential acceptance is heuristic; objective and deltas are exact integers.',
        gpu=subprocess.check_output(['nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.free', '--format=csv'], text=True),
        cpu=platform.processor(), seed_semantics='Only each T1 phase initializes 16 chains; later phases preserve exact current/best permutations, RNG and counters.',
        comparisons='The objective has the same definition on all cores, but each core has a different feasible domain; within-core progress only.',
        success='Integer E=0 stops this whole pilot for independent raw-factor, mixed/column-cap and residual review.',
        falsification='A positive score, failed run or resource stop does not exclude any core or the target.',
        target_resolution=False, independent_approval=False, no_engine_or_old_artifact_changes=True))
    resumes = {}; blocked = set(); zero_reported = False; records = []; begun = time.monotonic()
    for case in cases:
        core, label = case['core'], case['label']
        if zero_reported or core in blocked:
            record = dict(case=case, stage='SKIPPED', reason='E0 awaits independent review' if zero_reported else 'Previous phase failed or reached a resource limit')
            save(out/(label+'.receipt.json'), record); records.append(record); continue
        resume = resumes.get(core); before = read(resume) if resume else None
        initial_proposals = sum(s['proposals'] for s in before['chains']) if before else 0
        initial_best = min(s['best_score'] for s in before['chains']) if before else None
        directory = out/label
        command = [sys.executable, str(ENGINE), 'run', '--out', str(directory), '--core', core,
            '--independent-gate', str(gate_path), '--independent-gate-sha256', args.gate_sha256,
            '--portfolio-domain-gate', str(DOMAIN), '--portfolio-domain-gate-sha256', DOMAIN_SHA]
        if resume: command += ['--resume', str(resume)]
        for field in ('seed', 'temperature', 'chains', 'chunks', 'steps', 'seconds'): command += ['--'+field, str(case[field])]
        state_bindings = dict(resume_path=key(resume) if resume else None,
            resume_sha256=digest(resume) if resume else None,
            resume_null_reason=None if resume else 'This is the first phase and initializes the seed-bound chains.',
            initial_proposal_total=initial_proposals, initial_best_reported_score=initial_best,
            initial_best_null_reason=None if resume else 'Native initial input is saved by the wrapper; this driver does not recompute its objective.')
        save(out/(label+'.manifest.json'), dict(timestamp=timestamp(), case=case, command=command,
            **state_bindings, manifest_sha256=digest(out/'manifest.json')))
        print(json.dumps(dict(state='PORTFOLIO_PHASE_LAUNCHING', case=label, resume=state_bindings['resume_path'])), flush=True)
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
            **state_bindings, completed_chunks=0, observed_new_proposals=0)
        checkpoints = sorted(directory.glob('checkpoint_*.json')) if directory.exists() else []
        if checkpoints:
            last = checkpoints[-1]; after = read(last); best = min(s['best_score'] for s in after['chains'])
            need(len(after['chains']) == 16, 'exact chain count')
            increment = sum(s['proposals'] for s in after['chains'])-initial_proposals
            need(0 <= increment <= 131072 and increment == len(checkpoints)*16*1024, 'exact saved proposal increments')
            need(initial_best is None or best <= initial_best, 'historical best preserved across resume')
            record.update(completed_chunks=len(checkpoints), observed_new_proposals=increment,
                last_checkpoint=key(last), last_checkpoint_sha256=digest(last), final_best_reported_score=best)
            zero_reported = best == 0; resumes[core] = last
        if record['stage'] == 'COMPLETED':
            summary = read(directory/'summary.json')
            need(summary['completed_chunks'] == record['completed_chunks'], 'engine saved-chunk agreement')
            need(record['completed_chunks'] > 0, 'completed phase saved at least one chunk')
            record.update(summary=key(directory/'summary.json'), summary_sha256=digest(directory/'summary.json'))
            if record['completed_chunks'] < 8 and not zero_reported:
                record['stage'] = 'STOPPED_RESOURCE_LIMIT'; blocked.add(core)
        else:
            blocked.add(core)
            record['unsaved_inflight_proposals'] = None
            record['unsaved_inflight_proposals_null_reason'] = 'An abnormal or terminated native chunk may not have saved its exact final counter.'
        save(out/(label+'.receipt.json'), record); records.append(record)
        print(json.dumps(dict(state=record['stage'], case=label, completed_chunks=record['completed_chunks'],
            observed_new_proposals=record['observed_new_proposals'], best=record.get('final_best_reported_score'))), flush=True)
    need(all(digest(ROOT/p) == h for p, h in bindings.items()), 'all frozen initial inputs remain unchanged')
    summary = dict(status='CANDIDATE_CONNECTED_CORE_PORTFOLIO_PILOT_COMPLETED', timestamp=timestamp(),
        manifest_sha256=digest(out/'manifest.json'), cases=records, wall_seconds=time.monotonic()-begun,
        attempted_phases=sum(r['stage'] != 'SKIPPED' for r in records), completed_phases=sum(r['stage'] == 'COMPLETED' for r in records),
        errors=sum(r['stage'] == 'ERROR' for r in records), resource_stops=sum(r['stage'] == 'STOPPED_RESOURCE_LIMIT' for r in records),
        skipped_phases=sum(r['stage'] == 'SKIPPED' for r in records),
        completed_chunks=sum(r.get('completed_chunks', 0) for r in records),
        completed_new_proposals=sum(r.get('observed_new_proposals', 0) for r in records), maximum_new_proposals=1572864,
        distinct_initialized_chains_with_saved_checkpoints=16*sum(r['case']['temperature'] == 1 and r.get('completed_chunks', 0)>0 for r in records),
        stage_chain_endpoints_with_saved_checkpoints=16*sum(r.get('completed_chunks', 0)>0 for r in records),
        zero_reported=zero_reported, independent_object_audit_required=True, independent_approval=False, target_resolution=False,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        limitations=['Scores are producer-reported until independent exact raw recomputation.',
            'Positive scores are not bounds or exclusions.', 'The same chains continue across temperatures; phase-chain counts overlap.',
            'P=I and the four selected cores are restrictions, not target automorphism assumptions.',
            'No residual adjacency search was performed.'])
    save(out/'summary.json', summary)
    print(json.dumps(dict(summary=key(out/'summary.json'), sha256=digest(out/'summary.json'), zero_reported=zero_reported)), flush=True)

if __name__ == '__main__': main()
