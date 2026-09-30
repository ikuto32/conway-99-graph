# Prepared balanced-triplet parity projection pilot

Source preparation only. Root controls later preflight and launch after
independent encoding and object-calibration gates; no execution follows
from writing this protocol.

Question: does the frozen balanced-triplet necessary parity projection on
the fixed six-prism Hadamard support admit any assignment with at least one
noncyclic group? Pin CNF
92801921a62236effa19b0f6e7463c6f5c1ca2cb0b6957cf7d315a73e0e43fca
and model
a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147:
520 variables, 4,481 clauses, 220 pattern selectors, twenty groups of eleven
patterns, sixty coordinate-pair relations and the final nonconstant clause.
This is not a full factor encoding. No colour phases, full F, outside-cap
feasibility or residual D is decoded.

Scope distinction: the S3 classification and zero-or-three disagreement
relations are necessary for the additional balanced-triplet assumption and
the prescribed full Gram. The final nonconstant clause is necessary for a
balanced full factor WITH every outside-column cap only by the separately
checked cyclic-factor exclusion. Pin that exclusion's independent report
83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70,
claim C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FACTOR-EXCLUSION revision 1. Neither
balance nor cyclicity is assumed WLOG, and no target automorphism is assumed.
The runner executes only this exact formula; implications beyond it require
the independently checked reduction and explicit premises.

Require INDEPENDENT_HADAMARD_BALANCED_PARITY_ENCODING_PASS at
independent_review/hadamard_balanced_parity/summary.json and
INDEPENDENT_HADAMARD_BALANCED_PARITY_OBJECT_CHECKER_CALIBRATION_PASS at
independent_review/hadamard_balanced_parity_object_calibration/summary.json.
Actual hashes are mandatory CLI arguments once frozen. Both reports bind
the exact CNF/model; the object gate binds the same encoding gate. Recheck
all gate-bound source/input hashes. The encoding gate also directly binds
the prior cyclic exclusion needed for the nonconstant-clause implication.

One pristine native CaDiCaL 1.9.5 call: 60 seconds WALL time, 100,000
configured conflicts, 4 GiB address-space cap, 10 GiB proof-file cap, five
seconds termination grace and an 80-second outer Windows guard. Use the
unchanged calibrated native/ext4 helper functions and options, including
the default native seed. There is no CPU time limit. Reserve 21 GiB host and
11 GiB ext4 disk. No retry, solver reset or performance claim.

Preserve the exact command, source commit, locked environment, native/checker
provenance, receipts, stdout/stderr and actual exit status. Stream ASCII
proof output to a fresh ext4 directory, retain it, and copy/hash the entire
produced trace. Preserve transfer, timeout and parse failures. After outer
guard expiry, process state is UNKNOWN until freshly observed.

On SAT retain all 520 signed literals and a candidate decoded_projection.json:
twenty selected selector IDs, pattern indices, six-bit patterns, support-
bound masks, and sixty disagreement counts. The candidate decoder checks
one-hot choices, the nonconstant condition, each difference auxiliary and
the zero-or-three counts. A separate implementation must check the complete
native assignment, every actual clause and the projection. This is only a
parity witness; no full F or target graph follows from SAT.

On UNSAT preserve the complete trace for independent replay. A subsequent
balanced-family exclusion additionally requires exact reduction coverage,
the all-column-caps assumption and the already verified cyclic exclusion.
It would still concern only balanced factors on this fixed support. A
timeout, error, incomplete trace or missing object check is UNKNOWN.

Later CLI uses the root locked uv environment, fresh --out, mutually exclusive
--preflight or --research, and exact --encoding-gate/--encoding-gate-sha256
and --object-gate/--object-gate-sha256 arguments. Preflight performs no research
solver call. Root reviews and launches; this prepared source does neither.
