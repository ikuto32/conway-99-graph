# Lossless transport of the completed215 proof streams

Transport preparation only; proof approval comes exclusively from the separately completed independent proof gate. Authenticate the completed native campaign summary SHA25602520b91d50c0f448fc966b61348da0215d520a5f2082767d09918632b0b0b46 and the explicitly supplied proof gate with status INDEPENDENT_FIXED_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_UNSAT_PASS. Require all215 literal replay records, no UNKNOWN/pending SAT/unattempted case, and exact per-proof/CNF correspondence. The host originals total577,482,170 bytes; both original copies remain untouched. This package itself performs no DRAT replay or scientific promotion.

New source/helper/output names adapt the frozen54-proof implementation, whose three source hashes are retained. For every exact ordered profile record, split the raw proof into contiguous chunks of at most8MiB; gzip each with level9, empty filename,mtime0. Every compressed member must be strictly below10MiB. Save original native path, CNF hash, per-profile summary/hash, every offset/length/raw and compressed SHA256. The recipe is deterministic within the recorded Python/zlib versions. Provenance timestamps and source commit are not deterministic payload claims.

Fresh tiny recovery controls precede packaging: exact positive, wrong whole hash, chunk length, offset, compressed hash, escaping path and corrupt gzip payload. Immediately stream-recover every packaged proof, checking per-chunk and whole identity, then rehash its retained original. Run the standalone recovery CLI over the whole manifest once more and preserve that receipt separately. The parent will independently check complete byte transport and corruption controls; this producer's identity checks are not independent approval.

Bounded streaming memory is one8MiB chunk plus gzip buffers; no whole proof is loaded. All215 files form a finite transport task with no search. Failure stops and preserves outputs; no deletion or automatic retry. No CNF/model/native/checker/source/ledger/index/Git mutation. Availability remains LOCAL_ONLY until public publication is observed. Restore files only by exclusive creation in a new directory.

Commands with UV_PROJECT_ENVIRONMENT=build/research-venv:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_seven_profile_proofs.py --proof-gate EXACT_GATE --proof-gate-sha256 EXACT_SHA --out acceleration/results/20260930_hadamard_seven_profile_proof_package`

`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_seven_profile_proofs.py --manifest acceleration/results/20260930_hadamard_seven_profile_proof_package/package_manifest.json --manifest-sha256 EXACT_MANIFEST_SHA --verify-only`

For literal restoration, replace --verify-only with --out NEW_DIRECTORY. Optional --profile-id selects exactly one rank5_* profile. This restores exact bytes, not a proof of UNSAT by itself.
