"""Independent archive reconstruction and counterfactual replay of two traces."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/"external_conway99_research"
PIN = "85e705cc6c2a14d123120c93a847e30aaab1789e"
OUT = ROOT/"acceleration/results/20260930_independent_review/triangle_q1_partial99"
PROOF = "docs/AUDIT_20260930_TRIANGLE_Q1_PARTIAL99_PROPAGATION.md"
RAW = "acceleration/results/20260930_triangle_partial99/"
PRE = "acceleration/results/20260930_triangle_factor_preflight/"
PINS = {
    RAW+"wave151.json": "688b0255760a57a4cdd39e1ea471a784e3771a13c6fd3a6eb8b3615a7c43f063",
    RAW+"wave154.json": "e8581587313cf8207799dcf781d8469eb66a699687e023faf0a435000ab9f69b",
    PRE+"wave151.json": "78a545bac3af151c6107212f9975c8adceff21b0392cddd44d9e3dc376f32c88",
    PRE+"wave154.json": "de46520f9c24546c8b7f64987d71bbfcb0cb5992e44eddf53bcec51f4e038460",
}


def need(test, message):
    if not test: raise ValueError(message)


def digest(path):
    with Path(path).open("rb") as stream: return hashlib.file_digest(stream,"sha256").hexdigest()


def matrix_hash(matrix):
    return hashlib.sha256(json.dumps(matrix,separators=(",", ":")).encode()).hexdigest()


def matrix_ok(a):
    n = len(a)
    need(n and all(type(row) is list and len(row) == n for row in a), "square partial matrix")
    need(all(type(a[i][j]) is int and a[i][j] in (-1,0,1) and a[i][j] == a[j][i]
             and (i != j or a[i][j] == 0) for i in range(n) for j in range(n)), "partial binary symmetry/diagonal")


def row_interval(a, u):
    return sum(x == 1 for x in a[u]), sum(x != 0 for x in a[u])


def pair_interval(a, u, v):
    known = {w for w in range(len(a)) if a[u][w] == 1 and a[v][w] == 1}
    possible = {w for w in range(len(a)) if a[u][w] != 0 and a[v][w] != 0}
    return len(known), len(possible)


def check_step(a, step, k=14, lam=1, mu=2):
    edge, value, rule, witness = step["edge"], step["value"], step["rule"], step["witness"]
    need(len(edge) == 2 and all(type(x) is int for x in edge), "edge format")
    x,y = edge
    need(0 <= x < y < len(a) and a[x][y] == a[y][x] == -1, "forced edge is currently unknown")
    need(type(value) is int and value in (0,1), "forced value")
    contrary = deepcopy(a); contrary[x][y] = contrary[y][x] = 1-value
    if rule == "degree_bound":
        u = witness["vertex"]
        need(u in edge and witness["required"] == k, "degree witness")
        lower,upper = row_interval(a,u)
        need(lower <= k <= upper, "original degree interval")
        need((value == 0 and lower == k) or (value == 1 and upper == k), "degree tightness")
        bad_lower,bad_upper = row_interval(contrary,u)
        required = k
    else:
        u,v = witness["pair"]
        need(type(u) is int and type(v) is int and 0 <= u < v < len(a), "pair witness")
        lower,upper = pair_interval(a,u,v)
        if rule == "adjacency_from_common_interval":
            need(edge == [u,v], "adjacency witness is edge itself")
            feasible = [b for b,target in ((0,mu),(1,lam)) if lower <= target <= upper]
            need(feasible == [value], "unique adjacency choice")
            required = lam if contrary[u][v] else mu
        else:
            need(a[u][v] in (0,1), "fixed witness pair")
            required = lam if a[u][v] else mu
            need(lower <= required <= upper, "original pair interval")
            w = witness["center"]
            need(type(w) is int and 0 <= w < len(a) and w not in (u,v), "wedge center")
            need(set(edge) in ({u,w},{v,w}), "forced edge lies in witness wedge")
            other = v if u in edge else u
            if rule == "common_lower_tight":
                need(value == 0 and lower == required and a[other][w] == 1, "lower-tight one/unknown wedge")
            elif rule == "common_upper_tight":
                need(value == 1 and upper == required and a[other][w] != 0, "upper-tight possible wedge")
            else: raise ValueError("unknown rule")
        bad_lower,bad_upper = pair_interval(contrary,u,v)
    need(not bad_lower <= required <= bad_upper, "opposite value must contradict named constraint")
    return dict(edge=edge,value=value,rule=rule,original_interval=[lower,upper],
                opposite_interval=[bad_lower,bad_upper],required_after_opposite=required)


def scan(a,k=14,lam=1,mu=2):
    """Enumerate possible forces without changing the matrix or scan state."""
    matrix_ok(a)
    forces = set()
    for u in range(len(a)):
        low,high = row_interval(a,u)
        need(low <= k <= high, "degree contradiction")
        for v in range(len(a)):
            if a[u][v] == -1:
                if low == k: forces.add((min(u,v),max(u,v),0))
                if high == k: forces.add((min(u,v),max(u,v),1))
    for u,v in combinations(range(len(a)),2):
        low,high = pair_interval(a,u,v)
        if a[u][v] == -1:
            feasible = [b for b,target in ((0,mu),(1,lam)) if low <= target <= high]
            need(feasible, "no adjacency status possible")
            if len(feasible) == 1: forces.add((u,v,feasible[0]))
            continue
        target = lam if a[u][v] else mu
        need(low <= target <= high, "pair interval contradiction")
        for w in range(len(a)):
            if a[u][w] == 0 or a[v][w] == 0: continue
            if low == target:
                if a[u][w] == -1 and a[v][w] == 1: forces.add((min(u,w),max(u,w),0))
                if a[v][w] == -1 and a[u][w] == 1: forces.add((min(v,w),max(v,w),0))
            if high == target:
                if a[u][w] == -1: forces.add((min(u,w),max(u,w),1))
                if a[v][w] == -1: forces.add((min(v,w),max(v,w),1))
    return forces


def initial_from_blocks(q1):
    universe = list(p for p in combinations(range(12),2) if p[1] != (p[0]^1))
    need(sorted(q1) == list(range(60)), "archive Q1 permutation")
    tags = [("T",i) for i in range(3)]+[("A",i,u) for i in range(3) for u in range(12)]+[("B",d) for d in range(60)]
    def entry(x,y):
        if x == y: return 0
        if x[0] == "T":
            return int(y[0] == "T" or (y[0] == "A" and x[1] == y[1]))
        if x[0] == "A" and y[0] == "A":
            _,i,u = x; _,j,v = y
            if i == j: return int(v == (u^1))
            return int(v == ((u+6)%12 if (i,j) == (1,2) else u))
        if x[0] == "A" and y[0] == "B":
            _,i,u = x; d = y[1]
            return -1 if i == 2 else int(u in universe[d if i == 0 else q1[d]])
        need(x[0] == y[0] == "B", "tagged pair coverage")
        return -1
    a = [[0]*99 for _ in range(99)]
    for u,v in combinations(range(99),2): a[u][v] = a[v][u] = entry(tags[u],tags[v])
    matrix_ok(a)
    return a,universe


def replay(initial, artifact):
    need(artifact["initial_adjacency"] == initial, "every initial matrix entry")
    matrix_ok(initial); scan(initial)
    current = deepcopy(initial); checked = []
    for index,step in enumerate(artifact["steps"]):
        result = check_step(current,step)
        checked.append(dict(index=index,**result))
        u,v = step["edge"]; current[u][v] = current[v][u] = step["value"]
    need(current == artifact["final_adjacency"], "entire final matrix equals ordered replay")
    pending = scan(current)
    need(not pending and artifact["status"] == "FIXED_POINT_UNKNOWN", "fixed point for declared rule set")
    need(artifact["failure"] is None, "no contradiction claimed")
    unknown = [(u,v) for u,v in combinations(range(99),2) if current[u][v] == -1]
    c2 = sum(u in range(27,39) and v in range(39,99) for u,v in unknown)
    d = sum(u >= 39 for u,v in unknown)
    need(len(unknown) == artifact["remaining_unknown_edges"] == c2+d, "remaining complete edge count")
    need(c2 == artifact["remaining_C2_unknown"] and d == artifact["remaining_D_unknown"], "remaining block counts")
    need(artifact["initial_unknown_edges"] == sum(initial[u][v] == -1 for u,v in combinations(range(99),2)) == 2490, "initial unknown count")
    need(len(checked)+len(unknown) == 2490, "one fresh assignment per step")
    return current,checked,dict(remaining_unknown_edges=len(unknown),remaining_C2=c2,remaining_D=d,
                              final_fixedpoint_rules=0,initial_matrix_sha256=matrix_hash(initial),final_matrix_sha256=matrix_hash(current))


def controls():
    c5 = [[int((i-j)%5 in (1,4)) for j in range(5)] for i in range(5)]
    pairs = list(combinations(range(5),2))
    petersen = [[int(set(a).isdisjoint(b)) for b in pairs] for a in pairs]
    rook9 = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    known = []
    for name,a,k,lam,mu in (("C5",c5,2,0,1),("Petersen",petersen,3,0,1),("rook9",rook9,4,1,2)):
        need(not scan(a,k,lam,mu), "known complete SRG")
        for edge in ([0,1],[0,2]):
            u,v = edge; value = a[u][v]; masked = deepcopy(a); masked[u][v] = masked[v][u] = -1
            check_step(masked,dict(edge=edge,value=value,rule="degree_bound",witness=dict(vertex=u,required=k)),k,lam,mu)
        known.append(name)
    positive_steps = []
    for edge,value,rule,witness in [([0,1],1,"adjacency_from_common_interval",dict(pair=[0,1])),
                                   ([0,2],0,"adjacency_from_common_interval",dict(pair=[0,2])),
                                   ([0,2],0,"common_lower_tight",dict(pair=[0,1],center=2)),
                                   ([0,1],1,"common_upper_tight",dict(pair=[0,2],center=1))]:
        masked = deepcopy(c5);u,v=edge;masked[u][v]=masked[v][u]=-1
        step = dict(edge=edge,value=value,rule=rule,witness=witness)
        positive_steps.append(check_step(masked,step,2,0,1))
    rejected = {}
    def reject(name,call):
        try: call()
        except ValueError as error: rejected[name]=str(error)
        else: raise ValueError("corruption accepted: "+name)
    masked=deepcopy(c5);masked[0][1]=masked[1][0]=-1
    good=dict(edge=[0,1],value=1,rule="common_upper_tight",witness=dict(pair=[0,2],center=1))
    bad=deepcopy(good);bad["value"]=0
    reject("wrong_forced_value",lambda:check_step(masked,bad,2,0,1))
    reject("already_fixed_edge",lambda:check_step(c5,good,2,0,1))
    bad=deepcopy(good);bad["witness"]["pair"]=[2,3]
    reject("unrelated_witness",lambda:check_step(masked,bad,2,0,1))
    bad=deepcopy(c5);bad[0][1]=bad[1][0]=0
    reject("corrupt_complete_SRG",lambda:scan(bad,2,0,1))
    empty=[[0 if i==j else -1 for j in range(5)] for i in range(5)]
    reject("unjustified_force",lambda:check_step(empty,dict(edge=[0,1],value=1,rule="degree_bound",witness=dict(vertex=0,required=2)),2,0,1))
    return dict(known_valid_SRGs=known,masked_degree_positive_steps=6,other_rule_positive_steps=positive_steps,corruptions_rejected=rejected)


def main():
    need(not OUT.exists(),"refuse overwrite")
    bindings={}; archive_records=[]
    def bind(path,expected=None):
        p=Path(path)
        if not p.is_absolute():p=ROOT/p
        sha=digest(p);need(expected is None or sha==expected,"input hash: "+str(path))
        bindings[p.relative_to(ROOT).as_posix()]=sha
        return p
    def read(path,expected=None):return json.loads(bind(path,expected).read_text(encoding="utf-8"))
    raw={case:read(RAW+case+".json",PINS[RAW+case+".json"]) for case in ("wave151","wave154")}
    pre={case:read(PRE+case+".json",PINS[PRE+case+".json"]) for case in raw}
    manifest=read(RAW+"manifest.json")
    for path,sha in manifest["inputs_sha256"].items():bind(path,sha)
    stored={}
    for wave,folder in (("wave149","wave149-terwilliger-triple"),("wave151","wave151-triangle-root-factor"),("wave154","wave154-triangle-factor-portfolio")):
        path="attempts/"+folder+"/exact-results.json"
        command=["git","-C",str(ARCHIVE),"show",PIN+":"+path]
        content=subprocess.check_output(command)
        sha=hashlib.sha256(content).hexdigest();bind(ARCHIVE/path,sha)
        stored[wave]=json.loads(content)
        archive_records.append(dict(repository="https://github.com/YesterdaysLemon/conway-99-research",commit=PIN,path=path,sha256=sha,command=command))
    witness=stored["wave149"]["minimal_surviving_witness"]
    need(witness["M0_M1_M2_permutation"] == [i^1 for i in range(12)],"exact frozen matching")
    need(witness["F01_permutation"] == witness["F02_permutation"] == list(range(12)),"exact identity cross factors")
    need(witness["F12_permutation"] == [(i+6)%12 for i in range(12)],"exact frozen third factor")
    calibrated=controls();results=[];step_certificates={}
    for case,key in (("wave151","exact_partial_factor"),("wave154","second_exact_Q1_representative")):
        q1=stored[case][key]["Q1"]
        initial,universe=initial_from_blocks(q1)
        need(pre[case]["Q1"] == q1 and pre[case]["edge_universe"] == [list(e) for e in universe],"raw preflight permutation/edge universe")
        need(pre[case]["C01"] == [row[39:] for row in initial[3:27]],"raw preflight all C01 entries")
        final,steps,counts=replay(initial,raw[case])
        rule_counts=Counter((x["rule"],x["value"]) for x in steps)
        results.append(dict(case=case,propagation_artifact=RAW+case+".json",propagation_sha256=PINS[RAW+case+".json"],
            archive_Q1_source=next(x for x in archive_records if case in x["path"]),archive_Q1_key=key+".Q1",
            forced_entries=len(steps),forced_zero_count=sum(x["value"]==0 for x in steps),forced_one_count=sum(x["value"]==1 for x in steps),
            rule_counts=[dict(rule=r,value=v,count=n) for (r,v),n in sorted(rule_counts.items())],
            ordered_steps_counterfactually_checked=len(steps),initial_unknown_edges=2490,status="FIXED_POINT_UNKNOWN",**counts))
        step_certificates[case]=steps
    # Additional controls against the actual complete trace and raw assembly.
    case="wave154";q1=stored[case]["second_exact_Q1_representative"]["Q1"];initial,_=initial_from_blocks(q1)
    failures={}
    for label in ("missing_step","changed_final_entry","changed_initial_entry","wrong_step_value"):
        bad=deepcopy(raw[case])
        if label=="missing_step":bad["steps"].pop()
        elif label=="changed_final_entry":u,v=bad["steps"][-1]["edge"];bad["final_adjacency"][u][v]=bad["final_adjacency"][v][u]=-1
        elif label=="changed_initial_entry":bad["initial_adjacency"][0][1]=bad["initial_adjacency"][1][0]=0
        else:bad["steps"][0]["value"]=1
        try:replay(initial,bad)
        except ValueError as error:failures[label]=str(error)
        else:raise ValueError("actual trace corruption accepted")
    OUT.mkdir(parents=True,exist_ok=False)
    for case,steps in step_certificates.items():
        path=OUT/(case+"_counterfactual_steps.json")
        with path.open("x",encoding="utf-8") as stream:json.dump(steps,stream,indent=2);stream.write("\n")
        bind(path)
    bind(PROOF);bind(__file__);bind(RAW+"summary.json")
    report=dict(status="INDEPENDENT_TRIANGLE_Q1_PARTIAL99_PROPAGATION_PASS",timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],
        working_directory=str(Path.cwd()),python=platform.python_version(),verifier="/root/state_literature_audit independent archive/matrix/trace checker",
        claim_id="C-TRIANGLE-FIXED-Q1-PARTIAL99-PROPAGATION",claim_revision=1,recommendation="VERIFIED",review_state="CLEAR",kind="mathematical result",basis=["DERIVED","COMPUTED"],
        statement="For each of the exact wave151 and wave154 starting99x99 partial adjacency matrices reconstructed from the pinned archive factors, every recorded zero assignment is forced by the target degree/common-neighbor equalities. Their recorded final matrices have exactly the same target completions as their initial matrices and are fixed points of the four declared interval rules, with1928 and1927unknown unordered entries respectively.",
        scope="Only two exact fixed triangle-root M/F/Q1 configurations. A fixed point does not establish feasibility, exclude the family, or supply unrestricted target coverage.",
        assumptions=["Symmetric binary zero-diagonal99vertex target satisfying A^2=12I-A+2J and extending the indicated fixed initial entries.",
                     "Exact archived M/F/Q1 values define each conditional case; no target automorphism, asymmetry, or universal occurrence of either configuration is assumed."],
        dependencies=[],dependency_null_reason="These two conditional propagation implications follow directly from the defining target equation and exact fixed entries. Archive files identify the cases; archived mathematical status labels are not premises.",
        inputs_sha256=bindings,archive_sources=archive_records,written_audit=PROOF,results=results,
        matrix_hash_serialization="UTF-8 compact JSON array of integer rows, separators comma/colon, no trailing newline",
        controls=dict(generic=calibrated,actual_trace_corruptions_rejected=failures),producer_imported=False,
        shared_components=["Python standard library integer arithmetic, JSON and SHA256", "Git immutable blob lookup"],
        limitations=["No historical VERIFIED or untraced UNSAT assertion was promoted; the specified factors and every saved inference were checked afresh.",
                     "Preflight modular/GF2 consistency results, Gram ranks, archive orbit census and whole-family coverage are not audited here.",
                     "No solver run, target graph, conditional UNSAT proof, or unrestricted nonexistence claim.",
                     "The historical producer rounds field is not independently reproduced; fixed-point status is established by a separate final rule scan."],
        solver_calls=0,target_resolution=False,external_review=False,artifact_availability="LOCAL_ONLY")
    need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),"bound inputs stable")
    with (OUT/"summary.json").open("x",encoding="utf-8") as stream:json.dump(report,stream,indent=2);stream.write("\n")
    print(json.dumps(dict(status=report["status"],sha256=digest(OUT/"summary.json"),results=results),indent=2))


if __name__=="__main__":main()
