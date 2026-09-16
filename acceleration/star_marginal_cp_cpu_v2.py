"""Float64 CPU reference for star-simplex PDHG; numerical diagnostics only.

No solver or star-LP producer is imported. Complete domain tables must be
validated/bound by the caller. The graph and cap matrix come from full99.
"""
from itertools import combinations
import numpy as np
from scipy.sparse import coo_matrix, vstack

from audit_certificate import full_graph, require


def simplex_projection(values):
    """Euclidean projection onto {p >= 0, sum(p) = 1}, for any finite size."""
    z = np.asarray(values, dtype=np.float64)
    require(z.ndim == 1 and z.size > 0 and np.all(np.isfinite(z)), 'Bad simplex vector')
    # Translation invariance avoids cancellation from a large common offset.
    with np.errstate(over='ignore', invalid='ignore'):
        shifted = z - np.max(z)
    require(np.all(np.isfinite(shifted)), 'Simplex differences overflowed')
    # theta is in [-1,0] after max-shifting. Values <= -1 necessarily have
    # projected value zero, so this clamp is exact and bounds the prefix sum.
    shifted = np.maximum(shifted, -1.0)
    ordered = np.sort(shifted)[::-1]
    thresholds = (np.cumsum(ordered) - 1.0) / np.arange(1, z.size + 1)
    active = np.flatnonzero(ordered > thresholds)
    require(active.size > 0, 'Empty simplex support')
    projected = np.maximum(shifted - thresholds[active[-1]], 0.0)
    require(np.all(np.isfinite(projected)), 'Nonfinite simplex projection')
    return projected


def product_simplex_projection(values, offsets):
    result = np.empty_like(values, dtype=np.float64)
    for a, b in zip(offsets[:-1], offsets[1:]):
        result[a:b] = simplex_projection(values[a:b])
    return result


def transfer_probabilities(source_tables, source_p, target_tables):
    """Associate choices only by exact (vertex, mask); normalize retained mass."""
    require(len(source_tables) == len(target_tables) > 0, 'Transfer vertex count')
    source_p = np.asarray(source_p, dtype=np.float64)
    require(source_p.ndim == 1 and len(source_p) == sum(map(len, source_tables)) and
            np.all(np.isfinite(source_p)) and np.all(source_p >= 0), 'Bad source probabilities')
    transferred, metadata = [], []
    offset = 0
    for u, (source, target) in enumerate(zip(source_tables, target_tables)):
        require(len(source) > 0 and len(target) > 0 and len(set(source)) == len(source) and
                len(set(target)) == len(target), 'Transfer domain empty/duplicates')
        values = source_p[offset:offset+len(source)]; offset += len(source)
        require(abs(float(values.sum())-1) < 1e-10, 'Source is not a simplex')
        lookup = dict(zip(source, values))
        weights = np.asarray([lookup.get(mask, 0.0) for mask in target])
        mass = float(weights.sum())
        fallback = mass == 0
        if fallback:
            weights = np.full(len(target), 1.0/len(target))
        else:
            weights /= mass
        transferred.extend(weights)
        metadata.append(dict(outer_vertex=u, source_domains=len(source), target_domains=len(target),
            common_masks=sum(mask in lookup for mask in target), retained_probability_mass=mass,
            uniform_fallback=fallback))
    return np.asarray(transferred), metadata


