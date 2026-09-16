# Exact common-neighbor compatibility between completed stars

The first guided pilot passes independently checked reciprocal-edge arc consistency,
but fails the stronger exact pair-count condition. This separates the two
conditions by an explicit countercontrol. The new failure has a compact
three-domain certificate, independently checked without an LP or SAT solver.

The pilot is `acceleration/results/20260916_guided_pilot/best_candidate.json`,
SHA256 `811a9290f68d550d3d5be2e8d417b6ce407ff280db8be62ba54fe911f287b39d`.
Its original complete star domains and their independent audit are
`best_domains_python.json` and `best_domains_audit.json` in that directory.

## Uniform necessary relation and exact fixed-K reduction

For an outer vertex u and a locally valid star S, let

```text
N(u,S) = fixed neighbors of u in the 99-vertex partial graph
         union the eight chosen disjoint-support outer neighbors.
```

This is the complete final neighborhood of u and has fourteen vertices.
For two distinct outer vertices u and v, their star choices S and T are
compatible precisely when

```text
v in N(u,S)  if and only if  u in N(v,T),
|N(u,S) intersect N(v,T)| = 1 if adjacent, else 2.
```

These conditions apply to **every outer pair**: fixed adjacent overlap pairs,
fixed nonadjacent overlap pairs, same-fibre pairs, and variable disjoint-support
pairs. Fixed adjacency is read from the completed neighborhoods as well.
The intersection includes both root-neighbor and outer vertices.

For a fixed complete E0=0 overlap assignment, this gives an exact binary
constraint problem over the 84 complete local-star domains. Any graph
completion supplies a valid choice at every vertex and satisfies every pair
relation. Conversely, a simultaneous choice satisfying all these relations
defines a symmetric simple graph with all outer degrees fourteen. The root
and its fourteen neighbors already have their final degrees. Root-to-outer
counts are fixed by the labels, outer-to-root-neighbor counts are exact by
the star quotas, inner pairs are already fixed, and all remaining pair
counts are exactly the displayed relations. Thus the simultaneous assignment
is a valid completion of this fixed K.

**Arc consistency is only a necessary test for that simultaneous choice.**
Nonempty surviving domains do not establish a graph. The reduction remains
conditional on a prescribed K and the E0=0 overlap model; it does not cover
all possible Conway graphs or prove a uniform obstruction.

## Bounded implementation and independent replay

`acceleration/goal_theory_pair_domains.py` starts from the **original complete
domains**, not from the reciprocal-edge survivors. A cached relation records
which choices at v support each choice at u. An unsupported choice is removed,
and the affected incoming arcs are reconsidered. Initial vertex pairs are
ordered by the product of their domain sizes.

The default limits are 30 seconds and 10,000,000 tested domain pairs. A limit
produces `INCOMPLETE`, without an exclusion. Deliberate pair-count and time
limits were independently checked; see
`acceleration/results/20260916_goal_theory_pair_caps_audit.json`.

The pilot reaches an empty domain at vertex 25 after only 673 domain-pair
comparisons, six built vertex-pair relations, and seven deletion events in
0.00116 seconds. The separate checker `acceleration/audit_goal_theory_pairs.py`
imports no pair producer: it independently re-enumerates the six complete
domains used by the trace, forms ordinary Python sets for full neighborhoods,
and replays every deletion by exact set intersection. All seven events pass;
the audit takes 0.107 seconds and 12,874 independent enumeration nodes.

The result and independent replay are:

```text
acceleration/results/20260916_goal_theory_pair_pilot.json
acceleration/results/20260916_goal_theory_pair_pilot_audit.json
```

## Three-domain support-intersection core

Only vertices 25, 66, and 77 are needed. Their complete domains have 17, 11,
and 8 choices respectively. Domain IDs below index the saved sorted masks.

| Relation | Complete choice pairs examined | Compatible pairs | Supported choices at vertex 77 |
|---|---:|---:|---|
| 77 with 66 | 8 × 11 = 88 | 1 | `{5}` |
| 77 with 25 | 8 × 17 = 136 | 20 | `{0, 6, 7}` |

The support sets are disjoint, so no star at vertex 77 can coexist with a
star at both 66 and 25. The sole compatible first pair uses choices
`(77:5, 66:7)`. All 21 compatible pairs in the two relations have the edge
**absent** and exactly **two** common neighbors. Both vertex pairs have
disjoint supports; neither a fixed adjacent pair, a same-fibre pair, nor
a fixed overlap nonedge is needed by this particular core.

