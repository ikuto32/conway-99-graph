"""Producer-only six-prism fixed-cell design, with360independent bit choices."""
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
import native_20260930_unrestricted_full99 as native

ROOT=native.ROOT
SPEC=Path(__file__).with_name('theory_20260930_prism_unpaired_design_spec.md')
GATE=ROOT/'acceleration/results/20260930_native_cli_calibration/summary.json'
GATE_SHA='f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb'

def and_clauses(x,y,z):return [[-x,-y,z],[x,-z],[y,-z]]
def exact(xs,want):
    assert 0<=want<=len(xs)
    return [[-x for x in subset]for subset in combinations(xs,want+1)]+[list(subset)for subset in combinations(xs,len(xs)-want+1)]
def accepts(cs,values):return all(any(values[abs(v)]==int(v>0)for v in c)for c in cs)

def controls():
    for x,y,z in product((0,1),repeat=3):assert accepts(and_clauses(1,2,3),{1:x,2:y,3:z})==(z==(x&y))
    shapes=[]
    for n,k in [(4,2),(4,1),(8,4),(8,2)]:
        cs=exact(list(range(1,n+1)),k)
        for bits in product((0,1),repeat=n):assert accepts(cs,dict(enumerate(bits,1)))==(sum(bits)==k)
        shapes.append(dict(n=n,k=k,assignments=2**n,clauses=len(cs)))
    domains=[]
    for n,t in [(4,1),(8,2)]:
        allowed=0
        for x in range(1<<n):
            for y in range(1<<n):
                selected=((x&y).bit_count(),(x&~y).bit_count(),(~x&y).bit_count(),n-(x|y).bit_count())
                relation=x.bit_count()==2*t and y.bit_count()==2*t and (x&y).bit_count()==t
                assert relation==all(s==t for s in selected)
                allowed+=relation
        domains.append(dict(columns=n,joint_count=t,assignments=1<<(2*n),accepted=allowed))
    assert not accepts(and_clauses(1,2,3),{1:1,2:1,3:0})
    assert not accepts(exact([1,2,3,4],2),{1:1,2:1,3:1,4:0})
    return dict(status='PRODUCER_UNPAIRED_GADGET_CONTROLS_PASS',AND_assignments=8,cardinality_shapes=shapes,complete_domain_equivalence=domains,
                deliberate_bad_AND_rejected=True,deliberate_bad_count_rejected=True,independent_verification=False)

def build():
    matchings=[[[5,t],[(t+1)%5,(t-1)%5],[(t+2)%5,(t-2)%5]]for t in range(5)]
    assert sorted(tuple(sorted(e))for m in matchings for e in m)==list(combinations(range(6),2))
    patterns=[];columns=[];variables=0
    for mi,m in enumerate(matchings):
        for order in permutations(range(3)):
            cells=[None]*6
            for (a,b),g in zip(m,order):cells[a]=cells[b]=g
            pattern=len(patterns);patterns.append(dict(matching=mi,cells=cells))
            for repeat in range(2):
                bits=list(range(variables+1,variables+7));variables+=6
                columns.append(dict(pattern=pattern,repeat=repeat,cells=cells,bit_variables=bits))
    assert variables==360 and len(columns)==60
    products=[];lookup={};clauses=[]
    for d,column in enumerate(columns):
        for a,b in combinations(range(6),2):
            variables+=1;lookup[d,a,b]=variables
            x,y=column['bit_variables'][a],column['bit_variables'][b]
            clauses.extend(and_clauses(x,y,variables));products.append(dict(column=d,components=[a,b],inputs=[x,y],id=variables))
    constraints=[]
    for a,b in combinations(range(6),2):
        for g,h in product(range(3),repeat=2):
            ds=[d for d,column in enumerate(columns)if (column['cells'][a],column['cells'][b])==(g,h)]
            t=1 if g==h else 2;assert len(ds)==4*t
            xv=[columns[d]['bit_variables'][a]for d in ds];yv=[columns[d]['bit_variables'][b]for d in ds];zv=[lookup[d,a,b]for d in ds]
            start=len(clauses)
            for vs,k in [(xv,2*t),(yv,2*t),(zv,t)]:clauses.extend(exact(vs,k))
            assert len(clauses)-start==(23 if t==1 else 288)
            constraints.append(dict(components=[a,b],cells=[g,h],columns=ds,first_bits=xv,second_bits=yv,AND_variables=zv,bit_sum=2*t,AND_sum=t,all_four_joint_counts=t))
    assert variables==1260 and len(clauses)==29655 and len(products)==900 and len(constraints)==135
    return dict(schema='SIX_PRISM_FIVE_MATCHING_UNPAIRED_BIT_DESIGN_V1',matchings=matchings,patterns=patterns,columns=columns,
                AND_products=products,constraints=constraints,variables=variables,primary_bits=360,clauses=clauses,
                global_complement_pairing_required=False,fixed_bit_normalization=False,full_target_graph=False)

