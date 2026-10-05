# Independent balanced-triplet S3 and parity reduction

This audit addresses the producer's exact balanced-triplet projection on the
saved six-prism Hadamard support. Coordinatewise balance is an additional
assumption, not a consequence of the full Gram equations established here.
The final nonconstant clause additionally uses the independently checked
cyclic exclusion with outside-column caps. Thus the complete formula is a
necessary condition for a balanced prescribed-Gram factor **with those caps**,
and in particular for a target extension with this fixed support and balance.

For one support group let pi_i map its three raw columns to the colour of
coordinate i. Coordinatewise balance says pi_i is a permutation of three
symbols. Every column contains two coordinates of each colour, so the sum of
these six permutation matrices is 2J.

Each even permutation matrix intersects each odd permutation matrix in exactly
one cell: their relative permutation is a transposition with one fixed point.
The nine even/odd pairs account for the nine distinct cells. If e_0,e_1,e_2
and o_0,o_1,o_2 are their multiplicities, every cell equation therefore has
the form e_i+o_j=2. All even multiplicities equal alpha and all odd
multiplicities equal beta, with alpha+beta=2. Nonnegative integrality gives
(alpha,beta)=(2,0),(1,1),(0,2). The number of labelled coordinate assignments
is 90+720+90=900. Permuting the three columns acts freely, leaving 150 unordered
triples: 30 cyclic and 120 mixed.

For two nonmatching coordinates a,b, each of their five common support groups
contributes the relative permutation pi_b composed with pi_a inverse to their
three-by-three colour-pair Gram table. The required total is 2J-I. Let t be
the identity multiplicity. Its intersections with the three odd permutations
are the diagonal cells, so each odd multiplicity is 1-t. The two nonidentity
even permutations intersect those odd permutations off the diagonal; their
multiplicities are each 1+t. Therefore t is 0 or 1. Exactly three or zero of
the five relative permutations are odd. This proves the pair constraint:
the number of parity disagreements over the five support groups is 0 or 3.

A common column relabelling composes every pi_i on the right by one permutation.
It flips all six parity bits together when that permutation is odd. Consequently
we may choose the first coordinate bit to be zero. The allowed patterns are
the all-zero word and the ten weight-three words with first bit zero. This is
a local relabelling of the three identical-support columns, not an automorphism
assumption about a target graph or its residual D.

When a group's six permutations all have the same parity, relabel its columns
using pi_0 inverse. Every relative permutation pi_i composed with pi_0 inverse
is even, hence a cyclic colour shift. The three resulting columns have colours
c_i+r modulo three and c_0=0. Performing these independent column relabellings
for all groups preserves full Gram, outside-column caps and any residual
completion by conjugation. Therefore an all-constant parity choice would lie
in the already excluded cyclic construction. The final clause requiring at
least one mixed group is sound **using that cap-dependent exclusion**.

The independent checker enumerates all 6^6 ordered six-permutation tuples and
all 6^5 ordered five-permutation tuples, rather than the producer's multiset
enumeration. It reconstructs the 150 unordered local triples from these tuples,
checks their raw-domain identities, and checks every even/odd cell intersection
and all 180 ordered cyclic phase transports. These finite checks supplement
the universal cell-equation proof above.

The CNF has 220 primary selectors: eleven patterns for each of twenty groups.
An at-least-one clause and every pairwise at-most-one clause impose each
one-hot choice. For each of 60 nonmatching coordinate pairs there are five
auxiliary disagreement bits. Each auxiliary is defined in both directions
as the OR of the six selectors that disagree on the pair. The 21 forbidden
five-bit assignments give the exact relation that its weight is zero or three.
Finally the 200-selector clause requires a nonconstant group. This reconstructs
520 variables and 4,481 clauses, with no residual graph and no full factor.

The object checker validates all native v-lines, all 520 signed variables,
all actual clauses, and independently decodes the twenty raw parity patterns
and sixty disagreement counts. A SAT object proves only this finite parity
projection feasible. An UNSAT result requires a complete independently replayed
proof before it can exclude the balanced fixed-support family with caps; it
would not exclude unbalanced factors, another support, its core, or Conway-99.

Calibration includes complete one-hot, OR, and weight-relation truth tables;
positive generic assignment fixtures; the real all-constant assignment failing
only the required-mixed clause; malformed models, clauses, native streams,
assignments and projection records. A synthetic full-size codec fixture is
explicitly not a satisfying research assignment.
