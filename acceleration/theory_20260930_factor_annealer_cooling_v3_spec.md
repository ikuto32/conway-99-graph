# Cooling resume after independently reviewed v3 Python correction

This is an explicit fresh retry of the failed frozen v2 cooling protocol.
The failed batch at `20260930_factor_annealer_cooling` had two Python errors,
two skipped dependent stages and zero native calls/proposals. Its bytes and
the exact JSON list/tuple diagnosis are preserved. This new driver uses the
independently reviewed v3 Python wrapper with the unchanged calibrated v2
CUDA source, builder and executable. It requires the actual fresh independent
v3 gate and hash as command-line arguments before any research call. No old
calibration hash is invented or reused as if it approved the new wrapper.

The question, objective, starting points and proposal budget are unchanged.
Start from the original independently audited shift6_T1 and six_prism_T1
checkpoint_00007.json, not from calibration fixtures or a reinitialization.
Resume all current/best permutations, RNG states and cumulative proposal
counts literally. For each core run T=0.25 and then T=0, each with sixteen
chains, sixteen chunks, 1,024 proposals per chain per chunk and a 120-second
supervisor limit. Maximum NEW proposals: 1,048,576 across 32 previously
initialized chains; zero new chains. Temperature stages share those chains.
Only the owned process tree may be terminated on timeout, with at most
fifteen seconds cleanup. No automatic retries or silent checkpoint fallback.

Save manifest/source hashes before any native call and an actual resume
manifest before each stage. If a first stage fails or hits its resource limit,
skip its dependent T=0 stage. Stop every remaining planned case on any E=0
report for independent checking. Preserve every raw checkpoint, best matrix,
native input/output, subprocess receipt and observed proposal increment.

TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1 is an integer error objective to minimize
within each fixed core's two-permutation factor domain. Float acceptance is
only heuristic. Positive errors prove no exclusion or lower bound; E=0 still
requires independent raw checks and does not supply residual D. State/root
must independently recompute saved raw scores before any result promotion.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_factor_annealer_cooling_v3.py --gate FRESH_INDEPENDENT_V3_REPORT --gate-sha256 EXACT_HASH --out acceleration/results/20260930_factor_annealer_cooling_v3
```
