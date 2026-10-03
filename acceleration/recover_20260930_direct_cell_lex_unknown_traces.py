"""Restore only the two lex UNKNOWN host streams; no proof-validity inference."""
from pathlib import Path,PurePosixPath
import argparse
import hashlib
import json
import zlib

SCHEMA = 'DIRECT_CELL_LEX_UNKNOWN_HOST_TRACE_GZIP_PARTS_V1'
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
    destination=Path(destination) if destination is not None else None
    partial=destination.with_name(destination.name+'.partial') if destination is not None else None
    if destination is not None:need(not destination.exists(),'refuse overwriting recovered output')
    writer = partial.open('xb') if partial is not None else None
    reference = Path(original).open('rb') if original is not None else None
    seen=set()
    try:
        need(record['native_outcome'] == 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME', 'UNKNOWN transport scope')
        need(record['complete_unsat_proof'] is False, 'no complete proof claim')
        need(record['parts'], 'nonempty saved host trace')
        for index, part in enumerate(record['parts']):
            rel=PurePosixPath(part['relative_path']);need(not rel.is_absolute() and '..' not in rel.parts and '\\' not in str(rel),'safe package-relative POSIX path')
            need(str(rel)not in seen,'unique ordered package part');seen.add(str(rel))
            path = (base / str(rel)).resolve()
            need(path.is_relative_to(base), 'part stays inside package')
            need(part['index'] == index and part['raw_offset'] == offset, 'ordered contiguous parts')
            need(0 < part['raw_bytes'] <= CHUNK, 'bounded raw part')
            need(part['gzip_bytes'] <= MAX_GZIP, 'bounded gzip part')
            need(path.stat().st_size == part['gzip_bytes'] and sha(path) == part['gzip_sha256'], 'compressed identity')
            compressed=path.read_bytes();need(compressed[:4]==b'\x1f\x8b\x08\x00' and compressed[4:8]==b'\x00'*4,'deterministic unnamed mtime-zero gzip header')
            decoder=zlib.decompressobj(31);block=decoder.decompress(compressed,CHUNK+1)
            need(decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,'single complete gzip member with no trailing bytes')
            block+=decoder.flush();size=len(block)
            need(size==part['raw_bytes'] and hashlib.sha256(block).hexdigest()==part['raw_sha256'],'raw part identity')
            if reference is not None:need(reference.read(size)==block,'literal recovered/original bytes')
            if writer is not None:writer.write(block)
            total.update(block)
            offset += size
        need(offset == record['raw_bytes'] and total.hexdigest() == record['raw_sha256'], 'whole saved host identity')
        if reference is not None:
            need(reference.read(1) == b'', 'original has no unmatched tail')
        if writer is not None:
            writer.flush();writer.close();writer=None
            need(not destination.exists(),'refuse output replacement')
            partial.rename(destination)
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
    print(json.dumps(dict(status='SAVED_LEX_UNKNOWN_HOST_TRACE_RECOVERY_PASS', traces=2,
                         results=results, complete_unsat_proof=False, proof_validity_checked=False)))


if __name__ == '__main__':
    main()
