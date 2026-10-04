# Independent written review: the rook-nine deficiency-six gap

The exact conditional revision1 statement passes this different-author written
review. I derive the incidence identities directly from the complete target
hypotheses and give a separate elementary proof of the six-node dual graph
step. No target, rook family, graph census, matrix, program or scientific
worker was evaluated. The conclusion allows R=231 and does not establish
target existence or nonexistence.

The first whole paper/raw read for this review began at
2026-10-04T14:47:46Z. The accompanying immutable report records the final
verification timestamp, exact source hashes and all checking boundaries.
Structural is the mathematical producer; Native is the independent written
verifier. Root's prior reconstruction is shared discovery context, not the
independent verification performed here.

## Exact claim and counting objects

Claim C-UNRESTRICTED-TARGET-ROOK-NINE-DEFICIENCY-GAP revision1 has the exact
raw statement:

    For every complete finite simple SRG(99,14,1,2), the number R of distinct induced nine-vertex subsets isomorphic to the3-by-3 rook graph satisfies0<=R<=231 and R!=230. For each actual triangle T, its rook multiplicity r_T yields d_T=6-r_T; at every v in T the simple graph on the seven triangles through v, joining pairs not together contained in an induced rook-nine, has degree d_T at T. These nonnegative deficiencies sum to6*(231-R), and their odd support has even incidence at every point. The count231 and hypothetical target existence are not excluded.

R counts a set of actual vertex subsets. It does not count presentations of
the same subset, grid-coordinate maps, automorphisms, or a disjoint packing.
The full actual triangle family is used once. Containment of two triangles
in a rook requires an existing induced nine-subset, not an incomplete grid
proposal or the assertion that all squares extend.

## Triangle incidence from adjacent common-neighbor uniqueness

Fix a vertex v. Each neighbor a of v has precisely one neighbor b inside
N(v): the unique common neighbor of the adjacent pair v,a. Symmetry of
adjacency makes these links a perfect matching on the14 neighbors of v.
There are seven actual triangles through each v and hence99*7/3=231
actual triangles. Every graph edge is in exactly one actual triangle.

Two distinct actual triangles meet in at most one point. Otherwise their
shared edge would have two different common neighbors. Three actual triangles
cannot meet in three distinct pairwise intersection points p,q,r. Each of
pq,qr,rp is an edge. The triangle pqr completes, for example, the edge pq,
while the selected triangle that contains p and q also completes it. Its
third point cannot be r: that would give this selected triangle two points
in common with another selected triangle. This violates the unique edge
completion. This last prohibition is stronger than hypergraph linearity
alone and is needed in the six-triangle classification below.

## At most one rook for a pair of incident triangles

Write T={v,a,b}, U={v,c,d}. Their four outer points are distinct. A cross
edge such as ac would produce the triangle v,a,c, a second completion of
the edge v,a in addition to b. Thus all four cross pairs ac,ad,bc,bd are
nonadjacent. Each has v as a common neighbor and, by mu=2, a unique other
common neighbor.

If a rook contains T and U, they must be its unique row and column through
v. In grid coordinates their four opposite corner points are precisely
those four uniquely fixed other common neighbors. Consequently all nine
vertices of any such rook are fixed. A second alleged rook containing the
same T,U is the same nine-subset. Distinctness of the four corner points
is inherited from the existence of the alleged rook; it is not asserted
for arbitrary T,U without a rook. This is an at-most-one theorem, not a
grid-existence theorem.

## Local degree identity and an independent packing bound

Let D_v be the simple graph on the seven triangles through v. A distinct
pair is an edge when no actual induced rook contains both triangles.
For a fixed T through v, map a rook S containing T to the other triangle
through v contained in S. An induced3-by-3 rook has exactly two triangles
through each of its points, so this other triangle is unique. Conversely
every nondefective partner of T arises from a rook containing that pair.
The preceding at-most-one theorem makes the map injective as well.

This gives a bijection between the rooks containing T and its nondefective
partners among the six other triangles at v. Therefore

    deg_D_v(T)=6-r_T=d_T,       0<=d_T<=6.

