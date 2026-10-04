"""SOURCE ONLY V3: closing summary guard; preserved V1/V2 unexecuted.

Only independent 86e0/13783/98efe checking code is imported. No Native parser,
topology, reference scorer or caller is imported. Actual99 and census modes
are absent; the retained construction rows need not be every graph triangle.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline
import audit_20261003_ternary_two_line_controls_v1 as kernel

core, io, ROOT = kernel.core, kernel.io, kernel.ROOT
SELF = "acceleration/audit_20261003_ternary_saved_best_caller_controls_v3.py"
SPEC = "acceleration/audit_20261003_ternary_saved_best_caller_controls_v3_spec.md"
CALLER = "acceleration/census_20261003_ternary_saved_best_caller_v2.py"
CALLER_SPEC = "acceleration/census_20261003_ternary_saved_best_caller_v2_spec.md"
SUP = "acceleration/run_compute_command_v2.py"
SUP_SPEC = "acceleration/run_compute_command_v2_spec.md"
PLAN = "acceleration/plan_20261003_ternary_saved_best_caller_author_controls_v3.json"
PLAN_SHA = "259d3e03e3dbd0794de02b1f7df8f605ed8fe03c756349776dfcbce39031f9c4"
AUTHOR = "acceleration/results/20261003_ternary_saved_best_caller_controls02"
RUNTIME = "acceleration/results/20261003_ternary_saved_best_caller_controls_supervision02"
KERNEL_GATE = "acceleration/results/20261003_independent_review/ternary_two_line_kernel_full01/summary.json"
KERNEL_GATE_SHA = "77cf4c7d8ea79310a98be6628fbefd3d31a2615ff764811f2f2a172fa26b6544"
KERNEL_PASS = "INDEPENDENT_TERNARY_TWO_LINE_KERNEL_V1_COMPLETE_CONTROLS_PASS"
CALLER_PASS = "INDEPENDENT_TERNARY_SAVED_BEST_TWO_LINE_CALLER_V1_COMPLETE_CONTROLS_PASS"
INPUT_PASS = "INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS"
CAL_PASS = "INDEPENDENT_TERNARY_SAVED_BEST_CALLER_V3_CHECKER_CALIBRATION_PASS"
SOURCE_COMMIT = "d0c0dd7db0d3de420b1d718b59122b069df01107"
LINUX_ROOT = "/mnt/c/Users/ikuto/projects/conway-99-graph"
STATIC = {
 "acceleration/audit_20261003_ternary_two_line_controls_v1.py": "86e0b526d1202660284cb4a3639f4d89c2ea9bd38f7c9613f26a7790a57800d6",
 "acceleration/audit_20261003_ternary_two_line_controls_v1_spec.md": "55f20a5cc0136bd1b4ad09f5d83232d43667b4d1210fafe28d779c16bee70e45",
 kernel.RAW_CORE: "13783be56e50db81c4b474741129a2f6ae4e05dc25960d1551cbf70892d4292f",
 kernel.RAW_SPEC: "c38393a70d4edece969cd60fc6d508cc87b8279f9014fa1d072ac8be26565a54",
 core.SHARED: core.SHARED_SHA,
 "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
 "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
 "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
 PLAN: PLAN_SHA,
}


def reject(name, stage, call):
    try:
        call()
    except io.AuditError as error:
        io.need(error.stage == stage, "CONTROL_STAGE", name+":"+error.stage)
        return dict(case=name, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error))
    raise io.AuditError("CONTROL_ACCEPTED", name)


def natural(token, stage):
    io.need(type(token) is str and token.isascii() and token.isdecimal()
        and str(int(token)) == token, stage)
    return int(token)


def wire(raw):
    io.need(type(raw) is bytes and len(raw) <= 131072 and raw.endswith(b"\n")
        and b"\r" not in raw and b"\0" not in raw and raw.isascii(), "WIRE_BYTES")
    lines = raw[:-1].decode("ascii").split("\n")
    io.need(len(lines) >= 7 and lines[0] == "TERNARY_LINEAR_GRAPH_INPUT_V1" and lines[-1] == "END", "WIRE_SCHEMA")
    fields = []
    for index, name in ((1,"n"),(2,"degree"),(3,"source_graph_sha256"),(4,"triples")):
        words = lines[index].split(" ")
        io.need(len(words) == 2 and words[0] == name, "WIRE_FIELDS")
        fields.append(words[1])
    n, degree, count = (natural(fields[index], "WIRE_FIELDS") for index in (0,1,3))
    source = fields[2]
    io.need(len(source) == 64 and all(c in "0123456789abcdef" for c in source), "WIRE_FIELDS")
    io.need(3 <= n <= 99 and 0 < 2*degree < n and 3*count == n*degree, "WIRE_DIMENSIONS")
    io.need(len(lines) == count+6, "WIRE_POPULATION")
    rows = []
    for line in lines[5:-1]:
        words = line.split(" "); io.need(len(words) == 3, "WIRE_ROWS")
        rows.append([natural(word, "WIRE_ROWS") for word in words])
    # Independent full incidence/pair occupancy, with no Native domain call.
    io.need(all(len(set(row)) == 3 and all(0 <= point < n for point in row) for row in rows), "DOMAIN")
    incidences = Counter(point for row in rows for point in row)
    pairs = Counter(tuple(sorted(pair)) for row in rows for pair in combinations(row,2))
    io.need(all(incidences[point] == degree for point in range(n)) and all(value == 1 for value in pairs.values()), "DOMAIN")
    base = core.fixed_input(n, degree, rows)
    matrix = io.matrix_bytes(base.adjacency)
    io.need(hashlib.sha256(matrix).hexdigest() == source, "WIRE_MATRIX")
    neighbors = kernel.literal_sets(n, degree, rows)
    actual_triangles = [list(triple) for triple in combinations(range(n),3)
        if all(v in neighbors[u] for u,v in combinations(triple,2))]
    io.need(all(sorted(row) in actual_triangles for row in rows), "RETAINED_TRIANGLE_VALIDITY")
    return base, source, actual_triangles


def wire_bytes(base):
    source = hashlib.sha256(io.matrix_bytes(base.adjacency)).hexdigest()
    return ("TERNARY_LINEAR_GRAPH_INPUT_V1\n"+f"n {base.n}\ndegree {base.degree}\nsource_graph_sha256 {source}\ntriples {len(base.rows)}\n"
        + "".join(" ".join(map(str,row))+"\n" for row in base.rows)+"END\n").encode("ascii")


def header(gate, status, verifier, stage):
    io.need(type(gate) is dict and gate.get("status") == status and gate.get("producer") == "/root/native_driver"
        and gate.get("verifier") == verifier and gate.get("method") == "independent_artifact_check"
        and gate.get("target_resolution") == "NONE" and type(gate.get("inputs_sha256")) is dict, stage)


def finite_gate(kind, gate, software, kernel_software):
    caller = kind == "CALLER_GATE"; stage = kind
    expected = software if caller else kernel_software
    header(gate, CALLER_PASS if caller else KERNEL_PASS, "/root/structural", stage)
    counts = dict(unique_fixture_labels=51 if caller else 522, strict_author_negative_cases=144 if caller else 160,
        whole_prefix_resume_equalities=3)
    io.need(all(io.integer(gate.get(key)) and gate[key] == value for key,value in counts.items())
        and gate.get("actual_target_input_read") is False
        and all(gate["inputs_sha256"].get(path) == value for path,value in expected.items()), stage)


def input_gate(gate, base, wire_name, wire_sha, source_sha, prerequisite):
    stage = "INPUT_GATE"; header(gate, INPUT_PASS, "/root/checkpoint_audit", stage)
    io.need(io.integer(gate.get("input_implementation_version")) and gate["input_implementation_version"] == 2
        and gate.get("source_kind") == "final.best"
        and all(gate.get(key) is False for key in ("native_state_written","history_rng_counters_imported",
            "retained_construction_triples_are_all_graph_triangles_claimed")), stage)
    counts = dict(n=base.n,point_degree=base.degree,ordered_triples=len(base.rows),complete_integer_matrix_products=base.n**2)
    io.need(all(io.integer(gate.get(key)) and gate[key] == value for key,value in counts.items()), stage)
    io.need(gate.get("graph_input_path") == wire_name and gate.get("graph_input_sha256") == wire_sha
        and gate.get("source_graph_sha256") == source_sha and io.same(gate.get("metrics"),base.metrics)
        and all(gate["inputs_sha256"].get(path) == value for path,value in {**prerequisite,wire_name:wire_sha}.items()), stage)


def synthetic_gates(software, kernel_software):
    n,degree,rows = kernel.fixtures()["rook9"]; base = core.fixed_input(n,degree,rows)
    source = hashlib.sha256(io.matrix_bytes(base.adjacency)).hexdigest()
    result = {}
    for kind, expected, count, negatives in (("KERNEL_GATE",kernel_software,522,160),("CALLER_GATE",software,51,144)):
        result[kind] = dict(status=KERNEL_PASS if kind == "KERNEL_GATE" else CALLER_PASS,producer="/root/native_driver",
            verifier="/root/structural",method="independent_artifact_check",target_resolution="NONE",inputs_sha256=expected.copy(),
            actual_target_input_read=False,unique_fixture_labels=count,strict_author_negative_cases=negatives,whole_prefix_resume_equalities=3)
    prerequisite = {"build/synthetic-state.fragment":"2"*64,"build/synthetic-matrix.adj":source,"build/synthetic-report.json":"3"*64}
    result["INPUT_GATE"] = dict(status=INPUT_PASS,producer="/root/native_driver",verifier="/root/checkpoint_audit",
        method="independent_artifact_check",target_resolution="NONE",input_implementation_version=2,source_kind="final.best",
        native_state_written=False,history_rng_counters_imported=False,retained_construction_triples_are_all_graph_triangles_claimed=False,
        n=9,point_degree=2,ordered_triples=6,complete_integer_matrix_products=81,
        graph_input_path="build/synthetic-geometry.wire",graph_input_sha256="1"*64,source_graph_sha256=source,
        metrics=copy.deepcopy(base.metrics),inputs_sha256={**prerequisite,"build/synthetic-geometry.wire":"1"*64})
    return base, result, prerequisite


def metadata_check(kind, gate, software, kernel_software):
    if kind != "INPUT_GATE": return finite_gate(kind,gate,software,kernel_software)
    base, _, prerequisite = synthetic_gates(software,kernel_software)
    input_gate(gate,base,"build/synthetic-geometry.wire","1"*64,
        hashlib.sha256(io.matrix_bytes(base.adjacency)).hexdigest(),prerequisite)


def wire_cases(name, base, raw):
    lines = raw.decode("ascii").splitlines(); source = lines[3].split(" ")[1]
    duplicate = lines[:2]+[lines[1]]+lines[2:]; short = lines[:5]+lines[6:]
    floats = lines[:]; floats[5] = floats[5].replace(" ",".0 ",1)
    repeated = lines[:]; row = repeated[5].split(" "); row[1] = row[0]; repeated[5] = " ".join(row)
    def encoded(value): return ("\n".join(value)+"\n").encode("ascii")
    return [(name+"_"+case,stage,value) for case,stage,value in [
        ("no_lf","WIRE_BYTES",raw[:-1]),("crlf","WIRE_BYTES",raw.replace(b"\n",b"\r\n")),
        ("nonascii","WIRE_BYTES",raw+b"\xff"),("magic","WIRE_SCHEMA",raw.replace(b"TERNARY_LINEAR_GRAPH_INPUT_V1",b"OTHER_INPUT")),
        ("float_n","WIRE_FIELDS",raw.replace(f"n {base.n}\n".encode(),f"n {base.n}.0\n".encode())),
        ("duplicate_header","WIRE_FIELDS",encoded(duplicate)),("bad_hash","WIRE_FIELDS",raw.replace(source.encode(),b"X"*64)),
        ("wrong_count","WIRE_DIMENSIONS",raw.replace(f"triples {len(base.rows)}\n".encode(),f"triples {len(base.rows)+1}\n".encode())),
        ("short_rows","WIRE_POPULATION",encoded(short)),("float_row","WIRE_ROWS",encoded(floats)),
        ("repeated_point","DOMAIN",encoded(repeated)),("different_hash","WIRE_MATRIX",raw.replace(source.encode(),b"0"*64))]]


def metadata_cases(software, kernel_software):
    _, gates, _ = synthetic_gates(software,kernel_software); cases = []
    def add(name, kind, key, value):
        bad = copy.deepcopy(gates[kind]); bad[key] = value; cases.append((name,kind,bad))
    for kind,expected in (("KERNEL_GATE",kernel_software),("CALLER_GATE",software)):
        for key in ("status","producer","verifier","method","target_resolution"): add(kind+"_"+key,kind,key,"wrong")
        for at,key in enumerate(expected):
            bad = copy.deepcopy(gates[kind]); bad["inputs_sha256"].pop(key); cases.append((kind+"_missing_pin_"+str(at),kind,bad))
        add(kind+"_target_read",kind,"actual_target_input_read",True)
        for key in ("unique_fixture_labels","strict_author_negative_cases","whole_prefix_resume_equalities"):
            original = gates[kind][key]
            for label,value in (("wrong",original+1),("bool",True),("float",float(original))): add(kind+"_"+key+"_"+label,kind,key,value)
    kind = "INPUT_GATE"; gate = gates[kind]
    for key in ("status","producer","verifier","method","target_resolution"): add(kind+"_"+key,kind,key,"wrong")
    for label,value in (("wrong",3),("bool",True),("float",2.0)): add(kind+"_version_"+label,kind,"input_implementation_version",value)
    add(kind+"_source_kind",kind,"source_kind","census_selected")
    for key in ("native_state_written","history_rng_counters_imported","retained_construction_triples_are_all_graph_triangles_claimed"):
        add(kind+"_"+key,kind,key,True)
    for key in ("n","point_degree","ordered_triples","complete_integer_matrix_products"):
        for label,value in (("wrong",gate[key]+1),("bool",True),("float",float(gate[key]))): add(kind+"_"+key+"_"+label,kind,key,value)
    for key in ("graph_input_path","graph_input_sha256","source_graph_sha256"): add(kind+"_"+key,kind,key,"wrong")
    for key in gate["metrics"]:
        bad = copy.deepcopy(gate); bad["metrics"][key] = [True,0,0] if key == "residue_population" else float(gate["metrics"][key])
        cases.append((kind+"_metric_"+key,kind,bad))
    for at,key in enumerate(gate["inputs_sha256"]):
        bad = copy.deepcopy(gate); bad["inputs_sha256"].pop(key); cases.append((kind+"_missing_pin_"+str(at),kind,bad))
    io.need(len(cases) == 108,"METADATA_CONTROL_POPULATION")
    return cases


def emit_fixture(base, directory, identity, records, stop, prefix=None):
    """Independent hand-crafted protocol fixture with the declared ten chunk.

    Reuses independent raw IO and aggregate definitions, not Native enumeration.
    """
    directory.mkdir(); start = 0 if prefix is None else prefix["completed_proposals"]
    aggregate = core.Aggregate(); parts = [] if prefix is None else copy.deepcopy(prefix["parts"]); cps = []
    for record in records[:start]: aggregate.add(record)
    at = start
    while at < stop:
        end = min(at+10,stop); parts.append(kernel.emit_part(directory,at,records[at:end]))
        for record in records[at:end]: aggregate.add(record)
        at = end; path = directory/f"checkpoint_{at:09d}.json"
        kernel.save(path,dict(schema=core.CHECKPOINT_SCHEMA,identity=identity,next_proposal_id=at,parts=parts,aggregate=aggregate.snapshot()))
        cps.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=io.sha(path)))
    selected = min(aggregate.pair_ties,key=lambda row:row["proposal_id"]) if aggregate.pair_ties else None
    for filename,tied,scope in (("minimum_F3_ties.json",aggregate.f3_ties,"All labelled minimumF3 ties in this saved prefix."),
        ("minimum_pair_ties.json",aggregate.pair_ties,"All labelled minimum(F3,E) ties in this saved prefix.")):
        kernel.save(directory/filename,dict(records=tied,scope=scope))
    if selected is not None:
        _,adj,_ = core.expected_record(base,selected["proposal_id"])
        (directory/"selected_neighbor.adj").write_bytes(io.matrix_bytes(adj))
        kernel.save(directory/"selected_neighbor_triples.json",dict(n=base.n,point_degree=base.degree,
            ordered_triples=kernel.rows_for(base,selected),proposal_id=selected["proposal_id"],objective_version=core.OBJECTIVE,historical_native_state_written=False))
    matrices = {}
    if base.metrics["F3"] == 0:
        raw = io.matrix_bytes(base.adjacency); matrices[hashlib.sha256(raw).hexdigest()] = (None,raw,[list(row) for row in base.rows])
    for record in aggregate.zero_records:
        _,adj,_ = core.expected_record(base,record["proposal_id"]); raw = io.matrix_bytes(adj); key = hashlib.sha256(raw).hexdigest()
        if key not in matrices: matrices[key] = (record["proposal_id"],raw,kernel.rows_for(base,record))
    refs = []
    if matrices:
        zero_dir = directory/"residue_zero_objects"; zero_dir.mkdir()
        for index,(key,(pid,raw,rows)) in enumerate(sorted(matrices.items())):
            ap = zero_dir/f"object_{index:06d}.adj"; rp = zero_dir/f"object_{index:06d}.triples.json"; ap.write_bytes(raw)
            kernel.save(rp,dict(n=base.n,point_degree=base.degree,ordered_triples=rows,proposal_id=pid))
            refs.append(dict(adjacency_path=ap.relative_to(ROOT).as_posix(),adjacency_sha256=key,
                triples_path=rp.relative_to(ROOT).as_posix(),triples_sha256=io.sha(rp),proposal_id=pid,
                target99_domain=False,independent_full_SRG_validation_pending=True))
    value = dict(schema=kernel.MANIFEST_SCHEMA,identity=identity,objective_version=core.OBJECTIVE,population=base.total,
        completed_proposals=stop,starting_proposal_id=start,proposals_evaluated_this_invocation=stop-start,parts=parts,
        checkpoints=cps,aggregate=aggregate.snapshot(),baseline_metrics=base.metrics,status="UNKNOWN_PREFIX_ONLY",budget_stop=False,
        selection_rule="Every valid proposal eligible; minimize exact(F3,E), then proposalID.",
        selected_proposal_id=None if selected is None else selected["proposal_id"],residue_zero_objects=refs,
        producer="/root/native_driver",independent_approval=False,target_resolution="NONE",historical_native_state_written=False,limitations=kernel.LIMITATIONS)
    kernel.save(directory/"manifest.json",value); return value


def replay_fixture(root, name, n, degree, rows, software, reserve, synthetic=False):
    reference = core.fixed_input(n,degree,rows)
    raw = wire_bytes(reference) if synthetic else (root/(name+".wire")).read_bytes()
    base, source, triangles = wire(raw)
    io.need(io.same(base.rows,rows) and io.same(base.metrics,kernel.scalar_sets(n,degree,rows)[2]),"FIXTURE_GEOMETRY")
    identity = dict(synthetic_fixture=name,software=software,objective_version=core.OBJECTIVE)
    records = [core.expected_record(base,pid)[0] for pid in range(17)] if synthetic else None
    runs = {}; visits = cps = zeros = scalar_valid = 0
    for suffix,start,stop in (("whole17",0,17),("prefix7",0,7),("resumed17",7,17)):
        reserve(); directory = root/(name+"_"+suffix)
        manifest = emit_fixture(base,directory,identity,records,stop,
            prefix=None if suffix != "resumed17" else runs["prefix7"][0]) if synthetic else io.strict_json((directory/"manifest.json").read_bytes())
        kernel.named_boundary(manifest,start,stop)
        expected_intervals = {"whole17":[(0,10),(10,17)],"prefix7":[(0,7)],"resumed17":[(0,7),(7,17)]}[suffix]
        io.need(type(manifest.get("parts")) is list and [(part.get("start"),part.get("end")) for part in manifest["parts"]] == expected_intervals,
            "FINITE_PART_GEOMETRY")
        result = kernel.audit_run(base,directory,manifest,identity,reserve)
        zero = kernel.audit_objects(base,directory,manifest,result)
        visits += len(result["records"]); cps += len(result["checkpoints"]); zeros += len(zero)
        if suffix == "whole17":
            for record in result["records"]:
                reserve(); _,adj,cn = core.expected_record(base,record["proposal_id"])
                if record["valid"]: kernel.scalar_check(base,record["proposal_id"],record,adj,cn); scalar_valid += 1
        runs[suffix] = (manifest,result)
    whole,prefix,resumed = (runs[key] for key in ("whole17","prefix7","resumed17"))
    io.need(io.same(whole[1]["records"],resumed[1]["records"]) and io.same(whole[0]["aggregate"],resumed[0]["aggregate"])
        and io.same(prefix[0]["parts"],resumed[0]["parts"][:len(prefix[0]["parts"])]),"PREFIX_ORIGINAL_IDENTITY")
    io.need(visits == 41,"FIXTURE_RECORD_VISITS")
    if name == "prism9": io.need(base.metrics["E_lambda"] > 0,"POSITIVE_LAMBDA_FIXTURE")
    return base,raw,runs,dict(distinct_prefix_labels=17,evaluated_calls=34,prefix_resume_equal=True,metrics=base.metrics,
        source_graph_sha256=source,actual_graph_triangles=len(triangles),retained_construction_rows=len(rows),
        retained_construction_triples_are_all_graph_triangles_claimed=False,raw_record_visits=visits,
        checkpoint_prefixes=cps,zero_object_checks=zeros,valid_scalar_crosschecks=scalar_valid)


def profile(author, manifest, terminal, admission, plan, software):
    command = plan.get("command"); child = plan.get("child_command"); worker = plan.get("worker_command")
    expected_child = ["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3",
        "python","-B",CALLER,"controls","--seconds","100","--out",AUTHOR,"--supervision-out",RUNTIME,"--source-commit",SOURCE_COMMIT]
    io.need(type(command) is list and len(command) == 39 and command.count("--") == 1
        and command[:6] == ["/usr/bin/python3",SUP,"--seconds","120","--shutdown-reserve-seconds","20"]
        and io.same(command[command.index("--")+1:],expected_child) and io.same(child,expected_child)
        and io.same(worker,expected_child[12:]) and io.same(manifest.get("command"),child)
        and manifest.get("cwd") == LINUX_ROOT and manifest.get("source_sha256") == software[SUP]
        and type(manifest.get("seconds")) in (int,float) and type(manifest.get("shutdown_reserve_seconds")) in (int,float)
        and manifest["seconds"] == 120 and manifest["shutdown_reserve_seconds"] == 20
        and manifest.get("runtime_scope") == "LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2"
        and manifest.get("automatic_retry") is False and manifest.get("cumulative_across_commands") is False,"LINUX_COMMAND_PROFILE")
    # Python -B is an interpreter option and is absent from sys.argv.
    interpreter = LINUX_ROOT+"/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3"
    io.need(io.same(author.get("command"),[interpreter,*worker[2:]]) and author.get("cwd") == LINUX_ROOT,"LINUX_CHILD_BINDING")
    cleanup = terminal.get("cleanup"); observations = cleanup.get("cleanup_observations") if type(cleanup) is dict else None
    io.need(type(cleanup) is dict and cleanup.get("reaped") is True and cleanup.get("job_active_zero_observed") is True
        and io.integer(cleanup.get("actual_exit_code")) and cleanup["actual_exit_code"] == 0
        and cleanup.get("cleanup_errors") == [] and cleanup.get("process_group_live_pids") == []
        and io.integer(cleanup.get("cleanup_observation_count")) and type(observations) is list and len(observations) >= 1
        and cleanup["cleanup_observation_count"] == len(observations) and type(observations[-1]) is dict
        and observations[-1].get("live_pids") == [] and observations[-1].get("unreadable_pids") == []
        and io.integer(terminal.get("command_exit_code")) and terminal["command_exit_code"] == 0
        and terminal.get("stop_reason") == "COMMAND_EXITED" and terminal.get("deadline_reached") is False
        and terminal.get("hard_limit_observed") is True and terminal.get("invocation_id") == manifest.get("invocation_id"),"LINUX_TERMINAL")
    probe = admission.get("default_uid_probe"); admitted_plan = admission.get("plan")
    io.need(admission.get("schema") == "TERNARY_SAVED_BEST_TWO_LINE_CALLER_AUTHOR_CONTROLS_ADMISSION_V1"
        and type(probe) is dict and probe.get("command") == ["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"]
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"] == "1000"
        and io.integer(probe.get("exit")) and probe["exit"] == 0
        and admission.get("admitted") is True and admission.get("scientific_launched") is False
        and admission.get("actual_target_input_read") is False and admission.get("automatic_retry") is False
        and admission.get("paths_absent") is True and io.integer(admission.get("native_calls")) and admission["native_calls"] == 0
        and type(admitted_plan) is dict
        and admitted_plan.get("path") == PLAN and admitted_plan.get("sha256") == PLAN_SHA
        and io.integer(admitted_plan.get("words")) and admitted_plan["words"] == 39,"UID_ADMISSION")
    records = admission.get("source_pins")
    io.need(type(records) is dict and len(records) == 22 and io.same(records,software)
        and admission.get("source_pins_all_match") is True,"ADMISSION_SOURCE_PINS")


def profile_seed(software):
    plan = io.strict_json((ROOT/PLAN).read_bytes()); child = plan["child_command"]; worker = plan["worker_command"]
    author = dict(command=[LINUX_ROOT+"/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",*worker[2:]],cwd=LINUX_ROOT)
    manifest = dict(command=child,cwd=LINUX_ROOT,source_sha256=software[SUP],seconds=120.0,shutdown_reserve_seconds=20.0,
        runtime_scope="LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2",automatic_retry=False,cumulative_across_commands=False,invocation_id="synthetic_profile_only")
    terminal = dict(invocation_id=manifest["invocation_id"],command_exit_code=0,stop_reason="COMMAND_EXITED",deadline_reached=False,
        hard_limit_observed=True,cleanup=dict(reaped=True,job_active_zero_observed=True,actual_exit_code=0,cleanup_errors=[],
            process_group_live_pids=[],cleanup_observation_count=1,cleanup_observations=[dict(live_pids=[],unreadable_pids=[])]))
    admission = dict(schema="TERNARY_SAVED_BEST_TWO_LINE_CALLER_AUTHOR_CONTROLS_ADMISSION_V1",default_uid_probe=dict(
        command=["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"],stdout_uid="1000",exit=0),
        admitted=True,scientific_launched=False,actual_target_input_read=False,automatic_retry=False,paths_absent=True,native_calls=0,
        plan=dict(path=PLAN,sha256=PLAN_SHA,words=39),source_pins=software.copy(),source_pins_all_match=True)
    return plan,dict(synthetic_metadata_only=True,author=author,manifest=manifest,terminal=terminal,admission=admission)


def profile_cases(seed):
    cases = []
    def add(name, stage, group, key, value):
        bad = copy.deepcopy(seed); bad[group][key] = value; cases.append((name,stage,bad))
    add("profile_old_supervisor","LINUX_COMMAND_PROFILE","manifest","source_sha256","0"*64)
    add("profile_old_runtime_scope","LINUX_COMMAND_PROFILE","manifest","runtime_scope","LOCAL_LINUX_GROUP_V1")
    bad = copy.deepcopy(seed); bad["manifest"]["command"].remove("-B"); cases.append(("profile_missing_B","LINUX_COMMAND_PROFILE",bad))
    add("profile_outer_allocation","LINUX_COMMAND_PROFILE","manifest","seconds",121.0)
    add("profile_worker_command","LINUX_CHILD_BINDING","author","command",[])
    for name,key,value in (("live_group","process_group_live_pids",[7]),("bool_exit","actual_exit_code",False),
        ("missing_observations","cleanup_observations",[]),):
        bad = copy.deepcopy(seed); bad["terminal"]["cleanup"][key] = value; cases.append(("profile_"+name,"LINUX_TERMINAL",bad))
    bad = copy.deepcopy(seed); bad["terminal"]["cleanup"]["cleanup_observations"][-1]["unreadable_pids"] = [7]
    cases.append(("profile_unreadable_group","LINUX_TERMINAL",bad))
    bad = copy.deepcopy(seed); bad["admission"]["default_uid_probe"]["stdout_uid"] = 1000; cases.append(("profile_int_UID","UID_ADMISSION",bad))
    bad = copy.deepcopy(seed); bad["admission"]["plan"]["words"] = 39.0; cases.append(("profile_float_words","UID_ADMISSION",bad))
    bad = copy.deepcopy(seed); bad["admission"]["source_pins"].pop(next(iter(bad["admission"]["source_pins"]))); cases.append(("profile_21sources","ADMISSION_SOURCE_PINS",bad))
    add("profile_int_matched","ADMISSION_SOURCE_PINS","admission","source_pins_all_match",1)
    add("profile_actual99","UID_ADMISSION","admission","actual_target_input_read",True)
    add("profile_admission_family","UID_ADMISSION","admission","schema","OLD_ADMISSION")
    bad = copy.deepcopy(seed); bad["admission"]["plan"]["sha256"] = "0"*64; cases.append(("profile_plan_hash","UID_ADMISSION",bad))
    io.need(len(cases) == 16,"PROFILE_CONTROL_POPULATION"); return cases


def calibration(out, software, kernel_software, reserve):
    negatives = []; fixtures = {}
    for name,(n,degree,rows) in kernel.fixtures().items():
        reserve(); base,raw,runs,result = replay_fixture(out,name,n,degree,rows,software,reserve,synthetic=True)
        fixtures[name] = result; (out/(name+".wire")).write_bytes(raw)
        for case,stage,bad in wire_cases(name,base,raw):
            reserve(); (out/(case+".wire")).write_bytes(bad); negatives.append(reject(case,stage,lambda value=bad: wire(value)))
    _, gates, _ = synthetic_gates(software,kernel_software)
    for kind,gate in gates.items(): metadata_check(kind,gate,software,kernel_software); kernel.save(out/(kind+"_synthetic_positive.json"),gate)
    for case,stage,bad in metadata_cases(software,kernel_software):
        reserve(); kernel.save(out/(case+".json"),bad); negatives.append(reject(case,stage,lambda s=stage,value=bad: metadata_check(s,value,software,kernel_software)))
    io.need(len(negatives) == 144,"COUNTERPART_CONTROL_POPULATION")
    plan,seed = profile_seed(software); profile(seed["author"],seed["manifest"],seed["terminal"],seed["admission"],plan,software)
    kernel.save(out/"synthetic_profile_positive.json",seed)
    for case,stage,bad in profile_cases(seed):
        reserve(); kernel.save(out/(case+".json"),bad)
        negatives.append(reject(case,stage,lambda value=bad: profile(value["author"],value["manifest"],value["terminal"],value["admission"],plan,software)))
    for suffix,start,stop in (("whole17",0,17),("prefix7",0,7),("resumed17",7,17)):
        bad = copy.deepcopy(runs[suffix][0]); bad["starting_proposal_id"] = start+1
        case = "named_boundary_"+suffix; kernel.save(out/(case+".json"),bad)
        negatives.append(reject(case,"NAMED_RUN_BOUNDARY",lambda value=bad,a=start,b=stop: kernel.named_boundary(value,a,b)))
    for case,raw in (("json_duplicate",b'{"n":1,"n":2}'),("json_nonfinite",b'{"n":NaN}')):
        (out/(case+".json")).write_bytes(raw); negatives.append(reject(case,"JSON",lambda value=raw: io.strict_json(value)))
    io.need(len(negatives) == 165,"DECLARED_CONTROL_POPULATION"); kernel.save(out/"negative_controls.json",negatives)
    return dict(producer_outputs_checked=False,actual_target_input_read=False,positive_controls=7,strict_negative_controls=165,
        native_counterpart_cases=144,changed_profile_negative_controls=16,unique_fixture_labels=51,evaluated_fixture_calls=102,
        all_raw_record_visits=123,whole_prefix_resume_equalities=3,fixtures=fixtures)


def actual(out, pins, software, kernel_software, reserve, args):
    io.need(type(args.author_admission) is str and args.author_admission ==
        "acceleration/results/20261003_ternary_saved_best_caller_controls_admission02.json","AUTHOR_ADMISSION_PATH")
    raw_paths = []
    for directory in (ROOT/AUTHOR,ROOT/RUNTIME):
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                reserve(); relative = path.relative_to(ROOT).as_posix(); raw_paths.append(relative); pins[relative] = io.sha(path)
    fixed = {AUTHOR+"/summary.json":args.author_summary_sha256,RUNTIME+"/manifest.json":args.author_runtime_sha256,
        RUNTIME+"/summary.json":args.author_terminal_sha256,args.author_admission:args.author_admission_sha256,KERNEL_GATE:KERNEL_GATE_SHA}
    for path,value in fixed.items():
        reserve(); io.need(type(value) is str and len(value) == 64 and io.sha(io.relative_file(ROOT,path,ROOT)) == value,"AUTHOR_INPUT_IDENTITY",path); pins[path] = value
    root = ROOT/AUTHOR; author = io.strict_json((root/"summary.json").read_bytes())
    manifest = io.strict_json((ROOT/RUNTIME/"manifest.json").read_bytes()); terminal = io.strict_json((ROOT/RUNTIME/"summary.json").read_bytes())
    admission = io.strict_json((ROOT/args.author_admission).read_bytes()); plan = io.strict_json((ROOT/PLAN).read_bytes())
    profile(author,manifest,terminal,admission,plan,software)
    genuine = io.strict_json((ROOT/KERNEL_GATE).read_bytes()); finite_gate("KERNEL_GATE",genuine,software,kernel_software)
    for key in ("inputs_sha256","outputs_sha256"):
        for path,value in genuine.get(key,{}).items():
            reserve(); io.need(path not in ("CLAIMS.yaml",".git/index") and io.sha(io.relative_file(ROOT,path,ROOT)) == value,"KERNEL_GATE_CLOSURE",path); pins[path] = value
    io.need(author.get("status") == "AUTHOR_TERNARY_SAVED_BEST_TWO_LINE_CALLER_V2_CONTROLS_PENDING_INDEPENDENT_GATE"
        and author.get("producer") == "/root/native_driver" and io.same(author.get("software"),software)
        and io.same(author.get("kernel_software"),kernel_software) and author.get("source_reference_commit") == SOURCE_COMMIT
        and all(author.get(key) is False for key in ("actual_target_input_read","scientific_census_launched","historical_native_state_written",
            "rng_or_trajectory_imported","independent_approval")) and io.integer(author.get("native_calls")) and author["native_calls"] == 0
        and author.get("target_resolution") == "NONE","AUTHOR_SCOPE")
    negatives = []; results = {}
    for name,(n,degree,rows) in kernel.fixtures().items():
        base,raw,_,result = replay_fixture(root,name,n,degree,rows,software,reserve); results[name] = result
        reported = dict(distinct_prefix_labels=17,evaluated_calls=34,prefix_resume_equal=True,metrics=base.metrics,source_graph_sha256=result["source_graph_sha256"])
        io.need(io.same(author.get("fixture_counts",{}).get(name),reported),"AUTHOR_FIXTURE_COUNTS")
        for case,stage,bad in wire_cases(name,base,raw):
            reserve(); saved = (root/(case+".wire")).read_bytes(); io.need(saved == bad,"SAVED_CONTROL_CONTENT",case)
            negatives.append(reject(case,stage,lambda value=saved: wire(value)))
    _, gates, _ = synthetic_gates(software,kernel_software)
    for kind,gate in gates.items():
        value = io.strict_json((root/(kind+"_synthetic_positive.json")).read_bytes()); io.need(io.same(value,gate),"SAVED_POSITIVE_CONTENT",kind)
        metadata_check(kind,value,software,kernel_software)
    for case,stage,bad in metadata_cases(software,kernel_software):
        reserve(); value = io.strict_json((root/(case+".json")).read_bytes()); io.need(io.same(value,bad),"SAVED_CONTROL_CONTENT",case)
        negatives.append(reject(case,stage,lambda s=stage,v=value: metadata_check(s,v,software,kernel_software)))
    expected_counts = dict(unique_fixture_labels=51,evaluated_fixture_calls=102,whole_prefix_resume_equalities=3,strict_author_negative_cases=144,synthetic_gate_positives=3)
    io.need(all(io.integer(author.get(key)) and author[key] == value for key,value in expected_counts.items())
        and io.same(author.get("negative_group_counts"),dict(WIRE=36,KERNEL_GATE=33,CALLER_GATE=37,INPUT_GATE=38))
        and type(author.get("strict_negatives")) is list and len(author["strict_negatives"]) == 144,"AUTHOR_CONTROL_POPULATION")
    for actual_row,reported in zip(negatives,author["strict_negatives"]):
        io.need(type(reported) is dict and all(reported.get(key) == actual_row[key] for key in ("case","expected_stage","actual_stage")),"AUTHOR_CONTROL_STAGE")
    closing_paths = []
    for directory in (root,ROOT/RUNTIME):
        for path in sorted(directory.rglob("*")):
            if path.is_file(): closing_paths.append(path.relative_to(ROOT).as_posix())
    io.need(closing_paths == raw_paths,"AUTHOR_DIRECTORY_IMMUTABILITY")
    kernel.save(out/"author_negative_replay.json",negatives)
    return dict(unique_fixture_labels=51,evaluated_fixture_calls=102,all_raw_record_visits=123,strict_author_negative_cases=144,
        whole_prefix_resume_equalities=3,complete_wire_fixture_roundtrips=3,synthetic_gate_positives=3,
        complete_checkpoint_prefixes=sum(value["checkpoint_prefixes"] for value in results.values()),
        complete_zero_object_checks=sum(value["zero_object_checks"] for value in results.values()),fixtures=results,
        actual_target_input_read=False,scientific_census_launched=False,historical_native_state_written=False,
        retained_construction_triples_are_all_graph_triangles_claimed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("mode",choices=("calibration","check"))
    parser.add_argument("--out",type=Path,required=True); parser.add_argument("--seconds",type=float,required=True)
    for name in ("self-sha256","spec-sha256","source-commit"): parser.add_argument("--"+name,required=True)
    parser.add_argument("--calibration",type=Path); parser.add_argument("--calibration-sha256")
    for name in ("author-summary-sha256","author-runtime-sha256","author-terminal-sha256","author-admission","author-admission-sha256"):
        parser.add_argument("--"+name)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason="New Saved-BEST caller finite51-label/144-case artifact boundary only; all setup/hash/records/preservation inclusive;20save;no actual99/native/retry")
    def reserve(): io.need(not deadline.status()["stop_required"] and deadline.status()["remaining_seconds"] > 20,"DEADLINE_RESERVE")
    out = args.out.resolve(); io.need(out.is_relative_to(ROOT) and not out.exists(),"OUTPUT_PATH")
    pins = {**STATIC,SELF:args.self_sha256,SPEC:args.spec_sha256}
    for path,value in pins.items(): reserve(); io.need(io.sha(ROOT/path) == value,"SOURCE_IDENTITY",path)
    core.authenticate(ROOT); plan = io.strict_json((ROOT/PLAN).read_bytes()); software = plan.get("direct_inputs_sha256")
    io.need(type(software) is dict and len(software) == 22 and software.get(CALLER) == "f6a01af349aa2c8acb3d50a4c11c14cf0266d34e735af70e35ff70429dc04c89"
        and software.get(CALLER_SPEC) == "c04f61d477001d25d81a2f25b16e7a500a545c84808140f9c5234f4f4acb1f59","SOFTWARE_POPULATION")
    kernel_software = {path:value for path,value in software.items() if path not in (CALLER,CALLER_SPEC,SUP,SUP_SPEC)}
    io.need(len(kernel_software) == 18,"KERNEL_SOFTWARE_POPULATION")
    for path,value in software.items(): reserve(); io.need(io.sha(ROOT/path) == value,"SOURCE_IDENTITY",path); pins[path] = value
    out.mkdir(parents=True)
    try:
        if args.mode == "calibration": result = calibration(out,software,kernel_software,reserve); status = CAL_PASS
        else:
            io.need(args.calibration is not None and args.calibration.resolve().is_relative_to(ROOT)
                and type(args.calibration_sha256) is str and io.sha(args.calibration) == args.calibration_sha256,"CALIBRATION_IDENTITY")
            cal = io.strict_json(args.calibration.read_bytes())
            io.need(cal.get("status") == CAL_PASS and cal.get("verifier") == "/root/structural" and cal.get("producer_outputs_checked") is False
                and cal.get("actual_target_input_read") is False and io.integer(cal.get("strict_negative_controls")) and cal["strict_negative_controls"] == 165
                and all(cal.get("inputs_sha256",{}).get(path) == value for path,value in pins.items()),"CALIBRATION_SCOPE")
            pins[args.calibration.resolve().relative_to(ROOT).as_posix()] = args.calibration_sha256
            for path,value in cal.get("outputs_sha256",{}).items():
                reserve(); io.need(io.sha(io.relative_file(ROOT,path,args.calibration.parent)) == value,"CALIBRATION_OUTPUT_IDENTITY"); pins[path] = value
            result = actual(out,pins,software,kernel_software,reserve,args); status = CALLER_PASS
        for path,value in pins.items(): reserve(); io.need(io.sha(io.relative_file(ROOT,path,ROOT)) == value,"CLOSING_INPUT_IDENTITY",path)
        outputs = {}
        for path in sorted(out.rglob("*")):
            if path.is_file(): reserve(); outputs[path.relative_to(ROOT).as_posix()] = io.sha(path)
        reserve(); kernel.save(out/"summary.json",dict(status=status,producer="/root/native_driver" if args.mode == "check" else None,
            verifier="/root/structural",method="independent_artifact_check" if args.mode == "check" else "independent_finite_controls",
            timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,
            source_context=args.source_commit,inputs_sha256=pins,outputs_sha256=outputs,
            shared_components=["acceleration/audit_20261003_ternary_two_line_controls_v1.py",kernel.RAW_CORE,core.SHARED],
            observed_producer_containment="Supported Linux original process group; legacy job flag is not a Windows Job" if args.mode == "check" else None,
            **result,target_resolution="NONE",scientific_launched=False,deadline=deadline.status()))
        reserve()
    except BaseException as error:
        kernel.save(out/"failure.json",dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),
            preserved_partial_outputs=True,automatic_retry=False,target_resolution="NONE")); raise


if __name__ == "__main__": main()
