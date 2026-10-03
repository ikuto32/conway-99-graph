# A connected subcubic ternary residual support must span all99 vertices

Producer: /root/checkpoint_audit.
Frozen source timestamp: 2026-10-03T05:01:36+00:00.
Status: CANDIDATE pending a separate written derivation by a different verifier.
This producer does not approve its own statement. No mathematical program,
graph fixture, exhaustive computation, ledger/index change or target resolution
is asserted.

## Exact proposed statement

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly14 ones
in each integer row, put M=(A^2+A-12I-2J) modulo3 and let H be its simple
nonzero unordered off-diagonal support, with isolated vertices discarded.
If H is nonempty, connected and has maximum degree at most3, then H has
exactly99 vertices. No support with99 vertices is asserted realizable.
Disconnected and higher-degree supports are outside this claim, and it does
not resolve target existence or nonexistence.

The prospective claim is distinct from the preserved at-most12 and lower45
results. It concerns the whole nonisolated residual support H; it neither
assumes connectivity of A nor prescribes H as an induced adjacency subgraph.
No lambda1, incidence, numerical, fixed-graph or automorphism premise is used.

## Exact prior dependency

The proposed uses_result dependency is
C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-LOWER45 r1.
Its exact independently checked ordinary binding is
`acceleration/results/20261003_independent_review/ternary_connected_subcubic_support_lower45_01/claim_binding_schema2.json`,
SHA256 44cf238643a09335d5af17be9161baf7f18afb4d1b6f60d61c4936cdbd685455.
Its written proof is
`acceleration/audit_20261003_ternary_connected_subcubic_support_lower45_v1.md`,
SHA256 b51cf3d17586cad49a97ef7c369c4944964e2462c7c60e5ff15f9957b110a065.
Its report is
`acceleration/results/20261003_independent_review/ternary_connected_subcubic_support_lower45_01/summary.json`,
SHA256 baa69ead3f4a65902e9ef0d864a151e82017da0707a82337de359cdc7e846789.

Only the stated necessary size bounds m>=45, and m>=47 for the nonbipartite
case, are used from that prior theorem. Binary propagation is reproduced
below, rather than treated as an extra unstated claim in the prior headline.
The prior discovery producer was ROOT and its verifier was this Checkpoint;
the new proposed discovery producer is Checkpoint, requiring a different
verifier. The earlier verification does not approve this extension.

## Proposed exact derivation

Write D=A^2+A-12I-2J over the integers. Symmetric binary degree14 gives
(A^2)_uu=14 and D_uu=0. Each complete residual row sums to
(196-14)+14-2*98=0. Exact regularity and symmetry give AJ=JA=14J;
expanding both products proves AD=DA, hence AM=MA over GF(3).

Let S=V(H), of size m. Each support row is zero modulo3. Nonisolated degree
is at least2. Under the subcubic premise, each degree is2 or3; degree2 has
opposite edge labels and degree3 has equal edge labels.

For each z outside S, its entire M-row is zero. Its binary adjacency vector
x=(A_zu:u in S) satisfies x*M[S,S]=0. A degree2 column makes its two neighbor
coordinates equal modulo3 and hence equal as binary integers. A degree3
column makes their three-coordinate binary sum divisible by3, so it is0 or3
and all three coordinates agree. Thus x is constant along every even walk
in H. In a connected bipartite H the equality classes are the two parts;
in a connected nonbipartite H every pair can be joined by an even walk, by
prefixing an odd closed walk when necessary, so the class is all of S.

First suppose H is bipartite. Let its larger and smaller parts have sizes p
and q. The prior theorem gives m=p+q>=45. In H, minimum degree2 on the larger
part and maximum degree3 on the smaller part count the same edges, giving

 2p <= |E(H)| <= 3q.

Therefore 2m=2p+2q<=5q, so q>=2m/5>=18. The larger part also has at least18
vertices. For any outside vertex z, its adjacency coordinate is binary and
constant separately on each part. If it were1 on either part, z would have
at least18 neighbors, contradicting degree14. It is therefore0 on both parts.

If H is not bipartite, the prior theorem gives m>=47. The outside vector is
constant on all m support vertices. A coordinate1 would give z at least47
neighbors, again contradicting degree14. Thus every coordinate is0.

In either case, this proves A_zu=0 for EVERY outside z and EVERY u in S.
By symmetry the full A block between S and its complement is zero. If the
complement were nonempty, choose u in S and z outside it. They are nonadjacent.
They have no common neighbor: a common neighbor in S would require an edge
from z into S, while one outside S would require an edge from u out of S.
Both are forbidden by the full zero block. Consequently

 D_uz=(A^2)_uz+A_uz-2=0+0-2=-2,

which is nonzero modulo3. This says uz is a support edge and contradicts
z being outside the complete nonisolated support. Hence its complement is
empty and m=99.

## Required independent falsification boundaries

The separate verifier should reproduce the exact prior binding and the
appropriate45/47 bounds. Challenge both binary column equations, even-walk
propagation, and the use of the whole support rather than one component.
Verify 2p<=|E(H)|<=3q with the correct larger/smaller sides, including uneven
bipartitions, and that q>=18 is a literal bound exceeding14.

Check that outside degree14 forces zero coordinates on BOTH bipartition
classes; equality of coordinates alone does not imply a zero block. The
quantifier must cover every outside vertex, so the subsequent common-neighbor
argument forbids both possible locations of its third vertex. Finally verify
-2 is nonzero modulo3 and therefore contradicts the definition of S.

Do not apply the degree3 binary inference at support degree4. Do not assume
connectedness of A, an automorphism, uniform internal adjacency or an already
verified full99graph. The m=99 boundary leaves no outside vertex to select;
the proposed result explicitly permits this unclassified case. The empty
support boundary is also outside the nonempty premise.

All these are proposed written checks, not executed fixtures. This source
records no independent verification verdict, binding, formal proof, graph
realization, novelty, external review or engine/search approval. Overall search
coverage: UNKNOWN; no validated denominator.
