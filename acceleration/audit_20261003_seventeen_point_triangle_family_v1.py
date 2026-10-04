"""SOURCE_ONLY distinct whole-record checker for the fixed 9*24*24 family.

Structural produces geometry; Native checks artifacts. No producer import,
target-coverage derivation, ambient inducedness, or circuit proof is supplied.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
SOURCE = "acceleration/enumerate_20261003_seventeen_point_triangle_family_v1.py"
SOURCE_SPEC = "acceleration/enumerate_20261003_seventeen_point_triangle_family_v1_spec.md"
SUP = "acceleration/run_compute_command_v2.py"
PINS = {
    SOURCE: "62225a882421fc7a74990b9d4e396379a32ee429e0fd5e778a52e1d24f269495",
    SOURCE_SPEC: "c1a2be6654e2a667f57475d058aa31adea8f3486b09b4bf73fc33344cef83459",
    "acceleration/plan_20261003_seventeen_point_family_author_controls_v1.json": "51a101d5a4e13b6603bfce20e7218fbdfc2c08b86c62cdce9b54e60ada608a87",
    "acceleration/enumerate_20261003_seventeen_point_triangle_family_v1_durability_clarification01.md": "2fc642a2fcc4fd6ffe542f9e15701afe250daaaf1529915b0446d2e8741f3020",
    "acceleration/audit_20261003_unbalanced_twelve_triangle_word_target_family_v1.md": "31d2ff708881c36f2a6271e4d46de5181ba5d7e91377e481f29306b7f97b1d4c",
    "docs/CANDIDATE_20261003_UNBALANCED_TWELVE_TRIANGLE_WORD_TARGET_TYPES_V1.md": "6f26e9f4b989f76de8b5954627ed217a00a2beabf88e8b11f64eb33c34ba209b",
    "docs/CANDIDATE_20261003_SEVENTEEN_POINT_UNBALANCED_TWELVE_TRIANGLE_CIRCUIT_V1.md": "f6f9e883b577d6969eafaac9239c37d637804786a08a6b5e676cebe0208e576b",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "docs/COMPUTE_POLICY.md": "9d3f57e8e36376e71fe5fb2733d19d6c0eacf92c71f763e66224dda95f59e136",
    SUP: "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "acceleration/run_compute_command_v2_spec.md": "33e242b6dc28fa783b29825b76311fdc36d16f5cdf1897ca3b41671cafc1acc1",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
SIGNS = [-1] * 7 + [1] * 5
OLD = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 9], [1, 8, 10],
       [15, 11, 14], [16, 12, 13], [2, 15, 16], [3, 7, 11],
       [4, 8, 12], [5, 9, 13], [6, 10, 14]]
KNOWN51 = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 8], [1, 9, 10],
           [11, 12, 13], [14, 15, 16], [2, 11, 14], [3, 7, 12],
           [4, 9, 15], [5, 8, 16], [6, 10, 13]]
FAMILY_COVERAGE = "All9 x-r choices times24 a-b bijections times24 remaining-r assignments in literal lexicographic order."
PREFIX_COVERAGE = "Exact labelled prefix [0,next_proposal_id), no resumed or omitted cases."
STATUS = "INDEPENDENT_SEVENTEEN_POINT_LABELLED_FAMILY_V1_"


class Veto(ValueError):
    def __init__(self, stage, detail=None):
        self.stage, self.detail = stage, detail
        super().__init__(stage)


def need(value, stage, detail=None):
    if not value:
        raise Veto(stage, detail)


def exact(value, wanted, stage):
    need(type(value) is type(wanted), stage)
    if type(wanted) is dict:
        need(value.keys() == wanted.keys(), stage)
        for key in wanted:
            exact(value[key], wanted[key], stage)
    elif type(wanted) in (list, tuple):
        need(len(value) == len(wanted), stage)
        for item, expected in zip(value, wanted):
            exact(item, expected, stage)
    else:
        need(value == wanted, stage)


def tick(deadline):
    state = deadline.status()
    need(not state["stop_required"] and state["remaining_seconds"] > 20, "SAVE_RESERVE")


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, "JSON_BYTES")
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, "JSON_DUPLICATE")
            result[name] = value
        return result
    def nonfinite(_):
        raise Veto("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


def digest(path, deadline):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            tick(deadline)
            result.update(chunk)
    tick(deadline)
    return result.hexdigest()


def read(path, deadline):
    tick(deadline)
    result = strict_json(path.read_bytes())
    tick(deadline)
    return result


def save(path, value, deadline):
    tick(deadline)
    data = (json.dumps(value, allow_nan=False, indent=2) + "\n").encode("utf8")
    tick(deadline)
    with path.open("xb") as stream:
        for start in range(0, len(data), 1024 * 1024):
            stream.write(data[start:start + 1024 * 1024])
            tick(deadline)
    tick(deadline)


def unrank_four(index, values):
    """Factoradic selection, not the producer's permutations-table decoder."""
    need(type(index) is int and 0 <= index < 24, "PERMUTATION_INDEX")
    pool, result = list(values), []
    need(len(pool) == 4 and len(set(pool)) == 4, "PERMUTATION_VALUES")
    for length in (4, 3, 2, 1):
        position, index = divmod(index, math.factorial(length - 1))
        result.append(pool.pop(position))
    return result


def rank_four(values, universe):
    pool, result = list(universe), 0
    for value in values:
        need(value in pool, "PERMUTATION_VALUES")
        result += pool.index(value) * math.factorial(len(pool) - 1)
        pool.remove(value)
    need(not pool, "PERMUTATION_VALUES")
    return result


