# Fixed-X phase-I merit scorer

Build `build_overlap_phase_gpu.ps1`. Run
`acceleration/build/overlap_phase_gpu.exe INPUT.txt OUTPUT.json [--residuals]`.
The output path must be new.

Whitespace input starts `C99GLOBAL1 count`, followed by 1,680 doubles in the
lexicographic order of pairs `0 <= u < v < 84` with disjoint root supports.
Those values are shared by every candidate and must be finite and in `[0,1]`.
Clip tiny solver-bound violations explicitly before export if necessary.
Next are exactly 168 canonical zero-based endpoint pairs per candidate.
The native parser validates duplicate/range/support/degree constraints and all
99-vertex partial common-neighbor caps before scoring.

Output status is `NUMERICAL_FIXED_X_PHASE1_HEURISTIC`; `results` contains
`candidate_index`, `total_violation`, `quota_violation`, `pair_violation`,
`quota_max_abs`, and `pair_max_positive`. With `--residuals`, it also contains
840 `quota_residuals` in vertex/symbol order, excluding symbols in the vertex's
own two root groups, and 3,486 `pair_residuals` in lexicographic outer-pair order.
All pair rows are included; omitted LP tautologies have nonpositive residuals.

The numerical score is the sum of absolute quota residuals and positive linear
pair residuals. Let K be overlap adjacency and X the symmetric matrix supported
only on disjoint pairs. The pair residual is

```
|labels(u) intersect labels(v)| + K_uv + (K*K)_uv
    + X_uv + (K*X)_uv + (X*K)_uv - 2.
```

The `X*X` term is deliberately absent, matching the existing necessary linear
relaxation. Each quota residual is its known-plus-X label count minus two.
Scores are **numerical heuristics**, neither infeasibility certificates nor
LP optima. A score for frozen X is an upper bound on the minimized phase-I
objective for that K, subject to floating-point error.

`elapsed_seconds` covers device transfers and the kernel; `kernel_seconds`
reports device events separately. Parsing, independent native input validation,
host X-quota preprocessing, CUDA startup, and output serialization are outside
that compute interval. Bind the input, output, executable and source hashes in
the calling search manifest or review artifact.
