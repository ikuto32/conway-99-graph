"""Wave29 source-only draft for an explicit candidate inventory. No Git, tool execution, or proof replay."""
from pathlib import Path
from collections import defaultdict
import argparse, ast, hashlib, json, re, time
import yaml

ROOT = Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
N='acceleration/results/20261001_'
I=B+'independent_review/'
J=N+'independent_review/'
DIRECTORIES=[
 B+'exact_eight_next64_selection',B+'exact_eight_next64_launch_preparation',
 B+'exact_eight_next64_cnfs_part00',B+'exact_eight_next64_cnfs_part01',
 B+'exact_eight_next64_cnfs_part02',B+'exact_eight_next64_cnfs_part03',
 B+'exact_eight_next64_consolidated',B+'exact_eight_next64_native_preflight',B+'exact_eight_next64_native_pilot',
 I+'exact_eight_next64_selection',I+'exact_eight_next64_cnfs_v3',I+'exact_eight_next64_object_calibration',I+'exact_eight_next64_proofs',
 B+'exact_eight_four_builds_plan',B+'exact_eight_four_builds_plan_v2',
 B+'exact_eight_four_builds_preparation',B+'exact_eight_four_builds_preparation_v2',B+'exact_eight_four_builds_v2_correction',I+'four_serial_build_engineering',
 B+'exact_eight_prefix64_source_preparation',I+'exact_eight_prefix64_source_review',
 N+'exact_eight_prefix64_batch02_request',N+'exact_eight_prefix64_batch02_selection',
 N+'exact_eight_prefix64_batch02_execution',N+'exact_eight_prefix64_batch02_build_launcher',
 N+'exact_eight_prefix64_batch02_cnfs_part00',N+'exact_eight_prefix64_batch02_cnfs_part01',
 N+'exact_eight_prefix64_batch02_cnfs_part02',N+'exact_eight_prefix64_batch02_cnfs_part03',N+'exact_eight_prefix64_batch02_consolidated',
 J+'exact_eight_prefix64_batch02_selection',
]
# Terminal batch02 outputs are now independently frozen; no later batch is selected.
BATCH02_TERMINAL_DIRECTORIES=[
 J+'exact_eight_prefix64_batch02_cnfs_v3',J+'exact_eight_prefix64_batch02_object_calibration',
 N+'exact_eight_prefix64_batch02_native_preflight',N+'exact_eight_prefix64_batch02_native_pilot',
 J+'exact_eight_prefix64_batch02_proofs',
]
FILES=[
 'acceleration/select_20260930_exact_eight_next64.py',
 'acceleration/theory_20260930_exact_eight_next64_plan.md',
 'acceleration/audit_20260930_exact_eight_next64_selection.py',
 'acceleration/audit_20260930_exact_eight_next64_selection_spec.md',
 'acceleration/prepare_20260930_exact_eight_next64_launch.py',
 'acceleration/execute_20260930_exact_eight_next64_builds.py',
 'acceleration/run_20260930_exact_eight_four_builds.py',
 'acceleration/run_20260930_exact_eight_four_builds_spec.md',
 'acceleration/run_20260930_exact_eight_four_builds_v2.py',
 'acceleration/run_20260930_exact_eight_four_builds_v2_spec.md',
 'acceleration/check_20260930_exact_eight_four_builds_preparation.py',
 'acceleration/check_20260930_exact_eight_four_builds_preparation_v2.py',
 'acceleration/audit_20260930_four_serial_build_engineering.py',
 'acceleration/audit_20260930_four_serial_build_engineering_spec.md',
 'acceleration/select_20260930_exact_eight_prefix64.py',
 'acceleration/select_20260930_exact_eight_prefix64_spec.md',
 'acceleration/check_20260930_exact_eight_prefix64_preparation.py',
 'acceleration/audit_20261001_exact_eight_prefix64_selection.py',
 'acceleration/audit_20261001_exact_eight_prefix64_selection_spec.md',
 'docs/REVIEW_20260930_EXACT_EIGHT_PREFIX64_SOURCE.md',
 'acceleration/theory_20261001_exact_eight_prefix64_batch02_plan.md',
 'acceleration/audit_20260930_exact_eight_explicit_batch_v3.py',
 'acceleration/audit_20260930_exact_eight_explicit_batch_v3_spec.md',
 'acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2.py',
 'acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2_spec.md',
]

