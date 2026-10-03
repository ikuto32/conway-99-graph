# Identity-P mixed-cap redundancy: bounded exact derivation controls

This protocol is frozen before execution. The question is whether a binary
36-by-60 factor with the exact target Gram for an identity-P triangle core
necessarily satisfies `(I+C)F <= 2J`. The three within-fibre perfect matchings
are arbitrary. Identity cross matchings are an explicit restricted-family
assumption, not a normalization of every target and not a target automorphism.

The proposed proof uses zero same-coordinate cross-fibre Gram entries and
nonnegative binary products. Each closed core neighborhood is a coordinate
triangle plus one matching neighbor. No PSD test or floating arithmetic is used.

Execution independently reconstructs C and its Gram from the raw matching arrays
of the four already audited connected identity-P examples. For each example it
enumerates the complete 83,160 supports with six distinct coordinates and two
rows per fibre: choose(12,6) times 6!/(2!^3). It checks all 36 mixed caps and counts
which of these supports also avoid every zero Gram pair. Counts concern this
finite column population only; no collection of columns or full factor is found.
The direct proof, rather than these four controls, supplies the universal scope.

Positive controls exercise all enumerated supports. Negative controls include a
three-row coordinate triangle (mixed cap 3), repeated-coordinate columns, a
nonbinary column, a wrong core entry, a wrong Gram zero, and invalid matching
data. Time limit 120 seconds; no solver, RNG, dependency change or search for D.
On any failure save the failure and leave the proposed claim CANDIDATE.

Outputs include source commit, exact command, pinned input hashes, versions,
finite population counts and proof reference. A different agent must approve
the exact claim. Existing C-TRIANGLE-CORE-IDENTITY-P-CONSTRUCTION r1 and
C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION r1 concern local core caps, not this
factor/mixed-cap statement. This limited ledger comparison makes no novelty or
complete archive/literature claim. Existing CNFs remain unchanged.
