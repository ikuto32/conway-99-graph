# Independent written review: ordinary integer signed triangle one-design

This is an independent Native reconstruction of the frozen Structural signed
one-design candidate. The review is written only: no research source import,
AST extraction, matrix/backend execution, Smith computation or scientific
worker. The raw candidate and all historical evidence remain unchanged. This
claim is separate from prime-five support54, whose written report does not
approve the present conclusion.

Exact claim: C-UNRESTRICTED-TARGET-INTEGER-TRIANGLE-SIGNED-ONE-DESIGN, revision1.
Paper:
docs/CANDIDATE_20261004_TARGET_INTEGER_TRIANGLE_SIGNED_ONE_DESIGN_V1.md,
SHA256 ba19198241e3523ab0bf25dfbdc67bd522552668f420f0f63af4d3735a25b95d.
Raw:
acceleration/results/20261004_target_integer_triangle_signed_one_design_candidate01.json,
SHA256 855861ba2f0b551642fff0f1e47093b0bc6992c9a3cdd0414f3b462c9420e488.

## Exact conclusion and domain

For a complete finite simple SRG(99,14,1,2), N is the ordinary integer binary
99-by231 incidence of every actual triangle once. Its integer column cokernel
is finite and killed by30. An ordinary integer vector w exists with Nw=j99
and sum(w)=33. Every such w has odd squared norm at least33. Equality33 is
equivalent to a0/1 indicator of33 disjoint actual triangles covering all99
vertices. Existence of equality, a positive cover, an actual target, an extra
left kernel, symmetry or target resolution is not asserted.

This exact claim passes the derivation below. The construction is conditional
on an actual hypothetical complete N and uses unrestricted signed ordinary
integer weights; it does not construct N. Ring, positivity and equality-case
boundaries are essential and are retained verbatim in the report.

## 1. Recover all necessary complete geometry

Every edge has a unique third triangle vertex because adjacent common-neighbor
count is1. Each14-point vertex neighborhood is a matching, so every vertex is
on seven triangles, and incidence counting gives231 actual triangles. Thus

    Nq=7j, N^Tj=3q, NN^T=A+7I=H.

The integer adjacency identity A^2=12I-A+2J and Aj=14j follow directly from
the target common-neighbor counts and degree14. On the ordinary real j-perp
subspace A has eigenvalues3 and-4. Their multiplicities are54 and44 from
trace0 and total dimension98. Therefore H is positive definite with spectrum

    21 once, 10 fifty-four times, 3 forty-four times.

In particular N has ordinary rational row rank99 and the integer column
quotient is finite. This ordinary rank statement alone is not used to
assert any modular full rank.

## 2. Independently reconstruct the denominator210 integer right inverse

Expanding (A+7I)(6I-A) gives

    H(6I-A)=42I-A-A^2=30I-2J.

Define the ordinary integer231-by99 matrix

    P=7N^T(6I-A)+2qj^T.

Then the margins and Gram identity give

    NP=7H(6I-A)+2Nq j^T
      =210I-14J+14J=210I.

This proves that210 times every integer vertex vector lies in the integer
column lattice of N. Equivalently, every element of the finite cokernel
is killed by210. No division of an integer matrix by210, positivity of P,
or computed Smith invariant is presumed. A Smith description is optional:
each nonzero invariant factor divides210.

The same P identity is already in the pinned mod9 derivation. Its present
use remains ordinary integer, not an arbitrary 3-adic factor or merely
a congruence modulo a finite power.

## 3. Remove7 by actual modular rank and an ordinary integer lift

The exact Gram determinant is

    det(H)=21*10^54*3^44,

whose7-adic valuation is exactly1. Cauchy-Binet over the ordinary integers
expresses it as the sum of squared99-column minors of N. If N had F7 rank
less than99, every such minor would be divisible by7, so each square and
their sum would be divisible by49. This contradicts valuation1.
Therefore rank_F7(N)=99. Possible cancellation in the sum cannot destroy
the asserted divisibility49; positivity is not needed for that direction.

