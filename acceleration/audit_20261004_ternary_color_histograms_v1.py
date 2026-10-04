"""Independent saved colour-histogram replay; no producer imports or solver."""
from __future__ import annotations

import argparse
from collections import OrderedDict
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/audit_20261004_ternary_color_histograms_v1.py"
SPEC = "acceleration/audit_20261004_ternary_color_histograms_v1_spec.md"
PRODUCER = "acceleration/screen_20261004_ternary_color_histograms_v1.py"
PRODUCER_SPEC = "acceleration/screen_20261004_ternary_color_histograms_v1_spec.md"
PRODUCER_SHA = "06195603c1e63b29a7b0af4f9434b4b911c470bfa25427241debc7e635bf02e8"
PRODUCER_SPEC_SHA = "eaf7c8d2f0d51aa8c4d02a541e7e851a0bff57e4bc970af3e9cd2c8b6002c2ed"
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
FAMILY = "INDEPENDENT_TERNARY_COLOR_HISTOGRAM_SCREEN_V1_"
WRITTEN_ID = "C-UNRESTRICTED-TARGET-TERNARY-LEFT-CODE-COLOR-MOMENTS-WEIGHTS48-75"


class Veto(ValueError):
    pass


def need(condition, stage):
    if not condition:
        raise Veto(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_KEY")
        result[key] = value
    return result


def parse(data):
    def bad_constant(_):
        raise Veto("NONFINITE_JSON")
    return json.loads(data, object_pairs_hook=unique, parse_constant=bad_constant)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, payload):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, allow_nan=False, ensure_ascii=False, indent=2)
        stream.write("\n")


def safe(name):
    need(type(name) is str and "\\" not in name and ":" not in name
         and all(p not in ("", ".", "..") for p in name.split("/")), "INPUT_PATH")
    path = ROOT / name
    need(path.is_file() and path.resolve().is_relative_to(ROOT)
         and all(not p.is_symlink() for p in (path, *path.parents))
         and path.stat().st_size <= 50*1024*1024, "INPUT_PATH")
    return path


class Reader:
    def __init__(self, deadline, out):
        self.deadline, self.out, self.pins = deadline, out, {}
        self.progress = {"phase": "authentication", "completed_labels": 0}

    def tick(self):
        state = self.deadline.status()
        need(state.get("stop_required") is False and state["remaining_seconds"] > 20, "SAVE_GUARD")

    def raw(self, name, wanted):
        self.tick()
        data = safe(name).read_bytes()
        need(type(wanted) is str and len(wanted) == 64 and digest(data) == wanted, "INPUT_SHA")
        need(name not in self.pins or self.pins[name] == wanted, "PIN_CONFLICT")
        self.pins[name] = wanted
        self.tick()
        return data

    def ref(self, ref):
        need(type(ref) is dict and set(ref) == {"path", "sha256"}, "REFERENCE")
        return parse(self.raw(ref["path"], ref["sha256"]))

    def closing(self):
        for name, wanted in list(self.pins.items()):
            self.raw(name, wanted)

    def checkpoint(self, case):
        self.tick()
        save(self.out / f"checkpoint_{case:03d}.json",
             {"progress": dict(self.progress), "deadline": self.deadline.status()})
        self.tick()


def parameters(n, k, sizes):
    need(type(n) is int and type(k) is int and k > 0 and k % 2 == 0
         and 2*(n-1) == k*k, "PARAMETERS")
    need(type(sizes) in (tuple, list) and len(sizes) == 3
         and all(type(s) is int and s > 0 and s % 3 == 0 for s in sizes)
         and sum(sizes) == n, "POPULATION")


def scalar(n, k, sizes, t):
    parameters(n, k, sizes)
    need(type(t) is int, "T_TYPE")
    need(t % 3 == 0, "T_DIVISIBILITY")
    need(0 <= t and 2*t <= k*min(sizes), "T_RANGE")
    need((n, k) != (99, 14) or all(18*t >= s*(n-s) for s in sizes), "SCALAR_RAYLEIGH")
    q = sum(sizes[i]*sizes[j] for i in range(3) for j in range(i+1, 3))
    total_square_num = 3*(2*k+1)*t-2*q
    # Summed A^2 indicator norm, then isolate each individual norm equation.
    need(total_square_num % 3 == 0, "SCALAR_Z_INTEGER")
    total_square = total_square_num // 3
    answer = []
    for s in sizes:
        numerator = 2*s*s-(k*k+2)*s+(4*k+2)*t-total_square
        need(numerator % 3 == 0, "SCALAR_Z_INTEGER")
        z = numerator // 3
        need(0 <= 2*z <= k*t, "SCALAR_Z_RANGE")
        answer.append(z)
    return answer


def histogram(h, size, total, square, last):
    need(type(h) in (list, tuple) and len(h) == last+1, "HIST_SHAPE")
    need(all(type(x) is int and x >= 0 for x in h), "HIST_TYPE")
    need(sum(h) == size, "HIST_COUNT")
    need(sum(r*x for r, x in enumerate(h)) == total, "HIST_SUM")
    need(sum(r*r*x for r, x in enumerate(h)) == square, "HIST_SQUARES")


def enumerate_histograms(size, total, square, last, tick):
    # Different enumerator: enumerate through last-2 and solve the final two bins.
    def visit(lo, count, linear, quadratic, prefix):
        tick()
        if count < 0 or not lo*count <= linear <= last*count:
            return
        if quadratic < 0 or quadratic % 2 != linear % 2:
            return
        if quadratic*count < linear*linear or quadratic > (lo+last)*linear-lo*last*count:
            return
        if lo == last-1:
            high = linear-lo*count
            low = count-high
            if 0 <= high <= count and lo*lo*low+last*last*high == quadratic:
                yield tuple(prefix+[low, high])
            return
        for number in range(count+1):
            yield from visit(lo+1, count-number, linear-lo*number,
                             quadratic-lo*lo*number, prefix+[number])
    need(type(last) is int and last >= 1, "HIST_DOMAIN")
    yield from visit(0, size, total, square, [])


