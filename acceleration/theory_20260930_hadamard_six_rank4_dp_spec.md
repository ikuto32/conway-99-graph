# Nine rank-four sextets: complete marginal deviation DP

Freeze before running. Candidate input is the nine unresolved rank4/kernel2 subsets from the complete six-subset census. Allocation120 seconds, no native or local-factor solver. This stage uses linear marginal/count necessities only; it does not impose local colour triples, quadratic Gram equations, or column caps.

For each coordinate a, enumerate all literal six-vectors v with v_i=0 when group i does not contain a, v_i∈{-1,0,1,2} otherwise, and H_E*v=0. These bounds are exactly nonnegative fibre counts0..3 after subtracting1. Enumerate every ordered pair v0,v1 and retain v2=-v0-v1 iff it is in the same finite vector set. Thus all three fibre counts sum3 at every incident coordinate, with no fibre quotient or rational-lattice assumption.

Verify the supplied rank4 minor and independent two-vector kernel. Choose the lexicographically first two group coordinates for which the2x2 projection matrix on that kernel has nonzero determinant. Projection to those two coordinates is injective overQ; no unimodularity is asserted or needed because candidate vectors were enumerated literally. Global group-fibre quotas sum_a v_f(a)=0 are therefore equivalent to zero total projected coordinates for fibres0 and1; fibre2 then follows. Track exactly four integer quota sums plus the union of the six group activity bits. Final zero quota sums with activity mask63 means exactly all six nominated groups are unbalanced in this marginal relaxation.

Dynamic programming stores every reachable state, exact number of ordered coordinate-profile sequences, and one predecessor path. Save each complete coordinate layer as deterministic gzip JSONL with hashes, transition counts and immutable checkpoint receipts. Process cases and coordinates in ascending order. Report complete final path counts only for completed layers/cases. A cooperative deadline is checked every2,048 source states and after each layer; stop with UNKNOWN if unfinished. Resumption, if explicitly authorized, uses a new output directory and authenticates completed checkpoints; it restarts an interrupted layer from its last complete predecessor checkpoint. No automatic resume.

Controls: derive the real four-group rectangle(0,7,9,19), whose two common-coordinate opposite deviation profiles give six exactly-four-active marginal witnesses plus one balanced witness. Check those witnesses literally against H, support membership, all group/fibre sums and activity. Corrupt a local fibre sum, support membership, quota sum and activity to confirm rejection. Verify the two-coordinate projection determinant and reject an altered certificate. Controls are marginal witnesses only, not full factors.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_six_rank4_dp.py --out acceleration/results/20260930_hadamard_six_rank4_dp
```
