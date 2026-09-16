"""Checkpoint a finite list of walk snapshots using exact-audited HiGHS rays."""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

from audit_certificate import audit
from prepare import path_key
from ray_probe import solve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--walk', type=Path, required=True)
    parser.add_argument('--indices', required=True, help='Comma-separated snapshot indices')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if not isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    indices = [int(value) for value in args.indices.split(',')]
    if len(indices) != len(set(indices)) or not indices:
        parser.error('Expected distinct snapshot indices')
    raw = args.walk.read_bytes()
    walk = json.loads(raw)
    candidates = walk['overlap_candidates']
    if any(i < 0 or i >= len(candidates) for i in indices):
        parser.error('Snapshot index out of range')
    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out/'manifest.json'
    manifest = {'walk_path': path_key(args.walk), 'walk_sha256': sha256(raw).hexdigest(),
                'selected_indices': indices, 'seconds': args.seconds,
                'ray_producer_sha256': sha256(Path(__file__).with_name('ray_probe.py').read_bytes()).hexdigest(),
                'scope': 'These stored snapshots only; not a compression/E0/class enumeration.'}
    if manifest_path.exists():
        if json.loads(manifest_path.read_bytes()) != manifest:
            raise ValueError('Resume manifest mismatch')
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    records = []
    started = time.perf_counter()
    for index in indices:
        candidate = args.out/f'candidate_{index}.json'
        certificate = args.out/f'candidate_{index}_ray.json'
        audit_path = args.out/f'candidate_{index}_audit.json'
        data = {'overlap_edges_outer_zero_based': candidates[index], 'walk_path': path_key(args.walk),
                'walk_sha256': manifest['walk_sha256'], 'snapshot_index': index}
        if candidate.exists():
            if json.loads(candidate.read_bytes()) != data:
                raise ValueError('Resume candidate mismatch')
        else:
            candidate.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
        if certificate.exists():
            result = json.loads(certificate.read_bytes())
        else:
            result = solve(candidate, args.seconds)
            certificate.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        report = audit(candidate, certificate)
        if audit_path.exists():
            if json.loads(audit_path.read_bytes()) != report:
                raise ValueError('Resume audit mismatch')
        else:
            audit_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        record = {'index': index, 'producer_status': result['status'], 'audit_status': report['status'],
                  'candidate': path_key(candidate), 'certificate': path_key(certificate),
                  'audit': path_key(audit_path), 'combined_rhs': report.get('combined_rhs'),
                  'elapsed_seconds': result['elapsed_seconds']}
        records.append(record)
        summary = {'status': 'COMPLETE' if len(records) == len(indices) else 'PARTIAL',
                   'manifest': manifest, 'records': records, 'wall_seconds_this_invocation': time.perf_counter()-started}
        temporary = args.out/'summary.tmp'
        temporary.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
        temporary.replace(args.out/'summary.json')
        print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
