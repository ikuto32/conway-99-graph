# Candidate: R226 with maximum deficiency two has at most ten d2 roots

Structural derived the six-selection bridge-capacity and eleven-node
two-step contradictions. Root challenged the retained fourfold-incidence
boundaries before this freeze. Cubic-eight, even-six and rook uniqueness
components overlap the earlier R227 paper, but the present population and
fan capacity are reconstructed for R226. No old mathematical gate approves
this new exact scope. No program, import, enumeration, solver or worker ran.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle T.
Suppose R=226 and every d_T belongs to {0,1,2}. If b counts actual
deficiency-two triangles, then b<=10.

Maximum deficiency two is an explicit hypothesis, not inferred from a
pending theorem. The statement neither excludes R226/maxd2 nor asserts any
remaining population exists. The logical dependency list is empty; all
selected-family and rook facts needed below are reconstructed here.

Let a count d1 triangles. Since sum d_T=1386-6R=30, a=30-2b and the
positive population P=a+b=30-b, with integers0<=b<=15. At each actual point
the local simple defect graph has its incident triangles as nodes and joins
a pair when no induced rook contains both. Its node T has degree d_T:
each containing rook pairs T with one of the six other incident triangles,
and intersecting row/column uniqueness permits at most one rook per partner.
Thus r1 is even, and the d1 triangles form an even-incidence selection O.

The actual positive fan inequality is

    P>=3r1+5r2.                                      (1)

Its proof counts every focal positive root and its2d outer defect partners.
An external positive triangle cannot meet two outer points of this whole
fan: two points of one root violate linearity, while points of different
roots make three actual triangles meet at three distinct points, violating
lambda1. No uniform profile, automorphism or induced support is assumed.

## Multiplicities are proved, not assumed

For any even selection of s actual triangles, suppose a point is used by r
of them. Their2r outer points are distinct, and each has odd selected
incidence from its one fan root. Parity requires another selected root at
each point. One selected triangle external to the fan meets at most one
of those points, by the same actual geometry. Therefore

    s-r>=2r, or s>=3r.                               (2)

In particular, for s6 or8 every nonzero even point multiplicity is exactly
two: multiplicity four would require at least twelve selected triangles.
The exceptional multiplicity-four case is rejected by this explicit count,
not discarded by a cubic-dual assumption. The dual of either selection has
triangle nodes and intersection-point edges; it is simple cubic and
triangle-free, since a dual triangle has three distinct actual intersections.

For a general even selection of positive size s, put w equal to half its
point multiplicity. Let K=sum w(w-1), ell=sum(w_u-1)(w_v-1) over selected
triangle edges, and H be the weighted sum of every other actual internal
edge. Every nonzero w is at least one, so K,ell,H are nonnegative. The exact
expansion, with Q=3I-A+J/9 positive semidefinite, gives

    w^TQw=s(s-6)/4-5K-2ell-2H>=0.                   (3)

This identity permits arbitrary larger even incidences and extra actual
edges. It will handle s2/4 without a hidden nonempty-size assumption.

## Rook uniqueness and the small even selections

Two intersecting actual triangles in a containing rook must be a row and
column. Their common point p and other points a,b and c,d are fixed. Each
cross nonadjacent pair from {a,b} and {c,d} has p as one common neighbor;
mu2 fixes its second common neighbor and therefore the four other rook
points. Two disjoint actual triangles in a containing rook must be parallel
rows or columns. Their actual cross edges form a matching, because an
outside vertex cannot meet two vertices of an actual triangle. Lambda1
fixes each matching edge's completing point, which gives the third parallel
triangle. Consequently any two actual triangles determine at most one
containing induced rook. This is uniqueness conditional on existence.

Even selections of size two or four are impossible by(3). An even selection
of size six has multiplicity two by(2); its cubic triangle-free six-node
dual is K3,3. For a root node, its three neighbors are independent and each
must join both remaining nodes. The nine edge points form an actual rook.
An extra edge between grid nonneighbors would have two existing common
neighbors and violate lambda1, so this rook is induced. Its six actual
triangles are exactly the selected ones.

An even selection O of size eight cannot share four or more triangles with
an actual rook B. Their symmetric difference has even point incidence and
size14-2|O intersect B|. At overlap five or six this has size four or two,
impossible. At overlap four it is another six-triangle induced rook B',
distinct from B, sharing with B the two triangles of B outside O. This
violates the preceding two-triangle uniqueness. Thus every actual rook
contains at most three triangles of O.

## b11: the eight d1 roots force an impossible eleven-node defect graph

Here a8 and P19. By(2), the d1 selection has twelve support points and a
simple cubic triangle-free eight-node dual G. Every edge of G is in a
four-cycle, as follows without a graph census. A graph with no four-cycle
would have a root, its three neighbors and six distinct further neighbors,
requiring ten nodes. Choose a four-cycle C; it has no chord. Its four cross
edges to the remaining four nodes leave four internal edges among those
nodes. A triangle-free four-node graph with four edges is another four-cycle
C': a degree-three node would allow only its three incident edges. Hence the
cross edges form a bijective matching. Transporting C' to C's four labels,
the two cycles are either equal or share a perfect matching. At every label
there is an adjacent label common to both cycles, which supplies a square
containing that cross edge. Thus all twelve dual edges are square edges.

