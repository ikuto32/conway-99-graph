# Oriented-triple screen for all mixed groups on the fixed Hadamard support

This is a new finite necessary projection, not a modification of the frozen sixteen-candidate sampler. Only source preparation, calibrated finite construction, and artifact generation are authorized here. There is no solver call in this program. A native pilot would require separate independent semantic/encoding and complete-object calibration gates.

## Question and exact scope

Can each of the twenty six-coordinate support groups be partitioned into two triples, with each triple oriented cyclically, so that every one of the120 directed nonmatching-coordinate arcs occurs exactly once?

The raw twelve-by-sixty support is the one frozen six-prism Hadamard support. Its twenty distinct groups each repeat three times. Every group contains one coordinate from each of six matched pairs; each nonmatched coordinate pair is in five groups. This screen covers **all mixed balanced parity assignments** on this one support together with nonzero local phase amplitudes satisfying the even-relative phase equations. It is not restricted to the previously sampled parity assignment. Constant parity groups are outside its domain. Balance and this fixed support remain additional assumptions. No target automorphism is assumed.

Each group has ten unordered partitions into triples. The triple containing the first coordinate is labeled positive, giving the normalized parity pattern. Each triple has two cyclic orientations, independently, giving40 choices. The orientation `a -> b` means phase difference `t_b-t_a=1` in GF(3). Each choice contributes six directed arcs. There are800 selectors, one per choice, with no auxiliary variables.

There are140 exact-one rows: twenty group-choice rows, followed by the120 directed arcs in lexicographic coordinate order excluding loops and matched pairs. Each row has forty selectors. A direct pairwise exact-one encoding emits one positive clause followed by every lexicographic negative pair. Expected dimensions are800 variables and109,340 clauses. Counts are derived from raw domains and checked rather than accepted as a proof premise.

## Why this screen is necessary and what its converse means

For an all-mixed balanced group, its six affine coordinate maps consist of all six permutations of three letters. The three same-sign phase values are all distinct, so each sign triple has a cyclic phase orientation. On this support all-mixed parity and the necessary zero-or-three disagreement rule imply exactly three disagreements for each nonmatched pair: each such pair is therefore in the same sign triple in exactly two groups. Full Gram requires those two even-relative phases to be1 and2. This is exactly the assertion that its two directed arcs occur once each.

Conversely, a directed-arc cover has each undirected nonmatched pair in exactly two triples. Thus it defines an all-mixed parity projection with three disagreements per pair. Assign phase values0,1,2 cyclically on each oriented triple; shift the positive triple so the first coordinate phase is zero. Local mixed conditions and every even-relative phase equation hold. The negative triple retains a free additive offset in each group. **Odd-relative phase equations are not established by the cover.** They must be checked later, as must full factor Gram, outside-column caps, and any residual completion.

The selected orientation representative saved by the decoder sets each triple's least coordinate phase to zero. It is a local representative, not a solution of the complete phase system. No full factor or target graph is decoded.

The general equivalence above remains CANDIDATE pending independent review. The program's finite controls are not a substitute for that derivation or complete encoding verification.

## Construction controls and limits

Before constructing the research CNF, exhaustively check pairwise exactly-one truth tables for sizes1 through6; check every partition/orientation and literal phase difference for a six-coordinate local fixture; and check a tetrahedron's four consistently oriented faces cover all twelve directed arcs on four vertices. The tetrahedron is a generic directed-arc-validator fixture, not an instance of the research support or an SRG factor. Deliberately corrupt a one-hot assignment, directed orientation, local phase, and arc population and require detection.

Build allocation:30 seconds, no solver, integer arithmetic, streaming CNF; expected small memory. Manifest records actual source commit, exact command, environment/source/input hashes, and all output hashes. Source and spec are frozen before execution. Any failure is retained in its original output directory. Actual RSS is telemetry rather than an independently enforced memory ceiling.

The scope/model/CNF records remain CANDIDATE after construction. An UNSAT result could exclude this all-mixed balanced subfamily only after exact encoding/coverage review and independent full proof replay; it would not exclude constant-containing balanced branches, arbitrary factors on this support, other supports, or Conway99. A SAT result is only an oriented cover until its raw object is independently checked and the omitted conditions are addressed.

## Reproduction

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_oriented_triples.py --out acceleration/results/20260930_hadamard_oriented_triples
```

The decoder API is `decode(assignment, model_path, scope_path)`, where assignment contains all800 signed IDs exactly once. It returns selected selectors, all twenty local oriented choices, all120 exact arc counts, and normalized parity data. It explicitly reports `full_factor:false`, `target_graph:false`, `odd_phase_equations_checked:false`, and `residual_D:null`.
