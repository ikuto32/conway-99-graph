# Candidate obstruction to one literal wave205 third-star extension

The finite experiment reports that the **specific induced 28-vertex `t6_h1`
control** saved by wave205 cannot be extended to a complete star at its common
neighbour `a`, while retaining the prism-free and rank_F3(D)=11 necessary
conditions. This is a CANDIDATE pending independent reconstruction. It is not
an exclusion of all `t=6` controls, the rank11 branch, the endpoint, or a target
SRG. No existing archive conclusion is silently changed.

The original control remains a valid two-center local control. Its two full
stars are those of nonadjacent vertices `x,y`, with common neighbours `a,b`.
The new experiment tests a constraint that archive wave205 explicitly left
unresolved: consistency with a third complete graph star. The hostile
three-projector examples in that archive have different, relaxed point-graph
conditions and do not already perform this test.

## Why the finite universe covers every such third-star extension

All 28 old vertices and all their induced edges are fixed. The old neighbours
of `a` are exactly `x,alpha,y,gamma`, in its two triangles
`{a,x,alpha}` and `{a,y,gamma}`. Every old vertex is in the closed star of `x`
or `y`, whose degrees are already14. Thus the other ten neighbours of `a`
must be new vertices. Since lambda=1, a neighbourhood induces seven disjoint
edges. Consequently these ten vertices form five adjacent pairs, with no
edges between pairs and no further edges to the four old neighbours of `a`.

Every new neighbour `p` of `a` is nonadjacent to `x,y`. It already shares
neighbour `a` with both centers, so mu=2 forces exactly one additional
neighbour in each of their old neighbourhoods. The old common neighbour `b`
is unavailable: `a,b` already have their two common neighbours `x,y`.
The old vertices `alpha,gamma` are unavailable because their partners inside
the neighbourhood of `a` are already `x,y`.

For an old x-exclusive vertex `r` not adjacent to `a`, its remaining required
common neighbours with `a` are determined exactly by
`2 - |N_old(a) intersect N_old(r)|`. There are ten deficits equal to1 and one
equal to0; the latter is `x20`. The y-side likewise excludes `y20`. Therefore
the required attachment pools are exactly

```
X = beta, x21, x30, x31, x40, x41, x50, x51, x60, x61
Y = delta,y21, y30, y31, y40, y41, y50, y51, y60, y61.
```

Every pool vertex must be used exactly once. A new triangle `{a,p,q}` hence
uses an unordered pair from X, an unordered pair from Y, and one of two
matchings between those pairs. Naming the new vertices by their X endpoints
is only a relabelling of newly introduced vertices, not an automorphism
assumption. There are exactly `C(10,2)^2 * 2 = 4,050` candidates. All old-to-new
edges are determined by these attachments: the old vertices exhaust the
two-center ball, and each new vertex has precisely its prescribed one X,
one Y and `a` as neighbours in that ball.

## The exact modular extension test

Let G be the 14-by-14 ternary Gram of the two old stars, computed literally
as triangle-incidence transpose times local adjacency times incidence. Its
rank is11. An invertible principal 11-by-11 block M, its index set I and its
inverse are saved with the raw graph.

For any proposed new triangle, compute its old-to-new Gram column c from
the literal integer edges. Its coordinate vector relative to the selected
old columns must be `u=M^-1 c[I]`. A global rank11 Gram necessarily satisfies

```
G[:,I] u = c,                u^T M u = 0.
```

The first condition is the image condition; the second is the forced zero
triangle diagonal. They are ordinary symmetric-block rank conditions over
F3, with no arbitrary projector replacement. Two new a-triangles meet at a,
and the matching property of N(a) prevents edges between their other
vertices. Their integer incidence-adjacency cross sum is4, so their ternary
Gram entry must be1. Their coordinates therefore require `u^T M v=1`.

The old rank already fills the proposed global dimension, so every actual
extension must pass these tests. The experiment does not require the
unproved converse that these tests complete a graph.

## Complete candidate computation

Frozen executed source:
`acceleration/theory_20261001_wave205_third_star_v2.py`
(SHA256 `e8a63abb4bdd80fd6b2f0971e4569a874ad6f32fd1725ebd8a0a44c7072eb539`).
Matching spec SHA256:
`7b8e7abaf48d5659cd6bd7a21b8d6d41d1320edff45db94e5f6152bb59b8f527`.
V1 source/spec are preserved **unexecuted**. Before the sole run, v2 added a
complete traversal log and a separate node ceiling; no mathematical
predicate changed.

All 4,050 candidates were checked, with first-rejection counts:

| Stage | Candidates |
|---|---:|
| Integer local common-neighbour cap | 243 |
| Three-cross-edge prism cap on actual triangles | 445 |
| Old Gram image condition | 1,858 |
| Forced zero Gram norm | 1,208 |
| Retained | 296 |

The next test covers the ten X and ten Y positions by five retained options,
requiring all pairwise Gram entries1. Complete deterministic traversal chose
the first uncovered X vertex at each step. There are16 retained options
containing `beta`; none admits a disjoint compatible option covering the
next required X vertex. The traversal contains17 nodes including its root,
all with completed exhaustion records, and no complete leaf. Thus there was
no witness requiring the later 38-vertex full-graph checker. No timeout or
node limit was reached.

Output directory: `acceleration/results/20261001_wave205_third_star_v2/`.

- `literal_control.json`: all28 labels/adjacency bit rows, all14 old triangles,
  exact G, eligible attachments/deficits, principal block and inverse.
- `triangle_candidates.json`: every candidate ID, pairs, matching orientation,
  first failure, and the modular column/coordinates when reached.
- `exact_cover_traversal.jsonl`: every node entry, chosen IDs, parent/edge IDs
  and completed exit; together with the full option list and deterministic
  rule it permits an independent complete-child replay.
- `controls.json`:729 exhaustive small symmetric extension comparisons with
  direct ranks; the genuine243 generic SRG check; three corruptions rejected.
  The243 graph is explicitly not a prism-free/rank11 positive.
- `summary.json`: SHA256
  `39883336a9d6ce388589c08abdba9566a8a9b2b44903c440609f62b19f9b2322`.

Total producer time was0.594 seconds, below the declared120-second allocation.
No archive producer was imported, and no native/SAT solver was called.

The candidate conclusion depends on preserving **this exact induced local
graph**, and is stronger than testing two unrelated modular star embeddings.
Other integer realizations of its cross Gram, other `t=6` controls, or other
rank11 endpoint configurations have not been tested or excluded.
