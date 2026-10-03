# Independent fifteen-proof transport audit

This audit checks identity, not an additional mathematical exclusion. The fifteen complete DRAT traces were already independently replayed by the frozen `hadamard_fifteen_profile_unsat_v2` review. The exact manifest, every original trace, every compressed part, every native case summary and each corresponding CNF are bound in the new report.

The checker does not import the packager, recovery helper, solver or proof checker. It separately decompresses each complete gzip part, checks its declared raw hash and length, compares every byte with the corresponding contiguous portion of the original proof, and computes a whole-proof hash while concatenating the raw chunks. It requires sequential indices, contiguous offsets, unique safe relative paths, all fifteen prescribed cases, and every compressed part strictly below 10 MiB. The shared standard-library gzip/zlib and SHA256 implementations are disclosed.

A synthetic two-part positive control and ten deliberate corruptions test compressed and raw hashes, changed bytes, order, omission, offsets, unsafe paths, changed originals and extra suffixes. The control trace is an engineering byte fixture, not a claimed mathematical proof.

Run from the repository root in the existing locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_four_profile_proof_transport.py --out acceleration/results/20260930_independent_review/hadamard_four_profile_proof_transport
```

Use a fresh output directory when replaying. To reconstruct an absent original, process each manifest record's parts in increasing index, independently decompress each gzip stream, concatenate their raw outputs, and require the recorded final raw size and SHA256. The repository's separately provided recovery CLI can perform that write; this audit performs no recovery write and never changes an original.
