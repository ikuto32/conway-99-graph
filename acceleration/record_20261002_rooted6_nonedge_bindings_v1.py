"""Two immutable exact-revision bindings to one completed independent audit.

Component statements have different scopes and are therefore distinct claims.
No mathematical replay or scope broadening is performed by this bookkeeping.
"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR="acceleration/results/20261002_independent_review/rooted6_nonedge_domain01"
REPORT=DIR+"/summary.json"
REPORT_SHA="65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271"
FIRST="C-UNRESTRICTED-ROOTED6-NONEDGE-NECESSARY-SYSTEM-NULLSPACE"
SECOND="C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN"


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report["status"]=="INDEPENDENT_ROOTED6_NONEDGE_EXACT_NULLSPACES_AND_CONDITIONAL_DOMAIN_PASS"
    assert report["variables"]==567 and report["unrestricted_rows"]==1445 and report["conditional_rows"]==1446
    assert report["exact_rational_ranks"]==[564,565] and report["exact_nullities"]==[3,2] and report["complete_integer_profiles"]==210
    assert report["verifier"]=="/root/checkpoint_audit" and report["producer"]=="/root/structural"
    assert report["target_resolution"] is False and report["new_exclusions"]==0 and report["prismfree_premise_established"] is False
    inputs=dict(report["inputs_sha256"]);inputs[REPORT]=REPORT_SHA
    source=Path(__file__).relative_to(ROOT).as_posix()
    inputs["acceleration/audit_20261002_rooted6_nonedge_domain_v1_spec.md"]=sha("acceleration/audit_20261002_rooted6_nonedge_domain_v1_spec.md")
    now=datetime.now(timezone.utc).isoformat()
    common=dict(revision=1,claim_revision=1,kind="mathematical result",basis=["DERIVED","COMPUTED"],status="VERIFIED",review_state="CLEAR",
        verifier=report["verifier"],producer=report["producer"],method=report["method"],created_at=now,updated_at=now,
        verification_timestamp=report["timestamp"],source_commit=report["source_commit"],command=report["command"],cwd=report["cwd"],python=report["python"],
        inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,controls=report["controls"],shared_components=report["shared_components"],
        artifact_availability="LOCAL_ONLY",retrieval="Exact workspace inputs_sha256 paths; public availability/external review not established.",
        binding_creation=dict(script=source,sha256=sha(source),scope="Exact component revision bookkeeping only; no new mathematical replay."))
    first=dict(common,id=FIRST,
        statement="The exact independently reconstructed1445x567 integer coefficient operator for the complete locally admissible ordered-nonedge rooted-flag necessary system through order6 of srg(99,14,1,2) has rational rank564 and nullity3, with the complete saved three-vector rational kernel basis and corresponding primitive integer vectors.",
        scope=dict(description="Exact complete necessary local flag coefficient operator only; no theorem of graph realization or existence follows from its kernel.",unrestricted_target=True,target_resolution="NONE"),
        assumptions=["The rooted flag necessary system uses target parameters n99,k14,lambda1,mu2, exact degree/common-neighbor identities and complete locally admissible simple flags.",
            "Both ordered nonadjacent roots are fixed pointwise; only free labels are identified in the flag coordinates."],
        dependencies=[],dependency_reason="The operator is independently reconstructed from the parameter definition and exhaustive finite rooted bases; no imported result is required.",
        limitations=["The exact kernel describes a necessary linear operator, not a set of target graphs or a graph realization theorem.","No construction, exclusion, novelty or target-wide search coverage is established."])
    second=dict(common,id=SECOND,
        statement="For the complete567-coordinate ordered-nonedge rooted6 necessary row model of srg(99,14,1,2), adding its single triangular-prism coordinate zero gives a1446-row system of rational rank565/nullity2 whose entire nonnegative integer solution set is exactly the saved210full count profiles, parameterized by actual six-flag counts a(mask8024),b(mask15540) with0<=a<=20 and0<=b<=9.",
        scope=dict(description="Exact local necessary integer profile domain conditional on no induced triangular prism in a hypothetical target;210profiles are not210graphs and do not establish the premise or graph feasibility.",unrestricted_target=False,target_resolution="NONE"),
        assumptions=["The target parameter definition and complete ordered-nonedge rooted6 necessary operator recorded by the pinned first claim apply.",
            "A hypothetical target has no induced triangular prism; this premise is UNKNOWN and is not established by this result.",
            "Actual rooted extension counts are nonnegative integers; roots are fixed pointwise and no target automorphism is assumed."],
        dependencies=[dict(id=FIRST,revision=1,relation="uses_result")],
        premise_state=dict(no_induced_triangular_prism="UNKNOWN",reason="No unrestricted proof of this premise is supplied."),
        limitations=report["limitations"])
    for name,binding in [("nullspace_claim_binding.json",first),("integer_domain_claim_binding.json",second)]:
        path=DIR+"/"+name
        with (ROOT/path).open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(binding,stream,indent=2);stream.write("\n")
        print(json.dumps(dict(path=path,sha256=sha(path),id=binding["id"],revision=1)))


if __name__=="__main__":main()
