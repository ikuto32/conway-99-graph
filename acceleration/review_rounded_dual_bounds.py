"""Bounded CPU study of exact grid-dual bounds; not a CUDA/search implementation."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import time

from audit_certificate import require
from audit_phase1 import graph_rows, compare_rows, evaluate

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase1', type=Path, required=True)
    parser.add_argument('--proposal', type=Path, required=True)
    parser.add_argument('--probe-run', type=Path, action='append', default=[])
    parser.add_argument('--sample', type=int, default=64)
    parser.add_argument('--scale', type=int, default=1000000)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve previous study')
    require(0 < args.scale <= (2**63-1)//15372 and 0 <= args.sample <= 256, 'Study budget/scale invalid')
    started = time.perf_counter()
    hashes = {}

    def load(path):
        path = path.resolve()
        raw = path.read_bytes()
        hashes[path.relative_to(ROOT).as_posix()] = sha256(raw).hexdigest()
        return json.loads(raw)

    result = load(args.phase1)
    initial = load(ROOT/result['candidate_path'])
    columns, rows, _ = graph_rows(initial)
    compare_rows(result['constraint_groups'], rows)
    require(result['edge_variables'] == [list(edge) for edge in columns], 'Initial LP variable ordering differs')
    source_weights = {(row['kind'], tuple(row['coordinate'])): weight
                      for row, weight in zip(result['constraint_groups'], result['phase1_multipliers'])}
    numerators = []
    for row in rows:
        weight = Fraction(source_weights.get((row['kind'], tuple(row['coordinate'])), 0))
        weight = min(Fraction(1), max(Fraction(-1 if row['equality'] else 0), weight))
        numerators.append(round(args.scale*weight))
    require(all((-args.scale if row['equality'] else 0) <= n <= args.scale
                for row, n in zip(rows, numerators)), 'Rounded dual weights violate their exact interval')
    row_order = [(row['kind'], tuple(row['coordinate'])) for row in rows]
    exact_initial = evaluate(initial, result['numeric_edge_values'], exact=True)
    threshold = exact_initial['total_violation']
    candidates = {}

    def add(edges, reference, numeric_objective=None):
        key = tuple(sorted(map(tuple, edges)))
        if key not in candidates:
            candidates[key] = {'references': [], 'known_numeric_objectives': []}
        candidates[key]['references'].append(reference)
        if numeric_objective is not None:
            candidates[key]['known_numeric_objectives'].append(numeric_objective)

    add(initial['overlap_edges_outer_zero_based'], {'initial_phase1': str(args.phase1)}, result['numeric_objective'])
    native = load(args.proposal)
    indices = random.Random(20260926).sample(range(len(native['overlap_candidates'])),
                                            min(args.sample, len(native['overlap_candidates'])))
    for index in indices:
        add(native['overlap_candidates'][index], {'proposal_path': str(args.proposal), 'proposal_index': index})
    for directory in args.probe_run:
        for path in sorted((directory/'probes').glob('*_phase1.json')):
            probe = load(path)
            candidate = load(ROOT/probe['candidate_path'])
            add(candidate['overlap_edges_outer_zero_based'], {'phase1_path': str(path)}, probe['numeric_objective'])
    reports = []
    counts = Counter()
    for edges, metadata in candidates.items():
        _, candidate_rows, _ = graph_rows({'overlap_edges_outer_zero_based': [list(e) for e in edges]})
        require([(row['kind'], tuple(row['coordinate'])) for row in candidate_rows] == row_order,
                'Candidate full-row coordinate ordering differs')
        combined = [0]*1680
        quota_incidences, cap_incidences = [0]*1680, [0]*1680
        rhs = 0
        for row, n in zip(candidate_rows, numerators):
            require(0 <= row['target'] <= 2, 'Unexpected target range')
            rhs += row['target']*n
            incidence = quota_incidences if row['equality'] else cap_incidences
            for column in row['terms']:
                combined[column] += n
                incidence[column] += 1
        require(set(quota_incidences) == {4} and set(cap_incidences) == {9}, 'Unexpected column incidence count')
        require(all(-4*args.scale <= value <= 13*args.scale for value in combined), 'Column i64 range derivation failed')
        negative_column_sum = sum(min(0, value) for value in combined)
        numerator = -rhs+negative_column_sum
        require(-15372*args.scale <= numerator <= 1680*args.scale, 'Objective i64 range derivation failed')
        lower = Fraction(numerator, args.scale)
        for optimum in metadata['known_numeric_objectives']:
            require(float(lower) <= optimum+1e-7*max(1, abs(optimum)), 'Exact lower bound exceeds saved numerical optimum')
        positive = numerator > 0
        excludes_improvement = lower >= threshold
        excludes_half_escape = lower > threshold+Fraction(1, 2)
        counts['positive_exact_lower_bound'] += positive
        counts['provably_not_below_initial_feasible_upper_bound'] += excludes_improvement
        counts['provably_above_initial_feasible_upper_bound_plus_half'] += excludes_half_escape
        counts['with_saved_numeric_optimum'] += bool(metadata['known_numeric_objectives'])
        reports.append({**metadata, 'candidate_edges_sha256': sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest(),
                        'weighted_rhs': rhs, 'negative_column_sum': negative_column_sum,
                        'exact_lower_numerator': numerator, 'exact_lower_denominator': args.scale,
                        'lower_bound_approximate': float(lower),
                        'cannot_improve_initial_feasible_upper_bound': excludes_improvement,
                        'above_initial_feasible_upper_bound_plus_half': excludes_half_escape})
    for path in (Path(__file__), Path(__file__).with_name('audit_phase1.py'), Path(__file__).with_name('audit_certificate.py')):
        hashes[path.resolve().relative_to(ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    output = {'status': 'BOUNDED_EXACT_GRID_DUAL_CPU_STUDY', 'scale': args.scale,
              'source_phase1': str(args.phase1), 'rounded_full_row_numerators': numerators,
              'row_order': '840 independent quota rows followed by all3486 lexicographic outer-pair rows',
              'rounding': 'Nearest integer with ties to even, performed on the exact rational value of each stored binary float after exact interval clipping.',
              'initial_feasible_upper_bound': {'numerator': str(threshold.numerator), 'denominator': str(threshold.denominator),
                                               'approximate': float(threshold)},
              'uniform_native_proposal_sample_count': len(indices), 'unique_candidates_checked': len(reports),
              'counts': dict(counts), 'minimum_exact_lower_bound_approximate': min(row['lower_bound_approximate'] for row in reports),
              'maximum_exact_lower_bound_approximate': max(row['lower_bound_approximate'] for row in reports),
              'guaranteed_i64_ranges': {'combined_column_numerator': [-4*args.scale, 13*args.scale],
                                      'objective_numerator': [-15372*args.scale, 1680*args.scale]},
              'all_column_incidences_independently_verified': {'quota': 4, 'pair_cap': 9},
              'candidate_reports': reports, 'inputs_sha256': hashes, 'elapsed_seconds': time.perf_counter()-started,
              'scope': 'A bounded sample with one frozen rounded dual. Exact lower bounds apply only to their fixed candidates. Uniform sample and previously optimized candidates are separate sources; this is not all-family screening. No native/GPU implementation or search policy change. Rejecting non-improving candidates would still need a separate policy for deliberately uphill exploration.'}
    args.out.write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k not in ('rounded_full_row_numerators','candidate_reports','inputs_sha256')}))


if __name__ == '__main__':
    main()
