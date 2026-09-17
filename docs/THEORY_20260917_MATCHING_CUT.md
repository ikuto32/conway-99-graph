# Candidate positive-adjacency cuts that survive changing K

Status: **CANDIDATE**, independently unchecked. Source base at execution:
`938b32242532723a094b0fcf8729907d423a9951`. No mathematical claim has been
promoted, and no new complete overlap assignment has been excluded by this pilot.

The bounded pilot lifts sixteen previously rejected local stars into sixteen
distinct conditional adjacency clauses. All sixteen survive removal of the
old fixed-K absent-edge restrictions. Greedy reduction leaves only 8–14 positive
K-edge prerequisites per clause, together with eight selected center-star edges.
The run completed in 1.109 seconds of measured wall time, below its 240-second
limit. This timing is one run, not a general performance claim.

## What differs from completed work

The independently audited triangle filter applies to all 26,250 original local
choices of baseline18481, rejecting 6,756 within that fixed assignment. Repeating
that exclusion or its filtered LP would not address changing K.

This experiment removes the dependence on K's unlisted edges being absent.
It considers **every** missing edge between the remaining neighborhood vertices,
including overlap-support and same-fibre edges absent from the original K. The
implementation has no support/fibre classifier or old unknown-edge whitelist in
this step; same-fibre pairs are tested even if their failure can subsequently be
derived from positive scaffold incidences. An edge is omitted
only when its insertion contradicts an exact degree bound or common-neighbor
cap using positive edges still present in the reduced graph. It then deletes
most positive K edges as well. The resulting clause applies to any changed K
containing the remaining positive prerequisites, with the same named star
edges. It does not assert that every possible star for that K is forbidden.

Prior work inspected before selection included `ACTIVE_RESEARCH.md` and its
preserved continuations, `GOAL_20260916_VERTEX_STAR.md`,
`GOAL_20260916_PAIR_DOMAIN.md`, `GOAL_20260916_MATCHING_MIP.md`,
`acceleration/GROUP_ORBIT_VALIDITY.md`, `THEORY_20260917.md`, and the independent
triangle audit. Existing root relabeling arguments describe coordinate changes;
no nontrivial automorphism of a solution is assumed here. This inspection is not
a literature novelty claim.

## Proposed necessary implication

Fix the existing labeled root scaffold: its 189 positive root, root-matching,
and root-label-incidence edges. Let `C` be a set of positive overlap edges and
let `S` be eight positive edges incident with an outer center `x`. In every
pilot record, `C` includes all four original K edges incident with `x`.
Together with the scaffold's two root-label incidences, these prerequisites
force **fourteen distinct neighbors of x**. A target SRG has degree fourteen,
so only at this point is its entire neighborhood determined. No other incident
edge at x can then be added. The remaining K edges are unspecified, not fixed
absent.

Write `P` for the graph consisting only of the scaffold, `C`, and `S`. In an
SRG with lambda=1, every vertex in `N(x)` has exactly one neighbor inside
`N(x)`, so the induced neighborhood is a perfect matching. Internal edges
already present in `P` are forced matching edges. Remove their endpoints.
Call the remaining vertices `U`.

Construct a permissive graph `H` on `U`. Consider every pair in `U`, without
using the original disjoint-support unknown-edge restriction. Insert that edge
into `P`. Retain it in `H` if both endpoint degrees stay at most fourteen and
every partial common-neighbor cap stays valid. Each actual completion edge
must pass this test: adding further edges cannot reduce a common-neighbor
count, lower a degree, or increase the allowed cap when an absent pair becomes
adjacent. Additional changed-K edges therefore cannot repair a failed test.

The raw certificate supplies a separator `T` in `H` such that `H-T` has more
odd components than `|T|`. In any perfect matching of `H`, each such component
needs at least one matching edge to `T`, since its vertices cannot all be
matched internally and it has no edges to another component of `H-T`.
Different components require different vertices of `T`. The inequality is
therefore impossible. Only this elementary parity implication is needed for
certificate checking; no completeness theorem for finding separators is relied
on to accept a saved witness.

Consequently the proposed cut is

```text
sum(A_ab for ab in C union S) <= |C union S| - 1,
conditional on the fixed positive root scaffold.
```

All coefficients are exact integers. These pilot clauses contain 16–22
positive adjacency literals. Their raw records have `negative_K_literals: []`.
Root-scaffold absent incidences follow from its already saturated root-neighbor
degrees; no additional changing-K edge is silently fixed absent. The implication
and each recorded certificate still require independent review.

The proposed scope is thus conditional on the positive scaffold itself, without
assuming a complete E0=0 overlap assignment. The baseline E0=0 configuration was
used to discover small positive prerequisites, not retained as an assumption of
the proposed implication. This wider exact scope is a CANDIDATE statement for
independent review, not a promoted conclusion about unrestricted root normalizations.

## A small raw example

For original outer vertex 3, domain ID 2, the full-99 center is 18. The retained
K edges are

```text
(18,35) (18,38) (18,44) (18,53)
(64,70) (66,88) (74,83) (81,83).
```

The eight selected star edges join 18 to
`64,66,70,72,77,79,83,88`. Together with scaffold neighbors 2 and 4, this lists
all fourteen neighbors. The free-neighbor graph has components
`{35,44,72,77,79}` and `{83}`. Both are odd, with an empty separator.
This gives a sixteen-literal clause with right side fifteen.

