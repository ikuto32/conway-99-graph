"""Bind the isolated public-replay checks without promoting mathematical claims."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260917_public_replay"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    bindings = {}
    def read(relative):
        path = OUT / relative
        bindings[path.relative_to(ROOT).as_posix()] = digest(path)
        return json.loads(path.read_bytes())
    extraction = read("retry2/extraction_manifest.json")
    direct = read("direct_controls_wrapper.json")
    relocated = read("relocated_fresh16_wrapper.json")
    triangle = read("triangle_controls_wrapper.json")
    result = read("relocated_fresh16.json")
    reference_path = Path(extraction["extraction_root"]) / "acceleration/results/20260917_independent_review/batch_raw_review.json"
    reference = json.loads(reference_path.read_bytes())
    assert digest(reference_path) == extraction["files"][reference_path.relative_to(Path(extraction["extraction_root"])).as_posix()]["sha256"]
    assert direct["outcome"] == "FAIL" and direct["rejected_outside_paths"]
    assert relocated["outcome"] == "PASS" and not relocated["rejected_outside_paths"]
    assert relocated["checker_output_sha256"] == digest(OUT / "relocated_fresh16.json")
    assert triangle["outcome"] == "PASS" and len(triangle["control_results"]) == 6
    assert len(result["records"]) == len(reference["records"]) == 16
    assert result["records"] == reference["records"]
    assert result["controls"] == reference["controls"]
    assert all(extraction["files"][name]["sha256"] == expected for name, expected in relocated["opened_isolated_inputs_sha256"].items())
    assert all(extraction["files"][name]["sha256"] == expected for name, expected in triangle["opened_isolated_inputs_sha256"].items())
    source_paths = [Path(__file__), ROOT / "acceleration/audit_public_replay.py", ROOT / "acceleration/replay_published_checker.py"]
    for path in source_paths:
        bindings[path.relative_to(ROOT).as_posix()] = digest(path)
    for path in (OUT / "protocol.json", OUT / "retry1/protocol.json", OUT / "retry2/protocol.json"):
        bindings[path.relative_to(ROOT).as_posix()] = digest(path)
    receipt = dict(
        timestamp=datetime.now(timezone.utc).isoformat(), published_source_commit=extraction["source_commit"],
        command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
        status="FROZEN_FRESH16_REPLAY_PASS_WITH_EXPLICIT_RELOCATION",
        direct_unrelocated_execution="FAIL_PORTABILITY_ABSOLUTE_ORIGINAL_PATH",
        path_mapping_controls=len(relocated["path_mapping_controls"]),
        mapped_original_paths=len(relocated["mapped_paths"]), denied_local_fallback_reads_in_successful_replay=0,
        extracted_runtime_inventory=extraction["direct_runtime_inventories"],
        unique_extracted_runtime_paths=extraction["total_unique_paths"], extracted_runtime_bytes=extraction["extracted_bytes"],
        fresh16=dict(selected=16, attempted=16, completed=16, exact_results_identical_to_published_reference=True,
                     historical_positive_controls=1, corrupted_controls_rejected=6,
                     actually_opened_isolated_input_files=len(relocated["opened_isolated_inputs_sha256"]), elapsed_seconds=relocated["elapsed_seconds"]),
        triangle=dict(runtime_inventory_missing=[], runtime_inventory_hash_mismatches=[], calibration_fixtures_passed=6,
                      full_enumeration_rerun=False, full_enumeration_skip_reason="Bounded task prioritizes fresh16; saved 99-path runtime inventory verified, 73-million-subset audit not rerun"),
        failed_attempts=[
            dict(attempt=1, protocol="protocol.json", exit_code=1,
                 error="ValueError: Nonrelative dependency path: C:/Users/ikuto/projects/conway-99-graph/acceleration/audit_goal_theory_pairs.py",
                 disposition="Preserved protocol and partial Git-only extraction; extraction lookup later maps exact original-root prefix without changing raw bytes",
                 prior_helper_source_availability="MISSING", prior_helper_source_reason="Initial uncommitted helper revision was revised after failure; its exact hash survives in protocol, but no source snapshot was saved"),
            dict(attempt=2, protocol="retry1/protocol.json", exit_code=1,
                 error="ValueError: Byte budget reached; extraction incomplete", declared_byte_limit=300000000,
                 observed_partial_files=1776, observed_partial_bytes=299843010,
                 disposition="Preserved partial immutable extraction; retry2 scoped to actual saved checker runtime inventories instead of recursively rerunning unrelated producer histories",
                 prior_helper_source_availability="MISSING", prior_helper_source_reason="Intermediate uncommitted helper revision was revised; its exact hash survives in protocol, but no source snapshot was saved")],
        preserved_extraction_note="Isolation directory also retains extra immutable Git files from the capped provenance expansion; successful checker opened-file inventory is independently matched to the final runtime extraction manifest",
        inputs_sha256=bindings, mathematical_claim_promotion=False, target_resolution=False,
        limitations=["Repeated frozen arithmetic checker execution verifies portability and byte availability under the explicit wrapper; it is not a new independent derivation.",
                     "Prior complete local-domain enumeration is still a hash-bound saved dependency; not exhaustively reenumerated in this replay.",
                     "Triangle's full saved runtime input inventory is present and hash-matched, but full triangle mathematical replay was not executed.",
                     "No claim of complete historical producer-history replay; the broader recursive provenance extraction was capped.",
                     "Git objects at the published commit were used; a fresh network clone/package install was not attempted.",
                     "Frozen checker reports retain their historical source_commit and verifier strings; this receipt binds actual published source and classifies this execution as repetition."])
    with (OUT / "replay_receipt.json").open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    print(json.dumps(dict(status=receipt["status"], cases=16, repeated_outputs_identical=True, triangle_full_replay=False)))


if __name__ == "__main__":
    main()
