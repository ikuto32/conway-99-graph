# Independent triangle-path weight-five check V1

Prepared 2026-10-03 by /root/checkpoint_audit. New source; unexecuted at
preparation. This checks the frozen structural candidate from actual adjacency
and a separate universal inverse. No optimizer, native graph search, ledger,
index, documentation update, commit or publication is performed.

Sources are audit_20261003_triangle_image_weight5_v1.py and its new independent
core audit_20261003_triangle_image_weight5_core_v1.py. They import no producer
implementation. The written derivation is
audit_20261003_triangle_image_weight5_v1_proof.md, SHA
8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee.
Producer source ac8287ac4ca1cfc82f5b9042ac578900b5a4dec2fe13938d8a5adaeb96b60bbc,
producer spec aff76615bee6d7f2ae8a7c1aa0b52e9aa4701aaa00d21aadc845b758ca05ef78,
and candidate note f175e6803924056cbaee112f2430b010f21277cb5792d1ce104ed9cb6c9f60c4
are exact pins. The raw schema is read as a declared format, not used as a
calculation implementation.

## Statement and scope

For every finite simple graph in which each adjacent pair has exactly one
common neighbor, use its complete actual triangle family T, with incidence
counts r_v. The binary triangle-incidence image contains at least ceil(P/2)
distinct weight-five words, where
P=sum_t sum_{unordered {u,v} subset t}(r_u-1)(r_v-1).
The proof explicitly counts unordered paths, recovers the unique isolated
support vertex, and uses at most two perfect matchings of the remaining
four vertices. Nonadjacent common-neighbor counts are not a premise.

For the target, conditional arithmetic gives P=24948 and the lower count
12474; character orthogonality gives
sum_{w>0} A_w(12474-K5(w)) <= 71510670.
Neither a nonzero kernel nor a rank upper bound is assumed. These are
necessary bounds, not a target graph, exclusion, novelty or optimum.

## Pre-full calibration

ONE proposed supported local Windows invocation 60 seconds outer, 40 worker,
10 supervisor shutdown reserve. The worker reserves 20 seconds for saving.
The largest small graph has fifteen vertices/seven triangles; complete
kernel/weight-five character sums involve fewer than a million terms.
This allocation is chosen from that finite population, not a solver default.
No retries. ROOT reviews source and authorizes this separate command.

Exactly seven known graphs are reconstructed: single triangle, friendship
of seven triangles on fifteen points, intersecting pair plus disjoint
triangle, loose three-triangle chain, three disjoint triangles, loose
four-triangle cycle, rook9. All paths are found by exhaustively examining
unordered triples of actual triangles; the degree formula is checked
separately. Binary masks enumerate complete small image codes. Complete
ambient kernel words and all weight-five characters verify the sharp
constant and Krawtchouk sign. Rook must have18 paths/nine path images/nine
full-code weight-five words, each path fiber of size2. All three inverse
shapes must occur.

Exactly21 strict negatives: fifteen raw path/metadata corruptions listed
by the producer schema, Pasch/K7 missing-premise failures, Boolean pathcount,
floating exact formula, omitted zero-word character constant evaluated on
the actual rook enumerator, and a wrong-stage rejection harness. The
checker requires its own AuditError and the exact designated stage;
arbitrary exceptions cannot satisfy a control. JSON duplicate keys and
nonfinite literals are rejected; literal comparisons distinguish integers
from booleans and floats.

Calibration output status is
INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_V1_CALIBRATION_PASS. Producer outputs are
not checked by calibration. controls.json and calibration_fixtures.json
preserve exact outcomes. All source/env hashes and command/cwd/version are
saved. Ledger/index bytes are checked before/after but retained only as
historical protected execution observations, not immutable dependencies.

## Complete raw audit

After separate authorization, one fresh60outer/40worker/10shutdown command
uses unchanged calibrated code and complete calibration pins. It must receive
the exact calibration and producer-summary hashes. It authenticates the
producer's complete direct input/output closure, terminal Windows Job
receipt, stdout/stderr/manifest and source pins before approval.

It reconstructs all seven frozen adjacency fixtures from declared definitions,
then literally compares every actual triangle, all62 unordered three-triangle
combinations, all23 path records, all14 separate-fixture support fibers,
every inverse candidate matching/completion, all234 coefficient masks and
their complete image supports. Those stage populations overlap and are not
added into target progress. Full kernel character checks are separate exact
calculations, not floating-point guidance.

All fifteen saved corrupted inputs must reject at their own precise stages;
both actual missing-premise fixtures and every edge CN list are checked.
The three saved K7 paths must be distinct actual paths with one identical
five-set, explicitly falsifying a three-preimage extension outside the
edge-unique premise. The general proof is separately pinned; finite fixture
agreement alone is not a universal theorem proof.

Result status is INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS
only after complete raw checking. The saved statement, exact target rational
coefficients for all weights1..99, universal written audit, source/env/hash
closure, positive populations, actual corrupt-control outcomes and limitations
are preserved. No previous rank/kernel-weight interval or incidence count
claim is silently reused. A timeout or missing file gives no approval and
preserves failure.json; it is not a mathematical refutation.

## Proposed supported commands

Set UV_PROJECT_ENVIRONMENT=build/research-venv and use uv run --locked
--offline --cache-dir .uv-cache-20260917 python -B
acceleration/run_compute_command.py with the declared budgets, explicit
success/verification criteria, and fresh supervision outputs. Its child is
the absolute build/research-venv/Scripts/python.exe -B followed by the checker.

Calibration child:

    acceleration/audit_20261003_triangle_image_weight5_v1.py
    calibration --seconds40 --out <fresh-independent-calibration-output>

Full child:

    acceleration/audit_20261003_triangle_image_weight5_v1.py
    full --seconds40 --out <fresh-independent-full-output>
    --calibration <calibration-summary> --calibration-sha256 <exact-hash>
    --producer-summary-sha256 <exact-producer-summary-hash>

No command was launched by writing this specification. Keep ROOT publication
and registry mutations outside either checking invocation's protected interval.
