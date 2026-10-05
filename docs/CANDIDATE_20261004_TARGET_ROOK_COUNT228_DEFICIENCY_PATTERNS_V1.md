# Candidate: deficiency patterns at exactly228 induced rooks

This is a new source-only written candidate. It preserves every prior rook
paper, candidate, audit and binding. Root proposed examining the gap-six
boundary around a deficiency-two triangle; Structural derives the restrictions
below. No mathematical program, graph enumeration, import or solver ran.
Different-author review is required. No R228 exclusion is asserted.

## Exact statement

For every complete finite simple SRG(99,14,1,2), suppose R=228, counting actual
induced rook-nine vertex subsets once. Put d_T=6-r_T for each actual triangle T,
where r_T counts these rooks containing T. Then every d_T belongs to {0,1,2}.
If h counts deficiency-two triangles, then

    1 <= h <=5,
    #{T:d_T=1}=18-2h >=8.

For any deficiency-two triangle T, let k count the deficiency-two triangles
which form a defect pair with T at one of its three points. Here a defect
pair means that no actual induced rook contains both triangles. Then

    k <=3;
    k=3 implies h=4.

In particular, h=5 forces k<=2 for every deficiency-two triangle. The graph
on the h deficiency-two triangles, joining actual defect pairs, therefore
has maximum degree two when h=5. If it has a degree-three vertex, h=4 and
it is either a three-leaf star or that star with one edge between two leaves.

All counts refer to actual triangle and point incidences. The statement does
not assume point multiplicity two, an induced positive support, equitable
profiles, a graph automorphism, a nonconstant codeword, or a realization of
any surviving abstract pattern. It does not prove R!=228.

## Explicit dependency use and overlap

Two independently reviewed conditional results supply only the initial
deficiency range:

- C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1:
  d_T<=230-R whenever R<231.
- C-UNRESTRICTED-TARGET-NONZERO-ROOK-DEFICIENCY-MAXIMUM-LOWER2 r1:
  whenever R<231, some d_T>=2.

At R228 these imply maximum deficiency exactly two. The identities, parity
and even-six rook classification used below are rederived from the graph
hypotheses. Their overlap with the preserved R!=230 paper is disclosed.
Neither that old R!=230 approval nor the R!=229/R!=231 conclusions is an
approval of this candidate.

The current papers describing D12 and the all-d1 obstruction do not contain
the h1..5 and (h,k) restrictions stated here. A targeted literal search of
the current rook/deficiency Markdown files found no such statement. This
is a bounded overlap check, not a whole-archive or worldwide novelty claim.

## Triangle geometry and local degree identities

Each target edge belongs to one actual triangle, and the neighborhood of a
vertex is seven disjoint edges. Hence there are231 actual triangles. Distinct
triangles intersect in at most one point. Three actual triangles cannot meet
pairwise at three different points: those points would form a triangle and
give an original triangle edge a second triangle partner.

For each point v, let D_v be the simple graph on its seven incident actual
triangles, joining a pair when no induced rook contains both. Two triangles
through v determine at most one rook by the four cross pairs' unique second
common neighbors. Each rook containing T gives one different nondefective
partner at v. Thus

    deg_(D_v)(T)=6-r_T=d_T for each v in T.

Counting the six triangles of each rook gives sum_T d_T=6(231-R)=18.
At each v, the number of degree-one nodes of D_v is even. Since all d_T
are zero, one or two, the family P of deficiency-one triangles has even
incidence at every actual point. Write p=|P|; then p=18-2h.

## An even selection of fewer than six actual triangles is impossible

If a nonempty even-incidence selection had two triangles, each point of one
would need to lie in the other, contrary to intersection size at most one.

If it had four triangles, a point in all four leaves their eight distinct
other points with odd incidence and no further triangle to repair it.
Otherwise every used point has multiplicity two. The dual graph with
selected triangles as nodes and used points as edges is then simple cubic
on four vertices, hence K4. Its triangle contradicts the prohibition of
three actual triangles meeting at three different points.

