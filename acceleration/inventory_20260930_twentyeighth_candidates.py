"""Frozen wave28 allowlist inventory. No Git, tool execution, or proof replay."""
from pathlib import Path
from collections import defaultdict
import argparse, ast, hashlib, json, re, time
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
CHECKPOINT = B + 'resume/twentyeighth_milestone_checkpoint.json'
CHECKPOINT_SHA = '87eed00b74925fc752375a1aaa4884eeb4221fef4b499ec7767a8bb03ba9875a'
SNAPSHOT = B + 'resume/claims_at_twentyeighth_milestone.yaml'
SNAPSHOT_SHA = 'c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441'
PRIOR = B + 'twentyseventh_artifact_packaging/catalog.json'
PRIOR_SHA = 'fd10bd3872a7699f7ea80e1072c697b300cdb9d0cf7cdb19dd1a0c898e6565a8'
REGISTRATIONS = [B + 'twentyeighth_' + n + '_registration' for n in
                 ['initial', 'kernel_sizeclass', 'sizeclass_proof', 'launcher_refutation']]
REGISTRARS = ['register_20260930_twentyeighth_initial_claims_v2.py',
              'register_20260930_twentyeighth_kernel_sizeclass_claims.py',
              'register_20260930_twentyeighth_sizeclass_proofs.py',
              'register_20260930_twentyeighth_launcher_refutations.py']
