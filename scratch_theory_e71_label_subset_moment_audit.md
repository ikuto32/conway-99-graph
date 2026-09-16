# Independent audit of exact-label subset moment exclusions

Status: `INDEPENDENT_E71_LABEL_SUBSET_MOMENT_AUDIT_PASS`.

Eight independently checked Farkas certificates exclude these six complete
frozen E0=71 macros:

| Macro key | Full-Gram parameters | Labelled coverage |
|---|---|---:|
| (897,0,0) | t=-1, t=0 | 65,536 |
| (897,1,0) | t=-1, t=0 | 131,072 |
| (1219,7,0) | unique | 16,384 |
| (1219,10,0) | unique | 16,384 |
| (1289,2,0) | unique | 65,536 |
| (1408,0,0) | unique | 65,536 |

Their total coverage is 360,448. The audit checks the complete selected
manifest of 65 macros and 71 profiles, but independently reconstructs local
models only for these six newly certified macros. The remaining 59 local
models and their LP statuses are explicitly outside this audit's scope.

## Independent partial-graph check

For each certified macro, source fibre, target fibre, exact source vertex,
and one of sixteen target subsets, the audit reconstructs the fixed
root/first-neighbour/source/target graph as sets. It tests common-neighbour
counts by an explicit update identity. If `x` is the chosen source vertex
and `T` its new target neighbours, then

```text
common_new(x,v) = common_old(x,v)+|T intersect N_old(v)|,
common_new(a,b) = common_old(a,b)
 + [a,b both in N_old(x) union T] - [a,b both in N_old(x)]
                                              when a,b are different from x.
```

Known present pairs use cap1. Every other pair uses cap2, a necessary upper
bound whether an unassigned pair eventually becomes an edge or a nonedge.
This method does not import or reproduce the producer's trial-bitset
adjacency implementation. All 161,280 single-row subset tests agree with
the stored domains. Both internal fibre states and root-label incidences
are reconstructed independently from the frozen catalogue.

The soundness of this relaxation is reviewed in
`scratch_theory_e71_label_subset_review.md`. Unknown edges contribute zero
only to a common-neighbour **lower bound**; they are not declared absent.

## Moment and certificate check

Complete raw degree-row domains are rebuilt using the principal-inverse
routines of the standalone independent degree-moment audit. The dependency
is named and hashed in the result. No research producer or base helper is
imported, and no LP solver runs.

For each of the 84 exact-label positions, the audit intersects its raw row
domain with the independently derived allowed target degrees and its fixed
internal degree. It then rebuilds the model with:

- one unit-count equation per exact position;
- zero first moment in each support fibre;
- global second moment `R^T R=4K4` in principal coordinates.

Every position domain, variable, coefficient matrix and model hash agrees.
Each integer multiplier satisfies `A^T y>=0` column by column and
`b^T y<0`. These exact inequalities, not the floating LP status, certify
infeasibility.

For every credited macro, the audit reads the complete full-Gram profile
list directly from the frozen mining catalogue and requires an independently
verified certificate for every profile. Thus neither t=-1 nor t=0 may be
omitted for either source897 macro.

The input remaining-macro manifest is the frozen snapshot
`scratch_root_e71_theory_frontier_before_label_subset.json`, with SHA256
`C277833D2A68FE26D1C66C416CCE3A6A7B50631CFBEB9AB1B2AE11D6055A5336`.
Using this immutable input avoids a circular dependency when the live
inventory subsequently incorporates the new exclusions.

## Reproduction

```text
python scratch_theory_e71_label_subset_moment_audit.py
```

The machine-readable output is
`scratch_theory_e71_label_subset_moment_audit.json`. This is a finite
single-row necessary-condition calculation, not an overlap matching or
graph-completion enumeration. No complete E0=71 exclusion, pointwise E0
lower bound, or graph construction is claimed.
