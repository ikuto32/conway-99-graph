"""Explicit seventeenth publication closure, derived from frozen sixteenth checker."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,yaml
import package_20260930_eighth_catalog as common
import recover_20260930_seventeenth_inputs as recovery
ROOT=common.ROOT;B='acceleration/results/20260930_';I=B+'independent_review/'
REGISTRATIONS=[(B+'seventeenth_cyclic_registration',3),(B+'seventeenth_model_projection_registration',3)]
DIRS=[B+p for p in ['hadamard_six_prism_cyclic_cnf','hadamard_cyclic_native_preflight','hadamard_cyclic_native_pilot',
 'hadamard_cyclic_proof_packages','hadamard_prism_ordered_cnf','hadamard_prism_ordered_native_preflight','hadamard_prism_ordered_native_pilot',
 'hadamard_triplicate_counts']]+[p for p,_ in REGISTRATIONS]+[I+p for p in ['hadamard_six_prism_cyclic_reduction',
 'hadamard_cyclic_factor_cnf','hadamard_cyclic_factor_object_calibration','hadamard_cyclic_unsat','hadamard_cyclic_named_dependencies',
 'hadamard_prism_ordered_cnf','hadamard_prism_ordered_object_calibration','hadamard_prism_ordered_outcome_calibration',
 'hadamard_prism_ordered_native_outcome','hadamard_triplicate_counts','hadamard_triplicate_counts_v2','fixed_support_raw_preparation']]
FILES=['acceleration/'+p for p in ['theory_20260930_hadamard_cyclic_factor.py','theory_20260930_hadamard_cyclic_factor_spec.md',
 'audit_20260930_hadamard_cyclic_reduction.py','audit_20260930_hadamard_cyclic_factor_cnf.py','audit_20260930_hadamard_cyclic_factor_object.py',
 'audit_20260930_hadamard_cyclic_unsat.py','bind_20260930_hadamard_cyclic_dependencies.py','package_20260930_hadamard_cyclic_proof.py',
 'native_20260930_hadamard_cyclic.py','native_20260930_hadamard_cyclic_spec.md',
 'theory_20260930_hadamard_prism_ordered_cnf.py','theory_20260930_hadamard_prism_ordered_cnf_spec.md',
 'audit_20260930_hadamard_prism_ordered_cnf.py','audit_20260930_hadamard_prism_ordered_object.py','audit_20260930_hadamard_prism_ordered_outcome.py',
 'native_20260930_hadamard_prism_ordered.py','native_20260930_hadamard_prism_ordered_spec.md',
 'theory_20260930_hadamard_triplicate_counts.py','theory_20260930_hadamard_triplicate_counts_spec.md',
 'audit_20260930_hadamard_triplicate_counts.py','audit_20260930_hadamard_triplicate_counts_v2.py','repair_20260930_triplicate_checker_field.py',
 'audit_20260930_fixed_support_raw_preparation.py','audit_20260930_fixed_support_coloring_cnf.py',
 'register_20260930_seventeenth_cyclic.py','register_20260930_seventeenth_model_projection.py',
 'recover_20260930_seventeenth_inputs.py','package_20260930_seventeenth_catalog.py']]+['docs/'+p for p in [
 'DERIVATION_20260930_HADAMARD_CYCLIC_FACTOR.md','AUDIT_20260930_HADAMARD_CYCLIC_REDUCTION.md','AUDIT_20260930_HADAMARD_CYCLIC_FACTOR_CNF.md',
 'AUDIT_20260930_HADAMARD_CYCLIC_FACTOR_OBJECT.md','AUDIT_20260930_HADAMARD_CYCLIC_UNSAT.md',
 'AUDIT_20260930_HADAMARD_PRISM_ORDERED_CNF.md','AUDIT_20260930_HADAMARD_PRISM_ORDERED_OBJECT.md','AUDIT_20260930_HADAMARD_PRISM_ORDERED_OUTCOME.md',
 'DERIVATION_20260930_HADAMARD_TRIPLICATE_COUNTS.md','REVIEW_PLAN_20260930_FIXED_SUPPORT_COLORING.md','AUDIT_20260930_FIXED_SUPPORT_COLORING.md',
 'REPRODUCING_20260930_SEVENTEENTH_WAVE.md']]
LOCAL_FIXED={B+'hadamard_prism_ordered_native_pilot/main/proof.drat':'Incomplete UNKNOWN trace, LOCAL_ONLY without recovery; not an UNSAT certificate.'}
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_PACKAGES={
 B+'variable_core_factor_cnf/artifact_packages.json':'46867dcccbb99bd72379b50a7415e6dd1d9d888af8832289d3d054573cad3a1d',
 B+'prism_all_columns/artifact_packages.json':'112a6b94b98ef1f29f0b0691d356018f51697fd39f819b66fa52d8c2e934e55c',
 B+'prism_first_choice_normalization/artifact_packages.json':'ce2eb961406cbd780f7ff93d81a1916484fd42f29a0ac43f17065f4988c5a9f9'}
FALSE_BINDINGS={}
def execute(args,out):
    ledger_path=ROOT/args.ledger;ledger_bytes=ledger_path.read_bytes();ledger=yaml.safe_load(ledger_bytes)
    artifacts={a['id']:a for a in ledger['artifacts']}
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z');ids=[];previous=None
    for directory,count in REGISTRATIONS:
        p=ROOT/directory;receipt=json.loads((p/'summary.json').read_bytes());before=(p/'CLAIMS.before.yaml').read_bytes();after=(p/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256'] and hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or before==previous,'registration continuity';previous=after
        assert len(receipt['new_claim_ids'])==count;ids+=receipt['new_claim_ids']
    assert len(ids)==len(set(ids))==6 and len(ledger['claims'])==171,'exactseventeenth cohort'
    dirs=list(DIRS)+list(args.extra_dir);files=list(FILES)+list(args.extra_file)
    assert ledger_bytes==previous,'final registration snapshot'
    claims=[c for c in ledger['claims'] if c['id'] in ids];assert len(claims)==6 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    selected=set(files)
    for name in dirs:
        assert (ROOT/name).is_dir(),name;selected.update(common.relative(p) for p in (ROOT/name).rglob('*') if p.is_file())
    assert not any('binary_mip' in p or 'mip_raw' in p or 'coupled' in p for p in selected),'future18 cohort excluded'
    local=dict(LOCAL_FIXED)
    for manifest,pin in recovery.MANIFESTS.items():
        assert common.digest(ROOT/manifest)==pin
        for item in recovery.items(json.loads((ROOT/manifest).read_bytes())):
            if item['raw_bytes']>10*1024**2:local[item['raw_path']]='Raw retained LOCAL_ONLY; exact public gzip recovery available. Artifact identity only.'
    assert set(local)<=selected
    prior={};prior_recoverable={B+'prism_all_columns/clauses.body'}|{recovery.CHECKER_TARGET+n for n in recovery.CHECKER_FILES}
    for name,pin in PRIOR_PACKAGES.items():
        assert name in tracked and common.digest(ROOT/name)==pin;prior[name]=json.loads((ROOT/name).read_bytes())
        prior_recoverable.update(p['raw_path'] for p in prior[name]['packages'])
    cache={};refs=[];errors=[];recovered=[];corrupt=[]
    def info(path):
        if path not in cache:
            p=ROOT/path;assert p.is_file() and p.resolve().is_relative_to(ROOT),path
            cache[path]=dict(path=path,sha256=common.digest(p),bytes=p.stat().st_size)
        return cache[path]
    def check(name,expected,origin,archive=False):
        if name in artifacts:
            artifact=artifacts[name];assert artifact['sha256']==expected,('ledger artifact binding',name,origin)
            name=artifact['path']
        path=common.resolve_ref(name,ROOT/origin,archive)
        if path is None:errors.append(dict(kind='unresolved',name=name,origin=origin,expected=expected));return
        item=info(path)
        if item['sha256']!=expected:
            binding=FALSE_BINDINGS.get((origin,path))
            if binding:
                assert binding['expected']==expected and binding['actual']==item['sha256'] and common.digest(ROOT/origin)==binding['origin_sha256']
                assert common.digest(ROOT/binding['audit'])==binding['audit_sha256'];corrupt.append(dict(origin=origin,**item,reason=binding['reason']));return
            errors.append(dict(kind='hash_mismatch',origin=origin,**item,expected=expected));return
        if not(path in selected or path in tracked or path.startswith('external_conway99_research/') or path in LOCAL_TOOLS or path in prior_recoverable):errors.append(dict(kind='missing_explicit_dependency',origin=origin,**item))
        refs.append(dict(origin=origin,**item))
    def package(obj,origin):
        if not all(k in obj for k in ['raw_path','raw_sha256','raw_bytes']):return
        if 'ordered_parts' in obj:
            chunks=[]
            for p in obj['ordered_parts']:
                check(p['path'],p['sha256'],origin);b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes'];chunks.append(b)
            compressed=b''.join(chunks);assert hashlib.sha256(compressed).hexdigest()==obj['compressed_stream_sha256']
        elif 'parts' in obj:
            compressed=b''.join((ROOT/p['path']).read_bytes() for p in obj['parts'])
            for p in obj['parts']:check(p['path'],p['sha256'],origin);assert (ROOT/p['path']).stat().st_size==p['bytes']
            assert len(compressed)==obj['compressed_bytes'] and hashlib.sha256(compressed).hexdigest()==obj['compressed_sha256']
        elif 'gzip_path' in obj:
            check(obj['gzip_path'],obj['gzip_sha256'],origin);compressed=(ROOT/obj['gzip_path']).read_bytes();assert len(compressed)==obj['gzip_bytes']
        else:return
        raw=gzip.decompress(compressed);assert len(raw)==obj['raw_bytes'] and hashlib.sha256(raw).hexdigest()==obj['raw_sha256'];check(obj['raw_path'],obj['raw_sha256'],origin)
        recovered.append(dict(origin=origin,path=obj['raw_path'],sha256=obj['raw_sha256'],bytes=len(raw)))
        if obj['raw_path']==B+'prism_all_columns/instance.cnf':
            header,body=raw.split(b'\n',1);assert header==b'p cnf 245880 874800' and (ROOT/(B+'prism_all_columns/clauses.body')).read_bytes()==body
            recovered.append(dict(origin=origin,path=B+'prism_all_columns/clauses.body',sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),reconstruction='Dropauthenticatedheader.'))
    def walk(obj,origin):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in common.MAP_KEYS|{'outputs_sha256','input_sha256'} and isinstance(v,dict):
                    for p,h in v.items():
                        if isinstance(h,str) and common.HEX.fullmatch(h):check(p,h,origin)
                walk(v,origin)
            if isinstance(obj.get('path'),str) and isinstance(obj.get('sha256'),str) and common.HEX.fullmatch(obj['sha256']):check(obj['path'],obj['sha256'],origin,'conway-99-research' in obj.get('repository',''))
            package(obj,origin)
        elif isinstance(obj,list):
            for x in obj:walk(x,origin)
    for name,pin in recovery.CHECKER_FILES.items():
        source=recovery.CHECKER_SOURCE+name;target=recovery.CHECKER_TARGET+name
        assert source in tracked and (ROOT/source).read_bytes()==(ROOT/target).read_bytes()
        check(source,pin,key_self);check(target,pin,key_self)
        recovered.append(dict(origin=key_self,path=target,sha256=pin,bytes=(ROOT/target).stat().st_size,reconstruction='Exact prior public source copy; not executable.'))
    for name,obj in prior.items():
        check(name,PRIOR_PACKAGES[name],key_self)
        for p in obj['packages']:package(p,name)
    for name in sorted(selected):
        info(name)
        if name.endswith('.json'):walk(json.loads((ROOT/name).read_bytes()),name)
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path'] in selected,a['path'];check(a['path'],a['sha256'],args.ledger)
    common.save(out/'reference_diagnostics.json',dict(errors=errors,count=len(errors)));assert not errors,f'{len(errors)} closureerrors; see diagnostics'
    public=sorted(selected-set(local));assert all(info(p)['bytes']<=10*1024**2 for p in public),'oversize publicpayload'
    hashes=common.git('hash-object','--stdin-paths',input=('\n'.join(public)+'\n').encode()).decode().splitlines();assert len(hashes)==len(public);gitrows=[]
    for name,gitsha in zip(public,hashes,strict=True):
        raw=(ROOT/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==gitsha,('Gitbyte transformation',name)
        gitrows.append(dict(path=name,git_blob_sha1=gitsha,sha256=info(name)['sha256']))
    ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=ROOT,input='\n'.join(public)+'\n',text=True,capture_output=True);assert ignored.returncode in(0,1)
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='LOCAL_ONLY' if p in local else 'READY_FOR_PUBLICATION',limitation=local.get(p)) for p in sorted(selected)],
        exact_directories=dirs,exact_files=files,local_tools=[dict(info(p),availability='LOCAL_ONLY',limitation='Savednative tool; buildsourceavailable, exactnewtoolchain bytesnotguaranteed.') for p in sorted(LOCAL_TOOLS)],
        prior_public_package_manifests=PRIOR_PACKAGES,prior_recoverable_dependencies=sorted(prior_recoverable),
        excluded_cohorts=['All direct binary MIP and coupled-count work belongs to future wave18.','Unregistered oldidentityscope/proofcore/preflight work.','PROMPT.md anddirtyhistoricalsubmodule changes.'],
        candidate_only_artifacts=[],mathematical_reverification_performed=False))
    common.save(out/'reference_checks.json',dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',records=refs,gzip_recoveries=recovered,deliberately_corrupted_control_bindings=corrupt))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows,limitation='Readonly hash-object without-w; noindexmutation.'))
    common.save(out/'proposed_raw_ignore_paths.json',dict(paths=sorted(local),reason='Proposalonly, noignorefileedit.'))
    common.save(out/'ignored_payload_paths.json',dict(paths=ignored.stdout.splitlines(),meaning='Onlyselectedignoredpayloads maybeforce-staged.'))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],
        ledger_path=args.ledger,ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),claim_ids=ids,claim_population=171,new_claims=6,
        verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),target_resolution='UNKNOWN',preparation_only=args.prepare))
    payload=sorted(set(public)|{common.relative(p) for p in out.iterdir() if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p) for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,v in cache.items():assert common.digest(ROOT/p)==v['sha256'],('concurrentedit',p)
    assert ledger_path.read_bytes()==ledger_bytes and common.git('ls-files','--stage','-z')==index
    status='SEVENTEENTH_PREPARATION_CLOSURE_PASS' if args.prepare else 'SEVENTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json',dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,selected_files=len(selected),public_research_files=len(public),
        public_research_bytes=sum(info(p)['bytes'] for p in public),local_only_research_artifacts=len(local),new_public_recoverable_raw_files=4,
        incomplete_traces=1,reference_bindings=len(refs),unique_referenced_files=len({r['path'] for r in refs}),gzip_recoveries=len(recovered),
        output_hashes={common.relative(p):common.digest(p) for p in out.iterdir() if p.is_file()}));print(json.dumps(dict(status=status,public_files=len(public),local_only=len(local))))

key_self=common.relative(Path(__file__))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--ledger',default='CLAIMS.yaml');ap.add_argument('--prepare',action='store_true')
    ap.add_argument('--extra-dir',action='append',default=[]);ap.add_argument('--extra-file',action='append',default=[]);ap.add_argument('--revision-registration')
    args=ap.parse_args();out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);source=Path(__file__).read_bytes()
    try:execute(args,out)
    except BaseException as error:
        (out/'failed_source.py').write_bytes(source);common.save(out/'failure.json',dict(error=repr(error),source_sha256=hashlib.sha256(source).hexdigest(),command=[sys.executable,*sys.argv],timestamp=datetime.now(timezone.utc).isoformat(),mathematical_verification=False));raise

if __name__=='__main__':main()
