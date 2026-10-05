# Wave41 raw-byte index V2 source-only review

As of 2026-10-03 03:06:21 UTC. Reviewer: `/root/checkpoint_audit`.
Subject author: ROOT. The reviewer authored the separate milestone generator;
this review therefore supplies engineering source falsification, not independent
approval of the reviewer's mathematical discoveries or generator output.

The entire V2 source/specification and exact V1-to-V2 textual diff were read.
V2 source SHA256 is
`686e3c383447195e65e2f5c200ec751fe1e5ac498e159a47b8a2259aa45c7e88`;
specification SHA256 is
`5fc6bdf1616079833ed1211229a27741e8b2f627c14ae8ed43a5d23fac114851`.
The original V1 static veto is preserved in
`audit_20261003_wave41_index_v1_review.md`, SHA256
`8cf93af4c63a742f85ba140cbfdb9f6580fe01dd78ac25548d09fbdc26229058`.
V1 remains an unexecuted historical source; it is not retrospectively approved.

V2 resolves the identified independence gap in the source. Every saved historical
document byte string must now equal `git show` of that document at literal
immutable commit `00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8`. Only then does the
helper check that prepared bytes retain that suffix and current bytes equal
prepared. Actual comparison uses byte strings, before any index operation.
There is no implicit EOL normalization or permissive fallback. A real mismatch
must be preserved and investigated rather than silently substituting a baseline.

The exact diff adds only the fixed context commit, the three-step helper,
one positive and three precise negative document controls, updated control
counts, and the actual four Git-blob comparisons. The namespace, raw member,
package omission, NUL, archived source, unrelated index/Gitlink, shadow and
application paths retain V1 logic. Only the already pinned old engineering
helpers are imported; no generator, old main or mathematical producer is called,
and no old globals are overridden.

On paper the new controls make two positives and 25 precise negatives in total.
A consistently altered old/prepared/current triple reaches
`BEFORE_DOCUMENT_GIT_BLOB`; an altered suffix reaches
`DOCUMENT_HISTORICAL_SUFFIX`; altered current bytes reach
`CURRENT_DOCUMENT_PREPARED_BYTES`. Exact stage comparisons remain mandatory.
These are static reachability checks, not executed controls.

Calibration and shadow/apply still compare the exact new source/spec identities.
Therefore identical status labels do not transfer a V1 gate to V2. ROOT must
perform fresh V2 calibration and independently examine its actual controls and
terminal receipt before actual shadow/application. Shadow is reversible and
does not approve commit, publication, availability or mathematics.

Review outcome: `V2_SOURCE_ONLY_NO_FURTHER_STATIC_VETO_FOUND`. No subject
calibration, actual manifest evaluation, staging/index mutation, mathematical
replay or execution approval was performed by this review. The actual historical
document comparisons, all raw member identities and Git filter behavior remain
for the separately authorized ROOT checking invocation.
