# Twenty-seventh wave: literal proofs and complete necessary diagnostics

Read the [milestone](RESEARCH_20260930_TWENTYSEVENTH_WAVE.md) and its frozen
286-claim ledger. Eight scoped additions are VERIFIED/CLEAR. The first12
campaign instances have complete independently replayed UNSAT proofs. They
exclude literal count profiles on one fixed support; one repeats the preceding
single pilot. No unrestricted target graph or nonexistence proof is supplied.

Use the existing checkout and locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

Recorded versions are Python3.12.10, uv0.11.25, NumPy2.5.3, SciPy1.18.1,
highspy1.15.1, PyYAML6.0.2, jsonschema4.23.0 and tqdm4.67.1. The lockfile
SHA256 is `a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db`.
Original commands, source commits, source hashes and working directories remain
in each saved run. Do not rerun one-shot registrars or checkpoint writers.

Recover prior dependencies using the [wave26 guide](REPRODUCING_20260930_TWENTYSIXTH_WAVE.md)
and its linked earlier guides. Wave27 adds14 oversized originals totaling
158,441,925 bytes, recoverable from14 public gzip streams. Thirteen are models;
the other is the complete domain-inventory record. All13 complete solver traces
(one pilot plus twelve campaign attempts) are individually below10MiB and are
retained directly. The pilot and campaign case0 overlap mathematically.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentyseventh_raw_artifacts.py --manifest acceleration/results/20260930_twentyseventh_raw_recovery/manifest.json --manifest-sha256 d6d5e3933cd8294b4f4119c6ba495780a77cf19833ecb056598a863bbef11958 --receipt build/wave27-recovery.json
```

Use `--destination-dir build/fresh-wave27-recovery` for a separate tree or
`--verify-only` for streamed identity checks. The restorer refuses different
existing bytes and validates every part and whole-file hash. The saved
[fresh recovery receipt](../acceleration/results/20260930_twentyseventh_recovery_controls/fresh_recovery.json)
records actual reconstruction of all14 originals. Recovery checks identity,
not mathematics.

The audit replay wrapper authenticates ten original checker command vectors
and source hashes. It changes only the output directory and interpreter
invocation, using the same locked environment. It performs no native search;
complete retained proofs are replayed with the independent checker.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/replay_20260930_twentyseventh_audits.py --out build/research-local/wave27-audit-replay --plan-only
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/replay_20260930_twentyseventh_audits.py --out build/research-local/wave27-audit-replay
```

Choose a fresh directory if that path already exists. The
[saved plan](../acceleration/results/20260930_resume/twentyseventh_replay_plan.json)
contains the exact arguments. The ten checks cover the single-pilot encoding,
object calibration and complete proof; the three-profile kernel-option
diagnostic; all792 PSD certificates; first12 encodings and object calibration;
all792 fibre coverage; complete domain inventory; and all12 campaign proofs.
Every checker preserves its positive/corrupted controls and shared components.
Repeating these checkers is not a new independent implementation.

An actual fresh replay passed all ten checks. The
[completion receipt](../acceleration/results/20260930_twentyseventh_replay_validation/receipt.json)
copies the terminal reports and console logs. References inside those new
reports to fresh `build/research-local` artifacts remain LOCAL_ONLY. The
original independent reports and their bound original artifacts are the
authoritative public mathematical package.

The twelve campaign traces total56,815,018 bytes. Their exact CNF, scope, trace,
native receipt and replay-log hashes are in the
[complete proof audit](../acceleration/results/20260930_independent_review/exact_eight_first12_proofs/summary.json).
The native solver was CaDiCaL1.9.5, source
`146207318796f094dcded87349a64f0c6927309e`, binary SHA256
`021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7`.
Each attempt used explicit seed0,60 wall seconds,1,000,000 conflicts,4GiB
address space and256MiB proof-file limit. These are allocations, not measured
runtimes. The complete proof audit records actual outcomes and resources.

Independent replay uses drat-trim upstream
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, local binary SHA256
`23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac`.
On another platform, independently rebuild/calibrate the checker and record
its actual source, version, hash and controls. Do not alter historical pins
to portray a different build as the original. Historical ext4 temporary paths
are provenance; retained host proofs are the replay artifacts.

The complete PSD audit checks exact integer congruences for all792 canonical
survivors: R=3G-NN^T is positive semidefinite of rank22 in every case. No factor
feasibility follows. The kernel-option redundancy is restricted to three
historical profiles and removes zero of6,444 options. The coverage proof
transports all792 canonical profiles through six global fibre relabellings;
coverage by itself is not an exclusion. The inventory verifies all15,840
domains and16 size classes; dimensions of unbuilt formulas remain conditional
recipe estimates, distinct from the16 actually saved formula measurements.

Original failed inventory, coverage and native-wrapper preparations remain
with corrected versions and failure controls. The fixed support is not assumed
without loss of generality for the target. Cross-group column caps and residualD
are omitted from these Gram formulas. The next32 batch and any later checked
union belong to the next wave. Overall search coverage: UNKNOWN; no validated
denominator.
