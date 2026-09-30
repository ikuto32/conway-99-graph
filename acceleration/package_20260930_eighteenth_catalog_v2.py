"""Explicit eighteenth evidence closure; no solver, ledger or index mutation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,yaml
import package_20260930_eighth_catalog as common
ROOT=common.ROOT;B='acceleration/results/20260930_';I=B+'independent_review/'
DIRECTORIES=[B+p for p in [
 'hadamard_prism_binary_mip_model','hadamard_prism_binary_mip_controls','hadamard_prism_binary_mip_pilot',
 'hadamard_balanced_parity','hadamard_balanced_parity_native_preflight','hadamard_balanced_parity_native_pilot',
 'hadamard_parity_lift_cnf','hadamard_parity_lift_obstruction','balanced_lift_lp_not_run',
 'hadamard_parity_support_cuts','hadamard_parity_support_cuts_native_preflight','hadamard_parity_support_cuts_native_pilot']]+[I+p for p in [
 'hadamard_mip_raw_controls','hadamard_prism_binary_mip_calibration','hadamard_prism_binary_mip_claim_binding',
 'hadamard_prism_binary_mip_pilot','hadamard_prism_binary_mip_execution','hadamard_balanced_parity',
 'hadamard_balanced_parity_object_calibration','hadamard_balanced_parity_object_calibration_v2',
 'hadamard_balanced_parity_sat','hadamard_balanced_parity_sat_v2','hadamard_parity_object_v2_delta',
 'balanced_lift_zero_rows','hadamard_balanced_parity_cuts','hadamard_parity_support_cuts_encoding',
 'hadamard_parity_support_cuts_object_calibration','hadamard_parity_support_cuts_sat','hadamard_parity_support_cuts_sat_outcome']]
FILES=['acceleration/'+p for p in [
 'theory_20260930_hadamard_prism_binary_mip.py','theory_20260930_hadamard_prism_binary_mip_spec.md',
 'audit_20260930_hadamard_mip_raw.py','audit_20260930_hadamard_mip_raw_controls.py',
 'audit_20260930_hadamard_prism_binary_mip.py','bind_20260930_hadamard_prism_binary_mip.py',
 'audit_20260930_hadamard_mip_execution_supplement.py',
 'theory_20260930_hadamard_balanced_parity.py','theory_20260930_hadamard_balanced_parity_spec.md',
 'audit_20260930_hadamard_balanced_parity.py','audit_20260930_hadamard_balanced_parity_v2.py',
 'audit_20260930_hadamard_parity_object_v2_delta.py','native_20260930_hadamard_balanced_parity.py',
 'native_20260930_hadamard_balanced_parity_spec.md','theory_20260930_hadamard_parity_lift_cnf.py',
 'theory_20260930_hadamard_parity_lift_cnf_spec.md','audit_20260930_hadamard_parity_lift_cnf.py',
 'audit_20260930_hadamard_parity_lift_domains.py','theory_20260930_hadamard_parity_lift_obstruction.py',
 'theory_20260930_hadamard_parity_lift_obstruction_spec.md','audit_20260930_balanced_lift_lp.py',
 'audit_20260930_balanced_lift_zero_rows.py','theory_20260930_balanced_lift_lp.py',
 'theory_20260930_balanced_lift_lp_spec.md','record_20260930_balanced_lift_lp_cancellation.py',
 'audit_20260930_hadamard_balanced_parity_cuts.py','theory_20260930_hadamard_parity_support_cuts.py',
 'theory_20260930_hadamard_parity_support_cuts_spec.md','audit_20260930_hadamard_parity_support_cuts.py',
 'native_20260930_hadamard_parity_support_cuts.py','native_20260930_hadamard_parity_support_cuts_spec.md',
 'audit_20260930_hadamard_support_cuts_sat_outcome.py','register_20260930_eighteenth_preparation.py',
 'register_20260930_eighteenth_zero_row_and_constant.py','package_20260930_eighteenth_catalog.py','package_20260930_eighteenth_catalog_v2.py']]+['docs/'+p for p in [
 'AUDIT_20260930_HADAMARD_PRISM_BINARY_MIP.md','AUDIT_20260930_HADAMARD_BALANCED_PARITY.md',
 'AUDIT_20260930_HADAMARD_PARITY_LIFT_CNF.md','AUDIT_20260930_BALANCED_LIFT_LP.md',
 'AUDIT_20260930_HADAMARD_BALANCED_PARITY_CUTS.md','AUDIT_20260930_HADAMARD_PARITY_SUPPORT_CUTS.md',
 'REPRODUCING_20260930_EIGHTEENTH_WAVE.md']]
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_CATALOG=B+'seventeenth_artifact_packaging/catalog.json'
PRIOR_CATALOG_SHA='cc9efc4d4985c262ffe55778c0ae5aee64e88709498ddaddee736f7f5f61de05'

def execute(args,out):
    ledger_raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledger_raw)
    assert len(ledger['claims'])==178
    artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[];previous=None
    for directory in args.registration:
        receipt=json.loads((ROOT/directory/'summary.json').read_bytes())
        before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids.extend(receipt['new_claim_ids'])
    assert previous==ledger_raw and len(ids)==len(set(ids))==7
    claims=[c for c in ledger['claims']if c['id']in ids]
    assert len(claims)==7 and all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    dirs=DIRECTORIES+args.registration+args.extra_dir;files=FILES+args.extra_file
    selected=set(files)
    for directory in dirs:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    assert not any(p=='PROMPT.md'or p.startswith('tools/drat-trim')or 'second_parity_lift'in p for p in selected)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z')
    assert PRIOR_CATALOG in tracked and common.digest(ROOT/PRIOR_CATALOG)==PRIOR_CATALOG_SHA
    prior=json.loads((ROOT/PRIOR_CATALOG).read_bytes())
    prior_recoverable=set(prior['prior_recoverable_dependencies'])
    prior_recoverable.update(r['path']for r in prior['entries']if r['availability']=='LOCAL_ONLY'and 'recovery available'in r['limitation'])
    cache={};refs=[];errors=[]
    def info(p):
        if p not in cache:
            path=ROOT/p;assert path.is_file()and path.resolve().is_relative_to(ROOT),p
            cache[p]=dict(path=p,sha256=common.digest(path),bytes=path.stat().st_size)
        return cache[p]
    def check(name,expected,origin,archive=False):
        # A completed registration validator binds its historical root ledger.
        # Authenticate the immutable adjacent snapshot, preserving the original
        # validation record and the failed v1 catalog attempt unchanged.
        if name=='CLAIMS.yaml'and any(origin==d+'/validation.json'for d in args.registration):
            snapshot=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            assert common.digest(ROOT/snapshot)==expected
            name=snapshot
        if name in artifacts:
            a=artifacts[name];assert a['sha256']==expected;name=a['path']
        path=common.resolve_ref(name,ROOT/origin,archive)
        if path is None:errors.append(dict(kind='unresolved',origin=origin,path=name,expected=expected));return
        item=info(path)
        if item['sha256']!=expected:errors.append(dict(kind='hash_mismatch',origin=origin,expected=expected,**item));return
        if not(path in selected or path in tracked or path in LOCAL_TOOLS or path in prior_recoverable or path.startswith('external_conway99_research/')):
            errors.append(dict(kind='missing_explicit_dependency',origin=origin,**item))
        refs.append(dict(origin=origin,**item))
    def walk(obj,origin):
        if isinstance(obj,dict):
            for key,value in obj.items():
                if key in common.MAP_KEYS|{'outputs_sha256','input_sha256'}and isinstance(value,dict):
                    for p,sha in value.items():
                        if isinstance(sha,str)and common.HEX.fullmatch(sha):check(p,sha,origin)
                walk(value,origin)
            if isinstance(obj.get('path'),str)and isinstance(obj.get('sha256'),str)and common.HEX.fullmatch(obj['sha256']):
                check(obj['path'],obj['sha256'],origin,'conway-99-research'in obj.get('repository',''))
        elif isinstance(obj,list):
            for value in obj:walk(value,origin)
    for path in sorted(selected):
        assert info(path)['bytes']<=10*1024**2,('oversize',path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path']in selected;check(a['path'],a['sha256'],'CLAIMS.yaml')
    common.save(out/'reference_diagnostics.json',dict(errors=errors,count=len(errors)));assert not errors,f'{len(errors)}closureerrors'
    paths=sorted(selected);git_hashes=common.git('hash-object','--stdin-paths',input=('\n'.join(paths)+'\n').encode()).decode().splitlines()
    gitrows=[]
    for p,sha in zip(paths,git_hashes,strict=True):
        raw=(ROOT/p).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha,('Git transforms',p)
        gitrows.append(dict(path=p,sha256=info(p)['sha256'],git_blob_sha1=sha))
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='READY_FOR_PUBLICATION')for p in paths],exact_directories=dirs,exact_files=files,
        local_tools=[info(p)for p in sorted(LOCAL_TOOLS)],prior_catalog=dict(path=PRIOR_CATALOG,sha256=PRIOR_CATALOG_SHA),
        prior_recoverable_dependencies=sorted(prior_recoverable),new_gzip_streams=0,
        excluded_cohorts=['Second selected-parity lift belongs to wave19.','Historical unregistered proof-core/identity/preflight leftovers.','Protected user files.'],
        preserved_failures=['First parity object checker metadata failure.','Initial selected-lift partial CNF assertion.'],
        unexecuted_preparations=['Original selected-lift SAT audit and numerical LP screen; skipped before solver execution.'],mathematical_verification_performed=False))
    common.save(out/'reference_checks.json',dict(status='EXACT_HASH_CLOSURE_PASS',records=refs))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        ledger_sha256=hashlib.sha256(ledger_raw).hexdigest(),claim_ids=ids,claim_population=len(ledger['claims']),new_claims=7,
        verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in ledger['claims']),target_resolution='UNKNOWN',preparation_only=args.prepare))
    payload=sorted(selected|{common.relative(p)for p in out.iterdir()if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,row in cache.items():assert common.digest(ROOT/p)==row['sha256'],('concurrentchange',p)
    assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_raw and common.git('ls-files','--stage','-z')==index
    status='EIGHTEENTH_PREPARATION_CLOSURE_PASS'if args.prepare else'EIGHTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json',dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,selected_files=len(paths),public_research_files=len(paths),
        public_research_bytes=sum(info(p)['bytes']for p in paths),new_local_only_research_artifacts=0,new_gzip_streams=0,
        reference_bindings=len(refs),unique_referenced_files=len({r['path']for r in refs}),output_hashes={common.relative(p):common.digest(p)for p in out.iterdir()if p.is_file()}))
    print(json.dumps(dict(status=status,public_files=len(paths))))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--prepare',action='store_true')
    for key in ['registration','extra-dir','extra-file']:ap.add_argument('--'+key,action='append',default=[])
    args=ap.parse_args();out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes()
    try:execute(args,out)
    except BaseException as error:
        (out/'failed_source.py').write_bytes(source);common.save(out/'failure.json',dict(error=repr(error),source_sha256=hashlib.sha256(source).hexdigest(),command=[sys.executable,*sys.argv],timestamp=datetime.now(timezone.utc).isoformat()));raise
if __name__=='__main__':main()
