# Ternary mixed native engine V1

SOURCE ONLY. No compile, syntax/import execution, finite native control or
scientific invocation occurred before this source/spec freeze. A new applicable
independent control gate is required; no historical F60 binary approval transfers.

The target domain consists of99 labelled points,231 ordered triples, point
degree7 and pairwise linearity. The induced simple point graph has degree14.
Generic finite domains are rook9/prism9 with six triples and cube12 with eight
triples, point degree2. The explicit cyclic target initializer is only an
unoptimized engineering fixture. Neither its symmetry nor any frozen support,
root, lambda-zero restriction or nontrivial automorphism is required of search
states. No move-space connectedness or unrestricted exhaustive coverage claim.

Exact objective version SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1 has unordered
residual r=CN+A-2, residue in{0,1,2}, F3=count(nonzero residue),
E_lambda=sum adjacent r², E_mu=sum nonadjacent r², E=E_lambda+E_mu.
Saved residue_population counts all unordered pairs. Best retention uses exact
lexicographic(F3,E). The acceptance scalar is819820F3+E for99points;
generic scalar weight is choose(n,2)*(2*point_degree)²+1. All arithmetic for
graph scores and deltas is signed64bit integer; graph bounds make overflow
impossible after typed parser validation. The scalar changes objective ordering
relative to F60 and cannot be compared directly with old F60 values. Exact E
remains the same diagnostic on the same complete graph domain.

RNG distribution ALL_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1 uses
SplitMix64 seed expansion and xoshiro256** uint64 transitions. For bound b,
consume words until x>=(-b modulo2^64) modulo b, then return x modulo b.
Draw ti uniform in m, j uniform in m-1 and map j>=ti to j+1; draw pi,pj
uniform in3. Thus every ordered distinct-line/selected-position tuple is
equally weighted by the protocol, with variable rejection-word count recorded.
This is a new distribution identity even though transition/expansion code was
adapted from the preserved weight60 V2 source. Every valid proposal consumes one
additional acceptance word, including forced/mixing/descending/zero-temperature
branches. Invalid proposals consume only proposal words. Counters count attempted
proposals, admissible proposals, accepted proposals and strict best updates.

Move kernel ALL_LINE_EXCLUSIVE_SWAP_TERNARY_V1 selects exclusive x from first
line and exclusive y from second; shared-one-point lines are allowed. Four old
pairs are removed simultaneously for final-occupancy testing. All four new pairs
must be absent after removal. Valid moves sequentially remove four edges, add
four, replace the two literal selected positions, and preserve degree/linearity.
Rejected moves reverse the eight edge toggles and preserve exact caches/scores.
Incremental CN updates affect pairs meeting toggled endpoints and separately
account for the toggled pair's adjacency-category change. Full reconstruction
checks adjacency/masks/all unordered CN entries/F3/components/histogram.
For99points the separately derived necessary inequalities F3<=E<=28F3 and
q1-q2 divisible by3 are additional cache falsifiers, not cache certificates.

Mixing accepts all valid proposals for global steps below mix_steps. Otherwise
forced finite controls accept all valid moves; scalar delta<=0 is accepted;
positive delta at positive temperature is accepted iff
u=(acceptance_word>>11)*2^-53 < exp(-delta_scalar/T). Linear cooling uses
min(1,max(step-mix_steps,0)/schedule_steps). Floating temperature/exp/random
comparisons guide search only. Finite acceptance margins must be independently
checked; no scientific temperature/restart/allocation is frozen by this spec.
The old F60 scale cannot be reused: one F3 uphill increment costs about819820
scalar units. This scale must be informed by the complete new local census.

Graph-only input is ASCII token stream TERNARY_LINEAR_GRAPH_INPUT_V1 with keyed
n,degree,source_graph_sha256,triples followed by exactly n*degree/3 ordered
triples and END. Native checks source identity against the explicit CLI; it
does not implement SHA256 or establish source provenance itself. The future
gated wrapper/input adapter must independently bind actual raw matrix/triples
and hash before use. Import resets RNG from the new seed, all counters to0,
best=current, and captures any initial zero. It reads no old native RNG/history.

