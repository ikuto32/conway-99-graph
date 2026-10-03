"""Bind an already completed independent audit to one immutable claim revision.

This is bookkeeping only. It does not rerun or broaden the mathematical audit.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = "acceleration/results/20261002_independent_review/rooted5_rigidity02"
REPORT = f"{AUDIT}/summary.json"
REPORT_HASH = "4edccc52f486e6517e1cd00003491c02d2404af09328a1449e5552c4a232f01f"


def digest(path: str) -> str:
    h = hashlib.sha256()
    with (ROOT / path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    assert digest(REPORT) == REPORT_HASH
    report = json.loads((ROOT / REPORT).read_text(encoding="utf-8"))
    assert report["status"] == "INDEPENDENT_ROOTED5_RIGIDITY_AND_EXPLICIT_MOMENTS_PASS"
    assert report["method"] == "independent_derivation"
    assert report["verifier"] == "/root/checkpoint_audit"
    assert report["target_resolution"] is False and report["new_exclusions"] == 0
    now = datetime.now(timezone.utc).isoformat()
    evidence = dict(report["inputs_sha256"])
    evidence[REPORT] = REPORT_HASH
    for name in ("ordered_edge_audit.json", "ordered_nonedge_audit.json"):
        path = f"{AUDIT}/{name}"
        evidence[path] = digest(path)
    binding_source = "acceleration/record_20261002_rooted5_binding_v1.py"
    binding = {
        "id": "C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY",
        "revision": 1,
        "kind": "mathematical result",
        "basis": ["DERIVED", "COMPUTED"],
        "status": "VERIFIED",
        "review_state": "CLEAR",
        "statement": report["statement"],
        "scope": {
            "description": "Universal necessary conditional statistics for every actual ordered root in any hypothetical srg(99,14,1,2), including the complete saved five-flag vectors and explicitly defined actual-root second moments.",
            "unrestricted_target": True,
            "target_resolution": "NONE",
        },
        "assumptions": [
            "A hypothetical complete 99-vertex symmetric binary adjacency matrix has zero diagonal and satisfies A^2 = 12I - A + 2J exactly over the integers.",
            "Rooted flags fix the two ordered roots pointwise and identify only permutations of their free vertices.",
            "The moment M is the sum of actual ordered-root extension-count outer products, as stated in the audited theorem.",
        ],
        "dependencies": [],
        "dependency_reason": "The finite necessity derivation independently reconstructs all rooted bases and rows from the target definition; saved artifacts are checked objects rather than assumed mathematical results.",
        "verifier": report["verifier"],
        "producer": report["producer"],
        "method": report["method"],
        "claim_revision": 1,
        "created_at": now,
        "updated_at": now,
        "verification_timestamp": report["timestamp"],
        "source_commit": report["source_commit"],
        "command": report["command"],
        "cwd": report["cwd"],
        "python": report["python"],
        "inputs_sha256": evidence,
        "report": REPORT,
        "report_sha256": REPORT_HASH,
        "controls": {family["family"]: family["controls"] for family in report["families"]},
        "shared_components": report["shared_components"],
        "limitations": report["limitations"],
        "artifact_availability": "LOCAL_ONLY",
        "retrieval": "Repository workspace paths in inputs_sha256; public availability is not established by this binding.",
        "binding_creation": {
            "script": binding_source,
            "sha256": digest(binding_source),
            "scope": "Identity and revision bookkeeping only; no additional derivation, proof checking or broader claim promotion.",
        },
    }
    target = ROOT / AUDIT / "claim_binding.json"
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(binding, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"path": target.relative_to(ROOT).as_posix(), "sha256": digest(target.relative_to(ROOT).as_posix()), "id": binding["id"], "revision": 1, "created_at": now}))


if __name__ == "__main__":
    main()
