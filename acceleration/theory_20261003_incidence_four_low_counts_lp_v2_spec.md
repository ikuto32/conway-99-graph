# Prospective four-low-count target-kernel exact-dual guide V2

Prepared2026-10-02. Source preparation only: no calibration or optimizer has
executed for this version. All generic, thirteen-weight and seven-weight
source/output/receipt bytes remain unchanged. This source adds independently
checked N5=12474 to N3=231,N4=2079,N6=24486 and introduces two explicit,
separately recorded weight domains. No generic binary-code bound or target
resolution is claimed.

V1 preparation is preserved UNEXECUTED: source
efb478950e44b3be6795d9cdbd78b026fac25348375a2515bb7c98639455e423,
spec6bb4b468503297ee2bf31ad4e9881f70039cb28e006d9dd3bbae925b5124f293.
V2 additionally pins the exact64hex N5 producer summary
53cdcff6185d199b8f83a4989d0ea37a4b6ebbfa4fce69362e59594dcd3a6283
and universal proof8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee
in every runtime closure. V2 requires a version2-specific ROOT checker
gate; no execution or approval occurred for V1. Mathematical model and
finite three-lift selection are unchanged from that prepared version.

## Mathematical input and frozen variants

For the complete triangle-incidence matrix B of any hypothetical target,
C=ker_GF(2)(B transpose), A0=1, Aw>=0 and M=1+sum_nonzero Aw. Character
orthogonality and four low-image lower counts give for every j1..99

  sum_nonzero Aw*(Nj-Kj(w))/(binom(99,j)-Nj)<=1,

where Nj is the declared lower count for j3,4,5,6 and zero otherwise.
Kj(w)=sum_s(-1)^s binom(w,s)binom(99-w,j-s). Exact input retains every
coefficient. The dual seeks yj>=0 with every weight-row Gy>=1; any exact
dual proves M<=1+sum_y. It need not be optimal.

Frozen case population has two variants, selected explicitly by required
--weight-domain (no default):

* even13: weights36,38,...,60. Uses the earlier interval/even proof only.
  Full matrix13by99,1287 exact rational coefficients;13 inequalities.
* divisible4_seven: weights36,40,44,48,52,56,60. Adds the independently
  written divisible4 theorem. Full matrix7by99,693 coefficients;7 inequalities.

Each invocation runs exactly one selected case and records it in model,
certificate and summary. A certificate for seven weights cannot silently
be presented as an even13-domain certificate. Both are conditional bounds
on the same target-kernel object; neither assumes a nonzero kernel, upper
incidence rank, fixed graph profile, prism absence or an automorphism.

## Pinned premises and new checking gate

Source preserves and hash-checks genericV2 source453de424...; old thirteen
source90002c96... and seven source01ed2b4d... as copied-code provenance.
No past execution gate approves this changed guide. Earlier interval report
f6d37038.../independent written65d8ee... supplies only the weight premise,
not its numerical rank conclusion. For divisible4_seven, written proof
0231d687... is separately hash-checked; even13 does not use that premise.

Guide argv requires exact-hashed old3/4/6 audit626e4055... with status
INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS;
newN5 report dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2
at acceleration/results/20261003_independent_review/weight5_full02/summary.json
with status INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS,
target_unordered_paths24948/target_weight5_lower_count12474,
universal_derivation_checked true/new_exclusions0/rank_bound_claimed false;
and a NEW independently authored ROOT checker pre-output calibration.
The N5 report preserves failedfull01's message-transcription65hex veto,
successfulfull02's actual64hex producer identity, raw fibers and proof8844.

Prospective changed-checker interface required by source:
status INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_LP_CHECKER_V2_CALIBRATION_PASS;
verifier /root; full_producer_output_inspected false;
approved_weight_domains exactly
{'even13':[36,38,40,42,44,46,48,50,52,54,56,58,60],
 'divisible4_seven':[36,40,44,48,52,56,60]}; inputs_sha256 pins this exact
producer source and protocol. This interface is prospective, not an assertion
that such a checker/report has already passed. ROOT must author/review it
and authorize each full guide after fresh source/resource observation.

## Cheap author controls, unexecuted

