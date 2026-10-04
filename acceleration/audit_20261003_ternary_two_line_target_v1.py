"""SOURCE ONLY: one complete all-line F3/E neighborhood, no search execution.

Reuses the unchanged independent record/full-matrix/part/checkpoint path.
Adds exact complete invocation, input lineage and target zero-object scope.
"""
import argparse
import copy
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline
import audit_20261003_ternary_two_line_input_v1 as input_check

reader,kernel,core,io,ROOT=input_check.reader,input_check.kernel,input_check.core,input_check.io,input_check.ROOT
SELF="acceleration/audit_20261003_ternary_two_line_target_v1.py"
SPEC="acceleration/audit_20261003_ternary_two_line_target_v1_spec.md"
CAL_PASS="INDEPENDENT_TERNARY_ALL_LINE_CENSUS_V1_CALIBRATION_PASS"
PASS="INDEPENDENT_TERNARY_ALL_LINE_CENSUS_V1_COMPLETE_PASS"
AUTHOR="acceleration/results/20261003_ternary_warm_all_line_census01"
RUNTIME="acceleration/results/20261003_ternary_warm_all_line_census_supervision01"
PLAN="acceleration/plan_20261003_ternary_warm_all_line_census_v2.json"
PLAN_SHA="128824b533529622c14704074a095c9b628e9837cf20e2bd3b4dbe639df6f8ec"
PROTOCOL="acceleration/plan_20261003_ternary_warm_all_line_census_v2_spec.md"
INPUT_GRAPH="acceleration/results/20261003_ternary_warm_graph_input01/graph_input.json"
INPUT_GRAPH_SHA="b1d285b6025f8ad2ac589731aaa54839261df560345aabf07b4cc084ddfe1028"
INPUT_GATE="acceleration/results/20261003_independent_review/ternary_graph_only_input_full01/summary.json"
INPUT_GATE_SHA="e6ebb9de67a7c00e89c54c3697556b36bce6b530e59a57fbdec12087b9fe6be0"
STATIC={**input_check.STATIC,input_check.SELF:"3ddda91d568caa8751e2f92336ce094be4d4911928547ebb2303311bba7ba1d2",
    input_check.SPEC:"328e4d53e89c13c69346797b64a79d2df9067b767a60d536f8867140a7229c21",
    PLAN:PLAN_SHA,PROTOCOL:"b173bd333e9604ea07ba5d3ddac753e7f5d3148faff5c942cb9b3233af7ff6bb"}


def whole_boundary(base,directory,manifest,identity,chunk=5000):
    io.need(type(manifest) is dict and io.same(manifest.get("identity"),identity),"WHOLE_IDENTITY")
    io.need(all(io.integer(manifest.get(k)) for k in ("population","completed_proposals","starting_proposal_id","proposals_evaluated_this_invocation"))
        and manifest["population"]==base.total and manifest["completed_proposals"]==base.total
        and manifest["starting_proposal_id"]==0 and manifest["proposals_evaluated_this_invocation"]==base.total,"WHOLE_POPULATION")
    io.need(manifest.get("status")=="CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK" and manifest.get("budget_stop") is False,"WHOLE_COMPLETION")
    parts=manifest.get("parts");checkpoints=manifest.get("checkpoints")
    needed=(base.total+chunk-1)//chunk
    io.need(type(parts) is list and len(parts)==needed and type(checkpoints) is list and len(checkpoints)==max(1,needed),"WHOLE_CHUNKS")
    for at,part in enumerate(parts):
        io.need(type(part) is dict and io.integer(part.get("start")) and io.integer(part.get("end"))
            and part["start"]==at*chunk and part["end"]==min((at+1)*chunk,base.total),"WHOLE_PART_BOUNDARY")
        io.relative_file(ROOT,part.get("path"),directory)
    for checkpoint in checkpoints:
        io.need(type(checkpoint) is dict,"WHOLE_CHECKPOINT_REFERENCE")
        io.relative_file(ROOT,checkpoint.get("path"),directory)


def input_gate(value,graph,software):
    reader.check_gate("INPUT",value,software,{p:h for p,h in software.items() if p not in (reader.CALLER,reader.CALLER_SPEC)},graph)
    io.need(value.get("graph_only_input") is True and value.get("actual_target_input_read") is True
        and value.get("scientific_census_launched") is False
        and type(value.get("statement")) is str and bool(value["statement"]),"INPUT_COMPLETE_SCOPE")


