"""Probe a bounded, deterministic sample of GPU cut survivors with HiGHS."""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
from prepare import digest, path_key, require, require_recorded_hash, verify_manifest
from verify_scores import check_tensor, read_candidates


def checked_inputs(args):
    manifest = verify_manifest(args.manifest)
    candidate_path = args.manifest.parent/'candidates.txt'
    require_recorded_hash(manifest['source_sha256'], args.walk)
    walk = json.loads(args.walk.read_bytes())
    candidates = walk['overlap_candidates']
    exported = read_candidates(candidate_path)
    require(len(candidates) == len(exported) == manifest['candidates'], 'Walk candidate count mismatch')
    require(all(set(map(tuple, candidate)) == reference for candidate, reference in zip(candidates, exported)),
            'Walk snapshots differ from the manifest-bound candidate order')
    require(len(walk['candidate_steps']) == len(candidates), 'Walk step count mismatch')
    walk_audit = json.loads(args.walk_audit.read_bytes())
    require(walk_audit.get('status') == 'INDEPENDENT_RUST_WALK_TRACE_AND_COMPRESSION_AUDIT_PASS',
            'Expected complete fixed-compression walk audit')
    require_recorded_hash(walk_audit['inputs_sha256'], args.walk)
    require(walk_audit['snapshots_verified'] == len(candidates)
            and walk_audit['steps_verified'] == walk['completed_steps']
            and walk_audit['initial_overlap_compression_entries_checked'] == 105,
            'Walk audit scope differs from the provided trace')
    score_audit = json.loads(args.score_audit.read_bytes())
    require(score_audit.get('status') == 'PYTHON_RUST_CUDA_EXACT_SCORE_PARITY_PASS'
            and score_audit.get('python_reference_complete') is True,
            'Probe selection requires complete Python/native parity, not a prefix check')
    for path in [args.scores, args.manifest, candidate_path, args.manifest.parent/'cuts.txt']:
        require_recorded_hash(score_audit['inputs_sha256'], path)
    require(score_audit.get('manifest_sha256') == digest(args.manifest), 'Score audit manifest mismatch')
    total = manifest['candidates']*manifest['cuts']*128
    require(score_audit.get('candidate_count') == manifest['candidates']
            and score_audit.get('cut_count') == manifest['cuts']
            and score_audit.get('sign_masks') == 128
            and score_audit.get('python_reference_scores_checked') == total
            and score_audit.get('rust_cuda_scores_checked') == total,
            'Score audit dimensions or coverage mismatch')
    scores = json.loads(args.scores.read_bytes())['scores']
    check_tensor(scores, manifest['candidates'], manifest['cuts'])
    return walk, scores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--walk', type=Path, required=True)
    parser.add_argument('--scores', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--score-audit', type=Path, required=True)
    parser.add_argument('--walk-audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--count', type=int, default=4)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if args.count < 1:
        parser.error('--count must be positive')
    if not isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    walk, scores = checked_inputs(args)
    args.out.mkdir(parents=True, exist_ok=False)
    candidates = walk['overlap_candidates']
    surviving = [i for i, score in enumerate(scores) if all(v >= 0 for row in score for v in row)]
    # Evenly spaced surviving snapshots; deterministic, no optimality claim.
    count = min(args.count, len(surviving))
    selected = [surviving[(len(surviving)-1)*j//max(1, count-1)] for j in range(count)]
    summary = {'status': 'BOUNDED_OVERLAP_PROBES', 'sampled_candidates': len(candidates),
               'cut_survivors': len(surviving), 'cuts_per_candidate': len(scores[0])*128,
               'selected_indices': selected, 'results': [],
               'input_sha256': {path_key(p): digest(p) for p in
                                [args.walk, args.scores, args.manifest, args.score_audit, args.walk_audit, Path(__file__)]},
               'scope': 'Selected fixed assignments only, not an exhaustive class enumeration or Conway resolution.'}
    for i in selected:
        candidate = args.out / f'candidate_{i}.json'
        certificate = args.out / f'candidate_{i}_highs.json'
        audit = args.out / f'candidate_{i}_audit.json'
        data = {'overlap_edges_outer_zero_based': candidates[i], 'walk_source': str(args.walk),
                'walk_sha256': sha256(args.walk.read_bytes()).hexdigest(), 'snapshot_index': i,
                'walk_step': walk['candidate_steps'][i], 'cut_minima': [min(row) for row in scores[i]],
                'scope': summary['scope']}
        candidate.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
        subprocess.run([sys.executable, '-B', str(ROOT/'acceleration/linear_probe.py'),
                        '--input', str(candidate), '--out', str(certificate), '--seconds', str(args.seconds)],
                       check=True, timeout=2*args.seconds+30)
        result = json.loads(certificate.read_bytes())
        if result['status'] == 'EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION':
            subprocess.run([sys.executable, '-B', str(ROOT/'acceleration/audit_certificate.py'),
                            '--candidate', str(candidate), '--certificate', str(certificate), '--out', str(audit)],
                           check=True, timeout=30)
            audited = json.loads(audit.read_bytes())
            require(audited.get('status') == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'Exact certificate audit did not pass')
            require_recorded_hash(audited['inputs_sha256'], candidate)
            require_recorded_hash(audited['inputs_sha256'], certificate)
        record = {'snapshot_index': i, 'status': result['status'], 'primal_status': result['primal_status'],
                  'certificate_path': str(certificate), 'audit_path': str(audit) if audit.exists() else None,
                  'combined_rhs': result.get('combined_rhs')}
        summary['results'].append(record)
        (args.out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(record), flush=True)
    (args.out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
