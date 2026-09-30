"""Recover exact raw DRAT bytes from the 54-profile package; no proof approval."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re

SCHEMA = 'FIFTYFOUR_PROFILE_RAW_DRAT_GZIP_PARTS_V1'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def recover_record(record, base, destination=None):
    total = hashlib.sha256()
    offset = 0
    writer = None
    if destination is not None:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        writer = destination.open('xb')
    try:
        for index, part in enumerate(record['parts']):
            path = (base / part['relative_path']).resolve()
            need(path.is_relative_to(base.resolve()), 'part stays inside package')
            need(part['index'] == index and part['raw_offset'] == offset, 'contiguous ordered chunks')
            need(path.stat().st_size == part['gzip_bytes'] and sha(path) == part['gzip_sha256'], 'compressed identity')
            digest = hashlib.sha256()
            size = 0
            with gzip.open(path, 'rb') as stream:
                for block in iter(lambda: stream.read(1048576), b''):
                    total.update(block)
                    digest.update(block)
                    size += len(block)
                    if writer:
                        writer.write(block)
            need(size == part['raw_bytes'] and digest.hexdigest() == part['raw_sha256'], 'chunk raw identity')
            offset += size
        need(offset == record['raw_bytes'] and total.hexdigest() == record['raw_sha256'], 'whole raw identity')
        return dict(profile_id=record['profile_id'], raw_bytes=offset, raw_sha256=total.hexdigest(),
                    parts=len(record['parts']), identity_pass=True, proof_validity_checked=False)
    finally:
        if writer:
            writer.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only', action='store_true')
    mode.add_argument('--out', type=Path)
    parser.add_argument('--profile-id')
    args = parser.parse_args()
    need(sha(args.manifest) == args.manifest_sha256, 'manifest identity')
    manifest = json.loads(args.manifest.read_bytes())
    need(manifest['schema'] == SCHEMA, 'schema')
    records = manifest['records']
    ids = [record['profile_id'] for record in records]
    need(len(ids) == len(set(ids)) == 54, '54 unique profiles')
    need(all(re.fullmatch(r'rank4_\d+_profile_\d+', pid) for pid in ids), 'safe profile identifiers')
    if args.profile_id is not None:
        records = [record for record in records if record['profile_id'] == args.profile_id]
        need(len(records) == 1, 'selected profile occurs once')
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
    results = [recover_record(record, args.manifest.parent, None if args.verify_only else
               args.out / record['profile_id'] / 'proof.drat') for record in records]
    print(json.dumps(dict(status='RAW_PROOF_RECOVERY_IDENTITY_PASS', proofs=len(results),
                         raw_bytes=sum(r['raw_bytes'] for r in results), results=results,
                         proof_validity_checked=False)))

if __name__ == '__main__':
    main()