DIRECTORIES = REGISTRATIONS + [B + n for n in [
    'twentyeighth_initial_registration_preparation',
    'exact_eight_next32_cnfs', 'exact_eight_next32_consolidated',
    'exact_eight_next32_continuation_cnfs', 'exact_eight_next32_continuation_selection',
    'exact_eight_next32_native_pilot', 'exact_eight_next32_native_preflight',
    'exact_eight_next32_native_preparation', 'exact_eight_next32_selection',
    'exact_eight_explicit_batch_preparation_v2', 'exact_eight_explicit_native_preparation',
    'exact_eight_kernel_redundancy', 'exact_eight_parallel_build_preparation',
    'exact_eight_sizeclass16_cnfs', 'exact_eight_sizeclass16_native_pilot',
    'exact_eight_sizeclass16_native_preflight', 'exact_eight_sizeclass16_selection',
    'exact_eight_sizeclass16_selection_preparation',
]] + [I + n for n in [
    'exact_eight_next32_cnfs', 'exact_eight_next32_object_calibration', 'exact_eight_next32_proofs',
    'exact_eight_first12_union', 'exact_eight_first12_union_v2', 'exact_eight_kernel_redundancy',
    'exact_eight_sizeclass16_cnfs', 'exact_eight_sizeclass16_cnfs_v2',
    'exact_eight_sizeclass16_object_calibration', 'exact_eight_sizeclass16_proofs',
    'exact_eight_explicit_checker_v2_correction',
    'parallel_build_deadline', 'parallel_build_deadline_binding',
    'parallel_windows_job', 'parallel_windows_job_v2',
    'windows_job_assignment_race', 'windows_job_assignment_race_binding',
]]
SOURCE_STEMS = [
    'audit_20260930_exact_eight_first12_union', 'audit_20260930_exact_eight_first12_union_v2',
    'audit_20260930_exact_eight_kernel_redundancy', 'audit_20260930_exact_eight_next32',
    'audit_20260930_exact_eight_next32_proofs', 'audit_20260930_exact_eight_explicit_batch',
    'audit_20260930_exact_eight_explicit_batch_v2', 'audit_20260930_exact_eight_explicit_batch_proofs',
    'audit_20260930_parallel_build_deadline', 'audit_20260930_parallel_windows_job',
    'audit_20260930_parallel_windows_job_v2', 'audit_20260930_windows_job_assignment_race',
    'build_20260930_exact_eight_explicit_batch_v2', 'prepare_20260930_exact_eight_explicit_batch_v2',
    'build_20260930_exact_eight_parallel_batch', 'calibrate_20260930_parallel_build_canary',
    'calibrate_20260930_parallel_build_canary_v2', 'calibrate_20260930_parallel_build_canary_v3',
    'check_20260930_exact_eight_parallel_preparation',
    'check_20260930_exact_eight_explicit_native_preparation',
    'check_20260930_exact_eight_next32_native_preparation', 'continue_20260930_exact_eight_next32',
    'native_20260930_exact_eight_next32', 'native_20260930_exact_eight_next32_v2',
    'native_20260930_exact_eight_explicit_batch', 'prepare_20260930_exact_eight_explicit_native_source',
    'prepare_20260930_exact_eight_next32_consolidated_source',
    'prepare_20260930_exact_eight_next32_native_source', 'select_20260930_exact_eight_next32',
    'select_20260930_exact_eight_sizeclass16', 'select_20260930_exact_eight_sizeclass16_v2',
    'theory_20260930_exact_eight_kernel_redundancy',
    'register_20260930_twentyeighth_initial_claims', *[n[:-3] for n in REGISTRARS],
    'record_20260930_twentyeighth_checkpoint', 'plan_20260930_twentyeighth_replay',
    'inventory_20260930_twentyeighth_candidates',
]
# Optional sibling specs are individually enumerated by this rule, never a glob over future files.
FILES = ['acceleration/' + n + '.py' for n in SOURCE_STEMS] + [
    'acceleration/build_20260930_exact_eight_parallel_batch_pins.json',
    'acceleration/theory_20260930_exact_eight_next32_plan.md',
    'acceleration/theory_20260930_exact_eight_sizeclass16_plan.md',
    CHECKPOINT, SNAPSHOT, B + 'resume/twentyeighth_replay_plan.json',
    B + 'resume/twentyseventh_publication_ci_completion.json',
    B + 'resume/twentyeighth_process_snapshot.stdout.log',
    B + 'resume/twentyeighth_process_snapshot.stderr.log',
    'docs/RESEARCH_20260930_TWENTYEIGHTH_WAVE.md',
    'docs/REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md',
    'docs/AUDIT_20260930_EXACT_EIGHT_FIRST12_UNION.md',
    'docs/AUDIT_20260930_EXACT_EIGHT_FIRST12_UNION_V2.md',
    'docs/AUDIT_20260930_EXACT_EIGHT_KERNEL_REDUNDANCY.md',
    'docs/AUDIT_20260930_EXACT_EIGHT_NEXT32_PROOFS.md',
    'docs/AUDIT_20260930_EXACT_EIGHT_EXPLICIT_BATCH_PROOFS.md',
]
LIMIT = 10 * 1024**2
MAX_FILES = 20000
MAX_BYTES = 4 * 1024**3
MAX_SECONDS = 120
PROTECTED = {'PROMPT.md', 'CLAIMS.yaml', I + 'hadamard_oriented_unknown/process.stdout.log'}
FUTURE_TOKENS = ('next64', 'run_four_builds', 'explicit_batch_v3', 'explicit_batch_proofs_v2',
                 'sizeclass16_affine_gram_gf3')

def reason(p):
    low = p.lower()
    if p in PROTECTED or low.startswith('tools/') or low.endswith('/process.stdout.log'):
        return 'protected; never read or hashed'
    if any(t in low for t in FUTURE_TOKENS):
        return 'later wave; never read or hashed'
    if Path(p).name.lower() in {'.env', '.env.local', 'credentials', 'credentials.json', 'id_rsa', 'id_ed25519'} or Path(p).suffix.lower() in {'.pem', '.key'}:
        return 'secret-shaped path; never read or hashed'
    if Path(p).is_absolute() or '..' in Path(p).parts:
        return 'not a repository-relative path'
    return None

def safe(p):
    assert reason(p) is None, (p, reason(p))
    q = (ROOT / p).resolve()
    assert q.is_relative_to(ROOT)
    return q

