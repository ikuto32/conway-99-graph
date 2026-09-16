"""Read-only positive and corruption controls for the repaired CP record view."""
import argparse
import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import evaluate_recovered_cp_star as driver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    driver.require(not driver.resolve(args.out).exists(), 'Fresh QA report required')
    run = driver.ROOT/'acceleration/results/20260916_star_guided_round2/recovery'
    summary, audit = driver.load(run/'summary.json'), driver.load(run/'audit.json')
    expected = [19706,19683,20883,65262,50833,71755,18481,79792,23400,48418,21236]
    selected = driver.select_records(summary, audit)
    driver.require([r['proposal_index'] for r in selected] == expected, 'Wrong independently audited11 selection')
    controls = []
    def rejected(name, action):
        try:
            action()
        except (ValueError, KeyError, TypeError) as error:
            controls.append(dict(name=name, rejected=True, exception=type(error).__name__, message=str(error)))
        else:
            raise ValueError('Accepted corruption: '+name)
    def selection_control(name, mutate):
        s, a = deepcopy(summary), deepcopy(audit); mutate(s,a)
        rejected(name, lambda:driver.select_records(s,a))
    selection_control('unrepaired_search_status', lambda s,a:s.update(status='BOUNDED_CP_MATCHING_SEARCH_FINISHED'))
    selection_control('old_audit_status', lambda s,a:a.update(status='INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS'))
    selection_control('duplicate_view_index', lambda s,a:s['records'][1].update(proposal_index=s['records'][0]['proposal_index']))
    selection_control('duplicate_audit_index', lambda s,a:a['probe_reports'][1].update(proposal_index=a['probe_reports'][0]['proposal_index']))
    selection_control('missing_audited_record', lambda s,a:a['probe_reports'].pop())
    selection_control('wrong_inventory_count', lambda s,a:s.update(probes=63))
    selection_control('changed_candidate_sha', lambda s,a:s['records'][0].update(candidate_sha256='0'*64))
    selection_control('changed_result_sha', lambda s,a:s['records'][0].update(result_sha256='0'*64))
    selection_control('swapped_candidate', lambda s,a:s['records'][0].update(candidate_path=s['records'][1]['candidate_path']))
    selection_control('swapped_result', lambda s,a:s['records'][0].update(result_path=s['records'][1]['result_path']))
    selection_control('numerical_only_phase', lambda s,a:a['probe_reports'][0]['phase1_audit'].update(status='NUMERICAL_ONLY'))
    selection_control('negative_exact_upper', lambda s,a:a['probe_reports'][0]['phase1_audit'].update(exact_primal_upper_bound=driver.rational(-1)))
    selection_control('reversed_exact_interval', lambda s,a:a['probe_reports'][0]['phase1_audit'].update(exact_dual_lower_bound=driver.rational(100)))
    selection_control('zero_exact_denominator', lambda s,a:a['probe_reports'][0]['phase1_audit']['exact_dual_lower_bound'].update(denominator='0'))
    base_args = SimpleNamespace(run=run,
        baseline_star_audit=driver.ROOT/'acceleration/results/20260916_star_guided_round1/star_shortlist/index_3074/audit.json',
        out=driver.ROOT/'acceleration/results/never_created_recovered_cp_star_qa',
        max_candidates=11, seconds=30., audit_seconds=60.)
    old_process = driver.subprocess.run
    processes = []
    def no_process(*a, **k):
        processes.append((a,k)); raise ValueError('Unexpected scientific process in read-only QA')
    driver.subprocess.run = no_process
    try:
        manifest = driver.preflight(base_args)
        driver.require([r['proposal_index'] for r in manifest['selected_candidates']] == expected and
                       manifest['recovery_view'] is True and manifest['independent_LP_audit_tolerance'] == 1e-7,
                       'Positive recovered preflight differs')
        for field,value in (('max_candidates',0),('max_candidates',33),('seconds',float('nan')),
                            ('seconds',0),('audit_seconds',float('inf')),('audit_seconds',0),('out',run)):
            sample = deepcopy(base_args); setattr(sample,field,value)
            rejected('limits_'+field+'_'+str(value), lambda a=sample:driver.preflight(a))
        # The actual preflight above rehashed every physical dependency. For
        # semantic mutation controls, use that exact snapshot of file hashes;
        # only loaded summary/audit objects are changed, never source files.
        old_load, old_digest = driver.load, driver.digest
        cached_hashes = dict(manifest['inputs_sha256'])
        def cached_digest(name):
            label = driver.key(name)
            return cached_hashes[label] if label in cached_hashes else old_digest(name)
        driver.digest = cached_digest
        try:
            for name, mutate in (
                ('wrong_effective_view_path',lambda s,a:a.update(effective_summary_path=a['original_summary_path'])),
                ('wrong_effective_view_sha',lambda s,a:a.update(effective_summary_sha256='0'*64)),
                ('wrong_original_view_path',lambda s,a:s.update(original_summary_path=s['repair_manifest_path'])),
                ('wrong_original_view_sha',lambda s,a:s.update(original_summary_sha256='0'*64)),
                ('wrong_repair_manifest_path',lambda s,a:s.update(repair_manifest_path=s['original_summary_path'])),
                ('wrong_repair_manifest_sha',lambda s,a:s.update(repair_manifest_sha256='0'*64)),
                ('weakened_declared_audit_tolerance',lambda s,a:a.update(independent_LP_audit_tolerance=1e-5)),
                ('view_claims_changed_tolerance',lambda s,a:s.update(audit_tolerance_changed=True)),
                ('changed_recovery_auditor_pin',lambda s,a:a['inputs_sha256'].update({'acceleration/audit_cp_matching_recovery.py':'0'*64})),
            ):
                s,a = deepcopy(summary),deepcopy(audit); mutate(s,a)
                def virtual_load(path):
                    label = driver.key(path)
                    if label == driver.key(run/'summary.json'):return s
                    if label == driver.key(run/'audit.json'):return a
                    return old_load(path)
                driver.load = virtual_load
                rejected(name, lambda:driver.preflight(base_args))
        finally:
            driver.load,driver.digest = old_load,old_digest
    finally:
        driver.subprocess.run = old_process
    driver.require(not processes and not base_args.out.exists(), 'QA launched a process or created driver output')
    prior_source = driver.ROOT/'acceleration/evaluate_cp_star_shortlist_v2.py'
    def functions(path):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        return {node.name:ast.dump(node,include_attributes=False) for node in tree.body if isinstance(node,ast.FunctionDef)}
    previous,current=functions(prior_source),functions(Path(driver.__file__))
    unchanged=['complete_pair_evidence','checked_star_interval','main']
    driver.require(all(previous[name] == current[name] for name in unchanged), 'Scientific pipeline differs from frozen v2')
    inputs=dict(manifest['inputs_sha256'])
    for path in (Path(__file__),prior_source):inputs[driver.key(path)]=driver.digest(path)
    driver.require(all(driver.digest(path)==value for path,value in inputs.items()), 'Bound input/source changed')
    report=dict(status='RECOVERED_CP_STAR_SELECTION_ORIGIN_AND_CORRUPTION_CONTROLS_PASS',inputs_sha256=inputs,
        selected_indices=expected, audited_effective_inventory=64, negative_controls=len(controls),controls=controls,
        all_negative_controls_rejected=True,positive_controls=['actual64_record_repaired_view','exact11_ordered_nearzero_selection',
            'all_original_repair_effective_view_hashes','actual_read_only_preflight','unchanged_scientific_pipeline_AST'],
        scientific_functions_AST_equal_to_frozen_v2=unchanged,
        stricter_solver_diff='Only three HiGHS solver tolerances1e-10 and metadata/docstring; independent audit tolerance remains1e-7.',
        source_review_no_blocker_found=True,scientific_process_invocations=0,driver_output_directories_created=0,
        original_reports_modified=False,scope='Selection/provenance/preflight review only. The full recovery auditor and scientific stages were not rerun.')
    driver.save(args.out,report)
    print(driver.json.dumps(dict(status=report['status'],negative_controls=len(controls),selected_indices=expected,
        sha256=driver.digest(args.out))))


if __name__ == '__main__':
    main()
