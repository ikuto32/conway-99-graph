# Fixed17 labelled exterior-copy adjacency V1

Status: SOURCE_ONLY. No source import, syntax execution, solver call, calibration,
scientific output, independent gate or launch authority is supplied by this file.
Producer and source author: `/root/checkpoint_audit`. Prospective actual executor:
`/root`, established by a genuine external supervisor receipt. Independent
implementation verifier: `/root/native_driver`; Root reviews and authorizes each
separate invocation. Target resolution remains `NONE`.

## Necessary system and exact scope

Use the authenticated `468f281b...` parsed fixed profile, its complete 472 masks
and integer counts, the genuine count/pair/capacity gates and the independently
derived block-moment theorem `910a740a...`. The ten literal direct premises are
listed in the source. They are inherited premises, not a claim to repeat their
ancestor-wide arithmetic or hash closures. The fresh worker reads and hashes
these direct bytes. No support type is filtered: every input mask/count remains
in the saved profile, and count-zero types create no exterior copies.

For each original type index i and copy number c=0,...,n_i-1, create label [i,c].
Labels are ordered by i then c. Exterior ordinal x is its position in this list.
The accepted counts give 82 copies in 68 positive classes. Assign one variable
e_xy to every x<y in lexicographic order: 82*81/2 = 3,321 binary variables. The
same variable appears at both endpoints. There are no self-edge variables.

For a type-pair allowed-bit list L_ij, an actual distinct-copy pair with empty L
rejects the input. Bit 1 absent fixes e=0; L=[1] fixes e=1; L=[0,1] leaves e binary.
An empty diagonal type-pair list is harmless when that type has fewer than two
copies. Both off-diagonal and same-type distinct-copy constraints use the same
trusted pair relation. No equitable profile or automorphism is assumed.

For each exterior ordinal x of type T_x, impose the degree equation

    sum(y != x) e_xy = 14 - |T_x|.

For support coordinate u=0,...,16 impose

    sum(y != x, u in T_y) e_xy
      = 2 - 1[u in T_x] - sum(v) H[u,v] 1[v in T_x].

Order each copy's degree row before its 17 coordinate rows. The model has
82 degree plus 1,394 incidence rows, totalling 1,476 exact equalities. Every
sparse coefficient is the integer 1. A conservative sparse-entry bound is
2*3,321*18 = 119,556; actual nnz is recorded inside the invocation. This is a
larger coupled system than the 68-class aggregate flow, because all rows share
the actual per-copy edge variables.

There is a literal bijection between a binary e vector and a symmetric binary
82x82 zero-diagonal matrix D, by setting D[x,y]=D[y,x]=e_xy. Under this bijection,
the bounds express the allowed pair relations, the degree rows express exterior
degree, and the coordinate rows express H B + B D = 2 J - B for the fixed
support-to-exterior incidence matrix B. Thus the model is equivalent to exactly
this restricted labelled local system. This is a written derivation awaiting a
different-author review, not a computational or self-approved theorem.

The omitted exterior-pair common-neighbor equations matter. A known rook(9,4,1,2)
fixture uses H as an edge, masks [0,1,2,3], counts [2,2,2,1]. Switching exterior
edges (2,4),(3,5) to (2,5),(3,4) preserves its seven degree and fourteen coordinate
rows but gives CN(0,2)=0 for an exterior edge and CN(0,5)=3 for an exterior nonedge.
This counter-control uses explicitly free/mock pair bits. It is not an assertion
about which pairs the trusted fixed17 profile permits. Passing this relaxation
does not validate an SRG or prove a target exists. Numeric infeasibility, timeout,
no incumbent or failed extraction is UNKNOWN, not a count or target exclusion.

## Native guidance, exact extraction and containment

The new physical source text adapts the direct Reader, generic typed profile,
HiGHS sparse construction and numeric extraction conventions from the unchanged
`solve_20261004_fixed17_aggregate_edge_flow_v1.py` (ec556ba0...). No producer module
is imported and no old aggregate checker/control gate applies to this version.
Root proposed the coupled model; Structural authored the shared block theorem;
Native independently derived it and supplied the rook relaxation counter-control.
These shared origins are disclosed separately from new independent implementation
checking.

