# Factor permutation annealer prototype, 2026-09-30

Status: producer design and calibration only, CANDIDATE pending independent review.
No broad restart campaign is authorized by this document.

## Frozen question and scope

Can exact integer swap deltas on a CUDA device reproduce a separate CPU full
recomputation and the Python set-intersection reference for the same sequence?
The two enabled research cores are the separately audited standard-matching
triangle core with P12 shift6 and the six-prism core with P12 identity. No target
automorphism is assumed. Generic cores require a future separately saved audit
and new source version. SRG243 is a positive calibration fixture only.

For n=12, each fibre's column catalog is all 60 distinct nonmatching unordered
pairs of its internal perfect matching. C0 is lexicographic and fixed. C1 and C2
are independent arbitrary permutations of their catalogs, so row margins10,
two incidences per fibre per column, and within-fibre Grams hold identically.
For the n20 positive fixture, replace60 by180 and margins10 by18.

Objective TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1 is
E=sum_{0<=g<h<=2} sum_{i,j=0}^{n-1}(F_g F_h^T-G_gh)[i,j]^2.
G[i,j]=n delta_ij+2-C[i,j]-(C^2)[i,j]-[same fibre].
E is a nonnegative integer to minimize, covering exactly three144-entry blocks
for the two research cores. E0 is only an abstract full Gram factor. Neither
mixed caps nor Y-column caps nor residual D are encoded in this objective.
All E0 raw objects require separate checks; no floating score is a certificate.

## Delta, moves, acceptance, and state

A proposal chooses g in{1,2} and two distinct column positions a,b. Only rows
incident to exactly one of those two supports change, by toggling bits a,b.
For each such row and every row in either other fibre, GPU popcounts recompute
the old and new overlap. The delta is the sum of new squared errors minus old
squared errors. No affected cross-entry is double counted: exactly one endpoint
is in g. Score and delta arithmetic use signed32 integers; at n<=20, each cross
count is <=18, target in[-3,20], and at most1200 terms, safely below2^31.
Row masks have three64-bit words, including positive-fixture positions>=128.

The CPU path rebuilds the full candidate masks and recomputes every cross-entry
for each proposal; it does not call the GPU delta. Both paths share xorshift64*,
proposal generation and acceptance helper code, disclosed calibration trust.
RNG state0 is refused. Four RNG draws per proposal select fibre, a, b and u.
The double denominator literal9007199254740993.0 rounds to2^53, so the actual
acceptance variate is u=((draw>>11)+1)/2^53 in(0,1].
Modulo reduction has small sampling bias; no claim of exact uniform sampling.
Mode0 accepts all moves. Mode1 accepts nonpositive deltas or, at positive fixed
temperature, compares u with exp(-delta/T). Double exp/acceptance is heuristic;
CPU/GPU agreement on sampled moves is not a universal floating-point guarantee.
No --use_fast_math; --fmad=false; native architecture defaults sm_89.

## Preregistered calibration

Locked Python runs the existing nvcc/Visual Studio environment convention,
recording exact build command/log/source/binary hashes, nvcc and GPU versions.
Two deterministic shuffled chains per target core and one known E0 SRG243 chain
each receive64 forced moves,64 T0 moves and64 T3.25 moves:960 proposals total.
Two additional known-positive-fixture moves explicitly swap63/64 and127/128,
giving962 checked proposals and covering both internal mask-word boundaries.
Every GPU trace delta and state is checked by full Python set intersections;
the complete CPU and GPU traces/state must agree. Each fixture's T3.25 run is
also split23+41 with state save/reload and must exactly match its64-step run.
Malformed actual-native inputs: RNG0, duplicate permutation, duplicate catalog,
asymmetric target and trailing data; a corrupted saved delta must be rejected.
The known-valid positive is SRG243 E0 only. Random research-domain states are
valid permutation states, not known valid full Gram factors.

## Future bounded execution and replay

Use the unchanged uv.lock and environment:

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_factor_permutation_annealer.py calibrate --out acceleration/results/20260930_factor_permutation_annealer_calibration
```

Run mode requires an independently produced gate with status
INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS and exact normalized
inputs_sha256 entries for wrapper, native source, build script, spec and binary.
No initial campaign will be run by the producer. Native caps are256 chains and
1024 proposals/chain/call. Wrapper run mode requires explicit gate path/hash;
it supports --core,--seed,--chains,--chunks,--steps,--seconds,--temperature,
and --resume a prior complete checkpoint. Time is checked between chunks; each
call has at most60 seconds timeout. It records every chunk input/output/receipt,
complete current/best permutations, RNG/proposal state and raw best matrix.
Calibration also exports every raw initial, final and best factor object.
Resume authenticates exact domain/objective/source/binary and chain count.
Changing the temperature on resume is an explicit configuration change saved in
the new manifest. tqdm and per-chunk objective heartbeats provide progress.
Best raw JSON schema is {core_adjacency,factor,claimed_score}; status CANDIDATE.
Fresh paths only; no overwriting frozen artifacts. Calibration is replayed into
a new output and requires a new binary path/build variant if already compiled.
No timing samples here establish a performance improvement claim.
