# Candidate four-branch cover after root normalization

Status: CANDIDATE pending a separate exact coverage and literal-mapping audit.
This refines the old five-case portfolio concept; it does not claim novelty.
The old mixed two-edge branch is locally impossible. No old UNSAT answer is
used as a proof here. No target automorphism is assumed.

Take any target and apply C-ROOT-SCAFFOLD-NORMALIZATION revision1 at any root.
Its14 inner vertices form seven matched pairs, and its84 outer vertices have
distinct two-symbol labels from different pairs. Every outer vertex has exactly
12 outer neighbors.

For an outer u with label {p,q}, each of the four inner symbols p,p^1,q,q^1
occurs in exactly one label among u's outer neighbors. For p or q this is the
adjacent-pair common-neighbor equality1, with no inner contribution. For its
mate the nonadjacent equality2 has exactly one known inner common neighbor,
leaving quota1. Every other symbol has quota2, though that is not needed below.

Let a,s,d count u's outer neighbors whose root-pair supports meet u's support
in respectively2,1,0 groups. Counting the four quota1 symbols yields2a+s=4.
The degree equation givesa+s+d=12. Hence d=8+a>=8. In particular an outer edge
with disjoint pair supports exists.

Permuting the seven inner pairs and swapping the two labels within each pair
extends to a permutation of all outer labels and preserves the fixed root
scaffold. This is a relabeling of an arbitrary graph, not an automorphism of
that graph. Map an ordered disjoint-support edge to u={0,2}, v={4,6}; its
adjacency may therefore be required without losing every labeling of a target.

Let x,y,z be the three Boolean edges from u to {0,3},{1,2},{1,3}. The quota for
symbol3 implies x+z<=1, and that for symbol1 implies y+z<=1. The only possible
triples are000,001,010,100,110. Swapping root-pair groups0and1 (symbols0<->2,
1<->3) fixes u and v, and swaps x and y while fixing z. Thus010 can be relabeled
to100. Four canonical patterns suffice:

| Branch | x y z |
| --- | --- |
| a0 | 0 0 0 |
| a1_complement | 0 0 1 |
| a1_cross | 1 0 0 |
| a2_crosses | 1 1 0 |

Every unrestricted target has at least one normalized labeled representative
in one of these branches, each additionally requiring u-v. Conversely any full
SAT graph in a branch is a target by the already checked base equivalence.
Target isomorphism classes can occur in multiple branches through different
choices of root/edge/labeling. These branches are not equal-sized graph regions,
and no percentage of target graphs is assigned to a completed branch.

Only if every one of the four exact instances has a complete independently
checked UNSAT proof, and this coverage/encoding chain passes independent
review, could their conjunction support unrestricted nonexistence. No such
solver result is asserted by this derivation.
