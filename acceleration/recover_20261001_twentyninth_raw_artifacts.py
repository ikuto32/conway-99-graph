"""Restore hash-bound raw research artifacts without overwriting existing files."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse, gzip, hashlib, json, os, platform, subprocess, sys, uuid
from tqdm import tqdm
ROOT = Path(__file__).resolve().parents[1]
def need(ok, message):
    if not ok:
        raise ValueError(message)
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def identity(path, digest, length=None):
    need(path.is_file() and sha(path) == digest, 'exact file identity: ' + str(path))
    if length is not None:
        need(path.stat().st_size == length, 'exact file length: ' + str(path))
def contained(base, relative):
    path = Path(relative)
    need(not path.is_absolute() and '..' not in path.parts, 'safe relative path')
    result = (base / path).resolve()
    need(result.is_relative_to(base.resolve()), 'path inside declared tree')
    return result
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--destination-dir', type=Path, default=ROOT)
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    identity(manifest_path, args.manifest_sha256)
    need(manifest_path.is_relative_to(ROOT), 'manifest inside repository')
    need(not args.receipt.exists(), 'fresh receipt path')
    manifest = json.loads(manifest_path.read_bytes())
    records = [dict(record, raw_path=record.get('raw_path', record.get('path')), raw_sha256=record.get('raw_sha256', record.get('sha256')), raw_bytes=record.get('raw_bytes', record.get('bytes'))) for record in manifest['records']]
    declared = manifest['record_count'] if 'record_count' in manifest else manifest['raw_artifacts']
    need(declared == len(records) == len({r['raw_path'] for r in records}), 'complete distinct raw inventory')
    inputs = {manifest_path.relative_to(ROOT).as_posix(): args.manifest_sha256}
    destination = args.destination_dir.resolve()
    results = []
    for record in tqdm(records, desc='Restore wave29 raw identities', mininterval=1):
        target = contained(destination, record['raw_path'])
        if target.exists():
            identity(target, record['raw_sha256'], record['raw_bytes'])
        action = 'VERIFIED_EXISTING' if target.exists() else 'VERIFIED_STREAM_ONLY'
        temporary = None
        writer = None
        if not target.exists() and not args.verify_only:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.recovering-' + uuid.uuid4().hex)
            writer = temporary.open('xb')
            action = 'RESTORED_MISSING'
        whole = hashlib.sha256()
        total = 0
        seen = set()
        need(record['parts'], 'nonempty compressed part list')
        try:
            for part in record['parts']:
                need(part['path'] not in seen and part['raw_offset'] == total, 'unique contiguous parts')
                seen.add(part['path'])
                path = contained(ROOT, part['path'])
                identity(path, part['gzip_sha256'], part['gzip_bytes'])
                inputs[part['path']] = part['gzip_sha256']
                chunk = hashlib.sha256()
                size = 0
                with gzip.open(path, 'rb') as stream:
                    for block in iter(lambda: stream.read(1048576), b''):
                        size += len(block)
                        need(size <= part['raw_bytes'], 'bounded decompressed size')
                        chunk.update(block)
                        whole.update(block)
                        if writer:
                            writer.write(block)
                need(size == part['raw_bytes'] and chunk.hexdigest() == part['raw_sha256'], 'complete raw chunk identity')
                total += size
            need(total == record['raw_bytes'] and whole.hexdigest() == record['raw_sha256'], 'complete original identity')
        finally:
            if writer:
                writer.close()
        if temporary is not None:
            identity(temporary, record['raw_sha256'], record['raw_bytes'])
            need(not target.exists(), 'never replace existing destination')
            os.rename(temporary, target)
            identity(target, record['raw_sha256'], record['raw_bytes'])
        result = {field: record[field] for field in ['raw_path', 'raw_sha256', 'raw_bytes']}
        result.update(kind=record.get('kind'), kind_null_reason=None if 'kind' in record else 'No kind label in authoritative manifest.', case=record.get('case'), case_null_reason=None if 'case' in record else 'No case label in authoritative manifest.', action=action)
        results.append(result)
    receipt = dict(status='TWENTYNINTH_RAW_ARTIFACT_RECOVERY_PASS', timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), source_sha256=sha(Path(__file__)), inputs_sha256=inputs, destination=str(destination), verify_only=args.verify_only, originals=len(records), raw_bytes=sum(r['raw_bytes'] for r in records), action_counts=dict(Counter(r['action'] for r in results)), records=results, mathematical_verification=False)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: receipt[key] for key in ['status', 'originals', 'raw_bytes', 'action_counts']}))
if __name__ == '__main__':
    main()
