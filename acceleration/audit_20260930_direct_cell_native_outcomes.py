"""Independent UNKNOWN execution audit for either frozen direct-cell formula."""
import argparse
import copy
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'acceleration/results'
DATA = BASE / '20260930_direct_cell_count_cnf'
DOC = ROOT / 'docs/AUDIT_20260930_DIRECT_CELL_NATIVE_OUTCOMES.md'
WSL = ['wsl.exe', '--distribution', 'Ubuntu-24.04', '--exec']
VERSION = '1.9.5 146207318796f094dcded87349a64f0c6927309e'
NATIVE = 'build/research-cadical195/source/build/cadical'
NATIVE_SHA = '021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'
DRIVER = 'acceleration/native_20260930_direct_cell_count.py'
DRIVER_SHA = '10be73104e53f3ac90ca094771ab8afd5ba7071a1a6730046b067cc898fe498d'
GATES = [
    ('direct_cell_count_cnf', 'a7fd5968681257c60a0e82a36b53f40798487d727f2f467dae47918becf84042', 'INDEPENDENT_DIRECT_CELL_ALL_CAPS_ENCODING_PASS'),
    ('direct_cell_semantics', '88d6e8134c34b61d44a29e0bc525aebfb260f3f71c78efa72b98a7049275fdc8', 'INDEPENDENT_DIRECT_CELL_SEMANTICS_PASS'),
    ('direct_cell_count_object_calibration', '8e3666c68828e2c08bca49a39a108630652f17a5aed0ebe9dbce23dc4bf9b427', 'INDEPENDENT_DIRECT_CELL_ALL_CAPS_OBJECT_CALIBRATION_PASS')]
VARIANTS = {
    'standalone': (23112, 320484, '45bac5dddcc805010dd4da150cc1c4613855b5d0e1e436f7b584067875c85250', 'c74a90c4e81218d98623fa7fa683a5680c67e3b82f2e33fefc453c705c411b87', 'aa7f0e9ce4cd1679a1acc0aff0a8a76bbf60d2834013e419289be82ce8331e1e'),
    'at_least_seven': (169151, 968960, '07323c9fbbd75e328dfa0d1a99c760823799ecf7bba74722e2720d7dbb97c959', 'ea45aa8045ac7193e9492daae383d599cccdfcf0741d3a9357984dcadd5e0cbb', '8455669b3eec2edecd3e37bf7accebca75d8a65798b08a35f07fabb24edd96bf')}
LIMITS = dict(native_wall_seconds=60, conflicts=1000000,
    address_space_bytes=4294967296, trace_file_bytes=10737418240,
    kill_grace_seconds=5, outer_guard_seconds=70, maximum_research_calls=1,
    automatic_retry=False, host_reserve_bytes=21 * 1024**3, ext4_reserve_bytes=11 * 1024**3)


def need(value, message):
    if not value:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def linux(path):
    p = Path(path).resolve().as_posix()
    need(p[1:3] == ':/', 'absolute Windows source path')
    return '/mnt/' + p[0].lower() + p[2:]


def metric(text, pattern, convert):
    found = re.findall(pattern, text, re.M)
    need(len(found) == 1, 'unique native metric ' + pattern)
    return convert(found[0])


