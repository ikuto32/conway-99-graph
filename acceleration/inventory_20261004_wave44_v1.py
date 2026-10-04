"""SOURCE ONLY: bounded byte inventory and read-only staged comparison for cutoff400."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
LIMIT = 50 * 1024 * 1024
CHUNK = 1024 * 1024
SHA = re.compile(r'[0-9a-f]{64}\Z')
OID = re.compile(r'[0-9a-f]{40}\Z')
SECRET = re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{40,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
SOFTWARE = {
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/validate_claims.py': 'a48f55b54918b0c494e6f06f80bdcdc52f304dfc370dd25842aeae3a0f861265',
    'acceleration/run_compute_command_v2.py': '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def integer(value, stage):
    need(type(value) is int and value >= 0, stage)
    return value


def hash_text(value):
    need(type(value) is str and SHA.fullmatch(value), 'HASH_FORMAT')
    return value


def match_digest(actual, expected):
    need(actual == hash_text(expected), 'FILE_HASH')


def literal(name):
    need(type(name) is str and name and not any(c in name for c in '\\\r\n\0'), 'LITERAL_PATH')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and str(p) == name, 'PATH_BOUNDARY')
    need(not any(x.lower() in {'.git', 'build', 'private', 'recovered', 'secrets', '.ssh', '.env'}
                 for x in p.parts), 'PRIVATE_OR_BUILD_PATH')
    need(not name.startswith('tools/drat-trim'), 'EXTERNAL_SUBMODULE')
    need(name.startswith(('acceleration/', 'docs/')) or name in
         {'CLAIMS.yaml', 'README.md', 'ACTIVE_RESEARCH.md', 'pyproject.toml', 'uv.lock', '.gitattributes'},
         'RESEARCH_NAMESPACE')
    return p


def bounded(name):
    path = ROOT
    for part in literal(name).parts:
        path /= part
        if path.exists() or path.is_symlink():
            info = path.lstat()
            need(not stat.S_ISLNK(info.st_mode) and not
                 (getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)),
                 'SYMLINK_OR_REPARSE_POINT')
    need(path.resolve().is_relative_to(ROOT), 'RESOLVED_BOUNDARY')
    return path


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= LIMIT, 'JSON_SIZE')
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'JSON_DUPLICATE')
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError('JSON_NONFINITE')))


def secret_check(raw):
    need(SECRET.search(raw) is None, 'SECRET_MARKER')


def suffix(now, old):
    need(type(now) is bytes and type(old) is bytes and now.endswith(old), 'DOCUMENT_SUFFIX')


def public_identity(row, artifact):
    need(row['availability'] == 'PUBLIC' and artifact['availability'] == 'PUBLIC', 'PUBLIC_STATUS')
    need(row['path'] == artifact['path'] and row['sha256'] == artifact['sha256'], 'PUBLIC_IDENTITY')
    hash_text(row['sha256'])
    url = row['immutable_retrieval_url']
    retrieval = artifact['retrieval']
    need(type(url) is str and re.fullmatch(r'https://github\.com/ikuto32/conway-99-graph/blob/[0-9a-f]{40}/' + re.escape(row['path']), url)
         and type(retrieval) is str and retrieval.startswith(url)
         and (len(retrieval) == len(url) or retrieval[len(url)] in '; '), 'PUBLIC_RETRIEVAL')
    return dict(row, exact_ledger_retrieval=retrieval)


def unique_paths(rows):
    names = [str(literal(r['path'])) for r in rows]
    need(len(names) == len(set(names)) and len(names) == len({x.casefold() for x in names}), 'DUPLICATE_PATH')
    return names


def parse_index(raw):
    need(type(raw) is bytes and len(raw) <= LIMIT and (not raw or raw.endswith(b'\0')), 'INDEX_FORMAT')
    rows = []
    for item in raw.split(b'\0')[:-1]:
        fields, name = item.split(b'\t', 1)
        mode, oid, stage = fields.decode('ascii').split(' ')
        need(mode in {'100644', '100755', '120000', '160000'} and OID.fullmatch(oid) and stage in {'0', '1', '2', '3'}, 'INDEX_FORMAT')
        rows.append({'path': name.decode('utf8'), 'mode': mode, 'oid': oid, 'stage': int(stage), 'raw': item + b'\0'})
    return rows


def index_projection(rows, selected):
    raw = b''.join(sorted(r['raw'] for r in rows if r['path'] not in selected))
    links = [{'path': r['path'], 'mode': r['mode'], 'oid': r['oid'], 'stage': r['stage']}
             for r in rows if r['mode'] == '160000']
    return {'unselected_rows_sha256': hashlib.sha256(raw).hexdigest(),
            'unselected_rows': sum(r['path'] not in selected for r in rows), 'gitlinks': links}


def unchanged_index(current, before):
    need(current['gitlinks'] == before['gitlinks'], 'GITLINK_CHANGED')
    need(current['unselected_rows_sha256'] == before['unselected_rows_sha256'] and
         type(current['unselected_rows']) is int and current['unselected_rows'] == before['unselected_rows'], 'UNSELECTED_INDEX_CHANGED')


def blob_header(raw, oid, size):
    fields = raw.rstrip(b'\n').split(b' ')
    need(len(fields) == 3 and fields[0] == oid.encode('ascii'), 'BLOB_OBJECT_ID')
    need(fields[1] == b'blob', 'BLOB_TYPE')
    need(fields[2] == str(integer(size, 'TYPED_SIZE')).encode('ascii'), 'BLOB_SIZE')


def batch_blob(stream, oid, size, tick):
    tick()
    blob_header(stream.readline(256), oid, size)
    h = hashlib.sha256()
    left = size
    while left:
        tick()
        chunk = stream.read(min(CHUNK, left))
        need(bool(chunk), 'BLOB_TRUNCATED')
        left -= len(chunk)
        h.update(chunk)
    need(stream.read(1) == b'\n', 'BLOB_TRAILER')
    tick()
    return h.hexdigest()


def calibration(rows):
    digest = '0' * 64
    art = {'path': 'docs/x.md', 'sha256': digest, 'availability': 'PUBLIC',
           'retrieval': 'https://github.com/ikuto32/conway-99-graph/blob/' + '1' * 40 + '/docs/x.md;'}
    row = {'path': art['path'], 'sha256': digest, 'availability': 'PUBLIC', 'immutable_retrieval_url': art['retrieval'].rstrip(';')}
    idx = b'100644 ' + b'1' * 40 + b' 0\tdocs/old.md\0'
    selected = {'docs/new.md'}
    projection = index_projection(parse_index(idx), selected)
    oid = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
    header = (oid + ' blob 0\n').encode()
    def positive(name, fn):
        fn()
        rows.append({'case': name, 'expected_stage': 'PASS', 'actual_stage': 'PASS'})
    positive('strict_json', lambda: need(strict_json(b'{"n":400}') == {'n': 400}, 'POSITIVE'))
    positive('integer', lambda: integer(400, 'TYPED_COUNT'))
    positive('literal', lambda: literal('docs/x.md'))
    positive('suffix', lambda: suffix(b'notice\nold', b'old'))
    positive('empty_git_blob', lambda: need(hashlib.sha1(b'blob 0\0').hexdigest() == oid, 'POSITIVE'))
    positive('selected_addition', lambda: unchanged_index(index_projection(parse_index(idx + b'100644 ' + b'2' * 40 + b' 0\tdocs/new.md\0'), selected), projection))
    positive('public_identity', lambda: public_identity(row, art))
    positive('batch_empty', lambda: need(batch_blob(io.BytesIO(header + b'\n'), oid, 0, lambda: None) == hashlib.sha256(b'').hexdigest(), 'POSITIVE'))
    cases = [
        ('parent', 'PATH_BOUNDARY', lambda: literal('docs/../x')),
        ('backslash', 'LITERAL_PATH', lambda: literal('docs\\x')),
        ('build', 'PRIVATE_OR_BUILD_PATH', lambda: literal('acceleration/build/x')),
        ('json_duplicate', 'JSON_DUPLICATE', lambda: strict_json(b'{"x":1,"x":2}')),
        ('json_nonfinite', 'JSON_NONFINITE', lambda: strict_json(b'{"x":NaN}')),
        ('bool_count', 'TYPED_COUNT', lambda: integer(True, 'TYPED_COUNT')),
        ('bool_size', 'TYPED_SIZE', lambda: blob_header(header, oid, False)),
        ('hash_mismatch', 'FILE_HASH', lambda: match_digest(hashlib.sha256(b'record').hexdigest(), '0' * 64)),
        ('changed_suffix', 'DOCUMENT_SUFFIX', lambda: suffix(b'changed', b'old')),
        ('public_status', 'PUBLIC_STATUS', lambda: public_identity(dict(row, availability='LOCAL_ONLY'), art)),
        ('public_hash', 'PUBLIC_IDENTITY', lambda: public_identity(dict(row, sha256='2' * 64), art)),
        ('public_retrieval', 'PUBLIC_RETRIEVAL', lambda: public_identity(dict(row, immutable_retrieval_url='https://example.com'), art)),
        ('duplicate_path', 'DUPLICATE_PATH', lambda: unique_paths([{'path': 'docs/x'}, {'path': 'docs/x'}])),
        ('unselected_index', 'UNSELECTED_INDEX_CHANGED', lambda: unchanged_index(index_projection(parse_index(idx.replace(b'1' * 40, b'2' * 40)), selected), projection)),
        ('gitlink', 'GITLINK_CHANGED', lambda: unchanged_index(dict(projection, gitlinks=[{'path': 'tools/drat-trim', 'mode': '160000', 'oid': '1' * 40, 'stage': 0}]), projection)),
        ('batch_oid', 'BLOB_OBJECT_ID', lambda: batch_blob(io.BytesIO(header.replace(oid.encode(), b'1' * 40) + b'\n'), oid, 0, lambda: None)),
        ('batch_truncated', 'BLOB_TRUNCATED', lambda: batch_blob(io.BytesIO((oid + ' blob 1\n').encode()), oid, 1, lambda: None)),
        ('secret_marker', 'SECRET_MARKER', lambda: secret_check(b'ghp_' + b'A' * 36)),
    ]
    for name, stage, fn in cases:
        try:
            fn()
            actual = 'ACCEPTED_CORRUPTION'
        except ValueError as exc:
            actual = str(exc)
        rows.append({'case': name, 'expected_stage': stage, 'actual_stage': actual})
        need(actual == stage, 'CONTROL_STAGE')
    need(len(rows) == 26, 'CONTROL_POPULATION')
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=['calibrate', 'inventory', 'staged-check'])
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--self-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    ap.add_argument('--proposal')
    ap.add_argument('--proposal-sha256')
    ap.add_argument('--calibration')
    ap.add_argument('--calibration-sha256')
    ap.add_argument('--inventory')
    ap.add_argument('--inventory-sha256')
    ap.add_argument('--appendix')
    ap.add_argument('--appendix-sha256')
    ap.add_argument('--expected-index-sha256')
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Wave44 explicit byte inventory/read-only index checks; all setup/hash/Git/serialization shares one inclusive deadline')
    out_name = Path(args.out).resolve().relative_to(ROOT).as_posix()
    out = bounded(out_name)
    need(not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    completed, controls, pins = [], [], {}
    def tick():
        status = deadline.status()
        need(not status['stop_required'] and status['remaining_seconds'] > 20, 'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
        return status
    def save(name, data):
        tick()
        with (out / name).open('x', encoding='utf8', newline='\n') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        tick()
    def raw_read(path):
        tick()
        need(path.is_file() and path.stat().st_size <= LIMIT, 'MEMBER_SIZE')
        raw = bytearray()
        with path.open('rb') as stream:
            while chunk := stream.read(CHUNK):
                tick()
                raw.extend(chunk)
                need(len(raw) <= LIMIT, 'MEMBER_SIZE')
        tick()
        return bytes(raw)
    def file_identity(name, expected=None):
        path = bounded(name)
        tick()
        size = path.stat().st_size
        need(path.is_file() and size <= LIMIT, 'MEMBER_SIZE')
        h, blob = hashlib.sha256(), hashlib.sha1(b'blob ' + str(size).encode() + b'\0')
        total, tail = 0, b''
        with path.open('rb') as stream:
            while chunk := stream.read(CHUNK):
                tick()
                secret_check(tail + chunk)
                tail = (tail + chunk)[-128:]
                total += len(chunk)
                need(total <= LIMIT, 'MEMBER_SIZE')
                h.update(chunk)
                blob.update(chunk)
        tick()
        need(total == size and path.stat().st_size == size, 'FILE_SIZE_CHANGED')
        actual = h.hexdigest()
        if expected is not None:
            match_digest(actual, expected)
        return {'path': name, 'sha256': actual, 'bytes': total, 'git_blob_oid': blob.hexdigest()}
    def load(name, expected):
        identity = file_identity(name, expected)
        pins[name] = identity['sha256']
        raw = raw_read(bounded(name))
        need(hashlib.sha256(raw).hexdigest() == identity['sha256'], 'FILE_HASH')
        return strict_json(raw)
    def git(*words):
        tick()
        result = subprocess.run(['git', *words], cwd=ROOT, capture_output=True,
                                timeout=max(0.01, tick()['remaining_seconds'] - 20))
        tick()
        need(result.returncode == 0 and len(result.stdout) <= LIMIT, 'GIT_READ')
        return result.stdout
    def observe():
        tick()
        index = raw_read(ROOT / '.git' / 'index')
        return {'head': git('rev-parse', 'HEAD').decode().strip(),
                'ledger_sha256': file_identity('CLAIMS.yaml')['sha256'],
                'index_sha256': hashlib.sha256(index).hexdigest()}
    try:
        for name, expected in {SELF.relative_to(ROOT).as_posix(): args.self_sha256,
                               SPEC.relative_to(ROOT).as_posix(): args.spec_sha256, **SOFTWARE}.items():
            pins[name] = file_identity(name, expected)['sha256']
        calibration(controls)
        save('controls.json', controls)
        if args.mode == 'calibrate':
            summary = {'schema': 'WAVE44_BYTE_INVENTORY_CALIBRATION_V1', 'status': 'AUTHOR_ENGINEERING_CONTROLS_PASS',
                       'positive': 8, 'strict_negative': 18, 'selected_evidence_read': False,
                       'filesystem_or_git_process_controls_executed': False}
        else:
            gate = load(args.calibration, args.calibration_sha256)
            need(gate['schema'] == 'WAVE44_BYTE_INVENTORY_CALIBRATION_V1' and gate['status'] == 'AUTHOR_ENGINEERING_CONTROLS_PASS'
                 and type(gate['positive']) is int and gate['positive'] == 8 and type(gate['strict_negative']) is int and gate['strict_negative'] == 18,
                 'CALIBRATION_HEADER')
            need(gate['inputs_sha256'][SELF.relative_to(ROOT).as_posix()] == args.self_sha256 and
                 gate['inputs_sha256'][SPEC.relative_to(ROOT).as_posix()] == args.spec_sha256, 'CALIBRATION_SOURCE')
            config = load(args.proposal, args.proposal_sha256)
            need(config['schema'] == 'WAVE44_FROZEN400_EXPLICIT_PUBLICATION_PATHS_V2', 'PROPOSAL_SCHEMA')
            expected = config['protected_observation']
            before = observe()
            need(before['head'] == expected['head'] and before['ledger_sha256'] == expected['ledger_sha256'], 'PROTECTED_CONTEXT')
            need(git('rev-parse', '--show-object-format').strip() == b'sha1', 'GIT_OBJECT_FORMAT')
            from validate_claims import read_ledger
            ledger = read_ledger(bounded('CLAIMS.yaml'))
            counts = Counter(c['status'] for c in ledger['claims'])
            need(len(ledger['claims']) == 400 and counts == {'VERIFIED': 392, 'CANDIDATE': 3, 'REFUTED': 5}
                 and all(c['review_state'] == 'CLEAR' for c in ledger['claims']), 'LEDGER_CUTOFF')
            artifacts = {a['id']: a for a in ledger['artifacts']}
            need(sum(a['availability'] == 'PUBLIC' for a in artifacts.values()) == 6054, 'PUBLIC_POPULATION')
            public_reuse = [public_identity(row, artifacts[row['existing_artifact_id']])
                            for row in config['reused_public_evidence']]
            member_rows = config['selected_existing_files'] + config['explicit_appendix_files']
            names = unique_paths(member_rows)
            need(names == config['selected_paths_v2'], 'SELECTED_PATH_ORDER')
            selected = set(names)
            current_index = parse_index(git('ls-files', '--stage', '-z'))
            projection = index_projection(current_index, selected)
            if args.mode == 'inventory':
                need(before['index_sha256'] == expected['index_sha256'], 'PROTECTED_INDEX')
                for row in member_rows:
                    completed.append(file_identity(row['path'], row['expected_sha256']))
                doc = config['documentation']
                for row in doc['notices']:
                    old = git('show', expected['head'] + ':' + row['path'])
                    need(hashlib.sha256(old).hexdigest() == row['before_sha256'], 'HISTORICAL_DOCUMENT_HASH')
                    snapshot = raw_read(bounded(row['before_snapshot']))
                    need(snapshot == old, 'HISTORICAL_DOCUMENT_SNAPSHOT')
                    now = raw_read(bounded(row['path']))
                    suffix(now, old)
                    need(hashlib.sha256(now).hexdigest() == row['after_sha256'], 'DOCUMENT_CURRENT_HASH')
                after = observe()
                need(after == before, 'PROTECTED_AFTER')
                save('selected_paths.nul.json', {'encoding': 'UTF8_NUL', 'paths': names})
                tick()
                with (out / 'selected_paths.nul').open('xb') as stream:
                    stream.write(b''.join(name.encode('utf8') + b'\0' for name in names))
                tick()
                summary = {'schema': 'WAVE44_BYTE_INVENTORY_V1', 'status': 'EXPLICIT_BYTE_INVENTORY_COMPLETE',
                           'files': completed, 'selected_files': len(completed), 'selected_bytes': sum(r['bytes'] for r in completed),
                           'public_reuse': public_reuse, 'existing_PUBLIC_reuse_entries': len(public_reuse),
                           'protected_before': before, 'protected_after': after, 'index_projection': projection,
                           'initial_index_paths': [r['path'] for r in current_index],
                           'historical_document_suffixes_checked': 4, 'credential_pattern_screen': True}
            else:
                inventory = load(args.inventory, args.inventory_sha256)
                need(inventory['schema'] == 'WAVE44_BYTE_INVENTORY_V1' and inventory['status'] == 'EXPLICIT_BYTE_INVENTORY_COMPLETE', 'INVENTORY_HEADER')
                need(inventory['inputs_sha256'][args.proposal] == args.proposal_sha256, 'INVENTORY_PROPOSAL')
                rows = inventory['files']
                need([r['path'] for r in rows] == names, 'INVENTORY_PATHS')
                extra = []
                if args.appendix:
                    appendix = load(args.appendix, args.appendix_sha256)
                    need(appendix['schema'] == 'WAVE44_ROOT_EXPLICIT_STAGED_METADATA_APPENDIX_V1', 'STAGED_APPENDIX_SCHEMA')
                    extra = appendix['files']
                    for r in extra:
                        need(r['path'] not in inventory['initial_index_paths'], 'APPENDIX_EXISTING_INDEX_ROW')
                        completed.append(file_identity(r['path'], r['sha256']))
                    rows = rows + completed
                    unique_paths(rows)
                    completed = []
                allowed = {r['path'] for r in rows}
                need(before['index_sha256'] == hash_text(args.expected_index_sha256), 'STAGED_INDEX_PIN')
                # Appendices may add only paths absent from the inventory-time index.
                # Original projection recorded their absence if absent; changing an
                # existing unselected row cannot be waived by a later appendix.
                unchanged_index(index_projection(current_index, allowed), inventory['index_projection'])
                staged = {r['path']: r for r in current_index if r['stage'] == 0}
                need(not any(r['stage'] != 0 for r in current_index), 'INDEX_CONFLICT')
                process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                try:
                    for row in rows:
                        path = row['path']
                        item = staged.get(path)
                        need(item is not None and item['mode'] in {'100644', '100755'} and item['oid'] == row['git_blob_oid'], 'STAGED_BLOB_IDENTITY')
                        raw_identity = file_identity(path, row['sha256'])
                        need(raw_identity['bytes'] == integer(row['bytes'], 'TYPED_SIZE') and raw_identity['git_blob_oid'] == row['git_blob_oid'], 'STAGED_WORKTREE_BYTES')
                        tick()
                        process.stdin.write((item['oid'] + '\n').encode('ascii'))
                        process.stdin.flush()
                        need(batch_blob(process.stdout, item['oid'], row['bytes'], tick) == row['sha256'], 'STAGED_BLOB_SHA256')
                        completed.append({'path': path, 'sha256': row['sha256'], 'git_blob_oid': item['oid'], 'bytes': row['bytes']})
                    process.stdin.close()
                    need(process.wait(timeout=max(0.01, tick()['remaining_seconds'] - 20)) == 0, 'BATCH_EXIT')
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=max(0.01, deadline.status()['remaining_seconds']))
                    process.stdout.close()
                after = observe()
                need(after == before, 'STAGED_CONTEXT_CHANGED')
                summary = {'schema': 'WAVE44_READ_ONLY_STAGED_COMPARISON_V1', 'status': 'EXACT_STAGED_BYTES_PASS',
                           'checked_files': len(rows), 'checked_bytes': sum(r['bytes'] for r in rows),
                           'protected_before': before, 'protected_after': after, 'unselected_index_unchanged': True,
                           'gitlinks_unchanged': True, 'comparisons': completed}
        for name, expected_pin in pins.items():
            file_identity(name, expected_pin)
        output_hashes = {}
        for path in sorted(out.iterdir()):
            need(path.is_file(), 'OUTPUT_FILE')
            output_hashes[path.relative_to(ROOT).as_posix()] = file_identity(path.relative_to(ROOT).as_posix())['sha256']
        summary.update(timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/structural',
                       outputs_sha256=output_hashes,
                       inputs_sha256=pins, mathematical_replays=0, Git_mutations=0, availability_promotions=0,
                       target_resolution='NONE', limits='Author helper controls only; supported runtime and ROOT review are separate. No mathematical verification or availability promotion.')
        save('summary.json', summary)
        tick()
    except Exception as exc:
        # Never serialize exception text: a library exception can contain raw values.
        stage = str(exc) if isinstance(exc, ValueError) and re.fullmatch(r'[A-Z_]+', str(exc)) else type(exc).__name__
        with (out / 'failure.json').open('x', encoding='utf8', newline='\n') as stream:
            json.dump({'status': 'FAILED', 'stage': stage, 'completed_file_rows': completed, 'controls_completed': controls,
                       'deadline': deadline.status(), 'mathematical_replays': 0, 'Git_mutations': 0}, stream, indent=2)
            stream.write('\n')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
