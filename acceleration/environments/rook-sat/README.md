# Locked rook SAT solver environment

This small project isolates the new solver dependency from the root research
environment and its already-frozen manifests. It uses `python-sat==1.9.dev15`
and the exact transitive resolution in this directory's `uv.lock`.

From the repository root on PowerShell:

```powershell
$env:UV_PROJECT_ENVIRONMENT=(Join-Path (Get-Location) 'build/rook-sat-venv')
uv sync --project acceleration/environments/rook-sat --locked --cache-dir .uv-cache-20260917
uv run --project acceleration/environments/rook-sat --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_sat_runner.py --calibration-only --out acceleration/results/rook_solver_calibration_REPLAY
```

Use a fresh output directory. The first recorded setup selected Python
3.12.12, `python-sat` 1.9.dev15 and `six` 1.17.0. The runner records the actual
Python version and native `pysolvers` module hash. It uses the embedded
CaDiCaL195 engine and the existing `tools/drat-trim/drat-trim.exe` checker,
whose source/binary hashes are separately recorded. This directory does not
modify or replace historical `.deps` environments.

The main pilot additionally requires a generated CNF, its saved encoding
model, and a separate successful encoding audit. Providing an audit file is
only an evidence-binding step; a human/root agent must assess its exact
statement and outcome before launching the expensive solve. All producer
results remain unverified until separately checked. A local-window SAT result
is not a Conway-99 graph; an UNSAT result applies only to its exact encoding.
