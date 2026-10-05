"""Static/receipt checks of frozen catalog v3 without importing/executing it."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
SOURCE='acceleration/package_20260930_twentyeighth_catalog_v3.py'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def validate(u,inv,old,new):
    assert u['inventory_sha256']==sha(u['inventory_path'])
    assert u['path']=='docs/REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md'
    assert u['scientific_entry_overrides']==0 and u['metadata_entry_overrides']==1
    assert hashlib.sha256(old).hexdigest()==u['old_sha256']and len(old)==u['old_bytes']
    assert hashlib.sha256(new).hexdigest()==u['new_sha256']and len(new)==u['new_bytes']
    r=[r for r in inv['entries']if r['path']==u['path']];assert len(r)==1
    assert r[0]['sha256']==u['old_sha256']and r[0]['bytes']==u['old_bytes']
assert sha(SOURCE)=='efb10d9c03602353a0ff6497d4ed576c32be7eee5499394d3ea2730bcf5d84dd'
ast.parse((ROOT/SOURCE).read_text(encoding='utf8'))
update=B+'twentyeighth_guide_update/receipt.json';assert sha(update)=='ee492b54647b4bbe842df774f336d9332034a7b6ee2953b362bd06b20e96be99'
u=read(update);inv=read(u['inventory_path']);old=(ROOT/(B+'twentyeighth_guide_update/previous_guide.md')).read_bytes();new=(ROOT/u['path']).read_bytes()
validate(u,inv,old,new)
addition=(ROOT/(B+'twentyeighth_guide_update/recovery_addition.md')).read_bytes()
assert new.count(addition)==1 and new.replace(addition,b'',1)==old
controls=[]
for key,value in [('scientific_entry_overrides',1),('metadata_entry_overrides',2),('path','docs/RESEARCH_20260930_TWENTYEIGHTH_WAVE.md'),('old_sha256','0'*64),('new_sha256','0'*64),('old_bytes',len(old)+1),('new_bytes',len(new)+1)]:
    changed=dict(u);changed[key]=value
    try:validate(changed,inv,old,new)
    except AssertionError:controls.append({'field':key,'rejected':True})
    else:raise AssertionError(('control accepted',key))
prep=B+'twentyeighth_catalog_source_preparation/summary.json';assert sha(prep)=='bcea09ed695ae91496a5595ef83a6aafac6dd9f3758255ffa1742ab67909f7d5'
previous=read(prep);command=list(previous['required_final_command']);command[2]=SOURCE
out=B+'twentyeighth_catalog_v3_source_preparation';(ROOT/out).mkdir(exist_ok=False)
command+=['--extra-dir',out,'--extra-file',Path(__file__).relative_to(ROOT).as_posix()]
paths=[SOURCE,SOURCE.replace('.py','_spec.md'),'acceleration/prepare_20260930_twentyeighth_catalog_v3.py',Path(__file__).relative_to(ROOT).as_posix(),update,prep,u['inventory_path'],B+'twentyeighth_raw_recovery/manifest.json']
result=dict(status='TWENTYEIGHTH_CATALOG_V3_SOURCE_PREPARATION_PASS',inputs_sha256={p:sha(p)for p in paths},source_ast_checked=True,metadata_overrides=1,scientific_overrides=0,old_guide_literal_recovered=True,controls=controls,prior_safe_path_controls=previous['controls_count'],catalog_executions=0,git_commands=0,recovery_streams_executed=0,mathematical_verification=False,required_final_command=command)
with(ROOT/(out+'/summary.json')).open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'summary':out+'/summary.json','sha256':sha(out+'/summary.json'),'catalog_executions':0}))
