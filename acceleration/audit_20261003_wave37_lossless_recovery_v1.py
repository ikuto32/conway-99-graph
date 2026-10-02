"""Independent bounded fresh restoration of the two frozen Wave37 raw records.

No package-producer imports. Complete byte identities, not model semantics.
"""
import argparse
import copy
import gzip
import hashlib
import json
import platform
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'acceleration/results/20261003_wave37_rooted8_package01/manifest.json'
MANIFEST_SHA = 'ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14'
PACKAGER = 'acceleration/package_20261003_wave37_rooted8_v1.py'
PACKAGER_SHA = 'c7e36d38a1f723eb31b194fceab925e4c3f93ad45cb419ba6896a765b710ae2e'
AUDIT = 'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/summary.json'
AUDIT_SHA = 'ec5073a22027c512e29dac1d49048a507f272cb8ce1a0a79d2ca1f663f1be974'
POPULATION = {
    'acceleration/results/20261003_rooted8_unrestricted_extension01/model.json':
        ('b143c129fce1f450b54a397d6d508ecb81a67870c2bafd2e9f50dee0bda83f1a', 59358049),
    'acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/reconstructed_rows.json':
        ('033778d196dcf7d21f76b2460018944b291c1b34b38602ce9f66c24e198dbd70', 65506677),
}
SOFTWARE = {
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'acceleration/native_budget_env_v1/pyproject.toml': '96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782',
    'acceleration/native_budget_env_v1/uv.lock': '54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434',
}
BLOCK = 1024 * 1024
MAX_CHUNK = 8 * 1024 * 1024


class CheckError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(f'{stage}: {message}')


def require(ok, stage, message):
    if not ok:
        raise CheckError(stage, message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'JSON_DUPLICATE', key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding='utf8'), object_pairs_hook=unique_object)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def path_under(base, name):
    require(type(name) is str and name and '\\' not in name, 'PATH', 'relative POSIX path required')
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and '..' not in relative.parts and ':' not in name,
            'PATH', 'unsafe relative member')
    target = (base / name).resolve()
    require(target.is_relative_to(base.resolve()), 'PATH', 'resolved path escapes base')
    return target


def nonnegative(value):
    return type(value) is int and value >= 0


def shape(manifest, base):
    require(manifest.get('schema') == 'WAVE33_LITERAL_MODELS_LOSSLESS_V1', 'SHAPE', 'schema')
    records = manifest.get('records')
    require(type(records) is list and bool(records), 'SHAPE', 'records')
    raw_names, part_names = set(), set()
    raw_total = gzip_total = parts_total = 0
    for record in records:
        name = record['raw_path']; path_under(base, name)
        require(name not in raw_names, 'DUP_RAW', name); raw_names.add(name)
        require(nonnegative(record['raw_bytes']), 'SHAPE', 'raw length')
        require(type(record['parts']) is list and bool(record['parts']), 'SHAPE', 'parts')
        offset = 0
        for part in record['parts']:
            name = part['path']; path_under(base, name)
            require(name not in part_names, 'DUP_PART', name); part_names.add(name)
            require(nonnegative(part['raw_offset']) and part['raw_offset'] == offset, 'OFFSET', name)
            require(type(part['raw_bytes']) is int and 0 < part['raw_bytes'] <= MAX_CHUNK,
                    'SHAPE', 'bounded part length')
            require(type(part['gzip_bytes']) is int and part['gzip_bytes'] > 0,
                    'SHAPE', 'gzip length')
            offset += part['raw_bytes']; gzip_total += part['gzip_bytes']; parts_total += 1
        require(offset == record['raw_bytes'], 'SHAPE', 'complete part lengths')
        raw_total += record['raw_bytes']
    require((manifest.get('record_count'), manifest.get('raw_bytes'), manifest.get('gzip_parts'),
             manifest.get('gzip_bytes')) == (len(records), raw_total, parts_total, gzip_total),
            'SHAPE', 'aggregate population')
    return records


def literal_compare(left, right, tick):
    offset = 0
    with left.open('rb') as a, right.open('rb') as b:
        while True:
            tick(); aa, bb = a.read(BLOCK), b.read(BLOCK)
            require(aa == bb, 'ORIGINAL_BYTES', f'literal mismatch at block offset {offset}')
            if not aa:
                return offset
            offset += len(aa)


