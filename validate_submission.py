"""Validate a one-based {u, v} edge list for srg(99,14,1,2).

Reads only; never creates or changes a submission. Exit 0 means valid,
exit 1 means invalid content, and exit 2 means an input file could not be
read. --self-test runs small exact regressions entirely in memory.
"""

import argparse
import json
from pathlib import Path
import re
import sys


EDGE_LINE = re.compile(r"\{[ \t]*([0-9]+)[ \t]*,[ \t]*([0-9]+)[ \t]*\}")


class EdgeFormatError(ValueError):
    def __init__(self, code, message, **details):
        super().__init__(message)
        self.code = code
        self.details = details


def parse_edge_text(text, n=99, expected_edges=693):
    """Accept LF or CRLF, one optional final newline, and no blank lines.

    Horizontal spaces or tabs are allowed inside braces. Every line must
    otherwise match the full edge syntax; numbering is one-based.
    """
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[-1] == "":
        lines.pop()
    edges, seen = [], set()
    for number, line in enumerate(lines, 1):
        if not line:
            raise EdgeFormatError("BLANK_LINE", "blank lines are not permitted", line=number)
        match = EDGE_LINE.fullmatch(line)
        if match is None:
            raise EdgeFormatError("MALFORMED_LINE", "line must have the form {u, v}", line=number)
        try:
            u, v = map(int, match.groups())
        except ValueError:
            raise EdgeFormatError("MALFORMED_INTEGER", "endpoint integer is too long", line=number) from None
        if not 1 <= u <= n or not 1 <= v <= n:
            raise EdgeFormatError("OUT_OF_RANGE", f"endpoints must be in 1..{n}", line=number)
        if u == v:
            raise EdgeFormatError("SELF_LOOP", "self-loops are not permitted", line=number)
        edge = (min(u, v), max(u, v))
        if edge in seen:
            raise EdgeFormatError("DUPLICATE_EDGE", "undirected edge appears more than once",
                                  line=number, edge=list(edge))
        seen.add(edge)
        edges.append(edge)
    if expected_edges is not None and len(edges) != expected_edges:
        raise EdgeFormatError("WRONG_EDGE_COUNT", f"expected exactly {expected_edges} edge lines",
                              edge_count=len(edges), expected_edge_count=expected_edges)
    return edges


def verify_edges(edges, n=99, k=14, adjacent_common=1, nonadjacent_common=2, max_errors=10):
    """Verify every degree and unordered pair using adjacency sets.

    This general internal function accepts one-based edges. Malformed
    endpoints, loops, and duplicates raise ValueError; a simple graph
    with incorrect mathematical parameters returns valid=False.
    """
    values = (n, k, adjacent_common, nonadjacent_common, max_errors)
    if any(type(value) is not int for value in values):
        raise ValueError("parameters must be integers")
    if n < 1 or not 0 <= k < n or min(adjacent_common, nonadjacent_common, max_errors) < 0:
        raise ValueError("invalid graph parameters")
    neighbors = [set() for _ in range(n)]
    seen = set()
    for raw_edge in edges:
        if not isinstance(raw_edge, (tuple, list)) or len(raw_edge) != 2:
            raise ValueError("each edge must contain exactly two endpoints")
        u, v = raw_edge
        if type(u) is not int or type(v) is not int or not 1 <= u <= n or not 1 <= v <= n:
            raise ValueError("invalid endpoint")
        if u == v:
            raise ValueError("self-loop")
        edge = (min(u, v), max(u, v))
        if edge in seen:
            raise ValueError("duplicate undirected edge")
        seen.add(edge)
        neighbors[u - 1].add(v - 1)
        neighbors[v - 1].add(u - 1)
    degrees = [len(row) for row in neighbors]
    degree_errors = [{"vertex": i + 1, "actual": degree, "expected": k}
                     for i, degree in enumerate(degrees) if degree != k]
    pair_errors = []
    adjacent_bad = nonadjacent_bad = adjacent_checked = nonadjacent_checked = 0
    for u in range(n):
        for v in range(u + 1, n):
            adjacent = v in neighbors[u]
            common = len(neighbors[u] & neighbors[v])
            target = adjacent_common if adjacent else nonadjacent_common
            if adjacent:
                adjacent_checked += 1
                adjacent_bad += common != target
            else:
                nonadjacent_checked += 1
                nonadjacent_bad += common != target
            if common != target and len(pair_errors) < max_errors:
                pair_errors.append({"vertices": [u + 1, v + 1], "adjacent": adjacent,
                                    "actual": common, "expected": target})
    valid = len(seen) * 2 == n * k and not degree_errors and not adjacent_bad and not nonadjacent_bad
    return {
        "status": "VALID_GRAPH" if valid else "INVALID_GRAPH", "valid": valid,
        "parameters": {"n": n, "k": k, "lambda": adjacent_common, "mu": nonadjacent_common},
        "edge_count": len(seen), "degrees_checked": n,
        "degree_range": [min(degrees), max(degrees)], "degree_mismatch_count": len(degree_errors),
        "pairs_checked": adjacent_checked + nonadjacent_checked,
        "adjacent_pairs_checked": adjacent_checked, "nonadjacent_pairs_checked": nonadjacent_checked,
        "adjacent_pair_mismatch_count": adjacent_bad, "nonadjacent_pair_mismatch_count": nonadjacent_bad,
        "degree_errors_shown": degree_errors[:max_errors], "pair_errors_shown": pair_errors,
    }


