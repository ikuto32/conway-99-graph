# Independent exact review: equal outside words and nine defects

Discovery: `/root/structural`; verifier: `/root`. Source-context commit
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. Reviewed artifact:
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
The written verification timestamp is in the separately saved records.
This is an independent derivation from graph axioms, not a second execution
of producer code. Executed fixtures, finite enumerations and formal checks:
zero. No external review or target resolution follows.

Two precise claims are accepted: the recorded general row-budget/equal-word
necessary filter, including the m<=11 degree-at-most-four veto; and F3!=9
for every simple integer degree-14 graph on 99 vertices. The latter uses
the former. Neither imports the prior parity, subcubic, incidence-rank or
proper-support-nullity results.

## Independent derivation of the filter

For symmetric binary zero-diagonal A with A1=14*1, define the integer
R=A^2+A-12I-2J. Direct multiplication gives R1=(196+14-12-198)*1=0
and diagonal R=14-12-2=0. For u!=v, R_uv=CN(u,v)+A_uv-2>=-2.
Thus residue-zero entries are nonnegative multiples of three, whereas
residues 1 and 2 have minima -2 and -1 respectively.

If c1,c2 count the two nonzero residues in row u, the field row sum is
c1+2c2=0 mod3. Its total negative allowance beta=2c1+c2 is divisible
by three, at most 2(c1+c2), hence at most 3 floor(2deg_H(u)/3).
Giving every other bad entry its minimum and all other good entries zero
in R1=0 yields, for the singled-out pair uv, upper bounds beta,
beta-2 and beta-1 for its residues 0,1,2. The upper bound applies from
both endpoints. It does not assume minima are attained.

Let S be the entire nonisolated residual support, m=|S|. Equal outside-S
neighborhoods of two support vertices have size t and each internal
neighborhood has size d=14-t. Their internal intersection is at least
max(0,2d-m), so CN>=14-d+max(0,2d-m). For d<=floor(m/2), this is at
least 14-floor(m/2). For d>floor(m/2), it is at least
14+ceil(m/2)-m=14-floor(m/2). This proves the asserted integer bound
without a parity or endpoint error. Including forbidden self-neighbors
in the ambient S only weakens this safe bound.

At m<=11, CN>=9 and R_uv>=7. If the pair is good, divisibility rounds
this up to nine; if bad, it remains at least seven. An endpoint of
support degree at most four has beta<=6, and after removing a bad paired
entry its budget is at most five. Both cases are impossible. The
displayed general rounded inequality is valid at every m; only the
strict degree-four corollary has the stated m<=11 range.

## Independent low-degree propagation

Since A is regular and symmetric, AJ=JA. The polynomial M=A^2+A+J
over GF(3) commutes with A. M has zero rows outside the entire S.
Its (outside,S) commutation block therefore gives X M_S=0 for binary
X=A[outside,S]. At a support vertex of degree two the two labels must
be opposite, forcing its two neighbors' outside binary coordinates
equal in every outside row. At degree three the labels must all be the
same; a sum of three binary coordinates is zero mod3 only when all
are zero or all are one. Thus all three outside neighborhoods agree.

At m<=11, the previous strict filter forces each of the two or three
neighbors in these cases to have support degree at least five. Every
nonisolated support vertex has degree at least two, because degree one
has a nonzero field row sum.

## Independent nine-edge exhaustion

If e=9, the degree sum is eighteen. Minimum degree two gives m<=9;
simplicity gives m>=5. A degree-three vertex and its three distinct
degree-at-least-five neighbors would contribute at least
3+15+2(m-4)=2m+10>=20. Hence degree three is impossible.

A degree-two vertex requires two distinct degree-at-least-five
neighbors, giving total at least 10+2(m-2)=2m+6. Thus m<=6. For m=5
degree five is impossible. For m=6 equality forces exactly two
degree-five vertices and four degree-two vertices. The high vertices
are universal and adjacent, and each low vertex meets precisely both
highs. This is the literal K2,4 plus the high-high edge.

Each low vertex has opposite labels to the two highs. Adding the two
high field row sums cancels all low incidences and leaves twice the
nonzero high-high label. Two is invertible in GF(3), giving a
contradiction. If there is no degree two or three, minimum degree four
would give total at least 4m>=20. This exhausts the possible degree
patterns, without assuming connectivity or any automorphism of A.

## Independent falsification boundaries

1. R=0 and M=0 are allowed; neither accepted statement can prove target
   nonexistence by requiring a residual defect.
2. m=11 retains a strict good-pair gap 9>6. At m=12 the coarse good
   bound can be six, so the degree-four corollary is not extended.
3. Degree five can have beta nine: a blanket degree-five veto would be
   invalid. The specific nine-edge high-high contradiction is a signed
   row argument.
4. Removing the high-high edge gives a signed-row-feasible K2,4 with
   labels (1,1,2,2) at one high and opposites at the other. Signed field
   row feasibility does not imply an actual graph-polynomial lift.
5. Degree-three propagation requires binary coordinates; the ternary
   word (0,1,2) defeats an unrestricted-field equality assertion.
6. A residual support edge and an A adjacency edge are different; the
   derivation never fixes A on the support edges.
7. The paired positive residual cannot also supply its own negative
   allowance. Removing its minimum gives the beta-2/beta-1 bounds.
8. Outside rows must be outside the whole support. The result does not
   exclude a nine-edge component within an arbitrary larger support.
9. Empty support, changed order/degree/field and nonsymmetric adjacency
   are not covered by an unjustified extension. The accepted scope is
   exactly simple symmetric integer degree fourteen at order 99.

No veto was found in these complete exact derivations. This written
verification approves only the two recorded statements and dependencies;
it is not a graph construction, a sufficient support characterization,
a performance result, a formal-prover certificate or external review.
