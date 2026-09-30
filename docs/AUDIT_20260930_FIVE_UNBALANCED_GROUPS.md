# Independent exclusion of exactly five exceptional groups

Fix the literal six-prism coordinate support L, with20 distinct supports S_g,
each repeated in three columns. Assume a binary36-by60 matrix F has that
coordinate support and the prescribed full integer Gram. Neither outside
column caps nor the separately proved balanced-family UNSAT result is used.

For each coordinate a and fibre f define n_g(a,f) as the number of occupied
entries in that fibre in the three columns of group g. Put
delta_g(a,f)=n_g(a,f)-1 if a belongs to S_g, and zero otherwise. This agrees
with n_g(a,f)-1_(a in S_g), including absent coordinates. The deviations are
integers, are at least-1 on incident groups, and sum to zero over the three
fibres for each pair(a,g).

The already checked Gram marginal equations imply that every delta(a,f) is
in the kernel of the same13-by20 matrix H whose g-th column is(1,1_Sg).
Indeed, the leading row is the row-margin equation. The row indexed a repeats
it because deviations vanish off the groups containing a. The mate-of-a row
vanishes identically. Each of the ten other coordinate rows is exactly one
of the previously checked summed-Gram marginal equations. No passage from
the per-coordinate systems to H introduces an additional premise.

Suppose the union of nonzero deviations consists of exactly five groups E.
Every deviation restricted to E is in ker(H_E). The five binary support
columns are distinct. For an affine subspace of dimension d, select d ambient
coordinate functionals independent on its direction space. Their joint map
is injective on the affine subspace. Its binary points have at most2^d binary
images. Five distinct binary points therefore have affine span dimension at
least3, so rank(H_E) is at least4.

If the rank is5 there are no nonzero deviations. If it is4, its rational
kernel is a single line. Clear denominators of a nonzero rational generator
and divide by the greatest common divisor to obtain a primitive integer
vector sigma. Bezout gives integer coefficients b_g with sum b_g sigma_g=1.
Any integer deviation on this line is t sigma, and t=sum b_g delta_g is an
integer. This explicitly justifies the lattice step; a nonprimitive generator
would not have this property.

If sigma has a zero entry, that group has zero deviation for every a,f,
contrary to the definition of the five exceptional groups. Otherwise all five
entries are nonzero. The leading row gives sum sigma_g=0. An odd number of
entries in{1,-1} cannot sum to zero, so some fixed index g has|sigma_g|>=2.

For any coordinate a absent from S_g, delta_g(a,f)=0 forces every t(a,f)=0.
For a present coordinate and sigma_g>=2, the bound t(a,f)sigma_g>=-1 and
integrality force t(a,f)>=0. If sigma_g<=-2 they instead force t(a,f)<=0.
The fibre-sum identity gives sigma_g sum_f t(a,f)=0. Three integers of the
same weak sign with sum zero must all vanish. This holds for every a, making
all deviations zero and contradicting exactly five exceptional groups.

Thus no such Gram factor has exactly five unbalanced groups. This is a
Gram-only implication on the one literal support. It excludes neither four
nor six or more exceptional groups, and it is not a support-wide, core-wide
or unrestricted target nonexistence result. It assumes no automorphism or
balance normalization.

The accompanying checker reconstructs H and its relation to all twelve raw
marginal matrices, checks the exact raw Gram constants, and exhaustively
tests every five-point subset of the three- and four-dimensional Boolean
cubes using rational elimination. It checks primitive kernel generators,
explicit Bezout identities and all27 possible coefficient triples in{-1,0,1}.
These finite controls illustrate the universal argument; they are not its
coverage proof for arbitrary cube dimension. Additional controls retain a
four-point square permitting nonzero deviations, a five-point affine circuit
with coefficient magnitude2, an absent-coordinate constraint, a nonprimitive
generator with half-integral coefficient, and a fractional-count example.
Malformed matrices, kernel and Bezout certificates are rejected.

Only standard-library exact arithmetic is used. No producer implementation,
solver, outside-cap screen or balanced-family proof is imported or executed.