def decode(model,assignment):
    values={abs(v):int(v>0)for v in assignment};assert len(values)==1260 and accepts(model['clauses'],values)
    f=[[0]*60 for _ in range(36)]
    for d,column in enumerate(model['columns']):
        for a in range(6):f[12*column['cells'][a]+2*a+values[column['bit_variables'][a]]][d]=1
    c=[[0]*36 for _ in range(36)]
    for g in range(3):
        for i in range(12):c[12*g+i][12*g+(i^1)]=1
    for g,h in combinations(range(3),2):
        for i in range(12):c[12*g+i][12*h+i]=c[12*h+i][12*g+i]=1
    target=[[12*int(i==j)-c[i][j]-sum(c[i][t]*c[t][j]for t in range(36))+2-int(i//12==j//12)for j in range(36)]for i in range(36)]
    gram=[[sum(x*y for x,y in zip(r,s))for s in f]for r in f]
    assert gram==target and all(sum(r)==10 for r in f)
    assert all(sum(f[12*g+i][d]for i in range(12))==2 for g in range(3)for d in range(60))
    labels=[tuple(i for i in range(12)if f[i][d])for d in range(60)]
    expected=[e for e in combinations(range(12),2)if e[1]!=(e[0]^1)]
    assert sorted(labels)==expected
    order=sorted(range(60),key=lambda d:labels[d]);canonical=[[r[d]for d in order]for r in f]
    return dict(status='CANDIDATE_UNPAIRED_SIX_PRISM_36X60_FACTOR',incidence_matrix=canonical,original_column_incidence=f,canonical_column_order=order,
                core36_adjacency=c,target_gram=target,producer_integer_checks=dict(Gram_entries=1296,row_margins=36,fibre_column_margins=180,canonical_C0_bijection=True,all_pass=True),
                independent_approval=False,full99_graph=False,residual_D=None,residual_D_null_reason='Not encoded or searched. Independent factor check required before continuation.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--research',action='store_true');args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        assert native.digest(native.NATIVE)==native.NATIVE_SHA
        native.checked_gate(GATE,GATE_SHA,'INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS')
        native.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),
            inputs_sha256={native.key(p):native.digest(p)for p in [Path(__file__),SPEC,Path(native.__file__),native.NATIVE,GATE,ROOT/'uv.lock',ROOT/'pyproject.toml']},
            scope='Fixed six-prism core; fixed5round-robin matching cellpatterns repeated twice, with360independent bit choices. No complementpairing or targetautomorphism assumption.',
            predictions=dict(primary_bits=360,AND_variables=900,total_variables=1260,clauses=29655),numerical_settings='Exact Boolean/integer, no tolerance.',
            random_seed=None,random_seed_null_reason='Native default retained.',limits=dict(seconds=5,conflicts=100000,address_space_bytes=268435456,trace_bytes=134217728,kill_after_seconds=2,outer_guard_seconds=15),
            status='CANDIDATE',independent_verification=False))
        native.save(out/'controls.json',controls());model=build();native.save(out/'model.json',model)
        cnf=out/'instance.cnf'
        with cnf.open('x',encoding='ascii',newline='\n')as stream:
            stream.write('p cnf 1260 29655\n')
            for c in model['clauses']:stream.write(' '.join(map(str,c))+' 0\n')
        native.save(out/'preflight.json',dict(status='PRODUCER_EXACT_GEOMETRY_AND_CONTROLS_PASS',variables=1260,clauses=29655,primary_bits=360,AND_variables=900,scope_deviations=[],independent_approval=False,
                    cnf_sha256=native.digest(cnf),model_sha256=native.digest(out/'model.json'),controls_sha256=native.digest(out/'controls.json')))
        result=dict(status='CONSTRUCTION_INPUT_ONLY',variables=1260,clauses=29655,research_calls=0,independent_approval=False,target_resolution=False)
        if args.research:
            command=[*native.WSL,'/usr/bin/timeout','--signal=TERM','--kill-after=2s','5s','/usr/bin/prlimit','--as=268435456:268435456','--fsize=134217728:134217728','--core=0:0',native.linux(native.NATIVE),'--no-binary','-c','100000',native.linux(cnf),native.linux(out/'proof.drat')]
            native.save(out/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=native.digest(cnf),preflight_sha256=native.digest(out/'preflight.json')))
            print(json.dumps(dict(status='LAUNCHING_SINGLE_CAPPED_PILOT',variables=1260,clauses=29655)),flush=True)
            receipt=native.run_record(command,out/'solver',15);result.update(research_calls=1,receipt=receipt)
            code=receipt['actual_exit_code'];result['status']='SAT_CANDIDATE_PENDING_INDEPENDENT_CHECK'if code==10 else'UNSAT_RESTRICTED_DESIGN_UNCHECKED'if code==20 else'UNKNOWN'
            if code==10:
                assignment=native.parse_sat_stdout((out/'solver.stdout.log').read_text(),1260)
                native.save(out/'assignment.json',dict(assignment=assignment));native.save(out/'factor.json',decode(model,assignment))
        result['scope']='Only fixed5matching cellpatterns with independent column bits; no allfactor/core/target coverage.'
        result['elapsed_seconds']=time.monotonic()-start
        result['outputs_sha256']={native.key(p):native.digest(p)for p in out.iterdir()if p.is_file()}
        native.save(out/'summary.json',result)
        print(json.dumps(dict(status=result['status'],variables=1260,clauses=29655,research_calls=result['research_calls'],summary_sha256=native.digest(out/'summary.json'))))
    except BaseException as e:
        native.save(out/'failure.json',dict(status='PRODUCER_FAILED',timestamp=datetime.now(timezone.utc).isoformat(),error=repr(e),elapsed_seconds=time.monotonic()-start,not_an_exclusion=True));raise

if __name__=='__main__':main()
