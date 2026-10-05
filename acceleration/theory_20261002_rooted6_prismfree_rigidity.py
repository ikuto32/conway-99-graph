"""Discovery: first variable two-root flag layer and conditional prism-free face.

Build exact necessary rows through rooted order6; modular rank is exact.
If full column rank and an exact checked integer primal exist, the unique
local flag vector is an exact candidate. Separate review is still required.
"""
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from tqdm import tqdm

from theory_20261002_rooted5_flag_rigidity import ROOT,graph,encode,admissible,canon,marks,sha,save


def build(n,k,adjacent):
    classes={h:sorted({canon(h,mask)[0] for mask in range(1<<math.comb(h,2))
                      if bool(mask&1)==adjacent and admissible(h,mask)}) for h in range(2,7)}
    variables=[(h,m) for h in range(2,7) for m in classes[h]];index={key:i for i,key in enumerate(variables)}
    equations=[]
    for h in range(2,7):
        equations.append(dict(kind='total',order=h,mask=None,mark=None,
                              terms=[[index[h,m],1] for m in classes[h]],rhs=math.comb(n-2,h-2)))
    for h in range(2,6):
        descriptors={};accum={}
        for mask in classes[h]:
            adj=graph(h,mask);des=[('deletion',None,n-h)]
            for orbit in marks(h,mask):
                if len(orbit[0])==1:
                    des.append(('degree',orbit,sum(k-len(adj[u[0]]) for u in orbit)))
                else:
                    des.append(('common_neighbor',orbit,sum((1 if v in adj[u] else 2)-len(adj[u]&adj[v]) for u,v in orbit)))
            descriptors[mask]=des;accum[mask]=[Counter() for _ in des]
        for bigger in classes[h+1]:
            big=graph(h+1,bigger)
            for removed in range(2,h+1):
                original=[0,1]+[u for u in range(2,h+1) if u!=removed]
                sub=encode(big,original);key,order=canon(h,sub)
                neighbor={j for j,u in enumerate(order) if original[u] in big[removed]}
                for i,(kind,orbit,_) in enumerate(descriptors[key]):
                    value=1 if kind=='deletion' else sum(set(mark)<=neighbor for mark in orbit)
                    if value:
                        accum[key][i][index[h+1,bigger]]+=value
        for mask in classes[h]:
            for i,(kind,orbit,left) in enumerate(descriptors[mask]):
                if left:
                    accum[mask][i][index[h,mask]]-=left
                equations.append(dict(kind=kind,order=h,mask=mask,mark=orbit,rhs=0,
                                      terms=[[j,a] for j,a in sorted(accum[mask][i].items()) if a]))
    return dict(format='ROOTED6_MARKED_EXTENSIONS_V1',n=n,k=k,lambda_=1,mu=2,
                adjacent_roots=adjacent,variables=[list(v) for v in variables],equations=equations,
                scope='Per actual ordered root; complete simple flagged masks throughorder6; no target automorphism.')


def is_prism(mask):
    adj=graph(6,mask)
    for first in combinations(range(6),3):
        second=set(range(6))-set(first)
        if not all(v in adj[u] for u,v in combinations(first,2)) or not all(v in adj[u] for u,v in combinations(second,2)):
            continue
        if all(len(adj[u]&second)==1 for u in first) and all(len(adj[u]&set(first))==1 for u in second):
            return True
    return False


def exact_modular_rank(rows,columns,prime=65521):
    assert prime==65521
    work=np.zeros((len(rows),columns),dtype=np.int64)
    for i,row in enumerate(rows):
        for j,a in row['terms']:
            work[i,j]=a%prime
    at=0;pivots=[]
    for col in range(columns):
        candidates=np.flatnonzero(work[at:,col])
        if not len(candidates):
            continue
        selected=at+int(candidates[0]);work[[at,selected]]=work[[selected,at]]
        inverse=pow(int(work[at,col]),-1,prime)
        work[at]=(work[at]*inverse)%prime
        if at+1<len(rows):
            # Values/products stay below prime^2<2^33, safely inside signed64.
            work[at+1:]=(work[at+1:]-work[at+1:,col,None]*work[at])%prime
        pivots.append(col);at+=1
    return dict(prime=prime,rank=at,columns=columns,nullity=columns-at,pivots=pivots,
                arithmetic='Exact int64 modulo65521; every operand<=65520 and every product<2^33.',
                interpretation='Full modular column rank establishes rational fullcolumn rank; deficient modular rank alone is no rational upperbound.')


