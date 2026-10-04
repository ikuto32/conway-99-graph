# Five binary native controls: independent actual raw review

At 2026-10-04T15:34:58.7205109Z Native completed a distinct raw review of
Root's five separately executed finite controls from plan V4 f82cbcc5.
Result: PASS for these five tiny native protocol/guard cases. This review
approves no scientific formula or arbitrary binary proof parser, and issues
no execution authority. Native ran no solver, proof checker or process query.

Each whole admission's non-map fields and literal command were read; all 51
declared admission input hashes were freshly checked, with common identities
merged only when exactly equal. Each 22-word supervisor vector matches its
plan case; each manifest's six-word child matches the exact suffix. All five
whole manifests, terminals, stdout/stderr, progress and cleanup rows were
read. A clipped combined output was recovered by a separate read of the one
omitted UNSAT progress row. The exact inventories are 7,7,6,6,6 files: 32
physical outputs total, all freshly hashed. No scientific input was read.

| Case | Actual invocation | Child code | Elapsed seconds | Original PGID |
| --- | --- | --- | --- | --- |
| SAT | 0652044c5d414408bc2296052a13773e | 10 | 0.13231918500000006 | 407 |
| UNSAT | 07b0e8bb5a424b748f6695c0ad883144 | 20 | 0.20581944799999974 | 372 |
| Bad checksum | 75cbfd8702eb46c6a1a0714b10626b1b | 1 | 0.1508639069999944 | 367 |
| Unsupported 11 seconds | 02a01b754fe84f528a5f5f1b7d45bb99 | 64 | 0.13298732900000232 | 386 |
| Existing output | 5ef06da59cab4a3b85c49376707d5779 | 1 | 0.1551541830000076 | 358 |

Every terminal has literal SUP status `NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET`,
stop reason `COMMAND_EXITED`, null error, deadline false, hard-limit observed,
matching child/cleanup code, reaped and observed-empty original group, and no
cleanup errors. Each original-group cleanup row has no members, live or
unreadable PIDs. The expected nonzero protocol codes explain SUP's status;
the status is preserved, not renamed or interpreted as a timeout. These
observations are neither a new global process-absence claim nor hard real time.

The SAT stdout has exactly one `s SATISFIABLE` line and one `v 1 2 0`
assignment. Both variables occur once positively and the final zero occurs
once; there are no missing, duplicate or out-of-domain assignments. The
complete two-clause formula is `(1,2),(-1,2)`: under this assignment the first
is true from 1 or 2 and the second is true from 2. Both clauses are checked,
not a solver-status substitute. The solver declares its binary proof stream
closed; the actual proof file is zero bytes with the empty-file SHA256.
An empty SAT proof file is not an UNSAT certificate.

The UNSAT stdout has exactly one `s UNSATISFIABLE` line and records three
additions, no deletions, eight proof bytes and closed proof output. Native
directly read its entire byte array:
`61 05 00 61 02 00 61 00`, SHA256
8bb12aadd23c17bdf36e12987c0b1b1bc32dc31b29840ea821668595602db5e2.
Using the pinned binary encoding, 05 means -2 and 02 means 1. The three
records are `(-2),(1),empty`, with exact terminators, no trailing bytes,
all literals in domain 1..2 and a final empty addition.

The original formula is all four sign pairs on 1/2. To verify -2 by RUP,
assume 2: `(1,-2)` and `(-1,-2)` force opposite units on 1. After -2,
the two positive-2 originals become opposite units on 1. Thus unit 1 is
RUP (assumption -1 conflicts with `(1,2)`), and empty follows by propagation.
This is a complete written check of the actual eight-byte tiny refutation.
The separately proposed Linux checker calls remain distinct qualification;
this native review does not invent their results.

Wrong-checksum stdout shows only the formula FAILED and both launcher and
native executable OK. Stderr is the exact checksum mismatch warning; no
solver banner or proof file appears. The two other guard cases have empty
stdout/stderr. Unsupported duration returns the source's 64 before later
hash/proof work. Existing-output returns 1 before overwrite. Its original
sentinel remains exactly `sentinel` plus LF, SHA256
b5f7e7d285029324d9b3acae19cc05099271454ac98bfc059a92b0581625cd51,
matching the immutable prelaunch plan and all Root admissions. No new proof
file exists in any guard case's output directory. These are scoped directory
observations, not an assertion about unrelated filesystem content.

Raw stdout confirms the qualified CaDiCaL 1.9.5 binary's binary tracing on
both actual solver cases. The three checksum lists remain exactly the
declared three rows with launcher/native identity and the one intentional
bad-formula hash. Root UID/resources/scoped-owner/context observations are
inherited actual admission evidence, not Native recomputation of protected
state. The Linux build receipt 5ae6d562 retains its getc_unlocked warning and
component-only scope. Nine dependency-bearing proof controls still require
their own authentic receipts, exact statuses and distinct raw review.

No historical Windows text gate transfers, no SAT/UNSAT scientific result
is promoted, no I/O performance guarantee is made, and no source/Git/ledger
or original receipt bytes were altered. Target resolution remains UNKNOWN.
