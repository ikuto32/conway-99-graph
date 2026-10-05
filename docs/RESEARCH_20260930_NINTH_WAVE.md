# Ninth resumed milestone, 2026-09-30 JST

Seven independently checked claims were added since the [eighth milestone](RESEARCH_20260930_EIGHTH_WAVE.md). Three new fixed factors are exactly excluded; a component-kernel argument gives short obstructions for all five saved factors. Two broader binary-factor encodings are verified, but both bounded native attempts ended UNKNOWN.

**As of:** 2026-09-29T23:15:31.463987+00:00; source commit `4858e79ca64d278a0ec45767d94ec48617682549`. [Checkpoint](../acceleration/results/20260930_resume/ninth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_ninth_milestone.yaml); previous report: eighth milestone.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated 99-vertex target graph nor a general nonexistence proof. No candidate target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all seven records are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-FIXED-TRIANGLE-THREE-Q1-GRAM-FACTORS` | Three finite binary factors for the specified M0=M1=M2 and P=shift6 core; no third incidence cell or target extension. [Audit](../acceleration/results/20260930_independent_review/triangle_q1_binary_scout/summary.json). |
| `C-FIXED-TRIANGLE-Q1-FIVE-COORDINATE-ORBITS` | Only this explicitly defined complete384-element coordinate group and five raw factors; no classification of all factors or arbitrary target isomorphisms. [Audit](../acceleration/results/20260930_independent_review/triangle_q1_binary_scout/summary.json). |
| `C-FIXED-TRIANGLE-THREE-Q1-ROW27-EXCLUSIONS` | Three raw fixed configurations, each independently assembled without propagation; no exclusion of all Q1 factors or of the fixed core. [Audit](../acceleration/results/20260930_independent_review/triangle_q1_binary_scout/summary.json). |
| `C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING` | One fixed39vertex core; C1 and C2 entirely free, no residual D or full target graph encoded. [Audit](../acceleration/results/20260930_independent_review/triangle_joint_factor_cnf/summary.json). |
| `C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE` | One fixed39core Gram; no unrestricted target coverage, no residual D; five specific Q1 choices only. [Audit](../acceleration/results/20260930_independent_review/triangle_factor_components/summary.json). |
| `C-FIXED-TRIANGLE-COMPONENT-STRENGTHENED-CNF` | One fixed39core Gram; no unrestricted target coverage, no residual D; five specific Q1 choices only. [Audit](../acceleration/results/20260930_independent_review/triangle_factor_components/summary.json). |
| `C-FIVE-FIXED-TRIANGLE-Q1-COMPONENT-OVERFLOW-EXCLUSIONS` | One fixed39core Gram; no unrestricted target coverage, no residual D; five specific Q1 choices only. [Audit](../acceleration/results/20260930_independent_review/triangle_factor_components/summary.json). |

**Work completed:** three new saved binary24x60 factors pass all1,728 prescribed Gram-entry checks and exact margins. Together with the two freshly checked archived factors, they occupy five disjoint orbits under the specified384 coordinate relabelings. This is neither general graph nonisomorphism nor a census of all factors. Three complete row27 obstruction trees contain655 checked nodes,326 exhaustive splits and329 contradictions. They exclude precisely those three fixed configurations.

For the chosen39vertex core, exact component-kernel identities force every completed36x60 factor column to contain two entries in each of three components. The five saved two-cell factors have respectively3,1,1,1,1 overflow columns, so none extends even by a nonnegative third block. These shorter proofs overlap the existing fixed exclusions and add no further coverage.

The base factor CNF has58,860 variables and203,748 clauses. Its strengthened equivalent has61,296 variables and212,580 clauses, adding180 necessary component equations. Each allows both unknown incidence blocks to vary; neither encodes the residual60vertex graph. Independent encoding checks and separately calibrated complete-factor checkers preceded the native attempts. No valid36x60 factor with the actual research Gram is known; synthetic positive controls are labelled accordingly.

**Execution:** two distinct inputs each received one native attempt, both completed UNKNOWN with exit0. The configured conflict limit was1,000,000; the logs report 1,000,000 and 1,000,002 conflicts respectively. The second count exceeds the configured limit by two and is preserved as observed. Wrapper wall times are 69.594s and 81.453s; these are single attempts on different formulas, not a controlled speed comparison. The incomplete traces are574,434,634 and646,423,799 bytes and remain LOCAL_ONLY. Neither is an UNSAT certificate. [Independent run audit](../acceleration/results/20260930_independent_review/triangle_factor_two_unknown_runs/summary.json). A fresh observation at 2026-09-29T23:15:31.796590+00:00 returned `NO_CADICAL_PROCESS_OBSERVED`; the checkpoint includes its exact command and raw logs.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch is closed. The saved five-factor population is not exhaustive. Ledger population: 110 claims, 108 VERIFIED/CLEAR and2 CANDIDATE/CLEAR. No claim in this milestone establishes fixed-core nonexistence.

**Best result:** exact short conditional obstructions and independently verified broader factor encodings. No target-level bound or graph was obtained.

**Problems:** the first factor-checker corruption fixture accidentally shared mutable row objects. That calibration failure and its separately frozen correction are retained. New row-wrapper controls were added after the scout, with their timing disclosed. The scout's512,000 annealing swaps and final G01-only integer score24 are unreplayed heuristic telemetry, not certified search coverage. No exact factor was found by that heuristic batch. The UNKNOWN solver traces are retained locally, while exact inputs, logs and receipts are public payload candidates.

**Next experiment:** independently gate and solve the necessary Q1-only binary factor projection with component-capacity inequalities. A satisfying factor would establish only that projection; UNSAT requires full proof replay and would remain conditional on this core. Residual-D completion conditions are being investigated separately and are outside these seven claims. The user's continuation instruction remains active.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/4858e79ca64d278a0ec45767d94ec48617682549), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact catalog](../acceleration/results/20260930_ninth_artifact_packaging/catalog.json), [reproduction guide](REPRODUCING_20260930_NINTH_WAVE.md). Immutable PUBLIC pointers are set only after remote publication confirmation.
