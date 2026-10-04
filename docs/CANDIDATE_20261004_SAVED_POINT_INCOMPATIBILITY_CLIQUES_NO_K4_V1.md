# Candidate: all overlap-incompatibility clique cuts pass at the saved rational point

Claim `C-FIXED17-SAVED-RATIONAL-POINT-ALL-OVERLAP-CLIQUES-PASS`, revision 1. Root proposed the consequence of the complete triangle survey; Native writes the following finite combinatorial derivation. Structural is the prospective different-author reviewer. This candidate is not independently approved by its writer or by Root, and is not registered.

## Exact quantified statement and prerequisites

For the single saved e311192634b43b00e5c0b2e4d34cff62bcb38aaa59de1aae91450b5e004218da rational vector on the exact ordered 87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2 filtered472 types, restrict the type vertices to cardinality at least3. Put an edge between two distinct types precisely when their intersection has cardinality at least3. Then the positive-weight induced support graph has clique number exactly3, and every clique C of the whole cardinality-at-least3 type graph, including zero-weight types, satisfies the exact inequality

    sum of n_T over T in C <= 1.

No other vector, type universe, graph completion, integer solution, or whole-system feasibility/infeasibility is quantified. This is a consequence of one accepted complete finite artifact check plus the elementary graph argument below. No new maximum-clique executable was run.

The prerequisite complete computational diagnostic is `C-FIXED17-TRIPLE-CAPPED-RATIONAL-POINT-PAIR-TRIANGLE-CLIQUE-DIAGNOSTIC`, revision1: Native's genuine report `acceleration/results/20261003_independent_review/external_type_triangle_cliques_full02/summary.json`, SHA256 bd88848b459ee8cb85b169fe192f8a61202543805b02a9596eaf35235738aa85, independently reconstructed all60 positive eligible types, every1770 pair and34220 three-subset, all680 common-Q cuts, and the exact complete four-triangle stream. Root's exact-scope acceptance is `acceleration/results/20261003_external_type_triangle_cliques_v2_root_actual_full_acceptance01.json`, SHA256 19eb70473fb84aafbb38a9efa9926184a6231a880e55c68843f58b86a75b586a.

## The complete four triangles rule out K4

Using original type-column identifiers, the complete triangles are exactly

    {130,152,344},
    {395,399,471},
    {404,424,471},
    {461,466,471}.

Their literal union is

    {130,152,344,395,399,404,424,461,466,471},

which has ten vertices. A four-vertex clique contains the four distinct triangles obtained by deleting one vertex at a time. Because the accepted graph has exactly four triangles in total, any K4 would force those four listed triangles to be its four faces. Their union would then have exactly four vertices, contradicting the displayed ten-vertex union. Thus the positive support contains no K4. Any clique of order at least4 contains a K4, so every positive-support clique has order at most3. The four genuine triangles establish that the clique number is exactly3.

This proof uses the completeness of the accepted triangle stream. Merely finding these four triangles without excluding other triangles would not rule out a separate K4. The accepted pairwise-intersection rule is the literal edge relation; no target automorphism or unknown adjacency bit is assumed.

## All clique sums, including singleton and zero-weight cases

For a positive eligible type T, select any three-element subset Q of T. The accepted common-Q cap is the sum of all nonnegative type weights whose types contain Q, at most1. It contains n_T as one summand, so n_T<=1. This proves the singleton case without an unexecuted maximum-weight query. The empty clique has sum0.

A two-type clique is one of the accepted complete incompatible pairs, whose sum is at most1. A three-type clique is one of the four complete triangles, each with sum at most1. Together with the no-K4 result, these cover every positive-support clique.

Now let C be a clique of cardinality-at-least3 types with any zero-weight vertices included. Remove those zero-weight types to obtain C_positive. It is still a clique on the positive support and has the same sum. The preceding empty, singleton, pair and triangle cases show that sum(C)=sum(C_positive)<=1. It is unnecessary to forbid larger cliques containing zero-weight types; they cannot increase this saved sum.

The cardinality-at-least3 restriction is essential to the stated singleton argument and to the usual count-at-most-one clique cut. A type of size at most2 cannot share three inside neighbors with another type, and its exterior multiplicity need not be at most1. This corollary makes no singleton bound for such types. Nonnegative exact rational weights are also a premise, authenticated by the saved certificate and full replay.

## Necessary-cut meaning and limits

In a hypothetical target, two distinct exterior vertices cannot have at least3 common neighbors inside the fixed base. Therefore distinct eligible types connected by this intersection rule cannot both occur; an eligible type itself cannot occur twice. Hence each such clique gives the familiar necessary count-at-most-one inequality. The independently written pair/triple necessity is shared provenance, not rederived as a new target theorem here.

The corollary says that this saved rational point passes every cut of this particular overlap-clique form. It supplies no binary exterior adjacency, integrality, full Gram PSD/rank, vertex-external-CN sufficiency, induced completion, or target conclusion. Other necessary cuts can still separate the point. No actual clique beyond the accepted complete pair/triangle stream was enumerated by a new program, and no graph or type artifact was modified.

This new paper used file reads and hand combinatorics only: zero new mathematical commands, code imports, solver calls, matrix inversions, formal proofs, or external reviews. Native is the writer of this consequence and cannot approve it. Independent Structural written falsification and Root's separate metadata review remain required.
