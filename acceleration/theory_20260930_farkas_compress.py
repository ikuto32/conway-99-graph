"""Bounded exact coefficient simplification; no LP/SAT solver."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from functools import reduce
from hashlib import sha256
from math import gcd
from pathlib import Path
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'acceleration/results/20260930_hadamard_support_lp/exact_model.json'
ORIGINAL=ROOT/'acceleration/results/20260930_hadamard_support_lp_dual_repair/certificate.json'

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def check(columns,rhs,y):
    need(len(y)==len(rhs) and all(type(v)is int for v in y),'integer dualdimension')
    dots=[sum(y[r] for r in col) for col in columns]
    return dots,sum(v*b for v,b in zip(y,rhs,strict=True))

def repair(columns,rhs,groups,weights):
    n=len(groups);y=[0]*n+weights[:];minimum=[];argmin=[]
    for group in groups:
        values=[sum(y[r] for r in columns[j] if r>=n) for j in group]
        m=min(values);minimum.append(m);argmin.append(group[values.index(m)])
    y[:n]=[-v for v in minimum]
    divisor=reduce(gcd,(abs(v) for v in y),0) or 1;y=[v//divisor for v in y]
    dots,right=check(columns,rhs,y);need(min(dots)>=0,'exact repair all columns')
    return dict(values=y,column_dots=dots,rhs_dot=right,minimum_column_dot=min(dots),
                Gram_option_minima_before_gcd=minimum,argmin_selector_indices=argmin,divided_gcd=divisor)

def controls():
    feasible=repair([[0,1],[0,2]],[1,1,0],[[0,1]],[1,-1])
    need(feasible['rhs_dot']>=0,'feasible tiny cannot yield contradiction')
    negative=repair([[0,1]],[0,1],[[0]],[-1]);need(negative['rhs_dot']<0,'tiny exact infeasible positivecontrol')
    wrong=negative['column_dots'][:];wrong[0]+=1
    need(wrong!=check([[0,1]],[0,1],negative['values'])[0],'wrongsaved columndot rejected')
    opposite=[-v for v in negative['values']];dots,right=check([[0,1]],[0,1],opposite)
    need(not(min(dots)>=0 and right<0),'oppositesign noncertificate')
    return dict(feasible=feasible,infeasible=negative,corrupt_dot_rejected=True,opposite_sign_rejected=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();deadline=start+30
    inputs={key(p):digest(p) for p in [MODEL,ORIGINAL,Path(__file__),Path(__file__).with_name('theory_20260930_farkas_compress_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']}
    created=datetime.now(timezone.utc).isoformat();save(out/'manifest.json',dict(created_at=created,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        inputs_sha256=inputs,versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),limits=dict(seconds=30,solver_calls=0)))
    save(out/'controls.json',controls());model=read(MODEL);original=read(ORIGINAL);columns=model['columns_nonzero_row_indices'];rhs=model['rhs']
    dots,right=check(columns,rhs,original['values'])
    need(len(columns)==4067 and len(rhs)==726 and min(dots)>=0 and right==-37617760,'literal originalcandidate')
    need(dots==original['column_dots'] and right==original['rhs_dot'],'originalsaved dots')
    groups=[[j for j,pair in enumerate(model['selectors']) if pair[0]==d] for d in range(60)]
    need(all(group and all(columns[j][0]==d and all(r>=60 for r in columns[j][1:]) for j in group) for d,group in enumerate(groups)),'onehot group structure')
    active={r for col in columns for r in col};base=[v if 60+i in active else 0 for i,v in enumerate(original['values'][60:])]
    trials=[];best=None;best_metric=None
    def trial(weights,label,accept_sparse=False):
        nonlocal best,best_metric
        result=repair(columns,rhs,groups,weights);y=result['values'];valid=result['rhs_dot']<0
        metric=(max(map(abs,y)),sum(v!=0 for v in y[60:]),sum(map(abs,y)))
        trials.append(dict(index=len(trials),label=label,Gram_weights=[[60+i,v] for i,v in enumerate(weights) if v],
            repaired_onehot_weights=y[:60],gcd=result['divided_gcd'],rhs_dot=result['rhs_dot'],minimum_column_dot=result['minimum_column_dot'],
            exact_Farkas=valid,metric=list(metric)))
        if valid and (best is None or metric<best_metric or accept_sparse):best=result;best_metric=metric
        return valid,result
    trial(base,dict(stage='original_Gram_optimal_onehot'))
    divisors=sorted({m*10**k for k in range(9) for m in (1,2,5)})
    stopped=False
    for divisor in divisors:
        for threshold in range(4):
            if time.monotonic()>=deadline:stopped=True;break
            weights=[round(Fraction(v,divisor)) for v in base];weights=[v if abs(v)>threshold else 0 for v in weights]
            trial(weights,dict(stage='rounded_threshold',divisor=divisor,threshold=threshold))
        if stopped:break
    need(best is not None,'original contradiction retained')
    for i in sorted((i for i,v in enumerate(best['values'][60:]) if v),key=lambda i:(abs(best['values'][60+i]),i)):
        if time.monotonic()>=deadline:stopped=True;break
        weights=best['values'][60:];old=weights[i];weights[i]=0
        valid,_=trial(weights,dict(stage='greedy_zero',row=60+i,previous=old),accept_sparse=True)
        if not valid and abs(old)>1 and time.monotonic()<deadline:
            weights=best['values'][60:];weights[i]=1 if old>0 else -1
            trial(weights,dict(stage='greedy_sign',row=60+i,previous=old),accept_sparse=True)
    finaldots,finalright=check(columns,rhs,best['values']);need(finaldots==best['column_dots'] and finalright<0,'complete final exactrecheck')
    save(out/'certificate.json',dict(status='CANDIDATE_SIMPLIFIED_EXACT_INTEGER_FARKAS',**best,scope='Exact fixedconnected01 continuousGram selector relaxation only.',independent_approval=False))
    save(out/'trials.json',dict(attempts=trials,stopped_by_time_limit=stopped))
    table=[dict(matrix_row=60+i,Gram_rows=model['Gram_row_pairs'][i],weight=v,rhs=rhs[60+i]) for i,v in enumerate(best['values'][60:]) if v]
    save(out/'weighted_Gram_rows.json',dict(rows=table,onehot_weights=best['values'][:60]))
    text=['# Candidate simplified weighted-sum obstruction','',
        'All numbers are exact integers. Independent review is pending. This excludes only the fixed connected01 support if the matrix/scope and certificate are accepted.','',
        f'For every one of the 4,067 retained color choices, the sum of its Gram-row weights plus the corresponding column one-hot weight is nonnegative. The weighted required right-hand side is {finalright}. Thus a nonnegative selector solution cannot exist.','',
        f'There are {len(table)} nonzero Gram weights and {sum(v!=0 for v in best["values"][:60])} nonzero one-hot weights; the maximum absolute full weight is {max(map(abs,best["values"]))}.','',
        'The complete coefficient table and all option checks are in weighted_Gram_rows.json and certificate.json. This is not a graph/core exclusion and is not yet a short unweighted combinatorial argument.']
    (out/'explanation.md').write_text('\n'.join(text)+'\n',encoding='utf-8',newline='\n')
    need(all(digest(ROOT/p)==h for p,h in inputs.items()),'frozen inputs')
    summary=dict(status='CANDIDATE_FARKAS_COEFFICIENT_SIMPLIFICATION',created_at=created,completed_at=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=inputs,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
        exact_trials=len(trials),successful_exact_trials=sum(t['exact_Farkas'] for t in trials),stopped_by_time_limit=stopped,
        original_rhs=-37617760,simplified_rhs=finalright,maximum_absolute_weight=max(map(abs,best['values'])),
        nonzero_Gram_weights=len(table),nonzero_onehot_weights=sum(v!=0 for v in best['values'][:60]),
        solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',wall_seconds=time.monotonic()-start)
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs_sha256','outputs_sha256']}))

if __name__=='__main__':main()
