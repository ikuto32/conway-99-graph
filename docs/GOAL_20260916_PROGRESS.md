# Active Conway-99 construction or nonexistence goal

Execution stopped at the user's request. The latest round3 checkpoint and
completed128-case GPU ranking are in `STOP_20260916_FRESH_STAR.md`.
The mathematical objective remains unsolved; further exploration awaits a new resume instruction.

On 2026-09-16 the user explicitly requested a reset of the goal and continued
work. The goal tracker is **active**: construct a simple graph on 99 vertices
with degree 14, one common neighbor for every adjacent pair, and two for
every nonadjacent pair, or establish general nonexistence with an independent
verification. No such graph or general proof has been obtained.

Latest continuation: `GOAL_20260916_STAR_MARGINAL.md` and
`acceleration/results/20260916_star_guided_round2_checkpoint.json` (5,170 hash-verified files,
SHA-256 `7e5ff439fb04330b5654e3ce5e767b0972b9d563e5fe6695f00eef8478e4ed1b`).
Alternating Rust/GPU proposal searches reach a positive exact edge phase-I
interval approximately[0.06406993901974968,0.06406993911128354], then find two
numerical-zero candidates. Both pass independent complete local/pair checks;
neither is a graph or a certified exact LP feasible point. Fixed-K SAT returns
UNSAT for both, and independent DRAT checking passes. Nine more neighboring
numerical-zero cases also have verified DRAT contradictions and complete
local audits. A stronger star-simplex objective supplies independently
replayed integer obstructions for all11 cases and improves from approximately
9.067435 to8.113671. A subsequent8,837-candidate cross neighborhood, CUDA
selection and14 independently audited star LPs improve the new objective to
approximately6.038934. That round's best seed is candidate3074; all14 fixed-K bounds
remain positive and independently replayed. This is a different objective,
not a comparison to the old edge value. Rust fixed-dual integer ranking scores
the same8,837 candidates in68.27seconds, with no caps or pruning. A separate16
ranked-candidate cohort adds14 star certificates and2 independently replayed
pair contradictions without improving the seed. A bounded saved14-case CPU
study supports cold-start star-PDHG, now implemented and checked on CUDA.
The same two saved candidates run9.43× faster by the median of three paired
process comparisons, including startup and scalar JSON writing. See
`acceleration/STAR_PDHG_GPU.md` for measurement scope.

A further same-sign neighborhood has81,000 independently enumerated legal
candidates. Its64 old-edge LP records include one original strict-gap failure.
The original STOPPED receipt is preserved; a separately stored high-accuracy
solve passes the unchanged1e−7 audit. The recovered view independently checks
all64 records and all11 near-zero stronger LPs. Their fixed configurations
are excluded by exact integer replays; two strictly improve the seed.
The current best is18481, interval approximately[5.374367028255648,5.3743670369854],
with guaranteed decrease at least0.6645673908297139 from3074. All84 complete
domains and635 pair deletions are independently checked. The latest checkpoint
has no pending completion work and explicitly records recovery. Earlier indices below
remain historical evidence; the goal is still active.

The machine-readable continuation index is
`acceleration/results/20260916_goal_checkpoint.json`. It binds the current
coverage, search-trace, domain, GPU and exact-certificate audits by SHA-256.
That index preserves the first goal turn. The subsequent global-defect
continuation is described below and in `GOAL_20260916_GLOBAL_PHASE1.md`.

The requested Rust/GPU acceleration is implemented and tested. The current
research studies complete E0=0 overlap assignments followed by their disjoint
edge completions. Every exclusion below is restricted to explicitly identified
assignments. No batch is an exhaustive enumeration of this domain.

## Fixed walk: all stored snapshots excluded

The 10,000-step Rust walk has 101 saved snapshots. Its initial snapshot and
four selected snapshots were already excluded in the earlier continuation.
Eight further snapshots were checked using the separate dual LP. The remaining
88 were checked using direct infeasibility rays. The independent coverage
auditor reconstructs the full partial graphs, matches every certificate to its
snapshot, and rechecks all integer coefficients and negative right-hand sides.

