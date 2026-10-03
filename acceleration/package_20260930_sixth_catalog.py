"""Read-only completed-artifact inventory, exact recovery audit, ignore proposal."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260930_sixth_artifact_packaging"
BASE = ROOT / "acceleration/results/20260930_unrestricted_full99_cnf/instance.cnf"
FIFTH = ROOT / "acceleration/results/20260930_resume/fifth_artifact_catalog.json"
CHECKPOINT = ROOT / "acceleration/results/20260930_resume/fifth_milestone_checkpoint.json"
EXCLUDED = ["acceleration/results/20260930_strengthened_four_branch_native_pilot/",
            "acceleration/results/20260930_sixth_artifact_packaging/"]
LIMIT = 10 * 1024 ** 2


def digest(path):
    result = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            result.update(block)
    return result.hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(path.read_bytes())


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def require(value, message):
    if not value:
        raise ValueError(message)


def ready_file(path):
    return {"path": key(path), "sha256": digest(path), "bytes": path.stat().st_size,
            "availability": "LOCAL_ONLY", "publication_ready_under_10MiB": path.stat().st_size <= LIMIT,
            "availability_reason": "Present locally; this catalog does not assert GitHub publication."}


def recover_fifth_inputs():
    records = []
    for previous in read(FIFTH)["entries"]:
        if "parts" not in previous:
            continue
        parts = previous["parts"]
        for part in parts:
            path = ROOT / part["path"]
            require(digest(path) == part["sha256"] and path.stat().st_size == part["bytes"] <= LIMIT, "fifth part identity/size")
        compressed = b"".join((ROOT / part["path"]).read_bytes() for part in parts)
        require(sha256(compressed).hexdigest() == previous["gzip_sha256"], "whole gzip identity")
        state, count = sha256(), 0
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as stream:
            for block in iter(lambda: stream.read(1048576), b""):
                state.update(block)
                count += len(block)
        raw = ROOT / previous["raw"]
        require(state.hexdigest() == previous["sha256"] == digest(raw) and count == previous["bytes"] == raw.stat().st_size,
                "complete fifth gzip reconstruction")
        records.append({**ready_file(raw), "role": "Existing base mathematical input referenced by sixth-wave records",
            "recovery_type": "ORDERED_GZIP_PARTS", "parts": [ready_file(ROOT / part["path"]) for part in parts],
            "recovery": previous["recovery"], "reconstruction_checked": True,
            "public_retrieval": "Publish the listed parts with this catalog; concatenate in listed order and gzip-decompress, then verify raw SHA256.",
            "existing_catalog": key(FIFTH), "existing_catalog_sha256": digest(FIFTH)})
    return records


def recover_branches():
    ordinary = read(ROOT / "acceleration/results/20260930_unrestricted_four_branches/branches.json")
    stronger = read(ROOT / "acceleration/results/20260930_four_branch_strengthened_preparation/recipes.json")
    recipe_pins = [ROOT / "acceleration/results/20260930_unrestricted_four_branches/branches.json",
                   ROOT / "acceleration/results/20260930_four_branch_strengthened_preparation/recipes.json"]
    records = []
    for strengthened, collection in [(False, ordinary["branches"]), (True, stronger["branches"])]:
        for row in collection:
            parent = "20260930_four_branch_strengthened_preparation" if strengthened else "20260930_four_branch_native_preparation"
            path = ROOT / "acceleration/results" / parent / row["branch"] / "instance.cnf"
            units = ROOT / (row["original_branch_suffix"] if strengthened else row["suffix"])
            suffixes = [ROOT / row["equality_suffix"], units] if strengthened else [units]
            header = f"p cnf 1186500 {4141120 if strengthened else 4136458}\n".encode()
            state = sha256(header)
            byte_count = len(header)
            with BASE.open("rb") as stream:
                require(stream.readline() == b"p cnf 1186500 4136454\n", "base LF header")
                for block in iter(lambda: stream.read(1048576), b""):
                    state.update(block)
                    byte_count += len(block)
            for suffix in suffixes:
                require(suffix.stat().st_size <= LIMIT, "suffix too large")
                block = suffix.read_bytes()
                state.update(block)
                byte_count += len(block)
            require(state.hexdigest() == row["cnf_sha256"] == digest(path) and byte_count == path.stat().st_size, "full composed CNF reconstruction")
            audit = path.with_name("independent_composed_bytes.json" if strengthened else "independent_cnf_bytes.json")
            record = {**ready_file(path), "role": "Exact solver input; a conditional branch of the checked unrestricted cover",
                "recovery_type": "BASE_BODY_PLUS_SUFFIXES", "base_cnf": key(BASE), "base_cnf_sha256": digest(BASE),
                "replacement_header_ascii": header.decode(), "ordered_suffixes": [ready_file(p) for p in suffixes],
                "recipe": ready_file(recipe_pins[int(strengthened)]), "recipe_branch": row["branch"],
                "recovery": "Recover the base using fifth-catalog gzip parts; remove only its first LF-terminated header; prepend replacement_header_ascii; append ordered suffix files verbatim.",
                "reconstruction_checked": True, "independent_byte_audit": ready_file(audit),
                "certificate_claim": False, "raw_file_retained": True}
            if strengthened:
                record["reconstruction_tool"] = ready_file(ROOT / "acceleration/reconstruct_20260930_strengthened_branches.py")
                record["example_locked_command"] = "uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/reconstruct_20260930_strengthened_branches.py --recipes acceleration/results/20260930_four_branch_strengthened_preparation/recipes.json --out build/replay-strengthened-four --report build/replay-strengthened-four-report.json"
                record["environment"] = "Set UV_PROJECT_ENVIRONMENT=build/research-venv before the example; raw base must already be restored. No native solver is required."
            records.append(record)
    return records


def recover_rows():
    raw = ROOT / "acceleration/results/20260930_unrestricted_pair_equalities/run01/rows.jsonl"
    zipped = raw.with_name(raw.name + ".gz")
    require(zipped.stat().st_size <= LIMIT, "rows gzip too large")
    state, size = sha256(), 0
    with gzip.open(zipped, "rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            state.update(block)
            size += len(block)
    require(state.hexdigest() == digest(raw) and size == raw.stat().st_size, "complete equality rows reconstruction")
    return {**ready_file(raw), "role": "Exact polynomial/threshold provenance for the entailed equality-unit audit",
        "recovery_type": "GZIP", "companion": ready_file(zipped), "reconstruction_checked": True,
        "recovery": "Gzip-decompress rows.jsonl.gz and verify the recorded raw byte count and SHA256.", "raw_file_retained": True}


def partial_proof():
    run = ROOT / "acceleration/results/20260930_unrestricted_native_pilot"
    summary = read(run / "summary.json")
    raw = run / "main/proof.drat"
    record = summary["raw_artifacts"][key(raw)]
    require(summary["actual_exit_code"] == 124 and summary["independently_verified_target_resolution"] is False, "completed limited pilot expected")
    require(digest(raw) == record["sha256"] and raw.stat().st_size == record["bytes"], "limited pilot proof bytes changed")
    return {**ready_file(raw), "role": "Incomplete timeout-run engineering artifact; not a nonexistence certificate",
        "recovery_type": None, "recovery_type_null_reason": "Not packaged for public replay because no proof-based mathematical claim uses this incomplete trace.",
        "public_companion": None, "public_companion_null_reason": "Intentionally LOCAL_ONLY; no complete certified proof was produced.",
        "certificate_claim": False, "proof_completeness": "UNESTABLISHED", "solver_actual_exit": 124,
        "retrieval": "Local original retained at the exact raw path; no remote retrieval location is asserted.",
        "reproducibility_limit": "Repeating the time-limited run is not guaranteed to reproduce identical partial proof bytes.",
        "run_summary": ready_file(run / "summary.json"), "raw_file_retained": True}


def main():
    before_ignore = digest(ROOT / ".gitignore")
    before_ledger = digest(ROOT / "CLAIMS.yaml")
    checkpoint = read(CHECKPOINT)
    names = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z", "acceleration/results"], cwd=ROOT).decode().split("\0")
    names = sorted(name for name in names if name and not any(name.startswith(prefix) for prefix in EXCLUDED))
    OUT.mkdir(parents=True, exist_ok=False)
    save(OUT / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "source_sha256": digest(Path(__file__)),
        "previous_checkpoint": key(CHECKPOINT), "previous_checkpoint_sha256": digest(CHECKPOINT),
        "previous_catalog": key(FIFTH), "previous_catalog_sha256": digest(FIFTH),
        "population": "Snapshot of all currently untracked files beneath acceleration/results, excluding the exact active-pilot prefix and this output directory. Includes still-unpublished fifth-wave overlap; it is not a research-progress count.",
        "excluded_prefixes": EXCLUDED, "active_pilot_process_observed_by_this_script": False,
        "selection_rule": "Audit every file over10MiB in this frozen path inventory; explicitly include inherited base-input gzip recovery.",
        "changes_authorized": "New catalog/proposed-ignore files only. Do not modify source artifacts, shared .gitignore, ledger, stage, or commit."})
    inventory = []
    unstable = []
    previous_evidence = checkpoint["evidence_sha256"]
    for name in names:
        path = ROOT / name
        before = path.stat()
        hashed = digest(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            unstable.append(name)
            continue
        inventory.append({"path": name, "sha256": hashed, "bytes": before.st_size, "availability": "LOCAL_ONLY",
            "git_state_at_scan": "UNTRACKED", "publication_ready_under_10MiB": before.st_size <= LIMIT,
            "directly_named_in_fifth_checkpoint_evidence": name in previous_evidence,
            "availability_reason": "Publication is pending; local presence is verified without asserting remote availability."})
    save(OUT / "untracked_inventory.json", {"population": "Frozen untracked completed-output path inventory with stated exclusions", "entries": inventory, "unstable_files_deferred": unstable})
    require(not unstable, "an inventory file changed while hashing; preserve manifest and rerun as a new catalog revision")
    recovered_base = recover_fifth_inputs()
    entries = [*recover_branches(), recover_rows(), partial_proof()]
    oversized = {row["path"] for row in inventory if row["bytes"] > LIMIT}
    covered = {row["path"] for row in entries}
    require(oversized == covered, "every oversize untracked completed artifact needs an explicit disposition: " + repr(sorted(oversized ^ covered)))
    ignore_lines = ["# Sixth resumed milestone; exact branch recipes/gzip recovery and one incomplete LOCAL_ONLY trace."]
    existing_ignore = set((ROOT / ".gitignore").read_text().splitlines())
    ignore_lines += ["/" + path for path in sorted(covered) if "/" + path not in existing_ignore]
    (OUT / "proposed_gitignore.txt").write_text("\n".join(ignore_lines) + "\n", encoding="utf-8", newline="\n")
    # Tool provenance remains explicit; unavailable binary portability is not hidden.
    tools = []
    for path in [ROOT / "build/research-cadical195/source/build/cadical", ROOT / "build/rook-drat-checker/drat-trim.exe"]:
        tools.append({**ready_file(path), "role": "Local calibrated native executable; not a mathematical input",
            "public_companion": None, "public_companion_null_reason": "Executable not packaged by this task; recorded source/build evidence is the retrieval path.",
            "exact_binary_rebuild_guaranteed": False})
    tools[0]["source_retrieval"] = "acceleration/results/20260930_native_cadical195_build/cadical-1.9.5-source.tar.gz plus manifest/receipt/compiler/configure/make logs and acceleration/build_20260930_native_cadical195.py; official commit146207318796f094dcded87349a64f0c6927309e."
    tools[1]["source_retrieval"] = "Source-authenticated clean checker build recorded in acceleration/results/20260930_rook_sat_independent_proof/summary.json; local build/rook-drat-checker source/patch/build manifest remain available. Upstream commit2e3b2dc0ecf938addbd779d42877b6ed69d9a985; do not modify the dirty tools/drat-trim submodule."
    catalog = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "COMPLETED_ARTIFACT_RECOVERY_AND_IGNORE_PROPOSAL_READY",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "entries": entries, "inherited_base_input_recovery": recovered_base, "local_tool_artifacts": tools,
        "inventory": key(OUT / "untracked_inventory.json"), "inventory_sha256": digest(OUT / "untracked_inventory.json"),
        "proposed_ignore": key(OUT / "proposed_gitignore.txt"), "proposed_ignore_sha256": digest(OUT / "proposed_gitignore.txt"),
        "counts": {"inventory_untracked_files": len(inventory), "oversize_completed_untracked_files": len(oversized),
            "exact_recoverable_oversize_mathematical_inputs": sum(e.get("reconstruction_checked", False) for e in entries),
            "incomplete_local_only_noncertificate_traces": sum(e.get("proof_completeness") == "UNESTABLISHED" for e in entries),
            "inherited_base_inputs_rechecked": len(recovered_base), "proposed_ignore_lines": len(ignore_lines) - 1},
        "all_oversize_mathematical_inputs_have_under_10MiB_recovery_closure": True,
        "recovery_publication_status": "READY_FOR_PUBLICATION; companion files currently remain LOCAL_ONLY until actually published.",
        "mathematical_verification": False, "independent_review": False,
        "excluded_prefixes": EXCLUDED, "running_outputs_inspected": False, "raw_files_modified": False,
        "shared_gitignore_modified_by_this_script": False, "ledger_modified_by_this_script": False, "staged_or_committed": False,
        "shared_files_before_sha256": {".gitignore": before_ignore, "CLAIMS.yaml": before_ledger},
        "shared_files_after_sha256": {".gitignore": digest(ROOT / ".gitignore"), "CLAIMS.yaml": digest(ROOT / "CLAIMS.yaml")},
        "limitations": ["File/recovery counts are artifact units, not mathematical progress or target search coverage.",
            "Current active-pilot prefix was excluded even if its state later changes; it needs a subsequent catalog after completion.",
            "The hash inventory contains unpublished fifth-wave overlap; no attempt is made to infer research-stage counts from filenames.",
            "The incomplete timeout trace has no public companion and does not support any nonexistence claim.",
            "This byte/recovery audit does not independently verify the underlying mathematics or native binaries."]}
    save(OUT / "catalog.json", catalog)
    print(json.dumps({"status": catalog["status"], "counts": catalog["counts"], "catalog_sha256": digest(OUT / "catalog.json")}, indent=2))


if __name__ == "__main__":
    main()
