"""Review saved PDHG associations and statistics; never run an iteration or LP."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    return (ROOT/str(name).replace('\\', '/')).resolve()


def key(name):
    return resolve(name).relative_to(ROOT).as_posix()


def read(name):
    return json.loads(resolve(name).read_bytes())


def exact(q):
    return Fraction(int(q['numerator']), int(q['denominator']))


def ranks(values):
    # Independent comparison-count construction; no sorted tie groups.
    return [sum(other < value for other in values)+(sum(other == value for other in values)+1)/2 for value in values]


def correlation(left, right):
    a, b = math.fsum(left)/len(left), math.fsum(right)/len(right)
    x, y = [v-a for v in left], [v-b for v in right]
    return math.fsum(v*w for v, w in zip(x, y))/math.sqrt(math.fsum(v*v for v in x)*math.fsum(w*w for w in y))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    require(not resolve(args.out).exists(), 'Fresh review report required')
    directory = ROOT/'acceleration/results/20260916_star_pdhg_quality14'
    summary_path = directory/'summary.json'
    summary = read(summary_path)
    require(summary['status'] == 'BOUNDED_STAR_PDHG_QUALITY_STUDY_FINISHED' and
            summary['requested_candidates'] == summary['recorded_candidates'] == 14 and
            summary['requested_runs'] == summary['recorded_runs'] == summary['complete2000_runs'] == 28 and
            not summary['time_cap_reached'], 'Incomplete saved quality study')
    bindings = {}
    def bind(name, expected=None):
        label = key(name)
        if label not in bindings:
            bindings[label] = sha256(resolve(name).read_bytes()).hexdigest()
        require(expected is None or expected == bindings[label], 'Changed file: '+label)
        return bindings[label]
    for name in (Path(__file__), summary_path, directory/'comparison.md', ROOT/'acceleration/study_star_pdhg_quality.py'):
        bind(name)
    for mapping in (summary['inputs_sha256'], summary['outputs_sha256']):
        for name, expected in mapping.items():
            bind(name, expected)
    manifest = read(directory/'manifest.json')
    baseline = read(manifest['baseline_phase_path'])
    bind(manifest['baseline_phase_path'], manifest['baseline_phase_sha256'])
    baseline_tables = read(baseline['domains_path'])['domains']
    baseline_probs = baseline['numeric_probabilities']
    baseline_lookup, offset = [], 0
    for record in baseline_tables:
        masks = [int(mask, 16) for mask in record['domain_masks_hex']]
        baseline_lookup.append(dict(zip(masks, baseline_probs[offset:offset+len(masks)])))
        offset += len(masks)
    require(offset == len(baseline_probs), 'Warm baseline length mismatch')
    shortlist_path = ROOT/'acceleration/results/20260916_star_guided_round1/star_shortlist/summary.json'
    ranking_path = ROOT/'acceleration/results/20260916_star_dual_cross8837/summary.json'
    shortlist, ranking = read(shortlist_path), read(ranking_path)
    bind(shortlist_path); bind(ranking_path)
    source_rows = {row['proposal_index']: row for row in shortlist['records']}
    fixed_scores = {row['index']: Fraction(row['score_numerator'], row['denominator']) for row in ranking['ranked']}
    require(len(source_rows) == 14 and set(source_rows) == set(r['index'] for r in summary['records']), 'Different14 cohort')
    cases, truth = {}, {}
    parity_error, transfer_error, associations = 0., 0., 0
    for record in summary['records']:
        bind(record['path'], record['sha256'])
        case = read(record['path']); index = case['index']; source = source_rows[index]
        require(index == record['index'], 'Saved case/index mismatch')
        for label in ('candidate', 'audit', 'result'):
            bind(source[label+'_path'], source[label+'_sha256'])
        require(case['candidate_path'] == source['candidate_path'] and case['candidate_sha256'] == source['candidate_sha256'] and
                case['reference_audit_path'] == source['audit_path'] and case['reference_audit_sha256'] == source['audit_sha256'], 'Reference association mismatch')
        phase, audit = read(source['result_path']), read(source['audit_path'])
        require(audit['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', 'Unaudited reference')
        evidence = {key(name): h for name, h in audit['inputs_sha256'].items()}
        require(evidence[key(source['result_path'])] == source['result_sha256'] and
                evidence[key(source['candidate_path'])] == source['candidate_sha256'], 'Exact reference hash association')
        lower, upper = exact(audit['exact_dual_lower']), exact(audit['exact_primal_upper'])
        require(lower == exact(source['exact_lower']) and upper == exact(source['exact_upper']) and
                case['exact_star_interval'] == record['exact_star_interval'] == [float(lower), float(upper)], 'Exact interval differs')
        truth[index] = (lower, upper)
        error = max(abs(case['reference_numeric_check']['primal_upper_numeric']-phase['numeric_objective']),
                    abs(case['reference_numeric_check']['dual_lower_numeric']-phase['numeric_simplex_dual_lower']))
        require(error == case['reference_max_error'] and error < 1e-8, 'Reference numerical parity record differs')
        parity_error = max(parity_error, error)
        targets = read(phase['domains_path'])['domains']
        require(len(case['warm_transfer']) == len(targets) == 84, 'Warm transfer84 required')
        for u, (target, declared) in enumerate(zip(targets, case['warm_transfer'])):
            masks = [int(mask, 16) for mask in target['domain_masks_hex']]
            lookup = baseline_lookup[u]
            mass = math.fsum(lookup.get(mask, 0.) for mask in masks)
            require(declared['outer_vertex'] == u and declared['source_domains'] == len(lookup) and
                    declared['target_domains'] == len(masks) and declared['common_masks'] == sum(mask in lookup for mask in masks) and
                    declared['uniform_fallback'] == (mass == 0), 'Warm exact-mask/fallback association differs')
            transfer_error = max(transfer_error, abs(mass-declared['retained_probability_mass']))
            associations += 1
        require(len(case['runs']) == 2 and [r['start'] for r in case['runs']] == manifest['starts'], 'Missing/reordered starts')
        for run in case['runs']:
            require(run['complete'] and run['iterations_executed'] == 2000 and
                    [p['iterations'] for p in run['checkpoints']] == [500, 2000], 'Incomplete checkpoint')
            best_upper, best_lower = run['initial']['primal_upper_numeric'], run['initial']['dual_lower_numeric']
            if run['start'] == 'cold_uniform_zero_dual':
                require(best_lower == 0, 'Zero dual should give zero lower hint')
            for point in run['checkpoints']:
                for state in ('last', 'average'):
                    values = point[state]
                    require(all(math.isfinite(v) for v in values.values()), 'Nonfinite checkpoint scalar')
                    require(values['primal_upper_numeric'] >= float(lower)-1e-7 and
                            values['dual_lower_numeric'] <= float(upper)+1e-7, 'Saved numerical diagnostic contradicts reference')
                    best_upper = min(best_upper, values['primal_upper_numeric'])
                    best_lower = max(best_lower, values['dual_lower_numeric'])
                require(best_upper == point['best_upper_numeric'] and best_lower == point['best_lower_numeric'], 'Best includes wrong history')
        cases[index] = case
    require(transfer_error < 1e-12, 'Warm retained mass mismatch')
    true_order = sorted(truth, key=lambda i: truth[i][1])
    require(all(truth[a][1] < truth[b][0] for a, b in zip(true_order, true_order[1:])), 'Exact order not separated')
    metric_error = 0.
    metrics = []
    for metric in summary['metrics']:
        indices = metric['indices']; require(indices == sorted(cases) and metric['coverage'] == 14, 'Metric cohort differs')
        scores = []
        for i in indices:
            run = next(r for r in cases[i]['runs'] if r['start'] == metric['start'])
            point = next(p for p in run['checkpoints'] if p['iterations'] == metric['iterations'])
            field = metric['score']
            if field == 'fixed_dual':
                value = fixed_scores[i]
            elif field.startswith('best_'):
                value = point[field]
            else:
                state, direction = field.split('_')
                value = point[state]['primal_upper_numeric' if direction == 'upper' else 'dual_lower_numeric']
            scores.append(value)
        exact_truth = [(truth[i][0]+truth[i][1])/2 for i in indices]
        rho = correlation(ranks(scores), ranks(exact_truth))
        pearson = correlation(list(map(float, scores)), list(map(float, exact_truth)))
        predicted = sorted(indices, key=lambda i: (scores[indices.index(i)], i))[:4]
        actual = set(true_order[:4])
        require(metric['top_k'] == 4 and metric['predicted_top'] == predicted and metric['actual_top'] == sorted(actual) and
                metric['top_k_recall'] == len(set(predicted)&actual)/4, 'Top4 claim differs')
        metric_error = max(metric_error, abs(rho-metric['spearman']), abs(pearson-metric['pearson']))
        metrics.append(dict(start=metric['start'], iterations=metric['iterations'], score=metric['score'],
            independently_recomputed_spearman=rho, top4_recall=len(set(predicted)&actual)/4, predicted_top=predicted))
    require(len(metrics) == 28 and metric_error < 1e-14, 'Saved correlation differs')
    report = dict(status='INDEPENDENT_SAVED_STAR_PDHG_ASSOCIATIONS_AND_RANKING_METRICS_REVIEW_PASS',
        inputs_sha256=bindings, saved_candidates_checked=14, saved_runs_checked=28, saved_checkpoint_states_checked=112,
        exact_reference_intervals_strictly_separated=True, warm_vertex_mask_associations_checked=associations,
        maximum_saved_reference_parity_error=parity_error, maximum_warm_mass_recomputation_error=transfer_error,
        maximum_ranking_metric_recomputation_error=metric_error, metrics=metrics, substantive_issue_found=False,
        source_review=['Cold initialization is uniform within each vertex and zero dual; no solved probability vector is used.',
            'Warm start uses baseline25496 exact vertex/mask transfer and its dual in constant row coordinates.',
            'Every run resets pbar and averages; average includes new iterates1 through checkpoint.',
            'Best statistics include initialization plus requested last/average checkpoints only.',
            'Both upper and lower numerical hints rank ascending, with deterministic index ties.',
            'The14 cases were selected by prior CP and local gates; results are retrospective on this cohort.'],
        packaging_note='comparison.md is absent from summary.outputs_sha256 because it was written later; it is explicitly bound in this review.',
        new_PDHG_iterations=0, new_LP_runs=0, GPU_runs=0,
        scope='Read-only review of frozen source, saved input associations and scalar statistics. Existing matrix parity values are association-checked, not independently rerun. This review does not validate every floating iterate or establish generalization beyond the selected14.')
    with resolve(args.out).open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps(dict(status=report['status'], files_bound=len(bindings), max_metric_error=metric_error,
        actual_top4=true_order[:4], sha256=sha256(resolve(args.out).read_bytes()).hexdigest())))


if __name__ == '__main__':
    main()
