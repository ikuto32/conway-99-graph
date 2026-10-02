# Fixed-weight60 engine v2: exclusive-selected-point swap controls

Producer /root/native_driver. No independent approval by this author. Root
explicitly authorized this new engineering extension after controls01 failed.
Preserve all v1 source/spec/plan/build/25successful control attempts and failure;
27negative calls were never attempted. New source/code/build/checker gate needed.
Design remains design_20261002_hypergraph_weight60_v2.md SHA
4e15c3e8755348b580196651379a435311adbfd6c13fd2e452903a1994b01fcd.

Objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2 is exact F60=60E_lambda+E_mu,
E_lambda=sum_adj(CN-1)^2,E_mu=sum_nonadj(CN-2)^2 and ordinaryE their sum.
Target domain unchanged:99points,231linear labelled triples,eachpointdegree7,
simple14regular point graph. Generic controls9/12points degree2 have4regular
point graphs; no generic zero/lambda0 is a99certificate. Weight6,weight60 and
ordinary scores are different objectives and cannot be directly compared.

NEW move kernel LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2: choose two DISTINCT triples
using the unchanged4 xoshiro256** draws (ti modm,tj mod(m-1) skipti,pi mod3,pj
mod3). Do not resample. Triples may shareonepoint because source domain islinear.
Selectedx must not belong to the other triple; selectedy must not belong to the
first. Swap them iff allfour incoming pairs are absent after removing thefour
outgoing pairs. This is a larger move domain than old disjoint-only v1; no claim
about target ergodicity, connectivity or exhaustive coverage follows.

For an overlapping pair, two incoming edges equal outgoing edges through the
sharedpoint. Existing ordered8toggles remove4 then add4, so cancellation occurs
exactly through a valid intermediate graph. CN changes and weighted category
switches use actual current adjacency at each toggle. Reject by reversing all8
in reverseorder and verify exact F60/component rollback. Independent checker
must construct proposed labelled triples and their complete adjacency directly,
check degree/linearity and derive all integer deltas independently; do not just
trust the producer's intermediate edges. Every engineering proposal gets full
producer domain/CN/score reconstruction. Independent complete replay is separate.

New HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2 tag requires objectiveV2,lambda_weight60,
move_kernel LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2 before n/degree. All other v1 field
orderings are preserved: seed/mix/schedule/temperatures/forced,step/admissible/
accepted/best_updates,weighted/base/lambda/mu current+best scores,RNG4words,
current count+triples,best count+triples,upperpair CN cache,first_lambda0 flag,
optional complete first snapshot,END. Old weight60v1 checkpoints cannot resume.
Exact field-name lines and ordered triples are emitted by source. New target
or generic9/12degree2 domain only. Old weight6 graph import accepts only the
actual old domain9/99 and objectiveV1/fixed6, validates entire old record including
F6=6lambda+mu/components/CN/domain/RNG/counters then resets all counters/current=
best/newseed/config/RNG and recomputes F60. It is not an old trajectory resume.

First snapshot fields: first_step,first_admissible,first_accepted,
first_best_updates,first_rng4words,first_current count+triples,first_best
count+triples. Its current must have exact E_lambda0; its bestF60 must not exceed
currentF60; RNG nonzero; counters ordered and no later than current counters.
Currentlylambda0 requires selected snapshot. The first observed CURRENT graph
with E_lambda0 (including initial and each completed proposal) is retained
regardless of whether it improves bestF60. After proposal i it has step i+1.
Snapshot preserves rawcurrent/best/config/RNG/counters exactly and is exported
as immutable first_lambda0.state and first_lambda0.adj whenever found; selection
JSON always records found/firststep/null/carried_from_resume. Full finite replay
establishes earliest selection only on these finite paths. Sparse scientific
traces cannot prove selection facts in unobserved intervals.

New trace_schema HYPERGRAPH_WEIGHT60_MOVE_V2 and move_kernel are explicit.
Keep disjoint as a diagnostic and new_pairs_absent as literal absence before
removal; add selected_points_exclusive and new_pairs_absent_after_old_removal.
Admissibility now means exclusive AND after-removal absence, not disjoint.
Record old/proposed triples,selected indices,acceptance/mixing/temperature,
F60before/after/delta,lambda/mu before/after,bestF60,firstfound before/after/step,
decimal RNG before/after/draw. Accepted-or-rolled-back afterstate is exact.
Pair-cost tables contain86integer CN/category cases using fixed60; they are
algebraic controls, not claims every pair-case is realizable in target domain.

Freeze57native calls:29successful,28designatedexit2. Successful proposal
attempts20,992 include repeated whole/split engineering paths, not distinct
candidate graphs.328scheduled64-step checkpoints without timer extras; count
actual saved files separately.86pair-cost records per successful call/2,494total.

