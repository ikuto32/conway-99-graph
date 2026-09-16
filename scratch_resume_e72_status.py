"""Read-only E72 restart checks and a separate operational status snapshot.

This does not enumerate mathematical cases or edit the central inventory.
The two already frozen runners own their manifests and compute at most one
solver child each. Use the existing independent auditors for mathematical
coverage; producer-complete file counts are deliberately separate.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path


CHECKPOINT = Path("scratch_root_e72_stopped_20260905_1131_checkpoint.json")
PROCESSES = Path("scratch_resume_e72_processes.json")
OUTPUT = Path("scratch_resume_e72_status.json")
REPORT = Path("scratch_resume_e72_status.md")
AUDITS = {
    "small5": Path("scratch_root_e72_source150_small5_joint_primary_partial_audit.json"),
    "m03": Path("scratch_root_e72_source150_m03_joint_supplement_audit.json"),
}
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
SOLVER_SHA256 = "BE279135FF346E8CB22BEE5DB5DB4D4807D4C2FDE858FC53382BA1D8DBA21C6F"
SMALL_RUNNER = Path("scratch_root_e72_source150_small5_joint_primary_runner.py")
SMALL_RUNNER_SHA256 = "4A6AE54851BB2B8702BD1A78AC2EC83800BEEDD2F72B051B6BC71595AEC732CB"
M03_RUNNER = Path("scratch_root_e72_source150_m03_joint_supplement_runner.py")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic(path, text):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def process_snapshot():
    class Entry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260),
        ]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    entries = {}
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(Entry)
        more = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while more:
            entries[entry.th32ProcessID] = {
                "pid": entry.th32ProcessID, "parent_pid": entry.th32ParentProcessID,
                "executable_name": entry.szExeFile,
            }
            more = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    return entries


def main():
    checkpoint = load(CHECKPOINT)
    hashes = []
    for row in checkpoint["raw_manifest_snapshots"] + checkpoint["completed_checkpoint_files"]:
        path = Path(row.get("snapshot", row.get("path")))
        digest = sha(path)
        assert digest == row["sha256"], path
        hashes.append({"path": str(path), "sha256": digest, "matches_stop_snapshot": True})
    assert sha(SOLVER) == SOLVER_SHA256
    assert sha(SMALL_RUNNER) == SMALL_RUNNER_SHA256
    frozen_m03 = load(Path("scratch_root_e72_stopped_20260905_1131_m03_manifest.raw.json"))
    assert sha(M03_RUNNER) == frozen_m03["runner_sha256"]
    audits = {lane: load(path) for lane, path in AUDITS.items()}
    for lane, path in AUDITS.items():
        before = Path(f"scratch_resume_e72_{lane}_pre_resume_audit.json")
        if not before.exists():
            # First invocation follows the explicit pre-restart independent audits.
            before.write_bytes(path.read_bytes())
    small = audits["small5"]
    m03 = audits["m03"]
    assert small["status"] == "SOURCE150_SMALL5_PARTIAL_CHECKPOINT_AUDIT_PASS"
    assert m03["status"] == "SOURCE150_M03_JOINT_SUPPLEMENT_CHECKPOINT_AUDIT_PASS"
    old_small = load(Path("scratch_resume_e72_small5_pre_resume_audit.json"))
    old_m03 = load(Path("scratch_resume_e72_m03_pre_resume_audit.json"))
    process_entries = process_snapshot()
    roots = load(PROCESSES)
    trees = []
    for root in roots:
        owned = {root["pid"]}
        while True:
            new = {pid for pid, row in process_entries.items() if row["parent_pid"] in owned}
            if new <= owned:
                break
            owned.update(new)
        trees.append({**root, "parent_pid_present": root["pid"] in process_entries,
                      "process_tree": [process_entries[pid] for pid in sorted(owned) if pid in process_entries]})
    live_small = load(Path("scratch_root_e72_source150_small5_joint_primary_manifest.json"))
    live_m03 = load(Path("scratch_root_e72_source150_m03_joint_supplement_manifest.json"))
    assert live_small["jobs"] == live_m03["jobs"] == 1
    assert live_small["solver_sha256"] == live_m03["solver_sha256"] == SOLVER_SHA256
    manifest_statuses = {"small5": live_small["status"], "m03": live_m03["status"]}
    for tree in trees:
        tree["manifest_status"] = manifest_statuses[tree["lane"]]
        tree["terminal_completion_recorded"] = tree["manifest_status"] == "COMPLETE"
    small_files, small_pending = [], []
    for macro, start, stop in live_small["tasks"]:
        path = Path(f"scratch_theory_e72_source150_sync_jointprimary_small5_m{macro[0]}{macro[1]}_r{start}_{stop}.json")
        if path.exists():
            small_files.append(str(path))
        else:
            small_pending.append({"macro": macro, "start": start, "stop": stop, "output": str(path)})
    m03_files = [n for n in live_m03["records"]
                 if Path(f"scratch_theory_e72_source150_sync_jointmap_m03_sat_r{n}.json").exists()]
    whole = list(small["complete_macro_certificates"])
    if m03["whole_macro_excluded"]:
        whole.append({"macro": [0, 3], "catalog_orbits": 80, "catalog_coverage": 4096,
                      **m03["complete_macro_certificate"]})
    original_whole = {tuple(row["macro"]) for row in old_small["complete_macro_certificates"]}
    new_whole = [row for row in whole if tuple(row["macro"]) not in original_whole]
    inventory_delta_path = Path("scratch_resume_e72_m03_inventory_delta_audit.json")
    inventory_update = load(inventory_delta_path) if inventory_delta_path.exists() else None
    if inventory_update is not None:
        assert inventory_update["status"] == "INDEPENDENT_E72_M03_ONLY_INVENTORY_DELTA_AUDIT_PASS"
        assert inventory_update["only_changed_macro"] == [150, 0, 3]
        assert inventory_update["new_exact_non_DRAT_coverage"] == 4096
    inventory_path = Path("scratch_root_e72_complete_coverage_inventory.json")
    inventory = load(inventory_path)
    result = {
        "status": "RESUMED_WITH_EXPLICIT_USER_AUTHORIZATION",
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "resume_authority": "Parent /root confirmed explicit user resume on 2026-09-05.",
        "frozen_checkpoint": str(CHECKPOINT), "frozen_sha256_checks": hashes,
        "solver_sha256": SOLVER_SHA256,
        "runner_sha256": {"small5": sha(SMALL_RUNNER), "m03": sha(M03_RUNNER)},
        "maximum_computational_workers": 2,
        "runner_code_modified": False, "old_weaker_m03_full80_restarted": False,
        "no_lower_layer_enumeration": True, "processes": trees,
        "pre_resume_audits": {
            "small5": {"shards": old_small["audited_shards"], "records": old_small["audited_records"],
                       "UNSAT_mass": old_small["audited_UNSAT_mass"]},
            "m03": {"singletons": old_m03["audited_singletons"], "status_mass": old_m03["status_mass"]},
        },
        "producer_complete_files_not_coverage_credit": {"small5": len(small_files), "m03": len(m03_files)},
        "current_or_next_missing_task": {"small5": small_pending[0] if small_pending else None,
                                         "m03_record": next((n for n in live_m03["records"] if n not in m03_files), None)},
        "live_manifest_reported_complete_counts": {"small5": len(live_small["shards"]), "m03": len(live_m03["record_results"])},
        "manifest_caveat": "On restart, sequential runners may still be reading previously audited existing files; their transient manifest counts may be below the immutable pre-resume audit.",
        "current_independent_audits": {
            "small5": {"path": str(AUDITS["small5"]), "sha256": sha(AUDITS["small5"]),
                       "resume_audit_adapter": "scratch_resume_e72_small5_audit.py",
                       "union_manifest": "scratch_resume_e72_small5_union_manifest.json",
                       "shards": small["audited_shards"], "records": small["audited_records"],
                       "UNSAT_mass": small["audited_UNSAT_mass"]},
            "m03": {"path": str(AUDITS["m03"]), "sha256": sha(AUDITS["m03"]),
                    "singletons": m03["audited_singletons"], "status_mass": m03["status_mass"]},
        },
        "audited_whole_macros": whole, "new_whole_macros_since_resume": new_whole,
        "central_inventory_modified_by_this_agent": inventory_update is not None,
        "central_inventory_update": {"audit_path": str(inventory_delta_path),
                                     "audit_sha256": sha(inventory_delta_path),
                                     "only_changed_macro": [150, 0, 3],
                                     "new_exact_non_DRAT_coverage": 4096} if inventory_update else None,
        "current_central_inventory": {"path": str(inventory_path), "sha256": sha(inventory_path),
                                      "source150_open_coverage": inventory["source150"]["open_coverage"],
                                      "global_unresolved_coverage": inventory["global"]["unresolved_or_pending_coverage"]},
        "claim_boundary": "Only fully audited whole macros may receive central exclusion credit. Partial UNSAT mass is not whole-macro credit. Finite local CSP evidence is not DRAT. No full E72 exclusion, Conway graph, or nonexistence proof is claimed.",
    }
    atomic(OUTPUT, json.dumps(result, indent=2) + "\n")
    process_lines = "\n".join(f"- {row['lane']}: PID {row['pid']}, started {row['start_time']}; parent present={row['parent_pid_present']}. Command: `{row['command']}`" for row in trees)
    inventory_note = (
        "Under explicit root authorization, the central inventory was updated for the complete m03 macro (150,0,3), mass 4,096. The independent whole-document delta audit verifies that this is the sole coverage transfer; partial and supplement masses were not credited separately."
        if inventory_update else "This agent has not changed the central inventory."
    )
    note = f"""# E72 resumed status

