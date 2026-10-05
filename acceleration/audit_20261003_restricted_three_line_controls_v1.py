"""SOURCE ONLY: narrow independent kernel95/caller97 finite artifact checker.

No producer imports and no actual target99 mode. Complete raw math delegates
only to our separately calibrated immutable raw core98efe. This changed caller
needs its own typed interface calibration and separate ROOT-reviewed commands.
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

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/audit_20261003_restricted_three_line_controls_v1.py"
SPEC = "acceleration/audit_20261003_restricted_three_line_controls_v1_spec.md"
RAW_CORE = "acceleration/audit_20261003_restricted_three_line_raw_core_v1.py"
SCALAR = "acceleration/audit_20261003_restricted_three_line_core_v2.py"
CAL = "acceleration/results/20261003_independent_review/restricted_three_line_raw_calibration01/summary.json"
SOFTWARE = {
 "acceleration/census_20261003_root_focused_two_line_v1.py": "bbc91ed768a07b302e0e417e8c4415925ef6fac01bd14d78051a56b723419017",
 "acceleration/census_20261003_root_focused_two_line_v1_spec.md": "9b2fcfc0b330b9183a47c0f3888126ef8dfe8a8dbb4d41366c9adf11006cdcc8",
 "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
 "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
 "acceleration/native_budget_env_v1/pyproject.toml": "96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782",
 "acceleration/native_budget_env_v1/uv.lock": "54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434",
 "acceleration/census_20261003_root_focused_restricted_three_line_v3.py": "493aeace43b91c755c2c038db0ab71fd61f4acbcf62d7a717b07894fb7f0f41e",
 "acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md": "e2dcded34b2deb6f5eb0c326353487bb741e5b22eae9447d5216902982bc0164",
}
CALLER_SOFTWARE = {
 "acceleration/project_20261003_root_focused_chain_graph_v2.py": "5c22e4fec65ef3d95ae3f6e09023b3067b674d1a631c228e09b2282daa5d2aab",
 "acceleration/project_20261003_root_focused_chain_graph_v2_spec.md": "80d5e9148bd8bf387448483e3dd470c3418dea1d7ecaeb392a9e4bf63a2ed2a3",
 "acceleration/census_20261003_root_focused_restricted_three_line_v3.py": SOFTWARE["acceleration/census_20261003_root_focused_restricted_three_line_v3.py"],
 "acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md": SOFTWARE["acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md"],
 "acceleration/project_20261003_root_focused_neighbor_graph_v1.py": "593b04087da6d54f9d25c159466100dc2b215615d088caf1af7b0eb33009353c",
 "acceleration/project_20261003_root_focused_neighbor_graph_v1_spec.md": "9842e294d920094140776246c6a36ed2b840f948cefac5607129be23bf0864ec",
 **{key: value for key, value in SOFTWARE.items() if "restricted_three_line_v3" not in key},
 "acceleration/census_20261003_root_focused_restricted_three_line_caller_v1.py": "863b5cce5643241989ae7a4855c1f96a8deaf1eb91240249dcae0b1b73b71c49",
 "acceleration/census_20261003_root_focused_restricted_three_line_caller_v1_spec.md": "9ca63e1b950b843f6ee839e1690f8af382f56a38111b1c6fd6ddd0c8766a2f51",
}
PINS = {**CALLER_SOFTWARE,
 RAW_CORE: "98efe2641fe2952857efaa62b7812b0abe7a0f87ce4550bf64544a4ba3ebaa95",
 SCALAR: "44cd8135f626420454d155bdd6cebcf2b1a0568e3faf06dfa1bad85f9fe746b2",
 CAL: "ba21cbd99ee8d14ba015c16eaf9cd81733ef90b51cffa5c8e6429420ec91f715",
 "acceleration/audit_20261003_restricted_three_line_records_v1.py": "52566cfa7031b4a28f4a1633f78bfe992549f74f442e58124a5ca34cde2a0a31",
 "acceleration/audit_20261003_restricted_three_line_records_v1_spec.md": "456fefc3b1a95d575c3a3dc848e128a20f1c7ad44b6a8f51aab3ca9c3967e9a6",
 "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
 "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
CONFIG = {
 "kernel": dict(root="acceleration/results/20261003_restricted_three_line_v3_controls01",
   summary_sha="2749d7292fcc7546be713e81e041041d78c57837f65d593bc784bf04e3ec8429",
   supervision="acceleration/results/20261003_restricted_three_line_v3_controls_supervision01",
   supervisor_manifest_sha="ef458aec44b5927fcb56c56cee82d0522512bb742cb78ff31e431372883a1b4b",
   supervisor_summary_sha="f56cd8d23754d1f4a9f488da2a179056baaa70e5bde267748d5b03470619ba08",
   admission="acceleration/results/20261003_restricted_three_line_v3_controls_admission01.json",
   admission_sha="071efaeec6cbd98a0413c95747f1639429daa6103fea7afdc860fc010647c330",
   plan="acceleration/plan_20261003_restricted_three_line_author_controls_v3.json",
   plan_sha="43280ad91c10a8a0cc6b3cb2c18079859acb70b0312750292dcc77c2f22dcd0c",
   source="acceleration/census_20261003_root_focused_restricted_three_line_v3.py",
   context="00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8"),
 "caller": dict(root="acceleration/results/20261003_restricted_three_line_caller_v1_controls01",
   summary_sha="ff43f7f78b4bfde56010d807df9442316e7fea640f1ec53d6e41110a47472bcc",
   supervision="acceleration/results/20261003_restricted_three_line_caller_v1_controls_supervision01",
   supervisor_manifest_sha="95aac1edd3217cb4da74292f05c6a54e285d88d28b41ffee5ffba3290036a464",
   supervisor_summary_sha="44cfc35ea112d574879e54fddb932ff5cb0740e3793282137bb41cd8945c0507",
   admission="acceleration/results/20261003_restricted_three_line_caller_v1_controls_admission01.json",
   admission_sha="fe6b3a9ec0035526d0731397bb512185b900aac5753a017474abe256fd898b2d",
   plan="acceleration/plan_20261003_restricted_three_line_caller_author_controls_v1.json",
   plan_sha="400d76513ad58d27b8f7f2dfdddf202cfac39709eb22854a940c63e108e72266",
   source="acceleration/census_20261003_root_focused_restricted_three_line_caller_v1.py",
   context="63437c9b9fc2dd58b3bdfb51fc347b880b397503"),
}
FROZEN = [[15,59,3,11],[18,78,11,62],[22,37,18,11],[57,11,77,15],
          [61,88,11,12],[82,11,23,96],[154,11,93,46]]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    with path.open("x", encoding="utf8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write("\n")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec); sys.modules[name] = result; spec.loader.exec_module(result)
    return result


def run_boundary(core, manifest, expected_start, expected_end):
    core.need(type(manifest) is dict and core.integer(manifest.get("starting_proposal_id"))
        and core.integer(manifest.get("completed_proposals")) and core.integer(manifest.get("proposals_evaluated_this_invocation"))
        and manifest["starting_proposal_id"] == expected_start and manifest["completed_proposals"] == expected_end
        and manifest["proposals_evaluated_this_invocation"] == expected_end - expected_start, "NAMED_RUN_BOUNDARY")


def profile(core, kind, manifest, terminal, plan, admission, author):
    conf = CONFIG[kind]
    command = plan.get("command")
    core.need(type(command) is list and command[:3] == ["/usr/bin/python3", "acceleration/run_compute_command.py", "--seconds"]
         and command.count("--") == 1 and manifest.get("command") == command[command.index("--") + 1:]
         and manifest.get("cwd") == "/mnt/c/Users/ikuto/projects/conway-99-graph"
         and manifest.get("source_sha256") == SOFTWARE["acceleration/run_compute_command.py"]
         and manifest.get("seconds") == 120.0 and manifest.get("shutdown_reserve_seconds") == 20.0,
         "LINUX_COMMAND_PROFILE")
    expected_worker = ["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",
                       conf["source"], "controls", "--seconds", "100", "--out", conf["root"], "--source-commit", conf["context"]]
    expected_child = ["/usr/bin/env", "UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv", "/root/.local/bin/uv",
                      "run", "--locked", "--offline", "--project", "acceleration/native_budget_env_v1", "--cache-dir",
                      "build/native-budget-linux-cache", "--python", "/usr/bin/python3", "python", *expected_worker[1:]]
    core.need(core.same(manifest["command"], expected_child) and core.same(author.get("command"), expected_worker)
         and author.get("cwd") == manifest["cwd"] and author.get("python") == "3.12.3" and author.get("tqdm") == "4.67.1",
         "LINUX_CHILD_BINDING")
    cleanup = terminal.get("cleanup")
    core.need(type(cleanup) is dict and cleanup.get("reaped") is True and cleanup.get("actual_exit_code") == 0
         and type(cleanup.get("actual_exit_code")) is int and cleanup.get("cleanup_errors") == []
         and cleanup.get("process_group_live_pids") == [] and cleanup.get("job_active_zero_observed") is True
         and terminal.get("command_exit_code") == 0 and type(terminal.get("command_exit_code")) is int
         and terminal.get("invocation_id") == manifest.get("invocation_id"), "LINUX_TERMINAL")
    probe = admission.get("default_uid_probe")
    core.need(type(probe) is dict and probe.get("command") == ["wsl.exe", "-d", "Ubuntu-24.04", "--", "/usr/bin/id", "-u"]
         and core.integer(probe.get("stdout_uid")) and probe["stdout_uid"] == 1000
         and core.integer(probe.get("exit_code")) and probe["exit_code"] == 0
         and admission.get("admitted") is True and admission.get("scientific_launched") is False
         and admission.get("independent_approval") is False and admission.get("plan", {}).get("sha256") == conf["plan_sha"], "UID_ADMISSION")


def synthetic_profile(kind):
    """Hand-built profile control only; no execution/UID observation is invented."""
    conf = CONFIG[kind]
    child = ["/usr/bin/env", "UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv", "/root/.local/bin/uv",
             "run", "--locked", "--offline", "--project", "acceleration/native_budget_env_v1", "--cache-dir",
             "build/native-budget-linux-cache", "--python", "/usr/bin/python3", "python", conf["source"],
             "controls", "--seconds", "100", "--out", conf["root"], "--source-commit", conf["context"]]
    command = ["/usr/bin/python3", "acceleration/run_compute_command.py", "--seconds", "120", "--", *child]
    runtime = dict(command=child, cwd="/mnt/c/Users/ikuto/projects/conway-99-graph",
                   source_sha256=SOFTWARE["acceleration/run_compute_command.py"], seconds=120.0,
                   shutdown_reserve_seconds=20.0, invocation_id="SYNTHETIC_PROFILE_NOT_EXECUTED")
    terminal = dict(command_exit_code=0, invocation_id=runtime["invocation_id"], cleanup=dict(reaped=True,
        actual_exit_code=0, cleanup_errors=[], process_group_live_pids=[], job_active_zero_observed=True))
    admission = dict(default_uid_probe=dict(command=["wsl.exe", "-d", "Ubuntu-24.04", "--", "/usr/bin/id", "-u"],
        stdout_uid=1000, exit_code=0), admitted=True, scientific_launched=False, independent_approval=False,
        plan=dict(sha256=conf["plan_sha"]))
    author = dict(command=["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",
        *child[13:]], cwd=runtime["cwd"], python="3.12.3", tqdm="4.67.1")
    return [runtime, terminal, dict(command=command), admission, author]


def gate_positive(kind):
    basic = dict(producer="/root/native_driver", verifier="/root/structural", method="independent_artifact_check", target_resolution="NONE")
    if kind == "KERNEL_GATE":
        return dict(**basic, status="INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_V3_CONTROLS_PASS", inputs_sha256=SOFTWARE,
                    unique_fixture_role_records=4032, strict_author_negative_cases=95, whole_prefix_resume_equalities=3,
                    actual_target_input_read=False)
    if kind == "CALLER_GATE":
        return dict(**basic, status="INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_CALLER_V1_CONTROLS_PASS", inputs_sha256=CALLER_SOFTWARE)
    refs = {key: dict(path="synthetic/" + key + ".json", sha256="0" * 64) for key in
            ("source_manifest", "source_matrix", "source_triples", "source_complete_audit")}
    return dict(**basic, status="INDEPENDENT_FROZEN_ROOT_STRICT_LEX_GRAPH_PROJECTION_V1_COMPLETE_PASS",
       graph_only_input=True, historical_native_state_written=False, n=99, point_degree=7, root=11,
       ordered_triples=231, mutable_lines=224, frozen_lines=7, selected_proposal_id=145287,
       graph_input_path="acceleration/results/20261003_root_focused_selected145287_projection01/graph_input.json",
       graph_input_sha256="203204c24e3a2f4901cabd85f9c3f740db5b053831393db65c201a3773ff1748",
       frozen_original_literal_rows=FROZEN, metrics=dict(E_lambda=0, E_mu=5292, R_root=10),
       source_baseline_metrics=dict(E_lambda=0, E_mu=5344, R_root=10),
       **{key + "_sha256": value["sha256"] for key, value in refs.items()},
       inputs_sha256={"acceleration/results/20261003_root_focused_selected145287_projection01/graph_input.json":
                     "203204c24e3a2f4901cabd85f9c3f740db5b053831393db65c201a3773ff1748",
                     "acceleration/project_20261003_root_focused_chain_graph_v2.py": CALLER_SOFTWARE["acceleration/project_20261003_root_focused_chain_graph_v2.py"],
                     "acceleration/project_20261003_root_focused_chain_graph_v2_spec.md": CALLER_SOFTWARE["acceleration/project_20261003_root_focused_chain_graph_v2_spec.md"],
                     **{value["path"]: value["sha256"] for value in refs.values()}})


def check_fixed_synthetic_gate(core, kind, value):
    # This is deliberately a finite fixture validator, not a reviewer of a
    # future real scientific gate with nonzero source artifacts.
    core.need(core.same(value, gate_positive(kind)), kind, "every literal field/type of this declared synthetic metadata fixture")


def interface_calibration(core, out, reserve):
    controls = []
    def reject(label, stage, call):
        reserve()
        try:
            call()
        except core.AuditError as error:
            core.need(error.stage == stage, "CONTROL_STAGE", label)
            controls.append(dict(case=label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error)))
            return
        raise core.AuditError("CONTROL_ACCEPTED", label)
    for kind in ("INPUT_GATE", "KERNEL_GATE", "CALLER_GATE"):
        positive = gate_positive(kind); check_fixed_synthetic_gate(core, kind, positive)
        save(out / (kind + "_SYNTHETIC_POSITIVE.json"), dict(synthetic_metadata_only=True, gate=positive))
        for field, value in (("method", "producer_execution"), ("verifier", "/root/native_driver"), ("target_resolution", "SOLVED")):
            bad = copy.deepcopy(positive); bad[field] = value
            reject(kind + "_" + field, kind, lambda v=bad, k=kind: check_fixed_synthetic_gate(core, k, v))
    for name, value in (("inside_old_prefix", 5), ("boolean_start", False), ("float_start", 17.0)):
        bad = dict(starting_proposal_id=value, completed_proposals=4032, proposals_evaluated_this_invocation=4032 - int(value))
        reject(name, "NAMED_RUN_BOUNDARY", lambda v=bad: run_boundary(core, v, 17, 4032))
    run_boundary(core, dict(starting_proposal_id=17, completed_proposals=4032, proposals_evaluated_this_invocation=4015), 17, 4032)
    for kind in ("kernel", "caller"):
        positive = synthetic_profile(kind)
        profile(core, kind, *positive)
        save(out / (kind + "_synthetic_linux_profile.json"), dict(synthetic_not_executed=True, objects=positive))
        cases = [("child_source", "LINUX_COMMAND_PROFILE", 0, "command", ["wrong"]),
                 ("cwd", "LINUX_COMMAND_PROFILE", 0, "cwd", "wrong"),
                 ("worker_argv", "LINUX_CHILD_BINDING", 4, "command", ["wrong"]),
                 ("python_version", "LINUX_CHILD_BINDING", 4, "python", "wrong"),
                 ("exit_boolean", "LINUX_TERMINAL", 1, "command_exit_code", False),
                 ("invocation", "LINUX_TERMINAL", 1, "invocation_id", "wrong")]
        for label, stage, at, field, replacement in cases:
            value = copy.deepcopy(positive); value[at][field] = replacement
            reject(kind + "_" + label, stage, lambda v=value, k=kind: profile(core, k, *v))
        for label, stage, at, owner, field, replacement in [
            ("live_group", "LINUX_TERMINAL", 1, "cleanup", "process_group_live_pids", [1]),
            ("cleanup_error", "LINUX_TERMINAL", 1, "cleanup", "cleanup_errors", ["wrong"]),
            ("UID_boolean", "UID_ADMISSION", 3, "default_uid_probe", "stdout_uid", True),
            ("UID_root", "UID_ADMISSION", 3, "default_uid_probe", "stdout_uid", 0),
            ("UID_float", "UID_ADMISSION", 3, "default_uid_probe", "stdout_uid", 1000.0),
            ("plan_hash", "UID_ADMISSION", 3, "plan", "sha256", "wrong")]:
            value = copy.deepcopy(positive); value[at][owner][field] = replacement
            reject(kind + "_" + label, stage, lambda v=value, k=kind: profile(core, k, *v))
    for stage in ("INPUT_GATE", "KERNEL_GATE", "CALLER_GATE"):
        for label, value in caller_mutations(stage):
            reject("own_" + label, stage, lambda v=value, k=stage: check_fixed_synthetic_gate(core, k, v))
    identity = dict(root=0, software=SOFTWARE, synthetic_control_only=True)
    checkpoint = dict(schema="FROZEN_ROOT_RESTRICTED_THREE_LINE_CHECKPOINT_V1", identity=identity,
                      next_proposal_id=0, parts=[], aggregate={})
    core.checkpoint(checkpoint, identity, [], 0, {})
    for label, field, value in (("prefix_identity_boolean_root", "root", False),
                                ("prefix_identity_float_root", "root", 0.0),
                                ("prefix_identity_other_source", "software", {})):
        bad = copy.deepcopy(checkpoint); bad["identity"][field] = value
        reject(label, "CHECKPOINT_IDENTITY", lambda v=bad: core.checkpoint(v, identity, [], 0, {}))
    core.need(len(controls) == 136, "CONTROL_POPULATION")
    save(out / "strict_negative_controls.json", controls)
    return dict(positives=7, strict_negative_controls=controls, strict_negative_count=136,
                actual_producer_outputs_read=False, actual_target_input_read=False,
                exact_run_boundary_guard_checked=True, scope="Changed finite gate/attempt-count and source-bound Linux/UID receipt interface only; no new mathematical gate")


def author_artifacts(core, kind, pin):
    conf = CONFIG[kind]
    directory = ROOT / conf["root"]
    def read(name, expected=None):
        path = pin(name, expected)
        return core.strict_json(path.read_bytes())
    summary = read(conf["root"] + "/summary.json", conf["summary_sha"])
    plan = read(conf["plan"], conf["plan_sha"])
    runtime = read(conf["supervision"] + "/manifest.json", conf["supervisor_manifest_sha"])
    terminal = read(conf["supervision"] + "/summary.json", conf["supervisor_summary_sha"])
    admission = read(conf["admission"], conf["admission_sha"])
    profile(core, kind, runtime, terminal, plan, admission, summary)
    expected = SOFTWARE if kind == "kernel" else CALLER_SOFTWARE
    core.need(core.same(summary.get("software"), expected), "AUTHOR_SOFTWARE")
    core.need(summary.get("producer") == "/root/native_driver" and summary.get("independent_approval") is False
              and summary.get("target_resolution") == "NONE" and summary.get("scientific_census_launched") is False
              and summary.get("source_commit" if kind == "kernel" else "source_reference_commit") == conf["context"]
              and summary.get("actual_target_input_read" if kind == "kernel" else "actual99graph_read") is False
              and summary.get("status") == ("AUTHOR_RESTRICTED_THREE_LINE_V3_CONTROLS_PENDING_INDEPENDENT_GATE"
                 if kind == "kernel" else "AUTHOR_RESTRICTED_THREE_LINE_CALLER_V1_CONTROLS_PENDING_INDEPENDENT_GATE"),
              "AUTHOR_SCOPE")
    for group in ("windows", "linux"):
        ref = admission[group]; pin(ref["path"], ref["sha256"])
    for name in ("stdout.log", "stderr.log"):
        if (ROOT / conf["supervision"] / name).is_file():
            pin(conf["supervision"] + "/" + name)
    return directory, summary


def fixture_replay(core, scalar, kind, directory, summary, reserve, out):
    models, coverage, counts, attempted = {}, [], {}, 0
    for name, fixture in scalar.fixtures().items():
        reserve(); b = core.fixed_input(**fixture); d = core.domain(b)
        if kind == "kernel":
            raw_fixture = core.strict_json((directory / (name + ".json")).read_bytes())
            core.need(core.same(raw_fixture, dict(n=b.n, degree=b.degree, root=b.root, triples=[list(row) for row in b.rows])), "FIXTURE_LITERAL")
            identity = dict(fixture_path=(directory / (name + ".json")).relative_to(ROOT).as_posix(),
                fixture_sha256=sha(directory / (name + ".json")), software=SOFTWARE, universe=d["universe"], n=b.n, degree=b.degree, root=b.root)
            shapes = [("whole", 0, len(d["roles"])), ("prefix17", 0, min(17, len(d["roles"]))),
                      ("resumed", min(17, len(d["roles"])), len(d["roles"]))]
        else:
            graph = core.strict_json((directory / (name + ".graph.json")).read_bytes())
            expected_graph = dict(schema="FROZEN_ROOT_STRICT_LEX_GRAPH_INPUT_V1", n=b.n, degree=b.degree,
                root=b.root, ordered_triples=[list(row) for row in b.rows], frozen_rows=[list(row) for row in b.frozen],
                mutable_labels=list(b.mutable), metrics=dict(E_lambda=b.E_lambda, E_mu=b.E_mu, R_root=b.R_root),
                provenance=dict(mode="synthetic_engineering_fixture", historical_native_state_written=False,
                    selected_proposal_id=None, source_baseline_metrics=None, source_complete_audit=None,
                    source_manifest=None, source_matrix=None, source_triples=None,
                    null_reason="Known generic engineering graph; no selected99 input or historical computation."))
            core.need(core.same(graph, expected_graph), "GRAPH_ROUNDTRIP_LITERAL")
            identity = dict(synthetic_fixture=name, software=CALLER_SOFTWARE, universe=d["universe"])
            stop = min(17, len(d["roles"])); shapes = [("prefix_whole", 0, stop), ("prefix7", 0, min(7, stop)), ("prefix_resumed", min(7, stop), stop)]
        visits, results = 0, {}
        for suffix, start, stop in shapes:
            run_dir = directory / (name + "_" + suffix)
            manifest = core.strict_json((run_dir / "manifest.json").read_bytes())
            run_boundary(core, manifest, start, stop)
            result = core.audit_run(ROOT, directory, d, manifest, identity, reserve)
            core.audit_ties(run_dir, d, result)
            visits += stop; attempted += stop - start
            results[suffix] = (manifest, result)
            save(out / (name + "_" + suffix + "_replayed.json"), dict(complete_record_visits=stop,
                 attempted_producer_evaluations=stop - start, checkpoints=result["checkpoints"], independently_recomputed_aggregate=result["aggregate"].snapshot()))
        first, last = results[shapes[0][0]][1], results[shapes[-1][0]][1]
        core.need(core.same(first["aggregate"].snapshot(), last["aggregate"].snapshot()), "WHOLE_PREFIX_RESUME_EQUALITY")
        counts[name] = dict(role_universe=len(d["roles"]), distinct_checked_records=shapes[0][2], complete_raw_record_visits=visits,
                           whole_prefix_resume_equal=True, classifications=first["aggregate"].snapshot()["counts"])
        models[name] = (d, identity, results)
        for pid in range(shapes[0][2]):
            expected, _, _ = core.expected_record(d, pid)
            coverage.append(dict(fixture=name, proposal_id=pid, classification=expected["classification"]))
    if kind == "kernel":
        core.need(core.same(core.strict_json((directory / "coverage.json").read_bytes()), coverage), "AUTHOR_COVERAGE_RECORDS")
        for filename, role in (("known_rook_overlap_cycle.json", (1, 2, 4, 0, 0, 0)),
                               ("known_selected_repeat.json", (1, 4, 2, 1, 1, 0)),
                               ("known_receiver_collision.json", (1, 2, 4, 0, 2, 1))):
            actual = core.strict_json((directory / filename).read_bytes())
            expected, _, _ = core.literal_cycle(models["rook9"][0]["base"], role)
            core.need(core.same(actual, expected), "EXTRA_GENERIC_CYCLE", filename)
        core.need(attempted == 8064 and summary.get("recorded_role_evaluation_calls") == 8064
                  and summary.get("unique_role_records") == 4032 and type(summary["unique_role_records"]) is int
                  and summary.get("split_equalities") == 3 and summary.get("whole_split_equal") is True, "AUTHOR_STAGE_COUNTS")
    else:
        core.need(attempted == 34 and summary.get("finite_prefix_resume_equalities") == 3
                  and summary.get("generic_fixture_positives") == list(scalar.fixtures())
                  and core.same(summary.get("finite_prefix_counts"), {name: dict(role_universe=value["role_universe"],
                     distinct_prefix_records=value["distinct_checked_records"], evaluation_calls=2 * value["distinct_checked_records"],
                     prefix_resume_equal=True) for name, value in counts.items()}), "AUTHOR_STAGE_COUNTS")
    return models, counts, attempted


def kernel_negatives(core, directory, summary, models, reserve):
    results, declared = [], {}
    def reject(label, producer_stage, own_stage, call, provenance):
        reserve(); declared[label] = producer_stage
        try:
            call()
        except core.AuditError as error:
            core.need(error.stage == own_stage, "CONTROL_STAGE", label + " expected " + own_stage + " got " + error.stage)
            results.append(dict(case=label, producer_stage=producer_stage, independent_expected_stage=own_stage,
                                independent_actual_stage=error.stage, artifact_method=provenance, outcome="REJECTED"))
            return
        raise core.AuditError("CONTROL_ACCEPTED", label)
    for name, (d, identity, runs) in models.items():
        for key, stage in (("masks", "ADJ_CACHE"), ("cn", "CN_CACHE"), ("lambda_energy", "ENERGY_CACHE"),
                           ("mu_energy", "ENERGY_CACHE"), ("root_residual", "ENERGY_CACHE")):
            value = copy.deepcopy(core.native_cache(d))
            if key == "masks": value["base"][key][0] ^= 1
            elif key == "cn": value["base"][key][0][1] += 1
            else: value["base"][key] += 1
            reject(name + "_bad_" + key, stage, stage, lambda v=value: core.check_native_cache(d, v), "independently reconstructed unsaved cache corruption")
        value = copy.deepcopy(core.native_cache(d)); value["universe"]["proposal_count"] += 1
        reject(name + "_bad_role_count", "ROLE_CACHE", "ROLE_CACHE", lambda v=value: core.check_native_cache(d, v), "independently reconstructed unsaved cache corruption")
        neighbor = d["universe"]["root_neighbors"][0]
        for suffix, at, replacement in (("boolean_zero", (0, 0), False), ("float_zero", (0, 0), 0.0),
                                        ("boolean_one", (d["base"].root, neighbor), True), ("float_one", (d["base"].root, neighbor), 1.0)):
            value = copy.deepcopy(core.native_cache(d)); value["base"]["cn"][at[0]][at[1]] = replacement
            reject(name + "_CN_" + suffix, "CN_CACHE", "CN_CACHE", lambda v=value: core.check_native_cache(d, v), "independently reconstructed unsaved cache corruption")
        for suffix, replacement in (("boolean", False), ("float_equal", float(core.native_cache(d)["base"]["masks"][0]))):
            value = copy.deepcopy(core.native_cache(d)); value["base"]["masks"][0] = replacement
            reject(name + "_mask_" + suffix, "ADJ_CACHE", "ADJ_CACHE", lambda v=value: core.check_native_cache(d, v), "independently reconstructed unsaved cache corruption")
        prefix, result = runs["prefix17"]
        end, parts, aggregate = prefix["completed_proposals"], prefix["parts"], result["aggregate"].snapshot()
        cp_cases = [("checkpoint_aggregate", "CHECKPOINT_AGGREGATE", "CHECKPOINT_AGGREGATE"),
                    ("checkpoint_ID_boolean", "CHECKPOINT_TYPES", "CHECKPOINT_TYPES"),
                    ("checkpoint_ID_float_equal", "CHECKPOINT_TYPES", "CHECKPOINT_TYPES"),
                    ("checkpoint_count_boolean", "CHECKPOINT_AGGREGATE", "CHECKPOINT_AGGREGATE"),
                    ("checkpoint_count_float_equal", "CHECKPOINT_AGGREGATE", "CHECKPOINT_AGGREGATE"),
                    ("checkpoint_identity_boolean_zero", "CHECKPOINT_IDENTITY", "CHECKPOINT_IDENTITY"),
                    ("checkpoint_identity_float_zero", "CHECKPOINT_IDENTITY", "CHECKPOINT_IDENTITY")]
        for suffix, pstage, stage in cp_cases:
            label = name + "_" + suffix; value = core.strict_json((directory / (label + "_input.json")).read_bytes())
            reject(label, pstage, stage, lambda v=value: core.checkpoint(v, identity, parts, end, aggregate), "saved raw checkpoint corruption")
        reject(name + "_pid_boolean", "PROPOSAL_DOMAIN", "PROPOSAL_ID", lambda: core.expected_record(d, True), "independently reconstructed typed ID")
        reject(name + "_pid_oob", "PROPOSAL_DOMAIN", "PROPOSAL_ID", lambda: core.expected_record(d, len(d["roles"])), "independently reconstructed bounded ID")
    rook = models["rook9"][0]["base"]
    for label, role, pstage, stage in [("frozen_line", (0, 1, 2, 0, 0, 0), "FROZEN_UNIVERSE", "ROLE_MUTABLE_LINES"),
                                     ("same_line", (1, 1, 2, 0, 0, 0), "FROZEN_UNIVERSE", "ROLE_MUTABLE_LINES"),
                                     ("selected_coord_boolean", (1, 2, 4, True, 0, 0), "PROPOSAL_DOMAIN", "ROLE_TYPES"),
                                     ("selected_coord_oob", (1, 2, 4, 3, 0, 0), "PROPOSAL_DOMAIN", "ROLE_RANGE")]:
        reject(label, pstage, stage, lambda r=role: core.literal_cycle(rook, r), "independently reconstructed source selection")
    for label, raw in (("duplicate_json_key", b'{"a":1,"a":2}'), ("nonfinite_json", b'{"a":NaN}'), ("bad_json", b'{')):
        reject(label, "JSON", "JSON", lambda v=raw: core.strict_json(v), "exact written raw lexical fixture")
    d = models["doily_two_lift30"][0]
    valid_pid = next(pid for pid in range(len(d["roles"])) if core.expected_record(d, pid)[0]["valid"])
    records = [("record_role_u", "RECORD_ROLE", "RECORD_ROLE"), ("record_boolean_pid", "RECORD_ROLE", "RECORD_ID"),
               ("record_extra_field", "RECORD_ROLE", "RECORD_SCHEMA"), ("record_valid_flag", "RECORD_STATUS", "RECORD_STATUS"),
               ("record_classification", "RECORD_STATUS", "RECORD_STATUS"), ("record_old_triples", "RECORD_TOPOLOGY", "RECORD_TOPOLOGY"),
               ("record_toggle_omission", "RECORD_TOPOLOGY", "RECORD_TOPOLOGY"), ("record_wrong_lambda", "RECORD_SCORE", "RECORD_SCORE"),
               ("record_boolean_score", "RECORD_SCORE", "RECORD_SCORE"), ("record_wrong_delta_mu", "RECORD_SCORE", "RECORD_SCORE"),
               ("record_false_minus4", "RECORD_ROOT_CUT", "RECORD_ROOT_CUT"), ("record_root_count_omission", "RECORD_ROOT_CUT", "RECORD_ROOT_CUT"),
               ("record_wrong_root_residual", "RECORD_ROOT_CUT", "RECORD_ROOT_CUT"), ("record_root_frozen_flag", "RECORD_ROOT_CUT", "RECORD_ROOT_CUT")]
    for label, pstage, stage in records:
        value = core.strict_json((directory / (label + "_input.json")).read_bytes())
        reject(label, pstage, stage, lambda v=value: core.check_record(d, valid_pid, v), "saved raw nineteen-field corruption")
    part_cases = [("part_gzip_hash", "PART_HASH", "PART_COMPRESSED_HASH"), ("part_raw_hash", "PART_HASH", "PART_RAW_HASH"),
                  ("part_record_count", "PART_TYPES", "PART_TYPES"), ("part_id_shift", "PART_SEQUENCE", "PART_SEQUENCE"),
                  ("part_boolean_start", "PART_TYPES", "PART_TYPES"), ("part_float_zero_start", "PART_TYPES", "PART_TYPES"),
                  ("part_boolean_count", "PART_TYPES", "PART_TYPES"), ("part_float_equal_count", "PART_TYPES", "PART_TYPES"),
                  ("part_float_equal_rawbytes", "PART_TYPES", "PART_TYPES"), ("part_boolean_ID_zero", "PART_SEQUENCE", "PART_SEQUENCE"),
                  ("part_float_ID_zero", "PART_SEQUENCE", "PART_SEQUENCE")]
    for label, pstage, stage in part_cases:
        value = core.strict_json((directory / (label + "_input.json")).read_bytes())
        reject(label, pstage, stage, lambda v=value: core.part_records(ROOT, directory, v), "saved raw part/JSONL corruption")
    stated = summary.get("strict_negatives")
    core.need(type(stated) is list and len(stated) == 95 and len(declared) == 95 and summary.get("strict_negative_count") == 95,
              "AUTHOR_NEGATIVE_POPULATION")
    core.need([row.get("case") for row in stated] == list(declared), "AUTHOR_NEGATIVE_ORDER")
    for row in stated:
        core.need(type(row) is dict and set(row) == {"case", "expected_stage", "actual_stage", "diagnostic"}
                  and row["expected_stage"] == declared[row["case"]] == row["actual_stage"]
                  and type(row["diagnostic"]) is str and row["diagnostic"].startswith(row["actual_stage"] + ":"), "AUTHOR_NEGATIVE_STAGE")
    return results


def caller_mutations(stage):
    """Exact declared finite corruption universe, derived without producer code."""
    gate = gate_positive(stage); cases = []
    def changed(label, path, value):
        bad = copy.deepcopy(gate); owner = bad
        for key in path[:-1]: owner = owner[key]
        owner[path[-1]] = value
        cases.append((stage + "_" + label, bad))
    for key in ("status", "producer", "verifier", "method", "target_resolution"):
        changed("wrong_" + key, [key], "wrong")
    for at, key in enumerate(gate["inputs_sha256"]):
        bad = copy.deepcopy(gate); del bad["inputs_sha256"][key]
        cases.append((stage + "_missing_pin_" + str(at), bad))
    if stage == "INPUT_GATE":
        for key in ("graph_only_input", "historical_native_state_written"):
            changed("wrong_" + key, [key], not gate[key])
        for key in ("n", "point_degree", "root", "ordered_triples", "mutable_lines", "frozen_lines", "selected_proposal_id"):
            for suffix, value in (("wrong", gate[key] + 1), ("bool", True), ("float", float(gate[key]))):
                changed(key + "_" + suffix, [key], value)
        for key in ("graph_input_path", "graph_input_sha256", "source_manifest_sha256", "source_matrix_sha256",
                    "source_triples_sha256", "source_complete_audit_sha256"):
            changed("wrong_" + key, [key], "wrong")
        for owner in ("metrics", "source_baseline_metrics"):
            for key in ("E_lambda", "E_mu", "R_root"):
                changed("wrong_" + owner + "_" + key, [owner, key], gate[owner][key] + 1)
            changed("bool_" + owner, [owner, "R_root"], False)
            changed("float_" + owner, [owner, "R_root"], float(gate[owner]["R_root"]))
        bad = copy.deepcopy(gate); bad["frozen_original_literal_rows"][0].reverse()
        cases.append((stage + "_frozen_row_reordered", bad))
        changed("source_matrix_pin_corrupt", ["inputs_sha256", "synthetic/source_matrix.json"], "1" * 64)
    elif stage == "KERNEL_GATE":
        changed("actual_target_read", ["actual_target_input_read"], True)
        for key in ("unique_fixture_role_records", "strict_author_negative_cases", "whole_prefix_resume_equalities"):
            for suffix, value in (("wrong", gate[key] + 1), ("bool", True), ("float", float(gate[key]))):
                changed(key + "_" + suffix, [key], value)
        changed("kernel_source_pin_corrupt", ["inputs_sha256", CONFIG["kernel"]["source"]], "1" * 64)
    else:
        changed("caller_source_pin_corrupt", ["inputs_sha256", CONFIG["caller"]["source"]], "1" * 64)
    return cases


def caller_negatives(core, directory, summary, reserve):
    rows = summary.get("strict_negatives")
    core.need(type(rows) is list and len(rows) == 97 and summary.get("strict_negative_count") == 97, "CALLER_NEGATIVE_POPULATION")
    declared = [(stage, label, value) for stage in ("INPUT_GATE", "KERNEL_GATE", "CALLER_GATE")
                for label, value in caller_mutations(stage)]
    core.need(len(declared) == 97 and [row.get("case") for row in rows] == [label for _, label, _ in declared], "CALLER_NEGATIVE_ORDER")
    actual, group_counts, labels = [], {}, set()
    for row, (stage, label, expected_bad) in zip(rows, declared):
        reserve()
        core.need(type(row) is dict and set(row) == {"case", "expected_stage", "actual_stage", "diagnostic"}
                  and type(row["case"]) is str and row["case"] not in labels and row["actual_stage"] == row["expected_stage"]
                  and row["actual_stage"] in ("INPUT_GATE", "KERNEL_GATE", "CALLER_GATE")
                  and row["diagnostic"].startswith(row["actual_stage"] + ":"), "CALLER_NEGATIVE_STAGE")
        core.need(row["actual_stage"] == stage, "CALLER_NEGATIVE_STAGE")
        labels.add(row["case"])
        value = core.strict_json((directory / (row["case"] + ".json")).read_bytes())
        core.need(core.same(value, dict(synthetic_metadata_only=True, gate=expected_bad)),
                  "CALLER_CORRUPTION_ARTIFACT")
        try:
            check_fixed_synthetic_gate(core, stage, value["gate"])
        except core.AuditError as error:
            core.need(error.stage == stage, "CONTROL_STAGE")
            actual.append(dict(case=row["case"], actual_stage=error.stage, outcome="REJECTED", method="complete raw literal synthetic metadata comparison"))
        else:
            raise core.AuditError("CONTROL_ACCEPTED", row["case"])
        group_counts[stage] = group_counts.get(stage, 0) + 1
    core.need(group_counts == {"INPUT_GATE": 53, "KERNEL_GATE": 24, "CALLER_GATE": 20}, "CALLER_NEGATIVE_POPULATION")
    for stage in group_counts:
        positive = core.strict_json((directory / (stage + "_synthetic_positive.json")).read_bytes())
        metadata = dict(metrics=dict(E_lambda=0, E_mu=5292, R_root=10), provenance=dict(selected_proposal_id=145287,
            **{key: dict(path="synthetic/" + key + ".json", sha256="0" * 64)
               for key in ("source_manifest", "source_matrix", "source_triples", "source_complete_audit")},
            source_baseline_metrics=dict(E_lambda=0, E_mu=5344, R_root=10))) if stage == "INPUT_GATE" else None
        core.need(core.same(positive, dict(synthetic_metadata_only=True, actual99graph_read=False,
                    gate=gate_positive(stage), object_metadata=metadata)), "CALLER_POSITIVE_SCOPE")
        check_fixed_synthetic_gate(core, stage, positive["gate"])
    return actual


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["calibration", "controls"])
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--self-sha256", required=True); ap.add_argument("--spec-sha256", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--interface-calibration", type=Path); ap.add_argument("--interface-calibration-sha256")
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Narrow different-author finite kernel95/caller97 artifact replay or changed typed interface calibration; no producer imports/actual99/census")
    out = args.out.resolve()
    if not out.is_relative_to(ROOT) or out.exists(): raise ValueError("OUTPUT_PATH: fresh contained output")
    out.mkdir(parents=True); pins = dict(PINS); pins.update({SELF: args.self_sha256, SPEC: args.spec_sha256})
    def reserve():
        if deadline.status()["remaining_seconds"] <= 20 or deadline.status()["stop_required"]:
            raise ValueError("DEADLINE: not completed within allocated budget")
    def pin(relative, expected=None):
        reserve(); path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or relative in ("CLAIMS.yaml", ".git/index"):
            raise ValueError("INPUT_PATH: immutable public workspace artifact only")
        identity = sha(path)
        if expected is not None and identity != expected: raise ValueError("INPUT_HASH: " + str(relative))
        name = path.relative_to(ROOT).as_posix()
        if name in pins and pins[name] != identity: raise ValueError("INPUT_MUTATION: " + name)
        pins[name] = identity; return path
    try:
        for path, identity in list(pins.items()): pin(path, identity)
        core = module(RAW_CORE, "independent_restricted_raw_core_v1")
        scalar = module(SCALAR, "independent_restricted_scalar_v2")
        if args.mode == "calibration":
            result = interface_calibration(core, out, reserve)
            status = "INDEPENDENT_RESTRICTED_THREE_LINE_FINITE_INTERFACE_V1_CALIBRATION_PASS"
        else:
            core.need(args.interface_calibration is not None and args.interface_calibration_sha256 is not None, "CALIBRATION_REQUIRED")
            calibration = core.strict_json(pin(args.interface_calibration, args.interface_calibration_sha256).read_bytes())
            core.need(calibration.get("status") == "INDEPENDENT_RESTRICTED_THREE_LINE_FINITE_INTERFACE_V1_CALIBRATION_PASS"
                  and calibration.get("verifier") == "/root/structural"
                  and calibration.get("producer") == "/root/structural"
                  and calibration.get("method") == "finite_checker_calibration"
                  and calibration.get("actual_target_input_read") is False
                  and calibration.get("inputs_sha256", {}).get(SELF) == args.self_sha256
                  and calibration["inputs_sha256"].get(SPEC) == args.spec_sha256
                  and calibration["inputs_sha256"].get(RAW_CORE) == PINS[RAW_CORE], "CALIBRATION_REQUIRED")
            result = {}
            for kind in ("kernel", "caller"):
                part_out = out / kind; part_out.mkdir()
                directory, summary = author_artifacts(core, kind, pin)
                models, populations, attempted = fixture_replay(core, scalar, kind, directory, summary, reserve, part_out)
                negatives = kernel_negatives(core, directory, summary, models, reserve) if kind == "kernel" else caller_negatives(core, directory, summary, reserve)
                save(part_out / "independently_rejected_author_controls.json", negatives)
                for path in directory.rglob("*"):
                    if path.is_file(): pin(path.relative_to(ROOT).as_posix())
                result[kind] = dict(populations=populations, producer_evaluation_calls=attempted,
                    complete_raw_record_visits=sum(v["complete_raw_record_visits"] for v in populations.values()),
                    exact_record_fields=19, independent_corruptions=len(negatives), whole_prefix_resume_equalities=3,
                    actual_target_input_read=False, new_exclusions=0, scientific_census_launched=False,
                    author_negative_reconstruction_disclosure="Saved raw objects checked where present; unsaved cache/role/lexical counterparts independently reconstructed. Producer exceptions are source-bound author receipts, not rerun or formalproof.")
            status = "INDEPENDENT_RESTRICTED_THREE_LINE_COMBINED_FINITE_CONTROLS_V1_PASS"
        outputs = {path.relative_to(ROOT).as_posix(): sha(path) for path in out.rglob("*") if path.is_file()}
        record = dict(status=status, producer="/root/native_driver" if args.mode != "calibration" else "/root/structural",
            verifier="/root/structural", method="independent_artifact_check" if args.mode != "calibration" else "finite_checker_calibration",
            timestamp=datetime.now(timezone.utc).isoformat(), source_commit=args.source_commit,
            source_reference_scope="Published repository context only. This new uncommitted checker and every unchanged component are identified by the exact working-source hashes; no Git availability is inferred.",
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins,
            outputs_sha256=outputs, result=result, deadline=deadline.status(), target_resolution="NONE",
            actual_target_input_read=False, new_exclusions=0, external_review=False,
            shared_components=["Byte-preserved independently authored rawcore98efe/owncalba21, scalarcore44cd fixture definitions, lockedNumPy2.5.3/Python/JSON/gzip/hash/deadline.",
                               "No Native producer import or incremental scorer; copied raw schema and shared mathematical fixture choices explicitly disclosed."],
            limitations=["Finite generic controls only; no actual99 input read, target graph/exclusion, move-space connectivity or performance guarantee.",
                         "Linux receipt means observed empty contained process group, not a WindowsJob/global-worker assertion.",
                         "Historical producer source/index/ledger observations preserved; current publication baseline is independent admission context."])
        if args.mode == "controls":
            for kind, gate_status in (("kernel", "INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_V3_CONTROLS_PASS"),
                                      ("caller", "INDEPENDENT_RESTRICTED_ROOT_THREE_LINE_CALLER_V1_CONTROLS_PASS")):
                gate = dict(record); gate.update(status=gate_status, result=result[kind])
                if kind == "kernel":
                    gate.update(unique_fixture_role_records=4032, strict_author_negative_cases=95, whole_prefix_resume_equalities=3)
                save(out / (kind + "_controls_gate.json"), gate)
            record["outputs_sha256"] = {path.relative_to(ROOT).as_posix(): sha(path) for path in out.rglob("*") if path.is_file()}
        save(out / "summary.json", record); print(json.dumps(dict(status=status, mode=args.mode)))
    except Exception as error:
        if not (out / "failure.json").exists():
            save(out / "failure.json", dict(status="UNKNOWN_FAILED_OR_INCOMPLETE", error=repr(error), inputs_sha256=pins,
                 timestamp=datetime.now(timezone.utc).isoformat(), deadline=deadline.status(), automatic_retry=False,
                 restart="Preserve original artifacts and completed per-run replay records. New source or corrected invocation requires ROOT review and separate authorization.",
                 target_resolution="NONE"))
        raise


if __name__ == "__main__": main()