Full F7 row rank supplies a right inverse over F7. Take any ordinary integer
entrywise lift B of that right inverse. Then NB=I+7C for an ordinary
integer99-by99 C. This lift is not asserted to be an ordinary integer
right inverse by itself. With P as above, put

    R=30B-PC.

It is an ordinary integer matrix, and

    NR=30NB-NPC
      =30I+210C-210C
      =30I.

Thus the entire integer cokernel is killed by30. Its factors divide30, a
squarefree integer: it has no7-primary part or higher2-,3-,5-power torsion.
No claim is made about the number of factors at any prime. This conclusion
does not need a computed Smith form or a mistaken rational-to-modular
eigenvector transfer.

As an equivalent group-theoretic check, NP210 kills the group, while full
F7 rank implies its7-primary component is zero; its exponent therefore
divides30. The explicit R proof avoids any ambiguity about the coefficient
ring and constructs the required integral multiple30 directly.

## 4. Signed integer covering follows, with its precise norm boundary

Since13*7-3*30=91-90=1, define

    w=13q-3Rj.

Every coordinate is an ordinary integer and

    Nw=13*7j-3*30j=j.

Taking ordinary integer sums, each column of N has three ones, so
3sum(w)=sum(Nw)=99 and sum(w)=33. The equation is not just a field
congruence or a formal local-ring relation.

For any ordinary integer a, a(a-1) is nonnegative and even. Applied to all
coordinates of any integer solution w,

    ||w||^2-33 = sum(w_l(w_l-1)) >=0,
    ||w||^2 = 33 mod2.

Hence the squared norm is an odd integer at least33. Equality forces every
summand to0, so every coordinate is0 or1. Then Nw=j says each point occurs
in exactly one selected actual triangle, making them pairwise disjoint and
covering the99 points; the sum33 counts those triangles. Conversely such a
triangle factor gives an integer solution of norm33. Neither negative
weights nor weights greater than1 invalidate the inequality; they strictly
increase the relevant summand.

This is an equality characterization, not an existence argument for that
equality. The integer coset is nonempty by the constructed w, and a minimum
of its squared norm exists by ordinary integer discreteness. There is no
proof here that this minimum is33.

## 5. Real least norm does not replace the integer minimum

Because Hj=21j, H^{-1}j=j/21. The full real row rank gives the unique
minimum-norm real solution

    w0=N^T H^{-1}j=q/7.

Its squared norm is231/49=33/7. Every real solution is w0+h with
h in ker_R N, and w0 is perpendicular to h because it is in im_R N^T.
Thus ||w0+h||^2=33/7+||h||^2. This describes a real affine space; it does
not produce a short lattice point in the integer affine coset. The proposed
shortcut from33/7 to an attained integer norm33 is invalid.

The row7 vector q provides the integer cover of multiplicity7; R provides
an integer cover of multiplicity30. Coprimality makes a signed cover of
multiplicity1. It does not turn this Bezout combination into nonnegative
coordinates.

## 6. Independently check the six-point counter-boundary

Columns in order are123,124,135,236,125,136,234. Give them weights
(-1,1,1,1,0,0,0). At the first three points the totals are respectively

    -1+1+1=1, -1+1+1=1, -1+1+1=1,

and at points4,5,6 the selected columns124,135,236 each contribute1.
So the signed cover is exact. Weight sum2 and squared norm4 are consistent
with the six-point norm rule, whose equality floor is2.

Each column contains at least two of points1,2,3. Any two columns share one
of those points. A0/1 cover would require exactly two disjoint columns
because there are six points and column size3, but no such pair exists.

For real row rank, suppose all seven column sums on a vertex vector x vanish.
Comparing the first column123 with124,135,236 gives respectively

    x4=x3, x5=x2, x6=x1.

