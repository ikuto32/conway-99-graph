"""HiGHS continuous completion and exact integer dual reconstruction.

Every result applies to one complete overlap assignment only. A numerical
infeasibility flag is never promoted to a proof. No old artifact is modified.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import gcd, isfinite
from functools import reduce
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack, vstack, eye
from audit_certificate import full_graph


def constraints(known):
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2)
              for s in range(2) for t in range(2)]
    supports = [{x//2 for x in row} for row in labels]
    rows = [set() for _ in labels]
    for u, v in known:
        rows[u].add(v)
        rows[v].add(u)
    edges = [e for e in combinations(range(84), 2) if not supports[e[0]] & supports[e[1]]]
    index = {e: i for i, e in enumerate(edges)}
    groups = []
    for u in range(84):
        for s in range(14):
            terms = [index[tuple(sorted((u, v)))] for v in range(84)
                     if s in labels[v] and tuple(sorted((u, v))) in index]
            target = (1 if s//2 in supports[u] else 2) - sum(s in labels[v] for v in rows[u])
            if terms:
                groups.append(dict(kind='label_quota', coordinate=[u, s], terms=terms, target=target, equality=True))
            else:
                assert target == 0
    neq = len(groups)
    for u, v in combinations(range(84), 2):
        terms = [index[u, v]] if (u, v) in index else []
        for a, b in [(u, v), (v, u)]:
            terms += [index[tuple(sorted((b, w)))] for w in rows[a] if tuple(sorted((b, w))) in index]
        assert len(terms) == len(set(terms))
        target = 2 - len(set(labels[u]) & set(labels[v])) - ((u, v) in known) - len(rows[u] & rows[v])
        assert target >= 0
        if terms:
            groups.append(dict(kind='linear_pair_cap', coordinate=[u, v], terms=terms, target=target, equality=False))
    rr, cc = [], []
    for i, g in enumerate(groups):
        rr.extend([i]*len(g['terms']))
        cc.extend(g['terms'])
    matrix = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(len(groups), len(edges))).tocsr()
    target = np.array([g['target'] for g in groups], dtype=float)
    return edges, groups, neq, matrix, target


def reconstruct(groups, edges, values):
    for scale in [1000, 1000000, 1000000000]:
        weights = [int(round(v*scale)) for v in values]
        co = [0]*len(edges)
        rhs = 0
        for weight, group in zip(weights, groups):
            if not group['equality'] and weight < 0:
                break
            rhs += weight*group['target']
            for e in group['terms']:
                co[e] += weight
        else:
            bounds = [max(0, -v) for v in co]
            rhs += sum(bounds)
            if rhs < 0:
                divisor = reduce(gcd, [abs(v) for v in weights + bounds if v])
                return dict(status='EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION', combined_rhs=rhs//divisor,
                    group_multipliers=[dict(kind=g['kind'], coordinate=g['coordinate'], multiplier=w//divisor)
                                       for g, w in zip(groups, weights) if w],
                    edge_upper_bound_multipliers=[dict(edge=list(e), multiplier=w//divisor)
                                                 for e, w in zip(edges, bounds) if w],
                    reconstruction_scale=scale)
    return {'status': 'NO_EXACT_CERTIFICATE'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if not isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    if args.out.exists():
        raise FileExistsError(args.out)
    input_bytes = args.input.read_bytes()
    data = json.loads(input_bytes)
    full_graph(data)  # Validate before converting to a set, which would hide duplicates.
    known = set(map(tuple, data['overlap_edges_outer_zero_based']))
    started = time.perf_counter()
    edges, groups, neq, a, b = constraints(known)
    options = {'time_limit': args.seconds}
    primal = linprog(np.zeros(len(edges)), A_eq=a[:neq], b_eq=b[:neq],
                     A_ub=a[neq:], b_ub=b[neq:], bounds=(0, 1), method='highs', options=options)
    input_path, repository = args.input.resolve(), Path(__file__).resolve().parents[1]
    portable_input = input_path.relative_to(repository).as_posix() if input_path.is_relative_to(repository) else input_path.as_posix()
    result = {'candidate_path': portable_input, 'candidate_sha256': sha256(input_bytes).hexdigest(),
              'producer_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'scipy_version': scipy.__version__, 'primal_status': primal.status, 'primal_message': primal.message,
              'linear_variables': len(edges), 'linear_constraints': len(groups), 'time_limit_per_solve_seconds': args.seconds,
              'status': 'NUMERICAL_RESULT_ONLY', 'disjoint_block_totals_assumed': False,
              'scope': 'One complete E0=0 overlap assignment; no global exclusion, adjacency witness or exhaustive coverage.'}
    print(json.dumps(result), flush=True)
    if primal.status == 0:
        result['numeric_edge_values'] = primal.x.tolist()
    # Nonnegative positive/negative equality weights, nonnegative cap and box weights.
    # Minimize combined RHS subject to nonnegative variable coefficients and L1<=1.
    if primal.status == 2:
        co = hstack([a.T, -a[:neq].T, eye(len(edges))], format='csr')
        objective = np.concatenate([b, -b[:neq], np.ones(len(edges))])
        norm = coo_matrix(np.ones((1, len(objective)))).tocsr()
        dual = linprog(objective, A_ub=vstack([-co, norm], format='csr'),
                       b_ub=np.concatenate([np.zeros(len(edges)), [1.0]]), bounds=(0, None),
                       method='highs', options=options)
        result.update(dual_status=dual.status, dual_message=dual.message)
        if dual.status == 0:
            values = dual.x[:len(groups)].copy()
            values[:neq] -= dual.x[len(groups):len(groups)+neq]
            result['numeric_dual_objective'] = dual.fun
            result.update(reconstruct(groups, edges, values))
    result['elapsed_seconds'] = time.perf_counter()-started
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('numeric_edge_values', 'group_multipliers', 'edge_upper_bound_multipliers')}))


if __name__ == '__main__':
    main()
