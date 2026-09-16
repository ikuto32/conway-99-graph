# Conway-99 research resumed, 2026-09-05

The user's new `/goal` instruction explicitly resumes work on construction
or nonexistence. `STOPPED_BY_USER.md` records the earlier stop and remains
preserved as history; it no longer describes current execution.

No valid srg(99,14,1,2) or nonexistence proof has been obtained.
`submission.txt` must be written only after independent complete validation.

Current work:

- The preserved one-neighbourhood and simultaneous E0=0 controls have
  independent audits; stronger completion conditions are being developed.
- The resumed E72 m03 runner completed and its whole macro is audited
  and credited. Small5 remains live with one worker; incomplete macro
  coverage stays out of the ledger.
- Seek stronger uniform conditions; do not resume exhaustive E71 or lower
  layer enumeration. A new simultaneous integral E0=0 compression control
  is recorded in `scratch_resume_integral_compression.md`.

Online status was checked on 2026-09-05. Brouwer's parameter table still
marks (99,14,1,2) as unknown:
https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html
The 2026 papers arXiv:2604.23037v2 and arXiv:2608.11211v1 also report no
construction or nonexistence proof. Their restricted/heuristic results
are not treated as a resolution.

## Audited continuation results

The exact integral compression control passes its separate audit and
independent mathematical review. It attains tr(C^2)=2772 at E0=0 while
the full compression defect is positive semidefinite of rank14. The
previous rounding/covariance bound therefore cannot exclude E0=0 even
after imposing simultaneous integer symmetry and the complete spectral
compression condition.

Every one of its21 source fibres also has a separately verified binary
four-row neighbour incidence with all exact root-label quotas, six
source-pair intersections and partial graph caps. The root replayed
`scratch_resume_uniform_fibre_incidence_audit.py --all`:101,871 partial
pair checks,1,176 quotas,126 intersections pass. Those independently
chosen rows disagree on852 edge reciprocities and203 degree-Gram
entries. They cannot be submitted or called a graph.

An independent simultaneous168-edge overlapping-support lift gives a
357-edge partial graph with all4,851 common-neighbour upper caps valid.
Its fixed-compression completion is impossible: a separate smaller linear
relaxation is UNSAT with a checked DRAT proof, replayed by the root.
The proof core has1,034 input clauses and78 RUP lemmas. A separate
standard-library-only unit-propagation checker also verifies all78
lemmas and confirms the core is a multiset subset of the full CNF; root
replayed that checker and reviewed the graph-to-linear-CNF mapping.
See `scratch_resume_overlap_review_rup.py/.json`. This says nothing
about a different lift or a different compression. See
`scratch_resume_overlap_lift_audit.json` and
`scratch_resume_overlap_review.json`.

The preserved one-neighbourhood witness was independently audited:
206 edges exposed,945 matchings counted,286 locally admissible, all4,851
pair caps. See `scratch_resume_neighborhood_audit.md`.

`validate_submission.py` now reads the exact requested one-based edge
format and checks all99 degrees and4,851 pairs. Its31 regression checks
pass. The old693-edge14-regular candidate in
`scratch_general_v2_best.json` fails1,916 pair conditions; it remains an
invalid research artifact. No submission.txt was created.

## Running E72 work

The authorized small5 runner remains live with one solver worker. Its
latest root-replayed independent checkpoint is26/52 shards,204/400
records, local UNSAT mass15,840. The m33 macro still needs records104–111
and receives no new central credit. The m03 supplement runner completed
all11 records, UNSAT mass448, and exited. Do not restart it.

