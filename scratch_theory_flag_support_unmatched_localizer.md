# Minimal unmatched-slot localizer above the Wave205 kernel

Status: `EXACT_MINIMAL_UNMATCHED_SLOT_LOCALIZER_BOUNDARY_PASS`, with a
producer-independent exact audit.

This note assumes the usual triangle/flag notation of
`scratch_theory_root_flag_union.md`.  It does not construct a graph and does
not claim an `E0` lower bound.  It identifies the smallest real PSD object
which retains the slot information discarded by Wave205, derives its optimal
quadratic pointwise inequality, and records exactly why the existing frozen
inputs do not make that inequality strong enough.

## 1. Exact indices

Let `V`, `T`, and `F` be respectively the 99 points, 231 graph triangles,
and 693 flags `(T,t)` with `t in T`.  Write `B[x,T]` for point--triangle
incidence and `A` for graph adjacency.  Wave205 uses ordered triangle pairs:

```text
U[x,(T,U)] = B[x,T]B[x,U],
K_D[(T,U),(R,S)] = D[T,R]D[R,U]D[U,S]D[S,T],
H=U K_D U^T                         over F_3.             (1)
```

On the endpoint alphabet, the value-two triangle relation is the Schur
selector

```text
L = 2(D o D-D)                      over F_3.             (2)
```

Thus `L[T,U]=1` exactly for a disjoint pair with two cross edges.  Equation
(1), restricted to a diagonal target pair `(U,U)`, sees products of the form
`D[T,U]^2 D[T',U]^2`.  Applying (2) to the two legs refines this to
`L[T,U]L[T',U]`, but it still forgets which point is unmatched.

The minimal one-sided slot tensor restoring that information is

```text
W[x,T,U]
 =B[x,T] L[T,U] (1-(A B)[x,U]).                         (3)
```

On an `L`-pair, `(AB)[x,U]` is zero or one.  Hence (3) is one exactly when
`x` is the unmatched point of the source triangle `T`.  It is a nominal
`99 by 231 by 231` zero-one tensor, but has only 8,316 nonzero ordered
entries.  The full unmatched lift is then

```text
X[(T,x),(U,u)] = W[x,T,U] W[u,U,T],
Y[x,(U,u)]     = sum_T X[(T,x),(U,u)].                  (4)
```

Let `C` be the `693 by 231` flag-to-triangle collapse,
`C[(U,u),R]=1[U=R]`, and define

```text
M=Y C,
M[x,U]=sum_u Y[x,(U,u)]=sum_T W[x,T,U].                 (5)
```

The last equality uses the unique unmatched point at the target end of each
`L`-pair.  This `99 by 231` matrix is the least refinement of the diagonal
slice of `K_D|row(U)` which remembers the source slot but still collapses the
three target slots.

Equivalently, the exact sparse diagonal-slice tensor and its cross-root
contraction are

```text
Khat[(x,T),(y,T');U]=W[x,T,U]W[y,T',U],
Theta[x,y]=sum_(U,T,T') Khat[(x,T),(y,T');U]
          =(M M^T)[x,y].                                (5a)
```

For `x=y`, restricting `T,T'` to the seven-block `x`-star is precisely the
`L[T,U]L[T',U]` diagonal-target slice with both source-unmatched selectors
restored.  No fourth triangle index is needed for this minimal slice.

## 2. The minimal cross-root PSD localizer

For a root `x` and target triangle `U`, put

```text
p_xU=(Y[x,(U,u)]:u in U),       m_xU=1^T p_xU=M[x,U].   (6)
```

Every coordinate of `p_xU` is in `{0,1,2}`.  Same-slot and all-slot
contractions are

```text
G_=Y Y^T,
G_triangle=M M^T=Y C C^T Y^T.                          (7)
```

The three-slot permutation module splits as the trivial line and its
two-dimensional zero-sum complement.  Projecting onto the latter gives the
minimal signed cross-root localizer

```text
3 Lambda
 =3G_-G_triangle
 =Y(3I_693-C C^T)Y^T >= 0.                             (8)
```

Indeed, each diagonal `3 by 3` block is `3I_3-J_3`, and

```text
p^T(3I_3-J_3)p
 =(p0-p1)^2+(p1-p2)^2+(p2-p0)^2.                       (9)
```

Thus (8) is a genuine real PSD matrix simultaneously coupling all 99 roots.
It should not be confused with (1), which is a bilinear form over `F_3`.

This construction is minimal in a precise sense.  After averaging over the
intrinsic `S_3` action on a target triangle, every canonical quadratic PSD
slot form is `aI+bJ`, with

```text
a>=0,                 a+3b>=0.                          (10)
```

For `a>0`, the strongest lower bound on the same-slot square is obtained at
the boundary `b/a=-1/3`, namely (8).  The other boundary ray `J` only gives
the tautology `m^2>=0`.  Hence no other slot-symmetric quadratic PSD
contraction of this three-coordinate local problem is stronger.

