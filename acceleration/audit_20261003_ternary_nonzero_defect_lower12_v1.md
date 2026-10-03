# Independent exact review: nonzero residual support has at least 12 edges

Producer `/root/structural`; verifier `/root`. Exact candidate:
`docs/CANDIDATE_20261003_TERNARY_NONZERO_DEFECT_LOWER12_V1.md`, SHA256
`8af2f38aeb004b5d485b8596f10d04caf1d3bb061d03885031641a9b8ebcdd25`.
Source-context `63437c9b9fc2dd58b3bdfb51fc347b880b397503` is historical,
not a claim that the new files occur there. Actual review timestamp is
in the separate report. I read and rederived the whole candidate from
the adjacency axioms. No computational fixtures, enumeration, formal
proof, external review, graph realization or novelty check was executed.

The exact statement accepted is: for every symmetric binary integer
99-by-99 A of zero diagonal and row degree 14, the number F3 of nonzero
unordered off-diagonal entries of M=A^2+A+J over GF(3) is zero or at least
12. This is a necessary condition and allows the target M=0. It gives
neither general nonexistence nor a positive target graph.

## Independently deriving the common filter

Integer R=A^2+A-12I-2J has diagonal zero and row sum
196+14-12-198=0. Off-diagonal entries are CN+A_uv-2>=-2.
Residue-zero entries are consequently nonnegative multiples of three;
the minima at residues 1 and 2 are -2 and -1. The row's allowance
beta=2c1+c2 is zero mod3 because c1+2c2 is zero mod3. Hence
beta<=3 floor(2 deg_H/3). Isolating a paired entry gives maximum
beta, beta-2 or beta-1 at residues 0,1,2, from each endpoint.

For the entire nonisolated support S with m=|S|, equal outside binary
neighborhoods give internal degree d=14-t and common neighbors at least
14-d+max(0,2d-m)>=14-floor(m/2). At m<=11 this yields paired residual
at least seven, or at least nine for a good pair after residue rounding.
Support degree at most four has beta<=6, or remaining bad-pair allowance
at most five. Thus each endpoint of such an equal pair has degree at
least five. I independently checked both parity choices of m in the
intersection minimum; no off-by-one strengthens the bound incorrectly.

AM=MA follows from regularity and symmetry. Since all residual rows
outside the whole S vanish, X M_S=0 for binary X=A[outside,S]. A support
degree-two row has opposite labels, so its two neighbors' outside
coordinates agree. A degree-three row has equal labels, so its three
binary coordinates are all equal. Consequently those two or three
neighbors each have support degree at least five when m<=11. Degree
one is impossible by the nonzero signed row sum.

This is the material filter already recorded as revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`,
report `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The present review repeats its derivation and uses that pinned result;
it does not use any prior exclusion of a particular defect count.

## Exhausting the range 1 through 11

Assume 1<=e<=11. Minimum support degree two gives m<=e<=11 and total
degree at most 22. A degree-three vertex requires three degree-at-least-
five neighbors, totaling at least 2m+10. Thus m<=6, while simplicity of
a degree-five neighbor requires m>=6. Equality at m=6 forces three
universal vertices of degree five, the distinguished degree-three
vertex and two degree-two vertices. The latter would meet all three
universal vertices. This is impossible. Thus no degree three occurs.

If there is a degree-two vertex, its two high neighbors give total at
least 2m+6. Simplicity and the degree limit force 6<=m<=8.

At m=8, the exact upper limit forces degrees 5,5,2,2,2,2,2,2. The
six low vertices must each meet both highs, forcing their degrees at
least six. This excludes m=8.

At m=7, the base total is 20. A third degree-at-least-five vertex costs
three excess units and cannot occur. There is at most one degree-four
vertex among the other five, since degree three is forbidden. If one
exists, the other four are degree two and each already saturated by
the only two highs. The degree-four vertex has at most its two high
neighbors. This excludes that alternative. Thus all five lows meet
both highs, giving K2,5 with or without the high-high edge. The latter
edge raises both degrees to six, and is included in the classification.

