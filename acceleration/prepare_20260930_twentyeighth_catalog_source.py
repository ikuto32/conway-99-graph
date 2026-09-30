"""Prepare wave28 metadata-only catalog source; do not execute a catalog."""
from pathlib import Path
import ast,re,hashlib
A=Path(__file__).resolve().parent
old=A/'package_20260930_twentyseventh_catalog.py'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='fcc2097bc3889f45a672e4a492303bf4e20e7555966641f74c8a32e2f1b5981c'
s=old.read_text(encoding='utf8').replace('twentyseventh','twentyeighth').replace('TWENTYSEVENTH','TWENTYEIGHTH').replace('wave27','wave28').replace('Wave27','Wave28').replace('WAVE27','WAVE28')
registrations=['acceleration/results/20260930_twentyeighth_'+x+'_registration'for x in ['initial','kernel_sizeclass','sizeclass_proof','launcher_refutation']]
assignments={
 'REGISTRATIONS':registrations,
 'DIRECTORIES':[],
 'FILES':['acceleration/package_20260930_twentyeighth_catalog.py','acceleration/package_20260930_twentyeighth_catalog_spec.md','acceleration/prepare_20260930_twentyeighth_catalog_source.py'],
 'FORBIDDEN_DIRECTORIES':['acceleration/results/20260930_exact_eight_next64','acceleration/results/20260930_exact_eight_four_builds','acceleration/results/20260930_independent_review/four_serial_build','acceleration/results/20260930_sizeclass16_affine_gram_gf3'],
 'FORBIDDEN_TOKENS':['next64','NEXT64','four_builds','FOUR_BUILDS','four_serial_build','sizeclass16_affine_gram_gf3','SIZECLASS16_AFFINE_GRAM_GF3','exact_eight_explicit_batch_v3'],
 'PRIOR_CATALOG':'acceleration/results/20260930_twentyseventh_artifact_packaging/catalog.json',
 'PRIOR_CATALOG_SHA':'fd10bd3872a7699f7ea80e1072c697b300cdb9d0cf7cdb19dd1a0c898e6565a8',
}
for name,value in assignments.items():
    s,n=re.subn(r'^'+name+r'=.*$',name+'='+repr(value),s,flags=re.M);assert n==1,name
def replace(a,b):
    global s
    assert a in s,a[:100];s=s.replace(a,b)
replace("ledger_raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledger_raw)","ledger_path=B+'resume/claims_at_twentyeighth_milestone.yaml'\n    ledger_raw=(ROOT/ledger_path).read_bytes();ledger=yaml.safe_load(ledger_raw)")
replace('5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237','c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441')
replace("len(ledger['claims'])==286","len(ledger['claims'])==294")
replace("{('VERIFIED','CLEAR'):281,('CANDIDATE','CLEAR'):3,('REFUTED','CLEAR'):2}","{('VERIFIED','CLEAR'):287,('CANDIDATE','CLEAR'):3,('REFUTED','CLEAR'):4}")
replace("'exact ordered six-registration chain'","'exact ordered four-registration chain'")
replace("    promotion=json.loads((ROOT/(B+'twentyeighth_psd_promotion/summary.json')).read_bytes())\n    assert promotion['promoted_claim_ids']==['C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN']and promotion['from_revision']==1 and promotion['to_revision']==2\n",'')
replace("=={('VERIFIED','CLEAR'):8}","=={('VERIFIED','CLEAR'):6,('REFUTED','CLEAR'):2}")
replace("    dirs=DIRECTORIES+args.registration+args.extra_dir;files=FILES+args.extra_file\n    selected=set(files)\n    for directory in dirs:\n        assert(ROOT/directory).is_dir(),directory\n        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())", """    assert common.digest(ROOT/args.inventory)==args.inventory_sha256
    inventory=json.loads((ROOT/args.inventory).read_bytes())
    assert not inventory['pending']and not inventory['hash_mismatches']
    assert inventory['registration_chain']==REGISTRATIONS
    assert inventory['new_claim_ids']==ids
    inventory_entries=inventory['entries'];assert len({r['path']for r in inventory_entries})==len(inventory_entries)
    dirs=inventory['explicit_directories']
    files=inventory['explicit_files']+FILES+args.extra_file
    # Scientific selection is the exact hashed inventory, never a fresh directory walk.
    selected={r['path']for r in inventory_entries}|set(FILES)|set(args.extra_file)
    metadata_dirs=[str(Path(args.inventory).parent).replace('\\\\','/'),B+'twentyeighth_raw_recovery',B+'twentyeighth_recovery_controls']+args.extra_dir
    for directory in metadata_dirs:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    dirs=dirs+metadata_dirs""")