Updated UTC: {result['updated_utc']}

Explicit user resume was confirmed by root. Frozen snapshots and all 25 stopped completed-file SHA256 values match. Solver and runner code are unchanged. The saved small5 runner uses `--jobs 1`; m03 supplement uses its fixed one-worker mode. Total solver worker cap is 2. The weaker old m03 full80 job remains stopped. No lower-layer enumeration is performed.

Pre-resume independent audits passed: small5 24/52 shards, 188/400 records, UNSAT mass 14,912; m03 supplement record11, UNSAT mass 32. Only the already credited small5 macro (1,0), 96 records / mass 8,192, was whole at restart. The three previously unaudited m33 shards and m03 r11 are now audited.

{process_lines}

Current producer-complete files: small5 {len(small_files)}/52; m03 {len(m03_files)}/11. Current independent audits: small5 {small['audited_shards']} shards / {small['audited_records']} records / UNSAT mass {small['audited_UNSAT_mass']}; m03 {m03['audited_singletons']} singleton(s), status masses {m03['status_mass']}.

New whole macros since resume: {new_whole}.

The transient restarted manifest may list fewer old files until its sequential worker reaches them. The pre-resume audit copies preserve established coverage. Parent process IDs, start times, descendant IDs, exact commands, hashes, and scope are saved in the JSON status. Logs are `scratch_resume_e72_small5.stdout.log`, `scratch_resume_e72_small5.stderr.log`, `scratch_resume_e72_m03.stdout.log`, and `scratch_resume_e72_m03.stderr.log`.

