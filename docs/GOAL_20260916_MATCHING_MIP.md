# One free matching and joint phase-I optimization

This records the earlier 7.332122 base assignment. The subsequent complete
same-sign search and improved 7.316246 seed are documented in
[the whole-matching search continuation](GOAL_20260916_WHOLE_MATCHING_SEARCH.md).
The family exclusions below remain tied to the original base assignment.

The atomic-cycle pilots leave the best merit at 7.33212201. Their fixed-X
scores rank endpoints before reoptimization, and all other matching choices
stay implicit in a small shortlist. This continuation implements
optimizing one entire matching jointly with the 1,680 fractional disjoint
edges. The other 20 matchings remain fixed. This is still a restricted
necessary-condition search, not the original graph problem or a global proof.

## Why the partial-graph constraints are linear

Let B be the full 99-vertex known adjacency matrix after deleting the chosen
matching. Let Y be a replacement matching on the same vertex set S, with
binary variables for geometrically permitted edges. Matching degree equations
give every vertex in S exactly one partner. All other Y rows are zero.
The partner map is injective, so `(Y^2)[u,v]=0` for distinct u and v.
Consequently the hard partial-graph constraints are exactly

`(B^2 + BY + YB + B + Y)[u,v] <= 2`, for all `u < v`.

The adjacency terms B and Y are essential: a present edge has a common-neighbor
cap of one, rather than two. These constraints remain hard when the completion
residuals below receive slack. Matching constraints preserve the chosen
own-label category and degree; added-support legality is imposed separately.

A same-sign coordinate has 60 possible binary edges on 12 vertices. A cross
coordinate has 120 possible binary edges on 24 vertices. Excluding forbidden
same-fibre partners leaves 6,040 or 59,245,120 possible perfect matchings before
the common-neighbor caps. These counts concern one coordinate with all other
coordinates held fixed.

## Eliminating the binary-continuous products

Write X for the symmetric matrix of disjoint-edge variables, zero outside
that support, with entries in [0,1]. The necessary outer-pair inequality is

`[(B+Y)^2 + (B+Y) + (B+Y)X + X(B+Y) + X][u,v] <= 2 + t[u,v]`.

The nonnegative XX contribution of a full graph is omitted, exactly as in the
existing phase-I relaxation. Each pair has one nonnegative slack t. The
foreign-label equalities remain affine in X and Y and use absolute-residual
slacks. The objective is the sum of these quota and pair slacks, with unit
weights.

All vertices in S contain the same root group a. If both endpoints of a row
contain a, all relevant YX/XY entries vanish because disjoint-support X cannot
join two such vertices. Otherwise a nonlinear row can be oriented with u in
S and v outside all 24 vertices containing a. Only u has a variable partner.
Set

`H[u,v](X) = (B^2 + B + BX + XB + X)[u,v]`.

For a possible partner p of u, define `g[v,p] = B[v,p] + X[v,p]`. The two
summands have disjoint supports, so `0 <= g[v,p] <= 1`. With selected partner
p*, the true row is `H + g[v,p*] <= 2 + t`. It is equivalently encoded by

`H <= 2 + t`,

`H + g[v,p] + Y[u,p] <= 3 + t` for every allowed p.

The selected partner enforces the original row. Every unselected inequality
is dominated by the baseline and g<=1. Therefore the smallest shared slack is
exactly `max(0, H + g[v,p*] - 2)`. The coefficient one is sufficient; a large
generic big-M is unnecessary. Giving each indicator a separate slack would
change the objective and is not this model.

This avoids 4,800 or 9,600 product variables that a direct McCormick encoding
would need. With 840 foreign-label rows and all 3,486 outer-pair slacks, the
unsimplified model has about 6,906 same-sign or 6,966 cross-coordinate columns.
The actual row count depends on elimination of constant and duplicate rows.
At integral Y, minimizing this model is equivalent to minimizing the existing
phase-I merit over all legal replacements of that one matching.

## Validation and claim boundary

The implementation must first fix Y to the original matching and reproduce
the old fixed-K LP objective. Separate full-graph controls check the affine
partial caps and indicator slack identity on integral matching replacements
and fractional X. Projected MIP candidates must have an integral perfect
matching and pass independent full99 graph checks. Their merit is then
reoptimized and bounded with the unchanged fixed-K IPM and rational auditors.
Complete-star pair AC remains an independently checked endpoint condition.

A bounded MIP run is a candidate generator. Its floating-point objective,
bound, gap, node count, or terminal status is not an independently verified
neighborhood exclusion. A fractional relaxation, a time limit, or reuse of
the initial incumbent gives no new graph or proof. Freeing two matchings
would generally restore nonzero off-diagonal YY terms and is outside this
derivation. Even exact zero merit would only satisfy a necessary relaxation;
all 99 degrees and 4,851 vertex pairs still need a full graph witness.

