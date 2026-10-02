"""Candidate global b/prism mean calibration, preserving prior a derivation.

Shares only the frozen discovery graph/triangle/canonical helpers. Separate
independent derivation and raw artifact checking are required for promotion.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline
import theory_20261002_almost_prism_global_mean_v1 as prior

ROOT=prior.ROOT
PROTOCOL=ROOT/'docs/DERIVATION_20261002_PRISM_GLOBAL_PARAMETER_MEANS.md'


def need(ok,message):
    if not ok:raise ValueError(message)


def dump(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def triangle_pair_census(A,Ts,deadline):
    census=Counter();pairs={};two=[];three=[];b=Counter()
    for i,left in enumerate(Ts):
        for j in range(i+1,len(Ts)):
            right=Ts[j]
            if set(left)&set(right):continue
            cross=[(u,v)for u in left for v in right if A[u][v]]
            need(len({u for u,v in cross})==len({v for u,v in cross})==len(cross),'cross edges are a matching')
            count=len(cross);census[count]+=1
            if count>=2:
                pairs[(i,j)]=count
                vertices=sorted([*left,*right])
                if count==3:three.append(vertices)
                else:
                    u=next(v for v in left if v not in {x for x,y in cross})
                    v=next(v for v in right if v not in {y for x,y in cross});root=tuple(sorted((u,v)))
                    b[root]+=1;two.append({'triangle_indices':[i,j],'vertices':vertices,'unordered_root':list(root)})
        if i%64==0:need(deadline.status()['remaining_seconds']>15,'not completed within allocated budget')
    return census,pairs,two,sorted(three),b


def cycle_extension_census(A,N,Ts,deadline):
    triangle_index={tuple(t):i for i,t in enumerate(Ts)};cycles={}
    for u,v in combinations(range(len(A)),2):
        if A[u][v]:continue
        common=list(prior.members(N[u]&N[v]));need(len(common)==2 and not A[common[0]][common[1]],'exact opposite pair of induced4cycle')
        cycles[tuple(sorted([u,v,*common]))]=(u,v,*common)
    choices=[];multiplicity=Counter()
    for i,(vertices,(u,v,q,r))in enumerate(sorted(cycles.items())):
        rows=[]
        for edge1,edge2 in [((u,q),(v,r)),((u,r),(v,q))]:
            thirds=[]
            for s,t in [edge1,edge2]:
                x=list(prior.members(N[s]&N[t]));need(len(x)==1 and x[0]not in vertices,'unique outside triangle third');thirds.append(x[0])
            need(thirds[0]!=thirds[1],'disjoint opposite-edge triangle extensions')
            first=tuple(sorted([*edge1,thirds[0]]));second=tuple(sorted([*edge2,thirds[1]]))
            pair=tuple(sorted((triangle_index[first],triangle_index[second])));multiplicity[pair]+=1;rows.append(list(pair))
        choices.append({'four_cycle_vertices':list(vertices),'opposite_edge_extension_triangle_pairs':rows})
        if i%1024==0:need(deadline.status()['remaining_seconds']>15,'not completed within allocated budget')
    need(len(cycles)==len(A)*(len(A)-sum(A[0])-1)//4,'exact4cycle parameter population')
    return choices,multiplicity


def shape(mask):
    A=[[0]*6 for _ in range(6)]
    for bit,(u,v)in enumerate(combinations(range(6),2)):
        if mask>>bit&1:A[u][v]=A[v][u]=1
    return A


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='891triangle pair census and26730 opposite pairs, small rook direct flags first; outer180worker165reserve15')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        need(prior.sha(prior.RAW)==prior.RAW_SHA,'frozen validated243 source')
        paths=[Path(__file__),Path(prior.__file__),PROTOCOL,prior.RAW,ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/results/20261002_almost_prism_global_mean01/summary.json',ROOT/'acceleration/results/20261002_almost_prism_global_mean01/243_prism_six_sets.json']
        dump(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),'inputs_sha256':{str(p.relative_to(ROOT)):prior.sha(p)for p in paths},
            'archive_repository':'YesterdaysLemon/conway-99-research','archive_commit':'85e705cc6c2a14d123120c93a847e30aaab1789e',
            'success':'Exact two trianglepair/fourcycle incidence populations; ordered-root b counts and raw shape/corrupt controls.',
            'scope':'CANDIDATE general double-count and calibrated fixtures; no novelty/target solution.','independent_requirement':'Alternate proof and source-free raw fixture checks required.'})
        for mask in [8024,15540]:
            A=shape(mask);need(prior.canonical6(A,list(range(6)))==mask and prior.canonical6(A,[1,0,2,3,4,5])==mask,'exact positive raw rootmask controls')
            need(not A[0][1],'both raw roots are nonadjacent');A[0][1]=A[1][0]=1;need(prior.is_prism(A,list(range(6))),'adding missingroot edge gives inducedprism')
        rawb=shape(15540);census,pairs,two,three,b=triangle_pair_census(rawb,prior.triangles(rawb),deadline)
        need(len(two)==1 and not three and b[(0,1)]==1,'positive two-cross rawshape control')
        rook=[[int(u!=v and(u//3==v//3 or u%3==v%3))for v in range(9)]for u in range(9)]
        N=prior.validate(rook,4);Ts=prior.triangles(rook)
        census,pairs,two,three,b=triangle_pair_census(rook,Ts,deadline);choices,multiple=cycle_extension_census(rook,N,Ts,deadline)
        need(set(multiple)==set(pairs) and all(multiple[p]==(1 if count==2 else 3)for p,count in pairs.items()),'rook full incidence bijection')
        checked=0
        for u,v in combinations(range(9),2):
            if rook[u][v]:continue
            subsets=list(combinations([x for x in range(9)if x not in [u,v]],4))
            for first,second in [(u,v),(v,u)]:
                actual=sum(prior.canonical6(rook,[first,second,*s])==15540 for s in subsets);checked+=len(subsets)
                need(actual==b[(u,v)],'every ordered rook b flag')
        need(checked==1260 and len(choices)==9 and len(three)==6 and not two,'frozen rook9 populations')
        need(2*sum(b.values())==9*4-6*len(three) and 2*(sum(b.values())+1)!=9*4-6*len(three),'rook identity/count corruption')
        dump(out/'controls.json',{'rook9_ordered_nonedge_b_subsets_checked':checked,'rook9_induced_four_cycles':choices,'rook9_prisms':three,
            'rook9_disjoint_triangle_pair_census':dict(census),'raw_rootmask_controls':[8024,15540],'positive_raw15540_two_cross_control':two if two else [{'raw_graph_mask':15540,'unordered_root':[0,1],'count':1}],
            'count_corruption_rejected':True})
        A=json.loads(prior.RAW.read_bytes())['adjacency'];N=prior.validate(A,22);Ts=prior.triangles(A)
        census,pairs,two,three,b=triangle_pair_census(A,Ts,deadline);choices,multiple=cycle_extension_census(A,N,Ts,deadline)
        need(set(multiple)==set(pairs)and all(multiple[p]==(1 if count==2 else 3)for p,count in pairs.items()),'complete243 opposite-edge incidence bijection')
        need(len(two)+3*len(three)==2*len(choices),'complete243 double-count identity')
        profiles=[[u,v,b[(u,v)]]for u,v in combinations(range(243),2)if not A[u][v]]
        need(sum(v for u,w,v in profiles)==len(two)and 2*len(two)==243*220-6*len(three),'complete243 ordered-root b identity')
        prior_prisms=json.loads((ROOT/'acceleration/results/20261002_almost_prism_global_mean01/243_prism_six_sets.json').read_bytes())
        need(three==prior_prisms,'all induced prism witnesses equal prior frozen trianglepair output')
        dump(out/'243_triangles.json',Ts);dump(out/'243_two_cross_triangle_pairs.json',two);dump(out/'243_prism_six_sets.json',three)
        dump(out/'243_unordered_nonedge_b_counts.json',profiles);dump(out/'243_fourcycle_extension_choices.json',choices)
        dump(out/'summary.json',{'status':'CANDIDATE_GLOBAL_ROOTED6_PARAMETER_MEANS_CALIBRATION','timestamp':datetime.now(timezone.utc).isoformat(),
            'triangle_sets':len(Ts),'disjoint_triangle_pairs_by_cross_matching_size':dict(census),'four_cycle_sets':len(choices),'four_cycle_opposite_edge_extension_choices':2*len(choices),
            'induced_prism_six_sets':len(three),'two_cross_triangle_pairs':len(two),'unordered_nonedge_population':len(profiles),'ordered_b_sum':2*len(two),
            'general_statement':'sum ordered-nonedge b = n*(n-k-1)-6*T; sum ordered-nonedge a=2*sum ordered-nonedge b',
            'conditional_target_prismfree_means':{'a':2,'b':1,'premise_status':'UNKNOWN'},'novelty_claimed':False,'independent_review':None,
            'elapsed_seconds':time.monotonic()-started,'outputs_sha256':{str(p.relative_to(ROOT)):prior.sha(p)for p in out.iterdir()if p.is_file()}})
    except BaseException as error:
        dump(out/'failure.json',{'error':repr(error),'elapsed_seconds':time.monotonic()-started,'partial_only':True,'automatic_resume':False});raise


if __name__=='__main__':main()
