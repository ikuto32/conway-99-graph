# Prepared direct binary MIP on one Hadamard support

Preparation only; no invocation is authorized by creation of this document.
This is a different solver representation from the preserved SAT models.
Select the same fixed six-prism L after the exact exclusions of the four
other frozen supports. Retain all 90 local colourings in each of 60 columns,
with no cyclic constraint, complementary bits or target automorphism.
The independent identical-support order normalization remains applicable.
This single-support construction attempt has no residual D and no global
core or target coverage.

Reconstruct the literal 5,400-column, 726-row equality matrix and compare it
exactly with hadamard_support_remaining_lp/six_prism/exact_model.json
(SHA256 f5ac7adc289d6ca3cc7ce77394565919813138f6322e5ae2dc1856684eef6ae2).
The first 60 rows are one-hot equalities. The next 666 are upper-triangular
Gram equalities, including all 36 diagonal row sums. Every variable is
integer with bounds [0,1]. For each of the 40 adjacent identical-support
column pairs append sum(rank*x_left)-sum(rank*x_right)<=-1. On one-hot
binary choices this is precisely strict ascending option rank. Save exact
integer row indices/coefficients, bounds, integrality, all option mappings
and all order rows. Convert to floating coefficients only when supplying
HiGHS; these small integers are exactly representable. Objective is zero.

Initial research budget: one 120-second wall-clock budget across at most
three HiGHS run() calls, one retained solver instance, one thread, seed 0.
Set each call's time_limit to the remaining budget. Do not call clearSolver,
reset the solver or retry after errors. Preparation/checking between calls
consumes the same budget. Native time limits are cooperative, so preserve
observed overrun if any; a parent may add a 135-second outer process guard,
whose expiry leaves the attempt UNKNOWN with raw files retained. No
performance comparison or assumed process liveness. Python uses the existing
locked environment: highspy 1.15.1, numpy 2.5.3, scipy 1.18.1, tqdm 4.67.1.
No installation or lock changes.

With zero objective, every feasible integer solution is an optimal
incumbent; preserve the complete returned native floating vector, native
status, validity flag, information fields, actual options, logs and timings
for every call. Require all 5,400 finite values to be within 1e-7 of 0 or 1
before decoding. Record the maximum observed rounding distance and perform
all equality/order tests again over integers. A close floating vector is
not a certificate until those exact tests pass and a separate checker
reconstructs the raw factor. An independently accepted Gram factor with
outside-cap violations is useful saved evidence but is not a full factor
candidate for residual completion.

After each exact integer Gram-factor incumbent, save its full raw F, exact
selected options, all 1,770 overlap counts and every cap violation. For each
violating selected option pair add x_i+x_j<=1. This rejects only an actual
outside-cap violation and is therefore sound for all target-compatible
factors of this support. Add all distinct newly encountered violations in
sorted order; save the ordered cut list and complete augmented exact matrix
hash before the next call. Do not discard the violating raw factor. No
full pair-cap universe is silently omitted from final object validation.

Stop immediately for independent review if an exact incumbent passes all
Gram, margin, order, fixed-L, mixed-cap and outside-cap checks. Otherwise
continue only for new justified cuts while calls and time remain. Stop on
no integer incumbent, duplicate-only cuts, error or budget. Numerical
infeasibility, an optimal floating status, absence of an incumbent or timeout
is never promoted to exclusion. This workflow produces no proof of UNSAT.

Separate pre-research controls exercise a small known integral positive MIP,
exact matrix reconstruction, strict ordering, deliberately fractional and
out-of-range vectors, incorrect bounds/coefficients and a false lazy cut.
Controls do not invent a complete research-factor positive. Root reviews
source first; a separate independent MIP matrix/object calibration gate
must bind the exact prepared model and this source before research. The
independent raw path must permit classification of Gram-valid/cap-invalid
objects and require every cap for a complete factor. No producer approval.

Commands are separate prepare, controls and research modes, each with a new
output directory. Preparation/controls are not research calls. Research
requires --matrix, --review-gate and --review-gate-sha256. Manifests pin the
original support, exact LP matrix, order/support gates, lock, source/spec,
package versions, platform and exact command. Preserve any failure record
and partial files without overwriting previous runs.
