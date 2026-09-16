# Applicability of the new degree-moment constraints to source 150

Status: `INDEPENDENT_E72_SOURCE150_DEGREE_MOMENT_FEASIBLE_CONTROLS_AUDIT_PASS`.

All six historically open source-150 macro profiles selected from the frozen
`scratch_root_e72_complete_coverage_inventory_before_m10.json` pass both the
affine test and the convex raw degree-moment model. These controls do not
describe the current open inventory. Their LP weights were converted to exact
fractions and independently checked. Thus these macro-level tests yield no
new E72 exclusion:

```text
macro                 coverage       rank(K4)     exact LP witness
(150,0,3)               4,096             2             PASS
(150,1,0)               8,192             2             PASS
(150,3,3)               8,192             2             PASS
(150,9,0)               4,096             2             PASS
(150,10,0)              8,192             2             PASS
(150,11,0)              8,192             2             PASS
total                  40,960
```

The model uses every raw integral row in `row(K4)`, its prescribed internal
degree, nonnegative weights for each internal-degree position type, zero
first residual moment in each fibre, and the full global second moment
`R^T R=4K4`, where `R_x=4d_x-C[G,*]`. The independent control audit reconstructs
all domains and all equality matrices using
`scratch_theory_e71_degree_moment_lp_audit.py`; it imports neither LP/affine
producer nor their shared base helper and uses no solver. Every stored
nonnegative rational weight satisfies every reconstructed equation exactly.
A feasible weight vector is not a graph or a completion of a fixed overlap
branch.

The older `scratch_theory_e72_open_defect_rank_census.py` applies the
row-space/kernel-port CSP to its frozen input profiles. It does not assemble
the global residual second moment from all individual vertex rows. Its
stored JSON concerns an earlier 59-macro snapshot of coverage 2,236,416, not
the current open inventory; that census was not restarted.

The live source-150 synchronized configuration code imposes more than that
older census. It uses global ordinary configurations satisfying all eight
fibre-summed recurrence rows, followed by synchronized pointwise recurrence
and pair/map constraints. The represented recurrence is

```text
c_x = v_G,                 q=Bc,
H((B+I)q-12c)=0
```

coordinatewise, with the same multiplication by `H` in the fibre-summed
rows. In row-vector convention this is equivalently multiplication on the
right by `H`. The surviving source-150 Gram type is singular:

```text
H = [[4,0,0],[0,2,-2],[0,-2,2]],
ker(H) = span{(0,1,1)}.
```

Consequently code inspection establishes the implemented `H`-projected
recurrences, not an independently proved equivalence between this entire
subsystem and an explicit full `R^T R` row-degree test. No equivalence or
redundancy claim is made for the singular direction. Nevertheless, the
independently verified feasible controls show that adding the new raw
macro-level affine/LP checks would not exclude any of these six profiles.

Artifacts:

- `scratch_theory_e72_source150_degree_moment_applicability.py` and `.json`
- `scratch_theory_e72_source150_degree_moment_applicability_audit.py` and `.json`

Only six small profile-level LP checks were run. No E72 graph-search worker
or live runner was started, stopped, modified, or restarted. No
`submission.txt` was written.

The before-m(1,0) inventory snapshot is byte-identical to the original control
input (SHA-256 `651115B9B9443E8CC4A6C732E14BC50AC959C7D8C087BCD0967D6CF11928E0D0`).
After the separate m(1,0) exhaustive branch result became available, only
input-path/hash metadata and historical-scope wording were migrated; none
of the six numerical models or rational witnesses changed. Both independent
control audits were replayed against these frozen dependencies. A subsequent
branch-complete exclusion is compatible with macro-level relaxation feasibility.
