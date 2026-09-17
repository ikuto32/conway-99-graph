"""Full co-neighbor moments on frozen one-coordinate partial-K star domains."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import highspy
import numpy as np
import scipy
from scipy.sparse import coo_matrix, hstack, vstack, eye, save_npz
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "acceleration/results/20260917_partial_matching"
MODEL = "PARTIAL_K_FULL_CENTER_STAR_MOMENT_PHASE1_V1"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def members(mask):
    return [i for i in range(mask.bit_length()) if mask >> i & 1]


def build(supports, fixed, unknown, tables, mu=2, lam=1, progress=False):
    size = len(tables)
    pairs = list(combinations(range(size), 2))
    pair_id = {e: i for i, e in enumerate(pairs)}
    edge_id = {e: i for i, e in enumerate(unknown)}
    fixed_neighbors = [set() for _ in tables]
    for a, b in fixed:
        fixed_neighbors[a].add(b)
        fixed_neighbors[b].add(a)
    offsets = np.cumsum([0]+[len(t) for t in tables]).tolist()
    rr, rc, rv, mr, mc, mv = [], [], [], [], [], []
    for u in tqdm(range(size), desc="Build exact center-star columns", disable=not progress):
        for j, mask in enumerate(tables[u], offsets[u]):
            selected = set(members(mask))
            assert u not in selected and not selected & fixed_neighbors[u]
            for v in selected:
                e = (min(u, v), max(u, v))
                rr.append(edge_id[e]); rc.append(j); rv.append(1 if u < v else -1)
                if u < v:
                    mr.append(pair_id[e]); mc.append(j); mv.append(mu-lam)
            for e in combinations(sorted(selected | fixed_neighbors[u]), 2):
                mr.append(pair_id[e]); mc.append(j); mv.append(1)
    n = offsets[-1]
    R = coo_matrix((np.array(rv, dtype=np.int64), (rr, rc)), shape=(len(unknown), n)).tocsr()
    M = coo_matrix((np.array(mv, dtype=np.int64), (mr, mc)), shape=(len(pairs), n)).tocsr()
    N = coo_matrix((np.ones(n, dtype=np.int64), (np.repeat(np.arange(size), np.diff(offsets)), np.arange(n))), shape=(size, n)).tocsr()
    rhs = np.array([mu-len(supports[a] & supports[b])-(mu-lam)*int((a, b) in fixed) for a, b in pairs], dtype=np.int64)
    return N, R, M, rhs, offsets, pairs


def controls():
    A = np.array([[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)], dtype=np.int64)
    assert np.array_equal(A@A, 2*np.eye(9, dtype=np.int64)-A+2*np.ones((9, 9), dtype=np.int64))
    receipts = []
    for root in range(9):
        inner = set(np.flatnonzero(A[root]).tolist())
        outer = [i for i in range(9) if i != root and i not in inner]
        supports = [inner & set(np.flatnonzero(A[u]).tolist()) for u in outer]
        actual = {e for e in combinations(range(4), 2) if A[outer[e[0]], outer[e[1]]]}
        for fixed in (set(), {min(actual)}):
            unknown = sorted(set(combinations(range(4), 2))-fixed)
            tables = [[sum(1 << v for v in range(4) if (min(u,v), max(u,v)) in actual-fixed)] for u in range(4)]
            N, R, M, rhs, _, pairs = build(supports, fixed, unknown, tables)
            witness = np.ones(4, dtype=np.int64)
            assert np.array_equal(N@witness, np.ones(4, dtype=np.int64))
            assert not np.any(R@witness) and np.array_equal(M@witness, rhs)
            bad = M.copy(); bad.data[0] += 1
            assert not np.array_equal(bad@witness, rhs)
            bad_rhs = rhs.copy(); bad_rhs[0] += 1
            assert not np.array_equal(M@witness, bad_rhs)
            receipts.append(dict(root=root, outer=outer, fixed_edges=sorted(fixed), unknown_edges=unknown,
                supports=[sorted(s) for s in supports], masks=[t[0] for t in tables], pairs=pairs,
                exact_moment_matrix=M.toarray().tolist(), rhs=rhs.tolist(), positive="PASS",
                corrupted_coefficient="REJECTED", corrupted_rhs="REJECTED"))
    return dict(parameters=[9,4,1,2], adjacency=A.tolist(), records=receipts,
                positive_cases=18, corrupted_coefficient_cases=18, corrupted_rhs_cases=18,
                limitation="Exact witness calibration, not independent model verification or target existence")


def exact_bound(R, M, rhs, offsets, dual):
    # For any |y|<=1 and any reciprocity multiplier q:
    # L1(Mz-b) >= y*b - sum_u max_j ((M^T y+R^T q)_uj).
    scale = 1 << 20
    q = np.rint(np.array(dual[len(offsets)-1:len(offsets)-1+R.shape[0]])*scale)
    y = np.rint(np.clip(np.array(dual[len(offsets)-1+R.shape[0]:]), -1, 1)*scale)
    assert np.all(np.isfinite(q)) and np.all(np.isfinite(y))
    bound_max = (int(np.max(np.abs(q), initial=0))*int(abs(R).sum(axis=0).max())+
                 scale*int(abs(M).sum(axis=0).max()))
    assert bound_max < 2**62, "Use arbitrary precision instead of risking int64 overflow"
    q, y = q.astype(np.int64), y.astype(np.int64)
    column = M.T@y+R.T@q
    maxima = [int(max(column[a:b])) for a,b in zip(offsets, offsets[1:])]
    numerator = sum(int(a)*int(b) for a,b in zip(y, rhs))-sum(maxima)
    return dict(status="CANDIDATE_EXACT_SUPPORT_BOUND", denominator=scale, numerator=numerator,
        approximate=numerator/scale, moment_weight_numerators=y.tolist(), reciprocity_weight_numerators=q.tolist(),
        center_maxima_numerators=maxima, arithmetic="Integer sparse products guarded against overflow; Python integer final sum",
        independent_check_pending=True, strictly_positive=numerator > 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert not any(args.out.iterdir()), "Fresh output directory required"
    bindings = {}
    def read(path):
        bindings[path] = digest(ROOT/path)
        return json.loads((ROOT/path).read_bytes())
    primary = read(PRIMARY+"/manifest.json")
    summary = read(PRIMARY+"/summary.json")
    caps = read(PRIMARY+"/linear_caps.json")
    review = read("acceleration/results/20260917_independent_review/partial_matching/summary.json")
    assert summary["completed_centers"] == 84 and summary["incomplete"] is None
    tables = []
    for u in range(84):
        name = f"domain_{u:02d}.json"
        record = read(PRIMARY+"/"+name)
        assert bindings[PRIMARY+"/"+name] == summary["output_sha256"][name]
        tables.append([int(s,16) for s in record["domain_masks_hex"]])
    fixed = {tuple(e) for e in primary["remaining_fixed_K_edges_outer"]}
    unknown = [tuple(e) for e in caps["variable_edges"]]
    supports = [{2*a+s, 2*b+t} for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
    assert len(fixed)==162 and len(unknown)==1740 and sum(map(len,tables))==54478
    bindings[Path(__file__).relative_to(ROOT).as_posix()] = digest(__file__)
    bindings["uv.lock"] = digest(ROOT/"uv.lock")
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip(),
        command_argv=[sys.executable,*sys.argv], working_directory=str(Path.cwd()),
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, highs=highspy.Highs().version(),
        model=MODEL, inputs_sha256=bindings, selection="Frozen first same_0 root-group0 partial-K domains, no outcome selection",
        scope=primary["scope"], equation="For each outer pair v<w: sum_(t,S) 1[{v,w} subset fixed_outer_neighbors(t) union S] z_tS + x_vw = 2 - |support(v) intersect support(w)| - B_vw. x is zero for prescribed zeros/fixed edges; otherwise smaller-endpoint local marginal.",
        feasible_domain="84 nonnegative hard star simplices and 1740 hard reciprocity equations; moment equalities carry L1 phase-I residual slacks",
        objective="Minimize sum over 3486 outer pairs of absolute full co-neighbor equality residual. New model, no comparison to primary cap objective.",
        controls="Rook9 with own (9,4,1,2) parameters, all9roots and2fixed-edge choices; exact positive witness and separate coefficient/RHS corruptions",
        preregistered_solver=dict(solver="ipm", threads=1, crossover="off", time_limit_seconds=60),
        acceptance="No numerical threshold is a proof. Diagnostic near-zero label at abs(objective)<=1e-7 only when primal valid; exact rounded-dual support lower bound strictly >0 is a candidate conditional exclusion pending independent model and arithmetic checks.",
        preservation="Save full integer CSR augmented model plus bounds/cost and raw solver vectors; no frozen input mutation",
        target_resolution=False, independent_model_review=False)
    save(args.out/"manifest.json", manifest)
    started = time.monotonic()
    save(args.out/"controls.json", controls())
    N,R,M,rhs,offsets,pairs = build(supports, fixed, unknown, tables, progress=True)
    assert all(len(members(mask))+sum(u in e for e in fixed)==12 for u,t in enumerate(tables) for mask in t)
    A = vstack((N,R,M), format="csr", dtype=np.int64)
    slack = vstack((coo_matrix((84+1740,6972), dtype=np.int64), hstack((-eye(3486,dtype=np.int64),eye(3486,dtype=np.int64)),format="csr")),format="csr")
    augmented = hstack((A,slack),format="csr",dtype=np.int64)
    n = offsets[-1]
    b = np.r_[np.ones(84,dtype=np.int64),np.zeros(1740,dtype=np.int64),rhs]
    costs = np.r_[np.zeros(n,dtype=np.int64),np.ones(6972,dtype=np.int64)]
    save_npz(args.out/"integer_augmented_csr.npz",augmented,compressed=True)
    save(args.out/"model.json",dict(model=MODEL,shape=list(augmented.shape),nonzeros=augmented.nnz,
        matrix_sha256=digest(args.out/"integer_augmented_csr.npz"),row_order="84 simplex,1740 reciprocity,3486 moments",
        column_order="54478 probabilities by center/mask original order,3486 negative slacks,3486 positive slacks",
        probability_offsets=offsets,unknown_edges=unknown,pair_order=pairs, rhs=b.tolist(),costs=costs.tolist(),
        column_lower=0,column_upper=None,column_upper_null_reason="Positive infinity for every column",all_rows_equalities=True))
    lp = highspy.HighsLp(); lp.num_row_,lp.num_col_ = augmented.shape
    lp.col_cost_=costs.astype(float); lp.col_lower_=np.zeros(lp.num_col_); lp.col_upper_=np.full(lp.num_col_,highspy.kHighsInf)
    lp.row_lower_=b.astype(float); lp.row_upper_=b.astype(float)
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=augmented.indptr; lp.a_matrix_.index_=augmented.indices; lp.a_matrix_.value_=augmented.data.astype(float)
    solver=highspy.Highs()
    for key,val in (("output_flag",True),("threads",1),("solver","ipm"),("run_crossover","off"),("time_limit",60.0),("log_file",str(args.out/"highs.log"))):
        assert solver.setOptionValue(key,val)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    begin=time.monotonic(); status=solver.run(); elapsed=time.monotonic()-begin
    solution,info=solver.getSolution(),solver.getInfo()
    raw=dict(timestamp=datetime.now(timezone.utc).isoformat(),run_status=str(status),model_status=str(solver.getModelStatus()),
        value_valid=solution.value_valid,dual_valid=solution.dual_valid,raw_info_objective=info.objective_function_value,
        objective_usable=bool(solution.value_valid),solve_seconds=elapsed,
        col_value=list(solution.col_value),col_dual=list(solution.col_dual),row_value=list(solution.row_value),row_dual=list(solution.row_dual),
        invalid_vector_policy="Raw arrays preserved even if invalid flags are false; they are not feasible points or certificates")
    save(args.out/"numeric_lp.json",raw)
    bound=exact_bound(R,M,rhs,offsets,solution.row_dual) if solution.dual_valid else None
    save(args.out/"exact_support_bound.json",dict(bound=bound,null_reason=None if bound else "Solver supplied no valid dual vector; no bound attempted"))
    assert all(digest(ROOT/name)==value for name,value in bindings.items()),"Frozen input changed"
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_NUMERICAL_MOMENT_PILOT",model=MODEL,
        domains=84,choices=n,reciprocity_rows=1740,moment_rows=3486,shape=list(augmented.shape),nonzeros=augmented.nnz,
        run_status=str(status),model_status=raw["model_status"],value_valid=solution.value_valid,dual_valid=solution.dual_valid,
        objective=info.objective_function_value if solution.value_valid else None,
        objective_null_reason=None if solution.value_valid else "No valid primal; raw solver objective unusable",
        near_zero_diagnostic=bool(solution.value_valid and abs(info.objective_function_value)<=1e-7),
        support_bound=None if bound is None else {k:bound[k] for k in ("numerator","denominator","approximate","strictly_positive")},
        solve_seconds=elapsed,elapsed_seconds=time.monotonic()-started,
        output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},
        independent_model_review=False,family_exclusion_claimed=False,target_resolution=False)
    save(args.out/"summary.json",result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
