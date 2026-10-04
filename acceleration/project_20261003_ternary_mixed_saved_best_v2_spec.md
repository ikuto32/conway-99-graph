# Saved BEST graph-only projector V2 / input implementation 2

SOURCE ONLY. This version preserves V1 source cc7477213ed0416003168c43f62b4352d6d7e87bf410c185752887b18d00bf99
and spec 3ad7d8f620ccdb57d23452c200ebc9617e87110886a8482adfba714a2c41ddde,
its actual author controls and their separately written counting correction.
V1 has not produced an actual saved-BEST projection. Its material static veto is
the missing closing budget checks after hashes, output writes and final summary.

The sole executable change introduces check_budget(deadline), evaluating one
status snapshot with the existing remaining_seconds > 20 and not stop_required
SAVE_RESERVE predicate. pin checks before and after each complete hash. Additional
checks follow selected BEST extraction, raw matrix/report reading, wire encoding
and writing, provenance hashing/serialization, each source closing identity hash,
the raw output identity population, and final summary serialization. A failed
closing check preserves the files already written, writes failure.json through
the unchanged exception path, and raises; the process cannot report successful
completion merely because candidate summary.json was written. Failure preservation
is allowed to use the remaining reserve and is not recursively budget guarded.
These cooperative checks do not preempt a blocking hash/I/O operation or prove
hard real-time stopping. The separate supported SUP2 containment and actual
terminal receipt remain required.

extract_best, saved_relation, scalar/geometry arithmetic and wire are unchanged.
The projector reads selected BEST fields only from whole state bytes already
authenticated by genuine Saved4 complete checking. It does not replace the
independent full-state/RNG/cache parser. Same canonical graph-only wire and
projection schema/input implementation 2 are retained; producer filename/spec
and actual command/source pins distinguish V2. No native state, history/RNG or
counter import, search, target result, census or automatic next command is emitted.
The 231 construction triples are not claimed to be all actual graph triangles
when lambda is positive.

The unchanged prerequisite is Native producer / Checkpoint verifier /
independent_artifact_check / NONE Saved implementation 4 COMPLETE_PASS. Raw final
state and best matrix must be direct members of its immutable map; saved best
metrics must exactly match the selected literal row recomputation. Every map
member is freshly hashed inside the inclusive invocation. CLAIMS and .git/index
are rejected as immutable members. Historical SCI2/spec identities retain only
their explicitly disclosed formatter/parser ancestry role. No old graph gate
approves this new projector.

Required output population remains graph_input.txt, projection.json and candidate
summary.json, or failure.json plus every already written file. Closing checks do
not alter these schemas, source identities, rows or scores. The fresh V2 author
helper is synthetic only: three geometry positives, one saved-report relation,
three opaque-history equalities, the preserved 42 strict stages, and two positive
plus four negative synthetic tests of this exact budget predicate. This is an
applicability test of the predicate, not a simulation of filesystem stalls or a
general proof of deadline/containment behavior. The helper honestly counts 10026
binary adjacency entries and 4953 unordered-pair dot products across its fixtures.
It does not claim 10026 complete CN products. Fresh independent source-bound
calibration, actual author-output replay and full input checking must use their
own whole-state/scalar parser and all 9801 CN products on the actual target.

No import, calibration or actual projection is authorized by this freeze. A fresh
literal author plan proposes 120 outer / 100 inclusive worker / 20 preservation /
20 shutdown based on the completed sub-second synthetic V1 helper. Actual whole
prerequisite projection will have a separately reviewed allocation and literal
plan, fresh UID1000/ownership/resources/pins, and a genuine independent new-input
gate before any scientific consumer runs. Source changes do not approve or resume
research, alter the ledger/index, or transfer old approvals.
