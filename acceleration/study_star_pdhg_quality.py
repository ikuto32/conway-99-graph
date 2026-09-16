"""Bounded CPU-only PDHG ranking quality on already solved star-LP candidates.

Reuses the frozen float64 helper and independently audited original domains.
No LP solve, domain enumeration, native search, or GPU invocation is performed.
"""
import os
for _thread_name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_thread_name]='1'

import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import time
import numpy as np
import scipy
from star_marginal_cp_cpu_v2 import build_model, diagonal_steps, numeric_bounds, step, transfer_probabilities

ROOT=Path(__file__).resolve().parents[1]
HELPER_SHA='6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d'
CONVENTION='X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'

def path(p):
    return (ROOT/str(p).replace('\\','/')).resolve()

def key(p):
    return path(p).relative_to(ROOT).as_posix()

def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()

def require(ok,message):
    if not ok:
        raise ValueError(message)

def fraction(q):
    return Fraction(int(q['numerator']),int(q['denominator']))

def dump(p,d):
    with path(p).open('x',encoding='utf-8') as f:
        json.dump(d,f,indent=2,allow_nan=False); f.write('\n')

def ranks(values):
    ordered=sorted(range(len(values)),key=values.__getitem__)
    result=[0.0]*len(values); start=0
    while start<len(values):
        end=start+1
        while end<len(values) and values[ordered[end]]==values[ordered[start]]:
            end+=1
        for j in range(start,end):
            result[ordered[j]]=(start+1+end)/2
        start=end
    return result

def correlation(a,b):
    am,bm=sum(a)/len(a),sum(b)/len(b)
    x=[v-am for v in a]; y=[v-bm for v in b]
    den=math.sqrt(sum(v*v for v in x)*sum(v*v for v in y))
    return sum(v*w for v,w in zip(x,y))/den if den else None

