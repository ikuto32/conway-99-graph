# Independent scheduling countercontrol

Freeze before run. Authenticate and import only the reviewed parallel builder
and its immutable sequential utility; invoke only the supervisor with an
independently implemented deterministic clock and two harmless fake children.
No real process, producer, formula or native solver is launched. Shared tested
code is explicitly the exact supervisor under review, not reused approval.

Both children start at time0 with a shared deadline1. Child0 reports completion
at time0.025. Its finish method takes either zero (positive control) or five
seconds (countercontrol). Five seconds is a permitted wait duration in the real
WindowsChild cleanup. Child1 remains working until the supervisor cancels it.
Record all events and cancellation time. A cancellation after deadline1.025
in the delayed case contradicts a hard shared work-deadline guarantee, even
though later process cleanup succeeds. The positive case must cancel promptly.

This is a finite engineering falsification of the scheduler guarantee, not a
claim that the OS delayed a process during a research run. A corrected source
must be a new version and needs separate harmless real lifecycle calibration.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_parallel_build_deadline.py --out acceleration/results/20260930_independent_review/parallel_build_deadline
```

Budget10seconds; no ledger, Git or old source changes.