Such a dual four-cycle gives an actual induced square on four distinct
intersection points. A diagonal edge would have its two square corners as
common neighbors and violate lambda1. If a rook covered this square it
would contain its four selected edge-completing triangles, forbidden by the
eight-selection overlap result. Therefore at every selected support point
its two d1 roots are each other's defect partners, filling their degree-one
slots. A d2 root there needs two other d2 partners, so r2>=3, and(1) would
give P>=3*2+5*3=21>19. No d2 triangle meets the selected support.

At every d2 point there are consequently no d1 roots. Its local degree two
needs r2>=3, whereas(1) gives5r2<=19; hence r2=3 and the local defect graph
is K3. The eleven d2 roots form a simple six-regular defect graph F2. Each
adjacent pair has exactly one common F2 neighbor: any common root must
concur at their unique actual intersection, where exactly three roots are
present. Nonadjacent pairs are actual disjoint triangles, because every
intersection here is a defect; they have at most three common F2 neighbors,
as cross target edges form a matching with unique triangle completions.

For one root, its six neighbors each give five length-two paths other than
the return path. The thirty resulting endpoints are counted by common
neighbors with the other ten roots. Six adjacent endpoints contribute one
each; the four remaining endpoints contribute at most three each. Thus

    30<=6+3*(11-7)=18,                               (4)

a contradiction. The changed positive population19 is used explicitly;
the old R227 population16 gate is not transferred.

## b12: an actual rook cannot supply enough d2 bridge incidences

Here a6 and b12. The selected six d1 triangles form an induced rook on
S of size nine by the complete six-selection argument above. Its eighteen
edges give chi_S^TQchi_S=27-36+9=0. Positive semidefiniteness forces
Qchi_S=0, or

    Achi_S=3chi_S+j.                                 (5)

Every actual outside vertex has exactly one S neighbor. The only actual
triangles wholly inside S are its six row/column triangles, all designated
d1. Any other actual triangle has at most one S point: two adjacent S
points already have their unique third point in that d1 triangle, and an
outside vertex with two S neighbors would also contradict(5).

At every S point the two selected d1 triangles are a covered rook pair,
so neither can use the other as its degree-one defect partner. Both need
positive d2 partners. In particular each S point belongs to at least one
d2 triangle. Let t be the total d2/S incidence. Since each such triangle
meets S at most once, t>=9 counts distinct bridge triangles.

The two outer points of every bridge are outside S. These2t points are all
distinct across bridges: if two bridges shared an outside point, their S
points would both be its unique S neighbor by(5); they would then share
that S point as well, violating linearity. There are no d1 triangles at
these outside points, since all six lie wholly in S. Local d2 degree two
requires at least three d2 roots at each point. Thus the complete outside
d2 incidence satisfies

    3b-t>=3*(2t)=6t, hence3b>=7t>=63.                (6)

But b12 gives3b36. Covered intersections and any extra outside edges cannot
avoid the actual-vertex incidence count. No positivity of a signed design
or presumed automorphism is used.

## b13, b14 and b15

For b13/14 the selected positive d1 sizes are four/two. Their base in(3)
is-2, and subtracting nonnegative terms cannot give a positive-semidefinite
value. Both are impossible; larger selected multiplicities were allowed.

For b15 there are no d1 roots and P15. Every point of a d2 root has at
least three d2 roots, while(1) permits at most three. Their45 incidences
therefore use exactly fifteen actual points S, each in three designated
triangles. The45 edges in those fifteen actual d2 triangles are distinct.
Extra internal actual edges only increase e(S), so

    chi_S^TQchi_S=45-2e(S)+25<=45-90+25=-20,         (7)

impossible. This zero-d1 branch is treated separately from a nonempty even
selection, and no inducedness of S is assumed.

All integer b11..15 have been excluded, proving the literal upper bound10.

## Boundaries and review requirement

The eight-selection is not itself forbidden: its twelve-point line graph
can satisfy the local selected incidence conditions. The contradiction
uses P19, occupied d1 slots and the complete remaining eleven-node
common-neighbor count. A degree-six abstract graph without the exact
adjacent-one/nonadjacent-at-most-three constraints is no counterexample
to(4). At b12, merely counting six even triangles is insufficient; the
actual induced rook and its full-target equation(5) are essential. The
zero-d1 branch does not inherit a selected support by convention.

Earlier parity, cubic-eight, even-six, uniqueness and upper Gram proofs
overlap. This paper makes no archive-novelty assertion. It preserves all
covered actual intersections, arbitrary additional target edges and larger
selected incidences until their separate exact bounds exclude them. A
different complete written audit must bind this exact R226/maxd2 statement
before VERIFIED or ledger use. Remaining b0..10 are not claimed realizable;
no whole R226 or target exclusion, computation gate or publication change
is asserted.
