# Frozen six-coordinate GPU moment pilot

Question: can cold PDHG produce useful exact support multipliers for the
independently audited six-coordinate matching-filtered full-moment model?
The input population is exactly712,721 retained original stars across84centers,
not879,449 unfiltered stars. The independent sound matching partition and model
are premises; no new filtering, enumeration, normalization or automorphism.

Use the frozen moment_pdhg_gpu.cu and existing executable whose four-case
100-iteration independent CPU parity is a mandatory recorded gate. A new
binary export drops84 simplex rows and6972 slack columns; it orders3486 soft
moment rows followed by2040 hard reciprocal rows. Preserve every original
retained ID. Export retains sorted integer coefficients as exact binary float64
CSR and its transpose, using magic C99MHP01. Hash both matrices and all arrays.

Freeze checkpoints1000,5000,10000 and cold uniform probabilities/zero duals.
Use unchanged eta=.9/theta=1, row and block diagonal steps,60 bisections,
256-thread reductions and float64 --fmad=false. No tuning, warm start or retry.
Record source/executable/export/model/parity-gate hashes before launch.
Run one process with a strict300-second whole-process wall cap, which also
bounds GPU compute by300seconds. Retain partial checkpoints on cap/failure.
Measure CUDA event compute time and native post-import elapsed separately;
process wall minus native elapsed includes startup/import/shutdown and is not
a pure import measurement. Exporter separately times loading, transformation
and serialization. No performance improvement claim from these measurements.

After the run, attempt exactly six certificates, last and average duals for
each fixed checkpoint. Missing checkpoints produce explicit skipped records;
never omit a failed/nonpositive attempt or stop on the first positive result.
Convert the negative of CUDA saddle duals to support-function y,q, quantize at
D=2^20 by nearest integer with ties-to-even applied exactly to each saved
binary64 rational; clip moment y to[-D,D], leave reciprocal q unbounded.
Prove an int64 sparse-product bound below2^62 before arithmetic, otherwise
record failure and do not silently overflow. Compute every center maximum and
first maximizing retained/original ID. Final y*b−sum(maxima) uses Python
integers. Positive integer numerator is only a candidate conditional exclusion
until a separate raw-neighborhood checker reproduces it independently.

Every numerical checkpoint records softL1 separately from hard-reciprocity
residual. No numerical upper bound is certified. Do not compare this filtered
objective to old-star or unfiltered objectives as though the domains agree.
Six certificate attempts concern one fixed family, never the unrestricted
Conway99 target. The separate CPU IPM process must not be interrupted.

The approximately1.4GB binary stays LOCAL_ONLY, with deterministic recovery
generator and complete hash. Preserve raw vectors; provide deterministic gzip
companions and raw-byte parts below8MiB when needed. Do not commit the massive
binary or remove original artifacts. Keep checkpoint and recovery manifests.

Locked preparation command:
`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/export_20260917_six_moment_pdhg.py --out acceleration/results/20260917_six_moment_pdhg/export --binary build/research-local/six_moment_pdhg/input.bin`
with UV_PROJECT_ENVIRONMENT=build/research-venv. This command performs no GPU run.
Execution is a separate gated command, recorded before launch.
