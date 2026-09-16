# The endpoint triangle-flag relation and its first unfixed synchronization

Status: `E0_ZERO_TRIANGLE_FLAG_RELATION_EXACT_STUDY_PASS`, with independent
finite/algebraic replay
`INDEPENDENT_E0_ZERO_TRIANGLE_FLAG_RELATION_AUDIT_PASS`.

This note assumes a putative `srg(99,14,1,2)` and the extreme boundary

```text
sum_r E0(r)=0.
```

It derives a new strict collision bound and excludes the special case in
which the 99 vertex cells are equitable for the flag relation.  It does not
exclude the endpoint itself.

## 1. The endpoint and the flag graph

Every `E0(r)=S(r)+D(r)` is a sum of nonnegative integers.  Hence the boundary
assumption gives, pointwise,

```text
E0(r)=S(r)=D(r)=0.
```

There are no triangular prisms.  The standard identities therefore give

```text
P=0,  n3=4158,
q(T)=12,
(a0(T),a1(T),a2(T),a3(T))=(32,144,36,0)
```

for every one of the 231 graph triangles.

Let `Omega={(T,t):t in T}` be the 693 triangle flags.  The symmetric matrix
`X` joins `(T,t)` to `(U,u)` when `T,U` are disjoint, have exactly two cross
edges, and `t,u` are the unmatched vertices.  Identifying `(T,t)` with the
graph edge `T\{t}`, the prism-free endpoint identifies `X` with the
opposite-edge graph.  Consequently

```text
X is simple, symmetric, 12-regular and triangle-free,
|E(X)|=4158,
tr(X)=0, tr(X^2)=8316, tr(X^3)=0,
tr(X^4)=191268+8 c4(X).                              (1)
```

The last formula is the ordinary fourth-walk formula for a 12-regular graph.
Thus the first trace not fixed by the endpoint is already the number of
four-cycles of `X`.  Under the flag-edge identification it is an
order-at-most-eight graph-motif statistic.

## 2. Two flag partitions and the projector quotient

Use the following incidence matrices:

```text
F : 693 x 99,   F[(T,t),r]=1 iff t=r,
Q : 693 x 231,  Q[(T,t),U]=1 iff T=U,
N = F^T Q       (point--triangle incidence),
C : 99 x 693    (ordinary point--edge incidence).
```

Then

```text
F^T F=7I,  Q^T Q=3I,  N N^T=7I+A,
C=NQ^T-F^T,  CF=A,  CQ=2N,  CC^T=14I+A.             (2)
```

Put

```text
K=Q^T X Q,       W=F^T X Q,       H=F^T X F,
Y=F^T X,         bar(A)=J-I-A.
```

The integral triangle projector `M` satisfies

```text
M^2=21M, M1=0, diag(M)=4, rank(M)=44.
```

At the endpoint its off-diagonal row alphabet is

```text
(+1)^32, 0^162, (-1)^36,
```

and its negative relation is exactly

```text
K=(M o M o M+M o M-2M)/2-36I
 =(M o M-M)/2-6I.                                    (3)
```

Thus `K` is a simple 36-regular graph on the 231 triangles.  Each `K` edge
is represented by exactly one `X` edge between the corresponding two
three-flag cells.

## 3. Incidence transport determines the collapsed vertex quotient

At the endpoint the ordinary edge-incidence identity is

```text
C X=A C-C-2F^T.                                      (4)
```

For a fixed graph edge, (4) follows by separating a point into four cases:
an endpoint, its triangle mate, an outside point adjacent to exactly one
endpoint, or an outside point adjacent to neither.  In the third case the
second common neighbour gives the unique opposite edge; the other cases
give zero.

Right multiplication of (4) by `Q` and `F`, using (2), gives

```text
W=N K-2A N+4N,                                       (5)
N W^T-H=A^2-A-14I=2 bar(A).                          (6)
```

Since `A^2=12I-A+2J`, substitution of (5) into (6) yields the exact bridge

```text
H=N K N^T+6I-6A-6J.                                 (7)
```

Equivalently, if `t=NKN^T` is the Wave205 integer two-count matrix, then