`acceleration/results/20260916_fixed101_coverage_audit.json` records exactly
101 covered snapshots, 169,680 integer coefficient checks, and 489,951 partial
pair checks. The 9,931 distinct intermediate walk states have **not** all been
excluded. The earlier final-bank summary with 96 unresolved samples is retained
as historical evidence.

```powershell
python -B acceleration/audit_snapshot_coverage.py --walk acceleration/results/20260916_walk_10000.json --certificate acceleration/results/20260916_walk_highs.json --certificate-dir acceleration/results/20260916_probes --certificate-dir acceleration/results/20260916_goal_probes --certificate-dir acceleration/results/20260916_remaining_rays --out acceleration/build/fixed101_replay.json
```

Use a fresh output path. The auditor needs only the Python standard library.

## Faster exact certificates

`acceleration/ray_probe.py` requests a primal infeasibility ray directly from
HiGHS instead of solving a second minimum-L1 dual LP. It normalizes and rounds
the ray, reconstructs integer inequalities, and adds exact variable-bound
corrections. The unchanged producer-free full-graph auditor decides whether
the resulting certificate is valid. Numerical infeasibility alone excludes
nothing; numerical feasibility remains a relaxation result.

Typical new probes take about 1.2 seconds, versus roughly 14–22 seconds for
the previous two-LP procedure on these inputs. These are end-to-end producer
measurements on different snapshot subsets, not a controlled universal speedup.
`acceleration/results/20260916_ray_model_status_review.json` separately checks
all 4,200 rows of an actual model and twelve error/status cases. The Python
environment now includes `highspy==1.15.1` as well as NumPy and SciPy.

```powershell
.venv/Scripts/python.exe -m pip install -r acceleration/requirements.txt
.venv/Scripts/python.exe -B acceleration/ray_probe.py --input acceleration/results/20260916_wide_probes/candidate_15.json --out acceleration/build/wide15_replay.json --seconds 30
```

The HiGHS interface was checked against its primary documentation:
https://ergo-code.github.io/HiGHS/dev/interfaces/python/example-py/ and
https://ergo-code.github.io/HiGHS/dev/structures/enums/ . Solver results are
accepted only through the exact local checker, independently of those docs.

## Wider Rust walk and nonlinear structural conditions

The separate `acceleration/overlap_wide_walk.rs` allows overlap block totals
to change while preserving every required partial-graph invariant. In 2,000
steps it visited 1,995 distinct overlap assignments and 1,491 distinct overlap
compressions. Independent full-graph replay checked all 2,001 states. The
101 saved snapshots also have full Python/Rust/CUDA parity on 129,280 scores.
See `acceleration/WIDE_WALK.md` for commands and exact hashes.

The one-vertex nonlinear completion condition in
`docs/GOAL_20260916_VERTEX_STAR.md` excludes 55 of the 100 noninitial wide
snapshots by complete local exhaustion. Each of the other 45 has a separately
verified local completion for every vertex, which need not agree across
vertices. Three already have exact linear contradictions; a finite sweep of
the remaining 42 is recorded in `acceleration/results/20260916_wide_remaining_rays`.
The final combined independent audit is now complete:
`acceleration/results/20260916_wide101_coverage_audit.json`. It directly
re-enumerates 55 failed stars and replays 46 integer certificates, including
the initial snapshot. The historical `wide_bank/summary.json` is not overwritten.

Complete domains and reciprocal edge choices now exclude all 45 remaining
noninitial wide samples by a separately verified combinatorial argument.
`acceleration/results/20260916_goal_theory_domains_wide_batch/summary.json`
binds every candidate, complete domain table, and independent audit. No cap
was reached. Some proofs reduce to two or three vertices: wide100 needs
only three possible stars at two vertices, which require opposite values
of the same edge. See the vertex-star document for the exact cores.

## Native domains and a new countercontrol

The dependency-free Rust domain enumerator reproduces every Python domain on
the controls, and the independent checker re-enumerates them using a different
branch order and actual graph changes. On wide15, the native enumeration takes
0.00291 seconds versus 0.251 seconds for the Python producer, about 86 times
faster for this control. Process startup and independent audit are excluded
from this kernel comparison. The batch derivative resets all caps per candidate;
mixed complete/incomplete controls verify this behavior. See the artifacts in
`acceleration/results/20260916_rust_star_domains`.

