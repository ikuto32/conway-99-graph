# Coarse60 bidirectional arc-consistency scout

This protocol is frozen before execution. The finite input is the already
independently checked 18-domain model, with 136 choices per domain, all 135
binary Gram compatibility relations, and the explicit condition that all six
raw bits of column zero equal zero. Applying this condition is meaningful even
before the separate relabelling-equivalence candidate is approved: this scout
then has only the declared six-bit-fixed scope.

Start with all 136 choices except the six domains containing column zero, whose
68 bit-one choices are removed by the fixed bits. Reconstruct every forward
relation from the raw 60-bit masks and exact target intersections, compare it
to the saved model, and form its transpose. Run deterministic AC-3 on all 270
directed arcs, initially lexicographically ordered. Revise source choices in
increasing index order; after a change enqueue all arcs from other neighbors
into that source, excluding the neighbor just used. Do not stop merely on the
first empty domain: continue to the finite fixed point so records are uniform.

For every removed value record its domain/index/selector, neighbor, complete
support bit mask, neighbor's current mask, and their empty intersection. Save
all initial masks, six-bit removals, final masks, queue accounting and the exact
fixed-point check. A domain becoming empty gives a candidate finite obstruction
for this input only, subject to independent replay. Nonempty domains establish
no global assignment, factor, graph or target progress percentage. The Y caps
are not used in this pair-relation-only propagation.

Calibrate a known satisfiable tiny equality CSP with forced propagation, a tiny
empty-domain contradiction, and an arc-consistent but globally impossible
two-color triangle. Enumerate their complete tiny solution sets to distinguish
local consistency from global feasibility. Corrupt proof traces must be rejected
by a separate producer-side replay routine; this is calibration, not independent
research verification. Bound wall time by 120 seconds; no SAT solver, RNG or CNF
mutation. Save source commit, command, versions, hashes and failed controls.

No reverse-support CNF extension is built in this scout. Its preparation remains
gated on independent review of these exact records.
