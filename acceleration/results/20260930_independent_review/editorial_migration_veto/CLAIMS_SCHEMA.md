# Current claim registry (schema versions 1 and 2)

The root `CLAIMS.yaml` is the authoritative entry point for current project
claims. It is a claim registry, not an execution log. The historical source is
`https://github.com/YesterdaysLemon/conway-99-research`, commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`, path `CLAIMS.yaml`.
Its existing IDs and labels remain untouched in `external_conway99_research`.
An archived VERIFIED label is not a new independent verification.

The machine schema is [claims.schema.json](claims.schema.json). The separate
semantic checker is [validate_claims.py](../acceleration/validate_claims.py).
Schema validation and a green CI badge are not mathematical verification.
Version 2 adds a narrowly authorized editorial migration record. Version 1
ledgers remain valid without migration; the unchanged version 1 schema is
preserved as [claims.schema.v1.json](claims.schema.v1.json), SHA-256
`3925277499e54e1233097cf4a5c059198f515a5a3335baf258600a9603960a6f`.

## Locked setup and checks

New tooling uses the root `pyproject.toml` and committed `uv.lock`. Install uv
0.11.25, then run from the repository root:

```text
uv sync --locked
uv run --locked python -B -m unittest discover -s acceleration -p test_validate_claims.py -v
uv run --locked python -B acceleration/validate_claims.py --hashes available --out build/claims-validation.json
uv run --locked python -B acceleration/validate_claims.py --hashes public --previous build/previous-CLAIMS.yaml
```

`--previous` takes an actual ledger saved from an immutable earlier commit.
It is not a synthesized reconstruction. CI compares with the PR base, previous
push commit, or parent commit when that commit contains a current ledger.
An initial migration has no prior root ledger; CI explicitly reports that skip.
Historical environments and recorded commands are preserved as historical
evidence; this setup does not rewrite them.

## Records and references

The top-level fields are `schema_version`, `updated_at`, `archives`, `artifacts`,
`claims`, and `target`. Version 2 also requires `editorial_migrations` (possibly
empty); version 1 forbids that field. All timestamps include a timezone. Unknown and inapplicable
values are explicit nulls with reasons, not invented commands, hashes, or people.

Each artifact has `id`, `path`, SHA-256 `sha256`, `availability`, `retrieval`, and
`unavailable_reason`. PUBLIC requires a path, digest, and retrieval instructions.
LOCAL_ONLY or MISSING requires a reason, including an explanation for null fields.
A historical known hash can remain when the artifact is missing. Paths are
relative to the repository root unless explicitly absolute for a local artifact.
Keep old artifact IDs and bytes; altered bytes get a new ID. A digest establishes
identity, not artifact availability or correctness. PUBLIC describes published
availability, not a future intent to publish.

Every claim contains one exact quantified statement and these fields:

- `id`, positive integer `revision`, `statement`, `kind`, `basis`, `status`,
  `review_state`, `created_at`, and `updated_at`.
- `scope`: `description`, boolean `unrestricted_target`, and `target_resolution`
  (`NONE`, `POSITIVE`, or `NEGATIVE`). A broadly applicable structural theorem may
  have `unrestricted_target: true` and `target_resolution: NONE`.
- `assumptions`, `limitations`, `dependencies`, `evidence`, and `verification`.
  Empty lists mean none recorded, not unknown facts silently supplied.
- `external_source`: null with `unknowns.external_source` explaining why, or
  `{archive_id, original_claim_id}` resolving to the immutable historical source.
- `reproducibility`: null with `unknowns.reproducibility` explaining why, or
  `{manifest: artifact_id}`. COMPUTED claims require a manifest in `evidence`.
- `unknowns`: a mapping from unavailable/inapplicable field names to reasons.

Kinds are `mathematical result`, `encoding`, `exclusion`, `construction`,
`literature finding`, and `empirical/engineering result`. Basis is a nonempty
selection of `CITED`, `DERIVED`, and `COMPUTED`; basis is not verification status.
Statuses are `UNKNOWN`, `CANDIDATE`, `VERIFIED`, and `REFUTED`. Review states are
`CLEAR`, `QUARANTINED`, and `NEEDS_RECHECK`.

Dependencies contain `id`, exact `revision`, and `relation`: `premise`,
`uses_result`, `derived_from`, `encoding_equivalence`, `coverage`, `normalization`,
or `verification_dependency`. Current dependencies resolve to a current ledger
entry at exactly that revision. To use an archived claim, import a small explicit
alias first, such as `legacy@85e705c:C-N3-001`; its source reference preserves the
original ID. The validator checks that ID against the pinned Git blob. Aliases
are unique per immutable source and do not import the entire historical ledger.

Active claims are audited first. Imported records start UNKNOWN or CANDIDATE
unless fresh, exact-scope independent evidence justifies promotion. A historical
status may be described in evidence/limitations, without representing it as a
new check. Never rewrite the submodule as part of migration.

## Reproducibility and independent checking

An immutable computational manifest must record the source commit, exact command
and working directory, relevant dependency and solver/checker versions, input and
output hashes, configuration, seeds where relevant, actual result, and scope and
limitations. Hardware and numerical settings are required when material. Missing
facts use null plus a reason. Record run-selection rules, acceptance thresholds,
resource limits, and deviations in the linked run protocol. This checker requires
the manifest reference and checks its digest; it does **not** interpret every
historical manifest dialect or establish that a manifest's contents are complete.
An independent reviewer must check those contents before claim promotion.

For literature claims, linked evidence records the exact source version,
theorem/section, access date, and what was checked. Literature-status findings
also state search date and coverage; they do not assert global openness.

Verification records contain `claim_revision`, `verifier`, `method`,
`command_or_audit`, `timestamp`, `outcome`, `scope`, `artifact_hashes`,
`shared_components`, `controls`, and `limitations`. Methods distinguish
`repeated_execution`, `independent_artifact_check`, `independent_derivation`, and
`external_review`. Version 2 also permits `editorial_impact_review`, only when
authenticated by the exact migration described below. Outcomes are `PASS`,
`FAIL`, or `INCONCLUSIVE`.
`artifact_hashes` maps artifact IDs to exact SHA-256 values. Every hashed artifact
must be registered; preserve older artifact identities when inputs change.
The verifier identity must be real and recorded, not inferred from agent agreement.

A CLEAR VERIFIED claim needs an independent PASS bound to its current revision;
a computed claim also needs a nonempty artifact-hash binding. Repeated producer
execution cannot promote a claim. These are necessary bookkeeping gates, not
proof that the checking path is independent or complete. The reviewer must inspect
shared code/trusted components, positive and corrupted controls where applicable,
and the exact scope. A discovering agent must not approve its own claim.
Historical checks remain even if availability later changes. Missing bytes do
not automatically refute an earlier exact statement, and prevent current replay.

A VERIFIED conditional implication may depend on an unestablished `premise`
when the condition remains explicit in `assumptions` and the statement. Other
dependencies of current VERIFIED uses must themselves be CLEAR VERIFIED. A
REFUTED claim requires evidence against its exact statement; a timeout or invalid
proof alone is not evidence that the statement is false.

SAT requires independent validation of the decoded object. A target-level
positive result requires the complete 99-vertex graph and exact SRG check.
UNSAT needs the exact instance, full proof trace, solver/checker versions and
hashes, and independent proof replay. Target-level nonexistence additionally
requires independent encoding equivalence and unrestricted coverage, including
normalizations, branches, and pruning. A complete finite shortlist exclusion
remains a finite exclusion. Floating-point scores and numerical zeros are not
certificates. Formal proofs disclose admissions and additional axioms.

## Impact review and migration

Material changes to statement, scope, assumptions, or kind require a new stable
ID. Preserve rejected arguments and original evidence. The conservative
`--previous` gate does not decide whether arbitrary edits are editorial. The
sole assumption-edit exception is the explicit, independently reviewed migration
below; other assumption edits still require a new stable ID.
Evidence/dependency changes increment the revision. Retain old verification
records with their original revision and hashes. An affected VERIFIED claim
remains out of current totals using NEEDS_RECHECK or QUARANTINED until review.

`--previous` rejects deleted claims, revision decreases, rewritten old checks,
and unchanged revisions with changed evidence/dependencies. Changed evidence
digests or dependency revisions propagate impact transitively. Retaining a CLEAR
VERIFIED label requires a fresh independent check on a new revision; otherwise
the claim must need rechecking. The gate does not automatically declare dependent
mathematical statements false. Changed source code or unrecorded assumptions
cannot be detected magically: register those artifacts/dependencies and conduct
impact review when they change.

A genuinely new downstream claim can start at revision 1 with its own independent
current-revision PASS. Its changed dependencies must resolve to correctly pinned,
CLEAR VERIFIED revisions with independent current-revision checks. It does not
need a fictitious earlier revision solely because its premises were just revised.

Future incompatible schema changes require a new schema version, explicit
migration documentation, and tests. Keep the old ledger in Git; do not silently
relabel its historical checks or change archived IDs.

### Version 2 editorial migration

This exception clarifies that no nontrivial target automorphism is **assumed**;
it does not impose target asymmetry. It authorizes exactly the 17 claim edits
in the [independent editorial review](../acceleration/results/20260930_independent_review/automorphism_assumption_editorial/summary.json),
SHA-256 `1584c3c0ef52fdee47c056fec317260d6952fdbd46a9e47e0742ce1f6d711388`.
Its immutable [reviewed ledger snapshot](../acceleration/results/20260930_independent_review/automorphism_assumption_editorial/CLAIMS.reviewed.yaml)
has SHA-256 `20b3ee7d9c13c5142205492832a85ba877f35492ab26c0db1fdd5e3b9ba7e168`.
Those hashes and the exact review identity, status, and population are an explicit
allowlist in the checker. A reviewer name, PASS label, or replacement report
with a newly calculated hash cannot authorize another migration. Supporting
another review requires a separately reviewed checker change.

An operator applies the reviewed correction explicitly; the validator does not
edit claims or generate reviews. Register both immutable artifacts and add one
record of this form (the actual record must include all 17 approved members):

```yaml
schema_version: 2
editorial_migrations:
  - id: M-AUTOMORPHISM-ASSUMPTION-CLARIFICATION-20260930
    version: 1
    kind: REVIEWED_ASSUMPTION_CLARIFICATION
    review_artifact:
      artifact: registered-review-artifact-id
      sha256: 1584c3c0ef52fdee47c056fec317260d6952fdbd46a9e47e0742ce1f6d711388
    snapshot_artifact:
      artifact: registered-snapshot-artifact-id
      sha256: 20b3ee7d9c13c5142205492832a85ba877f35492ab26c0db1fdd5e3b9ba7e168
    claims:
      - claim_id: approved-claim-id
        from_revision: 1
        to_revision: 2
        old_claim_sha256: exact-canonical-old-claim-digest
        old_assumptions: [exact, original, list]
        new_assumptions: [exact, approved, list]
