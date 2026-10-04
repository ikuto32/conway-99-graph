# Native source-only review of Root's V20 eleven-copy checker

Reviewed the entire 228-line checker `audit_20261004_registrar_v20_eleven_copy_v1.py` (SHA256 `067bfc4966a35b946bb348065fbd322da00ea285bc89eb865b95d39f78f130fd`), its complete spec `cd667b25976e8830c0134d40fa012eaaded3940ec55cf05d0725f6e4ec3f8133`, and literal plan `bfae1b193c22e377511d33952a668467255201262340e35e766a17f4e1a504f3`. This was written inspection only: no checker import, syntax test, protected-copy invocation, registrar invocation, mathematical replay, or ledger/index/Git write.

## Material veto: success closes before deadline-sensitive work ends

After `protected()` at line207, lines208..218 serialize projection, controls and PASS summary without a closing `reserve()`. The final raw ledger/index reads and index hash at line224 also have no deadline check, and that final predicate omits HEAD. The last sampled deadline can therefore precede a slow write or final read; the worker can return0 despite failing its declared remaining-time criterion. Supported outer containment does not establish that the worker's own success criterion was met.

The final predicate also runs outside the `except` failure-record path. If it fails after summary serialization, the PASS summary may coexist with an unsuccessful worker and no saved failure record. Actual supervisor exit remains decisive; the summary alone must not be treated as an accepted gate.

Preserve V1 source/spec/plan unexecuted. A narrow new version should guard success serialization, close deadline/protected ledger/index/HEAD checks after it, and route a closing failure through the saved failure record. No deadline extension, invocation retry, generic hard-real-time theorem, or new mathematical controls follows from this source review. The final observed elapsed/contained terminal must still be checked after any future authorized execution.

## Barrier and frozen projection reconstruction

The unchanged pinned V20 main has exactly one `os.replace`, at line2187: source `dest/CLAIMS.pending.yaml`, target `ROOT/CLAIMS.yaml`. The local `report` exists at that point. Its prior before/after/pending YAML and validation writes are under the fresh destination. The checker authenticates and executes that actual main, replaces only the subject digest function, and raises the dedicated exception before replacement. The exact expected exception path therefore prevents the intended live ledger write. This review relies on the separately source-qualified frozen main, rather than asserting that monkeypatching protects arbitrary other programs or filesystem operations.

The typed recursive comparison distinguishes Boolean and integer revisions, checks all389 old claim records and every old artifact prefix, checks all other root fields except updated_at, checks eleven new claims/400 total, and compares exact descriptor scopes/dependencies and binding statement/status/roles/time. The immutable eleven-record list and binding list both have length11 and order1..11, so the projection's zip consumes the whole actual appended claim population.

All eleven frozen bindings have no extra `artifacts` or `evidence` collections. The unchanged main constructs each new evidence list from the sorted binding/report/input map and creates precisely the corresponding LOCAL_ONLY artifacts and verification hashes. The checker reconstructs that expected path/hash map independently and checks every referenced evidence entry. It does not reapprove the mathematics inside those reports.

Predicate limitation: outside this unchanged-main scope, it does not explicitly reject an unused extra appended artifact or an extra verification.artifact_hashes key. The actual frozen main does not produce those extras, as its append loop constructs one artifact per evidence path and one matching hash per entry. Either preserve this exact-source limitation or add explicit key-set/appended-union checks in the new version; do not claim general rejection coverage from the55 controls.

## Controls and literal containment

For each of eleven output claims, the five mutations reach their declared predicates: broadened statement, Boolean revision and UNKNOWN status reach NEW_CLAIM fields; empty scope reaches NEW_SCOPE; fictitious dependency reaches NEW_DEPENDENCIES. The loop thus declares55 distinct predicate cases. Their exact stages depend on the pristine projection first passing; a failure is preserved rather than reclassified as graph evidence. They do not exercise the write barrier, every source branch, or every filesystem failure under corruption.

The plan has identical command/supervisor arrays of45 words, a29-word child suffix and23-word worker suffix. The supported Windows593 supervisor precedes locked offline UV. The literal allocation is600 outer/550 worker/20 save/20 shutdown, with UV_PROJECT_ENVIRONMENT fixed. Preprocessing, complete inherited metadata hashes, main/schema serialization, copied outputs and55 controls share that worker deadline. Source/math identity dependencies are distinct from protected current HEAD28742325, ledgerb7d07a8b and indexe411963d observations. No actual launch or cleanup evidence is supplied by this written review.

## Decision

V1 is held for the closing deadline/protected-context defect. No additional material barrier or exact-frozen-projection defect was found in the inspected scope. Root authored this checker; Native independently inspected it and the relevant unchanged main/write path. Existing registry YAML/schema logic and prior source qualification remain disclosed common components. This is an engineering source review, not independent mathematical approval, execution approval, ledger registration, availability promotion, or a target result.
