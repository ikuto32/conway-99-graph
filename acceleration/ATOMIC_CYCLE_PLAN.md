# Proposed next move: atomic alternating cycles inside a matching

This is a bounded design analysis, not an implemented generator or a new
search result. The proposed next family is a simultaneous three-edge or
four-edge replacement inside one of the overlap graph's 21 perfect matchings.
Validate the completed replacement directly; do not require its decomposition
into two-edge swaps to pass intermediate partial-graph or pair-AC filters.

## Why the matching decomposition is forced

Write an outer vertex as `u = {(a,s),(b,t)}`, with distinct root groups `a,b`
in `0..6` and signs `s,t` in `0..1`. In the current E0 representation, every
K edge shares exactly one root group, and every outer vertex has K degree four.

For the root neighbor `(a,s)`, adjacent to `u`, the common-neighbor cap is one.
The known root edges contribute zero, so at most one K neighbor of `u` can
carry `(a,s)`. For the opposite root neighbor `(a,1-s)`, the cap is two and
the known edge between the two root signs contributes one. Thus at most one
K neighbor can carry `(a,1-s)`. The same argument applies to `(b,t)` and
`(b,1-t)`. Every K neighbor belongs to exactly one of these four categories;
degree four forces all four upper bounds to be equalities.

Consequently, for each fixed root group `a`, its 24 incident outer vertices
each have exactly two K neighbors sharing `a`: one with the same `a` sign
and one with the opposite `a` sign. Each sign cohort has 12 vertices, since
there are six choices of the other group and two of its signs. Its edges
therefore split into:

- `M[a,0]`: a perfect matching on the 12 vertices with `a` sign zero, six edges;
- `M[a,1]`: a perfect matching on the 12 vertices with `a` sign one, six edges;
- `B[a]`: a bipartite perfect matching between these cohorts, 12 edges.

Across seven groups there are 14 six-edge matchings and seven 12-edge
bipartite matchings: 21 matchings containing all 168 K edges. These are
independent coordinate choices for degree/quota purposes, but their
common-neighbor caps and completion constraints remain coupled.

This decomposition was checked directly on the saved 7.605367 and 7.332122
best candidates: each had exactly these 21 classes and degree one in every
applicable matching. No new candidate enumeration was performed for this plan.

A legal two-edge swap must remain inside one matching. At every endpoint,
the lost and replacement neighbor must carry the same one of its four
own-label categories. The two removed edges must therefore share the same
root group and sign class. This explains both the structure of the existing
move set and how to enlarge it without weakening the exact quota invariants.

## Atomic move specification

For a bipartite matching, choose `k` edges `(u_i,v_i)`, with all `u_i` in sign
zero and all `v_i` in sign one. Choose a permutation `pi` that is one `k`-cycle.
Remove the selected edges and insert `(u_i,v_pi(i))` simultaneously.

For a same-sign matching, choose `k` edges on `2k` distinct endpoints. Replace
them by a perfect matching such that the union of the old and new edges is
one alternating cycle of length `2k`. A convenient representation is an
ordered, oriented list of old edges `(a_i,b_i)`, inserting `(b_i,a_(i+1))`
cyclically. Canonicalize rotation/reversal and deduplicate final edge sets.

Start with `k=3`, then add `k=4`. Both moves preserve every vertex's K degree
and own-label categories by construction. The remaining checks are essential:

1. Every added edge is canonical, absent, and joins distinct supports sharing
   exactly the selected root group. In particular, endpoints cannot have the
   same other root group; those would create prohibited same-fibre edges.
2. Apply the entire atomic replacement before checking caps. Check each of
   the `2k` changed full-99 neighborhood rows against all 99 rows. Unchanged
   row pairs and their adjacency are unaffected. Also run the existing full
   independent Python graph/quota checker on saved QA controls.
3. Enumerate complete star domains and perform full pair AC on selected final
   candidates using the existing caps. An incomplete result is unavailable,
   never a rejection certificate. No pair-AC claim follows from degree/quota
   preservation alone.
4. Persist one atomic `{removed: k edges, added: k edges, root_group,
   matching_class, alternating_cycle}` record. Do not invent a valid
   intermediate path when its two-edge decomposition is invalid.

An atomic three-edge cycle may be expressible as two algebraic swaps while
every chosen intermediate violates a partial cap. Such a candidate is absent
from the current generator, which insists that both intermediate graphs be
valid. A single alternating eight-cycle inside one matching requires at least
three two-edge swaps; two switches either affect disjoint alternating
four-cycles or cancel an edge and change at most three original matching
edges. Thus atomic four-edge cycles also enlarge the move family beyond all
current two-step paths, regardless of intermediate checks.

