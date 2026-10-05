# Candidate exact double-fiber and induced-rook bijection

Status CANDIDATE; paper derivation only, no independent approval or executed
new controls. This does not supply an exclusion, a graph, a rank upper bound
or a novelty claim. The earlier inverse theorem is explicit mathematical
context, not an assertion that its producer verifies this new statement.

Let G be a finite simple graph in which every adjacent pair has exactly one
common neighbor. Use the full actual triangle family, one triangle per edge
completion, and its binary vertex-by-triangle incidence matrix B. An unordered
triangle path is a set of three distinct actual triangles whose pairwise
intersection sizes are0,1,1, with the two intersection vertices in the middle
triangle distinct. Its XOR support has size5. Let P be the number of these
paths, X the number of their distinct supports, and D the number of supports
having exactly two such path preimages. Let R be the number of induced nine-
vertex subsets isomorphic to the3-by-3 rook graph; count actual nine-subsets,
not graph automorphisms, labeled embeddings, or pairwise-disjoint copies.

The previously independently derived inverse lemma states that every path
support has a unique isolated point r in its induced subgraph, that each fiber
has at most two paths, and that a double fiber's remaining four vertices form
an induced C4. Thus X=P-D. That inverse theorem is in
`acceleration/audit_20261003_triangle_image_weight5_v1_proof.md` (8844b6...)
and its complete finite audit is dedb5c.... The sharper C4-injection proof is
separately written in ROOT's bdc99... and the peer's7099... notes. Those do not
independently verify the new whole-nine-set bijection below.

The new precise candidate statement is

    D=9R,  X=P-9R,  N5(im_GF(2) B)>=P-9R,

and every induced C4 is contained in at most one induced rook-nine subset.
In particular9R<=c4(G). No regularity, common-neighbor condition on nonedges,
target automorphism or hypothetical graph existence is assumed in this
general statement. R may be zero.

## Reconstruction of a whole rook from a double fiber

Name its induced C4 a-b-c-d-a and its unique isolated support point r. Let
p,q,s,t respectively be the unique edge completions of ab,cd,ad,bc. The two
inverse paths must use both perfect matchings of the C4, so their middle
triangles are r-p-q and r-s-t. Hence pq,st and all four r-completion edges
are present. Every completion lies outside the C4. If two adjacent C4 edges
had the same completion, their common endpoint joined to that completion
would have two common neighbors. If opposite C4 edges had the same completion,
that completion joined to any corner would likewise have the corner's two
C4 neighbors as common neighbors. Thus p,q,s,t are four distinct vertices.
The middle triangles and the isolated support property make r different from
all four completions and corners: all nine vertices are distinct.

No completion has additional C4 neighbors. For example p already completes
ab. If p-c were an edge, it would supply a second completion of bc in addition
to t. If p-d were an edge, it would supply a second completion of ad in
addition to s. The same argument applies cyclically. No edge connects two
completion vertices from different matchings: for example p-s would have
both a and r as common neighbors. The four forbidden pairs are ps,pt,qs,qt.
The support property excludes r joined to any corner. These exhaust every
possible extra edge among the nine vertices. Consequently their induced graph
has exactly the rows and columns of

    a b p
    d c q
    s t r

as triangles; it is the3-by-3 rook graph. This displayed coordinate assignment
is an isomorphism of the reconstructed fixed graph, not an automorphism
assumption on G or a target. The whole nine-subset is uniquely determined by
the support: its r/C4 are intrinsic, and all four edge completions are unique.

## Converse and the factor nine

Fix an induced rook-nine subset S and any r in S. Its four nonneighbors within
S form an induced C4 Q. Both of Q's perfect matchings have their edge
completions inside S, and each pair of opposite completions forms a triangle
with r. Those triangles are actual triangles of G, and uniqueness of edge
completion means that no outside point can replace them. The two constructed
triangle paths have the same support Q union {r}. The old inverse lemma gives
at most two preimages, so this is a double fiber.

Different r give different supports because their induced isolated points
differ. If two rook subsets gave the same support, the unique reconstruction
of the previous paragraph would make the subsets equal. The construction is
therefore a bijection between pairs(S,r), with r in S, and all double fibers.
This proves the candidate D=9R without assuming copies disjoint in vertices
or triangles. Their C4s are disjoint as four-subsets: any shared C4 has a
canonical matching whose unique completions fix its central completion and
whole nine-subset. A rook has nine C4s, one for each missing row/column r.

## Conditional target consequences and existing overlap

For an exact target A, P=24948 and c4=2079, so R<=231 and
N5>=24948-9R>=22869. This explains the existing lower count22869 but does not
improve it unconditionally. If R were separately proved zero, the same
implication would give N5>=24948; that premise is UNKNOWN here. No conditional
rook exclusion is being inferred from historical failed searches.

`docs/AUDIT_20260917_ROOK_REGULAR_SET.md` already independently derives the
conditional exact18-cell encoding for a target containing a rook-nine. Every
outside point then has exactly one neighbor in the rook; the90 outside points
form nine groups of ten. The quotient is compatible with the target spectrum.
This existing reduction is not new and not a rook exclusion. The earlier
`docs/LITERATURE_20261001_N3_HAMMING_SCOPE.md` records only the extra N3-free
hypothesis under which every square completes to a unique grid; that extra
hypothesis is not used or assumed in this bijection. It does not provide a
global covering theorem or unconditional target nonexistence.

## Proposed independent falsification, not executed

Use all seven small actual adjacency fixtures of the prior N5/C4 controls.
Independently enumerate complete nine-subsets in those small graphs and
compare each(S,r) to raw support fibers, rather than importing producer
reconstruction. Add two disjoint rook9s to challenge overlapping/disconnected
counting and a loose four-triangle cycle with a C4 outside the collision map.
Rook9 should have R1,D9,P18,X9; two disjoint rooks R2,D18, and other fixtures
R0,D0. A relabeling must preserve the actual nine-subset/support bijection.
Corrupt nine-vertex identifications, one extra edge, missing completion and
duplicate support/cycle ownership. Explicitly preserve a K7 missing-lambda
control where complete triangle image collisions violate the assumptions.
Neither fixture agreement nor self-authored controls establish the theorem;
a separate written reconstruction audit is required before promotion.
