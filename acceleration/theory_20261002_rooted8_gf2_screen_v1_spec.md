# Rooted-eight literal GF2 consistency screen, version 1

Question: does any exact parity consequence of the frozen 85,874-row,
23,019-variable integer equality model exclude one of its 210 parameter points?
Use every point `0<=a<=20,0<=b<=9`, in ascending `(a,b)` order, without omissions.
Input is the unscaled rooted8 model SHA256
`a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
The necessary-model derivation and fresh root8 coverage still require a
separate audit. An exact literal inconsistency is only a model result until then.

Encode each complete coefficient row and its three affine RHS coefficients
modulo two in a Python integer bitset. Least-significant variable pivots reduce
every original row, retaining its complete original-row XOR witness. Record
every distinct nonzero residual affine RHS after the variable columns vanish.
Replay each witness first as a packed-row XOR and then by ordinary scalar
coefficient addition modulo two across every raw variable and RHS coordinate.
Only the zero-left/nonzero-selected-RHS criterion excludes an integer profile.
A consistent profile is not an integer primal or a graph certificate.

Before the scientific invocation, the same frozen source has a separate
`--controls-only` run. Require consistent/inconsistent examples, a complete
scalar replay and rejection of changed witness, changed RHS and changed raw
coefficient. Source/model/spec hashes and the calibration receipt bind this
protocol. Another agent must independently replay any claimed relation and
approve necessary-model coverage before mathematical promotion.

Allocate a supported outer 600 / worker 560 seconds from the root7 packed
GF2 measurement of 0.782 seconds, with roughly eight times as many columns and
seven times as many rows here. This is an evidence-based allowance, not a
performance guarantee. Recheck host memory before launch. Preserve the active
LP invocation's existing deadline unchanged. A separate invocation has its
independent allowance. At a worker stop, save the processed-prefix pivots and
original-row witnesses in a compressed JSON checkpoint with exact source/model
pins. An incomplete reduction gives no complete-model consistency assertion.
No automatic resume is authorized; a restart needs unchanged pins and a
separately declared invocation. No floating-point calculation is used.

Target resolution: UNKNOWN. Overall search coverage: UNKNOWN; no validated
denominator. Complete model coefficients, not physical graph coverage, are the
population behind a reduction completion count.
