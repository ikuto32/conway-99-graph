"""Recover saved UNKNOWN host-trace bytes; this does not verify any proof."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

SCHEMA = 'DIRECT_CELL_UNKNOWN_HOST_TRACE_GZIP_PARTS_V1'
CHUNK = 8 * 1024**2
MAX_GZIP = 10 * 1024**2


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def recover_record(record, base, destination=None, original=None):
    base = Path(base).resolve()
    total = hashlib.sha256()
    offset = 0
    writer = Path(destination).open('xb') if destination is not None else None
    reference = Path(original).open('rb') if original is not None else None
    try:
        need(record['native_outcome'] == 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME', 'UNKNOWN transport scope')
        need(record['complete_unsat_proof'] is False, 'no complete proof claim')
        need(record['parts'], 'nonempty saved host trace')
        for index, part in enumerate(record['parts']):
            path = (base / part['relative_path']).resolve()
            need(path.is_relative_to(base), 'part stays inside package')
            need(part['index'] == index and part['raw_offset'] == offset, 'ordered contiguous parts')
            need(0 < part['raw_bytes'] <= CHUNK, 'bounded raw part')
            need(part['gzip_bytes'] <= MAX_GZIP, 'bounded gzip part')
            need(path.stat().st_size == part['gzip_bytes'] and sha(path) == part['gzip_sha256'], 'compressed identity')
            digest = hashlib.sha256()
            size = 0
            with gzip.open(path, 'rb') as stream:
                for block in iter(lambda: stream.read(1024**2), b''):
                    size += len(block)
                    need(size <= part['raw_bytes'], 'no excess decompressed bytes')
                    if reference is not None:
                        need(reference.read(len(block)) == block, 'literal recovered/original bytes')
                    if writer is not None:
                        writer.write(block)
                    digest.update(block)
                    total.update(block)
            need(size == part['raw_bytes'] and digest.hexdigest() == part['raw_sha256'], 'raw part identity')
            offset += size
        need(offset == record['raw_bytes'] and total.hexdigest() == record['raw_sha256'], 'whole saved host identity')
        if reference is not None:
            need(reference.read(1) == b'', 'original has no unmatched tail')
        return dict(variant=record['variant'], raw_bytes=offset, raw_sha256=total.hexdigest(),
                    parts=len(record['parts']), saved_host_transport_complete=True,
                    original_compared_literally=reference is not None,
                    native_outcome=record['native_outcome'], complete_unsat_proof=False,
                    proof_validity_checked=False)
    finally:
        if writer is not None:
            writer.close()
        if reference is not None:
            reference.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only', action='store_true')
    mode.add_argument('--out', type=Path)
    args = parser.parse_args()
    need(sha(args.manifest) == args.manifest_sha256, 'manifest identity')
    manifest = json.loads(args.manifest.read_bytes())
    need(manifest['schema'] == SCHEMA, 'transport schema')
    records = manifest['records']
    need([r['variant'] for r in records] == ['standalone', 'at_least_seven'], 'exact two saved traces')
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=False)
    results = [recover_record(record, args.manifest.parent,
               None if args.verify_only else args.out / (record['variant'] + '.saved_unknown_trace.drat'))
               for record in records]
    print(json.dumps(dict(status='SAVED_UNKNOWN_HOST_TRACE_RECOVERY_PASS', traces=2,
                         results=results, complete_unsat_proof=False, proof_validity_checked=False)))


if __name__ == '__main__':
    main()
