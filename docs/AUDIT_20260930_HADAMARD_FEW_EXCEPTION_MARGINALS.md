# Full-Gram marginal constraints require at least four exceptional groups

Fix the literal six-prism Hadamard support L and let F be a binary36-by60
factor with that coordinate support and the prescribed Gram K=FF^T. A group
means one of the twenty six-coordinate supports, repeated in three raw columns.
For coordinate a and fibre f, set t_g equal to the number of those three columns
choosing row12f+a; this variable is defined for the ten groups containing a.
Write delta_g=t_g-1. A group is unbalanced if any such coordinate/fibre deviation
is nonzero.

The diagonal K[(f,a),(f,a)]=10 and binary F give row sum10, hence sum_g delta_g=0.
For each nonmatched coordinate b, sum the three Gram entries against the three
fibres of b. Their prescribed values sum to1+2+2=5. The exact coordinate support
says precisely one b-row is selected in every column containing b, so

    sum_(g containing a,b) t_g = 5.

Exactly five raw groups contain a and b. Thus the eleven-by-ten matrix M_a
consisting of an all-one row followed by the ten nonmatched-coordinate
incidence rows satisfies M_a delta=0. This is a literal double-counting identity;
it does not use an intersection-size assumption or an automorphism.

The ten columns have leading entry one and distinct binary tails. Distinct
supports containing a cannot differ only at a or its mate, since all such
supports contain a and exclude its mate. Every set of at most three of these
columns is linearly independent over Q. For three, a dependence with all three
coefficients nonzero and sum zero would express one distinct binary tail as a
strict convex combination of the other two after separating signs. At a
coordinate where those two tails differ, that combination is strictly between
zero and one, so it cannot be a binary vector. Two columns are independent
because their leading entries agree and their tails differ. A single column
is nonzero.

Therefore any nonzero rational vector in ker(M_a) has at least four nonzero
entries. If F had at most three unbalanced groups globally, every coordinate
and fibre deviation vector would have support at most three. All would be
zero, and F would be entirely balanced. This implication is independent of
the balanced-CNF UNSAT result. The executable reconstructs all twelve matrices,
checks all2100 nonzero minor certificates with a separate Leibniz determinant,
and finds its own minors and exact ranks. Rank six is recorded but is not
needed for the support-at-least-four proof.

The balanced encoding also asks for two entries per fibre in each raw column.
These quotas already follow from K. For a fixed fibre, let k_d be its column
counts. The row diagonals give sum_d k_d=120; the sum of that12-by12 Gram block
is240, giving sum_d k_d^2=240. Hence sum_d(k_d-2)^2=240-480+240=0, so every
k_d=2. Thus the separately independently checked balanced-Gram exclusion
covers the balanced factors produced by the preceding implication.

Two conservation identities will also be useful for later fixed-group
arguments. For each coordinate in a group, sum_f delta_(g,a,f)=0 because its
three columns each choose exactly one fibre. For each group and fibre,
sum_(a in support_g) delta_(g,a,f)=0 because its three columns each have two
entries in that fibre, giving six entries in total. The latter identity uses
the column quotas derived above. These identities alone assert no existence.

Combining the implication with that exact balanced-family exclusion rules out
all factors on this fixed support having zero, one, two or three unbalanced
groups. Any factor on the support, if one exists, must have at least four.
This is not a full-support or core-wide exclusion and is not a target result.
It introduces no assumption that every factor is balanced.

Controls include every set of at most three distinct vertices of the three-bit
cube after adjoining a leading one; duplicate columns and removal of that
leading row are rejected. A four-corner binary square has the exact relation
(1,-1,-1,1), so the abstract argument does not extend to four columns. A literal
two-exception row-margin fixture is checked against all396 summed-Gram
identities and has nonzero marginal residuals, illustrating the difference
between row margins and the full Gram conditions.

The producer's separate64 filtered local catalogues and190 row-margin-only
pairing census are outside this audit. Its proposed0-or3 support-intersection
premise is already refuted by a separate raw witness and is unused here.
The prior DRAT proof is authenticated as a separate dependency; this audit
does not claim a new proof replay or a new solver run.
