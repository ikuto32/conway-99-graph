# Fourteenth resumed milestone, 2026-09-30 JST

Eight verified claims were added since the [thirteenth milestone](RESEARCH_20260930_THIRTEENTH_WAVE.md): finite GPU calibration and saved-state results, a public-checkpoint repair and its diagnosed failure, ordered-matching-pair normalization, a finite failed modular route, and the six-prism column-cap encoding. No target resolution or exclusion was obtained.

**As of:** 2026-09-30T01:46:37.221422+00:00; source commit `22fc0ea2f81faa791ee99daf456a3c9785c55dc0`. [Checkpoint](../acceleration/results/20260930_resume/fourteenth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_fourteenth_milestone.yaml); previous report: thirteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all eight claims are revision1. Verification applies only to each exact statement and scope.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-FACTOR-PERMUTATION-ANNEALER-CALIBRATION` | Finite CPU/GPU/native split calibration only; this does not establish the v2 Python public --resume path, whose two subsequent attempts failed before native invocation. [Evidence](../acceleration/results/20260930_independent_review/factor_permutation_annealer_bound/summary.json). |
| `C-FACTOR-PERMUTATION-ANNEALER-PILOT-SAVED-STATES` | Saved-state correctness in two fixed n12 core domains;768 checkpoint-current and768 checkpoint-best scores also recomputed, while786432 saved proposal records are counted without campaign transition replay. [Evidence](../acceleration/results/20260930_independent_review/factor_annealer_pilot/summary.json). |
| `C-FACTOR-PERMUTATION-PUBLIC-JSON-RESUME-CALIBRATION` | Exact source delta and bounded public calibration-mode disk-resume through the same run_chunks body; unchanged native algorithm retains its earlier finite gate, and future research outcomes require separate checks. [Evidence](../acceleration/results/20260930_independent_review/factor_resume_v3/summary.json). |
| `C-FACTOR-PERMUTATION-V2-PUBLIC-RESUME-FAILURE` | Exactly the two recorded v2 attempts and their two skipped dependent stages; a positive engineering failure finding, not a refutation of an unrecorded universal claim or the finite native calibration. [Evidence](../acceleration/results/20260930_independent_review/factor_resume_v3/summary.json). |
| `C-VARIABLE-CORE-ORDERED-MATCHING-PAIR-ORBIT-NORMALIZATION` | Universal normalization of the audited necessary arbitrary-core factor model by complete ordered matching-pair relabelling. Every target supplies a normalized-model solution under the pinned triangle-normalization premise. This is not a sufficient graph construction and excludes no target or factor. [Evidence](../acceleration/results/20260930_independent_review/variable_core_pair_orbits_v2/summary.json). |
| `C-FINITE-243-MODULAR-KERNEL-PERTURBATION-ROUTE` | Exactly the256 deterministically reconstructed finite-field perturbations of one pinned SRG243 fixture,128 in each field, and agreement with the saved finite summaries. No unrestricted-target coverage or universal redundancy implication. [Evidence](../acceleration/results/20260930_independent_review/triangle_modular_kernel_finite/summary.json). |
| `C-SIX-PRISM-COMPLETE-COLUMN-CAP-ENCODING` | Fixed identity-cross six-prism core only; no arbitrary-core containment, target automorphism or residual completion. [Evidence](../acceleration/results/20260930_independent_review/prism_column_caps/summary.json). |
| `C-FACTOR-PERMUTATION-ANNEALER-COOLING-SAVED-STATES` | Saved-state scores/domain and actual checkpoint carry across four cooling stages in two fixed cores, not a factor construction or target exclusion. [Evidence](../acceleration/results/20260930_independent_review/factor_annealer_cooling_v3/claim_binding.json). |

**Work completed:** the ordered-pair reduction checks114,345 second-stage matching transports, covering the108,056,025 labelled ordered matching pairs through the separately checked first-stage normalization. It leaves P arbitrary and assumes no target automorphism. Its114,484-variable,561,121-clause model remains a necessary factor problem without residual D. The fixed six-prism model adds all required Y-column overlap caps and has247,320 variables and920,401 clauses. Independent full decoded-object checking paths were calibrated before either native run.

| Completed native attempt | Result | Observed conflicts | Wrapper seconds |
| --- | --- | ---: | ---: |
| variable_core_pair_orbits | UNKNOWN_CONFLICT_LIMIT | 5000002 | 872.547 |
| prism_column_caps | UNKNOWN_TIMEOUT | 2374985 | 900.031 |

Each had one attempt with900 seconds and five million configured conflicts plus memory/file guards. Independent execution audits bind inputs, receipts, logs and the complete retained incomplete trace bytes. Neither trace is a checked UNSAT certificate. Different formulas and stops do not establish a performance comparison.

The initial GPU pilot completed6 cases and saved786,432 proposal records. Independent checking covered48 chunk-best,96 final-current and96 final-best raw states, plus all768 current and768 best checkpoint scores. The first cooling attempt failed in2 stages before any GPU proposals and skipped2 dependent stages: Python tuples did not match lists restored from JSON. The corrected public-resume path passed fresh independent calibration. Corrected cooling completed4 stages and1,048,576 new proposal records across32 continuing chains, with64 chunk-best,64 stage-final-current and64 stage-final-best objects and all1,024 current and1,024 best checkpoint scores independently checked. These overlapping stage populations are not summed; individual campaign transitions were not replayed.

The finite modular route independently reconstructed128 trials over each of GF(2) and GF(3) on the243-vertex fixture. All256 retained the tested mixed-kernel compatibility. This is neither a universal redundancy theorem nor a target exclusion. Original successful perturbation matrices were not saved; the independent reconstruction preserves new vectors and hashes without claiming to authenticate absent originals.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or fixed core was excluded. The ledger contains138 claims:136 VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Best result:** under `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1`, the exact saved minimum decreased164→134→124 for shift6 and184→146→142 for six-prism. This objective minimizes the sum of squared residuals of three cross-fibre Gram blocks on their fixed permutation domains. These positive heuristic-search scores are not mathematical bounds. Even objective zero would require further constraints and residual completion before yielding a target graph.

**Problems:** both native attempts ended UNKNOWN; no factor was found. Preserved failures include the original CUDA compile error, actual public-resume mismatch, two cap-builder preparation failures, the first pair-audit indexing error, and catalog control-binding omissions. The original premature PUBLIC metadata is retained with an explicit correction. Native binaries and incomplete traces remain LOCAL_ONLY. Large GPU records and cap inputs have lossless public recovery packages after publication. The GF2 conditional lemma and connected-core portfolio belong to a later cohort and are excluded from these totals.

**Execution:** cohort searches completed. Fresh native process observation at 2026-09-30T01:46:37.658363+00:00: `CADICAL_PROCESS_OBSERVED`. Exact process logs are saved in the checkpoint; any observed connected-core run belongs to a later cohort. The user's continuation instruction remains active.

**Next experiment:** execute the independently gated necessary-factor SAT instances for the four selected connected identity-P cores. A SAT object requires complete independent clause/raw-factor checks and then residual completion; checked UNSAT would concern only its fixed core.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/22fc0ea2f81faa791ee99daf456a3c9785c55dc0), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_fourteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_FOURTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
