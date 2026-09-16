"""Bind the CUDA CP implementation, independent controls, and improved search seed."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT/'acceleration/results'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve every previous checkpoint')
    verified, direct, statuses = {}, {}, {}

    def resolve(name):
        path = Path(str(name).replace('\\', '/'))
        if not path.is_absolute():
            path = ROOT/path
            if not path.exists() and len(Path(name).parts) == 1:
                path = ROOT/'acceleration'/name
        return path.resolve()

    def key(path):
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()

    def bind(name, expected=None):
        path = resolve(name)
        label = key(path)
        if label not in verified:
            require(path.is_file(), 'Missing artifact: '+label)
            verified[label] = sha256(path.read_bytes()).hexdigest()
        require(expected is None or verified[label] == expected, 'Changed artifact: '+label)
        return verified[label]

    def bindings(data):
        if isinstance(data, dict):
            for field, value in data.items():
                if field.endswith('_sha256') and isinstance(value, dict) and value and all(
                        isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v) for v in value.values()):
                    for name, expected in value.items():
                        bind(name, expected)
                elif field.endswith('_path') and isinstance(value, str):
                    other = field[:-5]+'_sha256'
                    if other in data and isinstance(data[other], str):
                        bind(value, data[other])
                bindings(value)
        elif isinstance(data, list):
            for value in data:
                bindings(value)

    def read(name, status=None):
        path = resolve(name)
        data = json.loads(path.read_bytes())
        require(status is None or data.get('status') == status, 'Unexpected status: '+str(name))
        bindings(data)
        direct[key(path)] = bind(path)
        if isinstance(data, dict) and 'status' in data:
            statuses[key(path)] = data['status']
        return data

    previous_path = RESULTS/'20260916_whole_matching_search_checkpoint.json'
    bind(previous_path, 'c27ee9f53a1ae03a1ba21134dfd02cee7a2b6941ec15e7fe841eb5c3d64961b7')
    previous = read(previous_path, 'HASH_VERIFIED_WHOLE_MATCHING_SEARCH_AND_IMPROVEMENT_CHECKPOINT')
    family = read(RESULTS/'20260916_cp_new_seed_family/independent_audit.json',
                  'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')
    require(family['legal_count'] == 73239 and family['raw_including_initial'] == 84560, 'Wrong new seed family')
    matvec = read(RESULTS/'20260916_cp_native_matvec_qa/audit.json',
                  'INDEPENDENT_FULL99_DYADIC_MATRIXFREE_MATVEC_AND_RATIONAL_CP_CONTROL_PASS')
    gpu = read(RESULTS/'20260916_cp_gpu_controls/audit.json',
               'INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS')
    cli = read(RESULTS/'20260916_cp_cli_controls/report.json', 'CP_CPU_GPU_SHARED_INPUT_NEGATIVE_CONTROLS_PASS')
    read(RESULTS/'20260916_cp_gpu_source_review/review.json', 'FROZEN_CP_CUDA_SOURCE_REVIEW_NO_BLOCKING_DEFECT_FOUND')
    read(RESULTS/'20260916_cp_gpu_tile_boundary/report.json')
    require(matvec['candidate_count'] == 5 and gpu['numeric_vector_entries_compared'] == 720720,
            'Incomplete native/GPU controls')
    require(cli['all_rejected'] and cli['negative_invocations'] == 74, 'Incomplete malformed-input controls')
    search_path = RESULTS/'20260916_cp_matching_search'
    search = read(search_path/'summary.json', 'BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    audit = read(search_path/'audit.json', 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS')
    require(search['coarse_candidate_count'] == 73239 and search['refined_candidate_count'] == 2048
            and search['probes'] == search['numerically_optimal_count'] == 64
            and search['numerical_improvement_count'] == 31 and search['cp_values_used_as_proof'] is False,
            'Unexpected bounded search coverage')
    for name in ('coarse', 'refined', 'selected_vectors'):
        read(search_path/(name+'_stage.json'))
    read(search_path/'manifest.json', 'CP_MATCHING_SEARCH_MANIFEST')
    read(search_path/'refine_selection.json')
    read(search_path/'lp_selection.json')
    local_path = search_path/'local/index_59390'
    gate = read(local_path/'gate.json', 'NATIVE_SHORTLIST_PAIR_GATE_FINISHED')
    pair = read(local_path/'independent_pair_audit.json', 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
    require(gate['passed'] and pair['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY'
            and len(pair['independently_reenumerated_domains']) == 84, 'Incomplete new seed local audit')
    adopted = search_path/'adopted_index_59390'
    best = read(adopted/'combined_evidence.json',
                'INDEPENDENT_STRICT_MATCHING_MERIT_IMPROVEMENT_AND_COMPLETE_PAIR_CLOSURE_PASS')
    require(best['numeric_objective'] < previous['current_best']['best_numeric_merit']
            and int(best['guaranteed_merit_decrease']['numerator']) > 0
            and best['independently_verified_surviving_pair_choices'] == 13424
            and best['best_fixed_K_integer_certificate_rhs'] < 0, 'Wrong improved-seed claim')
    for name in ('best_candidate.json', 'best_phase1.json', 'previous_phase1_audit.json', 'new_phase1_audit.json'):
        read(adopted/name)
    read(adopted/'integer_certificate_audit.json', 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS')
    for name in ('overlap_cp_cpu.rs', 'overlap_cp_gpu.cu', 'build_overlap_cp_gpu.ps1',
                 'audit_cp_matvec_cpu.py', 'review_cp_gpu_controls.py', 'review_cp_cli_controls.py', 'review_cp_gpu_tile_boundary.py',
                 'search_cp_matching.py', 'audit_cp_matching_search.py', 'bind_cp_matching_improvement.py',
                 'CP_GPU_INTERFACE.md', 'CP_GPU_RESEARCH_NOTES.md', Path(__file__).name):
        path = ROOT/'acceleration'/name
        direct[key(path)] = bind(path)
    require(not (ROOT/'submission.txt').exists(), 'Unexpected submission')
    current = dict(run='cp_matching_search', proposal_index=59390,
                   best_candidate_path=key(adopted/'best_candidate.json'), best_candidate_sha256=bind(adopted/'best_candidate.json'),
                   best_phase1_path=key(adopted/'best_phase1.json'), best_phase1_sha256=bind(adopted/'best_phase1.json'),
                   best_original_candidate_path=best['original_candidate_path'],
                   best_original_candidate_sha256=best['original_candidate_sha256'],
                   best_numeric_merit=best['numeric_objective'],
                   best_exact_interval=dict(lower=best['best_exact_lower_bound'], upper=best['best_exact_upper_bound']),
                   guaranteed_merit_decrease=best['guaranteed_merit_decrease'],
                   original_complete_star_choices=best['original_local_choices'], final_pair_ac_choices=13424,
                   best_pair_ac_independently_nonempty=True, pair_deletion_events_independently_replayed=pair['events_verified'],
                   best_exact_integer_rhs=best['best_fixed_K_integer_certificate_rhs'], move=best['move'],
                   positive_merit_seed_still_exactly_excluded=True, no_graph_completion=True)
    result = dict(status='HASH_VERIFIED_CUDA_CP_SEARCH_AND_IMPROVEMENT_CHECKPOINT',
                  created_utc=datetime.now(timezone.utc).isoformat(), goal=previous['goal'],
                  graph_constructed=False, general_nonexistence_proved=False, submission_txt_exists=False,
                  previous_checkpoint_preserved=dict(path=key(previous_path), sha256=bind(previous_path)),
                  current_best=current, independently_complete_same_sign_proposal_finals=73239,
                  gpu_cp_coarse_iterations=500, gpu_cp_refined_iterations=2000, gpu_cp_refined_candidates=2048,
                  actual_lp_artifacts=64, numeric_merit_improvers=31,
                  gpu_control_vector_comparisons=720720, gpu_control_max_vector_error=gpu['max_vector_absolute_error'],
                  numerical_cp_values_used_as_proofs=False, fixed_old_family_exclusions_not_transferred_to_new_seed=True,
                  next_work='Generate the complete same-sign family at the new seed; use validated CUDA CP ranking and exact/local audits. Harden producer input association/raw-dual/CLI checks in a new filename before reuse with new inputs.',
                  limits=dict(all_proposals_LP_optimized=False, whole_family_local_minimum_proved=False,
                              full_E0_or_Conway_coverage=False, E71_or_lower_exhaustive_enumeration_resumed=False),
                  direct_artifacts_sha256=direct, report_statuses=statuses,
                  referenced_files_sha256=verified, verified_referenced_file_count=len(verified),
                  indexing_only_no_solver_or_domain_reruns=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(status=result['status'], verified_files=len(verified), direct_artifacts=len(direct),
                          new_best=current['best_numeric_merit'], output_sha256=sha256(args.out.read_bytes()).hexdigest())))


if __name__ == '__main__':
    main()
