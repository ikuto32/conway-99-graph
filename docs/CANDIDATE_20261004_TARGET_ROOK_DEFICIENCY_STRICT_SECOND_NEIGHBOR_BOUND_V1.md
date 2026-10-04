# Candidate: the rook-deficiency second-neighbor bound is strict

This is a separate source-only written candidate. It preserves the earlier
second-neighbor paper and raw packet unchanged. Root proposed challenging its
equality case; Structural derives the square-count obstruction below. No
graph/matrix program, enumeration, import or scientific invocation ran, and no
different-author approval is inferred from this shared discussion.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
subsets once by their vertex sets. Write R for their number, r_T for those
containing an actual triangle T, and d_T=6-r_T. Let D=sum_T d_T=6(231-R).
If D>0, then every triangle with d_T=m>0 satisfies

    D > 6m,  hence D >=6m+6,
    d_T <=230-R.

Equivalently the last inequality holds for all triangles whenever R<231.
In particular, if R=229, exactly twelve triangles have deficiency one and
every other triangle has deficiency zero. This removes the earlier candidate's
possible d2 equality branch. It does not exclude R229, R231 or a target graph.

The local positive triangle multiplicities at R229 are even and may be2,4,6;
they are not assumed all two. There is no cubic dual, uniformity, equitable
partition, graph automorphism or nonconstant-codeword hypothesis.

## Local defect and square facts reconstructed here

Every point lies in seven actual triangles and every edge has its unique
triangle completion. Distinct triangles meet at most once. Three actual
triangles cannot meet pairwise at three different points: those points form
a triangle, giving an original triangle edge a second triangle partner.

At a point v, form D_v on its seven incident triangles, joining T,U exactly
when no induced rook contains both. Two triangles through v determine at most
one rook: the four nonadjacent cross pairs have v and their uniquely determined
second common neighbor as their two common neighbors. Their four opposite
grid points therefore fix every proposed rook. Each rook through T supplies
one different nondefective partner at each v in T. Consequently

    deg_(D_v)(T)=d_T,  0<=d_T<=6,  sum_T d_T=6(231-R).

For an induced square, the two edges at a corner lie in two distinct actual
triangles. If these triangles are together in a rook, the square itself is
in that rook: its opposite corner is their fixed second common neighbor.
Conversely a rook-covered square makes all four of these corner pairs
nondefective. Thus every corner of an uncovered square belongs to a defect
edge, and hence to a positive-deficiency triangle.

The target has4158 nonedges and2079 induced squares, each counted twice by its
opposite pairs. Any square is in at most one rook: four edge partners and one
unique further edge partner fix all nine points. Every rook has nine squares,
so the number U of uncovered squares is

    U=2079-9R=3D/2.

These are subset counts, not embedding or automorphism counts. No N3-free or
Makhnev premise is used.

## The non-strict mass bound and its entire equality geometry

Fix T={a,b,c} with d_T=m>0. At its three points it has m defect neighbors
per point. These3m distinct triangles form C. Their total deficiency K is
at least3m. A member of C has its defect partner T at its point on T. At
each of its other two points all its defect neighbors are outside C and T:
a triangle in the same bucket would meet it twice, and one in another bucket
would make three triangles meeting at three different points.

There are2K such outer defect incidences. An external triangle can meet at
most one C triangle in each bucket, again by the three-triangle prohibition,
and so can contribute at most three of these incidences. Its positive
deficiency is at least one. Therefore the total deficiency is at least

    D >= m + K + ceil(2K/3) >=6m.

Assume equality D=6m. Every inequality is tight. All3m triangles of C have
deficiency one; there are exactly2m further positive triangles V, also of
deficiency one. Each V meets one C triangle in each bucket and no positive
triangle remains elsewhere. The6m outer points of C are pairwise distinct:
an identification within one bucket violates linearity, and across buckets
gives the forbidden three-triangle configuration with T.

Thus the positive support is a set S of3+6m points. Besides T it contains
the3m C triangles and2m V triangles. Label the V triangles by2m nodes. In
each bucket, a C triangle pairs two distinct V nodes using its two outer
points; each V uses exactly one point in that bucket. These edges form a
perfect matching M_a,M_b,M_c on the same2m nodes. This is a reconstruction
of arbitrary matching choices, not a presumed target symmetry.

