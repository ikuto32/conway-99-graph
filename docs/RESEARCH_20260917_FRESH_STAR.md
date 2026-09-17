# Resumed fresh-star milestone, 2026-09-17

Changes since [the saved stop](STOP_20260916_FRESH_STAR.md): the selected fresh-star
evaluation and separate raw-artifact review are complete. The current claim ledger
is now [root CLAIMS.yaml](../CLAIMS.yaml); the pinned historical ledger is unchanged.

**As of:** 2026-09-17T08:52:10.807266+00:00; computational source `7518ebcec78589fe7f8b068ee7a1dd87e8bf8d42` plus
the explicitly hashed new tooling; checkpoint `195d2d008641c3da867933df00e33d81ebdcef252f6712df42db344fb1f9a696`.

**Verdict:** repository target resolution UNKNOWN. No complete target graph or
general nonexistence proof; no target-resolution external review.

**Verified changes:** `C-STAR-BASELINE-18481` revision1 freshly checks the exact
incumbent interval and fixed-K exclusion. `C-FRESH-STAR-16-EXCLUSIONS` revision2
excludes precisely the 16 selected fixed configurations.
`C-FRESH-STAR-16-NO-IMPROVEMENT` revision1 proves that each of their exact lower
bounds exceeds the incumbent upper bound. Same-fiber edges and all unlisted
overlapping-support edges are fixed absent. No nontrivial automorphism is assumed.

**Work completed:** 128 previously ranked candidates;
16 selected configurations; 16 attempted star evaluations;
16 completed exact pipelines;
16 separately checked distinct configurations;
0 improvements; 0 pending cases.
These pipeline populations overlap and must not be summed. The remaining112
ranked configurations were not evaluated by this wave.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
This wave evaluates16 of the128 previously ranked configurations only.

**Best result:** incumbent18481 retains its exact interval, approximately
[5.374367028255648,5.3743670369854]. Selected index67 is best in this batch,
approximately[7.00134161058368,7.0013416347365816]. Both use the same original-star
simplex reciprocity/cap violation objective; lower is better. Exact fractions are
in the linked audit. The positive bounds exclude the respective fixed K and do
not measure distance to an SRG.

**Execution:** the 16-case invocation exited0 at its saved receipt time. The next
same-sign whole-matching driver and GPU search were observed live at
2026-09-17T17:51:05.5657583+09:00; this is a dated observation, not a promise of
continued execution. The separate new triangle-matching filter remains CANDIDATE
pending independent review and is not included in verified totals here.

**Problems:** no candidate errors, timeouts or pending certificates in this wave.
Initial sandbox restrictions required native-library/read-access retries.
The first ledger impact check falsely rejected a new downstream claim; that failed
report is preserved, the checker was corrected with regression controls, and
the subsequent impact check passes. This bookkeeping correction does not alter
the mathematical artifacts. Some inherited checkpoint dependencies remain
local-only; hash identity alone does not provide public replay. New artifacts
are initially LOCAL_ONLY until their publication commit is available.

**Next experiment:** execute the preregistered [whole same-sign matching wave](NEXT_20260917_SAME_MATCHING.md)
from this checkpoint, to seek a strictly improved exact star interval. In parallel,
independently audit the stronger local triangle-matching filter.

**References:** [run summary](../acceleration/results/20260917_fresh_star_shortlist/summary.json),
[independent claim binding](../acceleration/results/20260917_independent_review/claim_bindings.json),
[written derivation](../acceleration/results/20260917_independent_review/MATHEMATICAL_AUDIT.md),
[checkpoint](../acceleration/results/20260917_fresh_star_checkpoint.json),
[machine-readable milestone](../acceleration/results/20260917_resume/milestone.json),
[claim schema and migration](CLAIMS_SCHEMA.md).
The immutable publication commit and draft PR are recorded separately after push.
