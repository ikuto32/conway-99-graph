# Candidate: the one-d3, six-d2 R226 lane has at most one bad focal point

Structural independently challenged Root's fan and Gram-equality outline.
The new containing-rook argument below also removes mixed and full good
attachments in the zero-bad-point case. This is a written CANDIDATE necessary
profile, not a six-d2 exclusion. Earlier papers and raw records are unchanged.
No mathematical program, import, enumeration, backend or worker ran.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_U=6-r_U, where r_U counts such sets
containing the actual triangle U. Suppose R=226, every d_U belongs to
{0,1,2,3}, exactly one actual triangle T has deficiency three, and exactly
six actual triangles have deficiency two. There are then fifteen d1
triangles. Each point of T is incident either to exactly three d1 triangles
and zero or one d2 triangle, or to exactly one d1 and two d2 triangles.
At most one T point has the latter profile.

If all three T points have the former profile, all their d2 incidences are
zero. The even selected family O=D1 union {T} has sixteen triangles and
support S=T union B_s of size21. Its three T points have selected incidence
four; the eighteen B_s points have selected incidence two. The actual
induced S has exactly the48 selected triangle edges. There is a partition

    T (3 points), B_s (18), B_o (18), C (60)

whose actual per-vertex neighbor counts, in that order, are

    T:   (2,6,6,0)
    B_s: (1,3,0,10)
    B_o: (1,0,3,10)
    C:   (0,3,3,8).

The induced B_o is the disjoint union of three six-vertex triangular
prisms, each of which, together with T, is an actual induced rook-nine.
The induced B_s is a connected cubic graph. Six actual d1 triangles
partition B_s, and the other nine d1 triangles meet T once and provide a
perfect matching on the eighteen B_s points. Each of the six triangles
contains one neighbor of each T point; its matching edges join points
with the same T neighbor.

The one-bad-point branch is retained, including its possible good
attachments and arbitrary other adjacency. No existence, infeasibility,
whole one-d3, R226 or target conclusion is asserted. The dependency list
is empty: the facts used for this conditional statement are derived below.

## Actual labels, parity and the fan inequality

The target identities are A^2=12I-A+2J and Aj=14j. Its nonprincipal
eigenvalues are3 and-4. Thus

    Q=3I-A+J/9 is positive semidefinite,
    Q^2=7Q, Qj=0.

At a vertex v, lambda1 makes its fourteen neighbors seven disjoint
edges, so exactly seven actual triangles pass through v. Two intersecting
triangles have at most one common point. A pair of intersecting triangles
can lie in at most one induced rook-nine: after naming their common point
p and their two outer pairs, each of the four remaining rook points must
be the second common neighbor of one outer-pair combination besides p.
The mu2 identity determines these four points uniquely whenever that rook
exists. This is uniqueness conditional on containment, not an assertion
that every triangle pair has a rook.

The defect graph at v has the seven actual triangles as vertices; an edge
means their pair has no containing induced rook-nine. A triangle U through
v has six other partners, and each rook on U covers exactly one of them
at v. Conditional pair uniqueness therefore gives graph degree d_U.
Zero-deficiency triangles cannot be defect partners. The handshaking
identity makes the number of odd-deficiency triangles through every
actual point even. Hence O=D1 union {T} has even selected incidence.

Three pairwise-intersecting actual triangles must concur. Three distinct
intersection points would make an edge have its original triangle partner
and a second common neighbor. Consequently a positive triangle external
to a whole positive fan at v can meet at most one of that fan's outer
points: meeting two on one root violates linearity, and meeting one on
each of two roots gives that forbidden actual loose triple. Counting two
outer points and d_U required defect partners at each yields

    P >= 3r1+5r2+7r3,                              (1)

where P is the total positive-triangle population. Extra actual edges,
covered intersections and separate local defect components remain allowed.

The total deficiency is1386-6R=30. With c1 and b6 this gives a15 and P22.
At a T point r1 is odd. Equation(1) and the local degree sequence give
exactly these possibilities:

    B: r1=1,r2=2; degrees(3,2,2,1).
    G0: r1=3,r2=0; the T three-leaf star.
    G1: r1=3,r2=1; degrees(3,2,1,1,1).
    F: r1=5,r2=0; the T three-leaf star plus a separate d1-d1 edge.

In B, T joins all three other nodes and the d2 pair is joined. In G1,
T joins the d2 and two d1 leaves; the d2 joins the remaining d1 leaf.
The r1five case F is genuinely permitted by the local fan P22 and is
included until the argument below rejects it. No P21 dichotomy is reused.

## Exact selected Gram and attached-root capacities

Let w be half the even O incidence, extended by zero off its support S.
There are s16 selected triangles and W=sum w=24. Put

    K=sum w(w-1),
    ell=sum (w_u-1)(w_v-1) over selected triangle edges,
    H=sum w_u w_v over every other actual internal edge.