The locked Windows research environment uses HiGHS 1.15.1. The worker authenticates
nine literal software/dependency files plus its own source/spec, checks local
highspy/numpy module paths, and verifies the native version. No broad prerequisite
crawler is added. Root's admission separately pins the Python and uv executables,
uses `uv run --locked --offline`, sets/restores `UV_PROJECT_ENVIRONMENT`, and uses
the supported suspended Windows Job supervisor 593a9fee before uv.

Each native model has zero objective, integer columns with binary bounds, seed 0,
threads 1, parallel off, presolve on, solver choose, both feasibility tolerances
1e-7, both MIP gaps 0, and preserved console-disabled logging. Calibration calls
one known-rook tiny native fixture with at most 5 seconds. A future scientific
invocation calls HiGHS exactly once with at most 1,200 seconds, further reduced by
remaining inclusive worker time minus a 180-second post-native reserve. Planned
science allowance is 1,800 outer / 1,500 worker / 20 save / 20 shutdown, subject
to source, finite gate, literal plan and ONE review. This is evidence-based:
previous count and aggregate invocations motivated a bounded coupled integer
attempt; no probability or completion-time forecast is claimed.

Raw numeric coordinates and their float.hex strings remain guidance. A value-valid
complete vector is rounded only as a candidate at distance <=1e-7. The strict binary
candidate must then satisfy every bound, symmetric matrix identity and integer row
exactly. No solver status, objective, optimality, numerical bound or missing witness
is proof. If extraction fails, save a null candidate plus its precise reason.

CommandDeadline starts before hashing and native work. Chunk hashes, outer loops,
solver checkpoints, exact rows, saves and closing direct-pin checks share the same
invocation. Every tick requires no stop and more than 20 remaining seconds. Finite
JSON parse/comprehensions, native calls and file-system atomic operations are not
hard-real-time services; only a genuine clean supervisor terminal establishes actual
containment. The reserve is a checked intent, not an absolute save guarantee.
Completed checkpoints and failure bytes are preserved, no automatic retry occurs,
and HiGHS internal resumability is not promised. No Git, index or ledger mutation.

## Physical wire

The candidate keys are exactly schema, copy_labels, variable_pairs, edge_values,
exterior_adjacency, graph_object_validated. Schema is
`FIXED17_COPY_ADJACENCY_INTEGER_CANDIDATE_V1`; graph_object_validated is literal false.
The binary edge vector length is 3,321 and D is 82x82. Candidate check order is
header, labels, pair order, strict binary values, matrix binary domain, zero diagonal,
symmetry, vector/matrix identity, pair bounds, then ordered degree/incidence rows.
Exact row observations have row/kind/copy_x/type_i/support_u/lhs/rhs.

`copy_model.json` uses schema `FIXED17_COPY_ADJACENCY_MODEL_V1`, with target_order,
target_degree,support_order,ordered_masks,counts,copy_labels,variable_pairs,variables,
outside_copies,lower,upper,rows,no_equitable_profile_assumed:true,
outside_pair_CN_equations_included:false. Each row has exactly kind,copy_x,type_i,
support_u,lower,upper,terms. Terms are ordered [variable_id,1] entries.

There are nine model checkpoints after copy counts 10,20,...,80,82. Their schema is
`FIXED17_COPY_ADJACENCY_MODEL_CHECKPOINT_V1`; keys are schema,index,completed_copies,
rows,variables,copy_labels_prefix,deadline. Index is 0,...,8; rows are 180,360,...,
1,440,1,476. The deadline is the actual ten-field status object from pinned 9876.
The producer does not regenerate or claim common per-copy profiles within a class.

Native files per call are PREFIX_solver.log (precreated even if empty),
PREFIX_before_solver.json, PREFIX_guidance.json, PREFIX_after_solver.json. Before
has variables/rows/nnz/proposed_options/remaining(status object)/
native_limit_finalized_after_checkpoint:true. Guidance schema
`FIXED17_COPY_ADJACENCY_NUMERIC_GUIDANCE_V1` has native_version,numpy_version,
run_status,model_status,solution_value_valid,col_value,col_value_float_hex,options,
wall_seconds,objective_all_zero:true,solver_calls:1,floating_status_is_proof:false,
numeric_infeasibility_is_proof:false. After has native_status/model_status/
wall_seconds/remaining(status object)/is_proof:false. Extraction has candidate:null
and reason/infeasibility_proved:false on absence (optionally max_rounding_distance),
or candidate/exact_check/rounding_tolerance/max_rounding_distance/
infeasibility_proved:false on success.

