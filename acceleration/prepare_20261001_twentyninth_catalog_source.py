"""Prepare a fresh wave29 catalog from the exercised wave28 closure design."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/package_20260930_twentyeighth_catalog_v2.py'
    assert sha(old)=='ce54f25d65d8a550682d86f6df84b19afbbd1880f3d7df8fe227ea925f2de2eb'
    text=old.read_text(encoding='utf8');changes=[]
    def replace(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b);changes.append(a[:120])
    def assign(name,value):
        nonlocal text
        lines=text.splitlines();found=[i for i,line in enumerate(lines)if line.startswith(name+'=')];assert len(found)==1,name
        lines[found[0]]=name+'='+repr(value);text='\n'.join(lines)+'\n';changes.append('assignment '+name)
    replace('import package_20260930_twentyeighth_recovery_v2 as recovery','import package_20261001_twentyninth_recovery as recovery')
    replace("ROOT=common.ROOT; B='acceleration/results/20260930_'; I=B+'independent_review/'","ROOT=common.ROOT; B='acceleration/results/20261001_'; I=B+'independent_review/'")
    assign('REGISTRATIONS',['acceleration/results/20260930_twentyninth_initial_registration','acceleration/results/20261001_twentyninth_followup_registration'])
    assign('FILES',['acceleration/'+name for name in ['package_20261001_twentyninth_catalog.py','package_20261001_twentyninth_catalog_spec.md','prepare_20261001_twentyninth_catalog_source.py','inventory_20261001_twentyninth_candidates.py','inventory_20261001_twentyninth_candidates_spec.md','package_20261001_twentyninth_recovery.py','package_20261001_twentyninth_recovery_spec.md','prepare_20261001_twentyninth_recovery_helpers.py','recover_20261001_twentyninth_raw_artifacts.py','check_20261001_twentyninth_recovery_controls.py','audit_20261001_twentyninth_checkpoint.py','audit_20261001_twentyninth_checkpoint_spec.md']])
    assign('FORBIDDEN_DIRECTORIES',['acceleration/results/20261001_exact_eight_prefix64_batch03','acceleration/results/20261001_independent_review/exact_eight_prefix64_batch03'])
    assign('FORBIDDEN_TOKENS',['batch03','BATCH03','batch04','BATCH04'])
    assign('PRIOR_CATALOG','acceleration/results/20260930_twentyeighth_artifact_packaging/catalog.json')
    assign('PRIOR_CATALOG_SHA','1dc941ddb899393f5d7d570f266cad6bc6205e64f3db13b4affe870f31de3586')
    assign('ALLOWED_OUTPUTS',{'acceleration/results/20261001_twentyninth_artifact_packaging','acceleration/results/20261001_twentyninth_preparation'})
    replace("ledger_path=B+'resume/claims_at_twentyeighth_milestone.yaml'","ledger_path=B+'resume/claims_at_twentyninth_milestone.yaml'")
    replace("hashlib.sha256(ledger_raw).hexdigest()=='c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441'","hashlib.sha256(ledger_raw).hexdigest()==args.ledger_sha256")
    replace("len(ledger['claims'])==294","len(ledger['claims'])==300")
    replace("{('VERIFIED','CLEAR'):287,('CANDIDATE','CLEAR'):3,('REFUTED','CLEAR'):4}","{('VERIFIED','CLEAR'):293,('CANDIDATE','CLEAR'):3,('REFUTED','CLEAR'):4}")
    replace("'exact ordered four-registration chain'","'exact ordered two-registration chain'")
    replace('len(ids)==len(set(ids))==8','len(ids)==len(set(ids))==6')
    replace("len(claims)==8 and Counter((c['status'],c['review_state']) for c in claims)=={('VERIFIED','CLEAR'):6,('REFUTED','CLEAR'):2}","len(claims)==6 and Counter((c['status'],c['review_state']) for c in claims)=={('VERIFIED','CLEAR'):6}")
    replace("metadata_dirs=[str(Path(args.inventory).parent).replace('\\\\','/'),B+'twentyeighth_raw_recovery',B+'twentyeighth_recovery_controls',B+'twentyeighth_recovery_preparation',B+'twentyeighth_recovery_schema_failure',I+'twentyeighth_checkpoint',I+'twentyeighth_checkpoint_v2']+args.extra_dir","metadata_dirs=[str(Path(args.inventory).parent).replace('\\\\','/'),B+'twentyninth_raw_recovery',B+'twentyninth_recovery_controls',B+'twentyninth_recovery_preparation',B+'twentyninth_catalog_source_preparation',I+'twentyninth_checkpoint']+args.extra_dir")
    replace("recovery_path=B+'twentyeighth_raw_recovery/manifest.json'","recovery_path=B+'twentyninth_raw_recovery/manifest.json'")
    previous="""    def check(name,expected,origin,archive=False):
        if any(origin==d+'/validation.json'for d in args.registration) and common.resolve_ref(name,ROOT/origin)=='CLAIMS.yaml':
            snapshot=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            assert common.digest(ROOT/snapshot)==expected;name=snapshot
