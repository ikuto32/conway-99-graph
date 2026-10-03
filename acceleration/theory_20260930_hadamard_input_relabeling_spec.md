# Fixed-input relabelling census

Question: which of the46080 permutations preserving the six coordinate
matching pairs also preserve the literal20-support set, core and prescribed
Gram, and how do their explicit relabellings act on108 four-exception profiles?

Enumerate all6!*2^6 coordinate maps without assuming any target graph is
invariant. Check each accepted map against all raw C and Gram entries and
the support bijection. Combine with each of the six global fibre permutations.
Every profile must map to a saved profile by transported circuit signs and
deviations. Record explicit maps to minimum case representatives.

Limits:120 cooperative wall seconds, no native calls or numerical arithmetic.
Success means all46080 maps were considered and every retained transformation
preserves the literal input. It gives a candidate exact label-normalization,
not an exclusion or target automorphism assumption. Corrupt non-bijections
and an unmatched-coordinate swap must fail. Scope: fixed support and
Gram-plus-column-cap108-profile family; any remaining D must be transported
by the induced column permutation. Separate independent review is mandatory
before using any map to omit a solver instance.

