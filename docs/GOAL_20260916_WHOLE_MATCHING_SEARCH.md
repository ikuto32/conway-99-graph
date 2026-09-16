# Complete same-sign matching proposals and GPU ranking

This is the preserved7.332122→7.316246 continuation. The subsequent CUDA
reoptimization and current5.944366 seed are documented in
[GOAL_20260916_CUDA_CP_SEARCH.md](GOAL_20260916_CUDA_CP_SEARCH.md).

The preceding checkpoint independently excluded eight one-coordinate families
around the current best K. It did not solve the Conway-99 problem. This
continuation changes whole same-sign matchings, including disconnected cycles
and five-/six-edge changes beyond the earlier atomic3/4 move family.

## Complete proposal geometry

`overlap_matching_neighbors.rs` recursively enumerates every allowed perfect
matching on the 12 vertices of one same-sign coordinate. There are 6,040
matchings per coordinate and 14 such coordinates. All other 20 matchings stay
fixed. The original matching is omitted from each coordinate's output, and
the final full99 partial-graph caps and own-label quotas are checked. No
intermediate swap path is required.

At the saved 7.332122 seed, the native generator enumerates 84,560 matchings,
including 14 copies of the original matching. It rejects 9,908 replacements
on partial caps and emits **74,638 distinct legal noninitial candidates** in
0.703 seconds, including JSON construction. Its CLI/alignment QA rejects
16 invalid-input controls.

`audit_whole_matching_family.py` independently enumerates the perfect
matchings using full99 adjacency sets. It verifies exact candidate-set
equality, all changed edges and disjoint alternating cycles, 83,233,498
set-based pair checks, and 3,216,088 own-label quota checks in 24.56 seconds.
Ten metadata/completeness corruptions are rejected. The separate accepted-move
auditor checks real examples of all ten cycle partitions and rejects
23 geometric corruptions. All reports are in
`acceleration/results/20260916_whole_matching_qa`.

| Changed matching edges | Legal candidates |
| --- | ---: |
| 2 | 323 |
| 3 | 1,541 |
| 4 | 7,637 |
| 5 | 24,628 |
| 6 | 40,509 |

Of these, 23,435 have multiple disjoint cycles. The `extended` LP-selection
scope admits five-/six-edge changes or multiple cycles: **66,647 candidates**.
The generator still saves and scores the complete 74,638-candidate family.
These are same-sign coordinates only; cross-coordinate matchings and
simultaneous changes in multiple coordinates are outside this enumeration.

## Current-X pilot

`guided_matching_overlap.py` uses CUDA scores at the current fractional X,
then independently reoptimizes selected candidates with the existing IPM LP.
It selects fresh global minima, minima from diverse coordinate/cycle-shape
buckets, and seeded random candidates. Existing numerical LP results and the
current proposal batch can be reused. Native complete-star/pair checks gate
acceptance; the best geometry still needs separate independent evidence.

The 16-iteration `20260916_whole_matching_pilot` finishes in 85.89 seconds.
It optimizes 128 noninitial candidates plus the initial K, accepts no moves,
and leaves the best merit at **7.332122013712173**. The smallest noninitial
numeric merit is 7.5908135847517135. One complete proposal batch is reused
15 times, so 1,194,208 proposal occurrences are not distinct candidates.

`audit_matching_trace.py` independently checks the complete family once,
all 129 LP models and exact primal/dual intervals, all selected GPU scores,
the extended-scope filter, random choices, acceptance, and both caches.
Every saved LP has a strictly positive exact dual lower bound. This excludes
only those fixed assignments; it is not a proof of a local minimum over the
74,638-candidate family. The unchanged best reuses the prior complete-domain
and pair proof only after exact labeled graph/unknown-domain identity checks.
Its exact merit interval remains
`[7.3321220135202125, 7.332122013712176]`.

## Coordinate-specific fractional hints

CUDA evaluates the whole initial proposal family in about 9.5 ms of kernel
time. The complete diagnostic, including input/output and independent QA,
takes 15.17 seconds. Sixty-four independent full99 controls agree with all
4,326 active residual rows to within 5.83e-16. The additional 336 own-label
quota rows are independently verified to be constant zero residuals.

However, the current-X top 100 are all two-edge swaps. The best five-edge
cycle has score 39.14014 and rank 4,271; the best six-edge replacement has
score 46.33822 and rank 14,507. These are upper bounds at one fixed X, not
lower bounds on the reoptimized merit. Large scores do not exclude useful
candidates.

The second diagnostic uses the X vector from each coordinate's previously
saved continuous whole-matching LP. It computes the true fixed-K residuals
at this alternative X and retains the smaller of the current-X and
coordinate-X scores. It performs no new optimization and introduces no
feasibility claim about the fractional matching itself.

