# Exact analytic q5 Delsarte candidate producer V1

Source: acceleration/construct_20261004_prime5_analytic_delsarte_v1.py
This new physical source is independent of the numerical producer. It imports
only standard Python libraries and the pinned CommandDeadline. It does not
import the numerical producer, a verifier, scipy or any solver. Root supplied
the truncated multiplication idea; Structural supplied the explicit recurrence.
Engineering controls do not independently prove the scientific polynomial.

## Scope and mathematical contract

The scientific mode constructs a formal dual for any linear F5 code of
length99 with no nonzero weights below55. Target applicability requires the
separately accepted C-UNRESTRICTED-TARGET-PRIME5-LEFT-CODE-SUPPORT-LOWER55 r1.
No target adjacency, incidence matrix, codeword or graph is read. That
binding/report/Root acceptance is pinned by the scientific plan outside this
worker; support_assumption_authenticated_inside_worker is honestly false.
No nonzero code, optimum or graph exclusion is forced.

The exact derivation is
docs/CANDIDATE_20261004_PRIME5_ANALYTIC_DELSARTE_DUAL_V1.md.
q5/n99/t10/s122 are fixed. The rational recurrence is
p0=1, p_(k+1)=((122-3k)p_k-k*p_(k-1))/(4(99-k)), k0..9.
Every p entry must be positive. Multiplying by K1-122 yields exactly zero
coefficients0..9, g10=10p9-92p10>0, and g11=11p10>0.

The coefficient of K_h in K_a K_b is
[X^aY^b](1+4XY)^(99-h)(X+Y+3XY)^h.
For each cancellation count d, put c=a+b-h-2d, u=a-c-d, v=b-c-d.
The nonnegative integer term is
binomial(h,c)*binomial(h-c,u)*3^c*binomial(99-h,d)*4^d,
only when c,u,v>=0 and u+v+c=h.
All22 coefficients of g*p are saved and nonnegative. The constant is
g10*p10*4^10*binomial(99,10)>0 and must match the independently formed
product constant. Coefficient21 is strictly positive.

Normalize by that constant; pad coefficients22..32 with zero. The exact
certificate uses schema EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1:
q5/n99/minimum_distance55/degree32/dual_lower_counts{},32 canonical rational
multipliers,46 polynomial values (weight0 and all45 weights55..99), size
upper, exact integer-dimension upper and adjacent powers5. Fractions use
their reduced str(Fraction) spelling, with no boolean or numeric alias.
The producer verifies every tail<=0, size>=1 and exact factorization identity
at all46 weights. It compares the final dimension to27, honestly, without
claiming beforehand that it improves that bound. LP_calls is always zero.

The constant-basis-one MacWilliams argument is conditional on the linear-code
hypothesis. A zero of p only gives an allowed zero tail. Negative coefficient,
wrong product constant, noncanonical fraction, positive tail or failed exact
factorization causes a nonzero failure; no clipping or approximate acceptance.

## Four small author controls

The action order and first stage are:

|index|action|expected|
|---|---|---|
|0|n2 K1 squared coefficients [8,3,2]|PASS; exact values64,9,4|
|1|q5 n2 d1 y1=y2=1|PASS; size25,dimension2,tail0,0|
|2|change product constant8 to9|PRODUCT_COEFFICIENT|
|3|change first multiplier1 to-1|MULTIPLIER_SIGN|

These use actual product_fixture/dual functions. No target recurrence or
target polynomial is evaluated during calibration. There are two positive
and two negative actions. No separate trusted target witness is invented.
Calibration saves four fixture payloads, four small progress checkpoints and
controls.json:9 non-summary payloads plus summary=10 physical files.

## Invocation, containment and stops

Use pinned locked/offline uv in build/research-venv under supported local
Windows SUPv2, CommandDeadline and an explicit allocation. Both proposed
modes are180 outer/150 worker/20 save/20 shutdown; Root owns all actual
admission/launches. Six hours is a ceiling, not a target. These allocations
reflect at most22-by22-by11 small exact combinatorial terms,32 multipliers,
46 values and ten recurrence steps. They are ceilings, not runtime forecasts.

Each tick requires strictly more than20 worker seconds remaining. The same
deadline covers all rational/combinatorial arithmetic, software reads,
checkpoints, output hashes and final seals. There is no internal retry.
Source/spec/CommandDeadline/SUPv2/pyproject/uv.lock are authenticated as six
direct worker inputs. Launchers are additionally checked by Root admission.

The output root must be absent and resolve under acceleration/results.
Each file uses exclusive creation. Scientific mode flushes each of ten
recurrence prefixes before expansion, then saves construction.json,
certificate.json,polynomial_values.json,construction_checkpoint.json:
14 non-summary payloads plus summary=15 physical files.
construction records all11 p,12 g and22 f coefficients and exact constant.

On exception, save failure.json if possible; all already written outputs
remain. A hard kill cannot guarantee the pending unsaved suffix. A final tick
after summary save can leave a provisional summary with nonzero failure;
clean supported terminal, full declared population and Root review are
required. No exit0 alone or provisional summary is a gate.

## New applicability and independent check

Run summary schema PRIME5_ANALYTIC_DELSARTE_RUN_V1, implementation1.
Calibration status PRIME5_ANALYTIC_DELSARTE_V1_AUTHOR_CONTROLS_PASS.
Science status CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V1_COMPLETE.
Producer Structural; actual executor is authenticated separately from SUP
by Root. No Native review timestamp or future gate is fabricated.

A distinct exact checker must verify32 canonical nonnegative multipliers,
all45 tails and weight-zero size from its own Krawtchouk implementation,
dimension/powers, exact file population and supported runtime. It may also
falsify recurrence/product trace independently. The mathematical certificate
format lies in the generic degree32/45-tail domain, but the new producer's
source/runtime applicability requires a fresh explicit adapter and gate:
old numerical source gates do not qualify this source.

No live ledger/index/Git/PUBLIC metadata changes, code enumeration or
automorphism premise. Earlier numerical status2 results stay UNKNOWN and
unchanged. The science plan remains unlaunchable until Root ONE authority
and applicable genuine author control receipt are bound.
