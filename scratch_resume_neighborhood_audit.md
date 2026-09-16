# Independent audit of the preserved one-neighborhood control

The saved control passes an independent audit. This certifies one partial
graph with 206 exposed edges and one completed second-layer neighborhood
`N(15)=7K2`, using the existing zero-based numbering. It establishes neither
a 693-edge graph nor the existence of any completion.

The audit reconstructs all 84 second-layer labels, the 189-edge rooted
skeleton, and the source's twelve second-layer neighbors independently.
It imports and executes no producer code. It checks the complete saved
edge set against that reconstruction plus the five saved edges. The
original producer and both input JSON files remain byte-identical; their
SHA-256 hashes are recorded in the result.

The seven neighborhood edges are

```text
(1,19), (3,47), (25,53), (59,87), (62,90), (73,94), (85,98).
```

The root, its fourteen neighbors, and source 15 have full degree 14. The
remaining degree histogram is 71 vertices of degree 2, two of degree 3,
and ten of degree 4. All 120 pairs among the sixteen full rows have their
exact SRG common-neighbor counts. All 4,851 vertex pairs pass the necessary
partial common-neighbor upper bounds. For other pairs these are only
upper-bound checks; many required common neighbors are still unassigned.

Canonical permutations enumerate 945 perfect matchings of the ten
remaining vertices. Exactly 286 respect the label and same-fiber
restrictions; all 286 pass every partial pair cap. A separate subset
dynamic program independently confirms both counts. This is a finite
audit of one fixed row's matchings, not a search of any lower E0 layer.

Run from the workspace:

```text
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_resume_neighborhood_audit.py
```

Result: `scratch_resume_neighborhood_audit.json`, with status
`INDEPENDENT_ONE_NEIGHBORHOOD_AUDIT_PASS`.

## A necessary simultaneous structure omitted by the one-row control

The following elementary implication applies to any hypothetical
`srg(99,14,1,2)`, at every root and for any value of E0.

Fix root `r`, and label its fourteen neighbors by `0,...,13`, paired into
seven edges. Each of the 84 second-layer vertices has exactly two
root-neighbor labels. Split its second-layer adjacency matrix as `B=P+Q`,
where a `P` edge joins vertices sharing one exact label and a `Q` edge
joins vertices with disjoint exact label sets.

1. **P is a spanning 2-regular graph with 84 edges.** A second-layer
   vertex `x` is adjacent to two root neighbors `a,b`. The unique common
   neighbor of `x,a` must be a second-layer vertex also labeled `a`:
   `r` is not adjacent to `x`, and the mate of `a` cannot be adjacent to
   `x` because the two labels of `x` come from different pairs. Thus
   exactly one second-layer edge of `x` shares label `a`, and exactly one
   shares `b`. These neighbors are distinct because no other vertex has
   both exact labels. Consequently P has degree two everywhere. Equivalently,
   each of the fourteen label classes contributes a matching of six edges.

2. **No second-layer triangle contains a P edge.** Such an edge already
   has its shared first-layer label as its unique common neighbor. A
   second-layer third vertex would supply a prohibited second one. In
   particular P is a disjoint union of cycles of length at least four.

3. **Q is 10-regular, and each of its neighborhoods induces 5K2.** Its
   degree is `12-2=10`. For a Q edge, its unique common neighbor is in
   the second layer because its endpoint label sets are disjoint. Both
   other triangle edges must also belong to Q by the preceding point.
   Hence every Q edge belongs to exactly one Q triangle, giving five
   edge-disjoint triangles at each vertex. No additional adjacency
   between Q neighbors is possible, because it would give an edge two
   common neighbors. Thus Q has 420 edges and exactly 140 triangles.

These statements impose a simultaneous requirement on all 84 rows: one
global 2-factor P and one global collection of 140 Q triangles. Each
vertex belongs to five of the Q triangles, two triangles cannot share
an edge, and the pairwise common-neighbor constraints still apply across
all of them. E0=0 additionally forbids every edge within a support fiber.

The audited witness exposes only two P edges and fifteen Q edges; the
latter form exactly five Q triangles through source 15. It therefore
meets the entire triangle requirement at this single source, while the
other vertices' triangle requirements and shared edge assignments remain
open. The matching count 286 measures possible local triangle choices;
it gives no compatibility count for the 84 neighborhoods. Applying root
symmetries to this witness proves corresponding local controls exist,
but does not select compatible controls simultaneously.

This identifies a precise missing constraint for a potential uniform
argument. It proves no positive lower bound on E0, excludes no macro,
and does not alter any established coverage inventory.
