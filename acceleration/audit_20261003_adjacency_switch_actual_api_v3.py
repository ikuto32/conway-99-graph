"""SOURCE_ONLY independent decoder of literal actual native Graph getter probes.

Checking-source author Native; prospective execution verifier ROOT. This imports
only the separately qualified independent record oracle, never producer code.
It emits an API-packet status, not the wrapper's combined controls gate.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import re
import sys

import audit_20261003_adjacency_switch_records_v1 as R
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
PINS = {
    "acceleration/audit_20261003_adjacency_switch_records_v1.py": "51fee63d5b7a2ea1fe4eb13c2fdde6750d937297a39087e71493788205d5a19a",
    "acceleration/audit_20261003_adjacency_switch_records_v1_spec.md": "d311f94931f3e496c94e06e6e54953c3e4f390eaef3d92b8c5cdb6d8b5496104",
    "acceleration/probe_20261003_adjacency_ternary_switch_api_v3.cpp": "9008e9f26826e3fa518f3e5c554babeba7d9f2baed49470a6eb4a894c761a6dc",
    "acceleration/probe_20261003_adjacency_ternary_switch_api_v1_spec.md": "93f742b4757c499a2288c664f387a14c54b9f07165a91899284b86b06638be58",
    "acceleration/adjacency_ternary_switch_kernel_20261003_v2.cpp": "ce35a195796266753cc123064e34a9bf0a9bda1880932576010089031bccba47",
    "acceleration/adjacency_switch_cpp_20261003_v2_compile_spec.md": "ad558d8757464cc0c5b0640b0281496f10ea7e445eb0a6711c9d94decd710d7e",
    "acceleration/adjacency_switch_api_20261003_v3_compile_spec.md": "fa717829267434809c51c87d5cd8e619cc188efca75e53ce6db24317a3d96c7c",
    "acceleration/diff_20261003_adjacency_switch_api_v2_v3.txt": "009e4c8d25473f024151d498729e9a30d3407c6fbfd51a25abdfb03a7b74383e",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "acceleration/run_compute_command_v2_spec.md": "33e242b6dc28fa783b29825b76311fdc36d16f5cdf1897ca3b41671cafc1acc1",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
FIXTURES = ("rook9", "triangular_prism6", "cube8", "synthetic99_14")
PROBE_SCHEMA = "ADJACENCY_TERNARY_SWITCH_NATIVE_API_PROBE_V1"
KERNEL_SHA = PINS["acceleration/adjacency_ternary_switch_kernel_20261003_v2.cpp"]


def metrics(rows):
    return {key: value for key, value in R.score(rows).items() if key != "scalar_weight"}


def snapshot(rows):
    n = len(rows)
    return dict(n=n, degree=rows[0].bit_count(),
                flat_adjacency=[(row >> v) & 1 for row in rows for v in range(n)],
                flat_true_A_squared=[value for row in R.full_product(rows) for value in row],
                **metrics(rows))


def kernel_record(rows, role):
    diagnostic, after, _ = R.replacement(rows, role)
    before_metrics = metrics(rows)
    after_metrics = metrics(after) if after is not None else before_metrics.copy()
    return dict(role=list(role), valid=after is not None, diagnostic=diagnostic,
                affected_unordered_pairs=4 * len(rows) - 10 if after is not None else 0,
                before_metrics=before_metrics, after_metrics=after_metrics,
                delta_F3=after_metrics["F3"] - before_metrics["F3"],
                delta_lambda=after_metrics["E_lambda"] - before_metrics["E_lambda"],
                delta_mu=after_metrics["E_mu"] - before_metrics["E_mu"],
                delta_E=after_metrics["E"] - before_metrics["E"],
                delta_scalar=after_metrics["scalar"] - before_metrics["scalar"]), after


def inverse_role(before, after):
    # Derive from complete graph differences, not the producer's role helper.
    original, candidate = set(R.edges(before)), set(R.edges(after))
    removed = sorted(candidate - original)
    R.need(len(removed) == 2 and len(original - candidate) == 2, "INVERSE_GRAPH_DIFFERENCE")
    for orientation in (0, 1):
        role = (*removed[0], *removed[1], orientation)
        _stage, restored, _key = R.replacement(after, role)
        if restored == before:
            return role
    raise ValueError("INVERSE_ROLE_NOT_FOUND")


def expected_probe(rows, role, pid):
    record, after = kernel_record(rows, role)
    valid = after is not None
    reverse = inverse_role(rows, after) if valid else None
    reverse_record = kernel_record(after, reverse)[0] if valid else None
    return dict(schema=PROBE_SCHEMA, proposal_id=pid,
                canonical_old_edges=[list(role[:2]), list(role[2:4])], orientation=role[4],
                kernel_record=record, before=snapshot(rows), after=snapshot(after if valid else rows),
                invalid_apply_unchanged=None if valid else True,
                reverse_role=list(reverse) if valid else None,
                reverse_kernel_record=reverse_record, restored=snapshot(rows) if valid else None)


def check_probe(raw, rows, role, pid):
    expected = expected_probe(rows, role, pid)
    R.need(type(raw) is dict and raw.keys() == expected.keys(), "PROBE_KEYS")
    for field in ("schema", "proposal_id", "canonical_old_edges", "orientation"):
        R.exact(raw[field], expected[field], "PROBE_FIELD:" + field)
    for field in ("before", "after", "restored"):
        wanted = expected[field]
        if wanted is None:
            R.exact(raw[field], None, "SNAPSHOT:" + field)
        else:
            R.need(type(raw[field]) is dict and raw[field].keys() == wanted.keys(), "SNAPSHOT_KEYS:" + field)
            for key in wanted:
                R.exact(raw[field][key], wanted[key], "SNAPSHOT:" + field + ":" + key)
    for field in ("kernel_record", "reverse_kernel_record"):
        wanted = expected[field]
        if wanted is None:
            R.exact(raw[field], None, "KERNEL_RECORD:" + field)
        else:
            R.need(type(raw[field]) is dict and raw[field].keys() == wanted.keys(), "KERNEL_RECORD_KEYS:" + field)
            for key in wanted:
                R.exact(raw[field][key], wanted[key], "KERNEL_RECORD:" + field + ":" + key)
    for field in ("invalid_apply_unchanged", "reverse_role"):
        R.exact(raw[field], expected[field], "PROBE_FIELD:" + field)
    return expected["kernel_record"]["valid"]


def roles(name, rows):
    if name == "synthetic99_14":
        return [(i, (0, 1, 20, 21, i)) for i in (0, 1)]
    return [(pid, role) for pid, _i, _j, role in R.labels(rows)]


def check_fixture(path, name, deadline):
    rows, _degree = R.fixture(name)
    labels = roles(name, rows)
    valid = 0
    with path.open("rb") as stream:
        def read():
            R.tick(deadline)
            raw = stream.readline(4 * 1024 * 1024 + 1)
            R.need(raw and len(raw) <= 4 * 1024 * 1024 and raw.endswith(b"\n"), "API_LINE_BOUNDARY")
            return R.strict_json(raw)
        R.exact(read(), dict(schema="ADJACENCY_SWITCH_API_FIXTURE_HEADER_V1", fixture=name,
                            declared_roles=len(labels), baseline_before=snapshot(rows)), "API_HEADER")
        for pid, role in labels:
            valid += check_probe(read(), rows, role, pid)
        R.exact(read(), dict(schema="ADJACENCY_SWITCH_API_FIXTURE_FOOTER_V1",
                            completed_roles=len(labels), baseline_after=snapshot(rows)), "API_FOOTER")
        R.need(stream.read(1) == b"", "API_TRAILING_BYTES")
    return dict(fixture=name, complete_roles=len(labels), valid_roles=valid,
                complete_getter_snapshots=2 + 2 * len(labels) + valid,
                reverse_calls=valid, invalid_unchanged_calls=len(labels) - valid)


def constructor_stage(n, degree, flat):
    if not (4 <= n <= 99 and 0 <= degree <= 14 and degree < n):
        return "GRAPH_DIMENSIONS"
    if len(flat) != n * n:
        return "GRAPH_SHAPE"
    for u in range(n):
        for v in range(n):
            if flat[u * n + v] not in (0, 1):
                return "GRAPH_BINARY"
            if flat[u * n + v] != flat[v * n + u]:
                return "GRAPH_SYMMETRY"
        if flat[u * n + u] != 0:
            return "GRAPH_DIAGONAL"
        if sum(flat[u * n:(u + 1) * n]) != degree:
            return "GRAPH_DEGREE"
    return "ACCEPTED_UNEXPECTED"


def negative_packets():
    rows, _ = R.fixture("rook9")
    flat = snapshot(rows)["flat_adjacency"]
    inputs = [("dimension_below4", "GRAPH_DIMENSIONS", 3, 2, [0] * 9),
              ("wrong_flat_shape", "GRAPH_SHAPE", 9, 4, flat[:-1])]
    for name, stage, updates in (("nonbinary_integer_entry", "GRAPH_BINARY", {1: 2}),
                                 ("one_sided_edge", "GRAPH_SYMMETRY", {1: 0}),
                                 ("diagonal_one", "GRAPH_DIAGONAL", {0: 1}),
                                 ("removed_edge_wrong_degree", "GRAPH_DEGREE", {1: 0, 9: 0})):
        changed = flat.copy()
        for i, value in updates.items():
            changed[i] = value
        inputs.append((name, stage, 9, 4, changed))
    packets = [dict(schema="ADJACENCY_SWITCH_API_CONSTRUCTOR_CASE_V1", case=name, n=n, degree=k,
                    input_flat_adjacency=a, expected_stage=stage,
                    actual_stage=constructor_stage(n, k, a), unexpected_accepted_snapshot=None)
               for name, stage, n, k, a in inputs]
    cases = [((-1, 1, 3, 4, 1), "ROLE_VERTEX_RANGE"), ((0, 1, 3, 4, 2), "ROLE_ORIENTATION"),
             ((1, 0, 3, 4, 1), "ROLE_CANONICAL_OLD_EDGES"), ((0, 1, 1, 2, 0), "ROLE_FOUR_DISTINCT_VERTICES"),
             ((0, 4, 3, 5, 0), "ROLE_OLD_EDGE_ABSENT"), ((0, 1, 3, 4, 0), "ROLE_NEW_EDGE_PRESENT")]
    packets += [dict(schema="ADJACENCY_SWITCH_API_ROLE_CASE_V1", case=stage, expected_stage=stage,
                     probe=expected_probe(rows, role, pid)) for pid, (role, stage) in enumerate(cases)]
    return packets


def read_negative(path, deadline):
    expected = negative_packets()
    with path.open("rb") as stream:
        for i, wanted in enumerate(expected):
            R.tick(deadline)
            raw = stream.readline(4 * 1024 * 1024 + 1)
            R.need(raw and len(raw) <= 4 * 1024 * 1024 and raw.endswith(b"\n"), "API_NEGATIVE_LINE")
            R.exact(R.strict_json(raw), wanted, "API_NEGATIVE_CASE:" + str(i))
        R.need(stream.read(1) == b"", "API_NEGATIVE_TRAILING")
    return len(expected)


def expected_manifest(context):
    return dict(schema="ADJACENCY_SWITCH_ACTUAL_API_HARNESS_V1",
                status="COMPLETE_CANDIDATE_REQUIRES_INDEPENDENT_API_REPLAY", producer="/root/structural",
                kernel_source_sha256=KERNEL_SHA, source_context=context,
                complete_tiny_roles=510, synthetic99_probes=2, negative_calls=12,
                actual_graph_getter_snapshots=True, actual_target_input_read=False, rng_used=False,
                rollback_API_claimed=False, independent_approval=False, target_resolution="NONE")


def check_manifest(manifest, context):
    expected = expected_manifest(context)
    R.need(type(manifest) is dict and manifest.keys() == expected.keys() | {"elapsed_seconds", "allocated_seconds", "save_seconds"}, "API_MANIFEST_KEYS")
    for key, wanted in expected.items():
        R.exact(manifest[key], wanted, "API_MANIFEST_FIELD:" + key)
    for key in ("elapsed_seconds", "allocated_seconds", "save_seconds"):
        R.need(type(manifest[key]) in (int, float) and math.isfinite(manifest[key]) and manifest[key] >= 0, "API_MANIFEST_TIME:" + key)
    R.need(manifest["allocated_seconds"] > manifest["save_seconds"] > 0
           and manifest["elapsed_seconds"] < manifest["allocated_seconds"] - manifest["save_seconds"], "API_MANIFEST_COOPERATIVE_TIME")


def write_fixture(path, name, deadline):
    rows, _ = R.fixture(name)
    labels = roles(name, rows)
    packets = [dict(schema="ADJACENCY_SWITCH_API_FIXTURE_HEADER_V1", fixture=name,
                    declared_roles=len(labels), baseline_before=snapshot(rows))]
    for pid, role in labels:
        R.tick(deadline)
        packets.append(expected_probe(rows, role, pid))
    packets.append(dict(schema="ADJACENCY_SWITCH_API_FIXTURE_FOOTER_V1", completed_roles=len(labels), baseline_after=snapshot(rows)))
    with path.open("x", encoding="utf8", newline="\n") as stream:
        for packet in packets:
            R.tick(deadline)
            stream.write(json.dumps(packet, allow_nan=False) + "\n")
    R.tick(deadline)


def own_controls(out, deadline):
    positives = []
    for name in FIXTURES:
        R.tick(deadline)
        path = out / (name + ".probes.jsonl")
        write_fixture(path, name, deadline)
        positives.append(check_fixture(path, name, deadline))
    path = out / "negative_calls.jsonl"
    with path.open("x", encoding="utf8", newline="\n") as stream:
        for packet in negative_packets():
            stream.write(json.dumps(packet, allow_nan=False) + "\n")
    R.exact(read_negative(path, deadline), 12, "OWN_NEGATIVE_CALL_POPULATION")
    rows, _ = R.fixture("rook9")
    valid = next((pid, role) for pid, role in roles("rook9", rows) if R.replacement(rows, role)[1] is not None)
    invalid = next((pid, role) for pid, role in roles("rook9", rows) if R.replacement(rows, role)[1] is None)
    pristine = expected_probe(rows, valid[1], valid[0])
    cases = []
    for field in ("proposal_id", "orientation"):
        for kind in ("boolean", "float"):
            cases.append((field + "_" + kind, "PROBE_FIELD:" + field,
                          lambda raw, f=field, k=kind: raw.update({f: bool(raw[f]) if k == "boolean" else float(raw[f])})))
    for side in ("before", "after", "restored"):
        for key in ("n", "degree", "F3", "E", "scalar"):
            cases.append((side + "_" + key + "_bool", "SNAPSHOT:" + side + ":" + key,
                          lambda raw, s=side, k=key: raw[s].update({k: bool(raw[s][k])})))
        for key in ("flat_adjacency", "flat_true_A_squared"):
            for kind in ("boolean", "float", "wrong"):
                cases.append((side + "_" + key + "_" + kind, "SNAPSHOT:" + side + ":" + key,
                              lambda raw, s=side, k=key, t=kind: raw[s][k].__setitem__(0, bool(raw[s][k][0]) if t == "boolean" else float(raw[s][k][0]) if t == "float" else raw[s][k][0] + 1)))
    for side in ("kernel_record", "reverse_kernel_record"):
        for key in ("valid", "diagnostic", "affected_unordered_pairs", "delta_F3", "delta_lambda", "delta_mu", "delta_E", "delta_scalar"):
            cases.append((side + "_" + key, "KERNEL_RECORD:" + side + ":" + key,
                          lambda raw, s=side, k=key: raw[s].update({k: 1 if k == "valid" else "WRONG" if k == "diagnostic" else float(raw[s][k])})))
    cases += [("wrong_inverse_orientation", "PROBE_FIELD:reverse_role", lambda raw: raw["reverse_role"].__setitem__(4, 1 - raw["reverse_role"][4])),
              ("valid_flag_forged", "PROBE_FIELD:invalid_apply_unchanged", lambda raw: raw.update(invalid_apply_unchanged=True)),
              ("missing_probe_key", "PROBE_KEYS", lambda raw: raw.pop("after"))]
    negatives = []
    for name, wanted, mutate in cases:
        R.tick(deadline)
        raw = deepcopy(pristine)
        mutate(raw)
        R.write_json(out / ("corrupt_" + name + ".json"), raw)
        try:
            check_probe(R.read_json(out / ("corrupt_" + name + ".json")), rows, valid[1], valid[0])
            actual = "ACCEPTED_CORRUPTION"
        except ValueError as error:
            actual = str(error)
        R.exact(actual, wanted, "OWN_STAGE:" + name)
        negatives.append(dict(case=name, expected_stage=wanted, actual_stage=actual))
    raw = expected_probe(rows, invalid[1], invalid[0])
    raw["invalid_apply_unchanged"] = False
    try:
        check_probe(raw, rows, invalid[1], invalid[0])
        actual = "ACCEPTED_CORRUPTION"
    except ValueError as error:
        actual = str(error)
    R.exact(actual, "PROBE_FIELD:invalid_apply_unchanged", "OWN_INVALID_FLAG")
    R.write_json(out / "corrupt_invalid_flag.json", raw)
    negatives.append(dict(case="invalid_unchanged_false", expected_stage=actual, actual_stage=actual))
    prism, _ = R.fixture("triangular_prism6")
    pid, role = next((pid, role) for pid, role in roles("triangular_prism6", prism)
                     if R.replacement(prism, role)[1] is not None)
    positive = expected_probe(prism, role, pid)
    for value in (0, 1):
        index = next(i for i, v in enumerate(positive["before"]["flat_true_A_squared"])
                     if v == value and i // len(prism) != i % len(prism))
        for kind in ("boolean", "float"):
            R.tick(deadline)
            raw = deepcopy(positive)
            raw["before"]["flat_true_A_squared"][index] = bool(value) if kind == "boolean" else float(value)
            name = "offdiagonal_cache" + str(value) + "_" + kind
            R.write_json(out / ("corrupt_" + name + ".json"), raw)
            try:
                check_probe(R.read_json(out / ("corrupt_" + name + ".json")), prism, role, pid)
                actual = "ACCEPTED_CORRUPTION"
            except ValueError as error:
                actual = str(error)
            R.exact(actual, "SNAPSHOT:before:flat_true_A_squared", "OWN_CACHE_ALIAS:" + name)
            negatives.append(dict(case=name, expected_stage=actual, actual_stage=actual))
    base = [R.strict_json(line) for line in (out / "cube8.probes.jsonl").read_bytes().splitlines()]
    stream_cases = [
        ("header_population_bool", "API_HEADER", lambda p: p[0].update(declared_roles=True)),
        ("header_cache_diagonal_zero", "API_HEADER", lambda p: p[0]["baseline_before"]["flat_true_A_squared"].__setitem__(0, 0)),
        ("drop_first_record", "PROBE_FIELD:proposal_id", lambda p: p.pop(1)),
        ("duplicate_first_record", "PROBE_FIELD:proposal_id", lambda p: p.insert(2, deepcopy(p[1]))),
        ("swap_first_orientation", "PROBE_FIELD:orientation", lambda p: p[1].update(orientation=1)),
        ("footer_count_float", "API_FOOTER", lambda p: p[-1].update(completed_roles=float(p[-1]["completed_roles"]))),
        ("extra_tail", "API_TRAILING_BYTES", lambda p: p.append({"unapproved": True})),
    ]
    for name, wanted, mutate in stream_cases:
        R.tick(deadline)
        raw = deepcopy(base)
        mutate(raw)
        path = out / ("corrupt_stream_" + name + ".jsonl")
        with path.open("x", encoding="utf8", newline="\n") as stream:
            for packet in raw:
                R.tick(deadline)
                stream.write(json.dumps(packet, allow_nan=False) + "\n")
        try:
            check_fixture(path, "cube8", deadline)
            actual = "ACCEPTED_CORRUPTION"
        except ValueError as error:
            actual = str(error)
        R.exact(actual, wanted, "OWN_STREAM_STAGE:" + name)
        negatives.append(dict(case=name, expected_stage=wanted, actual_stage=actual))
    for name, raw, wanted in (("duplicate_json_key", b'{"x":0,"x":1}', "JSON_DUPLICATE_KEY"),
                              ("nonfinite_json", b'{"x":NaN}', "JSON_NONFINITE")):
        (out / ("corrupt_" + name + ".json")).write_bytes(raw)
        try:
            R.strict_json(raw)
            actual = "ACCEPTED_CORRUPTION"
        except ValueError as error:
            actual = str(error)
        R.exact(actual, wanted, "OWN_JSON_STAGE:" + name)
        negatives.append(dict(case=name, expected_stage=wanted, actual_stage=actual))
    context = "d0c0dd7db0d3de420b1d718b59122b069df01107"
    manifest = dict(**expected_manifest(context), elapsed_seconds=0.25, allocated_seconds=10, save_seconds=1)
    R.write_json(out / "synthetic_manifest.json", manifest)
    check_manifest(R.read_json(out / "synthetic_manifest.json"), context)
    manifest_cases = []
    for key in ("complete_tiny_roles", "synthetic99_probes", "negative_calls"):
        for kind in ("boolean", "float"):
            manifest_cases.append((key + "_" + kind, "API_MANIFEST_FIELD:" + key,
                                   lambda p, k=key, t=kind: p.update({k: bool(p[k]) if t == "boolean" else float(p[k])})))
    for key in ("actual_graph_getter_snapshots", "actual_target_input_read", "rng_used", "rollback_API_claimed", "independent_approval"):
        manifest_cases.append((key, "API_MANIFEST_FIELD:" + key, lambda p, k=key: p.update({k: not p[k]})))
    for key in ("kernel_source_sha256", "source_context", "status", "producer"):
        manifest_cases.append((key, "API_MANIFEST_FIELD:" + key, lambda p, k=key: p.update({k: "WRONG"})))
    for key in ("elapsed_seconds", "allocated_seconds", "save_seconds"):
        manifest_cases.append((key + "_bool", "API_MANIFEST_TIME:" + key, lambda p, k=key: p.update({k: True})))
    manifest_cases += [("missing_field", "API_MANIFEST_KEYS", lambda p: p.pop("rng_used")),
                       ("late_completion", "API_MANIFEST_COOPERATIVE_TIME", lambda p: p.update(elapsed_seconds=9.0))]
    for name, wanted, mutate in manifest_cases:
        R.tick(deadline)
        raw = deepcopy(manifest)
        mutate(raw)
        path = out / ("corrupt_manifest_" + name + ".json")
        R.write_json(path, raw)
        try:
            check_manifest(R.read_json(path), context)
            actual = "ACCEPTED_CORRUPTION"
        except ValueError as error:
            actual = str(error)
        R.exact(actual, wanted, "OWN_MANIFEST_STAGE:" + name)
        negatives.append(dict(case="manifest_" + name, expected_stage=wanted, actual_stage=actual))
    R.write_json(out / "own_negative_records.json", negatives)
    R.exact(len(negatives), 90, "OWN_EXACT_NEGATIVE_POPULATION")
    R.exact(len(manifest_cases), 20, "OWN_EXACT_MANIFEST_POPULATION")
    return dict(own_fixture_streams=positives, strict_negative_cases=len(negatives),
                synthetic_constructor_and_role_calls=12, synthetic_manifest_positive=1,
                strict_manifest_negative_cases=len(manifest_cases), producer_outputs_read=False,
                actual_target_input_read=False, native_calls=0)


def admit_calibration(path, identity, software_inputs, pin):
    # This frozen software map excludes the later calibration-summary pin.
    cal = R.read_json(pin(path, identity))
    R.need(type(cal) is dict and
           cal.get("status") == "INDEPENDENT_ADJACENCY_SWITCH_ACTUAL_API_V1_OWN_CALIBRATION_PASS"
           and cal.get("producer") == "/root/structural" and cal.get("verifier") == "/root"
           and cal.get("source_author") == "/root/native_driver"
           and cal.get("method") == "independent_artifact_check"
           and cal.get("target_resolution") == "NONE", "API_CALIBRATION_HEADER")
    scope = cal.get("checked_scope")
    R.need(type(scope) is dict, "API_CALIBRATION_SCOPE")
    for name, wanted in {"strict_negative_cases": 102, "strict_manifest_negative_cases": 20,
                         "synthetic_constructor_and_role_calls": 12, "synthetic_manifest_positive": 1,
                         "synthetic_calibration_admission_positive": 1,
                         "strict_calibration_admission_negative_cases": 12,
                         "synthetic_calibration_baseline_output_files": 97,
                         "producer_outputs_read": False, "actual_target_input_read": False, "native_calls": 0}.items():
        R.exact(scope.get(name), wanted, "API_CALIBRATION_SCOPE:" + name)
    R.need(type(cal.get("inputs_sha256")) is dict and type(cal.get("outputs_sha256")) is dict
           and cal["inputs_sha256"] and cal["outputs_sha256"], "API_CALIBRATION_MAPS")
    R.exact(cal["inputs_sha256"], software_inputs, "API_CALIBRATION_SOURCE")
    for mapping in (cal["inputs_sha256"], cal["outputs_sha256"]):
        for name, wanted in mapping.items():
            R.need(type(name) is str and type(wanted) is str
                   and re.fullmatch(r"[0-9a-f]{64}", wanted), "API_CALIBRATION_MAP_ENTRY")
            pin(ROOT / name, wanted)
    return cal


def calibration_admission_controls(out, deadline, software_inputs, pin):
    # Reuse the actual runtime admission path and pinner with an isolated map;
    # synthetic own outputs belong to the output map, not software inputs.
    baseline_outputs = {p.relative_to(ROOT).as_posix(): R.digest(p, deadline)
                        for p in sorted(out.iterdir()) if p.is_file()}
    R.exact(len(software_inputs), 15, "OWN_CALIBRATION_SOFTWARE_POPULATION")
    R.exact(len(baseline_outputs), 97, "OWN_CALIBRATION_BASELINE_OUTPUT_POPULATION")
    packet = dict(status="INDEPENDENT_ADJACENCY_SWITCH_ACTUAL_API_V1_OWN_CALIBRATION_PASS",
                  producer="/root/structural", verifier="/root", source_author="/root/native_driver",
                  method="independent_artifact_check", target_resolution="NONE",
                  checked_scope=dict(strict_negative_cases=102, strict_manifest_negative_cases=20,
                                     synthetic_constructor_and_role_calls=12, synthetic_manifest_positive=1,
                                     synthetic_calibration_admission_positive=1,
                                     strict_calibration_admission_negative_cases=12,
                                     synthetic_calibration_baseline_output_files=97,
                                     producer_outputs_read=False, actual_target_input_read=False, native_calls=0),
                  inputs_sha256=software_inputs.copy(), outputs_sha256=baseline_outputs)
    path = out / "synthetic_calibration_admission.json"
    R.write_json(path, packet)
    observed = software_inputs.copy()
    observed_counts = []
    def scoped_pin(path, identity=None):
        result = pin(path, identity, observed)
        observed_counts.append(len(observed))
        return result
    admit_calibration(path, R.digest(path, deadline), software_inputs, scoped_pin)
    R.exact(observed_counts[0], 16, "OWN_CALIBRATION_SUMMARY_PIN_POPULATION")
    R.exact(len(observed), 113, "OWN_CALIBRATION_ADMISSION_CLOSURE_POPULATION")
    positive = dict(case="software15_summary16_then_full97_closure", software_inputs=15,
                    inputs_after_summary_pin=observed_counts[0], complete_output_closure_files=97,
                    final_identity_map_entries=len(observed), actual_stage="PASS")
    source_name = SELF.relative_to(ROOT).as_posix()
    output_name = sorted(baseline_outputs)[0]
    self_summary_name = path.relative_to(ROOT).as_posix()
    cases = [
        ("wrong_status", "API_CALIBRATION_HEADER", lambda p: p.update(status="WRONG")),
        ("wrong_verifier", "API_CALIBRATION_HEADER", lambda p: p.update(verifier="/root/native_driver")),
        ("native_calls_bool", "API_CALIBRATION_SCOPE:native_calls", lambda p: p["checked_scope"].update(native_calls=False)),
        ("negative_count_float", "API_CALIBRATION_SCOPE:strict_negative_cases", lambda p: p["checked_scope"].update(strict_negative_cases=102.0)),
        ("missing_software", "API_CALIBRATION_SOURCE", lambda p: p["inputs_sha256"].pop(source_name)),
        ("wrong_software_hash", "API_CALIBRATION_SOURCE", lambda p: p["inputs_sha256"].update({source_name: "0" * 64})),
        ("extra_software", "API_CALIBRATION_SOURCE", lambda p: p["inputs_sha256"].update({"acceleration/not_software.json": "0" * 64})),
        ("self_summary_in_software", "API_CALIBRATION_SOURCE", lambda p: p["inputs_sha256"].update({self_summary_name: R.digest(path, deadline)})),
        ("invalid_output_hash", "API_CALIBRATION_MAP_ENTRY", lambda p: p["outputs_sha256"].update({output_name: "WRONG"})),
        ("wrong_output_hash", "INPUT_SHA:" + output_name, lambda p: p["outputs_sha256"].update({output_name: "0" * 64})),
        ("empty_output_map", "API_CALIBRATION_MAPS", lambda p: p.update(outputs_sha256={})),
        ("nonmap_software", "API_CALIBRATION_MAPS", lambda p: p.update(inputs_sha256=True)),
    ]
    negatives = []
    for name, wanted, mutate in cases:
        R.tick(deadline)
        raw = deepcopy(packet)
        mutate(raw)
        damaged = out / ("corrupt_calibration_admission_" + name + ".json")
        R.write_json(damaged, raw)
        observed = software_inputs.copy()
        try:
            admit_calibration(damaged, R.digest(damaged, deadline), software_inputs, scoped_pin)
            actual = "ACCEPTED_CORRUPTION"
        except ValueError as error:
            actual = str(error)
        R.exact(actual, wanted, "OWN_CALIBRATION_ADMISSION_STAGE:" + name)
        negatives.append(dict(case=name, expected_stage=wanted, actual_stage=actual))
    R.exact(len(negatives), 12, "OWN_CALIBRATION_ADMISSION_NEGATIVE_POPULATION")
    R.write_json(out / "own_calibration_admission_records.json", dict(positive=positive, negatives=negatives))
    R.tick(deadline)
    return dict(synthetic_calibration_admission_positive=1, strict_calibration_admission_negative_cases=12,
                synthetic_calibration_baseline_output_files=97)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("calibrate", "native-api"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--native-dir", type=Path)
    parser.add_argument("--native-manifest-sha256")
    parser.add_argument("--source-context")
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--calibration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Independent literal actual API getters; complete products/JSON/hashes/save inside one invocation")
    out = args.out.resolve()
    R.need(out.is_relative_to(ROOT / "acceleration/results") and not out.exists(), "FRESH_OUTPUT")
    out.mkdir(parents=True)
    inputs = {}
    def pin(path, wanted=None, identity_map=None):
        identity_map = inputs if identity_map is None else identity_map
        path = Path(path).resolve()
        R.need(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink(), "INPUT_FILE")
        name = path.relative_to(ROOT).as_posix()
        R.need(name != "CLAIMS.yaml" and not name.startswith(".git/"), "MUTABLE_INPUT")
        observed = R.digest(path, deadline)
        R.need(wanted is None or observed == wanted, "INPUT_SHA:" + name)
        R.need(name not in identity_map or identity_map[name] == observed, "INPUT_CHANGED")
        identity_map[name] = observed
        return path
    try:
        for name, wanted in PINS.items():
            pin(ROOT / name, wanted)
        pin(SELF); pin(SPEC)
        software_inputs = inputs.copy()
        if args.mode == "calibrate":
            R.need(args.native_dir is None and args.native_manifest_sha256 is None and args.source_context is None
                   and args.calibration is None and args.calibration_sha256 is None, "CAL_NO_NATIVE")
            result = own_controls(out, deadline)
            result.update(calibration_admission_controls(out, deadline, software_inputs, pin))
            result["strict_negative_cases"] += result["strict_calibration_admission_negative_cases"]
            status = "INDEPENDENT_ADJACENCY_SWITCH_ACTUAL_API_V1_OWN_CALIBRATION_PASS"
        else:
            R.need(args.native_dir is not None and re.fullmatch(r"[0-9a-f]{64}", args.native_manifest_sha256 or "")
                   and re.fullmatch(r"[0-9a-f]{40}", args.source_context or ""), "NATIVE_OPTIONS")
            R.need(args.calibration is not None and re.fullmatch(r"[0-9a-f]{64}", args.calibration_sha256 or ""), "GENUINE_API_CALIBRATION")
            admit_calibration(args.calibration, args.calibration_sha256, software_inputs, pin)
            native = args.native_dir.resolve()
            R.need(native.is_relative_to(ROOT / "acceleration/results") and native.is_dir() and not native.is_symlink(), "NATIVE_DIR")
            expected_files = {name + ".probes.jsonl" for name in FIXTURES} | {"negative_calls.jsonl", "manifest.json"}
            R.need({p.name for p in native.iterdir()} == expected_files
                   and all(p.is_file() and not p.is_symlink() for p in native.iterdir()), "NATIVE_EXACT_FILES")
            for path in sorted(native.iterdir()):
                pin(path, args.native_manifest_sha256 if path.name == "manifest.json" else None)
            manifest = R.read_json(native / "manifest.json")
            check_manifest(manifest, args.source_context)
            fixtures = [check_fixture(native / (name + ".probes.jsonl"), name, deadline) for name in FIXTURES]
            result = dict(complete_fixture_scopes=fixtures, complete_tiny_roles=sum(x["complete_roles"] for x in fixtures[:3]),
                          synthetic99_probes=fixtures[3]["complete_roles"], constructor_and_role_negative_calls=read_negative(native / "negative_calls.jsonl", deadline),
                          native_output_files=6, actual_target_input_read=False, native_calls=0,
                          native_packet_contents_checked=True, rollback_API_claimed=False)
            status = "INDEPENDENT_ADJACENCY_SWITCH_ACTUAL_API_V1_COMPLETE_PASS"
        for name, wanted in list(inputs.items()):
            pin(ROOT / name, wanted)
        outputs = {p.relative_to(ROOT).as_posix(): R.digest(p, deadline) for p in sorted(out.iterdir()) if p.is_file()}
        R.tick(deadline)
        R.write_json(out / "summary.json", dict(status=status, producer="/root/structural", verifier="/root",
                     source_author="/root/native_driver", method="independent_artifact_check", target_resolution="NONE", implementation_version=3,
                     timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv],
                     inputs_sha256=inputs, outputs_sha256=outputs, checked_scope=result,
                     containment_checked=False, binary_build_identity_checked=False,
                     combined_wrapper_control_gate_emitted=False,
                     limitations=["API packet only; ROOT must separately bind authentic build/binary/child/UID/admission/containment evidence.",
                                  "Qualified independent51fee oracle reused; no producer parser/kernel/harness/cache update imported.",
                                  "No actualtarget,479556 census, stochastic search, rollback API or graph-space result."], deadline=deadline.status()))
        R.tick(deadline)
        return 0
    except BaseException as error:
        if (out / "summary.json").exists():
            (out / "summary.json").rename(out / "summary.not_approved.json")
        R.write_json(out / "failure.json", dict(error=repr(error), inputs_sha256=inputs,
                     deadline=deadline.status(), automatic_retry=False, target_resolution="NONE"))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
