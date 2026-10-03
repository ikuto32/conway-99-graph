# Fresh native54 object-checker calibration

This wrapper preserves the independently audited 54-formula source and gate unchanged. It binds the exact new native runner/spec, its statically resolved local imports and explicitly dynamic balanced helper, the producer spec, the complete independent checker import closure and the same frozen encoding gate. Native and producer modules are never imported or executed by this checker.

Every invocation authenticates all 54 CNF/model/scope triples, selected raw profiles and complete initial domains through that gate. For a research SAT object, the explicit profile ID selects exactly one permitted formula. The wrapper independently reconstructs that model/scope and every clause, compares the actual DIMACS bytes, parses all native signed IDs, requires a complete matching JSON assignment, and checks every actual clause. It decodes the raw factor, all literal profile counts, full integer Gram and margins, aggregate support, local caps and canonical C0 column bijection. All outside-column and mixed-cap violations are computed as diagnostics. An optional producer-decoded object must agree completely; its absence does not prevent independent validation.

Calibration repeats complete reconstruction for all 54 formulas. The genuine SRG243 factor and its reverse-column image calibrate the generic exact raw-factor path. Synthetic native/JSON/clause positives exercise both actual dimensions. First and last options from every raw domain give 108 positive *local* decode controls, with profile counts, aggregate entries and margins checked. Their complete auxiliary assignments are rejected against each actual full formula; they are not research SAT witnesses. Malformed native status/termination/IDs, missing or Boolean JSON literals, native/JSON mismatch, false clauses and corrupted generic factors are rejected. The actual command-line parser is exercised through `sat --help`.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fiftyfour_profile_object.py calibrate --encoding-gate acceleration/results/20260930_independent_review/hadamard_fiftyfour_profile_cnfs/summary.json --encoding-gate-sha256 4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5 --out acceleration/results/20260930_independent_review/hadamard_fiftyfour_profile_object_calibration
```

The research ABI is:

```text
sat --profile-id ID --encoding-gate PATH --encoding-gate-sha256 SHA --assignment JSON --native-output LOG [--decoded JSON] --out NEWDIR
```

Use fresh output directories. A successful research object check would establish a fixed-profile Gram factor only. It would still require omitted target constraints and residual completion; it would not be a Conway99 graph.
