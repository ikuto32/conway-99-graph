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
SPEC=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v4_spec.md'
PREDECESSOR=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v3.py'
NATIVE_GATE=ROOT/'acceleration/results/20260930_independent_review/factor_permutation_annealer_bound/summary.json'
VERSION='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'
PORTFOLIO_SUMMARY=ROOT/'acceleration/results/20260930_connected_identity_cores/summary.json'
PORTFOLIO_SUMMARY_SHA='3ab78be8b7a7582c730e4cfe4c95533a2bc68cecccdfca45fa7d3f8cd58190b5'
PORTFOLIO={
 'connected_00':(ROOT/'acceleration/results/20260930_connected_identity_cores/core_00.json','3d4ad2d5b8ff92ca3d7761ac79e3651e306052897c3327b4eec87d7a85dabe81'),
 'connected_01':(ROOT/'acceleration/results/20260930_connected_identity_cores/core_01.json','23fb79efbc42fcaf7d54edb32311703be47fa96014a1c46ed00859a0753576e4'),
 'connected_02':(ROOT/'acceleration/results/20260930_connected_identity_cores/core_02.json','40c23054a9276039b0dc1320594f102ae65d06c8e2c819a31d6600c3ee279eeb'),
 'connected_03':(ROOT/'acceleration/results/20260930_connected_identity_cores/core_03.json','cdd61bb140888090f092af7bbc3dbc40399f8e06bb3b41781dcfba22f0f701f1')}
CORE_NAMES=('shift6','six_prism',*PORTFOLIO)
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
    if label in PORTFOLIO:
        path,identity=PORTFOLIO[label];need(digest(path)==identity,'exact selected portfolio core bytes')
        raw=read(path);derived=problem(raw['core_adjacency'])
        need(derived['target']==raw['target_gram'] and derived['edges']==raw['nonmatching_edge_catalogs'],'portfolio raw Gram/catalog equals wrapper derivation')
        return raw['core_adjacency'],None
    if label=='shift6':
        x=read(SHIFT)['core'];n=12;c=[[0]*36 for _ in range(36)]
        for g in range(3):
            for i,j in enumerate(x['internal_matchings'][g]):c[g*n+i][g*n+j]=1
        for g,h,name in [(0,1,'F01'),(0,2,'F02'),(1,2,'P12')]:
            for i,j in enumerate(x[name]):c[g*n+i][h*n+j]=c[h*n+j][g*n+i]=1
        return c,None
    if label=='six_prism':return read(PRISM)['core_adjacency'],None
    need(label=='fixture243','unknown core label')
    x=read(FIXTURE);return x['cubic_core60'],x['factor60x180']

def bind_portfolio(args):
    needed=args.core in PORTFOLIO or args.mode=='portfolio-calibrate'
    if not needed:
        need(args.portfolio_domain_gate is None and args.portfolio_domain_gate_sha256 is None,'old-core modes do not accept unused portfolio gate arguments')
        return []
    need(args.portfolio_domain_gate is not None and args.portfolio_domain_gate_sha256 is not None,'separate independent portfolio domain gate required')
    need(digest(args.portfolio_domain_gate)==args.portfolio_domain_gate_sha256,'portfolio domain gate hash')
    gate=read(args.portfolio_domain_gate)
    need(gate['status']=='INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS','independent exact local-domain gate')
    need(digest(PORTFOLIO_SUMMARY)==PORTFOLIO_SUMMARY_SHA,'fixed portfolio selection summary')
    paths=[PORTFOLIO_SUMMARY,args.portfolio_domain_gate.resolve()]
    for p in [PORTFOLIO_SUMMARY,*[item[0] for item in PORTFOLIO.values()]]:
        need(gate['inputs_sha256'].get(key(p))==digest(p),'domain gate binds every selected source artifact');paths.append(p)
    for p,h in PORTFOLIO.values():need(digest(p)==h,'frozen four-core portfolio membership')
    return list(dict.fromkeys(paths))

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
    edges=[[list(pair) for pair in combinations(range(n),2) if not c[g*n+pair[0]][g*n+pair[1]]] for g in range(3)]
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

