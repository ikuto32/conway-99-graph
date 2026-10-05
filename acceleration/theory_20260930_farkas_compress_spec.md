# Thirty-second exact Farkas simplification scout

Freeze before execution. Input is the root's fixed connected01 exact726-by4067
binary LP matrix and integer Farkas candidate from hadamard_support_lp_dual_repair.
Independently recompute every original column dot and rhs dot before using it.
No LP/SAT solver, floating arithmetic or changed scope is allowed.

Retain only666 Gram weights, and recompute each of60 one-hot weights as the
negative minimum Gram score of any option in that column. This is the optimal
one-hot repair for these Gram weights and makes every exact column dot>=0.
Try deterministic rounding divisors {1,2,5}times10^k, k=0,...,8, in increasing
order, and thresholds0,1,2,3, setting rounded coefficients of magnitude at most
the threshold to zero (threshold0 leaves nonzero weights unchanged). Zero rows
with no matrix entries contribute nothing and may be dropped. Divide all final
weights by their gcd. Accept only all4067nonnegative column dots and strictly
negative exact rhs dot. Rank successful candidates by maximum absolute full
weight, then number of nonzero Gram weights, then full l1norm.

From the best rounded candidate, make at most one pass through nonzero Gram
weights ordered by increasing magnitude then rowID, trying to zero each while
retaining exact contradiction. Then attempt replacement by its sign when its
absolute value exceeds1. Preserve every attempted sparse vector, repaired
onehot weights, rhs and accepted/rejected verdict; always verify against the
original exact matrix. Stop at30seconds and keep the best complete candidate.

Calibrate feasible and infeasible tiny LPs, a wrong original column dot and
opposite-sign noncertificate. Save coefficient tables and per-column option
minima to make a short weighted-sum explanation possible. Failure to find a
simple certificate is not refutation. Every new certificate remains CANDIDATE
for a different agent to audit. No further coloring CNF or research solve.
