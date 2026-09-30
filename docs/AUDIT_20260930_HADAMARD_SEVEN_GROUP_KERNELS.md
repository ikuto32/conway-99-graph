# Seven exceptional groups: independent necessary-kernel review

Let the twenty fixed six-coordinate supports be the columns of their incidence
matrix, and prepend a row of ones to obtain (H). For each core coordinate (a)
and fibre (f), set δ(g)=t(g,a,f)-1 on groups containing (a), and zero
elsewhere. The independently checked full-Gram marginal identities imply

\[
H\delta=0,\qquad \delta_g\in\mathbb Z,\quad \delta_g\geq-1,
\quad \sum_{f=0}^2\delta_{g,a,f}=0.
\]

The bridge to (H) is literal: for each (a), the ten incident group columns
restrict the leading row to ones, the row for (a) duplicates it, the row for
its matched coordinate is zero, and the other ten rows are the already checked
marginal matrix. No outside-column-cap assumption is needed.

Fix seven nominated exceptional groups and restrict (H) to these columns.
Full column rank forces every deviation to vanish. If a coordinate vanishes on
a complete rational nullspace basis, it vanishes on every deviation vector;
that nominated group is balanced, contrary to being exceptional. This test
requires the entire basis, not a zero in one chosen basis vector.

Suppose the kernel is one-dimensional and has a primitive integer generator
c with no zero entry. Its entries sum to zero because (H) has a leading one
row. Seven nonzero entries of magnitude one cannot sum to zero, so some
\(|c_j|\geq2\). Every integral kernel vector equals (t c) with *integer* (t):
a checked integer Bézout row (b\cdot c=1) gives (t=b\cdot\delta\).
If (c_j\geq2), the integer lower bound (c_jt\geq-1) forces (t\geq0);
if (c_j\leq-2), it forces (t\leq0). For each (a), the three fibre
multipliers sum to zero, so all three vanish. This contradicts any exception.

No such scalar argument applies to a higher-dimensional kernel. Every
higher-dimensional subset with no forced-zero coordinate is retained. Retained
means only that these particular necessary tests did not exclude it.

The checker reads every lexicographically ordered septet certificate. It
reconstructs each minor from raw (H), checks its determinant independently by
modular elimination and an exact Leibniz bound, and checks all integer null
vectors literally. A nonzero projected determinant proves independence of the
whole null basis. Thus the minor and null basis establish both rank bounds;
the producer's Fraction rank routine is not imported or executed. Primitive
Bézout identities and every classification are checked separately. All chunk
boundaries, immutable checkpoint prefixes, and the final retained list are
compared with the frozen complete population \(\binom{20}{7}=77,520\).

Controls exhaust all 512 binary three-by-three matrices against a direct
permutation-determinant path, inspect synthetic full-rank/odd-line/forced-zero/
higher-dimensional examples, test the integrality and odd-cardinality
arguments, and deliberately corrupt minors, null bases, Bézout records,
classifications and coverage. No research solver, factor construction,
automorphism assumption, or general nonexistence claim is involved.
