"""Index audited v3 reranking untested shortlist and independent exact scope.

Copied scientific indexing checks from frozen build_fresh_star_checkpoint.py;
whole-family identity, union16 and separate review gates are new. No solve.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
from math import isfinite
import re

from build_cp_completion_checkpoint import Index, ROOT, require, resolve, key, fraction
from build_star_guided_checkpoint import inspect_record, choose_best, rational, OBJECTIVE
from build_star_dual_shortlist_checkpoint import resolve_empty_pair

PINS={
    'build_cp_completion_checkpoint.py':'3ce94bbdd49f9a6f216bb87d2f75ee3e6e2ad6f24dea198c4d4a5b0ba08a5b4f',
    'build_star_guided_checkpoint.py':'ff9b952e21e0ee569a93c0894e0a04c09b68d02e0c2e62daab47c3487263c242',
    'build_star_dual_shortlist_checkpoint.py':'bbf1cbd9f745568f8b46af4d741cc5af9dcf6adee2c0abe64a6d8d99e320845f',
    'audit_phase1_kkt.py':'c8efc709bcd10dc11d1f7ef3013a84cd834708880f09af5e026ee8cf3eda2d34',
    'audit_certificate.py':'22d3e334930f734890216f18cfc8335c0a5c046f142a72e5a30beca6be9f1c9d',
    'audit_goal_theory_pairs.py':'9da60c600c45c16274efd05db0cf3c21cab8a61969dd2fe0d372ac9a2e7be75f',
    'phase1_probe_precise.py':'7b77d2b4f201706d7ec5fe06d7729e34cf9d9180d7b15d7411c939992ef491ad',
}
EVALUATOR_SHA='6f9d2b3e1eb25dc1dd41640993bc9523ee06722ab45ba730df4affb6c367582f'
RANK_AUDITOR_SHA='e4d70026be4cf1407bb01be39fafca75a13e83fb91f3e32113b3ffada05e40ed'
PINS['build_fresh_whole_v2_checkpoint.py']='fdc321d788d4fb6fccd82580112036001c6506c4a14dca0bd8b048a4a0a20536'
PINS['build_fresh_star_checkpoint.py']='f759b4dfe307b249774c3860eed1e65fb20d07ab2e27db7a3aadd699feb85680'


def rebuild_selection(audit,count,mode):
    require(type(count) is int and count==16 and mode=='union','Invalid cohort selection limits')
    all_indices=[r['proposal_index'] for r in audit['records']]
    require(len(all_indices)==len(set(all_indices))==128 and all(type(i) is int and i>=0 for i in all_indices),'Repeated or malformed rank attempt')
    require(all(type(r['available']) is bool for r in audit['records']),'Malformed ranking availability')
    require(all(r['available'] is True for r in audit['records']),'Full128 reranking required')
    excluded=audit['excluded_LP_tested_indices']
    require(len(excluded)==len(set(excluded))==16 and all(type(i) is int for i in excluded) and set(excluded)<=set(all_indices),'Frozen16 excluded IDs required')
    available=[r for r in audit['records'] if r['proposal_index'] not in excluded]
    require(len(available)==112,'Eligible112 population differs')
    require(all(type(r[k]) in (int,float) and isfinite(r[k]) for r in audit['records'] for k in ('best_upper_numeric','best_lower_numeric')),
        'Nonfinite ranked score')
    upper=[r['proposal_index'] for r in sorted(available,key=lambda r:(r['best_upper_numeric'],r['proposal_index']))]
    lower=[r['proposal_index'] for r in sorted(available,key=lambda r:(r['best_lower_numeric'],r['proposal_index']))]
    controls=audit['numeric_cpu_controls']
    require(len(controls)==min(3,len(available)) and len({r['proposal_index'] for r in controls})==len(controls) and
        all(r['proposal_index'] in all_indices for r in controls),'Numerical CPU replay coverage required')
    require(len(set(upper))==len(upper) and upper==audit['eligible_ranked_by_upper_indices'] and lower==audit['eligible_ranked_by_lower_indices'],
        'Independent rank inventory/order differs')
    order=[];roles={}
    sequences=[(upper[:count],'upper')] if mode=='upper' else [(upper[:count//2],'upper'),(lower[:count//2],'lower')]
    for sequence,role in sequences:
        for index in sequence:
            if index not in roles:order.append(index);roles[index]=[]
            roles[index].append(role)
    if mode=='union':
        for index in upper:
            if len(order)>=count:break
            if index not in roles:order.append(index);roles[index]=['upper_fill']
    result=[dict(proposal_index=i,selection_roles=roles[i]) for i in order]
    require(result==audit['evaluation_selections'][f'{mode}_{count}'],'Independent shortlist differs')
    return result,upper,lower


def compare_domain_sets(ranked,fresh,proof):
    require(ranked['complete_domain_enumeration'] is True and fresh['complete_domain_enumeration'] is True and
        proof['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'] is True and
        proof['propagation_status']=='ARC_CONSISTENT_NONEMPTY','Original full domain proof absent')
    require([r['outer_vertex'] for r in ranked['domains']]==list(range(84)) and
        [r['outer_vertex'] for r in fresh['domains']]==list(range(84)) and
        [r['outer_vertex'] for r in proof['independently_reenumerated_domains']]==list(range(84)),'Original84 inventory differs')
    for a,b,p in zip(ranked['domains'],fresh['domains'],proof['independently_reenumerated_domains']):
        left=[int(x,16) for x in a['domain_masks_hex']];right=[int(x,16) for x in b['domain_masks_hex']]
        require(left and len(left)==len(set(left))==len(right)==len(set(right))==p['domain_size'] and set(left)==set(right),
            'Ranking mask set differs from independently complete original domain')


def parent_improvement(records,lower):
    eligible=[r for r in records if r['audited'] and r['fixed_K_excluded'] and fraction(r['exact_lower'])>0 and fraction(r['exact_upper'])<lower]
    return min(eligible,key=lambda r:(fraction(r['exact_upper']),r['proposal_index'])) if eligible else None


def promote_to_parent(current,row):
    lower=fraction(current['exact_interval']['lower'])
    promotion=deepcopy(row)
    promotion['guaranteed_improvement']=rational(lower-fraction(row['exact_upper']))
    return choose_best(current,[promotion],lower)


def check_warm(book,row):
    require(row['edge_LP_status']=='STRICTLY_AUDITED_RESTART_WARM','Best candidate lacks strict restart warm state')
    phase=book.read(row['edge_phase1_path']);audit=book.read(row['edge_phase1_audit_path'],'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS')
    require(key(phase['candidate_path'])==key(row['candidate_path']) and phase['candidate_sha256']==row['candidate_sha256'] and
        phase['optimal'] is True and phase['source_sha256'].get('phase1_probe_precise.py')==PINS['phase1_probe_precise.py'] and
        phase['independent_audit_tolerance_changed'] is False and phase['requested_solver_tolerances']==dict(
            ipm_optimality_tolerance=1e-10,primal_feasibility_tolerance=1e-10,dual_feasibility_tolerance=1e-10),
        'Wrong candidate or source in precise edge warm')
    require(audit['numerical_tolerance']==1e-7 and audit['solver_or_producer_imported'] is False and
        audit['auditor_sha256']==PINS['audit_phase1_kkt.py'] and audit['graph_auditor_sha256']==PINS['audit_certificate.py'] and
        fraction(audit['exact_dual_lower_bound'])<=fraction(audit['exact_primal_upper_bound']) and fraction(audit['exact_primal_upper_bound'])>=0,
        'Invalid strict edge warm audit')
    for p in (row['candidate_path'],row['edge_phase1_path']):
        book.assert_bound(audit,p)



def check_whole_identity(ranking,audit,family,manifest):
    require(ranking['status']=='NUMERICAL_WHOLE_STAR_RERANK_V3_FINISHED' and
        ranking['iterations']==5000 and ranking['source_iterations']==500 and
        ranking['objective_id']==manifest['objective_id']=='ORIGINAL_STAR_SIMPLEX_PDHG_V1',
        'Wrong whole-ranking objective/version')
    require(ranking['original_complete_domains_used'] is True and ranking['pair_pruned_domains_used'] is False and
        ranking['independently_audited_original_domains'] is False and
        manifest['original_complete_domains_used'] is True and manifest['pair_pruned_domains_used'] is False,
        'Whole original-domain flags differ')
    require(family['status']=='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION' and family['selector']=='all' and
        len(family['moves'])==len(family['overlap_candidates'])==family['legal_count'],'Whole complete family required')
    ids=ranking['input_selected_indices']
    require(ids==audit['input_selected_indices']==[r['proposal_index'] for r in ranking['records']]==
        [r['proposal_index'] for r in audit['records']] and len(ids)==len(set(ids)),'Whole attempted identity differs')
    selected={r['proposal_index']:r for r in manifest['selected_candidates']}
    for numerical,checked in zip(ranking['records'],audit['records']):
        i=numerical['proposal_index']
        require(type(i) is int and 0<=i<family['legal_count'] and
            type(numerical['original_native_index']) is int and type(checked['original_native_index']) is int and
            numerical['original_native_index']==checked['original_native_index']==i,'Whole native identity differs')
        move=family['moves'][i]
        shape=sorted(len(c)//2 for c in move['alternating_cycles'])
        require(move['matching_class'] in ('same_0','same_1') and type(move['root_group']) is int and
            0<=move['root_group']<7 and sum(shape)==move['changed_edges'] and
            2<=sum(shape)<=6 and all(n>=2 for n in shape),'Invalid whole matching geometry')
        for row in [numerical]+([selected[i]] if i in selected else []):
            require(type(row['original_native_index']) is int and row['original_native_index']==i and
                row['root_group']==move['root_group'] and row['matching_class']==move['matching_class'] and
                row['changed_edges']==move['changed_edges'] and row['alternating_cycle_sizes']==shape,
                'Whole selected multi-cycle geometry differs')
        for field in ('candidate_path','candidate_sha256','domains_path','domains_sha256','best_upper_numeric','best_lower_numeric'):
            require(numerical[field]==checked[field],'Independent ranking artifact association differs')
        require((numerical['status']=='NUMERICALLY_RERANKED')==checked['available'],'Ranking availability differs')


def check_independent_review(book,args,summary):
    require(type(args.scope_auditor_sha256) is str and re.fullmatch('[0-9a-f]{64}',args.scope_auditor_sha256),
        'Freeze independent scope checker first')
    book.bind(args.scope_auditor,args.scope_auditor_sha256)
    scope=book.read(args.scope_review,'INDEPENDENT_WHOLE_STAR_RERANK_V3_SHORTLIST_AUDIT_PASS')
    exact=book.read(args.exact_review,'THIRD_PATH_EXACT_FIXED_K_STAR_REVIEW_PASS')
    for path in (args.evaluation,args.exact_review,args.scope_auditor):book.assert_bound(scope,path)
    book.assert_bound(exact,args.evaluation)
    require(key(scope['evaluation_path'])==key(args.evaluation) and scope['evaluation_sha256']==book.bind(args.evaluation) and
        key(scope['raw_review_path'])==key(args.exact_review) and scope['raw_review_sha256']==book.bind(args.exact_review) and
        scope['records']==exact['records'],'Independent review association differs')
    require(scope['selected_indices']==[r['proposal_index'] for r in summary['records']] and len(scope['selected_indices'])==16,
        'Independent scope review covers another selection')
    require([r['proposal_index'] for r in exact['records']]==scope['selected_indices'] and
        scope['producer_imported'] is False and scope['original_ranked_masks_unchanged'] is True,
        'Independent exact inventory/scope differs')
    for produced,checked in zip(summary['records'],exact['records']):
        require(checked['result']=='INDEPENDENT_RAW_CHECK_PASS' and checked['fixed_K_excluded'] is True and
            fraction(checked['exact_lower'])>0 and produced['audited'] is True and produced['fixed_K_excluded'] is True and
            fraction(produced['exact_lower'])==fraction(checked['exact_lower']) and
            fraction(produced['exact_upper'])==fraction(checked['exact_upper']),
            'Independent exact reviewed interval differs')
    independent_best=min(exact['records'],key=lambda r:(fraction(r['exact_upper']),r['proposal_index']))
    require(scope['best']==independent_best and summary['best']['proposal_index']==independent_best['proposal_index'],
        'Independently reviewed best differs')
    return scope


def build(args):
    require(all(type(h) is str and re.fullmatch('[0-9a-f]{64}',h) for h in (EVALUATOR_SHA,RANK_AUDITOR_SHA)),
        'Fresh evaluator and ranking auditor are not yet frozen')
    book=Index()
    for name,h in PINS.items():book.bind(ROOT/'acceleration'/name,h)
    book.bind(ROOT/'acceleration/evaluate_whole_star_rerank_v3.py',EVALUATOR_SHA)
    book.bind(ROOT/'acceleration/audit_20260917_rerank_v3_results.py',RANK_AUDITOR_SHA)
    book.bind(args.previous,args.previous_sha256);previous=book.read(args.previous)
    refs=previous['referenced_files_sha256']
    require(type(refs) is dict and len(refs)==previous['verified_referenced_file_count'] and refs,'Invalid parent inventory')
    for p,h in refs.items():
        require(type(h) is str and re.fullmatch('[0-9a-f]{64}',h),'Malformed parent hash');book.bind(p,h)
    require(previous['goal']['active'] is True and previous['goal']['complete'] is False and previous['graph_constructed'] is False and
        previous['general_nonexistence_proved'] is False and previous.get('pending_completion_work') is None and
        not previous.get('unselected_eligible_indices'),'Parent goal/pending state requires reassessment')
    current=previous['current_star_marginal_best']
    require(current['objective']==OBJECTIVE and current['comparison_to_old_edge_merit'] is False,'Parent uses another objective')
    current_audit=book.read(current['star_audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    current_lower=fraction(current['exact_interval']['lower'])
    require(0<current_lower<=fraction(current['exact_interval']['upper']) and current_audit['positive_exact_dual_excludes_fixed_K'] is True and
        fraction(current_audit['exact_dual_lower'])==current_lower and
        fraction(current_audit['exact_primal_upper'])==fraction(current['exact_interval']['upper']),'Parent exact interval differs')
    book.assert_bound(current_audit,current['best_candidate_path']);book.assert_bound(current_audit,current['star_phase1_path'])
    summary=book.read(args.evaluation,'BOUNDED_WHOLE_STAR_RERANK_SHORTLIST_V3_EVALUATION_FINISHED')
    scope_review=check_independent_review(book,args,summary)
    manifest=book.read(summary['manifest_path'],'WHOLE_STAR_RERANK_SHORTLIST_EVALUATION_MANIFEST_V3')
    require(summary['inputs_sha256']==manifest['inputs_sha256'] and summary['SAT_or_DRAT_invocations']==0 and
        summary['graph_constructed'] is False and summary['general_nonexistence_proved'] is False and summary['goal_marked_complete'] is False and
        manifest['merit']==OBJECTIVE and manifest['old_edge_merit_comparison'] is False and manifest['original_domain_set_identity_required'] is True,
        'Fresh evaluator scope/objective differs')
    book.assert_bound(manifest,ROOT/'acceleration/evaluate_whole_star_rerank_v3.py')
    ranking=book.read(manifest['ranking_path']);audit=book.read(manifest['ranking_audit_path'],'INDEPENDENT_WHOLE_STAR_RERANK_V3_AUDIT_PASS')
    book.assert_bound(audit,manifest['ranking_path']);book.assert_bound(audit,ROOT/'acceleration/audit_20260917_rerank_v3_results.py')
    require(key(audit['ranking_summary_path'])==key(manifest['ranking_path']) and audit['ranking_summary_sha256']==manifest['ranking_sha256'],
        'Ranking audit is bound to another summary')
    require(audit['producer_or_native_imported'] is False and audit['original_serialized_models_independently_verified_via_reuse'] is True and
        audit['new_model_reconstruction_performed'] is False and audit['independent_domain_enumeration_performed'] is False,'Wrong independent ranking scope')
    require(manifest['reranked_existing_candidates']==128 and manifest['new_ranked_candidates']==0 and
        manifest['excluded_LP_tested_indices']==audit['excluded_LP_tested_indices']==ranking['excluded_LP_tested_indices']==
        [r['proposal_index'] for r in previous['star_records']] and len(previous['star_records'])==16,
        'Prior checkpoint16 must exactly match the excluded LP-tested list')
    require(manifest['per_star_LP_seconds']==30 and manifest['independent_pair_seconds']==60,'Frozen evaluator limits differ')
    for prefix in ('original_model_audit','payload_identity_review'):
        require(key(audit[prefix+'_path'])==key(manifest[prefix+'_path']) and
            audit[prefix+'_sha256']==manifest[prefix+'_sha256'],'Reuse dependency association differs')
        book.assert_bound(audit,manifest[prefix+'_path'])
    original=book.read(manifest['original_model_audit_path'],'INDEPENDENT_WHOLE_FRESH_STAR_PDHG_RANKING_AUDIT_PASS')
    payload=book.read(manifest['payload_identity_review_path'],'INDEPENDENT_WHOLE_STAR_RERANK_V3_INPUT_PASS')
    require(original['all_serialized_models_reconstructed'] is True and original['producer_or_native_imported'] is False and
        payload['producer_imported'] is False and original['input_selected_indices']==payload['selected_indices']==ranking['input_selected_indices'] and
        payload['excluded_LP_tested_indices']==manifest['excluded_LP_tested_indices'],'Original exact model and full-byte identity scope differs')
    family=book.read(manifest['family_path']);family_audit=book.read(manifest['family_audit_path'])
    for field in ('family','family_audit'):
        require(key(audit[field+'_path'])==key(manifest[field+'_path']) and audit[field+'_sha256']==manifest[field+'_sha256'],'Rank/family association differs')
        book.assert_bound(audit,manifest[field+'_path'])
    require(family_audit['status']=='INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS' and
        family['status']=='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION' and family['selector']=='all' and
        family_audit['legal_count']==family['legal_count']==manifest['family_legal_candidates'],'Family proof/count differs')
    book.assert_bound(family_audit,manifest['family_path'])
    check_whole_identity(ranking,audit,family,manifest)
    selection,upper,lower=rebuild_selection(audit,manifest['max_candidates'],manifest['selection_mode'])
    require(ranking['proposed_union16']==selection and ranking['eligible_ranked_by_upper']==upper and ranking['eligible_ranked_by_lower']==lower and
        ranking['reranked_candidates']==128 and ranking['new_candidates']==0 and ranking['eligible_for_next_LP']==112 and ranking['unavailable_count']==0,
        'Reranking union/accounting differs')
    rank_rows={r['proposal_index']:r for r in audit['records']}
    selected=manifest['selected_candidates']
    require([dict(proposal_index=r['proposal_index'],selection_roles=r['selection_roles']) for r in selected]==selection and
        manifest['eligible_candidates']==len(upper) and manifest['ranking_attempted_candidates']==len(audit['records']) and
        manifest['unselected_ranked_indices']==[i for i in upper if i not in {r['proposal_index'] for r in selection}] and
        manifest['unavailable_ranking_indices']==[r['proposal_index'] for r in audit['records'] if not r['available']],
        'Cohort selection accounting differs')
    for row in selected:
        i=row['proposal_index'];rank=rank_rows[i]
        require(rank['available'] is True and key(row['candidate_path'])==key(rank['candidate_path']) and row['candidate_sha256']==rank['candidate_sha256'] and
            key(row['ranking_domains_path'])==key(rank['domains_path']) and row['ranking_domains_sha256']==rank['domains_sha256'] and
            all(row[k]==rank[k] for k in ('best_upper_numeric','best_lower_numeric')) and row['upper_rank']==upper.index(i)+1 and row['lower_rank']==lower.index(i)+1,
            'Selected candidate/rank/domain association differs')
        for p in (row['candidate_path'],row['ranking_domains_path']):book.assert_bound(audit,p)
        candidate=book.read(row['candidate_path'])
        require(candidate['overlap_edges_outer_zero_based']==family['overlap_candidates'][i],'Selected graph is not its family member')
    baseline=book.read(manifest['baseline_star_audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    evaluation_lower=fraction(baseline['exact_dual_lower'])
    require(0<evaluation_lower<=fraction(baseline['exact_primal_upper']) and baseline['positive_exact_dual_excludes_fixed_K'] is True and
        evaluation_lower==fraction(manifest['baseline_exact_lower']) and fraction(baseline['exact_primal_upper'])==fraction(manifest['baseline_exact_upper']),
        'Evaluation baseline interval differs')
    baseline_bindings={key(p):h for p,h in baseline['inputs_sha256'].items()}
    for name in ('star_marginal_phase1.py','audit_star_marginal_phase1.py'):
        require(baseline_bindings.get(key(ROOT/'acceleration'/name))==book.bind(ROOT/'acceleration'/name),'Evaluation objective source differs')
    records=summary['records']
    require([r['proposal_index'] for r in records]==[r['proposal_index'] for r in selected],'Cohort record inventory differs')
    for row,chosen in zip(records,selected):
        inspect_record(book,row,chosen,evaluation_lower)
        if row['audited'] or 'result_path' in row:
            local=resolve(row['gate_path']).parent
            compare_domain_sets(book.read(row['ranking_domains_path']),book.read(local/'stars.json'),book.read(row['independent_pair_audit_path']))
            require(row['original84_domain_sets_equal_ranking'] is True and row['ranking_domain_audit_independent'] is True,
                'Domain identity was not recorded')
    audited=sorted((r for r in records if r['audited']),key=lambda r:(fraction(r['exact_upper']),r['proposal_index']))
    require(summary['best']==(audited[0] if audited else None) and summary['exact_fixed_K_exclusions']==sum(r['fixed_K_excluded'] for r in records) and
        summary['exact_strict_improvement_count']==sum(r['exact_strict_improvement'] for r in records) and
        summary['pending_candidates']==[r for r in records if not r['fixed_K_excluded']] and
        summary['unselected_ranked_indices']==manifest['unselected_ranked_indices'],'Evaluator accounting differs')
    best_separated=bool(audited) and all(fraction(audited[0]['exact_upper'])<fraction(r['exact_lower']) for r in audited[1:])
    require(summary['best_interval_strictly_below_other_audited_intervals'] is best_separated,'Best interval separation differs')
    eval_best=parent_improvement(records,evaluation_lower)
    require(summary['edge_LP_runs']==int(eval_best is not None),'Unexpected edge warm solve count')
    for row in records:
        if eval_best is None or row['proposal_index']!=eval_best['proposal_index']:
            require(row['edge_LP_status']=='NOT_EVALUATED_UNLESS_STRICT_BEST' and 'edge_phase1_path' not in row and
                'edge_phase1_audit_path' not in row,'Nonbest candidate received an edge warm solve')
    warm_rows=[r for r in records if r['edge_LP_status']=='STRICTLY_AUDITED_RESTART_WARM']
    require(len(warm_rows)<=1 and all(eval_best is not None and r['proposal_index']==eval_best['proposal_index'] for r in warm_rows),
        'Edge warm supplied for another candidate')
    if warm_rows:
        check_warm(book,warm_rows[0]);require(summary['restart_seed']==warm_rows[0] and summary['pending_restart'] is None,'Restart warm receipt differs')
    else:
        require(summary['restart_seed'] is None and (summary['pending_restart'] is None)==(eval_best is None),'Pending warm state lost')
        if eval_best is not None:
            pending_warm=summary['pending_restart']
            require(pending_warm['proposal_index']==eval_best['proposal_index'] and key(pending_warm['candidate_path'])==key(eval_best['candidate_path']) and
                pending_warm['candidate_sha256']==eval_best['candidate_sha256'] and pending_warm['status']=='PENDING_EDGE_WARM_RESULT_OR_STRICT_AUDIT',
                'Pending edge warm association differs')
    resolutions=[resolve_empty_pair(book,p,records) for p in args.resolved_pair_audit]
    resolved={r['proposal_index'] for r in resolutions};require(len(resolved)==len(resolutions),'Duplicate pair resolution')
    pending=[r for r in summary['pending_candidates'] if r['proposal_index'] not in resolved]
    parent_best=parent_improvement(records,current_lower);adopted=None;frontier=current;pending_restart=None
    if parent_best is not None:
        if parent_best['edge_LP_status']=='STRICTLY_AUDITED_RESTART_WARM':
            check_warm(book,parent_best)
            frontier,adopted=promote_to_parent(current,parent_best)
        else:
            pending_restart=dict(proposal_index=parent_best['proposal_index'],candidate_path=parent_best['candidate_path'],
                candidate_sha256=parent_best['candidate_sha256'],status='PENDING_STRICT_EDGE_WARM_FOR_PARENT_IMPROVEMENT')
            pending.append(pending_restart)
    for path in args.extra_report:book.read(path)
    book.bind(Path(__file__));require(not (ROOT/'submission.txt').exists(),'Unexpected submission')
    return dict(status='HASH_VERIFIED_STAR_GUIDED_ROUND_CHECKPOINT',created_utc=datetime.now(timezone.utc).isoformat(),
        fresh_star_GPU_cohort=True,whole_star_rerank_v3=True,reranked_existing_candidates=128,new_ranked_candidates=0,
        excluded_prior_LP_indices=manifest['excluded_LP_tested_indices'],independent_scope_review_path=key(args.scope_review),
        independent_scope_review_sha256=book.bind(args.scope_review),independent_exact_review_path=key(args.exact_review),
        independent_exact_review_sha256=book.bind(args.exact_review),CP_round_claimed=False,goal=previous['goal'],current_best=previous['current_best'],current_star_marginal_best=frontier,
        graph_constructed=False,general_nonexistence_proved=False,submission_txt_exists=False,
        previous_checkpoint_preserved=dict(path=key(args.previous),sha256=book.bind(args.previous)),
        evaluation_path=key(args.evaluation),evaluation_sha256=book.bind(args.evaluation),
        evaluation_baseline_preserved=dict(audit_path=manifest['baseline_star_audit_path'],audit_sha256=manifest['baseline_star_audit_sha256'],
            exact_lower=manifest['baseline_exact_lower'],exact_upper=manifest['baseline_exact_upper']),
        adoption_compared_to_parent_star_lower=previous['current_star_marginal_best']['exact_interval']['lower'],
        current_star_best_changed=adopted is not None,adopted_star_index=adopted,star_records=records,
        star_evaluated_candidates=len(records),exact_star_exclusions=sum(r['fixed_K_excluded'] for r in records),exact_pair_exclusions=len(resolutions),
        resolved_pair_exclusions=resolutions,original_evaluation_pending_preserved=summary['pending_candidates'],
        original_evaluation_pending_restart_preserved=summary['pending_restart'],
        pending_completion_work=pending or None,pending_restart=pending_restart,unselected_eligible_indices=[],
        unselected_ranked_indices=manifest['unselected_ranked_indices'],unavailable_ranking_indices=manifest['unavailable_ranking_indices'],
        family_legal_candidates=manifest['family_legal_candidates'],ranking_attempted_candidates=manifest['ranking_attempted_candidates'],
        selection_mode=manifest['selection_mode'],previous_edge_positive_best_preserved=True,merits_compared_numerically=False,
        limits=dict(full_E0_or_Conway_coverage=False,general_nonexistence=False,graph_witness=False,
            numerical_PDHG_scores_are_exact_proofs=False,nonpositive_bound_means_feasible=False,all_family_star_LP_optimized=False),
        direct_artifacts_sha256=book.direct,report_statuses=book.statuses,referenced_files_sha256=book.verified,
        verified_referenced_file_count=len(book.verified),indexing_only_no_solver_or_domain_reruns=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous',type=Path,required=True);parser.add_argument('--previous-sha256',required=True)
    parser.add_argument('--evaluation',type=Path,required=True)
    parser.add_argument('--scope-review',type=Path,required=True)
    parser.add_argument('--scope-auditor',type=Path,required=True)
    parser.add_argument('--scope-auditor-sha256',required=True)
    parser.add_argument('--exact-review',type=Path,required=True)
    parser.add_argument('--resolved-pair-audit',type=Path,action='append',default=[])
    parser.add_argument('--extra-report',type=Path,action='append',default=[])
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args();require(not args.out.exists(),'Preserve old checkpoint')
    result=build(args)
    if not args.validate_only:
        with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=result['status'],references=result['verified_referenced_file_count'],adopted=result['adopted_star_index'],
        output_created=not args.validate_only)))


if __name__=='__main__':main()
