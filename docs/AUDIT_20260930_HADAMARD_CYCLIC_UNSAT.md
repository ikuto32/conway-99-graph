# Independent cyclic-factor UNSAT replay

The audit authenticates the exact26360-variable122394-clause input and entire
29,697,087-byte proof, then replays it with the preserved DRAT-trim binary. Its
source is compared against immutable upstream Git commit
2e3b2dc0ecf938addbd779d42877b6ed69d9a985. Only the explicitly reconstructed
Windows portability block may differ. Compiler, source, patch, build recipe,
build logs and binary are hashed; no dirty submodule source is used or changed.

A truth-table-checked tiny UNSAT formula and valid trace are positive controls.
Missing proof steps, a fresh unsupported unit, a satisfiable changed formula,
and an empty-only proof for the real formula are negative controls. The entire
actual proof must return exit0 and `s VERIFIED`. Exact commands, working
directory, tool identities and raw stdout/stderr are retained for every call.

Native run identity, unique UNSAT status, exit20, formula header, frozen limits,
one-attempt receipt, complete transferred bytes and fresh local hashes are
separately checked. Corrupt native records must fail. Configured limits are not
performance claims. A read-only current process observation is timestamped.

The proof establishes only the cyclic construction subfamily specified by the
independently checked encoding and reduction. It does not exclude all factors
with this support, the six-prism core, or an unrestricted target graph. No
target automorphism is assumed; residual D was not encoded. Independent internal
proof replay is not external mathematical review or peer review.
