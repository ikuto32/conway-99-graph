"""Numerical star-simplex phase I with reciprocity and the existing linear caps.

For u<v, x_uv is the marginal from u's domain, explicitly choosing the
smaller outer index. Reciprocal equality makes both endpoint marginals agree.
No numerical solver status or objective is treated as a certificate.
"""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

import highspy
import numpy as np
from scipy.sparse import coo_matrix, hstack, vstack

from audit_phase1 import graph_rows

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--domains', type=Path, required=True)
    parser.add_argument('--domain-audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    require(not args.out.exists() and isfinite(args.seconds) and args.seconds > 0, 'Fresh output/positive finite limit required')
    started = time.perf_counter()
    bindings = {}
    def bind(path, expected=None):
        name = key(path)
        if name not in bindings:
            bindings[name] = digest(path)
        require(expected is None or expected == bindings[name], 'Changed input: '+name)
        return bindings[name]
    for p in (args.candidate, args.domains, args.domain_audit, Path(__file__), ROOT/'acceleration/audit_phase1.py', ROOT/'acceleration/audit_certificate.py'):
        bind(p)
    audit = json.loads(args.domain_audit.read_bytes())
    require(audit['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and audit['complete_used_domains_verified'], 'Independent full domains required')
    audit_bindings = {key(n): d for n, d in audit['inputs_sha256'].items()}
    require(all(audit_bindings.get(key(p)) == bind(p) for p in (args.candidate, args.domains)), 'Domain audit not bound to inputs')
    for p, expected in audit_bindings.items():
        bind(p, expected)
    candidate, domains = [json.loads(p.read_bytes()) for p in (args.candidate, args.domains)]
    require(domains['complete_domain_enumeration'], 'Incomplete domains')
    records = domains['domains']
    require([r['outer_vertex'] for r in records] == list(range(84)) and all(r['status'] == 'COMPLETE' for r in records), 'Incomplete vertex table')
    require([r['domain_size'] for r in audit['independently_reenumerated_domains']] == [len(r['domain_masks_hex']) for r in records], 'Audit size mismatch')
    edges, rows, omitted = graph_rows(candidate)
    caps = rows[840:]
    index = {e: i for i, e in enumerate(edges)}
    masks = [[int(m, 16) for m in r['domain_masks_hex']] for r in records]
    require(all(masks), 'An empty independently complete domain is already a direct obstruction')
    offsets = np.cumsum([0]+[len(r) for r in masks]).tolist()
    n = offsets[-1]
    rr, cc, vv, er, ec = [], [], [], [], []
    normal_rows = []
    for u, table in enumerate(masks):
        normal_rows.extend([u]*len(table))
        for i, mask in enumerate(table):
            column = offsets[u]+i
            require(mask.bit_count() == 8 and not mask >> 84, 'Invalid star mask')
            for v in range(84):
                if mask >> v & 1:
                    pair = tuple(sorted((u, v)))
                    require(pair in index, 'Star extends outside disjoint edge domain')
                    edge = index[pair]
                    rr.append(edge); cc.append(column); vv.append(1 if u < v else -1)
                    if u < v:
                        er.append(edge); ec.append(column)
    reciprocity = coo_matrix((vv, (rr, cc)), shape=(1680, n)).tocsr()
    projection = coo_matrix((np.ones(len(er)), (er, ec)), shape=(1680, n)).tocsr()
    normalization = coo_matrix((np.ones(n), (normal_rows, range(n))), shape=(84, n)).tocsr()
    cr, ce = [], []
    for i, row in enumerate(caps):
        cr.extend([i]*len(row['terms'])); ce.extend(row['terms'])
    edge_caps = coo_matrix((np.ones(len(cr)), (cr, ce)), shape=(3486, 1680)).tocsr()
    marginal_caps = (edge_caps @ projection).tocsr()
    matrix = vstack((normalization, reciprocity, marginal_caps), format='csr')
    target = np.r_[np.ones(84), np.zeros(1680), [r['target'] for r in caps]]
    neq, nrow = 84+1680, 84+1680+3486
    # Hard simplexes have no violation slacks. All other rows get an excess
    # slack; reciprocal equalities also get a shortage slack.
    penalized = 1680+3486
    sr = np.r_[np.arange(84, nrow), np.arange(84, neq)]
    sc = np.arange(penalized+1680)
    sv = np.r_[-np.ones(penalized), np.ones(1680)]
    slack = coo_matrix((sv, (sr, sc)), shape=(nrow, penalized+1680)).tocsr()
    augmented = hstack((matrix, slack), format='csr')
    lp = highspy.HighsLp()
    lp.num_row_, lp.num_col_ = nrow, augmented.shape[1]
    lp.col_cost_ = np.r_[np.zeros(n), np.ones(penalized+1680)]
    lp.col_lower_ = np.zeros(augmented.shape[1]); lp.col_upper_ = np.full(augmented.shape[1], highspy.kHighsInf)
    lp.row_lower_ = np.r_[target[:neq], np.full(nrow-neq, -highspy.kHighsInf)]; lp.row_upper_ = target
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = augmented.indptr, augmented.indices, augmented.data
    solver = highspy.Highs()
    for name, value in [('output_flag', False), ('time_limit', args.seconds), ('threads', 1), ('solver', 'ipm'), ('run_crossover', 'off')]:
        require(solver.setOptionValue(name, value) == highspy.HighsStatus.kOk, 'Solver option failed')
    require(solver.passModel(lp) == highspy.HighsStatus.kOk, 'Solver model load failed')
    built = time.perf_counter()
    run_status = solver.run()
    solution, info, model_status = solver.getSolution(), solver.getInfo(), solver.getModelStatus()
    result = dict(status='STAR_MARGINAL_NUMERICAL_NO_INCUMBENT', inputs_sha256=bindings,
                  candidate_path=key(args.candidate), candidate_sha256=bind(args.candidate), domains_path=key(args.domains),
                  domains_sha256=bind(args.domains), domain_audit_path=key(args.domain_audit), domain_audit_sha256=bind(args.domain_audit),
                  projection_convention=CONVENTION, original_complete_domains_used=True, pair_pruned_domains_used=False,
                  domain_counts=[len(r) for r in masks], domain_offsets=offsets, domain_variables=n, rows=nrow,
                  hard_normalizations=84, reciprocity_equalities=1680, retained_linear_caps=3486, augmented_columns=augmented.shape[1],
                  matrix_nonzeros=matrix.nnz, augmented_nonzeros=augmented.nnz,
                  highs_version=solver.version(), model_status=str(model_status), run_status=str(run_status),
                  numerical_optimal=model_status == highspy.HighsModelStatus.kOptimal, time_limit_seconds=args.seconds,
                  build_seconds=built-started, solve_seconds=time.perf_counter()-built,
                  numerical_values_are_proofs=False, graph_constructed=False, general_nonexistence_proved=False)
    if solution.value_valid and len(solution.col_value) == augmented.shape[1]:
        p = np.asarray(solution.col_value[:n])
        require(np.all(np.isfinite(p)), 'Nonfinite simplex incumbent')
        p = np.maximum(p, 0)
        for u in range(84):
            section = slice(offsets[u], offsets[u+1]); total = np.sum(p[section])
            require(total > 0, 'Numerical empty simplex'); p[section] /= total
        residual = matrix @ p-target
        result.update(status='STAR_MARGINAL_NUMERICAL_INCUMBENT', numeric_probabilities=p.tolist(),
                      numeric_objective=float(np.abs(residual[84:neq]).sum()+np.maximum(0, residual[neq:]).sum()),
                      numeric_solver_objective=float(info.objective_function_value),
                      numeric_reciprocity_violation=float(np.abs(residual[84:neq]).sum()),
                      numeric_cap_violation=float(np.maximum(0, residual[neq:]).sum()),
                      numeric_projected_edge_values=(projection @ p).tolist())
    if solution.dual_valid:
        dual = -np.asarray(solution.row_dual[84:])
        require(len(dual) == penalized and np.all(np.isfinite(dual)), 'Bad dual vector')
        dual[:1680] = np.clip(dual[:1680], -1, 1); dual[1680:] = np.clip(dual[1680:], 0, 1)
        coefficients = reciprocity.T @ dual[:1680]+marginal_caps.T @ dual[1680:]
        lower = sum(float(np.min(coefficients[offsets[u]:offsets[u+1]])) for u in range(84))-float(target[neq:] @ dual[1680:])
        result.update(numeric_reciprocity_duals=dual[:1680].tolist(), numeric_cap_duals=dual[1680:].tolist(),
                      numeric_simplex_dual_lower=lower)
    require(all(digest(p) == expected for p, expected in bindings.items()), 'Bound input changed')
    result.update(elapsed_seconds=time.perf_counter()-started,
                  scope='One fixed K: simplex distributions on complete local stars, exact-edge reciprocity and original linear pair caps. Numerical phase-I merit guides only; exact dual auditing is separate.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, separators=(',', ':'), allow_nan=False)+'\n')
    print(json.dumps({k: result.get(k) for k in ('status', 'domain_variables', 'matrix_nonzeros', 'numeric_objective', 'numeric_simplex_dual_lower', 'solve_seconds')}))


if __name__ == '__main__':
    main()
