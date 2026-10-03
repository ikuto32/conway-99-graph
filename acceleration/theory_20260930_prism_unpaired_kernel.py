"""Candidate exact marginal kernels and restricted-design parity obstruction."""
from fractions import Fraction
from itertools import combinations, permutations, product
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
import argparse
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
SPEC=Path(__file__).with_name('theory_20260930_prism_unpaired_kernel_spec.md')
DOC=ROOT/'docs/DERIVATION_20260930_PRISM_UNPAIRED_KERNEL.md'
MODEL=ROOT/'acceleration/results/20260930_prism_unpaired_design_pilot/model.json'
MODEL_SHA='24beb62eecb4eee61501b597734d91be6325958d002af6ad1e3ab16f1e287974'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def pairs(a):return [[[v.numerator,v.denominator]for v in row]for row in a]
def rref(raw):
    m=len(raw);n=len(raw[0]);a=[[Fraction(v)for v in row]for row in raw]
    transform=[[Fraction(i==j)for j in range(m)]for i in range(m)];ops=[];pivots=[];r=0
    for c in range(n):
        chosen=next((i for i in range(r,m)if a[i][c]),None)
        if chosen is None:continue
        if chosen!=r:
            a[chosen],a[r]=a[r],a[chosen];transform[chosen],transform[r]=transform[r],transform[chosen]
            ops.append(dict(operation='swap',rows=[r,chosen]))
        scale=1/a[r][c]
        if scale!=1:
            a[r]=[scale*x for x in a[r]];transform[r]=[scale*x for x in transform[r]]
            ops.append(dict(operation='scale',row=r,multiplier=[scale.numerator,scale.denominator]))
        for i in range(m):
            if i==r or not a[i][c]:continue
            multiple=-a[i][c];a[i]=[x+multiple*y for x,y in zip(a[i],a[r])];transform[i]=[x+multiple*y for x,y in zip(transform[i],transform[r])]
            ops.append(dict(operation='add_multiple',source=r,target=i,multiplier=[multiple.numerator,multiple.denominator]))
        pivots.append(c);r+=1
        if r==m:break
    basis=[]
    for free in range(n):
        if free in pivots:continue
        v=[Fraction(0)]*n;v[free]=1
        for i,p in enumerate(pivots):v[p]=-a[i][free]
        basis.append(v)
    need(all(sum(transform[i][t]*raw[t][j]for t in range(m))==a[i][j]for i in range(m)for j in range(n)),'row transformation exact identity')
    need(all(all(sum(row[j]*v[j]for j in range(n))==0 for row in raw)for v in basis),'all exact raw kernel products')
    return dict(rank=r,pivots=pivots,reduced=pairs(a),row_transformation=pairs(transform),row_operations=ops,nullbasis=pairs(basis))

def replay(raw,certificate):
    a=[[Fraction(x)for x in row]for row in raw];m=len(a)
    for op in certificate['row_operations']:
        kind=op['operation']
        if kind=='swap':
            i,j=op['rows'];need(0<=i<m and 0<=j<m and i!=j,'valid swap indices');a[i],a[j]=a[j],a[i]
        elif kind=='scale':
            i=op['row'];v=Fraction(*op['multiplier']);need(0<=i<m and v,'nonzero scale');a[i]=[v*x for x in a[i]]
        elif kind=='add_multiple':
            i,j=op['source'],op['target'];v=Fraction(*op['multiplier']);need(0<=i<m and 0<=j<m and i!=j,'valid addition indices');a[j]=[x+v*y for x,y in zip(a[j],a[i])]
        else:raise ValueError('unknown row operation')
    need(pairs(a)==certificate['reduced'],'all replayed reduced entries')
    pivots=[]
    for i,row in enumerate(a):
        nz=[j for j,x in enumerate(row)if x]
        if not nz:
            need(all(not any(r)for r in a[i:]),'trailing zero rows');break
        j=nz[0];need(row[j]==1 and all(not a[t][j]for t in range(m)if t!=i),'RREF pivot')
        need(not pivots or pivots[-1]<j,'ordered pivots');pivots.append(j)
    need(pivots==certificate['pivots']and len(pivots)==certificate['rank'],'exact pivot rank')
    for rawv in certificate['nullbasis']:
        v=[Fraction(*x)for x in rawv];need(all(sum(x*y for x,y in zip(row,v))==0 for row in raw),'nullvector raw membership')
    return True

