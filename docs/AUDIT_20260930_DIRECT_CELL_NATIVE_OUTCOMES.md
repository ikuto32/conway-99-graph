# Direct-cell native outcome audit

This independent execution audit covers the frozen standalone and count-coupled
`at_least_seven` direct-cell formulas separately. It does not reconstruct their
mathematical encoding: the exact encoding, semantic and object-calibration gates
are explicit, hash-bound premises. Neither formula encodes residual D or supplies
unrestricted support coverage.

Before inspecting a completed result, the CLI requires its exact summary hash and
variant. The fresh auditor imports only the standard library, independently
reconstructs the native command and all resource limits, hashes every saved input
and output, and checks raw receipts against the manifest and launch records.
The configured limits are one call, 60 seconds wall time, 1,000,000 conflicts,
4 GiB address space, 10 GiB trace file, five-second kill grace, 70-second outer
guard, and no retry. CPU and RSS figures remain observed solver statistics, not
independently enforced limits. Counts that exceed a configured conflict limit
are reported literally, without silently rounding them down.

UNKNOWN requires a literal UNKNOWN log without a SAT model, together with either
normal exit zero after the conflict limit, or the exact timeout/SIGTERM boundary.
Complete local partial-trace hashes and the saved ext4 hash/copy receipts are
checked. A fresh read-only ext4 hash is recorded separately, as is a targeted
`ps -C cadical` observation; no broad process inventory is read or saved.
Both partial trace copies remain LOCAL_ONLY and are not contradiction proofs.
The SIGTERM log may omit the closing-proof byte statistic; this absence is
recorded explicitly while both preserved byte lengths and hashes are checked.
No DRAT replay is performed on UNKNOWN traces. A SAT or UNSAT result deliberately
fails this UNKNOWN-specific path and requires its separately appropriate object
or complete-proof audit.

Calibration includes the actual saved positive UNKNOWN case, a clearly labelled
synthetic timeout/conflict parser boundary as needed, and mutations of status,
native exit, dimensions, configured limits, missing statistics, model lines,
outer guard, trace identity/size, command, and retry/promotion fields. Corruptions
must be rejected. Every failure is retained in a new output directory; old
sources, run evidence and gates remain unchanged.

This is a saved-run engineering claim only. UNKNOWN excludes nothing, and no
performance comparison, full factor, target graph or external acceptance is
asserted. The parser/receipt review design follows earlier independently written
UNKNOWN audits, but no earlier audit or producer is imported or executed.