def parse_unknown(text, receipt, variant):
    n, m = VARIANTS[variant][:2]
    lines = text.strip().splitlines()
    need(lines.count('c Version ' + VERSION) == 1, 'exact solver version')
    need(lines.count(f"c found 'p cnf {n} {m}' header") == 1, 'exact parsed dimensions')
    need(lines.count("c setting conflict limit to 1000000 conflicts (due to '1000000')") == 1, 'configured conflict bound')
    need(re.findall(r'^c (UNKNOWN|SATISFIABLE|UNSATISFIABLE)\s*$', text, re.M) == ['UNKNOWN'], 'one literal UNKNOWN result')
    need(not re.search(r'^[sv]\s', text, re.M), 'no SAT/UNSAT status or model lines')
    need(receipt['outer_windows_guard_expired'] is False and receipt['outer_windows_guard_seconds'] == 70, 'normal outer supervision')
    code = receipt['actual_exit_code']
    need(code in (0, 124), 'supported UNKNOWN return boundary')
    wall = receipt['wall_seconds']
    need(type(wall) in (float, int) and 0 < wall < 70, 'observed host wall time')
    stats = dict(
        conflicts=metric(text, r'^c conflicts:\s+(\d+)\s', int),
        cpu_seconds=metric(text, r'^c total process time since initialization:\s+([0-9.]+)\s+seconds', float),
        native_wall_seconds=metric(text, r'^c total real time since initialization:\s+([0-9.]+)\s+seconds', float),
        native_max_RSS_MB=metric(text, r'^c maximum resident set size of process:\s+([0-9.]+)\s+MB', float))
    trace_counts = re.findall(r'^c DRAT (\d+) bytes ', text, re.M)
    need(len(trace_counts) <= 1, 'at most one native trace-byte statistic')
    stats['trace_bytes'] = int(trace_counts[0]) if trace_counts else None
    stats['trace_bytes_null_reason'] = None if trace_counts else 'SIGTERM log omitted the closing-proof byte statistic; trace length is checked from both preserved files.'
    need(0 < stats['cpu_seconds'] < 65 and 0 < stats['native_wall_seconds'] < 65, 'bounded positive native timing')
    need(stats['cpu_seconds'] <= stats['native_wall_seconds'] + 0.05, 'CPU versus native elapsed time')
    need(stats['native_wall_seconds'] <= wall + 0.05, 'native versus wrapper timing')
    if stats['trace_bytes'] is not None:
        need(0 < stats['trace_bytes'] <= LIMITS['trace_file_bytes'], 'reported trace within file cap')
    if code == 0:
        need(lines[-1] == 'c exit 0' and lines.count('c exit 0') == 1, 'normal terminal native exit zero')
        need(not any('caught signal' in line or 'raising signal' in line for line in lines), 'normal exit not signal boundary')
        need(stats['trace_bytes'] is not None, 'normal completion emitted trace-byte statistic')
        need(stats['conflicts'] >= LIMITS['conflicts'] and wall < 60, 'conflict limit reached before wall guard')
        reason = 'UNKNOWN_NATIVE_CONFLICT_LIMIT'
        native_exit = 0
    else:
        need(lines.count('c caught signal 15 (SIGTERM)') == 1 and lines[-1] == 'c raising signal 15 (SIGTERM)', 'literal SIGTERM termination')
        need(not any(line.startswith('c exit ') for line in lines) and 60 <= wall < 65, 'timeout wrapper boundary')
        reason = 'UNKNOWN_GNU_TIMEOUT_SIGTERM'
        native_exit = None
    return dict(**stats, wrapper_exit_code=code, native_exit_code=native_exit,
        termination=reason, configured_conflicts=LIMITS['conflicts'],
        conflict_limit_reached=stats['conflicts'] >= LIMITS['conflicts'],
        wrapper_wall_seconds=wall,
        native_exit_null_reason=None if native_exit == 0 else 'Timeout wrapper returned 124 after signal; no normal native exit code.')


