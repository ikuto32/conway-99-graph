# The `YY^T` pair split, its Bose--Mesner projection, and the first missing moment

Status: `EXACT_YYT_PAIR_AND_ORDER8_SHADOW_CLASSIFICATION`.

Assume throughout that `G` is an `srg(99,14,1,2)`.  This note continues
`scratch_theory_root_flag_union.md`.  Its notation is

```text
X[(T,t),(U,u)] = 1
```

when the two disjoint triangles have exactly two cross edges and `t,u` are
the unmatched endpoints, `F[(T,t),r]=1` when `t=r`, and

```text
Y = F^T X,                 H = YY^T = F^T X^2 F.
```

The conclusion is deliberately two-sided.  The Bose--Mesner projection gives
two exact global PSD inequalities.  On the other hand, a complete local
classification shows that every off-diagonal entry of `H` is a nine-vertex
statistic.  The existing order-eight four-root block sees an exact shadow of
that statistic, but misses one binary triangle-completion mark.

## 1. Diagonal and total mass

Put

```text
D_* = sum_r D(r) = N(H_delta) = n3-z11/4,
N   = n3+D_* = 2*n3-z11/4,
Q2  = sum_T q(T)^2.
```

The flag identities give

```text
H[r,r] = 84-S(r)+2D(r) = 84-E0(r)+3D(r),             (1)
tr(H)  = 2N,                                         (2)
1^T H 1 = 3Q2.                                       (3)
```

Let

```text
a = sum_{r<s, r~s} H[r,s],
b = sum_{r<s, r not~s} H[r,s].
```

Then

```text
a+b = (3Q2-2N)/2.                                    (4)
```

## 2. Exact off-diagonal motif classification

Expand one summand of `H[r,s]`.  It consists of source flags `(T,r)` and
`(T',s)` joined by `X` to the same target flag `(U,u)`.

The source triangles cannot meet.  Indeed, suppose that they meet in `p`,
and write

```text
T={r,p,x},  T'={s,p,y},  U={u,c,d}.
```

Both `{p,x}` and `{p,y}` are perfectly matched to `{c,d}`.  If the two
copies of `p` are matched to different endpoints, then the edge `cd` has
the two common neighbours `u,p`, contradicting `lambda=1`.  If they are
matched to the same endpoint, say `c`, then the nonedge `pd` has the three
common neighbours `c,x,y`, contradicting `mu=2`.  This exhausts the four
labelled matching choices.  Thus `T,T',U` are pairwise disjoint and every
off-diagonal term uses nine vertices.

Cross edges between two triangles form a matching: two edges from one
vertex to an adjacent pair in the other triangle would give that edge two
common neighbours.  There are exactly

```text
sum_{j=0}^3 binom(3,j)^2 j! = 34
```

partial matchings between `T` and `T'`.  Exact enumeration leaves 18 marked
patterns after the internal `lambda/mu` upper tests and nine unmarked graph
types.  In the Wave147 degree-cell mask convention the identities are

```text
a = x9[35795456704] + x9[16260620944] + x9[14890182020],       (5)

b = x9[45743280832] + x9[16827884176] + x9[27220517280]
    + 3*x9[14890181764] + 2*x9[14874613832]
    + x9[14337762352].                                       (6)
```

Here `x9[K]` is the induced count of the unmarked nine-vertex class, and the
displayed coefficient is the number of unordered-root `YY^T` marks in one
copy.  The edge counts of the three classes in (5) are `14,15,16`; those of
the six classes in (6) are `13,14,14,15,15,15`.  The script records full
degree sequences, representative edge lists, both canonical-mask conventions,
and reconstructed mark multiplicities.

In particular there is no order-eight term hidden in the adjacent/nonadjacent
split of `YY^T`.  Equations (5)--(6), rather than an unverified claim of an
order-eight closure, are the exact coefficient identity.

## 3. Bose--Mesner projection

The adjacency eigenvalues are `14,3,-4`, with multiplicities `1,54,44`.
Orthogonally project the PSD matrix `H` onto the adjacency algebra.  Since
the primitive idempotents are mutually orthogonal projections, the projected
matrix is PSD and equals

```text
Hbar = d I + e A + f (J-I-A),
d = 2N/99,       e = a/693,       f = b/4158.          (7)
```

Its two nontrivial eigenvalues give

```text
d+3e-4f >= 0,                 d-4e+3f >= 0.            (8)
```

Using (4), these are exactly

