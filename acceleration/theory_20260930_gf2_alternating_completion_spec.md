# Binary residual completion and rank diagnostic, version 1

This is a discovery experiment, not an independently approved claim. The question
is whether the already known rank-54 binary projection condition supplies a new
necessary triangle-factor test, and whether symmetry, zero diagonal, and even
residual degree strengthen the known mixed-equation kernel condition.

Before execution freeze this source, the companion Python source and derivation.
Use only Python standard-library exact integers. No producer imports, native SAT,
ledger edits, or graph construction search. Allocate at most 120 cooperative
seconds, checking the limit between finite stages; preserve failure/partial output
in a newly created directory. Expected memory is below 128 MiB. No automatic retry.

The mathematical domains are separate:

1. Arbitrary binary F,H: classify alternating D solving FD=H, and the additional
   condition D1=0. Exhaust all 4,096 ordered pairs of 2-by-3 matrices, against all
   eight alternating 3-by-3 matrices. Include an explicitly generic 2-by-4 example
   where even residual degree adds an obstruction. It is not a triangle factor.
2. Arbitrary alternating B and rectangular E: test the lower bound
   rank([[B,E],[E^T,D]]) >= 2 rank([B,E])-rank(B). Exhaust eight B of size three,
   64 E of size 3-by-2 and two D of size two. Calibrate rank independently by
   exhaustive row spans of all 64 binary 2-by-3 matrices.
3. The authenticated SRG(243,22,1,2) positive fixture: independently recheck its
   full integer identity, raw relabelling, and triangle blocks. Measure binary
   ranks and both mixed-completion criteria. This is not a Conway99 example.
4. Five saved 36-vertex cores (four connected identity-cross cores and the
   six-prism core), the deliberately locally invalid six-K3,3 scaffold, and
   exactly 64 random matching/permutation scaffolds generated using seed 20260930.
   Preserve every literal matrix, rank certificate and local-cap flag. The random
   population is diagnostic only, never universal coverage. Check the polynomial
   Gram identities even on inadmissible scaffolds, without calling them factors.
5. Two frozen annealer first-chunk objects: measure ranks only after explicitly
   recording full integer Gram failures. These are local domain fixtures, not
   full factors. Their measurements cannot prove a completion theorem.

No general rank(B)>=18 premise is allowed. The shared three-vector kernel only
gives rank([B,E])<=3n when F has even cell-column sums. Consequently rank(B)>=18
is a conditional sufficient reason that this lower-bound screen is vacuous for
n=12; finite samples cannot make that a universal assertion.

The exact alternating-completion and even-degree statements are in the companion
derivation. The quadratic residual identity and projector completion are not
asserted to follow from the linear mixed equation. All new theorems/results remain
CANDIDATE until a separate reviewer checks them. No novelty claim is made.

Command (fresh output only):

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_gf2_alternating_completion.py --out acceleration/results/20260930_gf2_alternating_completion
```
