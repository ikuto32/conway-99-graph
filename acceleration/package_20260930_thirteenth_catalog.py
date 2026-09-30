"""Explicit thirteenth artifact catalog; no ledger/index mutation or proof checking."""
from datetime import datetime, timezone
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
 'srg243_residual_fixture','srg243_fixture_failures','variable_core_residual_screen_calibration',
 'prism_first_choice_normalization','prism_first_choice_native_preflight','prism_first_choice_native_pilot',
 'prism_first_choice_native_failures','variable_core_m1_orbits','variable_core_m1_orbits_native_preflight',
 'variable_core_m1_orbits_native_pilot','thirteenth_preparation_registration','thirteenth_packaging_failures',
]]+[I+p for p in [
 'srg243_residual_fixture','dynamic_residual_screen','prism_first_choice_normalization',
 'prism_first_choice_object_calibration','prism_first_choice_unknown','variable_core_m1_orbits',
 'variable_core_m1_orbits_object_calibration','variable_core_m1_orbits_unknown',
]]
FILES=['acceleration/'+p for p in [
 'theory_20260930_srg243_residual_fixture.py','theory_20260930_srg243_residual_fixture_spec.md',
 'audit_20260930_srg243_residual_fixture.py','theory_20260930_variable_core_residual_screen.py',
 'theory_20260930_variable_core_residual_screen_spec.md','audit_20260930_dynamic_residual_screen.py',
 'theory_20260930_prism_first_choice_normalization.py','theory_20260930_prism_first_choice_normalization_spec.md',
 'audit_20260930_prism_first_choice_normalization.py','audit_20260930_prism_first_choice_object.py',
 'native_20260930_prism_first_choice.py','native_20260930_prism_first_choice_spec.md',
 'audit_20260930_prism_first_choice_unknown.py','theory_20260930_variable_core_m1_orbits.py',
 'theory_20260930_variable_core_m1_orbits_spec.md','audit_20260930_variable_core_m1_orbits.py',
 'audit_20260930_variable_core_m1_orbits_object.py','native_20260930_variable_core_m1_orbits.py',
 'native_20260930_variable_core_m1_orbits_spec.md','audit_20260930_variable_core_m1_orbits_unknown.py',
 'audit_20260930_normalized_unknown_common.py',
 'register_20260930_thirteenth_preparation.py','recover_20260930_thirteenth_inputs.py',
 'package_20260930_thirteenth_catalog.py',
]]+['docs/'+p for p in [
 'AUDIT_20260930_DYNAMIC_RESIDUAL_SCREEN.md','AUDIT_20260930_PRISM_FIRST_CHOICE_NORMALIZATION.md',
 'AUDIT_20260930_VARIABLE_CORE_M1_ORBITS.md','PLAN_20260930_ARBITRARY_CORE_RESIDUAL_OBJECT_AUDIT.md',
 'REPRODUCING_20260930_THIRTEENTH_WAVE.md',
]]
LOCAL={
 B+'prism_first_choice_normalization/instance.cnf':'Oversized raw formula; exact public gzip recovery.',
 B+'prism_first_choice_native_pilot/main/proof.drat':'Incomplete UNKNOWN-run trace; not a proof certificate.',
 B+'variable_core_m1_orbits_native_pilot/main/proof.drat':'Incomplete UNKNOWN-run trace; not a proof certificate.',
}
LOCAL_TOOLS={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
PRIOR_RECOVERABLE={B+'variable_core_factor_cnf/model.json',B+'prism_all_columns/instance.cnf',
                   B+'prism_all_columns/model.json',B+'prism_all_columns/clauses.body'}
IDS={'C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL','C-DYNAMIC-TRIANGLE-RESIDUAL-SCREEN-NECESSITY',
     'C-SIX-PRISM-FIRST-CHOICE-NORMALIZATION-CNF','C-VARIABLE-CORE-M1-ELEVEN-ORBIT-NORMALIZATION'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    out=ROOT/a.out;assert not out.exists()
    selected=set(FILES)
    for directory in DIRS:
        assert (ROOT/directory).is_dir(),directory
        selected.update(common.relative(p) for p in (ROOT/directory).rglob('*') if p.is_file())
    assert set(LOCAL)<=selected
    ledger_bytes=(ROOT/'CLAIMS.yaml').read_bytes();data=yaml.safe_load(ledger_bytes)
    registration=ROOT/(B+'thirteenth_preparation_registration')
    r=json.loads((registration/'summary.json').read_bytes())
    assert hashlib.sha256((registration/'CLAIMS.before.yaml').read_bytes()).hexdigest()==r['previous_ledger_sha256']
    assert (registration/'CLAIMS.after.yaml').read_bytes()==ledger_bytes
    assert hashlib.sha256(ledger_bytes).hexdigest()==r['ledger_sha256'] and set(r['new_claim_ids'])==IDS
    claims=[c for c in data['claims'] if c['id'] in IDS]
    assert len(claims)==4 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index=common.git('ls-files','--stage','-z')
    cache={};refs=[];recoveries=[];corrupt_bindings=[]
    def info(path):
        if path not in cache:
            p=ROOT/path;assert p.is_file() and p.resolve().is_relative_to(ROOT),path
            cache[path]=dict(path=path,sha256=common.digest(p),bytes=p.stat().st_size)
        return cache[path]
    def check(name,sha,origin,archive=False):
        path=common.resolve_ref(name,ROOT/origin,archive);assert path,(origin,name)
        item=info(path)
        deliberate=(I+'dynamic_residual_screen/malformed_cli_controls/wrong_factor_hash/synthetic_gate.json',
                    I+'dynamic_residual_screen/malformed_cli_controls/wrong_factor_hash/synthetic_factor.json')
        if (origin,path)==deliberate:
            assert sha=='0'*64 and item['sha256']=='863005242acc308a079766c957d24d862fa37d288fa7fc23a942446ee476a5ce'
            corrupt_bindings.append(dict(origin=origin,**item,deliberately_false_sha256=sha,meaning='Frozen negative control; rejected by the independent dynamic-screen CLI audit, not an authentic evidence binding.'))
            return
        assert item['sha256']==sha,(origin,path)
        assert path in selected or path in tracked or path.startswith('external_conway99_research/') or path in LOCAL_TOOLS or path in PRIOR_RECOVERABLE,('missing explicit dependency',path)
        refs.append(dict(origin=origin,**item))
    def walk(obj,origin):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in common.MAP_KEYS|{'outputs_sha256'} and isinstance(v,dict):
                    for name,sha in v.items():
                        if isinstance(sha,str) and common.HEX.fullmatch(sha):check(name,sha,origin)
                walk(v,origin)
            if isinstance(obj.get('path'),str) and isinstance(obj.get('sha256'),str) and common.HEX.fullmatch(obj['sha256']):
                check(obj['path'],obj['sha256'],origin,'conway-99-research' in obj.get('repository',''))
            if all(k in obj for k in ('raw_path','raw_sha256','raw_bytes','ordered_parts','compressed_stream_sha256')):
                check(obj['raw_path'],obj['raw_sha256'],origin)
                stream=b''.join((ROOT/p['path']).read_bytes() for p in obj['ordered_parts'])
                assert hashlib.sha256(stream).hexdigest()==obj['compressed_stream_sha256']
                raw=gzip.decompress(stream)
                assert len(raw)==obj['raw_bytes'] and hashlib.sha256(raw).hexdigest()==obj['raw_sha256']
                recoveries.append(dict(origin=origin,path=obj['raw_path'],bytes=len(raw),sha256=obj['raw_sha256']))
        elif isinstance(obj,list):
            for v in obj:walk(v,origin)
    for name,status in [('variable_core_m1_orbits','INDEPENDENT_VARIABLE_CORE_M1_ORBITS_UNKNOWN_RUN_AUDIT_PASS'),
                        ('prism_first_choice','INDEPENDENT_PRISM_FIRST_CHOICE_UNKNOWN_RUN_AUDIT_PASS')]:
        audit=json.loads((ROOT/(I+name+'_unknown/summary.json')).read_bytes())
        assert audit['status']==status,(name,audit['status'])
    for path in sorted(selected):
        info(path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    artifacts={a['id']:a for a in data['artifacts']}
    for claim in claims:
        for aid in claim['evidence']:
            item=artifacts[aid];assert item['path'] in selected;check(item['path'],item['sha256'],'CLAIMS.yaml')
    public=sorted(selected-set(LOCAL));assert all(info(p)['bytes']<=10*1024**2 for p in public)
    ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=ROOT,input='\n'.join(public)+'\n',text=True,capture_output=True)
    assert ignored.returncode in (0,1);ignored_paths=ignored.stdout.splitlines();assert set(ignored_paths)<=set(public)
    out.mkdir(parents=True,exist_ok=False)
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='LOCAL_ONLY' if p in LOCAL else 'READY_FOR_PUBLICATION',limitation=LOCAL.get(p)) for p in sorted(selected)],
        directories=DIRS,files=FILES,local_tools=sorted(LOCAL_TOOLS),prior_public_gzip_recoverable_dependencies=sorted(PRIOR_RECOVERABLE),selection_rule='Exact directory/file allowlists, three explicit new raw exclusions; prior raw dependencies recovered using the twelfth guide.',
        excluded_cohorts=['GPU annealer calibration/pilot','full ordered-pair normalization','identity-scope audit','unused proof-core','earlier size-preflight results/spec'],
        mathematical_reverification_performed=False,local_retrieval='One raw formula is recovered from public gzip. Two incomplete traces are retained at their exact local receipt paths; hashes are not public retrieval.'))
    assert len(corrupt_bindings)==1
    common.save(out/'reference_checks.json',dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS',records=refs,binding_count=len(refs),unique_paths=len({x['path'] for x in refs}),gzip_recoveries=recoveries,deliberately_corrupted_control_bindings=corrupt_bindings))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),
        claim_ids=sorted(IDS),claim_population=len(data['claims']),verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in data['claims']),
        registration_chain_checked=True,target_resolution='UNKNOWN',local_only=[info(p) for p in sorted(LOCAL)]))
    common.save(out/'ignored_payload_paths.json',dict(paths=ignored_paths,raw_log_paths=[p for p in ignored_paths if p.endswith('.log')],meaning='Only these selected paths may be force-staged.'))
    payload=sorted(set(public)|{common.relative(p) for p in out.iterdir() if p.is_file()})
    common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p) for p in payload],wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for p,item in cache.items():assert common.digest(ROOT/p)==item['sha256'],('concurrent edit',p)
    assert (ROOT/'CLAIMS.yaml').read_bytes()==ledger_bytes and common.git('ls-files','--stage','-z')==index
    common.save(out/'summary.json',dict(status='THIRTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=sorted(IDS),
        selected_files=len(selected),public_research_files=len(public),public_payload_files=len(payload),public_research_bytes=sum(info(p)['bytes'] for p in public),
        local_only_research_artifacts=len(LOCAL),local_only_solver_traces=2,public_recoverable_raw_files=1,ignored_payload_paths=len(ignored_paths),
        reference_bindings=len(refs),unique_referenced_files=len({x['path'] for x in refs}),gzip_recoveries=len(recoveries),
        output_hashes={common.relative(p):common.digest(p) for p in sorted(out.iterdir()) if p.is_file()}))
    print(json.dumps(dict(status='THIRTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',public_files=len(public),local_only=len(LOCAL))))


if __name__=='__main__':main()
