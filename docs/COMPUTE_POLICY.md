# CPU/GPU command execution policy

The user's clarified limit is **21,600 seconds (six hours) per command
invocation**, not cumulative across commands. A separate command has its own
allowance. Conversation, human review and document editing do not consume a
command's computation time. Research remains stopped; this policy change does
not authorize a scientific run.

The unit is one monitored command invocation and its computational descendants.
Start the deadline before its computational preprocessing. Include CPU/GPU
execution, transfers, checking and internal retries performed within that command.
Four parallel children share their parent's elapsed wall-clock time, not summed
CPU-core/GPU-device time or four fresh allowances. Internal child launches do not
extend the command's deadline. Separate invocations, including a separately
launched checker, are not accumulated against a task-wide six-hour ceiling.
This clarification supersedes the earlier cumulative-task interpretation.

Before each command, declare its scientific scope, required output, acceptance
thresholds, success criterion and independent verification requirement. Producing
a useful result is distinct from proving correctness, completeness or optimality.
For Conway-99, all existing exact matrix/proof requirements and independent
verification rules remain in force.

The historical 120-second build cap is **not a default for future research**.
Choose an allocation up to 21,600 seconds from the question, resource estimates,
comparable historical runs and value of the expected result. A justified shorter
allocation remains appropriate. Six hours is an upper bound, never a target.
Likewise, do not copy the historical 60-second solver allocation automatically.
Reserve time inside the invocation for its checkpointing and orderly shutdown.

Monitor meaningful progress and resource usage. Reassess continuation at least
every 1,800 seconds during computation, and on significant new evidence. Record
elapsed and remaining time, completed/attempted work, comparable quality metrics,
resource trends and recoverable checkpoints. A timely continuation review can
renew the review interval while useful work continues, but cannot extend the
current command's hard deadline. A missed review stops further computation
until reassessment; this is not evidence of mathematical impossibility.

Compare the expected benefit of further work with remaining cost and alternatives.
Use calibrated historical data or credible execution diagnostics. Do not invent
a success probability or assume linear progress. A calibrated probability below
5% is a review threshold, not an automatic stop; the value of success may justify
continuation. Without a calibrated estimate, explain concrete diagnostics and
uncertainty. Stop early for negligible expected improvement, infeasible resource
needs or a clearly better alternative. Neither elapsed time alone nor silent
terminal output establishes stagnation. Prior time spent does not justify
continuing a low-value run.

The machine-readable policy is [compute_policy.json](../acceleration/compute_policy.json).
The [deadline helper](../acceleration/command_deadline.py) and
[command supervisor](../acceleration/run_compute_command.py) apply per invocation;
there is no cumulative cross-command budget file. Use the existing pinned
`uv.lock` environment (`uv run --locked`; on this Windows workspace set
`UV_PROJECT_ENVIRONMENT=build/research-venv`). Each supervised command requires
an explicit allocation and rationale, success criteria and verification criteria.
Positive/corrupted engineering controls establish only their tested behavior.

On Windows, use the supervisor's suspended Windows Job containment for a local
process tree. Do not wrap WSL, SSH, remote jobs or a process escaping that boundary.
For Linux/WSL computation, supervision and the native timeout guard must run
**inside Linux**, not merely around `wsl.exe` on Windows. OS scheduling and I/O
are not hard-real-time services: record actual stopping times and failures;
do not claim an unobserved absolute termination guarantee. Unknown process state
must prevent further launches until checked.

Historical launchers, source hashes, receipts, gates and the saved
`20261001_user_stop/resume_plan.json` remain unchanged for reproduction. Their
120-second and 60-second settings describe past runs, not current policy. New
commands use evidence-based allocations through the new supervisor or a separately
validated equivalent. Do not put an unchanged 120-second launcher inside a
six-hour wrapper: invoke the actual computational worker without that inherited
cutoff. Retain memory/disk guards where justified; six hours does not override
other resource constraints.

Batch05 already has all 64 formulas and encoding/object checks; do not rebuild
it. On an explicit future resume, reuse those mathematical artifacts, prepare
new policy-aware native command allocations and independently calibrate the
changed driver/proof-receipt interface. The old proof auditor pins `60s`; its
historical approval cannot be transferred to a modified driver by changing a
constant. The old saved resume argv is therefore superseded as operational
instructions. This policy change starts no native search or proof replay.

On success, early termination or timeout, preserve useful outputs/checkpoints
and report elapsed time, achieved quality, verified guarantees, uncertainty,
unmet requirements and evidence for the decision. Describe unfinished work as
**“not completed within the allocated budget”**. Do not infer general
nonexistence or impracticality of all methods. Computational policy maintenance
changes no mathematical claim or verification status in the ledger.
