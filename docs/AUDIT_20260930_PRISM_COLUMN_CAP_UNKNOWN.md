# Fixed-six-prism column-cap native outcome audit

This checks one recorded native execution, not the semantics of its encoding.
The reviewer `/root/eight_domain_audit` authored the cap-extension producer;
encoding approval therefore remains the separate Structural audit
`independent_review/prism_column_caps/summary.json` (SHA-256
`5c137eb4b497433d02d99e7b1105c34e06f679b55cd5cbe722b8f265d3f47edf`).
The raw-factor checker calibration is independently bound as well. Neither gate
is replaced or promoted by this outcome audit.

`audit_20260930_prism_column_caps_unknown.py` imports no producer implementation.
It follows the earlier independent native-receipt auditing conventions, but
reconstructs the exact command from the frozen 247,320-variable, 920,401-clause
CNF, explicit solver binary, 900-second GNU timeout, 5,000,000-conflict cap,
4-GiB address-space limit, 10-GiB file limit and saved exclusive native workspace.
All gate/model/scope/input hashes and the raw stdout/stderr/receipt identities
must match. Configured resource limits are not measurements of peak consumption.

A completed summary is required before the checker runs. The parser accepts
only explicit UNKNOWN with either native exit0 at its conflict cap, or timeout
exit124 with the native SIGTERM ending. Native final conflicts and CPU/real times
are read directly from stdout. SAT/model lines or UNSAT status are refused and
must instead be checked by the corresponding independent object/proof path.
Ten altered log/receipt controls are rejected in each successful audit.

The entire completed local partial trace is freshly SHA-256 hashed, with size
and modification-time stability checks. Its bytes must match both the original
native sha256sum receipt and the completed copy receipt, including exact command
paths. This authenticates a partial trace only; no DRAT proof is claimed or
checked. A new process snapshot confirms whether a process remains on the exact
input. The report records original and audit commands, commits, environments,
artifact hashes and actual outcome. Trace availability is LOCAL_ONLY.

Run from the repository root after the producer summary is frozen:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_prism_column_caps_unknown.py --summary-sha256 ACTUAL_FROZEN_SUMMARY_SHA256 --out acceleration/results/20260930_independent_review/prism_column_caps_unknown
```

Use the actual completed summary hash, not the placeholder above. The output
directory must be new. UNKNOWN is no feasibility result, exclusion, residual
completion, full target graph, or claim about unrestricted coverage.
