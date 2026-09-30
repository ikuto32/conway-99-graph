# First twelve-column residual PSD diagnostic

Freeze before execution. Input is the first saved partial object of completed case000 in joint-v2, hash pinned in the source. Recompute its full36x36 Gram from the raw36x12 matrix and subtract from the prescribed Gram. Necessary extension condition: if a full factor appends48 columns R, then the residual is RR^T and is positive semidefinite. A negative exact quadratic form excludes only this literal twelve-column choice, not its profile or circuit.

Use exact Fraction symmetric congruence elimination, retaining the original-coordinate basis. A negative diagonal yields its basis vector as a witness. A zero diagonal with a nonzero off-diagonal in the remaining block yields a signed sum of two zero-diagonal basis vectors with negative value; otherwise eliminate a positive diagonal by rational Schur complement. Clear denominators and save an integer vector with a literal integer quadratic value. If no negative pivot exists, save the complete exact congruence certificate and rank; this establishes PSD only after independent certificate checking, never realizability.

Controls: small positive Gram matrix with a nullspace, diagonal negative matrix, zero-diagonal/off-diagonal indefinite matrix, and a genuine243 residual obtained by removing12 columns from its independently checked60x180 factor. Compare the243 residual directly to the remaining168-column Gram. Reject a corrupted quadratic value/vector certificate. Bound120 seconds; no numerical solver, native solver, or full-factor search. Candidate result only, no ledger mutation.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_first_partial_psd.py --out acceleration/results/20260930_hadamard_first_partial_psd
```
