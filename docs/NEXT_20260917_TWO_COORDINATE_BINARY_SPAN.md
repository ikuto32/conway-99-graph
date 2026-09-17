# Binary affine-span pilot for the two-coordinate moment tables

Use all89,308 original probability columns in84 complete center domains,
with both root0 same-sign coordinates free,156 fixedK edges,1,800 unknown
edges and the exact prescribed absences. Gate on independent domain audit
f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb
and necessary moment-model audit
5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed.
The integer matrix has5,370 rows and96,280 columns; only the first89,308
columns participate. Residual slacks are fixed zero, never span generators.

Let f(t,S) be a full equality column modulo2 and choose the first original
column f(t,0) at every center. An integral target selects exactly one choice
at each center, so r=b−sum_t f(t,0) must lie in the binary linear span W of
all f(t,S)−f(t,0). This is a necessary condition only. A row vector w that
annihilates every such difference but has w*r=1 proves infeasibility of this
declared integer completion problem. If r belongs to W, arbitrary XOR
combinations need not select one actual choice percenter: survival establishes
neither a graph nor exact moment-LP feasibility. This is a new application
of standard modular elimination, not a novelty claim. Archive Wave61 applied
analogous generator screens to a different conditional six-set system.

Frozen traversal: ascending global originalcolumnID, ascending center blocks,
firstoriginalID reference, empty cold basis, highest-set-bit Gaussian pivots
overF2, exact integer bit operations. Stop at30seconds, fullpopulation, or
exact witnessed membership. The timed region includes reference/columnparity
construction and elimination; excludes inputhashing, matrixI/O, controls and
checkpointserialization. Save complete basis, provenance coefficients, current
residual and processed-column cursor on every outcome. Incomplete processing
never yields an exclusion. Early membership requires an explicit list of
originaldifferencecolumns whose XOR is exactly r. Outside-span certification
requires all89,308 differences and a fullannihilation check. A fresh output
folder with --resume CHECKPOINT continues the exact saved state with another
preregistered30seconds; priorartifacthash and initialization change are explicit.

Controls include integer onecenter choices[0,2] and target1 (rationally
LP-feasible but binary-infeasible),32 exhaustive small binary target tests,
positive coefficient witnesses, negative separating rows, and corrupted
zero separators/targets. Producer controls are not independent verification.
A meaningful outcome must be checked from raw neighborhoods by a separate
implementation, including exact rowmapping and originalID references.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_two_coordinate_binary_span.py --out acceleration/results/20260917_two_coordinate_binary_span
```

No automorphism assumption. No ledger edits. Overall search coverage:
UNKNOWN; no validated denominator for Conway-99.
