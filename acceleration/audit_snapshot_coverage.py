"""Independently verify exact certificates cover every saved walk snapshot.

Imports no optimizer or certificate producer. Coverage means only the explicit
stored snapshots, never all walk states, compressions, or E0 assignments.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import audit, full_graph, require

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def resolve(record):
    path = Path(record.replace('\\', '/'))
    return path if path.is_absolute() else ROOT/path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--walk', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, action='append', default=[])
    parser.add_argument('--certificate-dir', type=Path, action='append', default=[])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve existing audit')
    started = time.perf_counter()
    walk = json.loads(args.walk.read_bytes())
    snapshots = walk['overlap_candidates']
    keys = []
    for candidate in snapshots:
        full_graph({'overlap_edges_outer_zero_based': candidate})
        keys.append(tuple(sorted(map(tuple, candidate))))
    require(len(keys) == len(set(keys)), 'Expected distinct stored snapshots')
    index_of = {key: i for i, key in enumerate(keys)}
    paths = args.certificate[:]
    for directory in args.certificate_dir:
        paths += sorted(directory.glob('*_ray.json')) + sorted(directory.glob('*_highs.json'))
    require(len(paths) == len({p.resolve() for p in paths}), 'Duplicate certificate path')
    coverage = {}
    for certificate_path in paths:
        certificate = json.loads(certificate_path.read_bytes())
        candidate_path = resolve(certificate['candidate_path'])
        candidate = json.loads(candidate_path.read_bytes())
        key = tuple(sorted(map(tuple, candidate['overlap_edges_outer_zero_based'])))
        require(key in index_of, 'Certificate is outside the saved snapshot set')
        index = index_of[key]
        require(index not in coverage, f'Duplicate coverage for snapshot {index}')
        checked = audit(candidate_path, certificate_path)
        require(checked['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'No exact exclusion')
        coverage[index] = {'snapshot_index': index, 'candidate_path': candidate_path.relative_to(ROOT).as_posix(),
                           'candidate_sha256': digest(candidate_path),
                           'certificate_path': certificate_path.resolve().relative_to(ROOT).as_posix(),
                           'certificate_sha256': digest(certificate_path), 'combined_rhs': checked['combined_rhs']}
    require(set(coverage) == set(range(len(snapshots))), 'Incomplete snapshot coverage')
    result = {'status': 'INDEPENDENT_STORED_SNAPSHOT_CERTIFICATE_COVERAGE_PASS',
              'walk_path': args.walk.resolve().relative_to(ROOT).as_posix(), 'walk_sha256': digest(args.walk),
              'auditor_sha256': digest(Path(__file__)),
              'certificate_auditor_sha256': digest(Path(__file__).with_name('audit_certificate.py')),
              'snapshots': len(snapshots), 'exact_exclusions': len(coverage),
              'certificates': [coverage[i] for i in sorted(coverage)],
              'partial_pair_checks': 4851*len(snapshots), 'unknown_coefficients_checked': 1680*len(snapshots),
              'elapsed_seconds': time.perf_counter()-started,
              'scope': 'Only the listed stored snapshots have no continuous disjoint-edge completion. No coverage of unsaved intermediate states, all compressions, all E0 configurations, or the Conway problem.'}
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'certificates'}))


if __name__ == '__main__':
    main()
