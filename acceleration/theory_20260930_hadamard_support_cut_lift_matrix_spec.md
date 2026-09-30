# New selected parity branch: exact lift matrix and cheap linear screen

This is a fresh experiment after the sixty-cut parity SAT outcome. Preserve the
old selected branch, its failed CNF build, and its independently checked six-row
obstruction without modification. This new experiment belongs to the later
wave19 cohort and must not enter the frozen wave18 publication.

Selection: use all twenty patterns in the first independently checked SAT
assignment of the strengthened formula. Use the independent projection
f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c,
directly bound by gate
02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a.
No pattern is chosen, discarded, or adjusted after looking at the lift.

Enumerate all 6^6 coordinate permutations in S3, keep those whose three
six-letter color words contain two occurrences of every color, sort the three
words, and remove exact duplicates. The frozen criterion expects 900 labelled
objects and 150 unordered triples. Filter these by each selected normalized
parity pattern. Every retained triple assigns its increasing words to increasing
column labels in the corresponding identical-support group; this uses only the
previous independently audited column relabelling. No target automorphism is
assumed. No independent checking implementation is imported.

Construct all 666 exact upper-triangular Gram rows directly from the lifted
column sets. Each option contributes only 0 or 1 because balanced columns in one
group are disjoint. Save an exact nonnegative-variable system containing twenty
group normalization equations and all 540 positive off-diagonal Gram equations.
Verify that omitted zero Gram rows are identically zero and that each diagonal
row equals the sum of its ten containing group normalizations. Save complete
domain mappings, full row metadata, and exact coefficient-column lists in the
existing exact_model.json schema. No coefficient is floating point.

First report every positive-RHS equation having zero available terms. If any
exists, preserve a single-row integer Farkas certificate and all relevant raw
coefficients. A missing empty row only means this cheap obstruction was absent.
Then test, without optimizing, the explicitly prescribed uniform rational
weights 1/domain_size for every selector in each group. Use a common integer
denominator and save every exact row residual. If all residuals vanish, this is
only a candidate rational solution of the nonnegative equality relaxation.
It does not supply integer selections, the inter-group column caps, a binary F,
or a residual graph. A failed uniform test is not an infeasibility certificate.

Controls use a known half-weight feasible equality and deliberately corrupted
numerator/RHS cases. The complete local enumeration supplies local positive
controls; none is advertised as a research factor. Independent exact matrix and
certificate review is required before promotion.

Limits: one exact build, thirty seconds elapsed and 8 GiB sampled peak process
working set; zero optimizer or SAT calls. Preserve any exception and partial
outputs. Record source commit, exact command, locked environment, raw and gate
hashes, counts, all output identities and the actual result. No ledger, Git,
historical file or publication catalog changes.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_support_cut_lift_matrix.py --out acceleration/results/20260930_hadamard_support_cut_lift_matrix
```
