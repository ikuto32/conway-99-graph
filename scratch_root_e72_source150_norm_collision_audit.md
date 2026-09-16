# E72 source150 norm/collision independent audit

Status: **SOURCE150_NORM_COLLISION_AUDIT_PASS**.

The corrected filter's complete input is independently recovered: 5,943 local-graph orbits, labelled mass 2,244,608, partitioned among 17 canonical macro orbits. All 21 action copies of the five exact Gram matrices satisfy the diagonal, overlap, twelve disjoint-block, PSD, and compression-row checks.

The replay uses ordered ordinary-fibre products and a staged exceptional-row DP, rather than importing the filter. It reproduces all 25 controls and all five global norm/collision DP instances exactly.

The ordinary--exceptional rule is one-sided: each exceptional vertex chooses one neighbour in a disjoint ordinary C4, while an ordinary vertex may receive 0 through 4 such neighbours. The twelve disjoint exceptional blocks retain their exact Gram totals but deliberately drop common 4x4-matrix compatibility. Both omissions enlarge the feasible set, so a rejection would be safe.

Result: all 5,943 orbits pass. Thus this corrected artifact makes no source150 exclusion; the full 2,244,608 mass remains open. This is an exact executable audit, not a proof-assistant certificate.
