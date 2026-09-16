# Matrix-free CP: frozen implementations and completed controls

The Rust and CUDA implementations evaluate the same necessary phase-I model and
Chambolle–Pock (CP) recurrence. The completed controls below establish agreement
of the geometry, matrix products, updates, and saved numerical results. This
note contains no results from the ongoing CP candidate search.

All CP primal and dual values remain numerical diagnostics. They do not certify
an LP optimum, exclude a candidate, establish exact feasibility, or construct a
99-vertex graph. Existing exact fixed-K audits remain a separate step.

## Model and semantic order

For one complete overlap assignment K, the fractional variables are the 1,680
disjoint-support outer pairs, in lexicographic order. Every outer vertex has
four known K neighbors and two root labels. The model is

```text
F_K(x) = sum over quota rows |A_r x - b_r|
         + sum over pair rows max(0, A_r x - b_r),    0 <= x <= 1.
```

There are 840 foreign-label quota rows, ordered first by outer vertex 0–83 and
then by symbol 0–13, omitting the vertex's two root groups. These precede all
3,486 outer pairs u<v in lexicographic order. The 336 own-root zero-term quota
rows are absent; zero-term pair rows are retained. The pair inequalities drop
the nonnegative unknown–unknown common-neighbor contribution. Disjoint block
totals are not fixed.

Dual coordinates belong to [-1,1] for quota rows and [0,1] for pair rows. A saved
LP may omit tautological pair rows. Its dual must be transferred by
`(kind, coordinate)`, with zero weights for omitted rows, rather than copied by
array position. X must retain the exact disjoint-edge column order.

## Direct operator formulas

Let L(u) be the two root symbols of outer vertex u, and K(u) its four known
overlap neighbors. Extend x[u,v] by zero whenever {u,v} is not a disjoint-support
variable. For a foreign symbol s, the quota row is

```text
(A x)[u,s] = sum over v with s in L(v): x[u,v]
b[u,s]    = 2 - number of w in K(u) with s in L(w).
```

For an outer pair u<v, the pair row is

```text
(A x)[u,v] = x[u,v]
             + sum over w in K(u): x[v,w]
             + sum over w in K(v): x[u,w]
b[u,v]    = 2 - |L(u) intersect L(v)|
              - |K(u) intersect K(v)| - indicator({u,v} in K).
```

Write the dual coordinates as q[u,s] and symmetric p[u,v]. For a disjoint
column {u,v}, the transpose product is

```text
(A^T y)[u,v] = sum over s in L(v): q[u,s]
               + sum over s in L(u): q[v,s]
               + p[u,v]
               + sum over w in K(u): p[v,w]
               + sum over w in K(v): p[u,w].
```

Each column has four quota and nine pair incidences. Each quota row contains
eight columns, and each pair row contains at most nine. Thus there are 21,840
nonzeros, and

```text
||A||_2^2 <= ||A||_1 ||A||_infinity <= 13 * 9 = 117.
tau * sigma * 117 = (9/100)^2 * 117 = 9477/10000 < 1.
```

This is an algebraic bound on the model's operator and step-size condition.
Finite floating-point iterates still require numerical and independent exact
checks before they can support a mathematical claim.

## Update and bound bookkeeping

Both native programs use float64, tau=sigma=0.09 and theta=1:

```text
y_new    = clip_dual_box(y + 0.09 * (A*xbar - b))
x_new    = clip_[0,1](x - 0.09 * A^T*y_new)
xbar_new = 2*x_new - x
```

Initial xbar equals initial x. Incremental averages contain iterates 1 through
t, excluding the initial iterate. At requested checkpoints, both the last and
averaged iterates are evaluated using

```text
U(x) = F_K(x)
L(y) = -b.y + sum_j min(0, (A^T y)_j).
```

Reported `best_upper` and `best_lower` include the initial point and the last
and average values at requested checkpoints. They do not inspect every
iteration. A longer run can have a worse last iterate than a shorter run;
changing the requested checkpoint list can change the reported best values.
An initially good primal point is therefore retained explicitly.

## Implementations and shared interface

[overlap_cp_cpu.rs](overlap_cp_cpu.rs) is a dependency-free Rust implementation.
It uses degree-four K neighbor lists and geometry indices for forward and
transpose products, without storing a sparse constraint matrix. With
`--vectors`, it also exports the initial A*x, A^T*y, integer targets, and row
and column incidence sums for direct structural checks.

