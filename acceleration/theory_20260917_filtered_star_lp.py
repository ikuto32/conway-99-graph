"""Numerical phase I on independently sound triangle/pair-filtered star domains.

New objective TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1; no legacy domain flags
or original-domain objective claims are reused. Exact verification is separate.
"""
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import highspy
import numpy as np
from scipy.sparse import coo_matrix, hstack, vstack

from audit_phase1 import graph_rows

ROOT = Path(__file__).resolve().parents[1]
OBJECTIVE = 'TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1'
CONVENTION = 'X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'
CANDIDATE = ROOT/'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'
ORIGINAL = ROOT/'acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json'
REDUCTION = ROOT/'acceleration/results/20260917_theory/matching_pair_baseline18481/translated_pairs.json'
REVIEW = ROOT/'acceleration/results/20260917_independent_review/matching_pair.json'


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def key(p):
    return p.resolve().relative_to(ROOT).as_posix()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, obj, compressed=False):
    payload = (json.dumps(obj, separators=(',', ':'), allow_nan=False)+'\n').encode()
    with path.open('xb') as f:
        f.write(gzip.compress(payload, mtime=0) if compressed else payload)


def augment(base, target, normals, reciprocal):
    nrow, n = base.shape
    neq, penalized = normals+reciprocal, nrow-normals
    sr = np.r_[np.arange(normals,nrow),np.arange(normals,neq)]
    sc = np.arange(penalized+reciprocal)
    sv = np.r_[-np.ones(penalized),np.ones(reciprocal)]
    slack = coo_matrix((sv,(sr,sc)),shape=(nrow,penalized+reciprocal)).tocsr()
    matrix = hstack((base,slack),format='csr')
    matrix.sort_indices()
    cost = np.r_[np.zeros(n),np.ones(penalized+reciprocal)]
    lower = np.r_[target[:neq],np.full(nrow-neq,-highspy.kHighsInf)]
    return matrix, cost, lower, target


