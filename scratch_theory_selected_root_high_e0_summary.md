# Solver-free selected-root reduction to `E0<=74`

For the root guaranteed by `scratch_root_side_bound_selfcontained.md`,

```
S <= 69.
```

The allowed fibre catalogue has diagonal capacity at most its edge deficit,
so

```
Q <= 84-E0,             Q=E0-S >= E0-69.
```

This immediately excludes every `E0>=77`.

At `E0=76`, capacity forces four deficit-two fibres, all in their
two-diagonals state (`Q=8,S=68`).  Gram circulation forces their supports to
be a `C4`.  The integral residual/collision argument in
`scratch_theory_e76_analytic.md` then gives a contradiction.

At `E0=75`, `Q>=6`.  The only capable deficit multisets are

```
(3,2,2,2), (2,2,2,2,1), (2,2,2,1,1,1).
```

The PSD Gram-circulation classification in
`scratch_theory_gram_circulation.md` excludes all three.

Hence every putative `srg(99,14,1,2)` admits a root with

```
E0 <= 74.
```

This reduction uses no SAT/CP-SAT negative.  Its machine checks are:

* `scratch_root_side_bound_selfcontained_audit.json`;
* `scratch_theory_e75_gram_audit.json` and the independent graph-
  classification audit `scratch_theory_e75_gram_independent_audit.json`;
* `scratch_theory_e76_analytic_audit.json` and the independent occupancy
  audit `scratch_theory_e76_occupancy_independent_audit.json`.
