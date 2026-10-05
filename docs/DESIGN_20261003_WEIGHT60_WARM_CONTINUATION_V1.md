# Candidate warm continuation design, version 1

This document authorizes no execution. It recommends one next experiment using
the unchanged weight60 V2 exclusive-swap engine, after a new graph-reset driver
and its independent controls are published. A larger move kernel is a separate
alternative requiring new native source and gates.

## Evidence and question

The single 100,000,000-proposal pilot at seed 99032060 ended with a checked
99-vertex, 14-regular point-line graph. Every adjacent pair has one common
neighbor, but its nonadjacent-pair squared residual is 3608 and its exact target
matrix identity fails at 4934 ordered entries. The initial and final objectives
are different components: ordinary residual changed from 3486 to 3608, whereas
the weight60 objective changed from 7203 to 3608. Therefore this is an improvement
in that weighted objective, not a lower ordinary residual than the initial graph.

The independent saved-object report is
`acceleration/results/20261003_independent_review/weight60_pilot01/summary.json`
(SHA256 `a80ec86298ce13ae8fea44c118ebbe613dd4b55e4387ac49e39ec9b3d4cd40d2`).
The final labelled hypergraph state is
`acceleration/results/20261002_hypergraph_weight60_pilot01/native/final.state`
(SHA256 `0dc37fdc2dd58fb78f55b88fd8e2ee7c43a83d32d1cc7897591151d5aca6a1bb`),
and its current/best adjacency matrix has SHA256
`818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836`.

The checked 80-million and 100-million snapshots both record 74283 accepted
moves, 162 best updates, and current/best component scores `(lambda, mu)=(0,3608)`.
Those endpoint counters agree; a full transition history for the intervening
sparse trace is unavailable. This is a reason to test a fresh annealing schedule,
not a proof that all other moves or temperatures are ineffective.

The independent dense root census
`acceleration/results/20261003_independent_review/weight60_roots_dense01/summary.json`
(SHA256 `99a319ea75ca2984e3b5e85dcf42dff7e066cf8fef4d9e510d47479addf06a2f`)
checked all 99 roots in each of two saved lambda-zero graphs. Neither has a root
whose 84 outside vertices all have exactly two neighbors in the root neighborhood.
The final graph's smallest root-row residual is 50 at vertex 81. These raw graphs
cannot directly instantiate an exact root-scaffold search without modifying its
scope or completing the required root conditions.

Question: does a fresh, moderately warm schedule from the checked lambda-zero
graph lower the nonadjacent residual while retaining or recovering lambda zero?

## Recommended frozen experiment

Start from exactly the labelled 231 triples of the final graph, not a relabelled
matrix reconstruction. Set both current and best to that selected graph and
recompute every pair multiplicity, CN cache and exact integer score. Retain the
V2 objective weight60 and the exclusive two-line swap kernel. Initialize a new
RNG at seed **99032061**, reset proposal/admissible/accepted/update counters to
zero, use no mixing phase, and cool from **8 to 0.1 over 80,000,000 proposals**.
The proposed first comparison is 80 million proposals; a later 100-million case
would require its own declaration, rather than extending this invocation.

This is a fresh warm-start experiment, not exact continuation of the old RNG
trajectory. Passing new seed or schedule options alongside `--resume` of the old
state would violate the existing exact resume configuration. Prepare a new
versioned graph-reset driver that emits a canonical V2 state with independently
checked new configuration/RNG, zero counters, equal current/best triples and
caches, and the initial lambda-zero snapshot at new step zero. Preserve the old
first-snapshot step 29380701 separately as source provenance; it is not the first
step of the new run. Record raw source/selection hashes and the new state's hash.

Before science, require independent graph-reset controls: target-size and generic
fixtures; both source current/best selectors; exact new RNG initialization;
lambda-zero step-zero snapshot; a lambda-positive source that has no premature
snapshot; changed configuration/cache/score/triple/RNG rejection; and native
whole/split resume byte equality from the newly reset state. A discovery wrapper
cannot approve its own reset, and unchanged engine controls alone do not approve
the new driver.

Publish the new driver, protocol, controls and checking gate before fresh Linux
process/resource and exact Git/source preflight. A suggested independent command
allowance is 600 outer / 550 worker / 450 native / 445 internal seconds, with
orderly checkpointing. The prior 100-million native run took 239.705912105 seconds
on this host/configuration; that single observation motivates the allowance and
does not establish general speed or a future runtime guarantee. This design
does not prepare or launch a command vector.

## Acceptance and falsification

The fixed scientific input population is one selected labelled graph, one RNG
seed and one schedule. Record all attempted/completed proposals, errors and
timeouts without treating retries as distinct cases. Preserve periodic states,
current/best/first-lambda-zero raw matrices and sparse trace anchors.

An improvement of practical interest requires an independently checked saved
graph with `E_lambda=0` and `E_mu<3608`, using exactly the existing squared pair
residual definitions. A lower weighted score with positive lambda residual is
a separate heuristic observation, not that success. Exact matrix identity zero
must trigger the full independent SRG(99,14,1,2) validators and artifact release.
No numerical score or self-checked cache is a graph certificate.

Failure to improve within the allocation does not exclude graphs or kernels.
The whole trajectory and earliest lambda-zero event remain unknown across any
unobserved sparse intervals. No unrestricted search coverage denominator exists.

## Alternative: new three-line cyclic trade kernel V3

Choose three distinct triples and one point from each that is exclusive to its
own selected triple among those three triples. Move the selected points in a
directed three-cycle between the triples. Keep the other two points of each
triple fixed. This preserves all point degrees, and contains exchanges of three
line incidences that are not single two-line swaps. It may leave the same
connected components or offer no improvement; neither connectivity nor greater
reachability is established.

A legal implementation must test distinct/new line contents, remove the six
old affected pairs before testing the six new pairs, account for cancelled pair
updates when fixed points overlap, and reject any post-trade pair multiplicity.
Exact rollback must restore line labels, pair/adjacency/CN caches, component
scores and RNG counters. A new native kernel/state/trace marker, specified random
proposal distribution and versioned independent finite gates are necessary.
Controls should exercise both cyclic directions, shared fixed points,
collision rejection, cancelled toggles, sign/category changes, accepted/rejected
full scalar scoring, and first-lambda-zero snapshots distinct from best score.

The warm V2 experiment is recommended first because it tests reheating of an
independently checked lambda-zero object with a small new reset interface. The
V3 kernel is the next distinct heuristic attack if those records reveal continued
stagnation, subject to separate engineering and scientific authorization.
