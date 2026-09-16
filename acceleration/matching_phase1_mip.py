"""Bounded whole-matching phase-I candidate producer using compact M=1 rows.

Public solve_matching(edges, root_group, matching_class, seconds=30,
                     initial_x=None, fix_initial=False) returns JSON data.
MIP objectives, bounds, gaps and statuses are numerical diagnostics, never
certificates. One matching is binary; the 1,680 disjoint edges stay fractional.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import isfinite
from pathlib import Path
import sys
import time

import highspy
import numpy as np
import scipy
from scipy.sparse import coo_matrix

from audit_certificate import full_graph, require
from linear_probe import constraints

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ('same_0','same_1','cross')


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def path_key(path):
    path=path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def canonical(u,v):
    return (u,v) if u<v else (v,u)


def edge_digest(edges):
    return sha256(json.dumps(sorted(map(list,edges)),separators=(',',':')).encode('ascii')).hexdigest()


def finite_or_none(value):
    result=float(value)
    return result if isfinite(result) else None


def evaluate_fixed(edges,x,outer_pairs):
    """Use the frozen fixed-K builder, independent of this model assembly."""
    adjacency,_=full_graph({'overlap_edges_outer_zero_based':[list(e) for e in sorted(edges)]})
    columns,groups,neq,matrix,target=constraints(set(edges))
    require(neq==840,'Unexpected fixed-K quota count')
    residual=np.asarray(matrix@x-target)
    quotas=residual[:neq]
    caps=np.array([len(adjacency[u+15]&adjacency[v+15])+int(v+15 in adjacency[u+15])-2
                   for u,v in outer_pairs],dtype=float)
    index={p:i for i,p in enumerate(outer_pairs)}
    for row,group in enumerate(groups[neq:],neq):
        caps[index[tuple(group['coordinate'])]]=residual[row]
    excess=np.maximum(quotas,0);shortage=np.maximum(-quotas,0);violation=np.maximum(caps,0)
    return dict(objective=float(excess.sum()+shortage.sum()+violation.sum()),
                quota_residuals=quotas,cap_residuals=caps,
                quota_excess=excess,quota_shortage=shortage,cap_violation=violation,
                columns=columns)


def build_model(edges,root_group,matching_class,fix_initial=False):
    listed=[list(e) for e in edges]
    adjacency,unknown=full_graph({'overlap_edges_outer_zero_based':listed})
    require(type(root_group) is int and 0<=root_group<7,'root_group must be in 0..6')
    require(matching_class in CLASSES,'Invalid matching class')
    original=set(map(tuple,listed))
    labels=[{(s-1)//2:(s-1)%2 for s in adjacency[u+15] if 1<=s<=14} for u in range(84)]
    cohort={u for u in range(84) if root_group in labels[u]}
    affected=cohort if matching_class=='cross' else {u for u in cohort if labels[u][root_group]==int(matching_class[-1])}
    matching_edges=[]
    for u,v in combinations(sorted(affected),2):
        if len(set(labels[u])&set(labels[v]))!=1:continue
        opposite=labels[u][root_group]!=labels[v][root_group]
        if opposite != (matching_class=='cross'):continue
        matching_edges.append((u,v))
    expected_choices=120 if matching_class=='cross' else 60
    require(len(matching_edges)==expected_choices,'Unexpected matching choice count')
    initial_matching=original&set(matching_edges)
    require(len(initial_matching)==len(affected)//2 and
            Counter(u for edge in initial_matching for u in edge)==Counter({u:1 for u in affected}),
            'Initial chosen class is not a perfect matching')
    base=[set(row) for row in adjacency]
    for u,v in initial_matching:base[u+15].remove(v+15);base[v+15].remove(u+15)
    x_edges=sorted((u-15,v-15) for u,v in unknown)
    x_index={(u+15,v+15):i for i,(u,v) in enumerate(x_edges)}
    nx,nz=len(x_edges),len(matching_edges)
    require(nx==1680,'Unexpected X dimension')
    z_index={(u+15,v+15):nx+i for i,(u,v) in enumerate(matching_edges)}
    partners={u+15:[] for u in affected}
    for u,v in z_index:partners[u].append(v);partners[v].append(u)
    quotas=[(u+15,s+1) for u in range(84) for s in range(14) if s//2 not in labels[u]]
    require(len(quotas)==840,'Unexpected foreign-label quota count')
    outer_pairs=list(combinations(range(84),2))
    qplus=nx+nz;qminus=qplus+840;cap_start=qminus+840;ncols=cap_start+3486
    rr=[];cc=[];vv=[];lower=[];upper=[];row_kinds=Counter()

    def row(coefficients,lo,hi,kind):
        index=len(lower)
        for c,value in coefficients.items():
            if value:rr.append(index);cc.append(c);vv.append(value)
        lower.append(lo);upper.append(hi);row_kinds[kind]+=1

    def add_variable(coefficients,index,u,v):
        if u!=v:
            column=index.get(canonical(u,v))
            if column is not None:coefficients[column]+=1

    def partial_z(u,v):
        co=Counter();add_variable(co,z_index,u,v)
        for w in base[v]:add_variable(co,z_index,u,w)
        for w in base[u]:add_variable(co,z_index,v,w)
        return co

    # Symmetric degree one gives an injective partner map; Z_u intersect Z_v=empty.
    for u in sorted(partners):row({z_index[canonical(u,v)]:1 for v in partners[u]},1,1,'matching_degree')
    affected_full={u+15 for u in affected}
    for u,v in combinations(range(99),2):
        if u not in affected_full and v not in affected_full:continue
        rhs=2-len(base[u]&base[v])-int(v in base[u])
        row(partial_z(u,v),-highspy.kHighsInf,rhs,'hard_partial_cap')

    for i,(u,s) in enumerate(quotas):
        co=Counter()
        for w in base[s]:
            add_variable(co,x_index,u,w);add_variable(co,z_index,u,w)
        co[qplus+i]=-1;co[qminus+i]=1
        rhs=2-len(base[u]&base[s])
        row(co,rhs,rhs,'foreign_label_quota')

    cohort_full={u+15 for u in cohort}
    for i,(outer_u,outer_v) in enumerate(outer_pairs):
        u,v=outer_u+15,outer_v+15
        constant=len(base[u]&base[v])+int(v in base[u])
        co=Counter();add_variable(co,x_index,u,v)
        for w in base[u]:add_variable(co,x_index,v,w)
        for w in base[v]:add_variable(co,x_index,u,w)
        co[cap_start+i]=-1
        nonlinear=(u in affected_full and v not in cohort_full) or (v in affected_full and u not in cohort_full)
        if not nonlinear:
            co.update(partial_z(u,v))
            row(co,-highspy.kHighsInf,2-constant,'linear_completion_cap')
            continue
        active,other=(u,v) if u in affected_full else (v,u)
        # Baseline H<=2+t. One shared t for all partner indicators for this pair.
        row(co,-highspy.kHighsInf,2-constant,'completion_cap_baseline')
        for w in partners[active]:
            indicator=co.copy()
            add_variable(indicator,x_index,other,w)
            indicator[z_index[canonical(active,w)]]+=1
            row(indicator,-highspy.kHighsInf,3-constant-int(w in base[other]),'completion_cap_indicator_M1')

    matrix=coo_matrix((vv,(rr,cc)),shape=(len(lower),ncols)).tocsr()
    costs=np.concatenate([np.zeros(nx+nz),np.ones(2*840+3486)])
    col_lower=np.zeros(ncols);col_upper=np.concatenate([np.ones(nx+nz),np.full(2*840+3486,highspy.kHighsInf)])
    initial_z=np.array([int(edge in initial_matching) for edge in matching_edges],dtype=float)
    if fix_initial:col_lower[nx:nx+nz]=initial_z;col_upper[nx:nx+nz]=initial_z
    return dict(matrix=matrix,costs=costs,col_lower=col_lower,col_upper=col_upper,
                row_lower=np.array(lower),row_upper=np.array(upper),row_kinds=dict(row_kinds),
                original=original,initial_matching=initial_matching,matching_edges=matching_edges,
                affected=affected,x_edges=x_edges,outer_pairs=outer_pairs,quotas=quotas,
                initial_z=initial_z,nx=nx,nz=nz,qplus=qplus,qminus=qminus,cap_start=cap_start)


def model_violation(model,values):
    activity=np.asarray(model['matrix']@values)
    return float(max(np.max(model['row_lower']-activity,initial=0),np.max(activity-model['row_upper'],initial=0),
                     np.max(model['col_lower']-values,initial=0),np.max(values-model['col_upper'],initial=0)))


def pack_values(model,x,z,evaluation):
    return np.concatenate([x,z,evaluation['quota_excess'],evaluation['quota_shortage'],evaluation['cap_violation']])


def solve_matching(edges,root_group,matching_class,seconds=30,initial_x=None,fix_initial=False):
    require(not sys.flags.optimize,'Run without -O')
    require(type(seconds) in (int,float) and isfinite(seconds) and 0<seconds<=3600,'seconds must be in (0,3600]')
    require(type(fix_initial) is bool,'fix_initial must be boolean')
    started=time.perf_counter();model=build_model(edges,root_group,matching_class,fix_initial)
    nx,nz=model['nx'],model['nz']
    initial_vector=np.zeros(nx) if initial_x is None else np.asarray(initial_x,dtype=float)
    require(initial_vector.shape==(nx,) and np.all(np.isfinite(initial_vector)) and
            np.all((initial_vector>=0)&(initial_vector<=1)),'Initial X must contain 1680 finite values in [0,1]')
    initial_eval=evaluate_fixed(model['original'],initial_vector,model['outer_pairs'])
    require(initial_eval['columns']==model['x_edges'],'X order mismatch')
    warm=pack_values(model,initial_vector,model['initial_z'],initial_eval)
    warm_violation=model_violation(model,warm)
    require(warm_violation<=1e-7,'Initial known-feasible incumbent violates compact model')
    lp=highspy.HighsLp();lp.num_col_=len(warm);lp.num_row_=model['matrix'].shape[0]
    lp.col_cost_=model['costs'];lp.col_lower_=model['col_lower'];lp.col_upper_=model['col_upper']
    lp.row_lower_=model['row_lower'];lp.row_upper_=model['row_upper']
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=model['matrix'].indptr;lp.a_matrix_.index_=model['matrix'].indices;lp.a_matrix_.value_=model['matrix'].data
    lp.integrality_=[highspy.HighsVarType.kContinuous]*len(warm)
    if not fix_initial:
        integrality=list(lp.integrality_)
        integrality[nx:nx+nz]=[highspy.HighsVarType.kInteger]*nz
        lp.integrality_=integrality
    solver=highspy.Highs()
    options=[('output_flag',False),('time_limit',float(seconds)),('threads',1),('random_seed',0)]
    options += [('solver','ipm'),('run_crossover','off')] if fix_initial else [('mip_rel_gap',0.0001),('mip_abs_gap',0.000001)]
    for name,value in options:require(solver.setOptionValue(name,value)==highspy.HighsStatus.kOk,'Rejected option '+name)
    require(solver.passModel(lp)==highspy.HighsStatus.kOk,'HiGHS rejected model')
    warm_solution=highspy.HighsSolution();warm_solution.col_value=warm.tolist();warm_solution.value_valid=True
    warm_status=solver.setSolution(warm_solution)
    require(warm_status==highspy.HighsStatus.kOk,'HiGHS rejected initial incumbent')
    build_seconds=time.perf_counter()-started;solve_started=time.perf_counter()
    run_status=solver.run();solve_seconds=time.perf_counter()-solve_started
    status=solver.getModelStatus();solution=solver.getSolution();info=solver.getInfo()
    chosen_edges=model['original'];chosen_x=initial_vector;chosen_z=model['initial_z'];chosen_eval=initial_eval
    chosen_origin='INITIAL_INCUMBENT';rejection=None;raw_values=None;raw_matching=None;raw_model_violation=None;z_error=None;projection=None
    if solution.value_valid and len(solution.col_value)==len(warm) and np.all(np.isfinite(solution.col_value)):
        raw_values=np.asarray(solution.col_value,dtype=float);raw_matching=raw_values[nx:nx+nz]
        rounded=np.rint(raw_matching);z_error=float(np.max(np.abs(raw_matching-rounded),initial=0))
        raw_model_violation=model_violation(model,raw_values)
        if z_error<=1e-5 and np.all((rounded>=0)&(rounded<=1)) and raw_model_violation<=1e-5:
            selected={edge for edge,value in zip(model['matching_edges'],rounded) if value==1}
            proposed=(model['original']-model['initial_matching'])|selected
            try:
                full_graph({'overlap_edges_outer_zero_based':[list(e) for e in sorted(proposed)]})
                require(Counter(u for edge in selected for u in edge)==Counter({u:1 for u in model['affected']}),'Rounded matching invalid')
                clipped=np.clip(raw_values[:nx],0,1);projection=float(np.max(np.abs(clipped-raw_values[:nx]),initial=0))
                evaluated=evaluate_fixed(proposed,clipped,model['outer_pairs'])
                reconstructed=pack_values(model,clipped,rounded,evaluated)
                require(model_violation(model,reconstructed)<=1e-7,'Projected candidate does not satisfy compact model')
                require(evaluated['objective']<=float(model['costs']@raw_values)+1e-5*max(1,evaluated['objective']),
                        'Compact objective underestimates fixed-K merit')
                if evaluated['objective']<=initial_eval['objective']+1e-7:
                    chosen_edges,chosen_x,chosen_z,chosen_eval=proposed,clipped,rounded,evaluated
                    chosen_origin='SOLVER_INCUMBENT'
                else:rejection='SOLVER_INCUMBENT_WORSE_THAN_VALID_INITIAL_POINT'
            except (ValueError,AssertionError) as error:rejection='UNUSABLE_ROUNDED_INCUMBENT: '+str(error)
        else:rejection='NO_NUMERICALLY_FEASIBLE_INTEGRAL_INCUMBENT'
    else:rejection='NO_FINITE_SOLVER_INCUMBENT'
    returned_values=pack_values(model,chosen_x,chosen_z,chosen_eval)
    require(model_violation(model,returned_values)<=1e-7,'Retained incumbent invalid')
    numerical_optimal=(status==highspy.HighsModelStatus.kOptimal and run_status==highspy.HighsStatus.kOk and chosen_origin=='SOLVER_INCUMBENT')
    sources=[Path(__file__),ROOT/'acceleration/linear_probe.py',ROOT/'acceleration/audit_certificate.py']
    result=dict(status='NUMERICAL_FIXED_MATCHING_CONTROL' if fix_initial else 'NUMERICAL_WHOLE_MATCHING_CANDIDATE',
                numerical_optimal=numerical_optimal,fix_initial=fix_initial,root_group=root_group,matching_class=matching_class,
                selected_origin=chosen_origin,retained_initial_incumbent=chosen_origin=='INITIAL_INCUMBENT',
                matching_unchanged=chosen_edges==model['original'],solver_incumbent_rejection=rejection,
                overlap_edges_outer_zero_based=[list(e) for e in sorted(chosen_edges)],
                initial_overlap_edges_sha256=edge_digest(model['original']),overlap_edges_sha256=edge_digest(chosen_edges),
                edge_variables=[list(e) for e in model['x_edges']],numeric_edge_values=chosen_x.tolist(),
                matching_variables=[list(e) for e in model['matching_edges']],initial_matching_edges=[list(e) for e in sorted(model['initial_matching'])],
                selected_matching_edges=[list(e) for e,z in zip(model['matching_edges'],chosen_z) if z==1],
                matching_binary_values=chosen_z.astype(int).tolist(),raw_matching_values=raw_matching.tolist() if raw_matching is not None else None,
                raw_solution_values=raw_values.tolist() if raw_values is not None else None,
                numeric_objective=chosen_eval['objective'],initial_numeric_objective=initial_eval['objective'],
                numeric_solver_objective=finite_or_none(info.objective_function_value),
                numeric_mip_dual_bound=finite_or_none(info.mip_dual_bound) if not fix_initial else None,
                numeric_mip_gap=finite_or_none(info.mip_gap) if not fix_initial else None,
                mip_nodes=int(info.mip_node_count),solver_run_status=str(run_status),solver_model_status=str(status),
                primal_solution_status=int(info.primal_solution_status),time_limit_reached=status==highspy.HighsModelStatus.kTimeLimit,
                binary_rounding_maximum=z_error,x_projection_maximum=projection,
                raw_model_maximum_violation=raw_model_violation,returned_model_maximum_violation=model_violation(model,returned_values),
                initial_model_maximum_violation=warm_violation,
                numeric_slacks=dict(quota_excess=chosen_eval['quota_excess'].tolist(),quota_shortage=chosen_eval['quota_shortage'].tolist(),pair_cap_violation=chosen_eval['cap_violation'].tolist()),
                row_residuals=dict(quota=chosen_eval['quota_residuals'].tolist(),pair_caps=chosen_eval['cap_residuals'].tolist()),
                slack_coordinates=dict(quota=[[u-15,s-1] for u,s in model['quotas']],pair_caps=[list(p) for p in model['outer_pairs']]),
                residual_breakdown=dict(quota_absolute_sum=float(np.abs(chosen_eval['quota_residuals']).sum()),pair_cap_positive_sum=float(chosen_eval['cap_violation'].sum())),
                dimensions=dict(x_variables=nx,matching_variables=nz,slack_variables=2*840+3486,total_columns=len(warm),
                                rows=model['matrix'].shape[0],nonzeros=int(model['matrix'].nnz),row_kinds=model['row_kinds']),
                column_order='X; matching binaries;840 quota excess;840 quota shortage;3486 shared pair-cap slacks',
                objective_definition='Uniform sum of quota excess+shortage and one violation slack per outer pair; same fixed-K phase-I merit.',
                formulation='One variable perfect matching; hard full99 partial caps; compact M=1 partner indicators with shared pair slack and baseline H<=2+t.',
                source_sha256={path_key(p):digest(p) for p in sources},highs_version=solver.version(),numpy_version=np.__version__,scipy_version=scipy.__version__,
                seconds=seconds,model_build_seconds=build_seconds,solve_seconds=solve_seconds,elapsed_seconds=time.perf_counter()-started,
                scope='Numerical candidate optimization over one chosen matching with20 others fixed. MIP bounds/status/gaps are not proofs. X remains continuous and XX products are omitted. No pair-AC, global-coverage, exclusion or graph-construction claim.')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--root-group',type=int,required=True);parser.add_argument('--class',dest='matching_class',choices=CLASSES,required=True)
    parser.add_argument('--seconds',type=float,default=30);parser.add_argument('--initial-phase1',type=Path)
    parser.add_argument('--fix-initial',action='store_true');args=parser.parse_args()
    require(not args.out.exists(),'Preserve previous output directory')
    candidate=json.loads(args.initial.read_bytes());edges=candidate['overlap_edges_outer_zero_based'];full_graph(candidate)
    initial_x=None;bindings={path_key(args.initial):digest(args.initial)}
    if args.initial_phase1:
        previous=json.loads(args.initial_phase1.read_bytes())
        require(previous['overlap_edges_sha256']==edge_digest(edges),'Initial phase-I/candidate mismatch')
        initial_x=previous['numeric_edge_values'];require(initial_x is not None,'Initial phase-I has no X')
        bindings[path_key(args.initial_phase1)]=digest(args.initial_phase1)
    args.out.mkdir(parents=True)
    print(json.dumps(dict(status='BUILDING_WHOLE_MATCHING_MODEL',root_group=args.root_group,matching_class=args.matching_class,fix_initial=args.fix_initial,seconds=args.seconds)),flush=True)
    result=solve_matching(edges,args.root_group,args.matching_class,args.seconds,initial_x,args.fix_initial)
    result['inputs_sha256']=bindings
    output_candidate=args.out/'candidate.json'
    output_candidate.write_text(json.dumps({'overlap_edges_outer_zero_based':result['overlap_edges_outer_zero_based'],
                               'numeric_phase1_merit':result['numeric_objective'],'source_result':path_key(args.out/'result.json')},separators=(',',':'))+'\n',encoding='utf-8')
    result.update(candidate_path=path_key(output_candidate),candidate_sha256=digest(output_candidate))
    for path,expected in {**bindings,**result['source_sha256']}.items():require(digest(Path(path))==expected,'Input/source changed during run')
    (args.out/'result.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8')
    omitted={'overlap_edges_outer_zero_based','edge_variables','numeric_edge_values','matching_variables','raw_matching_values','raw_solution_values','numeric_slacks','row_residuals','slack_coordinates','matching_binary_values'}
    print(json.dumps({k:v for k,v in result.items() if k not in omitted},allow_nan=False),flush=True)


if __name__=='__main__':main()
