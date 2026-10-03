# Fixed connected01 support: cheap selector LP falsification

Use exactly the saved Hadamard connected01 support and its filtered colour
domains, SHA256 `2e839fda408da18e3689ffef00de647644375a000d308f4ea306b2cbdfa37e49`.
Selection is the first surviving support in the already frozen order
connected00, connected01, connected02, connected03, six_prism.

Question: do nonnegative real selector weights satisfy one unit sum for each
of60columns and all666unordered entries of the prescribed36x36 Gram matrix?
Each integer colour selection is feasible in this relaxation. Y-column caps,
integrality, residualD and target equations are absent. A feasible LP is not
a factor, and an infeasible LP could exclude only this fixed support.

One30second HiGHS simplex attempt, one thread, presolve off, seed0; numerical
primal and dual tolerances1e-7. Calibrate on known feasible and infeasible
tiny equality systems first. Preserve the entire exact sparse matrix,
right-hand side, numerical solution/ray, options, versions and log.

Numerical status never certifies a claim. Try bounded-denominator rational
reconstruction with denominator at most1000000. A primal is a candidate
certificate only when Ax=b and x>=0 hold exactly. A dual ray is a candidate
certificate only when yA>=0 and yb<0 hold exactly (either orientation tried).
Independent reconstruction of the scope, exact matrix and certificate is
required before promotion. No retries or automatic resource extension.
