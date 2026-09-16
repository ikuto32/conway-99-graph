# E72 resumed status

Updated UTC: 2026-09-05T03:55:54.191458+00:00

Explicit user resume was confirmed by root. Frozen snapshots and all 25 stopped completed-file SHA256 values match. Solver and runner code are unchanged. The saved small5 runner uses `--jobs 1`; m03 supplement uses its fixed one-worker mode. Total solver worker cap is 2. The weaker old m03 full80 job remains stopped. No lower-layer enumeration is performed.

Pre-resume independent audits passed: small5 24/52 shards, 188/400 records, UNSAT mass 14,912; m03 supplement record11, UNSAT mass 32. Only the already credited small5 macro (1,0), 96 records / mass 8,192, was whole at restart. The three previously unaudited m33 shards and m03 r11 are now audited.

- small5: PID 8280, started 2026-09-05T11:40:06.3258820+09:00; parent present=True. Command: `C:/Users/ikuto/.local/bin/python3.12.exe -B -u scratch_root_e72_source150_small5_joint_primary_runner.py --jobs 1`
- m03: PID 22500, started 2026-09-05T11:40:06.3323478+09:00; parent present=False. Command: `C:/Users/ikuto/.local/bin/python3.12.exe -B -u scratch_root_e72_source150_m03_joint_supplement_runner.py`

Current producer-complete files: small5 26/52; m03 11/11. Current independent audits: small5 26 shards / 204 records / UNSAT mass 15840; m03 11 singleton(s), status masses {'UNSAT': 448, 'SAT': 0, 'UNKNOWN': 0}.

New whole macros since resume: [{'macro': [0, 3], 'catalog_orbits': 80, 'catalog_coverage': 4096, 'path': 'scratch_root_e72_source150_m03_complete_audit.json', 'sha256': 'BAE3C5A09D42C140B3EE16B74FC29F52ADEA59BC5CB71E1F7CED622E8722D37F'}].

The transient restarted manifest may list fewer old files until its sequential worker reaches them. The pre-resume audit copies preserve established coverage. Parent process IDs, start times, descendant IDs, exact commands, hashes, and scope are saved in the JSON status. Logs are `scratch_resume_e72_small5.stdout.log`, `scratch_resume_e72_small5.stderr.log`, `scratch_resume_e72_m03.stdout.log`, and `scratch_resume_e72_m03.stderr.log`.

For small5 increments, run `scratch_resume_e72_small5_audit.py`. It joins stopped and current checkpoint entries into `scratch_resume_e72_small5_union_manifest.json` and invokes the unchanged independent partial auditor with only its input manifest path redirected. This avoids transient coverage loss without modifying the live runner manifest or frozen code. For m03 increments, run the original `scratch_root_e72_source150_m03_joint_supplement_audit.py`. Then regenerate this report with `scratch_resume_e72_status.py`.

Under explicit root authorization, the central inventory was updated for the complete m03 macro (150,0,3), mass 4,096. The independent whole-document delta audit verifies that this is the sole coverage transfer; partial and supplement masses were not credited separately. Current source150 open coverage: 28,672; total E72 unresolved coverage: 450,560.

Manifest states are small5=RUNNING, m03=COMPLETE. An absent parent after a COMPLETE manifest is expected terminal completion. Existing unfinished small5 work is left running; this update never starts another worker.

Partial macro results are not whole-macro exclusions. These local CSP results are not DRAT certificates, full E72 exclusion, a 99-vertex graph, or a nonexistence proof.
