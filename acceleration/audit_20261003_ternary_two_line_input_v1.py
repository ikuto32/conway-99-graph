"""SOURCE ONLY: exact graph-only best-object input checking, no census execution.

The calibrated independent caller supplies bounded wire/gate readers only.
Independent full-row geometry, int64 products and Python-set intersections
reconstruct all graph/count entries. Other archived history stays opaque.
"""
import argparse
import copy
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline
import audit_20261003_ternary_two_line_caller_controls_v2 as reader

kernel, core, io, ROOT = reader.kernel, reader.core, reader.io, reader.ROOT
SELF = "acceleration/audit_20261003_ternary_two_line_input_v1.py"
SPEC = "acceleration/audit_20261003_ternary_two_line_input_v1_spec.md"
CAL_PASS = "INDEPENDENT_TERNARY_ALL_LINE_GRAPH_ONLY_INPUT_V1_CALIBRATION_PASS"
INPUT_PASS = reader.INPUT_PASS
CALLER_GATE = "acceleration/results/20261003_independent_review/ternary_two_line_caller_full01/summary.json"
CALLER_GATE_SHA = "15ff807eae8f02096c90b021cb29912c51af1e568a283a8b11dc4961acd85227"
AUTHOR_PLAN = "acceleration/plan_20261003_ternary_warm_graph_input_v1.json"
AUTHOR_PLAN_SHA = "827f561adaa11db4bc6ff65b373fe1ac2ede80ed1ecba18ecec14f98361b256e"
AUTHOR = "acceleration/results/20261003_ternary_warm_graph_input01"
RUNTIME = "acceleration/results/20261003_ternary_warm_graph_input_supervision01"
STATIC = {**reader.STATIC,
    reader.SELF: "b362c1f111eb5ec5b9e325f8f182326544f2929d0212c0262f417b0ca21a5c5e",
    reader.SPEC: "ed109e49f8ba65e46c62b7a44d8e6e4a96ea8b62a8bc089bbdefed10297d936e",
    reader.KERNEL_GATE: reader.KERNEL_GATE_SHA, CALLER_GATE: CALLER_GATE_SHA,
    AUTHOR_PLAN: AUTHOR_PLAN_SHA}
GRAPH_KEYS = set("schema n point_degree ordered_triples metrics source_state_path source_state_sha256 source_matrix_path source_matrix_sha256 source_independent_audit_path source_independent_audit_sha256 source_section historical_native_state_written rng_or_trajectory_imported all_lines_mutable".split())
RECEIPT_KEYS = set("timestamp producer command cwd python tqdm source_reference_commit inputs_sha256 graph_input_sha256 scientific_census_launched graph_only_input historical_native_state_written rng_or_trajectory_imported all_lines_mutable baseline_metrics deadline independent_approval target_resolution overall_search_coverage".split())


def complete_scalar(base):
    neighbors, cn, metrics = kernel.scalar_sets(base.n, base.degree, base.rows)
    adjacency = [[int(v in neighbors[u]) for v in range(base.n)] for u in range(base.n)]
    io.need(io.same(adjacency, base.adjacency.tolist()) and io.same(cn, base.cn.tolist())
        and io.same(metrics, base.metrics), "COMPLETE_SCALAR_COUNTS")
    core.unchanged(base)
    return dict(ordered_adjacency_entries=base.n**2, ordered_common_neighbor_entries=base.n**2,
        unordered_pair_metrics=base.n*(base.n-1)//2, true_product_diagonal=2*base.degree,
        distinct_from_native_zero_diagonal_cache=True)


def expected_payload(base):
    return dict(schema="TERNARY_ALL_LINE_GRAPH_ONLY_INPUT_V1",n=base.n,point_degree=base.degree,
        ordered_triples=[list(row) for row in base.rows], metrics=copy.deepcopy(base.metrics),
        source_state_path=reader.STATE,source_state_sha256=reader.WARM_PINS[reader.STATE],
        source_matrix_path=reader.MATRIX,source_matrix_sha256=reader.WARM_PINS[reader.MATRIX],
        source_independent_audit_path=reader.WARM_AUDIT,source_independent_audit_sha256=reader.WARM_PINS[reader.WARM_AUDIT],
        source_section="ordered best triples only",historical_native_state_written=False,
        rng_or_trajectory_imported=False,all_lines_mutable=True)