## The equality support is forced induced

Let A be the complete target adjacency. The exact SRG equation is
A^2=12I-A+2J. On the all-one vector A has eigenvalue14; on its orthogonal
complement its roots are3,-4. Consequently

    Q=3I-A+J/9

is positive semidefinite. Give T's three points weight m, the6m outer points
weight one and all other points weight zero. The sum of weights is9m. In the
specified triangle edge union, A w equals4m at a central point and m+3 at an
outer point. Therefore (3I-A+J/9)w vanishes on S and its quadratic value is
zero. Any additional edge inside S decreases that value by twice the product
of its two strictly positive endpoint weights. Positivity forbids every
such edge. The specified edge union is exactly G[S].

This uses the target's upper Gram identity, not an arbitrary local lambda1
graph's spectrum. It is the same weighted equality mechanism as the preserved
non-strict candidate, now used to count every possible square in S.

## Too few squares unless all three matchings are identical

Let c_ab=|M_a intersect M_b|, and similarly c_ac,c_bc. Count nonadjacent pairs
in S having two common neighbors in S. Each gives a square in S; every square
is counted twice. The complete pair classification is as follows.

* Two central points are adjacent. A central point and an outer point in its
  own bucket are adjacent. A central point and an outer point in either other
  bucket have exactly two common neighbors: that other center and the unique
  same-V outer point in the first bucket. This gives12m pairs.
* Outer points in the same V triangle are adjacent. In the same bucket they
  are adjacent exactly on that bucket's matching; an unmatched pair has only
  its central point as a common neighbor.
* For outer points in different buckets and different V nodes v,w, the common
  neighbor count is precisely the sum of the two indicators
  [w=M_a(v)]+[w=M_b(v)]. It equals two exactly on an edge common to those two
  matchings. Each common edge contributes two such point pairs.

No other pair category exists. It follows that

    C4(G[S])=6m+c_ab+c_ac+c_bc <=9m,

since each common-matching count is at most m.

Every uncovered square has its four corners on positive triangles, hence
inside S. Equality requires U=3D/2=9m such squares. Therefore G[S] must have
at least9m squares; the preceding bound is attained and c_ab=c_ac=c_bc=m.
All three perfect matchings must be identical.

Choose any edge of their common matching. T, the two corresponding V triples
and the three C triples on that edge form a nine-point rook: T and the two V
triples are rows, and the three C triples are columns. It is induced because
S already is induced. This rook contains T and each of those C triangles,
contrary to their being designated defect neighbors. Thus D=6m is impossible.
Since D is a multiple of six, the strict bound in the statement follows.

## Hand boundaries and retained open cases

For m1, all three perfect matchings on two nodes coincide; the six actual
triangles make a rook. This recovers the earlier R!=230 argument without
asserting that an arbitrary even six-triangle selection is forbidden.

For m2, the three matchings on four nodes have these hand square counts:

| Matching pattern | Sum of pairwise common-edge counts | Squares in S | Required U |
|---|---:|---:|---:|
|All identical|6|18|18, but a defect pair is rook-covered|
|Exactly two identical|2|14|18|
|All distinct|0|12|18|

This is a symbolic classification of three matchings, not a graph census.
At R229 the d2 equality branch fails in every pattern. The remaining case is
twelve d1 triangles with even point incidence. Points supporting four or six
such triangles remain possible on the present proof; no cubic incidence dual
or all-multiplicity-two conclusion follows.

At R231 the total deficiency is zero; there is no positive m to which this
argument applies. At smaller R, the inequality does not prove a construction
or exclusion. Passing these conditions does not supply the remaining graph
or a full SRG completion.

The non-strict D>=6m paper, weighted regular-set identities, R!=230 proof and
local square count are preserved overlap. This candidate's new step combines
local uncovered-square support with the complete equality-square count to
eliminate the entire equality boundary. The October1 Hamming-scope and
September17 rook regular-set records are not global exclusion gates. Root
received the outline before freeze; a different reviewer must reconstruct
all matching incidences, square categories and strict inequality independently.
