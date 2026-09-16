"""Independent exact star-simplex dual bound from full99 sets and domain masks.

No optimization package, producer matrix or producer code is imported.
The integer certificate is sum_u min_{S in D_u} c(u,S) - sum_pair b*y > 0.
Each domain is used only after its prior independent full enumeration audit
and all of that audit's exact input hashes have been verified.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import gcd, isfinite, lcm
from pathlib import Path
import time

from audit_certificate import full_graph

ROOT = Path(__file__).resolve().parents[1]
CONVENTION = 'X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'


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


def rational(q):
    return dict(numerator=str(q.numerator), denominator=str(q.denominator), approximate=float(q))


def checked_vector(values, size):
    require(type(values) is list and len(values) == size and all(type(v) in (float, int) and isfinite(v) for v in values), 'Bad numerical vector')
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--certificate-out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists() and not args.certificate_out.exists(), 'Preserve existing certificate/audit')
    started, bindings = time.perf_counter(), {}
    def bind(path, expected=None):
        name = key(path)
        if name not in bindings:
            bindings[name] = digest(path)
        require(expected is None or bindings[name] == expected, 'Changed bound file: '+name)
        return bindings[name]
    for path in (args.result, Path(__file__), ROOT/'acceleration/audit_certificate.py'):
        bind(path)
    result = json.loads(args.result.read_bytes())
    for path, expected in result['inputs_sha256'].items():
        bind(path, expected)
    require(result['projection_convention'] == CONVENTION and result['original_complete_domains_used'] is True
            and result['pair_pruned_domains_used'] is False, 'Wrong marginal projection or domain scope')
    candidate_path, domains_path, proof_path = [resolve(result[name+'_path']) for name in ('candidate', 'domains', 'domain_audit')]
    for name, path in [('candidate', candidate_path), ('domains', domains_path), ('domain_audit', proof_path)]:
        require(result['inputs_sha256'].get(key(path)) == bind(path, result[name+'_sha256']), 'Unbound model dependency')
    candidate, stars, proof = [json.loads(p.read_bytes()) for p in (candidate_path, domains_path, proof_path)]
    require(proof['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'], 'Domain enumeration proof missing')
    pb = {key(p): d for p, d in proof['inputs_sha256'].items()}
    require(pb.get(key(candidate_path)) == bind(candidate_path) and pb.get(key(domains_path)) == bind(domains_path), 'Domain proof not bound to this K/table')
    for p, expected in pb.items():
        bind(p, expected)
    adjacency, unknown_full = full_graph(candidate)
    unknown = sorted((u-15, v-15) for u, v in unknown_full)
    edge_index = {e: i for i, e in enumerate(unknown)}
    tables = stars['domains']
    require(stars['complete_domain_enumeration'] and [r['outer_vertex'] for r in tables] == list(range(84)), 'Incomplete original domain tables')
    domains = [[frozenset(i for i in range(84) if int(mask, 16) >> i & 1) for mask in row['domain_masks_hex']] for row in tables]
    counts = [len(row) for row in domains]
    require(all(counts) and counts == result['domain_counts'] == [r['domain_size'] for r in proof['independently_reenumerated_domains']], 'Domain dimensions differ')
    offsets = [0]
    for count in counts:
        offsets.append(offsets[-1]+count)
    require(offsets == result['domain_offsets'] and offsets[-1] == result['domain_variables'], 'Domain column order differs')
    for u, table in enumerate(domains):
        require(len(set(table)) == len(table), 'Repeated original domain')
        for selected in table:
            require(len(selected) == 8 and all(tuple(sorted((u, v))) in edge_index for v in selected), 'Invalid full-star mask')
            completed = adjacency[u+15] | {v+15 for v in selected}
            require(all(len(completed & adjacency[s+1]) == (1 if s+1 in adjacency[u+15] else 2) for s in range(14)),
                    'Star does not meet exact root-label quotas')
    pairs = list(combinations(range(84), 2))
    # Rebuild each cap directly by differentiating actual full99 known
    # neighborhoods, not by reading the producer matrix or old row metadata.
    cap_terms, rhs = [], []
    for u, v in pairs:
        terms = []
        if (u, v) in edge_index:
            terms.append(edge_index[u, v])
        for changing, fixed in ((u, v), (v, u)):
            for w in adjacency[fixed+15]:
                e = tuple(sorted((changing, w-15)))
                if e in edge_index:
                    terms.append(edge_index[e])
        require(len(terms) == len(set(terms)), 'Repeated reconstructed cap term')
        cap_terms.append(terms)
        rhs.append(2-int(v+15 in adjacency[u+15])-len(adjacency[u+15] & adjacency[v+15]))
    reciprocal = [min(Fraction(1), max(Fraction(-1), Fraction(v))) for v in checked_vector(result['numeric_reciprocity_duals'], 1680)]
    gamma = [min(Fraction(1), max(Fraction(0), Fraction(v))) for v in checked_vector(result['numeric_cap_duals'], 3486)]
    scale = lcm(*(v.denominator for v in reciprocal+gamma))
    beta_i, gamma_i = [[int(v*scale) for v in vector] for vector in (reciprocal, gamma)]
    divisor = gcd(scale, *(abs(v) for v in beta_i+gamma_i))
    scale //= divisor; beta_i = [v//divisor for v in beta_i]; gamma_i = [v//divisor for v in gamma_i]
    require(all(-scale <= v <= scale for v in beta_i) and all(0 <= v <= scale for v in gamma_i), 'Integer dual boxes differ')
    edge_cost = [0]*1680
    for terms, weight in zip(cap_terms, gamma_i):
        for e in terms:
            edge_cost[e] += weight
    minima, minimizers = [], []
    for u, table in enumerate(domains):
        costs = [sum((beta_i[edge_index[tuple(sorted((u, v)))]] if u < v else -beta_i[edge_index[v, u]])
                     + (edge_cost[edge_index[u, v]] if u < v else 0) for v in selected) for selected in table]
        minimum = min(costs)
        minima.append(minimum); minimizers.append(costs.index(minimum))
    target_cost = sum(b*w for b, w in zip(rhs, gamma_i))
    gap_integer = sum(minima)-target_cost
    lower = Fraction(gap_integer, scale)
    # Independently normalize each stored simplex over exact binary rationals,
    # then evaluate the primal with the same full99-derived constraints.
    probability = list(map(Fraction, checked_vector(result['numeric_probabilities'], offsets[-1])))
    require(all(v >= 0 for v in probability), 'Negative stored probability')
    marginals = [[Fraction(0) for _ in range(84)] for _ in range(84)]
    for u, table in enumerate(domains):
        values = probability[offsets[u]:offsets[u+1]]
        total = sum(values, Fraction(0)); require(total > 0, 'Empty probability simplex')
        for selected, value in zip(table, values):
            for v in selected:
                marginals[u][v] += value/total
    x = [marginals[u][v] for u, v in unknown]
    require(all(0 <= v <= 1 for v in x), 'Marginal outside exact box')
    reciprocity_merit = sum((abs(marginals[u][v]-marginals[v][u]) for u, v in unknown), Fraction(0))
    cap_merit = sum((max(Fraction(0), sum((x[e] for e in terms), Fraction(0))-b) for terms, b in zip(cap_terms, rhs)), Fraction(0))
    upper = reciprocity_merit+cap_merit
    require(lower <= upper and abs(float(upper)-result['numeric_objective']) <= 1e-7*max(1, float(upper)), 'Independent primal mismatch')
    require(abs(float(lower)-result['numeric_simplex_dual_lower']) <= 1e-7*max(1, abs(float(lower))), 'Independent dual mismatch')
    certificate = dict(status='EXACT_STAR_MARGINAL_SIMPLEX_DUAL_CONTRADICTION' if lower > 0 else 'EXACT_STAR_MARGINAL_SIMPLEX_DUAL_BOUND',
                       inputs_sha256=bindings, projection_convention=CONVENTION, domain_scope='ALL_ORIGINAL_COMPLETE_DOMAINS',
                       integer_scale=str(scale), integer_reciprocity_weights=[str(v) for v in beta_i],
                       integer_cap_weights=[str(v) for v in gamma_i], integer_vertex_minima=[str(v) for v in minima],
                       minimizing_domain_ids=minimizers, integer_cap_rhs=str(target_cost), integer_gap=str(gap_integer),
                       exact_phase1_lower_bound=rational(lower), fixed_K_excluded=lower > 0,
                       proof='For simplex probabilities, weighted cost is at least the sum of per-vertex minimum star costs. Reciprocal constraints vanish and cap weights are nonnegative, so positive minimum-minus-RHS contradicts simultaneous feasibility.',
                       no_general_nonexistence_claim=True)
    args.certificate_out.parent.mkdir(parents=True, exist_ok=True)
    with args.certificate_out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(certificate, indent=2, allow_nan=False)+'\n')
    report = dict(status='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS', inputs_sha256=bindings,
                  certificate_path=key(args.certificate_out), certificate_sha256=digest(args.certificate_out),
                  original_complete_domain_choices_checked=offsets[-1], normalizations=84, reciprocity_constraints=1680,
                  full99_linear_caps_reconstructed=3486, coefficient_convention=CONVENTION,
                  exact_primal_upper=rational(upper), exact_dual_lower=rational(lower), exact_gap=rational(upper-lower),
                  positive_exact_dual_excludes_fixed_K=lower > 0, graph_constructed=False, general_nonexistence_proved=False,
                  solver_or_producer_imported=False, domain_completeness_reused_by_exact_hashes=True,
                  elapsed_seconds=time.perf_counter()-started,
                  scope='Fixed K only; original complete local-star domains independently enumerated in the bound prior proof. Exact integer simplex support calculation and full99-derived retained caps certify the new bound.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: report[k] for k in ('status', 'original_complete_domain_choices_checked', 'exact_dual_lower', 'positive_exact_dual_excludes_fixed_K', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
