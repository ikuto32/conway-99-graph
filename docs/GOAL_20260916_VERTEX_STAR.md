# A uniform nonlinear vertex-star condition for complete E0=0 overlaps

The new inexpensive condition rejects **50 of the 96 fixed-compression cut
survivors**, and **55 of the 100 variable-compression cut survivors**. Every
rejection was replayed by a separate exact search using actual graph changes.
This is a uniform necessary condition applicable to every complete overlap
assignment in the stated E0=0 domain; it is not a proof that every assignment
fails it. The positive controls below explicitly show that many pass.

## Necessary-condition theorem

Let P be the 99-vertex partial graph consisting of the root, its fourteen
neighbors, all root-label incidences, and a complete 168-edge overlap
assignment K on the 84 outer vertices. Every unlisted overlapping-support
edge and every same-fibre edge is fixed absent. Every outer vertex has degree
six in P: two root-label neighbors and four K-neighbors. Only disjoint-support
outer edges may be added.

For an outer vertex u, let D(u) be its forty disjoint-support outer vertices.
Any complete Conway graph extending P must supply an eight-element subset
S of D(u). Define P(u,S) by adding just the eight edges u-v for v in S.
Then:

1. Every pair in P(u,S) obeys the partial common-neighbor upper bound: one
   for adjacent pairs, two for nonadjacent pairs.
2. For every root-neighbor vertex r, the common-neighbor count of u and r
   already equals its final target, one or two according to adjacency.

Proof: adding edges never decreases a common-neighbor count. If a currently
absent edge is added, its own permitted count decreases from two to one.
Thus a subgraph of any valid completion satisfies all partial upper bounds.
Every root-neighbor already has degree fourteen in P, so its neighborhood
cannot change. Once all eight missing neighbors of u are chosen, each
u-r common-neighbor count is final. Therefore absence of such an S for even
one u excludes every completion of that fixed K. No disjoint compression
totals enter this argument.

## Small exact formulation

First discard every v for which adding u-v alone violates a partial pair cap.
For each root label s, prescribe

```text
sum_(v in S) [s in label(v)]
  = (1 if s's root group belongs to support(u), else 2)
    - number of K-neighbors of u carrying s.
```

These quotas sum to sixteen, so they require exactly eight selected vertices.
For each w other than u, write

```text
b(u,w) = 2 - P_uw - |N_P(u) intersect N_P(w)|.
```

The pair cap involving u is precisely

```text
|S intersect N_P(w)| + [w in S] <= b(u,w).
```

Finally, two selected vertices v and w create one new common neighbor u.
They therefore cannot both be selected when their existing pair cap is
already saturated. This is a nonlinear condition on the original disjoint
edge variables, implemented here as a conflict between two choices in S.
The one-edge permissions, displayed packing inequalities, and these
conflicts cover all changed pairs. They are equivalent to checking the
actual partial graph P(u,S), together with the exact label quotas.

The producer uses quota-first branching and integer residual capacities.
The independent auditor does **not** import that producer. It orders the
allowed vertices, enumerates subsets in increasing order, directly adds
each graph edge, and recomputes the affected common-neighbor counts using
99-bit adjacency rows. Prefix pruning is safe because counts are monotone;
remaining-label capacity pruning is an upper bound. There is no search-node
cap, timeout, LP, or SAT solver in either exact local search.

## Checked finite results

| Dataset | Snapshots | Impossible stars | Rejected snapshots | All-stars-pass snapshots | Explicit star witnesses |
|---|---:|---:|---:|---:|---:|
| Fixed compression, surviving the 1,280 previous cuts | 96 | 76 | 50 | 46 | 7,988 |
| Variable compression, 100 noninitial cut survivors | 100 | 92 | 55 | 45 | 8,308 |

The first scan took 3.54 seconds; its independent replay took 5.54 seconds.
The variable-compression scan took 3.77 seconds; its independent replay took
5.81 seconds. Each witness was checked by constructing the 365-edge partial
graph and examining all 4,851 pairs. Across both datasets, **16,296 explicit
star witnesses and 79,051,896 pair-cap checks pass**. The separate exhaustive
searches for all 168 impossible stars visit 163,588 nodes in total.

The fixed-compression snapshots with a witness for every star are:

```text
2, 8, 9, 12, 17, 21, 22, 24, 26, 27, 28, 29, 33, 35, 36, 37,
38, 40, 43, 47, 48, 50, 52, 53, 56, 58, 59, 60, 61, 62, 64,
65, 66, 68, 73, 79, 81, 82, 83, 84, 85, 86, 93, 96, 97, 99
```

The variable-compression snapshots with a witness for every star are:

```text
3, 4, 7, 10, 11, 13, 15, 16, 17, 18, 28, 30, 35, 37, 40, 41,
42, 45, 47, 48, 51, 52, 53, 55, 56, 58, 60, 61, 63, 66, 70,
71, 72, 74, 76, 77, 78, 79, 82, 83, 87, 93, 97, 99, 100
```

For example, wide snapshot 36 fails at outer vertices 26 and 51, while wide
snapshot 100 has all 84 separate local witnesses. Indexing is zero based
within each saved walk, not a global candidate identifier.

## What this resolves and what follows

The control replaces some expensive generic LP exclusions with a uniform
local combinatorial obstruction. It applies without holding C fixed and
without using the old cycle/flow projections. None of the 105 listed rejected
snapshots can be repaired solely by choosing different disjoint edges.

