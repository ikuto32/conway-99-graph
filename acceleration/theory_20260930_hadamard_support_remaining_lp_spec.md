# Remaining frozen Hadamard support LP batch

Run the three remaining previously selected supports in this exact order:
connected02, connected03, six_prism. Connected00 has an independently checked
empty-domain obstruction; connected01 has an integer Farkas candidate under
separate review. This batch does not change any support, domain or old run.

For each case use the same nonnegative selector relaxation with60one-hot
equalities and666prescribed Gram equalities, omitting integrality, column
pair caps and residualD. One30second HiGHS simplex attempt per case, one
thread, seed0, presolve off, primal/dual tolerances1e-7, no retries.

Calibrate the shared solver/certificate path on tiny feasible and infeasible
systems before the batch. Save each exact sparse integer matrix and complete
numerical result. Try the original rational reconstruction (denominator cap
1000000), retaining failure. If a numerical infeasibility ray is available,
also try the already frozen fixed scale1000 integer rounding and nonnegative
one-hot-row repair. Accept only exact integer yA>=0,yb<0 as a candidate
exclusion certificate. Exact Ax=b,x>=0 is only a continuous primal witness.

Independent checking must reconstruct all allowed colorings, every equation
and each certificate. Numerical status alone and absence of an exact
certificate establish nothing. All conclusions are restricted to the three
literal saved supports, never all Hadamard choices or all factors of a core.
