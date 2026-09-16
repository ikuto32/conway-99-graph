# Bounded single-row root-label quota probe

This probe strengthens the allowed-neighbour-subset model by requiring all
14 root-neighbour quotas of a **single** outer vertex simultaneously. It
does not coordinate two outer vertices or enumerate any graph completion.

For root-neighbour label `a` and outer vertex `x`, the necessary number of
outer neighbours of `x` carrying `a` is one when `a` or its matching mate
belongs to the two-label support of `x`, and two otherwise. Summing the two
labels of a root-neighbour pair gives coarse quotas two on the two source
groups and four on the other five groups.

The already reconstructed raw rows obey those coarse quotas. Therefore it
suffices to track the first label of each pair. Its quota vector has two
entries one and five entries two, so a direct dynamic program has at most
`2^2*3^5=972` states.

The own-fibre neighbour subset is fixed. On every ordinary target fibre,
the raw degree is zero or one. When it is one, all four singleton choices
are allowed; their two signs form a Cartesian product. Such fibres supply
independent interval slack `0,...,free_g` in each group. Process only the
exceptional target subsets of the specified degree, keeping partial first-
label counts below the quota. A final state is acceptable when each count
lies between `max(0,quota_g-free_g)` and `quota_g`. The coarse quota then
ensures the other label is also correct.

An independent theoretical review confirmed these quota and independence
steps. The discovery run checks all 71 pre-subset frontier profiles in
about 35 seconds; it visits at most 243 states in any row. Only three
position rows are removed, belonging to `(1219,7,0)`, `(1219,10,0)`, and
`(1289,2,0)`. All three macros were already excluded by the independently
audited subset-only certificates. The resulting moment model has exactly
the same eight profile cuts: **no additional macro exclusion**.

The discovery script and data are
`scratch_theory_e71_row_label_quota_moment_probe.py` and
`scratch_theory_e71_row_label_quota_moment_frontier.json`. The retained-row
decisions and floating feasible LP statuses have not been independently
audited, and no inventory credit depends on them. A bounded independent
check of the three discarded rows now passes:
`scratch_theory_e71_row_label_quota_removed_audit.py/.json/.md`.
In each case two different target fibres force a neighbour carrying the
same label already adjacent to the source vertex, producing two common
neighbours where `lambda=1` permits only one. The checker reconstructs
96 selected subset cases and proves this directly, without a DP or solver.
The other 20,759 retained-row decisions are outside its scope. This probe
is stopped at this recorded boundary; it gives no positive `E0` lower bound.
