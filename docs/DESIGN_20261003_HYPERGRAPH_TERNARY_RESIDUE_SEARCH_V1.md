# Proposed complete ternary-residue objective on linear triples

Author: /root/structural. Timestamp: 2026-10-03T02:14:52+00:00.
SOURCE ONLY; no implementation calibration or scientific command has run.
The current strict-lex census and its exact inputs are not changed. Target
resolution is UNKNOWN. This design is a separate attack for ROOT review after
at most five already authorized strict-lex continuation steps, not a new run.

## Exact scope and purpose

The proposed domain has 99 labelled points and 231 ordered three-point lines.
Each line has three distinct points, every point belongs to exactly seven
lines and every unordered point pair occurs in at most one line. Its point
graph is simple, symmetric, zero diagonal and degree14. Every graph edge is
in its generating triangle, but extra triangles and E_lambda>0 are allowed.
There are no frozen root lines or scalar root restrictions in this lane.

For a true target graph, adjacent common-neighbor count1 makes every edge lie
in one actual triangle, and its14-neighbor matching gives seven triangles
through each vertex. Thus this domain contains every target's complete triangle
decomposition; no target automorphism or additional incidence-kernel premise is
assumed. This observation does not prove completeness of the proposed move
component, nor does a failed run exclude the domain or target.

Let c_uv be the integer common-neighbor count and a_uv the adjacency bit. For
every unordered pair u<v define r_uv=c_uv+a_uv-2. Set

 F3 = sum_[u<v] 1[r_uv is not divisible by3],
 E_lambda = sum_[u<v,a_uv=1] r_uv^2,
 E_mu = sum_[u<v,a_uv=0] r_uv^2, E=E_lambda+E_mu.

F3 is a nonnegative INTEGER residue-violation count of all4851 unordered pairs;
symmetry and degree14 supply the complete diagonal congruence. The independently
reviewed theorem in source274ce3/audit9f34 proves F3=0 implies the complete target
integer identity in this domain. No approximate, floating, sampled or cached
zero is accepted. Raw adjacency must pass a separately authored full SRG
validator. A numerical optimizer or successful reference execution cannot
approve its own discovered object.

Compare states by the exact tuple(F3,E). The scalar
 F=819820*F3+E
has the same order because E<=4851*13^2=819819 is a conservative bound in the
simple degree14 domain. F<=3977766639, exceeding signed32-bit range; all metrics,
differences and retained objective values must use signed64-bit integers.
Native Metropolis temperature/exponential calculations, if chosen later, are
heuristic acceptance rules only; they never certify a graph or mathematical
bound. Scientific temperature, seed, start graph and resource allowance remain
null/unselected pending applicable calibration and ROOT review. No speed or
probability-of-success claim is made.

This differs from the strict-lex root lane: feasible swaps can increase
E_lambda and change the root residual. A state with E_lambda>0 may be preferred
when it lowers F3. It also differs from the old60*E_lambda+E_mu objective.
Old engine/state/trace/calibration hashes do not approve this changed objective.

## Independently derived feasible swap

Choose distinct ordered line indices i,j and positions p,q. Write the lines
as{x,a,b} and{y,c,d}, with x,y the selected points. Require x not in the second
line and y not in the first. Replace them by{y,a,b} and{x,c,d}, preserving each
position and every other ordered row.

Remove the four pairs xa,xb,yc,yd. In the pair occupancy AFTER those removals,
require every new pair ya,yb,xc,xd absent and non-loop. This rule permits the
lines to share one unselected point. Checking absence before removal would
incorrectly forbid those valid swaps. The new pairs are distinct by selected
point exclusivity; every new triple still has three distinct points. Original
lines share at most one point by linearity. Unchanged pairs ab,cd and all other
line pairs retain occupancy. These facts prove final linearity exactly.

Point-line incidence counts do not change: x loses its first line and gains
the second; y does the reverse; a,b,c,d retain their line counts. Therefore
degree14 is preserved. No requirement E_lambda=0, rootR descent or a fixed
local SRG profile is imposed. Swapping the same positions again is an inverse
proposal. This inverse is available but is not an ergodicity proof.

When an unselected point z is shared, xz and yz are removed and re-added; their
net adjacency changes are zero. Net changed edges must be combined before
describing changed rows. A discovery trace must preserve both the ordered
eight-toggle sequence and its net cancellations. Rollback restores every
integer metric, cache, adjacency bit and ordered line, not merely the score.

## Exact local score changes

For one unordered pair, a common-neighbor change delta with fixed adjacency
changes the squared residual by2*r*delta+delta^2. The residue cost changes by
 1[(r+delta) mod3 !=0] - 1[r mod3 !=0].
