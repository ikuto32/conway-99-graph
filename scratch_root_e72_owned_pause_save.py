"""Save stopped E72 checkpoints; this utility never launches search or audits."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


PREFIX = "scratch_root_e72_stopped_20260905_1131"
SMALL = Path("scratch_root_e72_source150_small5_joint_primary_manifest.json")
M03 = Path("scratch_root_e72_source150_m03_joint_supplement_manifest.json")
SMALL_AUDIT = Path("scratch_root_e72_source150_small5_joint_primary_partial_audit.json")
STOPPED_IDS = [30528, 6268, 59196, 42864, 43912, 76464, 14396, 21312, 19296, 57056,
               66144, 44304, 55696, 42792, 74484, 65552, 45740, 15428, 68252, 46788,
               812, 38272]


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def snapshot(path, label):
    data = path.read_bytes()
    destination = Path(f"{PREFIX}_{label}_manifest.raw.json")
    destination.write_bytes(data)
    return json.loads(data), {"source": str(path), "snapshot": str(destination), "sha256": sha(data)}


def main():
    small, small_snapshot = snapshot(SMALL, "small5")
    m03, m03_snapshot = snapshot(M03, "m03")
    previous_audit = json.loads(SMALL_AUDIT.read_bytes())
    audited_paths = {row["path"] for row in previous_audit["shards"]}
    completed = []
    for lane, checkpoints in (("small5", small["shards"]), ("m03", m03["record_results"])):
        for key, row in checkpoints.items():
            if row["status"] != "COMPLETE":
                continue
            path = Path(row["path"])
            digest = sha(path.read_bytes())
            assert digest == row["sha256"]  # Checkpoint integrity only, no solver replay.
            completed.append({"lane": lane, "task": key, "path": str(path), "sha256": digest,
                              "independently_audited_before_stop": lane == "small5" and str(path) in audited_paths})
    pending_small = []
    for macro, start, stop in small["tasks"]:
        key = f"{macro[0]}:{macro[1]}:{start}:{stop}"
        if key not in small["shards"] or small["shards"][key]["status"] != "COMPLETE":
            pending_small.append({"task": key, "macro": macro, "start": start, "stop": stop})
    pending_m03 = [number for number in m03["records"]
                   if str(number) not in m03["record_results"] or m03["record_results"][str(number)]["status"] != "COMPLETE"]
    result = {
        "operational_status": "STOPPED_BY_USER", "automatic_resume_authorized": False,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        "stop_verification": {"verified_by": "Get-Process after root escalated taskkill trees",
                              "verified_at_jst": "2026-09-05T11:31:53+09:00", "checked_process_ids": STOPPED_IDS,
                              "remaining_live_process_count": 0},
        "parent_identities_before_stop": [{"pid": 30528, "start_time_jst": "2026-09-05 10:00:27", "session": 76183},
                                          {"pid": 6268, "start_time_jst": "2026-09-05 11:26:13", "session": 33277}],
        "raw_manifest_snapshots": [small_snapshot, m03_snapshot],
        "producer_RUNNING_is_stale_after_termination": True,
        "small5_completed_shards": len(small["shards"]), "small5_total_shards": len(small["tasks"]),
        "small5_last_independent_audit_shards": previous_audit["audited_shards"],
        "m03_completed_singletons": len(m03["record_results"]), "m03_total_singletons": len(m03["records"]),
        "completed_checkpoint_files": completed,
        "finished_but_not_independently_audited": [row for row in completed if not row["independently_audited_before_stop"]],
        "small5_pending_tasks": pending_small, "m03_pending_records": pending_m03,
        "inflight_details": {"m03_interrupted_record": 36,
                             "small5_exact_child_command_mapping_captured": False,
                             "note": "Taskkill recorded exact terminated descendant IDs. Per-child small5 command lines were unavailable before termination. All remaining tasks are preserved above; checkpoint resume discovers completed files before executing any missing task."},
        "saved_resume_commands_NOT_EXECUTED": [
            "& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_root_e72_source150_small5_joint_primary_partial_audit.py",
            "& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_root_e72_source150_m03_joint_supplement_audit.py",
            "& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_root_e72_source150_small5_joint_primary_runner.py --jobs 8",
            "& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_root_e72_source150_m03_joint_supplement_runner.py",
        ],
        "resume_preconditions": "Explicit user request to resume; revalidate no owned runner is live; first audit finished-but-unaudited files. Preserve fixed solver/config hashes. Runners reuse completed output files and execute only missing tasks.",
        "old_ordinary_m03": "PID38272 was stopped by root. Its stronger every-depth replacement already completed all80 cases. The current plan resumes only the11-record joint-map supplement, not the redundant weaker full80 job.",
        "goal_status": "Original Conway-99 objective remains unchanged and unachieved. No graph or new exclusion claim is made by this save operation.",
    }
    output = Path(f"{PREFIX}_checkpoint.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    report = Path(f"{PREFIX}_restart.md")
    report.write_text("# Stopped by user — E72 owned jobs\n\n"
                      "All listed owned process IDs were absent after root's escalated tree termination. "
                      "The original manifests retain stale `RUNNING`; the operational state is `STOPPED_BY_USER`. "
                      "No automatic restart is authorized.\n\n"
                      f"Saved small-five completion: {len(small['shards'])}/52 shards; last independent audit: "
                      f"{previous_audit['audited_shards']} shards. Saved m03 supplement: {len(m03['record_results'])}/11 singleton files. "
                      "Finished-but-unaudited files are listed explicitly in the JSON checkpoint and have no new central credit.\n\n"
                      "Byte-exact manifest snapshots, completed-file SHA256 values, pending tasks, known stopped PIDs, "
                      "and saved resume commands are in `" + str(output) + "`. Existing proof artifacts and search outputs were not changed.\n\n"
                      "After an explicit user resume request, audit the finished-but-unaudited files, then run the saved "
                      "checkpoint runners. They validate and reuse completed files. Do not restart the weaker old m03 full80 job; "
                      "its stronger full every-depth result is already complete.\n", encoding="utf-8")
    print(json.dumps({"status": "STOPPED_BY_USER", "checkpoint": str(output), "restart_notes": str(report),
                      "small5_completed": len(small["shards"]), "small5_last_audited": previous_audit["audited_shards"],
                      "m03_completed": len(m03["record_results"]),
                      "unaudited_completed_files": len(result["finished_but_not_independently_audited"])}, separators=(",", ":")))


if __name__ == "__main__":
    main()
