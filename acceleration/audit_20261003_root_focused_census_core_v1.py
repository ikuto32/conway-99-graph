"""Independent fixed-input two-line swap scorer using exact integer adjacency masks.

No producer imports. Input decoding/full scalar fixture checks may use the
previous independently written root-focused core, disclosed by the caller.
"""
from itertools import combinations


class CensusError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)


def require(ok, stage, message):
    if not ok:
        raise CensusError(stage, message)


def from_triples(triples, n, degree, root):
    require(all(type(v) is int for v in [n, degree, root])
            and n > 0 and degree > 0 and 0 <= root < n,
            'DOMAIN', 'literal graph domain')
    require(type(triples) is list and len(triples) * 3 == n * degree,
            'DOMAIN', 'complete ordered triangle population')
    bits = [0] * n
    incidence = [0] * n
    for triangle in triples:
        require(type(triangle) is list and len(triangle) == 3
                and all(type(v) is int and 0 <= v < n for v in triangle)
                and len(set(triangle)) == 3, 'DOMAIN', 'three literal distinct points')
        for v in triangle:
            incidence[v] += 1
        for u, v in combinations(triangle, 2):
            require(not (bits[u] >> v & 1), 'DOMAIN', 'linear pair multiplicity')
            bits[u] |= 1 << v
            bits[v] |= 1 << u
    require(incidence == [degree] * n
            and all(row.bit_count() == 2 * degree for row in bits),
            'DOMAIN', 'regular incidence and point degree')
    frozen = [[i, *t] for i, t in enumerate(triples) if root in t]
    mutable = [i for i, t in enumerate(triples) if root not in t]
    require(len(frozen) == degree, 'FROZEN', 'complete literal root triangle population')
    cn = {}
    pair_cost = {}
    el = em = 0
    for u, v in combinations(range(n), 2):
        c = (bits[u] & bits[v]).bit_count()
        cn[u, v] = c
        adjacent = bool(bits[u] >> v & 1)
        cost = (c - (1 if adjacent else 2)) ** 2
        pair_cost[u, v] = (cost if adjacent else 0, cost if not adjacent else 0)
        el += pair_cost[u, v][0]
        em += pair_cost[u, v][1]
    rr = sum(((bits[root] & bits[v]).bit_count() - 2) ** 2
             for v in range(n) if v != root and not (bits[root] >> v & 1))
    return dict(n=n, degree=degree, root=root, triples=[t[:] for t in triples],
                bits=bits, cn=cn, pair_cost=pair_cost, frozen=frozen, mutable=mutable,
                lambda_energy=el, mu_energy=em, root_residual=rr,
                root_energy=60 * el + rr)


def labelled_universe(base):
    """Every mutable pair once, each of its nine ordered position choices."""
    return [(i, j, pi, pj) for i, j in combinations(base['mutable'], 2)
            for pi in range(3) for pj in range(3)]


def evaluate(base, indices):
    require(type(indices) in (list, tuple) and len(indices) == 4
            and all(type(v) is int for v in indices), 'LABEL', 'four literal proposal indices')
    i, j, pi, pj = indices
    require(0 <= i < j < len(base['triples']) and 0 <= pi < 3 and 0 <= pj < 3,
            'LABEL', 'unordered line labels and ordered point positions')
    require(i in base['mutable'] and j in base['mutable'],
            'FROZEN', 'proposal contains only mutable line labels')
    first, second = base['triples'][i], base['triples'][j]
    x, y = first[pi], second[pj]
    changed_first, changed_second = first[:], second[:]
    changed_first[pi], changed_second[pj] = y, x
    exclusive = x not in second and y not in first
    result = dict(indices=list(indices), old_triples=[first[:], second[:]],
                  proposed_triples=[changed_first, changed_second],
                  disjoint=not bool(set(first) & set(second)),
                  selected_points_exclusive=exclusive,
                  new_pairs_absent_after_old_removal=False,
                  admissible=False, invalid_reason='selected_point_not_exclusive')
    if not exclusive:
        return result
    old_pairs = {tuple(sorted(e)) for t in [first, second] for e in combinations(t, 2)}
    new_pairs = {tuple(sorted(e)) for t in [changed_first, changed_second]
                 for e in combinations(t, 2)}
    # In exclusive swaps the two changed lines are individually simple and
    # intersect in at most the original single common point. Check this too.
    require(len(set(changed_first)) == len(set(changed_second)) == 3
            and len(set(changed_first) & set(changed_second)) <= 1,
            'DOMAIN', 'exclusive swap retains internal line simplicity')
    absent = all(not (base['bits'][u] >> v & 1) or (u, v) in old_pairs
                 for u, v in new_pairs)
    result['new_pairs_absent_after_old_removal'] = absent
    if not absent:
        result['invalid_reason'] = 'new_pair_conflict'
        return result
    removed, added = old_pairs - new_pairs, new_pairs - old_pairs
    candidate = base['bits'][:]
    for u, v in removed:
        candidate[u] &= ~(1 << v)
        candidate[v] &= ~(1 << u)
    for u, v in added:
        candidate[u] |= 1 << v
        candidate[v] |= 1 << u
    touched = {v for edge in removed | added for v in edge}
    require(candidate[base['root']] == base['bits'][base['root']],
            'FROZEN', 'literal root adjacency unchanged')
    el, em = base['lambda_energy'], base['mu_energy']
    affected = 0
    for u in sorted(touched):
        for v in range(base['n']):
            if v == u or (v in touched and v < u):
                continue
            key = (min(u, v), max(u, v))
            old_l, old_m = base['pair_cost'][key]
            c = (candidate[u] & candidate[v]).bit_count()
            adjacent = bool(candidate[u] >> v & 1)
            cost = (c - (1 if adjacent else 2)) ** 2
            el += (cost if adjacent else 0) - old_l
            em += (cost if not adjacent else 0) - old_m
            affected += 1
    root = base['root']
    rr = sum(((candidate[root] & candidate[v]).bit_count() - 2) ** 2
             for v in range(base['n']) if v != root and not (candidate[root] >> v & 1))
    require(all(candidate[v].bit_count() == 2 * base['degree'] for v in touched)
            and all(candidate[v] & (1 << v) == 0 for v in touched),
            'DOMAIN', 'exact changed-row degree and no loops')
    result.update(admissible=True, invalid_reason='NONE',
                  lambda_energy=el, mu_energy=em, root_residual=rr,
                  root_energy=60 * el + rr, delta_lambda=el-base['lambda_energy'],
                  delta_mu=em-base['mu_energy'], delta_root=rr-base['root_residual'],
                  delta_F=60*(el-base['lambda_energy'])+rr-base['root_residual'],
                  changed_row_count=len(touched), affected_pair_count=affected,
                  lambda_preserving=el == base['lambda_energy'],
                  strict_root_descent=el == base['lambda_energy'] and rr < base['root_residual'],
                  candidate_bits=candidate)
    return result


def reconstruct_triples(base, evaluated):
    require(evaluated['admissible'] is True, 'DOMAIN', 'only valid candidate reconstructed')
    i, j, _, _ = evaluated['indices']
    candidate = [t[:] for t in base['triples']]
    candidate[i], candidate[j] = [t[:] for t in evaluated['proposed_triples']]
    return candidate


def matrix_bytes(bits):
    n = len(bits)
    return (str(n) + '\n' + ''.join(''.join(str(row >> v & 1) for v in range(n)) + '\n'
                                  for row in bits)).encode('ascii')
