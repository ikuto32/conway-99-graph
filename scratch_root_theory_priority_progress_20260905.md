# Theory-priority progress, 2026-09-05

**STOPPED BY USER at 11:31 JST.** All research worker trees are stopped.
The latest handoff is `STOPPED_BY_USER.md` and its machine-readable JSON.
The following running/progress descriptions are historical. Do not restart
any calculation until the user explicitly requests resumption.

## 11:27 JST addendum: one completed E72 macro and uniform moment limits

The complete source150 `(1,0)` macro is now independently coverage-audited:
all 96 local orbits, labelled mass 8,192, are exact local-CSP UNSAT. Its
immutable certificate is
`scratch_root_e72_source150_small5_joint_primary_m10_complete_audit.json`.
This is finite executable CSP evidence, not a DRAT certificate. The root
replayed its catalogue/shard audit and the separate whole-inventory delta
audit. Only this complete macro was newly credited. Global E72 unresolved
coverage is now **454,656**, including source150 open coverage **32,768**.
DRAT-backed coverage remains 135,098,368; exact non-DRAT coverage is
4,829,184; terminal solver UNSAT without checked proof remains 1,163,264.

The six historical source150 positive degree/label/quota controls now use
the byte-identical `before_m10` inventory snapshot. Their mathematical
payloads and witnesses did not change. Both independent audits were
replayed after this metadata migration, including all 161,280 local subset
checks and 792 row-quota decisions.

At the 11:21 small5 checkpoint, 21/52 shards and 168/400 records were
independently audited, with local UNSAT mass 13,248. No incomplete macro is
deducted from the central inventory. The separate m03 every-depth job
finished normally: all 80 orbits checked, 69 local UNSAT / mass 3,648 and
11 local SAT survivors / mass 448, no UNKNOWN. These are local feasibility
statuses, not graph witnesses. The independent catalogue audit was replayed
by the root. A survivor-only stronger joint-map check started at 11:26 JST,
using one worker in the slot freed by the completed every-depth job and
saving each of the eleven outcomes separately. Its manifest is
`scratch_root_e72_source150_m03_joint_supplement_manifest.json`. The existing
small5 runner and ordinary m03 job were left unchanged.

Uniform theory work produced two complementary, independently replayed
results, without enumerating any lower E0 layer:

- An exact rational averaged-row control at E0=0 passes the degree first
  and second moments, root-label quotas, and one-row partial-graph caps.
  It uses 630 degree templates, 30 per source fibre. It is not a simultaneous
  integral compression C or adjacency B. See
  `scratch_theory_uniform_e0_zero_degree_moment_control.md`.
- Integer compression entries force `tr(C^2)>=b(E0)`, with a four-piece
  convex function. In particular at E0=0, `tr(C^2)>=2772`, whereas the
  symmetrized Cbar has square trace 2688. Thus actual integer compressions
  require covariance at least 84, information lost by the averaged model.
  See `scratch_theory_uniform_compression_rounding.md` and its independent
  audit. This necessary bound is already implied when integer C entries
  are modeled explicitly; it excludes no low layer and is not a positive
  E0 lower bound.

The bounded E71 test frontier remains 59 macros / coverage 26,017,792.
The goal is unchanged and active. No verified Conway graph, nonexistence
proof, or universal positive E0 lower bound has been obtained.

## Earlier 11:01 JST addendum (historical)

The exact-label subset support test now independently
excludes six additional macros of coverage 360,448. The live disjoint
inventory therefore has **59 remaining macros, coverage 26,017,792**.
The 65-macro figures below describe the earlier raw-moment stage and are
preserved as history. See `scratch_theory_e71_label_subset_moment.md`.
Attainable four-row fibre moment hulls and the bounded single-row label
quota probe add no further macro exclusions in this frozen test frontier.
At the 11:01 JST liveness check, the E72 runner and both m03 processes
remain live. The small5 checkpoint has 15/52 shards, 120/400 records and
UNSAT mass 9,888 independently checked, with no whole macro yet credited.
All six source150 compressions also pass the new label-subset and single-
row quota moment models with independently checked rational weights.