def run_chunks(args,out,calibration_only=False):
    if calibration_only:
        need(args.independent_gate is None and args.independent_gate_sha256 is None,'calibration route does not fabricate a research gate')
        need(args.core in CORE_NAMES and args.seed==20260930 and args.chains==2 and args.chunks==1 and args.steps in (23,41,64) and args.seconds==30 and args.temperature==3.25,'fixed small public-resume calibration configuration')
        need(bool(args.resume)==(args.steps==41),'only41-step calibration chunk resumes')
        kernel_gate=NATIVE_GATE
        need(digest(kernel_gate)=='70c54735a3331f4bc9dff3ace2f5d1dd4bae49ec051f415a262538f9385b20b9','frozen native calibration gate')
        frozen_gate=read(kernel_gate)
        for p in [SOURCE,BUILDER,EXE]:need(frozen_gate['inputs_sha256'].get(key(p))==digest(p),'unchanged calibrated native source/binary')
    else:
        need(args.independent_gate and args.independent_gate_sha256,'independent audit gate required before research chunks')
        need(digest(args.independent_gate)==args.independent_gate_sha256,'gate digest');gate=read(args.independent_gate)
        need(gate['status']=='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS','gate status')
        for p in [SOURCE,BUILDER,EXE,Path(__file__),SPEC]:need(gate['inputs_sha256'].get(key(p))==digest(p),'gate exact source/binary binding')
        if args.core in PORTFOLIO:
            for p in [args.portfolio_domain_gate.resolve(),PORTFOLIO_SUMMARY,*[item[0] for item in PORTFOLIO.values()]]:
                need(gate['inputs_sha256'].get(key(p))==digest(p),'fresh wrapper gate binds exact independent portfolio admission')
    need(args.core in CORE_NAMES,'only the two old cores and four hash-bound connected cores enabled')
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
    return dict(status='CALIBRATION_ONLY_FACTOR_PERMUTATION_CHUNK_COMPLETED' if calibration_only else 'CANDIDATE_FACTOR_PERMUTATION_CHUNKS_COMPLETED',calibration_only=calibration_only,objective_version=VERSION,completed_chunks=completed,best_raw_object=key(best_path) if best_path else None,best_score=min(s.get('best_score',full_score(p,s['best_permutations'])) for s in ss),search_seconds=time.monotonic()-start,independent_review_required=True,target_resolution=False,stopping='E0, declared chunk cap or time checked between chunks; a native call may add at most its 60-second subprocess cap.')

