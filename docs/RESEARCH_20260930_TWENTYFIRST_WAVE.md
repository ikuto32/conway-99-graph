# Twenty-first resumed milestone, 2026-09-30 JST

Twelve independently checked claims were added since the [twentieth milestone](RESEARCH_20260930_TWENTIETH_WAVE.md). The fixed support requires at least four unbalanced groups and forbids exactly five. One exactly-four profile is excluded by a complete proof; six-group marginal screening leaves six group subsets with984 labelled marginal profiles. No full factor or target resolution follows.

**As of:** 2026-09-30T06:43:31.242907+00:00; source commit 18ca1122abb0b8eee909588654310b2de3116c25. [Checkpoint](../acceleration/results/20260930_resume/twentyfirst_milestone_checkpoint.json), [frozen ledger](../acceleration/results/20260930_resume/claims_at_twentyfirst_milestone.yaml); previous report: twentieth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
| C-FIXED-HADAMARD-AT-MOST-THREE-EXCEPTIONS-IMPLIES-BALANCED r1 | Universal conditional implication for factors on this literal fixed support; it does not assume balance or a target automorphism. [Evidence](../acceleration/results/20260930_independent_review/hadamard_few_exception_marginals/summary.json). |
| C-FIXED-HADAMARD-AT-MOST-THREE-UNBALANCED-GROUPS-EXCLUSION r1 | Exclusion of the at-most-three-unbalanced-group subfamily on this one fixed support, using the separately verified balanced-family exclusion. [Evidence](../acceleration/results/20260930_independent_review/hadamard_few_exception_marginals/summary.json). |
| C-FIXED-HADAMARD-FOUR-GROUP-CIRCUIT-NECESSITY r1 | Complete finite support census and a necessary condition for exactly four exceptional groups only; none of the14retained quartets is claimed realizable. [Evidence](../acceleration/results/20260930_independent_review/hadamard_four_group_circuits/summary.json). |
| C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN r1 | 108 explicitly labelled necessary profiles for exactly four exceptional groups in the fixed-support Gram-plus-column-cap family; 96 outcomes remain unresolved. [Evidence](../acceleration/results/20260930_independent_review/hadamard_four_group_local_screen/summary.json). |
| C-FIXED-HADAMARD-FOUR-EXCEPTION-GLOBAL-FIBRE-NORMALIZATION r1 | Normalization only of the exactly-four-exception Gram-plus-outside-column-cap family on this literal fixed support. No nonempty screen outcome is asserted feasible. [Evidence](../acceleration/results/20260930_independent_review/hadamard_fibre_profile_orbits/summary.json). |
| C-FIXED-HADAMARD-EXACTLY-FIVE-UNBALANCED-GROUPS-EXCLUSION r1 | Only the exactly-five-exception subfamily on one literal fixed support. The proof uses Gram marginals and integer counts, without outside-column caps or a balanced-family UNSAT premise. [Evidence](../acceleration/results/20260930_independent_review/five_unbalanced_groups/summary.json). |
| C-FIXED-HADAMARD-FOUR-EXCEPTION-PARTIAL12-CENSUS r1 | A complete finite census only for the recorded intervals and partial twelve-column objects; case35 beyond its prefix and60 other profiles remain UNKNOWN. [Evidence](../acceleration/results/20260930_independent_review/four_group_joint_v2/summary.json). |
| C-FIXED-HADAMARD-FIRST-PARTIAL12-RESIDUAL-PSD r1 | This one hash-bound partial object and its exact residual matrix only. [Evidence](../acceleration/results/20260930_independent_review/first_partial12_psd/summary.json). |
| C-FIXED-HADAMARD-SIX-EXCEPTION-KERNEL-CENSUS r1 | Complete finite sextet census and necessary exact-six-exception reduction for one fixed support; the nine retained subsets remain unresolved. [Evidence](../acceleration/results/20260930_independent_review/hadamard_six_exception_census/summary.json). |
| C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING r1 | Only this fixed support and literal profile: exceptional groups0,7,9,19, circuit signs1,-1,-1,1, common coordinates2,4, deviations[-1,0,1] and[1,0,-1]. Cross-group column caps and residualD are omitted. [Evidence](../acceleration/results/20260930_independent_review/hadamard_case0_profile_cnf/summary.json). |
| C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-EXCLUSION r1 | Only the literal case0 count profile on this fixed support; no orbit transfer, other profile or whole-support conclusion. [Evidence](../acceleration/results/20260930_independent_review/hadamard_case0_profile_unsat/summary.json). |
| C-FIXED-HADAMARD-SIX-EXCEPTION-INTEGER-MARGINAL-CENSUS r1 | Complete necessary marginal relaxation on nine fixed sextets; six positive marginal cases remain unresolved for local triples/full factors. [Evidence](../acceleration/results/20260930_independent_review/hadamard_six_rank4_profiles/summary.json). |

**Work completed:** all4,845 group quartets were checked. Fourteen necessary quartets yield108 labelled profiles; the complete local-cap screen excludes12 and leaves96 nonempty pairwise fixed points. Global fibre relabelling gives18 size-six orbits,16 with nonempty screens, without assuming any target automorphism.

The bounded joint search completed35 profiles and one partial prefix, leaving60 unattempted. Independent checking reconstructed every one of7,335,060 saved tuples over1,263 intervals and all36 first raw witnesses. The first residual Gram is exactly PSD with rank29/nullity7. None supplies the remaining48 columns.

All38,760 six-group subsets were checked:35,587 have rank6,3,164 rank5 and nine rank4. Exact integer marginal arguments exclude the rank5/6 cases. Direct independent enumeration of121,869 coordinate-profile sequences checks all108 DP layers and excludes three rank4 cases, leaving six with984 labelled marginal profiles. Marginal feasibility does not establish quadratic Gram feasibility.

The single native case0 attempt used10,564 variables and187,408 clauses and returned UNSAT after12,232 conflicts,1.82 native wall seconds and1.08 CPU seconds. Its complete9,139,513-byte trace was independently replayed against the exact CNF. This is a literal-profile exclusion, with within-group caps and no cross-group cap or residualD encoding. Any relabelled transfer uses the separately checked normalization.

**Coverage:** zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The frozen ledger has206 claims:203 VERIFIED/CLEAR,2 CANDIDATE/CLEAR and1 REFUTED/CLEAR. Counts of profiles, subsets and partial objects are different populations and are not summed.

**Best result:** exact scoped nonexistence results for small unbalanced-group counts and one full-Gram profile, with complete proof and finite certificates. The unrestricted target remains open in this repository.

**Problems:** the first joint enumerator's positive control used the research diagonal cap instead of the243-fixture diagonal. It failed before research enumeration; the corrected version and original failure are preserved. The120-second enumeration checkpoint is deliberately incomplete. The large raw case0 model remains LOCAL_ONLY at its raw path with public lossless recovery; the original checker executable is also LOCAL_ONLY with public source/build provenance. Earlier missing traces and private-process omissions remain unchanged.

**Execution:** the case0 native call and proof replay completed. Targeted census at 2026-09-30T06:43:31.265917+00:00: NO_CADICAL_PROCESS_OBSERVED. The fifteen-case campaign is outside this checkpoint; no continuing solver execution is implied.

**Next experiment:** Independently gate and run the fifteen remaining full-Gram four-exception profile representatives, one attempt per formula; preserve and independently check every outcome and complete proof.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/18ca1122abb0b8eee909588654310b2de3116c25), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_twentyfirst_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTYFIRST_WAVE.md). Immutable publication pointers follow remote confirmation.
