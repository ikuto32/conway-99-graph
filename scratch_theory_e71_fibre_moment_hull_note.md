# Bounded E71 fibre moment hull experiment

Result: no new exclusions. All 71 raw-row-LP-passing profiles in the frozen
65-macro frontier admit exact rational fibre-moment-hull witnesses. The extra
source 724 Q2 control also passes. Intersecting the hull construction with the
recorded exact-label actual-position domains leaves 63 exact-feasible profiles;
the other eight were already excluded by the label-subset row LP. The
intersection adds zero exclusions.

## Necessary condition tested

Write the integer residual row as `R_x = 4 d_x - C_G`, where `x` belongs to
fibre `G` and `d_x` is its vector of degrees into the 21 fibres. The necessary
identities are

`sum_(x in G) R_x = 0`, and `sum_x R_x^T R_x = 4 K4`.

Raw rows are integral degree vectors in `[0,4]^21`, of total degree 12, in the
required residual row space, with the exact internal degree of their actual
corner. For each fibre, choose four such ordered rows whose residual sum is
zero. Its upper-triangular pivot moment vector is the sum of their four outer
products. An actual graph must select one attainable vector per fibre. We
relax this selection to a nonnegative convex combination within each fibre,
with total global moment `4 K4`.

This couples four rows and strengthens the independent-row relaxation in
principle. It does not require these rows to be mutually realizable adjacency
rows, does not couple the quartet choices of different fibres, and does not
produce a graph. Its failure to cut this frontier does not prove redundancy
on other profiles.

## Enumeration and caps

The implementation uses pair-sum joining: ordered corners `(0,1)` and `(2,3)`
are grouped by residual sum and moment; opposite sums are joined, and equal
total moments are deduplicated. Repetition is allowed whenever it satisfies
the row domains. Thus the construction does not silently impose distinctness
of residual rows. No adjacency, port, matching, or global quartet product is
enumerated.

The explicit limits were 200,000 pairs per side, 2,000,000 joined pair-moment
combinations per profile, 10,000 distinct moments per fibre, 30 seconds of
enumeration per profile, and 15 seconds for the primal LP. A limit hit would
yield `CAPPED_NO_EXCLUSION`. All 71 raw and 71 combined profile tests completed
without a cap. The raw scan used at most 1,833 joined combinations and 480 LP
variables per profile.

Source 2378 was the initial large-coverage control: its four surviving
profiles remain feasible both raw and with recorded label-position domains.
Their hull LPs have respectively 480, 480, 456 and 125 columns. The separate
source 724 Q2 control has 76 columns and is feasible.

## Exact positive audits and boundary

`scratch_theory_e71_fibre_moment_hull_audit.py` verifies 72 positive controls
without importing the hull producer or an LP solver. It independently
reconstructs compressed matrices and pivot coordinates through the existing
independent matrix audit. Every positively weighted quartet is lifted and
checked in all 21 coordinates: integral bounded degrees, total degree 12,
actual-corner internal degree, zero sum, stored moment, rational positive
weight, unit fibre mass, and full lifted Gram equality.

`scratch_theory_e71_fibre_moment_hull_label_subset_audit.py` additionally
checks every used ordered row against its frozen actual-position label
domain. It passes on all 63 combined positive profiles. It does not rerun
the 23-vertex subset enumerator. Its claim is feasibility and membership in
the RECORDED domains, not independent validation of the positive profiles'
local subset tables. The separate subset audit replayed only the six negative
macros, not the other 59 local models. The general local-cap necessity argument
is sound, but that does not independently validate every recorded table.
The eight inherited negative profiles are listed but their Farkas
certificates are not re-audited or credited here.

For positive controls, verifying the used quartet witnesses is sufficient;
the audits do not rely on completeness of unused hull options. Rational
feasibility of these relaxations is not an adjacency completion or existence
result.

The input inventory is bound to the byte-identical frozen
`scratch_root_e71_theory_frontier_before_label_subset.json` (SHA-256 prefix
`C277833D2A68`). Metadata was rebound after the parent froze the inventory;
no row domains, quartet options, LP coefficients or certificates changed.

No E71 complete local census, E72 restart, live-runner mutation, inventory
exclusion update, order-eight regeneration, or `submission.txt` write was
performed. This bounded lane is complete.