def graph_payload(value, base, target=False):
    io.need(type(value) is dict and set(value) == GRAPH_KEYS and io.same(value,expected_payload(base)),"GRAPH_PAYLOAD")
    if target:
        io.need((base.n,base.degree,len(base.rows),base.total) == (99,7,231,239085)
            and value["n"] == 99 and value["point_degree"] == 7, "TARGET_INPUT_DIMENSIONS")
    return complete_scalar(base)


def merge_inputs(*maps):
    result = {}
    for mapping in maps:
        io.need(type(mapping) is dict,"IMMUTABLE_INPUT_MAP")
        for path, identity in mapping.items():
            io.need(type(path) is str and type(identity) is str and len(identity) == 64
                and set(identity) <= set("0123456789abcdef") and path not in ("CLAIMS.yaml",".git/index"),"IMMUTABLE_INPUT_MAP")
            io.relative_file(ROOT,path,ROOT)
            io.need(path not in result or result[path] == identity,"IMMUTABLE_INPUT_CONFLICT")
            result[path] = identity
    return result


def receipt(value, graph_sha, graph, expected_inputs, worker, context):
    io.need(type(value) is dict and set(value) == RECEIPT_KEYS
        and type(value.get("timestamp")) is str and bool(value["timestamp"]),"INPUT_RECEIPT")
    io.need(value.get("producer") == "/root/native_driver" and io.same(value.get("command"),worker)
        and value.get("cwd") == "/mnt/c/Users/ikuto/projects/conway-99-graph"
        and value.get("python") == "3.12.3" and value.get("tqdm") == "4.67.1"
        and value.get("source_reference_commit") == context,"INPUT_RECEIPT")
    io.need(value.get("graph_input_sha256") == graph_sha and io.same(value.get("inputs_sha256"),expected_inputs)
        and io.same(value.get("baseline_metrics"),graph["metrics"])
        and value.get("scientific_census_launched") is False and value.get("graph_only_input") is True
        and value.get("historical_native_state_written") is False and value.get("rng_or_trajectory_imported") is False
        and value.get("all_lines_mutable") is True and value.get("independent_approval") is False
        and value.get("target_resolution") == "NONE"
        and value.get("overall_search_coverage") == "UNKNOWN; no validated denominator."
        and type(value.get("deadline")) is dict,"INPUT_RECEIPT")


