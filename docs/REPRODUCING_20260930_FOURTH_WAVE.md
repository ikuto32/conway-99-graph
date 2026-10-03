# Fourth resumed milestone: evidence and replay

The root CLAIMS.yaml is authoritative. The fourth checkpoint freezes its claim
population and exact evidence hashes; later updates do not rewrite that snapshot.
The historical external ledger and historical execution environments remain intact.

Install the pinned new research environment from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked
uv run --locked python -B -m unittest discover -s acceleration -p test_validate_claims.py -v
uv run --locked python acceleration/validate_claims.py --hashes available --out build/fourth-local-validation.json
```

The schema/registry check is bookkeeping, not mathematical verification.
Detailed independent checks, their actual commands, controls, exact scopes,
tool versions and input hashes are in the audit links in
[the milestone](RESEARCH_20260930_FOURTH_WAVE.md). The one-shot claim registrar
must not be rerun against an already updated ledger.

Oversized completed raw inputs have exact gzip companions in
`acceleration/results/20260930_resume/fourth_artifact_catalog.json`.
For each entry, decompress `public_companion` to the named raw path in an
isolated replay checkout, then verify its recorded raw SHA256. Do not overwrite
an existing artifact with different bytes. The packager independently streamed
every gzip to confirm the recovered bytes and hash. This checks availability,
not a mathematical certificate. Earlier recovery requirements remain documented
in [the second-wave guide](REPRODUCING_20260930_SECOND_WAVE.md).

The universal proof audits are independently authored Python and written
derivations. Raw28 identities use exact integers; lower-Gram inverse controls
use Python Fraction. The box cuts recompute exact affine coefficients and an
attaining corner; the degree-bound audit checks all recorded matching optima
and bipartite primal/dual certificates. The32 map audit checks every fixed/free
entry and degree row. The352-clause audit checks all signed images and exact
DIMACS suffix bytes. None assumes an automorphism of a target graph.

Most frozen scripts deliberately reject preexisting output paths. Replay in a
separate scratch checkout, preserve the published output as evidence, and use a
fresh output destination where the recorded CLI supports it. Fixed-output
auditors need their generated report directory moved aside within that scratch
checkout before execution. Never change the preserved public evidence to make
a replay appear successful. New timestamps and absolute paths may change a
replayed report's bytes; the mathematical artifact hashes and outcomes remain
the comparison target.

The two specific29 obstructions are independently checked without approving the
producer's overall screen counts. One is already cap-excluded after restoration
of known outside edges. This distinction is recorded explicitly in the bound
report and must survive any later summary.

SAT tooling uses the separate pinned project in
`acceleration/environments/rook-sat/`, not a rewritten root lock. New UNSAT
claims require the exact complete proof, authenticated checker provenance and
independent replay. The current milestone adds no UNSAT claim.
