# Global phase-I merit for overlap search

The checked full-pair-arc-consistency survivor still has an exact linear
contradiction (RHS -5,404). This motivates a search merit that measures the
global necessary linear constraints, rather than only local support.

Fix one legal complete overlap assignment K. Let x contain the 1,680
disjoint-edge variables in lexical outer-vertex-pair order. The independent
full-99-vertex graph derivation gives 840 nontrivial root-label equalities
and 3,486 outer-pair upper bounds. The other 336 root-label equations are
zero equals zero. Zero-term pair inequalities remain harmless tautologies.
No disjoint compression totals are assumed.

For these rows define

\[
 F_K(x)=\sum_{i\in E}|a_i x-b_i|
       +\sum_{i\in C}\max(0,a_i x-b_i),\qquad 0\le x\le1,
 \quad \phi(K)=\min_{x\in[0,1]^{1680}}F_K(x).
\]

All summands are nonnegative. Therefore phi(K)=0 is equivalent to
feasibility of this necessary continuous linear system. It does not supply
a graph, integrality, or the discarded unknown-unknown common-neighbor
products. A positive numerical optimizer result is a search signal, not an
exact infeasibility certificate.

## Fixed-X scoring and safe bounds

Any fixed box-feasible x gives **phi(K') <= F_K'(x)** for every legal new
overlap assignment K'. Thus GPU evaluation of F at frozen X gives an upper
bound for each candidate's optimized merit. It can order candidates cheaply,
but that ordering need not match their optimized merits.

There is a useful monotonicity guarantee. If x optimally solves the current
K, then accepting K' with F_K'(x) <= F_K(x) ensures phi(K') <= phi(K).
If optimality is only numerical, retain an exact lower bound L on phi(K):
the stricter condition F_K'(x) < L certifies actual strict improvement.
In both statements the displayed F value must itself be evaluated exactly
or bounded in the required direction. An uncorrected floating-point
comparison is only a numerical heuristic.

For any weights y_i in [-1,1] on equality rows and [0,1] on cap rows, define

\[
 L_K(y)=-\sum_i b_i y_i
          +\sum_{j=1}^{1680}\min\{0,\sum_i a_{ij}y_i\}.
\]

Then **L_K(y) <= phi(K) <= F_K(x)**. To see this, each absolute value or
positive-part term is at least y_i(a_i x-b_i). Minimizing this linear form
over the box contributes min(0,(A^T y)_j) independently for each coordinate.
The same y, indexed by the full row coordinates, remains dual-feasible for
another K': its sign intervals do not depend on K. It consequently gives
a lower bound for ranking that candidate as well. Missing tautology weights
can be extended by zero before transferring the vector.

With the standard solver formulation Ax-s+ +s-=b and Ax-t<=b, each y is
the **negative** of the corresponding solver row marginal. The checker
tests this convention through primal-dual agreement and KKT residuals.

## Exact certificate extraction

Let c=A^T y. Add the nonnegative upper-bound weight max(0,-c_j) to the row
x_j<=1. The combined left coefficients are c_j+max(0,-c_j)>=0, and the
combined right side is

\[
 b^T y+\sum_j\max(0,-c_j)=-L_K(y).
\]

If L_K(y)>0 exactly, this is a contradiction for x>=0. Rational weights
can be cleared to integers and checked by the existing producer-independent
Farkas auditor. Approximate weights can also be rounded and repaired by the
same upper-bound correction; the resulting integer RHS must still be
strictly negative before making an exclusion claim.

`acceleration/audit_phase1.py` derives every row from the actual partial
99-vertex adjacency. It compares the producer's row metadata, verifies the
variable order, recomputes all residuals, checks the primal-dual gap and KKT
conditions, and computes bounds using exact rational representations of the
stored binary floating-point values. Small solver bound excursions are
clipped to produce a valid box point and valid dual sign intervals. The
report records clipping and separates numerical agreement from exact bound
claims. The evaluator imports no optimizer or producer mapping.

For uncrossed interior-point solver results, use the successor
`acceleration/audit_phase1_kkt.py`. The original evaluator and its existing
GPU/source bindings remain unchanged. A thresholded derivative diagnostic
in the original checker was unnecessarily strict close to a nonsmooth
kink: a cap residual of -2.62e-7 and multiplier 4.22e-5 have a tiny actual
complementarity product of 1.11e-11. The successor instead checks, with
exact rational arithmetic, that every Fenchel row slack and box slack is
nonnegative and that their sum equals the exact primal-dual gap. It retains
the original thresholded values as diagnostics, and still requires a small
total gap. No rejected IPM result was credited by the original checker.

## Independent control results

The four controls in
`acceleration/results/20260916_phase1_independent_review_v2/review.json`
all pass independent graph-row, residual, primal-dual, and exact
complementarity checks. The stored source and input hashes are bound in the
report. The absolute gap below is an exact rational difference, displayed
approximately.

| Fixed K / solver | Primal merit | Exact dual lower bound | Gap |
| --- | ---: | ---: | ---: |
| Old three-trade walk / simplex | 53.6006222366861 | 53.6006222366226 | 6.35e-11 |
| Old three-trade walk / IPM | 53.6006222477097 | 53.6006222296419 | 1.81e-8 |
| First guided pilot / IPM | 57.6107177196898 | 57.6107176728821 | 4.68e-8 |
| Guided pair-support pilot / IPM | 22.2201204306649 | 22.2201202956009 | 1.35e-7 |

For each result the stored binary dual values were converted to rationals
without rounding, their common denominators cleared, and their exact
negative-RHS integer certificate independently checked by
`audit_certificate.py`. These validate the fixed-K relaxation and extraction
pipeline; all these K already had separate exclusions.

Twelve corrupted or unsuitable controls were rejected, including a wrong
candidate hash, variable order, RHS, row term, omitted nontrivial row,
nonfinite/out-of-box X, false objective or dual bound, incorrect dual sign,
negative cap weight, and a box-feasible but nonoptimal all-zero X. The
reproducible driver is `acceleration/review_phase1_controls.py`.

The independent CUDA comparison additionally checked all 121,128 residuals
for seven K and four X choices, including a real fractional phase-I optimum.
The largest row difference was 1.78e-15 and the largest objective-component
difference was 9.10e-13. This validates numerical scoring only; the report is
`acceleration/results/20260916_phase_gpu_fractional_controls/review.json`.

## First global-guided pilot

The completed `20260916_global_pilot` run considered 3,072 proposals and
made 137 actual IPM evaluations plus eight cached lookups. It accepted 15
trades in 79.85 seconds. The accepted path now has a stronger statement than
numerical improvement: the independent checker recomputed the initial and
all 15 accepted phase-I models, using exact rational primal/dual intervals,
and proved **every accepted move strictly lowers the optimized merit**.

The initial exact dual lower bound is approximately 22.22012029560093,
while the final exact primal upper bound is 8.465144464340375. Their exact
difference guarantees an improvement of at least 13.754975831260555. The
complete accepted-path audit took 3.63 seconds; all model, candidate, trace,
proof, and auditor hashes are bound in
`acceleration/results/20260916_global_pilot/accepted_phase1_audit.json`.

The final exact dual lower bound is still positive, approximately
8.465144463890677. Clearing its binary-rational multipliers gives a checked
integer Farkas contradiction, with RHS
`-1309917658773155441514425820`, in
`accepted_phase1_audit_details/best_exact_binary_dual_certificate.json` and
its companion independent audit. This remains a fixed-K exclusion, despite
the improved global merit.

The certificate is bound to the original solver candidate
`probes/iteration_0023_choice_0105_candidate.json` (SHA256
`119cd0512479d11ddc82b2f00048b2dc30d09c906747e7bc5ca82a4a9aecaeef`).
The separately written `best_candidate.json` wrapper has a different file
hash; the checker verified that it contains exactly the same 168 overlap
edges. No file-hash substitution was used to audit the phase-I artifact.

The all-zero X control has quota merit 1,344 and pair merit zero: all
partial common-neighbor caps already hold. A successful search must improve
global feasibility while preserving the legal overlap assignment; no finite
sample establishes a uniform Conway-99 theorem.

## Coupled search and two-trade escape

The first global-only pilot's best loses pair-domain arc consistency. The
successor `guided_coupled_overlap.py` therefore requires a complete nonempty
native star/pair check before accepting each endpoint. Its main run reaches
9.09764321, then a continuation reaches 7.60536703. An alternative initial
assignment reaches 10.11509750. All three final local star domains and exact
pair closures have independent producer-free replays; the corresponding
positive phase-I dual bounds and integer contradictions are independently
checked for those same assignments. The continuation includes one permitted
strictly uphill move, so its whole path is not monotone.

`guided_two_trade_overlap.py` uses two legal Rust-generated swaps per proposed
move, with the local pair gate at the endpoint. A 16-iteration pilot evaluates
2,048 endpoints and 129 actual LPs in 75.09 seconds. Its single accepted path
lowers the exact optimum from at least 7.605367027116861 to at most
7.332122013712176. An independent full trace audit replays all intermediate
and final partial graphs and all 129 actual LP models. The final lower bound
7.3321220135202125 remains positive. Its independent integer contradiction has
RHS `-9076727413462412930908104042`, while independent local enumeration and
pair closure retain 13,665 of the original 21,145 complete star choices.

The recorded intermediate has a native pair-AC pass and an independently
bounded phase-I optimum [9.110011794299139, 9.11001181442254]. Hence this path
crosses a merit barrier: its first step increases the true optimum by at least
1.5046447671708045, above the one-step driver's 0.5 allowance. Its second step
then improves on the initial assignment. This diagnoses the value of the
larger move in this run; it does not establish a barrier for all possible
paths. The intermediate native pair result has not received an independent
domain replay and is only a diagnostic.

Evidence is in `acceleration/results/20260916_two_trade_pilot/` and
`acceleration/results/20260916_two_trade_intermediate/barrier_audit.json`.
See `GOAL_20260916_PROGRESS.md` for the run table and reproduction commands.
None of these improvements gives a feasible relaxation or a Conway graph.
