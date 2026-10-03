# Eleventh resumed milestone, 2026-09-30 JST

Eight independently verified claims were added since the [tenth milestone](RESEARCH_20260930_TENTH_WAVE.md). One native solve produced a valid 25x60 partial factor; eleven exact row proofs excluded that fixed candidate. Separate exact arguments exclude two restricted six-prism construction families. A strengthened full-factor search ended UNKNOWN.

**As of:** 2026-09-30T00:07:11.591575+00:00; source commit `b2842b933366c68ee42bbd5669717550d5227f08`. [Checkpoint](../acceleration/results/20260930_resume/eleventh_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_eleventh_milestone.yaml); previous report: tenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated target graph nor a general nonexistence proof. No target candidate is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all eight claims are revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-FIXED-TRIANGLE-ONE-C2-ROW-TARGET-PROJECTION-CNF` | One labelled fixed39core target projection, selected C2coordinate0; no target automorphism or unrestricted core containment. [Audit](../acceleration/results/20260930_independent_review/triangle_one_c2_row_cnf/summary.json). |
| `C-FIXED-TRIANGLE-ONE-C2-ROW-PROJECTION-CONSTRUCTION` | One explicit25row target-necessary projection in the fixed39core labels; no omittedC2 rows, residualD or targetgraph supplied. [Audit](../acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_binding/summary.json). |
| `C-SIX-PRISM-FIVE-MATCHING-COMPLEMENT-DESIGN-EXCLUSION` | Only the explicit frozen restricted construction design. [Audit](../acceleration/results/20260930_independent_review/prism_complement_design/summary.json). |
| `C-SIX-PRISM-GLOBAL-COMPLEMENT-PAIRING-EXCLUSION` | All cell-pattern choices under this explicit global complement-pairing restriction; not limited to the five matching patterns. [Audit](../acceleration/results/20260930_independent_review/prism_complement_design/summary.json). |
| `C-FIXED-TRIANGLE-ONE-C2-COMPACT-CNF-EQUIVALENCE` | Same explicit25row fixed-core target-necessary problem; no new target coverage. [Audit](../acceleration/results/20260930_independent_review/triangle_one_c2_compact/summary.json). |
| `C-FIXED-25-ROW-TRIANGLE-EXTENSION-EXCLUSION` | One fixedQ1 AND selectedC2coordinate0 incidence row, with all660otherC2 incidences and1770outsideedges unspecified. Not a Q1-only exclusion. [Audit](../acceleration/results/20260930_independent_review/one_c2_extension_rows/summary.json). |
| `C-SIX-PRISM-FIVE-MATCHING-UNPAIRED-DESIGN-EXCLUSION` | Exactly30specified round-robin cell patterns, each repeated twice, with all360bits free; fixed six-prism core. [Audit](../acceleration/results/20260930_independent_review/prism_unpaired_kernel/summary.json). |
| `C-FIXED-TRIANGLE-FULL-FACTOR-COLUMN-CAP-CNF` | One exact fixed39core; all C1 and C2 entries free subject to audited zero folds; residual D absent; no unrestricted core coverage. [Audit](../acceleration/results/20260930_independent_review/triangle_factor_column_caps/summary.json). |

**Work completed:** one 74,814-variable, 256,151-clause projection returned SAT. Independent checking authenticated the full assignment, every clause, all 625 Gram entries, margins, component capacities and 1,770 column-pair bounds. This yielded one verified 25x60 partial factor. Each of its eleven missing row domains then had a complete contradiction tree; the independent checker covered all 1,037 nodes. These are eleven proofs excluding the same fixed Q1 plus selected C2 row. They do not exclude that Q1 with a different selected row. A smaller equivalent 22,379-variable, 81,366-clause encoding was checked using a restriction of the same assignment; it was not a second SAT discovery or a performance test.

For the six-prism core, one prescribed five-matching, globally complement-paired design returned UNSAT with a complete independently replayed DRAT proof. A separate parity argument excludes global complement pairing for any cell-pattern choices in this core. The broader all-bits-free five-matching design timed out, but an independently derived exact-rank/parity proof later excluded that specific design: eighteen 15x10 integer matrices have rank nine with full-support signed kernels. The UNKNOWN solver trace is not a premise of that proof. The three exclusion statements overlap; their populations are not added.

The full36 model retains both unknown incidence blocks and adds all necessary column-pair caps. Its complete encoding and object-checker gates passed before launch. The run ended at its conflict limit with no factor and no complete proof.

| Native attempt | Outcome | Saved conflict count | Wrapper seconds |
| --- | --- | --- | --- |
| fixed25 | SAT | 176251 | 17.391 |
| prism_complement_design | UNSAT_REPLAYED_SCOPED | 97899 | 6.297 |
| prism_unpaired_design | UNKNOWN_TIMEOUT | 57015 | 7.891 |
| fixed36_column_caps | UNKNOWN_CONFLICT_LIMIT | 1000001 | 83.219 |

These are four attempts in four different models, with different limits recorded in their manifests. Times include each wrapper's recorded boundary and are not a performance comparison. Exactly one native UNSAT trace was independently replayed. The other three traces are SAT-run or incomplete UNKNOWN traces and provide no nonexistence certificate.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or complete fixed-core family was excluded. The new ledger population is 122 claims: 120 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR. Generated, checked and excluded partial objects are overlapping pipeline stages, not separate target coverage.

**Best result:** an exact 25-row partial factor with a complete explanation of its extension failure, plus exact obstructions to two proposed prism construction families. There is no target-wide bound or validated 36-row factor.

**Problems:** capacities and pair caps on a partial factor are insufficient for completion. The strengthened full-factor solve is UNKNOWN. Arbitrary cell-pattern choices remain outside the five-matching design exclusion; none of these constructions is assumed to cover every target. Large incomplete/SAT-run traces remain LOCAL_ONLY. The large clause recipe is recoverable from its public gzip package; availability is recorded separately from mathematical verification.

**Execution:** all four native attempts and all eleven row searches are complete. A fresh observation at 2026-09-30T00:07:11.987430+00:00 returned `CADICAL_PROCESS_OBSERVED`. Exact process output is pinned in the checkpoint. The user's continuation instruction remains active.

**Next experiment:** allow arbitrary M1, M2 and P in the triangle core, with canonical C0, exact Gram equations, mixed bounds and column-pair caps. Independently establish unrestricted normalization, encoding equivalence and object-checker gates before a new native pilot. A factor would still leave the 60-vertex residual graph unresolved.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/b2842b933366c68ee42bbd5669717550d5227f08), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_eleventh_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_ELEVENTH_WAVE.md). Immutable public evidence pointers are recorded after publication confirmation.
