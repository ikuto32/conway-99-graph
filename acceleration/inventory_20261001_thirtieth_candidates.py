"""Explicit wave30 candidate inventory, never mathematical approval."""
from pathlib import Path
from collections import defaultdict
import argparse,ast,hashlib,json,re,time
import yaml
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
N='acceleration/results/20261001_'
I=B+'independent_review/'
J=N+'independent_review/'
DIRECTORIES=['acceleration/results/20261001_exact_eight_case0_core', 'acceleration/results/20261001_exact_eight_case0_core_v2', 'acceleration/results/20261001_exact_eight_prefix64_batch03_build_launcher', 'acceleration/results/20261001_exact_eight_prefix64_batch03_cnfs_part00', 'acceleration/results/20261001_exact_eight_prefix64_batch03_cnfs_part01', 'acceleration/results/20261001_exact_eight_prefix64_batch03_cnfs_part02', 'acceleration/results/20261001_exact_eight_prefix64_batch03_cnfs_part03', 'acceleration/results/20261001_exact_eight_prefix64_batch03_consolidated', 'acceleration/results/20261001_exact_eight_prefix64_batch03_execution', 'acceleration/results/20261001_exact_eight_prefix64_batch03_native_pilot', 'acceleration/results/20261001_exact_eight_prefix64_batch03_native_preflight', 'acceleration/results/20261001_exact_eight_prefix64_batch03_request', 'acceleration/results/20261001_exact_eight_prefix64_batch03_selection', 'acceleration/results/20261001_exact_eight_prefix64_batch04_build_launcher', 'acceleration/results/20261001_exact_eight_prefix64_batch04_cnfs_part00', 'acceleration/results/20261001_exact_eight_prefix64_batch04_cnfs_part01', 'acceleration/results/20261001_exact_eight_prefix64_batch04_cnfs_part02', 'acceleration/results/20261001_exact_eight_prefix64_batch04_cnfs_part03', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_authorization', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_build_launcher', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_cnfs_part00', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_cnfs_part01', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_cnfs_part02', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_cnfs_part03', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_consolidated', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_preparation', 'acceleration/results/20261001_exact_eight_prefix64_batch04_continuation_selection', 'acceleration/results/20261001_exact_eight_prefix64_batch04_execution', 'acceleration/results/20261001_exact_eight_prefix64_batch04_native_pilot', 'acceleration/results/20261001_exact_eight_prefix64_batch04_native_preflight', 'acceleration/results/20261001_exact_eight_prefix64_batch04_request', 'acceleration/results/20261001_exact_eight_prefix64_batch04_selection', 'acceleration/results/20261001_exact_eight_prefix64_batch05_build_launcher', 'acceleration/results/20261001_exact_eight_prefix64_batch05_cnfs_part00', 'acceleration/results/20261001_exact_eight_prefix64_batch05_cnfs_part01', 'acceleration/results/20261001_exact_eight_prefix64_batch05_cnfs_part02', 'acceleration/results/20261001_exact_eight_prefix64_batch05_cnfs_part03', 'acceleration/results/20261001_exact_eight_prefix64_batch05_consolidated', 'acceleration/results/20261001_exact_eight_prefix64_batch05_execution', 'acceleration/results/20261001_exact_eight_prefix64_batch05_native_pilot', 'acceleration/results/20261001_exact_eight_prefix64_batch05_native_preflight', 'acceleration/results/20261001_exact_eight_prefix64_batch05_request', 'acceleration/results/20261001_exact_eight_prefix64_batch05_selection', 'acceleration/results/20261001_independent_review/exact_eight_case0_core', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch03_cnfs_v3', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch03_object_calibration', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch03_proofs', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch03_selection', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch04_cnfs_v4', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch04_continuation_preflight', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch04_object_calibration', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch04_proofs', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch04_selection', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_cnfs_v3', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_object_calibration', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_proofs', 'acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_selection', 'acceleration/results/20261001_independent_review/reimbayev_z82', 'acceleration/results/20261001_independent_review/thirtieth_followup_registrar_source_review', 'acceleration/results/20261001_independent_review/thirtieth_registrar_source_review', 'acceleration/results/20261001_independent_review/thirtieth_registrar_source_review_v2', 'acceleration/results/20261001_independent_review/thirtieth_registrar_source_review_v3', 'acceleration/results/20261001_reimbayev_seven_access', 'acceleration/results/20261001_reimbayev_z82_overlap', 'acceleration/results/20261001_reimbayev_z82_overlap_v2', 'acceleration/results/20261001_thirtieth_followup_registrar_preparation', 'acceleration/results/20261001_thirtieth_followup_registration', 'acceleration/results/20261001_thirtieth_initial_registrar_preparation', 'acceleration/results/20261001_thirtieth_initial_registration', 'acceleration/results/20261001_thirtieth_inventory_preparation_correction', 'acceleration/results/20261001_thirtieth_registrar_preparation', 'acceleration/results/20261001_thirtieth_registrar_v2_preparation', 'acceleration/results/20261001_thirtieth_registrar_v3_preparation']
FILES=['acceleration/audit_20261001_exact_eight_case0_core.py', 'acceleration/audit_20261001_exact_eight_checkpoint_continuation.py', 'acceleration/audit_20261001_exact_eight_checkpoint_records.py', 'acceleration/audit_20261001_exact_eight_explicit_batch_v4.py', 'acceleration/audit_20261001_reimbayev_z82.py', 'acceleration/audit_20261001_thirtieth_registrar_source.py', 'acceleration/audit_20261001_thirtieth_registrar_source_v2.py', 'acceleration/audit_20261001_thirtieth_registrar_source_v3.py', 'acceleration/bind_20261001_exact_eight_case0_core.py', 'acceleration/bind_20261001_reimbayev_z82.py', 'acceleration/check_20261001_exact_eight_batch04_continuation_preparation.py', 'acceleration/continue_20261001_exact_eight_batch04.py', 'acceleration/freeze_20261001_exact_eight_prefix64_batch03_request.py', 'acceleration/freeze_20261001_exact_eight_prefix64_request.py', 'acceleration/inventory_20261001_thirtieth_candidates.py', 'acceleration/prepare_20261001_thirtieth_followup_registrar.py', 'acceleration/prepare_20261001_thirtieth_initial_registrar.py', 'acceleration/prepare_20261001_thirtieth_inventory_source.py', 'acceleration/prepare_20261001_thirtieth_inventory_source_v2.py', 'acceleration/prepare_20261001_thirtieth_registrar.py', 'acceleration/prepare_20261001_thirtieth_registrar_v2.py', 'acceleration/prepare_20261001_thirtieth_registrar_v3.py', 'acceleration/record_20261001_thirtieth_checkpoint.py', 'acceleration/record_20261001_thirtieth_initial_checkpoint.py', 'acceleration/register_20261001_thirtieth_batches03_05.py', 'acceleration/register_20261001_thirtieth_batches03_05_v2.py', 'acceleration/register_20261001_thirtieth_batches03_05_v3.py', 'acceleration/register_20261001_thirtieth_followup_claims.py', 'acceleration/register_20261001_thirtieth_initial_claims.py', 'acceleration/results/20261001_resume/claims_at_thirtieth_milestone.yaml', 'acceleration/results/20261001_resume/thirtieth_initial_checkpoint.json', 'acceleration/results/20261001_resume/thirtieth_milestone_checkpoint.json', 'acceleration/theory_20261001_exact_eight_case0_core.py', 'acceleration/theory_20261001_exact_eight_case0_core_v2.py', 'acceleration/theory_20261001_exact_eight_prefix64_batch03_plan.md', 'acceleration/theory_20261001_exact_eight_prefix64_batch04_continuation_plan.md', 'acceleration/theory_20261001_exact_eight_prefix64_batch04_plan.md', 'acceleration/theory_20261001_exact_eight_prefix64_batch05_plan.md', 'acceleration/theory_20261001_reimbayev_z82_overlap.py', 'acceleration/theory_20261001_reimbayev_z82_overlap_v2.py', 'docs/AUDIT_20261001_REIMBAYEV_Z82.md', 'docs/LITERATURE_20261001_REIMBAYEV_SEVEN_Z82.md', 'docs/RESEARCH_20261001_THIRTIETH_WAVE.md', 'docs/RESULT_20261001_EXACT_EIGHT_CASE0_CORE.md', 'docs/REVIEW_PLAN_20261001_EXACT_EIGHT_CHECKPOINT_CONTINUATION.md']
SOURCE_STEMS=['audit_20261001_exact_eight_case0_core', 'audit_20261001_exact_eight_checkpoint_continuation', 'audit_20261001_exact_eight_checkpoint_records', 'audit_20261001_exact_eight_explicit_batch_v4', 'audit_20261001_reimbayev_z82', 'audit_20261001_thirtieth_registrar_source', 'audit_20261001_thirtieth_registrar_source_v2', 'audit_20261001_thirtieth_registrar_source_v3', 'bind_20261001_exact_eight_case0_core', 'bind_20261001_reimbayev_z82', 'check_20261001_exact_eight_batch04_continuation_preparation', 'continue_20261001_exact_eight_batch04', 'freeze_20261001_exact_eight_prefix64_batch03_request', 'freeze_20261001_exact_eight_prefix64_request', 'inventory_20261001_thirtieth_candidates', 'prepare_20261001_thirtieth_followup_registrar', 'prepare_20261001_thirtieth_initial_registrar', 'prepare_20261001_thirtieth_inventory_source', 'prepare_20261001_thirtieth_inventory_source_v2', 'prepare_20261001_thirtieth_registrar', 'prepare_20261001_thirtieth_registrar_v2', 'prepare_20261001_thirtieth_registrar_v3', 'record_20261001_thirtieth_checkpoint', 'record_20261001_thirtieth_initial_checkpoint', 'register_20261001_thirtieth_batches03_05', 'register_20261001_thirtieth_batches03_05_v2', 'register_20261001_thirtieth_batches03_05_v3', 'register_20261001_thirtieth_followup_claims', 'register_20261001_thirtieth_initial_claims', 'theory_20261001_exact_eight_case0_core', 'theory_20261001_exact_eight_case0_core_v2', 'theory_20261001_reimbayev_z82_overlap', 'theory_20261001_reimbayev_z82_overlap_v2']
REGISTRATIONS=['acceleration/results/20261001_thirtieth_initial_registration', 'acceleration/results/20261001_thirtieth_followup_registration']
CHECKPOINT='acceleration/results/20261001_resume/thirtieth_milestone_checkpoint.json'
SNAPSHOT='acceleration/results/20261001_resume/claims_at_thirtieth_milestone.yaml'
CHECKPOINT_SHA=None
SNAPSHOT_SHA=None
PRIOR='acceleration/results/20261001_twentyninth_artifact_packaging/catalog.json'
PRIOR_SHA='22a5e3b558a7b2104ae48d939d4bd116d03371333247c736e06a4e279b8fa0a5'
ORIGIN_PINS={'acceleration/inventory_20261001_twentyninth_candidates.py': 'b8deee06e2df3ea0007b7269238cf07589429c67af06d05fbb473179ff4ca091', 'acceleration/prepare_20261001_thirtieth_inventory_source_v2.py': 'f862c542eef1df62d86fc0d895d2a691a9aaedcf3931a136352e180bedb7ac47'}
LIMIT=10485760
MAX_FILES=20000
MAX_BYTES=4294967296
MAX_SECONDS=120
PROTECTED={'CLAIMS.yaml', 'PROMPT.md', 'acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log'}
FUTURE_TOKENS=('batch06', 'batch07', 'batch08', 'batch09', 'batch10', 'batch11', 'n3_hamming', 'three_center', 'thirtyfirst', 'thirtieth_raw_recovery', 'thirtieth_recovery', 'reproducing_20261001_thirtieth')
ACTIVE_OUTPUT=None

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
        assert len(records) < 31 and p not in [r['path'] for r in records]
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
    global CHECKPOINT_SHA,SNAPSHOT_SHA,ACTIVE_OUTPUT
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--checkpoint-sha256', required=True)
    ap.add_argument('--ledger-sha256', required=True)
    args = ap.parse_args()
    assert re.fullmatch('[0-9a-f]{64}',args.checkpoint_sha256)
    assert re.fullmatch('[0-9a-f]{64}',args.ledger_sha256)
    CHECKPOINT_SHA,SNAPSHOT_SHA=args.checkpoint_sha256,args.ledger_sha256
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'acceleration/results')
    assert 'thirtieth_candidate_inventory' in out.name
    out.mkdir(exist_ok=False, parents=True)
    ACTIVE_OUTPUT=out
    start = time.monotonic()
    for p,h in ORIGIN_PINS.items(): assert sha(p)==h,(p,h)
    assert sha(CHECKPOINT) == CHECKPOINT_SHA and sha(SNAPSHOT) == SNAPSHOT_SHA
    cp = read(CHECKPOINT)
    ledger = yaml.safe_load(safe(SNAPSHOT).read_bytes())
    assert len(ledger['claims']) == 308
    states = {s:sum(c['status'] == s for c in ledger['claims']) for s in ('VERIFIED', 'CANDIDATE', 'REFUTED')}
    assert states == {'VERIFIED':301, 'CANDIDATE':3, 'REFUTED':4}
    assert all(c['review_state'] == 'CLEAR' for c in ledger['claims'])
    assert cp['claim_population']==308 and cp['claim_status_counts']==states
    assert cp['ledger_snapshot_sha256']==SNAPSHOT_SHA
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
    assert sum(c['status']=='VERIFIED' for c in newclaims) == 8
    assert sum(c['status']=='REFUTED' for c in newclaims) == 0
    assert len(newclaims)==8 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in newclaims)
    assert set(cp['new_verified_ids'])==set(newids)

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
    whitelist = dict(schema='WAVE30_EXPLICIT_CANDIDATE_ALLOWLIST_V1', directories=DIRECTORIES,
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
    result = dict(schema='WAVE30_CANDIDATE_SELECTION_RECOVERY_INVENTORY_V1',
        status='CANDIDATE_INVENTORY_COMPLETE' if len(entries)==len(selected) else 'CANDIDATE_INVENTORY_PARTIAL_AT_BOUND',
        source_sha256=whitelist['source_sha256'], origin_pins=ORIGIN_PINS, checkpoint=dict(path=CHECKPOINT,sha256=CHECKPOINT_SHA),
        ledger_cutoff=dict(path=SNAPSHOT,sha256=SNAPSHOT_SHA,claims=308,**states,review_state='ALL_CLEAR'),
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
                    'Batch06 and later allocations and unrelated structural probes are excluded; recovery/publication audit and reproduction guide are later explicit supplements, not scientific inventory inputs.'])
    write(out/'inventory.json', result)
    brief=dict(status=result['status'],inventory_sha256=sha((out/'inventory.json').relative_to(ROOT).as_posix()),
        allowlist_sha256=result['allowlist_sha256'],selected_files=len(selected),selected_bytes=totalbytes,
        oversized=len(large),missing_packages=sum(r['recovery_status']=='PACKAGE_OR_RECOVERY_NEEDED' for r in large),
        pending=len(pending),recorded_hash_conflicts=len(mismatches),unselected_dependencies=len(unresolved),
        elapsed_seconds=result['elapsed_seconds'],native_calls=0,git_commands=0)
    write(out/'summary.json',brief)
    print(json.dumps(brief))

if __name__ == '__main__':
    try: main()
    except BaseException as exc:
        if ACTIVE_OUTPUT is not None and not (ACTIVE_OUTPUT/'failure.json').exists():
            write(ACTIVE_OUTPUT/'failure.json',dict(status='WAVE30_INVENTORY_FAILED',exception=type(exc).__name__,message=str(exc),checkpoint_sha256=CHECKPOINT_SHA,ledger_sha256=SNAPSHOT_SHA,mathematical_approval=False))
        raise
