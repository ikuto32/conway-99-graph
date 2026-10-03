# Candidate: equal outside neighborhoods and nine residual defects

Discovery author: `/root/structural`. Actual written UTC time:
`2026-10-03T08:42:14+00:00`. Source context:
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`; this new working file is not
asserted to occur in that commit. Status **CANDIDATE**, awaiting another
author's complete written derivation and falsification review. Mathematical
programs, finite enumerations, executable fixtures, ledger changes and index
changes: zero. No target resolution, novelty, optimality or realization claim.

Research context is the earlier residual-lift candidate `6189d5c4...` and
proper-support-nullity candidate `d4f08c8c...`, namely
`docs/CANDIDATE_20261003_TERNARY_RESIDUE_LIFT_PARITY_GLOBAL_SUBCUBIC24_V1.md`
and `docs/CANDIDATE_20261003_TERNARY_PROPER_SUPPORT_NULLITY3_V1.md`.
Neither result is imported. In particular the argument below does not use
eigenvalue-1 parity, global subcubic24, connected-spanning99, a prior defect
classification, an isomorphism catalogue or an incidence-rank premise.

## Exact candidate statements

Let A be any symmetric binary 99-by-99 integer matrix with zero diagonal
and exactly 14 ones in every integer row. Set

  R=A^2+A-12I-2J over the integers; M=R mod 3=A^2+A+J over GF(3).

Let H be the whole nonzero unordered off-diagonal support of M, let S be
its whole nonisolated vertex set, let m=|S|, let T be its complement and
let e=|E(H)|=F3. Support degrees refer to H, not the degree-14 graph A.

1. If m<=11 and two distinct vertices u,v in S have identical A-neighborhoods
   outside S, neither can have support degree at most 4. More generally the
   explicit pair-versus-row inequalities below hold for every m and support
   degree, including higher support degrees.
2. F3 cannot equal 9 in this complete adjacency domain.

These are necessary restrictions on actual polynomial residuals. They do
not assert the existence of a graph at any allowed value. M=0 is permitted;
there is no target nonexistence claim or conclusion about triangle incidence.
The second statement does not by itself exclude F3=8 or establish F3>=10.

## Exact identities and a row's negative budget

The integer diagonal of R is zero and its row sums are
14^2+14-12-2*99=0. Every off-diagonal entry is CN(u,v)+A_uv-2, at least -2.
A good entry M_uv=0 is a multiple of 3 and therefore nonnegative.
A support entry of residue 1 has integer lower bound -2, and one of residue
2 has lower bound -1. Symmetry and regularity give AJ=JA, hence AM=MA.
All outside-S M rows are zero. On the (T,S) block, commutation consequently
gives A[T,S]M[S,S]=0.

For u in S, let c1(u),c2(u) count its support entries of residues 1 and 2.
Its support degree d_u=c1+c2. Define its negative budget

  beta_u=2c1(u)+c2(u).

M1=0 gives c1+2c2=0 modulo 3, and therefore beta_u is a multiple of 3.
Since beta_u<=2d_u, it follows that

  beta_u<=3 floor(2d_u/3).

In particular beta_u<=6 whenever d_u<=4. This bound does not assume every
bad residual achieves its minimum; allowing the full negative budget is
only a necessary relaxation.

For a distinct pair u,v, the zero integer row sum implies these upper bounds:

  if M_uv=0, R_uv<=beta_u;
  if M_uv=1, R_uv<=beta_u-2;
  if M_uv=2, R_uv<=beta_u-1.

The same inequalities hold with u and v swapped. They follow by giving
every other bad entry its lower bound and every other good entry zero.
The paired positive residual is not also counted as an available negative
entry. These are general signed row-budget constraints, not numerical fits.

## Common-neighbor lower bound from identical outside neighborhoods

Suppose u,v have an identical outside-S neighborhood of size t. Both have
exactly d=14-t neighbors within S. Their two internal neighborhoods are
subsets of S of size d; their intersection has size at least max(0,2d-m).
Thus their complete integer common-neighbor count satisfies

  CN(u,v)>=t+max(0,2d-m)
          =14-d+max(0,2d-m)
          >=14-floor(m/2).

This is an integer minimum over d; excluding the endpoints themselves
could strengthen it but is not needed. All outside witnesses are included.
Consequently

  R_uv>=14-floor(m/2)+A_uv-2.

For any known residue s=M_uv, the lower bound must also be rounded upward
to the least integer congruent to s modulo 3. Combining this with the two
row budgets above is a necessary filter for identical-neighborhood classes
at any support degree. A support edge is not assumed to be an A edge.

If m<=11, CN(u,v)>=9 and R_uv>=7. A good paired entry is then at least 9,
whereas beta_u<=6 when d_u<=4. A bad paired entry is at least 7, whereas its
remaining negative budget is at most 5. Either case contradicts the zero
integer row sum. This proves candidate statement 1.

## Binary constraints forced by a low support degree

For any z in T its binary neighborhood word x=A[z,S] satisfies xM_S=0.
At a support vertex w of degree 2, its two nonzero labels must be opposites,
say s and -s. The corresponding equation is s*x_u-s*x_v=0, so x_u=x_v.
Thus those two support neighbors have identical outside-S neighborhoods
in the actual graph A.

At a support vertex w of degree 3, the three nonzero labels must all equal
one nonzero s. Its equation is x_u+x_v+x_h=0 over GF(3). Since each coordinate
is binary, their ordinary integer sum is 0 or 3; all three are equal.
These three support neighbors therefore have identical outside neighborhoods.
This conclusion concerns binary adjacency coordinates; arbitrary ternary
coordinates summing to zero need not be equal.

For m<=11, statement 1 implies that every degree-2 support vertex has two
neighbors of support degree at least 5, and every degree-3 support vertex
has three such neighbors. This is a general sparse-support mechanism, not
an isomorphism classification. In particular a degree-2 vertex requires
2e>=2m+6, and a degree-3 vertex requires 2e>=2m+10: compare each distinguished
vertex and its distinct neighbors with the minimum support degree 2.

## Nine-edge contradiction without finite enumeration

Assume e=9. A support vertex cannot have degree 1 because its M row sum
is zero and its sole support entry would be nonzero. Every support vertex
has degree at least 2, so m<=e=9. Simplicity and e=9 require m>=5, because
four vertices have at most six unordered pairs.

If some support vertex has degree 3, its three neighbors all have degree
at least 5 by the preceding mechanism. The total support degree is at least
3+3*5+2(m-4)=2m+10>=20, exceeding the exact total 2e=18. Hence no support
vertex has degree 3.

If some support vertex has degree 2, both its neighbors have degree at
least 5. Total degree is at least 2*5+2(m-2)=2m+6, so m<=6. The case m=5
is impossible because every support degree is at most m-1=4. Thus m=6,
and the degree total forces exactly two vertices of degree 5 and four of
degree 2. The two degree-5 vertices a,b are adjacent to each other and all
four remaining vertices. Each remaining vertex has exactly these two
neighbors. The support is therefore K2,4 plus the a-b edge. This conclusion
comes from literal degree constraints, not assumed isomorphism completeness.

For each low vertex w, its zero signed row gives M_wa+M_wb=0. Sum the rows
of a and b. Their four low-vertex incidences cancel in pairs by symmetry,
leaving 2M_ab. Both high rows sum to zero, so 2M_ab=0 over GF(3), impossible
for their nonzero support edge. This excludes the sole degree-2 possibility.

With no degree 2 or 3, every support vertex has degree at least 4. Then
2e>=4m>=20, again contradicting 18. All possibilities are excluded, proving
candidate statement 2. Connectivity and support maximum degree were never
assumed. No support graph was constructed or enumerated by a worker.

## Written boundary and counterattack checks

1. Empty support M=0 is permitted. This argument cannot force a defect or
   exclude a target solution.
2. At m=11 the lower CN is 9, a good residual is at least 9 and every
   degree-at-most-4 negative budget is at most 6. Both endpoint inequalities
   retain a strict gap. The support-degree and graph-degree symbols differ.
3. At m=12 the coarse CN bound is 8, and a good paired residual of 6 could
   meet the degree-4 budget 6. The strict general equal-pair filter is not
   extended there; this arithmetic boundary is not a graph realization.
4. Support degree 5 permits budget 9. Some hypothetical good-pair lower
   bounds can meet it. No blanket degree-5 veto or rank obstruction is
   claimed. The nine-edge exception is rejected separately by signed rows.
5. The support edge a-b in that exception is an M edge, with A_ab possibly
   either 0 or 1. Its cancellation contradiction does not assume adjacency
   in A or any particular nonzero residue label.
6. K2,4 without the high-high edge has eight edges and can have zero signed
   rows: assign the four edges from one high vertex labels (1,1,2,2) and
   assign their opposites from the other. Adding a single high-high edge
   destroys the two high signed rows. Signed row feasibility alone is not
   graph-lift feasibility; this example asserts neither an eight-defect
   realization nor any new eight-defect theorem.
7. A degree-3 row cannot use a mixed triple of nonzero GF(3) labels and
   still have zero sum. With three equal labels, binary (0,0,0) and (1,1,1)
   satisfy the equation. Ternary (0,1,2) also sums to zero but is not an
   adjacency word; allowing it would invalidate the equality propagation.
8. beta includes the two different integer minima -2 and -1. Treating
   every field label as the same ordinary integer, or counting the paired
   positive entry as a negative budget, would be an incorrect relaxation.
9. The complete set S is essential. Vertices of another residual component
   cannot be treated as zero outside rows. No small-component exclusion is
   inferred in a support with additional defects elsewhere.
10. The adjacency neighborhood equality must be proved from commutation
    and a binary outside word. Equal support degrees, commutation alone
    without the polynomial residual identity, or equal approximate CN
    values do not supply it.
11. The pair bound uses exact regular degree 14 and the integer residual
    row identities at order 99. Different degrees/orders, nonsymmetric
    matrices or another field require a changed proof. There are no
    executed fixtures, measured counts, formal-prover checks, sufficiency
    assertions or target constructions in this note.

## Next research use

The general filter compares whole-support size, identical outside binary
neighborhood classes and exact negative budgets. It can constrain support
vertices of higher degree through the displayed beta inequalities, rather
than merely adding another small support to a numerical acceptance rule.
It does not change a frozen heuristic objective, engine, validator or gate.
Any computational classification or use by a new engine would need its own
source, declared scope and independent controls. The candidate remains
outside the frozen 371-claim publication until separate verification and
registration. No live worker status is inferred from historical receipts.
