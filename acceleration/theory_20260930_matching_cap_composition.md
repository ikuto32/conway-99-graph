# Candidate: simultaneous residual matching caps are redundant

Status: **CANDIDATE**, newly derived by `/root/state_literature_audit` and
awaiting a separate written review. Computational controls and sampled checks
do not themselves establish this general theorem.

## Exact statement

For every finite simple undirected graph `G`, every independent vertex set `R`
of `G`, and every matching `M` whose endpoints lie in `R`, suppose `G` and every
single-edge extension `G+e` for `e ∈ M` satisfy

```
|N(x) ∩ N(y)| ≤ 2 - adjacency(x,y)  for every distinct x,y.
```

Then `G+M` satisfies these same inequalities for every distinct pair.
This concerns pairwise common-neighbor upper bounds only. It asserts neither
degree completion nor exact SRG equations nor extendibility to a full graph.

## Proof offered for independent review

Let `T ⊆ R` be the endpoints of `M`; write `m(x)` for the unique mate of each
`x ∈ T`. New neighborhoods are

```
N'(x) = N(x) ∪ {m(x)}   if x ∈ T,
N'(x) = N(x)           otherwise.
```

The unions are disjoint because `R` is independent in `G`.

If neither endpoint of a tested pair is in `T`, neither its neighborhoods nor
its adjacency changes, so its cap follows from `G`.

If exactly one endpoint, say `x`, is in `T`, the two tested rows and their mutual
adjacency are exactly those in the already admissible single-edge extension
`G + {x,m(x)}`. Other new edges change neither row. Its cap follows from that
single-edge assumption.

If both distinct endpoints `x,y` lie in `T`, their common-neighbor count is
unchanged. Indeed `m(x) ∉ N(y)` and `m(y) ∉ N(x)` because each of those vertices
belongs to the independent set `R`; also `m(x) ≠ m(y)` because a matching's mate
map is injective. Thus all three possible additional intersection terms are
zero. If `x,y` are not mates, their adjacency is unchanged too. If they are
mates, their new adjacency and unchanged common-neighbor count agree with the
single-edge extension for their matching edge. In both subcases the cap holds.

These cases exhaust all distinct tested pairs. No symmetry assumption or
floating-point calculation is used.

## Application to the existing neighborhood filter

For a completed center star in the stored partial graph, its known induced
neighborhood edges form a matching (otherwise an adjacent center-neighbor pair
already has at least two common neighbors). Remove every endpoint of every
known neighborhood edge. The residual vertices have no known edge to any
vertex in the neighborhood, hence in particular form an independent set `R`.

The existing individually permitted edge graph uses edges only between these
residual vertices and permits an edge precisely when its single-edge addition
preserves every pair cap affected by that addition. The base star's other caps
already hold. Consequently **every** perfect matching in that graph preserves
all pair caps when added in full, if the theorem is correct. Testing simultaneous
pair caps cannot reject an additional star or an additional matching.

This does not say that the selected local matchings for different center stars
are mutually consistent. Coupling different stars, requiring other vertices'
remaining degree/inner quotas, or completing the full SRG may still impose
additional constraints.

The prior independently checked filter premise is
`C-PARTIAL-K-EIGHT-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER` revision 1, with
audit SHA256 `4fcd5fd7f02cd5362bda1f8f0a1c8e4669ce036bde56a04dcd1b6a3391b262f4`.
Its complete checking path reconstructed forced and residual vertices and
individually permitted edges for all 2,290,122 original stars. The new
deterministic sample is a falsification exercise, not a replacement for the
general proof or those full-domain premises.

## Necessary hypotheses and controls

Independence cannot be dropped. On vertices `0..4`, use base edges
`03,04,12,24` and new matching `01,23`. The base and either single-edge
extension satisfy the caps. Together, vertices `0,2` have three common
neighbors `1,3,4` while remaining nonadjacent. The matching endpoints were not
an independent set in the base graph.

The matching hypothesis cannot be dropped either. Start with a star centered
at `0` and at least three leaves. Each edge `12` or `13` is individually
permitted, but adding both gives adjacent vertices `0,1` two common neighbors.

The saved experiment tests these corrupt hypotheses, a valid windmill fixture,
and the theorem on every five-vertex graph and every independent endpoint set
and perfect matching on that set. It also adds the saved witness for the first
256 retained stars in original-ID order at each of 84 centers and directly
checks all 4,851 full-99 unordered pair caps. The sample universe has 21,504
stars; a resource cap may leave part pending, which must be reported explicitly.
