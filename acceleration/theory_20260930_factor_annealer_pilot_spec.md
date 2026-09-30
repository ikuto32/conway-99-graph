# Two-core permutation annealer pilot, 2026-09-30

Question: can the independently calibrated permutation search produce an exact
full Gram factor for either of two specified triangle cores? This is a finite
heuristic construction attempt, not exhaustive coverage or a nonexistence test.

The frozen six cases are the Cartesian product of cores `shift6`, `six_prism`
and constant temperatures 1, 3.25, 8. Each case has 16 chains, at most eight
chunks of 1,024 proposals per chain, and 120 seconds checked between chunks.
Each native call has a 60-second cap. Core seeds are 20260930 and 20260931,
respectively; each core uses the same initial states at all three temperatures.
The maximum is 786,432 proposals across 96 initialized chains. Proposals are
attempts, not distinct matrices. Failed and truncated cases remain recorded.
No sampled fraction represents the target's search space.

The objective is `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1`, minimized over two
permutations of the core's nonmatching-edge catalogs, with C0 fixed. Its exact
integer value sums squared errors over the three cross-fibre Gram blocks.
Floating-point acceptance probabilities guide the search only. Scores are
reported separately for the two fixed-core domains and are not mathematical
lower bounds. No target automorphism is assumed.

All source, binary and calibration-gate hashes must match the independent gate
before launch. The unchanged uv.lock pins Python dependencies. The pilot saves
the exact configuration and hardware record before the first native call, plus
every chunk input, result, receipt, raw best object and resumable checkpoint.
The pilot stops after an E=0 report to permit immediate independent raw-object
checking; any remaining planned cases are explicitly skipped for that reason.
A producer error is recorded and does not erase other cases.

Success threshold: an independent raw-object checker must reproduce integer
E=0 and every within-fibre/domain condition. Mixed and outside-column bounds
then require their own checks. Even a full accepted Gram factor lacks the
residual 60-vertex adjacency matrix and is not a Conway-99 solution. A nonzero
minimum merely records the best saved state in this pilot; it falsifies neither
the fixed core nor the target. The independent audit will reconstruct all final
chains' current and best raw matrices, and check all saved per-chunk best raw
objects. It need not claim to replay every annealing transition.

Run under the existing locked environment, passing the independently supplied
gate and its exact hash:

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_factor_annealer_pilot.py --gate GATE --gate-sha256 SHA --out FRESH_DIRECTORY
```

Interrupted work is preserved. The calibrated engine's `run --resume` accepts
a completed checkpoint with exact source/binary/domain bindings. Any resumed
attempt must use a fresh output and record its source checkpoint, temperature,
remaining limits and deviation from this six-case initial pilot.