def linux_profile(manifest, terminal, plan, admission, software, plan_path, plan_sha, output, context):
    child = ["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python",
        reader.CALLER,"input","--seconds","100","--out",output,"--source-commit",context,
        "--kernel-gate",reader.KERNEL_GATE,"--kernel-gate-sha256",reader.KERNEL_GATE_SHA,
        "--caller-gate",CALLER_GATE,"--caller-gate-sha256",CALLER_GATE_SHA]
    command = plan.get("command")
    io.need(type(command) is list and len(command) == 44 and command.count("--") == 1
        and command[:6] == ["/usr/bin/python3","acceleration/run_compute_command.py","--seconds","120","--shutdown-reserve-seconds","20"]
        and io.same(command[command.index("--")+1:],child) and io.same(manifest.get("command"),child)
        and manifest.get("cwd") == "/mnt/c/Users/ikuto/projects/conway-99-graph"
        and manifest.get("source_sha256") == kernel.STATIC["acceleration/run_compute_command.py"]
        and type(manifest.get("seconds")) in (int,float) and manifest["seconds"] == 120
        and type(manifest.get("shutdown_reserve_seconds")) in (int,float) and manifest["shutdown_reserve_seconds"] == 20,"LINUX_INPUT_PROFILE")
    cleanup = terminal.get("cleanup")
    io.need(type(cleanup) is dict and cleanup.get("reaped") is True and io.integer(cleanup.get("actual_exit_code"))
        and cleanup["actual_exit_code"] == 0 and cleanup.get("cleanup_errors") == []
        and cleanup.get("process_group_live_pids") == [] and cleanup.get("job_active_zero_observed") is True
        and io.integer(terminal.get("command_exit_code")) and terminal["command_exit_code"] == 0
        and type(terminal.get("invocation_id")) is str and terminal["invocation_id"] == manifest.get("invocation_id"),"LINUX_TERMINAL")
    probe = admission.get("default_uid_probe"); admitted_plan = admission.get("plan")
    io.need(admission.get("schema") == "TERNARY_TWO_LINE_CALLER_V1_INPUT_ADMISSION_V1" and type(probe) is dict
        and probe.get("command") == ["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"]
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"] == "1000"
        and io.integer(probe.get("actual_exit_code")) and probe["actual_exit_code"] == 0 and admission.get("admitted") is True
        and admission.get("scientific_launched") is False and admission.get("actual99_read") is True
        and admission.get("scientific_census_launched") is False and type(admission.get("actual99_read_scope")) is str
        and bool(admission["actual99_read_scope"])
        and type(admitted_plan) is dict and admitted_plan.get("path") == plan_path and admitted_plan.get("sha256") == plan_sha
        and io.integer(admitted_plan.get("words")) and admitted_plan["words"] == 44,"UID_INPUT_ADMISSION")
    records = admission.get("source_pins")
    direct = {**software,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA,**reader.WARM_PINS}
    io.need(type(records) is list and len(records) == 26 and io.integer(admission.get("small_source_pin_population"))
        and admission["small_source_pin_population"] == 26
        and all(type(r) is dict and r.get("matched") is True and r.get("expected") == r.get("sha256") for r in records)
        and {r.get("path"):r.get("sha256") for r in records} == direct,"ADMISSION_SOURCE_PINS")
    return ["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",*child[13:]]


def reject(name, stage, call):
    try: call()
    except io.AuditError as error:
        io.need(error.stage == stage,"CONTROL_REJECTION_STAGE",name)
        return dict(case=name,expected_stage=stage,actual_stage=error.stage)
    raise io.AuditError("NEGATIVE_CONTROL_ACCEPTED",name)


