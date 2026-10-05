"""Record tooling tests and an unapplied dependency plan; never edit the ledger."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from validate_claims import canonical_claim_digest, read_ledger


ROOT = Path(__file__).resolve().parents[1]
REVIEW = Path("acceleration/results/20260930_independent_review/automorphism_assumption_editorial/summary.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="acceleration/results/20260930_editorial_migration_tooling/run01")
    args = parser.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=False)
    snapshot = out / "CLAIMS.unmodified.yaml"
    snapshot.write_bytes((ROOT / "CLAIMS.yaml").read_bytes())
    data = read_ledger(snapshot)
    review = json.loads((ROOT / REVIEW).read_text(encoding="utf-8"))
    claims = {c["id"]: c for c in data["claims"]}
    reviewed = {c["claim_id"]: c for c in review["records"]}
    selected = set(reviewed)
    affected = set(selected)
    while True:
        expanded = affected | {cid for cid, claim in claims.items()
                               if any(d["id"] in affected for d in claim["dependencies"])}
        if expanded == affected:
            break
        affected = expanded
    ancestors = set(selected)
    while True:
        expanded = ancestors | {d["id"] for cid in ancestors for d in claims[cid]["dependencies"]}
        if expanded == ancestors:
            break
        ancestors = expanded
    order, done = [], set()
    while done != affected:
        ready = sorted(cid for cid in affected-done
                       if all(d["id"] not in affected or d["id"] in done for d in claims[cid]["dependencies"]))
        if not ready:
            raise ValueError("Dependency cycle in proposed affected population")
        order.extend(ready)
        done.update(ready)
    records = []
    for cid in order:
        claim = claims[cid]
        row = {
            "claim_id": cid, "old_revision": claim["revision"], "proposed_revision": claim["revision"] + 1,
            "old_claim_sha256": canonical_claim_digest(claim),
            "old_status": claim["status"], "old_review_state": claim["review_state"],
            "editorial_member": cid in selected,
            "affected_dependency_pins": [dict(d, proposed_revision=claims[d["id"]]["revision"]+1)
                                         for d in claim["dependencies"] if d["id"] in affected],
            "action": "Apply exact approved clarification and authenticated editorial record; preserve all prior records"
                      if cid in selected else "Obtain separate actual dependency-impact review, or mark NEEDS_RECHECK and propagate",
            "must_review_before_editorial_descendant_can_remain_clear": cid in (ancestors & affected)-selected,
        }
        if cid in selected:
            row["current_claim_exactly_matches_reviewed_snapshot"] = row["old_claim_sha256"] == reviewed[cid]["reviewed_claim_sha256"]
            row["old_assumptions"] = claim["assumptions"]
            row["approved_new_assumptions"] = reviewed[cid]["recommended_assumptions"]
        records.append(row)
    plan = {
        "status": "UNAPPLIED_DEPENDENCY_MIGRATION_PLAN_REQUIRING_INDEPENDENT_REVIEW",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ledger_snapshot": snapshot.relative_to(ROOT).as_posix(), "ledger_sha256": sha(snapshot),
        "editorial_review": REVIEW.as_posix(), "editorial_review_sha256": sha(ROOT / REVIEW),
        "population": "Current ledger claim IDs in the transitive dependency closure of the exact 17 reviewed assumption edits",
        "current_claim_count": len(claims), "editorial_member_count": len(selected), "affected_count": len(affected),
        "additional_dependent_count": len(affected-selected),
        "noneditorial_prerequisites_of_editorial_members": sorted((ancestors & affected)-selected),
        "topological_order": order, "records": records,
        "automatic_approvals": [],
        "limitations": ["No ledger mutation or claim promotion occurred", "Plan is bound to this exact ledger snapshot; recompute if the ledger changes",
                        "The semantic editorial review covers wording only; dependent impact reviews are separate work",
                        "No mathematical experiment or independent proof was replayed by this tooling recorder"],
    }
    save(out / "dependency_plan.json", plan)
    commands = [
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "acceleration", "-p", "test_validate_claims.py", "-v"],
        [sys.executable, "-B", "acceleration/validate_claims.py", snapshot.relative_to(ROOT).as_posix(),
         "--hashes", "none", "--out", (out / "unmodified_ledger_validation.json").relative_to(ROOT).as_posix()],
    ]
    executions = []
    for index, command in enumerate(commands):
        start = time.perf_counter()
        run = subprocess.run(command, cwd=ROOT, capture_output=True)
        for stream in ("stdout", "stderr"):
            (out / f"command_{index:02d}.{stream}.log").write_bytes(getattr(run, stream))
        executions.append(dict(argv=command, working_directory=str(ROOT), returncode=run.returncode,
                               wall_seconds=time.perf_counter()-start,
                               stdout=f"command_{index:02d}.stdout.log", stderr=f"command_{index:02d}.stderr.log"))
    source_paths = [Path(__file__).relative_to(ROOT), Path("acceleration/validate_claims.py"), Path("acceleration/test_validate_claims.py"),
                    Path("docs/claims.schema.json"), Path("docs/claims.schema.v1.json"), Path("docs/CLAIMS_SCHEMA.md"),
                    Path("pyproject.toml"), Path("uv.lock"), REVIEW, Path(review["reviewed_ledger_snapshot"])]
    report = {
        "status": "PRODUCER_TOOLING_CHECKS_PASS_PENDING_INDEPENDENT_CODE_REVIEW" if all(x["returncode"] == 0 for x in executions) else "TOOLING_CHECK_FAILED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "command": [sys.executable, *sys.argv], "working_directory": str(ROOT),
        "setup": "UV_PROJECT_ENVIRONMENT=build/research-venv; uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/record_20260930_editorial_migration_tooling.py",
        "versions": {"python": platform.python_version(), "PyYAML": version("PyYAML"), "jsonschema": version("jsonschema"),
                     "uv": subprocess.check_output(["uv", "--version"], text=True).strip()},
        "inputs_sha256": {p.as_posix(): sha(ROOT / p) for p in source_paths},
        "outputs_sha256": {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()},
        "executions": executions,
        "development_failures": {"initial_run": "49 tests: three failures. Two authentic migration fixtures lacked the separate dependent prerequisite review; one intended bad basis mutation was identical to the original. Corrected fixtures and strengthened controls. No validator relaxation made for those failures.",
                                 "initial_stdout_artifact": None, "unavailable_reason": "Initial exploratory test stdout existed only in tool output; no exact saved log is claimed",
                                 "intermediate_results": "50 tests passed, then 53 tests passed after additional controls; final exact captured execution is recorded above"},
        "limitations": ["Producer test execution is engineering evidence, not independent approval of the new validator", "The root ledger was not edited",
                        "Unmodified current-ledger check intentionally disables ordinary artifact hashing and expensive mathematical checks; skips are explicit",
                        "The positive unit-test fixture's separate dependent impact verification is explicitly SYNTHETIC, not permission to promote a real claim"],
    }
    save(out / "summary.json", report)
    print(json.dumps(dict(status=report["status"], summary=(out / "summary.json").relative_to(ROOT).as_posix(),
                          summary_sha256=sha(out / "summary.json"), closure_count=len(affected),
                          additional_dependents=sorted(affected-selected)), indent=2))
    return 0 if all(x["returncode"] == 0 for x in executions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
