# Actual adjacency-switch API harness V1

Prepared by `/root/structural` at 2026-10-03T16:43:36+00:00. SOURCE_ONLY,
UNCOMPILED and UNEXECUTED. There is no binary, build command, invocation,
passed finite control, API gate or scientific authorization. ROOT owns separate
whole-source/build/control review and execution authorization. This harness is
an author component; Native's independent source/checker and ROOT's execution
review must not treat it as its own verification.

Source `acceleration/probe_20261003_adjacency_ternary_switch_api_v1.cpp`, SHA256
`de63220d17edc8a9d955db2665aaa20606031dc8913218b2fea4f7766b9dc9d3`.
It includes exactly the frozen pure kernel
`adjacency_ternary_switch_kernel_20261003_v1.cpp`, SHA256
`b10b8a10691a15a1f0e4133944fc634b5d7ba36199a37da8f0c1bae3089fe541`.
It does not include the census driver, another engine, oracle or verifier.
No source is rewritten and no previous source gate approves this harness.

## Actual branches and raw interface

For every fixture proposal the harness copies the fixed actual `Graph`, calls
its actual `apply`, then obtains `adjacency`, `full_product_cache` and `metrics`
from actual getters. It serializes these values without recomputing a matrix
product or substituting a reference cache. Every invalid proposal exposes the
unchanged candidate snapshot. Every valid proposal gets a canonical inverse
old-edge pairing, calls `apply` again on the candidate and exposes the inverse
record and restored snapshot. The inverse pairing is selected solely by exact
equality of the two added/removed unordered edge sets; this calculation is not
an independent correctness proof. The fixed base's actual getter snapshot is
also emitted before and after every complete fixture population.

`Graph` has no rollback API. This harness checks observable copy preservation,
invalid-apply immutability and reverse application; it does not claim an
unavailable rollback branch. Internal transactional failure is not deliberately
injected into private state. Full-cache correctness must be established from a
separate full adjacency reconstruction and independent product in the verifier.

Each complete tiny fixture emits `<fixture>.probes.jsonl`:

- A header with exact keys `schema`, `fixture`, `declared_roles`,
  `baseline_before`; schema `ADJACENCY_SWITCH_API_FIXTURE_HEADER_V1`.
- All proposals in lexicographic canonical edge-pair order, both orientations
  0 then1, retaining shared endpoints and new-edge-present rejections.
- A footer with exact keys `schema`, `completed_roles`, `baseline_after`;
  schema `ADJACENCY_SWITCH_API_FIXTURE_FOOTER_V1`.

Per-role schema is `ADJACENCY_TERNARY_SWITCH_NATIVE_API_PROBE_V1`. Besides its
schema key, it preserves the ten proposed fields: `proposal_id`,
`canonical_old_edges`, `orientation`, `kernel_record`, `before`, `after`,
`invalid_apply_unchanged`, `reverse_role`, `reverse_kernel_record`, `restored`.
The first two edges are the literal input edge coordinates, even in the
auxiliary noncanonical/range negative cases. In the complete fixture stream
they are canonical actual edges. IDs and all coordinates are integers.

Every snapshot has exactly `n`, `degree`, `flat_adjacency`,
`flat_true_A_squared`, `F3`, `E_lambda`, `E_mu`, `E`, `scalar`,
`residue_population`. Arrays are row-major actual integer vectors. This cache
has its true degree diagonal, never the historical triangle cache's zero
diagonal. Each metric subrecord has six keys: F3, E_lambda, E_mu, E, scalar and
the three-bin residue population. `kernel_record` has the literal actual role,
boolean valid, diagnostic, affected_unordered_pairs, before_metrics,
after_metrics, delta_F3, delta_lambda, delta_mu, delta_E and delta_scalar.
Invalid cases have `invalid_apply_unchanged` boolean and three inverse fields
null. Valid cases have that flag null and all inverse fields nonnull. Neither
a nonnull inverse nor a successful process exit is independent approval.

