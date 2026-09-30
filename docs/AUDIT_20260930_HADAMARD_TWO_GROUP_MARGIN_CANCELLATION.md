# Fixed-support row-margin cancellation

Let the twelve coordinates be a=0,...,11 and the three fibres f=0,1,2. The
frozen12-by60 matrix L has twenty distinct supports S_g, each of size six and
each repeated in exactly three raw columns D_g. The sets D_g partition all60
columns. Direct enumeration establishes that each coordinate occurs in ten
supports.

For any binary matrix F with36rows and60columns satisfying
sum_f F[12f+a,d]=L[a,d], define the embedded deviation

    Delta_g[a,f] = sum_(d in D_g) F[12f+a,d] - 1_(a in S_g).

This is a12-by3 matrix, zero outside S_g; its restriction to S_g is the6-by3
coordinate/fibre count matrix minus one. For each a,f,

    sum_g Delta_g[a,f] = sum_d F[12f+a,d] - 10.

Thus row sums10 force the twenty deviations to sum to zero entry by entry.
For binary F the prescribed Gram diagonal10 implies these row sums. This
argument needs neither the other Gram entries nor an UNSAT result.

A group is balanced exactly when its deviation is zero: every coordinate then
uses each fibre once in its three columns. There cannot be exactly one
unbalanced group, since its embedded matrix would have to equal zero. With
exactly two, Delta_g=-Delta_h. A coordinate outside S_h has Delta_h zero, so
Delta_g must vanish there as well; reversing g,h gives support confined to
S_g intersect S_h. In particular disjoint supports cannot be the only two
unbalanced groups. This is a conditional necessary statement, not a claim that
all factors are balanced or that such two-group patterns extend to full factors.

The proposed premise that all distinct supports meet in zero or three
coordinates is false. Independent literal set intersections over all190 pairs
give counts {0:1,1:16,2:58,3:60,4:47,5:8}. The first two groups have supports
{0,2,4,6,8,10} and {1,3,4,6,9,11}; their intersection is {4,6}. This exact
counterexample is preserved and no part of the cancellation proof uses the
false premise.

The controls include a literal36-by60 factor with all groups balanced and a
second literal factor with exactly groups0and1 unbalanced and opposite
deviations on coordinates4and6. Both satisfy the exact support, row margins
and per-column two-per-fibre quotas. The latter intentionally fails the full
Gram matrix, with every mismatch saved. Removing one cancelling change breaks
the row margins. Malformed matrices and changed support/deviation data are
rejected separately.

An additional strengthening, recorded as CANDIDATE pending separate review,
uses the column quotas: each group has six entries per fibre across its three
columns, so sum_a Delta_g[a,f]=0. A deviation supported on only one coordinate
must then be zero. Consequently an exceptional pair also cannot have a
singleton intersection. This removes the17 fixed group-pair choices of sizes
zero or one from that weaker row-margin population; it is not target coverage.

No relabelling or automorphism is needed. Coordinates and raw group columns
retain their saved labels. No full-factor or residual graph construction and
no general target exclusion is asserted.
