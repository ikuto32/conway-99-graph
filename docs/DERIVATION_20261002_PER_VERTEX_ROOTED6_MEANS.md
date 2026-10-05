# Candidate per-vertex coupling of both rooted-six coordinates

Producer `/root/structural`; separate independent derivation/checking pending.
Use the exact rooted mask definitions and induced-prism sixset count from the
two earlier frozen global-mean documents. Let `T_u` count induced triangular
prisms containing vertex `u`, each sixset once. For any finite simple
`srg(n,k,1,2)` with nonedges, the proposed stronger identities are

```
sum_(v nonadjacent u) a(u,v) + 2*T_u = k*(k-2),
sum_(v nonadjacent u) b(u,v) + T_u = n-k-1.
```

No symmetry is assumed. Global summation gives the earlier two identities
because each prism has six vertices. Subtract twice the second equation from
the first and use the SRG parameter relation to obtain `sum a=2*sum b` for
each fixed vertex. In a target graph without prisms, every vertex's 84
nonneighbors therefore have sums `a=168`, `b=84`, means `2`, `1`.

For the first equation, use the neighborhood matching bijection at each
neighbor `w` of `u`. There are `k-2` choices of `p in N(w)` nonadjacent to `u`.
In the matching on labels `N(w) minus {p,p*}` transported through the outside
neighbors of `p`, the label `u` has exactly one partner `v`. There are exactly
`k*(k-2)` such incidences. If `u,v` are nonadjacent, this is exactly one
rooted8024 occurrence at `(u,v)`, as in the earlier derivation. If adjacent,
it is a prism containing `u`. Each such prism contributes exactly twice:
`w` can be either other vertex in the triangle containing `u`, and `p` is
its cross-edge partner. This proves the proposed first identity.

For the second equation, choose any of the `k/2` triangles `{u,p,q}` through
`u`. Put `X=N(p) minus {u,p,q}`, `Y=N(q) minus {u,p,q}`. The two sets are
disjoint, each has `k-2` vertices. For each `x in X`, the nonedge `(x,q)`
has common neighbor `p` and exactly one additional neighbor `y`. It belongs
to `Y`: it cannot be `u`, and being another member of `X` would give the
adjacent pair `(p,q)` a second common neighbor. Conversely the same argument
at `y` makes this a perfect matching between `X,Y`.

Extend every matched edge `(x,y)` to its unique triangle `{x,y,v}`. Its third
vertex is outside `{u,p,q}` and the two triangles are disjoint; other cross
edges are ruled out by lambda1. They have the two cross edges `(p,x),(q,y)`.
If `(u,v)` is an edge, the result is a prism containing `u`, counted once at
its unique triangle through `u`. If `(u,v)` is a nonedge, it is exactly one
rooted15540 occurrence at `(u,v)`, also counted once. The total is
`(k/2)*(k-2)=n-k-1`, proving the second proposed identity.

Archive Wave35 already derives perfect cross-fibre matchings at every
triangle; this is overlap, not a novelty assertion. The useful new binding
is to the current rooted6 coordinates and root7 rerooting aggregates.

For the conditional target root7 model at primary ordered nonedge `(u,v)`,
aggregate variables sum `a`/`b` over external marked nonedge roots. Therefore
the proposed necessary additional rows are, for anchor0 and anchor1 and
coordinates0/1, respectively:

```
sum_(nonadjacent partitions) aggregate(anchor,partition,0) = 168 - a(u,v),
sum_(nonadjacent partitions) aggregate(anchor,partition,1) = 84 - b(u,v).
```

The excluded original other root contributes exactly the current coordinate.
Anchor0's nonadjacent partitions are0,2; anchor1's are0,1. Other partition
cardinalities and local bounds remain as frozen. The rows are conditional
on prism absence, not target-wide exclusions.

Before any new solve, recheck the saved rook9/243 per-root a,b and prism sixset
counts against each fixed-vertex identity. Save every vertex's totals and
deliberately corrupt one pair count or prism incidence to require rejection.
Check only the four already saved exact root7 corner vectors against the
proposed four rows, preserving exact rational residuals. A violating old
relaxation witness is not an excluded profile or graph. Allocate supported
outer60/worker40seconds from under100k raw records and four2766-coordinate
vectors, with20seconds reserve. No new numerical or modular solve is run.
