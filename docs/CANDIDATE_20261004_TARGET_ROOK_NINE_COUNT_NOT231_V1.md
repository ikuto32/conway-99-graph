# Candidate: the target cannot have exactly231 induced rook-nine subsets

Claim C-UNRESTRICTED-TARGET-ROOK-NINE-COUNT-NOT231, revision1.
For every complete finite simple undirected SRG(99,14,1,2), let R count
actual induced nine-vertex rook subsets, each vertex subset once. Then R!=231.
The elementary square count also gives R<=231, so this statement implies
R<=230. It does not exclude all target graphs, construct a target, assume a
particular induced support, or establish any universal Hamming cover.

Status CANDIDATE. Checkpoint authors this written composition; Root posed the
scope question; Structural/Native supplied the already-reviewed square-coverage
context; Makhnev1988 supplies the historical condition(*) theorem. A different
author must review this new exact count statement before its promotion.
No scientific worker, graph census, matrix program, solver or ledger write
was used. The independent primary-source reconstruction is saved separately
in acceleration/audit_20261004_makhnev_theorem2_lemmas6_9_checkpoint_v1.md and
its written report. That report authenticates Makhnev's conditional theorem;
it does not independently approve this new Checkpoint-authored count claim.

## The forward square argument, independently reconstructed

An adjacent edge has exactly one third triangle point. In an induced square
a-b-c-d-a, an actual containing rook must therefore contain the unique third
points on all four edges. In a3-by-3 rook, the third points on two opposite
parallel square edges are adjacent, and their unique triangle partner fixes
the ninth point. Consequently a square is contained in at most one actual
induced rook. This uniqueness does not assume that every square has a rook.

There are99*84/2=4158 nonadjacent pairs. Each such pair has exactly two common
neighbors. Those common neighbors are nonadjacent: otherwise their edge has
the original two points as distinct common neighbors, violatinglambda1.
This produces an induced square. Each square has two opposite pairs, hence
the total number of squares is2079. An induced3-by-3 rook has
binom(3,2)^2=9 squares. Their sets are disjoint across distinct rooks by the
uniqueness argument, so9R<=2079 and R<=231.

Suppose R=231. Then9R=2079, so every square lies in a rook. If there were
two disjoint triangles012 and345 with exactly two cross edges03,14, then
0-1-4-3-0 is an induced square. The unique third points on its opposite
edges01 and43 are2 and5. In any containing rook these two parallel-row
third points must be adjacent. The N3 presentation has no edge25, a
contradiction. Thus R=231 forces N3-freeness.

A point outside a triangle can meet at most one vertex of that triangle,
bylambda1; consequently cross edges between two disjoint triangles form a
matching. N3-freeness is therefore precisely condition(*): at least two
cross edges implies all three. It remains to show that no target graph has
this condition. The following full reconstruction supplies that step.

## The conditional triangle-graph contradiction

The primary source is A.A.Makhnev, Mat.Zametki44:5(1988),667-672, target99
branch of Theorem2 and Lemmas6-9. Primary PDF ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431
is preserved at acceleration/results/20261001_n3_hamming_scope/makhnev_1988.pdf.
All six pages were read visually. The direct spectral ending below avoids an
appeal to the source's separate Theorem1. All target hypotheses and(*) are
retained through this argument.
## Conventions and elementary facts

Let N(x) be the open neighborhood and U=N(a) union N(b) union N(c) for
Delta={a,b,c}. U includes Delta. A point outside a triangle meets at most one
of its vertices, since two such neighbors are adjacent and already have their
third triangle point as the unique common neighbor. Also N(x) induces seven
disjoint edges: each neighbor y has exactly one neighbor within N(x), namely
the unique third point of edge xy. Thus every vertex lies in seven triangles.

The triangle graph Lambda has all actual triangles as vertices. Two triangles
are adjacent only when disjoint and joined by three cross edges. Such cross
edges form a perfect matching. Distinct triangles sharing one point cannot
supply an additional edge between their nonshared points, by lambda1; hence no
shared-point ambiguity is needed in this definition.

Fix Delta. It has36 neighbors outside itself,12 at each of a,b,c, and these
three color classes are disjoint. Consequently |U|=39 and |X|=|V-U|=60.

## Independent reconstruction of Lemma6

Take x outsideDelta adjacent to a. The nonadjacent pair x,b has exactly two
common neighbors: a and a unique y outsideDelta adjacent to b. Let z be the
third vertex on xy. It is outsideDelta: a cannot meet y, b cannot meet x,
and c cannot meet x or y. The triangles Delta and {x,y,z} are disjoint and
have the two cross edges ax,by. Condition(*) forces cz. This is a Lambda
neighbor ofDelta. Any Lambda neighbor containing x must contain the same
unique y and third point z. Therefore the36 points of U-Delta partition
into12 neighbor triangles. Lambda is regular of degree12, with this
partition available around every triangle.

For adjacent triangles Delta={a1,a2,a3} and E={e1,e2,e3}, label the cross
matching ai-ei. Let fi be the unique third vertex on ai-ei. Each fi lies
outside Delta and E, and the three fi are distinct. For i!=j, the disjoint
triangles {ai,ei,fi} and {aj,ej,fj} have two cross edges ai-aj and ei-ej.
All other unintended edges incident to these four points are forbidden by
lambda1. Condition(*) forces fi-fj. Hence F={f1,f2,f3} is a triangle
adjacent inLambda to both Delta and E.

