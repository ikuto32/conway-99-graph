"""Eight unrestricted rooted7 corner guides; exact literal certificates only.

Copied numerical model-scaling mechanics from the disclosed prior corner drivers;
no discovery helper imports. Continuous rational counts never certify a graph.
"""
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
import highspy
import numpy as np
from scipy.sparse import coo_matrix
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'acceleration/results/20261002_rooted7_unrestricted_extension01/model.json'
MODEL_SHA='9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1'
AUDIT=ROOT/'acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/summary.json'
AUDIT_SHA='e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70'
SPEC=ROOT/'docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_CORNERS_V1.md'
CORNERS=[(c,a,b)for c in[0,2]for a in[0,20]for b in[0,9+c//2]]
POPULATION=[(c,a,b)for c in range(3)for a in range(21)for b in range(10+c//2)]
GRIDS=[1,10,1000,1000000]


def need(ok,why):
    if not ok:raise ValueError(why)


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,data):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(data,stream,indent=2);stream.write('\n')


def rhs(rows,point):
    return[sum(v*w for v,w in zip(row['rhs_affine'],[1,*point]))for row in rows]


def primal(rows,values,denominator,point):
    need(type(denominator)is int and denominator>0,'positive integer denominator')
    return min(values)>=0 and all(sum(coefficient*values[j]for j,coefficient in row['terms'])==target*denominator for row,target in zip(rows,rhs(rows,point)))


def farkas(rows,columns,values,point):
    products=[0]*columns;parameters=[0]*4
    for multiplier,row in zip(values,rows):
        for j,coefficient in row['terms']:products[j]+=multiplier*coefficient
        for j,coefficient in enumerate(row['rhs_affine']):parameters[j]+=multiplier*coefficient
    return min(products)>=0 and sum(v*w for v,w in zip(parameters,[1,*point]))<0,parameters


def common_fraction(values):
    denominator=math.lcm(*(value.denominator for value in values))
    return[value.numerator*(denominator//value.denominator)for value in values],denominator


def guide(rows,columns,point,seconds,scales,out,prefix):
    started=time.monotonic();rr=[];cc=[];vv=[];target=rhs(rows,point)
    for i,row in enumerate(rows):
        for j,coefficient in row['terms']:rr.append(i);cc.append(j);vv.append(coefficient)
    matrix=coo_matrix((vv,(rr,cc)),shape=(len(rows),columns),dtype=np.float64).tocsr()
    scaled=matrix.copy();scaled.data*=np.asarray(scales,dtype=np.float64)[scaled.indices]
    row_scales=np.maximum(np.maximum(np.asarray(abs(scaled).max(axis=1).toarray()).ravel(),abs(np.asarray(target,dtype=np.float64))),1)
    scaled.data/=np.repeat(row_scales,np.diff(scaled.indptr))
    lp=highspy.HighsLp();lp.num_col_=columns;lp.num_row_=len(rows)
    lp.col_names_=[f'c{j}'for j in range(columns)];lp.row_names_=[f'r{i}'for i in range(len(rows))]
    lp.col_cost_=np.zeros(columns);lp.col_lower_=np.zeros(columns);lp.col_upper_=np.full(columns,highspy.kHighsInf)
    lp.row_lower_=lp.row_upper_=np.asarray(target,dtype=np.float64)/row_scales
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_=scaled.indptr;lp.a_matrix_.index_=scaled.indices;lp.a_matrix_.value_=scaled.data
    highs=highspy.Highs()
    for name,value in[('output_flag',False),('threads',1),('random_seed',0),('solver','simplex'),('presolve','off'),('time_limit',seconds),('primal_feasibility_tolerance',1e-10),('dual_feasibility_tolerance',1e-10)]:need(highs.setOptionValue(name,value)==highspy.HighsStatus.kOk,'HiGHS option '+name)
    need(highs.passModel(lp)==highspy.HighsStatus.kOk,'literal scaled model loaded')
    record=dict(parameters=list(point),column_scales=scales,row_scales=[int(value)for value in row_scales],preparation_seconds=time.monotonic()-started,guide_seconds=seconds,status='UNKNOWN_NO_EXACT_CERTIFICATE')
    started=time.monotonic();status=highs.run();record.update(run_status=str(status),model_status=str(highs.getModelStatus()),native_seconds=time.monotonic()-started)
    solution=highs.getSolution();record['numerical_values']=[float(value*scale)if math.isfinite(value*scale)else None for value,scale in zip(solution.col_value,scales)]
    if highs.getBasis().valid:
        basis=out/(prefix+'.bas');need(highs.writeBasis(str(basis))==highspy.HighsStatus.kOk,'basis saved');record['saved_basis']=dict(path=basis.relative_to(ROOT).as_posix(),sha256=sha(basis),certificate=False)
    ray_status,exists=highs.getDualRayExist();record.update(ray_existence_status=str(ray_status),ray_exists=bool(exists))
    if exists:
        ray_status,returned,ray=highs.getDualRay();need(returned,'stored ray exists; implicit solver prohibited')
        record.update(ray_retrieval_status=str(ray_status),numerical_ray=[float(v/s)if math.isfinite(v/s)else None for v,s in zip(ray,row_scales)])
    return record


def certify(rows,columns,record):
    point=record['parameters'];attempts=[];numeric=record['numerical_values']
    if len(numeric)==columns and all(value is not None for value in numeric):
        for maximum in GRIDS:
            values=[Fraction(value).limit_denominator(maximum)for value in numeric];integers,denominator=common_fraction(values)
            ok=primal(rows,integers,denominator,point);attempts.append(dict(kind='primal',max_individual_denominator=maximum,common_denominator=denominator,exact_pass=ok))
            if ok:
                record.update(status='CANDIDATE_EXACT_RATIONAL_PRIMAL',certificate_numerators=integers,certificate_denominator=denominator,integer_vector=all(v%denominator==0 for v in integers));break
    if record['status']=='UNKNOWN_NO_EXACT_CERTIFICATE'and record.get('numerical_ray')and all(value is not None for value in record['numerical_ray']):
        numeric=record['numerical_ray'];magnitude=max(abs(value)for value in numeric)
        if magnitude:
            for maximum in GRIDS:
                values=[Fraction(value/magnitude).limit_denominator(maximum)for value in numeric];integers,denominator=common_fraction(values)
                for sign in[1,-1]:
                    multipliers=[sign*v for v in integers];ok,parameters=farkas(rows,columns,multipliers,point);attempts.append(dict(kind='farkas',max_individual_denominator=maximum,sign=sign,exact_pass=ok))
                    if ok:record.update(status='CANDIDATE_EXACT_FARKAS_EXCLUSION',certificate_multipliers=multipliers,certificate_rhs_affine=parameters);break
                if record['status']!='UNKNOWN_NO_EXACT_CERTIFICATE':break
    record['exact_attempts']=attempts


def controls(out):
    rows=[dict(terms=[[0,2]],rhs_affine=[1,0,0,0])]
    need(primal(rows,[1],2,[0,0,0])and not primal(rows,[2],2,[0,0,0]),'positive and corrupted rational primal')
    changed=[dict(terms=[[0,3]],rhs_affine=[1,0,0,0])];need(not primal(changed,[1],2,[0,0,0]),'genuine coefficient corruption')
    negative=[dict(terms=[[0,1]],rhs_affine=[-1,0,0,0])]
    need(farkas(negative,1,[1],[0,0,0])[0]and not farkas(negative,1,[-1],[0,0,0])[0],'positive and sign-corrupted Farkas')
    first=guide(rows,1,[0,0,0],5,[1],out,'tiny_positive');certify(rows,1,first);need(first['status']=='CANDIDATE_EXACT_RATIONAL_PRIMAL','actual positive numerical guide exact replay')
    second=guide(negative,1,[0,0,0],5,[1],out,'tiny_negative');certify(negative,1,second);need(second['status']=='CANDIDATE_EXACT_FARKAS_EXCLUSION','actual stored ray exact replay')
    save(out/'controls.json',dict(positive=first,negative=second,corrupt_primal_coefficient_and_ray_sign_rejected=True,producer_calibration_only=True))


def weights(point):
    c,a,b=point;t=Fraction(c,2);u=Fraction(a,20);z=Fraction(2*b,18+c)
    result=[(t if C else 1-t)*(u if A else 1-u)*(z if B else 1-z)for C,A,B in CORNERS]
    need(min(result)>=0 and sum(result)==1 and all(sum(w*p[j]for w,p in zip(result,CORNERS))==point[j]for j in range(3)),'exact eight-corner barycentric coordinates')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--controls-only',action='store_true');args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Old conditional four sparse guides .53s plus210 exact checks24s; eight unrestricted guides+651integerparameter rational replays,300outer260worker60internalreserve')
    start=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        need(sha(MODEL)==MODEL_SHA and sha(AUDIT)==AUDIT_SHA,'frozen raw model and independent necessary-encoding audit')
        pins={p.relative_to(ROOT).as_posix():sha(p)for p in[MODEL,AUDIT,SPEC,Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py']}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python_version=platform.python_version(),highs_version=highspy.Highs().version(),numpy_version=np.__version__,selected_corners=CORNERS,selected_integer_parameter_profiles=POPULATION,selection='All eight rational vertices of the complete local c,a,b domain; no omissions. Any exact Farkas is evaluated on all651 profiles; all8 primals permit exact convex interpolation.',scope='Unrestricted necessary CONTINUOUS rational count relaxation; no integer vector claim except explicitly checked, graph realization, target automorphism or prism-free premise.',settings=dict(solver='simplex',presolve='off',threads=1,seed=0,feasibility_tolerance=1e-10,rational_max_individual_denominators=GRIDS,native_corner_limit=20),success='Every raw row/nonnegative coordinate for a primal or every raw column/strict RHS for a Farkas; separate independent artifact checker required.',falsification='Nonzero exact residual, negative primal or Farkas column, non-strict RHS, missing profile or encoding contradiction vetoes certificate.',restart='No automatic extension. Raw numerical vectors and per-corner basis files permit a separately authorized new versioned continuation.',independent_requirement='Different author checks raw certificates and all651 classifications; existing encoding audit does not approve producer certificates.'))
        controls(out)
        if args.controls_only:save(out/'summary.json',dict(status='UNRESTRICTED_ROOTED7_CORNER_DRIVER_CALIBRATION_PASS',elapsed_seconds=time.monotonic()-start,producer_calibration_only=True));return
        model=json.loads(MODEL.read_bytes());rows=model['equations'];columns=len(model['variables']);need(columns==2810 and len(rows)==11769,'exact operator dimensions')
        scales=[math.comb(97,5)if v[0]==7 else 71*20 for v in model['variables']]
        records=[];primals={};rays=[]
        for index,point in enumerate(CORNERS):
            need(not deadline.status()['stop_required'],'not completed within the allocated budget')
            seconds=min(20,(deadline.status()['remaining_seconds']-60)/(8-index));need(seconds>0,'corner reserve retained')
            record=guide(rows,columns,point,seconds,scales,out,f'corner_{index}');certify(rows,columns,record)
            save(out/f'corner_{index}.json',record);records.append(record)
            if record['status']=='CANDIDATE_EXACT_RATIONAL_PRIMAL':primals[point]=record
            elif record['status']=='CANDIDATE_EXACT_FARKAS_EXCLUSION':rays.append(record)
            print(json.dumps(dict(corner=list(point),status=record['status'],native_seconds=record['native_seconds'])),flush=True)
        outcomes=[];full=len(primals)==8
        with(out/'all651_rational_witnesses.jsonl').open('x',encoding='utf8',newline='\n')as stream:
            for point in tqdm(POPULATION,desc='651 frozen profile certificate checks',mininterval=5):
                need(not deadline.status()['stop_required'],'not completed within the allocated budget')
                excluded=[j for j,r in enumerate(rays)if sum(v*w for v,w in zip(r['certificate_rhs_affine'],[1,*point]))<0]
                row=dict(parameters=list(point),status='UNKNOWN_NO_EXACT_CERTIFICATE')
                if excluded:row.update(status='CANDIDATE_EXACT_FARKAS_EXCLUDED',ray_index=excluded[0])
                elif full:
                    ws=weights(point);den=math.lcm(*(w.denominator*primals[p]['certificate_denominator']for w,p in zip(ws,CORNERS)))
                    values=[sum(w.numerator*(den//(w.denominator*primals[p]['certificate_denominator']))*primals[p]['certificate_numerators'][j]for w,p in zip(ws,CORNERS))for j in range(columns)]
                    need(primal(rows,values,den,point),'complete all-row rational convex witness')
                    row.update(status='CANDIDATE_EXACT_RATIONAL_PRIMAL',integer_vector=all(v%den==0 for v in values));stream.write(json.dumps(dict(parameters=list(point),numerators=values,denominator=den,corner_weights=[[w.numerator,w.denominator]for w in ws]),separators=(',',':'))+'\n')
                elif point in primals:row.update(status='CANDIDATE_EXACT_RATIONAL_PRIMAL',corner_certificate=CORNERS.index(point),integer_vector=primals[point]['integer_vector'])
                outcomes.append(row)
        save(out/'all651_outcomes.json',outcomes)
        save(out/'summary.json',dict(status='CANDIDATE_UNRESTRICTED_ROOTED7_LITERAL_CORNER_RESULTS',timestamp=datetime.now(timezone.utc).isoformat(),frozen_corner_population=8,numerical_corner_attempts=len(records),exact_corner_primals=len(primals),exact_corner_farkas=len(rays),frozen_integer_parameter_population=651,actual_exact_convex_witnesses=sum(r['status']=='CANDIDATE_EXACT_RATIONAL_PRIMAL'for r in outcomes),exact_ray_excluded_profiles=sum(r['status']=='CANDIDATE_EXACT_FARKAS_EXCLUDED'for r in outcomes),unknown_profiles=sum(r['status']=='UNKNOWN_NO_EXACT_CERTIFICATE'for r in outcomes),integer_count_vectors=sum(r.get('integer_vector',False)for r in outcomes),complete_convex_certificate=full,independent_review=None,target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',elapsed_seconds=time.monotonic()-start,deadline=deadline.status(),outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-start,all_completed_outputs_preserved=True));raise


if __name__=='__main__':main()