The goal is unchanged: construct a verified Conway graph or prove
nonexistence. No valid graph or nonexistence proof has been obtained, and
`submission.txt` remains absent. The existing 916 order-eight classes,
208 deletion rows, 944 marked-vertex rows, 4,440 marked-pair rows, and
2,414 coefficient matrices are reused read-only, not regenerated.

## New audited degree-moment obstruction

The exact identity `R^T R=4K4`, together with complete single-vertex degree
domains and zero residual sum in each fibre, gives a small convex moment
model. Integer quadratic inequalities certify its infeasibility without
enumerating any local graph completion.

The frozen 132-macro / 140-profile E71 frontier now has:

| Stage | Excluded macros | Excluded coverage |
| --- | ---: | ---: |
| New exact degree-moment certificates | 66 | 22,675,456 |
| Prior source724 transport/projector proof, disjoint | 1 | 32,768 |
| Audited union | 67 | 22,708,224 |
| Remaining in this input | 65 | 26,378,240 |

The new 68 profile certificates were discovered in about 29 seconds and
replayed in about eight seconds by a checker that imports neither the
producer nor its base helper and uses no LP solver. All 23,137 raw degree
rows and every coefficient were independently reconstructed. Each credited
macro has certificates for every frozen full-Gram profile.

The simplest explanatory certificates are source694's `4 != 52` quadratic
identity and source901's `384 != 512` square identities. They are included
in the 66-macro total, not added again.

Main files:

- `scratch_theory_e71_degree_moment_lp.md`
- `scratch_theory_e71_degree_moment_lp_frontier.json`
- `scratch_theory_e71_degree_moment_lp_audit.py/.json/.md`
- `scratch_root_e71_theory_frontier_inventory.py/.json`

This is a scoped compression-profile exclusion, not an E71-wide exhaustive
search and not a universal positive lower bound on `E0`.

## Structural compression of the triangle-rooted flag family

Every one of the 99 locally admissible triangle-rooted six-vertex flag
counts has the form `a_f+b_f t(T)`, where `t(T)` counts prism mates of the
root triangle. The earlier 74-type list is only a visible subset.
The full raw Gram has rank at most two, and is rank one when `P=0`.
Thus this large PSD family reduces to affine equalities and one scalar
variance condition. Higher-order affine completion obstructions are not
ruled out.

The proof, full coefficient table, and independent checker are
`scratch_theory_triangle_six_flag_affine.py/.json/.md` and
`scratch_theory_triangle_six_flag_affine_audit.py/.json`.

The bounded endpoint cross-centre spectral lane also produced
`tau_K+7 eta=4158+tr(P^2K)/6`, but an exact scalar control permits
`tau_K=0, eta=648`. This is not an entrywise matrix realization or an
endpoint exclusion. Its scope is recorded in
`scratch_theory_k_projector_crosscentre_spectrum.md`.

## E72 remains in progress

The source150 small5 runner resumed from six independently checked completed
shards. At the 10:27 JST checkpoint it had eight of 52 shards complete:
64 of 400 orbits, exact UNSAT mass 5,312. No whole macro was yet eligible
for exclusion. Partial shard mass is not deducted from the central macro
inventory. The live checkpoint is
`scratch_root_e72_source150_small5_joint_primary_partial_audit.json`.

The two pre-existing m03 searches and the small5 workers continue; no
duplicate graph-search worker was started for the theory experiments.
The six open source150 macro compressions have exact feasible degree-moment
weights, so this new necessary condition does not eliminate them.

The central E72 inventory remains unresolved coverage 462,848, including
source150 coverage 40,960, until a complete macro receives independent
coverage verification.

## Next priority

Preserve the E72 completion work. For E71 and below, use bounded data only
to strengthen the degree-moment inequalities or derive a uniform `E0`
bound; do not resume layer-by-layer local-completion enumeration. The
current certificates remove a substantial part of a frozen test frontier,
but they have not yet been converted into a compression-independent lower
bound that limits the number of E0 layers.