```text
3Q2/11 - 4N <= a <= Q2/6 + 3N,                         (9)
4Q2/3  - 4N <= b <= 27Q2/22 + 3N.                     (10)
```

The trivial eigenvalue is `3Q2/99`.  No automorphism assumption is used.
The same inequalities also follow by writing the projection as
`sum_i tr(E_i H)E_i/rank(E_i)`.

For individual roots, PSD supplies only

```text
H[r,s]^2 <= (84-E0(r)+3D(r)) (84-E0(s)+3D(s)).         (11)
```

The right side still contains the local diagonal count, while the left side
is one of the order-nine statistics above.  Thus (11) is not a pointwise
lower bound for `E0` in the known variables.

The support polynomial

```text
Z = 1_{Y>0} = (3Y-Y o Y)/2
```

does give `diag(ZZ^T)_r=84-E0(r)`, but `ZZ^T >= 0` is the Gram positivity of
the support rows themselves.  It does not follow as a new linear consequence
of the three class averages of `YY^T`; replacing `Y` by its support loses the
column multiplicities.  Hence this Schur polynomial restates, rather than
proves, the desired support bound.

## 4. Exact order-eight shadow in the full four-root blocks

Delete `u`, the unmatched vertex of the common target triangle.  The target
edge `cd`, the two source triangles, and `r,s` leave an eight-vertex
configuration.  Let `beta_e,beta_n` count these shadows for unordered
adjacent and nonadjacent roots.  Exhaustive evaluation on the frozen 916
Wave147 classes gives

```text
beta_e = x8[5691760] + 2*x8[127242964] + x8[144594160],       (12)

beta_n = x8[15424580] + x8[15436356] + x8[44489072]
       + x8[110787152] + x8[127315016] + x8[149654084].      (13)
```

These are not merely ad hoc class vectors.  They are explicit entries in
the full four-root raw moments of Wave152.  Write `M_tau` for that raw
moment matrix.

For adjacent roots use root mask `12`, with pointwise root edges `03,12`,
source roots `0,3`, and target edge `12`.  Then

```text
4 beta_e = M_12[17724,29988].                              (14)
```

For nonadjacent roots use root mask `1`, target edge `01`, source roots
`2,3`, and flag sets

```text
L={19601,23697,23817},   R={28817,29841,29961}.
```

Then

```text
4 beta_n = sum_{i in L, j in R} M_1[i,j].                 (15)
```

The factor four consists of the two orientations of the target-edge labels
and the passage from ordered to unordered source roots.  The accompanying
script verifies (14)--(15) coefficient-by-coefficient on all 916 classes.

The three masks in (12) also all occur in the independently verified sparse
mask-12 covariance cut from Wave156.  That cut uses different flags
`5428,6324`, so this common support is structural overlap, not equality of
the two functionals.

## 5. Completing the shadow by the prism relation

There is a useful way to make the order-eight shadow itself a Gram matrix.
Let `Pi` be the symmetric flag relation

```text
Pi[(T,t),(U,u)]=1
```

when `T,U` form a triangular prism and `tu` is their corresponding
perfect-matching edge.  Set

```text
Xhat=X+Pi,       Yhat=F^T Xhat,       G=Yhat Yhat^T.       (A1)
```

The twelve-choice construction proving (2) partitions into the `q(T)`
two-cross-edge choices and the `a_3(T)` prism choices.  Hence every row and
column of `Xhat` has sum 12.  It follows that every row of `Yhat` has sum 84
and every column has sum 12.

The two summands in `Yhat` have disjoint support: an `X` contribution has
`ru` absent, whereas a `Pi` contribution has `ru` present.  Moreover the
collapsed `Pi` entries are at most one.  To see this, write the target edge
as `cd`.  One prism source triangle through `r` supplies, for the nonedge
`rc`, the two common neighbours `u` and the source non-root matched to `c`.
A second source triangle through `r` would supply a third distinct common
neighbour, contrary to `mu=2`.  Therefore

```text
Yhat[r,beta] is in {0,1,2},
Yhat[r,beta]=2 iff Y[r,beta]=2.                            (A2)
```

The entries equal to two are consequently still exactly the diagonal events
counted by `D(r)`.  Thus

```text
G[r,r]=84+2D(r),             tr(G)=8316+2D_*,
1^T G 1=693*12^2=99792.                                  (A3)
```

For `r != s`, a term of `G[r,s]` is precisely an order-eight shadow from
(12)--(13): the unique triangle mate of its target edge decides whether each
source root used `X` or `Pi`.  Hence `beta_e,beta_n` are the adjacent and
nonadjacent unordered off-diagonal sums of `G`, and

