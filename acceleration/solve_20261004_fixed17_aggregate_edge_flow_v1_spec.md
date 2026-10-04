# Fixed17 coupled exterior edge-flow producer V1

This is a new source-only producer, authored by `/root/checkpoint_audit` from
Root's proposed coupled model. It has not been imported or executed. A finite
author calibration, distinct independent checker qualification, a concrete
scientific configuration, and one separate Root command authority are required
before the scientific invocation. Historical count, pair, capacity, and focal
gates do not approve this changed execution.

## Mathematical scope

Let H be the authenticated induced seventeen-point support and let T_i be the
authenticated exterior type masks with fixed nonnegative integer counts n_i.
The actual count witness has 472 ordered types, 82 exterior copies, and 68
positive classes. Zero-count classes are omitted canonically from this new
edge model, without filtering the positive support or assuming an equitable
per-copy neighborhood profile.

For each positive i <= j, e_ij counts unordered exterior edges between the
two classes; e_ii counts each same-class edge once. There are prospectively
68*69/2 = 2346 variables, including variables fixed to zero. Their capacities
are n_i*n_j off the diagonal and n_i*(n_i-1)/2 on the diagonal. If bit 1 is
absent from the authenticated necessary pair relation, the upper bound is
zero. If the sole bit is 1, both bounds equal the capacity. A pair with empty
bits and positive capacity is rejected before solver use. Empty diagonal bits
are allowed when capacity is zero: a singleton class contains no two distinct
same-type vertices.

Write t_i(u)=1 if u is in T_i. For each positive class, the exact necessary
rows are

    sum_(j != i) e_ij + 2 e_ii = n_i * (14 - |T_i|),

and, for every u in the support,

    sum_(j != i) t_j(u) e_ij + 2 t_i(u) e_ii
        = n_i * (2 - t_i(u) - sum_v H[u,v] t_i(v)).

The support formula is the columnwise sum of the independently established
block identity C X = 2 J - (H+I) C. A same-class edge has two endpoints and
therefore contributes exactly 2 to its degree row and 2*t_i(u) to its support
row. No individual vertex is required to have the average class profile.
The 68*(1+17) = 1224 rows are ordered by increasing original type index,
then its degree row followed by support indices 0..16. Sparse variable terms
are in canonical unordered-pair order and have literal integer coefficients
1 or 2. At most 2346*36 = 84456 nonzeros is a prospective upper bound, not an
observed model size.

An integer solution is a necessary aggregate relaxation only. It does not
construct an 82-copy adjacency matrix, enforce every pairwise common-neighbor
condition, or realize a 99-vertex graph. No local perfect-matching constraints
or additional pair-selection cuts are silently added. Numeric infeasibility,
timeout, solver bounds, or an absent candidate are UNKNOWN and do not exclude
this count witness or the target graph.

## Authenticated input and shared components

The ten explicit direct premises in the source include the previously verified
whole `parsed_screen_input.json` (468f281b...), exact integer count candidate
(133097b6...), Native count (37bcf42a...), pair (ee9fa896...), and capacity
(4f6711cb...) complete reports, the independent block theorem (910a740a...),
and their four literal Root acceptance records. The 468f profile's six fields
are target_order, target_degree, support_adjacency, ordered_masks, counts, and
pair_bits. The entire saved profile is reparsed with strict integer matrices,
strict increasing masks, all canonical i<=j pair rows, and allowed bits exactly
[], [0], [1], or [0,1]. The count candidate's masks and counts must equal it
with types retained. Native gate roles, methods, versions, and direct profile
and candidate bindings are checked. Root acceptance records are exact frozen
references, not a generic semantic approval parser.

This uses independently checked immutable data as a premise. It does not
regenerate old Gram inverses, revisit all raw pair parts, or recursively rehash
the earlier 575-input ancestor closure. The new configuration's explicitly
selected direct files and its fresh author-control packet are hashed inside
the new worker, and every directly read pin is freshly checked on closing.
Concurrent mutation of those bytes vetoes successful completion if observed;
this is not an atomic adversarial concurrency guarantee.

Pinned software is the unchanged CommandDeadline, supported local Windows593
supervisor, pyproject, uv.lock, and five installed highspy 1.15.1 interface,
extension, frontend, initialization, and metadata files. SELF and this spec
bring the source/software map to 11 files. Python, JSON, SHA, and NumPy/HiGHS
array conventions share the earlier tooling. The NumPy module path and version
are recorded but the entire NumPy package is not newly hash-qualified here.
The numerical API calls follow the installed pinned stubs and the historical
count producer. They must be exercised by new finite controls. No producer or
checker imports from the historical count, pair, capacity, or focal engines
are used.

## Native solve and candidate packet

All edge columns are integer, nonnegative, and capacity-bounded. HiGHS uses a
zero objective, seed 0, one thread, parallel off, presolve on, choose solver,
zero relative and absolute MIP gaps, and 1e-7 primal/MIP tolerance. One science
run is proposed with at most 1500 native seconds. Native time is finalized
after sparse construction and the before-solver checkpoint, as the lesser of
the configuration maximum and inclusive remaining worker time minus 180
seconds. Three tiny calibration runs each use at most five native seconds.
No internal retry or follow-on scientific call is allowed.

Raw guidance retains the exact float list, its hexadecimal spellings, whether
the native solution is value-valid, solver/model status strings, actual native
wall time, finalized options, and versions. These statuses are not proofs.
Extraction attempts nearest integers only when each value is within 1e-7;
the unrounded guidance is preserved independently. Every candidate capacity,
allowed-bit consequence, symmetric ordered-flow identity, even diagonal, and
all 1224 equations must then hold with exact Python integers before a candidate
is saved. This source's own exact check is not independent approval.

