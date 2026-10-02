"""Independent necessary nonedge rooted6 row/nullspace/domain derivation.

Discovery code is not imported. Complete raw null vectors are checked against
independently reconstructed rows, with a different prime/Python rank path.
The nonnegative domain is proved by explicit coordinate witnesses and four
corners, independently of the producer's polygon-clipping implementation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_rooted6_prismfree_v2 as review

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"acceleration/results/20261002_rooted6_prismfree_rigidity"
DOMAIN=ROOT/"acceleration/results/20261002_rooted6_exact_parameter_domain"
PINS={
    RAW/"ordered_nonedge_model.json":"ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645",
    RAW/"ordered_nonedge_prismfree_rows.json":"c3d65c00754b4b600140b0723fad42c23748324237ec16d1cdf506d73bc606c2",
    RAW/"ordered_nonedge_prismfree_primal.json":"1dadc060d77051baefe10ecc8bea5afc26441c3cfea877f37c6a484ded4fa64b",
    DOMAIN/"unrestricted_nonedge_nullspace.json":"5f3c4b485522156cccc458411d4b2f4517a320905418dc753c9896a5e0dbf384",
    DOMAIN/"prismfree_nonedge_nullspace.json":"b8abff4be27e90c5d1274cf94ee8aff262cf02117a2086cfdffec5dc97a13e77",
    DOMAIN/"prismfree_nonedge_domain.json":"54f08f8dc87bebf61bada59067cbc721497f3d3a9683936e850b695f0ec41b12",
}


def need(value,reason):
    if not value:raise ValueError(reason)


def save(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,indent=2)
        stream.write("\n")


def bases(deadline):
    classes,inventories={},[]
    for h in tqdm(range(2,7),desc="Independent rooted nonedge bases"):
        possible={mask for mask in range(0,1<<len(review.independent.pairs(h)),2)
            if review.independent.caps(review.independent.matrix(h,mask))}
        labelled=len(possible)
        representatives=[]
        while possible:
            images=review.independent.orbit(h,min(possible))
            need(images<=possible,"complete root-fixing admissible orbit")
            representatives.append(min(images));possible.difference_update(images)
        classes[h]=representatives
        inventories.append(dict(order=h,all_simple_masks=1<<len(review.independent.pairs(h)),
            ordered_nonedge_admissible_labelled_masks=labelled,rooted_classes=len(representatives)))
        need(not deadline.status()["stop_required"],"not completed within the allocated budget")
    return classes,inventories


def rational(values,columns):
    need(len(values)==columns,"entire rational vector")
    result=[]
    for value in values:
        need(len(value)==2 and all(type(cell)is int for cell in value) and value[1]>0,"exact rational cell")
        result.append(Fraction(*value))
    return result


def homogeneous(rows,vector):
    return all(sum(coefficient*vector[col] for col,coefficient in row["terms"])==0 for row in rows)


def space(certificate,rows,columns,wanted_rank):
    need(certificate["format"]=="EXACT_ROOTED6_AFFINE_NULLSPACE_V1","exact certificate format")
    rank=review.independent.modular_rank(rows,columns,1009)
    need(rank["rank"]==wanted_rank,"independent prime rank lower bound")
    vectors=[rational(vector,columns) for vector in certificate["rational_vectors"]]
    free=certificate["rank_lower_bound"]["free_coordinates"]
    need(len(vectors)==len(free)==columns-wanted_rank and len(set(free))==len(free),"matching nullity upper/lower bounds")
    need(all(homogeneous(rows,vector) for vector in vectors),"every exact homogeneous equation")
    need([[vector[col] for vector in vectors] for col in free]==
        [[Fraction(int(i==j)) for j in range(len(vectors))] for i in range(len(free))],"independent identity minor of rational vectors")
    integers=certificate["primitive_integer_vectors"]
    need(len(integers)==len(vectors),"all independent integer null vectors saved")
    for integers_row,vector in zip(integers,vectors):
        den=math.lcm(*(value.denominator for value in vector));scaled=[int(value*den) for value in vector]
        gcd=math.gcd(*scaled);scaled=[value//gcd for value in scaled]
        need(integers_row==scaled and homogeneous(rows,integers_row),"primitive integer vector exact identity")
    need(certificate["exact_rational_rank"]==wanted_rank and certificate["exact_nullity"]==len(vectors)
        and certificate["rank_upper_bound_from_independent_vectors"]==wanted_rank,"recorded rank equals independently matching exact bounds")
    changed=list(vectors[0]);changed[0]+=1
    need(not homogeneous(rows,changed),"corrupted null vector rejected")
    return vectors,free,rank


def normalize(coefficients):
    den=math.lcm(*(value.denominator for value in coefficients))
    ints=[int(value*den) for value in coefficients];divisor=math.gcd(*ints)
    return tuple(value//divisor for value in ints) if divisor else tuple(ints)


def run(args):
    start=time.monotonic()
    deadline=CommandDeadline(args.seconds,allocation_reason="Complete567-column nonedge basis/rows, exact3/2-vector nullspaces, and all210integer profiles;30second output reserve")
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    pins={}
    def pin(path,wanted=None):
        path=path.resolve();actual=hashlib.sha256(path.read_bytes()).hexdigest()
        need(wanted is None or actual==wanted,"exact input: "+path.name)
        pins[path.relative_to(ROOT).as_posix()]=actual
    try:
        for path,wanted in PINS.items():pin(path,wanted)
        pin(ROOT/"acceleration/audit_20261002_rooted6_prismfree_v2.py","006e2c9bcb5be8a65250897dca6089cd62e6804664c91cb00b35a569e40d6722")
        pin(ROOT/"acceleration/audit_20261002_rooted5_rigidity_v2.py",review.HELPER_SHA)
        for path in [Path(__file__),DOMAIN/"manifest.json",DOMAIN/"summary.json",ROOT/"uv.lock",ROOT/"pyproject.toml",ROOT/"acceleration/command_deadline.py",ROOT/"acceleration/run_compute_command.py"]:pin(path)
        raw={path.name:json.loads(path.read_bytes()) for path in PINS}
        classes,inventories=bases(deadline)
        variables,rows,transports=review.reconstruct(classes,99,14,deadline)
        model=raw["ordered_nonedge_model.json"]
        need(model["adjacent_roots"] is False,"actual ordered-nonedge root relation")
        review.independent.verify_model(model,variables,rows)
        need(len(variables)==567 and len(rows)==1445,"complete frozen universe dimensions")
        prism_indices=[at for at,(h,mask) in enumerate(variables) if h==6 and review.prism(mask)]
        added=[dict(kind="prismfree",order=6,mask=variables[at][1],mark=None,terms=[[at,1]],rhs=0) for at in prism_indices]
        need(added==raw["ordered_nonedge_prismfree_rows.json"] and len(added)==1,"entire conditional nonedge prism basis")
        unconditional,unconditional_free,base_rank=space(raw["unrestricted_nonedge_nullspace.json"],rows,len(variables),564)
        conditional_rows=[*rows,*added]
        vectors,free,conditional_rank=space(raw["prismfree_nonedge_nullspace.json"],conditional_rows,len(variables),565)
        primal=raw["ordered_nonedge_prismfree_primal.json"]["exact_primal"]
        need(len(primal)==567 and all(type(value)is int and value>=0 for value in primal) and review.rows_hold(primal,conditional_rows),"complete independent exact affine consistency")
        domain=raw["prismfree_nonedge_domain.json"]
        need(domain["format"]=="EXACT_ROOTED6_PRISMFREE_PARAMETER_DOMAIN_V1" and domain["free_coordinates"]==free
            and domain["free_variables"]==[list(variables[col]) for col in free],"precise actual flagged-count parameter axes")
        origin=[Fraction(primal[col])-sum(primal[axis]*vectors[i][col] for i,axis in enumerate(free)) for col in range(567)]
        need(origin==rational(domain["origin"],567) and review.rows_hold(origin,conditional_rows),"exact affine origin")
        need(all(origin[col]==0 for col in free),"actual parameters equal their free count coordinates")
        inequalities={normalize([vectors[0][col],vectors[1][col],origin[col]]) for col in range(567)}
        need(inequalities=={tuple(value) for value in domain["inequalities_primitive_integer"]},"every exact coordinate nonnegativity inequality")
        # Independent rectangle proof: free counts yield a,b>=0. Coordinate
        # witnesses give upper bounds without polygon clipping or LP calls.
        upper=[];witnesses=[]
        for at in range(2):
            candidates=[(origin[col]/-vectors[at][col],col) for col in range(567)
                if vectors[at][col]<0 and vectors[1-at][col]==0]
            need(candidates,"explicit uncoupled upper-bound coordinate")
            bound,col=min(candidates);upper.append(bound)
            witnesses.append(dict(parameter=at,coordinate=col,variable=list(variables[col]),constant=[origin[col].numerator,origin[col].denominator],coefficient=[vectors[at][col].numerator,vectors[at][col].denominator],bound=[bound.numerator,bound.denominator]))
        need(upper==[Fraction(20),Fraction(9)],"independent coordinate upper bounds")
        corners=[(Fraction(a),Fraction(b)) for a in [0,20] for b in [0,9]]
        for a,b in corners:
            values=[origin[col]+a*vectors[0][col]+b*vectors[1][col] for col in range(567)]
            need(all(value>=0 for value in values),"every affine coordinate nonnegative at all four corners")
        # All affine inequalities nonnegative at the rectangle's corners hold
        # throughout its convex hull; witness bounds prove the reverse inclusion.
        raw_vertices={tuple(Fraction(*value) for value in point) for point in domain["vertices"]}
        need(raw_vertices==set(corners) and domain["integer_bounding_rectangle"]==[[0,20],[0,9]],"saved rational polygon exactly independently proved rectangle")
        points=[];vector_records=[]
        for a in tqdm(range(21),desc="All exact necessary integer profiles"):
            for b in range(10):
                values=[origin[col]+a*vectors[0][col]+b*vectors[1][col] for col in range(567)]
                need(all(value.denominator==1 and value>=0 for value in values) and review.rows_hold(values,conditional_rows),"every full integer profile exact all-row check")
                integers=[int(value) for value in values]
                need([integers[col] for col in free]==[a,b],"distinct full profiles witnessed by actual parameter counts")
                points.append([a,b]);vector_records.append(dict(parameters=[a,b],full_count_vector=integers))
            need(not deadline.status()["stop_required"],"not completed within the allocated budget")
        need(domain["exact_integer_feasible_points"]==points and domain["integer_count_vectors"]==210 and domain["rectangle_attempts"]==210
            and domain["nonnegative_rectangle_points"]==210 and domain["fractional_vectors_rejected"]==0 and domain["complete_integer_domain"] is True
            and domain["graph_realizability_asserted"] is False,"complete exact saved210localprofile scope")
        outside=[]
        for a,b in [(-1,0),(0,-1),(21,0),(0,10)]:
            values=[origin[col]+a*vectors[0][col]+b*vectors[1][col] for col in range(567)]
            need(min(values)<0,"outside parameter control excluded by exact nonnegativity")
            outside.append([a,b])
        # Actual rook fixture validates every necessary row, including order6.
        rook=[[int(a!=b and (a//3==b//3 or a%3==b%3)) for b in range(9)] for a in range(9)]
        need(review.independent.graph_is_srg(rook,4),"independent known-valid rook SRG")
        fixture_variables,fixture_rows,_=review.reconstruct(classes,9,4,deadline)
        need(fixture_variables==variables,"same necessary nonedge basis in valid control")
        fixture_count=0
        for a,b in review.independent.permutations(range(9),2):
            if rook[a][b]:continue
            counts=review.count_root(rook,(a,b),variables)
            need(review.rows_hold(counts,fixture_rows),"every necessary row for every actual rook ordered nonedge")
            need(any(counts[col] for col in prism_indices),"prism-bearing fixture rejects conditional zero face")
            fixture_count+=1
        need(fixture_count==36,"all actual known-valid nonedge fixture roots")
        detail=dict(variables=[list(value) for value in variables],reconstructed_rows=rows,prism_zero_rows=added,
            basis_inventory=inventories,marked_isomorphism_value_checks=transports,
            unrestricted_modular_rank=base_rank,conditional_modular_rank=conditional_rank,
            exact_nullspace_dimensions=[3,2],conditional_free_count_coordinates=free,
            nonnegative_rectangle_upper_bound_witnesses=witnesses,complete_integer_profiles=vector_records)
        save(args.out/"nonedge_audit.json",detail);pin(args.out/"nonedge_audit.json")
        result=dict(status="INDEPENDENT_ROOTED6_NONEDGE_EXACT_NULLSPACES_AND_CONDITIONAL_DOMAIN_PASS",
            timestamp=datetime.now(timezone.utc).isoformat(),verifier="/root/checkpoint_audit",producer="/root/structural",method="independent_derivation",
            source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            statement="The complete necessary ordered-nonedge rooted6 integer row model has exact rational rank564 and nullity3. Its triangular-prism-zero conditional model has exact rational rank565 and nullity2. The latter's entire nonnegative integer solution set consists exactly of the saved210full567-coordinate profiles parameterized by actual six-flag counts (mask8024,mask15540) with0<=a<=20 and0<=b<=9.",
            scope="Exact complete local necessary row models;210profile domain requires a hypothetical target with no induced triangular prism. No target automorphism or graph realization is assumed.",
            variables=567,unrestricted_rows=1445,conditional_rows=1446,exact_rational_ranks=[564,565],exact_nullities=[3,2],
            complete_integer_profiles=210,conditional_count_axes=[list(variables[col]) for col in free],
            controls=dict(corrupted_null_vectors_rejected=2,outside_rectangle_points_rejected=outside,
                known_valid_rook_ordered_nonedges=36,necessary_rows_per_fixture_root=1445,conditional_prismfree_rejections=36),
            shared_components=["Prior independently authored rooted5/6 geometry, DSU mark, reconstruction and purePython prime-rank helpers are pinned; no discovery model builder, numerical solver or polygon clipper imported.","Python exact integer/Fraction arithmetic and locked environment."],
            limitations=["Prism absence remains UNKNOWN for the unrestricted target.","The210units are local necessary count profiles, not target graphs or an exhaustive graph search.","No construction, exclusion, novelty or target-wide coverage percentage follows from an exact necessary domain."],
            new_exclusions=0,target_resolution=False,graph_realizability_asserted=False,prismfree_premise_established=False,
            artifact_availability="LOCAL_ONLY",elapsed_seconds=time.monotonic()-start)
        save(args.out/"summary.json",result)
        print(json.dumps(dict(status=result["status"],sha256=hashlib.sha256((args.out/"summary.json").read_bytes()).hexdigest(),elapsed_seconds=result["elapsed_seconds"])),flush=True)
    except BaseException as error:
        save(args.out/"failure.json",dict(error=repr(error),elapsed_seconds=time.monotonic()-start,target_resolution=False))
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--out",type=Path,required=True);parser.add_argument("--seconds",type=float,required=True)
    run(parser.parse_args())
