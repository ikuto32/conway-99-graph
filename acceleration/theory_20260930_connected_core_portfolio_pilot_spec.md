# Four connected-core permutation portfolio pilot

This protocol is frozen before the first research call. It uses only the four
hash-bound P=I cores in `20260930_connected_identity_cores`, in the recorded order.
For each M1 stage, that catalog selected the first M2 representative whose 36-vertex
core is connected, then retained the first four qualifying stages. All 3,580
eligibility decisions were independently checked. These four deliberately selected
domains are not an exhaustive construction search and require no target automorphism.

The fresh v4 wrapper and its independent gate bind the unchanged native v2 source,
builder and executable, the exact four raw cores, and the separate independent core
domain gate. The original wrappers, kernels, calibration evidence and failed runs
remain unchanged. This driver adds a schedule and process supervision only.

For core indices 0,1,2,3 use seeds 20260930+i and initialize 16 chains each. Run
three phases at temperatures 1, 0.25, 0, sequentially for each core. Each phase has
at most eight chunks of 1,024 proposals per chain, and a 120-second wrapper wall
limit. Subsequent phases resume all current/best permutations, RNG and cumulative
proposal counters from the preceding phase's exact saved checkpoint. There are
at most 64 distinct initialized chains, 192 phase-chain endpoints, 96 chunks and
1,572,864 newly attempted proposals in fully saved chunks. These populations overlap
and must not be added. A killed unsaved chunk is reported separately as unknown.

Objective `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1` is the integer sum of squared
errors over the three 12-by-12 cross-fibre Gram blocks. C0 stays canonical; C1
and C2 independently permute their complete 60-column nonmatching-edge catalogs,
preserving within-fibre Grams and margins. Lower scores mean smaller error within
that core's domain. Do not compare scores as mathematical progress across different
core domains. Floating exponential acceptance guides the heuristic only.

An exact reported zero stops the entire pilot immediately for independent raw
factor validation, mixed/outside pair-cap checks and, if applicable, residual
completion. Zero is only an abstract Gram factor, not a target graph. Positive
scores and time/resource failures establish no exclusion. A failed or timed-out
phase blocks that core's later phases; the pilot preserves partial artifacts and
may proceed to the next core. No automatic retry is authorized in this protocol.

The immutable manifest records command, working directory, source commit, Python
and uv versions, hardware, gates, input hashes, complete planned schedule and
stopping rules before execution. Every phase saves its exact command, PID, stdout,
stderr, resource outcome, resume hash and completed checkpoint counts. The driver
can terminate only its owned process tree on expiry. Native stdout, raw inputs,
native outputs, checkpoints and per-chunk raw best factors remain available for
separate independent checking. No producer result is promoted by this driver.

Locked execution from the repository root (PowerShell):

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_connected_core_portfolio_pilot.py --gate acceleration/results/20260930_independent_review/factor_portfolio_v4/summary.json --gate-sha256 df3d3a9ef20c622ce9b529a1aabbba2df18e95ac3e17b1210a866d46657e3ae2 --out acceleration/results/20260930_connected_core_portfolio_pilot
```

The output directory must be new. The original inputs are checked again after the
run. Any later retry or changed schedule needs a new explicit protocol and output.
