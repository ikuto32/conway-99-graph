"""Read saved paired benchmark evidence; never execute a scientific backend."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SUMMARY = '690586a3f2023d10ac25a47db1efe71bc093cc04b3ce618d9f5af7375b13879a'
CHECKPOINTS = [1, 2, 10, 500, 2000]
METRICS = {'primal_upper_numeric', 'dual_lower_numeric', 'numeric_gap'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(name):
    return (ROOT / name).resolve()


def digest(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = path(args.out)
    require(not out.exists(), 'Preserve existing review')
    bound = {}

    def bind(name, expected=None):
        p = path(name)
        actual = digest(p)
        require(expected is None or actual == expected, 'Hash mismatch: ' + str(name))
        key = p.relative_to(ROOT).as_posix()
        require(key not in bound or bound[key] == actual, 'Conflicting binding')
        bound[key] = actual
        return p

    def load(name, expected=None):
        return json.loads(bind(name, expected).read_bytes())

    summary_path = bind(args.summary, EXPECTED_SUMMARY)
    summary = load(args.summary, EXPECTED_SUMMARY)
    for field in ('inputs_sha256', 'outputs_sha256'):
        for name, sha in summary[field].items():
            bind(name, sha)
    manifest = load(summary_path.parent / 'manifest.json')
    require(manifest['inputs_sha256'] == summary['inputs_sha256'], 'Timing manifest input mismatch')
    require(manifest['scalar_only'] is True and manifest['trials'] == 3, 'Timing manifest workload')
    export = load('acceleration/results/20260916_star_cuda_controls/real2/manifest.json')
    raw = bind(export['binary_path'], export['binary_sha256']).read_bytes()
    require(len(raw) == export['binary_bytes'] and raw[:8] == b'C99SCP01', 'Binary identity')
    count, ncheck = struct.unpack_from('<II', raw, 8)
    checks = list(struct.unpack_from('<' + 'I' * ncheck, raw, 16))
    require(count == 2 and checks == CHECKPOINTS == export['checkpoints'], 'Binary workload')
    position = 16 + 4 * ncheck
    shapes = []
    for i, case in enumerate(export['cases']):
        start = position
        n, m, q, blocks, nnz = struct.unpack_from('<IIIII', raw, position)
        position += 20
        offsets = list(struct.unpack_from('<' + 'I' * (blocks + 1), raw, position))
        position += 4 * (blocks + 1) + 4 * (m + 1) + 12 * nnz + 4 * (n + 1) + 12 * nnz + 8 * m
        require(case['index'] == i and [case[k] for k in ('N', 'M', 'Q', 'blocks', 'nnz')] == [n, m, q, blocks, nnz], 'Export shape mismatch')
        require(case['offsets'] == offsets and case['record_byte_offset'] == start and case['byte_length'] == position - start, 'Export record span')
        require(hashlib.sha256(raw[start:position]).hexdigest() == case['record_sha256'], 'Export record hash')
        for array in case['arrays'].values():
            first = start + array['relative_byte_offset']
            require(hashlib.sha256(raw[first:first + array['byte_length']]).hexdigest() == array['sha256'], 'Export array hash')
        shapes.append(dict(candidate_index=i, n_variables=n, n_rows=m, n_equalities=q,
                           domain_counts=[b-a for a, b in zip(offsets, offsets[1:])]))
    require(position == len(raw), 'Trailing or truncated binary')
    del raw
    trials = []
    for number, trial in enumerate(summary['trials']):
        require(trial['trial'] == number and trial['order'] == manifest['orders'][number], 'Trial order')
        reports = {}
        for backend in ('cpu', 'gpu'):
            run = trial['runs'][backend]
            report = load(run['result_path'], run['result_sha256'])
            command = run['command']
            require(path(command[-2]) == path(export['binary_path']) and path(command[-1]) == path(run['result_path']), 'Command input/output mismatch')
            require('--vectors' not in command, 'Unexpected vector workload')
            require(report['status'] == ('NUMERICAL_COLD_STAR_CPU_BENCHMARK_FINISHED' if backend == 'cpu' else 'NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED'), 'Completion status')
            require(report['candidate_count'] == len(report['results']) == 2, 'Result count')
            require(report['eta'] == .9 and report['theta'] == 1 and report['float_type'] == 'float64', 'Algorithm parameters')
            require(report['initialization'] == 'uniform_per_simplex_probability_zero_dual' and report['best_scope'] == 'initial_and_requested_checkpoint_last_and_average', 'Cold initialization/checkpoint semantics')
            require(report['numerical_scores_are_proofs'] is False, 'Numeric scope')
            require(run['reported_elapsed_seconds'] == report['elapsed_seconds'] and run['reported_iteration_seconds'] == report[backend + '_iteration_seconds'], 'Saved internal timing mismatch')
            require(math.isfinite(run['process_wall_seconds']) and run['process_wall_seconds'] >= report['elapsed_seconds'] > 0, 'External timing sanity')
            for shape, result in zip(shapes, report['results']):
                require(set(result) == set(shape) | {'initial', 'checkpoints'} and all(result[k] == v for k, v in shape.items()), 'Result ordering/shape/scope')
                require(set(result['initial']) == METRICS, 'Initial scalar schema')
                require([p['iterations'] for p in result['checkpoints']] == CHECKPOINTS, 'Checkpoint ordering')
                upper, lower = result['initial']['primal_upper_numeric'], result['initial']['dual_lower_numeric']
                for point in result['checkpoints']:
                    require(set(point) == {'iterations', 'last', 'average', 'best_upper_numeric', 'best_lower_numeric'}, 'Scalar-only checkpoint schema')
                    require(set(point['last']) == set(point['average']) == METRICS, 'Metric schema')
                    upper = min(upper, point['last']['primal_upper_numeric'], point['average']['primal_upper_numeric'])
                    lower = max(lower, point['last']['dual_lower_numeric'], point['average']['dual_lower_numeric'])
                    require(point['best_upper_numeric'] == upper and point['best_lower_numeric'] == lower, 'Best checkpoint aggregation')
            reports[backend] = report
        errors = []
        for cpu, gpu in zip(reports['cpu']['results'], reports['gpu']['results']):
            comparisons = [(cpu['initial'][k], gpu['initial'][k], 2e-8) for k in METRICS]
            for c, g in zip(cpu['checkpoints'], gpu['checkpoints']):
                tol = 2e-8 if c['iterations'] <= 10 else 2e-6
                comparisons += [(c[p][k], g[p][k], tol) for p in ('last', 'average') for k in METRICS]
                comparisons += [(c[k], g[k], tol) for k in ('best_upper_numeric', 'best_lower_numeric')]
            for a, b, tolerance in comparisons:
                error = abs(a-b)
                require(math.isfinite(a) and math.isfinite(b) and error <= tolerance, 'Scalar parity')
                errors.append(error)
        require(len(errors) == trial['parity']['scalar_checks'] == 86 and max(errors) == trial['parity']['maximum_absolute_error'], 'Saved parity mismatch')
        cpu_seconds = trial['runs']['cpu']['process_wall_seconds']
        gpu_seconds = trial['runs']['gpu']['process_wall_seconds']
        ratio = cpu_seconds / gpu_seconds
        require(ratio == trial['paired_CPU_over_GPU_process_ratio'], 'Paired ratio mismatch')
        trials.append(dict(trial=number, cpu_process_seconds=cpu_seconds, gpu_process_seconds=gpu_seconds,
                           paired_ratio=ratio, scalar_checks=len(errors), maximum_absolute_error=max(errors)))
    require(len(trials) == 3, 'Three trials required')
    median_ratio = statistics.median(t['paired_ratio'] for t in trials)
    median_cpu = statistics.median(t['cpu_process_seconds'] for t in trials)
    median_gpu = statistics.median(t['gpu_process_seconds'] for t in trials)
    require((median_ratio, median_cpu, median_gpu) == (summary['median_paired_process_ratio'], summary['median_cpu_process_seconds'], summary['median_gpu_process_seconds']), 'Median mismatch')
    bind(__file__)
    result = dict(status='INDEPENDENT_SAVED_STAR_PDHG_PAIRED_BENCHMARK_REVIEW_PASS', inputs_sha256=bound,
                  verified_file_count=len(bound), trials=trials, total_scalar_comparisons=258,
                  median_paired_process_ratio=median_ratio, median_cpu_process_seconds=median_cpu,
                  median_gpu_process_seconds=median_gpu, new_scientific_runs=0,
                  source_review=dict(no_workload_or_recurrence_mismatch_found=True,
                      timing_boundary='External perf_counter brackets subprocess.run through process exit; includes startup/imports, binary read/validation, cold iterations, requested scalar metrics and scalar JSON write. Wrapper hash checks, logs and parity checks are outside.',
                      cpu='Python/SciPy, one thread requested before NumPy import, two candidates sequentially.',
                      gpu='CUDA float64, batched candidates, host scalar metrics and checkpoint transfers included.',
                      manifest_binding='Benchmark summary omits its timing manifest from outputs_sha256; this review explicitly binds it and verifies identical inputs.'),
                  limitations=[
                      'Three alternating pairs, two saved models; no new independent wall-clock measurement in this review.',
                      'Warm OS/file cache and concurrent unrelated CPU stronger-LP research were disclosed; no isolated-machine measurement.',
                      'Ratio compares these Python/SciPy and CUDA implementations, not optimized native CPU code or general hardware throughput.',
                      'Scalar-only benchmark; full-vector equivalence and graph/model validity are inherited from separately bound prior controls.',
                      'CPU/GPU invalid-input acceptance is not identical (for example zero nnz); both benchmark models are valid positive-nnz inputs.',
                      'Timing values are saved perf_counter observations, not a cryptographic attestation of execution or environment.'],
                  exclusions_claimed=0)
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], verified_files=len(bound), ratios=[t['paired_ratio'] for t in trials], median=median_ratio, max_error=max(t['maximum_absolute_error'] for t in trials), report_sha256=digest(out))))


if __name__ == '__main__':
    main()
