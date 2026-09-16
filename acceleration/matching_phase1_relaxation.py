"""Numerical continuous relaxation diagnostic for the frozen matching model.

Exports the complete integer-coefficient matrix plus every primal value and
row/column dual. No dual bound or solver flag is treated as an exact proof.
Optional size-3/5 odd-set inequalities strengthen a 12-vertex same-sign class.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import highspy
import numpy as np
import scipy
from scipy.sparse import coo_matrix, vstack

from audit_certificate import require
from matching_phase1_mip import build_model, digest, path_key, finite_or_none, model_violation

ROOT=Path(__file__).resolve().parents[1]


def integer_or_none(values):
    result=[]
    for value in values:
        if np.isfinite(value):
            require(float(value).is_integer(),'Matrix export expected exact integer data')
            result.append(int(value))
        else:result.append(None)
    return result


def save(path,data):
    require(not path.exists(),'Preserve prior artifact')
    path.write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--root-group',type=int,required=True);parser.add_argument('--class',dest='matching_class',choices=['same_0','same_1','cross'],required=True)
    parser.add_argument('--seconds',type=float,default=30);parser.add_argument('--blossoms',action='store_true');args=parser.parse_args()
    require(np.isfinite(args.seconds) and 0<args.seconds<=3600,'Invalid seconds')
    require(not args.out.exists(),'Preserve prior diagnostic')
    require(not args.blossoms or args.matching_class!='cross','Blossom diagnostic is for same-sign classes')
    source_paths=[args.initial,Path(__file__),ROOT/'acceleration/matching_phase1_mip.py',ROOT/'acceleration/linear_probe.py',ROOT/'acceleration/audit_certificate.py']
    bindings={path_key(p):digest(p) for p in source_paths}
    started=time.perf_counter();candidate=json.loads(args.initial.read_bytes())
    model=build_model(candidate['overlap_edges_outer_zero_based'],args.root_group,args.matching_class,False)
    blossom_subsets=[]
    if args.blossoms:
        vertices=sorted(model['affected']);require(len(vertices)==12,'Expected12 same-sign vertices')
        rr=[];cc=[]
        for size in (3,5):
            for subset in combinations(vertices,size):
                index=len(blossom_subsets);chosen=set(subset);blossom_subsets.append(list(subset))
                for j,(u,v) in enumerate(model['matching_edges']):
                    if u in chosen and v in chosen:rr.append(index);cc.append(model['nx']+j)
        extra=coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(blossom_subsets),model['matrix'].shape[1])).tocsr()
        model['matrix']=vstack([model['matrix'],extra],format='csr')
        model['row_lower']=np.concatenate([model['row_lower'],np.full(len(blossom_subsets),-highspy.kHighsInf)])
        model['row_upper']=np.concatenate([model['row_upper'],np.array([(len(s)-1)//2 for s in blossom_subsets])])
        model['row_kinds']['same_sign_odd_set_3_5']=len(blossom_subsets)
    args.out.mkdir(parents=True)
    matrix=model['matrix'];matrix.sort_indices()
    matrix_path=args.out/'matrix.json'
    exported=dict(status='EXACT_INTEGER_COEFFICIENT_MATRIX_EXPORT',nrows=matrix.shape[0],ncols=matrix.shape[1],
                  csr_start=matrix.indptr.tolist(),csr_index=matrix.indices.tolist(),csr_value=integer_or_none(matrix.data),
                  row_lower=integer_or_none(model['row_lower']),row_upper=integer_or_none(model['row_upper']),
                  col_lower=integer_or_none(model['col_lower']),col_upper=integer_or_none(model['col_upper']),
                  col_cost=integer_or_none(model['costs']),all_columns_continuous=True,
                  bound_null_convention='A null lower bound means minus infinity; a null upper bound means plus infinity.',
                  row_kinds=model['row_kinds'],edge_variables=[list(e) for e in model['x_edges']],
                  matching_variables=[list(e) for e in model['matching_edges']],root_group=args.root_group,matching_class=args.matching_class,
                  column_order='1680 X; matching Y;840 quota excess;840 quota shortage;3486 shared pair-cap slacks',
                  blossom_subsets=blossom_subsets,
                  blossom_scope='Every selected odd subset S imposes sum(Y_e for e inside S)<=(|S|-1)/2. Size3/5 and degree-one equations imply complementary size9/7 inequalities on12vertices; sizes1/11 are trivial/complementary.',
                  inputs_sha256=bindings,
                  scope='Exact coefficients exported from the frozen producer, not independently established here. Continuous relaxation and optional mathematically valid matching cuts; no numerical proof claim.')
    save(matrix_path,exported)
    lp=highspy.HighsLp();lp.num_col_=matrix.shape[1];lp.num_row_=matrix.shape[0]
    lp.col_cost_=model['costs'];lp.col_lower_=model['col_lower'];lp.col_upper_=model['col_upper']
    lp.row_lower_=model['row_lower'];lp.row_upper_=model['row_upper'];lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=matrix.indptr;lp.a_matrix_.index_=matrix.indices;lp.a_matrix_.value_=matrix.data
    lp.integrality_=[highspy.HighsVarType.kContinuous]*matrix.shape[1]
    solver=highspy.Highs()
    for name,value in [('output_flag',False),('time_limit',args.seconds),('threads',1),('solver','ipm'),('run_crossover','off'),('random_seed',0)]:
        require(solver.setOptionValue(name,value)==highspy.HighsStatus.kOk,'Rejected option '+name)
    require(solver.passModel(lp)==highspy.HighsStatus.kOk,'Rejected diagnostic LP')
    build_seconds=time.perf_counter()-started
    print(json.dumps(dict(status='CONTINUOUS_MATCHING_LP_RUNNING',matching_class=args.matching_class,blossoms=args.blossoms,rows=matrix.shape[0],columns=matrix.shape[1])),flush=True)
    solve_started=time.perf_counter();run_status=solver.run();solve_seconds=time.perf_counter()-solve_started
    status,solution,info=solver.getModelStatus(),solver.getSolution(),solver.getInfo()
    valid_primal=solution.value_valid and len(solution.col_value)==matrix.shape[1] and np.all(np.isfinite(solution.col_value))
    valid_dual=solution.dual_valid and len(solution.row_dual)==matrix.shape[0] and np.all(np.isfinite(solution.row_dual))
    primal=np.array(solution.col_value) if valid_primal else None
    result=dict(status='CONTINUOUS_MATCHING_LP_NUMERICAL_DIAGNOSTIC',root_group=args.root_group,matching_class=args.matching_class,
                blossoms=args.blossoms,blossom_rows=len(blossom_subsets),matrix_path=path_key(matrix_path),matrix_sha256=digest(matrix_path),
                inputs_sha256=bindings,numerical_optimal=status==highspy.HighsModelStatus.kOptimal and run_status==highspy.HighsStatus.kOk,
                solver_run_status=str(run_status),solver_model_status=str(status),primal_solution_status=int(info.primal_solution_status),dual_solution_status=int(info.dual_solution_status),
                numeric_objective=finite_or_none(info.objective_function_value),
                numeric_recomputed_objective=float(model['costs']@primal) if valid_primal else None,
                numeric_maximum_primal_violation=model_violation(model,primal) if valid_primal else None,
                primal_values=primal.tolist() if valid_primal else None,
                row_duals=list(solution.row_dual) if valid_dual else None,column_duals=list(solution.col_dual) if valid_dual else None,
                dual_convention='HiGHS signed row marginals for row_lower<=A*x<=row_upper; reduced costs are c-A^T*row_dual.',
                ipm_iterations=int(info.ipm_iteration_count),seconds=args.seconds,model_build_seconds=build_seconds,
                solve_seconds=solve_seconds,elapsed_seconds=time.perf_counter()-started,highs_version=solver.version(),numpy_version=np.__version__,scipy_version=scipy.__version__,
                scope='Fractional Y relaxation diagnostic only. Positive or zero floating objectives and row duals are not certificates. No integral K candidate, exclusion or completed graph is asserted.')
    for p in source_paths:require(digest(p)==bindings[path_key(p)],'Source/input changed during diagnostic')
    save(args.out/'result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('primal_values','row_duals','column_duals','inputs_sha256')},allow_nan=False),flush=True)


if __name__=='__main__':main()
