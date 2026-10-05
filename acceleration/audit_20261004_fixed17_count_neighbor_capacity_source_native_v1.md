# Different-author static review of the count-neighbor capacity screen

Reviewed complete frozen source `screen_20261004_fixed17_count_neighbor_capacity_v1.py`, SHA256 `4d737ba3b8ea90df487a1b71cbc6fe4f8baf38234533fdc9115bb76034556371`; spec `35281d5f41ca2a49d872152d9d286c6f2b56f6b510bf7e1ea5fbd91d154b82d6`; complete source-only plan `503a6598`, including all calibration 38/22/14 vectors and nondispatchable scientific template. Checkpoint authored the producer. Native independently derived the mathematical row bound in written report `910a740a`; shared frozen count/pair premises and common wire conventions are disclosed. No producer import, syntax test, code execution, actual 472-vector calculation or scientific raw-part replay occurred in this review.

No material static veto was found in the requested arithmetic, fixture precedence or declared finite calibration framing. This is source review only, not a calibrated implementation or approval of a later screen result.

## Literal mathematics and slots

The kernel strictly checks the complete H shape/binary symmetry/zero diagonal, ordered unique mask domain, exact integer counts and their outside total, and complete typed triangular bit table. Python bool/float counts, masks, graph entries, pair coordinates and bits do not alias integers. Empty-bit coexistence is checked before row calculations; off-diagonal positive populations reject, while diagonal population1 is legal and population2 rejects.

The labelled pool is ordered by type and copy. For a focal positive type i, exactly `[i,0]` is removed. Remaining copies of type i stay in the pool. Eligibility requires bit1. Only literal `[1]` forces a slot; `[0,1]` gives an optional slot, `[0]` permits no edge, and an empty set has already enforced coexistence. Equal-type records refer to distinct vertices; the current vertex never becomes its own neighbor. One representative per type is sufficient for these bounds because relabeling copies leaves their type/bit/capacity inputs unchanged. It does not make actual neighbor profiles uniform.

Required outside degree is target_degree minus type size. The incidence vector is exactly `2-t-Ht`, consistent with adjacentCN1/nonadjacentCN2; the rook fixtures deliberately use degree4 with the same cross-CN equation. Mandatory-copy degree and point sums are subtracted once. A negative residual degree reports MANDATORY_CAPACITY; a residual larger than optional slot population reports NEIGHBOR_CAPACITY. Both leave extrema and attaining labels null for every retained Q row. They do not fabricate finite bounds for an empty selection problem.

When the residual degree is valid, sorting `(overlap,type,copy)` tuples and taking its first/last d entries is the exact unconstrained slot extremum. The d=0 high-end special case correctly gives the empty selection rather than Python's entire `[-0:]` list. The selected labels are distinct and deterministic under ties. Bounds include the mandatory sum, use a closed interval, and retain every Q and later type after the first failure. Q order is size1, size2, size3 lexicographic, then full support; size at least4 keeps these families disjoint. For17 the count is834, not all131072 masks. Passing separately attainable bounds does not establish one common selection.

## Hand reconstruction of calibration fixtures

The four-corner rook H is the square on grid points `(0,0),(0,1),(1,0),(1,1)`. The outside masks in increasing order are0,3,5,10,12. The empty mask corresponds to `(2,2)` and is adjacent to all four other outside vertices. The only other edges are masks3--12 (outside column2) and masks5--10 (outside row2). This exactly matches the six declared forced pairs. Each type has one copy, so diagonal allowed bits do not force an actual self edge. Free-bit fixtures contain the actual neighborhood and therefore pass all necessary intervals; forced fixtures reproduce its exact sums with residual degree0.

The repeated type15 fixture has matching H4, target_degree4 and two copies. Its exterior degree is0 and every `2-t-Ht` entry is0. The equal bit `[0]` permits two distinct nonadjacent copies. It passes the row kernel and is explicitly not a qualified complete graph/moment-model fixture. There is no spurious universal multiplicity1 cap.

The four expected geometric rejections are correctly reachable: the isolated single copy has degree1 but no remaining slot; changing the rook degree to6 gives its empty focal type demand6 against four slots; changing the forced rook degree to3 gives its empty focal type four mandatory slots against demand3; the five all-empty copies have degree4 and four optional zero-overlap slots but singleton demand2, so the first failure is ROW_BOUND. The separate all-empty equal-bit-empty fixture rejects EQUAL_MULTIPLICITY earlier in packet validation.

