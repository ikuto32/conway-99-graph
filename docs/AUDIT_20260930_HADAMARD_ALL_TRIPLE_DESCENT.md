# Independent all-triple descent artifact review

This review addresses the saved finite experiment, not the success of a construction method or an exclusion. Its objective is the exact sum of squared errors over all 36 by 36 entries of `FF^T` against the Gram prescribed by the raw core. The objective and feasible domain differ from the earlier permutation annealer, so their numbers must not be compared directly.

The independent implementation imports no producer or earlier checking code. It derives the Gram by literal multiplication of the raw core, reconstructs the twenty sorted repeated supports from L, enumerates all 117,480 increasing triples of the ninety balanced words, and checks local Gram and within-group column caps. All 31,110 surviving triples and every entry of the saved 31,110 by 171 contribution array are compared. NumPy is used only to load that array.

Every saved current and best factor is rebuilt from its raw catalogue indices. Whole Gram entries use Python integer row intersections; column violations use a separate literal scalar product. The complete event logs are replayed as recorded selections, independently scoring every coordinate update and post-kick state and binding all non-RNG sweep checkpoint fields. Seed initialization and the final/sweep RNG identities are checked; intermediate RNG states are parsed but not replayed.

The review does **not** recompute all 31,110 replacement scores at every update. Consequently it does not approve minimum-choice optimality, exact tie counts, random selection among ties, or the producer's 248,880,000 candidate-evaluation count as a separately reproduced calculation. These limitations do not affect independent verification of every saved object and logged selected score. The exact minimum among saved and logged selected states is reported; it is not a global lower bound.

Controls include the genuine SRG243 factor with exact zero against its own correct Gram, an independent scalar product check, a corrupted entry, a synthetic fixed-L factor with zero against its own Gram, malformed binary/domain inputs, and altered saved-score/factor/Gram/cap/index artifacts. None is represented as a Conway99 factor.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_all_triple_descent.py --out acceleration/results/20260930_independent_review/hadamard_all_triple_descent
```

Use a new output directory for replay. No native search, publication or ledger modification is performed.