```

`old_claim_sha256` uses UTF-8 JSON with sorted keys and separators `(',', ':')`,
with Python's default ASCII escaping, as in the immutable review. Authentication
checks the full old claim against that snapshot and its digest, the exact old
and approved new assumptions, unchanged statement/scope/kind, and a single
revision increment. All original evidence and verification records survive.
The initial correction may otherwise change only `updated_at`, append the two
migration evidence references and verification, and update existing dependency
revision pins. It cannot add/remove premises, change their relation, alter
status/review state, or change unrelated claim fields under this exception.
The current full old claim must equal the reviewed snapshot at the initial
transition; a later intervening revision requires new review, not reuse of
this exception. Migration records themselves cannot later be deleted or rewritten.

Every migrated claim appends an `editorial_impact_review` PASS bound to revision
2, the original review's verifier, the exact unchanged scope description, the
review path as `command_or_audit`, and both registered artifact hashes. The
validator requires that review's actual bytes and the snapshot bytes locally,
including under `--hashes none` and `--hashes public`. The review is an impact
assessment of wording and existing bound audits; it does not rerun mathematics.
Historical revision 1 records remain revision 1 records. Later evidence revisions
still require their own current-revision independent checks.

Ordinary dependency impact rules remain in force. Compute the complete affected
closure, update exact pins, and separately review non-editorial affected claims
or mark them NEEDS_RECHECK/QUARANTINED. An editorial review cannot establish an
unreviewed prerequisite, clear a dependent quarantine, or automatically promote
the whole closure. For example, the changed local-witness claim affects its
separate dual-Gram exclusion, which is then a prerequisite of the reviewed
43-literal box-cut claim; that exclusion needs its own dependency impact review
before the cut can remain CLEAR. The migration only allows the exact wording
correction to retain the prior mathematical scope and evidence.

## Public replay and progress

`--hashes public` checks all PUBLIC bytes and explicitly skips LOCAL_ONLY and
MISSING artifacts. `--hashes available` also checks available local artifacts and
reports absent local artifacts as skipped. PUBLIC missing bytes and any checked
hash mismatch are fatal. `--hashes none` is syntax/semantic bookkeeping only and
explicitly lists skipped hashes, except the mandatory migration review/snapshot
authentication described above. No mode silently downloads artifacts. Retrieve
PUBLIC artifacts using their recorded instructions before validating.

JSON output separates errors, checked digests, skipped work, and progress.
Saved `--out` reports are created exclusively; an existing file is never
overwritten. Choose a new timestamped report path for each run. Provenance binds
the UTC timestamp, source commit and dirty state, exact command argv and working
directory, tool versions, and ledger/schema/checker/previous-ledger hashes.
Expensive mathematical replay/proof checking and independent-review audits are
explicitly not performed by this command. CI uploads this output even on failure.

Progress counts current claim records, not candidates, graphs, experiments, or
branches. Current VERIFIED totals exclude QUARANTINED and NEEDS_RECHECK records.
`progress.trusted` is false whenever ledger validation fails; any displayed counts
then serve only as diagnostics and must not be published as verified progress.
True means the bookkeeping checks passed, not that mathematics was reverified.
The target object independently records UNKNOWN or an internally verified
CANDIDATE_POSITIVE/CANDIDATE_NEGATIVE resolution pending external review. It
cannot be promoted from a finite exclusion. `external_review` states the actual
review state separately. Neither schema version has a justified target-wide denominator:
`overall_search_coverage` remains null with `coverage_reason`.

The summary says: "Overall search coverage: UNKNOWN; no validated denominator."
It reports execution state UNKNOWN because a ledger read cannot establish live
process state. Experiment-stage counts and live observations come from the saved
run records and actual process checks, not ledger length or narrative confidence.
