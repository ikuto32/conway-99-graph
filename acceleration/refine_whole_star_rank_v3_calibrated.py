"""Bind preregistered calibration statistics to frozen v3 execution; no model edits."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json

import refine_whole_star_rank_v3 as base

PRODUCER_SHA='1b103f25edb3f73e2c7b35af474ce9f674ed9dcb3401b8d043dbfec1250e4592'
ADDENDUM='docs/NEXT_20260917_WHOLE_STAR_RERANK_V3_CALIBRATION.md'
ADDENDUM_SHA='b67a89d3d92d3cd2b3f7e9cb0a89718aff6bd9f08af97f22ad1f94a0d12083fc'


def rational(x):return Fraction(int(x['numerator']),int(x['denominator']))


def stored(q):return dict(numerator=str(q.numerator),denominator=str(q.denominator),approximate=float(q))


def binary(x):return Fraction.from_float(float(x))


def metrics(calibration):
    base.require(len(calibration)==16 and len({r['proposal_index'] for r in calibration})==16,'Exactly16 calibration cases')
    base.require(all(rational(r['exact_lower'])<=rational(r['exact_upper']) for r in calibration),'Invalid exact interval')
    result={};pairs=[];ambiguous=[];separated=[]
    for a,b in combinations(calibration,2):
        i,j=a['proposal_index'],b['proposal_index']
        if rational(a['exact_upper'])<rational(b['exact_lower']):small,large=a,b
        elif rational(b['exact_upper'])<rational(a['exact_lower']):small,large=b,a
        else:
            ambiguous.append([i,j]);pairs.append(dict(pair=[i,j],exact_relation='AMBIGUOUS_OVERLAPPING_OR_TOUCHING'));continue
        x=dict(pair=[i,j],exact_relation='STRICTLY_SEPARATED',exact_smaller=small['proposal_index'],exact_larger=large['proposal_index'])
        for label in ('iterations500','iterations5000'):
            x[label]={}
            for objective in ('upper','lower'):
                field=objective+'_numeric';aa=small[label][field];zz=large[label][field]
                x[label][objective]=dict(disagreement=(aa,small['proposal_index'])>(zz,large['proposal_index']),numerical_tie=aa==zz)
        pairs.append(x);separated.append(x)
    base.require(len(pairs)==120,'Calibration pair denominator')
    for label in ('iterations500','iterations5000'):
        gaps=[];violations=[]
        for row in calibration:
            low,up=binary(row[label]['lower_numeric']),binary(row[label]['upper_numeric'])
            base.require(low<=up,'Inverted numerical calibration bracket');gaps.append(up-low)
            if low>rational(row['exact_lower']):violations.append(dict(proposal_index=row['proposal_index'],endpoint='lower'))
            if up<rational(row['exact_upper']):violations.append(dict(proposal_index=row['proposal_index'],endpoint='upper'))
        ordered=sorted(gaps)
        result[label]=dict(mean_gap=stored(sum(gaps,Fraction())/16),median_gap=stored((ordered[7]+ordered[8])/2),
            individual_gaps=[dict(proposal_index=r['proposal_index'],gap=stored(g)) for r,g in zip(calibration,gaps)],
            lower_endpoint_violations=sum(v['endpoint']=='lower' for v in violations),upper_endpoint_violations=sum(v['endpoint']=='upper' for v in violations),
            total_endpoint_violations=len(violations),endpoint_check_count=32,cases_with_endpoint_violations=len({v['proposal_index'] for v in violations}),
            calibration_case_count=16,endpoint_violation_records=violations,
            upper_order_disagreements=sum(p[label]['upper']['disagreement'] for p in separated),
            lower_order_disagreements=sum(p[label]['lower']['disagreement'] for p in separated),
            upper_score_ties_among_separated_pairs=sum(p[label]['upper']['numerical_tie'] for p in separated),
            lower_score_ties_among_separated_pairs=sum(p[label]['lower']['numerical_tie'] for p in separated),
            exact_separated_pair_denominator=len(separated))
    old,new=result['iterations500'],result['iterations5000']
    improved={k:rational(new[k])<rational(old[k]) for k in ('mean_gap','median_gap')}
    improved.update(upper_order_disagreements=new['upper_order_disagreements']<old['upper_order_disagreements'],
        lower_order_disagreements=new['lower_order_disagreements']<old['lower_order_disagreements'])
    improved['both_gap_statistics']=improved['mean_gap'] and improved['median_gap']
    return dict(statistics=result,strict_empirical_improvement=improved,total_calibration_pairs=120,
        exact_separated_pairs=len(separated),ambiguous_exact_pairs=len(ambiguous),ambiguous_pair_ids=ambiguous,pair_records=pairs,
        calibration_cases=16,reranked_existing_candidates=128,new_candidates=0,next_LP_eligible_candidates=112,
        numeric_statistics_certify_GPU_arithmetic=False,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator')


def supplemental_gate(args,b):
    base.require(args.calibration_gate and args.calibration_auditor and args.calibration_auditor_sha256,
        'Independent calibration wrapper/addendum gate required beforeGPU')
    b.bind(args.calibration_auditor,args.calibration_auditor_sha256);r=b.read(args.calibration_gate)
    base.require(r['status']=='INDEPENDENT_WHOLE_STAR_RERANK_V3_CALIBRATION_GATE_PASS' and r['producer_imported'] is False,
        'Independent calibration gate differs')
    for p in (__file__,ADDENDUM,args.input_audit,args.calibration_auditor):
        base.require(r['inputs_sha256'].get(base.key(p))==b.bind(p),'Calibration gate does not bind '+base.key(p))


def main():
    parser=base.parser();parser.add_argument('--calibration-gate');parser.add_argument('--calibration-auditor');parser.add_argument('--calibration-auditor-sha256')
    args=parser.parse_args();base.require(not args.prepare,'Use frozen producer for preparation')
    m,b=base.preflight(args);b.bind(base.__file__,PRODUCER_SHA);b.bind(__file__);b.bind(ADDENDUM,ADDENDUM_SHA)
    if args.validate_only:
        r=dict(status='WHOLE_STAR_RERANK_V3_CALIBRATED_PREFLIGHT_PASS',created_at=base.now(),inputs_sha256=b.values,
            prepared_manifest_path=base.key(Path(args.prepared)/'manifest.json'),prepared_manifest_sha256=base.digest(Path(args.prepared)/'manifest.json'),
            GPU_processes=0,LP_runs=0,addendum_path=ADDENDUM,addendum_sha256=ADDENDUM_SHA,independent_verification=False)
        if args.report:base.save(args.report,r)
        print(json.dumps(dict(status=r['status'],GPU_processes=0,LP_runs=0)));return
    base.execution_gate(args,m,b);supplemental_gate(args,b);base.require(args.out,'Fresh output required')
    base.execute(args,m,b)
    summary=base.load(Path(args.out)/'summary.json');calibration=summary['calibration']
    result=metrics(calibration)
    result.update(status='WHOLE_STAR_RERANK_V3_PREREGISTERED_CALIBRATION_METRICS',created_at=base.now(),
        inputs_sha256={**b.values,base.key(Path(args.out)/'summary.json'):base.digest(Path(args.out)/'summary.json')},
        addendum_path=ADDENDUM,addendum_sha256=ADDENDUM_SHA,all_calibration_cases=calibration,independent_verification=False,
        scope='Descriptive16-case numerical calibration; shortlist unchanged; exact statistics do not certify numerical optimization')
    base.save(Path(args.out)/'calibration_metrics.json',result)
    print(json.dumps(dict(status=result['status'],empirical_improvement=result['strict_empirical_improvement'],
        ambiguous_exact_pairs=result['ambiguous_exact_pairs'])))


if __name__=='__main__':main()
