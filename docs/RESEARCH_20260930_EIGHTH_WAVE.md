# Eighth resumed milestone, 2026-09-30 JST

Six independently checked claims were added since the [seventh milestone](RESEARCH_20260930_SEVENTH_WAVE.md). They establish a complete matching-pair census, exact local permutation counts, two universal local-test limitations, and a small direct proof for the already excluded fixed Wave154 configuration.

**As of:** 2026-09-29T22:56:38.697702+00:00; source commit `b4cb1ee6a19fdca8d69f95617206d81d051069b8`. [Checkpoint](../acceleration/results/20260930_resume/eighth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_eighth_milestone.yaml); previous report: seventh milestone.

**Verdict:** target resolution UNKNOWN. No independently validated 99-vertex target or general nonexistence proof is available in this repository. No candidate target resolution is under external review. Draft [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is a repository statement, not a worldwide literature verdict.

**Verified changes:** all six records are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-TRIANGLE-ORDERED-MATCHING-PAIR-CENSUS` | Finite ordered-pair action on twelve labelled points only. No fibre interchange, no constraint on or classification of the additional A1--A2 bijection P, no target graph or family exclusion. [Audit](../acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json). |
| `C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION` | Exact positive-core local pair-cap feasibility only; at n12 this is the39vertex principal core, not target completion or a canonical core census. [Audit](../acceleration/results/20260930_independent_review/triangle_core_paircap_theorem/summary.json). |
| `C-TRIANGLE-CORE-LABELLED-P-PAIRCAP-CENSUS` | Fixed standard M0, named fibres, all labelled M1/M2/P choices; exact local39 pair-cap filter only, not P-orbit census or target extensions. [Audit](../acceleration/results/20260930_independent_review/triangle_core_permutation_census_v2/summary.json). |
| `C-FIXED-WAVE154-ROW29-EMPTY-DOMAIN` | Only row29 of the exact fixed labelled Wave154/Q1 partial graph; the claim is a necessary-row obstruction, not an equivalence of this row relaxation with full graph completion. [Audit](../acceleration/results/20260930_independent_review/triangle_wave154_row29_obstruction/summary.json). |
| `C-TRIANGLE39-UNIVERSAL-GRAM-PSD-REDUNDANCY` | All explicitly defined normalized39-vertex cores, including those that violate other target conditions. No prism-free, commutation, automorphism or feasibility premise. [Audit](../acceleration/results/20260930_independent_review/triangle39_gram_sos/summary.json). |
| `C-TRIANGLE-CORE-IDENTITY-P-CONSTRUCTION` | Only a local 3+3n positive graph; at n=12 a 39-vertex necessary-condition witness, no target completion. [Audit](../acceleration/results/20260930_independent_review/triangle_core_identity/summary.json). |

**Work completed:** the finite action on all 10,395 perfect matchings of twelve labels gives 11 first matching types and 3,580 ordered-pair orbits under the 46,080-element centralizer of a fixed matching. Exact orbit sizes cover 108,056,025 labelled ordered matching pairs. Of the 3,580 orbits, 1,701 have trivial joint stabilizer; no target automorphism is inferred.

All 3,580 labelled permutation-domain counts were independently recomputed, and all 3,580 saved local witnesses checked. The saved witnesses use 29 distinct permutation arrays across different matching-pair cases; they are not 3,580 distinct permutations. Every domain is nonempty. Counts range from 176,214,841 to 457,819,549. The exactly defined local labelled-triple population has 40,781,203,938,462,691 cap-compatible triples out of 51,759,008,864,640,000. This is not a population of target graphs or canonical full cores.

The identity permutation supplies a local cap-compatible construction for every triple of perfect matchings of every positive even order. It is not a valid normalization of an arbitrary target permutation. Separately, exact SOS identities show that both target Gram PSD tests automatically pass every explicitly defined 39-vertex core: ranks are 37-c and37, where c is the number of inner components. These statements explain why these local tests cannot settle the remaining binary incidence problem.

The direct Wave154 row29 certificate checks 38 binary entries through 139 nodes, 69 exhaustive splits and70 contradictory leaves. It gives a smaller independently checked explanation of the same fixed-family exclusion already certified in the seventh milestone. It adds no exclusion coverage. Its verifier reconstructs the constraints from the raw partial graph and does not rely on the SAT proof core.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. The matching and permutation populations are explicitly defined finite local universes. Their fractions must not be reported as fractions of Conway-99 solved. No unrestricted branch is closed. Ledger population: 103 claims, 101 VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Best result:** exact structural limits on two proposed core filters, complete finite local counts, and a139-node direct conditional proof. There is no full target witness, new general exclusion, or target-wide numerical bound.

**Problems:** the initial matching census completed its mathematical stages but failed while formatting output paths; its original artifacts and byte-identical corrected stages are preserved. The first permutation recount wrapper rejected a mismatched status string before counting; its corrected separately frozen version completed. Prior archive material already contains the related36-factor Gram mechanism, so no novelty claim or repeated exhaustive PSD search is made. Additional Q1 scouts and the new joint-factor encoding belong to the following wave and are outside these six claims.

**Execution:** the six recorded claims are complete and required no new SAT solver attempt. A fresh native-process observation at 2026-09-29T22:56:39.027312+00:00 returned `CADICAL_PROCESS_OBSERVED`. See its raw receipt for any separately running next-wave solver; this saved report is not a live status promise. The user's continuation instruction remains active.

**Next experiment:** solve the independently gated compact joint binary-incidence model for the fixed39core with both unknown factor blocks free, then independently check the raw factor or complete proof. This is broader than fixing one Q1 factor and remains conditional on the chosen core.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/b4cb1ee6a19fdca8d69f95617206d81d051069b8), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact catalog](../acceleration/results/20260930_eighth_artifact_packaging/catalog.json), [reproduction guide](REPRODUCING_20260930_EIGHTH_WAVE.md). PUBLIC pointers require exact immutable publication confirmation.
