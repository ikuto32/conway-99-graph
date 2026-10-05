# Balanced-triplet parity projection, fixed Hadamard support

Question: do the parity constraints of a coordinatewise balanced factor on
the exact six-prism Hadamard support permit any noncyclic support group?
Balance is an extra construction restriction, not a normalization of all
factors. No target or residual automorphism is assumed.

Before any solver call, enumerate all six-permutation multiplicities with
total six and sum of permutation matrices 2J, and all multiplicities with
total five and matrix sum 2J-I. Check the 150 saved balanced local triples.
Produce a necessary projection with twenty groups, eleven parity patterns
per group, and sixty pair constraints. Each pair co-occurs in five groups;
the number of parity disagreements must be zero or three. Require at least
one nonconstant group. Gauge only the common parity flip per group.

One-hot clauses, exact OR definitions, and all 32 five-bit assignments define
the CNF directly; no floating point, pruning, or solver is used in this build.
Save the complete abstract model, raw clauses, counts, source/input hashes,
environment and positive/corrupted controls. Build cap: 60 seconds and small
in-memory finite enumerations. The frozen universe contains all eleven
patterns (constant zero and all ten first-bit-zero weight-three words).

SAT would refute only the proposed parity-projection implication forcing
all groups cyclic, after an independent full assignment/clause/projection
check. It would not provide a coloring factor. UNSAT needs exact complete
proof replay, independent encoding and semantic-necessity checks before any
conditional conclusion. The separately verified cyclic factor exclusion
could then be combined only within the balanced-triplet subfamily.

This experiment builds candidate artifacts only. Research solver limits and
launch will be specified separately after independent verification gates.
