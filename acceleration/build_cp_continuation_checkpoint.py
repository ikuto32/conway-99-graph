"""Index an independently audited CP search round without redefining the goal."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--previous-sha256', required=True)
    parser.add_argument('--family-audit', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--extra-report', type=Path, action='append', default=[])
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

    def assert_bound(report, name):
        normalized = {key(resolve(path)): value for path, value in report['inputs_sha256'].items()}
        path = resolve(name)
        require(normalized.get(key(path)) == bind(path), 'Reports are not bound together: '+key(path))

    def graph_signature(name):
        candidate = json.loads(resolve(name).read_bytes())
        return tuple(sorted(map(tuple, candidate['overlap_edges_outer_zero_based'])))

    bind(args.previous, args.previous_sha256)
    previous = read(args.previous)
    require(previous['graph_constructed'] is False and previous['general_nonexistence_proved'] is False,
            'Reassess goal state before continuing')
    family = read(args.family_audit, 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')
    directory = args.directory.resolve()
    search = read(directory/'summary.json', 'BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    audit = read(directory/'audit.json', 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS')
    adoption = read(directory/'adoption.json', 'CP_EXACT_IMPROVEMENT_LOCAL_ADOPTION_FINISHED')
    manifest = read(directory/'manifest.json', 'CP_MATCHING_SEARCH_MANIFEST')
    assert_bound(audit, directory/'summary.json')
    assert_bound(audit, directory/'manifest.json')
    assert_bound(audit, args.family_audit)
    assert_bound(adoption, directory/'summary.json')
    assert_bound(adoption, directory/'audit.json')
    require(search['coarse_candidate_count'] == audit['coarse_candidates'] == family['legal_count']
            and search['refined_candidate_count'] == audit['refined_candidates']
            and search['probes'] == audit['actual_LP_exact_intervals_checked']
            and search['cp_values_used_as_proof'] is False, 'Round coverage differs')
    require(search['baseline_numeric_objective'] == previous['current_best']['best_numeric_merit'],
            'Round did not start at the previous current best')
    old_signature = graph_signature(previous['current_best']['best_original_candidate_path'])
    baseline_candidates = [name for name in audit['baseline_audit']['inputs_sha256'] if 'candidate' in Path(name).name]
    require(len(baseline_candidates) == 1 and graph_signature(baseline_candidates[0]) == old_signature,
            'Audited baseline graph differs from previous best')
    require(graph_signature(manifest['family_association']['initial_path']) == old_signature
            and graph_signature(manifest['family_association']['bound_base_path']) == old_signature,
            'Family/manifest baseline graph differs from previous best')
    for name in ('coarse', 'refined', 'selected_vectors'):
        read(directory/(name+'_stage.json'))
    read(directory/'refine_selection.json')
    read(directory/'lp_selection.json')
    for attempt in adoption['attempts']:
        read(attempt['gate_path'], 'NATIVE_SHORTLIST_PAIR_GATE_FINISHED')
        if 'pair_audit_path' in attempt:
            read(attempt['pair_audit_path'])
    current = previous['current_best']
    if adoption['adopted'] is not None:
        evidence_path = resolve(adoption['adopted']['combined_evidence_path'])
        best = read(evidence_path, 'INDEPENDENT_STRICT_MATCHING_MERIT_IMPROVEMENT_AND_COMPLETE_PAIR_CLOSURE_PASS')
        assert_bound(best, directory/'summary.json')
        assert_bound(best, directory/'audit.json')
        index = adoption['adopted']['proposal_index']
        chosen = [r for r in search['records'] if r['proposal_index'] == index]
        require(len(chosen) == 1 and index in audit['exact_strict_improvement_indices'], 'Adoption index is not audited')
        require(resolve(best['original_candidate_path']) == resolve(chosen[0]['candidate_path'])
                and best['original_candidate_sha256'] == chosen[0]['candidate_sha256'], 'Adopted candidate differs from selection')
        assert_bound(best, chosen[0]['candidate_path'])
        adopted = evidence_path.parent
        require(best['numeric_objective'] < current['best_numeric_merit']
                and int(best['guaranteed_merit_decrease']['numerator']) > 0
                and best['best_fixed_K_integer_certificate_rhs'] < 0,
                'Adoption is not a strict positive-merit improvement')
        for name in ('best_candidate.json', 'best_phase1.json', 'previous_phase1_audit.json', 'new_phase1_audit.json'):
            read(adopted/name)
        read(adopted/'integer_certificate_audit.json', 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS')
        current = dict(run=directory.name, proposal_index=adoption['adopted']['proposal_index'],
                       best_candidate_path=key(adopted/'best_candidate.json'), best_candidate_sha256=bind(adopted/'best_candidate.json'),
                       best_phase1_path=key(adopted/'best_phase1.json'), best_phase1_sha256=bind(adopted/'best_phase1.json'),
                       best_original_candidate_path=best['original_candidate_path'],
                       best_original_candidate_sha256=best['original_candidate_sha256'],
                       best_numeric_merit=best['numeric_objective'],
                       best_exact_interval=dict(lower=best['best_exact_lower_bound'], upper=best['best_exact_upper_bound']),
                       guaranteed_merit_decrease=best['guaranteed_merit_decrease'],
                       original_complete_star_choices=best['original_local_choices'],
                       final_pair_ac_choices=best['independently_verified_surviving_pair_choices'],
                       best_pair_ac_independently_nonempty=True,
                       pair_deletion_events_independently_replayed=best['pair_deletions_checked'],
                       best_exact_integer_rhs=best['best_fixed_K_integer_certificate_rhs'], move=best['move'],
                       positive_merit_seed_still_exactly_excluded=True, no_graph_completion=True)
    for path in args.extra_report:
        read(path)
    direct[key(Path(__file__).resolve())] = bind(Path(__file__))
    require(not (ROOT/'submission.txt').exists(), 'Unexpected submission')
    result = dict(status='HASH_VERIFIED_CP_CONTINUATION_CHECKPOINT',
                  created_utc=datetime.now(timezone.utc).isoformat(), goal=previous['goal'],
                  graph_constructed=False, general_nonexistence_proved=False, submission_txt_exists=False,
                  previous_checkpoint_preserved=dict(path=key(resolve(args.previous)), sha256=bind(args.previous)),
                  current_best=current, round_directory=key(directory),
                  adopted_new_seed=adoption['adopted'] is not None, pending_completion_work=adoption['pending_completion_work'],
                  independently_complete_same_sign_proposal_finals=family['legal_count'],
                  coarse_iterations=manifest['coarse_steps'], refined_iterations=manifest['refine_steps'],
                  refined_candidates=search['refined_candidate_count'], actual_lp_artifacts=search['probes'],
                  strictly_improving_exact_LP_intervals=len(audit['exact_strict_improvement_indices']),
                  numerical_cp_values_used_as_proofs=False, native_local_attempts=len(adoption['attempts']),
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
