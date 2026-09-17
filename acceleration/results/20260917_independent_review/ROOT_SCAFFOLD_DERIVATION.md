# Independent derivation: every-root positive scaffold

Exact claim reviewed: `C-ROOT-SCAFFOLD-NORMALIZATION`, revision 1. For every
99 by 99 symmetric binary zero-diagonal A satisfying A²=12I-A+2J, every
root r and every ordering/orientation of its neighborhood matching determine
a unique full labeling with the repository's 189 positive scaffold edges.
No outer adjacency is prescribed by this normalization. No automorphism is
assumed, and no restriction on same-fibre outer edges is used.

Independent argument: the diagonal matrix entries give degree 14. Off-diagonal
entries give one common neighbor for an adjacent pair and two for a nonadjacent
pair. For each u adjacent to r, precisely one of u's neighbors is also adjacent
to r. Therefore the fourteen vertices adjacent to r induce a 1-regular graph,
hence seven disjoint edges. These can be ordered and oriented arbitrarily.

An outside vertex x is nonadjacent to r and has exactly two neighbors among
those fourteen vertices. Their pair cannot be an edge of that matching:
otherwise that adjacent pair would have the two distinct common neighbors
r and x. Thus x determines an unordered pair across two different matching
edges.

Conversely take any cross-matching pair u,v. They are nonadjacent, so have
exactly two common neighbors, including r. A vertex of N(r) has only one
neighbor within N(r); thus no member of N(r) is a common neighbor of u,v.
Their second common neighbor is consequently an outside vertex, unique
because their common-neighbor count is exactly two. This proves both
surjectivity and injectivity of the outside-to-pair correspondence directly.
There are C(14,2)-7=84 pairs, accounting for all 84 outside vertices.

With the root at 0 and the chosen ordered/oriented edges at (1,2),...,(13,14),
each pair corresponds to exactly one outside vertex in the stated nested
group/group/sign/sign order. This proves uniqueness once the root-neighbor
choices are fixed. The prescribed edges number 14+7+2*84=189. Each inner
vertex occurs in twelve cross-matching pairs; its scaffold degree is
1+1+12=14. Root and inner degrees are therefore saturated. The reasoning
never chooses, removes, or forbids an outer-to-outer edge.

This is a conditional representation theorem. It allows conditional positive
scaffold clauses to be applied to normalized hypothetical targets. It does
not show that their conjunction is inconsistent or excludes every normalized
target. The theorem neither constructs a graph nor proves nonexistence.

The separate `root_scaffold.json` report checks the raw nine-vertex calibration
fixture, all root/label maps and corrupted controls through a distinct
implementation. Finite calibration is evidence about bookkeeping, not the
proof above. No literature priority or novelty claim is made.