def restore(manifest, base, destination, tick, originals=True):
    records = shape(manifest, base)
    require(not destination.exists(), 'DESTINATION', 'fresh destination required')
    destination.mkdir(parents=True)
    receipts = []
    for record in records:
        tick(); original = path_under(base, record['raw_path'])
        if originals:
            require(original.stat().st_size == record['raw_bytes'] and sha(original) == record['raw_sha256'],
                    'ORIGINAL_HASH', 'source identity')
        target = path_under(destination, record['raw_path']); target.parent.mkdir(parents=True, exist_ok=True)
        whole = hashlib.sha256(); total = 0; part_receipts = []
        with target.open('xb') as output:
            for part in record['parts']:
                tick(); compressed = path_under(base, part['path'])
                require(compressed.stat().st_size == part['gzip_bytes'], 'GZIP_LENGTH', part['path'])
                require(sha(compressed) == part['gzip_sha256'], 'GZIP_HASH', part['path'])
                digest = hashlib.sha256(); length = 0
                try:
                    with gzip.GzipFile(filename=str(compressed), mode='rb') as stream:
                        while True:
                            tick(); block = stream.read(min(BLOCK, part['raw_bytes'] - length + 1))
                            if not block:
                                break
                            length += len(block)
                            require(length <= part['raw_bytes'], 'PART_LENGTH', 'decompression exceeds bound')
                            output.write(block); digest.update(block); whole.update(block); total += len(block)
                except (gzip.BadGzipFile, EOFError, OSError, zlib.error) as error:
                    raise CheckError('GZIP_STREAM', type(error).__name__) from error
                require(length == part['raw_bytes'], 'PART_LENGTH', 'short decompression')
                require(digest.hexdigest() == part['raw_sha256'], 'PART_HASH', part['path'])
                part_receipts.append(dict(path=part['path'], raw_bytes=length, raw_sha256=digest.hexdigest()))
        require(total == record['raw_bytes'] and whole.hexdigest() == record['raw_sha256'],
                'WHOLE_HASH', record['raw_path'])
        require(sha(target) == record['raw_sha256'], 'RESTORED_HASH', record['raw_path'])
        compared = literal_compare(original, target, tick) if originals else None
        receipts.append(dict(raw_path=record['raw_path'], recovered_path=target.relative_to(ROOT).as_posix(),
                             raw_bytes=total, raw_sha256=whole.hexdigest(), literal_bytes_compared=compared,
                             parts=part_receipts))
    return receipts


