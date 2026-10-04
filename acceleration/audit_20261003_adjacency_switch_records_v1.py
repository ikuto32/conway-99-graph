"""SOURCE_ONLY independent adjacency replacement / native prefix checker.

Author /root/native_driver. Prospective execution verifier /root.
No producer module, C++ kernel, parser or cache-update formula is imported.
This source does not launch a native process or emit the wrapper's controls gate.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parent.parent
WEIGHT = 819820
SOURCE_AUTHOR = "/root/native_driver"
EXECUTION_VERIFIER = "/root"
PRODUCER = "/root/structural"
SCHEMA = "INDEPENDENT_ADJACENCY_SWITCH_RECORDS_V1"
RECORD_KEYS = (
    "schema", "proposal_id", "edge1_index", "edge2_index", "u", "v", "x", "y",
    "orientation", "valid", "diagnostic", "affected_pairs", "delta_F3",
    "delta_lambda", "delta_mu", "delta_E", "delta_scalar", "final_metrics",
    "graph_delta_key",
)
ORDER = "edge1_index ascending, edge2_index ascending greater than edge1, orientation0 then1"
RESTART = "Preserve this prefix. A separately authorized new invocation restarts at0 in a fresh output root; V1 has no resume or automatic retry."
SOFTWARE = {
    "acceleration/adjacency_ternary_switch_kernel_20261003_v1.cpp": "b10b8a10691a15a1f0e4133944fc634b5d7ba36199a37da8f0c1bae3089fe541",
    "acceleration/adjacency_ternary_switch_kernel_20261003_v1_spec.md": "1b5844c669be85b420d33626c144f078ec15c66259c921c6e2b29a433709dc8c",
    "acceleration/census_20261003_adjacency_ternary_switch_v1.cpp": "6127b5c2aa400ad3f055d1266aec4eab6e5ea0869b609c65f7802342830eed18",
    "acceleration/prepare_20261003_adjacency_ternary_switch_census_v1.py": "7f6a69edc065ab868ef8a1536d11b2aa7482a8d26d7b06c8afdf259e7f33a43b",
    "acceleration/census_20261003_adjacency_ternary_switch_v1_spec.md": "7f2c13a5357217cdfbb182344bc1e5f2f242f1a7de5993fbc1fbf8cf88269916",
    "acceleration/plan_20261003_adjacency_ternary_switch_controls_v1.json": "df3bcbf5c39c0201f0c07e6f4c79f43a510a804df7a3e9d9e25cbcd69b38e8bd",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
}


def need(value, stage):
    if not value:
        raise ValueError(stage)


def exact(value, expected, stage):
    """Type-exact recursive comparison; bool/float aliases never equal int."""
    need(type(value) is type(expected), stage)
    if type(expected) is dict:
        need(value.keys() == expected.keys(), stage)
        for key in expected:
            exact(value[key], expected[key], stage)
    elif type(expected) in (list, tuple):
        need(len(value) == len(expected), stage)
        for a, b in zip(value, expected):
            exact(a, b, stage)
    else:
        need(value == expected, stage)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE_KEY")
            result[key] = value
        return result

    def nonfinite(_value):
        raise ValueError("JSON_NONFINITE")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def read_json(path):
    return strict_json(Path(path).read_text(encoding="utf-8"))


def digest(path, deadline=None):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(1024 * 1024):
            if deadline is not None:
                tick(deadline)
            result.update(block)
    if deadline is not None:
        tick(deadline)
    return result.hexdigest()


def tick(deadline):
    need(not deadline.status()["stop_required"], "CHECKER_DEADLINE")


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def literal_graph(raw, n, degree):
    """Independent byte parser: canonical decimal header and exact binary rows."""
    need(type(n) is int and type(degree) is int and 4 <= n <= 99 and 0 <= degree <= 14 and degree < n, "GRAPH_DIMENSIONS")
    need(type(raw) is bytes and b"\x00" not in raw, "INPUT_BYTES")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("INPUT_ASCII") from exc
    # Native accepts LF or CRLF, including a final row without its terminal LF.
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    lines = [line[:-1] if line.endswith("\r") else line for line in lines]
    need(lines and lines[0] == str(n), "INPUT_LITERAL_HEADER")
    need(len(lines) == n + 1, "INPUT_LINE_POPULATION")
    masks = []
    for line in lines[1:]:
        need(len(line) == n, "INPUT_ROW_LENGTH")
        need(all(c in "01" for c in line), "INPUT_LITERAL_BINARY")
        masks.append(sum((c == "1") << j for j, c in enumerate(line)))
    validate_masks(masks, n, degree)
    return masks


def validate_masks(rows, n, degree):
    need(type(rows) is list and len(rows) == n and all(type(row) is int and 0 <= row < (1 << n) for row in rows), "GRAPH_ROWS")
    for u, row in enumerate(rows):
        need(not ((row >> u) & 1), "GRAPH_DIAGONAL")
        need(row.bit_count() == degree, "GRAPH_DEGREE")
        for v in range(n):
            need(((row >> v) & 1) == ((rows[v] >> u) & 1), "GRAPH_SYMMETRY")


def graph_bytes(rows):
    n = len(rows)
    return (str(n) + "\n" + "\n".join("".join(str((row >> j) & 1) for j in range(n)) for row in rows) + "\n").encode("ascii")


def full_product(rows, scalar=False):
    """All n*n entries; scalar dot products are a separate calibration path."""
    n = len(rows)
    if scalar:
        matrix = [[(row >> v) & 1 for v in range(n)] for row in rows]
        return [[sum(matrix[u][w] * matrix[w][v] for w in range(n)) for v in range(n)] for u in range(n)]
    return [[(rows[u] & rows[v]).bit_count() for v in range(n)] for u in range(n)]


def score(rows, product=None):
    n = len(rows)
    f3 = e_lambda = e_mu = 0
    populations = [0, 0, 0]
    for u in range(n):
        for v in range(u + 1, n):
            cn = product[u][v] if product is not None else (rows[u] & rows[v]).bit_count()
            edge = (rows[u] >> v) & 1
            residual = cn + edge - 2
            residue = residual % 3
            populations[residue] += 1
            f3 += residue != 0
            if edge:
                e_lambda += residual * residual
            else:
                e_mu += residual * residual
    energy = e_lambda + e_mu
    return dict(F3=f3, E_lambda=e_lambda, E_mu=e_mu, E=energy,
                scalar_weight=WEIGHT, scalar=WEIGHT * f3 + energy,
                residue_population=populations)


def edges(rows):
    return [(u, v) for u in range(len(rows)) for v in range(u + 1, len(rows)) if (rows[u] >> v) & 1]


def labels(rows):
    old = edges(rows)
    pid = 0
    for i in range(len(old)):
        for j in range(i + 1, len(old)):
            for orientation in (0, 1):
                yield pid, i, j, (*old[i], *old[j], orientation)
                pid += 1


def replacement(rows, role):
    """Whole adjacency replacement, without an incremental CN update."""
    n = len(rows)
    u, v, x, y, orientation = role
    if any(type(z) is not int or z < 0 or z >= n for z in (u, v, x, y)):
        return "ROLE_VERTEX_RANGE", None, None
    if type(orientation) is not int or orientation not in (0, 1):
        return "ROLE_ORIENTATION", None, None
    if not (u < v and x < y and (u, v) < (x, y)):
        return "ROLE_CANONICAL_OLD_EDGES", None, None
    if len({u, v, x, y}) != 4:
        return "ROLE_FOUR_DISTINCT_VERTICES", None, None
    if not ((rows[u] >> v) & 1 and (rows[x] >> y) & 1):
        return "ROLE_OLD_EDGE_ABSENT", None, None
    added = ((u, x), (v, y)) if orientation == 0 else ((u, y), (v, x))
    if any((rows[a] >> b) & 1 for a, b in added):
        return "ROLE_NEW_EDGE_PRESENT", None, None
    candidate = rows.copy()
    for a, b in ((u, v), (x, y)):
        candidate[a] &= ~(1 << b)
        candidate[b] &= ~(1 << a)
    for a, b in added:
        candidate[a] |= 1 << b
        candidate[b] |= 1 << a
    validate_masks(candidate, n, rows[0].bit_count())
    new_edges = sorted(tuple(sorted(pair)) for pair in added)
    key = [u, v, x, y, *new_edges[0], *new_edges[1]]
    return "VALID_SWITCH_PENDING_INDEPENDENT_CHECK", candidate, key


def expected_record(rows, label, baseline):
    pid, i, j, role = label
    diagnostic, candidate, key = replacement(rows, role)
    valid = candidate is not None
    final = score(candidate) if valid else None
    result = dict(schema="ADJACENCY_TERNARY_SWITCH_RECORD_V1", proposal_id=pid,
                  edge1_index=i, edge2_index=j, u=role[0], v=role[1], x=role[2], y=role[3], orientation=role[4],
                  valid=valid, diagnostic=diagnostic, affected_pairs=4 * len(rows) - 10 if valid else 0,
                  delta_F3=final["F3"] - baseline["F3"] if valid else 0,
                  delta_lambda=final["E_lambda"] - baseline["E_lambda"] if valid else 0,
                  delta_mu=final["E_mu"] - baseline["E_mu"] if valid else 0,
                  delta_E=final["E"] - baseline["E"] if valid else 0,
                  delta_scalar=final["scalar"] - baseline["scalar"] if valid else 0,
                  final_metrics=final, graph_delta_key=key)
    return result, candidate


def compare_record(raw, expected):
    need(type(raw) is dict and set(raw) == set(RECORD_KEYS), "RECORD_KEYS")
    for key in RECORD_KEYS:
        exact(raw[key], expected[key], "RECORD_FIELD:" + key)


class Aggregate:
    def __init__(self):
        self.processed = self.valid = self.invalid = self.zeros = 0
        self.rejections = {}
        self.keys = set()
        self.min_f3 = self.min_metrics = None
        self.f3_ties = []
        self.pair_ties = []
        self.selected_record = self.selected_graph = None
        self.zero_graphs = {}

    def add(self, record, candidate):
        self.processed += 1
        if not record["valid"]:
            self.invalid += 1
            diagnostic = record["diagnostic"]
            self.rejections[diagnostic] = self.rejections.get(diagnostic, 0) + 1
            return
        self.valid += 1
        self.keys.add(tuple(record["graph_delta_key"]))
        metric = record["final_metrics"]
        pid = record["proposal_id"]
        if self.min_f3 is None or metric["F3"] < self.min_f3:
            self.min_f3, self.f3_ties = metric["F3"], []
        if metric["F3"] == self.min_f3:
            self.f3_ties.append(pid)
        pair = (metric["F3"], metric["E"])
        old_pair = None if self.min_metrics is None else (self.min_metrics["F3"], self.min_metrics["E"])
        if old_pair is None or pair < old_pair:
            self.min_metrics, self.pair_ties = deepcopy(metric), []
            self.selected_record, self.selected_graph = deepcopy(record), graph_bytes(candidate)
        if pair == (self.min_metrics["F3"], self.min_metrics["E"]):
            self.pair_ties.append(pid)
        if metric["F3"] == 0:
            self.zeros += 1
            self.zero_graphs[pid] = graph_bytes(candidate)

    def json(self):
        return dict(processed=self.processed, valid_labels=self.valid, invalid_labels=self.invalid,
                    unique_valid_graphs=len(self.keys), raw_zero_neighbors=self.zeros,
                    rejection_counts=dict(sorted(self.rejections.items())), minimum_F3=self.min_f3,
                    minimum_pair_metrics=self.min_metrics, minimum_F3_tie_ids=self.f3_ties,
                    minimum_pair_tie_ids=self.pair_ties)


def check_native(native, input_path, n, degree, input_sha, source_context, mode, expected_complete, deadline):
    """Check one finished native directory or its closed cooperative prefix.

    The caller supplies exact raw identity. This is not a wrapper/containment gate.
    Partial tails remain unapproved and are only reported, never parsed as records.
    """
    native, input_path = Path(native), Path(input_path)
    need(digest(input_path, deadline) == input_sha, "INPUT_SHA256")
    rows = literal_graph(input_path.read_bytes(), n, degree)
    baseline = score(rows)
    tick(deadline)
    manifest = read_json(native / "manifest.json")
    need(type(manifest) is dict, "MANIFEST_SCHEMA")
    fixed = dict(schema="ADJACENCY_TERNARY_SWITCH_CENSUS_V1", mode=mode,
                 objective="SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1", move_kernel="FOUR_DISTINCT_VERTEX_EDGE_SWITCH_V1",
                 input_sha256=input_sha, source_context=source_context, start_proposal_id=0,
                 expected_labels=len(edges(rows)) * (len(edges(rows)) - 1), all_mutable=True, rng_used=False,
                 input_metrics=baseline, target_resolution="NONE", independent_approval=False,
                 overall_search_coverage="UNKNOWN", resume_supported=False)
    variable = {"status", "stop_proposal_id", "full_universe_processed", "aggregates", "closed_parts",
                "closed_checkpoints", "selected_proposal_id", "strict_improvement_candidate", "stop_reason",
                "elapsed_seconds", "allocated_native_seconds", "internal_save_seconds"}
    need(set(manifest) == set(fixed) | variable, "MANIFEST_KEYS")
    for key, value in fixed.items():
        exact(manifest[key], value, "MANIFEST_FIELD:" + key)
    stop = manifest["stop_proposal_id"]
    need(type(stop) is int and 0 <= stop <= fixed["expected_labels"], "MANIFEST_STOP")
    complete = stop == fixed["expected_labels"]
    exact(manifest["full_universe_processed"], complete, "MANIFEST_COMPLETE")
    exact(manifest["status"], "COMPLETE_CANDIDATE_PENDING_INDEPENDENT_FULL_REPLAY" if complete else "NOT_COMPLETED_WITH_ALLOCATED_BUDGET", "MANIFEST_STATUS")
    exact(complete, expected_complete, "REQUESTED_COMPLETE_SCOPE")
    need(type(manifest["stop_reason"]) is str and manifest["stop_reason"] in (
        "COMPLETE_DECLARED_LABEL_UNIVERSE", "SIGNAL_STOP", "REASSESSMENT_STOP_BEFORE1800", "COOPERATIVE_DEADLINE_STOP"), "MANIFEST_STOP_REASON")
    if complete:
        exact(manifest["stop_reason"], "COMPLETE_DECLARED_LABEL_UNIVERSE", "MANIFEST_STOP_REASON")
    for key in ("elapsed_seconds", "allocated_native_seconds", "internal_save_seconds"):
        value = manifest[key]
        need(type(value) in (int, float) and 0 <= value < float("inf"), "MANIFEST_TIME:" + key)
    need(manifest["allocated_native_seconds"] > manifest["internal_save_seconds"] > 0, "MANIFEST_SAVE_RESERVE")
    expected_universe = dict(schema="ADJACENCY_TERNARY_SWITCH_UNIVERSE_V1", n=n, degree=degree,
                             expected_labels=fixed["expected_labels"], old_edges=[list(pair) for pair in edges(rows)],
                             order=ORDER, all_mutable=True)
    exact(read_json(native / "universe.json"), expected_universe, "UNIVERSE_EXACT")
    need((native / "input_graph.adj").read_bytes() == graph_bytes(rows), "CANONICAL_INPUT_MATRIX")
    parts = (stop + 4999) // 5000
    exact(manifest["closed_parts"], parts, "MANIFEST_PARTS")
    exact(manifest["closed_checkpoints"], parts, "MANIFEST_CHECKPOINTS")
    aggregate = Aggregate()
    label_stream = labels(rows)
    expected_paths = {"manifest.json", "universe.json", "input_graph.adj"}
    for part_index in range(parts):
        tick(deadline)
        count = min(5000, stop - aggregate.processed)
        start = aggregate.processed
        filename = "part_" + str(part_index) + ".jsonl"
        expected_paths.add(filename)
        with (native / filename).open("r", encoding="utf-8", newline="") as stream:
            raw = stream.readline()
            need(raw.endswith("\n"), "PART_HEADER_LINE")
            exact(strict_json(raw), dict(schema="ADJACENCY_TERNARY_SWITCH_PART_HEADER_V1", part_index=part_index,
                                         start_proposal_id=start, maximum_records=5000), "PART_HEADER")
            for _ in range(count):
                tick(deadline)
                line = stream.readline()
                need(line.endswith("\n"), "PART_RECORD_LINE")
                expected, candidate = expected_record(rows, next(label_stream), baseline)
                compare_record(strict_json(line), expected)
                aggregate.add(expected, candidate)
            footer = stream.readline()
            need(footer.endswith("\n"), "PART_FOOTER_LINE")
            exact(strict_json(footer), dict(schema="ADJACENCY_TERNARY_SWITCH_PART_FOOTER_V1",
                                           stop_proposal_id=aggregate.processed, record_count=count), "PART_FOOTER")
            need(stream.read() == "", "PART_EXTRA_BYTES")
        cp_name = "checkpoint_" + str(aggregate.processed) + ".json"
        expected_paths.add(cp_name)
        expected_cp = dict(schema="ADJACENCY_TERNARY_SWITCH_PREFIX_CHECKPOINT_V1", start_proposal_id=0,
                           next_proposal_id=aggregate.processed, part_index=part_index, last_closed_part=filename,
                           input_sha256=input_sha, aggregates=aggregate.json(), resume_supported=False,
                           restart_instruction=RESTART)
        exact(read_json(native / cp_name), expected_cp, "CHECKPOINT_EXACT")
    exact(manifest["aggregates"], aggregate.json(), "MANIFEST_AGGREGATES")
    exact(manifest["selected_proposal_id"], aggregate.pair_ties[0] if aggregate.pair_ties else None, "MANIFEST_SELECTED")
    improvement = aggregate.min_metrics is not None and (aggregate.min_metrics["F3"], aggregate.min_metrics["E"]) < (baseline["F3"], baseline["E"])
    exact(manifest["strict_improvement_candidate"], improvement, "MANIFEST_IMPROVEMENT")
    if aggregate.min_metrics is not None:
        expected_paths.update(("selected_neighbor.adj", "selected_neighbor.json"))
        exact(read_json(native / "selected_neighbor.json"), aggregate.selected_record, "SELECTED_RECORD")
        need((native / "selected_neighbor.adj").read_bytes() == aggregate.selected_graph, "SELECTED_MATRIX")
        selected_rows = literal_graph(aggregate.selected_graph, n, degree)
        exact(full_product(selected_rows), full_product(selected_rows, scalar=True), "SELECTED_FULL_SCALAR_PRODUCT")
    for pid, raw_graph in aggregate.zero_graphs.items():
        path = "raw_zero_neighbor_" + str(pid) + ".adj"
        expected_paths.add(path)
        need((native / path).read_bytes() == raw_graph, "RAW_ZERO_MATRIX")
    # A stopped manifest does not authenticate any open partial tail.
    actual_paths = {path.name for path in native.iterdir() if path.is_file()}
    partials = {name for name in actual_paths if re.fullmatch(r"part_\d+\.jsonl\.partial", name)}
    need(not any(path.is_dir() or path.is_symlink() for path in native.iterdir()), "NATIVE_DIRECTORY_TYPE")
    need(not complete or not partials, "COMPLETE_PARTIAL_TAIL")
    need(actual_paths - partials == expected_paths, "NATIVE_EXACT_FILE_POPULATION")
    identity = {name: digest(native / name, deadline) for name in sorted(actual_paths)}
    need(digest(input_path, deadline) == input_sha, "INPUT_CLOSING_SHA256")
    tick(deadline)
    return dict(n=n, degree=degree, complete=complete, records_checked=stop, record_fields_checked=19,
                parts_checked=parts, checkpoints_checked=parts, aggregate=aggregate.json(),
                baseline_metrics=baseline, strict_improvement=improvement, selected_proposal_id=manifest["selected_proposal_id"],
                partial_tail_files_not_approved=sorted(partials), native_output_sha256=identity,
                wrapper_receipt_checked=False, native_API_cache_rollback_reverse_probes_checked=False,
                containment_checked=False, target_resolution="NONE")


def fixture(name):
    if name == "rook9":
        n, degree = 9, 4
        adjacent = lambda u, v: u != v and (u // 3 == v // 3 or u % 3 == v % 3)
    elif name == "triangular_prism6":
        n, degree = 6, 3
        adjacent = lambda u, v: u != v and (u // 3 == v // 3 or abs(u - v) == 3)
    elif name == "cube8":
        n, degree = 8, 3
        adjacent = lambda u, v: (u ^ v).bit_count() == 1
    elif name == "synthetic99_14":
        n, degree = 99, 14
        adjacent = lambda u, v: (u - v) % 99 in tuple(range(1, 8)) + tuple(range(92, 99))
    else:
        raise ValueError("FIXTURE_NAME")
    rows = [sum(int(adjacent(u, v)) << v for v in range(n)) for u in range(n)]
    validate_masks(rows, n, degree)
    return rows, degree


def synthetic_native(parent, rows, degree, stop):
    """Own framing fixtures; not observations of a native process."""
    parent.mkdir()
    native = parent / "native"
    native.mkdir()
    input_path = parent / "input.adj"
    input_path.write_bytes(graph_bytes(rows))
    input_sha = digest(input_path)
    old_edges = edges(rows)
    total = len(old_edges) * (len(old_edges) - 1)
    complete = stop == total
    context = "0" * 40
    (native / "input_graph.adj").write_bytes(graph_bytes(rows))
    write_json(native / "universe.json", dict(schema="ADJACENCY_TERNARY_SWITCH_UNIVERSE_V1", n=len(rows), degree=degree,
               expected_labels=total, old_edges=[list(pair) for pair in old_edges], order=ORDER, all_mutable=True))
    baseline = score(rows)
    aggregate = Aggregate()
    stream = labels(rows)
    part_count = (stop + 4999) // 5000
    for index in range(part_count):
        count = min(5000, stop - aggregate.processed)
        start = aggregate.processed
        filename = "part_" + str(index) + ".jsonl"
        lines = [dict(schema="ADJACENCY_TERNARY_SWITCH_PART_HEADER_V1", part_index=index,
                      start_proposal_id=start, maximum_records=5000)]
        for _ in range(count):
            record, candidate = expected_record(rows, next(stream), baseline)
            lines.append(record)
            aggregate.add(record, candidate)
        lines.append(dict(schema="ADJACENCY_TERNARY_SWITCH_PART_FOOTER_V1", stop_proposal_id=aggregate.processed, record_count=count))
        (native / filename).write_text("".join(json.dumps(line, separators=(",", ":"), allow_nan=False) + "\n" for line in lines), encoding="utf-8", newline="\n")
        write_json(native / ("checkpoint_" + str(aggregate.processed) + ".json"), dict(
            schema="ADJACENCY_TERNARY_SWITCH_PREFIX_CHECKPOINT_V1", start_proposal_id=0,
            next_proposal_id=aggregate.processed, part_index=index, last_closed_part=filename,
            input_sha256=input_sha, aggregates=aggregate.json(), resume_supported=False, restart_instruction=RESTART))
    if aggregate.min_metrics is not None:
        (native / "selected_neighbor.adj").write_bytes(aggregate.selected_graph)
        write_json(native / "selected_neighbor.json", aggregate.selected_record)
    for pid, raw in aggregate.zero_graphs.items():
        (native / ("raw_zero_neighbor_" + str(pid) + ".adj")).write_bytes(raw)
    write_json(native / "manifest.json", dict(schema="ADJACENCY_TERNARY_SWITCH_CENSUS_V1",
        status="COMPLETE_CANDIDATE_PENDING_INDEPENDENT_FULL_REPLAY" if complete else "NOT_COMPLETED_WITH_ALLOCATED_BUDGET",
        mode="fixture", objective="SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1", move_kernel="FOUR_DISTINCT_VERTEX_EDGE_SWITCH_V1",
        input_sha256=input_sha, source_context=context, start_proposal_id=0, stop_proposal_id=stop,
        expected_labels=total, full_universe_processed=complete, all_mutable=True, rng_used=False,
        input_metrics=baseline, aggregates=aggregate.json(), closed_parts=part_count, closed_checkpoints=part_count,
        selected_proposal_id=aggregate.pair_ties[0] if aggregate.pair_ties else None,
        strict_improvement_candidate=aggregate.min_metrics is not None and
            (aggregate.min_metrics["F3"], aggregate.min_metrics["E"]) < (baseline["F3"], baseline["E"]),
        stop_reason="COMPLETE_DECLARED_LABEL_UNIVERSE" if complete else "SIGNAL_STOP", elapsed_seconds=0.01,
        allocated_native_seconds=10.0, internal_save_seconds=1.0, target_resolution="NONE", independent_approval=False,
        overall_search_coverage="UNKNOWN", resume_supported=False))
    return native, input_path, input_sha, context


def mutate_json(path, change):
    obj = read_json(path)
    change(obj)
    path.write_text(json.dumps(obj, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def mutate_part(path, change):
    lines = [strict_json(line) for line in path.read_text(encoding="utf-8").splitlines()]
    change(lines)
    path.write_text("".join(json.dumps(line, allow_nan=False) + "\n" for line in lines), encoding="utf-8", newline="\n")


def own_calibration(out, deadline):
    """Independent math/schema controls only; no producer output/native call."""
    positives = []
    labels_checked = full_candidate_matrices = 0
    for name, population, shared in (("rook9", 306, 108), ("triangular_prism6", 72, 36), ("cube8", 132, 48)):
        tick(deadline)
        rows, degree = fixture(name)
        exact(literal_graph(graph_bytes(rows), len(rows), degree), rows, "CAL_GRAPH_ROUNDTRIP")
        bit_product, scalar_product = full_product(rows), full_product(rows, scalar=True)
        exact(bit_product, scalar_product, "CAL_BASE_FULL_PRODUCT")
        baseline = score(rows)
        exact(baseline, score(rows, scalar_product), "CAL_BASE_SCORE")
        aggregate = Aggregate()
        local_shared = 0
        records = []
        for label in labels(rows):
            tick(deadline)
            record, candidate = expected_record(rows, label, baseline)
            records.append(record)
            aggregate.add(record, candidate)
            labels_checked += 1
            local_shared += record["diagnostic"] == "ROLE_FOUR_DISTINCT_VERTICES"
            if candidate is not None:
                a, b = full_product(candidate), full_product(candidate, scalar=True)
                exact(a, b, "CAL_CANDIDATE_FULL_PRODUCT")
                exact(record["final_metrics"], score(candidate, b), "CAL_CANDIDATE_SCORE")
                full_candidate_matrices += 1
                # Direct inverse whole replacement; this is our own oracle, not a native API branch.
                original = candidate.copy()
                u, v, x, y, orientation = label[3]
                added = ((u, x), (v, y)) if orientation == 0 else ((u, y), (v, x))
                for p, q in added:
                    original[p] &= ~(1 << q)
                    original[q] &= ~(1 << p)
                for p, q in ((u, v), (x, y)):
                    original[p] |= 1 << q
                    original[q] |= 1 << p
                exact(original, rows, "CAL_WHOLE_REVERSE")
        exact(aggregate.processed, population, "CAL_LABEL_POPULATION")
        exact(local_shared, shared, "CAL_SHARED_ENDPOINT_POPULATION")
        exact(aggregate.valid, len(aggregate.keys), "CAL_KEY_INJECTION")
        write_json(out / (name + "_expected_records.json"), records)
        positives.append(dict(name=name, labels=population, shared_endpoint_labels=shared, aggregate=aggregate.json()))
    rows, degree = fixture("synthetic99_14")
    a, b = full_product(rows), full_product(rows, scalar=True)
    exact(a, b, "CAL_SYNTHETIC99_FULL_PRODUCT")
    baseline = score(rows, b)
    for orientation in (0, 1):
        stage, candidate, _key = replacement(rows, (0, 1, 20, 21, orientation))
        exact(stage, "VALID_SWITCH_PENDING_INDEPENDENT_CHECK", "CAL_SYNTHETIC99_PROBE_VALID")
        exact(full_product(candidate), full_product(candidate, scalar=True), "CAL_SYNTHETIC99_PROBE_PRODUCT")
        need(score(candidate)["scalar"] == WEIGHT * score(candidate)["F3"] + score(candidate)["E"], "CAL_TARGET_WEIGHT")
    positives.append(dict(name="synthetic99_14", baseline_metrics=baseline, full_matrix_entries=9801,
                          full_probe_matrices=2, actual_target_graph_read=False))
    # Typed, field-local wire controls. File/population/receipt corruptions require a
    # separately frozen actual author harness and are not counted by this calibration.
    rows, _degree = fixture("rook9")
    baseline = score(rows)
    candidates = [expected_record(rows, label, baseline)[0] for label in labels(rows)]
    reference = next(record for record in candidates if record["valid"])
    invalid = next(record for record in candidates if not record["valid"])
    negatives = []
    cases = []
    for field in ("proposal_id", "edge1_index", "edge2_index", "orientation", "affected_pairs", "delta_F3", "delta_lambda", "delta_mu", "delta_E", "delta_scalar"):
        for kind in ("boolean", "float"):
            raw = deepcopy(reference)
            raw[field] = bool(raw[field]) if kind == "boolean" else float(raw[field])
            cases.append((field + "_" + kind, raw, reference, "RECORD_FIELD:" + field))
    raw = deepcopy(reference); raw["final_metrics"]["F3"] += 1
    cases.append(("wrong_final_F3", raw, reference, "RECORD_FIELD:final_metrics"))
    raw = deepcopy(reference); raw["graph_delta_key"][0] = False
    cases.append(("boolean_graph_key", raw, reference, "RECORD_FIELD:graph_delta_key"))
    raw = deepcopy(invalid); raw["final_metrics"] = deepcopy(reference["final_metrics"])
    cases.append(("forged_invalid_score", raw, invalid, "RECORD_FIELD:final_metrics"))
    raw = deepcopy(reference); raw.pop("delta_E")
    cases.append(("missing_record_key", raw, reference, "RECORD_KEYS"))
    for name, raw, expected, wanted in cases:
        tick(deadline)
        try:
            compare_record(raw, expected)
        except ValueError as exc:
            actual = str(exc)
        else:
            actual = "ACCEPTED_CORRUPTION"
        exact(actual, wanted, "CAL_NEGATIVE_STAGE:" + name)
        negatives.append(dict(name=name, expected_stage=wanted, actual_stage=actual))
    # Genuine on-disk synthetic stream checking, separately scoped from real native
    # controls. This exercises the complete prefix reader/CP/tie/file-population path.
    stream_positives = []
    for name in ("rook9", "triangular_prism6", "cube8"):
        rows, degree = fixture(name)
        population = len(edges(rows)) * (len(edges(rows)) - 1)
        for stop in (17, population):
            parent = out / (name + "_synthetic_" + str(stop))
            native, raw_input, input_sha, context = synthetic_native(parent, rows, degree, stop)
            result = check_native(native, raw_input, len(rows), degree, input_sha, context, "fixture", stop == population, deadline)
            stream_positives.append(dict(name=name, synthetic_prefix=stop, result=result))
    rows, degree = fixture("cube8")
    population = len(edges(rows)) * (len(edges(rows)) - 1)
    raw_cases = [
        ("manifest_stop_boolean", "MANIFEST_STOP", lambda p: mutate_json(p / "manifest.json", lambda o: o.update(stop_proposal_id=False))),
        ("manifest_complete_integer", "MANIFEST_COMPLETE", lambda p: mutate_json(p / "manifest.json", lambda o: o.update(full_universe_processed=1))),
        ("manifest_closed_parts_float", "MANIFEST_PARTS", lambda p: mutate_json(p / "manifest.json", lambda o: o.update(closed_parts=1.0))),
        ("part_header_start_boolean", "PART_HEADER", lambda p: mutate_part(p / "part_0.jsonl", lambda o: o[0].update(start_proposal_id=False))),
        ("part_header_index_float", "PART_HEADER", lambda p: mutate_part(p / "part_0.jsonl", lambda o: o[0].update(part_index=0.0))),
        ("part_record_id_boolean", "RECORD_FIELD:proposal_id", lambda p: mutate_part(p / "part_0.jsonl", lambda o: o[1].update(proposal_id=False))),
        ("part_duplicate_id", "RECORD_FIELD:proposal_id", lambda p: mutate_part(p / "part_0.jsonl", lambda o: o[2].update(proposal_id=0))),
        ("part_swapped_orientation", "RECORD_FIELD:orientation", lambda p: mutate_part(p / "part_0.jsonl", lambda o: o[1].update(orientation=1))),
        ("part_footer_count_float", "PART_FOOTER", lambda p: mutate_part(p / "part_0.jsonl", lambda o: o[-1].update(record_count=float(population)))),
        ("checkpoint_next_boolean", "CHECKPOINT_EXACT", lambda p: mutate_json(p / ("checkpoint_" + str(population) + ".json"), lambda o: o.update(next_proposal_id=True))),
        ("checkpoint_processed_float", "CHECKPOINT_EXACT", lambda p: mutate_json(p / ("checkpoint_" + str(population) + ".json"), lambda o: o["aggregates"].update(processed=float(population)))),
        ("checkpoint_tie_drop", "CHECKPOINT_EXACT", lambda p: mutate_json(p / ("checkpoint_" + str(population) + ".json"), lambda o: o["aggregates"].update(minimum_pair_tie_ids=[]))),
        ("manifest_unique_wrong", "MANIFEST_AGGREGATES", lambda p: mutate_json(p / "manifest.json", lambda o: o["aggregates"].update(unique_valid_graphs=-1))),
        ("manifest_selected_wrong", "MANIFEST_SELECTED", lambda p: mutate_json(p / "manifest.json", lambda o: o.update(selected_proposal_id=-1))),
        ("selected_matrix_flip", "SELECTED_MATRIX", lambda p: (p / "selected_neighbor.adj").write_bytes(b"corrupt\n")),
        ("unexpected_payload", "NATIVE_EXACT_FILE_POPULATION", lambda p: (p / "extra.bin").write_bytes(b"unapproved")),
        ("complete_partial_tail", "COMPLETE_PARTIAL_TAIL", lambda p: (p / "part_1.jsonl.partial").write_bytes(b"preserved open tail")),
    ]
    for name, wanted, change in raw_cases:
        tick(deadline)
        parent = out / ("corrupt_" + name)
        native, raw_input, input_sha, context = synthetic_native(parent, rows, degree, population)
        change(native)
        try:
            check_native(native, raw_input, len(rows), degree, input_sha, context, "fixture", True, deadline)
        except ValueError as exc:
            actual = str(exc)
        else:
            actual = "ACCEPTED_CORRUPTION"
        exact(actual, wanted, "CAL_RAW_NEGATIVE_STAGE:" + name)
        negatives.append(dict(name=name, expected_stage=wanted, actual_stage=actual, actual_saved_stream=True))
    write_json(out / "own_negative_records.json", negatives)
    tick(deadline)
    return dict(status="INDEPENDENT_ADJACENCY_SWITCH_RECORDS_V1_OWN_CALIBRATION_PASS",
                positive_fixture_scopes=positives, unique_fixture_labels=labels_checked,
                full_candidate_matrices=full_candidate_matrices, strict_negative_cases=len(negatives),
                strict_record_field_negative_cases=len(cases),
                own_synthetic_stream_positive_cases=stream_positives,
                actual_saved_synthetic_stream_negative_cases=len(raw_cases),
                native_calls=0, producer_output_read=False, actual_target_input_read=False,
                author_kernel_control_gate_emitted=False, author_API_branches_approved=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "native-prefix"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--native-dir")
    parser.add_argument("--input")
    parser.add_argument("--input-sha256")
    parser.add_argument("--n", type=int)
    parser.add_argument("--degree", type=int)
    parser.add_argument("--source-context")
    parser.add_argument("--native-mode", choices=("fixture", "target"))
    parser.add_argument("--expect-complete", choices=("true", "false"))
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="New independent exact adjacency reconstruction and raw native-prefix checking; every hash/check/save shares one invocation.")
    out = Path(args.out).resolve()
    need(out.is_relative_to((ROOT / "acceleration/results").resolve()) and not out.exists(), "OUTPUT_NAMESPACE_OR_EXISTS")
    out.mkdir(parents=True)
    inputs = dict(SOFTWARE)
    inputs[Path(__file__).resolve().relative_to(ROOT).as_posix()] = digest(__file__, deadline)
    spec = ROOT / "acceleration/audit_20261003_adjacency_switch_records_v1_spec.md"
    inputs[spec.relative_to(ROOT).as_posix()] = digest(spec, deadline)
    try:
        for relative, expected in SOFTWARE.items():
            need(digest(ROOT / relative, deadline) == expected, "SOFTWARE_PIN:" + relative)
        if args.mode == "calibrate":
            result = own_calibration(out, deadline)
        else:
            need(all(value is not None for value in (args.native_dir, args.input, args.input_sha256, args.n,
                 args.degree, args.source_context, args.native_mode, args.expect_complete)), "NATIVE_PREFIX_OPTIONS")
            need(re.fullmatch(r"[0-9a-f]{64}", args.input_sha256) is not None and re.fullmatch(r"[0-9a-f]{40}", args.source_context) is not None, "RAW_IDENTITIES")
            result = check_native(args.native_dir, args.input, args.n, args.degree, args.input_sha256,
                                  args.source_context, args.native_mode, args.expect_complete == "true", deadline)
            result["status"] = "INDEPENDENT_ADJACENCY_SWITCH_RECORDS_V1_NATIVE_PREFIX_PASS"
            inputs[Path(args.input).resolve().relative_to(ROOT).as_posix()] = args.input_sha256
            for name, identity in result["native_output_sha256"].items():
                inputs[(Path(args.native_dir).resolve() / name).relative_to(ROOT).as_posix()] = identity
        result.update(schema=SCHEMA, producer=PRODUCER, verifier=EXECUTION_VERIFIER,
                      source_author=SOURCE_AUTHOR, method="independent_artifact_check", target_resolution="NONE",
                      timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs,
                      protected_mutable_state_in_immutable_map=False,
                      canonical_wrapper_controls_gate_emitted=False,
                      elapsed_seconds=deadline.status()["elapsed_seconds"], limitations=[
                          "No producer module, parser, native binary or incremental cache formula imported.",
                          "Single native-directory prefix scope only; no wrapper/UID/containment/API-branch approval.",
                          "No historical gate transfers and no target/global optimum or graph-space coverage claim.",
                          "Prospective verifier role /root is truthful only for a separately authorized ROOT execution."])
        for relative, identity in inputs.items():
            need(digest(ROOT / relative, deadline) == identity, "CLOSING_INPUT_PIN:" + relative)
        tick(deadline)
        write_json(out / "summary.json", result)
        tick(deadline)
        return 0
    except Exception as exc:
        if (out / "summary.json").exists():
            (out / "summary.json").rename(out / "summary.not_approved.json")
        write_json(out / "failure.json", dict(schema=SCHEMA, status="FAILED_NOT_APPROVED",
                   exception=type(exc).__name__, diagnostic=str(exc), elapsed_seconds=deadline.status()["elapsed_seconds"],
                   target_resolution="NONE", canonical_wrapper_controls_gate_emitted=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
