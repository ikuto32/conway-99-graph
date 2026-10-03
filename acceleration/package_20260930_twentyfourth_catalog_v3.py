"""Explicit wave24 evidence closure; no solver/ledger/index edits."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, gzip, hashlib, io, json, subprocess, sys, yaml
import package_20260930_eighth_catalog as common
import package_20260930_twentyfourth_recovery as recovery
# V2 caches only names already resolved exactly as repository-relative paths.
ROOT=common.ROOT; B='acceleration/results/20260930_'; I=B+'independent_review/'
REGISTRATIONS=['acceleration/results/20260930_twentyfourth_base_registration', 'acceleration/results/20260930_twentyfourth_count_registration', 'acceleration/results/20260930_twentyfourth_gram_registration', 'acceleration/results/20260930_twentyfourth_final_registration']
DIRECTORIES=['acceleration/results/20260930_count_interval_cnf', 'acceleration/results/20260930_count_interval_frechet_package', 'acceleration/results/20260930_count_interval_frechet_parse_failure', 'acceleration/results/20260930_count_interval_frechet_v2', 'acceleration/results/20260930_count_interval_inventory', 'acceleration/results/20260930_count_interval_witness', 'acceleration/results/20260930_count_master_eight_orbit_cuts', 'acceleration/results/20260930_count_profile_gram_blocks', 'acceleration/results/20260930_count_witness_interval_screen', 'acceleration/results/20260930_eight_count_profile_lift', 'acceleration/results/20260930_eight_count_profile_native_pilot', 'acceleration/results/20260930_eight_count_profile_native_preflight', 'acceleration/results/20260930_hadamard_count_gram_intervals', 'acceleration/results/20260930_hadamard_count_master_cnf', 'acceleration/results/20260930_hadamard_count_master_native_pilot', 'acceleration/results/20260930_hadamard_count_master_native_pilot_v2', 'acceleration/results/20260930_hadamard_count_master_native_preflight', 'acceleration/results/20260930_hadamard_count_master_preflight', 'acceleration/results/20260930_hadamard_gram_affine_gf2', 'acceleration/results/20260930_hadamard_seven_profile_batch_native', 'acceleration/results/20260930_hadamard_seven_profile_batch_preflight', 'acceleration/results/20260930_hadamard_seven_profile_cnf', 'acceleration/results/20260930_hadamard_seven_profile_native_pilot', 'acceleration/results/20260930_hadamard_seven_profile_native_preflight', 'acceleration/results/20260930_hadamard_seven_profile_proof_package', 'acceleration/results/20260930_hadamard_seven_remaining_cnfs', 'acceleration/results/20260930_hadamard_seven_remaining_selection', 'acceleration/results/20260930_seven_profile_batch_v2_preparation', 'acceleration/results/20260930_twentyfourth_count_registration_preflight_failure', 'acceleration/results/20260930_twentyfourth_final_registration_schema_failure', 'acceleration/results/20260930_twentyfourth_literal_proof_package', 'acceleration/results/20260930_independent_review/count_gram_intervals', 'acceleration/results/20260930_independent_review/count_interval_claim_bindings', 'acceleration/results/20260930_independent_review/count_interval_cnf', 'acceleration/results/20260930_independent_review/count_interval_constructed_object', 'acceleration/results/20260930_independent_review/count_interval_object_calibration', 'acceleration/results/20260930_independent_review/count_master_claim_binding', 'acceleration/results/20260930_independent_review/count_master_eight_orbit_cuts', 'acceleration/results/20260930_independent_review/count_master_extension_design', 'acceleration/results/20260930_independent_review/count_master_sat_outcome', 'acceleration/results/20260930_independent_review/count_profile_gram_blocks', 'acceleration/results/20260930_independent_review/count_witness_intervals', 'acceleration/results/20260930_independent_review/count_witness_intervals_v2', 'acceleration/results/20260930_independent_review/eight_count_profile_lift', 'acceleration/results/20260930_independent_review/eight_count_profile_lift_object_calibration', 'acceleration/results/20260930_independent_review/eight_count_profile_unsat', 'acceleration/results/20260930_independent_review/hadamard_count_master_cnf', 'acceleration/results/20260930_independent_review/hadamard_count_master_cnf_correction', 'acceleration/results/20260930_independent_review/hadamard_count_master_cnf_v2', 'acceleration/results/20260930_independent_review/hadamard_count_master_object_calibration', 'acceleration/results/20260930_independent_review/hadamard_count_master_preflight', 'acceleration/results/20260930_independent_review/hadamard_gram_affine_gf2', 'acceleration/results/20260930_independent_review/hadamard_seven_profile_cnf', 'acceleration/results/20260930_independent_review/hadamard_seven_profile_object_calibration', 'acceleration/results/20260930_independent_review/hadamard_seven_profile_union', 'acceleration/results/20260930_independent_review/hadamard_seven_profile_union_preparation', 'acceleration/results/20260930_independent_review/hadamard_seven_profile_unsat', 'acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_profile_cnfs', 'acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_profile_cnfs_v2', 'acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_profile_object_calibration', 'acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_profile_proofs', 'acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_proof_transport', 'acceleration/results/20260930_independent_review/local_frechet_equality']
FILES=['acceleration/audit_20260930_count_gram_intervals.py', 'acceleration/audit_20260930_count_interval_cnf.py', 'acceleration/audit_20260930_count_interval_object.py', 'acceleration/audit_20260930_count_master_eight_orbit_cuts.py', 'acceleration/audit_20260930_count_master_extension_design.py', 'acceleration/audit_20260930_count_master_sat_outcome.py', 'acceleration/audit_20260930_count_profile_gram_blocks.py', 'acceleration/audit_20260930_count_witness_intervals.py', 'acceleration/audit_20260930_count_witness_intervals_v2.py', 'acceleration/audit_20260930_eight_count_profile_lift.py', 'acceleration/audit_20260930_eight_count_profile_unsat.py', 'acceleration/audit_20260930_hadamard_count_master_cnf.py', 'acceleration/audit_20260930_hadamard_count_master_cnf_v2.py', 'acceleration/audit_20260930_hadamard_count_master_object.py', 'acceleration/audit_20260930_hadamard_count_master_preflight.py', 'acceleration/audit_20260930_hadamard_gram_affine_gf2.py', 'acceleration/audit_20260930_hadamard_seven_profile.py', 'acceleration/audit_20260930_hadamard_seven_profile_union.py', 'acceleration/audit_20260930_hadamard_seven_profile_union_spec.md', 'acceleration/audit_20260930_hadamard_seven_profile_unsat.py', 'acceleration/audit_20260930_hadamard_twohundredfifteen_profile_object.py', 'acceleration/audit_20260930_hadamard_twohundredfifteen_profile_proofs.py', 'acceleration/audit_20260930_hadamard_twohundredfifteen_profile_proofs_spec.md', 'acceleration/audit_20260930_hadamard_twohundredfifteen_profiles.py', 'acceleration/audit_20260930_hadamard_twohundredfifteen_profiles_v2.py', 'acceleration/audit_20260930_hadamard_twohundredfifteen_proof_transport.py', 'acceleration/audit_20260930_local_frechet_equality.py', 'acceleration/build_20260930_hadamard_seven_remaining_profiles.py', 'acceleration/build_20260930_hadamard_seven_remaining_profiles_spec.md', 'acceleration/native_20260930_count_interval.py', 'acceleration/native_20260930_count_interval_spec.md', 'acceleration/native_20260930_eight_count_profile_lift.py', 'acceleration/native_20260930_eight_count_profile_lift_spec.md', 'acceleration/native_20260930_hadamard_count_master.py', 'acceleration/native_20260930_hadamard_count_master_spec.md', 'acceleration/native_20260930_hadamard_seven_profile.py', 'acceleration/native_20260930_hadamard_seven_profile_batch.py', 'acceleration/native_20260930_hadamard_seven_profile_batch_spec.md', 'acceleration/native_20260930_hadamard_seven_profile_batch_v2.py', 'acceleration/native_20260930_hadamard_seven_profile_batch_v2_spec.md', 'acceleration/native_20260930_hadamard_seven_profile_spec.md', 'acceleration/package_20260930_count_interval_frechet.py', 'acceleration/package_20260930_seven_profile_proofs.py', 'acceleration/package_20260930_seven_profile_proofs_spec.md', 'acceleration/package_20260930_twentyfourth_catalog.py', 'acceleration/package_20260930_twentyfourth_catalog_spec.md', 'acceleration/package_20260930_twentyfourth_literal_proofs.py', 'acceleration/package_20260930_twentyfourth_recovery.py', 'acceleration/record_20260930_count_interval_audit_bindings.py', 'acceleration/record_20260930_count_master_audit_bindings.py', 'acceleration/record_20260930_count_master_binding_manifest.py', 'acceleration/recover_20260930_seven_profile_proofs.py', 'acceleration/register_20260930_twentyfourth_base.py', 'acceleration/register_20260930_twentyfourth_count_claims.py', 'acceleration/register_20260930_twentyfourth_count_claims_v2.py', 'acceleration/register_20260930_twentyfourth_final_claims.py', 'acceleration/register_20260930_twentyfourth_final_claims_v2.py', 'acceleration/register_20260930_twentyfourth_gram_claims.py', 'acceleration/results/20260930_resume/twentythird_publication_ci_completion.json', 'acceleration/results/20260930_resume/twentythird_publication_observation.json', 'acceleration/results/20260930_resume/twentythird_replay_guide_correction.json', 'acceleration/select_20260930_hadamard_seven_remaining_profiles.py', 'acceleration/select_20260930_hadamard_seven_remaining_profiles_spec.md', 'acceleration/theory_20260930_count_interval_cnf.py', 'acceleration/theory_20260930_count_interval_cnf_spec.md', 'acceleration/theory_20260930_count_interval_frechet.py', 'acceleration/theory_20260930_count_interval_frechet_spec.md', 'acceleration/theory_20260930_count_interval_frechet_v2.py', 'acceleration/theory_20260930_count_interval_frechet_v2_spec.md', 'acceleration/theory_20260930_count_interval_inventory.py', 'acceleration/theory_20260930_count_interval_inventory_spec.md', 'acceleration/theory_20260930_count_interval_witness.py', 'acceleration/theory_20260930_count_interval_witness_spec.md', 'acceleration/theory_20260930_count_master_eight_orbit_cuts.py', 'acceleration/theory_20260930_count_master_eight_orbit_cuts_spec.md', 'acceleration/theory_20260930_count_profile_gram_blocks.py', 'acceleration/theory_20260930_count_profile_gram_blocks_spec.md', 'acceleration/theory_20260930_count_witness_interval_screen.py', 'acceleration/theory_20260930_count_witness_interval_screen_spec.md', 'acceleration/theory_20260930_eight_count_profile_lift.py', 'acceleration/theory_20260930_eight_count_profile_lift_spec.md', 'acceleration/theory_20260930_hadamard_count_gram_intervals.py', 'acceleration/theory_20260930_hadamard_count_gram_intervals_spec.md', 'acceleration/theory_20260930_hadamard_count_master_cnf.py', 'acceleration/theory_20260930_hadamard_count_master_cnf_spec.md', 'acceleration/theory_20260930_hadamard_count_master_preflight.py', 'acceleration/theory_20260930_hadamard_count_master_preflight_spec.md', 'acceleration/theory_20260930_hadamard_gram_affine_gf2.py', 'acceleration/theory_20260930_hadamard_gram_affine_gf2_spec.md', 'acceleration/theory_20260930_hadamard_seven_profile_cnf.py', 'acceleration/theory_20260930_hadamard_seven_profile_cnf_general.py', 'acceleration/theory_20260930_hadamard_seven_profile_cnf_general_spec.md', 'acceleration/theory_20260930_hadamard_seven_profile_cnf_spec.md', 'docs/AUDIT_20260930_COUNT_GRAM_INTERVALS.md', 'docs/AUDIT_20260930_COUNT_INTERVAL_CNF.md', 'docs/AUDIT_20260930_COUNT_INTERVAL_OBJECT.md', 'docs/AUDIT_20260930_COUNT_MASTER_AT_LEAST_SEVEN.md', 'docs/AUDIT_20260930_COUNT_MASTER_EIGHT_ORBIT_CUTS.md', 'docs/AUDIT_20260930_COUNT_PROFILE_GRAM_BLOCKS.md', 'docs/AUDIT_20260930_EIGHT_COUNT_PROFILE_LIFT.md', 'docs/AUDIT_20260930_EIGHT_COUNT_PROFILE_UNSAT.md', 'docs/AUDIT_20260930_HADAMARD_COUNT_MASTER_CNF.md', 'docs/AUDIT_20260930_HADAMARD_COUNT_MASTER_OBJECT.md', 'docs/AUDIT_20260930_HADAMARD_COUNT_MASTER_PREFLIGHT.md', 'docs/AUDIT_20260930_HADAMARD_GRAM_AFFINE_GF2.md', 'docs/AUDIT_20260930_HADAMARD_SEVEN_PROFILE0001_UNSAT.md', 'docs/AUDIT_20260930_HADAMARD_SEVEN_PROFILE_CNF.md', 'docs/AUDIT_20260930_HADAMARD_TWOHUNDREDFIFTEEN_PROFILES.md', 'docs/AUDIT_20260930_HADAMARD_TWOHUNDREDFIFTEEN_PROFILES_V2.md', 'docs/AUDIT_20260930_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_OBJECT.md', 'docs/AUDIT_20260930_HADAMARD_TWOHUNDREDFIFTEEN_PROOF_TRANSPORT.md', 'docs/AUDIT_20260930_LOCAL_FRECHET_EQUALITY_REFUTATION.md', 'docs/AUDIT_20260930_SEVEN_PROFILE_UNION.md', 'docs/DERIVATION_20260930_COUNT_MASTER_EIGHT_ORBIT_CUTS.md', 'docs/REPRODUCING_20260930_TWENTYTHIRD_WAVE_V2.md']
FILES += [B+'twentyfourth_raw_recovery/manifest.json',B+'twentyfourth_catalog_inventory_plan/inventory.json','acceleration/package_20260930_twentyfourth_catalog_v2.py','acceleration/package_20260930_twentyfourth_catalog_v2_spec.md']
FILES += ['acceleration/package_20260930_twentyfourth_catalog_v3.py','acceleration/package_20260930_twentyfourth_catalog_v3_spec.md']
FORBIDDEN_DIRECTORIES=['acceleration/results/20260930_count_master_eight_orbit_cut_native_pilot', 'acceleration/results/20260930_count_master_eight_orbit_cut_native_preflight', 'acceleration/results/20260930_independent_review/count_master_eight_orbit_cut_object_calibration']
FORBIDDEN_FILES=['acceleration/audit_20260930_count_master_eight_orbit_cut_object.py', 'acceleration/audit_20260930_count_master_eight_orbit_cut_object_spec.md', 'acceleration/native_20260930_count_master_eight_orbit_cuts.py', 'acceleration/native_20260930_count_master_eight_orbit_cuts_spec.md', 'docs/AUDIT_20260930_COUNT_MASTER_EIGHT_ORBIT_CUT_OBJECT.md']
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_CATALOG=B+'twentythird_artifact_packaging/catalog.json'
PRIOR_CATALOG_SHA='5683804e5a4e0e42e50024799f05102d202665ec1b67c7f0dcb1917342dc1265'
RESEARCH_LIMIT=10*1024**2
WRAPPER_LIMIT=32*1024**2
WRAPPER_NAMES={'catalog.json','stage_inventory.json','reference_checks.json.gz'}
ALLOWED_OUTPUTS={B+'twentyfourth_preparation',B+'twentyfourth_artifact_packaging'}
METADATA_WRAPPERS={directory+'/'+name for directory in ALLOWED_OUTPUTS for name in WRAPPER_NAMES}

def compressed_json(path, value):
    """Deterministic single gzip stream: UTF-8 JSON, sorted keys, LF, mtime=0."""
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as gz:
            with io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as text:
                json.dump(value,text,sort_keys=True,separators=(',',':'));text.write('\n')

class ReferenceWriter:
    """Bounded reference buffers; exact ordered records in deterministic chunks."""
    def __init__(self,out):
        self.out=out;self.buffer=[];self.parts=[];self.count=0;self.unique=set()
    def append(self,row):
        self.buffer.append(row);self.count+=1;self.unique.add(row['path'])
        if len(self.buffer)==25000:self.flush()
    def flush(self):
        if not self.buffer:return
        index=len(self.parts);path=self.out/f'reference_checks.part{index:04d}.json.gz'
        compressed_json(path,dict(schema='WAVE24_REFERENCE_CHUNK_V1',index=index,records=self.buffer))
        assert path.stat().st_size<=RESEARCH_LIMIT
        self.parts.append(dict(path=common.relative(path),sha256=common.digest(path),bytes=path.stat().st_size,index=index,record_offset=self.count-len(self.buffer),records=len(self.buffer)))
        self.buffer=[]
    def finish(self,recovered):
        self.flush()
        return dict(schema='WAVE24_REFERENCE_MANIFEST_V1',status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',record_count=self.count,unique_referenced_files=len(self.unique),parts=self.parts,gzip_recoveries=recovered)

def execute(args,out):
    ledger_raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledger_raw)
    assert hashlib.sha256(ledger_raw).hexdigest()=='ee94a175838c99a0021ec409dbf6a43c326008f8ca8d8223867f56f4ece2707a'
    assert len(ledger['claims'])==248
    assert Counter((c['status'],c['review_state'])for c in ledger['claims'])=={('VERIFIED','CLEAR'):244,('CANDIDATE','CLEAR'):2,('REFUTED','CLEAR'):2}
    assert args.registration==REGISTRATIONS, 'exact ordered four-registration chain'
    artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[];previous=None
    for directory in args.registration:
        receipt=json.loads((ROOT/directory/'summary.json').read_bytes())
        before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids.extend(receipt['new_claim_ids'])
    assert previous==ledger_raw and len(ids)==len(set(ids))==19
    claims=[c for c in ledger['claims']if c['id']in ids]
    assert len(claims)==19 and Counter((c['status'],c['review_state']) for c in claims)=={('VERIFIED','CLEAR'):18,('REFUTED','CLEAR'):1}
    dirs=DIRECTORIES+args.registration+args.extra_dir;files=FILES+args.extra_file
    selected=set(files)
    for directory in dirs:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    for p in selected:
        assert not any(p==d or p.startswith(d+'/') for d in FORBIDDEN_DIRECTORIES),('future cohort',p)
        assert p!='PROMPT.md' and not p.startswith('tools/drat-trim') and p not in FORBIDDEN_FILES and p != 'acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log'
        assert Path(p).name.lower() not in {'.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'}
        assert not p.endswith(('.pem','.key')),('protected/private file type',p)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z')
    assert PRIOR_CATALOG in tracked and common.digest(ROOT/PRIOR_CATALOG)==PRIOR_CATALOG_SHA
    prior=json.loads((ROOT/PRIOR_CATALOG).read_bytes())
    prior_recoverable=set(prior['prior_recoverable_dependencies'])
    prior_recoverable.update(r['path']for r in prior['entries']if r['availability']=='LOCAL_ONLY'and 'recovery available'in r['limitation'])
    packages=recovery.packages()
    recovery_path=B+'twentyfourth_raw_recovery/manifest.json'
    assert common.digest(ROOT/recovery_path)=='2311cebb8617c95c3ae3a4225def8ce2dce8992ae9621cdcfd8cf0684806c3c8'
    assert packages==json.loads((ROOT/recovery_path).read_bytes())['records']
    local={r['path']:'Raw artifact retained LOCAL_ONLY; exact public gzip recovery available.' for r in packages}
    assert set(local)<=selected
    cache={};resolution_cache={};refs=ReferenceWriter(out);errors=[];recovered=[]
    def info(p):
        if p not in cache:
            path=ROOT/p;assert path.is_file()and path.resolve().is_relative_to(ROOT),p
            cache[p]=dict(path=p,sha256=common.digest(path),bytes=path.stat().st_size)
        return cache[p]
    def check(name,expected,origin,archive=False):
        if any(origin==d+'/validation.json'for d in args.registration) and common.resolve_ref(name,ROOT/origin)=='CLAIMS.yaml':
            snapshot=origin.rsplit('/',1)[0]+'/CLAIMS.after.yaml'
            assert common.digest(ROOT/snapshot)==expected;name=snapshot
        if name in artifacts:
            a=artifacts[name];assert a['sha256']==expected;name=a['path']
        path=resolution_cache.get(name) if not archive else None
        if path is None:
            path=common.resolve_ref(name,ROOT/origin,archive)
            if not archive and path==name:resolution_cache[name]=path
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
        excluded_cohorts=['Wave25 six-orbit-cut native/object pilot and later full-catalogue preparations.','Historical unregistered leftovers and protected user files.'],
        preserved_failures=['Count-master metadata checker v1; interval witness metadata checker v1; Frechet parse v1; numeric-vs-lexical 215-profile checker v1; count/final registrar preflight failures; native source preparations and failed count-pilot invocation.'],
        unexecuted_preparations=[],mathematical_verification_performed=False))
    compressed_json(out/'reference_checks.json.gz',refs.finish(recovered))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        ledger_sha256=hashlib.sha256(ledger_raw).hexdigest(),claim_ids=ids,claim_population=248,new_claims=19,verified_clear=244,candidate_clear=2,refuted_clear=2,target_resolution='UNKNOWN',preparation_only=args.prepare,
        research_payload_max_bytes=RESEARCH_LIMIT,metadata_wrapper_max_bytes=WRAPPER_LIMIT,metadata_wrapper_names=sorted(WRAPPER_NAMES),reference_format='WAVE24_REFERENCE_MANIFEST_V1: deterministic gzip JSON manifest with ordered <=25000-record WAVE24_REFERENCE_CHUNK_V1 gzip parts, whole part hashes/lengths and record offsets/counts; every part <=10MiB, manifest <=32MiB. All use mtime=0, empty filename, sorted keys and LF.'))
    payload=sorted(set(paths)|{common.relative(p)for p in out.iterdir()if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,row in cache.items():assert common.digest(ROOT/p)==row['sha256'],('concurrent change',p)
    assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_raw and common.git('ls-files','--stage','-z')==index
    assert all(p.stat().st_size <= (WRAPPER_LIMIT if p.name in WRAPPER_NAMES else RESEARCH_LIMIT) for p in out.iterdir() if p.is_file()), 'preregistered wrapper size limit'
    status='TWENTYFOURTH_PREPARATION_CLOSURE_PASS'if args.prepare else'TWENTYFOURTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json',dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,selected_files=len(selected),public_research_files=len(paths),public_research_bytes=sum(info(p)['bytes']for p in paths),
        new_local_only_research_artifacts=len(local),new_gzip_streams=sum(r['gzip_streams']for r in recovered),recovered_raw_bytes=sum(r['bytes']for r in recovered),reference_bindings=refs.count,unique_referenced_files=len(refs.unique),reference_parts=len(refs.parts),output_hashes={common.relative(p):common.digest(p)for p in out.iterdir()if p.is_file()}))
    print(json.dumps(dict(status=status,public_files=len(paths),local_originals=len(local))))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--prepare',action='store_true')
    for key in ['registration','extra-dir','extra-file']:ap.add_argument('--'+key,action='append',default=[])
    args=ap.parse_args();out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT) and common.relative(out) in ALLOWED_OUTPUTS;out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes()
    try:execute(args,out)
    except BaseException as error:
        (out/'failed_source.py').write_bytes(source);common.save(out/'failure.json',dict(error=repr(error),source_sha256=hashlib.sha256(source).hexdigest(),command=[sys.executable,*sys.argv],timestamp=datetime.now(timezone.utc).isoformat()));raise
if __name__=='__main__':main()