replace("and p not in FORBIDDEN_FILES and not p.startswith('tools/'),('protected/future reference before read',p)","and p not in FORBIDDEN_FILES and not p.startswith(('tools/','external_conway99_research/')),('protected/future reference before read',p)")
replace("p!='PROMPT.md' and not p.startswith('tools/drat-trim')","p!='PROMPT.md' and not p.startswith(('tools/','external_conway99_research/'))")
replace("    packages=recovery.packages()\n    recovery_path=B+'twentyeighth_raw_recovery/manifest.json'\n    assert common.digest(ROOT/recovery_path)=='d6d5e3933cd8294b4f4119c6ba495780a77cf19833ecb056598a863bbef11958'", "    recovery_path=B+'twentyeighth_raw_recovery/manifest.json'\n    assert args.recovery_manifest==recovery_path and common.digest(ROOT/recovery_path)==args.recovery_manifest_sha256\n    packages=recovery.packages()")
replace("    for path in tqdm(sorted(selected),desc=\"Check wave28 artifacts\",mininterval=1):", "    for row in inventory_entries:\n        assert info(row['path'])['sha256']==row['sha256']and info(row['path'])['bytes']==row['bytes'],'frozen inventory bytes'\n    for path in tqdm(sorted(selected),desc=\"Check wave28 artifacts\",mininterval=1):")
replace("package['manifest'])","package['manifest']or recovery_path)")
replace("        whole=hashlib.sha256();total=0\n        for part in package['parts']:","        whole=hashlib.sha256();total=0\n        original=(ROOT/package['path']).open('rb')\n        for part in package['parts']:")
replace("                    whole.update(block);chunk.update(block);size+=len(block)","                    assert original.read(len(block))==block,'literal original recovery bytes'\n                    whole.update(block);chunk.update(block);size+=len(block)")
replace("        assert total==package['bytes'] and whole.hexdigest()==package['sha256']","        assert not original.read(1);original.close()\n        assert total==package['bytes'] and whole.hexdigest()==package['sha256']")
replace("excluded_cohorts=['Wave28 next32 cohorts, explicit-builderv2, and first12 union.','Historical unregistered leftovers and protected user files.']","excluded_cohorts=['Wave29 next64, all four-builds replacements/engineering and sizeclass16 GF3 screen.','Historical unregistered leftovers and protected user files.']")
replace("preserved_failures=['Native preparation/source failures, inventory v1 and coverage v1 preserved unchanged.','PSD intermediate candidate revision1 and verified revision2 retained in registration chain.']","preserved_failures=['All exact inventory failures/corrections, including first registrar preparation, generic checker metadata correction and partial build continuation.','Both refuted shared-scheduler deadline and Popen/job-assignment containment records; replacement work excluded.']")
replace("unexecuted_preparations=['Source-only explicit build-batch interface v1; no additional build was executed by that preparation.']","unexecuted_preparations=['Only exact inventory-declared source preparations; no catalog process builds formulas or invokes native solvers.']")
replace("mathematical_verification_performed=False))","candidate_inventory=dict(path=args.inventory,sha256=args.inventory_sha256),normalized_recovery=dict(path=recovery_path,sha256=args.recovery_manifest_sha256),mathematical_verification_performed=False))")
replace('claim_population=286,new_claims=8,verified_clear=281,candidate_clear=3,refuted_clear=2','claim_population=294,new_claims=8,verified_clear=287,candidate_clear=3,refuted_clear=4')
replace("assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_raw","assert(ROOT/ledger_path).read_bytes()==ledger_raw")
replace("    for key in ['registration','extra-dir','extra-file']:ap.add_argument('--'+key,action='append',default=[])","    for key in ['inventory','inventory-sha256','recovery-manifest','recovery-manifest-sha256']:ap.add_argument('--'+key,required=True)\n    for key in ['registration','extra-dir','extra-file']:ap.add_argument('--'+key,action='append',default=[])")
replace("    args=ap.parse_args();out=(ROOT/args.out).resolve();", "    args=ap.parse_args()\n    if not args.registration:args.registration=list(REGISTRATIONS)\n    out=(ROOT/args.out).resolve();")
ast.parse(s)
with(A/'package_20260930_twentyeighth_catalog.py').open('x',encoding='utf8',newline='\n')as f:f.write(s)
print(hashlib.sha256((A/'package_20260930_twentyeighth_catalog.py').read_bytes()).hexdigest())
