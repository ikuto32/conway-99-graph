"""Bounded simplex/CSR PDHG controls and saved-LP profiling, without LP/GPU runs."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import statistics
import time

import numpy as np
import scipy

from star_marginal_cp_cpu_v2 import (build_model, diagonal_steps, factored_forward,
    factored_transpose, numeric_bounds, product_simplex_projection, simplex_projection, step, transfer_probabilities)

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def resolve(path):
    path = Path(path)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def key(path):
    return resolve(path).relative_to(ROOT).as_posix()


def digest(path):
    return sha256(resolve(path).read_bytes()).hexdigest()


def exact_projection(z):
    """Independent tiny oracle: enumerate supports, check exact KKT inequalities."""
    answer = None
    for bits in range(1, 1 << len(z)):
        active = [i for i in range(len(z)) if bits >> i & 1]
        threshold = (sum((z[i] for i in active), Fraction(0))-1) / len(active)
        if not all((z[i] > threshold) == bool(bits >> i & 1) for i in range(len(z))):
            continue
        current = [max(Fraction(0), value-threshold) for value in z]
        require(sum(current) == 1 and min(current) >= 0, 'Exact oracle simplex failure')
        require(answer is None or answer == current, 'Nonunique exact projection')
        answer = current
    require(answer is not None, 'No exact projection')
    return answer


def operator_controls():
    rng = random.Random(20260916)
    cases = [[Fraction(x, 4) for x in values] for n in (1, 3, 4)
             for values in product(range(-2, 3), repeat=n)]
    cases += [[Fraction(rng.randrange(-16, 17), 8) for _ in range(n)]
              for n in (2, 5, 6, 7, 8) for _ in range(8)]
    cases += [[Fraction(2**40)+Fraction(i, 4) for i in (0, -1, -1, -2)],
              [Fraction(-2**40)+Fraction(i, 4) for i in (0, -1, -1, -2)]]
    maximum = 0.0
    for values in cases:
        expected = np.asarray(list(map(float, exact_projection(values))))
        actual = simplex_projection(list(map(float, values)))
        maximum = max(maximum, float(np.max(abs(actual-expected))))
        require(np.max(abs(actual-expected)) <= 2e-14, 'Exact support-enumeration mismatch')
    extreme = simplex_projection([0, -1e308, -1e308])
    require(np.array_equal(extreme, [1, 0, 0]), 'Extreme finite prefix-sum regression')
    large = []
    for n in (84, 1053, 2049):
        values = np.asarray([rng.randrange(-32, 33)/16 for _ in range(n)])
        p = simplex_projection(values)
        support = p > 0
        threshold = float(np.mean(values[support]-p[support]))
        err = max(abs(float(p.sum())-1), float(np.max(abs(values[support]-p[support]-threshold))),
                  max(0.0, float(np.max(values[~support]-threshold))) if np.any(~support) else 0.0)
        require(err < 2e-12 and np.min(p) >= 0, 'Large simplex KKT failure')
        permutation = np.arange(n); rng.shuffle(permutation)
        require(np.max(abs(simplex_projection(values[permutation])-p[permutation])) < 1e-14,
                'Simplex permutation mismatch')
        require(np.max(abs(simplex_projection(values+8192)-p)) < 1e-14, 'Translation mismatch')
        large.append(dict(size=n, active=int(support.sum()), max_numeric_kkt_residual=err))
    negatives = []
    for name, values in [('empty', []), ('nan', [0, float('nan')]), ('inf', [float('inf')]),
                         ('not_vector', [[1, 2]]), ('unrepresentable_differences', [1e308, -1e308])]:
        try:
            simplex_projection(values)
        except ValueError:
            negatives.append(name)
        else:
            raise ValueError('Projection accepted invalid input: '+name)
    # An independent exact rational recurrence on a two-simplex toy saddle model.
    A = [[1, -1, 0, 0], [0, 0, 1, -1], [1, 0, 1, 0]]
    b = [Fraction(0), Fraction(0), Fraction(1, 2)]
    p = [Fraction(1, 4), Fraction(3, 4), Fraction(1, 2), Fraction(1, 2)]
    pbar, y = p[:], [Fraction(1, 8), Fraction(-1, 8), Fraction(1, 4)]
    fp, fbar, fy = np.asarray(p, dtype=float), np.asarray(pbar, dtype=float), np.asarray(y, dtype=float)
    mat = np.asarray(A, dtype=float)
    recurrence_error = 0.0
    for _ in range(10):
        ynew = [min(Fraction(1), max(Fraction(-1 if i < 2 else 0), y[i]+Fraction(9, 100)*
                 (sum(A[i][j]*pbar[j] for j in range(4))-b[i]))) for i in range(3)]
        trial = [p[j]-Fraction(9, 100)*sum(A[i][j]*ynew[i] for i in range(3)) for j in range(4)]
        pnew = exact_projection(trial[:2])+exact_projection(trial[2:])
        pbar, p, y = [2*a-c for a, c in zip(pnew, p)], pnew, ynew
        fy = np.clip(fy+.09*(mat@fbar-np.asarray(b, dtype=float)), [-1, -1, 0], 1)
        fnew = product_simplex_projection(fp-.09*(mat.T@fy), [0, 2, 4])
        fbar, fp = 2*fnew-fp, fnew
        recurrence_error = max(recurrence_error, float(np.max(abs(fp-np.asarray(p, dtype=float)))),
                               float(np.max(abs(fy-np.asarray(y, dtype=float)))))
    require(recurrence_error < 2e-14, 'Independent rational recurrence mismatch')
    # Reordered masks, removed source mass, unknown target masks, and no-mass
    # fallback are independently specified, not derived using the transfer.
    mapped, metadata = transfer_probabilities([[11, 22, 33], [7, 8], [7, 8]],
        [0.25, 0.5, 0.25, 0.75, 0.25, 1.0, 0.0], [[33, 11, 44], [9, 10], [8, 9]])
    require(np.array_equal(mapped, [0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.5]), 'Exact mask transfer mismatch')
    require([r['uniform_fallback'] for r in metadata] == [False, True, True] and
            [r['common_masks'] for r in metadata] == [2, 0, 1], 'Wrong transfer association/fallback')
    return dict(status='EXACT_TINY_SIMPLEX_ORACLE_AND_NUMERICAL_PDHG_CONTROLS_PASS',
                exact_projection_cases=len(cases), max_projection_error=maximum, large_size_controls=large,
                negative_controls=negatives, tiny_exact_recurrence_steps=10,
                maximum_exact_recurrence_float_error=recurrence_error,
                extreme_finite_projection_control=extreme.tolist(),
                exact_mask_association_and_zero_mass_fallback_controls=metadata)


def sparse_bytes(matrix):
    return matrix.data.nbytes+matrix.indices.nbytes+matrix.indptr.nbytes


def time_repeated(function, count=100):
    started = time.perf_counter()
    for _ in range(count):
        function()
    return (time.perf_counter()-started)/count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Output must be fresh')
    started = time.perf_counter()
    bindings = {}
    def bind(path, expected=None):
        name = key(path)
        value = digest(path)
        require(expected is None or value == expected, 'Changed bound input: '+name)
        require(name not in bindings or bindings[name] == value, 'Conflicting source binding')
        bindings[name] = value
        return value
    for name in (__file__, 'acceleration/star_marginal_cp_cpu_v2.py', 'acceleration/audit_certificate.py'):
        bind(name)
    controls = operator_controls()
    profiles = []
    paths = sorted((ROOT/'acceleration/results/20260916_star_marginal_shortlist').glob('index_*/phase1.json'))
    paths += [ROOT/f'acceleration/results/20260916_star_marginal_pilot/index_{i}.json' for i in (226, 2700)]
    for path in paths:
        bind(path)
        record = json.loads(path.read_bytes())
        profiles.append(dict(path=key(path), domain_variables=record['domain_variables'],
            min_domain=min(record['domain_counts']), max_domain=max(record['domain_counts']),
            matrix_nonzeros=record['matrix_nonzeros'], augmented_nonzeros=record['augmented_nonzeros'],
            build_seconds=record['build_seconds'], solve_seconds=record['solve_seconds'],
            solve_fraction=record['solve_seconds']/(record['build_seconds']+record['solve_seconds'])))
    cases = []
    baseline_phase, baseline_tables = None, None
    for index in (25496, 26025):
        phase_path = ROOT/f'acceleration/results/20260916_star_marginal_shortlist/index_{index}/phase1.json'
        audit_path = phase_path.with_name('audit.json')
        bind(phase_path); bind(audit_path)
        phase, audit = json.loads(phase_path.read_bytes()), json.loads(audit_path.read_bytes())
        require(audit['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', 'Reference audit failed')
        for name, expected in audit['inputs_sha256'].items():
            bind(name, expected)
        require(audit['inputs_sha256'].get(key(phase_path)) == digest(phase_path), 'Reference phase binding')
        candidate_path, domains_path, domain_audit_path = map(resolve,
            (phase['candidate_path'], phase['domains_path'], phase['domain_audit_path']))
        for path, field in ((candidate_path, 'candidate_sha256'), (domains_path, 'domains_sha256'),
                            (domain_audit_path, 'domain_audit_sha256')):
            bind(path, phase[field])
        proof = json.loads(domain_audit_path.read_bytes())
        require(proof['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
                proof['complete_used_domains_verified'], 'Complete-domain audit required')
        for name, expected in proof['inputs_sha256'].items():
            bind(name, expected)
        domains = json.loads(domains_path.read_bytes())
        require(domains['complete_domain_enumeration'] and all(r['status'] == 'COMPLETE' for r in domains['domains']),
                'Incomplete domains')
        proof_bindings = {key(name): value for name, value in proof['inputs_sha256'].items()}
        require(proof_bindings[key(domains_path)] == digest(domains_path) and
                proof_bindings[key(candidate_path)] == digest(candidate_path), 'Domain proof association')
        build_start = time.perf_counter()
        model = build_model(json.loads(candidate_path.read_bytes()), domains['domains'])
        build_seconds = time.perf_counter()-build_start
        A, AT, offsets = model['A'], model['AT'], model['offsets']
        require(model['counts'].tolist() == phase['domain_counts'] and
                model['counts'].tolist() == [r['domain_size'] for r in proof['independently_reenumerated_domains']], 'Domain ordering/counts')
        require(A.nnz+A.shape[1] == phase['matrix_nonzeros'], 'Independent coefficient count disagrees')
        p_ref = np.asarray(phase['numeric_probabilities'])
        y_ref = np.r_[phase['numeric_reciprocity_duals'], phase['numeric_cap_duals']]
        require(np.all(np.isfinite(p_ref)) and np.all(p_ref >= 0) and
                np.all(np.isfinite(y_ref)) and np.all(y_ref <= 1) and
                np.all(y_ref[:1680] >= -1) and np.all(y_ref[1680:] >= 0), 'Reference numerical boxes')
        ref_eval = numeric_bounds(model, p_ref, y_ref)
        ref_error = max(abs(ref_eval['primal_upper_numeric']-phase['numeric_objective']),
                        abs(ref_eval['dual_lower_numeric']-phase['numeric_simplex_dual_lower']))
        require(ref_error < 1e-8, 'Independent full99 matrix/reference merit mismatch')
        tau, sigma = diagonal_steps(model)
        row_max, col_max = float(max(model['row_sums'])), float(max(model['col_sums']))
        constant_step = .9/(row_max*col_max)**.5
        rng = np.random.default_rng(20260916+index)
        p_test, y_test = rng.random(A.shape[1]), rng.uniform(-1, 1, A.shape[0])
        factor_error = max(float(np.max(abs(A@p_test-factored_forward(model, p_test)))),
                           float(np.max(abs(AT@y_test-factored_transpose(model, y_test)))))
        require(factor_error < 1e-9, 'Factorized/explicit matrix mismatch')
        timings = dict(explicit_forward_seconds=time_repeated(lambda: A@p_test),
                       explicit_transpose_seconds=time_repeated(lambda: AT@y_test),
                       factored_forward_seconds=time_repeated(lambda: factored_forward(model, p_test)),
                       factored_transpose_seconds=time_repeated(lambda: factored_transpose(model, y_test)),
                       product_simplex_projection_seconds=time_repeated(lambda: product_simplex_projection(p_test, offsets)))
        p0 = np.repeat(1.0/model['counts'], model['counts'])
        y0 = np.zeros(5166)
        runs = []
        starts = [
                ('uniform_probability_zero_dual', p0, y0, [10, 100, 500, 2000]),
                ('stored_optimum_control', p_ref, y_ref, [1, 10])]
        transfer = None
        tables = [[int(mask, 16) for mask in row['domain_masks_hex']] for row in domains['domains']]
        if baseline_phase is not None:
            mapped, transfer = transfer_probabilities(baseline_tables,
                baseline_phase['numeric_probabilities'], tables)
            reused_y = np.r_[baseline_phase['numeric_reciprocity_duals'], baseline_phase['numeric_cap_duals']]
            starts.append(('baseline25496_exact_mask_probability_and_dual_transfer', mapped, reused_y, [10, 100, 500, 2000]))
        else:
            baseline_phase, baseline_tables = phase, tables
        for start_name, initial_p, initial_y, checkpoints in starts:
            p, pbar, y = initial_p.copy(), initial_p.copy(), initial_y.copy()
            pavg, yavg = np.zeros_like(p), np.zeros_like(y)
            initial = numeric_bounds(model, p, y)
            best_upper, best_lower = initial['primal_upper_numeric'], initial['dual_lower_numeric']
            records = []
            run_start = time.perf_counter()
            for iteration in range(1, checkpoints[-1]+1):
                p, pbar, y = step(model, p, pbar, y, tau, sigma)
                pavg += (p-pavg)/iteration; yavg += (y-yavg)/iteration
                if iteration not in checkpoints:
                    continue
                simplex_error = max(abs(float(p[a:b].sum())-1) for a, b in zip(offsets[:-1], offsets[1:]))
                require(simplex_error < 1e-10 and np.min(p) >= 0 and np.all(np.isfinite(p)) and
                        np.all(np.isfinite(y)), 'Numerical simplex/finite invariant failed')
                last, average = numeric_bounds(model, p, y), numeric_bounds(model, pavg, yavg)
                for point in (last, average):
                    require(point['primal_upper_numeric'] >= audit['exact_dual_lower']['approximate']-1e-7 and
                            point['dual_lower_numeric'] <= audit['exact_primal_upper']['approximate']+1e-7,
                            'Numerical bound contradicts independently exact interval')
                best_upper = min(best_upper, last['primal_upper_numeric'], average['primal_upper_numeric'])
                best_lower = max(best_lower, last['dual_lower_numeric'], average['dual_lower_numeric'])
                records.append(dict(iteration=iteration, last=last, ergodic_average=average,
                    best_upper_over_initial_and_checkpoints=best_upper,
                    best_lower_over_initial_and_checkpoints=best_lower,
                    max_simplex_sum_residual=simplex_error, computation_seconds=time.perf_counter()-run_start))
            runs.append(dict(initialization=start_name, initial=initial, checkpoints=records))
            print(json.dumps(dict(index=index, initialization=start_name, final=records[-1])), flush=True)
        cases.append(dict(index=index, candidate_path=key(candidate_path), phase_path=key(phase_path),
            reference_audit_path=key(audit_path), exact_reference_lower=audit['exact_dual_lower'],
            exact_reference_upper=audit['exact_primal_upper'], reference_scalar_error=ref_error,
            rows=A.shape[0], columns=A.shape[1], min_domain=int(min(model['counts'])), max_domain=int(max(model['counts'])),
            nonzeros=A.nnz, absolute_row_sum_max=row_max, absolute_column_sum_max=col_max,
            norm_squared_scalar_upper_bound=row_max*col_max, safe_equal_scalar_step=constant_step,
            diagonal_eta=.9, diagonal_weighted_norm_squared_bound=.81,
            tau_min=float(min(tau)), tau_max=float(max(tau)), sigma_min=float(min(sigma)), sigma_max=float(max(sigma)),
            coefficients_are_integral=bool(np.all(A.data == np.rint(A.data))), max_abs_coefficient=float(max(abs(A.data))),
            explicit_forward_transpose_csr_bytes=sparse_bytes(A)+sparse_bytes(AT),
            factored_forward_transpose_csr_bytes=sum(sparse_bytes(model[name]) for name in ('R','RT','E','ET','C','CT')),
            factorized_nonzeros=sum(model[name].nnz for name in ('R','E','C')), factorized_parity_error=factor_error,
            model_build_seconds=build_seconds, per_operation_cpu_timings=timings,
            warm_probability_transfer=transfer, runs=runs))
    require(all(digest(name) == expected for name, expected in bindings.items()), 'Input/source changed during study')
    report = dict(status='STAR_SIMPLEX_PDHG_CPU_V2_REFERENCE_WARM_TRANSFER_AND_BOUNDED_QUALITY_CONTROLS_PASS',
        inputs_sha256=bindings, operator_controls=controls, saved_lp_profiles=profiles,
        median_saved_lp_solve_seconds=statistics.median(r['solve_seconds'] for r in profiles),
        minimum_saved_lp_solve_fraction=min(r['solve_fraction'] for r in profiles), cases=cases,
        float_type='float64', numpy_version=np.__version__, scipy_version=scipy.__version__,
        new_lp_runs=0, gpu_runs=0, optimization_producer_imported=False, numerical_values_are_proofs=False,
        scope='Two saved fixed-K controls only, including exact-mask warm transfer25496 to26025. Existing independently exact intervals are hash-bound references; CP floating values are numerical diagnostics. No CUDA implementation, batch research search, graph construction, or new exclusion claim.',
        elapsed_seconds=time.perf_counter()-started)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, separators=(',', ':'), allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'], elapsed_seconds=report['elapsed_seconds'], out=key(args.out))), flush=True)


if __name__ == '__main__':
    main()
