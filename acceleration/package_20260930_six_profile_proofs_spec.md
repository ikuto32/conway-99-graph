# Frozen protocol: lossless transport of 54 native proof streams

This is engineering preparation, not a proof replay or a mathematical approval. The frozen population is the 54 ordered profile records in `acceleration/results/20260930_hadamard_six_profile_batch_campaign/summary.json`, SHA256 `4d649f76d27cb14eb4e4db325ef617d68c5c6bcef3b52e1efc7f8cd46855fb22`. The original host proof bytes total 555,334,934. Their native exit-20 receipts do not independently establish UNSAT.

Preserve every host and ext4 original. Authenticate the campaign, each per-profile summary and each whole raw proof. Adapt the existing fifteen-proof packager into new source/helper/output paths; record hashes of the unchanged historical implementation. Do not mutate ledger, Git, old packages, CNFs, models or native receipts.

Split each raw proof into contiguous chunks of at most 8 MiB. Compress each independently with gzip level 9, filename empty and mtime 0. Every emitted gzip must be strictly smaller than 10 MiB. Save the compressed hash, raw-chunk hash, contiguous offset and both lengths. The whole package manifest preserves the literal profile ID, exact CNF hash, native summary identity and original paths. The compression recipe is deterministic for the recorded Python/zlib versions; metadata timestamps and current source commit are provenance rather than deterministic payload claims.

Before research-byte packaging, require a tiny positive recovery and rejection of wrong whole hash, chunk length, offset, compressed hash, path traversal and corrupt gzip payload. Immediately stream-decompress each packaged proof and verify every part and whole SHA256. Rehash the retained original afterward. Then invoke the standalone recovery CLI over the entire manifest once more; save its raw output and exact receipt separately. Shared gzip/hash libraries and the recovery helper are disclosed. This is byte identity, not independent mathematical verification.

Ordinary bounded streaming memory: one 8 MiB input chunk plus gzip buffers; no whole proof is loaded. The finite batch is all 54 proofs. A failure stops packaging and preserves all completed files and a failure record; no original is deleted, no automatic retry and no native solver/checker invocation. Availability remains LOCAL_ONLY until publication is actually observed.

Exact preparation command, with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_six_profile_proofs.py --out acceleration/results/20260930_hadamard_six_profile_proof_package
```

Replay byte identity using the saved manifest SHA:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_six_profile_proofs.py --manifest acceleration/results/20260930_hadamard_six_profile_proof_package/package_manifest.json --manifest-sha256 MANIFEST_SHA --verify-only
```

To restore raw bytes, replace `--verify-only` with `--out NEW_DIRECTORY`; optional `--profile-id rank4_00_profile_0002` selects exactly one record. Output files use exclusive creation. Restore into ignored build storage for subsequent independent DRAT replay.
