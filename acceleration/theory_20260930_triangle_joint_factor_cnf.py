"""Build exact joint C1/C2 binary factor CNF for the fixed Wave149 core."""
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
from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, counter_controls, digest, package, save

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'external_conway99_research'
PIN='85e705cc6c2a14d123120c93a847e30aaab1789e'
E=[list(e) for e in combinations(range(12),2) if e[1]!=(e[0]^1)]


def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()


def target():
    result=[]
    for a in range(36):
        row=[]
        for b in range(36):
            i,j=a%12,b%12
            if a//12==b//12:v=10 if i==j else (0 if j==(i^1) else 1)
            elif a//12==0 or b//12==0:v=2-int(i==j)-2*int(j==(i^1))-int(j==((i+6)%12))
            else:v=2-int(i==j)-int(j==((i+6)%12))-2*int(j==(((i^1)+6)%12))
            row.append(v)
        result.append(row)
    assert result==[list(r) for r in zip(*result)]
    return result


def check_factor(c,g):
    if not c or any(len(r)!=60 or any(type(x)is not int or x not in (0,1) for x in r) for r in c):return False
    if any(sum(r)!=10 for r in c):return False
    if any(sum(c[a][d] for a in range(s,s+12))!=2 for s in range(0,len(c),12) for d in range(60)):return False
    return all(sum(c[a][d]*c[b][d] for d in range(60))==g[a][b] for a in range(len(c)) for b in range(len(c)))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    cap=ResourceCap();cap.check()
    archive_paths=[ARCHIVE/'attempts/wave149-terwilliger-triple/exact-results.json',ARCHIVE/'attempts/wave151-triangle-root-factor/exact-results.json',ARCHIVE/'attempts/wave154-triangle-factor-portfolio/exact-results.json']
    for p in archive_paths:assert subprocess.check_output(['git','-C',str(ARCHIVE),'show',PIN+':'+p.relative_to(ARCHIVE).as_posix()])==p.read_bytes()
    sources=[Path(__file__),Path(__file__).with_name('theory_20260930_triangle_joint_factor_cnf_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/theory_20260930_eight_full99_cnf.py',*archive_paths,ROOT/'acceleration/results/20260930_triangle_q1_binary_scout/joint_model_size.json']
    manifest={'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'platform':platform.platform(),'uv_version':subprocess.check_output(['uv','--version'],text=True).strip(),'inputs_sha256':{key(p):digest(p) for p in sources},'archive_repository':'https://github.com/YesterdaysLemon/conway-99-research','archive_commit':PIN,'limits':{'build_seconds':120,'memory_bytes':8*1024**3,'solver_calls':0},'scope':'All binary36x60 factors of the fixed Wave149 core Gram, up to C0 column labelling; C1/C2 entirely free. No residualD or unrestricted containment.','status':'CANDIDATE_ENCODING_BUILD','target_automorphism_assumed':False,'random_seed':None,'random_seed_reason':'Deterministic integer construction.','numerical_thresholds':None,'numerical_thresholds_reason':'Exact Boolean and integer operations.'}
    save(out/'manifest.json',manifest)
    try:
        g=target();archive_g=json.loads(archive_paths[0].read_bytes())['minimal_surviving_witness']['gram_rows'];assert g==archive_g
        c0=[[int(a in e) for e in E] for a in range(12)]
        controls=[]
        for p,k in [(archive_paths[1],'exact_partial_factor'),(archive_paths[2],'second_exact_Q1_representative')]:
            q=json.loads(p.read_bytes())[k]['Q1'];c=c0+[[int(a in E[q[d]]) for d in range(60)] for a in range(12)]
            assert check_factor(c,g);c[12][0]^=1;assert not check_factor(c,g)
            controls.append({'archive_factor':key(p),'full24row_exact_Gram_pass':True,'single_bit_corruption_rejected':True})
        save(out/'object_controls.json',{'controls':controls,'positive36row_factor_available':False,'limitation':'Two-group positive controls only; not a complete36row factor.'})
        save(out/'counter_controls.json',counter_controls())
        known=[r.copy() for r in c0]+[[-1]*60 for _ in range(24)];zeros=[];entries=[]
        for row in range(12,36):
            for d,e in enumerate(E):
                reasons=[a for a in e if g[a][row]==0]
                if reasons:known[row][d]=0;zeros.append({'row':row,'column':d,'C0_rows_with_zero_target':reasons})
                else:entries.append({'id':len(entries)+1,'row':row,'column':d})
        symbolic=[[bool(x) if x>=0 else None for x in r] for r in known]
        for item in entries:symbolic[item['row']][item['column']]=item['id']
        scope={'schema':'FIXED_TRIANGLE_JOINT_BINARY_FACTOR_SCOPE_V1','core':{'internal_matchings':[[i^1 for i in range(12)]]*3,'F01':list(range(12)),'F02':list(range(12)),'P12':[(i+6)%12 for i in range(12)]},'edge_columns_C0':E,'target_gram_rows':g,'known_incidence_rows':known,'forced_zero_witnesses':zeros,'entry_variables':entries,'row_sum':10,'column_sum_per_fibre':2,'C0_normalization':'Each nonmatching pair occurs once by its Gram entry1; relabel60columns lexicographically.','target_automorphism_assumed':False,'unrestricted_target_coverage':False,'Q1_fixed':False,'Q2_fixed':False,'residual_D_included':False}
        save(out/'scope.json',scope);products=[];rows=[]
        with (out/'clauses.body').open('xb') as body:
            clauses=Clauses(body,cap);enc=Encoder(len(entries),clauses)
            for fibre in (1,2):
                for a in range(12):
                    row=12*fibre+a;rows.append(enc.counter([x for x in symbolic[row] if type(x)is int],10,True,{'kind':'row_margin','row':row,'constant':0,'original_bound':10}))
                for d in range(60):rows.append(enc.counter([symbolic[12*fibre+a][d] for a in range(12) if type(symbolic[12*fibre+a][d])is int],2,True,{'kind':'column_margin','fibre':fibre,'column':d,'constant':0,'original_bound':2}))
                for a in range(12):
                    for b in range(12):
                        row=12*fibre+b;terms=[symbolic[row][d] for d,e in enumerate(E) if a in e and type(symbolic[row][d])is int]
                        rows.append(enc.counter(terms,g[a][row],True,{'kind':'C0_cross_gram','pair':[a,row],'constant':0,'original_bound':g[a][row]}))
            for a,b in combinations(range(12,36),2):
                terms=[]
                for d in range(60):
                    x,y=symbolic[a][d],symbolic[b][d]
                    if type(x)is int and type(y)is int:
                        first=clauses.count+1;z=enc.conjunction(x,y);products.append({'id':z,'left':x,'right':y,'pair':[a,b],'column':d,'first_clause':first,'clause_count':3});terms.append(z)
                rows.append(enc.counter(terms,g[a][b],True,{'kind':'unknown_pair_gram','pair':[a,b],'constant':0,'original_bound':g[a][b]}))
        cnf=out/'instance.cnf'
        with cnf.open('xb') as f,(out/'clauses.body').open('rb') as body:f.write(('p cnf %d %d\n'%(enc.top,clauses.count)).encode('ascii'));shutil.copyfileobj(body,f,1048576)
        model={'schema':'FIXED_TRIANGLE_JOINT_BINARY_FACTOR_PREFIX_CNF_V1','scope_path':key(out/'scope.json'),'scope_sha256':digest(out/'scope.json'),'known_incidence_rows':known,'target_gram_rows':g,'entry_variables':entries,'product_variables':products,'counter_rows':rows,'variables':enc.top,'clauses':clauses.count,'prefix_reference_format':'JSON booleans are constants; positive integers are variable IDs.','clauses_constant_folded':True,'gate_clause_order':{'and':['a -z','b -z','-a -b z'],'or':['-a z','-b z','a b -z'],'a_or_b_and_c':['-a z','-b -c z','a b -z','a c -z']},'solver_calls':0,'full_target_graph_encoded':False}
        save(out/'model.json',model);cap.check()
        actual={'variables':enc.top,'clauses':clauses.count,'primary_entries':len(entries),'AND_products':len(products),'counter_rows':len(rows),'forced_zeros':len(zeros)}
        assert actual=={'variables':58860,'clauses':203748,'primary_entries':1200,'AND_products':11400,'counter_rows':708,'forced_zeros':240}
        save(out/'artifact_packages.json',{'packages':[package(p,cap) for p in (cnf,out/'model.json')],'retrieval':'Concatenate gzip parts and decompress; check exact original bytes and SHA256.'})
        for p,h in manifest['inputs_sha256'].items():assert digest(ROOT/p)==h
        summary={'status':'CANDIDATE_JOINT_FIXED_CORE_BINARY_FACTOR_CNF','independent_encoding_review':'PENDING','timestamp':datetime.now(timezone.utc).isoformat(),**actual,'elapsed_seconds':time.monotonic()-cap.start,'peak_working_set_bytes':cap.peak_bytes,'solver_calls':0,'target_resolution':False,'outputs':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file() and p.name!='clauses.body'},'limitations':['No fixedQ1 assumption; all binary factors of this fixed core require coverage audit.','SAT is only a36x60factor, not a99vertex graph.','UNSAT needs independent exact input/encoding and complete proof replay.','No unrestricted core containment or target nonexistence claim.']}
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}))
    except BaseException as e:
        save(out/'failure.json',{'status':'INCOMPLETE_BUILD','error':repr(e),'elapsed_seconds':time.monotonic()-cap.start});raise


if __name__=='__main__':main()