Scientific outputs are the nine checkpoint files, parsed_copy_input.json,
copy_model.json, four scientific native files and extraction.json: 16 nonsummary
files, 17 physical including summary. A candidate adds exact_integer_copy_edges.json
and exact_copy_rows.json, giving 18 nonsummary and 19 physical. The producer writes
no full99 matrix and makes no graph validation claim. The distinct checker may
reconstruct [H B; B^T D] and separately diagnose all 9,801 products; its local
relaxation PASS must be distinct from reconstructed_graph_srg_valid and any later
Root object acceptance.

Producer report schema is `FIXED17_COPY_ADJACENCY_PRODUCER_REPORT_V1`, impl1, author
CP and actual executor separately receipt-bound. Status is author-controls PASS,
`CANDIDATE_FIXED17_COPY_ADJACENCY_V1`, or `NO_EXACT_COPY_ADJACENCY_WITNESS_V1`.
Summary `command` is sys.argv, excluding interpreter/-B; the genuine native command
is authenticated by the separate supervisor manifest. Inputs are direct relative
file hashes, outputs are relative basenames excluding summary, and no independent
approval or target resolution is implied.

## Finite controls and future qualification

The prospective author scope is 7 positives / 22 precise negatives / 29 total.
Save all29 payloads and stage rows, seven positive result files, four tiny native
files and controls.json: 70 nonsummary hashes / 71 physical files. All observed
stages remain null before a genuine invocation.

Positives: rook_model, rook_integer, sole1_rook, zero_count_four_corners,
singleton_empty_diagonal, local_relaxation_not_SRG, native_known_rook.

Negatives in literal source order: bool_order→PROFILE_TARGET;
bool_degree→PROFILE_TARGET; graph_float→PROFILE_GRAPH;
graph_asymmetric→PROFILE_GRAPH; mask_float→PROFILE_MASKS;
duplicate_mask→PROFILE_MASKS; count_bool→PROFILE_COUNTS;
count_total→PROFILE_COUNTS; pair_order→PROFILE_PAIR_ORDER;
bits_bool→PROFILE_PAIR_BITS; bits_unsorted→PROFILE_PAIR_BITS;
empty_positive_pair→PROFILE_INCOMPATIBLE_PAIR;
copy_label_bool→CANDIDATE_COPY_LABELS; edge_bool→CANDIDATE_BINARY;
edge_float→CANDIDATE_BINARY; self_loop→MATRIX_DIAGONAL;
asymmetric→MATRIX_SYMMETRY; matrix_float→MATRIX_BINARY;
edge_disagreement→EDGE_MATRIX_IDENTITY; forbidden_pair→PAIR_BOUND;
degree_corruption→DEGREE_EQUATION; incidence_corruption→INCIDENCE_EQUATION.

The future configuration schema is `FIXED17_COPY_ADJACENCY_CONFIGURATION_V1`,
with maximum_solver_seconds<=1200 and target_resolution:NONE. It must pin source/
spec, nine software files, all ten direct premises, genuine author_calibration
path/hash, and four fresh independent_checker_source/spec/calibration/
producer_controls path/hash pairs. Author summary must bind the same11 software
pins, all70 payload hashes and all29 matching stage rows. The Native calibration
and producer-controls headers are respectively
`INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_CALIBRATION_PASS` and
`INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_PRODUCER_CONTROLS_PASS`, strict impl1,
Checkpoint→Native/method independent_artifact_check/NONE; both pin current Native
source/spec, and the controls gate pins the genuine author summary. Root's saved
ONE admission checks accepted gate/runtime qualifications. Future complete status
is `INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_COMPLETE_PASS`, without graph or target
approval transfer. New code needs fresh applicable finite and full checking.

Calibration's recognized Root-flat plan uses 38 supervisor /22 child /14 worker
words. Future science uses nested solve.command/child_argv/worker_argv/allocation
and identical top aliases, 42/26/18. Current science config/command fields are
explicitly null where genuine fresh gates are missing. No placeholder gate hash,
execution, source-commit identity, numerical status or availability is invented.
