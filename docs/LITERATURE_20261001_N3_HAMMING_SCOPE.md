# N3-free SRGs: a local grid, but no new covering theorem established

This bounded investigation establishes no new exclusion or universal Hamming
covering theorem. The N3 here is exactly the archive's induced six-vertex graph
(lexicographic edge-mask 5941): triangles 012 and 345, with cross edges 03 and 14.
The target's N3-free exclusion was already cited in the archive. No Cayley
structure or automorphism of an unknown graph is assumed below.

## What follows locally

Let a graph have exactly one common neighbour for adjacent vertices, exactly two
for nonadjacent vertices, and no induced N3. Every induced square lies in a
unique induced H(2,3), the 3-by-3 grid.

For a square a-b-c-d-a, write e,f,h,g for the respective third vertices of
triangles on ab, dc, ad, bc. The common-neighbour bounds make the opposite
triangles disjoint. N3-freeness forces ef and hg. Let i be the third vertex on
ef, and j the third vertex on hg. Apply the same opposite-triangle argument
to squares a-b-g-h-a and d-c-g-h-d: it forces ej and fj. The unique common
neighbour of the adjacent pair e,f then gives i=j. The resulting rows are
(a,b,e), (d,c,f), (h,g,i), and the columns are triangles as well. The common-
neighbour bounds rule out vertex identifications. Any extra edge between
different rows and columns would have the two other grid corners as common
neighbours, contradicting lambda=1. The successive unique triangle partners
also prove uniqueness of this grid.

This is two-direction compatibility. It does not by itself supply a proof of
compatibility among three directions, path-independent coordinate transport,
or a global finite Hamming cover. Those implications remain UNKNOWN in this
investigation, not refuted. The examples below cannot prove them universally.

## Exact bounded controls

The frozen native-free source and protocol are
`acceleration/theory_20261001_n3_hamming_scope.py` and its `_spec.md`.
Results are in `acceleration/results/20261001_n3_hamming_scope/`.

| Actual graph | Squares checked | Distinct induced grids | Cover established |
|---|---:|---:|---|
| H(2,3), srg(9,4,1,2) | 9 | 1 | Identity |
| Authenticated srg(243,22,1,2) fixture | 13,365 | 1,485 | Explicit syndrome map from H(11,3) |

Both complete SRG identities were rechecked. Every grid contains nine of the
enumerated squares. The prior exhaustive 243 triangle-pair census is pinned,
not duplicated: its cross-edge multiplicities are 0,1,3, so it is N3-free.
For the 243 fixture only, the eleven saved syndrome columns define a linear
map F3^11 -> F3^5. An identity 5-by-5 minor proves surjectivity, and all 243
neighbourhoods were checked to have the prescribed 22 distinct images. Thus
this actual graph is covered, with 3^6 vertices in each fibre. This uses its
explicit coordinates; it is not a coordinate assumption on arbitrary SRGs.
Changed adjacency, a repeated syndrome direction, and wrong grid incidence
were rejected. Exact fixture work took 0.125 seconds; no native search ran.

If a connected finite graph G really has a graph cover H(k/2,3) -> G, then
|V(G)| divides 3^(k/2): lifting an edge gives a bijection between its endpoint
fibres, and connectivity makes all fibre sizes equal. Therefore such a cover
would exclude (v,k)=(99,14), since 99 does not divide 3^7. The absent premise is
the universal existence of that cover; the divisibility calculation alone is
not a new target constraint.

## Primary sources and exact hypothesis limits

1. A. A. Makhnev, *Strongly regular graphs with lambda=1*, Mat. Zametki 44:5
   (1988), 667-672; English translation Math. Notes 44:5, 847-850,
   [DOI 10.1007/BF01158426](https://doi.org/10.1007/BF01158426).
   The [official Russian full text](https://www.mathnet.ru/php/getFT.phtml?jrnid=mzm&paperid=4220&what=fullt&option_lang=eng)
   was retrieved and read. On printed p.668, condition (*) forbids two triangles
   joined by exactly two edges; Theorem 2 excludes (99,14,1,2) under (*).
   For lambda=1, cross edges of disjoint triangles form a matching, so (*) is
   N3-freeness. The proof on pp.671-672, Lemmas 6-9, constructs a triangle graph
   and an impossible 33-vertex strongly regular subgraph. It does not state the
   sought universal ternary-Hamming covering theorem. This confirms the existing
   archive attribution, not novelty. The downloaded bytes equal the archive's
   recorded SHA256 ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431.

2. M. Matsumoto, *On the Classification of Locally Hamming Distance-Regular
   Graphs*, RIMS Kokyuroku 768 (1991), 50-61,
   [primary PDF](https://www.kurims.kyoto-u.ac.jp/~kyodo/kokyuroku/contents/pdf/0768-07.pdf).
   Here H(r) means the **binary** cube. Definition p.50 requires triangle-
   freeness, exactly two common neighbours at distance two, and completion of
   every seven-vertex cube-with-one-vertex-deleted configuration. Proposition 1
   on p.51 supplies a cover only under that definition. Our graphs have
   triangles; the third condition is also not an established N3-free consequence.

3. K. Nomura, *Distance-regular graphs of Hamming type*, J. Combin. Theory B
   50:2 (1990), 160-167,
   [primary publisher abstract](https://www.sciencedirect.com/science/article/pii/0095895690900717),
   DOI 10.1016/0095-8956(90)90071-7. The abstract's sufficient hypotheses include
   c2=2, c3=3, a2=2a1, and a1!=2. Full-text access was unavailable (HTTP403), so
   this record makes no fuller theorem attribution. For a diameter-two SRG in
   question, a1=1 and a2=k-2; the 243 example has a2=20, the target would have
   a2=12, and neither has a distance-three intersection number. Thus this
   sufficient theorem cannot be applied directly. Its hypotheses are not
   necessary for all covers, as the explicit 243 cover illustrates.

The two downloaded primary PDFs have exact access times, headers and hashes in
`source_access.json` (2026-09-30 UTC / 2026-10-01 JST). They remain LOCAL_ONLY
access evidence. Matsumoto PDF SHA256:
03185deb58b2e715687109b1225e43e408cbce8f57463e5904971b0ad6ce103a.
No claim about all covering literature is made. This lane stops at the local
lemma and the explicit missing global implication; it does not repeat the
already-known target N3>0 exclusion as a new result.