For a compact falsification check, the five possible partners of 83 are
individually blocked as follows. The listed common vertices are computed after
inserting the proposed edge into the reduced positive graph.

| Proposed edge | Violated pair | Common vertices | Permitted maximum |
|---|---|---|---|
| 35–83 | 35–83 | 13,18 | 1 |
| 44–83 | 8–83 | 7,44,81 | 2 |
| 72–83 | 14–83 | 13,72,74 | 2 |
| 77–83 | 8–83 | 7,77,81 | 2 |
| 79–83 | 79–83 | 7,18 | 1 |

The complete record also identifies forced internal matching edges and every
other allowed/blocked free-neighbor pair. This table is a candidate derivation,
not its independent approval.

## Preregistered experiment and actual result

Before the prototype ran, its immutable `manifest.json` fixed:

- First rejected original domain ID at each outer vertex 0 through 15.
- First surviving original domain ID at each outer vertex 0 through 7 as
  positive regression controls.
- All absent free-neighbor pairs considered, with no original-K zero literals.
- Sorted greedy deletion of non-center K edges; all four center-K edges protected.
- Integer/Boolean acceptance only, a 240-second limit, and preservation of any
  case where lifting restored a perfect matching.
- Empirical core-containment evaluation on the saved fresh16 and same13
  candidate assignments, a population of 29 saved candidate records.

Actual stage counts: 16 stars selected, 16 attempted, 16 successful candidate
lifts, zero failed lifts, zero timeouts, and eight of eight old-survivor controls
still admitting a matching in the permissive graph. The five prototype control
records cover K4, two disconnected odd components, repairing them with a bridge,
the empty matching, and a windmill with a corrupt second internal edge.
Controls and discoveries are producer-side only.

Retained K-edge counts, in vertex order, are
`8,8,10,8,11,12,14,8,8,8,12,8,10,9,8,10`. Each separator has size zero to three,
and each odd-component deficit is two. The selected positive cores occur in
18–27 of the 29 saved candidate assignments. Those counts overlap across cuts
and must not be added. They establish only containment of prerequisites;
they do not establish original-star domain membership, a new K exclusion,
unique isomorphism classes, or unrestricted coverage.

Greedy support reduction is not claimed to minimize cardinality. Complete
enumeration of all rejected stars, all positive cores, or all root relabelings
was not attempted. Overall search coverage: UNKNOWN; no validated denominator.

## Artifacts, replay, and next falsification

Producer: [theory_20260917_matching_cut.py](../acceleration/theory_20260917_matching_cut.py).
Evidence: [manifest](../acceleration/results/20260917_matching_cut/manifest.json),
[summary](../acceleration/results/20260917_matching_cut/summary.json), and the
sixteen per-star JSON files in the same directory. Each record preserves all
fourteen center neighbors, protected and deleted K edges, all positive clause
literals, forced matching edges, the entire permissive graph, a blocker for
every omitted free-neighbor edge, the odd-component separator, and named
containment witnesses. Input/source hashes and tool versions are in the manifest.

```powershell
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_matching_cut.py --out build/matching-cut-new --seconds 240
```

Use an unused output directory. The prototype imports no existing graph builder,
matching producer, or mathematical checker. It uses ordinary Python integer
bitsets, a memoized Boolean matching search to guide deletion, and a separately
enumerated separator to provide a short raw obstruction witness. These are two
internal producer algorithms, not independent verification.

The next concrete action is independent reconstruction from the raw positive
literal sets, without importing this producer: rebuild the full-99 graph,
verify all fourteen neighbors, test every candidate internal edge by a separate
matrix/set route, verify the odd-component separator directly, and falsify
corrupted/deleted prerequisites. If the cuts survive, add them conditionally
to a joint K/X search or reusable star-filter cache. Do not apply them as
unconditional K-only exclusions or as evidence that every neighborhood fails.

## Next experiment frozen, awaiting independent approval

[next_application_protocol.json](../acceleration/results/20260917_matching_cut/next_application_protocol.json)
pins the candidate, original-domain, and complete-domain audit bytes for all
29 saved fresh16/same13 records. The planning script only freezes this mapping;
it does not evaluate cuts or count eliminated choices. Execution is gated on an
independent PASS for the exact sixteen cut artifacts.

The first application stage uses only the sixteen identity clauses. For every
original star it will test literal containment in the scaffold plus the changed
K plus that star's eight edges. Candidate IDs, outer-vertex IDs, and original
domain IDs are retained. Every reported hit must agree with a direct edge-set
check. Counts will distinguish total original choices, unique removed
`(center, original_domain_id)` pairs, survivors, and overlapping clause hits.
An empty domain would need a separate complete-domain coverage review before
becoming a fixed-K exclusion. This pilot has a 180-second wall limit and no
floating-point threshold. No elimination counts are available yet.

A second stage is only an idea: transport the sixteen clauses through the 128
sign flips of the seven root matching pairs. Each flip permutes the fourteen
root-neighbor symbols and maps each outer root-label pair accordingly. It
preserves the positive scaffold and adjacency equations, so a sound transported
clause would follow by relabeling a hypothetical graph. No graph automorphism
is assumed. The exact bijection and transported fourteen-neighbor prerequisites
must be independently reviewed before this stage runs. Generated clause images
must be deduplicated before reporting unique cuts or unique removed stars.
No orbit application or expansive group search has been launched.
