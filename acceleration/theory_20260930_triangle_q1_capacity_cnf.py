"""Build exact first-factor projection with necessary component capacities."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import Clauses,Encoder,ResourceCap,counter_controls,digest,package,save

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf'
KERNEL=ROOT/'acceleration/results/20260930_triangle_factor_components/kernel_certificate.json'
PINS={BASE/'scope.json':'51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0',KERNEL:'34852bbae744a346c87843bdd76d1697767cbbc9d9ad0b2276e9c8ccba47e0e1',ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json':'03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b'}


def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);cap=ResourceCap()
    for p,h in PINS.items():assert digest(p)==h
    inputs=[Path(__file__),Path(__file__).with_name('theory_20260930_triangle_q1_capacity_cnf_spec.md'),*PINS,ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'uv_version':subprocess.check_output(['uv','--version'],text=True).strip(),'inputs_sha256':{key(p):digest(p) for p in inputs},'status':'CANDIDATE_PROJECTED_ENCODING','scope':'Exact24x60first factor with component partial capacity; necessary not sufficient for fixedcore extension.','limits':{'build_seconds':120,'memory_bytes':8*1024**3,'solver_calls':0},'random_seed':None,'random_seed_reason':'Deterministic exact construction.','target_automorphism_assumed':False})
    save(out/'counter_controls.json',counter_controls())
    base=json.loads((BASE/'scope.json').read_bytes());kernel=json.loads(KERNEL.read_bytes());known=base['known_incidence_rows'][:24];gram=[r[:24] for r in base['target_gram_rows'][:24]];components=kernel['components'];entries=[x for x in base['entry_variables'] if x['row']<24]
    assert len(entries)==600 and [x['id'] for x in entries]==list(range(1,601))
    symbolic=[[bool(x) if x>=0 else None for x in r] for r in known]
    for item in entries:symbolic[item['row']][item['column']]=item['id']
    scope={'schema':'FIXED_TRIANGLE_Q1_COMPONENT_CAPACITY_SCOPE_V1','parent_scope':key(BASE/'scope.json'),'parent_scope_sha256':digest(BASE/'scope.json'),'kernel_certificate':key(KERNEL),'kernel_certificate_sha256':digest(KERNEL),'known_incidence_rows':known,'target_gram_rows':gram,'entry_variables':entries,'edge_columns_C0':base['edge_columns_C0'],'components':components,'row_sum':10,'column_sum_per_fibre':2,'partial_component_column_upper_bound':2,'C1_free':True,'C2_included':False,'D_included':False,'full_core_coverage_relation':'Every full fixedcore factor restricts to a model; converse extension not claimed.','unrestricted_target_coverage':False,'target_automorphism_assumed':False}
    save(out/'scope.json',scope);rows=[];products=[]
    with (out/'clauses.body').open('xb') as body:
        clauses=Clauses(body,cap);enc=Encoder(600,clauses)
        for row in range(12,24):rows.append(enc.counter([x for x in symbolic[row] if type(x)is int],10,True,{'kind':'row_margin','row':row,'constant':0,'original_bound':10}))
        for d in range(60):rows.append(enc.counter([symbolic[row][d] for row in range(12,24) if type(symbolic[row][d])is int],2,True,{'kind':'column_margin','fibre':1,'column':d,'constant':0,'original_bound':2}))
        for a in range(12):
            for b in range(12,24):rows.append(enc.counter([symbolic[b][d] for d in range(60) if known[a][d]==1 and type(symbolic[b][d])is int],gram[a][b],True,{'kind':'C0_cross_gram','pair':[a,b],'constant':0,'original_bound':gram[a][b]}))
        for a,b in combinations(range(12,24),2):
            terms=[]
            for d in range(60):
                x,y=symbolic[a][d],symbolic[b][d]
                if type(x)is int and type(y)is int:
                    first=clauses.count+1;z=enc.conjunction(x,y);products.append({'id':z,'left':x,'right':y,'pair':[a,b],'column':d,'first_clause':first,'clause_count':3});terms.append(z)
            rows.append(enc.counter(terms,gram[a][b],True,{'kind':'unknown_pair_gram','pair':[a,b],'constant':0,'original_bound':gram[a][b]}))
        for ci,component in enumerate(components):
            support=[r for r in component if r<24]
            for d in range(60):
                constant=sum(symbolic[r][d] is True for r in support);terms=[symbolic[r][d] for r in support if type(symbolic[r][d])is int]
                rows.append(enc.counter(terms,2-constant,False,{'kind':'partial_component_capacity','component':ci,'column':d,'raw_component_rows':component,'included_rows':support,'constant':constant,'original_bound':2}))
    cnf=out/'instance.cnf'
    with cnf.open('xb') as f,(out/'clauses.body').open('rb') as body:f.write(('p cnf %d %d\n'%(enc.top,clauses.count)).encode('ascii'));shutil.copyfileobj(body,f,1048576)
    model={'schema':'TRIANGLE_Q1_COMPONENT_CAPACITY_PREFIX_CNF_V1','scope_path':key(out/'scope.json'),'scope_sha256':digest(out/'scope.json'),'known_incidence_rows':known,'target_gram_rows':gram,'entry_variables':entries,'product_variables':products,'counter_rows':rows,'components':components,'variables':enc.top,'clauses':clauses.count,'prefix_reference_format':'JSON booleans are constants; positive integers are variableIDs.','gate_clause_order':{'and':['a -z','b -z','-a -b z'],'or':['-a z','-b z','a b -z'],'a_or_b_and_c':['-a z','-b -c z','a b -z','a c -z']},'clauses_constant_folded':True,'full_target_graph_encoded':False,'complete36row_factor_encoded':False,'C2_included':False,'solver_calls':0}
    save(out/'model.json',model);cap.check();assert len(rows)==462
    controls=[]
    for name,field in [('wave151-triangle-root-factor','exact_partial_factor'),('wave154-triangle-factor-portfolio','second_exact_Q1_representative')]:
        p=ROOT/'external_conway99_research/attempts'/name/'exact-results.json';q=json.loads(p.read_bytes())[field]['Q1'];e=base['edge_columns_C0'];c=known[:12]+[[int(a in e[q[d]]) for d in range(60)] for a in range(12)]
        assert all(sum(c[a][d]*c[b][d] for d in range(60))==gram[a][b] for a in range(24) for b in range(24))
        violations=[(ci,d) for ci,component in enumerate(components) for d in range(60) if sum(c[a][d] for a in component if a<24)>2];assert violations
        controls.append({'source':key(p),'sha256':digest(p),'exact24row_Gram_pass':True,'component_overflows':violations,'expected_rejected_by_projection':True})
    save(out/'archived_factor_controls.json',controls)
    save(out/'artifact_packages.json',{'packages':[package(p,cap) for p in (cnf,out/'model.json')],'retrieval':'Concatenate gzip parts, decompress, verify exact length/hash.'})
    summary={'status':'CANDIDATE_Q1_CAPACITY_PROJECTION_CNF','independent_verification':'PENDING','variables':enc.top,'clauses':clauses.count,'entry_variables':600,'AND_products':len(products),'counter_rows':len(rows),'equality_rows':282,'capacity_rows':180,'elapsed_seconds':time.monotonic()-cap.start,'peak_working_set_bytes':cap.peak_bytes,'solver_calls':0,'target_resolution':False,'outputs':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file() and p.name!='clauses.body'},'limitations':['SAT only provides24rows, neither36factor nor99graph.','UNSAT needs exactencoding/necessary-projection review and completeindependentproof.','No unrestricted fixedcore containment.']}
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}))


if __name__=='__main__':main()
