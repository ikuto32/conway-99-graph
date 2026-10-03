# Six ternary defects cannot occur in the complete degree14 domain

Producer: /root. Frozen version timestamp 2026-10-03T04:39:57+00:00.
Status: CANDIDATE pending separate written verification. No computation,
graph fixture, exhaustive program or target resolution is asserted.

## Precise statement

For every symmetric binary zero-diagonal 99-by-99 matrix A with exactly14
ones in each integer row, put r_uv=(A^2)_uv+A_uv-2 for u<v, and let F3
count all unordered residuals not divisible by3. Then F3 is not6.
This statement alone does not exclude any other positive value or establish
the existence or nonexistence of the target. No lambda1, triangle incidence,
automorphism, fixed graph or numerical premise is used.

## General identities and support rules

Let D=A^2-12I+A-2J over the integers and M=D modulo3. Its diagonal is0
and each complete row sums to196-12+14-198=0. Exact symmetry/regularity gives
AJ=JA=14J, hence AD=DA and AM=MA. Every distinct-pair residual is at least-2.
When M_uv=0 it is a multiple of3 at least-2, so r_uv>=0.

The support H consists of the unordered nonzero entries of M. Each nonisolated
vertex has degree at least2. At support degree2 the incident residues are
opposite; at degree3 all three are equal. An odd support cycle whose vertices
all have degree2 is impossible. These facts are derived directly from complete
row sums over GF(3), and do not require a prior ledger label.

For S the nonisolated support vertices and z outside S, the z-row of M vanishes.
Commutation therefore gives the row equation

 (A_z,S)*M_S,S=0 over GF(3).

Whenever this forces two binary coordinates A_zu,A_zv to agree modulo3, they
agree as integers. If it forces this for every z outside S, vertices u,v
have the same outside neighborhoods. Each has at least14-(|S|-1)=15-|S|
outside neighbors, all common. Thus r_uv>=13-|S|. These are bounds on the
complete graph; the support H does not prescribe any induced adjacency in A.

## Complete six-edge support classification

Suppose H has exactly6 edges and v nonisolated vertices. Minimum degree2 gives
v<=6, while simplicity gives v>=4. If disconnected, each nontrivial component
uses at least3 edges. The only six-edge disconnected possibility is two
triangles, forbidden by degree2 alternation. Thus H is connected.

If v=6, all degrees are2, so H is C6. If v=4, H is K4.
For v=5, the degree sum12 and minimum degree2 leave either degrees4,2,2,2,2
or degrees3,3,2,2,2. In the first case the degree4 vertex meets every other
vertex, and the two remaining edges must be a matching on those four vertices.
This is two triangles sharing a center (the bowtie).

In the second case suppress the three degree2 vertices into paths. With two
degree3 endpoints, the connected resulting multigraph is either three paths
between the endpoints (a theta), or one joining path and a cycle at each endpoint.
The latter requires two simple cycles of length at least3, hence at least four
degree2 vertices, and is impossible here. The theta's three path lengths sum6;
simplicity allows at most one length1. The possibilities are (1,2,3) or (2,2,2).
Equal endpoint residues at degree3 and alternation at degree2 require all three
paths to have the same parity: the residue at the other endpoint is multiplied
by (-1)^(length-1). Thus (1,2,3) is impossible, while (2,2,2) is K2,3.

The only support shapes still possible are therefore C6, K2,3, the bowtie,
and K4. The following contradictions cover every nonzero sign choice.

## Four adjacency-realization contradictions

For C6 label the cyclic vertices1,...,6. Degree2 makes edge signs alternate.
The outside equation at each column j equates the adjacency coordinates at
its two cyclic neighbors. Consequently all three odd vertices have identical
outside neighborhoods, and so do all three even vertices. Choose vertices1,3.
They are not a support pair, |S|=6, and r_13>=7. Divisibility by3 strengthens
this to r_13>=9. Row1 has only two bad residuals, each at least-2; every other
good residual is nonnegative. Its sum is at least9-4=5, contradicting0.

For K2,3 let a,b be the two degree3 vertices and x,y,w the three degree2
vertices. Every edge at a has residue s, and every edge at b has residue -s,
for nonzero s. The outside equation at column x forces A_za=A_zb for every
outside z. Since |S|=5, their common outside neighborhood has at least10
vertices. The pair ab is not in the support, so r_ab>=8 and divisibility by3
gives r_ab>=9. Row a has only three bad entries, whose sum is at least-6.
Its complete row sum is at least9-6=3, contradicting0.

For the bowtie write its triangles c,x,y and c,u,v. In the first triangle
the residues on cx,cy are s and on xy are -s. In the second they are t,t,-t.
The center row requires2s+2t=0, so t=-s. The outside equations at the four
leaf columns force A_zc=A_zx=A_zy=A_zu=A_zv for every outside z.
Choose x,u from different triangles. This pair is not in the support and
|S|=5 gives r_xu>=8, hence r_xu>=9. Row x has only two bad residuals.
Its complete row sum is at least9-4=5, contradicting0.

For K4 the degree3 rule and symmetry force every edge residue to be the same
nonzero s. Thus M_S,S=s*(J4-I4). An outside row of four binary entries solves
x*(J4-I4)=0 over GF(3), so every entry equals the sum of those four entries;
all four entries agree. Every support vertex therefore has the same outside
neighborhood, of size at least11. Every one of its three support-pair residuals
is at least11-2=9. All other off-diagonal residuals in its row are good and
nonnegative. The integer row sum is at least27, contradicting0.

Every possible six-edge support is contradicted. Hence F3 cannot be6.

## Falsification and scope boundaries

The independent reviewer should reconstruct the complete six-edge shape
classification, including disconnected supports, the suppressed-path argument,
and theta parity. Challenge all four outside-kernel calculations and their
conversion from field equalities to binary integer equalities. Check internal
neighbor upper bounds without prescribing any adjacency inside S, exact
residual lower bounds, good-pair divisibility and complete-row budgets.

Alternating C6, signed K2,3 and bowtie, and all-equal K4 are legitimate modular
zero-row-sum support matrices. Their adjacency realization fails by the extra
commutation and degree argument; their modular validity is not refuted.
Written support controls are not graph fixtures. No executable controls ran.

The statement uses no prior mathematical claim as a premise; elementary row
identities and support rules are reproduced here. The separately audited
small-support paper d887daf8 and the separate four-defect candidate08845d97
provide context only. Combining independently established exclusions would
still be a lower bound on nonzero defects, not a target-level proof.
External review, novelty, realization of any remaining defect count, and any
bound beyond this exact statement remain unestablished.
Overall search coverage: UNKNOWN; no validated denominator.
