# Source-only review of the Wave41 transition checker V2

Reviewer: /root/structural. Timestamp: 2026-10-03T02:06:11+00:00.
Method: written source review only. No invocation, calibration, future actual
registration inspection, registry/index mutation or mathematical replay.

Entire reviewed source: acceleration/audit_20261003_wave41_transition_v2.py,
SHA256 477075dd88d4be588f10bd4d858298828b7d2dbc0ca2dbefedaa38ed6d858ef1.
Entire reviewed specification: acceleration/audit_20261003_wave41_transition_v2_spec.md,
SHA256 b78dd61767f26802458e0d5325dffce9a9907718867038f41668125bed4d9cec.
The imported Wave37 transition projection and Wave31 duplicate-key/ID parsing
implementations were also read for the boundaries used here. Their sharing is
explicit in the checker. Neither mathematical producer nor registrar is imported.

Outcome: no static veto found in the requested boundaries. This is not an
execution gate or an endorsement of the later actual transition.

## Control inventory and stage reachability

Manual source inventory gives one synthetic positive and 53 negatives: 32
mutations of the synthetic ledger, 15 raw-report mutations, five binding
mutations and one duplicate-YAML-key case. The negative handler accepts only
AuditError with exactly the recorded stage. KeyError, another exception, a
wrong-stage AuditError or acceptance cannot count as a successful corruption
control. No code was run to claim these controls passed.

The ledger mutations are applied to a fresh deep copy of the positive fixture.
Typed JSON equality checks the prior claim prefix and prior artifact prefix
before the imported projection. It distinguishes boolean/integer and
integer/float aliases. The new claim fields and dependency projections use the
same typed equality. Verification revision has an explicit type-is-int check.
Duplicate IDs are caught before projection; missing/unbound evidence, revision
hashes, controls and shared-component changes are checked by the imported
complete evidence projection. The two exact statement/method mappings are
separately compared using typed JSON equality.

The report mutators reach their declared field checks: report role/method fields
precede exact literal headline checking, and the status-specific C4/rank87 fields
are then compared with typed expected values. Adding the wrong headline field is
rejected by an explicit absence condition. Binding identity/role/statement/report
and proof-control-premise checks precede their corresponding rejection stages.
These are paper reachability checks, not successful runtime observations.

## Command and protected-state boundary

The expected registrar summary is [sys.executable, script, arguments]. CPython's
interpreter option -B is absent from sys.argv and therefore correctly absent from
the registrar's [sys.executable, *sys.argv] report. The actual supervisor child is
checked as [the same Python, -B, script, arguments]. These two representations
are consistent; deleting -B from the actual child or inserting it into the
registrar's reported arguments would fail the exact-array check.

Full mode requires all actual identities explicitly. Calibration does not read
the later registration summary, after-ledger or its supervisor receipts. The
full path binds the original baseline snapshot, checks the live after-ledger
identity and data equality, requires exact two-ID/dependency order and 358
claims, and authenticates the separately approved registrar engineering gate.
It observes the live ledger and index before/after without using them as payload
artifacts. Their unchanged hashes are required at completion.

## Scope and independence limits

All 356 old claims and artifacts are preserved as typed data, including existing
PUBLIC metadata. The new exact evidence closure remains LOCAL_ONLY. Both added
statements are necessary conditional results: neither produces a target graph
nor excludes any target. The zero binary kernel remains permitted.

The checker author also authored the metadata registrar. That relationship is
explicit, and separate ROOT engineering approval is required. The mathematics
was produced by Structural and independently checked by ROOT; this metadata
review does not repeat or promote those proofs. Source review, synthetic
calibration, actual impact checking and public availability remain separate
stages. Future successful execution must preserve its own command, versions,
input/output hashes, precise controls and contained terminal receipt.
