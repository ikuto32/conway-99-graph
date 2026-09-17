# Independent finite clause transport and application audit

`matching_cut_cyclic.json`, SHA256
`4ce5e677ea93bb5b9e261a7ce6b07dc23c0b1aac97d07f29f9687faf998ae77d`,
records independent verification of the frozen cyclic/sign pilot. The source
is `acceleration/audit_20260917_matching_cut_cyclic.py`.

Every one of the seven cyclic root-group shifts combined with 128 target-group
sign masks was independently reconstructed as a full 99-vertex permutation.
All 896 are distinct, fix the root, and preserve the entire 189-edge positive
scaffold. The checker reconstructed every image of the sixteen independently
approved clauses and compared exact literal sets and all parent/map witnesses.
There are 14,336 generated images and 14,336 distinct literal sets in this
particular bank. No other root-group permutations were covered.

Transport is sound without assuming a graph automorphism. If a target graph
containing the scaffold violated a transported clause, applying the inverse
vertex permutation would yield a target graph containing the same scaffold
that violates the approved parent clause. Adjacency, degrees and common-neighbor
counts are invariant under a vertex permutation. This contradicts the parent
conditional theorem.

The application check scanned the entire bank for each of the frozen 29
candidate records. It compared the clause's missing positive literal set with
its eight required center-star edges. Any extra missing literal prevents a
hit; otherwise the exact original mask must occur in the recorded center's
domain table. This independently checks unsuccessful applications as well as
hits. At other centers, a single star can add at most one of these eight
required edges; all eight were explicitly checked absent from each candidate's
base. Consequently this covers every named original choice, not just sampled
centers. The identity application audit and all original IDs are hash-bound.

Result: exactly 324 unique original choices are removed from the population
of 747,064 named choices. The removed set equals the prior identity-clause set
in every record. Thus there are zero additional removals in this named corpus,
and no empty domain. This finite negative result does not establish that the
clauses have no use elsewhere, that other relabelings add nothing, or that any
complete overlap assignment has been excluded.

Controls accept the identity map and reject a duplicate image, a wrong outer
label, and a moved root. The checker imports only an earlier independent
scaffold/edge helper, ordinary Python libraries and tqdm for progress; it
does not import a producer. Original domain completeness is reused from the
hash-bound earlier independent audits, rather than newly enumerated here.