def census_receipt(value,graph_hash,graph,inputs,worker,context):
    io.need(type(value) is dict and set(value)==input_check.RECEIPT_KEYS
        and type(value.get("timestamp")) is str and bool(value["timestamp"])
        and value.get("producer")=="/root/native_driver" and io.same(value.get("command"),worker)
        and value.get("cwd")=="/mnt/c/Users/ikuto/projects/conway-99-graph"
        and value.get("python")=="3.12.3" and value.get("tqdm")=="4.67.1"
        and value.get("source_reference_commit")==context,"CENSUS_RECEIPT")
    io.need(value.get("graph_input_sha256")==graph_hash and io.same(value.get("inputs_sha256"),inputs)
        and io.same(value.get("baseline_metrics"),graph["metrics"])
        and value.get("scientific_census_launched") is True and value.get("graph_only_input") is True
        and value.get("historical_native_state_written") is False and value.get("rng_or_trajectory_imported") is False
        and value.get("all_lines_mutable") is True and value.get("independent_approval") is False
        and value.get("target_resolution")=="NONE" and value.get("overall_search_coverage")=="UNKNOWN; no validated denominator."
        and type(value.get("deadline")) is dict,"CENSUS_RECEIPT")


def target_objects(base,directory,manifest,result,reserve):
    # The shared finite object checker verifies exact files/triples/deduplication.
    # Its generic null target diagnostics are not used for actual99 conclusions.
    objects=kernel.audit_objects(base,directory,manifest,result)
    checked=[]
    for item,ref in zip(objects,manifest["residue_zero_objects"]):
        reserve();rows=io.strict_json(io.relative_file(ROOT,ref["triples_path"],directory).read_bytes())["ordered_triples"]
        fresh=core.fixed_input(base.n,base.degree,rows)
        input_check.complete_scalar(fresh)
        is_target=core.full_integer_target(fresh.adjacency) if (base.n,base.degree)==(99,7) else None
        if (base.n,base.degree)==(99,7): require_target_zero(fresh.adjacency)
        checked.append(dict(proposal_id=item["proposal_id"],matrix_sha256=item["matrix_sha256"],n=base.n,
            full_integer_target=is_target,target_null_reason=None if is_target is not None else "Generic finite fixture is outside99/7 domain.",
            ROOT_review_required=is_target is not None))
    selected=result["selected"]
    selected_checks=None
    if selected is not None:
        fresh=core.fixed_input(base.n,base.degree,kernel.rows_for(base,selected))
        scalar=input_check.complete_scalar(fresh)
        selected_checks=dict(proposal_id=selected["proposal_id"],metrics=fresh.metrics,complete_scalar_checks=scalar,
            full_integer_target=core.full_integer_target(fresh.adjacency) if (base.n,base.degree)==(99,7) else None)
    return checked,selected_checks


def require_target_zero(adjacency):
    target=core.full_integer_target(adjacency)
    io.need(target["degree14"] is True and target["is_target"] is True,"RESIDUE_ZERO_FULL_INTEGER_TARGET")
    return target


