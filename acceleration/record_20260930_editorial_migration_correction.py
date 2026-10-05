"""Record the preserved independent veto and producer correction replay."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

import test_validate_claims as fixtures
from validate_claims import validate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260930_editorial_migration_tooling/correction_v2.json"
VETO = "acceleration/results/20260930_independent_review/editorial_migration_veto/summary.json"
VETO_SHA = "62d2246a8ec141bf41c4e0f7e41b9a9cc113501ed5d8412e7bd521befc1bba7c"
RUN1 = "acceleration/results/20260930_editorial_migration_tooling/run01/summary.json"
RUN2 = "acceleration/results/20260930_editorial_migration_tooling/run02/summary.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    assert sha(ROOT / VETO) == VETO_SHA
    veto = json.loads((ROOT / VETO).read_text(encoding="utf-8"))
    old, new = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in (RUN1, RUN2)]
    inputs = {VETO: VETO_SHA, RUN1: sha(ROOT / RUN1), RUN2: sha(ROOT / RUN2)}
    for path, expected in veto["inputs_sha256"].items():
        preserved = ROOT / "acceleration/results/20260930_editorial_migration_tooling/rejected_v1" / Path(path).name
        assert sha(preserved) == expected == old["inputs_sha256"][path]
        inputs[preserved.relative_to(ROOT).as_posix()] = expected
    for path, expected in new["inputs_sha256"].items():
        assert sha(ROOT / path) == expected
        inputs[path] = expected
    fixtures.EditorialMigrationTests.setUpClass()
    fixture = fixtures.EditorialMigrationTests()
    fixture.setUp()
    try:
        positive = validate(fixture.data, fixture.root, fixture.schema, hash_mode="none", previous=None)
        assert positive["valid"]
        fixture.first["limitations"] = ["Unapproved deletion of restrictions"]
        corrupted = validate(fixture.data, fixture.root, fixture.schema, hash_mode="none", previous=None)
        assert not corrupted["valid"]
        assert any("unapproved initial editorial fields" in e for e in corrupted["errors"])
    finally:
        fixture.tearDown()
    log = ROOT / "acceleration/results/20260930_editorial_migration_tooling/run02/command_00.stderr.log"
    count = int(re.search(r"Ran (\d+) tests", log.read_text(encoding="utf-8")).group(1))
    assert count == 56 and all(x["returncode"] == 0 for x in new["executions"])
    inputs[log.relative_to(ROOT).as_posix()] = sha(log)
    inputs[Path(__file__).relative_to(ROOT).as_posix()] = sha(__file__)
    report = {
        "status": "PRODUCER_CORRECTION_TESTED_PENDING_INDEPENDENT_REVIEW",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": [sys.executable, *sys.argv], "working_directory": str(Path.cwd()), "python": platform.python_version(),
        "previous_independent_verdict": veto["status"],
        "defect": "At the approved migration revision, standalone mode accepted unrelated limitations changes because the restricted old/new field comparison ran only through --previous impact checking.",
        "correction": "check_editorial_migrations now invokes the same strict field/evidence/dependency-relation check against the immutable old snapshot whenever current revision equals the approved migration revision, regardless of --previous.",
        "schema_version_changed_again": False,
        "schema_reason": "The correction tightens semantic enforcement of the existing exact version2 migration; schema bytes remain unchanged.",
        "history_preserved": "Original source/schema/tests/docs and recorder bytes are preserved in rejected_v1; original run01 and the independent veto report remain untouched.",
        "inputs_sha256": inputs,
        "standalone_reproduction": {"positive_valid": positive["valid"], "original_corruption_valid": corrupted["valid"],
                                    "original_corruption_errors": corrupted["errors"]},
        "captured_test_count": count,
        "additional_controls": ["Eight unrelated claim-field changes without previous ledger", "Premise relation change, premise addition/deletion, unrelated evidence addition without previous ledger",
                                "Later revision cannot use stale editorial PASS, and changing the editorial record to that later revision is rejected"],
        "ledger_changed": False, "mathematical_claim_changed": False,
        "shared_components": ["Positive fixture and validator are producer implementations; this replay is not independent review", "Root's separate original failing audit is authenticated and preserved"],
        "limitations": ["New engineering test pass does not approve mathematics or application of the ledger migration", "Independent root re-review remains required before ledger application"],
    }
    with OUT.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "path": OUT.relative_to(ROOT).as_posix(), "sha256": sha(OUT)}))


if __name__ == "__main__":
    main()
