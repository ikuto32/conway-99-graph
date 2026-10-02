# Independent exact derivation of the per-vertex rooted-six means

Reviewer `/root/checkpoint_audit`, 2026-10-02 UTC. Candidate derivation reviewed:
`/root/structural`'s three frozen global/per-vertex documents. This argument
uses ordered nonadjacent neighbor wedges and marked induced four-cycles; it
does not use the producer's transported neighborhood matching enumeration.
Software controls accompanying this written review cannot by themselves prove
the theorem. This written proof gives the universal counting bijections.

Assume a finite simple srg(n,k,1,2) with n-k-1>0. Every adjacent pair has exactly
one common neighbor and every nonadjacent pair exactly two. Consequently N(u)
induces a perfect matching for each u: each neighbor has exactly one other
neighbor in N(u). In particular k is even. Counting walks of length2 from u to
its nonneighbors gives 2(n-k-1)=k(k-2): each of k neighbors has k-2 neighbors
outside {u} union N(u), and each nonneighbor is reached twice. No vertex or
graph automorphism is used.

For an ordered nonedge(u,v), a(u,v) counts unordered four-subsets inducing the
free-label orbit of rooted mask8024, b(u,v) likewise mask15540. Root labels0,1
stay ordered; edge bit positions are lexicographic unordered pairs. Write T_u
for the number of sixsets inducing a triangular prism and containing u, each
sixset once. The two triangles of a prism are its only triangles. The missing
edge endpoints of either pattern are its unique two degree2 vertices, and
swapping their root order preserves its free-label orbit. The companion
checker enumerates the complete24 free permutations to check this statement.

## First bijection: ordered nonadjacent neighbor wedges

Fix u. Choose an ordered pair(x,w) of distinct nonadjacent neighbors of u.
There are exactly k(k-2) choices: each x has exactly one matched neighbor and
therefore k-2 nonadjacent neighbors inside N(u).

The nonedge(x,w) has common neighbors u and a unique p different from u.
The vertex p lies outside N(u), because a neighbor of u adjacent to both x,w
would have degree2 inside the matching N(u). The edge(p,x) has a unique third
triangle vertex y. The vertex y is distinct from u,w: p is nonadjacent to u,
and x is nonadjacent to w. Further y is nonadjacent to u, because the edge(x,y)
already has common neighbor p and would otherwise have another u. It is
nonadjacent to w, because the edge(p,y) already has common neighbor x and
would otherwise have another w.

The nonedge(w,y) has common neighbors p and a unique other vertex v. This v
differs from all u,x,w,p,y: adjacency to w excludes x, adjacency to y excludes
u, and the other distinctions follow from simplicity and v!=p. The vertex v
is nonadjacent to p (otherwise edge(p,y) would have common neighbors x,v) and
to x (otherwise edge(x,y) would have common neighbors p,v).

All six vertices u,v,p,y,x,w are thus distinct. The induced edge list, in
labels u=0,v=1,p=2,y=3,x=4,w=5, is exactly

```
04,05,13,15,23,24,25,34; possibly also01.
```

Every other pair has been explicitly excluded above or by the selected
nonedge(x,w). Without01 it is mask8024; with01 it is the triangular prism
whose triangles are {u,w,v} and {p,x,y} and cross edges ux,wp,vy. Thus every
ordered wedge produces either an a occurrence at ordered root(u,v) or an
induced prism containing u. No case is discarded.

Conversely, in a rooted8024 occurrence at(u,v), u has precisely two neighbors
inside the sixset: x on its only full triangle's side and w, the common root
neighbor. The triangle is {p,x,y}; w is adjacent there only to p. This uniquely
determines the ordered wedge(x,w) and the three common-neighbor steps. There
can be no outside alternate common/triangle vertex, since the already present
ones exhaust lambda1 and mu2. Hence each a occurrence contributes exactly one
wedge for fixed u.