The native neighbor generator was independently exhaustively compared with
Python and the earlier Rust walk on nine controls, totaling 4,587 legal trades.
`guided_overlap.py` uses these neighbors and complete star domains to prefer
assignments with more supported local choices. These scores are heuristics.

The first bounded pilot evaluated 225 candidate states and accepted seven
trades in 5.76 seconds. Its final assignment **passes reciprocal-domain arc
consistency**, confirmed by independent re-enumeration of all 84 domains
(484,517 search nodes). However, a separate exact integer linear certificate
excludes the same assignment with right-hand side -10,705. This positive
control for reciprocity demonstrates that the condition alone cannot exclude
every E0=0 assignment. It is not a graph completion or evidence of satisfiability.

The pilot's inputs, trace, candidate, native/Python domain tables, independent
domain audit and exact linear certificate are all in
`acceleration/results/20260916_guided_pilot`.

```powershell
rustc -O -C target-cpu=native acceleration/overlap_neighbors.rs -o acceleration/build/overlap_neighbors.exe
rustc -O -C target-cpu=native acceleration/star_domains.rs -o acceleration/build/star_domains.exe
rustc -O -C target-cpu=native acceleration/star_domains_batch.rs -o acceleration/build/star_domains_batch.exe
python -B acceleration/guided_overlap.py --initial acceleration/results/20260916_wide_probes/candidate_15.json --out acceleration/build/guided_replay --iterations 8 --neighbors 32 --seed 20260916 --batch acceleration/build/star_domains_batch.exe
```

Always use fresh output paths. The pilot used single-candidate native calls;
batch mode preserves the candidate order and complete payloads. The current
pilot driver has a harmless reporting edge case if a passing candidate is
first found on the last permitted iteration: the status can still say
`ITERATION_LIMIT`, while `best_rank[0]` and the complete domains identify the
necessary-condition survivor. Its hash-bound source remains preserved.

The exact common-neighbor strengthening is now implemented and independently
verified. It excludes the first pilot via just three complete local domains
and two disjoint-support nonedge relations. Details and the equivalence between
a simultaneous assignment of all stars and a full fixed-K completion are in
`docs/GOAL_20260916_PAIR_DOMAIN.md`.

## Rust/CUDA pair-guided frontier

`star_pair_gpu.cu` evaluates exact initial pair support for batches of complete
star domains. Its full flags, not only summaries, agree with an independent
Python set-based reference on 1,369,666 control relations. The 16,502-domain
control batch takes 0.913 milliseconds for transfers plus kernel, with CUDA
initialization, parsing, aggregation, and output excluded. The format and
timing definitions are in `acceleration/STAR_PAIR_GPU_FORMAT.md`.

`guided_pair_overlap.py` combines native complete-domain enumeration, CUDA
support scores, and variable-compression trades. The 40-iteration pilot
evaluated 1,281 states and accepted 37 moves in **35.68 seconds end to end**.
Every batch of proposals is preserved. An independent auditor checks all
1,280 proposed graphs, all recorded trades, all 38 accepted snapshots, and
6,218,982 full-graph pair caps. This is a heuristic local search, not an
exhaustive cover of a graph class.

The final best assignment has 21,224 complete local stars. Independent GPU
score replay verifies all 1,761,592 nonself support flags: 17,104 choices
(80.588%) have support against each of the 83 original neighboring domains,
and every vertex has at least one such choice. The initial assignment had
only 63 vertices with such choices and a 5.141% supported-choice fraction.
This fraction measures a local necessary condition, not distance to a graph.

Full exact pair arc consistency examines all 3,486 vertex-pair relations and
222,226,323 domain pairs in 0.524 seconds in Rust. It retains **15,617** choices
across all 84 vertices, with a minimum of 59 at any vertex. A producer-free
auditor re-enumerates all complete domains, checks all 922 deletions using set
intersections, and verifies the final arc closure (4,112,608 compatibility
checks, 11.42 seconds). The native 10-million-pair attempt and Python 30-second
attempt were capped; their preserved `INCOMPLETE` results are not proofs.
An additional CUDA/Python set comparison verifies every one of the 1,296,211
remaining nonself support flags is true; the final domains are arc closed.

