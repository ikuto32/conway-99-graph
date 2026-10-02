"""Immutable exact revision binding for completed conditional independent audit."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR="acceleration/results/20261002_independent_review/rooted6_prismfree02"
REPORT=DIR+"/summary.json"
REPORT_SHA="f7e8f93a671648cd0e73c326a36ee8cc97682a2c568ed88f46044cb04abd4717"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report["status"]=="INDEPENDENT_CONDITIONAL_PRISMFREE_ROOTED6_EDGE_RIGIDITY_PASS"
    assert report["verifier"]=="/root/checkpoint_audit" and report["producer"]=="/root/structural"
    assert report["target_resolution"] is False and report["new_exclusions"]==0 and report["prismfree_premise_established"] is False
    now=datetime.now(timezone.utc).isoformat()
    inputs=dict(report["inputs_sha256"])
    inputs[REPORT]=REPORT_SHA
    binding=dict(id="C-PRISMFREE-ORDERED-EDGE-ROOTED6-RIGIDITY",revision=1,
        kind="mathematical result",basis=["DERIVED","COMPUTED"],status="VERIFIED",review_state="CLEAR",
        statement=report["statement"],scope=dict(description=report["scope"],unrestricted_target=False,target_resolution="NONE"),
        assumptions=["A hypothetical complete99-vertex symmetric binary adjacency matrix has zero diagonal and satisfies A^2=12I-A+2J exactly over integers.",
            "The hypothetical target has no induced triangular prism; this premise is UNKNOWN and is not established by this theorem.",
            "Roots are actual ordered adjacent vertices fixed pointwise; only free labels are identified in rooted flag coordinates."],
        dependencies=[],dependency_reason="Independent necessary row derivation from target definition and explicit conditional prism-zero assumptions; no imported mathematical result is a premise.",
        premise_state=dict(no_induced_triangular_prism="UNKNOWN",reason="No unrestricted proof of this premise is supplied."),
        verifier=report["verifier"],producer=report["producer"],method=report["method"],claim_revision=1,
        created_at=now,updated_at=now,verification_timestamp=report["timestamp"],source_commit=report["source_commit"],
        command=report["command"],cwd=report["cwd"],python=report["python"],inputs_sha256=inputs,
        report=REPORT,report_sha256=REPORT_SHA,controls=report["controls"],shared_components=report["shared_components"],
        limitations=report["limitations"],artifact_availability="LOCAL_ONLY",
        retrieval="Exact workspace paths in inputs_sha256; public availability and external review not established.",
        binding_creation=dict(script=Path(__file__).relative_to(ROOT).as_posix(),sha256=sha(Path(__file__).relative_to(ROOT).as_posix()),scope="Revision bookkeeping only; no theorem broadening or mathematical replay."))
    target=DIR+"/claim_binding.json"
    with (ROOT/target).open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(binding,stream,indent=2)
        stream.write("\n")
    print(json.dumps(dict(path=target,sha256=sha(target),id=binding["id"],revision=1)))


if __name__=="__main__":main()
