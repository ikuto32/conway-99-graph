# Candidate: the two possible whole supports at twelve ternary defects

Discovery author: `/root/structural`. Actual writing clock:
`2026-10-03T09:50:28+00:00`. Source context:
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`; this new working file is not
asserted present in that commit. Status **CANDIDATE**, pending a different
author's complete exact derivation and falsification. Executed mathematical
commands, finite enumerations, fixtures, formal checks, ledger changes and
index changes: zero. Target resolution: NONE; novelty: UNKNOWN.

## Exact proposed statement and scope

Let A be any symmetric binary integer 99-by-99 matrix with zero diagonal
and exactly 14 ones in each integer row. Define

  R=A^2+A-12I-2J over the integers; M=R mod 3=A^2+A+J over GF(3).

Let H be the WHOLE nonzero unordered off-diagonal support of M, let S
be its WHOLE nonisolated vertex set, let m=|S|, and let e=|E(H)|=F3.
The proposed necessary classification is:

  If F3=12, then H is K2,6, or H is K6 with one perfect matching deleted.

This is a classification of necessary whole-support shapes. It does not
assert that either shape has an adjacency-polynomial lift. It does not
exclude an arbitrary component in a larger residual, classify all signed
labelings, assume an automorphism of A, force a defect, or resolve the
target. In particular it is not a general twelve-defect nonrealizability
claim. The two remaining integer-lift questions are separate statements.

## Sole material dependency, repeated exactly

The sole material result used is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`.
Its independent ROOT audit is
`acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`, SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`;
its filter report is
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The original discovery source is
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
The small amount of that filter needed here is repeated for review.

Integer R has zero diagonal and zero row sums. Its good entries are
nonnegative multiples of three. Residue-one and residue-two entries have
integer minima -2 and -1. At a support vertex u of degree d_u, with c1
and c2 such labels, write beta_u=2c1+c2. The field row sum is zero, so
beta_u is a multiple of three and

  beta_u <= 3 floor(2d_u/3).

A paired good term is at most beta_u; a paired residue-one term is at
most beta_u-2; a paired residue-two term is at most beta_u-1. A paired
positive bad entry is not also available as a negative allowance.

Two distinct vertices with identical outside-S adjacency neighborhoods
have

  CN(u,v) >= 14-floor(m/2),
  R_uv >= 12-floor(m/2)+A_uv.

At m<=11 this contradicts support degree at most four at either endpoint,
regardless of the paired residue: CN>=9 gives R>=7, whereas its good
budget is at most six and its bad remaining budget at most five.

Commutation AM=MA, together with zero outside-S M rows, gives

  A[outside S,S] M[S,S] = 0.

A degree-two support row has opposite labels, forcing its two neighbors'
outside binary coordinates equal. A degree-three support row has three
equal labels; their three binary coordinates must all be zero or all be
one. Thus, whenever m<=11, every neighbor of a degree-two or degree-three
support vertex has degree at least five. These are support degrees, not
the integer degree fourteen of A.

## Order bounds and the m=12 boundary

A nonisolated support vertex cannot have degree one: its only nonzero
field entry could not sum to zero. Hence minimum support degree is two.
Under e=12 this gives m<=12, while simplicity gives m>=6 because five
vertices have at most ten edges.

At m=12, total degree 24 forces every degree to be two. Each such row
has one label of each residue and beta=3. Pick a degree-two vertex and
its two distinct neighbors u,v. Their outside neighborhoods coincide;
both u and v also have support degree two. The general pair bound now
gives CN(u,v)>=8 and R_uv>=6. This is incompatible with a good upper
budget three or a bad upper budget at most two. Therefore m=12 is
impossible. This uses a separate degree-two budget calculation: it does
not improperly extend the degree-at-most-four filter beyond m=11.

For the rest of the proof m<=11, so the high-neighbor restriction applies.
The exact total degree is always 24.

## Cases with a degree-three vertex

Choose a degree-three vertex w. Its three distinct support neighbors have
degrees at least five, so

  24 >= 3+3*5+2(m-4) = 2m+10.

Thus m<=7, while a degree-five vertex requires m>=6.

At m=6 the three high neighbors have degree five and are universal.
All three other vertices, including w, therefore have degree at least
three. This already costs 3*5+3*3=24, so all three other degrees equal
three. The literal support is a high triangle joined to three mutually
nonadjacent vertices: K3 joined to three isolated points. It has twelve
edges and degrees (5,5,5,3,3,3).

At m=7 equality is forced in the displayed degree lower bound. There
are three degree-five highs, w of degree three, and three degree-two
vertices. All low incidences go to the highs: w joins all three, and
each degree-two vertex joins two highs. The nine low incidences leave
six high incidences, so the highs form a triangle. Each high has exactly
two neighbors among the three degree-two points; that bipartite part
is K3,3 with a perfect matching deleted. This is the sole literal shape
in this branch, with degrees (5,5,5,3,2,2,2).

Both shapes fail the integer pair budget. The row of w makes all three
highs' outside neighborhoods identical. An edge between two highs is
a BAD M pair. At m=6 or 7 their CN is at least eleven, so their R is
at least nine even if that pair is not an A edge. A degree-five endpoint
has beta<=9, but the paired bad entry is at most beta-1<=8 (or beta-2
for residue one). The contradiction covers every nonzero sign on that
high-high pair. No degree-three case remains.

## Cases with a degree-two vertex and no degree three

A degree-two vertex has two high neighbors of degree at least five.
Consequently

  24 >= 2*5+2(m-2) = 2m+6,

so 6<=m<=9. Every vertex is now either low of degree two, medium of
degree four, or high of degree at least five. If h is the number of
highs and r the number of mediums, the excess above the baseline 2m is
at least 3h+2r. There are at least two highs. Every degree-two vertex
uses both its edges on highs.

### m=9

The excess is six. Exactly two highs of degree five and seven lows of
degree two are forced. Every low joins those two highs, giving each
high at least seven neighbors, a contradiction to degree five.

### m=8

The excess is eight. There are exactly two highs, and at most one
medium. With a medium, all five other low vertices already use both
edges on the two highs; the medium can join at most the two highs and
no other medium, so it cannot have degree four. Thus there is no medium.
All six low vertices join both highs. A possible high-high edge would
raise BOTH high degrees from six to seven and give thirteen edges.
Since e=12, that edge is absent and the support is exactly K2,6.

### m=7

The excess is ten, so there are two or three highs.

If there are three, their total degree is sixteen, their degrees being
(6,5,5), and the other four degrees are two. The low-high incidences
total eight, leaving eight high-high incidences. Three highs can supply
at most six such incidences. This case is impossible.

If there are two highs, there are at most two mediums. With one medium,
its possible neighbors are only the two highs; with two, each can join
the highs and the other medium, at most three points. The remaining
degree-two points are saturated by the highs. Neither medium possibility
can attain degree four. With no medium, all five lows join both highs.
The support is K2,5 with or without the high-high edge, giving ten or
eleven edges, rather than the required twelve. Thus no m=7 degree-two
case exists.

### m=6: the (5,5,4,4,4,2) case is retained explicitly

Each high has degree five and is universal. Three or more highs would
make every remaining vertex adjacent to at least three highs; with no
degree three, those remaining degrees are at least four. For three
highs the total is already at least 3*5+3*4=27, and for four or more it
is still larger than 24. There are therefore exactly two highs.

The remaining four degrees are two or four. Their sum is fourteen,
so exactly three are four and one is two. Let the highs be a,b, the
three mediums be c,d,f, and the low be w. The low has only a,b as
neighbors. Each medium has both highs and must also have the other
two mediums. The literal support is

  K2 joined to (K3 union one isolated point),
  degrees (5,5,4,4,4,2), with 1+8+3=12 edges.

This shape is NOT omitted or declared impossible by degree totals.
The degree-two row of w forces a,b's outside neighborhoods equal.
Their M pair is a support edge, and m=6 gives CN(a,b)>=11 and R_ab>=9.
Each degree-five high has remaining bad-pair budget at most eight.
Therefore this shape fails the same exact integer pair filter, regardless
of the nonzero high-high label or the binary value A_ab.

All degree-two cases except K2,6 have now been excluded.

## Cases without degree two or three

Minimum support degree is four. The total 24 gives m<=6; the initial
simplicity bound gave m>=6. Hence m=6 and every support degree is four.
The complement within these six vertices has every degree one, and is
a perfect matching. The support is K6 with that matching deleted.
No other order, component decomposition or degree sequence is possible
in this last branch.

The signed row equations would additionally require two labels of each
residue at each degree-four vertex, but the present discovery does not
classify their signed two-factors or attempt their integer lift. ROOT's
separate octahedral lift thread remains a different discovery and is not
a premise here.

## Exhaustion, falsification boundaries and separation from lift claims

The branches exhaust m=6,...,12 without a catalogue: m=12 is handled
first; degree three forces m=6 or 7; degree two with no degree three
forces m=6,...,9; and neither low degree forces m=6. This proves the
proposed two-shape necessary classification, pending separate verification.

1. The m=12 pair uses beta=3 at degree two. A degree-four good-pair
   budget six can meet the coarse m=12 residual bound six; that broader
   filter is deliberately not asserted.
2. Degree-three support rows require binary outside words. A ternary
   word (0,1,2) is not a permitted adjacency word and would break the
   asserted equal-neighborhood propagation.
3. At m=6 the degree-three branch uses universality to raise the two
   initially unclassified degrees to three; simply leaving them at two
   would produce an incorrect degree count.
4. At m=7 that branch explicitly derives all three high-high edges by
   the nine low and fifteen high incidences; it does not assume a triangle.
5. The high-high bad-pair contradiction uses beta minus the paired
   negative minimum, not the full beta. A good pair of two degree-five
   vertices may meet a budget nine and is not ruled out this way.
6. At m=8 a medium has no unsaturated low neighbor. In the surviving
   all-low case the high-high edge costs two degree units, not one.
7. At m=7 three highs can be allowed by the degree-unit bound; their
   (6,5,5) degrees are explicitly excluded by the internal incidence count.
8. The m=6 shape (5,5,4,4,4,2) is a valid simple twelve-edge support
   shape before the integer-lift filter. Its medium triangle is necessary,
   and all three of its edges are retained in the count.
9. The final six-vertex four-regular support is precisely a complement
   perfect matching. No connectivity or symmetry of the actual A is used.
10. The remaining K2,6 is not rejected by the paired BAD-entry argument:
    its highs are a GOOD M pair. Its separate integer lift proof needs
    a stronger saturation and spectral argument.
11. That separate ROOT candidate is
    `docs/CANDIDATE_20261003_TERNARY_K2_6_INTEGER_LIFT_V1.md`, SHA256
    `4efb2e1ffbcf4bf8c310c3521b175e570b93e1ed7ef18d20cbecaf05dea55260`.
    My independent written review is
    `acceleration/audit_20261003_ternary_k2_6_integer_lift_v1.md`, SHA256
    `2b8dad64a3d15443ddca45ddd4946ccc5aa215a7739a9d9f234b4c7f4873bd7d`,
    with report
    `acceleration/results/20261003_independent_review/ternary_k2_6_integer_lift01/summary.json`,
    SHA256 `0301d9591b261b3cf1b29f1f51bd52b0233126ea2bf01dfa2e0721e2e9cd8832`.
    These references disclose separate work; that verdict is not imported
    into this classification's statement or material dependencies.
12. The classification uses the WHOLE support. Removing a component
    would invalidate the outside-zero commutation and small-order bounds.
13. No nonzero residual is forced. A target graph with M=0 stays allowed;
    no general nonexistence, sharpness or twelve-defect realization follows.
14. All cases above are written exact degree, binary-word and row-budget
    arguments. There are zero executed support enumerations, executable
    fixtures, formal-prover checks, numerical spectra or external reviews.

This new discovery stays outside the frozen 371-claim publication and
changes no engine, objective, verification gate, ledger, index or current
notice. A separate author must verify the entire classification before
any mathematical promotion, and any later combination with an integer
lift obstruction must state those additional dependencies explicitly.
