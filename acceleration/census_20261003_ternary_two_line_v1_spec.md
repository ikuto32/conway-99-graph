# Complete ternary two-line census kernel V1

State: SOURCE_ONLY. The author has not imported, parsed or executed this new
source. This version supplies finite engineering controls only. It does not
read an actual 99-point graph, import native RNG/history/state, run an optimizer,
or launch a scientific census. A future target caller, actual input identity,
new independent engineering/raw checks and ROOT review are separate requirements.
No historical gate approves the new objective or execution.

## Exact domain, objective and fixed population

The domain is a labelled linear 3-uniform hypergraph on `3 <= n <= 99` points,
with exact integer point degree `d > 0`, `2d < n`. Every point occurs in exactly
`d` triples, each triple has three distinct integer labels, and every unordered
point pair occurs in at most one triple. Its complete point graph is simple,
symmetric, diagonal zero and exactly `2d` regular. Positive lambda residual is
allowed. There is no frozen root, required automorphism, fixed support, incidence
kernel assumption, or lambda-zero proposal filter.

Objective version `SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1` is, exactly:

```
r(u,v) = common(u,v) + A[u,v] - 2,  u < v
F3     = sum 1[r(u,v) mod 3 != 0]
E_lambda = sum A[u,v] * r(u,v)^2
E_mu     = sum (1-A[u,v]) * r(u,v)^2
E        = E_lambda + E_mu
```

`residue_population` records the three complete unordered-pair counts for
Python's residues `0,1,2`, including negative residuals. The direction of
improvement is the lexicographic pair `(F3,E)`. Every valid proposal is eligible,
including a proposal increasing `E_lambda` or `E_mu`.

For `n=99,d=7`, the scalar diagnostic is `819820*F3+E`. The conservative
`E <= 819819` bound makes its order equal to lexicographic order. For generic
controls its weight is `choose(n,2)*(2d)^2+1`; `|r| <= 2d` gives the analogous
strict ordering bound. Scores from F60/Froot/earlier objectives are not compared
as if they were this objective.

The exact written papers separately reviewed by ROOT/Structural establish, on
the complete `99`-vertex degree-14 simple graph domain, `F3=0` iff the full
integer SRG identity holds, `F3 <= E <= 28*F3`, and
`(residue_population[1]-residue_population[2]) mod 3 = 0`. Their immutable source
pins are in the code. They do not approve this implementation. New necessary
score checks are only cheap falsification checks; they do not verify a raw graph.
Any target-sized zero must receive a separate complete integer SRG validator.
The scalar upper bound `3977766639` is conservative and is not an objective
lower bound or a search-coverage measure.

The fixed labelled one-move population is all literal triple pairs `i<j` in
lexicographic order and selected positions `ix,jy` in lexicographic order:
`proposal_id = 9*pair_index + 3*ix + jy`. A target-domain input has 231 triples
and exactly `choose(231,2)*9 = 239085` labels. Every invalid or unfavorable label
is retained. This population does not enumerate all graphs or all moves of
other forms, and no connectedness/ergodicity/global optimum/exclusion follows.

## Swap and exact delta

The selected points must be exclusive to their source triples. The two literal
triples may share one unselected point. Remove all four old selected-point
pairs before checking all four new pairs for linearity. Re-added pairs cancel
in the sorted net-toggle set. All valid moves preserve point degree/linearity;
there is no lambda acceptance rule. Scores update all unordered pairs touching
any changed adjacency row. Before and after costs use their own adjacency
category, so a switched edge changes lambda/mu membership explicitly.

The 24 closed record fields are:

```
schema, objective_version, proposal_id, i, j, ix, jy,
old_triples, new_triples, valid, invalid_reason, conflict_pair,
removed_pairs, added_pairs, toggles, changed_rows,
delta_F3, delta_E_lambda, delta_E_mu, delta_E, delta_scalar,
new_metrics, tuple_direction, classification
```

Schema is `TERNARY_TWO_LINE_LABELLED_PROPOSAL_V1`. All IDs/coordinates/scores are
literal integers; `valid` is a literal boolean. Invalid records retain the exact
structural invalid reason and any proposed replacement triples/conflict pair,
with every score/toggle/changed-row field explicitly null. Selection failures
have null replacement triples. Valid records carry ordered four-element removed
and added pair lists, sorted cancellation-aware toggles, exact integer deltas,
and `new_metrics` with exactly `F3,E_lambda,E_mu,E,scalar_weight,scalar,
residue_population`. Classification is `valid_F3_down/equal/up` or the structural
`invalid_selection/invalid_linearity`; `tuple_direction` independently records
the exact pair's `down/equal/up` comparison. Canonical byte comparisons reject
boolean/float aliases even when Python numeric equality would agree.

## Files, prefix/resume and retention

Parts are canonical sorted JSONL, gzip level 1, mtime 0, at most 5000 records,
8192 bytes per complete line. Exact compressed/raw SHA256 and byte lengths,
start/end/count identify every part. A prefix has contiguous strictly integer
IDs from zero. The five-key checkpoint schema
`TERNARY_TWO_LINE_CENSUS_CHECKPOINT_V1` is `schema,identity,next_proposal_id,
parts,aggregate`; all identities and aggregates are compared canonically.
Before resuming, every saved raw record is freshly recomputed against the same
graph/objective/software and the complete prefix aggregate is reconstructed.
This is producer checking and still requires an independent complete path.

