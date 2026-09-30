# Wave22 explicit publication preparation

Frozen population: the five ordered registration records named in the source,
ten new VERIFIED/CLEAR claims, and the 216-claim ledger (213 VERIFIED/CLEAR,
two CANDIDATE/CLEAR, one REFUTED/CLEAR). Directory and file allowlists are exact.
Only this new output directory is written. No solver, mathematical review,
ledger edit, staging, commit, ignore change or original-artifact replacement occurs.

Include the completed fifteen four-profile formulas, native receipts and proofs,
six-exception individual domains/arc screen/fibre action, seven-group kernel and
marginal census, coordinate relabelling census, independent reviews, all failed
checker versions, proof transport, and raw recovery v1/v2. Exclude the later literal
six-profile formula/native pilot, remaining54 formulas, and all-triple heuristic.

Exactly thirty originals remain LOCAL_ONLY: fifteen raw model JSONs and fifteen
complete raw DRAT files. Stream-decompress all forty public gzip streams (fifteen
model streams and twenty-five proof chunks), check offsets, every chunk, full
length/hash and equality to each original. This does not replay the DRAT proofs.

Resolve saved hash maps and path/hash references, require every dependency to be
explicitly selected, already tracked, previously publicly recoverable, a disclosed
local checker/solver binary, or pinned archive content. Authenticate historical
registration validation ledger references against their immutable adjacent after
snapshots. Reject missing/mismatched references, protected file types, future
cohorts, unlisted dependencies and public research files larger than 10MiB. Check
Git's blob transformation bytes and unchanged ledger/index at completion.

`reference_checks.json.gz` contains the same JSON object keys as the previous
plain format: `status`, `records`, `gzip_recoveries`. Encoding is UTF-8, sorted
JSON keys, compact separators and one terminal LF; gzip level9, empty original
filename, mtime0. It is a single ordinary gzip stream, not JSONL. For inspection:
`json.load(gzip.open(path, 'rt', encoding='utf-8'))`. Catalog, diagnostics, byte
checks and scope remain JSON. The compressed wrapper is checked against the same
10MiB public limit. Reference multiplicity is retained, not deduplicated away.

Failure saves the exact source and exception in the fresh output directory;
correction requires a new source/version or explicit preserved failure history.
No result implies public availability until publication is separately confirmed.

Locked preparation command (the current root-authorized preparation pass):

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_twentysecond_catalog.py --prepare --out acceleration/results/20260930_twentysecond_preparation --registration acceleration/results/20260930_twentysecond_local_domains_registration --registration acceleration/results/20260930_twentysecond_encoding_and_seven_registration --registration acceleration/results/20260930_twentysecond_six_pairs_and_orbits_registration --registration acceleration/results/20260930_twentysecond_fifteen_proofs_registration --registration acceleration/results/20260930_twentysecond_four_union_registration
```

Do not run a final publication inventory until the root freezes the checkpoint,
entry documents and final packaging allowlist additions. `--prepare` deliberately
does not emit a stage inventory. The actual command, source commit, timestamp,
ledger hash and all checked byte identities are saved in the preparation outputs.