The m03 complete-macro certificate combines69 direct UNSAT orbits
(mass3,648) with11 supplement UNSAT orbits (mass448): all80 catalog
orbits, mass4,096. Root replayed the independent whole-document delta
audit `scratch_resume_e72_m03_inventory_delta_audit.py`: only macro
(150,0,3) moves from OPEN to exact executable non-DRAT evidence, once.
Global unresolved E72 coverage is450,560; source150 open coverage28,672;
exact non-DRAT coverage4,833,280. DRAT and unproved terminal UNSAT
coverage are unchanged. This remains a restricted E72 ledger.
The historical m10-only delta audit has been replayed against the immutable
pre-m03 snapshot; see `scratch_resume_e72_m10_historical_replay.json`.
Do not interpret its mismatch with a later legitimately updated live
inventory as failure of that historical transition.

Execution identities, stopped/current union audit, and resume-safe status:
`scratch_resume_e72_status.md/.json` and
`scratch_resume_e72_small5_audit.py`. Root runner PIDs were8280 and22500,
started2026-09-05 11:40:06 JST; only8280 remains present. Do not start duplicate workers; inspect
their recorded start times and process trees first.

The objective remains active and unachieved. The next missing condition
is simultaneous reciprocity and degree-Gram compatibility for the full
84-vertex adjacency, or a uniform theorem excluding all allowed choices.
Finite exclusions of a prescribed C/lift are not such a theorem.

## Next continuation: overlap capacity and degree covariance

The preceding goal turn was progress, not a wait: it produced checked
mathematical artifacts that changed the next action. Current continuation
strengthens the fixed-overlap exclusion and records new method limits.

The168-edge overlap assignment is impossible independently of every
disjoint C block total. The old RUP core uses102 label-quota groups and95
linear pair-cap groups, with none of the105 disjoint block-total groups.
All78 proof additions remain verified after removing17,136 clauses.
Root independently replayed `scratch_next_overlap_audit.py`.

A separate exact integer weighted-capacity certificate combines658
label equalities,376 pair caps, and174 edge upper bounds into a
nonnegative left side bounded above by-807. It therefore excludes even
continuous disjoint-edge completions. Its support uses all84 vertices;
it is not a small forbidden local pattern. Root replayed
`scratch_next_overlap_farkas_audit.py`. The fixed weights give a reusable
necessary inequality on any E0=0 overlap assignment, implemented by
`scratch_next_overlap_cut.py`. See `scratch_next_overlap_summary.md`.

The fixed cut is sensitive to root-sign indexing: only one of all128
sign images of the excluded K gives a negative score. Root added
`scratch_next_overlap_cut_orbit.py`, evaluating all128 conjugate valid
inequalities; its minimum (-807 here) is invariant under these swaps.
The XOR composition check passes. This prevents equivalent relabelings
from escaping the existing cut. Passing all128 still gives no completion
witness, and a complete overlap assignment (unlisted overlap edges absent)
is required. These tests do not enumerate different E0 classes.

A new rational PSD covariance control meets the prescribed sharp C,
all source means/own-zero/quota/trace conditions, and all441 global
degree-Gram entries. Its21 source covariance matrices have rank13;
actual centered four-row populations have rank at most3. Thus this
control supplies neither integer D nor adjacency B. Root independently
replayed `scratch_next_degree_covariance_control_audit.py`; all21 exact
PSD checks pass. The missing rank/alphabet/reciprocity conditions remain
essential; a positive E0 bound is still unproved. The exact derivation and
real-incidence interpretation are in
`scratch_next_degree_covariance_control.md`.

Two bounded attempts to construct the full adjacency at this C ended
UNKNOWN with no candidate, no exclusion, and no remaining live session.
Their limitations are in `scratch_next_full_c_search_note.md`. No
submission.txt exists. The original full goal remains active.

A concrete next construction experiment can vary the overlapping-support
placement itself, test the reusable capacity inequality and then the full
linear completion system, and only attempt nonlinear common-neighbour
completion for survivors. The previous fixed overlap is now excluded
regardless of its disjoint block totals, so changing those totals alone
cannot repair it. This is a candidate-generation strategy, not exhaustive
E0 coverage or a replacement success condition.

## New complete-overlap assignments and reusable cut bank

