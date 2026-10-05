# Preliminary independent reconstruction of Root's four-orbit conjecture

Status: **PAPER_ONLY PRELIMINARY**, not a revision-bound approval. Root proposed
the four-class partition argument; Structural reconstructs it here while
waiting for an exact frozen Root candidate. There are zero executed
isomorphism tests, graph computations, formal controls or external reviews.
The 5184 producer outputs are not independently replayed by this note.

## Exact graph construction being considered

Use centers s,t, their common point x, four A points a_i, four B points b_i,
and six R points. On R choose two disjoint three-point sets L,R and
distinguished points ell in L and r in R. The negative triangles are

    {s,t,x}; {s,a1,a2}; {s,a3,a4};
    {t,b1,b2}; {t,b3,b4}; L; R.

The positive triangles are {x,ell,r} and four {a_i,b_sigma(i),rho(i)},
where sigma is a bijection A->B and rho bijects the four rows to
(L minus ell) union (R minus r). The adjacency is exactly the edge union
of these triangles. These quantifiers specify the finite construction;
they do not assume target occurrence, automorphisms of a 99-vertex graph,
or coverage of extra induced edges.

Every displayed triangle pair intersects in at most one point. Therefore
s,t have graph degree6 and all other points have degree4. Those two degree6
points are intrinsic, and their unique common neighbor is x. Given an
ordering s,t, their other four neighbors intrinsically identify A,B; the
six remaining vertices identify the two-sided R set.

A correction to Root's initial informal outline is essential: the graph
induced on those six vertices is **two K3 joined by one bridge**, because
{x,ell,r} adds the edge ell-r. It is not two connected components. The
bridge endpoints are exactly the two R-neighbors of x. Deleting that bridge
canonically recovers the two three-point sides, without naming their order.

## Three intrinsic unordered partitions of four rows

The A-B edges are exactly a perfect matching. Use its four edges as the row
set. Each has its assigned free R point, determined by the literal
construction. There are three unordered 2+2 partitions of the row set:

* PA: the two negative A pairs;
* PB: the two negative B pairs pulled back through the matching;
* PR: the two free points on each recovered R side.

Any graph isomorphism must send the degree6 centers to the degree6 centers,
then send x,A,B,R and the A-B matching as described. It induces a permutation
of the four rows, preserving the three named partitions if the centers are
not swapped, or swapping the names PA/PB while retaining PR if they are.

Conversely, a row permutation with those partition properties extends to
an isomorphism: map centers (possibly swap), map x, map A/B row endpoints,
map each row's free R vertex, and map the distinguished bridge endpoint on
each corresponding PR side. The triangle edges listed above are all edges,
so this extension preserves the full adjacency. No further orientation or
choice at a bridge endpoint survives once these maps are specified.

## Exhaustion of four equality-pattern orbits

For a four-row set the three possible partitions are

    M0 = 12|34,   M1 = 13|24,   M2 = 14|23.

The action of S4 on these three partitions is all S3: row transposition
(23) swaps M0/M1 and fixes M2, while (34) swaps M1/M2 and fixes M0.
Its kernel is the four-element Klein group. Together with the allowed
center swap PA<->PB, the ordered triples of partitions have precisely
these four equality patterns, with representatives

    (M0,M0,M0); (M0,M0,M1); (M0,M1,M0); (M0,M1,M2).

The third pattern includes PR equal exactly one of PA/PB; those two cases
are identified by center swap followed, if needed, by a row permutation.
The patterns are inequivalent because equality and the special PR name
are invariant under every allowed graph isomorphism. Each representative
can be realized: choose a B bijection pulling its negative matching back
to the desired PB, then assign the two free vertices of one R side to a
block of PR and the other two to the other block.

Thus the described graph construction has four graph isomorphism classes
by this preliminary paper argument. This remains unapproved until an exact
Root candidate receives a complete different-author revision-bound audit.

## Optional exact labelled multiplicities and automorphism consequences

For fixed PA, PB has three possibilities and PR three. Each PB has eight
B bijections: two choices of which B pair is assigned to the first PA-row
pair of PB, and two orientations in each pair. Each PR has eight free-R
bijections: side choice and two orientations within each side. There are
nine choices of distinguished bridge endpoints. Therefore each of the nine
partition combinations contributes 9*8*8=576 labelled constructions.

The four patterns have respectively 1,2,4,2 combinations, giving predicted
labelled multiplicities 576,1152,2304,1152. These are combinatorial counts
of the declared construction, not numerical isomorphism results from raw
data. Literal adjacency injectivity follows because the matching, bridge
endpoints and each free-R row association recover all construction choices
on the fixed named point sets.

The row stabilizer has order8 if all three partitions coincide and order4
otherwise. A center-swapping coset exists for all patterns except PR equal
exactly one of PA/PB. The predicted automorphism orders are consequently
16,8,4,8. These are automorphisms of the small constructed graph only.

## Limitations and archive review

The argument concerns these complete small edge unions. It says nothing
about an induced target completion, extra internal edges, which class can
occur in a target, or target nonexistence. No actual 99 matrix is read.
The limited Markdown archive search found current family specifications and
unrelated matching-design work, not a prior four-class theorem. It is not
an exhaustive novelty search. This note is not an independent executable
gate, a current-claim binding or a mathematical self-approval.