In a prism containing u, x must be u's cross-edge partner and w must be one
of the other two vertices in u's triangle, if the same prism is to be obtained:
the generated triangle {p,x,y} is disjoint from u and therefore is the prism's
other triangle. Both choices of w give the stated forced construction. These
are exactly two wedges. Selecting a different first neighbor cannot produce
the same sixset because it would require a nonexistent triangle through a
prism cross edge. Thus the map is a bijection with multiplicities1 and2, giving

```
sum_(v nonadjacent u) a(u,v) + 2*T_u = k*(k-2).
```

## Second bijection: marked induced four-cycles

Again fix u. Choose one of its k/2 triangles {u,p,q}. Fix the order p<q merely
to name endpoints, without reducing the graph search. Choose x in
N(p) minus {u,q}; there are k-2 choices. The vertex x is nonadjacent to q,
because edge(p,q) already has common neighbor u, and to u, because edge(u,p)
already has common neighbor q. The nonedge(x,q) has common neighbors p and a
unique y distinct from p. It is outside {u,p,q,x}: x is nonadjacent to u;
simplicity handles x,q and y!=p. The vertex y is nonadjacent to p, because
edge(p,q) would otherwise have common neighbors u,y. It is nonadjacent to u,
because edge(u,q) already has common neighbor p. Therefore p,q,y,x is an
induced four-cycle with no chords.

Extend edge(x,y) to its unique triangle third vertex v. The third vertex is
outside {u,p,q}: neither u, p nor q is adjacent to both x,y. Between two
disjoint triangles, any vertex has at most one neighbor on the other triangle:
two cross neighbors would give two common neighbors to an adjacent pair on
that triangle. Hence the two triangles {u,p,q} and {v,x,y} have exactly cross
edges(p,x),(q,y), and possibly(u,v). All other cross edges are forbidden.
The sixset is mask15540 (free-label orbit) if uv is absent, and a prism if
uv is present. All selected choices produce one of these cases.

Conversely, a rooted15540 occurrence at(u,v) has unique triangles, with u,v
their unmatched cross-edge endpoints. Choosing the triangle containing u and
the uniquely determined matched x at its named p gives exactly its four-cycle.
All common and triangle neighbors used in reconstruction are already exhausted
inside the sixset. The occurrence contributes exactly one choice for fixed u.
A prism containing u likewise has a unique triangle containing u and exactly
one rectangular four-cycle using its opposite edge {p,q}; the remaining cross
edge uv determines the extended triangle. It contributes exactly one choice.
Thus there is a bijection with multiplicity1 in both cases and total
(k/2)(k-2)=n-k-1, giving

```
sum_(v nonadjacent u) b(u,v) + T_u = n-k-1.
```

The checker independently exhausts all128 supergraphs of each required
eight-edge pattern. The lambda<=1 cap allows only the original pattern and
the added root-edge prism; this finite control attempts to falsify the
extra-edge arguments, and is not a substitute for them.

## Global identities and conditional model application

Sum over u; each prism contributes to exactly six values T_u. With T its
unlabelled sixset count, obtain

```
sum_(u,v ordered nonedge) a(u,v) = n*k*(k-2) - 12*T,
sum_(u,v ordered nonedge) b(u,v) = n*(n-k-1) - 6*T.
```

For each u, the two sums satisfy sum a=2 sum b by the parameter relation.
For a target srg(99,14,1,2) conditional on having no induced prism, pervertex
sums are168 and84 over84 nonneighbors, means2 and1. The prism-free premise is
UNKNOWN. Neither these means nor the global identities fix any individual
ordered-pair coordinate, imply symmetry, exclude a graph/profile, or resolve
the target.

In the independently verified root7 necessary model, external aggregate labels
record sums over marked nonedge roots excluding the other primary root. The
excluded root contributes a or b itself; root swapping preserves both patterns.
Thus conditional on prism absence the aggregate partitions for anchor0 (0,2)
and anchor1 (0,1) have sums168-a and84-b. These are four necessary rows, with
the same UNKNOWN premise. All four already saved exact relaxation corners
are screened literally; their survival establishes no graph realization.

The frozen producer documents disclose overlap with pinned archive Wave35.
No novelty, fresh verification of archival claims, external review, target
construction, target-level nonexistence proof or target-wide coverage is asserted.
