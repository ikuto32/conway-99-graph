# Thirteenth resumed milestone, 2026-09-30 JST

Four verified claims were added since the [twelfth milestone](RESEARCH_20260930_TWELFTH_WAVE.md): a nonempty independent validation fixture, a necessary residual screen, and two coordinate relabelling reductions. Both normalized SAT attempts ended UNKNOWN.

**As of:** 2026-09-30T01:03:29.737774+00:00; source commit `b9de2985adea787b67017df5d0d757755bc22c9c`. [Checkpoint](../acceleration/results/20260930_resume/thirteenth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_thirteenth_milestone.yaml); previous report: twelfth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all four claims are revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL` | A nonempty positive verification fixture of a different known parameter family; not Conway99 evidence. [Audit](../acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json). |
| `C-DYNAMIC-TRIANGLE-RESIDUAL-SCREEN-NECESSITY` | Necessary local completion bounds for an authenticated supplied factor; no research factor or exclusion produced here. [Audit](../acceleration/results/20260930_independent_review/dynamic_residual_screen/summary.json). |
| `C-SIX-PRISM-FIRST-CHOICE-NORMALIZATION-CNF` | One fixed six-prism abstract Gram-factor family; finite specified relabelling group, not full automorphism-group census. [Audit](../acceleration/results/20260930_independent_review/prism_first_choice_normalization/summary.json). |
| `C-VARIABLE-CORE-M1-ELEVEN-ORBIT-NORMALIZATION` | Universal necessary arbitrary-core factor model after harmless labels; SAT is not a completed target graph. [Audit](../acceleration/results/20260930_independent_review/variable_core_m1_orbits/summary.json). |

**Work completed:** the 243-vertex raw graph passed all 59,049 full adjacency-square entries, its triangle-factor/residual block equations and seven corruption controls. It is a different-parameter validation fixture. The dynamic screen passed independent exact edge/quota checks, including this nonempty fixture; no research factor was supplied or excluded.

The six-prism reduction checked all 384 relabellings, 96 first-choice transports, 207,360 equation images and 147,456 compositions. The arbitrary-core reduction checked all 10,395 M1 transports and 623,700 C0 column images to eleven representatives. These are distinct finite populations, not counts of excluded graphs. M2 and P stay arbitrary in the latter model. Neither reduction assumes an automorphism of a target graph. Full native-assignment and raw-factor checking paths were separately calibrated.

| Completed native attempt | Result | Observed conflicts | Wrapper seconds |
| --- | --- | ---: | ---: |
| variable_core_m1_orbits | UNKNOWN_CONFLICT_LIMIT | 5000003 | 788.422 |
| prism_first_choice | UNKNOWN_TIMEOUT | 2137390 | 900.046 |

Each had one attempt with 900 seconds and five million configured conflicts, plus memory/file guards. Independent engineering audits authenticated exact inputs, logs, receipts and all retained incomplete trace bytes, with six altered-outcome controls per attempt. No trace is a complete checked UNSAT proof. Different formulas and stopping conditions do not establish a performance comparison.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or fixed-core family was excluded. Ledger population: 130 claims, 128 VERIFIED/CLEAR and two CANDIDATE/CLEAR.

**Best result:** independently checked relabelling reductions preserve their stated model coverage, and nonempty controls strengthen residual validation. No complete target factor, target graph or target-wide mathematical bound was obtained in this cohort.

**Problems:** both searches are UNKNOWN. Preserved failures include the initial fixture syntax error, the unavailable-psutil preflight import, and two publication-catalog bookkeeping omissions. Corrected runs and explicit control exceptions are recorded without overwriting failed sources. The first-choice raw formula has public gzip recovery; the two incomplete traces remain LOCAL_ONLY. The GPU and full ordered-pair work belong to later cohorts and are excluded from these claim totals and run counts.

**Execution:** both named attempts completed. Fresh observation at 2026-09-30T01:03:30.175128+00:00: `CADICAL_PROCESS_OBSERVED`. Exact command and process logs are in the checkpoint; any observed ordered-pair attempt is separate. The user's continuation instruction remains active.

**Next experiment:** test the independently gated 3,580 ordered-matching-pair normalization while leaving P arbitrary, and continue independently checked permutation construction attempts. A factor would still require residual completion and full exact graph verification.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/b9de2985adea787b67017df5d0d757755bc22c9c), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_thirteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_THIRTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
