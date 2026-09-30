# Conditional identity-cross completion and a triangle partition

This is an independent review of the root's proposed completion consequence
and of the separate identity-P mixed-cap lemma. It assumes a completed
SRG(99,14,1,2) containing the specified triangle-root core, whose three cross
matchings are identity. The three internal matchings are arbitrary. This
identity-cross premise is a restriction; no automorphism of the completed
graph is assumed.

Write the inner vertices as (g,a), with g in {0,1,2} and a in {0,...,11}.
Let C be their36×36 adjacency and F the36×60 outside incidence. The exact
target Gram is G=12I-C-C²+2J-B, where B has three diagonal J12 blocks.
For distinct fibres at the same coordinate, C has entry1, C² has entry1
(the third coordinate-triangle vertex), and B has entry0. Thus the Gram
entry is0. Nonnegativity of the integer binary products forces each column
to select at most one vertex of each coordinate triangle.

At a fixed inner row (g,a), its closed core neighborhood consists of its
three-vertex coordinate triangle and the additional vertex (g,M_g(a)). A
column therefore contributes at most2. This independently proves the
producer's (I+C)F≤2 lemma for arbitrary internal matchings, without requiring
connectedness. It is a mixed pair-cap statement, not the residual mixed
equality or a completion theorem. The finite controls below do not replace
this universal argument.

In a target completion, every outside vertex has two neighbors in each fibre
and hence six distinct selected coordinates. A selected pair in one fibre
cannot be a matching pair: that pair has C entry1, C² entry0 and B entry1,
giving Gram entry0. Across fibres, distinct coordinates are nonadjacent
because the cross matchings are identity. Consequently the six core
neighbors of every outside vertex form an independent set.

For every vertex y of a graph with degree14 and adjacent common-neighbor
count1, the induced graph on N(y) is1-regular: every neighbor z has exactly
one neighbor within N(y), namely the unique common neighbor of y and z.
Thus it is seven disjoint edges. For y in the outside60-set, six of its
neighbors are the independent core neighbors and eight are outside. Each
of the six core neighbors must therefore be paired with a different outside
neighbor. The two remaining outside neighbors are paired with each other.
Hence N_D(y) contains exactly one edge, where D is the induced outside graph.
Equivalently y belongs to exactly one triangle of D.

Since every outside vertex belongs to exactly one D-triangle, these triangles
are pairwise vertex-disjoint and cover all60 vertices. There are exactly20.
The root triangle and the12 coordinate triangles partition the remaining39
vertices. Together they give a vertex partition into33 triangles. This does
not say that the graph has only33 triangles (a target has231), that its
triangle partition is unique, or that such a completion exists. Removing
the internal edges of the20 D-triangles leaves a6-regular graph on60 vertices;
no particular quotient or Cartesian-product structure is asserted.

## Exact controls

The checker independently reproduces the four332,640 support controls of
the mixed-cap producer by choosing successive disjoint coordinate pairs for
the three fibres. It checks the raw cubic matrices and Gram entries and
compares the finite histograms. This covers the recorded four examples only.

Separately, it enumerates all135,135 perfect matchings on14 labeled points.
Exactly20,160 have no edge within the designated six core-neighbor points.
Every one has exactly one edge inside the other eight points. A matching
with a core-core edge is a countercontrol: it has more than one outside edge,
so the independent-six premise cannot simply be dropped. Invalid matchings
and incorrect outside-edge counts are rejected.

A60-vertex positive control is Q□K3, where Q is a6-regular bipartite graph
on20 vertices. Its degree is8 and its20 triangles partition the vertices.
This checks only the asserted residual triangle property; it supplies no F
and is not an SRG99 candidate. A degree-preserving switch that introduces
triangles into Q makes the residual property fail. Raw matrices and all
matching records are preserved.

## Archive and literature overlap

The pinned archive85e705cc6c2a14d123120c93a847e30aaab1789e, Wave149
`attempts/wave149-terwilliger-triple/derivation.md` §§1–3, already gives the
3+36+60 decomposition, incidence margins, residual degree8 and exact Gram.
Wave133 `attempts/wave133-triangle-holonomy-topology/README.md` identifies
cross-matching holonomy fixed points with coordinate triangles/prisms.
These are overlapping prerequisites, not new discoveries here. Historical
VERIFIED labels are not being promoted by inheritance.

Wave39 `attempts/wave39-simultaneous-bh/README.md`, lines120–134,
already records the local formula that an outside vertex belongs to1+e_y
outside triangles, where e_y counts edges among its selected core neighbors.
Its accompanying32-triangle count assumes the separate prism-free endpoint
described at the start of that file. We do not import that premise or count.
Here the exact identity-cross Gram forces e_y=0, and the independent local
matching proof gives20 outside triangles. This is a related conditional
corollary, with no novelty claim.

A dated narrow text/search audit looked for33-triangle partitions, triangle
spreads and identity holonomy. It did not locate a directly checked primary
source for this precise conditional33-triangle conclusion in the searched
material. A web fetch of the2023 Chicago REU SAT paper was unavailable.
Search-result pointers and failed reads are recorded separately. This is
not a novelty claim or a comprehensive literature audit. The proof above
does not depend on an external citation or on endpoint/prism-free premises.

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_identity_p_triangle_partition.py --out acceleration/results/20260930_independent_review/identity_p_triangle_partition
```
