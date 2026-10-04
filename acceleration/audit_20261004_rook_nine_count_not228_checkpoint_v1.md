# Independent written challenge of the exact R228 exclusion

Reviewer: /root/checkpoint_audit; producer: /root/structural. The whole frozen
paper a716630106db4064393d5500d6e33b8db9867e0e5a1d79029f0654f2b7a0f613
and raw candidate were read. I independently reconstructed the four-or-five
population prerequisite in the separate c7269281 audit/report, including its
complete actual-point cycle proof. That exact r1 result is the sole inherited
mathematical premise of this extension. This review used no mathematical
program, import, enumeration, solver or ledger/Git mutation.

The local neighborhood is seven independent edges, each edge has one triangle
completion, actual triangles are linear, and a triple of triangles cannot have
three distinct pairwise intersection points. The resulting local defect graph
has degree d_T at each of a triangle's points. Under the genuine prerequisite,
the two possible populations are h4/p10/P14 and h5/p8/P13, where P=p+h.
At any point the number r1 of d1 triangles is even by local handshaking.

Take all positive triangles through a point v as one fan. Their outer points
are pairwise distinct. At both outer points, each d1 triangle needs one defect
partner and each d2 needs two. All those partners must be positive triangles
outside the fan, giving 2r1+4r2 incidences. Crucially, an external actual
triangle meets at most one outer point of the entire fan. Meeting two points
of one fan triangle violates linearity. Meeting points of two different fan
triangles produces the forbidden triple with intersections v and those two
points. At that one outer point there is one fan triangle and one possible
defect pair, even if the external triangle has deficiency two. Thus distinct
external triangles, rather than their deficiency mass, give
P-(r1+r2) >= 2r1+4r2, or P >= 3r1+5r2.

Apply the same geometry to just the d1 fan. Each of its 2r1 outer points needs
another d1 triangle to make the total d1 incidence even. This partner lies
outside the fan and an external d1 triangle repairs at most one such point.
Therefore p >= 3r1. With p10 or p8, even r1 can only be zero or two. This is
not an assumption that general even families have point multiplicity two;
the present small population and actual fan geometry force it.

Since P <= 14, r2 >= 3 violates the positive-fan inequality. If r2=2 then
r1 must be zero: the next even value two would require P >= 16. But two
positive d2 nodes alone cannot each have degree two in a simple local graph.
Zero-deficiency triangles cannot provide an edge. Hence r2 <= 1 everywhere
and all d2 triangles are pairwise disjoint. Wherever r2=1 its degree-two
node needs two positive neighbors, so r1=2 exactly. The local defect graph
is the three-node path, with its d2 node central. At all d1 support points
r1=2, and that support therefore has exactly 3p/2 points.

The h5 branch asks its five disjoint d2 triangles to occupy 15 distinct points.
Each of those points is in the d1 support, which has only 12 points when p8.
This fails by ordinary set cardinality.

For h4/p10, let S be the 15-point d1 support and choose a d2 triangle T. Its
three points each have two d1 triangles. The resulting six C triangles are
distinct and have twelve distinct outer points, by linearity within a bucket
and the three-intersection prohibition between buckets. They and T already
fill all of S. Each outer point belongs to one C and exactly one more d1
triangle. The four remaining d1 triangles V avoid T and partition those
twelve outer points. No inducedness of S was used in this reconstruction.

From A^2=12I-A+2J and regularity14, the symmetric A has roots3/-4 on the
orthogonal complement of the all-one vector. Q=3I-A+J/9 consequently has
eigenvalues0 on the all-one vector, and0/7 on that complement. It is positive
semidefinite. Put weight two on T, one on the twelve outer points and zero
elsewhere. Then the sum is18 and squared norm24. The known T/C/V triangles
have disjoint edge sets, since each target edge has one triangle partner.
Their unordered weighted edge sum is12+6*5+4*3=54. The known union therefore
gives w'Qw=3*24-2*54+18^2/9=0.

Every additional actual edge of S would subtract twice a positive endpoint
product from that zero value. Edges leaving S have zero weight contribution.
Positive semidefiniteness forbids every additional support edge: the known
eleven-triangle edge union is exactly the induced graph on S. This direction
is important; inducedness is a conclusion of the target Gram identity rather
than a hypothesis about the selected support.

The other three d2 triangles lie entirely in S, because every d2 point is
also a d1 support point. They are different from T and the ten d1 triangles.
Yet every available edge of S already has its actual third partner in one of
the eleven known triangles. Any further actual triangle on S uses such an
edge and must equal its known completion. This contradicts the additional
three d2 triangles and rejects h4. Both exhaustive prerequisite branches
have failed, proving precisely R != 228.

Hand falsifications retained: an external d2 triangle cannot provide two
copies of the same defect edge or meet two fan outer points; those are actual
triangle incidences, not aggregate mass slots. A local three-d2 configuration
can exist as a degree pattern but needs P >= 15, and a collapsed four-d2
cycle needs P >= 20. The earlier local labeling boundaries do not realize
the current populations P14/P13. The known fifteen-point edge union itself
is compatible with Gram equality and is not outlawed; only its demanded
additional actual triangles fail. New outer/outer, center/outer and
center/center edges would decrease the quadratic form by2,4 and8 respectively.
No omitted extra support edge, equitable profile, automorphism, N3-free
condition, Hamming cover or code-rank premise was used.

PASS for the exact r1 exclusion R != 228. No other rook count or full target
nonexistence is approved. Root's earlier outline and Structural's shared
strategy are disclosed; this is a separate proof reconstruction, not an
independent discovery claim. The exact prerequisite is explicit and its
genuine report/binding will accompany this record. Registration, publication
and any combination with other count exclusions remain separate.
