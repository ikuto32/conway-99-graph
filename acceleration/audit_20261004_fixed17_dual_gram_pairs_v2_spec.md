# Independent fixed17 dual-Gram pair checker, implementation 2

This new source is Native-authored and remains source-only until a separately
reviewed ONE invocation. Structural authored the pair producer 079435 and its
specification 455767. The checker imports only standard Python components and
command_deadline. It never imports the pair or singleton producer, generates
an inverse, runs LDL, calls an LP solver or writes CLAIMS/index/Git.

Canonical report families are
INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_CALIBRATION_PASS,
INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_PRODUCER_CONTROLS_PASS, and
INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS. All have integer
implementation_version 2, Structural producer, Native verifier,
method independent_artifact_check and target_resolution NONE. Mode is
calibrate, controls or full. A new source needs fresh qualification; neither
the singleton gate nor producer author controls approve this checker.

## Distinct exact mathematical path

For ordered literal masks construct sets T, binary t, and rational b=1/9-t.
Multiply the submitted rational upper/lower inverse matrices directly by b/t.
For a pair compute rational bilinear products and the two Schur matrices:

    upper diagonals 28/9-b^T Uinv b;
    upper cross 1/9-a-b^T Uinv z;
    lower diagonals 4-t^T Linv t;
    lower cross a-t^T Linv u.

For each literal a=0,1 require both nonnegative diagonals and cross squared at
most their product. Compute support intersection using independently built
Python sets. Its CN cap is 2 for a=0 and 1 for a=1. Intersect the same adjacency
bit across all three tests. Only after this rational calculation convert the
upper entries to their common 81d numerator scale and lower entries to e.
This does not call or reproduce the producer's integer r/Nr context or integer
record function. Canonical Fraction strings reject aliases and numeric types.

Full mode reconstructs the literal seventeen-vertex H from the twelve specified
triples and compares all 289 binary entries to parsed_input.json. It parses the
complete submitted rational matrices and independently checks BOTH products
U*Uinv and Uinv*U, and BOTH L*Linv and Linv*L, all 1156 identity entries. Positive
definiteness/LDL qualification and the exact allowed 472-mask universe are
explicitly inherited from the genuine Checkpoint singleton COMPLETE gate;
this checker does not regenerate those proofs or reenumerate all 17-bit masks.
The gate must have implementation 1, Structural/Checkpoint/artifact/NONE,
the five direct singleton artifact pins and all six exact integer count fields.
Its entire declared input map is rehashed within this invocation.

Compare all 472 saved singleton coordinates and rational margins with the new
rational calculation. Independently derive denominator LCMs, numerator
matrices, every r/t vector, Nr/Pt product, diagonal and scaled_input field.
The scale conversion is justified exactly; no floating-point tolerance is used.

Enumerate combinations_with_replacement of indices in lexicographic order:
all 111628 labels, including 472 equal-type labels for DISTINCT outside
vertices and 111156 unequal-type labels. Do not filter positive primal support
or cardinality. Compare every one of nineteen record keys with strict recursive
type equality, all 23 parts of size 5000 except final 1628, all 23 checkpoints,
every complete-prefix input identity and cumulative count. The four classes
partition the joint bit sets; independent CN/upper/lower diagnostic failures
overlap. The complete aggregate and exact 48-physical/47-output population
must match. An independently saved aggregate is the full-mode output.

## Fresh synthetic qualification: 13 positive, 58 negative, 71 routes

All payloads are saved before evaluation, each mutation starts from a deep
copy, and every precise expected/actual first stage must match. The original
ten positives and forty-one negative producer-shaped routes are retained, but
evaluated with Native functions. Shared analytic fixtures are empty H2,
K3 and synthetic empty H17, with explicit hand inverse formulas I/3-J/87,
I/4; I/4+J/6, I/3-J/18; and I/3-J/132, I/4 respectively. These produce 26
unique Fraction pair records plus ten durable-stream comparisons, with four
three-record parts and four checkpoints. The first empty-H2 eight numerators
are 21870,21870,729,-6318,16,16,0,4; the first K3 values are
2997,2997,81,-891,72,72,0,18. The final seventeenth bit is exercised.

Three additional positives qualify a same-bit conflict, the new own report
header and the runtime path. The conflict uses one-coordinate submitted
upper inverse 243/128 and lower inverse 9/4 with mask 1. It yields upper-only
bit 0, lower-only bit 1 and CN both, so the joint set is empty. This is a
synthetic algebraic branch fixture; it is not presented as a realizable graph
or the inverse of a jointly realized H.

The retained forty-one precise routes are the producer's rational Boolean/
alias, inverse schema/gram/dimension/shape/entry/symmetry, mask Boolean/float/
range/distinct/order/population, record keys/integer/bits/coordinate/cross/
classification, singleton gate header/direct-pin/count, strict JSON duplicate/
constant, part integer/boundary/population, checkpoint integer/count/identity,
and author header Boolean-version/count controls. Their literal names and
execution order are public in author_routes.

Seventeen new negative routes are:

| Names | First stage |
|---|---|
| late_mask_bool | RECORD_INTEGER |
| late_lower_cross, late_upper_diagonal | RECORD_IDENTITY |
| scaled_numerator, scaled_last_vector, scaled_denominator_bool | SCALED_IDENTITY |
| runtime_exit_bool | RUNTIME_EXIT |
| runtime_source_wrong | RUNTIME_MANIFEST |
| runtime_live_job | RUNTIME_CLEANUP |
| runtime_invocation_wrong | RUNTIME_INVOCATION |
| runtime_elapsed_inf (literal string) | RUNTIME_ELAPSED |
| runtime_command_wrong | RUNTIME_SUMMARY_COMMAND |
| own_missing_pin, own_bool_version, own_bool_count | OWN_CALIBRATION_HEADER |
| inverse_left_corrupt | INVERSE_LEFT_IDENTITY |
| inverse_right_corrupt | INVERSE_RIGHT_IDENTITY |