[overlap_cp_gpu.cu](overlap_cp_gpu.cu) assigns one 256-thread block to a candidate.
Its quota-column table is shared geometry; the K-dependent pair contributions
use the four neighbors directly. X, extrapolated X, and Y reside in shared
memory, with barriers between the dual and primal updates. Running averages
reside in global memory. Candidate launches are tiled in groups of at most 256.
The reviewed CUDA build disables FMA contraction with `--fmad=false`.

Both programs accept:

```text
PROGRAM INPUT.txt OUTPUT.json [--vectors]

C99CP1 candidate_count checkpoint_count
ascending_checkpoint_integers
1680 initial X values
4326 initial Y values
candidate_count groups of 168 canonical outer endpoint pairs
```

All candidates share the initial X and Y. Output paths must be new. The input
limits are 100,000 candidates, 32 checkpoints, and 1,000,000 iterations; vector
output is limited to 64 candidates. These are parser limits, not suggested
experiment sizes. Full99 partial caps, degree four, exact own-label quotas,
finite boxes, and input shape are checked before computation.

See [CP_GPU_INTERFACE.md](CP_GPU_INTERFACE.md) for the full CUDA output schema,
build instructions, shared-memory requirements, and timing definitions. The
reviewed device was an NVIDIA GeForce RTX 4090. Small validation batches do not
establish large-batch throughput or speedup over HiGHS.

## Completed independent controls

The five saved real K controls are the unchanged baseline and candidates with
changed-edge cycle partitions 2+2, 5, 6, and 2+4. They come from the earlier
audited whole-matching pilot, not fabricated positive graphs.

| Control | Completed result | Durable report |
|---|---|---|
| Rust exact dyadic matrix products | All 21,630 forward entries, 8,400 transpose entries and 21,630 integer targets agree exactly with independently derived full99 rows. All row/column incidences and adjoint identities agree. | [Matvec audit](results/20260916_cp_native_matvec_qa/audit.json) |
| Rust updates at steps 1 and 2 | Quarter-valued X and eighth-valued Y compared with exact rational 9/100 updates; maximum vector error 2.50e-16, bound error 1.73e-11. | Same matvec audit |
| CUDA saved-CPU and direct short replay | Five graphs, two dual starts, and two run lengths: 20 cases. Checkpoints 1/2/10 and 500/2,000/10,000. All 720,720 vector entries agree within 3.89e-15; 620 scalar checks within 7.11e-14. | [GPU controls](results/20260916_cp_gpu_controls/audit.json) |
| Shared parser and output guards | 37 negative cases per tool, 74 invocations, all rejected. Includes malformed counts/checkpoints, nonfinite values, box violations, broken graph inputs, a degree-preserving partial-cap violation, vector limits, and existing outputs. | [CLI controls](results/20260916_cp_cli_controls/report.json) |

The Rust checker builds its reference rows using the frozen
[audit_phase1.py](audit_phase1.py) full99 derivation. Its initial dyadic matvec
comparisons use exact representable values. CP update comparisons separately
allow the documented floating error against rational 9/100 arithmetic.

The CUDA checker reuses the saved independent CPU iterates for long runs and
uses a separate plain-Python row recurrence for short runs. It checks semantic
row and column order, all vector boxes, and independently recomputes primal
and dual values. Neither checker imports an optimization producer's matrix
builder. These controls support implementation agreement within their tested
scope; they are not a general proof of software correctness.

## Frozen evidence

| Artifact | SHA256 |
|---|---|
| `overlap_cp_cpu.rs` | `2df9c312a8e83ead38be9ea279352f77c12a1a7e8cd1cda104e899b8f9caae16` |
| `build/overlap_cp_cpu.exe` | `8b81c702ef28c49834b65e831803237e376d9ff667c9ae2b4289ce2fb484f42e` |
| `overlap_cp_gpu.cu` | `4ae8a33b53df5176eedfd94f950ee9de2a667bcc850e69069af86049b96344a8` |
| `build/overlap_cp_gpu.exe` | `6ddc99a1fa55fd3880f3ce6d1a50e63d4144c1915e6bf30eb6c18abf25865e6d` |
| `results/20260916_cp_native_matvec_qa/audit.json` | `4d8e3fc7e807dd6f91d66f7a17e087d2f2c7899213b6b0f7ef43c854b172571a` |
| `results/20260916_cp_gpu_controls/audit.json` | `80812864937df9f764070bd0a18b6d380257e66a1d148ecc9e095bbb64e3afa9` |
| `results/20260916_cp_cli_controls/report.json` | `7fa5f9e841ce31612d375bef9fe862630acb3239cf687d1f7379add291898422` |

Reports bind the exact source, binary, candidate and input files by hash.
Rebuilds and new experiments need fresh output paths and fresh provenance;
the frozen implementations and control artifacts above remain unchanged.
