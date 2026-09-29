"""Twelve exact single-row extension tests for an independently checked Q1."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import ResourceCap
from theory_20260930_triangle_q1_binary_scout import row_solve,row_constraints

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'acceleration/results/20260930_triangle_q1_capacity_native_pilot/main/decoded_factor.json'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_object/summary.json'
SCOPE=ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json'
PINS={RAW:'94904b766b487e579f656e685643449c23a6aabf07825cac17e9fd8e241427c5',GATE:'34eec921b8c149c2bd49860e2f0208c4d2fa472e953c55a89dc867a9d8c2605d',SCOPE:'51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);cap=ResourceCap()
    for p,h in PINS.items():assert sha(p)==h
    gate=json.loads(GATE.read_bytes());assert gate['status']=='INDEPENDENT_TRIANGLE_Q1_CAPACITY_SAT_OBJECT_PASS' and gate['inputs_sha256'][key(RAW)]==PINS[RAW]
    paths=[Path(__file__),Path(__file__).with_name('theory_20260930_capacity_q1_rows_spec.md'),*PINS,ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/theory_20260930_triangle_q1_binary_scout.py',ROOT/'acceleration/results/20260930_triangle_q1_binary_scout/supplemental_row_controls.json',ROOT/'acceleration/results/20260930_independent_review/triangle_q1_binary_scout/summary.json',ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'uv_version':subprocess.check_output(['uv','--version'],text=True).strip(),'inputs_sha256':{key(p):sha(p) for p in paths},'limits':{'row_seconds':2,'row_nodes':20000,'rows':12,'total_seconds':120,'memory_bytes':8*1024**3},'status':'CANDIDATE_ROW_EXTENSION_TEST','scope':'New independently approved Q1 only, with original fixed core; no propagated-zero premise.','shared_code':'Previously checked necessary-row formulation and producer bounded recursion; independent new artifact audit required.','random_seed':None,'random_seed_reason':'Deterministic exact branching.'})
    raw=json.loads(RAW.read_bytes());scope=json.loads(SCOPE.read_bytes());c=raw['incidence_matrix'];assert len(c)==24 and all(len(r)==60 for r in c);core=scope['core'];known=[[0]*99 for _ in range(99)]
    def edge(a,b,value=1):known[a][b]=known[b][a]=value
    for a,b in combinations(range(3),2):edge(a,b)
    for g,m in enumerate(core['internal_matchings']):
        for i,j in enumerate(m):edge(g,3+12*g+i);edge(3+12*g+i,3+12*g+j)
    for i,j in enumerate(core['F01']):edge(3+i,15+j)
    for i,j in enumerate(core['F02']):edge(3+i,27+j)
    for i,j in enumerate(core['P12']):edge(15+i,27+j)
    for a in range(24):
        for d in range(60):edge(3+a,39+d,c[a][d])
    for a in range(27,39):
        for b in range(39,99):edge(a,b,-1)
    for a,b in combinations(range(39,99),2):edge(a,b,-1)
    neighbors=[{i for i,x in enumerate(row) if x==1} for row in known]
    failures=[(a,b) for a,b in combinations(range(99),2) if len(neighbors[a]&neighbors[b])+(known[a][b]==1)>2];assert not failures
    save(out/'raw99.json',{'known_adjacency':known,'Q1':raw['Q1'],'factor_input_sha256':PINS[RAW],'known_one_pair_caps_pass':True,'unknown_C2_entries':720,'unknown_BB_entries':1770,'propagated_assignments_used':0})
    outcomes=[]
    for u in range(27,39):
        cap.check();vv,cs=row_constraints(known,u);tree=row_solve(60,cs,cap)
        if tree['status']=='SAT':assert all(cn['lower']<=sum(tree['assignment'][i] for i in cn['variables'])<=cn['upper'] for cn in cs)
        filename='row_%02d.json'%u;save(out/filename,{'vertex':u,'variables':vv,'constraints':cs,'proof':tree})
        outcomes.append({'vertex':u,'status':tree['status'],'nodes':len(tree['nodes']),'artifact':key(out/filename),'sha256':sha(out/filename)})
    summary={'status':'CANDIDATE_TWELVE_ROW_DOMAINS_COMPLETE','independent_verification':'PENDING','attempted_rows':len(outcomes),'sat_rows':sum(x['status']=='SAT' for x in outcomes),'unsat_rows':sum(x['status']=='UNSAT' for x in outcomes),'unknown_rows':sum(x['status']=='UNKNOWN' for x in outcomes),'outcomes':outcomes,'fixed_Q1_candidate_exclusion':any(x['status']=='UNSAT' for x in outcomes),'joint_C2_feasibility':'UNKNOWN','target_resolution':False,'elapsed_seconds':time.monotonic()-cap.start,'peak_working_set_bytes':cap.peak_bytes,'output_hashes':{key(p):sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('output_hashes','outcomes')}))


if __name__=='__main__':main()
