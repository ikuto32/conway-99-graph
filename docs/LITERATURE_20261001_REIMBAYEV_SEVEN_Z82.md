# One versioned order-seven identity: exact, but already covered

This bounded literature investigation found no new constraint in the one identity
selected for detailed checking. It does not approve the paper's full table, assert
novelty, or resolve the Conway problem. The computation remains a producer
candidate pending separate review.

## Primary source and exact location

Reimbay Reimbayev, [Induced Subgraphs of Order Seven and Their Frequencies in
srg(n,k,1,2), arXiv:2608.19410v1](https://arxiv.org/html/2608.19410v1), submitted
19 August 2026. Section 2 gives an unnumbered frequency table and explicitly omits
the derivations. The selected row is `z82` on PDF page 10; its graph is panel 82
on PDF page 5 (`figure_2.png` in the source archive). There is no numbered theorem
for this identity.

Write H for two vertex-disjoint triangles with exactly two matching edges between
them. The source's N3 is H; Z82 is H together with an isolated vertex. With n3 and
z82 counting induced vertex subsets, the source states

\[
z_{82}=(n-6k+18)n_3.
\]

For unrestricted srg(99,14,1,2), this specializes to **z82 = 33 n3**.
No triangle-core normalization, fixed support, balance, or automorphism hypothesis
is involved.

## Independent local derivation

Fix any induced H. An outside vertex has at most one neighbor in each triangle:
otherwise an edge of that triangle would have both its third vertex and the
outside vertex as common neighbors, contradicting lambda=1. Thus the outside
neighbor count into H is at most two. Let b0,b1,b2 count these three possibilities.

H has eight edges and degrees 3,3,3,3,2,2. Counting incidences leaving H gives
`b1+2*b2=6*k-16`. The sum of prescribed common-neighbor counts over its 15 pairs is
`8*1+7*2=22`. Vertices inside H contribute
`4*binom(3,2)+2*binom(2,2)=14`, leaving exactly `b2=8` outside contributions.
Consequently

\[
(b_0,b_1,b_2)=(n-6k+18,\;6k-32,\;8).
\]

For the target this is `(33,52,8)`. Each H therefore has exactly 33 isolated
extenders. Conversely Z82 has a unique isolated vertex, so deleting it recovers
one H. This proves the displayed global frequency identity by a bijective count.

## Exact archive overlap

The 17 September note inspected this paper's abstract only. However, the pinned
archive's Wave 23 already includes deletion, vertex-orbit and pair-orbit extension
rows for all 208 seven-vertex classes. For each rooted extension of H, the row
combination

`deletion - sum(vertex-orbit rows) + sum(pair-orbit rows)`

has coefficient `1-d+binom(d,2)`. Since d is at most two, this is exactly the
indicator that the added vertex is isolated. Its right side is
`(n-6) - (6*k-16) + 8 = n-6*k+18`, times the number of H copies.

The fresh code checks the coefficient vector directly on all 208 saved raw graph
masks, without importing the old model. In its lexicographic-edge convention,
H has canonical mask 5941 and Z82 has mask 39509. The archived affine witness at
n3=705 has Z82 count 23265 and zero dependence on its Hamiltonian parameter,
exactly `33*705`. This establishes overlap for this row; it is not a rerun or
fresh approval of the whole archived 712-row system or the 208 paper formulas.

## Controls, correction and access provenance

The first frozen checker mistakenly demanded 32 H examples in the genuine
srg(243,22,1,2) fixture and failed that control requirement. Its source, protocol
and failure remain unchanged. V2 records the complete disjoint-triangle-pair
census: 133650 have zero cross edges, 240570 have one, and 8910 have three.
There are **zero** H copies, so this fixture is explicitly a vacuous check of the
selected identity; it is not reported as positive validation of the histogram.

A separate synthetic 99-vertex local fixture supplies a nonvacuous control.
Only the six H vertices have completed degree-14 and mutual common-neighbor
conditions; its remaining degrees are incomplete. It is not an SRG, full factor,
or proposed target. All 64 attachments, the 208 coefficients and six deliberately
corrupted controls are recorded. V2 completed in 0.504 seconds with no solver.

Primary bytes were accessed on 30 September 2026 at 16:44 UTC (1 October in
Japan). The versioned HTML and source archive are locally saved, with successful
HTTP receipts; downloaded complete source bytes are LOCAL_ONLY, with their
versioned primary URLs supplying retrieval locations.

- HTML SHA256: `09377f0b08646cfd92c847f76ee342805161f2480f8d3bbf49a95b4d52ff33af`
- Source archive SHA256: `21f5e912ede113c3dc1a892156274b2a4e184152bfe26b888ab4906b5e506e50`
- TeX member SHA256: `d2c0c9d8985a19c6f5418eed38ecff6b9b4d177c6359b4f2df799453cd2530e9`; selected row at line 211.
- Access receipt: `acceleration/results/20261001_reimbayev_seven_access/summary.json`, SHA256 `e3af72b27c456bcebe2ccd6387669c548d8aa06c53ddbd61828b8eac94d7b134`.
- Candidate result: `acceleration/results/20261001_reimbayev_z82_overlap_v2/summary.json`, SHA256 `6e79aa0c91a0f28fb575f089f9eb75915ce2b0debb0e777e73f27d0bc6fe1d57`.

The selected identity can serve as a consistency check in unrestricted graph
search, but adding it to the archived extension system supplies no additional
restriction. No claim is made about whether another table row could be useful in
a different search representation.
