"""Reversible transport packaging of the 215 frozen native proof streams."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
import zlib
import recover_20260930_seven_profile_proofs as recovery

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / 'acceleration/results/20260930_hadamard_seven_profile_batch_native/summary.json'
CAMPAIGN_SHA = '02520b91d50c0f448fc966b61348da0215d520a5f2082767d09918632b0b0b46'
RAW_TOTAL = 577482170
CHUNK = 8 * 1024**2
MAX_GZIP = 10 * 1024**2
HISTORICAL = {
    'acceleration/package_20260930_six_profile_proofs.py': 'b61d2b849dd84763614b38cb48db505e09a09be88505a4c87407c3bda0159769',
    'acceleration/recover_20260930_six_profile_proofs.py': '295172756cfb3dd7d259216d737b4d6e88d9cbd56d7b6d808c0bc7e78c86ee2f',
    'acceleration/package_20260930_six_profile_proofs_spec.md': 'c46994f47ad03657e2997d65e27fc996999da81018a9ff27a4167516c0d1a783',
}

need, sha = recovery.need, recovery.sha

def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()

def read(path):
    return json.loads(Path(path).read_bytes())

def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def gzip_part(path, raw):
    with path.open('xb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, compresslevel=9, mtime=0) as zipped:
            zipped.write(raw)

def calibration(out):
    out.mkdir()
    raw = b'1 -2 0\nd 3 0\n0\n' * 17
    path = out / 'tiny.gz'
    gzip_part(path, raw)
    part = dict(index=0, relative_path='tiny.gz', raw_offset=0, raw_bytes=len(raw),
                raw_sha256=hashlib.sha256(raw).hexdigest(), gzip_bytes=path.stat().st_size,
                gzip_sha256=sha(path))
    record = dict(profile_id='synthetic_control', raw_bytes=len(raw), raw_sha256=part['raw_sha256'], parts=[part])
    recovery.recover_record(record, out)
    rejected = []
    for name in ('wrong_whole_hash', 'wrong_chunk_length', 'wrong_offset', 'wrong_compressed_hash', 'outside_package_path'):
        bad = copy.deepcopy(record)
        if name == 'wrong_whole_hash':
            bad['raw_sha256'] = '0' * 64
        elif name == 'wrong_chunk_length':
            bad['parts'][0]['raw_bytes'] += 1
        elif name == 'wrong_offset':
            bad['parts'][0]['raw_offset'] = 1
        elif name == 'outside_package_path':
            bad['parts'][0]['relative_path'] = '../tiny.gz'
        else:
            bad['parts'][0]['gzip_sha256'] = '0' * 64
        try:
            recovery.recover_record(bad, out)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('corrupted metadata accepted')
    corrupt = bytearray(path.read_bytes())
    corrupt[-8] ^= 1
    badpath = out / 'corrupt.gz'
    badpath.write_bytes(corrupt)
    bad = copy.deepcopy(record)
    bad['parts'][0]['relative_path'] = 'corrupt.gz'
    bad['parts'][0]['gzip_sha256'] = sha(badpath)
    try:
        recovery.recover_record(bad, out)
    except (ValueError, OSError, EOFError, zlib.error):
        rejected.append('corrupt_gzip_payload')
    else:
        raise ValueError('corrupt gzip accepted')
    save(out / 'summary.json', dict(status='PACKAGING_RECOVERY_CALIBRATION_PASS', tiny_positive_bytes=len(raw),
         rejected_controls=rejected, proof_validity_checked=False,
         inputs_sha256={key(Path(recovery.__file__)): sha(Path(recovery.__file__))}))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--proof-gate', type=Path, required=True)
    parser.add_argument('--proof-gate-sha256', required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        need(sha(CAMPAIGN) == CAMPAIGN_SHA, 'campaign identity')
        need(sha(args.proof_gate)==args.proof_gate_sha256,'actual independent proof gate')
        gate=read(args.proof_gate)
        need(gate['status']=='INDEPENDENT_FIXED_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_UNSAT_PASS' and gate['completed_proof_replays']==215 and gate['UNKNOWN']==0 and gate['SAT_pending_separate_review']==0 and not gate['unattempted_profiles'],'all215 separately replayed literal proofs')
        checked={r['profile_id']:r for r in gate['profile_records']}
        need(len(checked)==215 and gate['inputs_sha256'][key(CAMPAIGN)]==CAMPAIGN_SHA,'exact gate/campaign population')
        for path, digest in HISTORICAL.items():
            need(sha(ROOT / path) == digest, 'preserved historical source')
        campaign = read(CAMPAIGN)
        items = campaign['profile_records']
        ids = [item['profile_id'] for item in items]
        need(campaign['completed_attempts'] == 215 and not campaign['unattempted_profiles'], 'complete population')
        need(len(ids) == len(set(ids)) == 215 and ids == campaign['selected_profiles'], 'ordered 215 distinct profiles')
        need(all(re.fullmatch(r'rank5_\d+_profile_\d+', pid) for pid in ids), 'safe profile IDs')
        calibration(out / 'controls')
        records = []
        inputs = {key(CAMPAIGN): CAMPAIGN_SHA, key(args.proof_gate):args.proof_gate_sha256, **HISTORICAL}
        for item in items:
            summarypath = ROOT / item['summary_path']
            need(sha(summarypath) == item['summary_sha256'], 'profile summary identity')
            case = read(summarypath)
            proof = case['proof_copy']
            path = summarypath.parent / 'main/proof.drat'
            need(case['profile_id'] == item['profile_id'], 'literal profile identity')
            witness=checked[item['profile_id']]
            need(witness['outcome']=='UNSAT_VERIFIED' and witness['trace']['path']==key(path) and witness['trace']['sha256']==proof['sha256'] and witness['trace']['bytes']==proof['bytes'] and witness['cnf_sha256']==case['cnf_sha256'],'same exact independently reviewed proof')
            need(case['native_receipt']['actual_exit_code'] == 20 and not case['native_receipt']['outer_windows_guard_expired'], 'saved native UNSAT outcome; no proof approval')
            need(sha(path) == proof['sha256'] and path.stat().st_size == proof['bytes'], 'raw transfer identity')
            inputs[key(summarypath)] = item['summary_sha256']
            inputs[key(path)] = proof['sha256']
            folder = out / item['profile_id']
            folder.mkdir()
            parts, offset, total = [], 0, hashlib.sha256()
            with path.open('rb') as stream:
                for index, data in enumerate(iter(lambda: stream.read(CHUNK), b'')):
                    target = folder / f'proof.part{index:04d}.drat.gz'
                    gzip_part(target, data)
                    need(target.stat().st_size < MAX_GZIP, 'strict sub10MiB payload')
                    parts.append(dict(index=index, relative_path=target.relative_to(out).as_posix(), raw_offset=offset,
                         raw_bytes=len(data), raw_sha256=hashlib.sha256(data).hexdigest(),
                         gzip_bytes=target.stat().st_size, gzip_sha256=sha(target)))
                    offset += len(data)
                    total.update(data)
            need(offset == proof['bytes'] and total.hexdigest() == proof['sha256'], 'raw unchanged during compression')
            record = dict(profile_id=item['profile_id'], raw_original_path=key(path), raw_sha256=proof['sha256'],
                 raw_bytes=proof['bytes'], preserved_ext4_original=proof['linux_source'],
                 profile_summary_path=item['summary_path'], profile_summary_sha256=item['summary_sha256'],
                 cnf_sha256=case['cnf_sha256'], parts=parts, proof_validity_checked_by_packager=False)
            recovered = recovery.recover_record(record, out)
            need(sha(path) == proof['sha256'], 'original retained unchanged')
            records.append(record)
            save(folder / 'recovery_identity.json', recovered)
            print(json.dumps(dict(profile_id=item['profile_id'], raw_bytes=offset,
                                 gzip_bytes=sum(p['gzip_bytes'] for p in parts), parts=len(parts))), flush=True)
        totalraw = sum(record['raw_bytes'] for record in records)
        need(totalraw == RAW_TOTAL, 'frozen total raw bytes')
        for path in (Path(__file__), Path(__file__).with_name('package_20260930_seven_profile_proofs_spec.md'),
                     Path(recovery.__file__), ROOT / 'uv.lock', ROOT / 'pyproject.toml'):
            inputs[key(path)] = sha(path)
        manifest = dict(schema=recovery.SCHEMA, created=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            zlib_compile_version=zlib.ZLIB_VERSION, zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION,
            inputs_sha256=inputs, raw_chunk_bytes=CHUNK, gzip_parameters=dict(compresslevel=9, mtime=0, filename=''),
            strict_maximum_part_bytes=MAX_GZIP, records=records, proofs=len(records), total_raw_bytes=totalraw,
            total_gzip_bytes=sum(p['gzip_bytes'] for r in records for p in r['parts']),
            parts=sum(len(r['parts']) for r in records), proof_validity_checked=False, originals_preserved=True,
            ext4_originals_not_modified_by_packager=True, artifact_availability='LOCAL_ONLY',
            availability_reason='Prepared public payload; publication not yet confirmed.',
            recovery_command='uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_seven_profile_proofs.py --manifest PATH --manifest-sha256 SHA --verify-only')
        save(out / 'package_manifest.json', manifest)
        summary = dict(status='TWOHUNDREDFIFTEEN_RAW_PROOFS_LOSSLESSLY_PACKAGED', package_manifest_path=key(out / 'package_manifest.json'),
            package_manifest_sha256=sha(out / 'package_manifest.json'), proofs=len(records), total_raw_bytes=totalraw,
            total_gzip_bytes=manifest['total_gzip_bytes'], gzip_parts=manifest['parts'],
            largest_gzip_part_bytes=max(p['gzip_bytes'] for r in records for p in r['parts']),
            all_raw_streams_recovered_and_rehashed=True, originals_preserved=True, proof_validity_checked=False,
            elapsed_seconds=time.monotonic()-start, artifact_availability='LOCAL_ONLY', inputs_sha256=inputs)
        save(out / 'summary.json', summary)
        print(json.dumps({k: v for k, v in summary.items() if k != 'inputs_sha256'}))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), source_sha256=sha(Path(__file__)), originals_not_deleted=True))
        raise

if __name__ == '__main__':
    main()
