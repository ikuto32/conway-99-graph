# Candidate: a nonzero ternary residual needs at least twelve defects

Discovery author: `/root/structural`. Actual writing clock:
`2026-10-03T09:17:49+00:00`. Source context:
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`; this new working file is not
asserted to occur in that commit. Status **CANDIDATE**, pending a different
author's complete exact derivation and falsification review. Executed
mathematical commands, enumerations, fixtures, ledger changes and index
changes: zero. Target resolution: NONE; novelty and sharpness: UNKNOWN.

This discovery is separate from the completed independent review of ROOT's
ten-defect candidate. That review is
`acceleration/audit_20261003_ternary_ten_defect_nonrealizability_v1.md`, SHA256
`e855d26e93ca9a33c632fad90e9f8528b719e33ea196fb807a983c20fe9bb73e`, with
revision-1 report
`acceleration/results/20261003_independent_review/ternary_ten_defect_nonrealizability01/summary.json`,
SHA256 `6b07be2b80c431c1c3faf51e251f05851b3ae4950874866e4512ed5ea9251f81`.
The new statement below is not an amendment or self-approval of that verdict.

## Exact proposed statement

For every symmetric binary integer 99-by-99 matrix A with zero diagonal
and exactly 14 ones per integer row, put

  R=A^2+A-12I-2J; M=R modulo 3=A^2+A+J over GF(3).

Let F3 be the number of unordered off-diagonal pairs with M_uv nonzero.
The proposed necessary bound is

  F3=0 or F3>=12.

No support connectivity, maximum support degree, automorphism, incidence
decomposition, catalogue or spectral-parity assumption is made. M=0 remains
allowed. This is not a target nonexistence theorem, an optimum, a sufficient
characterization or a twelve-defect realization. The proof addresses the
whole residual support, not an arbitrary small component of a larger support.

## Material filter and independently verified provenance

The material filter is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`.
ROOT's separate written audit is
`acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`, SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`;
its exact filter report is
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The discovery source was
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`, SHA256
`a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
The elementary filter is repeated below for a self-contained review.
No separate eight-, nine- or ten-defect exclusion, global subcubic bound,
connected-spanning statement or eigenvalue parity result is used as a premise.

Write H for the whole nonzero off-diagonal support of M, S for its whole
nonisolated vertex set, m=|S| and e=|E(H)|. Integer R has zero diagonal and
row sums. A good paired residual is a nonnegative multiple of three;
residues 1 and 2 have lower bounds -2 and -1. At a support vertex of degree
d with c1,c2 such residues, beta=2c1+c2 is a multiple of three and at most
3 floor(2d/3). A paired good term is at most beta; a paired residue-1 or
residue-2 term is at most beta-2 or beta-1.

Identical outside-S adjacency neighborhoods of u,v give
CN(u,v)>=14-floor(m/2): if their shared outside size is t and their shared
internal degree is d_A=14-t, their internal intersection is at least
max(0,2d_A-m). When m<=11 this forces a good paired residual at least 9
or a bad paired residual at least 7, both impossible at a support endpoint
of degree at most 4, whose available budget is at most 6 or 5 respectively.

Commutation AM=MA gives A[outside S,S]M_S=0. A degree-2 support row has
opposite labels and forces its two neighbors' outside binary coordinates
equal. A degree-3 support row has three equal labels and forces all three
neighbors' binary coordinates equal. Hence, for m<=11, every degree-2
vertex has two support neighbors of degree at least 5, and every degree-3
vertex has three such neighbors. These are restrictions on signed support
and outside binary words, not assumptions about the adjacency graph's
degree or an isomorphism class.

## A uniform small-support density argument

Suppose 1<=e<=11. A support vertex cannot have degree 1 because its signed
row sum is zero. Thus its minimum degree is 2 and m<=e<=11. Any required
degree-at-least-5 vertex entails m>=6 by simplicity.

First, degree 3 is impossible. Such a vertex and its three distinct high
neighbors would give total degree at least

  3+3*5+2(m-4)=2m+10.

Because total degree is at most 22, m<=6. Simplicity makes m>=6, so m=6
and equality is forced: three high vertices of degree 5, the chosen
degree-3 vertex and two vertices of degree 2. But the three high vertices
are universal at order 6. Each of the degree-2 vertices would be adjacent
to all three, contradicting its degree. This excludes the entire degree-3
alternative for every e<=11 at once.

Now assume there is a degree-2 vertex. Its two high neighbors give total
degree at least 10+2(m-2)=2m+6, so 6<=m<=8. The following three literal
degree arguments exhaust that range; no support enumeration is performed.

* At m=8, equality with the upper total 22 forces two vertices of degree
  5 and six of degree 2. The low vertices must all join the two high
  vertices, giving each high vertex at least six neighbors, a contradiction.
* At m=7, start with two degrees at least 5 and five degrees at least 2,
  costing total 20. With at most two additional degree units and no degree
  3, there cannot be a third high vertex and there can be at most one
  remaining degree-4 vertex. If there were one, the other four low vertices
  would already use both edges on the two high vertices, so the degree-4
  vertex could have at most those two neighbors. Hence all five lows have
  degree 2 and join the two highs. The support is K2,5, possibly with the
  high-high edge; these have ten or eleven edges respectively.
* At m=6, the two high vertices have degree 5 and are universal. Three
  universal high vertices would force all remaining degrees at least 3,
  and, as degree 3 was excluded, at least 4; total would exceed 22. Thus
  there are only two high vertices. The remaining four have degree 2 or 4.
  Their base total with the highs is 18, leaving at most four units, so at
  most two can have degree 4. A degree-4 vertex can join the two highs and
  at most one other degree-4 vertex; degree-2 vertices are already saturated
  by the highs. It cannot attain degree 4. Thus all four lows have degree
  2, and the literal support is K2,4 plus the high-high edge, with nine edges.

If there is no degree 2 or 3, minimum degree is 4. The total at most 22
then forces m<=5, while a vertex of degree 4 requires m>=5. So m=5 and
every degree is 4: the literal support is K5, with ten edges. Supports
of order at most 4 were also covered: they cannot contain a high vertex
required by degrees 2/3 or attain minimum degree 4.

Therefore any nonempty actual support with e<=11 would have to be one of
the four literal shapes K2,4+high edge, K2,5, K2,5+high edge, or K5. This
is a consequence of degree totals, not a claim based on an unverified
isomorphism list.

## Eliminating all four remaining shapes

For either K2,r plus a high-high edge, each low row says its two incident
labels are opposite. Sum the two high signed rows: their incidences to
the low vertices cancel, leaving twice the nonzero high-high label. It
cannot be zero in GF(3). Thus both the nine- and eleven-edge high-edge
shapes fail the signed row equations.

For K2,5 without that edge, let c count residue-1 labels from one high
vertex. Its signed row gives 10-c=0 modulo three, so c=1 or 4. The high
negative budgets are 6 and 9 in some order. A low degree-2 row forces the
highs' outside neighborhoods equal. At m=7 their CN is at least 11 and
their good paired residual at least 9, contradicting the smaller budget 6.
The field rows themselves can be valid; the contradiction needs the
integer adjacency lift, with no assumed value for the high-high A entry.

For K5, every row has two residues of each kind. Its positive edges form
a simple C5 and its negative edges the complementary C5. With cyclic
indices 0,...,4 the signed matrix B squares to 5I-J over the integers:
the diagonal is 4; at pair (0,1) the intermediate products are -1,+1,-1;
at pair (0,2) they are +1,-1,-1. Thus B^2=2I-J over GF(3), and Bx=0
forces 2x=Jx, so x is constant. Conversely B1=0. Every outside binary
word is therefore all zero or all one, making all five outside
neighborhoods identical. Support degree 4 and m=5 violate the filter.

All possible nonempty supports with at most eleven edges are excluded.
This proves the proposed F3=0 or F3>=12 bound, pending separate verification.

## Written falsification and boundary checks

1. An empty support is allowed. The proof never forces a defect or a
   nonzero triangle-incidence kernel, and does not resolve Conway-99.
2. The degree-3 total at m=6 is exactly 22; all listed degrees are forced,
   and the two degree-2 vertices really cannot avoid three universal highs.
3. At m=8, degree-2 propagation gives six low vertices but only two high
   vertices of degree exactly 5. An omitted high-high edge cannot repair
   their already excessive low-neighbor count.
4. At m=7, a third high costs at least three additional units. A medium
   degree-4 vertex costs two but has no available low neighbor. The
   remaining K2,5 possibilities include both high-high edge choices.
5. At m=6, a degree-4 vertex can gain at most one medium neighbor in
   addition to the two highs, not the two it would require. A third
   universal high is separately impossible with no degree 3.
6. The signed cancellation for the high-edge shapes uses M edges, not
   A edges, and uses no choice of the nonzero high-high label.
7. K2,5 has a field-valid labeling, but one budget is 6. It is not wrongly
   declared field-infeasible or rejected by a false all-word weight bound.
8. Both signed K5 product types are checked, and negating every label
   leaves its square and kernel unchanged. No automorphism of A is assumed.
9. The edge threshold 12 is not asserted sharp. A field-level signed
   K2,6 has twelve edges: give one high vertex three labels +1 and three
   -1, and the other the opposites. Every signed row is zero; both high
   budgets are 9, so the coarse equal-pair lower budget 9 need not conflict.
   In block form C=u s^T with u=(1,-1), s having three of each sign,
   the matrix [[0,C],[C^T,0]] has cube zero because s^T s=6=0 in GF(3).
   Its eigenvalue-1 primary space is empty and therefore passes that
   separate parity restriction. None of this supplies a binary14-regular
   polynomial lift, a twelve-defect graph, or sufficiency of these filters.
10. The whole support is essential. Additional residual components
    invalidate the small m and outside-zero arguments if silently dropped.
11. These are exact written calculations with zero executable fixtures,
    measured counts, formal-prover checks or external review. No heuristic
    acceptance rule, frozen engine, ledger or publication notice is changed.

The reusable ingredient is the combined binary-neighborhood and signed
negative-budget restriction. It gives a density obstruction for an entire
small-support range and leaves an explicit field-level boundary requiring
stronger lift information. This new discovery remains CANDIDATE and outside
the frozen 371-claim cutoff until a separate exact verification and any later
registration/publication. No live worker state is inferred here.
