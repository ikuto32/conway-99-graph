# Bounded optimization of one entire matching

`matching_phase1_mip.py` is a numerical candidate producer. It frees one of
the 21 perfect matchings described in [ATOMIC_CYCLE_PLAN.md](ATOMIC_CYCLE_PLAN.md),
keeps the other 20 fixed, and jointly optimizes that matching and the 1,680
continuous disjoint-edge variables. All phase-I residual weights are one.
It does not perform pair-AC checks or construct a completed graph.

```powershell
.venv/Scripts/python.exe -B acceleration/matching_phase1_mip.py --initial INITIAL.json --initial-phase1 PHASE1.json --out NEW_DIRECTORY --root-group 3 --class cross --seconds 30
```

`--class` accepts `same_0`, `same_1`, or `cross`; root groups are zero-based.
`--fix-initial` fixes the chosen matching and uses IPM as a numerical model
control. The default solver budget is 30 seconds, excluding model assembly
and output processing. HiGHS can slightly exceed its requested time limit.
Existing output directories are rejected. No frozen earlier source is changed.

The optional `--initial-phase1` must bind the same canonical initial edge set.
Its X vector is checked for finite values in `[0,1]`, and its merit is
recomputed. If omitted, zero X supplies a feasible, possibly poor incumbent.
The public API is:

```python
solve_matching(edges, root_group, matching_class,
               seconds=30, initial_x=None, fix_initial=False)
```

## Compact formulation

Let B be the full 99-vertex known graph with the chosen matching removed,
and let Y contain the binary replacement edges. Matching degree equations
make the partner map injective, so `Y_u intersect Y_v` is empty for distinct
vertices. The partial common-neighbor cap is therefore exactly linear:

```text
|B_u intersect B_v| + sum_w(B_vw Y_uw + B_uw Y_vw) + B_uv + Y_uv <= 2.
```

These partial caps are hard constraints, including the adjacency term Y_uv.
Own-label quotas follow from the matching class and are checked again on the
extracted full partial graph. The 840 foreign-label completion equations have
positive and negative residual slacks.

All vertices of the chosen matching contain one common root group. A
nonlinear outer-pair completion row therefore has just one variable partner:
`H(X) + g_p(X) <= 2 + t`, where `g_w = B_vw + X_vw` lies in `[0,1]`.
The model uses the baseline `H(X) <= 2 + t` and, for each possible partner w,
`H(X) + g_w(X) + Y_uw <= 3 + t`. The selected partner enforces the exact row;
the baseline implies every unselected row. One shared nonnegative slack t is
used for the whole original pair, and counted once in the objective.

The model retains all 3,486 outer-pair slack coordinates, including tautologies.
It omits the nonnegative X-X common-neighbor products just as the existing
fixed-K necessary linear model does. X remains continuous. Consequently even
zero phase-I merit is not a completed graph witness.

| Class | Binary choices | X columns | Slack columns | Total columns | Rows | Nonzeros |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `same_0` control | 60 | 1,680 | 5,166 | 6,906 | 12,648 | 77,526 |
| `cross` control | 120 | 1,680 | 5,166 | 6,966 | 20,826 | 128,046 |

The displayed row counts include the strengthening baseline rows. They are
larger than estimates for a formulation containing only conditional rows.

## Incumbent validation and output

`result.json` records the canonical matching choices, raw Y and full solver
column values, extracted integral matching, returned X, recomputed residuals
and minimal slacks, solver objective, model violation, status, timing, node
count, numerical gap/bound, and source/input hashes. Nonfinite bounds are
represented by JSON null. `candidate.json` contains the complete canonical
168-edge K and is hash-bound by the result.

An incumbent must be within the declared integrality tolerance, produce a
perfect matching, pass the existing full-99 partial-graph checker, and remain
feasible after X projection and slack reconstruction. The frozen fixed-K
builder separately recomputes its merit. Fractional or otherwise unusable
solver output is not turned into an assumed-valid K: the validated initial
incumbent is retained instead.