At m=6, the two degree-five vertices are universal. A third degree-five
vertex would force every other vertex to have degree at least three,
hence at least four, contradicting total<=22. The four lows therefore
have degree two or four. The base total is 18, so at most two can have
degree four. Such a medium vertex can meet the two highs and at most
one other medium vertex; low-degree-two vertices are already saturated.
It cannot achieve degree four. All lows are thus degree two and the
support is K2,4 plus the high-high edge.

If there is no degree two, absence of degree three gives minimum degree
four. Total<=22 implies m<=5 while simplicity forces m>=5. Thus m=5,
all degrees four and the support K5. Orders below five cannot meet the
requirements of either alternative. This proves the candidate's four
literal shapes cover the entire range without connectivity, catalogue
or automorphism assumptions.

## Eliminating the four shapes

In K2,r plus a high-high edge, every low signed row has opposite
high-incidence labels. Summing the two high field rows cancels all
low incidences and leaves twice the nonzero high-high label, impossible
in GF(3). This covers both r=4 and r=5 without an adjacency assumption.

In K2,5 without that edge, the first high's count c of residue-one
labels satisfies 10-c=0 mod3, so c=1 or 4. The endpoint budgets are
6 and 9. Their outside neighborhoods agree; m=7 gives CN>=11 and
good R_ab>=9, contradicting the smaller budget six. The signed field
rows can be feasible; it is their exact integer lift that fails.

In K5, each signed row has two labels of each kind. Label-one edges
form a simple 2-regular five-vertex graph, necessarily C5. The opposite
edges form its complementary C5. Independently multiplying the signed
matrix gives diagonal four and off-diagonal -1 for both cyclic distances:
the products are (-1,+1,-1) and (+1,-1,-1). Therefore B^2=5I-J over
the integers and 2I-J in GF(3). Bx=0 forces 2x=Jx, so its kernel is
exactly the constant line (B1=0). All binary outside words are zero
or all one, making all support vertices' outside neighborhoods equal.
Their degree four contradicts the filter. All four shapes are excluded.

## Independent falsification boundaries

1. Empty support is permitted; the proof never requires a defect.
2. The strict filter holds through m=11 and is not extended to m=12.
3. The degree-three m=6 total is exactly 22; no spare unit allows a
   nonuniversal high vertex or a larger degree at a low vertex.
4. The m=8 case is contradictory even before any high-high edge is
   added: six low incidences already exceed a high degree five.
5. The m=7 classification allows highs of degree six through the
   high-high edge; it does not silently assume degree exactly five.
6. Medium degree-four vertices at m=6/7 cannot gain edges to saturated
   degree-two vertices; all potential medium neighbors were counted.
7. High-edge cancellation uses M, independently of A adjacency and
   the selected nonzero sign of the high-high entry.
8. K2,5's field rows can have zero sums. Rejecting them at that stage
   would be a false stronger claim; the integer endpoint budget is used.
9. Signed K5's both cyclic product types and overall sign reversal have
   the stated square/kernel. No automorphism of A follows or is used.
10. For K2,6 with balanced three signs of each kind, C=u s^T has
    s^T s=0 and u^T u=2 in GF(3), giving M^3=0. This is a valid field
    boundary example and has no eigenvalue-one primary space. It does
    not provide a binary graph-polynomial lift, sharpness or sufficiency.
11. The whole support is essential; smaller components cannot be
    isolated from other residual defects by this argument.
12. No execution, formal verification, external review, triangle
    incidence conclusion, search percentage or target result is inferred.

**PASS** for the exact stated bound with its pinned filter dependency.
This independent written review is internal and LOCAL_ONLY pending
ordinary registration and immutable publication outside the frozen
371-claim cutoff. No heuristic source or gate was changed.
