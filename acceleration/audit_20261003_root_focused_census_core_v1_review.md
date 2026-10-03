# Paper-only review of the independent frozen-root census scorer

Reviewer: `/root/structural`. Recorded: 2026-10-02T21:57:44+00:00.

Reviewed immutable source:
`acceleration/audit_20261003_root_focused_census_core_v1.py`, SHA256
`78fdaa10e0056ca048b9e31049dc2e30951cfaa7dba418751a98008a2a69168c`.
Reviewed specification:
`acceleration/audit_20261003_root_focused_census_core_v1_spec.md`, SHA256
`db48d13241e4fa1ae82b783593357e9cf051c68528073ae4dd600d859d4e30c6`.

This is a static algorithm review. No computation or fixture execution was
performed for this review. It grants no engineering gate, census completeness,
mathematical promotion or target-resolution approval.

For a proposed exclusive swap, the scorer takes differences of complete old
and new line pair sets. An adjacency row changes only at an endpoint of a pair
in their symmetric difference. If both vertices of an unordered pair lie
outside this endpoint set U, their rows are literally unchanged. Their
intersection and adjacency status therefore remain unchanged even if some
common neighbor belongs to U. Such a pair needs no score replacement.

For every vertex u in U, the loop visits all other vertices v except a smaller
vertex already in U. Thus each pair meeting U occurs exactly once: pairs with
one endpoint in U occur in that endpoint's iteration; pairs with two endpoints
in U occur in the smaller endpoint's iteration. Its population is
`|U|(n-|U|)+binom(|U|,2)`. Both edge and nonedge cost components are replaced,
so a changed adjacency category is covered.

When two lines share a point z and selected points are exclusive, edges from z
to the selected points can be removed and readded by a raw toggle sequence.
They belong to both complete pair sets and correctly cancel before determining
U. The common point can consequently retain an unchanged row. This does not
invalidate the affected-pair argument. The absence predicate permits existing
pairs belonging to the removed old lines, while rejecting a proposed pair
already supplied by a third line. Linearity gives uniqueness of those old pair
occurrences. Exclusive selected points keep both new lines simple and preserve
at most their original one-point intersection.

Neither mutable old line contains the frozen root. Swapping points only between
these two lines cannot introduce it, and no changed adjacency edge contains it.
The literal root adjacency and all frozen root-line edges persist. This does
not mean every common-neighbor count involving the root persists; the separate
complete root-residual recomputation remains necessary.

No falsification was found in these arguments. Recommended independent finite
controls include a shared-point cancellation leaving z's row unchanged; an
untouched vertex pair with a common neighbor in U; and an adjacency change whose
cost moves between edge and nonedge components. Source parsing, all raw record
fields, domain completeness, tie retention and any actual target census remain
separate checking obligations.
