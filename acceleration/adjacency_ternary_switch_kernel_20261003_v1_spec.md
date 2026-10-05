# Source-only four-vertex adjacency switch kernel proposal

Author `/root/structural`; prepared 2026-10-03T13:34:14+00:00.
Source: `acceleration/adjacency_ternary_switch_kernel_20261003_v1.cpp`.
Status **SOURCE_ONLY / UNCOMPILED / UNEXECUTED**, with no approval, invocation,
test count, binary or computational performance claim. A complete new native
engine, parser, preparer, finite checker and saved-object checker are still
required. This file does not authorize any of them. No producer/checker code
is imported or copied; the common F3/E formulas and basic edge-toggle algebra
are disclosed shared mathematical components.

## Domain and outputs

The scientific domain is all symmetric binary 99-by-99 loopless matrices with
every row degree14. Generic fixture API accepts 4<=n<=99 and0<=k<=14<n.
Every matrix edge is mutable. The API imposes neither lambda1, triangle
linearity, triangle count231, incidence row degree7, root freeze nor symmetry.
It stores full integer C=A*A, including C_ii=k at regular proposal boundaries.
The old triangle producer's zero-diagonal CN convention is not used.

Metrics for unordered distinct pairs use r=C_ij+A_ij-2, canonical residue
(r mod3+3) mod3, F3=count(r not0 mod3), E_lambda=sum r^2 on edges,
E_mu=sum r^2 on nonedges, E=E_lambda+E_mu. The literal scalar is819820*F3+E.
It is signed64-bit; CN and adjacency arithmetic are bounded signed integers.
For this API domain CN<=14, |r|<=13, E<=4851*169=819819, making the scalar
equivalent to the lexicographic pair(F3,E). These generic-domain bounds are
loose exact bounds, not a target-neighborhood count or optimized theorem.

The Graph constructor receives a flat C++ integer array, validates its full
shape/binary/symmetry/diagonal/regularity and recomputes the entire product.
Serialized JSON bool/float equality is outside this pure C++ API. A future
wire parser must reject such values before integer conversion under its own
new typed controls; this source cannot approve that parser boundary.

`Role` has five integers(u,v,x,y,orientation). Validate range, orientation0/1,
canonical u<v, x<y, old edge pair lexicographically ordered, four distinct
endpoints, both old edges present, both new edges absent, in that order.
Orientation0 removesuv,xy and addsux,vy; orientation1 addsuy,vx (that is,
the unordered pairs{u,y},{v,x}). Each vertex loses and gains one edge.
All rejected roles remain observable with a specific diagnostic and unchanged
input graph/metrics. Invalid roles do not cause hidden resampling.

`Graph.apply` commits every valid switch regardless of score. A future search
driver must call it on a candidate copy, then independently decide whether
to retain that candidate. Internally apply also uses one transactional copy,
so failed local invariants never partially mutate the input. This deliberate
copy cost and the386-pair scan have unknown measured throughput. No RNG,
Metropolis acceptance, tabu rule, schedule, deadline, restart, wire/state
serialization, whole census or native main exists in this proposal.

`SwitchRecord` reports the original role, validity, diagnostic, affected pair
count, both complete metric tuples and exact F3/lambda/mu/E/scalar deltas.
Invalid records have affected count0 and equal metric tuples/deltas0.
Valid records have affected count4n-10, which is386 for n99. There is no
target approval bit or mathematical claim output.

## Exact cache mechanism

For a legal toggle(a,b,s), s=+1 add or-1 remove, and prior adjacency A,
T=e_a e_b^T+e_b e_a^T:

```
C' = C+s(AT+TA)+T^2.
C'_aw=C_aw+s*A_bw, C'_bw=C_bw+s*A_aw  (w outside{a,b}),
C'_ab=C_ab, C'_aa=C_aa+s, C'_bb=C_bb+s.
```

The diagonal rule uses the legal prior edge value. Toggle uv removal, xy
removal and the two additions sequentially; every step reads the CURRENT A.
Before any toggle, subtract every old metric contribution on pairs meeting
U={u,v,x,y} once; after all toggles, add every final contribution once. Pairs
disjoint from U have unchanged adjacency rows and unchanged common neighbors,
even if an unchanged common neighbor belongs to U. No score is taken at an
intermediate degree13/15 graph. Four final rows and true product diagonals
return to k. Category switches use final A, so edge/nonedge E changes are
included as well as the CN deltas. A full independent matrix rebuild is still
required to establish correctness of this source in finite controls.

## New applicable controls required before use

An independent path must construct final adjacency by whole matrix edge
replacement, independently multiply all n^2 products and compare all cache,
metric, classification and record entries; it must not import this source or
reuse its toggle/delta function. Generic rook/prism/cube and a literal99/14
fixture should cover degree preservation, shared-neighbor cancellation,
untouched pairs with a common neighbor in U, both orientations, edge/nonedge
category changes, true diagonal values, commit/copy/rejection and reverse
switch recovery. Explicit corruptions must cover each role diagnostic, shape,
nonbinary/symmetry/diagonal/degree, cached zeros/ones, altered CN and score,
scalar/histogram/record identity and any future literal typed wire fields.
Exact finite fixtures, counts, raw records, source hashes, success criteria,
deadline allocations and independently approved controls are not yet frozen.

Two literal source-only positive fixtures can begin that preparation. In the
row-major rook9 labeling0..8, old edges(0,1),(3,4), orientation1, add(0,4),(1,3)
which are nonedges; orientation0 is rejected because(0,3),(1,4) are edges.
For n99/k14, the engineering circulant with offsets plus/minus1..7 has old
edges(0,1),(20,21); both orientations are valid because every proposed new
edge has circular distance19,20 or21. This fixture is only a known domain/
switch control; its symmetry is not a restriction on the scientific domain.
No exact output metric or control success has been computed or asserted.

An eventual zero export must undergo a separate independent full99 validator
of binary/symmetric/zero diagonal/degree14 and every9801 integer entry of
A^2+A-12I-2J. This API does not substitute F3zero or its own cache for that
validation. No build/calibration/scientific command or chained invocation is
authorized by this proposal.
