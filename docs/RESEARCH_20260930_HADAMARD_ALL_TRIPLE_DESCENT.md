# Candidate all-triple descent pilot

The bounded pilot completed on source commit
`c31b42ffc2d0ac1dd3d905ac8f80afe1e094663e`. Producer results remain CANDIDATE
pending a separate raw-object/score audit. No mathematical exclusion or valid
factor was obtained. Overall search coverage is UNKNOWN; no validated target
denominator exists.

The fixed domain contains all31,110 local cap-compatible triples in every one
of20 repeated-support groups of the saved six-prism Hadamard support. Unlike
the earlier `theory_20260930_factor_permutation_annealer_v3.py` and v4 GPU
portfolio, updates do not preserve the within-fibre Gram entries. Those earlier
searches permuted complete nonmatching-edge catalogues and used a cross-Gram
objective. The new exact full-Gram objective is not numerically comparable.
Unlike the fixed-L binary MIP, balanced CNF and exception-profile CNFs, this
pilot uses exhaustive single-group replacements with random two-group kicks.
The complete original local-domain catalogue is retained, with no bound on the
exception count. This is a search-method distinction, not a novelty claim.

| Seed | Best full-Gram squared error | Outside cap violations at that best | Updates | Sweeps | Kicks |
|---|---:|---:|---:|---:|---:|
|99023000|326|31|2000|100|95|
|99023001|334|35|2000|100|95|
|99023002|296|37|2000|100|89|
|99023003|338|32|2000|100|94|

All four chains reached the preregistered update limit. Actual end-to-end time
was36.844 seconds within the120-second budget. The8,000 coordinate updates
evaluated248,880,000 replacement scores. These evaluations overlap and are not
a count of distinct global factors. The experiment saved408 immutable
checkpoints, each containing current and best raw matrices, exact scores,
catalogue choices and RNG state. No native SAT/MIP solver was invoked.

The frozen manifest records the exact command, source/spec/input hashes,
Python/numpy/tqdm versions and platform. Calibration used a genuine SRG243
factor,32 direct local contribution checks,52 direct replacement-score checks,
a clearly separate synthetic perfect-score factor, and serialized23+41 versus64
step continuation. These producer controls do not replace independent review.

The final summary is
`acceleration/results/20260930_hadamard_all_triple_descent/summary.json`,
SHA256 `733acd831ce70adc4b4b1e5503f3ee65bf01f5740b1daf3867790b324b812fff`.
The best raw object is `chain_02/best_factor.json`, SHA256
`f78d7ba779f4db8b4da743feaea875dcb8ba517f699ea9d2d93e98d8829138a8`.
The score is an exact integer, but its optimization is heuristic. Neither a
positive score nor failure to find zero certifies nonexistence.

For a later separately allocated resume, authenticate the original source,
model and checkpoint hashes, instantiate `Engine` from the pinned raw support
and catalogue, load the checkpoint's `state`, then call `Engine.step(state,
engine.target)`. The loader converts the saved RNG list back to tuples and
recomputes the full current residual before each update. Saved `order` and
`cursor` retain the exact point within a sweep. The23+41 control exercises that
JSON boundary. A new run must save its own manifest, resource allocation and
outputs; this completed pilot does not keep running or automatically restart.