The last two call the ACTUAL identity_products helper used by full mode.
The left fixture corrupts the empty-H2 upper inverse at (0,0). The right
fixture corrupts (0,1): its first left-product (0,0) stays 1 but its first
right product becomes 1+1/9. It intentionally bypasses the public symmetry
parser to exercise the right helper branch; that parser would reject the
nonsymmetric corruption earlier. Neither corruption claims a valid inverse. Successful qualification saves
71 control payloads, eight synthetic stream files, controls.json and summary:
81 physical files and 80 nonsummary hashes. It reads no actual singleton
artifact, scientific pair, primal, target graph or future producer packet.

## Genuine producer-controls and full replay

Controls mode first authenticates the new own calibration snapshot, its nine
source/software pins, all 80 outputs, exact 71 rows and complete directory.
Source applicability is snapshotted BEFORE pinning the calibration summary;
the summary cannot be compared to an input map containing itself.

Then authenticate the actual producer plan/summary/manifest/terminal. Reconstruct
all fifty-one expected source-shaped payloads independently, require exact
actual payload equality, evaluate every actual payload through Native routes,
and compare producer expected/actual/independent stage triples. Rebuild all ten
stored synthetic records, every boundary and prefix. All 61 physical files and
60 outputs are covered. Save producer_control_stage_pairs.json; this report
has only finite control scope and actual_target_input_read false.

Full mode additionally requires the genuinely qualified Native controls report
bound to this exact source/spec. The actual pair producer's author calibration
path/hash must occur directly in that controls report's immutable input map.
Authenticate the exact new singleton gate and five literal singleton objects,
the original author calibration, the complete 48-file raw pair packet, exact
source maps and original Path-string input identity maps. No absent future
endpoint or generic source-family status can substitute for a genuine gate.

## Runtime and complete closure

Read the producer's literal command/child_argv/worker_argv, verify exact suffixes,
calibrate 12-word or pairs 20-word worker, -B, source path/version/hash, actual
mode and output root. SUP2's source hash and LOCAL_WINDOWS_SUSPENDED_JOB_V1
scope must match. Allocation values come from the actual literal vector,
rather than assuming a historical fixed scientific ceiling. Bind a matching
invocation, integer zero exit, no error/deadline, created/resumed/reaped process,
empty Job, integer zero actual exit, no cleanup errors and finite outer elapsed.
The producer intentionally records sys.argv without interpreter/-B; compare
that exact declared slice, cwd and closing remaining-time status.

The checker imports no producer runtime or math code. Its own runtime is
checked separately by ROOT against the new frozen plan. Its immutable input
map includes every directly read raw file, all applicable gate/qualification
inputs and complete raw output maps. CLAIMS/index/HEAD are admission observations
outside that mathematical map. No arbitrary private process arguments belong
in public admissions. There is no complete ancestor evidence closure claim.

All preprocessing, Fraction operations, parsing, serialization, file hashing,
closing rehashes and children share one per-invocation deadline. Reads stream
one-MiB blocks with guards and accept files up to 64 MiB; no recursive external
crawler is used. Guarded saves and final input checks require more than twenty
seconds remaining. That is an allocated reserve intention, not a hard real-time
filesystem or OS guarantee. A closing failure preserves failure.json, raises
and vetoes an already serialized prospective summary. Earlier complete outputs
survive; a hard kill may lose a pending suffix. Exact clean contained terminal
and absence of failure are required for a genuine gate.

The initial own allocation is 180 outer / 150 worker / 20 save / 20 shutdown,
chosen for small new Fraction/runtime/serialization controls with unmeasured
overhead. It is a ceiling, not a target or inherited default cap. Future full
allocation remains a separately reviewed literal plan; 111628 direct Fraction
bilinear calculations and complete raw closure require their own allowance.
No automatic retry or chain to controls, science, pair cuts or ledger is allowed.

All results concern necessary conditional tests for this fixed induced H and
this ordered type universe. They do not prove integer/graph completion,
exclude the target, generate an LP cut, enumerate maximal cliques or justify
unit multiplicity for types of cardinality at most two.

## Narrow implementation 2 preservation and control delta

Implementation 1 source aba181/spec c01bde and its preliminary/corrected
source-only plans and templates remain unexecuted and byte-preserved. Its two
inverse-product corruptions tested a separate miniature multiplication
predicate, an honest helper-only check that did not qualify the actual full
helper's rejection routes. Implementation 2 changes only those two payloads
and their calls to the existing identity_products function, plus SELF/SPEC
paths and its OWN implementation headers. The Structural author header and
Checkpoint singleton header remain integer implementation 1. All pair math,
raw wire, runtime, closure, 13/58/71 control counts and 81/80 populations are
unchanged. Old own qualifications cannot approve this changed source.

For the empty-H2 upper Gram 3I+J/9, adding E00 to its exact inverse makes the
first left-product entry 1+28/9, so INVERSE_LEFT_IDENTITY is first. Adding E01
makes that same left entry remain 1 while the first right entry is 1+1/9, so
INVERSE_RIGHT_IDENTITY is first. These are exact paper calculations, not
observed control outcomes. The new explicit controls have not run.