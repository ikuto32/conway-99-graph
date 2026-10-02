"""Exact discovery: do rooted degree/codegree extensions force all5-flags?

Finite rooted classes include every locally admissible graph through order5.
Only two roots are fixed; no graph automorphism assumption is made.
"""
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
from functools import lru_cache
from itertools import combinations,permutations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(obj,stream,indent=2);stream.write('\n')


def graph(n,mask):
    adjacency=[set() for _ in range(n)]
    for bit,(u,v) in enumerate(combinations(range(n),2)):
        if (mask>>bit)&1:
            adjacency[u].add(v);adjacency[v].add(u)
    return adjacency


def encode(adj,order):
    return sum(1<<i for i,(u,v) in enumerate(combinations(order,2)) if v in adj[u])


def admissible(n,mask):
    adj=graph(n,mask)
    return all(len(adj[u]&adj[v])<=(1 if v in adj[u] else 2) for u,v in combinations(range(n),2))


@lru_cache(None)
def canon(n,mask):
    adj=graph(n,mask)
    best=None;bestorder=None
    for free in permutations(range(2,n)):
        order=(0,1,*free);key=encode(adj,order)
        if best is None or key<best:
            best=key;bestorder=order
    return best,bestorder


def marks(n,mask):
    adj=graph(n,mask)
    autom=[(0,1,*free) for free in permutations(range(2,n)) if encode(adj,(0,1,*free))==mask]
    remaining={tuple([u]) for u in range(n)}|set(combinations(range(n),2));result=[]
    while remaining:
        seed=min(remaining,key=lambda x:(len(x),x))
        orbit=sorted({tuple(sorted(order[u] for u in seed)) for order in autom})
        remaining.difference_update(orbit);result.append(orbit)
    return result


def model(n,k,adjacent):
    classes={h:sorted({canon(h,mask)[0] for mask in range(1<<math.comb(h,2))
                      if bool(mask&1)==adjacent and admissible(h,mask)}) for h in range(2,6)}
    variables=[(h,m) for h in range(2,6) for m in classes[h]];index={key:i for i,key in enumerate(variables)}
    equations=[]
    for h in range(2,6):
        equations.append(dict(kind='total',order=h,mask=None,mark=None,
                              terms=[[index[h,m],1] for m in classes[h]],rhs=math.comb(n-2,h-2)))
    for h in range(2,5):
        for mask in classes[h]:
            adj=graph(h,mask);descriptors=[('deletion',None,n-h)]
            for orbit in marks(h,mask):
                if len(orbit[0])==1:
                    descriptors.append(('degree',orbit,sum(k-len(adj[u[0]]) for u in orbit)))
                else:
                    descriptors.append(('common_neighbor',orbit,sum((1 if v in adj[u] else 2)-len(adj[u]&adj[v]) for u,v in orbit)))
            accum=[Counter() for _ in descriptors]
            for bigger in classes[h+1]:
                big=graph(h+1,bigger)
                for removed in range(2,h+1):
                    original=[0,1]+[u for u in range(2,h+1) if u!=removed]
                    sub=encode(big,original);key,order=canon(h,sub)
                    if key!=mask:
                        continue
                    # New label j corresponds to original[order[j]].
                    neighbor={j for j,u in enumerate(order) if original[u] in big[removed]}
                    for i,(kind,orbit,_) in enumerate(descriptors):
                        contribution=1 if kind=='deletion' else sum(set(mark)<=neighbor for mark in orbit)
                        if contribution:
                            accum[i][index[h+1,bigger]]+=contribution
            for i,(kind,orbit,left) in enumerate(descriptors):
                if left:
                    accum[i][index[h,mask]]-=left
                equations.append(dict(kind=kind,order=h,mask=mask,mark=orbit,rhs=0,
                                      terms=[[j,a] for j,a in sorted(accum[i].items()) if a]))
    return dict(format='ROOTED5_MARKED_EXTENSIONS_V1',n=n,k=k,lambda_=1,mu=2,
                adjacent_roots=adjacent,variables=[list(v) for v in variables],equations=equations,
                scope='Per actual ordered root, count free unordered subsets; root labels0,1 fixed pointwise.')