def self_test():
    checks = []

    def require(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    rook = [(u + 1, v + 1) for u in range(9) for v in range(u + 1, 9)
            if u // 3 == v // 3 or u % 3 == v % 3]
    triangle = [(1, 2), (1, 3), (2, 3)]
    require(verify_edges(rook, 9, 4, 1, 2)["valid"], "rook9_accept")
    triangle_result = verify_edges(triangle, 3, 2, 1, 0)
    require(triangle_result["valid"] and triangle_result["nonadjacent_pairs_checked"] == 0,
            "triangle3_accept_with_vacuous_nonedge_condition")
    require(not verify_edges(rook[:-1], 9, 4, 1, 2)["valid"], "rook9_edge_deletion_reject")
    for edges, n, k, lam, mu in ((rook, 9, 4, 1, 2), (triangle, 3, 2, 1, 0)):
        matrix = [[0] * n for _ in range(n)]
        for u, v in edges:
            matrix[u - 1][v - 1] = matrix[v - 1][u - 1] = 1
        require(all(sum(matrix[i][t] * matrix[t][j] for t in range(n)) ==
                    (k if i == j else lam if matrix[i][j] else mu)
                    for i in range(n) for j in range(n)), f"integer_matrix_calibration_{n}")
    rendered = "\n".join(f"{{{u}, {v}}}" for u, v in triangle)
    for suffix in ("", "\n", "\r\n"):
        require(parse_edge_text(rendered + suffix, 3, 3) == triangle, f"parser_final_newline_{suffix!r}")
    require(parse_edge_text(rendered.replace("\n", "\r\n") + "\r\n", 3, 3) == triangle,
            "parser_crlf")
    malformed = (
        ("", "WRONG_EDGE_COUNT"), ("{1, 2}\n\n{1, 3}", "BLANK_LINE"),
        (rendered + "\n\n", "BLANK_LINE"), ("{1, 2}\n{1, 2}", "DUPLICATE_EDGE"),
        ("{1, 2}\n{2, 1}", "DUPLICATE_EDGE"), ("{1, 1}", "SELF_LOOP"),
        ("{0, 2}", "OUT_OF_RANGE"), ("{1, 100}", "OUT_OF_RANGE"),
        ("{1 2}", "MALFORMED_LINE"), ("{1, 2} extra", "MALFORMED_LINE"),
        (" {1, 2}", "MALFORMED_LINE"), ("{1, 2} ", "MALFORMED_LINE"),
        ("{-1, 2}", "MALFORMED_LINE"), ("{True, 2}", "MALFORMED_LINE"),
        ("{1.0, 2}", "MALFORMED_LINE"), ("[1, 2]", "MALFORMED_LINE"),
        ("{1, 2}\r{1, 3}", "MALFORMED_LINE"), ("{1, 2}\v{1, 3}", "MALFORMED_LINE"),
        ("{1, 2}\r", "MALFORMED_LINE"),
        ("{1, 2}", "WRONG_EDGE_COUNT"),
    )
    for index, (text, expected_code) in enumerate(malformed):
        try:
            parse_edge_text(text)
        except EdgeFormatError as exc:
            require(exc.code == expected_code, f"parser_reject_{index}_{expected_code}")
        else:
            raise AssertionError(f"malformed parser case {index} accepted")
    circulant = sorted({tuple(sorted((u + 1, (u + distance) % 99 + 1)))
                        for u in range(99) for distance in range(1, 8)})
    require(len(circulant) == 693, "invalid_regular_graph_has_693_edges")
    text = "\n".join(f"{{{u}, {v}}}" for u, v in circulant) + "\n"
    result = verify_edges(parse_edge_text(text))
    require(not result["valid"] and result["degree_mismatch_count"] == 0
            and result["pairs_checked"] == 4851, "invalid_99_vertex_regular_graph_reject")
    return {"status": "SELF_TEST_PASS", "checks_passed": len(checks), "checks": checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path("submission.txt"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=True))
        return 0
    try:
        text = args.path.read_bytes().decode("utf-8")
    except FileNotFoundError:
        print(json.dumps({"status": "MISSING_FILE", "valid": False, "path": str(args.path)}))
        return 2
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"status": "READ_ERROR", "valid": False, "path": str(args.path), "error": str(exc)}))
        return 2
    try:
        edges = parse_edge_text(text)
    except EdgeFormatError as exc:
        print(json.dumps({"status": "INVALID_FORMAT", "valid": False, "path": str(args.path),
                          "error_code": exc.code, "error": str(exc), **exc.details}))
        return 1
    report = verify_edges(edges)
    print(json.dumps({"path": str(args.path), **report}))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