def subset_sums(capacities, degree, tick):
    need(type(degree) is int and degree >= 0, "SELECTION_DEGREE")
    need(all(type(x) is int and x >= 0 for x in capacities), "SELECTION_CAPACITY")
    possible = [{0}] + [set() for _ in range(degree)]
    copies_seen = 0
    for weight, number in enumerate(capacities):
        for _ in range(number):
            tick()
            copies_seen += 1
            for used in range(min(degree, copies_seen), 0, -1):
                possible[used].update(x+weight for x in possible[used-1])
    return possible[degree]


def pool(h, degree, tick, own=None):
    capacities = list(h)
    if own is None:
        capacities[0] = 0
    else:
        need(type(own) is int and 0 <= own < len(h) and h[own] > 0, "SELF_EXCLUSION")
        capacities[own] -= 1
        capacities[-1] = 0
    return subset_sums(capacities, degree, tick)


def bits(values):
    return sum(1 << x for x in values)


def cn_capacity(k, sizes, i, r, sums):
    d = k-2*r
    # Counts of nonreturn two-walks, organized by endpoint colour.
    for end in range(3):
        if end == i:
            parts = [(k-1)*d-2*sums[i]] + [sums[a]-r for a in range(3) if a != i]
            capacity = 2*(sizes[i]-1)-d
        else:
            third = 3-i-end
            parts = [sums[i], k*r-2*sums[end], sums[third]-r]
            capacity = 2*(sizes[end]-r)
        if any(x < 0 for x in parts) or sum(parts) != capacity:
            return False
    return True


