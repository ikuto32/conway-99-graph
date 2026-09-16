"""Hard-bounded independent DRAT check of an audited fixed-K CNF.

The checker never imports a SAT solver/producer. A verified contradiction
excludes only this labeled K, relative to the frozen unrestricted CNF model.
"""
import argparse
from hashlib import sha256
import json
from math import ceil, isfinite
from pathlib import Path
import subprocess
import time

from audit_fixed_overlap_cnf import audit as audit_mapping

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT/'tools/drat-trim/drat-trim.exe'
SOURCE = ROOT/'tools/drat-trim/drat-trim.c'
CHECKER_SHA = '10d317df526c36453986ef09495864bcabd9d02d72d7b772ee78f07939870620'
SOURCE_SHA = '57df8efd73fc4fd81c4f255a8a7a1659c80c73ab0829cc8194a65f3432cd3e88'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def key(name):
    path = resolve(name)
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def digest(name):
    h = sha256()
    with resolve(name).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def check_drat(cnf, proof, seconds):
    require(type(seconds) in (int, float) and isfinite(seconds) and seconds > 0, 'Finite positive checker budget required')
    hashes = {key(p): digest(p) for p in (cnf, proof, CHECKER, SOURCE, Path(__file__))}
    require(hashes[key(CHECKER)] == CHECKER_SHA and hashes[key(SOURCE)] == SOURCE_SHA, 'Pinned DRAT checker changed')
    command = [str(CHECKER), str(resolve(cnf)), str(resolve(proof)), '-t', str(max(1, ceil(seconds)))]
    started = time.monotonic()
    try:
        process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=seconds, check=False)
        transcript = process.stdout + process.stderr
        verified = process.returncode == 0 and 's VERIFIED' in transcript.splitlines()
        code, reason = process.returncode, None
    except subprocess.TimeoutExpired as exc:
        def text(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
        transcript = text(exc.stdout) + text(exc.stderr)
        verified, code, reason = False, None, 'CHECKER_WALL_TIME_LIMIT'
    require(all(digest(p) == expected for p, expected in hashes.items()), 'Checker/CNF/proof changed during verification')
    return dict(status='DRAT_VERIFIED' if verified else 'UNKNOWN' if reason else 'DRAT_NOT_VERIFIED',
                verified=verified, inputs_sha256=hashes, checker_command=command, return_code=code,
                reason=reason, checker_wall_limit_seconds=seconds, elapsed_seconds=time.monotonic()-started,
                transcript=transcript, external_checker_no_solver_imported=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve previous proof check')
    existing = json.loads(args.audit.read_bytes())
    require(existing['status'] == 'INDEPENDENT_FIXED_OVERLAP_CNF_MAPPING_AUDIT_PASS', 'Prior mapping audit absent')
    previous = {key(p): h for p, h in existing['inputs_sha256'].items()}
    require(previous.get(key(args.manifest)) == digest(args.manifest), 'Mapping audit binds a different manifest')
    require(all(digest(p) == h for p, h in previous.items()), 'Changed mapping-audit dependency')
    # Recheck exact original CNF bytes plus all 1806 units independently.
    mapping = audit_mapping(resolve(args.manifest))
    cnf = resolve(mapping['cnf_path'])
    result = check_drat(cnf, args.proof, args.seconds)
    result['inputs_sha256'].update({key(p): h for p, h in mapping['inputs_sha256'].items()})
    result['inputs_sha256'].update({key(args.audit): digest(args.audit), key(Path(__file__)): digest(Path(__file__))})
    result.update(candidate_path=mapping['candidate_path'], candidate_sha256=mapping['candidate_sha256'],
                  cnf_path=key(cnf), cnf_sha256=digest(cnf), proof_path=key(args.proof), proof_sha256=digest(args.proof),
                  mapping_rechecked=True, fixed_K_excluded_by_verified_CNF=result['verified'],
                  general_nonexistence_proved=False, graph_witness_created=False,
                  scope='Only this labeled fixed K, conditional on the frozen unrestricted base-CNF encoding; independently rechecked mapping and DRAT contradiction. No general nonexistence or other-K exclusion.')
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'verified', 'candidate_path', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
