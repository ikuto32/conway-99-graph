# Candidate: ternary incidence dependencies cannot lift on the left modulo nine

State CANDIDATE. Written derivation by `/root/structural`, prepared on
2026-10-04. Zero mathematical executions, finite fixture runs, formal checks or
external checks. This is separate from the accepted divided-Gram/rank77 paper,
the frozen four-claim registrar preparation and the fixed17 experiments. No
ledger, index, historical artifact or execution gate is changed. A different
author must challenge this exact argument before any acceptance.

## Exact proposed consequence

Let A be the adjacency matrix of a simple SRG(99,14,1,2), and let N be its
99-by-231 integer binary point-by-triangle incidence matrix, containing every
actual triangle once. Work over F3 when defining

    L = ker(N^T mod 3),       K = ker(N mod 3).

Let K_int be the reductions modulo three of exact integer relations
ker_Z(N). Then:

1. No nonzero x in L has an integer lift X with N^T X=0 modulo nine.
2. The divided cross-pairing

       gamma(x,u) = X^T N U / 3 mod 3,       x in L, u in K,

   is independent of both integer lifts X,U. Its left radical is zero and
   its right radical is precisely K_int. Therefore gamma induces a perfect
   pairing L times (K/K_int), and there is an exact sequence

       0 -> K_int -> K -> L^* -> 0.

   In particular dim K_int=132, whereas dim(K/K_int)=dim L.
3. For the all-one point vector j, gamma(j,u)=sum(u). Thus, if L=span(j)
   (equivalently rank_F3(N)=98), a ternary right-kernel word lifts to an exact
   integer relation if and only if its coordinate sum is zero modulo three.
   A nonconstant left-kernel vector instead forces a balanced right-kernel
   word which does not admit such an integer lift.

Integer lifting in this statement can change coefficient sizes and introduce
triangles outside the original support. It does not mean a circuit has an
integer relation on its own selected columns, or a relation with coefficients
restricted to 0,+1,-1. These necessary conditions neither force nonconstant L,
improve the existing rank77/rank98 bounds, impose a minority-sign population,
exclude the target, nor establish any fixed17 completion.

## An exact integral right inverse with denominator three times a unit

Every target edge lies in one actual triangle and each point lies on seven
triangles. Hence, over the integers,

    N 1_231 = 7j,        N^T j = 3 1_231,        H=NN^T=A+7I.

The complete common-neighbor identity gives

    H(6I-A) = (A+7I)(6I-A)
            = 42I-A-A^2
            = 30I-2J.

Define the integer 231-by-99 matrix

    P = 7N^T(6I-A) + 2 1_231 j^T.

Then

    NP = 7(30I-2J) + 2(7j)j^T = 210I.                 (1)

This also proves that N has real row rank99 without invoking a numerical
rank calculation or Smith form. Since 210=3*70 and 70 is prime to three,
over R=Z_(3), equation (1) says

    N(P/70)=3I,       3R^99 subset N R^231.             (2)

The R-cokernel of N is therefore killed by three. In a Smith description of
this rectangular matrix its nonunit three-primary factors are all exactly
three, with no factor nine. This is an interpretation of (1), not an
assumption of symmetric congruence for H and not a renewed determinant rank
argument. The Gram H has different invariant data and is not identified
with the cokernel of N.

The cokernel is nonzero: every column of N has coordinate sum three, so
sum modulo three annihilates N R^231 but is a nonzero functional on R^99.
The precise dimension will also follow directly from the pairing below.

## No nonzero left dependency lifts modulo nine

Transpose (1). If an integer vector X satisfies N^T X=0 modulo nine, then

    210X = P^T N^T X = 0 modulo nine.

Because 70 is a unit modulo three this implies X=0 modulo three. Thus a lift
of any nonzero x in L cannot satisfy the assumed modulo-nine equation.
This includes j, whose standard lift has N^T j=3 1_231. Failure to lift j is
an expected target condition, not a reason to reject a target.

## The pairing is independent of all lift choices

For u in K, N U is divisible coordinatewise by three, so X^T N U/3 is an
integer. Replacing X by X+3v changes this quotient by v^T N U, zero modulo
three. Replacing U by U+3w changes it by X^T Nw, also zero modulo three
because x is in L. A simultaneous change has the additional term
3v^T Nw, zero modulo three. Bilinearity follows by taking the corresponding
sum lifts. This is a pairing between two different code spaces; it is not
ordinary dot-product self-orthogonality of L or the old beta form on ker H.

Suppose gamma(x,u)=0 for every u in K. Put z=N^T X/3, an integer vector.
Then z mod3 is orthogonal to K. The ordinary coordinate pairing is
nondegenerate, and K^perp=im(N^T mod3), by inclusion and matching dimensions.
Choose an integer lift v with z=N^T v modulo three. Consequently

    N^T(X-3v) = 0 modulo nine.

The preceding no-lift result forces X-3v=0 modulo three, hence x=0. The left
radical of gamma is zero.

## The right radical equals the integer-liftable relations

Every reduction of an exact integer relation belongs to the right radical:
compute gamma using that integer relation as U and the numerator is zero.

Conversely suppose u is in K and gamma(x,u)=0 for every x in L. Choose an
integer lift U and write NU=3z. Then z mod3 is orthogonal to L and therefore
belongs to im(N mod3). Choose an integer lift v and an integer w such that

    z = Nv+3w,       N(U-3v)=9w.

Equation (1) produces a completely explicit exact integer relation:

    U_0 = 70U - 210v - 3Pw,
    N U_0 = 70*9w - 3*210w = 0.

