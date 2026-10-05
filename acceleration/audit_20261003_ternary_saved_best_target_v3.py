"""SOURCE ONLY: complete Saved-BEST all-line census, separately bound input.

No Native parser, topology, scorer, projector or state code is imported. The
unchanged independent full-row/int64 record path and calibrated wire reader
are reused; this caller adds one complete invocation and its exact provenance.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline
import audit_20261003_ternary_saved_best_caller_controls_v3 as reader

kernel, core, io, ROOT = reader.kernel, reader.core, reader.io, reader.ROOT
SELF = "acceleration/audit_20261003_ternary_saved_best_target_v3.py"
SPEC = "acceleration/audit_20261003_ternary_saved_best_target_v3_spec.md"
CAL_PASS = "INDEPENDENT_TERNARY_SAVED_BEST_ALL_LINE_CENSUS_V1_CALIBRATION_PASS"
PASS = "INDEPENDENT_TERNARY_SAVED_BEST_ALL_LINE_CENSUS_V1_COMPLETE_PASS"
CALLER_GATE = "acceleration/results/20261003_independent_review/ternary_saved_best_caller_full01/summary.json"
CALLER_GATE_SHA = "b58f23b9f8b0154b5174b45a6865e311cceae5f1fcbbb5291423138dc2082630"
PROJECTOR = "acceleration/project_20261003_ternary_mixed_saved_best_v2.py"
PROJECTOR_SPEC = "acceleration/project_20261003_ternary_mixed_saved_best_v2_spec.md"
PROJECTOR_PINS = {PROJECTOR:"0395227419dfb9140480cf58f7c6410940f345c69f2bdf8c54fc96f8a5112307",
    PROJECTOR_SPEC:"cecda6b65b24e1cbba7bb73078cbd4d3266aa82b47925d813a991c43c3e3ca9f"}
START_PINS = {
    "acceleration/results/20261003_ternary_mixed_pilot03/native/final.state":"140c3603069f01c59043c7642f7c0cff625f6a31a9386d04930bf99825188640",
    "acceleration/results/20261003_ternary_mixed_pilot03/native/best.adj":"bf313e3060513d501f8c7c6abe22f08f1b5b459e2ed252c6bf40f376a2fbef35",
    "acceleration/results/20261003_independent_review/ternary_mixed_saved_pilot03/summary.json":"7e43e40dc25d6130a7b11e648a2444b7d49c85b2e8743d641a28322fa4c4c7dd"}
START_MATRIX_SHA = list(START_PINS.values())[1]
STATIC = {**reader.STATIC, **PROJECTOR_PINS, reader.SELF:"b650568fa072abd042ff36976d5b7d9a0892c1c4bc272d798483be8ddb3ba114",
    reader.SPEC:"7ad7124515fd0914184b26de1636ab57c0c59125a4cbb08757bbd7968575ba72",
    "docs/COMPUTE_POLICY.md":"9d3f57e8e36376e71fe5fb2733d19d6c0eacf92c71f763e66224dda95f59e136"}
RECEIPT_KEYS = set("timestamp producer command cwd python source_reference_commit inputs_sha256 software source_graph_sha256 baseline_metrics graph_input_sha256 manifest_sha256 scientific_census_launched native_calls all_lines_mutable historical_native_state_written rng_or_trajectory_imported independent_approval target_resolution deadline".split())


def merge(*maps):
    result = {}
    for value in maps:
        io.need(type(value) is dict, "IMMUTABLE_INPUT_MAP")
        for name, identity in value.items():
            io.need(type(name) is str and type(identity) is str and len(identity)==64
                and all(c in "0123456789abcdef" for c in identity), "IMMUTABLE_INPUT_MAP")
            io.relative_file(ROOT,name,ROOT)
            io.need(name not in ("CLAIMS.yaml", ".git/index") and not name.startswith(".git/"), "IMMUTABLE_INPUT_ROLE")
            io.need(name not in result or result[name]==identity, "IMMUTABLE_INPUT_CONFLICT", name)
            result[name]=identity
    return result


def complete_scalar(base):
    neighbors, cn, metrics = kernel.scalar_sets(base.n,base.degree,base.rows)
    io.need(io.same(metrics,base.metrics) and io.same(cn,base.cn.tolist())
        and all(int(base.adjacency[u,v])==int(v in neighbors[u]) for u in range(base.n) for v in range(base.n)), "COMPLETE_SCALAR_MATRIX")
    return dict(binary_adjacency_entries=base.n**2,integer_common_neighbor_entries=base.n**2,
        unordered_pair_scores=base.n*(base.n-1)//2,true_product_diagonal=2*base.degree)


def whole_boundary(base,directory,manifest,identity,chunk=5000):
    io.need(type(manifest) is dict and io.same(manifest.get("identity"),identity), "WHOLE_IDENTITY")
    io.need(all(io.integer(manifest.get(k)) for k in ("population","completed_proposals","starting_proposal_id","proposals_evaluated_this_invocation"))
        and manifest["population"]==base.total and manifest["completed_proposals"]==base.total
        and manifest["starting_proposal_id"]==0 and manifest["proposals_evaluated_this_invocation"]==base.total, "WHOLE_POPULATION")
    io.need(manifest.get("status")=="CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK" and manifest.get("budget_stop") is False, "WHOLE_COMPLETION")
    parts,cps=manifest.get("parts"),manifest.get("checkpoints");needed=(base.total+chunk-1)//chunk
    io.need(type(parts) is list and len(parts)==needed and type(cps) is list and len(cps)==max(1,needed), "WHOLE_CHUNKS")
    for at,part in enumerate(parts):
        io.need(type(part) is dict and io.integer(part.get("start")) and io.integer(part.get("end"))
            and part["start"]==at*chunk and part["end"]==min((at+1)*chunk,base.total), "WHOLE_PART_BOUNDARY")
        io.relative_file(ROOT,part.get("path"),directory)
    for ref in cps: io.need(type(ref) is dict,"WHOLE_CHECKPOINT_REFERENCE");io.relative_file(ROOT,ref.get("path"),directory)


def input_scope(gate,base,wire_name,wire_sha,source_sha,prerequisite):
    reader.input_gate(gate,base,wire_name,wire_sha,source_sha,prerequisite)
    state,matrix,saved=list(prerequisite)
    expected=dict(source_state_path=state,source_state_sha256=prerequisite[state],source_matrix_path=matrix,
        source_matrix_sha256=prerequisite[matrix],prerequisite_saved_full_report_path=saved,
        prerequisite_saved_full_report_sha256=prerequisite[saved])
    io.need(all(gate.get(k)==v for k,v in expected.items())
        and gate.get("whole_source_state_checked") is True and gate.get("source_state_history_authenticated_but_not_imported") is True
        and all(gate["inputs_sha256"].get(p)==h for p,h in PROJECTOR_PINS.items()), "SAVED_BEST_INPUT_SCOPE")


def graph_payload(raw,base,wire_name,wire_sha,source_sha,prerequisite):
    expected=dict(schema="TERNARY_SAVED_BEST_ALL_LINE_CENSUS_INPUT_V1",n=base.n,point_degree=base.degree,
        ordered_triples=[list(row) for row in base.rows],metrics=base.metrics,source_graph_sha256=source_sha,
        graph_input_path=wire_name,graph_input_sha256=wire_sha,saved_best_prerequisite_pins=prerequisite,
        all_lines_mutable=True,historical_native_state_written=False,rng_or_trajectory_imported=False)
    io.need(io.same(raw,expected), "ORIGINAL_GRAPH_INPUT_IDENTITY")
    return complete_scalar(base)


def census_receipt(raw,graph_sha,manifest_sha,base,inputs,software,source_sha,worker,context):
    io.need(type(raw) is dict and set(raw)==RECEIPT_KEYS and type(raw.get("timestamp")) is str and bool(raw["timestamp"])
        and raw.get("producer")=="/root/native_driver" and io.same(raw.get("command"),worker)
        and raw.get("cwd")==reader.LINUX_ROOT and raw.get("python")=="3.12.3" and raw.get("source_reference_commit")==context
        and io.same(raw.get("inputs_sha256"),inputs) and io.same(raw.get("software"),software)
        and raw.get("source_graph_sha256")==source_sha and io.same(raw.get("baseline_metrics"),base.metrics)
        and raw.get("graph_input_sha256")==graph_sha and raw.get("manifest_sha256")==manifest_sha
        and raw.get("scientific_census_launched") is True and io.integer(raw.get("native_calls")) and raw["native_calls"]==0
        and raw.get("all_lines_mutable") is True and raw.get("historical_native_state_written") is False
        and raw.get("rng_or_trajectory_imported") is False and raw.get("independent_approval") is False
        and raw.get("target_resolution")=="NONE" and type(raw.get("deadline")) is dict, "CENSUS_RECEIPT")


def model_identity(base,inputs,software,wire_name,wire_sha,source_sha,context,prerequisite):
    return dict(schema="TERNARY_SAVED_BEST_NEIGHBORHOOD_IDENTITY_V1",inputs_sha256=inputs,software=software,
        objective_version=core.OBJECTIVE,n=base.n,point_degree=base.degree,total=base.total,
        graph_input_path=wire_name,graph_input_sha256=wire_sha,source_graph_sha256=source_sha,
        saved_best_prerequisite_pins=prerequisite,source_reference_commit=context,
        all_lines_mutable=True,lambda_zero_filter=False,root_filter=False,historical_native_state_written=False,rng_or_trajectory_imported=False,
        question="Does this exact Saved-BEST graph admit a valid labelled two-line swap with smaller exact(F3,E), or exact zero?",
        selection_rule="All valid labels eligible;minimum(F3,E),then proposalID;no graph-space/global-optimum claim.")


def linux_profile(runtime,terminal,plan,admission,software,direct,plan_name,plan_sha,context,author,runtime_name,wire_name,wire_sha,input_name,input_sha):
    child=["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3",
        "python","-B",reader.CALLER,"census","--seconds","550","--out",author,"--supervision-out",runtime_name,"--source-commit",context,
        "--kernel-gate",reader.KERNEL_GATE,"--kernel-gate-sha256",reader.KERNEL_GATE_SHA,
        "--caller-gate",CALLER_GATE,"--caller-gate-sha256",CALLER_GATE_SHA,
        "--input-gate",input_name,"--input-gate-sha256",input_sha,"--wire",wire_name,"--wire-sha256",wire_sha]
    command=plan.get("command");nwords=15+len(child)
    io.need(type(command) is list and len(command)==nwords and command.count("--")==1 and command.index("--")==14
        and command[:6]==["/usr/bin/python3",reader.SUP,"--seconds","600","--shutdown-reserve-seconds","20"]
        and command[6:12:2]==["--allocation-reason","--success-criterion","--verification-criterion"]
        and all(type(command[k]) is str and bool(command[k]) for k in (7,9,11))
        and command[12:14]==["--out",runtime_name] and io.same(command[15:],child)
        and io.same(plan.get("child_command"),child) and io.same(plan.get("worker_command"),child[12:])
        and io.same(runtime.get("command"),child) and runtime.get("cwd")==reader.LINUX_ROOT
        and runtime.get("source_sha256")==software[reader.SUP]
        and type(runtime.get("seconds")) in (int,float) and runtime["seconds"]==600
        and type(runtime.get("shutdown_reserve_seconds")) in (int,float) and runtime["shutdown_reserve_seconds"]==20
        and runtime.get("runtime_scope")=="LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2"
        and runtime.get("automatic_retry") is False and runtime.get("cumulative_across_commands") is False, "LINUX_CENSUS_PROFILE")
    cleanup=terminal.get("cleanup");obs=cleanup.get("cleanup_observations") if type(cleanup) is dict else None
    io.need(type(cleanup) is dict and cleanup.get("reaped") is True and cleanup.get("job_active_zero_observed") is True
        and io.integer(cleanup.get("actual_exit_code")) and cleanup["actual_exit_code"]==0
        and cleanup.get("cleanup_errors")==[] and cleanup.get("process_group_live_pids")==[]
        and io.integer(cleanup.get("cleanup_observation_count")) and type(obs) is list and len(obs)>=1
        and cleanup["cleanup_observation_count"]==len(obs) and type(obs[-1]) is dict
        and obs[-1].get("live_pids")==[] and obs[-1].get("unreadable_pids")==[]
        and io.integer(terminal.get("command_exit_code")) and terminal["command_exit_code"]==0
        and terminal.get("stop_reason")=="COMMAND_EXITED" and terminal.get("deadline_reached") is False
        and terminal.get("hard_limit_observed") is True and type(terminal.get("invocation_id")) is str
        and bool(terminal["invocation_id"]) and terminal["invocation_id"]==runtime.get("invocation_id"), "LINUX_TERMINAL")
    probe=admission.get("default_uid_probe");ap=admission.get("plan")
    io.need(admission.get("schema")=="TERNARY_SAVED_BEST_TWO_LINE_CALLER_CENSUS_ADMISSION_V1" and type(probe) is dict
        and probe.get("command")==["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"]
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"]=="1000" and io.integer(probe.get("exit_code")) and probe["exit_code"]==0
        and admission.get("admitted") is True and admission.get("scientific_launched") is False
        and admission.get("actual_target_input_read") is True and type(admission.get("actual_target_input_read_scope")) is str
        and bool(admission["actual_target_input_read_scope"]) and admission.get("automatic_retry") is False
        and admission.get("paths_absent") is True and io.integer(admission.get("native_calls")) and admission["native_calls"]==0
        and type(ap) is dict and ap.get("path")==plan_name and ap.get("sha256")==plan_sha
        and io.integer(ap.get("words")) and ap["words"]==nwords, "UID_CENSUS_ADMISSION")
    io.need(io.same(admission.get("source_pins"),direct) and admission.get("source_pins_all_match") is True, "ADMISSION_SOURCE_PINS")
    interpreter=reader.LINUX_ROOT+"/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3"
    return [interpreter,*child[14:]]


def require_target_zero(adjacency):
    result=core.full_integer_target(adjacency)
    io.need(result["degree14"] is True and result["is_target"] is True, "RESIDUE_ZERO_FULL_INTEGER_TARGET")
    return result


def objects(base,directory,manifest,result,reserve):
    raw=kernel.audit_objects(base,directory,manifest,result);zeros=[]
    for item,ref in zip(raw,manifest["residue_zero_objects"]):
        reserve();rows=io.strict_json(io.relative_file(ROOT,ref["triples_path"],directory).read_bytes())["ordered_triples"]
        fresh=core.fixed_input(base.n,base.degree,rows);scalar=complete_scalar(fresh)
        target=require_target_zero(fresh.adjacency) if (base.n,base.degree)==(99,7) else None
        zeros.append(dict(proposal_id=item["proposal_id"],matrix_sha256=item["matrix_sha256"],complete_scalar_checks=scalar,
            full_integer_target=target,ROOT_review_required=target is not None,
            target_null_reason=None if target is not None else "Generic fixture outside99/7 target domain."))
    selected=result["selected"];selected_check=None
    if selected is not None:
        reserve();fresh=core.fixed_input(base.n,base.degree,kernel.rows_for(base,selected));scalar=complete_scalar(fresh)
        selected_check=dict(proposal_id=selected["proposal_id"],metrics=fresh.metrics,complete_scalar_checks=scalar,
            full_integer_target=core.full_integer_target(fresh.adjacency) if (base.n,base.degree)==(99,7) else None)
    return zeros,selected_check


def output_population(directory,manifest,scientific=True):
    expected={directory/name for name in ("manifest.json","minimum_F3_ties.json","minimum_pair_ties.json")}
    if scientific: expected.update(directory/name for name in ("graph_input.json","run_receipt.json"))
    expected.update(io.relative_file(ROOT,part["path"],directory) for part in manifest["parts"])
    expected.update(io.relative_file(ROOT,ref["path"],directory) for ref in manifest["checkpoints"])
    if manifest["selected_proposal_id"] is not None: expected.update(directory/name for name in ("selected_neighbor.adj","selected_neighbor_triples.json"))
    for ref in manifest["residue_zero_objects"]:
        expected.update(io.relative_file(ROOT,ref[key],directory) for key in ("adjacency_path","triples_path"))
    actual={path.resolve() for path in directory.rglob("*") if path.is_file()}
    io.need(actual=={path.resolve() for path in expected}, "ORIGINAL_OUTPUT_POPULATION")
    return actual


GENUINE_PROFILE_PINS = {
    "acceleration/plan_20261003_ternary_saved_best_census_v1.json":"98630959e28520068d77fcb6d09543671562ca5663cc4af31c7b9f41fa967a0c",
    "acceleration/results/20261003_ternary_saved_best_census_admission01.json":"73a491c788c2f953451499e9bc43b5df6c9826adb9ee4d8e9a4c7a14570c974e",
    "acceleration/results/20261003_ternary_saved_best_census_supervision01/manifest.json":"de0fc2b666b94faf9b51e55ebacd6b399936f779c7427ac74cd887a969c72902",
    "acceleration/results/20261003_ternary_saved_best_census_supervision01/summary.json":"45836683743bfa63faac7736fe7fd388fdad843c9c95ae41cde0073160b04eca"}


def genuine_profile_control(out,reserve,software,pin):
    # Four real metadata files only. No wire, matrix, record, part, CP or tie
    # contents are read by this control; their path/hash strings are metadata.
    real={name:io.strict_json(pin(ROOT/name,identity).read_bytes()) for name,identity in GENUINE_PROFILE_PINS.items()}
    plan_name,admission_name,runtime_name,terminal_name=list(GENUINE_PROFILE_PINS)
    plan,admission,runtime,terminal=(real[name] for name in (plan_name,admission_name,runtime_name,terminal_name))
    wire_name="acceleration/results/20261003_ternary_mixed_saved_best_projection01/graph_input.txt"
    wire_sha="c5641c473f714d516505e5a87134b6ce6c2b1f93fbb921d26db68f5f042732f7"
    input_name="acceleration/results/20261003_independent_review/ternary_mixed_saved_best_input_full01/summary.json"
    input_sha="0b78305195cfb65397971c80d210f56018b1da592d0e377ab31532ef7f1e91b6"
    context="d0c0dd7db0d3de420b1d718b59122b069df01107"
    author="acceleration/results/20261003_ternary_saved_best_census01"
    runtime_dir="acceleration/results/20261003_ternary_saved_best_census_supervision01"
    direct=merge(software,{reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA,
        input_name:input_sha,wire_name:wire_sha},START_PINS)
    io.need(io.same(plan.get("direct_inputs_sha256"),direct),"GENUINE_PROFILE_PLAN_PINS")
    def profile(value):
        return linux_profile(runtime,terminal,plan,value,software,direct,plan_name,GENUINE_PROFILE_PINS[plan_name],context,
            author,runtime_dir,wire_name,wire_sha,input_name,input_sha)
    worker=profile(admission);negatives=[]
    legacy=copy.deepcopy(admission);legacy["default_uid_probe"]["exit"]=legacy["default_uid_probe"].pop("exit_code")
    negatives.append(reader.reject("genuine_uid_legacy_exit_field","UID_CENSUS_ADMISSION",lambda:profile(legacy)))
    alias=copy.deepcopy(admission);alias["default_uid_probe"]["exit_code"]=False
    negatives.append(reader.reject("genuine_uid_bool_exit_code","UID_CENSUS_ADMISSION",lambda:profile(alias)))
    result=dict(case="genuine_Native_SUP2_census_admission_runtime_profile",observed_producer_execution=True,
        profile_payload_population=4,original_payloads_sha256=GENUINE_PROFILE_PINS,invocation_id=runtime["invocation_id"],
        producer_command=runtime["command"],producer_worker_sysargv=worker,complete_source_pin_population=len(direct),
        complete_source_pin_map_compared=True,complete_source_pin_payloads_rehashed=False,
        producer_runtime_admission_checked=True,producer_census_records_checked=False,
        actual_target_input_read=False,actual_graph_matrix_read=False,
        observed_cleanup_scope="Original Native inside-Linux SUP2 group; separate own-calibration containment is WindowsJob.")
    kernel.save(out/"genuine_producer_profile_control.json",result);reserve()
    return result,negatives

def calibration(out,reserve,software,kernel_software,pin):
    positives=[];negatives=[]
    for name,n,degree,rows in [("single_triangle",3,1,[[0,1,2]]),("rook9",*kernel.fixtures()["rook9"])]:
        reserve();base=core.fixed_input(n,degree,rows);records=[core.expected_record(base,pid)[0] for pid in range(base.total)]
        marker=dict(synthetic_complete_frame=True,fixture=name);directory=out/name
        manifest=kernel.emit_synthetic(base,directory,marker,records,base.total)
        whole_boundary(base,directory,manifest,marker,50);result=kernel.audit_run(base,directory,manifest,marker,reserve)
        zero,selected=objects(base,directory,manifest,result,reserve);output_population(directory,manifest,False)
        positives.append(dict(case=name,complete_labels=base.total,complete_parts=len(manifest["parts"]),zero_objects=len(zero)))
    reject=reader.reject
    for label,key,value,stage in [("start_bool","starting_proposal_id",False,"WHOLE_POPULATION"),("shifted_start","starting_proposal_id",1,"WHOLE_POPULATION"),
        ("short_stop","completed_proposals",134,"WHOLE_POPULATION"),("count_float","proposals_evaluated_this_invocation",135.0,"WHOLE_POPULATION"),
        ("population_bool","population",True,"WHOLE_POPULATION"),("budget_integer","budget_stop",0,"WHOLE_COMPLETION"),
        ("prefix_status","status","UNKNOWN_PREFIX_ONLY","WHOLE_COMPLETION"),("missing_CP","checkpoints",manifest["checkpoints"][:-1],"WHOLE_CHUNKS"),
        ("duplicate_part","parts",manifest["parts"]+manifest["parts"][:1],"WHOLE_CHUNKS")]:
        bad=copy.deepcopy(manifest);bad[key]=value;negatives.append(reject(label,stage,lambda b=bad:whole_boundary(base,directory,b,marker,50)))
    bad=copy.deepcopy(manifest);bad["parts"][0]["start"]=False
    negatives.append(reject("part_start_bool","WHOLE_PART_BOUNDARY",lambda:whole_boundary(base,directory,bad,marker,50)))
    extra=directory/"unlisted.json";extra.write_bytes(b"{}\n")
    negatives.append(reject("unlisted_output","ORIGINAL_OUTPUT_POPULATION",lambda:output_population(directory,manifest,False)));extra.unlink()
    # V2 calibration-only repair: retain damaged bytes outside the fixture tree,
    # then replace existing test files explicitly. kernel.save remains create-only.
    damage_dir=out/"damaged_raw_counterparts";reserve();damage_dir.mkdir();reserve();retained={}
    def retained_payload(name,value):
        reserve();payload=value if type(value) is bytes else (json.dumps(value,indent=2,allow_nan=False)+"\n").encode("utf8")
        path=damage_dir/name;io.need(not path.exists(),"CALIBRATION_DAMAGE_PATH")
        path.write_bytes(payload);reserve()
        retained[name]=dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(payload).hexdigest())
        return payload
    tie_file=directory/"minimum_F3_ties.json";raw=tie_file.read_bytes();bad_ties=io.strict_json(raw);bad_ties["records"]=bad_ties["records"][:-1]
    damaged=retained_payload("truncated_literal_ties.json",bad_ties)
    try:
        reserve();tie_file.write_bytes(damaged);reserve()
        negatives.append(reject("truncated_literal_ties","TIE_RECORDS",lambda:objects(base,directory,manifest,result,reserve)))
    finally:tie_file.write_bytes(raw);reserve()
    selected_file=directory/"selected_neighbor.adj";raw=selected_file.read_bytes()
    damaged=retained_payload("changed_selected_matrix.adj",(b"1" if raw[:1]!=b"1" else b"0")+raw[1:])
    try:
        reserve();selected_file.write_bytes(damaged);reserve()
        negatives.append(reject("changed_selected_matrix","SELECTED_MATRIX",lambda:objects(base,directory,manifest,result,reserve)))
    finally:selected_file.write_bytes(raw);reserve()
    bad=copy.deepcopy(manifest);bad["residue_zero_objects"]=bad["residue_zero_objects"][:-1]
    manifest_file=directory/"manifest.json";raw=manifest_file.read_bytes();damaged=retained_payload("missing_zero_export_manifest.json",bad)
    try:
        reserve();manifest_file.write_bytes(damaged);reserve()
        negatives.append(reject("missing_zero_export","ZERO_POPULATION",lambda:objects(base,directory,io.strict_json(manifest_file.read_bytes()),result,reserve)))
    finally:manifest_file.write_bytes(raw);reserve()
    cp_ref=manifest["checkpoints"][0];cp_file=io.relative_file(ROOT,cp_ref["path"],directory);raw=cp_file.read_bytes()
    bad=copy.deepcopy(manifest);bad_cp=io.strict_json(raw);bad_cp["next_proposal_id"]=True
    damaged=retained_payload("checkpoint_bool_prefix.json",bad_cp)
    try:
        reserve();cp_file.write_bytes(damaged);reserve();bad["checkpoints"][0]["sha256"]=io.sha(cp_file);reserve()
        negatives.append(reject("checkpoint_bool_prefix","CHECKPOINT_COVERAGE",lambda:kernel.audit_run(base,directory,bad,marker,reserve)))
    finally:cp_file.write_bytes(raw);reserve()
    generic,gates,prerequisite=reader.synthetic_gates(software,kernel_software);source=hashlib.sha256(io.matrix_bytes(generic.adjacency)).hexdigest()
    wire_name="build/synthetic-geometry.wire";wire_sha="1"*64;gate=gates["INPUT_GATE"]
    state,matrix,saved=list(prerequisite);gate.update(source_state_path=state,source_state_sha256=prerequisite[state],source_matrix_path=matrix,
        source_matrix_sha256=prerequisite[matrix],prerequisite_saved_full_report_path=saved,prerequisite_saved_full_report_sha256=prerequisite[saved],
        whole_source_state_checked=True,source_state_history_authenticated_but_not_imported=True)
    gate["inputs_sha256"].update(PROJECTOR_PINS);input_scope(gate,generic,wire_name,wire_sha,source,prerequisite)
    payload=dict(schema="TERNARY_SAVED_BEST_ALL_LINE_CENSUS_INPUT_V1",n=9,point_degree=2,ordered_triples=[list(r) for r in generic.rows],metrics=generic.metrics,
        source_graph_sha256=source,graph_input_path=wire_name,graph_input_sha256=wire_sha,saved_best_prerequisite_pins=prerequisite,
        all_lines_mutable=True,historical_native_state_written=False,rng_or_trajectory_imported=False)
    graph_payload(payload,generic,wire_name,wire_sha,source,prerequisite);positives.append(dict(case="synthetic_new_input_scope_and_payload",observed_execution=False))
    for label,key,value in [("input_old_state","source_state_path","old"),("input_wrong_matrix","source_matrix_sha256","0"*64),
        ("input_not_whole_state","whole_source_state_checked",False),("input_history_imported","source_state_history_authenticated_but_not_imported",False)]:
        bad=copy.deepcopy(gate);bad[key]=value;negatives.append(reject(label,"SAVED_BEST_INPUT_SCOPE",lambda b=bad:input_scope(b,generic,wire_name,wire_sha,source,prerequisite)))
    bad=copy.deepcopy(gate);bad["inputs_sha256"].pop(PROJECTOR)
    negatives.append(reject("input_old_projector","SAVED_BEST_INPUT_SCOPE",lambda:input_scope(bad,generic,wire_name,wire_sha,source,prerequisite)))
    for label,key,value in [("payload_bool_n","n",True),("payload_extra_history","history",{}),("payload_wrong_rows","ordered_triples",[]),
        ("payload_wrong_wire","graph_input_sha256","0"*64),("payload_false_mutable","all_lines_mutable",False)]:
        bad=copy.deepcopy(payload);bad[key]=value;negatives.append(reject(label,"ORIGINAL_GRAPH_INPUT_IDENTITY",lambda b=bad:graph_payload(b,generic,wire_name,wire_sha,source,prerequisite)))
    context="d0c0dd7db0d3de420b1d718b59122b069df01107";author="build/synthetic-census";runtime_name="build/synthetic-supervision"
    plan_name="build/synthetic-plan.json";plan_sha="2"*64;input_name="build/synthetic-input-gate.json";input_sha="3"*64
    direct={**software,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA,input_name:input_sha,wire_name:wire_sha,**prerequisite}
    child=["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline","--project",
        "acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python","-B",reader.CALLER,
        "census","--seconds","550","--out",author,"--supervision-out",runtime_name,"--source-commit",context,
        "--kernel-gate",reader.KERNEL_GATE,"--kernel-gate-sha256",reader.KERNEL_GATE_SHA,"--caller-gate",CALLER_GATE,"--caller-gate-sha256",CALLER_GATE_SHA,
        "--input-gate",input_name,"--input-gate-sha256",input_sha,"--wire",wire_name,"--wire-sha256",wire_sha]
    plan=dict(command=["/usr/bin/python3",reader.SUP,"--seconds","600","--shutdown-reserve-seconds","20","--allocation-reason","synthetic",
        "--success-criterion","synthetic","--verification-criterion","synthetic","--out",runtime_name,"--",*child],child_command=child,worker_command=child[12:])
    runtime=dict(command=child,cwd=reader.LINUX_ROOT,source_sha256=software[reader.SUP],seconds=600.0,shutdown_reserve_seconds=20.0,
        runtime_scope="LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2",automatic_retry=False,cumulative_across_commands=False,invocation_id="synthetic_profile_only")
    terminal=dict(command_exit_code=0,invocation_id=runtime["invocation_id"],stop_reason="COMMAND_EXITED",deadline_reached=False,hard_limit_observed=True,
        cleanup=dict(reaped=True,actual_exit_code=0,cleanup_errors=[],process_group_live_pids=[],job_active_zero_observed=True,
            cleanup_observation_count=1,cleanup_observations=[dict(live_pids=[],unreadable_pids=[])]))
    admission=dict(schema="TERNARY_SAVED_BEST_TWO_LINE_CALLER_CENSUS_ADMISSION_V1",default_uid_probe=dict(
        command=["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"],stdout_uid="1000",exit_code=0),admitted=True,scientific_launched=False,
        actual_target_input_read=True,actual_target_input_read_scope="Synthetic metadata only.",automatic_retry=False,paths_absent=True,native_calls=0,
        plan=dict(path=plan_name,sha256=plan_sha,words=len(plan["command"])),source_pins=direct,source_pins_all_match=True)
    def profile(values):return linux_profile(values[0],values[1],values[2],values[3],software,direct,plan_name,plan_sha,context,author,runtime_name,wire_name,wire_sha,input_name,input_sha)
    values=[runtime,terminal,plan,admission];worker=profile(values);positives.append(dict(case="synthetic_SUP2_census_UID_profile",observed_execution=False))
    for label,which,path,value,stage in [("profile_old_source",0,["source_sha256"],"0"*64,"LINUX_CENSUS_PROFILE"),
        ("profile_missing_B",2,["child_command"],child[:13]+child[14:],"LINUX_CENSUS_PROFILE"),
        ("profile_wrong_seconds",0,["seconds"],120,"LINUX_CENSUS_PROFILE"),("profile_wrong_scope",0,["runtime_scope"],"OLD","LINUX_CENSUS_PROFILE"),
        ("terminal_exit_bool",1,["cleanup","actual_exit_code"],False,"LINUX_TERMINAL"),("terminal_live_pid",1,["cleanup","process_group_live_pids"],[1],"LINUX_TERMINAL"),
        ("terminal_unreadable",1,["cleanup","cleanup_observations"],[dict(live_pids=[],unreadable_pids=[1])],"LINUX_TERMINAL"),
        ("uid_integer",3,["default_uid_probe","stdout_uid"],1000,"UID_CENSUS_ADMISSION"),("uid_bool_exit",3,["default_uid_probe","exit_code"],False,"UID_CENSUS_ADMISSION"),
        ("admission_bool_words",3,["plan","words"],True,"UID_CENSUS_ADMISSION"),("admission_science_started",3,["scientific_launched"],True,"UID_CENSUS_ADMISSION"),
        ("admission_wrong_map",3,["source_pins"],{},"ADMISSION_SOURCE_PINS")]:
        v=copy.deepcopy(values);node=v[which]
        for k in path[:-1]:node=node[k]
        node[path[-1]]=value;negatives.append(reject(label,stage,lambda v=v:profile(v)))
    inputs=direct;graph_sha="4"*64;manifest_sha="5"*64
    receipt=dict(timestamp="synthetic",producer="/root/native_driver",command=worker,cwd=reader.LINUX_ROOT,python="3.12.3",source_reference_commit=context,
        inputs_sha256=inputs,software=software,source_graph_sha256=source,baseline_metrics=generic.metrics,graph_input_sha256=graph_sha,
        manifest_sha256=manifest_sha,scientific_census_launched=True,native_calls=0,all_lines_mutable=True,historical_native_state_written=False,
        rng_or_trajectory_imported=False,independent_approval=False,target_resolution="NONE",deadline={})
    census_receipt(receipt,graph_sha,manifest_sha,generic,inputs,software,source,worker,context)
    positives.append(dict(case="synthetic_new_census_receipt",observed_execution=False))
    for label,key,value in [("receipt_old_tqdm","tqdm","4.67.1"),("receipt_manifest_wrong","manifest_sha256","0"*64),
        ("receipt_wrong_software","software",{}),("receipt_native_bool","native_calls",False),("receipt_RNG_true","rng_or_trajectory_imported",True),
        ("receipt_worker_B_present","command",[worker[0],"-B",*worker[1:]]),("receipt_history_true","historical_native_state_written",True),
        ("receipt_selfapproved","independent_approval",True)]:
        bad=copy.deepcopy(receipt);bad[key]=value
        negatives.append(reject(label,"CENSUS_RECEIPT",lambda b=bad:census_receipt(b,graph_sha,manifest_sha,generic,inputs,software,source,worker,context)))
    rows=kernel.fixtures()["rook9"][2];rho2=core.fixed_input(99,2,[[v+9*b for v in row] for b in range(11) for row in rows])
    negatives.append(reject("constructed99_rho2_not_target","RESIDUE_ZERO_FULL_INTEGER_TARGET",lambda:require_target_zero(rho2.adjacency)))
    genuine,extra_negatives=genuine_profile_control(out,reserve,software,pin)
    positives.append(genuine);negatives.extend(extra_negatives)
    io.need(len(positives)==6 and len(negatives)==48,"CALIBRATION_POPULATION")
    kernel.save(out/"negative_controls.json",negatives);reserve()
    return dict(positive_controls=6,synthetic_positive_controls=5,genuine_positive_profile_controls=1,
        strict_negative_controls=48,complete_generic_labels=135,
        fixtures=positives,constructed99_rho2_target_veto_cells=9801,actual_target_input_read=False,actual_graph_matrix_read=False,
        producer_outputs_checked=True,producer_outputs_checked_scope="Four original producer runtime/admission/plan/terminal metadata payloads only; no census record or graph payload read.",
        producer_runtime_admission_checked=True,producer_census_records_checked=False,genuine_profile_payload_population=4,
        genuine_profile_original_payloads_sha256=GENUINE_PROFILE_PINS,
        synthetic_profile_receipt_are_execution_observations=False,framing_checker_implementation_version=3,
        durable_corruption_counterparts=retained,
        transient_damage_retention="Four damaged raw counterparts are persisted before test and original fixture bytes restored. Other malformed values are source-reproducible in-memory cases; their bytes are not individually persisted.")


def actual(out,pins,software,kernel_software,reserve,args,pin):
    required=("author_out","supervision","author_plan","author_admission","wire","input_gate")
    io.need(all(getattr(args,k) is not None for k in required),"ACTUAL_ARGUMENT_BOUNDARY")
    hashes=("author_plan_sha256","author_admission_sha256","runtime_manifest_sha256","terminal_sha256","wire_sha256",
        "input_gate_sha256","graph_sha256","receipt_sha256","census_manifest_sha256")
    io.need(all(type(getattr(args,k)) is str and len(getattr(args,k))==64
        and all(c in "0123456789abcdef" for c in getattr(args,k)) for k in hashes),"ACTUAL_ARGUMENT_IDENTITIES")
    for k in required:io.need(getattr(args,k).resolve().is_relative_to(ROOT),"ARTIFACT_PATH")
    name=lambda p:p.resolve().relative_to(ROOT).as_posix()
    plan=io.strict_json(pin(args.author_plan,args.author_plan_sha256).read_bytes())
    admission=io.strict_json(pin(args.author_admission,args.author_admission_sha256).read_bytes())
    runtime_file=pin(args.supervision/"manifest.json",args.runtime_manifest_sha256)
    runtime=io.strict_json(runtime_file.read_bytes());terminal=io.strict_json(pin(args.supervision/"summary.json",args.terminal_sha256).read_bytes())
    wire_file=pin(args.wire,args.wire_sha256);base,source,triangles=reader.wire(wire_file.read_bytes())
    io.need((base.n,base.degree,len(base.rows),base.total)==(99,7,231,239085) and source==START_MATRIX_SHA,"TARGET_START")
    gates=[]
    for path,identity in [(ROOT/reader.KERNEL_GATE,reader.KERNEL_GATE_SHA),(ROOT/CALLER_GATE,CALLER_GATE_SHA),(args.input_gate,args.input_gate_sha256)]:
        gates.append(io.strict_json(pin(path,identity).read_bytes()))
    reader.finite_gate("KERNEL_GATE",gates[0],software,kernel_software);reader.finite_gate("CALLER_GATE",gates[1],software,kernel_software)
    input_scope(gates[2],base,name(wire_file),args.wire_sha256,source,START_PINS)
    direct=merge(software,{reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA,name(args.input_gate):args.input_gate_sha256,
        name(wire_file):args.wire_sha256},START_PINS)
    worker=linux_profile(runtime,terminal,plan,admission,software,direct,name(args.author_plan),args.author_plan_sha256,args.source_commit,
        name(args.author_out),name(args.supervision),name(wire_file),args.wire_sha256,name(args.input_gate),args.input_gate_sha256)
    expected_inputs=merge(software,{name(runtime_file):args.runtime_manifest_sha256,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,
        CALLER_GATE:CALLER_GATE_SHA,name(args.input_gate):args.input_gate_sha256,name(wire_file):args.wire_sha256},*(g["inputs_sha256"] for g in gates))
    for path,identity in expected_inputs.items():pin(ROOT/path,identity)
    for gate in gates:
        # The historical Checkpoint input report has no outputs map. Its complete
        # declared inputs are checked above; do not invent undeclared output pins.
        if "outputs_sha256" in gate:
            io.need(type(gate["outputs_sha256"]) is dict,"GATE_OUTPUT_MAP")
            for path,identity in gate["outputs_sha256"].items():pin(io.relative_file(ROOT,path,ROOT),identity)
    graph_file=pin(args.author_out/"graph_input.json",args.graph_sha256);raw_graph=io.strict_json(graph_file.read_bytes())
    input_checks=graph_payload(raw_graph,base,name(wire_file),args.wire_sha256,source,START_PINS)
    manifest_file=pin(args.author_out/"manifest.json",args.census_manifest_sha256);manifest=io.strict_json(manifest_file.read_bytes())
    receipt_file=pin(args.author_out/"run_receipt.json",args.receipt_sha256)
    census_receipt(io.strict_json(receipt_file.read_bytes()),args.graph_sha256,args.census_manifest_sha256,base,expected_inputs,software,source,worker,args.source_commit)
    identity=model_identity(base,expected_inputs,software,name(wire_file),args.wire_sha256,source,args.source_commit,START_PINS)
    whole_boundary(base,args.author_out,manifest,identity);original=output_population(args.author_out,manifest)
    for path in sorted(original):pin(path)
    result=kernel.audit_run(base,args.author_out,manifest,identity,reserve);zero,selected=objects(base,args.author_out,manifest,result,reserve)
    if selected is not None:
        selected.update(matrix_path=name(args.author_out/"selected_neighbor.adj"),matrix_sha256=pins[name(args.author_out/"selected_neighbor.adj")],
            triples_path=name(args.author_out/"selected_neighbor_triples.json"),triples_sha256=pins[name(args.author_out/"selected_neighbor_triples.json")])
    tie_checks=[];seen=set()
    for record in [*result["aggregate"].f3_ties,*result["aggregate"].pair_ties]:
        reserve();pid=record["proposal_id"]
        if pid in seen:continue
        fresh=core.fixed_input(base.n,base.degree,kernel.rows_for(base,record));scalar=complete_scalar(fresh)
        io.need(io.same(fresh.metrics,record["new_metrics"]),"TIE_SCALAR_METRICS")
        tie_checks.append(dict(proposal_id=pid,metrics=fresh.metrics,complete_scalar_checks=scalar));seen.add(pid)
    io.need(len(result["records"])==239085 and len(result["checkpoints"])==48,"COMPLETE_TARGET_POPULATION")
    snapshot=result["aggregate"].snapshot();baseline_target=core.full_integer_target(base.adjacency)
    kernel.save(out/"complete_outcome.json",dict(aggregate=snapshot,baseline_metrics=base.metrics,baseline_full_integer_target=baseline_target,
        complete_input_scalar_checks=input_checks,complete_tie_scalar_checks=tie_checks,selected_neighbor=selected,residue_zero_objects=zero));reserve()
    io.need(output_population(args.author_out,manifest)==original,"ORIGINAL_OUTPUT_POPULATION_STABLE")
    for directory in (args.author_out,args.supervision):
        for path in sorted(directory.rglob("*")):
            if path.is_file():pin(path)
    statement=("For the exact Saved-BEST ordered231-triangle wire "+args.wire_sha256+" and reconstructed source matrix "+source
        +", a separate complete integer replay checks all239085 labelled unordered-line-pair/position proposals, all24 record fields, "
        +"all48 fixed5000-record parts/checkpoints (last4085), all minimumF3/minimum(F3,E) ties, the literal selected graph and every deduplicated zero-residue export. "
        +"Baseline(F3,E)="+str([base.metrics["F3"],base.metrics["E"]])+"; classifications="+str(snapshot["counts"])
        +", tuple directions="+str(snapshot["tuple_directions"])+", minimum neighbor(F3,E)="+str(snapshot["minimum_pair"])
        +", selected proposal="+str(None if selected is None else selected["proposal_id"])+", zero-residue exports="+str(len(zero))
        +". Each target-domain zero export is checked against all9801 entries of the full integer SRG identity and requires ROOT review. "
        +"The result concerns one finite allmutable two-line neighborhood, without a root/lambda-zero filter, global optimum, target nonexistence or imported RNG/trajectory. "
        +"Retained construction rows are not asserted to enumerate every actual graph triangle.")
    return dict(statement=statement,scope=dict(description="One exact complete239085-label Saved-BEST allmutable two-line F3/E neighborhood; finite one-move conclusions only.",
        unrestricted_target=False,target_resolution="NONE"),question=identity["question"],selection_rule=identity["selection_rule"],
        original_input_identity_map={name(wire_file):args.wire_sha256,name(args.input_gate):args.input_gate_sha256,**START_PINS},
        actual_original_output_identities={name(graph_file):args.graph_sha256,name(receipt_file):args.receipt_sha256,name(manifest_file):args.census_manifest_sha256},
        software=software,complete_producer_immutable_inputs=len(expected_inputs),complete_labelled_proposals=239085,complete_raw_record_fields=24,
        complete_parts=48,complete_checkpoints=48,chunk_size=5000,last_part_records=4085,aggregate=snapshot,
        baseline_metrics=base.metrics,baseline_full_integer_target=baseline_target,complete_input_scalar_checks=input_checks,
        distinct_ties_fully_scalar_checked=len(tie_checks),selected_neighbor=selected,residue_zero_objects=zero,residue_zero_graphs=len(zero),
        ROOT_review_required_zero_objects=len(zero),all_lines_mutable=True,lambda_zero_filter=False,root_filter=False,
        actual_target_input_read=True,producer_outputs_checked=True,producer_scientific_census_launched=True,
        full_neighborhood_zero_absence=len(zero)==0,new_exclusions=0,historical_native_state_written=False,rng_or_trajectory_imported=False,
        retained_construction_triples_are_all_graph_triangles_claimed=False,actual_graph_triangles=len(triangles),
        overall_search_coverage="UNKNOWN; no validated denominator.",
        cleanup_scope="Producer receipt checks one inside-Linux group; this verifier independently runs under its own supported WindowsJob.")


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("mode",choices=("calibration","check"))
    parser.add_argument("--out",type=Path,required=True);parser.add_argument("--seconds",type=float,required=True)
    for key in ("self-sha256","spec-sha256","source-commit"):parser.add_argument("--"+key,required=True)
    for key in ("calibration","author-out","supervision","author-plan","author-admission","wire","input-gate"):parser.add_argument("--"+key,type=Path)
    for key in ("calibration-sha256","author-plan-sha256","author-admission-sha256","runtime-manifest-sha256","terminal-sha256","wire-sha256",
        "input-gate-sha256","graph-sha256","receipt-sha256","census-manifest-sha256"):parser.add_argument("--"+key)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason="One complete source-bound Saved-BEST all-line census replay or narrow interface calibration; setup/closure/records/serialization share one deadline;20save;no producer run or retry")
    out=args.out.resolve();io.need(out.is_relative_to(ROOT) and not out.exists(),"OUTPUT_PATH");pins={}
    def reserve():io.need(not deadline.status()["stop_required"] and deadline.status()["remaining_seconds"]>20,"DEADLINE_RESERVE")
    def digest_file(path):
        digest=hashlib.sha256()
        with path.open("rb") as stream:
            while raw:=stream.read(1024*1024):reserve();digest.update(raw)
        reserve();return digest.hexdigest()
    def pin(path,identity=None):
        reserve();path=path.resolve();io.need(path.is_relative_to(ROOT) and path.is_file(),"ARTIFACT_PATH")
        name=path.relative_to(ROOT).as_posix();io.relative_file(ROOT,name,ROOT)
        io.need(name!="CLAIMS.yaml" and not name.startswith(".git/"),"IMMUTABLE_INPUT_ROLE")
        value=digest_file(path);io.need(identity is None or type(identity) is str and value==identity,"ARTIFACT_IDENTITY",name)
        io.need(name not in pins or pins[name]==value,"IMMUTABLE_INPUT_CONFLICT",name);pins[name]=value;return path
    try:
        for name,value in {**STATIC,SELF:args.self_sha256,SPEC:args.spec_sha256}.items():pin(ROOT/name,value)
        core.authenticate(ROOT);author_plan=io.strict_json((ROOT/reader.PLAN).read_bytes());software=author_plan["direct_inputs_sha256"]
        io.need(type(software) is dict and len(software)==22,"SOFTWARE_POPULATION")
        kernel_software={p:h for p,h in software.items() if p not in (reader.CALLER,reader.CALLER_SPEC,reader.SUP,reader.SUP_SPEC)}
        for name,value in software.items():pin(ROOT/name,value)
        out.mkdir(parents=True)
        if args.mode=="calibration":result=calibration(out,reserve,software,kernel_software,pin);status=CAL_PASS
        else:
            io.need(args.calibration is not None,"CALIBRATION_IDENTITY");source_inputs=pins.copy()
            cal=io.strict_json(pin(args.calibration,args.calibration_sha256).read_bytes())
            io.need(cal.get("status")==CAL_PASS and cal.get("verifier")=="/root/structural" and cal.get("actual_target_input_read") is False
                and cal.get("producer_outputs_checked") is True and cal.get("producer_runtime_admission_checked") is True
                and cal.get("producer_census_records_checked") is False and cal.get("actual_graph_matrix_read") is False
                and io.integer(cal.get("positive_controls")) and cal["positive_controls"]==6
                and io.integer(cal.get("synthetic_positive_controls")) and cal["synthetic_positive_controls"]==5
                and io.integer(cal.get("genuine_positive_profile_controls")) and cal["genuine_positive_profile_controls"]==1
                and io.integer(cal.get("genuine_profile_payload_population")) and cal["genuine_profile_payload_population"]==4
                and io.same(cal.get("genuine_profile_original_payloads_sha256"),GENUINE_PROFILE_PINS)
                and cal.get("synthetic_profile_receipt_are_execution_observations") is False
                and io.integer(cal.get("framing_checker_implementation_version")) and cal["framing_checker_implementation_version"]==3
                and io.integer(cal.get("strict_negative_controls")) and cal["strict_negative_controls"]==48
                and all(cal.get("inputs_sha256",{}).get(p)==h for p,h in GENUINE_PROFILE_PINS.items())
                and all(cal.get("inputs_sha256",{}).get(p)==h for p,h in source_inputs.items()),"CALIBRATION_SCOPE")
            for name,value in cal["outputs_sha256"].items():pin(io.relative_file(ROOT,name,args.calibration.parent),value)
            result=actual(out,pins,software,kernel_software,reserve,args,pin);status=PASS
        # Closing immutable rehash is included in this invocation, then guarded serialization.
        for name,value in list(pins.items()):pin(ROOT/name,value)
        outputs={p.relative_to(ROOT).as_posix():digest_file(p) for p in sorted(out.rglob("*")) if p.is_file()};reserve()
        kernel.save(out/"summary.json",dict(status=status,producer="/root/native_driver" if args.mode=="check" else None,verifier="/root/structural",
            method="independent_artifact_check" if args.mode=="check" else "independent_finite_controls",timestamp=datetime.now(timezone.utc).isoformat(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,source_context=args.source_commit,
            inputs_sha256=pins,outputs_sha256=outputs,shared_components=[reader.SELF,kernel.RAW_CORE,core.SHARED],**result,
            scientific_launched=False,target_resolution="NONE",deadline=deadline.status()));reserve()
    except BaseException as error:
        out.mkdir(parents=True,exist_ok=True)
        kernel.save(out/"failure.json",dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),automatic_retry=False,
            provisional_summary_is_approval=False,target_resolution="NONE"));raise


if __name__=="__main__":main()
