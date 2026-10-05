# Exact analytic q5 family producer V2

Source acceleration/construct_20261004_prime5_analytic_delsarte_v2.py.
The V1 t10/s122 source, raw candidate and degree29 result remain unchanged.
Root requested this finite family and supplied the image-count rescaling idea.
This is SOURCE_ONLY: no import, AST, syntax check, backend or family run.

## Frozen finite selection

For t in8,9,10,11,12,13,14,15, in that order, choose s values in this order:
first the forty integers121,...,160, then121+1/d for d2,4,8,16,32,64,128,256.
The latter strings are243/2,485/4,969/8,1937/16,3873/32,7745/64,15489/128,30977/256.
There are exactly8*48=384 distinct ordered cases. Case index is zero-based
lexicographic in those literal lists, with the stated rational ordering.
This is not a census of all rational s or all possible code duals.

q5/n99/nonzero minimum weight55 is fixed. Each t gives degree2t+1<=31.
Every successful certificate is padded to degree32; no degree33 is used.
The exact recurrence and Krawtchouk/product helper bodies come from V1:
p0=1, p_(k+1)=((s-3k)p_k-k*p_(k-1))/(4(99-k)), k0..t-1.
A nonpositive p immediately rejects this construction, saving all its computed
prefix including the failing value and index. It does not prove dual/code
infeasibility. If all p pass, g=(K1-s)p must have exactlyzero coefficients0..t-1
and g_(t+1)=(t+1)p_t. Nonpositive g_t is a second legitimate rejection with
all p/g coefficients and its precise value. Other exact identity failures are
fatal implementation failures, not silently classed as construction rejection.

For admissible p/g, f=g*p has all2t+2 nonnegative exact coefficients,
constant g_t*p_t*4^t*binomial(99,t)>0 and final coefficient positive.
Normalize by that constant, pad to32 and check the exact baseline dual:
all32 canonical nonnegative multipliers, weight0 and all45 tails55..99,
exact rational size and neighboring powers5/dimension. At every46 weights
the producer also verifies F=(K1-s)p^2/constant. s121 is permitted:
its weight55 factor iszero, an allowed nonpositive tail.

Kraw/product bodies are unchanged. Typed lru_cache entries memoize only
immutable integer inputs/results; typed=True keeps boolean aliases from
hitting an integer cache entry before the strict guard. No approximate
coefficient or solver result enters the process.

## Image-count rescaling

For a baseline F=1+sum y_j K_j and separately justified B_j>=ell_j>=0,
let d=1+sum y_j ell_j. Then
1+sum(y_j/d)(K_j-ell_j)=F/d.
MacWilliams gives |C|<=F(0)/d, with every tail sign unchanged.
The separate written candidate is
docs/CANDIDATE_20261004_CODE_DELSARTE_IMAGE_COUNT_RENORMALIZATION_V1.md.
No literature novelty is claimed.

The fixed low counts are ell3=924,ell4=8316,ell5=24948,ell6=391776.
Every admissible case saves both baseline{} and low-count certificates,
plus the exact rescaling denominator and all46 rescaled equality checks.
The low-count case needs the accepted image-count theorem's exact scope;
the formal worker does not reread a target matrix or authenticate those
theorem premises. Root pins their binding/report/acceptance externally.
Zero left code is permitted. A smaller rational bound may keep the same
integer dimension; no improvement below27 is promised.

## Four fresh author controls

Total4=2positive/2negative. The indices and first stages stay:

|index|action|expected|
|---|---|---|
|0|n2 product coefficients[8,3,2]|PASS;values64,9,4|
|1|n2 full-space baseline plus exact image rescaling|PASS|
|2|wrong product constant9|PRODUCT_COEFFICIENT|
|3|negative first multiplier-1|MULTIPLIER_SIGN|

Control1 retains baseline y1=y2=1,size25,dimension2,zero tails. It additionally
uses ell1=8,ell2=16, denominator25, new size1/dimension0/zero tails.
That second premise applies to C={0},D=full space. It cannot be applied to
C=full space,D={0}, where the asserted positive image lower counts are false.
No target recurrence or target family case is evaluated in calibration.
No old V1 calibration qualifies V2; these four actual actions need a fresh run.
Nine non-summary author payloads plus summary=10 physical files are retained.

## Output, objective and stop rules

Every completed scientific case saves case_NNNN.json and its separate
case_NNNN_checkpoint.json, including legitimate rejection prefixes or both
complete candidates. All384 completed cases give768 payloads+summary769 files.
All computed traces and every rejected p/g are retained. Case checkpoints
record cumulative valid/rejected totals, first-stage counts and both best
candidates. The exact objective is lowest rational size upper within the
frozen family; ties retain the first case index. Every best includes actual
dimension and adjacent powers5, with honest comparison to historical27.
No float, optimum over all duals or graph/code realization is claimed.

Use supported local Windows SUPv2 plus pinned locked/offline uv and the
same CommandDeadline across all preparation, arithmetic, writes and seals.
Author plan180outer150worker20save20shutdown. Family proposal600outer550worker
20save20shutdown. The larger allocation covers384 cases versus the observed
single V1 .328s complete invocation, higher t<=15 and768 file seals. This is
an allocation rationale, not linear runtime or success forecasting.
All modes have zero LP/backend calls and no automatic retry.

A tick requires more than20 worker seconds. Roots must be absent; files use
exclusive creation. Context records active/completed cases. Normal case
completion flushes both outputs before advancing. Unexpected exception or
hard kill cannot guarantee the current unsaved case prefix; previous completed
cases remain. Failure saves phase/progress/deadline if possible. A final tick
after summary can leave a provisional summary with nonzero failure, requiring
supported clean terminal and Root review before qualification.

Run schema PRIME5_ANALYTIC_DELSARTE_RUN_V2, implementation2.
Author status PRIME5_ANALYTIC_DELSARTE_V2_AUTHOR_CONTROLS_PASS.
Science status CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V2_FAMILY_COMPLETE.
Certificate schema EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1 is unchanged.
The six worker software pins and raw certificate semantics are unchanged
except new source/spec and the explicit lower-count path. Actual future
control/science/checker hashes remain null until genuine.

## Independent requirement and limitations

A distinct checker must authenticate new source/runtime applicability and
the exact384 ordered population, check all rejected prefixes and g signs,
and independently verify every baseline/low-count certificate with its own
Krawtchouk coefficients, all45 tails,32 multipliers, denominators, powers and
objective selection. Cached producer arithmetic is not an independent check.
The existing generic degree32 math core can be reused only with a new explicit
source/packet adapter and applicable controls. Old V1 and numerical gates stay
historical.

Target applicability uses accepted support55 and image-count claims pinned
by Root. No nonconstant/nonzero code, automorphism, target existence or
exclusion, rank gain, live ledger/index/Git change or broader family coverage.
