"""Scalar-only cold CPU replay of canonical C99SCP01 for paired timing."""
import os
for _name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
import numpy as np
from review_star_pdhg_gpu import parse_binary, bounds, product_simplex_projection

ROOT=Path(__file__).resolve().parents[1]
PINS={'review_star_pdhg_gpu.py':'555e9595808d2e9045876c895d96845a2baad3d2f0773de65c9f745756ac0786',
      'star_marginal_cp_cpu_v2.py':'6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');a=p.parse_args()
    output=Path(a.output)
    if output.exists():raise ValueError('Preserve existing output')
    for name,h in PINS.items():
        if sha256((ROOT/'acceleration'/name).read_bytes()).hexdigest()!=h:raise ValueError('Changed frozen dependency')
    started=time.perf_counter();checkpoints,models=parse_binary(a.input);parse_seconds=time.perf_counter()-started
    results=[];iteration_seconds=0.;metric_seconds=0.
    for index,m in enumerate(models):
        offsets=m['offsets'];counts=np.diff(offsets);N=m['A'].shape[1];M=m['A'].shape[0];Q=m['Q']
        x=np.repeat(1./counts,counts);bar=x.copy();y=np.zeros(M);xa=np.zeros(N);ya=np.zeros(M)
        tick=time.perf_counter();initial=bounds(m,x,y);metric_seconds+=time.perf_counter()-tick
        best_upper=initial['primal_upper_numeric'];best_lower=initial['dual_lower_numeric'];points=[]
        lower=np.r_[np.full(Q,-1.),np.zeros(M-Q)];previous=0
        for checkpoint in checkpoints:
            tick=time.perf_counter()
            for iteration in range(previous+1,checkpoint+1):
                newy=np.clip(y+m['sigma']*(m['A']@bar-m['b']),lower,1.)
                newx=product_simplex_projection(x-m['tau']*(m['AT']@newy),offsets)
                bar,x,y=2*newx-x,newx,newy;xa+=(x-xa)/iteration;ya+=(y-ya)/iteration
            iteration_seconds+=time.perf_counter()-tick;tick=time.perf_counter()
            last,average=bounds(m,x,y),bounds(m,xa,ya)
            best_upper=min(best_upper,last['primal_upper_numeric'],average['primal_upper_numeric']);best_lower=max(best_lower,last['dual_lower_numeric'],average['dual_lower_numeric'])
            points.append(dict(iterations=checkpoint,last=last,average=average,best_upper_numeric=best_upper,best_lower_numeric=best_lower))
            metric_seconds+=time.perf_counter()-tick;previous=checkpoint
        results.append(dict(candidate_index=index,n_variables=N,n_rows=M,n_equalities=Q,domain_counts=counts.tolist(),initial=initial,checkpoints=points))
    result=dict(status='NUMERICAL_COLD_STAR_CPU_BENCHMARK_FINISHED',candidate_count=len(results),eta=.9,theta=1,
                float_type='float64',initialization='uniform_per_simplex_probability_zero_dual',best_scope='initial_and_requested_checkpoint_last_and_average',
                parse_seconds=parse_seconds,cpu_iteration_seconds=iteration_seconds,metrics_seconds=metric_seconds,elapsed_seconds=time.perf_counter()-started,
                numerical_scores_are_proofs=False,results=results,threads_environment=1,
                scope='Scalar-only canonical CSR CPU reference; process timing must be measured externally to include Python imports and finalJSONwrite.')
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,separators=(',',':'),allow_nan=False);f.write('\n')
    print(json.dumps(dict(candidate_count=len(results),iteration_seconds=iteration_seconds,elapsed_seconds=time.perf_counter()-started)))

if __name__=='__main__':main()