`aggregate_model.json` uses schema FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_MODEL_V1.
It contains positive_type_ids, canonical variable_pairs, variables, literal
lower/upper/capacities, all sparse rows, the complete original mask/count/H
objects, and explicit omission/diagonal/no-equitable/graph flags. Each row is
{kind,type_i,support_u,lower,upper,terms}; terms are [variable_index,coefficient].

`exact_integer_edge_flow.json`, when present, has exactly schema,
variable_pairs, edge_counts, and ordered_flow_matrix. Its schema is
FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_INTEGER_CANDIDATE_V1. The matrix uses
positive-type order, has e_ij off-diagonal and 2*e_ii on its diagonal.
`exact_flow_rows.json` records row ordinal, kind, type_i, support_u, lhs, and
rhs for every exact equation. `extraction.json` retains the full candidate and
own row check or an explicit absence reason. No failure or absent incumbent
is converted into an infeasibility certificate.

The producer report has schema FIXED17_AGGREGATE_EDGE_FLOW_PRODUCER_REPORT_V1.
The positive status is CANDIDATE_FIXED17_AGGREGATE_INTEGER_EDGE_FLOW_V1; the
absent status is NO_EXACT_AGGREGATE_FLOW_WITNESS_V1. Both have target_resolution
NONE, independent_approval false, graph_completion false, actual source author
and producer `/root/checkpoint_audit`, and the literal executor declaration.
Actual process/executor/cleanup facts come from the separate supported
supervisor receipt; they are not inferred from source authorship.

Nine model checkpoints are proposed after positive classes 8,16,...,64,68.
Science output has 16 nonsummary files / 17 physical files if no exact candidate,
or 18 nonsummary / 19 physical with a candidate: nine model checkpoints,
parsed input, model, native before/log/guidance/after, extraction, and the two
conditional candidate/row files. All output names and counts are enforced
before a success summary. Partial files and failure records survive a failed
attempt; no claim is made that native internal search state is resumable.

## New finite author controls

The new own packet proposes 7 positive and 25 precise negative routes, 32 total.
Each route saves its raw payload and actual/expected stage row; all seven
positive results are saved. Three tiny native runs additionally save a log,
guidance, and before/after checkpoints. This is 84 nonsummary files / 85
physical including the summary. A missing native log is a population failure.

The known-valid rook(9,4,1,2) edge-support fixture uses H=K2, masks [0,1,2,3]
and counts [2,2,2,1]. Its canonical unordered-edge vector is
[1,2,2,2,1,2,0,1,0,0]; it has 10 variables and 12 exact rows. A separate
necessary-bit fixture forces all three size-two diagonal capacities, the 0/3
cross capacity, and the appropriate zero pairs. A second valid rook fixture
uses four corners, two inserted zero classes, and five positive classes; it
checks canonical omission without an equitable-profile assumption.

The seven positives are the two edge-support witnesses, zero-class rook,
strict integer JSON, a tiny rook integer native model, and the two tiny known
contradictions 2e=1 with integer 0<=e<=1 and e=2 with e<=1. Numeric fixture
statuses are observed engineering outcomes; the contradictions are independently
hand-reasoned fixture identities and no scientific infeasibility claim.

Ten profile negatives are bool/float/negative count, bool/float/asymmetric H,
bool/unsorted mask, bool allowed bit, and duplicate pair index. Thirteen raw
candidate negatives are wrong header, wrong variable order, bool/negative/
over-capacity edge, forbidden zero/forced-one failure, bool ordered matrix,
asymmetry, odd diagonal, wrong even diagonal, degree failure, and an incidence
failure that preserves every degree. The latter changes the edge vector to
[1,3,2,1,1,1,0,1,1,0]; its first incidence failure is focal class 0/support
coordinate 1 with lhs 3 versus rhs 4. Duplicate JSON keys and nonfinite JSON
are the last two negatives. Exact stage names and ordering are in the source;
these are prospective until actual execution. No diagnostic alias is accepted.

Calibration reads no actual count/profile/pair/theorem input. Its scope is
strictly synthetic geometry/raw integer fixtures and three tiny native models.
An independent implementation must qualify its own controls, replay this
actual saved author packet, then validate the full actual model and candidate.
A full checker may truthfully certify an absent packet as correctly preserved
while carrying no integer-feasibility or infeasibility conclusion.

## Invocation, deadline, and limitations

Calibration is proposed as one supported Windows593 Job command, 180 outer /
150 worker seconds, 20-second save guard and 20 shutdown seconds, using the
locked offline `uv run` environment `build/research-venv`. Science remains a
null template pending genuine new controls and Root review; proposed 1800
outer / 1740 worker / at most1500 native seconds leaves at least180 worker
seconds for exact extraction/checking/closing when preprocessing fits. A fresh
operational HEAD/index/ledger observation belongs to admission, not this old
source's timestamp. No current computational peer is inferred from a plan.

The CommandDeadline covers direct hashes, parses, typed profile/model loops,
native call, exact extraction, output hashing, and closing checks. A status
guard before/after saves and 1 MiB hash chunks requires more than20 seconds
remaining with no stop request. Finite JSON parsing/serialization, list
comprehensions, OS scheduling, and a native call are atomic regions without a
tick for every instruction. Supported outer containment is separately required;
there is no hard-real-time shutdown or unconditional durable partial-save
promise. Useful completed files/checkpoints and a best-effort failure record
are preserved on error, with no automatic retry.

No syntax check, import, solver call, calibration, raw actual model generation,
ledger/status/index/staging/commit/push action, or new mathematical approval
occurred in preparing this source/spec. All command authorities remain separate.
