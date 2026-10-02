# Independent exact lambda-phase equivalence and root mean derivation

Verifier checkpoint_audit, reviewing root's proposed phase claim,2026-10-02UTC.
This written proof is universal. Finite graph/shape controls alone do not prove
it. No automorphism, symmetry normalization, approximate score or SRG existence
assumption is used. Assume99points and231distinct triples forming a linear
3uniform hypergraph, every point in exactly7triples. Its point graph G puts an
edge between two points iff they share a triple. Linearity means every graph
edge belongs to exactly one given triple. Each point has14distinct neighbors,
and there are693edges. Every given triple is a graph triangle.

Let B be the231given unordered triples, let Delta be ALL unordered graph
triangles, and X=Delta minus B. For each graph edge e={u,v}, every common
neighbor w determines exactly one graph triangle {u,v,w}, and conversely.
Exactly one is its given line. Therefore

```
m_e := CN(u,v)-1 = number of extra triangles in X containing e >=0,
E_lambda = sum_(e graph edge) m_e^2.
```

E_lambda is an exact sum of nonnegative integer squares. It is zero iff all
m_e are zero, iff X is empty: every extra triangle would contribute one to
each of its three edges. Thus E_lambda0 is equivalent to having exactly the
231given triangles, with no extras. This equivalence actually holds for every
linear3uniform point graph, even without regularity; its mean consequence below
requires the regular target-size assumptions.

Summing edge incidences gives sum_e m_e=3|X|. Thus E_lambda>=3|X|, with equality
iff every m_e is0or1. In the saved graph's independently checked adjacent
histogram630edges haveCN1 and63haveCN2. Consequently sum_e m_e=63 and |X|=21.
The claimed count must still be checked by independently enumerating all
triangles and subtracting B, as done by the companion checker.

For a fixed vertex u, write t_u=|{x in X:u in x}|. Every triangle containing u
uses exactly two incident edges, so sum_(v neighbor u)(CN(u,v)-1)=2t_u. In a
kregular graph the length2walks from u ending at a different vertex number
k(k-1). Divide them into endpoints adjacent and nonadjacent to u:

```
sum_(v nonadjacent u) CN(u,v)
 = k(k-1) - sum_(v adjacent u) CN(u,v)
 = k(k-1) - (k+2t_u)
 = k(k-2)-2t_u.
```

Here k14 and there are99-14-1=84nonneighbors, so this sum is168-2t_u and the
exact mean is2-t_u/42. In particular, global E_lambda0 forces every t_u0 and
every nonadjacent mean2. A mean2 does not imply every nonadjacent common-neighbor
count2. Global E_mu must independently vanish for that stronger pair condition.

A root u is clean precisely when t_u0. Equivalently all its incident edges
haveCN1: they each contain their given line and no extra triangle containing u.
Each neighbor then has degree1 inside N(u), because that internal degree is
CN(u,v). Thus N(u) is a perfect matching of7edges on14vertices. This establishes
only the neighborhood matching; it cannot assign every outside vertex degree2
into N(u). The outside cross-edge TOTAL at a clean root is168, but its84
individual contributions can differ from2 while preserving that total. In
particular, a189edge total14+7+168 is not a valid inference of the full target
scaffold distribution or its canonical labels.

The21extra triangles cover at most63vertices, so at least99-63=36roots are
clean. This is a lower bound on a named population, not overall search coverage.
The checker records the actual covered union, every t_u and all99histograms,
and tests separately whether any root is both clean and hasCN2at every one of
its84nonneighbors. These two local conditions are necessary for the proposed
root-scaffold import; no sufficiency for the complete canonical target scaffold,
its outside-pair uniqueness, SAT encoding or graph completion is asserted.

The exact saved graph is already known to be non-SRG. This phase guide and
its finite root census give no target exclusion, construction, existence result,
changed-engine correctness, launch approval, novelty or external review.
