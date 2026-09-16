"""Read-only association/cap controls for the CP-to-star orchestration."""
import argparse
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import evaluate_cp_star_shortlist_v2 as driver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integration', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    driver.require(not args.out.exists(), 'Fresh control report required')
    run = driver.ROOT/'acceleration/results/20260916_cp_zero_neighborhood_226/search'
    baseline = driver.ROOT/'acceleration/results/20260916_star_marginal_pilot/index_226_audit.json'
    summary, audit = driver.load(run/'summary.json'), driver.load(run/'audit.json')
    selected = driver.select_records(summary, audit)
    driver.require([r['proposal_index'] for r in selected] == [25463,26003,25469,27892,64054,26032,25496,25434,26025],
                   'Historical independent selection differs')
    inputs = {driver.key(p): driver.digest(p) for p in (Path(__file__), Path(driver.__file__), run/'summary.json', run/'audit.json', baseline)}
    controls = []
    def rejected(name, action):
        try:
            action()
        except (ValueError, KeyError, TypeError) as error:
            controls.append(dict(name=name, rejected=True, exception=type(error).__name__, message=str(error)))
        else:
            raise ValueError('Accepted negative control: '+name)
    def selection_control(name, change):
        s, a = deepcopy(summary), deepcopy(audit)
        change(s, a)
        rejected(name, lambda: driver.select_records(s, a))
    selection_control('unfinished_search', lambda s,a:s.update(status='RUNNING'))
    selection_control('unverified_search', lambda s,a:a.update(status='UNVERIFIED'))
    selection_control('duplicate_summary_index', lambda s,a:s['records'][1].update(proposal_index=s['records'][0]['proposal_index']))
    selection_control('duplicate_audit_index', lambda s,a:a['probe_reports'][1].update(proposal_index=a['probe_reports'][0]['proposal_index']))
    selection_control('missing_audit_row', lambda s,a:a['probe_reports'].pop())
    selection_control('incorrect_probe_count', lambda s,a:s.update(probes=63))
    selection_control('changed_candidate_hash', lambda s,a:s['records'][0].update(candidate_sha256='0'*64))
    selection_control('swapped_candidate_path', lambda s,a:s['records'][0].update(candidate_path=s['records'][1]['candidate_path']))
    selection_control('swapped_result_path', lambda s,a:a['probe_reports'][0].update(result_path=a['probe_reports'][1]['result_path']))
    selection_control('unverified_phase', lambda s,a:a['probe_reports'][0]['phase1_audit'].update(status='NUMERICAL_ONLY'))
    selection_control('negative_upper', lambda s,a:a['probe_reports'][0]['phase1_audit'].update(exact_primal_upper_bound=driver.rational(-1)))
    selection_control('reversed_interval', lambda s,a:a['probe_reports'][0]['phase1_audit'].update(exact_dual_lower_bound=driver.rational(100)))
    selection_control('zero_denominator', lambda s,a:a['probe_reports'][0]['phase1_audit']['exact_dual_lower_bound'].update(denominator='0'))
    base_args = SimpleNamespace(run=run, baseline_star_audit=baseline, out=driver.ROOT/'acceleration/results/never_created_cp_star_guard',
                                max_candidates=1, seconds=30., audit_seconds=60.)
    for field, value in (('max_candidates',0), ('max_candidates',33), ('seconds',0), ('seconds',float('nan')),
                         ('audit_seconds',float('inf')), ('audit_seconds',0), ('out',run)):
        test = deepcopy(base_args); setattr(test,field,value)
        rejected('invalid_'+field+'_'+str(value), lambda t=test:driver.preflight(t))
    manifest = driver.preflight(base_args)
    driver.require(manifest['eligible_candidates'] == 9 and len(manifest['selected_candidates']) == 1, 'Preflight selection failed')
    inputs.update(manifest['inputs_sha256'])
    integration_path = args.integration/'summary.json'
    integration = driver.load(integration_path)
    driver.require(integration['status'] == 'BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED' and
                   len(integration['records']) == 1 and integration['exact_fixed_K_exclusions'] == 1 and
                   integration['SAT_or_DRAT_invocations'] == 0, 'Missing positive end-to-end integration')
    for mapping in (integration['inputs_sha256'], integration['outputs_sha256']):
        for p, expected in mapping.items():
            driver.require(driver.digest(p) == expected, 'Integration binding differs')
            inputs[driver.key(p)] = expected
    inputs[driver.key(integration_path)] = driver.digest(integration_path)
    row = integration['records'][0]
    pair = driver.load(row['independent_pair_audit_path'])
    stars = driver.resolve(row['independent_pair_audit_path']).with_name('stars.json')
    driver.complete_pair_evidence(pair,row,stars)
    for name, change in (
        ('pair_incomplete', lambda p:p.update(complete_used_domains_verified=False)),
        ('pair_empty', lambda p:p.update(propagation_status='EMPTY_DOMAIN')),
        ('pair_missing_vertex', lambda p:p['independently_reenumerated_domains'].pop()),
        ('pair_duplicate_vertex', lambda p:p['independently_reenumerated_domains'][1].update(outer_vertex=0)),
        ('pair_empty_domain', lambda p:p['independently_reenumerated_domains'][0].update(domain_size=0)),
        ('pair_wrong_candidate', lambda p:p['inputs_sha256'].update({row['candidate_path']:'0'*64})),
    ):
        bad = deepcopy(pair); change(bad)
        rejected(name, lambda b=bad:driver.complete_pair_evidence(b,row,stars))
    star, replay = driver.load(row['audit_path']), driver.load(row['replay_path'])
    lower, upper = driver.checked_star_interval(star,replay)
    driver.require(lower > 0 and lower <= upper, 'Positive exact integration bound missing')
    for name, change in (
        ('replay_bad_status',lambda a,r:r.update(status='NUMERICAL_ONLY')),
        ('replay_wrong_gap',lambda a,r:r.update(exact_integer_gap=str(int(r['exact_integer_gap'])+1))),
        ('replay_zero_scale',lambda a,r:r.update(integer_scale='0')),
        ('replay_wrong_exclusion',lambda a,r:r.update(fixed_K_excluded=False)),
        ('star_wrong_exclusion',lambda a,r:a.update(positive_exact_dual_excludes_fixed_K=False)),
    ):
        a,r = deepcopy(star),deepcopy(replay);change(a,r)
        rejected(name, lambda a=a,r=r:driver.checked_star_interval(a,r))
    a,r = deepcopy(star),deepcopy(replay)
    a.update(exact_dual_lower=driver.rational(0),positive_exact_dual_excludes_fixed_K=False)
    r.update(exact_integer_gap='0',fixed_K_excluded=False)
    driver.require(driver.checked_star_interval(a,r)[0] == 0, 'Valid nonpositive bound rejected')
    driver.require(not base_args.out.exists(), 'Read-only controls created output')
    report = dict(status='CP_STAR_SHORTLIST_ORCHESTRATION_V2_CONTROLS_PASS',inputs_sha256=inputs,
                  controls=controls,negative_controls=len(controls),all_negative_controls_rejected=True,
                  positive_controls=['historical_nine_selection','real_preflight','fresh_one_candidate_all_stages',
                                     'complete84_pair_binding','exact_positive_replay','nonpositive_bound_remains_nonproof'],
                  integration_summary_path=driver.key(integration_path),integration_summary_sha256=driver.digest(integration_path),
                  guard_process_invocations=0,guard_output_created=False,graph_constructed=False)
    driver.save(args.out,report)
    print(driver.json.dumps(dict(status=report['status'],negative_controls=len(controls),positive_controls=6)))


if __name__ == '__main__':
    main()
