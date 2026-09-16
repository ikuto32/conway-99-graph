"""Compare every CUDA fixed-X phase-I residual against independent full99 rows."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import time

from audit_certificate import require
from audit_phase1 import evaluate

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--phase1', type=Path)
    args = parser.parse_args()
    require(not args.out.exists(), 'QA directory must be new')
    args.out.mkdir(parents=True)
    started = time.perf_counter()
    candidates = [ROOT/'scratch_resume_overlap_lift.json'] + [ROOT/f'scratch_next_overlap_alternatives_r{i}.json' for i in range(4)]
    candidates += [ROOT/'scratch_follow_overlap_walk.json', ROOT/'acceleration/results/20260916_guided_pair_pilot/best_candidate.json']
    data = [json.loads(path.read_bytes()) for path in candidates]
    randomizer = random.Random(20260916)
    vectors = [('zero', [0.0]*1680), ('ones', [1.0]*1680), ('random', [randomizer.random() for _ in range(1680)])]
    if args.phase1:
        phase = json.loads(args.phase1.read_bytes())
        vectors.append(('phase1', [max(0.0, min(1.0, float(value))) for value in phase['numeric_edge_values']]))
    executable = ROOT/'acceleration/build/overlap_phase_gpu.exe'
    reports = []
    max_residual_difference = 0.0
    max_objective_difference = 0.0
    python_seconds = 0.0
    gpu_seconds = 0.0
    kernel_seconds = 0.0
    produced = []
    for name, x in vectors:
        require(len(x) == 1680, 'Wrong X size')
        input_path, output_path = args.out/f'{name}.txt', args.out/f'{name}_gpu.json'
        with input_path.open('x', encoding='ascii') as stream:
            stream.write(f'C99GLOBAL1 {len(data)}\n')
            stream.write(' '.join(format(value, '.17g') for value in x)+'\n')
            for candidate in data:
                stream.write(' '.join(str(v) for edge in candidate['overlap_edges_outer_zero_based'] for v in edge)+'\n')
        subprocess.run([str(executable), str(input_path), str(output_path), '--residuals'], check=True, capture_output=True)
        gpu = json.loads(output_path.read_bytes())
        require(gpu['status'] == 'NUMERICAL_FIXED_X_PHASE1_HEURISTIC' and gpu['candidate_count'] == len(data), 'Wrong GPU batch')
        gpu_seconds += gpu['elapsed_seconds']
        kernel_seconds += gpu['kernel_seconds']
        reference_started = time.perf_counter()
        for index, (candidate, actual) in enumerate(zip(data, gpu['results'])):
            expected = evaluate(candidate, x)
            require(actual['candidate_index'] == index, 'GPU candidate order mismatch')
            residual_difference = 0.0
            for field, length in [('quota_residuals', 840), ('pair_residuals', 3486)]:
                require(len(actual[field]) == len(expected[field]) == length, 'GPU residual dimensions')
                error = max(abs(a-b) for a, b in zip(actual[field], expected[field]))
                residual_difference = max(residual_difference, error)
                require(error < 1e-10, f'Full99 residual mismatch: {name}, {index}, {field}, {error}')
            objective_difference = max(abs(actual[key]-expected[key]) for key in
                                       ('total_violation', 'quota_violation', 'pair_violation'))
            require(objective_difference < 1e-8, f'Phase-I objective mismatch: {name}, {index}')
            require(abs(actual['quota_max_abs']-max(map(abs, expected['quota_residuals']))) < 1e-10,
                    'Quota max mismatch')
            require(abs(actual['pair_max_positive']-max(0, max(expected['pair_residuals']))) < 1e-10,
                    'Pair max mismatch')
            if name == 'zero':
                require(actual['total_violation'] == actual['quota_violation'] == 1344 and actual['pair_violation'] == 0,
                        'Zero-X degree/label balance control failed')
            max_residual_difference = max(max_residual_difference, residual_difference)
            max_objective_difference = max(max_objective_difference, objective_difference)
            reports.append({'x_control': name, 'candidate_index': index,
                            'total_violation': actual['total_violation'], 'quota_violation': actual['quota_violation'],
                            'pair_violation': actual['pair_violation'], 'max_row_difference': residual_difference,
                            'max_objective_component_difference': objective_difference})
        python_seconds += time.perf_counter()-reference_started
        produced.extend([input_path, output_path])
    sources = candidates + produced + [Path(__file__), ROOT/'acceleration/overlap_phase_gpu.cu',
        ROOT/'acceleration/build_overlap_phase_gpu.ps1', executable, ROOT/'acceleration/audit_phase1.py',
        ROOT/'acceleration/audit_certificate.py'] + ([args.phase1] if args.phase1 else [])
    result = {'status': 'ALL_CUDA_PHASE1_RESIDUALS_MATCH_INDEPENDENT_FULL99_NUMERIC_ROWS',
              'candidate_controls': len(data), 'x_controls': [name for name, _ in vectors],
              'quota_residuals_checked': len(reports)*840, 'pair_residuals_checked': len(reports)*3486,
              'max_residual_absolute_difference': max_residual_difference,
              'max_objective_component_absolute_difference': max_objective_difference,
              'python_full99_reference_seconds': python_seconds,
              'cuda_transfer_and_kernel_seconds': gpu_seconds, 'cuda_kernel_seconds': kernel_seconds,
              'records': reports, 'elapsed_seconds': time.perf_counter()-started,
              'inputs_sha256': {path.resolve().relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sources},
              'scope': 'Double-precision frozen-X heuristic merit validated numerically, with all row residuals checked. Does not certify LP optimality, infeasibility, a completion, or global coverage.'}
    (args.out/'review.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records', 'inputs_sha256')}))


if __name__ == '__main__':
    main()
