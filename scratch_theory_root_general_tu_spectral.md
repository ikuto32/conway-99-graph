# General-root spectral traces of `T` and `U`

Status: `INDEPENDENT_GENERAL_ROOT_TU_SPECTRAL_AUDIT_PASS`.

This calculation is valid at every root of a putative
`srg(99,14,1,2)`; it does not assume the prism-free endpoint.  It extends the
fixed-`Q` endpoint trace table, then checks all immediate scalar consequences.
The outcome is exact but null: the new traces repackage the known first
moments and yield no stronger inequality in `n3,z11`, or `sum E0`.

## Rooted scaffold and the two factors

Fix a root `r`.  Its 84 nonneighbours are naturally the edges of
`H=K14-7K2`.  Let `B` be their induced adjacency and let `Q` be the line
graph of `H`.  For two labels `x,y`, let `d_r(x,y)` count the mate crossings
between their endpoints.  The exact rooted equation is

```text
Q=10I+2One-B^2-B.                                      (1)
```

Let `T` be the selected intersecting-label edges.  It is a simple spanning
2-factor.  Let

```text
U_xy=B_xy d_r(x,y).
```

This is the augmented factor `R_tm J_E`, translated to the 84 outside
labels.  It is a nonnegative integral weighted 2-factor.

Write `S=S(r)` for selected same-fibre sides and `D=D(r)` for selected
same-fibre diagonals.  The complete edge profiles are

```text
T:  84-S unit edges of type (Q,d)=(1,0),
        S unit edges of type (Q,d)=(1,1);

U:      S unit edges of type (1,1),
        D double edges of type (0,2),
   84-S-2D unit edges of type (0,1).                    (2)
```

Consequently

```text
S>=0, D>=0, S+2D<=84,
tr(T^2)=168,    tr(U^2)=168+4D,    tr(TU)=2S.           (3)
```

The last equality records exactly the side edges shared by the two factors.

## The spectrum of `B` is fixed without the endpoint

The line graph `Q` has eigenvalues

```text
22^1, 10^7, 8^6, (-2)^70.
```

Equation (1) initially allows the root pairs

```text
22 -> 12,
10 -> {0,-1},
 8 -> {1,-2},
-2 -> {3,-4}.
```

Every outside vertex has two intersecting-label neighbours, hence ten
disjoint-label neighbours.  The 420 disjoint-label edges each have their
unique common neighbour outside and therefore partition into 140 triangles.
No intersecting-label edge can lie in an outside triangle, since its shared
base point is already the unique common neighbour of its endpoints.  Thus

```text
tr(B)=0,       tr(B^2)=1008,       tr(B^3)=840.
```

Solving the three integer multiplicity equations gives the unique spectrum

```text
spec(B)=12^1,3^40,0^7,(-2)^6,(-4)^30.                  (4)
```

So the spectrum used in the endpoint calculation was not endpoint-specific.

## Exact projector traces

The clean-room line-graph census gives

| `(Q,d)` | `(1,0)` | `(1,1)` | `(0,0)` | `(0,1)` | `(0,2)` |
|:--|--:|--:|--:|--:|--:|
| `(Q^2)_xy` | 11 | 10 | 4 | 3 | 2 |

Let `E_lambda` be the five spectral projectors of `B` in the order
`lambda=12,3,0,-2,-4`, and put
`a_lambda(F)=tr(F E_lambda)`.  From (2),

```text
tr(TQ)=168,          tr(TQ^2)=1848-2S,
tr(UQ)=2S,           tr(UQ^2)=504+14S-4D.              (5)
```

Together with `tr F=0`, `a_12(F)=2`, and `tr(BF)=168`, these five equations
uniquely give

| `lambda` | `a_lambda(T)` | `a_lambda(U)` |
|--:|:--|:--|
| 12 | `2` | `2` |
| 3 | `72/5+2S/105` | `112/5-8S/105+4D/105` |
| 0 | `7-S/12` | `-7+S/12-D/6` |
| -2 | `18/5+S/10` | `18/5+S/10+D/5` |
| -4 | `-27-S/28` | `-21-3S/28-D/14` |

The independent audit obtains the same table by a different route: it first
uses explicit Lagrange polynomials `E_lambda=p_lambda(B)` and derives the
needed `B` moments entrywise.

For every selected outside edge,

```text
(BQ)_xy=2-Q_xy-d_r(x,y).                               (6)
```

Equations (2) and (6), or equivalently the projector table, yield

```text
tr(TBQ)=168-2S,              tr(UBQ)=168-2S-4D,

tr(B^3T)=5544+2S,            tr(B^4T)=35784-6S,
tr(B^2U)=168-2S,
tr(B^3U)=5376+4S+4D,         tr(B^4U)=37968-32S-12D.   (7)
```