All are nonnegative. Selected edges are distinct because lambda1 gives a
unique triangle on each edge. The exact expansion is

    q=w^TQw=40-5K-2ell-2H.                         (2)

Each selected triangle at a point contributes two selected neighbors;
its weighted edge expansion is3s+4K+ell. This identity does not assume
incidence two or four, or selected inducedness. Moreover q is strictly
positive here. If q=0, positive semidefiniteness gives Qw=0. A point
outside S would require the integer weighted neighbor sum8/3; such a
point exists since W24 and nonzero w>=1 give |S|<=24.

Let Y=3Qw. It is integer2 mod3 and satisfies

    AY=-4Y, sum Y=0, ||Y||^2=63q.                  (3)

Attached d2 roots through different T points are distinct and have
distinct outer points. Same-center repetition violates linearity; different
centers would give a forbidden actual loose triple with T. At an attached
outer point outside S there is no d1 or T root. Local degree two needs
at least two other d2 roots. None can be another attached root: a same-fan
root would meet twice, and a different-fan root would create a second
common neighbor of the corresponding T edge. Thus both are unattached.

For a fixed attached fan center, an unattached root meets at most one
outer point of its whole fan. Accordingly k outside outer points at that
center need at least2k distinct unattached roots. Also distinct outside
outer points require distinct unattached-root pairs by linearity. With
two unattached roots there is at most one such point globally.

An attached root centered at weight one contributes at least0,1,3 to H
for0,1,2 inner outer points. At weight two these bounds are0,2,5.
No attached outer point can be another T point. All these edges are
nonselected and distinct across the actual d2 roots.

## The incidence-six focal case F is impossible

At F the T point has w3 and contributes K6. If another point of T is
good, it has w2, so K>=8 and ell>=2 on T. Equation(2) gives q<=-4.
Two F points have still larger K and cannot help. The remaining case is
one F and two bad points, with four attached and two unattached d2 roots.
Each bad center has four outer points, at most one outside S by the
per-center capacity. At least three are inner, so each attached pair
contributes H>=4. Hence H>=8, whereas(2) gives q<=10-2H<0.
This rejects F without omitting its separate local low-low edge.

## Two or three bad focal points are impossible

First take two bad points p,q and one good point r, and suppose r is G0.
There are four attached and two unattached roots, so at most one of the
eight outer points is outside S. At least seven are inner and H>=10.
The good point gives K>=2. If K>=4, (2) gives q<=0, already impossible.
Thus K2 is forced: r alone has weight two, all other support weights are
one, and ell0. No assumption K4 is used in this branch.

One bad center, say p, has both attached roots wholly in S. The other q
has at least three attached outer points in S. Before extra internal
edges the three T coordinates of Y are2, the six ordinary selected
neighbors of r have value2, and every other ordinary coordinate is5.
Thus Y_r<=2 and Y_q<=-7. The two ordinary points in p's d1 triangle have
Y<=5. Each of p's four wholly attached outer neighbors has two extra
unit-weight neighbors in its d2 triangle, so its Y<=-1.

These eight distinct forced S neighbors of p therefore have Y sum at
most2-7+10-4=1. Let a>=0 count any further S neighbors of p. Since r is
already a T neighbor, these have weight one and Y<=5; hence
Y_p=-10-3a. Each of the6-a remaining outside-S neighbors also has Y<=5,
because its weighted neighbor sum includes p of weight one. Therefore

    (AY)_p <= 1+5a+5(6-a)=31,
    -4Y_p=40+12a >=40,

contradicting(3). Arbitrary extra actual S and exterior edges are included.

If the good point is G1, five attached roots leave one unattached root.
All ten outer points are inner, giving H>=4*3+5=17 and K>=2. Thus
q<=40-10-34=-4. This completes the two-bad-point cases.

With three bad points all six d2 roots are attached. All twelve outer
points are inner and H>=18. K>=2 would give q<0, so K0, all weights
one, and |S|24. Write H=18+z. Equation(2) gives q=4-2z>0, so z0 or1.
After the six wholly inner d2 triangles the three T coordinates of Y
are-7, the twelve outer coordinates are-1, and the other nine coordinates
are5. Their squared norm is384. Any further ordinary edge lowers this
inside norm by at most42, because its two starting Y values are at most5
and each decreases by3. Thus

    ||Y||^2_S >=384-42z >252-126z=63q,

again contradicting(3). We have proved that at most one T point is bad.

## Zero bad points force exact equality and the four cells

Now all T points are good. Their weights give K>=6 and ell>=3. If K>=8,
equation(2) is negative. Hence exactly the three T points have w2 and all
other support points have w1. There are eighteen such points B_s, S21,
ell3, and q=4-2H. The nine central d1 triangles give eighteen distinct
outer points by linearity and lambda1 on the T edges; these exhaust B_s.
The six other d1 triangles partition B_s. A central selected edge joins
the two points having the same T neighbor, whereas each outer triangle
contains one point of each of the three T-neighbor colors.

