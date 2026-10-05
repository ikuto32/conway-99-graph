"""Fresh standalone CLI recovery of saved lex UNKNOWN trace bytes, not proof review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'acceleration/results/20260930_direct_cell_lex_unknown_trace_package'
OUT = ROOT / 'acceleration/results/20260930_direct_cell_lex_trace_recovery'
DEST = ROOT / 'build/research-local/direct-cell-lex-trace-recovery'
HELPER = ROOT / 'acceleration/recover_20260930_direct_cell_lex_unknown_traces.py'
MANIFEST_SHA = 'f4ab5f151b82bb57f621de549c6e3b7bb0eedbaa92148a7a3fcf89b65831b028'
HELPER_SHA = '83bef77829d2534119dc92cea6619420c735454160d0dbf31040bc1849913f8b'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def need(condition, label):
    if not condition:
        raise ValueError(label)


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    attempts = []
    start = time.monotonic()
    try:
        manifest_path = PACKAGE / 'package_manifest.json'
        need(sha(manifest_path) == MANIFEST_SHA, 'frozen package manifest')
        need(sha(HELPER) == HELPER_SHA, 'frozen independent-command recovery helper')
        need(not DEST.exists(), 'fresh ignored restore tree')
        pins = {key(p): sha(p) for p in (Path(__file__), HELPER, manifest_path,
                ROOT / 'uv.lock', ROOT / 'pyproject.toml')}
        save(OUT / 'manifest.json', dict(inputs_sha256=pins,
             timestamp=datetime.now(timezone.utc).isoformat(),
             selection='verify-only then fresh-output standalone CLI recovery',
             native_calls=0, proof_validity_checked=False, independent_approval=False))
        base = [sys.executable, '-B', str(HELPER), '--manifest', str(manifest_path),
                '--manifest-sha256', MANIFEST_SHA]
        for label, suffix in [('verify', ['--verify-only']), ('restore', ['--out', str(DEST)])]:
            command = base + suffix
            began = time.monotonic()
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60)
            stdout = OUT / (label + '.stdout.log')
            stderr = OUT / (label + '.stderr.log')
            stdout.write_bytes(completed.stdout)
            stderr.write_bytes(completed.stderr)
            attempt = dict(label=label, command=command, exit_code=completed.returncode,
                           seconds=time.monotonic()-began, timeout_seconds=60,
                           stdout_path=key(stdout), stdout_sha256=sha(stdout),
                           stderr_path=key(stderr), stderr_sha256=sha(stderr))
            attempts.append(attempt)
            save(OUT / (label + '.receipt.json'), attempt)
            need(completed.returncode == 0, 'standalone recovery CLI succeeds')
            result = json.loads(completed.stdout)
            need(result['status'] == 'SAVED_LEX_UNKNOWN_HOST_TRACE_RECOVERY_PASS', 'explicit recovery status')
            need(result['proof_validity_checked'] is False and result['complete_unsat_proof'] is False,
                 'transport scope only')
        manifest = json.loads(manifest_path.read_bytes())
        recovered = []
        for record in manifest['records']:
            original = ROOT / record['raw_original_path']
            destination = DEST / (record['variant'] + '.saved_unknown_trace.drat')
            need(destination.stat().st_size == record['raw_bytes'], 'restored complete saved length')
            need(sha(destination) == sha(original) == record['raw_sha256'], 'both fresh whole-file hashes')
            with original.open('rb') as a, destination.open('rb') as b:
                while True:
                    block = a.read(1024**2)
                    need(block == b.read(1024**2), 'literal restored/retained byte equality')
                    if not block:
                        break
            recovered.append(dict(variant=record['variant'], restored_path=key(destination),
                raw_sha256=record['raw_sha256'], raw_bytes=record['raw_bytes'],
                retained_original_path=record['raw_original_path'], literal_equal=True))
        receipt = dict(status='CANDIDATE_LEX_UNKNOWN_TRACE_STANDALONE_RECOVERY_COMPLETE',
            inputs_sha256=pins, attempts=attempts, recovered=recovered,
            seconds=time.monotonic()-start, complete_unsat_proof=False, native_calls=0,
            proof_validity_checked=False, independent_approval=False)
        save(OUT / 'receipt.json', receipt)
        print(json.dumps(dict(status=receipt['status'], raw_bytes=sum(r['raw_bytes'] for r in recovered),
             receipt_path=key(OUT / 'receipt.json'), receipt_sha256=sha(OUT / 'receipt.json'))))
    except BaseException as error:
        save(OUT / 'failure.json', dict(error=repr(error), attempts=attempts,
             source_sha256=sha(Path(__file__)), originals_preserved=True))
        raise


if __name__ == '__main__':
    main()
