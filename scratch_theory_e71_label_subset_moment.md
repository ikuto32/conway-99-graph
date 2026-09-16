# Exact-label subset support strengthens the degree-moment inequality

The audited addition excludes six frozen E71 macros, coverage 360,448,
without overlap or graph-completion enumeration. Together with the earlier
degree-moment and source724 cuts, the original 132-macro test frontier now
has 59 remaining macros, coverage 26,017,792. This is not an exclusion of
the entire E71 layer and gives no universal positive `E0` lower bound.

## One assigned adjacency row on 23 vertices

Fix source fibre `S`, target fibre `F != S`, and a vertex `x in S`.
The 23 known vertices are the root, its 14 neighbours, and the two
four-vertex fibres. Root incidences and both internal fibre states are
fixed. For each of the 16 subsets `T` of `F`, assign `N(x) intersect F=T`.
No other cross edge between the fibres is assigned.

Count common neighbours using just known edges. These counts are lower
bounds for any eventual graph completion. A known edge has cap one. Every
other pair may safely use cap two, even an unassigned pair that might
eventually become an edge, since its true cap would then be smaller.
Rejecting a row whose lower count exceeds its cap is therefore sound.

This simultaneously uses constraints at the source vertex, target
vertices, their known internal neighbours, and all root-neighbour labels.
The independent implementation updates common counts by set intersections
and an explicit delta formula; it does not reuse the producer's trial
adjacency bitsets.

At each of the 84 exact-label positions, intersect the raw residual degree
rows with the allowed degree into each target fibre and the fixed internal
degree. Preserve a separate unit-count equation for each position. The
remaining moment equations are unchanged:

```text
sum_(x in fibre G) R_x = 0,        sum_x R_x^T R_x = 4K4.
```

Each new certificate is an integer `y` with `A^T y>=0` and `b^T y<0`, now
on these position-specific domains. The certificate is still a sum of
pointwise quadratic inequalities, not a solver-status claim.

## Exact audited scope

The six new keys are `(897,0,0)`, `(897,1,0)`, `(1219,7,0)`,
`(1219,10,0)`, `(1289,2,0)`, and `(1408,0,0)`. Both full-Gram parameters
are covered for each source897 macro. The independent audit reconstructs
all 161,280 single-row subset tests for these six macros, every raw degree
domain needed by their eight profiles, and all eight integer certificates.

The full discovery run reads a frozen 65-macro / 71-profile frontier.
It takes about 61 seconds. The audit takes about eight seconds and checks
the entire input manifest, but makes no independent assertion about the
other 59 local subset models or their floating feasible statuses.

The frozen input file
`scratch_root_e71_theory_frontier_before_label_subset.json` preserves the
exact pre-subset inventory bytes. Discovery input paths were rebound to
that file before final audits; no model, domain, or coefficient changed.
This prevents the live inventory's new exclusions from creating a
circular proof dependency.

Files:

- `scratch_theory_e71_label_subset_moment_probe.py`
- `scratch_theory_e71_label_subset_moment_frontier.json`
- `scratch_theory_e71_label_subset_moment_audit.py/.json/.md`
- `scratch_theory_e71_label_subset_review.md`

No 916-class regeneration, lower-layer enumeration, or `submission.txt`
creation occurs in this lane.
