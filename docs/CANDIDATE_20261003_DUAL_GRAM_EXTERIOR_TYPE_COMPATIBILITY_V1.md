# Candidate: exact upper and lower Gram constraints on exterior types

Claim `C-TARGET-DUAL-GRAM-EXTERIOR-TYPE-COMPATIBILITY`, revision 1.
Basis DERIVED, status CANDIDATE, review NEEDS_RECHECK. Root proposed testing
the corrected upper and lower principal Grams against the fixed 17-point
exterior types. Structural independently derives the general conditional
formulas here. No actual 472-type, pair-population or matrix computation was
executed. This is not approval of the author's discovery.

## Complete assumptions and statement

Let A be the adjacency matrix of an exact simple (99,14,1,2) graph, so
A^2=12I-A+2J and A1=14*1. Let S be any vertex subset of size m, let H=A[S,S],
and assume its upper principal matrix U=3I_m-H+J_m/9 is positive definite.
For an exterior vertex with its literal adjacency type t in {0,1}^m, put
b_t=(1/9)1-t, q_t=b_t^T U^-1 b_t, and c_tu=b_t^T U^-1 b_u. Then

    q_t <= 28/9,
    (1/9-a-c_tu)^2 <= (28/9-q_t)(28/9-q_u),

where a is the actual adjacency, zero or one, of two distinct exterior
vertices of types t and u. The Schur complement on all 99-m exterior vertices
is PSD and has rank 44-m. These are necessary conditions only.

Separately assume K=H+4I_m is positive definite. Define l_t=t^T K^-1 t
and d_tu=t^T K^-1 u. Then

    l_t <= 4,
    (a-d_tu)^2 <= (4-l_t)(4-l_u),

and the full lower Schur complement is PSD of rank 55-m. The two hypotheses
on principal matrices are separate. For a fixed exact 17-point base satisfying
both, the exterior ranks are respectively 27 and 38.

All inverses and inequalities are exact rational identities when H,t,u are
integral and the hypotheses hold. Neither numerical near-equality nor an
unverified positive-definiteness assertion substitutes for those hypotheses.
There is no target existence/nonexistence, type pruning or whole-family
exclusion conclusion in this paper.

## Historical PSD and rank identities reconstructed

Set G=27I-9A+J. Expanding with the stated target identity, AJ=JA=14J and
J^2=99J gives G^2=63G. Thus x^T G x=||Gx||^2/63>=0. Its trace is
27*99+99=2772, so its rank is 2772/63=44. Consequently G/9 is the upper
matrix 3I-A+J/9, with diagonal 28/9 and off-diagonal 1/9-A_uv.
This is the historical target upper Gram, not a new rank obstruction.

For the lower matrix L=A+4I, direct expansion gives L^2=7L+2J and L1=18*1.
Set T=L-(2/11)J. Then T1=0 and T^2=7T, so T is PSD. Its trace is
396-18=378 and its rank is 54. The all-one line is orthogonal to its image;
adding (2/11)J proves L is PSD of rank 55. In particular A+3I is not used:
its target -4 eigenspace would have a negative eigenvalue.

These calculations explicitly preserve the correction to Root's earlier
A+3I proposal. They do not create a new rank bound for target incidence or
an unbalanced incidence-kernel circuit.

## Schur derivation, including the actual adjacency bit

Partition the upper target matrix by S and its exterior. Its S block is U;
a type-t exterior column restricted to S is exactly b_t. Congruence by the
block elimination matrix leaves U and the exterior Schur matrix D-B^T U^-1 B.
PSD of the whole matrix implies PSD of this Schur matrix. Because U is PD
with rank m, the rank-additivity of this same invertible congruence gives
rank(D-B^T U^-1 B)=44-m.

An exterior diagonal entry is 28/9-q_t. A two-vertex off-diagonal entry is
1/9-a-c_tu. Its 2-by-2 principal matrix is PSD only if both diagonals are
nonnegative and its determinant is nonnegative. This is exactly the upper
singleton and pair test above. The lower derivation is identical, with
restricted columns t, diagonal 4 and exterior off-diagonal a.

The bit a is actual graph adjacency. It is not an incidence-support label,
an assumed bipartite relation, or determined by the type intersection alone.
For a planned necessary compatibility test, try both literal bits independently
and intersect the allowed bits from upper and lower Grams. The existing target
common-neighbor constraints also require |t intersect u|<=1 for a=1 and
|t intersect u|<=2 for a=0, since these internal common neighbors cannot be
removed by exterior completion. Empty intersection forbids coexistence of
those two types; a singleton intersection forces their adjacency bit.

