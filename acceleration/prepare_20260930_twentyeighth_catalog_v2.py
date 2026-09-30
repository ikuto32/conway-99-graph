"""Prepare the inventory-schema-aligned wave28 catalog; no catalog execution."""
from pathlib import Path
import ast,hashlib,json
A=Path(__file__).resolve().parent
old=A/'package_20260930_twentyeighth_catalog.py'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='ce6f0846c3a6bba7dafa5ee87f2b3951446c3026cddd1645a55d4e37cdfd0e57'
s=old.read_text(encoding='utf8')
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:100],s.count(a));s=s.replace(a,b)
replace('import package_20260930_twentyeighth_recovery as recovery','import package_20260930_twentyeighth_recovery_v2 as recovery')
replace("'exact_eight_explicit_batch_v3']","'exact_eight_explicit_batch_v3', 'exact_eight_explicit_batch_proofs_v2']")
replace("FILES=['acceleration/package_20260930_twentyeighth_catalog.py', 'acceleration/package_20260930_twentyeighth_catalog_spec.md', 'acceleration/prepare_20260930_twentyeighth_catalog_source.py']", "FILES="+repr([
 'acceleration/package_20260930_twentyeighth_catalog.py','acceleration/package_20260930_twentyeighth_catalog_spec.md','acceleration/prepare_20260930_twentyeighth_catalog_source.py',
 'acceleration/package_20260930_twentyeighth_catalog_v2.py','acceleration/package_20260930_twentyeighth_catalog_v2_spec.md','acceleration/prepare_20260930_twentyeighth_catalog_v2.py',
 'acceleration/inventory_20260930_twentyeighth_candidates.py','acceleration/inventory_20260930_twentyeighth_candidates_spec.md',
 'acceleration/package_20260930_twentyeighth_recovery.py','acceleration/package_20260930_twentyeighth_recovery_spec.md',
 'acceleration/package_20260930_twentyeighth_recovery_v2.py','acceleration/package_20260930_twentyeighth_recovery_v2_spec.md',
 'acceleration/correct_20260930_twentyeighth_recovery_schema.py','acceleration/prepare_20260930_twentyeighth_recovery_helpers.py',
 'acceleration/recover_20260930_twentyeighth_raw_artifacts.py','acceleration/check_20260930_twentyeighth_recovery_controls.py',
 'acceleration/audit_20260930_twentyeighth_checkpoint.py','acceleration/audit_20260930_twentyeighth_checkpoint_spec.md',
 'acceleration/audit_20260930_twentyeighth_checkpoint_v2.py','acceleration/audit_20260930_twentyeighth_checkpoint_v2_spec.md']))
replace('def compressed_json(path, value):', '''def safe_path(p):
    """Validate canonical repository-relative paths before any content read/hash."""
    assert isinstance(p,str)and p and '\\\\'not in p,p
    q=(ROOT/p).resolve()
    assert q.is_relative_to(ROOT)and q.relative_to(ROOT).as_posix()==p,('noncanonical path',p)
    assert not any(token in p for token in FORBIDDEN_TOKENS),('future cohort',p)
    assert not any(p==d or p.startswith(d+'/')for d in FORBIDDEN_DIRECTORIES),p
    assert p not in FORBIDDEN_FILES and not p.startswith(('tools/','external_conway99_research/')),('protected path',p)
    assert q.name.lower()not in {'.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'},p
    assert not p.endswith(('.pem','.key')),p
    return q

def compressed_json(path, value):''')
replace("assert common.digest(ROOT/args.inventory)==args.inventory_sha256", "assert common.digest(safe_path(args.inventory))==args.inventory_sha256")
replace("assert not inventory['pending']and not inventory['hash_mismatches']", "assert not inventory['pending']and not inventory['recorded_hash_conflicts']")
replace("assert inventory['registration_chain']==REGISTRATIONS", """assert [r['directory']for r in inventory['registration_chain']]==REGISTRATIONS
    for r in inventory['registration_chain']:
        d=r['directory'];receipt=json.loads(safe_path(d+'/summary.json').read_bytes())
        assert common.digest(safe_path(d+'/summary.json'))==r['summary_sha256']
        assert receipt['previous_ledger_sha256']==r['before_sha256']and receipt['ledger_sha256']==r['after_sha256']
        assert receipt['new_claim_ids']==r['new_claim_ids']""")
replace("metadata_dirs=[str(Path(args.inventory).parent).replace('\\\\','/'),B+'twentyeighth_raw_recovery',B+'twentyeighth_recovery_controls']+args.extra_dir", "metadata_dirs=[str(Path(args.inventory).parent).replace('\\\\','/'),B+'twentyeighth_raw_recovery',B+'twentyeighth_recovery_controls',B+'twentyeighth_recovery_preparation',B+'twentyeighth_recovery_schema_failure',I+'twentyeighth_checkpoint',I+'twentyeighth_checkpoint_v2']+args.extra_dir")
replace("assert(ROOT/directory).is_dir(),directory\n        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())", "assert safe_path(directory).is_dir(),directory\n        selected.update(common.relative(p)for p in safe_path(directory).rglob('*')if p.is_file())")
start=s.index('    for p in selected:\n');end=s.index("    tracked=set(common.git",start)
s=s[:start]+"    for p in selected:safe_path(p)\n"+s[end:]
replace("assert args.recovery_manifest==recovery_path and common.digest(ROOT/recovery_path)==args.recovery_manifest_sha256", "assert args.recovery_manifest==recovery_path and common.digest(safe_path(recovery_path))==args.recovery_manifest_sha256")
replace("            assert not any(token in p for token in FORBIDDEN_TOKENS)and p not in FORBIDDEN_FILES and not p.startswith(('tools/','external_conway99_research/')),('protected/future reference before read',p)\n            path=ROOT/p;assert path.is_file()and path.resolve().is_relative_to(ROOT),p", "            path=safe_path(p);assert path.is_file(),p")
ast.parse(s)
target=A/'package_20260930_twentyeighth_catalog_v2.py'
with target.open('x',encoding='utf8',newline='\n')as f:f.write(s)
spec=(A/'package_20260930_twentyeighth_catalog_spec.md').read_text(encoding='utf8')
spec+='''

V2 schema alignment before any catalog execution: bind the frozen inventory's
recorded_hash_conflicts and ordered registration records (including each summary,
before/after hashes and IDs). Import the corrected recovery_v2 helper. Preserve
the unexecuted first catalog draft, recovery v1 schema failure, and checkpoint
v1 failure with corrected v2 source/report. Additional metadata directories are
literal named wave28 directories only. Canonical safe_path checks apply before
inventory reads, metadata traversal and all referenced content reads/hashes.
The static preparation performs no Git command, catalog, recovery or math check.
'''
with (A/'package_20260930_twentyeighth_catalog_v2_spec.md').open('x',encoding='utf8',newline='\n')as f:f.write(spec)
print(json.dumps({'source':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'catalog_executions':0}))