The quantity r_T is global, but this bijection holds at each of the three
points of T separately. The resulting three equal degrees are derived;
they do not posit equitable external profiles or an automorphism.

An induced rook has precisely its three row and three column triangles.
Any actual triangle contained in its nine-subset is among these six.
An external third point cannot replace a row/column edge completion because
that adjacent pair already has its unique common neighbor inside the rook.
Double counting the pairs (T,S) with T contained in rook S gives

    sum_T r_T=6R,
    sum_T d_T=6*231-6R=6*(231-R).

Since each r_T<=6, these identities alone imply R<=231. This is my separate
check on the paper's C4 packing argument, without using a binary-image
injection or an earlier approved packing result. Nonnegativity R>=0 is
immediate for a family of subsets. Overlapping rooks remain counted exactly
by these incidences; no disjointness premise is introduced.

## Checking the paper's C4 route separately

The target has99*14/2=693 edges and choose(99,2)-693=4158 nonedges. The two
common neighbors of a nonedge cannot be adjacent: if they were, their edge
would have both nonedge endpoints as common neighbors. Thus each nonedge
determines one induced square. Each induced square contributes its two
diagonals, giving4158/2=2079 squares.

Every induced C4 in a rook is a rectangle determined by two rows and two
columns. The unique completions of its four edges supply the other four
points on these rows and columns. For two opposite row edges, their third
points are adjacent in the alleged rook, and their unique completion supplies
the remaining corner. These constructions are fixed by the original C4,
so at most one rook contains it. There are choose(3,2)^2=9 rectangles per
rook. Hence9R<=2079, the same R<=231. No implication that an uncovered
C4 forces an N3, or that every square has a rook, is used.

## Evenness and why total deficiency six has only unit entries

At every v the handshake identity in D_v says

    sum_(T containing v) d_T=2|E(D_v)|.

Reducing this integer equality modulo2 proves that the set of actual
triangles with odd d_T has even point incidence. This does not assert an
arbitrary nonzero incidence-kernel word; it describes the actual odd
deficiency support if such deficiencies arise.

Assume R=230. Its total deficiency is6. If some T had d_T=h>=2, then at
each of its three points the node T in D_v would have h distinct partners.
Every partner has positive deficiency, since an incident edge gives positive
degree. The partner lists at different points of T are disjoint: another
triangle cannot meet T at two points. The total deficiency would be at least

    h+3h=4h>=8.

This contradicts6. Therefore all positive deficiencies equal1 and there
are exactly six such triangles. At a point, all other D_v nodes have degree0
and the selected nodes have degree1. Their number is even, and their local
edges form a matching. In particular the selected six actual triangles have
even incidence at every graph point.

## Separate elementary classification of the even six

Consider six distinct actual triangles with even incidence, without assuming
anything about deficiency. Every used point has multiplicity2,4 or6.
A multiplicity6 point would be common to all six triangles; linearity makes
the other twelve triangle points private, contrary to even incidence.
A multiplicity4 point yields eight distinct outer points in those four
triangles. Each needs at least one incidence in the two remaining triangles,
which have only six incidences in total. Eight cannot be covered by six.
Thus every used point has multiplicity2, and there are18/2=9 used points.

Construct a dual graph whose six vertices are the selected triangles and
whose edges are the used points. It has no loop; every point belongs to
two distinct triangles. It is simple by linearity, and cubic since each
triangle contains three points. A triangle in this dual graph would be the
three distinct pairwise intersection points prohibited above.

Here is an elementary alternative to the candidate's complement argument.
Choose a dual vertex w and its three neighbors S. Triangle-freeness makes
S independent. Only two vertices p,q remain outside {w} union S. Every
member of S already meets w and still needs two distinct neighbors, both
of which must be p,q. Hence all six edges between S and {p,q} are present.
These fulfill the degree of p and q; p and q are nonadjacent. This identifies
the graph exactly as K3,3 with parts S and {w,p,q}.

The nine used graph points are therefore the nine edges of this K3,3.
Two points with a shared dual endpoint lie in the same selected triangle
and are adjacent. These are precisely the adjacencies of a3-by-3 rook.
Two points with disjoint dual endpoints already have the other two grid
corners as distinct common neighbors. If an extra graph edge joined this
pair, it would have at least two common neighbors, violating lambda=1.
The nine points thus induce a rook, and it contains all six selected
triangles. This proof allows even-six dependencies; it identifies them.

