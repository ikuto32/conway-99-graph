"""Independent read-only313->315->317 exact binding and scope transition audit."""
from collections import Counter
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed,need

ROOT=Path(__file__).resolve().parents[1]
R1="acceleration/results/20261002_wave32_registration01"
R2="acceleration/results/20261002_wave32_registration02"
BINDINGS={
    "C-UNRESTRICTED-PARTIAL-DRAT-CANDIDATE-STATE-TRANSFORM":("acceleration/results/20261002_drat_restart_artifact_audit01/claim_binding.json","a666194859ed3d885a5921d535321b06bab4881f50eda7269dc3b7ab342e96d1"),
    "C-PRISMFREE-ORDERED-EDGE-ROOTED6-RIGIDITY":("acceleration/results/20261002_independent_review/rooted6_prismfree02/claim_binding.json","4796347924350b025eb463b0f28a3c42cc9f00fb91b81e803af31668b1bf9b2f"),
    "C-UNRESTRICTED-ROOTED6-NONEDGE-NECESSARY-SYSTEM-NULLSPACE":("acceleration/results/20261002_independent_review/rooted6_nonedge_domain01/nullspace_claim_binding.json","d1d98cc87c9320dab95442c77826abe3071bf40bbc4691b01c3f2f4199dec3e8"),
    "C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN":("acceleration/results/20261002_independent_review/rooted6_nonedge_domain01/integer_domain_claim_binding.json","0569ea768ae8ef2389667446cc4544cfd8c8f3e90f3d20d417c6fdab03ced653"),
}
NONEDGE_REPORT="65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271"


def transition(before,after,wanted,bindings):
    old,new=indexed(before["claims"]),indexed(after["claims"])
    need(set(new)-set(old)==set(wanted) and set(old)<=set(new),"exact additions and no previous deletion")
    need(all(new[cid]==claim for cid,claim in old.items()),"all previous claim semantics unchanged")
    old_artifacts,artifacts=indexed(before["artifacts"]),indexed(after["artifacts"])
    need(all(artifacts[aid]==record for aid,record in old_artifacts.items()),"all previous artifact records unchanged")
    for field in set(before)|set(after):
        if field not in {"claims","artifacts","updated_at"}:need(before[field]==after[field],"unchanged target/archive/schema/migration semantics")
    need(after["target"]["status"]=="UNKNOWN" and after["target"]["overall_search_coverage"] is None,"no target or coverage promotion")
    for cid in wanted:
        claim,binding=new[cid],bindings[cid]
        for field in ["id","revision","statement","kind","basis","status","review_state","assumptions","dependencies","limitations"]:
            need(claim[field]==binding[field],"exact frozen bound field: "+cid+":"+field)
        description=binding["scope"]["description"] if isinstance(binding["scope"],dict) else binding["scope"]
        need(claim["scope"]["description"]==description and claim["scope"]["target_resolution"]=="NONE","exact scoped non-resolution")
        if isinstance(binding["scope"],dict):need(claim["scope"]==binding["scope"],"complete unchanged bound scope")
        else:need(claim["scope"]["unrestricted_target"] is False,"syntactic transform has no unrestricted mathematical application")
        need(claim["status"]=="VERIFIED" and claim["review_state"]=="CLEAR" and claim["revision"]==1,"exact current approved revision")
        verification=claim["verification"]
        need(len(verification)==1 and verification[0]["verifier"]==binding["verifier"]!=binding["producer"]
            and verification[0]["claim_revision"]==1 and verification[0]["outcome"]=="PASS","separate exact-revision check")
        need(verification[0]["scope"]==description and verification[0]["limitations"]==binding["limitations"],"checking scope and limitations retained")
        for dep in claim["dependencies"]:need(dep["id"] in new and dep["revision"]==new[dep["id"]]["revision"],"exact dependency revision")
        need(set(verification[0]["artifact_hashes"])==set(claim["evidence"]),"every new evidence ID bound in verification")
        if cid.startswith("C-PRISMFREE-"):
            need(binding["premise_state"]["no_induced_triangular_prism"]=="UNKNOWN" and "UNKNOWN" in claim["unknowns"]["premises"],"prism absence remains unestablished")
    return old,new,artifacts


