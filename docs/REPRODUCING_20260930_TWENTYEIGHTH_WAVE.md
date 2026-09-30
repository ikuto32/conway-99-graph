# Reproducing the twenty-eighth milestone

Read the [frozen milestone](RESEARCH_20260930_TWENTYEIGHTH_WAVE.md) and
[checkpoint](../acceleration/results/20260930_resume/twentyeighth_milestone_checkpoint.json).
The authoritative cutoff has294 claims:287 VERIFIED/CLEAR, three CANDIDATE/CLEAR
and four REFUTED/CLEAR. The next64 allocation and replacement launcher are later
work. Nothing here establishes a99-vertex target graph or general nonexistence.

Use the existing repository, including its pinned submodules, and the locked
environment from [the preceding replay guide](REPRODUCING_20260930_TWENTYSEVENTH_WAVE.md).
Do not rewrite historical execution commands to use a different environment.
For new replay invocations in PowerShell at the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

The recorded versions include Python3.12.10, uv0.11.25, PyYAML6.0.2,
jsonschema4.23.0 and tqdm4.67.1. The lockfile and project hashes remain in each
run manifest. Full-proof checks use the previously documented drat-trim build
and its exact source, patch, compiler and binary provenance. Rebuilding or
substituting a checker requires a new recorded validation, not a silent hash
replacement. The original CaDiCaL1.9.5 executions use their saved seed0,
conflict, memory, time and proof limits.

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

The [authenticated replay plan](../acceleration/results/20260930_resume/twentyeighth_replay_plan.json)
contains eight exact original commands and corresponding fresh-output commands.
It changes only the interpreter location/`-B` option and `--out` destination.
Run an individual `replay_command` as an argument array under the locked
environment, using a fresh output root. Its `expected_status` must match the
actual new summary. Preserve nonzero exits, stderr and partial outputs. Never
overwrite the original evidence or resume a native search merely to inspect it.

| Check | Authoritative executed record |
| --- | --- |
| Next32 complete literal formulas and prior-proof selection | [Encoding audit](../acceleration/results/20260930_independent_review/exact_eight_next32_cnfs/summary.json) |
| Next32 decoded-object controls and bound source closure | [Object calibration](../acceleration/results/20260930_independent_review/exact_eight_next32_object_calibration/summary.json) |
| Next32 complete retained contradiction traces | [Proof audit](../acceleration/results/20260930_independent_review/exact_eight_next32_proofs/summary.json) |
| First12 six-image union and exact overlaps | [Fibre-union audit](../acceleration/results/20260930_independent_review/exact_eight_first12_union_v2/summary.json) |
| Sixteen size-class sample formulas and exact44-case skip set | [Encoding audit](../acceleration/results/20260930_independent_review/exact_eight_sizeclass16_cnfs_v2/summary.json) |
| Sizeclass16 decoded-object controls and bound source closure | [Object calibration](../acceleration/results/20260930_independent_review/exact_eight_sizeclass16_object_calibration/summary.json) |
| Sizeclass16 complete retained contradiction traces | [Proof audit](../acceleration/results/20260930_independent_review/exact_eight_sizeclass16_proofs/summary.json) |
| All792 residual-kernel identities and local projections | [Kernel audit](../acceleration/results/20260930_independent_review/exact_eight_kernel_redundancy/summary.json) |

The two proof audits replay32 and16 complete traces respectively. All inputs,
scope records, checker versions, outputs and positive/corrupted controls are
bound in their reports. Their domains omit cross-group column caps and residual
D; an UNSAT result excludes only its literal necessary instance. The separately
checked first12 image union contains72 labelled tables. It does not expand the
later48 literal exclusions to their fibre images. A size-class sample cannot
exclude every member of its size class.

The common-kernel diagnostic checks integer annihilation and an explicit
14-dimensional basis, using the prior independently checked rank22 certificates.
It does not rerun rank computation or establish integral factor feasibility.
All1,687,356 initial options pass its necessary local-projection test.

The initial next32 build was partial after22 formulas. Its exact10-case
continuation and32-case consolidation remain separate immutable records.
Completed native batches must not be rerun by registration, publication or
replay commands. Registration scripts mutate the ledger and are historical
transactions; use the frozen ledger and validation tools to inspect them.

The unused launcher v1 has two independently demonstrated engineering failures:
the [deterministic deadline counterexample](../acceleration/results/20260930_independent_review/parallel_build_deadline/summary.json)
and the [real pre-assignment containment race](../acceleration/results/20260930_independent_review/windows_job_assignment_race/summary.json).
The latter uses harmless owned processes and records their explicit cleanup.
Earlier successful timing samples remain preserved, but do not prove universal
containment. Neither record alleges an escaped historical research run.
The replacement launcher belongs to the following wave.

No fresh repeat of the eight already successful mathematical audits was run
during publication preparation. The replay plan authenticates commands and
source hashes; it is not an additional mathematical verification record.
Schema checks, file recovery and publication metadata checks likewise do not
establish mathematical correctness. Missing historical traces and the documented
privacy omission retain their earlier availability limits.
