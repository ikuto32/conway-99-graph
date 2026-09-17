# Sixth resumed milestone: two-coordinate family excluded

Since the [fifth milestone](RESEARCH_20260917_FIFTH_WAVE.md), fresh complete
domains and a new integer moment model allowed an exclusion after freeing
both sign coordinates at rootgroup0. A separate binary test passed its
necessary membership condition; that supplies no graph or LP solution.

**As of:** 2026-09-17T11:11:09.933411+00:00; source `d4f4a926ad075afa7309fb17c776e0de2c18bf7a` plus hash-bound new sources;
checkpoint `89e39b77c2457058e0e3ed6c83de7cbc80fc2ab8fd422ca4b0cea7e90e5e662a`.

**Verdict:** repository target resolution UNKNOWN. The new exact certificate
excludes only the family with156fixed outer edges and the recorded prescribed
absences, allowing120coordinate edges and1680disjoint-support edges to vary.
No unrestricted proof, target graph, automorphism assumption or external
target-resolution review is claimed.

**Verified changes:**

- `C-PARTIAL-K-TWO-COORDINATE-DOMAINS` revision 1: Both same-sign coordinates at rootgroup0 freed; exactly156 baseline K edges and all other prescribed absences retained. No nontrivial automorphism assumption.
- `C-PARTIAL-K-TWO-COORDINATE-FULL-MOMENT-ENCODING` revision 1: Retain156baselineK edges including all7cross matchings and12other same-sign matchings; all same-fibre and unlisted other-coordinate absences remain fixed. Unknown120same-sign edges in2root0coordinates plus1680disjoint-support edges.
- `C-PARTIAL-K-TWO-COORDINATE-EXCLUSION` revision 1: Both same-sign coordinates at rootgroup0 freed; exactly156 baseline K edges and all other prescribed absences retained. No nontrivial automorphism assumption.
- `C-PARTIAL-K-TWO-COORDINATE-BINARY-AFFINE-MEMBERSHIP` revision 1: Binary affine relaxation of the exact5370-row two-coordinate moment model; 1837 witness differences and84reference columns only. No full population rank assertion.

**Work completed:** all84domains independently enumerated, containing89,308
choices; all54,478old choices embed with identical full neighborhoods. The
5,370×96,280integer model has7,315,157nonzeros. A fresh raw-neighborhood audit
recomputed every89,308column and all84maxima for the positive certificate.
These are stages of one conditional-family result and their counts overlap.

The modular witness uses1,837column differences and84reference columns. Only
the exact witness membership was independently checked; the producer's
partial basis rank and processed-column count are not independently claimed.
Binary affine membership is compatible with a positive real moment bound:
it implies neither nonnegative star mixtures nor one selected star per center.

**Coverage:** one precisely specified two-coordinate family. No count or union
with the earlier family is added to progress. Overall search coverage: UNKNOWN;
no validated denominator.

**Best result:** `469399553/1048576 > 0` is an exact lower bound on this new
family's full moment L1residual with hard reciprocal equalities. Any admitted
target completion would have zero residual. The bound is not a score of a
candidate graph and need not be optimal. Older objectives and configurations
are not compared numerically with it.

**Execution:** the single900-second-capped solve completed successfully; its
recorded solver duration is605.953seconds. The transferred old weights were
evaluated first and gave an independently reproduced negative bound, retained
as an unsuccessful attempt. No wider exclusion was inferred from transfer.
Other process states are not inferred from this report.

**Problems and replay:** the one-coordinate proof was successfully replayed
using only115Git-bound runtime/seed files from public commitd4f4a926. This is
repeated execution of the independent checker, not fresh domain enumeration
or a new mathematical derivation. Initial newline conversion and Windows
provenance-command representation failures were preserved and corrected;
scientific inputs and checker arithmetic remained unchanged. The binary
partial-basis checkpoint is preserved with an exact gzip companion.

**Next experiment:** four freed same-sign coordinates at rootgroups0and1,
leaving144fixed outer edges. Complete-domain review, necessary matching
filtering and a separately checked reduced moment model precede the longer
bounded solve. A nonpositive transferred certificate already gives no
automatic broader-family exclusion.

**References:** [ledger](../CLAIMS.yaml), [new exact audit](../acceleration/results/20260917_independent_review/two_matching_solve_bound.json),
[scope binding](../acceleration/results/20260917_independent_review/two_matching_exclusion_claim_binding.json), [modular audit](../acceleration/results/20260917_independent_review/two_coordinate_binary_span.json),
[checkpoint](../acceleration/results/20260917_two_coordinate_checkpoint.json), [machine-readable milestone](../acceleration/results/20260917_resume/sixth_milestone.json),
[public replay](../acceleration/results/20260917_moment_public_replay/replay_receipt_v2.json), [replay instructions](REPRODUCING.md),
[draft PR1](https://github.com/ikuto32/conway-99-graph/pull/1), [source commit](https://github.com/ikuto32/conway-99-graph/commit/d4f4a926ad075afa7309fb17c776e0de2c18bf7a).
