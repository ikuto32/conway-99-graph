# Fixed seventeen-point selected-triangle family, version1

SOURCE_ONLY preparation by `/root/structural`. No import, parse execution,
controls, enumeration, solver or new mathematical approval has occurred.
This is a new finite geometry producer. Native will own a different-source
complete record verifier; ROOT owns each exact invocation authorization.
No previous circuit fixture, moment result or native gate approves this code.

## Exact question and hypotheses

Which of the 5,184 labelled assignments below have a linear actual-triangle
collinearity graph with adjacent common-neighbor count1 and nonadjacent count
at most2? This question is about selected local geometry, not a 99-vertex
completion or a complete induced subgraph. No ambient extra-edge set, exterior
moment model, symmetry, isomorphism classification, forced word or target
nonexistence statement is produced. No circuit-minimality conclusion is made.

The family is motivated by candidate6f26 and the separate written audit31d2.
Those immutable sources prove only a necessary shape for a twelve-column
unbalanced GF(3) right-kernel word in a target. The present program independently
rechecks local triangle/word conditions for each literal assignment. Its result
must receive independent whole-record verification before any finite claim.

## Labels, exhaustive labelled universe and signs

Points are s=0,t=1,x=2,a=(3,4,5,6),b=(7,8,9,10),
r_left=(11,12,13),r_right=(14,15,16). The seven negative rows, in this exact
order, are

```
(0,1,2),(0,3,4),(0,5,6),(1,7,8),(1,9,10),(11,12,13),(14,15,16).
```

Choose one left and one right r for the first positive row containing x:
3*3=9 choices. Choose a bijection from the four ordered a points to the four
b points:4!=24 choices. The remaining four r points, initially sorted by
literal point label, are assigned bijectively to these four positive a-b
rows:4!=24 choices. Their final row order is a0,a1,a2,a3. The first positive
row precedes them. The coefficient vector is seven -1 followed by five +1.
Its coefficient sum is -2, or1 over GF(3).

Both permutations use `itertools.permutations(range(4))` lexicographic order.
With left/right choices L,R and permutation indices B,T,

```
proposal_id = ((3*L+R)*24+B)*24+T,    0<=proposal_id<5184.
```

Successive quotient/remainder by24,24,3 gives a unique inverse. The Cartesian
product covers every selection in this fixed labelled representation. Relabelling
an abstract necessary-family member into these point names is not an assumption
that the target has an automorphism. No quotient by relabelling is taken.
The graph hash deduplicates literal17x17 adjacency matrices only. It is not an
isomorphism hash. Hash groups retain all contributing proposal IDs; independent
verification must also compare exact matrices against hash-collision ambiguity.

The candidate literal ID51 is a handwritten relabelling of the previously
written17-point example. Its last five rows are

```
(2,11,14),(3,7,12),(4,9,15),(5,8,16),(6,10,13).
```

No successful execution of this positive has been guessed. It is a required
finite positive; if it fails, the command must preserve the failure and stop.

## Independent arithmetic and exact validation order

The producer uses Python integers and full scalar adjacency multiplication,
without importing old topology, native, moment, scoring or reference modules.
It imports only the unchanged deadline helper. A row creates all three edges;
the matrix is symmetric binary with diagonal0. Complete common-neighbor matrix
is genuine A*A including diagonal equal to graph degree, not an off-diagonal
cache convention. All17*17 entries are emitted for every case.

First rejection stages are: ROW_SHAPE,ROW_TYPES,ROW_RANGE,
ROW_DISTINCT_POINTS,DISTINCT_ROWS,PAIR_LINEARITY,COEFFICIENT_POPULATION,
COEFFICIENT_TYPES,COEFFICIENT_DOMAIN,SIGN_COUNTS,GF3_WORD,SELECTED_DEGREES,
then matrix shape/type/binary/diagonal/symmetry, EDGE_CN,NONEDGE_CN,
ACTUAL_TRIANGLE_FAMILY. Every integer guard excludes booleans/floats explicitly.
The selected degrees must be exactly two3s and fifteen2s. Every GF(3) row is
checked from the integer signed incidence sum. Actual triangles are enumerated
independently from all C(17,3) triples in the graph and compared to the sorted
literal selected rows. Edge and nonedge checks use full integer intersections;
the first pair is the literal lexicographic pair. Rejected cases remain records.

## Complete raw objects and checkpoints

Each record has exactly these16 fields:

