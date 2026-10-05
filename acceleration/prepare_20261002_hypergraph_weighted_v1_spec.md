# Fixed-weight hypergraph engine v1 build and controls

Producer: /root/native_driver. No independent approval by this author. Sources
are new weighted versions; preserve the complete unweighted v1 sources, build,
controls, pilot and auditors. No gate for their bytes approves this version.
Use the existing repository, compiler pin and locked native uv environment.

Objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1 is exactly F=6E_lambda+E_mu,
where E_lambda=sum_adj(CN-1)^2, E_mu=sum_nonadj(CN-2)^2 and ordinary E is their
sum. Lambda weight is fixed integer6, not a CLI tuning option. Feasible target
domain:99points,231 linear labelled triples, eachpoint occurs7times, giving a
14-regular simple graph. Rook9 controls use6 triples/degree2 occurrences and
graphdegree4. The initial99 graph/trades/RNG match the unweighted implementation;
no target automorphism, fixed triangle core or Hadamard support is required.
No claim about move-space connectivity, exhaustive coverage or target resolution.

Incremental CN changes use actual current adjacency category weights. Toggling
uv changes its category while its CN remains fixed: replace its old lambda/mu
contribution by its new contribution and update F by6 times lambda delta plus
mu delta. Rejections toggle the8 changed edges in reverse order and require exact
F/lambda/mu rollback. Producer bitset full reconstruction/domain/cache checks run
after every engineering proposal, including invalid or rejected proposals. These
are producer diagnostics, not independent verification.

Implementation uses a distinct HYPERGRAPH_WEIGHTED_ANNEAL_STATE_V1 tag rather
than the design's tentative HYPERGRAPH_ANNEAL_STATE_V2 tag. Neither accepts an
unweighted checkpoint as a weighted resume. Ordered text fields are:

HYPERGRAPH_WEIGHTED_ANNEAL_STATE_V1
objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1
lambda_weight6
n degree seed mix_steps schedule_steps t_start t_end forced
step admissible accepted best_updates
weighted_energy base_energy lambda_energy mu_energy
best_weighted_energy best_base_energy best_lambda_energy best_mu_energy
rng followed by4 decimal uint64 words
current count followed by ordered labelled triples
best count followed by ordered labelled triples
cn count followed by upper-pair CN integers; END

Each field is a separate labelled line, including the exact spaces omitted in
this compact field list. RNG must be nonzero. Score/component/cache/domain and
best weighted order are fully recomputed on native load. Best selection minimizes
F, so its ordinary E need not be the smallest ordinary E visited. Both raw
current.adj and best.adj are saved with headern andn binary rows.

Resume retains the entire saved objective/configuration/RNG/counters. CLI seed,
mix/temperature/schedule values are ignored on resume, preserving the trajectory.
Runtime step/time/checkpoint/trace limits come from the new invocation. An explicit
--import-v1 PATH --import-select current|best instead validates the complete old
unweighted record, selects exactly its labelled graph, recomputes weighted scores,
sets current=best, resets all counters to0 and uses the NEW CLI seed/config/RNG.
Import and resume are exclusive. The wrapper authenticates the raw import file;
import_source must never be confused with a continued old trajectory.

Weighted JSONL move records retain step/indices/old/proposed triples, all boolean
admissibility/acceptance/mixing facts, heuristic temperature and decimal RNG/draw
words. They include objective/lambda_weight, delta (proposed F change, even if
rejected), weighted_energy_before/after, lambda_energy_before/after,
mu_energy_before/after and best_weighted_energy. The after component values are
the actual accepted-or-rolled-back state, not the rejected proposed graph. An
independent checker must recompute the proposed graph and delta from raw triples.

Every successful engineering call also exports pair_costs.jsonl: for c=0..14,
a=0,1, every CN increment/decrement remaining in0..14, plus every edge category
switch. Record kind,c,a,delta,new_c,new_a,old_lambda,old_mu,new_lambda,new_mu,delta_F.
There are56 CN and30 EDGE records,86 total per successful call. These algebraic
pair controls are not assertions that every pair case is realizable in a graph.
Independent derivation must reject an intentionally erroneous old unweighted
category-switch cost and corrupt weight/component/delta records.

