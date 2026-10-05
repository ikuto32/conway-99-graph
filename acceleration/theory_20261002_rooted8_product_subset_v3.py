"""Explicit weaker rooted8 product relaxation: calibrated scaled guides.

Only integer common-denominator certificates approve literal feasibility or
infeasibility. No implicit second LP is requested to manufacture a dual ray.
Every numerical solution/basis and completed corner is saved for manual resume.
"""
import argparse
from datetime import datetime, timezone
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
MODEL=ROOT/'acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
MODEL_SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'
SPEC=ROOT/'acceleration/theory_20261002_rooted8_product_subset_v3_spec.md'
CORNERS=[(0,0),(20,0),(0,9),(20,9)]
ROW_INDICES=list(range(11750))+list(range(82046,85874))


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def rhs(rows,point):
    a,b=point
    return [c+a*x+b*y for c,x,y in (row['rhs_affine'] for row in rows)]


def primal(rows,integers,denominator,point):
    return min(integers)>=0 and all(sum(coefficient*integers[j] for j,coefficient in row['terms'])==target*denominator for row,target in zip(rows,rhs(rows,point)))


def farkas(rows,columns,integers,point):
    products=[0]*columns;parameters=[0]*3
    for multiplier,row in zip(integers,rows):
        if not multiplier:continue
        for j,coefficient in row['terms']:products[j]+=multiplier*coefficient
        for j,coefficient in enumerate(row['rhs_affine']):parameters[j]+=multiplier*coefficient
    return min(products)>=0 and parameters[0]+point[0]*parameters[1]+point[1]*parameters[2]<0,parameters


def finite_values(values):
    return [float(value) if math.isfinite(value) else None for value in values]


def guide(rows,columns,point,seconds,scales,out,prefix,basis=None):
    phase_start=time.monotonic();rr=[];cc=[];vv=[];target=rhs(rows,point)
    for i,row in enumerate(rows):
        for j,coefficient in row['terms']:rr.append(i);cc.append(j);vv.append(coefficient)
    matrix=coo_matrix((vv,(rr,cc)),shape=(len(rows),columns),dtype=np.float64).tocsr()
    scaled=matrix.copy();scaled.data*=np.asarray(scales,dtype=np.float64)[scaled.indices]
    row_scales=np.maximum(np.maximum(np.asarray(abs(scaled).max(axis=1).toarray()).ravel(),abs(np.asarray(target,dtype=np.float64))),1)
    scaled.data/=np.repeat(row_scales,np.diff(scaled.indptr))
    lp=highspy.HighsLp();lp.num_col_=columns;lp.num_row_=len(rows)
    # Explicit deterministic names avoid writeBasis warning for unnamed models.
    lp.col_names_=[f'c{j}' for j in range(columns)];lp.row_names_=[f'r{i}' for i in range(len(rows))]
    lp.col_cost_=np.zeros(columns);lp.col_lower_=np.zeros(columns);lp.col_upper_=np.full(columns,highspy.kHighsInf)
    lp.row_lower_=lp.row_upper_=np.asarray(target,dtype=np.float64)/row_scales
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=scaled.indptr;lp.a_matrix_.index_=scaled.indices;lp.a_matrix_.value_=scaled.data
    highs=highspy.Highs()
    for name,value in [('output_flag',False),('threads',1),('random_seed',0),('solver','simplex'),('presolve','off'),
                       ('time_limit',seconds),('primal_feasibility_tolerance',1e-9),('dual_feasibility_tolerance',1e-9)]:
        need(highs.setOptionValue(name,value)==highspy.HighsStatus.kOk,'option '+name)
    need(highs.passModel(lp)==highspy.HighsStatus.kOk,'scaled literal subset model accepted')
    record=dict(parameters=list(point),column_scales=scales,row_scales=[int(value) for value in row_scales],
                matrix_preparation_seconds=time.monotonic()-phase_start,guide_seconds=seconds,
                numeric_settings=dict(solver='simplex',presolve='off',threads=1,seed=0,feasibility_tolerance=1e-9),
                scaling='x_original=column_scale*x_scaled; row_scaled=(A*x_original)/row_scale; y_original=y_scaled/row_scale',
                resumed_basis=None,status='NO_EXACT_CERTIFICATE',ray_exists=False)
    if basis:
        need(highs.readBasis(str(basis))==highspy.HighsStatus.kOk,'same-input basis reload')
        record['resumed_basis']=dict(path=str(basis.resolve()),sha256=sha(basis))
    phase_start=time.monotonic();run_status=highs.run();record['native_run_seconds']=time.monotonic()-phase_start
    record.update(run_status=str(run_status),model_status=str(highs.getModelStatus()))
    info=highs.getInfo();record['native_info']={name:getattr(info,name) for name in ['valid','simplex_iteration_count','num_primal_infeasibilities','num_dual_infeasibilities']}
    record['max_primal_infeasibility']=info.max_primal_infeasibility if math.isfinite(info.max_primal_infeasibility) else None
    record['max_primal_infeasibility_unavailable_reason']=None if math.isfinite(info.max_primal_infeasibility) else 'nonfinite native diagnostic'
    solution=highs.getSolution();record['numerical_values']=finite_values([value*scale for value,scale in zip(solution.col_value,scales)])
    record['numerical_values_scope']='Saved guide values at any returned status; never a certificate without exact replay.'
    if highs.getBasis().valid:
        basis_path=out/(prefix+'.bas');need(highs.writeBasis(str(basis_path))==highspy.HighsStatus.kOk,'basis checkpoint')
        record['saved_basis']=dict(path=str(basis_path.resolve()),sha256=sha(basis_path),mathematical_certificate=False)
    phase_start=time.monotonic();exist_status,exists=highs.getDualRayExist()
    record.update(ray_existence_status=str(exist_status),ray_exists=bool(exists),ray_existence_query_seconds=time.monotonic()-phase_start)
    if exists:
        phase_start=time.monotonic();ray_status,returned,ray=highs.getDualRay()
        record.update(ray_retrieval_status=str(ray_status),ray_retrieval_seconds=time.monotonic()-phase_start,
                      numerical_ray=finite_values([value/scale for value,scale in zip(ray,row_scales)]))
        need(returned,'stored ray retrieval; no implicit LP permitted')
    else:
        record['ray_retrieval_skipped_reason']='No stored ray; do not request an implicit extra LP.'
    return record


