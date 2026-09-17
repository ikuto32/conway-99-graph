"""Bounded new-domain pilot with one unfixed same-sign matching coordinate.

Results are candidate engineering evidence, never an exact family exclusion.
Frozen complete-K builders and domain files are not imported or modified.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json"
OLD_DOMAINS = "acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json"
OBJECTIVE = "PARTIAL_K_STAR_RECIPROCITY_CAP_PHASE1_V1"


class Cap(Exception):
    pass


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def edge(a, b):
    return min(a, b), max(a, b)


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask -= bit


def add(rows, a, b):
    rows[a] |= 1 << b
    rows[b] |= 1 << a


def valid(rows):
    return all(r.bit_count() <= 14 for r in rows) and all((rows[a] & rows[b]).bit_count() <= 2-int(bool(rows[a] >> b & 1)) for a, b in combinations(range(99), 2))


def build(candidate):
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in (0, 1) for t in (0, 1)]
    supports = [{s//2 for s in pair} for pair in labels]
    affected = [u for u, pair in enumerate(labels) if 0 in pair]
    allowed_Y = {edge(u, v) for u, v in combinations(affected, 2) if len(supports[u] & supports[v]) == 1}
    all_K = {tuple(e) for e in candidate["overlap_edges_outer_zero_based"]}
    removed = all_K & allowed_Y
    assert len(affected) == 12 and len(allowed_Y) == 60 and len(removed) == 6
    assert Counter(u for e in removed for u in e) == Counter({u: 1 for u in affected})
    fixed_K = all_K-removed
    rows = [0]*99
    for r in range(1, 15):
        add(rows, 0, r)
    for r in range(1, 15, 2):
        add(rows, r, r+1)
    for u, pair in enumerate(labels, 15):
        for s in pair:
            add(rows, u, s+1)
    for u, v in fixed_K:
        add(rows, u+15, v+15)
    disjoint = {edge(u, v) for u, v in combinations(range(84), 2) if not supports[u] & supports[v]}
    unknown = sorted(disjoint | allowed_Y)
    assert len(unknown) == 1740 and len(fixed_K) == 162 and valid(rows)
    assert [rows[u+15].bit_count() for u in range(84)] == [5 if u in affected else 6 for u in range(84)]
    return labels, rows, unknown, affected, sorted(removed), sorted(fixed_K), sorted(allowed_Y)


def enumerate_star(rows, labels, unknown, outer, budget, restricted=None):
    center = outer+15
    count_needed = 14-rows[center].bit_count()
    candidates = sorted(v if u == outer else u for u, v in unknown if outer in (u, v))
    if restricted is not None:
        candidates = [v for v in candidates if v in restricted]
    # Single-edge validity uses full partial graph mutation (all pair caps).
    legal = []
    for v in candidates:
        trial = rows[:]
        add(trial, center, v+15)
        if valid(trial):
            legal.append(v)
    candidates = legal
    n = len(candidates)
    demands = [2-int(bool(rows[center] >> (s+1) & 1))-(rows[center] & rows[s+1]).bit_count() for s in range(14)]
    assert sum(demands) == 2*count_needed and min(demands) >= 0
    caps = [2-int(bool(rows[center] >> w & 1))-(rows[center] & rows[w]).bit_count() if w != center else 99 for w in range(99)]
    by_label = [sum(1 << i for i, v in enumerate(candidates) if s in labels[v]) for s in range(14)]
    resource_rows = [list(members(rows[v+15] | (1 << (v+15)))) for v in candidates]
    by_resource = [sum(1 << i for i, rr in enumerate(resource_rows) if w in rr) for w in range(99)]
    conflicts = []
    for i, v in enumerate(candidates):
        conflicts.append(sum(1 << j for j, w in enumerate(candidates) if i != j and
                             (rows[v+15] & rows[w+15]).bit_count() >= 2-int(bool(rows[v+15] >> (w+15) & 1))))
    masks = []
    local_nodes = 0
    def visit(available, chosen, remaining, capacity):
        nonlocal local_nodes
        local_nodes += 1
        budget["nodes"] += 1
        if budget["nodes"] > budget["node_cap"]:
            raise Cap("GLOBAL_NODE_CAP")
        if local_nodes % 128 == 0 and time.monotonic() >= budget["deadline"]:
            raise Cap("TIME_CAP")
        if not any(remaining):
            assert chosen.bit_count() == count_needed
            if len(masks) >= budget["domain_cap"]:
                raise Cap("PER_VERTEX_DOMAIN_CAP")
            masks.append(chosen)
            return
        choices = []
        for s, need in enumerate(remaining):
            number = (available & by_label[s]).bit_count()
            if number < need:
                return
            if need:
                choices.append((number-need, number, s))
        _, _, symbol = min(choices)
        options = available & by_label[symbol]
        first = options & -options
        i = first.bit_length()-1
        rest = available ^ first
        v = candidates[i]
        if all(remaining[s] > 0 for s in labels[v]) and all(capacity[w] > 0 for w in resource_rows[i]):
            next_remaining = remaining[:]
            next_capacity = capacity[:]
            next_available = rest & ~conflicts[i]
            for s in labels[v]:
                next_remaining[s] -= 1
                if next_remaining[s] == 0:
                    next_available &= ~by_label[s]
            for w in resource_rows[i]:
                next_capacity[w] -= 1
                if next_capacity[w] == 0:
                    next_available &= ~by_resource[w]
            visit(next_available, chosen | (1 << v), next_remaining, next_capacity)
        visit(rest, chosen, remaining, capacity)
    available = (1 << n)-1
    for s in range(14):
        if demands[s] == 0:
            available &= ~by_label[s]
    for w in range(99):
        if caps[w] == 0:
            available &= ~by_resource[w]
    visit(available, 0, demands, caps)
    assert len(masks) == len(set(masks))
    return sorted(masks), local_nodes, candidates


def direct_subset_ok(rows, labels, outer, selected):
    center = outer+15
    trial = rows[:]
    for v in selected:
        add(trial, center, v+15)
    return trial[center].bit_count() == 14 and valid(trial) and all(
        (trial[center] & trial[s+1]).bit_count() == 2-int(bool(trial[center] >> (s+1) & 1)) for s in range(14))


def numerical_lp(rows, unknown, tables, seconds, out):
    import highspy
    import numpy as np
    from scipy.sparse import coo_matrix, hstack, vstack
    edge_index = {pair: i for i, pair in enumerate(unknown)}
    offsets = np.cumsum([0]+[len(t) for t in tables]).tolist()
    n, m = offsets[-1], len(unknown)
    rr, cc, vv, er, ec, nr = [], [], [], [], [], []
    for u, table in enumerate(tables):
        nr.extend([u]*len(table))
        for i, mask in enumerate(table):
            for v in members(mask):
                eid = edge_index[edge(u, v)]
                rr.append(eid); cc.append(offsets[u]+i); vv.append(1 if u < v else -1)
                if u < v:
                    er.append(eid); ec.append(offsets[u]+i)
    R = coo_matrix((vv, (rr, cc)), shape=(m, n)).tocsr()
    P = coo_matrix((np.ones(len(er)), (er, ec)), shape=(m, n)).tocsr()
    N = coo_matrix((np.ones(n), (nr, range(n))), shape=(84, n)).tocsr()
    cap_rows, cap_cols, cap_values, rhs, exact_caps = [], [], [], [], []
    for k, (a, b) in enumerate(combinations(range(84), 2)):
        coefficients = defaultdict(int)
        if (a, b) in edge_index:
            coefficients[edge_index[a, b]] += 1
        for u, opposite in ((a, b), (b, a)):
            for w in members(rows[opposite+15]):
                if w >= 15 and w-15 != u and edge(u, w-15) in edge_index:
                    coefficients[edge_index[edge(u, w-15)]] += 1
        bound = 2-int(bool(rows[a+15] >> (b+15) & 1))-(rows[a+15] & rows[b+15]).bit_count()
        for c, value in sorted(coefficients.items()):
            cap_rows.append(k); cap_cols.append(c); cap_values.append(value)
        rhs.append(bound)
        exact_caps.append(dict(pair=[a, b], rhs=bound, terms=sorted(coefficients.items())))
    L = coo_matrix((cap_values, (cap_rows, cap_cols)), shape=(3486, m)).tocsr()
    A = vstack((N, R, L @ P), format="csr")
    eq = 84+m
    slack = coo_matrix((np.r_[-np.ones(m+3486), np.ones(m)],
                        (np.r_[np.arange(84, eq), np.arange(eq, eq+3486), np.arange(84, eq)], np.arange(2*m+3486))),
                       shape=(eq+3486, 2*m+3486)).tocsr()
    augmented = hstack((A, slack), format="csr")
    model = highspy.HighsLp()
    model.num_row_, model.num_col_ = augmented.shape
    model.col_cost_ = np.r_[np.zeros(n), np.ones(2*m+3486)]
    model.col_lower_ = np.zeros(model.num_col_); model.col_upper_ = np.full(model.num_col_, highspy.kHighsInf)
    model.row_lower_ = np.r_[np.ones(84), np.zeros(m), np.full(3486, -highspy.kHighsInf)]
    model.row_upper_ = np.r_[np.ones(84), np.zeros(m), rhs]
    model.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    model.a_matrix_.start_, model.a_matrix_.index_, model.a_matrix_.value_ = augmented.indptr, augmented.indices, augmented.data
    solver = highspy.Highs()
    for name, value in (("output_flag", False), ("threads", 1), ("solver", "ipm"), ("run_crossover", "off"), ("time_limit", max(1.0, seconds))):
        assert solver.setOptionValue(name, value) == highspy.HighsStatus.kOk
    assert solver.passModel(model) == highspy.HighsStatus.kOk
    save(out / "linear_caps.json", dict(objective=OBJECTIVE, variable_edges=unknown, caps=exact_caps,
                                         note="Necessary offdiagonal B²+B+BE+EB+E caps; nonnegativeE² omitted; new partialB"))
    started = time.monotonic()
    run_status = solver.run()
    solution, info = solver.getSolution(), solver.getInfo()
    result = dict(status="NUMERICAL_DIAGNOSTIC_ONLY", objective=OBJECTIVE,
                  definition="Minimize sum absolute1740edge reciprocity residuals plus3486positive linear-cap residuals over84hard local-star simplices",
                  domain_scope="New one-freed-coordinate local domains; not historical complete-K domains", direction="minimize",
                  highs_version=solver.version(), solver="ipm", crossover="off", threads=1,
                  run_status=str(run_status), model_status=str(solver.getModelStatus()),
                  objective_value=info.objective_function_value, domain_variables=n, reciprocity_rows=m,
                  linear_caps=3486, matrix_nonzeros=augmented.nnz, row_count=model.num_row_, column_count=model.num_col_,
                  solve_seconds=time.monotonic()-started, time_limit_seconds=seconds,
                  numeric_probabilities=list(solution.col_value[:n]) if solution.value_valid else None,
                  numeric_row_duals=list(solution.row_dual) if solution.dual_valid else None,
                  exact_certificate_generated=False, independent_completeness_verified=False,
                  family_exclusion_claimed=False, target_resolution=False)
    save(out / "numeric_lp.json", result)
    return {k: v for k, v in result.items() if k not in ("numeric_probabilities", "numeric_row_duals")}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seconds", type=float, default=240)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert not (args.out / "manifest.json").exists(), "Fresh evidence directory required"
    candidate = json.loads((ROOT / CANDIDATE).read_bytes())
    old = json.loads((ROOT / OLD_DOMAINS).read_bytes())
    labels, rows, unknown, affected, removed, fixed_K, allowed_Y = build(candidate)
    bindings = {CANDIDATE: digest(ROOT / CANDIDATE), OLD_DOMAINS: digest(ROOT / OLD_DOMAINS),
                "acceleration/theory_20260917_partial_matching.py": digest(__file__), "uv.lock": digest(ROOT / "uv.lock")}
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(), inputs_sha256=bindings,
                    question="Can generalized local domains and a new partialBstar-simplex relaxation expose a whole same-sign coordinate obstruction?",
                    selection="First sorted same_0 coordinate at root_group0 of baseline18481; no outcome-based choice",
                    root_group=0, matching_class="same_0", removed_edges_outer=removed, remaining_fixed_K_edges_outer=fixed_K,
                    freed_legal_matching_edges_outer=allowed_Y, affected_outer_vertices=affected,
                    scope="Remaining162Kedges fixed, including13other same-sign and7cross matchings; all same-fibre and unlisted other-coordinate absences fixed. Only60freed matching edges+1680disjoint edges unknown.",
                    model=OBJECTIVE, missing_neighbors="9at12affected centers;8at72others",
                    acceptance="Exact complete per-center enumeration flags only if no cap; no family proof from partial tables or floating objective",
                    enumeration_limits=dict(global_seconds=min(160, args.seconds*.7), global_nodes=3000000, per_vertex_domains=20000, total_domains=200000),
                    overall_wall_limit_seconds=args.seconds, numerical_acceptance="Diagnostic only; no threshold produces a proof",
                    controls="Two preselected actual-center restricted universes checked by independent brute subsets and directfull99mutation; every historical baseline domain embedded in completed new domains",
                    LP_gate="All84nonempty domains complete and enough remaining time; otherwise skip explicitly",
                    objective_comparison="Different feasible domain; not comparable as a historical star-merit improvement", independent_review=False)
    save(args.out / "manifest.json", manifest)
    started = time.monotonic()
    budget = dict(deadline=started+min(160, args.seconds*.7), nodes=0, node_cap=3000000, domain_cap=20000)
    controls = []
    for outer in (affected[0], next(u for u in range(84) if u not in affected)):
        selected = set(members(int(old["domains"][outer]["domain_masks_hex"][0], 16)))
        if outer in affected:
            selected |= {v if u == outer else u for u, v in removed if outer in (u, v)}
        pool = selected | set(v if u == outer else u for u, v in unknown if outer in (u, v))
        pool = selected | set(sorted(pool-selected)[:2])
        actual, nodes, _ = enumerate_star(rows, labels, unknown, outer, budget, restricted=pool)
        q = 14-rows[outer+15].bit_count()
        expected = sorted(sum(1 << v for v in subset) for subset in combinations(sorted(pool), q) if direct_subset_ok(rows, labels, outer, subset))
        assert actual == expected and actual, "Restricted brute-force calibration mismatch"
        corrupt = actual[0] ^ (1 << next(members(actual[0])))
        assert not direct_subset_ok(rows, labels, outer, list(members(corrupt)))
        controls.append(dict(outer_vertex=outer, pool=sorted(pool), size=q, brute_subsets=len(list(combinations(pool, q))),
                             accepted_masks=[hex(m) for m in actual], corrupted_missing_edge="REJECT", outcome="PASS"))
    save(args.out / "controls.json", controls)
    tables, records, incomplete = [], [], None
    total = 0
    for outer in tqdm(range(84), desc="New partialKlocal domains", unit="center"):
        try:
            masks, nodes, candidates = enumerate_star(rows, labels, unknown, outer, budget)
        except Cap as error:
            incomplete = dict(outer_vertex=outer, reason=str(error))
            break
        expected_old = []
        for text in old["domains"][outer]["domain_masks_hex"]:
            mask = int(text, 16)
            if outer in affected:
                for u, v in removed:
                    if outer in (u, v):
                        mask |= 1 << (v if u == outer else u)
            expected_old.append(mask)
        assert set(expected_old) <= set(masks), "Historical-domain embedding control failed"
        total += len(masks)
        record = dict(outer_vertex=outer, status="CANDIDATE_COMPLETE_NEW_PARTIAL_K_DOMAIN", missing_neighbor_count=14-rows[outer+15].bit_count(),
                      allowed_single_neighbors=candidates, domain_masks_hex=[hex(m) for m in masks],
                      domain_size=len(masks), search_nodes=nodes, historical_embedded_choices=len(expected_old),
                      family_matching_choice_count_check=all(sum((edge(outer, v) in set(allowed_Y)) for v in members(m)) == (1 if outer in affected else 0) for m in masks))
        assert record["family_matching_choice_count_check"]
        save(args.out / f"domain_{outer:02d}.json", record)
        tables.append(masks); records.append({k: v for k, v in record.items() if k != "domain_masks_hex"})
        if total >= 200000:
            incomplete = dict(outer_vertex=outer, reason="TOTAL_DOMAIN_CAP")
            break
    lp = None
    if len(tables) == 84 and all(tables) and incomplete is None and args.seconds-(time.monotonic()-started) > 10:
        lp = numerical_lp(rows, unknown, tables, min(60, args.seconds-(time.monotonic()-started)-3), args.out)
    summary = dict(timestamp=datetime.now(timezone.utc).isoformat(), status="CANDIDATE_PARTIAL_MATCHING_PILOT_FINISHED",
                   manifest_sha256=digest(args.out / "manifest.json"), objective=OBJECTIVE,
                   completed_centers=len(tables), new_domain_choices=total, domains=records, incomplete=incomplete,
                   independently_complete=False, LP_result=lp,
                   LP_skipped_reason=None if lp else "Incomplete/empty domains or insufficient remaining bound; no incomplete-table LP permitted",
                   search_nodes=budget["nodes"], elapsed_seconds=time.monotonic()-started,
                   output_sha256={path.name: digest(path) for path in args.out.glob("*.json")},
                   family_exclusion_claimed=False, target_resolution=False)
    assert all(digest(ROOT / name) == expected for name, expected in bindings.items())
    save(args.out / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("completed_centers", "new_domain_choices", "incomplete", "search_nodes", "elapsed_seconds", "LP_skipped_reason")}))
    if lp:
        print(json.dumps(lp))


if __name__ == "__main__":
    main()
