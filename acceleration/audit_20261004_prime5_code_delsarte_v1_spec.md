# Independent exact quinary Delsarte checker, first source version

SOURCE_ONLY. Native authors this separate implementation against Structural
producer V2 `solve_20261004_prime5_code_delsarte_v2.py` SHA256
`ac47adedb67794ed029c72b920fcfd039ef0210f1e45daf257dcd361223776d7`
and its specification
`d21bb894ba67f4b5e6f4582963ae8c70dd7f66ab7d05810f8226eb80bcbc45b4`.
No checker import, AST extraction, syntax test, calibration, coefficient
calculation, numerical backend, scientific read or executable verification has
occurred. All control stages below are prospective written predictions.
Checker version1 and its status headers are distinct from producer version2.
Neither version-one producer gates nor any other code gate approve this source.

## Different exact arithmetic and independent mathematical derivation

For q=2 or5 define K_j(i) by the generating polynomial
(1+(q-1)z)^(n-i)(1-z)^i. The producer evaluates a binomial signed sum.
This checker instead starts with coefficients [1,0,...,0] and multiplies one
linear factor per coordinate, using descending coefficient updates. For the
first i coordinates the slope is -1; for the other n-i it is q-1. Descending
updates use only the preceding coordinate's coefficients, and truncation above
degree h does not change any coefficient through h. This reconstructs every
submitted K_j(i) independently without a producer function, import, AST,
combinatorial-sum reuse or backend. All coefficients are ordinary integers.

The theorem is derived directly from additive characters. For a linear code C,
sum_(x in C) psi(u dot x) is |C| when u is in C-perp and zero otherwise.
In a coordinate where x is zero, choosing a nonzero u contributes q-1; where
x is nonzero it contributes -1, since the sum over all field elements is zero.
Summing first over words u of weight j and then over codewords therefore gives
sum_i A_i K_j(i)=|C| B_j, with no missing factor of q, |C| or ambient size.
K_0(i)=1 provides the normalization check. The even binary length-three
fixture computes all eight character sums directly and transformed counts
[4,0,0,4] for dual counts [1,0,0,1].

Suppose A_0=1, A_i=0 for1<=i<d, and B_j>=ell_j. For y_j>=0 and
f(i)=1+sum_j y_j(K_j(i)-ell_j)<=0 at every i=d..n,

    sum_i A_i f(i)=|C|*(1+sum_j y_j(B_j-ell_j))>=|C|,
    sum_i A_i f(i)<=f(0).

Thus |C|<=f(0). The checker reconstructs f at weight0 and every allowed
nonzero weight, checks every sign exactly and checks the largest integer k
with q^k<=f(0)<q^(k+1) by integer products/rational comparisons. A candidate
is an upper bound, never an optimum or code realization. Zero C remains
allowed. A valid target candidate improves the historical dimension27 bound
only when its exact dimension upper bound is below27, equivalently f0<5^27.
The historical determinant theorem is a comparison, not a newly checked gate.

Parameters, integers, Boolean distinctions and canonical Fraction strings are
strict. Accepted degrees satisfy1<=h<=min(32,n), n<=99. Every fraction has at
most2048 characters, denominator at most10^512 and its exact canonical spelling.
Negative multipliers, missing coordinates, noncanonical strings and altered
value tables are rejected. No numerical coefficient is rounded by this checker.

## Exact scientific applicability and direct premises

The only scientific profile is q5/n99/d55 with ordered degrees[20,32], each
with baseline or lower counts{3:924,4:8316,5:24948,6:391776}. The certificate
wire remains EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1 with exactly its fifteen
declared fields. Each target certificate has46 values, including all45 signs
at55..99, and20 or32 multipliers. Header/scope, fixed parameters, exact values,
f0, integer dimension and neighboring powers are checked in that order.
nonzero_code_forced and is_optimality_certificate are false; target_resolution
is NONE. None can be replaced by Boolean or floating-point stand-ins.

The exact six premise identities in source PREMISES are immutable direct
dependencies: support55 schema2/report/Root written acceptance and image-count
schema2/report/Root written acceptance. They are authenticated, not rederived
by this numerical-certificate checker. No graph object, entire code enumerator
or transitive ancestor closure is recomputed. Their bindings must have exact
IDs/r1, Structural producer/Native written verifier, VERIFIED/CLEAR,
independent_derivation and unrestricted/NONE scope, with exact report refs.
High-weight bounds96:924 and99:2776 are recorded as unused; they are not added
to low rows or interpolated into an entire weight enumerator.

