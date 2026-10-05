# Candidate fixed-weight60 construction experiment

Design by root, 2026-10-02 UTC. Status CANDIDATE; no changed-engine or scientific
launch is approved by this file. Preserve the weight6 engine and all old states,
sources, controls and failed versions. The immediate next science remains GF3.

The independently checked weight6 pilot02 best graph has adjacent residual63
and nonadjacent residual3423, ordinary residual3486. It improved its own fixed
weighted objective but worsened ordinary residual3034 from the earlier pilot.
The exact best matrix is
`acceleration/results/20261002_hypergraph_weighted_pilot02/native/best.adj`, SHA
`5f21ae090fdae2fad1ca27730b6d74e86b820866039317cc89c59ad1d9641066`;
the final weighted state is SHA
`f4df0eadf3e7c4199c0715ed6c647ea995e41ffe8f972f91889b3a62a10879ad`.
Its complete saved-object audit is SHA
`6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0`.

Question: can stronger fixed emphasis on lambda1 produce a complete14-regular
99-point linear-triple graph with every adjacent pair having exactly one common
neighbor, and then reduce its nonadjacent residual? A lambda1 partial graph is
not a target graph; every nonadjacent pair still requires exactly2 common
neighbors and complete independent matrix validation.

New objective `SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2` is
`F60 = 60*E_lambda + E_mu`, minimized on the same99-point231-linear-triple,
point-degree7 domain. The imported graph has F60=7203=60*63+3423. Weight60 is a
declared heuristic tenfold increase from weight6, chosen after the recorded
pilot ended with lambda residual63. No controlled performance advantage or
success probability is claimed. Preserve F60, E_lambda, E_mu and ordinaryE
separately; F60 cannot be compared numerically to F6 or ordinaryE as improvement.

Each edge already lies in exactly one source triple. Thus lambda1 is equivalent
to having no triangles beyond the231source triples. For any14-regular lambda1
graph, nonadjacent common-neighbor counts have mean2. These are mathematical
criteria awaiting the separately requested independent general derivation and
raw triangle audit; no numerical threshold, mean or clean root proves mu2.
The existing graph has recorded adjacent histogram630 at1 and63 at2; its
extra-triangle/clean-root populations must be independently computed before
using them. A clean root alone does not imply the full fixed189-edge SAT scaffold:
its84nonneighbors must also have exactly2neighbors in its14-neighborhood.

Implementation must be new versioned C++/wrapper/spec/state/binary. Use explicit
weight60/objective/state markers; exact component arithmetic, category-switch
updates, rollback and CN cache validation remain required. Import the pinned
weight6 state only by a distinct new-state conversion checking old weight6
scores, selected best/current triples and source hash. Set a NEW seed/schedule,
reset all counters/RNG and record conversion bytes. Do not pretend to resume
the weight6 trajectory or reuse its execution approval.

Before science, new independent controls must check full proposal sequences,
all raw matrices/component scores, weighted category changes, rejected-trade
rollback, RNG/acceptance decisions, exact split resumes and imports. Deliberately
wrong objective/weight/component/cache/counter/input-hash and retained-old-counter
controls must fail at their precise stages. Known rook9 zero and a corrupted
fixture calibrate full checking but cannot be accepted as99 target certificates.
Source/binary/gate commits, exact commands and locked runtime are required.

A prospective single scientific selection is the pinned weight6 best graph,
NEW seed99032060, no forced random mixing, temperature60 to0.1 with an80million
proposal schedule and at most100million proposals. Freeze the exact count and
budget only after changed-engine control timings. Prior20million native proposals
took41.919seconds, but that single measurement is not a performance guarantee.
A proposed outer600/worker550/native450-second allocation gives ample margin
for preprocessing, checkpointing, hashing and shutdown under the per-command
policy; reassess if new control data contradict it. Never extend the invocation
with internal retries or silently change objective/thresholds.

Success output is complete current/best raw matrices and resumable states with
component histories and fixed selection records. Save the first lambda0 state,
if one appears, under an explicit immutable artifact rule and independently
check it. Target success requires full A^2=12I-A+2J over integers; F60=0 must
still be independently validated from raw99x99matrix. Every nonzero result or
timeout provides no exclusion, coverage fraction, ergodicity or impracticality
claim. Stop/checkpoint at the actual command deadline and list unmet criteria.
