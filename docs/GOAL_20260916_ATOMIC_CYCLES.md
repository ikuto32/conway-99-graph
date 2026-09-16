# Atomic matching cycles, 2026-09-16

The preceding continuation improved the necessary linear-completion merit to
about 7.33212201. That fixed overlap assignment is independently excluded,
despite passing complete-star pair arc consistency. The next search changes
the overlap assignment using larger simultaneous matching replacements.

## Move family and verification scope

Exact own-label quotas split the 168 overlap edges into 21 perfect matchings:
14 same-sign matchings with six edges and seven bipartite matchings with 12
edges. Replacing k matching edges along one alternating cycle preserves these
quotas and all degrees. Every added edge must still have a legal support, and
the resulting full 99-vertex partial graph must satisfy every common-neighbor
cap. Only this final partial graph is required to be valid; no intermediate
two-edge-swap path is claimed.

The raw subfamily contains
`14*C(6,k)*2^(k-1)*(k-1)! + 7*C(12,k)*(k-1)!` moves: 5,320 for k=3 and 30,870
for k=4. A connected alternating eight-cycle requires at least three two-edge
swaps, so the four-edge family reaches beyond the previous two-trade moves.
The independent combinatorial controls, including abstract switch-graph BFS,
are in `acceleration/results/20260916_atomic_matching_math.json`.
The derivation and limitations are in `acceleration/ATOMIC_CYCLE_PLAN.md`.

`acceleration/overlap_cycle_neighbors.rs` enumerates the selected subfamily.
Its interface is `INPUT.txt OUTPUT.json [3|4|both]`, with default 3. Input uses
the existing single-candidate C99OVERLAPS1 format. Output aligns
`overlap_candidates` with `moves`, whose fields are `removed`, `added`,
`root_group`, `matching_class`, `cycle_size`, and `alternating_cycle`.
The last field lists 2k distinct vertices: consecutive pairs starting at
position zero are removed edges; consecutive pairs starting at position one,
including the closing pair, are added edges. Classes are `same_0`, `same_1`,
and `cross`. Enumeration does not apply local-star or pair-AC filters.

Complete enumeration here means only this move subfamily at one fixed state.
It is not an exhaustive search of E0 assignments or of Conway graphs. It also
does not show that no improving move exists unless optimization bounds cover
every proposal; the search below solves only a finite shortlist.

## Candidate selection

`acceleration/guided_atomic_overlap.py` uses the existing CUDA residual kernel
and IPM phase-I solver. It ranks every generated endpoint at the current
fractional edge vector, then optimizes selected endpoints separately. A fixed-X
score is an upper bound on reoptimized merit, so even a high score cannot
exclude improvement.

By default each iteration selects two global best scores among candidates
without a cached usable LP, four bucket minima from randomly chosen distinct
`(root_group, matching_class, cycle_size)` buckets not already represented,
and two random remaining candidates. Up to two eligible cached optima are
considered separately. Thus cached trials do not consume the fresh LP budget.
Cached local failures, including capped checks, are skipped only as a search
policy; they are never promoted to mathematical exclusions.

The driver retains complete-star and exact pair-AC native checks at accepted
endpoints. It permits a small uphill escape, at most 0.5 with probability 0.1,
and records the best separately. Necessary-condition passes and numerical
merit zero still require independent exact validation and a full graph
construction. Every positive exact dual bound excludes only its own fixed K.

When the current state is unchanged, proposal and GPU batches are reused with
the same path and hash. Only the current batch is retained in memory. The
trace distinguishes newly generated proposal counts from repeated proposal
occurrences, and fresh LP trials from cached trials. All raw experiments and
old hash-bound sources are preserved.

The independent auditors are `audit_atomic_accepted.py` for accepted exact
merit intervals, `audit_atomic_trace.py` for proposals/LP/GPU/cache provenance,
and the existing complete-domain/pair checker for the final best geometry.
Their reports have separate scopes; native gate status alone is not an
independent local proof.

## Verified controls and first experiments

On the saved 7.332122 seed the native generator produces 2,940 legal k=3
endpoints and 13,359 legal k=4 endpoints. It examines all 36,190 raw cycles
for `both`. Independent recursive perfect-matching/bijection enumeration,
using a separate connectivity test and Python neighborhood sets, obtains
exactly the same legal-move set and per-coordinate counts. It checks
13,172,589 affected full-graph pair constraints in 4.26 seconds. Native times
on this control are 0.0266 seconds for k=3 and 0.1279 seconds for k=4,
including output construction. Twelve negative CLI controls and four
completeness/metadata corruption controls also pass. The evidence is in
`acceleration/results/20260916_atomic_cycle_qa/qa.json` and `both_audit.json`.

