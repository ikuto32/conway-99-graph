"""SOURCE ONLY: individual exterior-neighbor integer feasibility for one count witness."""
import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
MAX_BYTES = 64 * 1024 * 1024
ROUND_TOLERANCE = 1e-7
HELPER = "acceleration/screen_20261004_fixed17_count_neighbor_capacity_v1.py"
HELPER_SHA = "4d737ba3b8ea90df487a1b71cbc6fe4f8baf38234533fdc9115bb76034556371"
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
    HELPER: HELPER_SHA,
}
COUNT_BASE = "acceleration/results/20261004_fixed17_integer_type_counts01/"
COUNT_PINS = {
    COUNT_BASE+"summary.json": "857dc4a986cf509e697bc61c79562adeec3f561aab827a6e54ad0dbe2e660ab3",
    COUNT_BASE+"exact_integer_candidate.json": "133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5",
    COUNT_BASE+"parsed_fixed_input.json": "cfe5003a2bd0ad4b2b979264c6e6d1648dc3cd67d1ebc03226d44998371b1248",
    COUNT_BASE+"integer_model.json": "3279f118e3bce092b61a3d6d3feb8eaa15ff9f9a6178d99f91ccf4183251ccdc",
    COUNT_BASE+"pair_rules.json": "ef52a35246c2ae9634f13284d4850da25f4b4f666f15fe0675284c168b03086c",
}
COUNT_GATE_PATH = "acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json"
COUNT_GATE_SHA = "37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8"
COUNT_ROOT_PATH = "acceleration/results/20261004_integer_counts_independent_full_root_actual_acceptance01.json"
COUNT_ROOT_SHA = "3823dec446f661d87a27d2cad80b4c2f91883c786f30def4f43a25eb913bb10d"
PAIR_GATE_PATH = "acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json"
PAIR_GATE_SHA = "ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218"
PAIR_ROOT_PATH = "acceleration/results/20261004_fixed17_dual_gram_pairs_checker_root_actual_full_acceptance02.json"
PAIR_ROOT_SHA = "39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586"
PROOF_PATH = "acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json"
PROOF_SHA = "910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6"
PAIR_RAW = "acceleration/results/20261004_fixed17_dual_gram_pairs01/"
PAIR_FIELDS = ("proposal_id", "i", "j", "left_mask", "right_mask", "intersection",
    "upper_left_diagonal", "upper_right_diagonal", "upper_cross_0", "upper_cross_1",
    "lower_left_diagonal", "lower_right_diagonal", "lower_cross_0", "lower_cross_1",
    "upper_bits", "lower_bits", "cn_bits", "combined_bits", "classification")
CLASS_NAMES = {(): "incompatible", (0,): "forced_nonadjacent", (1,): "forced_adjacent", (0, 1): "either"}
CONTROL_COUNTS = dict(positive=9, negative=25, total=34)
CAL_STATUS = "FIXED17_FOCAL_NEIGHBOR_INTEGER_V1_AUTHOR_CONTROLS_PASS"


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


def budget_snapshot(raw):
    need(type(raw) is dict and raw.get("stop_required") is False
         and type(raw.get("remaining_seconds")) in (int, float)
         and math.isfinite(raw["remaining_seconds"]) and raw["remaining_seconds"] > 20, "SAVE_RESERVE")
    return raw


def tick(deadline):
    return budget_snapshot(deadline.status())


def solver_allowance(raw, maximum, reserve=180):
    remaining = budget_snapshot(raw)["remaining_seconds"]
    need(type(maximum) in (int, float) and math.isfinite(maximum) and 0 < maximum <= 10, "SOLVER_MAXIMUM")
    need(type(reserve) is int and reserve in (30, 180), "SOLVER_RESERVE_POLICY")
    result = min(float(maximum), remaining - reserve)
    need(result > 0, "SOLVER_RESERVE")
    return result


def safe(raw):
    need(type(raw) is str and raw and "\x00" not in raw, "PATH_STRING")
    path = Path(raw)
    path = ROOT/path if not path.is_absolute() else path
    resolved = path.resolve()
    need(resolved.is_relative_to(ROOT), "PATH_SCOPE")
    current = path
    while current != ROOT and current.is_relative_to(ROOT):
        need(not current.is_symlink() and not current.is_junction(), "PATH_LINK")
        current = current.parent
    return resolved


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def bad(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=bad)


