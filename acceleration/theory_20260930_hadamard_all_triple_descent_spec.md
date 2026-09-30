# Bounded all-triple exact Gram descent

Question: can direct block-coordinate descent find a full prescribed-Gram
factor on the one fixed six-prism Hadamard coordinate support, without fixing
how many repeated-support groups are balanced or exceptional?

The domain is the Cartesian product of the complete, independently checked
31,110 increasing local word triples for each of20 equal-support groups. Each
word has two coordinates in each fibre. All local Gram upper bounds and all
three within-group column caps are already enforced by this catalogue. Every
group may use every catalogue entry. No fibre parity, exception count, cyclic
relation, target automorphism, or cross-group cap restriction is imposed during
the search. ResidualD is absent. Ordering the three equal-support columns is the
previously checked harmless local column relabelling.

This differs from the recorded GPU permutation annealer: that search preserves
within-fibre Gram matrices and minimizes its cross-Gram objective over edge
permutations. Here the support L is fixed, a move replaces an entire local triple,
and temporary within-fibre Gram errors are allowed. The earlier fixed-L SAT/MIP
models and balanced/profile searches do not use this coordinate-update rule.
No novelty or comparative performance claim is made.

Objective `FIXED_L_FULL_GRAM_FROBENIUS_SQUARED_V1` is exactly
E(F)=sum over all36x36 entries of (FF^T-B)^2, computed with signed64-bit integers.
Smaller is better; zero means full Gram equality only. Diagonal entries have
weight1 and strict upper-triangle entries weight2. Each local triple's171 upper
triangular entries on its18 possible rows are precomputed. An update evaluates
all31,110 candidate replacements by the exact expansion of this objective and
chooses uniformly among minimum-score choices. Sweep order is shuffled. After
a full sweep without improving that chain's saved best score, replace two
distinct randomly chosen groups by uniform catalogue entries. Preserve those
worsening kicks, RNG state and current/best states. There are no floating-point
scores, annealing probabilities, pruning or certificate claims.

Selection/resource protocol: four chains, seeds99023000,99023001,99023002,
99023003, each with24 seconds of cooperative search time. One120-second total
pilot budget includes preparation, calibration and checkpointing. Each chain
has a maximum2,000 coordinate updates. Check time before each coordinate call;
one matrix operation may finish after its deadline and actual overrun is saved.
No automatic restart of the pilot or silent time allocation extension. Save an
immutable checkpoint at every sweep and final state, with RNG, current/best
indices, current/best exact scores and raw36x60 factors. Save every update and
kick in JSONL. Stop immediately on an exact Gram zero and send it for independent
raw validation; never self-promote. A positive score or time limit excludes
nothing, and no target-wide search fraction exists.

Before research, the generic literal scorer must pass the genuine SRG243
factor fixture against its correct non-target Gram and reject a flipped entry.
The fast local matrix and replacement-score formulas are compared against
separate literal set-intersection computations on saved controls. A synthetic
fixed-L factor supplies a perfect-score positive against its own Gram, explicitly
not the research Gram. Split23+41 steps through a JSON checkpoint must equal64
steps in current/best choices, RNG, counters and scores. Deliberately corrupted
score/domain/input controls must fail. These are producer calibrations; root's
independent raw-score review remains necessary for any material outcome.

Python uses only existing locked numpy2.5.3 and tqdm4.67.1 plus the standard
library. No environment or native compiler changes. Save source/spec/input hashes,
source commit, commands, platform/processor metadata, dependency versions,
precomputation hashes, calibration results and actual execution limits. Checkpoints
are resumable through the same state-loading function; a later research resume
requires a separate declared allocation, never an automatic continuation.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_all_triple_descent.py --out acceleration/results/20260930_hadamard_all_triple_descent
```
