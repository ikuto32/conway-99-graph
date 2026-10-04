"""Independent exact certificate arithmetic; no LP, RREF or producer imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import re
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
PRODUCER = "acceleration/solve_20261003_external_moment_filtered_lp_v2.py"
PRODUCER_SPEC = "acceleration/solve_20261003_external_moment_filtered_lp_v2_spec.md"
PINS = {
    PRODUCER: "c3bf96ea6466c6ccc8c135c40657d408996990016362dcd6aecc6e6f695610f6",
    PRODUCER_SPEC: "2f637623651e69dbcfd144daf7bd6045ec229c3899dcedda997fc3dee8a00f40",
    "acceleration/audit_20261003_external_moment_outside_cn_v1.py": "14d17af3d661c12ffded3988e84f112a68d4535d15d8c5c10ea5bc68f13aeaec",
    "acceleration/audit_20261003_external_moment_outside_cn_v1_spec.md": "1115238db9d0402d088e64ad115d73eb89b881cfbfc25c9c71240ec49aa9ebb8",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
BASE = "acceleration/results/20261003_external_moment_outside_cn_filter01"
MODEL = BASE + "/filtered_system.json"
TYPES = BASE + "/types.json"
FIXED = {
    MODEL: "c628c76325d5b49106740bce7c6d3b72bc7728fdc78d85437ad484f3afbd7306",
    TYPES: "87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2",
    BASE + "/summary.json": "89f8976ba3a18b52394417e58c9a0ce991cf1b4f4d41f14570079f8342ce3591",
    BASE + "/decisions.json": "1a48f95f646d0cea4191c43ac9b8e03a7fb0bbea05dc9bbccca68ef774ba0dc2",
}
FILTER_STATUS = "INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS"
CAL_STATUS = "INDEPENDENT_FILTERED_EXTERNAL_MOMENT_CERTIFICATE_V1_CALIBRATION_PASS"
FULL_STATUS = "INDEPENDENT_FILTERED_EXTERNAL_MOMENT_CERTIFICATE_V1_COMPLETE_PASS"
PAIRS = list(itertools.combinations(range(17), 2))
AUTHOR_STAGES = [
    ("verification_method_only_header", "FILTER_GATE_SCOPE"),
    ("inconsistent", "INCONSISTENT_SUPPORT"), ("negative_rref", "NEGATIVE_SOLUTION"),
    ("bool_coefficient", "SYSTEM_INTEGER"), ("float_rhs", "SYSTEM_INTEGER"),
    ("noncanonical_fraction", "FRACTION_CANONICAL"), ("float_fraction", "FRACTION_STRING"),
    ("negative_primal", "PRIMAL_NONNEGATIVE"), ("wrong_primal_row", "PRIMAL_MOMENTS"),
    ("wrong_farkas_rhs", "FARKAS_RHS_SIGN"), ("wrong_farkas_column", "FARKAS_COLUMN_SIGN"),
    ("bool_mask", "TYPE_MASK_INTEGER"), ("decreasing_masks", "TYPE_MASK_ORDER"),
]


def require(condition, stage):
    if not condition:
        raise ValueError(stage)


def equal(left, right):
    """Recursive equality with exact Python types; bool is never an integer."""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(equal(a, b) for a, b in zip(left, right))
    return left == right


def fields(value, names, stage):
    require(type(value) is dict and set(value) == set(names), stage)


def parsed(raw):
    require(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, "JSON_SIZE")
    def pairs(items):
        answer = {}
        for name, value in items:
            require(name not in answer, "JSON_DUPLICATE")
            answer[name] = value
        return answer
    def nonfinite(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


def rational(raw):
    require(type(raw) is str, "RATIONAL_TYPE")
    require(re.fullmatch(r"-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?", raw) is not None,
            "RATIONAL_CANONICAL")
    try:
        answer = Fraction(raw)
    except (ValueError, ZeroDivisionError):
        raise ValueError("RATIONAL_CANONICAL") from None
    require(str(answer) == raw, "RATIONAL_CANONICAL")
    return answer


def vector(raw, length):
    require(type(raw) is list and len(raw) == length, "VECTOR_LENGTH")
    return [rational(item) for item in raw]


def integer_system(matrix, rhs):
    require(type(matrix) is list and matrix and type(matrix[0]) is list and matrix[0],
            "SYSTEM_SHAPE")
    width = len(matrix[0])
    require(all(type(row) is list and len(row) == width for row in matrix)
            and type(rhs) is list and len(rhs) == len(matrix), "SYSTEM_SHAPE")
    require(all(type(v) is int for row in matrix for v in row)
            and all(type(v) is int for v in rhs), "SYSTEM_INTEGER")


def certificate(kind, raw, matrix, rhs, guard=lambda: None):
    integer_system(matrix, rhs)
    if kind == "primal":
        fields(raw, ["schema", "values", "nonnegative", "rows_exact", "integer"], "PRIMAL_FIELDS")
        require(raw["schema"] == "FILTERED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1"
                and raw["nonnegative"] is True and raw["rows_exact"] is True
                and type(raw["integer"]) is bool, "PRIMAL_HEADER")
        x = vector(raw["values"], len(matrix[0]))
        require(all(v >= 0 for v in x), "PRIMAL_NONNEGATIVE")
        require(raw["integer"] is all(v.denominator == 1 for v in x), "PRIMAL_INTEGER_FLAG")
        receipts = []
        for index, (row, b) in enumerate(zip(matrix, rhs)):
            guard()
            lhs = sum((x[j] * row[j] for j in range(len(x))), Fraction(0))
            require(lhs == b, "PRIMAL_EQUATION")
            receipts.append(dict(row=index, lhs=str(lhs), rhs=str(b), equal=True))
        return dict(values=len(x), rows=len(receipts), nonnegative=True,
                    integer=raw["integer"], receipts=receipts)
    require(kind == "farkas", "CERTIFICATE_KIND")
    fields(raw, ["schema", "values", "rhs_dot", "all_column_inequalities_exact",
                 "candidate_rationalization_max_denominator"], "FARKAS_FIELDS")
    require(raw["schema"] == "FILTERED_EXTERNAL_MOMENT_EXACT_FARKAS_V1"
            and raw["all_column_inequalities_exact"] is True
            and type(raw["candidate_rationalization_max_denominator"]) is int
            and raw["candidate_rationalization_max_denominator"] == 1_000_000_000, "FARKAS_HEADER")
    y = vector(raw["values"], len(matrix))
    dot = sum((y[i] * rhs[i] for i in range(len(y))), Fraction(0))
    require(dot < 0, "FARKAS_RHS_NEGATIVE")
    require(rational(raw["rhs_dot"]) == dot, "FARKAS_RHS_RECEIPT")
    columns = []
    for j in range(len(matrix[0])):
        guard()
        value = sum((matrix[i][j] * y[i] for i in range(len(y))), Fraction(0))
        require(value >= 0, "FARKAS_COLUMN_NONNEGATIVE")
        columns.append(dict(column=j, dot=str(value), nonnegative=True))
    return dict(values=len(y), columns=len(columns), rhs_dot=str(dot),
                receipts=dict(rhs_dot=str(dot), negative=True, columns=columns))


def primal(values):
    return dict(schema="FILTERED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1", values=values,
                nonnegative=True, rows_exact=True, integer=all(rational(v).denominator == 1 for v in values))


def dual(values, dot):
    return dict(schema="FILTERED_EXTERNAL_MOMENT_EXACT_FARKAS_V1", values=values,
                rhs_dot=dot, all_column_inequalities_exact=True,
                candidate_rationalization_max_denominator=1_000_000_000)


def labels():
    return ([dict(kind="total")] + [dict(kind="vertex", vertex=i) for i in range(17)]
            + [dict(kind="pair", vertices=[i, j]) for i, j in PAIRS])


def model_system(model, types, guard=lambda: None):
    require(type(model) is dict and model.get("schema") == "OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1",
            "MODEL_SCHEMA")
    for key, value in [("target_order", 99), ("target_degree", 14), ("adjacent_cn", 1),
                       ("nonadjacent_cn", 2), ("original_eligible_type_count", 534), ("eligible_type_count", 472)]:
        require(type(model.get(key)) is int and model[key] == value, "MODEL_DOMAIN")
    require(equal(model.get("ordered_support_vertices"), list(range(17))), "MODEL_ORDER")
    h = model.get("induced_adjacency")
    require(type(h) is list and len(h) == 17 and all(type(row) is list and len(row) == 17 for row in h),
            "MODEL_GRAPH_SHAPE")
    require(all(type(v) is int and v in (0, 1) for row in h for v in row)
            and all(h[i][i] == 0 and h[i][j] == h[j][i] for i in range(17) for j in range(17)),
            "MODEL_GRAPH_DOMAIN")
    require(equal(model.get("row_labels"), labels()), "MODEL_LABELS")
    b = model.get("right_hand_side")
    require(type(b) is list and len(b) == 154 and all(type(v) is int for v in b), "MODEL_RHS_TYPE")
    # Outside cardinality, missing point degrees and residual pair CN are independently rebuilt.
    expected = [82] + [14 - sum(row) for row in h]
    for i, j in PAIRS:
        guard()
        cn = sum(h[i][k] * h[j][k] for k in range(17))
        expected.append((1 if h[i][j] else 2) - cn)
    require(equal(b, expected), "MODEL_RHS_GEOMETRY")
    require(model.get("retained_coefficients_are_literal_originals") is True
            and model.get("original_row_labels_rhs_unchanged") is True, "MODEL_PROVENANCE")
    indices = model.get("retained_original_type_indices")
    require(type(indices) is list and len(indices) == 472
            and all(type(v) is int and 0 <= v < 534 for v in indices)
            and indices == sorted(set(indices)), "MODEL_INDICES")
    require(type(types) is list and len(types) == 472, "TYPES_COUNT")
    columns, masks, previous = [], [], -1
    for item in types:
        guard()
        fields(item, ["mask", "coefficient"], "TYPE_FIELDS")
        mask = item["mask"]
        require(type(mask) is int and 0 <= mask < (1 << 17), "TYPE_MASK_INTEGER")
        require(mask > previous, "TYPE_MASK_ORDER")
        previous = mask
        bits = [(mask >> i) & 1 for i in range(17)]
        col = [1] + bits + [bits[i] * bits[j] for i, j in PAIRS]
        require(equal(item["coefficient"], col), "TYPE_COEFFICIENT")
        masks.append(mask)
        columns.append(col)
    a = [[col[i] for col in columns] for i in range(154)]
    integer_system(a, b)
    return a, b, masks


def filter_header(gate):
    require(type(gate) is dict and gate.get("status") == FILTER_STATUS
            and gate.get("producer") == "/root/checkpoint_audit"
            and gate.get("verifier") == "/root/native_driver"
            and gate.get("method") == "independent_artifact_check"
            and gate.get("target_resolution") == "NONE"
            and type(gate.get("implementation_version")) is int and gate["implementation_version"] == 1,
            "FILTER_HEADER")
    closure = gate.get("inputs_sha256")
    require(type(closure) is dict and closure, "FILTER_CLOSURE")
    native = {k: v for k, v in PINS.items() if "outside_cn_v1" in k}
    require(all(closure.get(k) == v for k, v in {**FIXED, **native}.items()), "FILTER_DIRECT_PINS")
    return closure


def path_words(words):
    require(type(words) is list and words and all(type(v) is str for v in words), "COMMAND_TYPES")
    return [v.replace("\\", "/") for v in words]


def runtime(manifest, terminal, expected_child, worker_summary, seconds):
    require(type(manifest) is dict and type(terminal) is dict, "RUNTIME_OBJECT")
    require(manifest.get("source_sha256") == PINS["acceleration/run_compute_command.py"]
            and type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1
            and manifest.get("process_scope") == "Local non-escaping process tree only; remote/daemonized compute is unsupported",
            "RUNTIME_SOURCE_SCOPE")
    require(type(manifest.get("invocation_id")) is str and re.fullmatch(r"[0-9a-f]{32}", manifest["invocation_id"])
            and terminal.get("invocation_id") == manifest["invocation_id"], "RUNTIME_INVOCATION")
    require(path_words(manifest.get("command")) == path_words(expected_child)
            and Path(manifest.get("cwd", "")).resolve() == ROOT, "RUNTIME_COMMAND")
    require(type(manifest.get("seconds")) in (int, float) and math.isfinite(manifest["seconds"])
            and manifest["seconds"] == seconds and manifest.get("automatic_retry") is False
            and manifest.get("cumulative_across_commands") is False, "RUNTIME_ALLOCATION")
    cleanup = terminal.get("cleanup")
    require(type(cleanup) is dict and cleanup.get("created_suspended") is True
            and cleanup.get("resumed") is True and cleanup.get("reaped") is True
            and cleanup.get("job_active_zero_observed") is True
            and equal(cleanup.get("cleanup_errors"), []), "RUNTIME_CLEANUP")
    require(type(terminal.get("command_exit_code")) is int and terminal["command_exit_code"] == 0
            and type(cleanup.get("actual_exit_code")) is int and cleanup["actual_exit_code"] == 0
            and terminal.get("stop_reason") == "COMMAND_EXITED"
            and terminal.get("status") == "COMMAND_COMPLETED_VERIFICATION_PENDING"
            and terminal.get("deadline_reached") is False and terminal.get("error") is None, "RUNTIME_EXIT")
    require(type(terminal.get("elapsed_seconds")) in (int, float)
            and math.isfinite(terminal["elapsed_seconds"]) and 0 <= terminal["elapsed_seconds"] <= seconds,
            "RUNTIME_ELAPSED")
    # Producer records sys.argv without interpreter -B. Compare the original worker suffix exactly.
    child = path_words(expected_child)
    location = child.index(str((ROOT / PRODUCER).as_posix())) if str((ROOT / PRODUCER).as_posix()) in child else child.index(PRODUCER)
    reported = path_words(worker_summary.get("command"))
    require(reported[1:] == child[location:]
            and Path(reported[0]).resolve() == (ROOT / "build/research-venv/Scripts/python.exe").resolve(), "WORKER_COMMAND")
    require(Path(worker_summary.get("cwd", "")).resolve() == ROOT
            and worker_summary.get("python") == "3.12.10", "WORKER_ENVIRONMENT")
    return dict(invocation_id=manifest["invocation_id"], elapsed_seconds=terminal["elapsed_seconds"],
                observed_scope="LOCAL_WINDOWS_SUSPENDED_JOB_V1", reaped=True, empty_job=True)


def attempt_header(attempt):
    fields(attempt, ["LP_calls", "certificate_kind", "certificate", "certificate_unavailable_reason"], "ATTEMPT_FIELDS")
    require(type(attempt["LP_calls"]) is int and attempt["LP_calls"] in (1, 2), "ATTEMPT_CALLS")
    require(attempt["certificate_kind"] in ("primal", "farkas") and attempt["certificate_unavailable_reason"] is None,
            "EXACT_CERTIFICATE_REQUIRED")
    require(attempt["LP_calls"] == (1 if attempt["certificate_kind"] == "primal" else 2), "ATTEMPT_BRANCH")


def author_inventory(kind, rank=0):
    common = {"control_genuine_method_header.json", "control_unique_rational.json", "controls.json"}
    common |= {"control_negative_" + name + ".json" for name, _ in AUTHOR_STAGES}
    common |= {"control_lp_primal_" + suffix + ".json" for suffix in
               ["primal_guidance", "support", "rref", "primal_rows", "primal"]}
    common |= {"control_lp_dual_" + suffix + ".json" for suffix in
               ["primal_guidance", "dual_guidance", "farkas_checks", "farkas"]}
    require(len(common) == 25, "AUTHOR_INVENTORY_INTERNAL")
    if kind is not None:
        common |= {"model_receipt.json", "attempt.json", "filtered_primal_guidance.json"}
        if kind == "primal":
            common |= {"filtered_" + suffix + ".json" for suffix in ["support", "rref", "primal_rows", "primal"]}
            common |= {"checkpoints/pivot_%03d.json" % k for k in range(10, rank + 1, 10)}
        else:
            common |= {"filtered_" + suffix + ".json" for suffix in ["dual_guidance", "farkas_checks", "farkas"]}
    return common


def inventory(declared, physical, kind, rank=0):
    require(type(declared) is list and type(physical) is list
            and all(type(v) is str for v in declared + physical)
            and len(declared) == len(set(declared)) and len(physical) == len(set(physical)), "OUTPUT_POPULATION")
    required = author_inventory(kind, rank)
    require(set(declared) == required and set(physical) == required | {"summary.json"}, "OUTPUT_POPULATION")
    return dict(declared=len(declared), physical=len(physical))


def exact_receipt(observed, expected):
    require(equal(observed, expected), "EXACT_RECEIPT")
    return dict(typed_equal=True)


def synthetic_model():
    h = [[0] * 17 for _ in range(17)]
    model = dict(schema="OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1", target_order=99, target_degree=14,
                 adjacent_cn=1, nonadjacent_cn=2, original_eligible_type_count=534, eligible_type_count=472,
                 ordered_support_vertices=list(range(17)), induced_adjacency=h, row_labels=labels(),
                 right_hand_side=[82] + [14] * 17 + [2] * 136,
                 retained_coefficients_are_literal_originals=True, original_row_labels_rhs_unchanged=True,
                 retained_original_type_indices=list(range(472)))
    types = []
    for mask in range(472):
        bits = [(mask >> i) & 1 for i in range(17)]
        types.append(dict(mask=mask, coefficient=[1] + bits + [bits[i] * bits[j] for i, j in PAIRS]))
    return model, types


def own_controls(guard, save):
    records = []
    def positive(name, payload, action):
        guard()
        observed = action()
        save("controls/positive_" + name + ".json", dict(payload=payload, observation=observed))
        records.append(dict(case=name, expected_stage="PASS", actual_stage="PASS"))
    def negative(name, stage, payload, action):
        guard()
        save("controls/negative_" + name + ".json", payload)
        actual = "ACCEPTED"
        try:
            action()
        except ValueError as exc:
            actual = str(exc)
        require(actual == stage, "CONTROL_STAGE_" + name)
        records.append(dict(case=name, expected_stage=stage, actual_stage=actual))
    a, b = [[1, 2], [2, 1]], [1, 1]
    p = primal(["1/3", "1/3"])
    positive("hand_rational", p, lambda: certificate("primal", p, a, b, guard))
    z = primal(["1", "0"])
    positive("zero_coordinate", z, lambda: certificate("primal", z, [[1, 1], [0, 1]], [1, 0], guard))
    d = dual(["1"], "-1")
    positive("hand_farkas", d, lambda: certificate("farkas", d, [[1]], [-1], guard))
    d2 = dual(["1", "1"], "-1")
    positive("zero_dual_column", d2, lambda: certificate("farkas", d2, [[1], [-1]], [1, -2], guard))
    big_a = [[0] * 472 for _ in range(154)]
    big_a[153][471] = 1
    big_b = [0] * 153 + [1]
    big_p = primal(["0"] * 471 + ["1"])
    positive("all154_rows_472_primal", big_p, lambda: certificate("primal", big_p, big_a, big_b, guard))
    big_da = [[0] * 472 for _ in range(154)]
    big_db = [-1] + [0] * 153
    big_d = dual(["1"] + ["0"] * 153, "-1")
    positive("all472_dual_columns", big_d, lambda: certificate("farkas", big_d, big_da, big_db, guard))
    model, types = synthetic_model()
    positive("synthetic_model_geometry", model, lambda: dict(rows=len(model_system(model, types, guard)[0]), columns=472))
    gate = dict(status=FILTER_STATUS, producer="/root/checkpoint_audit", verifier="/root/native_driver",
                method="independent_artifact_check", target_resolution="NONE", implementation_version=1,
                inputs_sha256={**FIXED, **{k: v for k, v in PINS.items() if "outside_cn_v1" in k}})
    positive("synthetic_native_header", gate, lambda: dict(direct_pins=len(filter_header(gate))))
    child = [str(ROOT / "build/research-venv/Scripts/python.exe"), "-B", PRODUCER, "solve"]
    worker = dict(command=[child[0], PRODUCER, "solve"], cwd=str(ROOT), python="3.12.10")
    manifest = dict(schema_version=1, source_sha256=PINS["acceleration/run_compute_command.py"],
                    process_scope="Local non-escaping process tree only; remote/daemonized compute is unsupported",
                    invocation_id="1" * 32, command=child, cwd=str(ROOT), seconds=300.0,
                    automatic_retry=False, cumulative_across_commands=False)
    terminal = dict(invocation_id="1" * 32, cleanup=dict(created_suspended=True, resumed=True, reaped=True,
                    job_active_zero_observed=True, cleanup_errors=[], actual_exit_code=0), command_exit_code=0,
                    stop_reason="COMMAND_EXITED", status="COMMAND_COMPLETED_VERIFICATION_PENDING", deadline_reached=False,
                    error=None, elapsed_seconds=1.0)
    positive("synthetic_windows_runtime", dict(manifest=manifest, terminal=terminal, worker=worker),
             lambda: runtime(manifest, terminal, child, worker, 300))
    no_scope = copy.deepcopy(manifest)
    require("runtime_scope" not in no_scope, "CONTROL_593_NO_SCOPE_FIELD")
    positive("genuine_shaped_593_without_runtime_scope", dict(manifest=no_scope, terminal=terminal, worker=worker),
             lambda: runtime(no_scope, terminal, child, worker, 300))
    positive("strict_json", {"a": 0, "b": True}, lambda: parsed(b'{"a":0,"b":true}'))
    primal_files = sorted(author_inventory("primal", 20))
    dual_files = sorted(author_inventory("farkas"))
    positive("primal_branch_population", dict(files=primal_files),
             lambda: inventory(primal_files, primal_files + ["summary.json"], "primal", 20))
    positive("dual_branch_population", dict(files=dual_files),
             lambda: inventory(dual_files, dual_files + ["summary.json"], "farkas"))
    # Payload, function and stage are saved together; no producer implementation is executed.
    for name, value, stage in [("bool_fraction", True, "RATIONAL_TYPE"), ("float_fraction", 1.0, "RATIONAL_TYPE"),
        ("integer_fraction", 1, "RATIONAL_TYPE"), ("noncanonical", "2/2", "RATIONAL_CANONICAL"),
        ("negative_zero", "-0", "RATIONAL_CANONICAL"), ("leading_zero", "01", "RATIONAL_CANONICAL"),
        ("space", " 1", "RATIONAL_CANONICAL"), ("zero_denominator", "1/0", "RATIONAL_CANONICAL")]:
        negative(name, stage, dict(value=value), lambda v=value: rational(v))
    negative("vector_missing", "VECTOR_LENGTH", dict(values=["1"]), lambda: vector(["1"], 2))
    negative("bool_matrix", "SYSTEM_INTEGER", dict(a=[[True]], rhs=[1]), lambda: integer_system([[True]], [1]))
    negative("float_rhs", "SYSTEM_INTEGER", dict(a=[[1]], rhs=[1.0]), lambda: integer_system([[1]], [1.0]))
    negative("ragged", "SYSTEM_SHAPE", dict(a=[[1], []], rhs=[1, 0]), lambda: integer_system([[1], []], [1, 0]))
    for name, key, value, stage in [("primal_bool_flag", "integer", 0, "PRIMAL_HEADER"),
        ("primal_false_flag", "nonnegative", False, "PRIMAL_HEADER"),
        ("primal_integer_lie", "integer", True, "PRIMAL_INTEGER_FLAG"),
        ("negative_primal", "values", ["-1", "1"], "PRIMAL_NONNEGATIVE"),
        ("wrong_primal", "values", ["1/3", "2/3"], "PRIMAL_EQUATION")]:
        bad = copy.deepcopy(p); bad[key] = value
        negative(name, stage, bad, lambda v=bad: certificate("primal", v, a, b, guard))
    bad = copy.deepcopy(big_p); bad["values"][471] = "0"
    negative("last_row154", "PRIMAL_EQUATION", bad, lambda: certificate("primal", bad, big_a, big_b, guard))
    bad = primal(["0"] * 471 + ["-1"])
    negative("last_coordinate472", "PRIMAL_NONNEGATIVE", bad, lambda: certificate("primal", bad, big_a, big_b, guard))
    for name, key, value, stage in [("farkas_zero_rhs", "values", ["0"], "FARKAS_RHS_NEGATIVE"),
        ("farkas_wrong_receipt", "rhs_dot", "-2", "FARKAS_RHS_RECEIPT"),
        ("farkas_bool_denominator", "candidate_rationalization_max_denominator", True, "FARKAS_HEADER"),
        ("farkas_false_flag", "all_column_inequalities_exact", 1, "FARKAS_HEADER")]:
        bad = copy.deepcopy(d); bad[key] = value
        negative(name, stage, bad, lambda v=bad: certificate("farkas", v, [[1]], [-1], guard))
    late = copy.deepcopy(big_da); late[0][471] = -1
    negative("last_dual_column472", "FARKAS_COLUMN_NONNEGATIVE", dict(a=late, y=big_d),
             lambda: certificate("farkas", big_d, late, big_db, guard))
    for name, key, value, stage in [("model_bool_order", "target_order", True, "MODEL_DOMAIN"),
        ("model_bool_vertices", "ordered_support_vertices", [False] + list(range(1, 17)), "MODEL_ORDER"),
        ("model_wrong_labels", "row_labels", list(reversed(labels())), "MODEL_LABELS"),
        ("model_bool_rhs", "right_hand_side", [True] + model["right_hand_side"][1:], "MODEL_RHS_TYPE"),
        ("model_wrong_rhs", "right_hand_side", [81] + model["right_hand_side"][1:], "MODEL_RHS_GEOMETRY"),
        ("model_bool_provenance", "original_row_labels_rhs_unchanged", 1, "MODEL_PROVENANCE"),
        ("model_bool_index", "retained_original_type_indices", [False] + list(range(1, 472)), "MODEL_INDICES")]:
        bad = copy.deepcopy(model); bad[key] = value
        negative(name, stage, bad, lambda v=bad: model_system(v, types, guard))
    for name, value, stage in [("type_bool_mask", True, "TYPE_MASK_INTEGER"),
                              ("type_float_mask", 0.0, "TYPE_MASK_INTEGER"), ("type_order", 1, "TYPE_MASK_ORDER")]:
        bad = copy.deepcopy(types)
        if name == "type_order":
            bad[1]["mask"] = 0
        else:
            bad[0]["mask"] = value
        negative(name, stage, bad, lambda v=bad: model_system(model, v, guard))
    bad = copy.deepcopy(types); bad[-1]["coefficient"][-1] = True
    negative("type_bool_last_coefficient", "TYPE_COEFFICIENT", bad, lambda: model_system(model, bad, guard))
    for name, key, value, stage in [("filter_wrong_method", "method", None, "FILTER_HEADER"),
        ("filter_wrong_role", "verifier", "/root/structural", "FILTER_HEADER"),
        ("filter_missing_pin", "inputs_sha256", {}, "FILTER_CLOSURE")]:
        bad = copy.deepcopy(gate); bad[key] = value
        negative(name, stage, bad, lambda v=bad: filter_header(v))
    bad = copy.deepcopy(gate); bad["inputs_sha256"][MODEL] = "0" * 64
    negative("filter_changed_pin", "FILTER_DIRECT_PINS", bad, lambda: filter_header(bad))
    for name, key, value, stage in [("runtime_bool_exit", "command_exit_code", False, "RUNTIME_EXIT"),
        ("runtime_deadline", "deadline_reached", True, "RUNTIME_EXIT"),
        ("runtime_wrong_invocation", "invocation_id", "2" * 32, "RUNTIME_INVOCATION"),
        ("runtime_elapsed_bool", "elapsed_seconds", True, "RUNTIME_ELAPSED")]:
        bad = copy.deepcopy(terminal); bad[key] = value
        negative(name, stage, bad, lambda v=bad: runtime(manifest, v, child, worker, 300))
    for name, key, value in [("runtime_unreaped", "reaped", False), ("runtime_job_bool_alias", "job_active_zero_observed", 1),
                             ("runtime_cleanup_errors", "cleanup_errors", ["error"])]:
        bad = copy.deepcopy(terminal); bad["cleanup"][key] = value
        negative(name, "RUNTIME_CLEANUP", bad, lambda v=bad: runtime(manifest, v, child, worker, 300))
    for name, key, value, stage in [("runtime_wrong_scope", "process_scope", "unsupported remote tree", "RUNTIME_SOURCE_SCOPE"),
        ("runtime_changed_command", "command", child + ["--retry"], "RUNTIME_COMMAND"),
        ("runtime_bool_seconds", "seconds", True, "RUNTIME_ALLOCATION")]:
        bad = copy.deepcopy(manifest); bad[key] = value
        negative(name, stage, bad, lambda v=bad: runtime(v, terminal, child, worker, 300))
    bad_source = copy.deepcopy(manifest); bad_source["source_sha256"] = "0" * 64
    negative("runtime_altered_593_source", "RUNTIME_SOURCE_SCOPE", bad_source,
             lambda: runtime(bad_source, terminal, child, worker, 300))
    bad_schema = copy.deepcopy(manifest); bad_schema["schema_version"] = True
    negative("runtime_boolean_schema_version", "RUNTIME_SOURCE_SCOPE", bad_schema,
             lambda: runtime(bad_schema, terminal, child, worker, 300))
    bad = copy.deepcopy(worker); bad["command"] = [child[0], PRODUCER, "calibrate"]
    negative("worker_wrong_mode", "WORKER_COMMAND", bad, lambda: runtime(manifest, terminal, child, bad, 300))
    bad = copy.deepcopy(worker); bad["python"] = 3.12
    negative("worker_version_type", "WORKER_ENVIRONMENT", bad, lambda: runtime(manifest, terminal, child, bad, 300))
    negative("duplicate_json", "JSON_DUPLICATE", dict(raw='{"a":0,"a":1}'), lambda: parsed(b'{"a":0,"a":1}'))
    negative("nonfinite_json", "JSON_NONFINITE", dict(raw='{"a":NaN}'), lambda: parsed(b'{"a":NaN}'))
    att = dict(LP_calls=1, certificate_kind="primal", certificate=p, certificate_unavailable_reason=None)
    for name, key, value, stage in [("attempt_bool_calls", "LP_calls", True, "ATTEMPT_CALLS"),
        ("attempt_guidance_only", "certificate_kind", None, "EXACT_CERTIFICATE_REQUIRED"),
        ("attempt_wrong_branch", "LP_calls", 2, "ATTEMPT_BRANCH")]:
        bad = copy.deepcopy(att); bad[key] = value
        negative(name, stage, bad, lambda v=bad: attempt_header(v))
    for name, declared, physical in [
        ("population_missing", primal_files[:-1], primal_files + ["summary.json"]),
        ("population_extra", primal_files, primal_files + ["summary.json", "failure.json"]),
        ("population_duplicate", primal_files + [primal_files[0]], primal_files + ["summary.json"]),
        ("population_summary_map", primal_files + ["summary.json"], primal_files + ["summary.json"]),
        ("population_checkpoint", primal_files, primal_files + ["summary.json", "checkpoints/pivot_030.json"]),
    ]:
        negative(name, "OUTPUT_POPULATION", dict(declared=declared, physical=physical),
                 lambda x=declared, y=physical: inventory(x, y, "primal", 20))
    receipt = [dict(row=0, lhs="1", rhs="1", equal=True)]
    bad_receipt = [dict(row=False, lhs="1", rhs="1", equal=True)]
    negative("receipt_bool_index", "EXACT_RECEIPT", bad_receipt, lambda: exact_receipt(bad_receipt, receipt))
    bad_receipt2 = [dict(row=0, lhs="1", rhs="1", equal=1)]
    negative("receipt_bool_flag", "EXACT_RECEIPT", bad_receipt2, lambda: exact_receipt(bad_receipt2, receipt))
    result = dict(positive=sum(r["actual_stage"] == "PASS" for r in records),
                  strict_negative=sum(r["actual_stage"] != "PASS" for r in records), records=records,
                  target_model_read=False, genuine_runtime_read=False, producer_outputs_checked=False,
                  LP_calls=0, RREF_calls=0, graph_completion_checks=0)
    require(result["positive"] == 13 and result["strict_negative"] == 65, "CONTROL_POPULATION")
    save("controls.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["calibrate", "full"])
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    for name in ["calibration", "producer-summary", "producer-plan", "runtime-manifest", "runtime-summary", "filter-gate"]:
        parser.add_argument("--" + name)
        parser.add_argument("--" + name + "-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Independent exact rational certificate, framing, hashes and preservation within one invocation")
    def guard():
        state = deadline.status()
        require(not state["stop_required"] and state["remaining_seconds"] > 20, "SAVE_RESERVE")
        return state
    out = Path(args.out).resolve()
    require(not out.exists(), "OUTPUT_FRESH")
    out.mkdir(parents=True)
    inputs, outputs = {}, {}
    def key(path):
        return Path(path).resolve().relative_to(ROOT).as_posix()
    def digest(path):
        guard()
        value = hashlib.sha256()
        with Path(path).open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                guard(); value.update(chunk)
        guard()
        return value.hexdigest()
    def pin(path, expected):
        require(type(expected) is str and re.fullmatch(r"[0-9a-f]{64}", expected), "HASH_FORMAT")
        path = Path(path).resolve()
        name = key(path)
        require(path.is_file() and not path.is_symlink(), "PIN_FILE")
        actual = digest(path)
        require(actual == expected and (name not in inputs or inputs[name] == expected), "INPUT_IDENTITY")
        inputs[name] = actual
        return path
    def read(path):
        guard(); value = parsed(Path(path).read_bytes()); guard()
        return value
    def save(name, value):
        guard()
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write((json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf8"))
        guard(); outputs[key(path)] = digest(path)
    def mapped(raw, base=None):
        require(type(raw) is dict and raw, "PIN_MAP")
        for name, expected in raw.items():
            require(type(name) is str and name and "\\" not in name and ":" not in name
                    and all(v not in ("", ".", "..") for v in name.split("/"))
                    and name != "CLAIMS.yaml" and not name.startswith(".git/"), "PIN_MAP_PATH")
            path = (ROOT / name).resolve()
            if base is not None:
                require(path.is_relative_to(base), "OUTPUT_MAP_SCOPE")
            pin(path, expected)
    def parameter(name):
        path, sha = getattr(args, name.replace("-", "_")), getattr(args, name.replace("-", "_") + "_sha256")
        require(path is not None and sha is not None, "REQUIRED_" + name)
        return pin(path, sha)
    try:
        pin(SELF, args.self_sha256); pin(SPEC, args.spec_sha256)
        for name, sha in PINS.items():
            pin(ROOT / name, sha)
        controls = own_controls(guard, save)
        actual = None
        if args.mode == "full":
            cal = read(parameter("calibration"))
            require(cal.get("status") == CAL_STATUS and cal.get("verifier") == "/root/structural"
                    and equal(cal.get("software"), {key(SELF): args.self_sha256, key(SPEC): args.spec_sha256, **PINS})
                    and type(cal.get("controls", {}).get("positive")) is int
                    and cal["controls"]["positive"] == 13
                    and type(cal.get("controls", {}).get("strict_negative")) is int
                    and cal["controls"]["strict_negative"] == 65, "CALIBRATION_SCOPE")
            mapped(cal["inputs_sha256"]); mapped(cal["outputs_sha256"])
            gate = read(parameter("filter-gate")); mapped(filter_header(gate))
            for name, sha in FIXED.items():
                pin(ROOT / name, sha)
            a, b, masks = model_system(read(ROOT / MODEL), read(ROOT / TYPES), guard)
            subject_path = parameter("producer-summary")
            subject, plan = read(subject_path), read(parameter("producer-plan"))
            require(subject.get("status") == "CANDIDATE_FILTERED_EXTERNAL_MOMENT_EXACT_CERTIFICATE"
                    and subject.get("producer") == "/root/checkpoint_audit"
                    and subject.get("independent_verifier_required") == "/root/structural"
                    and subject.get("implementation_version") == 2 and type(subject["implementation_version"]) is int
                    and subject.get("mode") == "solve" and subject.get("independent_approval") is False,
                    "PRODUCER_SCOPE")
            for name, value in [("tiny_fixture_LP_calls", 3), ("integer_search_calls", 0)]:
                require(type(subject.get(name)) is int and subject[name] == value, "PRODUCER_COUNTS")
            for name in ["original_model_changed", "graph_completion_proved", "whole_family_exclusion",
                         "old_weaker_exact_primal_approval_transferred", "ledger_index_git_mutations"]:
                require(subject.get(name) is False, "PRODUCER_LIMITS")
            require(subject.get("target_resolution") == "NONE", "PRODUCER_LIMITS")
            mapped(subject.get("inputs_sha256"))
            require(all(subject["inputs_sha256"].get(k) == v for k, v in {**PINS, **FIXED}.items())
                    and subject["inputs_sha256"].get(key(parameter("filter-gate"))) == args.filter_gate_sha256,
                    "PRODUCER_DIRECT_PINS")
            mapped(subject.get("outputs_sha256"), subject_path.parent)
            def payload(name):
                path = subject_path.parent / name
                require(subject["outputs_sha256"].get(key(path)) == digest(path), "PAYLOAD_PIN")
                return read(path)
            attempt = payload("attempt.json"); attempt_header(attempt)
            require(equal(subject.get("filtered_result"), attempt)
                    and type(subject.get("target_LP_calls")) is int
                    and subject["target_LP_calls"] == attempt["LP_calls"], "ATTEMPT_SUMMARY")
            kind = attempt["certificate_kind"]
            raw = payload("filtered_" + ("primal" if kind == "primal" else "farkas") + ".json")
            require(equal(raw, attempt["certificate"]), "CERTIFICATE_DUPLICATE")
            exact = certificate(kind, raw, a, b, guard)
            saved_receipt = payload("filtered_primal_rows.json" if kind == "primal" else "filtered_farkas_checks.json")
            exact_receipt(saved_receipt, exact["receipts"])
            mr = payload("model_receipt.json")
            require(equal(mr, dict(model_path=MODEL, model_sha256=FIXED[MODEL], types_path=TYPES,
                                  types_sha256=FIXED[TYPES], rows=154, columns=472, ordered_masks=masks,
                                  old_weaker_feasibility_approval_transferred=False)), "MODEL_RECEIPT")
            rank = 0
            if kind == "primal":
                guidance, support = payload("filtered_primal_guidance.json"), payload("filtered_support.json")
                xs = guidance.get("x")
                require(type(xs) is list and len(xs) == 472 and all(type(v) is float and math.isfinite(v) for v in xs),
                        "GUIDANCE_SHAPE")
                require(equal(support, dict(indices=[i for i, v in enumerate(xs) if v > 0],
                    rule="every numeric coordinate strictly >0.0; no tolerance", numerical_selection_only=True)), "SUPPORT_METADATA")
                require(all(raw["values"][i] == "0" for i in range(472) if i not in support["indices"]), "SUPPORT_EXPANSION")
                metadata = payload("filtered_rref.json")
                rank = metadata.get("rank")
                require(type(rank) is int and 0 <= rank <= min(154, len(support["indices"]))
                        and metadata.get("rank_is_producer_metadata") is True
                        and metadata.get("free_variables_zero") is True, "RREF_METADATA_SCOPE")
                # No rank, pivot or reduced-row arithmetic is used as a premise or approved here.
            declared = [str((ROOT / name).resolve().relative_to(subject_path.parent)).replace("\\", "/")
                        for name in subject["outputs_sha256"]]
            physical = [p.relative_to(subject_path.parent).as_posix() for p in subject_path.parent.rglob("*") if p.is_file()]
            inventory(declared, physical, kind, rank)
            require(not any(p.is_symlink() for p in subject_path.parent.rglob("*")), "OUTPUT_POPULATION")
            author = payload("controls.json")
            require(equal(subject.get("controls"), author) and type(author.get("positive")) is int
                    and author["positive"] == 4 and type(author.get("strict_negative")) is int
                    and author["strict_negative"] == 13 and type(author.get("total")) is int and author["total"] == 17,
                    "AUTHOR_CONTROLS")
            table = author.get("records")
            expected = [("genuine_method_header", "PASS"), ("unique_rational", "PASS"), ("tiny_lp_primal", "PASS"),
                        ("tiny_lp_dual", "PASS")] + AUTHOR_STAGES
            require(equal(table, [dict(case=n, expected_stage=s, actual_stage=s) for n, s in expected]), "AUTHOR_CONTROL_STAGES")
            require(type(author.get("tiny_fixture_LP_calls")) is int and author["tiny_fixture_LP_calls"] == 3
                    and author.get("target_model_read") is False and type(author.get("target_LP_calls")) is int
                    and author["target_LP_calls"] == 0, "AUTHOR_CONTROL_SCOPE")
            # Authenticate all raw author controls; independently replay only their exact certificates.
            certificate("primal", payload("control_lp_primal_primal.json"), [[1, 0], [0, 1]], [1, 1], guard)
            certificate("farkas", payload("control_lp_dual_farkas.json"), [[1]], [-1], guard)
            unique = payload("control_unique_rational.json")
            require(equal(unique, dict(a=[[1, 2], [2, 1]], rhs=[1, 1], values=["1/3", "1/3"])), "AUTHOR_HAND_VALUES")
            certificate("primal", primal(unique["values"]), unique["a"], unique["rhs"], guard)
            require(type(plan) is dict and plan.get("source") == PRODUCER and plan.get("source_sha256") == PINS[PRODUCER]
                    and plan.get("spec_sha256") == PINS[PRODUCER_SPEC], "PLAN_SOURCE")
            science = plan.get("solve")
            require(type(science) is dict and type(science.get("command")) is list, "PLAN_CONCRETE")
            command = science["command"]
            child = command[command.index("--") + 1:]
            require(equal(science.get("child_argv"), child), "PLAN_CHILD")
            require(len(command) == 36 and len(child) == 20 and command.index("--") == 15
                    and Path(command[0]).resolve() == (ROOT / "build/research-venv/Scripts/python.exe").resolve()
                    and command[1] == "-B" and Path(command[2]).resolve() == (ROOT / "acceleration/run_compute_command.py").resolve()
                    and command[3:7] == ["--seconds", "300", "--shutdown-reserve-seconds", "20"]
                    and command[7] == "--allocation-reason" and command[9] == "--success-criterion"
                    and command[11] == "--verification-criterion" and command[13] == "--out"
                    and Path(child[0]).resolve() == Path("C:/Users/ikuto/.local/bin/uv.exe").resolve()
                    and child[1:6] == ["run", "--locked", "--offline", "python", "-B"]
                    and Path(child[6]).resolve() == (ROOT / PRODUCER).resolve()
                    and child[7:10] == ["solve", "--seconds", "270"] and child[10] == "--out"
                    and Path(child[11]).resolve() == subject_path.parent
                    and child[12:16] == ["--source-sha256", PINS[PRODUCER], "--spec-sha256", PINS[PRODUCER_SPEC]],
                    "PLAN_PROFILE")
            require(all(type(science.get("allocation", {}).get(k)) is int and science["allocation"][k] == v
                        for k, v in [("outer", 300), ("worker", 270), ("save", 20), ("shutdown", 20)]), "PLAN_ALLOCATION")
            require("solve" in child and "--full-gate" in child and "--full-gate-sha256" in child
                    and child[child.index("--full-gate-sha256") + 1] == args.filter_gate_sha256
                    and Path(child[child.index("--full-gate") + 1]).resolve() == Path(args.filter_gate).resolve(), "PLAN_FILTER_GATE")
            require(Path(args.runtime_manifest).resolve().parent == Path(args.runtime_summary).resolve().parent
                    and Path(command[14]).resolve() == Path(args.runtime_manifest).resolve().parent,
                    "PLAN_RUNTIME_ROOT")
            runtime_result = runtime(read(parameter("runtime-manifest")), read(parameter("runtime-summary")),
                                     child, subject, science["allocation"]["outer"])
            exact.pop("receipts")
            statement = ("The fixed 472-column, 154-equation filtered necessary external-neighborhood moment system "
                "has the saved nonnegative rational feasible vector; every original equation holds exactly." if kind == "primal" else
                "The fixed 472-column, 154-equation filtered necessary external-neighborhood moment system has "
                "the saved rational Farkas vector: all 472 column dots are nonnegative and its RHS dot is strictly negative, "
                "so that exact rational nonnegative system is infeasible.")
            actual = dict(certificate_kind=kind, statement=statement, exact=exact, rows=154, columns=472,
                          producer_output_files=len(physical), author_positive=4, author_strict_negative=13,
                          model_path=MODEL, model_sha256=FIXED[MODEL], types_path=TYPES, types_sha256=FIXED[TYPES],
                          runtime=runtime_result, rank_and_pivot_mathematics_checked=False,
                          graph_completion_proved=False, integer_realization_proved=False)
            save("exact_certificate_outcome.json", actual)
        for name, sha in list(inputs.items()):
            pin(ROOT / name, sha)
        summary = dict(status=CAL_STATUS if args.mode == "calibrate" else FULL_STATUS,
            timestamp=datetime.now(timezone.utc).isoformat(), producer="/root/checkpoint_audit", verifier="/root/structural",
            method="independent_artifact_check", target_resolution="NONE", implementation_version=3,
            command=[sys.executable] + sys.argv, cwd=str(ROOT), python=platform.python_version(),
            software={key(SELF): args.self_sha256, key(SPEC): args.spec_sha256, **PINS},
            inputs_sha256=inputs.copy(), outputs_sha256=outputs.copy(), controls=controls, outcome=actual,
            genuine_runtime_read=args.mode == "full", target_model_read=args.mode == "full",
            producer_outputs_checked=args.mode == "full", LP_calls=0, RREF_calls=0,
            scope=dict(description="One exact fixed filtered necessary moment relaxation; no outside graph, full family or global target conclusion",
                       unrestricted=False, target_resolution="NONE"),
            limitations=["Native COMPLETE is the independently authenticated filter/type eligibility premise",
                "Python Fraction, integer arithmetic, JSON, SHA256, deadline and Windows supervisor are shared trust",
                "No producer LP/RREF code is imported; floating statuses and rank/pivots are not mathematical premises",
                "Hand controls and synthetic runtime are finite; no synthetic fixture is an observed producer execution",
                "Guidance-only output is rejected as absent certificate, not interpreted as infeasibility",
                "Rational feasibility alone is not integer realizability or graph completion; infeasibility concerns this fixed relaxation only"],
            deadline=guard())
        save("summary.json", summary)
        guard()
    except Exception as exc:
        failure = dict(status="FAILED_PRESERVED", timestamp=datetime.now(timezone.utc).isoformat(), stage=str(exc),
                       exception_type=type(exc).__name__, inputs_sha256=inputs, outputs_sha256=outputs,
                       no_automatic_retry=True, no_infeasibility_inference=True, deadline=deadline.status())
        (out / "failure.json").write_text(json.dumps(failure, indent=2, allow_nan=False) + "\n", encoding="utf8")
        raise


if __name__ == "__main__":
    main()
