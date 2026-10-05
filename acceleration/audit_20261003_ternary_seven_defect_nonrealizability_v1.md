# Independent written audit: seven ternary defects

Verifier: /root/checkpoint_audit. Discovery producer: /root.
This is an exact written derivation, with no executed mathematical program,
support enumeration, adjacency fixture, solver or formal proof assistant.
The frozen discovery source is
`docs/CANDIDATE_20261003_TERNARY_SEVEN_DEFECT_NONREALIZABILITY_V1.md`,
SHA256 b292fa51bf1c4ec07c07633e768d525085523cefecd9cc1028a39aa459a8a827.
The published context is 63437c9b9fc2dd58b3bdfb51fc347b880b397503;
the separately pinned working documents are not claimed present in that commit.

## Exact statement and dependency

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly 14
ones in each integer row, put r_uv=(A^2)_uv+A_uv-2 for u<v and let F3
count all unordered residuals not divisible by 3. Then F3 is not 7.
This statement alone excludes no other residual count and makes no
existence, nonexistence or realization assertion about the target.

The only uses_result premise is
C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION r1,
whose exact conclusion forbids the *whole* nonempty connected residual
support from having both at most 12 vertices and maximum degree at most 3.
Binding 562676e3af281e33384265824f9e115dfce27cca498b94f3b46cd0100346edd3,
report e3b6ea1f00bea171554867b68667bdf6d25ed57a3c8c1438d8654cfed01aba15,
and proof 1233903ac6449e354f8aead02d222b9b2594b617f06dfa0ce8c07800611809ed
pin that precise prior result. The earlier proof has the same verifier;
that reuse is disclosed. Neither lower45 nor spanning99 is used here.

## Identities reproduced independently

Let D=A^2+A-12I-2J over the integers and M its entrywise reduction modulo 3.
Since A is binary and zero-diagonal, (A^2)_uu=14, hence D_uu=0.
The complete row sum is 196+14-12-198=0. Regular symmetry gives
AJ=JA=14J; expanding AD and DA shows equality over the integers, so
AM=MA over GF(3).

Let H have the nonzero unordered off-diagonal pairs of M as edges, with
isolates discarded. Each edge has one identical nonzero residue at its
two endpoints, represented by +1 or -1. Every complete support row sums
to 0 modulo 3. A nonisolated vertex cannot have degree 1. Degree 2 has
opposite labels, degree 3 has equal labels, and degree 4 has two labels
of each sign: the possible integer sums in those degrees establish these
rules without an assumption about adjacency in A.

For every off-diagonal pair r_uv>=-2. A good pair has residual divisible
by 3, so its integer residual is nonnegative. A row with exactly h bad
pairs has each bad residual >=-2; in particular any chosen good residual
in that row is <=2h. This uses the complete row, not a sampled subset.

## Complete support coverage for seven edges

Every nonempty simple component of H has minimum degree at least 2 and
at least three edges. A three-edge component is C3; the opposite signs
at its degree-2 vertices cannot be continued around its odd cycle.
Thus every allowable component has at least four edges. Seven edges
therefore force H connected. Its degree sum is 14, so its number m of
nonisolated vertices is at most 7.

The prior old12 result now applies to this whole connected H if it is
subcubic. Consequently H has a vertex of degree at least 4. Simplicity
requires m>=5. Degree at least 5 would require m>=6 and degree sum at
least 5+2(m-1)>=15, which is impossible. Thus the maximum degree is 4.

Subtracting degree 2 at every vertex leaves total excess 14-2m, with
each excess at most 2. For m=7 this is zero, so no degree-4 vertex exists.
For m=6 it is 2, requiring the sequence (4,2,2,2,2,2). For m=5 it is 4;
with an excess 2 present the only partitions are 2+2 or 2+1+1, giving
(4,4,2,2,2) or (4,3,3,2,2). This independently covers every simple graph
and every possible sign assignment; no graph topology has been selected
from a numerical enumeration.

### Two universal vertices on five support vertices

Let a,b have degree 4. Their edge has residue s nonzero. Each other
vertex is adjacent to both a,b and has no remaining neighbor in H.
Its two spokes have opposite labels. Sum the support row equations of
a and b: all spoke pairs cancel and the a-b edge contributes twice,
so 2s=0 modulo 3, impossible. This argument does not require the
individual degree-4 rows to have any particular arrangement of signs.

### One degree-4 vertex on six support vertices

