# Minimal marked mate/doubled-status lift

Status: `MINIMAL_ORDER9_MATE_DOUBLED_STATUS_LIFT_INDEPENDENT_AUDIT_PASS`.

The producer is `scratch_theory_minimal_order9_mate_lift.py`; the separate
edge-set replay is `scratch_theory_minimal_order9_mate_lift_audit.py`.  The
lift reads the frozen Wave147/148 resources and does **not** regenerate the
916 order-eight classes, the 2,414 coefficient matrices, or a general
order-nine census.

## 1. Minimal rooted state

Fix a target edge `e`, let `u` be its unique triangle mate, and put

```text
m_r = 1[r~u],       y_r = Yhat[r,e],
s_r = m_r y_r + binom(y_r,2).
```

The proved support restrictions leave exactly three nonzero states:

| state | `(m,y,s)` | source occurrences | meaning |
|---|---:|---:|---|
| `G` | `(0,1,0)` | 1 | one good `X` flag |
| `D` | `(0,2,1)` | 2 | doubled `X`, hence a diagonal fibre edge |
| `P` | `(1,1,1)` | 1 | one prism flag, hence a side fibre edge |

Thus the state is equivalent to `(m,y)` on the nonzero domain and is a
necessary and sufficient *local status* for evaluating `s`.  If `L_ab`
counts ordered **source-occurrence** pairs with physical states `a,b`, one
physical root pair contributes `y_a y_b` occurrences.  Consequently

```text
K_rel = (1/2) sum_(a,b) [s_a s_b/(y_a y_b)] L_rel,ab.   (1)
```

The factor `1/2` changes ordered roots to unordered roots.  The only nonzero
weights inside the sum are

```text
DD: 1/4,       DP and PD: 1/2,       PP: 1.
```

Likewise the old bad-mate correction is exactly one half of the sum of all
`L_ab` with at least one `P` coordinate.  Hence these tags track both the
mate correction and the desired selected collision without ambiguity.

## 2. Frozen order-eight deletion rows

Only nine of the 916 frozen order-eight columns have a nonzero two-root
shadow coefficient.  On a canonical `K8`, mark

```text
(left root, right root, left source triangle,
 right source triangle, target edge).
```

The 20 ordered marks split into 11 automorphism orbits.  For a marked orbit
`i` of size `o_i`, introduce the nine state cells `L_i,ab` and impose

```text
sum_(a,b) L_i,ab = o_i x8[K].                            (2)
```

This equation is invariant under relabelling: an induced copy of `K` has
exactly `o_i` marks in that intrinsic marked-isomorphism orbit.  Adding the
unique mate gives four visible mate-bit extensions.  Every extension was
checked against the induced adjacent/nonadjacent common-neighbour upper
bounds and checked to delete back to the exact frozen mask.

The complete compact row table is:

| row | frozen mask | orbit size | pair-upper-forbidden states | all-G H9 equation |
|---|---:|---:|---|---|
| `E019O0` | 5691760 | 2 | none | `2x=2h3` |
| `E515O0` | 127242964 | 4 | none | `4x=2h8` |
| `E561O0` | 144594160 | 2 | none | `2x=2h6` |
| `N057O0` | 15424580 | 1 | `GP,DP,PP` | `x=h2` |
| `N057O1` | 15424580 | 1 | `PG,PD,PP` | `x=h2` |
| `N060O0` | 15436356 | 2 | none | `2x=2h0` |
| `N109O0` | 44489072 | 2 | `GP,DP,PG,PD,PP` | `2x=2h7` |
| `N442O0` | 110787152 | 1 | `GP,DP,PP` | `x=2h5` |
| `N442O1` | 110787152 | 1 | `PG,PD,PP` | `x=2h5` |
| `N525O0` | 127315016 | 2 | none | `2x=6h4` |
| `N593O0` | 149654084 | 2 | none | `2x=2h1` |

Here `E/N` means adjacent/nonadjacent ordered roots, and `h0,...,h8` are the
nine already-audited all-`X` H9 types.  The complete representatives,
canonical mark keys, exact masks, violations, and frozen column indices are
in the JSON artifact.

The dimensions are small:

```text
11 deletion rows,
99 orbit-state cells before pair-upper, 82 after it,
180 marked-slot state cells before pair-upper, 158 after it,
19 visible degree-cell H9 masks over all allowed mate-bit extensions.
```

All 17 forbidden orbit cells (22 with marked-orbit multiplicity) occur on
the nonadjacent-root side.  In particular, `GG` is allowed in every row.

## 3. Exact all-G closure at `T=0`

At `T=0`, nonnegativity gives `D_*=P=0`; every nonzero root-edge state is
therefore `G`.  On this face the status tag is visible on nine vertices and
(2) can be closed using the nine frozen X-X H9 types.  Direct enumeration of
all ordered marks gives an `11 x 9` integer incidence matrix of rational
rank 9.  It also yields the actual-graph congruences

```text
x8[110787152] = 0 (mod 2),
x8[127315016] = 0 (mod 3),
h9[8]         = 0 (mod 2).
```

The duplicated orientation rows agree identically.  These are genuine new
integer consequences on the all-G face, but do not force a selected edge.

The Wave159 exact rational endpoint has a nonnegative solution for all nine
H9 variables.  Its ordered shadow masses are

```text
edge + nonedge = 91476 = 2*45738,
```

and (1) is zero.  There is also a natural coarse status Gram.  Let `N_a` be
the total physical root-edge incidences of status `a`, and sum `L_ab` over
both root relations.  Then

```text
C_ab = L_ab                         (a != b),
C_aa = L_aa + y_a^2 N_a,
C = sum_e z_e z_e^T >= 0,
z_e,a = y_a * #{roots of state a at e}.                 (3)
```

At the endpoint, `(N_G,N_D,N_P)=(8316,0,0)` and

```text
C = diag(99792,0,0),
```

so (3) is PSD of rank one.  Therefore neither the deletion rows, their
pair-upper zero cells, the restricted unmarked H9 bridge, nor this coarse
PSD condition excludes `T=0`.

## 4. Exact scope boundary for doubled status

The mate is an honest ninth vertex, but `G` and `D` have the same mate bit.
No induced graph on these nine displayed vertices can tell whether a second
source flag exists at one root.  Certifying it explicitly adds the two
non-root vertices of that second source triangle:

```text
no D coordinate: order 9,
one D coordinate: order 11,
two D coordinates: order 13.
```

The tagged lift is nevertheless exact and directly streamable on any graph:

1. bucket augmented flags by `(root,target edge)` to obtain `y`;
2. read the unique mate bit and map the bucket to `G,D,P`;
3. stream Cartesian pairs of source occurrences into the 11 marked rows.

Actual occurrence totals arrive in packets of size `y_a y_b`.  Global
divisibility is necessary, while compatibility of those packets across the
marked orbits is precisely the first missing order-11/13 constraint.  Thus
the lift is a sufficient statistic for (1), but its nonnegative deletion
rows are not claimed sufficient for realization by one graph.

## 5. Boundary conclusion

This lane supplies exact local zero cells and useful all-G congruences, but
no positive lower bound for `T=sum_r E0(r)` and no exclusion of the Wave159
endpoint.  A stronger cut must synchronize doubled packets (generic order
11/13) or use a different full four-root constraint.  No `submission.txt`
was created.

Reproduction:

```text
python scratch_theory_minimal_order9_mate_lift.py
python scratch_theory_minimal_order9_mate_lift_audit.py
```