Full mode authenticates the exact source configuration schema
PRIME5_CODE_DELSARTE_CONFIGURATION_V2 with schema/parameters plus nine refs.
Its producer input map must equal the six software objects, configuration and
nine refs, sixteen objects total. Author acceptance and science Root authority
have the V2 source's literal contracts. The accepted prior independent
producer-controls gate must apply to this exact checker software and exact
author summary. Later gates authenticate qualified own68 raw files; they do
not rerun own68 actions. Full mode genuinely replays all31 producer actions.

## Runtime and complete closure

An exact CHECK_PACKET_V1 supplies mode, own_calibration/own_acceptance,
producer_summary/producer_plan/producer_manifest/producer_terminal/
producer_acceptance refs. Full adds producer_controls and its acceptance.
No future hash can be null in an executable packet. Source-only followup
templates must retain null refs until genuine endpoints exist. Root receipts
are pinned administrative dependencies, not alternate mathematical algorithms.

Author runtime explicitly recognizes PRIME5_CODE_DELSARTE_V2_SOURCE_ONLY_
AUTHOR_CALIBRATION_PLAN, flat36/20/12 and declared120/100/20/20. Science
recognizes PRIME5_CODE_DELSARTE_CONCRETE_SCIENCE_PLAN_V2 with nested solve
and five byte-identical top aliases, or the separately identified Root-flat
ROOT_PRIME5_CODE_DELSARTE_CONCRETE_SCIENCE_PLAN_V2. The Root-flat profile has
40/24/16, exact source/spec/config refs and literal180outer/150worker/20shutdown.
It has no manufactured solve or allocation field: save20 is this profile's
declared intent with actual repeated guards. The synthetic Root-flat control
exercises precisely that missing-field shape; its data are not actual receipts.

In both profiles the exact supported SUP2 child and worker suffixes are checked,
Windows suspended Job containment precedes locked/offline uv with explicit
research Python/cache, and actual source464102 identifies SUPv2. The manifest
uses LOCAL_WINDOWS_SUSPENDED_JOB_V1 and the literal local non-escaping process
scope. Actual terminal must have child0, COMMAND_EXITED, no error/deadline and
created_suspended/resumed/reaped/job_active_zero_observed all true with no
cleanup errors. Elapsed is finite and within outer allocation. Producer
summary intentionally has no command/executor; the checker never demands an
invented field and authenticates the actual plan and SUP separately.

Every input hash is checked and rechecked before final seal. Every declared
producer output and actual file inventory is checked, including dynamic
polynomial population. Only exact base/summary.json is exempted; a nested
extra/summary.json must be listed or causes OUTPUT_INVENTORY. All paths stay
within ROOT, without symlinks/traversal. Reads are bounded2MiB. Duplicate JSON
keys and nonfinite JSON values are rejected. Output directory handling uses
safe(...,False), then authenticated parent/directory comparison, rather than
incorrectly treating a directory as a regular file. Positive actions convert
Path results explicitly to strings; JSON never has a global stringify fallback.

The four cases are checked in producer order:20baseline,20lower,32baseline,
32lower. For each guidance, candidate and immutable checkpoint are required;
an available certificate additionally requires exactly its polynomial file.
All outcome rows and checkpoint completed-case prefixes/LP-call counts are
typed and exact. Source output closure is13..17 nonsummary,14..18 physical.
Numeric status and objective are guidance. A missing certificate has a strict
nonempty string reason and returns UNKNOWN with null bound/dimension and false
improvement. Numerical infeasibility is never an exact code/graph obstruction.

## Prospective independent own controls:68=16positive52negative

Indices0..30 independently replay the producer's literal31 routes in source
order. The original29 retain their meanings; the tiny numerical-guide positive
uses a synthetic header and separately exact size4 certificate, with zero
backend calls. Later actual-author mode inspects the genuine saved tiny guide
without rerunning its LP. Index29 is full quinary n32,d1,h32 with all32 y_j=1:
the generating polynomial at z1 is5^32 at weight0 and zero at every weight1..32.
Thus all33 values, literal23283064365386962890625 and dimension32 are checked.
Index30 rejects degree33 at PARAMETERS. The first31 contain10 positives and21
negatives; their exact stages/names are bound to the producer V2 specification.

