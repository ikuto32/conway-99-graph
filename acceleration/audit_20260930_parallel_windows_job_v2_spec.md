# Harmless real Windows Job Object component calibration

Freeze this checker, canary and spec before execution. Authenticate the exact
parallel v1 source/spec/pinfile and its sequential import closure. Import only
that reviewed module to test its WindowsJob implementation and unchanged
WindowsChild finish/poll/abort paths. Do not call producer main, plan/build,
Git, WSL, any native solver or any broad process inventory.

Three canary runs use a separately authored Python file writer with a stdin
barrier. Each creates a three-generation process tree and writes only tiny
heartbeat/PID files within its fresh output directory. Its own eight-second
maximum protects against an unexpected containment failure. Use the same
job-assignment-before-RUN rule as production. Inspect only exact handles to
owned PIDs and this calibrator's PID as a negative membership control.

Check inherited membership of all three generations. Test explicit termination,
kill-on-last-handle-close, and normal root exit with live descendants followed
by the unchanged finish method. Every owned process handle must be signalled,
the root reaped, and heartbeat files unchanged after cleanup. Complete raw
receipts, PID chains, exit codes and file identities remain saved.

Also exercise the unmodified real WindowsChild constructor/worker with a
deliberately invalid canary command; the worker must reject it before calling
the frozen formula producer. Then inject an assignment refusal before RUN and
verify the unmodified abort path kills/reaps that unreleased worker. The
injection is explicitly a control; it does not alter frozen source bytes.

Budget40seconds; about11 harmless Python processes total, at most three canary
generations simultaneously. CREATE_NO_WINDOW is mandatory. Final cleanup
terminates only handles/jobs created by this calibrator and waits on them.
Failure remains preserved; no automatic retry or source mutation.

Successful status INDEPENDENT_PARALLEL_WINDOWS_JOB_COMPONENT_CALIBRATION_PASS
approves only these finite platform containment/cleanup observations. It does
NOT approve the v1 scheduler: the independent delayed-cleanup countercontrol
already refutes its shared work-deadline guarantee. A fresh corrected scheduler
must be separately checked before any research build. No speedup, mathematical
encoding or target claim follows.

API semantics were checked against the Microsoft primary documentation:

- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject
- https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject

Run locked/offline:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_parallel_windows_job_v2.py --out acceleration/results/20260930_independent_review/parallel_windows_job_v2
```

## V1 calibration assumption correction

V1 stopped before releasing RUN because it asserted that the job contained exactly
one process. This is not a valid precondition for a Windows virtual-environment
interpreter redirector. V2 instead checks absent application markers, saves the
actual job count, and authenticates both Popen/runtime PIDs through explicit
canary spawn records. Every known owned runtime handle must have membership and
terminate. The original source/spec/canary/failure are preserved and bound. The
canary remains bounded and harmless; no production bytes change.
