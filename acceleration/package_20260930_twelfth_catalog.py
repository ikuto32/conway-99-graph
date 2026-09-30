"""Explicit twelfth cohort catalog; frozen receipt hashes required, no ledger/index edits."""
from datetime import datetime,timezone
import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import yaml
import package_20260930_eighth_catalog as common

ROOT=common.ROOT
B='acceleration/results/20260930_'
I=B+'independent_review/'
DIRS=[B+p for p in [
 'unrestricted_triangle_factor','variable_core_factor_cnf','variable_core_factor_native_preflight',
 'variable_core_factor_native_pilot','prism_all_columns','prism_all_columns_native_preflight',
 'prism_all_columns_native_pilot','prism_column_modular','twelfth_preparation_registration',
 'prism_all_columns_registration','prism_linear_witness_registration',
]]+[I+p for p in [
 'unrestricted_triangle_factor','variable_core_factor_cnf','variable_core_factor_cnf_v2',
 'variable_core_factor_corruption_addendum','variable_core_factor_object_calibration','variable_core_factor_unknown',
 'prism_all_columns_cnf','prism_all_columns_object_calibration','prism_column_modular',
 'prism_all_columns_unknown',
]]
FILES=['acceleration/'+p for p in [
 'theory_20260930_unrestricted_triangle_factor.py','theory_20260930_unrestricted_triangle_factor_spec.md',
 'audit_20260930_unrestricted_triangle_factor.py','theory_20260930_variable_core_factor_cnf.py',
 'theory_20260930_variable_core_factor_cnf_spec.md','theory_20260930_variable_core_factor_preflight.py',
 'audit_20260930_variable_core_factor_cnf.py','audit_20260930_variable_core_factor_cnf_v2.py',
 'audit_20260930_variable_core_factor_corruption_addendum.py','audit_20260930_variable_core_factor_object.py',
 'native_20260930_variable_core_factor.py','native_20260930_variable_core_factor_spec.md',
 'audit_20260930_variable_core_factor_unknown.py','theory_20260930_prism_all_columns.py',
 'theory_20260930_prism_all_columns_spec.md','audit_20260930_prism_all_columns.py',
 'audit_20260930_prism_all_columns_object.py','native_20260930_prism_all_columns.py',
 'native_20260930_prism_all_columns_spec.md','audit_20260930_prism_all_columns_unknown.py',
 'theory_20260930_prism_column_modular.py','audit_20260930_prism_column_modular.py',
 'register_20260930_twelfth_preparation.py','register_20260930_prism_all_columns.py',
 'register_20260930_prism_linear_witnesses.py','recover_20260930_twelfth_inputs.py',
 'package_20260930_twelfth_catalog.py',
]]+['docs/'+p for p in [
 'DERIVATION_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md','AUDIT_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md',
 'AUDIT_20260930_VARIABLE_CORE_FACTOR_CNF.md','AUDIT_20260930_PRISM_ALL_COLUMNS.md',
 'REPRODUCING_20260930_TWELFTH_WAVE.md',
]]
LOCAL={
 B+'variable_core_factor_cnf/model.json':'Oversized raw model, exactly recoverable from public gzip.',
 B+'variable_core_factor_native_pilot/main/proof.drat':'Incomplete UNKNOWN-run trace; no proof certificate.',
 B+'prism_all_columns/instance.cnf':'Oversized raw formula, exactly recoverable from public gzip.',
 B+'prism_all_columns/model.json':'Oversized raw model, exactly recoverable from public gzip.',
 B+'prism_all_columns/clauses.body':'Duplicate oversized raw clause body; exact recovered CNF bytes after its header.',
 B+'prism_all_columns_native_pilot/main/proof.drat':'Incomplete UNKNOWN-run trace; no proof certificate.',
}
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
EXPECTED_IDS={
 'C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION','C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING',
 'C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF','C-SIX-PRISM-COLUMN-LINEAR-RELAXATION-WITNESSES',
}
REGISTRATIONS=['twelfth_preparation_registration','prism_all_columns_registration','prism_linear_witness_registration']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True)
    ap.add_argument('--pilot-summary-sha256',required=True);ap.add_argument('--pilot-audit-sha256',required=True);args=ap.parse_args()
    out=ROOT/args.out;assert not out.exists()
    selected=set(FILES)
    for directory in DIRS:
        assert(ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in(ROOT/directory).rglob('*')if p.is_file())
    assert set(LOCAL)<=selected
    ledger_bytes=(ROOT/'CLAIMS.yaml').read_bytes();data=yaml.safe_load(ledger_bytes);ids=[];previous=None
    for name in REGISTRATIONS:
        d=ROOT/(B+name);r=json.loads((d/'summary.json').read_bytes());before=(d/'CLAIMS.before.yaml').read_bytes();after=(d/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==r['previous_ledger_sha256']and hashlib.sha256(after).hexdigest()==r['ledger_sha256']
        if previous is not None:assert previous==before
        previous=after;ids+=r['new_claim_ids']
    assert previous==ledger_bytes and len(ids)==4 and set(ids)==EXPECTED_IDS
    claims=[c for c in data['claims']if c['id']in ids]
    assert len(claims)==4 and all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index_before=common.git('ls-files','--stage','-z');cache={};refs=[];recoveries=[]
    def info(path):
        if path not in cache:
            p=ROOT/path;assert p.is_file()and p.resolve().is_relative_to(ROOT),path
            cache[path]=dict(path=path,sha256=common.digest(p),bytes=p.stat().st_size)
        return cache[path]
    def check(name,sha,origin,archive=False):
        path=common.resolve_ref(name,ROOT/origin,archive);assert path,(origin,name)
        item=info(path);assert item['sha256']==sha,(origin,path)
        assert path in selected or path in tracked or path.startswith('external_conway99_research/')or path in LOCAL_TOOLS,('missing explicit dependency',path)
        refs.append(dict(origin=origin,**item))
    def walk(obj,origin):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in common.MAP_KEYS|{'outputs_sha256'}and isinstance(v,dict):
                    for name,sha in v.items():
                        if isinstance(sha,str)and common.HEX.fullmatch(sha):check(name,sha,origin)
                walk(v,origin)
            if isinstance(obj.get('path'),str)and isinstance(obj.get('sha256'),str)and common.HEX.fullmatch(obj['sha256']):check(obj['path'],obj['sha256'],origin,'conway-99-research'in obj.get('repository',''))
            if all(k in obj for k in('raw_path','raw_sha256','raw_bytes','ordered_parts','compressed_stream_sha256')):
                check(obj['raw_path'],obj['raw_sha256'],origin);stream=b''.join((ROOT/p['path']).read_bytes()for p in obj['ordered_parts'])
                assert hashlib.sha256(stream).hexdigest()==obj['compressed_stream_sha256'];raw=gzip.decompress(stream)
                assert len(raw)==obj['raw_bytes']and hashlib.sha256(raw).hexdigest()==obj['raw_sha256']
                recoveries.append(dict(origin=origin,path=obj['raw_path'],bytes=len(raw),sha256=obj['raw_sha256']))
        elif isinstance(obj,list):
            for v in obj:walk(v,origin)
    check(B+'prism_all_columns_native_pilot/summary.json',args.pilot_summary_sha256,'final-receipt')
    check(I+'prism_all_columns_unknown/summary.json',args.pilot_audit_sha256,'final-audit')
    audit=json.loads((ROOT/(I+'prism_all_columns_unknown/summary.json')).read_bytes())
    assert audit['status']=='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_UNKNOWN_RUN_AUDIT_PASS'
    for path in sorted(selected):
        info(path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    cnf=(ROOT/(B+'prism_all_columns/instance.cnf')).read_bytes();header,body=cnf.split(b'\n',1)
    assert header==b'p cnf 245880 874800'and(ROOT/(B+'prism_all_columns/clauses.body')).read_bytes()==body
    artifacts={a['id']:a for a in data['artifacts']}
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path']in selected;check(a['path'],a['sha256'],'CLAIMS.yaml')
    public=sorted(selected-set(LOCAL));assert all(info(p)['bytes']<=10*1024**2 for p in public),'unexpected large public artifact'
    ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=ROOT,input='\n'.join(public)+'\n',text=True,capture_output=True);assert ignored.returncode in(0,1)
    ignored_paths=ignored.stdout.splitlines();assert set(ignored_paths)<=set(public)
    out.mkdir(parents=True,exist_ok=False)
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='LOCAL_ONLY'if p in LOCAL else'READY_FOR_PUBLICATION',limitation=LOCAL.get(p))for p in sorted(selected)],directories=DIRS,files=FILES,local_tools=sorted(LOCAL_TOOLS),selection_rule='Exact frozen directory/file allowlists, six explicit raw exclusions.',
      excluded_cohorts=['first-choice normalization','SRG243 fixture','residual dynamic wrapper','identity scope','unused proof_core','variable-core size-preflight results/spec'],
      included_dependency_exception='theory_20260930_variable_core_factor_preflight.py is required as the actual producer calibrate import; its size-preflight result cohort is excluded.',
      mathematical_reverification_performed=False,local_retrieval='Workspace trace paths are retained and named in native receipts; hashes are not public retrieval. Three original raw inputs and one duplicate body are exactly recoverable from supplied gzip and header removal.'))
    common.save(out/'reference_checks.json',dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',records=refs,binding_count=len(refs),unique_paths=len({r['path']for r in refs}),gzip_recoveries=recoveries,duplicate_clause_body_recovery=True))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),claim_ids=ids,claim_population=len(data['claims']),verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in data['claims']),registration_chain_checked=True,target_resolution='UNKNOWN',local_only=[info(p)for p in sorted(LOCAL)]))
    common.save(out/'ignored_payload_paths.json',dict(paths=ignored_paths,raw_log_paths=[p for p in ignored_paths if p.endswith('.log')],meaning='Exact selected paths only. No ignore/index edits performed.'))
    payload=sorted(set(public)|{common.relative(p)for p in out.iterdir()if p.is_file()})
    common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,item in cache.items():assert common.digest(ROOT/p)==item['sha256'],('concurrent edit',p)
    assert(ROOT/'CLAIMS.yaml').read_bytes()==ledger_bytes and common.git('ls-files','--stage','-z')==index_before
    common.save(out/'summary.json',dict(status='TWELFTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,selected_files=len(selected),public_research_files=len(public),public_payload_files=len(payload),public_research_bytes=sum(info(p)['bytes']for p in public),local_only_research_artifacts=len(LOCAL),local_only_solver_traces=2,public_recoverable_raw_files=4,ignored_payload_paths=len(ignored_paths),reference_bindings=len(refs),unique_referenced_files=len({r['path']for r in refs}),gzip_recoveries=len(recoveries),output_hashes={common.relative(p):common.digest(p)for p in sorted(out.iterdir())if p.is_file()}))
    print(json.dumps(dict(status='TWELFTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',public_files=len(public),local_only=len(LOCAL))))
if __name__=='__main__':main()