The number of triangles in an even-incidence selection is even, since its
total incidence is three times that number. Thus there is no nonempty
selection of size below six.

## Defect-neighbor mass around a deficiency-two triangle

Fix T={a,b,c} with d_T=2. At each of its three points T has two defect
neighbors. These six actual triangles are distinct; partition them into
the three buckets C_a,C_b,C_c according to their point on T, and write C
for their union.

Let k of these six have deficiency two. The total deficiency of C is

    K=6+k.

At a bucket's central point, a C triangle may have other defect partners;
we do not discard those incidences. At each of its other two points,
however, every defect partner lies outside C and T. Two C triangles in
the same bucket cannot meet at an outer point without meeting twice.
Two from different buckets cannot meet there without forming the forbidden
three-triangle configuration together with T.

Consequently C supplies exactly2K outer defect incidences. These are
incidences with multiplicity, not necessarily2K distinct points. The twelve
outer points of the six C triangles themselves are distinct, by the same
linearity and three-triangle prohibition.

An external triangle can contribute at most three of these outer incidences:
it can meet at most one outer C point in each bucket. If it met two C
triangles in one bucket at distinct outer points, those two C triangles
and the external triangle would meet pairwise at three different points.

The external positive deficiency mass is

    M=18-2-K=10-k.

Let ell count deficiency-two triangles outside C and T. All other positive
external triangles have deficiency one, so their number is M-ell=10-k-ell.
Capacity of at most three per such triangle gives

    12+2k =2K <=3(10-k-ell),
    3ell+5k <=18.                                      (1)

Since ell>=0, k<=3. This is stronger than merely using the strict global
bound on d_T. It is a local restriction on actual defect neighbors.

If h=9, there are no deficiency-one triangles. Then all six neighbors in C
have deficiency two, so k=6, contrary to this restriction. If h=8 or7,
p=2 or4, contradicting the preceding even-selection argument. Thus h<=6.

## Six deficiency-one triangles would force too many external triangles

It remains to exclude h=6 and p=6. For any six distinct actual triangles
with even incidence, a point in all six leaves twelve odd outer points
uncovered. A point in four leaves eight outer points needing the remaining
two triangles, which have only six incidences. Thus all used points have
multiplicity two.

Their dual is a simple cubic triangle-free graph on six vertices. To see it
is K3,3 without a catalog, take any vertex and its three mutually
nonadjacent neighbors. There are exactly two other vertices. Each of the
three neighbors needs two further neighbors and must use both of those
vertices. This fills a K3,3 and every degree. Its nine edge points are the
three row and three column triangles of a rook-nine. Any extra edge in that
nine-set already has two rook common neighbors and violates lambda1, so
the rook is induced.

Therefore the six deficiency-one triangles at h6 are the six actual
triangles of an induced rook on nine points. At each of its nine points,
the two deficiency-one triangles are rook-covered and not a defect pair.
Each nevertheless has local degree one in D_v. Its defect partner must be
a deficiency-two triangle: the other four deficiency-one triangles do not
contain that point, and a zero-deficiency triangle has no defect edge.

Every one of those nine points must consequently lie on at least one of
the six deficiency-two triangles. But an actual triangle different from
the six rook triangles can contain at most one point of this rook.
Two nonadjacent rook points cannot both lie in a triangle, and for two
adjacent rook points lambda1 fixes their third point to the existing rook
triangle. Six external triangles therefore cover at most six rook points,
whereas nine are required. This contradiction excludes h6.

The accepted maximum-lower2 statement gives h>=1. We have now proved
1<=h<=5 and p>=8.

## The saturated (h,k)=(5,3) case cannot supply the missing partner

For a chosen T with k=3, the identity h=1+k+ell gives ell=h-4. Since h<=5,
the only possibilities are (h,ell)=(4,0) or(5,1).

