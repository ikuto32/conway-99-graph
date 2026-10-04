"""SOURCE ONLY: necessary coupled integer exterior class-edge flow, not a graph."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import re
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
    "build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi": "53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699",
    "build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd": "f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2",
    "build/research-venv/Lib/site-packages/highspy/highs.py": "00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a",
    "build/research-venv/Lib/site-packages/highspy/__init__.py": "01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9",
    "build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA": "cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d",
}
PROFILE_PATH = "acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json"
PROFILE_SHA = "468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e"
COUNT_PATH = "acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json"
COUNT_SHA = "133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5"
COUNT_GATE = "acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json"
COUNT_GATE_SHA = "37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8"
SCREEN_GATE = "acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json"
SCREEN_GATE_SHA = "4f6711cba2450262709ba0724bbd9bdbba3c95934c85265479985be7a38decb3"
PAIR_GATE = "acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json"
PAIR_GATE_SHA = "ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218"
THEOREM_GATE = "acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json"
THEOREM_GATE_SHA = "910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6"
PREMISES = {
    PROFILE_PATH: PROFILE_SHA, COUNT_PATH: COUNT_SHA, COUNT_GATE: COUNT_GATE_SHA,
    SCREEN_GATE: SCREEN_GATE_SHA, PAIR_GATE: PAIR_GATE_SHA, THEOREM_GATE: THEOREM_GATE_SHA,
    "acceleration/results/20261004_integer_counts_independent_full_root_actual_acceptance01.json": "3823dec446f661d87a27d2cad80b4c2f91883c786f30def4f43a25eb913bb10d",
    "acceleration/results/20261004_fixed17_count_neighbor_capacity_full_root_actual_acceptance01.json": "d8eaf7c2cb41a0bd8f1287b652edcbcc498b97f3475575b6e3b0d77e5d655017",
    "acceleration/results/20261004_fixed17_dual_gram_pairs_checker_root_actual_full_acceptance02.json": "39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586",
    "acceleration/results/20261004_target_exterior_type_edge_moments_root_written_acceptance01.json": "0e09566986883576c0f421cb1e47391eaadb49db72183d4e90c3ce55f9356728",
}
CAL_STATUS = "FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_V1_AUTHOR_CONTROLS_PASS"
MODEL_SCHEMA = "FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_MODEL_V1"
CANDIDATE_SCHEMA = "FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_INTEGER_CANDIDATE_V1"
CONTROL_COUNTS = {"positive": 7, "negative": 25, "total": 32}
MAX_JSON = 64 * 1024**2
ROUND_TOLERANCE = 1e-7


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def tick(deadline):
    status = deadline.status()
    need(not status["stop_required"] and status["remaining_seconds"] > 20, "SAVE_RESERVE")
    return status


def safe(name):
    need(type(name) is str, "PATH_TYPE")
    candidate = Path(name)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    need(not candidate.is_symlink(), "PATH_SYMLINK")
    result = candidate.resolve()
    need(result.is_relative_to(ROOT), "PATH_SCOPE")
    for parent in (candidate, *candidate.parents):
        need(not parent.is_symlink(), "PATH_SYMLINK")
        if parent == ROOT:
            break
    return result


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def constant(_):
        raise ValueError("JSON_NONFINITE")
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("JSON_SYNTAX") from None


def save(path, value, deadline):
    tick(deadline)
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    need(len(raw.encode("utf-8")) <= MAX_JSON, "OUTPUT_JSON_BOUND")
    path.write_text(raw, encoding="utf-8")
    tick(deadline)


class Reader:
    def __init__(self, deadline):
        self.deadline, self.pins = deadline, {}

    def read(self, name, digest, parsed=True):
        tick(self.deadline)
        need(type(digest) is str and re.fullmatch("[0-9a-f]{64}", digest) is not None, "SHA_TYPE")
        path = safe(str(name))
        need(path.is_file(), "INPUT_FILE")
        if parsed:
            need(path.stat().st_size <= MAX_JSON, "INPUT_JSON_BOUND")
        hasher, chunks = hashlib.sha256(), []
        with path.open("rb") as handle:
            while True:
                tick(self.deadline)
                chunk = handle.read(1024**2)
                if not chunk:
                    break
                hasher.update(chunk)
                if parsed:
                    chunks.append(chunk)
        need(hasher.hexdigest() == digest, "INPUT_SHA")
        key = path.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == digest, "INPUT_IDENTITY_CHANGED")
        self.pins[key] = digest
        result = decode(b"".join(chunks)) if parsed else None
        tick(self.deadline)
        return result

    def mapping(self, pins):
        need(type(pins) is dict and pins, "INPUT_MAP")
        for path, digest in pins.items():
            self.read(path, digest, False)

    def closing(self):
        # Fresh direct bytes, not an implicit ancestor-report crawler.
        for path, digest in list(self.pins.items()):
            self.read(path, digest, False)


def profile(raw, deadline):
    need(type(raw) is dict and set(raw) == {"target_order", "target_degree", "support_adjacency",
        "ordered_masks", "counts", "pair_bits"}, "PROFILE_FIELDS")
    order, degree, h = raw["target_order"], raw["target_degree"], raw["support_adjacency"]
    need(type(order) is int and type(degree) is int and 0 < degree < order - 1, "PROFILE_TARGET")
    need(type(h) is list and 0 < len(h) < order and all(type(row) is list and len(row) == len(h) for row in h), "PROFILE_GRAPH")
    m = len(h)
    need(all(type(x) is int and x in (0, 1) for row in h for x in row) and
         all(h[i][i] == 0 and all(h[i][j] == h[j][i] for j in range(m)) for i in range(m)), "PROFILE_GRAPH")
    masks, counts, pairs = raw["ordered_masks"], raw["counts"], raw["pair_bits"]
    need(type(masks) is list and masks and all(type(x) is int and 0 <= x < 1 << m for x in masks)
         and all(a < b for a, b in zip(masks, masks[1:])), "PROFILE_MASKS")
    need(type(counts) is list and len(counts) == len(masks) and
         all(type(x) is int and 0 <= x <= order - m for x in counts) and sum(counts) == order - m, "PROFILE_COUNTS")
    need(type(pairs) is list and len(pairs) == len(masks) * (len(masks) + 1) // 2, "PROFILE_PAIR_POPULATION")
    bits, index = {}, 0
    for i in range(len(masks)):
        tick(deadline)
        for j in range(i, len(masks)):
            row = pairs[index]
            need(type(row) is dict and set(row) == {"i", "j", "bits"} and
                 type(row["i"]) is int and type(row["j"]) is int and row["i"] == i and row["j"] == j, "PROFILE_PAIR_ORDER")
            value = row["bits"]
            need(type(value) is list and all(type(x) is int for x in value) and value in ([], [0], [1], [0, 1]), "PROFILE_PAIR_BITS")
            bits[i, j] = value
            index += 1
    return order, degree, h, masks, counts, bits


def model(raw, deadline, checkpoint=None):
    order, degree, h, masks, counts, bits = profile(raw, deadline)
    m = len(h)
    positive = [i for i, n in enumerate(counts) if n > 0]
    pairs = list(itertools.combinations_with_replacement(positive, 2))
    lower, upper, capacities = [], [], []
    for i, j in pairs:
        tick(deadline)
        capacity = counts[i] * counts[j] if i != j else counts[i] * (counts[i] - 1) // 2
        allowed = bits[i, j]
        need(allowed or capacity == 0, "PROFILE_INCOMPATIBLE_COEXISTENCE")
        capacities.append(capacity)
        lower.append(capacity if allowed == [1] else 0)
        upper.append(capacity if 1 in allowed else 0)
    rows = []
    incidence = [[int(mask >> u & 1) for u in range(m)] for mask in masks]
    for ordinal, i in enumerate(positive):
        tick(deadline)
        r = degree - masks[i].bit_count()
        b = [2 - incidence[i][u] - sum(h[u][v] * incidence[i][v] for v in range(m)) for u in range(m)]
        degree_terms, coordinate_terms = [], [[] for _ in range(m)]
        for variable, (a, c) in enumerate(pairs):
            if a != i and c != i:
                continue
            multiplier, other = (2, i) if a == c else (1, c if a == i else a)
            degree_terms.append([variable, multiplier])
            for u in range(m):
                if incidence[other][u]:
                    coordinate_terms[u].append([variable, multiplier])
        rows.append({"kind": "degree", "type_i": i, "support_u": None,
                     "lower": counts[i] * r, "upper": counts[i] * r, "terms": degree_terms})
        for u in range(m):
            rows.append({"kind": "support_incidence", "type_i": i, "support_u": u,
                         "lower": counts[i] * b[u], "upper": counts[i] * b[u], "terms": coordinate_terms[u]})
        if checkpoint is not None and ((ordinal + 1) % 8 == 0 or ordinal + 1 == len(positive)):
            checkpoint({"positive_classes_completed": ordinal + 1, "exact_rows_completed": len(rows),
                        "total_positive_classes": len(positive), "total_expected_rows": len(positive) * (m + 1)})
    return {"schema": MODEL_SCHEMA, "target_order": order, "target_degree": degree,
            "support_order": m, "positive_type_ids": positive, "variable_pairs": [list(x) for x in pairs],
            "variables": len(pairs), "lower": lower, "upper": upper, "capacities": capacities,
            "rows": rows, "ordered_masks": masks, "counts": counts,
            "support_adjacency": h, "zero_count_classes_omitted_canonically": True,
            "diagonal_is_unordered_edge_count": True, "diagonal_row_coefficient": 2,
            "no_equitable_profile_assumed": True, "graph_completion": False}


def candidate_from_counts(built, values):
    positive = built["positive_type_ids"]
    ordinal = {i: j for j, i in enumerate(positive)}
    ordered = [[0] * len(positive) for _ in positive]
    for (i, j), value in zip(built["variable_pairs"], values):
        a, b = ordinal[i], ordinal[j]
        ordered[a][b] = ordered[b][a] = value if a != b else 2 * value
    return {"schema": CANDIDATE_SCHEMA, "variable_pairs": built["variable_pairs"],
            "edge_counts": values, "ordered_flow_matrix": ordered}


def check_candidate(built, raw, deadline):
    need(type(raw) is dict and set(raw) == {"schema", "variable_pairs", "edge_counts", "ordered_flow_matrix"}
         and raw["schema"] == CANDIDATE_SCHEMA, "CANDIDATE_HEADER")
    need(same(raw["variable_pairs"], built["variable_pairs"]), "CANDIDATE_VARIABLE_ORDER")
    values, ordered = raw["edge_counts"], raw["ordered_flow_matrix"]
    need(type(values) is list and len(values) == built["variables"] and
         all(type(x) is int and x >= 0 for x in values), "CANDIDATE_INTEGER")
    need(all(lo <= x <= hi for lo, x, hi in zip(built["lower"], values, built["upper"])), "CANDIDATE_BOUND")
    p = len(built["positive_type_ids"])
    need(type(ordered) is list and len(ordered) == p and all(type(row) is list and len(row) == p for row in ordered)
         and all(type(x) is int and x >= 0 for row in ordered for x in row), "CANDIDATE_ORDERED_DOMAIN")
    need(all(ordered[i][j] == ordered[j][i] for i in range(p) for j in range(p)), "CANDIDATE_SYMMETRY")
    need(all(ordered[i][i] % 2 == 0 for i in range(p)), "CANDIDATE_DIAGONAL_PARITY")
    need(same(ordered, candidate_from_counts(built, values)["ordered_flow_matrix"]), "CANDIDATE_ORDERED_IDENTITY")
    observations = []
    for index, row in enumerate(built["rows"]):
        tick(deadline)
        lhs = sum(coefficient * values[variable] for variable, coefficient in row["terms"])
        stage = "DEGREE_EQUATION" if row["kind"] == "degree" else "INCIDENCE_EQUATION"
        need(lhs == row["lower"] == row["upper"], stage)
        observations.append({"row": index, "kind": row["kind"], "type_i": row["type_i"],
                             "support_u": row["support_u"], "lhs": lhs, "rhs": row["lower"]})
    return {"exact_integer_edge_variables": len(values), "exact_rows": len(observations),
            "ordered_flow_symmetric": True, "all_diagonal_flows_even": True,
            "capacities_and_allowed_bits_checked": True, "observations": observations,
            "integer_aggregate_feasible": True, "graph_completion": False}


def native(built, maximum, out, prefix, deadline, reserve):
    tick(deadline)
    import highspy
    import numpy as np
    need(Path(highspy.__file__).resolve() == ROOT / "build/research-venv/Lib/site-packages/highspy/__init__.py", "HIGHS_MODULE_PATH")
    need(Path(np.__file__).resolve() == ROOT / "build/research-venv/Lib/site-packages/numpy/__init__.py", "NUMPY_MODULE_PATH")
    solver = highspy.Highs()
    need(solver.version() == "1.15.1", "HIGHS_VERSION")
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = built["variables"], len(built["rows"])
    lp.col_cost_ = np.zeros(lp.num_col_, dtype=np.float64)
    lp.col_lower_ = np.asarray(built["lower"], dtype=np.float64)
    lp.col_upper_ = np.asarray(built["upper"], dtype=np.float64)
    lp.integrality_ = [highspy.HighsVarType.kInteger] * lp.num_col_
    lp.row_lower_ = np.asarray([row["lower"] for row in built["rows"]], dtype=np.float64)
    lp.row_upper_ = np.asarray([row["upper"] for row in built["rows"]], dtype=np.float64)
    starts, indices, values = [0], [], []
    for row in built["rows"]:
        tick(deadline)
        for variable, coefficient in row["terms"]:
            need(type(variable) is int and type(coefficient) is int and 0 <= variable < lp.num_col_
                 and coefficient in (1, 2), "MODEL_SPARSE_COEFFICIENT")
            indices.append(variable)
            values.append(coefficient)
        starts.append(len(indices))
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = np.asarray(starts, dtype=np.int32)
    lp.a_matrix_.index_ = np.asarray(indices, dtype=np.int32)
    lp.a_matrix_.value_ = np.asarray(values, dtype=np.float64)
    options = {"presolve": "on", "solver": "choose", "threads": 1, "parallel": "off", "random_seed": 0,
               "mip_feasibility_tolerance": ROUND_TOLERANCE, "primal_feasibility_tolerance": ROUND_TOLERANCE,
               "mip_rel_gap": 0.0, "mip_abs_gap": 0.0, "output_flag": True, "log_to_console": False,
               "log_file": str(out / (prefix + "_solver.log")), "time_limit": float(maximum)}
    for key, value in options.items():
        need(solver.setOptionValue(key, value) == highspy.HighsStatus.kOk, "HIGHS_OPTION:" + key)
    need(solver.passModel(lp) == highspy.HighsStatus.kOk, "HIGHS_MODEL")
    save(out / (prefix + "_before_solver.json"), {"variables": lp.num_col_, "rows": lp.num_row_,
        "nnz": len(indices), "proposed_options": dict(options), "remaining": deadline.status(),
        "native_limit_finalized_after_checkpoint": True}, deadline)
    allowance = min(float(maximum), tick(deadline)["remaining_seconds"] - reserve)
    need(allowance > 0, "SOLVER_RESERVE")
    need(solver.setOptionValue("time_limit", allowance) == highspy.HighsStatus.kOk, "HIGHS_OPTION:time_limit")
    options["time_limit"] = allowance
    started = time.monotonic()
    status = solver.run()
    elapsed = time.monotonic() - started
    tick(deadline)
    solution = solver.getSolution()
    floats = [float(x) for x in solution.col_value]
    need(all(math.isfinite(x) for x in floats), "NUMERIC_NONFINITE")
    guidance = {"schema": "FIXED17_AGGREGATE_EDGE_FLOW_NUMERIC_GUIDANCE_V1", "native_version": solver.version(),
        "numpy_version": np.__version__, "run_status": str(status), "model_status": str(solver.getModelStatus()),
        "solution_value_valid": bool(solution.value_valid), "col_value": floats,
        "col_value_float_hex": [x.hex() for x in floats], "options": options, "wall_seconds": elapsed,
        "objective_all_zero": True, "solver_calls": 1, "floating_status_is_proof": False,
        "numeric_infeasibility_is_proof": False}
    save(out / (prefix + "_guidance.json"), guidance, deadline)
    save(out / (prefix + "_after_solver.json"), {"native_status": str(status), "model_status": guidance["model_status"],
        "wall_seconds": elapsed, "remaining": deadline.status(), "is_proof": False}, deadline)
    return guidance


def extract(built, guidance, deadline):
    values = guidance["col_value"]
    if not guidance["solution_value_valid"] or len(values) != built["variables"]:
        return {"candidate": None, "reason": "No complete value-valid numeric incumbent", "infeasibility_proved": False}
    integers = [int(round(x)) for x in values]
    distances = [abs(x - y) for x, y in zip(values, integers)]
    if any(d > ROUND_TOLERANCE for d in distances):
        return {"candidate": None, "reason": "Numerical coordinates exceed the declared extraction distance",
                "max_rounding_distance": max(distances), "infeasibility_proved": False}
    candidate = candidate_from_counts(built, integers)
    try:
        checked = check_candidate(built, candidate, deadline)
    except ValueError as exc:
        if str(exc) == "SAVE_RESERVE":
            raise
        return {"candidate": None, "reason": "Extracted integers fail exact check: " + str(exc), "infeasibility_proved": False}
    return {"candidate": candidate, "exact_check": checked, "rounding_tolerance": ROUND_TOLERANCE,
            "max_rounding_distance": max(distances, default=0.0), "infeasibility_proved": False}


def rook_edge_profile(forced=False):
    masks, counts = [0, 1, 2, 3], [2, 2, 2, 1]
    forced_bits = {(0, 0): [1], (1, 1): [1], (2, 2): [1], (0, 3): [1],
                   (1, 3): [0], (2, 3): [0], (3, 3): [0]}
    return {"target_order": 9, "target_degree": 4, "support_adjacency": [[0, 1], [1, 0]],
            "ordered_masks": masks, "counts": counts,
            "pair_bits": [{"i": i, "j": j, "bits": forced_bits.get((i, j), [0, 1]) if forced else [0, 1]}
                          for i in range(4) for j in range(i, 4)]}


def rook_zero_profile():
    masks, counts = [0, 1, 2, 3, 5, 10, 12], [1, 0, 0, 1, 1, 1, 1]
    return {"target_order": 9, "target_degree": 4,
            "support_adjacency": [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]],
            "ordered_masks": masks, "counts": counts,
            "pair_bits": [{"i": i, "j": j, "bits": [0, 1]} for i in range(7) for j in range(i, 7)]}


def controls(out, deadline):
    records, positives = [], 0
    free, forced = rook_edge_profile(), rook_edge_profile(True)
    built, fixed = model(free, deadline), model(forced, deadline)
    rook_values = [1, 2, 2, 2, 1, 2, 0, 1, 0, 0]
    witness, fixed_witness = candidate_from_counts(built, rook_values), candidate_from_counts(fixed, rook_values)
    def run(name, expected, payload, action):
        nonlocal positives
        tick(deadline)
        index = len(records)
        save(out / ("control_%03d_%s.json" % (index, name)), payload, deadline)
        try:
            returned = action(payload)
            actual = "PASS"
        except ValueError as exc:
            returned, actual = None, str(exc)
        row = {"index": index, "name": name, "expected_stage": expected,
               "actual_stage": actual, "matches": actual == expected}
        records.append(row)
        save(out / ("stage_%03d.json" % index), row, deadline)
        if expected == "PASS":
            positives += 1
            save(out / ("result_%03d.json" % index), returned, deadline)
        need(actual == expected, "CONTROL_STAGE:" + name + ":" + actual)
    def mutate(name, expected, payload, edit, action):
        changed = copy.deepcopy(payload)
        edit(changed)
        run(name, expected, changed, action)
    check = lambda raw: check_candidate(built, raw, deadline)
    fixed_check = lambda raw: check_candidate(fixed, raw, deadline)
    run("known_rook_aggregate_multiplicities", "PASS", witness, check)
    run("known_rook_sole1_full_capacities", "PASS", fixed_witness, fixed_check)
    zero = model(rook_zero_profile(), deadline)
    edges = {(0, 3), (0, 4), (0, 5), (0, 6), (3, 6), (4, 5)}
    zero_witness = candidate_from_counts(zero, [int(tuple(pair) in edges) for pair in zero["variable_pairs"]])
    run("known_rook_zero_classes_omitted", "PASS", zero_witness, lambda raw: check_candidate(zero, raw, deadline))
    run("strict_json_integer_positive", "PASS", {"text": '{"count":2,"zero":0}'}, lambda raw: decode(raw["text"]))
    def tiny(payload, prefix):
        guidance = native(payload["model"], 5, out, prefix, deadline, 20)
        if payload["expected"] == "FEASIBLE":
            exact = extract(payload["model"], guidance, deadline)
            need(exact["candidate"] is not None, "TINY_NATIVE_FIXTURE")
            return {"guidance": guidance, "exact": exact, "synthetic_only": True}
        need(guidance["model_status"] == "HighsModelStatus.kInfeasible", "TINY_NATIVE_FIXTURE")
        return {"guidance": guidance, "numeric_status_is_not_a_scientific_proof": True,
                "known_fixture_contradiction": payload["contradiction"]}
    run("tiny_rook_integer_model", "PASS", {"model": built, "expected": "FEASIBLE"}, lambda raw: tiny(raw, "tiny_rook"))
    parity = {"variables": 1, "lower": [0], "upper": [1], "rows": [{"lower": 1, "upper": 1, "terms": [[0, 2]]}]}
    cap = {"variables": 1, "lower": [0], "upper": [1], "rows": [{"lower": 2, "upper": 2, "terms": [[0, 1]]}]}
    run("tiny_odd_diagonal_fixture", "PASS", {"model": parity, "expected": "INFEASIBLE", "contradiction": "2e=1 for integer e"}, lambda raw: tiny(raw, "tiny_parity"))
    run("tiny_capacity_fixture", "PASS", {"model": cap, "expected": "INFEASIBLE", "contradiction": "e=2 but 0<=e<=1"}, lambda raw: tiny(raw, "tiny_capacity"))
    pcheck = lambda raw: model(raw, deadline)
    mutate("profile_count_bool", "PROFILE_COUNTS", free, lambda r: r["counts"].__setitem__(0, True), pcheck)
    mutate("profile_count_float", "PROFILE_COUNTS", free, lambda r: r["counts"].__setitem__(0, 2.0), pcheck)
    mutate("profile_count_negative", "PROFILE_COUNTS", free, lambda r: r["counts"].__setitem__(0, -1), pcheck)
    mutate("profile_graph_bool", "PROFILE_GRAPH", free, lambda r: r["support_adjacency"][0].__setitem__(1, True), pcheck)
    mutate("profile_graph_float", "PROFILE_GRAPH", free, lambda r: r["support_adjacency"][0].__setitem__(1, 1.0), pcheck)
    mutate("profile_graph_asymmetric", "PROFILE_GRAPH", free, lambda r: r["support_adjacency"][0].__setitem__(1, 0), pcheck)
    mutate("profile_mask_bool", "PROFILE_MASKS", free, lambda r: r["ordered_masks"].__setitem__(0, False), pcheck)
    mutate("profile_mask_unsorted", "PROFILE_MASKS", free, lambda r: r["ordered_masks"].__setitem__(0, 1), pcheck)
    mutate("profile_pair_bit_bool", "PROFILE_PAIR_BITS", free, lambda r: r["pair_bits"][0].__setitem__("bits", [False, 1]), pcheck)
    mutate("profile_pair_duplicate", "PROFILE_PAIR_ORDER", free, lambda r: r["pair_bits"][1].__setitem__("j", 0), pcheck)
    mutate("candidate_wrong_schema", "CANDIDATE_HEADER", witness, lambda r: r.__setitem__("schema", "wrong"), check)
    mutate("candidate_pair_order", "CANDIDATE_VARIABLE_ORDER", witness, lambda r: r["variable_pairs"].reverse(), check)
    mutate("candidate_edge_bool", "CANDIDATE_INTEGER", witness, lambda r: r["edge_counts"].__setitem__(0, True), check)
    mutate("candidate_edge_negative", "CANDIDATE_INTEGER", witness, lambda r: r["edge_counts"].__setitem__(0, -1), check)
    mutate("candidate_edge_overcapacity", "CANDIDATE_BOUND", witness, lambda r: r["edge_counts"].__setitem__(0, 2), check)
    mutate("candidate_forced_zero", "CANDIDATE_BOUND", fixed_witness, lambda r: r["edge_counts"].__setitem__(6, 1), fixed_check)
    mutate("candidate_forced_one", "CANDIDATE_BOUND", fixed_witness, lambda r: r["edge_counts"].__setitem__(3, 1), fixed_check)
    mutate("candidate_matrix_bool", "CANDIDATE_ORDERED_DOMAIN", witness, lambda r: r["ordered_flow_matrix"][0].__setitem__(0, True), check)
    mutate("candidate_asymmetric", "CANDIDATE_SYMMETRY", witness, lambda r: r["ordered_flow_matrix"][0].__setitem__(1, 1), check)
    mutate("candidate_odd_diagonal", "CANDIDATE_DIAGONAL_PARITY", witness, lambda r: r["ordered_flow_matrix"][0].__setitem__(0, 1), check)
    mutate("candidate_wrong_even_diagonal", "CANDIDATE_ORDERED_IDENTITY", witness, lambda r: r["ordered_flow_matrix"][0].__setitem__(0, 0), check)
    degree_bad = candidate_from_counts(built, [0, 2, 2, 2, 1, 2, 0, 1, 0, 0])
    run("candidate_degree_failure", "DEGREE_EQUATION", degree_bad, check)
    # Four-cycle change preserves every degree: +e01-e12+e23-e03.
    incidence_bad = candidate_from_counts(built, [1, 3, 2, 1, 1, 1, 0, 1, 1, 0])
    run("candidate_incidence_failure_with_correct_degrees", "INCIDENCE_EQUATION", incidence_bad, check)
    run("json_duplicate", "JSON_DUPLICATE", {"text": '{"x":1,"x":2}'}, lambda raw: decode(raw["text"]))
    run("json_nonfinite", "JSON_NONFINITE", {"text": '{"x":NaN}'}, lambda raw: decode(raw["text"]))
    save(out / "controls.json", records, deadline)
    need(positives == CONTROL_COUNTS["positive"] and len(records) == CONTROL_COUNTS["total"], "CONTROL_POPULATION")
    return {**CONTROL_COUNTS, "all_precise_stages_match": True, "tiny_native_calls": 3,
            "actual_count_input_read": False, "actual_model_generated": False,
            "known_rook_positive_classes": 4, "known_rook_unordered_variables": 10,
            "known_rook_rows": 12, "graph_completion": False}


def actual_premises(reader):
    # Read only declared direct premises; do not recursively replay their ancestors.
    raw = {path: reader.read(path, digest) for path, digest in PREMISES.items()}
    theorem = raw[THEOREM_GATE]
    need(theorem.get("status") == "INDEPENDENT_TARGET_EXTERIOR_TYPE_NEIGHBOR_PROFILES_AND_EDGE_MOMENTS_V1_WRITTEN_PASS"
         and theorem.get("claim_id") == "C-TARGET-EXTERIOR-TYPE-NEIGHBOR-PROFILES-AND-EDGE-MOMENTS"
         and type(theorem.get("claim_revision")) is int and theorem["claim_revision"] == 1
         and theorem.get("producer") == "/root/structural" and theorem.get("verifier") == "/root/native_driver"
         and theorem.get("method") == "independent_derivation" and theorem.get("outcome") == "PASS"
         and theorem.get("target_resolution") == "NONE", "BLOCK_THEOREM_GATE")
    expected = ((COUNT_GATE, "INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS", 1, "/root/checkpoint_audit"),
                (PAIR_GATE, "INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS", 2, "/root/structural"),
                (SCREEN_GATE, "INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS", 1, "/root/checkpoint_audit"))
    for path, status, implementation, producer in expected:
        gate = raw[path]
        need(type(gate) is dict and gate.get("status") == status and gate.get("mode") == "full"
             and type(gate.get("implementation_version")) is int and gate["implementation_version"] == implementation
             and gate.get("producer") == producer
             and gate.get("verifier") == "/root/native_driver" and gate.get("method") == "independent_artifact_check"
             and gate.get("target_resolution") == "NONE", "EXISTING_PREMISE_GATE")
    count, screen, saved = raw[COUNT_GATE], raw[SCREEN_GATE], raw[PROFILE_PATH]
    need(count.get("outcome", {}).get("candidate_exact_checked") is True and
         count["inputs_sha256"].get(COUNT_PATH) == COUNT_SHA, "COUNT_EXACT_PREMISE")
    need(screen["inputs_sha256"].get(PROFILE_PATH) == PROFILE_SHA and
         screen.get("outcome", {}).get("all_screens_pass") is True, "TRUSTED_PROFILE_PREMISE")
    candidate = raw[COUNT_PATH]
    need(same(saved.get("ordered_masks"), candidate.get("ordered_masks")) and
         same(saved.get("counts"), candidate.get("counts")), "COUNT_PROFILE_IDENTITY")
    return saved


def qualify_author(reader, config, software):
    name, digest = config.get("author_calibration_path"), config.get("author_calibration_sha256")
    need(type(name) is str and type(digest) is str and config["inputs_sha256"].get(safe(name).relative_to(ROOT).as_posix()) == digest,
         "AUTHOR_CALIBRATION_PIN")
    raw = reader.read(name, digest)
    need(raw.get("status") == CAL_STATUS and raw.get("mode") == "calibrate"
         and raw.get("producer") == "/root/checkpoint_audit" and raw.get("independent_approval") is False
         and same(raw.get("source_software"), software) and
         all(type(raw.get("outcome", {}).get(k)) is int and raw["outcome"][k] == n for k, n in CONTROL_COUNTS.items()),
         "AUTHOR_CALIBRATION_HEADER")
    outputs = raw.get("outputs_sha256")
    need(type(outputs) is dict and len(outputs) == 84 and "controls.json" in outputs, "AUTHOR_CALIBRATION_POPULATION")
    base = safe(name).parent
    need({p.name for p in base.iterdir()} == set(outputs) | {"summary.json"}, "AUTHOR_CALIBRATION_DIRECTORY")
    for filename, sha in outputs.items():
        need(type(filename) is str and Path(filename).name == filename, "AUTHOR_CALIBRATION_FILENAME")
        reader.read(str(base / filename), sha, False)
    rows = reader.read(str(base / "controls.json"), outputs["controls.json"])
    need(type(rows) is list and len(rows) == CONTROL_COUNTS["total"] and all(type(row) is dict
         and type(row.get("index")) is int and row["index"] == index and row.get("matches") is True
         and row.get("expected_stage") == row.get("actual_stage") for index, row in enumerate(rows)), "AUTHOR_CONTROL_TABLE")


def scientific(reader, config, out, software):
    need(type(config) is dict and config.get("schema") == "FIXED17_AGGREGATE_EDGE_FLOW_CONFIGURATION_V1"
         and type(config.get("inputs_sha256")) is dict and config.get("target_resolution") == "NONE", "CONFIG_HEADER")
    need(all(config["inputs_sha256"].get(path) == digest for path, digest in {**software, **PREMISES}.items()), "CONFIG_REQUIRED_PINS")
    need(type(config.get("maximum_solver_seconds")) is int and 0 < config["maximum_solver_seconds"] <= 1500, "CONFIG_SOLVER_RANGE")
    # Fresh independent source/finite gates must be selected before a concrete run.
    for prefix in ("independent_checker_source", "independent_checker_spec", "independent_calibration", "independent_producer_controls"):
        name, digest = config.get(prefix + "_path"), config.get(prefix + "_sha256")
        need(type(name) is str and type(digest) is str and config["inputs_sha256"].get(safe(name).relative_to(ROOT).as_posix()) == digest,
             "CONFIG_INDEPENDENT_PIN:" + prefix)
    reader.mapping(config["inputs_sha256"])
    qualify_author(reader, config, software)
    saved = actual_premises(reader)
    need(type(saved.get("target_order")) is int and saved["target_order"] == 99
         and type(saved.get("target_degree")) is int and saved["target_degree"] == 14
         and len(saved.get("support_adjacency", [])) == 17 and len(saved.get("counts", [])) == 472, "FIXED_PROFILE_POPULATION")
    names = []
    def checkpoint(value):
        name = "model_checkpoint_%03d.json" % len(names)
        names.append(name)
        save(out / name, value, reader.deadline)
    built = model(saved, reader.deadline, checkpoint)
    need(len(built["positive_type_ids"]) == 68 and built["variables"] == 2346 and len(built["rows"]) == 1224
         and sum(built["counts"]) == 82 and len(names) == 9, "FIXED_COUPLED_POPULATION")
    save(out / "parsed_aggregate_input.json", saved, reader.deadline)
    save(out / "aggregate_model.json", built, reader.deadline)
    guidance = native(built, config["maximum_solver_seconds"], out, "scientific", reader.deadline, 180)
    exact = extract(built, guidance, reader.deadline)
    save(out / "extraction.json", exact, reader.deadline)
    if exact["candidate"] is not None:
        save(out / "exact_integer_edge_flow.json", exact["candidate"], reader.deadline)
        save(out / "exact_flow_rows.json", exact["exact_check"]["observations"], reader.deadline)
    return {"complete_input_type_count": 472, "outside_copies": 82, "positive_classes": 68,
            "unordered_edge_variables": built["variables"], "exact_equations": len(built["rows"]),
            "model_checkpoints": len(names), "scientific_solver_calls": 1,
            "exact_integer_candidate_produced": exact["candidate"] is not None,
            "candidate_absent_reason": exact.get("reason"), "numeric_model_status": guidance["model_status"],
            "coupled_integer_feasibility": "CANDIDATE" if exact["candidate"] is not None else "UNKNOWN",
            "infeasibility_proved": False, "graph_completion": False, "no_equitable_profile_assumed": True}


def output_hashes(out, deadline):
    result = {}
    for path in sorted(out.iterdir()):
        tick(deadline)
        need(path.is_file() and not path.is_symlink() and path.suffix not in (".part", ".tmp"), "OUTPUT_POPULATION")
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                tick(deadline)
                block = handle.read(1024**2)
                if not block:
                    break
                hasher.update(block)
        result[path.name] = hasher.hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "solve"))
    parser.add_argument("--seconds", required=True, type=float)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--executor", required=True, choices=("/root", "/root/checkpoint_audit"))
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="One coupled aggregate integer flow search or fresh finite author controls; all direct authentication, native time, exact extraction and saves share this invocation")
    out = safe(args.out)
    need(out.is_relative_to(ROOT / "acceleration/results") and not out.exists(), "OUTPUT_FRESH_SCOPE")
    out.mkdir(parents=True)
    reader = Reader(deadline)
    software = {**SOFTWARE, SELF.relative_to(ROOT).as_posix(): args.self_sha256, SPEC.relative_to(ROOT).as_posix(): args.spec_sha256}
    try:
        reader.mapping(software)
        if args.mode == "calibrate":
            outcome, status = controls(out, deadline), CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None, "CONFIG_ARGUMENTS")
            config = reader.read(args.configuration, args.configuration_sha256)
            outcome = scientific(reader, config, out, software)
            status = "CANDIDATE_FIXED17_AGGREGATE_INTEGER_EDGE_FLOW_V1" if outcome["exact_integer_candidate_produced"] else "NO_EXACT_AGGREGATE_FLOW_WITNESS_V1"
        reader.closing()
        outputs = output_hashes(out, deadline)
        if args.mode == "calibrate":
            need(len(outputs) == 84, "AUTHOR_OUTPUT_POPULATION")
        else:
            need(len(outputs) == (18 if outcome["exact_integer_candidate_produced"] else 16),
                 "SCIENTIFIC_OUTPUT_POPULATION")
        report = {"schema": "FIXED17_AGGREGATE_EDGE_FLOW_PRODUCER_REPORT_V1", "status": status,
            "implementation_version": 1, "mode": args.mode, "timestamp": datetime.now(timezone.utc).isoformat(),
            "producer": "/root/checkpoint_audit", "source_author": "/root/checkpoint_audit",
            "executor_declaration": args.executor, "actual_executor_requires_external_receipt": True,
            "method": "coupled_integer_model_search_and_exact_candidate_extraction" if args.mode == "solve" else "finite_author_controls",
            "independent_verifier": None, "independent_verifier_null_reason": "A separately authored qualified aggregate-flow checker must validate all raw integer rows and capacities",
            "source_software": software, "inputs_sha256": dict(reader.pins), "outputs_sha256": outputs,
            "outcome": outcome, "command": sys.argv, "cwd": str(ROOT), "python": platform.python_version(),
            "actual_count_input_read": args.mode == "solve", "independent_approval": False,
            "automatic_retry": False, "target_resolution": "NONE", "deadline": deadline.status(),
            "shared_components": ["Root proposed the coupled model; Structural block theorem was independently derived by Native in910a",
                "Pinned Python/json/SHA/CommandDeadline and locked Highs/numpy construction conventions share earlier tooling; no old solver or checker gate transfers",
                "Count/pair/capacity direct immutable premises are reused; no old ancestor-wide arithmetic/hash crawler"],
            "limitations": ["Exact integer aggregate flow is necessary only and is not82-copy adjacency or full99 target realization",
                "Numeric infeasibility, timeout, bounds and missing incumbents are UNKNOWN and prove no count-witness or target exclusion",
                "Rounded numerical extraction is a candidate only; raw floats/hex preserved and every integer capacity/equation must hold exactly",
                "No equitable/uniform type profile, selected support filter, local perfect-matching or extra adjacency cuts are assumed",
                "One scientific Highs run; finite calibration has three tiny known fixtures; no automatic retry",
                "Guards and completed checkpoints are durable intent, not native internal resumability or hard-real-time save/concurrency guarantee",
                "No graph/optimizer/rank/formal/external approval or Git/index/ledger action"]}
        save(out / "summary.json", report, deadline)
        reader.closing()
        tick(deadline)
        print(json.dumps({"status": status, "outcome": outcome, "physical_files": len(outputs) + 1}), flush=True)
    except Exception as exc:
        try:
            (out / "failure.json").write_text(json.dumps({"status": "FAILED_PRESERVED", "stage": str(exc),
                "exception": type(exc).__name__, "inputs_sha256": reader.pins, "target_resolution": "NONE",
                "infeasibility_inferred": False, "automatic_retry": False, "deadline": deadline.status()}, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
