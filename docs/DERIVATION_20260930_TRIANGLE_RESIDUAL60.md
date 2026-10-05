# Candidate exact residual60 completion conditions

This is conditional preparation, CANDIDATE pending independent review. No
validated36 by60 factor is assumed available, and no residual search is run.
No nontrivial target automorphism or universal containment of the selected
core is assumed. These block identities overlap prior triangle-incidence
work; no novelty claim is made.

## Fixed input and exact equivalence

Let S=J3-I3. Let R be the36 by3 cell-incidence matrix, one1 per row and
twelve1s per column. Let C be the symmetric cubic36 adjacency with a
perfect matching in each cell and between each pair of cells. The three
internal matchings and cross permutation may be arbitrary. In particular,

    R^T R=12I3, R R^T=diag(J12,J12,J12), R^T C=J_(3,36).

Suppose the raw binary36 by60 matrix F has been independently validated:

    R^T F=2J_(3,60),
    F F^T=12I36-C-C^2+2J36-R R^T.                 (F)

The first equation gives two neighbors per cell, six in each column. The
diagonal of the second gives ten1s in each row. No binary factorization
claim follows merely from knowing the right-hand Gram is positive.

For a symmetric binary zero-diagonal60 by60 D, assemble

    A = [ S    R^T    0  ]
        [ R     C    F  ].
        [ 0    F^T   D  ]

Then A satisfies A^2=12I99-A+2J99 if and only if

    F D =2J_(36,60)-F-CF,                         (L)
    D^2+F^T F=12I60-D+2J60.                       (Q)

This is sufficiency as well as necessity. Every block of the target
identity is accounted for:

| Block | Equality |
|---|---|
| TT | S^2+R^TR=13I3+J3=12I3-S+2J3 |
| TX | SR^T+R^TC=2J-R^T |
| TY | R^TF=2J by(F) |
| XX | RR^T+C^2+FF^T=12I-C+2J by(F) |
| XY | CF+FD=2J-F by(L) |
| YY | F^TF+D^2=12I-D+2J by(Q) |

The other three blocks are transposes. The diagonal of(Q), using the six1s
per F column and binary D, gives6+deg_D(y)=14. Therefore D has degree8;
one may impose this redundantly for clarity and propagation. Dropping(Q)
or replacing it by only degree8 would destroy the sufficiency statement.

## Cheap exact rejection tests for a future factor

Compute H=2J-F-CF and T=F^TF, exactly. Equation(L) has a nonnegative left
side, so any H entry below zero rejects the supplied factor. For distinct
y,z, equation(Q) says

    T_yz+|N_D(y) intersection N_D(z)|=2-D_yz.

Thus T_yz>2 rejects the factor; T_yz=2 forces D_yz=0 and forbids a common
D neighbor. An allowed edge y--z must satisfy all three conditions

    T_yz<=1, F[:,z]<=H[:,y], F[:,y]<=H[:,z],

where inequalities are entrywise. The two column inequalities are necessary
for both symmetric entries of(L). Construct this undirected allowed-edge
graph. A vertex of allowed degree below8, or a coordinate whose entire
allowed-neighbor capacity falls below the corresponding H entry, gives
a cheap exact obstruction.

The next stronger individual-row question is finite: choose a set S_y
of eight allowed neighbors, with

    sum_(z in S_y) F[:,z]=H[:,y],
    T_zw<=1 for all distinct z,w in S_y.

The last condition prevents two selected vertices from having a forbidden
common D neighbor y. This uses both the linear mixed equations and the
currently known pair caps. A complete empty-row proof excludes this factor.
A surviving row does not establish simultaneous symmetry, compatibility of
different rows, or the remaining quadratic equations. Any expensive exact
domain enumeration needs a fresh frozen protocol and complete certificates.

Some aggregate checks are automatic and should not be mistaken for progress:
every H column has sum48, each cell contributes16 to that sum, and every H
row has sum80. These follow from the factor marginals and cubic equitable
core. They merely agree with eight selected columns of weight6, two per
cell, and ten factor incidences per row.

## Calibration and execution scope

The source checks the literal full matrix residual against the six expanded
blocks on four arbitrary binary block controls, including the actual99
dimensions. These controls need not be target graphs: they test every
coefficient, sign and transpose exactly. A known SRG(9,4,1,2) supplies a
valid triangle-partition control; its residual cell is empty, so this is
explicitly not an example of a target-sized nonempty factor.

For the local-star predicate, a different bipartition of the same rook9
graph has six known vertices and a nonempty three-vertex residual triangle.
All12 possible individual star subsets are compared with literal adjacency
pair caps and exact mixed counts, including the three valid degree2 stars.
This calibrates the generic local formulas, not existence of a36 by60 factor.
Corrupted graph edges, mixed-block signs, capacities and co-neighbor
restrictions must be rejected. All arithmetic is integer; no numerical
threshold, SAT call or search is used.

The source exposes `analyze_factor(F)` for the currently selected fixed
shift6 core. It first validates all binary factor prerequisites, then returns
the exact cheap screen. A false rejection flag means only that those cheap
tests passed. It must not be promoted to a target feasibility certificate.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_triangle_residual60.py --out acceleration/results/20260930_triangle_residual60
```