Freeze32 native engineering calls before launch:16 successful and16 expected
exit2 calls. Every successful proposal is traced and each full current graph is
reconstructed after every proposal; checkpoint interval64, seconds15. Numeric
acceptance remains heuristic exp/RNG, with independent temperature tolerance and
probabilistic margin threshold1e-12. Fixed successful population:

- rook9_positive0steps/T0; rook9_forced2048/T0/forced.
- target99_forced2048/T0/forced; target99_greedy2048/T0;
  target99_anneal2048/T16; target99_cooling2048/T48 to0.2;
  target99_warming2048/T0.2 to48; target99_mixed2048/T24/mix256.
  These use seed99032020, mix0 unless specified, schedule1024.
- resume_whole256, resume_first73 and resume_second183 from first/final;
  seed99032021,T16,mix64,schedule1024. Require identical final raw bytes and
  whole trace equals first+second.
- import_v1_current and import_v1_best2048 each from pinned old
  target99_mixed/final.state SHAef9e5ca27c248413d62efdb0888eb23d2eb734ed955431653145e830ef0872c1.
  Its old currentE5304/bestE5248 are distinct; source is bound by the independent
  unweighted raw controls gate only. New seed99032022,T24 to0.2,mix64,schedule1024.
- import_resume_whole256, import_resume_first73, import_resume_second183 from
  imported best initial.state and first/final, same new settings. Require raw
  final byte identity and complete trace concatenation.

Expected successful proposal population is19,456, counting whole/split control
execution attempts separately, not distinct graphs. Expected304 intermediate
step checkpoints at interval64 if no15s timer checkpoint adds an additional
one; auditor counts actual saved files and completely checks all. Five zero-step
copies do not exist: only rook9_positive has0steps. No performance guarantee.

Expected malformed weighted resumes mutate one field at a time: lambda_weight,
weighted_energy,best_weighted_energy,lambda_energy,mu_energy,base_energy,CNcache,
duplicate current triple, zero RNG, accepted counter above step. Five malformed
v1 imports mutate ordinary current score,CNcache,duplicate current triple,
accepted counter above step,zero RNG. Final malformed selector uses 'wrong'.
Require matching exact stderr diagnostic, empty stdout, no native scientific
artifacts and independent rejection of the exact corrupted content; unrelated
exit2 or unrelated exception does not calibrate a negative. Preserve every failure.

Before weighted scientific admission the independent agent must validate the
32 exact receipt commands/code/build/tool/environment/resource pins, complete
raw artifact population, all19,456 proposals, all saved objects/caches/components,
pair tables, imported source selection/reset and both complete split resumes.
Calibrate its own positive/corrupt parser/matrix/scope/trade/RNG/weight controls,
including false retained old counters or wrong selected graph. Check F0 iff exact
SRG identity on the declared regular domain by independent derivation. Any raw
targetF0 requires a full independent99matrix check; rook9 is never a99certificate.
Required fresh gate status INDEPENDENT_HYPERGRAPH_WEIGHTED_ANNEAL_V1_CONTROLS_PASS
must bind the exact changed CODE files, binary and build_manifest before research
mode can proceed. Producer must not promote itself.

Choose build300s outer240s worker from observed v1 build1.36s with ample setup/
compile/log/hash reserve. Controls600s outer540s worker, per-case30s native guard,
2GiB AS and1GiB per-file cap, from v1 total control7.84s and larger new32-call
population;20s worker/10s outer reserve, no automatic retry. The per-case guards
share the one invocation's deadline; do not add per-case times or subtract previous
commands. Reassessment1800s exceeds these deliberately smaller allocations.
Six hours is the ceiling, no inherited historical build/solver stopping cap.

Supervisor and GNU guard execute inside Linux. Use /usr/bin/python3 supervisor,
locked offline uv project acceleration/native_budget_env_v1 and persistent repo
build/native-budget-linux-venv environment/cache. Pinned g++13.3 SHA
1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769.
Record exact commands, source commit, hashes/tool versions, actual native and
outer outcomes/cleanup. A completed build/control producer output is pending
independent verification; timeout or failure is not a mathematical exclusion.
No ledger/index edits or weighted scientific launch authorized by these controls.
