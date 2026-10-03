# Candidate: endpoint-aware outside classes and a nonnegative lift budget

Discovery author `/root/structural`; the actual writing clock is recorded
in the accompanying message and file-hash metadata. Source context
`d0c0dd7db0d3de420b1d718b59122b069df01107` was observed read-only; this
new file is not asserted committed. Status **CANDIDATE**, pending another
author's complete exact derivation and falsification. Mathematical workers,
enumerations, fixtures, formal checks, external review and ledger/index
mutations: zero. Target resolution NONE; novelty and sharpness UNKNOWN.

This is a new discovery separate from my different-author verification
of ROOT's thirteen-defect paper. It was NOT used in that verdict or its
binding. It changes no old filter revision, engine, objective or claim.

## Exact proposed general necessary inequalities

Let A be any symmetric binary integer 99-by-99 matrix with zero diagonal
and integer row sums fourteen. Define R=A^2+A-12I-2J and M=R modulo three.
Let H be the WHOLE nonzero unordered off-diagonal support of M and S its
WHOLE nonisolated vertex set, with m=|S|. For u in S let d_u be its
support degree, c1(u),c2(u) its residue-one and residue-two counts, and
beta_u=2c1(u)+c2(u).

Suppose C is a nonempty set of k distinct vertices in S whose A adjacency
neighborhoods outside S are all identical. For every distinct u,v in C,
the proposed endpoint-aware lower bound is

  R_uv >= L(m), where L(m)=13-floor(m/2).

Put b(0)=0, b(1)=2, b(2)=1, and define the exact integer lift costs

  W_uv=(R_uv+b(M_uv))/3 for u!=v; W_uu=0.

Then W is symmetric, entrywise nonnegative and integer, and its row sum
at u is EXACTLY beta_u/3. Consequently, writing

  g(m)=max(0, ceil(L(m)/3)),

every u in C obeys

  W_uv >= g(m) for each other v in C,
  beta_u >= 3(k-1)g(m),
  d_u >= ceil(3(k-1)g(m)/2).

The last bound is necessary, not sufficient. It is valid for any such
actual class; no support connectivity, adjacency symmetry, incidence
decomposition, numerical kernel or catalogue is assumed. Empty support
remains allowed, in which case no nonempty C is supplied. These statements
neither force a defect nor resolve Conway-99.

## Material context and independent reuse disclosure

