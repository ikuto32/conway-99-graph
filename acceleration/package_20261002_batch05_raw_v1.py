"""Lossless batch05 direct replay closure; engineering only, no claim promotion."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse, gzip, hashlib, json, os, platform, shutil, sys, time
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
NATIVE = 'acceleration/results/20261002_batch05_native01/summary.json'
NATIVE_SHA = '8e9d697fae19a83ed1127d7594f824f3451e8e84a8d91ef3fdf9744d6fdb89f1'
AUDIT = 'acceleration/results/20261002_independent_review/batch05_proofs01/summary.json'
AUDIT_SHA = '1b94e67d00af2d1971074e121e245d392e9e3a49d540380fb476d634ed779d61'
CHUNK = 8 * 1024**2
LIMIT = 10 * 1024**2
LEVEL = 9
RESERVE = 20
CODE = [SELF, SPEC, ROOT/'acceleration/command_deadline.py',
        ROOT/'acceleration/run_compute_command.py', ROOT/'pyproject.toml', ROOT/'uv.lock',
        ROOT/'acceleration/run_20260930_exact_eight_four_builds_v2.py',
        ROOT/'acceleration/build_20260930_exact_eight_parallel_batch.py',
        ROOT/'acceleration/recover_20261001_twentyninth_raw_artifacts.py']
LOCAL_BINARIES = {'build/research-cadical195/source/build/cadical',
                  'build/rook-drat-checker/drat-trim.exe'}


def need(ok, text):
    if not ok:
        raise ValueError(text)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def safe(name):
    need(isinstance(name, str) and name and '\\' not in name, 'literal POSIX path')
    p = Path(name)
    need(not p.is_absolute() and '..' not in p.parts, 'safe relative path')
    q = (ROOT/p).resolve()
    need(q.is_relative_to(ROOT) and q.relative_to(ROOT).as_posix() == name, 'canonical path')
    need(name != 'PROMPT.md' and not name.startswith(('tools/', 'external_conway99_research/')), 'protected path')
    return q


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def tick(deadline):
    s = deadline.status()
    need(not s['stop_required'] and s['remaining_seconds'] > RESERVE,
         'not completed within the allocated budget; preserve completed record receipts')
    return s


def sha(path, deadline):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(CHUNK), b''):
            tick(deadline)
            h.update(b)
    return h.hexdigest()


def check(name, digest, deadline, length=None):
    p = safe(name)
    need(p.is_file() and (length is None or p.stat().st_size == length), 'file/size: '+name)
    need(sha(p, deadline) == digest, 'sha256: '+name)
    return p


def read(name):
    return json.loads(safe(name).read_bytes())


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def progress(out, value):
    p = out/'progress.json'
    t = out/'progress.tmp'
    t.write_text(json.dumps(value)+'\n', encoding='utf8')
    os.replace(t, p)


def compressed_part(path, block, offset, deadline):
    tick(deadline)
    with path.open('xb') as f:
        with gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0, compresslevel=LEVEL) as g:
            g.write(block)
    n = path.stat().st_size
    need(n <= LIMIT, 'compressed part exceeds publication payload limit')
    return dict(path=key(path), gzip_sha256=sha(path, deadline), gzip_bytes=n,
                raw_offset=offset, raw_sha256=hashlib.sha256(block).hexdigest(), raw_bytes=len(block))


def recovered_identity(record, deadline):
    whole = hashlib.sha256()
    total = 0
    with safe(record['path']).open('rb') as original:
        for part in record['parts']:
            check(part['path'], part['gzip_sha256'], deadline, part['gzip_bytes'])
            need(part['raw_offset'] == total, 'contiguous raw offsets')
            h = hashlib.sha256()
            size = 0
            with gzip.open(safe(part['path']), 'rb') as stream:
                for block in iter(lambda: stream.read(1024**2), b''):
                    tick(deadline)
                    size += len(block)
                    need(size <= part['raw_bytes'], 'bounded decompressed part')
                    need(original.read(len(block)) == block, 'literal original byte comparison')
                    h.update(block)
                    whole.update(block)
            need(size == part['raw_bytes'] and h.hexdigest() == part['raw_sha256'], 'part raw identity')
            total += size
        need(not original.read(1), 'no omitted original tail')
    need(total == record['bytes'] and whole.hexdigest() == record['sha256'], 'whole raw identity')
    return dict(path=record['path'], bytes=total, sha256=whole.hexdigest(), literal_byte_comparison=True)


def freeze(args, deadline, out):
    check(NATIVE, NATIVE_SHA, deadline)
    check(AUDIT, AUDIT_SHA, deadline)
    native, audit = read(NATIVE), read(AUDIT)
    need(audit['status'] == 'INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS'
         and audit['completed_proof_replays'] == 64, 'independent exact 64 proof gate')
    ns, ars = native['case_records'], audit['case_records']
    need(len(ns) == len(ars) == 64 and native['attempted_evaluations'] == native['completed_evaluations'] == 64,
         'complete 64 producer/auditor population')
    need([(r['case_id'], r['case_index']) for r in ns] == [(r['case_id'], r['case_index']) for r in ars],
         'identical ordered case population')
    need(len(set(r['case_id'] for r in ns)) == 64, 'distinct case IDs')
    check(native['manifest_path'], native['manifest_sha256'], deadline)
    manifest = read(native['manifest_path'])
    pins = {NATIVE: NATIVE_SHA, AUDIT: AUDIT_SHA}
    for source in [manifest['inputs_sha256'], audit['inputs_sha256'],
                   {native['manifest_path']: native['manifest_sha256']}]:
        for p, h in source.items():
            need(p not in pins or pins[p] == h, 'conflicting recorded hash')
            pins[p] = h
    code = {key(p): sha(p, deadline) for p in CODE}
    pins.update(code)
    cases = []
    kinds = {}
    reuse = {}
    for n, a in zip(ns, ars):
        check(n['summary_path'], n['summary_sha256'], deadline)
        pins[n['summary_path']] = n['summary_sha256']
        c = read(n['summary_path'])
        files = c['formula']['files']
        need((a['cnf_path'], a['cnf_sha256']) == (files['instance.cnf']['path'], files['instance.cnf']['sha256']), 'audited CNF binding')
        need((a['proof_path'], a['proof_sha256'], a['proof_bytes']) ==
             (c['raw_proof']['path'], c['raw_proof']['sha256'], c['raw_proof']['bytes']), 'audited proof binding')
        need(a['verification_outcome'] == 'UNSAT_VERIFIED' and a['complete_independent_replay']['accepted'], 'completed independent replay')
        for label, descriptor in files.items():
            need(pins.get(descriptor['path']) == descriptor['sha256'], 'formula direct pin')
            kinds[descriptor['path']] = label
        kinds[a['proof_path']] = 'proof.drat'
        cases.append(dict(case_id=n['case_id'], case_index=n['case_index'],
                          proof_path=a['proof_path'], cnf_path=a['cnf_path'],
                          model_path=files['model.json']['path'], scope_path=files['scope.json']['path']))
        mp = files['model_package.json']
        check(mp['path'], mp['sha256'], deadline, mp['bytes'])
        package = read(mp['path'])
        m = files['model.json']
        need((package['raw_path'], package['raw_sha256'], package['raw_bytes']) ==
             (m['path'], m['sha256'], m['bytes']), 'model reuse raw pin')
        need(package['gzip_bytes'] <= LIMIT, 'model gzip publication size')
        reuse[m['path']] = dict(manifest=mp['path'], manifest_sha256=mp['sha256'],
            part=dict(path=package['gzip_path'], gzip_sha256=package['gzip_sha256'],
                      gzip_bytes=package['gzip_bytes'], raw_offset=0,
                      raw_sha256=m['sha256'], raw_bytes=m['bytes']))
    rows, unavailable = [], []
    for name, digest in tqdm(sorted(pins.items()), desc='Freeze direct replay bytes', mininterval=1):
        path = check(name, digest, deadline)
        if name in LOCAL_BINARIES:
            unavailable.append(dict(path=name, sha256=digest, bytes=path.stat().st_size,
                                    availability='LOCAL_ONLY', reason='Platform tool binary; rebuild from pinned source provenance.'))
            continue
        rows.append(dict(path=name, sha256=digest, bytes=path.stat().st_size,
                         kind=kinds.get(name, 'direct_replay_metadata_or_source'), case=next(
                             (c['case_id'] for c in cases if name in [c['proof_path'], c['cnf_path'], c['model_path'], c['scope_path']]), None),
                         reuse=reuse.get(name)))
    counts = Counter(r['kind'] for r in rows)
    need(all(counts[x] == 64 for x in ['proof.drat', 'instance.cnf', 'model.json', 'scope.json']), '64 complete critical populations')
    value = dict(schema='BATCH05_RAW_PUBLICATION_FROZEN_V1', timestamp=stamp(),
        source_commit=args.source_commit, command=[sys.executable, *sys.argv], cwd=str(ROOT),
        python=platform.python_version(), cases=cases, records=rows, record_count=len(rows),
        raw_bytes=sum(r['bytes'] for r in rows), kind_counts=dict(counts),
        code_sha256=code, non_payload_tools=unavailable,
        scope='Exact direct inputs of batch05 native manifest and complete independent proof audit; explicit 64 case raw proof/CNF/model/scope closure.',
        limitations=['Historical gate transitive evidence closure is not recursively repackaged.',
                     'Packaging is engineering and creates no mathematical verification.',
                     'Public availability is pending independent complete recovery audit and publication.'],
        availability='LOCAL_ONLY', publication_pending=True, mathematical_verification=False)
    save(out/'inventory.json', value)
    return dict(status='BATCH05_RAW_INVENTORY_FROZEN', inventory=key(out/'inventory.json'),
                inventory_sha256=sha(out/'inventory.json', deadline), records=len(rows), raw_bytes=value['raw_bytes'], kind_counts=dict(counts))


def controls(args, deadline, out):
    check(args.inventory, args.inventory_sha256, deadline)
    inv = read(args.inventory)
    samples = []
    for kind in ['proof.drat', 'instance.cnf', 'model.json']:
        r = next(x for x in inv['records'] if x['kind'] == kind)
        check(r['path'], r['sha256'], deadline, r['bytes'])
        with safe(r['path']).open('rb') as f:
            block = f.read(CHUNK)
        started = time.monotonic()
        part = compressed_part(out/(kind.replace('.', '_')+'.gz'), block, 0, deadline)
        need(gzip.decompress(safe(part['path']).read_bytes()) == block, 'representative recovered bytes')
        samples.append(dict(kind=kind, source=r['path'], source_sha256=r['sha256'],
                            sample_sha256=part['raw_sha256'], raw_bytes=len(block), gzip_bytes=part['gzip_bytes'],
                            compression_and_check_seconds=time.monotonic()-started, part=part))
    empty = compressed_part(out/'empty.gz', b'', 0, deadline)
    need(gzip.decompress(safe(empty['path']).read_bytes()) == b'', 'empty raw file supported')
    return dict(status='BATCH05_PACKAGING_PRODUCER_CONTROLS_PASS', samples=samples, empty=empty,
                independent_approval=False, mathematical_verification=False,
                allocation_estimate_is_heuristic=True)


def package(args, deadline, out):
    check(args.inventory, args.inventory_sha256, deadline)
    inv = read(args.inventory)
    need(inv['schema'] == 'BATCH05_RAW_PUBLICATION_FROZEN_V1', 'frozen exact schema')
    for name, digest in inv['code_sha256'].items():
        check(name, digest, deadline)
    need(inv['record_count'] == len(inv['records']) == len({r['path'] for r in inv['records']}), 'frozen unique population')
    (out/'records').mkdir()
    rows = []
    for index, raw in enumerate(tqdm(inv['records'], desc='Package exact batch05 raw closure', mininterval=1)):
        tick(deadline)
        need(shutil.disk_usage(ROOT).free > 32*1024**3, '32 GiB host free reserve')
        check(raw['path'], raw['sha256'], deadline, raw['bytes'])
        parts = []
        if raw['reuse'] is not None:
            reuse = raw['reuse']
            check(reuse['manifest'], reuse['manifest_sha256'], deadline)
            p = reuse['part']
            check(p['path'], p['gzip_sha256'], deadline, p['gzip_bytes'])
            parts = [p]
        else:
            offset = 0
            with safe(raw['path']).open('rb') as f:
                while True:
                    block = f.read(CHUNK)
                    if not block and parts:
                        break
                    p = compressed_part(out/f'raw_{index:04d}.part{len(parts):04d}.gz', block, offset, deadline)
                    parts.append(p)
                    offset += len(block)
                    if not block:
                        break
            need(offset == raw['bytes'], 'complete raw chunk population')
        row = {k: raw[k] for k in ['path', 'sha256', 'bytes', 'kind', 'case']}
        row.update(parts=parts, manifest=raw['reuse']['manifest'] if raw['reuse'] else None,
                   manifest_null_reason=None if raw['reuse'] else 'New deterministic compressed parts.')
        result = recovered_identity(row, deadline)
        save(out/'records'/f'raw_{index:04d}.json', dict(record=row, producer_control=result, independent_approval=False))
        rows.append(row)
        progress(out, dict(timestamp=stamp(), stage='packaging', complete_records=len(rows),
             total_records=inv['record_count'], raw_bytes_completed=sum(r['bytes'] for r in rows),
             deadline=deadline.status(), checkpoint='Immutable records/raw_NNNN.json plus corresponding parts.',
             restart='No automatic resume. Authenticate completed per-record receipts and preserve them before a new invocation.'))
    parts = [p for r in rows for p in r['parts']]
    manifest = dict(schema='BATCH05_NORMALIZED_RAW_RECOVERY_V1', timestamp=stamp(),
        source_commit=args.source_commit, command=[sys.executable, *sys.argv], cwd=str(ROOT),
        python=platform.python_version(), zlib_version=__import__('zlib').ZLIB_VERSION,
        tqdm_version=__import__('tqdm').__version__, inventory=args.inventory,
        inventory_sha256=args.inventory_sha256, records=rows, raw_artifacts=len(rows),
        raw_bytes=sum(r['bytes'] for r in rows), gzip_parts=len(parts),
        gzip_bytes=sum(p['gzip_bytes'] for p in parts), compressed_payload_limit_bytes=LIMIT,
        raw_chunk_bytes=CHUNK, compression_level=LEVEL, gzip_mtime=0, filename='',
        all_original_bytes_compared_by_producer=True, independent_approval=False,
        availability='LOCAL_ONLY', publication_pending=True, mathematical_verification=False,
        non_payload_tools=inv['non_payload_tools'], limitations=inv['limitations'],
        source_sha256=sha(SELF, deadline), spec_sha256=sha(SPEC, deadline),
        independent_recovery_required='Fresh full recovery with separate implementation; check every hash/length/part, corrupt controls, and compare raw bytes.')
    save(out/'manifest.json', manifest)
    return dict(status='BATCH05_RAW_PACKAGE_CANDIDATE_RECOVERY_PENDING',
                manifest=key(out/'manifest.json'), manifest_sha256=sha(out/'manifest.json', deadline),
                raw_artifacts=len(rows), raw_bytes=manifest['raw_bytes'], gzip_parts=len(parts), gzip_bytes=manifest['gzip_bytes'],
                independent_approval=False, mathematical_verification=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=['freeze', 'controls', 'package'], required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--allocation-reason', required=True)
    ap.add_argument('--source-commit', required=True)
    ap.add_argument('--inventory')
    ap.add_argument('--inventory-sha256')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason=args.allocation_reason)
    need(RESERVE < args.seconds <= 1700, 'producer allocation avoids unattended 1800s review interval')
    out = safe(args.out)
    out.mkdir(parents=True, exist_ok=False)
    save(out/'invocation.json', dict(timestamp=stamp(), command=[sys.executable, *sys.argv],
         cwd=str(ROOT), allocation_seconds=args.seconds, allocation_reason=args.allocation_reason,
         source_commit=args.source_commit, source_sha256=sha(SELF, deadline), spec_sha256=sha(SPEC, deadline),
         success='Exact declared raw artifacts losslessly recoverable; every original byte preserved.',
         verification='Independent complete recovery audit and corruption controls before PUBLIC availability.',
         supported_supervision_required='Local Windows Job or supervisor inside Linux; no cross-host wrapper.'))
    try:
        result = dict(freeze=freeze, controls=controls, package=package)[args.mode](args, deadline, out)
        result.update(timestamp=stamp(), elapsed_seconds=deadline.status()['elapsed_seconds'])
        save(out/'summary.json', result)
        print(json.dumps(result), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(timestamp=stamp(), error=repr(error), deadline=deadline.status(),
             originals_changed=False, independent_approval=False, completed_records_preserved=True,
             unmet_requirements=['Complete declared raw population', 'Independent complete recovery audit']))
        raise


if __name__ == '__main__':
    main()
