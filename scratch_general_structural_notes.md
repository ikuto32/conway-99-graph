# Rigorous structural deductions for the rooted 84-vertex model

Write an outer label as one symbol from each of two distinct matched groups,
and let `B` be the outer adjacency matrix.  The equation `BP = PA0` says that
an outer vertex has one neighbour containing either symbol of each group in
its own support, and two neighbours containing each symbol of every other
group.  Summing these equations gives outer degree 12.

## Coordinate matchings and group 2-factors

For every inner symbol `s`, the 12 outer labels containing `s` induce a
perfect matching.  Hence the 14 matchings contain 84 distinct shared-symbol
edges.  For a matched group `g`, let `S_g` be the 24 labels using that group.
Every vertex of `S_g` has exactly two neighbours in `S_g`: one using its same
symbol and one using the mate.  Thus `B[S_g]` is a 2-factor whose edges
alternate between these two kinds.  Every cycle consequently has length
divisible by four.  Every vertex outside `S_g` has exactly four neighbours in
`S_g`.

The other 420 edges have disjoint exact labels.  Each lies in a unique
all-outer triangle, so they split into 140 edge-disjoint triangles and every
outer vertex lies in five of them.  The three labels of such a triangle are
pairwise exact-symbol-disjoint.

## Same-support fibres

For a vertex `x`, let `a,s,d` count neighbours with the same support, with
one common support group, and with disjoint supports.  Then

```
2a + s = 4,       a + s + d = 12,       d = 8 + a.
```

Inside a four-vertex fibre, regard the four labels as a square.  Its four
side edges share one exact symbol; its two diagonals join complementary
labels.  The BP target-one equations imply a sharper rule: a diagonal edge
isolates both its endpoints inside the fibre.  Otherwise the induced graph
is an arbitrary subgraph of the square `C4`.  Up to the dihedral action this
gives exactly eight types (six subgraphs of `C4`, one diagonal, or both
diagonals).  In particular the former `a2_mixed` branch is locally
impossible, without invoking any common-neighbour clauses.

Let `C` and `Q` be the total numbers of side and diagonal fibre edges.  Then

```
same-support edges                 = C + Q,
one-support-group edges            = 168 - 2C - 2Q,
disjoint-support edges             = 336 + C + Q,
exact-disjoint one-group edges     = 84 - C - 2Q,
```

so in particular `C + 2Q <= 84`.

An all-outer triangle's support multigraph has one of five forms: `3K2`,
`P3+K2`, `P4`, `C3`, or a doubled support edge plus a disjoint edge.  The last
type occurs exactly `Q` times, once for every diagonal fibre edge.

## Exact-CNF and portfolio audit

The one-way product helpers in `scratch_general_exact_sat.py` are logically
sound.  BP fixes every outer degree at 12 and therefore fixes

```
sum_{u<v} (edge(u,v) + common_outer(u,v))
  = 504 + 84*C(12,2) = 6048.
```

The sum of all per-pair upper-bound targets is also
`924*1 + 2562*2 = 6048`.  Consequently all upper bounds must be equalities in
any satisfying edge assignment, even though helper variables only encode
`edge(u,w) & edge(v,w) -> helper`.  The encoding is exact but propagation is
weaker than a full equivalence/equality encoding.

The normalization in `scratch_general_triangle_portfolio.py` is exhaustive:
a disjoint-support neighbour always exists (`d=8+a`), and its unique outer
common neighbour is exact-symbol-disjoint from both endpoints.  The residual
group enumeration covers all 42 possible labels.  Nine of the 26 orbit
branches, however, contradict either a fixed negative edge or a BP
target-one quota immediately.  The bounded audit reduces the live portfolio
to 17 branches before loading a solver.

Finally, the forced spectrum of `B` is
`12^1, 3^40, 0^7, (-2)^6, (-4)^30`.  The seven-dimensional zero eigenspace
contains the differences between the two symbol-incidence columns of each
matched group; this is useful as an independent verifier invariant.
