# Candidate: disjoint two-d3 roots at R226 cannot have four through six d2 roots

Root and Structural independently found the actual-label restriction on
the bad-pair graph. Structural challenged every degree, component and
outside-support step below. This new written CANDIDATE uses only the
literal hypotheses, and no pending population gate. No mathematical
program, enumeration, import, solver or worker ran. All earlier proof
and publication bytes remain unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T. Suppose R=226, every d_T
belongs to {0,1,2,3}, and exactly two actual deficiency-three triangles
occur and are disjoint. Then the number b of actual deficiency-two
triangles does not belong to {4,5,6}.

Disjointness and maxd3 are explicit assumptions. No preceding R226 theorem
is promoted into them. The argument derives its own fan/parity/weighted
Gram identities and has no inherited logical claim dependency. It does
not exclude all two-d3 populations, R226 or the target.

Name the d3 roots A,B. For b4..6, a=24-2b, P=26-b<=22. At each actual
point, the local defect degrees are the root deficiencies, r1+r3 is even,
and the actual positive fan satisfies 3r1+5r2+7r3<=P. The injection proving
this fan bound counts each external positive triangle at at most one fan
outer point, by linearity and the lambda1 prohibition on an actual loose
triple. No automorphism, uniform profile or selected inducedness is assumed.

## The bad-pair graph is a union of singleton, edge and two-edge paths

A point on A or B is bad if r1=1. Its degree-three node needs at least
two d2 nodes, and r2>=3 would need fan25>P. Thus exactly two d2 roots
occur there, with valid local degree sequence(3,2,2,1). Every other A/B
point has r1>=3.

Let J have the b actual d2 roots as vertices, and one edge for each bad
point joining its two roots. Color it A or B according to that point's
d3 root. J is simple: two actual triangles meet at most once. Each color
class is a matching: one actual d2 root cannot meet A or B twice, and a
bad point cannot have a third d2 root. Hence degree(J)<=2, with proper
alternating two-color components.

There is no three-edge path X1-X2-X3-X4 with colors A-B-A. Its labels
p,q,r lie on A,B,A respectively. The points p,r are distinct: coincidence
would give X2,X3 common vertices both there and at q. Also q is distinct
from p,r by A/B disjointness. Thus A,X2,X3 meet pairwise at the three
different actual points p,r,q. Their intersection edge has a second
triangle partner, violating lambda1. The B-A-B case is identical.

Every longer path or alternating cycle contains such a three-edge path.
An odd cycle is already impossible in a proper two-edge-color graph.
Consequently the complete components of J are only singletons, K2 or P3.
In particular, with h=|E(J)| the bad-point count,

    h<=floor(2b/3).                            (1)

The bound is purely combinatorial, not a realizability assertion.
For b4/5/6 it gives h<=2/3/4 respectively.

## Two components leave no outside selected-support point

Choose O=D1 union D3 and let S be its actual point support. All bad-point
labels lie in S. Two d2 roots in one K2 component already meet at their
bad point and cannot meet again outside S. In a P3 component X-Y-Z,
the two bad labels are distinct, one on A and one on B. Its endpoints
X,Z cannot intersect anywhere: an additional distinct point gives the
forbidden actual loose triple X,Y,Z; coincidence with either existing
label violates triangle linearity. Thus an outside point can contain at
most one d2 root from each J component.

At a point outside S, no d1/d3 root occurs. A positive root there is d2,
and the simple local degree-two graph needs at least three positive roots.
Therefore, if J has at most two components, no d2 root has an outside
point, and all b d2 triangles are wholly in S. Their actual triangle
edges are distinct from O and each other. With positive integer weights
on S, their total weighted internal contribution is at least3b. Extra
actual edges only increase it.

J is a forest with b-h components. Its maximal-h configurations here
have exactly two: at b4/h2 they are either two K2 or P3 plus singleton;
at b5/h3 they are P3 plus K2; at b6/h4 they are two P3. This is finite
component counting, not an enumeration of graph completions.

## Exact weighted identity and all scalar cases

The O incidence is even at every actual point by the local degree sum.
Let w be half that incidence on S, zero elsewhere. Put s=|O|=26-2b,
K=sum w(w-1), ell=sum_(selected O edges)(w_u-1)(w_v-1), and H equal to
the weighted sum of all internal S edges not in O. All are nonnegative
integers. Unique actual selected triangle edges give

    E_selected=3s+4K+ell,
    0<=q=w^T(3I-A+J99/9)w=s(s-6)/4-5K-2ell-2H. (2)

Here J99 is the all-ones matrix, distinct from the bad-pair graph J.
The exact identity follows by expanding w=1+(w-1) on each selected
triangle; the linear terms sum to4K, and ||w||^2=3s/2+K. It permits
selected incidence six or larger and retains all extra actual edges.

There are six A/B points. A nonbad one has incidence at least four and
contributes at least two to K, so K>=2(6-h). If h_A,h_B count the bad
points on A,B, the selected d3 edges alone give

    ell>=binom(3-h_A,2)+binom(3-h_B,2).        (3)

For h<=2 this is at least two; for h3 it is at least one. Bounds (1)-(3)
give the complete hand table:

| b | h branch | s(s-6)/4 | K minimum | ell minimum | H minimum used | q upper bound |
|---:|---|---:|---:|---:|---:|---:|
|4|0|54|12|6|0|-18|
|4|1|54|10|4|0|-4|
|4|2|54|8|2|12|-14|
|5|0..2|40|8|2|0|-4|
|5|3|40|6|1|15|-22|
|6|0..3|28|6|0|0|-2|
|6|4|28|4|0|18|-28|

The H bounds in maximal-h rows are supplied by the exact two-component
outside-point argument. Every row is strictly negative, contradicting
the target upper Gram. This proves the stated exclusion of b4,b5,b6.

## Actual-label counter-controls and scope boundary

An abstract properly colored P4 or C4 is a valid graph, but cannot carry
these actual target triangle labels. For the C4, its four alternating bad
points also give an actual four-cycle whose diagonal is the edge of A,
with two common neighbors, directly violating lambda1. The proof uses
this actual point obstruction, not a general assertion that selected-even
dual graphs are triangle-free or have no cycles.

The two-edge P3 component is deliberately retained. Its endpoints are
disjoint as actual triangles, and its middle root meets A/B at distinct
points. This matches the valid two-fan configuration used elsewhere; no
false P3 veto is introduced. Additional outside d2 points are excluded
only when their local degree needs three roots but at most two components
are available. In other branches none of that absence is assumed: H is
merely dropped from the safe upper bound.

The selected weighted identity and fan methods overlap prior work. The
new restriction is the actual-label bad-component bound and its complete
norm contradiction for b4..6 in the literal disjoint c2 lane. No full
archive absence, novelty, survivor construction, two-d3/R226 exclusion
or target resolution is claimed. A different author must challenge this
exact full proof before any VERIFIED/ledger use; the publication cutoff
is unchanged.
