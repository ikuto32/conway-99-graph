# Candidate: nonzero rook deficiency cannot have maximum one

This is a separate source-only written candidate. The earlier R229 paper and
raw record remain unchanged. Root received the outline before freeze. No
mathematical program, source import, graph census or solver ran.

## Exact statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
nine-point rook subsets once. For each actual triangle T set d_T=6-r_T, where
r_T counts those subsets containing T. If R<231, then some triangle has d_T>=2.

Equivalently, a nonempty family of positive deficiencies cannot consist only
of ones. R=231, when all deficiencies vanish, is permitted. This does not
exclude the target or assume a nonconstant codeword.

## Defect graph and square facts

Every edge has its unique triangle partner, and every vertex belongs to seven
actual triangles. Distinct actual triangles meet at most once. Three triangles
cannot meet pairwise at three distinct points, since the shared points would
give an original edge a second triangle partner.

At a point v, join two incident triangles in D_v exactly when no induced rook
contains them both. The four cross pairs of two triangles through v have v
and unique second common neighbors; they fix every proposed nine-point rook.
Hence at most one rook contains that pair, and deg_(D_v)(T)=d_T for each v in T.
Counting six triangles per rook gives D=sum_T d_T=6(231-R).

An induced square is contained in a rook if and only if its two actual edge
triangles at any chosen corner are together in a rook. That corner's opposite
point is their fixed second common neighbor. Each square belongs to at most
one rook; the four edge partners and a further unique edge partner fix its
nine points. There are 4158 target nonedges, each with two common neighbors,
so there are 2079 induced squares. Every rook contains nine of them. Thus
the number U of uncovered squares is 2079-9R=3D/2.

## A cubic graph without a point-multiplicity assumption

Assume every positive deficiency is one and D>0. Let F have those D positive
triangles as nodes, with an edge whenever they meet in a point and form its
defect pair. At each point the positive nodes of D_v form a matching: they
have degree one and all other nodes have degree zero.

The graph F is simple by triangle linearity. Each selected triangle has
exactly one defect partner at each of its three points, and the three partners
are distinct by the same linearity. Thus F is cubic.

At any node, two F edges meet their actual triangle at different points.
An F triangle would therefore give three actual triangles meeting at three
different points, which is impossible. Hence F is triangle-free. This does
not assert that the positive support has point multiplicity two: a point can
support multiple distinct defect edges, and additional target edges are allowed.

## Every four-cycle is geometrically faithful

For a four-cycle T1,T2,T3,T4 in F, let v12,v23,v34,v41 be its intersection points.
Adjacent points are distinct because the two F edges at their common triangle
come from different actual points. Opposite points cannot coincide either.
For example, if v12=v34=v, all four triangles contain v. Linearity then forces
T2 and T3 to intersect at v, contradicting v23 different from v12.

The four distinct intersection points form a target square: each consecutive
pair lies in its selected triangle. A diagonal cannot be an edge, since its
endpoints already have the two other square corners as common neighbors and
lambda=1. At each corner the adjacent triangles are its defect pair, so the
square is uncovered.

Conversely, the four actual edge triangles of an uncovered target square
are distinct, positive and joined by their corner defect pairs. They form
a four-cycle of F. The two constructions are inverse because distinct triangle
pairs have their unique intersection point. In particular, no two cycles
collapse to one square, and possible extra support edges do not spoil the map.
Therefore C4(F)=U=3D/2.

## Cubic equality is a rook contradiction

In any simple cubic triangle-free graph, each node has three neighbor pairs.
Each pair has the chosen node and at most two further common neighbors, so
each node belongs to at most six four-cycles. Counting their four nodes gives
C4(F)<=6D/4=3D/2.

The forced equality holds at every node. For a node v with neighbors x,y,z,
each pair among x,y,z has three common neighbors; their degree-three neighbor
sets are identical, say {v,p,q}. All six nodes have their full degree inside
this K3,3, so every component is K3,3.

The nine F edges of a K3,3 component represent nine distinct actual points.
Adjacent F edges are already distinct. If two disjoint edges (a,x),(b,y)
represented the same point v, the cross edge (a,y) would also be the unique
intersection at v. It would give triangle a two defect partners at that point,
contrary to the local matching. Thus no disjoint edges coincide.

The six actual triangles are exactly the three rows and three columns on those
nine points. They induce a rook: an extra edge in different rows and columns
already has two grid common neighbors, violating lambda=1. Each F edge is
therefore a triangle pair together in an actual rook, contrary to its definition
as a defect pair. This contradiction proves the statement.

## Boundaries, overlap and usefulness

The zero-deficiency case has an empty F and is not contradicted. An arbitrary
even selection of triangles need not have point multiplicity two, and the proof
does not impose that assumption. Two rooks joined at a point give a hand boundary
with multiplicity four; their selected pairs are rook-covered and therefore do
not give the required defect graph.

Two abstract K3,3 components meet the cubic square bound sharply. Their line
graphs are rooks, so they fail precisely the required defect condition. A
hexagonal prism is cubic and triangle-free but has six rather than eighteen
four-cycles, confirming that cubic geometry alone is insufficient.

The local square and defect identities overlap the preserved R230, strict-mass
and R229 candidates. The new step is the global cubic graph of defect pairs,
whose edges can share actual points away from a node, followed by the faithful
cycle map that handles those identifications. No archived census is imported.

Together with a separately established strict bound d_T<=230-R for R<231,
this would imply R<=228 whenever R<231. That is a conditional combination,
not an approval transfer and not an R231 exclusion. A different reviewer must
challenge the local matching, the cycle map and the nine-point distinctness.
