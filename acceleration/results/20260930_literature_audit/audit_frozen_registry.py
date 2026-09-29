"""Read-only check of frozen ledger public retrieval pointers, not mathematics.

Run with the repository's pinned uv environment. Output is created exclusively.
This does not import the registry validator or any research producer.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from urllib.parse import unquote

import yaml


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout


def pointer(url: str):
    match = re.fullmatch(
        r"https://github\.com/ikuto32/conway-99-graph/blob/([0-9a-f]{40})/(.+)", url)
    return (match[1], unquote(match[2])) if match else None


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        raise ValueError("Require immutable full commit")
    assert pointer("https://github.com/ikuto32/conway-99-graph/blob/" + "a" * 40 + "/x%20y") == ("a" * 40, "x y")
    assert pointer("https://github.com/ikuto32/conway-99-graph/blob/main/x") is None
    assert pointer("https://github.com/unrelated/repo/blob/" + "a" * 40 + "/x") is None
    raw = git_blob(args.commit, "CLAIMS.yaml")
    data = yaml.safe_load(raw)
    rows = []
    for artifact in data["artifacts"]:
        if artifact["availability"] != "PUBLIC":
            continue
        item = {"id": artifact["id"], "path": artifact["path"],
                "sha256_expected": artifact["sha256"],
                "retrieval": artifact["retrieval"]}
        ref = pointer(artifact["retrieval"])
        if ref is None:
            item.update(outcome="NOT_CHECKED", reason="Not a direct immutable project GitHub blob pointer")
        else:
            item["pointer_commit"], item["pointer_path"] = ref
            try:
                observed = sha(git_blob(*ref))
                item["sha256_observed"] = observed
                item["path_matches"] = ref[1] == artifact["path"]
                item["outcome"] = "PASS" if observed == artifact["sha256"] and item["path_matches"] else "FAIL"
            except subprocess.CalledProcessError as exc:
                item.update(outcome="FAIL", reason=exc.stderr.decode("utf-8", errors="replace"))
        rows.append(item)
    paths = ["CLAIMS.yaml", "docs/claims.schema.json", "docs/CLAIMS_SCHEMA.md",
             "acceleration/validate_claims.py", "acceleration/test_validate_claims.py",
             ".github/workflows/claims.yml", "docs/STOP_20260917_SIX_COORDINATE.md",
             "docs/LITERATURE_20260917.md"]
    report = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verifier": "Codex subagent /root/state_literature_audit",
        "source_commit": args.commit,
        "command_argv": [sys.executable, *sys.argv],
        "working_directory": str(Path.cwd()),
        "tool_versions": {"python": platform.python_version(), "PyYAML": version("PyYAML")},
        "checker_sha256": sha(Path(__file__).read_bytes()),
        "input_git_blob_hashes": {p: sha(git_blob(args.commit, p)) for p in paths},
        "control_count": 3,
        "controls": "Immutable pointer accepted; mutable branch and wrong repository rejected.",
        "population": "PUBLIC artifact records in frozen root CLAIMS.yaml",
        "counts": dict(Counter(row["outcome"] for row in rows)),
        "public_pointer_results": rows,
        "ledger_counts": dict(Counter(f'{c["status"]}/{c["review_state"]}' for c in data["claims"])),
        "target": data["target"],
        "limitations": [
            "Checks local Git object contents for immutable retrieval URLs, not remote HTTP accessibility.",
            "No solver, proof, domain-enumeration, mathematical claim, or reviewer-independence replay.",
            "Counts describe ledger records; they are not graph or branch coverage.",
            "The separate project validator and its CI are inspected in the written audit; not imported here.",
            "No active-process observation is performed; execution state is UNKNOWN from this audit."
        ]
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"counts": report["counts"], "ledger_counts": report["ledger_counts"],
                      "report": str(out), "sha256": sha(out.read_bytes())}))


if __name__ == "__main__":
    main()