Suppose h5 and ell1. Then K9 and M7. There are six positive external
triangles: five deficiency-one triangles and one deficiency-two triangle O.
The18 outer defect incidences exhaust their combined capacity of18. Each
external triangle must therefore contribute exactly three, one in each
bucket. Its three actual points are the three distinct outer C points at
which these defect edges occur. In particular it meets no central point
of T.

At any point v of O, exactly one C triangle C(v) occurs; outer C points
are distinct. Triangle O has one defect edge there to C(v) and requires
a second defect partner because d_O=2. This partner cannot be T or any
other C triangle: v is an outer C point. It cannot be another external
deficiency-two triangle: O is the only one. It must be an external
deficiency-one triangle Z.

But saturation applies to Z as well. At each of its three points it is
already joined by its unique defect edge to the unique C triangle at that
point. At v that triangle is C(v). Z cannot also have a defect edge to O,
since its degree in D_v is one. This contradicts O's required second
partner. Hence h5,k3 is impossible.

This reasoning uses the exact actual point labels and individual local
degrees. Counting18 incidences alone would not exclude this case; the
missing-partner contradiction is the additional step.

## The finite pattern table and the deficiency-two graph

For reference, the capacity inequality and the new saturation rejection give:

| k | K | M | outer incidences | ell upper bound from(1) | h after all restrictions |
|---|---:|---:|---:|---:|---|
|0|6|10|12|6|1,2,3,4,5|
|1|7|9|14|4|2,3,4,5|
|2|8|8|16|2|3,4,5|
|3|9|7|18|1|4 only|

These are necessary possibilities, not completed target patterns. In
particular the (k3,h4) case has seven external deficiency-one triangles
with capacity21 for18 outer incidences. It is not saturated and is not
excluded by the preceding argument. The (k2,h5) case has six external
positive triangles with capacity18 for16 incidences and likewise remains.

The deficiency-two graph is simple, since any two actual triangles meet at
most one point. Its node degree is exactly k as defined above. At h5 every
degree is at most two, so its components are paths, cycles or isolated nodes;
a three-cycle is allowed by this graph statement when all three actual
triangles meet at one point. No cubic dual is imposed.

If a degree-three node T exists, h4 and its other three nodes are precisely
its three deficiency-two neighbors in C. Two of these can intersect only
when they are in the same bucket; different buckets' outer points are
distinct and their central points differ. No bucket contains more than
two neighbors of T, because T's local defect degree is two. Thus among
the three leaf nodes there can be at most one edge. The graph is the
three-leaf star or that star plus one leaf edge. The latter's triangle
must be realized at their common central point, not at three different
points. No uniqueness or realizability of these graph shapes is claimed.

## Hand falsifications and scope limits

The even-six classification does not forbid a binary six-triangle relation:
the rook itself is an allowed relation. The h6 contradiction requires those
six triangles all have deficiency one and that only six deficiency-two
triangles are available to supply missing partners on nine distinct points.

The stars at the eight vertices of the ordinary cube form eight actual
triangles in its line graph. Each of the twelve edge points lies in two
stars. That selected edge union has lambda1, and nonadjacent common-neighbor
counts at most two, but is not the target SRG. It is a hand boundary showing
that even-incidence parity alone does not exclude p8. No deficiency values
or full target are assigned to this example.

The scalar slot counts alone permit k3,h4 and k2,h5; their unused slots
must not be treated as a new equality contradiction. Conversely k3,h5
has zero unused slots and the exact local degree conflict proved above.
Extra target edges on the broader positive support have not been assumed
absent. The only inducedness assertion is the rederived nine-point rook
in the h6 branch, forced by lambda1.

A local triangle among deficiency-two nodes at one point is not forbidden
by the three-triangle prohibition; only three different intersection points
are forbidden. The new graph restrictions retain this boundary.

This candidate is a necessary screen for an R228 target only. It gives no
target realization, contradiction for all surviving cases, code dimension
bound, automorphism, or nonconstant-codeword assertion. There is no scientific
coverage census. Root received the mechanism before freeze; a different
reviewer must reconstruct the parity, nine-versus-six actual-point argument,
individual saturation partners, and the table before promotion.

