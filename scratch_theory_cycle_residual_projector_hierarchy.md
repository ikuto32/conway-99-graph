# Two residual cycle-projector identities

Status: exact coefficient audit passed.  This is a reusable necessary
condition, not yet an `E0` lower bound.

At a fixed root, label the 84 outer vertices by the edges of
`K14-7K2`.  Let `H` be the rank-70 exact-label cycle projector, `B` the
outer adjacency matrix, `U` normalized coarse-fibre incidence, `K` the
rank-14 coarse cycle projector, `Z=C0-C`, and `R=4BP-PC=8W`.

The cycle-space spectral projectors are

```text
E4=H(3I-B)/7,                 E3=H(4I+B)/7.
```

Their coordinate diagonals are `5/14` and `10/21`.  Their coarse blocks
and coordinate rows are

```text
U^T E4 U = Z/28,              (E4 U)_x=(Z_G-r_x)/56,
U^T E3 U = K-Z/28,            (E3 U)_x=(28K_G-Z_G+r_x)/56.
```

Put

```text
s_x=Z_G-r_x,                  D=28K-Z,
t_x=28K_G-Z_G+r_x.
```

Subtract from each spectral projector the projector onto the range of its
coarse columns and scale:

```text
G4=112(E4-proj range(E4U)),
G3=1680(E3-proj range(E3U)).
```

Both are scaled orthogonal projectors and their ranges are orthogonal.  For
distinct exact labels `x,y`, let `q_xy` count shared endpoints and `d_xy`
count mate crossings.  Then

```text
g_x=(G4)_xx=40-s_x Z^+ s_x,
a_xy=4-6q_xy-2d_xy-s_x Z^+s_y,
(G4)_xy=a_xy-16B_xy,

h_x=(G3)_xx=800-15t_x D^+t_x,
b_xy=-32-64q_xy+16d_xy-15t_x D^+t_y,
(G3)_xy=b_xy+240B_xy.
```

The coefficient `1680` is forced by the denominator 120 in `H`.  Indeed,
for `x!=y`,

```text
H_xy=(2-11q_xy-d_xy)/120,
112(E4)_xy=4-6q_xy-2d_xy-16B_xy,
1680(E3)_xy=-32-64q_xy+16d_xy+240B_xy.
```

Because `B_xy` is binary, the diagonal parts of
`G4^2=112G4`, `G3^2=1680G3`, and `G4G3=0` are linear weighted-degree
equations:

```text
sum_{y~x}(8-a_xy)
  =(112g_x-g_x^2-sum_{y!=x}a_xy^2)/32,

sum_{y~x}(b_xy+120)
  =(1680h_x-h_x^2-sum_{y!=x}b_xy^2)/480,

sum_{y~x}(240a_xy-16b_xy-3840)
  =-g_xh_x-sum_{y!=x}a_xy b_xy.
```

Thus the +3 residual and cross-orthogonality equations can be added as two
exact scalar coordinates to a per-vertex block-reachability test.  Their
*independence is not asserted*: since `E3=H-E4` and `HE4=E4`, one has

```text
E3^2-E3=E4^2-E4,              E4E3=-(E4^2-E4).
```

Consequently, after the coarse Gram block and the strong cross-block
transport identity have both been imposed, the three residual diagonal
equations may reduce to the same remaining block equation.  A
configuration-level audit must test that dependency before crediting either
new coordinate as an additional exclusion.  In either form, no new
order-eight catalogue or complete lower-`E0` local-completion search is
required.

The standard-library checker
`scratch_theory_cycle_residual_projector_hierarchy.py` reconstructs the
84-label cycle projector from
`(L^TL)^(-1)=11I/120-J/240+mate/120`, verifies its idempotence and rank,
checks every exact-label relation coefficient, and checks all three binary
linearizations with exact rational arithmetic.  The machine-readable output
is `scratch_theory_cycle_residual_projector_hierarchy.json`.
The separate checker
`scratch_theory_cycle_residual_projector_hierarchy_audit.py` imports no
producer code, reconstructs all 3,486 exact-label pairs entrywise, and
reports
`INDEPENDENT_CYCLE_RESIDUAL_PROJECTOR_COEFFICIENT_AUDIT_PASS`.

Claim boundary: these identities are necessary for a putative Conway graph.
No `E0=71` macro or lower layer is declared excluded until a complete
configuration-level application and an independent coverage audit pass.
