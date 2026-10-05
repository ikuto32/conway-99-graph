# Independent eight-exception marginal census

This is a necessary-condition census on the one pinned six-prism Hadamard support. It does not use outside-column caps, a graph automorphism, or a symmetry restriction on an unknown solution. It does not establish feasibility of retained subsets.

For support group g and coordinate a in its six-element support, let `delta[g,a,f]` be the number of its three columns selecting fibre f at coordinate a, minus one. It is an integer at least -1. Set it to zero outside that support. Summing over fibres gives zero. Each column has two entries in each fibre: this follows from the prescribed Gram and aggregate L by the exact identities `sum k=120`, `sum k^2=240`, hence `sum (k-2)^2=0` over the sixty columns. Consequently each group's sum of deviations over coordinates is zero for each fibre.

The separately verified full-Gram marginal theorem gives the leading row and every nonmatched-coordinate incidence row of `H delta=0`, where H has a leading one row followed by the twelve support-incidence rows. Restricted to supports containing a, the a row duplicates the leading row and the mate-of-a row vanishes. This explicitly establishes all thirteen H rows, including on coordinates absent from some nominated groups. The audit compares all twelve old marginal matrices with this raw global matrix.

For an eight-element nominated group set, a nonzero rank-size minor and a complete independent integer null basis establish the exact rational rank. Full rank forces every deviation to zero. A coordinate that vanishes in every vector of a complete null basis is zero in every null vector, so that nominated group is balanced. Either situation contradicts *exactly* eight unbalanced groups.

If the kernel is a line with primitive integer generator c, a recorded Bezout identity proves that every integer vector on this line is `t*c` with integer t. If a coefficient is at least 2, `t*c_i >= -1` forces `t >= 0`; a coefficient at most -2 forces `t <= 0`. For a fixed coordinate the three fibre multipliers sum to zero, because some c_i is nonzero and the fibre deviations sum to zero. The one-sided constraint therefore forces all three multipliers to vanish. This holds at every coordinate.

Otherwise a full-support primitive line has only coefficients +1 and -1. For any coordinate outside the intersection of all eight supports, an absent group's zero deviation and its nonzero c_i force t=0. Thus nonzero deviations are supported only on the common coordinates. If there are no common coordinates, all deviations vanish. If there is one, the groupwise coordinate sum zero forces its coefficient to vanish too. With two common coordinates this argument does **not** exclude the line: opposite multipliers at the two coordinates provide a nonzero count-level control. It is not a factor construction. No line argument is applied to a higher-dimensional kernel.

All 125,970 lexicographic eight-subsets, all 63 chunk intervals, every prefix checkpoint and all retained records are checked. The independent modular determinant path uses a prime greater than twice the binary minor's Leibniz bound, so the declared bounded integer determinant is uniquely determined by its residue. Null equations and independence prove the complementary rank upper bound. This reuses a pinned earlier independent checker, not the producer's Fraction/Bareiss helper.

Controls include all 512 binary 3 by 3 determinant cases checked against permutation expansion, full rank, forced zero, a large primitive line, a retained higher-dimensional kernel, alternating sign lines with zero/one/two common coordinates, and malformed determinants, minors, null bases, Bezout identities, classifications and coverage.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_eight_exception_census.py --out acceleration/results/20260930_independent_review/hadamard_eight_exception_census
```

Use a new output directory for replay. Exact classification here is not a measure of target-wide search coverage.