State magic HYPERGRAPH_TERNARY_MIXED_STATE_V1 is followed, in literal order, by
objective/move_kernel/distribution/source_graph_sha256/n/degree/scalar_weight;
seed/mix_steps/schedule_steps/t_start/t_end/forced;
step/admissible/accepted/best_updates/rng_words/rng(4uint64 words);
current_metrics and best_metrics each(F3,El,Em,q0,q1,q2,scalar);
current and best keyed populations with ordered triples;
cn keyed choose(n,2) followed by u<v row-major CN values;
zero_archive count followed by every zero_step/zero_admissible/zero_accepted/
zero_updates/zero_rng_words/zero_rng/zero_triples; END.
Unsigned decimal tokens are canonical digits, no bool/float/negative/overflow
aliases. Real temperatures must parse wholly and finitely. Domain, metrics,
cache, counters, nonzero RNG and strict source/config identities are checked.
Resume preserves exact RNG/config/counters/current/best/archive and requires
the original graph identity via CLI. All source/config fields must agree;
invocation trace/checkpoint intervals may differ without changing trajectory.
Step-zero state additionally requires seeded RNG, zero counters and literal
current=best. Object validation is not proof of the unrecorded prior trajectory.

Every distinct retained current F3zero matrix is archived with literal triples,
step/counters/RNG. Matrix bytes define distinctness; labelled triple order is
preserved, with no isomorphism collapse. The first archive entry is the first
retained zero in that actual native invocation/history, including initial;
sparse scientific traces cannot independently prove an unobserved earliest
trajectory event. Current/best zero objects must be present in the saved archive.
Generic zeros are not99certificates. A99zero automatically stops at the next
loop guard, exports raw matrix/triples and exact capture state immediately,
and remains pending a separate full99integer SRG validator. No numerical zero
or native self-check promotes a target result. All exported statuses set
target_resolution:false and independent_approval:false.

Native outputs: initial.state; periodic checkpoint_<globalstep>.state;
zero_capture_<step>.state; final.state; current.adj/best.adj (order then literal
binary rows); moves.jsonl; result.json; zero_selection.json;
zero_objects/object_<index>.adj and .triples. Existing files are never overwritten.
Trace selection is globalstep<trace_prefix or globalstep divisible by trace_stride.
Complete finite traces contain every proposed tuple, old/new triples, all
validity flags, before/candidate/after/best metrics, delta scalar, floating T,
acceptance draw and exact pre/post RNG/word counters. Invalid candidate metrics
equal before; proposed triples are literal proposal data, not valid graph claims.
Probe mode allows only step-zero generic n<=12 and enumerates every i<j/pi/pj
tuple without RNG or retained state changes, full-rescores every admissible
candidate and rollback, and emits probes.jsonl. It is outside science mode.
Pair-cost table has596 records:396 bounded CN±1 cases and200 category toggles,
with signed integer residual and exact modulo normalization, c=0..99/a=0,1.
These arithmetic cases include values outside feasible generic graph counts.

SIGTERM/SIGINT set a cooperative stop flag; native timer checks every256 attempted
proposals. Initialization/probes/full verifies/exporting belong to the enclosing
command deadline. The outer supported Linux supervisor controls the entire
group, while the wrapper reserves shutdown/save time. Actual termination/empty
group observations are recorded, never an absolute unobserved guarantee.
Files/receipts from all failures are preserved. No retry or historical cap wrapper.

Shared producer components: SplitMix/xoshiro and CN edge-toggle strategy adapted
from acceleration/hypergraph_weight60_anneal_20261002_v2.cpp, unchanged historical
source pinned separately. New F3/category/hist/scalar/typed-state/probe/import/
zero/archive/trace implementation is unapproved. Independent verifier must use
raw triples, separate adjacency/CN/F3/E math, exact RNG/proposal reconstruction,
complete finite trajectories/rollbacks, strict corruption controls and positive
rook9 versus full99scope veto. Agreement between producer paths is not a gate.
