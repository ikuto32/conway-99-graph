# Independent rook-cell audit protocol

Frozen before running the independent checker. Auditor is Codex subagent
`/root/state_literature_audit`. Inputs are the discovery raw files under
`acceleration/results/20260930_rook_cell_factors/`, the discovery written
derivation, and the existing independent rook-encoding recheck.

Question: do the raw matrices satisfy the exact one-cell identity and is the
recorded local two-factor universe complete? These are separate claims.

Acceptance is exact integer equality, binary entries, correct row and column
degrees, perfect matchings, disjoint factor partition, zero matrix residual,
and raw masks forming a distinct valid population with the independently
calculated total and cycle-type counts. No tolerance, seed or numerical solver.

Independent method: Python integer Gram matrices and a separately derived
conditional diagonal-block argument. The census uses subset Hamilton-path
dynamic programming, reversal division by two, and anchored set partitions.
It does not import the producer or duplicate its graph enumeration algorithm.

Positive count controls are complete graphs on 3, 4, 5, 6 and 10 vertices,
whose cycle counts follow from factorial formulas. Raw-witness corrupted
controls alter edges, incidence entries, factor overlap, matching endpoints,
the recorded matrix and a right-side matching. Census corruption controls
duplicate a factor, omit factors and set an out-of-domain bit.

Resource limit: this finite ten-vertex DP and one pass over 89,000 saved
factor masks; terminate and record failure if exceeding 120 seconds.
Every failed run/report is retained; an accepted count cannot be inferred
from a timeout. No graph completion solver or target search is run here.

Command, from repository root, using a fresh report path:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_rook_cell_independent.py --input acceleration/results/20260930_rook_cell_factors --out acceleration/results/20260930_rook_cell_independent/audit.json
```

The script refuses to overwrite its report. Timestamps, exact commands,
source commit, inputs, checker hash and dependency versions are captured in
the produced receipt. Written proof review is recorded separately.
