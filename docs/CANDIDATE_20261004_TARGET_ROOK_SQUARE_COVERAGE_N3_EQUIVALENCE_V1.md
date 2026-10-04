# Candidate: rook square coverage is exactly N3-freeness

This is a source-only written derivation. No graph census, matrix calculation,
code import, solver or scientific invocation was executed. Root proposed the
scope question; Structural reconstructs the local implication and its converse.
The statement remains CANDIDATE pending a different-author written challenge.
The Makhnev consequence below is explicitly conditional on a separately
authenticated theorem, rather than an inherited mathematical gate.

## Exact statement and labeling

Let G be any complete finite simple SRG(99,14,1,2). Let R count actual induced
nine-vertex rook subsets, each once; let U count induced C4 subsets not contained
in any such rook. Let n3 count induced six-subsets consisting of two disjoint
triangles joined by exactly two independent cross edges. Then

    U = 2079 - 9R,
    R=231  <=>  U=0  <=>  G is N3-free,
    0 <= n3 <= 2U = 4158 - 18R.

The square/grid equivalence itself needs only the exact common-neighbor rules
lambda=1 and mu=2, not degree14 or order99. The numerical coefficients above
use the target parameters. No hypothetical automorphism or equitable partition
is assumed. R=231 is not excluded by the local proof.

For a convenient labeled N3 presentation use triangles {0,1,2}, {3,4,5} and
cross edges 03,14, with no other edges. The archive's canonical lexicographic
mask is5941. That number is not the literal mask of this convenient labeling:
with increasing lexicographic pairs and the first pair as the low bit, the
presentation has mask28839. Relabeling old(0,1,2,3,4,5) to new(0,1,5,3,2,4)
gives edges01,03,05,12,15,23,24,34, hence canonical mask5941. This explicit
isomorphism prevents the mask convention from becoming a different graph.
The earlier scope note's bytes and presentation remain unchanged.

## Local facts before any covering inference

An adjacent pair has its unique triangle partner. A point outside a triangle
cannot meet two of its vertices: their edge would have its triangle partner
and that external point as two common neighbors. Consequently cross edges
between disjoint triangles form a matching. If two disjoint triangles have
two cross edges, their induced union is N3 when the third matching edge is
absent, and is the triangular prism when it is present.

Take an induced square a-b-c-d-a. Let e,f,h,g be the unique partners of edges
ab,dc,ad,bc respectively. All four are outside the square and pairwise distinct.
For example e=c would add diagonal ac, while e adjacent to c would make edge
bc have both e and g as common neighbors. If two edge partners coincide,
their common square endpoint, or an endpoint of one of their opposite edges,
has an edge with two distinct square common neighbors. These contradictions
also rule out every unintended edge between a partner and a square corner.

Thus triangles abe and dcf are disjoint and have exactly the known cross edges
ad,bc, and possibly ef. Similarly triangles adh and bcg have exactly ab,dc,
and possibly hg. A rook containing the square must contain these four unique
partners. If it exists, ef and hg are edges, and the unique third vertex on
ef determines its ninth point. Therefore every square is in at most one rook.

## N3-free implies a unique rook around every square

Assume G is N3-free. The two opposite-triangle pairs just described force
ef and hg. Let i be the unique partner on ef and j the unique partner on hg.
The partial grid consists of the square and its four edge partners. Its
lambda1 constraints make i and j distinct from those eight points: for
example h cannot be adjacent to e, since edge ah already has partner d and
would acquire e as another common neighbor. The remaining exclusions follow
from the corresponding corners in the same way.

Now a-b-g-h-a and d-c-g-h-d are induced squares. For the first, the disjoint
triangles abe and hgj have cross edges ah,bg, so N3-freeness forces ej. For
the second, dcf and hgj have cross edges dh,cg, so it forces fj. Since ef is
adjacent and j meets both e and f, its unique triangle partner gives i=j.

The resulting rows and columns are

    rows:    (a,b,e), (d,c,f), (h,g,i),
    columns: (a,d,h), (b,c,g), (e,f,i).

