# Independent eight-coordinate support audit derivation

This is a checking argument for the fixed 120-K-edge family, all its prescribed
absences, and the independently enumerated and matching-filtered stars. It
does not assume a nontrivial automorphism. It establishes no statement about
families not covered by these explicit premises.

For an outer center `u`, let `F_u` be its fixed outer neighbors and `S` its
retained chosen unknown neighbors. The full outer neighborhood is `F_u ∪ S`
and has size 12. Let `y_ab` be an integer for each unordered pair of outer
vertices, and `q_ab` an integer for each allowed unknown edge. With the smaller
endpoint first, the independently evaluated column score is

```
sum(y_ab : {a,b} ⊆ F_u ∪ S)
  + sum(y_uv + q_uv : v ∈ S, u < v)
  - sum(q_vu : v ∈ S, v < u).
```

This expression is evaluated directly from raw neighborhood sets using Python
integers. It neither reads matrix entries to obtain scores nor imports the
producer's scoring implementation. NumPy/SciPy remain trusted components of
the separate matrix/export audits, which are disclosed premises.

A hypothetical graph completion selects one star at each center. The complete
domain audit covers that star, and the independently checked necessary matching
filter cannot discard it. Its chosen-edge decisions agree between endpoints,
so the sum of the signed `q` terms is zero. Summing the pair terms over centers
counts all common outer neighbors. The additional smaller-endpoint adjacency
term counts each unknown edge once. The exact SRG pair identity therefore gives

```
b_ab = 2 - |label(a) ∩ label(b)| - fixed_adjacency(a,b),
sum(selected column scores) = sum(y_ab * b_ab).
```

The maximum score in each complete retained center domain is at least the
selected score. Thus every completion implies

```
N = sum(y_ab * b_ab) - sum_u max_S score(u,S) ≤ 0.
```

In particular, an independently checked strict integer inequality `N > 0`
would exclude this conditional family. For positive integer `D` and `|y| ≤ D`,
the same expression divided by `D` is a lower bound for the matching-filtered
full-moment LP's L1 residual. Neither LP optimality nor feasibility of an
unconstrained solver dual is required. A nonpositive `N` proves no exclusion
and no graph or LP feasibility.

The frozen six numerical attempts only propose integer weights. The checker
independently negates each saved binary64 number using its exact integer ratio,
rounds at `D = 2^20` with ties to even, and clips only the moment weights to
`[-D,D]`. It then checks every retained raw star and all 84 maxima for each
completed attempt. The floating checkpoint itself supplies no certificate.
Known valid rook-9 identities, altered right-hand sides and column totals,
rounding ties of both signs, altered result and out-of-box weight controls
calibrate the independent checking path. Missing and failed attempts remain
explicitly separate from independently evaluated bounds.

See `eight_gpu_audit_preregistration.json` and its first amendment for the
pre-run selection, criteria, resource cap, source identities and resume rule.
The completed machine-readable audit binds exact input hashes, commands,
versions and resulting per-attempt values; this derivation alone is not an
execution record or a promotion of any result.
