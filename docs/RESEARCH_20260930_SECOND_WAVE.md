# Second resumed milestone, 2026-09-30 JST

Seven independently checked scoped claims were added since the
[first resumed milestone](RESEARCH_20260930_FIRST_WAVE.md). No target-level
conclusion changed. The full matching filter and moment encoding passed;
a fixed rook-window family was proof-checked UNSAT, and a broader local
family produced a valid 59-vertex witness with an exact extension obstruction.

**As of:** 2026-09-29T20:01:38.357341+00:00; source base
`dacbbaa157f30182f877dc38b2017f790ddc5938`; saved
[checkpoint](../acceleration/results/20260930_resume/second_milestone_checkpoint.json)
and [ledger snapshot](../acceleration/results/20260930_resume/claims_at_second_milestone.yaml).

**Verdict:** target resolution UNKNOWN. There is no independently validated
99-vertex target graph or general nonexistence proof in this repository.
No external target-resolution review is underway. Scoped research remains in
[draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3).

**Verified changes:** each claim below is revision 1.

| Claim | Exact scope and independent evidence |
| --- | --- |
| `C-PARTIAL-K-EIGHT-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER` | All 2,290,122 original stars checked: 414,908 fail the necessary matching test; 1,875,214 survive across 84 nonempty centers. [Binding](../acceleration/results/20260930_independent_review/eight_matching_filter_claim_binding.json). |
| `C-PARTIAL-K-EIGHT-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING` | Every target extension of the exact 120-fixed-K family gives a zero-objective point of the saved LP. All 156,321,767 coefficients checked. [Audit](../acceleration/results/20260930_independent_review/eight_filtered_moments/summary.json). |
| `C-ROOK-FIXED-STAR-WINDOW-CNF-ENCODING` | Exact equivalence for the labelled fixed central star, five internal matchings and 600 free edges. [Complete clause check](../acceleration/results/20260930_rook_window_sat/independent_cnf_encoding.json). |
| `C-ROOK-FIXED-STAR-WINDOW-EXCLUSION` | This 600-edge family is UNSAT. The complete DRAT proof passed a fresh checker built from pinned upstream source, with positive and corrupted controls. [Proof audit](../acceleration/results/20260930_rook_sat_independent_proof/summary.json). |
| `C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING` | Freeing four internal matchings gives a distinct 780-edge family; every one of its 3,689,820 clauses was independently reconstructed. [Audit](../acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json). |
| `C-ROOK-FOUR-FACTOR-WINDOW-LOCAL-CONSTRUCTION` | One complete local 59-vertex graph satisfies the broader CNF and all declared degrees/caps. Every clause, decoded edge and graph condition checked. [Audit and raw witness](../acceleration/results/20260930_rook_free_internal_independent_certificate/summary.json). |
| `C-ROOK-LOCAL59-NEGATIVE-GRAM-EXCLUSION` | That exact local graph cannot extend to the target: an integer vector has quadratic value `-30571152163483770` for `27I-9A+J`. [Independent direct integer check](../acceleration/results/20260930_independent_review/rook_original_gram.json). |

The local construction remains valid for its weaker constraints. Its failure
to extend is a separate statement. No rook-containment theorem or graph
automorphism is assumed. For any target, exact expansion gives
`G² = 63G`, where `G = 27I-9A+J`, hence `xᵀGx = ||Gx||²/63 ≥ 0`.
Every induced principal submatrix must obey that condition.

**Work completed:** matching-filter decisions cover the complete frozen
2,290,122-star population. They are not additional stars to add to the domain
count. The moment LP has 5,730 rows, 1,875,214 probability columns and 6,972
slack columns; every entry was checked. The two SAT families are overlapping
conditional populations, not disjoint target branches. Their results cannot
be summed into coverage. The saved registry has 55 claims: 53 VERIFIED/CLEAR
and 2 CANDIDATE/CLEAR. Schema checks do not establish mathematical validity.

**Execution and problems:** the first GPU attempt exited with code 2 before
iteration because its input exceeded a 2 GiB native guard. All six missing
support attempts were independently recorded as skipped. A separate native
variant changes only four admission guards; it passed 14 parser controls and
all 16 saved checkpoints across four CPU comparison inputs. These are
engineering checks, not a full-model numerical theorem. The larger-input
retry was observed active at the checkpoint's
[process observation](../acceleration/results/20260930_resume/second_milestone_process_observation.json).
That dated observation is not a perpetual running claim. Numerical and later
cut-wave results require their own completed audit records.

The broader SAT pilot saved its result/model before a native cleanup failure;
the anomaly is preserved. Its local SAT conclusion rests on independently
checked raw artifacts. This anomaly would not substitute for checking an
UNSAT proof. No mathematical verification veto occurred in these seven claims.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the earlier six-coordinate bound `14157/16384 > 0` still
excludes only its 132-fixed-K family. It is not an eight-coordinate bound or
a target-wide progress metric. At this checkpoint no new eight-coordinate
support bound has completed independent checking.

**Next experiment:** complete the eight-coordinate GPU retry and independently
evaluate all six frozen exact support attempts. The separate local SAT lane
uses independently checked Gram cuts to falsify additional local completions.

**Reproduction:** [recovery instructions](REPRODUCING_20260930_SECOND_WAVE.md)
retain exact commands, locked environments, raw graph/proof hashes, source
versions, compressed proof/CNF files and byte-exact matrix chunks. Artifact
publication state is tracked separately in the ledger; a hash alone does not
make a local binary publicly available.
