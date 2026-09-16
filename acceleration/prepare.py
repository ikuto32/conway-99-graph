"""Export audited overlap inputs for exact Rust/CUDA evaluators (stdlib only)."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scratch_next_overlap_cut_bank import load_cuts, LABELS, SUPPORTS, PAIRS, EDGES
from audit_certificate import full_graph, audit as audit_certificate

SOURCES = ['scratch_resume_overlap_lift.json'] + [
    f'scratch_next_overlap_alternatives_r{i}.json' for i in range(4)
] + ['scratch_follow_overlap_walk.json']
HISTORICAL_CUT_INPUTS = [ROOT/name for name in (
    'scratch_next_overlap_cut_review.json', 'scratch_next_overlap_semantic_map.json',
    'scratch_next_overlap_farkas.json')] + [
    ROOT/f'scratch_next_overlap_alternatives_r{i}_farkas{suffix}.json'
    for i in range(4) for suffix in ('', '_audit')]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def path_key(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def recorded_path(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def require_recorded_hash(records, path):
    path = Path(path).resolve()
    matches = [value for name, value in records.items() if recorded_path(name) == path]
    require(len(matches) == 1 and matches[0] == digest(path), f'Missing or stale SHA256 for {path}')


def verify_manifest(path, candidates=None):
    path = Path(path)
    manifest = json.loads(path.read_bytes())
    require(manifest.get('status') == 'EXPORTED_PARTIAL_GRAPH_INPUTS', 'Wrong export manifest status')
    require(type(manifest.get('candidates')) is int and manifest['candidates'] > 0,
            'Invalid manifest candidate count')
    require(type(manifest.get('cuts')) is int and manifest['cuts'] > 0, 'Invalid manifest cut count')
    for name, value in manifest['input_sha256'].items():
        require(Path(name).name == name, 'Manifest input names must be basenames')
        require(digest(path.parent/name) == value, f'Input manifest SHA256 mismatch: {name}')
    require('candidates.txt' in manifest['input_sha256'] and 'cuts.txt' in manifest['input_sha256'],
            'Manifest must bind candidate and cut inputs')
    for name, value in manifest['source_sha256'].items():
        require(digest(recorded_path(name)) == value, f'Source manifest SHA256 mismatch: {name}')
    if candidates is not None:
        require(digest(candidates) == manifest['input_sha256']['candidates.txt'],
                'Candidate file is not the manifest candidate input')
    return manifest


def as_paths(value):
    if value is None:
        return []
    if isinstance(value, (str, Path)):
        return [Path(value)]
    return [Path(path) for path in value]


def all_cuts(extra_certificate=None, certificate_audit=None):
    # Historical load_cuts uses assertions as audit gates.
    require(not sys.flags.optimize, 'Run without -O: historical certificate checks use assertions')
    certificates, audits = as_paths(extra_certificate), as_paths(certificate_audit)
    require(len(certificates) == len(audits), 'Each extra certificate requires one matching audit')
    require(len({p.resolve() for p in certificates}) == len(certificates), 'Duplicate extra certificate')
    cuts = load_cuts()
    for certificate_path, audit_path in zip(certificates, audits):
        certificate = json.loads(certificate_path.read_bytes())
        audited = json.loads(audit_path.read_bytes())
        require(audited.get('status') == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'Wrong certificate audit status')
        require_recorded_hash(audited['inputs_sha256'], certificate_path)
        require(certificate.get('status') == 'EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION',
                'Extra certificate does not contain an exact contradiction')
        candidate_path = recorded_path(certificate['candidate_path'])
        require_recorded_hash(audited['inputs_sha256'], candidate_path)
        fresh_audit = audit_certificate(candidate_path, certificate_path)
        require(fresh_audit['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS'
                and fresh_audit['combined_rhs'] == audited['combined_rhs'], 'Independent certificate recheck failed')
        alpha, beta = [[0]*14 for _ in range(84)], [[0]*84 for _ in range(84)]
        seen = set()
        for group in certificate['group_multipliers']:
            kind, coordinate, weight = group['kind'], group['coordinate'], group['multiplier']
            require(type(coordinate) is list and len(coordinate) == 2
                    and all(type(v) is int for v in coordinate), 'Invalid cut coordinate')
            u, v = coordinate
            require(type(weight) is int and (kind, u, v) not in seen, 'Invalid or repeated cut multiplier')
            seen.add((kind, u, v))
            if kind == 'label_quota':
                require(0 <= u < 84 and 0 <= v < 14, 'Invalid label-quota coordinate')
                alpha[u][v] = weight
            else:
                require(kind == 'linear_pair_cap' and 0 <= u < v < 84 and weight >= 0,
                        'Invalid pair-cap coordinate or multiplier')
                beta[u][v] = beta[v][u] = weight
        constant = sum(alpha[u][s]*(1 if s//2 in SUPPORTS[u] else 2)
                       for u in range(84) for s in range(14))
        constant += sum(beta[u][v]*(2-len(set(LABELS[u]) & set(LABELS[v]))) for u, v in PAIRS)
        base = {(u, v): sum(alpha[u][s] for s in LABELS[v])
                         + sum(alpha[v][s] for s in LABELS[u]) + beta[u][v] for u, v in EDGES}
        cuts.append(dict(name=certificate_path.stem, alpha=alpha, beta=beta,
                         constant=constant, base=base, gamma=dict.fromkeys(EDGES, 0)))
    return cuts


def cut_text(cuts):
    lines = [f'C99CUTS1 {len(cuts)}']
    for cut in cuts:
        values = [cut['constant']] + [v for row in cut['alpha'] for v in row] + [v for row in cut['beta'] for v in row]
        lines.append(' '.join(map(str, values)))
    return '\n'.join(lines) + '\n'


def write_candidates(path, candidates):
    require(type(candidates) is list and len(candidates) > 0, 'Expected a nonempty candidate list')
    for edges in candidates:
        full_graph({'overlap_edges_outer_zero_based': edges})
    with path.open('x', encoding='ascii', newline='\n') as stream:
        stream.write(f'C99OVERLAPS1 {len(candidates)}\n')
        for edges in candidates:
            stream.write(' '.join(str(v) for edge in edges for v in edge) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--walk', type=Path, help='Rust walk JSON instead of historical controls')
    parser.add_argument('--walk-audit', type=Path)
    parser.add_argument('--extra-certificate', type=Path, action='append', default=[])
    parser.add_argument('--certificate-audit', type=Path, action='append', default=[])
    args = parser.parse_args()
    require(not args.out.exists(), 'Export directory must be new')
    require(args.walk is not None or args.walk_audit is None, '--walk-audit requires --walk')
    cuts = all_cuts(args.extra_certificate, args.certificate_audit)
    sources = [args.walk] if args.walk else [ROOT/name for name in SOURCES]
    if args.walk:
        candidates = json.loads(args.walk.read_bytes())['overlap_candidates']
        if args.walk_audit:
            audit = json.loads(args.walk_audit.read_bytes())
            require(audit.get('status') == 'INDEPENDENT_RUST_WALK_TRACE_AND_COMPRESSION_AUDIT_PASS',
                    'Wrong walk audit status')
            require_recorded_hash(audit['inputs_sha256'], args.walk)
            sources.append(args.walk_audit)
    else:
        candidates = [json.loads(p.read_bytes())['overlap_edges_outer_zero_based'] for p in sources]
    require(type(candidates) is list and len(candidates) > 0, 'Expected a nonempty candidate list')
    for candidate in candidates:
        full_graph({'overlap_edges_outer_zero_based': candidate})
    args.out.mkdir(parents=True)
    (args.out/'cuts.txt').write_text(cut_text(cuts), encoding='ascii', newline='\n')
    write_candidates(args.out/'candidates.txt', candidates)
    for i, edges in enumerate(candidates):
        if not args.walk or i == 0:
            write_candidates(args.out/f'candidate_{i}.txt', [edges])
    sources += args.extra_certificate + args.certificate_audit + HISTORICAL_CUT_INPUTS
    sources += [Path(__file__), ROOT/'acceleration/audit_certificate.py', ROOT/'scratch_next_overlap_cut_bank.py']
    for certificate in args.extra_certificate:
        sources.append(recorded_path(json.loads(certificate.read_bytes())['candidate_path']))
    manifest = {'status': 'EXPORTED_PARTIAL_GRAPH_INPUTS', 'schema_version': 2,
                'candidates': len(candidates), 'cuts': len(cuts), 'cut_names': [c['name'] for c in cuts],
                'extra_cut_certificates': [{'certificate': path_key(c), 'audit': path_key(a)}
                                           for c, a in zip(args.extra_certificate, args.certificate_audit)],
                'source_sha256': {path_key(p): digest(p) for p in sources},
                'input_sha256': {p.name: digest(p) for p in args.out.glob('*.txt')},
                'scope': 'All candidates pass the independent 99-vertex partial-graph checker. Scores are necessary conditions only.'}
    with (args.out/'manifest.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
