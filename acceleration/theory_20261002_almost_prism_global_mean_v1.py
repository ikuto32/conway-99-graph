"""Calibrate candidate global rooted8024/prism double count on rook9 and243.

No target search, no automorphism assumption, no choose243,6 enumeration.
The proof and producer fixture checks require a separate independent review.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
from itertools import combinations,permutations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'acceleration/results/20260930_srg243_residual_fixture/adjacency243.json'
RAW_SHA='5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3'
PROTOCOL=ROOT/'docs/DERIVATION_20261002_ALMOST_PRISM_GLOBAL_MEAN.md'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def members(bits):
    while bits:
        first=bits&-bits;yield first.bit_length()-1;bits-=first


def validate(A,k):
    n=len(A);need(n-k-1>0 and all(len(row)==n for row in A),'square noncomplete fixture')
    need(all(value in (0,1) for row in A for value in row),'binary fixture')
    need(all(A[u][u]==0 and sum(A[u])==k and all(A[u][v]==A[v][u] for v in range(n)) for u in range(n)),'diagonal/symmetry/degree')
    N=[sum(1<<v for v in range(n) if A[u][v]) for u in range(n)]
    need(all((N[u]&N[v]).bit_count()==(1 if A[u][v] else 2) for u,v in combinations(range(n),2)),'exact lambda1/mu2')
    return N


def triangles(A):
    return [list(triple) for triple in combinations(range(len(A)),3) if all(A[u][v] for u,v in combinations(triple,2))]


def is_prism(A,vertices):
    if not all(sum(A[u][v] for v in vertices if u!=v)==3 for u in vertices):return False
    for triple in combinations(vertices,3):
        other=[v for v in vertices if v not in triple]
        if all(A[u][v] for side in [triple,other] for u,v in combinations(side,2)):return True
    return False


def prism_pairs(A,triangles_list,deadline):
    witnesses=[];seen=set()
    for i,first in enumerate(tqdm(triangles_list,desc='disjoint triangle-pair prism count',mininterval=5)):
        first_set=set(first)
        for second in triangles_list[i+1:]:
            if first_set.intersection(second):continue
            cross=[(u,v) for u in first for v in second if A[u][v]]
            if len(cross)==3 and len({u for u,_ in cross})==len({v for _,v in cross})==3:
                vertices=tuple(sorted([*first,*second]));need(vertices not in seen,'each induced prism has unique two-triangle partition')
                seen.add(vertices);witnesses.append(list(vertices))
        if not i%64:need(deadline.status()['remaining_seconds']>15,'not completed within allocated budget')
    return sorted(witnesses)


def canonical6(A,order):
    best=None
    for free in permutations(order[2:]):
        current=[*order[:2],*free];mask=sum(1<<i for i,(u,v) in enumerate(combinations(range(6),2)) if A[current[u]][current[v]])
        best=mask if best is None else min(best,mask)
    return best


def almost_counts(A,N,k,deadline):
    records=[];total=0
    for u in tqdm(range(len(A)),desc='all nonedge/common-root almost-prisms',mininterval=5):
        for v in range(u+1,len(A)):
            if A[u][v]:continue
            common=list(members(N[u]&N[v]));need(len(common)==2,'both common roots')
            count=0
            for w in common:
                partner_u=list(members(N[u]&N[w]));partner_v=list(members(N[v]&N[w]))
                need(len(partner_u)==len(partner_v)==1,'local matching partners')
                forbidden=(1<<u)|(1<<v)|(1<<partner_u[0])|(1<<partner_v[0])
                allowed=N[w]&~forbidden;need(allowed.bit_count()==k-4,'exact allowed local neighbors')
                for p in members(allowed):
                    q=list(members((N[u]&N[p])&~(1<<w)));r=list(members((N[v]&N[p])&~(1<<w)))
                    need(len(q)==len(r)==1 and q[0]!=r[0],'unique distinct other common neighbors')
                    if A[q[0]][r[0]]:count+=1
            records.append([u,v,count]);total+=count
        need(deadline.status()['remaining_seconds']>15,'not completed within allocated budget')
    return records,total


def local_matching_count(A,N,k):
    paired=nonpaired=0
    for w in range(len(A)):
        for p in members(N[w]):
            outside=N[p]&~(N[w]|(1<<w));need(outside.bit_count()==k-2,'outside neighborhood size')
            local_edges=[(x,y) for x,y in combinations(members(outside),2) if A[x][y]]
            need(len(local_edges)==(k-2)//2 and len({v for edge in local_edges for v in edge})==k-2,'outside local perfect matching')
            for x,y in local_edges:
                u=list(members((N[x]&N[w])&~(1<<p)));v=list(members((N[y]&N[w])&~(1<<p)))
                need(len(u)==len(v)==1 and u[0]!=v[0],'outside label transport')
                if A[u[0]][v[0]]:paired+=1
                else:nonpaired+=1
    return paired,nonpaired


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--seconds',type=float,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Rook9 exhaustive84sixsets/1260rooted flags before243trianglepairs/local embeddings;15seconds checkpoint reserve')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(sha(RAW)==RAW_SHA,'frozen243 graph')
        paths=[RAW,PROTOCOL,Path(__file__),ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'.gitmodules',ROOT/'external_conway99_research/README.md']
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python_version=platform.python_version(),inputs_sha256={str(path.relative_to(ROOT)):sha(path) for path in paths},
            archive_commit=subprocess.check_output(['git','-C','external_conway99_research','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            scope='Candidate general lambda1/mu2 double count calibration, no target search and no novelty claim.',
            success_criteria='Exact SRG fixture checks, independent small exhaustive prism/rootflag counts, exact two local/global population identities and corruption rejection.',
            independent_review_requirement='Alternate derivation and independent raw fixture checking required before promotion.'))
        rook=[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)];N=validate(rook,4)
        save(out/'rook9_adjacency.json',dict(parameters=[9,4,1,2],adjacency=rook))
        small_prisms=prism_pairs(rook,triangles(rook),deadline)
        exhaustive=[list(vertices) for vertices in combinations(range(9),6) if is_prism(rook,vertices)]
        need(small_prisms==exhaustive and len(exhaustive)==6,'all84 independent six-subset rook prisms')
        small_a,total=almost_counts(rook,N,4,deadline)
        rooted_subsets_checked=0
        for u,v,value in small_a:
            for first,second in [(u,v),(v,u)]:
                subsets=list(combinations([x for x in range(9) if x not in [u,v]],4))
                direct=sum(canonical6(rook,[first,second,*subset])==8024 for subset in subsets)
                rooted_subsets_checked+=len(subsets)
                need(direct==value,'every ordered-root six-subset flag')
        need(rooted_subsets_checked==1260,'exact ordered-root subset population')
        rawflag=[[0]*6 for _ in range(6)]
        for bit,(u,v) in enumerate(combinations(range(6),2)):
            if 8024>>bit&1:rawflag[u][v]=rawflag[v][u]=1
        need(canonical6(rawflag,list(range(6)))==8024 and canonical6(rawflag,[1,0,2,3,4,5])==8024,'ordered-root swap statistic identity')
        damaged=[list(row) for row in rook];damaged[0][1]^=1
        try:validate(damaged,4)
        except ValueError:pass
        else:raise ValueError('corrupted graph accepted')
        need(2*total==9*4*2-12*len(small_prisms),'rook exact identity')
        need(2*(total+1)!=9*4*2-12*len(small_prisms) and 2*total!=9*4*2-12*(len(small_prisms)+1),'changed counts rejected')
        save(out/'controls.json',dict(rook9_six_subsets_exhausted=84,rook9_ordered_nonedge_flag_subsets_checked=rooted_subsets_checked,
            rook9_prisms=small_prisms,rook9_nonedge_a_counts=small_a,root_mask_swap_pass=True,adjacency_corruption_rejected=True,count_corruptions_rejected=True))
        graph=json.loads(RAW.read_bytes())['adjacency'];N=validate(graph,22)
        Ts=triangles(graph);need(len(Ts)==243*22//6,'exact fixture triangle population');save(out/'243_triangles.json',Ts)
        prisms=prism_pairs(graph,Ts,deadline);save(out/'243_prism_six_sets.json',prisms)
        profiles,unordered_a=almost_counts(graph,N,22,deadline);save(out/'243_unordered_nonedge_a_counts.json',profiles)
        paired,nonpaired=local_matching_count(graph,N,22)
        need(paired==6*len(prisms) and nonpaired==unordered_a and paired+nonpaired==243*22*20//2,'exact separate local matching partition')
        need(2*unordered_a==243*22*20-12*len(prisms),'exact243 ordered-count identity')
        save(out/'summary.json',dict(status='CANDIDATE_ALMOST_PRISM_GLOBAL_COUPLING_CALIBRATION',timestamp=datetime.now(timezone.utc).isoformat(),
            fixture_parameters=[243,22,1,2],triangle_sets=len(Ts),induced_prism_six_sets=len(prisms),unordered_nonedge_population=len(profiles),
            ordered_a_count=2*unordered_a,local_paired_matchings=paired,local_nonpaired_matchings=nonpaired,
            general_statement='sum ordered-nonedge rooted8024 counts = n*k*(k-2)-12*induced_prism_sixset_count',
            target_prismfree_consequence='Ordered-nonedge a mean2, conditional premise UNKNOWN.',
            novelty_claimed=False,independent_review=None,elapsed_seconds=time.monotonic()-start,
            outputs_sha256={str(path.relative_to(ROOT)):sha(path) for path in out.iterdir() if path.is_file()}))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-start,partial_only=True,automatic_resume=False));raise


if __name__=='__main__':main()
