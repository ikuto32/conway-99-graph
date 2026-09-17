# Seventh milestone: wider domains and simpler exact evidence

Since the [sixth milestone](RESEARCH_20260917_SIXTH_WAVE.md), four necessary
four-coordinate results were independently checked. The existing two-coordinate
exclusion gained a simpler integer certificate; its statement and scope remain
unchanged. The claim ledger records these five changes, with 34 claim records:
33 VERIFIED/CLEAR and one CANDIDATE/CLEAR literature record.

**As of:** timestamp and source commit in the [generated milestone](../acceleration/results/20260917_resume/seventh_milestone.json),
based on `2fca344c28bbf0b1be329336c26f24f270ba5746` plus hash-bound new sources.
Checkpoint SHA256: `60fbfb569c8b0ed2b54407f1a7d905d02116ec23ec86b421c719fe9bd6d10c5b`.

**Verdict:** repository target resolution UNKNOWN. No independently validated
99-vertex graph or general nonexistence proof exists in this evidence package.
No external review of a target resolution is claimed. No automorphism is assumed.

**Verified changes:**

- `C-PARTIAL-K-FOUR-COORDINATE-DOMAINS` revision 1: exactly 290,460 locally
  admissible choices at 84 centers; every one of the earlier 89,308 choices
  embeds with the same full neighborhood.
- `C-PARTIAL-K-FOUR-COORDINATE-FULL-MOMENT-ENCODING` revision 1: every admitted
  target completion induces a zero-residual point in the exact necessary LP.
- `C-PARTIAL-K-FOUR-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER` revision 1: exactly
  59,581 choices fail the necessary matching test and 230,879 survive. No domain
  is empty. Positive witnesses do not establish simultaneous graph feasibility.
- `C-PARTIAL-K-FOUR-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING` revision 1:
  all retained columns, rows, costs, bounds and slack columns were checked.
- `C-PARTIAL-K-TWO-COORDINATE-EXCLUSION` revision 2: additional exact evidence
  only. All nine preregistered denominator cases passed independent checking;
  the simplest tested denominator is 1, with bound `204 = 379 - 175 > 0`.

**Work completed:** the four-coordinate family retains 144 fixed outer edges
and prescribed absences, with 240 coordinate edges and 1680 disjoint-support
edges unknown. The original model has 5,490 rows, 297,432 columns and 24,085,997
integer nonzeros. Filtering leaves 237,851 columns and 19,139,922 nonzeros.
These are overlapping stages of one conditional-family experiment.

For each of nine two-coordinate weight sets, the independent checker rebuilt
all 89,308 raw-neighborhood column scores and 84 maxima. Deterministic rounding,
clipping, first maximizing original IDs, selection rules, positive fixtures
and corrupted certificates were checked. This is nine certificates for the
same family, not nine new excluded families.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
The four-coordinate domains and filter alone do not exclude that family.
No union with earlier exclusions or target-wide percentage is asserted.

**Best result:** `204 > 0` is a simpler exact lower bound for the already excluded
two-coordinate moment relaxation. It is weaker numerically than its existing
bound `469399553/1048576`; its benefit is integer coefficients, including moment
weights in `{−1,0,1}`. No globally minimal certificate is claimed. The original
certificate and successful checks remain preserved.

**Execution and problems:** the four-coordinate filtered solve has its own
2,400-second cap and [saved observations](../acceleration/results/20260917_four_matching_filtered_solve2400/run01/).
This static milestone does not assert current process liveness or its outcome.
The independent recovery audit checked every byte of the four-part matrix and
tested path, corruption and overwrite rejection. Reconstruction is engineering
verification, not mathematics. Large raw matrices remain LOCAL_ONLY with exact
chunk companions; availability is recorded separately in the ledger/catalog.

Strict Git-only replay preparation for the two-coordinate proof found one
missing input at commit `2fca344`: the 6,517-byte `highs.log` was excluded by
the generic log ignore rule. Its local bytes match the frozen audit hash.
The preparation failure is preserved; the exact log is included in this next
publication. A successful public replay is not claimed until actually rerun
from that publication. Existing mathematical checks are unaffected.

GitHub reported PR #1 externally merged at the fifth milestone; the research
agent did not merge it. [Draft PR #2](https://github.com/ikuto32/conway-99-graph/pull/2)
continues review. The [saved remote observation](../acceleration/results/20260917_resume/sixth_remote_review_observation.json)
records the actual merge, draft state and CI checks. CI is not proof verification.

**Next experiment:** finish the separately capped filtered four-coordinate LP
and independently evaluate any saved exact support certificate. A bounded
six-coordinate domain pilot separately tests the tractability of a wider family;
no completeness or exclusion is inferred before its audit.

**References:** [ledger](../CLAIMS.yaml), [checkpoint](../acceleration/results/20260917_four_coordinate_foundations_checkpoint.json),
[domain audit](../acceleration/results/20260917_independent_review/four_matchings/summary.json),
[filter audit](../acceleration/results/20260917_independent_review/four_coordinate_matching_filter/summary.json),
[filtered model audit](../acceleration/results/20260917_independent_review/four_matching_filtered_moments.json),
[small-certificate audit](../acceleration/results/20260917_independent_review/two_coordinate_small_certificate.json),
[recovery audit](../acceleration/results/20260917_independent_review/recovery_tools.json),
[recovery commands](REPLAY_20260917_COMPRESSED_AND_CHUNKED.md).