The selected baseline Y has values-4 on T and2 on B_s, inside sum24 and
inside norm120. Let d count nonselected S edges incident to T. There is
no nonselected T-T edge. The total weighted neighbor increment on S is
2H-d, and its increment on T is d. At baseline2 an integer increment k
changes the square by9k^2-12k>=-3k; at baseline-4 it changes the square
by9k^2+24k>=33k. Consequently

    ||Y||^2_S >=120-6H+39d,
    sum_S Y=24-6H+3d.

Each of the78 outside coordinates is2 mod3 and satisfies y^2-y-2>=0.
Using sum Y=0 gives outside norm at least132+6H-3d, and therefore

    252-126H=63q >=252+36d.

Thus H=d=0. All outside coordinates are-1 or2, eighteen of them2 and
sixty of them-1. Name them B_o and C. Inside S the actual graph is
exactly its48 selected edges.

At a T point the eight selected neighbors have Y sum4. Its six remaining
neighbors must have Y sum12 by AY=-4Y, so all are in B_o. These outside
neighbor sets are distinct by lambda1 on T. A B_s point has one T and
three B_s neighbors with Y sum2; its ten exterior neighbors must all
belong to C. Therefore B_s and B_o have no edges between them.

A B_o point has weighted S-neighbor sum2 because Y=8-3Aw there.
It cannot meet B_s, so it has one T neighbor. The eigenvector equation
then gives three B_o and ten C neighbors. A C point has weighted
S-neighbor sum3, no T neighbor, hence three B_s neighbors; its
eigenvector equation gives three B_o and eight C neighbors. These are
precisely the four stated neighbor-count rows. The regular partition is
derived from equality, never assumed as an equitable-profile hypothesis.

## Containing rooks remove all good attachments

There are exactly r_T=3 actual rooks on T. In any one, its six outside
points induce a connected triangular prism. With no B_s-B_o edges, this
prism lies wholly in B_s or wholly in B_o. Each containing rook covers
one local central triangle at each of T's three points.

At a G0 point all three B_s central triangles are defect partners of T,
so none is covered. At G1 exactly one B_s central d1 is covered with T,
by the explicit degree(3,2,1,1,1) graph. Therefore the number of T rooks
whose outside prism lies in B_s equals the G1 indicator at every T point.
The indicators must all agree: only all-zero or all-one is possible.

Suppose all are one. There is one B_s prism and two B_o prisms on T.
Distinct rooks on T have disjoint outside points: a shared point has a
unique T neighbor and belongs to its unique local triangle by lambda1,
so the two rooks would contain the same intersecting triangle pair and
coincide. Each prism is an entire cubic B_o component. After removing
the two components, six B_o points still induce a cubic graph.

A simple cubic graph on six vertices which has a triangle is a prism
under lambda1: its three external neighbors are distinct, and these
must themselves form a triangle. If it is triangle-free, the three
neighbors of any vertex are independent; the other two vertices must
both join all three of them, giving K3,3. The latter has a nonadjacent
pair with three common neighbors and violates mu2. Thus the remaining
six B_o points form another prism.

Each prism triangle has three different T colors by lambda1. A pair of
nonadjacent prism points already has two prism common neighbors, so
cannot share a T neighbor. Consequently each matching edge joins equal
T colors. Together with T this remaining prism is an actual induced
rook-nine, providing a fourth containing rook. Contradiction. All good
attachments are therefore zero. The three T rooks exhaust B_o as three
disjoint prism components.

Finally every component of B_s contains whole outer d1 triangles, each
rainbow in the three T colors. If it has r such triangles, each color
has r points and its central matching pairs them within the component;
hence r is even. A six-point component would, by the same cubic-six
argument, be a prism and provide a forbidden T rook on B_s. The six
outer triangles in total cannot split into even component sizes without
a two-triangle component, except as one component. Thus B_s is connected.
No assertion that its contracted triangle graph is simple is needed;
two matching edges between distinct outer triangles are not silently
converted into three.

## Boundaries and pending independent challenge

The F profile, both two-bad profiles and the three-bad profile were all
included before rejection. The one-bad branch is retained. The zero-bad
partition is a necessary configuration, not a construction or contradiction.
All containing-rook steps use actual vertex sets and conditional uniqueness,
not a Hamming embedding or an assertion that arbitrary triangle pairs have
a rook. Arbitrary covered intersections and additional exterior edges are
retained throughout. The fan/weighted-Gram method and earlier prism-cell
research overlap; bounded literal searches do not establish archive novelty.
This new exact source requires a different complete written challenge.
No prior profile gate, numerical result or agreement approves it.