The manifest schema is `TERNARY_TWO_LINE_CENSUS_MANIFEST_V1`. It distinguishes
fixed population, completed prefix, new streamed evaluation calls, labelled
counts, unique valid raw neighbor matrices (net toggles; no isomorphism collapse),
all minimum-F3 ties and all minimum-`(F3,E)` ties. The selected neighbor minimizes
`(F3,E,proposal_id)`. Ties are not dropped to favor a result. Baseline and every
distinct observed residue-zero adjacency are saved with literal ordered triples;
raw adjacency SHA identifies duplicates. A generic fixture zero is explicitly
not a target-99 certificate. Zero records are candidates pending independent
full integer validation. There is no RNG/state/history to fabricate.

Checkpoint/progress and all hashes/write/setup share the worker deadline.
Enumeration cooperatively stops with 20 seconds remaining and preserves the
current part/checkpoint/ties/manifest. An unfinished prefix has status
`UNKNOWN_PREFIX_ONLY` and cannot establish absence of improvement. A complete
producer manifest is `CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK`. No automatic
retry, threshold extension or target-level coverage claim exists.

## Shared components and independence

The pinned `census_20261003_weight60_two_line_v2.py` supplies only exact domain,
exclusive two-line topology, net-toggle reconstruction and raw adjacency format.
Its computed root-0 diagnostic is unused; it freezes no root and all pairs are
included here. Its old objective/gates/main/selection rule are not invoked. The
new scorer computes its own F3/residue/category costs and crosschecks category
deltas against this shared component; that agreement is not independent proof.

The pinned restricted-three-line V3 file supplies only strict JSON/canonical
encoding, bounded part IO, output saving and software/runtime pins. No restricted
three-line domain/proposal/scorer/main is called. Its two pinned historical
structural dependency files are included in the software closure transparently,
although their mathematical kernel is not invoked by this source.

The pinned ternary reference `692ecf...` is used for author finite controls only,
with a direct integer matrix scorer and raw pair-occupancy reconstruction. Its
author is Structural; it does not by itself independently approve Native's
changed code. A future independent gate must disclose shared components and
check the raw changed-objective artifacts through a separate exact formulation,
including invalid/unfavorable labels, category switches, signed residues, all
ties, checkpoints, inverse moves and raw matrices. Producer agreement, agent
agreement and source/schema validation are not mathematical verification.

The software manifest contains 18 exact sources/specs/papers/runtime files.
Python/tqdm versions, working directory, source-context commit, actual command,
deadline state, raw parts/checkpoints and failures are saved. The current Git
context does not claim that uncommitted new sources are part of that commit.
Artifact availability remains LOCAL_ONLY until a separate public byte check.

## Declared finite engineering population

Literal rook9, prism9 and cube12 degree-2 hypergraphs give complete canonical
`i<j` populations `135+135+252=522` labels. The design reference's ordered
both-directions fixture population is different; it is not silently substituted.
Each runs whole, prefix17, and exact resume to completion: 1044 streamed proposal
evaluation calls, three equality checks. Fresh record checks, raw reconstruction,
scalar rescoring and negative controls add checking calls; they are not additional
distinct labels and are not included in that streamed-call counter.

Every valid label gets full raw candidate reconstruction, all-pair direct scalar
reference scoring and an exact inverse raw graph check. All labels get raw
reference feasibility checking. Required positive branches are valid overlap,
valid disjoint, changed row0 (frozen-root restriction absent), and positive-lambda
candidate. Rook9 gives known-valid generic zero; prism9 gives an allowed graph
with positive lambda energy. Signed residuals `-2,-1,0,1,2,3,6,12` give eight
arithmetic positives.

The exact 160 strict negative cases are predeclared by the source:

- For each of three fixtures: five cache aliases; five delta corruptions;
  four metric corruptions; boolean and float record IDs; two schema/objective,
  two direction/classification, one float-toggle and one forged-invalid-score
  corruption: 22 per fixture.
- Twelve checkpoint/prefix corruptions per fixture: empty boolean/float next,
  boolean/float identity, empty boolean/float counts, extra header, old schema,
  wrong next, float bestF3, and boolean/float limit.
- Twelve part/raw corruptions per fixture: boolean/float start, wrong count,
  gzip/raw hash, gzip/raw bytes, escaping path, shifted IDs, rehashed boolean/
  float raw IDs, and a rehashed forged score caught during resume.
- Ten exact pair-cost type/domain corruptions, seven graph-domain corruptions,
  three strict JSON corruptions, one invalid candidate and one float-mask score:
  22 global cases.

The rejecting harness accepts only the declared local or pinned shared
`CheckError` classes with the precise expected `stage`, never an arbitrary
ValueError/timeout/missing artifact. Controls save each corrupted object and
actual diagnostic. Source authentication precedes the source's failure handler;
an authentication/import/syntax failure is preserved by the contained supervisor,
while failures inside engineering also save `failure.json` and partial objects.
Unattempted controls remain unattempted, not successful.

Proposed author allocation is 180 seconds outer, 150 worker inclusive, 20 seconds
cooperative saving and 20 shutdown. This is a prospective small-fixture allowance,
not a historical build/solver cap or target-throughput prediction. The actual new
ternary-control runtime is unknown. Source-only plan review, fresh ownership/
resources and explicit ROOT authorization are required before a single invocation.
No scientific F3 run or stochastic engine is authorized by this specification.