```text
t_rr=0,
t_rs=12                    if r~s,
t_rs=6+H_rs                if r not~s, r!=s.          (8)
```

Also, transposing (4) and multiplying by `F^T` gives

```text
Y C^T=2 bar(A).                                      (9)
```

At `D(r)=0`, every entry of `Y` is zero or one.  Equation (9) says that the
84 graph edges selected by row `r` form a simple 2-factor on the 84
nonneighbours of `r`.

## 4. The 7-by-7 blocks are partial matchings

The entry `Y[r,beta]` is the column degree of target flag `beta` in the
block from the seven flags centred at `r`.  Since `D(r)=0`, it is at most
one.  Applying the same statement with the other centre and using symmetry
shows that every block

```text
X[F_r,F_s]
```

has both row and column degrees at most one.  It is a partial matching.
Moreover unmatched endpoints of an `N3` are nonadjacent.  Therefore

```text
H_rr=0,
H_rs=0                    for r~s,
0<=H_rs<=7                for r not~s,
H1=84*1.                                                   (10)
```

There are 4,158 nonedge point-pairs and the total of `H_rs` over them is
4,158.  Hence the orthogonal projection of `H` to the Bose--Mesner algebra
is exactly `bar(A)`.  In particular

```text
tr(E_0 H)=84,  tr(E_3 H)=-216,  tr(E_-4 H)=132.       (11)
```

Define the block-collision count and the centred deviation by

```text
ell=sum_{r<s} binom(H_rs,2),
Delta=H-bar(A).
```

Then

```text
tr(H^2)=8316+4ell,
||Delta||_F^2=4ell.                                   (12)
```

Writing

```text
delta_3=||Delta E_3||_F^2,
delta_-4=||Delta E_-4||_F^2,
```

gives

```text
delta_3+delta_-4=4ell.                               (13)
```

### A zero nonedge block is locally admissible

For a graph nonedge `r,s`, (8) gives the exact equivalence

```text
H_rs=0  <=>  t_rs=(N K N^T)_rs=6.                   (13a)
```

This value cannot be excluded from the presently available two-centre
conditions.  The frozen Wave205 control `t6_h1` is an exact 28-vertex local
configuration with `t_rs=6`.  It has both centre degrees 14 and two centre
common neighbours; every local edge has at most one local common neighbour,
every local nonedge at most two; all exclusive neighbours have the required
opposite-centre `mu=2`; the selected disjoint blocks obey the endpoint cross
edge cap; and the full local two-star Gram is reproduced with rank 11,
principal determinant 2, and kernel minimum weight 6.  Hence it realizes
`H_rs=0` while passing all of those local tests.

Wave205 also calls another quantity `h=1`; that `h` is an `F_3` fourth trace
and is unrelated to the matrix entry `H_rs` in this note.

The control is deliberately not a 99-vertex graph.  It omits completion of
the unsaturated local pairs and simultaneous compatibility of the 99
overlapping point-stars.  Thus it proves the precise boundary statement:
local `lambda/mu`, selected block-cap, and two-star Gram/projectivity data do
not imply `H_rs>=1`.  A proof excluding a zero block must use this missing
global synchronization.

## 5. The equitable or cover case is impossible

The vertex partition is equitable precisely when

```text
X F=F B.
```

Then `H=7B`.  Because every off-diagonal 7-by-7 block is a partial
matching, `B` would be a simple 12-regular graph supported on graph
nonedges, and `X` would be a seven-sheet graph cover of `B`.

But transposing the equitable identity gives `Y=B F^T`.  Equation (9) then
forces

```text
B A=2 bar(A).                                        (14)
```

The adjacency matrix `A` is invertible, with eigenvalues `14,3,-4`, so the
solution is unique:

```text
B=2 bar(A) A^{-1}=(J-A-13I)/6.                       (15)
```

It has diagonal `-2` and entry `1/6` on every graph nonedge.  This is not an
adjacency matrix.  Thus the equitable/cover endpoint subcase is excluded.

