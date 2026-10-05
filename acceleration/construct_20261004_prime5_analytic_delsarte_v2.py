"""Exact rational analytic q5 Delsarte candidate; no numerical backend."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/construct_20261004_prime5_analytic_delsarte_v2.py"
SPEC = "acceleration/construct_20261004_prime5_analytic_delsarte_v2_spec.md"
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}

class Veto(ValueError):
    pass

def need(ok, stage):
    if not ok:
        raise Veto(stage)

def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")

def canon(value):
    need(type(value) is str and len(value) <= 2048, "FRACTION_TEXT")
    try:
        number = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise Veto("FRACTION_CANONICAL") from None
    need(str(number) == value, "FRACTION_CANONICAL")
    return number

@lru_cache(maxsize=None, typed=True)
def kraw(n, j, i):
    need(all(type(v) is int for v in (n, j, i)) and 0 <= j <= n <= 99 and 0 <= i <= n, "PARAMETERS")
    return sum((-1)**z * 4**(j-z) * math.comb(i, z) * math.comb(n-i, j-z)
               for z in range(max(0, j-(n-i)), min(i, j)+1))

@lru_cache(maxsize=None, typed=True)
def product_coefficient(n, a, b, h):
    need(all(type(v) is int for v in (n, a, b, h))
         and 0 <= a <= n <= 99 and 0 <= b <= n and 0 <= h <= n, "PARAMETERS")
    total = 0
    for d in range(min(a, b, n-h)+1):
        c = a+b-h-2*d
        u, v = a-c-d, b-c-d
        if min(c, u, v) < 0 or u+v+c != h:
            continue
        total += (math.comb(h, c)*math.comb(h-c, u)*3**c
                  * math.comb(n-h, d)*4**d)
    return total

def product_fixture(values):
    need(type(values) is list and len(values) == 3
         and all(type(x) is int for x in values), "PRODUCT_INTEGER")
    actual = [product_coefficient(2, 1, 1, h) for h in range(3)]
    need(values == actual, "PRODUCT_COEFFICIENT")
    return {"coefficients": actual, "values": [
        sum(actual[h]*kraw(2, h, i) for h in range(3)) for i in range(3)]}

def lower_counts(n, degree, lower):
    need(type(lower) is dict, "LOWER_SHAPE")
    for key, value in lower.items():
        need(type(key) is str and key.isdecimal() and str(int(key)) == key
             and 1 <= int(key) <= degree, "LOWER_KEY")
        need(type(value) is int and 0 <= value <= math.comb(n, int(key))*4**int(key), "LOWER_RANGE")

def dual(n, distance, texts, tick=lambda: None, lower=None):
    need(type(n) is int and 1 <= n <= 99 and type(distance) is int
         and 1 <= distance <= n and type(texts) is list and 1 <= len(texts) <= min(32, n), "PARAMETERS")
    ys = [canon(x) for x in texts]
    need(all(x >= 0 for x in ys), "MULTIPLIER_SIGN")
    lower = {} if lower is None else lower
    lower_counts(n, len(texts), lower)
    values = []
    for i in [0, *range(distance, n+1)]:
        tick()
        value = 1+sum(y*(kraw(n, j, i)-lower.get(str(j), 0)) for j, y in enumerate(ys, 1))
        need(i == 0 or value <= 0, "POLYNOMIAL_SIGN")
        values.append({"weight": i, "value": str(value)})
    bound = Fraction(values[0]["value"])
    need(bound >= 1, "ZERO_CODE_BOUND")
    dimension, power = 0, 1
    while power*5 <= bound:
        tick()
        dimension, power = dimension+1, power*5
    return {"schema": "EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1", "q": 5, "n": n,
            "minimum_distance": distance, "degree": len(texts), "dual_lower_counts": lower,
            "multipliers": texts, "polynomial_values": values, "code_size_upper": str(bound),
            "integer_dimension_upper": dimension, "dimension_lower_power": power,
            "dimension_next_power": power*5, "nonzero_code_forced": False,
            "is_optimality_certificate": False, "target_resolution": "NONE"}

def renormalize(baseline, lower, tick=lambda: None):
    need(baseline["dual_lower_counts"] == {}, "BASELINE_LOWER")
    n, degree = baseline["n"], baseline["degree"]
    lower_counts(n, degree, lower)
    ys = [canon(x) for x in baseline["multipliers"]]
    denominator = 1+sum(y*lower.get(str(j), 0) for j, y in enumerate(ys, 1))
    need(denominator > 0, "RENORMALIZATION_SIGN")
    result = dual(n, baseline["minimum_distance"], [str(y/denominator) for y in ys], tick, lower)
    need(result["polynomial_values"] == [
        {"weight": row["weight"], "value": str(Fraction(row["value"])/denominator)}
        for row in baseline["polynomial_values"]], "RENORMALIZATION_IDENTITY")
    return {"denominator": str(denominator), "certificate": result}

def fullspace_fixture(tick):
    baseline = dual(2, 1, ["1", "1"], tick)
    scaled = renormalize(baseline, {"1": 8, "2": 16}, tick)
    need(scaled["denominator"] == "25" and scaled["certificate"]["code_size_upper"] == "1"
         and scaled["certificate"]["integer_dimension_upper"] == 0, "RENORMALIZATION_KNOWN_VALUES")
    return {"baseline": baseline, "renormalized": scaled}

def calibration(out, tick):
    actions = [
        ("product_n2", "PASS", {"coefficients": [8, 3, 2]}, lambda: product_fixture([8, 3, 2])),
        ("full_space_n2", "PASS", {"n": 2, "distance": 1, "multipliers": ["1", "1"], "lower_counts": {"1": 8, "2": 16}},
         lambda: fullspace_fixture(tick)),
        ("wrong_product_constant", "PRODUCT_COEFFICIENT", {"coefficients": [9, 3, 2]},
         lambda: product_fixture([9, 3, 2])),
        ("negative_multiplier", "MULTIPLIER_SIGN", {"n": 2, "distance": 1, "multipliers": ["-1", "1"]},
         lambda: dual(2, 1, ["-1", "1"], tick)),
    ]
    rows = []
    for index, (name, expected, fixture, action) in enumerate(actions):
        tick()
        try:
            result, actual = action(), "PASS"
        except Veto as exc:
            result, actual = None, str(exc)
        save(out / ("fixture_"+str(index)+".json"), {"fixture": fixture, "result": result})
        rows.append({"index": index, "name": name, "expected": expected, "actual": actual,
                     "passed": actual == expected})
        save(out / ("checkpoint_"+str(index)+".json"), {"completed_controls": index+1, "row": rows[-1]})
        need(actual == expected, "CONTROL_STAGE")
        if index == 0:
            need(result["values"] == [64, 9, 4], "PRODUCT_KNOWN_VALUES")
        if index == 1:
            need(result["baseline"]["code_size_upper"] == "25" and result["baseline"]["integer_dimension_upper"] == 2
                 and result["baseline"]["polynomial_values"] == [
                     {"weight": 0, "value": "25"}, {"weight": 1, "value": "0"}, {"weight": 2, "value": "0"}],
                 "FULLSPACE_KNOWN_VALUES")
        tick()
    save(out / "controls.json", rows)
    return {"status": "PRIME5_ANALYTIC_DELSARTE_V2_AUTHOR_CONTROLS_PASS",
            "positive_controls": 2, "negative_controls": 2, "control_count": 4,
            "target_polynomial_constructed": False, "target_certificate": None}

LOWER = {"3": 924, "4": 8316, "5": 24948, "6": 391776}
T_VALUES = tuple(range(8, 16))
S_INTEGERS = tuple(range(121, 161))
S_NEAR_DENOMINATORS = (2, 4, 8, 16, 32, 64, 128, 256)

def build_case(t, s, tick):
    n, p = 99, [Fraction(1)]
    trace = {"q": 5, "n": n, "minimum_distance": 55, "s": str(s), "t": t}
    for k in range(t):
        tick()
        previous = p[k-1] if k else Fraction(0)
        value = ((s-3*k)*p[k]-k*previous)/(4*(n-k))
        p.append(value)
        if value <= 0:
            return {**trace, "status": "REJECTED_CONSTRUCTION", "first_veto": "RECURRENCE_SIGN",
                    "failed_p_index": k+1, "p_coefficients": [str(x) for x in p],
                    "failed_value": str(value), "g_coefficients": None}
    g = [Fraction(0)]*(t+2)
    for k in range(t+2):
        tick()
        g[k] = ((k*p[k-1] if 0 <= k-1 <= t else 0)
                + ((3*k-s)*p[k] if k <= t else 0)
                + (4*(n-k)*p[k+1] if k+1 <= t else 0))
    need(all(x == 0 for x in g[:t]) and g[t+1] == (t+1)*p[t], "TRUNCATED_PRODUCT")
    trace.update(p_coefficients=[str(x) for x in p], g_coefficients=[str(x) for x in g])
    if g[t] <= 0:
        return {**trace, "status": "REJECTED_CONSTRUCTION", "first_veto": "TRUNCATED_SIGN",
                "failed_g_index": t, "failed_value": str(g[t])}
    coeff = [Fraction(0)]*(2*t+2)
    for h in range(len(coeff)):
        tick()
        coeff[h] = sum(g[a]*p[b]*product_coefficient(n, a, b, h)
                       for a in (t, t+1) for b in range(t+1))
        need(coeff[h] >= 0, "EXPANSION_SIGN")
    constant = g[t]*p[t]*4**t*math.comb(n, t)
    need(coeff[0] == constant and constant > 0 and coeff[-1] > 0, "CONSTANT_COEFFICIENT")
    texts = [str(coeff[j]/constant) if j < len(coeff) else "0" for j in range(1, 33)]
    baseline = dual(99, 55, texts, tick)
    for row in baseline["polynomial_values"]:
        tick()
        i = row["weight"]
        pvalue = sum(p[j]*kraw(n, j, i) for j in range(t+1))
        need(Fraction(row["value"]) == (kraw(n, 1, i)-s)*pvalue*pvalue/constant,
             "FACTORIZATION_IDENTITY")
    scaled = renormalize(baseline, LOWER, tick)
    return {**trace, "status": "CANDIDATE_CERTIFICATES", "first_veto": None,
            "f_coefficients": [str(x) for x in coeff], "constant_coefficient": str(constant),
            "baseline": baseline, "low_image_counts": scaled["certificate"],
            "renormalization_denominator": scaled["denominator"]}

def science(out, tick, progress):
    s_values = [Fraction(s) for s in S_INTEGERS]+[
        Fraction(121*d+1, d) for d in S_NEAR_DENOMINATORS]
    selected = [(t, s) for t in T_VALUES for s in s_values]
    need(len(selected) == 384 and len(set(selected)) == 384, "FAMILY_UNIVERSE")
    best, valid, rejected, veto_counts = {"baseline": None, "low_image_counts": None}, 0, 0, {}
    for index, (t, s) in enumerate(selected):
        tick()
        progress.update(active_case={"index": index, "t": t, "s": str(s)})
        result = {"case_index": index, **build_case(t, s, tick)}
        save(out / ("case_"+str(index).zfill(4)+".json"), result)
        if result["status"] == "REJECTED_CONSTRUCTION":
            rejected += 1
            stage = result["first_veto"]
            veto_counts[stage] = veto_counts.get(stage, 0)+1
        else:
            valid += 1
            for branch in best:
                candidate = result[branch]
                if best[branch] is None or Fraction(candidate["code_size_upper"]) < Fraction(best[branch]["code_size_upper"]):
                    best[branch] = {"case_index": index, "t": t, "s": str(s),
                        "code_size_upper": candidate["code_size_upper"],
                        "integer_dimension_upper": candidate["integer_dimension_upper"],
                        "dimension_lower_power": candidate["dimension_lower_power"],
                        "dimension_next_power": candidate["dimension_next_power"],
                        "stronger_than_historical27": candidate["integer_dimension_upper"] < 27}
        progress.update(completed_cases=index+1, active_case=None)
        save(out / ("case_"+str(index).zfill(4)+"_checkpoint.json"),
             {"completed_cases": index+1, "valid_cases": valid, "rejected_cases": rejected,
              "first_veto_counts": veto_counts.copy(), "best": {key: None if row is None else row.copy() for key, row in best.items()}})
        tick()
    return {"status": "CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V2_FAMILY_COMPLETE",
            "selected_cases": 384, "completed_cases": 384, "valid_cases": valid,
            "rejected_cases": rejected, "first_veto_counts": veto_counts, "best": best,
            "objective": "Lowest exact rational size upper; equal objectives retain first frozen case index.",
            "target_polynomial_constructed": valid > 0, "separate_exact_checker_required": True,
            "image_counts_authenticated_inside_worker": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "science"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="One fixed384-case exact analytic family or four tiny controls, including all rational work and output seals.")
    out, inputs, phase = Path(args.out), {}, "admission"
    progress = {"completed_cases": 0, "active_case": None}
    def tick():
        need(deadline.status()["remaining_seconds"] > 20, "SAVE_GUARD")
    try:
        tick()
        need(not out.exists(), "OUTPUT_EXISTS")
        need(out.resolve().is_relative_to(ROOT / "acceleration/results")
             and all(not path.is_symlink() for path in out.parents), "OUTPUT_PATH")
        out.mkdir(parents=True)
        for path, expected in {SELF: args.self_sha256, SPEC: args.spec_sha256, **SOFTWARE}.items():
            tick()
            need(type(expected) is str and len(expected) == 64
                 and all(x in "0123456789abcdef" for x in expected), "SOFTWARE_SHA")
            raw = (ROOT/path).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == expected, "SOFTWARE_SHA")
            inputs[path] = expected
        phase = args.mode
        result = calibration(out, tick) if args.mode == "calibrate" else science(out, tick, progress)
        tick()
        outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(out.iterdir()) if path.is_file()}
        tick()
        summary = {"schema": "PRIME5_ANALYTIC_DELSARTE_RUN_V2", "implementation_version": 2,
             "mode": args.mode, "timestamp": datetime.now(timezone.utc).isoformat(),
             "producer": "/root/structural", "source": {"path": SELF, "sha256": args.self_sha256},
             "specification": {"path": SPEC, "sha256": args.spec_sha256}, **result,
             "inputs_sha256": inputs, "outputs_sha256": outputs,
             "output_payload_count": len(outputs), "physical_file_count": len(outputs)+1,
             "deadline": deadline.status(), "progress": progress, "LP_calls": 0, "target_resolution": "NONE",
             "target_graph_read": False, "nonzero_code_forced": False,
             "support_assumption_authenticated_inside_worker": False,
             "limitations": ["Finite selected analytic q5 length99/minimum-distance55 family, not all duals.",
                  "Target applicability uses separately accepted support55 and image-count theorems.",
                  "Old numerical-producer or checker gates do not qualify this source.",
                  "No optimum, nonzero code or target exclusion is inferred."]}
        save(out / "summary.json", summary)
        tick()
        print(json.dumps({"status": summary["status"], "summary": str(out/"summary.json")}))
        return 0
    except Exception as exc:
        if out.is_dir() and not (out/"failure.json").exists():
            save(out/"failure.json", {"status": "FAILED_OR_NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET",
                "error_type": type(exc).__name__, "error": str(exc), "phase": phase,
                "progress": progress, "deadline": deadline.status(), "provisional_summary_is_not_a_gate": (out/"summary.json").exists()})
        print(json.dumps({"error_type": type(exc).__name__, "error": str(exc)}), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