Return now to the six deficiency-one triangles. At every used point there
are exactly two positive-deficiency triangles. Both occur in the rook just
proved to exist, so they are not an edge of D_v. Every other D_v node has
degree0 and cannot be a partner. The two selected nodes consequently cannot
have their required degree1. This contradiction rules out R=230.

## Written falsification boundaries and limits

1. On the known rook9, each point lies in two triangles and the six actual
   triangles have even incidence. The local cap is2-1=1, r_T=1 and the
   analogous deficiency is0. The even-six classification returns that rook.
   The target-specific formula6-r_T must not be applied to these parameters.
2. At R=231 the identities force every d_T=0. All D_v are empty and this
   argument has no contradictory degree. No actual target realizing this
   necessary pattern is constructed, but it is not excluded by the proof.
3. A total6 pattern containing a d_T=2 requires at least six other positive
   triangles and weight at least8. This rejects partitions with a larger
   entry without assuming all partners have the same degree.
4. Six unit entries satisfy the parity equations only if their incidence is
   even. Once this holds they form a rook; the failure is their required
   defect degree, not the existence of the even selection itself.
5. A multiplicity4 point needs eight outer incidences while only six remain.
   A multiplicity6 point leaves twelve private points. These reject both
   higher point-multiplicity branches explicitly.
6. A triangular-prism cubic dual would contain a three-cycle, which represents
   three graph triangles meeting at different points and violates lambda1.
   K3,3 has the required nine point edges; a complement classification is
   unnecessary for the independent proof.
7. Adding a grid-diagonal edge creates an adjacent pair with the two rook
   cross corners as common neighbors. Removing a row edge destroys one of
   the six selected actual triangles. Neither modification preserves the
   hypothesis used in the even-six conclusion.
8. A mock defect edge between two triangles known to be in one rook is false
   by definition. Absence of an arbitrary proposed completion is insufficient
   to establish a defect edge; actual rook absence is required.
9. Sharing vertices or triangles between different rooks is permitted. A
   common C4 or incident-triangle pair cannot belong to two different rook
   subsets because the reconstruction makes the subsets equal.
10. Counting each rook by its72 coordinate presentations changes both the6R
    and9R coefficients. The present coefficients count nine-subsets once.
11. A nonedge with two adjacent common neighbors would violate lambda1 for
    their edge. Without the exact mu2 premise this target C4 count is not
    justified. No claim about arbitrary lambda1 graphs is substituted.
12. The correct allowed count range is {0,...,229} union {231}. It cannot be
    replaced by R<=229 without an additional proof excluding231.

All twelve boundaries are displayed hand reasoning. They are not executed
fixtures or a complete enumeration of small graphs. The at-most-one statements
remain conditional on existence and do not infer grid cover or Hamming cover.

## Bounded ancestry read and independent-check scope

I read the whole new paper/raw and the five named historical comparison texts:
the October3 double-fiber rook and weight-seven image papers, the N3/Hamming
scope note, the September17 rook regular-set audit and the wave112 C4 short-
vector derivation. They contain the nine-square packing, even-six K3,3
geometry, conditional rook regular-set encoding and the explicit limitation
of the N3-free cover route. Their historical scopes agree with the limits
above. The wave112 cap25 remains a proposed route, not a premise here.

The present proof directly derives the degree/global deficiency mechanism.
No historical approval, binary code gate, enumeration or spectral quotient
is used as a mathematical dependency. Empty claim dependencies are therefore
appropriate. The comparisons do not establish novelty in the entire archive
or literature, and no new external source was sought or used.

The report separates38 written-check boundaries from the twelve hand
falsification boundaries. Mathematical commands, executed controls, formal
or external checking, imports, graph enumerations and scientific launches
are all zero. Candidate bytes and ledger/index/Git state were not changed.
This is a conditional necessary theorem, not a resolution or an executed
rook census. Independent report acceptance and any later registration remain
separate administrative steps.
