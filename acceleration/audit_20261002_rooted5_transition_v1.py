"""Independent read-only exact single-claim registry transition audit."""
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from audit_20261002_wave31_transition_v1 import UniqueLoader, indexed, need
import yaml

ROOT = Path(__file__).resolve().parents[1]
REG = "acceleration/results/20261002_rooted5_registration01"
BEFORE_SHA = "e55403664288e5595316b07a2772735a35dd4de1503239992e7ca7d496c9c423"
BIND = "acceleration/results/20261002_independent_review/rooted5_rigidity02/claim_binding.json"
BIND_SHA = "9a14b7f1a4af1b0dcbc52cd2bfb71c477e98f6ea95b82017e6fc7a9f657e507a"
REPORT_SHA = "4edccc52f486e6517e1cd00003491c02d2404af09328a1449e5552c4a232f01f"
CID = "C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY"


def check(old, current, binding):
    previous, now = indexed(old["claims"]), indexed(current["claims"])
    need(len(previous) == 312 and set(now) == set(previous) | {CID}, "exact new ID without old deletion")
    need(all(previous[cid] == now[cid] for cid in previous), "every previous claim preserved")
    old_artifacts, artifacts = indexed(old["artifacts"]), indexed(current["artifacts"])
    need(all(artifacts[aid] == record for aid, record in old_artifacts.items()), "every previous artifact preserved")
    for field in set(old) | set(current):
        if field not in {"claims", "artifacts", "updated_at"}:
            need(old[field] == current[field], "all other semantics preserved: " + field)
    claim = now[CID]
    for field in ["id", "revision", "statement", "kind", "basis", "status", "review_state", "scope", "assumptions", "dependencies", "limitations"]:
        need(claim[field] == binding[field], "exact independently bound field: " + field)
    need(claim["scope"]["unrestricted_target"] is True and claim["scope"]["target_resolution"] == "NONE", "unrestricted necessary conditional theorem only")
    need(claim["kind"] == "mathematical result" and claim["dependencies"] == [], "no mathematical exclusion or imported premise")
    need(len(claim["verification"]) == 1, "one exact verification binding")
    verification = claim["verification"][0]
    for field, value in {"claim_revision": 1, "verifier": "/root/checkpoint_audit", "method": "independent_derivation", "outcome": "PASS", "command_or_audit": binding["report"], "timestamp": binding["verification_timestamp"], "scope": binding["scope"]["description"]}.items():
        need(verification[field] == value, "exact checking record: " + field)
    need(verification["verifier"] != binding["producer"], "discovery does not approve itself")
    need(verification["limitations"] == binding["limitations"] and verification["shared_components"] == binding["shared_components"], "checking limitations preserved")
    need(set(claim["evidence"]) == set(artifacts) - set(old_artifacts), "all and only new artifacts serve exact new claim")
    need(all(artifacts[aid]["availability"] == "LOCAL_ONLY" for aid in claim["evidence"]), "public availability not invented")
    need(set(verification["artifact_hashes"]) == set(claim["evidence"]), "all new evidence hashes bound to r1")
    need(current["target"]["status"] == "UNKNOWN" and current["target"]["overall_search_coverage"] is None, "no target or coverage promotion")
    return claim, artifacts


def main():
    pins = {}
    def pin(path, wanted=None):
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        need(wanted is None or actual == wanted, "exact bytes: " + path)
        pins[path] = actual
        return actual
    pin(f"{REG}/CLAIMS.before.yaml", BEFORE_SHA)
    pin("CLAIMS.yaml")
    pin(f"{REG}/CLAIMS.after.yaml", pins["CLAIMS.yaml"])
    pin(BIND, BIND_SHA)
    binding = json.loads((ROOT / BIND).read_bytes())
    pin(binding["report"], REPORT_SHA)
    report = json.loads((ROOT / binding["report"]).read_bytes())
    need(binding["statement"] == report["statement"] and report["target_resolution"] is False and report["new_exclusions"] == 0, "exact completed theorem scope")
    old = yaml.load((ROOT / f"{REG}/CLAIMS.before.yaml").read_text(encoding="utf-8"), Loader=UniqueLoader)
    current = yaml.load((ROOT / "CLAIMS.yaml").read_text(encoding="utf-8"), Loader=UniqueLoader)
    claim, artifacts = check(old, current, binding)
    for aid in claim["evidence"]:
        artifact = artifacts[aid]
        pin(artifact["path"], artifact["sha256"])
        need(claim["verification"][0]["artifact_hashes"][aid] == artifact["sha256"], "recorded evidence identity")
        need(artifact["path"] == BIND or binding["inputs_sha256"].get(artifact["path"]) == artifact["sha256"], "new evidence inside immutable independent checking closure")
    rejected = []
    for label, mutate in [
        ("old_statement_changed", lambda value: value["claims"][0].update(statement="changed")),
        ("broader_resolution", lambda value: value["claims"][-1]["scope"].update(target_resolution="NONEXISTENCE")),
        ("discovery_self_approval", lambda value: value["claims"][-1]["verification"][0].update(verifier="/root/structural")),
    ]:
        damaged = copy.deepcopy(current)
        mutate(damaged)
        try:
            check(old, damaged, binding)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("corruption accepted: " + label)
    pin(Path(__file__).relative_to(ROOT).as_posix())
    pin("acceleration/audit_20261002_wave31_transition_v1.py")
    pin("uv.lock")
    counts = Counter(c["status"] for c in current["claims"] if c["review_state"] == "CLEAR")
    out = ROOT / "acceleration/results/20261002_independent_review/rooted5_transition01"
    out.mkdir(exist_ok=False)
    result = dict(status="INDEPENDENT_ROOTED5_EXACT_LEDGER_TRANSITION_PASS",
        timestamp=datetime.now(timezone.utc).isoformat(), verifier="/root/checkpoint_audit",
        source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=pins,
        previous_claims=312, current_claims=313, current_clear_status_counts=dict(counts),
        unchanged_previous_claims=312, new_claim_id=CID, revision=1,
        new_exclusions=0, target_resolution="UNKNOWN", overall_search_coverage="UNKNOWN; no validated denominator.",
        corrupted_controls_rejected=rejected, mathematical_replays=0,
        scope="Exact registry transition and immutable evidence identity only; prior complete independent mathematical derivation is preserved.",
        shared_components=["Strict duplicate-key YAML loader and ID indexing from this verifier's earlier transition audit; no registrar imported or executed.", "PyYAML/Python and locked environment."],
        limitations=["No mathematical replay or external review is performed by this metadata audit."], artifact_availability="LOCAL_ONLY")
    with (out / "summary.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(path=(out / "summary.json").relative_to(ROOT).as_posix(), sha256=hashlib.sha256((out / "summary.json").read_bytes()).hexdigest(), status=result["status"])))


if __name__ == "__main__":
    main()
