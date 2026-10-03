# Seven exceptional groups: frozen necessary-kernel census

Question: which seven-element subsets of the twenty literal fixed Hadamard supports can carry nonzero deviations at every nominated group? The population is all C(20,7)=77,520 subsets in lexicographic order. This is a full-Gram necessary marginal relaxation only, with no column-cap premise, no actual factor or target graph, and no automorphism assumption.

Use the previously checked equations H delta=0, where H has a leading one row and twelve support-incidence rows. Every integer deviation is at least -1, and its sum across the three fibres is zero. Full column rank forces balance. If any coordinate of every vector in a complete kernel basis vanishes, that nominated group is balanced, regardless of kernel dimension. Exclude such subsets as impossible for exactly seven exceptional groups.

For a one-dimensional kernel, write its primitive integer generator c and save a Bezout certificate. Every integer deviation is t c with integer t. If c has full support, its seven nonzero entries sum to zero, so at least one has absolute value at least two: seven signs of magnitude one cannot sum to zero. The lower bound c_i t >= -1 forces all fibre values of t to one side of zero. Their sum is zero, hence all vanish. This excludes every remaining rank-six subset. Do not extend this one-dimensional argument to larger kernels. Retain every other subset without claiming feasibility.

Save a nonzero rank-size minor, a complete independent integer null basis and all classifications. Exact Fraction/Bareiss arithmetic only. The rank helper is explicitly shared with the earlier producer; this is not independent verification. Before research enumeration, run its exhaustive 512 binary 3x3 controls, and new seven-column controls for full rank, a full-support odd relation, a zero kernel coordinate and a retained kernel of dimension at least two. Deliberate corruptions must be rejected.

Resource limit: 240 seconds of enumeration per invocation, tested at each completed chunk of at most 2,000 subsets. Complete chunks and immutable checkpoints permit resume into a fresh output directory using an explicit checkpoint SHA256. Resume authenticates all prior chunk identities, fixed sources and population, and continues strictly after the recorded lexicographic prefix. No solver calls. A stopped prefix is not a full census. Expected runtime is under a minute, but no speed claim is made.

Success is a complete exact classification of the frozen population; exclusions remain CANDIDATE until independently checked. Nonzero retained counts do not falsify the necessary theorem and do not establish a construction. A bad rank, null vector, population identity or corrupted control stops the run without promotion. Preserve every failed invocation.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_seven_exception_census.py --out acceleration/results/20260930_hadamard_seven_exception_census
```

Resume uses `--resume-checkpoint PATH --resume-checkpoint-sha256 SHA` and a new `--out` path. Outputs include source commit, commands, cwd, tool versions, exact input/output hashes, progress, completed-population counts, and a candidate-only summary.
