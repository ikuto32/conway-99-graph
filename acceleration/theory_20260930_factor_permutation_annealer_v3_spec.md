# V3 Python JSON resume-boundary correction

Preserve the complete v2 Python source, failed cooling batch and diagnosis.
The only search-domain representation change is that `problem()` constructs
each nonmatching-edge pair as an explicit list instead of a tuple. The saved
JSON already contains lists. All integer entries, edge order, target matrices,
native input bytes, objective, RNG, proposal logic and native source/builder/
executable remain unchanged. The v2 algorithm specification is historical
evidence and remains unchanged.

The public `run --resume` path still requires exact full problem equality,
objective identity, source/binary hashes and chain count. It no longer compares
JSON lists with in-memory tuples. No check is removed or weakened. Current
and best permutations, RNG states, and cumulative proposals are resumed
literally from the saved checkpoint. No native recompilation is performed.
Research mode requires a fresh independent gate binding this new Python
source/spec and the unchanged calibrated native components before it runs.

An explicit `resume-calibrate` mode spawns this actual wrapper's constrained
`calibration-chunk` mode. That mode is restricted to the two fixed cores,
seed 20260930, two chains, one chunk, temperature 3.25, thirty seconds and
23, 41 or 64 steps. Only the 41-step control resumes. It verifies the old
independent native calibration gate but does not fabricate a research PASS
gate or pretend these controls are a search. For each core, write a 23-step
checkpoint, reload it from disk into a separate 41-step process, and compare
against a separate 64-step process from the identical initialization. Check
all chain fields, complete split-versus-whole traces, current and best
permutations/scores, RNG and cumulative proposal counts. Six native calls
perform 512 control proposals total. Each wrapper subprocess has a 45-second
outer guard and native invocation has the configured thirty-second bound.

Five deliberately corrupted JSON checkpoints alter target, edge catalog,
objective, native-source hash, or binary hash. Each must fail through the
actual public wrapper before creating any native chunk input. These are
negative controls, not proof failures in the mathematical target.

Save all source/command/input/output hashes, intermediate checkpoints,
receipts, controls and failed outputs. An independent reviewer must check
the narrow diff and replay the actual wrapper controls before any cooling
retry. Calibration PASS from this producer is not self-approval. No old file
is overwritten, no solver is launched, and no target conclusion follows.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_factor_permutation_annealer_v3.py resume-calibrate --out acceleration/results/20260930_factor_permutation_resume_calibration_v3
```
