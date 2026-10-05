"""One independently gated proof-enabled fixed-scaffold SAT call."""
from datetime import datetime,timezone
from hashlib import sha256
import gzip
import json
import multiprocessing
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from theory_20260930_rook_sat_runner import bounded

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'
OUT=B/'20260930_rook_orbit_solver_pilot'
BASE=B/'20260930_rook_free_internal_sat/instance.cnf'
MODEL=BASE.with_name('model.json')
PART=B/'20260930_rook_cut_orbits01/clauses.cnfpart'
GATE=B/'20260930_independent_review/rook_cut_orbits/summary.json'
CAL=B/'20260930_independent_review/rook_orbit_sat_calibration/summary.json'
ENC=BASE.with_name('independent_cnf_encoding.json')

def digest(p):
    h=sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,v):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def gate(p,h,status):
    assert digest(p)==h and read(p)['status']==status
    for name,expected in read(p).get('inputs_sha256',{}).items():assert digest(ROOT/name)==expected,name

def main():
    import pysat,pysolvers
    assert digest(BASE)=='ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403'
    assert digest(MODEL)=='26908e992235e307cfc6145275deb3d2765a930c7c59a774c9a7bc42f2f0f95e'
    assert digest(ENC)=='a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0'
    gate(GATE,'9abc83c032bc5454c6f05d6cab0146fd39775f9f994d4f4dc3579dfccf6ef6ac','INDEPENDENT_ROOK_GRAM_CUT_ORBITS_PASS')
    gate(CAL,'2bc5c6689640bbc0eee981a080da6b049319f8d08f9158a25067f8276681b61e','INDEPENDENT_ROOK_ORBIT_SAT_CHECKER_CALIBRATION_PASS')
    assert digest(PART)=='5a66925d688b43aafb6737abfe67f088bed9b3ad41e5027bc334bcb4b67e38ca'
    OUT.mkdir(exist_ok=False)
    cnf=OUT/'instance.cnf'
    with BASE.open('rb') as src,cnf.open('xb') as dst:
        assert src.readline()==b'p cnf 30420 3689820\n'
        dst.write(b'p cnf 30420 3690172\n');shutil.copyfileobj(src,dst,1048576)
        dst.write(PART.read_bytes())
    paths=[BASE,MODEL,ENC,PART,GATE,CAL,Path(__file__),Path(__file__).with_name('theory_20260930_rook_orbit_solver_spec.md'),
        ROOT/'acceleration/theory_20260930_rook_sat_runner.py',ROOT/'acceleration/audit_20260930_rook_orbit_sat.py',
        ROOT/'acceleration/environments/rook-sat/uv.lock',ROOT/'acceleration/environments/rook-sat/pyproject.toml',
        B/'20260930_eight_full99_solver_calibration/controls.json',ROOT/'build/rook-drat-checker/build_manifest.json',ROOT/'build/rook-drat-checker/build_receipt.json']
    save(OUT/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'platform':platform.platform(),
        'pysat':pysat.__version__,'native_module':str(pysolvers.__file__),'native_sha256':digest(pysolvers.__file__),
        'inputs_sha256':{key(p):digest(p) for p in paths},'cnf_sha256':digest(cnf),'variables':30420,'clauses':3690172,
        'question':'One exact fixed-star family plus352verified necessary Gram cuts: local SAT or proof-producing UNSAT?',
        'selection':'All352distinct clauses; no symmetry constraint on a graph.','scope':'Frozen780edge central-factor family only.',
        'limits':{'seconds':300,'conflicts':1000000,'calls':1},'with_proof':True,'seed':None,'seed_null_reason':'Default options, no override.',
        'success_criteria':'Separate complete SAT/raw59 check or exact complete UNSAT proof replay; neither resolves unrestricted target.',
        'status':'PREREGISTERED_GATED_INVOCATION','numerical_threshold':None,'numerical_threshold_null_reason':'Exact SAT and proof only.'})
    folder=OUT/'main';folder.mkdir()
    print(json.dumps({'state':'LAUNCHING','seconds':300,'clauses':3690172}),flush=True)
    result=bounded(cnf,folder,1000000,300)
    save(folder/'receipt.json',{'timestamp':datetime.now(timezone.utc).isoformat(),**result,'cnf_sha256':digest(cnf)})
    checks=[]
    if (folder/'model.json').exists():
        cmd=[str(ROOT/'build/research-venv/Scripts/python.exe'),'acceleration/audit_20260930_rook_orbit_sat.py','check',
            '--base-cnf',str(BASE),'--augmented-cnf',str(cnf),'--model',str(MODEL),'--assignment',str(folder/'model.json'),
            '--orbit-audit',str(GATE),'--orbit-audit-sha256',digest(GATE),'--encoding-audit',str(ENC),'--encoding-audit-sha256',digest(ENC),
            '--out',str(OUT/'independent_sat')]
        try:
            call=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=120)
            (OUT/'independent_sat.log').write_bytes(call.stdout+call.stderr)
            checks.append({'command':cmd,'exit_code':call.returncode,'log_sha256':digest(OUT/'independent_sat.log')})
        except subprocess.TimeoutExpired as exc:
            (OUT/'independent_sat_timeout.log').write_bytes((exc.stdout or b'')+(exc.stderr or b''))
            checks.append({'command':cmd,'status':'INDEPENDENT_CHECK_TIMEOUT'})
    packages=[];started=time.monotonic()
    for raw in [cnf,folder/'proof.drat',folder/'model.json']:
        if not raw.exists():continue
        compressed=raw.with_name(raw.name+'.gz')
        with raw.open('rb') as src,compressed.open('xb') as dst:
            with gzip.GzipFile(filename='',fileobj=dst,mode='wb',mtime=0,compresslevel=6) as gz:shutil.copyfileobj(src,gz,1048576)
        parts=[]
        if compressed.stat().st_size>10*1024*1024:
            with compressed.open('rb') as src:
                for i,block in enumerate(iter(lambda:src.read(8*1024*1024),b'')):
                    p=compressed.with_name(compressed.name+f'.part{i:03d}');p.write_bytes(block)
                    parts.append({'path':key(p),'sha256':digest(p),'bytes':p.stat().st_size})
        packages.append({'raw':key(raw),'raw_sha256':digest(raw),'raw_bytes':raw.stat().st_size,'gzip':key(compressed),'gzip_sha256':digest(compressed),'gzip_bytes':compressed.stat().st_size,'parts':parts})
        if time.monotonic()-started>120:break
    save(OUT/'artifact_packages.json',{'packages':packages,'recovery':'Concatenate ordered gzip parts if listed, decompress and verify raw hash.'})
    save(OUT/'summary.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'solver_attempts':1,'actual_result':result,
        'independent_checks':checks,'target_resolution':False,'scope':'Frozen780edge family with352Gramcuts only.',
        'unsat_proof_independent_replay_pending':(folder/'proof.drat').exists(),'worker_observed_stopped':result['worker_observed_stopped']})
    print(json.dumps({'answer':result['solver_answer'],'exit':result['worker_exit_code'],'independent_checks':checks}),flush=True)

if __name__=='__main__':multiprocessing.freeze_support();main()
