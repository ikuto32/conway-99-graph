# Independent full99 family clause transport argument

The objects here are the exact eight-coordinate full99 family model and a
previously independently checked 44-literal Gram clause. This application
uses full99 permutations, rather than broadening the earlier written theorem
for permutations of a designated59vertex scaffold.

Let `S` be the complete99by99 symmetric matrix of fixed 0, fixed 1, or free
entries. Let `p` be a permutation of all99 indices satisfying
`S[u,v]=S[p(u),p(v)]` for every ordered pair. Let `X_e` denote the distinct
Boolean variable attached to each free unordered pair `e`. Then `p` induces
a bijection `f` of the 2,160 free-edge variables: the variable of `{u,v}`
maps to the variable of `{p(u),p(v)}`. Signs of literals are unchanged.

Given any target adjacency `A` extending `S`, define
`B[u,v]=A[p(u),p(v)]`. The permutation preserves symmetry, binarity, diagonal,
and the identity `A^2=12I-A+2J`; simultaneous row and column permutation fixes
both `I` and `J`. Preservation of `S` ensures that `B` extends the same
recorded family. The independently verified source clause therefore holds
on `B`. When its literals are expressed using entries of `A`, it becomes
exactly the same-sign clause obtained by mapping each variable with `f`.
Thus every checked clause image is necessary for every target in this family.

This changes labels between possible completions. It does not assume or prove
`A=B`, does not assume that `p` is an automorphism of any hypothetical graph,
and does not use any restriction on the graph's automorphism group.

The independently audited full99 CNF is equivalent to target adjacencies in
this family. Accordingly each transported clause is already a consequence
of that CNF. Appending these clauses, if separately authorized, would be a
redundant strengthening, with no additional assumption and no reduction of
the target family. No auxiliary-variable permutation is needed for this
semantic argument, and none is claimed by the edge-map audit.

The artifact checker verifies every raw matrix entry and every primary
variable image for every supplied permutation. It derives clause images
directly from raw vertex permutations and the exact source literals, checks
every recorded transport, and compares the complete deduplicated clause set.
It tests an identity map and deliberately corrupted maps and clause records.
The parent source clause's exact certificate and independent audit are pinned.

This verification establishes only the supplied explicit maps and their
clause images. Unless a separate exhaustive argument is recorded, it makes
no assertion that the producer found all permutations preserving this family,
or that any proposed candidate-generation census is complete. The count of
unique clauses is a syntactic count; it does not count disjoint excluded graphs
or provide a denominator for overall Conway-99 search coverage.
