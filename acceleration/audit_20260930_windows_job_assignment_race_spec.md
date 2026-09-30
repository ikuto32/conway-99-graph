# Live pre-assignment scheduling countercontrol

Freeze source/spec/canary before execution. The question is whether a stdin RUN
barrier alone guarantees that all processes created by a Windows virtual-env
Python launcher are contained when the root is assigned after Popen returns.
Earlier immediate-assignment success is not a proof against another permitted
scheduling order. This is a harmless real lifecycle probe, not a formula run.

Launch only the fresh canary v3 with CREATE_NO_WINDOW. It writes a startup PID
record before blocking on RUN. Delay assignment until that record exists, then
assign the original Popen PID with the exact frozen WindowsJob implementation.
Inspect IsProcessInJob only for the original Popen/runtime PIDs named in this
owned tree. Positively confirm root membership. Release RUN, let the bounded
canary create its two further generations, and inspect their recorded handles.
No process list, WSL, Git, native research or formula producer is invoked.

Terminate the assigned job and verify its active count is zero. If a canary
application is outside that job, check whether its exact process handle remains
unsignalled and whether heartbeat files continue growing. Such an observation
is a concrete counterexample to guaranteed tree containment under this launch
order. If none is observed, report only NOT_OBSERVED; do not invent a positive
result. Either way, terminate/wait every known owned handle and retain all files.
The canary has its own three-second maximum, and the audit allocation is15seconds.

The controlled delay represents a permitted preemption between Popen and job
assignment, not a claim about the frequency of races in earlier builds. The
application barrier can hold application work while the interpreter/runtime
process already exists. Windows child membership is inherited at creation;
late assignment does not promise retroactive membership. Primary API basis:
https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_windows_job_assignment_race.py --out acceleration/results/20260930_independent_review/windows_job_assignment_race
```

No source/input, ledger or Git mutation. Preserve any failure before a fresh
version. A future suspended-create/assign/resume backend needs independent
calibration; this countercontrol does not approve one.