def resume_regression(out,args=None,core_names=('shift6','six_prism')):
    """Actual public wrapper processes and disk JSON; no synthetic PASS gate."""
    records=[];negative=[];parity=[]
    def launch(label,core,steps,resume=None,expect_ok=True):
        directory=out/label
        command=[sys.executable,str(Path(__file__).resolve()),'calibration-chunk','--out',str(directory),
            '--core',core,'--seed','20260930','--chains','2','--chunks','1','--steps',str(steps),
            '--seconds','30','--temperature','3.25']
        if resume:command+=['--resume',str(resume)]
        if core in PORTFOLIO:
            need(args is not None,'portfolio calibration arguments')
            command+=['--portfolio-domain-gate',str(args.portfolio_domain_gate),'--portfolio-domain-gate-sha256',args.portfolio_domain_gate_sha256]
        start=time.monotonic();result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=45)
        receipt=dict(command=command,cwd=str(ROOT),exit_code=result.returncode,wall_seconds=time.monotonic()-start,
            stdout=result.stdout,stderr=result.stderr,resume_path=key(resume) if resume else None,
            resume_sha256=digest(resume) if resume else None,expect_ok=expect_ok)
        save(out/(label+'.receipt.json'),receipt)
        need((result.returncode==0)==expect_ok,'actual public wrapper outcome '+label)
        return directory
    for core in core_names:
        first=launch(core+'_first23',core,23);checkpoint=first/'checkpoint_00000.json'
        second=launch(core+'_resume41',core,41,checkpoint);whole=launch(core+'_whole64',core,64)
        a,b,z=[read(path/'checkpoint_00000.json') for path in (first,second,whole)]
        need(a['problem']==b['problem']==z['problem']==problem(core_data(core)[0]),'literal JSON problem equality after public reload')
        for initial,continued,total in zip(a['chains'],b['chains'],z['chains'],strict=True):
            left=deepcopy(continued);right=deepcopy(total)
            left_trace=left.pop('trace');right_trace=right.pop('trace')
            need(left==right,'all persisted final/current/best/RNG/proposal fields')
            need(initial['trace']+left_trace==right_trace,'full split versus whole transition trace')
            need(initial['proposals']==23 and continued['proposals']==total['proposals']==64,'public resume proposal continuation')
        records.append(dict(core=core,first_checkpoint=key(checkpoint),first_checkpoint_sha256=digest(checkpoint),
            resumed_checkpoint=key(second/'checkpoint_00000.json'),resumed_checkpoint_sha256=digest(second/'checkpoint_00000.json'),
            whole_checkpoint=key(whole/'checkpoint_00000.json'),whole_checkpoint_sha256=digest(whole/'checkpoint_00000.json'),
            chains=2,first_steps=23,resumed_steps=41,whole_steps=64,all_persisted_fields_and_trace_equal=True))
        if core in PORTFOLIO:
            p=problem(core_data(core)[0]);initial=states(p,20260930,2)
            gpu=read(whole/'chunk_00000.json');cpu=invoke(whole/'chunk_00000.txt',out/(core+'_whole64_cpu.json'),'cpu')
            need(cpu['chains']==gpu['chains'],'new-core full CPU vs unchanged GPU parity')
            checked=check_trace(p,initial,gpu)
            for i,s in enumerate(gpu['chains']):
                save(out/f'{core}_chain{i}_raw_initial.json',raw_object(p,initial[i]['permutations'],full_score(p,initial[i]['permutations'])))
                save(out/f'{core}_chain{i}_raw_final.json',raw_object(p,s['permutations'],s['score']))
                save(out/f'{core}_chain{i}_raw_best.json',raw_best(p,s))
            parity.append(dict(core=core,whole_proposals=checked,CPU_GPU_all_chain_fields_equal=True,Python_full_recomputation_all_deltas_equal=True,core_sha256=PORTFOLIO[core][1]))
    control_core=core_names[0]
    original=read(out/(control_core+'_first23')/'checkpoint_00000.json')
    for label in ('wrong_target','changed_edge_pair','wrong_objective','wrong_source_hash','wrong_binary_hash'):
        bad=deepcopy(original)
        if label=='wrong_target':bad['problem']['target'][0][0]+=1
        elif label=='changed_edge_pair':bad['problem']['edges'][0][0]=bad['problem']['edges'][0][1]
        elif label=='wrong_objective':bad['objective_version']='WRONG'
        elif label=='wrong_source_hash':bad['source_sha256']='0'*64
        else:bad['binary_sha256']='0'*64
        path=out/('bad_'+label+'_checkpoint.json');save(path,bad)
        directory=launch('bad_'+label,control_core,41,path,expect_ok=False)
        need(not list(directory.glob('chunk_*')),'corrupt checkpoint rejected before native invocation')
        negative.append(dict(control=label,failure=read(directory/'failure.json'),native_calls=0))
    return dict(status='CANDIDATE_FOUR_CORE_WRAPPER_CALIBRATION_PASS' if parity else 'CANDIDATE_PUBLIC_JSON_RESUME_REGRESSION_PASS',calibration_only=True,
        records=records,public_wrapper_native_calls=3*len(core_names),calibration_proposals=256*len(core_names),new_core_parity=parity,CPU_parity_calls=len(parity),distinct_whole_trajectory_proposals_checked=sum(r['whole_proposals'] for r in parity),
        corrupt_public_resume_controls=negative,independent_review_required=True,target_resolution=False,
        unchanged_native_source_sha256=digest(SOURCE),unchanged_binary_sha256=digest(EXE),
        scope='Four exact connected-core domains, native CPU/GPU/Python parity and actual public disk-checkpoint resume.' if parity else 'Actual disk-checkpoint public Python-wrapper resume only; native algorithm and objective unchanged.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['resume-calibrate','portfolio-calibrate','calibration-chunk','run']);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--core',choices=CORE_NAMES,default='shift6');ap.add_argument('--chains',type=int,default=32);ap.add_argument('--chunks',type=int,default=1);ap.add_argument('--steps',type=int,default=256);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--temperature',type=float,default=3.25);ap.add_argument('--seed',type=int,default=20260930);ap.add_argument('--resume',type=Path);ap.add_argument('--independent-gate',type=Path);ap.add_argument('--independent-gate-sha256');ap.add_argument('--portfolio-domain-gate',type=Path);ap.add_argument('--portfolio-domain-gate-sha256')
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    for p,h in PINS.items():need(digest(p)==h,'pinned local-core/fixture source changed')
    geometry_pin=read(PRISM_GATE)['derived_geometry_sha256']
    need(digest(PRISM)==geometry_pin,'independent prism geometry pin')
    need(digest(PREDECESSOR)=='8f2a85f5a87d1c6a3a37fdb104628c126c67c4ba6ace846b7c9f3b3aba0525b3','unchanged predecessor Python source')
    inputs=[Path(__file__),SOURCE,BUILDER,EXE,SPEC,PREDECESSOR,NATIVE_GATE,ROOT/'uv.lock',ROOT/'pyproject.toml',PRISM,*PINS]
    inputs+=bind_portfolio(args)
    for p in [args.resume,args.independent_gate]:
        if p:inputs.append(p.resolve())
    common=dict(timestamp=timestamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins(inputs),configuration=vars(args)|{'out':str(args.out),'resume':str(args.resume) if args.resume else None,'independent_gate':str(args.independent_gate) if args.independent_gate else None,'portfolio_domain_gate':str(args.portfolio_domain_gate) if args.portfolio_domain_gate else None})
    save(out/'manifest.json',common)
    try:
        if args.mode=='portfolio-calibrate':result=resume_regression(out,args,tuple(PORTFOLIO))
        elif args.mode=='resume-calibrate':result=resume_regression(out)
        else:result=run_chunks(args,out,calibration_only=args.mode=='calibration-chunk')
        result.update(common);result['binary_sha256']=digest(EXE);result['outputs_sha256']=pins([p for p in out.iterdir() if p.is_file()])
        save(out/'summary.json',result);print(json.dumps({'status':result['status'],'summary_sha256':digest(out/'summary.json')}))
    except Exception as e:
        save(out/'failure.json',dict(timestamp=timestamp(),error_type=type(e).__name__,error=str(e)));raise

if __name__=='__main__':main()
