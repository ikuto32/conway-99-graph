# Completed fifteen-proof review and schema correction

The original audit stopped before any proof replay because its campaign-metadata
lookup expected `selected_cases`; the frozen campaign manifest uses `selection`.
The final summary correctly uses `selected_cases`. Version2 changes that one
lookup and pins the original checker and failure record. No producer artifact,
formula, proof or experimental limit changed.

All fifteen complete traces passed the authenticated DRAT-trim checker. The raw
proof total is149,571,922 bytes, distinct from the recorded299,143,844 bytes for
both ext4 originals and host copies. There were fifteen completed UNSAT runs,
zero SAT runs and zero UNKNOWN runs. One reasoning-positive control, eighteen
proof-negative controls (including empty-only traces on all fifteen actual
inputs), and ninety corrupted native-receipt controls passed. Every saved
checkpoint prefix and immediate trace-transfer identity was checked.

These results exclude only the fifteen literal profiles. Their normalized-orbit
coverage is outside this review. Cross-group column caps and residualD are absent
from the formulas; within-group column caps are part of their domain scope.

The replay report is
`acceleration/results/20260930_independent_review/hadamard_fifteen_profile_unsat_v2/summary.json`,
SHA256 `351b66f7b01f5863e932991737b8d35f4b1c043b48ff673c987c653d6ed81768`.
Its claim binding is SHA256
`e1277688015537abf01ba533a242bf0ae7ccb884764fde238d9ce74720e9dcc1`.

Replay into a new output directory from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fifteen_profile_unsat_v2.py --out build/fifteen-profile-proof-replay
```

The source-authenticated Windows checker binary must be available as described
by the pinned build records. Packaging or public availability of the proof files
requires separate verification; the report correctly records its then-current
local availability.
