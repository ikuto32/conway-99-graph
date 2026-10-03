# Candidate exact coupling between residue and integer energies

Producer: /root/structural. SOURCE/PAPER ONLY; no executed controls or claim
promotion. This new statement is separate from the preserved residue design
and complete-equivalence proof. Independent ROOT review is required.

For every simple symmetric zero-diagonal 99-by99 adjacency matrix of integer
degree14, put r_uv=(A^2)_uv+A_uv-2 for u<v, F3=sum1[3 does not divide r_uv]
and E=sum r_uv^2, with both sums over all4851 unordered pairs. Then

 F3 <= E <= 28*F3.

The assertion has no lambda1, linear-triple, target existence, automorphism or
incidence-rank premise. It is only an exact relation between these two metrics
on the same feasible domain, not a target exclusion or search guarantee.

Exact regularity gives sum_[v!=u] r_uv=182+14-2*98=0 for every u. Consequently
sum_[u<v] r_uv=0. Simplicity bounds each common-neighbor count by13 at an edge
and14 at a nonedge. Thus -2<=r_uv<=12. Write P for the sum of positive
residuals and N for the sum of the magnitudes of negative residuals; P=N.
For positive r, r^2<=12*r. For negative r, r^2<=2*|r|. Therefore
 E<=12P+2N=14N.
Every negative residual is -1 or -2 and is counted in F3. Hence N<=2*F3,
which proves the upper bound. Every counted residue violation has a nonzero
integer residual and contributes at least1 to E, proving the lower bound.

There is also an exact histogram constraint. Let q1,q2 count unordered residuals
congruent to1,2 modulo3 respectively. Then F3=q1+q2 and q1+2q2 is divisible
by3 because the full integer residual sum is zero. Thus q1-q2 is divisible
by3. In particular F3=1 is impossible; if F3=2, both histogram counts equal1.
The same congruence holds in each full vertex row. These are arithmetic
necessities, not sufficiency or claims that such small defects are realizable.

These relations provide cheap independent score/cache falsification conditions
for a future native engine. Any reported scores or residue histograms violating
them are corrupt on the recorded domain. They do not validate a cache on their
own. The full dense common-neighbor computation remains required for calibration,
and a candidate graph must pass the independent full integer SRG validator.

The row-sum step requires exact degree14 and order99. Matrices with only ternary
degree congruence, variable degree, another order or a partial pair census do not
have the asserted zero residual sum. The bound12 uses simple binary adjacency;
weighted or directed matrices are outside this statement. No finite fixture
passing these inequalities is described as proof of their universality.
Novelty and external review are UNKNOWN. Overall search coverage: UNKNOWN;
no validated denominator.
