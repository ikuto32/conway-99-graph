"""Synthetic calibration-statistic controls, not scientific observations."""
import argparse
from copy import deepcopy
from fractions import Fraction
import json

import refine_whole_star_rank_v3_calibrated as c


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    rows=[dict(proposal_index=i,exact_lower=c.stored(Fraction(10*i)),exact_upper=c.stored(Fraction(10*i+1)),
        iterations500=dict(lower_numeric=float((15-i)*10-200),upper_numeric=float((15-i)*10+200)),
        iterations5000=dict(lower_numeric=float(10*i-1),upper_numeric=float(10*i+2))) for i in range(16)]
    r=c.metrics(rows);controls=[]
    c.base.require(r['exact_separated_pairs']==120 and r['ambiguous_exact_pairs']==0 and
        r['statistics']['iterations500']['upper_order_disagreements']==120 and
        r['statistics']['iterations500']['lower_order_disagreements']==120 and
        r['statistics']['iterations5000']['upper_order_disagreements']==0 and
        r['statistics']['iterations5000']['lower_order_disagreements']==0 and
        c.rational(r['statistics']['iterations500']['mean_gap'])==400 and c.rational(r['statistics']['iterations5000']['median_gap'])==3,
        'Exact reversal/order/gap fixture')
    controls.append(dict(name='ALL120_REVERSE_TO_CORRECT_MEAN400_TO3',outcome='ACCEPT'))
    ambiguous=[dict(proposal_index=i,exact_lower=c.stored(Fraction(1)),exact_upper=c.stored(Fraction(2)),
        iterations500=dict(lower_numeric=.1,upper_numeric=1.9),iterations5000=dict(lower_numeric=1.1,upper_numeric=2.1)) for i in range(16)]
    r=c.metrics(ambiguous)
    c.base.require(r['ambiguous_exact_pairs']==120 and r['exact_separated_pairs']==0 and
        r['statistics']['iterations500']['upper_endpoint_violations']==16 and r['statistics']['iterations500']['lower_endpoint_violations']==0 and
        r['statistics']['iterations5000']['lower_endpoint_violations']==16 and r['statistics']['iterations5000']['upper_endpoint_violations']==0,
        'Overlap and endpoint counts')
    controls.append(dict(name='ALL120_AMBIGUOUS_AND16_ENDPOINT_VIOLATIONS',outcome='ACCEPT'))
    tied=deepcopy(rows)
    for row in tied:
        row['iterations500']=dict(lower_numeric=-1.,upper_numeric=200.)
        row['iterations5000']=dict(lower_numeric=-1.,upper_numeric=200.)
    r=c.metrics(tied)
    c.base.require(r['statistics']['iterations500']['upper_score_ties_among_separated_pairs']==120 and
        r['statistics']['iterations500']['upper_order_disagreements']==0 and
        not any(r['strict_empirical_improvement'].values()),'Tie breaking/nonimprovement')
    controls.append(dict(name='ALL120_NUMERICAL_TIES_AND_NO_STRICT_IMPROVEMENT',outcome='ACCEPT'))
    touching=deepcopy(rows);touching[1]['exact_lower']=deepcopy(touching[0]['exact_upper'])
    c.base.require(c.metrics(touching)['ambiguous_exact_pairs']==1,'Touching endpoint ambiguity')
    controls.append(dict(name='TOUCHING_EXACT_INTERVAL_AMBIGUOUS',outcome='ACCEPT'))
    for name,change in [('missing_case',lambda x:x.pop()),('duplicate_ID',lambda x:x[0].update(proposal_index=1)),
        ('inverted_exact',lambda x:x[0].update(exact_lower=c.stored(Fraction(99)))),
        ('inverted_numerical',lambda x:x[0]['iterations500'].update(lower_numeric=999.)),
        ('nonfinite_numeric',lambda x:x[0]['iterations500'].update(upper_numeric=float('inf')))]:
        data=deepcopy(rows);change(data)
        try:c.metrics(data)
        except (ValueError,OverflowError) as e:controls.append(dict(name=name,outcome='REJECT',reason=str(e)))
        else:raise ValueError('Accepted corruption: '+name)
    report=dict(status='WHOLE_STAR_RERANK_V3_CALIBRATION_CONTROLS_PASS',created_at=c.base.now(),
        inputs_sha256={c.base.key(p):c.base.digest(p) for p in (__file__,c.__file__,c.base.__file__,c.ADDENDUM)},controls=controls,
        positive_controls=4,negative_controls=5,independent_verification=False,synthetic_fixtures_only=True,GPU_processes=0,LP_runs=0)
    c.base.save(a.out,report);print(json.dumps(dict(status=report['status'],positive_controls=4,negative_controls=5,sha256=c.base.digest(a.out))))


if __name__=='__main__':main()