Despite passing full pair arc consistency, this same assignment has an
independent exact linear contradiction with RHS **-5,404**. Thus even complete
pair arc consistency is insufficient as a uniform obstruction. No simultaneous
star assignment, feasible linear completion, or full Conway graph was found.
The next search should couple these fast local conditions with global
completion constraints; the saved best assignment itself is already excluded.

All outputs are in `acceleration/results/20260916_guided_pair_pilot`, with
the full proposal/trace audit in
`acceleration/results/20260916_guided_pair_pilot_trace_audit.json`.

```powershell
./acceleration/build_star_pair_gpu.ps1
rustc -O -C target-cpu=native acceleration/pair_domains.rs -o acceleration/build/pair_domains.exe
python -B acceleration/guided_pair_overlap.py --initial acceleration/results/20260916_guided_pilot/best_candidate.json --out acceleration/build/pair_guided_replay --iterations 40 --neighbors 32 --seed 20260917
```

Build the native neighbor/domain binaries from the preceding section first.
Full independent replays create new artifacts with current source/path hashes;
historical Windows path bindings are retained in the original records.

## Global-defect continuation

The previous goal turn constitutes progress: it produced an independently
checked pair-arc-consistent assignment with an exact global linear obstruction,
which changes the next search objective. The continuation uses an unweighted
phase-I merit: minimize the sum of absolute label-quota residuals plus positive
linear pair-cap residuals over all 1,680 fractional disjoint-edge variables.
Only a zero **exact** optimum gives feasibility of this necessary relaxation;
it is still weaker than a graph completion.

The new `phase1_probe_ipm.py` solves this model in roughly 0.34–0.43 seconds
on the initial controls, compared with roughly nine seconds for cold simplex.
The independent checker reconstructs the full graph equations, derives exact
rational primal/dual bounds, and verifies nonnegative complementary slacks.
The first threshold-based KKT diagnostic was too strict for an interior-point
solution near a kink; its frozen source is retained and the corrected separate
`audit_phase1_kkt.py` checks the actual duality gap. Four controls and twelve
corruption/nonoptimality cases are recorded in
`acceleration/results/20260916_phase1_independent_review_v2/review.json`.

CUDA evaluates every proposed overlap assignment at the current fractional
vector. Full comparison of 121,128 individual residuals has maximum difference
1.78e-15 from an independent full-graph evaluator. A 512-candidate batch took
1.218 milliseconds for transfers plus kernel. These fixed-X scores are only
upper bounds on the optimized defect; the driver solves the actual phase-I
problem for four top-ranked and two random proposals per iteration.

The 24-iteration `20260916_global_pilot` evaluated 3,072 legal proposals,
performed 137 actual LP solves, and reused eight cached optima in 79.85 seconds.
All 15 accepted moves strictly improve the **true** optimized merit, as proved
by disjoint exact rational intervals. The certified total improvement is at
least 13.754975831260555: initial lower bound 22.22012029560093 exceeds final
upper bound 8.465144464340375. The final lower bound remains positive. All 137
LP-probed candidates have independently verified positive exact dual bounds;
the other proposals have not been credited as exclusions.

The full trace audit checks every proposed graph/trade, each LP input/model,
all 144 selected GPU scores and 24 GPU baselines, all cache references, and
the saved-best identity. The final integer certificate and accepted-state
intervals are in `accepted_phase1_audit_details/`; the two main reports are
`trace_audit.json` and `accepted_phase1_audit.json` in the pilot directory.

However, the best global-defect assignment fails native full pair arc
consistency. A bounded scan of the accepted path finds only one noninitial
pair-AC survivor, with defect about 17.51056004. The subsequent
`guided_coupled_overlap.py` therefore requires both a completed native pair-AC
pass and an acceptable global merit before accepting a move. Two bounded
searches use the independently checked original seed and that alternative
native-checked seed; all capped checks remain unavailable results, not proofs.
An allowed small uphill escape is recorded explicitly and must not be called
a monotone improvement. Independent final-state audits remain mandatory.

