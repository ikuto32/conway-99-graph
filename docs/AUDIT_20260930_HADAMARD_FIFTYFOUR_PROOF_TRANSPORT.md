# Independent 54-proof transport review

Freeze the package manifest, producer summary, standalone recovery receipt and
previous independent complete-proof report before execution. The finite
population is exactly the 54 proof streams already checked against their own
CNFs. This review checks transport identity only and does not rerun DRAT or a
SAT solver.

Use a new decoder built directly on `zlib.decompressobj(31)`, not the packaging
or recovery Python helper. Authenticate every compressed part, require one
complete gzip member with no trailing data, and compare every decompressed
byte with its corresponding range of the retained original proof. Verify
ordered indices, contiguous offsets, raw part sizes and hashes, whole sizes
and hashes, and all native summary/CNF identities against the prior proof
report. Reconstruct all 99 parts and all 555,334,934 raw bytes. Each gzip part
must be strictly below 10 MiB. The gzip/zlib implementation and SHA256 remain
shared trusted components and are disclosed.

Calibrate using a separately constructed multi-part positive fixture. Reject
missing, duplicated and reordered parts; invalid indices/offsets/lengths;
compressed, raw-part and whole hash mutations; path escape; truncated or
CRC-corrupted gzip; appended gzip members; and deliberately changed payload
with self-consistent metadata that disagrees with the authenticated original.
Preserve each corrupt manifest/payload and its exact rejection. Bind the saved
standalone recovery command/output without invoking its producer helper.

No existing artifact, ledger, Git index or publication metadata changes. New
reports describe local recoverability; public availability remains unasserted
until actual publication. A failed checker is preserved before correction.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fiftyfour_proof_transport.py --out acceleration/results/20260930_independent_review/hadamard_fiftyfour_proof_transport
```
