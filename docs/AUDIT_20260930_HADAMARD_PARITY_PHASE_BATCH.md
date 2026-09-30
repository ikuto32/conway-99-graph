# Independent sampled parity and phase-screen checking path

This checker is for a bounded sample of complete parity assignments of the
authenticated fixed-support formula. Neither a sample nor a list of full-pattern
blocking clauses is an exhaustive cover. No balance normalization for arbitrary
factors or target automorphism is assumed.

The checker rebuilds the original 4,481 clauses with the frozen independent
parity reconstruction and directly adds the sixty raw support conditions. It
compares the exact 4,541-clause base bytes. For a sample case, it authenticates
the ordered prior raw projections and adds exactly the negatives of all twenty
chosen selectors from each. The DIMACS header and entire body must agree.
Every native literal, JSON assignment entry, actual clause, selected pattern,
raw coordinate-pair count and support condition is checked. Sampling blocks
are distinguished from mathematical exclusions: only a checked exact phase
contradiction supports the latter.

The general phase derivation is independently reconstructed from the twenty
raw supports and selected patterns. There are 120 phase coordinates. For each
group the first phase is fixed to zero. A constant group contributes its one
six-phase sum; a mixed group contributes the sums of its two three-phase sign
classes. For each nonmatching coordinate pair, the five relative intercepts
are `t_b - s_b*s_a*t_a`. The odd and even sums are both retained, including
empty odd sums. This gives exactly `160 + mixed_groups` homogeneous rows.
The only rejection functionals in the initial batch are the six pairwise
differences within each mixed group's two sign classes. Constant groups have
no such blanket-distinctness condition.

Each pair row records all five incident groups as its parity dependency, even
if some groups contribute no term to the chosen sum. This batch uses only full
twenty-selector blocks; no shortening is inferred from sparse coefficients.
The independently checked general-necessity report is a premise of the screen.

For an exclusion, the checker evaluates all 120 coordinates of the supplied
row combination modulo three and compares them to an independently derived
required-nonzero mixed-group difference. Since every row has right-hand side
zero, equality supplies an exact contradiction. A separate reverse-column
elimination checks rank and nullspace; the explicit combination remains the
proof path for the exclusion. A surviving linear screen is not a full factor.

Controls include both previously checked raw native projections on their
proper formulas, full-size synthetic codec inputs explicitly labelled as such,
small clause-composition controls, the prior authenticated exact phase
obstruction, and deliberate changes to native status/literals, clauses,
ordering, phase rows, nonzero-functionals and row-combination coefficients.
No full research factor is invented as a positive control.

Only the frozen independently authored original parity parser/reconstructor is
imported; no producer source, phase generator, elimination code or native
runner is imported. The final calibration report records exact producer,
protocol and checking-source hashes before any authorized batch launch.
