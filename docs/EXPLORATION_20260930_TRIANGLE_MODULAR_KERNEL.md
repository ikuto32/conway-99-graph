# Bounded modular mixed-equation route

Status: CANDIDATE producer record, not a new independently verified theorem.
The target remains UNKNOWN. No target automorphism or prism-free hypothesis
is assumed, and no novelty is claimed.

The existing independent target-rank derivation already gives rank_F2(A)=54,
rank_F3(A)=45 and rank_F2(27I-9A+J)=44. The universal39-core Gram SOS record
and pinned archive Wave58 section2 already explain automatic real PSD and
the real incidence Gram kernel. This exploration does not count those facts
again or inherit Wave58's additional endpoint assumptions.

For a specified core C and factor F, put H=2J-(I+C)F. Any residual completion
requires FD=H. Over every field, a row vector w satisfying wF=0 must then
satisfy wH=0. This provides an exact, cheap necessary condition for a future
factor. It does not establish a symmetric zero-diagonal binary D, its degree,
or the remaining quadratic residual equation. Merely restating this linear
solvability condition is not claimed as new mathematical progress.

The bounded question was whether a modular Gram equality and modular margins
alone automatically imply this condition. In the known nonempty SRG243
fixture, choose v with Fv=0, sum(v)=0 and v.v=0, and u whose sum on each
fibre is zero. Then F'=F+uv^T preserves FF^T over the field, as direct
expansion shows. It also preserves every row margin and each column's fibre
sum. Such F' is a modular matrix, not an asserted binary graph incidence
factor; a parameter243 counterexample would not by itself settle a claim
restricted to Conway99.

The saved run tested128 deterministic perturbations over GF(2) and128 over
GF(3), using seed20260930. Every perturbation passed the modular Gram and
margin identities, but none produced a left-kernel witness contradicting
FD=H. The observed modular row ranks were57 for all binary-field trials and
48 for all ternary-field trials; these ranks are producer telemetry, not an
independently established rank claim. The input243 factor had reported ranks
57 and47 respectively. No universal consistency theorem or obstruction
follows from this finite failed attempt.

Controls used the exact integer243 Gram, mixed and residual quadratic
identities, a changed mixed RHS rejected by its actual D, and the rook9
triangle's explicitly empty residual. Every computed modular nullspace
vector was checked by multiplication with its original matrix. The protocol's
counterexample-corruption check was conditional on finding a counterexample;
it was not reached, and must not be reported as a successful executed test.

Evidence: acceleration/results/20260930_triangle_modular_kernel/manifest.json
and summary.json, latter SHA256
70a7c9600ac6283f7593e93e91920024258fa527733e515a12a0e9d2a07b01ee.
No solver was called; the bounded exact experiment completed in about three
seconds. Replay to a new directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_triangle_modular_kernel.py --out acceleration/results/NEW_MODULAR_KERNEL_REPLAY
```

The next useful application is checking a genuinely obtained factor against
the exact mixed equation; no further random modular perturbation campaign
is justified by this result alone.