The remaining columns give

    x1+2x2=0, 2x1+x3=0, x2+2x3=0.

Thus x1=-2x2, x3=4x2, and9x2=0. Over Q or R this means x2=0 and all
six entries vanish. The binary incidence therefore has full ordinary row
rank6. The argument is explicitly not a modular rank claim at3.

The example really falsifies positivity from binary triple columns, full
ordinary row rank and a signed cover alone. It lacks target row7 and
lambda-one geometry; it is neither a target counterexample nor evidence
that any target lacks a triangle factor.

As a separate positive boundary, rook9's three disjoint row triangles form
a genuine0/1 cover of its nine points, sum3 and norm3. Rook's six triangle
columns, row degree2, singular Gram and different target size prevent
transferring the present exponent30 or norm33 claims to it.

## 7. Ancillary prime floors and historical overlap

For a prime p, if d=99-rank_Fp(N), integer row operations with unit
determinant at p make the last d rows p-divisible. In the congruent Gram
matrix a p factor can be removed from each of those d rows and d columns.
Hence v_p(detH)>=2d. With the exact determinant above,

    v2(detH)=54, v3(detH)=45, v5(detH)=54.

Thus the respective rank floors are72,77,72. These are floors only.
The odd3-valuation is correctly rounded down for the allowed deficiency22;
it does not give deficiency23 or rank76. They force no left dependency or
exact modular rank. The paper appropriately retains stronger/overlapping
historical binary87 and ternary77 results as comparison rather than
reapproving those unrelated claims.

The whole modular-rank audit, whole Wave23 failed-routes note, and whole
Wave168 Gram/minor-energy derivation were read in this review interval.
Wave23 already explicitly records F7 full incidence rank; that overlap is
disclosed. Wave168 already gives ordinary triangle geometry, Gram and
spectrum. The mod9 and3-adic papers were already whole-read in Native's
preceding audits and their exact pins were checked again. No p3 module
statement is silently applied to the present ordinary integer cokernel.
The comparison is bounded to these five documents, with no exhaustive
novelty or external literature claim.

## 8. Adversarial boundaries and verdict

The following hand boundaries were checked independently:

* Ordinary rank99 does not alone imply full modular rank; the exact
  determinant valuation1 and squared-minor argument supply the F7 step.
* NP210 alone leaves a possible7-primary component. NR30 needs the actual
  mod7 lift and integral C, not cancellation by dividing a matrix by7.
* The signs in R=30B-PC give exact cancellation of210C.
* The signs in w=13q-3Rj give91j-90j=j.
* Dropping the complete row7 or column3 margins invalidates the Bezout or
  sum33 steps; incomplete triangle selections are not admitted.
* A formal3-adic relation does not ensure ordinary integer w or the ordered
  norm inequality. The ordinary integer ring is an explicit hypothesis.
* For an integer a=-1, a^2-a=2, so a negative weight cannot attain equality.
  For an integer a2 the same strict increase occurs.
* The real q/7 has norm33/7 but is not an integer vector; the equality
  characterization cannot be inferred from that real lower minimum.
* The six-point binary signed-cover example has full Q row rank and no
  positive cover, checking the exact weaker-hypothesis shortcut failure.
* Its relation9x2=0 cannot be used to claim full rank modulo3.
* Rook9 supplies a known positive cover at different parameters; no target
  norm/exponent statement is transplanted to it.
* Modularity at2,3,5 is distinct from ordinary rank and F7 full rank; none
  of the floor inequalities determines unknown primary multiplicities.

No material veto was found in the exact frozen signed-design claim/r1.
Written PASS applies to the conditional exponent30, existence of an ordinary
signed cover, and the norm/equality characterization. There is no asserted
positive cover, extra code word, actual target realization or exclusion.
The first whole read completed at2026-10-04T13:38:46Z; a separate exact
start timestamp was not recorded and is not reconstructed. The companion
report records the authentic final sealing timestamp. No computational or
registration action is included.

