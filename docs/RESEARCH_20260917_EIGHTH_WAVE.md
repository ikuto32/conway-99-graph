# Eighth milestone: four-coordinate family excluded

Since the [seventh milestone](RESEARCH_20260917_SEVENTH_WAVE.md), the larger
four-coordinate family has an independently checked exact exclusion. The
six-coordinate extension has verified domains, a necessary matching filter
and a verified moment encoding, but no exclusion at this checkpoint. Seven
new claim records are VERIFIED/CLEAR; the generated ledger totals are 41
records, including 40 VERIFIED/CLEAR and one unchanged CANDIDATE literature record.

**As of:** exact timestamp in the [generated milestone](../acceleration/results/20260917_resume/eighth_milestone.json),
source `7c5e2bb59580fdae1c0a0eb9beb2513a41ecdad8` plus hash-bound new sources.
Checkpoint SHA256: `9f6bf0bbc1e7bbb44216a6cbe54feb2971e298e969a57aba0738b04b307fc64c`.

**Verdict:** repository target resolution UNKNOWN. No target graph or general
nonexistence proof is established. No target-resolution external review or
nontrivial automorphism assumption is claimed.

**Verified changes:**

- `C-PARTIAL-K-FOUR-COORDINATE-EXCLUSION` revision 1 excludes exactly the
  family with 144 fixed outer edges and the recorded prescribed absences,
  allowing 240 same-sign-coordinate and 1680 disjoint-support edges to vary.
- `C-PARTIAL-K-SIX-COORDINATE-DOMAINS` revision 1 records all 879,449 local
  choices and embeds all 290,460 prior choices with identical full neighborhoods.
- `C-PARTIAL-K-SIX-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER` revision 1 rejects
  166,728 of those choices and retains 712,721, with no empty domain.
- `C-PARTIAL-K-SIX-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING` revision 1
  checks the necessary zero-residual embedding into the complete recorded LP.
- `C-FOUR-COORDINATE-FIXED-WEIGHT-TRANSFER-SCREEN` revision 1 records failure
  of ten particular transferred weight sets. It supplies neither feasibility
  nor an exclusion; all ten failed cases are retained.
- `C-ROOK-NINE-REGULAR-SET-ENCODING` revision 1 gives an exact block-matrix
  representation conditional on an induced nine-vertex rook graph. Its
  eighteen-cell quotient spectrum is compatible, not contradictory.
- `C-MOMENT-PDHG-GPU-CPU-PARITY` revision 1 verifies numerical agreement on
  four saved inputs at four checkpoints through 100 iterations. It is an
  engineering result, not a mathematical certificate or a speedup guarantee.

**Work completed:** the four-coordinate certificate audit independently scored
all 230,879 surviving raw neighborhoods and all 84 center maxima. Per-center
original IDs establish that the 59,581 sound matching rejections and these
survivors partition all 290,460 original choices. The single capped LP returned
successfully, with recorded solver duration 1432.875 seconds. No solver
feasibility flag or floating objective is needed for the exact certificate.

The six-coordinate family retains 132 fixed outer edges, with 360 coordinate
and 1680 disjoint-support edges unknown. Its direct filtered model has 5,610
rows, 719,693 columns and 59,380,799 integer nonzeros. All retained columns,
slacks, bounds and costs were independently reconstructed. The transferred
four-coordinate certificate gave the independently checked negative bound
`-2378749843/1048576`; this is a failed shortcut, not evidence of feasibility.
The pipeline counts overlap and are not summed as distinct target cases.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
These are precisely declared conditional families; no target-wide fraction
or union with previous exclusions is asserted.

**Best result:** `68986111/262144 > 0` is an exact lower bound on the filtered
four-coordinate full-moment L1 residual with hard reciprocity constraints.
Every target completion in that family would have zero residual, yielding the
contradiction. It is not a graph score, and values on other families/objectives
are not ranked against it.

**Execution:** a [direct process observation](../acceleration/results/20260917_resume/eighth_solver_process_observation.json)
at 2026-09-17T11:54:51Z found the six-coordinate CPU solver active. Its separate
5,400-second cap and saved runtime heartbeats govern that attempt; this static
report does not establish current liveness. The first launcher preflight failed
before solver execution because of resource-field names; the original source
and failure were preserved before a separately named correction. A separately
gated GPU weight search is being prepared. No six-coordinate result is inferred.

**Problems and verification:** two rook auditors collided on a source filename.
The original report survives, but its exact original checker is unavailable.
Promotion was held; a fresh, uniquely named independent checker established
the current result without that missing source. The collision and unavailable
source records remain preserved. The GPU audit also preserved its initial
corruption-control dtype failure before a new float64-decoding audit passed.
Neither failure was concealed or treated as a mathematical refutation.

The two-coordinate proof now successfully replays from 285 Git-bound inputs
at public commit `7c5e2bb`; the earlier omitted-log failure remains recorded.
This is repeated execution of an independent checker, not a new derivation.
Large raw files remain LOCAL_ONLY, with exact gzip/chunk companions and
retrieval manifests where prepared. Artifact availability is separate from
mathematical verification.

**Next experiment:** finish the capped six-coordinate CPU solve and the
independently gated GPU weight search; check every meaningful support bound
using a separate raw-neighborhood implementation. The rook representation is
a distinct conditional structural route and does not imply universal containment.

**References:** [ledger](../CLAIMS.yaml), [checkpoint](../acceleration/results/20260917_four_coordinate_exclusion_checkpoint.json),
[exact four-coordinate audit](../acceleration/results/20260917_independent_review/four_matching_filtered_run01_bound.json),
[scope binding](../acceleration/results/20260917_independent_review/four_matching_exclusion_claim_binding.json),
[six-coordinate model audit](../acceleration/results/20260917_independent_review/six_filtered_moments.json),
[fresh rook audit](../acceleration/results/20260917_independent_review/rook_regular_set_recheck.json),
[GPU parity audit](../acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity_v2/summary.json),
[public proof replay](../acceleration/results/20260917_two_coordinate_public_replay/replay_receipt.json),
[replay instructions](REPRODUCING.md), [draft PR2](https://github.com/ikuto32/conway-99-graph/pull/2).
