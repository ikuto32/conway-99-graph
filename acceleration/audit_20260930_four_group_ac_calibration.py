"""Append-only tiny exhaustive CSP calibration of the independent certificate checker."""
import argparse, hashlib, importlib.util, json, platform, subprocess, sys
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHECK=ROOT/'acceleration/audit_20260930_hadamard_four_group_local_screen.py'
GATE=ROOT/'acceleration/results/20260930_independent_review/hadamard_four_group_local_screen/summary.json'
HASH='ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    if sha(GATE)!=HASH:raise ValueError('gate hash')
    gate=json.loads(GATE.read_bytes())
    if sha(CHECK)!=gate['inputs_sha256'][key(CHECK)]:raise ValueError('checker source identity')
    spec=importlib.util.spec_from_file_location('independent_local_screen',CHECK);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cases=[]
    for relation in range(16):
        # Only variables0 and1 are constrained. All other pairs are universal.
        allowed={(a,b) for a,b in product(range(2),repeat=2) if relation>>(2*a+b)&1}
        tables={(i,j):[3,3] for i in range(4) for j in range(4) if i!=j}
        tables[0,1]=[sum(1<<b for b in range(2) if (a,b) in allowed) for a in range(2)]
        tables[1,0]=[sum(1<<a for a in range(2) if (a,b) in allowed) for b in range(2)]
        solutions=[v for v in product(range(2),repeat=4) if (v[0],v[1]) in allowed]
        final=[sum(1<<k for k in range(2) if any(v[i]==k for v in solutions)) for i in range(4)]
        current=[3]*4;steps=[]
        for i,j in [(0,1),(1,0),(2,0),(3,0)]:
            for k in range(2):
                if not final[i]>>k&1:
                    steps.append(dict(left=i,right=j,option_index=k,right_domain_mask=hex(current[j])));current[i]&=~(1<<k)
        saved=dict(removals=steps,final_masks=list(map(hex,final)),final_domain_sizes=[v.bit_count() for v in final],empty=not solutions)
        m.replay_ac(saved,[2]*4,tables)
        cases.append(dict(relation=relation,solutions=len(solutions),certificate=saved))
    m.need(sum(c['solutions']>0 for c in cases)==15 and cases[0]['certificate']['empty'],'all sixteen binary relations')
    croot=ROOT/'acceleration/results/20260930_hadamard_four_group_local_screen'
    excluded=[]
    for i in range(108):
        r=json.loads((croot/f'case_{i:03d}.json').read_bytes())
        if r['gram_caps_ac']['empty']:
            zero=[p['sides'] for p in r['pairs'] if p['gram_compatible']==0]
            m.need(r['groups']==[2,5,6,18] and all(any(v) for v in r['profile']) and zero==[[0,3],[1,2]],'literal narrow empty-relation observation')
            excluded.append(i)
    m.need(len(excluded)==12,'twelve literal exclusions')
    write(out/'cases.json',cases)
    inputs={key(p):sha(p) for p in [Path(__file__),CHECK,GATE,ROOT/'uv.lock',ROOT/'pyproject.toml']}
    result=dict(status='INDEPENDENT_FOUR_GROUP_AC_SUPPLEMENTAL_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256={key(out/'cases.json'):sha(out/'cases.json')},complete_relation_controls=16,jointly_feasible=15,empty=1,research_zero_relation_cases=excluded,shared_components='Imports only the frozen independently authored checker to exercise its actual certificate-validation path; no producer imports.',scope='Additional checker calibration and a literal observation about already authenticated pair tables. The original report and claim bytes remain unchanged.',solver_calls=0,target_resolution=False)
    write(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'))))
if __name__=='__main__':main()