The coupled runs and the first two-trade run have now finished. Each final
best has independent complete-domain enumeration, exact pair-compatibility
deletion/closure replay, rational phase-I bounds and an integer contradiction.
The following quantities concern necessary relaxations, not progress toward
a proven fraction of a complete graph.

| Run suffix (20260916_) | Proposals / actual LPs | Accepted moves | Final defect | Pair-AC choices | Search seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| coupled_pilot | 3,072 / 176 | 12 | 9.09764321 | 12,266 | 114.05 |
| coupled_alt | 2,048 / 113 | 5 | 10.11509750 | 12,801 | 75.66 |
| coupled_continue | 9,216 / 176 | 3 | 7.60536703 | 11,613 | 114.01 |
| two_trade_pilot | 2,048 / 129 | 1 path / 2 trades | 7.33212201 | 13,665 | 75.09 |

The main route starts at defect 22.22012043; the alternate route starts at
17.51056004. The 48-iteration continuation includes one strictly uphill move,
then two strict improvements. Its 209 LP cache references are individually
checked; all 176 newly solved candidates have positive exact lower bounds.
The original global pilot and all three one-trade coupled runs have complete
independent trace audits, with every sampled partial graph, selected GPU
score, LP model, cache binding and gate-input binding checked.

`overlap_two_neighbors.rs` broadens the sampled move family to two successive
legal degree-preserving trades, retaining both intermediate and final partial
graph caps. It rejects duplicate endpoints and endpoints reachable by a single
two-edge swap (fewer than three net removed edges). Its bounded nonuniform
sampling is not exhaustive. Separate controls replay 128 proposals and all
257 partial graphs, plus deterministic-seed and invalid-input/corruption tests;
see `acceleration/TWO_TRADE_NEIGHBORS.md`.

`guided_two_trade_overlap.py` retains the coupled driver semantics: CUDA ranks
the fixed-X scores, six top-ranked and two random finalists receive actual
LP solves, and acceptable endpoints must pass complete native pair AC. Only
the endpoint needs this pair AC gate. The 16-iteration pilot accepts one path
at iteration 5. Its exact optimum lies in
**[7.3321220135202125, 7.332122013712176]**. The accepted interval audit proves
a reduction of at least **0.27324501340468477** from its starting assignment.

The final local audit independently enumerates 21,145 complete stars, checks
1,079 pair-domain deletions and verifies the nonempty final closure containing
13,665 choices. Nevertheless, the same fixed assignment has an independently
checked integer contradiction with RHS **-9,076,727,413,462,412,930,908,104,042**.
Its files are in `acceleration/results/20260916_two_trade_pilot`, including
`accepted_phase1_intervals_audit.json`, `best_pair_independent_audit.json`, and
`best_combined_evidence.json`. Preserve the solver's original candidate hash;
the best-candidate wrapper is linked by independently checked edge identity.
The completed `trace_audit.json` additionally replays all 4,096 atomic trades,
checks all 2,048 middle and 2,048 final partial graphs, and validates all 129
actual LP models with positive exact dual bounds. Its 144 selected/baseline
GPU comparisons agree to numerical tolerance. No final proposal within a
batch is duplicated; sampled endpoints remove either three or four original
edges. This verifies the sampled record, not exhaustive two-trade coverage.

A separate native check of the accepted path's intermediate state also passes
pair AC. Thus this observed improvement does not demonstrate crossing a
pair-AC-empty intermediate; it establishes the usefulness of wider proposal
selection. The intermediate native domain/AC result is a diagnostic, not an
independently replayed local proof.
Its independently audited phase-I optimum is instead about 9.11001181.
In the recorded order, the first step raises the true optimized merit by
at least 1.50464476717, exceeding the one-step driver's 0.5 escape allowance;
the second step reaches the improved endpoint. The exact rational comparison
is saved in `20260916_two_trade_intermediate/barrier_audit.json`. This is an
observed merit barrier for that order, not a proof about every alternative path.

Fresh-output reproduction of the final search (after building the native and
CUDA binaries documented in the format guides):

