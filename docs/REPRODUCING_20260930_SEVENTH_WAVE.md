# Seventh milestone: fixed triangle proofs and local checks

The [ledger snapshot](../acceleration/results/20260930_resume/claims_at_seventh_milestone.yaml)
and [checkpoint](../acceleration/results/20260930_resume/seventh_milestone_checkpoint.json)
describe ten newly checked claims. Neither fixed-family UNSAT result proves
unrestricted Conway-99 nonexistence. No target automorphism is assumed.

Use the existing repository and its pinned submodules. Preserve historical
commands and frozen evidence bytes. The root environment remains Python 3.12
with the unchanged `uv.lock`:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/reconstruct_20260930_triangle_artifacts.py recover --include-bodies --report build/seventh-triangle-recovery.json
```

Choose a new report path. This restores the two exact raw CNFs, two raw models
and two clause bodies from the checked gzip packages. Existing identical raw
files are accepted; conflicting bytes are refused. `--out-root` selects a fresh
recovery root if desired. Parts, raw hashes, byte counts and the body recipes
are in the [artifact catalog](../acceleration/results/20260930_seventh_artifact_packaging/catalog.json).
The [recovery calibration](../acceleration/results/20260930_independent_review/seventh_triangle_recovery_calibration/summary.json)
checked fresh restoration, repeated identical outputs, and six corruptions.
Recovery is byte checking, not mathematical verification.

## Complete fixed-family proof replay

| Fixed input | Exact CNF SHA256 | Complete proof SHA256 |
| --- | --- | --- |
| Wave154 | `4b9c05bb01ac76340c6f72e314c4ee84317facb687e9a32a79094f6fce85d8ea` | `8e0f01ddc42ad6a6f5baf84115ee16ab4034042e2344e26d6304070dbd2a087f` |
| Wave151 | `24d6b14e08fcd10f390edf462f75a6bc160c91c863448adf72d076f2297fc27e` | `e53deda5d5b10b29b800481f9a7497034b7e8b08e023dea42a44f3863ad6384b` |

The raw proofs are small and included directly at
`acceleration/results/20260930_triangle_native_pilot/main/proof.drat` and
`acceleration/results/20260930_wave151_triangle_native_pilot/main/proof.drat`.
They are complete proofs, unlike the previous wave's incomplete timeout traces.

The [Wave154 replay](../acceleration/results/20260930_independent_review/triangle_wave154_unsat/summary.json)
and [Wave151 replay](../acceleration/results/20260930_independent_review/triangle_wave151_unsat/summary.json)
preserve exact commands, input/output hashes, checker provenance, positive and
corrupt controls, logs and successful returns. The checker was authenticated
against upstream commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`; only the
explicit Windows portability block differed. The preserved prior MSVC build was
reused, not independently recompiled during these checks. Its executable is
LOCAL_ONLY; [build instructions](REPRODUCING_20260930_FOURTH_WAVE.md) and source
provenance are public.

A fresh Linux/WSL replay can build the unmodified pinned upstream checker in a
new directory, then check the two mathematical artifacts directly:

```sh
git clone https://github.com/marijnheule/drat-trim.git build/seventh-drat-replay-source
git -C build/seventh-drat-replay-source checkout --detach 2e3b2dc0ecf938addbd779d42877b6ed69d9a985
make -C build/seventh-drat-replay-source
build/seventh-drat-replay-source/drat-trim acceleration/results/20260930_triangle_full99_cnf/instance.cnf acceleration/results/20260930_triangle_native_pilot/main/proof.drat
build/seventh-drat-replay-source/drat-trim acceleration/results/20260930_triangle_wave151_full99_cnf/instance.cnf acceleration/results/20260930_wave151_triangle_native_pilot/main/proof.drat
```

These are instructions for a new replay, not a claim that this particular Linux
build was executed in the recorded milestone. Preserve its actual compiler,
binary hash, commands and logs in a new receipt. Do not change old expected
hashes to fit a new executable. DRAT acceptance establishes only UNSAT of the
exact CNF; the scope and encoding dependencies below are also necessary.

## Scope and independent encoding

The immutable archive is `external_conway99_research` at commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`. The
[propagation audit](../acceleration/results/20260930_independent_review/triangle_q1_partial99/summary.json)
freshly reconstructs both initial partial matrices from its factors and checks
every forced assignment. It does not import historical VERIFIED labels or
untraced historical UNSAT claims.

Separate [Wave154 encoding](../acceleration/results/20260930_independent_review/triangle_full99_cnf/summary.json)
and [Wave151 encoding](../acceleration/results/20260930_independent_review/wave151_triangle_full99_cnf/summary.json)
audits reconstruct every clause and variable of each exact fixed-family
completion instance. Each has 99 degree equalities and 4,851 exact pair
equalities. Shared independent truth-table checking helpers are disclosed.
The equivalences establish no universal containment of these fixed factors.

To repeat a frozen auditor, use its saved `command` with a fresh `--out` path
after restoring all inputs. In the original authenticated Windows environment:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_triangle_wave154_unsat.py --out build/seventh-wave154-proof-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_triangle_wave151_unsat.py --out build/seventh-wave151-proof-recheck
```

These strict auditors intentionally require the original preserved tool and
input hashes. A different platform/build needs its own truthful receipt rather
than silently edited pins. Repetition of an existing auditor is not a new
independent implementation or external review.

The native runs used pristine CaDiCaL 1.9.5 commit
`146207318796f094dcded87349a64f0c6927309e`, with a single 300-second / one-million
conflict cap per configuration, 4 GiB address-space and 10 GiB file limits.
Both returned native exit 20 before the limits. The solver is not trusted for
the exclusion: the complete proof is independently checked. Exact launch
commands are in the two run manifests; no solver rerun is needed for replay.
Dedicated SAT object checkers were calibrated before either launch; their
synthetic full-size controls are not target graphs. No research SAT model was
produced.

## Local results and continuation

The [single-star audit](../acceleration/results/20260930_independent_review/unrestricted_star_matching/summary.json)
contains the universal derivation and separates it from 128 sample controls.
The [joint audit](../acceleration/results/20260930_independent_review/joint_two_star_domains/summary.json)
checks all 32 raw local witnesses and independently enumerates all 244
individual domains. It does not certify simultaneous compatibility or replay
the capped coupled search as exhaustive.

The [36-literal audit](../acceleration/results/20260930_independent_review/two_star_empty_domain_cut_v2/summary.json)
checks all 460 row patterns and their exact contradictions. The
[transport audit](../acceleration/results/20260930_independent_review/nogood36_anchor_transport/summary.json)
checks all 192 specified maps, complete primary-variable permutations and clause
images. Recover the unrestricted base model using the fifth/sixth catalogs
before rerunning these auditors. Neither result closes an unrestricted branch.

Original failed attempts and corrected checking paths remain in their run
directories; do not overwrite or reclassify them as mathematical refutations.
The seventh checkpoint's next work is direct row-obstruction analysis and
broader triangle-core classification. Newly completed results after that
checkpoint require separate ledger registration and verification. Overall
search coverage: UNKNOWN; no validated denominator.