All expressions in (5)--(7) are integral for integer `S,D`.  Spectral
projector traces themselves are rational traces of rational idempotents and
are not required to be integers; their denominators yield no congruence.

## Sum over all 99 roots

Use the independently audited first moments

```text
S_*=sum_r S(r)=8316-2n3,
D_*=sum_r D(r)=n3-z11/4.                               (8)
```

The projector sums are:

| `lambda` | `sum_r a_lambda(T_r)` | `sum_r a_lambda(U_r)` |
|--:|:--|:--|
| 12 | `198` | `198` |
| 3 | `1584-4n3/105` | `1584+4n3/21-z11/105` |
| 0 | `n3/6` | `-n3/3+z11/24` |
| -2 | `1188-n3/5` | `1188-z11/20` |
| -4 | `-2970+n3/14` | `-2970+n3/7+z11/56` |

In particular the most transparent global mixed traces are

```text
sum_r tr(T_r B_r Q_r)=4n3,
sum_r tr(U_r B_r Q_r)=z11,
sum_r tr(B_r^2 U_r)=4n3.                               (9)
```

Thus the two new-looking contractions in (9) are exact spectral
reexpressions of the already known motif counts, not additional equations.
For completeness,

```text
sum tr(B^3T)=565488-4n3,
sum tr(B^4T)=3492720+12n3,
sum tr(B^3U)=565488-4n3-z11,
sum tr(B^4U)=3492720+52n3+3z11.                        (10)
```

## Exhaustion of the immediate scalar inequalities

For two symmetric factors define their scalar projector inner product

```text
p(F,H)=sum_lambda a_lambda(F)a_lambda(H)/rank(E_lambda).
```

Orthogonal projection in Frobenius space says the residual Gram matrix

```text
[ 168-p(T,T)        2S-p(T,U)       ]
[ 2S-p(T,U)   168+4D-p(U,U) ]                         (11)
```

must be positive semidefinite.  The producer expands (11) exactly as a
polynomial in `S,D`.  To prove that it supplies no hidden inequality,
normalize

```text
x=S/84,       y=D/42,       h=1-x-y.
```

The domain (3) is precisely `x,y,h>=0`.  Both diagonal residuals have
strictly positive degree-two triangular Bernstein coefficients.  The degree
four Bernstein coefficients of the determinant of (11), indexed by
`(i,j,k)` for the basis `4!/(i!j!k!) x^i y^j h^k`, are

```text
(0,0,4)  9570288/625       (0,1,3) 12261123/625
(0,2,2) 14702058/625       (0,3,1) 16893093/625
(0,4,0) 18834228/625

(1,0,3)   423654/25        (1,1,2)   2631839/125
(1,2,1)  3095428/125       (1,3,0)   3509037/125

(2,0,2)   365344/25        (2,1,1)     93688/5
(2,2,0)     112308/5

(3,0,1)      43512/5       (3,1,0)      65268/5
(4,0,0)            0.
```

They are all nonnegative.  The sole zero is the expected corner
`(S,D)=(84,0)`, where `T=U`.  Hence the full two-factor
Frobenius/Cauchy condition is automatically satisfied everywhere in (3).

The operator bounds

```text
|a_lambda(T)|,|a_lambda(U)| <=2 rank(E_lambda),
|a_lambda(T+/-U)|           <=4 rank(E_lambda)
```

are affine absolute-value inequalities.  The exact audit checks all three
vertices `(0,0),(84,0),(0,42)` of (3), so they too hold throughout the
simplex.

Finally, summing over roots does not improve the result.  The mean local
point has barycentric coordinates

```text
x_bar = S_*/8316                 =1-n3/4158,
y_bar = 2D_*/8316                =(4n3-z11)/16632,
h_bar = (8316-S_*-2D_*)/8316     =z11/16632.            (12)
```

Nonnegativity of (12) is exactly the already known domain

```text
0<=n3<=4158,          0<=z11<=4n3.
```

Jensen/Bessel on the 99-root direct sum evaluates (11) at this mean point,
so the same Bernstein certificate proves that no further global inequality
appears.

## Boundary

The general-root projector traces are rigorous and sharpen the endpoint-only
presentation, but all immediate operator, projected Frobenius, Cauchy, and
integrality tests are redundant with the elementary edge-profile simplex.
The missing information is the entrywise, noncommutative placement of `T`
and `U` inside the fixed `Q` scaffold.  For example, the independent
`T`-fit/Berge-triangle residual constraints act at exactly that stronger
level and are invisible to this scalar calculation.

Reproduce with:

```text
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_root_general_tu_spectral.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_root_general_tu_spectral_audit.py
```
