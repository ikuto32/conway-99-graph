# Transport of target-extension cuts under scaffold relabeling

Let `S` be a partial adjacency specification on a designated59vertex set:
every pair is either fixed0, fixed1, or free, and each free unordered pair
has one distinct Boolean edge variable. Let `p` be a permutation of those
59 vertices preserving this entire fixed/free specification.

Extend `p` to99labels by fixing the other40labels. If a target adjacency
`A` extends `S`, define `B[i,j]=A[p(i),p(j)]`. Vertex relabeling preserves
symmetry, binarity, the zero diagonal, and the identity
`A²=12I-A+2J`: the relabeled identity holds because simultaneous row/column
permutation preserves `I` and `J`. Specification preservation implies that
`B` also extends exactly the same `S`.

Suppose an edge-variable clause `C` has independently been proved necessary
for **every** target extension of `S`. Apply that statement to `B`. Each
positive or negative literal on edge `{i,j}` becomes the same-sign literal
on edge `{p(i),p(j)}` when expressed in `A`. Consequently the mapped clause
is also necessary for every target extension of `S`.

This is a bijective change of labels between possible completions. It does
not assume `A=B`, that `p` is an automorphism of any hypothetical target, or
that the target has any nontrivial automorphism. The inference is valid even
if every hypothetical target graph is asymmetric.

If a local relaxation additionally uses degree groups, their prescribed
degree values and edge-variable groups must also be preserved to describe
the same local encoding family. In the audited780edge family, the checker
directly confirms all160degree rows. It also checks all59by59 fixed/free
entries, all780free edge-variable images, the rook core, the designated root,
the ten central vertices, the central matching and four incidence blocks,
the five ownership cells, and core common-neighbor contributions.

The current audit establishes each of32 explicitly supplied maps. It does
not establish completeness of the producer's proposed30,720-pair census,
enumerate all automorphisms of the scaffold, or normalize any hypothetical
target by its automorphism group. The map table applies only to the780edge
variables; no map of the17,400/29,640 auxiliary AND variables is asserted.

Every transported clause must still bind its parent proof, exact parent
literals, map and map direction, resulting literals and artifact hashes.
Map validity alone does not certify an unproved source clause. Deduplicating
identical mapped clauses does not count distinct excluded graphs or provide
target-wide coverage.