def calibration(out, reserve, software):
    positives = []; cases = []
    for name,(n,degree,rows) in kernel.fixtures().items():
        reserve(); raw = (
            "HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2\n"+f"n {n}\ndegree {degree}\ncurrent 0\nbest {len(rows)}\n"
            +"".join(" ".join(map(str,row))+"\n" for row in rows)+"cn 0\nEND\n").encode()
        base = reader.state_graph(raw); graph = expected_payload(base)
        matrix=(str(n)+"\n"+"".join("".join(str(int(v)) for v in row)+"\n" for row in base.adjacency)).encode()
        reader.matrix_graph(matrix,base)
        checked = graph_payload(graph,base); positives.append(dict(fixture=name,**checked))
        kernel.save(out/(name+"_graph.json"),graph)
        for key in ("schema","n","point_degree","ordered_triples","metrics","source_section"):
            bad = copy.deepcopy(graph); bad.pop(key)
            cases.append((name+"_missing_"+key,"GRAPH_PAYLOAD",lambda b=bad,s=base: graph_payload(b,s)))
    rook = kernel.fixtures()["rook9"][2]
    rows99 = [[v+9*block for v in row] for block in range(11) for row in rook]
    synthetic = core.fixed_input(99,2,rows99); graph = expected_payload(synthetic)
    checked = graph_payload(graph,synthetic); positives.append(dict(fixture="constructed99rho2",**checked))
    kernel.save(out/"constructed99rho2_graph.json",graph)
    cases.append(("constructed99_not_degree7","TARGET_INPUT_DIMENSIONS",lambda: graph_payload(graph,synthetic,True)))
    for key in ("historical_native_state_written","rng_or_trajectory_imported","all_lines_mutable"):
        bad = copy.deepcopy(graph); bad[key] = not bad[key]
        cases.append(("graph_"+key,"GRAPH_PAYLOAD",lambda b=bad:graph_payload(b,synthetic)))
    for name,path,value in [("n_bool",["n"],True),("degree_float",["point_degree"],2.0),
        ("triple_bool",["ordered_triples",0,0],False),("F3_bool",["metrics","F3"],True)]:
        bad = copy.deepcopy(graph); node = bad
        for key in path[:-1]: node = node[key]
        node[path[-1]] = value; cases.append((name,"GRAPH_PAYLOAD",lambda b=bad:graph_payload(b,synthetic)))
    seed_inputs = {reader.CALLER:STATIC[reader.CALLER]}; graph_sha="1"*64
    output="acceleration/results/synthetic_input_only"; context="63437c9b9fc2dd58b3bdfb51fc347b880b397503"
    # Synthetic execution metadata, never an observation of a real invocation.
    child=["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python",
        reader.CALLER,"input","--seconds","100","--out",output,"--source-commit",context,
        "--kernel-gate",reader.KERNEL_GATE,"--kernel-gate-sha256",reader.KERNEL_GATE_SHA,"--caller-gate",CALLER_GATE,"--caller-gate-sha256",CALLER_GATE_SHA]
    plan=dict(command=["/usr/bin/python3","acceleration/run_compute_command.py","--seconds","120","--shutdown-reserve-seconds","20",
        "--allocation-reason","synthetic","--success-criterion","synthetic","--verification-criterion","synthetic","--out","synthetic","--",*child])
    manifest=dict(command=child,cwd="/mnt/c/Users/ikuto/projects/conway-99-graph",source_sha256=kernel.STATIC["acceleration/run_compute_command.py"],
        seconds=120.0,shutdown_reserve_seconds=20.0,invocation_id="synthetic_metadata_only")
    terminal=dict(invocation_id=manifest["invocation_id"],command_exit_code=0,cleanup=dict(reaped=True,actual_exit_code=0,
        cleanup_errors=[],process_group_live_pids=[],job_active_zero_observed=True))
    admission=dict(schema="TERNARY_TWO_LINE_CALLER_V1_INPUT_ADMISSION_V1",default_uid_probe=dict(command=["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"],
        stdout_uid="1000",actual_exit_code=0),admitted=True,scientific_launched=False,scientific_census_launched=False,
        actual99_read=True,actual99_read_scope="Synthetic metadata only; no actual warm input read",plan=dict(path="synthetic_plan",sha256="2"*64,words=44),
        small_source_pin_population=26,source_pins=[dict(path=p,sha256=h,expected=h,matched=True) for p,h in
            {**software,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA,**reader.WARM_PINS}.items()])
    worker=linux_profile(manifest,terminal,plan,admission,software,"synthetic_plan","2"*64,output,context)
    value=dict(timestamp="synthetic_metadata_only",producer="/root/native_driver",command=worker,cwd=manifest["cwd"],python="3.12.3",tqdm="4.67.1",
        source_reference_commit=context,inputs_sha256=seed_inputs,graph_input_sha256=graph_sha,scientific_census_launched=False,
        graph_only_input=True,historical_native_state_written=False,rng_or_trajectory_imported=False,all_lines_mutable=True,
        baseline_metrics=graph["metrics"],deadline={},independent_approval=False,target_resolution="NONE",overall_search_coverage="UNKNOWN; no validated denominator.")
    receipt(value,graph_sha,graph,seed_inputs,worker,context); positives.append(dict(fixture="synthetic_input_profile_receipt",observed_execution=False))
    for key,bad_value in [("scientific_census_launched",True),("graph_only_input",1),("historical_native_state_written",True),
        ("rng_or_trajectory_imported",True),("all_lines_mutable",0),("independent_approval",True),("graph_input_sha256","3"*64),("inputs_sha256",{})]:
        bad=copy.deepcopy(value);bad[key]=bad_value
        cases.append(("receipt_"+key,"INPUT_RECEIPT",lambda b=bad:receipt(b,graph_sha,graph,seed_inputs,worker,context)))
    profile_seed=[manifest,terminal,plan,admission]
    for name,index,path,bad_value,stage in [("input_profile_mode",2,["command",29],"controls","LINUX_INPUT_PROFILE"),
        ("input_profile_allocation",0,["seconds"],180,"LINUX_INPUT_PROFILE"),("input_profile_UID_bool",3,["default_uid_probe","stdout_uid"],True,"UID_INPUT_ADMISSION"),
        ("input_profile_actualread_alias",3,["actual99_read"],1,"UID_INPUT_ADMISSION"),("input_profile_word_float",3,["plan","words"],44.0,"UID_INPUT_ADMISSION"),
        ("input_profile_source25",3,["source_pins"],admission["source_pins"][:-1],"ADMISSION_SOURCE_PINS"),
        ("input_profile_group_live",1,["cleanup","process_group_live_pids"],[7],"LINUX_TERMINAL")]:
        bad=copy.deepcopy(profile_seed);node=bad[index]
        for key in path[:-1]:node=node[key]
        node[path[-1]]=bad_value
        cases.append((name,stage,lambda b=bad:linux_profile(*b,software,"synthetic_plan","2"*64,output,context)))
    cases.append(("protected_immutable_map","IMMUTABLE_INPUT_MAP",lambda:merge_inputs({"CLAIMS.yaml":"a"*64})))
    cases.append(("conflicting_immutable_map","IMMUTABLE_INPUT_CONFLICT",lambda:merge_inputs({SELF:"a"*64},{SELF:"b"*64})))
    results=[]
    for name,stage,call in cases:reserve();results.append(reject(name,stage,call))
    io.need(len(positives)==5 and len(results)==43,"DECLARED_INPUT_CALIBRATION_POPULATION")
    kernel.save(out/"negative_controls.json",results)
    return dict(positive_controls=5,strict_negative_controls=43,positive_cases=positives,
        constructed99_scalar_cells=9801,constructed99_point_degree=2,actual_target_input_read=False,producer_outputs_checked=False)


