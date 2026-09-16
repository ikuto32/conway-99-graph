"""Bind completed whole-matching evidence without rerunning any experiment."""
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

    previous_path = RESULTS / '20260916_atomic_checkpoint.json'
    bind(previous_path, '8645fb6777b545823422281c9b50b14ed7b900b7a712ed58a40e4fcf2a36ebf7')
    previous = read(previous_path, 'HASH_VERIFIED_ATOMIC_RESEARCH_CHECKPOINT')
    base_path = RESULTS / '20260916_two_trade_pilot/best_candidate.json'
    base = read(base_path)
    edges = set(map(tuple, base['overlap_edges_outer_zero_based']))
    mip = []
    for suffix in ('fixed_cross3', 'cross3', 'fixed_same0', 'same0'):
        directory = RESULTS / ('20260916_matching_mip_' + suffix)
        result = read(directory / 'result.json', 'NUMERICAL_FIXED_MATCHING_CONTROL' if suffix.startswith('fixed_')
                      else 'NUMERICAL_WHOLE_MATCHING_CANDIDATE')
        candidate = read(directory / 'candidate.json')
        read(directory / 'candidate_independent_audit.json', 'INDEPENDENT_WHOLE_MATCHING_CANDIDATE_AND_RETURNED_MERIT_AUDIT_PASS')
        pair = read(directory / 'pair_identity_audit.json', 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
        identity = read(directory / 'evidence_identity_reuse.json', 'INDEPENDENT_IDENTICAL_MATCHING_CANDIDATE_PRIOR_PHASE1_AND_PAIR_EVIDENCE_BOUND')
        require(result['matching_unchanged'] and set(map(tuple, candidate['overlap_edges_outer_zero_based'])) == edges,
                'Unexpected new matching; reassess checkpoint')
        require(pair['new_domain_enumeration_nodes'] == 0 and identity['same_exact_fixed_K_phase1_optimum'],
                'Unexpected reused evidence scope')
        mip.append(dict(directory=key(directory), matching_class=result['matching_class'],
                        fix_initial=result['fix_initial'], matching_unchanged=True,
                        numerical_optimal=result['numerical_optimal'], solve_seconds=result['solve_seconds'],
                        exact_optimality_claimed=False))
    read(RESULTS / '20260916_matching_mip_control_summary.json', 'BOUNDED_MATCHING_MODEL_CONTROL_SUMMARY')
    read(RESULTS / '20260916_matching_indicator_audit.json', 'INDEPENDENT_FULL99_MATCHING_INDICATOR_ALGEBRA_AND_SLACK_CONTROLS_PASS')
    diagnostics = read(RESULTS / '20260916_matching_lp_summary.json', 'NUMERICAL_CONTINUOUS_MATCHING_DIAGNOSTIC_SUMMARY')
    for record in diagnostics['results']:
        for name in ('matrix.json', 'result.json'):
            read(Path(record['directory']) / name)
    read(RESULTS / '20260916_matching_lp_same0/scope_arithmetic_review.json', 'INDEPENDENT_ZERO_SLACK_ARITHMETIC_AND_FAMILY_SCOPE_REVIEW_PASS')
    controls = read(RESULTS / '20260916_matching_lp_same0/corruption_controls.json', 'INDEPENDENT_WHOLE_MATCHING_FARKAS_CORRUPTION_CONTROLS_PASS')
    require(controls['negative_controls'] == 25 and controls['all_negative_controls_rejected']
            and controls['additional_positive_controls'] == 1, 'Incomplete corruption controls')
    bind(ROOT / 'acceleration/review_matching_farkas_controls.py', controls['reviewer_sha256'])
    read(RESULTS / '20260916_atomic_cycle_qa/rounded_dual_cpu_study.json', 'BOUNDED_EXACT_GRID_DUAL_CPU_STUDY')
    sweep = read(RESULTS / '20260916_matching_all21/summary.json', 'BOUNDED_21_MATCHING_COORDINATE_LP_SWEEP_FINISHED')
    read(RESULTS / '20260916_matching_all21/manifest.json')
    batch = read(RESULTS / '20260916_matching_all21/independent_batch_audit.json', 'INDEPENDENT_POSITIVE_MATCHING_COORDINATE_BATCH_AND_FAMILY_UNION_AUDIT_PASS')
    require(batch['candidate_sha256'] == bind(base_path), 'Different proof base')
    require(batch['exact_excluded_coordinates'] == batch['exact_same_sign_families'] == 8
            and batch['exact_cross_families'] == 0 and batch['numeric_only_unresolved_coordinates'] == 13
            and batch['labeled_overlap_patterns_excluded_in_proven_union'] == 48313,
            'Unexpected exact scope')
    require(batch['no_global_E0_or_Conway_nonexistence_claim'] and batch['no_numerical_zero_is_claimed_exactly_feasible']
            and not batch['simultaneous_changes_to_multiple_coordinates_covered'], 'Unexpected claim boundary')
    coordinates = []
    for record in batch['records']:
        read(record['matrix_path'])
        read(record['result_path'])
        item = {name: record[name] for name in ('root_group', 'matching_class', 'numeric_objective', 'status')}
        if record['status'] == 'EXACT_ONE_COORDINATE_EXCLUSION':
            read(record['certificate_path'], 'INTEGER_ZERO_SLACK_MATCHING_CONTRADICTION_CANDIDATE')
            proof = read(record['audit_path'], 'INDEPENDENT_WHOLE_MATCHING_MATRIX_AND_INTEGER_FARKAS_AUDIT_PASS')
            require(proof['contradiction_margin'] == record['contradiction_margin'] > 0, 'Invalid exact margin')
            item.update(contradiction_margin=proof['contradiction_margin'], audit_path=record['audit_path'])
        coordinates.append(item)
    require(len(coordinates) == sweep['coordinate_count'] == 21 and sweep['capped_or_unresolved_count'] == 0,
            'Incomplete diagnostic coverage')
    for name in ('matching_phase1_mip.py', 'matching_phase1_relaxation.py', 'certify_matching_relaxation.py',
                 'audit_matching_farkas.py', 'audit_matching_coordinate_batch.py', 'audit_matching_indicator.py',
                 'review_matching_farkas_scope.py', 'review_matching_farkas_controls.py',
                 'review_whole_matching_candidate.py', 'bind_matching_identity_evidence.py',
                 'review_rounded_dual_bounds.py', Path(__file__).name):
        path = ROOT / 'acceleration' / name
        direct[key(path)] = bind(path)
    require(not (ROOT / 'submission.txt').exists(), 'Unexpected submission')
    current = dict(previous['current_best'])
    current['unchanged_through_matching_continuation'] = True
    result = dict(status='HASH_VERIFIED_WHOLE_MATCHING_RESEARCH_CHECKPOINT',
                  created_utc=datetime.now(timezone.utc).isoformat(), goal=previous['goal'],
                  graph_constructed=False, general_nonexistence_proved=False, submission_txt_exists=False,
                  previous_atomic_checkpoint_preserved=dict(path=key(previous_path), sha256=bind(previous_path)),
                  current_best=current, mip_controls=mip, matching_coordinates=coordinates,
                  exact_family_exclusions=8, exact_labeled_family_union_before_partial_caps=48313,
                  numeric_zero_coordinates_unresolved=13, new_lp_runs=sweep['new_lp_runs'],
                  reused_lp_runs=sweep['reused_lp_runs'], corruption_controls_rejected=25,
                  limits=dict(other_matching_coordinates_fixed_per_proof=20,
                              simultaneous_coordinate_changes_covered=False, phase1_local_minimum_proved=False,
                              full_E0_or_Conway_coverage=False, numeric_zero_claimed_exactly_feasible=False,
                              capped_mip_is_neighborhood_proof=False, graph_or_merit_improved=False,
                              raw_union_includes_partial_cap_invalid_patterns=True,
                              E71_or_lower_exhaustive_enumeration_resumed=False),
                  direct_artifacts_sha256=direct, report_statuses=statuses,
                  referenced_files_sha256=verified, verified_referenced_file_count=len(verified),
                  indexing_only_no_solver_or_domain_reruns=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(status=result['status'], verified_files=len(verified), direct_artifacts=len(direct),
                          exact_families=8, conditional_labeled_union=48313,
                          output_sha256=sha256(args.out.read_bytes()).hexdigest())))


if __name__ == '__main__':
    main()