def ordinal(pid):
    need(type(pid) is int, "PROPOSAL_ID_TYPE")
    need(0 <= pid < 5184, "PROPOSAL_ID_RANGE")
    choice, tail = divmod(pid, 576)
    left, right = divmod(choice, 3)
    b_index, r_index = divmod(tail, 24)
    role = dict(x_left_choice=left, x_right_choice=right,
                ab_permutation_index=b_index, r_permutation_index=r_index)
    selected_r = (11 + left, 14 + right)
    b = unrank_four(b_index, range(7, 11))
    r = unrank_four(r_index, [point for point in range(11, 17) if point not in selected_r])
    negatives = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 8], [1, 9, 10],
                 list(range(11, 14)), list(range(14, 17))]
    positives = [[2, *selected_r]] + [[a, bv, rv] for a, bv, rv in zip(range(3, 7), b, r)]
    return role, negatives + positives


def neighborhood(rows):
    neighbors = [set() for _ in range(17)]
    for row in rows:
        for u in row:
            neighbors[u].update(v for v in row if v != u)
    return neighbors


def geometry(rows):
    neighbors = neighborhood(rows)
    matrix = [[int(v in neighbors[u]) for v in range(17)] for u in range(17)]
    cn = [[len(neighbors[u] & neighbors[v]) for v in range(17)] for u in range(17)]
    triangles = [[u, v, w] for u in range(17) for v in range(u + 1, 17)
                 for w in range(v + 1, 17) if v in neighbors[u] and w in neighbors[u] and w in neighbors[v]]
    return matrix, cn, triangles


def caps(matrix):
    need(type(matrix) is list and len(matrix) == 17 and all(type(row) is list and len(row) == 17 for row in matrix), "MATRIX_SHAPE")
    need(all(type(value) is int for row in matrix for value in row), "MATRIX_TYPES")
    need(all(value in (0, 1) for row in matrix for value in row), "MATRIX_BINARY")
    need(all(matrix[u][u] == 0 for u in range(17)), "MATRIX_DIAGONAL")
    need(all(matrix[u][v] == matrix[v][u] for u in range(17) for v in range(u)), "MATRIX_SYMMETRY")
    sets = [{v for v in range(17) if matrix[u][v]} for u in range(17)]
    cn = [[len(sets[u] & sets[v]) for v in range(17)] for u in range(17)]
    for edge in (True, False):
        for u in range(17):
            for v in range(u + 1, 17):
                if bool(matrix[u][v]) is edge:
                    need(cn[u][v] == 1 if edge else cn[u][v] <= 2,
                         "EDGE_CN" if edge else "NONEDGE_CN", [u, v, cn[u][v]])
    return cn


def local_word(rows, signs):
    need(type(rows) is list and len(rows) == 12 and all(type(row) is list and len(row) == 3 for row in rows), "ROW_SHAPE")
    need(all(type(point) is int for row in rows for point in row), "ROW_TYPES")
    need(all(0 <= point < 17 for row in rows for point in row), "ROW_RANGE")
    need(all(len(set(row)) == 3 for row in rows), "ROW_DISTINCT_POINTS")
    canonical = [tuple(sorted(row)) for row in rows]
    need(len(set(canonical)) == 12, "DISTINCT_ROWS")
    used_pairs = set()
    for row in canonical:
        for pair in ((row[0], row[1]), (row[0], row[2]), (row[1], row[2])):
            need(pair not in used_pairs, "PAIR_LINEARITY")
            used_pairs.add(pair)
    need(type(signs) is list and len(signs) == 12, "COEFFICIENT_POPULATION")
    need(all(type(value) is int for value in signs), "COEFFICIENT_TYPES")
    need(all(value in (-1, 1) for value in signs), "COEFFICIENT_DOMAIN")
    need(signs.count(-1) == 7 and signs.count(1) == 5, "SIGN_COUNTS")
    incidence, selected = [0] * 17, [0] * 17
    for row, sign in zip(rows, signs):
        for point in row:
            incidence[point] += sign
            selected[point] += 1
    need(all(value % 3 == 0 for value in incidence), "GF3_WORD")
    need(selected.count(3) == 2 and selected.count(2) == 15, "SELECTED_DEGREES")
    matrix, cn, triangles = geometry(rows)
    exact(caps(matrix), cn, "NEIGHBOR_PRODUCT_DISAGREEMENT")
    need(triangles == [list(row) for row in sorted(canonical)], "ACTUAL_TRIANGLE_FAMILY")
    return matrix, cn, selected, incidence, triangles


def expected_record(pid):
    role, rows = ordinal(pid)
    matrix, cn, triangles = geometry(rows)
    try:
        local_word(rows, SIGNS)
        stage, detail = None, None
    except Veto as error:
        stage, detail = error.stage, error.detail
    strings = ["".join(map(str, row)) for row in matrix]
    return dict(proposal_id=pid, role=role, negative_centers=[0, 1], triples=rows,
                coefficients=SIGNS.copy(), adjacency_rows=strings, common_neighbors=cn,
                selected_degrees=[sum(point in row for row in rows) for point in range(17)],
                graph_degrees=[len(values) for values in neighborhood(rows)], actual_triangles=triangles,
                integer_incidence_sum=[sum(sign for row, sign in zip(rows, SIGNS) if point in row) for point in range(17)],
                coefficient_sum_mod3=1, valid_local_geometry=stage is None, first_veto=stage,
                veto_detail=detail, labelled_graph_sha256=hashlib.sha256(("\n".join(strings) + "\n").encode("ascii")).hexdigest())


def check_record(raw, pid):
    expected = expected_record(pid)
    need(type(raw) is dict and raw.keys() == expected.keys(), "RECORD_KEYS")
    for field in expected:
        exact(raw[field], expected[field], "RECORD:" + field)
    return expected


