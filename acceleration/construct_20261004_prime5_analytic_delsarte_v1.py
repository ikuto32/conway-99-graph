"""Exact rational analytic q5 Delsarte candidate; no numerical backend."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/construct_20261004_prime5_analytic_delsarte_v1.py"
SPEC = "acceleration/construct_20261004_prime5_analytic_delsarte_v1_spec.md"
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

def kraw(n, j, i):
    need(all(type(v) is int for v in (n, j, i)) and 0 <= j <= n <= 99 and 0 <= i <= n, "PARAMETERS")
    return sum((-1)**z * 4**(j-z) * math.comb(i, z) * math.comb(n-i, j-z)
               for z in range(max(0, j-(n-i)), min(i, j)+1))

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

def dual(n, distance, texts, tick=lambda: None):
    need(type(n) is int and 1 <= n <= 99 and type(distance) is int
         and 1 <= distance <= n and type(texts) is list and 1 <= len(texts) <= min(32, n), "PARAMETERS")
    ys = [canon(x) for x in texts]
    need(all(x >= 0 for x in ys), "MULTIPLIER_SIGN")
    values = []
    for i in [0, *range(distance, n+1)]:
        tick()
        value = 1+sum(y*kraw(n, j, i) for j, y in enumerate(ys, 1))
        need(i == 0 or value <= 0, "POLYNOMIAL_SIGN")
        values.append({"weight": i, "value": str(value)})
    bound = Fraction(values[0]["value"])
    need(bound >= 1, "ZERO_CODE_BOUND")
    dimension, power = 0, 1
    while power*5 <= bound:
        tick()
        dimension, power = dimension+1, power*5
    return {"schema": "EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1", "q": 5, "n": n,
            "minimum_distance": distance, "degree": len(texts), "dual_lower_counts": {},
            "multipliers": texts, "polynomial_values": values, "code_size_upper": str(bound),
            "integer_dimension_upper": dimension, "dimension_lower_power": power,
            "dimension_next_power": power*5, "nonzero_code_forced": False,
            "is_optimality_certificate": False, "target_resolution": "NONE"}

def calibration(out, tick):
    actions = [
        ("product_n2", "PASS", {"coefficients": [8, 3, 2]}, lambda: product_fixture([8, 3, 2])),
        ("full_space_n2", "PASS", {"n": 2, "distance": 1, "multipliers": ["1", "1"]},
         lambda: dual(2, 1, ["1", "1"], tick)),
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
            need(result["code_size_upper"] == "25" and result["integer_dimension_upper"] == 2
                 and result["polynomial_values"] == [
                     {"weight": 0, "value": "25"}, {"weight": 1, "value": "0"}, {"weight": 2, "value": "0"}],
                 "FULLSPACE_KNOWN_VALUES")
        tick()
    save(out / "controls.json", rows)
    return {"status": "PRIME5_ANALYTIC_DELSARTE_V1_AUTHOR_CONTROLS_PASS",
            "positive_controls": 2, "negative_controls": 2, "control_count": 4,
            "target_polynomial_constructed": False, "target_certificate": None}

def science(out, tick):
    n, t, s = 99, 10, Fraction(122)
    p = [Fraction(1)]
    for k in range(t):
        tick()
        previous = p[k-1] if k else Fraction(0)
        value = ((s-3*k)*p[k]-k*previous)/(4*(n-k))
        need(value > 0, "RECURRENCE_SIGN")
        p.append(value)
        save(out / ("recurrence_checkpoint_"+str(k)+".json"),
             {"completed_recurrence": k+1, "p": [str(x) for x in p]})
    g = [Fraction(0)]*(t+2)
    for k in range(t+2):
        tick()
        g[k] = ((k*p[k-1] if 0 <= k-1 <= t else 0)
                + ((3*k-s)*p[k] if k <= t else 0)
                + (4*(n-k)*p[k+1] if k+1 <= t else 0))
    need(all(x == 0 for x in g[:t]) and g[t] > 0 and g[t+1] == 11*p[t], "TRUNCATED_PRODUCT")
    coeff = [Fraction(0)]*(2*t+2)
    for h in range(len(coeff)):
        tick()
        coeff[h] = sum(g[a]*p[b]*product_coefficient(n, a, b, h)
                       for a in (t, t+1) for b in range(t+1))
        need(coeff[h] >= 0, "EXPANSION_SIGN")
    constant = g[t]*p[t]*4**t*math.comb(n, t)
    need(coeff[0] == constant and constant > 0 and coeff[-1] > 0, "CONSTANT_COEFFICIENT")
    texts = [str(coeff[j]/constant) if j < len(coeff) else "0" for j in range(1, 33)]
    certificate = dual(99, 55, texts, tick)
    for row in certificate["polynomial_values"]:
        tick()
        i = row["weight"]
        pvalue = sum(p[j]*kraw(n, j, i) for j in range(t+1))
        need(Fraction(row["value"]) == (kraw(n, 1, i)-s)*pvalue*pvalue/constant,
             "FACTORIZATION_IDENTITY")
    save(out / "construction.json", {"q": 5, "n": 99, "minimum_distance": 55, "s": str(s), "t": t,
         "p_coefficients": [str(x) for x in p], "g_coefficients": [str(x) for x in g],
         "f_coefficients": [str(x) for x in coeff], "constant_coefficient": str(constant),
         "product_identity": "[X^aY^b](1+4XY)^(99-h)(X+Y+3XY)^h"})
    save(out / "certificate.json", certificate)
    save(out / "polynomial_values.json", certificate["polynomial_values"])
    save(out / "construction_checkpoint.json", {"phase": "exact_candidate_complete",
         "recurrence_steps": 10, "f_coefficients": 22, "dual_multipliers": 32,
         "checked_tail_weights": 45, "LP_calls": 0})
    return {"status": "CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V1_COMPLETE",
            "outcome": {"code_size_upper": certificate["code_size_upper"],
                "integer_dimension_upper": certificate["integer_dimension_upper"],
                "stronger_than_historical27": certificate["integer_dimension_upper"] < 27},
            "target_polynomial_constructed": True, "separate_exact_checker_required": True}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "science"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="One exact analytic polynomial construction or four tiny controls, including all rational work and output seals.")
    out, inputs, phase = Path(args.out), {}, "admission"
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
        result = calibration(out, tick) if args.mode == "calibrate" else science(out, tick)
        tick()
        outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(out.iterdir()) if path.is_file()}
        tick()
        summary = {"schema": "PRIME5_ANALYTIC_DELSARTE_RUN_V1", "implementation_version": 1,
             "mode": args.mode, "timestamp": datetime.now(timezone.utc).isoformat(),
             "producer": "/root/structural", "source": {"path": SELF, "sha256": args.self_sha256},
             "specification": {"path": SPEC, "sha256": args.spec_sha256}, **result,
             "inputs_sha256": inputs, "outputs_sha256": outputs,
             "output_payload_count": len(outputs), "physical_file_count": len(outputs)+1,
             "deadline": deadline.status(), "LP_calls": 0, "target_resolution": "NONE",
             "target_graph_read": False, "nonzero_code_forced": False,
             "support_assumption_authenticated_inside_worker": False,
             "limitations": ["Formal q5 length99/minimum-distance55 dual candidate.",
                  "Target applicability uses the separately accepted support55 theorem.",
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
                "deadline": deadline.status(), "provisional_summary_is_not_a_gate": (out/"summary.json").exists()})
        print(json.dumps({"error_type": type(exc).__name__, "error": str(exc)}), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
