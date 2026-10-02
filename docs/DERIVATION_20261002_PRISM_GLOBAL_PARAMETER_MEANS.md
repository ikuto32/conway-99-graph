# Candidate global mean identities for both rooted-six coordinates

Producer `/root/structural`; independent alternate derivation and raw checking
are required. No novelty claim. Preserve the earlier mask8024 derivation and
calibration unchanged. Assume a finite simple `srg(n,k,1,2)` with nonedges.
Let `T` count unlabelled induced triangular-prism six-subsets once, `a(u,v)`
count rooted mask8024 occurrences, and `b(u,v)` count rooted mask15540
occurrences, with ordered nonedge roots and unordered four-subsets.

The two candidate identities are

```
sum_(ordered nonedges) a(u,v) = n*k*(k-2) - 12*T,
sum_(ordered nonedges) b(u,v) = n*(n-k-1) - 6*T.
```

The first identity has a separate complete local-matching derivation in
`DERIVATION_20261002_ALMOST_PRISM_GLOBAL_MEAN.md`. The second is derived here.
For the target with `T=0`, the 8,316 ordered nonedges have exactly means
`a=2`, `b=1`. These are population means, not individual coordinate values.
No automorphism, graph realization, unconditional prism absence or local
profile exclusion is implied.

Each nonadjacent pair has exactly two common neighbors. They are nonadjacent,
since otherwise their adjacent pair would have two common neighbors. Thus it
lies as one opposite pair of a unique induced four-cycle. Every four-cycle
has two opposite pairs, so the unlabelled four-cycle population is exactly
`C4=n*(n-k-1)/4`.

For each four-cycle, choose either of its two pairs of opposite edges. Extend
each chosen edge to its unique triangle. The two third vertices are outside
the four-cycle: chords are absent. They are distinct, since a common third
vertex would be adjacent to all four cycle vertices, contradicting lambda1
on any edge from that vertex. The resulting two triangles are therefore
disjoint. Between two disjoint triangles, every vertex has at most one cross
neighbor, as two cross neighbors on a triangle would give two common neighbors
to an adjacent pair. Their cross edges form a matching. The original cycle
provides two cross edges, and the only possible additional one joins the
third vertices.

Let `X2` count disjoint unordered triangle pairs with exactly two cross edges.
Each contributes exactly one four-cycle/opposite-edge extension choice. A
three-cross-edge pair induces a triangular prism; it contributes exactly
three such choices, one for each of its three rectangular four-cycles. The
two triangles of a prism are unique. Hence

```
X2 + 3*T = 2*C4 = n*(n-k-1)/2.
```

A two-cross-edge pair is precisely a prism with one matching edge removed.
Its missing edge endpoints are the unique two degree2 vertices; rooting them
and ordering the roots gives the free-label orbit of mask15540. Conversely,
every such rooted occurrence contains this unique two-triangle pair. Therefore
`sum_(unordered nonedges) b = X2`, and doubling gives the second identity.
Together with `2*(n-k-1)=k*(k-2)`, these also give `sum a = 2*sum b`.

This is substantial overlap with pinned archive
`YesterdaysLemon/conway-99-research` commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`, Wave35 `n3+3P=4158`.
The new contribution sought is a precise binding of the current two rooted
coordinates to global counts and a reusable coupled population constraint.
The archive's historical status is not treated as fresh verification.

Before larger counting, use rook9: enumerate all84six-subsets for prisms,
all1260 ordered-root four-subsets for each mask, and every induced four-cycle
with its two opposite-edge extension choices. Require exact agreement with
disjoint triangle-pair counting, and positive raw8024/raw15540 canonical-mask
controls plus deliberately changed global count rejection. The six-vertex
raw patterns are shape controls, not valid SRG fixtures.

Then use the already pinned243graph; revalidate the exact SRG identity, count
all unordered triangle pairs by cross matching size, save any two-cross-edge
sixset/root witnesses, and enumerate unique four-cycles via opposite pairs.
Save per-unordered-root b counts and every triangle pair/four-cycle witness.
No `choose(243,6)` enumeration. Supported outer180/worker165 allocation with15
seconds orderly reserve is justified by891triangle sets (~400k pairs) and
26,730 opposite-root pairs. This producer calibration is not independent
approval of the general theorem or fixture evidence.
