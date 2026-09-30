"""Add the root-authenticated one-file guide update to unexecuted catalog v2."""
from pathlib import Path
import ast,hashlib,json
A=Path(__file__).resolve().parent
old=A/'package_20260930_twentyeighth_catalog_v2.py'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='ce54f25d65d8a550682d86f6df84b19afbbd1880f3d7df8fe227ea925f2de2eb'
s=old.read_text(encoding='utf8')
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:100],s.count(a));s=s.replace(a,b)
replace('FORBIDDEN_DIRECTORIES=',"FILES += ['acceleration/package_20260930_twentyeighth_catalog_v3.py','acceleration/package_20260930_twentyeighth_catalog_v3_spec.md','acceleration/prepare_20260930_twentyeighth_catalog_v3.py','acceleration/record_20260930_twentyeighth_guide_update.py','acceleration/check_20260930_twentyeighth_catalog_preparation.py']\nGUIDE_UPDATE=B+'twentyeighth_guide_update/receipt.json'\nGUIDE_UPDATE_SHA='ee492b54647b4bbe842df774f336d9332034a7b6ee2953b362bd06b20e96be99'\nFORBIDDEN_DIRECTORIES=")
replace("    inventory_entries=inventory['entries'];assert len({r['path']for r in inventory_entries})==len(inventory_entries)","""    inventory_entries=inventory['entries'];assert len({r['path']for r in inventory_entries})==len(inventory_entries)
    assert common.digest(safe_path(GUIDE_UPDATE))==GUIDE_UPDATE_SHA
    guide_update=json.loads(safe_path(GUIDE_UPDATE).read_bytes())
    assert guide_update['inventory_path']==args.inventory and guide_update['inventory_sha256']==args.inventory_sha256
    assert guide_update['scientific_entry_overrides']==0 and guide_update['metadata_entry_overrides']==1
    guide_path=guide_update['path'];assert guide_path=='docs/REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md'
    guide_previous=B+'twentyeighth_guide_update/previous_guide.md'
    assert common.digest(safe_path(guide_previous))==guide_update['old_sha256']and safe_path(guide_previous).stat().st_size==guide_update['old_bytes']
    assert common.digest(safe_path(guide_path))==guide_update['new_sha256']and safe_path(guide_path).stat().st_size==guide_update['new_bytes']
    old_guide_rows=[r for r in inventory_entries if r['path']==guide_path];assert len(old_guide_rows)==1
    assert old_guide_rows[0]['sha256']==guide_update['old_sha256']and old_guide_rows[0]['bytes']==guide_update['old_bytes']""")
replace("I+'twentyeighth_checkpoint_v2']+args.extra_dir", "I+'twentyeighth_checkpoint_v2',B+'twentyeighth_guide_update',B+'twentyeighth_catalog_source_preparation']+args.extra_dir")
replace("    def check(name,expected,origin,archive=False):", """    def check(name,expected,origin,archive=False):
        # Exactly one old inventory reference points to its preserved historical bytes.
        if origin==args.inventory and name==guide_path and expected==guide_update['old_sha256']:
            name=guide_previous""")
replace("    for row in inventory_entries:\n        assert info(row['path'])['sha256']==row['sha256']and info(row['path'])['bytes']==row['bytes'],'frozen inventory bytes'", """    for row in inventory_entries:
        p=guide_previous if row['path']==guide_path else row['path']
        assert info(p)['sha256']==row['sha256']and info(p)['bytes']==row['bytes'],'frozen inventory bytes'
    assert info(guide_path)['sha256']==guide_update['new_sha256']and info(guide_path)['bytes']==guide_update['new_bytes']""")
replace("candidate_inventory=dict(path=args.inventory,sha256=args.inventory_sha256),normalized_recovery=", "candidate_inventory=dict(path=args.inventory,sha256=args.inventory_sha256),metadata_overrides=[dict(receipt_path=GUIDE_UPDATE,receipt_sha256=GUIDE_UPDATE_SHA,path=guide_path,old_sha256=guide_update['old_sha256'],new_sha256=guide_update['new_sha256'],historical_path=guide_previous)],normalized_recovery=")
ast.parse(s)
target=A/'package_20260930_twentyeighth_catalog_v3.py'
with target.open('x',encoding='utf8',newline='\n')as f:f.write(s)
spec=(A/'package_20260930_twentyeighth_catalog_v2_spec.md').read_text(encoding='utf8')+'''

V3 adds exactly one authorized metadata update. Receipt
results/20260930_twentyeighth_guide_update/receipt.json, SHA
ee492b54647b4bbe842df774f336d9332034a7b6ee2953b362bd06b20e96be99,
binds original inventoried guide db2f23d9830708be66c9012001d5b82862a8dc59c96fc4e6aaed415274e43651
and final guide95b76d5f21e15d90ebc036a36e7f47eabaec91c548015a42ebf0f56d87ecd779.
The original exact5669 bytes remain previous_guide.md, and the inserted recovery
instructions plus final7297 bytes are separately preserved. No other inventory
entry can change. Only the inventory's old path/hash reference is resolved to
the preserved old file; the actual selected guide is authenticated by the new
receipt. Catalog metadata_overrides explicitly records this one alias. V1/v2
catalog sources remain unchanged and unexecuted. No scientific override exists.
'''
with(A/'package_20260930_twentyeighth_catalog_v3_spec.md').open('x',encoding='utf8',newline='\n')as f:f.write(spec)
print(json.dumps({'source':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'catalog_executions':0}))