This is a reusable obstruction rule: for a center u, intersect the sets of
its complete stars supported by selected other vertices. An empty intersection
excludes the fixed overlap assignment. There is no assertion that every K
contains this concrete three-domain pattern.

The extractor `acceleration/goal_theory_pair_core.py` writes the three full
domain tables and both relations. The separate
`acceleration/audit_goal_theory_pair_core.py` independently re-enumerates all
three domains and all 224 choice pairs. It verifies the empty intersection in
0.048 seconds with 5,301 local search nodes. This compact audit does not need
the original full 84-domain audit as a trusted premise.

```text
acceleration/results/20260916_goal_theory_pair_pilot_core.json
acceleration/results/20260916_goal_theory_pair_pilot_core_audit.json
```

The first fixed pilot is excluded by the small core. The next guided run
produced a survivor of the stronger arc consistency; its distinct global
obstruction is recorded below.

## Checked full-pair-AC survivor with a global obstruction

The next guided run evaluated 1,281 overlap states and accepted 37 trades in
35.68 seconds. Its best candidate is
`acceleration/results/20260916_guided_pair_pilot/best_candidate.json`, SHA256
`884cb45d945b98404f8037037e044d748fccf4107aeeb48f4e5fa1c46ee42c49`.
This is a different candidate from the first pilot above.

All 84 complete star domains were independently re-enumerated, confirming
**21,224 initial choices**. Native exact-pair propagation examined all 3,486
outer vertex-pair relations and 222,226,323 choice pairs. After 922 deletion
events, it leaves **15,617 choices across all 84 vertices**, with domain sizes
between 59 and 406.

The independent standard-library checker verified the entire nonempty
closure in 11.42 seconds. It re-enumerated the 84 complete domains in 916,324
search nodes, replayed all 922 deletion events using ordinary set
intersections, and checked that every final choice has a compatible choice
at each of the other 83 vertices. The deletion replay alone made 4,112,608
set-based compatibility checks. No audit cap was hit. See
`best_domains_audit.json`, `best_pair_native_500m.json`, and
`best_pair_audit.json` in the new pilot directory.

The separate Python producer reached its 30-second time cap after 3,006
relations and correctly records `INCOMPLETE` in `best_pair_python.json`.
The checked positive closure claim comes from the completed native result
and its complete independent replay, not from that capped Python run.

Nevertheless, the same fixed candidate has an independently checked integer
Farkas certificate in `best_ray.json` / `best_ray_audit.json`: 754 signed
label equalities, 500 nonnegative pair caps, and 231 edge upper bounds give
1,680 nonnegative combined coefficients with right-hand side **-5,404**.
It has no completion even in the necessary continuous linear system.

This is an explicit countercontrol to the sufficiency of full pair-domain
arc consistency. The supporting choice at another vertex can depend on
which pair is being checked; no common global selection has been supplied.
The combination of a completely checked arc-consistent closure and a
completely checked global linear contradiction identifies the present
method limit without relying on a solver's numeric status.

There is no reason to repeat graph completion search on this already excluded
K. The next construction work should vary K while accounting for global
constraints, or seek a new uniform theorem. Exact domain branching on this
particular candidate is useful only as a future bounded negative-control
regression, not as a graph-construction attempt.

## Bounded exact-CSP continuation design

For a new K that survives pair arc consistency and has no known exact global
exclusion, retain the same complete domain IDs and
cached binary support bitsets. Choose a vertex with the smallest nonsingleton
active domain, branch on each of its remaining complete stars, and propagate
all affected exact pair relations. Preserve a reversible deletion trail or
copy the 84 active-domain bitsets at each branch. No numerical relaxation is
needed by this search.

Use explicit global limits on elapsed time, branch nodes, and relation-pair
work. A missing relation table, interrupted propagation, or any limit returns
`UNKNOWN` for that branch and prevents an UNSAT conclusion for its ancestors.
An UNSAT claim requires every alternative of a branch to be exhaustively
covered, with complete initial domains and independently replayable empty
domain leaves. The proof checker must verify the branching partitions and
all support deletions, not just the final solver status.

When every active domain is a singleton, form the 336 undirected disjoint
edges from their reciprocal choices and add the 357 fixed edges. Write the
result as a new research candidate, then independently check all 99 degrees,
all 4,851 common-neighbor equations, simplicity, symmetry, and the total of
693 edges using the complete graph validator. Only that full validation can
turn a search result into a Conway graph. A fixed-K exhaustive failure remains
a restricted exclusion, even if its domain branching is fully checked.
