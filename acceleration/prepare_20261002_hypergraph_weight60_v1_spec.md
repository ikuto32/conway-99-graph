# Fixed-weight60 engine v1 engineering protocol

Producer /root/native_driver; a new independently checked gate is required.
This source copies disclosed weight6 v1 implementation mechanics, with changed
fixed weight, objective/state/trace schemas, weight6 import and persistent first
lambda0 selection. The old sources, controls and gates remain immutable. A gate
for their bytes does not approve this changed engine. The design is pinned
design_20261002_hypergraph_weight60_v2.md SHA
4e15c3e8755348b580196651379a435311adbfd6c13fd2e452903a1994b01fcd.

Objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2 is the exact integer
F60=60*E_lambda+E_mu, with E_lambda=sum_adj(CN-1)^2 and
E_mu=sum_nonadj(CN-2)^2. Ordinary E=E_lambda+E_mu is recorded separately.
Feasible target domain remains99 points,231 labelled linear triples and point
degree7; the point graph is simple14-regular. Rook9 degree2/6triples is a generic
positive control, never a99certificate. The source initialization/trade proposal
and xoshiro256**/SplitMix64 RNG algorithms are copied from the disclosed weight6
v1 source. No symmetry, fixed support, move-space connectivity or coverage claim.

The new HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V1 preserves the weight6 field ordering
through current/best/CN, but requires objectiveV2 and fixed weight60. Before END
it adds first_lambda00|1; if1, first_step,first_admissible,first_accepted,
first_best_updates,first_rng4words,first_current count and triples,first_best
count and triples. Graphs are fully recomputed, snapshot current E_lambda must
be0, snapshot best F60 must not exceed snapshot current F60, RNG nonzero and
counters consistent and no later than the current counters. A currently lambda0
graph requires a selected snapshot. A checkpoint alone does not prove absence
of an earlier lambda0 graph; full finite trace replay establishes selection only
for the calibrated finite populations. Sparse scientific traces cannot establish
unobserved trajectory properties.

The immutable selection rule is first observed current graph with exact lambda
energy0, including the invocation's initial graph and every completed proposal,
regardless of whether it improves best F60. Snapshot includes complete current,
best,RNG,counters and config, making first_lambda0.state exactly resumable.
First capture after proposal i has completed step i+1. It is preserved verbatim
across exact weight60 resumes. Native exports first_lambda0.state and
first_lambda0.adj whenever found, plus lambda0_selection.json always. Its first
step is null when absent. carried_from_resume describes an existing snapshot,
not a new discovery. Exact split states, first objects and traces are checked.

Move records add trace_schema HYPERGRAPH_WEIGHT60_MOVE_V1 and objectiveV2,
lambda_weight60,first_lambda0_before/after/step. Remaining fields match the old
weighted record. Integer CN updates use current categories; an edge toggle
replaces its old category contribution by the new one with coefficient60 on
lambda change. Rejected trades reverse all8edge toggles and require exact
rollback of F60/lambda/mu. Each engineering proposal gets full producer graph,
score/cache/domain reconstruction; independent replay is a separate path.
Pair-cost table retains86exact CN/category cases, but F delta uses weight60.

--import-weight6 validates the complete old HYPERGRAPH_WEIGHTED_ANNEAL_STATE_V1
record and objectiveV1/weight6, recomputes F6=6lambda+mu and every component,
cache,domain,RNG/counter condition, selects current|best, then creates a new
weight60 state with recomputed F60,current=best,new CLI seed/config and all
counters0. It never resumes a weight6 trajectory. --resume preserves exact new
config/RNG/counters and persistent selection; CLI schedule values are ignored.
Both are mutually exclusive. Wrapper pins exact import raw identity.

Frozen52native engineering calls:25successful and27expected exit2. Successful
proposal attempts total20,480, including overlapping whole/split control paths;
this is not unique graphs.320scheduled64-step checkpoints are expected without
timer extras; count actual saved objects separately.86pair-cost records per
successful call,2,150total, are algebraic test cases, not asserted graph cases.

