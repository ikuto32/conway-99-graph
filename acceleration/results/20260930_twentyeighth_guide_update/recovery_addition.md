Forty-seven oversized raw models have exact public gzip recovery streams.
Their [normalized manifest](../acceleration/results/20260930_twentyeighth_raw_recovery/manifest.json)
binds524,689,195 original bytes. The raw identities retain LOCAL_ONLY labels;
the compressed streams supply public retrieval once this evidence is published.
Recover them after obtaining the committed streams:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentyeighth_raw_artifacts.py --manifest acceleration/results/20260930_twentyeighth_raw_recovery/manifest.json --manifest-sha256 33b00a791e57a732a27d18061c52f1ac6b3e71d964d9bf03c1e986ae12c82c89 --receipt build/research-local/wave28-recovery-receipt.json
```

The helper refuses conflicting existing originals and checks all lengths,
offsets and hashes. Add `--destination-dir` for a fresh separate tree or
`--verify-only` for compressed-stream checking without restoring missing files.
The actual [fresh recovery receipt](../acceleration/results/20260930_twentyeighth_recovery_controls/fresh_recovery.json)
records47 complete restorations, and [seven corrupted controls](../acceleration/results/20260930_twentyeighth_recovery_controls/summary.json)
were rejected. The packaging checker also compared every decompressed byte to
its original. Earlier-wave originals needed by transitive audits are recovered
using their preceding guides; their recorded hashes and availability remain
unchanged. All48 new complete proof files fit the10MiB individual publication
limit and are retained directly. File recovery is not a proof check.