All nine points are distinct and the six listed triples are actual triangles.
Any prospective extra edge between points in different rows and columns has
the two other grid corners as common neighbors, contradicting lambda1 for
that extra edge. The nine-subset is therefore an induced rook. Its unique
edge partners and ninth triangle completion already proved uniqueness.

This proves a local grid around each square. It supplies neither a universal
Hamming cover nor path-independent transport through three or more directions.

## Square coverage implies N3-free, and the n3 bound

Conversely take an induced N3 in the convenient presentation. Its vertices
0,1,4,3 form an induced square. Its opposite edge partners are2 and5. In any
rook containing the square those partners complete opposite parallel rows
and must be adjacent. But25 is absent in the induced N3. This square cannot
be covered. Thus coverage of every square forbids N3.

The induced N3 has exactly one square: a square must use both cross edges,
and its other edges are01 and34. This gives a map from actual N3 subsets to
uncovered squares. For a fixed square a-b-c-d-a, a preimage must arise from
one of its two pairs of opposite edges, ab/dc or ad/bc. The partners on those
edges are uniquely fixed. There is at most one N3 preimage in each direction,
so at most two in total. Hence n3<=2U. No injective map or equality is claimed;
an uncovered square need not itself have a missing opposite partner edge.

## Target counting and the explicitly conditional literature consequence

There are99*84/2=4158 nonadjacent pairs. Each pair and its two common neighbors
gives an induced square: if those common neighbors were adjacent, their edge
would have both original points as common neighbors. Each square has two
opposite pairs and so the target has2079 squares. Each rook has
binom(3,2)^2=9 squares, and square uniqueness makes their square sets disjoint.
Thus the number of covered squares is9R and U=2079-9R. In particular U=0
is exactly R=231. Combining this identity with the local proof gives the
stated equivalence and n3 inequality.

The existing literature record attributes to Makhnev1988 Theorem2 the
nonexistence of SRG(99,14,1,2) under condition(*): two triangles with at least
two cross edges have exactly three. In the present lambda1 setting, the
matching observation makes(*) precisely N3-freeness. IF that exact theorem,
its conventions and proof are separately authenticated as an applicable
independent premise, the equivalence above excludes R231. IF in addition
the separate R!=230 result is independently accepted, then

    R <=229,  U >=18.

These are conditional consequences, not unconditional approved conclusions
of this packet. Even cited n3>0 alone only gives R<=230; the gap argument is
needed to move to229. No unverified N3>0 premise is smuggled into the local
derivation, and no Hamming-cover theorem is substituted for Makhnev's theorem.

## Evidence boundaries and failed transfers

The preserved October1 scope note states the local grid lemma and cites
Makhnev's condition(*) and Theorem2. Its actual9/243 fixture packet has status
CANDIDATE_SCOPE_LIMITATION and universal_cover UNKNOWN. The9-point rook has
n3=0,U=0,R=1 and checks the parameter-free equivalence; the243 fixture checks
only its explicit grid/syndrome cover. Neither fixture proves the target
N3-free exclusion. The September17 rook regular-set quotient is compatible
with the target spectrum and supplies no rook-count contradiction.

The bounded archive read found C-N3-001 marked DERIVED, with an explicit
limitation that Makhnev's full proof was not independently reconstructed.
C-N3-NORMALIZATION-001 checks a conditional relabeling, not existence of N3.
The official MathNet bibliography was accessible in this source check; a
fresh official PDF request failed. The preserved downloaded PDF identity
ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431
was checked, but its full Russian proof was not newly decoded here. The
citations establish a source route, not a new independent theorem gate.

Primary bibliography: A.A.Makhnev, *Strongly regular graphs with lambda=1*,
Mat.Zametki44:5(1988),667-672; translation Math.Notes44:5,847-850,
[official MathNet record](https://www.mathnet.ru/eng/mzm4220),
[DOI10.1007/BF01158426](https://doi.org/10.1007/BF01158426).
The direct source/assumption comparison is retained separately from the
independently reconstructed local counting argument.

No old claim, source, gate, ledger or publication bytes are modified. A
different reviewer must challenge the square completion, all identifications,
N3 map, two-preimage bound and counting coefficients. Root's proposed scope
question and the earlier local lemma are shared context, not approval by
agreement. No mathematical worker, enumeration or verification run occurred.
