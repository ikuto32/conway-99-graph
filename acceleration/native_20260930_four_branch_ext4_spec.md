# Preregistered four-branch native ext4 preparation and pilot

This is a separate runner. It never changes the original unrestricted pilot,
its source, base CNF, model, or any completed run. Preparation materializes four
exact base-body-plus-four-unit CNFs and invokes the separately authored byte
checker on each. Preparation and preflight call no research solver. The separate
root controller decides whether to launch the `--research` mode.

The frozen coverage gate states target existence iff at least one recorded
branch is satisfiable, using proved vertex relabeling without an automorphism
assumption. Each branch alone is conditional. Use all four branch names and their
exact recorded recipes in the saved order: a0, a1_complement, a1_cross,
a2_crosses. There are no equality strengthening units in this protocol. Future
strengthening requires a distinct input gate and a new recorded protocol.

Prerequisites are the independent unrestricted encoding/coverage gate, four-case
coverage gate, complete raw SAT-object checker calibration, byte-checker
calibration, pristine native CLI calibration and ext4 proof-path calibration.
Bind exact gate/report/source/input hashes, and replay the independent actual
CNF byte checker immediately before each solver call. Do not infer those gates
from status messages or previous runs alone.

If root chooses to launch: two batches of two simultaneous native calls,
in the recorded order. Each call is limited to 300 seconds, TERM then group KILL
5 seconds later, 1000000 conflicts, 4294967296 bytes of virtual address space,
10737418240 bytes per native output file, and no core dump. Thus simultaneous
native solver address spaces are capped at 8 GiB; Windows orchestration/checking
memory is outside that accounting. No retries or hidden extra research calls.
Maximum four calls and 1200 cumulative solver seconds (at most two concurrently).
The separately measured artifact-copy/check time is outside each solver budget.

Use an exclusive fresh ext4 temporary directory from mktemp. Proofs go directly
to that filesystem, while input/stdout/stderr stay in the existing repository.
Copy each proof back and compare native SHA256 with the Windows streaming hash.
Retain both original and copied artifacts; no cleanup deletion is part of this
experiment. Require at least 81 GiB free on the Windows host and 41 GiB free in
the ext4 filesystem before launch, conservatively allowing four maximum-sized
proofs plus exact copies. Each copy subprocess has a 180-second bound, and each
native checksum subprocess a 90-second bound. Preserve incomplete transfer
receipts as engineering failures. They do not become mathematical outcomes.

The first batch must return before the second starts. If a first-batch raw SAT
status appears, an outer Windows guard expires, or a worker raises an error,
save all current receipts and skip the next batch pending independent review.
Never claim an expired Windows guard proves Linux termination. No checkpoint
is silently resumed or overwritten; a continuation requires a new directory
and explicit new run record.

Actual native exit codes are preserved. SAT saves a complete assignment and
the explicit99by99 decoded matrix as a candidate only; independently check it
with the existing full99 validator on the unaugmented base (sufficient for the
target), plus separately checked branch-clause satisfaction for a branch claim.
UNSAT retains the complete raw proof and remains unproved until independent
authenticated replay on the exact augmented CNF. The overall target is unresolved
unless a target object passes independent checking or every branch has a complete
independently replayed proof under the checked coverage argument.