|Index|Additional independent case|Expected first stage|
|---:|---|---|
|31|Zero left code boundary, exact f0=1 and dimension0|PASS|
|32|Missing candidate retains UNKNOWN and null bound|PASS|
|33|Actual-shaped Windows SUPv2 manifest/terminal|PASS|
|34|Output directory returns a JSON string|PASS|
|35|Only exact probe base/summary exemption|PASS|
|36|Actual-shaped Root-flat science plan without invented fields|PASS|
|37|Extra certificate field|CERTIFICATE_HEADER|
|38|Old certificate schema|CERTIFICATE_HEADER|
|39|Forcing nonzero code|CERTIFICATE_SCOPE|
|40|Optimality overclaim|CERTIFICATE_SCOPE|
|41|Target-resolution overclaim|CERTIFICATE_SCOPE|
|42|First value altered|VALUE_TABLE|
|43|Last value altered|VALUE_TABLE|
|44|Value order changed|VALUE_TABLE|
|45|Boolean weight|VALUE_TABLE|
|46|Unreduced value spelling|VALUE_TABLE|
|47|Floating value|VALUE_TABLE|
|48|Canonical bound disagrees|BOUND_VALUE|
|49|Unreduced bound spelling|FRACTION_CANONICAL|
|50|Boolean bound|FRACTION_TEXT|
|51|Boolean dimension|DIMENSION_POWERS|
|52|Boolean lower power|DIMENSION_POWERS|
|53|Floating next power|DIMENSION_POWERS|
|54|Wrong next power|DIMENSION_POWERS|
|55|Negative dimension|DIMENSION_POWERS|
|56|Absent candidate with null reason|UNKNOWN_REASON|
|57|Absent candidate with Boolean reason|UNKNOWN_REASON|
|58|Certificate with unknown reason|CANDIDATE_REASON|
|59|Extra wrapper field|CANDIDATE_WRAPPER|
|60|Wrong manifest source|RUNTIME_MANIFEST|
|61|Wrong manifest scope|RUNTIME_MANIFEST|
|62|Boolean child exit|RUNTIME_EXIT|
|63|Child not created suspended|RUNTIME_CLEANUP|
|64|String inf elapsed|RUNTIME_ELAPSED|
|65|Worker source differs from child suffix|RUNTIME_SUFFIX|
|66|Unlisted nested extra/summary.json|OUTPUT_INVENTORY|
|67|Duplicate JSON key|DUPLICATE_KEY|

The immutable control records preserve actual/result/detail. Each damaged
certificate/runtime fixture is separately deep-copied before mutation. None
of the selected mutation locations aliases a different semantically checked
field; the intentional positive runtime argv aliases are not mutated. The inventory
probe has three real files: base summary/data and later nested extra summary.
All three are declared in the enclosing own packet's inventory. Own output
population is68 control records+controls+3probe files=72 nonsummary and73
physical with summary. Main asserts72, source own gate asserts16/52. Controls
mode has one stage-pair payload plus summary; full has two payloads plus summary.
No stale author count or unrelated source-version gate is accepted.

## Allocation, stop handling and source-only corrections

Prospective own68 uses120outer/100worker/20save/20shutdown under SUPv2, with
zero backend calls and no actual target input. All pinning, coefficient folds,
JSON, inventories, closing hash checks and saves share the worker deadline.
The ceiling is evidence from small bounded dimensions, not a timing promise.
Reserve guards check finite remaining>20 before/after each success save and
before/after final summary. They are declared guards, not a hard-real-time
proof that storage finishes within20s. SUP enforces outer cleanup independently.
Failure writes failure.json where possible; a provisional summary beside
failure is not a gate. No retry, resumed worker or automatic scientific chain.

Pre-freeze written corrections are disclosed: nested summary exemption was
narrowed; directories were explicitly handled as directories; Root's genuine
V1 flat science plan was read and the separate V2 profile is declared; a misplaced
elif in the editable high-degree hand-check branch was corrected by plain text
inspection before freeze. None was an executed failure or mathematical refutation.
The editable draft was first designed for V1 but never frozen or qualified;
the first frozen checker binds V2 exactly. Original producer V1 actual UNKNOWN
records and historical gates remain untouched and outside current applicability.