## First implementation and exact algebra controls

`acceleration/matching_phase1_mip.py` implements the compact model using the
installed HiGHS MIP solver. It saves the raw solver vector and matching
values, the independently reconstructable returned matching and X, residuals,
all shared slacks, source/input hashes, and explicit time/gap/status fields.
The initial K/X point is a feasible fallback. A returned rounded matching
must pass full graph and matching checks, and the reconstructed fixed-K
residual slacks must satisfy the assembled model. Numerical bounds never
become exclusion claims.

The producer-free `20260916_matching_indicator_audit.json` checks sixteen
real-graph controls: cross and same-sign coordinates, original and valid
atomic replacements, and four exact quarter-valued X vectors. It verifies
19,404 partial-cap identities, 55,776 joint-cap rows, 18,816 label coordinates,
and 172,800 indicator inequalities. Minimum shared slacks and the old fixed-K
residuals agree exactly. Separate real controls show why M=0, double-counting
the B partner term, or summing separate indicator slacks is wrong.

The root-group-3 cross model has 6,966 columns, 20,826 rows and 128,046 nonzero
coefficients. Fixing its binary choices to the initial matching yields merit
7.33212201868121, within 4.97e-9 of the saved 7.332122013712173. Building takes
0.11 seconds and the fixed-choice IPM solve takes 0.93 seconds. This is a
numerical model control, complemented by the exact algebra controls above.

The first free cross-matching probe reaches its 30-second solver limit and
returns the unchanged initial matching/X point. It reports zero completed
branch-and-bound nodes, numerical lower bound zero and gap one. These facts
provide no neighborhood exclusion or improvement. The retained point remains
the already excluded fixed assignment. Outputs are in
`acceleration/results/20260916_matching_mip_fixed_cross3` and
`acceleration/results/20260916_matching_mip_cross3`.

```powershell
.venv/Scripts/python.exe -B acceleration/matching_phase1_mip.py --initial acceleration/results/20260916_two_trade_pilot/best_candidate.json --initial-phase1 acceleration/results/20260916_two_trade_pilot/best_phase1.json --out acceleration/build/matching_cross_control --root-group 3 --class cross --seconds 30 --fix-initial
.venv/Scripts/python.exe -B acceleration/matching_phase1_mip.py --initial acceleration/results/20260916_two_trade_pilot/best_candidate.json --initial-phase1 acceleration/results/20260916_two_trade_pilot/best_phase1.json --out acceleration/build/matching_cross_search --root-group 3 --class cross --seconds 30
```

Both output paths must be new. The current producer keeps exactly one matching
free; the other 20 are the input assignment. Changes to this scope require a
new derivation and independent checks.

## Exact exclusion of an entire matching coordinate

The root-group-3 `same_0` fixed-choice control reproduces the saved merit
within 9.59e-9. Its free MIP run also reaches the 30-second limit without a new
matching. Independent full-graph checks of both cross and same-sign returned
points confirm that their labeled overlap edges are unchanged. The prior
exact fixed-K and complete pair-domain proofs are reused through checked
graph identity; solver noise is not counted as an improvement.

The separate continuous relaxation gives a numerical objective of
1.1769910422845806 for `same_0`. The cross relaxation is numerically near zero.
Neither floating result is itself a proof. Adding 1,012 size-3/5 odd-set
inequalities to the same-sign model does not materially improve its numerical
bound and is unnecessary for the certificate below.

`certify_matching_relaxation.py` rounds the same-sign row marginals to signed
integer multipliers. `audit_matching_farkas.py` independently reconstructs
all 12,648 rows, 6,906 columns, and 77,526 nonzero coefficients from full
99-vertex adjacency, without importing the model producer or an optimizer.
It checks every bound, variable coordinate, and shared-slack position before
checking the integer combination. A full graph completion would set all
5,166 nonnegative completion slacks to zero. For the remaining 1,740 boxed
X/Y variables, the 1,315 weighted rows then imply

`C · v >= 1,264,132`, while `0 <= v <= 1` implies `C · v <= 87,369`.

The strictly positive difference **1,176,763** is verified using integers
only. Therefore **every replacement of root-group-3 / same_0 is excluded
when the other 20 matchings are fixed to the current best assignment**.
The independently counted domain contains 6,040 perfect matchings before
partial-cap filtering. The proof covers that entire domain, including
replacements involving multiple disjoint alternating cycles, rather than a
shortlist of sampled endpoints. An additional independent arithmetic/scope
review agrees with the certificate.

This is a conditional family exclusion. It does not exclude changing another
matching simultaneously, the full E0 class, or all Conway-99 graphs. It also
does not prove a local minimum for the positive phase-I merit: some family
members could still improve 7.33212201 while remaining impossible to complete.
The best search assignment and its merit are unchanged.

