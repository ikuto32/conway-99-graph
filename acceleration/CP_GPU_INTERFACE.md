# CUDA phase-I approximate reoptimization prototype

`overlap_cp_gpu.cu` implements the float64 Chambolle–Pock recurrence reviewed in
`PHASE1_CHAMBOLLE_POCK_REVIEW.md`. Existing sources and historical artifacts are
unchanged. Results are numerical ranking diagnostics; no floating primal or
dual value is a certificate, exclusion, exact optimum, or graph completion.

Build from the repository with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File acceleration/build_overlap_cp_gpu.ps1
```

The helper uses the installed CUDA compiler and Visual Studio C++ toolchain,
targets `sm_89` by default, and disables fused multiply-add contraction with
`--fmad=false` for reference parity. Rebuilding changes executable provenance;
the reviewed executable is already frozen at the hashes below.

## Command and input

```text
acceleration/build/overlap_cp_gpu.exe INPUT.txt OUTPUT.json [--vectors]
```

`OUTPUT.json` must not exist. Input is whitespace-separated ASCII:

```text
C99CP1 candidate_count checkpoint_count
checkpoint_1 ... checkpoint_k
initial_x_0 ... initial_x_1679
initial_y_0 ... initial_y_4325
168 canonical u v overlap pairs for candidate0
168 canonical u v overlap pairs for candidate1
...
```

All candidates share the initial X and Y. Candidate count is 1–100,000;
checkpoint count is 1–32; checkpoints must be strictly increasing integers in
1–1,000,000. These are parser limits, not runtime recommendations. Vector output
is permitted only for at most 64 candidates.

X uses the existing lexicographic disjoint outer-pair order (1,680 entries) and
must be finite in [0,1]. The first 840 Y entries are quota rows, ordered by outer
vertex 0–83 and symbol 0–13, excluding symbols in that vertex's two root groups;
their box is [-1,1]. The remaining 3,486 Y entries are all outer pairs u<v in
lexicographic order, with box [0,1]. Omitted zero-term pair rows in an LP output
must be explicitly filled with zero before export. Do not include the 336
own-root zero-term quotas in this Y vector.

Edges have zero-based outer endpoints with 0<=u<v<84. The 168 edges must be
distinct, join supports sharing exactly one root group, and give overlap degree
four. The parser reconstructs full99 adjacency and checks all partial degrees,
all 4,851 partial pair caps, and all 336 exact own-root label equalities. It
rejects malformed integers, nonfinite scalars, invalid boxes, trailing tokens,
and inconsistent candidate graphs before launching CUDA.

## Update and output

The recurrence is:

```text
y_new    = clip_D(y + 0.09 * (A*xbar - b))
x_new    = clip_[0,1](x - 0.09 * A^T*y_new)
xbar_new = 2*x_new - x
x_average += (x_new - x_average) / iteration
y_average += (y_new - y_average) / iteration
```

The averages start at zero and include updates 1 through the current iteration.
Initial xbar is initial x. All 4,326 semantic rows are retained, including
tautological pair rows. The operator is matrix-free: quota rows have eight
gathers, cap rows at most nine, and each transpose column thirteen.

Output contains:

```text
status: NUMERICAL_CHAMBOLLE_POCK_PHASE1_HEURISTIC
candidate_count, device, precision, tau, sigma, theta, checkpoints
results[candidate_index]:
  candidate_index: global zero-based input index
  initial: {primal_upper, dual_lower}
  checkpoints[k]:
    iterations
    last: {primal_upper, dual_lower}
    average: {primal_upper, dual_lower}
    best_upper, best_lower
    x_last, y_last, x_average, y_average   # only with --vectors
```

`best_upper` is the minimum over the initial primal value and the last/average
values at requested checkpoints up to that point. `best_lower` is the analogous
maximum. They do not scan every iteration. Thus changing the requested
checkpoint list may change the reported best values even when final iterates
remain the same.

The objective formulas are U(x)=sum|quota residuals|+sum positive cap residuals
and L(y)=-b*y+sum min(0,A^T*y). The output includes an explicit numerical-only
scope. Consumers must bind input, source, executable, and candidate order;
the executable does not compute SHA256 hashes itself.

## Execution and validation

Each candidate is processed by one 256-thread block. Shared x/xbar/y use 61,488
bytes; candidate neighbors and RHS add 4,662 bytes; reduction scratch adds
4,096 bytes. Dynamic shared-memory opt-in is required. Running averages reside
in global float64 memory. The host queues tiles of at most 256 candidates to
bound individual launch duration; iterations are performed inside each block.

`kernel_seconds` is the CUDA-event interval enclosing all queued candidate
tiles. `elapsed_seconds` includes device copies, kernels, and result copies, but
excludes parsing, allocation, and JSON serialization. Host stdout also reports
wall time including parsing and serialization. Large-batch performance requires
measurement on the actual batch; small controls do not establish it.

Independent positive controls are frozen at
`results/20260916_cp_gpu_controls/audit.json`, SHA256
`80812864937df9f764070bd0a18b6d380257e66a1d148ecc9e095bbb64e3afa9`.
They cover five real graphs, two dual initializations, checkpoints 1/2/10 and
500/2,000/10,000, direct short-step Python replay, and saved CPU long-step
vectors. All 720,720 vector entries matched within 3.89e-15, and 620 scalar
comparisons within 7.11e-14. Every returned vector was finite and within its box.

The independent Rust dyadic control used quarter-valued X and eighth-valued Y
at one and two iterations. GPU and Rust initial objectives agreed exactly;
the maximum vector discrepancy was 3.33e-16. Its GPU output is preserved at
`results/20260916_cp_gpu_smoke/dyadic_gpu.json`.

Frozen SHA256 values:

| Artifact | SHA256 |
|---|---|
| `overlap_cp_gpu.cu` | `4ae8a33b53df5176eedfd94f950ee9de2a667bcc850e69069af86049b96344a8` |
| `build_overlap_cp_gpu.ps1` | `5fbb14853c50330a27352b665d90ff0efbfc135ed1dd3301909ddfea12b2bda5` |
| `build/overlap_cp_gpu.exe` | `6ddc99a1fa55fd3880f3ce6d1a50e63d4144c1915e6bf30eb6c18abf25865e6d` |
