"""Candidate unrestricted rooted6 edge exact affine domain.

Reuses the existing discovery modular-lifting helper, fully disclosed/pinned.
No target graph/model builder or native solver. Independent review is required.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from command_deadline import CommandDeadline
import theory_20261002_rooted6_exact_parameter_domain as L

ROOT=L.ROOT;R=ROOT/'acceleration/results'
INPUTS={
 '20261002_rooted6_prismfree_rigidity/ordered_edge_model.json':'06051294a142dfcda956f4ee3748986982f7f8ba5f9785fe4d7680d967538584',
 '20261002_rooted6_prismfree_rigidity/ordered_edge_prismfree_primal.json':'8c914f27e91f5c003644148738b9a634ac0dfe9683915dd42dc3ae067d2a2010',
 '20261002_independent_review/rooted6_prismfree02/summary.json':'f7e8f93a671648cd0e73c326a36ee8cc97682a2c568ed88f46044cb04abd4717'}
HELPER_SHA='4827a116ac9258d0ccd0fedc43891efc49cb0dc0e09309b72c983d62e9c8d139'
PROTOCOL=ROOT/'docs/DESIGN_20261002_UNRESTRICTED_ROOTED6_EDGE_DOMAIN.md'


def domain(origin,basis,tick,cap):
    inequalities=[];witnesses=[]
    for j,c in enumerate(origin):
        values=[basis[0][j],basis[1][j],c];den=math.lcm(*(v.denominator for v in values));row=[int(v*den)for v in values];g=math.gcd(*row)
        if g:row=[v//g for v in row]
        if row in inequalities:witnesses[inequalities.index(row)].append(j)
        else:inequalities.append(row);witnesses.append([j])
    total=math.comb(97,4)
    for row in [[-1,0,total],[0,-1,total]]:
        if row not in inequalities:inequalities.append(row);witnesses.append([])
    points={};attempts=0
    for i,j in combinations(range(len(inequalities)),2):
        attempts+=1
        if not attempts%128:tick()
        a,b,c=inequalities[i];d,e,f=inequalities[j];det=a*e-b*d
        if not det:continue
        x=(b*f-c*e);y=(c*d-a*f)
        if det<0:det=-det;x=-x;y=-y
        if all(a*x+b*y+c*det>=0 for a,b,c in inequalities):points.setdefault((Fraction(x,det),Fraction(y,det)),[i,j])
    L.need(points,'EXACT_EDGE_DOMAIN_NONEMPTY')
    bounds=[[math.ceil(min(p[q]for p in points)),math.floor(max(p[q]for p in points))]for q in range(2)];population=math.prod(b-a+1 for a,b in bounds);integer=[];fractional=[]
    if population<=cap:
        for p in product(*[range(a,b+1)for a,b in bounds]):
            if not all(a*p[0]+b*p[1]+c>=0 for a,b,c in inequalities):continue
            values=[origin[j]+sum(p[q]*basis[q][j]for q in range(2))for j in range(len(origin))]
            if any(v.denominator!=1 for v in values):fractional.append(list(p))
            else:integer.append(list(p))
    return dict(vertices=[[[v.numerator,v.denominator]for v in p]for p in sorted(points)],vertex_generating_inequality_pairs=[points[p]for p in sorted(points)],integer_bounding_rectangle=bounds,bounding_integer_population=population,inequalities_primitive_integer=inequalities,inequality_raw_coordinate_witnesses=witnesses,integer_points=integer if population<=cap else None,fractional_vector_points=fractional if population<=cap else None,complete_integer_domain=population<=cap,pair_intersection_attempts=attempts)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--max_integer_attempts',type=int,default=1000000)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Previouslyseconds-scale394variable exact modularlift and2Ddomain;60outer40worker20reserve;no newroot7build');out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic();pins={}
    def tick():L.need(not deadline.status()['stop_required'],'not completed within allocated budget')
    try:
        L.need(L.sha(L.__file__)==HELPER_SHA,'UNCHANGED_EXACT_LIFT_HELPER')
        for path,wanted in INPUTS.items():L.need(L.sha(R/path)==wanted,'FROZEN_INPUT '+path);pins[(R/path).relative_to(ROOT).as_posix()]=wanted
        for path in [Path(__file__),Path(L.__file__),PROTOCOL,ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'pyproject.toml',ROOT/'uv.lock']:pins[path.relative_to(ROOT).as_posix()]=L.sha(path)
        L.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,question='What is the unrestricted exact edge rooted6 affine profile/domain needed by rerooting?',selection='Complete frozen394variable1099rowmodel; exactkernel lifts prime65521 then1000000007 onlyifneeded; every raw row replay; all2Dvertices and entire bounded integer rectangle undercap.',success='Exactrankbounded byexplicitkernel andprimenonzero minor; actualtwo prism coordinates; exactdomain andallacceptedprofile integer/rawrowchecks.',independent_requirement='New exactkernel/domain are discovery candidates until independently reconstructed and audited; prior conditionalrankgate alone is not an unrestrictedkernel/domaingate.',max_integer_attempts=args.max_integer_attempts,python_version=platform.python_version(),numpy_version=L.np.__version__,shared_discovery_helper='Unchanged old exact modular echelon/lift code, not independent validation.'))
        # Cheap independent arithmetic controls for domain intersections.
        origin=[Fraction(0),Fraction(0),Fraction(2),Fraction(2)];basis=[[Fraction(1),Fraction(0),Fraction(-1),Fraction(0)],[Fraction(0),Fraction(1),Fraction(0),Fraction(-1)]]
        test=domain(origin,basis,tick,100);L.need(len(test['vertices'])==4 and len(test['integer_points'])==9,'HAND_SQUARE_DOMAIN')
        model=L.read(R/'20261002_rooted6_prismfree_rigidity/ordered_edge_model.json');rows=model['equations'];columns=len(model['variables']);cert,basis=L.lift(rows,columns,deadline,out,'unrestricted_edge')
        L.need(cert['exact_nullity']==2 and cert['exact_rational_rank']==392,'EXACT_EDGE_AFFINE_DIMENSION')
        free=cert['rank_lower_bound']['free_coordinates'];L.need(free==[382,393]and [model['variables'][j]for j in free]==[[6,8025],[6,15541]],'ACTUAL_EDGE_PRISM_AXES')
        origin=list(map(Fraction,L.read(R/'20261002_rooted6_prismfree_rigidity/ordered_edge_prismfree_primal.json')['exact_primal']))
        L.need([origin[j]for j in free]==[0,0]and not any(L.residuals(rows,origin,True)),'EXACT_UNRESTRICTED_EDGE_ORIGIN')
        corrupt=origin[:];corrupt[0]+=1;L.need(any(L.residuals(rows,corrupt,True)),'CORRUPT_EDGE_ORIGIN')
        corrupt=basis[0][:];corrupt[0]+=1;L.need(any(L.residuals(rows,corrupt,False)),'CORRUPT_EDGE_KERNEL')
        six=[j for j,(h,mask)in enumerate(model['variables'])if h==6]
        L.need(sum(origin[j]for j in six)==math.comb(97,4)and all(sum(v[j]for j in six)==0 for v in basis),'EDGE_COMPACT_COUNT_TOTAL')
        result=domain(origin,basis,tick,args.max_integer_attempts)
        if result['integer_points']is not None:
            for p in result['integer_points']:
                tick();values=[origin[j]+sum(p[q]*basis[q][j]for q in range(2))for j in range(columns)]
                L.need(all(v.denominator==1 and v>=0 for v in values)and not any(L.residuals(rows,values,True)),'EVERY_EDGE_INTEGER_PROFILE_ALL_ROWS')
        result.update(format='EXACT_UNRESTRICTED_ROOTED6_EDGE_PARAMETER_DOMAIN_CANDIDATE_V1',coordinate_order=['triangle_edge_prism','matching_edge_prism'],free_coordinates=free,free_variables=[model['variables'][j]for j in free],origin=[[v.numerator,v.denominator]for v in origin],basis=[[[v.numerator,v.denominator]for v in vec]for vec in basis],exact_rational_rank=392,exact_nullity=2,compactness_argument='All307sixflagcounts nonnegative,sumC(97,4); twoactualprismcounts0..total. Enumerateallindependenttightplane pairs andtesteveryinequality; fullintegerrectangle scanned.',independent_review=None,independent_review_reason='Separate exactkernel/domaincheckingpending.',graph_realizability_asserted=False)
        L.save(out/'domain.json',result)
        summary=dict(status='CANDIDATE_UNRESTRICTED_ROOTED6_EDGE_EXACT_DOMAIN',timestamp=datetime.now(timezone.utc).isoformat(),exact_rank=392,exact_nullity=2,rational_vertices=len(result['vertices']),integer_bounding_rectangle=result['integer_bounding_rectangle'],bounding_integer_population=result['bounding_integer_population'],integer_profile_count=None if result['integer_points']is None else len(result['integer_points']),fractional_profiles_rejected=None if result['fractional_vector_points']is None else len(result['fractional_vector_points']),complete_integer_domain=result['complete_integer_domain'],kernel_sha256=L.sha(out/'unrestricted_edge_nullspace.json'),domain_sha256=L.sha(out/'domain.json'),elapsed_seconds=time.monotonic()-started,deadline=deadline.status(),target_resolution=False,scope='Exact necessary unrestricted edge count profile candidate, no graph/exclusion/coverage or automorphism. Discovery helper reused and disclosed.')
        L.save(out/'summary.json',summary);print(json.dumps(summary))
    except BaseException as error:L.save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-started,outputs_preserved=True));raise


if __name__=='__main__':main()
