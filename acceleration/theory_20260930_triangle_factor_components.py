"""Candidate entailed component-column extension of the joint factor CNF."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import Clauses,Encoder,ResourceCap,digest,package,save,counter_controls

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf'
CNF=BASE/'instance.cnf';MODEL=BASE/'model.json';SCOPE=BASE/'scope.json'
PINS={CNF:'c56b4b5511530efe2ee08934549a1a3f012b8481741f70b58faa440fdaef032c',MODEL:'d1a52720be73dfdc809a86c7d872ad4d36aaccb3c0b104f9565338ba43a9f1fb',SCOPE:'51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0'}


def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);cap=ResourceCap()
    for p,h in PINS.items():assert digest(p)==h
    paths=[Path(__file__),Path(__file__).with_name('theory_20260930_triangle_factor_components_spec.md'),*PINS,ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'inputs_sha256':{key(p):digest(p) for p in paths},'limits':{'seconds':120,'memory_bytes':8*1024**3},'status':'CANDIDATE_ENTAILED_EXTENSION','solver_calls':0,'scope':'Fixed39core joint binary factor only.'})
    scope=json.loads(SCOPE.read_bytes());model=json.loads(MODEL.read_bytes());core=scope['core'];adj=[set() for _ in range(36)]
    def edge(a,b):adj[a].add(b);adj[b].add(a)
    for g,m in enumerate(core['internal_matchings']):
        for a,b in enumerate(m):edge(12*g+a,12*g+b)
    for a,b in enumerate(core['F01']):edge(a,12+b)
    for a,b in enumerate(core['F02']):edge(a,24+b)
    for a,b in enumerate(core['P12']):edge(12+a,24+b)
    assert all(len(x)==3 for x in adj)
    remaining=set(range(36));components=[]
    while remaining:
        seen=set();todo=[min(remaining)]
        while todo:
            a=todo.pop()
            if a not in seen:seen.add(a);todo.extend(adj[a]-seen)
        components.append(sorted(seen));remaining-=seen
    assert len(components)==3 and all(len(c)==12 and all(sum(a//12==g for a in c)==4 for g in range(3)) for c in components)
    gram=scope['target_gram_rows'];contrasts=[]
    for c in (1,2):
        v=[int(a in components[0])-int(a in components[c]) for a in range(36)];image=[sum(row[a]*v[a] for a in range(36)) for row in gram];assert image==[0]*36
        contrasts.append({'vector':v,'exact_Kv':image,'exact_quadratic':sum(x*y for x,y in zip(v,image))})
    save(out/'kernel_certificate.json',{'adjacency_core_rows':[sorted(x) for x in adj],'components':components,'target_gram_rows':gram,'contrast_certificates':contrasts,'column_total':6,'entailed_component_column_total':2,'argument':'CC^T=K implies squared_norm(C^Tv)=v^TKv=0; counts equal across3components and sum6.'})
    save(out/'counter_controls.json',counter_controls())
    symbolic=[[bool(x) if x>=0 else None for x in r] for r in model['known_incidence_rows']]
    for item in model['entry_variables']:symbolic[item['row']][item['column']]=item['id']
    appended=[];suffix=out/'component_equalities.cnfpart'
    with suffix.open('xb') as f:
        clauses=Clauses(f,cap);enc=Encoder(model['variables'],clauses)
        for ci,component in enumerate(components):
            for d in range(60):
                constant=sum(symbolic[r][d] is True for r in component);inputs=[symbolic[r][d] for r in component if type(symbolic[r][d])is int]
                row=enc.counter(inputs,2-constant,True,{'kind':'component_column_margin','component':ci,'column':d,'raw_component_rows':component,'constant':constant,'original_bound':2})
                row['first_clause']+=model['clauses'];appended.append(row)
    total_clauses=model['clauses']+clauses.count;cnf=out/'instance.cnf'
    with cnf.open('xb') as f,CNF.open('rb') as base,suffix.open('rb') as tail:
        assert base.readline()==b'p cnf 58860 203748\n';f.write(('p cnf %d %d\n'%(enc.top,total_clauses)).encode('ascii'));shutil.copyfileobj(base,f,1048576);shutil.copyfileobj(tail,f,1048576)
    new_model=dict(model);new_model.update(schema='FIXED_TRIANGLE_JOINT_BINARY_FACTOR_COMPONENT_PREFIX_CNF_V1',base_model_path=key(MODEL),base_model_sha256=PINS[MODEL],base_cnf_sha256=PINS[CNF],component_kernel_certificate=key(out/'kernel_certificate.json'),component_kernel_certificate_sha256=digest(out/'kernel_certificate.json'),counter_rows=model['counter_rows']+appended,variables=enc.top,clauses=total_clauses,appended_component_counters=180)
    save(out/'model.json',new_model);save(out/'appended_rows.json',appended)
    factor_inputs=[(ROOT/'external_conway99_research/attempts/wave151-triangle-root-factor/exact-results.json','exact_partial_factor'),(ROOT/'external_conway99_research/attempts/wave154-triangle-factor-portfolio/exact-results.json','second_exact_Q1_representative')]
    factors=[(p,json.loads(p.read_bytes())[k]['Q1']) for p,k in factor_inputs]
    for p in sorted((ROOT/'acceleration/results/20260930_triangle_q1_binary_scout').glob('factor_??.json')):factors.append((p,json.loads(p.read_bytes())['Q1']))
    e=scope['edge_columns_C0'];diagnostics=[]
    for p,q in factors:
        violations=[]
        for ci,comp in enumerate(components):
            for d in range(60):
                known_rows=[a for a in comp if (a<12 and a in e[d]) or (12<=a<24 and a-12 in e[q[d]])]
                if len(known_rows)>2:violations.append({'component':ci,'column':d,'known_incidence_rows':known_rows,'count':len(known_rows)})
        diagnostics.append({'factor_input':key(p),'factor_sha256':digest(p),'Q1':q,'overflow_count':len(violations),'violations':violations,'status':'CANDIDATE_COMPONENT_OVERFLOW' if violations else 'NO_OVERFLOW_OBSTRUCTION_FOUND'})
    save(out/'five_Q1_diagnostic.json',diagnostics);cap.check()
    save(out/'artifact_packages.json',{'packages':[package(p,cap) for p in (cnf,out/'model.json')],'retrieval':'Concatenate gzip parts and decompress; verify raw length and SHA256.'})
    for p,h in PINS.items():assert digest(p)==h
    summary={'status':'CANDIDATE_COMPONENT_STRENGTHENED_FACTOR_ENCODING','independent_verification':'PENDING','base_variables':model['variables'],'base_clauses':model['clauses'],'new_variables':enc.top-model['variables'],'appended_clauses':clauses.count,'variables':enc.top,'clauses':total_clauses,'component_equations':180,'five_Q1_overflow_counts':[x['overflow_count'] for x in diagnostics],'elapsed_seconds':time.monotonic()-cap.start,'peak_working_set_bytes':cap.peak_bytes,'solver_calls':0,'target_resolution':False,'scope':'Same fixed39core factor family; entailed strengthening pending independent review.','outputs':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}}
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}))


if __name__=='__main__':main()
