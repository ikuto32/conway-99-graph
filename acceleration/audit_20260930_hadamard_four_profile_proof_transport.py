"""Independent part-by-part gzip identity audit; no packager/checker imports."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import io
import json
import platform
import subprocess
import sys
import traceback
import zlib

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'acceleration/results/20260930_hadamard_four_profile_proof_package'
MANIFEST = PACKAGE + '/package_manifest.json'
MANIFEST_HASH = 'e55ce731d5ca1d18c4f5f5c9fc3195bc934f20f45b0172fc867ca1781e976250'
GATE = 'acceleration/results/20260930_independent_review/hadamard_fifteen_profile_unsat_v2/summary.json'
GATE_HASH = '351b66f7b01f5863e932991737b8d35f4b1c043b48ff673c987c653d6ed81768'
CASES = [6, 12, 18, 24, 30, 36, 42, 48, 51, 72, 78, 84, 90, 96, 102]
MAX_PART = 10485760


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_relative(path):
    p = PurePosixPath(path)
    need(isinstance(path, str) and '\\' not in path and ':' not in path,
         'portable relative path')
    need(not p.is_absolute() and all(x not in ('', '.', '..') for x in path.split('/')),
         'relative path with no traversal')
    return p


def check_record(record, get_part, raw):
    """Compare decompressed chunks directly with a separately opened raw stream."""
    safe_relative(record['raw_original_path'])
    total = hashlib.sha256()
    offset = 0
    compressed = 0
    seen = set()
    need(record['parts'], 'nonempty prescribed parts')
    for index, part in enumerate(record['parts']):
        relative = str(safe_relative(part['relative_path']))
        need(relative not in seen, 'unique part path')
        seen.add(relative)
        need(part['index'] == index and part['raw_offset'] == offset,
             'contiguous ordered raw chunks')
        packed = get_part(relative)
        need(0 < len(packed) < MAX_PART and len(packed) == part['gzip_bytes'],
             'strict public part size')
        need(sha(packed) == part['gzip_sha256'], 'compressed identity')
        # Fresh implementation uses complete per-part decompression, unlike the
        # producer's streaming compression/recovery. Python gzip/zlib is shared.
        chunk = gzip.decompress(packed)
        need(len(chunk) == part['raw_bytes'] and sha(chunk) == part['raw_sha256'],
             'decompressed chunk identity')
        need(raw.read(len(chunk)) == chunk, 'literal original/recovered bytes')
        total.update(chunk)
        offset += len(chunk)
        compressed += len(packed)
    need(raw.read(1) == b'', 'original has no unaccounted suffix')
    need(offset == record['raw_bytes'] and total.hexdigest() == record['raw_sha256'],
         'complete recovered proof identity')
    return dict(raw_bytes=offset, gzip_bytes=compressed, parts=len(seen),
                recovered_sha256=total.hexdigest(), literal_byte_comparison=True)


def controls():
    chunks = [b'1 0\n-1 0\n', b'0\n']
    packed = {f'control/part{i}.gz': gzip.compress(c, mtime=0) for i, c in enumerate(chunks)}
    raw = b''.join(chunks)
    rec = dict(raw_original_path='control/proof.drat', raw_bytes=len(raw), raw_sha256=sha(raw), parts=[])
    offset = 0
    for i, c in enumerate(chunks):
        p = f'control/part{i}.gz'
        rec['parts'].append(dict(index=i, relative_path=p, raw_offset=offset,
            raw_bytes=len(c), raw_sha256=sha(c), gzip_bytes=len(packed[p]), gzip_sha256=sha(packed[p])))
        offset += len(c)
    check_record(rec, packed.__getitem__, io.BytesIO(raw))
    bad = []
    names = ['changed_part', 'changed_compressed_hash', 'changed_chunk_hash',
             'changed_whole_hash', 'reordered_parts', 'dropped_part',
             'wrong_offset', 'path_traversal', 'changed_original', 'extra_original_suffix']
    for name in names:
        r = deepcopy(rec)
        ps = dict(packed)
        original = raw
        if name == 'changed_part':
            b = ps['control/part0.gz']; ps['control/part0.gz'] = b[:-1] + bytes([b[-1] ^ 1])
        elif name == 'changed_compressed_hash': r['parts'][0]['gzip_sha256'] = '0' * 64
        elif name == 'changed_chunk_hash': r['parts'][0]['raw_sha256'] = '0' * 64
        elif name == 'changed_whole_hash': r['raw_sha256'] = '0' * 64
        elif name == 'reordered_parts': r['parts'].reverse()
        elif name == 'dropped_part': r['parts'].pop()
        elif name == 'wrong_offset': r['parts'][1]['raw_offset'] += 1
        elif name == 'path_traversal': r['parts'][0]['relative_path'] = '../outside.gz'
        elif name == 'changed_original': original = bytes([raw[0] ^ 1]) + raw[1:]
        elif name == 'extra_original_suffix': original += b'0\n'
        try:
            check_record(r, ps.__getitem__, io.BytesIO(original))
        except (ValueError, OSError, EOFError):
            bad.append(name)
        else:
            raise ValueError('accepted negative control: ' + name)
    return dict(positive='Exact two independently compressed chunks, both and whole byte identity.',
                mathematical_validity_of_control_trace_not_asserted=True, rejected_corruptions=bad)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def run(out):
    inputs = {}
    def pin(path, expected=None):
        safe_relative(path)
        h = file_sha(ROOT / path)
        if expected is not None:
            need(h == expected, 'input identity: ' + path)
        inputs[path] = h
        return h
    pin(MANIFEST, MANIFEST_HASH)
    pin(GATE, GATE_HASH)
    manifest = json.loads((ROOT / MANIFEST).read_bytes())
    gate = json.loads((ROOT / GATE).read_bytes())
    need(manifest['schema'] == 'FOUR_PROFILE_RAW_DRAT_GZIP_PARTS_V1', 'package schema')
    need(gate['status'] == 'INDEPENDENT_FIXED_HADAMARD_FIFTEEN_PROFILE_UNSAT_PASS', 'independent proof gate')
    need([r['case'] for r in manifest['records']] == CASES, 'exact ordered package cases')
    proofs = {r['case']: r for r in gate['case_records']}
    need(set(proofs) == set(CASES) and len(gate['case_records']) == 15, 'exact independently replayed population')
    need(manifest['strict_maximum_part_bytes'] == MAX_PART, 'part bound')
    for path, expected in manifest['inputs_sha256'].items():
        pin(path, expected)
    calibration = controls()
    save(out / 'controls.json', calibration)
    checked = []
    for rec in manifest['records']:
        proof = proofs[rec['case']]
        need(proof['proof']['complete_independent_replay'] is True and
             proof['replay']['accepted'] is True and proof['replay']['actual_exit_code'] == 0,
             'previous complete DRAT replay bound')
        need((rec['raw_original_path'], rec['raw_sha256'], rec['raw_bytes']) ==
             (proof['proof']['path'], proof['proof']['sha256'], proof['proof']['bytes']),
             'exact independently replayed raw proof')
        need(rec['cnf_sha256'] == proof['cnf_sha256'], 'proof CNF identity')
        need(rec['case_summary_path'] == proof['run_summary_path'] and
             rec['case_summary_sha256'] == proof['run_summary_sha256'], 'native summary identity')
        pin(proof['cnf_path'], proof['cnf_sha256'])
        pin(rec['raw_original_path'], rec['raw_sha256'])
        for part in rec['parts']:
            pin(PACKAGE + '/' + part['relative_path'], part['gzip_sha256'])
        with (ROOT / rec['raw_original_path']).open('rb') as original:
            result = check_record(rec, lambda p: (ROOT / PACKAGE / p).read_bytes(), original)
        checked.append(dict(case=rec['case'], raw_path=rec['raw_original_path'],
                            raw_sha256=rec['raw_sha256'], cnf_sha256=rec['cnf_sha256'], **result))
    totals = dict(proofs=len(checked), raw_bytes=sum(r['raw_bytes'] for r in checked),
                  gzip_bytes=sum(r['gzip_bytes'] for r in checked), parts=sum(r['parts'] for r in checked))
    need(totals == dict(proofs=15, raw_bytes=149571922, gzip_bytes=27706059, parts=25), 'exact totals')
    need(totals == dict(proofs=manifest['proofs'], raw_bytes=manifest['total_raw_bytes'],
                       gzip_bytes=manifest['total_gzip_bytes'], parts=manifest['parts']), 'declared totals')
    save(out / 'records.json', checked)
    for p in [Path(__file__).resolve().relative_to(ROOT).as_posix(),
              'docs/AUDIT_20260930_FOUR_PROFILE_PROOF_TRANSPORT.md', 'uv.lock', 'pyproject.toml']:
        pin(p)
    report = dict(status='INDEPENDENT_FIFTEEN_PROFILE_PROOF_TRANSPORT_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
        zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION, inputs_sha256=inputs,
        outputs_sha256={p.name:file_sha(p) for p in sorted(out.glob('*.json'))},
        counts=totals, controls=calibration,
        scope='Complete byte identity of every packaged chunk and all fifteen complete proof artifacts already independently replayed; no new proof replay or broader mathematical exclusion.',
        reconstruction='For each record, independently gzip-decompress parts in increasing index, concatenate the raw bytes; verify each chunk offset/size/hash and final raw size/hash. Paths are relative to the package directory. Existing originals were compared read-only.',
        checking_path='Independently authored per-part complete gzip decompression and literal comparison; no packager, recovery, solver or DRAT checker imports.',
        trusted_components=['Python standard library gzip/zlib and SHA256', 'Pinned prior complete DRAT replay gate for proof validity'],
        limitations=['Transport verification does not re-establish CNF semantic coverage or DRAT validity.', 'No publication action performed; current artifacts LOCAL_ONLY until repository publication.'],
        recovery_writes=0, native_calls=0, proof_replays=0, artifact_availability='LOCAL_ONLY')
    save(out / 'summary.json', report)
    print(json.dumps(dict(status=report['status'], summary_sha256=file_sha(out / 'summary.json'))))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    try:
        run(args.out.resolve())
    except Exception as error:
        save(args.out / 'failure.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
            error=repr(error), traceback=traceback.format_exc(), source_sha256=file_sha(Path(__file__))))
        raise
