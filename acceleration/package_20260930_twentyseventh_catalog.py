"""Explicit wave27 evidence closure; no solver/ledger/index edits."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, gzip, hashlib, io, json, subprocess, sys, yaml
from tqdm import tqdm
import package_20260930_eighth_catalog as common
import package_20260930_twentyseventh_recovery as recovery
# V2 caches only names already resolved exactly as repository-relative paths.
ROOT=common.ROOT; B='acceleration/results/20260930_'; I=B+'independent_review/'
REGISTRATIONS=['acceleration/results/20260930_twentyseventh_pilot_registration', 'acceleration/results/20260930_twentyseventh_psd_candidate_registration', 'acceleration/results/20260930_twentyseventh_campaign_gates_registration', 'acceleration/results/20260930_twentyseventh_psd_promotion', 'acceleration/results/20260930_twentyseventh_first12_proof_registration', 'acceleration/results/20260930_twentyseventh_inventory_registration']
DIRECTORIES=['acceleration/results/20260930_exact_eight_campaign_native_preparation', 'acceleration/results/20260930_exact_eight_campaign_native_preparation_v2', 'acceleration/results/20260930_exact_eight_campaign_preparation', 'acceleration/results/20260930_exact_eight_explicit_batch_preparation', 'acceleration/results/20260930_exact_eight_first12_cnfs', 'acceleration/results/20260930_exact_eight_first12_native_pilot', 'acceleration/results/20260930_exact_eight_first12_native_preflight', 'acceleration/results/20260930_exact_eight_next_lift', 'acceleration/results/20260930_exact_eight_next_lift_native_pilot', 'acceleration/results/20260930_exact_eight_next_lift_native_preflight', 'acceleration/results/20260930_exact_eight_next_lift_native_preparation', 'acceleration/results/20260930_exact_eight_population_inventory', 'acceleration/results/20260930_exact_eight_population_inventory_v2', 'acceleration/results/20260930_exact_eight_psd_screen', 'acceleration/results/20260930_independent_review/exact_eight_campaign', 'acceleration/results/20260930_independent_review/exact_eight_campaign_coverage', 'acceleration/results/20260930_independent_review/exact_eight_campaign_coverage_v2', 'acceleration/results/20260930_independent_review/exact_eight_campaign_inventory', 'acceleration/results/20260930_independent_review/exact_eight_campaign_object_calibration', 'acceleration/results/20260930_independent_review/exact_eight_first12_proofs', 'acceleration/results/20260930_independent_review/exact_eight_next_lift', 'acceleration/results/20260930_independent_review/exact_eight_next_lift_object_calibration', 'acceleration/results/20260930_independent_review/exact_eight_next_lift_unsat', 'acceleration/results/20260930_independent_review/exact_eight_psd_screen', 'acceleration/results/20260930_independent_review/triplicate_psd_kernel_options', 'acceleration/results/20260930_support_stabilizer_prior_work', 'acceleration/results/20260930_triplicate_psd_kernel_options', 'acceleration/results/20260930_twentyseventh_campaign_gates_registration', 'acceleration/results/20260930_twentyseventh_first12_proof_registration', 'acceleration/results/20260930_twentyseventh_inventory_registration', 'acceleration/results/20260930_twentyseventh_pilot_registration', 'acceleration/results/20260930_twentyseventh_psd_candidate_registration', 'acceleration/results/20260930_twentyseventh_psd_promotion', 'acceleration/results/20260930_twentyseventh_candidate_inventory', 'acceleration/results/20260930_twentyseventh_raw_recovery', 'acceleration/results/20260930_twentyseventh_recovery_controls']
FILES=['acceleration/audit_20260930_exact_eight_campaign.py', 'acceleration/audit_20260930_exact_eight_campaign_coverage.py', 'acceleration/audit_20260930_exact_eight_campaign_coverage_spec.md', 'acceleration/audit_20260930_exact_eight_campaign_coverage_v2.py', 'acceleration/audit_20260930_exact_eight_campaign_coverage_v2_spec.md', 'acceleration/audit_20260930_exact_eight_campaign_inventory.py', 'acceleration/audit_20260930_exact_eight_campaign_inventory_spec.md', 'acceleration/audit_20260930_exact_eight_campaign_spec.md', 'acceleration/audit_20260930_exact_eight_first12_proofs.py', 'acceleration/audit_20260930_exact_eight_next_lift.py', 'acceleration/audit_20260930_exact_eight_next_lift_unsat.py', 'acceleration/audit_20260930_exact_eight_population_core.py', 'acceleration/audit_20260930_exact_eight_psd_screen.py', 'acceleration/audit_20260930_exact_eight_psd_screen_spec.md', 'acceleration/audit_20260930_triplicate_psd_kernel_options.py', 'acceleration/audit_20260930_triplicate_psd_kernel_options_spec.md', 'acceleration/build_20260930_exact_eight_explicit_batch.py', 'acceleration/build_20260930_exact_eight_explicit_batch_spec.md', 'acceleration/build_20260930_exact_eight_first12.py', 'acceleration/check_20260930_twentyseventh_recovery_controls.py', 'acceleration/complete_20260930_exact_eight_campaign_native_v2.py', 'acceleration/correct_20260930_exact_eight_campaign_native_preparation.py', 'acceleration/inventory_20260930_twentyseventh_candidates.py', 'acceleration/inventory_20260930_twentyseventh_candidates_spec.md', 'acceleration/native_20260930_exact_eight_campaign.py', 'acceleration/native_20260930_exact_eight_campaign_spec.md', 'acceleration/native_20260930_exact_eight_campaign_v2.py', 'acceleration/native_20260930_exact_eight_campaign_v2_spec.md', 'acceleration/native_20260930_exact_eight_next_lift.py', 'acceleration/native_20260930_exact_eight_next_lift_spec.md', 'acceleration/package_20260930_twentyseventh_catalog.py', 'acceleration/package_20260930_twentyseventh_catalog_spec.md', 'acceleration/package_20260930_twentyseventh_recovery.py', 'acceleration/package_20260930_twentyseventh_recovery_spec.md', 'acceleration/prepare_20260930_exact_eight_campaign_native.py', 'acceleration/prepare_20260930_exact_eight_campaign_native_v2.py', 'acceleration/prepare_20260930_exact_eight_explicit_batch.py', 'acceleration/prepare_20260930_exact_eight_next_lift_native.py', 'acceleration/prepare_20260930_twentyseventh_catalog_source.py', 'acceleration/prepare_20260930_twentyseventh_inventory_source.py', 'acceleration/prepare_20260930_twentyseventh_recovery_helpers.py', 'acceleration/promote_20260930_twentyseventh_psd_claim.py', 'acceleration/record_20260930_support_stabilizer_prior_work.py', 'acceleration/record_20260930_twentyseventh_checkpoint.py', 'acceleration/recover_20260930_twentyseventh_raw_artifacts.py', 'acceleration/register_20260930_twentyseventh_campaign_gates.py', 'acceleration/register_20260930_twentyseventh_first12_proofs.py', 'acceleration/register_20260930_twentyseventh_inventory.py', 'acceleration/register_20260930_twentyseventh_pilot_claims.py', 'acceleration/register_20260930_twentyseventh_psd_candidate.py', 'acceleration/replay_20260930_twentyseventh_audits.py', 'acceleration/results/20260930_resume/claims_at_twentyseventh_milestone.yaml', 'acceleration/results/20260930_resume/twentyseventh_milestone_checkpoint.json', 'acceleration/results/20260930_resume/twentyseventh_process_snapshot.stderr.log', 'acceleration/results/20260930_resume/twentyseventh_process_snapshot.stdout.log', 'acceleration/results/20260930_resume/twentyseventh_replay_plan.json', 'acceleration/revise_20260930_exact_eight_population_inventory.py', 'acceleration/theory_20260930_exact_eight_campaign.py', 'acceleration/theory_20260930_exact_eight_campaign_plan.md', 'acceleration/theory_20260930_exact_eight_campaign_spec.md', 'acceleration/theory_20260930_exact_eight_next_lift.py', 'acceleration/theory_20260930_exact_eight_next_lift_plan.md', 'acceleration/theory_20260930_exact_eight_next_lift_spec.md', 'acceleration/theory_20260930_exact_eight_population_inventory.py', 'acceleration/theory_20260930_exact_eight_population_inventory_spec.md', 'acceleration/theory_20260930_exact_eight_population_inventory_v2.py', 'acceleration/theory_20260930_exact_eight_population_inventory_v2_spec.md', 'acceleration/theory_20260930_exact_eight_psd_screen.py', 'acceleration/theory_20260930_exact_eight_psd_screen_spec.md', 'acceleration/theory_20260930_triplicate_psd_kernel_options.py', 'acceleration/theory_20260930_triplicate_psd_kernel_options_spec.md', 'docs/AUDIT_20260930_EXACT_EIGHT_CAMPAIGN_COVERAGE.md', 'docs/AUDIT_20260930_EXACT_EIGHT_CAMPAIGN_COVERAGE_V2.md', 'docs/AUDIT_20260930_EXACT_EIGHT_CAMPAIGN_INVENTORY.md', 'docs/AUDIT_20260930_EXACT_EIGHT_FIRST12_PROOFS.md', 'docs/AUDIT_20260930_EXACT_EIGHT_NEXT_LIFT.md', 'docs/AUDIT_20260930_EXACT_EIGHT_NEXT_LIFT_UNSAT.md', 'docs/AUDIT_20260930_EXACT_EIGHT_PSD_SCREEN.md', 'docs/AUDIT_20260930_TRIPLICATE_PSD_KERNEL_OPTIONS.md', 'docs/PLAN_20260930_EXACT_EIGHT_CAMPAIGN_INDEPENDENT_AUDIT.md', 'docs/RESEARCH_20260930_TWENTYSEVENTH_WAVE.md']
FORBIDDEN_DIRECTORIES=['acceleration/results/20260930_exact_eight_next32', 'acceleration/results/20260930_independent_review/exact_eight_next32', 'acceleration/results/20260930_independent_review/exact_eight_first12_union', 'acceleration/results/20260930_independent_review/exact_eight_first12_union_v2', 'acceleration/results/20260930_exact_eight_explicit_batch_preparation_v2']
FORBIDDEN_FILES=['PROMPT.md', 'acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log']
FORBIDDEN_TOKENS=['next32', 'NEXT32', 'first12_union', 'FIRST12_UNION', 'explicit_batch_v2', 'explicit_batch_preparation_v2']
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_CATALOG='acceleration/results/20260930_twentysixth_artifact_packaging/catalog.json'
PRIOR_CATALOG_SHA='d27a41ee61c1ed7453682ae69dd5a041e94e47e91d2aacaaf9b9c429619e27fb'
RESEARCH_LIMIT=10*1024**2
WRAPPER_LIMIT=32*1024**2
WRAPPER_NAMES={'catalog.json','stage_inventory.json','reference_checks.json.gz'}
ALLOWED_OUTPUTS={'acceleration/results/20260930_twentyseventh_artifact_packaging', 'acceleration/results/20260930_twentyseventh_preparation'}
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
        compressed_json(path,dict(schema='WAVE27_REFERENCE_CHUNK_V1',index=index,records=self.buffer))
        assert path.stat().st_size<=RESEARCH_LIMIT
        self.parts.append(dict(path=common.relative(path),sha256=common.digest(path),bytes=path.stat().st_size,index=index,record_offset=self.count-len(self.buffer),records=len(self.buffer)))
        self.buffer=[]
    def finish(self,recovered):
        self.flush()
        return dict(schema='WAVE27_REFERENCE_MANIFEST_V1',status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',record_count=self.count,unique_referenced_files=len(self.unique),parts=self.parts,gzip_recoveries=recovered)

def execute(args,out):
    ledger_raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledger_raw)
    assert hashlib.sha256(ledger_raw).hexdigest()=='5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237'
    assert len(ledger['claims'])==286
    assert Counter((c['status'],c['review_state'])for c in ledger['claims'])=={('VERIFIED','CLEAR'):281,('CANDIDATE','CLEAR'):3,('REFUTED','CLEAR'):2}
    assert args.registration==REGISTRATIONS, 'exact ordered six-registration chain'
    artifacts={a['id']:a for a in ledger['artifacts']}
    ids=[];previous=None
    for directory in args.registration:
        receipt=json.loads((ROOT/directory/'summary.json').read_bytes())
        before=(ROOT/directory/'CLAIMS.before.yaml').read_bytes();after=(ROOT/directory/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or previous==before
        previous=after;ids.extend(receipt.get('new_claim_ids',[]))
    assert previous==ledger_raw and len(ids)==len(set(ids))==8
    promotion=json.loads((ROOT/(B+'twentyseventh_psd_promotion/summary.json')).read_bytes())
    assert promotion['promoted_claim_ids']==['C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN']and promotion['from_revision']==1 and promotion['to_revision']==2
    claims=[c for c in ledger['claims']if c['id']in ids]
    assert len(claims)==8 and Counter((c['status'],c['review_state']) for c in claims)=={('VERIFIED','CLEAR'):8}
    dirs=DIRECTORIES+args.registration+args.extra_dir;files=FILES+args.extra_file
    selected=set(files)
    for directory in dirs:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    for p in selected:
        assert not any(token in p for token in FORBIDDEN_TOKENS),('future wave27',p)
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
    recovery_path=B+'twentyseventh_raw_recovery/manifest.json'
    assert common.digest(ROOT/recovery_path)=='d6d5e3933cd8294b4f4119c6ba495780a77cf19833ecb056598a863bbef11958'
    assert packages==json.loads((ROOT/recovery_path).read_bytes())['records']
    local={r['path']:'Raw artifact retained LOCAL_ONLY; exact public gzip recovery available.' for r in packages}
    assert set(local)<=selected
    cache={};resolution_cache={};refs=ReferenceWriter(out);errors=[];recovered=[]
    def info(p):
        if p not in cache:
            assert not any(token in p for token in FORBIDDEN_TOKENS)and p not in FORBIDDEN_FILES and not p.startswith('tools/'),('protected/future reference before read',p)
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
                if key in common.MAP_KEYS|{'outputs_sha256','input_sha256','checked_artifact_hashes'}and isinstance(value,dict):
                    for p,sha in value.items():
                        if isinstance(sha,str)and common.HEX.fullmatch(sha):check(p,sha,origin)
                walk(value,origin)
            if isinstance(obj.get('path'),str)and isinstance(obj.get('sha256'),str)and common.HEX.fullmatch(obj['sha256']):
                check(obj['path'],obj['sha256'],origin,'conway-99-research'in obj.get('repository',''))
        elif isinstance(obj,list):
            for value in obj:walk(value,origin)
    for path in tqdm(sorted(selected),desc="Check wave27 artifacts",mininterval=1):
        assert path in local or info(path)['bytes'] <= (WRAPPER_LIMIT if path in METADATA_WRAPPERS else RESEARCH_LIMIT),('oversize',path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    # Stream each public gzip independently and compare the whole restored raw original.
    for package in tqdm(packages,desc="Recover wave27 identities",mininterval=1):
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
        excluded_cohorts=['Wave28 next32 cohorts, explicit-builderv2, and first12 union.','Historical unregistered leftovers and protected user files.'],
        preserved_failures=['Native preparation/source failures, inventory v1 and coverage v1 preserved unchanged.','PSD intermediate candidate revision1 and verified revision2 retained in registration chain.'],
        unexecuted_preparations=['Source-only explicit build-batch interface v1; no additional build was executed by that preparation.'],mathematical_verification_performed=False))
    compressed_json(out/'reference_checks.json.gz',refs.finish(recovered))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        ledger_sha256=hashlib.sha256(ledger_raw).hexdigest(),claim_ids=ids,claim_population=286,new_claims=8,verified_clear=281,candidate_clear=3,refuted_clear=2,target_resolution='UNKNOWN',preparation_only=args.prepare,
        research_payload_max_bytes=RESEARCH_LIMIT,metadata_wrapper_max_bytes=WRAPPER_LIMIT,metadata_wrapper_names=sorted(WRAPPER_NAMES),reference_format='WAVE27_REFERENCE_MANIFEST_V1: deterministic gzip JSON manifest with ordered <=25000-record WAVE27_REFERENCE_CHUNK_V1 gzip parts, whole part hashes/lengths and record offsets/counts; every part <=10MiB, manifest <=32MiB. All use mtime=0, empty filename, sorted keys and LF.'))
    payload=sorted(set(paths)|{common.relative(p)for p in out.iterdir()if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,row in cache.items():assert common.digest(ROOT/p)==row['sha256'],('concurrent change',p)
    assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_raw and common.git('ls-files','--stage','-z')==index
    assert all(p.stat().st_size <= (WRAPPER_LIMIT if p.name in WRAPPER_NAMES else RESEARCH_LIMIT) for p in out.iterdir() if p.is_file()), 'preregistered wrapper size limit'
    status='TWENTYSEVENTH_PREPARATION_CLOSURE_PASS'if args.prepare else'TWENTYSEVENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
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
