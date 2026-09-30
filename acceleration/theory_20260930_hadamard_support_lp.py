"""A continuous fixed-support falsification test; exact certificates remain candidates."""
from datetime import datetime, timezone
from fractions import Fraction
from importlib.metadata import version
from itertools import combinations_with_replacement
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import time
import highspy
import numpy as np
from scipy.sparse import coo_matrix

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
RAW=B+'hadamard20_support/connected_01.json'
PIN='2e839fda408da18e3689ffef00de647644375a000d308f4ea306b2cbdfa37e49'
OUT=ROOT/(B+'hadamard_support_lp')


def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def save(name,obj):
    with (OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')


def solve(columns,rhs,seconds,log):
    ri=[r for col in columns for r in col];ci=[j for j,col in enumerate(columns) for _ in col]
    a=coo_matrix((np.ones(len(ri)),(ri,ci)),shape=(len(rhs),len(columns))).tocsr()
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=a.shape
    lp.col_cost_=np.zeros(len(columns));lp.col_lower_=np.zeros(len(columns));lp.col_upper_=np.full(len(columns),highspy.kHighsInf)
    lp.row_lower_=np.array(rhs,dtype=float);lp.row_upper_=np.array(rhs,dtype=float)
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
    solver=highspy.Highs()
    options=dict(solver='simplex',presolve='off',threads=1,random_seed=0,time_limit=seconds,
        primal_feasibility_tolerance=1e-7,dual_feasibility_tolerance=1e-7,log_to_console=False,output_flag=True,log_file=str(OUT/log))
    for k,v in options.items():assert solver.setOptionValue(k,v)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    started=time.monotonic();run_status=solver.run();elapsed=time.monotonic()-started
    status=solver.getModelStatus();solution=solver.getSolution()
    result=dict(run_status=str(run_status),model_status=str(status),wall_seconds=elapsed,options=options,
        solution_value_valid=solution.value_valid,solution_dual_valid=solution.dual_valid,
        primal=list(solution.col_value),row_dual=list(solution.row_dual),dual_ray=None)
    if status==highspy.HighsModelStatus.kInfeasible:
        ray_status,exists,ray=solver.getDualRay()
        result['dual_ray']=dict(status=str(ray_status),exists=bool(exists),values=list(ray))
    return result


def certify(columns,rhs,result):
    if result['model_status']=='HighsModelStatus.kOptimal' and result['solution_value_valid']:
        x=[Fraction(v).limit_denominator(1000000) for v in result['primal']]
        got=[Fraction(0)for _ in rhs]
        for value,col in zip(x,columns,strict=True):
            for row in col:got[row]+=value
        if min(x)>=0 and got==rhs:
            return dict(kind='EXACT_RATIONAL_PRIMAL_CANDIDATE',values=[[v.numerator,v.denominator]for v in x],
                interpretation='Only the continuous nonnegative Gram-selector relaxation is feasible.')
    ray=result.get('dual_ray')
    if ray and ray['exists']:
        y=[Fraction(v).limit_denominator(1000000)for v in ray['values']]
        for sign in [1,-1]:
            yy=[sign*v for v in y];left=[sum(yy[i]for i in col) for col in columns];right=sum(v*b for v,b in zip(yy,rhs,strict=True))
            if min(left)>=0 and right<0:
                return dict(kind='EXACT_RATIONAL_FARKAS_CANDIDATE',values=[[v.numerator,v.denominator]for v in yy],
                    minimum_column_dot=[min(left).numerator,min(left).denominator],rhs_dot=[right.numerator,right.denominator],
                    interpretation='Only this exact fixed-support continuous relaxation is infeasible.')
    return dict(kind='NO_EXACT_CERTIFICATE',reason='Numerical status or bounded-denominator reconstruction did not yield a checked exact certificate.')


def main():
    assert h(RAW)==PIN;OUT.mkdir(parents=True,exist_ok=False);now=datetime.now(timezone.utc).isoformat()
    paths=[RAW,Path(__file__).resolve().relative_to(ROOT).as_posix(),'acceleration/theory_20260930_hadamard_support_lp_spec.md','uv.lock','pyproject.toml']
    save('manifest.json',dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={p:h(p)for p in paths},python=platform.python_version(),
        versions={v:version(v)for v in ['highspy','numpy','scipy']},hardware=platform.uname()._asdict(),
        scope='Fixed connected01 Hadamard support; continuous nonnegative selector equality relaxation, no Ycaps or residualD.',
        selection='First support passing all frozen cheap screens in connected00,01,02,03,six_prism order.',
        limits=dict(research_attempts=1,solver_seconds=30,threads=1,automatic_retry=False),
        numerical_acceptance='No numerical value is a proof; exact rational reconstruction and separate checking required.'))
    controls=[]
    for label,columns,rhs,expected in [('feasible',[[0],[0]],[1],'EXACT_RATIONAL_PRIMAL_CANDIDATE'),('infeasible',[[0,1]],[0,1],'EXACT_RATIONAL_FARKAS_CANDIDATE')]:
        r=solve(columns,rhs,3,'control_'+label+'.log');c=certify(columns,rhs,r);assert c['kind']==expected
        controls.append(dict(label=label,columns=columns,rhs=rhs,result=r,certificate=c))
    save('controls.json',controls)
    raw=json.loads((ROOT/RAW).read_bytes());pairs=list(combinations_with_replacement(range(36),2));index={p:60+i for i,p in enumerate(pairs)}
    rhs=[1]*60+[raw['prescribed_Gram36'][a][b]for a,b in pairs];columns=[];selectors=[]
    for d,options in enumerate(raw['column_colour_options']):
        assert options
        for j,option in enumerate(options):
            rows=option['rows'];assert len(rows)==len(set(rows))==6
            columns.append([d]+[index[p]for p in combinations_with_replacement(rows,2)])
            selectors.append([d,j])
    assert len(rhs)==726
    save('exact_model.json',dict(nonnegative_variables=True,columns_nonzero_row_indices=columns,rhs=rhs,selectors=selectors,
        Gram_row_pairs=[list(p)for p in pairs],variables=len(columns),equations=len(rhs),binary_coefficients=True))
    result=solve(columns,rhs,30,'solver.log');save('numerical_result.json',result)
    certificate=certify(columns,rhs,result);save('certificate.json',certificate)
    summary=dict(status='CANDIDATE_FIXED_HADAMARD_SUPPORT_LP_OUTCOME',timestamp=datetime.now(timezone.utc).isoformat(),
        model_status=result['model_status'],certificate_kind=certificate['kind'],variables=len(columns),equations=len(rhs),
        research_calls=1,solver_wall_seconds=result['wall_seconds'],producer_controls=len(controls),
        outputs_sha256={p.relative_to(ROOT).as_posix():h(p.relative_to(ROOT))for p in OUT.iterdir()if p.is_file()},
        independent_approval=False,target_resolution='UNKNOWN',limitations=['No integer factor, cap feasibility or residual graph is inferred from a feasible LP.','An exact Farkas candidate still requires an independent matrix/scope and rational check.'])
    save('summary.json',summary);print(json.dumps({k:summary[k]for k in ['status','model_status','certificate_kind','variables','equations','solver_wall_seconds']}))


if __name__=='__main__':main()
