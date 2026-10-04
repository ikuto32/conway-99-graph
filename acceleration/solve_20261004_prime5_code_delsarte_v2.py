"""Small numerical guides followed by exact rational code-LP dual candidates."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/solve_20261004_prime5_code_delsarte_v2.py"
SPEC = "acceleration/solve_20261004_prime5_code_delsarte_v2_spec.md"
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
SUPPORT_ID = "C-UNRESTRICTED-TARGET-PRIME5-LEFT-CODE-SUPPORT-LOWER55"
COUNTS_ID = "C-PRIME5-LINEAR-TRIPLE-IMAGE-WEIGHT-COUNTS"
LOWER = {"3": 924, "4": 8316, "5": 24948, "6": 391776}


class Veto(ValueError):
    def __init__(self, stage, detail=None):
        super().__init__(stage)
        self.stage, self.detail = stage, detail


def need(ok, stage, detail=None):
    if not ok:
        raise Veto(stage, detail)


def unique(items):
    value = {}
    for key, item in items:
        need(type(key) is str and key not in value, "DUPLICATE_KEY")
        value[key] = item
    return value


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


class Context:
    def __init__(self, seconds, out):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            "One new code-LP invocation; all guidance, exact candidate checks, files and seals share this deadline.")
        self.out, self.inputs, self.LP_calls = out, {}, 0
        self.progress = {"completed_cases": [], "active_case": None, "phase": "input"}

    def tick(self):
        need(self.deadline.status()["remaining_seconds"] > 20, "SAVE_GUARD")

    def raw(self, path, sha):
        self.tick()
        need(type(path) is str and path and "\\" not in path and ":" not in path
             and not path.startswith("/") and all(x not in ("", ".", "..") for x in path.split("/")), "INPUT_PATH")
        actual = ROOT / path
        need(actual.is_file() and not actual.is_symlink()
             and all(not p.is_symlink() for p in actual.parents)
             and actual.resolve().is_relative_to(ROOT) and actual.stat().st_size <= 2*1024*1024, "INPUT_PATH")
        need(type(sha) is str and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha), "INPUT_SHA")
        data = actual.read_bytes()
        need(hashlib.sha256(data).hexdigest() == sha, "INPUT_SHA")
        self.inputs[path] = sha
        self.tick()
        return data

    def ref(self, ref):
        need(type(ref) is dict and set(ref) == {"path", "sha256"}, "REFERENCE")
        return json.loads(self.raw(ref["path"], ref["sha256"]), object_pairs_hook=unique)

    def checkpoint(self, name):
        self.tick()
        save(self.out / name, {"progress": copy.deepcopy(self.progress),
             "LP_calls": self.LP_calls, "deadline": self.deadline.status()})
        self.tick()


def parameters(q, n, distance, degree, lower):
    need(type(q) is int and q in (2, 5) and type(n) is int and 1 <= n <= 99
         and type(distance) is int and 1 <= distance <= n
         and type(degree) is int and 1 <= degree <= min(32, n), "PARAMETERS")
    need(type(lower) is dict, "LOWER_SHAPE")
    for key, value in lower.items():
        need(type(key) is str and key.isdecimal() and str(int(key)) == key
             and 1 <= int(key) <= degree, "LOWER_KEY")
        need(type(value) is int, "LOWER_INTEGER")
        need(0 <= value <= math.comb(n, int(key))*(q-1)**int(key), "LOWER_RANGE")


def kraw(q, n, j, i):
    need(all(type(x) is int for x in (q, n, j, i)) and q in (2, 5)
         and 0 <= j <= n <= 99 and 0 <= i <= n, "KRAW_PARAMETERS")
    return sum((-1)**ell * (q-1)**(j-ell) * math.comb(i, ell) * math.comb(n-i, j-ell)
               for ell in range(max(0, j-(n-i)), min(i, j)+1))


def rational(text):
    need(type(text) is str and len(text) <= 2048, "FRACTION_TEXT")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError):
        raise Veto("FRACTION_CANONICAL") from None
    need(str(value) == text and value.denominator <= 10**512, "FRACTION_CANONICAL")
    return value


def certificate(q, n, distance, degree, lower, texts):
    parameters(q, n, distance, degree, lower)
    need(type(texts) is list and len(texts) == degree, "COEFFICIENT_SHAPE")
    ys = [rational(t) for t in texts]
    need(all(y >= 0 for y in ys), "COEFFICIENT_SIGN")
    values = []
    for i in [0, *range(distance, n+1)]:
        value = 1+sum(ys[j-1]*(kraw(q, n, j, i)-lower.get(str(j), 0)) for j in range(1, degree+1))
        need(i == 0 or value <= 0, "POLYNOMIAL_SIGN", {"weight": i, "value": str(value)})
        values.append({"weight": i, "value": str(value)})
    bound = rational(values[0]["value"])
    need(bound >= 1, "ZERO_CODE_BOUND")
    dimension, power = 0, 1
    while power*q <= bound:
        dimension, power = dimension+1, power*q
    return {"schema": "EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1", "q": q, "n": n,
            "minimum_distance": distance, "degree": degree, "dual_lower_counts": lower,
            "multipliers": texts, "polynomial_values": values, "code_size_upper": str(bound),
            "integer_dimension_upper": dimension, "dimension_lower_power": power,
            "dimension_next_power": power*q, "nonzero_code_forced": False,
            "is_optimality_certificate": False, "target_resolution": "NONE"}


def rescale(q, n, distance, degree, lower, floats, scales=None):
    parameters(q, n, distance, degree, lower)
    need(type(floats) is list and len(floats) == degree
         and all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in floats), "GUIDANCE_COEFFICIENTS")
    # A negative solver coefficient is never silently clipped. No further backend call occurs.
    if scales is None:
        scales = [1]*degree
    need(type(scales) is list and len(scales) == degree
         and all(type(s) is int and s > 0 for s in scales), "GUIDANCE_SCALES")
    # Rationalize the moderate scaled variables first. Direct rounding of
    # y_j near 1/K_j(0) could erase every high-degree direction.
    ys = [Fraction(v).limit_denominator(10**8)/s for v, s in zip(floats, scales)]
    tails = [sum(ys[j-1]*(kraw(q, n, j, i)-lower.get(str(j), 0))
                 for j in range(1, degree+1)) for i in range(distance, n+1)]
    need(all(v < 0 for v in tails), "RATIONAL_DIRECTION")
    scale = max(Fraction(1), max(-1/v for v in tails))
    return certificate(q, n, distance, degree, lower, [str(y*scale) for y in ys])


def guide(ctx, q, n, distance, degree, lower):
    parameters(q, n, distance, degree, lower)
    ctx.tick()
    from scipy.optimize import linprog
    from scipy import __version__ as scipy_version
    need(scipy_version == "1.18.1", "BACKEND_VERSION")
    # Column scaling keeps the numerical inputs moderate; it is never a proof.
    scales = [kraw(q, n, j, 0) for j in range(1, degree+1)]
    costs = [(scales[j-1]-lower.get(str(j), 0))/scales[j-1] for j in range(1, degree+1)]
    rows = [[(kraw(q, n, j, i)-lower.get(str(j), 0))/scales[j-1]
             for j in range(1, degree+1)] for i in range(distance, n+1)]
    seconds = min(20.0, ctx.deadline.status()["remaining_seconds"]-40)
    need(seconds > 0, "SAVE_GUARD")
    ctx.LP_calls += 1
    result = linprog(costs, A_ub=rows, b_ub=[-1.0]*len(rows), bounds=(0, None),
                     method="highs", options={"time_limit": seconds, "presolve": True})
    ctx.tick()
    guidance = {"schema": "NUMERICAL_CODE_LP_GUIDANCE_V1", "status": int(result.status),
                "message": str(result.message), "scipy_version": scipy_version,
                "variable_count": degree, "constraint_count": len(rows), "time_limit_seconds": seconds,
                "solver_success": bool(result.success), "fun": None if result.fun is None else float(result.fun),
                "scaled_variables": None if result.x is None else [float(x) for x in result.x],
                "is_exact_certificate": False}
    if not result.success or result.x is None:
        return guidance, None, "NUMERICAL_GUIDE_UNKNOWN"
    try:
        candidate = rescale(q, n, distance, degree, lower, [float(x) for x in result.x], scales)
    except Veto as exc:
        return guidance, None, exc.stage
    return guidance, candidate, None


def software(ctx, self_sha, spec_sha):
    ctx.raw(SELF, self_sha)
    ctx.raw(SPEC, spec_sha)
    for path, sha in SOFTWARE.items():
        ctx.raw(path, sha)


def claim_binding(ctx, ref, id_, report_ref):
    binding = ctx.ref(ref)
    need(binding.get("schema") == "CLAIM_BINDING_SCHEMA2" and binding.get("id") == id_
         and type(binding.get("revision")) is int and binding["revision"] == 1
         and binding.get("status") == "VERIFIED" and binding.get("review_state") == "CLEAR"
         and binding.get("producer") == "/root/structural" and binding.get("verifier") == "/root/native_driver"
         and binding.get("method") == "independent_derivation"
         and type(binding.get("scope")) is dict and binding["scope"].get("unrestricted_target") is True
         and binding["scope"].get("target_resolution") == "NONE", "PREMISE_HEADER")
    need(binding.get("report") == report_ref["path"] and binding.get("report_sha256") == report_ref["sha256"], "PREMISE_REPORT")
    ctx.ref(report_ref)
    return binding


def configuration(ctx, ref, self_sha, spec_sha):
    config = ctx.ref(ref)
    keys = {"schema", "parameters", "support_binding", "support_report", "support_acceptance",
            "counts_binding", "counts_report", "counts_acceptance", "author_controls",
            "author_controls_acceptance", "root_authority"}
    need(type(config) is dict and set(config) == keys and config["schema"] == "PRIME5_CODE_DELSARTE_CONFIGURATION_V2", "CONFIGURATION")
    need(config["parameters"] == {"q": 5, "n": 99, "minimum_distance": 55, "degrees": [20, 32],
                                "image_lower_counts": LOWER}
         and type(config["parameters"].get("q")) is int and type(config["parameters"].get("n")) is int
         and type(config["parameters"].get("minimum_distance")) is int
         and all(type(x) is int for x in config["parameters"].get("degrees", []))
         and all(type(x) is int for x in config["parameters"].get("image_lower_counts", {}).values()), "FIXED_PARAMETERS")
    claim_binding(ctx, config["support_binding"], SUPPORT_ID, config["support_report"])
    claim_binding(ctx, config["counts_binding"], COUNTS_ID, config["counts_report"])
    for label, id_ in (("support", SUPPORT_ID), ("counts", COUNTS_ID)):
        receipt = ctx.ref(config[label+"_acceptance"])
        need(receipt.get("reviewer") == "/root" and receipt.get("claim_id") == id_
             and type(receipt.get("claim_revision")) is int and receipt["claim_revision"] == 1
             and receipt.get("result") in ("PASS_WRITTEN_SCOPE_AND_BOUND_ARTIFACTS", "PASS_WRITTEN_SCOPE_AND_EXACT_BINDING"), "PREMISE_ACCEPTANCE")
    controls = ctx.ref(config["author_controls"])
    need(controls.get("status") == "PRIME5_CODE_DELSARTE_V2_AUTHOR_CONTROLS_PASS"
         and type(controls.get("implementation_version")) is int and controls["implementation_version"] == 2
         and controls.get("source") == {"path": SELF, "sha256": self_sha}
         and controls.get("specification") == {"path": SPEC, "sha256": spec_sha}
         and controls.get("positive") == 10 and type(controls.get("positive")) is int
         and controls.get("negative") == 21 and type(controls.get("negative")) is int, "AUTHOR_CONTROLS")
    receipt = ctx.ref(config["author_controls_acceptance"])
    need(receipt.get("schema") == "ROOT_PRIME5_CODE_DELSARTE_AUTHOR_CONTROLS_ACCEPTANCE_V2"
         and receipt.get("result") == "PASS_ENGINEERING_ONLY" and receipt.get("author_controls") == config["author_controls"], "AUTHOR_ACCEPTANCE")
    authority = ctx.ref(config["root_authority"])
    need(authority.get("schema") == "ROOT_PRIME5_CODE_DELSARTE_ONE_AUTHORITY_V2"
         and authority.get("permitted_mode") == "science"
         and authority.get("source") == {"path": SELF, "sha256": self_sha}
         and authority.get("specification") == {"path": SPEC, "sha256": spec_sha}, "ROOT_AUTHORITY")
    return config


def calibration(ctx):
    def character_control():
        words = ((0, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1))
        sums = []
        dual_weights = [0]*4
        for mask in range(8):
            u = tuple((mask >> bit) & 1 for bit in range(3))
            value = sum((-1)**sum(x*y for x, y in zip(u, word)) for word in words)
            need(value in (0, 4), "HAND_EXPECTATION")
            sums.append(value)
            if value == 4:
                dual_weights[sum(u)] += 1
        need(dual_weights == [1, 0, 0, 1], "HAND_EXPECTATION")
        transformed = [kraw(2, 3, j, 0)+3*kraw(2, 3, j, 2) for j in range(4)]
        need(transformed == [4, 0, 0, 4], "HAND_EXPECTATION")
        zeros = [kraw(2, 3, 0, i) for i in range(4)]
        need(zeros == [1, 1, 1, 1], "HAND_EXPECTATION")
        return {"eight_character_sums": sums, "dual_weight_counts": dual_weights,
                "transformed_weight_counts": transformed, "K0": zeros}

    def cert(q, n, d, degree, lower, ys, expected):
        value = certificate(q, n, d, degree, lower, ys)
        need(value["code_size_upper"] == expected, "HAND_EXPECTATION")
        return value

    def tiny():
        guidance, candidate, reason = guide(ctx, 2, 3, 2, 1, {})
        need(candidate is not None and candidate["code_size_upper"] == "4", "TINY_GUIDE")
        return {"guidance": guidance, "candidate": candidate, "unknown_reason": reason}

    def scaled_control():
        first = rescale(2, 3, 2, 1, {}, [0.99])
        second = rescale(2, 3, 2, 1, {}, [9900000000.0], [10**10])
        need(first["multipliers"] == second["multipliers"] == ["1"], "HAND_EXPECTATION")
        return {"unscaled": first, "scaled": second}

    def high_degree_control():
        value = certificate(5, 32, 1, 32, {}, ["1"]*32)
        need(value["code_size_upper"] == "23283064365386962890625"
             and value["integer_dimension_upper"] == 32
             and len(value["polynomial_values"]) == 33
             and all(row["value"] == "0" for row in value["polynomial_values"][1:]), "HAND_EXPECTATION")
        return value

    def ref_bad():
        return ctx.ref({"path": SELF, "sha256": True})

    def hash_bad():
        return ctx.raw(SELF, "0"*64)

    def output_bad():
        need(not ctx.out.exists(), "OUTPUT_EXISTS")

    actions = [
        ("character_normalization_and_kraw_zero", "PASS", character_control, None),
        ("kraw_first", "PASS", lambda: [kraw(5, 3, 1, i) for i in range(4)], [12, 7, 2, -3]),
        ("kraw_second", "PASS", lambda: [kraw(2, 3, 2, i) for i in range(4)], [3, -1, -1, 3]),
        ("binary_even_three", "PASS", lambda: cert(2, 3, 2, 1, {}, ["1"], "4"), None),
        ("binary_repetition", "PASS", lambda: cert(2, 3, 3, 1, {}, ["1/3"], "2"), None),
        ("quinary_length_one", "PASS", lambda: cert(5, 1, 1, 1, {}, ["1"], "5"), None),
        ("quinary_length_two", "PASS", lambda: cert(5, 2, 2, 1, {}, ["1/2"], "5"), None),
        ("rational_rescale", "PASS", scaled_control, None),
        ("tiny_numerical_guide", "PASS", tiny, None),
        ("boolean_q", "PARAMETERS", lambda: parameters(True, 3, 2, 1, {}), None),
        ("zero_length", "PARAMETERS", lambda: parameters(5, 0, 1, 1, {}), None),
        ("zero_distance", "PARAMETERS", lambda: parameters(5, 3, 0, 1, {}), None),
        ("boolean_degree", "PARAMETERS", lambda: parameters(5, 3, 2, True, {}), None),
        ("noncanonical_lower_key", "LOWER_KEY", lambda: parameters(5, 3, 2, 1, {"01": 0}), None),
        ("late_lower_key", "LOWER_KEY", lambda: parameters(5, 3, 2, 1, {"2": 0}), None),
        ("boolean_lower", "LOWER_INTEGER", lambda: parameters(5, 3, 2, 1, {"1": True}), None),
        ("negative_lower", "LOWER_RANGE", lambda: parameters(5, 3, 2, 1, {"1": -1}), None),
        ("ambient_lower_exceeded", "LOWER_RANGE", lambda: parameters(5, 1, 1, 1, {"1": 5}), None),
        ("short_coefficients", "COEFFICIENT_SHAPE", lambda: certificate(2, 3, 2, 1, {}, []), None),
        ("boolean_fraction", "FRACTION_TEXT", lambda: certificate(2, 3, 2, 1, {}, [True]), None),
        ("float_fraction", "FRACTION_TEXT", lambda: certificate(2, 3, 2, 1, {}, [1.0]), None),
        ("unreduced_fraction", "FRACTION_CANONICAL", lambda: certificate(2, 3, 2, 1, {}, ["2/2"]), None),
        ("zero_denominator", "FRACTION_CANONICAL", lambda: certificate(2, 3, 2, 1, {}, ["1/0"]), None),
        ("negative_coefficient", "COEFFICIENT_SIGN", lambda: certificate(2, 3, 2, 1, {}, ["-1"]), None),
        ("insufficient_coefficient", "POLYNOMIAL_SIGN", lambda: certificate(2, 3, 2, 1, {}, ["1/2"]), None),
        ("last_weight_sign", "POLYNOMIAL_SIGN", lambda: certificate(2, 2, 1, 2, {}, ["0", "1"]), {"weight": 2}),
        ("boolean_sha", "INPUT_SHA", ref_bad, None),
        ("wrong_source_sha", "INPUT_SHA", hash_bad, None),
        ("occupied_output", "OUTPUT_EXISTS", output_bad, None),
        ("high_degree_full_space", "PASS", high_degree_control, None),
        ("degree_cap_33", "PARAMETERS", lambda: parameters(5, 33, 1, 33, {}), None),
    ]
    table = []
    for index, (name, expected, action, reference) in enumerate(actions):
        ctx.tick()
        value, detail = None, None
        try:
            value, actual = action(), "PASS"
            if reference is not None and expected == "PASS":
                need(value == reference, "HAND_EXPECTATION")
        except Veto as exc:
            actual, detail = exc.stage, exc.detail
        if reference is not None and expected != "PASS":
            need(type(detail) is dict and all(detail.get(k) == v for k, v in reference.items()), "HAND_EXPECTATION")
        row = {"index": index, "name": name, "expected": expected, "actual": actual, "detail": detail, "value": value}
        save(ctx.out / f"control_{index:02d}.json", row)
        table.append({k: v for k, v in row.items() if k != "value"})
        need(actual == expected, "CONTROL_STAGE", {"index": index, "expected": expected, "actual": actual})
    save(ctx.out / "controls.json", {"schema": "PRIME5_CODE_DELSARTE_CONTROLS_V2", "rows": table})
    return {"status": "PRIME5_CODE_DELSARTE_V2_AUTHOR_CONTROLS_PASS", "positive": 10, "negative": 21,
            "LP_calls": ctx.LP_calls, "scientific_LP_calls": 0, "target_parameters_read": False}


def science(ctx, config):
    save(ctx.out / "parsed_input.json", {"parameters": config["parameters"],
         "accepted_premise_refs": {k: v for k, v in config.items() if k not in ("schema", "parameters")},
         "not_used_at_degree20_or32": {"96": 924, "99": 2776},
         "historical_dimension27_comparison_is_not_a_new_gate": True})
    results = []
    for degree in (20, 32):
        for name, lower in (("baseline", {}), ("low_image_counts", LOWER)):
            ctx.tick()
            label = f"degree{degree}_{name}"
            ctx.progress.update(active_case=label, phase="numerical_guide")
            guidance, candidate, reason = guide(ctx, 5, 99, 55, degree, lower)
            save(ctx.out / (label+"_guidance.json"), guidance)
            save(ctx.out / (label+"_candidate.json"), {"candidate": candidate, "unknown_reason": reason})
            if candidate is not None:
                save(ctx.out / (label+"_polynomial.json"), {
                     "multipliers": candidate["multipliers"], "values": candidate["polynomial_values"]})
            row = {"case": label, "degree": degree, "image_lower_counts_used": lower,
                   "candidate_available": candidate is not None, "unknown_reason": reason,
                   "code_size_upper": None if candidate is None else candidate["code_size_upper"],
                   "integer_dimension_upper": None if candidate is None else candidate["integer_dimension_upper"],
                   "candidate_stronger_than_historical27": candidate is not None and candidate["integer_dimension_upper"] < 27}
            results.append(row)
            ctx.progress["completed_cases"].append(label)
            ctx.progress.update(active_case=None, phase="checkpoint")
            ctx.checkpoint(label+"_checkpoint.json")
    return {"status": "CANDIDATE_PRIME5_CODE_DELSARTE_V2_COMPLETE", "outcome": results,
            "LP_calls": ctx.LP_calls, "scientific_LP_calls": ctx.LP_calls,
            "target_parameters_read": True, "nonzero_code_forced": False,
            "separate_exact_rational_checker_required": True, "optimality_or_code_realization_claimed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "science"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    ctx = Context(args.seconds, Path(args.out))
    try:
        need(not ctx.out.exists(), "OUTPUT_EXISTS")
        need(ctx.out.resolve().is_relative_to(ROOT / "acceleration/results")
             and all(not p.is_symlink() for p in ctx.out.parents), "OUTPUT_PATH")
        ctx.out.mkdir(parents=True)
        software(ctx, args.self_sha256, args.spec_sha256)
        if args.mode == "calibrate":
            need(args.configuration is None and args.configuration_sha256 is None, "CALIBRATION_SCOPE")
            result = calibration(ctx)
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None, "CONFIGURATION")
            config = configuration(ctx, {"path": args.configuration, "sha256": args.configuration_sha256},
                                   args.self_sha256, args.spec_sha256)
            result = science(ctx, config)
        ctx.tick()
        outputs = {p.relative_to(ctx.out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(ctx.out.rglob("*")) if p.is_file()}
        ctx.tick()
        summary = {"schema": "PRIME5_CODE_DELSARTE_RUN_V2", "implementation_version": 2,
                   "timestamp": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
                   "producer": "/root/structural", "source": {"path": SELF, "sha256": args.self_sha256},
                   "specification": {"path": SPEC, "sha256": args.spec_sha256}, **result,
                   "inputs_sha256": ctx.inputs, "outputs_sha256": outputs,
                   "output_payload_count": len(outputs), "physical_file_count": len(outputs)+1,
                   "deadline": ctx.deadline.status(), "target_resolution": "NONE",
                   "limitations": ["Exact producer candidates require a separately implemented rational checker.",
                     "Numerical failure or infeasibility is UNKNOWN, never code or graph exclusion.",
                     "A successful dual is an upper bound, not an optimum or a code/graph construction.",
                     "L5=0 remains possible. No scientific matrix/code is enumerated."]}
        save(ctx.out / "summary.json", summary)
        ctx.tick()
        print(json.dumps({"status": summary["status"], "summary": str(ctx.out/"summary.json")}))
        return 0
    except Exception as exc:
        if ctx.out.is_dir():
            failure = ctx.out / "failure.json"
            if not failure.exists():
                save(failure, {"status": "FAILED_OR_NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET",
                     "error_type": type(exc).__name__, "error": str(exc), "detail": getattr(exc, "detail", None),
                     "progress": ctx.progress, "LP_calls": ctx.LP_calls, "deadline": ctx.deadline.status(),
                     "provisional_summary_is_not_a_gate": (ctx.out/"summary.json").exists()})
        print(json.dumps({"error": str(exc), "error_type": type(exc).__name__}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
