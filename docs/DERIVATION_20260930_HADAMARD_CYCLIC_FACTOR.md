# Candidate twenty-domain cyclic-factor reduction

This is an extra construction subfamily of the one fixed six-prism Hadamard
support L. It is not unrestricted normalization, not a six-prism exclusion,
and imposes no automorphism on residualD or a completed99-vertex target.

The raw L has twenty distinct supports S_p of size6, each repeated in three
columns. Impose that these three columns use a balanced fibre coloring
`c_p:S_p->{0,1,2}` and the colorings c_p+1,c_p+2, respectively. Balanced means
two coordinates of each color. A cyclic relabelling of just the three equal-L
columns allows c_p at its least coordinate to be0, preserving every Gram and
column cap and transporting any possibleD by relabelling. This is a phase
gauge inside the restricted class only. There are90balanced colorings before
the gauge and30after it; the raw package saves every phase transport.

Each coordinate occurs in ten base supports, hence each of its three fibre
rows occurs once in each such triplet and has weight10. Within a column each
coordinate is used once and each fibre twice. Matched coordinate endpoints
never occur together. For any other coordinate pair a<b, the exact collapsed
support Gram gives fifteen co-occurrences across repeated columns, hence five
base supports. A lifted triplet containing a,b contributes exactly one common
column to raw rows(g,a),(h,b) iff

`h-g = c_p(b)-c_p(a) (mod3)`.

The six-prism full Gram requires one for equal fibres and two for unequal
fibres. Therefore its complete1296entries are equivalent, in this class, to
the180 scalar equations over sixty coordinate pairs: difference counts(1,2,2).
The diagonal, same-coordinate and matched-coordinate cases are automatic.
In particular every nonmatching coordinate pair occurs once in fibre0, giving
the full canonical C0 catalog after a column permutation, without assuming it.

Three columns in one triplet are pairwise disjoint. For two distinct triplets,
compare every pair of their three lifted columns. A row can coincide only at
a coordinate common to both supports. The overlap depends on the relative
phase, so its nine values consist of three repeated difference counts. All
outside caps hold precisely when those three counts are at most2. The producer
checks all nine actual overlaps and encodes an incompatible choice pair once.
This accounts for all1710cross-triplet and60within-triplet column pairs.

Consequently the new CNF is intended to encode exactly this restricted full
factor problem, including all Gram entries and outside caps. A SAT factor
would still need residualD and full target validation. UNSAT with a checked
trace would exclude this chosen cyclic factor subfamily only. A failure here
does not exclude the larger ordered60column support family. All these new
equivalence claims remain CANDIDATE until independent review.
