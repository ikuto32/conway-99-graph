"""Diagnose saved strict phase-I audit failures without changing tolerance.

Every artifact first receives the original default1e-7 audit. Failed artifacts
receive separate exact-bound and remaining-check diagnostics, never a relaxed
PASS. No solver, producer, native evaluator or search is run.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import time

import audit_phase1_kkt as frozen

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_AUDITOR='c8efc709bcd10dc11d1f7ef3013a84cd834708880f09af5e026ee8cf3eda2d34'
TOLERANCE=1e-7


def resolve(path):
    p=Path(str(path).replace('\\','/'));return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(path):return resolve(path).relative_to(ROOT).as_posix()
def digest(path):return sha256(resolve(path).read_bytes()).hexdigest()


def remaining_checks(candidate_path,result_path):
    candidate=json.loads(candidate_path.read_bytes());result=json.loads(result_path.read_bytes())
    require=frozen.require
    require(result['candidate_sha256']==digest(candidate_path),'Candidate SHA mismatch')
    edges,groups,omitted=frozen.graph_rows(candidate)
    actual=result['constraint_groups'];frozen.compare_rows(actual,groups)
    require(result['edge_variables']==[list(e) for e in edges],'X variable order mismatch')
    require(result.get('disjoint_block_totals_assumed',False) is False,'Unsupported compression totals')
    for name,expected in result.get('source_sha256',{}).items():
        require(Path(name).name==name,'Unexpected producer source path')
        require(digest(ROOT/'acceleration'/name)==expected,'Producer source changed')
    x=frozen.finite_vector(result['numeric_edge_values'],len(edges),'X')
    require(all(-TOLERANCE<=v<=1+TOLERANCE for v in x),'Numerically invalid X box')
    clipped_x=[min(1,max(0,v)) for v in x]
    evaluation=frozen.evaluate(candidate,clipped_x)
    objective=result['numeric_objective']
    require(type(objective) in (float,int) and math.isfinite(objective),'Invalid objective')
    require(abs(evaluation['total_violation']-objective)<=TOLERANCE*max(1,abs(objective)),'Objective mismatch')
    weights=frozen.finite_vector(result['phase1_multipliers'],len(actual),'dual weights')
    marginals=frozen.finite_vector(result['row_duals'],len(actual),'marginals')
    require(all(y==-m for y,m in zip(weights,marginals)),'Row marginal sign mismatch')
    residuals=frozen.finite_vector(result['row_residuals'],len(actual),'residuals')
    truth=[sum(clipped_x[e] for e in row['terms'])-row['target'] for row in actual]
    require(all(abs(a-b)<=TOLERANCE for a,b in zip(residuals,truth)),'Declared residual mismatch')
    for name in ('numeric_solver_objective','numeric_slack_objective'):
        value=result[name]
        require(type(value) in (int,float) and math.isfinite(value),'Invalid '+name)
        require(abs(value-objective)<=TOLERANCE*max(1,abs(objective)),name+' disagrees with residual merit')
    indexed={(r['kind'],tuple(r['coordinate'])):y for r,y in zip(actual,weights)}
    y=[indexed.get((r['kind'],tuple(r['coordinate'])),0) for r in groups]
    violation=max(max((-1 if r['equality'] else 0)-v,v-1,0) for r,v in zip(groups,y))
    require(violation<=TOLERANCE,'Dual weight interval violation')
    upper,lower,qy,combined=frozen.exact_bounds(groups,clipped_x,y)
    gap=upper-lower;threshold=TOLERANCE*max(1,abs(float(upper)))
    for name,value in (('numerical_dual_lower_bound',float(lower)),('numerical_primal_dual_gap',float(gap))):
        require(type(result[name]) in (int,float) and math.isfinite(result[name]),'Invalid '+name)
        require(abs(result[name]-value)<=threshold,'Declared '+name+' mismatch')
    qx=list(map(Fraction,clipped_x))
    residuals=[sum((qx[e] for e in r['terms']),Fraction(0))-r['target'] for r in groups]
    row_slacks=[(abs(v) if r['equality'] else max(0,v))-w*v for r,v,w in zip(groups,residuals,qy)]
    box_slacks=[c*v-min(0,c) for v,c in zip(qx,combined)]
    require(all(v>=0 for v in row_slacks+box_slacks),'Negative exact complementarity slack')
    require(sum(row_slacks)+sum(box_slacks)==gap,'Exact complementarity decomposition differs')
    return dict(status='EXACT_BOUND_DIAGNOSTIC_NOT_OPTIMALITY_AUDIT',all_checks_other_than_gap_satisfied=True,
        fixed_tolerance=TOLERANCE,original_gap_criterion_satisfied=float(gap)<=threshold,
        exact_upper=frozen.rational(upper),exact_lower=frozen.rational(lower),exact_gap=frozen.rational(gap),
        original_gap_threshold=threshold,gap_to_threshold_ratio=float(gap)/threshold,
        graph_rows_checked=len(groups)+len(omitted),numerical_objective_difference=abs(evaluation['total_violation']-objective),
        dual_interval_violation=violation,x_clipped=sum(a!=b for a,b in zip(x,clipped_x)),
        dual_clipped=sum(Fraction(a)!=b for a,b in zip(y,qy)),exact_complementarity_sum_equals_gap=True,
        largest_exact_row_complementarity=frozen.rational(max(row_slacks)),
        largest_exact_box_complementarity=frozen.rational(max(box_slacks)),
        exact_lower_positive=lower>0,exact_interval_is_not_an_optimality_claim=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();frozen.require(not args.out.exists(),'Fresh diagnostic output required')
    frozen.require(digest(frozen.__file__)==EXPECTED_AUDITOR,'Frozen auditor changed')
    summary_path=resolve(args.run)/'summary.json';summary=json.loads(summary_path.read_bytes())
    frozen.require(summary['status']=='BOUNDED_CP_MATCHING_SEARCH_FINISHED','Search producer not terminal')
    rows=summary['records'];frozen.require(len(rows)==summary['probes']==len({r['proposal_index'] for r in rows}),'Invalid probe inventory')
    bindings={key(p):digest(p) for p in (summary_path,Path(__file__),Path(frozen.__file__),ROOT/'acceleration/audit_certificate.py')}
    started=time.perf_counter();records=[]
    for row in rows:
        paths=[resolve(row[k+'_path']) for k in ('candidate','result')]
        for kind,path in zip(('candidate','result'),paths):
            actual=digest(path);frozen.require(actual==row[kind+'_sha256'],'Probe input changed');bindings[key(path)]=actual
        record=dict(proposal_index=row['proposal_index'],candidate_path=key(paths[0]),candidate_sha256=digest(paths[0]),
                    result_path=key(paths[1]),result_sha256=digest(paths[1]))
        try:
            audit=frozen.inspect_artifact(*paths)
        except (ValueError,AssertionError) as error:
            record.update(strict_default_audit_passed=False,strict_error=str(error))
            try:record['diagnostic']=remaining_checks(*paths)
            except (ValueError,AssertionError) as diagnostic_error:
                record['diagnostic']=dict(status='ADDITIONAL_VALIDITY_CHECK_FAILED',error=str(diagnostic_error))
            print(json.dumps(dict(index=row['proposal_index'],strict_error=str(error),diagnostic=record['diagnostic'])),flush=True)
        else:
            record.update(strict_default_audit_passed=True,strict_audit=audit)
        records.append(record)
    frozen.require(all(digest(p)==h for p,h in bindings.items()),'Inputs changed during diagnostic')
    failed=[r for r in records if not r['strict_default_audit_passed']]
    report=dict(status='SAVED_PHASE1_STRICT_AUDIT_DIAGNOSTIC_FINISHED',inputs_sha256=bindings,records=records,
        original_default_tolerance=TOLERANCE,strict_pass_count=len(rows)-len(failed),strict_failure_count=len(failed),
        failed_indices=[r['proposal_index'] for r in failed],all_failures_only_gap=all(r.get('strict_error')=='Phase-I primal-dual gap too large' and
            r['diagnostic'].get('all_checks_other_than_gap_satisfied') is True for r in failed),
        search_audit_repaired=False,relaxed_audit_used=False,LP_reruns=0,graph_constructed=False,general_nonexistence_proved=False,
        elapsed_seconds=time.perf_counter()-started)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('status','strict_pass_count','strict_failure_count','failed_indices','all_failures_only_gap','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
