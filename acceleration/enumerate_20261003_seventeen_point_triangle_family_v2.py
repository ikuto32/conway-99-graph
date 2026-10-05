"""SOURCE_ONLY: exact labelled 9*24*24 local twelve-triangle family.

No target completion, inducedness, symmetry or independent approval is inferred.
Controls and enumeration are separate, explicitly authorized invocations.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/enumerate_20261003_seventeen_point_triangle_family_v2.py"
SPEC = "acceleration/enumerate_20261003_seventeen_point_triangle_family_v2_spec.md"
PINS = {
    "docs/CANDIDATE_20261003_UNBALANCED_TWELVE_TRIANGLE_WORD_TARGET_TYPES_V1.md": "6f26e9f4b989f76de8b5954627ed217a00a2beabf88e8b11f64eb33c34ba209b",
    "docs/CANDIDATE_20261003_SEVENTEEN_POINT_UNBALANCED_TWELVE_TRIANGLE_CIRCUIT_V1.md": "f6f9e883b577d6969eafaac9239c37d637804786a08a6b5e676cebe0208e576b",
    "acceleration/audit_20261003_unbalanced_twelve_triangle_word_target_family_v1.md": "31d2ff708881c36f2a6271e4d46de5181ba5d7e91377e481f29306b7f97b1d4c",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "docs/COMPUTE_POLICY.md": "9d3f57e8e36376e71fe5fb2733d19d6c0eacf92c71f763e66224dda95f59e136",
}
N = 17
POPULATION = 5184
PART_SIZE = 128
SIGNS = [-1] * 7 + [1] * 5
NEGATIVE = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 8],
            [1, 9, 10], [11, 12, 13], [14, 15, 16]]
PERMS = tuple(itertools.permutations(range(4)))
OLD_VALID = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 9], [1, 8, 10],
             [15, 11, 14], [16, 12, 13], [2, 15, 16], [3, 7, 11],
             [4, 8, 12], [5, 9, 13], [6, 10, 14]]
ID51_VALID = NEGATIVE + [[2, 11, 14], [3, 7, 12], [4, 9, 15],
                         [5, 8, 16], [6, 10, 13]]


class Veto(ValueError):
    def __init__(self, stage, detail=None):
        self.stage, self.detail = stage, detail
        super().__init__(stage)


class SaveStop(RuntimeError):
    pass


def require(condition, stage, detail=None):
    if not condition:
        raise Veto(stage, detail)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def tick(deadline, reserve=20):
    state = deadline.status()
    if state["stop_required"] or state["remaining_seconds"] <= reserve:
        raise SaveStop("not completed within the allocated budget")


def bytes_json(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def save(path, value):
    with path.open("xb") as handle:
        handle.write(bytes_json(value))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(proposal_id):
    require(type(proposal_id) is int, "PROPOSAL_ID_TYPE")
    require(0 <= proposal_id < POPULATION, "PROPOSAL_ID_RANGE")
    quotient, r_index = divmod(proposal_id, 24)
    choice_index, ab_index = divmod(quotient, 24)
    left_index, right_index = divmod(choice_index, 3)
    r_left, r_right = 11 + left_index, 14 + right_index
    remaining = [v for v in range(11, 17) if v not in (r_left, r_right)]
    ab, assignment = PERMS[ab_index], PERMS[r_index]
    positive = [[2, r_left, r_right]] + [
        [3 + i, 7 + ab[i], remaining[assignment[i]]] for i in range(4)]
    role = {"x_left_choice": left_index, "x_right_choice": right_index,
            "ab_permutation_index": ab_index, "r_permutation_index": r_index}
    return role, [row[:] for row in NEGATIVE] + positive


def matrix_from(rows):
    matrix = [[0] * N for _ in range(N)]
    for row in rows:
        for u, v in itertools.combinations(row, 2):
            matrix[u][v] = matrix[v][u] = 1
    return matrix


def products(matrix):
    return [[sum(matrix[u][w] * matrix[w][v] for w in range(N))
             for v in range(N)] for u in range(N)]


def graph_caps(matrix):
    require(type(matrix) is list and len(matrix) == N and
            all(type(row) is list and len(row) == N for row in matrix), "MATRIX_SHAPE")
    require(all(type(v) is int for row in matrix for v in row), "MATRIX_TYPES")
    require(all(v in (0, 1) for row in matrix for v in row), "MATRIX_BINARY")
    require(all(matrix[u][u] == 0 for u in range(N)), "MATRIX_DIAGONAL")
    require(all(matrix[u][v] == matrix[v][u] for u in range(N)
                for v in range(u)), "MATRIX_SYMMETRY")
    cn = products(matrix)
    for u, v in itertools.combinations(range(N), 2):
        if matrix[u][v]:
            require(cn[u][v] == 1, "EDGE_CN", [u, v, cn[u][v]])
    for u, v in itertools.combinations(range(N), 2):
        if not matrix[u][v]:
            require(cn[u][v] <= 2, "NONEDGE_CN", [u, v, cn[u][v]])
    return cn


def validate(rows, signs):
    require(type(rows) is list and len(rows) == 12 and
            all(type(row) is list and len(row) == 3 for row in rows), "ROW_SHAPE")
    require(all(type(v) is int for row in rows for v in row), "ROW_TYPES")
    require(all(0 <= v < N for row in rows for v in row), "ROW_RANGE")
    require(all(len(set(row)) == 3 for row in rows), "ROW_DISTINCT_POINTS")
    canonical = [tuple(sorted(row)) for row in rows]
    require(len(set(canonical)) == 12, "DISTINCT_ROWS")
    occupancy = Counter(pair for row in canonical for pair in itertools.combinations(row, 2))
    require(all(c == 1 for c in occupancy.values()), "PAIR_LINEARITY")
    require(type(signs) is list and len(signs) == 12, "COEFFICIENT_POPULATION")
    require(all(type(s) is int for s in signs), "COEFFICIENT_TYPES")
    require(all(s in (-1, 1) for s in signs), "COEFFICIENT_DOMAIN")
    require(signs.count(-1) == 7 and signs.count(1) == 5, "SIGN_COUNTS")
    integer_sum = [sum(s for row, s in zip(rows, signs) if v in row) for v in range(N)]
    require(all(v % 3 == 0 for v in integer_sum), "GF3_WORD")
    degrees = [sum(v in row for row in rows) for v in range(N)]
    require(degrees.count(3) == 2 and degrees.count(2) == 15, "SELECTED_DEGREES")
    matrix = matrix_from(rows)
    cn = graph_caps(matrix)
    actual = [list(t) for t in itertools.combinations(range(N), 3)
              if all(matrix[u][v] for u, v in itertools.combinations(t, 2))]
    require(actual == [list(t) for t in sorted(canonical)], "ACTUAL_TRIANGLE_FAMILY")
    return matrix, cn, degrees, integer_sum, actual


def record(proposal_id):
    role, rows = decode(proposal_id)
    matrix = matrix_from(rows)
    cn = products(matrix)
    actual = [list(t) for t in itertools.combinations(range(N), 3)
              if all(matrix[u][v] for u, v in itertools.combinations(t, 2))]
    try:
        validate(rows, SIGNS)
        stage, detail = None, None
    except Veto as error:
        stage, detail = error.stage, error.detail
    adjacency = ["".join(map(str, row)) for row in matrix]
    graph_key = hashlib.sha256(("\n".join(adjacency) + "\n").encode("ascii")).hexdigest()
    return {"proposal_id": proposal_id, "role": role, "negative_centers": [0, 1],
            "triples": rows, "coefficients": SIGNS[:], "adjacency_rows": adjacency,
            "common_neighbors": cn, "selected_degrees": [sum(v in t for t in rows) for v in range(N)],
            "graph_degrees": [sum(row) for row in matrix], "actual_triangles": actual,
            "integer_incidence_sum": [sum(s for t, s in zip(rows, SIGNS) if v in t) for v in range(N)],
            "coefficient_sum_mod3": sum(SIGNS) % 3, "valid_local_geometry": stage is None,
            "first_veto": stage, "veto_detail": detail, "labelled_graph_sha256": graph_key}


def controls(out, deadline):
    # These literal positives predate this enumeration; cal is not a target proof.
    old_matrix, old_cn, old_degrees, old_sum, old_triangles = validate(OLD_VALID, SIGNS)
    mapped_matrix, mapped_cn, mapped_degrees, mapped_sum, mapped_triangles = validate(ID51_VALID, SIGNS)
    require(decode(51)[1] == ID51_VALID, "KNOWN_DECODER_51")
    last_role, last_rows = decode(5183)
    require(last_role == {"x_left_choice": 2, "x_right_choice": 2,
                         "ab_permutation_index": 23, "r_permutation_index": 23} and
            last_rows[7:] == [[2, 13, 16], [3, 10, 15], [4, 9, 14], [5, 8, 12], [6, 7, 11]], "KNOWN_DECODER_LAST")
    triangle = [[0] * N for _ in range(N)]
    for u, v in itertools.combinations(range(3), 2):
        triangle[u][v] = triangle[v][u] = 1
    triangle_cn = graph_caps(triangle)
    positives = [
        {"case": "literal_old17", "rows": OLD_VALID, "signs": SIGNS,
         "adjacency": old_matrix, "common_neighbors": old_cn, "selected_degrees": old_degrees,
         "integer_incidence_sum": old_sum, "actual_triangles": old_triangles},
        {"case": "literal_mapped51", "rows": ID51_VALID, "signs": SIGNS,
         "adjacency": mapped_matrix, "common_neighbors": mapped_cn, "selected_degrees": mapped_degrees,
         "integer_incidence_sum": mapped_sum, "actual_triangles": mapped_triangles},
        {"case": "decoder51", "proposal_id": 51, "role": decode(51)[0], "rows": decode(51)[1]},
        {"case": "decoder_last", "proposal_id": 5183, "role": last_role, "rows": last_rows},
        {"case": "isolated_triangle_caps", "adjacency": triangle, "common_neighbors": triangle_cn},
    ]
    cases = []

    def reject(name, expected, call, damage):
        tick(deadline)
        try:
            call()
        except Veto as error:
            observed = error.stage
        else:
            observed = "ACCEPTED"
        entry = {"case": name, "expected": expected, "actual": observed, "damage": damage}
        cases.append(entry)
        require(observed == expected, "CONTROL_STAGE", entry)

    for value, stage in [(-1, "PROPOSAL_ID_RANGE"), (5184, "PROPOSAL_ID_RANGE"),
                         (False, "PROPOSAL_ID_TYPE"), (1.0, "PROPOSAL_ID_TYPE")]:
        reject("id_" + repr(value), stage, lambda v=value: decode(v), value)
    mutations = [
        ("missing_row", "ROW_SHAPE", OLD_VALID[:-1]),
        ("row_object", "ROW_SHAPE", [{"points": OLD_VALID[0]}] + OLD_VALID[1:]),
        ("bool_point", "ROW_TYPES", [[False, 1, 2]] + OLD_VALID[1:]),
        ("float_point", "ROW_TYPES", [[0.0, 1, 2]] + OLD_VALID[1:]),
        ("outside_point", "ROW_RANGE", [[17, 1, 2]] + OLD_VALID[1:]),
        ("repeated_point", "ROW_DISTINCT_POINTS", [[0, 0, 2]] + OLD_VALID[1:]),
        ("duplicate_row", "DISTINCT_ROWS", OLD_VALID[:-1] + [OLD_VALID[0]]),
        ("reused_pair", "PAIR_LINEARITY", OLD_VALID[:-1] + [[0, 1, 16]]),
    ]
    for name, stage, rows in mutations:
        reject(name, stage, lambda rows=rows: validate(rows, SIGNS), rows)
    for name, stage, signs in [
        ("missing_coefficient", "COEFFICIENT_POPULATION", SIGNS[:-1]),
        ("bool_coefficient", "COEFFICIENT_TYPES", [False] + SIGNS[1:]),
        ("float_coefficient", "COEFFICIENT_TYPES", [-1.0] + SIGNS[1:]),
        ("zero_coefficient", "COEFFICIENT_DOMAIN", [0] + SIGNS[1:]),
        ("all_positive", "SIGN_COUNTS", [1] * 12),
        ("opposite_sign_exchange", "GF3_WORD", [1] + SIGNS[1:7] + [-1] + SIGNS[8:]),
    ]:
        reject(name, stage, lambda signs=signs: validate(OLD_VALID, signs), signs)
    graph_damage = []
    graph_damage.append(("short_matrix", "MATRIX_SHAPE", triangle[:-1]))
    for name, stage, row, col, value in [
        ("bool_zero", "MATRIX_TYPES", 3, 3, False),
        ("float_one", "MATRIX_TYPES", 0, 1, 1.0),
        ("nonbinary", "MATRIX_BINARY", 0, 1, 2),
        ("loop", "MATRIX_DIAGONAL", 3, 3, 1),
        ("asymmetry", "MATRIX_SYMMETRY", 0, 1, 0),
    ]:
        damaged = [r[:] for r in triangle]
        damaged[row][col] = value
        graph_damage.append((name, stage, damaged))
    k4 = [[int(u != v and u < 4 and v < 4) for v in range(N)] for u in range(N)]
    # All edges pass the first EDGE_CN scan; nonedge (0,1) has CN=3.
    # Six private triangle completions of the six K2,3 edges, padded to17.
    k23 = matrix_from([[0, 2, 5], [0, 3, 6], [0, 4, 7],
                       [1, 2, 8], [1, 3, 9], [1, 4, 10]])
    graph_damage.extend([("edge_two_CN", "EDGE_CN", k4), ("nonedge_three_CN", "NONEDGE_CN", k23)])
    for name, stage, matrix in graph_damage:
        reject(name, stage, lambda matrix=matrix: graph_caps(matrix), matrix)
    save(out / "controls.json", cases)
    save(out / "positive_fixtures.json", positives)
    tick(deadline)
    return {"status": "SEVENTEEN_POINT_LABELLED_FAMILY_V2_AUTHOR_CONTROLS_PASS",
            "positive_controls": 5, "strict_negative_controls": len(cases),
            "actual_family_enumerated": False, "actual_target_input_read": False,
            "literal_known_valid_rows": {"old17": OLD_VALID, "mapped_id51": ID51_VALID},
            "scope": "Producer-only literal fixtures and precise parser/local-geometry rejection controls; independent verification required."}


def enumerate_family(out, deadline):
    records, tallies, valid_by_graph, part_files, next_id = [], Counter(), {}, [], 0
    valid_graph_matrices = {}

    def flush():
        if not records:
            return
        part = out / ("part_%03d.json" % len(part_files))
        save(part, {"schema": "SEVENTEEN_POINT_LABELLED_FAMILY_PART_V1",
                    "start": records[0]["proposal_id"], "stop": records[-1]["proposal_id"] + 1,
                    "records": records})
        part_files.append({"path": part.name, "sha256": sha(part), "population": len(records)})
        records.clear()
        cp = {"schema": "SEVENTEEN_POINT_LABELLED_FAMILY_CHECKPOINT_V1", "next_proposal_id": next_id,
              "tallies": dict(tallies), "valid_graphs": valid_by_graph, "parts": part_files[:],
              "coverage": "Exact labelled prefix [0,next_proposal_id), no resumed or omitted cases."}
        save(out / ("checkpoint_%03d.json" % (len(part_files) - 1)), cp)

    try:
        for proposal_id in range(POPULATION):
            tick(deadline)
            item = record(proposal_id)
            records.append(item)
            next_id = proposal_id + 1
            tallies[item["first_veto"] or "VALID_LOCAL_GEOMETRY"] += 1
            if item["valid_local_geometry"]:
                key = item["labelled_graph_sha256"]
                require(key not in valid_graph_matrices or valid_graph_matrices[key] == item["adjacency_rows"],
                        "GRAPH_HASH_COLLISION")
                valid_graph_matrices.setdefault(key, item["adjacency_rows"])
                valid_by_graph.setdefault(key, []).append(proposal_id)
                (out / "valid").mkdir(exist_ok=True)
                save(out / "valid" / ("case_%04d.json" % proposal_id), item)
            if len(records) == PART_SIZE:
                flush()
                print(json.dumps({"completed": next_id, "population": POPULATION,
                                  "valid_labelled": tallies["VALID_LOCAL_GEOMETRY"],
                                  "distinct_labelled_graphs": len(valid_by_graph)}), flush=True)
        flush()
        tick(deadline)
    except SaveStop:
        flush()
        raise
    save(out / "valid_graph_groups.json", valid_by_graph)
    tick(deadline)
    return {"status": "SEVENTEEN_POINT_LABELLED_FAMILY_V2_ENUMERATION_CANDIDATE_COMPLETE",
            "completed_labelled_selections": next_id, "declared_labelled_selections": POPULATION,
            "tallies": dict(tallies), "valid_labelled_selections": tallies["VALID_LOCAL_GEOMETRY"],
            "distinct_labelled_valid_graphs": len(valid_by_graph), "isomorphism_classes_claimed": False,
            "part_count": len(part_files), "parts": part_files,
            "coverage": "All9 x-r choices times24 a-b bijections times24 remaining-r assignments in literal lexicographic order.",
            "scope": "Complete local selected-triangle family only. No inducedness, ambient extra-edge or target completion verdict."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("controls", "enumerate"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Fixed17-point labelled local-family geometry and all required hashing/output serialization in one invocation.")
    require(not args.out.exists(), "OUTPUT_FRESH")
    args.out.mkdir(parents=True)
    try:
        inputs = dict(PINS, **{SELF: args.self_sha256, SPEC: args.spec_sha256})
        for path, expected in inputs.items():
            tick(deadline)
            require(sha(ROOT / path) == expected, "INPUT_HASH", path)
        result = controls(args.out, deadline) if args.mode == "controls" else enumerate_family(args.out, deadline)
        outputs = {}
        for path in sorted(args.out.rglob("*")):
            if path.is_file():
                tick(deadline)
                outputs[path.relative_to(ROOT).as_posix()] = sha(path)
        result.update(timestamp=stamp(), producer="/root/structural", verifier=None,
                      independent_approval=False, target_resolution="NONE", target_exclusions=0,
                      mathematical_claim_status="CANDIDATE", command=[sys.executable] + sys.argv,
                      cwd=str(Path.cwd()), python=platform.python_version(),
                      inputs_sha256=inputs, outputs_sha256=outputs, deadline=deadline.status(),
                      automatic_retry=False, ledger_mutations=0, index_mutations=0)
        save(args.out / "summary.json", result)
        tick(deadline)
        return 0
    except Exception as error:
        save(args.out / "failure.json", {"timestamp": stamp(), "stage": getattr(error, "stage", type(error).__name__),
             "detail": getattr(error, "detail", str(error)), "deadline": deadline.status(),
             "independent_approval": False, "target_resolution": "NONE",
             "description": "not completed within the allocated budget" if isinstance(error, SaveStop) else "Failed; preserved prefix is not complete approval."})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
