# Independent rooted-five rigidity derivation and audit v2

For a hypothetical target graph and a fixed actual ordered root `(a,b)`, let
`x_H` count unordered subsets of the other 97 vertices inducing rooted class
`H`. The roots are fixed pointwise. Every induced class through order five obeys
the local adjacent/nonadjacent common-neighbor caps one/two. The independent
checker exhausts every labelled mask (at most 1,024), partitions only free-label
permutation orbits, and matches every saved variable. This is an exhaustive
necessary basis, not a claim that every locally admissible flag is realizable.

For each order h, `sum_H x_H = binomial(97,h-2)`. For each lower class H of order
h=2,3,4, count one-vertex extensions in three ways. An instance has `99-h`
available new vertices. For a vertex-mark orbit O its outside-neighbor count
sums `14-deg_H(u)` over marked vertices. For a pair-mark orbit O its outside
common-neighbor count sums `2-A_H(u,v)-common_H(u,v)` over marked pairs. These are
exact integer identities for every actual target root, by degree14/lambda1/mu2.

The same pairs `(lower instance, new vertex)` are counted from each larger
rooted class K by deleting only a free vertex. Its contribution is one, the
number of marked vertices adjacent to the deleted vertex, or the number of
marked pairs fully adjacent to it. Any two root-preserving isomorphisms from
the remainder to H differ by a root-fixing automorphism of H, preserving each
mark orbit. The independent checker uses DSU group action on marks and tests
every such isomorphism for identical coefficients, rather than importing the
producer's canonical transport. These are automorphisms of small flags used to
define coordinates; no automorphism of the target graph is assumed.

The complete saved systems match all independently reconstructed integer rows:
87 variables / 194 rows for ordered edges, 111 variables / 224 rows for ordered
nonedges. Independent Gaussian elimination modulo the independently checked
prime1009 gives full column rank87/111. A nonzero maximal minor modulo a prime
is a nonzero integer minor, so the rational ranks are exactly87/111. The saved
explicit rational vectors satisfy every reconstructed integer equation exactly;
therefore they are the unique rational solutions. Every coordinate is checked
as a nonnegative integer. Every actual root's count vector must equal that unique
vector, independently of N3, prisms, chosen support or target automorphisms.

The order-five coordinates have populations66/87, each summing to
`binomial(97,3)=147440`. Every mask/value agrees with the archived coordinate basis
and endpoint vectors: `c_edge=2*u`, `c_nonedge=v`. Defining the actual ordered-root
moment by `M=sum_theta c(theta)c(theta)^T`, constancy and exact ordered-root
populations `99*14=1386` and `99*84=8316` give
`M_edge=1386*c_edge*c_edge^T` and `M_nonedge=8316*c_nonedge*c_nonedge^T`.
Every66x66 and87x87 saved endpoint/binding matrix entry is compared exactly.
The full archived order5..8 coefficient-layer derivation is not repeated here;
the moment equality uses the explicitly stated actual-root definition.

The independent known-valid grid construction is checked as srg(9,4,1,2).
All36 actual ordered edges and36 ordered nonedges pass every independently
reconstructed n9/k4 row. A changed forced count and a changed raw coefficient
are rejected. Removing one rook edge fails the independent exact SRG validator
and necessary rows at34 adjacent and38 nonadjacent corrupted-graph roots.
These are complete stated control populations, not sampled checks.

The first v1 run stopped on an endpoint-reader interface error: endpoint matrix
cells are raw integers, while the reader attempted rational-pair unpacking. Its
source/failure/receipts remain unchanged in `rooted5_rigidity01` and
`rooted5_rigidity_supervision01`. Version2 explicitly requires exact integer
cells. Its complete PASS report is in `results/20261002_independent_review/
rooted5_rigidity02/`, with its declared300-second supported invocation in
`rooted5_rigidity_supervision02/`.

No producer or archived discovery module is imported. The shared trusted
components are Python integer/Fraction arithmetic, JSON/SHA-256, OS/runtime,
and the pinned uv environment. This is a conditional universal exact statistic
and a checked endpoint identity, not a graph construction or nonexistence proof.
It adds zero exclusions and no target-wide coverage percentage. Pech2021 is
established literature context; novelty and a complete literature theorem audit
are not asserted by this finite derivation.
