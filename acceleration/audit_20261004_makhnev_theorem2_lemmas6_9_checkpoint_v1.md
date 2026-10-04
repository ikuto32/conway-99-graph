# Independent written audit of Makhnev's target99 branch

A. A. Makhnev, "On strongly regular graphs with lambda=1", Matematicheskie
Zametki44:5(1988),667-672. The preserved Russian primary PDF is
acceleration/results/20261001_n3_hamming_scope/makhnev_1988.pdf,
SHA256 ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431.
All six preserved page images were visually read. Printed p668 states
condition(*) and Theorem2. The target99 proof is Lemmas6-9 on pp671-672.
The separate115/18/1/3 branch and Lemmas1-5/10 are not independently proved here.

This is a different-author written reconstruction of the primary target99 proof,
not a census or an execution gate. Root requested the challenge and suggested
checking eigenvalue multiplicities directly. Checkpoint independently reconstructs
the incidence/closure argument and its arithmetic. No matrix or graph program,
solver, code import, scientific worker, formal checker or ledger write was used.

Exact verified statement: no complete finite simple undirected SRG(99,14,1,2)
can satisfy condition(*): two disjoint triangles joined by at least two
intertriangle edges are joined by exactly three. This is the target99 branch of
Theorem2; it is conditional on(*), not unrestricted target nonexistence.
For lambda1, cross edges between disjoint triangles form a matching, so(*)
is exactly absence of the induced six-point two-triangle/two-cross-edge graph N3.

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

## Scope, attempted falsifications and prior overlap

The target order99/degree14/mu2 are essential for the39/60/12/20/33 counts.
The known rook(9,4,1,2) is N3-free and causes no contradiction: its complement
X around a triangle is empty, so the target's20-triangle argument does not apply.
No step identifies all actual graph triangles with the33-component; the full
target has231 triangles and Lambda could have other components. Their existence
does not repair the impossible33-component.

The historical October1 literature note already cited this target99 theorem.
Its saved9/243 finite fixture and universal_cover UNKNOWN are not promoted.
The present work authenticates and reconstructs the previously unreconstructed
primary proof. It makes no novelty claim for Makhnev's theorem, no unrestricted
Hamming cover, no target construction, and no unrestricted target exclusion.

The separately accepted square-coverage paper proves R=231 iffN3-free.
The present primary reconstruction supplies its formerly missing N3-free
nonexistence premise. A separate new R!=231 candidate may combine them; it
must not silently overwrite the accepted R!=230 statement or the historical
conditional paper. In fact only the forward R=231=>N3-free is needed for
that count exclusion, and it can be rederived directly as in the new candidate.
No claim that all possible target graphs are N3-free is made.

Primary bibliography: https://www.mathnet.ru/eng/mzm4220 ; Russian pages667-672.
All preserved primary PDF/PNG, historical note and existing claim bytes remain
unchanged. This audit establishes only its exact written theorem scope.
