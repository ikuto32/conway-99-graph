# Fifth resumed milestone: an exact conditional family exclusion

Since the [fourth milestone](RESEARCH_20260917_FOURTH_WAVE.md), an exact
support-function certificate has excluded an entire one-coordinate family.
Independent raw-neighborhood arithmetic reproduced the certificate. Separate
matching filtering, population counting and scope inclusion were also checked.

**As of:** 2026-09-17T10:48:06.520007+00:00; source `50eb5ed9da1d5a849aae0677cc129e7d6da76906` plus hash-bound new sources;
checkpoint `8ef4773cd204065495aa3be5f4fa9f2533af5f1874ba578dc1657eb32afb2df2`.

**Verdict:** target resolution UNKNOWN. No complete99-vertex target graph or
general nonexistence proof. No target-resolution external review is claimed.
The result fixes162outer edges and the recorded absent edges; only60coordinate
edges and1680disjoint-support edges vary. No automorphism is assumed.

**Verified changes:**

- `C-PARTIAL-K-NEIGHBORHOOD-MATCHING-FILTER` revision 1: Exact frozen 162-fixed-overlap-edge family with same-fibre and other-coordinate prescribed absences, 1740 unknown edges and 54478 original choices. Original center/domain IDs retained.
- `C-PARTIAL-K-ONE-COORDINATE-EXCLUSION` revision 1: Only the labeled partial-coordinate family specified by manifest dcc0118cc35993743e94bf7b548e6870526e33f3d4fe4015a48cdacb0c1fc05c: 162 fixed outer K edges, 60 freed matching-coordinate and 1680 disjoint-support unknown edges, and all prescribed absences.
- `C-PARTIAL-K-COORDINATE-MATCHING-UNIVERSE` revision 1: The12vertices/60allowededges and162fixedK edges in the frozen manifest only; no symmetry quotient.
- `C-PARTIAL-K-MATCHING-SUBFAMILY-COVERAGE` revision 1: Only the fixed162-edge family and its6040 labeled coordinate assignments, with the same prescribed absences. No union with historical exclusions.

**Work completed:** one conditional family excluded using all54,478 unfiltered
local stars over84centers. The independent checker reconstructed every column
directly from full neighborhoods with Python integers and checked all84maxima.
Nine rooted rook9 controls, their RHS/column corruptions, an altered bound,
an out-of-box weight and zero weights calibrated that path.

The separate matching filter removes13,105 of54,478local choices, leaving41,373
with no empty domain. It was not needed for the family certificate. The complete
coordinate list has6,040distinct matchings; all pass partial upper caps. An
independently reviewed inclusion argument places each assignment's completion
problem inside the excluded family. These are6,040coordinate assignments,
not6,040independently solved LP instances or completed graphs. Pipeline units
are separate and must not be added.

**Coverage:** all6,040assignments in this one frozen coordinate population are
covered by the conditional exclusion. No union with earlier fixed-case
exclusions was computed. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the exact bound `9227079/16384 > 0` is a lower bound on the
L1full-common-neighbor moment residual over the stated star simplices with
hard reciprocal equalities. Every admitted target completion would have zero
residual, yielding the contradiction. The bound need not be optimal. It is
not comparable with the older original-star or edge objectives; their incumbent
records are retained separately.

**Execution:** the600-second-capped attempt completed after
268.68700000000536solver seconds. Earlier60and240second
attempts timed out; their invalid vectors and negative exact extractions are
preserved. The successful certificate depends on exact arithmetic, not the
solver's floating-point optimality report. Other live process states are not
inferred from this saved report.

**Problems:** no unrestricted conclusion follows from the fixed configuration.
Initial registry attempts rejected a wrong dependency key and a missing
explicit null; both failed before changing the ledger and their evidence is
retained. These engineering corrections changed no mathematical result.
Artifact availability is updated separately only after confirmed publication.

**Next experiment:** free both sign coordinates of the same root group, leaving
156fixed outer edges. Require fresh domain and integer-model checks. Recompute
any transferred certificate on every enlarged-domain column; if nonpositive,
use the separately preregistered bounded new LP solve.

**References:** [ledger](../CLAIMS.yaml), [exact arithmetic audit](../acceleration/results/20260917_independent_review/moment_positive600.json),
[scope/binding correction](../acceleration/results/20260917_independent_review/moment_positive600_claim_binding.json), [matching population](../acceleration/results/20260917_independent_review/coordinate_universe.json),
[coverage proof](AUDIT_20260917_COORDINATE_FAMILY_COVERAGE.md),
[checkpoint](../acceleration/results/20260917_partial_coordinate_checkpoint.json),
[saved milestone](../acceleration/results/20260917_resume/fifth_milestone.json),
[draft PR1](https://github.com/ikuto32/conway-99-graph/pull/1),
[source commit](https://github.com/ikuto32/conway-99-graph/commit/50eb5ed9da1d5a849aae0677cc129e7d6da76906).