This is only a subcase exclusion: `H=bar(A)`, one `X` edge in every nonedge
cell-pair, is the opposite extreme and is not equitable.  In particular,
even a hypothetical proof of `H_rs>=1` for every graph nonedge would give
`H=bar(A)` by the average-one identity, not the equitable relation `H=7B`;
the cover contradiction above would not by itself exclude that case.

## 6. A strict quantitative nonequitability bound

Let

```text
P_F=FF^T/7,
R=Y(I-P_F).
```

Since `YF=H` and every row of `Y` has norm squared 84,

```text
R R^T=YY^T-H^2/7,
||R||_F^2=7128-4ell/7.                               (16)
```

Orthogonalize the ordinary edge-incidence columns against the `F`-space:

```text
C_perp=(I-P_F)C^T.
```

Using (2),

```text
C_perp^T C_perp=14I+A-A^2/7.                         (17)
```

Its eigenvalues on the `14,3,-4` eigenspaces of `A` are respectively

```text
0, 110/7, 54/7.                                      (18)
```

Equations (9) and `YF=H` give

```text
R C_perp=2bar(A)-HA/7.                               (19)
```

On `E_3`, the fixed Bose--Mesner part of (19) is `(-44/7)E_3` and the
deviation is `-(3/7)Delta E_3`.  On `E_-4`, they are `(54/7)E_-4` and
`(4/7)Delta E_-4`.  The cross terms vanish by (11).  Least-squares
projection onto `col(C_perp)` therefore proves

```text
7128-4ell/7
 >= 2376/5 +(9/770)delta_3 +(8/189)delta_-4
  = 2376/5 +(18/385)ell +(91/2970)delta_-4.           (20)
```

Since `delta_-4>=0`, (20) gives

```text
ell <= floor(182952/17)=10761.                        (21)
```

The partition-only maximum is 12,474, attained by twelve size-seven blocks
at every vertex.  Thus (21) is a genuine strict strengthening.  It also
gives

```text
||XF-FH/7||_F^2 >= 6852/7
```

and, by Cauchy, at least 674 of the 4,158 nonedge point-pairs have
`H_rs>0`.

## 7. Adding the full triangle-cell space

The cross matrix `W=F^T XQ` has a useful entrywise interpretation.  An
`X` edge with source unmatched point `r` can meet only a target triangle
anticomplete to `r`.  Hence

```text
W_rU=0 if r is in U or adjacent to a point of U,
W_rU in {0,1,2,3} otherwise,
W1=84*1,  1^T W=36*1^T.                              (22)
```

Define

```text
C8=sum_{r,U} binom(W_rU,2).
```

Then

```text
||W||_F^2=8316+2C8.                                  (23)
```

The motif counted by `C8` has exactly eight vertices: two distinct source
triangles meet at `r`, and both are in the `N3` relation with the same target
triangle, using distinct unmatched target flags.  Its unique unmarked class
has

```text
13 edges,
degree sequence (4,4,3,3,3,3,3,3),
global least mask 5675512,
Wave147 degree-cell mask 44481136,
automorphism order 2,
one marked C8 event per induced copy.                 (24)
```

No order-eight classes were regenerated.  Direct lookup in the frozen
integral `T=0` pseudocount gives

```text
x8[44481136]=2442.                                    (25)
```

To see exactly where `C8` enters the joint Gram, let `P_0` be the orthogonal
projector onto `ker(N)` in triangle-label space.  From (5), the part of `W`
on this kernel is `NK P_0`.  The fixed entry profile of `NK` is

```text
0 on the 7 incident triangles,
2 on the 84 triangles meeting N(r),
W_rU on the 140 anticomplete triangles.
```

Consequently

```text
||NK||_F^2=41580+2C8.                                 (26)
```

Projection onto `row(N)` and (11)--(13) now give the exact residual identity

```text
||NK P_0||_F^2
 =16632/5+2C8-(2/5)ell-(7/30)delta_-4.                (27)
```

The full triangle residual uses

```text
Q^T(I-P_F)Q=3I-N^TN/7.
```

Its `im(N^T)` part is (20), while its `ker(N)` part adds one third of
(27).  Taking traces yields the lower projection

```text
1584-(20/231)ell +(2/3)C8 -(14/297)delta_-4.           (28)
```

