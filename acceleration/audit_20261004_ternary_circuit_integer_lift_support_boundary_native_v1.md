# Independent written audit: integer lifting and the specified 17-point support

Mathematical producer /root/structural; independent verifier
/root/native_driver. WRITTEN PASS for the three exact statement fields in
candidate361f7272 and paper5b4c3f45. Parent requested revision1, but the raw
candidate contains no claim ID or explicit revision field; this audit invents
no registry identity. A separate metadata identity is needed for registration.
No mathematical worker, import, executable fixture, enumeration, formal or
external check occurred. The bound report supplies final verification time;
the written-review start was not separately timestamped.

## General circuit consequence, derived independently

Let E be the integer matrix of the w selected columns and let every column
sum to the same nonzero integer c. A ternary matroid circuit is nonempty,
has rank w-1 and a one-dimensional kernel whose nonzero generator u has
full support. Its nonzero (w-1)-minor modulo3 is also nonzero over Q,
so rank_Q(E) is at least w-1.

Assume rational dependence. Then rank_Q(E)=w-1 and a primitive integer
vector z generates its rational kernel: clear denominators of a rational
generator and divide all coordinates by their gcd. Since gcd(z)=1, at
least one coordinate is not divisible by3. Thus z mod3 is a nonzero
multiple of u. On the other hand

    0=1^T E z=c sum(z)

over the integers, so sum(z)=0 because c is nonzero. Hence sum(u)=0,
contrary to the hypothesis. Therefore rank_Q(E)=w and E^T E is positive
definite. This works for w=1 as well: a ternary loop circuit can be a
nonzero integer column divisible by3.

All w-minors are zero modulo3, since the ternary rank is w-1. Each integer
w-minor is divisible by3. Cauchy-Binet expresses det(E^T E) as the sum of
their squares, and rational full column rank makes the sum positive. It
is a positive multiple of9. No cancellation/sign argument permits a
universal extra factor3, nor an upper/lower circuit-weight improvement.
If c is not divisible by3, the unbalanced hypothesis is impossible after
summing E u modulo3; the result remains valid, then vacuously.

The hypothesis boundaries are substantive. With E=[1,2], u=(1,1) is an
unbalanced ternary circuit but the rational rank is1: equal column sum
is missing. With E having rows (1,2) and (-1,-2), column sums are both
zero and the same failure occurs. Circuit minimality also matters:
rows (1,1,3) and (2,2,0) give common column sum3 and full-support
ternary dependence (1,2,1), whose sum is1, but rational rank2 rather
than3. This selected set is not a circuit because it contains a ternary
loop and a two-column dependence.

For Q=J4-I4, Qj=3j, ker_F3 Q=span(j), sum(j)=4=1 and Q is rationally
invertible. Q^T Q=I+2J has eigenvalues9,1,1,1 and determinant9. Thus
divisibility27 is not universal. This example violates lambda-one
triangle geometry and challenges no target circuit-size theorem.
Conversely the one-column E=(3,3,3)^T has Gram determinant27 and Smith
factor3. Gcd of maximal minors3 does not force the Gram valuation to be
exactly2. Neither the candidate nor this audit makes that strengthening.

## Symbolic family reduction without enumeration

Use the disjoint points and twelve column order in the frozen paper: seven
negative coefficients h0 through h6, and five positive coefficients y0
and y_a. Only the listed columns enter this matrix; extra ambient triangles
and graph edges are not assumptions. The choices are ell in L, r in R,
sigma:A->B and rho:A->F bijections. Their literal universe is
3*3*4!*4!=5184; no population or isomorphism algorithm was executed.

The ell and r equations are h5+y0=0 and h6+y0=0. Each free point belongs
to one side and exactly one positive column, so its equation has a unit
pivot y_a and gives y_a=y0 after the appropriate side equation is
subtracted. The rows a1,a3 then give unit pivots h1,h2; rows b1,b3 give
unit pivots h3,h4 irrespective of sigma. All four become -y0. The row x
gives unit pivot h0=-y0. These eleven pivots use only integer row additions,
subtractions, swaps and unit column elimination; none divides by3.

For clarity, after eliminating these eleven variables, all six remaining
rows have the following coefficient of the remaining column y0:

| Row | Residual coefficient |
| --- | --- |
| s | -3 |
| t | -3 |
| a2 | 0 |
| a4 | 0 |
| b2 | 0 |
| b4 | 0 |

Replacing t by t-s leaves only the -3 row. Consequently the whole
17-by12 integer matrix is equivalent by unimodular row/column operations
to a diagonal block I11,3 with five zero rows. This is a direct ordinary
rectangular Smith reduction, not symmetric congruence of a Gram matrix.
It proves rational rank12, ternary rank11 and cokernel Z^5 plus Z/3Z
for every choice, without sampling all5184 choices.

The selected twelve rows ell,r,F,a1,a3,b1,b3,x,s contain exactly the eleven
unit pivots and the -3 row. They are distinct because the point sets are
disjoint, the two endpoints are outside F and A/B anchors belong to their
different named sets. Their 12-by12 determinant is plus or minus3.
The actual sign can change with row/column order and is not claimed fixed.
Every maximal minor is divisible by3, while this one has absolute value3,
so their gcd is3. The independent full reduction gives the claimed eleven
unit Smith factors as well, avoiding any hidden minor-count assumption.

Modulo3 y0 is free and all positive coefficients equal y0, all negative
coefficients equal -y0. This is the only direction; for nonzero y0 every
coordinate is nonzero, so no proper subset has a dependence. It is a
genuine ternary circuit with five positive and seven negative coefficients,
whose sum is -2y0=y0 modulo3. Over Q the -3 equation forces y0=0, hence
there is no exact nonzero integer relation on these twelve columns.

## Lifting shortcut and complete-versus-partial boundary

For any complete triangle incidence N, sum(N U)=3 sum(U). An unbalanced
word u cannot have an exact integer relation lift, since sum(U)=0 would
reduce to sum(u)=0. It cannot have a modulo9 relation lift either: NU
divisible by9 forces 3 sum(U) divisible by9, thus sum(U)=0 modulo3.
The newly accepted global pairing already predicts this obstruction.
Treating expected nonlifting as a contradiction would wrongly discard
the necessary unbalanced word itself.

The partial D has rational left-kernel dimension17-12=5 and ternary
left-kernel dimension17-11=6. Any primitive nonzero exact integer left
relation has nonzero ternary residue and certainly lifts modulo9; such
relations exist by rational rank12 and clearing denominators. Therefore
the global zero-left-radical/nonlifting conclusion does not hold for this
partial matrix. It cannot have a full-row-rank right inverse DP=210I17.
Extra full-incidence columns may remove partial left dependencies, and
none is proved persistent through every target completion.

For a balanced complete right word, the exact global integer lift can
use the remaining columns and larger coefficients. An asserted lift on
the original support would be an additional condition, not a consequence.
No inference here refutes the global mod9 theorem, assumes a target
automorphism, forces this family to occur, establishes inducedness or
excludes completion. The relevant mod9 claim remains intact.

## Bounded historical comparison and written-check inventory

All five pinned paper sources were whole-read and their small hashes
matched. The old17-circuit paper already proves ternary rank11/minimality
for its literal member; the four-class family paper supplies the same
parameterized universe. Their geometry, isomorphism and interlacing
conclusions are not newly approved by this arithmetic boundary review.
The identity-permutation triangle-core paper already supplies the stated
39-point local construction at fibre12 and leaves60 target vertices
unspecified. It makes no without-loss-of-generality or target automorphism
claim. This is bounded overlap comparison, not an exhaustive novelty check.

The final bound report counts20 paper-only checks: rational-rank lower
minor; primitive integer generator; nonzero reduction; constant-sum
contradiction; one-column boundary; Cauchy-Binet positive9 divisibility;
Q determinant9; unequal sums counterexample; zero common sum
counterexample; nonminimal full-support counterexample; Gram27 versus
Smith3 boundary; eleven symbolic unit pivots; six-row residual table;
distinct literal selected rows/determinant sign; full rectangular Smith
and cokernel; unique all-nonzero ternary circuit/sign count;
unbalanced full exact/mod9 obstruction; partial left-kernel/right-inverse
boundary; support/sign/completion restrictions; whole bounded archive
overlap. All20 are written derivations, not executed controls.