Original16successful calls repeated against NEW kernel/source: rook9positive0,
rook9forced2048,target99forced/greedy/anneal/cooling/warming/mixed2048each,
256versus73+183freshsplit,2048each weight6importcurrent/best,256versus73+183
importedsplit. Fresh seed99032020,T0forced,T0greedy,T16anneal,T48to.2cooling,
.2to48warming,T24/mix256; schedule1024. Freshsplit seed99032021,T16,mix64.
Imports use old warming finalstate fa54362fc5822d36e7107cbab35398a2e223cdc378593598153205bb77595cf2,
currentF6=8877/E5482/lambda679/mu4803 and bestF6=8815/E5590/lambda645/mu4945,
so both selections differ. Newseed99032060,T60to.1,mix0,schedule1024; imported
split ignores runtime config and preserves this saved config. Exact finalbytes
and whole trace=first+second required.

Additional5calls: rook9whole256/first73/second183 seed99032060,T60,mix0;
zero-step oldweight6rook9 best import;zero-step independently checked pilot02
best import f4df0eadf3e7c4199c0715ed6c647ea995e41ffe8f972f91889b3a62a10879ad
bound by report6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0.
Expected pilot imported lambda63/mu3423/E3486/F60=7203; newseed/config/reset.

Prism9four calls:initial0 then256versus73+183greedy,seed181,T0,mix0,
schedule1024. Triples {0,2,6},{0,1,7},{1,2,8},{3,5,6},{3,4,7},{4,5,8};initial
lambda6/mu6/F60366. Firstfourdraws select ti0,tj3,pi0,pj0. These lines share6;
selected0/3 are exclusive. Known accepted overlaptrade gives lambda0/mu0,
firstcapturestep1. Whole/split final/firststate/firstmatrix/trace identity required.
The failedv1 prism expectation remains preserved; extension changes the allowed
kernel rather than retroactively changing its seed or threshold.

Cube12four calls:initial0 then256versus73+183greedy,seed149,T0/mix0/schedule1024.
Triples {1,2,7},{0,3,4},{1,5,6},{3,5,7},{2,8,9},{4,8,10},{6,9,11},{0,10,11}.
Initiallambda6/mu62/F60422. Known first proposal ti0,tj7,pi2,pj0 is disjoint and
gives lambda0/mu48/F6048, a useful partial-lambda0 fixture that is not SRG.
Require firstcapturestep1 and exact whole/split final/firststate/matrix/traces.
These seeds were preregistered by lowest seed0..9999 proposing the known exact
trade on first4draws, recorded in diagnosis03; no heuristic science selection.

Strict28negatives:13new-resume mutations(weight,currentF,bestF,lambda,mu,base,
CN,duplicate triple,zeroRNG,counter,objective,oldversion,wrongmovekernel);
9weight6import mutations(F6,CN,triple,counter,RNG,objective,weight,lambda,base);
wrongimportselector1;first-selection5(flag2,zeroRNG,latercounter,duplicatetriple,
missing snapshot on currentlylambda0rook9). Source's exact diagnostic map is
required: matching complete stderr+newline,emptystdout,no artifacts,exit2.
Unrelated errors cannot satisfy a negative. Independently falsify retainedold
counters,wronginputhash,wronggraphselector,unweightedcategorycost,ignored-overlap
cancellations,wrong exclusive predicate,wrong firstcapture and99scope controls.

Historical diagnosis sources preserved: v1 incomplete360nonnop dual records
omitted u=v selfmaps;v2 added allswaps but emitted wrongcube inverse tuple because
it reused prism variables in report;v3 corrects that tuple. V3 report d292c6ab61f3a7d61276b0d335035a681e4e4e371d260b725d1c6c959ffefeaf
records70cubic6graphs/all5005subsets,all exclusive swaps with labeled oldkernel
subpopulation and exactfixture/RNG rawdata. Its copied scope prose mentions
only disjoint trades although tables explicitly contain both kernels. No own
independent mathematical approval; independent gate must reconstruct actual
frozen population and audit corrections/limitations rather than trust prose.

Fresh independent gate INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS
must bind changed CODE,binary/build/receipts,all20,992proposals,all rawstates/CN/
matrices/imports,5whole/splits,2,494cost records and exact negative stages. It
must derive degree/linearity preservation for new overlap predicate and explicitly
check accepted/rejected overlapping proposals with cancelling edges. Additional
savedchecker gate INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_CALIBRATION_PASS
plus fresh committedsource/resources and root authorization are required before
science. Acceptance margins >1e-12,temperature tolerance1e-12; exactinteger scores.
TargetF60zero still needs complete independent99integer SRG multiplication.

Build180outer150worker(nativefield120explicit),from v1compiler1.658seconds;
controls300outer270worker/30percase/2GiBAS1GiBfile,from prior25positives17.55outer.
Shared invocation deadline includes all children/preprocessing/hashes/retries(no
retries permitted). Separate invocations have independent allowances. Supervisor+
GNU hard group guard inside Ubuntu-24.04(defaultUID1000),/usr/bin/python3,locked
offline native_budget_env_v1 uv project/repo cache,compiler g++13.3 pinnedSHA
1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769.
Preserve all exact commands/commit/hashes/tools/resource/actualoutcome and any
failedversions. Timeout is incomplete engineering,not exclusion. No ledger/index
edits, own promotion or changed-engine scientific launch authorized here.
