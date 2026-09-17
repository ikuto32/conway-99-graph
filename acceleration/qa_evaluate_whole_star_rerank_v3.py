"""Synthetic reranking evaluator handoff controls; no scientific artifacts."""
from copy import deepcopy
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path

import evaluate_whole_star_rerank_v3 as e


def fixtures():
    moves=[dict(root_group=i%7,matching_class='same_'+str(i%2),changed_edges=4,
        alternating_cycles=[[0,1,2,3],[4,5,6,7]]) for i in range(128)]
    family=dict(status='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION',selector='all',legal_count=128,
        overlap_candidates=[None]*128,moves=moves)
    rows=[dict(proposal_index=i,original_native_index=i,available=True,best_upper_numeric=130.+i,
        best_lower_numeric=128.-i,candidate_path='IN_MEMORY_ONLY',candidate_sha256='NOT_AN_ARTIFACT',
        domains_path='IN_MEMORY_ONLY',domains_sha256='NOT_AN_ARTIFACT') for i in range(128)]
    upper=list(range(16,128));lower=list(reversed(upper))
    audit=dict(status=e.RANKING_AUDIT_STATUS,producer_or_native_imported=False,
        original_serialized_models_independently_verified_via_reuse=True,new_model_reconstruction_performed=False,
        independent_domain_enumeration_performed=False,records=rows,input_selected_indices=list(range(128)),
        excluded_LP_tested_indices=list(range(16)),numeric_cpu_controls=[dict(proposal_index=i) for i in (0,64,127)],
        eligible_ranked_by_upper_indices=upper,eligible_ranked_by_lower_indices=lower,
        evaluation_selections={'union_16':e.evaluation_selection(upper,lower,16,'union')})
    ranking=dict(status='NUMERICAL_WHOLE_STAR_RERANK_V3_FINISHED',iterations=5000,source_iterations=500,
        objective_id=e.OBJECTIVE,original_complete_domains_used=True,pair_pruned_domains_used=False,
        independently_audited_original_domains=False,input_selected_indices=list(range(128)),
        records=[dict(**r,status='NUMERICALLY_RERANKED',root_group=moves[i]['root_group'],matching_class=moves[i]['matching_class'],
            changed_edges=4,alternating_cycle_sizes=[2,2]) for i,r in enumerate(rows)])
    return ranking,audit,family


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    e.require(not e.resolve(args.out).exists(),'Preserve controls');ranking,audit,family=fixtures();controls=[]
    e.verify_whole_records(ranking,audit,family);selected,upper,lower,unavailable=e.select_records(audit,family,16,'union')
    e.require([r['proposal_index'] for r in selected]==list(range(16,24))+list(range(127,119,-1)) and
        len(upper)==len(lower)==112 and unavailable==[],'Untested112 selection; excluded CPUcontrol remains permitted')
    controls.append(dict(name='HONEST_REUSE_UNTESTED112_UNION16_MULTICYCLE',outcome='ACCEPT'))
    same=deepcopy(audit)
    for row in same['records']:row['best_lower_numeric']=1.;row['best_upper_numeric']=2.
    same['eligible_ranked_by_lower_indices']=same['eligible_ranked_by_upper_indices']
    same['evaluation_selections']['union_16']=e.evaluation_selection(upper,upper,16,'union')
    s,_,_,_=e.select_records(same,family,16,'union')
    e.require([r['proposal_index'] for r in s]==list(range(16,32)) and s[0]['selection_roles']==['upper','lower'] and
        s[8]['selection_roles']==['upper_fill'],'Tie roles andfill')
    controls.append(dict(name='TIED_UNION_OVERLAP_FILL_UNTESTED_ONLY',outcome='ACCEPT'))
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as err:controls.append(dict(name=name,outcome='REJECT',reason=str(err)))
        else:raise ValueError('Accepted corruption: '+name)
    for name,change in (
        ('old_audit_status',lambda a:a.update(status='INDEPENDENT_WHOLE_FRESH_STAR_PDHG_RANKING_AUDIT_PASS')),
        ('unverified_reuse',lambda a:a.update(original_serialized_models_independently_verified_via_reuse=False)),
        ('false_new_reconstruction',lambda a:a.update(new_model_reconstruction_performed=True)),
        ('producer_import',lambda a:a.update(producer_or_native_imported=True)),
        ('false_domain_completeness',lambda a:a.update(independent_domain_enumeration_performed=True)),
        ('missing_CPU',lambda a:a.update(numeric_cpu_controls=[])),
        ('missing_case',lambda a:a['records'].pop()),('duplicate_ID',lambda a:a['records'][1].update(proposal_index=0)),
        ('boolean_native_ID',lambda a:a['records'][1].update(original_native_index=True)),
        ('missing_exclusion',lambda a:a['excluded_LP_tested_indices'].pop()),
        ('duplicate_exclusion',lambda a:a['excluded_LP_tested_indices'].__setitem__(0,1)),
        ('out_of_family_exclusion',lambda a:a['excluded_LP_tested_indices'].__setitem__(0,999)),
        ('bool_exclusion',lambda a:a['excluded_LP_tested_indices'].__setitem__(0,False)),
        ('unavailable',lambda a:a['records'][0].update(available=False)),
        ('nonfinite',lambda a:a['records'][0].update(best_upper_numeric=float('nan'))),
        ('inverted',lambda a:a['records'][0].update(best_lower_numeric=999.)),
        ('all128_ranklist',lambda a:a.update(eligible_ranked_by_upper_indices=list(range(128)))),
        ('selected_oldLP',lambda a:a['evaluation_selections']['union_16'][0].update(proposal_index=0)),
        ('wrong_roles',lambda a:a['evaluation_selections']['union_16'][0].update(selection_roles=['lower'])),
    ):
        a=deepcopy(audit);change(a);reject(name,lambda a=a:e.select_records(a,family,16,'union'))
    for name,change in (
        ('wrong_iteration',lambda r,a,f:r.update(iterations=500)),('wrong_previous_iteration',lambda r,a,f:r.update(source_iterations=2000)),
        ('filtered_objective',lambda r,a,f:r.update(objective_id='TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1')),
        ('filtered_flag',lambda r,a,f:r.update(pair_pruned_domains_used=True)),
        ('old_numerical_status',lambda r,a,f:r['records'][0].update(status='NUMERICALLY_SCORED')),
        ('changed_native_ID',lambda r,a,f:r['records'][0].update(original_native_index=1)),
        ('changed_geometry',lambda r,a,f:r['records'][0].update(alternating_cycle_sizes=[4])),
        ('changed_graph_hash',lambda r,a,f:a['records'][0].update(candidate_sha256='CORRUPTED')),
        ('changed_domain_hash',lambda r,a,f:a['records'][0].update(domains_sha256='CORRUPTED')),
        ('cross_family',lambda r,a,f:f.update(status='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION')),
    ):
        data=deepcopy([ranking,audit,family]);change(*data);reject(name,lambda data=data:e.verify_whole_records(*data))
    reject('wrong_selection_limit',lambda:e.select_records(audit,family,8,'union'))
    reject('wrong_selection_mode',lambda:e.select_records(audit,family,16,'upper'))
    inputs={e.key(p):e.digest(p) for p in (__file__,e.__file__)}
    for name,h in e.PINS.items():
        p=e.ROOT/'acceleration'/name;e.require(e.digest(p)==h,'Frozen producer dependency changed');inputs[e.key(p)]=h
    result=dict(status='WHOLE_STAR_RERANK_V3_EVALUATOR_CONTROLS_PASS',created_at=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=inputs,controls=controls,positive_controls=2,negative_controls=len(controls)-2,
        independent_verification=False,scientific_fixture_artifacts_written=False,GPU_processes=0,LP_runs=0,
        scope='Producer handoff controls; no domain enumeration or proof replay')
    e.save(args.out,result);print(json.dumps(dict(status=result['status'],negative_controls=result['negative_controls'],sha256=e.digest(args.out))))


if __name__=='__main__':main()