DIRECTORIES += BATCH02_TERMINAL_DIRECTORIES + [
 B+'exact_eight_next64_launch_execution', B+'exact_eight_next64_build_launcher',
 I+'exact_eight_next64_proof_preparation', B+'sizeclass16_affine_gram_gf3',
 I+'sizeclass16_gf3_affine_weights', N+'exact_eight_uniform_gram',
 J+'exact_eight_uniform_gram', B+'twentyninth_initial_registration_preparation',
]
FILES=[p for p in FILES if p!='acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2_spec.md']+[
 'docs/AUDIT_20260930_EXACT_EIGHT_EXPLICIT_BATCH_PROOFS_V2.md',
 'acceleration/allowlist_20261001_twentyninth_candidate_seed.py',
 'acceleration/allowlist_20261001_twentyninth_candidate_seed_v2.py',
]
CHECKPOINT=N+'resume/twentyninth_milestone_checkpoint.json'
SNAPSHOT=N+'resume/claims_at_twentyninth_milestone.yaml'
CHECKPOINT_SHA=None
SNAPSHOT_SHA=None
PRIOR=B+'twentyeighth_artifact_packaging/catalog.json'
PRIOR_SHA='1dc941ddb899393f5d7d570f266cad6bc6205e64f3db13b4affe870f31de3586'
REGISTRATIONS=[B+'twentyninth_initial_registration',N+'twentyninth_followup_registration']
DIRECTORIES += REGISTRATIONS
SOURCE_STEMS=[
 'theory_20260930_sizeclass16_affine_gram_gf3','audit_20260930_sizeclass16_gf3_weights',
 'theory_20261001_exact_eight_uniform_gram','audit_20261001_exact_eight_uniform_gram',
 'register_20260930_twentyninth_initial_claims','register_20261001_twentyninth_followup_claims',
 'record_20261001_twentyninth_checkpoint','plan_20261001_twentyninth_replay',
 'inventory_20261001_twentyninth_candidates',
]
FILES += ['acceleration/'+s+'.py' for s in SOURCE_STEMS] + [
 CHECKPOINT,SNAPSHOT,N+'resume/twentyninth_replay_plan.json',
 N+'resume/twentyninth_process_snapshot.stdout.log',N+'resume/twentyninth_process_snapshot.stderr.log',
 'docs/RESEARCH_20261001_TWENTYNINTH_WAVE.md',
]
# Only explicitly named sibling specs; no discovery of later source versions.
SOURCE_STEMS=sorted(set(SOURCE_STEMS+[Path(p).stem for p in FILES if p.startswith('acceleration/') and p.endswith('.py')]))
DIRECTORIES=sorted(set(DIRECTORIES))
FILES=sorted(set(FILES))
ORIGIN_PINS={
 'acceleration/inventory_20260930_twentyeighth_candidates.py':'291862736d7a95617d302ca153cb58cb39de5c5c1c0d73c250c90d166bb97485',
 'acceleration/allowlist_20261001_twentyninth_candidate_seed.py':'83790b7b011494ea5491b05bcb6e3320d2a4cb49cd8035617b4f2bb7a8d4653f',
 'acceleration/allowlist_20261001_twentyninth_candidate_seed_v2.py':'973aaf7a00ab039c6cb30b35181bd5465ce9b58df9d8e5aaad28f19d6d91c691',
}
LIMIT=10*1024**2
MAX_FILES=20000
MAX_BYTES=4*1024**3
MAX_SECONDS=120
PROTECTED={'PROMPT.md','CLAIMS.yaml',I+'hadamard_oriented_unknown/process.stdout.log'}
FUTURE_TOKENS=('batch03','batch04','batch05','prefix64_batch03','twentyninth_recovery',
               'twentyninth_raw_recovery','reproducing_20261001_twentyninth','thirtieth')
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
        assert len(records) < 29 and p not in [r['path'] for r in records]
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
    assert 'twentyninth_candidate_inventory' in out.name
    out.mkdir(exist_ok=False, parents=True)
    ACTIVE_OUTPUT=out
    start = time.monotonic()
    for p,h in ORIGIN_PINS.items(): assert sha(p)==h,(p,h)
    assert sha(CHECKPOINT) == CHECKPOINT_SHA and sha(SNAPSHOT) == SNAPSHOT_SHA
    cp = read(CHECKPOINT)
    ledger = yaml.safe_load(safe(SNAPSHOT).read_bytes())
    assert len(ledger['claims']) == 300
    states = {s:sum(c['status'] == s for c in ledger['claims']) for s in ('VERIFIED', 'CANDIDATE', 'REFUTED')}
    assert states == {'VERIFIED':293, 'CANDIDATE':3, 'REFUTED':4}
    assert all(c['review_state'] == 'CLEAR' for c in ledger['claims'])
    assert cp['claim_population']==300 and cp['claim_status_counts']==states
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
    assert len(newids) == len(set(newids)) == 6
    newclaims = [c for c in ledger['claims'] if c['id'] in newids]
    assert sum(c['status']=='VERIFIED' for c in newclaims) == 6
    assert sum(c['status']=='REFUTED' for c in newclaims) == 0
    assert len(newclaims)==6 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in newclaims)
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
    whitelist = dict(schema='WAVE29_EXPLICIT_CANDIDATE_ALLOWLIST_V1', directories=DIRECTORIES,
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
    result = dict(schema='WAVE29_CANDIDATE_SELECTION_RECOVERY_INVENTORY_V1',
        status='CANDIDATE_INVENTORY_COMPLETE' if len(entries)==len(selected) else 'CANDIDATE_INVENTORY_PARTIAL_AT_BOUND',
        source_sha256=whitelist['source_sha256'], origin_pins=ORIGIN_PINS, checkpoint=dict(path=CHECKPOINT,sha256=CHECKPOINT_SHA),
        ledger_cutoff=dict(path=SNAPSHOT,sha256=SNAPSHOT_SHA,claims=300,**states,review_state='ALL_CLEAR'),
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
                    'Batch03 and later allocations are excluded; recovery/publication audit and reproduction guide are later explicit supplements, not scientific inventory inputs.'])
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
            write(ACTIVE_OUTPUT/'failure.json',dict(status='WAVE29_INVENTORY_FAILED',exception=type(exc).__name__,message=str(exc),checkpoint_sha256=CHECKPOINT_SHA,ledger_sha256=SNAPSHOT_SHA,mathematical_approval=False))
        raise
