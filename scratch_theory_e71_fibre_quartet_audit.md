# A scalar moment contradiction for both source-694 E71 macros

Status: `INDEPENDENT_E71_FIBRE_QUARTET_SOURCE694_SCALAR_AUDIT_PASS`.

The two frozen E71 macros `(694,0,0)` and `(694,1,0)` are excluded. Their
labelled coverages are respectively 262,144 and 524,288, totalling 786,432.
Each has exactly one full-Gram profile in the frozen profile catalog. The
proof is a scalar equality contradiction, **4 = 52**. It needs no matching
product, local graph completion, SAT call, projector row pruning, or
four-row quartet enumeration.

Let `B` be the 84-vertex outer adjacency matrix, `P` its 84-by-21 fibre
incidence matrix, and

```text
C=P^T B P,
R=4BP-PC,
K4=28Z-Z^2,                  Z=C0-C.
```

The rooted SRG identities give `R^T R=4K4`. In particular, every integer
row `R_x` belongs to the row space of `K4`. Both macros have the same
compression. Its defect matrix has rank two, with the following principal
block on fibres `A=(0,3)` and `B=(0,4)`:

```text
K4[{A,B},{A,B}] = [[46,-23],[-23,36]].
```

The independent checker verifies rank two by reconstructing all 441 entries
from these two principal columns and their exact inverse. Write

```text
a_x=R[x,A],                  b_x=R[x,B],
Phi(a,b)=ab+b^2.
```

The Gram identity requires

```text
sum_x Phi(a_x,b_x)
  =4(K4[A,B]+K4[B,B])
  =4(-23+36)
  =52.                                                   (1)
```

An exhaustive single-row calculation gives a different value. To see its
small size, `a=4d_A-C[G,A]` and `b=4d_B-C[G,B]`, with `d_A,d_B` each in
`{0,1,2,3,4}`. These 25 pivot choices uniquely determine the remaining
19 coordinates. Keeping exactly the integral degree rows with all degrees
in `{0,...,4}` and total 12 leaves only 50 rows across all 21 source fibres.
No row is discarded by a spectral filter in this argument.

Require each row's degree to its own fibre to agree with the fixed internal
graph in the macro. For ordinary fibres it is necessarily two: an internal
triangle would violate `lambda=1` at an adjacent pair sharing an exact root
label, while a triangle-free four-vertex graph with four edges is a cycle.
The resulting pivot rows satisfy:

| Source fibres | Necessary relation |
| --- | --- |
| `(0,4),(2,3),(2,4),(2,6),(4,6)` | `b=0` |
| `(0,5),(1,3),(1,5),(1,6),(5,6)` | `a+b=0` |
| All remaining fibres except `(0,3)` | `(a,b)=(0,0)` |

Thus every vertex outside `(0,3)` contributes zero to `Phi`. The internal
graph on `(0,3)` is a path with degree sequence `(2,1,2,1)` in the fixed
corner order. Its allowed rows are:

| Internal degree | Allowed `(a,b)` | `Phi(a,b)` |
| --- | --- | ---: |
| 2 | `(2,-1)` | -1 |
| 1 | `(-2,-1)` or `(-2,3)` | 3 |

Consequently

```text
sum_x Phi(a_x,b_x) = -1+3-1+3 = 4,                       (2)
```

contradicting (1). All rows in every exact-label position were checked; the
choices for different positions need not be synchronized. The proof does
not even need the four residual rows of a fibre to sum to zero.

Scaling is explicit: the integer residual used here is
`R_x=4d_x-C[G,*]`. If instead the centred degree row is denoted by
`r_x=d_x-C[G,*]/4`, then `R=4r` and `sum_x r_x^T r_x=K4/4`.

The initial quartet probe found that all tested 4-by-4 residual-projector
principal blocks remained PSD. A small matrix-moment dynamic program then
failed to realize the target Gram, revealing the simpler equality above.
The independent audit certifies this scalar proof; it does not rely on, or
credit, those optional quartet/DP diagnostics. It imports no producer or
shared research helper module and uses a different two-column inverse
parameterization to reconstruct the complete raw row domains.

The reusable condition exposed by this example is: for any symmetric
coefficient matrix `L`, the pointwise degree-domain values of
`R_x L R_x^T` must sum to `4 trace(L K4)`. Here
`L=[[0,1/2],[1/2,1]]` on the two pivot coordinates makes each allowed
pointwise value constant after its internal degree is fixed. This provides
an exact row-moment obstruction beyond the positive-semidefinite
compression test.

Artifacts:

- `scratch_theory_e71_fibre_quartet_probe.py` and `.json`
- `scratch_theory_e71_fibre_quartet_audit.py` and `.json`

The exclusion concerns only the two listed macros. It proves no universal
positive lower bound on `E0`, no exclusion of the entire E71 layer, and no
construction or nonexistence theorem for the Conway graph. No
`submission.txt` was written.
