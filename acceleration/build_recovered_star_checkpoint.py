"""Index an explicitly repaired CP LP view without rewriting a stopped round.

No solver, enumeration, or scientific replay is performed here. All claims use
hash-bound independent reports; exact intervals govern star-frontier adoption.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from build_cp_completion_checkpoint import Index, ROOT, require, resolve, key, fraction
from build_star_guided_checkpoint import select_from_cp, check_baseline, inspect_record, choose_best
from build_star_dual_shortlist_checkpoint import resolve_empty_pair

PINS = {
    'build_cp_completion_checkpoint.py': '3ce94bbdd49f9a6f216bb87d2f75ee3e6e2ad6f24dea198c4d4a5b0ba08a5b4f',
    'build_star_guided_checkpoint.py': 'ff9b952e21e0ee569a93c0894e0a04c09b68d02e0c2e62daab47c3487263c242',
    'build_star_dual_shortlist_checkpoint.py': 'bbf1cbd9f745568f8b46af4d741cc5af9dcf6adee2c0abe64a6d8d99e320845f',
    'audit_cp_matching_recovery.py': '73f9652fdaeb419a0d532effb3c82b94a56184db062864a72dbcbbc02f7e1f19',
    'evaluate_recovered_cp_star.py': '229fad86005b0c59d7bc51e92ec90f1b4002453f8c58fc395fd549d957a5965c',
    'phase1_probe_precise.py': '7b77d2b4f201706d7ec5fe06d7729e34cf9d9180d7b15d7411c939992ef491ad',
    'audit_phase1_kkt.py': 'c8efc709bcd10dc11d1f7ef3013a84cd834708880f09af5e026ee8cf3eda2d34',
    'audit_goal_theory_pairs.py': '9da60c600c45c16274efd05db0cf3c21cab8a61969dd2fe0d372ac9a2e7be75f',
}
RESULT_FIELDS = {'result_path', 'result_sha256', 'numeric_objective', 'optimal', 'status'}
VIEW_FIELDS = {'status', 'records', 'inputs_sha256', 'outputs_sha256', 'best', 'numerically_improving_candidates',
    'numerical_improvement_count', 'original_summary_path', 'original_summary_sha256', 'repair_manifest_path',
    'repair_manifest_sha256', 'original_search_preserved', 'original_audit_failure_preserved',
    'audit_tolerance_changed', 'repaired_proposal_indices'}


def check_stopped_round(manifest, failure):
    require(failure['status'] == 'ONE_STAR_CP_ROUND_STOPPED_PRESERVING_ARTIFACTS' and
            failure['stage'] == 'search_audit' and failure['exception_type'] == 'ValueError' and
            failure['retries'] == 0 and failure['goal_marked_complete'] is False,
            'Original orchestration failure must remain explicit')
    steps = manifest['steps']
    failed = [i for i,s in enumerate(steps) if s['stage'] == 'search_audit']
    require(len(failed) == 1 and len(failure['completed_steps']) == failed[0], 'Stopped-stage inventory differs')
    require(all(r['stage'] == s['stage'] and key(r['result_path']) == key(s['result_path']) and
                r['status'] == s['expected_status'] for r,s in zip(failure['completed_steps'],steps)),
            'Completed receipts differ from the original stage plan')


def check_recovery_semantics(original, view, audit, repairs):
    """Pure checks, separately exercised with rebound semantic corruptions."""
    require(original['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED' and
            view['status'] == 'AUDITED_REPAIRED_CP_LP_RECORD_VIEW' and
            audit['status'] == 'INDEPENDENT_CP_MATCHING_REPAIRED_LP_AUDIT_PASS' and
            repairs['status'] == 'EXPLICIT_HIGH_ACCURACY_CP_LP_REPLACEMENTS', 'Unexpected recovery protocol')
    require(view['original_search_preserved'] is True and view['original_audit_failure_preserved'] is True and
            view['audit_tolerance_changed'] is False and repairs['original_files_overwritten'] is False and
            repairs['audit_tolerance_changed'] is False and audit['original_search_and_failed_LP_files_preserved'] is True and
            audit['independent_LP_audit_tolerance'] == 1e-7, 'History or strict audit tolerance changed')
    require(set(original) <= set(view) and all(view[k] == v for k,v in original.items() if k not in VIEW_FIELDS) and
            set(view)-set(original) <= VIEW_FIELDS, 'Effective view changed non-LP search metadata')
    for name in ('inputs_sha256','outputs_sha256'):
        require(all(view[name].get(k) == h for k,h in original[name].items()), 'Original view bindings were removed or changed')
    oldrows = {r['proposal_index']:r for r in original['records']}
    newrows = {r['proposal_index']:r for r in view['records']}
    mapping = {r['proposal_index']:r for r in repairs['records']}
    reports = {r['proposal_index']:r for r in audit['probe_reports']}
    require(len(oldrows) == len(original['records']) == len(newrows) == len(view['records']) ==
            original['probes'] == view['probes'] == len(reports) == len(audit['probe_reports']) ==
            audit['actual_LP_exact_intervals_checked'] and list(oldrows) == list(newrows) and set(oldrows) == set(reports),
            'Original/effective/independent CP inventory differs')
    require(0 < len(mapping) == len(repairs['records']) == repairs['solver_runs'] ==
            audit['LP_solutions_replaced_from_bound_external_artifacts'] and set(mapping) <= set(oldrows) and
            sorted(mapping) == view['repaired_proposal_indices'] == audit['repaired_proposal_indices'],
            'Replacement inventory differs')
    for i, old in oldrows.items():
        new, report = newrows[i], reports[i]
        require(report['phase1_audit']['status'] == 'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS' and
                report['phase1_audit']['numerical_tolerance'] == 1e-7, 'Effective LP strict audit status/tolerance differs')
        require(set(old) == set(new) and all(new[k] == v for k,v in old.items() if k not in RESULT_FIELDS),
                'Repair changed a candidate, selection, move, or other non-result field')
        require(key(report['candidate_path']) == key(old['candidate_path']) and key(report['result_path']) == key(new['result_path']) and
                key(report['original_result_path']) == key(old['result_path']) and report['original_result_sha256'] == old['result_sha256'] and
                report['LP_replaced'] is (i in mapping), 'Independent repair report association differs')
        if i not in mapping:
            require(old == new, 'Unlisted LP changed')
            continue
        repair = mapping[i]
        require(key(repair['candidate_path']) == key(old['candidate_path']) and repair['candidate_sha256'] == old['candidate_sha256'] and
                key(repair['original_result_path']) == key(old['result_path']) and repair['original_result_sha256'] == old['result_sha256'] and
                key(repair['replacement_result_path']) == key(new['result_path']) and repair['replacement_result_sha256'] == new['result_sha256'] and
                key(new['result_path']) != key(old['result_path']) and new['optimal'] is True and
                repair['original_strict_audit_error'] == 'Phase-I primal-dual gap too large', 'Invalid explicit LP replacement')
    ordered = sorted(view['records'],key=lambda r:(r['numeric_objective'],r['proposal_index']))
    improving = [r for r in ordered if r['numeric_objective'] < view['baseline_numeric_objective']]
    require(view['best'] == ordered[0] and view['numerically_improving_candidates'] == improving and
            view['numerical_improvement_count'] == len(improving) and
            audit['effective_best_numeric_proposal_index'] == ordered[0]['proposal_index'] and
            audit['effective_best_numeric_objective'] == ordered[0]['numeric_objective'], 'Effective numerical summary differs')
    require(audit['LP_solver_or_family_enumeration_reruns'] == 0 and audit['search_or_native_producer_imported'] is False and
            audit['both_selection_stages_indices_roles_and_upper_only_ties_replayed'] is True and
            audit['selected_saved_vectors_finite_and_exact_box_feasible'] is True,
            'Recovery did not preserve the independent full CP audit')
    return mapping


def inspect_recovery(book, directory, recovery):
    original_path, view_path, audit_path = directory/'search/summary.json', recovery/'summary.json', recovery/'audit.json'
    original = book.read(original_path)
    view = book.read(view_path)
    audit = book.read(audit_path)
    repairs = book.read(view['repair_manifest_path'])
    mapping = check_recovery_semantics(original,view,audit,repairs)
    for obj in (view,audit,repairs):
        require(key(obj['original_summary_path']) == key(original_path) and obj['original_summary_sha256'] == book.bind(original_path),
                'Recovery points to another original summary')
    require(key(audit['effective_summary_path']) == key(view_path) and audit['effective_summary_sha256'] == book.bind(view_path) and
            key(audit['repair_manifest_path']) == key(view['repair_manifest_path']) and
            audit['repair_manifest_sha256'] == view['repair_manifest_sha256'] == book.bind(view['repair_manifest_path']),
            'Effective view/repair/auditor association differs')
    for p in (view_path,original_path,view['repair_manifest_path'],ROOT/'acceleration/audit_cp_matching_recovery.py'):
        book.assert_bound(audit,p)
    for p in (directory/'failure.json',directory/'logs/03_search_audit.log',original_path):
        book.assert_bound(repairs,p)
    require('Phase-I primal-dual gap too large' in (directory/'logs/03_search_audit.log').read_text(encoding='utf-8'),
            'Original failure log does not show the strict gap rejection')
    reports = {r['proposal_index']:r for r in audit['probe_reports']}
    effective = {r['proposal_index']:r for r in view['records']}
    for i,row in mapping.items():
        stored = book.read(row['strict_audit_path'],'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS')
        fresh = reports[i]['phase1_audit']
        require(stored['numerical_tolerance'] == fresh['numerical_tolerance'] == 1e-7 and all(
                stored[k] == fresh[k] for k in ('exact_primal_upper_bound','exact_dual_lower_bound','exact_primal_dual_gap')),
                'Replacement stored and fresh strict audits differ')
        result = book.read(row['replacement_result_path'])
        require(result['source_sha256'].get('phase1_probe_precise.py') == PINS['phase1_probe_precise.py'] and
                result['requested_solver_tolerances'] == dict(ipm_optimality_tolerance=1e-10,
                    primal_feasibility_tolerance=1e-10,dual_feasibility_tolerance=1e-10) and
                result['independent_audit_tolerance_changed'] is False, 'Repair is not the pinned high-accuracy solve')
        require(key(result['candidate_path']) == key(row['candidate_path']) and result['candidate_sha256'] == row['candidate_sha256'],
                'Repaired result belongs to another candidate')
        require(all(effective[i][name] == result[name] for name in ('numeric_objective','optimal','status')),
                'Effective LP metadata differs from its replacement file')
        for obj in (repairs,audit,stored,fresh):
            for p in (row['candidate_path'],row['replacement_result_path']):
                book.assert_bound(obj,p)
        book.assert_bound(repairs,row['original_result_path']);book.assert_bound(audit,row['original_result_path'])
    return original,view,audit,repairs


def build(args):
    book = Index()
    for name, digest in PINS.items():
        book.bind(ROOT/'acceleration'/name,digest)
    book.bind(args.previous,args.previous_sha256)
    previous = book.read(args.previous)
    refs = previous['referenced_files_sha256']
    require(type(refs) is dict and len(refs) == previous['verified_referenced_file_count'], 'Invalid parent reference inventory')
    for p,h in refs.items():
        require(type(h) is str and re.fullmatch('[0-9a-f]{64}',h), 'Malformed parent reference hash')
        book.bind(p,h)
    require(previous['goal']['active'] is True and previous['goal']['complete'] is False and
            previous['graph_constructed'] is False and previous['general_nonexistence_proved'] is False and
            previous.get('pending_completion_work') is None and not previous.get('unselected_eligible_indices'),
            'Parent state requires reassessment')
    directory, recovery = resolve(args.round),resolve(args.recovery)
    require(not (directory/'run_result.json').exists() and not (directory/'search/audit.json').exists(),
            'Stopped original round now has an unexpected success artifact')
    round_manifest = book.read(directory/'manifest.json','STAR_GUIDED_CP_NEIGHBORHOOD_MANIFEST')
    failure = book.read(directory/'failure.json')
    check_stopped_round(round_manifest,failure)
    require(key(round_manifest['parent_checkpoint_path']) == key(args.previous) and
            round_manifest['parent_checkpoint_sha256'] == args.previous_sha256 and round_manifest['goal_complete'] is False,
            'Original round parent differs')
    book.assert_bound(round_manifest,args.previous)
    for receipt in failure['completed_steps']:
        book.read(receipt['result_path'],receipt['status'])
    original,search,cp_audit,repairs = inspect_recovery(book,directory,recovery)
    search_manifest = book.read(directory/'search/manifest.json')
    book.assert_bound(cp_audit,directory/'search/manifest.json')
    require(search['paths'] == search_manifest['paths'] and search['family_association'] == cp_audit['family_association'] == search_manifest['family_association'],
            'Search family association differs')
    old = previous['current_star_marginal_best']
    require(key(search['paths']['initial']) == key(old['best_candidate_path']) and key(search['paths']['initial_phase1']) == key(old['edge_phase1_path']),
            'CP search used another initial state')
    family = book.read(search['paths']['family_audit'])
    require(family['status'] == 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS' and
            family['legal_count'] == search['coarse_candidate_count'] == cp_audit['coarse_candidates'], 'Family scope/count differs')
    for p in (search['paths']['family_audit'],search['paths']['native'],old['best_candidate_path'],old['edge_phase1_path']):
        book.assert_bound(cp_audit,p)
    book.assert_bound(family,search['paths']['native']);book.assert_bound(family,old['best_candidate_path'])
    summary = book.read(args.evaluation,'BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED')
    manifest = book.read(summary['manifest_path'],'RECOVERED_CP_STAR_SHORTLIST_EVALUATION_MANIFEST')
    require(summary['inputs_sha256'] == manifest['inputs_sha256'] and summary['SAT_or_DRAT_invocations'] == 0 and
            summary['graph_constructed'] is False and summary['general_nonexistence_proved'] is False and summary['goal_marked_complete'] is False and
            manifest['recovery_view'] is True and manifest['original_search_preserved'] is True and manifest['independent_LP_audit_tolerance'] == 1e-7,
            'Unexpected recovered evaluation scope or inputs')
    book.assert_bound(manifest,ROOT/'acceleration/evaluate_recovered_cp_star.py')
    require(key(manifest['search_summary_path']) == key(recovery/'summary.json') and key(manifest['search_audit_path']) == key(recovery/'audit.json'),
            'Evaluation used another effective CP view')
    book.assert_bound(manifest,recovery/'summary.json');book.assert_bound(manifest,recovery/'audit.json')
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
    require(summary['best_interval_strictly_below_other_audited_intervals'] is separated, 'Best interval separation differs')
    resolutions = [resolve_empty_pair(book,p,records) for p in args.resolved_pair_audit]
    resolved = {r['proposal_index'] for r in resolutions}
    require(len(resolved) == len(resolutions), 'Repeated pending resolution')
    pending = [r for r in summary['pending_candidates'] if r['proposal_index'] not in resolved]
    current,adopted = choose_best(old,records,baseline_lower)
    for report in args.extra_report:
        book.read(report)
    book.bind(Path(__file__))
    require(not (ROOT/'submission.txt').exists(),'Unexpected submission')
    return dict(status='HASH_VERIFIED_STAR_GUIDED_ROUND_CHECKPOINT',created_utc=datetime.now(timezone.utc).isoformat(),
        recovery=True,original_driver_finished=False,original_failure_preserved=True,original_orchestrator_status=failure['status'],
        original_failure_path=key(directory/'failure.json'),original_failure_sha256=book.bind(directory/'failure.json'),
        original_summary_path=key(directory/'search/summary.json'),original_summary_sha256=book.bind(directory/'search/summary.json'),
        effective_summary_path=key(recovery/'summary.json'),effective_summary_sha256=book.bind(recovery/'summary.json'),
        recovery_audit_path=key(recovery/'audit.json'),recovery_audit_sha256=book.bind(recovery/'audit.json'),
        repair_manifest_path=search['repair_manifest_path'],repair_manifest_sha256=search['repair_manifest_sha256'],
        repaired_proposal_indices=search['repaired_proposal_indices'],LP_repair_records=repairs['records'],
        independent_LP_audit_tolerance=1e-7,audit_tolerance_changed=False,
        goal=previous['goal'],current_best=previous['current_best'],current_star_marginal_best=current,
        graph_constructed=False,general_nonexistence_proved=False,submission_txt_exists=False,
        previous_checkpoint_preserved=dict(path=key(args.previous),sha256=book.bind(args.previous)),
        prior_pending_completion_work_preserved=previous.get('pending_completion_work'),
        pending_completion_work=pending or None,original_evaluation_pending_preserved=summary['pending_candidates'],resolved_pair_exclusions=resolutions,
        unselected_eligible_indices=summary['unselected_eligible_indices'],current_star_best_changed=adopted is not None,
        adopted_star_index=adopted,round_path=key(directory),round_kind=round_manifest['kind'],
        family_legal_candidates=family['legal_count'],CP_LP_artifacts=search['probes'],near_zero_eligible=len(eligible),
        star_evaluated_candidates=len(records),exact_star_exclusions=summary['exact_fixed_K_exclusions'],exact_pair_exclusions=len(resolutions),
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
    parser.add_argument('--recovery',type=Path,required=True)
    parser.add_argument('--evaluation',type=Path,required=True)
    parser.add_argument('--resolved-pair-audit',type=Path,action='append',default=[])
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
