"""Compare manifest-bound Rust/CUDA scores with the historical Python evaluator."""
import argparse
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scratch_next_overlap_cut_bank import evaluate
from scratch_next_overlap_cut_orbit import transform
from audit_certificate import full_graph
from prepare import (all_cuts, cut_text, digest, path_key, recorded_path,
                     require, verify_manifest)


def read_candidates(path):
    tokens = iter(path.read_text(encoding='ascii').split())
    require(next(tokens, None) == 'C99OVERLAPS1', 'Wrong candidate header')
    count = int(next(tokens))
    require(0 < count <= 100000, 'Invalid candidate count')
    candidates = []
    for _ in range(count):
        edges = [[int(next(tokens)), int(next(tokens))] for _ in range(168)]
        full_graph({'overlap_edges_outer_zero_based': edges})
        candidates.append(frozenset(map(tuple, edges)))
    require(next(tokens, None) is None, 'Trailing candidate input')
    return candidates


def check_tensor(scores, candidate_count, cut_count):
    require(type(scores) is list and len(scores) == candidate_count, 'Wrong score candidate dimension')
    for candidate in scores:
        require(type(candidate) is list and len(candidate) == cut_count, 'Wrong score cut dimension')
        for row in candidate:
            require(type(row) is list and len(row) == 128, 'Wrong score mask dimension')
            require(all(type(value) is int and -(2**63) <= value < 2**63 for value in row),
                    'Scores must be exact signed i64 integers')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, help='Default: manifest.json beside candidate input; must exist')
    parser.add_argument('--cpu', type=Path, required=True)
    parser.add_argument('--gpu', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reference-limit', type=int, default=0,
                        help='0 checks every Python score; a positive prefix produces a partial-reference status')
    parser.add_argument('--extra-certificate', type=Path, action='append', default=[])
    parser.add_argument('--certificate-audit', type=Path, action='append', default=[])
    args = parser.parse_args()
    require(not args.out.exists(), f'Output already exists: {args.out}')
    require(args.reference_limit >= 0, '--reference-limit must be nonnegative')
    manifest_path = args.manifest or args.candidates.parent/'manifest.json'
    manifest = verify_manifest(manifest_path, args.candidates)
    certificates, audits = args.extra_certificate, args.certificate_audit
    if not certificates and not audits:
        certificates = [recorded_path(r['certificate']) for r in manifest.get('extra_cut_certificates', [])]
        audits = [recorded_path(r['audit']) for r in manifest.get('extra_cut_certificates', [])]
    cuts = all_cuts(certificates, audits)
    require(len(cuts) == manifest['cuts'], 'Reference cut count differs from manifest')
    cut_path = manifest_path.parent/'cuts.txt'
    require(cut_path.read_text(encoding='ascii').split() == cut_text(cuts).split(),
            'Reference cuts differ from the manifest-bound native cut input')
    candidates = read_candidates(args.candidates)
    require(len(candidates) == manifest['candidates'], 'Candidate count differs from manifest')
    cpu, gpu = [json.loads(p.read_bytes()) for p in (args.cpu, args.gpu)]
    for result in (cpu, gpu):
        check_tensor(result['scores'], len(candidates), len(cuts))
        require(type(result.get('repeats')) is int and result['repeats'] > 0, 'Invalid benchmark repeats')
        require(type(result.get('evaluations')) is int and
                result['evaluations'] == len(candidates)*len(cuts)*128*result['repeats'],
                'Benchmark evaluation count mismatch')
        require(type(result.get('elapsed_seconds')) in (int, float) and
                math.isfinite(result['elapsed_seconds']) and result['elapsed_seconds'] > 0,
                'Invalid benchmark elapsed time')
    require(cpu['scores'] == gpu['scores'], 'Rust/CUDA mismatch')
    count, minima = 0, []
    reference = candidates[:args.reference_limit] if args.reference_limit else candidates
    started = time.perf_counter()
    for i, candidate in enumerate(reference):
        images = [transform(candidate, mask) for mask in range(128)]
        minimum = []
        for j, cut in enumerate(cuts):
            values = [evaluate(image, cut)['score'] for image in images]
            require(values == cpu['scores'][i][j], f'Python/native score mismatch at candidate {i}, cut {j}')
            minimum.append(min(values))
            count += 128
        minima.append(minimum)
        print(json.dumps({'reference_candidate': i, 'minima': minimum}), flush=True)
    seconds = time.perf_counter()-started
    complete = len(reference) == len(candidates)
    sources = [args.candidates, cut_path, manifest_path, args.cpu, args.gpu, Path(__file__),
               ROOT/'acceleration/prepare.py', ROOT/'acceleration/audit_certificate.py',
               ROOT/'acceleration/overlap_cpu.rs', ROOT/'acceleration/overlap_gpu.cu',
               ROOT/'scratch_next_overlap_cut_bank.py', ROOT/'scratch_next_overlap_cut_orbit.py']
    sources += certificates + audits
    result = {'status': 'PYTHON_RUST_CUDA_EXACT_SCORE_PARITY_PASS' if complete
                       else 'RUST_CUDA_PARITY_WITH_PARTIAL_PYTHON_REFERENCE_PASS',
              'manifest_sha256': digest(manifest_path), 'python_reference_complete': complete,
              'candidate_count': len(candidates), 'cut_count': len(cuts), 'sign_masks': 128,
              'partial_graphs_checked': len(candidates), 'python_reference_scores_checked': count,
              'rust_cuda_scores_checked': len(candidates)*len(cuts)*128,
              'python_reference_seconds': seconds, 'reference_cut_minima': minima,
              'cpu_evaluations_per_second': cpu['evaluations']/cpu['elapsed_seconds'],
              'gpu_evaluations_per_second': gpu['evaluations']/gpu['elapsed_seconds'],
              'python_evaluations_per_second': count/seconds,
              'inputs_sha256': {path_key(p): digest(p) for p in sources},
              'scope': 'Finite exact arithmetic parity on manifest-bound partial graphs. Only complete Python parity binds every score to its candidate and cut. Cut passage is not a completion witness or existence proof.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
