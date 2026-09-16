"""Bounded shared C99CP1 rejection controls for independent CPU and CUDA tools."""
import argparse
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import time

from audit_certificate import full_graph

ROOT=Path(__file__).resolve().parents[1]


def require(ok,message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def cap_bad_edges(edges):
    labels=[(a,b) for a,b in combinations(range(14),2) if a//2!=b//2]
    labels.sort(key=lambda pair:(pair[0]//2,pair[1]//2,pair))
    supports=[{a//2,b//2} for a,b in labels]
    known=set(map(tuple,edges))
    for old1,old2 in combinations(sorted(known),2):
        u,v=old1;a,b=old2
        if len({u,v,a,b})!=4:
            continue
        for raw in (((u,a),(v,b)),((u,b),(v,a))):
            added={tuple(sorted(pair)) for pair in raw}
            if added & known or any(len(supports[i]&supports[j])!=1 for i,j in added):
                continue
            changed=sorted(known-{old1,old2}|added)
            try:
                full_graph({"overlap_edges_outer_zero_based":list(map(list,changed))})
            except ValueError as exc:
                if "Partial common-neighbor cap" in str(exc):
                    return changed,dict(removed=[old1,old2],added=sorted(added),independent_rejection=str(exc))
    raise ValueError("No bounded two-swap partial-cap negative control found")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--cpu",type=Path,default=ROOT/"acceleration/build/overlap_cp_cpu.exe")
    parser.add_argument("--gpu",type=Path,default=ROOT/"acceleration/build/overlap_cp_gpu.exe")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),"Preserve prior rejection report")
    start=time.perf_counter()
    paths=[args.input,args.cpu,args.gpu,Path(__file__),ROOT/"acceleration/audit_certificate.py",
           ROOT/"acceleration/overlap_cp_cpu.rs",ROOT/"acceleration/overlap_cp_gpu.cu"]
    bindings={key(path):digest(path) for path in paths}
    tokens=args.input.read_text().split()
    require(tokens[0]=="C99CP1","Unexpected source format")
    n,nsteps=map(int,tokens[1:3]);xoff=3+nsteps;yoff=xoff+1680;eoff=yoff+4326
    require(n>=1 and nsteps>=2 and len(tokens)==eoff+336*n,"Unexpected valid input shape")
    edges=[[int(tokens[eoff+2*i]),int(tokens[eoff+2*i+1])] for i in range(168)]
    full_graph({"overlap_edges_outer_zero_based":edges})
    cases=[]

    def modify(name,index,value):
        copied=tokens.copy();copied[index]=str(value);cases.append((name,copied,[]))

    for name,index,value in [
        ("wrong_magic",0,"BAD"),("zero_candidates",1,0),("negative_candidates",1,-1),("too_many_candidates",1,100001),
        ("zero_checkpoints",2,0),("too_many_checkpoints",2,33),("zero_checkpoint",3,0),
        ("too_large_checkpoint",3,1000001),("negative_checkpoint",3,-1),("duplicate_checkpoint",4,tokens[3]),
        ("noninteger_checkpoint",3,"1.5"),
        ("nan_x",xoff,"NaN"),("inf_x",xoff,"inf"),("negative_x",xoff,-.125),("x_above_one",xoff,1.125),
        ("nan_quota_y",yoff,"NaN"),("negative_inf_y",yoff,"-inf"),("quota_y_below_minus_one",yoff,-1.125),
        ("quota_y_above_one",yoff,1.125),("cap_y_below_zero",yoff+840,-.125),("cap_y_above_one",yoff+840,1.125),
        ("edge_endpoint_out_of_range",eoff+1,84),("negative_edge_endpoint",eoff,-1),
        ("self_loop",eoff+1,tokens[eoff])]:
        modify(name,index,value)
    backwards=tokens.copy();backwards[3],backwards[4]=backwards[4],backwards[3];cases.append(("descending_checkpoints",backwards,[]))
    reversed_edge=tokens.copy();reversed_edge[eoff:eoff+2]=reversed(reversed_edge[eoff:eoff+2]);cases.append(("reversed_edge",reversed_edge,[]))
    duplicate=tokens.copy();duplicate[eoff:eoff+2]=duplicate[eoff+2:eoff+4];cases.append(("duplicate_edge",duplicate,[]))
    nonoverlap=tokens.copy();nonoverlap[eoff:eoff+2]=["0","1"];cases.append(("same_support_edge",nonoverlap,[]))
    cap_bad,witness=cap_bad_edges(edges)
    cap_tokens=tokens.copy();cap_tokens[eoff:eoff+336]=[str(v) for edge in cap_bad for v in edge]
    cases.append(("degree_preserving_partial_cap_violation",cap_tokens,[]))
    cases.extend([(name,tokens[:stop],[]) for name,stop in (("truncated_x",yoff-1),("truncated_y",eoff-1),("truncated_last_edge",len(tokens)-1))])
    cases.append(("trailing_tokens",tokens+["0"],[]))
    cases.append(("invalid_option",tokens,["--unknown"]))
    vector_tokens=tokens[:eoff]+tokens[eoff:eoff+336]*65;vector_tokens[1]="65"
    cases.append(("vector_candidate_limit",vector_tokens,["--vectors"]))
    args.out.mkdir(parents=True,exist_ok=False)
    inputs_dir=args.out/"invalid_inputs";inputs_dir.mkdir()
    reports=[]
    for name,case_tokens,flags in cases:
        path=inputs_dir/(name+".txt")
        path.write_text(" ".join(case_tokens)+"\n",encoding="ascii")
        bindings[key(path)]=digest(path)
        for tool,binary in (("cpu",args.cpu),("gpu",args.gpu)):
            out=args.out/(tool+"_"+name+"_unexpected.json")
            proc=subprocess.run([str(binary),str(path),str(out),*flags],capture_output=True,text=True,timeout=20)
            require(proc.returncode!=0 and not out.exists(),"Invalid CLI input accepted: "+tool+"/"+name)
            reports.append(dict(tool=tool,name=name,input_path=key(path),input_sha256=digest(path),options=flags,
                                returncode=proc.returncode,rejected=True,reason=proc.stderr.strip()))
    for tool,binary in (("cpu",args.cpu),("gpu",args.gpu)):
        out=args.out/(tool+"_existing_output.txt")
        out.write_text("immutable sentinel\n",encoding="ascii");before=digest(out)
        proc=subprocess.run([str(binary),str(args.input),str(out)],capture_output=True,text=True,timeout=20)
        require(proc.returncode!=0 and digest(out)==before,"Existing output overwritten")
        reports.append(dict(tool=tool,name="existing_output",returncode=proc.returncode,rejected=True,reason=proc.stderr.strip(),preserved_sha256=before))
        proc=subprocess.run([str(binary)],capture_output=True,text=True,timeout=20)
        require(proc.returncode!=0,"Missing CLI arguments accepted")
        reports.append(dict(tool=tool,name="missing_arguments",returncode=proc.returncode,rejected=True,reason=proc.stderr.strip()))
    require(all(digest(ROOT/path)==expected for path,expected in bindings.items()),"Bound source or input changed")
    report=dict(status="CP_CPU_GPU_SHARED_INPUT_NEGATIVE_CONTROLS_PASS",inputs_sha256=bindings,
                tools_checked=["cpu","gpu"],negative_cases_per_tool=len(cases)+2,negative_invocations=len(reports),
                all_rejected=True,controls=reports,degree_preserving_cap_negative=witness,
                own_label_quota_note="Under degree4 and one-overlapping-group edges, all four own-label counts sum4 and full99 caps bound each by1, so quota violations also violate a cap. The native parsers separately enforce the exact own-label equalities.",
                new_positive_numerical_runs=0,elapsed_seconds=time.perf_counter()-start,
                scope="Input rejection/immutability controls only. Matvec and numerical iteration agreement have separate positive audits. No convergence, exclusion or completion claim.")
    with (args.out/"report.json").open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({name:report[name] for name in ("status","negative_cases_per_tool","negative_invocations","elapsed_seconds")}))


if __name__=="__main__":
    main()