def eliminate(data):
    size=len(data['variables']);work=[]
    for row in data['equations']:
        full=[Fraction(0)]*(size+1)
        for j,a in row['terms']:
            full[j]=Fraction(a)
        full[-1]=Fraction(row['rhs']);work.append(full)
    pivotrows=[];at=0
    for column in range(size):
        selected=next((i for i in range(at,len(work)) if work[i][column]),None)
        if selected is None:
            continue
        work[at],work[selected]=work[selected],work[at]
        divisor=work[at][column]
        work[at]=[x/divisor for x in work[at]]
        for i in range(len(work)):
            if i==at or not work[i][column]:
                continue
            multiplier=work[i][column]
            work[i]=[a-multiplier*b for a,b in zip(work[i],work[at])]
        pivotrows.append((column,at));at+=1
    consistent=not any(not any(row[:-1]) and row[-1] for row in work)
    solution=None
    if consistent and len(pivotrows)==size:
        solution=[None]*size
        for column,row in pivotrows:
            solution[column]=[work[row][-1].numerator,work[row][-1].denominator]
    return dict(rank=len(pivotrows),variables=size,nullity=size-len(pivotrows),consistent=consistent,
                unique_solution=solution,status='CANDIDATE_EXACT_RIGIDITY' if solution is not None else 'NOT_UNIQUE_OR_INCONSISTENT',
                rref_rows=[[[x.numerator,x.denominator] for x in row] for row in work if any(row)],independent=False)


def rook_counts(variables,root):
    vertices=[(i,j) for i in range(3) for j in range(3)]
    adj=[{j for j,v in enumerate(vertices) if u!=v and (u[0]==v[0] or u[1]==v[1])} for u in vertices]
    counts=Counter();remaining=set(range(9))-set(root)
    for h in range(2,6):
        for free in combinations(sorted(remaining),h-2):
            counts[h,canon(h,encode(adj,(*root,*free)))[0]]+=1
    return [counts[tuple(key)] for key in variables]


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),
                                     source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                                     command=[sys.executable,*sys.argv],cwd=str(ROOT),
                                     basis='New complete rooted simple masks through5 filtered by local lambda1/mu2 caps.',
                                     input_artifacts=None,input_artifacts_reason='Complete bases built directly; no inherited discovery source/data.',
                                     numerical_settings=None,numerical_settings_reason='Exact Python integers/Fraction throughout.',
                                     verification='Separate implementation must reconstruct bases/rows and exactrank/solution; discovery cannot selfapprove.'))
    summary=[]
    for family,adjacent,root in [('ordered_edge',True,(0,1)),('ordered_nonedge',False,(0,4))]:
        control=model(9,4,adjacent);actual=rook_counts(control['variables'],root)
        assert all(sum(a*actual[j] for j,a in row['terms'])==row['rhs'] for row in control['equations'])
        damaged=actual[:];damaged[0]+=1
        assert any(sum(a*damaged[j] for j,a in row['terms'])!=row['rhs'] for row in control['equations'])
        data=model(99,14,adjacent);result=eliminate(data)
        save(args.out/f'{family}_model.json',data);save(args.out/f'{family}_rref.json',result)
        if result['unique_solution'] is not None:
            exact=[Fraction(*x) for x in result['unique_solution']]
            assert all(sum(a*exact[j] for j,a in row['terms'])==row['rhs'] for row in data['equations'])
            flagcounts=[(mask,result['unique_solution'][j]) for j,(h,mask) in enumerate(data['variables']) if h==5]
            save(args.out/f'{family}_forced5flags.json',dict(flag_counts=flagcounts,scope='Necessary per ordered actualroot; exact model rigidity is pending independent verification.'))
        outcome=dict(family=family,variables=len(data['variables']),equations=len(data['equations']),rank=result['rank'],nullity=result['nullity'],
                     consistent=result['consistent'],status=result['status'],rook_positive_control='PASS',corrupt_count_control='REJECTED')
        summary.append(outcome);print(json.dumps(outcome),flush=True)
    save(args.out/'summary.json',dict(status='COMPLETED_INDEPENDENT_VERIFICATION_PENDING',outcomes=summary,
                                     target_resolution='UNKNOWN',elapsed_seconds=time.monotonic()-start,
                                     outputs=[dict(path=f.name,sha256=sha(f)) for f in sorted(args.out.iterdir()) if f.is_file()]))


if __name__=='__main__':
    main()
