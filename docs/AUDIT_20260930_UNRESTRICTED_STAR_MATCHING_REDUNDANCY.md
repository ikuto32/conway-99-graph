# Independent audit: one unrestricted star always passes the local matching test

The quantified statement is valid with precisely the declared partial-graph
scope. The proof below does not infer the universal statement from sampled
stars and does not assume an automorphism or asymmetry of a target.

Let the root-neighbor symbols be 0 through13, with mate m(s)=s xor1.
An outer label is an unordered pair from different mate pairs. Write U={0,2}
for the center u, and let S consist of twelve distinct outer labels, excluding
U. The incidence quotas are1 on symbols0,1,2,3 and2 on4 through13. The root
scaffold has root--inner edges, the seven inner matching edges, and the two
incidence edges of every outer label. No other outer edges are prescribed.

This is an arbitrary labeling convention for the two root pairs meeting u,
not a permutation asserted to fix a hypothetical graph. The already verified
root-scaffold normalization gives its target applicability. The local theorem
can also be read directly as a statement about this explicitly defined graph.

## Matching existence by a separate Hall argument

There is exactly one label y0 in S containing0 and exactly one y2 containing2.
They are distinct because the only pair containing both is U, which is excluded.
Their incidence edges to inner0 and inner2 will be two neighborhood matching
edges. The other ten labels T avoid0 and2. Each symbol occurs in at most two
labels of T. A label has two symbols, each present in at most one other label,
so it intersects at most two other labels of T.

Partition T arbitrarily into sets L and R of size5. Join a label in L to one
in R exactly when they are disjoint. Every label has at least three opposite
neighbors. For a nonempty subset X of L of size at most2, its neighborhood has
at least3 vertices. For |X| at least3, every right label meets at most two left
labels, and thus has a disjoint neighbor in X; the neighborhood is all of R.
In either case |N(X)| is at least |X|. Hall's condition holds, so a perfect
bipartite matching M exists. In particular, the disjointness graph on T has
a perfect matching. This argument is distinct from the producer's maximum
matching augmenting-pair degree proof and uses no search or floating point.

For completeness, the finite Hall implication follows from alternating paths:
if a maximum matching leaves a left vertex unmatched, take all left vertices
reachable from unmatched left vertices via alternating paths. No reachable
right vertex is unmatched, since that would augment the matching. Every such
right vertex is matched back to a reachable left vertex, and at least one
reachable left vertex is unmatched. Consequently |N(X)|<|X|, a contradiction.

## Constructed partial specification

Add the twelve edges u--S and the five outer edges M. Call the graph of known
present edges P. Fully specify the center row, and specify every pair in N(u):
the seven matching edges are present and every other pair there is absent.
Other unprescribed outer entries remain unknown. Zeros of the displayed P
are therefore only lower-count placeholders except at these fixed positions.

These absences are consistent with the scaffold. Inner0 and inner2 are not
mates; their only incidence neighbors within S are y0 and y2 respectively.
No residual label T meets U, and before construction no outer--outer pair is
fixed present. Therefore N(u) consists of the two inner vertices and S, and
induces exactly the two incidence edges plus M, namely7K2.

## Exhaustive pair categories, not sampled-star coverage

For distinct vertices x,y write Q(x,y)=|N_P(x) intersect N_P(y)|+P_xy.
The following categories exhaust all unordered pairs of the99 vertices.

1. Root--inner: common count1 (the inner mate) and adjacency1, so Q=2.
   Root--outer: common count2 (the label's symbols), adjacency0, so Q=2.
2. Two inner vertices: mates have their root as the sole common neighbor and
   are adjacent; nonmates have the root and their unique outer pair-label as
   common neighbors and are nonadjacent. Q=2 in either case. New outer edges
   do not change inner neighbor sets.
3. Inner s and center u: Q=q(s)+1[m(s) in U]+1[s in U]=2, directly by the
   incidence quotas and the two distinct mate pairs meeting U.
4. Inner s and selected label y: the complete value is
   1[m(s) in y]+1[s in U]+1[s in partner(y)]+1[s in y], with the partner term
   absent for y0,y2. The first and last terms cannot both be1, because y is a
   valid outer label. If s is in U, the partner term is0. If s is outside U,
   the second term is0. Thus Q<=2. For an unselected outer vertex other than
   u, both new terms are absent, giving Q<=1.
5. Center u and a selected label y: either y is y0/y2 and contributes its one
   shared inner symbol, or y is in T and contributes its matching partner as
   its one common neighbor with u. Adjacency1 gives Q=2. For an unselected
   label y, only shared inner symbols contribute; distinct labels meet U in
   at most one symbol, so Q<=1 and u,y are nonadjacent.
6. Distinct outer labels x,y, neither equal to u: their common inner count is
   |x intersect y|<=1. A common outer neighbor exists exactly when both are
   selected, and that neighbor is u. Distinct selected vertices cannot share
   a matching partner, since M is a matching. If P_xy=1, they are matched and
   disjoint, giving Q=0+1+1=2. If P_xy=0, Q<=1+1=2. If at least one is
   unselected, its outer-neighbor set is empty and Q<=1.

Thus every pair cap holds. The root and fourteen inner vertices keep degree14;
u has degree14. The two selected labels y0,y2 have degree3, the ten labels in
T have degree4, and the other71 outer vertices have degree2. Hence all degrees
are at most14. There are exactly206 known-present edges, versus189 in the
root scaffold. No unknown outer edge has been interpreted as a target nonedge.

## What the verification establishes

The separate checker reconstructs all99 vertices from the combinatorial label
definition, checks the four saved raw matrices against their claimed matchings,
and checks both the saved and independently found matching for each of the128
saved stars. Its matching algorithm is bipartite augmentation, rather than the
producer's general subset recursion. All pair caps are evaluated by literal
neighbor-set intersections, rather than the producer's bit masks. A separate
unanchored hand-written quota fixture and corrupted controls are included.
Finite local-label category loops are falsification checks of the above case
formulas. They are not an enumeration of all quota-compliant stars.

The universal conclusion rests on the Hall and pair-category derivations.
It says that the specified unrestricted single-star matching/known-cap test
cannot reject a quota-compliant S. It supplies no target completion, no SRG,
no global coverage fraction, and no statement about multiple completed stars
or extra fixed outer edges. In particular, the archived conditional-family
matching filters retain their distinct scope. No novelty claim is made.
