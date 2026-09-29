# Fifth and sixth resumed evidence replay

Start with [the sixth checkpoint](../acceleration/results/20260930_resume/sixth_milestone_checkpoint.json)
and [claim snapshot](../acceleration/results/20260930_resume/claims_at_sixth_milestone.yaml).
The root ledger is authoritative for subsequent changes. The pinned external
ledger remains historical. No target resolution is claimed.

Use the existing pinned root environment; do not rewrite historical commands:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B -m unittest discover -s acceleration -p test_validate_claims.py -v
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/validate_claims.py --hashes public
```

The validator explicitly distinguishes skipped local hashes and mathematical
proof replay. A passing schema check is not mathematical verification.
Version2 requires the exact published editorial review and its immutable
snapshot even when ordinary hashes are disabled. See [schema migration rules](CLAIMS_SCHEMA.md).
Do not rerun one-shot registrars or overwrite old checkpoints to replay research.

## Exact input recovery

The [fifth artifact catalog](../acceleration/results/20260930_resume/fifth_artifact_catalog.json)
and [sixth catalog](../acceleration/results/20260930_sixth_artifact_packaging/catalog.json)
give sizes, SHA256 identities, ordered gzip parts, and reconstruction recipes.
Concatenate each input's explicitly ordered `.gz.partNNN` files and decompress
once; compare the raw digest before use. The unrestricted base CNF is
`7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138`;
its model is `77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e`.
The intermediate `clauses.body` is exactly that CNF after its first LF-terminated
header line. The conditional eight-family input is separate and uses its own
`artifact_packages.json`; do not interchange the two encodings.

The equality producer's `rows.jsonl.gz` expands to its exact raw row record.
The equality suffix and four branch suffixes are small literal files. Once the
base input is recovered, this solver-independent helper reconstructs all four
strengthened inputs in a new output directory:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/reconstruct_20260930_strengthened_branches.py --recipes acceleration/results/20260930_four_branch_strengthened_preparation/recipes.json --out build/replay-strengthened-four --report build/replay-strengthened-four.json
```

Use a new output path on each replay. The saved
[reconstruction receipt](../acceleration/results/20260930_four_branch_strengthened_reconstruction/summary.json).
Its recipe replaces the base header, copies the whole original body, appends
the4,662 equality units, then the branch's four literals. All four outputs
have1,186,500 variables and4,141,120 clauses. Their complete hashes are in
[recipes.json](../acceleration/results/20260930_four_branch_strengthened_preparation/recipes.json).
The original four unstrengthened instances use only the branch suffixes and
their original recipes. No native binary is needed for reconstruction.

## Independent checks

Exact commands, working directories, source revisions, source hashes, and
shared trusted components are retained in each audit. Important starting points:

- [Unrestricted CNF equivalence](../acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json)
  and [unrestricted derivation](AUDIT_20260930_UNRESTRICTED_FULL99_ENCODING_DERIVATION.md).
- [Four-branch coverage](../acceleration/results/20260930_independent_review/unrestricted_four_branch_cover/summary.json),
  [equality entailment](../acceleration/results/20260930_independent_review/unrestricted_pair_equalities_v2/summary.json),
  and [complete composed-input check](../acceleration/results/20260930_independent_review/strengthened_four_branch_composition/summary.json).
- [Augmented SAT-object checker calibration](../acceleration/results/20260930_independent_review/strengthened_full99_sat_object_calibration/summary.json).
  Its synthetic positive controls are not a research SAT model. Any real native
  output must pass all assignment variables, all actual clauses, the exact99
  graph scope, and every integer identity entry through this separate path.
- [Modular theorem](../acceleration/results/20260930_independent_review/modular_rank_exact/theorem.json)
  and [22 explicit minor checks](../acceleration/results/20260930_independent_review/modular_rank_exact/summary.json).
  Bareiss determinant checks establish the stated lower bounds, not all
  producer-reported full ranks.
- [Migration veto](../acceleration/results/20260930_independent_review/editorial_migration_veto/summary.json),
  [correction history](../acceleration/results/20260930_editorial_migration_tooling/correction_v2.json),
  [independent corrected-checker review](../acceleration/results/20260930_independent_review/editorial_migration_corrected/summary.json),
  and [independent actual-transition check](../acceleration/results/20260930_independent_review/editorial_migration_applied/summary.json).
  Historical checker bytes are preserved in `rejected_v1` and veto snapshots;
  their original source-path hashes describe those historical versions.

Auditors commonly refuse an existing output directory. Replay into a fresh
checkout/output location following each saved command; do not edit frozen
expected digests to fit a different implementation. Where a path names a later
changed ledger or source, retrieve the exact preserved snapshot with the
recorded digest. Claim revisions and historical records remain distinct.

## Completed native attempts and restart

The pristine native solver is CaDiCaL1.9.5 commit
`146207318796f094dcded87349a64f0c6927309e`, built in existing Ubuntu24.04 WSL.
[Build provenance](../acceleration/results/20260930_native_cadical195_build/manifest.json)
and its source archive preserve the exact build; the executable is LOCAL_ONLY.
The separate authenticated DRAT checker build/source is documented in the
[fourth reproduction guide](REPRODUCING_20260930_FOURTH_WAVE.md). A newly built
binary must get new truthful calibration/provenance bindings; do not replace a
saved binary hash without review.

The [unbranched native pilot](../acceleration/results/20260930_unrestricted_native_pilot/manifest.json)
and [strengthened branch wave](../acceleration/results/20260930_strengthened_four_branch_native_pilot/manifest.json)
save exact launch commands. The latter ran two branches concurrently, then two
more, with300seconds, one million conflicts,4GiB address space, and10GiB output
file limits per process. Proof output went to ext4 and was copied with exact
hash checks. All four returned timeout124; the unbranched pilot also timed out.
All five are UNKNOWN and have no complete proof or SAT model. Raw partial
traces are retained locally with hashes and reasons in the
[partial trace catalog](../acceleration/results/20260930_resume/sixth_native_partial_trace_catalog.json).
They are not UNSAT certificates and are not required evidence for an exclusion.

To intentionally rerun the same bounded wave, replay its manifest command with
a fresh `--out` directory after recovering inputs, rebuilding/calibrating local
binaries, and checking every gate. That is a retry, not four additional distinct
instances or guaranteed progress. The next research action is the triangle-factor
finite-field falsification and joint-neighborhood compatibility work recorded in
the sixth checkpoint. No auto-resume process is implied by this document.
