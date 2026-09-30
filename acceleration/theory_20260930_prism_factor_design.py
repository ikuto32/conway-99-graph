"""Cheap restricted construction candidate for a six-prism incidence factor."""
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import native_20260930_unrestricted_full99 as native

ROOT=native.ROOT
SPEC=Path(__file__).with_name('theory_20260930_prism_factor_design_spec.md')


def xor_clauses(x,y,z):
    return [[x,y,-z],[-x,-y,-z],[x,-y,z],[-x,y,z]]


def exact_two(xs):
    return [list(s) for s in combinations(xs,3)]+[[-v for v in s] for s in combinations(xs,3)]


def accepts(clauses,values):
    return all(any(values[abs(l)]==(l>0) for l in c) for c in clauses)


def fixtures():
    for x,y,z in product([False,True],repeat=3):
        assert accepts(xor_clauses(1,2,3),{1:x,2:y,3:z})==(z==(x^y))
    for values in product([False,True],repeat=4):
        assert accepts(exact_two([1,2,3,4]),dict(enumerate(values,1)))==(sum(values)==2)
    return dict(xor_assignments=8,exact_two_assignments=16,independent_verification=False)


def build():
    matchings=[[[5,t],[(t+1)%5,(t-1)%5],[(t+2)%5,(t-2)%5]] for t in range(5)]
    assert sorted(tuple(sorted(p)) for m in matchings for p in m)==list(combinations(range(6),2))
    patterns=[];variables=0;clauses=[]
    for mi,m in enumerate(matchings):
        for order in permutations(range(3)):
            cells=[-1]*6
            for edge,cell in zip(m,order):
                for a in edge:cells[a]=cell
            bits=[0]
            for a in range(1,6):variables+=1;bits.append(variables)
            patterns.append(dict(matching=mi,cells=cells,bit_variables=bits))
    parities={}
    for t,p in enumerate(patterns):
        for a,b in combinations(range(6),2):
            if a==0:parities[t,a,b]=p['bit_variables'][b]
            else:
                variables+=1;parities[t,a,b]=variables
                clauses.extend(xor_clauses(p['bit_variables'][a],p['bit_variables'][b],variables))
    constraints=[]
    for a,b in combinations(range(6),2):
        for g in range(3):
            for k in range(3):
                indices=[t for t,p in enumerate(patterns) if p['cells'][a]==g and p['cells'][b]==k]
                vs=[parities[t,a,b] for t in indices]
                if g==k:
                    assert len(vs)==2;clauses.extend([vs,[-v for v in vs]])
                else:
                    assert len(vs)==4;clauses.extend(exact_two(vs))
                constraints.append(dict(components=[a,b],cells=[g,k],patterns=indices,parity_variables=vs,odd_count=len(vs)//2))
    assert variables==450 and len(clauses)==2010
    return dict(matchings=matchings,patterns=patterns,constraints=constraints,variables=variables,clauses=clauses)


def decode(model,assignment):
    values={abs(v):int(v>0) for v in assignment}
    assert accepts(model['clauses'],values)
    f=[[0]*60 for _ in range(36)]
    for t,p in enumerate(model['patterns']):
        for a in range(6):
            bit=values[p['bit_variables'][a]] if a else 0
            for complement in range(2):f[12*p['cells'][a]+2*a+(bit^complement)][2*t+complement]=1
    labels=[tuple(i for i in range(12) if f[i][y]) for y in range(60)]
    assert sorted(labels)==[p for p in combinations(range(12),2) if p[0]^1!=p[1]]
    order=sorted(range(60),key=lambda y:labels[y]);f=[[row[y] for y in order] for row in f]
    c=[[0]*36 for _ in range(36)]
    for g in range(3):
        for i in range(12):c[12*g+i][12*g+(i^1)]=1
    for g,k in combinations(range(3),2):
        for i in range(12):c[12*g+i][12*k+i]=c[12*k+i][12*g+i]=1
    gram=[[sum(f[i][y]*f[j][y] for y in range(60)) for j in range(36)] for i in range(36)]
    target=[[12*int(i==j)-c[i][j]-sum(c[i][x]*c[x][j] for x in range(36))+2-int(i//12==j//12) for j in range(36)] for i in range(36)]
    assert gram==target and all(sum(row)==10 for row in f)
    assert all(sum(f[i][y] for i in range(12*g,12*g+12))==2 for g in range(3) for y in range(60))
    return dict(status='CANDIDATE_SIX_PRISM_BINARY36X60_FACTOR',incidence_matrix=f,core36_adjacency=c,
        target_gram=target,canonical_column_order_from_design=order,
        producer_exact_check=dict(Gram_entries=1296,row_margins=36,fibre_column_margins=180,all_pass=True),
        independent_approval=False,full99_graph=False,residual_D=None,residual_D_null_reason='Not searched or encoded.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--research',action='store_true');args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    assert native.digest(native.NATIVE)==native.NATIVE_SHA
    gate=ROOT/'acceleration/results/20260930_native_cli_calibration/summary.json'
    native.checked_gate(gate,'f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS')
    native.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
        inputs_sha256={native.key(p):native.digest(p) for p in [Path(__file__),SPEC,Path(native.__file__),native.NATIVE,gate,ROOT/'uv.lock',ROOT/'pyproject.toml']},
        scope='One five-matching/complement-paired binary design for the six-prism core; no target coverage claim.',
        numerical_settings='All arithmetic integer/Boolean; no tolerances.',random_seed=None,random_seed_null_reason='Native default retained.',
        limits=dict(seconds=5,conflicts=100000,address_space_bytes=256*1024**2,trace_bytes=128*1024**2,kill_after_seconds=2,outer_guard_seconds=15)))
    native.save(out/'controls.json',fixtures());model=build();native.save(out/'model.json',model)
    cnf=out/'instance.cnf'
    with cnf.open('x',encoding='ascii',newline='\n') as f:
        f.write('p cnf 450 2010\n')
        for clause in model['clauses']:f.write(' '.join(map(str,clause))+' 0\n')
    result=dict(status='CONSTRUCTION_INPUT_ONLY',variables=450,clauses=2010,research_calls=0,independent_approval=False,target_resolution=False)
    if args.research:
        command=[*native.WSL,'/usr/bin/timeout','--signal=TERM','--kill-after=2s','5s','/usr/bin/prlimit',
            '--as=268435456:268435456','--fsize=134217728:134217728','--core=0:0',native.linux(native.NATIVE),'--no-binary','-c','100000',native.linux(cnf),native.linux(out/'proof.drat')]
        receipt=native.run_record(command,out/'solver',15);result.update(research_calls=1,receipt=receipt)
        code=receipt['actual_exit_code'];result['status']='SAT_CANDIDATE_PENDING_INDEPENDENT_CHECK' if code==10 else 'UNSAT_RESTRICTED_DESIGN_UNCHECKED' if code==20 else 'UNKNOWN'
        if code==10:
            assignment=native.parse_sat_stdout((out/'solver.stdout.log').read_text(),450)
            native.save(out/'assignment.json',dict(assignment=assignment));native.save(out/'factor.json',decode(model,assignment))
    result['outputs_sha256']={native.key(p):native.digest(p) for p in out.iterdir() if p.is_file()}
    native.save(out/'summary.json',result)
    print(json.dumps(dict(status=result['status'],variables=450,clauses=2010,research_calls=result['research_calls'])))


if __name__=='__main__':main()
