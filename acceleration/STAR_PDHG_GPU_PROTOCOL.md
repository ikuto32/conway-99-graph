# Cold star-simplex CUDA prototype, protocol 1

This is a numerical ranking prototype. It does not produce a graph, an exact
bound, or an exclusion certificate. Existing star-LP and integer-proof tools
remain unchanged. The binary model is generic; its graph/domain interpretation
is supplied and hash-bound by the separate exporter and independent auditors.

Frozen implementation:

* `star_pdhg_gpu.cu`: SHA256
  `79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8`
* `build_star_pdhg_gpu.ps1`: SHA256
  `ca2b9f7117601b2e5d8e67fbfdab84d1604bf1a0b56fee36f021204a0895772b`
* `build/star_pdhg_gpu.exe`: SHA256
  `9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075`

Built with CUDA 13.2, `sm_89`, C++17, optimization, and `--fmad=false`.
The reference is frozen `star_marginal_cp_cpu_v2.py`, SHA256
`6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d`.

## CLI and input

```
star_pdhg_gpu INPUT.bin FRESH_OUTPUT.json [--vectors]
star_pdhg_gpu --projection-self-test FRESH_OUTPUT.json
```

All integers below are unsigned little-endian 32-bit integers. Floating arrays
are little-endian IEEE754 float64. There is no padding between fields.

```
8 ASCII bytes: C99SCP01
candidate_count, checkpoint_count
checkpoints[checkpoint_count]
repeat candidate_count times:
    N, M, Q, blocks, nnz
    simplex_offsets[blocks+1]                  # uint32
    A.rowptr[M+1], A.columns[nnz]              # uint32
    A.values[nnz]                             # float64
    AT.rowptr[N+1], AT.columns[nnz]            # uint32
    AT.values[nnz]                            # float64
    b[M]                                     # float64
```

`N` counts probability variables, `M` all penalized rows, and `Q` the initial
equality rows. The first `Q` dual entries lie in `[-1,1]`; the remaining duals
lie in `[0,1]`. Hard simplex normalizations are encoded by offsets, not matrix
rows. Actual star models have 84 blocks, 1,680 equality rows and 3,486 cap
rows, so `M=5166`. Generic small models are supported, including zero matrices.

CSR columns must be strictly increasing within each row, with no duplicate
or zero-valued entries. Values and targets must be finite. Both transpose
indices and values are checked exactly before any CUDA call. Row and column
absolute sums and target magnitudes must not exceed `1e290`; this explicit
numerical-range limit prevents internal overflow for valid simplex iterates.

Limits are checked, never truncated:

| Quantity | Limit |
|---|---:|
| Candidates | 1–256; at most 16 with `--vectors` |
| Checkpoints | 1–16, strictly increasing, each 1–20,000 |
| N / M / blocks per candidate | 100,000 / 20,000 / 128; each positive |
| Q | 0–M |
| nnz per candidate | 0–8,000,000 |
| Choices in any simplex | 1–8,192 |
| Aggregate N / M / nnz | 2,000,000 / 1,000,000 / 64,000,000 |
| Input file | at most 2 GiB, no truncation or trailing bytes |
| Saved vector entries | checkpoints × (3 total N + 2 total M) ≤20,000,000 |

An existing output is rejected before parsing/launching and is never
overwritten. Output creation uses an exclusive file open. Invalid input exits
nonzero; partial computational results are not emitted as completed output.

## Iteration and kernel organization

Initialize each simplex uniformly and set all duals to zero. `pbar=p` and both
running averages start at zero. Native code independently computes

```
sigma_i = .9 / max(1, sum_j abs(A_ij))
tau_u = .9 / max(1, max_{j in simplex u} sum_i abs(A_ij))
y_new = clip(y + sigma*(A*pbar-b), dual boxes)
p_new[u] = simplex_project(p[u] - tau_u*(AT*y_new)[u])
pbar_new = 2*p_new-p
p_average += (p_new-p_average)/iteration
y_average += (y_new-y_average)/iteration
```

The primal step is constant inside each simplex. The weighted operator norm
bound is `.81`, as derived in `STAR_MARGINAL_CP_FEASIBILITY.md`. Iteration
numbers and averages continue across checkpoints; a checkpoint does not restart
the solver.

The first kernel assigns one thread to each CSR dual row. The second assigns
one block of 256 threads to each `(candidate, simplex)`, gathers transpose
rows, and projects. Default-stream kernel boundaries provide the global
dual→primal→next-dual ordering. All model state lives in device global memory;
the domains within a candidate write disjoint variable ranges.

Projection subtracts the maximum, clamps at `-1`, performs a descending
bitonic sort, then computes the threshold with a serial prefix in sorted
order. Values below `-1` after shifting cannot enter the active support.
Padding values are `-2` and are excluded from the prefix calculation.
There is no 1,024-choice assumption. Shared memory is
`(next_power_of_two(max_domain)+256)*8` bytes; the 8,192-choice maximum uses
67,584 bytes. The native code checks the device opt-in limit and explicitly
sets the dynamic shared-memory attribute. No conditional thread exits occur
inside the collective projection.

## Output

Top-level status is `NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED`. Output includes
`eta=.9`, `theta=1`, `float_type="float64"`, device name, candidate count and
`numerical_scores_are_proofs=false`.

Each `results[candidate_index]` contains `n_variables`, `n_rows`, `n_equalities`,
`domain_counts`, an `initial` scalar object, and ordered `checkpoints`.
Each checkpoint contains:

```
iterations
last:    {primal_upper_numeric, dual_lower_numeric, numeric_gap}
average: {primal_upper_numeric, dual_lower_numeric, numeric_gap}
best_upper_numeric
best_lower_numeric
# with --vectors only:
p_last, pbar_last, y_last, p_average, y_average
```

The scalar expressions are `sum(abs(Ap-b)[:Q]) + sum(max(0,Ap-b)[Q:])`
and `sum_u min((AT*y)[u]) - b*y`. Scalars are computed on the host from copied
checkpoint states, which is explicitly reported as
`scalar_metrics_computed_on_host=true`. Finite values, simplex normalization
and dual boxes are checked. “Best” includes initialization plus last and
average states only at requested checkpoints, matching the CPU contract.

`gpu_iteration_seconds` is the summed CUDA-event span of iteration segments;
`checkpoint_transfer_and_metrics_seconds` covers vector copies and host
checks/metrics. JSON `elapsed_seconds` includes parsing, setup and those
operations, before final JSON formatting/writing. The one-line stdout elapsed
time includes output formatting/writing as well.

## Initial validation and next boundary

Four generic tiny models at iterations1/2/10 matched the independently
generated CPU state vectors bit for bit; maximum scalar error was `8.33e-17`.
The separate projection smoke test covers sizes3,1,2,1053,2049,8192, including
`[0,-1e308,-1e308] -> [1,0,0]`. Its output contains `cases` records with
`case_index`, `name`, `size`, `input` and `projected`.

Formal real-model/negative controls are owned by the independent Rust-agent
harness. No broad search is authorized by these smoke results. Preserve this
implementation; layout, prefix-scan or factored-matrix optimizations require
new source/binary paths and new parity evidence.
