# Independent audit of the self-contained side bound

The derivation in `scratch_root_side_bound_selfcontained.md` passes an
independent logical and arithmetic audit.  The machine-readable result is
`scratch_root_side_bound_selfcontained_audit.json` with
`status: LOGIC_AND_ARITHMETIC_VERIFIED` and no errors.

The fragile steps were checked explicitly:

- For disjoint triangles, common neighbours in the triangle-intersection
  graph correspond bijectively to cross edges; the cross edges form a
  matching.
- The second binomial moment is exactly `6*12/2=36`.  An ordered pair
  `x!=z` and external neighbour `y~x` gives the unique second common
  neighbour `w` of the nonedge `yz`; the triangle on `yw` is disjoint from
  the fixed triangle.  Reversing `(x,z)` exchanges the two selected cross
  edges, so every unordered pair is counted exactly twice.
- The polynomial formula for the rank-44 projector is correct on all four
  eigenspaces.  For `M=21E`, `W=M o M` is positive semidefinite and
  `A4=MWM` is positive semidefinite.
- `A4` is congruent to `M` modulo two, and every row of `M` has at least
  `a0=20+q` odd entries.  With `D=(W-M)/2`, symmetry and even diagonal imply
  `vDv^T` is even, so every diagonal of `A4` is divisible by four.  A zero
  diagonal in a PSD matrix would force that row to be zero; hence
  `tr(A4)>=4*231=924`.
- The row cube sum and cyclic trace calculation give
  `tr(A4)=84*(n3-693)`.  Together with `3|n3`, this yields `n3>=705`.
- An `r=3` disjoint triangle pair is exactly an induced triangular prism.
  Marking any of its six vertices recovers one rooted fibre side, and the
  inverse construction has no additional choice.  Thus `sum_r S(r)=6P`.

Consequently

```
n3 >= 705,
n3 + 3P = 4158  =>  P <= 1151,
sum_r S(r) = 6P <= 6906 < 99*70.
```

Every putative `srg(99,14,1,2)` therefore has a choice of root with
`S(r)<=69`, without importing the stronger public `n3>=708` bound.  At such
a root, `E0=73` necessarily implies `Q=E0-S>=4`.

This validates a reduction only.  It neither constructs a graph nor converts
an incomplete SAT portfolio into a nonexistence proof.
