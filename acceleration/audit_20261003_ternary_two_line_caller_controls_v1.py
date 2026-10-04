"""SOURCE ONLY: independent finite checking of the changed F3 caller.

Imports only the preserved independent kernel checker/full-row core/strict IO.
No Native parser, caller, incremental scorer, author reference or topology imports.
Calibration/check modes read generic fixtures and synthetic metadata only.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline
import audit_20261003_ternary_two_line_controls_v1 as kernel

core, io, ROOT = kernel.core, kernel.io, kernel.ROOT
SELF = "acceleration/audit_20261003_ternary_two_line_caller_controls_v1.py"
SPEC = "acceleration/audit_20261003_ternary_two_line_caller_controls_v1_spec.md"
CALLER = "acceleration/census_20261003_ternary_two_line_caller_v1.py"
CALLER_SPEC = "acceleration/census_20261003_ternary_two_line_caller_v1_spec.md"
PLAN = "acceleration/plan_20261003_ternary_two_line_caller_author_controls_v1.json"
PLAN_SHA = "0081fb6476a19b66ff29ce207342d1780c901adb1cf2129ad7b31fa47594f002"
AUTHOR = "acceleration/results/20261003_ternary_two_line_caller_v1_controls01"
RUNTIME = "acceleration/results/20261003_ternary_two_line_caller_v1_controls_supervision01"
ADMISSION = "acceleration/results/20261003_ternary_two_line_caller_v1_controls_admission01.json"
KERNEL_GATE = "acceleration/results/20261003_independent_review/ternary_two_line_kernel_full01/summary.json"
KERNEL_GATE_SHA = "77cf4c7d8ea79310a98be6628fbefd3d31a2615ff764811f2f2a172fa26b6544"
KERNEL_PASS = "INDEPENDENT_TERNARY_TWO_LINE_KERNEL_V1_COMPLETE_CONTROLS_PASS"
CALLER_PASS = "INDEPENDENT_TERNARY_TWO_LINE_CALLER_V1_COMPLETE_CONTROLS_PASS"
INPUT_PASS = "INDEPENDENT_TERNARY_ALL_LINE_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS"
CAL_PASS = "INDEPENDENT_TERNARY_TWO_LINE_CALLER_RAW_CHECKER_V1_CALIBRATION_PASS"
STATE = "acceleration/results/20261003_hypergraph_weight60_warm01/native/final.state"
MATRIX = "acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj"
WARM_AUDIT = "acceleration/results/20261003_independent_review/weight60_warm01/summary.json"
WARM_SOURCE = "acceleration/results/20261003_hypergraph_weight60_warm01/summary.json"
WARM_PINS = {
 STATE: "c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b",
 MATRIX: "9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d",
 WARM_AUDIT: "256c8277ab5c69e74f4c9725c4b42e96e31b4e546c490b8e231df4ed6831bf6c",
 WARM_SOURCE: "da370b4898dcd7288e42787684d12b7945933516234c2965155ed312722d4baf",
}
STATIC = {
 "acceleration/audit_20261003_ternary_two_line_controls_v1.py": "86e0b526d1202660284cb4a3639f4d89c2ea9bd38f7c9613f26a7790a57800d6",
 "acceleration/audit_20261003_ternary_two_line_controls_v1_spec.md": "55f20a5cc0136bd1b4ad09f5d83232d43667b4d1210fafe28d779c16bee70e45",
 **kernel.STATIC, PLAN: PLAN_SHA,
 CALLER: "4984f029ce22dfbe5dff204aef67d0c7b8127bc92c26910f744687ada3849f12",
 CALLER_SPEC: "f3aa82d7f944b3adea32703758ff3b8783448e3f6eb6efb93f3fb498e3471124",
}


def wire(raw, stage):
    io.need(type(raw) is bytes and len(raw) <= 131072, stage)
    try:
        text = raw.decode("ascii")
    except UnicodeError as error:
        raise io.AuditError(stage) from error
    io.need(text.endswith("\n") and "\r" not in text and "\x00" not in text, stage)
    return text[:-1].split("\n")


def decimal(token):
    return (0 < len(token) <= 6 and all("0" <= c <= "9" for c in token)
            and (token == "0" or token[0] != "0"))


def state_graph(raw):
    lines = wire(raw, "STATE_WIRE")
    io.need(lines[0] == "HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2" and lines[-1] == "END", "STATE_SCHEMA")
    headers = {}
    for key in ("n", "degree", "best"):
        hits = [(at, line.split(" ")) for at, line in enumerate(lines) if line.startswith(key + " ")]
        io.need(len(hits) == 1 and len(hits[0][1]) == 2 and decimal(hits[0][1][1]), "STATE_HEADERS")
        headers[key] = (hits[0][0], int(hits[0][1][1]))
    n, degree, count = (headers[key][1] for key in ("n", "degree", "best"))
    io.need(3 <= n <= 99 and 0 < 2*degree < n and 3*count == n*degree, "STATE_DIMENSIONS")
    at = headers["best"][0] + 1
    io.need(at + count < len(lines), "STATE_TRIPLES")
    rows = []
    for line in lines[at:at+count]:
        tokens = line.split(" ")
        io.need(len(tokens) == 3 and all(decimal(token) for token in tokens), "STATE_TRIPLES")
        rows.append([int(token) for token in tokens])
    end = lines[at+count].split(" ")
    io.need(not (len(end) == 3 and all(decimal(token) for token in end)), "STATE_TRIPLES")
    # Whole geometry, incidence counts, simplicity and exact int64 A@A follow
    # from the independent core. Other saved native fields are opaque history.
    return core.fixed_input(n, degree, rows)


def matrix_graph(raw, base):
    lines = wire(raw, "MATRIX_WIRE")
    io.need(len(lines) == base.n+1 and lines[0] == str(base.n)
        and all(len(line) == base.n and set(line) <= {"0", "1"} for line in lines[1:]), "MATRIX_SHAPE")
    io.need(raw == io.matrix_bytes(base.adjacency), "MATRIX_IDENTITY")


def gate_header(gate, status, stage):
    io.need(type(gate) is dict and gate.get("status") == status and gate.get("producer") == "/root/native_driver"
        and gate.get("verifier") == "/root/structural" and gate.get("method") == "independent_artifact_check"
        and gate.get("target_resolution") == "NONE" and type(gate.get("inputs_sha256")) is dict, stage)


def check_gate(kind, gate, software, kernel_software, graph):
    stage = kind + "_GATE"
    status = {"KERNEL": KERNEL_PASS, "CALLER": CALLER_PASS, "INPUT": INPUT_PASS}[kind]
    gate_header(gate, status, stage)
    required = kernel_software if kind == "KERNEL" else software
    if kind == "KERNEL":
        io.need(all(io.integer(gate.get(key)) and gate[key] == expected for key, expected in
            dict(unique_fixture_labels=522, strict_author_negative_cases=160, whole_prefix_resume_equalities=3).items()), stage)
    if kind != "INPUT":
        io.need(gate.get("actual_target_input_read") is False, stage)
    else:
        required = {**software, **WARM_PINS}
        io.need(gate.get("graph_only_input") is True and gate.get("historical_native_state_written") is False
            and gate.get("rng_or_trajectory_imported") is False and gate.get("all_lines_mutable") is True, stage)
        io.need(all(io.integer(gate.get(key)) and gate[key] == expected for key, expected in
            dict(n=99, point_degree=7, ordered_triples=231, proposal_population=239085).items()), stage)
        io.need(io.same(gate.get("graph_input"), graph), stage)
    io.need(all(gate["inputs_sha256"].get(path) == identity for path, identity in required.items()), stage)


def check_warm(value):
    # A metadata-only historical-interface control. It does not certify a graph.
    io.need(type(value) is dict and value.get("status") == "INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS"
        and value.get("producer") == "/root/native_driver" and value.get("verifier") == "/root/structural"
        and value.get("target_resolution") is False and type(value.get("inputs_sha256")) is dict, "WARM_AUDIT")
    io.need(all(io.integer(value.get(key)) and value[key] == count for key, count in
        dict(saved_state_files=103, complete_integer_saved_current_best_objects=206).items()), "WARM_AUDIT")
    io.need(all(value["inputs_sha256"].get(key) == WARM_PINS[key] for key in (STATE, MATRIX, WARM_SOURCE)), "WARM_AUDIT")
    diag = value.get("final_best_diagnostics")
    io.need(type(diag) is dict and diag.get("domain_valid") is True and diag.get("srg_valid") is False
        and all(io.integer(diag.get(key)) and diag[key] == count for key, count in
            dict(ordered_entries_checked=9801, lambda_energy=0, mu_energy=3480, base_energy=3480, identity_mismatches=4764).items()),
        "WARM_AUDIT")


def synthetic_graph():
    return dict(schema="TERNARY_ALL_LINE_GRAPH_ONLY_INPUT_V1", n=99, point_degree=7, ordered_triples=[],
        metrics=dict(F3=2376, E_lambda=0, E_mu=3480, E=3480), synthetic_metadata_only=True,
        source_state_path=STATE, source_state_sha256=WARM_PINS[STATE], source_matrix_path=MATRIX,
        source_matrix_sha256=WARM_PINS[MATRIX], source_independent_audit_path=WARM_AUDIT,
        source_independent_audit_sha256=WARM_PINS[WARM_AUDIT], historical_native_state_written=False,
        rng_or_trajectory_imported=False, all_lines_mutable=True)


def synthetic_gates(software, kernel_software):
    head = dict(producer="/root/native_driver", verifier="/root/structural", method="independent_artifact_check", target_resolution="NONE")
    graph = synthetic_graph()
    gates = dict(KERNEL_GATE=dict(head, status=KERNEL_PASS, inputs_sha256=dict(kernel_software),
        unique_fixture_labels=522, strict_author_negative_cases=160, whole_prefix_resume_equalities=3, actual_target_input_read=False),
        CALLER_GATE=dict(head, status=CALLER_PASS, inputs_sha256=dict(software), actual_target_input_read=False),
        INPUT_GATE=dict(head, status=INPUT_PASS, inputs_sha256={**software, **WARM_PINS}, graph_input=graph,
            graph_only_input=True, historical_native_state_written=False, rng_or_trajectory_imported=False,
            all_lines_mutable=True, n=99, point_degree=7, ordered_triples=231, proposal_population=239085))
    warm = dict(status="INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS", producer="/root/native_driver",
        verifier="/root/structural", target_resolution=False, saved_state_files=103,
        complete_integer_saved_current_best_objects=206, inputs_sha256={key: WARM_PINS[key] for key in (STATE, MATRIX, WARM_SOURCE)},
        final_best_diagnostics=dict(domain_valid=True, srg_valid=False, ordered_entries_checked=9801,
            lambda_energy=0, mu_energy=3480, base_energy=3480, identity_mismatches=4764))
    return graph, gates, warm


def software_order(raw):
    # This finite source-derived insertion order determines Native *_missing_N
    # filenames. It is not imported from any executable producer.
    order = ["acceleration/census_20261003_weight60_two_line_v2.py", "acceleration/census_20261003_weight60_two_line_v2_spec.md",
        "acceleration/census_20261003_root_focused_restricted_three_line_v3.py", "acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md",
        "acceleration/theory_20261003_hypergraph_ternary_residue_reference_v1.py",
        "docs/DESIGN_20261003_HYPERGRAPH_TERNARY_RESIDUE_SEARCH_V1.md", "docs/CANDIDATE_20261003_TERNARY_DEGREE14_EXACTNESS_V1.md",
        "acceleration/audit_20261003_ternary_degree14_exactness_v1.md", "docs/CANDIDATE_20261003_TERNARY_RESIDUE_ENERGY_BOUNDS_V1.md",
        "acceleration/audit_20261003_ternary_residue_energy_bounds_v1.md", "acceleration/census_20261003_root_focused_two_line_v1.py",
        "acceleration/census_20261003_root_focused_two_line_v1_spec.md", "acceleration/command_deadline.py", "acceleration/run_compute_command.py",
        "acceleration/native_budget_env_v1/pyproject.toml", "acceleration/native_budget_env_v1/uv.lock",
        "acceleration/census_20261003_ternary_two_line_v1.py", "acceleration/census_20261003_ternary_two_line_v1_spec.md", CALLER, CALLER_SPEC]
    io.need(type(raw) is dict and set(raw) == set(order), "SOFTWARE_UNIVERSE")
    return {path: raw[path] for path in order}


def wire_cases(name, n, raw, matrix):
    yield name+"_no_lf", "STATE_WIRE", raw[:-1], None
    yield name+"_crlf", "STATE_WIRE", raw.replace(b"\n", b"\r\n"), None
    yield name+"_nonascii", "STATE_WIRE", raw+b"\xff", None
    yield name+"_badmagic", "STATE_SCHEMA", raw.replace(b"ANNEAL_STATE_V2", b"ANNEAL_STATE_V1"), None
    yield name+"_duplicate_best", "STATE_HEADERS", raw.replace(b"current 0\n", b"best 0\n"), None
    yield name+"_float_n", "STATE_HEADERS", raw.replace(f"n {n}\n".encode(), f"n {n}.0\n".encode()), None
    yield name+"_short_best", "STATE_DIMENSIONS", raw.replace(b"best ", b"best 999"), None
    yield name+"_matrix_no_lf", "MATRIX_WIRE", None, matrix[:-1]
    yield name+"_matrix_nonbinary", "MATRIX_SHAPE", None, matrix.replace(b"0", b"2", 1)
    at = len(str(n))+1
    yield name+"_matrix_diagonal", "MATRIX_IDENTITY", None, matrix[:at]+b"1"+matrix[at+1:]


def metadata_cases(software, kernel_software, first=30):
    graph, gates, warm = synthetic_gates(software, kernel_software)
    count = first
    for stage, gate in gates.items():
        required = kernel_software if stage == "KERNEL_GATE" else software
        if stage == "INPUT_GATE": required = gate["inputs_sha256"]
        mutations = []
        for key in ("status", "producer", "verifier", "method", "target_resolution"):
            bad = copy.deepcopy(gate); bad[key] = "wrong"; mutations.append((stage+"_"+key, bad))
        for name, bad in mutations:
            yield name, stage, bad; count += 1
        for key in required:
            bad = copy.deepcopy(gate); bad["inputs_sha256"].pop(key)
            yield stage+"_missing_"+str(count), stage, bad; count += 1
        if stage != "INPUT_GATE":
            bad = copy.deepcopy(gate); bad["actual_target_input_read"] = True
            yield stage+"_target_read", stage, bad; count += 1
        if stage == "KERNEL_GATE":
            for key in ("unique_fixture_labels", "strict_author_negative_cases", "whole_prefix_resume_equalities"):
                for suffix, value in (("wrong", gate[key]+1), ("bool", True), ("float", float(gate[key]))):
                    bad = copy.deepcopy(gate); bad[key] = value
                    yield stage+"_"+key+"_"+suffix, stage, bad; count += 1
        elif stage == "INPUT_GATE":
            for key in ("graph_only_input", "historical_native_state_written", "rng_or_trajectory_imported", "all_lines_mutable"):
                bad = copy.deepcopy(gate); bad[key] = not bad[key]
                yield stage+"_"+key, stage, bad; count += 1
            for key in ("n", "point_degree", "ordered_triples", "proposal_population"):
                for suffix, value in (("wrong", gate[key]+1), ("bool", True), ("float", float(gate[key]))):
                    bad = copy.deepcopy(gate); bad[key] = value
                    yield stage+"_"+key+"_"+suffix, stage, bad; count += 1
            for key in graph:
                bad = copy.deepcopy(gate); bad["graph_input"].pop(key)
                yield stage+"_graph_missing_"+key, stage, bad; count += 1
    for key in ("status", "producer", "verifier", "target_resolution"):
        bad = copy.deepcopy(warm); bad[key] = "wrong"
        yield "WARM_AUDIT_"+key, "WARM_AUDIT", bad; count += 1
    for key in warm["inputs_sha256"]:
        bad = copy.deepcopy(warm); bad["inputs_sha256"].pop(key)
        yield "WARM_AUDIT_missing_"+str(count), "WARM_AUDIT", bad; count += 1
    for key in ("saved_state_files", "complete_integer_saved_current_best_objects"):
        for suffix, value in (("wrong", warm[key]+1), ("bool", True), ("float", float(warm[key]))):
            bad = copy.deepcopy(warm); bad[key] = value
            yield "WARM_AUDIT_"+key+"_"+suffix, "WARM_AUDIT", bad; count += 1
    for key in ("domain_valid", "srg_valid"):
        bad = copy.deepcopy(warm); bad["final_best_diagnostics"][key] = not bad["final_best_diagnostics"][key]
        yield "WARM_AUDIT_diag_"+key, "WARM_AUDIT", bad; count += 1
    for key in ("ordered_entries_checked", "lambda_energy", "mu_energy", "base_energy", "identity_mismatches"):
        for suffix, value in (("wrong", warm["final_best_diagnostics"][key]+1), ("bool", True), ("float", float(warm["final_best_diagnostics"][key]))):
            bad = copy.deepcopy(warm); bad["final_best_diagnostics"][key] = value
            yield "WARM_AUDIT_diag_"+key+"_"+suffix, "WARM_AUDIT", bad; count += 1
    io.need(count == 179, "DECLARED_CONTROL_POPULATION")


def metadata_check(stage, value, software, kernel_software):
    if stage == "WARM_AUDIT": check_warm(value)
    else: check_gate(stage.removesuffix("_GATE"), value, software, kernel_software, synthetic_graph())


def reject(name, expected_stage, call):
    try:
        call()
    except io.AuditError as error:
        io.need(error.stage == expected_stage, "CONTROL_STAGE", name+":"+error.stage)
        return dict(case=name, expected_stage=expected_stage, actual_stage=error.stage, diagnostic=str(error))
    raise io.AuditError("CONTROL_ACCEPTED", name)


def synthetic_wire(n, degree, rows):
    return (f"HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2\nn {n}\ndegree {degree}\ncurrent 0\nbest {len(rows)}\n"
        + "".join(" ".join(map(str, row))+"\n" for row in rows)+"cn 0\nEND\n").encode("ascii")


def replay_fixture(root, name, n, degree, rows, software, reserve, synthetic=False):
    raw = synthetic_wire(n, degree, rows) if synthetic else (root/(name+".state")).read_bytes()
    base = state_graph(raw)
    io.need(io.same(base.rows, rows), "FIXTURE_ORDERED_ROWS")
    matrix = io.matrix_bytes(base.adjacency) if synthetic else (root/(name+".adj")).read_bytes()
    matrix_graph(matrix, base)
    identity = dict(synthetic_fixture=name, objective=core.OBJECTIVE, software=software)
    records = [core.expected_record(base, pid)[0] for pid in range(17)] if synthetic else None
    runs = {}; visits = cps = zeros = valid = 0
    for suffix, start, stop in (("whole17", 0, 17), ("prefix7", 0, 7), ("resumed17", 7, 17)):
        reserve(); directory = root/(name+"_"+suffix)
        if synthetic:
            manifest = kernel.emit_synthetic(base, directory, identity, records, stop,
                prefix=None if suffix != "resumed17" else runs["prefix7"][0])
        else: manifest = io.strict_json((directory/"manifest.json").read_bytes())
        kernel.named_boundary(manifest, start, stop)
        result = kernel.audit_run(base, directory, manifest, identity, reserve)
        zero = kernel.audit_objects(base, directory, manifest, result)
        visits += len(result["records"]); cps += len(result["checkpoints"]); zeros += len(zero)
        runs[suffix] = (manifest, result)
        if suffix == "whole17":
            for record in result["records"]:
                reserve(); _, adj, cn = core.expected_record(base, record["proposal_id"])
                if record["valid"]:
                    kernel.scalar_check(base, record["proposal_id"], record, adj, cn); valid += 1
    whole, prefix, resumed = (runs[key] for key in ("whole17", "prefix7", "resumed17"))
    io.need(io.same(whole[1]["records"], resumed[1]["records"])
        and io.same(whole[0]["aggregate"], resumed[0]["aggregate"])
        and io.same(prefix[0]["parts"], resumed[0]["parts"][:len(prefix[0]["parts"])]), "PREFIX_ORIGINAL_IDENTITY")
    return base, raw, matrix, runs, dict(distinct_prefix_labels=17, streamed_evaluation_calls=34,
        prefix_resume_equal=True, raw_record_visits=visits, checkpoint_prefixes=cps, zero_object_checks=zeros,
        valid_prefix_labels=valid, baseline_metrics=base.metrics, aggregate=whole[0]["aggregate"])


def calibration(out, software, kernel_software, reserve):
    negatives = []; fixtures = {}
    for name, (n, degree, rows) in kernel.fixtures().items():
        base, raw, matrix, runs, result = replay_fixture(out, name, n, degree, rows, software, reserve, synthetic=True)
        fixtures[name] = result
        (out/(name+".state")).write_bytes(raw); (out/(name+".adj")).write_bytes(matrix)
        for case, stage, state_bad, matrix_bad in wire_cases(name, n, raw, matrix):
            reserve(); bad = state_bad if state_bad is not None else matrix_bad
            (out/(case+".wire")).write_bytes(bad)
            negatives.append(reject(case, stage, lambda s=state_bad, m=matrix_bad:
                state_graph(s) if s is not None else matrix_graph(m, base)))
    graph, gates, warm = synthetic_gates(software, kernel_software)
    for stage, gate in gates.items():
        metadata_check(stage, gate, software, kernel_software); kernel.save(out/(stage+"_positive.json"), gate)
    check_warm(warm); kernel.save(out/"WARM_AUDIT_positive.json", dict(synthetic_metadata_only=True, audit=warm))
    for case, stage, bad in metadata_cases(software, kernel_software):
        reserve(); kernel.save(out/(case+".json"), bad)
        negatives.append(reject(case, stage, lambda s=stage, b=bad: metadata_check(s, b, software, kernel_software)))
    io.need(len(negatives) == 179, "DECLARED_CONTROL_POPULATION")
    # New named-run controls apply the original-prefix boundary to this caller,
    # without rerunning the already approved complete kernel universe.
    for suffix, start, stop in (("whole17",0,17),("prefix7",0,7),("resumed17",7,17)):
        bad = copy.deepcopy(runs[suffix][0]); bad["starting_proposal_id"] = start+1
        case = "named_boundary_"+suffix
        kernel.save(out/(case+".json"), bad)
        negatives.append(reject(case, "NAMED_RUN_BOUNDARY", lambda b=bad, a=start, z=stop: kernel.named_boundary(b,a,z)))
    kernel.save(out/"negative_controls.json", negatives)
    return dict(producer_outputs_checked=False, actual_target_input_read=False, complete_wire_fixture_roundtrips=3,
        unique_fixture_prefix_labels=51, streamed_evaluation_calls=102, all_raw_record_visits=123,
        whole_prefix_resume_equalities=3, synthetic_gate_positives=4, strict_negative_controls=len(negatives),
        native_counterpart_cases=179, fixtures=fixtures)


def profile(author, manifest, terminal, plan, admission, software):
    command = plan.get("command")
    child = ["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python",
        CALLER,"controls","--seconds","100","--out",AUTHOR,"--source-commit","63437c9b9fc2dd58b3bdfb51fc347b880b397503"]
    worker = ["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",*child[13:]]
    io.need(type(command) is list and len(command) == 36 and command.count("--") == 1
        and command[:6] == ["/usr/bin/python3","acceleration/run_compute_command.py","--seconds","120","--shutdown-reserve-seconds","20"]
        and io.same(command[command.index("--")+1:],child) and io.same(manifest.get("command"),child)
        and manifest.get("cwd") == "/mnt/c/Users/ikuto/projects/conway-99-graph"
        and manifest.get("source_sha256") == kernel.STATIC["acceleration/run_compute_command.py"]
        and manifest.get("seconds") == 120.0 and manifest.get("shutdown_reserve_seconds") == 20.0, "LINUX_COMMAND_PROFILE")
    io.need(io.same(author.get("command"),worker) and author.get("cwd") == manifest["cwd"]
        and author.get("python") == "3.12.3" and author.get("tqdm") == "4.67.1", "LINUX_CHILD_BINDING")
    cleanup = terminal.get("cleanup")
    io.need(type(cleanup) is dict and cleanup.get("reaped") is True and io.integer(cleanup.get("actual_exit_code"))
        and cleanup["actual_exit_code"] == 0 and cleanup.get("cleanup_errors") == [] and cleanup.get("process_group_live_pids") == []
        and cleanup.get("job_active_zero_observed") is True and io.integer(terminal.get("command_exit_code"))
        and terminal["command_exit_code"] == 0 and terminal.get("invocation_id") == manifest.get("invocation_id"), "LINUX_TERMINAL")
    probe = admission.get("default_uid_probe"); admitted_plan = admission.get("plan")
    io.need(admission.get("schema") == "TERNARY_TWO_LINE_CALLER_V1_AUTHOR_CONTROLS_ADMISSION_V1" and type(probe) is dict
        and probe.get("command") == ["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"]
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"] == "1000"
        and io.integer(probe.get("exit_code")) and probe["exit_code"] == 0 and admission.get("admitted") is True
        and admission.get("scientific_launched") is False and admission.get("actual99_read") is False
        and type(admitted_plan) is dict and admitted_plan.get("path") == PLAN and admitted_plan.get("sha256") == PLAN_SHA
        and io.integer(admitted_plan.get("words")) and admitted_plan["words"] == 36, "UID_ADMISSION")
    records = admission.get("source_pins")
    io.need(type(records) is list and len(records) == 20 and all(type(r) is dict and r.get("matched") is True for r in records)
        and {r.get("path"):r.get("sha256") for r in records} == software, "ADMISSION_SOURCE_PINS")


def actual(out, pins, software, kernel_software, reserve, args):
    fixed = {AUTHOR+"/summary.json":"f2ea6bddd4c79398e9de3a740edf85c53c5a1c84f1dca2f44bb7feb66e916a0d",
        RUNTIME+"/manifest.json":"e59cc7a92d281c495dcb941ed55cb3b1b66c2f0da5c5cf542fa722c3010971ed",
        RUNTIME+"/summary.json":"625e6a3e17e2cd2312a86c2dcee7e597bde113af803f0b415e512cfe490eb691",
        ADMISSION:args.author_admission_sha256,KERNEL_GATE:KERNEL_GATE_SHA}
    for path, identity in fixed.items():
        reserve(); io.need(type(identity) is str and len(identity) == 64 and io.sha(ROOT/path) == identity,"AUTHOR_INPUT_IDENTITY",path)
        pins[path] = identity
    root = ROOT/AUTHOR; author = io.strict_json((root/"summary.json").read_bytes())
    manifest = io.strict_json((ROOT/RUNTIME/"manifest.json").read_bytes()); terminal = io.strict_json((ROOT/RUNTIME/"summary.json").read_bytes())
    admission = io.strict_json((ROOT/ADMISSION).read_bytes()); plan = io.strict_json((ROOT/PLAN).read_bytes())
    profile(author,manifest,terminal,plan,admission,software)
    genuine_kernel = io.strict_json((ROOT/KERNEL_GATE).read_bytes())
    check_gate("KERNEL", genuine_kernel,software,kernel_software,None)
    io.need(author.get("status") == "AUTHOR_TERNARY_TWO_LINE_CALLER_V1_CONTROLS_PENDING_INDEPENDENT_GATE"
        and author.get("producer") == "/root/native_driver" and io.same(author.get("software"),software)
        and io.same(author.get("kernel_software"),kernel_software) and author.get("actual_target_input_read") is False
        and author.get("scientific_census_launched") is False and author.get("historical_native_state_written") is False
        and author.get("independent_approval") is False and author.get("target_resolution") == "NONE"
        and author.get("source_reference_commit") == "63437c9b9fc2dd58b3bdfb51fc347b880b397503", "AUTHOR_SCOPE")
    negatives = []; results = {}; fixtures = list(kernel.fixtures())
    for name,(n,degree,rows) in kernel.fixtures().items():
        base, raw, matrix, runs, result = replay_fixture(root,name,n,degree,rows,software,reserve)
        results[name] = result
        expected_counts = dict(distinct_prefix_labels=17,streamed_evaluation_calls=34,prefix_resume_equal=True)
        io.need(io.same(author.get("finite_prefix_counts",{}).get(name),expected_counts), "AUTHOR_FIXTURE_COUNTS")
        for case,stage,bad_state,bad_matrix in wire_cases(name,n,raw,matrix):
            reserve(); expected = bad_state if bad_state is not None else bad_matrix
            saved = (root/(case+".wire")).read_bytes(); io.need(saved == expected,"SAVED_CONTROL_CONTENT",case)
            negatives.append(reject(case,stage,lambda s=bad_state,m=bad_matrix:
                state_graph(s) if s is not None else matrix_graph(m,base)))
    graph,gates,warm = synthetic_gates(software,kernel_software)
    for stage,gate in gates.items():
        value = io.strict_json((root/(stage+"_positive.json")).read_bytes())
        io.need(io.same(value,gate),"SAVED_POSITIVE_CONTENT",stage); metadata_check(stage,value,software,kernel_software)
    value = io.strict_json((root/"WARM_AUDIT_positive.json").read_bytes())
    io.need(io.same(value,dict(synthetic_metadata_only=True,audit=warm)),"SAVED_POSITIVE_CONTENT"); check_warm(value["audit"])
    for case,stage,bad in metadata_cases(software,kernel_software):
        reserve(); value = io.strict_json((root/(case+".json")).read_bytes())
        io.need(io.same(value,bad),"SAVED_CONTROL_CONTENT",case)
        negatives.append(reject(case,stage,lambda s=stage,v=value: metadata_check(s,v,software,kernel_software)))
    io.need(io.same(author.get("fixture_positives"),fixtures) and io.integer(author.get("synthetic_gate_positives"))
        and author["synthetic_gate_positives"] == 4 and io.integer(author.get("strict_negative_count"))
        and author["strict_negative_count"] == 179 and type(author.get("strict_negatives")) is list
        and len(author["strict_negatives"]) == 179, "AUTHOR_CONTROL_POPULATION")
    for own, reported in zip(negatives,author["strict_negatives"]):
        io.need(reported.get("case") == own["case"] and reported.get("expected_stage") == own["expected_stage"]
            and reported.get("actual_stage") == own["actual_stage"], "AUTHOR_CONTROL_STAGE")
    for directory in (root,ROOT/RUNTIME):
        for path in sorted(directory.rglob("*")):
            if path.is_file(): reserve(); pins[path.relative_to(ROOT).as_posix()] = io.sha(path)
    kernel.save(out/"author_negative_replay.json",negatives)
    return dict(unique_fixture_prefix_labels=51,streamed_evaluation_calls=102,all_raw_record_visits=123,
        strict_author_negative_cases=179,whole_prefix_resume_equalities=3,complete_wire_fixture_roundtrips=3,
        synthetic_gate_positives=4,complete_checkpoint_prefixes=sum(r["checkpoint_prefixes"] for r in results.values()),
        complete_zero_object_checks=sum(r["zero_object_checks"] for r in results.values()),fixtures=results,
        actual_target_input_read=False,scientific_census_launched=False,historical_native_state_written=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["calibration","check"])
    for name in ("out","calibration"): parser.add_argument("--"+name,type=Path,required=name=="out")
    parser.add_argument("--seconds",type=float,required=True)
    for name in ("self-sha256","spec-sha256","source-commit"): parser.add_argument("--"+name,required=True)
    parser.add_argument("--calibration-sha256"); parser.add_argument("--author-admission-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason="Changed caller wire/gate51prefix/179negative finite controls or raw artifact replay only; inclusive setup/hashes/reserve; no actual99/science/retry")
    out = args.out.resolve(); io.need(out.is_relative_to(ROOT) and not out.exists(),"OUTPUT_PATH")
    pins = {**STATIC,SELF:args.self_sha256,SPEC:args.spec_sha256}
    for path,value in pins.items(): io.need(io.sha(ROOT/path) == value,"SOURCE_IDENTITY",path)
    core.authenticate(ROOT)
    plan = io.strict_json((ROOT/PLAN).read_bytes()); software = software_order(plan.get("inputs_sha256"))
    kernel_software = {path:value for path,value in software.items() if path not in (CALLER,CALLER_SPEC)}
    for path,value in software.items(): io.need(io.sha(ROOT/path) == value,"SOURCE_IDENTITY",path); pins[path] = value
    out.mkdir(parents=True)
    def reserve(): io.need(deadline.status()["remaining_seconds"] > 20 and not deadline.status()["stop_required"],"DEADLINE_RESERVE")
    try:
        if args.mode == "calibration": result = calibration(out,software,kernel_software,reserve); status = CAL_PASS
        else:
            io.need(args.calibration is not None and args.calibration.resolve().is_relative_to(ROOT)
                and type(args.calibration_sha256) is str and io.sha(args.calibration) == args.calibration_sha256,"CALIBRATION_IDENTITY")
            cal = io.strict_json(args.calibration.read_bytes())
            io.need(cal.get("status") == CAL_PASS and cal.get("verifier") == "/root/structural"
                and cal.get("producer_outputs_checked") is False and cal.get("actual_target_input_read") is False
                and io.integer(cal.get("strict_negative_controls")) and cal["strict_negative_controls"] == 182
                and all(cal.get("inputs_sha256",{}).get(path) == value for path,value in pins.items()),"CALIBRATION_SCOPE")
            pins[args.calibration.resolve().relative_to(ROOT).as_posix()] = args.calibration_sha256
            for path,value in cal.get("outputs_sha256",{}).items():
                reserve(); io.need(io.sha(io.relative_file(ROOT,path,args.calibration.parent)) == value,"CALIBRATION_OUTPUT_IDENTITY"); pins[path] = value
            result = actual(out,pins,software,kernel_software,reserve,args); status = CALLER_PASS
        outputs = {path.relative_to(ROOT).as_posix():io.sha(path) for path in sorted(out.rglob("*")) if path.is_file()}
        kernel.save(out/"summary.json",dict(status=status,producer="/root/native_driver" if args.mode=="check" else None,
            verifier="/root/structural",method="independent_artifact_check" if args.mode=="check" else "independent_finite_controls",
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            numpy=np.__version__,source_context=args.source_commit,inputs_sha256=pins,
            shared_components=["acceleration/audit_20261003_ternary_two_line_controls_v1.py",kernel.RAW_CORE,core.SHARED],
            outputs_sha256=outputs,**result,target_resolution="NONE",scientific_launched=False,deadline=deadline.status()))
    except BaseException as error:
        kernel.save(out/"failure.json",dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),
            preserved_partial_outputs=True,automatic_retry=False,target_resolution="NONE")); raise


if __name__ == "__main__": main()
