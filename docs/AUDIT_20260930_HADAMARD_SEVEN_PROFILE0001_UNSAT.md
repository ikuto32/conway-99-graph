# Independent literal seven-profile proof review

This review concerns only `rank5_07_profile_0001` on the frozen six-prism Hadamard support, with exceptional groups 0, 1, 4, 7, 8, 9, 19. The authenticated encoding has 9,898 variables and 171,091 clauses. Its complete initial local domains include within-triple column caps; cross-group column caps and residual D are omitted. No orbit transfer or other profile is inferred here.

Before replay, bind the complete raw CNF, model, scope, selected profile, encoding/object gates, native source and configuration, manifest, receipts and both proof-copy identities. Check exactly one bounded native call, native exit 20, literal dimensions, version, configured wall/conflict/address-space/file limits, original ext4 SHA256 and copied host SHA256. Process inspection is restricted to the exact `cadical` process name.

The raw complete trace is 7,440,373 bytes, SHA256 `1f2bffea9b59e2a3d17da368468ea5ef8750082fb3d244b4b8f8c07c48f283c6`. The saved run-summary SHA256 is `f03fe30995cfae9f34d6ee412b8b7abeecd09cfd017bda90b2770de4a93d8d1a`. Complete DRAT replay must pass with the previously source-authenticated checker (drat-trim commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, disclosed Windows timing shim). Reusing the same checker is disclosed; no diverse or formally verified checker is claimed.

Calibration uses a tiny exhaustively classified SAT/UNSAT pair and a nonempty reasoning proof. Empty-only and invalid-fresh-unit proofs, a changed SAT input, and an empty-only proof against the actual research formula must fail. Corrupted native header, status, exit, deadline and allocation records must also fail. Replays are bounded separately by the existing helper; no SAT solver is invoked.

The new source is specialized from the frozen independent six-profile proof review. It imports only the previously independent checker-authentication/replay helper, never producer encoding or solver code. It emits a precise r1 exclusion binding whose mathematical dependency is `C-FIXED-HADAMARD-SEVEN-EXCEPTION-PROFILE0001-GRAM-ENCODING r1`, relation `encoding_equivalence`. Existing source, proof and run artifacts remain unchanged, and any checker failure must be preserved before a corrected version is created.

Run in the existing locked environment with a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_seven_profile_unsat.py --out acceleration/results/20260930_independent_review/hadamard_seven_profile_unsat
```

Passing establishes one conditional literal-profile exclusion, with pending publication/external review disclosed. It does not exclude all seven-exception profiles, the fixed support, a core family, or Conway-99.