def main():
    pins={}
    def pin(name,wanted=None):
        path=ROOT/name
        with path.open("rb") as stream:actual=hashlib.file_digest(stream,"sha256").hexdigest()
        need(wanted is None or actual==wanted,"exact checked artifact identity: "+name);pins[name]=actual
    def load(name,wanted=None):pin(name,wanted);return json.loads((ROOT/name).read_bytes())
    one,two=load(R1+"/summary.json"),load(R2+"/summary.json")
    need(one["before_ledger_sha256"]=="284a49239cb8869fcbfc3c6a980a355e38172e4a2d8508a78ec60b8d3aa11be7","exact frozen313ledger")
    need(two["before_ledger_sha256"]==one["ledger_sha256"] and two["ledger_sha256"]=="44e119ac7e1952e1d0abde8d68f3556c8aec9f73ba6e470d3d24e8fddc781d56","frozen registration chain")
    names=[R1+"/CLAIMS.before.yaml",R1+"/CLAIMS.after.yaml",R2+"/CLAIMS.before.yaml",R2+"/CLAIMS.after.yaml"]
    hashes=[one["before_ledger_sha256"],one["ledger_sha256"],two["before_ledger_sha256"],two["ledger_sha256"]]
    snapshots=[]
    for name,wanted in zip(names,hashes):pin(name,wanted);snapshots.append(yaml.load((ROOT/name).read_text(encoding="utf-8"),Loader=UniqueLoader))
    need(snapshots[1]==snapshots[2],"chain snapshots identical")
    bindings={cid:load(path,digest) for cid,(path,digest) in BINDINGS.items()}
    need(set(one["new_claim_ids"])|set(two["new_claim_ids"])==set(BINDINGS),"exact four new material scopes")
    transition(snapshots[0],snapshots[1],one["new_claim_ids"],bindings)
    transition(snapshots[2],snapshots[3],two["new_claim_ids"],bindings)
    old,new,artifacts=transition(snapshots[0],snapshots[3],BINDINGS,bindings)
    need(len(old)==313 and len(new)==317,"complete313to317population")
    for cid,binding in bindings.items():
        claim=new[cid]
        if "verification_records" in binding:
            record=binding["verification_records"][0];report=load(record["audit_path"],record["audit_sha256"])
            need(report["complete_active_multiset_checked"] is True and report["complete_prefix_bytes_checked"] is True and report["variables_unchanged"] is True,"complete checked transform")
            need(report["rat_rup_checked"] is False and report["equisatisfiability_asserted"] is False and report["target_resolution"] is False,"no proof/equivalence promotion")
            need(all(value is False or value==0 for key,value in binding["mathematical_scope"].items() if key!="reason"),"all mathematical transformation claims remain unestablished")
            need(report["counters"]["active_clause_occurrences"]==3069024 and report["counters"]["trailing_dropped_bytes"]==36,"exact state counters")
        else:
            report=load(binding["report"],binding["report_sha256"])
            need(report["new_exclusions"]==0 and report["target_resolution"] is False,"no mathematical exclusion promotion")
            if cid=="C-PRISMFREE-ORDERED-EDGE-ROOTED6-RIGIDITY":need(report["statement"]==binding["statement"] and report["rank_over_Q"]==394 and report["prismfree_premise_established"] is False,"exact conditional edge theorem")
            else:
                need(binding["report_sha256"]==NONEDGE_REPORT and report["exact_rational_ranks"]==[564,565] and report["exact_nullities"]==[3,2]
                    and report["complete_integer_profiles"]==210 and report["conditional_count_axes"]==[[6,8024],[6,15540]],"two exact component statements supported by complete combined audit")
                need(report["graph_realizability_asserted"] is False and report["prismfree_premise_established"] is False,"nonedge domain is not realized graphs")
        for aid in claim["evidence"]:
            artifact=artifacts[aid];pin(artifact["path"],artifact["sha256"])
            need(claim["verification"][0]["artifact_hashes"][aid]==artifact["sha256"],"raw evidence exact verification binding")
    rejected=[]
    for label,mutate in [
        ("changed_prior_claim",lambda value:value["claims"][0].update(statement="changed")),
        ("broadened_target_resolution",lambda value:value["claims"][-1]["scope"].update(target_resolution="NONEXISTENCE")),
        ("unestablished_premise_promoted",lambda value:value["claims"][-1]["unknowns"].update(premises="VERIFIED")),
    ]:
        damaged=copy.deepcopy(snapshots[3]);mutate(damaged)
        try:transition(snapshots[0],damaged,BINDINGS,bindings)
        except ValueError:rejected.append(label)
        else:raise ValueError("damaged transition accepted")
    for name in [Path(__file__).relative_to(ROOT).as_posix(),"acceleration/audit_20261002_wave31_transition_v1.py","acceleration/register_20261002_bound_claims_v2.py","uv.lock"]:pin(name)
    result=dict(status="INDEPENDENT_WAVE32_EXACT313_TO317_TRANSITION_PASS",timestamp=datetime.now(timezone.utc).isoformat(),verifier="/root/checkpoint_audit",
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
        previous_claims=313,current_claims=317,unchanged_prior_claims=313,new_claim_ids=list(BINDINGS),current_clear_status_counts=dict(Counter(claim["status"] for claim in new.values() if claim["review_state"]=="CLEAR")),
        new_exclusions=0,target_resolution="UNKNOWN",overall_search_coverage="UNKNOWN; no validated denominator.",corrupted_controls_rejected=rejected,mathematical_replays=0,
        scope="Frozen exact ledger/evidence transition only; independently verified source-bound scientific statements remain within their stated scopes.",
        limitations=["No mathematical replay is repeated here.","No present live-ledger or remote publication state is inferred from frozen registration snapshots.","Derivative transformation remains syntactic; prism absence remains UNKNOWN and local domains establish no graphs."],artifact_availability="LOCAL_ONLY")
    out=ROOT/"acceleration/results/20261002_independent_review/wave32_transition01";out.mkdir(exist_ok=False)
    with (out/"summary.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(result,stream,indent=2);stream.write("\n")
    print(json.dumps(dict(path=(out/"summary.json").relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/"summary.json").read_bytes()).hexdigest())))


if __name__=="__main__":main()
