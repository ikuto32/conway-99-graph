# Cold star-marginal PDHG on CUDA

`star_pdhg_gpu.cu` implements the stronger star-simplex objective on the GPU.
This is a numerical candidate ranker. Exact exclusions still require complete
independent domain checks and the separate integer certificate replay.

The frozen CPU reference is `star_marginal_cp_cpu_v2.py`. Each vertex starts
with a uniform distribution over its complete original star domain; all duals
start at zero. The implementation uses float64, `--fmad=false`, extrapolation
factor1, and the same diagonal steps with safety factor0.9 as that reference.
Warm probability transfer is not used.

## Implementation and inputs

One kernel updates dual rows of the explicit CSR matrix. A second kernel uses
one block per candidate/vertex, gathers the transpose product and projects
onto that vertex's probability simplex. Bitonic sorting is followed by a
serial prefix sum in canonical order. Max-shifting and clamping the shifted
values below at−1 prevent overflow from a large negative tail. Kernel
boundaries synchronize the two stages. Running averages contain iterations
1 through the current iteration.

`export_star_pdhg_binary.py` binds each input candidate, complete domain table,
independent domain audit and saved star-LP audit. It canonicalizes CSR row
order and exports both A and its exact transpose. CPU parity uses those same
exported bytes. The binary protocol is little-endian `C99SCP01`:

```
magic[8], u32 candidate_count, u32 checkpoint_count, u32 checkpoints[]
per candidate:
  u32 N, M, equality_rows, simplex_blocks, nnz
  u32 domain_offsets[blocks+1]
  CSR A:  u32 rowptr[M+1], u32 indices[nnz], f64 values[nnz]
  CSR AT: u32 rowptr[N+1], u32 indices[nnz], f64 values[nnz]
  f64 right_hand_side[M]
```

The native parser checks dimensions, finite values, sorted unique columns,
all offsets, and exact transpose identity before GPU execution. It derives
the steps from absolute row/column sums. A simplex may contain up to8,192
choices, subject to the GPU's checked shared-memory capacity. Larger inputs
are rejected explicitly;8,192 is an implementation limit, not a theorem about
possible star domains. Aggregate, file-size and vector-output caps also apply.

The CLI is `star_pdhg_gpu.exe INPUT.bin FRESH_OUTPUT.json [--vectors]`.
The optional flag saves last p, extrapolated p, last dual and both averages.
Scalar bounds are evaluated on the host at requested checkpoints. Existing
outputs are preserved. Saved binaries and sources are hash-bound; rebuilds
belong at new paths with new control reports.

## Verified controls

`results/20260916_star_cuda_controls/summary.json` has SHA-256
`54aac067fb73fc8ed1ced3db1768c447d68f2538760431ec58df58af0d7bf020`.
It binds1,355 files. The source hash is
`79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8`;
the local binary hash is
`9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075`.

* Four tiny models match all five CPU state vectors at iterations1,2,10.
* Two saved actual configurations,25496 and26025, match all five vectors at
  iterations1,2,10,500,2000 with maximum observed vector difference0. Scalar
  differences are at most3.41e−13.
* Projection controls include sizes1,2,3,1,053,2,049 and8,192. The extreme
  negative-tail case returns[1,0,0]; maximum KKT residual is2.61e−17.
* All37 malformed-input, limit and output-preservation controls pass.
  The2GiB input and64-million-nonzero aggregate caps were source-reviewed,
  without constructing huge invalid files.
* Fourteen previously solved candidates at500 iterations reproduce the CPU
  scalar values to5.41e−13 and all compared rankings. Best dual ranking has
  Spearman0.951648 and includes allfour candidates with the smallest exact
  star-objective intervals.

These14 were selected earlier by edge-CP and local gates. The comparison is
retrospective; ranking quality outside that sample has not been established.

## Initial timing

On the local RTX4090, the14-candidate500-iteration run took0.3395s to parse,
0.9662s in the iteration kernels, and0.0403s for checkpoint transfer and host
metrics. Native elapsed time before JSON serialization was1.4987s. This does
not include Python model construction/export or process startup. Historical
CPU iteration times use a different scope and do not establish an end-to-end
speedup ratio. Separate paired measurements use identical binary inputs and
process boundaries.

Three alternating CPU/GPU process pairs used the same two saved candidates
(25496 and26025), binary bytes, checkpoints1,2,10,500,2000 and scalar-only
output. Their CPU/GPU wall-time ratios were9.4307,9.4345 and9.1822; the median
paired ratio is **9.43×**. Median process times were11.4039s for CPU and1.2340s
for GPU. Both include startup/imports, parsing/validation, iterations, host
metrics and final JSON writing. All86 scalar comparisons per trial passed
the unchanged tolerances; maximum difference was3.41e−13. The OS/file cache
was warm, and unrelated CPU research was running. These measurements describe
this two-candidate workload, not general hardware throughput or domain-export
time. The report is `results/20260916_star_cuda_controls/paired_benchmark/summary.json`
with SHA-256 `690586a3f2023d10ac25a47db1efe71bc093cc04b3ce618d9f5af7375b13879a`.

The current exporter consumes independently audited saved cases. Applying
this GPU model to a new neighborhood still needs a bounded batch exporter for
new native domains, selection provenance, and fresh independent verification
of the final shortlist. A later factorized R/E/C implementation can reduce
geometry storage, after preserving the current parity controls.