Calibrate mode takes the same required weight-domain but invokes no solver.
It recomputes the literal rook9 full kernel16 and image32, with N3=6,N4=9,
N5=9,N6=6. A complete exact synthetic rook dual has U=512/31 and all
two kernel-weight inequalities equal1. All nine shifted character rows
are checked, including the new fifth-degree coefficients1/39,5/39.
Rook's nonzero weight6 explicitly cannot prove target divisibility.

For the chosen n99 domain, a full synthetic dual with
yj=(binom(99,j)-Nj)/39271 has all weight inequalities1 and U=2^99/39271.
Every1287 or693 raw coefficient, all99 coordinates and13 or7 rows are saved.
The existing140 literal small-character comparisons remain. Twelve precise
negatives reject sign/nonnegative/truncation/insufficient-dual/coefficient/
missing-population/denominator/A0/count defects; the two added negatives
overstate the rook N5 and change its row sign. These are producer calibration
only. Separate ROOT checking must reconstruct coefficients from a different
integer recurrence or character path, require full vector lengths and test
deliberate actual certificate/cell corruption.

Proposed author calibration commands are separate60outer40worker10guard
invocations with explicit even13 or divisible4_seven output roots. Evidence:
prior synthetic seven-weight controls .235seconds, newN5 controls .531seconds,
and one extra row shift have small complete populations. No calibration runs
or numerical results exist yet for this source.

## Prospective full execution and acceptance

Each full guide is separately authorized:120seconds outer,90worker,
10second supervisor shutdown guard,30second internal numerical/save reserve.
One native HiGHS simplex call only, max30seconds, thread1/random_seed0;
primal/dual tolerances1e-10, small_matrix_value1e-12. Floating coefficients
with absolute value<1e-11 are removed from the guide matrix only, with counts
saved. All exact coefficients remain in exact_model.json and certification.

The predetermined rational reconstruction limits are1000,1000000,1000000000.
Unlike preserved earlier guides' first-valid selection, this NEW driver
attempts all three on the same saved numeric vector, saving each positive
exact certificate_limit_<limit>.json and every failed minimum. It selects
the smallest exact rational U among those three for certificate.json;
this is a frozen finite lift selection, not another optimizer call or an
optimum claim. Unknown/failed lifts and raw numeric statuses are preserved.

Positive acceptance requires all99 exact rational dual coordinates>=0,
all13 or7 full exact inequalities>=1, exact U and the power-of-two comparison.
If U<2^k, then dimC<=k-1 and rankB>=100-k; equivalently maximum dimension
is the unique d with2^d<=U<2^(d+1). Existing validated dimension14/rank85
is only a comparison outcome, not a premise of the model. A stronger integer
result requires d<14; otherwise record new evidence without a stronger claim.
A numerical zero/optimal status/timeout is not a certificate or exclusion.

Schemas remain TRIANGLE_KERNEL_LOW_WEIGHT_EXACT_MODEL_V1 and
TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_RATIONAL_DUAL_V1, with additional
weight_domain field. Other exact fields retain prior layout; lower_word_counts
now includes '5':12474. No finite-field or float-only object is promoted.

Use supported Windows Job supervisor run_compute_command.py and the pinned
uv.lock environment, UV_PROJECT_ENVIRONMENT=build/research-venv,
uv run --locked --offline --cache-dir .uv-cache-20260917. Worker argv is
absolute Python/source, --mode calibrate or guide, --weight-domain explicit,
--seconds40 or90, --source-sha256/--protocol-sha256 and a new absolute --out.
Guide adds --low-weight-audit/--low-weight-audit-sha256,
--weight5-audit/--weight5-audit-sha256,
--checker-calibration/--checker-calibration-sha256. The exact literal execution
plan and actual source/resource admission must be frozen before launch;
unknown gate hashes are not invented. Source/protocol/deadline/supervisor/
environment and raw output identities, exact command/cwd/versions/sourceHEAD,
native limit and actual timings are saved. New source is separately pinned
until public commitment; historical sourceHEAD is not its publication claim.

No retries or deadline extensions. Every failure preserves outputs, attempted
lift records and exact restart requirements. Parent independently validates
every material certificate and conditional interpretation; discovery source
cannot approve itself. No ledger/index write, merge, external review, novelty,
code optimum, graph construction or general nonexistence claim is authorized.
