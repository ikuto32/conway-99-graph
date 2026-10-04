"""SOURCE ONLY: independent finite/raw F3 two-line kernel artifact checking.

No producer, author reference, topology or incremental scorer imports.
The ROOT-authored full-row core supplies exact matrix calculations; the
separate Python-set path below calibrates every finite literal label.
Actual99 and scientific modes are deliberately absent.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline
import audit_20261003_ternary_two_line_raw_core_v1 as core

io = core.io
ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/audit_20261003_ternary_two_line_controls_v1.py"
SPEC = "acceleration/audit_20261003_ternary_two_line_controls_v1_spec.md"
RAW_CORE = "acceleration/audit_20261003_ternary_two_line_raw_core_v1.py"
RAW_SPEC = "acceleration/audit_20261003_ternary_two_line_raw_core_v1_spec.md"
AUTHOR_PLAN = "acceleration/plan_20261003_ternary_two_line_author_controls_v1.json"
AUTHOR_PLAN_SHA = "dc530a24738d97d19526fa89d6bd7bc159585533a11d9a941424afc66e346e75"
AUTHOR_ROOT = "acceleration/results/20261003_ternary_two_line_v1_controls01"
AUTHOR_SUMMARY_SHA = "2b1fde47bd19039e737ff3386e3cb8580df71ee6f67df24281bbc49ffa8fe871"
AUTHOR_RUNTIME = "acceleration/results/20261003_ternary_two_line_v1_controls_supervision01"
AUTHOR_RUNTIME_SHA = "046feab9188077cd2315e1391fd16632e0a94712a366c40f559d9700d500c473"
AUTHOR_TERMINAL_SHA = "2243ee5f77270ce08e8626965a6bca9225bd73390100edf928c6d8a27a6b1187"
AUTHOR_ADMISSION = "acceleration/results/20261003_ternary_two_line_v1_controls_admission01.json"
AUTHOR_ADMISSION_SHA = "8b0bf15617161f7f72669902dbeed588f2c07c784e5db2580d658508e69b4d33"
STATIC = {
 RAW_CORE: "13783be56e50db81c4b474741129a2f6ae4e05dc25960d1551cbf70892d4292f",
 RAW_SPEC: "c38393a70d4edece969cd60fc6d508cc87b8279f9014fa1d072ac8be26565a54",
 core.SHARED: core.SHARED_SHA,
 "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
 "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
 "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
 "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
 AUTHOR_PLAN: AUTHOR_PLAN_SHA,
}
MANIFEST_SCHEMA = "TERNARY_TWO_LINE_CENSUS_MANIFEST_V1"
MANIFEST_KEYS = set("schema identity objective_version population completed_proposals starting_proposal_id proposals_evaluated_this_invocation parts checkpoints aggregate baseline_metrics status budget_stop selection_rule selected_proposal_id residue_zero_objects producer independent_approval target_resolution historical_native_state_written limitations".split())
LIMITATIONS = [
 "One exact graph/all labelled two-line proposals only; no graph-space, ergodicity or target exclusion.",
 "No frozen root, lambda0 acceptance or stochastic search exists in this kernel.",
 "Generic fixture residue zero is not a target99 certificate; any actual99 zero needs independent fullintegerSRG validation.",
]


def save(path, value):
    with path.open("x", encoding="utf8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write("\n")


def fixtures():
    # Literal generic controls; neither target graphs nor imported fixtures.
    return {
      "rook9": (9, 2, [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]),
      "prism9": (9, 2, [[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]),
      "cube12": (12, 2, [[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]),
    }


def literal_sets(n, degree, rows):
    io.need(io.integer(n) and io.integer(degree) and 3 <= n <= 99 and 0 < 2*degree < n,
            "SET_DOMAIN")
    io.need(type(rows) in (list, tuple) and len(rows)*3 == n*degree
        and all(type(row) in (list, tuple) and len(row) == 3 and all(io.integer(v) and 0 <= v < n for v in row)
                and len(set(row)) == 3 for row in rows), "SET_ROWS")
    point_counts = Counter(v for row in rows for v in row)
    io.need(all(point_counts[v] == degree for v in range(n)), "SET_DEGREE")
    occupied = Counter(tuple(sorted(pair)) for row in rows for pair in combinations(row, 2))
    io.need(all(value == 1 for value in occupied.values()), "SET_LINEARITY")
    adjacent = [set() for _ in range(n)]
    for u, v in occupied:
        adjacent[u].add(v); adjacent[v].add(u)
    io.need(all(len(row) == 2*degree for row in adjacent), "SET_GRAPH_DEGREE")
    return adjacent


def scalar_sets(n, degree, rows):
    adjacent = literal_sets(n, degree, rows)
    cn = [[len(adjacent[u] & adjacent[v]) for v in range(n)] for u in range(n)]
    el = em = 0; hist = [0, 0, 0]
    for u, v in combinations(range(n), 2):
        edge = int(v in adjacent[u]); residual = cn[u][v] + edge - 2
        hist[residual % 3] += 1
        if edge: el += residual*residual
        else: em += residual*residual
    f3 = hist[1]+hist[2]
    weight = 819820 if (n, degree) == (99, 7) else n*(n-1)//2*(2*degree)**2+1
    return adjacent, cn, dict(F3=f3, E_lambda=el, E_mu=em, E=el+em,
        scalar_weight=weight, scalar=weight*f3+el+em, residue_population=hist)


def set_swap(base, pid):
    """Separate literal-set replacement, with no core topology invocation."""
    pairs = list(combinations(range(len(base.rows)), 2)); i, j = pairs[pid//9]
    ix, jy = divmod(pid % 9, 3)
    before, second = base.rows[i], base.rows[j]; x, y = before[ix], second[jy]
    if x in second or y in before:
        return "invalid_selection", None
    rows = [list(row) for row in base.rows]; rows[i][ix], rows[j][jy] = y, x
    pairs_after = [tuple(sorted(pair)) for row in rows for pair in combinations(row, 2)]
    if len(set(pairs_after)) != len(pairs_after):
        return "invalid_linearity", None
    return "valid", rows


def scalar_check(base, pid, record, adjacency, cn):
    status, rows = set_swap(base, pid)
    io.need(record["valid"] is (status == "valid"), "SCALAR_SWAP_VALIDITY")
    if status != "valid":
        io.need(record["classification"] == status, "SCALAR_SWAP_VALIDITY")
        return False
    neighbors, set_cn, metrics = scalar_sets(base.n, base.degree, rows)
    io.need(io.same(metrics, record["new_metrics"])
        and io.same(set_cn, cn.tolist())
        and all(int(adjacency[u,v]) == int(v in neighbors[u]) for u in range(base.n) for v in range(base.n)),
        "SCALAR_FULL_SCORE")
    # Every valid labelled swap has the same-position reverse. Verify every
    # literal ordered row returns, not merely an isomorphic point graph.
    restored = [row[:] for row in rows]
    i,j,ix,jy = (record[k] for k in ("i","j","ix","jy"))
    restored[i][ix], restored[j][jy] = restored[j][jy], restored[i][ix]
    io.need(io.same(restored, base.rows), "SCALAR_INVERSE_ROWS")
    inverse_base = core.fixed_input(base.n, base.degree, rows)
    inverse, returned, returned_cn = core.expected_record(inverse_base, pid)
    io.need(inverse["valid"] is True and np.array_equal(returned, base.adjacency)
        and np.array_equal(returned_cn, base.cn), "SCALAR_INVERSE_MATRIX")
    return True


def named_boundary(manifest, start, stop):
    io.need(all(io.integer(manifest.get(k)) for k in ("starting_proposal_id", "completed_proposals", "proposals_evaluated_this_invocation"))
        and manifest["starting_proposal_id"] == start and manifest["completed_proposals"] == stop
        and manifest["proposals_evaluated_this_invocation"] == stop-start, "NAMED_RUN_BOUNDARY")


def audit_run(base, directory, manifest, identity, reserve=lambda: None):
    core.unchanged(base)
    io.need(type(manifest) is dict and set(manifest) == MANIFEST_KEYS and manifest.get("schema") == MANIFEST_SCHEMA,
        "MANIFEST_SCHEMA")
    io.need(io.same(manifest.get("identity"), identity) and manifest.get("objective_version") == core.OBJECTIVE,
        "MANIFEST_IDENTITY")
    io.need(all(io.integer(manifest.get(k)) and 0 <= manifest[k] <= base.total for k in
        ("population", "completed_proposals", "starting_proposal_id", "proposals_evaluated_this_invocation"))
        and manifest["population"] == base.total and manifest["starting_proposal_id"] <= manifest["completed_proposals"]
        and manifest["proposals_evaluated_this_invocation"] == manifest["completed_proposals"]-manifest["starting_proposal_id"],
        "MANIFEST_POPULATION")
    io.need(type(manifest.get("parts")) is list and type(manifest.get("checkpoints")) is list
        and type(manifest.get("budget_stop")) is bool and manifest.get("producer") == "/root/native_driver"
        and manifest.get("independent_approval") is False and manifest.get("historical_native_state_written") is False
        and manifest.get("target_resolution") == "NONE" and manifest.get("selection_rule") ==
        "Every valid proposal eligible; minimize exact(F3,E), then proposalID." and io.same(manifest.get("limitations"), LIMITATIONS),
        "MANIFEST_TYPES")
    io.need(io.same(manifest.get("baseline_metrics"), base.metrics), "MANIFEST_BASELINE")
    aggregate = core.Aggregate(); parts=[]; at=0; snapshots={}; paths=set(); all_records=[]
    # A resumed stream references the original prefix part. Allow only the
    # three named streams under this one fixture's authenticated parent root.
    allowed = directory.parent
    for part in manifest["parts"]:
        reserve(); core.unchanged(base)
        raw = io.part_records(ROOT, allowed, part)
        io.need(part["start"] == at and part["end"] <= manifest["completed_proposals"] and part["path"] not in paths,
            "PART_COVERAGE")
        paths.add(part["path"])
        for record in raw:
            reserve(); expected, _, _ = core.check_record(base, record["proposal_id"], record)
            aggregate.add(expected); all_records.append(expected)
        parts.append(part); at=part["end"]; snapshots[at]=(list(parts),aggregate.snapshot())
        core.unchanged(base)
    io.need(at == manifest["completed_proposals"] and io.same(aggregate.snapshot(), manifest.get("aggregate")),
        "MANIFEST_AGGREGATE")
    if not snapshots: snapshots[0]=([],aggregate.snapshot())
    seen=set(); checked=[]
    for ref in manifest["checkpoints"]:
        reserve()
        io.need(type(ref) is dict and set(ref) == {"path","sha256"} and type(ref["path"]) is str
            and ref["path"] not in seen, "CHECKPOINT_REFERENCE")
        path=io.relative_file(ROOT, ref["path"], directory)
        io.need(io.sha(path) == ref["sha256"], "CHECKPOINT_HASH")
        value=io.strict_json(path.read_bytes())
        io.need(type(value) is dict and io.integer(value.get("next_proposal_id"))
            and value["next_proposal_id"] in snapshots, "CHECKPOINT_COVERAGE")
        end=value["next_proposal_id"]; prefix,snap=snapshots[end]
        core.checkpoint(value,identity,prefix,end,snap); seen.add(ref["path"]); checked.append(end)
    required=[part["end"] for part in parts if part["start"] >= manifest["starting_proposal_id"]]
    io.need(checked == (required or [at]), "CHECKPOINT_COVERAGE")
    complete=at==base.total
    io.need(manifest.get("status") == ("CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK" if complete else "UNKNOWN_PREFIX_ONLY"),
        "MANIFEST_STATUS")
    chosen=min(aggregate.pair_ties,key=lambda record:record["proposal_id"]) if aggregate.pair_ties else None
    io.need(io.same(manifest.get("selected_proposal_id"), None if chosen is None else chosen["proposal_id"]),
        "MANIFEST_SELECTION")
    core.unchanged(base)
    return dict(aggregate=aggregate, records=all_records, checkpoints=checked, selected=chosen)


def rows_for(base, record):
    rows=[list(row) for row in base.rows]
    for key,row in zip(("i","j"),record["new_triples"]): rows[record[key]]=row[:]
    return rows


def audit_objects(base, directory, manifest, result):
    aggregate=result["aggregate"]; selected=result["selected"]
    for filename, tied, scope in [
        ("minimum_F3_ties.json",aggregate.f3_ties,"All labelled minimumF3 ties in this saved prefix."),
        ("minimum_pair_ties.json",aggregate.pair_ties,"All labelled minimum(F3,E) ties in this saved prefix.")]:
        io.need(io.same(io.strict_json((directory/filename).read_bytes()),dict(records=tied,scope=scope)), "TIE_RECORDS")
    if selected is None:
        io.need(not(directory/"selected_neighbor.adj").exists() and not(directory/"selected_neighbor_triples.json").exists(),
            "SELECTED_ABSENCE")
    else:
        _,adj,_=core.expected_record(base,selected["proposal_id"])
        io.need((directory/"selected_neighbor.adj").read_bytes()==io.matrix_bytes(adj),"SELECTED_MATRIX")
        io.need(io.same(io.strict_json((directory/"selected_neighbor_triples.json").read_bytes()),dict(n=base.n,
            point_degree=base.degree,ordered_triples=rows_for(base,selected),proposal_id=selected["proposal_id"],
            objective_version=core.OBJECTIVE,historical_native_state_written=False)),"SELECTED_TRIPLES")
    by_matrix={}
    if base.metrics["F3"] == 0:
        raw=io.matrix_bytes(base.adjacency); by_matrix[hashlib.sha256(raw).hexdigest()]=(None,raw,[list(row) for row in base.rows])
    for record in aggregate.zero_records:
        _,adj,_=core.expected_record(base,record["proposal_id"]); raw=io.matrix_bytes(adj); identity=hashlib.sha256(raw).hexdigest()
        if identity not in by_matrix: by_matrix[identity]=(record["proposal_id"],raw,rows_for(base,record))
    refs=manifest.get("residue_zero_objects"); io.need(type(refs) is list and len(refs)==len(by_matrix),"ZERO_POPULATION")
    expected_files=set(); checked=[]
    for at,(matrix_sha,(pid,raw,rows)) in enumerate(sorted(by_matrix.items())):
        adj_path=directory/"residue_zero_objects"/f"object_{at:06d}.adj"
        rows_path=directory/"residue_zero_objects"/f"object_{at:06d}.triples.json"
        expected_ref=dict(adjacency_path=adj_path.relative_to(ROOT).as_posix(),adjacency_sha256=matrix_sha,
            triples_path=rows_path.relative_to(ROOT).as_posix(),triples_sha256=io.sha(rows_path),proposal_id=pid,
            target99_domain=(base.n,base.degree)==(99,7),independent_full_SRG_validation_pending=True)
        io.need(io.same(refs[at],expected_ref) and adj_path.read_bytes()==raw,"ZERO_OBJECT_IDENTITY")
        io.need(io.same(io.strict_json(rows_path.read_bytes()),dict(n=base.n,point_degree=base.degree,
            ordered_triples=rows,proposal_id=pid)),"ZERO_OBJECT_TRIPLES")
        fresh=core.fixed_input(base.n,base.degree,rows)
        io.need(fresh.metrics["F3"]==0,"ZERO_OBJECT_SCORE")
        checked.append(dict(matrix_sha256=matrix_sha,proposal_id=pid,n=base.n,
            target99_validation=None,target99_validation_null_reason="Finite generic fixture is not target99."))
        expected_files.update((adj_path.name,rows_path.name))
    zero_dir=directory/"residue_zero_objects"
    io.need((zero_dir.is_dir() and {p.name for p in zero_dir.iterdir()}==expected_files) if expected_files else not zero_dir.exists(),
        "ZERO_DIRECTORY_COVERAGE")
    return checked


def emit_part(directory,begin,records):
    raw=b"".join(io.canonical(r) for r in records); path=directory/f"part_{begin:09d}.jsonl.gz"
    with path.open("xb") as stream:
        with gzip.GzipFile(filename="",fileobj=stream,mode="wb",mtime=0) as writer: writer.write(raw)
    return dict(path=path.relative_to(ROOT).as_posix(),start=begin,end=begin+len(records),record_count=len(records),
        raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest(),gzip_bytes=path.stat().st_size,gzip_sha256=io.sha(path))


def emit_synthetic(base,directory,identity,records,stop,prefix=None):
    """Hand-crafted protocol control; Native strings describe schemas only."""
    directory.mkdir(); start=0 if prefix is None else prefix["completed_proposals"]
    aggregate=core.Aggregate(); parts=[] if prefix is None else list(prefix["parts"]); cps=[]
    for record in records[:start]: aggregate.add(record)
    at=start
    while at<stop:
        end=min(at+50,stop); part=emit_part(directory,at,records[at:end]); parts.append(part)
        for record in records[at:end]: aggregate.add(record)
        at=end; path=directory/f"checkpoint_{at:09d}.json"
        save(path,dict(schema=core.CHECKPOINT_SCHEMA,identity=identity,next_proposal_id=at,parts=parts,aggregate=aggregate.snapshot()))
        cps.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=io.sha(path)))
    if not cps:
        path=directory/f"checkpoint_{at:09d}.json"
        save(path,dict(schema=core.CHECKPOINT_SCHEMA,identity=identity,next_proposal_id=at,parts=parts,aggregate=aggregate.snapshot()))
        cps.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=io.sha(path)))
    selected=min(aggregate.pair_ties,key=lambda r:r["proposal_id"]) if aggregate.pair_ties else None
    for filename,tied,scope in [("minimum_F3_ties.json",aggregate.f3_ties,"All labelled minimumF3 ties in this saved prefix."),
        ("minimum_pair_ties.json",aggregate.pair_ties,"All labelled minimum(F3,E) ties in this saved prefix.")]:
        save(directory/filename,dict(records=tied,scope=scope))
    if selected is not None:
        _,adj,_=core.expected_record(base,selected["proposal_id"]); (directory/"selected_neighbor.adj").write_bytes(io.matrix_bytes(adj))
        save(directory/"selected_neighbor_triples.json",dict(n=base.n,point_degree=base.degree,ordered_triples=rows_for(base,selected),
            proposal_id=selected["proposal_id"],objective_version=core.OBJECTIVE,historical_native_state_written=False))
    by_matrix={}
    if base.metrics["F3"]==0:
        raw=io.matrix_bytes(base.adjacency); by_matrix[hashlib.sha256(raw).hexdigest()]=(None,raw,[list(r) for r in base.rows])
    for record in aggregate.zero_records:
        _,adj,_=core.expected_record(base,record["proposal_id"]); raw=io.matrix_bytes(adj); key=hashlib.sha256(raw).hexdigest()
        if key not in by_matrix: by_matrix[key]=(record["proposal_id"],raw,rows_for(base,record))
    zero_refs=[]
    if by_matrix:
        zero_dir=directory/"residue_zero_objects"; zero_dir.mkdir()
        for index,(key,(pid,raw,rows)) in enumerate(sorted(by_matrix.items())):
            ap=zero_dir/f"object_{index:06d}.adj"; rp=zero_dir/f"object_{index:06d}.triples.json"; ap.write_bytes(raw)
            save(rp,dict(n=base.n,point_degree=base.degree,ordered_triples=rows,proposal_id=pid))
            zero_refs.append(dict(adjacency_path=ap.relative_to(ROOT).as_posix(),adjacency_sha256=key,
                triples_path=rp.relative_to(ROOT).as_posix(),triples_sha256=io.sha(rp),proposal_id=pid,
                target99_domain=(base.n,base.degree)==(99,7),independent_full_SRG_validation_pending=True))
    value=dict(schema=MANIFEST_SCHEMA,identity=identity,objective_version=core.OBJECTIVE,population=base.total,
        completed_proposals=stop,starting_proposal_id=start,proposals_evaluated_this_invocation=stop-start,
        parts=parts,checkpoints=cps,aggregate=aggregate.snapshot(),baseline_metrics=base.metrics,
        status="CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK" if stop==base.total else "UNKNOWN_PREFIX_ONLY",
        budget_stop=False,selection_rule="Every valid proposal eligible; minimize exact(F3,E), then proposalID.",
        selected_proposal_id=None if selected is None else selected["proposal_id"],residue_zero_objects=zero_refs,
        producer="/root/native_driver",independent_approval=False,target_resolution="NONE",historical_native_state_written=False,
        limitations=LIMITATIONS)
    save(directory/"manifest.json",value); return value


def calibration(out,reserve,software):
    results={}; branches=Counter(); negatives=[]; models={}; checked=0; valid=0; visits=0
    def reject(label,stage,call):
        reserve()
        try: call()
        except io.AuditError as error:
            io.need(error.stage==stage,"CALIBRATION_WRONG_STAGE",label+":"+str(error))
            negatives.append(dict(case=label,expected_stage=stage,actual_stage=error.stage,diagnostic=str(error))); return
        raise io.AuditError("CALIBRATION_ACCEPTED_CORRUPTION",label)
    for name,(n,degree,rows) in fixtures().items():
        reserve(); base=core.fixed_input(n,degree,rows); neighbors,set_cn,metrics=scalar_sets(n,degree,rows)
        io.need(io.same(metrics,base.metrics) and io.same(set_cn,base.cn.tolist()),"BASE_SCALAR")
        records=[]
        for pid in range(base.total):
            reserve(); record,adj,cn=core.expected_record(base,pid); records.append(record); checked+=1
            if scalar_check(base,pid,record,adj,cn):
                valid+=1; branches["overlap" if set(record["old_triples"][0]) & set(record["old_triples"][1]) else "disjoint"]+=1
                branches["positive_lambda" if record["new_metrics"]["E_lambda"] else "lambda_zero"]+=1
                if np.any(adj[0]!=base.adjacency[0]): branches["row0_changed"]+=1
        io.need(base.total==(252 if name=="cube12" else 135),"CANONICAL_FINITE_POPULATION")
        identity=dict(fixture=name,software={"synthetic_scope":"OWN_CALIBRATION_ONLY"},n=n,point_degree=degree,total=base.total,objective_version=core.OBJECTIVE)
        runs={}
        for suffix,stop,prefix in [("whole",base.total,None),("prefix17",17,None),("resumed",base.total,"prefix17")]:
            directory=out/(name+"_"+suffix); value=emit_synthetic(base,directory,identity,records,stop,runs.get(prefix))
            named_boundary(value,0 if prefix is None else 17,stop)
            result=audit_run(base,directory,value,identity,reserve); audit_objects(base,directory,value,result)
            visits+=len(result["records"]); runs[suffix]=value
        io.need(io.same(runs["whole"]["aggregate"],runs["resumed"]["aggregate"])
            and io.same(runs["prefix17"]["parts"],runs["resumed"]["parts"][:len(runs["prefix17"]["parts"])]),"PREFIX_ORIGINAL_IDENTITY")
        models[name]=(base,records,identity,runs); results[name]=dict(population=base.total,baseline=base.metrics,valid=sum(r["valid"] for r in records))
    io.need(checked==522 and all(branches[key]>0 for key in ("overlap","disjoint","positive_lambda","row0_changed")),"FINITE_BRANCHES")
    base,records,identity,runs=models["prism9"]; pid=next(r["proposal_id"] for r in records if r["valid"]); good=records[pid]
    for key in sorted(core.FIELDS):
        bad=copy.deepcopy(good); bad[key]="CORRUPTED"
        stage="RECORD_ID" if key=="proposal_id" else "RECORD_SCHEMA" if key in ("schema","objective_version") else "RECORD_CONTENT"
        reject("record_"+key,stage,lambda b=bad:core.check_record(base,pid,b))
    for key in ("F3","E_lambda","E_mu","E","scalar_weight","scalar"):
        bad=copy.deepcopy(good); bad["new_metrics"][key]=float(bad["new_metrics"][key])
        reject("float_metric_"+key,"RECORD_CONTENT",lambda b=bad:core.check_record(base,pid,b))
    for value in (True,float(pid)):
        bad=copy.deepcopy(good); bad["proposal_id"]=value
        reject("typed_pid_"+str(type(value).__name__),"RECORD_ID",lambda b=bad:core.check_record(base,pid,b))
    empty=core.Aggregate().snapshot(); cp=dict(schema=core.CHECKPOINT_SCHEMA,identity=identity,next_proposal_id=0,parts=[],aggregate=empty)
    for label,path,value,stage in [("bool_next",["next_proposal_id"],False,"CHECKPOINT_TYPES"),
        ("float_next",["next_proposal_id"],0.0,"CHECKPOINT_TYPES"),("bad_schema",["schema"],"OLD","CHECKPOINT_IDENTITY"),
        ("bool_identity",["identity","n"],True,"CHECKPOINT_IDENTITY"),
        ("wrong_next",["next_proposal_id"],1,"CHECKPOINT_PREFIX"),
        ("float_count",["aggregate","unique_valid_neighbor_graphs"],0.0,"CHECKPOINT_AGGREGATE"),
        ("bool_count",["aggregate","unique_valid_neighbor_graphs"],False,"CHECKPOINT_AGGREGATE")]:
        bad=copy.deepcopy(cp); owner=bad
        for part in path[:-1]: owner=owner[part]
        owner[path[-1]]=value
        reject("checkpoint_"+label,stage,lambda b=bad:core.checkpoint(b,identity,[],0,empty))
    whole=runs["whole"]; directory=out/"prism9_whole"
    for key,value,stage in [("schema","OLD","MANIFEST_SCHEMA"),("population",float(base.total),"MANIFEST_POPULATION"),
        ("budget_stop",0,"MANIFEST_TYPES"),("baseline_metrics",{},"MANIFEST_BASELINE"),
        ("aggregate",{},"MANIFEST_AGGREGATE"),("status","UNKNOWN_PREFIX_ONLY","MANIFEST_STATUS"),
        ("selected_proposal_id",False,"MANIFEST_SELECTION"),("checkpoints",[],"CHECKPOINT_COVERAGE")]:
        bad=copy.deepcopy(whole); bad[key]=value
        reject("manifest_"+key,stage,lambda b=bad:audit_run(base,directory,b,identity,reserve))
    for key,value in [("starting_proposal_id",1),("completed_proposals",True),("proposals_evaluated_this_invocation",float(base.total))]:
        bad=copy.deepcopy(whole); bad[key]=value
        reject("named_"+key,"NAMED_RUN_BOUNDARY",lambda b=bad:named_boundary(b,0,base.total))
    part=whole["parts"][0]
    for key,value,stage in [("start",False,"PART_TYPES"),("record_count",part["record_count"]+1,"PART_TYPES"),
        ("gzip_sha256","0"*64,"PART_COMPRESSED_HASH"),("raw_sha256","0"*64,"PART_RAW_HASH"),
        ("path","../outside.gz","ARTIFACT_PATH")]:
        bad=copy.deepcopy(part); bad[key]=value
        reject("part_"+key,stage,lambda b=bad:io.part_records(ROOT,out,b))
    for label,raw in [("duplicate",b'{"a":0,"a":1}'),("nonfinite",b'{"a":NaN}'),("utf8",b'\xff')]:
        reject("json_"+label,"JSON",lambda r=raw:io.strict_json(r))
    zero_bad=copy.deepcopy(runs["whole"])
    zero_bad["residue_zero_objects"]=[] if whole["residue_zero_objects"] else [{}]
    prism_result=audit_run(base,directory,whole,identity,reserve)
    reject("zero_wrong_population","ZERO_POPULATION",lambda:audit_objects(base,directory,zero_bad,prism_result))
    # Immutable-cache and genuine integer diagonal controls. Alter a clone,
    # leaving all original finite inputs untouched for subsequent raw replay.
    bad_base=core.fixed_input(base.n,base.degree,base.rows); bad_base.metrics["F3"]=float(bad_base.metrics["F3"])
    reject("mutable_metric_alias","BASE_IMMUTABILITY",lambda:core.unchanged(bad_base))
    for label,array,degree in [("float_matrix",base.adjacency.astype(float),2),("bool_degree",base.adjacency,True),
        ("wrong_regular_degree",base.adjacency,3)]:
        reject(label,"TERNARY_SCORE_DOMAIN",lambda a=array,d=degree:core.score(a,d))
    for name,(b,_,_,_) in models.items(): core.unchanged(b)
    # Constructed99 degree4 graph from eleven disjoint rook9 blocks. This is
    # a size/arithmetic fixture, not the actual99 scientific input or a target.
    rook_rows=fixtures()["rook9"][2]
    rows99=[[v+9*block for v in row] for block in range(11) for row in rook_rows]
    synthetic99=core.fixed_input(99,2,rows99); _,cn99,metrics99=scalar_sets(99,2,rows99)
    io.need(io.same(cn99,synthetic99.cn.tolist()) and io.same(metrics99,synthetic99.metrics),"SYNTHETIC99_SCALAR")
    full99=core.full_integer_target(synthetic99.adjacency)
    io.need(full99["degree14"] is False and full99["is_target"] is False and full99["identity_mismatches"]>0,
        "SYNTHETIC99_NOT_TARGET")
    reject("float_target_array","TARGET_DOMAIN",lambda:core.full_integer_target(synthetic99.adjacency.astype(float)))
    # Independently hand-built protocol profile: no claim of actual Linux
    # execution/UID observation. The actual profile is read only in check mode.
    plan=io.strict_json((ROOT/AUTHOR_PLAN).read_bytes()); child=plan["command"][plan["command"].index("--")+1:]
    runtime=dict(command=child,cwd="/mnt/c/Users/ikuto/projects/conway-99-graph",source_sha256=STATIC["acceleration/run_compute_command.py"],
        seconds=180.0,shutdown_reserve_seconds=20.0,invocation_id="SYNTHETIC_NOT_EXECUTED")
    terminal=dict(command_exit_code=0,invocation_id=runtime["invocation_id"],cleanup=dict(reaped=True,actual_exit_code=0,
        cleanup_errors=[],process_group_live_pids=[],job_active_zero_observed=True))
    admission=dict(schema="TERNARY_TWO_LINE_V1_AUTHOR_CONTROLS_ADMISSION_V1",default_uid_probe=dict(
        command=["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"],stdout_uid="1000",exit_code=0),
        admitted=True,scientific_launched=False,actual99_read=False,plan=dict(path=AUTHOR_PLAN,sha256=AUTHOR_PLAN_SHA,words=36),
        source_pins=[dict(path=p,sha256=h,matched=True) for p,h in software.items()])
    author=dict(command=["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",*child[13:]],
        cwd=runtime["cwd"],python="3.12.3",tqdm="4.67.1")
    profile_values=[author,runtime,terminal,plan,admission]
    linux_profile(*profile_values,software)
    for label,at,path,value,stage in [
        ("wrong_cwd",1,["cwd"],"outside","LINUX_COMMAND_PROFILE"),
        ("wrong_supervisor",1,["source_sha256"],"0"*64,"LINUX_COMMAND_PROFILE"),
        ("wrong_outer",1,["seconds"],120.0,"LINUX_COMMAND_PROFILE"),
        ("wrong_shutdown",1,["shutdown_reserve_seconds"],10.0,"LINUX_COMMAND_PROFILE"),
        ("wrong_python",0,["python"],"wrong","LINUX_CHILD_BINDING"),
        ("wrong_tqdm",0,["tqdm"],"wrong","LINUX_CHILD_BINDING"),
        ("bool_exit",2,["command_exit_code"],False,"LINUX_TERMINAL"),
        ("bool_actual_exit",2,["cleanup","actual_exit_code"],False,"LINUX_TERMINAL"),
        ("unreaped",2,["cleanup","reaped"],False,"LINUX_TERMINAL"),
        ("live_group",2,["cleanup","process_group_live_pids"],[17],"LINUX_TERMINAL"),
        ("cleanup_error",2,["cleanup","cleanup_errors"],["error"],"LINUX_TERMINAL"),
        ("wrong_invocation",2,["invocation_id"],"wrong","LINUX_TERMINAL"),
        ("integer_uid",4,["default_uid_probe","stdout_uid"],1000,"UID_ADMISSION"),
        ("bad_uid",4,["default_uid_probe","stdout_uid"],"0","UID_ADMISSION"),
        ("bool_uid_exit",4,["default_uid_probe","exit_code"],False,"UID_ADMISSION"),
        ("wrong_plan",4,["plan","sha256"],"0"*64,"UID_ADMISSION"),
        ("bool_words",4,["plan","words"],True,"UID_ADMISSION"),
        ("science_flag",4,["scientific_launched"],True,"UID_ADMISSION"),
        ("actual99_flag",4,["actual99_read"],True,"UID_ADMISSION"),
        ("missing_software",4,["source_pins"],[],"ADMISSION_SOURCE_PINS")]:
        values=copy.deepcopy(profile_values); owner=values[at]
        for key in path[:-1]: owner=owner[key]
        owner[path[-1]]=value
        reject("profile_"+label,stage,lambda v=values:linux_profile(*v,software))
    for residual in (-2,-1,0,1,2,3,6,12):
        io.need(pair_cost(residual+2,0)==[int(residual%3!=0),0,residual*residual,residual%3],"PAIR_COST_POSITIVE")
    for label,common,adjacent in [("bool_common0",False,0),("bool_common1",True,0),("float_common",0.0,0),
        ("negative_common",-1,0),("bool_edge",0,False),("float_edge",0,1.0),("nonbinary_edge",0,2)]:
        reject("pair_cost_"+label,"PAIR_COST",lambda c=common,a=adjacent:pair_cost(c,a))
    for name,(n,degree,rows) in fixtures().items(): domain_control(dict(n=n,point_degree=degree,triples=rows))
    # The producer stores off-diagonal CN with zero diagonal. This adapter is
    # independently tested rather than confusing that cache with true A^2.
    cn_cache=base.cn.tolist()
    for at in range(base.n): cn_cache[at][at]=0
    cache_values={"masks":[sum(int(base.adjacency[u,v])<<v for v in range(base.n)) for u in range(base.n)],
        "cn":cn_cache,"metrics":copy.deepcopy(base.metrics),"pairs":[list(p) for p in base.pairs],"total":base.total}
    for key,value in cache_values.items(): cache_control(base,dict(cache_key=key,corrupted_value=value))
    for key in cache_values:
        value=copy.deepcopy(cache_values[key])
        if key=="masks": value[0]=float(value[0])
        elif key=="cn": value[0][0]=False
        elif key=="metrics": value["F3"]=float(value["F3"])
        elif key=="pairs": value[0]=[False,1]
        else: value=float(value)
        reject("cache_"+key,"CACHE_"+key.upper(),lambda k=key,v=value:cache_control(base,dict(cache_key=k,corrupted_value=v)))
    rb,_,ri,rr=models["rook9"]; rd=out/"rook9_whole"; rm=rr["whole"]
    rresult=audit_run(rb,rd,rm,ri,reserve)
    io.need(len(rm["residue_zero_objects"])>0,"KNOWN_ROOK_ZERO_OBJECT")
    for key,value in [("adjacency_sha256","0"*64),("target99_domain",True),("proposal_id",False)]:
        bad=copy.deepcopy(rm); bad["residue_zero_objects"][0][key]=value
        reject("zero_ref_"+key,"ZERO_OBJECT_IDENTITY",lambda b=bad:audit_objects(rb,rd,b,rresult))
    io.need(len(negatives)==99,"CALIBRATION_NEGATIVE_POPULATION")
    save(out/"negative_controls.json",negatives)
    return dict(unique_fixture_labels=checked,valid_fixture_labels=valid,raw_record_replay_visits=visits,
        whole_prefix_resume_equalities=3,complete_scalar_crosschecks=522,scalar_CN_diagonal_convention="Genuine A squared, diagonal=2degree",
        branches=dict(branches),fixtures=results,strict_negative_controls=len(negatives),negative_controls=negatives,
        constructed99_scalar_cells=9801,constructed99_point_degree=2,
        actual_target_input_read=False,producer_outputs_checked=False)


def authenticate(self_sha,spec_sha):
    pins={**STATIC,SELF:self_sha,SPEC:spec_sha}
    for path,value in pins.items(): io.need(io.sha(ROOT/path)==value,"SOURCE_IDENTITY",path)
    core.authenticate(ROOT)
    plan=io.strict_json((ROOT/AUTHOR_PLAN).read_bytes()); software=plan.get("inputs_sha256")
    io.need(type(software) is dict and len(software)==18,"AUTHOR_SOFTWARE_IDENTITY")
    for path,value in software.items():
        io.need(io.sha(ROOT/path)==value,"SOURCE_IDENTITY",path); pins[path]=value
    return pins,software


def pair_cost(common,adjacent):
    io.need(io.integer(common) and common>=0 and io.integer(adjacent) and adjacent in (0,1),"PAIR_COST")
    residual=common+adjacent-2
    return [int(residual%3!=0),residual*residual if adjacent else 0,
        residual*residual if not adjacent else 0,residual%3]


def cache_control(base,value):
    key=value.get("cache_key"); io.need(key in ("masks","cn","metrics","pairs","total"),"CACHE_CONTROL_SCHEMA")
    cn=base.cn.tolist()
    for row in range(base.n): cn[row][row]=0
    expected={"masks":[sum(int(base.adjacency[u,v])<<v for v in range(base.n)) for u in range(base.n)],
        "cn":cn,"metrics":base.metrics,"pairs":[list(pair) for pair in base.pairs],"total":base.total}
    io.need(io.same(value.get("corrupted_value"),expected[key]),"CACHE_"+key.upper())


def domain_control(value):
    n,degree,rows=(value.get(k) for k in ("n","point_degree","triples"))
    io.need(io.integer(n) and io.integer(degree) and 3<=n<=99 and 0<2*degree<n
        and type(rows) is list and all(type(row) is list and len(row)==3 and all(io.integer(v) and 0<=v<n for v in row)
            and len(set(row))==3 for row in rows)
        and len({tuple(sorted(row)) for row in rows})==len(rows),"DOMAIN_CONTROL")
    occupancy=Counter(tuple(sorted(pair)) for row in rows for pair in combinations(row,2))
    io.need(all(count==1 for count in occupancy.values()),"DOMAIN_LINEARITY")
    io.need(len(rows)*3==n*degree and all(sum(v in row for row in rows)==degree for v in range(n)),"DOMAIN_DEGREE")
    return core.fixed_input(n,degree,rows)


def replay_checkpoint(base,directory,value,identity,reserve=lambda:None):
    io.need(type(value) is dict and set(value)=={"schema","identity","next_proposal_id","parts","aggregate"}
        and io.integer(value.get("next_proposal_id")) and type(value.get("parts")) is list
        and type(value.get("aggregate")) is dict,"CHECKPOINT_TYPES")
    io.need(value.get("schema")==core.CHECKPOINT_SCHEMA and io.same(value.get("identity"),identity),"CHECKPOINT_IDENTITY")
    aggregate=core.Aggregate(); at=0
    for part in value["parts"]:
        reserve(); raw=io.part_records(ROOT,directory,part); io.need(part["start"]==at,"PART_COVERAGE")
        for record in raw:
            expected,_,_=core.check_record(base,record["proposal_id"],record); aggregate.add(expected)
        at=part["end"]
    core.checkpoint(value,identity,value["parts"],at,aggregate.snapshot())


def linux_profile(author,runtime,terminal,plan,admission,software):
    command=plan.get("command")
    io.need(type(command) is list and len(command)==36 and command.count("--")==1
        and command[:6]==["/usr/bin/python3","acceleration/run_compute_command.py","--seconds","180","--shutdown-reserve-seconds","20"]
        and io.same(runtime.get("command"),command[command.index("--")+1:])
        and runtime.get("cwd")=="/mnt/c/Users/ikuto/projects/conway-99-graph"
        and runtime.get("source_sha256")==STATIC["acceleration/run_compute_command.py"]
        and runtime.get("seconds")==180.0 and runtime.get("shutdown_reserve_seconds")==20.0,"LINUX_COMMAND_PROFILE")
    child=["/usr/bin/env","UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv","/root/.local/bin/uv","run","--locked","--offline",
        "--project","acceleration/native_budget_env_v1","--cache-dir","build/native-budget-linux-cache","--python","/usr/bin/python3","python",
        "acceleration/census_20261003_ternary_two_line_v1.py","controls","--seconds","150","--out",AUTHOR_ROOT,"--source-commit",
        "63437c9b9fc2dd58b3bdfb51fc347b880b397503"]
    worker=["/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/native_budget_env_v1/build/native-budget-linux-venv/bin/python3",*child[13:]]
    io.need(io.same(runtime["command"],child) and io.same(author.get("command"),worker)
        and author.get("cwd")==runtime["cwd"] and author.get("python")=="3.12.3" and author.get("tqdm")=="4.67.1",
        "LINUX_CHILD_BINDING")
    cleanup=terminal.get("cleanup")
    io.need(type(cleanup) is dict and cleanup.get("reaped") is True and io.integer(cleanup.get("actual_exit_code"))
        and cleanup["actual_exit_code"]==0 and cleanup.get("cleanup_errors")==[] and cleanup.get("process_group_live_pids")==[]
        and cleanup.get("job_active_zero_observed") is True and io.integer(terminal.get("command_exit_code"))
        and terminal["command_exit_code"]==0 and terminal.get("invocation_id")==runtime.get("invocation_id"),"LINUX_TERMINAL")
    probe=admission.get("default_uid_probe")
    io.need(admission.get("schema")=="TERNARY_TWO_LINE_V1_AUTHOR_CONTROLS_ADMISSION_V1"
        and type(probe) is dict and probe.get("command")==["wsl.exe","-d","Ubuntu-24.04","--","/usr/bin/id","-u"]
        and type(probe.get("stdout_uid")) is str and probe["stdout_uid"]=="1000"
        and io.integer(probe.get("exit_code")) and probe["exit_code"]==0 and admission.get("admitted") is True
        and admission.get("scientific_launched") is False and admission.get("actual99_read") is False
        and admission.get("plan",{}).get("path")==AUTHOR_PLAN and admission.get("plan",{}).get("sha256")==AUTHOR_PLAN_SHA
        and io.integer(admission.get("plan",{}).get("words")) and admission["plan"]["words"]==36,"UID_ADMISSION")
    records=admission.get("source_pins")
    io.need(type(records) is list and len(records)==18 and all(type(r) is dict and r.get("matched") is True for r in records)
        and {r.get("path"):r.get("sha256") for r in records}==software,"ADMISSION_SOURCE_PINS")


def author_negatives(directory,author,models,reserve):
    rows=author.get("strict_negatives"); io.need(type(rows) is list and len(rows)==160
        and io.integer(author.get("strict_negative_count")) and author["strict_negative_count"]==160,"AUTHOR_NEGATIVE_POPULATION")
    expected=[]; reports=[]
    def reject(label,pstage,stage,call):
        reserve(); expected.append((label,pstage))
        try: call()
        except io.AuditError as error:
            io.need(error.stage==stage,"AUTHOR_COUNTERPART_STAGE",label+":"+str(error))
            reports.append(dict(case=label,producer_expected_stage=pstage,independent_expected_stage=stage,
                independent_actual_stage=error.stage,diagnostic=str(error))); return
        raise io.AuditError("AUTHOR_CORRUPTION_ACCEPTED",label)
    def artifact(label): return io.strict_json((directory/(label+".json")).read_bytes())
    for name,(base,identity,_) in models.items():
        for key,pstage in [("masks","ADJ_CACHE"),("cn","CN_CACHE"),("metrics","SCORE_CACHE"),("pairs","UNIVERSE_CACHE"),("total","UNIVERSE_CACHE")]:
            label=name+"_bad_"+key; value=artifact(label)
            reject(label,pstage,"CACHE_"+key.upper(),lambda v=value:cache_control(base,v))
        for suffix,pstage,stage in [
            *[("record_"+k,"RECORD_SCORE","RECORD_CONTENT") for k in ("delta_F3","delta_E","delta_E_lambda","delta_E_mu","delta_scalar")],
            *[("metric_"+k,"RECORD_SCORE","RECORD_CONTENT") for k in ("F3","E","scalar","residue_population")],
            ("boolean_record_ID","RECORD_ID","RECORD_ID"),("float_record_ID","RECORD_ID","RECORD_ID"),
            ("wrong_schema","RECORD_SCHEMA","RECORD_SCHEMA"),("wrong_objective_version","RECORD_SCHEMA","RECORD_SCHEMA"),
            ("wrong_tuple_direction","RECORD_SCORE","RECORD_CONTENT"),("wrong_classification","RECORD_SCORE","RECORD_CONTENT"),
            ("float_toggle","RECORD_TOPOLOGY","RECORD_CONTENT"),("forged_invalid_score","RECORD_SCORE","RECORD_CONTENT")]:
            label=name+"_"+suffix; value=artifact(label)
            pid=value.get("proposal_id")
            reject(label,pstage,stage,lambda v=value,p=pid:core.check_record(base,p,v))
        for suffix,pstage,stage in [
            ("empty_boolean_next","CHECKPOINT_TYPES","CHECKPOINT_TYPES"),("empty_float_next","CHECKPOINT_TYPES","CHECKPOINT_TYPES"),
            ("boolean_identity_n","CHECKPOINT_IDENTITY","CHECKPOINT_IDENTITY"),("float_identity_n","CHECKPOINT_IDENTITY","CHECKPOINT_IDENTITY"),
            ("empty_boolean_count","CHECKPOINT_AGGREGATE","CHECKPOINT_AGGREGATE"),("empty_float_count","CHECKPOINT_AGGREGATE","CHECKPOINT_AGGREGATE"),
            ("extra_header","CHECKPOINT_TYPES","CHECKPOINT_TYPES"),("wrong_schema","CHECKPOINT_IDENTITY","CHECKPOINT_IDENTITY"),
            ("wrong_next","CHECKPOINT_AGGREGATE","CHECKPOINT_PREFIX"),("float_best_F3","CHECKPOINT_AGGREGATE","CHECKPOINT_AGGREGATE")]:
            label=name+"_checkpoint_"+suffix; value=artifact(label)
            reject(label,pstage,stage,lambda v=value:replay_checkpoint(base,directory,v,identity,reserve))
        for suffix in ("boolean","float"):
            label=name+"_limit_"+suffix; value=artifact(label)
            reject(label,"CHECKPOINT_TYPES","NAMED_LIMIT",lambda v=value:io.need(io.integer(v.get("limit")) and v["limit"]>=0,"NAMED_LIMIT"))
        for suffix,pstage,stage in [("boolean_start","PART_TYPES","PART_TYPES"),("float_start","PART_TYPES","PART_TYPES"),
            ("wrong_record_count","PART_TYPES","PART_TYPES"),("gzip_hash","PART_HASH","PART_COMPRESSED_HASH"),
            ("raw_hash","PART_HASH","PART_RAW_HASH"),("gzip_bytes","PART_HASH","PART_COMPRESSED_HASH"),
            ("raw_bytes","PART_HASH","PART_RAW_HASH"),("outside_path","PART_PATH","ARTIFACT_PATH"),
            ("shifted_IDs","PART_SEQUENCE","PART_SEQUENCE"),("boolean_ID","PART_SEQUENCE","PART_SEQUENCE"),
            ("float_ID","PART_SEQUENCE","PART_SEQUENCE")]:
            label=name+"_part_"+suffix; value=artifact(label)
            reject(label,pstage,stage,lambda v=value:io.part_records(ROOT,directory,v))
        label=name+"_part_forged_score"; value=artifact(label)
        reject(label,"RECORD_SCORE","RECORD_CONTENT",lambda v=value:replay_checkpoint(base,directory,v,identity,reserve))
    for suffix in ("boolean_common_zero","boolean_common_one","float_common_zero","float_common_one","negative_common",
        "boolean_adj_zero","boolean_adj_one","float_adj_zero","float_adj_one","nonbinary_adj"):
        label="pair_cost_"+suffix; value=artifact(label)
        reject(label,"PAIR_COST","PAIR_COST",lambda v=value:pair_cost(v.get("common"),v.get("adjacent")))
    for suffix,pstage,stage in [("boolean_n","DOMAIN","DOMAIN_CONTROL"),("boolean_degree","DOMAIN","DOMAIN_CONTROL"),
        ("wrong_degree","DEGREE","DOMAIN_DEGREE"),("boolean_vertex","DOMAIN","DOMAIN_CONTROL"),
        ("duplicate_vertex","DOMAIN","DOMAIN_CONTROL"),("duplicate_triple","DOMAIN","DOMAIN_CONTROL"),
        ("repeated_pair","LINEARITY","DOMAIN_LINEARITY")]:
        label="domain_"+suffix; value=artifact(label)
        reject(label,pstage,stage,lambda v=value:domain_control(v))
    for suffix in ("duplicate_key","nonfinite","invalid_utf8"):
        label="json_"+suffix; value=artifact(label)
        reject(label,"JSON","JSON",lambda v=value:io.strict_json(bytes.fromhex(v["raw_hex"])))
    value=artifact("invalid_record_has_no_candidate")
    reject("invalid_record_has_no_candidate","RECORD_VALIDITY","RECORD_VALIDITY",
        lambda:io.need(value.get("valid") is True,"RECORD_VALIDITY"))
    value=artifact("score_float_masks")
    reject("score_float_masks","SCORE_DOMAIN","MASK_DOMAIN",lambda:io.need(type(value.get("masks")) is list
        and all(io.integer(v) for v in value["masks"]),"MASK_DOMAIN"))
    io.need(len(expected)==160 and [r.get("case") for r in rows]==[label for label,_ in expected],"AUTHOR_NEGATIVE_ORDER")
    for row,(label,stage) in zip(rows,expected):
        io.need(type(row) is dict and set(row)=={"case","expected_stage","actual_stage","diagnostic"}
            and row["case"]==label and row["expected_stage"]==row["actual_stage"]==stage
            and type(row["diagnostic"]) is str and row["diagnostic"].startswith(stage+":"),"AUTHOR_NEGATIVE_STAGE")
    return reports


def actual_check(out,pins,software,reserve):
    root=ROOT/AUTHOR_ROOT
    fixed={AUTHOR_ROOT+"/summary.json":AUTHOR_SUMMARY_SHA,AUTHOR_RUNTIME+"/manifest.json":AUTHOR_RUNTIME_SHA,
        AUTHOR_RUNTIME+"/summary.json":AUTHOR_TERMINAL_SHA,AUTHOR_ADMISSION:AUTHOR_ADMISSION_SHA}
    for path,expected in fixed.items(): io.need(io.sha(ROOT/path)==expected,"AUTHOR_INPUT_IDENTITY",path); pins[path]=expected
    author=io.strict_json((root/"summary.json").read_bytes()); runtime=io.strict_json((ROOT/AUTHOR_RUNTIME/"manifest.json").read_bytes())
    terminal=io.strict_json((ROOT/AUTHOR_RUNTIME/"summary.json").read_bytes()); plan=io.strict_json((ROOT/AUTHOR_PLAN).read_bytes())
    admission=io.strict_json((ROOT/AUTHOR_ADMISSION).read_bytes())
    linux_profile(author,runtime,terminal,plan,admission,software)
    io.need(author.get("status")=="AUTHOR_TERNARY_TWO_LINE_V1_CONTROLS_PENDING_INDEPENDENT_GATE"
        and author.get("producer")=="/root/native_driver" and io.same(author.get("software"),software)
        and author.get("actual99graph_read") is False and author.get("scientific_census_launched") is False
        and author.get("stochastic_engine_launched") is False and author.get("independent_approval") is False
        and author.get("target_resolution")=="NONE"
        and author.get("source_reference_commit")=="63437c9b9fc2dd58b3bdfb51fc347b880b397503","AUTHOR_SCOPE")
    models={}; outcome={}; unique=0; calls=0; visits=0; checked_cps=0; valid=0; zeros=0; branches=Counter()
    for name,(n,degree,rows) in fixtures().items():
        reserve(); io.need(io.same(io.strict_json((root/(name+".json")).read_bytes()),dict(n=n,point_degree=degree,triples=rows)),"FIXTURE_IDENTITY")
        base=core.fixed_input(n,degree,rows); identity=dict(fixture=name,software=software,n=n,point_degree=degree,total=base.total,objective_version=core.OBJECTIVE)
        runs={}; models[name]=(base,identity,runs)
        for suffix,start,stop in [("whole",0,base.total),("prefix17",0,17),("resumed",17,base.total),("empty",0,0)]:
            directory=root/(name+"_"+suffix); value=io.strict_json((directory/"manifest.json").read_bytes()); named_boundary(value,start,stop)
            result=audit_run(base,directory,value,identity,reserve); zero_objects=audit_objects(base,directory,value,result)
            visits+=len(result["records"]); checked_cps+=len(result["checkpoints"]); zeros+=len(zero_objects); runs[suffix]=(value,result)
            if suffix in ("whole","prefix17","resumed"): calls+=stop-start
            if suffix=="whole":
                unique+=len(result["records"])
                for record in result["records"]:
                    if not record["valid"]: continue
                    valid+=1; _,adj,cn=core.expected_record(base,record["proposal_id"])
                    scalar_check(base,record["proposal_id"],record,adj,cn)
                    branches["valid_overlap" if set(record["old_triples"][0])&set(record["old_triples"][1]) else "valid_disjoint"]+=1
                    branches["moves_row0" if np.any(adj[0]!=base.adjacency[0]) else "retains_row0"]+=1
                    branches["candidate_positive_lambda" if record["new_metrics"]["E_lambda"] else "candidate_lambda_zero"]+=1
                io.need(io.same(author.get("fixture_manifests",{}).get(name),value),"AUTHOR_FIXTURE_MANIFEST")
        io.need(io.same(runs["whole"][1]["records"],runs["resumed"][1]["records"])
            and io.same(runs["whole"][0]["aggregate"],runs["resumed"][0]["aggregate"])
            and io.same(runs["prefix17"][0]["parts"],runs["resumed"][0]["parts"][:len(runs["prefix17"][0]["parts"])]),"PREFIX_ORIGINAL_IDENTITY")
        outcome[name]=dict(population=base.total,baseline_metrics=base.metrics,aggregate=runs["whole"][0]["aggregate"])
    io.need(unique==522 and calls==1044 and io.same(dict(branches),author.get("branch_counts"))
        and author.get("unique_fixture_labels")==unique and io.integer(author["unique_fixture_labels"])
        and author.get("streamed_proposal_evaluation_calls")==calls and io.integer(author["streamed_proposal_evaluation_calls"])
        and author.get("valid_fixture_labels")==valid and io.integer(author["valid_fixture_labels"])
        and author.get("whole_prefix_resume_equalities")==3 and io.integer(author["whole_prefix_resume_equalities"]),"AUTHOR_COMPLETE_COUNTS")
    negatives=author_negatives(root,author,models,reserve)
    for residual in (-2,-1,0,1,2,3,6,12):
        io.need(pair_cost(residual+2,0)==[int(residual%3!=0),0,residual*residual,residual%3],"SIGNED_RESIDUE")
    io.need(io.integer(author.get("signed_residue_arithmetic_cases")) and author["signed_residue_arithmetic_cases"]==8,"AUTHOR_ARITHMETIC_POPULATION")
    # Preserve a direct hash closure of every finite raw/corrupted file and
    # every observed runtime receipt; this is a finite package, not history.
    for directory in (root,ROOT/AUTHOR_RUNTIME):
        for path in sorted(directory.rglob("*")):
            if path.is_file(): reserve(); pins[path.relative_to(ROOT).as_posix()]=io.sha(path)
    save(out/"author_negative_replay.json",negatives)
    return dict(unique_fixture_labels=unique,streamed_proposal_evaluation_calls=calls,all_raw_record_visits=visits,
        strict_author_negative_cases=len(negatives),whole_prefix_resume_equalities=3,complete_checkpoint_prefixes=checked_cps,
        complete_zero_object_checks=zeros,valid_fixture_labels=valid,branch_counts=dict(branches),fixtures=outcome,
        actual_target_input_read=False,full_target_identity_checked=False,scientific_census_launched=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["calibration","check"])
    parser.add_argument("--out",type=Path,required=True); parser.add_argument("--seconds",type=float,required=True)
    parser.add_argument("--self-sha256",required=True); parser.add_argument("--spec-sha256",required=True)
    parser.add_argument("--source-commit",required=True)
    parser.add_argument("--calibration",type=Path); parser.add_argument("--calibration-sha256")
    args=parser.parse_args(); deadline=CommandDeadline(args.seconds,allocation_reason="NEW F3 independent finite scalar/all24-field/protocol controls or separately authorized finite raw package replay; setup/hash/saving included; no actual99/science/retry")
    out=args.out.resolve(); io.need(out.is_relative_to(ROOT) and not out.exists(),"OUTPUT_PATH")
    pins,software=authenticate(args.self_sha256,args.spec_sha256); out.mkdir(parents=True)
    def reserve(): io.need(deadline.status()["remaining_seconds"]>20 and not deadline.status()["stop_required"],"DEADLINE_RESERVE")
    try:
        if args.mode=="calibration":
            result=calibration(out,reserve,software)
            status="INDEPENDENT_TERNARY_TWO_LINE_RAW_CHECKER_V1_CALIBRATION_PASS"
        else:
            io.need(args.calibration is not None and type(args.calibration_sha256) is str
                and args.calibration.resolve().is_relative_to(ROOT) and io.sha(args.calibration)==args.calibration_sha256,"CALIBRATION_IDENTITY")
            cal=io.strict_json(args.calibration.read_bytes())
            io.need(cal.get("status")=="INDEPENDENT_TERNARY_TWO_LINE_RAW_CHECKER_V1_CALIBRATION_PASS"
                and cal.get("verifier")=="/root/structural" and cal.get("producer_outputs_checked") is False
                and cal.get("complete_scalar_crosschecks")==522 and io.integer(cal["complete_scalar_crosschecks"])
                and cal.get("strict_negative_controls")==99 and io.integer(cal["strict_negative_controls"])
                and all(cal.get("inputs_sha256",{}).get(p)==h for p,h in pins.items()),"CALIBRATION_SCOPE")
            pins[args.calibration.resolve().relative_to(ROOT).as_posix()]=args.calibration_sha256
            for path,value in cal.get("outputs_sha256",{}).items():
                reserve(); io.need(io.sha(io.relative_file(ROOT,path,args.calibration.parent))==value,"CALIBRATION_OUTPUT_IDENTITY"); pins[path]=value
            result=actual_check(out,pins,software,reserve)
            status="INDEPENDENT_TERNARY_TWO_LINE_KERNEL_V1_COMPLETE_CONTROLS_PASS"
        outputs={p.relative_to(ROOT).as_posix():io.sha(p) for p in sorted(out.rglob("*")) if p.is_file()}
        save(out/"summary.json",dict(status=status,
            producer="/root/native_driver" if args.mode=="check" else None,verifier="/root/structural",
            method="independent_artifact_check" if args.mode=="check" else "independent_finite_controls",timestamp=datetime.now(timezone.utc).isoformat(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,
            source_context=args.source_commit,inputs_sha256=pins,shared_components=[RAW_CORE,core.SHARED],
            outputs_sha256=outputs,**result,target_resolution="NONE",scientific_launched=False,deadline=deadline.status()))
    except BaseException as error:
        save(out/"failure.json",dict(error=repr(error),inputs_sha256=pins,deadline=deadline.status(),
            preserved_partial_outputs=True,automatic_retry=False,target_resolution="NONE")); raise


if __name__=="__main__": main()