class Reader:
    def __init__(self, deadline):
        self.deadline, self.pins = deadline, {}

    def read(self, raw, expected, parse=True):
        need(type(expected) is str and re.fullmatch("[0-9a-f]{64}", expected), "SHA256_STRING")
        path = safe(raw)
        need(path.is_file() and path.stat().st_size <= MAX_BYTES, "FILE_BOUND")
        key = path.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == expected, "PIN_CONFLICT")
        digest, blocks, size = hashlib.sha256(), [], 0
        with path.open("rb") as handle:
            while True:
                tick(self.deadline)
                block = handle.read(1024*1024)
                if not block:
                    break
                size += len(block)
                need(size <= MAX_BYTES, "FILE_BOUND")
                digest.update(block)
                if parse:
                    blocks.append(block)
        need(digest.hexdigest() == expected, "INPUT_HASH")
        self.pins[key] = expected
        tick(self.deadline)
        return strict_json(b"".join(blocks)) if parse else None

    def mapping(self, raw):
        need(type(raw) is dict and raw, "INPUT_MAP")
        for path, digest in raw.items():
            self.read(path, digest, False)

    def closing(self):
        self.mapping(dict(self.pins))


def save(path, value, deadline):
    tick(deadline)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n").encode("utf8")
    need(len(raw) <= MAX_BYTES, "OUTPUT_BOUND")
    temporary = path.with_suffix(path.suffix+".tmp")
    tick(deadline)
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    tick(deadline)
    os.replace(temporary, path)
    tick(deadline)


def helper_functions(reader):
    # Explicit three preserved producer-side parser functions only. No module imports/main/old screen.
    reader.read(HELPER, HELPER_SHA, False)
    tick(reader.deadline)
    tree = ast.parse(safe(HELPER).read_bytes(), filename=HELPER)
    wanted = ("packet", "count_gate", "raw_pairs")
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    need(len(nodes) == 3 and set(node.name for node in nodes) == set(wanted)
         and all(not node.decorator_list for node in nodes), "HELPER_NODE_SET")
    namespace = dict(need=need, same=same, tick=tick, itertools=itertools, PAIR_RAW=PAIR_RAW,
                     PAIR_FIELDS=PAIR_FIELDS, CLASS_NAMES=CLASS_NAMES)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), HELPER, "exec"), namespace)
    tick(reader.deadline)
    return {name:namespace[name] for name in wanted}


def focal_model(raw, focal, packet_function, deadline):
    h, masks, counts, bits = packet_function(raw)
    need(type(focal) is int and 0 <= focal < len(masks), "FOCAL_INDEX")
    need(counts[focal] > 0, "FOCAL_POSITIVE")
    m, n = len(h), len(masks)
    capacities = [counts[j]-int(j == focal) for j in range(n)]
    lower, upper = [], []
    for j, capacity in enumerate(capacities):
        tick(deadline)
        value = bits[min(focal, j), max(focal, j)]
        lower.append(capacity if value == [1] else 0)
        upper.append(capacity if 1 in value else 0)
    t = [(masks[focal] >> u) & 1 for u in range(m)]
    degree = raw["target_degree"]-sum(t)
    b = [2-t[u]-sum(h[u][v]*t[v] for v in range(m)) for u in range(m)]
    rows = [dict(kind="degree", coordinate=None, rhs=degree, coefficients=[1]*n)]
    rows += [dict(kind="support_coordinate", coordinate=u, rhs=b[u],
                  coefficients=[(mask >> u) & 1 for mask in masks]) for u in range(m)]
    return dict(schema="FIXED17_FOCAL_NEIGHBOR_INTEGER_MODEL_V1", focal_type=focal, focal_label=[focal, 0],
                ordered_masks=list(masks), count_vector=list(counts), copy_capacities=capacities,
                variables=n, support_size=m, lower=lower, upper=upper, rows=rows,
                required_outside_degree=degree, required_support_incidences=b,
                same_type_neighbor_profiles_not_assumed=True, uniform_profiles=False)


def bound_witness(model):
    lower, upper = model["lower"], model["upper"]
    degree = model["required_outside_degree"]
    if degree < sum(lower):
        return dict(stage="MANDATORY_BOUND", rhs=degree, minimum=sum(lower), maximum=sum(upper), row=0)
    if not 0 <= degree <= sum(upper):
        return dict(stage="CAPACITY_BOUND", rhs=degree, minimum=sum(lower), maximum=sum(upper), row=0)
    for i, row in enumerate(model["rows"][1:], 1):
        low = sum(c*y for c, y in zip(row["coefficients"], lower))
        high = sum(c*y for c, y in zip(row["coefficients"], upper))
        if not low <= row["rhs"] <= high:
            return dict(stage="COORDINATE_BOUND", rhs=row["rhs"], minimum=low, maximum=high, row=i)
    return None


