"""Direct-CNF producer for one fixed-star rook window; independent audit required."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import argparse
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def save(p, data):
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def upper(variables, bound):
    assert len(variables) == len(set(variables))
    if bound < 0:
        return [()]
    if bound >= len(variables):
        return []
    return [tuple(-v for v in group) for group in combinations(variables, bound + 1)]


def exact(variables, value):
    if not 0 <= value <= len(variables):
        return [()]
    return upper(variables, value) + [tuple(group) for group in combinations(variables, len(variables) - value + 1)]


def encode(known, shared, degree_builder):
    n = len(known)
    assert all(len(row) == n for row in known)
    assert all(known[u][v] == known[v][u] for u in range(n) for v in range(n))
    assert all(known[u][u] == 0 for u in range(n))
    edge_vars = []
    adjacency = [[bool(known[u][v]) if known[u][v] != -1 else None for v in range(n)] for u in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if known[u][v] == -1:
                number = len(edge_vars) + 1
                adjacency[u][v] = adjacency[v][u] = number
                edge_vars.append({"u": u, "v": v, "id": number})
    degree_rows = degree_builder(adjacency)
    clauses = []
    for row in degree_rows:
        assert all(type(v) is int and v > 0 for v in row["variables"])
        clauses.extend(exact(row["variables"], row["value"]))
    degree_clause_count = len(clauses)
    products = []
    product_ids = {}
    pair_rows = []
    for u in range(n):
        for v in range(u + 1, n):
            constant = shared[u][v]
            literals = []
            for w in range(n):
                x, y = adjacency[u][w], adjacency[v][w]
                if x is False or y is False:
                    continue
                if x is True and y is True:
                    constant += 1
                elif x is True:
                    literals.append(y)
                elif y is True:
                    literals.append(x)
                else:
                    assert type(x) is int and type(y) is int and x != y
                    key = tuple(sorted((x, y)))
                    z = product_ids.get(key)
                    if z is None:
                        z = len(edge_vars) + len(products) + 1
                        product_ids[key] = z
                        products.append({"id": z, "left": key[0], "right": key[1]})
                        clauses.extend([(-z, key[0]), (-z, key[1]), (z, -key[0], -key[1])])
                    literals.append(z)
            edge = adjacency[u][v]
            if edge is True:
                constant += 1
            elif edge is not False:
                literals.append(edge)
            assert all(type(x) is int and x > 0 for x in literals)
            assert len(set(literals)) == len(literals)
            bound = 2 - constant
            clauses.extend(upper(literals, bound))
            pair_rows.append({"u": u, "v": v, "constant": constant, "literals": literals, "bound": bound})
    model = {"known_adjacency": known, "shared_core_common_neighbors": shared,
             "edge_variables": edge_vars, "products": products,
             "degree_constraints": degree_rows, "pair_constraints": pair_rows,
             "variables": len(edge_vars) + len(products), "clauses": len(clauses),
             "degree_clause_count": degree_clause_count, "product_clause_count": 3 * len(products)}
    return model, clauses


def evaluate(model, clauses, graph):
    values = {entry["id"]: bool(graph[entry["u"]][entry["v"]]) for entry in model["edge_variables"]}
    for entry in model["products"]:
        values[entry["id"]] = values[entry["left"]] and values[entry["right"]]
    violated = [i for i, clause in enumerate(clauses) if not any(values[abs(lit)] == (lit > 0) for lit in clause)]
    return values, violated


def controls(out):
    cardinality_cases = 0
    for n in range(7):
        variables = list(range(1, n + 1))
        for values in product((False, True), repeat=n):
            def satisfies(clauses):
                return all(any(values[abs(lit) - 1] == (lit > 0) for lit in clause) for clause in clauses)
            for k in range(-1, n + 2):
                assert satisfies(upper(variables, k)) == (sum(values) <= k)
                assert satisfies(exact(variables, k)) == (sum(values) == k)
                cardinality_cases += 2
    rook = [[int(u != v and (u // 3 == v // 3 or u % 3 == v % 3)) for v in range(9)] for u in range(9)]
    known = [[0 if u == v else -1 for v in range(9)] for u in range(9)]
    def degrees(adj):
        return [{"variables": [adj[u][v] for v in range(9) if u != v], "value": 4, "label": [u]}
                for u in range(9)]
    model, clauses = encode(known, [[0] * 9 for _ in range(9)], degrees)
    values, violations = evaluate(model, clauses, rook)
    assert not violations
    corrupted = [row.copy() for row in rook]
    corrupted[0][1] = corrupted[1][0] = 1 - corrupted[0][1]
    _, corrupt_failures = evaluate(model, clauses, corrupted)
    assert corrupt_failures
    save(out / "rook_control_model.json", model)
    save(out / "rook_control_assignment.json", {"adjacency": rook, "assignment": values,
         "corrupted_adjacency": corrupted, "corrupted_false_clause_indices": corrupt_failures})
    write_cnf(out / "rook_control.cnf", model["variables"], clauses)
    return {"cardinality_truth_table_cases": cardinality_cases, "rook9_all_unknown_encoding": True,
            "rook9_positive_assignment_false_clauses": 0,
            "corrupted_edge_assignment_false_clauses": len(corrupt_failures),
            "controls_are_producer_calibration_not_independent_verification": True}


def write_cnf(path, variables, clauses):
    with path.open("x", encoding="ascii", newline="\n") as stream:
        stream.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in (Path(__file__), args.input, Path("acceleration/theory_20260930_rook_window_sat_spec.md"), Path("uv.lock"))},
        "question": "Exact CNF for the stated fixed-star local-window necessary constraints.",
        "scope": "CANDIDATE encoding equivalence for one fixed central star, 600 independent edge variables, no target-wide coverage.",
        "resource_limits": "Finite generation only; solver invocation deferred to independent model review gate.",
        "status": "CANDIDATE", "independent_review_pending": True,
    })
    calibration = controls(args.out)
    star = json.loads(args.input.read_text())
    known = [[0] * 50 for _ in range(50)]
    def edge(u, v, value):
        known[u][v] = known[v][u] = value
    for u, v in star["matching"]:
        edge(u, v, 1)
    for cell, item in enumerate(star["four_factors"], 1):
        for u, v in item["partner_matching"]:
            edge(cell * 10 + u, cell * 10 + v, 1)
        for u, row in enumerate(item["incidence_block"]):
            for v, value in enumerate(row):
                if value:
                    edge(u, cell * 10 + v, 1)
    for ca, cb in combinations(range(1, 5), 2):
        for u in range(ca * 10, ca * 10 + 10):
            for v in range(cb * 10, cb * 10 + 10):
                edge(u, v, -1)
    def degrees(adj):
        rows = []
        for ca, cb in combinations(range(1, 5), 2):
            value = 2 if (ca, cb) in ((1, 4), (2, 3)) else 1
            for u in range(ca * 10, ca * 10 + 10):
                rows.append({"variables": [adj[u][v] for v in range(cb * 10, cb * 10 + 10)], "value": value, "label": [ca, cb, "row", u]})
            for v in range(cb * 10, cb * 10 + 10):
                rows.append({"variables": [adj[u][v] for u in range(ca * 10, ca * 10 + 10)], "value": value, "label": [ca, cb, "column", v]})
        return rows
    shared = [[int(u != v and u // 10 == v // 10) for v in range(50)] for u in range(50)]
    model, clauses = encode(known, shared, degrees)
    assert len(model["edge_variables"]) == 600
    model["cell_rook_coordinates"] = [[0, 0], [1, 1], [1, 2], [2, 1], [2, 2]]
    save(args.out / "model.json", model)
    write_cnf(args.out / "instance.cnf", model["variables"], clauses)
    for name in ("instance.cnf", "model.json"):
        with (args.out / name).open("rb") as source, (args.out / (name + ".gz")).open("xb") as target:
            with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as compressed:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    compressed.write(block)
    save(args.out / "controls.json", calibration)
    files = [p for p in args.out.iterdir() if p.is_file()]
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE",
         "variables": model["variables"], "edge_variables": 600, "product_variables": len(model["products"]),
         "clauses": len(clauses), "pair_constraints": len(model["pair_constraints"]),
         "degree_constraints": len(model["degree_constraints"]), "independent_review_pending": True,
         "solver_launched": False, "elapsed_seconds": time.monotonic() - start,
         "outputs": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in files}})
    print(json.dumps({"variables": model["variables"], "clauses": len(clauses), "controls": calibration, "elapsed_seconds": time.monotonic() - start}, indent=2))


if __name__ == "__main__":
    main()