As 70=1 modulo three, U_0 reduces to u. Thus the right radical is exactly
K_int. This proof uses neither a Smith algorithm nor an assumption that a
generic rational relation reduces to every finite-field relation.

Writing r=rank_F3(N), elementary finite-dimensional linear algebra gives
dim L=99-r and dim K=231-r. Left nondegeneracy means the map K -> L^*
defined by gamma has rank dim L, so it is onto. Its kernel is K_int. Hence

    dim K_int = (231-r)-(99-r)=132,
    dim(K/K_int)=99-r.

This agrees with the dimension of the exact rational right kernel, but the
explicit lift above establishes the needed reduction statement directly.
For this target N, a right word is liftable to a relation modulo nine if and
only if it is liftable to an exact integer relation: the modulo-nine lift
condition is z mod3 in im N, precisely the same right-radical condition.

## The constant functional and the additional-kernel bridge

The point vector j is in L because N^T j=3 1_231. For every u in K,

    gamma(j,u) = j^T N U/3 = sum(U) = sum(u) modulo three.

Because j is nonzero and the pairing has zero left radical, sum is nonzero
on K. This recovers the already verified affine obstruction and existence of
an unbalanced right-kernel word. It is explicitly overlap, not a new circuit
existence or upper-bound claim.

If L=span(j), the right radical is exactly the balanced subspace of K, so
the claimed integer-lift criterion follows. Conversely suppose x in L is
not a multiple of j. Left nondegeneracy makes gamma(x,.) linearly independent
of gamma(j,.)=sum. A linear functional on K vanishing on ker(sum) would be a
multiple of sum. Therefore some u in K has sum(u)=0 but gamma(x,u) nonzero.
That u is balanced and not in K_int. Equivalently, L contains a nonconstant
vector if and only if K contains a balanced non-integer-liftable word.

The established minority-sign lower bounds concern unbalanced circuits.
They cannot be applied to this balanced u. Minimizing u under its two
functional constraints does not automatically make it a circuit of N, and
no improved circuit-size bound follows. Nor can one prove that L is
constant-only by assuming all balanced relations lift; that assumption is
exactly the additional assertion at issue.

## Hand-checkable positive and corrupt boundaries

These are written examples, not executed controls or target constructions.

* For Q=J_4-I_4, each column is one of the four three-point subsets of a
  four-point set. Qj=3j, and 3Q^-1=-3I+J is integral. Modulo three both
  kernels are span(j). The divided pairing has gamma(j,j)=4=1, so is
  nondegenerate; a nonzero dependency cannot lift modulo nine.
* For diag(Q,Q), let x=(j,0) and u=(j,-j). Here sum(u)=4-4=0 but
  gamma(x,u)=4=1. The balanced word cannot lift. This binary column-weight
  three example falsifies a general claim that balancedness alone suffices
  when an additional left dependency is present. It has eight points,
  row degree three and lambda two, and is not a target or local target core.
* The integer matrices diag(1,3) and diag(1,9) have the same reduction
  modulo three. For their nonzero left/right kernel generators the divided
  pairing is respectively1 and0. In the second case the left vector already
  lifts modulo nine. Thus a mod3 matrix/rank alone cannot justify the new
  assertion; the integral identity (1) is essential. These matrices are not
  triangle incidence matrices.
* In the nine-point rook graph, N has nine rows and six triangle columns,
  and its real row rank is five. The four-corner vector with rows
  (1,-1,0),(-1,1,0),(0,0,0) has N^T X=0 exactly over the integers. This
  refutes transfer of the no-lift assertion to arbitrary lambda-one/mu-two
  parameter analogues. The rook row degree is two, H=A+2I is singular, and
  identity (1) is unavailable.
* A new modulo-nine dependency with X=3v is allowed; it reduces to zero
  modulo three and does not contradict the statement. The theorem concerns
  lifts of nonzero ternary vectors.
* The exact lift U_0 need not preserve support or signs. Treating it as a
  same-support circuit lift would be a false strengthening.

## Origin, comparison, utility and remaining uncertainty

Root requested an unrestricted ternary code attack after the divided beta3
proof. Structural derived (1), the no-lift argument and the cross-pairing
before Root independently sent the same pairing outline; Root then separately
challenged the arithmetic. The exact integer right-radical lifting proof and
the balanced-extra-kernel bridge are developed here. Shared origin is
disclosed, and agreement is not independent approval.

Compared on paper: current verified modular-rank, affine/unbalanced-circuit
and minority-sign statements; the full new divided-Gram paper; the old
nonconstant-color note with its complete rainbow-degree moments; archive
Wave168 incidence-minor energy, Wave170 ternary block profiles, Wave171
centered-code identification and Wave191 star-module derivation. Bounded
text searches also covered incidence/Smith/cokernel/mod9 terms in the pinned
external archive. The compared sources did not identify this exact
no-lift/right-radical package. This is not exhaustive novelty verification.
The rank77 floor, Gram Smith valuations and affine existence consequence
remain prior or separately accepted material and are not recounted as new.

This supplies a concrete extra necessary test for a proposed complete
integer incidence factor: a nonzero ternary left dependency must have a
nontrivial modulo-nine lift obstruction, and all right dependencies have
the exact pairing/lifting classification above. It does not act on a bare
fixed17 exterior-count relaxation, which lacks N, and it gives no numerical
workflow or prospective launch. Whether the lifting restriction yields an
unrestricted contradiction or an efficient completion screen remains
UNKNOWN. The hypothetical case L=span(j) satisfies all conclusions and is
not excluded. Overall target and coverage remain UNKNOWN.
