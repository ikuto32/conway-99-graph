# Independent six-exception kernel argument

This argument applies to the literal fixed Hadamard support and binary
prescribed-Gram factors. It requires neither outside-column caps nor an
automorphism of a hypothetical target. A support group is exceptional when
some coordinate/fibre count among its three columns differs from one.

Let H have a leading all-one row and the twelve binary support-incidence
rows. For each coordinate a and fibre f, let delta_g be its group count
minus one on groups containing a, and zero outside those groups. The
separately checked Gram marginal equations give H delta=0. The leading
row is the row-total identity; rows for coordinates other than a and its
matched mate are the pair marginals. On the possible support of delta the
a row equals the leading row and the mate row is zero. Thus the bridge
to the augmented global matrix has no omitted equation.

Suppose exactly six groups are exceptional. Restrict H to those six
columns. Rank six forces every deviation to vanish, a contradiction.
At rank five its rational kernel is one-dimensional. Take a primitive
integer generator c. Every integral deviation vector is z*c with integer
z: integers b_g with sum b_g*c_g=1 give z=sum b_g*delta_g. Primitivity is
essential; a nonprimitive generator can have half-integral scalars.

A zero coefficient of c makes that group's deviations zero at every
coordinate and fibre, contradicting exactly six exceptional groups. If a
coefficient has magnitude at least two, the count bounds
-1 <= c_g*z_f <= 2 force all three integral z_f to the same weak sign
(or force them all to zero). The coordinate's three count deviations sum
to zero, so sum_f z_f=0 and every z_f is zero. This applies at every
coordinate, again contradicting exceptional groups. Therefore a possible
rank-five case needs full support and all coefficients in {+1,-1}. The
leading row then requires three positive and three negative coefficients.

For such a full-support generator, a nonzero coordinate deviation forces
that coordinate to lie in every one of the six supports. Group fibre
quotas imply sum_a z_(a,f)=0. If the common intersection has fewer than
two coordinates, all z vanish. Consequently a rank-five sextet is a
necessary survivor only if its primitive kernel has six coefficients of
magnitude one and its common support has size at least two. These are
necessary conditions only, not local-triple or full-factor constructions.

At rank four the kernel has dimension two. Different coordinate/fibre
deviations may lie on different kernel lines, with different zero entries.
The preceding one-dimensional deductions cannot be applied to an
arbitrarily chosen basis vector or to the six-way support intersection.
Such sextets must be retained unless a separately checked argument removes
them. Any lower-rank result would likewise require explicit treatment;
none may be silently discarded by assuming the planned rank histogram.

For this literal support, each unmatched coordinate pair lies in exactly
five of the twenty distinct groups; the six matched pairs lie in zero.
These sixty-six counts are checked directly. Thus six distinct groups
cannot have common intersection of size two, eliminating every remaining
rank-five sign-kernel case on this support.

The independent preparation classifies all38760 sextets through exact
Gram determinants and independent-column Cramer kernel construction. Its
counts are rank6:35587, rank5:3164 and rank4:9. The separate final checker
compares every result to the producer's frozen certificate, reconstructs
each raw minor and validates every null vector and primitive Bezout
identity. Raw binary minors have determinant magnitude at most r! by the
Leibniz formula. Their determinants are checked independently modulo1000003;
since this exceeds twice6!, the bounded signed residue proves the exact
claimed value. Null-vector independence is also checked on the free
coordinates. Every rank-four case is retained, including cases with a
small common support, because the one-dimensional argument does not apply.

The3164 rank-five subsets split into2746 whose primitive kernel has a zero
entry,219 with full support and a coefficient magnitude at least two, and
199 sign-kernel cases lacking a sufficiently large common intersection.
Only nine sextets remain as necessary possibilities for exactly six
unbalanced groups. No local-triple realization of those nine is asserted.

Calibration includes all28 six-vertex subsets of the three-dimensional
binary cube and every full-support primitive zero-sum six-coefficient
vector in{-3,-2,-1,1,2,3}, with exact bounded integer scalar triples.
Changed minors, vectors, primitivity, basis independence, coverage and
the invalid pruning of rank-four cases are rejected. No producer source
is imported and no native solver is called.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_six_group_rank_preparation.py --out acceleration/results/20260930_independent_review/six_group_rank_preparation
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_six_exception_census.py --out acceleration/results/20260930_independent_review/hadamard_six_exception_census
```