"""
    corrected="""    ledger_aliases=[]
    historical_ledger_origins={}
    for d in REGISTRATIONS:
        snapshots=[d+'/CLAIMS.before.yaml',d+'/CLAIMS.after.yaml']
        for suffix in ['summary.json','validation.json']:
            historical_ledger_origins[d+'/'+suffix]=snapshots
    prep='acceleration/results/20260930_twentyninth_initial_registration_preparation'
    for suffix in ['summary.json','validation.json']:
        historical_ledger_origins[prep+'/'+suffix]=[prep+'/CLAIMS.before.yaml',prep+'/CLAIMS.proposed.yaml']
    def check(name,expected,origin,archive=False):
        if common.resolve_ref(name,ROOT/origin)=='CLAIMS.yaml':
            if expected==args.ledger_sha256:
                snapshot=ledger_path
            else:
                candidates=historical_ledger_origins.get(origin,[])
                matches=[p for p in candidates if common.digest(safe_path(p))==expected]
                assert len(matches)==1,('unbound historical ledger identity',origin,expected)
                snapshot=matches[0]
            ledger_aliases.append(dict(origin=origin,original_path=name,sha256=expected,resolved_snapshot=snapshot))
            name=snapshot
"""
    replace(previous,corrected)
    replace("common.save(out/'reference_diagnostics.json',dict(errors=errors,count=len(errors)));assert not errors", "common.save(out/'historical_ledger_aliases.json',dict(records=ledger_aliases,scope='Exact historical ledger bytes are resolved only to authenticated immutable snapshots; original receipts are unchanged.'))\n    common.save(out/'reference_diagnostics.json',dict(errors=errors,count=len(errors)));assert not errors")
    replace("excluded_cohorts=['Wave29 next64, all four-builds replacements/engineering and sizeclass16 GF3 screen.','Historical unregistered leftovers and protected user files.']","excluded_cohorts=['Batch03 and later allocations are outside the300-claim wave29 cutoff.','Historical unregistered leftovers and protected user files.']")
    replace("preserved_failures=['All exact inventory failures/corrections, including first registrar preparation, generic checker metadata correction and partial build continuation.','Both refuted shared-scheduler deadline and Popen/job-assignment containment records; replacement work excluded.']","preserved_failures=['All failures/corrections explicitly listed in the frozen wave29 inventory.','Earlier launcher refutations and failed preparations remain in the immutable prior catalog chain.']")
    replace('claim_population=294,new_claims=8,verified_clear=287','claim_population=300,new_claims=6,verified_clear=293')
    replace("['inventory','inventory-sha256','recovery-manifest','recovery-manifest-sha256']","['inventory','inventory-sha256','recovery-manifest','recovery-manifest-sha256','ledger-sha256']")
    text=text.replace('wave28','wave29').replace('WAVE28','WAVE29').replace('TWENTYEIGHTH_','TWENTYNINTH_')
    ast.parse(text);new=ROOT/'acceleration/package_20261001_twentyninth_catalog.py'
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    spec=ROOT/'acceleration/package_20261001_twentyninth_catalog_spec.md'
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('# Wave29 explicit evidence closure\n\nConsume the exact candidate inventory, frozen300-claim ledger and normalized raw recovery manifest through explicit CLI SHA256s. Require the two continuous registration transitions with six new VERIFIED/CLEAR claims and unchanged prior records. Include only inventory paths and explicit metadata supplements; the reproduction guide is supplemental after recovery is frozen. Exclude protected paths and batch03/later work.\n\nCheck every reachable recorded identity, complete compressed recovery byte stream and Git filter byte identity. Preserve historical CLAIMS.yaml identities by exact immutable before/after snapshots only for declared registration/preparation origins, recording every alias; do not rewrite original receipts. The current ledger identity resolves to the frozen milestone snapshot. Unknown identities fail. Public research files are at most10MiB; only explicitly named metadata wrappers may reach32MiB, with references split into deterministic gzip parts of25000 records. No native search, ledger/index edit or mathematical approval. Independent publication review is still required before staging.\n')
    out=ROOT/'acceleration/results/20261001_twentyninth_catalog_source_preparation';out.mkdir(exist_ok=False)
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),predecessor_sha256=sha(old),source_sha256=sha(new),spec_sha256=sha(spec),preparer_sha256=sha(Path(__file__)),changes=changes,catalog_calls=0,native_calls=0,mathematical_verification=False)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(source_sha256=sha(new),spec_sha256=sha(spec),catalog_calls=0)))
if __name__=='__main__':main()
