# Exact affine degree-moment certificates on the frozen E71 frontier

Status: `INDEPENDENT_E71_DEGREE_MOMENT_AFFINE_AUDIT_PASS`.

The affine test excludes four profiles belonging to three macros, with
labelled coverage 1,310,720. It checks the frozen 132-macro frontier and its
140 kernel-port-passing profiles, reconstructing all 23,137 raw single-row
degree patterns. No quartet, overlap, matching, binary-block, or local graph
products are generated. Discovery took 8.14 seconds and independent replay
took 21.968 seconds.

| Macro | Profile | Forced quadratic sum | Gram-required sum | Coverage |
| --- | --- | ---: | ---: | ---: |
| `(694,0,0)` | unique | 4 | 52 | 262,144 |
| `(694,1,0)` | unique | 4 | 52 | 524,288 |
| `(901,0,0)` | `t=-2` | 384 | 512 | 524,288 shared |
| `(901,0,0)` | `t=-1` | 384 | 512 | same macro |

The source-694 result is documented separately in
`scratch_theory_e71_fibre_quartet_audit.md`. Source 901 is the new macro
excluded by the broader affine test; its coverage is counted once.

For a fixed root, use the integer residual rows

```text
R_x=4d_x-C[G,*],              R^T R=4K4,
K4=28Z-Z^2,                  Z=C0-C.
```

Every row lies in `row(K4)`. Let `v_x` denote its independent pivot
coordinates, and let `m(v_x)` contain the upper-triangular entries of
`v_x v_x^T`. At each of the 84 exact-label positions, `D_x` is the complete
raw degree-row domain after its known internal degree is imposed. Fix one
moment `b_x` from that position's domain and form

```text
S = span_Q { m(v)-b_x : x is a position, v in D_x }.
```

The necessary Gram target must satisfy

```text
upper(4K4[pivots,pivots]) - sum_x b_x in S.               (1)
```

When (1) fails, an exact rational vector `ell` annihilating `S` gives a
certificate. The value `ell.m(v)` is constant throughout each position's
domain. Its 84 forced values sum to something different from
`ell.upper(4K4)`. The test uses only an affine span; it does not claim that
positions can be synchronized, that affine combinations have nonnegative
weights, or that a passing profile has a graph realization.

For source 901, the three pivot supports are `(0,3),(0,4),(1,3)`. Write the
corresponding integer residual coordinates as `a,b,c`.

For `t=-2`, the null vector is
`ell=(0,0,0,1,-2,1)` in upper-triangular coordinate order, giving

```text
Phi(a,b,c) = (b-c)^2.
```

It is 16 at every vertex in the six fibres
`(0,4),(0,5),(1,3),(1,5),(2,3),(2,4)`, and zero at every other vertex.
Therefore its total is `6*4*16=384`. The principal defect block is

```text
K4 = [[46,-23,-23],[-23,72,8],[-23,8,72]],
```

so the Gram identity requires `4*(72-2*8+72)=512`.

For `t=-1`, the null vector is
`ell=(1,2,2,1,2,1)`, giving

```text
Phi(a,b,c) = (a+b+c)^2.
```

It is 16 on the six fibres
`(0,4),(0,5),(1,3),(1,4),(2,3),(2,5)` and zero elsewhere, again totalling
384. This profile's principal block is

```text
K4 = [[46,-23,-23],[-23,72,15],[-23,15,72]],
```

whose all-ones quadratic value is 128, so the required sum is again
`4*128=512`. Both profiles of the macro contradict a necessary equality.

The independent checker imports no producer or shared research helper.
It rebuilds the compression matrices, reconstructs the complete raw degree
domains with principal-column inverses instead of the producer's RREF
parameterization, verifies every exact-position domain hash, and replays
all 140 affine membership decisions using a separate incremental echelon
calculation. It directly checks all four scalar certificates at all allowed
raw rows. Macro keys, retained profile lists, input hashes, and coverage
totals are checked against the frozen catalog, moment profiles, and
kernel-port manifest. Earlier kernel-port exclusions remain frozen inputs.

Artifacts:

- `scratch_theory_e71_degree_moment_affine_probe.py` and `.json`
- `scratch_theory_e71_degree_moment_affine_audit.py` and `.json`

This establishes scoped degree-moment obstructions beyond compression PSD
feasibility. The 136 other tested profiles survive this affine test. No
positive universal `E0` lower bound or exclusion of the entire E71 layer
follows. No `submission.txt` was written.
