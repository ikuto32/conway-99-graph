"""Independent source-authenticated exact DRAT checker path and falsification controls.

No native producer imports. Call only inside a declared contained invocation.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
HELPER_SHA = '93e6426fb5a8503e541a692d6c3d2b3e6210be43c16b2a9ff9772aba56085459'
BUILD = ROOT / 'build/rook-drat-checker'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def authenticate(pin):
    pin(HELPER, HELPER_SHA)
    module_spec = importlib.util.spec_from_file_location('frozen_independent_drat_authentication', HELPER)
    helper = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(helper)
    for path in [BUILD / 'drat-trim.exe', BUILD / 'build_manifest.json', BUILD / 'build_receipt.json']:
        pin(path, helper.PINS[path])
    # Authenticates raw upstream Git blob, sole portability hunk, preserved
    # binary/compiler/environment/build receipts. No proof replay helper used.
    return helper.authenticate(pin)


def replay(name, cnf, proof, out, deadline, expected=True):
    command = [str(BUILD / 'drat-trim.exe'), str(cnf.resolve()), str(proof.resolve())]
    allocation = deadline.child_seconds(deadline.status()['remaining_seconds'], reserve_seconds=10)
    require(allocation > 0, 'remaining checker allocation')
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).isoformat()
    stdout = out / (name + '.stdout.log')
    stderr = out / (name + '.stderr.log')
    with stdout.open('xb') as so, stderr.open('xb') as se:
        worker = subprocess.Popen(command, cwd=ROOT, stdout=so, stderr=se)
        timed_out = False
        try:
            code = worker.wait(timeout=allocation)
        except subprocess.TimeoutExpired:
            timed_out = True
            worker.kill()
            code = worker.wait(timeout=5)
    text = stdout.read_text(errors='replace')
    statuses = [line.strip() for line in text.splitlines() if line.startswith('s ')]
    accepted = not timed_out and code == 0 and statuses == ['s VERIFIED']
    receipt = {
        'name': name, 'command': command, 'cwd': str(ROOT), 'timestamp': stamp,
        'allocated_seconds_from_same_invocation': allocation, 'actual_exit_code': code,
        'timed_out': timed_out, 'reaped': worker.poll() is not None,
        'accepted': accepted, 'expected_acceptance': expected,
        'cnf_path': key(cnf), 'cnf_sha256': sha(cnf), 'proof_path': key(proof), 'proof_sha256': sha(proof),
        'proof_bytes': proof.stat().st_size, 'stdout': key(stdout), 'stdout_sha256': sha(stdout),
        'stderr': key(stderr), 'stderr_sha256': sha(stderr), 'elapsed_seconds': time.monotonic() - started,
    }
    save(out / (name + '.receipt.json'), receipt)
    require(not timed_out, 'complete proof checking not completed within the allocated budget')
    require(accepted == expected, 'proof/control replay result ' + name)
    print(json.dumps({'check': name, 'accepted': accepted, 'elapsed_seconds': receipt['elapsed_seconds']}), flush=True)
    return receipt


def controls(out, deadline):
    fixtures = {
        'tiny_unsat.cnf': b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n',
        'tiny_sat.cnf': b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n',
        'tiny_valid.drat': b'-2 0\n1 0\n0\n',
        'empty_only.drat': b'0\n',
        'fresh_unit.drat': b'3 0\n0\n',
        'truncated_reasoning.drat': b'-2 0\n',
    }
    for name, data in fixtures.items():
        with (out / name).open('xb') as stream:
            stream.write(data)
    clauses = [(1, 2), (1, -2), (-1, 2), (-1, -2)]
    truth = lambda rows: [bits for bits in range(4) if all(any(bool(bits & (1 << (abs(lit) - 1))) == (lit > 0) for lit in row) for row in rows)]
    require(truth(clauses) == [] and truth(clauses[:-1]) == [3], 'independent exhaustive two-variable truth table')
    tests = [
        ('positive_reasoning', 'tiny_unsat.cnf', 'tiny_valid.drat', True),
        ('missing_reasoning', 'tiny_unsat.cnf', 'empty_only.drat', False),
        ('invalid_fresh_unit', 'tiny_unsat.cnf', 'fresh_unit.drat', False),
        ('changed_SAT_formula', 'tiny_sat.cnf', 'tiny_valid.drat', False),
        ('truncated_reasoning', 'tiny_unsat.cnf', 'truncated_reasoning.drat', False),
    ]
    return [replay(name, out / cnf, out / proof, out, deadline, expected) for name, cnf, proof, expected in tests]


def native_status(text, exit_code, variables, clauses):
    """Unique status and true formula identity only; no historical 60s pin."""
    statuses = [line.strip() for line in text.splitlines() if line.startswith('s ')]
    if exit_code == 20 and statuses == ['s UNSATISFIABLE']:
        require(text.splitlines().count(f"c found 'p cnf {variables} {clauses}' header") == 1, 'unique actual native formula dimensions')
        require(text.splitlines().count('c exit 20') == 1, 'normal native20 exit')
        return 'UNSAT_COMPLETE_PROOF_PENDING'
    if exit_code == 10 and statuses == ['s SATISFIABLE']:
        require(text.splitlines().count(f"c found 'p cnf {variables} {clauses}' header") == 1, 'unique actual native formula dimensions')
        require(text.splitlines().count('c exit 10') == 1, 'normal native10 exit')
        return 'SAT_COMPLETE_OBJECT_PENDING'
    require(not (exit_code in (10, 20) or statuses in (['s SATISFIABLE'], ['s UNSATISFIABLE'])), 'inconsistent conclusive native outcome')
    return 'UNKNOWN'


def status_controls():
    good = "c found 'p cnf 2 4' header\ns UNSATISFIABLE\nc exit 20\n"
    require(native_status(good, 20, 2, 4) == 'UNSAT_COMPLETE_PROOF_PENDING', 'positive receipt parser')
    rejected = []
    for name, text, code in [
        ('wrong_header', good.replace('2 4', '2 5'), 20),
        ('wrong_exit', good, 0),
        ('duplicate_status', good + 's UNSATISFIABLE\n', 20),
        ('changed_status', good.replace('s UNSATISFIABLE', 's SATISFIABLE'), 20),
    ]:
        try:
            native_status(text, code, 2, 4)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted malformed native receipt ' + name)
    require(native_status('s UNKNOWN\n', 124, 2, 4) == 'UNKNOWN', 'timeout remains UNKNOWN')
    return {'rejected': rejected, 'timeout': 'UNKNOWN'}