## 3. The one correct-direction inequality

Write

```text
u_x=sum_U m_xU=84-S(x).
```

The diagonal same-slot energy is

```text
sum_U ||p_xU||^2=u_x+2D(x).
```

Taking the `(x,x)` entry of (8) therefore gives

```text
6D(x) >= sum_U m_xU^2-3u_x
       = sum_U m_xU^2-3(84-S(x)).                       (11)
```

This is the desired sign: concentration of several one-sided unmatched
incidences on one target triangle forces a doubled target flag.

The complete symbolic basis has only 27 vectors `p in {0,1,2}^3`.  Exact
enumeration gives

| `m=1^T p` | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| minimum `sum_u binom(p_u,2)` | 0 | 0 | 0 | 0 | 1 | 2 | 3 |

Consequently the sharp integer strengthening of (11) is

```text
D(x) >= sum_U max(0,m_xU-3),                            (12)
|supp Y_x| <= u_x-sum_U max(0,m_xU-3).                  (13)
```

For a target support bound `h`, (11) would suffice if a new theorem proved

```text
sum_U m_xU^2 >= 9u_x-6h.                                (14)
```

Thus `h=13` needs the right side `9u_x-78`, and `h=12` needs `9u_x-72`.
Equivalently, (12) needs at least `u_x-h` units of mass above three.

## 4. Why Wave205 does not supply the missing moment

Wave205's `t_xy`, including the exact nonedge average seven, determines only

```text
sum_U m_xU=u_x=84-S(x).
```

It does not determine `sum_U m_xU^2` or the number of `U` with `m_xU>=4`.
The factorization `H=U K_D U^T` cannot be read as a real PSD constraint:
it lives over `F_3`.  The frozen Wave205 positive control has nonzero
fourth-trace rank nine and zero diagonal.  Any nonzero symmetric real lift
with zero diagonal has a principal block

```text
[0 a]
[a 0]
```

of determinant `-a^2`, so it is indefinite.  Real positivity arises only
after introducing the actual incidence tensor `W` and the slot projector in
(8).

Nor does `rank_F3(U)=99` yield a cap for (8): its 99 independent unit witness
columns say precisely that the star-pair source has no rank compression.

## 5. Exact positive `T=0` control

The earlier cyclic 99-root flag control was reconstructed without importing
its producer.  It has

```text
X degree                         12,
Y entries                         0 or 1,
every Y row sum/support             84,
D(x)=formal E0(x)                    0,
M=YC entries                       0 or 1,
sum_U m_xU^2                         84.
```

Nevertheless, `3Lambda` has diagonal 168 and is PSD.  Exact rational
elimination gives

```text
rank_Q(3Lambda)=94,          nullity=5,
rank mod 101,103,107 = 94,94,94.                       (15)
```

An explicit primitive integer nullspace basis independently supplies the
matching upper bound; its `L1` norms are `22,22,99,99,99` and its largest
coordinates are `1,1,3,3,3`.  Thus the new PSD constraint is strongly
nonzero--in particular every root diagonal is strict--on a formal `D=0`
point.  Positivity or a generic rank condition on `Lambda` cannot force even
`D(x)>0`.

This remains a scoped relaxation control: its formal `K2` is not the actual
two-cross relation of its shadow, and it fails the integral projector,
transport, and SRG equations.  It is not a graph candidate.

## 6. Frozen order-eight boundary

The scripts only read and hash the already verified assets:

```text
916 order-eight classes,
208 ordinary deletion rows,
944 marked-vertex rows,
4,440 marked-pair rows,
2,414 coefficient matrices.
```

Nothing was regenerated.  For one root, a diagonal term in (11) uses two
source triangles and one target triangle and has union order at most eight.
The complete cross-root entry `Lambda[x,y]` can use two disjoint source
triangles together with the common target triangle and reaches order nine.
Deleting the target mate leaves the known order-eight shadow, but loses the
mate's adjacency signature; this is exactly the already audited
order-eight-to-nine boundary.

The frozen order-eight pseudowitness also has total `E0=0`.  Therefore no
global averaging of (11) using only the existing order-eight equalities can
force a positive `D` moment.  A genuinely new use of (8) must provide either

1. a pointwise graph-specific lower bound for `sum_U m_xU^2`; or
2. enough sparse marked order-nine cross-root entries to use PSD minors of
   `Lambda` jointly, while retaining the mate signature.

## 7. Disposition

The unmatched-slot refinement does reveal one new correct-direction
inequality, (11), and its sharp integer version (12).  It does **not** prove
`|supp Y_x|<=13` or `<=12`.  The exact obstruction is now a concentration
moment of the one-sided unmatched masses `M[x,U]`, not another scalar
fourth trace.

Reproduction artifacts:

```text
scratch_theory_flag_support_unmatched_localizer.py/.json
scratch_theory_flag_support_unmatched_localizer_independent_audit.py/.json
```

No `submission.txt`, graph, endpoint exclusion, or Conway-99 resolution is
claimed.