def actual(out,pins,software,reserve,args):
    io.need(args.author_out is not None and args.author_out.resolve()==(ROOT/AUTHOR).resolve()
        and args.supervision is not None and args.supervision.resolve()==(ROOT/RUNTIME).resolve()
        and args.author_plan is not None and args.author_plan.resolve()==(ROOT/AUTHOR_PLAN).resolve()
        and args.author_plan_sha256==AUTHOR_PLAN_SHA and args.author_admission is not None
        and args.author_admission.resolve().is_relative_to(ROOT),"ACTUAL_ARGUMENT_BOUNDARY")
    def pin(path,identity):
        reserve(); resolved=path.resolve();io.need(resolved.is_relative_to(ROOT),"ARTIFACT_PATH")
        name=resolved.relative_to(ROOT).as_posix()
        io.need(type(identity) is str and len(identity)==64 and set(identity)<=set("0123456789abcdef")
            and io.sha(resolved)==identity,"ACTUAL_ARTIFACT_IDENTITY",name)
        io.need(name not in pins or pins[name]==identity,"IMMUTABLE_INPUT_CONFLICT",name);pins[name]=identity
        return resolved
    graph_file=pin(args.author_out/"graph_input.json",args.graph_sha256)
    receipt_file=pin(args.author_out/"run_receipt.json",args.receipt_sha256)
    plan=io.strict_json(pin(args.author_plan,args.author_plan_sha256).read_bytes())
    admission=io.strict_json(pin(args.author_admission,args.author_admission_sha256).read_bytes())
    manifest=io.strict_json(pin(args.supervision/"manifest.json",args.manifest_sha256).read_bytes())
    terminal=io.strict_json(pin(args.supervision/"summary.json",args.terminal_sha256).read_bytes())
    worker=linux_profile(manifest,terminal,plan,admission,software,AUTHOR_PLAN,AUTHOR_PLAN_SHA,AUTHOR,args.source_commit)
    gates=[io.strict_json((ROOT/p).read_bytes()) for p in (reader.KERNEL_GATE,CALLER_GATE)]
    for path,identity in reader.WARM_PINS.items():pin(ROOT/path,identity)
    warm=io.strict_json((ROOT/reader.WARM_AUDIT).read_bytes());reader.check_warm(warm)
    expected_inputs=merge_inputs(software,{reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA},reader.WARM_PINS,
        gates[0]["inputs_sha256"],gates[1]["inputs_sha256"],warm["inputs_sha256"])
    io.need(io.same(plan.get("inputs_sha256"),{**software,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,CALLER_GATE:CALLER_GATE_SHA,**reader.WARM_PINS})
        and io.same(plan.get("full_gate_union"),expected_inputs) and io.integer(plan.get("full_gate_union_pin_count"))
        and plan["full_gate_union_pin_count"]==len(expected_inputs),"SOURCE_BOUND_INPUT_UNION")
    for path,identity in expected_inputs.items():pin(io.relative_file(ROOT,path,ROOT),identity)
    base=reader.state_graph((ROOT/reader.STATE).read_bytes())
    reader.matrix_graph((ROOT/reader.MATRIX).read_bytes(),base)
    graph=io.strict_json(graph_file.read_bytes());checked=graph_payload(graph,base,True)
    io.need(base.metrics["E_lambda"]==0 and base.metrics["E_mu"]==3480,"ORIGINAL_SCOPED_GRAPH_COMPONENTS")
    raw_receipt=io.strict_json(receipt_file.read_bytes())
    receipt(raw_receipt,args.graph_sha256,graph,expected_inputs,worker,args.source_commit)
    target=core.full_integer_target(base.adjacency)
    io.need(target["degree14"] is True and target["is_target"] is False
        and target["identity_mismatches"]==warm["final_best_diagnostics"]["identity_mismatches"],"FULL_INTEGER_GRAPH_IDENTITY")
    kernel.save(out/"complete_graph_counts.json",dict(adjacency=base.adjacency.tolist(),common_neighbors=base.cn.tolist(),
        metrics=base.metrics,full_integer_target=target,**checked))
    statement=("The exact graph-only derivative "+args.graph_sha256+" is the preserved ordered best231 triangle object of state "
        +reader.WARM_PINS[reader.STATE]+", with all99 adjacency rows equal to the preserved matrix "+reader.WARM_PINS[reader.MATRIX]
        +". Independent complete integer reconstruction checks 231 ordered triples, 9801 adjacency and common-neighbor entries and 4851 unordered-pair scores; "
        +"all lines are mutable, the labelled two-line proposal population is239085, and the exact baseline isF3="+str(base.metrics["F3"])
        +", E_lambda="+str(base.metrics["E_lambda"])+", E_mu="+str(base.metrics["E_mu"])+", E="+str(base.metrics["E"])
        +". This finite input verification imports no archived RNG or trajectory and certifies no target SRG or move outcome.")
    scope=dict(description="One exact archived ordered-best graph derivative and complete integer input counts; no neighborhood enumeration or search coverage.",
        unrestricted_target=False,target_resolution="NONE")
    return dict(statement=statement,scope=scope,graph_only_input=True,historical_native_state_written=False,
        rng_or_trajectory_imported=False,all_lines_mutable=True,n=99,point_degree=7,ordered_triples=231,proposal_population=base.total,
        graph_input=graph,metrics=base.metrics,complete_scalar_checks=checked,full_integer_target=target,
        original_graph_identity_map={**reader.WARM_PINS,graph_file.relative_to(ROOT).as_posix():args.graph_sha256},
        complete_producer_immutable_inputs=len(expected_inputs),actual_target_input_read=True,producer_outputs_checked=True,
        producer_cleanup_scope="Original receipt observes a reaped empty insideLinux process group; the independent verifier uses a separate supported Windows Job.",
        scientific_census_launched=False,old_history_verification_claimed=False,new_exclusions=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("mode",choices=["calibration","check"])
    parser.add_argument("--out",type=Path,required=True);parser.add_argument("--seconds",type=float,required=True)
    for name in ("self-sha256","spec-sha256","source-commit"):parser.add_argument("--"+name,required=True)
    for name in ("calibration","author-out","author-plan","author-admission","supervision"):parser.add_argument("--"+name,type=Path)
    for name in ("calibration-sha256","graph-sha256","receipt-sha256","author-plan-sha256","author-admission-sha256","manifest-sha256","terminal-sha256"):parser.add_argument("--"+name)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason="Exact graph-only best231 input/calibration; every hash/scalar/serialization included, no census/retry/history verification")
    out=args.out.resolve();io.need(out.is_relative_to(ROOT) and not out.exists(),"OUTPUT_PATH")
    pins={**STATIC,SELF:args.self_sha256,SPEC:args.spec_sha256}
    for path,value in pins.items():io.need(io.sha(ROOT/path)==value,"SOURCE_IDENTITY",path)
    core.authenticate(ROOT);software=reader.software_order(io.strict_json((ROOT/reader.PLAN).read_bytes())["inputs_sha256"])
    for path,value in software.items():io.need(io.sha(ROOT/path)==value,"SOURCE_IDENTITY",path);pins[path]=value
    for path,identity in [(reader.KERNEL_GATE,reader.KERNEL_GATE_SHA),(CALLER_GATE,CALLER_GATE_SHA)]:
        gate=io.strict_json((ROOT/path).read_bytes());reader.check_gate("KERNEL" if path==reader.KERNEL_GATE else "CALLER",gate,software,
            {p:h for p,h in software.items() if p not in (reader.CALLER,reader.CALLER_SPEC)},None)
    out.mkdir(parents=True)
    def reserve():io.need(deadline.status()["remaining_seconds"]>20 and not deadline.status()["stop_required"],"DEADLINE_RESERVE")
    try:
        if args.mode=="calibration":result=calibration(out,reserve,software);status=CAL_PASS
        else:
            io.need(args.calibration is not None and args.calibration.resolve().is_relative_to(ROOT)
                and type(args.calibration_sha256) is str and io.sha(args.calibration)==args.calibration_sha256,"CALIBRATION_IDENTITY")
            cal=io.strict_json(args.calibration.read_bytes())
            io.need(cal.get("status")==CAL_PASS and cal.get("verifier")=="/root/structural"
                and cal.get("producer_outputs_checked") is False and cal.get("actual_target_input_read") is False
                and io.integer(cal.get("positive_controls")) and cal["positive_controls"]==5
                and io.integer(cal.get("strict_negative_controls")) and cal["strict_negative_controls"]==43
                and all(cal.get("inputs_sha256",{}).get(p)==h for p,h in pins.items()),"CALIBRATION_SCOPE")
            pins[args.calibration.resolve().relative_to(ROOT).as_posix()]=args.calibration_sha256
            for path,identity in cal.get("outputs_sha256",{}).items():
                reserve();io.need(io.sha(io.relative_file(ROOT,path,args.calibration.parent))==identity,"CALIBRATION_OUTPUT_IDENTITY");pins[path]=identity
            result=actual(out,pins,software,reserve,args);status=INPUT_PASS
        outputs={p.relative_to(ROOT).as_posix():io.sha(p) for p in sorted(out.rglob("*")) if p.is_file()}
        kernel.save(out/"summary.json",dict(status=status,producer="/root/native_driver" if args.mode=="check" else None,
            verifier="/root/structural",method="independent_artifact_check" if args.mode=="check" else "independent_finite_controls",
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,
            source_context=args.source_commit,inputs_sha256=pins,outputs_sha256=outputs,shared_components=[reader.SELF,kernel.RAW_CORE,core.SHARED],
            **result,scientific_launched=False,target_resolution="NONE",deadline=deadline.status()))
    except BaseException as error:
        kernel.save(out/"failure.json",dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),automatic_retry=False,target_resolution="NONE"));raise


if __name__=="__main__":main()
