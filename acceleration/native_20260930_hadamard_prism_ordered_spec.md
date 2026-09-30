# Prepared broader fixed-Hadamard colouring pilot

Question: does the exact saved six-prism Hadamard support admit any binary
36-by-60 factor with the full prescribed Gram, two-per-fibre column margins
and all 1,770 outside-column caps? Use only the independently justified
strict option-rank ordering within its 20 identical-support column groups.
All 90 colourings per column remain available before those order constraints;
there is no cyclic-triplet, bit-complement or target-automorphism assumption.
Residual D is unencoded. This is one fixed support, not the whole core.

Selection: of the five frozen support scouts, connected-00 has a checked
local obstruction and connected-01/02/03 have checked integer Farkas
certificates. The six-prism support has an exact fractional equality witness
and no established whole-support exclusion. The separately excluded cyclic
colouring subclass does not resolve this broader model. The trial is a
single new bounded search, not a retry of that subclass formula.

Pin the 595,464-variable / 3,336,642-clause formula
51cedaa0e54ab569e6ec4b8ad19fb17136ad5e8a9bdbd751b994903e4024f5df,
model 85f2008d34c5f089e04e87306462a10be4919c582da6b6a2303523f5f6ea737a
and scope 5d8cac247339006994035ac21c379edafdb8b55ec11213eba2ac22859430b466.
Require the independent encoding gate
INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_CNF_PASS and complete-object
calibration gate
INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_OBJECT_CHECKER_CALIBRATION_PASS.
Their planned paths are independent_review/hadamard_prism_ordered_cnf/summary.json
and independent_review/hadamard_prism_ordered_object_calibration/summary.json.
Pass actual frozen SHA256 values on the CLI; no placeholder or guessed hash
is accepted. Both gates must bind all three exact raw inputs, and the object
gate must bind the same encoding report. All transitive gate input hashes are
rechecked. The independent ordering premise is pinned separately.

One pristine native CaDiCaL 1.9.5 attempt is permitted after root launch
approval: 300 seconds wall time, 2,000,000 configured conflicts, 4 GiB address
space, 10 GiB proof-file limit, five seconds termination grace and a
320-second outer Windows guard. Retain the existing calibrated ext4/native
helpers and options; default seed is unchanged. Reserve 21 GiB host and
11 GiB ext4 disk before invocation. No automatic retry or speed claim.
The initial task's phrase "300 CPU seconds" was corrected before execution:
the existing control is wall time and there is no CPU rlimit. CPU time may
be reported only from actual native output, distinct from the wall limit.

Stream the ASCII trace to a unique ext4 directory, preserve its original,
then copy and hash the entire produced file. Save actual command, source
commit, locked environment, tool/source/input hashes, stdout/stderr, native
exit code, subprocess receipt and any transfer/parser/decoder failure. An
outer-guard expiration leaves process state UNKNOWN until a fresh observation.
Never describe an incomplete trace as a proof.

SAT creates only an unchecked candidate factor. Require the entire 595,464
native assignment, all 3,336,642 clauses and an independent raw factor check:
exact fixed L, all 1,296 Gram entries, margins, all column caps, actual mixed
caps, the 40 option-rank comparisons and canonical-C0 reordering. The producer
decoder is not its own verifier. Even a valid factor requires residual D and
independent full99 validation before any target-resolution claim.

UNSAT requires a complete independent proof replay with the exact CNF,
solver/checker provenance, hashes and independent encoding/ordering coverage.
Only then does it exclude this particular support modulo permitted column
relabellings; it does not exclude other supports, the six-prism core or SRG99.
UNKNOWN, errors and timeouts exclude nothing. Preserve all raw outcomes.

This preparation performs no execution. Later invocation uses the locked
root uv environment, a fresh --out directory, mutually exclusive --preflight
or --research, and explicit --encoding-gate, --encoding-gate-sha256,
--object-gate and --object-gate-sha256 arguments. Preflight checks authenticated
inputs and disk/mount conditions but makes zero research solver calls. Root
owns research launch after independent gates and source review.