def controls():
    cases=[([[1,0,0],[0,1,0],[0,0,1]],3),([[0,0,0],[0,0,0]],0),([[1,2,3,4],[2,4,6,8],[0,1,1,0]],2)]
    outputs=[]
    for a,rank in cases:
        cert=rref(a);need(cert['rank']==rank and len(cert['nullbasis'])==len(a[0])-rank,'known control rank/nullity');replay(a,cert);outputs.append(dict(raw=a,certificate=cert))
    from copy import deepcopy
    raw=cases[-1][0];cert=outputs[-1]['certificate'];bad=deepcopy(cert);bad['reduced'][0][0][0]+=1
    badnull=deepcopy(cert);badnull['nullbasis'][0][0][0]+=1
    badop=deepcopy(cert);badop['row_operations'].append(dict(operation='swap',rows=[0,len(raw)]))
    rejected=[]
    for name,c in [('changed_reduced_entry',bad),('changed_kernel_entry',badnull),('invalid_operation_index',badop)]:
        try:replay(raw,c)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupt control accepted '+name)
    even_counts=[]
    for a,b,c,d in product((0,1),repeat=4):
        columns=[(a,b),(a,b),(c,d),(c,d)]
        counts=[columns.count(pair)for pair in product((0,1),repeat=2)]
        need(all(x%2==0 for x in counts)and counts!=[1,1,1,1],'two identical patterns cannot have allfour counts1')
        even_counts.append(counts)
    for a,b,c in product((0,1),repeat=3):need(((a!=b)+(b!=c)+(c!=a))%2==0,'coordinate parity')
    return dict(known_rank_cases=outputs,corruptions_rejected=rejected,all16_identical_pattern_counts=even_counts,all8_triple_bit_parities_checked=True,independent_approval=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    need(h(MODEL)==MODEL_SHA,'frozen unpaired design input');model=json.loads(MODEL.read_bytes())
    inputs={p.relative_to(ROOT).as_posix():h(p)for p in [Path(__file__),SPEC,DOC,MODEL,ROOT/'uv.lock',ROOT/'pyproject.toml']}
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,
        question='All18 marginal matrices rank9 with full-support unit-magnitude nullvector?',scope='Frozen5round-robin matching cellpatterns only.',limits=dict(seconds=120),thresholds=None,thresholds_null_reason='Exact Fraction arithmetic.',random_seed=None,random_seed_null_reason='Deterministic elimination.',independent_approval=False))
    save(out/'controls.json',controls())
    patterns=[]
    for t in range(5):
        m=[[5,t],[(t+1)%5,(t-1)%5],[(t+2)%5,(t-2)%5]]
        for order in permutations(range(3)):
            cells=[None]*6
            for edge,g in zip(m,order):
                for a in edge:cells[a]=g
            patterns.append(dict(matching=t,cells=cells))
    need(patterns==model['patterns'],'exact same frozen30patterns')
    records=[];failed=[]
    for a in range(6):
        for g in range(3):
            need(time.monotonic()-start<120,'120second cap')
            selected=[t for t,p in enumerate(patterns)if p['cells'][a]==g];need(len(selected)==10,'ten selected patterns')
            labels=[(b,k)for b in range(6)if b!=a for k in range(3)]
            matrix=[[int(patterns[t]['cells'][b]==k)for t in selected]for b,k in labels]
            cert=rref(matrix);replay(matrix,cert)
            conjecture=cert['rank']==9 and len(cert['nullbasis'])==1 and all(abs(Fraction(*v))==1 for v in cert['nullbasis'][0])
            record=dict(component=a,cell=g,selected_pattern_indices=selected,row_labels=[list(p)for p in labels],matrix=matrix,certificate=cert,conjecture_holds=conjecture)
            save(out/f'component_{a}_cell_{g}.json',record);records.append(dict(component=a,cell=g,rank=cert['rank'],nullity=len(cert['nullbasis']),full_support_unit_generator=conjecture))
            if not conjecture:failed.append(record)
    # Check every same-cell pair population used by the human type argument.
    intersections=[]
    for g in range(3):
        for a,b in combinations(range(6),2):
            ids=[t for t,p in enumerate(patterns)if p['cells'][a]==p['cells'][b]==g]
            need(len(ids)==2,'same-cell components share exactly two repeated patterns')
            intersections.append(dict(components=[a,b],cell=g,patterns=ids))
    save(out/'same_cell_intersections.json',intersections)
    save(out/'summary.json',dict(status='CANDIDATE_UNPAIRED_FIVE_MATCHING_KERNEL_EXCLUSION'if not failed else'KERNEL_CONJECTURE_REFUTED',
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        proposed_claim_id='C-SIX-PRISM-FIVE-MATCHING-UNPAIRED-DESIGN-EXCLUSION',proposed_claim_revision=1,
        statement='No binary36x60 prescribed-Gram incidence factor for the standard-matchings/identity-cross-matching six-prism core can use exactly the30five-round-robin matching cellpatterns each repeated twice, even when all360column bits are independent.',
        basis=['DERIVED','COMPUTED'],kind='exclusion',independent_approval=False,matrices=18,records=records,failed_conjecture_systems=len(failed),
        proof_chain='Exact rank9/full-support signed kernel forces each(component,cell) to be all-complementary or all-identical across repeated columns. Same-cell bitpair counts1 allow at most one identical component per cell. At least three components are complementary in every cell. Required pairwise representative Hamming distances15 contradict triple parity.',
        scope='Only the exact5matching cell-pattern family; not all six-prism factors or target graphs.',
        assumptions=['Exact frozen cellpattern population and repetitions.','Prescribed Gram and row/column margins for the fixed core.','No nontrivial target automorphism or universal occurrence assumption.'],
        limitations=['Producer-only candidate; all18 raw matrices/certificates and the written proof require independent verification.','No solver was launched or retried.','Earlier UNKNOWN run is preserved and is not exclusion evidence.','No all-factor/core/target exclusion.'],
        inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()},elapsed_seconds=time.monotonic()-start))
    print(json.dumps(dict(status='CANDIDATE_KERNEL_EXCLUSION'if not failed else'CONJECTURE_REFUTED',ranks=[r['rank']for r in records],summary_sha256=h(out/'summary.json'))))

if __name__=='__main__':main()