The matrix, integer certificate, and independent report are preserved in
`acceleration/results/20260916_matching_lp_same0`. The check uses the standard
library only:

```powershell
python -B acceleration/audit_matching_farkas.py --candidate acceleration/results/20260916_two_trade_pilot/best_candidate.json --matrix acceleration/results/20260916_matching_lp_same0/matrix.json --certificate acceleration/results/20260916_matching_lp_same0/integer_certificate.json --out acceleration/build/matching_farkas_replay.json
```

Use a fresh output filename. Solver reruns are unnecessary for this proof.

## All 21 coordinate diagnostics

The next bounded sweep evaluates each of the 21 coordinates at the same
initial K, reusing the two previous plain LPs and running 19 new ones. It
finishes in 34.73 seconds with no capped or unresolved LP runs. Eight
same-sign coordinates yield positive integer contradiction candidates:

| Root group | Class | Numerical LP objective | Integer contradiction margin |
| --- | --- | ---: | ---: |
| 0 | same_1 | 0.66930324 | 669,071 |
| 1 | same_0 | 0.60441270 | 604,177 |
| 2 | same_1 | 0.91985809 | 919,632 |
| 3 | same_0 | 1.17699104 | 1,176,763 |
| 3 | same_1 | 0.95108529 | 950,836 |
| 4 | same_0 | 0.18763605 | 187,377 |
| 5 | same_0 | 0.18687721 | 186,596 |
| 6 | same_0 | 1.77550347 | 1,775,222 |

Each margin is computed with integer row multipliers rounded at scale
1,000,000. The integer margin establishes an empty zero-slack box system
after independent semantic verification; dividing it by that scale is not
asserted to give a bound on the nonzero phase-I objective.

The other 13 coordinates, including all seven cross coordinates, have
numerically near-zero relaxation objectives. They have no exact feasibility
certificate and no integral replacement candidate from this sweep. The
complete input/source/output bindings and numerical statuses are preserved in
`acceleration/results/20260916_matching_all21/summary.json`. Its historical
"audit required" fields describe the producer's state; independent proof
audits remain separate artifacts.

All **eight** integer certificates now pass independent matrix and arithmetic
audits. Seven reports are new; the byte-identical root-group-3 / same_0 proof
reuses its previously completed check. Together the reports rebuild 101,184
rows and check 620,208 nonzero matrix coefficients and 10,607 weighted rows.
`acceleration/results/20260916_matching_all21/independent_batch_audit.json`
binds these reports and verifies the matching-coordinate decomposition.

The allowed edge domains of distinct coordinates are disjoint, and each
family fixes all domains except its own. Two distinct-coordinate families
therefore intersect only at the unchanged base K. The independently checked
union contains exactly **1 + 8 × (6,040 − 1) = 48,313 labeled overlap
patterns** before partial-cap filtering. This count includes patterns already
invalid under those caps; it is not a count of inequivalent graphs or new
valid partial graphs. Simultaneous changes to multiple matchings remain
outside this union, and the 13 numerical-zero coordinates remain unresolved.

The original target is still active and incomplete. The conditional proofs
and completed numerical diagnostics are saved progress, not a construction
or a general nonexistence theorem.

The semantic auditor also rejects all 25 corruption controls, including a
different valid base graph, changed coordinates, reordered variables, altered
coefficients/bounds, a missing row, invalid multiplier signs/types, and false
combined totals. Modified matrices receive updated hashes in these controls,
so rejection tests the semantics rather than only the original file digest.
A valid certificate scaled by 10^30 still passes, checking unbounded integer
arithmetic. Evidence is in
`acceleration/results/20260916_matching_lp_same0/corruption_controls.json`.

CI now includes the standard-library replay of the original same_0 proof.
The local independent checks pass; this continuation has not run GitHub CI.

The complete continuation is indexed in
`acceleration/results/20260916_matching_checkpoint.json`, with hashes of the
model controls, proof/audit artifacts, and the preceding atomic checkpoint.
Historical indices and frozen source files are preserved.

A concrete next search route is complete Rust generation of same-sign
matching replacements, with independent enumeration against the 6,040-domain
count, hard partial-graph checks, CUDA fixed-X ranking, and bounded fresh LP
probes. This would include disconnected alternating cycles and five-/six-edge
changes missed by the current atomic3/4 subfamilies. The six numerically-zero
same-sign coordinates are natural initial controls. Exact family exclusion
must not be used to discard a coordinate when the aim is merely to improve
positive merit: such an improvement can still be useful as a seed for later
changes to other coordinates. This generator is a next step, not implemented
or counted as completed coverage here.