def tally(records):
    counts, groups, matrices = {}, {}, {}
    for item in records:
        stage = item["first_veto"] or "VALID_LOCAL_GEOMETRY"
        counts[stage] = counts.get(stage, 0) + 1
        if item["valid_local_geometry"]:
            key = item["labelled_graph_sha256"]
            need(key not in matrices or matrices[key] == item["adjacency_rows"], "GRAPH_HASH_COLLISION")
            matrices[key] = item["adjacency_rows"]
            groups.setdefault(key, []).append(item["proposal_id"])
    return counts, groups


def check_part(raw, start, stop, deadline):
    need(type(raw) is dict and raw.keys() == {"schema", "start", "stop", "records"}, "PART_KEYS")
    exact(raw["schema"], "SEVENTEEN_POINT_LABELLED_FAMILY_PART_V1", "PART_SCHEMA")
    exact(raw["start"], start, "PART_START")
    exact(raw["stop"], stop, "PART_STOP")
    need(type(raw["records"]) is list and len(raw["records"]) == stop - start, "PART_POPULATION")
    checked = []
    for pid, record in zip(range(start, stop), raw["records"]):
        tick(deadline)
        checked.append(check_record(record, pid))
    return checked


def check_checkpoint(raw, next_id, counts, groups, parts):
    expected = dict(schema="SEVENTEEN_POINT_LABELLED_FAMILY_CHECKPOINT_V1", next_proposal_id=next_id,
                    tallies=counts, valid_graphs=groups, parts=parts, coverage=PREFIX_COVERAGE)
    need(type(raw) is dict and raw.keys() == expected.keys(), "CHECKPOINT_KEYS")
    for field in expected:
        exact(raw[field], expected[field], "CHECKPOINT:" + field)


def positive_packets():
    def complete(name, rows):
        matrix, cn, selected, incidence, triangles = local_word(rows, SIGNS)
        return dict(case=name, rows=rows, signs=SIGNS, adjacency=matrix, common_neighbors=cn,
                    selected_degrees=selected, integer_incidence_sum=incidence, actual_triangles=triangles)
    role51, rows51 = ordinal(51)
    exact(rows51, KNOWN51, "HAND_51_ROWS")
    role_last, rows_last = ordinal(5183)
    exact(rows_last[7:], [[2, 13, 16], [3, 10, 15], [4, 9, 14], [5, 8, 12], [6, 7, 11]], "HAND_LAST_ROWS")
    exact(role_last, dict(x_left_choice=2, x_right_choice=2, ab_permutation_index=23, r_permutation_index=23), "HAND_LAST_ROLE")
    triangle = [[int(u != v and u < 3 and v < 3) for v in range(17)] for u in range(17)]
    return [complete("literal_old17", OLD), complete("literal_mapped51", KNOWN51),
            dict(case="decoder51", proposal_id=51, role=role51, rows=rows51),
            dict(case="decoder_last", proposal_id=5183, role=role_last, rows=rows_last),
            dict(case="isolated_triangle_caps", adjacency=triangle, common_neighbors=caps(triangle))]


def producer_negative_cases():
    cases = [("id_" + repr(value), stage, value, lambda v=value: ordinal(v))
             for value, stage in ((-1, "PROPOSAL_ID_RANGE"), (5184, "PROPOSAL_ID_RANGE"),
                                  (False, "PROPOSAL_ID_TYPE"), (1.0, "PROPOSAL_ID_TYPE"))]
    row_cases = [("missing_row", "ROW_SHAPE", OLD[:-1]), ("row_object", "ROW_SHAPE", [{"points": OLD[0]}] + OLD[1:]),
                 ("bool_point", "ROW_TYPES", [[False, 1, 2]] + OLD[1:]), ("float_point", "ROW_TYPES", [[0.0, 1, 2]] + OLD[1:]),
                 ("outside_point", "ROW_RANGE", [[17, 1, 2]] + OLD[1:]), ("repeated_point", "ROW_DISTINCT_POINTS", [[0, 0, 2]] + OLD[1:]),
                 ("duplicate_row", "DISTINCT_ROWS", OLD[:-1] + [OLD[0]]), ("reused_pair", "PAIR_LINEARITY", OLD[:-1] + [[0, 1, 16]])]
    cases += [(name, stage, damage, lambda rows=damage: local_word(rows, SIGNS)) for name, stage, damage in row_cases]
    sign_cases = [("missing_coefficient", "COEFFICIENT_POPULATION", SIGNS[:-1]),
                  ("bool_coefficient", "COEFFICIENT_TYPES", [False] + SIGNS[1:]),
                  ("float_coefficient", "COEFFICIENT_TYPES", [-1.0] + SIGNS[1:]),
                  ("zero_coefficient", "COEFFICIENT_DOMAIN", [0] + SIGNS[1:]),
                  ("all_positive", "SIGN_COUNTS", [1] * 12),
                  ("opposite_sign_exchange", "GF3_WORD", [1] + SIGNS[1:7] + [-1] + SIGNS[8:])]
    cases += [(name, stage, damage, lambda signs=damage: local_word(OLD, signs)) for name, stage, damage in sign_cases]
    triangle = positive_packets()[-1]["adjacency"]
    matrix_cases = [("short_matrix", "MATRIX_SHAPE", triangle[:-1])]
    for name, stage, u, v, value in (("bool_zero", "MATRIX_TYPES", 3, 3, False),
                                    ("float_one", "MATRIX_TYPES", 0, 1, 1.0), ("nonbinary", "MATRIX_BINARY", 0, 1, 2),
                                    ("loop", "MATRIX_DIAGONAL", 3, 3, 1), ("asymmetry", "MATRIX_SYMMETRY", 0, 1, 0)):
        damage = deepcopy(triangle)
        damage[u][v] = value
        matrix_cases.append((name, stage, damage))
    matrix_cases += [("edge_two_CN", "EDGE_CN", [[int(u != v and u < 4 and v < 4) for v in range(17)] for u in range(17)]),
                     ("nonedge_three_CN", "NONEDGE_CN", [[int((u < 2 and 2 <= v < 5) or (v < 2 and 2 <= u < 5)) for v in range(17)] for u in range(17)])]
    return cases + [(name, stage, damage, lambda matrix=damage: caps(matrix)) for name, stage, damage in matrix_cases]


