"""Explicit sixteenth-wave publication closure; no Git or ledger mutation."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import yaml
import package_20260930_eighth_catalog as common
import recover_20260930_sixteenth_inputs as recovery

ROOT=common.ROOT;B='acceleration/results/20260930_';I=B+'independent_review/'
REGISTRATIONS=[(B+'sixteenth_'+name+'_registration',count) for name,count in [
    ('preparation',5),('cyclic',1),('contraction',2),('hadamard',4),('farkas',3),('prism_lp_order',2)]]
DIRS=[B+p for p in [
    'identity_p_mixed_redundancy','prism_coarse60_bitflip','prism_coarse60_bitflip_native_preflight','prism_coarse60_bitflip_native_pilot',
    'prism_coarse60_arc','prism_coarse60_triangle_cover','coarse60_cyclic_cover','triangle_contraction',
    'hadamard20_support','fixed_support_connected01_cnf','hadamard_support_lp','hadamard_support_lp_dual_repair',
    'hadamard_support_remaining_lp','farkas_compress','hadamard_prism_uniform_lp','sixteenth_raw_packages',
    'sixteenth_compressed_registration_failure','sixteenth_compressed_registration',
]]+[p for p,_ in REGISTRATIONS]+[I+p for p in [
    'identity_p_triangle_partition','prism_coarse60_bitflip','prism_coarse60_bitflip_object_calibration',
    'prism_coarse60_bitflip_outcome_calibration','prism_coarse60_bitflip_native_outcome',
    'prism_coarse60_arc','prism_coarse60_arc_v2','prism_coarse60_triangle_cover','coarse60_cyclic_cover',
    'triangle_contraction','triangle_capacity_floor','hadamard20_support','hadamard20_support_v2',
    'hadamard_support_farkas','hadamard_farkas_compressed','hadamard_six_prism_uniform_lp','hadamard_six_prism_column_order','farkas_revision2_impact',
]]
FILES=['acceleration/'+p for p in [
    'theory_20260930_identity_p_mixed_redundancy.py','theory_20260930_identity_p_mixed_redundancy_spec.md','audit_20260930_identity_p_triangle_partition.py',
    'theory_20260930_prism_coarse60_bitflip.py','theory_20260930_prism_coarse60_bitflip_spec.md','audit_20260930_prism_coarse60_bitflip.py',
    'audit_20260930_prism_coarse60_bitflip_object.py','audit_20260930_prism_coarse60_bitflip_native_outcome.py',
    'native_20260930_prism_coarse60_bitflip.py','native_20260930_prism_coarse60_bitflip_spec.md',
    'theory_20260930_prism_coarse60_arc.py','theory_20260930_prism_coarse60_arc_spec.md','audit_20260930_prism_coarse60_arc.py','audit_20260930_prism_coarse60_arc_v2.py',
    'theory_20260930_prism_coarse60_triangle_cover.py','theory_20260930_prism_coarse60_triangle_cover_spec.md','audit_20260930_prism_coarse60_triangle_cover.py',
    'theory_20260930_coarse60_cyclic_cover.py','theory_20260930_coarse60_cyclic_cover_spec.md','audit_20260930_coarse60_cyclic_cover.py',
    'theory_20260930_triangle_contraction.py','theory_20260930_triangle_contraction_spec.md','audit_20260930_triangle_contraction.py','audit_20260930_triangle_capacity_floor.py',
    'theory_20260930_hadamard20_support.py','theory_20260930_hadamard20_support_spec.md','audit_20260930_hadamard20_support.py','audit_20260930_hadamard20_support_v2.py',
    'theory_20260930_fixed_support_coloring_cnf.py','theory_20260930_fixed_support_coloring_cnf_spec.md',
    'theory_20260930_hadamard_support_lp.py','theory_20260930_hadamard_support_lp_spec.md','theory_20260930_hadamard_lp_dual_repair.py',
    'theory_20260930_hadamard_support_remaining_lp.py','theory_20260930_hadamard_support_remaining_lp_spec.md','audit_20260930_hadamard_support_farkas.py',
    'theory_20260930_farkas_compress.py','theory_20260930_farkas_compress_spec.md','audit_20260930_hadamard_farkas_compressed.py',
    'theory_20260930_hadamard_prism_uniform_lp.py','audit_20260930_hadamard_prism_relaxation_and_order.py',
    'register_20260930_sixteenth_preparation.py','register_20260930_sixteenth_cyclic.py','register_20260930_sixteenth_contraction.py',
    'register_20260930_sixteenth_hadamard.py','register_20260930_sixteenth_farkas.py','register_20260930_sixteenth_prism_lp_order.py',
    'register_20260930_sixteenth_compressed_evidence.py','register_20260930_sixteenth_compressed_evidence_v2.py','audit_20260930_farkas_revision2_impact.py',
    'package_20260930_sixteenth_inputs.py','recover_20260930_sixteenth_inputs.py','package_20260930_sixteenth_catalog.py',
]]+['docs/'+p for p in [
    'DERIVATION_20260930_IDENTITY_P_MIXED_REDUNDANCY.md','AUDIT_20260930_IDENTITY_P_TRIANGLE_PARTITION.md',
    'DERIVATION_20260930_PRISM_COARSE60_BITFLIP.md','AUDIT_20260930_PRISM_COARSE60_BITFLIP.md','AUDIT_20260930_PRISM_COARSE60_BITFLIP_OBJECT.md',
    'AUDIT_20260930_PRISM_COARSE60_ARC.md','AUDIT_20260930_PRISM_COARSE60_ARC_V2.md',
    'DERIVATION_20260930_COARSE60_TRIANGLE_COVER.md','AUDIT_20260930_PRISM_COARSE60_TRIANGLE_COVER.md','AUDIT_20260930_COARSE60_CYCLIC_COVER.md',
    'DERIVATION_20260930_TRIANGLE_CONTRACTION.md','AUDIT_20260930_TRIANGLE_CONTRACTION.md',
    'DERIVATION_20260930_HADAMARD20_SUPPORT.md','AUDIT_20260930_HADAMARD20_SUPPORT.md','AUDIT_20260930_HADAMARD20_SUPPORT_V2.md',
    'AUDIT_20260930_HADAMARD_SUPPORT_FARKAS.md','AUDIT_20260930_HADAMARD_PRISM_RELAXATION_AND_ORDER.md',
    'REPRODUCING_20260930_SIXTEENTH_WAVE.md',
]]
LOCAL_FIXED={B+'prism_coarse60_bitflip_native_pilot/main/proof.drat':'IncompleteUNKNOWN trace, LOCAL_ONLY, no public recovery and not an UNSAT certificate.'}
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe','acceleration/build/factor_permutation_anneal_20260930_v2.exe'}
PRIOR_PACKAGES={
    B+'variable_core_factor_cnf/artifact_packages.json':'46867dcccbb99bd72379b50a7415e6dd1d9d888af8832289d3d054573cad3a1d',
    B+'prism_all_columns/artifact_packages.json':'112a6b94b98ef1f29f0b0691d356018f51697fd39f819b66fa52d8c2e934e55c',
    B+'prism_first_choice_normalization/artifact_packages.json':'ce2eb961406cbd780f7ff93d81a1916484fd42f29a0ac43f17065f4988c5a9f9',
}
FALSE_BINDINGS={}

def execute(args,out):
    ledger_path=ROOT/args.ledger;ledger_bytes=ledger_path.read_bytes();ledger=yaml.safe_load(ledger_bytes)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z');ids=[];previous=None
    for directory,count in REGISTRATIONS:
        p=ROOT/directory;receipt=json.loads((p/'summary.json').read_bytes());before=(p/'CLAIMS.before.yaml').read_bytes();after=(p/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256'] and hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        assert previous is None or before==previous,'registration continuity';previous=after
        assert len(receipt['new_claim_ids'])==count;ids+=receipt['new_claim_ids']
    assert len(ids)==len(set(ids))==17 and len(ledger['claims'])==165,'exactsixteenth cohort'
    dirs=list(DIRS)+list(args.extra_dir);files=list(FILES)+list(args.extra_file)
    if not args.prepare:
        assert args.revision_registration and args.revision_registration in dirs,'explicitfinal r2registrar required'
        p=ROOT/args.revision_registration;receipt=json.loads((p/'summary.json').read_bytes())
        before=(p/'CLAIMS.before.yaml').read_bytes();after=(p/'CLAIMS.after.yaml').read_bytes()
        assert before==previous and after==ledger_bytes,'r2 finalledger continuity'
        assert hashlib.sha256(before).hexdigest()==receipt['previous_ledger_sha256'] and hashlib.sha256(after).hexdigest()==receipt['ledger_sha256']
        revised=next(c for c in ledger['claims'] if c['id']=='C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION');assert revised['revision']==2
    else:assert ledger_bytes==previous or next(c for c in ledger['claims'] if c['id']=='C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION')['revision']==2
    claims=[c for c in ledger['claims'] if c['id'] in ids];assert len(claims)==17 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    selected=set(files)
    for name in dirs:
        assert (ROOT/name).is_dir(),name;selected.update(common.relative(p) for p in (ROOT/name).rglob('*') if p.is_file())
    assert not any('hadamard_six_prism_cyclic' in p or 'hadamard_cyclic_factor' in p or 'native_20260930_hadamard_cyclic' in p for p in selected),'future17cohort excluded'
    local=dict(LOCAL_FIXED)
    for manifest,pin in recovery.MANIFESTS.items():
        assert common.digest(ROOT/manifest)==pin
        for item in json.loads((ROOT/manifest).read_bytes())['packages']:local[item['raw_path']]='Raw retainedLOCAL_ONLY; exact publicgzip recovery available. Artifactidentity only.'
    assert set(local)<=selected
    prior={};prior_recoverable={B+'prism_all_columns/clauses.body'}
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
    for name,obj in prior.items():
        check(name,PRIOR_PACKAGES[name],key_self)
        for p in obj['packages']:package(p,name)
    for name in sorted(selected):
        info(name)
        if name.endswith('.json'):walk(json.loads((ROOT/name).read_bytes()),name)
    artifacts={a['id']:a for a in ledger['artifacts']}
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
        excluded_cohorts=['Allcyclicfactor construction/encoding/native future17work.','Unregistered oldidentityscope/proofcore/preflight work.','PROMPT.md anddirtyhistoricalsubmodule changes.'],
        candidate_only_artifacts=[B+'fixed_support_connected01_cnf'],mathematical_reverification_performed=False))
    common.save(out/'reference_checks.json',dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',records=refs,gzip_recoveries=recovered,deliberately_corrupted_control_bindings=corrupt))
    common.save(out/'git_byte_checks.json',dict(status='CURRENT_GIT_FILTER_BYTES_PASS',records=gitrows,limitation='Readonly hash-object without-w; noindexmutation.'))
    common.save(out/'proposed_raw_ignore_paths.json',dict(paths=sorted(local),reason='Proposalonly, noignorefileedit.'))
    common.save(out/'ignored_payload_paths.json',dict(paths=ignored.stdout.splitlines(),meaning='Onlyselectedignoredpayloads maybeforce-staged.'))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],
        ledger_path=args.ledger,ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),claim_ids=ids,claim_population=165,new_claims=17,
        verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),target_resolution='UNKNOWN',preparation_only=args.prepare))
    payload=sorted(set(public)|{common.relative(p) for p in out.iterdir() if p.is_file()})
    if not args.prepare:common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p) for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,v in cache.items():assert common.digest(ROOT/p)==v['sha256'],('concurrentedit',p)
    assert ledger_path.read_bytes()==ledger_bytes and common.git('ls-files','--stage','-z')==index
    status='SIXTEENTH_PREPARATION_CLOSURE_PASS' if args.prepare else 'SIXTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
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
