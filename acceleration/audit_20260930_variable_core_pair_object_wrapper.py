"""Separate review and adversarial calibration of the producer-authored object wrapper."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import file_digest
from pathlib import Path
from types import SimpleNamespace
import argparse
import gzip
import importlib
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
WRAPPER=ROOT/'acceleration/audit_20260930_variable_core_pair_orbits_object.py'
CAL=ROOT/'acceleration/results/20260930_variable_core_pair_orbits_object_calibration/summary.json'
GATE=ROOT/'acceleration/results/20260930_independent_review/variable_core_pair_orbits_v2/summary.json'
D=ROOT/'acceleration/results/20260930_variable_core_pair_orbits'
BASE=ROOT/'acceleration/results/20260930_variable_core_factor_cnf'
PROOF=ROOT/'docs/AUDIT_20260930_VARIABLE_CORE_PAIR_OBJECT_WRAPPER.md'
PINS={WRAPPER:'752ee912fa5d4575b30c4b3ad0b0341a44c9d5eac8345df623a9a65953849b2a',CAL:'2985b04b0c8d48aedcd372eaa977318e26f903e83b03dc88838870482aa61313',GATE:'6a9840be472b5bcd546a270c881c9f86d09a4bf6cc8eccade6b30f045a2bb33a'}

def need(b,s):
    if not b:raise ValueError(s)
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def native(raw,n):
    values=[None]*(n+1);status=0;ended=False
    for line in raw.splitlines():
        if not line or line.startswith(b'c'):continue
        if line==b's SATISFIABLE':status+=1;continue
        need(line.startswith(b'v '),'only SAT native value lines');need(not ended,'no values after zero')
        fields=[int(x) for x in line.split()[1:]]
        for k,x in enumerate(fields):
            if x==0:need(k==len(fields)-1,'zero is final field');ended=True;continue
            need(1<=abs(x)<=n and values[abs(x)] is None,'native ID range and uniqueness');values[abs(x)]=int(x>0)
    need(status==1 and ended and all(x is not None for x in values[1:]),'complete native model')
    return values

def cnf(raw,values,n,count):
    lines=raw.splitlines();need(lines[0]==f'p cnf {n} {count}'.encode(),'CNF header');need(len(lines)==count+1,'clause count')
    literals=0
    for line in lines[1:]:
        fields=[int(x) for x in line.split()];need(fields and fields[-1]==0 and all(1<=abs(x)<=n for x in fields[:-1]),'CNF literal framing')
        need(any(values[abs(x)]==int(x>0) for x in fields[:-1]),'satisfied clause');literals+=len(fields)-1
    return literals

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();inputs={}
    for p,h in PINS.items():need(digest(p)==h,'review input pin');inputs[key(p)]=h
    cal=read(CAL);gate=read(GATE)
    need(cal['status']=='VARIABLE_CORE_PAIR_ORBIT_OBJECT_CHECKER_CALIBRATION_PASS' and gate['status']=='INDEPENDENT_VARIABLE_CORE_PAIR_ORBIT_NORMALIZATION_PASS','prerequisite statuses')
    for owner in [cal,gate]:
        for p,h in owner['inputs_sha256'].items():need(digest(ROOT/p)==h,'all transitive premise inputs');inputs[p]=h
    for p,h in cal['outputs_sha256'].items():need(digest(ROOT/p)==h,'raw calibration output hash');inputs[p]=h
    for p in [Path(__file__),PROOF,ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    n,clauses=114484,561121;folder=CAL.parent
    raw_native=gzip.decompress((folder/'synthetic_native.txt.gz').read_bytes());raw_cnf=gzip.decompress((folder/'synthetic_fullsize.cnf.gz').read_bytes())
    values=native(raw_native,n);literals=cnf(raw_cnf,values,n,clauses)
    extension=read(D/'extension.json');model=read(BASE/'model.json')
    exact_suffix=b''.join((' '.join(map(str,c))+' 0\n').encode() for c in extension['appended_clauses'])
    need(raw_cnf.endswith(exact_suffix),'real selector suffix in synthetic codec')
    rook=read(folder/'rook9_raw_positive.json')['partial_adjacency_full99']
    need(len(rook)==9 and all(len(row)==9 and all(type(x)is int and x in (0,1) for x in row) for row in rook),'strict raw9 graph')
    for i in range(9):
        need(rook[i][i]==0 and sum(rook[i])==4,'rook diagonal/degree')
        for j in range(9):need(rook[i][j]==rook[j][i] and sum(rook[i][k]*rook[k][j] for k in range(9))==2*int(i==j)-rook[i][j]+2,'literal rook SRG identity')
    # Black-box calls to reviewed wrapper supplement the independently parsed artifacts.
    wrapper=importlib.import_module('audit_20260930_variable_core_pair_orbits_object')
    wrapper.bind(SimpleNamespace(encoding_gate=GATE,encoding_gate_sha256=PINS[GATE]))
    positive=0
    for index,rep in enumerate(extension['representative_pairs']):
        vv=bytearray(n+1);vv[extension['selectors'][index]]=1
        raw={field:[[int(rep[field][i]==j) for j in range(12)] for i in range(12)] for field in ['M1','M2']}
        for item in model['matching_variables']:
            a,b=item['endpoints'];vv[item['id']]=raw[f'M{item["fibre"]}'][a][b]
        result=wrapper.selected_pair(vv,extension,model,raw);need(result['pair_representative_index']==index,'positive selected-pair index');positive+=1
    failures=[]
    def reject(label,call):
        try:call()
        except (ValueError,KeyError,IndexError,TypeError):failures.append(label)
        else:raise AssertionError('corruption accepted '+label)
    missing=vv[:];missing[extension['selectors'][-1]]=0;reject('no_selector',lambda:wrapper.selected_pair(missing,extension,model,raw))
    two=vv[:];two[extension['selectors'][0]]=1;reject('two_selectors',lambda:wrapper.selected_pair(two,extension,model,raw))
    for field in ['M1','M2']:
        bad=deepcopy(raw);bad[field][0][1]^=1;reject('raw_'+field+'_mismatch',lambda bad=bad:wrapper.selected_pair(vv,extension,model,bad))
    edge=vv[:];edge[model['matching_variables'][0]['id']]^=1;reject('matching_edge_mismatch',lambda:wrapper.selected_pair(edge,extension,model,raw))
    reject('native_missing_status',lambda:native(raw_native.replace(b's SATISFIABLE\n',b''),n))
    reject('native_duplicate',lambda:native(raw_native.replace(b'v 1 2 ',b'v 1 1 ',1),n))
    reject('CNF_wrong_header',lambda:cnf(raw_cnf.replace(b'114484 561121',b'114484 561122',1),values,n,clauses))
    reject('CNF_false_clause',lambda:cnf(raw_cnf.replace(b'1 0\n',b'-1 0\n',1),values,n,clauses))
    reject('CNF_missing_suffix_clause',lambda:cnf(raw_cnf[:raw_cnf.rfind(b'\n',0,-1)+1],values,n,clauses))
    for label in ['wrong_status','wrong_bound_model']:
        bad=deepcopy(gate)
        if label=='wrong_status':bad['status']='CANDIDATE'
        else:bad['inputs_sha256'][key(BASE/'model.json')]='0'*64
        path=args.out/(label+'.json');save(path,bad)
        reject(label,lambda path=path:wrapper.bind(SimpleNamespace(encoding_gate=path,encoding_gate_sha256=digest(path))))
    reject('wrong_gate_hash',lambda:wrapper.bind(SimpleNamespace(encoding_gate=GATE,encoding_gate_sha256='0'*64)))
    need(digest(WRAPPER)==PINS[WRAPPER],'reviewed source unchanged')
    result=dict(status='INDEPENDENT_VARIABLE_CORE_PAIR_ORBIT_OBJECT_WRAPPER_REVIEW_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,independent_raw_checks=dict(native_variables=n,synthetic_clauses=clauses,synthetic_literals=literals,real_selector_suffix_clauses=42961,rook_integer_identity_entries=81),black_box_wrapper_controls=dict(all_representative_raw_positive_cases=positive,fresh_corruptions_rejected=failures),source_review=str(PROOF.relative_to(ROOT)),shared_code='Wrapper imports frozen independent arbitrary-core base checker and its parsers; direct calls into the reviewed wrapper are disclosed black-box controls. Separate raw native/CNF/rook checks here use new stdlib implementation.',actual_research_SAT_checked=False,actual_research_SAT_reason='No raw research factor available; synthetic fullsize codec plus known small graph are calibration only.',solver_calls=0,target_resolution=False,scope='Reviewed wrapper may check full enlarged SAT objects against the independently gated necessary-factor encoding. Its actual results remain pending separate artifact review; no residual completion claim.',elapsed_seconds=time.monotonic()-started,outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()})
    save(args.out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=digest(args.out/'summary.json'))))

if __name__=='__main__':main()