def check_values(model, values, deadline):
    need(type(values) is list and len(values) == model["variables"], "NEIGHBOR_SHAPE")
    need(all(type(x) is int for x in values), "NEIGHBOR_INTEGER")
    need(all(x >= 0 for x in values), "NEIGHBOR_NONNEGATIVE")
    need(all(lo <= x <= hi for lo, x, hi in zip(model["lower"], values, model["upper"])), "NEIGHBOR_BOUND")
    checked = []
    for i, row in enumerate(model["rows"]):
        tick(deadline)
        lhs = sum(c*x for c, x in zip(row["coefficients"], values))
        need(lhs == row["rhs"], "NEIGHBOR_DEGREE" if i == 0 else "NEIGHBOR_COORDINATE")
        checked.append(dict(index=i, kind=row["kind"], coordinate=row["coordinate"], lhs=lhs, rhs=row["rhs"], exact=True))
    return checked


def chosen_labels(model, values):
    labels = []
    for j, number in enumerate(values):
        start = int(j == model["focal_type"])
        labels += [[j, k] for k in range(start, start+number)]
    return labels


def check_labels(model, values, labels, deadline):
    need(type(labels) is list and all(type(x) is list and len(x) == 2 for x in labels), "LABEL_SHAPE")
    need(all(type(x) is int for pair in labels for x in pair), "LABEL_INTEGER")
    need(model["focal_label"] not in labels, "LABEL_SELF")
    need(labels == sorted(labels) and len({tuple(pair) for pair in labels}) == len(labels), "LABEL_ORDER")
    need(all(0 <= j < model["variables"] and 0 <= k < model["count_vector"][j] for j, k in labels), "LABEL_CAPACITY")
    need(len(labels) == model["required_outside_degree"], "LABEL_DEGREE")
    observed = [0]*model["variables"]
    for j, _ in labels:
        tick(deadline)
        observed[j] += 1
    need(same(observed, values), "LABEL_AGGREGATION")
    check_values(model, observed, deadline)
    return dict(chosen_labels=labels, binary_labeled_neighbor_choice=True, selected_count=len(labels), self_excluded=True)


def extract(model, guidance, deadline):
    values = guidance["col_value"]
    if guidance["solution_value_valid"] is not True or len(values) != model["variables"]:
        return dict(candidate=None, reason="No complete value-valid numerical incumbent", numeric_infeasibility_is_proof=False)
    integers = [int(round(x)) for x in values]
    distances = [abs(x-y) for x, y in zip(values, integers)]
    if any(x > ROUND_TOLERANCE for x in distances):
        return dict(candidate=None, reason="Coordinate exceeds declared extraction tolerance", maximum_distance=max(distances), numeric_infeasibility_is_proof=False)
    try:
        rows = check_values(model, integers, deadline)
    except ValueError as exc:
        if str(exc) == "SAVE_RESERVE":
            raise
        return dict(candidate=None, reason="Exact extraction rejected: "+str(exc), rounded_values=integers,
                    maximum_distance=max(distances, default=0), numeric_infeasibility_is_proof=False)
    return dict(candidate=integers, rows=rows, maximum_distance=max(distances, default=0), exact_constraints=True,
                independent_approval=False, graph_completion=False)