The 91 all-stars-pass snapshots are countercontrols to the claim that this
condition alone gives a uniform E0=0 obstruction. Independently chosen stars
need not agree: v can be selected as a neighbor of u while u is absent from
v's chosen star. They also need not jointly meet all common-neighbor counts.
Accordingly, local witnesses are not full graph candidates or evidence of
global satisfiability. Other checked LP certificates may already exclude
some all-stars-pass snapshots.

The next structural strengthening, now implemented below, enumerates all
feasible star domains L(u) and propagates reciprocal edge decisions. Adding
common-neighbor compatibility between two chosen stars would strengthen it
further. Native bitsets are well suited to these small set operations.

## Complete domains and reciprocal-edge propagation

For each u, enumerate the complete set L(u) of locally valid eight-neighbor
choices. A global graph must choose one S(u) in every L(u), with

```text
v belongs to S(u)  if and only if  u belongs to S(v).
```

If every remaining star at v contains u, remove every star at u omitting v.
If every remaining star at v omits u, remove every star at u containing v.
Repeat these sound deletions until a domain is empty or no deletion applies.
Induction proves that every simultaneous graph completion survives each
deletion, so an empty domain excludes that fixed K.

The implementation checks edge reciprocity only in this propagation stage.
A nonempty arc-consistent result would not guarantee that one can select
mutually reciprocal stars simultaneously, nor that a resulting graph meets
all pair counts. No sufficiency or global graph construction is claimed.

`acceleration/goal_theory_star_domains.py` uses explicit limits: 30 seconds
for the entire candidate enumeration, 2,000,000 global search nodes, and
20,000 choices per vertex by default. Hitting any limit returns `INCOMPLETE`
and completely disables propagation. All 84 domains must be complete before
any empty-domain result is used. Node-, domain-, and time-limit negative
controls independently confirm this behavior in
`20260916_goal_theory_domains_caps_audit.json`.

`acceleration/audit_goal_theory_domains.py` imports no domain producer. It
independently enumerates increasing-order vertex subsets using actual graph
edge additions, compares every complete domain exactly, then replays each
forced/forbidden-edge deletion and its domain IDs. Its own caps likewise
give an incomplete audit rather than an exclusion.

The two initial controls were followed by a bounded batch over **all 45**
all-stars-pass variable-compression snapshots. All 45 have complete domains
and independently verified empty-domain reciprocal closures. No enumeration
or audit was capped, and no arc-consistent survivor was obtained. The batch
took 145.5 seconds, preserving the two initial artifacts. Its full input,
domain, audit, and source hashes are in
`acceleration/results/20260916_goal_theory_domains_wide_batch/summary.json`.
Together with the preceding 55 single-star failures, this gives a purely
combinatorial exclusion of the saved 100 noninitial wide snapshots. These
are finite samples, not an enumeration of E0=0 assignments.

## Two compact reciprocal obstructions

The long deletion traces reduce to particularly small independently checked
cores. They concern complete local-star domains at the listed vertices,
not an unproved assumption about a small induced graph.

**Wide snapshot 100:** vertex 24 has exactly two possible complete stars,
both containing vertex 61. Vertex 61 has exactly one possible complete star,
which omits vertex 24. Their required values of edge 24–61 contradict.
Only two exhaustive domains, three star choices, and one deletion suffice.
The separate core checker re-enumerates these domains in 0.038 seconds.

**Wide snapshot 15:** all 24 stars at vertex 6 omit vertex 81, and all 20
stars at vertex 12 omit vertex 81. Every one of the nine stars at vertex 81
contains vertex 6 or vertex 12. Reciprocity forbids both options, emptying
the domain at 81. This uses three exhaustive domains, 53 star choices,
and two deletions. Independent re-enumeration takes 0.109 seconds.

The extractor is `acceleration/goal_theory_domain_core.py`; the separate
checker is `acceleration/audit_goal_theory_core.py`. The self-contained
core domain tables and their independent audits are:

```text
acceleration/results/20260916_goal_theory_core_wide15.json
acceleration/results/20260916_goal_theory_core_wide15_audit.json
acceleration/results/20260916_goal_theory_core_wide100.json
acceleration/results/20260916_goal_theory_core_wide100_audit.json
```

The reusable obstruction is the reciprocal-domain argument. There is no
claim that every K contains either concrete pattern. A productive next
construction experiment is to guide overlap trades toward a candidate
whose complete domains survive reciprocity, then test stronger pair
compatibility and the exact linear completion system.

## Artifacts and replay

Producer: `acceleration/goal_theory_vertex_star.py`.
Independent checker: `acceleration/audit_goal_theory_stars.py`.

The input hashes, all witnesses, exact failed vertices, and independent
search counts are preserved in:

```text
acceleration/results/20260916_goal_theory_stars96.json
acceleration/results/20260916_goal_theory_stars96_audit.json
acceleration/results/20260916_goal_theory_wide_stars100.json
acceleration/results/20260916_goal_theory_wide_stars100_audit.json
```

To independently recheck either result, choose a fresh output path:

```text
python acceleration/audit_goal_theory_stars.py --out build/stars96_recheck.json
python acceleration/audit_goal_theory_stars.py --walk acceleration/results/20260916_wide_walk_2000.json --control acceleration/results/20260916_goal_theory_wide_stars100.json --out build/wide_stars100_recheck.json
```

Create the output directory beforehand. Both auditors use only the Python
standard library and the existing independent partial-graph builder.
