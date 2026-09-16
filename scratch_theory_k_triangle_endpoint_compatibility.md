# Local endpoint compatibility around a triangle of K

Assume `T=sum_r E0(r)=0`, so the triangle relation `K` is 36-regular on
231 triangles, and each of its edges has one endpoint label at each end.
At every triangle the three label classes have size 12. This bounded study
establishes exactly what the separate order-eight wedge counts and one row
of the projector equation constrain. It does not exclude `T=0`.

## Fixed wedges and the order-eight diagonal lift

Each triangle has `3*C(12,2)=198` same-label wedges and 432 different-label
wedges. Globally these totals are 45,738 and 99,792. Reading the existing
916 frozen masks, with no regenerated classes, gives exactly three classes
whose outer triangles overlap in one vertex:

| Frozen degree-cell mask | Same-label roles | Different-label roles | Frozen T=0 count |
|---|---:|---:|---:|
| 57358896 | 1 | 0 | 0 |
| 44481136 | 0 | 1 | 2442 |
| 57905480 | 0 | 1 | 8316 |

The sole same-label role has its shared outer point unmatched in both
outer triangles. Consequently it is precisely one entry `Y[r,beta]=2`.
Conversely every such entry determines these three triangles and their
eight-vertex union. The root-flag identity `D(r)=sum_beta binom(Y[r,beta],2)`
therefore gives the universal identity

```text
x8[57358896] = sum_r D(r) = n3-z11/4.
```

It is the unique triangle-mate extension of the seven-vertex `H_delta`
motif, rather than a new independent moment. In particular every same-label
wedge at `T=0` has pairwise-disjoint graph triangles. For the frozen
pseudocount, 10,758 different-label wedges have overlapping outer triangles
and 89,034 have pairwise-disjoint triangles. These latter numerical values
refer to that pseudocount, not to every putative endpoint graph.

## Closing the wedges

Let `c(Delta)` be the number of equal-label corners of a `K` triangle.
Three equal-label corners would lift to an `X` triangle, hence an alternate
triangular prism. Thus `c(Delta)<=2` and, if `C_same` counts closed
same-label wedges,

```text
C_same = sum_Delta c(Delta) <= 2*tau_K.
```

The 45,738 count includes open wedges; it cannot be substituted for
`C_same`. Their closure involves three disjoint triangles, or nine vertices.

A targeted check considers only three specified triangles with every pair
in `K`. There are exactly `18^3=5832` labelled matching assignments. This
is not an ambient order-nine census. Among assignments satisfying every
local adjacent/nonadjacent common-neighbour upper cap, the prism-free
counts for `c=0,1,2` are respectively `1080,1296,648`; all 108 admissible
assignments with `c=3` contain a prism. Explicit nine-vertex controls for
each of `c=0,1,2` are saved. The tested local conditions cannot strengthen
the corner bound to `c<=1` or force a compatible triangle.

## What one projector row permits

Write the positive and negative shells of a triangle `T` as `P(T)` and
`K(T)`. On a `K` edge `TU`, the equation `M^2=21M` reduces to

```text
a-b-c+d = -13,
```

where `a,b` count the positive/negative relations from `U` into `P(T)`,
and `c,d` count them into `K(T)\{U}`. Here `d` is the number of `K`
triangles on the edge.

An explicit 231-point signed relation in the JSON has all 231 exact row
profiles `4,+1^32,0^162,-1^36`, all row sums zero, and the complete centre
row of `M^2=21M`. Nevertheless its 36 negative neighbours have no negative
edges among them. Assigning them three groups of 12 gives `d=0` on every
edge at the centre and no compatible triangle there.

This control fails 25,056 non-centre upper-triangle entries of the full
projector equation. It has endpoint colours only at the centre. It proves
only that the complete row profiles plus one full projector row cannot
force the desired closure. It makes no assertion about all projector rows
or the simultaneous endpoint partitions, and is not a 99-vertex graph.

The initial unexecuted construction used an infeasible consecutive-vertex
two-factor completion. It was replaced with an exact bipartite degree
realization for the zero-shell negative relation. The independent audit
reads the emitted edges and checks the matrix directly; it neither imports
the producer nor reruns its construction algorithm.

## Reproduction and boundary

```text
python scratch_theory_k_triangle_endpoint_compatibility.py
python scratch_theory_k_triangle_endpoint_compatibility_audit.py
```

Audit status: `INDEPENDENT_K_TRIANGLE_ENDPOINT_COMPATIBILITY_AUDIT_PASS`.
It recounts all 916 frozen masks, all 5,832 targeted assignments, all 231
row profiles, and all 26,796 upper-triangle projector entries. The next
unresolved condition is simultaneous cross-centre projector/endpoint
compatibility. No positive lower bound on `E0`, endpoint exclusion, or
`submission.txt` is produced by this lane.
