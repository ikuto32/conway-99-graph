# Prepared four-worker exact-eight Python build orchestration

This is a new, unexecuted formula builder. It does not run SAT/native solvers,
change the frozen campaign producer, alter the formula format, edit the ledger,
select research cases, or infer any exclusions. All earlier sources remain intact.

CLI:

```text
plan|build --selection PATH --selection-sha256 SHA --attempt-id LABEL
 --seconds 1..120 --workers 1..4 --out NEW
```

Accept exactly 1..64 caller-ordered distinct IDs in the existing authenticated
ALL792 selection schema. Bind the entire selection and its authorization record,
unchanged producer and local source closure, raw population gate and manifest.
Do not subtract prior outcomes or silently deduplicate. Every output directory is
new; each case has a stable case ID and a caller-prefix plus case-index attempt ID.
Any later continuation requires a new explicit selection and new output/attempt.

Build exactly the old producer command, arguments and source. No in-process
producer import or shared producer globals exist across cases. Parent imports only
the frozen sequential orchestration utility module. The producer and helpers write
inside their own case folders and share read-only evidence. The producer itself
does run a short `git rev-parse HEAD` provenance child; that read-only descendant
is why killing only the Python producer is insufficient. No producer commands are
executed during this source preparation.

On Windows, allocate a separate Job Object per worker with
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE and no breakaway flags. Start a minimal Python
worker with file-backed stdout/stderr and a one-line stdin barrier. Associate it
with the job *before* releasing RUN. Only then can it invoke the unchanged producer;
the producer and its Git child inherit job membership. Assignment failure kills
and waits for the unreleased worker, saves all logs, and stops the batch. There is
no fallback to uncontained production. Windows prior to nested-job support or a
restrictive enclosing job may refuse this preparation at runtime.

The coordinator launches at most four simultaneous producer trees. It polls every
25 ms and never hashes models or validates child outputs while a producer is
active. One absolute monotonic deadline starts at invocation entry and includes
input checks and preparation; no deadline is reset per case. Reaching it stops all
new launches and terminates every active job. First nonzero producer exit, launch
error, or supervisor error has the same stop-and-cleanup behavior. Every launched
worker is waited on, every job is queried for zero active descendants, then all
handles and logs are closed. Cleanup attempts continue even after another child's
cleanup error. A cleanup error prevents an ordinary complete summary.

The 120 seconds is the maximum **build-work deadline**. Process termination,
reaping and exact receipt hashing may extend the invocation's return time and are
reported separately. This is necessary to avoid leaving a process running merely
to return at a nominal deadline. This source does not claim a hard 120-second
function-return guarantee under operating-system stalls. The OS backend must be
tested with harmless live canaries before any real build; preparation here tests
only AST, structure and a deterministic mocked lifecycle.

Only normally exited, fully reaped children with exit code zero are considered for
completion. Rehash every child input/output, all eight standard formula artifacts,
source case/attempt identities, and full count digest. Retain all partial outputs
and logs without deletion. Completed records are finally emitted in caller order,
not completion order. A partial parallel result may have holes; pending IDs are
an explicit set complement preserving caller order, never a suffix inferred from
the number of completed cases. Every completed record uses the existing schema so
the independent complete-clause checker is unchanged mathematically. Its outer
provenance review must explicitly accept this new parallel plan and receipts.

Preparation controls use deterministic fake children to cover success with
out-of-order completion, one/four worker boundaries, deadlines, nonzero exits,
launch errors, supervisor errors and cleanup errors. They inspect command bytes,
1..64 selection bounds and Job Object ctypes layouts. They do not invoke Windows
job APIs, Git, the campaign producer, native executables, or any formula build.
No measured speedup or promise that 64 cases fit in 120 seconds follows.

Microsoft API references consulted for this design:

- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-setinformationjobobject
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information

These specify inherited child membership, nested jobs, kill-on-close behavior,
the extended-limit information class and Windows structure field types. No API
success or platform compatibility is inferred solely from reading documentation.
