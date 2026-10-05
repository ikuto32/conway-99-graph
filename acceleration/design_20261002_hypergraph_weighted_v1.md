# Proposed weighted hypergraph objective v1

Status: CANDIDATE design; independent scientific approval and implementation gate
pending. No weighted scientific computation has been launched. The producer and
this design share an author. Original annealer/control/pilot sources and receipts
remain immutable.

The preliminary pilot01 saved-object audit (summary SHA
e14d136e7ff2d0e4cc2e84ef7ea8ca3deafd3d6fb3e1acf261a758ad825779f1) gives E=3034,
E_lambda=427 and E_mu=2607. Its best graph has adjacent common-neighbor histogram
{1:387,2:269,3:35,4:2} on693 unordered pairs, and nonadjacent histogram
{0:94,1:1120,2:2054,3:818,4:71,5:1} on4158 pairs. Thus306 adjacent pairs violate
lambda1 and2104 nonadjacent pairs violate mu2. These are counts of saved pairs,
not independent trajectory or target-wide search coverage. The audit adapter is
producer-authored and remains preliminary until checkpoint_audit's separate
review/execution; do not use this file as its approval.

Define a new fixed objective, SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1:

F(A) = 6 sum_{i<j,Aij=1}(CNij-1)^2
       + sum_{i<j,Aij=0}(CNij-2)^2 = 6 E_lambda + E_mu.

Its feasible domain is exactly99 labelled points,231 linear triples, every point
in7 triples, giving a simple14-regular point graph. The integer weight6 equals
4158/693, so the two pair populations have equal total weight. This is a declared
heuristic choice from the pair populations and one pilot, not a demonstrated
performance advantage or calibrated probability of success. The pilot graph's F
is5169; that is a score on the same saved object under a different objective,
not an improved score. All results must retain E_lambda,E_mu,E and F explicitly.
Minimize F. Never compare F numerically with unweighted E, earlier Gram/factor
scores or scores from another domain. A positive F supplies no mathematical
exclusion. Overall search coverage: UNKNOWN; no validated denominator.

For any binary symmetric zero-diagonal14-regular graph, positive integer weights
make F=0 equivalent to every offdiagonal common-neighbor condition and hence the
full integer identity A^2=12I-A+2J. This is a derived checking criterion, pending
independent derivation review; all raw zero graphs must still undergo the complete
independent99x99 validator. Numerical annealing temperature is not a certificate.

Use the same unrestricted admissible disjoint-triple point exchange as v1.
There is no fixed triangle core, Hadamard support or required target automorphism.
Initial cyclic symmetry is a starting choice only. Move-space connectedness and
exhaustive coverage remain UNKNOWN. Best means smallest F in the saved trajectory;
it need not have the smallest ordinary E seen. A separate ordinary-E record may
be saved only if its population and selection rule are declared in advance.

For incremental arithmetic define
q(c,a)=6(c-1)^2 when a=1 and q(c,a)=(c-2)^2 when a=0.
When a common-neighbor count changes by delta on an unchanged adjacency pair,
change F by w(a)[2(c+a-2)delta+delta^2], with w(1)=6,w(0)=1.
When an edge uv toggles, CNuv does not change, but its category changes: add
q(CNuv,new_a)-q(CNuv,old_a). Update all other affected CN pairs using their actual
current adjacency categories at each sequential edge toggle. The uv change must
not use6 times the old unweighted toggle formula. Roll back in reverse order;
check exact F,E_lambda,E_mu,E,CN cache and adjacency restoration after rejection.

The implementation must be NEW versioned C++/Python/spec files, native binary,
build manifest, controls and independent checking path. Proposed state/trace
format HYPERGRAPH_ANNEAL_STATE_V2 must include the objective identifier, exact
weight6, current/best triples, all component/weighted scores, full CN cache,
RNG/config/counters and exact acceptance schedule. Preserve v1 state bytes.
Resume a V2 state only with exactly its saved weight/config/RNG. If starting from
a V1 best/current graph, use a separately hash-bound explicit conversion/import
record identifying which graph is selected and the new seed/schedule/counter
reset; never pretend that reweighting preserves the old annealing trajectory.
Export both current.adj and best.adj to avoid the v1 raw-current omission.

Before a weighted scientific worker is admitted, all these controls must pass:

- Known rook9 grid row/column triple fixture: all integer identities and
  E_lambda=E_mu=E=F=0; independently reject its use as a99 certificate.
- Independent adjacency-set full rescoring after every fully traced proposal
  on fresh99 and rook9 forced, greedy, warming/cooling and mixed controls, using
  fixed seeds and allocations frozen before launch. Require at least2048
  proposals in each99 mode and a fully checked256 versus73+183 split resume.
- Verify every saved triple domain, all CN cache entries, component scores,
  exact weighted deltas, admissibility, acceptance decision, RNG and rollback.
  Acceptance is heuristic: retain absolute temperature tolerance1e-12 and require
  probabilistic decision margins>1e-12; ambiguous decisions veto the gate.
- Calibrate category-switch arithmetic with independently enumerated pair
  contributions and an intentionally erroneous old unweighted toggle rule.
  A wrong weight/component/weighted score/cache/duplicate triple/zero RNG must
  fail with the precise matching diagnostic. An unrelated exception cannot
  satisfy a corrupted-control requirement.
- Independent import check binds any V1 source state raw hash, selected triples,
  recomputed F components and explicit new configuration; reject wrong graph,
  changed source bytes and falsely retained trajectory counters.
- Independently review the weighted F=0 criterion and separately validate every
  raw target-zero99 matrix with exact integer matrix multiplication. Rook9 and
  floating numerical zeros never substitute for a complete target object.

Engineering build/controls use the pinned compiler, locked native uv environment,
command_deadline.py and run_compute_command.py inside Linux with native guards.
Choose allowances from the v1 measured build1.36s/control7.84s, allowing ample
margin for more components and artifact validation rather than inheriting old
build/solver caps. No gate for v1 bytes approves changed execution. Preserve all
failures and resumable outputs. Record source/tool/input/output hashes and actual
observed process-group cleanup. Independent checkpoint_audit should own the new
finite controls gate, because the design/producer author cannot approve it.

After the gate, freeze exactly one next scientific selection/allocation/seed and
success/falsification criteria before launching. Measure actual weighted native
throughput in controls to choose the proposal count and time; do not extrapolate
a general performance guarantee from v1's single40.3258s pilot. No scientific
seed, allocation or success probability is approved by this design alone.