Any common Lambda neighbor G is disjoint from Delta and E. Each of its
vertices meets one ai and one ej. If i!=j, the nonadjacent pair ai,ej already
has the two common neighbors aj,ei, so such a new vertex is impossible.
If i=j, its only possibility is fi bylambda1. Thus G=F. Lambda has lambda1.
This derives Lemma6 without a Hamming-cover or rook-count premise.

## Independent reconstruction of Lemma7

For v inX, each pair v,a, v,b, v,c is nonadjacent, so v has two neighbors
in each color class U-Delta: six distinct neighbors inU. They are independent.
Two from the same color cannot be adjacent because their edge would have
both v and that color's triangle point as common neighbors. Two from different
colors cannot be adjacent: their triangle with v would have two cross edges
toDelta, and(*) would force the third cross edge to v, contradicting v inX.

In the seven-edge matching induced by N(v), these six independent U-neighbors
must pair with six distinct X-neighbors. The two remaining neighbors are inX
and pair with each other. Hence v lies in exactly one triangle wholly inX.
These unique triangles partition X into20 triangles. Call them Lambda2;
call the12 neighbors ofDelta inLambda, Lambda1.

## Independent reconstruction of Lemma8: closure at Lambda1

Take E inLambda1 and its unique common neighbor F withDelta. Suppose G is
adjacent to E and contains a point g ofU. Write g-ei for its cross edge to E.

If g=ai inDelta, then for each j!=i the other matched point ofG must be a
common neighbor of ai,ej. Those two common neighbors are aj,ei. G is disjoint
fromE, so it must contain aj. Therefore G=Delta.

Otherwise g lies inU-Delta and has a unique neighbor al inDelta. If l!=i,
the nonadjacent pair al,ei already has common neighbors ai,el, both unavailable
for g. This violates mu2. If l=i, lambda1 forces g=fi.

If G contains fi, then for j!=i the matched vertex ofG is a common neighbor
of fi,ej. These two points are nonadjacent: an extra fi-ej edge would give
the edge ei-ej both fi and its existing triangle partner as common neighbors.
Their two actual common neighbors are ei,fj. Since G is disjoint fromE,
the matched point is fj. Thus G=F.

Every other neighbor of E is wholly inX, hence belongs toLambda2. As E has
degree12, exactly10 of its neighbors are inLambda2; Delta and F are the
other two. No unobserved vertices or automorphism assumption occur here.

## Independent reconstruction of Lemma9: saturation and full local closure

Take G inLambda2. Each of its three points has six neighbors inU; these18
points are all distinct, since an outside point meeting two vertices ofG
would violate lambda1 on their edge. Each Lambda1 neighbor ofG consumes
three of these18 points, and different neighbor triangles have disjoint
points by the Lemma6 partition aroundG. Therefore G has at most six
neighbors inLambda1.

Lemma8 gives12*10=120 incidences betweenLambda1 andLambda2. There are20
Lambda2 triangles, each with at most six incidences. Equality of the totals
forces exactly six for every G. Those six triangles consume all18 U-points
neighboringG. Any remaining Lambda neighbor ofG cannot contain another
U-point, by the unique partition of N(G)-G into its12 Lambda neighbors.
The other six neighbor triangles are therefore wholly inX and inLambda2.

Thus Lambda0={Delta} unionLambda1 unionLambda2, with33 vertices, is closed
under every Lambda adjacency. It is connected: Lambda1 meetsDelta and every
Lambda2 vertex has six neighbors inLambda1. It is a full connected component
ofLambda, regular of degree12, inheriting lambda1.

The statement mu6 for every nonadjacent pair requires one extra explicit
closure argument, not just the six neighbors of Delta and G. Recenter the
same construction at ANY E inLambda0. It gives a closed connected33-vertex
set containingE, so it is the same connected componentLambda0. Its20
nonneighbors ofE each have six common neighbors withE by the preceding
incidence argument. This proves mu6 for all nonedges, without transitivity.

## Direct spectral contradiction replacing the source's Theorem1 appeal

For the adjacency matrix M of Lambda0,
M^2=12I+1M+6(J-I-M)=6I-5M+6J.
Connectedness makes the degree12 eigenvalue simple. On the orthogonal
complement of the all-ones vector, eigenvalues satisfy x^2+5x-6=0,
so are1 and-6. If their multiplicities are f,g, then f+g=32 and
trace(M)=0 gives12+f-6g=0. Substitution yields7g=44, impossible for an
integer multiplicity. This uses no floating eigenvalue computation or
classification theorem.


## Conclusion and evidence boundaries

Under the supposition R=231, square coverage forces(*). The33-vertex closed
triangle component derived under(*) has impossible integer eigenvalue
multiplicities. Therefore R=231 is impossible. This proves the exact candidate
statement without assuming R=231 as an ambient hypothesis or invoking a
universal Hamming cover.

The separate accepted deficiency-gap statement R!=230 is unchanged. A later
explicit composition could combine it with this new R!=231 and the square
upper bound to obtain R<=229. That composition is not silently registered
or asserted as an independently approved new claim here.

The theorem ruling out(*) was already cited in the October1 source record.
This candidate makes no novelty claim for Makhnev's1988 result. Its new work
is an explicit primary-proof reconstruction and its precise rook-count
composition. It contains no computational coverage denominator or target
resolution. The known rook9 is N3-free and is consistent with the proof:
its degree4/order9 do not produce the target39/60/33 local counts.

The originals, all raw reports, the conditional square-coverage paper and
its revisions remain immutable. This new candidate needs different-author
review of the forward square implication, triangle-component closure,
recenteredmu6 argument, exact trace equations and count scope.
