"""Root-owned exact allowlist staging and raw Git-index byte identity checking.

Metadata only. Does not approve mathematics, alter artifacts or promote availability.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def identities(path):
    size = path.stat().st_size
    sha = hashlib.sha256()
    git = hashlib.sha1(('blob ' + str(size) + '\0').encode('ascii'))
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(chunk); git.update(chunk)
    return size, sha.hexdigest(), git.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--ledger-sha256', required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact2100-member metadata staging and raw Gitblob comparison; no mathematical computation or new availability')
    out = args.out.resolve(); need(out.is_relative_to(ROOT), 'bounded result'); out.mkdir(parents=True, exist_ok=False)
    manifest_path = args.manifest.resolve(); need(manifest_path.is_relative_to(ROOT), 'bounded allowlist')
    need(identities(manifest_path)[1] == args.manifest_sha256, 'exact independently prepared allowlist')
    manifest = json.loads(manifest_path.read_bytes())
    need(manifest['schema'] == 'WAVE36_INCREMENTAL_EXACT_EVIDENCE_ALLOWLIST_V2' and manifest['current_claims'] == 337 and manifest['ledger_sha256'] == args.ledger_sha256 and manifest['index_mutated'] is False, 'frozen metadata scope')
    need(identities(ROOT / 'CLAIMS.yaml')[1] == args.ledger_sha256, 'live337ledger unchanged')
    records = manifest['records']; names = [row['path'] for row in records]
    need(len(names) == len(set(names)) == manifest['direct_record_count'], 'unique exact direct population')
    stage_names = sorted(set(names) | set(manifest['self_metadata_paths']))
    nul_path = manifest_path.parent / 'stage_paths.nul'
    need(identities(nul_path)[1] == manifest['stage_paths_sha256'] and nul_path.read_bytes() == b''.join(name.encode('utf8') + b'\0' for name in stage_names), 'complete authenticated exact stage path list')
    expected = {}
    for row in records:
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20, 'not completed within the allocated budget')
        path = (ROOT / row['path']).resolve(); need(path.is_relative_to(ROOT), 'bounded raw member')
        size, identity, blob = identities(path)
        need((size, identity) == (row['bytes'], row['sha256']), 'exact allowlisted raw bytes ' + row['path'])
        expected[row['path']] = blob
    for name in manifest['self_metadata_paths']:
        expected[name] = identities(ROOT / name)[2]
    source_name = Path(__file__).relative_to(ROOT).as_posix()
    expected[source_name] = identities(Path(__file__))[2]
    stage_names = sorted(set(stage_names) | {source_name})
    exact_nul = out / 'root_stage_paths.nul'
    exact_nul.write_bytes(b''.join(name.encode('utf8') + b'\0' for name in stage_names))
    subprocess.run(['git', 'add', '-f', '--pathspec-from-file=' + str(exact_nul), '--pathspec-file-nul'], cwd=ROOT, check=True, timeout=max(1, deadline.status()['remaining_seconds'] - 15), capture_output=True)
    index = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT, timeout=max(1, deadline.status()['remaining_seconds'] - 10))
    blobs = {}
    for entry in index.split(b'\0'):
        if not entry:
            continue
        metadata, path = entry.split(b'\t', 1)
        mode, blob, stage = metadata.decode('ascii').split()
        if stage == '0':
            blobs[path.decode('utf8')] = blob
    failures = [dict(path=name, expected_raw_git_blob=blob, index_blob=blobs.get(name)) for name, blob in expected.items() if blobs.get(name) != blob]
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), status='WAVE36_EXACT_INDEX_RAW_BYTE_IDENTITY_PASS' if not failures else 'WAVE36_INDEX_RAW_BYTE_IDENTITY_VETO', source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), source_sha256=identities(Path(__file__))[1], command=[sys.executable, *sys.argv], cwd=str(ROOT), allowlist_manifest_sha256=args.manifest_sha256, ledger_sha256=args.ledger_sha256, direct_records=len(records), indexed_paths_checked=len(expected), raw_bytes_checked=sum(row['bytes'] for row in records), failures=failures, index_mutated=True, artifacts_changed=False, mathematical_replay=False, availability_changed=False, deadline=deadline.status())
    (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    need(not failures, 'Git-index normalization changed raw evidence; preserve failure and correct only exact attributes before new check')
    need(identities(ROOT / 'CLAIMS.yaml')[1] == args.ledger_sha256, 'ledger unchanged through staging')
    print(json.dumps({key: report[key] for key in ('status', 'direct_records', 'indexed_paths_checked', 'raw_bytes_checked')}))


if __name__ == '__main__':
    main()
