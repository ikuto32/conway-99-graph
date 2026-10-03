# Candidate global coupling of rooted-six counts and induced prisms

Producer derivation, pending independent alternate derivation/checking. No
novelty is claimed. The target remains unresolved. Assume a finite simple
`srg(n,k,1,2)` with nonedges (`n-k-1>0`). Let `T` count unlabelled vertex
six-subsets inducing the triangular prism, each subset once. For an ordered
nonedge `(u,v)`, let `a(u,v)` count unordered four-subsets of the other vertices
whose induced rooted-six flag is the free-label orbit of mask 8024. Edge bits
are lexicographic unordered pairs with bit zero `(0,1)`, and roots `0,1` stay
ordered. This is exactly the current root6 parameter `a` at raw index 552.

The candidate exact identity is

```
sum_(u,v ordered nonedge) a(u,v) = n*k*(k-2) - 12*T.
```

For the target, the ordered-nonedge population is `99*84=8316`. Under `T=0`,
the sum is 16,632 and the average is exactly 2. This is a global distribution
constraint: it does not force `a(u,v)=2` at every pair, imply any automorphism,
or exclude a surviving local profile by itself.

## Overlap search before calculation

The pinned archive `YesterdaysLemon/conway-99-research`, commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`, has the Wave35 relation
`n3+3P=4158`, with `P` its induced-prism count, in `README.md` under
“Wave35: first general upper-bound checkpoint” and later in `STRUCTURE.md`.
This is substantial overlap. With that historical normalization, the target
identity above reads `sum a = 4*n3`. The archive's historical status is not
promoted by this observation; a fresh local/global coordinate binding and
the complete derivation below still need independent checking. No change is
made to the pinned archive or historical IDs.

## Local incidence bijection

For any vertex `w`, its neighborhood `L=N(w)` is a perfect matching on `k`
vertices: a neighbor has exactly one neighbor within `L` because adjacent
vertices have exactly one common neighbor. Write `p*` for the partner of `p`.
Every vertex outside `{w} union L` has exactly two neighbors in `L`; those
neighbors are nonadjacent, since an adjacent pair's unique common neighbor is
already `w`. Conversely, every nonadjacent unordered pair `{p,u}` in `L` has
exactly one common neighbor other than `w`, denoted `x_(p,u)`, and it lies
outside `{w} union L`. Thus outside vertices and nonmatched pairs of `L` are
in bijection. No target symmetry is used.

Fix `p in L`. Its neighborhood contains the triangle partner pair `{w,p*}`
and its `k-2` outside neighbors `x_(p,u)`, where `u` runs over
`L minus {p,p*}`. The neighborhood matching at `p` pairs these outside neighbors,
giving a perfect matching `M_(w,p)` on the `k-2` labels `u`. Across all `w,p`,
there are exactly `n*k*(k-2)/2` such labelled matching pairs.

For a matched pair `{u,v}` of `M_(w,p)`, there are two cases.

* If `u,v` form an original matching edge of `L`, the triangles
  `{w,u,v}` and `{p,x_(p,u),x_(p,v)}` have exactly the three cross edges
  `w-p`, `u-x_(p,u)`, `v-x_(p,v)`. Other cross edges are excluded by the
  outside vertex's exact two neighbors in `L`. The six-set is an induced
  triangular prism. Conversely, each induced prism contributes exactly six
  such local matching pairs: choose any of its six vertices as `w`, and `p`
  is its opposite cross-edge neighbor. Its other two vertices on the first
  triangle are the original local matched pair. Therefore this case counts
  exactly `6*T`.

* If `u,v` are nonadjacent in `L`, the six-set
  `{u,v,w,p,x_(p,u),x_(p,v)}` is an induced prism with a triangle-edge removed,
  rooted at the missing edge `(u,v)`. Its only common root neighbor inside
  the six-set is `w`, and `p` is the unique neighbor of `w` on the other triangle.
  Thus every such rooted almost-prism occurrence gives exactly one `w,p`
  local matching pair. This case counts
  `sum_(unordered nonedge {u,v}) a(u,v)`, where swapping roots gives the same
  value but is not yet counted a second time.

For the second case, map the local labels to the raw representative as
`u=0,v=1,w=5,p=2,x_(p,u)=4,x_(p,v)=3`. Its exact edge list is
`04,05,13,15,23,24,25,34`, which encodes mask 8024. Adding the missing edge
`01` produces the triangular prism; that edge is inside one of its triangles.
All extra edges are excluded by the local matching and exact outside-neighbor
bijection. The other root6 coordinate, mask15540, removes a prism matching edge
and is not the statistic counted here.

Partition the local labelled matching-pair population:

```
sum_(unordered nonedge {u,v}) a(u,v) + 6*T = n*k*(k-2)/2.
```

Double the unordered root-pair count to obtain the stated ordered identity.
The SRG parameter identity `2*(n-k-1)=k*(k-2)` then gives
`average a = 2 - 12*T/(n*(n-k-1))`. In particular, `T=0` forces mean2 and
nonnegativity gives the familiar target bound `T<=1386`; the archive overlap
above prevents presenting that bound as novel progress.

## Frozen calibration protocol

Before larger counting, calibrate the exact graph validator and two prism
enumerations on rook9 `srg(9,4,1,2)`. Its induced-prism population can be checked
by all `binomial(9,6)=84` six-subsets; the proposed triangle-pair routine must
match it. Direct canonical-mask8024 enumeration at every ordered nonedge checks
the almost-prism count independently of the local embedding formula. Require
deliberate adjacency/count corruption rejection.

Then use the raw independently validated 243-vertex fixture at
`acceleration/results/20260930_srg243_residual_fixture/adjacency243.json`,
SHA256 `5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3`.
Recheck its full exact SRG identity before counting. Count prisms by disjoint
triangle pairs with one-to-one cross matching, and almost-prisms through the
explicit common-neighbor embedding path above. Preserve per-root raw counts,
triangle sets and prism six-set witnesses, graph hashes, commands and versions.
Never enumerate all `binomial(243,6)` subsets. Allocate a supported outer180 /
worker165 seconds from about 400,000 triangle pairs and 1,000,000 local checks,
with orderly shutdown reserve. These are producer calibrations and finite
controls; the theorem requires independent alternate derivation and artifact
checking before promotion. No normalization/modular solve is duplicated.
