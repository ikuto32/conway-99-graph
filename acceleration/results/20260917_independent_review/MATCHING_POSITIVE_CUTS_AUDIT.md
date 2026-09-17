# Independent audit of sixteen positive-edge neighborhood clauses

Claim `C-MATCHING-POSITIVE-CUTS-16`, revision 1: **VERIFIED within its
conditional scope**, recommended for independent-ledger promotion. The raw
checking record is `matching_positive_cuts_recheck.json`, SHA256
`3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9`.
It binds every raw clause, producer source, manifest, and the exact proposed
statement. The checker is `acceleration/audit_20260917_matching_cut_recheck.py`.
The first successful report, `matching_positive_cuts.json`, is preserved but
its documentation binding became stale when the producer clarified that all
non-scaffold edges remain unrestricted. Final delivery detected that change;
the independently identical calculations were rerun against the frozen new
document. Neither raw clause nor mathematical statement changed.

For each saved positive literal set L, every target SRG containing the fixed
189 positive labeled root-scaffold edges satisfies
`sum(A_ab for ab in L) <= |L|-1`. Every other adjacency is unrestricted.
These are sixteen reusable conditional clauses, not sixteen newly excluded
complete overlap assignments, and not a proof of general nonexistence.

The independent checker imports no project or producer code. It reconstructs
the scaffold and positive prerequisites using Python sets, checks all 4,851
unordered full-graph pairs, then repeats that complete degree/common-neighbor
check after inserting every missing pair of free neighborhood vertices.
It exactly reconstructs every allowed/blocked pair and checks every saved
explicit blocker. It separately reconstructs the connected components after
the saved separator and verifies the odd-component inequality. An edge-by-edge
reachable-subset dynamic program independently confirms absence of a perfect
matching; it does not use the producer's recursive matching routine.

The implication is sound because the four protected center-overlap edges,
eight selected center-star edges, and two scaffold edges force fourteen
distinct neighbors of the center. Degree fourteen fixes its neighborhood.
For each neighbor y, lambda=1 says that precisely one member of that
neighborhood is adjacent to y. Thus its induced graph must be a matching.
Already present internal edges are forced matching edges with disjoint
endpoints. Remove their endpoints. Every remaining completion matching edge
must be in the checked permissive graph: positive-edge additions cannot
decrease degrees or common-neighbor counts, and changing a nonedge to an
edge decreases the allowed common-neighbor cap. A failed insertion therefore
cannot be repaired by an otherwise unrestricted adjacency choice.

In the permissive graph, each odd component after removing the saved
separator needs a distinct separator vertex in any perfect matching. The
checked number of odd components exceeds the separator size in every case.
This elementary necessity proves the contradiction without a completeness
theorem about finding such separators. No negative overlap literal or
nontrivial automorphism is assumed.

Controls: K4, two disjoint odd components, their bridge repair, and the empty
matching have the expected independent matching outcomes. Five altered raw
certificates are rejected: a deleted center prerequisite, deleted clause
literal, false common-neighbor blocker, false separator, and an added
permissive edge. All sixteen original raw records pass.

This audit does not establish minimal cores, reproduce the greedy deletion
history, or freshly verify historical star-domain membership or empirical
containment counts. None is needed for the exact recorded clause statements.
The underlying target and target-wide coverage remain UNKNOWN.