def certify(rows,columns,record):
    point=tuple(record['parameters']);attempts=[]
    numeric=record['numerical_values']
    if len(numeric)==columns and all(value is not None for value in numeric):
        for denominator in [1,10,1000,1000000]:
            integers=[round(value*denominator) for value in numeric];ok=primal(rows,integers,denominator,point)
            attempts.append(dict(kind='primal',common_denominator=denominator,exact_pass=ok))
            if ok:
                record.update(status='EXACT_WEAKER_RELAXATION_PRIMAL',certificate_integer_values=integers,
                              certificate_common_denominator=denominator,integer_vector=all(value%denominator==0 for value in integers));break
    if record['status']=='NO_EXACT_CERTIFICATE' and record.get('numerical_ray'):
        numeric=record['numerical_ray']
        if all(value is not None for value in numeric):
            magnitude=max(abs(value) for value in numeric)
            if magnitude:
                for denominator in [1,10,1000,1000000]:
                    integers=[round(value/magnitude*denominator) for value in numeric]
                    for sign in [1,-1]:
                        multipliers=[sign*value for value in integers];ok,parameters=farkas(rows,columns,multipliers,point)
                        attempts.append(dict(kind='farkas',common_grid_denominator=denominator,sign=sign,exact_pass=ok))
                        if ok:
                            record.update(status='EXACT_WEAKER_FARKAS_EXCLUSION',certificate_integer_multipliers=multipliers,
                                          certificate_rhs_affine=parameters);break
                    if record['status']!='NO_EXACT_CERTIFICATE':break
    record['exact_grid_attempts']=attempts


