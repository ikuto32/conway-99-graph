# Complete coordinate marginal domains, arbitrary exception counts

Frozen before execution. The question is the size and exact contents of the necessary integer marginal domains for each of the twelve coordinates on the pinned six-prism Hadamard support. Earlier `hadamard_triplicate_counts` enumerated only until the first nonzero witness in `{-1,0,1}^10`. The six- and seven-exception DP sources enumerate restricted nominated group sets. This task does not repeat those restricted experiments or claim a complete repository-history search.

For each coordinate a, construct the leading-one and twelve raw support-incidence rows restricted to its ten incident groups. Derive exact rational RREF with a complete left row-operation matrix. Rank six leaves four free coordinates. Enumerate all 256 free-coordinate assignments in `{-1,0,1,2}^4`, recover the other six entries exactly, and keep only integral vectors with all ten entries in `[-1,2]`. Save every trial, every accepted vector and its full twenty-group zero extension. RREF and enumeration of every bounded free assignment prove completeness of this producer domain; independent review remains required.

Then enumerate every ordered pair of accepted vectors `(v0,v1)` and retain the triple exactly when `v2=-v0-v1` is also in the domain. Save every ordered triple as vector indices, explicit three-by-twenty deviations, incident ten-by-three counts, full twenty-by-three count signatures and activity masks. Counts are `1+delta` on incident groups and zero on absent groups. No exception-count bound, local word-triple lookup, joint compatibility across coordinates, groupwise cancellation across coordinates, outside-column caps or residual graph is imposed. All such subsequent tasks require separate protocols. A zero or nonzero vector here is only a marginal projection.

Before the census, compare free-coordinate enumeration with complete brute force on small synthetic matrices, include zero and nonzero exact solutions, and reject malformed bounds/kernel/count controls. Check exact `E*M=R` and all accepted raw integer equations. Bind the existing independently established marginal theorem and raw support, plus all inspected overlap sources and commands. Output remains CANDIDATE; this producer must not approve itself.

Limits: sixty seconds for the complete twelve-coordinate census, checked between coordinates and ordered-pair rows; at most 256 projection trials and 65,536 ordered vector pairs per coordinate. Save an immutable checkpoint after every completed coordinate. On a limit, preserve the completed prefix and report incomplete rather than promote a complete table. No native solver, GPU or environment change. Use the existing locked uv environment and tqdm.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_coordinate_marginal_domains.py --out acceleration/results/20260930_hadamard_coordinate_marginal_domains
```

The parent plans an independent complete `4^10` literal enumeration per coordinate, separate from this free-variable production path.
