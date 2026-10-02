"""Bind the completed independent finite catalogue check, without model approval."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR="acceleration/results/20261002_independent_review/rooted7_catalogue01"
REPORT=DIR+"/summary.json"
REPORT_SHA="3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758"


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    assert sha(REPORT)==REPORT_SHA
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report["status"]=="INDEPENDENT_COMPLETE_ROOTED7_CATALOGUE_COVERAGE_PASS"
    assert report["all_labelled_masks_of_fixed_nonedge"]==1048576 and report["complete_rooted_classes"]==2770 and report["conditional_prismfree_classes"]==2750
    assert report["target_resolution"] is False and report["new_exclusions"]==0
    inputs=dict(report["inputs_sha256"]);inputs[REPORT]=REPORT_SHA
    now=datetime.now(timezone.utc).isoformat();source=Path(__file__).relative_to(ROOT).as_posix()
    binding=dict(id="C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE",revision=1,claim_revision=1,
        kind="encoding",basis=["DERIVED","COMPUTED"],status="VERIFIED",review_state="CLEAR",statement=report["statement"],
        scope=dict(description=report["scope"]+" The prism-free subcatalogue is applicable to a target only conditional on that unestablished premise.",unrestricted_target=True,target_resolution="NONE"),
        assumptions=["Finite simple labelled seven-vertex graphs with fixed ordered nonadjacent roots obey the local adjacent/nonadjacent common-neighbor caps1/2.",
            "Only permutations of the five free labels define the catalogue coordinates; no automorphism of a hypothetical target is assumed.",
            "The2750-class subcatalogue uses the explicit no-induced-triangular-prism predicate; this predicate is not proved for an unrestricted target."],
        dependencies=[],dependency_reason="Independent full labelled-mask exhaustion, without the producer's rooted6 augmentation or imported catalogue completeness premise.",
        premise_state=dict(no_induced_triangular_prism="UNKNOWN",reason="Only subcatalogue membership is verified; no unrestricted target premise is established."),
        verifier=report["verifier"],producer=report["producer"],method=report["method"],created_at=now,updated_at=now,
        verification_timestamp=report["timestamp"],source_commit=report["source_commit"],command=report["command"],cwd=report["cwd"],python=report["python"],
        inputs_sha256=inputs,report=REPORT,report_sha256=REPORT_SHA,controls=report["controls"],shared_components=report["shared_components"],limitations=report["limitations"],
        artifact_availability="LOCAL_ONLY",retrieval="Exact workspace inputs_sha256 paths; public retrieval/external review not established.",
        binding_creation=dict(script=source,sha256=sha(source),scope="Revision bookkeeping only; no marked/reroot model, LP or target approval."))
    target=DIR+"/claim_binding.json"
    with (ROOT/target).open("x",encoding="utf-8",newline="\n") as stream:json.dump(binding,stream,indent=2);stream.write("\n")
    print(json.dumps(dict(path=target,sha256=sha(target),id=binding["id"],revision=1)))


if __name__=="__main__":main()
