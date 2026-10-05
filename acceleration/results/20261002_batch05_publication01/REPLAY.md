# Batch05 exact raw recovery

The published payload population is 936 exact gzip parts representing 934 raw
artifacts (1,127,340,761 bytes), including all64 proof/CNF/model/scope inputs.
Manifest SHA256: `95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329`.
Independent byte-recovery report:
`acceleration/results/20261002_independent_review/batch05_recovery01/summary.json`,
SHA256 `5e6f232f1f22e18988d7ff6c2042ba00109290e0912bdea6643d3e80651ce48f`.
This is engineering recovery, not a new mathematical replay or unrestricted
exclusion. Native platform binaries remain separately LOCAL_ONLY; historical
gate transitive evidence is not recursively repackaged.

The manifest references parts in package02, preserved package01, and the64
original model.json.gz files. Keep those literal paths after checkout. The
separately authored historical recovery implementation accepts this manifest
format. It verifies every compressed/raw part and whole original hash and size,
enforces offsets/decompression bounds, and never overwrites a mismatching file.

From the repository root on Windows, with uv available:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked
$taskPython=(Resolve-Path build/research-venv/Scripts/python.exe).Path
uv run --locked python acceleration/run_compute_command.py --seconds 600 --allocation-reason 'Recover the frozen1.13GB batch05 population; local complete byte audit took4s,600s allows fresh output IO and reserve' --success-criterion 'All934 exact raw identities restored into fresh destination' --verification-criterion 'Each compressed/raw part and original hash/size checked by separate historical recovery implementation; mathematical proof replay remains separate' --shutdown-reserve-seconds 10 --out build/batch05-recovery-supervision-v1 -- $taskPython acceleration/recover_20261001_twentyninth_raw_artifacts.py --manifest acceleration/results/20261002_batch05_raw_package02/manifest.json --manifest-sha256 95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329 --destination-dir build/batch05-recovered-v1 --receipt build/batch05-recovered-v1.receipt.json
```

Use fresh supervisor/destination/receipt paths for each separate invocation.
`--verify-only` streams without restoration. To restore missing originals into
the checkout for later proof/encoding replay, use `--destination-dir .`; existing
files must already match exact recorded identities. The complete independent
local recovery auditor also compares every recovered byte against authenticated
originals and tests11 corrupt controls, using a different decompressor/scorer
path. Its local run requires the separately disclosed tool identities.

Preserved failure records describe the initial missing-Python launcher and the
Windows progress-file replacement race. The v2 package explicitly authenticated
and reused344 completed v1 receipts, preserving all old bytes. No scientific
solver was launched by packaging. Every payload is below10MiB (largest1,556,867
bytes). Publication readiness is independent of actual Git/public availability;
the prepared staging list never stages or commits automatically.