The separate accepted-move checker passes the previous successful net
three-edge cycle and rejects ten geometric corruptions, including a purported
four-edge move consisting of two disconnected cycles. See
`acceleration/results/20260916_atomic_geometry_auditor_qa.json`. Abstract
cycle checks do not assert a fabricated concrete graph witness.

The first separate 16-iteration pilots optimize 128 new endpoints each, plus
their shared initial assignment. Neither accepts a move or improves the
7.332122 seed. Atomic3 takes 69.64 seconds; Atomic4 takes 71.24 seconds.
Each generates its complete selected family once and reuses that batch 15
times. Thus repeated occurrence counts are not counts of distinct graphs.

The atomic3 trace audit independently reproduces its complete 2,940-endpoint
family and all 129 actual LPs. It exactly replays seeded shortlist selection,
tie-breaking, and uphill acceptance draws, checks two cached LP references,
and distinguishes 47,040 proposal occurrences from 2,940 generated endpoints.
Its 130 selected GPU scores and 16 baselines agree with independent full-graph
evaluation. All 129 exact dual lower bounds are positive.

Both final best geometries are exactly the prior best labeled graph. Their
local proof is reused only after verifying the original proof/source hashes
and exact identity of all 168 overlap edges, all 99 adjacency rows, and the
1,680 unknown-edge domain. The reports explicitly identify this reuse and
claim no new domain enumeration. Their new phase-I intervals and integer
certificates are separately checked; no improvement is claimed.

Fresh-output reproduction uses the isolated solver environment:

```powershell
rustc -O -C target-cpu=native acceleration/overlap_cycle_neighbors.rs -o acceleration/build/overlap_cycle_neighbors.exe
.venv/Scripts/python.exe -B acceleration/guided_atomic_overlap.py --initial acceleration/results/20260916_two_trade_pilot/best_candidate.json --out acceleration/build/atomic3_replay --iterations 16 --cycle-size 3 --seed 20260923
.venv/Scripts/python.exe -B acceleration/guided_atomic_overlap.py --initial acceleration/results/20260916_two_trade_pilot/best_candidate.json --out acceleration/build/atomic4_replay --iterations 16 --cycle-size 4 --seed 20260924
```

The revised CI step builds the native cycle generator and independently
reenumerates both families on this saved control. CUDA and HiGHS are not
required for that completeness check.

The additional `20260916_atomic_both_pilot` uses both families for 32
iterations, taking 145.90 seconds for 257 actual LPs and 25 cached LP lookups.
At iteration 25 it accepts one three-edge uphill move to the previously known
7.605367 assignment; the best stays 7.332122. Its two distinct current states
produce 16,299 and 16,028 endpoints respectively, or 32,327 proposal records
before cross-state deduplication. There are 519,942 repeated proposal
occurrences and 30 batch reuses. The accepted interval audit confirms the
uphill direction and no strict improvement. This is exploration, not progress
of the best merit or an exhaustive neighborhood optimum.

The k4 trace audit also passes: all 13,359 legal finals are independently
reenumerated and checked, all 129 actual LPs have positive exact dual lower
bounds, and the 10 cached LP lookups, 138 selected GPU scores, 16 baselines
and all random decisions agree. The graph/family and optimization scopes are
kept separate in each `trace_audit.json`.

The mixed-family trace audit also passes, independently reconstructing both
complete proposal batches and all 257 positive LP bounds. The frozen index
`acceleration/results/20260916_atomic_checkpoint.json` binds the three runs,
515 LP artifacts, all geometry/selection audits, and the unchanged best.
The count includes repeated candidates across runs and is not unique coverage.

A CPU study also tested whether one rounded dual could provide useful cheap
lower bounds for GPU pruning. It evaluates 319 distinct assignments, including
the initial point. All 318 noninitial transferred bounds are negative, from
-23.713504 to -2.045954, so none rules out an improving endpoint. The maximum
rounding error bound is only 0.015246; extra multiplier precision cannot fix
this lack of transfer. No GPU implementation of this ineffective pruning rule
was added. The exact arithmetic study and its limits are preserved in
`acceleration/results/20260916_atomic_cycle_qa/rounded_dual_cpu_study.json`.

The next implemented route frees an entire matching jointly with X. Its
derivation, numerical controls, and independently verified conditional family
exclusion are in [the whole-matching continuation](GOAL_20260916_MATCHING_MIP.md).
