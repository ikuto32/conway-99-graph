# Eighteenth resumed milestone, 2026-09-30 JST

Seven independently checked claims were added since the [seventeenth milestone](RESEARCH_20260930_SEVENTEENTH_WAVE.md). Exact integer evidence excludes one selected balanced-parity lift. Sixty general necessary conditions reject that assignment, and a second independently checked parity assignment satisfies the strengthened formula. The separate direct MIP attempt ended UNKNOWN without a valid incumbent.

**As of:** 2026-09-30T04:37:38.926307+00:00; source commit `81320d3cf74339d2ffb1e671f51f0865218ac161`. [Checkpoint](../acceleration/results/20260930_resume/eighteenth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_eighteenth_milestone.yaml); previous report: seventeenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex graph or general nonexistence proof. No target resolution is under external review; this is not a worldwide literature verdict. Draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
| `C-FIXED-HADAMARD-SIX-PRISM-BINARY-MIP-ENCODING` r1 | One exact frozen six-prism support L and its 90 colorings per column. This is an exact binary linear encoding equivalence, not a numerical feasibility result or target-level coverage claim. [Evidence](../acceleration/results/20260930_independent_review/hadamard_prism_binary_mip_calibration/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION` r1 | Necessary projection only for the balanced fixed-support family WITH outside-column caps; SAT is not a factor and unbalanced factors remain outside its coverage. [Evidence](../acceleration/results/20260930_independent_review/hadamard_balanced_parity/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-NONCYCLIC-PARITY-PROJECTION-WITNESS` r1 | Only a witness for the necessary parity projection; no local-colouring lift, full36x60factor, residual graph, fixed-support feasibility or target graph is asserted. [Evidence](../acceleration/results/20260930_independent_review/hadamard_balanced_parity_sat_v2/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-FIRST-PARITY-LIFT-EXCLUSION` r1 | Only this one fully specified selected-parity colouring branch on one fixed support. No other parity assignment, unbalanced factor, whole support, core or Conway99 exclusion. [Evidence](../acceleration/results/20260930_independent_review/balanced_lift_zero_rows/summary.json). |
| `C-FIXED-HADAMARD-BALANCED-PARITY-CONSTANT-GROUP-NECESSITY` r1 | All balanced parity branches on one exact fixed support, not arbitrary fixed-support factors. [Evidence](../acceleration/results/20260930_independent_review/hadamard_balanced_parity_cuts/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-PROJECTION` r1 | Necessary projection only for the balanced-triplet fixed-support family with outside-column caps; no full factor equivalence. [Evidence](../acceleration/results/20260930_independent_review/hadamard_parity_support_cuts_sat_outcome/claim_bindings.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS` r1 | One exact parity-projection witness on the fixed support; not a full Gram factor or graph. [Evidence](../acceleration/results/20260930_independent_review/hadamard_parity_support_cuts_sat_outcome/claim_bindings.json). |

**Work completed:** two distinct parity formulas were each attempted once and each produced one completely checked projection witness. Both have 520 variables; the formulas have 4,481 and 4,541 clauses respectively. The first witness has sixteen mixed and four constant groups. The second has twenty mixed groups and sixty disagreement counts equal to three. Neither witness is a full Gram factor, cap-feasible factor or graph.

The first witness's exact lift relaxation has 312 variables and 560 equations. Six required rows have identically zero coefficients. An independent checker rebuilt all domains and coefficients and verified the literal dual with RHS product -1 and all column products zero. This excludes exactly one selected parity branch. No LP or SAT run was needed for that exclusion. The separately proved sixty necessary conditions apply to balanced factors on the same fixed support; balance remains an additional assumption.

The direct binary MIP encoding has 5,400 variables and 766 rows. Its one completed attempt reached its cooperative allocation without a valid incumbent, Gram object or lazy cut. The saved 120.25-second wrapper time explicitly exceeds the 120-second allocation by 0.25 seconds. No numerical status is a certificate or exclusion.

**Coverage:** one selected balanced-parity branch excluded; zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains 178 claims: 176 VERIFIED/CLEAR and two CANDIDATE/CLEAR. Counts of native SAT calls, MIP calls, failed builds and skipped LP work are separate populations.

**Best result:** an exact selected-branch obstruction, a general necessary cut for the balanced fixed-support family, and a new checked parity projection that survives all sixty cuts. No full factor or comparable target-wide bound was obtained.

**Problems:** the direct MIP run was inconclusive. The first parity object check failed on hexadecimal metadata formatting; the failed source, corrected checker, independent delta audit and new calibration are preserved. The initial selected-lift CNF build stopped at an empty-counter assertion; its partial output is retained, and the separate exact zero-row proof supplies the exclusion. The planned numerical LP was skipped before execution. The old parity witness remains valid for its original formula.

**Execution:** both cohort native attempts and the direct MIP call completed. Fresh native observation at 2026-09-30T04:37:39.440449+00:00: `NO_CADICAL_PROCESS_OBSERVED`. Later second-witness lift work is a separate cohort and requires its own receipts. The user's continuation instruction remains active.

**Next experiment:** Independently check the second selected parity branch through its exact balanced-lift matrix and affine phase equations over GF(3); if an obstruction survives review, derive a broader sound phase-screening rule. This later work belongs to the nineteenth cohort.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/81320d3cf74339d2ffb1e671f51f0865218ac161), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_eighteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_EIGHTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