def numeric_primal_then_exact(data,rows):
    variables=data['variables'];scale=[math.comb(data['n']-2,h-2) for h,_ in variables]
    rr,cc,vv,bb=[],[],[],[]
    for i,row in enumerate(rows):
        normalizer=max([abs(a*scale[j]) for j,a in row['terms']]+[abs(row['rhs']),1])
        for j,a in row['terms']:
            rr.append(i);cc.append(j);vv.append(a*scale[j]/normalizer)
        bb.append(row['rhs']/normalizer)
    mat=coo_matrix((vv,(rr,cc)),shape=(len(rows),len(variables))).tocsr()
    result=linprog(np.zeros(len(variables)),A_eq=mat,b_eq=bb,bounds=(0,None),method='highs',
                   options=dict(time_limit=60,primal_feasibility_tolerance=1e-9,dual_feasibility_tolerance=1e-9))
    outcome=dict(scipy_status=int(result.status),message=result.message,exact_primal=None,
                 exact_primal_reason='No successful exact rounded vector yet; floating status is not proof.')
    if result.x is not None:
        counts=[float(x*scale[j]) for j,x in enumerate(result.x)]
        rounded=[int(round(x)) for x in counts]
        failed=sum(sum(a*rounded[j] for j,a in row['terms'])!=row['rhs'] for row in rows)
        outcome.update(max_rounding_adjustment=max(abs(a-b) for a,b in zip(counts,rounded)),failed_exact_rows=failed,
                       nonnegative=min(rounded)>=0,numerical_counts=counts)
        if failed==0 and min(rounded)>=0:
            outcome['exact_primal']=rounded;outcome['exact_primal_reason']='Every selected raw integer row checked exactly; independent checking pending.'
    return outcome


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),
                                     source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                                     command=[sys.executable,*sys.argv],cwd=str(ROOT),
                                     dependencies=[dict(path='acceleration/theory_20261002_rooted5_flag_rigidity.py',sha256=sha(ROOT/'acceleration/theory_20261002_rooted5_flag_rigidity.py'))],
                                     scope='Unrestricted rooted6 necessarymodel plus separately conditional prismfree rootface.',
                                     independent=False,verification='Separate implementation must check bases/rows, rankand exactprimal before promotion.',
                                     random_seed=None,random_seed_reason='Deterministic enumeration and elimination.'))
    # A small modular rank control and failure case test before model work.
    assert exact_modular_rank([dict(terms=[[0,1],[1,2]]),dict(terms=[[0,3],[1,4]])],2)['rank']==2
    assert exact_modular_rank([dict(terms=[[0,1],[1,2]]),dict(terms=[[0,2],[1,4]])],2)['rank']==1
    outcomes=[]
    for family,adjacent in [('ordered_edge',True),('ordered_nonedge',False)]:
        data=build(99,14,adjacent);save(args.out/f'{family}_model.json',data)
        base_rank=exact_modular_rank(data['equations'],len(data['variables']))
        prism_indices=[j for j,(h,mask) in enumerate(data['variables']) if h==6 and is_prism(mask)]
        added=[dict(kind='prismfree',order=6,mask=data['variables'][j][1],mark=None,terms=[[j,1]],rhs=0) for j in prism_indices]
        endpoint_rank=exact_modular_rank([*data['equations'],*added],len(data['variables']))
        save(args.out/f'{family}_prismfree_rows.json',added)
        save(args.out/f'{family}_rank.json',dict(unrestricted=base_rank,prismfree=endpoint_rank))
        primal=numeric_primal_then_exact(data,[*data['equations'],*added])
        save(args.out/f'{family}_prismfree_primal.json',primal)
        outcome=dict(family=family,variables=len(data['variables']),base_rows=len(data['equations']),
                     six_flag_count=sum(h==6 for h,_ in data['variables']),prism_flags=len(prism_indices),
                     base_modular_rank=base_rank['rank'],base_modular_nullity=base_rank['nullity'],
                     endpoint_modular_rank=endpoint_rank['rank'],endpoint_modular_nullity=endpoint_rank['nullity'],
                     exact_nonnegative_endpoint_primal=primal['exact_primal'] is not None,
                     status='CANDIDATE_EXACT_PRISMFREE_RIGIDITY' if endpoint_rank['rank']==len(data['variables']) and primal['exact_primal'] is not None else 'RIGIDITY_NOT_ESTABLISHED')
        outcomes.append(outcome);print(json.dumps(outcome),flush=True)
    save(args.out/'summary.json',dict(status='COMPLETED_INDEPENDENT_VERIFICATION_PENDING',outcomes=outcomes,
                                     elapsed_seconds=time.monotonic()-start,target_resolution='UNKNOWN',exact_new_bound=None,
                                     outputs=[dict(path=f.name,sha256=sha(f)) for f in sorted(args.out.iterdir()) if f.is_file()]))


if __name__=='__main__':
    main()
