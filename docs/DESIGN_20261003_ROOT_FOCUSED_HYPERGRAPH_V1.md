# Root-focused construction after the complete warm-root census

Design only. This document launches no search and approves no changed engine.
The fixed two-line census remains the immediate experiment; its independently
checked outcome must inform the decision to implement this alternative.

## Question and exact inputs

Can admissible degree-preserving linear-triple trades produce a graph with
zero adjacent-pair residual and zero common-neighbor residual at one selected
root, while preserving that root's seven triples? This is a construction
heuristic on a restricted move space, not an exhaustive target exclusion.

The independently checked warm saved-object result is
`acceleration/results/20261003_independent_review/weight60_warm01/summary.json`,
SHA256 `256c8277ab5c69e74f4c9725c4b42e96e31b4e546c490b8e231df4ed6831bf6c`.
Its final graph has E_lambda=0 and E_mu=3480, with 4764 ordered failures of
the target matrix identity. The separate ROOT dense census report is
`acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/summary.json`,
SHA256 `becf048cbb32ec577a78c7084fc949103af91f66c92c5936137a9740c5cdd35a`.
It checks exactly two labelled raw graphs and all 198 graph/root choices:
neither has a root with all 84 nonneighbors having exactly two common
neighbors. The final graph minimum root residual is 52 at roots 11, 41, 77;
the step-zero graph minimum is 50 uniquely at root 81. These are VERIFIED
saved-artifact statements within those reports' finite scope.

If this design is selected without a better independently checked census
neighbor, the prospective deterministic start rule is the minimum root
residual among those 198 checked choices, then graph label/root in lexical
order for any tie. That selects the step-zero graph and root 81:
`acceleration/results/20261003_hypergraph_weight60_warm01/native/first_lambda0.adj`,
SHA256 `818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836`.
Its ordered triple source must be bound to the exact step-zero serialized
state before implementation. The graph start is imported with a new RNG,
counters and objective configuration; it is not an old RNG continuation.
This prospective selection can change only in a new frozen protocol that
records the complete local census evidence, rather than omitting failures.

## New objective and move domain

Use a new objective version, provisionally
`SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1`, with exact integers

`E_lambda = sum_{i<j, Aij=1}(CN(i,j)-1)^2`,

`R_root = sum_{j!=r, Arj=0}(CN(r,j)-2)^2`,

`F_root = 60*E_lambda + R_root`.

Lower is better. The root diagnostic uses the current graph's own
nonneighbors; a checker must not reuse the old outsider list unless it
independently confirms that the frozen root edges were preserved.
The original full E_mu remains a separately recomputed diagnostic and
target-certificate criterion. F_root values are not comparable to the old
global F60=60*E_lambda+E_mu values. No performance or probability assertion
is made from the old engine's timing.

Keep 99 points, point degree 7, 231 distinct linear triples and hence a
14-regular simple point graph. Freeze exactly the seven labelled triples
containing r, including their ordered literal vertices. The new kernel
draws pairs only among the remaining 224 triples. It otherwise uses V2
exclusive selected points, shared-one-point permission, exact linearity
tests, duplicate rejection and degree preservation. This preserves the
14 root edges and seven root-neighbor matching edges. Additional unwanted
edges within that neighborhood are penalized by E_lambda. Restricting this
kernel does not establish its connectedness or exhaustive coverage.

An explicit new proposal-distribution/RNG version is required: drawing
indices uniformly from the 224 nonfrozen labelled triples differs from
drawing all 231 and rejecting frozen lines. Neither choice may be hidden
under the V2 engine's old gate. A split checkpoint must reproduce the new
distribution, RNG state, root/frozen-line identity and counters exactly.

## What a zero proves and what it does not

F_root=0 means E_lambda=R_root=0 in this declared domain. It supplies a
matching root neighborhood and two root neighbors for each outsider.
It does not enforce all other nonadjacent-pair common-neighbor counts and
does not certify the original complete SAT scaffold or an SRG.

Before describing such a graph as the original scaffold, independently
check every outsider's support pair and its multiplicity. There are 84
permitted unmatched neighbor pairs. R_root=0 gives 84 outsiders with
two-element support, but does not alone establish that each permitted
pair occurs once; repeated support pairs remain an explicit possibility
requiring a separate exact check. A new support-collision penalty, if
needed, would change the objective and requires another version/gate.
Never introduce adjacency assumptions into an unrestricted SAT attempt
merely because a partial graph scores zero on this objective.

Every saved potential target graph must additionally pass a separately
authored complete 99 by 99 symmetric binary zero-diagonal integer check
of A^2=12I-A+2J. A zero numerical or local objective is not that check.

## Required implementation controls and independent checking

Freeze new C++ source, wrapper, state/trace format and objective spec before
build or controls. Preserve the unchanged V2 sources, failed controls and
all scientific raw states. The independent checker must derive full
adjacency sets/common-neighbor counts and both objective components without
importing the changed producer. Its finite scope must cover:

- known-valid rook9 full SRG identity and root residual, with the generic
  control clearly separated from the target99 gate;
- every proposed trade in the finite controls, including accepted/rejected
  overlap trades, root/frozen-line exclusions, category changes and rollback;
- root residual deltas against complete matrix multiplication, including
  deliberately changed root adjacency in a checker-only negative fixture;
- exact imported triples, recomputed full E_lambda/R_root/E_mu, new seed
  expansion, reset counters, root/frozen-line identity and step-zero snapshot;
- whole/split/resumed byte-equivalent RNG, state, traces, counters and first
  retained F_root=0 state; current/best matrices exported independently;
- strict corrupted score/cache/row/root/frozen-line/RNG/counter/config/matrix
  controls with the expected diagnostic, not acceptance of arbitrary errors.

A distinct pre-output saved-object checker/calibration must bind the exact
changed source/helper closure. It checks every saved complete object and
only explicitly anchored trace segments; sparse gaps cannot support a
complete-trajectory or earliest-attainment statement. Preserve the first
retained E_lambda=R_root=0 raw state/matrix independently of the best global
E_mu graph, and label unobserved earlier history UNKNOWN.

No scientific allocation, seed, temperature schedule or proposal count is
authorized here. Set them in a separate frozen plan after engineering
throughput, calibration and resource evidence. Use the current contained
per-command deadline, a shutdown reserve and resumable immutable outputs;
ROOT must review the exact frozen command before launch. The acceptance
criterion is a checked root-local construction or a useful checked saved
improvement, never target nonexistence or target-wide coverage.
