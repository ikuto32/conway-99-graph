# Native fixed-core joint-factor pilot

Single research invocation only after explicit independent complete encoding
and object-checker calibration gates are supplied by path and SHA256. The
runner has no default approval hash and fails closed if the new scope is
not bound. Root controls research launch. Preflight launches no SAT solver.

Input: exact58,860-variable/203,748-clause joint binary36x60 factor CNF.
Both C1 and C2 are free; C0 is canonically labelled. SAT is a local incidence
factor only, never a99vertex graph. Independent raw clause, native assignment,
scope and integer Gram checking is mandatory. UNSAT requires complete DRAT
replay and the independently checked C0 normalization/encoding equivalence;
then it excludes only factors of this one fixed39vertex core.

Reuse the pristine official CaDiCaL1.9.5 binary and authenticated DRAT checker,
with their recorded build/source provenance and two frozen engineering
calibrations. Shared parser/subprocess/ext4-copy helpers are disclosed.
No historical solver status or old fixed-Q1 exclusion is a premise.

Limits: one300second native call,1,000,000conflicts,4GiB address space,
10GiB per-file limit,5second TERM-to-KILL delay,320second outer Windows
guard. Use GNU timeout/prlimit from the existing calibrated Ubuntu24.04
environment. Stream ASCII DRAT directly to a unique ext4/tmp directory,
then retain and hash-copy exact bytes to the repository. Require at least
11GiB ext4 free and21GiB host free before launch. No automatic retry or
cleanup of evidence. Preserve actual exit10/20/0/124 or other exit and
stdout/stderr, timing, native limits and copy anomalies. An incomplete
trace or timeout is UNKNOWN, never an exclusion.

CLI requires --preflight or --research, --out, --encoding-gate,
--encoding-gate-sha256, --object-gate and --object-gate-sha256. Run through
the locked root uv environment. Proposed output prefixes are
20260930_triangle_joint_factor_native_preflight and
20260930_triangle_joint_factor_native_pilot. Exact gate hashes must come
from the independent reviewers; they are not fabricated here.