```text
beta_e+beta_n=45738-D_*.                                  (A4)
```

Projecting `G` to the Bose--Mesner algebra, exactly as in Section 3, gives

```text
-7560-4D_* <= beta_e <= 18018+3D_*,
27720-4D_* <= beta_n <= 53298+3D_*.                       (A5)
```

The useful sides are the upper bound on `beta_e` and lower bound on `beta_n`.
Via (14)--(15), they are the exact order-eight inequalities

```text
M_12[17724,29988] <= 72072+12D_*,
sum_{i in L,j in R} M_1[i,j] >= 110880-16D_*.             (A6)
```

These inequalities use the full fixed marginals of the augmented relation;
they do not assume that an ordinary--exceptional block is a function in both
directions.  The only function assertion above is the proved one-sided
statement that a fixed `(r,(U,u))` receives at most one prism contribution.

### 5.1 Vertex--edge incidence and a weighted 2-factor

Identify a flag `(T,t)` with its opposite graph edge `e=T\{t}`.  Let `C` be
the ordinary `99 x 693` vertex--edge incidence matrix, let `R` be the
triangle-mate incidence matrix

```text
R[v,e]=1 iff v is the unique vertex completing e to a triangle,
```

and write `J_E` for `Xhat` in the opposite-edge coordinates.  Thus two
disjoint graph edges are adjacent in `J_E` exactly when their four cross
incidences form a perfect matching.  Entrywise,

```text
C J_E = A C-C-2R.                                      (A7)
```

For completeness, fix `e=ab`.  A vertex `v` is in exactly one of four
classes.  If it is an endpoint, `(AC,C,R)=(1,1,0)`; if it is the unique
triangle mate, the triple is `(2,0,1)`; if it is outside the triangle and
adjacent to one endpoint, it is `(1,0,0)`; otherwise it is `(0,0,0)`.
The right side of (A7) is respectively `0,0,1,0`.  In the third case, say
`v~a` and `v` is nonadjacent to `b`, the second common neighbour `w` of
`v,b` gives the unique `J_E`-neighbour edge `vw`; `lambda=1` forces the
other cross incidences absent.  This proves (A7), not just its row sums.

The elementary mate-incidence identities are

```text
R C^T=A,                  R R^T=7I.
```

Transpose (A7), multiply by `R`, and use
`A^2=12I-A+2J_99`.  Since `Yhat=R J_E`, this gives

```text
Yhat C^T = R J_E C^T
          = A^2-A-14I
          = 2(J_99-I-A).                               (A8)
```

All entries of `Yhat` are nonnegative.  Equation (A8) therefore says that,
for every root `r`, its row is supported on graph edges whose endpoints are
both among the 84 nonneighbours of `r`, and has weighted degree exactly two
at each of those vertices.  It is an integer weighted 2-factor.  Its doubled
edges are exactly the `D(r)` fibre diagonals.

This also settles its relation to the Wave65 transition factor.  For an
outside vertex `p`, let `L(p)` be its two root-neighbour labels and let

```text
d_r(p,q)=#{x in L(p): mate(x) in L(q)}.
```

On an outside graph edge `pq`, direct comparison with `J_E` gives
`Yhat[r,pq]=d_r(p,q)`.  If `E0(r)=0`, then `S(r)=D(r)=0`; the factor is
simple and consists of the 84 selected edges of type

```text
(|L(p) intersect L(q)|,d_r(p,q))=(0,1).                 (A9)
```

Wave65's transition factor `T`, by contrast, consists of the 84 selected
exact-symbol-sharing edges, now of type `(1,0)`.  Hence the two factors do
**not** coincide: they are edge-disjoint.  The `Yhat` factor lies inside
Wave65's 10-regular disjoint-label point graph `D`; it is exactly the
selected `d_r=1` factor already present in the independently verified Wave3
weighted-factor identity.  This comparison also prevents an accidental
reuse of the letter `D`: `D(r)` above counts doubled fibre diagonals, whereas
Wave65's matrix `D` is the entire disjoint-label residual graph.

### 5.2 Endpoint spectral traces of the two factors

At the prism-free endpoint, let `B` be the adjacency matrix on the 84 outside
vertices and `Q` the line graph of `K14-7K2`.  The rooted SRG equation is

```text
Q=10I+2J-B^2-B.                                         (A10)
```

Thus the `B` eigenspaces `12,3,0,-2,-4`, of respective ranks
`1,40,7,6,30`, have `Q` eigenvalues `22,-2,10,8,-2`.

