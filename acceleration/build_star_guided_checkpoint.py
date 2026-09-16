"""Index one audited star-guided CP round; perform no scientific reruns."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from build_cp_completion_checkpoint import Index, ROOT, require, resolve, key, fraction
import json

INDEX_HELPER_SHA = '3ce94bbdd49f9a6f216bb87d2f75ee3e6e2ad6f24dea198c4d4a5b0ba08a5b4f'
EVALUATOR_SHA = '83cc10e42923ea5dfd6e39b81bee4ad19585539639045a03f9c812c97eac19ae'
OBJECTIVE = 'STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS'
PENDING = {'PENDING_NATIVE_GATE_FAILED_OR_CAPPED', 'PENDING_INCOMPLETE_INDEPENDENT_PAIR_AUDIT',
           'PENDING_NO_STAR_PRIMAL_DUAL', 'PENDING_NONPOSITIVE_EXACT_STAR_BOUND'}


def rational(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def select_from_cp(search, audit):
    rows = {r['proposal_index']:r for r in search['records']}
    reports = {r['proposal_index']:r for r in audit['probe_reports']}
    require(len(rows) == len(search['records']) == search['probes'] == len(reports) == len(audit['probe_reports']) ==
            audit['actual_LP_exact_intervals_checked'] and set(rows) == set(reports), 'CP inventory differs')
    selected = []
    for index, row in rows.items():
        report = reports[index]
        require(key(row['candidate_path']) == key(report['candidate_path']) and key(row['result_path']) == key(report['result_path']),
                'CP report candidate/result association differs')
        phase = report['phase1_audit']
        require(phase['status'] == 'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS', 'Unaudited CP phase')
        bindings = {key(p):h for p,h in phase['inputs_sha256'].items()}
        require(bindings.get(key(row['candidate_path'])) == row['candidate_sha256'] and
                bindings.get(key(row['result_path'])) == row['result_sha256'], 'CP interval is bound to different files')
        lo, hi = fraction(phase['exact_dual_lower_bound']), fraction(phase['exact_primal_upper_bound'])
        require(lo <= hi and hi >= 0, 'Invalid edge merit interval')
        if lo <= 0 and hi <= Fraction(1,100000000):
            selected.append(dict(proposal_index=index,candidate_path=key(row['candidate_path']),candidate_sha256=row['candidate_sha256'],
                edge_phase1_path=key(row['result_path']),edge_phase1_sha256=row['result_sha256'],
                exact_edge_lower=rational(lo),exact_edge_upper=rational(hi)))
    return sorted(selected,key=lambda r:(fraction(r['exact_edge_upper']),r['proposal_index']))


def check_baseline(previous, round_manifest, evaluation_manifest, baseline):
    old = previous['current_star_marginal_best']
    require(old['objective'] == evaluation_manifest['merit'] == OBJECTIVE and old['comparison_to_old_edge_merit'] is False and
            evaluation_manifest['old_edge_merit_comparison'] is False, 'Star objective changed')
    require(key(round_manifest['initial_candidate_path']) == key(old['best_candidate_path']) and
            round_manifest['initial_candidate_sha256'] == old['best_candidate_sha256'] and
            key(round_manifest['initial_edge_phase1_path']) == key(old['edge_phase1_path']) and
            round_manifest['initial_edge_phase1_sha256'] == old['edge_phase1_sha256'], 'Round does not start at prior star best')
    require(key(round_manifest['baseline_star_audit_path']) == key(evaluation_manifest['baseline_star_audit_path']) == key(old['star_audit_path'])
            and round_manifest['baseline_star_audit_sha256'] == evaluation_manifest['baseline_star_audit_sha256'] == old['star_audit_sha256'],
            'Star baseline audit identity changed')
    lower, upper = fraction(baseline['exact_dual_lower']), fraction(baseline['exact_primal_upper'])
    require(0 < lower <= upper and baseline['positive_exact_dual_excludes_fixed_K'] is True and
            lower == fraction(old['exact_interval']['lower']) == fraction(evaluation_manifest['baseline_exact_lower']) and
            upper == fraction(old['exact_interval']['upper']) == fraction(evaluation_manifest['baseline_exact_upper']), 'Star baseline interval changed')
    return lower


def check_audited_row(row, audit, replay, certificate, baseline_lower):
    lo, hi = fraction(audit['exact_dual_lower']), fraction(audit['exact_primal_upper'])
    require(lo <= hi and hi >= 0 and lo == fraction(row['exact_lower']) and hi == fraction(row['exact_upper']), 'Stored star interval differs')
    require(int(replay['integer_scale']) > 0 and Fraction(int(replay['exact_integer_gap']), int(replay['integer_scale'])) == lo and
            int(certificate['integer_scale']) == int(replay['integer_scale']) and
            int(certificate['integer_gap']) == int(replay['exact_integer_gap']) and
            fraction(certificate['exact_phase1_lower_bound']) == lo, 'Exact certificate arithmetic differs')
    positive = lo > 0
    require(row['fixed_K_excluded'] is positive and audit['positive_exact_dual_excludes_fixed_K'] is positive and
            replay['fixed_K_excluded'] is positive and certificate['fixed_K_excluded'] is positive,
            'Contradiction status is inconsistent with exact sign')
    require(row['status'] == ('FIXED_K_EXCLUDED_EXACT_STAR_CERTIFICATE' if positive else 'PENDING_NONPOSITIVE_EXACT_STAR_BOUND') and
            certificate['status'] == ('EXACT_STAR_MARGINAL_SIMPLEX_DUAL_CONTRADICTION' if positive else 'EXACT_STAR_MARGINAL_SIMPLEX_DUAL_BOUND'),
            'Contradiction/bound status differs')
    margin = baseline_lower-hi
    require(row['exact_strict_improvement'] is (margin > 0) and fraction(row['guaranteed_improvement']) == margin,
            'Strict improvement claim differs')
    return lo,hi


def inspect_record(book, row, selected, baseline_lower):
    require(all(row[k] == v for k,v in selected.items()), 'Evaluation selected candidate differs from CP audit')
    gate = book.read(row['gate_path'],'NATIVE_SHORTLIST_PAIR_GATE_FINISHED')
    require(key(gate['candidate_path']) == selected['candidate_path'] and gate['candidate_sha256'] == selected['candidate_sha256'] and
            row['native_passed'] is gate['passed'], 'Native gate candidate/decision differs')
    book.assert_bound(gate,selected['candidate_path'])
    local = resolve(row['gate_path']).parent
    if not gate['passed']:
        require(row['status'] == 'PENDING_NATIVE_GATE_FAILED_OR_CAPPED' and row['audited'] is False and
                row['fixed_K_excluded'] is False and row['exact_strict_improvement'] is False, 'Native failure credited as proof')
        return
    local_audit = book.read(row['independent_pair_audit_path'])
    for p in (selected['candidate_path'],local/'stars.json',local/'pairs.json'):
        book.assert_bound(local_audit,p)
    if local_audit['status'] != 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS':
        require(local_audit['status'] in ('INCOMPLETE_PAIR_AUDIT_NO_EXCLUSION','INCOMPLETE_PAIR_SEARCH_NO_EXCLUSION') and
                row['status'] == 'PENDING_INCOMPLETE_INDEPENDENT_PAIR_AUDIT' and row['audited'] is False and
                row['fixed_K_excluded'] is False and row['exact_strict_improvement'] is False, 'Incomplete local evidence credited')
        return
    require(local_audit['complete_used_domains_verified'] is True and local_audit['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and
            [r['outer_vertex'] for r in local_audit['independently_reenumerated_domains']] == list(range(84)) and
            all(r['domain_size'] > 0 for r in local_audit['independently_reenumerated_domains']), 'All84 complete domains required')
    stars = book.read(local/'stars.json')
    pairs = book.read(local/'pairs.json','EXACT_PAIR_DOMAIN_ARC_CONSISTENT_NONEMPTY')
    require(stars['complete_domain_enumeration'] is True and pairs['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and
            len(pairs['surviving_domain_ids']) == 84 and all(pairs['surviving_domain_ids']) and
            [r['domain_size'] for r in local_audit['independently_reenumerated_domains']] ==
            [len(r['domain_masks_hex']) for r in stars['domains']], 'Native/independent domain inventory differs')
    result = book.read(row['result_path'])
    require(key(result['candidate_path']) == selected['candidate_path'] and result['candidate_sha256'] == selected['candidate_sha256'] and
            key(result['domains_path']) == key(local/'stars.json') and key(result['domain_audit_path']) == key(row['independent_pair_audit_path']),
            'Star LP candidate/domain association differs')
    for p in (selected['candidate_path'],local/'stars.json',row['independent_pair_audit_path']):
        book.assert_bound(result,p)
    if not row['audited']:
        require(row['status'] == 'PENDING_NO_STAR_PRIMAL_DUAL' and row['fixed_K_excluded'] is False and
                row['exact_strict_improvement'] is False and not all(k in result for k in
                ('numeric_probabilities','numeric_cap_duals','numeric_reciprocity_duals')), 'Available exact evidence was misclassified')
        return
    audit = book.read(row['audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    replay = book.read(row['replay_path'],'INDEPENDENT_INTEGER_STAR_MARGINAL_CERTIFICATE_REPLAY_PASS')
    cert = book.read(row['certificate_path'])
    require(key(audit['certificate_path']) == key(row['certificate_path']) and audit['certificate_sha256'] == row['certificate_sha256'],
            'Audit certificate association differs')
    for obj in (audit,replay,cert):
        for p in (selected['candidate_path'],local/'stars.json',row['independent_pair_audit_path']):
            book.assert_bound(obj,p)
    book.assert_bound(audit,row['result_path']);book.assert_bound(replay,row['certificate_path'])
    check_audited_row(row,audit,replay,cert,baseline_lower)


def choose_best(previous_best, records, baseline_lower):
    improving = [r for r in records if r['audited'] and r['fixed_K_excluded'] and
                 fraction(r['exact_lower']) > 0 and fraction(r['exact_upper']) < baseline_lower]
    if not improving:
        return previous_best,None
    best = min(improving,key=lambda r:(fraction(r['exact_upper']),r['proposal_index']))
    frontier = dict(objective=OBJECTIVE,comparison_to_old_edge_merit=False,proposal_index=best['proposal_index'],
        best_candidate_path=best['candidate_path'],best_candidate_sha256=best['candidate_sha256'],
        star_phase1_path=best['result_path'],star_phase1_sha256=best['result_sha256'],
        star_audit_path=best['audit_path'],star_audit_sha256=best['audit_sha256'],
        star_certificate_replay_path=best['replay_path'],star_certificate_replay_sha256=best['replay_sha256'],
        edge_phase1_path=best['edge_phase1_path'],edge_phase1_sha256=best['edge_phase1_sha256'],
        exact_interval=dict(lower=best['exact_lower'],upper=best['exact_upper']),
        baseline_candidate_path=previous_best['best_candidate_path'],baseline_candidate_sha256=previous_best['best_candidate_sha256'],
        baseline_audit_path=previous_best['star_audit_path'],baseline_audit_sha256=previous_best['star_audit_sha256'],
        baseline_exact_lower=previous_best['exact_interval']['lower'],guaranteed_improvement=best['guaranteed_improvement'],
        positive_merit_seed_still_excluded=True,independent_pair_audit_path=best['independent_pair_audit_path'],
        independent_pair_audit_sha256=best['independent_pair_audit_sha256'],graph_completion=False)
    return frontier,best['proposal_index']


def build(args):
    book = Index()
    book.bind(ROOT/'acceleration/build_cp_completion_checkpoint.py',INDEX_HELPER_SHA)
    book.bind(ROOT/'acceleration/evaluate_cp_star_shortlist_v2.py',EVALUATOR_SHA)
    book.bind(args.previous,args.previous_sha256)
    previous = book.read(args.previous)
    require(previous['goal']['active'] is True and previous['goal']['complete'] is False and
            previous['graph_constructed'] is False and previous['general_nonexistence_proved'] is False, 'Goal state requires reassessment')
    directory = resolve(args.round)
    round_manifest = book.read(directory/'manifest.json','STAR_GUIDED_CP_NEIGHBORHOOD_MANIFEST')
    run = book.read(directory/'run_result.json','STAR_GUIDED_CP_NEIGHBORHOOD_FINISHED')
    require(key(run['manifest_path']) == key(directory/'manifest.json') and key(round_manifest['parent_checkpoint_path']) == key(args.previous) and
            round_manifest['parent_checkpoint_sha256'] == args.previous_sha256 and run['goal_complete'] is False,
            'Round parent/manifest differs')
    book.assert_bound(round_manifest,args.previous)
    require(len(run['records']) == len(round_manifest['steps']) and all(r['stage'] == s['stage'] and key(r['result_path']) == key(s['result_path'])
            for r,s in zip(run['records'],round_manifest['steps'])), 'Round receipt is incomplete')
    for row in run['records']:
        book.read(row['result_path'],row['status'])
    search = book.read(directory/'search/summary.json','BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    cp_audit = book.read(directory/'search/audit.json')
    require(cp_audit['status'] in ('INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS','INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'), 'Unverified CP search')
    book.assert_bound(cp_audit,directory/'search/summary.json')
    search_manifest = book.read(directory/'search/manifest.json')
    book.assert_bound(cp_audit,directory/'search/manifest.json')
    require(search['paths'] == search_manifest['paths'] and search['family_association'] == cp_audit['family_association'] == search_manifest['family_association'],
            'Search family association differs')
    old = previous['current_star_marginal_best']
    require(key(search['paths']['initial']) == key(old['best_candidate_path']) and key(search['paths']['initial_phase1']) == key(old['edge_phase1_path']),
            'CP search used another initial state')
    family = book.read(search['paths']['family_audit'])
    require(family['status'] in ('INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS','INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS') and
            family['legal_count'] == search['coarse_candidate_count'] == cp_audit['coarse_candidates'], 'Family scope/count differs')
    for p in (search['paths']['family_audit'],search['paths']['native'],old['best_candidate_path'],old['edge_phase1_path']):
        book.assert_bound(cp_audit,p)
    book.assert_bound(family,search['paths']['native']);book.assert_bound(family,old['best_candidate_path'])
    evaluation_path = resolve(args.evaluation) if args.evaluation else directory/'star_shortlist/summary.json'
    summary = book.read(evaluation_path,'BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED')
    manifest = book.read(summary['manifest_path'],'CP_STAR_SHORTLIST_EVALUATION_MANIFEST')
    require(summary['inputs_sha256'] == manifest['inputs_sha256'] and summary['SAT_or_DRAT_invocations'] == 0 and
            summary['graph_constructed'] is False and summary['general_nonexistence_proved'] is False and summary['goal_marked_complete'] is False,
            'Unexpected evaluation scope or inputs')
    book.assert_bound(manifest,ROOT/'acceleration/evaluate_cp_star_shortlist_v2.py')
    require(key(manifest['search_summary_path']) == key(directory/'search/summary.json') and
            key(manifest['search_audit_path']) == key(directory/'search/audit.json'), 'Evaluation used another CP search')
    book.assert_bound(manifest,directory/'search/summary.json');book.assert_bound(manifest,directory/'search/audit.json')
    baseline = book.read(manifest['baseline_star_audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    book.assert_bound(baseline,old['best_candidate_path']);book.assert_bound(baseline,old['star_phase1_path'])
    baseline_lower = check_baseline(previous,round_manifest,manifest,baseline)
    eligible = select_from_cp(search,cp_audit)
    cap = manifest['max_candidates'];require(type(cap) is int and 1 <= cap <= 32, 'Invalid shortlist cap')
    selected = eligible[:cap]
    require(manifest['eligible_candidates'] == len(eligible) and manifest['selected_candidates'] == selected and
            manifest['unselected_eligible_indices'] == summary['unselected_eligible_indices'] == [r['proposal_index'] for r in eligible[cap:]],
            'Independent exact shortlist reconstruction differs')
    records = summary['records']
    require([r['proposal_index'] for r in records] == [r['proposal_index'] for r in selected], 'Evaluation inventory missing or repeated')
    for row,chosen in zip(records,selected):
        inspect_record(book,row,chosen,baseline_lower)
    audited = sorted((r for r in records if r['audited']),key=lambda r:(fraction(r['exact_upper']),r['proposal_index']))
    require(summary['best'] == (audited[0] if audited else None) and
            summary['pending_candidates'] == [r for r in records if not r['fixed_K_excluded']] and
            summary['exact_fixed_K_exclusions'] == sum(r['fixed_K_excluded'] for r in records) and
            summary['exact_strict_improvement_count'] == sum(r['exact_strict_improvement'] for r in records), 'Summary accounting differs')
    separated = bool(audited) and all(fraction(audited[0]['exact_upper']) < fraction(r['exact_lower']) for r in audited[1:])
    require(summary['best_interval_strictly_below_other_audited_intervals'] is separated, 'Best interval separation claim differs')
    current,adopted = choose_best(old,records,baseline_lower)
    for report in args.extra_report:
        book.read(report)
    book.bind(Path(__file__))
    require(not (ROOT/'submission.txt').exists(),'Unexpected submission')
    return dict(status='HASH_VERIFIED_STAR_GUIDED_ROUND_CHECKPOINT',created_utc=datetime.now(timezone.utc).isoformat(),
        goal=previous['goal'],current_best=previous['current_best'],current_star_marginal_best=current,
        graph_constructed=False,general_nonexistence_proved=False,submission_txt_exists=False,
        previous_checkpoint_preserved=dict(path=key(args.previous),sha256=book.bind(args.previous)),
        prior_pending_completion_work_preserved=previous.get('pending_completion_work'),
        pending_completion_work=summary['pending_candidates'] or None,
        unselected_eligible_indices=summary['unselected_eligible_indices'],current_star_best_changed=adopted is not None,
        adopted_star_index=adopted,round_path=key(directory),round_kind=round_manifest['kind'],
        family_legal_candidates=family['legal_count'],CP_LP_artifacts=search['probes'],near_zero_eligible=len(eligible),
        star_evaluated_candidates=len(records),exact_star_exclusions=summary['exact_fixed_K_exclusions'],
        exact_star_improvement_count=summary['exact_strict_improvement_count'],star_records=records,
        previous_edge_positive_best_preserved=True,merits_compared_numerically=False,
        limits=dict(full_E0_or_Conway_coverage=False,general_nonexistence=False,graph_witness=False,
                    nonpositive_bound_means_feasible=False,all_family_LP_optimized=False),
        next_focus='Continue changing K under the stronger star-marginal objective; investigate pending exact-nonpositive cases separately.',
        direct_artifacts_sha256=book.direct,report_statuses=book.statuses,referenced_files_sha256=book.verified,
        verified_referenced_file_count=len(book.verified),indexing_only_no_solver_or_domain_reruns=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous',type=Path,required=True)
    parser.add_argument('--previous-sha256',required=True)
    parser.add_argument('--round',type=Path,required=True)
    parser.add_argument('--evaluation',type=Path)
    parser.add_argument('--extra-report',type=Path,action='append',default=[])
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--validate-only',action='store_true')
    args = parser.parse_args()
    require(not args.out.exists(),'Preserve old index')
    result = build(args)
    if not args.validate_only:
        with args.out.open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=result['status'],verified_files=result['verified_referenced_file_count'],
                         star_best_changed=result['current_star_best_changed'],output_created=not args.validate_only)),flush=True)


if __name__ == '__main__':
    main()
