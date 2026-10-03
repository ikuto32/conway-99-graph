"""Explicit tenth-wave artifact inventory; no ledger/index/staging mutation."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
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
DIRS=[
 B+'triangle_q1_capacity_cnf', I+'triangle_q1_capacity_cnf',
 I+'triangle_q1_capacity_object_calibration',
 B+'triangle_q1_capacity_native_preflight', B+'triangle_q1_capacity_native_pilot',
 I+'triangle_q1_capacity_sat_object', I+'triangle_q1_capacity_sat_binding',
 B+'capacity_q1_rows', I+'triangle_capacity_q1_rows',
 B+'triangle_residual60', I+'triangle_residual60',
 B+'tenth_preparation_registration', B+'capacity_q1_exclusion_registration',
]
FILES=['acceleration/'+p for p in [
 'theory_20260930_triangle_q1_capacity_cnf.py','theory_20260930_triangle_q1_capacity_cnf_spec.md',
 'audit_20260930_triangle_q1_capacity_cnf.py','audit_20260930_triangle_q1_capacity_object.py',
 'audit_20260930_triangle_q1_capacity_sat_binding.py',
 'native_20260930_triangle_q1_capacity.py','native_20260930_triangle_q1_capacity_spec.md',
 'theory_20260930_capacity_q1_rows.py','theory_20260930_capacity_q1_rows_spec.md',
 'audit_20260930_triangle_capacity_q1_rows.py','bind_20260930_triangle_capacity_q1_rows.py',
 'theory_20260930_triangle_residual60.py','audit_20260930_triangle_residual60.py',
 'register_20260930_tenth_preparation.py','register_20260930_capacity_q1_exclusion.py',
 'package_20260930_tenth_catalog.py',
]]+['docs/'+p for p in [
 'AUDIT_20260930_TRIANGLE_Q1_CAPACITY_ENCODING.md','AUDIT_20260930_TRIANGLE_CAPACITY_Q1_ROWS.md',
 'DERIVATION_20260930_TRIANGLE_RESIDUAL60.md','AUDIT_20260930_TRIANGLE_RESIDUAL60.md',
 'REPRODUCING_20260930_TENTH_WAVE.md',
]]
LOCAL_BINARIES={'build/research-cadical195/source/build/cadical','build/rook-drat-checker/drat-trim.exe'}
EXPECTED_IDS={
 'C-FIXED-TRIANGLE-Q1-CAPACITY-PROJECTION-CNF','C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE',
 'C-FIXED-TRIANGLE-CAPACITY-COMPATIBLE-Q1-CONSTRUCTION','C-FIXED-TRIANGLE-CAPACITY-Q1-ROW-EXCLUSION',
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=ROOT/args.out;assert not out.exists()
    selected=set(FILES)
    for directory in DIRS:
        assert (ROOT/directory).is_dir(),directory
        selected.update(common.relative(p)for p in (ROOT/directory).rglob('*')if p.is_file())
    ledger_bytes=(ROOT/'CLAIMS.yaml').read_bytes();data=yaml.safe_load(ledger_bytes)
    first=json.loads((ROOT/(B+'tenth_preparation_registration/summary.json')).read_bytes())
    last=json.loads((ROOT/(B+'capacity_q1_exclusion_registration/summary.json')).read_bytes())
    assert first['ledger_sha256']==last['previous_ledger_sha256']
    assert hashlib.sha256(ledger_bytes).hexdigest()==last['ledger_sha256']
    assert (ROOT/(B+'tenth_preparation_registration/CLAIMS.after.yaml')).read_bytes()==(ROOT/(B+'capacity_q1_exclusion_registration/CLAIMS.before.yaml')).read_bytes()
    assert (ROOT/(B+'capacity_q1_exclusion_registration/CLAIMS.after.yaml')).read_bytes()==ledger_bytes
    ids=first['new_claim_ids']+last['new_claim_ids'];assert len(ids)==4 and set(ids)==EXPECTED_IDS
    claims=[c for c in data['claims']if c['id']in ids]
    assert len(claims)==4 and all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in claims)
    tracked=set(common.git('ls-files','-z').decode().split('\0'));index_before=common.git('ls-files','--stage','-z');cache={};refs=[]
    def info(path):
        if path not in cache:
            p=ROOT/path;assert p.is_file()and p.resolve().is_relative_to(ROOT),path
            cache[path]=dict(path=path,sha256=common.digest(p),bytes=p.stat().st_size)
        return cache[path]
    def check(name,expected,origin,archive=False):
        path=common.resolve_ref(name,ROOT/origin,archive);assert path,(origin,name)
        item=info(path);assert item['sha256']==expected,(origin,path)
        assert path in selected or path in tracked or path.startswith('external_conway99_research/')or path in LOCAL_BINARIES,('missing explicit dependency',path)
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
        elif isinstance(obj,list):
            for v in obj:walk(v,origin)
    for path in sorted(selected):
        info(path)
        if path.endswith('.json'):walk(json.loads((ROOT/path).read_bytes()),path)
    artifacts={a['id']:a for a in data['artifacts']}
    for claim in claims:
        for aid in claim['evidence']:
            a=artifacts[aid];assert a['path']in selected;check(a['path'],a['sha256'],'CLAIMS.yaml')
    assert all(info(p)['bytes']<=10*1024**2 for p in selected),'unexpected large public artifact'
    ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=ROOT,input='\n'.join(sorted(selected))+'\n',text=True,capture_output=True)
    assert ignored.returncode in (0,1)
    ignored_paths=ignored.stdout.splitlines();assert set(ignored_paths)<=selected
    out.mkdir(parents=True,exist_ok=False)
    common.save(out/'catalog.json',dict(entries=[dict(info(p),availability='READY_FOR_PUBLICATION')for p in sorted(selected)],
        directories=DIRS,files=FILES,local_tool_binaries=sorted(LOCAL_BINARIES),
        selection_rule='Exact frozen directory and source allowlists, not a scan of all untracked work.',
        omitted_next_wave='Live25row work and identity-core/archive/spectral reviews are excluded.',
        trace_scope='The retained1816830byte proof.drat came from aSATrun and is not an UNSAT certificate. The positive evidence is the independent complete assignment/rawfactor check.',
        mathematical_reverification_performed=False))
    common.save(out/'reference_checks.json',dict(status='EXACT_REFERENCED_HASHES_PASS',records=refs,binding_count=len(refs),unique_paths=len({r['path']for r in refs})))
    common.save(out/'scope.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=common.git('rev-parse','HEAD').decode().strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),claim_ids=ids,
        claim_population=len(data['claims']),verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in data['claims']),target_resolution='UNKNOWN',
        registration_chain_checked=True,original_registration_snapshots_retained=True))
    common.save(out/'ignored_payload_paths.json',dict(paths=ignored_paths,raw_log_paths=[p for p in ignored_paths if p.endswith('.log')],
        meaning='Explicit allowlisted paths only; publisher may stage them intentionally. This checker never changes ignore rules or index.'))
    payload=sorted(selected|{common.relative(p)for p in out.iterdir()if p.is_file()})
    common.save(out/'stage_inventory.json',dict(paths=payload,entries=[info(p)for p in payload],
        wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'),common.relative(out/'summary.json')]))
    for path,item in cache.items():assert common.digest(ROOT/path)==item['sha256'],('concurrent edit',path)
    assert (ROOT/'CLAIMS.yaml').read_bytes()==ledger_bytes
    assert common.git('ls-files','--stage','-z')==index_before
    common.save(out/'summary.json',dict(status='TENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_ids=ids,
        selected_files=len(selected),public_payload_files=len(payload),public_research_bytes=sum(info(p)['bytes']for p in selected),
        local_only_research_artifacts=0,ignored_payload_paths=len(ignored_paths),reference_bindings=len(refs),unique_referenced_files=len({r['path']for r in refs}),
        output_hashes={common.relative(p):common.digest(p)for p in sorted(out.iterdir())if p.is_file()}))
    print(json.dumps(dict(status='TENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',selected_files=len(selected),payload_files=len(payload),ignored_paths=len(ignored_paths))))

if __name__=='__main__':main()