For small5 increments, run `scratch_resume_e72_small5_audit.py`. It joins stopped and current checkpoint entries into `scratch_resume_e72_small5_union_manifest.json` and invokes the unchanged independent partial auditor with only its input manifest path redirected. This avoids transient coverage loss without modifying the live runner manifest or frozen code. For m03 increments, run the original `scratch_root_e72_source150_m03_joint_supplement_audit.py`. Then regenerate this report with `scratch_resume_e72_status.py`.

{inventory_note} Current source150 open coverage: {inventory['source150']['open_coverage']:,}; total E72 unresolved coverage: {inventory['global']['unresolved_or_pending_coverage']:,}.

Manifest states are small5={live_small['status']}, m03={live_m03['status']}. An absent parent after a COMPLETE manifest is expected terminal completion. Existing unfinished small5 work is left running; this update never starts another worker.

Partial macro results are not whole-macro exclusions. These local CSP results are not DRAT certificates, full E72 exclusion, a 99-vertex graph, or a nonexistence proof.
"""
    atomic(REPORT, note)
    print(json.dumps({"status": result["status"], "producer_complete_files": result["producer_complete_files_not_coverage_credit"],
                      "processes": trees, "new_whole_macros": new_whole}, separators=(",", ":")))


if __name__ == "__main__":
    main()
