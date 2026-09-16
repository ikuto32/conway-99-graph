"""Prepare and independently audit matrix-free CUDA Chambolle--Pock controls.

Long references are immutable saved CPU vectors. Short references use direct
Python row sums and transpose scatter, with no CP producer or solver import.
The number117 is an exact squared-norm upper bound, not a spectral norm.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

from audit_certificate import require
from audit_phase1 import graph_rows, compare_rows

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "acceleration/results"
LONG = [500, 2000, 10000]
SHORT = [1, 2, 10]
VECTOR_TOLERANCE = 1e-8
SCALAR_TOLERANCE = 1e-7


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def resolve(name):
    path = Path(str(name).replace("\\", "/"))
    return path if path.is_absolute() else ROOT / path


def key(path):
    path = resolve(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def vector(value, size, lower, name):
    require(type(value) is list and len(value) == size and
            all(type(v) in (int, float) and isfinite(v) for v in value), "Malformed/nonfinite " + name)
    lows = lower if type(lower) is list else [lower] * size
    require(all(lo <= v <= 1 for lo, v in zip(lows, value)), "Vector outside exact box: " + name)
    return value


def structure(candidate):
    edges, rows, omitted = graph_rows(candidate)
    require(len(edges) == 1680 and len(rows) == 4326 and len(omitted) == 336, "Wrong semantic dimensions")
    require(all(row["equality"] == (i < 840) and len(row["terms"]) == len(set(row["terms"]))
                for i, row in enumerate(rows)), "Invalid semantic row order/duplicate term")
    quota = Counter(j for row in rows[:840] for j in row["terms"])
    cap = Counter(j for row in rows[840:] for j in row["terms"])
    require(all(quota[j] == 4 and cap[j] == 9 for j in range(1680)), "Wrong exact column incidences")
    sums = [len(row["terms"]) for row in rows]
    require(all(v == 8 for v in sums[:840]) and max(sums[840:]) == 9 and sum(sums) == 21840, "Wrong exact row norms")
    require(Fraction(9, 100) ** 2 * 117 == Fraction(9477, 10000) < 1, "Unsafe fixed step sizes")
    report = dict(rows=4326, columns=1680, nonzeros=21840, omitted_own_label_rows=336,
                  row_absolute_sum_histogram={str(k): v for k, v in Counter(sums).items()}, all_column_absolute_sums=13,
                  quota_column_incidence=4, cap_column_incidence=9,
                  operator_squared_norm_upper_bound=117, exact_step_product_times_bound="9477/10000")
    return edges, rows, report


def bounds(rows, x, y):
    vector(x, 1680, 0, "X")
    vector(y, 4326, [-1] * 840 + [0] * 3486, "Y")
    residual = [sum(x[j] for j in row["terms"]) - row["target"] for row in rows]
    primal = sum(abs(r) if row["equality"] else max(0, r) for row, r in zip(rows, residual))
    co = [0.0] * 1680
    for row, weight in zip(rows, y):
        for j in row["terms"]:
            co[j] += weight
    dual = -sum(row["target"] * weight for row, weight in zip(rows, y)) + sum(min(0, c) for c in co)
    require(isfinite(primal) and isfinite(dual) and dual <= primal + SCALAR_TOLERANCE, "Invalid independent weak duality")
    return dict(primal_upper=primal, dual_lower=dual)


def short_replay(rows, initial_x, initial_y, checkpoints):
    x, y = list(initial_x), list(initial_y)
    xbar, xavg, yavg = list(x), [0.0] * 1680, [0.0] * 4326
    result = []
    for step in range(1, max(checkpoints) + 1):
        y = [min(1, max(-1 if i < 840 else 0,
                       y[i] + .09 * (sum(xbar[j] for j in row["terms"]) - row["target"])))
             for i, row in enumerate(rows)]
        co = [0.0] * 1680
        for row, weight in zip(rows, y):
            for j in row["terms"]:
                co[j] += weight
        new = [min(1, max(0, old - .09 * c)) for old, c in zip(x, co)]
        xbar = [2 * a - b for a, b in zip(new, x)]
        x = new
        xavg = [a + (v - a) / step for a, v in zip(xavg, x)]
        yavg = [a + (v - a) / step for a, v in zip(yavg, y)]
        if step in checkpoints:
            result.append(dict(iterations=step, x_last=list(x), y_last=list(y),
                               x_average=list(xavg), y_average=list(yavg)))
    return result


def prepare(args):
    require(not args.directory.exists(), "Preserve previous controls")
    summary = json.loads(args.cpu_summary.read_bytes())
    require(summary["status"] == "INDEPENDENT_FULL99_CHAMBOLLE_POCK_CPU_QUALITY_CONTROL_PASS" and
            summary["checkpoints"] == LONG and summary["control_count"] == 5 and
            (summary["tau"], summary["sigma"], summary["theta"]) == (.09, .09, 1), "Unexpected saved CPU controls")
    hashes = {key(p): digest(p) for p in (args.cpu_summary, args.warm_phase1, Path(__file__),
                ROOT / "acceleration/audit_phase1.py", ROOT / "acceleration/audit_certificate.py")}
    for mapping in (summary["inputs_sha256"], summary["outputs_sha256"]):
        for name, expected in mapping.items():
            require(digest(resolve(name)) == expected, "Saved CPU dependency changed: " + name)
            hashes[key(name)] = expected
    warm = json.loads(args.warm_phase1.read_bytes())
    warm_path = resolve(warm["candidate_path"])
    require(digest(warm_path) == warm["candidate_sha256"], "Warm base candidate changed")
    hashes[key(warm_path)] = digest(warm_path)
    warm_candidate = json.loads(warm_path.read_bytes())
    edges, warm_rows, _ = structure(warm_candidate)
    require(warm["edge_variables"] == list(map(list, edges)), "Warm X column order differs")
    compare_rows(warm["constraint_groups"], warm_rows)
    initial_x = vector(warm["numeric_edge_values"], 1680, 0, "initial X")
    require(len(warm["constraint_groups"]) == len(warm["phase1_multipliers"]), "Warm dual length mismatch")
    require(all(type(v) in (int, float) and isfinite(v) for v in warm["phase1_multipliers"]), "Nonfinite warm dual")
    mapped = {(row["kind"], tuple(row["coordinate"])): y
              for row, y in zip(warm["constraint_groups"], warm["phase1_multipliers"])}
    initial_y = [min(1, max(-1 if row["equality"] else 0,
                           mapped.get((row["kind"], tuple(row["coordinate"])), 0))) for row in warm_rows]
    vector(initial_y, 4326, [-1] * 840 + [0] * 3486, "initial Y")
    controls, candidates = [], []
    for record in summary["controls"]:
        path = resolve(record["candidate_path"])
        require(digest(path) == record["candidate_sha256"], "Control candidate changed")
        candidate = json.loads(path.read_bytes())
        other_edges, rows, geometry = structure(candidate)
        require(other_edges == edges and [(r["kind"], r["coordinate"]) for r in rows] ==
                [(r["kind"], r["coordinate"]) for r in warm_rows], "Semantic X/Y order differs across K")
        controls.append(dict(shape=record["shape"], candidate_path=key(path), candidate_sha256=digest(path),
                             geometry=geometry, exact_reference_interval=record["exact_reference_interval"],
                             saved_runs=record["runs"]))
        candidates.append(candidate["overlap_edges_outer_zero_based"])
    require([r["shape"] for r in controls] == ["baseline", "2+2", "5", "6", "2+4"], "Unexpected control order")
    args.directory.mkdir(parents=True)
    inputs = []
    for initialization, y in (("zero_dual", [0.0] * 4326), ("current_dual", initial_y)):
        for length, checkpoints in (("long", LONG), ("short", SHORT)):
            stem = f"{length}_{initialization}"
            path = args.directory / (stem + "_input.txt")
            with path.open("x", encoding="ascii", newline="\n") as stream:
                stream.write(f"C99CP1 5 {len(checkpoints)}\n")
                stream.write(" ".join(map(str, checkpoints)) + "\n")
                stream.write(" ".join(format(v, ".17g") for v in initial_x) + "\n")
                stream.write(" ".join(format(v, ".17g") for v in y) + "\n")
                for candidate in candidates:
                    stream.write(" ".join(str(v) for edge in candidate for v in edge) + "\n")
            inputs.append(dict(initialization=initialization, length=length, checkpoints=checkpoints,
                               input_path=key(path), input_sha256=digest(path),
                               output_path=key(args.directory / (stem + "_gpu.json"))))
    manifest = dict(status="INDEPENDENT_CP_GPU_CONTROLS_PREPARED", inputs_sha256=hashes, controls=controls, inputs=inputs,
                    initial_x=initial_x, current_initial_y=initial_y, tau=.09, sigma=.09, theta=1,
                    vector_absolute_tolerance=VECTOR_TOLERANCE, scalar_absolute_tolerance=SCALAR_TOLERANCE,
                    scope="Saved CPU vectors are numerical references only. Long controls use exactly500/2000/10000 requested checkpoints; separate1/2/10 controls use direct independent row-sum replay.")
    save(args.directory / "manifest.json", manifest)
    print(json.dumps(dict(status=manifest["status"], directory=key(args.directory), inputs=inputs)))


def audit(args):
    started = time.perf_counter()
    out = args.directory / "audit.json"
    require(not out.exists(), "Preserve previous GPU control audit")
    manifest_path = args.directory / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    require(manifest["status"] == "INDEPENDENT_CP_GPU_CONTROLS_PREPARED", "Wrong control manifest")
    hashes = {key(manifest_path): digest(manifest_path)}
    for name, expected in manifest["inputs_sha256"].items():
        require(digest(resolve(name)) == expected, "Prepared dependency changed: " + name)
        hashes[key(name)] = expected
    for path in (args.gpu_source, args.gpu_binary, Path(__file__)):
        hashes[key(path)] = digest(path)
    controls = manifest["controls"]
    vector_count, scalar_count, max_vector_error, max_scalar_error = 0, 0, 0.0, 0.0
    reports = []
    for job in manifest["inputs"]:
        input_path, output_path = resolve(job["input_path"]), resolve(job["output_path"])
        require(digest(input_path) == job["input_sha256"], "GPU input changed")
        hashes[key(input_path)], hashes[key(output_path)] = digest(input_path), digest(output_path)
        tokens = input_path.read_text(encoding="ascii").split()
        checkpoints = job["checkpoints"]
        require(tokens[:3] == ["C99CP1", "5", str(len(checkpoints))] and
                list(map(int, tokens[3:3 + len(checkpoints)])) == checkpoints, "GPU input header differs")
        offset = 3 + len(checkpoints)
        initial_x = list(map(float, tokens[offset:offset + 1680]))
        initial_y = list(map(float, tokens[offset + 1680:offset + 1680 + 4326]))
        expected_y = [0.0] * 4326 if job["initialization"] == "zero_dual" else manifest["current_initial_y"]
        require(initial_x == manifest["initial_x"] and initial_y == expected_y and
                len(tokens) == offset + 1680 + 4326 + 5 * 336, "GPU starts/input length differs")
        payload = json.loads(output_path.read_bytes())
        require(payload["status"] == "NUMERICAL_CHAMBOLLE_POCK_PHASE1_HEURISTIC" and
                payload["candidate_count"] == 5 and payload["checkpoints"] == checkpoints and
                len(payload["results"]) == 5, "GPU output dimensions/status differ")
        require((payload["tau"], payload["sigma"], payload["theta"]) == (.09, .09, 1), "GPU algorithm parameters differ")
        for number, (control, result) in enumerate(zip(controls, payload["results"])):
            candidate_path = resolve(control["candidate_path"])
            require(digest(candidate_path) == control["candidate_sha256"], "Control candidate changed")
            candidate = json.loads(candidate_path.read_bytes())
            _, rows, geometry = structure(candidate)
            require(geometry == control["geometry"], "Prepared operator geometry differs")
            start = offset + 1680 + 4326 + number * 336
            flat = list(map(int, tokens[start:start + 336]))
            require([flat[i:i + 2] for i in range(0, 336, 2)] == candidate["overlap_edges_outer_zero_based"], "GPU K input differs")
            require(result["candidate_index"] == number and len(result["checkpoints"]) == len(checkpoints), "GPU candidate/checkpoint order differs")
            saved_run = next(r for r in control["saved_runs"] if r["initialization"] == job["initialization"])
            if job["length"] == "long":
                path = resolve(saved_run["saved_iterates_path"])
                require(digest(path) == saved_run["saved_iterates_sha256"], "Saved CPU vectors changed")
                hashes[key(path)] = digest(path)
                cpu = json.loads(path.read_bytes())
                require(cpu["shape"] == control["shape"] and cpu["initialization"] == job["initialization"], "Wrong saved CPU control")
                references = cpu["checkpoints"]
            else:
                references = short_replay(rows, initial_x, initial_y, checkpoints)
            expected_initial = bounds(rows, initial_x, initial_y)
            best_upper, best_lower = expected_initial["primal_upper"], expected_initial["dual_lower"]

            def check_scalar(actual, expected):
                nonlocal scalar_count, max_scalar_error
                require(type(actual) in (int, float) and isfinite(actual), "Nonfinite scalar output")
                error = abs(actual - expected)
                require(error <= SCALAR_TOLERANCE, "GPU/independent scalar differs")
                scalar_count += 1
                max_scalar_error = max(max_scalar_error, error)

            for field in ("primal_upper", "dual_lower"):
                check_scalar(result["initial"][field], expected_initial[field])
            check_scalar(result["initial"]["primal_upper"], saved_run["initial_bounds"]["primal_upper_numeric"])
            check_scalar(result["initial"]["dual_lower"], saved_run["initial_bounds"]["dual_lower_numeric"])
            checkpoint_reports = []
            for step, actual, reference in zip(checkpoints, result["checkpoints"], references):
                require(actual["iterations"] == reference["iterations"] == step, "Wrong checkpoint step")
                errors = {}
                for field in ("x_last", "y_last", "x_average", "y_average"):
                    is_x = field.startswith("x")
                    gpu_vector = vector(actual[field], 1680 if is_x else 4326, 0 if is_x else [-1] * 840 + [0] * 3486, field)
                    reference_vector = vector(reference[field], len(gpu_vector), 0 if is_x else [-1] * 840 + [0] * 3486, "CPU " + field)
                    error = max(abs(a - b) for a, b in zip(gpu_vector, reference_vector))
                    require(error <= VECTOR_TOLERANCE, "GPU/CPU vector differs: " + field)
                    errors[field] = error
                    vector_count += len(gpu_vector)
                    max_vector_error = max(max_vector_error, error)
                last = bounds(rows, actual["x_last"], actual["y_last"])
                average = bounds(rows, actual["x_average"], actual["y_average"])
                lower_ref = control["exact_reference_interval"]["lower"]["approximate"]
                upper_ref = control["exact_reference_interval"]["upper"]["approximate"]
                for name, independent in (("last", last), ("average", average)):
                    require(independent["primal_upper"] + SCALAR_TOLERANCE >= lower_ref and
                            independent["dual_lower"] - SCALAR_TOLERANCE <= upper_ref, "CP value contradicts exact LP reference interval")
                    for field in ("primal_upper", "dual_lower"):
                        check_scalar(actual[name][field], independent[field])
                best_upper = min(best_upper, last["primal_upper"], average["primal_upper"])
                best_lower = max(best_lower, last["dual_lower"], average["dual_lower"])
                check_scalar(actual["best_upper"], best_upper)
                check_scalar(actual["best_lower"], best_lower)
                if job["length"] == "long":
                    cpu_point = next(r for r in saved_run["checkpoints"] if r["iterations"] == step)
                    for gpu_name, cpu_name in (("last", "last"), ("average", "ergodic_average")):
                        for field, cpu_field in (("primal_upper", "primal_upper_numeric"), ("dual_lower", "dual_lower_numeric")):
                            check_scalar(actual[gpu_name][field], cpu_point[cpu_name][cpu_field])
                    check_scalar(actual["best_upper"], cpu_point["best_upper_over_initial_and_checked_points"])
                    check_scalar(actual["best_lower"], cpu_point["best_lower_over_initial_and_checked_points"])
                checkpoint_reports.append(dict(iterations=step, vector_maximum_absolute_errors=errors,
                                               independent_last=last, independent_average=average,
                                               best_upper=best_upper, best_lower=best_lower))
            reports.append(dict(shape=control["shape"], initialization=job["initialization"], length=job["length"],
                                output_path=job["output_path"], candidate_index=number, independent_geometry=geometry,
                                initial=expected_initial, checkpoints=checkpoint_reports))
    require(all(digest(resolve(name)) == expected for name, expected in hashes.items()), "Bound source/input/output changed during audit")
    report = dict(status="INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS", inputs_sha256=hashes,
                  cases_checked=len(reports), distinct_candidates=5, starts_per_candidate=2,
                  long_checkpoints=LONG, short_checkpoints=SHORT, numeric_vector_entries_compared=vector_count,
                  scalar_comparisons=scalar_count, max_vector_absolute_error=max_vector_error,
                  max_scalar_absolute_error=max_scalar_error, vector_absolute_tolerance=VECTOR_TOLERANCE,
                  scalar_absolute_tolerance=SCALAR_TOLERANCE, exact_squared_norm_upper_bound=117,
                  exact_step_product_times_bound="9477/10000", all_x_y_vectors_finite_and_exact_box_feasible=True,
                  reports=reports, old_cpu_producer_or_gpu_implementation_imported=False,
                  solver_reruns=0, exact_certificate_or_exclusion_claim=False, elapsed_seconds=time.perf_counter() - started,
                  scope="Numerical GPU quality control on five fixed graphs and two initial dual states. All saved CPU vectors compared at500/2000/10000; direct full99 row replay at1/2/10. Primal and dual scalars independently recomputed. Floating results remain heuristics, not exact proofs.117 is an induced-norm bound, not the actual squared spectral norm.")
    save(out, report)
    print(json.dumps({k: v for k, v in report.items() if k not in ("inputs_sha256", "reports")}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "audit"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--cpu-summary", type=Path, default=RESULTS / "20260916_phase1_chambolle_pock_cpu/summary.json")
    parser.add_argument("--warm-phase1", type=Path, default=RESULTS / "20260916_two_trade_pilot/best_phase1.json")
    parser.add_argument("--gpu-source", type=Path, default=ROOT / "acceleration/overlap_cp_gpu.cu")
    parser.add_argument("--gpu-binary", type=Path, default=ROOT / "acceleration/build/overlap_cp_gpu.exe")
    args = parser.parse_args()
    prepare(args) if args.mode == "prepare" else audit(args)


if __name__ == "__main__":
    main()