```
proposal_id,role,negative_centers,triples,coefficients,adjacency_rows,
common_neighbors,selected_degrees,graph_degrees,actual_triangles,
integer_incidence_sum,coefficient_sum_mod3,valid_local_geometry,
first_veto,veto_detail,labelled_graph_sha256.
```

The role has four exact integer coordinates x_left_choice,x_right_choice,
ab_permutation_index,r_permutation_index. Negative centers are exactly[0,1].
Adjacency rows are17 strings of17 ASCII binary characters. The graph SHA is
computed from these rows joined by newline plus one final newline. The raw
triples retain sign order and point order. The common-neighbor array contains
289 literal integer values. Validity is a genuine boolean; the veto is null
for a valid case and a first-stage string for an invalid one.

All5,184 records are retained in fixed128-case parts:41 parts, last64. Each
part is `{schema,start,stop,records}` and covers exactly[start,stop). Each
part-end checkpoint is `{schema,next_proposal_id,tallies,valid_graphs,parts,
coverage}`; it retains the exact labelled prefix, cumulative classifications,
graph-hash-to-all-valid-IDs map and literal part hashes. Valid cases also have
individual complete raw records. `valid_graph_groups.json` is the final map.
No resume mode is claimed. A interrupted run preserves its completed labelled
prefix and any partial final part, but is not a complete family result.

Progress is printed after every128 records. No numerical endpoint/count of
valid cases or distinct graphs is hardcoded. Complete success requires5184
records,41 parts/41 checkpoints, a canonical ordinal reconstruction, all16
fields/289 CN cells/actual triangles/first vetoes and exact grouping verified
by the different-source checker. No sampled verification can satisfy this.

## Separate finite controls

Five positives are the old literal17 example, the mapped ID51 example, the
ID51 decoder, the last ordinal5183 decoder, and a single isolated triangle
padded to17 vertices for the general local-cap routine. Only the two complete
family fixtures assert twelve rows and the word conditions. The triangle
fixture tests local-cap arithmetic alone. Durable positive payloads include
actual full computed products; their provenance remains producer self-checking.

Twenty-six negative cases are literal malformed ordinals4, row mutations8,
coefficient mutations6 and matrix/cap mutations8. K4 padded to17 rejects
EDGE_CN; K2,3 padded to17 rejects NONEDGE_CN. Typed false-at-zero and float-one
fail before arithmetic. All expected/actual first stages and damaged case
payloads are saved in `controls.json`; original valid inputs and the five
positive results are saved in `positive_fixtures.json`. No actual target input
or complete family enumeration is read by this controls command.

The independent checker should reconstruct the two literal fixtures from
different neighborhood sets, reconstruct both ordinal inverses, rederive
the K4/K2,3 negatives and reject corrupted case/role, boolean CN/count, missing
or duplicate ordinal/part/checkpoint, shifted prefix, sign-row permutation,
wrong product diagonal, changed graph grouping or count-preserving ID shuffle.
Its source and applicable controls must be frozen before producer census output.
This is a required separate path, not an existing gate or inferred approval.

## Deadline, outputs and trust

One deadline starts before input hashing and spans the controls or enumeration,
all record construction, file writes, closure hashes and final serialization.
The outer supported Windows supervisor starts before locked/offline uv.
The worker preserves20 seconds for output/shutdown and checks after every
closing write/hash. A failure/nonzero exit invalidates any provisional PASS
summary; historical bytes remain untouched. Partial prefix is saved on a
cooperative deadline stop. No retry is automatic and no resume is claimed.

Prospective controls allocation60outer/40worker/20internal save/10shutdown
is justified by five tiny17-point fixtures and26 first-stage failures.
Prospective complete enumeration180outer/150worker/20save/20shutdown is
justified by roughly51million scalar product summands plus bounded17-point
triangle checks and raw JSON output. No measured enumeration throughput is
claimed; ROOT may review a changed allocation in a new exact plan. Six hours
is a per-invocation ceiling, not a target. No native child, solver or RNG runs.

Source, spec, three written geometry inputs, deadline/policy, locked uv and
supported containment are disclosed trusted components. The independent
checker may share immutable IO/deadline conventions but must not import this
producer decoder, graph builder, validator, grouping or summaries as truth.
Canonical producer `/root/structural`; all generated conclusions remain
CANDIDATE until independently checked and ROOT-reviewed. Target resolution
NONE, target exclusions0, ledger/index/Git mutations0 in every mode.