def validate(summary, manifest, receipt, launch, workspace, text, variant, proofsha, proofsize):
    need(summary['receipt'] == receipt, 'raw solver receipt matches summary')
    need(summary['variant'] == manifest['variant'] == launch['variant'] == variant, 'same variant everywhere')
    need(summary['research_calls'] == 1 and summary['automatic_retry'] is False and summary['target_resolution'] is False and summary['independent_approval'] is False, 'one unapproved research call without target promotion')
    need(summary['interpreted_result'] == 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME', 'saved outcome UNKNOWN')
    need(manifest['mode'] == 'RESEARCH' and manifest['limits'] == LIMITS, 'exact preregistered scope and limits')
    need(manifest['host_free_bytes'] >= LIMITS['host_reserve_bytes'] and manifest['ext4_free_bytes'] >= LIMITS['ext4_reserve_bytes'], 'saved initial storage reserves')
    need(re.fullmatch('/tmp/conway99-direct-cell-[A-Za-z0-9]+', workspace['path']) and workspace['preserved'] is True, 'dedicated preserved ext4 path')
    proof = workspace['path'] + '/proof.drat'
    command = [*WSL, '/usr/bin/timeout', '--signal=TERM', '--kill-after=5s', '60s', '/usr/bin/prlimit', '--as=4294967296:4294967296', '--fsize=10737418240:10737418240', '--core=0:0', linux(ROOT / NATIVE), '--no-binary', '-c', '1000000', linux(DATA / variant / 'instance.cnf'), proof]
    need(launch['command'] == receipt['command'] == command, 'literal full command and resource caps')
    need(launch['cnf_sha256'] == VARIANTS[variant][2] and launch['ext4_proof'] == proof, 'launch formula/proof')
    stats = parse_unknown(text, receipt, variant)
    transfer = summary['proof_copy']
    need(transfer['sha256'] == proofsha and transfer['bytes'] == proofsize and transfer['linux_source'] == proof, 'trace size/hash agree with receipt and saved bytes')
    need(stats['trace_bytes'] is None or stats['trace_bytes'] == proofsize, 'trace bytes agree with native statistic when emitted')
    need(0 < proofsize <= LIMITS['trace_file_bytes'], 'complete saved partial trace respects cap')
    for field in ('native_hash_receipt', 'copy_receipt'):
        need(transfer[field]['actual_exit_code'] == 0 and transfer[field]['outer_windows_guard_expired'] is False, 'completed trace preservation command')
    return stats


def calibrate(summary, manifest, receipt, launch, workspace, text, variant, proofsha, proofsize):
    rejected = []
    names = ['false_outcome', 'wrong_exit', 'configured_conflict_limit', 'wrong_trace_hash', 'wrong_trace_size', 'expired_outer_guard', 'second_attempt', 'false_target', 'wrong_command', 'missing_metric', 'false_sat_line', 'wrong_dimensions', 'wrong_version', 'missing_terminal', 'spurious_model', 'false_wall_time']
    for name in names:
        s, m, r, l, w, t = copy.deepcopy(summary), copy.deepcopy(manifest), copy.deepcopy(receipt), copy.deepcopy(launch), copy.deepcopy(workspace), text
        if name == 'false_outcome': s['interpreted_result'] = 'UNSAT_TRACE_UNCHECKED'
        elif name == 'wrong_exit': r['actual_exit_code'] = 20
        elif name == 'configured_conflict_limit': m['limits']['conflicts'] = 999999
        elif name == 'wrong_trace_hash': s['proof_copy']['sha256'] = '0' * 64
        elif name == 'wrong_trace_size': s['proof_copy']['bytes'] += 1
        elif name == 'expired_outer_guard': r['outer_windows_guard_expired'] = True
        elif name == 'second_attempt': s['research_calls'] = 2
        elif name == 'false_target': s['target_resolution'] = True
        elif name == 'wrong_command': r['command'][7] = '600s'; l['command'] = r['command']
        elif name == 'missing_metric': t = re.sub(r'^c conflicts:.*\n', '', t, flags=re.M)
        elif name == 'false_sat_line': t = t.replace('c UNKNOWN', 's SATISFIABLE')
        elif name == 'wrong_dimensions': t = t.replace(f'p cnf {VARIANTS[variant][0]} {VARIANTS[variant][1]}', 'p cnf 1 1')
        elif name == 'wrong_version': t = t.replace('c Version ' + VERSION, 'c Version altered')
        elif name == 'missing_terminal': t = '\n'.join(t.strip().splitlines()[:-1])
        elif name == 'spurious_model': t += 'v 1 0\n'
        elif name == 'false_wall_time': r['wall_seconds'] = 9999
        s['receipt'] = r
        try: validate(s, m, r, l, w, t, variant, proofsha, proofsize)
        except (ValueError, KeyError): rejected.append(name)
        else: raise ValueError('corrupted fixture accepted: ' + name)
    # Deliberately synthetic parser-only boundary, not another research run.
    n, m = VARIANTS[variant][:2]
    common = f"c Version {VERSION}\nc found 'p cnf {n} {m}' header\nc setting conflict limit to 1000000 conflicts (due to '1000000')\nc UNKNOWN\nc conflicts: 1000000 1 per second\nc total process time since initialization: 50 seconds\nc total real time since initialization: 55 seconds\nc maximum resident set size of process: 100 MB\nc DRAT 100 bytes (0 MB)\n"
    positives = []
    for code, tail, wall in [(0, 'c exit 0\n', 55.2), (124, 'c caught signal 15 (SIGTERM)\nc raising signal 15 (SIGTERM)\n', 60.1)]:
        r = dict(actual_exit_code=code, outer_windows_guard_expired=False, outer_windows_guard_seconds=70, wall_seconds=wall)
        positives.append(parse_unknown(common + tail, r, variant))
    return dict(actual_saved_UNKNOWN_positive=True, synthetic_parser_boundaries=positives, synthetic_not_research=True, corruptions_rejected=rejected)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--summary-sha256', required=True)
    ap.add_argument('--variant', choices=tuple(VARIANTS), required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out, run = args.out.resolve(), args.run.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    bindings = {}
    stats_cache = {}

    def bind(path, expected=None):
        path = Path(path).resolve(); stat = path.stat(); name = key(path)
        fingerprint = (stat.st_size, stat.st_mtime_ns)
        if name not in bindings:
            bindings[name] = sha(path); stats_cache[name] = fingerprint
        need(stats_cache[name] == fingerprint, 'unchanged cached file metadata ' + name)
        need(expected is None or bindings[name] == expected, 'literal byte identity ' + name)
        return bindings[name]

    def load(path, expected=None):
        bind(path, expected)
        return read(path)

    def check_receipt(r, allowed=(0,)):
        need(r['actual_exit_code'] in allowed and r['outer_windows_guard_expired'] is False, 'saved supporting command completed')
        for stream in ('stdout', 'stderr'):
            bind(ROOT / r[stream], r[stream + '_sha256'])

    def capture(command, name):
        ts = stamp(); before = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        stdout, stderr = out / (name + '.stdout.log'), out / (name + '.stderr.log')
        stdout.write_bytes(proc.stdout); stderr.write_bytes(proc.stderr)
        rec = dict(timestamp=ts, command=command, exit_code=proc.returncode, wall_seconds=time.monotonic() - before,
                   stdout=key(stdout), stdout_sha256=sha(stdout), stderr=key(stderr), stderr_sha256=sha(stderr))
        save(out / (name + '.json'), rec)
        return proc, rec

    try:
        summary = load(run / 'summary.json', args.summary_sha256)
        manifest = load(run / 'manifest.json')
        preflight_dir = BASE / ('20260930_direct_cell_standalone_native_preflight' if args.variant == 'standalone' else '20260930_direct_cell_count_coupled_native_preflight')
        preflight = load(preflight_dir / 'summary.json')
        preflight_manifest = load(preflight_dir / 'manifest.json')
        need(preflight['status'] == 'DIRECT_CELL_ALL_CAPS_NATIVE_PREFLIGHT_PASS' and preflight['research_calls'] == 0 and preflight['variant'] == args.variant, 'saved variant preflight PASS without research calls')
        need(preflight['inputs_sha256'] == manifest['inputs_sha256'] and preflight_manifest['inputs_sha256'] == manifest['inputs_sha256'], 'preflight to research exact source/input closure')
        need(preflight_manifest['limits'] == LIMITS and preflight_manifest['mode'] == 'PREFLIGHT_ONLY', 'preflight exact resource protocol')
        for mapping in (summary['inputs_sha256'], manifest['inputs_sha256'], summary['outputs_sha256']):
            for name, value in mapping.items(): bind(ROOT / name, value)
        need(summary['inputs_sha256'] == manifest['inputs_sha256'], 'manifest/summary source closure identity')
        bind(ROOT / DRIVER, DRIVER_SHA); bind(ROOT / NATIVE, NATIVE_SHA)
        direct = {key(DATA / args.variant / name): digest for name, digest in zip(('instance.cnf', 'model.json', 'scope.json'), VARIANTS[args.variant][2:])}
        for name, value in direct.items():
            need(manifest['inputs_sha256'][name] == value, 'intended selected input in manifest')
        gate_records = []
        for name, digest, status in GATES:
            path = BASE / '20260930_independent_review' / name / 'summary.json'
            gate = load(path, digest)
            need(gate['status'] == status, 'separate immutable gate status')
            for p, h in gate['inputs_sha256'].items(): bind(ROOT / p, h)
            for p, h in direct.items(): need(gate['inputs_sha256'][p] == h, 'gate binds literal formula/model/scope')
            gate_records.append(dict(path=key(path), sha256=digest, status=status))
        receipt = load(run / 'main/solver.receipt.json')
        launch = load(run / 'main/launch.json'); workspace = load(run / 'workspace.json')
        text = (ROOT / receipt['stdout']).read_text(encoding='utf-8')
        need((ROOT / receipt['stderr']).read_bytes() == b'', 'empty native solver stderr')
        trace = run / 'main/proof.drat'; trace_stat = trace.stat(); trace_sha = bind(trace)
        metrics = validate(summary, manifest, receipt, launch, workspace, text, args.variant, trace_sha, trace_stat.st_size)
        controls = calibrate(summary, manifest, receipt, launch, workspace, text, args.variant, trace_sha, trace_stat.st_size)
        save(out / 'controls.json', controls)
        transfer = summary['proof_copy']; proof = workspace['path'] + '/proof.drat'
        native_hash = load(run / 'main/transfer_hash.receipt.json'); copied = load(run / 'main/transfer_copy.receipt.json')
        need(transfer['native_hash_receipt'] == native_hash and transfer['copy_receipt'] == copied, 'original transfer receipt equality')
        need(native_hash['command'] == [*WSL, '/usr/bin/sha256sum', proof], 'exact native hash command')
        need(copied['command'] == [*WSL, '/usr/bin/cp', '--', proof, linux(trace)], 'exact native copy command')
        need((ROOT / native_hash['stdout']).read_text().split() == [trace_sha, proof], 'recorded native/local full trace hash agreement')
        for r in (native_hash, copied, manifest['mount_receipt'], manifest['disk_receipt'], workspace['receipt']): check_receipt(r)
        need('ext4' in (ROOT / manifest['mount_receipt']['stdout']).read_text().split(), 'recorded ext4 filesystem')
        need(manifest['mount_receipt']['command'] == [*WSL, '/usr/bin/findmnt', '--target', '/tmp', '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS', '--noheadings'], 'recorded mount command')
        need(int((ROOT / manifest['disk_receipt']['stdout']).read_text().splitlines()[-1]) == manifest['ext4_free_bytes'], 'recorded initial ext4 free bytes')
        before_launch = load(run / 'disk_before_launch.receipt.json'); check_receipt(before_launch)
        need(before_launch['command'] == [*WSL, '/usr/bin/df', '--output=avail', '-B1', workspace['path']], 'immediate disk command')
        need(int((ROOT / before_launch['stdout']).read_text().splitlines()[-1]) >= LIMITS['ext4_reserve_bytes'], 'immediate saved ext4 reserve')
        historical_process = []
        ps_cmd = [*WSL, '/usr/bin/ps', '-C', 'cadical', '-o', 'pid,ppid,comm,pcpu,rss,args']
        for name, field in [('processes_before', 'processes_before'), ('processes_after', 'fresh_process_observation')]:
            r = load(run / (name + '.receipt.json'))
            need(r == summary[field] and r['command'] == ps_cmd, 'targeted historical process receipt')
            check_receipt(r, (0, 1))
            raw = (ROOT / r['stdout']).read_text()
            if r['actual_exit_code'] == 1: need(len(raw.strip().splitlines()) <= 1, 'empty exact-name observation')
            historical_process.append(dict(name=name, timestamp=r['timestamp'], exit_code=r['actual_exit_code'], nonempty_records=max(0, len(raw.strip().splitlines()) - 1), stderr=(ROOT/r['stderr']).read_text()))
        need(not (run / 'main/parsed_model.json').exists() and not (run / 'main/decoded_factor.json').exists(), 'no saved SAT factor/model')
        p, fresh_hash = capture([*WSL, '/usr/bin/sha256sum', proof], 'fresh_ext4_hash')
        need(p.returncode == 0 and p.stdout.decode().split() == [trace_sha, proof], 'fresh full ext4 trace identity')
        p, fresh_size = capture([*WSL, '/usr/bin/stat', '--format=%s', proof], 'fresh_ext4_size')
        need(p.returncode == 0 and int(p.stdout.decode().strip()) == trace_stat.st_size, 'fresh exact ext4 byte length')
        p, fresh_ps = capture(ps_cmd, 'targeted_process')
        need(p.returncode in (0, 1), 'fresh exact-name process query completed')
        if p.returncode == 1: need(len(p.stdout.decode().strip().splitlines()) <= 1, 'fresh empty exact-name process query')
        exact_input = linux(DATA / args.variant / 'instance.cnf')
        active = [line for line in p.stdout.decode().splitlines()[1:] if exact_input in line]
        need(not active, 'no current exact-input solver observed')
        need(trace.stat().st_size == trace_stat.st_size and trace.stat().st_mtime_ns == trace_stat.st_mtime_ns, 'host trace unchanged throughout audit')
        bind(__file__); bind(DOC); bind(ROOT / 'uv.lock'); bind(ROOT / 'pyproject.toml')
        for name, fingerprint in stats_cache.items():
            st = (ROOT / name).stat(); need((st.st_size, st.st_mtime_ns) == fingerprint, 'frozen file stable throughout audit')
        trace_record = dict(path=key(trace), sha256=trace_sha, bytes=trace_stat.st_size, original_ext4_path=proof,
            local_complete_hash=True, fresh_ext4_complete_hash=True, availability='LOCAL_ONLY', unsat_certificate=False,
            proof_replay_performed=False, reason='UNKNOWN partial trace; no complete contradiction was claimed or independently replayed.')
        ts = stamp()
        report = dict(status='INDEPENDENT_DIRECT_CELL_UNKNOWN_NATIVE_RUN_AUDIT_PASS', timestamp=ts,
            variant=args.variant, inputs_sha256=bindings, gates=gate_records,
            command=[sys.executable, *sys.argv], python=platform.python_version(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            run_source_commit=manifest['source_commit'], run_command=manifest['command'],
            actual_research_calls=1, new_solver_calls=0, interpreted_result='UNKNOWN', metrics=metrics,
            configured_limits=LIMITS, partial_trace=trace_record, solver_version=VERSION, solver_binary_sha256=NATIVE_SHA,
            controls_rejected=len(controls['corruptions_rejected']), historical_process_observations=historical_process,
            fresh_ext4_hash_receipt=fresh_hash, fresh_ext4_size_receipt=fresh_size, fresh_targeted_process_receipt=fresh_ps,
            no_exact_input_process_observed=True, target_resolution=False,
            scope='Exact saved native execution only. Literal fixed-support full-Gram factor plus all outside-column caps' + (' and >=7 exceptions.' if args.variant == 'at_least_seven' else ', without exception-count bound.'),
            shared_components=['Saved producer/native/encoding/object evidence authenticated as input data.', 'Parser/receipt design follows previous independent UNKNOWN audits; only standard-library imports and no producer execution.', 'Same pinned native solver, not an independent second solver.'],
            limitations=['UNKNOWN excludes nothing and supplies neither a factor nor a complete UNSAT proof.', 'No residual D or target graph is encoded; no unrestricted support coverage.', 'Address-space limit is configured; native RSS/CPU values are reported statistics.', 'Saved immediate host reserve is enforced by pinned source but not separately logged immediately before launch.', 'No performance comparison or external review claimed.'],
            artifact_availability='LOCAL_ONLY', elapsed_seconds=time.monotonic() - started)
        evidence = {key(p): sha(p) for p in out.iterdir() if p.is_file()}
        binding = dict(id='C-FIXED-HADAMARD-DIRECT-CELL-' + ('STANDALONE' if args.variant == 'standalone' else 'AT-LEAST-SEVEN') + '-NATIVE-UNKNOWN', revision=1,
            kind='empirical/engineering result', basis=['COMPUTED'], status='VERIFIED', review_state='CLEAR',
            statement='One frozen direct-cell native pilot returned UNKNOWN under its recorded wall/conflict/resource guards; its complete saved partial trace agrees with both recorded and fresh ext4 hashes. It excludes no factor or target.',
            scope=report['scope'], verifier='/root/structural_attack', producer='/root',
            method='Independent raw log/receipt/source/input/output checking, complete trace hashes, exact command reconstruction and fresh corruption controls.',
            dependencies=[dict(artifact=g['path'], sha256=g['sha256'], relation='verification_dependency') for g in gate_records],
            inputs_sha256=bindings, evidence_sha256=evidence, metrics=metrics, trace=trace_record,
            shared_components=report['shared_components'], limitations=report['limitations'],
            artifact_availability='LOCAL_ONLY', external_review=None, external_review_reason='No external review asserted.', created_at=ts, updated_at=ts)
        save(out / 'claim_binding.json', binding)
        report['outputs_sha256'] = {key(p): sha(p) for p in out.iterdir() if p.is_file()}
        save(out / 'summary.json', report)
        print(json.dumps(dict(status=report['status'], variant=args.variant, summary_sha256=sha(out/'summary.json'), binding_sha256=sha(out/'claim_binding.json'), metrics=metrics, trace=trace_record)))
    except BaseException as error:
        save(out / 'failure.json', dict(status='AUDIT_FAILED', timestamp=stamp(), error=repr(error)))
        raise


if __name__ == '__main__':
    main()
