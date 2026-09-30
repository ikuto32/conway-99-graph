# Six exceptional groups: global marginal rank census

Freeze before execution. Population is every six-element subset of the20 literal fixed Hadamard supports, checked as C(20,6)=38,760. Allocation120 seconds, exact integer/Fraction arithmetic, no native/local-factor solver, no ledger edit. The task classifies necessary global marginal kernels; no remaining subset is claimed realizable.

Let H have a leading all-one row and the twelve support-incidence rows. For each coordinate a and fibre f, extend its deviation delta[g,a,f]=t[g,a,f]-1 by zero on groups not containing a. The previously independently checked full-Gram marginals imply H*delta=0: the a-row repeats the leading row, its matching mate has no incident groups, and every other coordinate supplies a summed-Gram equation. Restrict H to the six nominated exceptional groups.

Rank6 forces all deviations to zero. Rank5 has a one-dimensional rational kernel with primitive integer generator c. Every integer deviation is z*c with integer z because gcd(c)=1; a saved Bézout coefficient vector witnesses this step. If c has a zero coordinate, that nominated group is balanced for every a,f, so exactly six exceptional groups are impossible. If a coefficient has absolute value at least2, the count bound delta>=-1 forces all three integer z_f to one side of zero, while sum_f z_f=0; hence all are zero. These exclusions use integer counts, not floating-point rank or a generic real nullspace.

The only remaining rank5 possibility has full-support c∈{±1}^6, with exactly three signs of each kind because the leading row sums to zero. At any nonzero coordinate deviation all six supports must contain the coordinate. Group fibre quotas imply sum_a z[a,f]=0, so their common support must have at least two coordinates. Save such subsets as necessary candidates only. Rank4 or lower, including a kernel of dimension at least two, is explicitly retained unresolved; do not apply the one-dimensional argument there.

For all38,760 subsets save a literal nonzero rank-size minor and a complete linearly independent integer null basis (with distinct free-coordinate pivots). The minor proves the lower rank bound and the basis proves the upper bound. Rank5 records include primitive c, Bézout coefficients, common support and exact classification. Save compressed JSONL records plus a plain necessary-candidate list and rank/class counts. Input and output hashes, source commit, command, environment, controls and timed progress are retained. If allocation is exceeded, preserve failure/progress and do not report a complete population.

Controls: all512 binary3x3 matrices compared against exhaustive minor ranks; a six-cycle incidence matrix with full ±1 kernel; a five-dimensional augmented cube simplex relation containing a coefficient magnitude3; a rectangle plus independent columns whose primitive kernel has zeros; six vertices of the3-cube with rank4/kernel2 retained; altered minor/null/Bézout identities rejected. Synthetic count profiles test both the allowed ±1 shape and the integer one-sided obstruction, with no claim these controls are research factors.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_six_exception_census.py --out acceleration/results/20260930_hadamard_six_exception_census
```
