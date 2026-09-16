# Independent reduction of the source-332 parametric Gram family

For the sole underdetermined `E0=72` Gram macro (source row 332), the exact
diagonal and overlap equations give

```
H(t) =
 [ 2  -1   0  -t ]
 [-1   2   t   0 ]
 [ 0   t   2  -1 ]
 [-t   0  -1   2 ].                                        (1)
```

This note independently checks the short last step which turns the rational
parameter into exactly three discrete cases.  It does not re-use the RREF or
PSD routines which produced the affine family.

Put `K(t)=H(t)-2I` and reorder the coordinates as `(0,2 | 1,3)`.  Then

```
K(t) = [ 0   C  ],        C = [-1  -t],
       [ C^T 0  ]             [ t  -1]

C C^T = C^T C = (1+t^2)I.                                  (2)
```

Thus the eigenvalues of `K(t)` are
`+sqrt(1+t^2),+sqrt(1+t^2),-sqrt(1+t^2),-sqrt(1+t^2)`, and
the eigenvalues of `H(t)` are

```
2+sqrt(1+t^2)  twice,
2-sqrt(1+t^2)  twice.                                      (3)
```

Consequently

```
H(t) is PSD  iff  t^2<=3.                                  (4)
```

One of the actual disjoint exceptional block totals is `3+t` (others include
`3-t` and `4+-t`).  Every block total is an integer, hence `t` is an integer.
Combining this with (4) gives exactly

```
t in {-1,0,1}.                                              (5)
```

All displayed block totals lie in their legal range for these three values,
and the complete compression row sums are 48, as checked in the original
affine audit `scratch_theory_e72_source332_parametric_gram.py/.json`.

The standard-library script
`scratch_theory_e72_source332_parametric_gram_independent_audit.py` verifies
`K(t)^2=(1+t^2)I` as a polynomial matrix, independently enumerates the
integer/range/PSD cases, and obtains (5).
