# Fifteen retained native proof files: lossless public packaging

Packaging only, no mathematical verification or solver call. Freeze the completed campaign summary SHA256 `1b735246ecd4ca2e5d3512d356b3c8130c67db74bfb0911dd6fa54e4f87a8b1f`. Read its ordered fifteen case-summary references and authenticate every raw host proof against the original native transfer identity. Expected combined raw size149,571,922 bytes; preserve and freshly rehash all original host files. The ext4 originals are untouched.

Split each raw byte stream deterministically into8MiB pieces, compress each with gzip level9, empty embedded filename and mtime0. Require every gzip payload strictly below10MiB. Preserve per-part raw offset/length/hash and compressed length/hash, the whole raw file identity, source CNF and native receipt references, and exact recovery instructions. Write only new package files and new records. Raw traces, formulas, models, prior catalogs and ledger are not modified. The package is LOCAL_ONLY until publication is separately confirmed.

Run a separate recovery helper with an externally supplied manifest hash. It checks paths remain within the package, chunk order/offsets, compressed hashes, decompressed chunk hashes and the complete raw identity. Stream-verification requires no149MB recovered copy; users may instead choose a new output directory. Deliberately damaged compressed bytes, wrong chunk metadata and wrong whole-file hashes must be rejected in tiny controls. Source and helper are shared engineering code and do not constitute independent proof checking. Structural's complete DRAT replay is a separate audit.

Locked commands:
```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_four_profile_proofs.py --out acceleration/results/20260930_hadamard_four_profile_proof_package
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_four_profile_proofs.py --manifest acceleration/results/20260930_hadamard_four_profile_proof_package/package_manifest.json --manifest-sha256 ACTUAL_SHA --verify-only
```
To write recovered raw files, replace `--verify-only` with `--out NEWDIR`; optional `--case ID` selects one proof. No deletion or overwrite is performed.