There are two useful entrywise checks.  In the line graph, two labels of
type `(Q,d)=(1,0)` have exactly 11 common neighbours, while labels of type
`(0,1)` have exactly three; hence

```text
(Q^2)[x,y]=11 on T,             (Q^2)[x,y]=3 on U.       (A11)
```

Also the rooted endpoint-profile equation, for a base point `s`, is

```text
sum_{z: s in L(z)} B[x,z]
 =2-[s in L(x)]-[mate(s) in L(x)].
```

Sum this over the two points of `L(y)`.  The term `z=y` is counted twice and
every other label at most once, so for a selected edge `xy`,

```text
(BQ)[x,y]=2-Q[x,y]-d_r(x,y)=1       on T union U.         (A12)
```

Let `a_lambda(F)=tr(F E_lambda(B))`.  The equations
`sum a_lambda=0`, `a_12=2`, `tr(FB)=168`, together with the `Q,Q^2` traces
from (A11), uniquely give

| factor | `a_12` | `a_3` | `a_0` | `a_-2` | `a_-4` |
|:--|--:|--:|--:|--:|--:|
| `T` | 2 | 72/5 | 7 | 18/5 | -27 |
| `U` | 2 | 112/5 | -7 | 18/5 | -21 |

Equation (A12) independently checks `tr(TBQ)=tr(UBQ)=168`.  The resulting
mixed moments are

```text
tr(B^3 T)=5544,       tr(B^4 T)=35784,
tr(B^3 U)=5376,       tr(B^4 U)=37968.                   (A13)
```

For `T`, this pins Wave65's parameter `w=tr(T E_3)` to `72/5`, inside its
previous interval `[64/5,16]`; it also gives
`35784+3*5544=52416`, exactly the Wave65 scalar identity.

The immediate joint PSD/Cauchy tests do not contradict simultaneous
existence.  The scalar-projection Frobenius lower bounds for
`T,U,T+U,T-U` are respectively

```text
10661/250, 10101/250, 16912/125, 154/5,
```

against available squared norms `168,168,336,336`.  Since `tr(TU)=0`, the
remaining two-vector Cauchy determinant is `9570288/625>0`.  All projector
operator bounds for the two 2-factors and their sum/difference pass, and all
mixed power traces in (A13) are integral.  Thus this fixed-`Q` scalar layer is
strictly sharper than the prior interval for `w`, but supplies no elementary
PSD, Cauchy, or integrality contradiction by itself.

## 6. The precise missing order-nine statistic

The edge `cd` has a unique triangle mate `u`.  Internal pair bounds force
`u` to be nonadjacent to the four non-root source vertices, but either
adjacency bit `ur,us` can still be zero or one.  Let `R_e,R_n` count shadows
whose mate has at least one of these two bits equal to one.  Then

```text
a = beta_e-R_e,            b = beta_n-R_n,              (16)
R_e,R_n >= 0.                                                
```

For one target flag `(U,u)`, put `q=q(U)` and `p=12-q`.  Its twelve augmented
neighbours consist of `q` good (`X`) flags and `p` bad (`Pi`) flags.  The
same-root collisions occur only among good flags and cancel when old and
augmented off-diagonal masses are subtracted.  Thus the flag contributes
`binom(12,2)-binom(q,2)` bad-containing pairs.  Summing over the three flags
of each target triangle gives the exact identities

```text
R_e+R_n = beta_e+beta_n-(3Q2-2N)/2,                       (17)
        = 3 sum_T [66-binom(q(T),2)]
        = 45738+n3-3Q2/2.
```

or, in four-root raw moments,

```text
M_12[17724,29988] + sum_{L x R} M_1[i,j]
    = 6Q2-4N + 4(R_e+R_n).                                (18)
```

The four mate-bit states also admit a solver-free local capacity bound.  The
`p` bad roots form a subset of `N(u)=7K2`, so the number of adjacent `11`
pairs is at most `floor(p/2)`.  A good root is nonadjacent to `u`, hence has
exactly two neighbours in `N(u)`; including good-flag multiplicity, the
number of adjacent `01/10` pairs is at most `q min(p,2)`.  Therefore, per
target flag,

```text
R_e(flag) <= f(q)=floor((12-q)/2)+q min(12-q,2),
R_n(flag) >= h(q)=66-binom(q,2)-f(q).                    (18a)
```

