"""Exact full99 conditional CNF with custom, fully equivalent threshold gates.

No SAT solver or third-party cardinality encoder is imported by this producer.
"""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import argparse
import ctypes
import gzip
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import zlib

from theory_20260930_full_srg_validator import controls as graph_controls, validate


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "acceleration/results/20260917_partial_eight_matchings/manifest.json"
SCOPE_AUDIT = ROOT / "acceleration/results/20260930_independent_review/eight_domains_claim_binding.json"
PROTOCOL = Path(__file__).with_name("theory_20260930_eight_full99_cnf_spec.md")


def digest(path):
    value = sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1048576), b""):
            value.update(chunk)
    return value.hexdigest()


def save(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def negate(reference):
    return not reference if type(reference) is bool else -reference


class ResourceCap:
    def __init__(self):
        self.start = time.monotonic()
        self.peak_bytes = 0
        self.samples = 0
        if os.name == "nt":
            from ctypes import wintypes
            class Counters(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            self.counter_type = Counters
            self.get_process = ctypes.windll.kernel32.GetCurrentProcess
            self.get_process.restype = wintypes.HANDLE
            self.get_memory = ctypes.windll.psapi.GetProcessMemoryInfo
            self.get_memory.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            self.get_memory.restype = wintypes.BOOL

    def check(self):
        if os.name == "nt":
            counters = self.counter_type()
            counters.cb = ctypes.sizeof(counters)
            assert self.get_memory(self.get_process(), ctypes.byref(counters), counters.cb)
            self.peak_bytes = max(self.peak_bytes, counters.PeakWorkingSetSize)
        else:
            import resource
            self.peak_bytes = max(self.peak_bytes, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
        self.samples += 1
        if self.peak_bytes > 8 * 1024 ** 3:
            raise MemoryError("8GiB process working-set cap")
        if time.monotonic() - self.start > 120:
            raise TimeoutError("120-second complete build cap")


class Clauses:
    def __init__(self, stream=None, cap=None):
        self.stream = stream
        self.cap = cap
        self.count = 0
        self.rows = [] if stream is None else None

    def emit(self, *references):
        row, present = [], set()
        for reference in references:
            if type(reference) is bool:
                if reference:
                    return
                continue
            assert type(reference) is int and reference != 0
            if -reference in present:
                return
            if reference not in present:
                present.add(reference)
                row.append(reference)
        self.count += 1
        if self.stream is None:
            self.rows.append(row)
        else:
            self.stream.write((" ".join(map(str, row)) + (" " if row else "") + "0\n").encode("ascii"))
        if self.cap is not None and self.count % 10000 == 0:
            self.cap.check()


class Encoder:
    def __init__(self, top, clauses):
        self.top = top
        self.clauses = clauses

    def fresh(self):
        self.top += 1
        return self.top

    def conjunction(self, a, b):
        if type(a) is bool:
            return b if a else False
        if type(b) is bool:
            return a if b else False
        z = self.fresh()
        self.clauses.emit(a, -z)
        self.clauses.emit(b, -z)
        self.clauses.emit(-a, -b, z)
        return z

    def disjunction(self, a, b):
        if type(a) is bool:
            return True if a else b
        if type(b) is bool:
            return True if b else a
        z = self.fresh()
        self.clauses.emit(-a, z)
        self.clauses.emit(-b, z)
        self.clauses.emit(a, b, -z)
        return z

    def recurrence(self, a, b, c):
        if type(a) is bool:
            return True if a else self.conjunction(b, c)
        if type(b) is bool:
            return self.disjunction(a, c) if b else a
        if type(c) is bool:
            return self.disjunction(a, b) if c else a
        z = self.fresh()
        self.clauses.emit(-a, z)
        self.clauses.emit(-b, -c, z)
        self.clauses.emit(a, b, -z)
        self.clauses.emit(a, c, -z)
        return z

    def counter(self, inputs, bound, equality, annotation):
        assert len(inputs) == len(set(inputs)) and all(type(x) is int and x > 0 for x in inputs)
        assert 0 <= bound <= len(inputs)
        previous = {0: True}
        states = []
        first_clause = self.clauses.count + 1
        first_variable = self.top + 1
        for i, literal in enumerate(inputs, 1):
            current = {0: True}
            for j in range(1, min(i, bound + 1) + 1):
                reference = self.recurrence(previous.get(j, False), literal, previous.get(j - 1, False))
                current[j] = reference
                states.append([i, j, reference])
            previous = current
        if equality:
            self.clauses.emit(previous.get(bound, False))
        self.clauses.emit(negate(previous.get(bound + 1, False)))
        return {**annotation, "inputs": inputs, "bound": bound, "equality": equality,
                "states": states, "first_auxiliary_variable": first_variable if self.top >= first_variable else None,
                "last_auxiliary_variable": self.top if self.top >= first_variable else None,
                "auxiliary_null_reason": "All states folded to constants or inputs." if self.top < first_variable else None,
                "first_clause": first_clause, "clause_count": self.clauses.count - first_clause + 1}


def satisfies(clauses, values):
    return all(any(values[abs(v)] == (v > 0) for v in row) for row in clauses)


def counter_controls():
    gate_cases = 0
    for a, c in product((False, True, 1), (False, True, 3)):
        clauses = Clauses()
        encoder = Encoder(3, clauses)
        ref = encoder.recurrence(a, 2, c)
        for bits in product((False, True), repeat=3):
            values = {i + 1: value for i, value in enumerate(bits)}
            expected = (a if type(a) is bool else values[a]) or (values[2] and (c if type(c) is bool else values[c]))
            accepted = 0
            for helper_values in product((False, True), repeat=encoder.top - 3):
                assignment = {**values, **{i + 4: value for i, value in enumerate(helper_values)}}
                if satisfies(clauses.rows, assignment):
                    accepted += 1
                    assert (ref if type(ref) is bool else assignment[ref]) == expected
            assert accepted == 1
            gate_cases += 1
    rows, full_assignments, wrong_auxiliary_rejections = [], 0, 0
    for n in range(5):
        for bound in range(n + 1):
            for equality in (False, True):
                clauses = Clauses()
                encoder = Encoder(n, clauses)
                encoder.counter(list(range(1, n + 1)), bound, equality, {})
                accepted = 0
                for input_values in product((False, True), repeat=n):
                    expected = sum(input_values) == bound if equality else sum(input_values) <= bound
                    count = 0
                    for helper_values in product((False, True), repeat=encoder.top - n):
                        values = {i + 1: value for i, value in enumerate(input_values + helper_values)}
                        answer = satisfies(clauses.rows, values)
                        count += answer
                        full_assignments += 1
                        wrong_auxiliary_rejections += int(expected and not answer)
                    assert count == int(expected), (n, bound, equality, input_values, count)
                    accepted += count
                rows.append({"n": n, "bound": bound, "equality": equality, "variables": encoder.top,
                             "clauses": clauses.count, "accepted_full_assignments": accepted})
    assert wrong_auxiliary_rejections > 0
    return {"status": "PRODUCER_THRESHOLD_CONTROLS_PASS", "gate_input_cases": gate_cases,
            "exhaustive_counter_rows": rows, "full_assignments_checked": full_assignments,
            "wrong_auxiliary_assignments_rejected": wrong_auxiliary_rejections,
            "all_admissible_inputs_have_exactly_one_auxiliary_extension": True, "independent_review": False}


def decode(model, assignment):
    assert len(assignment) == model["variables"]
    assert all(type(v) is int and v != 0 for v in assignment)
    assert {abs(v) for v in assignment} == set(range(1, model["variables"] + 1))
    values = {abs(v): int(v > 0) for v in assignment}
    adjacency = [row.copy() for row in model["known_adjacency_full99"]]
    for item in model["edge_variables"]:
        adjacency[item["u"]][item["v"]] = adjacency[item["v"]][item["u"]] = values[item["id"]]
    checked = validate(adjacency, 99, 14, 1, 2)
    return {"adjacency_full99": adjacency, "producer_validation": checked,
            "independent_review_required": True, "scope_sha256": model["scope_sha256"]}


class ChunkWriter:
    def __init__(self, prefix, cap):
        self.prefix, self.cap = prefix, cap
        self.buffer = bytearray()
        self.parts = []
        self.limit = 9 * 1024 * 1024
        self.compressed_hash = sha256()

    def write(self, data):
        self.compressed_hash.update(data)
        self.buffer.extend(data)
        while len(self.buffer) >= self.limit:
            self.flush_part(self.limit)
        return len(data)

    def flush(self):
        return None

    def flush_part(self, count):
        path = Path(str(self.prefix) + f".part{len(self.parts):03d}")
        with path.open("xb") as target:
            target.write(self.buffer[:count])
        del self.buffer[:count]
        self.parts.append({"path": key(path), "bytes": path.stat().st_size, "sha256": digest(path)})
        self.cap.check()

    def finish(self):
        if self.buffer:
            self.flush_part(len(self.buffer))


def package(path, cap):
    writer = ChunkWriter(Path(str(path) + ".gz"), cap)
    with gzip.GzipFile(filename="", fileobj=writer, mode="wb", mtime=0) as target:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1048576), b""):
                target.write(chunk)
                cap.check()
    writer.finish()
    reproduced, raw_count = sha256(), 0
    decompressor = zlib.decompressobj(wbits=31)
    for part in writer.parts:
        with (ROOT / part["path"]).open("rb") as source:
            for chunk in iter(lambda: source.read(1048576), b""):
                raw = decompressor.decompress(chunk)
                reproduced.update(raw)
                raw_count += len(raw)
                cap.check()
    tail = decompressor.flush()
    reproduced.update(tail)
    raw_count += len(tail)
    assert decompressor.eof and not decompressor.unused_data
    assert raw_count == path.stat().st_size and reproduced.hexdigest() == digest(path)
    return {"raw_path": key(path), "raw_sha256": digest(path), "raw_bytes": path.stat().st_size,
            "compression": "gzip stream, mtime=0; concatenate ordered parts before decompression",
            "compressed_stream_sha256": writer.compressed_hash.hexdigest(), "ordered_parts": writer.parts,
            "producer_decompression_identity_passed": True, "max_part_bytes_exclusive": 10 * 1024 * 1024}


def build(args):
    args.out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    cap.check()
    bindings = [Path(__file__), PROTOCOL, Path(__file__).with_name("theory_20260930_full_srg_validator.py"),
        SCOPE, SCOPE_AUDIT, ROOT / "acceleration/environments/rook-sat/uv.lock",
        ROOT / "acceleration/environments/rook-sat/pyproject.toml"]
    manifest = {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "platform": platform.platform(), "uv_version": subprocess.check_output(["uv", "--version"], text=True).strip(),
        "input_hashes": {key(p): digest(p) for p in bindings},
        "question": "Build exact full99 equations for the pinned120fixedK eight-coordinate family with independently reconstructible prefix thresholds.",
        "scope": "189 fixed scaffold edges,120fixed outer edges,2160unknown outer edges, all other absences fixed; no target symmetry assumed.",
        "limits": {"build_seconds": 120, "working_set_bytes": 8 * 1024 ** 3, "solver_calls": 0},
        "status": "CANDIDATE_ENCODING_BUILD", "numerical_thresholds": None,
        "numerical_thresholds_null_reason": "Exact integer/Boolean arithmetic only.",
        "random_seed": None, "random_seed_null_reason": "Deterministic edge/pair/counter order.",
        "solver_imported": False, "third_party_cardinality_encoder_imported": False}
    save(args.out / "manifest.json", manifest)
    try:
        save(args.out / "counter_controls.json", counter_controls())
        save(args.out / "graph_validator_controls.json", graph_controls())
        cap.check()
        scope = json.loads(SCOPE.read_text())
        fixed = set(map(tuple, scope["remaining_fixed_K_edges_outer"]))
        unknown = set(map(tuple, scope["unknown_edges_outer"]))
        assert len(fixed) == 120 and len(unknown) == 2160 and not fixed & unknown
        labels = [(2 * a + s, 2 * b + t) for a, b in combinations(range(7), 2) for s in (0, 1) for t in (0, 1)]
        known = [[0] * 99 for _ in range(99)]
        def set_edge(u, v, value):
            known[u][v] = known[v][u] = value
        for s in range(1, 15):
            set_edge(0, s, 1)
        for s in range(1, 15, 2):
            set_edge(s, s + 1, 1)
        for u, label in enumerate(labels, 15):
            for s in label:
                set_edge(u, s + 1, 1)
        for u, v in fixed:
            set_edge(u + 15, v + 15, 1)
        for u, v in unknown:
            set_edge(u + 15, v + 15, -1)
        assert sum(row.count(1) for row in known) == 2 * (189 + 120)
        adjacency = [[bool(value) if value >= 0 else None for value in row] for row in known]
        edge_variables = []
        for u, v in combinations(range(99), 2):
            if known[u][v] == -1:
                variable = len(edge_variables) + 1
                adjacency[u][v] = adjacency[v][u] = variable
                edge_variables.append({"u": u, "v": v, "id": variable})
        assert len(edge_variables) == 2160
        counters, products = [], []
        body_path = args.out / "clauses.body"
        with body_path.open("xb") as body:
            clauses = Clauses(body, cap)
            encoder = Encoder(2160, clauses)
            for u in range(99):
                inputs = [reference for reference in adjacency[u] if type(reference) is int]
                constant = sum(reference is True for reference in adjacency[u])
                counters.append(encoder.counter(inputs, 14 - constant, True,
                    {"kind": "degree", "vertex": u, "original_bound": 14, "constant": constant}))
            for pair_index, (u, v) in enumerate(combinations(range(99), 2)):
                terms, constant = [], 0
                for w in range(99):
                    if w == u or w == v:
                        continue
                    a, b = adjacency[u][w], adjacency[v][w]
                    if a is False or b is False:
                        continue
                    if a is True and b is True:
                        constant += 1
                    elif a is True:
                        terms.append(b)
                    elif b is True:
                        terms.append(a)
                    else:
                        first = clauses.count + 1
                        reference = encoder.conjunction(a, b)
                        products.append({"id": reference, "left": a, "right": b,
                            "pair": [u, v], "center": w, "first_clause": first, "clause_count": 3})
                        terms.append(reference)
                edge = adjacency[u][v]
                if edge is True:
                    constant += 1
                elif type(edge) is int:
                    terms.append(edge)
                residual = 2 - constant
                assert residual >= 0
                # A cap with a bound larger than its term count is identically true.
                bound = min(residual, len(terms))
                counters.append(encoder.counter(terms, bound, False,
                    {"kind": "pair_cap", "pair": [u, v], "original_bound": 2,
                     "constant": constant, "residual_before_trivial_cap_fold": residual}))
                if pair_index % 500 == 0:
                    print(json.dumps({"state": "BUILDING_PAIR_CAPS", "completed_pairs": pair_index + 1,
                                      "variables": encoder.top, "clauses": clauses.count}), flush=True)
                    cap.check()
        cap.check()
        cnf = args.out / "instance.cnf"
        with cnf.open("xb") as destination, body_path.open("rb") as source:
            destination.write(f"p cnf {encoder.top} {clauses.count}\n".encode("ascii"))
            for chunk in iter(lambda: source.read(1048576), b""):
                destination.write(chunk)
                cap.check()
        model = {"schema": "EIGHT_FULL99_EXACT_PREFIX_CNF_V1", "scope_path": key(SCOPE),
            "scope_sha256": digest(SCOPE), "known_adjacency_full99": known, "outer_labels": labels,
            "fixed_scaffold_edges": 189, "fixed_K_edges": sorted(fixed),
            "unknown_edges_outer": sorted(unknown), "edge_variables": edge_variables,
            "product_variables": products, "counter_rows": counters,
            "variables": encoder.top, "clauses": clauses.count,
            "degree_rows": 99, "pair_cap_rows": 4851,
            "prefix_reference_format": "JSON booleans are constants; positive integers are SAT variable IDs.",
            "gate_clause_order": {"and": ["a -z", "b -z", "-a -b z"],
                "or": ["-a z", "-b z", "a b -z"],
                "a_or_b_and_c": ["-a z", "-b -c z", "a b -z", "a c -z"]},
            "clauses_constant_folded": True, "row_order": "99 degrees first; then lexicographic full99 unordered pairs; product centers ascending before each pair counter."}
        assert len(products) == 110640 and len(counters) == 4950
        model_path = args.out / "model.json"
        save(model_path, model)
        cap.check()
        all_false = [-variable for variable in range(1, encoder.top + 1)]
        rejected = decode(model, all_false)
        assert not rejected["producer_validation"]["valid"]
        save(args.out / "all_unknown_edges_false_control.json", rejected)
        packages = [package(path, cap) for path in (cnf, model_path)]
        save(args.out / "artifact_packages.json", {"packages": packages,
            "retrieval": "Concatenate each ordered gzip-part list byte-for-byte, verify compressed SHA256, then gzip-decompress and verify raw SHA256. Raw counterparts are local; parts are intended for repository publication."})
        cap.check()
        for path, expected in manifest["input_hashes"].items():
            assert digest(ROOT / path) == expected, path
        files = [p for p in args.out.iterdir() if p.is_file() and p.name != "clauses.body"]
        save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CANDIDATE_FULL99_ENCODING_PENDING_INDEPENDENT_GATE", "complete": True,
            "variables": encoder.top, "edge_variables": 2160, "product_variables": len(products),
            "prefix_variables": encoder.top - 2160 - len(products), "clauses": clauses.count,
            "degree_rows": 99, "pair_cap_rows": 4851, "solver_calls": 0,
            "elapsed_seconds": time.monotonic() - cap.start, "peak_working_set_bytes": cap.peak_bytes,
            "resource_samples": cap.samples, "target_resolution": False,
            "outputs": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in files},
            "limitations": ["Producer calibration is not independent encoding verification.",
                "This family retains120fixedK edges and prescribed absences; no unrestricted coverage claim.",
                "No solver result, graph witness or exclusion is claimed."]})
        print(json.dumps({"status": "CANDIDATE_FULL99_ENCODING_PENDING_INDEPENDENT_GATE", "variables": encoder.top,
                          "clauses": clauses.count, "seconds": time.monotonic() - cap.start}), flush=True)
    except BaseException as exc:
        save(args.out / "failure.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "INCOMPLETE_BUILD", "type": type(exc).__name__, "message": str(exc),
            "elapsed_seconds": time.monotonic() - cap.start, "peak_working_set_bytes": cap.peak_bytes,
            "solver_calls": 0})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--decode-model", type=Path)
    parser.add_argument("--assignment", type=Path)
    parser.add_argument("--decoded-out", type=Path)
    args = parser.parse_args()
    if args.decode_model:
        assert args.assignment and args.decoded_out and args.out is None
        assignment = json.loads(args.assignment.read_text())["assignment"]
        save(args.decoded_out, decode(json.loads(args.decode_model.read_text()), assignment))
    else:
        assert args.out and not args.assignment and not args.decoded_out
        build(args)


if __name__ == "__main__":
    main()
