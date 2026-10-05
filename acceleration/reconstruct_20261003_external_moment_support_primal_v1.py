"""Candidate exact moment primal from a fixed saved numeric support; no LP call."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
BASE = "acceleration/results/20261003_external_neighborhood_moment_seventeen_base01"
SUMMARY = BASE + "/summary.json"
MODEL = BASE + "/seventeen_base/model.json"
TYPES = BASE + "/seventeen_base/types.json"
GUIDANCE = BASE + "/seventeen_base/numerical_guidance.json"
COMPLETION = "acceleration/results/20261003_external_neighborhood_moment_seventeen_base_completion01.json"
RAW_INPUTS = {
    SUMMARY: "23fc6d633fe626a0a8141d3f974c415b6a559c6b67c60f231de8c412b63672d0",
    MODEL: "d5f1afaf937b75c22f6e5d5c376a36f55f9326dc131399011a5502598742a3f9",
    TYPES: "4799c4603dc949ace22184c5742816eb0dbfe1bd6ea9b2d0ff407678e13de46a",
    GUIDANCE: "ee318f07cc7d7d21c4c232b5ef7bca5c8a0da5e5dc15efa3b2b6c35a581c4461",
    COMPLETION: "799400d2decc46518829f98f4e18a6cdc9339857890c8a1d5429d97b894bd508",
}
FULL_HEADER = "INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS"


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def typed_equal(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def tick(deadline):
    snapshot = deadline.status()
    need(not snapshot["stop_required"] and snapshot["remaining_seconds"] > 20, "SAVE_RESERVE")


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, "JSON_BYTES")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


def system(a, rhs):
    need(type(a) is list and a and type(rhs) is list and len(rhs) == len(a), "SYSTEM_SHAPE")
    need(type(a[0]) is list and a[0], "SYSTEM_SHAPE")
    columns = len(a[0])
    need(all(type(row) is list and len(row) == columns for row in a), "SYSTEM_SHAPE")
    need(all(type(value) is int for row in a for value in row)
         and all(type(value) is int for value in rhs), "SYSTEM_INTEGER")
    return [[Fraction(value) for value in row] + [Fraction(b)] for row, b in zip(a, rhs)]


def rref_solve(a, rhs, deadline, checkpoint=None, progress=False):
    """First available row pivot, left-to-right columns, exact Q; free variables zero."""
    reduced = system(a, rhs)
    count = len(a[0])
    pivots = []
    row_order = list(range(len(a)))
    target_row = 0
    columns = range(count)
    if progress:
        columns = tqdm(columns, total=count, desc="exact support columns", unit="column")
    for column in columns:
        tick(deadline)
        found = next((i for i in range(target_row, len(reduced)) if reduced[i][column]), None)
        if found is None:
            continue
        reduced[target_row], reduced[found] = reduced[found], reduced[target_row]
        row_order[target_row], row_order[found] = row_order[found], row_order[target_row]
        pivot = reduced[target_row][column]
        reduced[target_row][column:] = [value / pivot for value in reduced[target_row][column:]]
        for i, row in enumerate(reduced):
            tick(deadline)
            if i != target_row and row[column]:
                factor = row[column]
                row[column:] = [left - factor * right
                                for left, right in zip(row[column:], reduced[target_row][column:])]
        pivots.append({"row": target_row, "column": column, "original_row": row_order[target_row],
                       "pivot_before_normalization": str(pivot)})
        target_row += 1
        if checkpoint is not None and target_row % 10 == 0:
            checkpoint(reduced, pivots, row_order)
        tick(deadline)
    need(not any(all(value == 0 for value in row[:-1]) and row[-1] != 0 for row in reduced),
         "INCONSISTENT_SUPPORT")
    answer = [Fraction(0) for _ in range(count)]
    for record in pivots:
        answer[record["column"]] = reduced[record["row"]][-1]
    need(all(value >= 0 for value in answer), "NEGATIVE_SOLUTION")
    # This also checks the original unreduced rows before anything is a primal.
    need(all(sum(Fraction(c) * x for c, x in zip(row, answer)) == b
             for row, b in zip(a, rhs)), "SUPPORT_MOMENTS")
    return answer, reduced, pivots, row_order


def own_controls(deadline, save, read):
    cases = [
        ("unique_rational", [[2, 1], [1, -1]], [1, 0], "PASS", ["1/3", "1/3"]),
        ("free_variable_zero", [[1, 1]], [1], "PASS", ["1", "0"]),
        ("inconsistent_rows", [[1], [1]], [1, 2], "INCONSISTENT_SUPPORT", None),
        ("negative_solution", [[1]], [-1], "NEGATIVE_SOLUTION", None),
        ("bool_coefficient", [[True]], [1], "SYSTEM_INTEGER", None),
    ]
    records = []
    for label, matrix, rhs, wanted, solution in cases:
        tick(deadline)
        filename = "control_" + label + ".json"
        save(filename, {"matrix": matrix, "rhs": rhs, "expected_stage": wanted,
                        "expected_solution": solution})
        payload = read(ROOT / save.output_relative / filename)
        actual = "PASS"
        observed = None
        try:
            x, _, pivots, _ = rref_solve(payload["matrix"], payload["rhs"], deadline)
            observed = [str(value) for value in x]
        except ValueError as error:
            actual = str(error)
        need(actual == wanted, "CONTROL_STAGE:" + label)
        if wanted == "PASS":
            need(typed_equal(observed, solution), "CONTROL_SOLUTION:" + label)
        records.append({"case": label, "expected_stage": wanted, "actual_stage": actual,
                        "expected_solution": solution, "actual_solution": observed})
    save("controls.json", {"positive": 2, "strict_negative": 3, "total": 5, "records": records,
                          "synthetic_exact_systems": True, "graph_realizations": 0})
    return {"positive": 2, "strict_negative": 3, "total": 5}


def validate_saved_model(model, types, guidance):
    need(type(model) is dict and model.get("schema") == "EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1", "MODEL_SCHEMA")
    for key, value in [("target_order", 99), ("target_degree", 14), ("adjacent_cn", 1),
                       ("nonadjacent_cn", 2), ("eligible_type_count", 534)]:
        need(type(model.get(key)) is int and model[key] == value, "MODEL_PARAMETER:" + key)
    need(typed_equal(model.get("ordered_support_vertices"), list(range(17))), "MODEL_POINT_ORDER")
    pairs = list(itertools.combinations(range(17), 2))
    labels = [{"kind": "total"}] + [{"kind": "vertex", "vertex": i} for i in range(17)]
    labels += [{"kind": "pair", "vertices": list(pair)} for pair in pairs]
    need(typed_equal(model.get("row_labels"), labels), "MODEL_ROW_ORDER")
    rhs = model.get("right_hand_side")
    need(type(rhs) is list and len(rhs) == 154 and all(type(x) is int and x >= 0 for x in rhs),
         "MODEL_RHS_INTEGER")
    need(type(types) is list and len(types) == 534, "TYPE_POPULATION")
    previous = -1
    for record in types:
        need(type(record) is dict and set(record) == {"mask", "coefficient"}, "TYPE_FIELDS")
        mask = record["mask"]
        need(type(mask) is int and previous < mask < 2 ** 17, "TYPE_MASK_ORDER")
        bits = [(mask >> i) & 1 for i in range(17)]
        coefficients = [1] + bits + [bits[i] * bits[j] for i, j in pairs]
        need(type(record["coefficient"]) is list
             and all(type(x) is int for x in record["coefficient"])
             and typed_equal(record["coefficient"], coefficients), "TYPE_COEFFICIENT")
        previous = mask
    need(type(guidance) is dict and guidance.get("certificate") is False, "GUIDANCE_NOT_CERTIFICATE")
    values = guidance.get("primal_float64")
    need(type(values) is list and len(values) == 534, "GUIDANCE_LENGTH")
    need(all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in values), "GUIDANCE_VALUES")
    support = [i for i, value in enumerate(values) if value > 0.0]
    need(len(support) == 109, "FIXED_POSITIVE_SUPPORT_POPULATION")
    return rhs, support


def reconstruct(model, types, guidance, deadline, save):
    rhs, support = validate_saved_model(model, types, guidance)
    save("support.json", {"selection_rule": "All saved finite numeric values strictly >0.0; no tolerance",
                         "ordered_type_indices": support, "ordered_masks": [types[i]["mask"] for i in support],
                         "numeric_values_are_support_guidance_only": True,
                         "saved_numeric_values": [guidance["primal_float64"][i] for i in support]})
    matrix = [[types[i]["coefficient"][row] for i in support] for row in range(154)]
    def checkpoint(reduced, pivots, order):
        save("pivot_%03d.json" % len(pivots),
             {"rank_so_far": len(pivots), "support_indices": support, "pivots": pivots,
              "original_row_order": order, "augmented_rref_so_far": [[str(v) for v in row] for row in reduced],
              "complete_solution_claimed": False})
    x, reduced, pivots, order = rref_solve(matrix, rhs, deadline, checkpoint, True)
    full = [Fraction(0) for _ in range(534)]
    for index, value in zip(support, x):
        full[index] = value
    need(all(value >= 0 for value in full), "PRIMAL_NONNEGATIVE")
    rows = []
    for row in range(154):
        tick(deadline)
        observed = sum(value * record["coefficient"][row] for value, record in zip(full, types))
        need(observed == rhs[row], "FULL_MOMENT_ROW:%d" % row)
        rows.append({"row": row, "label": model["row_labels"][row], "computed": str(observed),
                     "rhs": rhs[row], "exactly_equal": True})
    integer = all(value.denominator == 1 for value in full)
    primal = {"status": "CANDIDATE_EXACT_MOMENT_PRIMAL",
              "values": [str(value) for value in full], "integer": integer}
    save("rref.json", {"rank": len(pivots), "support_columns": 109, "moment_rows": 154,
                      "pivots": pivots, "original_row_order": order,
                      "free_support_columns": [i for i in range(109) if i not in {p["column"] for p in pivots}],
                      "free_variables_set_to_zero": True,
                      "augmented_rref": [[str(value) for value in row] for row in reduced]})
    save("row_checks.json", rows)
    # Existing independently qualified three-field primal contract; no new headline in its schema.
    save("primal.json", primal)
    return {"complete_moment_rows": 154, "full_primal_coordinates": 534, "selected_support_columns": 109,
            "rank": len(pivots), "free_support_variables": 109 - len(pivots),
            "nonnegative_exact_rational": True, "integer": integer,
            "nonzero_exact_coordinates": sum(value != 0 for value in full)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["calibrate", "reconstruct"])
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--full-gate", type=Path)
    parser.add_argument("--full-gate-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Exact fixed-support Fraction RREF; all authentication, controls, arithmetic and preservation inside one invocation")
    out = args.out.resolve()
    need(out.is_relative_to(ROOT / "acceleration/results") and not out.exists(), "FRESH_OUTPUT")
    out.mkdir(parents=True)
    pins = {}
    def digest(path):
        tick(deadline)
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                sha.update(block)
                tick(deadline)
        tick(deadline)
        return sha.hexdigest()
    def pin(path, expected=None):
        path = Path(path).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), "INPUT_PATH")
        name = path.relative_to(ROOT).as_posix()
        need(name != "CLAIMS.yaml" and not name.startswith(".git/"), "MUTABLE_INPUT")
        observed = digest(path)
        need(expected is None or type(expected) is str and observed == expected, "INPUT_SHA:" + name)
        need(name not in pins or pins[name] == observed, "CONFLICTING_INPUT:" + name)
        pins[name] = observed
        return path
    def read(path, expected=None):
        value = strict_json(pin(path, expected).read_bytes())
        tick(deadline)
        return value
    def save(name, value):
        tick(deadline)
        raw = (json.dumps(value, allow_nan=False, indent=2) + "\n").encode("utf8")
        tick(deadline)
        with (out / name).open("xb") as stream:
            for start in range(0, len(raw), 1024 * 1024):
                stream.write(raw[start:start + 1024 * 1024])
                tick(deadline)
        tick(deadline)
    save.output_relative = out.relative_to(ROOT)
    try:
        for name, expected in SOFTWARE.items():
            pin(ROOT / name, expected)
        pin(SELF, args.source_sha256)
        pin(SPEC, args.spec_sha256)
        controls = own_controls(deadline, save, read)
        result = None
        if args.mode == "calibrate":
            need(args.full_gate is None and args.full_gate_sha256 is None, "CALIBRATION_NO_SCIENCE")
            status = "AUTHOR_EXACT_MOMENT_SUPPORT_PRIMAL_V1_CONTROLS_PASS"
        else:
            need(args.full_gate is not None and args.full_gate_sha256 is not None, "GENUINE_FULL_GATE_REQUIRED")
            gate = read(args.full_gate, args.full_gate_sha256)
            need(type(gate) is dict and gate.get("status") == FULL_HEADER
                 and gate.get("producer") == "/root" and gate.get("verifier") == "/root/native_driver"
                 and gate.get("method") == "independent_artifact_check"
                 and gate.get("target_resolution") == "NONE"
                 and type(gate.get("checker_implementation_version")) is int
                 and gate["checker_implementation_version"] == 3, "FULL_GATE_ROLE_SCOPE")
            closure = gate.get("inputs_sha256")
            need(type(closure) is dict and closure, "FULL_GATE_INPUTS")
            for name, expected in closure.items():
                pin(ROOT / name, expected)
            need(all(closure.get(name) == RAW_INPUTS[name] for name in (SUMMARY, MODEL, TYPES, GUIDANCE)),
                 "FULL_GATE_LITERAL_INPUTS")
            packets = {name: read(ROOT / name, expected) for name, expected in RAW_INPUTS.items()}
            need(all(packets[SUMMARY]["outputs_sha256"].get(name) == RAW_INPUTS[name]
                     for name in (MODEL, TYPES, GUIDANCE)), "ORIGINAL_OUTPUT_BINDING")
            need(packets[COMPLETION].get("exact_primal_saved") is False
                 and type(packets[COMPLETION].get("float_nonzero_support_count")) is int
                 and packets[COMPLETION]["float_nonzero_support_count"] == 109
                 and packets[COMPLETION]["inputs_sha256"].get(SUMMARY) == RAW_INPUTS[SUMMARY],
                 "ORIGINAL_COMPLETION")
            result = reconstruct(packets[MODEL], packets[TYPES], packets[GUIDANCE], deadline, save)
            status = "CANDIDATE_EXACT_MOMENT_SUPPORT_PRIMAL_V1_PENDING_INDEPENDENT_CHECK"
        for name, expected in list(pins.items()):
            pin(ROOT / name, expected)
        outputs = {path.relative_to(ROOT).as_posix(): digest(path)
                   for path in sorted(out.iterdir()) if path.is_file()}
        save("summary.json", {"status": status, "timestamp": datetime.now(timezone.utc).isoformat(),
                              "source_author": "/root/checkpoint_audit", "producer": "/root/checkpoint_audit",
                              "independent_verifier_required": "/root/native_driver", "independent_approval": False,
                              "mode": args.mode, "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
                              "python": platform.python_version(), "inputs_sha256": pins,
                              "outputs_sha256": outputs, "controls": controls, "exact_candidate": result,
                              "LP_calls": 0, "model_reenumerations": 0, "target_resolution": "NONE",
                              "graph_completion_claimed": False, "ledger_index_git_mutations": False,
                              "limitations": ["Only the original fixed induced17-point necessary moment relaxation.",
                                              "Numeric positive support selects columns only; no tolerance or numeric proof.",
                                              "Failure of this support/free-zero reconstruction is not infeasibility.",
                                              "Exact rational moment feasibility does not establish graph completion or target existence.",
                                              "All certificates remain candidate until separate Native raw checking."],
                              "deadline": deadline.status()})
        tick(deadline)
        return 0
    except BaseException as error:
        if (out / "summary.json").exists():
            (out / "summary.json").rename(out / "summary.not_approved.json")
        (out / "failure.json").write_text(json.dumps({"status": "FAILED_OR_NOT_COMPLETED_EXACT_SUPPORT_ATTEMPT",
            "error": repr(error), "inputs_sha256": pins, "deadline": deadline.status(),
            "checkpoints_preserved": True, "automatic_retry": False, "target_resolution": "NONE",
            "feasibility_or_nonexistence_inferred": False}, allow_nan=False, indent=2) + "\n", encoding="utf8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