def stage_of(action):
    try:
        action()
    except Veto as error:
        return error.stage
    return "ACCEPTED_CORRUPTION"


def control_table():
    result = []
    for name, wanted, damage, action in producer_negative_cases():
        actual = stage_of(action)
        exact(actual, wanted, "INDEPENDENT_CONTROL:" + name)
        result.append(dict(case=name, expected=wanted, actual=actual, damage=damage))
    exact(len(result), 26, "INDEPENDENT_AUTHOR_CONTROL_COUNT")
    return result


def profile(plan, manifest, terminal, mode, producer_root):
    need(type(plan) is dict and type(plan.get("command")) is list and type(plan.get("child_command")) is list
         and type(plan.get("worker_command")) is list and type(plan.get("allocation")) is dict, "PLAN_FIELDS")
    command, child, worker = plan["command"], plan["child_command"], plan["worker_command"]
    python = str(ROOT / "build/research-venv/Scripts/python.exe")
    uv = str(Path.home() / ".local/bin/uv.exe")
    need(len(command) == 36 and len(child) == 20 and len(worker) == 12, "PLAN_WORDS")
    exact(command[:3], [python, "-B", str(ROOT / SUP)], "PLAN_SUPERVISOR")
    exact(command[-20:], child, "PLAN_CHILD")
    exact(command[-21], "--", "PLAN_BOUNDARY")
    exact(child[:10], [uv, "run", "--locked", "--offline", "--cache-dir", str(ROOT / "build/uv-cache"),
                       "--python", python, python, "-B"], "PLAN_UV_PREFIX")
    exact(child[8:], worker, "PLAN_WORKER")
    exact(worker[:4], [python, "-B", str(ROOT / SOURCE), mode], "PLAN_WORKER_PREFIX")
    exact(worker[4:6], ["--out", str(producer_root)], "PLAN_WORKER_OUTPUT")
    allocation = plan["allocation"]
    seconds, shutdown = allocation.get("outer_seconds"), allocation.get("shutdown_seconds")
    worker_seconds = allocation.get("worker_seconds")
    need(all(type(value) is int and value > 0 for value in (seconds, shutdown, worker_seconds)), "PLAN_ALLOCATION")
    need(seconds >= worker_seconds + shutdown and worker_seconds > 20, "PLAN_ALLOCATION")
    exact(command[3:7], ["--seconds", str(seconds), "--shutdown-reserve-seconds", str(shutdown)], "PLAN_OUTER_SECONDS")
    exact(worker[6:], ["--seconds", str(worker_seconds), "--self-sha256", PINS[SOURCE], "--spec-sha256", PINS[SOURCE_SPEC]], "PLAN_WORKER_SCOPE")
    need(type(manifest) is dict, "OUTER_OBJECT")
    exact(manifest.get("source_sha256"), PINS[SUP], "OUTER_SOURCE")
    exact(manifest.get("cwd"), str(ROOT), "OUTER_CWD")
    exact(manifest.get("command"), child, "OUTER_CHILD")
    exact(manifest.get("seconds"), float(seconds), "OUTER_SECONDS")
    exact(manifest.get("shutdown_reserve_seconds"), float(shutdown), "OUTER_SHUTDOWN")
    exact(manifest.get("automatic_retry"), False, "OUTER_RETRY")
    exact(manifest.get("cumulative_across_commands"), False, "OUTER_CUMULATIVE")
    need(type(terminal) is dict and terminal.get("invocation_id") == manifest.get("invocation_id"), "TERMINAL_INVOCATION")
    exact(terminal.get("status"), "COMMAND_COMPLETED_VERIFICATION_PENDING", "TERMINAL_STATUS")
    exact(terminal.get("command_exit_code"), 0, "TERMINAL_EXIT")
    cleanup = terminal.get("cleanup")
    need(type(cleanup) is dict, "TERMINAL_CLEANUP")
    for name, wanted in (("reaped", True), ("job_active_zero_observed", True), ("cleanup_errors", []), ("actual_exit_code", 0)):
        exact(cleanup.get(name), wanted, "TERMINAL:" + name)
    return [python, *worker[2:]]


def synthetic_profile(mode, root):
    python, uv = str(ROOT / "build/research-venv/Scripts/python.exe"), str(Path.home() / ".local/bin/uv.exe")
    worker_seconds, outer_seconds, shutdown = (40, 60, 10) if mode == "controls" else (150, 180, 20)
    worker = [python, "-B", str(ROOT / SOURCE), mode, "--out", str(root), "--seconds", str(worker_seconds),
              "--self-sha256", PINS[SOURCE], "--spec-sha256", PINS[SOURCE_SPEC]]
    child = [uv, "run", "--locked", "--offline", "--cache-dir", str(ROOT / "build/uv-cache"), "--python", python] + worker
    command = [python, "-B", str(ROOT / SUP), "--seconds", str(outer_seconds), "--shutdown-reserve-seconds", str(shutdown),
               "--allocation-reason", "synthetic", "--success-criterion", "synthetic", "--verification-criterion", "synthetic",
               "--out", str(root.parent / "synthetic_supervisor"), "--"] + child
    plan = dict(command=command, child_command=child, worker_command=worker,
                allocation=dict(outer_seconds=outer_seconds, worker_seconds=worker_seconds, shutdown_seconds=shutdown))
    manifest = dict(source_sha256=PINS[SUP], cwd=str(ROOT), command=child, seconds=float(outer_seconds),
                    shutdown_reserve_seconds=float(shutdown), automatic_retry=False, cumulative_across_commands=False, invocation_id="synthetic")
    terminal = dict(invocation_id="synthetic", status="COMMAND_COMPLETED_VERIFICATION_PENDING", command_exit_code=0,
                    cleanup=dict(reaped=True, job_active_zero_observed=True, cleanup_errors=[], actual_exit_code=0))
    return plan, manifest, terminal


