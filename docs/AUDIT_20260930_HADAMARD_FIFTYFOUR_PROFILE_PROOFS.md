# Independent 54-profile native campaign review

This plan is frozen before inspecting final campaign outcomes. The selected
population is the 54 literal profiles in the authenticated remaining-formula
manifest, not the whole fixed-support family. The independent encoding and
object-calibration reports are separate premises. In particular, an individual
UNSAT result will establish only the corresponding full-Gram and within-group
column-cap profile exclusion. Cross-group caps and residual D are not encoded.

The checker requires the final campaign summary SHA256 explicitly on its CLI.
It verifies the original manifest, exact selected order, every immutable
checkpoint prefix, all completed receipts, unattempted suffix, and resource
accounting. Each formula/model/scope is bound to the complete encoding gate.
Actual SAT, UNSAT, UNKNOWN and unattempted cases are counted separately. A SAT
receipt is not an approved factor; it remains pending the separate raw-object
checker. UNKNOWN and partial traces prove no exclusion.

Every completed UNSAT trace is checked in full against its exact CNF using the
source-authenticated DRAT-trim build. Reuse of the previously independent
checker authentication and replay helper is explicit; no producer Python or
SAT solver is imported or invoked. Native and Windows proof copies must agree
by the saved complete SHA256 receipts and a fresh complete host hash. Preserve
all checker stdout, stderr, return codes, versions and source provenance.

Fresh controls comprise a truth-table-checked small UNSAT instance with a
nonempty reasoning trace, its SAT variant, unsupported-unit and empty-only
proof corruptions, plus rejection of empty-only traces on every actual UNSAT
formula. Mutated native headers, statuses, exit codes, guard flags and declared
conflict allocations must be rejected. Complete replay of one trace never
certifies another trace or an unattempted formula.

Inspect only the exact executable name `cadical` for process observations;
never collect an unrelated process argument inventory. Do not modify the
campaign, prior checker sources, ledger or Git index. Preserve any failed
checker source/receipt before correcting it in a new version.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fiftyfour_profile_proofs.py --campaign-summary-sha256 ACTUAL_FINAL_SHA256 --out acceleration/results/20260930_independent_review/hadamard_fiftyfour_profile_proofs
```

No claim of fibre-orbit transfer, full exception-count coverage, fixed-support
nonexistence, core nonexistence, or target nonexistence is made by this review.
