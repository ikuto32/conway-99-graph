"""Explicit wave23 evidence closure; no solver/ledger/index edits."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, gzip, hashlib, io, json, subprocess, sys, yaml
import package_20260930_eighth_catalog as common
ROOT=common.ROOT; B='acceleration/results/20260930_'; I=B+'independent_review/'
PROFILE_IDS=['rank4_00_profile_0002', 'rank4_00_profile_0004', 'rank4_00_profile_0007', 'rank4_00_profile_0009', 'rank4_00_profile_0011', 'rank4_00_profile_0012', 'rank4_00_profile_0039', 'rank4_00_profile_0041', 'rank4_00_profile_0042', 'rank4_01_profile_0000', 'rank4_01_profile_0001', 'rank4_01_profile_0002', 'rank4_01_profile_0045', 'rank4_01_profile_0046', 'rank4_01_profile_0047', 'rank4_03_profile_0000', 'rank4_03_profile_0003', 'rank4_03_profile_0004', 'rank4_03_profile_0007', 'rank4_03_profile_0010', 'rank4_03_profile_0011', 'rank4_03_profile_0012', 'rank4_03_profile_0039', 'rank4_03_profile_0040', 'rank4_03_profile_0041', 'rank4_04_profile_0000', 'rank4_04_profile_0003', 'rank4_04_profile_0006', 'rank4_04_profile_0009', 'rank4_04_profile_0010', 'rank4_04_profile_0011', 'rank4_04_profile_0012', 'rank4_04_profile_0039', 'rank4_04_profile_0040', 'rank4_04_profile_0041', 'rank4_05_profile_0000', 'rank4_05_profile_0009', 'rank4_08_profile_0004', 'rank4_08_profile_0018', 'rank4_08_profile_0030', 'rank4_08_profile_0042', 'rank4_08_profile_0049', 'rank4_08_profile_0051', 'rank4_08_profile_0055', 'rank4_08_profile_0234', 'rank4_08_profile_0236', 'rank4_08_profile_0238', 'rank4_08_profile_0241', 'rank4_08_profile_0243', 'rank4_08_profile_0245', 'rank4_08_profile_0246', 'rank4_08_profile_0273', 'rank4_08_profile_0275', 'rank4_08_profile_0278']
REGISTRATIONS=[B+x+"_registration" for x in ['twentythird_base_results', 'twentythird_fiftyfour_proofs', 'twentythird_seven_and_coordinates', 'twentythird_six_union', 'twentythird_seven_normalization']]
DIRECTORIES=[B+x for x in ['hadamard_six_profile_cnf', 'hadamard_six_profile_native_preflight', 'hadamard_six_profile_native_pilot', 'hadamard_six_profile_batch_preparation', 'hadamard_six_profile_batch_preflight', 'hadamard_six_profile_batch_campaign', 'hadamard_six_profile_proof_package', 'hadamard_six_remaining_selection', 'hadamard_six_remaining_cnfs', 'six_literal_model_recovery', 'hadamard_all_triple_descent', 'hadamard_eight_exception_census', 'hadamard_seven_profile_local_domains', 'hadamard_seven_profile_arc_preparation', 'hadamard_seven_profile_arc', 'hadamard_seven_profile_arc_v2', 'hadamard_seven_fibre_orbits', 'hadamard_coordinate_marginal_domains']]+[I+x for x in ['hadamard_six_profile_cnf', 'hadamard_six_profile_object_calibration', 'hadamard_six_profile_unsat', 'hadamard_fiftyfour_profile_cnfs', 'hadamard_fiftyfour_profile_object_calibration', 'hadamard_fiftyfour_profile_proofs', 'hadamard_fiftyfour_proof_transport', 'hadamard_all_triple_descent', 'hadamard_eight_exception_census', 'hadamard_seven_profile_local_domains', 'hadamard_seven_profile_arc', 'hadamard_seven_fibre_orbits', 'coordinate_marginal_domains', 'hadamard_six_profile_union']]
FILES=["acceleration/"+x for x in ['audit_20260930_hadamard_six_profile.py', 'audit_20260930_hadamard_six_profile_unsat.py', 'audit_20260930_hadamard_fiftyfour_profiles.py', 'audit_20260930_hadamard_fiftyfour_profile_object.py', 'audit_20260930_hadamard_fiftyfour_profile_proofs.py', 'audit_20260930_hadamard_fiftyfour_proof_transport.py', 'audit_20260930_hadamard_all_triple_descent.py', 'audit_20260930_hadamard_eight_exception_census.py', 'audit_20260930_hadamard_seven_profile_local_domains.py', 'audit_20260930_seven_profile_arc.py', 'audit_20260930_hadamard_seven_fibre_orbits.py', 'audit_20260930_coordinate_marginal_domains.py', 'audit_20260930_hadamard_six_profile_union.py', 'theory_20260930_hadamard_six_profile_cnf.py', 'theory_20260930_hadamard_six_profile_cnf_spec.md', 'select_20260930_hadamard_six_remaining_profiles.py', 'select_20260930_hadamard_six_remaining_profiles_spec.md', 'build_20260930_hadamard_six_remaining_profiles.py', 'build_20260930_hadamard_six_remaining_profiles_spec.md', 'native_20260930_hadamard_six_profile.py', 'native_20260930_hadamard_six_profile_spec.md', 'native_20260930_hadamard_six_profile_batch.py', 'native_20260930_hadamard_six_profile_batch_spec.md', 'package_20260930_six_profile_proofs.py', 'package_20260930_six_profile_proofs_spec.md', 'recover_20260930_six_profile_proofs.py', 'recover_20260930_six_literal_model.py', 'theory_20260930_hadamard_all_triple_descent.py', 'theory_20260930_hadamard_all_triple_descent_spec.md', 'theory_20260930_hadamard_eight_exception_census.py', 'theory_20260930_hadamard_eight_exception_census_spec.md', 'theory_20260930_hadamard_seven_profile_local_domains.py', 'theory_20260930_hadamard_seven_profile_local_domains_spec.md', 'theory_20260930_hadamard_seven_profile_arc.py', 'theory_20260930_hadamard_seven_profile_arc_spec.md', 'theory_20260930_hadamard_seven_profile_arc_v2.py', 'theory_20260930_hadamard_seven_profile_arc_v2_spec.md', 'theory_20260930_hadamard_seven_fibre_orbits.py', 'theory_20260930_hadamard_seven_fibre_orbits_spec.md', 'theory_20260930_hadamard_coordinate_marginal_domains.py', 'theory_20260930_hadamard_coordinate_marginal_domains_spec.md', 'package_20260930_twentythird_catalog.py', 'package_20260930_twentythird_catalog_spec.md', 'register_20260930_twentythird_base_results.py', 'register_20260930_twentythird_fiftyfour_proofs.py', 'register_20260930_twentythird_seven_and_coordinates.py', 'register_20260930_twentythird_six_union.py', 'register_20260930_twentythird_seven_normalization.py']]+["docs/"+x for x in ['AUDIT_20260930_HADAMARD_SIX_PROFILE_CNF.md', 'AUDIT_20260930_HADAMARD_SIX_PROFILE0000_UNSAT.md', 'AUDIT_20260930_HADAMARD_FIFTYFOUR_PROFILES.md', 'AUDIT_20260930_HADAMARD_FIFTYFOUR_PROFILE_OBJECT.md', 'AUDIT_20260930_HADAMARD_FIFTYFOUR_PROFILE_PROOFS.md', 'AUDIT_20260930_HADAMARD_FIFTYFOUR_PROOF_TRANSPORT.md', 'AUDIT_20260930_HADAMARD_ALL_TRIPLE_DESCENT.md', 'RESEARCH_20260930_HADAMARD_ALL_TRIPLE_DESCENT.md', 'AUDIT_20260930_HADAMARD_EIGHT_EXCEPTION_CENSUS.md', 'AUDIT_20260930_HADAMARD_SEVEN_LOCAL_DOMAINS.md', 'AUDIT_20260930_SEVEN_PROFILE_ARC_PLAN.md', 'AUDIT_20260930_HADAMARD_SEVEN_FIBRE_ORBITS.md', 'DERIVATION_20260930_SEVEN_PROFILE_FIBRE_NORMALIZATION.md', 'AUDIT_20260930_COORDINATE_MARGINAL_DOMAINS.md', 'DERIVATION_20260930_SIX_PROFILE_UNION_CANDIDATE.md', 'AUDIT_20260930_SIX_PROFILE_UNION.md', 'REPRODUCING_20260930_TWENTYTHIRD_WAVE.md']]+[B+"resume/twentysecond_publication_observation.json"]
FILES+=['acceleration/recover_20260930_twentythird_raw_artifacts.py',B+'resume/twentythird_raw_recovery.json']
FORBIDDEN_DIRECTORIES=[B+'hadamard_count_master_preflight',B+'hadamard_count_master_cnf']
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_CATALOG=B+'twentysecond_artifact_packaging/catalog.json'
PRIOR_CATALOG_SHA='954f74663121ec84b550a09f4a18a6edadcdc74c532ff0fdc8b8c0130368e76d'
RESEARCH_LIMIT=10*1024**2
WRAPPER_LIMIT=32*1024**2
WRAPPER_NAMES={'catalog.json','stage_inventory.json','reference_checks.json.gz'}
ALLOWED_OUTPUTS={B+'twentythird_preparation',B+'twentythird_artifact_packaging'}
METADATA_WRAPPERS={directory+'/'+name for directory in ALLOWED_OUTPUTS for name in WRAPPER_NAMES}

def compressed_json(path, value):
    """Deterministic single gzip stream: UTF-8 JSON, sorted keys, LF, mtime=0."""
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as gz:
            with io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as text:
                json.dump(value,text,sort_keys=True,separators=(',',':'));text.write('\n')

def execute(args,out):
    ledger_raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledger_raw)
    assert len(ledger['claims'])==229
    assert Counter((c['status'],c['review_state'])for c in ledger['claims'])=={('VERIFIED','CLEAR'):226,('CANDIDATE','CLEAR'):2,('REFUTED','CLEAR'):1}
    assert args.registration==REGISTRATIONS, 'exact ordered five-registration chain'
    artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[];previous=None
    for directory in args.registration:
        receipt=json.loads((ROOT/directory/'summary.json').read_bytes())
        before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids.extend(receipt['new_claim_ids'])
    assert previous==ledger_raw and len(ids)==len(set(ids))==13
    claims=[c for c in ledger['claims']if c['id']in ids]
    assert len(claims)==13 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    dirs=DIRECTORIES+args.registration+args.extra_dir;files=FILES+args.extra_file
    selected=set(files)
    for directory in dirs:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    for p in selected:
        assert not any(p==d or p.startswith(d+'/') for d in FORBIDDEN_DIRECTORIES),('future cohort',p)
        assert p!='PROMPT.md' and not p.startswith('tools/drat-trim') and 'count_master' not in p
        assert Path(p).name.lower() not in {'.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'}
        assert not p.endswith(('.pem','.key')),('protected/private file type',p)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z')
    assert PRIOR_CATALOG in tracked and common.digest(ROOT/PRIOR_CATALOG)==PRIOR_CATALOG_SHA
    prior=json.loads((ROOT/PRIOR_CATALOG).read_bytes())
    prior_recoverable=set(prior['prior_recoverable_dependencies'])
    prior_recoverable.update(r['path']for r in prior['entries']if r['availability']=='LOCAL_ONLY'and 'recovery available'in r['limitation'])
    local={B+f'hadamard_six_remaining_cnfs/run01/{pid}/model.json':'Raw model retained LOCAL_ONLY; exact public gzip recovery available.' for pid in PROFILE_IDS}
    local[B+'hadamard_six_profile_cnf/profile_0000/model.json']='Raw model retained LOCAL_ONLY; exact public gzip recovery available.'
    local.update({B+f'hadamard_six_profile_batch_campaign/{pid}/main/proof.drat':'Raw proof retained LOCAL_ONLY; exact public chunked gzip recovery available.' for pid in PROFILE_IDS})
    assert len(local)==109 and set(local)<=selected
    cache={};refs=[];errors=[];recovered=[]
    def info(p):
        if p not in cache:
            path=ROOT/p;assert path.is_file()and path.resolve().is_relative_to(ROOT),p
            cache[p]=dict(path=p,sha256=common.digest(path),bytes=path.stat().st_size)
        return cache[p]
    def check(name,expected,origin,archive=False):
        if common.resolve_ref(name,ROOT/origin)=='CLAIMS.yaml'and any(origin==d+'/validation.json'for d in args.registration):
            snapshot=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            assert common.digest(ROOT/snapshot)==expected;name=snapshot
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
        assert path in local or info(path)['bytes'] <= (WRAPPER_LIMIT if path in METADATA_WRAPPERS else RESEARCH_LIMIT),('oversize',path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    # Stream each public gzip independently and compare the whole restored raw original.
    batchpath=B+'hadamard_six_remaining_cnfs/run01/summary.json';batch=json.loads((ROOT/batchpath).read_bytes())
    proofpath=B+'hadamard_six_profile_proof_package/package_manifest.json';proofs=json.loads((ROOT/proofpath).read_bytes())
    assert batch['selection']==PROFILE_IDS==[r['profile_id'] for r in proofs['records']]
    packages=[]
    for case in batch['records']:
        manifest=case['model_package_path'];check(manifest,case['model_package_sha256'],batchpath)
        m=json.loads((ROOT/manifest).read_bytes())
        assert m['raw_path']==case['model_path'] and m['raw_sha256']==case['model_sha256']
        packages.append(dict(manifest=manifest,path=m['raw_path'],sha256=m['raw_sha256'],bytes=m['raw_bytes'],parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_sha256=m['raw_sha256'],raw_bytes=m['raw_bytes'],raw_offset=0)]))
    literal_manifest=B+'hadamard_six_profile_cnf/profile_0000/model_package.json'
    literal=json.loads((ROOT/literal_manifest).read_bytes())
    packages.append(dict(manifest=literal_manifest,path=literal['raw_path'],sha256=literal['raw_sha256'],bytes=literal['raw_bytes'],parts=[dict(path=literal['gzip_path'],gzip_sha256=literal['gzip_sha256'],gzip_bytes=literal['gzip_bytes'],raw_sha256=literal['raw_sha256'],raw_bytes=literal['raw_bytes'],raw_offset=0)]))
    for record in proofs['records']:
        parts=[dict(p,path=common.relative((ROOT/proofpath).parent/p['relative_path']))for p in record['parts']]
        packages.append(dict(manifest=proofpath,path=record['raw_original_path'],sha256=record['raw_sha256'],bytes=record['raw_bytes'],parts=parts))
    assert {p['path']for p in packages}==set(local) and len(packages)==109
    for package in packages:
        whole=hashlib.sha256();total=0
        for part in package['parts']:
            check(part['path'],part['gzip_sha256'],package['manifest'])
            assert info(part['path'])['bytes']==part['gzip_bytes'] and part['raw_offset']==total
            chunk=hashlib.sha256();size=0
            with gzip.open(ROOT/part['path'],'rb')as stream:
                for block in iter(lambda:stream.read(1048576),b''):
                    whole.update(block);chunk.update(block);size+=len(block)
            assert size==part['raw_bytes'] and chunk.hexdigest()==part['raw_sha256'];total+=size
        assert total==package['bytes'] and whole.hexdigest()==package['sha256']
        check(package['path'],package['sha256'],package['manifest'])
        assert info(package['path'])['bytes']==total
        recovered.append({k:package[k]for k in ('path','sha256','bytes','manifest')}|dict(gzip_streams=len(package['parts'])))
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path']in selected;check(a['path'],a['sha256'],'CLAIMS.yaml')
    common.save(out/'reference_diagnostics.json',dict(errors=errors,count=len(errors)));assert not errors,f'{len(errors)} closure errors'
    paths=sorted(selected-set(local));git_hashes=common.git('hash-object','--stdin-paths',input=('\n'.join(paths)+'\n').encode()).decode().splitlines()
    gitrows=[]
    for p,sha in zip(paths,git_hashes,strict=True):
        raw=(ROOT/p).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha,('Git transforms',p)
        gitrows.append(dict(path=p,sha256=info(p)['sha256'],git_blob_sha1=sha))
    ignored=subprocess.run(['git','check-ignore','--stdin','-z'],cwd=ROOT,input=('\0'.join(paths)+'\0').encode(),capture_output=True)
    assert ignored.returncode in (0,1)
    common.save(out/'ignored_public_files.json',dict(paths=sorted(set(ignored.stdout.decode().split('\0'))-{''}),meaning='Exact files requiring explicit force-add if not yet tracked; no index edits performed.'))
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='LOCAL_ONLY'if p in local else'READY_FOR_PUBLICATION',limitation=local.get(p))for p in sorted(selected)],exact_directories=dirs,exact_files=files,
        local_tools=[info(p)for p in sorted(LOCAL_TOOLS)],prior_catalog=dict(path=PRIOR_CATALOG,sha256=PRIOR_CATALOG_SHA),prior_recoverable_dependencies=sorted(prior_recoverable),new_gzip_streams=sum(r['gzip_streams']for r in recovered),
        excluded_cohorts=['Later arbitrary-exception joint count-master preflight/build and subsequent scientific work.','Historical unregistered leftovers and protected user files.'],
        preserved_failures=['Seven-profile AC v1 inventory rejected512MiB allocation; separate v2 allocation768MiB and run01 partial checkpoint retained.'],
        unexecuted_preparations=[],mathematical_verification_performed=False))
    compressed_json(out/'reference_checks.json.gz',dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',records=refs,gzip_recoveries=recovered))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        ledger_sha256=hashlib.sha256(ledger_raw).hexdigest(),claim_ids=ids,claim_population=229,new_claims=13,verified_clear=226,candidate_clear=2,refuted_clear=1,target_resolution='UNKNOWN',preparation_only=args.prepare,
        research_payload_max_bytes=RESEARCH_LIMIT,metadata_wrapper_max_bytes=WRAPPER_LIMIT,metadata_wrapper_names=sorted(WRAPPER_NAMES),reference_format='reference_checks.json.gz: deterministic gzip (mtime=0, empty filename), UTF-8 JSON object with status, records and gzip_recoveries; sorted JSON keys; no lossy conversion.'))
    payload=sorted(set(paths)|{common.relative(p)for p in out.iterdir()if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,row in cache.items():assert common.digest(ROOT/p)==row['sha256'],('concurrent change',p)
    assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_raw and common.git('ls-files','--stage','-z')==index
    assert all(p.stat().st_size <= (WRAPPER_LIMIT if p.name in WRAPPER_NAMES else RESEARCH_LIMIT) for p in out.iterdir() if p.is_file()), 'preregistered wrapper size limit'
    status='TWENTYTHIRD_PREPARATION_CLOSURE_PASS'if args.prepare else'TWENTYTHIRD_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json',dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,selected_files=len(selected),public_research_files=len(paths),public_research_bytes=sum(info(p)['bytes']for p in paths),
        new_local_only_research_artifacts=109,new_gzip_streams=sum(r['gzip_streams']for r in recovered),recovered_raw_bytes=sum(r['bytes']for r in recovered),reference_bindings=len(refs),unique_referenced_files=len({r['path']for r in refs}),output_hashes={common.relative(p):common.digest(p)for p in out.iterdir()if p.is_file()}))
    print(json.dumps(dict(status=status,public_files=len(paths),local_originals=109)))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--prepare',action='store_true')
    for key in ['registration','extra-dir','extra-file']:ap.add_argument('--'+key,action='append',default=[])
    args=ap.parse_args();out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT) and common.relative(out) in ALLOWED_OUTPUTS;out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes()
    try:execute(args,out)
    except BaseException as error:
        (out/'failed_source.py').write_bytes(source);common.save(out/'failure.json',dict(error=repr(error),source_sha256=hashlib.sha256(source).hexdigest(),command=[sys.executable,*sys.argv],timestamp=datetime.now(timezone.utc).isoformat()));raise
if __name__=='__main__':main()
