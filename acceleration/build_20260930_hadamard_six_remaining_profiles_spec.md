# Bounded54-case formula build wrapper

This implements the selection/build protocol in `select_20260930_hadamard_six_remaining_profiles_spec.md`, with selection SHA256 `64035c4d033c9b7d605f556bf69447780bb185ba7bd0fd0c7733ab9e1b0e741f`. It launches only the frozen Python formula builder, never a native solver. Exact source/spec/selection/environment identities are pinned.

Process all54 literal profile IDs in frozen order. A completed case must match its expected raw profile hash, six initial domain references/sizes, selector/variable/clause dimensions, and all manifest output hashes. Independently from the child's compression write, stream every model gzip and confirm its complete raw SHA256/length; retain all original raw files. Record elapsed child wall time, exact command, stdout/stderr and exit. This repeated producer identity checking is not an independent mathematical encoding audit.

Allocation180 wall seconds, minimum5 seconds remaining before next launch,3GiB host disk reserve. Child outer timeout is the actual remaining allocation, bounded also by its own120-second build limit. Stop on timeout/error/resource limit and save an immutable per-case checkpoint plus final partial summary. No automatic retry. Explicit resume into a new directory authenticates the checkpoint and every completed output, verifies an exact selected prefix, skips it and records the previous checkpoint. Prior failed or partial artifacts are never removed or overwritten. Each subsequent allocation needs its own explicit invocation.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/build_20260930_hadamard_six_remaining_profiles.py --out acceleration/results/20260930_hadamard_six_remaining_cnfs/run01
```
Optional explicit resumption: add `--resume-checkpoint PATH --resume-checkpoint-sha256 SHA`. These artifacts belong to wave23. No UNSAT claim is made, regardless of any previously attempted case.