def linux_profile(manifest,terminal,plan,admission,software,plan_sha,context):
    child=["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python",
        reader.CALLER,"census","--seconds","550","--out",AUTHOR,"--source-commit",context,
        "--kernel-gate",reader.KERNEL_GATE,"--kernel-gate-sha256",reader.KERNEL_GATE_SHA,
        "--caller-gate",input_check.CALLER_GATE,"--caller-gate-sha256",input_check.CALLER_GATE_SHA,
        "--input-gate",INPUT_GATE,"--input-gate-sha256",INPUT_GATE_SHA]
    command=plan.get("command")
    io.need(type(command) is list and len(command)==48 and command.count("--")==1
        and command[:6]==["/usr/bin/python3","acceleration/run_compute_command.py","--seconds","600","--shutdown-reserve-seconds","20"]
        and io.same(command[command.index("--")+1:],child) and io.same(manifest.get("command"),child)
        and manifest.get("cwd")=="/mnt/c/Users/ikuto/projects/conway-99-graph"
        and manifest.get("source_sha256")==kernel.STATIC["acceleration/run_compute_command.py"]
        and type(manifest.get("seconds")) in (int,float) and manifest["seconds"]==600
        and type(manifest.get("shutdown_reserve_seconds")) in (int,float)
        and manifest["shutdown_reserve_seconds"]==20,"LINUX_CENSUS_PROFILE")
    cleanup=terminal.get("cleanup")
    io.need(type(cleanup) is dict and cleanup.get("reaped") is True and io.integer(cleanup.get("actual_exit_code"))
        and cleanup["actual_exit_code"]==0 and cleanup.get("cleanup_errors")==[]
        and cleanup.get("process_group_live_pids")==[] and cleanup.get("job_active_zero_observed") is True
        and io.integer(terminal.get("command_exit_code")) and terminal["command_exit_code"]==0
        and type(terminal.get("invocation_id")) is str and terminal["invocation_id"]==manifest.get("invocation_id"),"LINUX_TERMINAL")
    probe=admission.get("default_uid_probe"); admitted_plan=admission.get("plan")
    io.need(admission.get("schema")=="TERNARY_TWO_LINE_CALLER_V1_CENSUS_ADMISSION_V1" and type(probe) is dict
        and probe.get("command")==["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"]
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"]=="1000"
        and io.integer(probe.get("actual_exit_code")) and probe["actual_exit_code"]==0
        and admission.get("admitted") is True and admission.get("scientific_launched") is False
        and admission.get("scientific_census_launched") is False and admission.get("actual99_read") is True
        and type(admission.get("actual99_read_scope")) is str and bool(admission["actual99_read_scope"])
        and type(admitted_plan) is dict and admitted_plan.get("path")==PLAN and admitted_plan.get("sha256")==plan_sha
        and io.integer(admitted_plan.get("words")) and admitted_plan["words"]==48,"UID_CENSUS_ADMISSION")
    direct={**software,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,input_check.CALLER_GATE:input_check.CALLER_GATE_SHA,
        INPUT_GATE:INPUT_GATE_SHA,**reader.WARM_PINS,INPUT_GRAPH:INPUT_GRAPH_SHA}
    records=admission.get("source_pins")
    io.need(type(records) is list and len(records)==28 and io.integer(admission.get("small_source_pin_population"))
        and admission["small_source_pin_population"]==28
        and all(type(r) is dict and r.get("matched") is True and r.get("expected")==r.get("sha256") for r in records)
        and {r.get("path"):r.get("sha256") for r in records}==direct,"ADMISSION_SOURCE_PINS")
    return ["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",*child[13:]],direct


def model_identity(graph,inputs,software,context):
    return dict(inputs_sha256=inputs,software=software,objective_version=core.OBJECTIVE,graph_only_input=graph,
        n=99,point_degree=7,total=239085,source_reference_commit=context,
        source_reference_scope="Published context only; changed source/raw gates separately pinned, availability not inferred.",
        all_lines_mutable=True,lambda_zero_filter=False,root_filter=False,historical_native_state_written=False,
        question="Does this exact complete graph have an admissible line swap with smaller exact(F3,E), or exact F3zero?",
        selection_rule="Every valid proposal eligible; minimum(F3,E), then proposalID; no global search claim.")


