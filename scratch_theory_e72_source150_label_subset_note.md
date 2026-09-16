# Six frozen E72 source150 label-subset / row-quota controls

Result: no new exclusions. On each of the six frozen source150 profiles,
all 132 raw internal-degree-compatible actual-position residual rows survive
both the 23-vertex label-subset filter and the single-row root-label quota
filter. Both resulting moment LPs have independently checked exact rational
feasible witnesses.

The keys are `(150,0,3)`, `(150,1,0)`, `(150,3,3)`, `(150,9,0)`,
`(150,10,0)`, `(150,11,0)`, each with its unique full compressed Gram profile.
Their total labelled coverage is 40,960 and each residual Gram rank is two.
The scope comes from the frozen prior applicability JSON, not a new read of
mutable runner status or an assertion about which branches are currently open.
The applicability artifact is now bound to the byte-identical historical
`scratch_root_e72_complete_coverage_inventory_before_m10.json` snapshot
(SHA-256 prefix `651115B9B944`). This preserves all six controls when m(1,0)
is removed from the central open inventory. No numerical model, row domain,
quota decision or rational witness changed in that metadata migration.

## Conditions and bounded computation

The subset test fixes the root, its 14 neighbours, two known four-vertex
fibres and just one adjacency row between those fibres. It checks all 16
possible target subsets against the known common-neighbour upper bounds.
Other inter-fibre edges remain unspecified. This is a necessary local
relaxation, not an inter-fibre completion search.

The optional quota test couples one vertex's choices of target subsets across
the 21 fibres. For either label in a root-neighbour pair, the required number
of neighbours among these fibres is one for a pair in the source support and
two otherwise. The coarse group totals fix the sum of the two label counts;
the seven even-label counts therefore suffice. Each such coordinate has at
most two or three possible values, giving a bound of `2^2 * 3^5 = 972` states.
The observed maximum was 243 states.

Each cone has one unit-mass constraint per actual position, zero residual
first moment per fibre, and global second moment `4 K4`. At rank two this is
129 equations. Six subset LPs and six quota LPs were solved, with a 15-second
primal LP limit per call; the complete producer run took under five seconds.
No rows were removed on this six-profile scope, so these filters do not
strengthen the raw actual-position degree-moment cone here. This observation
does not assert redundancy on arbitrary E72 profiles or fixed overlap branches.

## Independent audit

The audit imports no research producer and invokes no solver. It uses the
existing independent matrix reconstruction and the independent local
common-neighbour delta formula, replaying all six local subset tables:
161,280 partial 23-vertex row choices. It independently reconstructs all
raw and filtered actual-position domains and all LP coefficients.

For quota replay it uses direct seven-coordinate convolution over all 21
target fibres, including ordinary fibres; it does not use the producer's
exceptional-fibre / ordinary-free-slack split. All 792 retained-row decisions
are checked. All 12 positive witnesses have nonnegative rational weights
satisfying every model equation, and the pivot moment identity is lifted to
the full 21-coordinate Gram matrix.

Unlike the preceding E71 hull-positive audit's membership-in-recorded-domain
scope, every local subset table used by these six E72 controls has been
independently replayed. These exact positive witnesses still certify only
feasibility of the specified convex macro-level relaxations. They are not
graphs and do not certify any fixed overlap branch feasible.

Files: `scratch_theory_e72_source150_label_subset_probe.py/.json` and
`scratch_theory_e72_source150_label_subset_audit.py/.json`.

No CSP worker, overlap completion, E72 restart, inventory mutation, graph
completion or `submission.txt` write occurred. This bounded lane is complete.
