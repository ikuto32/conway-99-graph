"""Frozen, explicit eleventh publication inventory. No index or ledger mutation."""
from datetime import datetime, timezone
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

ROOT=common.ROOT
B='acceleration/results/20260930_'
I=B+'independent_review/'
DIRS=[B+p for p in [
 'triangle_one_c2_row_cnf','triangle_one_c2_row_native_preflight','triangle_one_c2_row_native_pilot',
 'triangle_one_c2_compact','one_c2_extension_rows','prism_factor_design_pilot',
 'prism_unpaired_design_pilot','prism_unpaired_kernel','triangle_factor_column_caps',
 'triangle_column_cap_factor_native_preflight','triangle_column_cap_factor_native_pilot',
 'eleventh_preparation_registration','eleventh_factor_registration','eleventh_packaging_failures',
]]+[I+p for p in [
 'one_c2_synthetic_control','one_c2_raw25_calibration','triangle_one_c2_row_cnf',
 'triangle_one_c2_row_object_calibration','triangle_one_c2_row_sat_object','triangle_one_c2_row_sat_binding',
 'triangle_one_c2_compact','triangle_one_c2_compact_object_calibration','one_c2_extension_rows',
 'prism_complement_design','prism_unpaired_kernel','triangle_factor_column_caps',
 'triangle_column_cap_factor_object_calibration','triangle_column_cap_factor_unknown',
]]
FILES=['acceleration/'+p for p in [
 'theory_20260930_triangle_one_c2_row_cnf.py','theory_20260930_triangle_one_c2_row_cnf_spec.md',
 'audit_20260930_triangle_one_c2_row_cnf.py','audit_20260930_triangle_one_c2_row_object.py',
 'audit_20260930_triangle_one_c2_row_sat_binding.py','native_20260930_triangle_one_c2_row.py',
 'native_20260930_triangle_one_c2_row_spec.md','prepare_20260930_one_c2_synthetic_control.py',
 'audit_20260930_one_c2_raw25.py','theory_20260930_triangle_one_c2_compact.py',
 'theory_20260930_triangle_one_c2_compact_spec.md','audit_20260930_triangle_one_c2_compact.py',
 'audit_20260930_triangle_one_c2_compact_object.py','theory_20260930_one_c2_extension_rows.py',
 'theory_20260930_one_c2_extension_rows_spec.md','audit_20260930_one_c2_extension_rows.py',
 'theory_20260930_prism_factor_design.py','theory_20260930_prism_factor_design_spec.md',
 'audit_20260930_prism_complement_design.py','theory_20260930_prism_unpaired_design.py',
 'theory_20260930_prism_unpaired_design_spec.md','theory_20260930_prism_unpaired_kernel.py',
 'theory_20260930_prism_unpaired_kernel_spec.md','audit_20260930_prism_unpaired_kernel.py',
 'theory_20260930_triangle_factor_column_caps.py','theory_20260930_triangle_factor_column_caps_spec.md',
 'audit_20260930_triangle_factor_column_caps.py','audit_20260930_triangle_column_cap_factor_object.py',
 'native_20260930_triangle_column_cap_factor.py','native_20260930_triangle_column_cap_factor_spec.md',
 'audit_20260930_triangle_column_cap_factor_unknown.py','register_20260930_eleventh_preparation.py',
 'register_20260930_eleventh_factor_results.py','recover_20260930_eleventh_recipe.py',
 'package_20260930_eleventh_catalog.py',
]]+['docs/'+p for p in [
 'AUDIT_20260930_TRIANGLE_ONE_C2_ROW_ENCODING.md','AUDIT_20260930_TRIANGLE_ONE_C2_COMPACT.md',
 'AUDIT_20260930_ONE_C2_EXTENSION_ROWS.md','AUDIT_20260930_PRISM_COMPLEMENT_DESIGN.md',
 'DERIVATION_20260930_PRISM_UNPAIRED_KERNEL.md','AUDIT_20260930_PRISM_UNPAIRED_KERNEL.md',
 'AUDIT_20260930_TRIANGLE_FACTOR_COLUMN_CAPS.md','REPRODUCING_20260930_ELEVENTH_WAVE.md',
]]
LOCAL={
 B+'triangle_one_c2_row_native_pilot/main/proof.drat':'SAT-run trace; positive evidence is the independently checked complete assignment and raw factor. No UNSAT certificate.',
 B+'prism_unpaired_design_pilot/proof.drat':'Incomplete UNKNOWN-run trace; not an UNSAT certificate.',
 B+'triangle_column_cap_factor_native_pilot/main/proof.drat':'Incomplete UNKNOWN-run trace; not an UNSAT certificate.',
 B+'triangle_factor_column_caps/clause_recipe.json':'Oversized raw recipe; exact public gzip package restores it without a new computation.',
}
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical'}|{'build/rook-drat-checker/'+p for p in [
 'drat-trim.exe','build_manifest.json','build_receipt.json','upstream-drat-trim.c','windows-portability.patch',
 'drat-trim.c','build.cmd','build_stdout.log','build_stderr.log',
]}
EXPECTED_IDS={
 'C-FIXED-TRIANGLE-ONE-C2-ROW-TARGET-PROJECTION-CNF','C-FIXED-TRIANGLE-ONE-C2-ROW-PROJECTION-CONSTRUCTION',
 'C-SIX-PRISM-FIVE-MATCHING-COMPLEMENT-DESIGN-EXCLUSION','C-SIX-PRISM-GLOBAL-COMPLEMENT-PAIRING-EXCLUSION',
 'C-FIXED-TRIANGLE-ONE-C2-COMPACT-CNF-EQUIVALENCE','C-FIXED-25-ROW-TRIANGLE-EXTENSION-EXCLUSION',
 'C-SIX-PRISM-FIVE-MATCHING-UNPAIRED-DESIGN-EXCLUSION','C-FIXED-TRIANGLE-FULL-FACTOR-COLUMN-CAP-CNF',
}
FROZEN={
 B+'triangle_column_cap_factor_native_pilot/summary.json':'b50c6c4b3a6c234241c72fee802e3e22a06e736f60f071382931c1a1180086da',
 I+'triangle_column_cap_factor_unknown/summary.json':'ab28ea5661f6289b21e1a82f813ab6889f0a8479338bdf1273e714cb9f547160',
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=ROOT/args.out;assert not out.exists()
    selected=set(FILES)
    for directory in DIRS:
        assert (ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in (ROOT/directory).rglob('*')if p.is_file())
    assert set(LOCAL)<=selected
    ledger_bytes=(ROOT/'CLAIMS.yaml').read_bytes();data=yaml.safe_load(ledger_bytes)
    first=json.loads((ROOT/(B+'eleventh_preparation_registration/summary.json')).read_bytes())
    last=json.loads((ROOT/(B+'eleventh_factor_registration/summary.json')).read_bytes())
    assert first['ledger_sha256']==last['previous_ledger_sha256']
    assert hashlib.sha256(ledger_bytes).hexdigest()==last['ledger_sha256']
    assert (ROOT/(B+'eleventh_preparation_registration/CLAIMS.after.yaml')).read_bytes()==(ROOT/(B+'eleventh_factor_registration/CLAIMS.before.yaml')).read_bytes()
    assert (ROOT/(B+'eleventh_factor_registration/CLAIMS.after.yaml')).read_bytes()==ledger_bytes
    ids=first['new_claim_ids']+last['new_claim_ids'];assert len(ids)==8 and set(ids)==EXPECTED_IDS
    claims=[c for c in data['claims']if c['id']in ids]
    assert len(claims)==8 and all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index_before=common.git('ls-files','--stage','-z');cache={};refs=[];recovered=[]
    def info(path):
        if path not in cache:
            p=ROOT/path;assert p.is_file()and p.resolve().is_relative_to(ROOT),path
            cache[path]=dict(path=path,sha256=common.digest(p),bytes=p.stat().st_size)
        return cache[path]
    def check(name,expected,origin,archive=False):
        path=common.resolve_ref(name,ROOT/origin,archive);assert path,(origin,name)
        item=info(path);assert item['sha256']==expected,(origin,path)
        assert path in selected or path in tracked or path.startswith('external_conway99_research/')or path in LOCAL_TOOLS,('missing explicit dependency',path)
        refs.append(dict(origin=origin,**item))
    def walk(obj,origin):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in common.MAP_KEYS|{'outputs_sha256'}and isinstance(v,dict):
                    for name,expected in v.items():
                        if isinstance(expected,str)and common.HEX.fullmatch(expected):check(name,expected,origin)
                walk(v,origin)
            if isinstance(obj.get('path'),str)and isinstance(obj.get('sha256'),str)and common.HEX.fullmatch(obj['sha256']):
                check(obj['path'],obj['sha256'],origin,'conway-99-research'in obj.get('repository',''))
            if all(k in obj for k in ('raw_path','raw_sha256','raw_bytes','ordered_parts','compressed_stream_sha256')):
                check(obj['raw_path'],obj['raw_sha256'],origin)
                stream=b''.join((ROOT/p['path']).read_bytes()for p in obj['ordered_parts'])
                assert hashlib.sha256(stream).hexdigest()==obj['compressed_stream_sha256']
                raw=gzip.decompress(stream)
                assert len(raw)==obj['raw_bytes'] and hashlib.sha256(raw).hexdigest()==obj['raw_sha256']
                recovered.append(dict(origin=origin,raw_path=obj['raw_path'],bytes=len(raw),sha256=obj['raw_sha256']))
        elif isinstance(obj,list):
            for v in obj:walk(v,origin)
    for path,sha in FROZEN.items():check(path,sha,'fixed-final-receipts')
    for path in sorted(selected):
        info(path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    artifacts={a['id']:a for a in data['artifacts']}
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path']in selected;check(a['path'],a['sha256'],'CLAIMS.yaml')
    public=sorted(selected-set(LOCAL))
    assert all(info(p)['bytes']<=10*1024**2 for p in public),'unexpected large public artifact'
    ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=ROOT,input='\n'.join(public)+'\n',text=True,capture_output=True)
    assert ignored.returncode in (0,1)
    ignored_paths=ignored.stdout.splitlines();assert set(ignored_paths)<=set(public)
    out.mkdir(parents=True,exist_ok=False)
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='LOCAL_ONLY'if p in LOCAL else'READY_FOR_PUBLICATION',limitation=LOCAL.get(p))for p in sorted(selected)],
        directories=DIRS,files=FILES,local_tool_dependencies=sorted(LOCAL_TOOLS),selection_rule='Exact frozen directories and source allowlists; four explicitly named raw files omitted from Git payload.',
        excluded_cohorts=['unrestricted triangle normalization','variable-core preflight','unused proof_core','identity scope audit'],
        local_retrieval='Exact workspace paths; native source/copy receipts retained. Incomplete solver traces are not publicly retrievable from hashes. Raw clause recipe is restored from the public authenticated gzip package.',
        mathematical_reverification_performed=False))
    common.save(out/'reference_checks.json',dict(status='EXACT_REFERENCED_HASHES_AND_GZIP_RECOVERY_PASS',records=refs,binding_count=len(refs),unique_paths=len({r['path']for r in refs}),gzip_recoveries=recovered))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),claim_ids=ids,
        claim_population=len(data['claims']),verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in data['claims']),target_resolution='UNKNOWN',
        registration_chain_checked=True,original_registration_snapshots_retained=True,local_only=[info(p)for p in sorted(LOCAL)]))
    common.save(out/'ignored_payload_paths.json',dict(paths=ignored_paths,raw_log_paths=[p for p in ignored_paths if p.endswith('.log')],
        meaning='Explicit allowlisted paths only; publisher may stage intentionally. No ignore or index changes by this script.'))
    payload=sorted(set(public)|{common.relative(p)for p in out.iterdir()if p.is_file()})
    common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],
        wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for path,item in cache.items():assert common.digest(ROOT/path)==item['sha256'],('concurrent edit',path)
    assert (ROOT/'CLAIMS.yaml').read_bytes()==ledger_bytes
    assert common.git('ls-files','--stage','-z')==index_before
    common.save(out/'summary.json',dict(status='ELEVENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,
        selected_files=len(selected),public_research_files=len(public),public_payload_files=len(payload),public_research_bytes=sum(info(p)['bytes']for p in public),
        local_only_research_artifacts=len(LOCAL),local_only_solver_traces=3,public_gzip_recoverable_raw_files=1,ignored_payload_paths=len(ignored_paths),
        reference_bindings=len(refs),unique_referenced_files=len({r['path']for r in refs}),gzip_package_recoveries=len(recovered),
        output_hashes={common.relative(p):common.digest(p)for p in sorted(out.iterdir())if p.is_file()}))
    print(json.dumps(dict(status='ELEVENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',selected_files=len(selected),payload_files=len(payload),local_only=len(LOCAL))))

if __name__=='__main__':main()
