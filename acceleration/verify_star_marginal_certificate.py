"""Replay an integer star-simplex certificate without numerical LP artifacts."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import re
import time

from audit_certificate import full_graph

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    p = Path(str(name).replace('\\', '/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(path):
    return resolve(path).relative_to(ROOT).as_posix()


def digest(path):
    return sha256(resolve(path).read_bytes()).hexdigest()


def integer(value):
    require(type(value) is str and re.fullmatch('-?(0|[1-9][0-9]*)', value) is not None, 'Canonical integer string required')
    return int(value)


def verify(candidate, stars, proof, certificate):
    require(proof['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'], 'Complete independent domain proof missing')
    require(certificate['projection_convention'] == 'X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'
            and certificate['domain_scope'] == 'ALL_ORIGINAL_COMPLETE_DOMAINS', 'Unsupported projection/domain convention')
    adjacency, unknown_full = full_graph(candidate)
    edges = sorted((u-15, v-15) for u, v in unknown_full)
    edge_index = {edge: i for i, edge in enumerate(edges)}
    pairs = list(combinations(range(84), 2)); pair_index = {p: i for i, p in enumerate(pairs)}
    require(stars['complete_domain_enumeration'] and [r['outer_vertex'] for r in stars['domains']] == list(range(84)), 'Incomplete star inventory')
    domain_counts = [len(r['domain_masks_hex']) for r in stars['domains']]
    require(all(domain_counts) and domain_counts == [r['domain_size'] for r in proof['independently_reenumerated_domains']], 'Wrong domain sizes')
    scale = integer(certificate['integer_scale'])
    beta, gamma = [list(map(integer, certificate[name])) for name in ('integer_reciprocity_weights', 'integer_cap_weights')]
    require(scale > 0 and len(beta) == 1680 and len(gamma) == 3486 and
            all(-scale <= w <= scale for w in beta) and all(0 <= w <= scale for w in gamma), 'Dual dimensions/boxes failed')
    # Direct transpose: each disjoint X_uv occurs in its own adjacency cap and
    # in caps joining one endpoint to the other's four fixed outer neighbors.
    coefficient = []
    for u, v in edges:
        weight = gamma[pair_index[u, v]]
        for endpoint, other in ((u, v), (v, u)):
            for w in adjacency[other+15]:
                if w >= 15:
                    require(w-15 != endpoint, 'Unexpected diagonal transpose term')
                    weight += gamma[pair_index[tuple(sorted((endpoint, w-15)))]]
        coefficient.append(weight)
    minima, witness_ids = [], []
    for u, row in enumerate(stars['domains']):
        require(row['status'] == 'COMPLETE', 'Incomplete domain row')
        costs = []
        masks = [int(m, 16) for m in row['domain_masks_hex']]
        require(len(set(masks)) == len(masks), 'Repeated domain mask')
        for mask in masks:
            require(mask >= 0 and not mask >> 84 and mask.bit_count() == 8, 'Bad domain mask')
            selected = [v for v in range(84) if mask >> v & 1]
            require(all(tuple(sorted((u, v))) in edge_index for v in selected), 'Domain outside unknown edge set')
            cost = 0
            for v in selected:
                i = edge_index[tuple(sorted((u, v)))]
                cost += beta[i] if u < v else -beta[i]
                if u < v:
                    cost += coefficient[i]
            costs.append(cost)
        minima.append(min(costs)); witness_ids.append(costs.index(min(costs)))
    rhs = sum((2-int(v+15 in adjacency[u+15])-len(adjacency[u+15] & adjacency[v+15]))*gamma[i]
              for i, (u, v) in enumerate(pairs))
    gap = sum(minima)-rhs
    require(list(map(integer, certificate['integer_vertex_minima'])) == minima, 'Declared domain minima differ')
    require(certificate['minimizing_domain_ids'] == witness_ids, 'Declared minimizing domains differ')
    require(integer(certificate['integer_cap_rhs']) == rhs and integer(certificate['integer_gap']) == gap, 'Declared RHS/gap differs')
    exact = certificate['exact_phase1_lower_bound']
    require(Fraction(integer(exact['numerator']), integer(exact['denominator'])) == Fraction(gap, scale), 'Declared exact bound differs')
    require(certificate['fixed_K_excluded'] == (gap > 0), 'Wrong exclusion flag')
    expected_status = 'EXACT_STAR_MARGINAL_SIMPLEX_DUAL_CONTRADICTION' if gap > 0 else 'EXACT_STAR_MARGINAL_SIMPLEX_DUAL_BOUND'
    require(certificate['status'] == expected_status, 'Wrong certificate status')
    return dict(status='INDEPENDENT_INTEGER_STAR_MARGINAL_CERTIFICATE_REPLAY_PASS', domain_choices_checked=sum(domain_counts),
                cap_transpose_coefficients_checked=1680, cap_rhs_terms_checked=3486, exact_integer_gap=str(gap), integer_scale=str(scale),
                exact_lower_approximate=float(Fraction(gap, scale)), fixed_K_excluded=gap > 0,
                solver_or_marginal_producer_imported=False, no_general_nonexistence_claim=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('candidate', 'domains', 'domain-audit', 'certificate', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Fresh replay report required')
    started, bindings = time.perf_counter(), {}
    def bind(path, expected=None):
        name = key(path)
        if name not in bindings:
            bindings[name] = digest(path)
        require(expected is None or bindings[name] == expected, 'Bound artifact changed: '+name)
        return bindings[name]
    candidate, stars, proof, cert = [json.loads(p.read_bytes()) for p in (args.candidate, args.domains, args.domain_audit, args.certificate)]
    for p in (args.candidate, args.domains, args.domain_audit, args.certificate, Path(__file__), ROOT/'acceleration/audit_certificate.py'):
        bind(p)
    for doc in (proof, cert):
        for p, expected in doc['inputs_sha256'].items():
            bind(p, expected)
    for doc, paths in ((proof, (args.candidate, args.domains)), (cert, (args.candidate, args.domains, args.domain_audit))):
        normalized = {key(p): expected for p, expected in doc['inputs_sha256'].items()}
        require(all(normalized.get(key(p)) == bind(p) for p in paths), 'Certificate/domain proof not input-bound')
    report = verify(candidate, stars, proof, cert)
    report.update(inputs_sha256=bindings, elapsed_seconds=time.perf_counter()-started)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: report[k] for k in ('status', 'domain_choices_checked', 'exact_lower_approximate', 'fixed_K_excluded', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