def calibration(out,reserve,software):
    positives=[];negatives=[];seeds=[]
    for name,n,degree,rows in [("single_triangle",3,1,[[0,1,2]]),("rook9",*kernel.fixtures()["rook9"])]:
        reserve();base=core.fixed_input(n,degree,rows);records=[core.expected_record(base,pid)[0] for pid in range(base.total)]
        marker=dict(synthetic_complete_frame=True,fixture=name)
        directory=out/name;manifest=kernel.emit_synthetic(base,directory,marker,records,base.total)
        whole_boundary(base,directory,manifest,marker,50)
        checked=kernel.audit_run(base,directory,manifest,marker,reserve)
        zero,selected=target_objects(base,directory,manifest,checked,reserve)
        positives.append(dict(fixture=name,complete_labels=base.total,checkpoint_prefixes=len(checked["checkpoints"]),
            zero_objects=len(zero),selected_proposal_id=None if selected is None else selected["proposal_id"]))
        seeds.append((base,directory,manifest,marker))
    base,directory,manifest,marker=seeds[1]
    for name,key,bad_value,stage in [("start_bool","starting_proposal_id",False,"WHOLE_POPULATION"),
        ("start_shift","starting_proposal_id",1,"WHOLE_POPULATION"),("stop_prefix","completed_proposals",134,"WHOLE_POPULATION"),
        ("count_float","proposals_evaluated_this_invocation",135.0,"WHOLE_POPULATION"),("population_bool","population",True,"WHOLE_POPULATION"),
        ("budget_integer","budget_stop",0,"WHOLE_COMPLETION"),("unknown_status","status","UNKNOWN_PREFIX_ONLY","WHOLE_COMPLETION"),
        ("missing_checkpoint","checkpoints",manifest["checkpoints"][:-1],"WHOLE_CHUNKS"),("duplicate_part","parts",manifest["parts"]+manifest["parts"][:1],"WHOLE_CHUNKS")]:
        bad=copy.deepcopy(manifest);bad[key]=bad_value
        negatives.append(kernel_reject(name,stage,lambda b=bad:whole_boundary(base,directory,b,marker,50)))
    bad=copy.deepcopy(manifest);bad["parts"][0]["start"]=False
    negatives.append(kernel_reject("part_start_bool","WHOLE_PART_BOUNDARY",lambda:whole_boundary(base,directory,bad,marker,50)))
    bad_path=copy.deepcopy(manifest);bad_path["parts"][0]["path"]=SELF
    negatives.append(kernel_reject("part_outside_invocation","ARTIFACT_PATH",lambda:whole_boundary(base,directory,bad_path,marker,50)))
    wrong=copy.deepcopy(marker);wrong["fixture"]="other"
    negatives.append(kernel_reject("wrong_input_identity","WHOLE_IDENTITY",lambda:whole_boundary(base,directory,manifest,wrong,50)))
    graph,gates,_=reader.synthetic_gates(software,{p:h for p,h in software.items() if p not in (reader.CALLER,reader.CALLER_SPEC)})
    gate=gates["INPUT_GATE"];gate.update(actual_target_input_read=True,scientific_census_launched=False,
        statement="Synthetic input-interface control only; no graph or execution observation.")
    input_gate(gate,graph,software)
    positives.append(dict(case="synthetic_input_gate",observed_execution=False))
    for label,key,value,stage in [("input_actual_false","actual_target_input_read",False,"INPUT_COMPLETE_SCOPE"),
        ("input_science_true","scientific_census_launched",True,"INPUT_COMPLETE_SCOPE"),
        ("input_statement_null","statement",None,"INPUT_COMPLETE_SCOPE"),
        ("input_history_true","historical_native_state_written",True,"INPUT_GATE"),
        ("input_population_bool","proposal_population",True,"INPUT_GATE")]:
        bad=copy.deepcopy(gate);bad[key]=value
        negatives.append(kernel_reject(label,stage,lambda b=bad:input_gate(b,graph,software)))
    context="63437c9b9fc2dd58b3bdfb51fc347b880b397503";plan_sha="2"*64
    child=["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python",
        reader.CALLER,"census","--seconds","550","--out",AUTHOR,"--source-commit",context,
        "--kernel-gate",reader.KERNEL_GATE,"--kernel-gate-sha256",reader.KERNEL_GATE_SHA,
        "--caller-gate",input_check.CALLER_GATE,"--caller-gate-sha256",input_check.CALLER_GATE_SHA,
        "--input-gate",INPUT_GATE,"--input-gate-sha256",INPUT_GATE_SHA]
    plan=dict(command=["/usr/bin/python3","acceleration/run_compute_command.py","--seconds","600","--shutdown-reserve-seconds","20",
        "--allocation-reason","synthetic","--success-criterion","synthetic","--verification-criterion","synthetic","--out","synthetic","--",*child])
    runtime=dict(command=child,cwd="/mnt/c/Users/ikuto/projects/conway-99-graph",source_sha256=kernel.STATIC["acceleration/run_compute_command.py"],
        seconds=600,shutdown_reserve_seconds=20,invocation_id="synthetic")
    terminal=dict(command_exit_code=0,invocation_id="synthetic",cleanup=dict(reaped=True,actual_exit_code=0,
        cleanup_errors=[],process_group_live_pids=[],job_active_zero_observed=True))
    direct={**software,reader.KERNEL_GATE:reader.KERNEL_GATE_SHA,input_check.CALLER_GATE:input_check.CALLER_GATE_SHA,
        INPUT_GATE:INPUT_GATE_SHA,**reader.WARM_PINS,INPUT_GRAPH:INPUT_GRAPH_SHA}
    admission=dict(schema="TERNARY_TWO_LINE_CALLER_V1_CENSUS_ADMISSION_V1",default_uid_probe=dict(
        command=["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"],stdout_uid="1000",actual_exit_code=0),
        admitted=True,scientific_launched=False,scientific_census_launched=False,actual99_read=True,actual99_read_scope="Synthetic metadata only.",
        plan=dict(path=PLAN,sha256=plan_sha,words=48),small_source_pin_population=28,
        source_pins=[dict(path=p,sha256=h,expected=h,matched=True) for p,h in direct.items()])
    worker,_=linux_profile(runtime,terminal,plan,admission,software,plan_sha,context)
    positives.append(dict(case="synthetic48word_UID28_profile",observed_execution=False))
    for label,which,path,value,stage in [("profile_missing_input_gate","plan",["command"],plan["command"][:-2],"LINUX_CENSUS_PROFILE"),
        ("profile_old120","runtime",["seconds"],120,"LINUX_CENSUS_PROFILE"),
        ("terminal_exit_bool","terminal",["cleanup","actual_exit_code"],False,"LINUX_TERMINAL"),
        ("terminal_live_PID","terminal",["cleanup","process_group_live_pids"],[1],"LINUX_TERMINAL"),
        ("uid_integer1000","admission",["default_uid_probe","stdout_uid"],1000,"UID_CENSUS_ADMISSION"),
        ("plan_words_bool","admission",["plan","words"],True,"UID_CENSUS_ADMISSION"),
        ("predispatch_science_true","admission",["scientific_launched"],True,"UID_CENSUS_ADMISSION"),
        ("missing28th_pin","admission",["source_pins"],admission["source_pins"][:-1],"ADMISSION_SOURCE_PINS")]:
        values=dict(plan=copy.deepcopy(plan),runtime=copy.deepcopy(runtime),terminal=copy.deepcopy(terminal),admission=copy.deepcopy(admission))
        node=values[which]
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        negatives.append(kernel_reject(label,stage,lambda v=values:linux_profile(v["runtime"],v["terminal"],v["plan"],v["admission"],software,plan_sha,context)))
    graph_hash="1"*64;inputs={reader.CALLER:software[reader.CALLER]}
    raw_receipt=dict(timestamp="synthetic",producer="/root/native_driver",command=worker,cwd="/mnt/c/Users/ikuto/projects/conway-99-graph",
        python="3.12.3",tqdm="4.67.1",source_reference_commit=context,inputs_sha256=inputs,graph_input_sha256=graph_hash,
        scientific_census_launched=True,graph_only_input=True,historical_native_state_written=False,rng_or_trajectory_imported=False,
        all_lines_mutable=True,baseline_metrics=graph["metrics"],deadline={},independent_approval=False,target_resolution="NONE",
        overall_search_coverage="UNKNOWN; no validated denominator.")
    census_receipt(raw_receipt,graph_hash,graph,inputs,worker,context)
    positives.append(dict(case="synthetic_census_receipt",observed_execution=False))
    for label,key,value in [("receipt_science_false","scientific_census_launched",False),("receipt_history_true","historical_native_state_written",True),
        ("receipt_RNG_true","rng_or_trajectory_imported",True),("receipt_baseline_wrong","baseline_metrics",{}),
        ("receipt_graph_wrong","graph_input_sha256","0"*64),("receipt_inputs_wrong","inputs_sha256",{}),
        ("receipt_selfapproval_true","independent_approval",True),("receipt_worker_wrong","command",worker[:-1])]:
        bad=copy.deepcopy(raw_receipt);bad[key]=value
        negatives.append(kernel_reject(label,"CENSUS_RECEIPT",lambda b=bad:census_receipt(b,graph_hash,graph,inputs,worker,context)))
    rook_rows=kernel.fixtures()["rook9"][2]
    constructed=core.fixed_input(99,2,[[v+9*block for v in row] for block in range(11) for row in rook_rows])
    negatives.append(kernel_reject("constructed99_rho2_not_target","RESIDUE_ZERO_FULL_INTEGER_TARGET",lambda:require_target_zero(constructed.adjacency)))
    io.need(len(positives)==5 and len(negatives)==34,"CALIBRATION_POPULATION")
    kernel.save(out/"negative_controls.json",negatives)
    return dict(positive_controls=5,strict_negative_controls=34,complete_generic_labels=135,fixtures=positives,
        constructed99_rho2_target_veto_cells=9801,actual_target_input_read=False,producer_outputs_checked=False,
        synthetic_receipt_profile_are_execution_observations=False)