The original16successful population is reused as explicit changed-engine calls:
rook9 positive0; rook9 forced2048; target99 forced/greedy/anneal/cooling/warming/
mixed2048 each;256 versus73+183 fresh split;2048each imported current/best;
256versus73+183 imported split. Fresh calls retain old seed99032020/T0forced,
T0greedy,T16anneal,T48to.2cooling,.2to48warming,T24mix256; schedule1024.
Fresh split seed99032021,T16,mix64. Imports use the independently checked old
weight6 warming final state SHAfa54362fc5822d36e7107cbab35398a2e223cdc378593598153205bb77595cf2:
current F6=8877/E5482/lambda679/mu4803 and best F6=8815/E5590/lambda645/mu4945,
so current/best source graphs differ. New import seed99032060,T60to.1,mix0,
schedule1024. Imported split runtime CLI values are ignored in favor of the
saved initial config, and raw whole versus split states/traces must coincide.

Additional5calls: rook9 whole256/first73/second183 at seed99032060,T60,mix0,
checking first-lambda0 state/matrix retention and exact split trace; zero-step
weight6 rook9 import best; zero-step independently checked pilot02 best import,
new seed99032060,T60to.1,mix0. Pilot source f4df0eadf3e7c4199c0715ed6c647ea995e41ffe8f972f91889b3a62a10879ad
is bound by saved-object report6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0;
expected imported lambda63/mu3423/E3486/F60=7203. No scientific proposals here.

Additional4calls calibrate capture after a proposal: prism9 initial0 and a
256versus73+183 greedy split,seed99032060/T0/mix0/schedule1024. Its six triples
are {0,2,6},{0,1,7},{1,2,8},{3,5,6},{3,4,7},{4,5,8}, representing vertex stars
of a triangular prism with9edge-points. It is a distinct linear degree2 fixture
with E_lambda>0 initially. The frozen finite greedy sequence must first reach
lambda0 at a positive completed step, export that exact snapshot and preserve
its bytes across split resumes. If it fails to reach lambda0 this finite
selection control fails; do not retrospectively change seed/counts or thresholds.
These small9vertex fixtures are outside the target99 domain.

Negative12resumes: wrong weight,Fcurrent,Fbest,lambda,mu,base,CN,duplicate
current triple,zero RNG,counter,objective,version. Negative9weight6imports:
F6,CN,triple,counter,RNG,objective,weight,lambda,base. Wrong selector1. Negative
first-selection5:flag2,zero snapshot RNG,first_step later than current,duplicate
snapshot triple,missing snapshot on a current lambda0 fixture. Source contains
the exact expected diagnostic map: require matching complete stderr plus newline,
empty stdout,no scientific artifacts and exit2. Unrelated exceptions do not pass.
Independent checker must additionally falsify wrong import selection, retained
old counters, input hash,wrong weights/components/category costs/trace selection.

New independent gate INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V1_CONTROLS_PASS
must bind all changed CODE, binary/build and raw receipts, rederive integer
category costs, all20,480proposals,RNG/schedule/acceptance,all saved objects/raw
matrices/import reset and4whole/split traces. Temperature tolerance1e-12 and
acceptance minimum margin1e-12; ambiguous finite decisions veto approval. All
lambda0 and F60zero controls need independently multiplied exact identity, and
rook9 must fail a99scope assertion. Scientific admission additionally requires
INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V1_CALIBRATION_PASS for the changed
state/selection/matrix checker, fresh committed source/resource preflight and
root authorization. This engineer cannot approve its own production output.

Build allocation180outer150worker120declared native field, chosen from prior
weight6 build1.6seconds; compiler child shares150worker and outer group deadline.
Controls300outer270worker30native per-call,2GiBAS/1GiBperfile, from old producer
32calls approximately8seconds and complete independent replay110.86seconds.
These52tiny native calls with full producer checks get generous shared270seconds
including receipts/hashes and20second worker reserve; no retries/extensions.
Separate commands have independent allowances; prior GF3 duration is not deducted.
This is engineering computation only. No weight60 science authorized here.

Supervisor+GNU hard group guard run inside Ubuntu-24.04 as default UID1000,
/usr/bin/python3; locked offline native_budget_env_v1 uv project and repo cache.
Compiler pinned /usr/bin/g++13.3 SHA1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769.
Raw exact commands/source commit/input/output SHA/tool versions/resources/outcomes
are recorded. A failed call preserves all preceding artifacts and gets a new
version if corrected. Timeout is incomplete engineering, not an exclusion.
