"""Independent reusable version2 CUDA-CP ranking and fixed-K LP audit.

No search, CP, GPU or optimization producer is imported. Complete-family
geometry is reused by exact byte bindings; only ranking values are numerical.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.sparse import csr_matrix

from audit_certificate import require
from audit_phase1 import graph_rows, compare_rows
from audit_phase1_kkt import inspect_artifact, rational

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "acceleration/results"


def resolve(name):
    path = Path(str(name).replace("\\", "/"))
    return path if path.is_absolute() else ROOT / path


def signature(edges):
    require(type(edges) is list and len(edges) == 168 and all(
        type(e) is list and len(e) == 2 and all(type(v) is int for v in e)
        and 0 <= e[0] < e[1] < 84 for e in edges), "Malformed overlap signature")
    require(len({tuple(e) for e in edges}) == 168, "Repeated overlap edge")
    return bytes(v for edge in sorted(map(tuple, edges)) for v in edge)


def edge_hash(sig):
    return sha256(json.dumps([list(sig[i:i + 2]) for i in range(0, len(sig), 2)], separators=(",", ":")).encode("ascii")).hexdigest()


def partition(move):
    return tuple(sorted(len(c) // 2 for c in move["alternating_cycles"]))


def selection(eligible, scores, moves, count, diversity):
    rank = lambda i: (scores[i], i)
    coordinates, shapes, strata = defaultdict(list), defaultdict(list), defaultdict(list)
    for i in eligible:
        coordinate = moves[i]["root_group"], moves[i]["matching_class"]
        shape = partition(moves[i])
        coordinates[coordinate].append(i)
        shapes[shape].append(i)
        strata[coordinate, shape].append(i)
    selected, roles = [], {}

    def add(i, role):
        if i not in roles:
            selected.append(i)
            roles[i] = []
        roles[i].append(role)

    for group in sorted(coordinates):
        add(min(coordinates[group], key=rank), "coordinate_minimum")
    for shape in sorted(shapes):
        add(min(shapes[shape], key=rank), "cycle_partition_minimum")
    represented = {((moves[i]["root_group"], moves[i]["matching_class"]), partition(moves[i])) for i in selected}
    minima = [min(indices, key=rank) for stratum, indices in strata.items() if stratum not in represented]
    for i in sorted(minima, key=rank):
        if len(selected) >= diversity:
            break
        add(i, "coordinate_partition_minimum")
    for i in sorted(eligible, key=rank):
        if len(selected) >= count:
            break
        if i not in roles:
            add(i, "global_score_fill")
    require(len(selected) == count, "Insufficient stage selection")
    return [dict(proposal_index=i, selection_roles=roles[i], score=scores[i], move=moves[i]) for i in selected]


def scalar(value, name):
    require(type(value) in (int, float) and isfinite(value), "Nonfinite scalar: " + name)
    return value


def finite_box(values, size, dual=False):
    require(type(values) is list and len(values) == size and all(type(v) in (int, float) and isfinite(v) for v in values), "Malformed vector")
    require(all((-1 if dual and i < 840 else 0) <= v <= 1 for i, v in enumerate(values)), "Vector outside box")
    return values


def independent_bounds(rows, x, y):
    finite_box(x, 1680)
    finite_box(y, 4326, True)
    residual = [sum(x[j] for j in row["terms"]) - row["target"] for row in rows]
    primal = sum(abs(r) if row["equality"] else max(0, r) for row, r in zip(rows, residual))
    co = [0.0] * 1680
    for row, weight in zip(rows, y):
        for j in row["terms"]:
            co[j] += weight
    dual = -sum(row["target"] * weight for row, weight in zip(rows, y)) + sum(min(0, c) for c in co)
    require(dual <= primal + 1e-7, "Numerical weak duality failed")
    return dict(primal_upper=primal, dual_lower=dual)


def cpu_replay(rows, x0, y0, steps):
    row_ids, columns = [], []
    for i, row in enumerate(rows):
        require(len(row["terms"]) == len(set(row["terms"])), "Duplicate row term")
        row_ids.extend([i] * len(row["terms"]))
        columns.extend(row["terms"])
    matrix = csr_matrix((np.ones(len(columns)), (row_ids, columns)), shape=(4326, 1680))
    transpose = matrix.transpose().tocsr()
    require(matrix.nnz == 21840 and np.all(np.asarray(matrix.sum(axis=0)).ravel() == 13) and
            np.max(np.asarray(matrix.sum(axis=1)).ravel()) <= 9, "Operator norm/incidence check failed")
    rhs = np.asarray([row["target"] for row in rows], dtype=np.float64)
    low = np.r_[np.full(840, -1.0), np.zeros(3486)]
    x, y = np.asarray(x0, dtype=np.float64), np.asarray(y0, dtype=np.float64)
    extrapolated, xavg, yavg = x.copy(), np.zeros(1680), np.zeros(4326)
    for iteration in range(1, steps + 1):
        y = np.clip(y + .09 * (matrix @ extrapolated - rhs), low, 1.0)
        next_x = np.clip(x - .09 * (transpose @ y), 0.0, 1.0)
        extrapolated = 2 * next_x - x
        x = next_x
        xavg += (x - xavg) / iteration
        yavg += (y - yavg) / iteration
    return dict(x_last=x.tolist(), y_last=y.tolist(), x_average=xavg.tolist(), y_average=yavg.tolist())


def rational_value(record):
    return Fraction(int(record["numerator"]), int(record["denominator"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--native", type=Path, default=None)
    parser.add_argument("--family-audit", type=Path, default=None)
    parser.add_argument("--initial", type=Path, default=None)
    parser.add_argument("--initial-phase1", type=Path, default=None)
    parser.add_argument("--gpu-audit", type=Path, default=None)
    parser.add_argument("--gpu", type=Path, default=None)
    parser.add_argument("--gpu-source", type=Path, default=None)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve prior search audit")
    started = time.perf_counter()
    hashes = {}

    def bind(path, expected=None):
        path = resolve(path).resolve()
        name = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        if name not in hashes:
            hashes[name] = sha256(path.read_bytes()).hexdigest()
        require(expected is None or hashes[name] == expected, "Hash mismatch: " + name)
        return hashes[name]

    def load(path):
        bind(path)
        return json.loads(resolve(path).read_bytes())

    summary, manifest = load(args.run / "summary.json"), load(args.run / "manifest.json")
    require(summary["status"] == "BOUNDED_CP_MATCHING_SEARCH_FINISHED" and manifest["status"] == "CP_MATCHING_SEARCH_MANIFEST", "Search unfinished")
    require(summary["producer_version"] == manifest["producer_version"] == 2, "Expected version2 driver")
    require(summary["paths"] == manifest["paths"], "Manifest/summary paths differ")
    require(summary["inputs_sha256"] == manifest["inputs_sha256"], "Manifest/summary inputs differ")
    for field in ("native", "family_audit", "initial", "initial_phase1", "gpu_audit", "gpu", "gpu_source"):
        declared = resolve(manifest["paths"][field])
        supplied = getattr(args, field)
        require(supplied is None or supplied.resolve() == declared.resolve(), "Supplied path differs from version2 manifest: " + field)
        setattr(args, field, declared)
    for mapping in (manifest["inputs_sha256"], summary["outputs_sha256"]):
        for path, expected in mapping.items():
            bind(path, expected)
    declared_outputs = {resolve(p).resolve(): expected for p, expected in summary["outputs_sha256"].items()}
    require(len(declared_outputs) == len(summary["outputs_sha256"]), "Duplicate normalized output path")
    def output_load(path):
        path = resolve(path)
        require(declared_outputs.get(path.resolve()) == bind(path), "Required output is not bound: " + str(path))
        return load(path)
    require(declared_outputs.get((args.run / "manifest.json").resolve()) == bind(args.run / "manifest.json"), "Manifest output not bound")
    for path in (args.native, args.family_audit, args.initial, args.initial_phase1, args.gpu_audit, args.gpu, args.gpu_source,
                 ROOT / "acceleration/search_cp_matching_v2.py"):
        name = resolve(path).resolve().relative_to(ROOT).as_posix()
        require(manifest["inputs_sha256"].get(name) == bind(path), "Unbound supplied input")
    family = load(args.family_audit)
    require(family["status"] == "INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS" and family["selector"] == "all", "Wrong family proof")
    family_bindings = {resolve(p).resolve(): sha for p, sha in family["inputs_sha256"].items()}
    for path, expected in family["inputs_sha256"].items():
        bind(path, expected)
    # Version2 family association may reuse byte-identical payload paths and
    # candidate wrappers with exactly the same labeled graph. Checked below.
    association = manifest["family_association"]
    require(summary["family_association"] == association, "Family association summary differs")
    bound_native = resolve(association["bound_native_path"])
    bound_base = resolve(association["bound_base_path"])
    require(family_bindings.get(bound_native.resolve()) == bind(bound_native) == bind(args.native), "Family native bytes are not identically bound")
    require(family_bindings.get(bound_base.resolve()) == bind(bound_base), "Family base file is not bound")
    require(signature(load(bound_base)["overlap_edges_outer_zero_based"]) ==
            signature(load(args.initial)["overlap_edges_outer_zero_based"]), "Family base labeled graph differs")
    def relative(path):
        return resolve(path).resolve().relative_to(ROOT).as_posix()
    expected_association = dict(native_path=relative(args.native), native_sha256=bind(args.native),
        bound_native_path=relative(bound_native), bound_native_sha256=bind(bound_native),
        native_method="EXACT_BOUND_FILE" if args.native.resolve() == bound_native.resolve() else "IDENTICAL_BOUND_BYTES",
        initial_path=relative(args.initial), initial_sha256=bind(args.initial),
        bound_base_path=relative(bound_base), bound_base_sha256=bind(bound_base),
        base_method="EXACT_BOUND_FILE" if args.initial.resolve() == bound_base.resolve() else "EXACT_LABELED_GRAPH_IDENTITY",
        overlap_edges_sha256=edge_hash(signature(load(args.initial)["overlap_edges_outer_zero_based"])))
    require(association == expected_association, "Declared family association differs from checked identities")
    gpu_audit_path = args.gpu_audit
    gpu_audit = load(gpu_audit_path)
    require(gpu_audit["status"] == "INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS", "GPU numeric controls missing")
    for path, expected in gpu_audit["inputs_sha256"].items():
        bind(path, expected)
    gpu_bindings = {resolve(p).resolve(): expected for p, expected in gpu_audit["inputs_sha256"].items()}
    require(all(gpu_bindings.get(p.resolve()) == bind(p) for p in (args.gpu, args.gpu_source)),
            "GPU source/binary are not the independently controlled implementation")
    require(manifest["inputs_sha256"].get(gpu_audit_path.relative_to(ROOT).as_posix()) == bind(gpu_audit_path), "Different GPU quality report")
    initial, warm = load(args.initial), load(args.initial_phase1)
    initial_sig = signature(initial["overlap_edges_outer_zero_based"])
    warm_candidate = resolve(warm["candidate_path"])
    bind(warm_candidate, warm["candidate_sha256"])
    require(signature(load(warm_candidate)["overlap_edges_outer_zero_based"]) == initial_sig, "Warm K differs")
    edges, base_rows, omitted = graph_rows(initial)
    require(len(base_rows) == 4326 and len(omitted) == 336 and warm["edge_variables"] == list(map(list, edges)), "Warm column/row order differs")
    compare_rows(warm["constraint_groups"], base_rows)
    require(len(warm["phase1_multipliers"]) == len(warm["constraint_groups"]) and
            all(type(v) in (int, float) and isfinite(v) for v in warm["phase1_multipliers"]),
            "Warm dual values malformed or nonfinite before clipping")
    mapped = {(row["kind"], tuple(row["coordinate"])): weight for row, weight in zip(warm["constraint_groups"], warm["phase1_multipliers"])}
    require(len(mapped) == len(warm["constraint_groups"]), "Duplicate raw warm semantic dual key")
    expected_y = [min(1, max(-1 if row["equality"] else 0, mapped.get((row["kind"], tuple(row["coordinate"])), 0))) for row in base_rows]
    x0, y0 = finite_box(manifest["initial_x"], 1680), finite_box(manifest["initial_y"], 4326, True)
    require(x0 == warm["numeric_edge_values"] and y0 == expected_y, "Stage restart X/Y differs from semantic warm data")
    baseline_audit = inspect_artifact(warm_candidate, args.initial_phase1)
    require(manifest["baseline_numeric_objective"] == summary["baseline_numeric_objective"] == warm["numeric_objective"], "Baseline objective differs")

    excluded, previous, previous_by_path = set(), [], {}
    def add_previous(path, expected_sha, origin):
        path = resolve(path)
        actual_sha = bind(path, expected_sha)
        sig = signature(load(path)["overlap_edges_outer_zero_based"])
        excluded.add(sig)
        name = relative(path)
        if name not in previous_by_path:
            item = dict(candidate_path=name, candidate_sha256=actual_sha,
                        overlap_edges_sha256=edge_hash(sig), origins=[])
            previous_by_path[name] = item
            previous.append(item)
        previous_by_path[name]["origins"].append(origin)
        return sig
    for directory in ("20260916_whole_matching_pilot", "20260916_matching_hint_shortlist"):
        for path in sorted((RESULTS / directory / "probes").glob("*_candidate.json")):
            add_previous(path, None, dict(kind="DEFAULT_PROBE_DIRECTORY", directory=relative(RESULTS / directory)))
    require(len(previous) == 193, "Default legacy previous-candidate inventory differs")
    seen_summary_paths, previous_reports = set(), []
    require(type(manifest["previous_summary_arguments"]) is list, "Malformed previous-summary arguments")
    for declared_path in manifest["previous_summary_arguments"]:
        path = resolve(declared_path)
        name = relative(path)
        require(declared_path == name, "Previous summary path not normalized")
        if name in seen_summary_paths:
            continue
        seen_summary_paths.add(name)
        prior_summary = load(path)
        require(prior_summary["status"] in ("BOUNDED_CP_MATCHING_SEARCH_FINISHED", "BOUNDED_MATCHING_HINT_SHORTLIST_FINISHED"),
                "Prior summary is not a completed supported study")
        prior_records = prior_summary["records"]
        require(type(prior_records) is list and len(prior_records) == prior_summary["probes"], "Prior summary record count differs")
        prior_outputs = {relative(p): expected for p, expected in prior_summary["outputs_sha256"].items()}
        prior_signatures = set()
        for row in prior_records:
            candidate_path = resolve(row["candidate_path"])
            require(prior_outputs.get(relative(candidate_path)) == row["candidate_sha256"], "Prior summary candidate output is not bound")
            prior_signatures.add(add_previous(candidate_path, row["candidate_sha256"],
                dict(kind="PREVIOUS_SUMMARY", summary_path=name, summary_sha256=bind(path))))
        previous_reports.append(dict(path=name, sha256=bind(path), status=prior_summary["status"],
                                     records_count=len(prior_records), unique_candidate_count=len(prior_signatures)))
    require(previous_reports == manifest["previous_summary_reports"] == summary["previous_summary_reports"],
            "Previous summary report identities/counts differ")
    require(previous == manifest["previous_candidates"], "Previous candidate exclusions or origin roles differ")
    require(all(manifest["inputs_sha256"].get(relative(path)) == bind(path) for path in
                [resolve(row["candidate_path"]) for row in previous] + [resolve(row["path"]) for row in previous_reports]),
            "Previous candidate/summary is missing from input bindings")
    native = load(args.native)
    options = native.pop("overlap_candidates")
    moves, keys = native["moves"], [signature(k) for k in options]
    require(len(keys) == len(moves) == family["legal_count"] == manifest["coarse_candidates"] and
            len(set(keys)) == len(keys), "Wrong audited family size")
    require(native["status"] == "COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION" and
            native["selector"] == "all", "Wrong native family scope")
    del options
    stage_reports = []

    def stage(stem, indices, steps, baseline):
        record, payload = output_load(args.run / (stem + "_stage.json")), output_load(args.run / (stem + "_gpu.json"))
        expected_indices = ([None] if baseline else []) + list(indices)
        require(record["stage"] == stem and record["proposal_indices"] == expected_indices and
                record["candidate_count"] == len(expected_indices) and record["steps"] == steps and
                record["baseline_included"] is baseline, "Stage metadata/order differs")
        input_path, output_path = args.run / (stem + "_input.txt"), args.run / (stem + "_gpu.json")
        require(resolve(record["gpu_input_path"]).resolve() == input_path.resolve() and
                resolve(record["gpu_output_path"]).resolve() == output_path.resolve(), "Stage paths differ")
        bind(input_path, record["gpu_input_sha256"])
        bind(output_path, record["gpu_output_sha256"])
        require(declared_outputs.get(input_path.resolve()) == bind(input_path), "GPU input output binding absent")
        with input_path.open(encoding="ascii") as stream:
            require(stream.readline().split() == ["C99CP1", str(len(expected_indices)), "1"] and
                    stream.readline().split() == [str(steps)], "GPU input header/checkpoint differs")
            require(list(map(float, stream.readline().split())) == x0 and
                    list(map(float, stream.readline().split())) == y0, "GPU stage did not restart common X/Y")
            for i in expected_indices:
                flat = list(map(int, stream.readline().split()))
                require(len(flat) == 336 and bytes(flat) == (initial_sig if i is None else keys[i]), "GPU candidate input/order mismatch")
            require(not stream.read().strip(), "Trailing GPU input")
        require(payload["status"] == "NUMERICAL_CHAMBOLLE_POCK_PHASE1_HEURISTIC" and
                payload["candidate_count"] == len(expected_indices) and payload["checkpoints"] == [steps] and
                (payload["tau"], payload["sigma"], payload["theta"]) == (.09, .09, 1) and
                len(payload["results"]) == len(expected_indices), "GPU output semantics differ")
        scores, outputs = {}, {}
        for n, (i, result) in enumerate(zip(expected_indices, payload["results"])):
            require(result["candidate_index"] == n and len(result["checkpoints"]) == 1, "GPU result order differs")
            point = result["checkpoints"][0]
            require(point["iterations"] == steps, "GPU output checkpoint differs")
            points = [result["initial"], point["last"], point["average"]]
            for values in points:
                upper = scalar(values["primal_upper"], "upper")
                lower = scalar(values["dual_lower"], "lower")
                require(upper >= 0 and lower <= upper + 1e-7, "Invalid numerical CP bounds")
            upper = min(p["primal_upper"] for p in points)
            lower = max(p["dual_lower"] for p in points)
            require(abs(scalar(point["best_upper"], "best upper") - upper) <= 1e-10 and
                    abs(scalar(point["best_lower"], "best lower") - lower) <= 1e-10 and lower <= upper + 1e-7,
                    "Initial/checkpoint best values differ")
            if i is not None:
                scores[i], outputs[i] = upper, result
        require(record["minimum_upper"] == min(scores.values()), "Stage minimum differs")
        stage_reports.append(dict(stage=stem, candidate_count=len(expected_indices), steps=steps,
                                  minimum_upper=record["minimum_upper"], all_scalar_summaries_checked=True,
                                  complete_input_candidate_order_and_warm_X_Y_checked=True))
        return scores, outputs

    coarse_steps, refine_steps, refine_count, lp_count = (manifest[k] for k in ("coarse_steps", "refine_steps", "refine_count", "lp_count"))
    require(all(type(v) is int for v in (coarse_steps, refine_steps, refine_count, lp_count)) and
            0 < coarse_steps < refine_steps <= 1000000 and 32 <= lp_count <= 64 and
            140 <= refine_count <= min(99999, len(keys)) and lp_count <= refine_count, "Invalid finite version2 study size")
    coarse, coarse_rows = stage("coarse", range(len(keys)), coarse_steps, True)
    del coarse_rows
    refine_expected = selection(list(coarse), coarse, moves, refine_count, 140)
    require(output_load(args.run / "refine_selection.json") == refine_expected, "Coarse-to-refine selection/roles differs")
    refined, refined_rows = stage("refined", [r["proposal_index"] for r in refine_expected], refine_steps, True)
    eligible = [i for i in refined if keys[i] not in excluded]
    expected = selection(eligible, refined, moves, lp_count, 32)
    for order, row in enumerate(expected):
        i = row["proposal_index"]
        row.update(selection_order=order, coarse_score=coarse[i], overlap_edges_sha256=edge_hash(keys[i]))
    require(output_load(args.run / "lp_selection.json") == expected, "Refine-to-LP selection/roles differs")
    selected = [r["proposal_index"] for r in expected]
    replay_scores, gpu_vectors = stage("selected_vectors", selected, refine_steps, False)
    require(all(abs(replay_scores[i] - refined[i]) <= 1e-9 for i in selected), "Selected rerun ranking differs")
    require(len(summary["records"]) == summary["probes"] == lp_count and len(list((args.run / "probes").glob("*_candidate.json"))) ==
            len(list((args.run / "probes").glob("*_phase1.json"))) == lp_count, "Wrong LP inventory")
    replay_indices = []
    for shape in ((2, 2), (5,), (6,)):
        matching = [i for i in selected if partition(moves[i]) == shape]
        if matching:
            replay_indices.append(matching[0])
    for i in selected:
        if len(replay_indices) >= 3:
            break
        if i not in replay_indices:
            replay_indices.append(i)
    reports, cpu_reports, max_scalar_error, max_vector_error = [], [], 0.0, 0.0
    for chosen, record in zip(expected, summary["records"]):
        require(all(record.get(k) == v for k, v in chosen.items()), "LP record selection metadata differs")
        i = record["proposal_index"]
        require(keys[i] not in excluded, "Previously probed K selected for LP")
        candidate_path, result_path = resolve(record["candidate_path"]), resolve(record["result_path"])
        stem = f"selection_{record['selection_order']:02d}_index_{i}"
        require(candidate_path.resolve() == (args.run / "probes" / (stem + "_candidate.json")).resolve() and
                result_path.resolve() == (args.run / "probes" / (stem + "_phase1.json")).resolve(), "LP file order differs")
        candidate, result = output_load(candidate_path), output_load(result_path)
        bind(candidate_path, record["candidate_sha256"])
        bind(result_path, record["result_sha256"])
        require(signature(candidate["overlap_edges_outer_zero_based"]) == keys[i] and candidate["selection"] == chosen and
                candidate["native_source_sha256"] == bind(args.native) and resolve(candidate["native_source_path"]).resolve() == args.native.resolve(), "Candidate family association differs")
        require(result["overlap_edges_sha256"] == edge_hash(keys[i]) and resolve(result["candidate_path"]).resolve() == candidate_path.resolve(), "LP candidate differs")
        require(all(result[field] == record[field] for field in ("numeric_objective", "optimal", "status")) and result["optimal"] is True, "Incomplete or mismatched LP")
        for name, expected_sha in result["source_sha256"].items():
            require(Path(name).name == name, "Unexpected producer source path")
            bind(ROOT / "acceleration" / name, expected_sha)
        interval = inspect_artifact(candidate_path, result_path)
        _, rows, omitted = graph_rows(candidate)
        require(len(rows) == 4326 and len(omitted) == 336, "Selected full99 rows differ")
        point = gpu_vectors[i]["checkpoints"][0]
        scalar_values = {}
        initial_values = independent_bounds(rows, x0, y0)
        for label, xname, yname in (("last", "x_last", "y_last"), ("average", "x_average", "y_average")):
            values = independent_bounds(rows, point[xname], point[yname])
            for field, truth in values.items():
                error = abs(point[label][field] - truth)
                require(error <= 1e-7, "Selected full99 CP scalar mismatch")
                max_scalar_error = max(max_scalar_error, error)
                require(abs(point[label][field] - refined_rows[i]["checkpoints"][0][label][field]) <= 1e-9, "Selected/refined checkpoint differs")
            require(values["primal_upper"] + 1e-7 >= interval["exact_dual_lower_bound"]["approximate"] and
                    values["dual_lower"] - 1e-7 <= interval["exact_primal_upper_bound"]["approximate"], "CP numerics contradict exact interval")
            scalar_values[label] = values
        for field, truth in initial_values.items():
            require(abs(gpu_vectors[i]["initial"][field] - truth) <= 1e-7, "Selected initial full99 bounds differ")
        upper = min(v["primal_upper"] for v in [initial_values, *scalar_values.values()])
        lower = max(v["dual_lower"] for v in [initial_values, *scalar_values.values()])
        require(abs(upper - chosen["score"]) <= 1e-7 and abs(lower - point["best_lower"]) <= 1e-7, "Selected independent best CP values differ")
        improvement = rational_value(baseline_audit["exact_dual_lower_bound"]) - rational_value(interval["exact_primal_upper_bound"])
        reports.append(dict(proposal_index=i, candidate_path=record["candidate_path"], result_path=record["result_path"],
                            numeric_objective=record["numeric_objective"], phase1_audit=interval,
                            independent_cp_initial=initial_values, independent_cp_last=scalar_values["last"],
                            independent_cp_average=scalar_values["average"], independent_cp_best_upper=upper,
                            independent_cp_best_lower=lower, exact_strict_improvement=improvement > 0,
                            exact_improvement_margin=rational(improvement)))
        if i in replay_indices:
            cpu = cpu_replay(rows, x0, y0, refine_steps)
            errors = {field: max(abs(a - b) for a, b in zip(values, point[field])) for field, values in cpu.items()}
            require(max(errors.values()) <= 1e-8, "Independent refinement CPU/GPU vectors differ")
            max_vector_error = max(max_vector_error, *errors.values())
            cpu_reports.append(dict(proposal_index=i, cycle_partition=list(partition(moves[i])), steps=refine_steps,
                                    maximum_vector_errors=errors, vector_entries_compared=sum(map(len, cpu.values())),
                                    independent_operator_nonzeros=21840, squared_norm_upper_bound=117))
    numeric_order = sorted(summary["records"], key=lambda row: (row["numeric_objective"], row["proposal_index"]))
    improving = [row for row in numeric_order if row["numeric_objective"] < warm["numeric_objective"]]
    require(summary["best"] == numeric_order[0] and summary["numerically_improving_candidates"] == improving and
            summary["numerical_improvement_count"] == len(improving) and summary["numerically_optimal_count"] == lp_count,
            "Best/improvement counts differ")
    require(summary["coarse_candidate_count"] == len(keys) and summary["refined_candidate_count"] == len(refined) and
            summary["cp_values_used_as_proof"] is False and summary["pair_gates_run"] == 0 and
            summary["full_graph_constructed"] is False and summary["general_nonexistence_proved"] is False, "Summary scope differs")
    for path in (Path(__file__), ROOT / "acceleration/audit_certificate.py", ROOT / "acceleration/audit_phase1.py", ROOT / "acceleration/audit_phase1_kkt.py"):
        bind(path)
    report = dict(status="INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS", audited_producer_version=2, inputs_sha256=hashes,
                  family_association=expected_association, previous_summary_reports=previous_reports,
                  previous_candidate_artifacts=len(previous), raw_warm_dual_finite_length_unique_semantic_keys_checked=True,
                  exact_GPU_source_and_binary_control_report_binding_checked=True,
                  full_family_proof_reused_by_exact_base_and_payload_hashes=True, family_enumeration_rerun=False,
                  coarse_candidates=len(keys), refined_candidates=len(refined), previously_evaluated_candidates_excluded_from_LP=len(excluded),
                  eligible_refined_candidates=len(eligible), selected_distinct_new_LP_candidates=lp_count,
                  both_selection_stages_indices_roles_and_upper_only_ties_replayed=True, stages=stage_reports,
                  selected_saved_vectors_finite_and_exact_box_feasible=True, selected_full99_primal_dual_checkpoint_evaluations=2 * lp_count,
                  max_selected_cp_scalar_absolute_error=max_scalar_error, cpu_replays=cpu_reports,
                  cpu_replay_steps=refine_steps, max_cpu_gpu_vector_absolute_error=max_vector_error,
                  actual_LP_exact_intervals_checked=lp_count, actual_LP_exact_positive_lower_bounds=sum(r["phase1_audit"]["exact_positive_dual_bound"] for r in reports),
                  baseline_audit=baseline_audit, best_numeric_proposal_index=numeric_order[0]["proposal_index"],
                  best_numeric_objective=numeric_order[0]["numeric_objective"],
                  exact_strict_improvement_indices=[r["proposal_index"] for r in reports if r["exact_strict_improvement"]],
                  probe_reports=reports, scipy_version=scipy.__version__, numpy_version=np.__version__,
                  LP_solver_or_family_enumeration_reruns=0, search_or_native_producer_imported=False,
                  native_pair_or_domain_checks_performed=False, elapsed_seconds=time.perf_counter() - started,
                  scope="Coarse/refined rankings replay saved numerical upper values only; previously evaluated candidates are excluded at the LP shortlist stage, not at coarse/refinement. Exact scalar/input associations checked for all stages; independent full99 CP evaluation only for the declared LP shortlist vectors, plus independent refinement-length CPU replay for three selected shapes. Exact positive LP lower bounds exclude only their own K. No pair/domain pass, exhaustive LP coverage, exact CP proof, graph construction or general nonexistence claim.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("inputs_sha256", "probe_reports", "baseline_audit", "cpu_replays")}))


if __name__ == "__main__":
    main()
