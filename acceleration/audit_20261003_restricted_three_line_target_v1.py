"""SOURCE ONLY: one fixed actual99 restricted-three-line complete raw audit.

No producer imports, optimization or scientific discovery execution. The frozen
independent rawcore performs every complete row replacement and exact int64 A@A.
This new scope/receipt/identity/SRG wrapper needs its own applicable calibration.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/audit_20261003_restricted_three_line_target_v1.py"
SPEC = "acceleration/audit_20261003_restricted_three_line_target_v1_spec.md"
CORE = "acceleration/audit_20261003_restricted_three_line_raw_core_v1.py"
META = "acceleration/audit_20261003_restricted_three_line_controls_v1.py"
PLAN = "acceleration/plan_20261003_restricted_three_line_selected145287_science_v1.json"
GRAPH = "acceleration/results/20261003_root_focused_selected145287_projection01/graph_input.json"
INPUT_GATE = "acceleration/results/20261003_independent_review/root_focused_selected145287_projection_full01/summary.json"
GATE_ROOT = "acceleration/results/20261003_independent_review/restricted_three_line_combined_controls01/"
NATIVE_OUT = "acceleration/results/20261003_restricted_three_line_selected145287_census01"
NATIVE_SUP = "acceleration/results/20261003_restricted_three_line_selected145287_census_supervision01"
REFS = {
    GRAPH: "203204c24e3a2f4901cabd85f9c3f740db5b053831393db65c201a3773ff1748",
    INPUT_GATE: "b664c631ec37c8d4cbd08d395aebed538f8acdfebf8f4c751be731fd0b9152de",
    GATE_ROOT + "kernel_controls_gate.json": "7769ca4bd996269bf442f1c468cb06eb407a3b2dde7629477a66572c20243cfd",
    GATE_ROOT + "caller_controls_gate.json": "df014c7a5cab3d6584f7a1fd663effe357ffaee7d79065d8ea3b1d5882947a07",
}
PINS = {
    CORE: "98efe2641fe2952857efaa62b7812b0abe7a0f87ce4550bf64544a4ba3ebaa95",
    META: "5d4b6d778b88f7bf4cf7f6fbb02cac28bdd746037c0e05123c59d891dfb17550",
    "acceleration/audit_20261003_restricted_three_line_controls_v1_spec.md": "6bc81c100e2ff411016551532a9e3ec1c24bca8a4d8f775d23d16db330c5f8fd",
    "acceleration/results/20261003_independent_review/restricted_three_line_raw_calibration01/summary.json": "ba21cbd99ee8d14ba015c16eaf9cd81733ef90b51cffa5c8e6429420ec91f715",
    PLAN: "d9e9333eeccbc8ff0cf75049137bda5b0c2e1ea14b8dea2be25a981aa71aac33",
    "acceleration/protocol_20261003_restricted_three_line_selected145287_science_v1.md": "f6057909c061c6c38e69ed95fce6a4d85ef60bb9d2902badefffe14f61f5e24e",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
PROVENANCE = dict(mode="actual_independently_checked_strict_lex_selection", selected_proposal_id=145287,
    source_manifest=dict(path="acceleration/results/20261003_root_focused_strict_lex_step1_census01/manifest.json", sha256="bbec654446297fa955972724673f43ef4687d0778c9aa614250adca776af878c"),
    source_matrix=dict(path="acceleration/results/20261003_root_focused_strict_lex_step1_census01/best_root_neighbor.adj", sha256="6bb186fe59bc415c1366b201b4559f1ca2488be49ea56a9e5ce4d2dd7b66a617"),
    source_triples=dict(path="acceleration/results/20261003_root_focused_strict_lex_step1_census01/best_root_neighbor_triples.json", sha256="3967bdddfd638f931f52a6e2975cab3fb9ef24f4f588edbeccbf15f020ea147b"),
    source_complete_audit=dict(path="acceleration/results/20261003_independent_review/root_focused_strict_lex_step1_full01/summary.json", sha256="c62722ac0bf54f5166ee692d84822dd0124dde5af2a2b4fb4c9c620cc4c6e471", status="INDEPENDENT_FROZEN_ROOT_STRICT_LEX_TWO_LINE_V1_COMPLETE_PASS"),
    source_baseline_metrics=dict(E_lambda=0, E_mu=5344, R_root=10), historical_native_state_written=False)


def load_module(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value; spec.loader.exec_module(value)
    return value


def save(path, value):
    with path.open("x", encoding="utf8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write("\n")


def header(core, gate, status, software):
    core.need(type(gate) is dict and gate.get("status") == status and gate.get("producer") == "/root/native_driver"
        and gate.get("verifier") == "/root/structural" and gate.get("method") == "independent_artifact_check"
        and gate.get("target_resolution") == "NONE" and type(gate.get("inputs_sha256")) is dict
        and all(gate["inputs_sha256"].get(k) == v for k, v in software.items()), "GATE_HEADER")


def srg(core, adjacency, n, k):
    np = core.np
    core.need(type(adjacency) is np.ndarray and adjacency.dtype == np.dtype("int64")
              and adjacency.shape == (n, n), "SRG_MATRIX_TYPES")
    core.need(np.array_equal(adjacency, adjacency.T) and np.all((adjacency == 0) | (adjacency == 1))
              and np.all(np.diag(adjacency) == 0), "SRG_MATRIX_DOMAIN")
    core.need(np.all(adjacency.sum(axis=1) == k), "SRG_DEGREE")
    target = (k - 2) * np.eye(n, dtype=np.int64) - adjacency + 2 * np.ones((n, n), dtype=np.int64)
    core.need(np.array_equal(adjacency @ adjacency, target), "SRG_INTEGER_IDENTITY")
    return dict(n=n, k=k, lambda_value=1, mu_value=2, entries_checked=n * n, exact_arithmetic="signedint64, products <=n and all values far below overflow")


def profile(core, meta, runtime, terminal, receipt, plan):
    command = plan.get("command")
    core.need(type(command) is list and len(command) == 44 and command.count("--") == 1
        and core.same(runtime.get("command"), command[command.index("--") + 1:])
        and runtime.get("cwd") == "/mnt/c/Users/ikuto/projects/conway-99-graph"
        and runtime.get("source_sha256") == meta.SOFTWARE["acceleration/run_compute_command.py"]
        and runtime.get("seconds") == 600.0 and runtime.get("shutdown_reserve_seconds") == 20.0, "SCIENTIFIC_LINUX_PROFILE")
    worker = ["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",
              *command[command.index("python") + 1:]]
    core.need(core.same(receipt.get("command"), worker) and receipt.get("cwd") == runtime["cwd"]
        and receipt.get("python") == "3.12.3" and receipt.get("tqdm") == "4.67.1"
        and receipt.get("source_reference_commit") == plan.get("source_reference_commit")
        and receipt.get("producer") == "/root/native_driver" and receipt.get("historical_native_state_written") is False
        and receipt.get("scientific_census_launched") is True and receipt.get("independent_approval") is False
        and receipt.get("target_resolution") == "NONE", "SCIENTIFIC_WORKER_RECEIPT")
    clean = terminal.get("cleanup")
    core.need(type(clean) is dict and clean.get("reaped") is True and clean.get("job_active_zero_observed") is True
        and core.integer(clean.get("actual_exit_code")) and clean["actual_exit_code"] == 0
        and clean.get("cleanup_errors") == [] and clean.get("process_group_live_pids") == []
        and core.integer(terminal.get("command_exit_code")) and terminal["command_exit_code"] == 0
        and terminal.get("invocation_id") == runtime.get("invocation_id"), "SCIENTIFIC_LINUX_TERMINAL")


def admission(core, value, plan):
    """Historical pre-dispatch metadata only; no present process-state inference."""
    probe = value.get("default_uid_probe", {}) if type(value) is dict else {}
    core.need(type(value) is dict and value.get("schema") == "RESTRICTED_THREE_LINE_SELECTED145287_SCIENCE_ADMISSION_V1"
        and value.get("admitted") is True and value.get("scientific_launched") is False
        and value.get("independent_approval") is False and value.get("target_resolution") == "NONE"
        and type(probe) is dict and core.same(probe.get("command"), ["wsl.exe", "-d", "Ubuntu-24.04", "--", "/usr/bin/id", "-u"])
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"] == "1000"
        and core.integer(probe.get("exit_code")) and probe["exit_code"] == 0
        and type(value.get("plan")) is dict and value["plan"].get("path") == PLAN
        and value["plan"].get("sha256") == PINS[PLAN]
        and type(value["plan"].get("words")) is int and value["plan"]["words"] == len(plan["command"]), "SCIENTIFIC_UID_ADMISSION")


def identity(inputs, software, graph, universe, context):
    return dict(inputs_sha256=inputs, software=software, graph_input_path=GRAPH, graph_input_sha256=REFS[GRAPH],
        input_gate_sha256=REFS[INPUT_GATE], kernel_controls_gate_sha256=REFS[GATE_ROOT + "kernel_controls_gate.json"],
        caller_controls_gate_sha256=REFS[GATE_ROOT + "caller_controls_gate.json"], n=99, degree=7, root=11,
        total=universe["proposal_count"], source_reference_commit=context,
        source_reference_scope="Published context only; exact new source/raw/gates separately pinned, availability not inferred.",
        graph_only_input=True, historical_native_state_written=False, input_provenance=graph["provenance"],
        frozen_rows=graph["frozen_rows"], mutable_labels=graph["mutable_labels"], universe=universe,
        question="Does this exact checked graph have a valid lambda-preserving root-R-descending proposal in this distinct-selected CN1/CN3 oriented role family? Mu may worsen.",
        role_population_scope="All declared raw roles including invalid selected repeats; not all three-line moves, a plateau or graph-space coverage.")


def calibrate(core, meta, plan, out):
    controls = []
    def reject(case, stage, call):
        try: call()
        except core.AuditError as error:
            core.need(error.stage == stage, "CONTROL_STAGE", case)
            controls.append(dict(case=case, expected_stage=stage, actual_stage=error.stage, outcome="REJECTED")); return
        raise core.AuditError("CONTROL_ACCEPTED", case)
    np = core.np
    rows = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8]]
    known = core.geometry(9, 2, rows, 0); positive = srg(core, known, 9, 4)
    for case, bad in (("uint8", known.astype(np.uint8)), ("boolean_dtype", known.astype(bool)),
                      ("float_dtype", known.astype(float)), ("matrix_shape", known[:8,:8])):
        reject(case, "SRG_MATRIX_TYPES", lambda v=bad: srg(core, v, 9, 4))
    for case, at, value in (("nonbinary", (0,1), 2), ("diagonal", (0,0), 1), ("asymmetric", (0,1), 0)):
        bad = known.copy(); bad[at] = value
        if case == "nonbinary": bad[at[::-1]] = value
        reject(case, "SRG_MATRIX_DOMAIN", lambda v=bad: srg(core, v, 9, 4))
    bad = known.copy(); bad[0,1] = bad[1,0] = 0
    reject("wrong_degree", "SRG_DEGREE", lambda: srg(core, bad, 9, 4))
    bad = np.zeros((9,9), dtype=np.int64)
    for x in range(9):
        for delta in (-2,-1,1,2): bad[x, (x+delta)%9] = 1
    reject("regular_corrupted_identity", "SRG_INTEGER_IDENTITY", lambda: srg(core, bad, 9, 4))
    runtime = dict(command=plan["command"][plan["command"].index("--") + 1:], cwd="/mnt/c/Users/ikuto/projects/conway-99-graph",
        source_sha256=meta.SOFTWARE["acceleration/run_compute_command.py"], seconds=600.0,
        shutdown_reserve_seconds=20.0, invocation_id="SYNTHETIC_NOT_EXECUTED")
    receipt = dict(command=["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",
        *plan["command"][plan["command"].index("python") + 1:]], cwd=runtime["cwd"], python="3.12.3", tqdm="4.67.1",
        source_reference_commit=plan["source_reference_commit"], producer="/root/native_driver", historical_native_state_written=False,
        scientific_census_launched=True, independent_approval=False, target_resolution="NONE")
    terminal = dict(invocation_id=runtime["invocation_id"], command_exit_code=0, cleanup=dict(reaped=True,
        job_active_zero_observed=True, actual_exit_code=0, cleanup_errors=[], process_group_live_pids=[]))
    profile(core, meta, runtime, terminal, receipt, plan)
    for case, stage, at, field, value in (("source_child", "SCIENTIFIC_LINUX_PROFILE", 0, "command", ["wrong"]),
        ("source_cwd", "SCIENTIFIC_LINUX_PROFILE", 0, "cwd", "wrong"),
        ("worker_command", "SCIENTIFIC_WORKER_RECEIPT", 2, "command", ["wrong"]),
        ("worker_history", "SCIENTIFIC_WORKER_RECEIPT", 2, "historical_native_state_written", True),
        ("worker_self_approval", "SCIENTIFIC_WORKER_RECEIPT", 2, "independent_approval", True),
        ("invocation", "SCIENTIFIC_LINUX_TERMINAL", 1, "invocation_id", "wrong"),
        ("boolean_exit", "SCIENTIFIC_LINUX_TERMINAL", 1, "command_exit_code", False)):
        objects = copy.deepcopy([runtime, terminal, receipt]); objects[at][field] = value
        reject(case, stage, lambda v=objects: profile(core, meta, *v, plan))
    bad = copy.deepcopy(terminal); bad["cleanup"]["process_group_live_pids"] = [1]
    reject("live_linux_group", "SCIENTIFIC_LINUX_TERMINAL", lambda: profile(core, meta, runtime, bad, receipt, plan))
    uid = dict(schema="RESTRICTED_THREE_LINE_SELECTED145287_SCIENCE_ADMISSION_V1", admitted=True,
        scientific_launched=False, independent_approval=False, target_resolution="NONE",
        plan=dict(path=PLAN, sha256=PINS[PLAN], words=len(plan["command"])),
        default_uid_probe=dict(command=["wsl.exe", "-d", "Ubuntu-24.04", "--", "/usr/bin/id", "-u"], stdout_uid="1000", exit_code=0))
    admission(core, uid, plan)
    for case, section, key, replacement in (("UID_boolean", "default_uid_probe", "stdout_uid", True),
        ("UID_root", "default_uid_probe", "stdout_uid", "0"), ("UID_integer", "default_uid_probe", "stdout_uid", 1000),
        ("UID_other_probe", "default_uid_probe", "command", ["wrong"]), ("UID_plan_hash", "plan", "sha256", "wrong"),
        ("UID_not_admitted", None, "admitted", False), ("UID_already_launched", None, "scientific_launched", True),
        ("UID_self_approval", None, "independent_approval", True)):
        bad = copy.deepcopy(uid); (bad if section is None else bad[section])[key] = replacement
        reject(case, "SCIENTIFIC_UID_ADMISSION", lambda v=bad: admission(core, v, plan))
    good = dict(status="FINITE_SYNTHETIC_GATE", producer="/root/native_driver", verifier="/root/structural",
        method="independent_artifact_check", target_resolution="NONE", inputs_sha256=meta.CALLER_SOFTWARE)
    header(core, good, "FINITE_SYNTHETIC_GATE", meta.CALLER_SOFTWARE)
    for field in ("status", "producer", "verifier", "method", "target_resolution", "inputs_sha256"):
        bad = copy.deepcopy(good); bad[field] = {} if field == "inputs_sha256" else "wrong"
        reject("gate_" + field, "GATE_HEADER", lambda v=bad: header(core, v, "FINITE_SYNTHETIC_GATE", meta.CALLER_SOFTWARE))
    meta.run_boundary(core, dict(starting_proposal_id=0, completed_proposals=0, proposals_evaluated_this_invocation=0), 0, 0)
    for field in ("starting_proposal_id", "completed_proposals", "proposals_evaluated_this_invocation"):
        for suffix, value in (("boolean", False), ("float", 0.0)):
            bad = dict(starting_proposal_id=0, completed_proposals=0, proposals_evaluated_this_invocation=0); bad[field] = value
            reject(field + suffix, "NAMED_RUN_BOUNDARY", lambda v=bad: meta.run_boundary(core, v, 0, 0))
    core.need(len(controls) == 37, "CONTROL_POPULATION")
    save(out / "strict_negative_controls.json", controls)
    save(out / "synthetic_profile_not_executed.json", dict(synthetic_not_executed=True, runtime=runtime, terminal=terminal, receipt=receipt, admission=uid))
    return dict(positive_interfaces=5, exact_rook_integer_entries=positive["entries_checked"], strict_negative_count=37,
        controls=controls, actual_target_input_read=False, actual_scientific_output_read=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["calibration", "check"])
    for field in ("out", "seconds", "self_sha256", "spec_sha256", "source_commit"):
        ap.add_argument("--" + field.replace("_", "-"), required=True, type=float if field == "seconds" else str)
    for field in ("calibration", "calibration_sha256", "manifest_sha256", "receipt_sha256", "runtime_manifest_sha256", "runtime_summary_sha256", "admission", "admission_sha256"):
        ap.add_argument("--" + field.replace("_", "-"))
    args = ap.parse_args(); deadline = CommandDeadline(args.seconds, allocation_reason="One fixedactual99 complete raw audit or new scope/receipt/integer-validator finite calibration; all hashes/reconstruction/saving included, no automatic retry")
    out = Path(args.out).resolve()
    if not out.is_relative_to(ROOT) or out.exists(): raise ValueError("OUTPUT_FRESH")
    out.mkdir(parents=True); pins = dict(PINS); pins.update({SELF:args.self_sha256, SPEC:args.spec_sha256})
    phase, last_heartbeat = "source hashes", time.monotonic()
    def reserve():
        nonlocal last_heartbeat
        if deadline.status()["remaining_seconds"] <= 20 or deadline.status()["stop_required"]:
            raise ValueError("DEADLINE: not completed within allocated budget; complete rechecking remains required")
        if time.monotonic() - last_heartbeat >= 20:
            print(json.dumps(dict(phase=phase, deadline=deadline.status(), completeness="PENDING; no sampled approval")), flush=True); last_heartbeat=time.monotonic()
    def pin(name, expected=None):
        reserve(); path=Path(name); path = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
        if not path.is_relative_to(ROOT) or ".git" in path.relative_to(ROOT).parts or path.name == "CLAIMS.yaml" or not path.is_file(): raise ValueError("INPUT_PATH")
        relative=path.relative_to(ROOT).as_posix()
        with path.open("rb") as stream: actual=hashlib.file_digest(stream,"sha256").hexdigest()
        if expected is not None and actual != expected or relative in pins and pins[relative] != actual: raise ValueError("INPUT_HASH:"+relative)
        pins[relative]=actual; return path
    try:
        for name, value in list(pins.items()): pin(name, value)
        core=load_module(CORE,"immutable_independent_restricted_raw_core"); meta=load_module(META,"immutable_independent_restricted_metadata")
        for name,value in meta.CALLER_SOFTWARE.items(): pin(name,value)
        plan=core.strict_json((ROOT/PLAN).read_bytes())
        if args.mode == "calibration":
            result=calibrate(core,meta,plan,out); status="INDEPENDENT_RESTRICTED_THREE_LINE_TARGET_V1_CALIBRATION_PASS"
        else:
            core.need(all(getattr(args,f) is not None for f in ("calibration","calibration_sha256","manifest_sha256","receipt_sha256","runtime_manifest_sha256","runtime_summary_sha256","admission","admission_sha256")),"REQUIRED_ARTIFACT_IDENTITIES")
            cal=core.strict_json(pin(args.calibration,args.calibration_sha256).read_bytes())
            core.need(cal.get("status")=="INDEPENDENT_RESTRICTED_THREE_LINE_TARGET_V1_CALIBRATION_PASS"
                and cal.get("inputs_sha256",{}).get(SELF)==args.self_sha256 and cal["inputs_sha256"].get(SPEC)==args.spec_sha256
                and cal.get("actual_target_input_read") is False,"CALIBRATION_REQUIRED")
            phase="original input and gate closure"
            reports={name:core.strict_json(pin(name,value).read_bytes()) for name,value in REFS.items() if name!=GRAPH}
            producer_inputs=dict(meta.CALLER_SOFTWARE); producer_inputs.update(REFS)
            for name,report in reports.items():
                status0="INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_COMPLETE_PASS" if name==INPUT_GATE else (
                    "INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_V3_CONTROLS_PASS" if "kernel_controls" in name else "INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_CALLER_V1_CONTROLS_PASS")
                header(core,report,status0,{})
                for member,value in report["inputs_sha256"].items():
                    pin(member,value); core.need(member not in producer_inputs or producer_inputs[member]==value,"PRODUCER_INPUT_UNION")
                    producer_inputs[member]=value
            graph=core.strict_json(pin(GRAPH,REFS[GRAPH]).read_bytes())
            core.need(type(graph) is dict and set(graph)==set("schema n degree root ordered_triples frozen_rows mutable_labels metrics provenance".split())
                and graph["schema"]=="FROZEN_ROOT_STRICT_LEX_GRAPH_INPUT_V1" and core.same(graph["provenance"],PROVENANCE)
                and all(type(graph[k]) is int and graph[k]==v for k,v in dict(n=99,degree=7,root=11).items()),"ACTUAL_INPUT_SCOPE")
            b=core.fixed_input(graph["n"],graph["degree"],graph["ordered_triples"],graph["root"]); d=core.domain(b)
            core.need(core.same(graph["frozen_rows"],[list(row) for row in b.frozen]) and core.same(graph["frozen_rows"],meta.FROZEN)
                and core.same(graph["mutable_labels"],list(b.mutable)) and core.same(graph["metrics"],dict(E_lambda=b.E_lambda,E_mu=b.E_mu,R_root=b.R_root))
                and (b.E_lambda,b.E_mu,b.R_root)==(0,5292,10),"ACTUAL_INPUT_GEOMETRY")
            universe=d["universe"]; count=len(d["roles"])
            core.need(len(universe["zero_neighbor_lines"])==140 and len(universe["one_neighbor_lines"])==84
                and count==7506*len(universe["under_vertices"])*len(universe["over_vertices"]),"DERIVED_ROLE_POPULATION")
            expected_identity=identity(producer_inputs,meta.CALLER_SOFTWARE,graph,universe,plan["source_reference_commit"])
            manifest=core.strict_json(pin(NATIVE_OUT+"/manifest.json",args.manifest_sha256).read_bytes())
            receipt=core.strict_json(pin(NATIVE_OUT+"/run_receipt.json",args.receipt_sha256).read_bytes())
            runtime=core.strict_json(pin(NATIVE_SUP+"/manifest.json",args.runtime_manifest_sha256).read_bytes())
            terminal=core.strict_json(pin(NATIVE_SUP+"/summary.json",args.runtime_summary_sha256).read_bytes())
            profile(core,meta,runtime,terminal,receipt,plan)
            admitted=core.strict_json(pin(args.admission,args.admission_sha256).read_bytes()); admission(core,admitted,plan)
            for field in ("windows","linux","supplementary_windows"):
                observation=admitted.get(field)
                core.need(type(observation) is dict and type(observation.get("path")) is str
                    and type(observation.get("sha256")) is str,"SCIENTIFIC_OBSERVATION_REFERENCE")
                pin(observation["path"],observation["sha256"])
            core.need(receipt.get("manifest_sha256")==args.manifest_sha256 and receipt.get("universe_sha256")==core.sha(pin(NATIVE_OUT+"/universe.json"))
                and all(type(receipt.get(k)) is int and receipt[k]==v for k,v in dict(actual_role_population=count,
                    actual_U_size=len(universe["under_vertices"]),actual_V_size=len(universe["over_vertices"])).items()),"ACTUAL_CENSUS_RECEIPT")
            core.need(core.same(core.strict_json((ROOT/NATIVE_OUT/"universe.json").read_bytes()),universe),"COMPLETE_UNIVERSE")
            meta.run_boundary(core,manifest,0,count); phase="all raw19field proposals and checkpoint prefixes"
            checked=core.audit_run(ROOT,ROOT/NATIVE_OUT,d,manifest,expected_identity,reserve)
            phase="all ties and selected literal objects"; core.audit_ties(ROOT/NATIVE_OUT,d,checked)
            aggregate=checked["aggregate"].snapshot(); zeros=[]; selected_validation=None
            if checked["selected"] is not None:
                pid=checked["selected"]["proposal_id"]; record,selected_adjacency,_=core.expected_record(d,pid)
                full_target=12*core.np.eye(99,dtype=core.np.int64)-selected_adjacency+2*core.np.ones((99,99),dtype=core.np.int64)
                selected_validation=dict(proposal_id=pid,metrics=dict(E_lambda=record["new_lambda"],E_mu=record["new_mu"],R_root=record["new_root_residual"]),
                    full_integer_entries_checked=9801,ordered_integer_identity_mismatches=int(core.np.count_nonzero(selected_adjacency@selected_adjacency!=full_target)),
                    raw_matrix_sha256=core.sha(ROOT/NATIVE_OUT/"selected_neighbor.adj"))
            for pid in aggregate["zero_score_proposal_ids"]:
                reserve(); _,adjacency,_=core.expected_record(d,pid); certificate=srg(core,adjacency,99,14)
                path=out/("candidate_srg99_"+str(pid)+".adj"); path.write_bytes(core.matrix_bytes(adjacency))
                zeros.append(dict(proposal_id=pid,artifact=path.relative_to(ROOT).as_posix(),sha256=core.sha(path),check=certificate))
            phase="final complete artifact hashes"; native_outputs={}
            for path in sorted((ROOT/NATIVE_OUT).rglob("*")):
                if path.is_file():
                    pinned=pin(str(path)); native_outputs[pinned.relative_to(ROOT).as_posix()]=pins[pinned.relative_to(ROOT).as_posix()]
            result=dict(complete_roles=count,actual_U=len(universe["under_vertices"]),actual_V=len(universe["over_vertices"]),
                role_count_definition="7506 times freshlyderived |U| times freshlyderived |V|; every invalid/unfavorable label retained",
                parts=len(manifest["parts"]),checkpoints=checked["checkpoints"],aggregate=aggregate,selected_proposal_id=manifest["selected_proposal_id"],
                exact_record_fields=19,selected_literal_integer_validation=selected_validation,candidate_srg99_objects=zeros,root_review_required=bool(zeros),
                selected_null_reason=None if selected_validation is not None else "Complete checked family contains no valid lambda-preserving proposal, hence no selected literal object exists.",
                valid_lambda_preserving_root_descents=aggregate["counts"].get("valid_lambda_preserving_root_down",0),
                exact_input_integer_CN_entries=9801,new_unrestricted_exclusions=0,
                scope="ONE fixed labelled graph/distinct-selected orientedCN1/CN3 family only; not all three-line/rootdescents/plateau/target coverage")
            status="INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_CALLER_V1_COMPLETE_PASS"
        statement=("The independently authored fixed-target wrapper passed its five declared positive interfaces and all 37 precise negative controls, including a complete exact 9-vertex SRG identity, synthetic source-bound Linux/UID receipts and typed named-run boundaries; it read no actual target graph or scientific output."
            if args.mode=="calibration" else
            "For the fixed 99-vertex root11 graph input with SHA256 "+REFS[GRAPH]+", every one of the "+str(count)+
            " freshly derived role-labelled selections in the declared distinct-selected CN1/CN3 oriented three-line family was independently reconstructed and compared with all 19 saved record fields, all "+str(len(manifest["parts"]))+
            " parts and their checkpoint prefixes, complete ties and any selected literal graph. The complete family contains "+str(result["valid_lambda_preserving_root_descents"])+
            " valid lambda-preserving root-residual descents. Selected or zero-score graph objects receive a separate complete integer adjacency calculation. This statement concerns only this fixed labelled one-move family and establishes no unrestricted target resolution or broader move-space absence.")
        save(out/"summary.json",dict(status=status,producer="/root/native_driver" if args.mode=="check" else "/root/structural",
            verifier="/root/structural",method="independent_artifact_check" if args.mode=="check" else "finite_checker_calibration",
            statement=statement,scope=dict(description="One fixed labelled graph and the exact distinct-selected CN1/CN3 oriented role family" if args.mode=="check" else "Five positive and 37 precise negative finite wrapper interfaces only",
                unrestricted_target=False,target_resolution="NONE"),
            timestamp=datetime.now(timezone.utc).isoformat(),source_context=args.source_commit,
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=core.np.__version__,
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():core.sha(p) for p in out.rglob("*") if p.is_file()},
            actual_target_input_read=args.mode=="check",result=result,deadline=deadline.status(),target_resolution="NONE",
            original_input=dict(path=GRAPH,sha256=REFS[GRAPH]) if args.mode=="check" else None,
            original_input_null_reason=None if args.mode=="check" else "Own finite calibration does not read the actual 99-vertex graph.",
            native_output_manifest=dict(path=NATIVE_OUT+"/manifest.json",sha256=args.manifest_sha256) if args.mode=="check" else None,
            native_output_manifest_null_reason=None if args.mode=="check" else "Own finite calibration does not read scientific output.",
            native_original_outputs_sha256=native_outputs if args.mode=="check" else None,
            native_original_outputs_null_reason=None if args.mode=="check" else "No producer scientific output is read by own calibration.",
            shared_components=["Immutable different-author rawcore98efe/int64 NumPy path, metadata5d4 constants/named-boundary function and rootlocked environment; no producer import/scorer/reviewer.",
                "Copied raw19field/schema/identity contract explicitly shared; original input alreadyindependently checkedb664 and finite gates7769/df014 remain separate exact dependencies."],
            limitations=["No rank/automorphism/prism/coverage/ergodicity/performance inference; raw exactzero requires ROOT review and public evidence package before repository resolution.",
                "Observed terminal cleanup is one insideLinux processgroup, not a WindowsJob or globalworker claim.",
                "Verifier itself has no saved partial accumulator; interrupted full audit remains incomplete and needs a separatelyauthorized full replay from0. Native raw checkpoints remain preserved."]))
        print(json.dumps(dict(status=status,mode=args.mode)),flush=True)
    except Exception as error:
        save(out/"failure.json",dict(error=repr(error),phase=phase,inputs_sha256=pins,deadline=deadline.status(),
            timestamp=datetime.now(timezone.utc).isoformat(),target_resolution="NONE",automatic_retry=False,
            incomplete="not completed within allocated budget if stopped; no partial/sample approval or absence theorem",restart="Preserve all raw/native checkpoints and failedreceipt. No automatic retry; new frozen invocation and ROOT review required.")); raise


if __name__=="__main__": main()
