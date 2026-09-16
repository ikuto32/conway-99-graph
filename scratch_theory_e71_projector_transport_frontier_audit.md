# Independent audit of the E71 single-row projector frontier

Status: `INDEPENDENT_E71_PROJECTOR_TRANSPORT_FRONTIER_AUDIT_PASS`.
The independent checker replayed every field of all 140 stored profiles in
132 frozen kernel-port-passing macros. No discrepancy or unsound rejection
was found. The run completed in about 191 seconds.

The checked labelled coverage is 49,086,464. The filters remove individual
degree rows but exclude **no additional profile or macro**:

| Quantity | Exact count |
| --- | ---: |
| Integral single-vertex degree rows reconstructed | 23,137 |
| Rows removed by the corrected minus-four leverage cap | 5,823 |
| Rows removed by the plus-three leverage cap | 0 |
| Rows removed by pointwise transport intervals | 9 |
| Rows removed by residual-projector row-norm intervals | 2,256 |
| Additional rows removed by two-by-two projector minors | 0 |
| Rows remaining after all filters | 15,049 |
| Full-Gram profiles excluded by these row-domain tests | 0 |
| Macros excluded by these row-domain tests | 0 |

The union in the producer includes the previously audited source-724 macro
`(724,1,0)`, with coverage 32,768. That is an inherited exclusion, not a new
consequence of this frontier test. The remaining union coverage is
49,053,696 across 131 macros.

The checker imports only the Python standard library. It reconstructs `C`,
`Z=C0-C`, and `K4=28Z-Z^2` from the catalog and profile JSON, verifies the
alternate rooted-SRG expression for `K4`, and generates every integral
single-vertex degree row using reduced row echelon form. This is independent
of the producer's basis-inversion implementation. Exact principal-range
inverses check positive semidefiniteness and range membership before any
quadratic form is evaluated.

The necessary equations used are

```text
R = 4BP-PC,                 R^T R = 4K4,
4BR = PK4-R(C+4I),
s_x = Z_G-R_x,              s_x Z^+s_x <= 40,
D = 28K-Z,                 t_x = D_G+R_x,
t_x D^+t_x <= 160/3.
```

Here `P` is the 84-by-21 fibre incidence matrix and `K` is the rank-14
coarse cycle projector. The corrected vector `s_x=Z_G-R_x` is essential.
The cross-block-only vector `R_x` is not substituted in its place.

For the residual minus-four projector, the checker uses

```text
g_x = 40-s_x Z^+s_x,
a_xy = 4-6q_xy-2d_xy-s_x Z^+s_y,
G_xy = a_xy-16B_xy,         G_xx = g_x,
sum_{y != x} G_xy^2 = 112g_x-g_x^2,
G_xy^2 <= g_x g_y.
```

It reconstructs the rank-70 exact-label cycle projector and checks its
idempotence with integer arithmetic. All four source positions in every
one of the 441 ordered fibre pairs have the same multiset of geometric
coefficients. Consequently every row-domain deletion occurs in all four
positions simultaneously in this particular relaxation. This explains the
producer's 9,024 removed local assignments: exactly four times 2,256 rows.
The audit uses a degree-indexed dynamic program for the minimum and maximum
squared-row contributions, independently of the producer's enumeration of
adjacent-position subsets.

Soundness depends on the direction of relaxation. Target rows may be chosen
independently, with repetition, and blocks at different source vertices
need not agree. These choices enlarge the feasible set. Therefore an empty
interval or impossible four-row zero sum would exclude a real completion;
surviving rows do not establish one. The input kernel-port frontier is
treated as frozen and its earlier CSP exclusions are not re-proved here.
All recorded dependency hashes, macro keys, profile parameters, and labelled
coverage totals were checked, including the prior source-724 audit inputs.

Artifacts:

- `scratch_theory_e71_projector_transport_frontier_audit.py`
- `scratch_theory_e71_projector_transport_frontier_audit.json`

This result supplies no positive lower bound on `E0`, no exclusion of the
whole E71 layer, and no Conway graph. It establishes that this inexpensive
single-row relaxation, even after exact fixed-point propagation and pair
minors, retains all 140 frozen profiles. No `submission.txt` was written.