When a graph edge bit changes, its common-neighbor count is unchanged during
that single edge toggle: the updated endpoints' diagonal bits are zero. Its
old/new residuals are c+a-2 and c+a'-2, so both residue and squared/category
changes must be applied. In particular lambda/mu reclassification is required.
Signed C++ residues must be normalized to0,1,2 for reported histograms; testing
divisibility by3 itself is sign independent.

For a toggle of edge(p,q) by sign s, every w outside{p,q} changes c_pw by
s*a_qw and c_qw by s*a_pw, with adjacency sampled before that toggle. c_pq does
not change. The diagonal degree cache changes by s for both endpoints but is
not part of the off-diagonal objective. Sequential toggles must use current
intermediate adjacency, so shared-point cancellation and rollback remain exact.

An alternative reference path compares completed before/after matrices.
Let U be precisely their changed ROWS. Only unordered pairs with at least one
endpoint in U can change their row dot product or adjacency classification.
Even a common neighbor in U cannot change a pair outside U: both endpoint rows
are literally unchanged. Recompute every such pair's integer scalar dot product
and subtract old costs. If |U|=s, the complete affected population is
binom(99,2)-binom(99-s,2); s<=6 gives at most573pairs. Shared-point cancellations
can make U smaller, so do not infer U from all line points without checking.
This reference path supplies a different local calculation from native toggles;
future independent controls must compare both to a full dense Gram calculation.

## New checking and control plan, unexecuted

The source-only reference
acceleration/theory_20261003_hypergraph_ternary_residue_reference_v1.py
reconstructs literal pair occupancies, checks exact point degrees, computes all
integer scalar common-neighbor counts, implements exclusive-swap feasibility
and recomputes score changes for the changed-row pair set. It imports no native
producer. It is a design/producer reference, not its own independent gate.

Before any native run, freeze a new producer, wrapper, state/trace schemas and
independently authored checker, toolchain/config/source hashes and exact fixture
population. All old states may supply graph-only starts through a new separately
checked adapter; old RNG/counters/temperature/objective/history cannot become
new-format continuations. A new state must bind exact tuple/scalar constants,
current and best objects, seed/RNG/counters, schedule, new objective/move markers
and raw graph lineage. Retain both current and best, plus every raw residue-zero
candidate. Sparse records cannot establish the earliest full trajectory event.

Proposed cheap positive-control population: raw rook9, prism9 and cube12 fixtures
from the preserved weight60 source; all ordered distinct line-index/position
proposals, respectively270/270/504=1044 label attempts. This is a declared future
test population, not executed work or a count of valid moves. Required outcomes
include rook9 exact generalized SRG zero, lambda-positive prism, shared-point
cancellation, disjoint swaps, invalid pair collisions, exact inverses and
positive-lambda states accepted as domain-valid. Cube12 is an n12/degree4
engineering fixture, not an instance of the order99 equivalence.

A separately authored checker must construct dense adjacency/Gram from the raw
ordered lines, classify all1044 proposals by independent replacement-plus-full
linearity/degree checks and compare complete before/after(F3,E_lambda,E_mu,E,F).
It must test illegal selected shared points, old-pair presence versus final
pair absence, symmetric/binary/loop/degree/duplicate-pair corruptions, boolean/
float aliases, changed score/category/cache, negative-residue histogram mapping,
rollback, RNG/counter/config/schema identity, whole-versus-split state equality,
retained current/best distinction and actual integer-validator vetoes. Exact
diagnostic stages and case counts must be frozen before invocation, not inferred
after agreement. A malformed source artifact cannot pass by failing at a later
missing-output or score field.

RNG selection and acceptance protocols remain unselected. If a rejection-bounded
modulo sampler is used, disclose the conditional uniform-word argument and the
actual consumed words; do not claim PRNG uniformity. Probe tapes must exercise
valid overlap/disjoint moves, rejection rollback and departure from E_lambda=0.
No frozen-root rule may accidentally survive from the previous engine.

Future controls should use the pinned locked/offline uv environment and supported
supervisor, with an evidence-based contained budget and internal save reserve.
No controls, compile, optimization or scientific command is authorized by this
note. ROOT review, independently calibrated checking and fresh resource/ownership
observations are required before each separate invocation. Every target zero
requires complete raw99adjacency and independent integer validation.

Existing repository residue/mod3 evidence concerns rooted necessary operators
and a fixed incidence-only ternary rank fixture. Neither proves feasibility of
the complete adjacency congruence. Prior search and false generic rank arguments
are not reused as proof premises. Novelty and ergodicity are UNKNOWN.
Overall search coverage: UNKNOWN; no validated denominator.
