# Finite weight5 trianglepath author controls V1

Prepared2026-10-02. UNEXECUTED; no optimizer, graph search, ledger operation
or publication. Preserve the existing weight7 source versions unexecuted.
Source: acceleration/theory_20261003_triangle_image_weight5_v1.py.
Discovery note SHA f175e6803924056cbaee112f2430b010f21277cb5792d1ce104ed9cb6c9f60c4.

Exact hypothesis is a finite simple adjacency graph with every edge having
one common neighbor, and the complete family of actual graph triangles.
Trianglepath count P=sum_t sum_{unordered p,q in t}(r_p-1)(r_q-1);
each raw weight5 support has at most two unordered path preimages. General
irregular conclusion is distinct imagewords>=ceil(P/2). Uniform incidence
has P=3m(r-1)^2; hypothetical target m231/r7 gives P24948,N5>=12474.
No nonzero kernel, rank upper bound, generic-code bound or target conclusion.

## Frozen raw populations

Seven adjacency fixtures: one triangle; friendship7 on15points; one meeting
pair plus disjoint triangle on8points; loosechain3 on7points; three disjoint
triangles on9points; loosecycle4 on8points; rook9. Every actual triangle
and all62 three-triangle combinations are saved. Exactly23 paths are
present, yielding14 path-generated supports across the seven separate
fixtures. Counts across fixtures are engineering populations, not distinct
words in one common code. Full small-image enumeration has234 coefficient
masks across seven graphs; it is neither target image enumeration nor a
proof of the universal injection/multiplicity statement.

Rook must have18 paths/nine distinct weight5 supports/all fibers of size2.
Loosechain has one path/word. Triangle and friendship have zero paths.
All three support shapes2K2+isolated, P4+isolated andC4+isolated must occur.
The general irregular and regular formulas are independently recorded.

Raw artifact schema TRIANGLE_IMAGE_WEIGHT5_PATH_FIXTURE_V1 has:
label, vertices, sorted edges, actual_triangles in lexicographic order;
vertex_triangle_counts; all_triangle_triples with sorted triangle_indices,
exact support, weight and intersection_pairs; path_records; support_fibers;
path_count/distinct_path_words/path_word_lower_bound/irregular_path_formula;
regular_r and regular_path_formula (null when nonuniform, infer reason from
vertex_triangle_counts); complete_small_image_records (coefficient_mask,
support), complete_small_image_size and complete_small_image_weight5_words.

Each path record contains sorted triangle_indices, central_triangle_index,
sorted intersection_points, support, isolated_vertex, induced_edges,
induced_shape, perfect_matchings, and candidate_preimages. Each candidate
preimage saves matching_edges, corresponding unique edge_completions,
and sorted triangle_indices. Each support fiber saves support, all unordered
triangle-index triples, and multiplicity. Raw inverse candidates must agree
with the complete path fiber, not only recover one producer-selected path.
Code imagewords are literal point supports, not isomorphism classes.

Fifteen raw rook corruption cases are frozen: dropped path, changed support,
isolated vertex, induced edge, shape, matching, completion, central index,
fiber, pathcount, distinctcount, irregularformula, regularformula, complete
smallimage record, and actualtriangle. Each must reject at the exact staged
InvalidControl string saved by the source. Two missing-premise fixtures
(Pasch pointgraph and completeK7) must reject at SCOPE_EDGE_CN1. Thus there
are17 strict negatives. Three explicit actualK7 triangle paths sum to the
same five-set; preserve them as a falsification of extending fiber<=2
without the common-neighbor hypothesis. Pasch/K7 are not target fixtures.

## Prospective execution and verification

Proposed one author invocation60seconds outer/40worker,10second supervisor
shutdown guard; the worker checks a10second internal serialization reserve
between its seven tiny fixtures. Seven graphs/max128 coefficient masks and
small corrupted records justify this allocation, rather than a historical
solver default. No retries. Partial completed files and exact failure/deadline
diagnostic survive any stop; no failure is a mathematical refutation.

Use UV_PROJECT_ENVIRONMENT=build/research-venv and uv run --locked --offline
--cache-dir .uv-cache-20260917 acceleration/run_compute_command.py. New worker:

  <absolute>/build/research-venv/Scripts/python.exe
  <absolute>/acceleration/theory_20261003_triangle_image_weight5_v1.py
  --mode controls --seconds 40 --source-sha256 <source hash>
  --protocol-sha256 <spec hash>
  --out <absolute>/acceleration/results/20261003_triangle_image_weight5_controls01

Supervisor output is20261003_triangle_image_weight5_controls_supervision01.
Source/spec/note/deadline/supervisor/uv.lock/pyproject.toml hashes, actual Git
HEAD and command/cwd/Python version are saved. Source may not yet be committed;
historical source2d578 is context only. Seed null because no random generation.

Expected author status is AUTHOR_TRIANGLE_IMAGE_WEIGHT5_CONTROLS_V1_PASS,
with mathematical_status CANDIDATE and independent_approval false. Raw outputs:
actual_graph_fixtures.json;17 deliberately corrupted artifacts, including
two missing-premise records; strict_controls.json; missing_premise_controls.json;
candidate_constants.json; summary.json. Corrupt Pasch/K7 raw objects are in
missing_premise_controls rather than standalone input files. Shared producer
rechecking is only author calibration. No numerical thresholds are involved.

Independent reviewer /root/checkpoint_audit has separately written a universal
proof (acceleration/audit_20261003_triangle_image_weight5_v1_proof.md,
SHA8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee)
and will reconstruct complete raw adjacency/trianglepaths/inverse fibers and
small imagewords without importing this implementation, testing actual
corruption controls. ROOT reviews the scope before any new code dual.
Agent agreement or this finite report cannot promote the universal theorem.

The denominator for a future target character row is binom(99,5)-12474;
sign/constant formula is sum_nonzero Aw*(N5-K5(w))<=binom(n,5)-N5. No changed
LP is authorized. Old bound85 and its artifacts remain unchanged. Novelty,
external review and overall target search coverage are UNKNOWN.
