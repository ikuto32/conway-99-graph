# Small-five joint-primary checkpoint recovery

At 2026-09-05 09:58 JST, authoritative `Get-Process` checks showed that the
previous runner PID 41124 and all its Python workers were absent. The two
independent macro `(0,3)` jobs, PIDs 38272 and 19520, remained live. The cause
of the disappearance was not determined; the stale manifest still said
`RUNNING` and was not treated as liveness evidence.

The independent partial audit passed for all six completed checkpoint files:
48 of 400 catalog orbits, labelled UNSAT mass 3,968, no failed checkpoint.
No whole macro was covered. Therefore the macro inventory was unchanged:
source150 open mass 40,960; total unresolved/pending E72 mass 462,848.

At 10:00:27 JST the unchanged runner was resumed using its existing-output
validation path, with eight workers, no DFS cap, no joint-map cap, and no
projection. All six completed files were reused without re-execution; only
previously unfinished tasks were restarted. Existing `(0,3)` jobs were left
untouched.

- Runner SHA256: `4A6AE54851BB2B8702BD1A78AC2EC83800BEEDD2F72B051B6BC71595AEC732CB`
- Solver SHA256: `BE279135FF346E8CB22BEE5DB5DB4D4807D4C2FDE858FC53382BA1D8DBA21C6F`
- Resumed execution session: `76183`
- Resumed runner PID: `30528`
- Initial resumed worker PIDs: `5704, 15696, 23372, 26436, 52284, 54904, 57128, 63004`

The operational plan is to audit each new completed shard and only credit a
macro when its full catalog record set has been audited as exact UNSAT. The
partial auditor is `scratch_root_e72_source150_small5_joint_primary_partial_audit.py`.
Its JSON is a checkpoint snapshot, not a process-liveness assertion or a DRAT
certificate. The complete-run audit remains the existing
`scratch_root_e72_source150_small5_joint_primary_audit.py`.

The process identifiers above are observations at the recovery event, not
claims that those processes remain live later. Revalidate them or session
76183 before any subsequent resume.
