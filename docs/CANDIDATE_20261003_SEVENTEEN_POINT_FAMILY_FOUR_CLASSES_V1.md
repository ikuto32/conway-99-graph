# Candidate: four isomorphism classes of the specified 17-point edge unions

Claim: `C-SEVENTEEN-POINT-LABELLED-TRIANGLE-FAMILY-FOUR-ISOMORPHISM-CLASSES`,
revision 1. Basis DERIVED; status CANDIDATE; review NEEDS_RECHECK.
Discovery author `/root`; frozen 2026-10-03T21:51:41.7627743+00:00. No computation or external review is asserted.

## Exact statement and scope

Let s,t,x,A={a1,a2,a3,a4},B={b1,b2,b3,b4},L={l1,l2,l3},R={r1,r2,r3}
be disjoint named point sets. Choose ell in L, r in R, a bijection
sigma:A->B, and a bijection rho:A->(L\{ell}) union (R\{r}).
Let H have exactly the edges in the following twelve triangles:

    {s,t,x}, {s,a1,a2}, {s,a3,a4},
    {t,b1,b2}, {t,b3,b4}, L, R,
    {x,ell,r}, and {a,sigma(a),rho(a)} for each a in A.

As all 9*24*24=5184 choices vary, these edge unions have exactly four
isomorphism classes under arbitrary permutations of their 17 vertices.
This statement is solely about the complete small graphs just defined.
It assumes neither their occurrence in an SRG nor any automorphism of a
hypothetical 99-vertex graph. It does not cover extra internal edges or
assert circuit minimality, inducedness, extension feasibility or an exclusion.

## Proof proposed for independent checking

The centers s,t are the only degree6 vertices; every other vertex has degree4.
They are adjacent, and x is their unique common neighbor. Given their order,
A and B are respectively their neighbors outside {s,t,x}. The remaining six
vertices form L union R. The graph on those six vertices is two K3 joined by
the bridge ell-r. Its bridge endpoints are exactly their two neighbors of x.
Deleting that bridge intrinsically recovers the two unordered three-point sides.
The initial informal statement that they were two disconnected components
was incorrect; this frozen statement includes the bridge.

The four A-B edges form a matching, and serve as a four-element row set.
Each row has a unique common neighbor in (L union R)\{ell,r}, namely rho(a).
Define three unordered partitions of the rows into pairs: PA from the two
A pairs in the displayed negative triangles; PB from the two B pairs pulled
back through the matching; and PR from the side of the assigned free vertex.

Every graph isomorphism therefore induces a row permutation preserving
the three named partitions, except that exchanging the centers exchanges
PA and PB. PR retains its name. Conversely, any row bijection with this
property extends to a graph isomorphism: map the centers and x; map each
row's A and B endpoints according to the center order; map its free vertex;
then map each distinguished bridge endpoint to the endpoint on the side
corresponding to that row partition. All twelve displayed triangles, hence
every edge, are preserved. This determines a bijection of all 17 vertices.

There are exactly three unordered pair partitions of a four-element set:
M0=12|34, M1=13|24, M2=14|23. Row permutations induce all permutations of
these three partitions: (23) exchanges M0,M1, and (34) exchanges M1,M2.
Together with PA/PB exchange, their triples have precisely four orbits:

    (M0,M0,M0); (M0,M0,M1); (M0,M1,M0); (M0,M1,M2).

They are distinguished by: all equal; PA=PB different from PR; PR equal
exactly one of PA/PB; and all distinct. Equality and the distinguished PR
name are invariants. Each pattern occurs because sigma can pull the fixed
B pairing back to any PB, and rho can assign its two vertices on each side
to any PR. The isomorphism converse above proves no further invariant remains.

## Evidence, shared components and limitations

The independent raw-family replay is a separate claim: Structural producer
a01fa and Native checker d661, report
`acceleration/results/20261003_independent_review/seventeen_point_family_full03/summary.json`
SHA256 f9a97abf560956b8b6d3dc154fbb47030c088093788cf0679651840d65cd8a57.
That replay checks all5184 labelled matrices and local geometry but does not
check this isomorphism theorem. This proposed proof does not use its valid
geometry count as a premise and has no executed isomorphism algorithm.

Root proposed the partition mechanism; Structural independently reconstructed
it in `acceleration/notes_20261003_seventeen_point_family_four_orbits_preliminary_v1.md`
SHA256 ba1791bf11d7e1e3c7b6802ac822d88fec5e37fcb3615c151ae0ab9b5b855f89
and caught the missing bridge. The preliminary reconstruction is disclosed
prior evidence, not approval of this frozen revision. A separate written
audit must bind this exact file hash, examine both implications and four-pattern
coverage, and try to falsify them. Labelled multiplicities and small-graph
automorphism orders are omitted from this claim. There is no target resolution,
formal proof, novelty claim or external review.