def controls(out, tick):
    base = out / 'fixture'; base.mkdir()
    data = [b'known-positive\x00\xff\n' * 19, bytes(range(256)) * 3]
    records = []
    for index, raw in enumerate(data):
        name = f'raw_{index}.bin'; (base / name).write_bytes(raw); parts = []
        offset = 0
        for number, block in enumerate([raw[:13], raw[13:]]):
            part_name = f'part_{index}_{number}.gz'
            compressed = gzip.compress(block, compresslevel=1, mtime=0); (base / part_name).write_bytes(compressed)
            parts.append(dict(path=part_name, gzip_bytes=len(compressed), gzip_sha256=sha(base / part_name),
                              raw_offset=offset, raw_bytes=len(block), raw_sha256=hashlib.sha256(block).hexdigest()))
            offset += len(block)
        records.append(dict(raw_path=name, raw_bytes=len(raw), raw_sha256=sha(base / name), parts=parts))
    manifest = dict(schema='WAVE33_LITERAL_MODELS_LOSSLESS_V1', record_count=2, raw_bytes=sum(map(len, data)),
                    gzip_parts=4, gzip_bytes=sum(p['gzip_bytes'] for r in records for p in r['parts']), records=records)
    save(base / 'manifest.json', manifest)
    positives = restore(manifest, base, out / 'positive_recovered', tick)
    checks = []
    def negative(label, stage, invoke):
        try:
            invoke()
        except CheckError as error:
            require(error.stage == stage, 'CALIBRATION', f'{label}: expected {stage}, got {error.stage}')
            checks.append(dict(label=label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
        else:
            raise CheckError('CALIBRATION', f'{label}: accepted corruption')
    def mutated(label, stage, change, originals=True):
        value = copy.deepcopy(manifest); change(value)
        save(base / f'{label}.json', value)
        negative(label, stage, lambda: restore(value, base, out / f'negative_{label}', tick, originals=originals))
    mutated('offset', 'OFFSET', lambda m: m['records'][0]['parts'][1].update(raw_offset=1))
    mutated('part_hash', 'PART_HASH', lambda m: m['records'][0]['parts'][0].update(raw_sha256='0' * 64))
    mutated('whole_hash', 'WHOLE_HASH', lambda m: m['records'][0].update(raw_sha256='0' * 64), originals=False)
    mutated('original_hash', 'ORIGINAL_HASH', lambda m: m['records'][0].update(raw_sha256='0' * 64))
    mutated('traversal', 'PATH', lambda m: m['records'][0].update(raw_path='../escape.bin'))
    mutated('duplicate_part', 'DUP_PART', lambda m: m['records'][1]['parts'][0].update(path=m['records'][0]['parts'][0]['path']))
    mutated('duplicate_raw', 'DUP_RAW', lambda m: m['records'][1].update(raw_path=m['records'][0]['raw_path']))
    mutated('gzip_hash', 'GZIP_HASH', lambda m: m['records'][0]['parts'][0].update(gzip_sha256='0' * 64))
    def bad_length(m):
        m['records'][0]['parts'][0]['raw_bytes'] -= 1
        m['records'][0]['parts'][1]['raw_offset'] -= 1
        m['records'][0]['raw_bytes'] -= 1; m['raw_bytes'] -= 1
    mutated('part_length', 'PART_LENGTH', bad_length, originals=False)
    corrupted = base / 'bad_stream.gz'; corrupted.write_bytes(b'not-a-gzip-stream')
    def bad_stream(m):
        part = m['records'][0]['parts'][0]
        m['gzip_bytes'] += corrupted.stat().st_size - part['gzip_bytes']
        part.update(path=corrupted.name, gzip_bytes=corrupted.stat().st_size, gzip_sha256=sha(corrupted))
    mutated('bad_stream', 'GZIP_STREAM', bad_stream)
    changed = base / 'changed_original.bin'; changed.write_bytes(bytes([data[0][0] ^ 1]) + data[0][1:])
    negative('literal_original', 'ORIGINAL_BYTES', lambda: literal_compare(changed, base / 'raw_0.bin', tick))
    negative('destination_exists', 'DESTINATION', lambda: restore(manifest, base, out / 'positive_recovered', tick))
    save(out / 'summary.json', dict(schema='INDEPENDENT_WAVE37_LOSSLESS_RECOVERY_CONTROLS_V1', status='PASS',
                                  positive_records=len(positives), negatives=checks, negative_count=len(checks)))
    return positives, checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--source-commit', required=True)
    args = ap.parse_args(); out = args.out.resolve()
    require(out.is_relative_to(ROOT), 'PATH', 'workspace output'); out.mkdir(parents=True, exist_ok=False)
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent two-record Wave37 bounded recovery and every original byte comparison; finite calibrated corrupt controls; no model semantics')
    def tick():
        require(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20,
                'DEADLINE', 'not completed within allocated budget; partial outputs preserved')
    try:
        tick(); inputs = {}
        for name, identity in [(MANIFEST, MANIFEST_SHA), (PACKAGER, PACKAGER_SHA), (AUDIT, AUDIT_SHA), *SOFTWARE.items()]:
            require(sha(ROOT / name) == identity, 'INPUT', name); inputs[name] = identity
        manifest = load(ROOT / MANIFEST); audit = load(ROOT / AUDIT)
        require(args.source_commit == manifest['source_commit'], 'INPUT', 'reported historical package source commit')
        require(manifest['source_sha256'] == PACKAGER_SHA and manifest['originating_audit'] == dict(path=AUDIT, sha256=AUDIT_SHA),
                'INPUT', 'producer provenance')
        record_map = {r['raw_path']: (r['raw_sha256'], r['raw_bytes']) for r in shape(manifest, ROOT)}
        require(record_map == POPULATION and (manifest['raw_bytes'], manifest['gzip_parts'], manifest['gzip_bytes']) == (124864726, 16, 4416662),
                'POPULATION', 'exact frozen two-record universe')
        bound = dict(audit['inputs_sha256'])
        bound.update({(Path(AUDIT).parent / name).as_posix(): value for name, value in audit['outputs_sha256'].items()})
        require(all(bound.get(name) == identity for name, (identity, _) in POPULATION.items()), 'INPUT', 'independent model report raw bindings')
        controls_out = out / 'controls'; controls_out.mkdir()
        positives, checks = controls(controls_out, tick)
        recovered = restore(manifest, ROOT, out / 'recovered', tick)
        for record in manifest['records']:
            inputs[record['raw_path']] = record['raw_sha256']
            inputs.update({part['path']: part['gzip_sha256'] for part in record['parts']})
        save(out / 'summary.json', dict(schema='INDEPENDENT_WAVE37_LOSSLESS_RECOVERY_V1', status='PASS',
             timestamp=datetime.now(timezone.utc).isoformat(), source_commit=args.source_commit,
             command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
             verifier='/root/native_driver', producer='/root', source_sha256=sha(Path(__file__)),
             spec_sha256=sha(Path(__file__).with_name('audit_20261003_wave37_lossless_recovery_v1_spec.md')),
             inputs_sha256=inputs, records=recovered, record_count=2, gzip_parts=16, raw_bytes=124864726,
             gzip_bytes=4416662, original_literal_bytes_compared=124864726, controls=dict(positives=positives, negatives=checks),
             availability='LOCAL_ONLY', mathematical_replay=False, producer_imports=False,
             shared_components=['Python standard-library gzip/zlib, hashlib, filesystem I/O and unchanged command_deadline containment dependency'],
             limitations=['Complete byte restoration and literal comparison only; no fresh model-semantic theorem replay.',
                          'LOCAL_ONLY until separately checked immutable publication.', 'No full historical transitive source/platform-binary closure.']))
    except Exception as error:
        save(out / 'failure.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), error_type=type(error).__name__, diagnostic=str(error),
                                       stage=getattr(error, 'stage', None), source_sha256=sha(Path(__file__)), preserved_partial_outputs=True))
        raise


if __name__ == '__main__':
    main()