def sha(p):
    with safe(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def read(p):
    return json.loads(safe(p).read_bytes())

def write(p, obj):
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.write('\n')

def references(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v) and k.startswith(('acceleration/', 'docs/', '.github/', 'build/', 'tools/', 'external_conway99_research/')):
                yield k, v
            if k in ('path', 'raw_path', 'raw_original_path', 'cnf_path', 'model_path', 'scope_path', 'source_path') and isinstance(v, str):
                hk = {'raw_path':'raw_sha256', 'raw_original_path':'raw_sha256', 'cnf_path':'cnf_sha256', 'model_path':'model_sha256', 'scope_path':'scope_sha256', 'source_path':'source_sha256'}.get(k, 'sha256')
                if re.fullmatch('[0-9a-f]{64}', str(obj.get(hk, ''))) and v.startswith(('acceleration/', 'docs/', 'build/', 'tools/')):
                    yield v, obj[hk]
            yield from references(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from references(v)

def package_records(obj, origin):
    if isinstance(obj, dict):
        p = obj.get('raw_path', obj.get('raw_original_path'))
        if p and obj.get('gzip_path') and obj.get('gzip_sha256'):
            yield p, dict(manifest_path=origin, raw_sha256=obj.get('raw_sha256'), raw_bytes=obj.get('raw_bytes'), parts=[dict(path=obj['gzip_path'], sha256=obj['gzip_sha256'], bytes=obj.get('gzip_bytes'))])
        if p and isinstance(obj.get('parts'), list) and obj['parts']:
            yield p, dict(manifest_path=origin, raw_sha256=obj.get('raw_sha256'), raw_bytes=obj.get('raw_bytes'), parts=obj['parts'])
        for v in obj.values():
            yield from package_records(v, origin)
    elif isinstance(obj, list):
        for v in obj:
            yield from package_records(v, origin)

def prior_inventory():
    known, records = set(), []
    p, expected = PRIOR, PRIOR_SHA
    while p:
        assert len(records) < 28 and p not in [r['path'] for r in records]
        assert sha(p) == expected
        obj = read(p)
        records.append(dict(path=p, sha256=expected, bytes=safe(p).stat().st_size))
        for entry in obj.get('entries', []):
            if isinstance(entry, dict) and isinstance(entry.get('path'), str):
                known.add(entry['path'])
        for entry in obj.get('prior_recoverable_dependencies', []):
            if isinstance(entry, str): known.add(entry)
            elif isinstance(entry, dict) and isinstance(entry.get('path'), str): known.add(entry['path'])
        parent = obj.get('prior_catalog')
        if not isinstance(parent, dict) or not parent.get('path') or not parent.get('sha256'): break
        p, expected = parent['path'], parent['sha256']
    return known, records

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'acceleration/results')
    assert 'twentyeighth_candidate_inventory' in out.name
    out.mkdir(exist_ok=False, parents=True)
    start = time.monotonic()
    assert sha(CHECKPOINT) == CHECKPOINT_SHA and sha(SNAPSHOT) == SNAPSHOT_SHA
    cp = read(CHECKPOINT)
    ledger = yaml.safe_load(safe(SNAPSHOT).read_bytes())
    assert len(ledger['claims']) == 294
    states = {s:sum(c['status'] == s for c in ledger['claims']) for s in ('VERIFIED', 'CANDIDATE', 'REFUTED')}
    assert states == {'VERIFIED':287, 'CANDIDATE':3, 'REFUTED':4}
    assert all(c['review_state'] == 'CLEAR' for c in ledger['claims'])
    known, prior = prior_inventory()
    selected, pending, rejected, chain, expected = set(), [], {}, [], defaultdict(set)
    previous = None
    for d in REGISTRATIONS:
        s = read(d + '/summary.json')
        before = safe(d + '/CLAIMS.before.yaml').read_bytes()
        after = safe(d + '/CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest() == s['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest() == s['ledger_sha256']
        assert previous is None or before == previous
        previous = after
        chain.append(dict(directory=d, summary_sha256=sha(d+'/summary.json'), before_sha256=s['previous_ledger_sha256'], after_sha256=s['ledger_sha256'], new_claim_ids=s['new_claim_ids']))
    assert hashlib.sha256(previous).hexdigest() == SNAPSHOT_SHA
    newids = [cid for c in chain for cid in c['new_claim_ids']]
    assert len(newids) == len(set(newids)) == 8
    newclaims = [c for c in ledger['claims'] if c['id'] in newids]
    assert sum(c['status']=='VERIFIED' for c in newclaims) == 6
    assert sum(c['status']=='REFUTED' for c in newclaims) == 2

    def add(p, optional=False):
        why = reason(p)
        if why:
            rejected[p] = why
        elif safe(p).is_file():
            selected.add(p)
        elif not optional:
            pending.append(dict(path=p, reason='explicitly allowlisted file absent'))
    for d in DIRECTORIES:
        assert reason(d) is None
        if not safe(d).is_dir():
            pending.append(dict(path=d, reason='explicitly allowlisted cohort absent'))
            continue
        for q in safe(d).rglob('*'):
            if q.is_file(): add(q.relative_to(ROOT).as_posix())
    for p in FILES: add(p)
    for stem in SOURCE_STEMS: add('acceleration/'+stem+'_spec.md', optional=True)
    totalbytes = sum(safe(p).stat().st_size for p in selected)
    assert len(selected) <= MAX_FILES and totalbytes <= MAX_BYTES
    whitelist = dict(schema='WAVE28_EXPLICIT_CANDIDATE_ALLOWLIST_V1', directories=DIRECTORIES,
                     files=sorted(p for p in selected if not any(p.startswith(d+'/') for d in DIRECTORIES)),
                     excluded_tokens=FUTURE_TOKENS, protected_paths=sorted(PROTECTED),
                     source_sha256=sha(Path(__file__).relative_to(ROOT).as_posix()),
                     checkpoint_sha256=CHECKPOINT_SHA, frozen_ledger_sha256=SNAPSHOT_SHA)
    write(out/'allowlist.json', whitelist)
    entries, packages, syntax, omitted_json, references_count = [], defaultdict(list), [], [], 0
    static_imports = set()
    for p in sorted(selected):
        if time.monotonic()-start >= MAX_SECONDS: break
        q = safe(p)
        entry = dict(path=p, sha256=sha(p), bytes=q.stat().st_size,
                     recorded_in_prior_catalog=p in known)
        entries.append(entry)
        if q.suffix == '.json' and q.name not in ('model.json', 'initial_domains.json'):
            try: obj = read(p)
            except (UnicodeError, json.JSONDecodeError): continue
            for name, h in references(obj):
                references_count += 1
                why = reason(name)
                if why: rejected[name] = why
                else: expected[name].add(h)
            for raw, rec in package_records(obj, p): packages[raw].append(rec)
        elif q.suffix == '.json':
            omitted_json.append(p)
        elif q.suffix == '.py':
            try: tree = ast.parse(q.read_bytes())
            except SyntaxError as exc:
                syntax.append(dict(path=p, line=exc.lineno, message=exc.msg)); continue
            for node in ast.walk(tree):
                names = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
                for name in names:
                    rel='acceleration/'+name.split('.')[0]+'.py'
                    if reason(rel) is None and safe(rel).is_file(): static_imports.add(rel)
    actual = {r['path']:r for r in entries}
    large, mismatches = [], []
    for e in entries:
        p, h, size = e['path'], e['sha256'], e['bytes']
        wrong = expected[p] - {h}
        if wrong:
            mismatches.append(dict(path=p, actual_sha256=h, different_recorded_hashes=sorted(wrong), current_hash_also_bound=h in expected[p], note='Historical/corrupt-control references require explicit contextual handling by final catalog; not silently ignored.'))
        if size > LIMIT:
            rec = [r for r in packages[p] if r['raw_sha256']==h and r['raw_bytes']==size]
            gzip_path = p+'.gz'
            gzip_exists = reason(gzip_path) is None and safe(gzip_path).is_file()
            large.append(dict(**e, recovery_status='EXISTING_MANIFEST_METADATA' if rec else 'EXISTING_GZIP_SIBLING' if gzip_exists else 'PACKAGE_OR_RECOVERY_NEEDED', package_records=rec, gzip_sibling=gzip_path if gzip_exists else None, raw_bytes_recovered_by_inventory=False))
    unresolved = sorted(set(expected)-set(actual)-known)
    dependency_groups = defaultdict(list)
    for p in unresolved:
        if p.startswith(('build/', 'external_conway99_research/')): category='LOCAL_TOOL_OR_BUILD_REFERENCE_NOT_READ'
        elif p in selected: category='ALLOWLISTED_NOT_YET_HASHED'
        else: category='OUTSIDE_ALLOWLIST_NOT_READ'
        dependency_groups[category].append(dict(path=p, recorded_sha256=sorted(expected[p])))
    result = dict(schema='WAVE28_CANDIDATE_SELECTION_RECOVERY_INVENTORY_V1',
        status='CANDIDATE_INVENTORY_COMPLETE' if len(entries)==len(selected) else 'CANDIDATE_INVENTORY_PARTIAL_AT_BOUND',
        source_sha256=whitelist['source_sha256'], checkpoint=dict(path=CHECKPOINT,sha256=CHECKPOINT_SHA),
        ledger_cutoff=dict(path=SNAPSHOT,sha256=SNAPSHOT_SHA,claims=294,**states,review_state='ALL_CLEAR'),
        recorded_baseline_commit=cp['source_commit'], git_commands=0, current_git_status_checked=False,
        prior_catalog_chain=prior, registration_chain=chain, new_claim_ids=newids,
        allowlist_sha256=sha((out/'allowlist.json').relative_to(ROOT).as_posix()),
        explicit_directories=DIRECTORIES, explicit_files=whitelist['files'], entries=entries,
        selected_files=len(selected), hashed_files=len(entries), selected_bytes=totalbytes,
        oversized_raw_or_payload_files=large, recorded_hash_conflicts=mismatches, pending=pending,
        rejected_future_or_protected_references=[dict(path=p,reason=v,read_or_hashed=False) for p,v in sorted(rejected.items())],
        reference_bindings_observed=references_count, unique_referenced_paths=len(expected),
        unselected_dependencies=dict(dependency_groups),
        prior_catalog_dependencies=sorted(set(expected)&known),
        unselected_static_imports=sorted(static_imports-set(actual)-known),
        preserved_syntax_failure_sources=syntax, payload_json_not_parsed=omitted_json,
        research_payload_limit_bytes=LIMIT, resource_plan=dict(cooperative_seconds=MAX_SECONDS,max_files=MAX_FILES,max_selected_bytes=MAX_BYTES),
        elapsed_seconds=time.monotonic()-start,
        limitations=['Metadata inventory only; no mathematical approval, code execution, solver, proof replay, raw restoration, Git command, ledger/index mutation, or publication approval.',
                    'Prior-catalog membership is recorded metadata, not a fresh Git availability check.',
                    'Only the explicit cohort/file allowlist is read or hashed; transitive references outside it are reported without opening them.',
                    'Model/initial-domain payload JSON is hashed but not recursively parsed; this is not complete reference-closure validation.',
                    'All raw payloads over10MiB need exact public recovery before publication; existing package metadata is not byte recovery.',
                    'Next64, replacement run_four_builds, draft checker/proof v3/v2, and later affine-GF3 work are excluded.'])
    write(out/'inventory.json', result)
    brief=dict(status=result['status'],inventory_sha256=sha((out/'inventory.json').relative_to(ROOT).as_posix()),
        allowlist_sha256=result['allowlist_sha256'],selected_files=len(selected),selected_bytes=totalbytes,
        oversized=len(large),missing_packages=sum(r['recovery_status']=='PACKAGE_OR_RECOVERY_NEEDED' for r in large),
        pending=len(pending),recorded_hash_conflicts=len(mismatches),unselected_dependencies=len(unresolved),
        elapsed_seconds=result['elapsed_seconds'],native_calls=0,git_commands=0)
    write(out/'summary.json',brief)
    print(json.dumps(brief))

if __name__ == '__main__': main()