Scores improve for 58,924 candidates. Examples include a five-edge cycle
(native index 32085), 42.77503 to 32.71667, and a six-edge cycle (index 52435),
55.84803 to 34.76635. The top 100 remain two-edge swaps, so geometry diversity
still matters. There are 140 independent full99 evaluations: 77 full
coordinate-X row controls and 63 current-X objective controls. Maximum row
error is 6.66e-16. Reports are in
`20260916_whole_matching_gpu_diagnostic_v2` and
`20260916_whole_matching_coordinate_x_diagnostic` under acceleration/results.

The first current-X diagnostic stopped on a strict Python list/tuple input
wrapper error before independent comparison. Its artifacts and source are
preserved; the separately named v2 completes the comparison. This was not a
CUDA numerical failure and the failed run is not counted as a passing audit.

The original target remains an independently validated 99-vertex graph
satisfying all required SRG conditions, or a general nonexistence proof. No submission or general proof has
been obtained. Complete proposal enumeration, positive fixed-K bounds, and
numerical hints have distinct scopes throughout this continuation.

## Strictly improved seed after hint-based selection

`scan_matching_hint_shortlist.py` selects 64 previously unprobed extended
candidates using the smaller of the two GPU scores. It first covers each
coordinate and cycle partition, then other coordinate/partition minima, then
fills by score. All 129 earlier pilot candidates are excluded by exact labeled
edge identity. All 64 LPs finish numerically in 36.81 seconds. The independent
shortlist audit replays every selected index and role, checks both scores for
each selected candidate, and verifies each LP's full99 model and exact bounds.

Two candidates improve the old merit. Native index17436 is a five-edge cycle
with exact interval `[7.2561662855096225, 7.256166285514626]`, but independent
complete-domain/pair replay proves an empty domain after 4,140 deletions.
It is not adopted as the pair-consistent search seed.

Native index17109 changes four edges in two disjoint two-edge cycles within
root-group1 / same_1. Its exact interval is
**[7.31624645746978, 7.316246457542742]**, so the improvement over the previous
best is at least **0.015875555977470427**. Independent reenumeration verifies
all 84 local domains, 20,507 original choices, 1,245 pair deletions, and the
nonempty final closure retaining **12,558 choices**. The independent checker
uses 860,398 domain-search nodes and 4,625,450 set-based compatibility checks.

The new seed and all evidence are in
`acceleration/results/20260916_matching_hint_shortlist/adopted_index_17109`.
`combined_evidence.json` binds the exact merit decrease, full-domain/pair
proof, and integer certificate. That certificate has weighted RHS
`-579652763326826475169423633150`, excluding this fixed K itself. Thus this is
a better seed for further overlap changes, not a completed or completable
graph. Earlier eight-family exclusions remain tied to their old base K and
must not be transferred to the new seed.

The shortlist producer's numeric-best record (index17436) is preserved;
the separately named adopted directory records the pair-consistent choice.
No historical result is rewritten to hide the failed local check.

Fresh-output reproduction after the standard native/CUDA build:

```powershell
rustc -O -C target-cpu=native acceleration/overlap_matching_neighbors.rs -o acceleration/build/overlap_matching_neighbors.exe
.venv/Scripts/python.exe -B acceleration/guided_matching_overlap.py --initial acceleration/results/20260916_two_trade_pilot/best_candidate.json --out acceleration/build/whole_matching_replay --iterations 16 --coordinates all --move-scope extended --seed 20260926
```

CI now regenerates the full native family from the small saved input and
checks it with the independent standard-library enumerator. GitHub CI has
not been run in this continuation.

## Next GPU step: approximate reoptimization

The new scores still evaluate only two fixed X points. A CPU quality control
therefore tests a projected primal-dual method that optimizes X itself.
The independently constructed phase-I matrix has exactly 13 unit entries
per column, at most nine per row, and 21,840 nonzeros. Consequently
`||A||_2^2 <= ||A||_1 ||A||_infinity <= 117`; primal and dual step sizes
0.09 give product bound0.9477, below one.

The [derivation and saved controls](../acceleration/PHASE1_CHAMBOLLE_POCK_REVIEW.md)
use the baseline and four actual extended candidates with already audited LP
intervals. At the four candidates, warm-started 2,000-iteration primal values
are 8.13–10.49, compared with initial fixed-X scores 35–50. At 10,000 steps,
their excess over the known LP upper bounds is about 0.049–0.065. Sixty
independent full99 checkpoint comparisons pass. No LP is rerun in this study.

These are numerical quality controls for a prospective CUDA implementation,
not exact dual certificates or measured GPU optimization speeds. Keep the
best feasible primal value, including the initial X, because intermediate
iterations can worsen it. Near-tied candidates can remain misranked, so final
LP reoptimization and the independent exact/domain checks remain necessary.
Implementing batched CUDA approximate reoptimization is the next concrete
route, starting from the new 7.316246 pair-consistent seed.

The complete continuation is indexed in
`acceleration/results/20260916_whole_matching_search_checkpoint.json`.
Its builder verifies 1,815 referenced files and 48 direct artifacts without
rerunning solvers or domain enumeration. It records an active, incomplete
goal and preserves the preceding matching checkpoint byte-for-byte.
