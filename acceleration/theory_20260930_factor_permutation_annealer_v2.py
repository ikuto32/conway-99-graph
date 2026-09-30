"""Bounded permutation annealer orchestration; producer outputs remain candidates."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import file_digest
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import random
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'acceleration/factor_permutation_anneal_20260930_v2.cu'
BUILDER=ROOT/'acceleration/build_factor_permutation_anneal_20260930_v2.ps1'
EXE=ROOT/'acceleration/build/factor_permutation_anneal_20260930_v2.exe'
SPEC=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v2_spec.md'
VERSION='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'
SHIFT=ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json'
SHIFT_GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_factor_column_caps/summary.json'
PRISM=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/derived_geometry.json'
PRISM_GATE=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
FIXTURE=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
FIXTURE_GATE=ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json'
PINS={SHIFT:'51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0',
      SHIFT_GATE:'675dae8635175088bff026c59e171c1d2b2b66a4a880cd6a10500ae66bb74331',
      PRISM_GATE:'07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3',
      FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
      FIXTURE_GATE:'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}

def need(b,s):
    if not b: raise ValueError(s)
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def pins(paths):return {key(p):digest(p) for p in paths}
def timestamp():return datetime.now(timezone.utc).isoformat()

def core_data(label):
    if label=='shift6':
        x=read(SHIFT)['core'];n=12;c=[[0]*36 for _ in range(36)]
        for g in range(3):
            for i,j in enumerate(x['internal_matchings'][g]):c[g*n+i][g*n+j]=1
        for g,h,name in [(0,1,'F01'),(0,2,'F02'),(1,2,'P12')]:
            for i,j in enumerate(x[name]):c[g*n+i][h*n+j]=c[h*n+j][g*n+i]=1
        return c,None
    if label=='six_prism':return read(PRISM)['core_adjacency'],None
    x=read(FIXTURE);return x['cubic_core60'],x['factor60x180']

def problem(c):
    n=len(c)//3;m=n*(n-2)//2
    need(n in (12,20) and len(c)==3*n,'supported dimensions')
    need(all(len(row)==3*n and all(type(x)is int and x in (0,1) for x in row) for row in c),'literal binary core')
    need(all(c[i][i]==0 and c[i][j]==c[j][i] for i in range(3*n) for j in range(3*n)),'simple symmetric core')
    need(all(sum(c[g*n+i][h*n:(h+1)*n])==1 for g in range(3) for h in range(3) for i in range(n)),'block matchings')
    need(all(c[i][j]==int(j==(i^1)) for i in range(n) for j in range(n)),'M0 standard')
    need(all(c[i][g*n+j]==int(i==j) for g in (1,2) for i in range(n) for j in range(n)),'two identity cross maps')
    neighbours=[set(j for j,x in enumerate(row) if x) for row in c]
    target=[[n*int(i==j)+2-c[i][j]-len(neighbours[i]&neighbours[j])-int(i//n==j//n) for j in range(3*n)] for i in range(3*n)]
    need(all(2-c[i][j]-len(neighbours[i]&neighbours[j])-int(i//n==j//n)>=0 for i,j in combinations(range(3*n),2)),'positive-core pair caps')
    edges=[[pair for pair in combinations(range(n),2) if not c[g*n+pair[0]][g*n+pair[1]]] for g in range(3)]
    need(all(len(e)==m for e in edges),'edge catalogs')
    return dict(n=n,m=m,core_adjacency=c,target=target,edges=edges)

def factor(p,perms):
    f=[[0]*p['m'] for _ in range(3*p['n'])]
    for g,q in enumerate([list(range(p['m'])),*perms]):
        need(sorted(q)==list(range(p['m'])),'permutation domain')
        for d,k in enumerate(q):
            for i in p['edges'][g][k]:f[g*p['n']+i][d]=1
    return f

def full_score(p,perms):
    f=factor(p,perms);rows=[set(d for d,x in enumerate(row) if x) for row in f];n=p['n']
    return sum((len(rows[g*n+i]&rows[h*n+j])-p['target'][g*n+i][h*n+j])**2 for g,h in combinations(range(3),2) for i in range(n) for j in range(n))

def states(p,seed,chains,positive=None):
    rand=random.Random(seed);result=[]
    for k in range(chains):
        if positive is None:
            perms=[list(range(p['m'])) for _ in range(2)]
            for q in perms:rand.shuffle(q)
        else:
            perms=[]
            for g in (1,2):
                lookup={tuple(pair):i for i,pair in enumerate(p['edges'][g])}
                perms.append([lookup[tuple(i for i in range(p['n']) if positive[g*p['n']+i][d])] for d in range(p['m'])])
        result.append(dict(rng=str(rand.randrange(1,2**64)),proposals=0,permutations=perms,best_permutations=deepcopy(perms)))
    return result

def input_text(p,ss,steps,mode,temp):
    lines=[f'FACTOR_PERMUTATION_V1 {p["n"]} {len(ss)} {steps} {mode} {temp:.17g}']
    lines += [' '.join(map(str,row)) for row in p['target']]
    lines += [' '.join(map(str,pair)) for block in p['edges'] for pair in block]
    for s in ss:
        lines.append(f'{s["rng"]} {s["proposals"]}')
        lines += [' '.join(map(str,q)) for q in s['permutations']+s['best_permutations']]
    return '\n'.join(lines)+'\n'

def invoke(inp,out,backend,timeout=60,expect_ok=True):
    command=[str(EXE),backend,str(inp),str(out)];start=time.monotonic()
    r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
    receipt=dict(command=command,cwd=str(ROOT),returncode=r.returncode,wall_seconds=time.monotonic()-start,stdout=r.stdout,stderr=r.stderr,input_sha256=digest(inp),output_sha256=digest(out) if out.exists() else None)
    save(out.with_suffix('.receipt.json'),receipt)
    need((r.returncode==0)==expect_ok,'native outcome expectation')
    return read(out) if expect_ok else receipt

def check_trace(p,initial,result):
    count=0
    for old,new in zip(initial,result['chains'],strict=True):
        perms=deepcopy(old['permutations']);score=full_score(p,perms);best=full_score(p,old['best_permutations'])
        for g,a,b,delta,accepted,claimed,claimed_best in new['trace']:
            trial=deepcopy(perms);trial[g-1][a],trial[g-1][b]=trial[g-1][b],trial[g-1][a]
            changed=full_score(p,trial);need(changed-score==delta,'literal full recomputation delta')
            if accepted:perms=trial;score=changed;best=min(best,score)
            need(score==claimed and best==claimed_best,'trace objective state');count+=1
        need(perms==new['permutations'] and score==new['score'],'final permutation/score')
        need(best==new['best_score']==full_score(p,new['best_permutations']),'best recomputation')
    return count

def raw_object(p,perms,score):return dict(core_adjacency=p['core_adjacency'],factor=factor(p,perms),claimed_score=score,objective_version=VERSION,status='CANDIDATE',target_graph=False)
def raw_best(p,s):return raw_object(p,s['best_permutations'],s['best_score'])

def rng_next(x):
    mask=(1<<64)-1;x^=x>>12;x^=(x<<25)&mask;x^=x>>27
    return x,(x*2685821657736338717)&mask

def boundary_seed(m,a,b):
    for seed in range(1,1000000):
        x,_=rng_next(seed);x,aa=rng_next(x);x,bb=rng_next(x)
        aa%=m;bb%=m-1;bb+=int(bb>=aa)
        if (aa,bb)==(a,b):return seed
    raise AssertionError('boundary control seed search cap')

def calibration(out):
    command=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(BUILDER)]
    start=time.monotonic();r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=120)
    save(out/'build_receipt.json',dict(command=command,cwd=str(ROOT),returncode=r.returncode,wall_seconds=time.monotonic()-start,stdout=r.stdout,stderr=r.stderr,nvcc_version=subprocess.check_output(['nvcc','--version'],text=True),binary_sha256=digest(EXE) if EXE.exists() else None))
    need(r.returncode==0,'build')
    hardware=subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.free','--format=csv'],text=True)
    records=[];raw_outputs=[];moves=0
    for label in tqdm(['shift6','six_prism','fixture243'],desc='Calibrating cores'):
        c,positive=core_data(label);p=problem(c);ss=states(p,20260930,1 if positive else 2,positive)
        save(out/f'{label}_problem.json',p);save(out/f'{label}_initial.json',ss)
        for k,s in enumerate(ss):save(out/f'{label}_initial_chain{k}_raw.json',raw_object(p,s['permutations'],full_score(p,s['permutations'])))
        if positive is not None:need(full_score(p,ss[0]['permutations'])==0,'known valid positive Gram')
        for mode,temp,name in [(0,0.0,'forced'),(1,0.0,'greedy'),(1,3.25,'anneal')]:
            inp=out/f'{label}_{name}.txt';inp.write_text(input_text(p,ss,64,mode,temp),encoding='utf-8',newline='\n')
            cpu=invoke(inp,out/f'{label}_{name}_cpu.json','cpu');gpu=invoke(inp,out/f'{label}_{name}_gpu.json','gpu')
            need(cpu['chains']==gpu['chains'],'CPU full recomputation vs GPU delta parity (floating acceptance sampled only)')
            moves+=check_trace(p,ss,gpu)
            for k,s in enumerate(gpu['chains']):
                path=out/f'{label}_{name}_chain{k}_raw_best.json';save(path,raw_best(p,s));raw_outputs.append(key(path))
                save(out/f'{label}_{name}_chain{k}_raw_final.json',raw_object(p,s['permutations'],s['score']))
            records.append(dict(core=label,mode=name,chains=len(ss),proposals_per_chain=64,initial_scores=[full_score(p,s['permutations']) for s in ss],best_scores=[s['best_score'] for s in gpu['chains']],kernel_ms=gpu['kernel_ms'],native_result=key(out/f'{label}_{name}_gpu.json')))
        # Chunk split proves persisted permutation/RNG/proposal/best state continues identically.
        first=out/f'{label}_split_first.txt';first.write_text(input_text(p,ss,23,1,3.25),encoding='utf-8',newline='\n')
        split1=invoke(first,out/f'{label}_split_first.json','gpu')
        second=out/f'{label}_split_second.txt';second.write_text(input_text(p,split1['chains'],41,1,3.25),encoding='utf-8',newline='\n')
        split2=invoke(second,out/f'{label}_split_second.json','gpu')
        whole=read(out/f'{label}_anneal_gpu.json')
        for a,b,z in zip(split1['chains'],split2['chains'],whole['chains'],strict=True):
            expected=deepcopy(z);expected['trace']=expected['trace'][23:]
            need(b==expected and a['trace']==z['trace'][:23],'checkpoint split replay')
        if positive is not None:
            for a,b in [(63,64),(127,128)]:
                boundary=deepcopy(ss);boundary[0]['rng']=str(boundary_seed(p['m'],a,b))
                inp=out/f'boundary_{a}_{b}.txt';inp.write_text(input_text(p,boundary,1,0,0),encoding='utf-8',newline='\n')
                cpu=invoke(inp,out/f'boundary_{a}_{b}_cpu.json','cpu');gpu=invoke(inp,out/f'boundary_{a}_{b}_gpu.json','gpu')
                need(cpu['chains']==gpu['chains'] and gpu['chains'][0]['trace'][0][1:3]==[a,b],'explicit word-boundary parity')
                moves+=check_trace(p,boundary,gpu)
                save(out/f'boundary_{a}_{b}_raw_final.json',raw_object(p,gpu['chains'][0]['permutations'],gpu['chains'][0]['score']))
    # Native malformed controls exercise the actual executable, not a substitute parser.
    p=problem(core_data('shift6')[0]);ss=states(p,20260930,1);valid=input_text(p,ss,0,1,0)
    failures=[]
    for label in ['zero_rng','duplicate_permutation','duplicate_catalog','asymmetric_target','trailing_input']:
        pp=deepcopy(p);tt=deepcopy(ss)
        if label=='zero_rng':tt[0]['rng']='0'
        if label=='duplicate_permutation':tt[0]['permutations'][0][1]=tt[0]['permutations'][0][0]
        if label=='duplicate_catalog':pp['edges'][0][1]=pp['edges'][0][0]
        if label=='asymmetric_target':pp['target'][0][1]+=1
        text=input_text(pp,tt,0,1,0)+('unexpected\n' if label=='trailing_input' else '')
        inp=out/f'bad_{label}.txt';inp.write_text(text,encoding='utf-8',newline='\n')
        receipt=invoke(inp,out/f'bad_{label}.json','gpu',expect_ok=False);failures.append(dict(control=label,error=receipt['stderr']))
    altered=deepcopy(read(out/'shift6_forced_gpu.json'));altered['chains'][0]['trace'][0][3]+=1
    try:check_trace(problem(core_data('shift6')[0]),read(out/'shift6_initial.json'),altered)
    except ValueError as e:failures.append(dict(control='corrupted_delta_trace',error=str(e)))
    else:raise AssertionError('corrupt delta accepted')
    return dict(status='CANDIDATE_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_COMPLETE',objective_version=VERSION,domain='Two independently permuted nonmatching-edge incidence catalogs; C0 canonical; fixed exact valid core.',hardware=hardware,records=records,deterministic_proposals_checked=moves,checkpoint_split_controls=3,malformed_controls_rejected=failures,raw_best_objects=raw_outputs,known_positive='SRG243 abstract factor starts at integer E=0; n20 fixture only, not target99.',scope='Calibration only: no restart campaign, no completeness or performance guarantee.',target_resolution=False,independent_review_required=True)

def run_chunks(args,out):
    need(args.independent_gate and args.independent_gate_sha256,'independent audit gate required before research chunks')
    need(digest(args.independent_gate)==args.independent_gate_sha256,'gate digest');gate=read(args.independent_gate)
    need(gate['status']=='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS','gate status')
    for p in [SOURCE,BUILDER,EXE,Path(__file__),SPEC]:need(gate['inputs_sha256'].get(key(p))==digest(p),'gate exact source/binary binding')
    need(args.core in ('shift6','six_prism'),'only two audited target cores enabled')
    need(1<=args.chains<=256 and 1<=args.chunks<=10000 and 1<=args.steps<=1024 and 0<args.seconds<=3600,'bounded resource configuration')
    need(0<=args.temperature<=1e6,'temperature bound')
    p=problem(core_data(args.core)[0]);ss=states(p,args.seed,args.chains)
    if args.resume:
        prev=read(args.resume);need(prev['problem']==p and prev['objective_version']==VERSION,'resume domain/objective binding');ss=prev['chains']
        need(prev['source_sha256']==digest(SOURCE) and prev['binary_sha256']==digest(EXE),'resume exact engine binding')
        need(len(ss)==args.chains,'resume chain count')
    start=time.monotonic();completed=0;best_path=None
    for chunk in tqdm(range(args.chunks),desc='Annealing chunks'):
        if time.monotonic()-start>=args.seconds:break
        inp=out/f'chunk_{chunk:05d}.txt';inp.write_text(input_text(p,ss,args.steps,1,args.temperature),encoding='utf-8',newline='\n')
        result=invoke(inp,out/f'chunk_{chunk:05d}.json','gpu',timeout=min(60,args.seconds));ss=result['chains'];completed+=1
        checkpoint=dict(timestamp=timestamp(),objective_version=VERSION,problem=p,chains=ss,source_sha256=digest(SOURCE),binary_sha256=digest(EXE),chunk=chunk,elapsed_seconds=time.monotonic()-start)
        save(out/f'checkpoint_{chunk:05d}.json',checkpoint)
        best=min(ss,key=lambda s:s['best_score']);best_path=out/f'best_{chunk:05d}.json';save(best_path,raw_best(p,best))
        tqdm.write(f'chunk={chunk} proposals={sum(s["proposals"] for s in ss)} best_integer_E={best["best_score"]}')
        if best['best_score']==0:break
    return dict(status='CANDIDATE_FACTOR_PERMUTATION_CHUNKS_COMPLETED',objective_version=VERSION,completed_chunks=completed,best_raw_object=key(best_path) if best_path else None,best_score=min(s.get('best_score',full_score(p,s['best_permutations'])) for s in ss),search_seconds=time.monotonic()-start,independent_review_required=True,target_resolution=False,stopping='E0, declared chunk cap or time checked between chunks; a native call may add at most its 60-second subprocess cap.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['calibrate','run']);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--core',choices=['shift6','six_prism'],default='shift6');ap.add_argument('--chains',type=int,default=32);ap.add_argument('--chunks',type=int,default=1);ap.add_argument('--steps',type=int,default=256);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--temperature',type=float,default=3.25);ap.add_argument('--seed',type=int,default=20260930);ap.add_argument('--resume',type=Path);ap.add_argument('--independent-gate',type=Path);ap.add_argument('--independent-gate-sha256')
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    for p,h in PINS.items():need(digest(p)==h,'pinned local-core/fixture source changed')
    geometry_pin=read(PRISM_GATE)['derived_geometry_sha256']
    need(digest(PRISM)==geometry_pin,'independent prism geometry pin')
    inputs=[Path(__file__),SOURCE,BUILDER,SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml',PRISM,*PINS]
    for p in [args.resume,args.independent_gate]:
        if p:inputs.append(p.resolve())
    common=dict(timestamp=timestamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins(inputs),configuration=vars(args)|{'out':str(args.out),'resume':str(args.resume) if args.resume else None,'independent_gate':str(args.independent_gate) if args.independent_gate else None})
    save(out/'manifest.json',common)
    try:
        result=calibration(out) if args.mode=='calibrate' else run_chunks(args,out)
        result.update(common);result['binary_sha256']=digest(EXE);result['outputs_sha256']=pins([p for p in out.iterdir() if p.is_file()])
        save(out/'summary.json',result);print(json.dumps({'status':result['status'],'summary_sha256':digest(out/'summary.json')}))
    except Exception as e:
        save(out/'failure.json',dict(timestamp=timestamp(),error_type=type(e).__name__,error=str(e)));raise

if __name__=='__main__':main()
