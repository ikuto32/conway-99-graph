# CPU control for approximate phase-I reoptimization

The bounded CPU control supports trying a CUDA implementation. On four extended
matching moves, 2,000 iterations reduced fixed-X merits of 35–50 to within
0.49–0.59 of independently audited LP upper endpoints. At 10,000 iterations the
remaining excess was 0.049–0.065. This is a ranking experiment, not an exclusion
method or an exhaustive assessment of ranking quality.

Frozen implementation: `review_phase1_chambolle_pock.py` (SHA256
`7894bd7effef68d74ac52ab83990dda109de77e22aee213b6a26d00f30347d59`).
Report: `results/20260916_phase1_chambolle_pock_cpu/summary.json` (SHA256
`f4f30d2a32e76d4f047ab97daf8ba6dbb2a139020d3e61d9c5cbf51b05eb5a97`).
All checkpoint primal/dual vectors are saved beside the report. No historical
producer, checker, CUDA source, or proof artifact was modified.

## Model and update

For a fixed legal overlap graph K, independently reconstruct the full99 rows.
Let A have 1,680 disjoint-edge columns and 4,326 rows: 840 foreign-label quotas,
then all 3,486 outer-pair caps. Another 336 own-label quotas are independently
checked to have no unknown terms and zero target, then omitted.

For r = Ax − b, define

    h(r) = sum_{quota rows} |r_i| + sum_{cap rows} max(0,r_i).
    min_{0 <= x <= 1} h(Ax-b)
      = min_{0 <= x <= 1} max_{y in D} y^T(Ax-b),
    D = [-1,1]^840 x [0,1]^3486.

The conjugate of h is the indicator of D. Including the translation by b in
the dual proximal step gives exactly:

    y_new    = clip_D(y + sigma * (A*xbar - b))
    x_new    = clip_[0,1](x - tau * A^T*y_new)
    xbar_new = 2*x_new - x

Use theta=1, tau=sigma=0.09. This is the standard primal-dual update of
[Chambolle and Pock, 2011](https://link.springer.com/article/10.1007/s10851-010-0251-1),
specialized to the two box projections above. The norm estimate below supplies
the strict step-size condition. We do not assume strong convexity or an
accelerated convergence rate.

For any feasible x and y, the model's primal and dual objective formulas are:

    U_K(x) = h(Ax-b)
    L_K(y) = -b^T*y + sum_j min(0,(A^T*y)_j).

They bracket the optimal model value in exact arithmetic. This experiment
evaluates them in float64 and labels them numerical values; no positive
floating lower value is accepted as a certificate.

## Uniform operator bound

Every disjoint unknown edge {u,v} appears in four quota rows: the two labels of
v in rows belonging to u, and the two labels of u in rows belonging to v.
It also appears in nine cap rows: its own adjacency term, four rows induced by
the overlap neighbors of u, and four induced by those of v. The overlap degree
is four and the graph has no loops; these nine occurrences have distinct pair
coordinates.

Each quota row contains eight columns. A pair row contains at most the one
unknown adjacency term and eight KX/XK terms. Thus the matrix is nonnegative
with column absolute sums exactly 13 and row absolute sums at most 9:

    ||A||_2^2 <= ||A||_1 * ||A||_infinity <= 13 * 9 = 117.
    tau*sigma*||A||_2^2 <= 0.09^2 * 117 = 0.9477 < 1.

The independent full99 reconstruction verified these incidence counts, all
21,840 nonzeros, and the absence of duplicate column terms in every tested
matrix. This check uses graph-derived rows, not the LP producer's matrix.

## Controls and results

The five controls are the unchanged best K and the lowest saved LP objective
within each of the cycle partitions 2+2, 5, 6, and 2+4 among the already audited
whole-matching pilot probes. Selection is disclosed and is not a random sample
of the 74,638-candidate family. No LP was rerun. Exact reference intervals and
all their candidate, result, and auditor hashes were checked before reuse.

Both runs initialize x to the same current-best LP vector. One initializes
y=0; the other maps the saved current dual by semantic row coordinate, assigns
zero to absent tautological cap rows, and projects onto D. The table shows the
second initialization and last-iterate upper values. “LP reference” is the
rounded upper endpoint of an existing exact rational interval.

| Cycle partition | Frozen-X upper | LP reference | Upper at 500 | Upper at 2,000 | Upper at 10,000 | Lower at 10,000 |
|---|---:|---:|---:|---:|---:|---:|
| 2+2 | 35.154827 | 8.702755 | 12.629553 | 9.275110 | 8.764079 | 8.668816 |
| 5 | 42.775035 | 9.903186 | 13.795670 | 10.489642 | 9.953156 | 9.875677 |
| 6 | 50.065273 | 9.970135 | 13.700917 | 10.462573 | 10.019310 | 9.948559 |
| 2+4 | 49.531788 | 7.590814 | 10.979739 | 8.128725 | 7.655564 | 7.546991 |

The baseline with its current dual remained at 7.332122 to about 2e-9. Starting
its dual at zero temporarily worsened the last-iterate objective to 11.787374
at 500 iterations, despite starting at an optimal primal point. A scoring
implementation must retain the initial feasible point when reporting its best
upper value.

The last iterate outperformed the ergodic average for every extended control at
the requested checkpoints. The averages are still saved because the standard
ergodic convergence analysis does not justify a universal preference for the
last iterate. Reusing the dual modestly helped the early checkpoints. At
2,000 steps the order of the close 5- and 6-cycle controls was still reversed
relative to their exact LP intervals; 10,000 steps restored it. Small merit
differences still need actual LP optimization.

Sixty checkpoint pairs were checked through the independent full99 evaluator
and a separate scalar dual accumulation. Maximum scalar discrepancy against
the SciPy sparse evaluation was 8.1e-13. All numerical lower/upper values were
consistent with the existing exact LP intervals within the declared 1e-7
diagnostic tolerance. This comparison does not certify the floating iterates.

Total study time was 8.57 seconds, including loading, construction, reference
checks, and saving vectors. Per control, the 2,000-step iteration loop took
about 0.11 seconds and the 10,000-step loop about 0.54 seconds. These are CPU
measurements, not a CUDA speed prediction.

## Suggested bounded CUDA prototype

Preserve full semantic row order and the 1,680-column disjoint-edge order.
Begin with float64, one candidate per block, and the tested update above.
Quota rows have eight gathers; cap rows have at most nine. Each transpose
update has exactly thirteen gathers. The graph geometry permits these indices
to be generated directly, but parity should first be checked against these
saved CPU matrices and iterates.

Inputs should include candidate K, initial x, and the full 4,326-coordinate
dual y. Report numerical primal, dual, and gap at fixed checkpoints, together
with the minimum upper value over the initial point and observed checkpoints.
Keep candidate/input/source bindings, iteration count, and precision explicit.
Retain both last and average checkpoint values during validation.

A reasonable quality-first experiment is 500 iterations on a diversified
candidate subset, then 2,000 on the retained shortlist, followed by actual LP
optimization. Measuring a broader shortlist is needed before choosing a final
budget. This report does not establish that scoring all 74,638 candidates is
fast, that approximate ranking is reliable near ties, or that a positive
numerical gap excludes any candidate.