## Exact size of the raw move families

These counts are before support and pair-cap rejection; they count only a
single alternating cycle inside one matching, not all possible multi-cycle
replacements or the complete graph neighborhood.

For `k` chosen edges of a same-sign matching, the number of replacements
forming one alternating `2k`-cycle is `2^(k-1) (k-1)!`: choose a cyclic order
of the old matched pairs, then endpoint orientations, identifying reversal.
For `k` chosen edges of a bipartite matching it is `(k-1)!`, the number of
single cycles on the selected partners. Therefore

`N_k = 14 * C(6,k) * 2^(k-1) * (k-1)! + 7 * C(12,k) * (k-1)!`.

| Cycle | Same-sign moves | Bipartite moves | Total raw moves |
| --- | ---: | ---: | ---: |
| Six vertices, `k=3` | `14 * 20 * 8 = 2,240` | `7 * 220 * 2 = 3,080` | **5,320** |
| Eight vertices, `k=4` | `14 * 15 * 48 = 10,080` | `7 * 495 * 6 = 20,790` | **30,870** |

These finite sizes support enumerating the complete proposed subfamily once
per state rather than repeatedly sampling the same two-edge neighbors. Native
runtime and the number surviving full partial caps must still be measured.
Use the existing CUDA fixed-X merit to rank valid finals, followed by actual
phase-I solves and full pair AC on a bounded shortlist. Fixed-X merit is an
upper bound on the reoptimized objective, so a large fixed-X score cannot
safely discard a candidate as incapable of improvement. Reserve some solve
budget across matching classes and cycle lengths rather than interpreting
only the best fixed-X candidates as an exhaustive plateau test.

## What the successful two-trade pilot actually established

The accepted path in `results/20260916_two_trade_pilot/summary.json`, iteration
5, changed numerical merit from 7.6053670271 to 7.3321220137. Both swaps are in
`B[3]`, with zero-based root-group numbering. Their net replacement is:

```text
remove: (31,64), (65,70), (28,62)
add:    (31,65), (28,70), (62,64)
```

This is precisely one bipartite three-edge cycle, providing a concrete
successful member of the proposed atomic family. It does not establish that
any new cycle will improve merit or retain pair AC.

The fresh intermediate check is saved in
`results/20260916_two_trade_intermediate/summary.json`. All 84 original domains
were nonempty (21,456 values, minimum 72); native full pair AC remained
nonempty with 13,275 survivors after all 3,486 relations and 227,102,153 domain
pair checks. The check took 0.545 seconds. Intermediate/final partial graphs
and the saved trade path were independently replayed, but these native domain
and AC outcomes were not independently re-enumerated/replayed in this check.

Accordingly, this accepted path **did not demonstrate crossing a native
pair-AC-empty intermediate**. It demonstrates useful wider proposal selection.
It did cross the one-step merit threshold in the recorded order. The separate
independent rational audit, `results/20260916_two_trade_intermediate/barrier_audit.json`,
bounds the intermediate optimum between approximately 9.110011794299139
and 9.11001181442254. Its lower bound exceeds the initial upper bound
7.605367027128334 by at least 1.5046447671708045, exceeding the existing
one-step allowed increase of 0.5. Thus the recorded first step would be
rejected even though the combined move gives a certified strict decrease.
This does not prove that every alternative path or ordering has such a
barrier. It directly motivates evaluating a simultaneous matching cycle by
its endpoint rather than imposing the merit rule after each constituent swap.

The earlier saved 22.22012 → 19.97120 → 17.51056 detour does have a native
AC-empty intermediate, as recorded in `results/20260916_two_trade_qa/known_detour.json`.

## Symmetries and limitations

Permuting the seven root groups and globally flipping their signs induces
only a relabeling of this representation. Applying the same permutation to
the unknown-edge variables, rows, and star domains preserves the unweighted
phase-I optimum and pair-AC status. Such relabelings can alter a sampler's
order but should not be counted as new structural progress. A sign or vertex
permutation restricted to only part of the incidence structure is not an
automatic symmetry and must pass all quota/cap checks.

Atomic cycles stay within the existing E0 representation. They do not test
other same-fibre or overlap-degree regimes. Larger simultaneous changes may
have a lower pair-AC survival rate; the new family's usefulness must be judged
by valid distinct final states, independently verified controls, and actual
LP improvement, not its raw proposal count. A nonempty pair-AC endpoint is
still only a necessary-condition survivor, never a Conway graph witness.
