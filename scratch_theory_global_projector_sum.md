# Global rank-14 fibre-projector sum: exact clean-room audit

Status: `GLOBAL_PROJECTOR_SUM_EXACT_AUDIT_PASS_NO_POSITIVE_E0_BOUND`.

## Result

The global rank-14 projector identity is exact:

```text
S := sum_r P_r = H/4-7I-(11/12)(J-I-A) >= 0.
```

Its primitive block traces, square trace, and all integer collision and
`E0` second-moment consequences derived below were checked with exact
rational arithmetic.  They do not imply either a pointwise lower bound
`E0(r)>=1` or a positive average lower bound on
`T=sum_r E0(r)`.

The obstruction is explicit.  At `T=0`,

```text
H0 = 84I+3(J-I-A)
```

passes every matrix-, trace-, integrality-, and second-moment condition in
this audit.  This is a scoped boundary control, not a claimed binary
`2079 x 99` incidence factorization and not a graph construction.

No order-eight class was regenerated.

## 1. The two incidence matrices

For a root `r`, its 84 outer vertices are partitioned into 21 four-point
fibres indexed by the edges of `K7`.  Let `M` have one row for each rooted
fibre and one column for each graph vertex.  Then

```text
shape(M)=2079 x 99,       H=M^T M,
H_xx=84,                 H 1=336 1,
sum_(x<y) H_xy=12474,
sum_(x~y) H_xy=T=sum_r E0(r).
```

Let `W` be the `99 x 693` root-group incidence matrix.  A column is indexed
by an oriented triangle `(r,t)`, where `r` is one of the three vertices of
`t`.  If `c_t` is the triangle indicator, its group column is

```text
w_(r,t)=(A-I)c_t-(A+I)e_r.
```

The vertex-triangle incidence matrix `C` satisfies `CC^T=7I+A`.  Summing
the oriented-column outer products gives, before using the SRG equation,

```text
WW^T = 3(A-I)(7I+A)(A-I)
       -(A-I)(7I+A)(A+I)
       -(A+I)(7I+A)(A-I)
       +7(A+I)^2
     = A^3+8A^2-23A+42I.
```

Since `A^2=12I-A+2J`, this reduces exactly to

```text
WW^T=126I-18A+42J.                                    (1)
```

Its diagonal, edge, and nonedge entries are `168,24,42`; its eigenvalues
on the constant, `+3`, and `-4` spaces are `4032,72,198`.

## 2. The rank-14 support projector

Let `R` be the unsigned `7 x 21` vertex-edge incidence of `K7`.  Then

```text
RR^T=5I+J,       (RR^T)^(-1)=I/5-J/60,
Q=I-R^T(RR^T)^(-1)R.
```

Direct `Fraction` multiplication verifies `Q^2=Q`, `rank(Q)=14`, and
`Q 1=0`.  Its entries for two `K7` edges are

```text
equal       2/3,
overlap    -2/15,
disjoint    1/15.
```

Lifting a support coordinate to its four fibre vertices divides these
entries by four.  Thus each rooted projector `P_r` has entries

```text
same fibre       1/6,
overlap support -1/30,
disjoint support 1/60.                                (2)
```

## 3. Direct derivation of the summed projector

For two distinct vertices put `h=H_xy`.  They have `h` common outer roots
at which their supports are equal.  Equation (1) counts shared support
groups, while the SRG parameters give 72 eligible roots for an edge and 71
for a nonedge.  Hence the exact root counts are

| pair | equal | overlap | disjoint |
|---|---:|---:|---:|
| `x~y` | `h` | `24-2h` | `48+h` |
| `x` nonadjacent `y` | `h` | `42-2h` | `29+h` |

Nonnegativity gives the pointwise codegree caps

```text
H_xy<=12 on edges,       H_xy<=21 on nonedges.          (3)
```

Substitution of (2) gives

```text
S_xx=14,
S_xy=h/4                         if x~y,
S_xy=h/4-11/12                   otherwise.
```

This proves entry by entry

```text
S=sum_r P_r=H/4-7I-(11/12)(J-I-A).                     (4)
```

It also proves `S 1=0`, `tr(S)=1386`, and

```text
0<=S<=84I.                                               (5)
```

For (5), `P_r` is dominated by the coordinate projector onto the 84 outer
vertices at `r`; every vertex is outer for exactly 84 roots.

## 4. Pointwise `E0` and primitive traces

Fix a root and write `e=E0(r)`.  Its outer graph is 12-regular, hence has
504 edges.  Each of the seven root groups contains two 12-point sides.
The two sides induce six matching edges each, and the `mu=2` equation gives
a 12-edge cross matching.  Therefore each group contains 24 outer edges
and the total shared-support incidence is 168.  The edge counts by support
relation are consequently

```text
equal=e,       overlap=168-2e,       disjoint=336+e.     (6)
```

Using (2) in `tr(AP_r)` yields

```text
tr(AP_r)=e/2.                                            (7)
```

For

```text
E+=(A+4I-2J/11)/7,       rank(E+)=54,
E-=(-A+3I+J/9)/7,        rank(E-)=44,
```

