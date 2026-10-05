# Twenty-sixth wave: complete count census, necessary screens and literal proof

This wave enumerates the exactly-eight count population on one literal fixed
support and excludes 756 of its 1,548 global fibre classes by scalar bounds.
All 792 survivors pass separate block tests. One further literal profile is
excluded by a complete proof. No factor or unrestricted target resolution is
claimed. Read the [corrected milestone](RESEARCH_20260930_TWENTYSIXTH_WAVE_CORRECTED.md)
and its frozen ledger; the initial report is retained with its scope correction.

Use the existing checkout and pinned environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

Python 3.12.10 and uv 0.11.25 were recorded. Relevant locked packages include
NumPy 2.5.3, SciPy 1.18.1, highspy 1.15.1, PyYAML 6.0.2, jsonschema 4.23.0
and tqdm 4.67.1. The lockfile SHA256 is
`a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db`.
Actual commands, working directories, source commits, source hashes and
versions remain in each original manifest. Do not rerun one-shot registrars
or checkpoint writers. Fresh execution reports have new timestamps and need
not match old report hashes.

Recover prior dependencies with the [wave25 guide](REPRODUCING_20260930_TWENTYFIFTH_WAVE.md)
and its linked earlier guides. This wave adds two oversized originals totaling
23,119,778 bytes: the upper-envelope CNF and third-profile model. Three retained
gzip streams reconstruct them exactly. The restorer checks every stream and
whole-file hash and refuses to overwrite different bytes:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentysixth_raw_artifacts.py --manifest acceleration/results/20260930_twentysixth_raw_recovery/manifest.json --manifest-sha256 7f8f2c99a0ddd50fdb4fce9eaf4100240ecb19c4c6dbc6946b7e27cec29d6cd6 --receipt build/wave26-recovery.json
```

Use `--destination-dir build/fresh-wave26-recovery` for a separate tree or
`--verify-only` to check recovery without writing originals. The saved
[fresh recovery receipt](../acceleration/results/20260930_twentysixth_recovery_controls/fresh_recovery.json)
records actual reconstruction. Recovery verifies identity, not mathematics.

The replay wrapper extracts twelve original audit command vectors from their
bound reports/manifests, authenticates each checker source and changes only the
output directory and interpreter invocation. It does not rerun native searches.
Inspect the plan first, then use a fresh output directory:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/replay_20260930_twentysixth_audits.py --out build/research-local/wave26-audit-replay --plan-only
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/replay_20260930_twentysixth_audits.py --out build/research-local/wave26-audit-replay
```

The twelve commands cover the third-profile scalar/block diagnostic, full
encoding, object calibration, complete proof, upper-envelope encoding, forced
block identity, exact-eight subset preflight, complete count join, GF(3)
criterion, three-profile PSD check, scalar screen and block screen. The
[saved plan](../acceleration/results/20260930_resume/twentysixth_replay_plan.json)
contains their literal arguments. Each checker uses positive/corrupted controls;
shared components are disclosed in its report. Repeating these checkers is not
a new independent implementation. The wrapper saves per-audit completion and
stops on a failure; already completed historical evidence is never overwritten.

The third-profile proof is exactly 5,549,451 bytes, SHA256
`17d87b5ef8724d70d7809d8f9cb581afe720272a1633fde261767f90b035340c`.
Its CNF SHA256 is
`0f82ec4239be19f6ba3311b26a5d0f10b093c4aee0aff682dc68debe55d160a9`.
It proves only the literal profile in
`acceleration/results/20260930_eight_count_profile_lift_third/instance.cnf`.
The host trace is in
`acceleration/results/20260930_eight_count_profile_lift_third_native_pilot/main/proof.drat`.
The original native call used CaDiCaL 1.9.5, source commit
`146207318796f094dcded87349a64f0c6927309e`, with the recorded 60-second,
1,000,000-conflict, 4-GiB address-space and 10-GiB proof limits.

Independent replay uses the preserved drat-trim build from upstream
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, with binary SHA256
`23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac`.
The historical audit authenticates that local Windows executable. On another
platform, rebuild/calibrate the checker independently, record its source,
version, binary hash and controls, and replay the exact retained CNF/trace.
Do not edit historical pins to present a different build as the old one.
An earlier ext4 temporary path is historical metadata; the retained host trace
is the replay artifact.

The count census is independently reproduced through all 7,122,626 remaining
Cartesian assignments. The scalar screen checks all 1,548 canonical profiles
and all labelled fibre images. The block checker independently constructs
complete two-plus-three sum sets for 2,527 distinct problems and checks all
47,520 profile/block pairs. Its proof does not rely on the producer's dynamic
programming prefix states. Separate block witnesses may be incompatible with
each other; no simultaneous factor follows.

The exact PSD test covers only the three named historical profiles. The GF(3)
criterion concerns symmetric/hollow linear mixed completion with its recorded
consistency premises. Neither gives a binary integer quadratic residual graph.
The first/third proof-core, singleton and numerical LP diagnostics remain
exploratory; failed rational LP recovery is preserved and is not a certificate.

Continuation starts from the frozen 792-class survivor population, with the
next literal lift under independent encoding/object gates. Next-profile and
PSD-kernel experiments are later-wave work and are excluded from this report.
The active ledger remains authoritative. Overall search coverage: UNKNOWN;
no validated denominator.
