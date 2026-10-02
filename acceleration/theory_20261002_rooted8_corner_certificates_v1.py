"""Four LP corner guides, exact certificates, and all210 profile checks.

Numerical optimization never certifies a claim. Primal or Farkas vectors are
rationalized and checked on every exact integer row/column. If all rectangle
corners have exact nonnegative rational primals, explicitly reconstruct and
check all210 profiles by convex combinations. No graph realization is asserted.
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

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
MODEL_SHA = 'a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'
CALIBRATION = ROOT/'acceleration/results/20261002_rooted8_product_calibration01/summary.json'
CALIBRATION_SHA = 'd351ab8188861f0a847e0558345fb7b4f6e250e32533110dc6fdc73f6b8be95d'
CORNERS = [(0,0), (20,0), (0,9), (20,9)]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def rhs(rows, point):
    a, b = point
    return [constant+a*left+b*right for constant, left, right in (row['rhs_affine'] for row in rows)]


def primal_ok(rows, values, point):
    target = rhs(rows, point)
    if min(values) < 0:
        return False
    denominator = math.lcm(*(value.denominator for value in values))
    integers = [value.numerator*(denominator//value.denominator) for value in values]
    return all(sum(coefficient*integers[j] for j, coefficient in row['terms']) == target[i]*denominator for i, row in enumerate(rows))


def farkas_ok(rows, columns, vector, point):
    products = [Fraction(0)]*columns
    parameters = [Fraction(0)]*3
    for value, row in zip(vector, rows):
        if not value:
            continue
        for j, coefficient in row['terms']:
            products[j] += value*coefficient
        for j, coefficient in enumerate(row['rhs_affine']):
            parameters[j] += value*coefficient
    return min(products) >= 0 and parameters[0]+point[0]*parameters[1]+point[1]*parameters[2] < 0, products, parameters


def solver(rows, columns, target, seconds, column_scales=None):
    rr, cc, vv = [], [], []
    for i, row in enumerate(rows):
        for j, coefficient in row['terms']:
            rr.append(i); cc.append(j); vv.append(coefficient)
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(rows), columns), dtype=np.float64).tocsr()
    scales=np.asarray(column_scales if column_scales is not None else [1]*columns,dtype=np.float64)
    scaled=matrix.copy();scaled.data*=scales[scaled.indices]
    row_scales=np.maximum(np.maximum(np.asarray(abs(scaled).max(axis=1).toarray()).ravel(),abs(np.asarray(target,dtype=np.float64))),1)
    scaled.data/=np.repeat(row_scales,np.diff(scaled.indptr))
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = columns, len(rows)
    lp.col_cost_ = np.zeros(columns)
    lp.col_lower_, lp.col_upper_ = np.zeros(columns), np.full(columns, highspy.kHighsInf)
    lp.row_lower_ = lp.row_upper_ = np.asarray(target, dtype=np.float64)/row_scales
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = scaled.indptr, scaled.indices, scaled.data
    highs = highspy.Highs()
    for name, value in [('output_flag', False), ('threads', 1), ('random_seed', 0), ('solver', 'simplex'),
                        ('time_limit', seconds), ('primal_feasibility_tolerance', 1e-10), ('dual_feasibility_tolerance', 1e-10)]:
        need(highs.setOptionValue(name, value) == highspy.HighsStatus.kOk, 'solveroption ' + name)
    need(highs.passModel(lp) == highspy.HighsStatus.kOk, 'numerical exact integer model accepted')
    start = time.monotonic(); status = highs.run()
    return highs, dict(run_status=str(status), model_status=str(highs.getModelStatus()), numerical_seconds=time.monotonic()-start,
        highs_version=highs.version(), guide_seconds=seconds, numeric_feasibility_tolerance=1e-10,
        column_scales=[int(value) for value in scales],row_scales=[int(value) for value in row_scales],
        scaling='x_original=diag(column_scales)*x_scaled; A_scaled=diag(1/row_scales)*A_original*diag(column_scales); b_scaled=b_original/row_scales; y_original=y_scaled/row_scales.')


def lift_primal(rows, numeric, point):
    if not all(math.isfinite(value) for value in numeric):
        return None, []
    attempts = []
    for denominator in [1, 10, 1000, 1000000]:
        values = [Fraction(value).limit_denominator(denominator) for value in numeric]
        accepted = primal_ok(rows, values, point)
        attempts.append(dict(max_denominator=denominator, exact_all_rows=accepted,
            max_numeric_adjustment=max(abs(float(exact)-original) for exact, original in zip(values, numeric))))
        if accepted:
            return values, attempts
    return None, attempts


def lift_farkas(rows, columns, numeric, point):
    if not numeric or not all(math.isfinite(value) for value in numeric):
        return None, [], None
    magnitude = max(abs(value) for value in numeric)
    if not magnitude:
        return None, [], None
    attempts = []
    for denominator in [1, 10, 1000, 1000000]:
        values = [Fraction(value/magnitude).limit_denominator(denominator) for value in numeric]
        for sign in [1, -1]:
            vector = [value*sign for value in values]
            accepted, _, parameters = farkas_ok(rows, columns, vector, point)
            attempts.append(dict(max_denominator=denominator, sign=sign, exact_all_columns_and_strict_rhs=accepted))
            if accepted:
                return vector, attempts, parameters
    return None, attempts, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--resume', type=Path, help='Prior exact same-source corner directory; recheck and reuse exact certificates only')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Four23019var85874row968172nonzero LP corner guides, exact certificate lifts and210 convex profiles; reserve120 seconds for exact checking/checkpoints and shutdown.')
    out=args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start=time.monotonic()
    try:
        need(sha(MODEL) == MODEL_SHA and sha(CALIBRATION) == CALIBRATION_SHA, 'frozen exact model and pre-optimization calibration')
        need(json.loads(CALIBRATION.read_bytes())['status'] == 'RAW_ROOTED8_PRODUCT_CALIBRATION_PASS','pre-optimization calibration passed; not independent approval')
        model=json.loads(MODEL.read_bytes()); rows=model['equations']; columns=len(model['variables'])
        if args.resume:
            prior_manifest=json.loads((args.resume/'manifest.json').read_bytes())
            need(prior_manifest['inputs_sha256'][MODEL.relative_to(ROOT).as_posix()] == MODEL_SHA and
                 prior_manifest['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()] == sha(Path(__file__)),
                 'resume requires identical source and model bytes')
        cardinalities={0:71,1:12,2:12,3:2}
        column_scales=[math.comb(97,variable[0]-2) if variable[0] in [7,8] else cardinalities[variable[2]]*(20 if variable[3]==0 else 9)
                       for variable in model['variables']]
        save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT), python_version=platform.python_version(),
            numpy_version=np.__version__,highspy_version=highspy.Highs().version(),
            inputs_sha256={MODEL.relative_to(ROOT).as_posix():MODEL_SHA,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
                CALIBRATION.relative_to(ROOT).as_posix():CALIBRATION_SHA,
                'pyproject.toml':sha(ROOT/'pyproject.toml'),'uv.lock':sha(ROOT/'uv.lock')},
            corners=[list(point) for point in CORNERS], selected_profile_population=[[a,b] for a in range(21) for b in range(10)],
            resume_directory=None if not args.resume else str(args.resume.resolve()),automatic_resume=False,
            restart='Invoke this exact source with --resume this output directory, a fresh --out and newly declared contained allocation. Previously exact corners are fully rechecked; other attempts remain preserved and may be retried.',
            selection_rule='All four rectangle corners; if exactly feasible, explicit nonnegative convex witnesses cover and are checked on all210 profiles. Every point is tested against any exactFarkascut.',
            scope='Conditional continuous rooted8 extension/universal5 product relaxation; model necessity pending independent audit, no graph realization.',
            success_criterion='Primalcertificates check every exactrow and nonnegativity; Farkaschecks every exactcolumn andstrict negative RHS; all210 individually certified or recordedunknown.',
            falsification_criterion='Any nonzero exactprimal residual, negative coordinate, invalid ray or missingpoint vetoes certificate; floatingstatus alone remains diagnostic.',
            numerical_acceptance='No floating certificate threshold; exact checks decide. HiGHS feasibility tolerance1e-10 guides only; exact integer row/column scales preserved.',
            independent_verification_requirement='Separate rawvector/checker and catalogue/modelderivation review before promotion.'))
        tiny=[dict(terms=[[0,2]],rhs_affine=[1,0,0])]
        need(primal_ok(tiny,[Fraction(1,2)],(0,0)) and not primal_ok(tiny,[Fraction(1)],(0,0)), 'exact primal positive/corruptcontrol')
        infeasible=[dict(terms=[[0,1]],rhs_affine=[-1,0,0])]
        need(farkas_ok(infeasible,1,[Fraction(1)],(0,0))[0] and not farkas_ok(infeasible,1,[Fraction(-1)],(0,0))[0], 'exact Farkas positive/corruptcontrol')
        control_solver, control_record=solver(infeasible,1,[-1],deadline.child_seconds(15,reserve_seconds=120))
        need(control_solver.getModelStatus() == highspy.HighsModelStatus.kInfeasible,'tiny numericalnegativecontrol')
        _, control_exists, control_ray=control_solver.getDualRay()
        need(control_exists and lift_farkas(infeasible,1,[value/scale for value,scale in zip(control_ray,control_record['row_scales'])],(0,0))[0] is not None,'actualraycontrol')
        save(out/'controls.json',dict(exact_primal_and_farkas_corruptions_rejected=True, actual_numeric_ray=control_record))
        corner_results, exact_primals, exact_rays=[],{},[]
        for index, point in enumerate(CORNERS):
            need(not deadline.status()['stop_required'],'not completed within the allocated budget')
            if args.resume and (args.resume/f'corner_{point[0]}_{point[1]}.json').exists():
                prior_path=args.resume/f'corner_{point[0]}_{point[1]}.json'
                record=json.loads(prior_path.read_bytes())
                if record['status'] == 'EXACT_NONNEGATIVE_RATIONAL_PRIMAL':
                    exact=[Fraction(numerator,denominator) for numerator,denominator in record['exact_values']]
                    need(len(exact)==columns and primal_ok(rows,exact,point),'complete resumed primal replay')
                    exact_primals[point]=exact
                elif record['status'] == 'EXACT_FARKAS_EXCLUSION':
                    exact=[Fraction(numerator,denominator) for numerator,denominator in record['exact_ray']]
                    need(len(exact)==len(rows),'complete resumed ray length')
                    valid,_,parameters=farkas_ok(rows,columns,exact,point)
                    need(valid,'complete resumed Farkas replay')
                    exact_rays.append((exact,parameters))
                else:
                    record=None
                if record is not None:
                    record['resumed_from']=dict(path=str(prior_path.resolve()),sha256=sha(prior_path),complete_exact_recheck=True)
                    save(out/f'corner_{point[0]}_{point[1]}.json',record)
                    corner_results.append(dict(parameters=list(point),status=record['status'],numerical_seconds=0,resumed_exact_certificate=True))
                    print(json.dumps(corner_results[-1]),flush=True)
                    continue
            # A guide may use the currently available invocation remainder;
            # later exact checks and allfuturecorners retain their fair share.
            available=max(.001,deadline.status()['remaining_seconds']-120)
            guide=available/(len(CORNERS)-index)
            highs,record=solver(rows,columns,rhs(rows,point),guide,column_scales)
            record.update(parameters=list(point),status='NO_EXACT_CERTIFICATE',primal_lifting_attempts=[],farkas_lifting_attempts=[])
            if highs.getModelStatus() == highspy.HighsModelStatus.kOptimal:
                numeric=[value*scale for value,scale in zip(highs.getSolution().col_value,record['column_scales'])]
                record['numerical_values']=numeric
                exact,attempts=lift_primal(rows,numeric,point); record['primal_lifting_attempts']=attempts
                if exact is not None:
                    exact_primals[point]=exact
                    record.update(status='EXACT_NONNEGATIVE_RATIONAL_PRIMAL',
                        exact_values=[[value.numerator,value.denominator] for value in exact],
                        integer_vector=all(value.denominator==1 for value in exact))
            elif highs.getModelStatus() == highspy.HighsModelStatus.kInfeasible:
                ray_status,exists,ray=highs.getDualRay(); record.update(ray_status=str(ray_status),ray_exists=bool(exists))
                if exists:
                    numeric=[value/scale for value,scale in zip(ray,record['row_scales'])]; record['numerical_ray']=numeric
                    exact,attempts,parameters=lift_farkas(rows,columns,numeric,point); record['farkas_lifting_attempts']=attempts
                    if exact is not None:
                        exact_rays.append((exact,parameters))
                        record.update(status='EXACT_FARKAS_EXCLUSION',
                            exact_ray=[[value.numerator,value.denominator] for value in exact],
                            exact_rhs_affine=[[value.numerator,value.denominator] for value in parameters])
            save(out/f'corner_{point[0]}_{point[1]}.json',record)
            corner_results.append(dict(parameters=list(point),status=record['status'],numerical_seconds=record['numerical_seconds']))
            print(json.dumps(corner_results[-1]),flush=True)
        all210=[]
        complete_convex=len(exact_primals)==4
        for a in tqdm(range(21),desc='all210 exact certificate evaluations',mininterval=5):
            need(not deadline.status()['stop_required'],'not completed within the allocated budget')
            for b in range(10):
                point=(a,b)
                excluded=[i for i,(_,coefficients) in enumerate(exact_rays) if coefficients[0]+a*coefficients[1]+b*coefficients[2]<0]
                record=dict(parameters=[a,b],status='UNKNOWN_NO_EXACT_CERTIFICATE',first_farkas_exclusion=None)
                if excluded:
                    record.update(status='EXACT_NECESSARY_RELAXATION_EXCLUDED',first_farkas_exclusion=excluded[0])
                elif complete_convex:
                    weights=[Fraction((20-a)*(9-b),180),Fraction(a*(9-b),180),Fraction((20-a)*b,180),Fraction(a*b,180)]
                    need(sum(weights)==1 and sum(weight*corner[0] for weight,corner in zip(weights,CORNERS))==a
                         and sum(weight*corner[1] for weight,corner in zip(weights,CORNERS))==b,'exact convexparameterbinding')
                    vector=[sum(weight*exact_primals[corner][j] for weight,corner in zip(weights,CORNERS)) for j in range(columns)]
                    need(primal_ok(rows,vector,point),'every210exactprimal row/nonnegativecoordinate')
                    record.update(status='EXACT_NONNEGATIVE_RATIONAL_RELAXATION_PRIMAL',
                        convex_weights=[[weight.numerator,weight.denominator] for weight in weights],
                        integer_vector=all(value.denominator==1 for value in vector))
                elif point in exact_primals:
                    record.update(status='EXACT_NONNEGATIVE_RATIONAL_RELAXATION_PRIMAL',corner_certificate=list(point))
                all210.append(record)
        save(out/'all210_outcomes.json',all210)
        summary=dict(status='CANDIDATE_EXACT_ROOTED8_CORNER_CERTIFICATES',timestamp=datetime.now(timezone.utc).isoformat(),
            selected_profiles=210,completed_certificate_evaluations=210,numerical_corner_attempts=4,
            corner_results=corner_results,complete_convex_certificate=complete_convex,
            exact_rational_primals=sum(row['status']=='EXACT_NONNEGATIVE_RATIONAL_RELAXATION_PRIMAL' for row in all210),
            exact_exclusions=sum(row['status']=='EXACT_NECESSARY_RELAXATION_EXCLUDED' for row in all210),
            unknown=sum(row['status']=='UNKNOWN_NO_EXACT_CERTIFICATE' for row in all210),
            integer_vectors=sum(row.get('integer_vector',False) for row in all210),
            target_resolution='UNKNOWN',graph_realizability_asserted=False,independent_review=None,
            independent_review_reason='Rawcorner/convex/Farkas certificates and modelcoverage/derivation require separate check.',
            elapsed_seconds=time.monotonic()-start,
            outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json',summary); print(json.dumps(summary),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-start,target_resolution='UNKNOWN'));raise


if __name__=='__main__':
    main()
