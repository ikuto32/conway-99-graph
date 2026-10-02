"""Confirm published wave36 bytes and change only new artifact availability.

This is byte-identity bookkeeping, not a mathematical replay. Six raw model/control
inputs are public through lossless gzip parts; their raw paths are absent in Git.
"""
import argparse, copy, gzip, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import yaml
import validate_claims as registry
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/20261003_wave36_registration02/CLAIMS.before.yaml'
STAGE = 'acceleration/results/20261003_wave36_allowlist02/manifest.json'
STAGE_SHA = '83e995d249766549450f46e92b0a2bc9c27038eafb96af82352eb7fc2802c5b4'
PACKAGES = [
    ('acceleration/results/20261002_wave33_model_package01/manifest.json',
     'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
     'acceleration/results/20261002_independent_review/wave33_model_recovery01/summary.json',
     'b9352a5e5810f20ff9187c06f5e00636f2f3abad2810ed3d7c23df655b76f583'),
    ('acceleration/results/20261002_wave33_reconstruction_package01/manifest.json',
     'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
     'acceleration/results/20261002_independent_review/wave33_reconstruction_recovery01/summary.json',
     '09623c7c36a6b6b4d7905992361721f38b9ea7778fe7493f01455a4de90d1ba5'),
    ('acceleration/results/20261003_wave36_coupling_package01/manifest.json',
     '38f641ec21ec3d1d617515e8b3e578e098886863f7016ad640ac1906e8b0988f',
     'acceleration/results/20261003_independent_review/wave36_census_recovery01/summary.json',
     '659827807687970e2ca5ab714ba779a703fc9223f84bbe29fd4edc1c7259079b'),
]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--commit', required=True)
    ap.add_argument('--previous-sha256', required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    deadline = CommandDeadline(args.seconds, allocation_reason='Immutable wave36 byte identity and lossless public model recovery bookkeeping')
    before = (ROOT / 'CLAIMS.yaml').read_bytes()
    need(hashlib.sha256(before).hexdigest() == args.previous_sha256, 'exact frozen337 ledger')
    old = registry.read_ledger(ROOT / 'CLAIMS.yaml')
    data = copy.deepcopy(old)
    need(len(data['claims']) == 337, 'exact frozen claim population')
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/codex/eight-coordinate-continuation-20260930'], cwd=ROOT, text=True).strip()
    need(remote.split()[0] == args.commit, 'expected public remote branch commit')
    repo = json.loads(subprocess.check_output(['gh', 'repo', 'view', 'ikuto32/conway-99-graph', '--json', 'isPrivate,url'], cwd=ROOT))
    need(repo['isPrivate'] is False, 'public repository observation')
    need(digest(ROOT / STAGE) == STAGE_SHA, 'exact frozen stage manifest')
    stage = json.loads((ROOT / STAGE).read_bytes())
    final_name = 'acceleration/results/20261003_wave36_finalize01/summary.json'
    final_sha = 'de677cad0280350e23ad50329fc407229a53727363ed9f0e00009de5f949b95a'
    need(digest(ROOT / final_name) == final_sha, 'exact late metadata and AST receipt')
    final = json.loads((ROOT / final_name).read_bytes())
    need(final['status'] == 'WAVE36_LATE_METADATA_AND_INDEXED_PYTHON_AST_PASS' and final['ledger_sha256'] == args.previous_sha256, 'exact completed late metadata scope')
    merged = {row['path']: row for row in stage['records']}
    for row in final['records']:
        if row['path'] in merged:
            need((merged[row['path']]['sha256'], merged[row['path']]['bytes']) == (row['sha256'], row['bytes']), 'consistent late raw input')
        merged[row['path']] = row
    merged[final_name] = dict(path=final_name, sha256=final_sha, bytes=(ROOT / final_name).stat().st_size)
    stage = copy.deepcopy(stage)
    stage['records'] = list(merged.values())
    baseline = registry.read_ledger(ROOT / BASE)
    prior_ids = {a['id'] for a in baseline['artifacts']}
    new = [a for a in data['artifacts'] if a['id'] not in prior_ids]
    needed = {r['path'] for r in stage['records']} | {STAGE}
    needed.update(a['path'] for a in new if a['path'])
    packages = []
    for name, identity, review, review_identity in PACKAGES:
        need(digest(ROOT / name) == identity and digest(ROOT / review) == review_identity, 'frozen package and independent recovery')
        package = json.loads((ROOT / name).read_bytes())
        packages.append((name, identity, package))
        needed.update([name, review])
        needed.update(row['raw_path'] for row in package['records'])
        needed.update(p['path'] for row in package['records'] for p in row['parts'])
    blobs = {}
    process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for name in sorted(needed):
            need(not deadline.status()['stop_required'], 'immutable byte deadline')
            need((ROOT / name).resolve().is_relative_to(ROOT) and '\n' not in name, 'literal bounded path')
            process.stdin.write((args.commit + ':' + name + '\n').encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            if header[-1:] == [b'missing']:
                blobs[name] = None
                continue
            need(len(header) == 3 and header[1] == b'blob', 'published literal file object')
            size = int(header[2])
            remaining, h = size, hashlib.sha256()
            while remaining:
                block = process.stdout.read(min(8 * 1024 ** 2, remaining))
                need(bool(block), 'complete Git blob')
                h.update(block)
                remaining -= len(block)
            need(process.stdout.read(1) == b'\n', 'complete Git batch record')
            blobs[name] = dict(sha256=h.hexdigest(), bytes=size)
        process.stdin.close()
        need(process.wait(timeout=10) == 0, 'Git reader completion')
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
    for row in stage['records']:
        need(blobs[row['path']] == dict(sha256=row['sha256'], bytes=row['bytes']), 'all frozen staged bytes ' + row['path'])
    need(blobs[STAGE]['sha256'] == STAGE_SHA, 'published stage anchor')
    raw = {}
    part_count = raw_bytes = gzip_bytes = 0
    for name, identity, package in packages:
        need(blobs[name]['sha256'] == identity, 'published package anchor')
        for row in package['records']:
            h, offset = hashlib.sha256(), 0
            need(row['raw_path'] not in raw, 'disjoint literal raw population')
            for part in row['parts']:
                need(not deadline.status()['stop_required'], 'lossless decoding deadline')
                need(blobs[part['path']] == dict(sha256=part['gzip_sha256'], bytes=part['gzip_bytes']), 'published gzip identity')
                need(digest(ROOT / part['path']) == part['gzip_sha256'], 'local decoding bytes equal immutable Git bytes')
                decoded = gzip.decompress((ROOT / part['path']).read_bytes())
                need(offset == part['raw_offset'] and len(decoded) == part['raw_bytes'] and hashlib.sha256(decoded).hexdigest() == part['raw_sha256'], 'literal ordered decoded segment')
                h.update(decoded)
                offset += len(decoded)
                part_count += 1
                gzip_bytes += part['gzip_bytes']
            need(offset == row['raw_bytes'] and h.hexdigest() == row['raw_sha256'], 'complete raw model identity')
            need(blobs.get(row['raw_path']) is None, 'raw models intentionally absent from Git')
            raw[row['raw_path']] = dict(manifest=name, manifest_sha256=identity, sha256=h.hexdigest(), bytes=offset)
            raw_bytes += offset
    need((len(raw), part_count, raw_bytes, gzip_bytes) == (6, 32, 242396575, 7306880), 'exact frozen model recovery population')
    changed, retained = [], []
    prefix = 'https://github.com/ikuto32/conway-99-graph/blob/' + args.commit + '/'
    for artifact in new:
        name = artifact['path']
        if name in raw:
            item = raw[name]
            need(item['sha256'] == artifact['sha256'], 'exact new raw artifact')
            retrieval = ('Lossless public package: ' + prefix + item['manifest'] + '; run the pinned recover_20261001_twentyninth_raw_artifacts.py against this manifest into a fresh destination. Literal recovered path: ' + name + '; SHA-256: ' + item['sha256'] + '. This is byte recovery, not mathematical replay.')
        elif blobs.get(name) is not None:
            need(blobs[name]['sha256'] == artifact['sha256'], 'exact direct artifact ' + name)
            retrieval = prefix + name + '; exact immutable artifact. Historical transitive checking closure and platform binaries have separate availability.'
        else:
            retained.append(dict(id=artifact['id'], path=name, availability=artifact['availability'], reason='Not authenticated in this published payload; previous availability retained.'))
            continue
        artifact.update(availability='PUBLIC', retrieval=retrieval, unavailable_reason=None)
        changed.append(artifact['id'])
    need(data['claims'] == old['claims'] and data['target'] == old['target'], 'all material claims and target unchanged')
    need([a for a in data['artifacts'] if a['id'] in prior_ids] == baseline['artifacts'], 'all prior artifact records unchanged')
    need(len(retained) == 0, 'every new wave36 artifact authenticated directly or losslessly')
    now = datetime.now(timezone.utc).isoformat()
    data['updated_at'] = now
    validation = registry.validate(data, ROOT, json.loads((ROOT / 'docs/claims.schema.json').read_bytes()), 'public', old)
    need(validation['valid'], repr(validation['errors']))
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    report = dict(timestamp=now, status='IMMUTABLE_WAVE36_DIRECT_AND_LOSSLESS_EVIDENCE_PUBLICATION_CONFIRMED', command=[sys.executable, *sys.argv], cwd=str(ROOT), source_sha256=digest(Path(__file__)), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), publication_commit=args.commit, remote_observation=remote, public_repository_observation=repo, before_ledger_sha256=args.previous_sha256, after_ledger_sha256=hashlib.sha256(after).hexdigest(), stage_manifest=dict(path=STAGE, sha256=STAGE_SHA), immutable_records=stage['records'], changed_artifact_ids=changed, retained_artifacts=retained, raw_recovery_records=raw, raw_population=dict(raw_members=len(raw), gzip_parts=part_count, raw_bytes=raw_bytes, gzip_bytes=gzip_bytes), changed_material_claims=0, new_exclusions=0, mathematical_replay=False, validation=validation, limitations=['Remote advertises the locally checked immutable commit; no second clean-clone network transfer was performed.', 'All six recovered literal inputs were decoded and hashed; no mathematical proof was replayed.', 'Complete historical transitive gate closure and platform binaries remain separately disclosed.'])
    (out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    need((ROOT / 'CLAIMS.yaml').read_bytes() == before, 'no concurrent ledger modification')
    pending = out / 'CLAIMS.pending.yaml'
    pending.write_bytes(after)
    os.replace(pending, ROOT / 'CLAIMS.yaml')
    print(json.dumps(dict(status=report['status'], public_artifact_records=len(changed), raw_population=report['raw_population'], changed_material_claims=0)))


if __name__ == '__main__':
    main()
