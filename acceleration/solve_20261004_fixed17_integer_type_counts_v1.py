"""SOURCE ONLY: complete fixed17 necessary integer type-count feasibility."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
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
BASE = "acceleration/results/20261003_external_moment_outside_cn_filter01/"
FIXED = {
    BASE + "filtered_system.json": "c628c76325d5b49106740bce7c6d3b72bc7728fdc78d85437ad484f3afbd7306",
    BASE + "types.json": "87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2",
}
PAIR_SOURCE = {
    "acceleration/audit_20261004_fixed17_dual_gram_pairs_v2.py": "7f7b9f965d2d6051af7614c4a7ab2737504a455eeb086f9b96b9d9ead57fe3bf",
    "acceleration/audit_20261004_fixed17_dual_gram_pairs_v2_spec.md": "e3728e455da83f4291b361931c944902fb54e7384e54b3a49901ced92f04e032",
}
PAIR_STATUS = "INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS"
PAIR_PARSED_INPUT = "acceleration/results/20261004_fixed17_dual_gram_singletons01/parsed_input.json"
PAIR_PARSED_INPUT_SHA = "fa363f43b1e3de238c330b0b9caaf4e2c61dd8e1f7dc7044d3817b02b3b246b5"
CAL_STATUS = "FIXED17_INTEGER_TYPE_COUNTS_V1_AUTHOR_CONTROLS_PASS"
PAIR_FIELDS = ("proposal_id", "i", "j", "left_mask", "right_mask", "intersection",
    "upper_left_diagonal", "upper_right_diagonal", "upper_cross_0", "upper_cross_1",
    "lower_left_diagonal", "lower_right_diagonal", "lower_cross_0", "lower_cross_1",
    "upper_bits", "lower_bits", "cn_bits", "combined_bits", "classification")
CLASSES = {(): "incompatible", (0,): "forced_nonadjacent", (1,): "forced_adjacent", (0, 1): "either"}
MAX_BYTES = 64 * 1024 * 1024
ROUND_TOLERANCE = 1e-7
CONTROL_COUNTS = dict(positive=11, negative=30, total=41)


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


def solver_seconds(deadline, maximum):
    remaining = tick(deadline)["remaining_seconds"]
    seconds = min(float(maximum), remaining - 180)
    need(seconds > 0, "SOLVER_RESERVE")
    return seconds


def safe(raw):
    need(type(raw) is str and raw and "\x00" not in raw, "PATH_STRING")
    path = Path(raw)
    path = (ROOT / path) if not path.is_absolute() else path
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
    def nonfinite(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


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
                block = handle.read(1024 * 1024)
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

    def map(self, raw):
        need(type(raw) is dict and raw, "INPUT_MAP")
        for path, digest in raw.items():
            self.read(path, digest, False)

    def closing(self):
        self.map(dict(self.pins))


def save(path, value, deadline):
    tick(deadline)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf8")
    need(len(raw) <= MAX_BYTES, "OUTPUT_BOUND")
    tick(deadline)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    tick(deadline)
    os.replace(temporary, path)
    tick(deadline)


def coefficients(raw_types, size):
    need(type(raw_types) is list and raw_types, "TYPES_SHAPE")
    masks, columns, previous = [], [], -1
    for row in raw_types:
        need(type(row) is dict and set(row) == {"mask", "coefficient"}, "TYPE_FIELDS")
        mask = row["mask"]
        need(type(mask) is int and 0 <= mask < 1 << size, "TYPE_MASK_INTEGER")
        need(mask > previous, "TYPE_MASK_ORDER")
        previous = mask
        bits = [(mask >> i) & 1 for i in range(size)]
        expected = [1] + bits + [bits[i] * bits[j] for i, j in itertools.combinations(range(size), 2)]
        need(same(row["coefficient"], expected), "TYPE_COEFFICIENT")
        masks.append(mask)
        columns.append(expected)
    return masks, [[col[i] for col in columns] for i in range(len(columns[0]))]


def geometry(h, target_order, target_degree):
    need(type(h) is list, "GRAPH_SHAPE")
    m = len(h)
    need(m > 0 and all(type(row) is list and len(row) == m for row in h), "GRAPH_SHAPE")
    need(all(type(x) is int and x in (0, 1) for row in h for x in row)
         and all(h[i][i] == 0 and h[i][j] == h[j][i] for i in range(m) for j in range(m)), "GRAPH_DOMAIN")
    rhs = [target_order - m] + [target_degree - sum(row) for row in h]
    rhs += [2 - h[i][j] - sum(h[i][k] * h[j][k] for k in range(m))
            for i, j in itertools.combinations(range(m), 2)]
    labels = [dict(kind="total")] + [dict(kind="vertex", vertex=i) for i in range(m)]
    labels += [dict(kind="pair", vertices=list(pair)) for pair in itertools.combinations(range(m), 2)]
    return rhs, labels


def moment_identity(raw, expected_a, expected_rhs):
    need(type(raw) is dict and set(raw) == {"matrix", "rhs"}, "MOMENT_KEYS")
    need(type(raw["matrix"]) is list and all(type(row) is list and all(type(x) is int for x in row)
         for row in raw["matrix"]) and type(raw["rhs"]) is list and all(type(x) is int for x in raw["rhs"]), "MODEL_INTEGER")
    need(same(raw["matrix"], expected_a), "MODEL_COEFFICIENT_IDENTITY")
    need(same(raw["rhs"], expected_rhs), "MODEL_RHS_IDENTITY")


def pair_gate(raw, required):
    need(type(raw) is dict and raw.get("status") == PAIR_STATUS and raw.get("mode") == "full"
         and type(raw.get("implementation_version")) is int and raw["implementation_version"] == 2
         and raw.get("producer") == "/root/structural" and raw.get("verifier") == "/root/native_driver"
         and raw.get("method") == "independent_artifact_check" and raw.get("target_resolution") == "NONE", "PAIR_GATE_HEADER")
    need(type(raw.get("inputs_sha256")) is dict and all(raw["inputs_sha256"].get(p) == h for p, h in required.items()), "PAIR_GATE_DIRECT_PINS")
    counts = dict(complete_pair_records=111628, complete_record_fields=19, complete_parts=23,
                  complete_checkpoints=23, final_part_records=1628, complete_scaled_type_vectors=472,
                  complete_induced_adjacency_entries=289, complete_raw_physical_files=48)
    need(type(raw.get("outcome")) is dict and all(type(raw["outcome"].get(k)) is int and raw["outcome"][k] == v
         for k, v in counts.items()) and raw["outcome"].get("equal_types_are_distinct_external_vertices") is True
         and raw["outcome"].get("same_adjacency_bit_required") is True, "PAIR_GATE_COUNTS")


def pair_record(row, proposal, i, j, masks):
    need(type(row) is dict and set(row) == set(PAIR_FIELDS), "PAIR_RECORD_KEYS")
    need(all(type(row[k]) is int for k in PAIR_FIELDS[:14]), "PAIR_RECORD_INTEGER")
    need(same([row[k] for k in ("proposal_id", "i", "j", "left_mask", "right_mask")],
              [proposal, i, j, masks[i], masks[j]]) and row["intersection"] == (masks[i] & masks[j]).bit_count(), "PAIR_COORDINATES")
    for key in PAIR_FIELDS[14:18]:
        need(type(row[key]) is list and all(type(bit) is int and bit in (0, 1) for bit in row[key])
             and row[key] == sorted(set(row[key])), "PAIR_BITS")
    joint = sorted(set(row["upper_bits"]) & set(row["lower_bits"]) & set(row["cn_bits"]))
    need(same(row["combined_bits"], joint) and row["classification"] == CLASSES[tuple(joint)], "PAIR_INTERSECTION")
    return not joint


def integer_model(masks, moments, rhs, triples, forbidden, equal_forbidden):
    n = len(masks)
    upper = [1 if mask.bit_count() >= 3 or i in equal_forbidden else 82 for i, mask in enumerate(masks)]
    rows = []
    for i, (coeff, value) in enumerate(zip(moments, rhs)):
        rows.append(dict(kind="moment", origin=i, lower=value, upper=value,
                         terms=[[j, c] for j, c in enumerate(coeff) if c]))
    for q in triples:
        qm = sum(1 << i for i in q)
        rows.append(dict(kind="triple", origin=list(q), lower=None, upper=1,
                         terms=[[j, 1] for j, mask in enumerate(masks) if mask & qm == qm]))
    for i, bound in enumerate(upper):
        rows.append(dict(kind="presence_lower", origin=i, lower=0, upper=None, terms=[[i, 1], [n+i, -1]]))
        rows.append(dict(kind="presence_upper", origin=i, lower=None, upper=0, terms=[[i, 1], [n+i, -bound]]))
    for i, j in forbidden:
        rows.append(dict(kind="forbidden_pair", origin=[i, j], lower=None, upper=1, terms=[[n+i, 1], [n+j, 1]]))
    return dict(schema="FIXED17_INTEGER_TYPE_COUNT_MODEL_V1", ordered_masks=masks, count_variables=n,
                presence_variables=n, variables=2*n, objective=[0]*(2*n), lower=[0]*(2*n), upper=upper+[1]*n,
                all_columns_integer=True, rows=rows, moment_rhs=rhs, moments=moments,
                triples=[list(q) for q in triples], forbidden_distinct_pairs=[list(x) for x in forbidden],
                equal_forbidden_indices=sorted(equal_forbidden), target_graph=False)


def check_counts(model, counts, presence, deadline):
    n = model["count_variables"]
    need(type(counts) is list and len(counts) == n, "COUNT_POPULATION")
    need(all(type(x) is int for x in counts), "COUNT_INTEGER")
    need(all(0 <= x <= bound for x, bound in zip(counts, model["upper"][:n])), "COUNT_BOUND")
    need(type(presence) is list and len(presence) == n, "PRESENCE_POPULATION")
    need(all(type(x) is int and x in (0, 1) for x in presence), "PRESENCE_INTEGER")
    need(all(p == int(x > 0) for x, p in zip(counts, presence)), "PRESENCE_EQUIVALENCE")
    records = []
    for i, (row, rhs) in enumerate(zip(model["moments"], model["moment_rhs"])):
        tick(deadline)
        lhs = sum(c*x for c, x in zip(row, counts))
        need(lhs == rhs, "MOMENT_EQUALITY")
        records.append(dict(kind="moment", index=i, lhs=lhs, rhs=rhs))
    masks = model["ordered_masks"]
    for q in model["triples"]:
        tick(deadline)
        qm = sum(1 << i for i in q)
        lhs = sum(x for mask, x in zip(masks, counts) if mask & qm == qm)
        need(lhs <= 1, "TRIPLE_CAP")
        records.append(dict(kind="triple", vertices=q, lhs=lhs, upper=1))
    for i, j in model["forbidden_distinct_pairs"]:
        tick(deadline)
        need(not (counts[i] > 0 and counts[j] > 0), "PAIR_PRESENCE_NOGOOD")
        records.append(dict(kind="forbidden_pair", i=i, j=j, lhs=presence[i]+presence[j], upper=1))
    values = counts + presence
    for row in model["rows"]:
        tick(deadline)
        lhs = sum(c*values[j] for j, c in row["terms"])
        need((row["lower"] is None or lhs >= row["lower"]) and
             (row["upper"] is None or lhs <= row["upper"]), "SPARSE_ROW_EXACT")
    return records


def native(model, seconds, out, prefix, deadline, reserve):
    # These imports and one run() per call are inside the supervised invocation.
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
    lp.integrality_ = [highspy.HighsVarType.kInteger] * lp.num_col_
    lp.row_lower_ = np.asarray([-highspy.kHighsInf if r["lower"] is None else r["lower"] for r in model["rows"]], dtype=np.float64)
    lp.row_upper_ = np.asarray([highspy.kHighsInf if r["upper"] is None else r["upper"] for r in model["rows"]], dtype=np.float64)
    starts, indices, values = [0], [], []
    for row in model["rows"]:
        tick(deadline)
        for j, c in row["terms"]:
            need(type(j) is int and type(c) is int and abs(c) <= 82, "SPARSE_INTEGER_COEFFICIENT")
            indices.append(j)
            values.append(c)
        starts.append(len(indices))
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = np.asarray(starts, dtype=np.int32), np.asarray(indices, dtype=np.int32), np.asarray(values, dtype=np.float64)
    options = dict(presolve="on", solver="choose", threads=1, parallel="off", random_seed=0,
                   mip_feasibility_tolerance=ROUND_TOLERANCE, primal_feasibility_tolerance=ROUND_TOLERANCE,
                   mip_rel_gap=0.0, mip_abs_gap=0.0, output_flag=True, log_to_console=False,
                   log_file=str(out/(prefix+"_solver.log")), time_limit=float(seconds))
    for key, value in options.items():
        need(solver.setOptionValue(key, value) == highspy.HighsStatus.kOk, "HIGHS_OPTION:"+key)
    need(solver.passModel(lp) == highspy.HighsStatus.kOk, "HIGHS_MODEL")
    # Sparse construction, imports, options and passModel consumed this SAME deadline.
    actual_seconds = min(float(seconds),tick(deadline)["remaining_seconds"]-reserve)
    need(actual_seconds > 0,"SOLVER_RESERVE")
    need(solver.setOptionValue("time_limit",actual_seconds) == highspy.HighsStatus.kOk,"HIGHS_OPTION:time_limit")
    options["time_limit"] = actual_seconds
    started = time.monotonic()
    run_status = solver.run()
    elapsed = time.monotonic() - started
    tick(deadline)
    solution, info = solver.getSolution(), solver.getInfo()
    floats = [float(x) for x in solution.col_value]
    need(all(math.isfinite(x) for x in floats), "NATIVE_NONFINITE_VECTOR")
    fields = ("mip_node_count", "mip_gap", "mip_dual_bound", "objective_function_value",
              "max_integrality_violation", "max_primal_infeasibility", "primal_solution_status")
    def finite_field(value):
        if type(value) is int:
            return value
        number = float(value)
        return number if math.isfinite(number) else dict(nonfinite=str(number), is_proof=False)
    guidance = dict(schema="FIXED17_INTEGER_TYPE_COUNT_NUMERIC_GUIDANCE_V1", native_version=solver.version(),
        numpy_version=np.__version__, run_status=str(run_status), model_status=str(solver.getModelStatus()),
        solution_value_valid=bool(solution.value_valid), col_value=floats, col_value_float_hex=[x.hex() for x in floats],
        info={key:finite_field(getattr(info, key)) for key in fields}, options=options, wall_seconds=elapsed,
        solver_calls=1, objective_all_zero=True, floating_status_is_proof=False, numeric_infeasibility_is_proof=False)
    save(out/(prefix+"_guidance.json"), guidance, deadline)
    return guidance


def extract(model, guidance, deadline):
    values = guidance["col_value"]
    if not guidance["solution_value_valid"] or len(values) != model["variables"]:
        return dict(candidate=None, reason="No complete value-valid numerical incumbent", rounding_tolerance=ROUND_TOLERANCE)
    integers = [int(round(x)) for x in values]
    distances = [abs(x-y) for x, y in zip(values, integers)]
    if any(d > ROUND_TOLERANCE for d in distances):
        return dict(candidate=None, reason="Numerical coordinate farther from integer than declared extraction threshold",
                    rounding_tolerance=ROUND_TOLERANCE, max_rounding_distance=max(distances))
    n = model["count_variables"]
    try:
        rows = check_counts(model, integers[:n], integers[n:], deadline)
    except ValueError as exc:
        if str(exc) == "SAVE_RESERVE":
            raise
        return dict(candidate=None, reason="Exact integer extraction rejected: "+str(exc),
                    rounding_tolerance=ROUND_TOLERANCE, rounded_values=integers, max_rounding_distance=max(distances))
    return dict(candidate=dict(schema="FIXED17_EXACT_INTEGER_TYPE_COUNTS_V1", ordered_masks=model["ordered_masks"],
        counts=integers[:n], presence=integers[n:], integer=True, exact_constraints=True,
        independent_approval=False, graph_completion=False), exact_rows=rows,
        rounding_tolerance=ROUND_TOLERANCE, max_rounding_distance=max(distances),
        statement="Exact integer extraction passes this necessary count model only; independent raw checking is required.")


def controls(out, deadline):
    masks = [0, 1, 2, 3, 7, 15]
    a = [[1]*6] + [[(mask >> i) & 1 for mask in masks] for i in range(4)]
    fixture = integer_model(masks, a, [3, 1, 1, 1, 0], list(itertools.combinations(range(4), 3)), [(1, 2)], {2})
    def payload(counts, rhs=None):
        m = copy.deepcopy(fixture)
        if rhs is not None:
            m["moment_rhs"] = rhs
            for i, value in enumerate(rhs):
                m["rows"][i]["lower"] = m["rows"][i]["upper"] = value
        return dict(model=m, counts=counts, presence=[int(x > 0) for x in counts])
    check = lambda p:check_counts(p["model"], p["counts"], p["presence"], deadline)
    base = payload([2, 0, 0, 0, 1, 0])
    routes = [("low_type_multiplicity_two", "PASS", base, check),
        ("allowed_low_type_pair_total_three", "PASS", payload([0, 2, 0, 1, 0, 0], [3,3,1,0,0]), check),
        ("high_type_one", "PASS", payload([0,0,0,0,1,0], [1,1,1,1,0]), check),
        ("equal_forbidden_single_copy", "PASS", payload([0,0,1,0,0,0], [1,0,1,0,0]), check),
        ("exact_presence_link", "PASS", copy.deepcopy(base), check)]
    h = [[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]]
    rook_masks = [0,3,5,10,12]
    raw_types = [dict(mask=mask, coefficient=[1]+[(mask >> i)&1 for i in range(4)]
        + [((mask >> i)&1)*((mask >> j)&1) for i,j in itertools.combinations(range(4),2)]) for mask in rook_masks]
    _, rook_a = coefficients(raw_types, 4)
    rook_rhs, _ = geometry(h, 9, 4)
    need(same(rook_rhs, [5,2,2,2,2,1,1,0,0,1,1]), "ROOK_LITERAL_RHS")
    rook_payload = dict(matrix=rook_a, rhs=rook_rhs)
    def rook_check(p):
        moment_identity(p, rook_a, [5,2,2,2,2,1,1,0,0,1,1])
        m = integer_model(rook_masks, p["matrix"], p["rhs"], list(itertools.combinations(range(4),3)), [], set())
        check_counts(m, [1]*5, [1]*5, deadline)
    routes.append(("known_rook_exterior_five", "PASS", rook_payload, rook_check))
    gate = dict(status=PAIR_STATUS, mode="full", implementation_version=2, producer="/root/structural",
        verifier="/root/native_driver", method="independent_artifact_check", target_resolution="NONE",
        inputs_sha256={"synthetic":"pin"}, outcome=dict(complete_pair_records=111628, complete_record_fields=19,
        complete_parts=23, complete_checkpoints=23, final_part_records=1628, complete_scaled_type_vectors=472,
        complete_induced_adjacency_entries=289, complete_raw_physical_files=48,
        equal_types_are_distinct_external_vertices=True, same_adjacency_bit_required=True))
    gate_check = lambda p:pair_gate(p, {"synthetic":"pin"})
    routes.append(("canonical_pair_gate", "PASS", gate, gate_check))
    class FixedClock:
        def __init__(self, payload):self.payload = payload
        def status(self):return self.payload
    budget_check = lambda p:solver_seconds(FixedClock(p), 1500)
    routes.append(("solver_budget_above_reserve", "PASS", dict(stop_required=False, remaining_seconds=181), budget_check))
    for name, field, value, stage in [
        ("count_bool","counts",[True,0,0,0,1,0],"COUNT_INTEGER"),
        ("count_float","counts",[2.0,0,0,0,1,0],"COUNT_INTEGER"),
        ("count_missing","counts",[2,0,0,0,1],"COUNT_POPULATION"),
        ("count_negative","counts",[-1,0,0,0,1,0],"COUNT_BOUND"),
        ("count_over82","counts",[83,0,0,0,1,0],"COUNT_BOUND"),
        ("high_type_multiple","counts",[2,0,0,0,2,0],"COUNT_BOUND"),
        ("equal_forbidden_multiple","counts",[2,0,2,0,1,0],"COUNT_BOUND"),
        ("wrong_moment","counts",[1,0,0,0,1,0],"MOMENT_EQUALITY"),
        ("presence_bool","presence",[True,0,0,0,1,0],"PRESENCE_INTEGER"),
        ("presence_missing","presence",[1,0,0,0,1],"PRESENCE_POPULATION"),
        ("wrong_presence_link","presence",[0,0,0,0,1,0],"PRESENCE_EQUIVALENCE")]:
        p = copy.deepcopy(base)
        p[field] = value
        # Keep equivalence valid for the wrong-moment fixture so that row checking is first.
        if name == "wrong_moment":p["presence"] = [1,0,0,0,1,0]
        routes.append((name,stage,p,check))
    routes += [("triple_violation","TRIPLE_CAP",payload([1,0,0,0,1,1],[3,2,2,2,1]),check),
               ("forbidden_low_type_pair","PAIR_PRESENCE_NOGOOD",payload([1,1,1,0,0,0],[3,1,1,0,0]),check)]
    for name, field, value, stage in [("type_mask_bool","mask",True,"TYPE_MASK_INTEGER"),
        ("type_mask_float","mask",0.0,"TYPE_MASK_INTEGER"), ("type_order","mask",3,"TYPE_MASK_ORDER"),
        ("coefficient_bool","coefficient",True,"TYPE_COEFFICIENT"),
        ("coefficient_float","coefficient",1.0,"TYPE_COEFFICIENT")]:
        p = copy.deepcopy(raw_types)
        if field == "coefficient":p[0][field][0] = value
        elif name == "type_order":p[2][field] = value
        else:p[0][field] = value
        routes.append((name,stage,p,lambda q:coefficients(q,4)))
    for name, field, value in [("pair_gate_bool_version","implementation_version",True),
        ("pair_gate_old_version","implementation_version",1), ("pair_gate_method_alias","method",None)]:
        p = copy.deepcopy(gate)
        p[field] = value
        if name == "pair_gate_method_alias":p["verification_method"] = "independent_artifact_check"
        routes.append((name,"PAIR_GATE_HEADER",p,gate_check))
    p = copy.deepcopy(gate)
    p["outcome"]["complete_pair_records"] = 111627
    routes.append(("pair_gate_incomplete","PAIR_GATE_COUNTS",p,gate_check))
    record = dict(zip(PAIR_FIELDS[:14], [0,0,0,0,0,0,0,0,0,0,0,0,0,0]))
    record.update(upper_bits=[0,1], lower_bits=[0,1], cn_bits=[0,1], combined_bits=[0,1], classification="either")
    for name, field, value, stage in [("pair_record_bool","proposal_id",False,"PAIR_RECORD_INTEGER"),
        ("pair_bits_bool","cn_bits",[False,1],"PAIR_BITS"),
        ("pair_combined_mismatch","combined_bits",[],"PAIR_INTERSECTION")]:
        p = copy.deepcopy(record)
        p[field] = value
        routes.append((name,stage,p,lambda q:pair_record(q,0,0,0,[0])))
    routes += [("budget_at_reserve","SOLVER_RESERVE",dict(stop_required=False,remaining_seconds=180),budget_check),
               ("budget_expired","SAVE_RESERVE",dict(stop_required=False,remaining_seconds=0),budget_check),
               ("budget_review_due","SAVE_RESERVE",dict(stop_required=True,remaining_seconds=500),budget_check)]
    for name, field, value, stage in [("wrong_rhs","rhs",[5,3,2,2,2,1,1,0,0,1,1],"MODEL_RHS_IDENTITY"),
        ("wrong_integer_coefficient","matrix",None,"MODEL_COEFFICIENT_IDENTITY")]:
        p = copy.deepcopy(rook_payload)
        if value is None:p[field][0][0] = 0
        else:p[field] = value
        routes.append((name,stage,p,rook_check))
    table = []
    for name, expected, p, function in routes:
        save(out/(name+".json"), p, deadline)
        actual = "PASS"
        try:function(copy.deepcopy(p))
        except ValueError as exc:actual = str(exc)
        need(actual == expected, "CONTROL_STAGE:"+name+":"+actual)
        table.append(dict(name=name,expected_stage=expected,actual_stage=actual))
    # New local backend/API controls: zero objective; no scientific gate read.
    tiny = [("native_low_multiplicity",[1],[[1]],[2],True),
            ("native_rational_only",[1],[[2]],[1],False),
            ("native_allowed_low_pair",[1,3],[[1,1]],[3],True)]
    for name, tiny_masks, matrix, rhs, feasible in tiny:
        m = integer_model(tiny_masks,matrix,rhs,[],[],set())
        save(out/(name+"_model.json"),m,deadline)
        tick(deadline)
        raw = native(m,min(2.0,tick(deadline)["remaining_seconds"]-20),out,name,deadline,20)
        result = extract(m,raw,deadline)
        save(out/(name+"_extraction.json"),result,deadline)
        if feasible:
            need(result["candidate"] is not None,"TINY_INTEGER_WITNESS")
        else:
            # Exhaust this one-coordinate exact domain; floating infeasible is not its proof.
            need(all(2*n != 1 for n in range(83)) and result["candidate"] is None,"TINY_NO_INTEGER_WITNESS")
        table.append(dict(name=name,expected_stage="PASS",actual_stage="PASS"))
    need(len(table) == CONTROL_COUNTS["total"] and sum(r["expected_stage"] == "PASS" for r in table) == CONTROL_COUNTS["positive"], "CONTROL_COUNTS")
    save(out/"controls.json",table,deadline)
    return dict(controls=CONTROL_COUNTS, backend_fixture_calls=3, actual_target_input_read=False,
                genuine_pair_gate_read=False, known_rook_exterior_vertices=5, tiny_integer_domain_oracle_values=83)


def scientific(reader, config, out):
    deadline = reader.deadline
    need(type(config) is dict and config.get("schema") == "FIXED17_INTEGER_TYPE_COUNTS_CONFIGURATION_V1", "CONFIG_HEADER")
    need(config.get("source_sha256") == reader.pins[SELF.relative_to(ROOT).as_posix()]
         and config.get("spec_sha256") == reader.pins[SPEC.relative_to(ROOT).as_posix()], "CONFIG_SOURCE")
    reader.map(config.get("inputs_sha256"))
    # Administrative acceptance is byte-bound by the new reviewed configuration;
    # its schema is not treated as a generic mathematical gate or role waiver.
    reader.read(config["pair_root_acceptance_path"],config["pair_root_acceptance_sha256"])
    gate = reader.read(config["pair_gate_path"],config["pair_gate_sha256"])
    pair_gate(gate,{**FIXED,**PAIR_SOURCE})
    reader.map(gate["inputs_sha256"])
    calibration = reader.read(config["author_calibration_path"],config["author_calibration_sha256"])
    need(calibration.get("status") == CAL_STATUS and same(calibration.get("outcome",{}).get("controls"),CONTROL_COUNTS)
         and same(calibration.get("source_software"), {**SOFTWARE,SELF.relative_to(ROOT).as_posix():reader.pins[SELF.relative_to(ROOT).as_posix()],
         SPEC.relative_to(ROOT).as_posix():reader.pins[SPEC.relative_to(ROOT).as_posix()]}), "AUTHOR_CALIBRATION")
    reader.map(calibration["inputs_sha256"])
    for name, digest in calibration["outputs_sha256"].items():
        reader.read(str(safe(config["author_calibration_path"]).parent/name),digest,False)
    table = reader.read(str(safe(config["author_calibration_path"]).parent/"controls.json"),calibration["outputs_sha256"]["controls.json"])
    need(type(table) is list and len(table) == 41 and all(type(row) is dict and
         type(row.get("expected_stage")) is str and row.get("actual_stage") == row["expected_stage"] for row in table)
         and sum(row["expected_stage"] == "PASS" for row in table) == 11,"AUTHOR_CALIBRATION_TABLE")
    source_model = reader.read(BASE+"filtered_system.json",FIXED[BASE+"filtered_system.json"])
    source_types = reader.read(BASE+"types.json",FIXED[BASE+"types.json"])
    need(source_model.get("schema") == "OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1" and
         all(type(source_model.get(k)) is int and source_model[k] == v for k,v in
             [("target_order",99),("target_degree",14),("adjacent_cn",1),("nonadjacent_cn",2),("eligible_type_count",472)])
         and same(source_model.get("ordered_support_vertices"),list(range(17))), "FIXED_MODEL_HEADER")
    masks, moments = coefficients(source_types,17)
    need(len(masks) == 472,"FIXED_TYPE_POPULATION")
    need(source_model.get("retained_coefficients_are_literal_originals") is True and
         source_model.get("original_row_labels_rhs_unchanged") is True,"FIXED_MODEL_PROVENANCE")
    need(gate["inputs_sha256"].get(PAIR_PARSED_INPUT) == PAIR_PARSED_INPUT_SHA,"PAIR_MODEL_CONTEXT_PIN")
    pair_context = reader.read(PAIR_PARSED_INPUT,PAIR_PARSED_INPUT_SHA)
    need(same(pair_context.get("ordered_masks"),masks) and
         same(pair_context.get("induced_adjacency"),source_model["induced_adjacency"]),"PAIR_MODEL_CONTEXT")
    rhs, labels = geometry(source_model["induced_adjacency"],99,14)
    need(same(source_model.get("row_labels"),labels),"FIXED_ROW_LABELS")
    moment_identity(dict(matrix=moments,rhs=source_model.get("right_hand_side")),moments,rhs)
    need(len(rhs) == 154 and rhs[0] == 82,"FIXED_MOMENT_POPULATION")
    pair_summary_path = config["pair_producer_summary_path"]
    key = safe(pair_summary_path).relative_to(ROOT).as_posix()
    need(key in gate["inputs_sha256"],"PAIR_PRODUCER_DIRECT_PIN")
    summary = reader.read(pair_summary_path,gate["inputs_sha256"][key])
    need(summary.get("status") == "CANDIDATE_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE", "PAIR_PRODUCER_HEADER")
    base = safe(pair_summary_path).parent
    outputs = summary["outputs_sha256"]
    expected = {"scaled_input.json"}|{kind+"_%03d.json"%i for i in range(23) for kind in ("part","checkpoint")}
    need(set(outputs) == expected and len(outputs) == 47,"PAIR_RAW_POPULATION")
    entries = list(base.iterdir())
    need(all(p.is_file() and not p.is_symlink() and not p.is_junction() for p in entries)
         and {p.name for p in entries} == expected|{"summary.json"},"PAIR_PHYSICAL_POPULATION")
    for name,digest in outputs.items():
        raw_key = (base/name).relative_to(ROOT).as_posix()
        need(gate["inputs_sha256"].get(raw_key) == digest,"PAIR_RAW_DIRECT_PIN")
        reader.read(str(base/name),digest,False)
    forbidden, equal_forbidden, rules, proposal = [], set(), [], 0
    labels_iter = iter(itertools.combinations_with_replacement(range(472),2))
    for index in range(23):
        tick(deadline)
        part = reader.read(str(base/("part_%03d.json"%index)),outputs["part_%03d.json"%index])
        start, stop = index*5000,min((index+1)*5000,111628)
        need(type(part) is dict and part.get("schema") == "DUAL_GRAM_PAIR_PART_V1" and
             same([part.get(k) for k in ("part_index","start","stop","count")],[index,start,stop,stop-start])
             and type(part.get("records")) is list and len(part["records"]) == stop-start,"PAIR_PART_BOUNDARY")
        for row in part["records"]:
            tick(deadline)
            i,j = next(labels_iter)
            if pair_record(row,proposal,i,j,masks):
                if i == j:equal_forbidden.add(i)
                else:forbidden.append((i,j))
                rules.append(dict(proposal_id=proposal,i=i,j=j,left_mask=masks[i],right_mask=masks[j],
                                  rule="multiplicity_at_most_one" if i == j else "presence_sum_at_most_one"))
            proposal += 1
        save(out/("pair_read_checkpoint_%03d.json"%index),dict(pair_records=proposal,total=111628,
             forbidden_distinct_pairs=len(forbidden),equal_forbidden_types=len(equal_forbidden)),deadline)
        print(json.dumps(dict(pair_records=proposal,total=111628)),flush=True)
    need(proposal == 111628 and next(labels_iter,None) is None,"PAIR_STREAM_POPULATION")
    triples = list(itertools.combinations(range(17),3))
    need(len(triples) == 680,"TRIPLE_POPULATION")
    model = integer_model(masks,moments,rhs,triples,forbidden,equal_forbidden)
    need(model["variables"] == 944 and len(model["rows"]) == 1778+len(forbidden),"INTEGER_MODEL_POPULATION")
    save(out/"parsed_fixed_input.json",dict(ordered_masks=masks,induced_adjacency=source_model["induced_adjacency"],
         moment_labels=labels,moments=moments,rhs=rhs,triples=[list(q) for q in triples]),deadline)
    save(out/"pair_rules.json",dict(complete_pair_records=proposal,rules=rules,all_record_labels_scanned=True,
         equal_types_mean_distinct_vertices=True,retained_count_types=472),deadline)
    save(out/"integer_model.json",model,deadline)
    seconds = solver_seconds(deadline,1500)
    save(out/"before_solver_checkpoint.json",dict(stage="full_model_saved",solver_time_limit=seconds,
         rows=len(model["rows"]),variables=944,deadline=deadline.status()),deadline)
    # Recheck after save/serialization, so its cost cannot extend the native slice.
    seconds = solver_seconds(deadline,1500)
    guidance = native(model,seconds,out,"scientific",deadline,180)
    save(out/"after_solver_checkpoint.json",dict(stage="native_returned",deadline=deadline.status(),
         model_status=guidance["model_status"],value_valid=guidance["solution_value_valid"]),deadline)
    extracted = extract(model,guidance,deadline)
    save(out/"extraction.json",extracted,deadline)
    if extracted["candidate"] is not None:
        save(out/"exact_integer_candidate.json",extracted["candidate"],deadline)
        save(out/"exact_constraint_rows.json",extracted["exact_rows"],deadline)
    return dict(exact_integer_candidate_produced=extracted["candidate"] is not None,count_types=472,presence_variables=472,
        original_moment_equalities=154,triple_caps=680,complete_pair_records=111628,
        forbidden_distinct_pair_rules=len(forbidden),equal_forbidden_multiplicity_bounds=len(equal_forbidden),
        all_type_variables_retained=True,high_cardinality_types_binary=True,scientific_solver_calls=1,
        floating_status_is_proof=False,numeric_infeasibility_is_proof=False,graph_completion=False,
        certificate_unavailable_reason=extracted.get("reason"),solver_time_limit=guidance["options"]["time_limit"])


def output_hashes(out,deadline):
    result = {}
    for path in sorted(out.iterdir()):
        tick(deadline)
        need(path.is_file() and not path.is_symlink() and path.suffix != ".tmp","OUTPUT_POPULATION")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                tick(deadline)
                block = handle.read(1024*1024)
                if not block:break
                digest.update(block)
        result[path.name] = digest.hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",choices=("calibrate","solve"))
    parser.add_argument("--seconds",required=True,type=float)
    parser.add_argument("--out",required=True)
    parser.add_argument("--self-sha256",required=True)
    parser.add_argument("--spec-sha256",required=True)
    parser.add_argument("--executor",required=True,choices=("/root","/root/checkpoint_audit"))
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason="One complete fixed17 count-IP or finite author controls; all authentication, backend, exact extraction and saves share this deadline")
    out = safe(args.out)
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(),"OUTPUT_FRESH_SCOPE")
    out.mkdir(parents=True)
    reader = Reader(deadline)
    software = {**SOFTWARE,SELF.relative_to(ROOT).as_posix():args.self_sha256,SPEC.relative_to(ROOT).as_posix():args.spec_sha256}
    try:
        reader.map(software)
        if args.mode == "calibrate":
            outcome = controls(out,deadline)
            status = CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None,"CONFIG_ARGUMENTS")
            config = reader.read(args.configuration,args.configuration_sha256)
            outcome = scientific(reader,config,out)
            status = "CANDIDATE_FIXED17_INTEGER_TYPE_COUNTS_V1" if outcome["exact_integer_candidate_produced"] else "NO_EXACT_INTEGER_COUNT_WITNESS_V1"
        reader.closing()
        outputs = output_hashes(out,deadline)
        report = dict(schema="FIXED17_INTEGER_TYPE_COUNT_PRODUCER_REPORT_V1",status=status,implementation_version=1,
            timestamp=datetime.now(timezone.utc).isoformat(),producer="/root/checkpoint_audit",source_author="/root/checkpoint_audit",
            executor_declaration=args.executor,executor_identity_requires_external_runtime_receipt=True,
            independent_verifier=None,independent_verifier_null_reason="Separate qualified raw model/count checker required before feasibility approval",
            method="integer_model_search_and_exact_candidate_extraction" if args.mode == "solve" else "finite_author_controls",
            mode=args.mode,outcome=outcome,source_software=software,inputs_sha256=dict(reader.pins),outputs_sha256=outputs,
            command=sys.argv,cwd=str(ROOT),python=platform.python_version(),deadline=deadline.status(),
            actual_target_input_read=args.mode == "solve",automatic_retry=False,LP_search_calls=0,
            old_primal_positive_support_filter_used=False,independent_approval=False,target_resolution="NONE",
            ledger_index_git_mutations=0,complete_ancestor_evidence_closure_rehashed=False,
            scope="Necessary count relaxation for this exact fixed induced17 and all ordered472 types; integer feasibility is not exterior graph or target existence",
            shared_components=["Pinned Python/json/SHA/command_deadline, locked highspy/numpy numerical runtime and old exact target/model/type premises",
                "Count model and exact integer extraction newly authored; pair inequalities inherit only genuine Native implementation2 complete pair evidence",
                "Root proposed this experiment; executor declaration is separate from source authorship and must be corroborated by the external receipt"],
            limitations=["All numeric statuses, bounds, gaps, infeasible and timeout outcomes are guidance only and prove no exclusion",
                "Independent exact raw model/vector verification is required; no optimizer, graph, full exterior PSD/rank or optimality assertion",
                "Only zero-objective single scientific run; no auto retry/lazy cut chain, historical LP or rational support restriction",
                "Checkpoint/log durability is guarded intent; a hard kill may lose a pending suffix and is not guaranteed to preserve native internal state"])
        save(out/"summary.json",report,deadline)
        reader.closing()
        tick(deadline)
        print(json.dumps(dict(status=status,outcome=outcome,output_files=len(outputs)+1)),flush=True)
    except Exception as exc:
        failure = dict(status="FAILED",stage=str(exc),exception=type(exc).__name__,timestamp=datetime.now(timezone.utc).isoformat(),
                       target_resolution="NONE",infeasibility_inferred=False,automatic_retry=False,deadline=deadline.status())
        # Best effort within the same invocation; no renewed allowance or success after closing veto.
        try:
            (out/"failure.json").write_text(json.dumps(failure,indent=2,allow_nan=False)+"\n",encoding="utf8")
        except Exception:pass
        raise


if __name__ == "__main__":
    main()