The needed original integer budget and binary-word mechanism is revision1
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`, separately
ROOT-verified in
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`;
its independent written audit
`acceleration/audit_20261003_ternary_equal_outside_nine_v1.md` has SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`.
I authored the original discovery, not that independent verdict. The
definitions, zero-row identities and budget facts are proved again below.
No thirteen-defect exclusion, lower13 composition or ROOT integer-lift
statement is a material premise of this new discovery.

## Endpoints improve the common-neighbor calculation by one

Fix distinct u,v in C. Write nu=A_uv in {0,1} and let t be their common
outside-neighborhood size. Their internal adjacency degrees both equal
d_A=14-t. Remove the two endpoints u,v from the universe S. Each internal
neighbor set then has d_A-nu members of the m-2 available vertices.
The endpoints themselves can never be common neighbors, since A has
zero diagonal. Thus the exact common-neighbor count is bounded by

  CN(u,v) >= t + max(0, 2(d_A-nu)-(m-2))
          = 14-d_A + max(0, 2d_A-(m-2+2nu))
          >= 14-floor((m-2+2nu)/2)
          = 15-floor(m/2)-nu.

For the middle inequality, for any integer h and integer d_A,
d_A-max(0,2d_A-h)<=floor(h/2). This is checked by d_A<=h/2 and
d_A>=h/2; restricting the possible degree range can only strengthen
the lower bound. Adding nu-2 in R_uv=CN+nu-2 gives

  R_uv >= 13-floor(m/2),

independently of whether the pair is an A edge. This improves the old
coarse R>=12-floor(m/2) because that estimate did not use both the
zero-diagonal endpoint restriction and the added A_uv term. A support
edge has not been mistaken for an A edge. Both possible binary nu values
were retained and their effects cancel in the residual bound.

## The row budget is an exact nonnegative integer lift

Integer R has zero diagonal and zero row sums. An off-diagonal residual
is at least -2. A field-zero residual is therefore a nonnegative multiple
of three. For residue one its minimum is -2; for residue two it is -1.
Adding b(M_uv) gives a nonnegative multiple of three in all three cases.
Thus W as defined above is an exact symmetric nonnegative integer matrix.

Because b is zero on good pairs and has values two and one on the two
bad labels, its off-diagonal row sum is beta_u. Therefore

  3 sum_v W_uv = sum_v R_uv + sum_v b(M_uv) = beta_u.

No minimum of a paired bad entry is counted twice. The identity includes
its actual positive lift cost; it does not assign that entry its negative
minimum while simultaneously spending a separate positive allowance.

For any pair from C, 3W_uv=R_uv+b(M_uv)>=L(m). Nonnegativity and its
being a multiple of three give W_uv>=g(m). Summing the k-1 distinct
paired costs in row u gives beta_u>=3(k-1)g(m).

The field row sum is zero, so beta_u is a multiple of three; beta_u is
also at most 2d_u. The displayed degree lower bound follows directly.
Equivalently the old bound beta_u<=3floor(2d_u/3) gives the same integer
ceiling. These are exact arithmetic deductions, not a continuous LP.

## Useful boundaries without a new defect-count theorem

For m<=13, L(m)>=7 and g(m)>=3. An equal-outside pair must therefore
have each beta>=9 and support degree>=5. A class of three equal outside
words requires each beta>=18 and support degree>=9. These are stronger
than the earlier coarse pair boundary m<=11 and the coarse triple mass
twelve; they do not amend those earlier independently verified claims.

At m=6 or7, L=10 and g=4. Any equal-outside pair would require each
support degree at least six. This cannot occur in a six-vertex support,
and in an order-seven support would require universal endpoints. No
claim about a field-only signed graph or a general residual count follows.

At m=8 or9, L=9 and g=3. At m=10 or11, L=8 but the same g=3 is
forced by integer divisibility. At m=12 or13, L=7 and still g=3.
At m=14 or15 the value drops to L=6,g=2. A degree-four pair with beta
six can meet that necessary cost: this boundary is retained, not wrongly
excluded. At m=24 or25 L=1,g=1; at m>=26 the lower bound has g=0
and the class inequality by itself supplies no positive degree restriction.

The outside-word source can be commutation: because S is the WHOLE M
support, A[outside,S]M_S=0. A degree-two row forces equal coordinates
at its two neighbors; a degree-three row forces three equal binary
coordinates. Once an actual class is established, the budget above
applies to every member. Arbitrary ternary kernel vectors do not have
the same equality interpretation, and no finite list of such vectors
or support shapes is asserted complete here.

## Fourteen written falsification boundaries for later review

1. Both graph endpoints are removed from the internal-neighbor universe;
   their own diagonal entries cannot create common neighbors.
2. Internal degrees agree because actual integer degree is exactly14
   and the outside neighborhoods agree in cardinality and membership.
3. Both nu=0 and nu=1 are checked; no M-support edge implies A adjacency.
4. The integer minimization uses floor, not a floating half-degree.
5. b(1)=2 and b(2)=1 represent two different exact negative minima.
6. Every cost is nonnegative and divisible by three, including good pairs.
7. The exact row sum beta/3 prevents spending a paired entry's own
   negative allowance twice.
8. The k-1 class pairs are distinct off-diagonal entries, never a diagonal
   or a repeated member of the class.
9. The k=1 class gives only the trivial beta>=0, as required.
10. The integer ceiling persists at m=12/13; m>=26 deliberately loses
    the positive bound. Neither boundary is asserted sharp or realized.
11. The degree bound uses beta<=2d or the equivalent quantized bound,
    and does not identify support degree with degree14 in A.
12. Binary outside-word equality needs a genuine class; a ternary
    word012 or a selected component with other defects does not supply it.
13. The balanced whole K2,6 field example at m=8 has high beta nine;
    an equal high pair's single required cost nine can meet this filter.
    It is not falsely refuted by the new pair inequality, nor is its
    actual adjacency lift asserted to exist.
14. M=0 is allowed. No target construction, general nonexistence, rank
    obstruction, optimum, measured fixture or formal/external review follows.

The reusable conclusion is an exact nonnegative integer row budget on
all equal-outside classes. It may replace repeated single-pair estimates
in a future separately reviewed proof, but it is not used to retrospectively
alter any existing report or acceptance gate. This new paper remains
CANDIDATE outside the frozen371 publication, with zero mathematical execution.
