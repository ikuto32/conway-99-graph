# V4 four-core portfolio admission and calibration

This is a new Python wrapper only. The native v2 source, builder and executable,
objective TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1, RNG, acceptance, integer deltas
and native interface remain byte-identical. V3's explicit JSON-list edge catalog
representation is retained, as are all full resume domain/source/binary checks.
Old shift6 and six_prism modes retain their domain and execution semantics.

The only additional research core IDs are connected_00 through connected_03,
bound by literal SHA256 to the four raw artifacts in
results/20260930_connected_identity_cores. The portfolio summary is also pinned.
No arbitrary input path or generic core admission is exposed. Their frozen
selection was first connected P=I representative per M1stage, followed by the
first four qualifying stages; this is a four-domain construction portfolio,
not exhaustive target coverage and not a graph-automorphism assumption.

Any new-core mode, including calibration, requires
--portfolio-domain-gate PATH --portfolio-domain-gate-sha256 HASH with status
INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS, binding the exact selection
summary and all four raw cores. Research `run` additionally requires a fresh
independent wrapper calibration gate, status
INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS, binding this v4source,
spec, unchanged native components, domain gate and all portfolio raw artifacts.
The calibration route never fabricates a research approval gate.

`portfolio-calibrate` runs the actual CLI in fresh subprocesses for each new
core: two chains, seed20260930, T3.25, one23-step chunk, a new process resuming
41 steps from its disk JSON, and a separate64-step run. All final/current/best
permutations, RNG states, cumulative proposals, scores and joined traces must
agree. Each64-step input is also run through the native CPU full-recomputation
path and checked against all GPU chain fields, then every delta is checked by
Python's full set-intersection objective implementation. Raw initial, final
and best matrices are exported in {core_adjacency,factor,claimed_score} schema.

These twelve GPU calibration calls execute1024 proposal evaluations (512
whole-trajectory proposals and512 split repeats); four CPU parity calls repeat
the512 whole proposals. No campaign or large restarts are run. Five altered
checkpoints (target, edgecatalog, objective, nativesource, nativebinary) must
fail through the public CLI before native invocation. All paths/receipts/hashes
are preserved, and each public subprocess has a45-second outer guard.
Temperature acceptance remains floating-point heuristic. No full factor is
assumed and no positive-error score is a bound on mathematical feasibility.

Run calibration after the independent domain gate is available:

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_factor_permutation_annealer_v4.py portfolio-calibrate --portfolio-domain-gate REPORT --portfolio-domain-gate-sha256 HASH --out acceleration/results/20260930_factor_permutation_portfolio_calibration_v4
```

An independent reviewer must verify the source changes, each raw core, all
new saved trajectories and public resume paths before a portfolio pilot.
No uv dependency, ledger, old engine, old wrapper or gate is changed here.
