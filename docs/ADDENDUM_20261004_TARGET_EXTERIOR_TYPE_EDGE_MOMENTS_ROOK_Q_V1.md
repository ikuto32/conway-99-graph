# Rook9 subset qualification for the exterior type edge-moment candidate

This append-only note qualifies the written rook9 example in
`CANDIDATE_20261004_TARGET_EXTERIOR_TYPE_EDGE_MOMENTS_V1.md`, SHA256
`cac608098a8bfee29487bce3c2b40ce86d8b2eb008cd5390b31c3a43b3d599c8`.
The original paper and candidate statement remain unchanged. Native identified
the omitted qualification during independent written review; Structural
reconstructed both cases here. This note does not approve the theorem or any
computational implementation.

Fix the current exterior type `e_i`. The rook9 exterior pool contains two
copies of each of `e_0,e_1,e_2`; excluding the particular current vertex leaves
one copy of `e_i` and two copies of each other type. Let Q be a two-point
subset of the three induced row points. No bits are forced in this hand
example, so the residual degree is three and the required overlap sum is two.

- If `i` belongs to Q, the free overlap slots are `0,0,1,1,1`. The sums of
  the three smallest and three largest entries are respectively one and
  three, so the required two lies in the closed interval `[1,3]`.
- If `i` does not belong to Q, the slots are `0,1,1,1,1`. The sums of the
  three smallest and three largest entries are respectively two and three,
  so the required two lies in `[2,3]`, at its lower endpoint.

The old paper's literal slot list is correct in the first case and was
unqualified about Q. Both cases obey its universal own-copy and multiset
proof. The block/profile/aggregate statement and its target-edge heterogeneous
counterattack need no mathematical change. No rook matrix, count witness,
solver, mathematical program, formal checker or external review was executed.
This is a written qualification only, with no ledger, index, publication or
availability change.
