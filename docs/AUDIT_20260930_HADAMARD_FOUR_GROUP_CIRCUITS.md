# Independent four-support circuit review

The finite universe is all4845 four-element subsets of the twenty distinct
six-coordinate supports in the frozen six-prism Hadamard matrix L. The review
uses their literal incidence columns, not a proposed restriction on pairwise
intersection sizes. In particular the previously refuted0-or3 intersection
premise is not used.

Adjoin a leading one to a binary incidence column. Any three distinct such
columns are independent: a nonzero dependence would express one binary point
as a strict convex combination of two distinct binary points. At a coordinate
where those two differ the combination is strictly between zero and one,
which is impossible. Two distinct columns and a single nonzero column are
also independent.

For a dependence of four distinct binary points, all four coefficients must
therefore be nonzero. Their sum is zero. A split of one coefficient against
three is impossible because a binary point is an extreme point of the cube.
Hence there are two positive and two negative coefficients. A varying binary
coordinate selects a proper zero-sum subset of these coefficients. It cannot
select one or three coefficients, so it selects a pair of opposite equal
coefficients. If there were two unequal coefficient magnitudes, the only
allowed varying-coordinate patterns would select one of two fixed opposite
pairs; coordinates within each such pair would then be indistinguishable.
That would duplicate two of the points. Thus all magnitudes are equal, and
the unique relation, up to scale, is a permutation of(1,1,-1,-1). Equivalently
two disjoint pair sums coincide. Conversely every such pair-sum equality is
an affine dependence. This proves the rectangle characterization for any four
distinct binary points, not only the saved twenty.

The independent checker calculates the determinant of each quartet's Gram
matrix by fraction-free Bareiss elimination, rather than repeating the
producer's Fraction row-basis algorithm. A nonzero Gram determinant certifies
rank4. For each zero determinant it independently finds an equal-pair-sum
split, checks its literal null vector, and checks a nonzero three-column Gram
determinant; thus the rank is exactly3. Every producer independent minor is
also checked from raw row indices using a separate Leibniz determinant. All
190 pair sums, their170 distinct values, every saved circuit and every one of
the2520 coordinate-restricted quartets are reconstructed independently.

There are21 circuits. Their four-way common intersections have size1 for7,
size2 for13, and size3 for1. Their unions and pair-sum partitions are saved
with exact raw labels. The census is exhaustive for this named finite
population; it supplies no target-wide search denominator.

## Consequence for exactly four exceptional groups

For an actual factor with the prescribed Gram, fixed support and per-column
two-per-fibre quotas, write delta_g[a,f] for the number of fibre-f entries of
coordinate a in group's three columns minus one when a is supported, and
zero outside that support. The separately checked full-Gram marginal theorem
gives M_a delta[a,f]=0 and states that every three columns of M_a are
independent. If precisely four groups are unbalanced and any deviation is
nonzero, all four of its coefficients must be nonzero. In particular a lies
in all four supports. For quartets containing a, the coordinate matrix and
the augmented global incidence matrix have identical column relations:
the omitted coordinate-a row is all ones, and its matched-coordinate row
is all zeros. The quartet must therefore be one of the21 rank3 circuits.

Let c_g in {+1,-1} be its primitive relation. The kernel is one-dimensional,
so delta_g[a,f]=c_g*z[a,f], with z zero outside the common support. The group's
fibre quotas give sum_a z[a,f]=0. If the common support is empty or singleton,
z must vanish and there are no exceptional groups, a contradiction. Thus the
seven singleton-intersection circuits are excluded in this exact-four-group
setting; only the14 saved quartets with intersection size at least2 remain
as necessary possibilities. This does not assert that any of them is realized
by local triples, a Gram factor, outside-column caps or a residual completion.

As a scope control, the checker gives each retained circuit a nonzero formal
deviation array using two common coordinates with opposite vectors(1,-1,0).
It verifies every marginal equation, group fibre sum, coordinate fibre sum
and integer count bound. These are witnesses for the linear/count margins
only, explicitly not binary-factor constructions. They show why this review
does not silently exclude all21 circuits or promote the14 survivors.

Controls exhaust all70 quartets of the3-bit cube and all1820 quartets of the
4-bit cube. Binary squares give dependent positive cases and tetrahedra give
independent cases. Corrupted null coefficients, claimed minor determinants,
quartet coverage, intersection metadata and coordinate certificates are
rejected. Duplicate points and nonbinary collinear points demonstrate why
the theorem's input hypotheses matter. All arithmetic is exact; no solver
or floating-point rank calculation is used.

This is a conditional fixed-support theorem. It does not assume target
automorphisms, prove that four groups can occur, or exclude every factor on
the support. The at-most-three theorem and any balanced-family UNSAT proof
remain separate dependencies; this checker does not repeat that DRAT replay.