def native(model, out, prefix, deadline, maximum, reserve=180):
    tick(deadline)
    import highspy
    import numpy as np
    need(Path(highspy.__file__).resolve() == ROOT/"build/research-venv/Lib/site-packages/highspy/__init__.py", "HIGHS_MODULE_PATH")
    need(Path(np.__file__).resolve() == ROOT/"build/research-venv/Lib/site-packages/numpy/__init__.py", "NUMPY_MODULE_PATH")
    solver = highspy.Highs()
    need(solver.version() == "1.15.1", "HIGHS_VERSION")
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = model["variables"], len(model["rows"])
    lp.col_cost_ = np.zeros(lp.num_col_, dtype=np.float64)
    lp.col_lower_, lp.col_upper_ = np.asarray(model["lower"], dtype=np.float64), np.asarray(model["upper"], dtype=np.float64)
    lp.integrality_ = [highspy.HighsVarType.kInteger]*lp.num_col_
    rhs = [row["rhs"] for row in model["rows"]]
    lp.row_lower_, lp.row_upper_ = np.asarray(rhs, dtype=np.float64), np.asarray(rhs, dtype=np.float64)
    starts, indices, coefficients = [0], [], []
    for row in model["rows"]:
        tick(deadline)
        for j, c in enumerate(row["coefficients"]):
            need(type(c) is int and abs(c) <= 82, "SPARSE_INTEGER")
            if c:
                indices.append(j)
                coefficients.append(c)
        starts.append(len(indices))
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = np.asarray(starts, dtype=np.int32)
    lp.a_matrix_.index_, lp.a_matrix_.value_ = np.asarray(indices, dtype=np.int32), np.asarray(coefficients, dtype=np.float64)
    log = out/(prefix+"_solver.log")
    with log.open("xb"):
        pass
    options = dict(presolve="on", solver="choose", threads=1, parallel="off", random_seed=0,
        mip_feasibility_tolerance=ROUND_TOLERANCE, primal_feasibility_tolerance=ROUND_TOLERANCE,
        mip_rel_gap=0.0, mip_abs_gap=0.0, output_flag=True, log_to_console=False, log_file=str(log))
    for key, value in options.items():
        need(solver.setOptionValue(key, value) == highspy.HighsStatus.kOk, "HIGHS_OPTION:"+key)
    need(solver.passModel(lp) == highspy.HighsStatus.kOk, "HIGHS_MODEL")
    actual = solver_allowance(deadline.status(), maximum, reserve)
    need(solver.setOptionValue("time_limit", actual) == highspy.HighsStatus.kOk, "HIGHS_OPTION:time_limit")
    options["time_limit"] = actual
    started = time.monotonic()
    run_status = solver.run()
    elapsed = time.monotonic()-started
    tick(deadline)
    solution, info = solver.getSolution(), solver.getInfo()
    values = [float(x) for x in solution.col_value]
    need(all(math.isfinite(x) for x in values), "NATIVE_NONFINITE_VECTOR")
    def finite(value):
        if type(value) is int:
            return value
        number = float(value)
        return number if math.isfinite(number) else dict(nonfinite=str(number), is_proof=False)
    guidance = dict(schema="FIXED17_FOCAL_NEIGHBOR_NUMERIC_GUIDANCE_V1", native_version=solver.version(),
        numpy_version=np.__version__, run_status=str(run_status), model_status=str(solver.getModelStatus()),
        solution_value_valid=bool(solution.value_valid), col_value=values, col_value_float_hex=[x.hex() for x in values],
        info={key:finite(getattr(info, key)) for key in ("mip_node_count", "mip_gap", "mip_dual_bound",
             "objective_function_value", "max_integrality_violation", "max_primal_infeasibility", "primal_solution_status")},
        options=options, wall_seconds=elapsed, solver_calls=1, objective_all_zero=True,
        floating_status_is_proof=False, numeric_infeasibility_is_proof=False)
    save(out/(prefix+"_guidance.json"), guidance, deadline)
    return guidance


def rook_fixture(forced=False):
    adjacent = {(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3)}
    return dict(target_order=9, target_degree=4,
        support_adjacency=[[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]],
        ordered_masks=[0, 3, 5, 10, 12], counts=[1]*5,
        pair_bits=[dict(i=i, j=j, bits=([int((i, j) in adjacent)] if forced and i != j else [0, 1]))
                   for i, j in itertools.combinations_with_replacement(range(5), 2)])


