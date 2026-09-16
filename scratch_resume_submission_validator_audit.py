"""Bounded review/calibration of the strict submission validator."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from validate_submission import parse_edge_text, self_test, verify_edges


def main():
    here = Path(__file__).resolve().parent
    candidate = here / "scratch_general_v2_best.json"
    before = candidate.read_bytes()
    data = json.loads(before)
    # Exercise the requested text parser without writing a candidate text
    # file, and independently recompute every mathematical condition.
    text = "\n".join("{%d, %d}" % tuple(edge) for edge in data["edges"]) + "\n"
    report = verify_edges(parse_edge_text(text))
    assert report["valid"] is False
    assert report["edge_count"] == 693 and report["degree_mismatch_count"] == 0
    assert report["pairs_checked"] == 4851
    bad_pairs = report["adjacent_pair_mismatch_count"] + report["nonadjacent_pair_mismatch_count"]
    assert bad_pairs == 1916 == data["bad_pairs"]
    assert candidate.read_bytes() == before
    absent = here / "scratch_resume_submission_validator_intentionally_absent.txt"
    assert not absent.exists()
    completed = subprocess.run([sys.executable, "-B", str(here / "validate_submission.py"), str(absent)],
                               capture_output=True, text=True, check=False)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "MISSING_FILE"
    result = {
        "status": "STRICT_SUBMISSION_VALIDATOR_CHECK_PASS",
        "validator_sha256": sha256((here / "validate_submission.py").read_bytes()).hexdigest(),
        "self_test": self_test(),
        "existing_invalid_candidate": str(candidate.relative_to(here)),
        "existing_candidate_sha256": sha256(before).hexdigest(),
        "existing_invalid_candidate_report": report,
        "missing_file_cli_exit_code": completed.returncode,
        "candidate_bytes_unchanged": True,
        "submission_created_or_modified": False,
    }
    (here / "scratch_resume_submission_validator_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "self_tests_passed": result["self_test"]["checks_passed"],
                      "existing_candidate_bad_pairs": bad_pairs, "submission_created_or_modified": False}))


if __name__ == "__main__":
    main()
