"""Source-only wave28 catalog controls; no catalog/Git/recovery execution."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B='acceleration/results/20260930_'
SOURCE='acceleration/package_20260930_twentyeighth_catalog_v2.py'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with (ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
assert sha(SOURCE)=='ce54f25d65d8a550682d86f6df84b19afbbd1880f3d7df8fe227ea925f2de2eb'
tree=ast.parse((ROOT/SOURCE).read_text(encoding='utf8'))
env={'ROOT':ROOT,'Path':Path}
for node in tree.body:
    if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ['FORBIDDEN_DIRECTORIES','FORBIDDEN_FILES','FORBIDDEN_TOKENS','FILES','REGISTRATIONS']for t in node.targets):exec(compile(ast.Module([node],[]),SOURCE,'exec'),env)
    if isinstance(node,ast.FunctionDef)and node.name=='safe_path':exec(compile(ast.Module([node],[]),SOURCE,'exec'),env)
safe=env['safe_path'];controls=[]
for p in [SOURCE,B+'twentyeighth_raw_recovery/manifest.json',B+'independent_review/windows_job_assignment_race/summary.json']:
    assert safe(p)==(ROOT/p).resolve();controls.append({'control':'valid_canonical_path','path':p,'accepted':True})
for p in ['PROMPT.md','tools/a','external_conway99_research/a',B+'independent_review/hadamard_oriented_unknown/process.stdout.log','../outside.json','acceleration/../CLAIMS.yaml','acceleration\\a.json','C:/outside.json','acceleration/.env','acceleration/id_rsa','acceleration/a.key',B+'exact_eight_next64_selection/selection.json',B+'exact_eight_four_builds_plan_v2/summary.json',B+'independent_review/four_serial_build_engineering/summary.json',B+'sizeclass16_affine_gram_gf3/summary.json','acceleration/audit_20260930_exact_eight_explicit_batch_v3.py','acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2.py']:
    try:safe(p)
    except AssertionError:controls.append({'control':'protected_future_or_noncanonical_path','path':p,'rejected':True})
    else:raise AssertionError(('accepted malformed path',p))
inventory_path=B+'twentyeighth_candidate_inventory/inventory.json'
assert sha(inventory_path)=='0057d4f0101eb1e56516ade234840defb4be5b17d2b0a2b5e35bd85491b48ce1'
inventory=read(inventory_path)
assert not inventory['pending']and not inventory['recorded_hash_conflicts']
assert [r['directory']for r in inventory['registration_chain']]==env['REGISTRATIONS']
ids=[]
for r in inventory['registration_chain']:
    receipt=read(r['directory']+'/summary.json')
    assert sha(r['directory']+'/summary.json')==r['summary_sha256']
    assert receipt['previous_ledger_sha256']==r['before_sha256']and receipt['ledger_sha256']==r['after_sha256']
    assert receipt['new_claim_ids']==r['new_claim_ids'];ids+=r['new_claim_ids']
assert ids==inventory['new_claim_ids']and len(ids)==8
for r in inventory['entries']:safe(r['path'])
for p in env['FILES']:assert safe(p).is_file(),p
manifest=B+'twentyeighth_raw_recovery/manifest.json'
assert sha(manifest)=='33b00a791e57a732a27d18061c52f1ac6b3e71d964d9bf03c1e986ae12c82c89'
m=read(manifest);assert len(m['records'])==47 and sum(r['bytes']for r in m['records'])==524689195
out=B+'twentyeighth_catalog_source_preparation';(ROOT/out).mkdir(exist_ok=False)
inputs={p:sha(p)for p in env['FILES']+[inventory_path,manifest,'acceleration/package_20260930_eighth_catalog.py',Path(__file__).relative_to(ROOT).as_posix()]}
save(out+'/summary.json',dict(status='TWENTYEIGHTH_CATALOG_SOURCE_PREPARATION_PASS',inputs_sha256=inputs,source_ast_checked=True,controls=controls,controls_count=len(controls),inventory_schema_checked=True,inventory_entries=len(inventory['entries']),new_claim_ids=ids,recovery_manifest_schema_checked=True,recovery_streams_executed=0,catalog_executions=0,git_commands=0,native_calls=0,mathematical_verification=False,required_final_command=['python','-B',SOURCE,'--inventory',inventory_path,'--inventory-sha256',sha(inventory_path),'--recovery-manifest',manifest,'--recovery-manifest-sha256',sha(manifest),'--out',B+'twentyeighth_artifact_packaging','--extra-dir',out,'--extra-file',Path(__file__).relative_to(ROOT).as_posix()]))
print(json.dumps({'summary':out+'/summary.json','sha256':sha(out+'/summary.json'),'catalog_executions':0,'controls':len(controls)}))
