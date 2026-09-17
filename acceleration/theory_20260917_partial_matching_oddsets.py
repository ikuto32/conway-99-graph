"""Exact saved-point odd-set diagnostic, optionally a separate strengthened LP."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
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
PRIMARY = "acceleration/results/20260917_partial_matching"
MODEL = "PARTIAL_K_STAR_RECIPROCITY_CAP_WITH_ALL_ODDSETS_V2"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path, value, compact=False):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=None if compact else 2)
        f.write("\n")


def exact(value):
    value = Fraction(value)
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def odd_masks():
    return [mask for mask in range(1 << 12) if mask.bit_count() % 2]


def subset_value(mask, edge_values, position):
    return sum((value for (a, b), value in edge_values.items() if mask >> position[a] & 1 and mask >> position[b] & 1), Fraction(0))


def controls():
    position = {u: u for u in range(12)}
    matching = {(2*i, 2*i+1): Fraction(1) for i in range(6)}
    assert all(subset_value(mask, matching, position) <= (mask.bit_count()-1)//2 for mask in odd_masks())
    fractional = {(0, 1): Fraction(1, 2), (1, 2): Fraction(1, 2), (0, 2): Fraction(1, 2),
                  (3, 4): Fraction(1, 2), (4, 5): Fraction(1, 2), (3, 5): Fraction(1, 2),
                  (6, 7): Fraction(1), (8, 9): Fraction(1), (10, 11): Fraction(1)}
    assert all(sum(value for e, value in fractional.items() if u in e) == 1 for u in range(12))
    violation = subset_value(7, fractional, position)-1
    opposite = ((1 << 12)-1)^7
    assert violation == Fraction(1, 2) == subset_value(opposite, fractional, position)-4
    assert len(odd_masks()) == 2048 and sum(mask < (((1 << 12)-1)^mask) for mask in odd_masks()) == 1024
    return [dict(name="exact_perfect_matching_all2048oddsets", outcome="PASS"),
            dict(name="degree1_fractional_two_odd_cycles", outcome="REJECT_ODDSET", violation=exact(violation)),
            dict(name="complement_equivalence_with_exact_degrees", outcome="PASS"),
            dict(name="2048subsets_1024complement_pairs", outcome="PASS")]


def strengthened_lp(tables, cap_data, affected, odd, seconds, out):
    import highspy
    import numpy as np
    from scipy.sparse import coo_matrix, hstack, vstack
    unknown = [tuple(e) for e in cap_data["variable_edges"]]
    index = {e: i for i, e in enumerate(unknown)}
    offsets = np.cumsum([0]+[len(t) for t in tables]).tolist()
    n, m = offsets[-1], len(unknown)
    rr, cc, vv, er, ec, nr = [], [], [], [], [], []
    for u, table in enumerate(tables):
        nr.extend([u]*len(table))
        for i, mask in enumerate(table):
            for v in range(84):
                if mask >> v & 1:
                    eid = index[min(u, v), max(u, v)]
                    rr.append(eid); cc.append(offsets[u]+i); vv.append(1 if u < v else -1)
                    if u < v:
                        er.append(eid); ec.append(offsets[u]+i)
    R = coo_matrix((vv, (rr, cc)), shape=(m, n)).tocsr()
    P = coo_matrix((np.ones(len(er)), (er, ec)), shape=(m, n)).tocsr()
    N = coo_matrix((np.ones(n), (nr, range(n))), shape=(84, n)).tocsr()
    lr, lc, lv = [], [], []
    for k, row in enumerate(cap_data["caps"]):
        for e, value in row["terms"]:
            lr.append(k); lc.append(e); lv.append(value)
    L = coo_matrix((lv, (lr, lc)), shape=(3486, m)).tocsr()
    orows, ocols = [], []
    affected_set = set(affected)
    for k, mask in enumerate(odd):
        chosen = {affected[i] for i in range(12) if mask >> i & 1}
        for e, (a, b) in enumerate(unknown):
            if a in affected_set and b in affected_set and a in chosen and b in chosen:
                orows.append(k); ocols.append(e)
    O = coo_matrix((np.ones(len(orows)), (orows, ocols)), shape=(2048, m)).tocsr()
    A = vstack((N, R, L @ P, O @ P), format="csr")
    eq, cap_end = 84+m, 84+m+3486
    slack = coo_matrix((np.r_[-np.ones(m+3486), np.ones(m)],
                       (np.r_[np.arange(84, eq), np.arange(eq, cap_end), np.arange(84, eq)], np.arange(2*m+3486))),
                      shape=(cap_end+2048, 2*m+3486)).tocsr()
    augmented = hstack((A, slack), format="csr")
    model = highspy.HighsLp()
    model.num_row_, model.num_col_ = augmented.shape
    model.col_cost_ = np.r_[np.zeros(n), np.ones(2*m+3486)]
    model.col_lower_ = np.zeros(model.num_col_); model.col_upper_ = np.full(model.num_col_, highspy.kHighsInf)
    model.row_lower_ = np.r_[np.ones(84), np.zeros(m), np.full(3486+2048, -highspy.kHighsInf)]
    model.row_upper_ = np.r_[np.ones(84), np.zeros(m), [r["rhs"] for r in cap_data["caps"]], [(mask.bit_count()-1)//2 for mask in odd]]
    model.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    model.a_matrix_.start_, model.a_matrix_.index_, model.a_matrix_.value_ = augmented.indptr, augmented.indices, augmented.data
    solver = highspy.Highs()
    for name, value in (("output_flag", False), ("threads", 1), ("solver", "ipm"), ("run_crossover", "off"), ("time_limit", seconds)):
        assert solver.setOptionValue(name, value) == highspy.HighsStatus.kOk
    assert solver.passModel(model) == highspy.HighsStatus.kOk
    save(out / "strengthened_model.json", dict(model=MODEL, unknown_edges=unknown, odd_subsets_masks=odd,
        odd_subset_outer_vertex_order=affected, odd_rhs=[(s.bit_count()-1)//2 for s in odd], hard_odd_rows=2048,
        domain_scope="Same54,478new partialKstars; all2048odd-set rows hard; no relaxation/slack on oddrows",
        probability_offsets=offsets, cap_source=PRIMARY+"/linear_caps.json", objective_slacks="Only1740reciprocity absolute residuals and3486linear-cap positive residuals"))
    started = time.monotonic()
    run_status = solver.run()
    solution, info = solver.getSolution(), solver.getInfo()
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), status="NUMERICAL_STRENGTHENED_DIAGNOSTIC_ONLY", model=MODEL,
        highs_version=solver.version(), solver="ipm", crossover="off", threads=1, time_limit_seconds=seconds,
        run_status=str(run_status), model_status=str(solver.getModelStatus()), objective_value=info.objective_function_value,
        rows=model.num_row_, columns=model.num_col_, nonzeros=augmented.nnz,
        numeric_probabilities=list(solution.col_value[:n]) if solution.value_valid else None,
        numeric_row_duals=list(solution.row_dual) if solution.dual_valid else None,
        solve_seconds=time.monotonic()-started, exact_certificate_generated=False,
        independently_complete_domains=False, independent_model_audit=False, family_exclusion_claimed=False, target_resolution=False)
    save(out / "strengthened_numeric_lp.json", result)
    return {k: v for k, v in result.items() if k not in ("numeric_probabilities", "numeric_row_duals")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert not (args.out / "manifest.json").exists(), "Choose fresh output directory"
    bindings = {}
    def read(name):
        bindings[name] = digest(ROOT / name)
        return json.loads((ROOT / name).read_bytes())
    primary = read(PRIMARY+"/manifest.json")
    summary = read(PRIMARY+"/summary.json")
    numeric = read(PRIMARY+"/numeric_lp.json")
    caps = read(PRIMARY+"/linear_caps.json")
    assert summary["completed_centers"] == 84 and summary["incomplete"] is None
    assert summary["manifest_sha256"] == bindings[PRIMARY+"/manifest.json"]
    tables = []
    for u in range(84):
        name = f"domain_{u:02d}.json"
        record = read(PRIMARY+"/"+name)
        assert bindings[PRIMARY+"/"+name] == summary["output_sha256"][name]
        tables.append([int(s, 16) for s in record["domain_masks_hex"]])
    affected = primary["affected_outer_vertices"]
    Y = [tuple(e) for e in primary["freed_legal_matching_edges_outer"]]
    assert len(affected) == 12 and len(Y) == 60
    bindings["acceleration/theory_20260917_partial_matching_oddsets.py"] = digest(__file__)
    bindings["uv.lock"] = digest(ROOT / "uv.lock")
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
        command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
        question="Does the saved primary partialKnumeric point violate matching-polytope odd-set inequalities?",
        frozen_universe="All2048odd subsets of12named freed-coordinate vertices, sizes1,3,5,7,9,11;1024complement pairs recorded separately",
        exact_arithmetic="Interpret every storedbinaryfloat via Fraction.from_float, then divide by its exact per-center sum. Normalized rationals need not be dyadic.",
        negative_value_policy="Abort rather than clip any negative probability or zero normalization sum",
        projection="Smaller outer endpoint's normalized local marginal, matching primary convention",
        complement_policy="Evaluate both members; equivalent only with exact projected degree1. Record exact complement-gap/degree-defect identity.",
        violation_threshold="Strictly positive exact rational excess, with no tolerance; diagnostics of a saved numerical point, not a family proof",
        strengthening_trigger="If at least one strict exact violation, run separate V2LP with ALL2048hardoddrows, unchanged54,478domain choices and60sHiGHS cap; otherwise no LP",
        strengthened_model=MODEL, inputs_sha256=bindings, independent_review=False, family_exclusion_claimed=False, target_resolution=False)
    save(args.out / "manifest.json", manifest)
    started = time.monotonic()
    control_records = controls()
    p = numeric["numeric_probabilities"]
    assert len(p) == sum(map(len, tables))
    normalized, normalizations, offset = [], [], 0
    for u, table in enumerate(tables):
        values = [Fraction.from_float(value) for value in p[offset:offset+len(table)]]
        offset += len(table)
        total = sum(values, Fraction(0))
        assert total > 0 and all(v >= 0 for v in values), "Invalid saved simplex values: no clipping allowed"
        normalized.append([v/total for v in values])
        normalizations.append(dict(outer_vertex=u, exact_binary_input_sum=exact(total), deviation_from1=exact(total-1)))
    marginals, reciprocal = {}, []
    for u, v in Y:
        small = sum((prob for mask, prob in zip(tables[u], normalized[u]) if mask >> v & 1), Fraction(0))
        large = sum((prob for mask, prob in zip(tables[v], normalized[v]) if mask >> u & 1), Fraction(0))
        marginals[u, v] = small
        reciprocal.append(dict(edge=[u, v], smaller_endpoint=exact(small), larger_endpoint=exact(large), exact_difference=exact(small-large)))
    degree = {u: sum((value for e, value in marginals.items() if u in e), Fraction(0)) for u in affected}
    for u in affected:
        own = sum((prob*sum(tuple(sorted((u, v))) in set(Y) for v in range(84) if mask >> v & 1)
                   for mask, prob in zip(tables[u], normalized[u])), Fraction(0))
        assert own == 1
    position = {u: i for i, u in enumerate(affected)}
    odd = odd_masks()
    excess = {}
    rows = []
    for mask in tqdm(odd, desc="Exact saved-point odd subsets", unit="subset"):
        total = subset_value(mask, marginals, position)
        bound = (mask.bit_count()-1)//2
        excess[mask] = total-bound
        rows.append(dict(mask=mask, outer_vertices=[affected[i] for i in range(12) if mask >> i & 1], size=mask.bit_count(),
                         exact_internal_weight=exact(total), bound=bound, exact_excess=exact(total-bound), violated=total > bound))
    pairs = []
    for mask in odd:
        complement = ((1 << 12)-1)^mask
        if mask >= complement:
            continue
        identity = sum(((degree[u]-1) if mask >> position[u] & 1 else -(degree[u]-1) for u in affected), Fraction(0))/2
        assert excess[mask]-excess[complement] == identity
        pairs.append(dict(masks=[mask, complement], violated_members=[s for s in (mask, complement) if excess[s] > 0],
                          exact_excess_difference=exact(identity), exact_equivalence_at_saved_projection=identity == 0))
    violations = [row for row in rows if row["violated"]]
    diagnostic = dict(timestamp=datetime.now(timezone.utc).isoformat(), status="EXACT_RATIONAL_SAVED_NUMERIC_POINT_DIAGNOSTIC",
        manifest_sha256=digest(args.out / "manifest.json"), controls=control_records,
        affected_outer_vertices=affected, per_center_normalizations=normalizations, matching_edge_marginals=reciprocal,
        projected_degrees=[dict(outer_vertex=u, degree=exact(degree[u]), defect=exact(degree[u]-1)) for u in affected],
        projected_degrees_exactly1=all(value == 1 for value in degree.values()),
        all_matching_reciprocities_exact=sum(abs(Fraction(r["exact_difference"]["numerator"])/Fraction(r["exact_difference"]["denominator"])) for r in reciprocal) == 0,
        odd_subset_count=2048, violated_subsets=len(violations),
        maximum_excess=exact(max(excess.values())), maximum_excess_mask=max(excess, key=excess.get),
        complement_pair_count=1024, complement_pairs_with_a_violation=sum(bool(pair["violated_members"]) for pair in pairs),
        odd_subsets=rows, complement_pairs=pairs,
        meaning="Exact evaluation of rationally normalized saved floating-point coordinates only; not proof about the family or an exact solution of primaryLP",
        elapsed_seconds=time.monotonic()-started, family_exclusion_claimed=False, target_resolution=False)
    save(args.out / "oddset_diagnostic.json", diagnostic, compact=True)
    lp = strengthened_lp(tables, caps, affected, odd, 60, args.out) if violations else None
    assert all(digest(ROOT / name) == expected for name, expected in bindings.items()), "Inputs changed"
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), status="CANDIDATE_ODDSET_DIAGNOSTIC_FINISHED",
        odd_subsets=2048, violated_subsets=len(violations), complement_pairs=1024,
        complement_pairs_with_a_violation=diagnostic["complement_pairs_with_a_violation"], maximum_excess=diagnostic["maximum_excess"],
        projected_degrees_exactly1=diagnostic["projected_degrees_exactly1"], strengthened_LP=lp,
        strengthening_skipped_reason=None if lp else "No strict positive rational odd-set violation in the saved normalized point",
        output_sha256={f.name: digest(f) for f in args.out.glob("*.json")}, elapsed_seconds=time.monotonic()-started,
        independent_domain_model_review=False, family_exclusion_claimed=False, target_resolution=False)
    save(args.out / "summary.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
