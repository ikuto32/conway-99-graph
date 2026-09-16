"""Independently bind a fixed-dual ranked cohort to the current star frontier.

Native scores select only. Exact audited star bounds determine exclusions and
adoption. Unselected ranked proposals are not pending CP completion work.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re

from build_cp_completion_checkpoint import Index, ROOT, require, resolve, key, fraction
from build_star_guided_checkpoint import inspect_record, choose_best, rational, OBJECTIVE

PINS={
    'build_cp_completion_checkpoint.py':'3ce94bbdd49f9a6f216bb87d2f75ee3e6e2ad6f24dea198c4d4a5b0ba08a5b4f',
    'build_star_guided_checkpoint.py':'ff9b952e21e0ee569a93c0894e0a04c09b68d02e0c2e62daab47c3487263c242',
    'evaluate_star_dual_shortlist.py':'f5f9c2415bb34ec56017ab0b23b6858d56b7804bc4aaa06625bc0586572050fb',
    'audit_phase1_kkt.py':'c8efc709bcd10dc11d1f7ef3013a84cd834708880f09af5e026ee8cf3eda2d34',
    'audit_certificate.py':'22d3e334930f734890216f18cfc8335c0a5c046f142a72e5a30beca6be9f1c9d',
}


def signature(candidate):
    edges=candidate['overlap_edges_outer_zero_based']
    require(type(edges) is list and len(edges)==168 and all(type(e) is list and len(e)==2 and
            all(type(v) is int for v in e) and 0<=e[0]<e[1]<84 for e in edges), 'Malformed labeled K')
    require(edges==sorted(edges) and len(set(map(tuple,edges)))==168,'Repeated or unsorted edge')
    return tuple(map(tuple,edges))


def rank_selection(family,scores,ranking,cp,candidates,cap):
    """Independent raw-score ordering and exclusion by exact labeled graphs."""
    require(type(cap) is int and 1<=cap<=16,'Invalid cohort cap')
    require(family['status']=='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION' and family['selector']=='cross_3_4' and
            family['cycle_sizes']==[3,4],'Unsupported cross family')
    n=family['legal_count']
    require(n==len(family['overlap_candidates'])==len(family['moves'])==len(family['original_native_indices'])==
            scores['candidate_count']==len(scores['results'])==ranking['candidate_count']==cp['coarse_candidate_count'],
            'Candidate inventory differs')
    graphs=[signature(dict(overlap_edges_outer_zero_based=e)) for e in family['overlap_candidates']]
    require(len(set(graphs))==n,'Repeated family final')
    require(scores['status']=='HEURISTIC_FIXED_STAR_DUAL_BATCH_FINISHED' and scores['scores_are_certificates'] is False and
            ranking['status']=='HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED','Incorrect ranking scope/status')
    require(len(candidates)==len(cp['records'])==cp['probes']==64,'Expected all64 audited CP records')
    excluded=set();excluded_indices=[]
    for row,candidate in zip(cp['records'],candidates):
        i=row['proposal_index'];require(type(i) is int and 0<=i<n and i not in excluded_indices,'Bad CP family index')
        graph=signature(candidate);require(graph==graphs[i],'CP graph/family index differs')
        excluded.add(graph);excluded_indices.append(i)
    require(len(excluded)==64,'Repeated CP graph')
    available=[];unavailable=[]
    for i,value in enumerate(scores['results']):
        if value['status']!='COMPLETE_HEURISTIC_SCORE':
            require(value['status'] in ('UNAVAILABLE_EMPTY_DOMAIN','UNAVAILABLE_INCOMPLETE_DOMAINS') and
                    value['score'] is None and value['score_numerator'] is None,'Unavailable native score was ranked')
            unavailable.append(i);continue
        require(value['complete_domain_enumeration'] is True and value['local_empty_count']==0 and
                len(value['domain_counts'])==84 and all(type(k) is int and k>0 for k in value['domain_counts']) and
                type(value['score_numerator']) is int and value['denominator']==2**40,'Invalid available native score')
        available.append((value['score_numerator'],i))
    available.sort()
    require([r['index'] for r in ranking['ranked']]==[i for _,i in available] and
            ranking['complete_scores']==len(available) and ranking['unavailable_scores']==len(unavailable),'Ranking is incomplete or unordered')
    for row,(numerator,i) in zip(ranking['ranked'],available):
        move=family['moves'][i]
        require(row['score_numerator']==numerator and row['denominator']==2**40 and row['root_group']==move['root_group'] and
                row['cycle_size']==move['cycle_size'] and move['matching_class']=='cross' and
                row['original_native_index']==move['original_native_index']==family['original_native_indices'][i],
                'Ranked row score/move association differs')
    rank={i:position+1 for position,(_,i) in enumerate(available)}
    eligible=[i for _,i in available if graphs[i] not in excluded]
    return eligible[:cap],eligible[cap:],sorted(excluded_indices),rank,unavailable


def check_chosen(chosen,candidate,family,ranking_path,ranking_hash,family_path,family_hash,rank,scores):
    i=chosen['proposal_index'];move=family['moves'][i];score=scores['results'][i]
    require(candidate==chosen['candidate_document'] and signature(candidate)==signature(dict(overlap_edges_outer_zero_based=family['overlap_candidates'][i])),
            'Materialized cohort graph differs from selected family graph')
    require(candidate['status']=='FIXED_STAR_DUAL_SHORTLIST_CANDIDATE' and candidate['proposal_index']==i and
            key(candidate['family_path'])==key(family_path) and candidate['family_sha256']==family_hash and
            key(candidate['ranking_path'])==key(ranking_path) and candidate['ranking_sha256']==ranking_hash and
            candidate['ranking_score_numerator']==chosen['fixed_dual_score_numerator']==score['score_numerator'] and
            candidate['ranking_score_denominator']==chosen['fixed_dual_score_denominator']==score['denominator'] and
            chosen['fixed_dual_rank']==rank[i] and chosen['root_group']==move['root_group'] and
            chosen['cycle_size']==move['cycle_size'] and chosen['original_native_index']==move['original_native_index'],
            'Candidate/rank/move metadata differs')
    require(candidate['score_used_only_for_ordering'] is True and candidate['edge_LP_status']=='NOT_EVALUATED_BY_THIS_PIPELINE' and
            candidate['graph_constructed'] is False and candidate['fixed_K_excluded'] is False,'Native rank became a scientific claim')


def incumbent_improvers(records,lower):
    return sorted((r for r in records if r['audited'] and r['fixed_K_excluded'] and fraction(r['exact_lower'])>0 and
                   fraction(r['exact_upper'])<lower),key=lambda r:(fraction(r['exact_upper']),r['proposal_index']))


def resolve_empty_pair(book,audit_path,records):
    audit=book.read(audit_path,'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
    bindings={key(p):h for p,h in audit['inputs_sha256'].items()}
    matches=[r for r in records if bindings.get(key(r['candidate_path']))==r['candidate_sha256']]
    require(len(matches)==1,'Pair resolution has no unique cohort candidate')
    row=matches[0]
    require(row['fixed_K_excluded'] is False and row['audited'] is False,'Pair resolution must resolve an original pending row')
    local=resolve(row['gate_path']).parent
    for path in (row['candidate_path'],local/'stars.json',local/'pairs.json',ROOT/'acceleration/audit_goal_theory_pairs.py'):
        book.assert_bound(audit,path)
    require(audit['producer_or_solver_imported'] is False and audit['complete_used_domains_verified'] is True and
            audit['propagation_status']=='EMPTY_DOMAIN' and not audit.get('cap_reason'),'Incomplete/nonempty pair resolution')
    stars=book.read(local/'stars.json');proof=book.read(local/'pairs.json')
    require(stars['complete_domain_enumeration'] is True and proof['propagation_status']=='EMPTY_DOMAIN' and
            audit['empty_vertex']==proof['empty_vertex'] and audit['events_verified']==len(proof['events']) and
            not proof['surviving_domain_ids'][proof['empty_vertex']],'Pair empty-domain conclusion differs')
    used={proof['empty_vertex']}|{v for event in proof['events'] for v in (event['target_vertex'],event['support_vertex'])}
    complete=audit['independently_reenumerated_domains']
    require(len(complete)==len(used) and {r['outer_vertex'] for r in complete}==used and
            all(r['domain_size']==len(stars['domains'][r['outer_vertex']]['domain_masks_hex']) for r in complete),
            'Not every domain used in the contradiction was independently complete')
    return dict(proposal_index=row['proposal_index'],candidate_path=row['candidate_path'],candidate_sha256=row['candidate_sha256'],
        original_evaluation_status=row['status'],audit_path=key(audit_path),audit_sha256=book.bind(audit_path),
        domains_path=key(local/'stars.json'),domains_sha256=book.bind(local/'stars.json'),
        pair_certificate_path=key(local/'pairs.json'),pair_certificate_sha256=book.bind(local/'pairs.json'),
        resolution='INDEPENDENT_EMPTY_PAIR_DOMAIN_FIXED_K_EXCLUSION',independently_complete_used_vertices=sorted(used),
        events_verified=audit['events_verified'],empty_vertex=audit['empty_vertex'],fixed_K_excluded=True,
        star_LP_bound_claimed=False,full84_reenumeration_required_for_this_contradiction=False)


def build(args):
    book=Index()
    for name,expected in PINS.items():book.bind(ROOT/'acceleration'/name,expected)
    book.bind(args.previous,args.previous_sha256);previous=book.read(args.previous)
    require(previous['status'] in ('HASH_VERIFIED_STAR_GUIDED_ROUND_CHECKPOINT','HASH_VERIFIED_FIXED_STAR_DUAL_SHORTLIST_CHECKPOINT') and
            previous['goal']['active'] is True and previous['goal']['complete'] is False and previous['graph_constructed'] is False and
            previous['general_nonexistence_proved'] is False,'Invalid parent research state')
    refs=previous['referenced_files_sha256']
    require(len(refs)==previous['verified_referenced_file_count'] and len({key(p) for p in refs})==len(refs),'Bad parent reference inventory')
    for path,expected in refs.items():
        require(type(expected) is str and re.fullmatch('[0-9a-f]{64}',expected),'Malformed parent hash')
        book.bind(path,expected)
    old=previous['current_star_marginal_best']
    require(old['objective']==OBJECTIVE and old['comparison_to_old_edge_merit'] is False,'Changed incumbent objective')
    old_audit=book.read(old['star_audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    book.assert_bound(old_audit,old['best_candidate_path']);book.assert_bound(old_audit,old['star_phase1_path'])
    incumbent_lower=fraction(old['exact_interval']['lower'])
    require(0<incumbent_lower==fraction(old_audit['exact_dual_lower']) and
            fraction(old['exact_interval']['upper'])==fraction(old_audit['exact_primal_upper']),'Incumbent interval differs')
    directory=resolve(args.cohort)
    summary=book.read(directory/'summary.json','BOUNDED_FIXED_STAR_DUAL_SHORTLIST_EVALUATION_FINISHED')
    manifest=book.read(summary['manifest_path'],'FIXED_STAR_DUAL_SHORTLIST_EVALUATION_MANIFEST')
    require(key(summary['manifest_path'])==key(directory/'manifest.json') and summary['inputs_sha256']==manifest['inputs_sha256'] and
            summary['native_scores_are_exclusion_certificates'] is False and summary['CP_nearzero_eligibility_assumed'] is False and
            summary['edge_LP_runs']==summary['SAT_or_DRAT_invocations']==0 and summary['goal_marked_complete'] is False and
            summary['graph_constructed'] is False and summary['general_nonexistence_proved'] is False,'Wrong cohort scope')
    book.assert_bound(manifest,ROOT/'acceleration/evaluate_star_dual_shortlist.py')
    ranking=book.read(manifest['ranking_path'],'HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED')
    scores_path=resolve(manifest['ranking_path']).with_name('scores.json');scores=book.read(scores_path)
    comparison=book.read(manifest['comparison_path'],'FIXED_STAR_DUAL_CP_SELECTION_COMPARISON')
    family=book.read(manifest['family_path']);family_audit=book.read(manifest['family_audit_path'],'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS')
    cp=book.read(manifest['excluded_CP_summary_path'],'BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    cp_audit=book.read(manifest['excluded_CP_audit_path'],'INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS')
    for path in (manifest['ranking_path'],manifest['family_path'],manifest['family_audit_path'],manifest['excluded_CP_summary_path'],manifest['excluded_CP_audit_path']):
        require(refs.get(key(path))==book.bind(path),'Cohort source is outside parent checkpoint')
    book.assert_bound(ranking,scores_path);book.assert_bound(ranking,manifest['family_path']);book.assert_bound(ranking,manifest['family_audit_path'])
    book.assert_bound(family_audit,manifest['family_path']);book.assert_bound(cp_audit,manifest['excluded_CP_summary_path'])
    book.assert_bound(cp_audit,manifest['family_path']);book.assert_bound(comparison,manifest['ranking_path'])
    book.assert_bound(comparison,manifest['excluded_CP_summary_path'])
    require(family_audit['legal_count']==family['legal_count'] and family_audit['by_class']==family['by_class'] and
            key(cp['paths']['native'])==key(ranking['family_path'])==key(manifest['family_path']),'Family association differs')
    cp_reports={r['proposal_index']:r for r in cp_audit['probe_reports']}
    require(len(cp_reports)==len(cp_audit['probe_reports'])==cp_audit['actual_LP_exact_intervals_checked']==64,'Unaudited full CP inventory')
    cp_candidates=[]
    for row in cp['records']:
        report=cp_reports[row['proposal_index']]
        require(key(row['candidate_path'])==key(report['candidate_path']) and key(row['result_path'])==key(report['result_path']),
                'CP candidate audit association differs')
        book.assert_bound(cp_audit,row['candidate_path']);book.bind(row['candidate_path'],row['candidate_sha256'])
        cp_candidates.append(book.read(row['candidate_path']))
    indices,unselected,excluded,rank,unavailable=rank_selection(family,scores,ranking,cp,cp_candidates,manifest['max_candidates'])
    require([r['proposal_index'] for r in manifest['selected_candidates']]==indices and
            manifest['unselected_eligible_indices']==summary['unselected_eligible_indices']==unselected and
            manifest['excluded_CP_indices']==excluded and manifest['excluded_exact_CP_graphs']==64 and
            manifest['eligible_candidates']==len(indices)+len(unselected),'Independent ranked selection differs')
    require(comparison['cp_candidates_with_fixed_dual_rank']==[dict(index=i,rank=rank.get(i)) for i in excluded] and
            [r['index'] for r in comparison['first32_fixed_dual_candidates_outside_cp_selection']]==(indices+unselected)[:32],
            'Comparison inventory differs')
    baseline=book.read(manifest['baseline_star_audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    book.assert_bound(baseline,family['candidate_path']);book.assert_bound(ranking,manifest['baseline_star_audit_path'])
    baseline_lower=fraction(baseline['exact_dual_lower'])
    require(manifest['merit']==OBJECTIVE and manifest['old_edge_merit_comparison'] is False and
            0<baseline_lower==fraction(manifest['baseline_exact_lower']) and
            fraction(baseline['exact_primal_upper'])==fraction(manifest['baseline_exact_upper']), 'Ranking baseline changed')
    records=summary['records']
    require([r['proposal_index'] for r in records]==indices,'Missing/repeated cohort result')
    for row,chosen in zip(records,manifest['selected_candidates']):
        candidate=book.read(chosen['candidate_path']);book.bind(chosen['candidate_path'],chosen['candidate_sha256'])
        check_chosen(chosen,candidate,family,manifest['ranking_path'],manifest['ranking_sha256'],
                     manifest['family_path'],manifest['family_sha256'],rank,scores)
        selected={k:v for k,v in chosen.items() if k!='candidate_document'}
        inspect_record(book,row,selected,baseline_lower)
    audited=sorted((r for r in records if r['audited']),key=lambda r:(fraction(r['exact_upper']),r['proposal_index']))
    require(summary['best']==(audited[0] if audited else None) and summary['pending_candidates']==[r for r in records if not r['fixed_K_excluded']] and
            summary['exact_fixed_K_exclusions']==sum(r['fixed_K_excluded'] for r in records) and
            summary['exact_strict_improvement_count']==sum(r['exact_strict_improvement'] for r in records),'Cohort summary accounting differs')
    require(summary['best_interval_strictly_below_other_audited_intervals'] is (bool(audited) and
            all(fraction(audited[0]['exact_upper'])<fraction(r['exact_lower']) for r in audited[1:])),'Unjustified separated-best claim')
    improvers=incumbent_improvers(records,incumbent_lower)
    current,adopted=old,None
    if improvers:
        require(args.edge_warm is not None and args.edge_audit is not None,'An improving cohort K needs a separately audited edge warm start')
        best=deepcopy(improvers[0]);warm=book.read(args.edge_warm)
        warm_audit=book.read(args.edge_audit,'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS')
        book.assert_bound(warm_audit,best['candidate_path']);book.assert_bound(warm_audit,args.edge_warm)
        require(key(warm['candidate_path'])==key(best['candidate_path']) and warm['candidate_sha256']==best['candidate_sha256'] and
                warm_audit['auditor_sha256']==PINS['audit_phase1_kkt.py'] and warm_audit['graph_auditor_sha256']==PINS['audit_certificate.py'],
                'Improved candidate edge warm/audit association differs')
        best.update(edge_phase1_path=key(args.edge_warm),edge_phase1_sha256=book.bind(args.edge_warm),
                    exact_strict_improvement=True,guaranteed_improvement=rational(incumbent_lower-fraction(best['exact_upper'])))
        current,adopted=choose_best(old,[best],incumbent_lower)
    else:
        require(args.edge_warm is None and args.edge_audit is None,'No improving cohort seed: unexpected warm-start replacement')
    resolved=[resolve_empty_pair(book,path,records) for path in args.resolved_pair_audit]
    resolved_indices={r['proposal_index'] for r in resolved}
    require(len(resolved_indices)==len(resolved),'Duplicate pair resolution')
    pending=[]
    if previous.get('pending_completion_work'):
        old_pending=previous['pending_completion_work'];pending.extend(old_pending if isinstance(old_pending,list) else [old_pending])
    pending.extend(r for r in summary['pending_candidates'] if r['proposal_index'] not in resolved_indices)
    for path in args.extra_report:book.read(path)
    book.bind(Path(__file__))
    require(not (ROOT/'submission.txt').exists(),'Unexpected submission')
    return dict(status='HASH_VERIFIED_FIXED_STAR_DUAL_SHORTLIST_CHECKPOINT',created_utc=datetime.now(timezone.utc).isoformat(),
        goal=previous['goal'],current_best=previous['current_best'],current_star_marginal_best=current,
        graph_constructed=False,general_nonexistence_proved=False,submission_txt_exists=False,
        previous_checkpoint_preserved=dict(path=key(args.previous),sha256=book.bind(args.previous)),
        pending_completion_work=pending or None,unselected_eligible_indices=previous.get('unselected_eligible_indices',[]),
        unselected_ranked_indices=unselected,unavailable_native_score_indices=unavailable,
        cohort_path=key(directory),selected_ranked_indices=indices,excluded_CP_indices=excluded,distinct_excluded_CP_graphs=64,
        cohort_records=records,cohort_exact_fixed_K_exclusions=summary['exact_fixed_K_exclusions'],
        original_cohort_pending_candidates=summary['pending_candidates'],resolved_pair_exclusions=resolved,
        cohort_exact_pair_exclusions=len(resolved),cohort_total_exact_exclusions=summary['exact_fixed_K_exclusions']+len(resolved),
        ranking_baseline_exact_lower=manifest['baseline_exact_lower'],ranking_baseline_strict_improvement_count=summary['exact_strict_improvement_count'],
        incumbent_baseline_exact_lower=old['exact_interval']['lower'],incumbent_strict_improvement_count=len(improvers),
        current_star_best_changed=adopted is not None,adopted_star_index=adopted,
        native_rank_scores_used_as_proof=False,prior_CP_nearzero_assumed_for_cohort=False,
        old_edge_positive_best_preserved=True,merits_compared_numerically=False,
        limits=dict(full_E0_or_Conway_coverage=False,all_family_LP_optimized=False,graph_witness=False,
                    nonpositive_bounds_imply_feasible=False,unselected_ranked_proposals_are_pending_CP_completion=False),
        next_focus='Continue from the current exact star-merit seed; preserve any incomplete or nonpositive cases separately.',
        direct_artifacts_sha256=book.direct,report_statuses=book.statuses,referenced_files_sha256=book.verified,
        verified_referenced_file_count=len(book.verified),indexing_only_no_scientific_reruns=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous',type=Path,required=True)
    parser.add_argument('--previous-sha256',required=True)
    parser.add_argument('--cohort',type=Path,required=True)
    parser.add_argument('--edge-warm',type=Path)
    parser.add_argument('--edge-audit',type=Path)
    parser.add_argument('--resolved-pair-audit',type=Path,action='append',default=[])
    parser.add_argument('--extra-report',type=Path,action='append',default=[])
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args();require(not args.out.exists(),'Preserve prior index')
    result=build(args)
    if not args.validate_only:
        with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=result['status'],verified_files=result['verified_referenced_file_count'],
        star_best_changed=result['current_star_best_changed'],output_created=not args.validate_only)),flush=True)


if __name__=='__main__':main()
