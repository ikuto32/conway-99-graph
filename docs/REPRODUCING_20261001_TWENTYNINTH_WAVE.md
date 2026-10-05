# Reproducing the twenty-ninth milestone

Read the [frozen milestone](RESEARCH_20261001_TWENTYNINTH_WAVE.md) and
[checkpoint](../acceleration/results/20261001_resume/twentyninth_milestone_checkpoint.json).
The cutoff contains 300 claims: 293 VERIFIED/CLEAR, three CANDIDATE/CLEAR and
four REFUTED/CLEAR. Batch03 and later allocations are outside this milestone.
No target graph, whole-support exclusion or general nonexistence proof is claimed.

Use the existing repository and pinned submodules. The
[preceding replay guide](REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md) documents
the prior evidence chain. Preserve original commands and environments; for new
PowerShell invocations at the repository root, set up the retained lockfile:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

Recorded versions include Python 3.12.10, uv 0.11.25, PyYAML 6.0.2,
jsonschema 4.23.0 and tqdm 4.67.1. The run manifests bind the lockfile, project
configuration and all scientific sources. Complete proof checks use the recorded
drat-trim source, portability patch, compiler and binary. A changed checker or
environment requires a new documented calibration; do not replace historical
hashes. Original CaDiCaL 1.9.5 runs retain their seed, time, conflict, memory and
proof-size settings in their exact manifests.

The [normalized recovery manifest](../acceleration/results/20261001_twentyninth_raw_recovery/manifest.json)
binds 128 oversized raw models containing 1,444,495,608 bytes to 128 compressed
streams. Raw originals remain LOCAL_ONLY; the exact gzip streams are the public
retrieval form when the evidence commit is published. Recover the originals
after obtaining those streams:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20261001_twentyninth_raw_artifacts.py --manifest acceleration/results/20261001_twentyninth_raw_recovery/manifest.json --manifest-sha256 0db330b0207414345bea0cfbd957219d3f93e1dc10d91d0aab4f37e58f2e3f11 --receipt build/research-local/wave29-recovery-receipt.json
```

The restorer rejects conflicting existing files and checks every length, offset
and hash. `--destination-dir` selects a separate tree; `--verify-only` checks
compressed streams without creating missing originals. The actual
[fresh recovery receipt](../acceleration/results/20261001_twentyninth_recovery_controls/fresh_recovery.json)
records all 128 restored originals, and
[seven corrupted controls](../acceleration/results/20261001_twentyninth_recovery_controls/summary.json)
were rejected. The normalizer compared every decompressed byte with its original.
Earlier oversized inputs still require their preceding-wave recovery instructions.
All 128 new complete proof files fit the individual 10 MiB publication limit and
are retained directly. Recovery is not mathematical verification.

The [authenticated replay plan](../acceleration/results/20261001_resume/twentyninth_replay_plan.json)
contains eight original command vectors and fresh-output equivalents. It changes
only the interpreter location/`-B` option and output directory. Run a selected
`replay_command` as an argument array under the locked environment; check its
actual summary against `expected_status`. Keep all failures and partial outputs,
use a fresh output root, and never overwrite original evidence.

| Check | Original executed record |
| --- | --- |
| First next64 formulas, domains and exact prior-60 skip set | [Encoding audit](../acceleration/results/20260930_independent_review/exact_eight_next64_cnfs_v3/summary.json) |
| First next64 object controls and source closure | [Object calibration](../acceleration/results/20260930_independent_review/exact_eight_next64_object_calibration/summary.json) |
| First next64 complete retained proofs | [Proof replay](../acceleration/results/20260930_independent_review/exact_eight_next64_proofs/summary.json) |
| Batch02 formulas, domains and exact prior-124 skip set | [Encoding audit](../acceleration/results/20261001_independent_review/exact_eight_prefix64_batch02_cnfs_v3/summary.json) |
| Batch02 object controls and source closure | [Object calibration](../acceleration/results/20261001_independent_review/exact_eight_prefix64_batch02_object_calibration/summary.json) |
| Batch02 complete retained proofs | [Proof replay](../acceleration/results/20261001_independent_review/exact_eight_prefix64_batch02_proofs/summary.json) |
| Sixteen literal affine Gram witnesses over GF(3) | [Literal-weight audit](../acceleration/results/20260930_independent_review/sizeclass16_gf3_affine_weights/summary.json) |
| All 792 uniform-mixture counterexamples | [Independent rational audit](../acceleration/results/20261001_independent_review/exact_eight_uniform_gram/summary.json) |

Each proof audit checks 64 complete traces. These are fixed-support necessary
Gram instances with complete initial local domains and within-triplicate caps;
they omit cross-group caps and the residual graph. UNSAT therefore excludes the
specified literal count profile only. The combined five-batch union has 188
distinct literal cases from the frozen 792. The separately checked first-12
labelled-image union remains 72 tables; no sixfold expansion of later cases is
silently added.

The GF(3) checker recomputes weighted incidence-column outer products. Its 16
witnesses satisfy all 20,736 Gram residues and 320 affine normalizations, but do
not verify the producer's rank assertion or provide integral factors. The uniform
checker independently rebuilds the local catalogue and all 15,840 group domains,
then checks one explicit rational mismatch for each of 792 profiles. It does not
check every reported differing entry or the earliest differing position. Unequal
convex weights and LP feasibility are not settled by that diagnostic.

The [suspended-launch engineering audit](../acceleration/results/20260930_independent_review/four_serial_build_engineering/summary.json)
records finite positive and failure controls for the replacement launcher. Each
actual four-part build has separate deadline, root-reaping and empty-Job records.
These observations do not prove a universal operating-system containment or
real-time guarantee. Earlier launcher refutations remain preserved in wave28.

No fresh mathematical replay was performed solely for publication preparation.
The eight original successful audits are the verification records; the replay
plan checks command/source identities only. Registration scripts are historical
ledger transactions, not replay tools, and must not be rerun to inspect evidence.
Schema checks, CI, metadata audits and file recovery do not prove mathematics.
Prior missing artifacts and the documented privacy omission retain their recorded
limitations.
