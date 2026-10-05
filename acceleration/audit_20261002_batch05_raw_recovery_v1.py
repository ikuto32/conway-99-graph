"""Independent bounded full-byte recovery of batch05 raw package.

No packaging module is imported. Frozen population is reconstructed from the
native manifest and prior independent proof-audit pins plus explicit helpers.
This is engineering byte recovery, not a fresh mathematical proof replay.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import gzip
import hashlib
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
NATIVE="acceleration/results/20261002_batch05_native01/summary.json"
NATIVE_SHA="8e9d697fae19a83ed1127d7594f824f3451e8e84a8d91ef3fdf9744d6fdb89f1"
AUDIT="acceleration/results/20261002_independent_review/batch05_proofs01/summary.json"
AUDIT_SHA="1b94e67d00af2d1971074e121e245d392e9e3a49d540380fb476d634ed779d61"
BINARIES={"build/research-cadical195/source/build/cadical","build/rook-drat-checker/drat-trim.exe"}
COMMON_CODE={"acceleration/command_deadline.py","acceleration/run_compute_command.py","pyproject.toml","uv.lock",
    "acceleration/run_20260930_exact_eight_four_builds_v2.py","acceleration/build_20260930_exact_eight_parallel_batch.py",
    "acceleration/recover_20261001_twentyninth_raw_artifacts.py"}


def need(value,why):
    if not value:raise ValueError(why)


def safe(relative):
    need(isinstance(relative,str) and relative and "\\" not in relative,"literal POSIX path")
    path=Path(relative)
    need(not path.is_absolute() and ".." not in path.parts,"safe relative path")
    result=(ROOT/path).resolve()
    need(result.is_relative_to(ROOT) and result.relative_to(ROOT).as_posix()==relative,"canonical contained path")
    return result


def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()


def save(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,indent=2);stream.write("\n")


def recover(record,read_compressed,original,deadline):
    """Independent streaming decompressor, every raw byte and offset bounded."""
    need(type(record["bytes"])is int and record["bytes"]>=0 and record["parts"],"explicit finite raw size and parts")
    whole=hashlib.sha256();offset=0;seen=set()
    for part in record["parts"]:
        need(part["path"] not in seen and part["raw_offset"]==offset,"unique contiguous compressed parts")
        seen.add(part["path"])
        need(type(part["raw_bytes"])is int and 0<=part["raw_bytes"]<=record["bytes"]-offset,"part bounded by remaining raw record")
        need(type(part["gzip_bytes"])is int and 0<part["gzip_bytes"]<=10*1024**2,"published compressed size bound")
        compressed=read_compressed(part["path"])
        need(len(compressed)==part["gzip_bytes"] and sha_bytes(compressed)==part["gzip_sha256"],"exact compressed identity")
        partial=hashlib.sha256();count=0
        with gzip.GzipFile(fileobj=BytesIO(compressed),mode="rb") as reader:
            while True:
                need(not deadline.status()["stop_required"],"not completed within the allocated budget")
                # Read at most one extra raw byte, so declared limits fail
                # before unbounded expansion; never load a whole raw model.
                block=reader.read(min(1024**2,part["raw_bytes"]-count+1))
                if not block:break
                count+=len(block)
                need(count<=part["raw_bytes"],"bounded decompressed part")
                need(original.read(len(block))==block,"every literal original raw byte agrees")
                whole.update(block);partial.update(block)
        need(count==part["raw_bytes"] and partial.hexdigest()==part["raw_sha256"],"every complete raw part identity")
        offset+=count
    need(offset==record["bytes"] and not original.read(1) and whole.hexdigest()==record["sha256"],"whole raw length/hash and no omitted tail")
    return dict(path=record["path"],sha256=whole.hexdigest(),bytes=offset,parts=len(record["parts"]),literal_byte_comparison=True)


def controls(deadline):
    payload=b"known raw recovery fixture\x00\xff\n"*9
    first,second=payload[:70],payload[70:]
    data={"first.gz":gzip.compress(first,mtime=0),"second.gz":gzip.compress(second,mtime=0)}
    parts=[];offset=0
    for name,raw in [("first.gz",first),("second.gz",second)]:
        parts.append(dict(path=name,gzip_sha256=sha_bytes(data[name]),gzip_bytes=len(data[name]),raw_offset=offset,raw_sha256=sha_bytes(raw),raw_bytes=len(raw)))
        offset+=len(raw)
    record=dict(path="fixture.raw",sha256=sha_bytes(payload),bytes=len(payload),parts=parts)
    recover(record,lambda name:data[name],BytesIO(payload),deadline)
    rejected=[]
    mutations=[("raw_hash",lambda value:value.update(sha256="0"*64)),
        ("raw_length",lambda value:value.update(bytes=len(payload)+1)),
        ("compressed_hash",lambda value:value["parts"][0].update(gzip_sha256="0"*64)),
        ("part_raw_hash",lambda value:value["parts"][0].update(raw_sha256="0"*64)),
        ("noncontiguous_parts",lambda value:value["parts"][1].update(raw_offset=71)),
        ("duplicate_part",lambda value:value["parts"][1].update(path="first.gz")),
        ("decompression_length_bound",lambda value:value["parts"][0].update(raw_bytes=69))]
    for label,mutate in mutations:
        bad=copy.deepcopy(record);mutate(bad)
        try:recover(bad,lambda name:data[name],BytesIO(payload),deadline)
        except ValueError:rejected.append(label)
        else:raise ValueError("corrupted recovery control accepted: "+label)
    try:recover(record,lambda name:data[name],BytesIO(payload[:-1]+b"x"),deadline)
    except ValueError:rejected.append("conflicting_original_bytes")
    else:raise ValueError("corrupted original accepted")
    empty=gzip.compress(b"",mtime=0)
    empty_record=dict(path="empty.raw",sha256=sha_bytes(b""),bytes=0,parts=[dict(path="empty.gz",gzip_sha256=sha_bytes(empty),gzip_bytes=len(empty),raw_offset=0,raw_sha256=sha_bytes(b""),raw_bytes=0)])
    recover(empty_record,lambda _:empty,BytesIO(),deadline)
    for name in ["../escape", "C:/escape", "path\\escape"]:
        try:safe(name)
        except ValueError:rejected.append("path_guard:"+name)
        else:raise ValueError("unsafe path accepted")
    return dict(positive_multichunk=True,positive_empty=True,corrupted_controls_rejected=rejected)


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason="Full lossless direct batch05 package recovery and independent inventory reconstruction;30second orderly output reserve")
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    pins={};outcomes=[]
    def pin(path,wanted=None):
        path=path.resolve();h=hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda:stream.read(1024**2),b""):
                need(not deadline.status()["stop_required"],"not completed within the allocated budget");h.update(block)
        actual=h.hexdigest();need(wanted is None or actual==wanted,"exact identity: "+str(path))
        pins[path.relative_to(ROOT).as_posix()]=actual;return actual
    def read(name,wanted=None):
        pin(safe(name),wanted);return json.loads(safe(name).read_bytes())
    try:
        calibrated=controls(deadline)
        if args.calibrate_only:
            pin(Path(__file__));pin(ROOT/"uv.lock");pin(ROOT/"acceleration/run_compute_command.py");pin(ROOT/"acceleration/command_deadline.py")
            result=dict(status="INDEPENDENT_BATCH05_RAW_RECOVERY_V1_CONTROLS_PASS",timestamp=datetime.now(timezone.utc).isoformat(),verifier="/root/checkpoint_audit",controls=calibrated,inputs_sha256=pins,
                command=[sys.executable,*sys.argv],cwd=str(ROOT),mathematical_verification=False,elapsed_seconds=time.monotonic()-start)
        else:
            need(args.manifest and args.manifest_sha256 and args.inventory and args.inventory_sha256,"frozen explicit inventory/manifest identities")
            inv=read(args.inventory,args.inventory_sha256);manifest=read(args.manifest,args.manifest_sha256)
            need(inv["schema"]=="BATCH05_RAW_PUBLICATION_FROZEN_V1" and manifest["schema"]=="BATCH05_NORMALIZED_RAW_RECOVERY_V1","normalized frozen raw interface")
            native,audit=read(NATIVE,NATIVE_SHA),read(AUDIT,AUDIT_SHA)
            native_manifest=read(native["manifest_path"],native["manifest_sha256"])
            need(audit["status"]=="INDEPENDENT_EXACT_EIGHT_POLICY_LITERAL_PROOFS_PASS" and audit["completed_proof_replays"]==64,"prior exact64proof outcome scope")
            expected={NATIVE:NATIVE_SHA,AUDIT:AUDIT_SHA,native["manifest_path"]:native["manifest_sha256"]}
            for dictionary in [native_manifest["inputs_sha256"],audit["inputs_sha256"]]:
                for name,identity in dictionary.items():
                    need(name not in expected or expected[name]==identity,"source/audit pin consistency");expected[name]=identity
            code=set(inv["code_sha256"])
            need(COMMON_CODE<=code and all(name in COMMON_CODE or re.fullmatch(r"acceleration/package_20261002_batch05_raw_v[1-9][0-9]*(?:_spec\.md|\.py)",name) for name in code),"explicit safe packaging helper closure")
            for name,identity in inv["code_sha256"].items():
                pin(safe(name),identity);expected[name]=identity
            cases=[];kinds={}
            need(len(native["case_records"])==len(audit["case_records"])==64,"exact ordered64case population")
            for produced,checked in zip(native["case_records"],audit["case_records"]):
                need((produced["case_id"],produced["case_index"])==(checked["case_id"],checked["case_index"]),"same ordered raw case identity")
                case=read(produced["summary_path"],produced["summary_sha256"])
                expected[produced["summary_path"]]=produced["summary_sha256"]
                files=case["formula"]["files"]
                need((checked["cnf_path"],checked["cnf_sha256"])==(files["instance.cnf"]["path"],files["instance.cnf"]["sha256"]),"rawCNF independently checked identity")
                proof=case["raw_proof"]
                need((checked["proof_path"],checked["proof_sha256"],checked["proof_bytes"])==(proof["path"],proof["sha256"],proof["bytes"]),"complete raw proof identity")
                need(checked["verification_outcome"]=="UNSAT_VERIFIED" and checked["complete_independent_replay"]["accepted"] is True,"complete previous mathematical replay outcome")
                for label,descriptor in files.items():
                    need(expected.get(descriptor["path"])==descriptor["sha256"],"entire direct formula input pin");kinds[descriptor["path"]]=label
                kinds[proof["path"]]="proof.drat"
                cases.append(dict(case_id=produced["case_id"],case_index=produced["case_index"],proof_path=proof["path"],cnf_path=checked["cnf_path"],model_path=files["model.json"]["path"],scope_path=files["scope.json"]["path"]))
            need(len({case["case_id"] for case in cases})==64 and inv["cases"]==cases,"complete distinct frozen critical population")
            tools={row["path"]:row for row in inv["non_payload_tools"]}
            need(set(tools)==BINARIES,"only two explicit platform binaries omitted")
            for name in BINARIES:pin(safe(name),expected[name]);need(tools[name]["sha256"]==expected[name] and tools[name]["availability"]=="LOCAL_ONLY","tool identity/disclosure")
            expected={name:identity for name,identity in expected.items() if name not in BINARIES}
            inventory={record["path"]:record for record in inv["records"]}
            need(len(inventory)==len(inv["records"])==inv["record_count"] and set(inventory)==set(expected),"entire independently reconstructed direct recovery population")
            rows=manifest["records"]
            need(len(rows)==len({row["path"] for row in rows})==len(inventory) and {row["path"] for row in rows}==set(inventory),"no missing/duplicated raw manifest members")
            for row in tqdm(rows,desc="Independent complete raw recovery",mininterval=5):
                original=inventory[row["path"]]
                need({key:row[key] for key in ["path","sha256","bytes","kind","case"]}=={key:original[key] for key in ["path","sha256","bytes","kind","case"]},"exact frozen raw descriptor")
                need(row["sha256"]==expected[row["path"]] and row["kind"]==kinds.get(row["path"],"direct_replay_metadata_or_source"),"independent byte/kind population")
                with safe(row["path"]).open("rb") as raw:
                    checked=recover(row,lambda name:safe(name).read_bytes(),raw,deadline)
                for part in row["parts"]:pins[part["path"]]=part["gzip_sha256"]
                outcomes.append(checked)
            counts=Counter(row["kind"] for row in rows)
            need(all(counts[kind]==64 for kind in ["proof.drat","instance.cnf","model.json","scope.json"]),"every64critical artifact class recovered")
            need(manifest["inventory"]==args.inventory and manifest["inventory_sha256"]==args.inventory_sha256 and manifest["raw_artifacts"]==len(rows)
                and manifest["raw_bytes"]==inv["raw_bytes"]==sum(row["bytes"] for row in rows),"actual manifest whole population summary")
            parts=[part for row in rows for part in row["parts"]]
            need(manifest["gzip_parts"]==len(parts) and manifest["gzip_bytes"]==sum(part["gzip_bytes"] for part in parts),"exact compressed counting unit")
            need(manifest["mathematical_verification"] is False and manifest["independent_approval"] is False and manifest["availability"]=="LOCAL_ONLY","producer not self-promoted")
            pin(Path(__file__));pin(ROOT/"uv.lock");pin(ROOT/"pyproject.toml");pin(ROOT/"acceleration/run_compute_command.py");pin(ROOT/"acceleration/command_deadline.py")
            result=dict(status="INDEPENDENT_BATCH05_COMPLETE_RAW_RECOVERY_V1_PASS",timestamp=datetime.now(timezone.utc).isoformat(),verifier="/root/checkpoint_audit",producer="/root/native_driver",
                source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
                inputs_sha256=pins,controls=calibrated,case_count=64,raw_artifacts=len(rows),raw_bytes=sum(row["bytes"] for row in rows),kind_counts=dict(counts),gzip_parts=len(parts),gzip_bytes=sum(part["gzip_bytes"] for part in parts),records=outcomes,
                scope="Exact frozen direct replay closure, every decompressed part and literal raw byte; historical transitive gate closure is not recursively repackaged.",
                shared_components=["Python gzip/zlib/SHA-256, pinned environment and contained deadline; no packaging or historical recovery module imported."],
                limitations=["Recovery is an engineering identity check; no mathematical proof replay repeated.","Platform binaries remain separately LOCAL_ONLY with exact pinned identity.","No remote public availability or complete historical recursive recovery is established by this local check."],
                mathematical_verification=False,new_exclusions=0,target_resolution=False,artifact_availability="LOCAL_ONLY",elapsed_seconds=time.monotonic()-start)
        save(args.out/"summary.json",result);print(json.dumps(dict(status=result["status"],sha256=sha_bytes((args.out/"summary.json").read_bytes()))),flush=True)
    except BaseException as error:
        save(args.out/"failure.json",dict(error=repr(error),completed_raw_recoveries=len(outcomes),elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True);parser.add_argument("--seconds",type=float,required=True);parser.add_argument("--calibrate-only",action="store_true")
    parser.add_argument("--inventory");parser.add_argument("--inventory-sha256");parser.add_argument("--manifest");parser.add_argument("--manifest-sha256")
    run(parser.parse_args())