def solver_for(matrix,cost,lower,upper,seconds,log_path=None):
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = matrix.shape
    lp.col_cost_,lp.col_lower_,lp.col_upper_ = cost,np.zeros(matrix.shape[1]),np.full(matrix.shape[1],highspy.kHighsInf)
    lp.row_lower_,lp.row_upper_ = lower,upper
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_ = matrix.indptr,matrix.indices,matrix.data
    solver=highspy.Highs()
    options=[('output_flag',log_path is not None),('log_to_console',False),('time_limit',seconds),('threads',1),
             ('solver','ipm'),('run_crossover','off')]
    if log_path is not None:
        options.append(('log_file',str(log_path)))
    for name,value in options:
        assert solver.setOptionValue(name,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    return solver


def controls():
    base=coo_matrix(np.ones((2,2))).tocsr()
    records=[]
    for rhs,expected,name in [(1,0,'FEASIBLE_SIMPLEX_CAP'),(0,1,'CORRUPTED_CAP_REQUIRES_UNIT_VIOLATION')]:
        matrix,cost,lower,upper=augment(base,np.array([1,rhs]),1,0)
        solver=solver_for(matrix,cost,lower,upper,5)
        solver.run()
        observed=solver.getInfo().objective_function_value
        assert solver.getModelStatus()==highspy.HighsModelStatus.kOptimal and abs(observed-expected)<1e-8
        records.append(dict(name=name, exact_expected_optimum=expected, numerical_observed=observed))
    return dict(status='PRODUCER_NUMERICAL_SLACK_SIGN_CONTROLS_PASS', tolerance=1e-8,records=records,
                mathematical_reason='p0+p1=1 forces cap excess max(0,1-rhs); independent review still required.',independent_verification=False)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=float,default=30)
    args=p.parse_args()
    assert np.isfinite(args.seconds) and 0<args.seconds<=30
    started=time.perf_counter()
    review=json.loads(REVIEW.read_bytes())
    assert review['status']=='INDEPENDENT_MATCHING_FILTERED_PAIR_PROPAGATION_AND_COMPARISON_PASS'
    assert review['pair_verification']['final_all_directed_pair_closure_checked'] is True
    bindings={}
    for name,h in review['inputs_sha256'].items():
        path=Path(name)
        if not path.is_absolute(): path=ROOT/path
        assert digest(path)==h, 'Changed independent reduction premise: '+name
        bindings[key(path)]=h
    for path in (CANDIDATE,ORIGINAL,REDUCTION):
        assert review['inputs_sha256'][key(path)]==digest(path)
    for path in (REVIEW,Path(__file__),ROOT/'acceleration/audit_phase1.py',ROOT/'acceleration/audit_certificate.py',
                 ROOT/'uv.lock',ROOT/'pyproject.toml'):
        bindings[key(path)]=digest(path)
    reduction,original,candidate=(json.loads(path.read_bytes()) for path in (REDUCTION,ORIGINAL,CANDIDATE))
    assert reduction['propagation_status']=='ARC_CONSISTENT_NONEMPTY' and reduction['original_complete_domains'] is False
    ids=reduction['surviving_original_domain_ids']
    assert len(ids)==84 and sum(map(len,ids))==review['pair_verification']['final_choices']==15335
    masks=[]
    for u,row in enumerate(ids):
        table=original['domains'][u]
        assert table['outer_vertex']==u and row and row==sorted(set(row))
        assert all(type(i) is int and 0<=i<len(table['domain_masks_hex']) for i in row)
        masks.append([int(table['domain_masks_hex'][i],16) for i in row])
    args.out.mkdir(parents=True,exist_ok=False)
    manifest=dict(schema_version=1,created_at=stamp(),objective_id=OBJECTIVE,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=['uv','run','--locked','--offline','--cache-dir','.uv-cache-20260917','python','-B']+sys.argv,
        cwd=str(ROOT),environment={'UV_PROJECT_ENVIRONMENT':'build/research-venv'},
        python=sys.version,platform=platform.platform(),dependencies={name:version(name) for name in ('numpy','scipy','highspy','tqdm')},
        inputs_sha256=bindings,source_additions_explicitly_hashed=True,
        prerequisite={'id':'C-STAR-MATCHING-PAIR-18481','revision':1,'relation':'uses_result','audit_sha256':digest(REVIEW)},
        question='What exact phase-I bound can be certified for the continuous model on all15335 sound triangle/pair-filtered baseline18481 stars?',
        interpretation='A positive exact lower bound excludes zero residual for this filtered necessary model; it supplies another fixedK obstruction only. No numerical comparison with the old original-domain objective.',
        selection='All84 sound filtered subdomains, original IDs ascending; no post-result selection.',
        domain_scope='TRIANGLE_AND_PAIR_FILTERED_ORIGINAL_ID_DOMAINS',original_complete_domains_used=False,
        pair_pruned_domains_used=True,projection_convention=CONVENTION,
        mathematical_objective='Minimum sum_abs(edge reciprocity residuals)+sum_positive_part(retained outer-pair linear cap residuals), over one hard probability simplex per filtered vertex domain.',
        direction='MINIMIZE',caps={'solver_time_seconds':args.seconds,'threads':1},
        solver_options={'solver':'ipm','run_crossover':'off'},
        numerical_acceptance_thresholds={'producer_controls_absolute':1e-8,'certificate_promotion':'No numerical threshold; independent exact lower/upper checking required'},
        random_seed=None,random_seed_reason='No random selection; deterministic input order, single solver thread.',
        limitations=['No direct comparison to original-domain5.374 objective or target-wide progress.','Numerical status is not a certificate.','BaselineK already excluded.'],
        shared_producer_helpers=['audit_phase1.graph_rows','audit_certificate.full_graph and graph_constraint'],
        independent_review='Must rebuild graph constraints and filtered columns separately; old original-domain auditor is not invoked.')
    save(args.out/'manifest.json',manifest)
    save(args.out/'controls.json',controls())
    frozen=dict(objective_id=OBJECTIVE,domain_scope=manifest['domain_scope'],original_complete_domains_used=False,
        original_domains_path=key(ORIGINAL),original_domains_sha256=digest(ORIGINAL),reduction_path=key(REDUCTION),
        reduction_sha256=digest(REDUCTION),independent_reduction_audit_path=key(REVIEW),independent_reduction_audit_sha256=digest(REVIEW),
        domains=[dict(outer_vertex=u,original_domain_ids=ids[u],domain_masks_hex=[hex(m) for m in row]) for u,row in enumerate(masks)])
    save(args.out/'frozen_domains.json',frozen)
    edges,rows,_=graph_rows(candidate)
    caps=rows[840:]
    index={e:i for i,e in enumerate(edges)}
    offsets=np.cumsum([0]+[len(row) for row in masks]).tolist()
    n=offsets[-1]
    rr,cc,vv,er,ec,normal_rows=[],[],[],[],[],[]
    for u,table in enumerate(masks):
        normal_rows.extend([u]*len(table))
        for i,mask in enumerate(table):
            assert mask.bit_count()==8 and not mask>>84
            for v in range(84):
                if mask>>v&1:
                    edge=index[tuple(sorted((u,v)))]
                    rr.append(edge);cc.append(offsets[u]+i);vv.append(1 if u<v else -1)
                    if u<v: er.append(edge);ec.append(offsets[u]+i)
    reciprocity=coo_matrix((vv,(rr,cc)),shape=(1680,n)).tocsr()
    projection=coo_matrix((np.ones(len(er)),(er,ec)),shape=(1680,n)).tocsr()
    normal=coo_matrix((np.ones(n),(normal_rows,range(n))),shape=(84,n)).tocsr()
    cr,ce=[],[]
    for i,row in enumerate(caps): cr.extend([i]*len(row['terms']));ce.extend(row['terms'])
    edge_caps=coo_matrix((np.ones(len(cr)),(cr,ce)),shape=(3486,1680)).tocsr()
    marginal_caps=(edge_caps@projection).tocsr()
    base=vstack((normal,reciprocity,marginal_caps),format='csr')
    target=np.r_[np.ones(84),np.zeros(1680),[row['target'] for row in caps]]
    matrix,cost,lower,upper=augment(base,target,84,1680)
    assert np.array_equal(matrix.data,matrix.data.astype(np.int64))
    exact_model=dict(objective_id=OBJECTIVE,domain_scope=manifest['domain_scope'],original_complete_domains_used=False,
        domains_sha256=digest(args.out/'frozen_domains.json'),projection_convention=CONVENTION,
        shape=list(matrix.shape),probability_columns=n,domain_offsets=offsets,
        row_order={'normalization':[0,84],'reciprocity':[84,1764],'linear_caps':[1764,5250]},
        edge_order=edges,cap_rows=caps,csr_indptr=matrix.indptr.tolist(),csr_indices=matrix.indices.tolist(),
        csr_integer_values=matrix.data.astype(np.int64).tolist(),integer_column_cost=cost.astype(np.int64).tolist(),
        column_lower_bound=0,column_upper_bound=None,column_upper_bound_reason='Positive infinity for every column',
        integer_row_upper_bounds=upper.astype(np.int64).tolist(),
        row_lower_bounds=[int(value) if i<1764 else None for i,value in enumerate(lower)],
        null_row_lower_reason='Negative infinity for cap rows; equality target for all preceding rows',
        slack_convention='One nonnegative excess variable with coefficient-1 on every penalized row; extra coefficient+1 shortage for reciprocity rows; all slack costs1.')
    save(args.out/'exact_model.json.gz',exact_model,compressed=True)
    solver=solver_for(matrix,cost,lower,upper,args.seconds,args.out/'highs.log')
    built=time.perf_counter()
    begun=stamp()
    run_status=solver.run()
    solution,info,model_status=solver.getSolution(),solver.getInfo(),solver.getModelStatus()
    ended=stamp()
    result=dict(status='TRIANGLE_PAIR_FILTERED_NUMERICAL_NO_INCUMBENT',objective_id=OBJECTIVE,
        domain_scope=manifest['domain_scope'],original_complete_domains_used=False,pair_pruned_domains_used=True,
        inputs_sha256=bindings,candidate_path=key(CANDIDATE),candidate_sha256=digest(CANDIDATE),
        frozen_domains_path=key(args.out/'frozen_domains.json'),frozen_domains_sha256=digest(args.out/'frozen_domains.json'),
        reduction_path=key(REDUCTION),reduction_sha256=digest(REDUCTION),reduction_audit_path=key(REVIEW),reduction_audit_sha256=digest(REVIEW),
        exact_model_path=key(args.out/'exact_model.json.gz'),exact_model_sha256=digest(args.out/'exact_model.json.gz'),
        projection_convention=CONVENTION,domain_counts=[len(row) for row in masks],domain_offsets=offsets,domain_variables=n,
        rows=5250,hard_normalizations=84,reciprocity_equalities=1680,retained_linear_caps=3486,
        augmented_columns=matrix.shape[1],matrix_nonzeros=base.nnz,augmented_nonzeros=matrix.nnz,
        highs_version=solver.version(),model_status=str(model_status),run_status=str(run_status),
        numerical_optimal=model_status==highspy.HighsModelStatus.kOptimal,time_limit_seconds=args.seconds,
        started_at=begun,finished_at=ended,build_seconds=built-started,solve_seconds=time.perf_counter()-built,
        numerical_values_are_proofs=False,independently_verified=False,graph_constructed=False,general_nonexistence_proved=False)
    raw={'value_valid':bool(solution.value_valid),'dual_valid':bool(solution.dual_valid)}
    if solution.value_valid:
        raw.update(col_value=solution.col_value,row_value=solution.row_value)
        probabilities=np.maximum(np.asarray(solution.col_value[:n]),0)
        assert len(probabilities)==n and np.all(np.isfinite(probabilities))
        for u in range(84):
            s=slice(offsets[u],offsets[u+1]);total=probabilities[s].sum();assert total>0
            probabilities[s]/=total
        residual=base@probabilities-target
        result.update(status='TRIANGLE_PAIR_FILTERED_NUMERICAL_INCUMBENT',numeric_probabilities=probabilities.tolist(),
            numeric_objective=float(np.abs(residual[84:1764]).sum()+np.maximum(residual[1764:],0).sum()),
            numeric_solver_objective=float(info.objective_function_value),
            numeric_reciprocity_violation=float(np.abs(residual[84:1764]).sum()),numeric_cap_violation=float(np.maximum(residual[1764:],0).sum()),
            numeric_projected_edge_values=(projection@probabilities).tolist(),
            probability_encoding='JSON round-trip IEEE754 binary64; exact rational interpretation and per-simplex renormalization required for an exact upper certificate.')
    if solution.dual_valid:
        raw.update(col_dual=solution.col_dual,row_dual=solution.row_dual)
        dual=-np.asarray(solution.row_dual[84:])
        assert len(dual)==5166 and np.all(np.isfinite(dual))
        dual[:1680]=np.clip(dual[:1680],-1,1);dual[1680:]=np.clip(dual[1680:],0,1)
        coefficients=reciprocity.T@dual[:1680]+marginal_caps.T@dual[1680:]
        lower_hint=sum(float(np.min(coefficients[offsets[u]:offsets[u+1]])) for u in range(84))-float(target[1764:]@dual[1680:])
        result.update(numeric_reciprocity_duals=dual[:1680].tolist(),numeric_cap_duals=dual[1680:].tolist(),
            numeric_simplex_dual_lower=lower_hint,dual_encoding='JSON round-trip IEEE754 binary64; exact integer denominator clearing is reserved for independent checker.')
    save(args.out/'raw_highs_solution.json',raw)
    result['raw_solution_sha256']=digest(args.out/'raw_highs_solution.json')
    assert all(digest(ROOT/name)==h for name,h in bindings.items())
    save(args.out/'phase1.json',result)
    summary={k:v for k,v in result.items() if k not in ('inputs_sha256','numeric_probabilities','numeric_reciprocity_duals','numeric_cap_duals','numeric_projected_edge_values')}
    summary.update(status='FILTERED_STAR_LP_NUMERICAL_RUN_COMPLETED',source_commit=manifest['source_commit'],
        outputs_sha256={path.name:digest(path) for path in args.out.iterdir() if path.is_file()},
        target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator')
    save(args.out/'summary.json',summary)
    print(json.dumps({k:summary.get(k) for k in ('status','objective_id','domain_variables','model_status','numeric_objective','numeric_simplex_dual_lower','solve_seconds')}))


if __name__=='__main__':
    main()