def main():
    wall_started=time.perf_counter()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--shortlist',required=True)
    p.add_argument('--ranking',required=True)
    p.add_argument('--baseline-phase',required=True)
    p.add_argument('--baseline-audit',required=True)
    p.add_argument('--helper-qa',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--seconds',type=float,default=300)
    p.add_argument('--candidate-limit',type=int,default=14)
    a=p.parse_args()
    require(math.isfinite(a.seconds) and 0<a.seconds<=300 and 1<=a.candidate_limit<=14,'Bounded limits required')
    out=path(a.out)
    require(not out.exists(),'Fresh output required')
    deadline=wall_started+a.seconds
    bindings={}
    def bind(p,expected=None):
        name,h=key(p),digest(p)
        require(expected is None or h==expected,'Changed dependency '+name)
        require(name not in bindings or bindings[name]==h,'Conflicting dependency')
        bindings[name]=h
        return h
    def load(p):
        bind(p)
        d=json.loads(path(p).read_bytes())
        for name,h in d.get('inputs_sha256',{}).items():
            bind(name,h)
        return d
    for source in (__file__,ROOT/'acceleration/audit_certificate.py'):
        bind(source)
    bind(ROOT/'acceleration/star_marginal_cp_cpu_v2.py',HELPER_SHA)
    qa=load(a.helper_qa)
    require(qa['status']=='STAR_SIMPLEX_PDHG_CPU_V2_REFERENCE_WARM_TRANSFER_AND_BOUNDED_QUALITY_CONTROLS_PASS','Missing helper QA')
    require(qa['operator_controls']['status']=='EXACT_TINY_SIMPLEX_ORACLE_AND_NUMERICAL_PDHG_CONTROLS_PASS','Missing exact small controls')
    require({key(p):h for p,h in qa['inputs_sha256'].items()}.get('acceleration/star_marginal_cp_cpu_v2.py')==HELPER_SHA,'Helper QA/source association')
    shortlist=load(a.shortlist); ranking=load(a.ranking)
    require(shortlist['status']=='BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED' and len(shortlist['records'])==14,'Expected14 solved CP-star observations')
    require(ranking['status']=='HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED','Unfinished ranking')
    family=load(ranking['family_path'])
    bind(ranking['family_path'],ranking['family_sha256'])
    fixed_scores={r['index']:r for r in ranking['ranked']}
    baseline_phase=load(a.baseline_phase); baseline_audit=load(a.baseline_audit)
    def evidence(phase,audit,phase_path,candidate_path):
        require(audit['status']=='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS','Missing star evidence')
        ab={key(p):h for p,h in audit['inputs_sha256'].items()}
        require(ab.get(key(phase_path))==digest(phase_path) and ab.get(key(candidate_path))==digest(candidate_path),'Star proof association')
        require(phase['projection_convention']==CONVENTION and phase['original_complete_domains_used'] and not phase['pair_pruned_domains_used'],'Wrong complete star objective')
        for name in ('candidate','domains','domain_audit'):
            bind(phase[name+'_path'],phase[name+'_sha256'])
        require(key(candidate_path)==key(phase['candidate_path']),'Wrong phase candidate')
        stars=load(phase['domains_path']); proof=load(phase['domain_audit_path'])
        require(stars['complete_domain_enumeration'] and len(stars['domains'])==84 and all(r['status']=='COMPLETE' for r in stars['domains']),'Incomplete original domains')
        require(proof['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'],'Missing independent domain completeness')
        pb={key(p):h for p,h in proof['inputs_sha256'].items()}
        require(pb.get(key(candidate_path))==digest(candidate_path) and pb.get(key(phase['domains_path']))==digest(phase['domains_path']),'Pair proof association')
        require([r['outer_vertex'] for r in proof['independently_reenumerated_domains']]==list(range(84)),'Incomplete84 independent domains')
        counts=[len(r['domain_masks_hex']) for r in stars['domains']]
        require(counts==phase['domain_counts']==[r['domain_size'] for r in proof['independently_reenumerated_domains']] and all(counts),'Wrong domain counts')
        offsets=np.r_[0,np.cumsum(counts)]
        p0=np.asarray(phase['numeric_probabilities'],dtype=float)
        y0=np.r_[phase['numeric_reciprocity_duals'],phase['numeric_cap_duals']]
        require(p0.shape==(int(offsets[-1]),) and y0.shape==(5166,) and np.all(np.isfinite(p0)) and np.all(p0>=0) and np.all(np.isfinite(y0)),'Bad saved vectors')
        require(np.all(y0<=1) and np.all(y0[:1680]>=-1) and np.all(y0[1680:]>=0),'Bad saved dual boxes')
        require(max(abs(float(p0[start:end].sum())-1) for start,end in zip(offsets[:-1],offsets[1:]))<1e-10,'Bad saved probability simplexes')
        tables=[[int(m,16) for m in r['domain_masks_hex']] for r in stars['domains']]
        return stars,tables,p0,y0
    baseline_stars,baseline_tables,baseline_p,baseline_y=evidence(baseline_phase,baseline_audit,a.baseline_phase,baseline_phase['candidate_path'])
    require(baseline_phase['candidate_sha256']==family['candidate_sha256'],'Warm reference/family baseline mismatch')
    cases=[]
    for r in shortlist['records'][:a.candidate_limit]:
        i=r['proposal_index'];require(i in fixed_scores and r['audited'],'Missing score/exact star evidence')
        for field in ('candidate','result','audit'):
            bind(r[field+'_path'],r[field+'_sha256'])
        candidate=load(r['candidate_path']);phase=load(r['result_path']);audit=load(r['audit_path'])
        require(sorted(candidate['overlap_edges_outer_zero_based'])==family['overlap_candidates'][i],'Candidate/family identity mismatch')
        stars,tables,p_ref,y_ref=evidence(phase,audit,r['result_path'],r['candidate_path'])
        lower,upper=fraction(audit['exact_dual_lower']),fraction(audit['exact_primal_upper'])
        require(lower==fraction(r['exact_lower']) and upper==fraction(r['exact_upper']) and lower<=upper,'Wrong exact reference interval')
        cases.append(dict(index=i,candidate=candidate,phase=phase,stars=stars,tables=tables,p_ref=p_ref,y_ref=y_ref,lower=lower,upper=upper,record=r))
    ordered=sorted(cases,key=lambda c:c['upper'])
    require(all(x['upper']<y['lower'] for x,y in zip(ordered,ordered[1:])),'Exact optimum order unresolved')
    out.mkdir(parents=True)
    manifest=dict(status='BOUNDED_STAR_PDHG_SAVED_CANDIDATE_QUALITY_INPUTS_BOUND',inputs_sha256=dict(bindings),
                  candidate_indices=[c['index'] for c in cases],checkpoints=[500,2000],overall_seconds_cap=a.seconds,
                  starts=['cold_uniform_zero_dual','warm25496_exact_mask_and_dual'],eta=.9,theta=1,
                  numpy_version=np.__version__,scipy_version=scipy.__version__,float_type='float64',
                  thread_environment={n:os.environ[n] for n in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
                  baseline_phase_path=key(a.baseline_phase),baseline_phase_sha256=digest(a.baseline_phase),
                  reference_scope='Original complete84star sets, exact saved interval; no new domain or optimization run',
                  averaging='Arithmetic running average of new iterates, starting iteration1',best_scope='Initial point plus last and average at requested checkpoints only')
    dump(out/'manifest.json',manifest)
    completed=[]; cutoff=False
    for case in cases:
        if time.perf_counter()>=deadline:
            cutoff=True;break
        index=case['index']; build_tick=time.perf_counter()
        model=build_model(case['candidate'],case['stars']['domains'])
        model_seconds=time.perf_counter()-build_tick
        reference=numeric_bounds(model,case['p_ref'],case['y_ref'])
        ref_error=max(abs(reference['primal_upper_numeric']-case['phase']['numeric_objective']),abs(reference['dual_lower_numeric']-case['phase']['numeric_simplex_dual_lower']))
        require(ref_error<1e-8,'Frozen CPU/reference model mismatch')
        require(model['counts'].tolist()==case['phase']['domain_counts'] and model['A'].nnz+model['A'].shape[1]==case['phase']['matrix_nonzeros'],'Matrix shape/order mismatch')
        tau,sigma=diagonal_steps(model)
        warm,transfer=transfer_probabilities(baseline_tables,baseline_p,case['tables'])
        cold=np.repeat(1.0/model['counts'],model['counts'])
        result=dict(index=index,candidate_path=case['record']['candidate_path'],candidate_sha256=case['record']['candidate_sha256'],
                    reference_audit_path=case['record']['audit_path'],reference_audit_sha256=case['record']['audit_sha256'],
                    exact_star_interval=[float(case['lower']),float(case['upper'])],reference_numeric_check=reference,
                    reference_max_error=ref_error,build_seconds=model_seconds,variables=model['A'].shape[1],nnz=model['A'].nnz,
                    warm_transfer=transfer,runs=[])
        for name,p0,y0 in [('cold_uniform_zero_dual',cold,np.zeros(5166)),('warm25496_exact_mask_and_dual',warm,baseline_y)]:
            if time.perf_counter()>=deadline:
                cutoff=True;break
            x,xbar,y=p0.copy(),p0.copy(),y0.copy()
            xavg,yavg=np.zeros_like(x),np.zeros_like(y)
            initial=numeric_bounds(model,x,y)
            best_upper,best_lower=initial['primal_upper_numeric'],initial['dual_lower_numeric']
            points=[]; tick=time.perf_counter(); iteration=0
            for iteration in range(1,2001):
                x,xbar,y=step(model,x,xbar,y,tau,sigma)
                xavg+=(x-xavg)/iteration;yavg+=(y-yavg)/iteration
                if iteration in (500,2000):
                    last,average=numeric_bounds(model,x,y),numeric_bounds(model,xavg,yavg)
                    simplex=max(abs(float(x[start:end].sum())-1) for start,end in zip(model['offsets'][:-1],model['offsets'][1:]))
                    require(simplex<1e-10 and np.min(x)>=0 and np.all(np.isfinite(x)) and np.all(np.isfinite(y)),'Numerical iterate invariant')
                    for point in (last,average):
                        require(point['primal_upper_numeric']>=float(case['lower'])-1e-7 and point['dual_lower_numeric']<=float(case['upper'])+1e-7,'Approximation contradicts exact reference')
                        best_upper=min(best_upper,point['primal_upper_numeric']);best_lower=max(best_lower,point['dual_lower_numeric'])
                    points.append(dict(iterations=iteration,last=last,average=average,best_upper_numeric=best_upper,best_lower_numeric=best_lower,elapsed_seconds=time.perf_counter()-tick,simplex_max_error=simplex))
                if iteration%16==0 and time.perf_counter()>=deadline:
                    cutoff=True;break
            result['runs'].append(dict(start=name,initial=initial,checkpoints=points,iterations_executed=iteration,complete=iteration==2000,elapsed_seconds=time.perf_counter()-tick))
            print(json.dumps(dict(index=index,start=name,iterations=iteration,checkpoints=points,overall_seconds=time.perf_counter()-wall_started)),flush=True)
            if cutoff:break
        dump(out/f'index_{index}.json',result);completed.append(result)
        if cutoff:break
    metrics=[]
    all_truth={c['index']:c for c in cases}
    for mode in manifest['starts']:
        for iteration in (500,2000):
            available={r['index']:p for r in completed for run in r['runs'] if run['start']==mode for p in run['checkpoints'] if p['iterations']==iteration}
            if not available:continue
            indices=sorted(available)
            truth=[float((all_truth[i]['lower']+all_truth[i]['upper'])/2) for i in indices]
            k=min(4,len(indices)); true_top=set(sorted(indices,key=lambda i:all_truth[i]['upper'])[:k])
            for field in ('best_upper_numeric','last_upper','average_upper','best_lower_numeric','last_lower','average_lower','fixed_dual'):
                def value(i):
                    cp=available[i]
                    if field=='fixed_dual':return Fraction(fixed_scores[i]['score_numerator'],fixed_scores[i]['denominator'])
                    if field in ('best_upper_numeric','best_lower_numeric'):return cp[field]
                    which,bound=field.split('_')
                    return cp[which]['primal_upper_numeric' if bound=='upper' else 'dual_lower_numeric']
                vals=[value(i) for i in indices]
                selected=sorted(indices,key=lambda i:(value(i),i))[:k]
                metrics.append(dict(start=mode,iterations=iteration,score=field,coverage=len(indices),indices=indices,
                                    spearman=correlation(ranks(vals),ranks(truth)),pearson=correlation(list(map(float,vals)),truth),
                                    top_k=k,predicted_top=selected,actual_top=sorted(true_top),top_k_recall=len(set(selected)&true_top)/k,
                                    comparison_scope='Only candidates with this completed checkpoint; lower values rank first for both upper and lower hints'))
    artifacts={key(out/f'index_{r["index"]}.json'):digest(out/f'index_{r["index"]}.json') for r in completed}
    artifacts[key(out/'manifest.json')]=digest(out/'manifest.json')
    require(all(digest(p)==h for p,h in bindings.items()),'Input changed during bounded study')
    summary=dict(status='BOUNDED_STAR_PDHG_QUALITY_STUDY_FINISHED' if not cutoff else 'BOUNDED_STAR_PDHG_QUALITY_STUDY_TIME_CAP',
                 inputs_sha256=bindings,outputs_sha256=artifacts,requested_candidates=len(cases),recorded_candidates=len(completed),
                 requested_runs=2*len(cases),recorded_runs=sum(len(r['runs']) for r in completed),
                 complete2000_runs=sum(run['complete'] for r in completed for run in r['runs']),time_cap_reached=cutoff,
                 elapsed_seconds=time.perf_counter()-wall_started,metrics=metrics,
                 records=[dict(index=r['index'],path=key(out/f'index_{r["index"]}.json'),sha256=digest(out/f'index_{r["index"]}.json'),exact_star_interval=r['exact_star_interval']) for r in completed],
                 lp_runs=0,gpu_runs=0,new_domain_enumerations=0,exclusions_claimed=0,numerical_scores_are_proofs=False,
                 scope='Retrospective selected14 CP/local-gate-passing candidates. PDHG scores and their correlations are numerical ranking diagnostics, not audited bounds or general performance estimates. A time cap only reduces reported coverage.')
    dump(out/'summary.json',summary)
    lines=['Saved14-candidate CPU PDHG quality study','',f"Status: {summary['status']}; complete2000 runs: {summary['complete2000_runs']}/{summary['requested_runs']}; wall seconds: {summary['elapsed_seconds']:.2f}.",'',
           '| Start | Iterations | Ranking hint | N | Spearman | Top4 recall | Selected indices |','|---|---:|---|---:|---:|---:|---|']
    for r in metrics:
        if r['score'] not in ('best_upper_numeric','best_lower_numeric','fixed_dual'):continue
        rho='n/a' if r['spearman'] is None else f"{r['spearman']:.4f}"
        lines.append(f"| {r['start']} | {r['iterations']} | {r['score']} | {r['coverage']} | {rho} | {r['top_k_recall']:.2f} | {r['predicted_top']} |")
    lines.extend(['',summary['scope'],''])
    (out/'comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(dict(status=summary['status'],complete2000_runs=summary['complete2000_runs'],seconds=summary['elapsed_seconds'],summary_sha256=digest(out/'summary.json'))),flush=True)

if __name__=='__main__':
    main()
