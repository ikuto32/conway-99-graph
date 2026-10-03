# Twentieth resumed milestone, 2026-09-30 JST

Five verified claims and one refuted claim were added since the [nineteenth milestone](RESEARCH_20260930_NINETEENTH_WAVE.md). A complete independently replayed proof excludes all balanced factors on the fixed six-prism support. Unbalanced factors and Conway-99 remain unresolved.

**As of:** 2026-09-30T06:00:18.899683+00:00; source commit 4442207abbe24effffefb56ab323e3891bc3fafd. [Checkpoint](../acceleration/results/20260930_resume/twentieth_milestone_checkpoint.json), [frozen ledger](../acceleration/results/20260930_resume/claims_at_twentieth_milestone.yaml); previous report: nineteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact is under external review. This is not a worldwide literature verdict; draft PR3 remains unmerged.

**Claim and verification changes:**

| Status | Claim | Exact scope and evidence |
| --- | --- | --- |
| VERIFIED | C-FIXED-HADAMARD-ALL-MIXED-ORIENTED-TRIPLE-ENCODING r1 | Only the fixed six-prism Hadamard support and all-mixed balanced subfamily; no odd-phase, outside-cap or residual-D equivalence. [Evidence](../acceleration/results/20260930_independent_review/hadamard_oriented_triples/summary.json). |
| VERIFIED | C-FIXED-HADAMARD-ORIENTED-TRIPLE-NATIVE-UNKNOWN r1 | Only this exact source/input/configuration/run receipt; no mathematical exclusion or coverage conclusion. [Evidence](../acceleration/results/20260930_independent_review/hadamard_oriented_unknown/summary.json). |
| VERIFIED | C-FIXED-HADAMARD-COMPLETE-BALANCED-GRAM-ENCODING r1 | One fixed core/support and the extra balanced-triple condition; outside-column caps and residualD are omitted. [Evidence](../acceleration/results/20260930_independent_review/hadamard_balanced_gram_cnf_v2/summary.json). |
| VERIFIED | C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION r1 | Excludes only the extra balanced-triplet class of this literal fixed support, not all factors on that support or all factors for the core. [Evidence](../acceleration/results/20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json). |
| VERIFIED | C-FIXED-HADAMARD-AT-MOST-TWO-GROUP-MARGIN-CANCELLATION r1 | Necessary row-margin conditions on one fixed support, for any binary factor satisfying the stated support and margins. No general balance normalization or full-factor existence is asserted. [Evidence](../acceleration/results/20260930_independent_review/hadamard_two_group_margin_cancellation/summary.json). |
| REFUTED | C-FIXED-HADAMARD-SUPPORT-INTERSECTIONS-ZERO-OR-THREE r1 | A proposed finite-support intersection restriction; explicitly false on this raw input. [Evidence](../acceleration/results/20260930_independent_review/hadamard_two_group_margin_cancellation/summary.json). |

**Work completed:** two distinct native instances were attempted and completed: one oriented projection ended UNKNOWN at 1,000,000 conflicts, and one full balanced-Gram formula returned UNSAT after 248,698 conflicts. The latter has 10,480 variables and 74,200 clauses covering all 150 normalized local choices per group, including constants and mixed choices. Its complete 227,098,316-byte trace passed independent DRAT checking. Six public-size compressed parts recover exactly those bytes; an independent transport check verified the full stream, literal original comparison and ten corrupted controls. The capped extension was built but never independently approved or searched.

**Coverage:** exactly one balanced fixed-support family is newly excluded. Zero new whole-support, core or unrestricted exclusions. Overall search coverage: UNKNOWN; no validated denominator. The ledger contains194 claims:191 VERIFIED/CLEAR,2 CANDIDATE/CLEAR and1 REFUTED/CLEAR. Claim counts do not measure target coverage.

**Best result:** exact nonexistence of balanced binary36×60 factors with this literal support and prescribed integer Gram, without assuming outside-column caps. The three-column balance restriction is essential to the recorded scope.

**Problems:** the oriented result is UNKNOWN and its incomplete trace remains LOCAL_ONLY. The first encoding checker used an incorrect channel-count assumption; the first proof wrapper misparsed portability-patch context. Both original failures and corrected checkers are preserved. A guessed support-intersection restriction is refuted by a size-two intersection. The private broad process snapshot is omitted from public payloads; a narrow observation and hash-only availability record are retained. Four older learned traces remain MISSING; no proof depends on them.

**Execution:** both wave20 native calls and proof replay completed. Targeted census at 2026-09-30T06:00:18.921283+00:00: NO_CADICAL_PROCESS_OBSERVED. Later wave21 mathematical work has separate records. This checkpoint does not assert continuing native execution.

**Next experiment:** Use full-Gram marginal identities to bound unbalanced groups, then enumerate exact local deviation profiles for the surviving four-group circuits and screen their compatibility before further native search.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/4442207abbe24effffefb56ab323e3891bc3fafd), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_twentieth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWENTIETH_WAVE.md). Immutable publication pointers follow remote confirmation.
