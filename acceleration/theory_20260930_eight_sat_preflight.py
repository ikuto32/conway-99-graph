"""No-solver size preflight for exact full99 completion of the eight-coordinate family."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "acceleration/results/20260917_partial_eight_matchings/manifest.json"
BASE = ROOT / "scratch_general_exact.cnf"
BASE_SOURCE = ROOT / "scratch_general_exact_sat.py"


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(p, obj):
    with p.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    from pysat.card import CardEnc, EncType
    import pysat
    source_paths = [Path(__file__), SCOPE, BASE, BASE_SOURCE,
        ROOT / "acceleration/environments/rook-sat/uv.lock", ROOT / "acceleration/fixed_overlap_cnf.py",
        ROOT / "acceleration/audit_fixed_overlap_cnf.py", ROOT / "acceleration/run_fixed_overlap_sat.py",
        ROOT / "docs/GOAL_20260916_CP_CONTINUATION.md", ROOT / "scratch_general_exact_portfolio.json"]
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "pysat": pysat.__version__, "input_hashes": {str(p): digest(p) for p in source_paths},
        "question": "Determine exact scope/mapping and count candidate CNF sizes for the 2160-edge eight-coordinate family without building or solving a research CNF.",
        "limits": {"outer_vertices": 84, "outer_pairs": 3486, "solver_calls": 0},
        "status": "CANDIDATE_ENGINEERING_PREFLIGHT", "independent_review_pending": True})
    assert digest(BASE) == "91d22e62625e1221dd46b819e89494db8141dd4ddc9a06f13b9abdb530b83242"
    assert digest(BASE_SOURCE) == "8c21ac331af1569ee526ae4ddbf2553f6252d544a08b14bebb7fe3fd485489cc"
    scope = json.loads(SCOPE.read_text())
    fixed = set(map(tuple, scope["remaining_fixed_K_edges_outer"]))
    unknown = set(map(tuple, scope["unknown_edges_outer"]))
    assert len(fixed) == 120 and len(unknown) == 2160 and not fixed & unknown
    supports = list(combinations(range(7), 2))
    labels = [(2 * a + s, 2 * b + t) for a, b in supports for s in (0, 1) for t in (0, 1)]
    legacy = sorted(labels)
    forward = [legacy.index(label) for label in labels]
    legacy_variables = {pair: n for n, pair in enumerate(combinations(range(84), 2), 1)}
    units = []
    for pair in combinations(range(84), 2):
        if pair not in unknown:
            u, v = sorted(forward[x] for x in pair)
            variable = legacy_variables[u, v]
            units.append(variable if pair in fixed else -variable)
    units.sort(key=abs)
    assert len(units) == 1326 and sum(x > 0 for x in units) == 120
    base_header, body = BASE.read_bytes().split(b"\n", 1)
    assert base_header == b"p cnf 817278 1622502"
    suffix = "".join(f"{v} 0\n" for v in units).encode("ascii")
    new_header = b"p cnf 817278 1623828\n"
    streamed_digest = sha256(new_header)
    streamed_digest.update(body)
    streamed_digest.update(suffix)
    # Do not write a research CNF in this preflight.
    known = [[0] * 84 for _ in range(84)]
    for u, v in fixed:
        known[u][v] = known[v][u] = 1
    for u, v in unknown:
        known[u][v] = known[v][u] = -1
    bp, caps = Counter(), Counter()
    contradictory = []
    products = 0
    bp_rows, cap_rows = [], []
    for u in range(84):
        for symbol in range(14):
            incident = [known[u][v] for v in range(84) if v != u and symbol in labels[v]]
            target = 1 if symbol in labels[u] or (symbol ^ 1) in labels[u] else 2
            residual = target - incident.count(1)
            n = incident.count(-1)
            bp[n, residual] += 1
            bp_rows.append({"vertex": u, "symbol": symbol, "unknown_terms": n,
                            "known_ones": incident.count(1), "target": target, "residual": residual})
            if not 0 <= residual <= n:
                contradictory.append(["BP", u, symbol, n, residual])
    for u, v in combinations(range(84), 2):
        constant = int(known[u][v] == 1)
        linear = int(known[u][v] == -1)
        quadratic = 0
        for w in range(84):
            if w in (u, v):
                continue
            a, b = known[u][w], known[v][w]
            if a == 0 or b == 0:
                continue
            if a == b == 1:
                constant += 1
            elif a == b == -1:
                quadratic += 1
            else:
                linear += 1
        target = 2 - len(set(labels[u]) & set(labels[v]))
        residual = target - constant
        caps[linear + quadratic, residual] += 1
        products += quadratic
        cap_rows.append({"pair": [u, v], "constant": constant, "linear_terms": linear,
                         "quadratic_terms": quadratic, "target": target, "residual": residual})
        if residual < 0:
            contradictory.append(["PAIR_CAP", u, v, residual])
    def cardinality_counts(hist, equality):
        records = []
        total_clauses = total_aux = 0
        for (n, target), count in sorted(hist.items()):
            if not 0 <= target <= n:
                if not equality and target > n:
                    clauses = aux = 0
                else:
                    raise AssertionError("unsupported contradictory row")
            elif n == 0:
                clauses = aux = 0
            else:
                encode = CardEnc.equals if equality else CardEnc.atmost
                formula = encode(list(range(1, n + 1)), target, top_id=n, encoding=EncType.seqcounter)
                clauses, aux = len(formula.clauses), max(0, formula.nv - n)
            total_clauses += clauses * count
            total_aux += aux * count
            records.append({"terms": n, "target": target, "rows": count,
                            "clauses_per_row": clauses, "auxiliary_variables_per_row": aux})
        return {"rows": records, "total_clauses": total_clauses, "total_auxiliary_variables": total_aux}
    assert not contradictory
    bp_counts = cardinality_counts(bp, True)
    cap_counts = cardinality_counts(caps, False)
    compact_vars = 2160 + products + bp_counts["total_auxiliary_variables"] + cap_counts["total_auxiliary_variables"]
    common_clauses = bp_counts["total_clauses"] + cap_counts["total_clauses"]
    save(args.out / "constraint_census.json", {"bp_rows": bp_rows, "cap_rows": cap_rows,
        "bp_cardinality_counts": bp_counts, "cap_cardinality_counts": cap_counts})
    save(args.out / "legacy_adapter_plan.json", {"current_to_legacy": forward, "unit_literals": units,
        "true_units": 120, "false_units": 1206, "unknown_edges": 2160, "no_added_branch_units": True,
        "base_body_sha256": sha256(body).hexdigest(), "prospective_cnf_sha256": streamed_digest.hexdigest(),
        "prospective_cnf_bytes": len(new_header) + len(body) + len(suffix),
        "variables": 817278, "clauses": 1623828, "cnf_written": False})
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE_ENGINEERING_PREFLIGHT",
        "scope": "Exact eight-coordinate120-fixed-K family: 480 freed same-sign coordinate edges plus1680 disjoint-support edges; all remaining prescribed absences fixed.",
        "solver_calls": 0, "research_cnf_written": False, "full_target_resolution": False,
        "fixed_root_edges": 189, "fixed_K_edges": 120, "outer_unknown_edges": 2160, "outer_fixed_false_edges": 1206,
        "legacy_adapter": {"variables": 817278, "clauses": 1623828, "bytes": len(new_header)+len(body)+len(suffix)},
        "fixed_folded_candidate": {"edge_variables": 2160, "and_product_helpers": products,
             "bp_equalities": 1176, "outer_pair_caps": 3486, "variables": compact_vars,
             "clauses_oneway_product_implications": common_clauses + products,
             "clauses_exact_and_helpers": common_clauses + 3 * products,
             "encoding": "Fresh disjoint sequential-counter helpers per nontrivial fixed-folded row; product helper per pair/center; no row simplification beyond constants."},
        "constant_contradictions": contradictory,
        "outputs_sha256": {p.name: digest(p) for p in args.out.iterdir() if p.name != "manifest.json"},
        "limitations": ["Counts do not establish encoding correctness; prospective compact encoder has not been built or independently checked.",
            "Existing adapter only accepts168fixedK and must not be used unchanged on this scope.",
            "Historical fixed-K DRAT results and branch portfolios do not exclude this broader family."]}
    save(args.out / "summary.json", summary)
    print(json.dumps({"legacy": summary["legacy_adapter"], "compact": summary["fixed_folded_candidate"]}, indent=2))


if __name__ == "__main__":
    main()
