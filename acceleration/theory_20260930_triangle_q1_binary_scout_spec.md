# Fixed-core binary-factor continuation scout

Frozen before execution. The inspected latest factor continuation is archived
Wave154 at85e705cc6c2a14d123120c93a847e30aaab1789e: two stored Q1 factors,
384-map simultaneous-coordinate orbit tests, and an unresolved joint
69,270-triple exact-cover model. No later triangle-Q1 package was found in
the scoped archive text search. The present task uses the same fixed core
M0=M1=M2=(01)(23)...(10,11), F01=F02=I, F12=P=shift6. This is not universal
containment. Gram PSD redundancy is archived Wave36/58 content, not novelty.

Generate at most8 distinct new Q1 factors, excluding both archived orbits
under exactly the named384 coordinate maps (no full-isomorphism claim).
First enumerate deterministic balanced two-row incidence trades for up to
20seconds: swapping C1 vertices x,y on a selected common-neighbour subset R
preserves C0*C1^T iff the sum of the changed C0 edge columns is zero.
Every generated factor must independently pass the producer's literal
24x60 integer Gram calculation, all row/column margins and Q1 permutation.
If fewer than8 factors result, use at most60seconds of deterministic-seed
integer-objective permutation annealing, seed20260930, at most512000
attempted swaps, with fresh exact validation of every zero objective.
Floating acceptance probabilities guide search only. Objective is exactly
sum_(a,b)(C0*C1^T-G01)[a,b]^2, nonnegative integer, lower is better; it is
not compared to three-group objectives. Preserve attempted/completed
counts, scores, selection rule and seeds. No heuristic zero is accepted
without literal validation.

For each new factor construct raw initial99 partial adjacency, leaving all
C2-B and B-B pairs free. For each of the twelve C2 rows, in ascending order,
test degree10,24 exact C0/C1 common-neighbour equations, and forbidden pairs
arising from already-known B-pair common neighbours. Stop that factor at
the first empty row domain; otherwise retain each row witness or UNKNOWN.
Each UNSAT row emits a complete binary branching/propagation tree. Each SAT
row emits its complete60-bit vector, not a joint factor. Per-row limits are
2seconds/20000nodes; overall120seconds/8GiB. Preserve incomplete trees with
UNKNOWN status. All discoveries await independent raw-matrix/tree checking.
Stop starting row evaluations after105seconds to preserve the size scout and
final records within the120second overall limit; count unattempted factors.

Also run an exact size scout for a different joint model: two binary12x60
blocks C1,C2 with C0 fixed. Fold only the explicit zero-target incidences;
enforce24row sums10,120column sums2,288linear C0-cross equations, and276
pair Gram equations among C1/C2 rows using exact ANDs and the frozen exact
prefix-threshold encoder. This is a size calculation, no solver or model
equivalence promotion. It retains the binary integral factor rather than an
archived rational projection. If tractable, recommend a separately audited
joint encoding before more fixed-Q1 samples.

Controls: both archived Q1 matrices replay exactly; a deliberately swapped
image fails. Row solver is the previously independently checked rule set,
with shared producer code disclosed, and calibration against small complete
truth tables. No new UNSAT status is independent verification.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_q1_binary_scout.py --out acceleration/results/20260930_triangle_q1_binary_scout`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