def controls(out):
    positive=[dict(terms=[[0,2]],rhs_affine=[1,0,0])]
    need(primal(positive,[1],2,(0,0)) and not primal(positive,[2],2,(0,0)),'positive/corrupt primal')
    negative=[dict(terms=[[0,1]],rhs_affine=[-1,0,0])]
    need(farkas(negative,1,[1],(0,0))[0] and not farkas(negative,1,[-1],(0,0))[0],'positive/corrupt Farkas')
    record=guide(negative,1,(0,0),10,[1],out,'control_negative')
    need(record['model_status']=='HighsModelStatus.kInfeasible' and record['ray_exists'],'presolve-off stored ray control')
    certify(negative,1,record);need(record['status']=='EXACT_WEAKER_FARKAS_EXCLUSION','actual stored ray replay')
    first=guide(positive,1,(0,0),10,[1],out,'control_positive')
    second=guide(positive,1,(0,0),10,[1],out,'control_reload',out/'control_positive.bas')
    certify(positive,1,second);need(second['status']=='EXACT_WEAKER_RELAXATION_PRIMAL','actual basis reload primal replay')
    bad=out/'corrupted_control.bas';bad.write_text('invalid basis\n',encoding='ascii')
    tiny=highspy.Highs();tiny.setOptionValue('output_flag',False)
    need(tiny.readBasis(str(bad))!=highspy.HighsStatus.kOk,'corrupt basis syntax rejected')
    save(out/'controls.json',dict(exact_primal_and_farkas_corruptions_rejected=True,negative=record,
                                 basis_reload=second,corrupt_basis_rejected=True,implicit_ray_solver_never_requested=True))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--controls-only',action='store_true');parser.add_argument('--resume',type=Path)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Explicit weaker15578-row root8 product subset; calibrated guides and exact integer-grid replay,60-second checkpoint/shutdown reserve')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(sha(MODEL)==MODEL_SHA,'frozen full raw model')
        pins={path.relative_to(ROOT).as_posix():sha(path) for path in [MODEL,SPEC,Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/command_deadline.py']}
        if args.resume:
            old=json.loads((args.resume/'manifest.json').read_bytes());need(old['inputs_sha256']==pins,'identical source/spec/model/environment resume closure')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python_version=platform.python_version(),highs_version=highspy.Highs().version(),
            selected_profiles=[[a,b] for a in range(21) for b in range(10)],selection='All210; four corner guides and exact convex/ray evaluation where available.',
            scope='Explicit weaker literal row subset; primals do not certify omitted constraints. Farkas zero-extends only after independent exact replay.',
            resume=None if not args.resume else str(args.resume.resolve()),restart='Same source/input closure --resume this_directory with fresh --out; basis reload is numerical warm-start only.',automatic_resume=False))
        save(out/'selected_original_row_indices.json',ROW_INDICES);controls(out)
        if args.controls_only:
            save(out/'summary.json',dict(status='ROOTED8_WEAKER_DRIVER_CONTROLS_PASS',elapsed_seconds=time.monotonic()-start,mathematical_scope='Engineering calibration only.'));return
        model=json.loads(MODEL.read_bytes());need(len(model['equations'])==85874 and len(model['variables'])==23019,'fixed full model dimensions')
        rows=[model['equations'][i] for i in ROW_INDICES];columns=len(model['variables']);cardinality={0:71,1:12,2:12,3:2}
        scales=[math.comb(97,v[0]-2) if v[0] in [7,8] else cardinality[v[2]]*(20 if v[3]==0 else 9) for v in model['variables']]
        corner_records=[];primals={};rays=[]
        for i,point in enumerate(CORNERS):
            need(deadline.status()['remaining_seconds']>60,'not completed within allocated budget')
            prefix=f'corner_{point[0]}_{point[1]}';basis=None
            if args.resume and (args.resume/(prefix+'.bas')).exists():basis=args.resume/(prefix+'.bas')
            seconds=(deadline.status()['remaining_seconds']-60)/(4-i)
            record=guide(rows,columns,point,seconds,scales,out,prefix,basis)
            exact_start=time.monotonic();certify(rows,columns,record);record['exact_replay_seconds']=time.monotonic()-exact_start
            save(out/(prefix+'.json'),record);corner_records.append(dict(parameters=list(point),status=record['status']))
            if record['status']=='EXACT_WEAKER_RELAXATION_PRIMAL':primals[point]=(record['certificate_integer_values'],record['certificate_common_denominator'])
            if record['status']=='EXACT_WEAKER_FARKAS_EXCLUSION':rays.append(record['certificate_rhs_affine'])
            print(json.dumps(corner_records[-1]),flush=True)
        outcomes=[]
        for a in tqdm(range(21),desc='all210 weaker exact outcomes',mininterval=5):
            for b in range(10):
                excluded=[i for i,(c,x,y) in enumerate(rays) if c+a*x+b*y<0]
                record=dict(parameters=[a,b],status='UNKNOWN_NO_EXACT_CERTIFICATE')
                if excluded:record.update(status='EXACT_WEAKER_RELAXATION_EXCLUDED',first_certificate=excluded[0])
                elif len(primals)==4:
                    weights=[(20-a)*(9-b),a*(9-b),(20-a)*b,a*b];denominator=math.lcm(*(den for _,den in primals.values()))*180
                    integers=[sum(weight*primals[corner][0][j]*(denominator//(180*primals[corner][1])) for weight,corner in zip(weights,CORNERS)) for j in range(columns)]
                    need(primal(rows,integers,denominator,(a,b)),'complete convex weaker row/nonnegativity replay')
                    record.update(status='EXACT_WEAKER_RELAXATION_PRIMAL',convex_integer_weights=weights,convex_weight_denominator=180)
                elif (a,b) in primals:record['status']='EXACT_WEAKER_RELAXATION_PRIMAL'
                outcomes.append(record)
        save(out/'all210_outcomes.json',outcomes)
        save(out/'summary.json',dict(status='CANDIDATE_ROOTED8_WEAKER_DIAGNOSTIC',timestamp=datetime.now(timezone.utc).isoformat(),
            selected_rows=len(rows),omitted_rows=85874-len(rows),variables=columns,selected_profiles=210,outcome_records_written=210,
            numerical_corner_attempts=len(corner_records),exact_corner_certificates=sum(r['status']!='NO_EXACT_CERTIFICATE' for r in corner_records),
            affine_certificate_applications=210*len(rays),complete_convex_row_replays=210 if len(primals)==4 else 0,
            corner_records=corner_records,exact_exclusions=sum(r['status']=='EXACT_WEAKER_RELAXATION_EXCLUDED' for r in outcomes),
            exact_weaker_primals=sum(r['status']=='EXACT_WEAKER_RELAXATION_PRIMAL' for r in outcomes),unknown=sum(r['status']=='UNKNOWN_NO_EXACT_CERTIFICATE' for r in outcomes),
            target_resolution='UNKNOWN',independent_review=None,elapsed_seconds=time.monotonic()-start,
            outputs_sha256={str(path.relative_to(ROOT)):sha(path) for path in out.iterdir() if path.is_file()}))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-start,automatic_resume=False,
            restart='Use unchanged source/spec/model and --resume this_directory under a fresh allocation; saved basis is numerical only.'));raise


if __name__=='__main__':main()
