# Fixed-overlap exclusion independent of disjoint compression totals

The prescribed 168-edge overlap assignment cannot be completed even if
all 105 disjoint compression block totals are left free. In fact its
simultaneous linear relaxation is infeasible over real edge variables
in [0,1]. This remains an exclusion of one prescribed overlap assignment;
it does not exclude every overlap assignment, every compression, or E0=0.

## Reused proof and semantic provenance

The old 84,696-clause CNF was reproduced byte-for-byte. Dropping all
105 disjoint block-total equations removes 17,136 clauses and leaves
67,560. The already sealed 1,034-clause UNSAT core contains no block-total
clause at all. Its semantic support is 102 label-quota equations and
95 linear pair caps (710 and 324 core clauses, respectively).

`scratch_next_overlap_audit.py` checks the weaker CNF is exactly that
subset, reconstructs every used quota/cap coefficient from the overlap
assignment without reading disjoint compression entries, and replays the
same 78 RUP additions. It returns
`INDEPENDENT_NO_DISJOINT_TOTALS_FIXED_OVERLAP_RUP_PASS` with exit 0.
The sealed earlier CNF/core/proof files were not modified.

A fresh CaDiCaL run also reported UNSAT, but its newly emitted proof was
not accepted by drat-trim. That fresh proof is not used as evidence; the
valid reused core and independent replay establish the stated result.

## Exact weighted-capacity contradiction

A separate LP dual calculation produced an integer certificate. The
independent checker reconstructs its coefficients directly from the
fixed overlap edges and verifies the complete inequality using integers.
No solver, cardinality encoder, or floating-point arithmetic is imported
by this checker.

The combination uses 658 label-quota equalities, 376 linear pair caps,
and 174 bounds of the form x_e<=1. Equality multipliers may have either
sign; all inequality multipliers are nonnegative. Group multipliers lie
between -26 and 52. After combining them, every edge coefficient is
nonnegative, while the right side is -807:

```text
0 <= sum_e w_e x_e <= -807.
```

There are 826 positive coefficients. This is a contradiction for real
nonnegative edge variables, so edge integrality is unnecessary for this
particular exclusion. The proof's quota support includes all 84 outer
vertices. It has not been reduced to a small forbidden overlap pattern.
The certificate is in `scratch_next_overlap_farkas.json`; its exact
independent audit is `scratch_next_overlap_farkas_audit.py/.json`.

By contrast, all 84 individual rows can separately satisfy their own
quotas and every projected linear pair cap when other unknown row terms
are dropped. The eight selected edges for each row are saved and checked
directly in `scratch_next_overlap_row_probe.json`. Thus those single-row
capacity tests do not explain the simultaneous contradiction.

## A necessary weighted-capacity inequality for any overlap assignment

Write q(K) for the remaining label quotas of an arbitrary prescribed
overlap adjacency K, and r(K) for its linear pair-cap right sides. For
fixed multipliers alpha on quota equalities, beta>=0 on pair caps, and
gamma>=0 on edge upper bounds, let

```text
R(K) = alpha.q(K) + beta.r(K) + sum_e gamma_e,
w_e(K) = the combined coefficient of disjoint-edge variable x_e.
```

Every completion with zero same-fiber edges must satisfy

```text
R(K) - sum_e min(0,w_e(K)) >= 0.                    (*).
```

Indeed the weighted equality/inequality sum gives
`sum_e w_e(K)x_e <= R(K)`, and 0<=x_e<=1 gives the lower bound
`sum_e min(0,w_e(K))`. The negative-part term makes (*) valid even when
changing K makes some combined coefficients negative. Therefore the
same stored multipliers define a necessary inequality for every overlap
assignment, not only the one that produced the certificate. They give
score -807 on the saved lift. This supplies a reusable capacity cut;
a nonnegative score is only passage of this one necessary condition.

`scratch_next_overlap_cut.py` evaluates this inequality with integer
arithmetic on an input overlap-edge JSON. It does not use disjoint C
entries and does not solve a graph search.

## Reproduction

```text
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_next_overlap_audit.py
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_next_overlap_farkas_audit.py
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_next_overlap_cut.py
```

The first two are certificate replays. The third reports score -807 and
`excluded_by_this_cut: true` on the default fixed overlap lift. No
submission file, new exhaustive lower-layer search, or global E0 bound
is produced by this work.
