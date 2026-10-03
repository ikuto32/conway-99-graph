# Independent written audit: equal outside classes and integer lift budgets

Verifier `/root/checkpoint_audit`, discovery producer `/root/structural`.
Verdict: the exact necessary inequalities below are established by a separate
written derivation. No mathematical worker, enumeration, executable fixture,
formal prover or actual graph realization was used. This is not a search,
target conclusion, sharpness claim or registrar engineering approval.

The complete candidate is
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_CLASS_LIFT_BUDGET_V1.md`,
SHA256 `b04c03b85fa49807256f4ee54a9c6e535e3680077c2ad46bbebeffbf7aa0945e`.
Its bytes remain unchanged. I also read the complete prior independent filter
audit `acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`, SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`,
and filter report SHA256
`7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The explicit material dependency is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`.
The old discovery/ROOT-verifier roles remain intact. I rederive the arithmetic
and endpoint calculation here rather than relying on a metadata status.

## Exact domain and statement

Let A be any symmetric binary integer 99-by-99 matrix with zero diagonal and
every integer row sum 14. Put R=A^2+A-12I-2J over the integers and M=R modulo 3.
Let H be the whole unordered off-diagonal nonzero support of M, let S be its
whole nonisolated vertex set, and put m=|S|. For u in S let c1(u),c2(u) count
the residue-one and residue-two incident entries, d_u=c1(u)+c2(u), and
beta_u=2c1(u)+c2(u). Let C be any nonempty set of k distinct vertices in S
whose actual A-neighborhoods outside S are all identical.

Then every distinct u,v in C satisfies

    R_uv >= L(m) = 13-floor(m/2).

With b(0)=0, b(1)=2, b(2)=1 and W_uu=0, define

    W_uv=(R_uv+b(M_uv))/3  for u!=v.

W is symmetric, nonnegative and integer. Its row sum at u in S is exactly
beta_u/3. Define g(m)=max(0,ceil(L(m)/3)). Every u in C satisfies

    W_uv >= g(m) for v in C\{u},
    beta_u >= 3(k-1)g(m),
    d_u >= ceil(3(k-1)g(m)/2).

These inequalities are necessary for the actual class, not sufficient for a
graph lift. Empty M support is allowed and supplies no such nonempty C.

## Separate endpoint cases and integer intersection minimization

Fix distinct u,v in C. Equality of the two outside words gives an identical
outside neighbor set of size t. Regularity gives the same internal degree
d=14-t at u and v. Write nu=A_uv. Zero diagonal excludes both endpoints from
the common-neighbor universe. Set
P=N_A(u) intersect (S\{u,v}) and Q=N_A(v) intersect (S\{u,v}); both have
d-nu members in a universe of size m-2. Therefore

    CN(u,v) = t+|P intersect Q|
             >= 14-d+max(0,2d-(m-2+2nu)).

For the nonadjacent case nu=0, h=m-2. For the adjacent case nu=1, h=m.
For any integer h and integer d,

    d-max(0,2d-h) <= floor(h/2).

Indeed if 2d<=h the left side is d<=floor(h/2); if 2d>=h it is h-d,
and d>=ceil(h/2) implies h-d<=floor(h/2). This also covers the odd-h
two-middle-value boundary without a continuous relaxation.

Thus, separately,

    nu=0: CN(u,v)>=14-floor((m-2)/2)=15-floor(m/2),
    nu=1: CN(u,v)>=14-floor(m/2).

Since R_uv=CN(u,v)+nu-2, both cases give R_uv>=13-floor(m/2).
The feasible internal degree range may exclude an unconstrained minimizer;
that can only increase this lower bound. Neither H adjacency nor equality
of outside words was used to assert nu. No adjacency automorphism is needed.

## A residue lift gives the exact row budget

The diagonal of R is 14-12-2=0. Since A1=14*1, A^2 1=196*1 and J1=99*1,

    R1=(196+14-12-198)*1=0.