def controls(out, deadline, functions):
    routes = []
    free, forced = rook_fixture(), rook_fixture(True)
    adjacent = {(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3)}
    def model(p):
        return focal_model(p["packet"], p["focal"], functions["packet"], deadline)
    def witness(p):
        m = model(p)
        rows = check_values(m, p["values"], deadline)
        return dict(model=m, values=p["values"], rows=rows,
                    labels=check_labels(m, p["values"], chosen_labels(m, p["values"]), deadline))
    def all_rook(p):
        results = []
        for i in range(5):
            y = [int(tuple(sorted((i, j))) in adjacent) if i != j else 0 for j in range(5)]
            results.append(witness(dict(packet=p, focal=i, values=y)))
        return dict(results=results, complete_actual_rook_exterior_choices=5)
    repeated = dict(target_order=6, target_degree=4,
        support_adjacency=[[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
        ordered_masks=[15], counts=[2], pair_bits=[dict(i=0, j=0, bits=[0])])
    def self_zero(p):
        result = witness(p)
        need(result["model"]["copy_capacities"] == [1] and result["labels"]["chosen_labels"] == [], "SELF_CAPACITY_CONTROL")
        return result
    base = dict(packet=free, focal=1, values=[1, 0, 0, 0, 1])
    def labels_action(p):
        m = model(p)
        return check_labels(m, p["values"], p["labels"], deadline)
    routes += [("known_rook_all_five_free_choices", "PASS", free, all_rook),
        ("known_rook_all_five_forced_choices", "PASS", forced, all_rook),
        ("two_same_type_copies_exclude_self_zero_degree", "PASS", dict(packet=repeated, focal=0, values=[0]), self_zero),
        ("aggregate_lifts_to_distinct_binary_copy_slots", "PASS", dict(**base, labels=[[0, 0], [4, 0]]), labels_action),
        ("numeric_absent_is_not_an_infeasibility_proof", "PASS", dict(solution_value_valid=False, col_value=[]),
         lambda p:extract(model(base), p, deadline)),
        ("budget_above_reserve", "PASS", dict(stop_required=False, remaining_seconds=20.000001), budget_snapshot)]
    tiny = [dict(variables=2, lower=[0, 0], upper=[1, 1], rows=[dict(kind="degree", coordinate=None, rhs=1, coefficients=[1, 1]),
            dict(kind="support_coordinate", coordinate=0, rhs=1, coefficients=[1, 0])]),
        dict(variables=1, lower=[0], upper=[1], rows=[dict(kind="degree", coordinate=None, rhs=1, coefficients=[2])]),
        dict(variables=1, lower=[1], upper=[1], rows=[dict(kind="degree", coordinate=None, rhs=1, coefficients=[1])])]
    for i, m in enumerate(tiny):
        def tiny_action(p, case=i):
            g = native(p, out, "tiny_%d" % case, deadline, 5, reserve=30)
            result = extract(p, g, deadline)
            if case == 1:
                need(result["candidate"] is None, "TINY_PARITY_NOT_EXACT")
            else:
                need(result["candidate"] == ([1, 0] if case == 0 else [1]), "TINY_VALID_WITNESS")
            return dict(guidance=g, extraction=result, mathematical_infeasibility_proven=False)
        routes.append(("tiny_integer_%d" % i, "PASS", m, tiny_action))
    def mutate(name, stage, original, change, action=witness):
        p = copy.deepcopy(original)
        change(p)
        routes.append((name, stage, p, action))
    mutate("count_bool", "COUNT_INTEGER", base, lambda p:p["packet"]["counts"].__setitem__(0, True))
    mutate("count_float", "COUNT_INTEGER", base, lambda p:p["packet"]["counts"].__setitem__(0, 1.0))
    mutate("count_sum", "COUNT_SUM", base, lambda p:p["packet"]["counts"].__setitem__(0, 0))
    mutate("mask_bool", "TYPE_MASK_INTEGER", base, lambda p:p["packet"]["ordered_masks"].__setitem__(0, False))
    mutate("mask_order", "TYPE_MASK_ORDER", base, lambda p:p["packet"]["ordered_masks"].reverse())
    mutate("graph_bool", "GRAPH_DOMAIN", base, lambda p:p["packet"]["support_adjacency"][0].__setitem__(0, False))
    mutate("pair_label_bool", "PAIR_COORDINATES", base, lambda p:p["packet"]["pair_bits"][0].__setitem__("i", False))
    mutate("pair_bits_bool", "PAIR_BITS", base, lambda p:p["packet"]["pair_bits"][0].__setitem__("bits", [False, 1]))
    mutate("pair_missing", "PAIR_POPULATION", base, lambda p:p["packet"]["pair_bits"].pop())
    mutate("pair_incompatible_coexistence", "INCOMPATIBLE_COEXISTENCE", base, lambda p:p["packet"]["pair_bits"][1].__setitem__("bits", []))
    mutate("focal_bool", "FOCAL_INDEX", base, lambda p:p.__setitem__("focal", True))
    def absent(p):
        p["focal"] = 0
        p["packet"]["counts"] = [0, 2, 1, 1, 1]
    mutate("focal_absent", "FOCAL_POSITIVE", base, absent)
    mutate("neighbor_bool", "NEIGHBOR_INTEGER", base, lambda p:p["values"].__setitem__(0, True))
    mutate("neighbor_float", "NEIGHBOR_INTEGER", base, lambda p:p["values"].__setitem__(0, 1.0))
    mutate("neighbor_negative", "NEIGHBOR_NONNEGATIVE", base, lambda p:p["values"].__setitem__(0, -1))
    mutate("neighbor_above_capacity", "NEIGHBOR_BOUND", base, lambda p:p["values"].__setitem__(0, 2))
    forced_base = dict(packet=forced, focal=1, values=[1, 0, 0, 0, 1])
    mutate("mandatory_pair_one_not_selected", "NEIGHBOR_BOUND", forced_base, lambda p:p["values"].__setitem__(4, 0))
    mutate("neighbor_wrong_degree", "NEIGHBOR_DEGREE", base, lambda p:p["values"].__setitem__(4, 0))
    mutate("neighbor_wrong_coordinate", "NEIGHBOR_COORDINATE", base,
           lambda p:p.__setitem__("values", [1, 0, 1, 0, 0]))
    label_base = dict(**base, labels=[[0, 0], [4, 0]])
    mutate("chosen_label_bool", "LABEL_INTEGER", label_base, lambda p:p["labels"][0].__setitem__(0, False), labels_action)
    mutate("chosen_label_self", "LABEL_SELF", label_base, lambda p:p.__setitem__("labels", [[1, 0], [4, 0]]), labels_action)
    mutate("chosen_label_missing", "LABEL_DEGREE", label_base, lambda p:p["labels"].pop(), labels_action)
    routes += [("budget_at_reserve", "SAVE_RESERVE", dict(stop_required=False, remaining_seconds=20), budget_snapshot),
        ("budget_stop", "SAVE_RESERVE", dict(stop_required=True, remaining_seconds=100), budget_snapshot),
        ("solver_closing_reserve", "SOLVER_RESERVE", dict(stop_required=False, remaining_seconds=180),
         lambda p:solver_allowance(p, 10))]
    need(len(routes) == 34 and sum(stage == "PASS" for _, stage, _, _ in routes) == 9, "CONTROL_DECLARATION")
    table, mismatches = [], []
    for i, (name, expected, payload, action) in enumerate(routes):
        tick(deadline)
        save(out/("control_%02d_%s.json" % (i, name)), payload, deadline)
        value = None
        try:
            value, actual = action(payload), "PASS"
        except ValueError as exc:
            actual = str(exc)
        row = dict(index=i, name=name, expected_stage=expected, actual_stage=actual, matches=expected == actual)
        table.append(row)
        if expected != actual:
            mismatches.append(row)
        if value is not None:
            save(out/("result_%02d.json" % i), value, deadline)
    save(out/"controls.json", table, deadline)
    need(not mismatches, "AUTHOR_CONTROL_STAGE_MISMATCH")
    return dict(counts=CONTROL_COUNTS, stage_mismatches=mismatches, table=table, native_solver_calls=3,
                actual_count_witness_read=False, positive_graph="rook9 with four-corner support",
                duplicate_copy_fixture_is_row_kernel_only=True)


def qualify_calibration(reader, raw, software):
    need(type(raw) is dict and raw.get("status") == CAL_STATUS and raw.get("mode") == "calibrate"
         and raw.get("producer") == "/root/checkpoint_audit" and raw.get("independent_approval") is False, "AUTHOR_CAL_HEADER")
    need(same(raw.get("source_software"), software) and same(raw.get("outcome", {}).get("counts"), CONTROL_COUNTS)
         and raw["outcome"].get("stage_mismatches") == [] and type(raw.get("outputs_sha256")) is dict, "AUTHOR_CAL_SCOPE")
    root = safe(raw["output_root"])
    need(len(raw["outputs_sha256"]) == 50 and set(p.name for p in root.iterdir()) == set(raw["outputs_sha256"]) | {"summary.json"}, "AUTHOR_CAL_POPULATION")
    for name, digest in raw["outputs_sha256"].items():
        need(type(name) is str and Path(name).name == name, "AUTHOR_CAL_NAME")
        reader.read(str(root/name), digest, False)


def scientific(reader, functions, config, out, software):
    need(type(config) is dict and config.get("schema") == "FIXED17_FOCAL_NEIGHBOR_INTEGER_CONFIGURATION_V1"
         and config.get("target_resolution") == "NONE" and type(config.get("inputs_sha256")) is dict, "CONFIG_HEADER")
    required = {**COUNT_PINS, COUNT_GATE_PATH:COUNT_GATE_SHA, COUNT_ROOT_PATH:COUNT_ROOT_SHA,
                PAIR_GATE_PATH:PAIR_GATE_SHA, PAIR_ROOT_PATH:PAIR_ROOT_SHA, PROOF_PATH:PROOF_SHA}
    need(all(config["inputs_sha256"].get(p) == digest for p, digest in required.items()), "CONFIG_DIRECT_PINS")
    need(type(config.get("per_focal_solver_seconds")) in (int, float) and 0 < config["per_focal_solver_seconds"] <= 10,
         "CONFIG_SOLVER_SECONDS")
    reader.mapping(config["inputs_sha256"])
    cal = reader.read(config["author_calibration_path"], config["author_calibration_sha256"])
    qualify_calibration(reader, cal, software)
    gate = reader.read(COUNT_GATE_PATH, COUNT_GATE_SHA)
    functions["count_gate"](gate, COUNT_PINS)
    parsed = reader.read(COUNT_BASE+"parsed_fixed_input.json", COUNT_PINS[COUNT_BASE+"parsed_fixed_input.json"])
    candidate = reader.read(COUNT_BASE+"exact_integer_candidate.json", COUNT_PINS[COUNT_BASE+"exact_integer_candidate.json"])
    need(type(candidate) is dict and candidate.get("schema") == "FIXED17_EXACT_INTEGER_TYPE_COUNTS_V1"
         and candidate.get("integer") is True and candidate.get("exact_constraints") is True
         and candidate.get("independent_approval") is False and candidate.get("graph_completion") is False, "COUNT_CANDIDATE_HEADER")
    masks = candidate.get("ordered_masks")
    need(type(masks) is list and len(masks) == 472 and same(parsed.get("ordered_masks"), masks), "COUNT_MASKS")
    table = functions["raw_pairs"](reader, masks, reader.read(PAIR_GATE_PATH, PAIR_GATE_SHA))
    payload = dict(target_order=99, target_degree=14, support_adjacency=parsed["induced_adjacency"],
                   ordered_masks=masks, counts=candidate["counts"], pair_bits=table)
    h, _, counts, _ = functions["packet"](payload)
    positive = [i for i, n in enumerate(counts) if n]
    need(len(h) == 17 and sum(counts) == 82 and len(positive) == 68, "FIXED_SCOPE")
    save(out/"parsed_focal_input.json", payload, reader.deadline)
    decisions, calls, solver_elapsed = [], 0, 0.0
    for completed, i in enumerate(positive, 1):
        tick(reader.deadline)
        prefix = "type_%03d" % i
        model = focal_model(payload, i, functions["packet"], reader.deadline)
        save(out/(prefix+"_model.json"), model, reader.deadline)
        bound = bound_witness(model)
        witness_path, guidance_path = None, None
        if bound is None:
            guidance = native(model, out, prefix, reader.deadline, config["per_focal_solver_seconds"])
            calls += 1
            solver_elapsed += guidance["wall_seconds"]
            guidance_path = prefix+"_guidance.json"
            decision = extract(model, guidance, reader.deadline)
            if decision["candidate"] is not None:
                values = decision["candidate"]
                labels = check_labels(model, values, chosen_labels(model, values), reader.deadline)
                witness = dict(schema="FIXED17_EXACT_FOCAL_NEIGHBOR_VECTOR_V1", focal_type=i, focal_label=[i, 0],
                    ordered_masks=masks, neighbor_counts=values, **labels, exact_rows=decision["rows"],
                    exact_constraints=True, independent_approval=False, graph_completion=False,
                    same_type_uniform_profile_claimed=False)
                witness_path = prefix+"_witness.json"
                save(out/witness_path, witness, reader.deadline)
                status = "CANDIDATE_EXACT_LOCAL_NEIGHBOR_CHOICE"
            else:
                status = "UNKNOWN_NO_EXACT_LOCAL_NEIGHBOR_VECTOR"
        else:
            decision = dict(candidate=None, exact_simple_bound=bound,
                            reason="A directly reconstructed necessary bound fails; independent replay required",
                            numeric_infeasibility_is_proof=False)
            status = "CANDIDATE_EXACT_SIMPLE_BOUND_FAILURE"
        decision.update(focal_type=i, status=status, guidance_path=guidance_path, witness_path=witness_path,
                        graph_completion=False, infeasibility_from_numeric_status=False)
        save(out/(prefix+"_decision.json"), decision, reader.deadline)
        decisions.append(dict(focal_type=i, status=status, witness_path=witness_path, guidance_path=guidance_path))
        save(out/("checkpoint_%03d.json" % i), dict(schema="FIXED17_FOCAL_NEIGHBOR_CHECKPOINT_V1", completed_types=completed,
             positive_type_prefix=positive[:completed], decisions=list(decisions), scientific_solver_calls=calls,
             solver_wall_seconds=solver_elapsed, target_resolution="NONE", automatic_retry=False), reader.deadline)
        print(json.dumps(dict(completed_types=completed, focal_type=i, status=status)), flush=True)
    outcome = dict(outside_copies=82, positive_types=68, all_type_variables=472, equalities_per_focal=18,
        complete_equalities_checked_for_witnesses=True, completed_focal_types=len(decisions), decisions=decisions,
        exact_neighbor_witnesses=sum(d["witness_path"] is not None for d in decisions),
        exact_simple_bound_failures=sum(d["status"] == "CANDIDATE_EXACT_SIMPLE_BOUND_FAILURE" for d in decisions),
        unknown_focal_types=sum(d["status"] == "UNKNOWN_NO_EXACT_LOCAL_NEIGHBOR_VECTOR" for d in decisions),
        scientific_solver_calls=calls, solver_wall_seconds=solver_elapsed,
        every_focal_has_exact_choice=all(d["witness_path"] is not None for d in decisions),
        graph_completion=False, numerical_infeasibility_proves_nothing=True, uniform_profiles=False)
    save(out/"focal_neighbor_outcome.json", outcome, reader.deadline)
    return outcome


def output_hashes(out, deadline):
    result = {}
    for path in sorted(out.iterdir()):
        tick(deadline)
        need(path.is_file() and not path.is_symlink() and path.suffix != ".tmp", "OUTPUT_POPULATION")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                tick(deadline)
                block = handle.read(1024*1024)
                if not block:
                    break
                digest.update(block)
        result[path.name] = digest.hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "solve"))
    for name in ("seconds", "out", "self-sha256", "spec-sha256", "executor"):
        parser.add_argument("--"+name, required=True, type=float if name == "seconds" else str)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="One individual neighbor-profile integer test for every positive type, or fresh finite controls; authentication/solver/saves share this invocation")
    out = safe(args.out)
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(), "OUTPUT_FRESH_SCOPE")
    out.mkdir(parents=True)
    reader = Reader(deadline)
    software = {**SOFTWARE, SELF.relative_to(ROOT).as_posix():args.self_sha256, SPEC.relative_to(ROOT).as_posix():args.spec_sha256}
    try:
        reader.mapping(software)
        functions = helper_functions(reader)
        author = controls(out, deadline, functions)
        if args.mode == "calibrate":
            outcome, status = author, CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None, "CONFIG_ARGUMENTS")
            config = reader.read(args.configuration, args.configuration_sha256)
            outcome = scientific(reader, functions, config, out, software)
            status = "CANDIDATE_FIXED17_FOCAL_NEIGHBOR_INTEGER_SYSTEMS_V1"
        reader.closing()
        outputs = output_hashes(out, deadline)
        if args.mode == "calibrate":
            need(len(outputs) == 50, "AUTHOR_OUTPUT_COUNT")
        report = dict(schema="FIXED17_FOCAL_NEIGHBOR_INTEGER_PRODUCER_REPORT_V1", status=status, implementation_version=1,
            timestamp=datetime.now(timezone.utc).isoformat(), mode=args.mode, producer="/root/checkpoint_audit",
            source_author="/root/checkpoint_audit", executor_declaration=args.executor,
            executor_identity_requires_external_runtime_receipt=True, independent_approval=False,
            independent_verifier=None, independent_verifier_null_reason="Fresh distinct implementation/control and raw vector/model checks required",
            independent_verifier_required="/root/native_driver", target_resolution="NONE", source_software=software,
            inputs_sha256=dict(reader.pins), outputs_sha256=outputs, output_root=out.relative_to(ROOT).as_posix(),
            author_controls=author, outcome=outcome, command=sys.argv, cwd=str(ROOT), deadline=deadline.status(),
            native_solver_calls=author["native_solver_calls"]+outcome.get("scientific_solver_calls", 0),
            actual_count_witness_read=args.mode == "solve", automatic_retry=False, ledger_index_git_mutations=0,
            shared_components=["Pinned producer-side packet/count-gate/raw-pair AST functions from old capacity source, no old scientific screen/main imports",
                "Pinned common Python/json/SHA/deadline and highspy1.15.1/NumPy runtime; new model/controls not approved by old gates",
                "Root proposed stronger simultaneous-coordinate experiment; Structural/Native block theorem is an independent immutable mathematical premise"],
            limitations=["An exact local neighbor choice is sufficient for one labeled focal row only, not for symmetric choices or a whole graph",
                "No uniform/equitable profiles: each same-type actual vertex may make a different local choice",
                "Absent exact incumbent, numerical infeasibility, timeout or gap is UNKNOWN, never count-witness or target exclusion",
                "Simple exact-bound failures are candidate necessary-obstruction data until independent replay",
                "Completed per-type artifacts/checkpoints persist; hard stop/unexpected exceptions may lose the in-memory current suffix",
                "Prefix reuse requires a separately authorized new invocation/root and authenticated source/input identities; no automatic retry/resume",
                "20-second closing guard and outer containment are engineering scope, not an OS/filesystem hard-real-time guarantee"])
        save(out/"summary.json", report, deadline)
        reader.closing()
        tick(deadline)
        print(json.dumps(dict(status=status, exact_neighbor_witnesses=outcome.get("exact_neighbor_witnesses"), unknown_focal_types=outcome.get("unknown_focal_types"))), flush=True)
    except Exception as exc:
        try:
            (out/"failure.json").write_text(json.dumps(dict(status="FAILED_PRESERVED", stage=str(exc), exception=type(exc).__name__,
                timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=reader.pins, target_resolution="NONE",
                automatic_retry=False, deadline=deadline.status()), indent=2, allow_nan=False)+"\n", encoding="utf8")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
