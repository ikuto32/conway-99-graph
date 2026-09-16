"""Bind complete same-sign search, improved seed, and GPU reoptimization controls."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'acceleration/results'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve every existing checkpoint')
    verified, direct, statuses = {}, {}, {}

    def resolve(name):
        path = Path(name)
        if not path.is_absolute():
            path = ROOT / path
            if not path.exists() and len(Path(name).parts) == 1:
                path = ROOT / 'acceleration' / name
        return path.resolve()

    def key(path):
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()

    def bind(name, expected=None):
        path = resolve(name)
        name = key(path)
        if name not in verified:
            require(path.is_file(), 'Missing artifact: ' + name)
            verified[name] = sha256(path.read_bytes()).hexdigest()
        require(expected is None or verified[name] == expected, 'Changed artifact: ' + name)
        return verified[name]

    def bindings(data):
        if isinstance(data, dict):
            for field, value in data.items():
                if field.endswith('_sha256') and isinstance(value, dict) and value and all(
                        isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v) for v in value.values()):
                    for name, expected in value.items():
                        bind(name, expected)
                elif field.endswith('_path') and isinstance(value, str):
                    hash_field = field[:-5] + '_sha256'
                    if hash_field in data and isinstance(data[hash_field], str):
                        bind(value, data[hash_field])
                bindings(value)
        elif isinstance(data, list):
            for value in data:
                bindings(value)

    def read(name, status=None):
        path = resolve(name)
        data = json.loads(path.read_bytes())
        require(status is None or data.get('status') == status, 'Unexpected report status: ' + str(path))
        bindings(data)
        direct[key(path)] = bind(path)
        if 'status' in data:
            statuses[key(path)] = data['status']
        return data

    previous_path = RESULTS / '20260916_matching_checkpoint.json'
    bind(previous_path, '7009c7fc402c539ac4e1f270329afcf5ef111abd2b738511981a378d2e8c52a0')
    previous = read(previous_path, 'HASH_VERIFIED_WHOLE_MATCHING_RESEARCH_CHECKPOINT')
    qa = RESULTS / '20260916_whole_matching_qa'
    native = read(qa / 'qa.json', 'WHOLE_MATCHING_NATIVE_CLI_AND_ALIGNMENT_QA_PASS')
    family = read(qa / 'all_independent_audit.json', 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')
    family_controls = read(qa / 'auditor_controls.json', 'INDEPENDENT_WHOLE_MATCHING_FAMILY_AUDITOR_CONTROLS_PASS')
    geometry = read(qa / 'accepted_geometry_controls.json', 'INDEPENDENT_MATCHING_ACCEPTED_GEOMETRY_REAL_AND_CORRUPTION_CONTROLS_PASS')
    require(native['legal_count'] == family['legal_count'] == 74638 and family['raw_including_initial'] == 84560,
            'Whole-matching enumeration counts differ')
    require(family_controls['negative_controls_rejected'] == 10 and geometry['negative_controls'] == 23
            and geometry['all_negative_controls_rejected'], 'Incomplete geometry controls')
    current_gpu = read(RESULTS / '20260916_whole_matching_gpu_diagnostic_v2/summary.json',
                       'WHOLE_MATCHING_FIXED_X_GPU_DIAGNOSTIC_AND_INDEPENDENT_SAMPLE_AUDIT_PASS')
    coordinate_gpu = read(RESULTS / '20260916_whole_matching_coordinate_x_diagnostic/summary.json',
                          'COORDINATE_X_GPU_RESCORE_AND_INDEPENDENT_SAMPLE_AUDIT_PASS')
    require(current_gpu['all_noninitial_candidates_scored'] == coordinate_gpu['candidate_count'] == 74638,
            'Unexpected GPU scoring domain')
    failed = RESULTS / '20260916_whole_matching_gpu_diagnostic'
    require(not (failed / 'summary.json').exists(), 'Reassess historical failed diagnostic status')
    for path in sorted(failed.glob('*.json')):
        read(path)
    bind(failed / 'all_input.txt')
    bind(failed / 'checked_input.txt')
    pilot = RESULTS / '20260916_whole_matching_pilot'
    run = read(pilot / 'summary.json', 'BOUNDED_WHOLE_MATCHING_COUPLED_SEARCH_FINISHED')
    read(pilot / 'manifest.json')
    trace = read(pilot / 'trace_audit.json', 'INDEPENDENT_WHOLE_MATCHING_TRACE_GRAPH_MODELS_MERITS_SELECTION_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS')
    read(pilot / 'accepted_phase1_intervals_audit.json', 'INDEPENDENT_WHOLE_MATCHING_ACCEPTED_PHASE1_INTERVAL_AUDIT_PASS')
    read(pilot / 'best_pair_independent_audit.json', 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
    read(pilot / 'best_combined_evidence.json', 'INDEPENDENT_WHOLE_MATCHING_BEST_LOCAL_PASS_GLOBAL_OBSTRUCTION_BOUND')
    require(run['phase1_evaluations'] == trace['actual_lp_probe_artifacts_checked'] == 129
            and run['accepted_moves'] == trace['accepted_moves_replayed'] == 0, 'Unexpected pilot outcome')
    shortlist = RESULTS / '20260916_matching_hint_shortlist'
    short = read(shortlist / 'summary.json', 'BOUNDED_MATCHING_HINT_SHORTLIST_FINISHED')
    read(shortlist / 'manifest.json')
    short_audit = read(shortlist / 'independent_audit.json',
                       'INDEPENDENT_MATCHING_HINT_SELECTION_TWO_X_SCORES_AND_EXACT_PHASE1_BOUNDS_AUDIT_PASS')
    require(short['probes'] == short_audit['selected_new_distinct_candidates'] == short_audit['exact_positive_lower_bounds'] == 64,
            'Incomplete shortlist audit')
    require(short_audit['prior_candidate_signatures_excluded'] == 129 and short_audit['selected_two_x_scores_independently_recomputed'] == 128,
            'Shortlist novelty or score check differs')
    local = {}
    for index in (17436, 17109):
        directory = shortlist / 'local' / ('index_' + str(index))
        gate = read(directory / 'gate.json', 'NATIVE_SHORTLIST_PAIR_GATE_FINISHED')
        pair = read(directory / 'independent_pair_audit.json', 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
        require(pair['propagation_status'] == ('EMPTY_DOMAIN' if index == 17436 else 'ARC_CONSISTENT_NONEMPTY'),
                'Unexpected independent pair result')
        local[str(index)] = dict(native_pass=gate['passed'], independent_pair_status=pair['propagation_status'],
                                 deletion_events=pair['events_verified'])
    adopted = shortlist / 'adopted_index_17109'
    best = read(adopted / 'combined_evidence.json',
                'INDEPENDENT_STRICT_MATCHING_MERIT_IMPROVEMENT_AND_COMPLETE_PAIR_CLOSURE_PASS')
    require(best['numeric_objective'] < previous['current_best']['best_numeric_merit']
            and int(best['guaranteed_merit_decrease']['numerator']) > 0
            and best['independently_verified_surviving_pair_choices'] == 12558
            and best['best_fixed_K_integer_certificate_rhs'] < 0, 'Unexpected improved-seed scope')
    best_wrapper = read(adopted / 'best_candidate.json')
    read(adopted / 'best_phase1.json')
    read(adopted / 'integer_certificate_audit.json', 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS')
    cp = read(RESULTS / '20260916_phase1_chambolle_pock_cpu/summary.json',
              'INDEPENDENT_FULL99_CHAMBOLLE_POCK_CPU_QUALITY_CONTROL_PASS')
    require(cp['operator_squared_norm_uniform_upper_bound'] == 117 and cp['step_product_upper_bound'] < 1
            and cp['control_count'] == 5 and cp['cp_numeric_values_used_as_proof'] is False,
            'Unexpected numerical optimization control scope')
    unique = set()
    for directory in (pilot, shortlist):
        for path in sorted((directory / 'probes').glob('*_candidate.json')):
            data = json.loads(path.read_bytes())
            unique.add(tuple(sorted(map(tuple, data['overlap_edges_outer_zero_based']))))
            bind(path)
    require(len(unique) == 193, 'Unexpected duplicate or missing fixed-K probes')
    for name in ('overlap_matching_neighbors.rs', 'qa_whole_matching_cli.py', 'audit_whole_matching_family.py',
                 'qa_whole_matching_family_auditor.py', 'review_matching_accepted_geometry.py',
                 'guided_matching_overlap.py', 'audit_matching_trace.py', 'audit_matching_accepted.py',
                 'bind_matching_best_evidence.py', 'diagnose_whole_matching_gpu.py', 'diagnose_whole_matching_gpu_v2.py',
                 'diagnose_coordinate_x_gpu.py', 'scan_matching_hint_shortlist.py', 'audit_matching_hint_shortlist.py',
                 'check_shortlist_native_pair.py', 'bind_matching_hint_improvement.py',
                 'review_phase1_chambolle_pock.py', 'PHASE1_CHAMBOLLE_POCK_REVIEW.md', Path(__file__).name):
        path = ROOT / 'acceleration' / name
        direct[key(path)] = bind(path)
    require(not (ROOT / 'submission.txt').exists(), 'Unexpected submission')
    current = dict(run='matching_hint_shortlist', proposal_index=17109,
                   best_candidate_path=key(adopted / 'best_candidate.json'), best_candidate_sha256=bind(adopted / 'best_candidate.json'),
                   best_phase1_path=key(adopted / 'best_phase1.json'),
                   best_original_candidate_path=best['original_candidate_path'],
                   best_original_candidate_sha256=best['original_candidate_sha256'],
                   best_numeric_merit=best['numeric_objective'],
                   best_exact_interval=dict(lower=best['best_exact_lower_bound'], upper=best['best_exact_upper_bound']),
                   guaranteed_merit_decrease=best['guaranteed_merit_decrease'],
                   original_complete_star_choices=best['original_local_choices'], final_pair_ac_choices=12558,
                   best_pair_ac_independently_nonempty=True, pair_deletion_events_independently_replayed=1245,
                   best_exact_integer_rhs=best['best_fixed_K_integer_certificate_rhs'],
                   move=best['move'], positive_merit_seed_still_exactly_excluded=True, no_graph_completion=True)
    result = dict(status='HASH_VERIFIED_WHOLE_MATCHING_SEARCH_AND_IMPROVEMENT_CHECKPOINT',
                  created_utc=datetime.now(timezone.utc).isoformat(), goal=previous['goal'],
                  graph_constructed=False, general_nonexistence_proved=False, submission_txt_exists=False,
                  previous_checkpoint_preserved=dict(path=key(previous_path), sha256=bind(previous_path)),
                  current_best=current, independently_complete_same_sign_proposal_finals=74638,
                  eligible_extended_shapes=66647, pilot_actual_lp_artifacts=129, hint_actual_lp_artifacts=64,
                  unique_fixed_K_LP_states_this_continuation=193, independent_local_outcomes=local,
                  old_family_exclusions_remain_bound_to_old_base_K=True,
                  cp_control=dict(controls=5, uniform_squared_norm_bound=117, step_product=.9477,
                                  GPU_implementation_performed=False, numerical_values_used_as_proofs=False),
                  preserved_failed_diagnostic=dict(directory=key(failed), reason='Strict list/tuple input wrapper error before independent comparison; v2 passes separately',
                                                   counted_as_passing_audit=False),
                  limits=dict(all_proposals_LP_optimized=False, whole_family_local_minimum_proved=False,
                              full_E0_or_Conway_coverage=False, numeric_zero_means_full_graph=False,
                              E71_or_lower_exhaustive_enumeration_resumed=False),
                  direct_artifacts_sha256=direct, report_statuses=statuses,
                  referenced_files_sha256=verified, verified_referenced_file_count=len(verified),
                  indexing_only_no_solver_or_domain_reruns=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(status=result['status'], verified_files=len(verified), direct_artifacts=len(direct),
                          new_best=current['best_numeric_merit'], output_sha256=sha256(args.out.read_bytes()).hexdigest())))


if __name__ == '__main__':
    main()