Four alternative complete168-edge overlap assignments at the saved sharp
C were generated in under4 seconds each. Each is distinct from the
original and its predecessors under all128 root-sign swaps. Root replayed
all four independent357-edge partial-graph audits (all4,851 pair caps,
quotas, overlap C totals, and sign-orbit exclusions pass).

Each nevertheless has an exact capacity contradiction without disjoint
C totals. Root wrote a separate auditor deriving the constraints from
the full99-vertex partial adjacency sets, importing neither producer nor
solver. All1,680 disjoint-variable coefficients are nonnegative and the
combined RHS values are-819,-793,-796,-797. See
`scratch_next_overlap_alternatives_farkas_audit.py` and the four audit
JSONs; summary: `scratch_next_overlap_alternatives_summary.md`.
The r1/r2 primal LPs returned ABNORMAL and establish no conclusion; their
separate exact dual certificates are what proves these fixed exclusions.

All four pass the original128-sign cut family (minimum scores
8,654;9,265;9,015;9,088), so these are new necessary inequalities.
They are four distinct sign orbits, not proved distinct classes under
every isomorphism and not an exhaustive exclusion at this C or E0=0.

`scratch_next_overlap_cut_review.py` independently verifies the generic
cut algebra, all1,680 edge ids and16,384 sign compositions. It also proves
that, with the negative-part box correction, removing nonnegative upper
bound multipliers preserves validity and can strengthen the cut.
Root's `scratch_next_overlap_cut_bank.py/.json` compiles five coordinate
cuts using this simplification. The5-by5 cross-evaluation rejects each
stored assignment with its own cut; all fixed-index off-diagonal scores
are positive. The r1 own score improves from-793 to-794. Eight original
sign controls match the prior evaluator exactly when upper multipliers
are retained. No solver remains from this bounded alternative pool.

The five no-gamma inequalities now have a pure-stdlib sparse polynomial
compiler. Root replayed `scratch_next_overlap_cut_compile.py`:60 direct
semantic comparisons and100,800 affine coefficients agree. The compiled
artifact SHA is
`f0f2a851b782f37ddd32e8d3af10da07c35f3ddd2b78a16448fd503fab13277d`;
the check JSON binds19 actual inputs, including the proof coefficients,
independent audits, comparison controls, and compiler source.

`scratch_next_overlap_cut_encoding.md` proves that the existing one-way
products p>=K_uw*K_vw can be reused: every product coefficient in the cut
RHS is nonpositive, and choosing exact products preserves the base model's
upper caps. The max terms must use exact equalities, not merely epigraph
lower bounds. All five cuts need4,881 exact-max variables; their24,492
wedges are already among the generator's65,520 products. This is an
encoding theorem and finite coefficient audit, not graph feasibility.

The first actual five-cut CP-SAT model was built and run once with a
45-second limit and one worker, excluding all640 sign images of the five
saved K assignments. It ended UNKNOWN after45.047 seconds with no
candidate. Model validation passes; all4,881 maxima use exact equalities.
Root reviewed the integration code and replayed
`scratch_next_overlap_cut_guided_audit.py`, checking the compiled SHA and
all19 leaves. See `scratch_next_overlap_cut_guided.py/.json` and
`scratch_next_overlap_cut_guided_audit.json`. No LP/dual follow-up or
unchanged extension was run; this process is terminal.

This continuation is progress: it completed a whole E72 macro with an
independently checked accounting transition, produced four new exact
overlap obstructions, and implemented a proved reusable cut encoding.
The bounded five-cut UNKNOWN is a method limitation, not an exclusion.
Only the saved small5 E72 runner remains live. No submission.txt exists,
and the original construction-or-nonexistence goal remains active.

Next construction work can seek a new overlap assignment through a
constraint-preserving local edge trade or a simpler candidate generator,
then apply the exact cut bank externally before full linear completion.
The dense exact-max model currently has no known candidate and should
not be silently rerun unchanged. Any successful linear relaxation must
still meet integer adjacency, reciprocity, and all nonlinear pair counts.