| `q` | `p` | all corrected pairs | `f(q)` | `h(q)` |
|---:|---:|---:|---:|---:|
|0|12|66|6|60|
|1|11|66|7|59|
|2|10|65|9|56|
|3|9|63|10|53|
|4|8|60|12|48|
|5|7|56|13|43|
|6|6|51|15|36|
|7|5|45|16|29|
|8|4|38|18|20|
|9|3|30|19|11|
|10|2|21|21|0|
|11|1|11|11|0|
|12|0|0|0|0|

Using only `sum q=2n3/3` and `Q2=sum q^2`, the complete lower convex hull of
these thirteen points gives the sharp family generated by (18a):

```text
R_n >= max(0,
  41580-3Q2,
  41580-2n3-3Q2/2,
  41580-22n3+3Q2/2,
  38808+4n3-3Q2,
  33264+8n3-3Q2,
  24948+12n3-3Q2,
  13860+16n3-3Q2).                                     (18b)
```

Each plane is pointwise below `h(q)` on `q=0,...,12`; exact enumeration of
all supporting triples gives precisely these eight facets.  Together with
(17), this is equivalently an upper family for `R_e`.  It is the strongest
consequence of this particular capacity table using only the first two
moments of `q`, not a claim that no stronger graph-level mate-bit inequality
exists.

This identifies the first missing data exactly: an order-eight-to-nine
extension of the marked four-root configuration recording whether the unique
common neighbour of the target edge has root-adjacency signature `00`,
`01/10`, or `11`.  Equivalently, the shadow is a selected second moment of
the four-root flag vector, while (16) needs that second moment weighted by a
binary one-vertex extension indicator--a mixed third moment.  The existing
four-root covariance controls the shadow jointly with other order-eight
moments but does not itself contain this indicator.

Combining (9)--(10) with `a<=beta_e`, `b<=beta_n` gives two valid necessary
order-eight-shadow inequalities:

```text
11 M_12[17724,29988] >= 12Q2-176N,                       (19)
3 sum_{L x R} M_1[i,j] >= 16Q2-48N.                     (20)
```

They are rigorous, but need not be strong: `Q2` itself is a triangle-root
second moment.  Its universally available bounds are

```text
sum_T q(T)=2n3/3,
Q2 >= (2n3/3)^2/231 = 4n3^2/2079,                       (21)
```

with the standard sharper integer-convex rounding because the 231 values
`q(T)` are integers in `[0,12]`.

## 7. Boundary for an `E0` lower bound

The exact order-eight pseudowitness recorded in
`scratch_root_order8_e0_lower_bound_boundary.md` already has
`sum_r E0(r)=0` while satisfying Wave147/148 and fifteen scalar four-root
cuts.  Therefore (7)--(21), without the complete higher marked moment or a
new graph-level integrality argument, cannot imply a positive universal
`E0` lower bound.

The augmented identities show this boundary particularly cleanly.  On the
Wave159 rational witness, `n3=4158` and `z11=16632`, so `D_*=0`.  Since
`P=0`, every triangle has `q=12`, whence `Q2=33264` and (17) gives
`R_e+R_n=0`.  Exact evaluation of (12)--(13) gives

```text
beta_e = 2070988839162253926522129810139492169693988
         /517521941776627318214642378508170816671,
beta_n = 21599429733817126353979183298067224643204210
         /517521941776627318214642378508170816671,
beta_e+beta_n=45738.
```

Both inequalities in (A5), and all capacity bounds (18b), pass exactly.
Thus the prism augmentation closes the shadow and controls the signs of the
order-nine correction, but these scalar constraints still do not force
`D_*`, `sum E0`, or any pointwise `E0(r)` to be positive.

For the actual support second moment

```text
M2 = sum_r binom(84-E0(r),2),
```

the independent event-pair census in that boundary artifact gives the
complementary decomposition

```text
M2 = 4*x8[127242964] + sum_{h=9}^{13} R_h.               (22)
```

Thus both approaches locate the same first obstruction at order nine, but
they are different functionals: (5)--(6) concern row intersections in
`YY^T`, whereas (22) concerns pairs inside one support row of `Z`.

## Reproduction artifacts

```text
scratch_theory_root_yyt_pair_classification.py/.json
scratch_theory_root_yyt_order8_shadow.py/.json
scratch_theory_root_yyt_bose_mesner_audit.py/.json
scratch_theory_root_yyt_augmented_relation.py/.json
scratch_theory_root_yyt_augmented_relation_audit.py/.json
scratch_theory_root_flag_union.md
scratch_root_order8_e0_lower_bound_boundary.py/.json/.md
```

No graph, positive `E0` bound, or solution of Conway's problem is claimed.
