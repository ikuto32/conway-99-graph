# Fourth resumed milestone: reranked shortlist and partial-coordinate model

Since the [third milestone](RESEARCH_20260917_THIRD_WAVE.md), another frozen
16-configuration shortlist has passed independent exact checks. A larger
partial-coordinate domain and a full common-neighbor moment relaxation have
also been independently checked. These are scoped results, not a resolution.

**As of:** 2026-09-17T10:21:50.216626+00:00; source `2c7e733827ef05c6da445f7787fe676962b9d334` plus separately hash-bound new sources;
checkpoint `ce0ebb9f245502724979dcc7e90ac988662609786bc0a9f245774b0b08055442`.

**Verdict:** repository target resolution UNKNOWN. No validated target graph or
general nonexistence proof; no target-resolution external review.

**Verified changes:**

- `C-WHOLE-STAR-RERANK-V3-CALIBRATION` revision 1: Only16 named saved calibration cases and their120 unordered pairs under ORIGINAL_STAR_SIMPLEX_PDHG_V1, same model payloads/init and the two specified checkpoint budgets; exact statistics of stored floats.
- `C-PARTIAL-K-ONE-COORDINATE-DOMAINS` revision 1: Exactly prescribed162positiveKedges and all same-fibre/unlisted-other-coordinate absences; only one60edge matching coordinate and1680disjoint edges unfixed
- `C-PARTIAL-K-SAVED-POINT-ODDSETS` revision 1: Exact rational interpretation and perstar normalization of this saved floating vector; smaller-endpoint matching projection; no numerical tolerance
- `C-RERANK-V3-STAR-16-EXCLUSIONS` revision 1: Exactly these16 labeled fixedK assignments with prescribed absent edges; positive independent exact original-star lower bounds
- `C-RERANK-V3-STAR-16-NO-IMPROVEMENT` revision 1: All16 exact original-star lower bounds exceed incumbent18481 upper bound
- `C-PARTIAL-K-FULL-MOMENT-ENCODING` revision 1: Remaining162Kedges fixed, including13other same-sign and7cross matchings; all same-fibre and unlisted other-coordinate absences fixed. Only60freed matching edges+1680disjoint edges unknown.

**Work completed:** 128 existing candidates
reranked at 5,000 cold iterations, zero new candidates. The frozen union policy
selected 16 of 112
previously untested candidates. Independent checking covered
404,686 original star choices across those
16 configurations. Every selected
configuration has a positive exact lower bound in its fixed-edge scope;
0 improves the incumbent and
0 has an unseparated comparison interval.
Ranking and evaluation stages overlap and are not summed.

The separate partial-coordinate model has 54,478
complete local choices over 84 centers. It holds 162
outer edges fixed, frees 60 possible matching-coordinate edges, and retains
1,680 disjoint-support unknown edges with the documented prescribed absences.
The saved numerical point violates one of 2,048 tested odd
subsets by approximately 3.92e-15, while its degree/reciprocity equalities are
not exact. This is a point diagnostic, not a family obstruction.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
The selection fraction describes this finite batch only. No automorphism of a
hypothetical target graph is assumed.

**Best result:** original-domain incumbent18481 remains approximately
[5.374367028255648, 5.3743670369854]. Best new selected index66083 has exact
rational bounds displayed approximately as
[8.190622896422129, 8.190622973001425].
Lower is better for this defined reciprocity/cap violation objective; these
positive values are conditional obstructions, not distances to a solution.
The partial-coordinate and full moment objectives have different feasible
domains/definitions and are not compared numerically with this objective.

**Execution:** the shortlist invocation completed at
2026-09-17T10:10:59.025696+00:00 with exit0 and final independent review.
Other process states are not inferred by this saved report.

**Problems:** the strengthened odd-set LP and initial full moment LP reached
their separate 60-second solver caps without valid primal or dual solutions.
Their raw objective fields of zero are unusable. The moment model's complete
integer matrix was independently checked, but that does not establish
feasibility or exclusion. The saved original failure records are preserved.
Four V3 numerical input copies totaling 3,212,989,588 bytes remain LOCAL_ONLY;
selected-case exact artifacts are separate. Public availability is recorded
only after the corresponding commit is confirmed remote.

**Next experiment:** extract exact support-function bounds from arbitrary saved
finite weights, which need not be solver-certified dual solutions, then run
the same frozen model with a separately declared longer limit if necessary.
A matching-filter pilot is separately awaiting independent checking.

**References:** [ledger](../CLAIMS.yaml), [exact shortlist audit](../acceleration/results/20260917_independent_review/rerank_v3_16_scope.json),
[full moment audit](../acceleration/results/20260917_independent_review/partial_moments.json), [checkpoint](../acceleration/results/20260917_whole_star_rerank_v3_checkpoint.json),
[machine-readable milestone](../acceleration/results/20260917_resume/fourth_milestone.json),
[large-input catalog](../acceleration/results/20260917_whole_star_rerank_v3/local_artifacts.json),
[draft PR1](https://github.com/ikuto32/conway-99-graph/pull/1),
[source commit](https://github.com/ikuto32/conway-99-graph/commit/2c7e733827ef05c6da445f7787fe676962b9d334).
