"""Read-only selection corruption controls for the fixed-star-dual evaluator."""
import argparse
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import evaluate_star_dual_shortlist as driver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    driver.require(not driver.resolve(args.out).exists(), 'Preserve control report')
    root = driver.ROOT/'acceleration/results'
    rank_dir = root/'20260916_star_dual_cross8837'
    family_dir = root/'20260916_star_guided_round1/family'
    cp_dir = root/'20260916_star_guided_round1/search'
    names = [rank_dir/'summary.json', rank_dir/'cp_comparison.json', family_dir/'cross.json',
             family_dir/'independent_audit.json', rank_dir/'scores.json', cp_dir/'summary.json', cp_dir/'audit.json']
    values = [driver.load(path) for path in names]
    values.append([driver.load(r['candidate_path']) for r in values[5]['records']])
    positive, excluded = driver.select_records(*values)
    expected = [2963, 3125, 8469, 8293, 8466, 8467, 8138, 7757, 8527, 8468, 2962, 8555, 8528, 8796, 8166, 3055]
    driver.require([r['index'] for r in positive[:16]] == expected and len(excluded) == 64, 'Real selection changed')
    controls = []
    def rejected(name, action):
        try:
            action()
        except (ValueError, KeyError, TypeError) as error:
            controls.append(dict(name=name, rejected=True, exception=type(error).__name__, message=str(error)))
        else:
            raise ValueError('Accepted corruption: '+name)
    def change_one(name, position, modify):
        sample = values[:]
        # Rank/scores/family each have large aligned arrays; only the object
        # being corrupted is copied, so the other inputs remain untouched.
        sample[position] = deepcopy(values[position])
        modify(sample[position])
        rejected(name, lambda: driver.select_records(*sample))
    for name, modify in (
        ('unfinished_rank', lambda r:r.update(status='RUNNING')),
        ('wrong_candidate_count', lambda r:r.update(candidate_count=r['candidate_count']-1)),
        ('duplicate_rank_index', lambda r:r['ranked'][1].update(index=r['ranked'][0]['index'])),
        ('missing_rank', lambda r:r['ranked'].pop()),
        ('wrong_integer_score', lambda r:r['ranked'][0].update(score_numerator=r['ranked'][0]['score_numerator']+1)),
        ('float_integer_score', lambda r:r['ranked'][0].update(score_numerator=float(r['ranked'][0]['score_numerator']))),
        ('negative_denominator', lambda r:r['ranked'][0].update(denominator=-1)),
        ('wrong_root_group', lambda r:r['ranked'][0].update(root_group=-1)),
        ('wrong_cycle_size', lambda r:r['ranked'][0].update(cycle_size=7)),
        ('wrong_original_index', lambda r:r['ranked'][0].update(original_native_index=-1)),
        ('unsorted_exact_ranks', lambda r:r['ranked'].reverse()),
        ('different_rank_family', lambda r:r.update(family_sha256='0'*64)),
    ):
        change_one(name, 0, modify)
    for name, modify in (
        ('wrong_comparison_status', lambda r:r.update(status='RUNNING')),
        ('omitted_CP_inventory_member', lambda r:r['cp_candidates_with_fixed_dual_rank'].pop()),
        ('incorrect_excluded_CP_count', lambda r:r.update(cp_selected_count=63)),
        ('wrong_suggested_index', lambda r:r['first32_fixed_dual_candidates_outside_cp_selection'][0].update(index=0)),
        ('reordered_suggestion', lambda r:r['first32_fixed_dual_candidates_outside_cp_selection'].reverse()),
    ):
        change_one(name, 1, modify)
    for name, modify in (
        ('wrong_family_selector', lambda r:r.update(selector='same_sign')),
        ('duplicate_family_final', lambda r:r['overlap_candidates'].__setitem__(1,r['overlap_candidates'][0])),
        ('noncanonical_family_edge', lambda r:r['overlap_candidates'][0][0].reverse()),
        ('mismatched_move_metadata', lambda r:r['moves'][0].update(matching_class='same_0')),
    ):
        change_one(name, 2, modify)
    for name, modify in (
        ('family_proof_unverified', lambda r:r.update(status='NATIVE_ONLY')),
        ('family_proof_no_graph_check', lambda r:r.update(all_original_native_indices_and_final_graphs_checked=False)),
        ('family_coordinate_count_changed', lambda r:r['by_class'][0].update(legal_cycles=-1)),
    ):
        change_one(name, 3, modify)
    for name, modify in (
        ('native_scores_claim_certificates', lambda r:r.update(scores_are_certificates=True)),
        ('ranked_score_capped', lambda r:r['results'][values[0]['ranked'][0]['index']].update(status='INCOMPLETE')),
        ('ranked_domains_incomplete', lambda r:r['results'][values[0]['ranked'][0]['index']].update(complete_domain_enumeration=False)),
        ('ranked_local_empty', lambda r:r['results'][values[0]['ranked'][0]['index']].update(local_empty_count=1)),
        ('native_score_numerator_changed', lambda r:r['results'][values[0]['ranked'][0]['index']].update(score_numerator=0)),
    ):
        change_one(name, 4, modify)
    for name, modify in (
        ('missing_CP_record', lambda r:r['records'].pop()),
        ('CP_candidate_hash_changed', lambda r:r['records'][0].update(candidate_sha256='0'*64)),
        ('CP_candidate_path_swapped', lambda r:r['records'][0].update(candidate_path=r['records'][1]['candidate_path'])),
    ):
        change_one(name, 5, modify)
    change_one('CP_audit_missing_probe', 6, lambda r:r['probe_reports'].pop())
    change_one('CP_exact_graph_swapped', 7, lambda r:r[0].update(overlap_edges_outer_zero_based=r[1]['overlap_edges_outer_zero_based']))
    base_args = SimpleNamespace(ranking=names[0], comparison=names[1], family=names[2], family_audit=names[3],
        cp_run=cp_dir, baseline_star_audit=root/'20260916_star_marginal_shortlist/index_25496/audit.json',
        out=root/'never_created_fixed_star_dual_shortlist_controls', max_candidates=16, seconds=30., audit_seconds=60.)
    for field, value in (('max_candidates',0), ('max_candidates',17), ('seconds',float('nan')),
                         ('seconds',0), ('audit_seconds',float('inf')), ('audit_seconds',0), ('out',cp_dir)):
        test = deepcopy(base_args); setattr(test,field,value)
        rejected('preflight_'+field+'_'+str(value), lambda t=test:driver.preflight(t))
    calls = []
    old_run = driver.subprocess.run
    def no_process(*args, **kwargs):
        calls.append((args,kwargs))
        raise ValueError('Unexpected process during read-only controls')
    driver.subprocess.run = no_process
    try:
        manifest = driver.preflight(base_args)
    finally:
        driver.subprocess.run = old_run
    driver.require(not calls and not base_args.out.exists(), 'Read-only preflight mutated output or ran a process')
    driver.require([r['proposal_index'] for r in manifest['selected_candidates']] == expected and
                   all('edge_phase1_path' not in r for r in manifest['selected_candidates']) and
                   manifest['CP_nearzero_eligibility_assumed'] is False, 'Dishonest candidate eligibility')
    for row in manifest['selected_candidates']:
        driver.require(driver.sha256(driver.candidate_bytes(row['candidate_document'])).hexdigest() == row['candidate_sha256'],
                       'Planned candidate byte/hash mismatch')
    # Reuse the frozen scientific guard QA, not its historical candidate selection.
    previous_path = root/'20260916_cp_star_shortlist_v2_controls.json'
    previous = driver.load(previous_path)
    driver.require(previous['status'] == 'CP_STAR_SHORTLIST_ORCHESTRATION_V2_CONTROLS_PASS' and
                   previous['all_negative_controls_rejected'] is True, 'Missing frozen scientific guard controls')
    inputs = dict(manifest['inputs_sha256'])
    for p, expected_hash in previous['inputs_sha256'].items():
        driver.require(driver.digest(p) == expected_hash, 'Historical guard binding differs')
        inputs[driver.key(p)] = expected_hash
    inputs[driver.key(previous_path)] = driver.digest(previous_path)
    inputs[driver.key(Path(__file__))] = driver.digest(Path(__file__))
    report = dict(status='FIXED_STAR_DUAL_SHORTLIST_READ_ONLY_SELECTION_AND_CORRUPTION_CONTROLS_PASS',
        inputs_sha256=inputs, controls=controls, negative_controls=len(controls), all_negative_controls_rejected=True,
        selected_indices=expected, eligible_candidates=manifest['eligible_candidates'], excluded_exact_CP_graphs=64,
        positive_controls=['real_full8837_integer_order_and_native_association', 'all64_exact_CP_graph_exclusion',
            'independent_family_and_baseline_binding', 'fresh16_candidate_full99_validation_and_byte_hashes',
            'read_only_preflight', 'frozen_scientific_pipeline_guards_reused'],
        scientific_pipeline_frozen_controls_path=driver.key(previous_path),
        scientific_pipeline_frozen_controls_sha256=driver.digest(previous_path),
        scientific_processes_launched=0, driver_output_directories_created=0,
        new_LP_runs=0, new_native_domain_runs=0, graph_constructed=False,
        scope='New selection and provenance preflight only. Scientific stage guards reuse frozen v2 controls; no selected candidate was solved by this QA.')
    driver.save(args.out, report)
    print(driver.json.dumps(dict(status=report['status'], negative_controls=len(controls), selected_indices=expected)))


if __name__ == '__main__':
    main()
