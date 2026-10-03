# Exact degree-block Gram bound pilot

Status: preregistered **CANDIDATE** producer. Independent checking is required
before any cut is used in SAT or any mathematical claim is promoted.

Question: for each of the nine frozen vectors behind
`results/20260930_rook_box_batch01/accepted_checkpoint.json`, does its exact
Gram quadratic already have negative maximum over the degree-only780edge
relaxation? Then can degree constraints shorten the initial21literal box cut?

Scope: one exact fixed-central-factor scaffold and its780Boolean free edges.
The160 degree equations separate into four internal perfect matchings on10
vertices, four10by10 bipartite perfect matchings, and two10by10 bipartite
degree-two factors. The common-neighbor inequalities are dropped, so these
independent blocks form a superset of the locally feasible assignments.
No symmetry or universal rook containment is assumed.

For each exact saved vector, compute all780coefficients `-18*w_u*w_v` and
the fixed-part quadratic from the raw59graph. The sum of ten independent
block maxima plus this constant is an upper bound on the true local maximum.
Each internal matching uses an exact subset recurrence, with saved table and
attaining edges. Each bipartite block uses integral successive shortest paths
and records both an attaining edge set and a dual certificate:

`max Σ c_e x_e ≤ Σ_v b_v α_v + Σ_e max(0,c_e-α_u-α_v)`.

Here forced-one edges are removed after consuming endpoint quotas and
contributing their weight; forced-zero edges are removed. Alpha may have
either sign. Primal feasibility and exact primal–dual equality certify the
maximum independently of the optimization implementation. Fixed values
come from a known feasible local graph, so the actual pilot cases are
feasible. Controls include intentionally infeasible configurations.

Selection: all nine vectors, in frozen checkpoint order, with no edge values
fixed. Next evaluate the initial21literal fixed-value pattern, then greedily
try dropping its values in increasing variable-ID order. Accept a deletion
only if the exact block bound remains strictly negative. A failed deletion
does not need retry after further deletions: relaxing additional fixed
values cannot decrease the exact maximum. The experiment does not claim a
globally shortest clause.

Limits:60seconds overall after manifest creation and100greedy attempts;
the current one-pass selection requires at most21attempts. Check the clock
between block optimizations and save completed results plus checkpoints.
Before the nine-vector run, exhaust small matching/b-factor fixtures and
reject corrupted primal, dual and dynamic-programming certificates. Use
only Python integers; no floating-point mathematical acceptance threshold.
The sole success threshold is an exact bound `<0`; zero is not sufficient.

Preserve every failed deletion's exact bound and witness. A negative
unrestricted-vector bound would only be a candidate exclusion of this one
780edge family; a retained pattern gives only a candidate conditional cut.
No positive target graph, general nonexistence, or independent review is
claimed by this producer.
