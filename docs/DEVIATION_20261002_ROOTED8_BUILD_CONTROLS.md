# Rooted-eight build ordering and failed-source preservation

The first producer source failed at Python parsing before creating any worker
artifact. The supported receipt is
`acceleration/results/20261002_rooted8_universal5_product_model_supervisor/`:
exit 1, elapsed 0.125 seconds, deadline not reached, descendants reaped and
empty Windows Job observed. Its `stderr.log` identifies the malformed ternary
token on line 199. This was a syntax failure, not a timeout or mathematical result.

The original bytes are preserved losslessly at
`acceleration/theory_20261002_rooted8_universal5_product_model.py.failed-source.txt`,
SHA256 `06a0d69c925a23d357040305995dd9ed9a68430adc5cbf68759454e2adbbf355`.
The original and archived hashes were compared before and after the literal
path move. The failed `.py` is therefore not a maintained executable source
subject to normal source parsing; its original command path remains unchanged
in the historical receipt. V2 corrects the three ternary syntax errors and
performs an actual mutated-product-coefficient evaluation, retaining the
failure evidence rather than overwriting the source.

V2 passed a separate contained AST control before its build. Its frozen
pre-launch protocol required positive/corrupted product controls before
optimization. It executed those controls after catalogue/row generation and
completed in 62.547 observed supervisor seconds. While that build was already
running, the parent required a stronger gate before scientific building.
The worker had completed before an observed-PID stop could be applied; no other
process was stopped. The later requirement was **not** satisfied before that
already-started build, and must not be represented as having been satisfied
retroactively. No optimizer ran during either build.

Before any optimizer, a separate discovery-agent calibration now checks the
raw stored product rows using a separately written adjacency-set and complete
free-permutation counting implementation, with no producer imports. It checks
all 3,828 product rows at each of the Petersen graph's 60 ordered nonedges,
the ordered union totals 1/12/30/20, and actual altered coefficients/counts.
The supported invocation completed with exit zero in 7.047 observed seconds,
reaped descendants and an observed empty Windows Job. Records are in
`acceleration/results/20261002_rooted8_product_calibration01/` and
`acceleration/results/20261002_rooted8_product_calibration_supervisor01/`.
This is calibration by the discovery agent, not independent claim approval.
Independent catalogue coverage and complete mathematical-row audit remain
required before any target-relevant exclusion can be promoted.
