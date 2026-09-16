# Solver-free exclusion of the source-724 E71 boundary

Status: `INDEPENDENT_SOURCE724_MULTIBLOCK_TRANSPORT_AUDIT_PASS`.

This note concerns only the frozen E71 macro

```text
source_row_index = 724, key = (724,1,0), Q=2,
labelled coverage = 32,768.
```

It does not enumerate the rest of the E71 frontier.  Starting from the 128
previously retained overlap products, two exact pointwise identities remove
every possible fibre-degree completion.  No SAT solver and no regeneration of
the order-eight assets is used.

## 1. Coarse defect and the transport equation

Let `B` be the adjacency matrix on the 84 outer vertices.  Let `P` be the
`84 by 21` zero-one fibre incidence matrix and put

```text
U=P/2,                    U^T U=I,
C=P^T B P,
A0=U^T B U=C/4,
W=(I-UU^T)BU,
R=8W=4BP-PC.
```

The established defect Gram is

```text
R^T R=4K4,                W^T W=K4/16.                 (1)
```

The rooted SRG equation is

```text
B^2+B=12I+2J-Q_line.                                  (2)
```

Its right side preserves the coarse fibre space.  Taking the off-diagonal
block of (2), and then its coarse block, gives

```text
(I-UU^T)BW=-W(A0+I),
U^T BW=W^T W=K4/16.
```

Consequently every outer vertex must satisfy the exact vector equation

```text
4BR=PK4-R(C+4I).                                      (3)
```

This is stronger than the aggregate Gram (1): it transports each individual
defect row through the still unknown binary blocks of `B`.

For completeness, summing (3) over edges also gives the cubic moment

```text
R^TBR=16G3-4G2 C-4C G2+C^3,
G2=P^T B^2P,
G3=P^T B^3P,
```

where `G2,G3` are fixed by the rooted equations.  On this macro, however, the
independent-block scalar support intervals for that aggregate equation retain
all 26,112 degree/overlap instances.  The pointwise form (3) is essential.

## 2. A residual spectral-projector row equation

Let `L` be the unsigned incidence of the 84 exact-label edges with their 14
root-neighbour labels, and

```text
H=I-L(L^TL)^(-1)L^T.
```

This is the rank-70 cycle-space projector.  The root-label action of `B`
implies that on this space the `-4` spectral projector is

```text
E4=H(3I-B)/7,             diag(E4)=5/14.               (4)
```

Write `Z=C0-C`.  The exact coarse compression and coordinate rows are

```text
U^T E4 U=Z/28,
(E4U)[x,*]=(Z_G-R_x)/56                                  (5)
```

for a vertex `x` in fibre `G`.  Set

```text
s_x=Z_G-R_x,
Pi=(E4U)(U^TE4U)^+(E4U)^T,
G4=112(E4-Pi).
```

Since `Pi` projects onto a subspace of the range of `E4`, `G4/112` is itself
an orthogonal projector.  In particular

```text
G4^2=112G4.                                             (6)
```

For distinct outer vertices define

```text
q_xy = number of common exact root-neighbour labels,
d_xy = number of mate-label incidences,
a_xy = 4-6q_xy-2d_xy-s_x Z^+ s_y,
g_x  = 40-s_x Z^+s_x.
```

Substituting (4)--(5) gives the exact entries

```text
(G4)_xx=g_x,
(G4)_xy=a_xy-16B_xy.                                  (7)
```

The diagonal of (6) is linear in the unknown adjacency bits, because
`B_xy^2=B_xy`.  Expanding (7) yields

```text
sum_{y~x} (8-a_xy)
  = (112g_x-g_x^2-sum_{y!=x}a_xy^2)/32.               (8)
```

Equation (8), not merely positive semidefiniteness, supplies the final cut.
The two-by-two minors

```text
(a_xy-16B_xy)^2 <= g_x g_y                              (9)
```

were also checked.  They remove none of the final 16 instances, and (8)
removes all 16 even when (9) is not used.

The related leverage inequality is

```text
s_x Z^+s_x <= 40.                                      (10)
```

It is important that `s_x=Z_G-R_x`; the cross-block-only expression
`R_x Z^+R_x^T<=40` is invalid.  Nine raw source-724 row patterns fail (10),
but none occurs in the complete Gram-compatible frontier below, so (10)
causes no additional configuration-level reduction here.

## 3. Exact finite template

For a fixed exceptional vertex `x`, each of its ten disjoint target fibres
contributes one row of a binary `4 by 4` matrix with prescribed ordered row and
column margins.  All such matrices are enumerated.  An option contributes

```text
( sum of the three pivot coordinates of R_y over y~x,
  sum of 8-a_xy over y~x ).                             (11)
```

The first three coordinates enforce (3), and the last enforces (8).  Taking
the exact Minkowski sum of the ten finite option sets is a relaxation: blocks
used at different source vertices are not required to agree.  Therefore
failure of membership is a sound exclusion.

Ordinary-fibre row order need not be separately enumerated.  Permuting its
four rows simultaneously permutes the residual vectors and the corresponding
column margins.  Column relabelling is a bijection on the `4 by 4` binary
matrices, so the option set (11) is unchanged.  Exceptional rows remain fully
ordered throughout.

## 4. Complete source-724 census

The 128 frozen overlap products split into two fixed-degree signatures of 64
products each.  The audit independently reconstructs:

```text
ordinary row-multiset product:                         34,992
complete Gram-compatible degree multisets:                 408
overlap x degree-multiset instances:                    26,112
```

For each of the 408 degree multisets it also verifies the full 21-coordinate
identity `R^TR=4K4`, not only its three pivot coordinates.  The exact outcome
is

```text
                                           enter       fail       pass
pointwise transport (3)                   26,112     26,096         16
projector row norm (8), no pair filter        16         16          0
```

Both signatures contribute eight of the intermediate 16 survivors.  For the
first retained control the transport candidates have local overlap indices
`24,26,28,30`; equation (8) already fails at outer vertex 12.  Its required
four-coordinate free sum is

```text
(-11,16,4,50/3),
```

while the exact finite reachable set has 39 elements and contains no such
vector.

Thus the entire macro `(724,1,0)` and its labelled coverage `32,768` are
excluded.  This is a scoped E71 result, not an exclusion of E0=71 or a
construction/nonexistence proof for the Conway graph.

## 5. Artifacts and independent audit

```text
scratch_theory_e71_source724_multiblock_transport.py
scratch_theory_e71_source724_multiblock_transport.json
scratch_theory_e71_source724_multiblock_transport_audit.py
scratch_theory_e71_source724_multiblock_transport_audit.json
```

The audit does not import the producer.  It independently decodes the 128
frozen products, rebuilds all 34,992 ordinary products and all 408 complete
degree multisets, checks the configuration-record digest, replays all 26,112
transport decisions, and replays the 16 rational projector equations.  It
also reconstructs the exact root-label Gram inverse and checks all 3,486
off-diagonal entries in (4), all 1,764 entries of (5), and the scale factors
`28,56,112`.

No `submission.txt` was written.
