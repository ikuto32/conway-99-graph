# Candidate weight-seven words from three actual triangles

Written on2026-10-02 by /root/structural. CANDIDATE: independent derivation
and calibrated artifact checking are required before ledger promotion or a
changed code dual. No control or scientific command has executed for this note.

Let G be any finite simple graph in which every edge has exactly one common
neighbor. Let B contain one binary incidence column for every actual graph
triangle. No assumption of nontrivial automorphisms or mu2 is used below.

The candidate statement is: distinct unordered triples of actual triangles
whose binary sum has weight7 give distinct words in im_GF(2) B. If every
vertex lies in r triangles, n=|V(G)|, and m=nr/3, their number is exactly

  N7 = n*binom(r,2)*(m-5r+4) + n*binom(r,3).

This counts three-triangle words, not every possible word of imB. Hence it is
a lower bound for the full weight7 enumerator. For a hypothetical target,
n99,r7,m231 give N7=2079*200+3465=419265. The graph and any nonzero kernel
word may fail to exist; the claim is universally conditional on G.

## Intersection types and exact count

Actual triangles are linear: two distinct triangles cannot share an edge,
whose endpoints would have two common neighbors. Three triangles with three
different pairwise intersection points are impossible. Those intersection
points form another graph triangle; one of its edges belongs to its original
triangle as well, contradicting the edge-unique-triangle property.

Thus three distinct actual triangles have one of four intersection types:

* pairwise disjoint: binary-sum weight9;
* exactly one intersecting pair, with the third disjoint from both: weight7;
* an intersection path on three triangles, using two different points: weight5;
* all three through one common point: weight7.

These exhaust the types. In particular a common-point triple is different
from the forbidden configuration with three different intersection points.

For regular incidence r, the intersection graph of triangles has degree
3(r-1): the triangles meeting a given triangle are the disjoint lists at its
three points. Two adjacent triangle vertices have exactly r-2 common
neighbors in the intersection graph, all through their shared point. A
common neighbor using different points would be the forbidden configuration.
The number of unordered intersecting pairs is Q=n*binom(r,2).

For such a pair, exclude the two triangles themselves. The union of their
other neighbor lists has size

  2*(3(r-1)-1)-(r-2)=5r-6.

Therefore m-5r+4 triangles meet neither member. Each resulting exactly-one-
intersection triple has a unique intersecting pair, so Q*(m-5r+4) counts it
once. Common-point triples are counted once by n*binom(r,3). Their supports
have weight7 because the common point has multiplicity3 and six private
points have multiplicity1. The two populations are disjoint.

## Collision falsification by even dependencies

Suppose two distinct triangle triples have equal binary sums. Cancel shared
triangles; this yields a nonempty even dependence on2,4,or6 distinct actual
triangles. Every point has even incidence multiplicity among these selected
triangles.

Two triangles cannot give a dependence: they would have identical supports.
For four triangles, a point of multiplicity4 would lie on all four. By
linearity every other point on those triangles is then private, violating
evenness. Thus every used point has multiplicity2. Form the dual graph whose
four vertices are selected triangles and whose edges are their shared points.
It is simple and3-regular, so it is K4. Its triangle is forbidden by the
different-intersection argument above. Hence no four-triangle dependence.

For six triangles, multiplicity6 would again put every selected triangle
through one point and leave private points, which is impossible. If a point
p has multiplicity4, the four triangles through p have eight other pairwise
distinct points. Each of these points must belong to one of the remaining two
triangles to make its multiplicity even; those two triangles have only six
point incidences in total. Eight incidences cannot fit into six. This rules
out multiplicity4 even when some of the remaining points have higher
multiplicity. Therefore every used point has multiplicity2.

The dual graph on the six triangles is now simple,3-regular and triangle-free.
Its complement is2-regular on six vertices, hence a six-cycle or two disjoint
three-cycles. The complement of a six-cycle contains a triangle; only two
three-cycles remain, giving dual K3,3. Its nine edges are the nine point
supports. For any three selected dual vertices U, their triangle sum is the
edge cut delta(U), of size9-2e(U). A three-vertex subset has split3+0 or2+1
between the two parts of K3,3, so e(U) is0 or2 and the weight is9 or5.

Consequently a six-triangle dependence cannot identify two weight7 triples.
All possible collision sizes have been excluded, proving the proposed
injection. This reasoning permits rook9 dependencies and the known weight5
and weight9 collisions; claiming injection for all three-triangle sums would
be false.

## Character row and dependencies

Let C=ker_GF(2)(B transpose), A_w count its weight-w words, and
M=|C|=1+sum_(w>0) A_w. Character orthogonality gives

  sum_(w>=0) A_w*K7(w)=M*|{y in imB:wt(y)=7}|,
  K7(w)=sum_s(-1)^s*binom(w,s)*binom(n-w,7-s).

The candidate N7 therefore gives exactly

  sum_(w>0) A_w*(N7-K7(w)) <= binom(n,7)-N7.

For the target the denominator is positive. A normalized LP row may use
(419265-K7(w))/(binom(99,7)-419265) with right side1. No row or optimizer has
been executed; the existing seven-weight bound and its artifacts stay intact.
Any changed guide would require this new proof, the separately audited kernel
weight interval/divisibility, and a changed independent certificate gate.
There is no rank upper bound, forced nonzero kernel, optimum, construction,
or nonexistence conclusion here.

## Proposed finite controls and provenance

The unexecuted source protocol uses actual adjacency graphs and recomputes
every actual triangle. Rook9 supplies an even K3,3 dependence and twenty
three-triangle sums: eighteen of weight5 and two of weight9, with collisions
allowed at those weights. A seven-triangle friendship graph supplies35
distinct weight7 sums; one-intersection-plus-disjoint, loose-chain and three-
disjoint controls distinguish all other types. Pasch and completeK7 controls
demonstrate failure without the actual edge-unique-triangle premise. A complete
32768-labelled-mask exhaustion of six-vertex graphs would check all70 cubic
graphs and all20 three-vertex cuts for the ten triangle-free K3,3 graphs.
These are small engineering/derivation controls, not coverage of target graphs.

Scoped archive-overlap search on2026-10-02 examined attempts/ and
verification/ Markdown at YesterdaysLemon/conway-99-research commit
85e705cc6c2a14d123120c93a847e30aaab1789e for419265, weight7 and small even
triangle dependencies. This is not a literature-status claim or novelty proof.
The existing current lowword claim covers j3,4,6 only:
C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS r1,
independent report626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd.
Its character identity is context; its numerical lower counts are not premises
of the injection above. No historical labels have been freshly promoted.
