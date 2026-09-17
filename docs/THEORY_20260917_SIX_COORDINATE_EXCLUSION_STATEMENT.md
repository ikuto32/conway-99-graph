# Exact scope of the six-coordinate exclusion

Proposed ledger binding: C-PARTIAL-K-SIX-COORDINATE-EXCLUSION, revision1.
This addendum records completed evidence during the explicit user stop; it
authorizes no resumed computation and does not itself promote the claim.

Statement: no strongly regular graph with parameters(99,14,1,2) completes the
frozen labelled root-neighborhood partial graph in
`acceleration/results/20260917_partial_six_matchings/manifest.json`, with its
132 fixed outer K edges and all prescribed absences retained, and both
same-sign coordinates at root groups0,1,2 freed. Only its2,040 listed unknown
outer pairs may vary. This is a conditional family exclusion, not a claim
that every hypothetical target graph belongs to this family. No nontrivial
automorphism assumption or target-wide coverage fraction is used.

The independently complete original local tables contain879,449 choices.
The independently sound neighborhood matching filter rejects166,728 and
retains712,721 choices across84 nonempty centers. These are disjoint stages
of one frozen population, not counts of complete graphs. Every target
completion in the declared family induces one retained choice per center,
hard reciprocal marginals, and all full co-neighbor moment equalities.

For those retained tables, the final-checkpoint integer support weights give
the lower bound906048/1048576=14157/16384>0. Therefore the necessary phase-I
objective cannot be zero, contradicting any completion in this exact family.
The producer artifact is
`acceleration/results/20260917_six_moment_pdhg/run01/certificates/10000_last.json`,
SHA256 `e4d660b5d3ddb7039f9cdf7fb80e014e1e53e1ce858c6d16cac2b9a3a3509d7f`.

Independent premises and arithmetic:

- Complete-domain audit: `independent_review/six_matchings/summary.json`,
  SHA256 `051a57b2fc1b5353a6100b949f86674483cff686c4f797f4f1ad8b037d7f3768`.
- Matching partition audit: `independent_review/six_coordinate_matching_filter/summary.json`,
  SHA256 `05d4284f04fb5c84491394695c6f56a3e5517302ae95c1885b27592cfed78a7f`.
- Necessary model audit: `independent_review/six_filtered_moments.json`,
  SHA256 `f27467b03a34fe3ea3adec4e537585e71d5697f4e63562cdd43d7e6822c8f3e7`.
- Independent raw-neighborhood support audit of all six attempts:
  `independent_review/six_gpu_support.json`,
  SHA256 `0814b6d5e660b876247cf83dc4e37cfaa0e86ec1d1b05b59ab8b6fd63ebbcf80`.

The abbreviated independent-review paths above are relative to
`acceleration/results/20260917_`. The separate reviewer checked every recorded
support maximum, first maximizing original ID, integer numerator and exact
quantization rule. Four positive and two nonpositive attempts are preserved.
No floating score or solver convergence claim is a proof premise. External
review and unrestricted Conway99 resolution remain unestablished. Root owns
the final ledger binding and status.
