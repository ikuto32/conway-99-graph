# The `E0(r)=0` rooted hypergraph layer

Status: `E0_ZERO_HYPERGRAPH_AUDIT_PASS`.

This is a clean-room necessary-condition audit.  It uses the independently
verified Wave65 identities but does not import or rerun its discovery code.
No graph, endpoint exclusion, or Conway-99 resolution is claimed.

## What `E0(r)=0` newly removes

The 84 residual points are the four signed versions of each of the 21 edges
of `K7`.  Within a fibre there are four side pairs sharing one exact symbol
and two complementary diagonals.  `E0(r)=0` makes all six pairs nonedges.
For the Wave65 split `B=T+D`, this removes 84 possible same-fibre `T` sides
and the 42 possible same-fibre `D` diagonals.

For a residual point `x` and the mate of either one of its two exact support
labels, `mu=2` leaves exactly one outer common neighbour after the original
support label.  The same-fibre prohibition forces this neighbour into a
different fibre.  Thus every point has exactly one overlapping-support `D`
neighbour through each support group.  Consequently `D` splits into 84
overlapping-support and 336 disjoint-support edges.  Each support fibre lies
in 20 distinct blocks, and relative to each of the seven root groups the 140
blocks have occupancy distribution

```text
number of incident supports in block:   0   1   2
number of blocks:                       32  96  12.
```

More sharply, for every support fibre `e` and each endpoint group `g` of
`e`, exactly four selected blocks containing `e` contain a second support
through `g`.  These are 42 separate support-port equalities, obtained by
summing the four signed point/group degree-one equations for `U`.

A `D` block is a triple of pairwise exact-symbol-disjoint points.  Of 35,560
such labelled triples, exactly 1,680 use a repeated support: one of the 42
diagonals followed by a point on one of ten disjoint supports, with four sign
choices.  They are all forbidden.  The remaining 33,880 triples have three
distinct supports, with catalogue

```text
3K2       6,720
P3+K2    20,160
P4        6,720
C3          280
```

If the selected 140 blocks have shape counts `n0,n1,n2,n3` in this order,

```text
n0+n1+n2+n3 = 140,
n1+2n2+3n3 = 84,
n1+n3 is even.
```

The second equation counts the 84 selected `D` edges whose supports meet.
For a `C3` support block, the product of the three within-fibre product signs
is necessarily `-1`; the script checks all 280 labelled cases.  For each of
the three nontrivial fibre characters, the number of selected blocks with
negative column-product is even.  For character `(1,1)` this says that
`n_C3` plus the negative-product non-`C3` count is even.

## The opposite-edge product supplies a second 2-factor