def build_model(candidate, domain_records):
    adjacency, unknown = full_graph(candidate)
    edges = sorted(unknown)
    require(len(edges) == 1680, 'Unexpected unknown edge count')
    index = {edge: i for i, edge in enumerate(edges)}
    require([r['outer_vertex'] for r in domain_records] == list(range(84)), 'Domain order')
    masks = [[int(s, 16) for s in row['domain_masks_hex']] for row in domain_records]
    counts = np.asarray([len(table) for table in masks], dtype=np.int64)
    require(np.all(counts > 0), 'Empty complete domain is a separate obstruction')
    offsets = np.r_[0, np.cumsum(counts)]
    n = int(offsets[-1])
    rr, cc, vv, pr, pc = [], [], [], [], []
    for u, table in enumerate(masks):
        require(len(set(table)) == len(table), 'Duplicate domain choice')
        for i, mask in enumerate(table):
            require(mask >= 0 and mask.bit_count() == 8 and mask >> 84 == 0, 'Malformed domain mask')
            col = int(offsets[u]) + i
            for v in range(84):
                if mask >> v & 1:
                    edge = tuple(sorted((u + 15, v + 15)))
                    require(edge in index, 'Star uses a fixed or self edge')
                    e = index[edge]
                    rr.append(e); cc.append(col); vv.append(1 if u < v else -1)
                    if u < v:
                        pr.append(e); pc.append(col)
    R = coo_matrix((vv, (rr, cc)), shape=(1680, n), dtype=np.float64).tocsr()
    E = coo_matrix((np.ones(len(pr)), (pr, pc)), shape=(1680, n)).tocsr()
    cr, ce, targets = [], [], []
    for row, (u, v) in enumerate(combinations(range(15, 99), 2)):
        terms = []
        if (u, v) in index:
            terms.append(index[u, v])
        for fixed, changing in ((u, v), (v, u)):
            for neighbor in adjacency[fixed]:
                edge = tuple(sorted((changing, neighbor)))
                if edge in index:
                    terms.append(index[edge])
        targets.append(2 - int(v in adjacency[u]) - len(adjacency[u] & adjacency[v]))
        cr.extend([row] * len(terms)); ce.extend(terms)
    C = coo_matrix((np.ones(len(cr)), (cr, ce)), shape=(3486, 1680)).tocsr()
    require(min(targets) >= 0 and np.all(np.asarray(C.sum(axis=0)).ravel() == 9), 'Cap geometry changed')
    A = vstack((R, C @ E), format='csr')
    AT = A.transpose().tocsr()
    b = np.r_[np.zeros(1680), targets]
    row_sums = np.asarray(abs(A).sum(axis=1)).ravel()
    col_sums = np.asarray(abs(A).sum(axis=0)).ravel()
    require(np.all(col_sums >= 8) and np.max(col_sums) <= 80, 'Star incidence bound failed')
    return dict(A=A, AT=AT, b=b, R=R, RT=R.transpose().tocsr(), E=E,
                ET=E.transpose().tocsr(), C=C, CT=C.transpose().tocsr(),
                offsets=offsets, counts=counts, row_sums=row_sums, col_sums=col_sums)


def diagonal_steps(model, eta=.9):
    """One primal step per simplex, reciprocal absolute-sum dual steps.

    With d_j=max_{k in same vertex} sum_i |A_ik| and r_i=sum_j |A_ij|,
    tau_j=eta/d_j, sigma_i=eta/max(1,r_i). Weighted Cauchy-Schwarz gives
    ||sqrt(Sigma) A sqrt(T)||^2 <= eta^2 < 1. Equal tau within a block
    makes its weighted prox the ordinary Euclidean simplex projection.
    """
    require(0 < eta < 1, 'Step safety factor must be inside (0,1)')
    tau = np.empty(model['A'].shape[1])
    for a, b in zip(model['offsets'][:-1], model['offsets'][1:]):
        tau[a:b] = eta / max(1.0, float(np.max(model['col_sums'][a:b])))
    sigma = eta / np.maximum(1.0, model['row_sums'])
    return tau, sigma


def factored_forward(model, p):
    return np.r_[model['R'] @ p, model['C'] @ (model['E'] @ p)]


def factored_transpose(model, y):
    return model['RT'] @ y[:1680] + model['ET'] @ (model['CT'] @ y[1680:])


def numeric_bounds(model, p, y):
    residual = model['A'] @ p - model['b']
    costs = model['AT'] @ y
    upper = float(np.abs(residual[:1680]).sum() + np.maximum(residual[1680:], 0).sum())
    lower = sum(float(np.min(costs[a:b])) for a, b in zip(model['offsets'][:-1], model['offsets'][1:])) - float(model['b'] @ y)
    return dict(primal_upper_numeric=upper, dual_lower_numeric=lower, numeric_gap=upper-lower)


def step(model, p, pbar, y, tau, sigma):
    lower = np.r_[np.full(1680, -1.0), np.zeros(3486)]
    ynew = np.clip(y + sigma * (model['A'] @ pbar - model['b']), lower, 1.0)
    pnew = product_simplex_projection(p - tau * (model['AT'] @ ynew), model['offsets'])
    return pnew, 2 * pnew - p, ynew