This does not claim a polynomial-time or linear-programming encoding of all
such coexistence restrictions. It merely supplies exact necessary predicates
for a future independently checked artifact.

## Equal-type multiplicities and exact thresholds

Two distinct vertices may have equal type. One must not omit t=u from the
pair test or confuse it with a diagonal entry belonging to the same vertex.
For equal upper types, c_tt=q_t. The nonadjacent determinant condition is

    (1/9-q_t)^2 <= (28/9-q_t)^2,

equivalent, after subtracting squares, to q_t<=29/18. The adjacent condition
(8/9+q_t)^2 <= (28/9-q_t)^2 is equivalent to q_t<=10/9.
These equivalences assume the separately required nonnegative singleton
diagonal. Thus q_t>29/18 prohibits two distinct vertices of that type;
10/9<q_t<=29/18 forces any equal-type pair to be nonadjacent. A singleton
may still pass with q_t above both pair thresholds. No multiplicity or
adjacency is inferred for the actual 472 types without exact evaluation.

For equal lower types, the nonadjacent condition l_t^2<=(4-l_t)^2 is
equivalent to l_t<=2. The adjacent condition (1-l_t)^2<=(4-l_t)^2 is
equivalent to l_t<=5/2. Hence l_t>5/2 prohibits multiplicity at least two;
2<l_t<=5/2 forces equal-type pairs adjacent. These lower and upper conclusions
must be combined with each other and the common-neighbor intersection cap;
none is a stand-alone sufficient condition.

Equality at any threshold is included as written. A zero residual singleton
diagonal requires every corresponding Schur off-diagonal to be zero, as also
follows from the pair determinant. Boolean zero/one aliases in a future raw
artifact are not literal adjacency bits or exact rational coordinates.

## Fixed-base applicability and explicit limits

The intended application is the precisely authenticated induced case51
17-point base of the existing 472-type relaxation. The fourth-class positive
upper Gram in the separate written four-class theorem is relevant only after
the exact raw base-to-class identification is authenticated. The class-I
two-extra-edge repair is a different graph and cannot be substituted for
this fixed class-IV model. This paper makes no actual base identification or
472-value computation.

For an exact selected twelve-triangle edge union with point incidence degrees
d_v in {2,3}, the lower hypothesis can independently be seen from its binary
selected incidence C: H+4I=C C^T+diag(4-d_v), with the latter diagonal at least
one. This proves PD for that exact edge union. Extra edges require their own
matrix check; selected incidence alone no longer equals full adjacency there.

Pair tests are not full PSD tests. For example the rational symmetric
3-by-3 matrix with diagonal 1 and all off-diagonals -3/4 has positive
2-by-2 determinants 7/16, but its all-one quadratic is 3-9/2=-3/2.
This is a written generic counterexample to pairwise sufficiency, not an
adjacency or target countermodel. The full exterior Schur PSD and rank
conditions remain stronger requirements.

The lower singleton constraints might be redundant on the existing filtered
type universe. Upper singleton/pair tests might also all pass. No retained
type, pair count, rational witness, numerical spectrum, pruning rate or cost
estimate is invented. Those are questions for a new source-bound calculation
with finite positive/corrupt controls and a separate verifier, before a ONE
authorization. Existing finite gates do not approve that new calculation.

## Provenance, overlap and falsification boundaries

Root proposed the corrected upper/lower test; Structural reconstructed the
target polynomial identities, Schur signs, rank-additivity and equal-type
thresholds. The historical dependency is
`C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS`, revision 1. The conditional theorem
does not depend on a newly computed case51 inverse or the old nonzero-defect
chain. Any later fixed-base calculation must bind its own accepted raw graph,
ordered types and source version.

Written boundaries include upper diagonal28/9 rather than3, upper restricted
column1/9-t rather than t, actual a in both formulas, lower shift4 rather than
the refuted3, the four equal-type equality thresholds, zero-diagonal forcing,
separate PD hypotheses, ranks27/38 only for m17, type intersections as lower
CN bounds, and the pairwise-PSD counterexample. All claims are conditional on
the complete target identity and exact induced base. Zero mathematical
commands, numerical or symbolic matrix programs, formal-proof executions or
external controls were executed. No ledger/index/Git or target status changes.
