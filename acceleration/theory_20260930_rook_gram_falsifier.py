"""Exact PSD/rank discovery certificates for completed local rook windows."""
from datetime import datetime, timezone
from fractions import Fraction
from functools import reduce
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def save(p, data):
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def quadratic(matrix, vector):
    return sum(vector[u] * matrix[u][v] * vector[v]
               for u in range(len(matrix)) for v in range(len(matrix)))


def primitive(vector):
    scale = lcm(*(value.denominator for value in vector))
    integers = [int(value * scale) for value in vector]
    divisor = reduce(gcd, integers)
    assert divisor
    return [value // divisor for value in integers]


def exact_test(matrix, rank_bound):
    n = len(matrix)
    assert all(len(row) == n for row in matrix)
    assert all(matrix[u][v] == matrix[v][u] for u in range(n) for v in range(n))
    reduced = [[Fraction(x) for x in row] for row in matrix]
    vectors = [[Fraction(i == j) for i in range(n)] for j in range(n)]
    original_indices = list(range(n))
    pivots = []
    def negative(vector, reason):
        integers = primitive(vector)
        value = quadratic(matrix, integers)
        assert value < 0
        return {"psd": False, "rank": None, "rank_null_reason": "A negative-direction certificate already falsifies PSD; full rank was not needed.",
                "reason": reason, "integer_negative_vector": integers,
                "support": [i for i, x in enumerate(integers) if x], "quadratic_value": value}
    for k in range(n):
        for j in range(k, n):
            if reduced[j][j] < 0:
                return negative(vectors[j], "NEGATIVE_DIAGONAL_CONGRUENCE_PIVOT")
        positive = next((j for j in range(k, n) if reduced[j][j] > 0), None)
        if positive is None:
            for i in range(k, n):
                for j in range(i + 1, n):
                    if reduced[i][j]:
                        sign = 1 if reduced[i][j] > 0 else -1
                        return negative([x - sign * y for x, y in zip(vectors[i], vectors[j])], "ZERO_DIAGONAL_NONZERO_OFFDIAGONAL")
            break
        if positive != k:
            reduced[k], reduced[positive] = reduced[positive], reduced[k]
            for row in reduced:
                row[k], row[positive] = row[positive], row[k]
            vectors[k], vectors[positive] = vectors[positive], vectors[k]
            original_indices[k], original_indices[positive] = original_indices[positive], original_indices[k]
        pivot = reduced[k][k]
        pivots.append(pivot)
        weights = [reduced[k][j] / pivot for j in range(k + 1, n)]
        for j in range(k + 1, n):
            weight = weights[j - k - 1]
            vectors[j] = [x - weight * y for x, y in zip(vectors[j], vectors[k])]
        for i in range(k + 1, n):
            for j in range(i, n):
                value = reduced[i][j] - reduced[i][k] * reduced[k][j] / pivot
                reduced[i][j] = reduced[j][i] = value
        for j in range(k + 1, n):
            reduced[k][j] = reduced[j][k] = Fraction(0)
    rank = len(pivots)
    result = {"psd": True, "rank": rank, "rank_bound": rank_bound, "rank_bound_pass": rank <= rank_bound}
    if rank > rank_bound:
        size = rank_bound + 1
        determinant = Fraction(1)
        for pivot in pivots[:size]:
            determinant *= pivot
        assert determinant.denominator == 1 and determinant > 0
        result.update(nonzero_principal_minor_indices=original_indices[:size],
                      nonzero_principal_minor_determinant=int(determinant))
    return result


def controls():
    tests = [([[1, 0], [0, 1]], 2, True, 2),
             ([[1, 1], [1, 1]], 2, True, 1),
             ([[-1, 0], [0, 1]], 2, False, None),
             ([[0, 1], [1, 0]], 2, False, None),
             ([[1]], 0, True, 1)]
    records = []
    for matrix, bound, psd, rank in tests:
        result = exact_test(matrix, bound)
        assert result["psd"] == psd and result["rank"] == rank
        records.append({"matrix": matrix, "rank_bound": bound, "result": result})
    rook = [[int(u != v and (u // 3 == v // 3 or u % 3 == v % 3)) for v in range(9)] for u in range(9)]
    gram = [[27 * int(u == v) - 9 * rook[u][v] + 1 for v in range(9)] for u in range(9)]
    result = exact_test(gram, 8)
    assert result["psd"] and result["rank"] == 8
    records.append({"name": "rook9_exact_gram", "result": result})
    return records


def load_graph(path):
    raw = json.loads(path.read_text())
    if "adjacency_full59" in raw:
        graph = raw["adjacency_full59"]
    else:
        if "external_adjacency_rows_hex" in raw:
            rows = [int(row, 16) for row in raw["external_adjacency_rows_hex"]]
            external = [[(row >> v) & 1 for v in range(50)] for row in rows]
        else:
            external = raw["adjacency"]
        assert len(external) == 50 and all(len(row) == 50 for row in external)
        graph = [[0] * 59 for _ in range(59)]
        for u in range(9):
            for v in range(9):
                graph[u][v] = int(u != v and (u // 3 == v // 3 or u % 3 == v % 3))
        coords = raw.get("cell_rook_coordinates", [[0, 0], [1, 1], [1, 2], [2, 1], [2, 2]])
        assert coords == [[0, 0], [1, 1], [1, 2], [2, 1], [2, 2]]
        for u in range(50):
            r, c = coords[u // 10]
            graph[9 + u][3 * r + c] = graph[3 * r + c][9 + u] = 1
            for v in range(50):
                graph[9 + u][9 + v] = external[u][v]
    assert len(graph) == 59 and all(len(row) == 59 for row in graph)
    assert all(type(value) is int and value in (0, 1) for row in graph for value in row)
    assert all(graph[u][u] == 0 for u in range(59))
    assert all(graph[u][v] == graph[v][u] for u in range(59) for v in range(59))
    return graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), Path("acceleration/theory_20260930_rook_gram_falsifier.md"), Path("uv.lock")]
    if args.input:
        files.append(args.input)
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
         "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
         "input_hashes": {p.as_posix(): digest(p) for p in files},
         "question": "Does a completed induced59 local graph violate either exact principal Gram PSD/rank necessity?",
         "scope": "Necessary extension test only; raw local graph validity requires a separate checker.",
         "resource_limits": "At most two 59-by-59 rational congruence eliminations and six calibration matrices.",
         "status": "CANDIDATE", "independent_review_pending": True})
    save(args.out / "controls.json", controls())
    if not args.input:
        print(json.dumps({"producer_controls": "PASS", "research_graph_tested": False}))
        return
    graph = load_graph(args.input)
    records = []
    for name, diagonal, edge_coefficient, constant, bound in (("27I-9A+J", 27, -9, 1, 44), ("A+4I", 4, 1, 0, 55)):
        gram = [[diagonal * int(u == v) + edge_coefficient * graph[u][v] + constant for v in range(59)] for u in range(59)]
        records.append({"matrix": name, "result": exact_test(gram, bound)})
    save(args.out / "result.json", {"status": "CANDIDATE", "independent_review_pending": True,
         "tests": records, "extension_obstruction_candidate": any(not x["result"]["psd"] or not x["result"].get("rank_bound_pass", True) for x in records),
         "target_level_nonexistence": False})
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