and `P_r 1=0`, (7) gives the exact pointwise block traces

```text
tr(E+ P_r)=8+e/14,
tr(E- P_r)=6-e/14.                                      (8)
```

Positivity of the compressions recovers only `0<=e<=84`.  Summing (8)
over the roots gives

```text
tr(E+ S)=792+T/14,
tr(E- S)=594-T/14.                                      (9)
```

At `T=0`, every nonnegative `E0(r)` is zero and the two local traces are
still the admissible positive values `8` and `6`.

## 5. Square trace, pinching, and integer collisions

Define the fibre-block collision count

```text
K=sum_(x<y) binom(H_xy,2).
```

Because the off-diagonal entries of `H` sum to 12474,

```text
tr(H^2)=723492+4K.
```

Expanding (4), with
`tr(H(J-I-A))=2(12474-T)`, gives

```text
tr(S^2)=K/4+33033/2+11T/12.                             (10)
```

Pinching to the two primitive spaces and applying trace Cauchy gives

```text
tr(S^2) >= (792+T/14)^2/54+(594-T/14)^2/44,

K >= 12474-3T+T^2/1188.                                (11)
```

Since every `H_xy` is an integer, convex distribution over the 693 edges
and 4158 nonedges gives the stronger piecewise-linear bound

```text
K >= cmin(T,693)+cmin(12474-T,4158),                    (12)
```

where, for `S=mq+r`,
`cmin(S,m)=m*binom(q,2)+rq`.  Exhaustion of all 8317 integral values of
`T` verifies that (12) always dominates (11), by at most 594.  Its absolute
minimum is

```text
K>=10395,
```

with equality in the scalar bound for every `1386<=T<=2079`.  It supplies
no positive lower bound on `T`.

## 6. The `sum E0(r)^2` lane

Writing `E2=sum_r E0(r)^2`, integrality and `0<=E0(r)<=84` give

```text
sqmin(T,99) <= E2
 <= 84^2 floor(T/84)+(T mod 84)^2
 <= 84T.                                                (13)
```

Equation (8) retains `E2` exactly in the squared local traces:

```text
sum_r tr(E+P_r)^2 =6336+8T/7+E2/196,
sum_r tr(E-P_r)^2 =3564-6T/7+E2/196.                    (14)
```

Each primitive compression of a rank-14 projector is a rank-at-most-14
positive contraction.  Applying
`trace(B)^2/14<=trace(B^2)<=trace(B)` to either sign gives

```text
E2<=931392-28T.                                         (15)
```

But

```text
84T <= 931392-28T       for every 0<=T<=8316,
```

so (15) is redundant throughout the full range.  At `T=0`, (13) forces
`E2=0` and all compression inequalities remain valid.

There is also a pointwise row consequence.  If
`t_x=sum_(y~x)H_xy`, then the edge and nonedge row sums of `S` are
`t_x/4` and `-14-t_x/4`.  Relation-wise Cauchy yields

```text
(S^2)_xx >= 196+t_x^2/224+(14+t_x/4)^2/84.              (16)
```

At the zero boundary it is attained with value `595/3`, so it likewise
does not force a positive root defect.

## 7. Exact zero boundary

For

```text
H0=84I+3(J-I-A),
S0=14I-(J-I-A)/6,
```

the eigenvalues on the constant, `+3`, and `-4` eigenspaces are

```text
H0: 336, 72, 93,
S0:   0, 44/3, 27/2.
```

Thus both matrices are positive semidefinite, `S0<=84I`, and

```text
tr(S0)=1386,       tr(S0^2)=19635,
K=4158*binom(3,2)=12474,       E2=0.
```

It attains equality in both (11) and (12) at `T=0`.  Its support-relation
counts are nonnegative integers:

```text
edge pair:       equal/overlap/disjoint = 0/24/48,
nonedge pair:    equal/overlap/disjoint = 3/36/32,
root outer edges when E0(r)=0:           0/168/336.
```

Modulo two, `H0` is the complement adjacency matrix, hence symmetric
alternating with zero row sum and even rank at most 98.  Therefore parity
does not remove the boundary either.

What remains unproved is precisely the graph-valued factorization: this
audit does not construct a binary `M` whose 2079 rows split into the 99
required fibre partitions.  A new condition retaining that root assignment
is needed to exclude `H0`.

## 8. Reproducibility

The standard-library exact calculation is in
`scratch_theory_global_projector_sum.py` with machine-readable output
`scratch_theory_global_projector_sum.json`.  A separately implemented
replay, which imports no function from the primary checker, is in
`scratch_theory_global_projector_sum_audit.py` and checks all 8317 integral
values of `T`.

```powershell
& 'C:\Users\ikuto\.local\bin\python3.12.exe' -B `
  scratch_theory_global_projector_sum.py
& 'C:\Users\ikuto\.local\bin\python3.12.exe' -B `
  scratch_theory_global_projector_sum_audit.py
```

The minimum observed free physical memory was above 65%, versus the 18%
required gate.
