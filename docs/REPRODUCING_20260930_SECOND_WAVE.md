# Replaying the second resumed milestone

Use the existing repository and its root locked environment. These commands
use PowerShell; historical manifests preserve their original commands and
environments without alteration.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked
uv run --locked python acceleration/restore_compressed_artifacts.py acceleration/results/20260930_second_packaging/compressed_artifacts.json
uv run --locked python acceleration/restore_compressed_artifacts.py acceleration/results/20260930_eight_matching_filter/run01/compressed_artifacts.json
uv run --locked python acceleration/restore_chunked_artifacts.py acceleration/results/20260930_eight_filtered_moments/run01/chunk_manifest.json --report build/eight-moment-restore.json
uv run --locked python acceleration/validate_claims.py --hashes available --out build/current-claims-validation.json
```

The chunk restorer intentionally refuses existing outputs. On the original
workspace, use `--destination build/FRESH_RECOVERY_DIRECTORY`, or verify the
already present hashes. Never delete historical files to force a replay.
Restore earlier prerequisite chunks/gzip according to the existing
[main reproduction guide](REPRODUCING.md). New reports require fresh paths;
some historical audit scripts intentionally use fixed output paths. For
literal full reruns, use an isolated checkout and retain the new outputs
separately from historical evidence.

The complete moment and matching-filter audit commands are in their JSON
reports. Each binds all input hashes and the exact source bytes. The model
audit checks every coefficient; the matching audit checks every rejection
and a positive witness for each survivor. Positive matching multiplicities
are not independently claimed.

The fixed-star UNSAT proof is at
`acceleration/results/20260930_rook_sat_pilot/main/proof.drat.gz`; its raw
SHA256 is `6378d40355ff016c3ac5a7434c98116b2c835390f0422539471b19322788aaaa`.
The exact CNF SHA256 is
`85110f18e5f4bb63c5070c0b5b454e683b292467e5e5173a283bfb56abf66d4e`.
The independent proof report records the complete replay invocation and
controls. Its `checker_build` directory preserves upstream source, exact
Windows portability patch, build script, compiler identity and receipts.
The checker upstream commit is
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985` of
[`marijnheule/drat-trim`](https://github.com/marijnheule/drat-trim/tree/2e3b2dc0ecf938addbd779d42877b6ed69d9a985).
Compiled native binaries and the original machine's compiler remain local;
source provenance is public when its containing evidence commit is published.
Build/replay scripts contain recorded Windows paths: adapt output locations
explicitly for a new environment and record that deviation. Do not substitute
the preexisting dirty submodule executable for the authenticated checker.

New solver runs use the separate pinned environment at
`acceleration/environments/rook-sat/uv.lock` with `python-sat==1.9.dev15`
and the `cadical195` engine. The exact local SAT model and independent raw
59-vertex adjacency are preserved; target validation still requires 99 vertices.
The original negative Gram certificate can be checked using only Python
integer arithmetic and the saved raw adjacency, as shown by
`acceleration/audit_20260930_rook_gram_original_v1.py`.

The large GPU binary input is LOCAL_ONLY and deterministically regenerated
by `export_20260930_eight_moment_pdhg.py` after exact inputs are restored.
It has SHA256
`eab22693fbb961fda88bc0401e53f19b3976ecc539b9c1269ad95bfc647b6ea7`.
The new native source/build script and its build receipt are distinct from
the preserved original executable. See the
[retry protocol](NEXT_20260930_EIGHT_GPU_RETRY.md). GPU numerical runs are
optional for replaying a saved exact support certificate; floating scores
are never proof artifacts.