def own_controls(out, deadline):
    positive = positive_packets()
    save(out / "known_positive_packets.json", positive, deadline)
    table = control_table()
    save(out / "independent_author_counterparts.json", table, deadline)
    permutations = [unrank_four(index, range(4)) for index in range(24)]
    exact(len({tuple(values) for values in permutations}), 24, "PERMUTATION_BIJECTION")
    exact([rank_four(values, range(4)) for values in permutations], list(range(24)), "PERMUTATION_ROUNDTRIP")
    save(out / "factoradic_bijection.json", permutations, deadline)
    records = [expected_record(pid) for pid in range(4)]
    mini = dict(schema="SEVENTEEN_POINT_LABELLED_FAMILY_PART_V1", start=0, stop=4, records=records)
    check_part(mini, 0, 4, deadline)
    counts, groups = tally(records)
    parts = [dict(path="part_000.json", sha256="a" * 64, population=4)]
    cp = dict(schema="SEVENTEEN_POINT_LABELLED_FAMILY_CHECKPOINT_V1", next_proposal_id=4,
              tallies=counts, valid_graphs=groups, parts=parts, coverage=PREFIX_COVERAGE)
    check_checkpoint(cp, 4, counts, groups, parts)
    save(out / "synthetic_part.json", mini, deadline)
    save(out / "synthetic_checkpoint.json", cp, deadline)
    negatives = [dict(case="author_" + item["case"], expected_stage=item["expected"], actual_stage=item["actual"]) for item in table]
    def reject(name, wanted, raw, action):
        tick(deadline)
        save(out / ("corrupt_" + name + ".json"), raw, deadline)
        actual = stage_of(action)
        exact(actual, wanted, "OWN_STAGE:" + name)
        negatives.append(dict(case=name, expected_stage=wanted, actual_stage=actual))
    base = expected_record(51)
    corruptions = {
        "proposal_id": lambda p: p.update(proposal_id=True),
        "role": lambda p: p["role"].update(x_left_choice=False),
        "negative_centers": lambda p: p["negative_centers"].__setitem__(0, False),
        "triples": lambda p: p["triples"].reverse(),
        "coefficients": lambda p: p["coefficients"].__setitem__(0, 1),
        "adjacency_rows": lambda p: p["adjacency_rows"].__setitem__(0, "1" + p["adjacency_rows"][0][1:]),
        "common_neighbors": lambda p: p["common_neighbors"][0].__setitem__(0, 0),
        "selected_degrees": lambda p: p["selected_degrees"].__setitem__(0, 0),
        "graph_degrees": lambda p: p["graph_degrees"].__setitem__(0, False),
        "actual_triangles": lambda p: p["actual_triangles"].pop(),
        "integer_incidence_sum": lambda p: p["integer_incidence_sum"].__setitem__(0, -2),
        "coefficient_sum_mod3": lambda p: p.update(coefficient_sum_mod3=True),
        "valid_local_geometry": lambda p: p.update(valid_local_geometry=1),
        "first_veto": lambda p: p.update(first_veto="WRONG"),
        "veto_detail": lambda p: p.update(veto_detail=[0, 1, 9]),
        "labelled_graph_sha256": lambda p: p.update(labelled_graph_sha256="0" * 64),
    }
    for field, mutate in corruptions.items():
        raw = deepcopy(base); mutate(raw)
        reject("record_" + field, "RECORD:" + field, raw, lambda r=raw: check_record(r, 51))
    late = expected_record(5183); late["proposal_id"] = 51
    reject("late_ordinal_5183", "RECORD:proposal_id", late, lambda: check_record(late, 5183))
    for value, kind in ((0, "bool"), (0, "float"), (1, "bool")):
        raw = deepcopy(base)
        u, v = next((u, v) for u in range(17) for v in range(u + 1, 17) if raw["common_neighbors"][u][v] == value)
        raw["common_neighbors"][u][v] = bool(value) if kind == "bool" else float(value)
        reject("cache_" + str(value) + "_" + kind, "RECORD:common_neighbors", raw, lambda r=raw: check_record(r, 51))
    part_cases = [("schema", "PART_SCHEMA", lambda p: p.update(schema="WRONG")),
                  ("start", "PART_START", lambda p: p.update(start=False)), ("stop", "PART_STOP", lambda p: p.update(stop=4.0)),
                  ("drop", "PART_POPULATION", lambda p: p["records"].pop()),
                  ("duplicate", "RECORD:proposal_id", lambda p: p["records"].__setitem__(1, deepcopy(p["records"][0]))),
                  ("shift", "RECORD:proposal_id", lambda p: p["records"].reverse())]
    for name, wanted, mutate in part_cases:
        raw = deepcopy(mini); mutate(raw)
        reject("part_" + name, wanted, raw, lambda r=raw: check_part(r, 0, 4, deadline))
    for field, replacement in (("schema", "WRONG"), ("next_proposal_id", 4.0), ("tallies", {"VALID_LOCAL_GEOMETRY": False}),
                               ("valid_graphs", {"0" * 64: [51]}), ("parts", []), ("coverage", "WRONG")):
        raw = deepcopy(cp); raw[field] = replacement
        reject("checkpoint_" + field, "CHECKPOINT:" + field, raw, lambda r=raw: check_checkpoint(r, 4, counts, groups, parts))
    raw = deepcopy(cp); raw.pop("parts")
    reject("checkpoint_missing", "CHECKPOINT_KEYS", raw, lambda: check_checkpoint(raw, 4, counts, groups, parts))
    original_groups = {base["labelled_graph_sha256"]: [51]}
    for name, raw in (("missing", {}), ("float_id", {base["labelled_graph_sha256"]: [51.0]}),
                      ("duplicate", {base["labelled_graph_sha256"]: [51, 51]}), ("wrong_hash", {"0" * 64: [51]})):
        reject("group_" + name, "GRAPH_GROUPS", raw, lambda r=raw: exact(r, original_groups, "GRAPH_GROUPS"))
    root = out / "synthetic_producer"
    cal_profile = synthetic_profile("controls", root)
    full_profile = synthetic_profile("enumerate", root)
    profile(*cal_profile, "controls", root); profile(*full_profile, "enumerate", root)
    save(out / "synthetic_runtime_profiles.json", dict(controls=cal_profile, enumerate=full_profile), deadline)
    runtime_cases = [("source", "OUTER_SOURCE", 1, lambda p: p.update(source_sha256="0" * 64)),
                     ("cwd", "OUTER_CWD", 1, lambda p: p.update(cwd="WRONG")),
                     ("child", "OUTER_CHILD", 1, lambda p: p["command"].pop()),
                     ("seconds_bool", "OUTER_SECONDS", 1, lambda p: p.update(seconds=True)),
                     ("shutdown_bool", "OUTER_SHUTDOWN", 1, lambda p: p.update(shutdown_reserve_seconds=True)),
                     ("retry", "OUTER_RETRY", 1, lambda p: p.update(automatic_retry=True)),
                     ("cumulative", "OUTER_CUMULATIVE", 1, lambda p: p.update(cumulative_across_commands=True)),
                     ("status", "TERMINAL_STATUS", 2, lambda p: p.update(status="FAILED")),
                     ("exit_bool", "TERMINAL_EXIT", 2, lambda p: p.update(command_exit_code=False)),
                     ("exit_float", "TERMINAL_EXIT", 2, lambda p: p.update(command_exit_code=0.0)),
                     ("reaped", "TERMINAL:reaped", 2, lambda p: p["cleanup"].update(reaped=False)),
                     ("empty", "TERMINAL:job_active_zero_observed", 2, lambda p: p["cleanup"].update(job_active_zero_observed=False)),
                     ("errors", "TERMINAL:cleanup_errors", 2, lambda p: p["cleanup"].update(cleanup_errors=["WRONG"])),
                     ("actual_exit_bool", "TERMINAL:actual_exit_code", 2, lambda p: p["cleanup"].update(actual_exit_code=False)),
                     ("worker_prefix", "PLAN_WORKER", 0, lambda p: p["worker_command"].__setitem__(1, "")),
                     ("worker_mode", "PLAN_WORKER_PREFIX", 0, lambda p: (p["worker_command"].__setitem__(3, "controls"), p["child_command"].__setitem__(11, "controls"), p["command"].__setitem__(27, "controls")))]
    for name, wanted, which, mutate in runtime_cases:
        raw = deepcopy(full_profile); mutate(raw[which])
        reject("runtime_" + name, wanted, raw, lambda r=raw: profile(*r, "enumerate", root))
    for name, raw, wanted in (("duplicate_JSON", b'{"a":0,"a":1}', "JSON_DUPLICATE"),
                              ("nonfinite_JSON", b'{"a":NaN}', "JSON_NONFINITE")):
        tick(deadline); (out / ("corrupt_" + name + ".json")).write_bytes(raw)
        actual = stage_of(lambda data=raw: strict_json(data)); exact(actual, wanted, "OWN_JSON")
        negatives.append(dict(case=name, expected_stage=wanted, actual_stage=actual))
    exact(len(negatives), 81, "OWN_NEGATIVE_POPULATION")
    save(out / "own_negative_records.json", negatives, deadline)
    return dict(positive_cases=8, strict_negative_cases=81, independent_author_counterparts=26,
                exact_record_fields=16, factoradic_orders=24, actual_family_enumerated=False,
                producer_outputs_read=False, actual_target_input_read=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("calibrate", "producer-controls", "full"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--calibration-sha256")
    parser.add_argument("--producer-controls", type=Path)
    parser.add_argument("--producer-controls-sha256")
    parser.add_argument("--producer-root", type=Path)
    parser.add_argument("--producer-summary-sha256")
    parser.add_argument("--producer-plan", type=Path)
    parser.add_argument("--producer-plan-sha256")
    parser.add_argument("--supervision-out", type=Path)
    parser.add_argument("--supervisor-manifest-sha256")
    parser.add_argument("--supervisor-summary-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Distinct complete fixed5184 local family checker; authentication/matrices/parts/groups/save inside one inclusive worker")
    out = args.out.resolve()
    need(out.is_relative_to(ROOT / "acceleration/results") and not out.exists(), "FRESH_OUTPUT")
    out.mkdir(parents=True)
    inputs = {}
    def pin(path, wanted=None):
        path = Path(path).resolve()
        need(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink(), "INPUT_FILE")
        name = path.relative_to(ROOT).as_posix()
        need(name != "CLAIMS.yaml" and not name.startswith(".git/"), "MUTABLE_INPUT")
        observed = digest(path, deadline)
        need(wanted is None or type(wanted) is str and re.fullmatch(r"[0-9a-f]{64}", wanted) and observed == wanted, "INPUT_SHA:" + name)
        need(name not in inputs or inputs[name] == observed, "INPUT_CHANGED")
        inputs[name] = observed
        return path
    def gate(path, identity, expected_status, expected_scope):
        need(path is not None and identity is not None, "GENUINE_GATE_REQUIRED")
        value = read(pin(path, identity), deadline)
        need(type(value) is dict and value.get("status") == STATUS + expected_status
             and value.get("producer") == "/root/structural" and value.get("verifier") == "/root/native_driver"
             and value.get("method") == "independent_artifact_check" and value.get("target_resolution") == "NONE", "GATE_HEADER")
        for field, wanted in expected_scope.items():
            exact(value.get("checked_scope", {}).get(field), wanted, "GATE_SCOPE:" + field)
        for mapping in (value.get("inputs_sha256"), value.get("outputs_sha256")):
            need(type(mapping) is dict and mapping, "GATE_MAP")
            for name, sha in mapping.items():
                pin(ROOT / name, sha)
        need(all(value["inputs_sha256"].get(name) == sha for name, sha in source_pins.items()), "GATE_SOFTWARE")
        return value
    try:
        for name, sha in PINS.items():
            pin(ROOT / name, sha)
        pin(SELF); pin(SPEC)
        source_pins = inputs.copy()
        if args.mode == "calibrate":
            need(all(value is None for name, value in vars(args).items() if name not in ("mode", "seconds", "out")), "CALIBRATION_NO_ACTUAL_PACKET")
            result = own_controls(out, deadline)
            status = STATUS + "OWN_CALIBRATION_PASS"
        else:
            gate(args.calibration, args.calibration_sha256, "OWN_CALIBRATION_PASS",
                 dict(positive_cases=8, strict_negative_cases=81, independent_author_counterparts=26,
                      actual_family_enumerated=False, producer_outputs_read=False, actual_target_input_read=False))
            if args.mode == "full":
                gate(args.producer_controls, args.producer_controls_sha256, "AUTHOR_CONTROLS_PASS",
                     dict(positive_controls=5, strict_negative_controls=26, actual_family_enumerated=False, actual_target_input_read=False))
            else:
                need(args.producer_controls is None and args.producer_controls_sha256 is None, "AUTHOR_CONTROLS_NO_SELF_GATE")
            need(args.producer_root is not None and args.producer_summary_sha256 is not None and args.producer_plan is not None
                 and args.producer_plan_sha256 is not None and args.supervision_out is not None
                 and args.supervisor_manifest_sha256 is not None and args.supervisor_summary_sha256 is not None, "ACTUAL_OPTIONS")
            root = args.producer_root.resolve()
            need(root.is_relative_to(ROOT / "acceleration/results") and root.is_dir() and not root.is_symlink(), "PRODUCER_ROOT")
            summary = read(pin(root / "summary.json", args.producer_summary_sha256), deadline)
            plan = read(pin(args.producer_plan, args.producer_plan_sha256), deadline)
            outer = read(pin(args.supervision_out / "manifest.json", args.supervisor_manifest_sha256), deadline)
            terminal = read(pin(args.supervision_out / "summary.json", args.supervisor_summary_sha256), deadline)
            mode = "controls" if args.mode == "producer-controls" else "enumerate"
            expected_command = profile(plan, outer, terminal, mode, root)
            exact(summary.get("command"), expected_command, "PRODUCER_COMMAND")
            for name, wanted in (("producer", "/root/structural"), ("verifier", None), ("independent_approval", False),
                                 ("target_resolution", "NONE"), ("target_exclusions", 0), ("mathematical_claim_status", "CANDIDATE"),
                                 ("cwd", str(ROOT)), ("automatic_retry", False), ("ledger_mutations", 0), ("index_mutations", 0)):
                exact(summary.get(name), wanted, "PRODUCER_FIELD:" + name)
            expected_software = {name: sha for name, sha in PINS.items() if name in (SOURCE, SOURCE_SPEC) or name in (
                "docs/CANDIDATE_20261003_UNBALANCED_TWELVE_TRIANGLE_WORD_TARGET_TYPES_V1.md",
                "docs/CANDIDATE_20261003_SEVENTEEN_POINT_UNBALANCED_TWELVE_TRIANGLE_CIRCUIT_V1.md",
                "acceleration/audit_20261003_unbalanced_twelve_triangle_word_target_family_v1.md",
                "acceleration/command_deadline.py", "docs/COMPUTE_POLICY.md")}
            exact(summary.get("inputs_sha256"), expected_software, "PRODUCER_INPUT_MAP")
            actual_files = {path.relative_to(root).as_posix(): path for path in root.rglob("*") if path.is_file()}
            need(all(not path.is_symlink() for path in root.rglob("*")), "PRODUCER_SYMLINK")
            actual_payloads = {path.relative_to(ROOT).as_posix(): digest(path, deadline) for name, path in sorted(actual_files.items()) if name != "summary.json"}
            exact(summary.get("outputs_sha256"), actual_payloads, "PRODUCER_OUTPUT_MAP")
            for name, sha in actual_payloads.items():
                pin(ROOT / name, sha)
            if mode == "controls":
                exact(set(actual_files), {"summary.json", "controls.json", "positive_fixtures.json"}, "AUTHOR_EXACT_FILES")
                exact(summary.get("status"), "SEVENTEEN_POINT_LABELLED_FAMILY_V1_AUTHOR_CONTROLS_PASS", "AUTHOR_STATUS")
                exact(read(root / "positive_fixtures.json", deadline), positive_packets(), "AUTHOR_POSITIVES")
                expected = control_table()
                exact(read(root / "controls.json", deadline), expected, "AUTHOR_CONTROL_TABLE")
                for field, wanted in (("positive_controls", 5), ("strict_negative_controls", 26), ("actual_family_enumerated", False),
                                      ("actual_target_input_read", False), ("literal_known_valid_rows", dict(old17=OLD, mapped_id51=KNOWN51))):
                    exact(summary.get(field), wanted, "AUTHOR_SUMMARY:" + field)
                save(out / "independent_author_controls.json", expected, deadline)
                result = dict(positive_controls=5, strict_negative_controls=26, complete_known_fixture_products=3 * 289,
                              actual_family_enumerated=False, actual_target_input_read=False)
                status = STATUS + "AUTHOR_CONTROLS_PASS"
            else:
                exact(summary.get("status"), "SEVENTEEN_POINT_LABELLED_FAMILY_V1_ENUMERATION_CANDIDATE_COMPLETE", "FAMILY_STATUS")
                records, part_receipts, valid_matrices = [], [], {}
                counts, groups = {}, {}
                expected_paths = {"summary.json", "valid_graph_groups.json"}
                for number in range(41):
                    tick(deadline)
                    start, stop = number * 128, min((number + 1) * 128, 5184)
                    part_name, cp_name = "part_%03d.json" % number, "checkpoint_%03d.json" % number
                    expected_paths.update((part_name, cp_name))
                    need(part_name in actual_files and cp_name in actual_files, "FAMILY_PART_OR_CHECKPOINT_MISSING")
                    block = check_part(read(actual_files[part_name], deadline), start, stop, deadline)
                    for item in block:
                        stage = item["first_veto"] or "VALID_LOCAL_GEOMETRY"
                        counts[stage] = counts.get(stage, 0) + 1
                        if item["valid_local_geometry"]:
                            key = item["labelled_graph_sha256"]
                            need(key not in valid_matrices or valid_matrices[key] == item["adjacency_rows"], "GRAPH_HASH_COLLISION")
                            valid_matrices[key] = item["adjacency_rows"]
                            groups.setdefault(key, []).append(item["proposal_id"])
                            valid_name = "valid/case_%04d.json" % item["proposal_id"]
                            expected_paths.add(valid_name)
                            need(valid_name in actual_files, "VALID_RAW_MISSING")
                            exact(read(actual_files[valid_name], deadline), item, "VALID_RAW_RECORD")
                    records.extend(block)
                    part_receipts.append(dict(path=part_name, sha256=actual_payloads[actual_files[part_name].relative_to(ROOT).as_posix()], population=stop - start))
                    check_checkpoint(read(actual_files[cp_name], deadline), stop, counts, groups, part_receipts)
                    # Source prints valid count after each completed128 part; its Counter lookup retains an explicit zero.
                    if stop - start == 128:
                        counts.setdefault("VALID_LOCAL_GEOMETRY", 0)
                    print(json.dumps(dict(checked=stop, population=5184, complete_parts=number + 1)), flush=True)
                exact(set(actual_files), expected_paths, "FAMILY_EXACT_FILES")
                exact(read(root / "valid_graph_groups.json", deadline), groups, "GRAPH_GROUPS")
                for field, wanted in (("completed_labelled_selections", 5184), ("declared_labelled_selections", 5184),
                                      ("tallies", counts), ("valid_labelled_selections", counts.get("VALID_LOCAL_GEOMETRY", 0)),
                                      ("distinct_labelled_valid_graphs", len(groups)), ("isomorphism_classes_claimed", False),
                                      ("part_count", 41), ("parts", part_receipts), ("coverage", FAMILY_COVERAGE)):
                    exact(summary.get(field), wanted, "FAMILY_SUMMARY:" + field)
                save(out / "independent_tallies.json", counts, deadline)
                save(out / "independent_valid_graph_groups.json", groups, deadline)
                result = dict(complete_labelled_selections=5184, complete_record_fields=16, complete_CN_entries=5184 * 289,
                              complete_parts=41, complete_checkpoints=41, final_part_population=64, tallies=counts,
                              valid_labelled_selections=counts.get("VALID_LOCAL_GEOMETRY", 0), distinct_labelled_valid_graphs=len(groups),
                              all_valid_raw_records_checked=True, full_exact_matrix_groups_checked=True, target_coverage_independently_derived=False,
                              ambient_inducedness_claimed=False, circuit_minimality_checked=False, target_resolution="NONE")
                status = STATUS + "COMPLETE_PASS"
        for name, sha in list(inputs.items()):
            pin(ROOT / name, sha)
        outputs = {path.relative_to(ROOT).as_posix(): digest(path, deadline) for path in sorted(out.iterdir()) if path.is_file()}
        save(out / "summary.json", dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), producer="/root/structural",
             verifier="/root/native_driver", method="independent_artifact_check", target_resolution="NONE", implementation_version=1,
             source_sha256=inputs[SELF.relative_to(ROOT).as_posix()], spec_sha256=inputs[SPEC.relative_to(ROOT).as_posix()],
             command=[sys.executable, *sys.argv], checked_scope=result, inputs_sha256=inputs, outputs_sha256=outputs,
             shared_origins=["Shared written31d2 necessary-family geometry; artifact computation does not independently derive target coverage",
                             "Factoradic ordinal selection and full neighbor-set CN/triangle/first-veto reconstruction are independent of Structural62225",
                             "Only unchanged deadline/stdlib JSON/hash infrastructure is shared; no producer decoder/parser/validator import"],
             limitations=["Fixed labelled local family only; no inducedness/ambient extras/completion/target/circuit/isomorphism conclusion",
                          "Interrupted producer suffix durability limited by preserved2fc642; full gate requires all5184 successful actual records",
                          "No mathematical source novelty/formal proof/external review claim"], deadline=deadline.status()), deadline)
        tick(deadline)
        return 0
    except BaseException as error:
        if (out / "summary.json").exists():
            (out / "summary.json").rename(out / "summary.not_approved.json")
        (out / "failure.json").write_text(json.dumps(dict(stage=getattr(error, "stage", type(error).__name__), detail=str(error),
             inputs_sha256=inputs, deadline=deadline.status(), automatic_retry=False, target_resolution="NONE", partial_outputs_not_complete=True),
             allow_nan=False, indent=2) + "\n", encoding="utf8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