Let `C` be unsigned vertex-edge incidence, `R_tm` mark the unique triangle
mate of each graph edge, and `J_e` be the opposite-edge graph.  (`R_tm` is
not Wave65's 140-block graph `R`.)  Direct entrywise counting gives

```text
C J_e = A C-C-2R_tm,
C R_tm^T=A,                 R_tm R_tm^T=7I,
C J_e R_tm^T=2(J_99-I-A).
```

Therefore row `r` of `R_tm J_e`, viewed as weights on residual edges, has
weighted degree two at each of the 84 outer points and zero elsewhere.  Its
local weights are 1 on a same-fibre side, 2 on a same-fibre diagonal, 1 on a
distinct-fibre exact-disjoint pair with one common support group, and 0 on
the other pair types.  At `E0(r)=0` only the third type survives, with weight
one, so it is a binary 2-factor

```text
U = D restricted to overlapping group supports.
```

This is not Wave65's `T`: a `T` edge has equal signs at its shared group and
`Q=1`, while a `U` edge has opposite signs and `Q=0`.  Thus `T` and `U` are
edge-disjoint.  For each root group `g`, `T_g` is two six-edge matchings
inside the two sign classes and `U_g` is a twelve-edge matching between the
classes.  Every component of `T_g union U_g` is consequently an alternating
cycle of length divisible by four.  Its possible cycle signatures are four
times the 11 partitions of six, and

```text
rank_R(T_g+U_g)=24-2c_g,
```

where `c_g` is the number of cycles; in particular every such local matrix
is singular.  In the target, `lambda=1` also prevents any `D`-triangle made
from three different hyperedges.  Inside one selected `D` block the number
of `U` edges is `0,1,2,3` for the four shapes above, giving additionally

```text
tr(U^3)=6 n_C3,
tr(U^2 D)=2 n_P4+6 n_C3,
tr(U^2(D-U))=2 n_P4.
```

## New 21-fibre Fourier Gram system

Let `P10,P01,P11` flip the first, second, or both signs in every fibre, put
`L_delta=Z^T P_delta Z`, and put `A=R+3I=Z^T Z`.  Because no block repeats a
fibre, the four unnormalised fibre-character incidence matrices `W_chi` are
21 by 140 with entries in `{0,+1,-1}`.  Exact Hadamard orthogonality gives

```text
G00 = A+L10+L01+L11,
G10 = A-L10+L01-L11,
G01 = A+L10-L01-L11,
G11 = A-L10-L01+L11,

G00+G10+G01+G11 = 4(R+3I).
```

Every `G_chi=W_chi^T W_chi` is PSD, has trace 420 and rank at most 21;
therefore every 22 by 22 minor vanishes.  Each `L_delta` is symmetric,
nonnegative integral, hollow, and 15-regular.  The `G_chi` row sums are
respectively `60,0,0,0`.  In particular the weighted (not necessarily
simple) support-overlap block graph

```text
R_support=G00-3I=R+L10+L01+L11
```

is 57-regular and has eigenvalue `-3` with multiplicity at least 119.
Modulo 3 its rank is at most 20.  There is also a separate characteristic-two
constraint on the 21 by 21 fibre row-Grams

```text
H_chi=W_chi W_chi^T:    rank_F2(H_chi)<=20.
```

Indeed all four signed incidences reduce to the same matrix modulo 2; its row
weights are 20 and its column weights are 3, so `H_chi 1=0`.  (This does not
assert the same rank bound for the 140 by 140 column-Grams in characteristic
two.)  This four-Gram decomposition, its entry alphabet, and the large
kernels are information added by the same-fibre prohibition; Wave65's single
`Z^T Z` Gram does not record them.

## Diagonal-pair collision identity coupling `Z` and `T`

For all three fibre matchings, `T^2[x,Px]=0`.  For a side pair, every possible
common `T` candidate would use the same exact-symbol perfect matching twice;
for a diagonal pair the only two candidates are forbidden same-fibre sides.
The script exhausts all 42 pairs of each kind.

Let `L_delta=Z^T P_delta Z` and
`M_delta=tr(Z^T P_delta T Z)=tr(T D P_delta)`.  Taking the matching trace of
`B^2+B=10I+2J-Q` gives the new exact necessities

```text
tr(R L10)+2 M10 = 84,
tr(R L01)+2 M01 = 84,
tr(R L11)+2 M11 = 168.
```

For the 42 diagonal pairs define `A` as their total number of common
`D`-neighbours and `M` as their total mixed `T/D` common-neighbours.  Then

```text
A = tr(R L11)/2,
M = tr(Z^T P11 T Z),
A+M = 84.
```

Equivalently, between two diagonal-pair quotient vertices of disjoint
supports let `p,q <= 2` count the two orientation classes of selected `D`
edges.  Then `A=sum p*q`, so `sum p*q<=84`.  This is an entrywise collision
budget coupling the hypergraph blocks to `T`, not a scalar consequence of
`D+5I=ZZ^T` alone.

## Boundary

The original embedded 140-block cyclic support control has 56 `3K2` and 84
`P3+K2` blocks, support degree 20, rational rank 21, and the forced
`(32,96,12)` group occupancy.  It does *not* satisfy the new oriented-port
rows: its 42 values are `0,1,2,5,6,10`, each seven times.  Thus the new
2-factor bridge genuinely distinguishes it from a sign-liftable control.

A second bounded search selected 20 of all 170 cyclic support orbits, making
all 42 port values four, then searched the 6,272 compatible signed blocks on
that fixed skeleton.  It found a witness, which this clean-room script replays
without trusting the solver status:

```text
blocks / unique D edges / U edges:  140 / 420 / 84
point-degree rows:                  {5: 84}
point/group U exact-one rows:       168
U cycle lengths:                    [3, 3, 78]
```

This proves that degree five, point-level linearity, and all 168 `U`
exact-one rows are jointly feasible; hence they yield no contradiction.
The control intentionally omitted `T` and the full rooted equation.  As a
diagnostic, it has 87 Berge
triangles outside its selected blocks (including
2 `U`-triangles) and
261 aggregate extra local
block-graph edges, so `R` is not locally `3K4`.  The first unresolved layer
is therefore the stronger compatibility of the four Fourier Grams, both
2-factors, the three matching-trace identities, the local `3K4` condition,
and Wave65's entrywise equation.  No Conway-99 conclusion is claimed.