def row(k, sizes, i, r, h, pools, tick):
    j, ell = [c for c in range(3) if c != i]
    own = pool(h, k-2*r, tick, own=r)
    cross_j, cross_ell = pools[j][r], pools[ell][r]
    lhs = k*k+2-3*(k+1)*r+2*(sizes[j]-sizes[i])
    rhs = 2*(sizes[ell]-sizes[j])
    need(lhs % 3 == rhs % 3 == 0, "ROW_INTEGRAL")
    allowed, first = set(), None
    for value in sorted(cross_j):
        tick()
        trial = [0, 0, 0]
        trial[j], trial[i], trial[ell] = value, value+lhs//3, value-rhs//3
        if trial[i] in own and trial[ell] in cross_ell and cn_capacity(k, sizes, i, r, trial):
            allowed.add(value)
            if first is None:
                first = trial
    return {"possible": bool(allowed), "feasible_j_bits": bits(allowed), "first_witness_sums": first,
            "rainbow_degree": r, "own_bits": bits(own), "j_bits": bits(cross_j),
            "ell_bits": bits(cross_ell), "own_minus_j": lhs//3, "j_minus_ell": rhs//3}, allowed


def aggregate(hist, choices, target, tick):
    need(type(target) is int and target >= 0, "AGGREGATE_TARGET")
    attainable = {0}
    for r, number in enumerate(hist):
        for _ in range(number):
            tick()
            attainable = {old+value for old in attainable for value in choices[r]
                          if old+value <= target}
            if not attainable:
                return False
    return target in attainable


def propagate(k, sizes, squares, domains, tick, emit):
    rounds = 0
    cache = OrderedDict()
    def cross(h, d):
        key = (h, d)
        if key not in cache:
            cache[key] = pool(h, d, tick)
            if len(cache) > 8192:
                cache.popitem(last=False)
        return cache[key]
    while all(domains):
        tick()
        rounds += 1
        pools = [[set() for _ in range(k//2+1)] for _ in range(3)]
        for i in range(3):
            for _, h in domains[i]:
                for d in range(k//2+1):
                    tick()
                    pools[i][d].update(cross(h, d))
        following = [[], [], []]
        for i in range(3):
            for ordinal, h in domains[i]:
                tick()
                choices, rejection = [set() for _ in h], None
                for r, number in enumerate(h):
                    if number:
                        result, choices[r] = row(k, sizes, i, r, h, pools, tick)
                        if not result["possible"]:
                            rejection = {"round": rounds, "color": i, "histogram_ordinal": ordinal, **result}
                            break
                j = next(c for c in range(3) if c != i)
                if rejection is None and not aggregate(h, choices, squares[j], tick):
                    rejection = {"round": rounds, "color": i, "histogram_ordinal": ordinal,
                                 "possible": False, "reason": "AGGREGATE_STUB_SUM", "other_color": j,
                                 "required_total": squares[j], "row_j_bits": [bits(s) for s in choices]}
                if rejection is None:
                    following[i].append((ordinal, h))
                else:
                    emit(rejection)
        previous_sizes = [len(d) for d in domains]
        domains = following
        if [len(d) for d in domains] == previous_sizes:
            break
    return {"rounds": rounds, "surviving_ordinals": [[o for o, _ in d] for d in domains],
            "surviving_histograms": [len(d) for d in domains], "necessary_screen_pass": all(domains)}


def populations():
    return [list(s) for a in range(24, 34, 3) for b in range(a, 52, 3)
            if b <= (c := 99-a-b) for s in [(a, b, c)]]


def labels():
    return [{"label": index, "populations": sizes, "rainbow_triangles": t}
            for index, (sizes, t) in enumerate((s, t) for s in populations() for t in range(0, 7*s[0]+1, 3))]


def gate(value, ending):
    need(type(value) is dict and value.get("status") == FAMILY+ending
         and type(value.get("implementation_version")) is int and value["implementation_version"] == 1
         and value.get("producer") == "/root/structural" and value.get("verifier") == "/root/checkpoint_audit"
         and value.get("method") == "independent_artifact_check" and value.get("target_resolution") == "NONE"
         and value.get("source_sha256") == PRODUCER_SHA
         and value.get("specification_sha256") == PRODUCER_SPEC_SHA, "GATE_HEADER")
    if ending == "AUTHOR_CONTROLS_PASS":
        for key, expected in (("positive_controls", 10), ("negative_controls", 21), ("total_controls", 31), ("matched_controls", 31)):
            need(type(value.get(key)) is int and value[key] == expected, "GATE_COUNTS")


def written_gate(value):
    need(type(value) is dict and value.get("status") ==
         "INDEPENDENT_TARGET_TERNARY_LEFT_CODE_COLOR_MOMENTS_WEIGHTS48_75_V1_WRITTEN_PASS"
         and value.get("id") == WRITTEN_ID and type(value.get("claim_revision")) is int
         and value["claim_revision"] == 1 and value.get("producer") == "/root/structural"
         and value.get("verifier") == "/root/native_driver" and value.get("method") == "independent_derivation"
         and value.get("target_resolution") == "NONE", "WRITTEN_GATE")


def options(words):
    need(type(words) is list and len(words) % 2 == 0, "RUNTIME_OPTIONS")
    result = {}
    for name, value in zip(words[::2], words[1::2]):
        need(type(name) is str and name.startswith("--") and name not in result and type(value) is str,
             "RUNTIME_OPTIONS")
        result[name] = value
    return result


def runtime(plan, manifest, terminal, summary, mode):
    command, child, worker = [plan.get(k) for k in ("command", "child_argv", "worker_argv")]
    need(type(command) is list and type(child) is list and type(worker) is list and "--" in command,
         "RUNTIME_PLAN")
    split = command.index("--")
    need(same(command[split+1:], child) and same(child[8:], worker)
         and plan.get("supervisor_argv", command) == command, "RUNTIME_SUFFIX")
    need(len(worker) == (12 if mode == "calibrate" else 16) and worker[1] == "-B"
         and Path(worker[2]).resolve() == ROOT/PRODUCER and worker[3] == mode
         and Path(command[2]).resolve() == ROOT/"acceleration/run_compute_command_v2.py", "RUNTIME_WORKER")
    outer, flags = options(command[3:split]), options(worker[4:])
    need(flags.get("--self-sha256") == PRODUCER_SHA and flags.get("--spec-sha256") == PRODUCER_SPEC_SHA,
         "RUNTIME_SOURCE")
    need(same(manifest.get("command"), child) and type(manifest.get("schema_version")) is int
         and manifest["schema_version"] == 1 and manifest.get("source_sha256") == SOFTWARE["acceleration/run_compute_command_v2.py"]
         and manifest.get("runtime_scope") == "LOCAL_WINDOWS_SUSPENDED_JOB_V1"
         and manifest.get("process_scope") == "Local non-escaping process tree only; remote/daemonized compute is unsupported"
         and manifest.get("cumulative_across_commands") is False and manifest.get("automatic_retry") is False
         and Path(manifest.get("cwd", "")).resolve() == ROOT, "RUNTIME_MANIFEST")
    for key, flag in (("seconds", "--seconds"), ("shutdown_reserve_seconds", "--shutdown-reserve-seconds")):
        need(type(manifest.get(key)) in (int, float) and math.isfinite(manifest[key])
             and manifest[key] == float(outer[flag]), "RUNTIME_ALLOCATION")
    need(type(terminal.get("command_exit_code")) is int and terminal["command_exit_code"] == 0
         and terminal.get("deadline_reached") is False and terminal.get("error") is None, "RUNTIME_EXIT")
    cleanup = terminal.get("cleanup")
    need(type(cleanup) is dict and type(cleanup.get("actual_exit_code")) is int and cleanup["actual_exit_code"] == 0
         and all(cleanup.get(k) is True for k in ("created_suspended", "resumed", "reaped", "job_active_zero_observed"))
         and cleanup.get("cleanup_errors") == [], "RUNTIME_CLEANUP")
    need(type(manifest.get("invocation_id")) is str and bool(manifest["invocation_id"])
         and terminal.get("invocation_id") == manifest["invocation_id"], "RUNTIME_INVOCATION")
    elapsed = terminal.get("elapsed_seconds")
    need(type(elapsed) in (int, float) and math.isfinite(elapsed) and 0 <= elapsed <= manifest["seconds"], "RUNTIME_ELAPSED")
    # Producer records [sys.executable,*sys.argv]; interpreter -B is not sys.argv.
    need(type(summary.get("command")) is list and len(summary["command"]) == len(worker)-1
         and Path(summary["command"][0]).resolve() == Path(worker[0]).resolve()
         and Path(summary["command"][1]).resolve() == Path(worker[2]).resolve()
         and same(summary["command"][2:], worker[3:]), "RUNTIME_SUMMARY_COMMAND")
    state = summary.get("deadline")
    need(type(state) is dict and state.get("stop_required") is False
         and type(state.get("remaining_seconds")) in (int, float) and math.isfinite(state["remaining_seconds"])
         and state["remaining_seconds"] > 20, "RUNTIME_DEADLINE")
    return flags


def synthetic_runtime():
    python = (ROOT/"build/research-venv/Scripts/python.exe").as_posix()
    worker = [python, "-B", (ROOT/PRODUCER).as_posix(), "calibrate", "--seconds", "150", "--out",
              (ROOT/"acceleration/results/synthetic_scalar").as_posix(), "--self-sha256", PRODUCER_SHA,
              "--spec-sha256", PRODUCER_SPEC_SHA]
    child = ["uv", "run", "--locked", "--offline", "--cache-dir", (ROOT/"build/uv-cache").as_posix(), "--python", python, *worker]
    command = [python, "-B", (ROOT/"acceleration/run_compute_command_v2.py").as_posix(), "--seconds", "180",
               "--shutdown-reserve-seconds", "20", "--allocation-reason", "synthetic only", "--success-criterion", "clean0",
               "--verification-criterion", "source fixture", "--out", "synthetic_supervision", "--", *child]
    manifest = {"schema_version": 1, "source_sha256": SOFTWARE["acceleration/run_compute_command_v2.py"],
                "command": child, "cwd": ROOT.as_posix(), "seconds": 180.0, "shutdown_reserve_seconds": 20.0,
                "runtime_scope": "LOCAL_WINDOWS_SUSPENDED_JOB_V1",
                "process_scope": "Local non-escaping process tree only; remote/daemonized compute is unsupported",
                "cumulative_across_commands": False, "automatic_retry": False, "invocation_id": "synthetic-only"}
    terminal = {"command_exit_code": 0, "error": None, "deadline_reached": False, "invocation_id": "synthetic-only",
                "elapsed_seconds": 0.1, "cleanup": {"actual_exit_code": 0, "created_suspended": True, "resumed": True,
                "reaped": True, "job_active_zero_observed": True, "cleanup_errors": []}}
    summary = {"command": [python, *worker[2:]], "deadline": {"stop_required": False, "remaining_seconds": 149.0}}
    return {"plan": {"command": command, "supervisor_argv": command, "child_argv": child, "worker_argv": worker},
            "manifest": manifest, "terminal": terminal, "summary": summary}


AUTHOR_NAMES = (
    "rook9_row_colors_scalar", "rook9_complete_histogram_universe", "bounded_subset_sum_exact",
    "hand_local24_24_51_survivor", "old21_boundary_pointwise_rejected", "zero_r_cross_pool_empty",
    "rook_self_copy_removed", "rook_pair_CN_capacities", "declared12_population761_label_universe",
    "exact_weighted_stub_sum_gap", "k_boolean", "population_boolean", "population_total", "t_boolean",
    "t_not_divisible3", "t_negative", "t_above_capacity", "histogram_boolean", "histogram_short",
    "histogram_negative", "histogram_count", "histogram_first_moment", "histogram_square_only",
    "selection_degree_boolean", "selection_degree_negative", "self_copy_missing", "duplicate_json",
    "parent_relative_input", "wrong_source_hash", "inclusive_reserve_boundary", "configuration_population_boolean")
AUTHOR_STAGES = ("PASS",)*10 + ("PARAMETERS", "POPULATION", "POPULATION", "T_TYPE", "T_DIVISIBILITY",
    "T_RANGE", "T_RANGE", "HIST_TYPE", "HIST_SHAPE", "HIST_TYPE", "HIST_COUNT", "HIST_SUM", "HIST_SQUARES",
    "SELECTION_DEGREE", "SELECTION_DEGREE", "SELF_EXCLUSION", "DUPLICATE_KEY", "INPUT_PATH", "INPUT_SHA",
    "SAVE_GUARD", "CONFIG_DOMAIN")


def author_payloads():
    rook = [0, 3, 0]
    ha, hc = [0, 0, 0, 0, 0, 5, 17, 2], [0, 0, 14, 35, 2, 0, 0, 0]
    cfg = {"schema": "TERNARY_COLOR_HISTOGRAM_SCREEN_CONFIGURATION_V1", "n": 99, "k": 14,
           "populations": populations(), "root_authority": {}, "written_bound_gate": {}, "independent_author_controls": {}}
    cfg["populations"][-1][-1] = True
    return (
        {"n": 9, "k": 4, "sizes": [3, 3, 3], "t": 3, "z": [3, 3, 3]},
        {"size": 3, "t": 3, "z": 3, "only_bins": rook},
        {"capacities": [2, 1], "degree": 2, "sums": [0, 1]},
        {"sizes": [24, 24, 51], "t": 141, "z": [835, 835, 403], "histograms": [ha, ha, hc]},
        {"sizes": [21, 36, 42], "t": 147, "bin": 7}, {"h": [3, 0, 0], "degree": 1},
        {"h": rook, "r": 1, "degree": 2, "sums": [2]},
        {"k": 4, "sizes": [3, 3, 3], "color": 0, "r": 1, "sums": [2, 1, 1]},
        {"populations": populations(), "count": 761}, {"hist": [2], "row_sums": [1, 3], "allowed": [2, 4, 6], "forbidden": 5},
        {"k": True}, {"sizes": [True, 3, 5]}, {"sizes": [3, 3, 6]}, {"t": True}, {"t": 1}, {"t": -3}, {"t": 9},
        {"h": [0, True, 2]}, {"h": [0, 3]}, {"h": [-1, 4, 0]}, {"h": [0, 2, 0]}, {"h": [1, 1, 1]},
        {"h": [0, 0, 0, 0, 0, 4, 19, 1], "s": 24, "t": 141, "z": 835},
        {"degree": True}, {"degree": -1}, {"h": rook, "r": 0}, {"raw": '{ "x":1,"x":2 }'},
        {"path": "../outside"}, {"path": PRODUCER, "sha256": "0"*64}, {"synthetic_remaining_seconds": 20}, cfg)


def author_row(stored, index):
    need(type(stored) is dict and type(stored.get("index")) is int and stored["index"] == index
         and stored.get("name") == AUTHOR_NAMES[index] and stored.get("expected_stage") == AUTHOR_STAGES[index]
         and stored.get("observed_stage") == AUTHOR_STAGES[index] and stored.get("matched") is True
         and stored.get("synthetic_only") is True, "AUTHOR_STAGE")
    need(same(stored.get("payload"), author_payloads()[index]), "AUTHOR_PAYLOAD")


def author_action(index, payload, reader):
    tick = reader.tick
    rook, ha, hc = (0, 3, 0), (0, 0, 0, 0, 0, 5, 17, 2), (0, 0, 14, 35, 2, 0, 0, 0)
    def check(ok):
        need(ok, "HAND_REFERENCE")
        return True
    if index == 0:
        return check(scalar(9, 4, [3, 3, 3], 3) == [3, 3, 3])
    if index == 1:
        return check(list(enumerate_histograms(3, 3, 3, 2, tick)) == [rook])
    if index == 2:
        return check(subset_sums([2, 1], 2, tick) == {0, 1})
    if index == 3:
        for h, s, z in zip((ha, ha, hc), (24, 24, 51), (835, 835, 403)):
            histogram(h, s, 141, z, 7)
        rejected = []
        outcome = propagate(14, [24, 24, 51], [835, 835, 403], [[(0, ha)], [(0, ha)], [(0, hc)]], tick, rejected.append)
        return check(outcome["necessary_screen_pass"] and outcome["surviving_histograms"] == [1, 1, 1] and not rejected)
    if index == 4:
        hs = ((0, 0, 0, 0, 0, 0, 0, 21), (0, 0, 0, 0, 35, 0, 0, 1), (0, 0, 0, 21, 21, 0, 0, 0))
        pools = [[pool(h, d, tick) for d in range(8)] for h in hs]
        result, _ = row(14, [21, 36, 42], 1, 7, hs[1], pools, tick)
        return check(not result["possible"] and pools[0][7] == {49} and max(pools[2][7]) == 28)
    if index == 5:
        return check(pool((3, 0, 0), 1, tick) == set())
    if index == 6:
        return check(pool(rook, 2, tick, own=1) == {2})
    if index == 7:
        return check(cn_capacity(4, [3, 3, 3], 0, 1, [2, 1, 1]))
    if index == 8:
        return check(len(populations()) == 12 and len(labels()) == 761
                     and len({(tuple(x["populations"]), x["rainbow_triangles"]) for x in labels()}) == 761)
    if index == 9:
        return check(aggregate([2], [{1, 3}], 4, tick) and not aggregate([2], [{1, 3}], 5, tick))
    if index == 10:
        return parameters(9, payload["k"], [3, 3, 3])
    if index in (11, 12):
        return parameters(9, 4, payload["sizes"])
    if 13 <= index <= 16:
        return scalar(9, 4, [3, 3, 3], payload["t"])
    if 17 <= index <= 21:
        return histogram(payload["h"], 3, 2 if index == 21 else 3, 3, 2)
    if index == 22:
        return histogram(payload["h"], payload["s"], payload["t"], payload["z"], 7)
    if index in (23, 24):
        return subset_sums([2, 1], payload["degree"], tick)
    if index == 25:
        return pool(payload["h"], 2, tick, own=payload["r"])
    if index == 26:
        return parse(payload["raw"])
    if index == 27:
        return reader.raw(payload["path"], "0"*64)
    if index == 28:
        return reader.raw(payload["path"], payload["sha256"])
    if index == 29:
        class Synthetic:
            def status(self):
                return {"stop_required": False, "remaining_seconds": payload["synthetic_remaining_seconds"]}
        return Reader(Synthetic(), reader.out).tick()
    if index == 30:
        return configuration(payload)
    raise Veto("AUTHOR_INDEX")


def configuration(value):
    need(type(value) is dict and value.get("schema") == "TERNARY_COLOR_HISTOGRAM_SCREEN_CONFIGURATION_V1"
         and type(value.get("n")) is int and value["n"] == 99 and type(value.get("k")) is int and value["k"] == 14
         and same(value.get("populations"), populations()), "CONFIG_DOMAIN")
    need(all(type(value.get(k)) is dict for k in ("root_authority", "written_bound_gate", "independent_author_controls")),
         "CONFIG_GATES")


def qualification(reader, ref):
    own = reader.ref(ref)
    gate(own, "CALIBRATION_PASS")
    need(own.get("checking_source_sha256") == reader.pins[SELF]
         and own.get("checking_specification_sha256") == reader.pins[SPEC], "OWN_SOURCE")
    for name, count in (("positive_controls", 16), ("negative_controls", 34), ("total_controls", 50), ("matched_controls", 50)):
        need(type(own.get(name)) is int and own[name] == count, "OWN_COUNTS")
    need(own.get("actual_target_input_read") is False and own.get("producer_imports") == 0
         and own.get("solver_calls") == 0, "OWN_SCOPE")
    software = {SELF: reader.pins[SELF], SPEC: reader.pins[SPEC], PRODUCER: PRODUCER_SHA,
                PRODUCER_SPEC: PRODUCER_SPEC_SHA, **SOFTWARE}
    need(same(own.get("inputs_sha256"), software), "OWN_SOFTWARE")
    base = safe(ref["path"]).parent
    outputs = own.get("outputs_sha256")
    expected = {"controls.json"} | {f"case_{i:02d}.json" for i in range(50)}
    need(type(outputs) is dict and set(outputs) == expected
         and {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()} == expected | {"summary.json"},
         "OWN_OUTPUT_POPULATION")
    data = {}
    for name, wanted in outputs.items():
        data[name] = parse(reader.raw(base.relative_to(ROOT).as_posix()+"/"+name, wanted))
    table = data["controls.json"]
    need(type(table) is list and len(table) == 50 and sum(r.get("expected_stage") == "PASS" for r in table) == 16,
         "OWN_TABLE")
    for i, row in enumerate(table):
        need(type(row) is dict and type(row.get("index")) is int and row["index"] == i and row.get("matched") is True
             and row.get("synthetic_only") is True and row.get("expected_stage") == row.get("observed_stage")
             and same(row, data[f"case_{i:02d}.json"]), "OWN_STAGE")
    return own


def packet(reader, ref, mode):
    value = reader.ref(ref)
    need(value.get("schema") == "TERNARY_COLOR_HISTOGRAM_INDEPENDENT_PACKET_V1", "PACKET_SCHEMA")
    qualification(reader, value["independent_calibration"])
    summary = reader.ref(value["producer_summary"])
    plan, manifest, terminal = [reader.ref(value[k]) for k in ("producer_plan", "supervisor_manifest", "supervisor_terminal")]
    flags = runtime(plan, manifest, terminal, summary, "calibrate" if mode == "controls" else "screen")
    need(type(summary.get("implementation_version")) is int and summary["implementation_version"] == 1
         and summary.get("source_sha256") == PRODUCER_SHA and summary.get("specification_sha256") == PRODUCER_SPEC_SHA
         and summary.get("producer") == "/root/structural" and summary.get("method") == "candidate_exact_enumeration"
         and summary.get("target_resolution") == "NONE", "PRODUCER_HEADER")
    expected_status = "TERNARY_COLOR_HISTOGRAM_SCREEN_V1_AUTHOR_CONTROLS_CANDIDATE_PASS" if mode == "controls" else "CANDIDATE_TERNARY_COLOR_HISTOGRAM_SCREEN_V1_COMPLETE"
    need(summary.get("status") == expected_status, "PRODUCER_STATUS")
    need(type(summary.get("inputs_sha256")) is dict and summary["inputs_sha256"].get(PRODUCER) == PRODUCER_SHA
         and summary["inputs_sha256"].get(PRODUCER_SPEC) == PRODUCER_SPEC_SHA, "PRODUCER_INPUTS")
    for name, wanted in summary["inputs_sha256"].items():
        reader.raw(name, wanted)
    output_root = safe(value["producer_summary"]["path"]).parent
    need(Path(flags["--out"]).resolve() == output_root and output_root.is_relative_to(ROOT/"acceleration/results"), "PRODUCER_OUTPUT_ROOT")
    outputs = summary.get("outputs_sha256")
    need(type(outputs) is dict and "summary.json" not in outputs and "failure.json" not in outputs, "PRODUCER_OUTPUTS")
    actual = {p.relative_to(output_root).as_posix() for p in output_root.rglob("*") if p.is_file()}
    need(actual == set(outputs) | {"summary.json"}, "OUTPUT_POPULATION")
    for name, wanted in outputs.items():
        reader.raw(output_root.relative_to(ROOT).as_posix()+"/"+name, wanted)
    if mode == "full":
        controls = reader.ref(value["independent_author_controls"])
        gate(controls, "AUTHOR_CONTROLS_PASS")
        written = reader.ref(value["written_bound_gate"])
        written_gate(written)
        cfg = reader.ref({"path": flags["--configuration"], "sha256": flags["--configuration-sha256"]})
        configuration(cfg)
        need(same(cfg["written_bound_gate"], value["written_bound_gate"])
             and same(cfg["independent_author_controls"], value["independent_author_controls"]), "CONFIG_GATE_BINDING")
        reader.ref(cfg["root_authority"])
    return value, summary, output_root, outputs


def replay_author(reader, summary, folder):
    for key, expected in (("positive_controls", 10), ("negative_controls", 21), ("total_controls", 31)):
        need(type(summary.get(key)) is int and summary[key] == expected, "AUTHOR_COUNTS")
    need(summary.get("target_graph_read") is False and summary.get("scientific_labels_screened") == 0
         and type(summary.get("scientific_labels_screened")) is int and summary.get("actual_calibration_only") is True,
         "AUTHOR_SCOPE")
    table = parse((folder/"controls.json").read_bytes())
    need(type(table) is list and len(table) == 31, "AUTHOR_TABLE")
    matches = []
    for index, stored in enumerate(table):
        reader.tick()
        author_row(stored, index)
        need(same(stored, parse((folder/f"case_{index:02d}.json").read_bytes())), "AUTHOR_DUPLICATED_ROW")
        try:
            result, observed = author_action(index, stored["payload"], reader), "PASS"
        except Veto as exc:
            result, observed = None, str(exc)
        need(observed == AUTHOR_STAGES[index] and same(result, stored.get("result")), "AUTHOR_REPLAY")
        matches.append({"index": index, "name": AUTHOR_NAMES[index], "expected_stage": AUTHOR_STAGES[index],
                        "independent_stage": observed, "matched": True})
    return matches


def jsonl_rows(reader, path):
    with path.open("rb") as stream:
        for line in stream:
            reader.tick()
            need(line.endswith(b"\n") and bool(line.strip()), "JSONL_FRAMING")
            yield parse(line)


def check_next(iterator, expected, stage):
    try:
        stored = next(iterator)
    except StopIteration:
        raise Veto(stage+"_EARLY_EOF")
    need(same(stored, expected), stage)


def eof(iterator, stage):
    try:
        next(iterator)
    except StopIteration:
        return
    raise Veto(stage+"_EXTRA")


def full(reader, summary, folder, outputs):
    universe = labels()
    need(same(parse((folder/"universe.json").read_bytes()), {"populations": populations(), "labels": universe}), "LABEL_UNIVERSE")
    saved_labels, results, expected_outputs = jsonl_rows(reader, folder/"labels.jsonl"), [], {"universe.json", "labels.jsonl"}
    total_histograms = total_rejections = 0
    for item in universe:
        case, sizes, t = item["label"], item["populations"], item["rainbow_triangles"]
        reader.progress.update(phase="full_label", active_label=case)
        reader.tick()
        result = dict(item)
        last_histogram, last_round = None, None
        try:
            squares = scalar(99, 14, sizes, t)
        except Veto as exc:
            result.update(scalar_pass=False, first_veto=str(exc), necessary_screen_pass=False)
        else:
            base = f"label_{case:03d}"
            expected_outputs.update(base+"/"+suffix for suffix in ("histograms.jsonl", "rejections.jsonl", "result.json"))
            stored_hist = jsonl_rows(reader, folder/base/"histograms.jsonl")
            domains = [[], [], []]
            for color in range(3):
                for ordinal, h in enumerate(enumerate_histograms(sizes[color], t, squares[color], 7, reader.tick)):
                    check_next(stored_hist, {"color": color, "ordinal": ordinal, "bins": list(h)}, "HISTOGRAM_ROW")
                    domains[color].append((ordinal, h))
                    total_histograms += 1
                    last_histogram = [color, ordinal]
            eof(stored_hist, "HISTOGRAM_ROW")
            initial = [len(d) for d in domains]
            rejections = jsonl_rows(reader, folder/base/"rejections.jsonl")
            def reject(expected):
                nonlocal total_rejections, last_round
                check_next(rejections, expected, "REJECTION_ROW")
                total_rejections += 1
                last_round = expected["round"]
            outcome = propagate(14, sizes, squares, domains, reader.tick, reject)
            eof(rejections, "REJECTION_ROW")
            result.update(scalar_pass=True, square_totals=squares, initial_histograms=initial, **outcome)
            need(same(parse((folder/base/"result.json").read_bytes()), result), "LABEL_RESULT")
        check_next(saved_labels, result, "LABEL_ROW")
        checkpoint_name = f"checkpoint_{case:03d}.json"
        expected_outputs.add(checkpoint_name)
        cp = parse((folder/checkpoint_name).read_bytes())
        progress = cp.get("progress")
        need(same(progress, {"completed_labels": case+1, "active_label": None, "phase": "between_labels",
                            "active_histogram": last_histogram, "active_round": last_round}), "LABEL_CHECKPOINT")
        state = cp.get("deadline")
        need(type(state) is dict and state.get("stop_required") is False
             and type(state.get("remaining_seconds")) in (int, float) and math.isfinite(state["remaining_seconds"])
             and state["remaining_seconds"] > 20, "CHECKPOINT_DEADLINE")
        results.append(result)
        reader.progress["completed_labels"] = case+1
        reader.checkpoint(case)
    eof(saved_labels, "LABEL_ROW")
    need(set(outputs) == expected_outputs, "SCIENCE_OUTPUT_POPULATION")
    expected = {"complete_labels": 761, "scalar_pass": sum(r["scalar_pass"] for r in results),
                "necessary_screen_pass": sum(r["necessary_screen_pass"] for r in results),
                "excluded_labels": [r["label"] for r in results if not r["necessary_screen_pass"]],
                "remaining_labels": [r["label"] for r in results if r["necessary_screen_pass"]],
                "graph_cases_enumerated": 0, "joint_histogram_tuples_enumerated": 0,
                "actual_left_word_existence_asserted": False, "constants_allowed": True}
    need(all(same(summary.get(k), v) for k, v in expected.items()), "FULL_SUMMARY")
    return {**expected, "complete_histogram_rows": total_histograms, "complete_rejection_rows": total_rejections}


def calibration(reader):
    routes = []
    def run(name, expected, payload, action):
        reader.tick()
        try:
            result, observed = action(), "PASS"
        except Veto as exc:
            result, observed = None, str(exc)
        row = {"index": len(routes), "name": name, "expected_stage": expected, "observed_stage": observed,
               "matched": expected == observed, "payload": payload, "result": result, "synthetic_only": True}
        save(reader.out/f"case_{len(routes):02d}.json", row)
        routes.append(row)
        need(row["matched"], "OWN_CONTROL_MISMATCH")
    def check(ok):
        need(ok, "HAND_REFERENCE")
        return True
    run("rook_scalar", "PASS", {}, lambda: check(scalar(9, 4, [3, 3, 3], 3) == [3, 3, 3]))
    run("rook_last_two_histograms", "PASS", {}, lambda: check(list(enumerate_histograms(3, 3, 3, 2, reader.tick)) == [(0, 3, 0)]))
    run("set_copy_sums", "PASS", {}, lambda: check(subset_sums([2, 1, 1], 2, reader.tick) == {0, 1, 2, 3}))
    run("self_remove", "PASS", {}, lambda: check(pool((0, 3, 0), 2, reader.tick, own=1) == {2}))
    run("cross_zero_excluded", "PASS", {}, lambda: check(pool((3, 0, 0), 1, reader.tick) == set()))
    run("aggregate_gap", "PASS", {}, lambda: check(aggregate([2], [{1, 3}], 4, reader.tick) and not aggregate([2], [{1, 3}], 5, reader.tick)))
    run("universe", "PASS", {}, lambda: check(len(populations()) == 12 and len(labels()) == 761))
    run("target_survivor", "PASS", {}, lambda: author_action(3, {}, reader))
    run("old_boundary_rejected", "PASS", {}, lambda: author_action(4, {}, reader))
    header = {"status": FAMILY+"AUTHOR_CONTROLS_PASS", "implementation_version": 1, "producer": "/root/structural",
              "verifier": "/root/checkpoint_audit", "method": "independent_artifact_check", "target_resolution": "NONE",
              "source_sha256": PRODUCER_SHA, "specification_sha256": PRODUCER_SPEC_SHA,
              "positive_controls": 10, "negative_controls": 21, "total_controls": 31, "matched_controls": 31}
    run("strict_controls_header", "PASS", header, lambda: gate(header, "AUTHOR_CONTROLS_PASS"))
    for key, value, expected in (("verifier", None, "GATE_HEADER"), ("implementation_version", True, "GATE_HEADER"),
                                 ("target_resolution", "EXCLUDED", "GATE_HEADER"), ("matched_controls", 30, "GATE_COUNTS"),
                                 ("positive_controls", True, "GATE_COUNTS")):
        damaged = {**header, key: value}
        run("damaged_header_"+key, expected, damaged, lambda d=damaged: gate(d, "AUTHOR_CONTROLS_PASS"))
    for name, expected, payload, action in (
        ("bool_degree", "SELECTION_DEGREE", True, lambda: subset_sums([2], True, reader.tick)),
        ("bool_count", "SELECTION_CAPACITY", [True], lambda: subset_sums([True], 1, reader.tick)),
        ("negative_count", "SELECTION_CAPACITY", [-1], lambda: subset_sums([-1], 1, reader.tick)),
        ("missing_self", "SELF_EXCLUSION", 0, lambda: pool((0, 3, 0), 2, reader.tick, own=0)),
        ("hist_square", "HIST_SQUARES", [0, 0, 0, 0, 0, 4, 19, 1], lambda: histogram([0, 0, 0, 0, 0, 4, 19, 1], 24, 141, 835, 7)),
        ("bool_t", "T_TYPE", True, lambda: scalar(9, 4, [3, 3, 3], True)),
        ("bool_n", "PARAMETERS", True, lambda: parameters(True, 4, [3, 3, 3])),
        ("duplicate_json", "DUPLICATE_KEY", '{"x":1,"x":2}', lambda: parse('{"x":1,"x":2}')),
        ("nonfinite_json", "NONFINITE_JSON", 'NaN', lambda: parse('NaN')),
        ("parent_path", "INPUT_PATH", '../x', lambda: safe('../x')),
        ("wrong_sha", "INPUT_SHA", '0'*64, lambda: reader.raw(SELF, '0'*64)),
        ("typed_row", "HAND_REFERENCE", {"x": True}, lambda: check(not same({"x": True}, {"x": 1})))):
        # typed_row is a positive reference rather than an expected Veto.
        run(name, "PASS" if name == "typed_row" else expected, payload, action)
    run("early_eof", "WIRE_EARLY_EOF", {}, lambda: check_next(iter([]), {}, "WIRE"))
    run("extra_eof", "WIRE_EXTRA", {}, lambda: eof(iter([{}]), "WIRE"))
    run("row_bool_corruption", "WIRE", {"x": True}, lambda: check_next(iter([{"x": True}]), {"x": 1}, "WIRE"))
    run("final_two_nontrivial_histogram", "PASS", {}, lambda: check(list(enumerate_histograms(3, 3, 5, 2, reader.tick)) == [(1, 1, 1)]))
    run("zero_selection", "PASS", {}, lambda: check(subset_sums([2, 1], 0, reader.tick) == {0}))
    run("bool_aggregate", "AGGREGATE_TARGET", True, lambda: aggregate([1], [{1}], True, reader.tick))
    run("negative_aggregate", "AGGREGATE_TARGET", -1, lambda: aggregate([1], [{1}], -1, reader.tick))
    written = {"status": "INDEPENDENT_TARGET_TERNARY_LEFT_CODE_COLOR_MOMENTS_WEIGHTS48_75_V1_WRITTEN_PASS",
               "id": WRITTEN_ID, "claim_revision": 1, "producer": "/root/structural", "verifier": "/root/native_driver",
               "method": "independent_derivation", "target_resolution": "NONE"}
    run("genuine_shaped_written_header", "PASS", written, lambda: written_gate(written))
    for key, value in (("id", "OTHER"), ("claim_revision", True), ("target_resolution", "EXCLUDED")):
        damaged = {**written, key: value}
        run("damaged_written_"+key, "WRITTEN_GATE", damaged, lambda d=damaged: written_gate(d))
    author = {"index": 0, "name": AUTHOR_NAMES[0], "expected_stage": "PASS", "observed_stage": "PASS",
              "matched": True, "synthetic_only": True, "payload": author_payloads()[0], "result": True}
    run("exact_author_payload", "PASS", author, lambda: author_row(author, 0))
    damaged_author = copy.deepcopy(author)
    damaged_author["payload"]["t"] = True
    run("author_payload_bool", "AUTHOR_PAYLOAD", damaged_author, lambda: author_row(damaged_author, 0))
    specimen = synthetic_runtime()
    def actual_shaped(value):
        return runtime(value["plan"], value["manifest"], value["terminal"], value["summary"], "calibrate")
    run("actual_shaped_runtime", "PASS", specimen, lambda: actual_shaped(specimen))
    for name, expected, role, key, value in (
        ("native20", "RUNTIME_EXIT", "terminal", "command_exit_code", 20),
        ("bool_exit", "RUNTIME_EXIT", "terminal", "command_exit_code", True),
        ("deadline_exit", "RUNTIME_EXIT", "terminal", "deadline_reached", True),
        ("wrong_invocation", "RUNTIME_INVOCATION", "terminal", "invocation_id", "OTHER"),
        ("bool_elapsed", "RUNTIME_ELAPSED", "terminal", "elapsed_seconds", True),
        ("wrong_scope", "RUNTIME_MANIFEST", "manifest", "process_scope", "OTHER"),
        ("wrong_summary_command", "RUNTIME_SUMMARY_COMMAND", "summary", "command", [])):
        damaged = copy.deepcopy(specimen)
        damaged[role][key] = value
        run(name, expected, damaged, lambda d=damaged: actual_shaped(d))
    unreaped = copy.deepcopy(specimen)
    unreaped["terminal"]["cleanup"]["reaped"] = False
    run("unreaped_runtime", "RUNTIME_CLEANUP", unreaped, lambda: actual_shaped(unreaped))
    run("inclusive_reserve", "SAVE_GUARD", {"remaining_seconds": 20},
        lambda: author_action(29, {"synthetic_remaining_seconds": 20}, reader))
    need(len(routes) == 50 and sum(r["expected_stage"] == "PASS" for r in routes) == 16, "OWN_POPULATION")
    save(reader.out/"controls.json", routes)
    return {"positive_controls": sum(r["expected_stage"] == "PASS" for r in routes),
            "negative_controls": sum(r["expected_stage"] != "PASS" for r in routes), "total_controls": len(routes),
            "matched_controls": len(routes), "actual_target_input_read": False, "producer_imports": 0, "solver_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("calibrate", "controls", "full"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--packet")
    parser.add_argument("--packet-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Separate exact set-DP colour histogram verification, all authentication and output inside one invocation.")
    out = Path(args.out).resolve()
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(), "OUTPUT_PATH")
    out.mkdir(parents=True, exist_ok=False)
    reader = Reader(deadline, out)
    try:
        for name, wanted in {SELF: args.self_sha256, SPEC: args.spec_sha256, PRODUCER: PRODUCER_SHA,
                             PRODUCER_SPEC: PRODUCER_SPEC_SHA, **SOFTWARE}.items():
            reader.raw(name, wanted)
        if args.mode == "calibrate":
            outcome = calibration(reader)
            ending = "CALIBRATION_PASS"
        else:
            _, summary, folder, outputs = packet(reader, {"path": args.packet, "sha256": args.packet_sha256}, args.mode)
            if args.mode == "controls":
                need(set(outputs) == {"controls.json"} | {f"case_{i:02d}.json" for i in range(31)}, "AUTHOR_OUTPUT_POPULATION")
                table = replay_author(reader, summary, folder)
                save(out/"author_controls_replay.json", table)
                outcome = {"positive_controls": 10, "negative_controls": 21, "total_controls": 31,
                           "matched_controls": 31, "actual_target_input_read": False}
                ending = "AUTHOR_CONTROLS_PASS"
            else:
                outcome = full(reader, summary, folder, outputs)
                save(out/"independent_outcome.json", outcome)
                ending = "COMPLETE_PASS"
        reader.closing()
        output_map = {}
        for path in sorted(out.rglob("*")):
            reader.tick()
            if path.is_file():
                output_map[path.relative_to(out).as_posix()] = digest(path.read_bytes())
                reader.tick()
        report = {"status": FAMILY+ending, "implementation_version": 1, "producer": "/root/structural",
                  "verifier": "/root/checkpoint_audit", "method": "independent_artifact_check", "target_resolution": "NONE",
                  "source_sha256": PRODUCER_SHA, "specification_sha256": PRODUCER_SPEC_SHA,
                  "checking_source_sha256": args.self_sha256, "checking_specification_sha256": args.spec_sha256,
                  "timestamp": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
                  "inputs_sha256": reader.pins, "outputs_sha256": output_map, "deadline": deadline.status(), **outcome,
                  "limitations": ["Necessary scalar/histogram relaxation only; no codeword, graph or target resolution.",
                                  "Different rows can select different pooled histograms and endpoints.",
                                  "Producer imports, AST and solver calls are absent; source identity is authenticated only.",
                                  "Finite atomic parsing regions have no hard real-time stop guarantee."]}
        save(out/"summary.json", report)
        reader.tick()
        print(json.dumps({"status": report["status"], "summary": (out/"summary.json").relative_to(ROOT).as_posix()}), flush=True)
        reader.tick()
        return 0
    except Exception as exc:
        save(out/"failure.json", {"status": "FAILED_OR_NOT_COMPLETED_PRESERVED", "stage": str(exc),
             "error_type": type(exc).__name__, "progress": reader.progress, "inputs_sha256": reader.pins,
             "deadline": deadline.status(), "target_resolution": "NONE", "automatic_retry": False,
             "wording": "not completed within the allocated budget" if str(exc) == "SAVE_GUARD" else "Input or engineering veto; no mathematical conclusion."})
        print(json.dumps({"status": "FAILED_OR_NOT_COMPLETED_PRESERVED", "stage": str(exc)}), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
