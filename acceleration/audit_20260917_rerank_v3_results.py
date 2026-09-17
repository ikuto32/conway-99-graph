"""Independent5000-step scalar/model association, calibration and selection."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import numpy as np
import audit_20260917_whole_fresh_ranking as cold

def q(x):return Fraction(int(x['numerator']),int(x['denominator']))
def stored(v):return dict(numerator=str(v.numerator),denominator=str(v.denominator),approximate=float(v))

def calibration_stats(rows):
    ids=[r['proposal_index']for r in rows];cold.require(len(ids)==len(set(ids))==16,'calibration population')
    byid={r['proposal_index']:r for r in rows};pair_records=[];ambiguous=[];separated=[]
    orders={}
    for label in ('iterations500','iterations5000'):
        orders[label]={k:sorted(ids,key=lambda i:(byid[i][label][k+'_numeric'],i))for k in ('lower','upper')}
    for i,j in combinations(ids,2):
        a,b=byid[i],byid[j]
        if q(a['exact_upper'])<q(b['exact_lower']):small,large=i,j
        elif q(b['exact_upper'])<q(a['exact_lower']):small,large=j,i
        else:
            ambiguous.append([i,j]);pair_records.append(dict(pair=[i,j],exact_relation='AMBIGUOUS_OVERLAPPING_OR_TOUCHING'));continue
        row=dict(pair=[i,j],exact_relation='STRICTLY_SEPARATED',exact_smaller=small,exact_larger=large)
        for label in orders:
            row[label]={k:dict(disagreement=orders[label][k].index(small)>orders[label][k].index(large),
                numerical_tie=byid[small][label][k+'_numeric']==byid[large][label][k+'_numeric'])for k in ('upper','lower')}
        separated.append(row);pair_records.append(row)
    result={}
    for label in orders:
        gaps=[Fraction.from_float(float(r[label]['upper_numeric']))-Fraction.from_float(float(r[label]['lower_numeric']))for r in rows]
        violations=[dict(proposal_index=r['proposal_index'],endpoint=k)for r in rows for k in ('lower','upper')if
            (Fraction.from_float(float(r[label][k+'_numeric']))>q(r['exact_'+k])if k=='lower'else Fraction.from_float(float(r[label][k+'_numeric']))<q(r['exact_'+k]))]
        result[label]=dict(mean_gap=stored(statistics.mean(gaps)),median_gap=stored(statistics.median(gaps)),
            individual_gaps=[dict(proposal_index=i,gap=stored(g))for i,g in zip(ids,gaps)],
            lower_endpoint_violations=sum(v['endpoint']=='lower'for v in violations),upper_endpoint_violations=sum(v['endpoint']=='upper'for v in violations),
            total_endpoint_violations=len(violations),endpoint_check_count=32,cases_with_endpoint_violations=len({v['proposal_index']for v in violations}),
            calibration_case_count=16,endpoint_violation_records=violations,exact_separated_pair_denominator=len(separated),
            **{k+'_order_disagreements':sum(p[label][k]['disagreement']for p in separated)for k in ('upper','lower')},
            **{k+'_score_ties_among_separated_pairs':sum(p[label][k]['numerical_tie']for p in separated)for k in ('upper','lower')})
    old,new=result['iterations500'],result['iterations5000']
    improvement={k:q(new[k])<q(old[k])for k in ('mean_gap','median_gap')}
    improvement.update({k+'_order_disagreements':new[k+'_order_disagreements']<old[k+'_order_disagreements']for k in ('upper','lower')})
    improvement['both_gap_statistics']=improvement['mean_gap']and improvement['median_gap']
    return dict(statistics=result,strict_empirical_improvement=improvement,total_calibration_pairs=120,exact_separated_pairs=len(separated),
        ambiguous_exact_pairs=len(ambiguous),ambiguous_pair_ids=ambiguous,pair_records=pair_records,calibration_cases=16,
        reranked_existing_candidates=128,new_candidates=0,next_LP_eligible_candidates=112,numeric_statistics_certify_GPU_arithmetic=False,
        target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    cold.require(not cold.path(a.out).exists(),'preserve prior audit');start=time.perf_counter();bindings={}
    def bind(p,h=None):
        k=cold.key(p)
        if k not in bindings:bindings[k]=cold.digest(p)
        cold.require(h is None or h==bindings[k],'changed bound input '+k);return bindings[k]
    def read(p):
        bind(p);d=json.loads(cold.path(p).read_bytes())
        for field in ('inputs_sha256','outputs_sha256'):
            for f,h in d.get(field,{}).items():bind(f,h)
        return d
    for f in (__file__,cold.__file__,'acceleration/review_star_pdhg_gpu.py','acceleration/star_marginal_cp_cpu_v2.py','uv.lock'):bind(f)
    run=cold.path(a.run);summary=read(run/'summary.json');metrics=read(run/'calibration_metrics.json');execution=read(run/'manifest.json')
    prep=read(summary['preparation_path']);bind(summary['preparation_path'],summary['preparation_sha256'])
    old=read(prep['source_ranking_path']);old_audit=read(prep['source_audit_path']);scope=read(prep['calibration_review_path'])
    bind(prep['source_audit_path'],'34f72e00cf1b6e734b6be706c12ce414d8978a6f24803e648eefbc0d19bb8788')
    bind(prep['calibration_review_path'],'f023c28c8f82388c69ea56af5b91785853bb7519c51044371a957743fc6072d1')
    input_gate=read(execution['input_review_path']);bind(execution['input_review_path'],'012cbae529722638288cf529ab60f045fcd036a7eef5828d7ee8d44926745311')
    supplement=read('acceleration/results/20260917_independent_review/rerank_v3_calibration_gate.json')
    bind('acceleration/results/20260917_independent_review/rerank_v3_calibration_gate.json','e8ac76f56818c9face7879ca2d791e2f8d05fcf41bb5b17a76b364096fccbca4')
    cold.require(summary['status']=='NUMERICAL_WHOLE_STAR_RERANK_V3_FINISHED'and summary['objective_id']=='ORIGINAL_STAR_SIMPLEX_PDHG_V1'and
        summary['iterations']==5000 and summary['source_iterations']==500 and summary['reranked_candidates']==128 and summary['new_candidates']==0 and summary['unavailable_count']==0,'completed reranking scope')
    cold.require(summary['original_complete_domains_used']is True and summary['pair_pruned_domains_used']is False and summary['independently_audited_original_domains']is False and
        summary['domain_enumeration_processes']==summary['model_exporter_invocations']==summary['LP_runs']==summary['exclusions_claimed']==0 and summary['GPU_processes']==4 and summary['numerical_scores_are_proofs']is False,'scope flags')
    ids=prep['input_selected_indices'];excluded=scope['selected_indices'];oldrows={r['proposal_index']:r for r in old['records']}
    cold.require(summary['input_selected_indices']==ids==old_audit['input_selected_indices']and summary['excluded_LP_tested_indices']==excluded and len(set(ids))==128,'input/exclusion mapping')
    rows=summary['records'];cold.require([r['proposal_index']for r in rows]==ids,'record order')
    byid={r['proposal_index']:r for r in rows};normalized=[]
    for r,oldr in zip(rows,prep['records']):
        comparable={k:v for k,v in r.items()if k not in ('status','best_lower_numeric','best_upper_numeric')}
        cold.require(comparable=={k:v for k,v in oldr.items()if k not in ('status','best_lower_numeric','best_upper_numeric')}and r['status']=='NUMERICALLY_RERANKED','unchanged graph/domain metadata')
        orig=next(t for t in old_audit['records']if t['proposal_index']==r['proposal_index']);nr=dict(orig)
        nr.update(status='NUMERICALLY_RERANKED',best_lower_numeric=r['best_lower_numeric'],best_upper_numeric=r['best_upper_numeric']);normalized.append(nr)
    control_ids=[ids[0],ids[64],ids[-1]];controls=[];inspected=[];initial_errors=[]
    for c,chunk in zip(prep['chunks'],summary['chunks']):
        j=c['chunk_index'];cold.require(chunk['chunk_index']==j and chunk['return_code']==0,'successful chunk')
        cold.require([cold.key(p)for p in chunk['command']]==['acceleration/build/star_pdhg_gpu.exe',cold.key(c['input_path']),cold.key(chunk['gpu_output_path'])],'GPU exact command')
        bind(c['input_path'],c['input_sha256']);cold.require(input_gate['inputs_sha256'][cold.key(c['input_path'])]==c['input_sha256'],'independent unchanged payload identity')
        gpu=read(chunk['gpu_output_path']);bind(chunk['gpu_output_path'],chunk['gpu_output_sha256']);checkpoints,models=cold.parse_binary(c['input_path'])
        cold.require(checkpoints==[5000]and len(models)==len(c['cases'])==len(gpu['results'])==32,'binary/result inventory')
        cold.require(gpu['status']=='NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED'and gpu['eta']==.9 and gpu['theta']==1 and gpu['float_type']=='float64'and
            gpu['initialization']=='uniform_per_simplex_probability_zero_dual'and gpu['best_scope']=='initial_and_requested_checkpoint_last_and_average'and
            gpu['numerical_scores_are_proofs']is False and gpu['scalar_metrics_computed_on_host']is True,'GPU numerical convention')
        for k,(case,model,result)in enumerate(zip(c['cases'],models,gpu['results'])):
            i=case['proposal_index'];cold.require(case['record_sha256']==model['record_sha256']and model['start']==case['record_byte_offset']and model['end']-model['start']==case['byte_length'],'record identity')
            cold.inspect_gpu_result(result,k,model,[5000]);point=result['checkpoints'][0]
            cold.require(byid[i]['best_upper_numeric']==point['best_upper_numeric']and byid[i]['best_lower_numeric']==point['best_lower_numeric'],'raw numerical score mapping')
            initial=cold.bounds(model,np.repeat(1./np.diff(model['offsets']),np.diff(model['offsets'])),np.zeros(5166))
            error=max(abs(initial[f]-result['initial'][f])for f in cold.METRICS);cold.require(error<=2e-8,'initial scalar parity');initial_errors.append(error)
            if i in control_ids:controls.append(dict(proposal_index=i,iterations=5000,**cold.compare_cpu(cold.replay_cpu(model,[5000]),result)))
            inspected.append(i)
        del models
        print(json.dumps(dict(chunk_checked=j,models=len(inspected),cpu_controls=len(controls))),flush=True)
    cold.require(inspected==ids and [r['proposal_index']for r in controls]==control_ids,'all128/sampled3 inventory')
    eligible=set(ids)-set(excluded);upper=sorted(eligible,key=lambda i:(byid[i]['best_upper_numeric'],i));lower=sorted(eligible,key=lambda i:(byid[i]['best_lower_numeric'],i))
    selection=cold.evaluation_selection(upper,lower,16,'union')
    cold.require(len(eligible)==summary['eligible_for_next_LP']==112 and upper==summary['eligible_ranked_by_upper']and lower==summary['eligible_ranked_by_lower']and selection==summary['proposed_union16'],'eligible112/union16 selection')
    old_orders={k:sorted(ids,key=lambda i:(oldrows[i]['best_'+k+'_numeric'],i))for k in ('upper','lower')}
    new_orders={k:sorted(ids,key=lambda i:(byid[i]['best_'+k+'_numeric'],i))for k in ('upper','lower')}
    expected_calibration=[]
    for exact in scope['records']:
        i=exact['proposal_index'];lo,hi=q(exact['exact_lower']),q(exact['exact_upper']);r=dict(proposal_index=i,exact_lower=exact['exact_lower'],exact_upper=exact['exact_upper'],numerical_scores_are_certificates=False)
        for label,source,order in [('iterations500',oldrows,old_orders),('iterations5000',byid,new_orders)]:
            low,up=source[i]['best_lower_numeric'],source[i]['best_upper_numeric']
            r[label]=dict(lower_numeric=low,upper_numeric=up,gap_numeric=up-low,upper_rank_among128=order['upper'].index(i)+1,lower_rank_among128=order['lower'].index(i)+1,
                numerical_lower_le_exact_lower=Fraction.from_float(float(low))<=lo,numerical_upper_ge_exact_upper=Fraction.from_float(float(up))>=hi,
                upper_minus_exact_upper_display=up-float(hi),exact_lower_minus_lower_display=float(lo)-low)
        expected_calibration.append(r)
    cold.require(summary['calibration']==metrics['all_calibration_cases']==expected_calibration,'all16 calibration exact/raw mapping')
    expected_metrics=calibration_stats(expected_calibration)
    cold.require(metrics['status']=='WHOLE_STAR_RERANK_V3_PREREGISTERED_CALIBRATION_METRICS'and all(metrics[k]==v for k,v in expected_metrics.items()),'independent exact metric/pair records')
    # Reject deliberately changed descriptive artifacts without new GPU work.
    metric_controls=[dict(name='complete_real16_calibration_and120pairs',outcome='PASS')]
    for name in ('mean_gap','pair_disagreement_count','missing_calibration_pair'):
        bad=json.loads(json.dumps(expected_metrics))
        if name=='mean_gap':bad['statistics']['iterations5000']['mean_gap']['numerator']='0'
        if name=='pair_disagreement_count':bad['statistics']['iterations5000']['upper_order_disagreements']+=1
        if name=='missing_calibration_pair':bad['pair_records'].pop()
        cold.require(bad!=expected_metrics,'ineffective corrupted metric control');metric_controls.append(dict(name=name,outcome='REJECT'))
    cold.require(all(cold.digest(f)==h for f,h in bindings.items()),'evidence changed during review')
    result=dict(status='INDEPENDENT_WHOLE_STAR_RERANK_V3_AUDIT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=execution['source_commit'],
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        ranking_summary_path=cold.key(run/'summary.json'),ranking_summary_sha256=bind(run/'summary.json'),records=normalized,
        family_path=old_audit['family_path'],family_sha256=old_audit['family_sha256'],family_audit_path=old_audit['family_audit_path'],family_audit_sha256=old_audit['family_audit_sha256'],
        input_selected_indices=ids,excluded_LP_tested_indices=excluded,eligible_ranked_by_upper=upper,eligible_ranked_by_lower=lower,
        eligible_ranked_by_upper_indices=upper,eligible_ranked_by_lower_indices=lower,
        ranked_by_upper_indices=upper,ranked_by_lower_indices=lower,evaluation_selections={'union_16':selection},numeric_cpu_controls=controls,
        maximum_initial_scalar_error=max(initial_errors),unchanged_independently_reconstructed_models=128,model_reconstruction_repeated_here=False,
        exact_payload_identity_dependency=cold.key(execution['input_review_path']),calibration=expected_calibration,calibration_metrics=expected_metrics,metric_controls=metric_controls,
        producer_or_native_imported=False,producer_model_builder_used=False,independent_domain_enumeration_performed=False,
        original_serialized_models_independently_verified_via_reuse=True,new_model_reconstruction_performed=False,
        payload_identity_review_path=cold.key(execution['input_review_path']),payload_identity_review_sha256=bind(execution['input_review_path']),
        original_model_audit_path=cold.key(prep['source_audit_path']),original_model_audit_sha256=bind(prep['source_audit_path']),
        numerical_scores_are_proofs=False,exclusions_claimed=0,LP_runs=0,GPU_runs=0,
        shared_trusted_components=['NumPy/SciPy','prior independent parser/bounds/CPU recurrence','CPU simplex projection shared with historical model library','hash-bound exact-byte proof and previous independent integer reconstruction'],
        scope='All1285000 scalar/model associations,3sampledCPUrecurrences,all16exact calibration mappings/120pair statistics and frozen112eligible union16; no mathematical certificate fromGPU',target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-start)
    cold.path(a.out).open('x',encoding='utf8').write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],selected=[r['proposal_index']for r in selection],empirical=expected_metrics['strict_empirical_improvement'],sha256=cold.digest(a.out))))

if __name__=='__main__':main()
