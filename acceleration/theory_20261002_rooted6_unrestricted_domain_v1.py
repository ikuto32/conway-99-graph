"""Candidate exact unrestricted rooted6 nonedge 3D integer domain.

Reuses independently checked raw operator/nullspace as pinned data only.
Enumerates all rational vertices of the bounded nonnegative count polytope,
then every integer point in its exact bounding box if the declared cap permits.
This is a necessary local count domain, not graph feasibility or an exclusion.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations, permutations, product
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'acceleration/results'
INPUTS={
 '20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json':'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',
 '20261002_rooted6_exact_parameter_domain/unrestricted_nonedge_nullspace.json':'5f3c4b485522156cccc458411d4b2f4517a320905418dc753c9896a5e0dbf384',
 '20261002_rooted6_exact_parameter_domain/prismfree_nonedge_domain.json':'54f08f8dc87bebf61bada59067cbc721497f3d3a9683936e850b695f0ec41b12',
 '20261002_independent_review/rooted6_nonedge_domain01/summary.json':'65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271'}
PROTOCOL=ROOT/'docs/DESIGN_20261002_UNRESTRICTED_ROOTED7_DOMAIN.md'


def need(ok,msg):
    if not ok:raise ValueError(msg)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def determinant(a,b,c):
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])


def vertices(inequalities,tick):
    found={};attempts=0
    for selected in combinations(range(len(inequalities)),3):
        attempts+=1
        if not attempts%256:tick()
        rows=[inequalities[j]for j in selected];d=determinant(*[r[:3]for r in rows])
        if not d:continue
        columns=list(zip(*[r[:3]for r in rows]));rhs=[-r[3]for r in rows]
        nums=[determinant(*[rhs if q==j else columns[q]for q in range(3)])for j in range(3)]
        if d<0:d=-d;nums=[-v for v in nums]
        if all(sum(r[j]*nums[j]for j in range(3))+r[3]*d>=0 for r in inequalities):
            point=tuple(Fraction(v,d)for v in nums)
            found.setdefault(point,selected)
    return found,attempts


def exact_domain(inequalities,tick,cap):
    found,attempts=vertices(inequalities,tick);need(found,'EXACT_BOUNDED_POLYTOPE_EMPTY')
    bounds=[[math.ceil(min(p[j]for p in found)),math.floor(max(p[j]for p in found))]for j in range(3)]
    bounding_population=math.prod(max(0,b-a+1)for a,b in bounds);points=[]
    if bounding_population<=cap:
        for index,point in enumerate(product(*[range(a,b+1)for a,b in bounds])):
            if not index%256:tick()
            if all(sum(row[j]*point[j]for j in range(3))+row[3]>=0 for row in inequalities):points.append(list(point))
    return dict(vertices=[[[x.numerator,x.denominator]for x in p]for p in sorted(found)],vertex_generating_inequality_triples=[list(found[p])for p in sorted(found)],vertex_intersection_attempts=attempts,integer_bounding_box=bounds,bounding_integer_population=bounding_population,integer_points=points if bounding_population<=cap else None,complete_integer_domain=bounding_population<=cap)


def adjacency(mask):
    result=[set()for _ in range(6)]
    for bit,(u,v)in enumerate(combinations(range(6),2)):
        if(mask>>bit)&1:result[u].add(v);result[v].add(u)
    return result


def canonical(adj):
    return min(sum(1<<bit for bit,(u,v)in enumerate(combinations((0,1,*free),2))if v in adj[u])for free in permutations(range(2,6)))


def prism(mask):
    adj=adjacency(mask);triangles=[list(t)for t in combinations(range(6),3)if all(v in adj[u]for u,v in combinations(t,2))]
    return dict(mask=mask,neighbors=[sorted(v)for v in adj],degrees=[len(v)for v in adj],triangles=triangles,root_adjacent=1 in adj[0],canonical_mask=canonical(adj),is_triangular_prism=all(len(v)==3 for v in adj)and len(triangles)==2 and set(triangles[0]).isdisjoint(triangles[1]))


def residuals(rows,values,affine):return [sum(c*values[j]for j,c in r['terms'])-(r['rhs']if affine else 0)for r in rows]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--max_integer_attempts',type=int,default=1000000)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='3D exact affine-domain vertices from567integer inequalities;60outer40worker20reserve;maxone millionintegerpoints, no new graph/model build')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def tick():need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    try:
        for path,wanted in INPUTS.items():
            actual=sha(R/path);need(actual==wanted,'FROZEN_INPUT '+path);pins[(R/path).relative_to(ROOT).as_posix()]=actual
        for path in [Path(__file__),PROTOCOL,ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[path.relative_to(ROOT).as_posix()]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python_version=platform.python_version(),question='What is the entire nonnegative integer domain of the independently checked unrestricted rooted6 nonedge necessary model?',selection='All567 affine coordinate inequalities, no prism-zero premise; all rational vertices and all bounding integer triples up todeclaredcap.',success='Exact integer affine parameterization in actual mask7100/8024/15540 coordinates, complete bounded polytope and integer point census; allpoint allrow/allcoordinate checks.',independent_requirement='Separate checker must rederive coordinate prism interpretation and full domain completeness; discovery remains CANDIDATE.',max_integer_attempts=args.max_integer_attempts,scope='Unrestricted necessary local count domain only, no graph coverage or exclusion.'))
        cube=[[1,0,0,0],[-1,0,0,2],[0,1,0,0],[0,-1,0,2],[0,0,1,0],[0,0,-1,2]]
        test=exact_domain(cube,tick,100);need(len(test['vertices'])==8 and len(test['integer_points'])==27,'CUBE_POSITIVE_CONTROL')
        simplex=exact_domain([cube[0],cube[2],cube[4],[-1,-1,-1,2]],tick,100);need(len(simplex['vertices'])==4 and len(simplex['integer_points'])==10,'SIMPLEX_POSITIVE_CONTROL')
        for p in simplex['integer_points']:need(all(sum(r[j]*p[j]for j in range(3))+r[3]>=0 for r in [cube[0],cube[2],cube[4],[-1,-1,-1,2]]),'SIMPLEX_FULL_CONTROL')
        model=json.loads((R/'20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json').read_bytes());null=json.loads((R/'20261002_rooted6_exact_parameter_domain/unrestricted_nonedge_nullspace.json').read_bytes());conditional=json.loads((R/'20261002_rooted6_exact_parameter_domain/prismfree_nonedge_domain.json').read_bytes())
        free=null['rank_lower_bound']['free_coordinates'];need(free==[514,552,566]and [model['variables'][j]for j in free]==[[6,7100],[6,8024],[6,15540]],'ACTUAL_UNRESTRICTED_COUNT_AXES')
        origin=[Fraction(*v)for v in conditional['origin']];basis=[[Fraction(*v)for v in vector]for vector in null['rational_vectors']]
        need(len(origin)==567 and len(basis)==3 and all(len(v)==567 for v in basis),'AFFINE_SHAPE')
        need(all(v.denominator==1 for v in origin)and all(v.denominator==1 for vec in basis for v in vec),'INTEGER_AFFINE_ORIGIN_BASIS')
        origin=list(map(int,origin));basis=[list(map(int,v))for v in basis]
        need([origin[j]for j in free]==[0,0,0]and [[basis[q][j]for j in free]for q in range(3)]==[[1,0,0],[0,1,0],[0,0,1]],'IDENTITY_FREE_MINOR')
        need(not any(residuals(model['equations'],origin,True))and all(not any(residuals(model['equations'],v,False))for v in basis),'EXACT_ALL_RAW_AFFINE_ROWS')
        corrupt=origin[:];corrupt[0]+=1;need(any(residuals(model['equations'],corrupt,True)),'CORRUPT_ORIGIN_CONTROL')
        corrupt=basis[0][:];corrupt[0]+=1;need(any(residuals(model['equations'],corrupt,False)),'CORRUPT_KERNEL_CONTROL')
        prism_records=[prism(mask)for mask in [7100,8025,15541]];need(all(r['is_triangular_prism']and r['canonical_mask']==r['mask']for r in prism_records)and not prism_records[0]['root_adjacent']and all(r['root_adjacent']for r in prism_records[1:]),'ROOTED_PRISM_GEOMETRY')
        inequalities=[];witnesses=[]
        for j,c in enumerate(origin):
            row=[basis[q][j]for q in range(3)]+[c];g=math.gcd(*row)
            if g:row=[v//g for v in row]
            if row not in inequalities:inequalities.append(row);witnesses.append([j])
            else:witnesses[inequalities.index(row)].append(j)
        # Nonnegative counts and the complete order6 total prove a compact box.
        six=[j for j,(h,mask)in enumerate(model['variables'])if h==6];total=math.comb(97,4)
        need(sum(origin[j]for j in six)==total and all(sum(v[j]for j in six)==0 for v in basis),'ALL_ORDER6_COUNTS_TOTAL')
        for coordinate in range(3):
            row=[-int(j==coordinate)for j in range(3)]+[total]
            if row not in inequalities:inequalities.append(row);witnesses.append([])
        result=exact_domain(inequalities,tick,args.max_integer_attempts)
        if result['integer_points']is not None:
            for index,point in enumerate(result['integer_points']):
                if not index%32:tick()
                values=[origin[j]+sum(point[q]*basis[q][j]for q in range(3))for j in range(567)]
                need(min(values)>=0 and [values[j]for j in free]==point and not any(residuals(model['equations'],values,True)),'EVERY_UNRESTRICTED_POINT_FULL_INTEGER_ROWS')
        zero_face=[[p[1],p[2]]for p in result['integer_points']if p[0]==0]if result['integer_points']is not None else None
        need(zero_face is None or zero_face==conditional['exact_integer_feasible_points'],'EXACT_OLD_ZERO_FACE_RECOVERED')
        result.update(format='EXACT_UNRESTRICTED_ROOTED6_NONEDGE_PARAMETER_DOMAIN_CANDIDATE_V1',coordinate_order=['c','a','b'],free_coordinates=free,free_variables=[model['variables'][j]for j in free],origin=origin,basis=basis,inequalities_primitive_integer=inequalities,inequality_raw_coordinate_witnesses=witnesses,compactness_argument='Everycoordinateisactualsixflagcount;sum456sixflagcounts=C(97,4),allnonnegative;three redundant upperboundsC(97,4). Everyvertex ofthe resultingcompact3Dpolytope arises atthreeindependenttight inequalities. Alltriplesenumeratedexactly.',rooted_prism_geometry=prism_records,complete_zero_face_equals_prior210=zero_face==conditional['exact_integer_feasible_points'],graph_realizability_asserted=False,independent_review=None,independent_review_reason='New3Ddomain/prisminterpretation awaitdifferentcheckingpath.')
        save(out/'domain.json',result)
        summary=dict(status='CANDIDATE_UNRESTRICTED_ROOTED6_NONEDGE_EXACT_DOMAIN',timestamp=datetime.now(timezone.utc).isoformat(),coordinates=result['coordinate_order'],inequalities=len(inequalities),rational_vertices=len(result['vertices']),integer_bounding_box=result['integer_bounding_box'],bounding_integer_population=result['bounding_integer_population'],complete_integer_domain=result['complete_integer_domain'],integer_profile_count=None if result['integer_points']is None else len(result['integer_points']),zero_prism_face_profiles=None if zero_face is None else len(zero_face),positive_prism_profile_count=None if result['integer_points']is None else len(result['integer_points'])-len(zero_face),complete_raw_rows_per_profile=1445,controls=dict(cube8vertices27integers=True,simplex4vertices10integers=True,changedoriginandkernelrejected=True),domain_sha256=sha(out/'domain.json'),elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),target_resolution=False,scope='Candidate exact unrestricted necessary local integer count domain; no graph construction, exclusion, target coverage or automorphism.',outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()})
        save(out/'summary.json',summary);print(json.dumps(summary))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-started,outputs_preserved=True));raise


if __name__=='__main__':main()
