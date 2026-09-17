# Additional pre-execution identity gate

Before any six-coordinate GPU result, add independent binary mapping audit
`six_gpu_export_verifier.json` SHA256
`e9bef8db00a638de44546f3d03ae873312b693f76814127c8563a4dc345ae7d4`
as a mandatory gate alongside independent CPU parity SHA256
`c0ae24550c1f33c1d808107f7aaa9bf49d83d968805f2691a26388b777e2aaf2`.
The first runner/preflight are retained as preparation attempt1. Separately
named runner_v2 adds this gate; it leaves CUDA, export, selection, steps,
300second cap and six certificate attempts unchanged. No GPU ran in attempt1.

With UV_PROJECT_ENVIRONMENT=build/research-venv, launch only:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/run_20260917_six_moment_pdhg_v2.py --out acceleration/results/20260917_six_moment_pdhg/run01`

The runner binds this addendum and both actual gate reports before execution.
Its exact-support extractor uses the audited integer matrix; an independent
raw-neighborhood calculation remains mandatory before mathematical promotion.
