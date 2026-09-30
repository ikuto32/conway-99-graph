# V2 defensive job-handle correction

V1 source and preparation remain preserved. The sole runtime change requires a
non-null job handle before cleanup queries active-process counts. A kill-on-close
fallback therefore fails the active-zero receipt explicitly; it cannot query the
caller job through a NULL handle. All other semantics and CLI remain unchanged.

# Four contained sequential Python build invocations

Fresh alternative to the vetoed shared-scheduler source. The old source/spec,
preparation and both independent counterexamples remain intact. Reuse ONLY its
separately calibrated WindowsJob class/structures, never its scheduler or Popen
launch method. Frozen sequential builder v2 and every scientific producer/helper
are unchanged. This launcher has no SAT/native solver, ledger or Git operation.
The unchanged producer reads Git provenance when an authorized build later runs.

```text
plan|build --launch-plan PATH --launch-plan-sha256 SHA --out NEW
build additionally: --engineering-gate PATH --engineering-gate-sha256 SHA
```

Mandatory independent status before process creation:
INDEPENDENT_FOUR_SERIAL_BUILD_ENGINEERING_PASS. Bind the actual new launcher/spec,
frozen serial builder and reused WindowsJob source. Every engineering dependency
is rehashed. Plan mode validates sources/partitions and writes commands without
creating processes or jobs.

Root-authenticated JSON launch plan:
schema EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1;
parent_selection_path/parent_selection_sha256;
workers=4; seconds_per_chunk=120;
build_selections = four {path,sha256,attempt_id,out} objects.
Each selection is an existing EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1 with policy
AUTHORIZED_DISJOINT_BUILD_PARTITION_V1, matching parent path/hash, index0..3 and
offset16*index. Its16 IDs must be exactly that slice of the parent64 list. All
IDs are distinct authenticated members; all output paths and attempt IDs are new
and disjoint. Preserve ordering and all raw counts. No previous outcome is
consumed, no native outcome skipped, no implicit resume or deduplication.

Four independent120-second build allocations total480 allocated seconds. There
is no single120-second global allocation. Start each clock when its suspended
interpreter is released. At most four serial builder trees run concurrently.
Scientific code and output formats are unchanged; no timing or speedup claim.

Containment fixes the observed virtual-environment redirector race. Use documented
CreateProcessW with CREATE_SUSPENDED|CREATE_NO_WINDOW, then assign the returned
process handle to a non-breakaway kill-on-close Job Object, then ResumeThread.
No interpreter instruction or runtime child can run before assignment. Prepare
all four suspended roots before releasing any. An assignment/preparation failure
terminates those suspended roots and reaps them without scientific work.
Each child uses explicit stdout/stderr files and NUL stdin, no output pipes. The
three owned std handles are temporarily inheritable only across creation and are
reset before preparing the next root. Native process/thread handles are explicit;
there is no private Popen thread-handle workaround.

The active monitor phase ONLY resumes, zero-time polls and requests termination.
It does not wait, close output files, hash logs or validate child outputs. A root
exit requests termination of its entire job, removing any lingering runtime
descendants. A chunk reaching its own deadline receives the same nonblocking
termination request. Nonzero exits or monitor exceptions request all remaining
stops. Complete the entire stop-request pass BEFORE any blocking reap, job-active
drain, log hash or receipt verification. Thus a slow cleanup cannot allow a peer's
build work to continue beyond its allocation. The monitor's nominal10ms polling
resolution and OS scheduling latency are recorded, not disguised as exact clocks.
Termination failures try kill-on-close; losing the job handle prevents an observed
active-zero certificate and makes the final invocation fail rather than claiming
cleanup success.

After all stops are requested, wait for every root, observe each job's active
process count zero (including runtime descendants), close every handle/log, then
hash all preserved chunk artifacts. Record exit codes, deadlines, stop reasons,
reap/active-zero evidence and child summary identity if present. Cleanup may extend
return time; it never extends the permitted build-work allocation. The parent
consolidator must independently verify child outputs and explicit pending cases.
A missing child summary or timeout is preserved, not called complete. No output
is deleted. This launcher supplies engineering receipts, not formula correctness.

Prior negative controls that this source must address:

- I/parallel_build_deadline/summary.json
  8ab768a0a6b77fb27da69399b50e12e270254afaaf5e64cdd4e15f77e6d7a490:
  blocking5s finish delayed another child's1s deadline to5.025s.
- I/windows_job_assignment_race/summary.json
  758e611699d893f831c4071c59093864e5f33dcd570e6c75eea719d10a25516f:
  the already-spawned venv interpreter and descendants escaped late assignment.

WindowsJob component calibration e9256816... covers only that old component, not
this new suspended launcher or scheduler. New independent harmless lifecycle
tests must include delayed cleanup, pre-resume inactivity, complete nested runtime
containment and termination, launch failures, and exact command/selection controls.
No formula build is authorized by source preparation or mocked tests alone.

Microsoft documentation used for API signatures and ordering:

- https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw
- https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread
- https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
