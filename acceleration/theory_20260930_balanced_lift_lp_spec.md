# Cheap continuous screen of the first checked parity lift

Select the balanced color-lift model for the first independently checked
nonconstant parity assignment. Test only its nonnegative one-hot/Gram
equality relaxation; integrality, inter-group column caps and residual D
are omitted. The whole support and other parity assignments are not covered.

One research LP call: HiGHS 1.15.1 simplex, presolve off, one thread, seed 0,
20-second solver limit, primal/dual tolerances 1e-7. Two tiny known feasible
and infeasible controls run first. Preserve all numerical vectors/statuses.
No retry. A floating result is guidance only.

First attempt the pre-existing exact rational reconstruction with denominator
at most 1,000,000. If no exact certificate results and a dual ray exists,
try both ray signs at the predetermined integer scales 1, 10, 100, 1000,
10000 and 1000000, in that order. For each candidate raise each of the twenty
one-hot multipliers by the smallest nonnegative integer that makes every
column product nonnegative. Save every trial, including failures; do not
alter thresholds after seeing the result. Accept only exact integer
nonnegative column products and a strictly negative right-hand-side product.

An exact candidate still needs independent reconstruction of the complete
raw coloring domain, matrix and all certificate products. A feasible
relaxation supplies no integer factor or target graph. A failed rational
reconstruction, timeout or numeric infeasibility is not an exclusion.