def kernel_reject(name,stage,call):
    return input_check.reject(name,stage,call)


def actual(out,pins,software,reserve,args):
    io.need(args.author_out is not None and args.author_out.resolve()==(ROOT/AUTHOR).resolve()
        and args.supervision is not None and args.supervision.resolve()==(ROOT/RUNTIME).resolve()
        and args.author_plan is not None and args.author_plan.resolve()==(ROOT/PLAN).resolve()
        and args.author_plan_sha256==PLAN_SHA and args.author_admission is not None
        and args.author_admission.resolve().is_relative_to(ROOT),"ACTUAL_ARGUMENT_BOUNDARY")
    def pin(path,identity):
        reserve();resolved=path.resolve();io.need(resolved.is_relative_to(ROOT),"ARTIFACT_PATH")
        name=resolved.relative_to(ROOT).as_posix()
        io.need(type(identity) is str and len(identity)==64 and set(identity)<=set("0123456789abcdef")
            and io.sha(resolved)==identity,"ACTUAL_ARTIFACT_IDENTITY",name)
        io.need(name not in pins or pins[name]==identity,"IMMUTABLE_INPUT_CONFLICT",name)
        pins[name]=identity;return resolved
    plan=io.strict_json(pin(args.author_plan,args.author_plan_sha256).read_bytes())
    admission=io.strict_json(pin(args.author_admission,args.author_admission_sha256).read_bytes())
    runtime=io.strict_json(pin(args.supervision/"manifest.json",args.runtime_manifest_sha256).read_bytes())
    terminal=io.strict_json(pin(args.supervision/"summary.json",args.terminal_sha256).read_bytes())
    worker,direct=linux_profile(runtime,terminal,plan,admission,software,PLAN_SHA,args.source_commit)
    gates=[]
    for path,identity in [(reader.KERNEL_GATE,reader.KERNEL_GATE_SHA),(input_check.CALLER_GATE,input_check.CALLER_GATE_SHA),(INPUT_GATE,INPUT_GATE_SHA)]:
        gates.append(io.strict_json(pin(ROOT/path,identity).read_bytes()))
    raw_graph=io.strict_json(pin(ROOT/INPUT_GRAPH,INPUT_GRAPH_SHA).read_bytes())
    io.need(type(raw_graph) is dict and io.integer(raw_graph.get("n")) and io.integer(raw_graph.get("point_degree")),"GRAPH_PAYLOAD")
    base=core.fixed_input(raw_graph["n"],raw_graph["point_degree"],raw_graph.get("ordered_triples"))
    input_checks=input_check.graph_payload(raw_graph,base,True)
    input_gate(gates[2],raw_graph,software)
    warm=io.strict_json(pin(ROOT/reader.WARM_AUDIT,reader.WARM_PINS[reader.WARM_AUDIT]).read_bytes())
    reader.check_warm(warm)
    expected_inputs=input_check.merge_inputs(direct,*(gate["inputs_sha256"] for gate in gates),warm["inputs_sha256"])
    io.need(io.same(plan.get("inputs_sha256"),direct) and io.same(plan.get("full_gate_union"),expected_inputs)
        and io.integer(plan.get("full_gate_union_pin_count")) and plan["full_gate_union_pin_count"]==len(expected_inputs),"SOURCE_BOUND_CENSUS_UNION")
    for path,identity in expected_inputs.items():pin(io.relative_file(ROOT,path,ROOT),identity)
    graph_file=pin(args.author_out/"graph_input.json",args.graph_sha256)
    new_graph=io.strict_json(graph_file.read_bytes())
    io.need(io.same(new_graph,raw_graph),"ORIGINAL_GRAPH_INPUT_IDENTITY")
    receipt_file=pin(args.author_out/"run_receipt.json",args.receipt_sha256)
    census_receipt(io.strict_json(receipt_file.read_bytes()),args.graph_sha256,new_graph,expected_inputs,worker,args.source_commit)
    manifest_file=pin(args.author_out/"manifest.json",args.census_manifest_sha256)
    manifest=io.strict_json(manifest_file.read_bytes());expected_identity=model_identity(new_graph,expected_inputs,software,args.source_commit)
    whole_boundary(base,args.author_out,manifest,expected_identity)
    original_file_population={path.resolve() for path in args.author_out.rglob("*") if path.is_file()}
    for path in sorted(original_file_population):pin(path,io.sha(path))
    result=kernel.audit_run(base,args.author_out,manifest,expected_identity,reserve)
    zero_checks,selected_checks=target_objects(base,args.author_out,manifest,result,reserve)
    tie_checks=[];seen=set()
    for record in [*result["aggregate"].f3_ties,*result["aggregate"].pair_ties]:
        reserve();pid=record["proposal_id"]
        if pid in seen:continue
        fresh=core.fixed_input(base.n,base.degree,kernel.rows_for(base,record))
        counts=input_check.complete_scalar(fresh)
        io.need(io.same(fresh.metrics,record["new_metrics"]),"TIE_SCALAR_METRICS")
        tie_checks.append(dict(proposal_id=pid,metrics=fresh.metrics,complete_scalar_checks=counts));seen.add(pid)
    snapshot=result["aggregate"].snapshot();baseline_target=core.full_integer_target(base.adjacency)
    io.need(base.total==239085 and len(result["records"])==base.total and len(result["checkpoints"])==48,"COMPLETE_TARGET_POPULATION")
    kernel.save(out/"complete_outcome.json",dict(aggregate=snapshot,baseline_metrics=base.metrics,
        baseline_full_integer_target=baseline_target,complete_input_scalar_checks=input_checks,
        complete_tie_scalar_checks=tie_checks,selected_neighbor=selected_checks,residue_zero_objects=zero_checks))
    io.need({path.resolve() for path in args.author_out.rglob("*") if path.is_file()}==original_file_population,"ORIGINAL_OUTPUT_POPULATION_STABLE")
    for directory in (args.author_out,args.supervision):
        for path in sorted(directory.rglob("*")):
            if path.is_file():reserve();pin(path,io.sha(path))
    statement=("For the exact ordered231-triangle graph-only input "+INPUT_GRAPH_SHA
        +", a separate complete integer replay checks every one of the239085 labelled unordered-line-pair/position proposals, "
        +"all24 fields per record, all48 fixed5000-record parts and checkpoints (lastpart4085), all exact minimumF3 and minimum(F3,E) ties, "
        +"the literal selected graph and every deduplicated zero-residue export. The baseline isF3="+str(base.metrics["F3"])+", E="+str(base.metrics["E"])
        +"; exact classifications are"+str(snapshot["counts"])+", tuple directions are"+str(snapshot["tuple_directions"])
        +", and the minimum neighbour(F3,E) is"+str(snapshot["minimum_pair"])+" with selected proposal"
        +str(None if result["selected"] is None else result["selected"]["proposal_id"])+". There are"+str(len(zero_checks))
        +" zero-residue graph exports, each independently checked against the full99 integer SRG identity. "
        +"This is one finite complete one-move family, with no fixed-root or lambda-zero filter, no global search or target nonexistence conclusion and no imported RNG/trajectory.")
    scope=dict(description="One exact complete239085-label allmutable two-line F3/E neighborhood of the bound ordered231-triangle input; finite one-move conclusions only.",
        unrestricted_target=False,target_resolution="NONE")
    return dict(statement=statement,scope=scope,question=expected_identity["question"],selection_rule=expected_identity["selection_rule"],
        original_input_identity_map={INPUT_GRAPH:INPUT_GRAPH_SHA,INPUT_GATE:INPUT_GATE_SHA,**reader.WARM_PINS},
        actual_original_output_identities={graph_file.relative_to(ROOT).as_posix():args.graph_sha256,
            receipt_file.relative_to(ROOT).as_posix():args.receipt_sha256,manifest_file.relative_to(ROOT).as_posix():args.census_manifest_sha256},
        software=software,complete_producer_immutable_inputs=len(expected_inputs),complete_labelled_proposals=base.total,
        complete_raw_record_fields=24,complete_parts=len(manifest["parts"]),complete_checkpoints=len(result["checkpoints"]),
        chunk_size=5000,last_part_records=4085,aggregate=snapshot,complete_input_scalar_checks=input_checks,
        distinct_ties_fully_scalar_checked=len(tie_checks),selected_neighbor=selected_checks,residue_zero_objects=zero_checks,
        residue_zero_graphs=len(zero_checks),ROOT_review_required_zero_objects=len(zero_checks),
        all_lines_mutable=True,lambda_zero_filter=False,root_filter=False,actual_target_input_read=True,producer_outputs_checked=True,
        producer_scientific_census_launched=True,full_neighborhood_zero_absence=(len(zero_checks)==0),new_exclusions=0,
        historical_native_state_written=False,rng_or_trajectory_imported=False,overall_search_coverage="UNKNOWN; no validated denominator.",
        cleanup_scope="Original producer receipt is an observed empty insideLinux group; verifier separately uses supported WindowsJob.")


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("mode",choices=["calibration","check"])
    parser.add_argument("--out",type=Path,required=True);parser.add_argument("--seconds",type=float,required=True)
    for name in ("self-sha256","spec-sha256","source-commit"):parser.add_argument("--"+name,required=True)
    for name in ("calibration","author-out","author-plan","author-admission","supervision"):parser.add_argument("--"+name,type=Path)
    for name in ("calibration-sha256","author-plan-sha256","author-admission-sha256","graph-sha256","receipt-sha256",
        "census-manifest-sha256","runtime-manifest-sha256","terminal-sha256"):parser.add_argument("--"+name)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason="One complete bound F3/E raw neighborhood check or narrow interface calibration; all setup/closure/record/serialization included, no producer/science launch/retry")
    out=args.out.resolve();io.need(out.is_relative_to(ROOT) and not out.exists(),"OUTPUT_PATH")
    pins={**STATIC,SELF:args.self_sha256,SPEC:args.spec_sha256}
    for path,value in pins.items():io.need(io.sha(ROOT/path)==value,"SOURCE_IDENTITY",path)
    core.authenticate(ROOT);software=reader.software_order(io.strict_json((ROOT/reader.PLAN).read_bytes())["inputs_sha256"])
    for path,value in software.items():io.need(io.sha(ROOT/path)==value,"SOURCE_IDENTITY",path);pins[path]=value
    out.mkdir(parents=True)
    def reserve():io.need(deadline.status()["remaining_seconds"]>20 and not deadline.status()["stop_required"],"DEADLINE_RESERVE")
    try:
        if args.mode=="calibration":result=calibration(out,reserve,software);status=CAL_PASS
        else:
            io.need(args.calibration is not None and args.calibration.resolve().is_relative_to(ROOT)
                and type(args.calibration_sha256) is str and io.sha(args.calibration)==args.calibration_sha256,"CALIBRATION_IDENTITY")
            cal=io.strict_json(args.calibration.read_bytes())
            io.need(cal.get("status")==CAL_PASS and cal.get("verifier")=="/root/structural"
                and cal.get("actual_target_input_read") is False and cal.get("producer_outputs_checked") is False
                and io.integer(cal.get("positive_controls")) and cal["positive_controls"]==5
                and io.integer(cal.get("strict_negative_controls")) and cal["strict_negative_controls"]==34
                and all(cal.get("inputs_sha256",{}).get(p)==h for p,h in pins.items()),"CALIBRATION_SCOPE")
            pins[args.calibration.resolve().relative_to(ROOT).as_posix()]=args.calibration_sha256
            for path,value in cal.get("outputs_sha256",{}).items():
                reserve();io.need(io.sha(io.relative_file(ROOT,path,args.calibration.parent))==value,"CALIBRATION_OUTPUT_IDENTITY");pins[path]=value
            result=actual(out,pins,software,reserve,args);status=PASS
        outputs={p.relative_to(ROOT).as_posix():io.sha(p) for p in sorted(out.rglob("*")) if p.is_file()}
        kernel.save(out/"summary.json",dict(status=status,producer="/root/native_driver" if args.mode=="check" else None,
            verifier="/root/structural",method="independent_artifact_check" if args.mode=="check" else "independent_finite_controls",
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,
            source_context=args.source_commit,inputs_sha256=pins,outputs_sha256=outputs,shared_components=[reader.SELF,kernel.RAW_CORE,core.SHARED],
            **result,scientific_launched=False,target_resolution="NONE",deadline=deadline.status()))
    except BaseException as error:
        kernel.save(out/"failure.json",dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),automatic_retry=False,target_resolution="NONE"));raise


if __name__=="__main__":main()