```powershell
rustc -O -C target-cpu=native acceleration/overlap_two_neighbors.rs -o acceleration/build/overlap_two_neighbors.exe
.venv/Scripts/python.exe -B acceleration/guided_two_trade_overlap.py --initial acceleration/results/20260916_coupled_continue/best_candidate.json --out acceleration/build/two_trade_replay --iterations 16 --neighbors 128 --lp-best 6 --lp-random 2 --seed 20260922
```

The saved best remains an excluded fixed assignment. Continue by changing its
overlap edges, strengthening the search objective, or deriving uniform
constraints. No feasible linear completion, full graph or general
nonexistence proof has been found.

The concrete next move family is specified in
`acceleration/ATOMIC_CYCLE_PLAN.md`: exact own-label quotas decompose the
168 edges into 21 perfect matchings. Atomic alternating cycles change three
or four matching edges at once; their raw subfamilies contain 5,320 and
30,870 moves respectively before support/cap rejection. Four-edge cycles
include endpoints beyond the current two-trade reach. This is a derived
implementation plan, not a completed generator or an exhaustive graph search.

This plan has since been implemented and independently checked in the next
continuation. The full results, cache/selection policy, and limitations are
in `GOAL_20260916_ATOMIC_CYCLES.md`. Three pilots do not improve the best
7.332122 assignment. Their new index is
`acceleration/results/20260916_atomic_checkpoint.json`; the earlier global
index below remains a preserved record of the preceding continuation.

The subsequent whole-matching continuation is documented in
`GOAL_20260916_MATCHING_MIP.md`. It implements joint matching/X optimization,
checks all 21 one-coordinate continuous diagnostics, and independently proves
eight conditional same-sign family exclusions. Their union contains exactly
48,313 labeled overlap patterns before partial-cap filtering, because the
eight coordinate families intersect only at the unchanged base K. The other
13 coordinates remain unresolved. This expands exact exclusion coverage
around one assignment; it neither improves the 7.332122 best merit nor
excludes simultaneous changes to multiple coordinates or the full problem.
The original goal remains active and incomplete.

The evidence index for that stage is
`acceleration/results/20260916_matching_checkpoint.json`. It binds the new
model controls, all-coordinate diagnostics, exact family audits, corruption
controls, and the preserved atomic checkpoint. No older index is overwritten.

The next continuation is `GOAL_20260916_WHOLE_MATCHING_SEARCH.md`. Complete
Rust/Python enumeration agrees on74,638 same-sign replacements, and a second
CUDA scoring point per coordinate leads to a strictly improved pair-consistent
seed at7.31624646. The exact improvement is at least0.015875555977470427;
12,558 choices remain after independently checked complete-domain/pair
propagation. Its own integer certificate still excludes the fixed assignment.
The new index `acceleration/results/20260916_whole_matching_search_checkpoint.json`
checks1,815 file hashes and48 direct artifacts, preserving all prior indices.
The goal remains active and incomplete.

The new machine index `acceleration/results/20260916_global_checkpoint.json`
binds all five global/coupled/two-trade runs and the merit-barrier result. Its
builder checked 43 direct artifacts and 2,145 referenced file hashes without
re-running numerical experiments. It records an active, incomplete goal and
the fixed-assignment/finite-search limits. The preceding goal checkpoint is
preserved byte-for-byte.

## Continuation policy

The first CP continuation is [CUDA CP search](GOAL_20260916_CUDA_CP_SEARCH.md).
Matrix-free Rust/CUDA reoptimization is implemented and independently checked.
The whole73,239-proposal family at the7.316246 seed is evaluated on GPU,
2,048 candidates are refined, and64 LPs are independently audited.
Thirty-one strict improvements are verified. The best seed has exact interval
**[5.944366121123388,5.944366121993081]**, improving by at least1.3718803354766993,
and13,424 independently pair-consistent choices. Its positive integer
certificate still excludes that fixed K. No graph or general proof is obtained.
The latest index `acceleration/results/20260916_cp_search_checkpoint.json`
binds2,043 files and36 direct artifacts, preserving all previous indices.

Preserve all prior hash-bound sources and results. Continue guided structural
search or derive uniform constraints; do not return to exhaustive E71-or-lower
enumeration. Keep finite-sample evidence separate from a theorem quantifying
over all possible overlap assignments, and from the entire Conway problem.
Do not create `submission.txt` before independent complete validation.