`selected_origin` identifies whether the returned values came from HiGHS or
the stored fallback. `retained_initial_incumbent` indicates use of the fallback,
while `matching_unchanged` compares the actual graph. Thus HiGHS returning the
provided initial incumbent can have `selected_origin=SOLVER_INCUMBENT` and
`matching_unchanged=true`. Tiny same-graph numerical differences are not
structural improvements.

No infeasible, optimal, time-limit, bound or gap status is promoted to an exact
exclusion or neighborhood-coverage certificate. A changed candidate still
requires the independent fixed-K and local-domain audit pipeline.

## Saved controls and bounded runs

`results/20260916_matching_mip_control_summary.json` binds four controls using
the saved 7.332122013712173 seed and its fractional X. All use root group 3.

| Run | Recomputed merit | Solver seconds | Outcome |
| --- | ---: | ---: | --- |
| Fixed `cross` | 7.332122018681210 | 0.930 | Numerical optimum; difference 4.97e-9 |
| Fixed `same_0` | 7.332122023296805 | 0.678 | Numerical optimum; difference 9.58e-9 |
| Free `cross` | 7.332122013712173 | 30.512 | Time limit; unchanged K/X |
| Free `same_0` | 7.332122013613444 | 30.007 | Time limit; unchanged K, numerical noise only |

Both variable runs reported zero completed branch-and-bound nodes. Their
reported numerical lower bounds were zero and approximately 1.177 respectively;
these are diagnostics only. The bounded tests found no new overlap assignment
and do not establish that the matching neighborhoods lack improvements.

The separate `results/20260916_matching_indicator_audit.json` checks the
indicator mathematics using 16 independently constructed real Y/X controls,
including changed matchings. It checks 55,776 cap coordinates, 18,816 label
coordinates and 172,800 indicator inequalities. Negative controls demonstrate
that M=0, double-counted fixed-neighbor terms, and separately summed indicator
slacks change the intended model. This is independent algebra/semantic testing
plus fixed-matching numerical agreement, not an exact certificate for a MIP
bound or an independent replay of every emitted matrix coefficient.

Frozen producer SHA256:
`8c69da5e7b53dc3987d139a5772dd575e991fd2389e1c8c9d0960f5afd7f0ece`.

## Continuous-relaxation diagnostics

The separate `matching_phase1_relaxation.py` imports the frozen model builder,
makes every Y column continuous, and uses IPM with crossover disabled. It
exports every integer matrix coefficient, objective coefficient, bound, primal
value, and signed row/column dual. A null exported lower/upper bound represents
negative/positive infinity respectively. These exports allow subsequent exact
arithmetic checks; exporting an integer matrix does not independently certify
its graph interpretation.

```powershell
.venv/Scripts/python.exe -B acceleration/matching_phase1_relaxation.py --initial INITIAL.json --out NEW_DIRECTORY --root-group 3 --class same_0 --seconds 30
```

For same-sign classes, `--blossoms` adds all 1,012 odd-subset matching
inequalities of sizes three and five. The degree-one equations imply the
complementary size-nine and size-seven inequalities on the 12-vertex cohort;
singleton/complement inequalities are trivial. Each subset S imposes
`sum(Y_e for e inside S) <= (|S|-1)/2`.

The three bounded diagnostics, each permitted 30 seconds, completed quickly:

| Continuous case, root group 3 | Numerical objective | IPM seconds |
| --- | ---: | ---: |
| `cross` | 1.49e-13 | 1.311 |
| `same_0` | 1.1769910423 | 0.828 |
| `same_0`, size-3/5 odd-set cuts | 1.1769910383 | 0.930 |

The cross case is numerically zero. The same-sign case has a positive
numerical relaxation optimum even without MIP cuts; the additional odd-set
constraints make no material difference at this precision. The small
four-billionth decrease in the reported strengthened value is numerical noise,
not a mathematical weakening. Full exports and a hash-bound summary are in
`results/20260916_matching_lp_{cross3,same0,same0_blossoms}/` and
`results/20260916_matching_lp_summary.json`.

A positive exact dual, after independent validation of the coefficient
semantics, could exclude zero-defect completion for every matching in that
chosen class with the other 20 fixed. The diagnostic output itself makes no
such proof claim. Its fractional Y values are not extracted as K candidates.
