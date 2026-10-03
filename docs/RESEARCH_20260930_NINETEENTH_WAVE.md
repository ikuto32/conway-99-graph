# Nineteenth resumed milestone, 2026-09-30 JST

Ten independently checked claims were added since the [eighteenth milestone](RESEARCH_20260930_EIGHTEENTH_WAVE.md). Exact phase arguments exclude four specified balanced parity assignments and give eleven overlapping exclusions that leave some groups free. No full factor or target graph was found.

**As of:** 2026-09-30T05:26:16.570789+00:00; source commit `75243dc84ee6c37852a62f0935e45562094fe3ca`. [Checkpoint](../acceleration/results/20260930_resume/nineteenth_milestone_checkpoint.json), [frozen ledger](../acceleration/results/20260930_resume/claims_at_nineteenth_milestone.yaml); previous report: eighteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
| `C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-LIFT-RATIONAL-PRIMAL` r1 | One exact rational point in one specified continuous selected-parity Gram relaxation; not an integral factor. [Evidence](../acceleration/results/20260930_independent_review/hadamard_support_cut_lift_primal/summary.json). |
| `C-FIXED-HADAMARD-SECOND-PARITY-GF3-PHASE-SCREEN` r1 | Only this second selected balanced parity branch; outside-column caps are not needed for this exclusion, residualD absent. [Evidence](../acceleration/results/20260930_independent_review/hadamard_f3_phase_obstruction/summary.json). |
| `C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY` r1 | General necessary conditional theorem for this balanced fixed-support family. No assertion of global phase sufficiency or any family exclusion. [Evidence](../acceleration/results/20260930_independent_review/hadamard_general_f3_phase_necessity/summary.json). |
| `C-FIXED-HADAMARD-FOURTEEN-PATTERN-PHASE-EXCLUSION` r1 | The exact14group-pattern partial assignment in verified_nogood.json; this is broader than the single20pattern witness but excludes neither allbalancedfactors on the support nor any unrestrictedtarget. [Evidence](../acceleration/results/20260930_independent_review/hadamard_phase_premise_subset/summary.json). |
| `C-FIXED-HADAMARD-TWELVE-ORDER-PHASE-PREMISE-COLLECTION` r1 | Only the finite hash-bound collection of partial assignments in unique_clauses.json. Their excluded parity families overlap; no summed graph/search coverage or global minimum is claimed. [Evidence](../acceleration/results/20260930_independent_review/hadamard_phase_premise_orders/summary.json). |
| `C-FIXED-HADAMARD-BALANCED-PHASE-MATRIX-FORM` r1 | Exact fixed-support conditional algebra; neither universal rank119 nor any family exclusion, full factor or target construction is asserted. [Evidence](../acceleration/results/20260930_independent_review/balanced_phase_matrix_form_v2/summary.json). |
| `C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-PROJECTIONS` r1 | Three specified parity projections on the single frozen six-prism Hadamard support; no full Gram factor or graph. [Evidence](../acceleration/results/20260930_independent_review/hadamard_parity_phase_batch_outcome/summary.json). |
| `C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-LOCAL-PHASE-EXCLUSIONS` r1 | Exactly two specified balanced fixed-support parity branches; not the entire support, any core, or the unrestricted target. [Evidence](../acceleration/results/20260930_independent_review/hadamard_parity_phase_batch_outcome/summary.json). |
| `C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-LINEAR-SURVIVOR` r1 | One specified linear necessary-condition screen, with its72 declared individual rejection functionals. [Evidence](../acceleration/results/20260930_independent_review/hadamard_parity_phase_batch_outcome/summary.json). |
| `C-FIXED-HADAMARD-PARITY-PHASE-BATCH01-CASE01-COMPLETE-PHASE-EXCLUSION` r1 | One exact case01 parity assignment on one frozen six-prism Hadamard support; no complete support/core/target exclusion. [Evidence](../acceleration/results/20260930_independent_review/hadamard_phase_case01_enumeration/summary.json). |

**Work completed:** the second parity assignment's 240-variable rational lift has a checked uniform primal, but exact GF(3) phase equations forbid its integer coloring lift. A general balanced-phase necessity theorem and a matrix formulation were independently derived. The all-mixed signed-Gram identity does not establish universal phase rank.

One greedy premise reduction keeps fourteen of twenty patterns fixed. Twelve recorded reduction orders produce eleven distinct overlapping clauses, with fourteen to seventeen fixed patterns. No global minimum or union size is established.

The finite sampler attempted four native calls: three distinct SAT projections were completely checked, followed by one UNKNOWN outcome at the conflict setting. Two projections have literal phase contradiction certificates. The third has rank113/nullity7 and no individually vanishing mixed difference. Independent enumeration of all2,187 vectors then rejects every vector:1,611 first fail mixed-group distinctness and576 first fail constant-group multiplicity. No research vector reaches the pair, full-Gram or outside-cap stages. The earlier linear-screen and projection claims remain valid within their narrower scopes.

**Coverage:** the four newly excluded complete assignments are distinct; the reduced pattern families overlap and are not added as disjoint graph counts. Zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger has188 claims:186 VERIFIED/CLEAR and two CANDIDATE/CLEAR. These are claim counts, not a fraction of Conway99 solved.

**Best result:** exact independently checkable phase exclusions, including one exhaustive seven-dimensional finite phase universe and reductions fixing as few as fourteen local patterns. Balance and the single six-prism support remain extra restrictions. No comparable target-wide bound follows.

**Problems:** the fourth native attempt was UNKNOWN. All four deferred batch traces are now MISSING despite successful historical stat/hash receipts; the later failed archive and independent availability observations are preserved. Their loss cause is UNKNOWN. No UNSAT proof or mathematical exclusion depends on those traces. The matrix checker first used an incorrect metadata key, and the finite enumerator had two setup failures before evaluating any vectors. All original sources/failures and corrected versions remain available. The prepared second-branch lift CNF was cancelled before solving after the exact phase obstruction.

**Execution:** all four batch attempts and all finite enumerations completed. Native census at 2026-09-30T05:26:16.590957+00:00: `NO_CADICAL_PROCESS_OBSERVED`. The later oriented-triple pilot and grouped full-Gram formulation belong to the next cohort. No ongoing solver work is implied by this report.

**Next experiment:** Independently audit and then run the grouped full balanced-Gram encoding on this fixed support, covering constant and mixed local groups together; test any decoded factor against exact Gram and outside-column conditions before residual completion.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/75243dc84ee6c37852a62f0935e45562094fe3ca), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_nineteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_NINETEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