The exact complete tiny population is510: rook9 degree4 gives306 roles,
triangular_prism6 degree3 gives72, and cube8 degree3 gives132. Fixtures are
constructed from the literal generic row/column, prism and bit-XOR definitions;
none reads a scientific matrix or imports triangle rows. An additional
`synthetic99_14.probes.jsonl` contains exactly two declared probes
(0,1,20,21,orientation0/1) on the circulant with offsets plus/minus1..7. These
two synthetic probes are separate from510 and do not enumerate479556 labels.
The full99/cache snapshots remain engineering examples, not a target graph.

`negative_calls.jsonl` has exactly12 direct API calls, separate from the labelled
fixture roles. Six constructor cases preserve all literal malformed integer
arrays and expected/actual diagnostics: dimensions, shape, binary, symmetry,
diagonal and degree. An unexpected acceptance retains the actual constructed
snapshot. Six role cases retain the complete actual probe packet: range,
orientation, noncanonical old edges, shared endpoints, absent old edge and
present new edge. Expected stages are declared in source; the verifier must
check every observed stage independently. These calls do not test the census
driver's raw graph parser or nine-pair CLI. JSON bool/float corruption tests
belong to the independent packet decoder and remain separately required.

## Deadline, receipt and verifier contract

The CLI is exactly four distinct option/value pairs: `--out`, `--seconds`,
`--save-seconds`, `--source-context`. Positive finite seconds must exceed the
save reserve; the context is literal40 lowercase hex. The timer starts at main
entry before parsing/fixture construction. Cooperative checks surround every
record serialization, flush, closed-file rename and final manifest write.
The exact finite Graph constructor/apply have no internal deadline callback;
their bounded99-vertex call cost is not yet measured. A supported external
contained supervisor is required, with all compiler/setup/native/receipt work
charged to its own reviewed invocation deadline. No allocation is selected
here from historical throughput.

Every probe file is written as `.partial`, flushed record by record, then closed
and renamed only when its complete population and footer exist. A signal/time
exception retains any partial file and writes `failure.json` with completed
counts and no retry. There is no resume option and no completeness inference
from a truncated stream. A closing-guard failure can coexist with a provisional
manifest; nonzero/failure is never approval.

`manifest.json` has schema `ADJACENCY_SWITCH_ACTUAL_API_HARNESS_V1`, status
`COMPLETE_CANDIDATE_REQUIRES_INDEPENDENT_API_REPLAY`, producer Structural,
source context, literal kernel SHA metadata, complete_tiny_roles510,
synthetic99_probes2, negative_calls12, timing and explicit false target-read,
RNG, rollback-API and independent-approval flags. The literal kernel SHA in C++
is metadata, not an implementation of native hashing. A future reviewed build
and bounded wrapper receipt must bind exact harness/kernel source hashes,
compiler argv/version/binary hash, actual child argv/cwd/UID, all output hashes
and actual external containment. A full native driver stream is a separately
required artifact and is not emitted by this API harness.

The prospective independent path must check all actual before/after/restored
adjacency and true cache cells, all metric/histogram/delta fields, exact role
classification, every inverse and every fixed-base footer. It independently
replaces all four matrix edges and computes full integer products/scalar set
intersections without importing the pure kernel/harness. It must also falsify
typed packet alterations, changed cache0/1/diagonal values, final adjacency,
metrics/deltas, inverse role, unchanged flags, missing/duplicated/swapped IDs,
header/footer population and changed source/binary/receipt identities. All
required corruptions need a new frozen finite plan before actual checking.

The old V2 controls-plan API fields were a source-only contract. This source
fills its null harness path with a concrete implementation; it does not mutate
that preserved plan, provide its missing binary or emit its prospective gate.
The existing19-field independent driver calibration did not test these getter
branches. No old gate transfers, no ledger/index/Git mutation and no scientific
execution follow from this specification.
