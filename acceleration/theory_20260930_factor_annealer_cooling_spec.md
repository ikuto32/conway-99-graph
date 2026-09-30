# Frozen cooling-resume pilot

Question: does cooling the saved T=1 positive-error states improve the exact
cross-Gram objective or produce a zero-error factor candidate for either of
the two specified cores? This is a bounded construction experiment, not a
fixed-core exclusion or target-wide search coverage calculation.

Use the unchanged calibrated v2 Python engine, CUDA source and executable.
The kernel gate is `70c54735a3331f4bc9dff3ace2f5d1dd4bae49ec051f415a262538f9385b20b9`.
The starting-state independent audit is
`97858230f5e777d601554e51184f0cb3b57ce6d39ed022a3850005b49c27fdd5`.
Start shift6 and six_prism respectively from their six-case pilot T1
`checkpoint_00007.json`. Exact checkpoint hashes are pinned by the driver.
All current permutations, historical best permutations, RNG states and
cumulative proposal counters are resumed unchanged, not reinitialized.

For each core run T=0.25, then resume its latest completed checkpoint at T=0.
Use 16 chains, at most 16 chunks and 1,024 proposals per chain per chunk in
each stage. This is four planned stages, at most 1,048,576 NEW proposals,
across 32 previously initialized chains. Stage counts and chain counts
overlap and are not added. Seeds remain recorded for CLI completeness but
the exact resume checkpoint replaces initialization. Both cores use their
original seed values. No new starts or retries are permitted.

Configure the existing engine with `--seconds 120`; additionally the new
driver supervises each engine process with a 120-second deadline, terminating
only that launched process tree on expiry and preserving every complete
checkpoint. Cleanup may add up to fifteen seconds. This makes the stage
budget explicit despite the engine's between-chunk clock check. An expired
or failed first cooling stage prevents its dependent T=0 stage; the other
core remains an independent planned case. Do not silently restart from an
older checkpoint. On any reported E=0 stop all further cases for independent
raw-object review, including when it appears in a last saved checkpoint
after an abnormal exit.

The objective is TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1, minimized over two
permutations of each fixed core's nonmatching-edge catalogs. Its score is
computed over integers; floating acceptance probabilities are heuristic.
Compare only scores within the same core/objective. No positive score is a
lower bound or nonexistence certificate. E=0 is only a full-Gram candidate:
all raw factor/domain/mixed/column-cap checks and residual D still matter.

Before any research engine call save source commit, exact commands, all
source/binary/gate/checkpoint hashes, hardware observation and full planned
configuration. Save a separate stage manifest binding the actual resume
artifact before each call. Preserve stdout/stderr, exit/timeout receipt,
all engine artifacts and exact proposal increments. No engine source, prior
checkpoint or previous result may be overwritten. Independent State/root
recomputation of all saved scores is required before promoting any result.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_factor_annealer_cooling.py --out acceleration/results/20260930_factor_annealer_cooling
```
