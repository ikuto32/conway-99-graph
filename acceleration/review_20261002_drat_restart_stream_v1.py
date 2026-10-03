"""Read-only source/calibration review with independent hand-derived tiny state.

No substantial input replay. The reviewed checker's implementation is shared
for the additional engineering controls and explicitly disclosed as such.
"""
from datetime import datetime, timezone
from io import BytesIO
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "acceleration/audit_20261002_drat_restart_artifact_v2.py"
SOURCE_SHA = "3693f1d77b60f9c095cd6afa0f6b67a9c048b4ad6336b9454f30ce459eb6156e"
CAL = "acceleration/results/20261002_drat_restart_stream_calibration02/summary.json"
CAL_SHA = "e4013fdff6233f36b603666fd846946e73b7b0a446e3c267b0b131b6fbb6f8f9"
SUP = "acceleration/results/20261002_drat_restart_stream_calibration_supervision02/summary.json"


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    assert sha(SOURCE) == SOURCE_SHA and sha(CAL) == CAL_SHA
    calibration = json.loads((ROOT / CAL).read_bytes())
    supervisor = json.loads((ROOT / SUP).read_bytes())
    assert calibration["status"] == "INDEPENDENT_DRAT_RESTART_STREAMING_CALIBRATION_V1_PASS"
    positive = [control for control in calibration["controls"] if control["result"] == "PASS_COMPLETE_STATE"]
    negative = [control for control in calibration["controls"] if control["result"] == "REJECT"]
    assert len(positive) == 6 and len(negative) == 6
    assert all(control["rejection_stage"] == "INPUT_SYNTAX" and control["reason"] for control in negative)
    assert supervisor["command_exit_code"] == 0 and supervisor["cleanup"]["reaped"]
    assert supervisor["cleanup"]["job_active_zero_observed"]
    spec = importlib.util.spec_from_file_location("reviewed_stream_checker", ROOT / SOURCE)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    # Independently hand-derived counts and order, not the imported tiny oracle.
    formula = b"p cnf 3 4\n1 2 0\n2 1 0\n3 0\n-1 -2 0\n"
    prefix = b"d 1 2 0\n2 2 1 0\nd 3 0\nd -3 0\nd 1 -2 0\nd 1 2 0\n-3 0\n"
    derivative = b"p cnf 3 4\n1 2 0\n3 0\n-2 -1 0\n-3 0\n"
    counters = dict(variables=3, original_clauses=4, original_literals=7,
        active_clause_occurrences=4, unique_recorded_clauses=4, stored_literals=6,
        proof_additions=2, proof_deletions=5, effective_deletions=2,
        missing_deletions=1, ignored_small_deletions=2,
        duplicate_literals_normalized=1, duplicate_clause_additions=2,
        tautology_records_retained=0, original_proof_bytes=len(prefix),
        retained_original_bytes=len(prefix), trailing_dropped_bytes=0,
        appended_boundary_newline=False)
    summary = dict(schema="DRAT_ACTIVE_MULTISET_PARSER_V1", status="CANDIDATE_RESTART_STATE",
        profile=checker.PROFILE, rat_rup_checked=False, equisatisfiability_asserted=False,
        target_resolution=False, **counters)
    deadline = checker.CommandDeadline(30, allocation_reason="Hand-derived independent tiny state engineering review")
    actual = checker.check(BytesIO(formula), BytesIO(prefix), BytesIO(derivative), BytesIO(prefix), summary, deadline)
    assert actual == counters
    rejected = []
    for label, raw, terminated in [
        ("zero_then_extra_EOF", b"-2 0 1", False),
        ("garbage_EOF", b"garbage", False),
        ("complete_extra_token", b"-2 0 1", True),
        ("extra_variable", b"4 0", True),
        ("integer_overflow", b"2147483648 0", True),
    ]:
        try:
            checker.parse(raw, 3, terminated)
        except checker.ParseSyntaxError:
            rejected.append(label)
        else:
            raise AssertionError("Malformed raw record accepted: " + label)
    paths = [SOURCE, CAL, SUP, "acceleration/audit_20261002_drat_restart_artifact_v1.py",
        "acceleration/audit_20261002_drat_restart_controls_v1.py",
        "acceleration/drat_restart_20261002_v1.cpp", "build/rook-drat-checker/drat-trim.c",
        "acceleration/command_deadline.py", "acceleration/run_compute_command.py",
        "uv.lock", "pyproject.toml", Path(__file__).relative_to(ROOT).as_posix()]
    report = dict(status="INDEPENDENT_DRAT_RESTART_STREAMING_SOURCE_REVIEW_V2_PASS",
        timestamp=datetime.now(timezone.utc).isoformat(), verifier="/root/checkpoint_audit",
        source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT),
        inputs_sha256={path: sha(path) for path in paths},
        scope="Read-only checking-profile, algorithm and frozen calibration review; additional independently hand-derived tiny state controls. No substantial original input or candidate state replay.",
        reviewed_properties=[
            "Canonical sorted unique signed literals are stored as complete packed int32 bytes; Counter equality has no digest-only clause comparison.",
            "Counter keys retain first-seen order and zero multiplicities; addition restores one copy and deletion removes one existing non-small copy.",
            "Default pinned backward DRAT parser ignores normalized size<=1 deletion at drat-trim.c:1192; the candidate profile discloses this restriction.",
            "Every retained line preserves raw order/pivot bytes, with only the explicit EOF newline or final unterminated-record transformation.",
            "All derivative clause occurrences, variable bound, statistics and final byte exhaustion are checked; no sampled state comparisons.",
            "Version2 malformed controls require ParseSyntaxError at the input stage; v1's overly broad ValueError/KeyError catch is preserved and does not approve v2.",
        ],
        calibration=dict(valid_state_controls=6, malformed_raw_controls=6,
            malformed_rejection_stage="INPUT_SYNTAX", corrupted_artifact_controls=calibration["corrupted_controls_rejected"],
            supervisor_reaped_group_empty=True),
        additional_controls=dict(hand_derived_multiset="PASS", malformed_records_rejected=rejected),
        expected_resource_population=dict(unique_recorded_clauses=8502107, stored_literals=35738534,
            interpretation="The Counter retains all recorded identities including deleted ones, beyond the 3069024 active occurrences; budget must include this population."),
        shared_components=["Additional tiny controls execute the reviewed streaming checker itself; this is engineering source review, not another independent substantial artifact checker.", "Python integers/Counter/struct, pinned environment and deadline/supervisor."],
        limitations=["No substantial 431.5MB input replay performed by this review.", "No RAT/RUP, equisatisfiability, model reconstruction or target resolution established."],
        target_resolution=False, rat_rup_checked=False, equisatisfiability_asserted=False,
        artifact_availability="LOCAL_ONLY")
    out = ROOT / "acceleration/results/20261002_independent_review/restart_streaming_review01"
    out.mkdir(exist_ok=False)
    with (out / "summary.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(path=(out / "summary.json").relative_to(ROOT).as_posix(), sha256=sha((out / "summary.json").relative_to(ROOT).as_posix()))))


if __name__ == "__main__":
    main()
