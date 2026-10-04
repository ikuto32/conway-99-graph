# Independent written review of the saved-point overlap-clique corollary

Reviewer `/root/structural`; discovery origin `/root`; candidate writer
`/root/native_driver`. Review is against exactly
`docs/CANDIDATE_20261004_SAVED_POINT_INCOMPATIBILITY_CLIQUES_NO_K4_V1.md`,
SHA256 `ea10899e67a651d6bc4e9efc46c17273bf63f18ca8fdc0786442c93dc425e614`,
and its candidate record SHA256
`13b5f2ca1a996062a2fc9c573f2a8b2fe7dadbf212ebd2df10e778aec88b8eee`.
The full paper and record were read. This reviewer did not author the
candidate or the prerequisite pair/triangle checker. The only mathematical
work here is a different-author handwritten implication proof. No type,
clique, matrix or LP program, import, formal checker or external review was
run. No artifact, claim ledger, index or historical source was changed.

## Exact dependency and matching scope

The sole uses-result premise is
`C-FIXED17-TRIPLE-CAPPED-RATIONAL-POINT-PAIR-TRIANGLE-CLIQUE-DIAGNOSTIC` r1.
The statement-bound report is
`acceleration/results/20261004_independent_review/fixed17_saved_point_pair_triangle_cliques01/summary.json`,
SHA256 `63581c8af33390fbe4de82ebe48286920cc2b6fc8149d12aa07afeccf2b6ebab`.
Its full result is `external_type_triangle_cliques_full02/summary.json`,
SHA256 `bd88848b459ee8cb85b169fe192f8a61202543805b02a9596eaf35235738aa85`;
Root's accepted scope record is SHA256
`19eb70473fb84aafbb38a9efa9926184a6231a880e55c68843f58b86a75b586a`.
The logical/nonmap metadata of both reports was read. This does not repeat
their718-input closure or1770/34220 computation.

The same saved e311 rational vector, first472 ordered87d types, eligibility
cardinality>=3, positivity predicate and intersection>=3 edge definition
occur in both premise and candidate. The premise authenticates nonnegative
weights, all680 common-Q caps, every eligible positive pair and three-subset,
and exactly four triangle cliques with no weight violation. Its exact
triangle stream, SHA256
`4a9f741b8452efce4abdaf3499c8c25a0ed4d33a4344ab055f9d21ec9be37feb`,
was read in full: four records only. Thus completeness here is an accepted
premise, not inferred by inspecting a few producer records.

## Separate proof reconstruction

Let P be the60 positive eligible type vertices with the authenticated edge
relation. The four triangle vertex sets are

```
{130,152,344}, {395,399,471}, {404,424,471}, {461,466,471}.
```

Their union is the ten distinct labels
130,152,344,395,399,404,424,461,466,471. If a K4 existed, its four different
three-element subsets would all be triangles. Since the entire graph has
only four triangles, those four faces would equal the whole displayed
collection. Their union would be the four vertices of that K4. The observed
union has ten vertices, so a K4 cannot exist. A larger clique contains a K4,
so every clique in P has size at most three. A genuine listed triangle
exists, so the positive-support clique number is exactly three.

For any eligible positive type T, choose a three-subset Q of T. Its weight
is one nonnegative summand in the accepted common-Q sum, at most one.
Therefore every singleton weight is at most one. A two-element clique is
one of the completely checked incompatible pairs, with sum at most one.
A three-element clique is one of the four completely checked triangles,
also with sum at most one. The empty clique has sum zero. These exhaust
every positive-support clique by the preceding size bound.

For an arbitrary clique C in the whole eligible type graph, delete its
zero-weight vertices. The result is a positive-support clique with the same
total weight. The preceding cases therefore prove sum(C)<=1, regardless of
how many zero-weight vertices were deleted. This does not prove that the
whole eligible graph is K4-free. It proves exactly the saved-point weight
statement.

The four saved exact triangle sums were also inspected as rational strings:
122/143, 8020/10153, 9263/10153, 7063/10153. Each numerator is smaller than
its positive denominator. Arithmetic of the underlying weights is inherited
from the accepted complete diagnostic, not newly replayed here.

## Written falsification boundaries

1. Four found triangles alone do not rule out an additional disjoint K4;
   accepted completeness is indispensable.
2. The four faces123/124/134/234 of a K4 have union size four, so the union
   contradiction does not reject a legitimate K4 pattern.
3. Having a ten-vertex triangle union alone, without total triangle count
   four, would not be sufficient.
4. A positive clique of size five contains a four-subclique, so no separate
   maximum-clique census is needed after the K4 contradiction.
5. Pair sums<=1 alone allow three weights1/2 with triangle sum3/2; the
   separately authenticated triangle sums are necessary.
6. The singleton proof uses at least three points in T so a Q exists.
7. An empty or size-two type could have weight greater than one; such types
   are explicitly outside the claim, not silently assumed zero.
8. Common-Q caps imply an individual bound only with nonnegative other
   weights; this premise is inherited explicitly.
9. An all-zero eligible clique keeps sum zero after deletion and is covered.
10. A zero-extended positive pair or triangle keeps the same bounded sum,
    even if the original clique has more than three vertices.
11. The count threshold is <=1; equality is allowed, not a violation.
12. Clique vertices are distinct types, and the graph has no loops. A
    type's own possible multiplicity is handled by the singleton cap.
13. The occurrence of four positive triangles proves maximum exactly three,
    not merely an upper bound. No claim about the low-cardinality support
    maximum is inferred.
14. A new rational vector could have other positive support and a K4;
    no assertion is transferred away from the exact saved e311 point.

## Verdict and limits

No mathematical veto was found. The exact revision-1 candidate follows from
the stated accepted finite diagnostic, without a new numerical computation.
The verdict is limited to the single saved rational point's overlap-clique
cuts on cardinality>=3 types. No graph/integer completion, unrestricted
target conclusion, absence of other separating cuts, or whole-system LP
feasibility claim follows. The older necessary-cut interpretation is shared
provenance; this audit does not reapprove its author's theorem or the bulk
diagnostic by agreement. Root must read this distinct derivation before any
registration. There are14 written boundary checks and zero executed,
formal or external controls.