For u!=v, R_uv=CN(u,v)+A_uv-2>=-2. The complete integer possibilities for
each residue start at 0, -2 and -1 for residues 0, 1 and 2 respectively.
Adding b therefore gives a nonnegative multiple of three in every case.
Symmetry of A gives symmetry of R, M and W; W has its separately specified
zero diagonal. There is no floating arithmetic or division in GF(3).

The row sum of b(M) is exactly 2c1+c2=beta. Consequently

    3*sum_v W_uv = sum_v R_uv + sum_v b(M_uv) = beta_u.

The cost of each class partner is its actual W entry, including any positive
lift over the negative residue minimum. Its own negative allowance is not
also spent elsewhere. This avoids the paired-entry subtraction pitfall.

For a class pair, 3W_uv=R_uv+b(M_uv)>=L. W_uv is a nonnegative integer,
so it is at least max(0,ceil(L/3))=g. The k-1 partners are distinct
off-diagonal entries in row u. Summing them gives beta>=3(k-1)g.
Finally beta=2c1+c2<=2(c1+c2)=2d_u, giving the displayed degree ceiling.
The field row sum c1+2c2=0 modulo 3 also gives beta=0 modulo 3, consistent
with the exact row sum and the prior quantized beta<=3floor(2d_u/3) bound.

## Class supply and dependency boundary

The inequalities above start with an actual equal-outside class. They do not
need an assertion that a numerical kernel supplies one. For the disclosed
prior binary-word mechanism, M commutes with A because it is a polynomial
in A and J, and AJ=JA=14J. The whole support condition makes the outside
block of AM=MA read A[outside,S]M_S=0. A support degree-two row has opposite
nonzero labels by its zero row sum, forcing equal neighboring coordinates
in an outside binary row. A support degree-three row has three equal labels,
forcing its three binary coordinates all zero or all one. This uses binary
coordinates: a general ternary word (0,1,2) would defeat the equality inference.

The filter-r1 dependency records this original row-budget/binary mechanism.
Its proof is reconstructed here where used. No lower13, thirteen-defect,
support catalogue, incidence, lambda-one or target claim is a premise.
Selecting one component while other M defects exist does not inherit this
whole-support commutator block. No component-wise extension is asserted.

## Eighteen written falsification boundaries

1. nu=0 removes both endpoints and uses universe m-2, not m.
2. nu=1 removes the adjacent endpoints and reduces each internal set by one.
3. Both parity cases of integer h retain floor(h/2), including its odd middle.
4. Equality of outside membership and degree 14, not an automorphism, gives d.
5. H support adjacency never determines the independent A_uv binary value.
6. The exact R diagonal and 99-term row sum include both 12I and 2J terms.
7. Residue 0 cannot have residual -3 because every off-diagonal R is >=-2.
8. Residue 1 starts at -2 and residue 2 at -1; swapping b's labels is invalid.
9. A positive lift on a bad pair is included once in its actual W cost.
10. Class partners are distinct, with no diagonal or duplicate row expenditure.
11. k=1 gives beta>=0 and degree>=0; it does not force a defect.
12. m=6/7 gives L=10,g=4; a pair needs d>=6, impossible at m=6.
13. m=8/9 gives L=9,g=3; m=10/11 gives L=8 but the same g=3.
14. m=12/13 gives L=7,g=3; a pair needs d>=5 and a three-class d>=9.
15. m=14/15 gives L=6,g=2; beta=6 at degree four meets a pair's cost,
    so this budget alone cannot exclude that boundary or assert sharpness.
16. m=24/25 gives g=1; m>=26 gives g=0, including negative L at large m.
17. A balanced whole K2,6 field support has high beta=9 at m=8: the single
    high-pair required beta cost 9 can meet this filter. It is not refuted here
    and is not asserted to have an actual 99/14 graph realization.
18. Empty M, ternary nonbinary words, components of larger support and unknown
    realizability are retained; none is an executable graph fixture.

All eighteen entries are written checks, with zero executed fixtures or support
enumerations. I find no failure of the exact proposed necessary statement.
The bound is not a new theorem that excludes a defect count. M=0 remains
allowed; novelty, sharpness and realizability remain UNKNOWN. Formal and
external review are absent. Metadata/registrar engineering authorship by this
verifier is unrelated to this different-author mathematical derivation.