Combining (16), (28), and `0<=delta_-4<=4ell` gives the clean necessary
tradeoff

```text
4ell+9C8 <= 74844.                                    (29)
```

The frozen value (25) does not come with an `ell` value, because `ell` is a
higher two-point synchronization absent from that order-eight count vector.
At the purely scalar choice `ell=0`, (29) has large slack:
`9*2442=21978<74844`.  This is a boundary check, not a simultaneous flag
realization.

## 8. Triangle partition, interlacing, and the first missing trace terms

For the triangle cells, the normalized compression is

```text
(Q/sqrt(3))^T X(Q/sqrt(3))=K/3.                       (30)
```

The partition cannot be equitable: every nonzero 3-by-3 block contains
exactly one edge, which cannot have constant integral row degree.  More
quantitatively,

```text
Q^T X^2 Q-K^2/3 >=0,
tr(Q^T X^2 Q-K^2/3)=8316-8316/3=5544.                (31)
```

For the vertex cells the normalized compression is `H/7`.  Thus the spectra
of `H/7` and `K/3` interlace the spectrum of `X`.  Their squared traces are

```text
tr((H/7)^2)=(8316+4ell)/49,
tr((K/3)^2)=924.                                      (32)
```

The two normalized cell spaces are not orthogonal.  The squared principal
cosines are

```text
1                 with multiplicity 1,
10/21             with multiplicity 54,
1/7               with multiplicity 44.              (33)
```

Hence they meet only in the constant vector and together span dimension
`99+231-1=329`.  Equations (20) and (28) are the corresponding exact
least-squares consequences.  Their slack remains positive.

The projector equation does not fix the next triangle-quotient trace.  If
`A_+` is the `M=+1` relation, then `M-4I=A_+-K` and

```text
tr(A_+^3)-3tr(A_+^2K)+3tr(A_+K^2)-tr(K^3)=204204.     (34)
```

The four summands are not individually determined.  In particular,

```text
tr(K^3)=6 tau_K,
```

where `tau_K` counts triples of pairwise-disjoint graph triangles, hence an
order-nine motif.  A `K` triangle need not lift to an `X` triangle: its three
single intercell edges can choose incompatible endpoint flags.  The endpoint
condition `tr(X^3)=0` says exactly that no compatible choice occurs; it does
not force `tau_K=0`.

## 9. Exact boundary

The strongest conclusions of this bounded lane are:

```text
the endpoint flag graph X is 12-regular and triangle-free;
H is the partial-matching quotient fixed by (7);
the equitable/seven-sheet-cover subcase is impossible;
ell<=10761, strictly below the partition-only maximum 12474;
4ell+9C8<=74844;
C8 is the exact order-eight class x8[44481136].
a nonedge zero block H_rs=0 passes the exact Wave205 two-centre local tests.
```

They do not exclude `sum E0=0`.  The earliest unfixed data appear in three
equivalent-looking but distinct places:

1. `c4(X)` in the fourth trace of the 693-vertex flag graph (order at most
   eight);
2. `C8`, the first mixed `F`--`Q` collision (exactly order eight); and
3. the synchronization of those order-eight collisions across two vertex
   cells, measured by `ell` and its module split, or endpoint compatibility
   around a `K` triangle (order nine and higher).

The full projector equation `M^2=21M` controls the signed triangle relation,
but does not close any of these mixed ordinary/Schur products.  A next proof
must couple `C8` to `ell,delta_-4`, or control the endpoint labels around
`K`-triangles.  In particular, ruling out `H_rs=0` requires simultaneous
extension of the overlapping two-centre stars, beyond the exact 28-vertex
`t6_h1` control.  Scalar traces and separate interlacing cannot do this.

## Reproduction

```text
python scratch_theory_e0_zero_triangle_flag_relation.py
python scratch_theory_e0_zero_triangle_flag_relation_audit.py
```

Artifacts:

```text
scratch_theory_e0_zero_triangle_flag_relation.py/.json/.md
scratch_theory_e0_zero_triangle_flag_relation_audit.py/.json
```

No `submission.txt`, graph, endpoint exclusion, or Conway-99 resolution is
claimed.