Let a have degree 4 and z be its unique nonneighbor in H. Deleting a
leaves five vertices of degrees (2,1,1,1,1), with z of degree 2 and only
three edges. The two edges at z end at distinct degree-1 vertices; the
two remaining degree-1 vertices are joined by the last edge. Thus H
is a 4-cycle and a 3-cycle meeting only at a.

Write the residue on one triangle edge at a as t. The two degree-2
vertices of that triangle force its other edge at a to have the same
residue t. On the 4-cycle, its three degree-2 vertices force the two
edges at a to have opposite residues. The row of a therefore sums to
2t, a nonzero element of GF(3). Both choices of t fail. The shared
vertex cannot repair the odd-cycle contribution using this even cycle.

### The legitimate signed fan on five support vertices

Let a be the degree-4 vertex, b,c degree 3 and d,e degree 2. Deleting a
gives a simple graph on four vertices of degrees (2,2,1,1). Its edge
count is three; its two degree-1 ends must belong to a path containing
both degree-2 vertices. It is P4, say d-c-b-e. A cycle component would
use three degree-2 vertices or leave an isolate, which the sequence
does not permit.

The edge b-c forces the equal degree-3 labels at b and c to be the
same nonzero s. The spoke labels a-d and a-e are then -s, while a-b
and a-c are s. These seven labels actually satisfy every modular row.
This is a valid written modular support control, not an adjacency
realization. Rejecting it from zero-row signs alone would be incorrect.

Take any z outside the entire support and put x_u=A_zu for u in H.
Its M row is zero. The (z,u) commutator entries therefore give
x M[H,H]=0. The columns d and e give x_a=x_c and x_a=x_b, respectively.
The column b gives x_a+x_c+x_e=0. Because x_a=x_c is binary,
2x_a+x_e=0 forces x_e=x_a in both cases x_a=0 or 1. The column c gives
x_d=x_a the same way. Thus all five binary coordinates are equal for
each outside z. This independently derives outside twins without an
assumption that all modular-kernel vectors are constant over GF(3).

Every support vertex consequently has the same outside neighborhood.
There are at most four possible internal neighbors in A, so that common
outside neighborhood has at least 14-4=10 vertices. The support pair
d,e is good, regardless of whether A_de is 0 or 1. It has at least ten
common neighbors, so r_de>=8; divisibility by 3 gives r_de>=9.
Vertex d has exactly two bad pairs in the complete residual row. Its
other good entries are nonnegative, so the row is at least 9-2-2=5>0,
contrary to its integer zero sum. Equivalently r_de<=4, or <=3 after
divisibility, contradicts the lower bound 9. No internal value of A
or additional common neighbor can weaken this contradiction.

All seven-edge cases are excluded. Therefore F3!=7 in the stated domain.

## Twelve written falsification boundaries

1. Recover diagonal zero, complete row sum zero and the integer commutator
   before reducing modulo 3; degree 14 and order 99 are indispensable.
2. An individual bad residual can be -2; only a good residual is promoted
   to nonnegative by divisibility. No bad-pair positivity is assumed.
3. A three-edge component must be C3 and fails odd opposite-label closure;
   this justifies connectedness rather than presupposing it.
4. The m=4 case has at most six simple edges; m=7 has all degrees 2.
5. A hypothetical degree-5 vertex needs at least six vertices and total
   degree at least 15. Degree sequences with degree 5 are not omitted.
6. The exact excess partitions for m=5 and m=6 cover every high-degree case.
7. Both signs of the edge between the two universal vertices fail 2s=0;
   spoke cancellation uses identical endpoint residues.
8. Deleting the six-vertex degree-4 center gives precisely P3 disjoint K2,
   not an assumed theta graph; its odd and even contributions cannot cancel.
9. Four positive residual degrees (2,2,1,1) permit only P4; no triangle
   plus isolate survives that degree sequence.
10. The signed fan has seven genuine edges and satisfies modular rows;
    it is retained until the binary commutator contradiction.
11. The two binary solutions of 2x+y=0 are (0,0) and (1,1); equality is
    not asserted for arbitrary GF(3) entries or disconnected supports.
12. The pair d,e need not be an A-nonedge. Worst internal degree 4 and
    A_de=0 still yield residual >=8, then >=9; the row budget remains <=4.

These are twelve paper checks and one written modular-support control,
with zero executed fixtures and zero graph realizations. There is no
formalization, novelty audit, peer review, target matrix, exhaustive
graph-space coverage or computation/performance approval. Discovery
candidate bytes stay unchanged; the independent verdict is a separate
record. The frozen first V17 four-claim batch remains unaffected.
