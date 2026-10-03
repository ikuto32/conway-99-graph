"""Explicit twenty-first evidence closure; no solver, ledger or index mutation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,subprocess,sys,yaml
import package_20260930_eighth_catalog as common
ROOT=common.ROOT;B='acceleration/results/20260930_';I=B+'independent_review/'
DIRECTORIES=['acceleration/results/20260930_hadamard_case0_model_package', 'acceleration/results/20260930_hadamard_case0_profile_cnf', 'acceleration/results/20260930_hadamard_case0_profile_native_pilot', 'acceleration/results/20260930_hadamard_case0_profile_native_preflight', 'acceleration/results/20260930_hadamard_exception_groups', 'acceleration/results/20260930_hadamard_fibre_profile_orbits', 'acceleration/results/20260930_hadamard_first_partial_psd', 'acceleration/results/20260930_hadamard_four_group_circuits', 'acceleration/results/20260930_hadamard_four_group_joint', 'acceleration/results/20260930_hadamard_four_group_joint_v2', 'acceleration/results/20260930_hadamard_four_group_local_screen', 'acceleration/results/20260930_hadamard_six_exception_census', 'acceleration/results/20260930_hadamard_six_rank4_dp', 'acceleration/results/20260930_independent_review/case0_model_transport', 'acceleration/results/20260930_independent_review/first_partial12_psd', 'acceleration/results/20260930_independent_review/five_unbalanced_groups', 'acceleration/results/20260930_independent_review/four_group_ac_calibration', 'acceleration/results/20260930_independent_review/four_group_joint_v2', 'acceleration/results/20260930_independent_review/four_group_partial12_object', 'acceleration/results/20260930_independent_review/hadamard_case0_profile_cnf', 'acceleration/results/20260930_independent_review/hadamard_case0_profile_object_calibration', 'acceleration/results/20260930_independent_review/hadamard_case0_profile_unsat', 'acceleration/results/20260930_independent_review/hadamard_few_exception_marginals', 'acceleration/results/20260930_independent_review/hadamard_fibre_profile_orbits', 'acceleration/results/20260930_independent_review/hadamard_four_group_circuits', 'acceleration/results/20260930_independent_review/hadamard_four_group_local_screen', 'acceleration/results/20260930_independent_review/hadamard_six_exception_census', 'acceleration/results/20260930_independent_review/hadamard_six_rank4_profiles', 'acceleration/results/20260930_independent_review/six_group_rank_preparation']
FILES=['acceleration/audit_20260930_case0_model_package.py', 'acceleration/audit_20260930_first_partial_psd.py', 'acceleration/audit_20260930_five_unbalanced_groups.py', 'acceleration/audit_20260930_four_group_ac_calibration.py', 'acceleration/audit_20260930_four_group_joint_v2.py', 'acceleration/audit_20260930_four_group_partial_object.py', 'acceleration/audit_20260930_hadamard_case0_profile.py', 'acceleration/audit_20260930_hadamard_case0_profile_unsat.py', 'acceleration/audit_20260930_hadamard_few_exception_marginals.py', 'acceleration/audit_20260930_hadamard_fibre_profile_orbits.py', 'acceleration/audit_20260930_hadamard_four_group_circuits.py', 'acceleration/audit_20260930_hadamard_four_group_local_screen.py', 'acceleration/audit_20260930_hadamard_six_exception_census.py', 'acceleration/audit_20260930_hadamard_six_rank4_profiles.py', 'acceleration/audit_20260930_six_group_rank_preparation.py', 'acceleration/native_20260930_hadamard_case0_profile.py', 'acceleration/native_20260930_hadamard_case0_profile_spec.md', 'acceleration/package_20260930_case0_profile_model.py', 'acceleration/register_20260930_twentyfirst_joint_and_five.py', 'acceleration/register_20260930_twentyfirst_normalization.py', 'acceleration/register_20260930_twentyfirst_proof_and_marginals.py', 'acceleration/register_20260930_twentyfirst_six_and_case0.py', 'acceleration/register_20260930_twentyfirst_structural.py', 'acceleration/package_20260930_twentyfirst_catalog.py', 'acceleration/theory_20260930_hadamard_case0_profile_cnf.py', 'acceleration/theory_20260930_hadamard_case0_profile_cnf_spec.md', 'acceleration/theory_20260930_hadamard_exception_groups.py', 'acceleration/theory_20260930_hadamard_exception_groups_spec.md', 'acceleration/theory_20260930_hadamard_fibre_profile_orbits.py', 'acceleration/theory_20260930_hadamard_fibre_profile_orbits_spec.md', 'acceleration/theory_20260930_hadamard_first_partial_psd.py', 'acceleration/theory_20260930_hadamard_first_partial_psd_spec.md', 'acceleration/theory_20260930_hadamard_four_group_circuits.py', 'acceleration/theory_20260930_hadamard_four_group_circuits_spec.md', 'acceleration/theory_20260930_hadamard_four_group_joint.py', 'acceleration/theory_20260930_hadamard_four_group_joint_spec.md', 'acceleration/theory_20260930_hadamard_four_group_joint_v2.py', 'acceleration/theory_20260930_hadamard_four_group_joint_v2_spec.md', 'acceleration/theory_20260930_hadamard_four_group_local_screen.py', 'acceleration/theory_20260930_hadamard_four_group_local_screen_spec.md', 'acceleration/theory_20260930_hadamard_six_exception_census.py', 'acceleration/theory_20260930_hadamard_six_exception_census_spec.md', 'acceleration/theory_20260930_hadamard_six_rank4_dp.py', 'acceleration/theory_20260930_hadamard_six_rank4_dp_spec.md', 'docs/AUDIT_20260930_FIVE_UNBALANCED_GROUPS.md', 'docs/AUDIT_20260930_HADAMARD_CASE0_PROFILE.md', 'docs/AUDIT_20260930_HADAMARD_CASE0_PROFILE_UNSAT.md', 'docs/AUDIT_20260930_HADAMARD_FEW_EXCEPTION_MARGINALS.md', 'docs/AUDIT_20260930_HADAMARD_FIBRE_PROFILE_ORBITS.md', 'docs/AUDIT_20260930_HADAMARD_FIRST_PARTIAL_PSD.md', 'docs/AUDIT_20260930_HADAMARD_FOUR_GROUP_CIRCUITS.md', 'docs/AUDIT_20260930_HADAMARD_FOUR_GROUP_JOINT.md', 'docs/AUDIT_20260930_HADAMARD_FOUR_GROUP_LOCAL_SCREEN.md', 'docs/AUDIT_20260930_HADAMARD_SIX_GROUP_KERNELS.md', 'docs/AUDIT_20260930_HADAMARD_SIX_RANK4_MARGINALS.md', 'docs/DERIVATION_20260930_FIVE_UNBALANCED_GROUPS_CANDIDATE.md', 'docs/REPRODUCING_20260930_TWENTYFIRST_WAVE.md']
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_CATALOG=B+'twentieth_artifact_packaging/catalog.json'
PRIOR_CATALOG_SHA='8ac7d74c8a6ebcd0977e980a3d6003f6c198c4e38e5b132d797aded8f1e5c987'

def execute(args,out):
    ledger_raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledger_raw)
    assert len(ledger['claims'])==206
    artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[];previous=None
    for directory in args.registration:
        receipt=json.loads((ROOT/directory/'summary.json').read_bytes())
        before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids.extend(receipt['new_claim_ids'])
    assert previous==ledger_raw and len(ids)==len(set(ids))==12
    claims=[c for c in ledger['claims']if c['id']in ids]
    assert len(claims)==12 and all(c['review_state']=='CLEAR' for c in claims)
    assert all(c['status']=='VERIFIED' for c in claims)
    dirs=DIRECTORIES+args.registration+args.extra_dir;files=FILES+args.extra_file
    selected=set(files)
    for directory in dirs:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    assert not any(p=='PROMPT.md'or p.startswith('tools/drat-trim')or 'four_profile_cnfs'in p or 'input_relabeling'in p or 'six_profile_local_domains'in p for p in selected)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z')
    assert PRIOR_CATALOG in tracked and common.digest(ROOT/PRIOR_CATALOG)==PRIOR_CATALOG_SHA
    prior=json.loads((ROOT/PRIOR_CATALOG).read_bytes())
    prior_recoverable=set(prior['prior_recoverable_dependencies'])
    prior_recoverable.update(r['path']for r in prior['entries']if r['availability']=='LOCAL_ONLY'and 'recovery available'in r['limitation'])
    local={B+'hadamard_case0_profile_cnf/model.json':'Raw retained LOCAL_ONLY; exact public gzip recovery available.'}
    assert set(local)<=selected
    cache={};refs=[];errors=[];recovered=[]
    def info(p):
        if p not in cache:
            path=ROOT/p;assert path.is_file()and path.resolve().is_relative_to(ROOT),p
            cache[p]=dict(path=p,sha256=common.digest(path),bytes=path.stat().st_size)
        return cache[p]
    def check(name,expected,origin,archive=False):
        # A completed registration validator binds its historical root ledger.
        # Authenticate the immutable adjacent snapshot, preserving the original
        # validation record and the failed v1 catalog attempt unchanged.
        if common.resolve_ref(name,ROOT/origin)=='CLAIMS.yaml'and any(origin==d+'/validation.json'for d in args.registration):
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
        assert path in local or info(path)['bytes']<=10*1024**2,('oversize',path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    manifest=B+'hadamard_case0_model_package/artifact_packages.json'
    m=json.loads((ROOT/manifest).read_bytes())
    compressed=b''.join((ROOT/r['path']).read_bytes() for r in m['parts'])
    assert len(m['parts'])==1 and len(compressed)==m['compressed_bytes'] and hashlib.sha256(compressed).hexdigest()==m['compressed_sha256']
    raw=gzip.decompress(compressed)
    assert len(raw)==m['raw_bytes'] and hashlib.sha256(raw).hexdigest()==m['raw_sha256']
    check(m['raw_path'],m['raw_sha256'],manifest)
    recovered.append(dict(path=m['raw_path'],sha256=m['raw_sha256'],bytes=len(raw),manifest=manifest))
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path']in selected;check(a['path'],a['sha256'],'CLAIMS.yaml')
    common.save(out/'reference_diagnostics.json',dict(errors=errors,count=len(errors)));assert not errors,f'{len(errors)}closureerrors'
    paths=sorted(selected-set(local));git_hashes=common.git('hash-object','--stdin-paths',input=('\n'.join(paths)+'\n').encode()).decode().splitlines()
    gitrows=[]
    for p,sha in zip(paths,git_hashes,strict=True):
        raw=(ROOT/p).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha,('Git transforms',p)
        gitrows.append(dict(path=p,sha256=info(p)['sha256'],git_blob_sha1=sha))
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='LOCAL_ONLY' if p in local else 'READY_FOR_PUBLICATION',limitation=local.get(p))for p in sorted(selected)],exact_directories=dirs,exact_files=files,
        local_tools=[info(p)for p in sorted(LOCAL_TOOLS)],prior_catalog=dict(path=PRIOR_CATALOG,sha256=PRIOR_CATALOG_SHA),
        prior_recoverable_dependencies=sorted(prior_recoverable),new_gzip_streams=1,
        excluded_cohorts=['Remaining15-profile encoding/native campaign, six-profile local-domain filter and input-coordinate relabelling diagnostic belong to wave22.','Historical unregistered leftovers and protected user files.'],
        preserved_failures=['Joint enumerator v1 positive fixture used research diagonal limit; corrected v2 kept fixed120-second limit.'],
        unexecuted_preparations=[],mathematical_verification_performed=False))
    common.save(out/'reference_checks.json',dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',records=refs,gzip_recoveries=recovered))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        ledger_sha256=hashlib.sha256(ledger_raw).hexdigest(),claim_ids=ids,claim_population=len(ledger['claims']),new_claims=12,
        verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in ledger['claims']),target_resolution='UNKNOWN',preparation_only=args.prepare))
    payload=sorted(set(paths)|{common.relative(p)for p in out.iterdir()if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,row in cache.items():assert common.digest(ROOT/p)==row['sha256'],('concurrentchange',p)
    assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_raw and common.git('ls-files','--stage','-z')==index
    status='TWENTYFIRST_PREPARATION_CLOSURE_PASS'if args.prepare else'TWENTYFIRST_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json',dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,selected_files=len(selected),public_research_files=len(paths),
        public_research_bytes=sum(info(p)['bytes']for p in paths),new_local_only_research_artifacts=len(local),new_gzip_streams=1,
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
