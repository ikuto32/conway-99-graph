# Seventeenth resumed milestone, 2026-09-30 JST

Six independently checked claims were added since the [sixteenth milestone](RESEARCH_20260930_SIXTEENTH_WAVE.md). A complete replayable proof excludes one cyclic coloring subclass of the remaining fixed Hadamard support. A broader model without the cyclic restriction ended UNKNOWN. Exact marginal and local-triple checks establish why the tested projections do not justify imposing that restriction.

**As of:** 2026-09-30T03:55:44.207113+00:00; source commit `bbec1f4a3faee372fecf7b95d4ffc9fee9ac886d`. [Checkpoint](../acceleration/results/20260930_resume/seventeenth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_seventeenth_milestone.yaml); previous report: sixteenth milestone.

**Verdict:** target resolution UNKNOWN. No independently validated 99-vertex graph or general nonexistence proof exists in this repository. No target resolution is under external review; this is not a worldwide literature verdict. Draft PR3 remains unmerged.

**Verified changes:**

| Claim | Exact scope and evidence |
| --- | --- |
| `C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FIBRE-REDUCTION` r1 | Exactly the specified20triplicate-support cyclic-F construction subclass. This is not without loss of generality among arbitrary fixed-support factors; residualD is arbitrary and unencoded. [Evidence](../acceleration/results/20260930_independent_review/hadamard_six_prism_cyclic_reduction/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-COLORING-CNF` r1 | One fixed six-prism L and additional cyclic three-column restriction; not all fixed-L factors. [Evidence](../acceleration/results/20260930_independent_review/hadamard_cyclic_factor_cnf/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FACTOR-EXCLUSION` r1 | This excludes only the extra cyclic construction subfamily of one literal support, not all factors for that support or core. [Evidence](../acceleration/results/20260930_independent_review/hadamard_cyclic_unsat/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-ORDERED-COLORING-CNF` r1 | One exact six-prism Hadamard support only, modulo independently verified identical-support column sorting. [Evidence](../acceleration/results/20260930_independent_review/hadamard_prism_ordered_cnf/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION` r1 | The exact12 marginal projections and120 separate local realizations only; the full-Gram implication that all triplicate colour counts are(1,1,1) remains UNKNOWN. [Evidence](../acceleration/results/20260930_independent_review/hadamard_triplicate_counts_v2/summary.json). |
| `C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS` r1 | Complete local finite universe on one support, applicable to each of the20supports by its six distinct matching-pair coordinates; no between-support Gram or column conditions or residualD are included. [Evidence](../acceleration/results/20260930_independent_review/hadamard_triplicate_counts_v2/summary.json). |

**Work completed:** two distinct native models were each attempted once. The cyclic model has 26,360 variables and 122,394 clauses. Its UNSAT result has a 29,697,087-byte trace, independently replayed completely against the exact formula with positive and corrupted controls. The semantic reduction and every clause were checked independently. This excludes only the explicitly imposed cyclic triplet construction, not all factors on its support or core.

The broader ordered model retains all 90 coloring options for each of 60 columns before ordering, with 595,464 variables and 3,336,642 clauses. Every clause was independently checked, including the 163,800 ordering clauses and all column caps. Ordering only relabels identical-support columns; no target automorphism is assumed. Its sole attempt stopped at the 300-second wall guard with wrapper exit 124, after 525,037 conflicts. The 350,457,856-byte partial trace and execution receipts were independently checked. This UNKNOWN result excludes nothing.

The independent complete local census considers all 117,480 increasing triples from 90 balanced words. Exactly 31,110 satisfy the local Gram upper bounds and column caps; 150 have color counts (1,1,1) at all six coordinates, and 30 are cyclic. These nested populations are not added. All 12 saved marginal matrices have exact rational rank 6; their nonconstant integer witnesses have 120 separately checked local realizations. Those realizations need not agree globally. Whether full Gram feasibility forces balanced triplets remains UNKNOWN.

**Coverage:** one cyclic subclass excluded; zero new whole-support, core or unrestricted exclusions. The previous four-of-five selected support exclusions remain unchanged. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains 171 claims: 169 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** a complete exact certificate for the specified cyclic subclass, plus an independently approved broader encoding. No full 36-by-60 factor or new comparable target-wide bound was obtained.

**Problems:** the broader search timed out. The first independent projection checker used an incorrect raw field name and failed before mathematical checking; its original source and failure are preserved with the corrected independent audit. Local counterexamples refute only the stated projection-level implications. Lossless packages preserve the complete cyclic proof and large inputs; the incomplete broader trace remains LOCAL_ONLY. No numerical zero or timeout is promoted to a certificate.

**Execution:** both cohort native attempts completed. Fresh observation at 2026-09-30T03:55:44.739547+00:00: `NO_CADICAL_PROCESS_OBSERVED`. Exact logs are bound in the checkpoint. Later MIP or coupled-count work requires separate receipts and is outside these counts. The user's continuation instruction remains active.

**Next experiment:** Complete the separately gated direct binary MIP attempt on the remaining fixed support, then independently check any saved integer factor and all column caps. This later attempt belongs to the eighteenth cohort.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/bbec1f4a3faee372fecf7b95d4ffc9fee9ac886d), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_seventeenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_SEVENTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
