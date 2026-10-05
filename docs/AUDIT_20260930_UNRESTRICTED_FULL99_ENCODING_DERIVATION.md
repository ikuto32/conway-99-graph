# Independent unrestricted full99 encoding and coverage derivation

Claim proposed: `C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING`, revision 1.
This new claim does not broaden or replace the earlier conditional eight-family
claim. Its exact artifacts must pass the complete independent checker.

For a symmetric binary zero-diagonal matrix satisfying
`A^2 = 12I - A + 2J`, the diagonal gives degree 14 and the off-diagonal entries
give one common neighbor on edges and two on nonedges. Choose any root `r`.
Every vertex of `N(r)` has precisely one neighbor in `N(r)`, because its common
neighbors with `r` number one. Thus `N(r)` is seven disjoint edges. Order and
orient these seven edges arbitrarily, and label their vertices 1 through 14.
The root receives label 0.

Each of the 84 vertices outside the root and its neighborhood has exactly two
neighbors in `N(r)`. They cannot form a matched pair: that pair would then have
two common neighbors, the root and the outside vertex. Conversely, every pair
from different matching edges is nonadjacent, already has the root as one
common neighbor, and has no common neighbor within `N(r)` since that induced
graph is a matching. Its unique other common neighbor is outside. Therefore
outside vertices correspond bijectively to all `C(14,2)-7=84` cross-matching
pairs. Assign labels 15 through 98 in the stated pair order.

This argument supplies a permutation of any target graph. It never asserts
that the permutation is an automorphism of that graph. All 14 root incidences,
seven inner matching edges, and 168 outside-to-inner incidences are prescribed:
189 positive edges. Root and inner vertices already have degree 14; their
remaining incidences are absent. All 3,486 unordered pairs among the 84 outside
vertices remain free, including every possible overlap pattern. No K choice,
outer absence, branch condition, or Gram cut is introduced. This independently
rederives the coverage premise of `C-ROOT-SCAFFOLD-NORMALIZATION` revision 1.

The independent checker constructs these fixed and free states directly. It
checks all 9,801 matrix entries and the complete primary-variable bijection.
Every degree row is the exact sum of the corresponding adjacency entries.
For each of 4,851 unordered pairs `(u,v)`, it reconstructs the polynomial
`sum_w A[u,w]*A[v,w] + A[u,v]`. Every unknown product receives a Boolean
equivalence gate; constant factors are evaluated exactly.

Cardinality rows use states `t(i,j)` meaning at least `j` of the first `i`
input variables are true. Boundary states are `t(i,0)=true` and
`t(0,j)=false` for positive `j`. Induction on `i` proves
`t(i,j) = t(i-1,j) OR (x_i AND t(i-1,j-1))` exactly. Thresholds only through
`k+1` are required to express at most `k`; exact `k` additionally asserts the
`k` threshold. Missing states with `j>i` are false. Every gate is bidirectional,
and its Boolean truth relation is checked independently by enumerating all
truth assignments and deriving prime implicates, rather than importing the
producer's clause templates. Constant and input-alias folds are checked with
their exact Python Boolean/integer types. Fresh variable order is checked,
so these acyclic functional gates give a unique auxiliary extension for every
primary assignment obeying the rows. Trivial caps are folded only when their
bound exceeds the exact number of inputs; equality rows are not weakened.

For any symmetric binary graph with 99 vertices and all degrees 14,
there are 693 edges. Double counting the common-neighbor sums over unordered
pairs gives `99*C(14,2)=9009`. Consequently the sum of all cap left sides is
`9009+693=9702=2*C(99,2)`. If every cap is at most 2, each must equal 2.
The exact degree and common-neighbor equations are therefore precisely
`A^2=12I-A+2J`, including the diagonal. Conversely a target graph satisfies
all these rows. Combined with the preceding normalization, the exact saved
CNF is satisfiable if and only if the unrestricted Conway-99 target exists.

This is an encoding and coverage theorem, not a solver result or a resolution.
A SAT assignment still requires independent complete decoded graph validation.
An UNSAT assertion requires the exact full input, a complete proof artifact,
and an independently authenticated checker replay. No normalization branch
counts are used as a fraction of the remaining mathematical problem.

The new checker reuses the already independently authored truth-table gate
checker from `audit_20260930_eight_full99_cnf_v1.py`, and explicitly records
that shared checking component. It imports no producer implementation. The
scope construction, coverage proof, and full raw clause comparison apply to
the new unrestricted artifact. All earlier source files and reports remain
unchanged. Finite rook9 and corrupted-fixture controls calibrate bookkeeping;
they do not replace the universal proof above.