All31 literal routes were checked by source precedence on paper:

| Population | Routes and first stage |
|---|---|
| Eight positives | free rook; forced rook; self exclusion; forced sums; budget20.000001; exact-shaped count gate;834-Q order; repeated type15 zero outside degree |
| Five count negatives | bool/float COUNT_INTEGER; negative COUNT_BOUND; missing COUNT_SHAPE; changed total COUNT_SUM |
| Three mask negatives | bool/float TYPE_MASK_INTEGER; reverse TYPE_MASK_ORDER |
| One graph negative | Boolean diagonal GRAPH_DOMAIN |
| Four pair negatives | Boolean coordinate PAIR_COORDINATES; Boolean/reversed bits PAIR_BITS; missing row PAIR_POPULATION |
| One empty-bit coexistence | INCOMPATIBLE_COEXISTENCE |
| Four retained geometric failures | isolated and shortage NEIGHBOR_CAPACITY; forced excess MANDATORY_CAPACITY; empty-vector ROW_BOUND |
| One equal multiplicity | EQUAL_MULTIPLICITY |
| Two gate negatives | unchecked flag and bool population COUNT_GATE_SCOPE |
| Two budget negatives | remaining20 and stop-required SAVE_RESERVE |

The counts are8+23=31. Six positive actions return saved objects and four ScreenReject actions return full rejected tables, giving10 result files plus31 payloads, controls and summary =43 physical/42 nonsummary files. Gate/Q helper positives return no result, which the plan correctly discloses. These are proposed outcomes, not observed executions.

## Input, save and runtime boundaries

Scientific configuration requires authentic count/full and Root acceptance plus exact five fixed count artifacts and pair/full and Root receipt. The candidate flags, literal ordered masks, counts and presence equivalence are rechecked; the packet repeats their integer shape/domain/total. All23 raw pair parts are taken from direct pins in the genuine complete pair gate. All111628 labels/masks/19 fields and sorted integer bit sets are consumed to EOF. The combined bits use the same intersection of upper/lower/CN sets, with classification. Raw Gram integers themselves are trusted from the already accepted pair gate, not independently recomputed here; the source and spec do not claim new inverse or Schur checking. Its47 nonsummary source outputs are authenticated, and checkpoint bytes are inherited immutable premises rather than newly calculated prefixes.

The row theorem report is configured as an explicit pinned external mathematical premise. This producer merely authenticates its bytes; it does not validate an arbitrary theorem-status string or independently approve that proof. The final concrete configuration/Root authority must bind the genuine `910a740a` report and any Root acceptance. The existing null scientific template cannot launch.

Reader/path helpers bound files at64MiB before and during chunk reads, reject links and path escapes, and use strict duplicate/nonfinite JSON. Loop/hash and save boundaries share the worker deadline. Success saves guard before serialization/open/write, after flush/fsync, after rename, and after the final summary/closing input pass. Output hashes precede summary and exclude it. Failures preserve prior type files and best-effort failure diagnostics; no retry or solver is called. Calibration command uses supported593 Windows supervision before locked/offline UV,150 inclusive worker/180 outer and20 shutdown. Actual suspended/resumed/reaped empty Job receipt is still required.

Two exact limitations should govern any later acceptance rather than be inflated from spec shorthand. `packet`, `q_universe`, some comprehensions and JSON parsing are finite atomic helper regions without an internal tick on each iteration; the source does not prove the spec phrase “every loop” literally, nor a hard real-time20-second reserve. Also the best-effort failure save is outside success reserve guards and can itself fail or be cut off; saved earlier outputs are the durable facts. Supported actual outer containment is separate evidence. These limitations do not alter the row arithmetic or justify an inherited/new gate before actual controls.

This review approves no actual counts/culprits, complete56712 row population, graph rejection or graph completion. A different checker should reconstruct labelled slots with independent cumulative histogram extrema, verify every row/witness/first-failure ordering and per-type checkpoint, authenticate literal runtime and producer controls, and require a clean actual terminal. The shared count/pair/type/theorem evidence must remain explicitly trusted and byte-pinned. Current and historical ledger/index/HEAD identities are observations, never mathematical premises or automatic launch permission.
