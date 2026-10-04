# Independent written audit: target incidence mod-nine nonlifting and divided pairing

Verifier: /root/native_driver. Mathematical producer: /root/structural.
Result: WRITTEN PASS for the exact candidate r1 statement, conditional on a
complete simple SRG(99,14,1,2). No computational invocation, matrix generation,
import, executable fixture, formal checker, external review or registration.
The start of this written review was not separately timestamped. The bound JSON
report supplies the truthful final verification timestamp.

The complete paper 0d7a6dfc0a7520ae43046675105666381da5adbcb6b75e2caeec068d6cbfa82a
and raw candidate 6cdc43f22987e2289ae8665fe33d815965287bac48109ae156d017259f29862f
were read. This audit derives the quotient map independently, rather than
assuming the candidate's radical or an unproved Smith/congruence identification.
Root supplied a shared gamma direction and Structural authored the candidate;
common discovery origin is disclosed. Agreement is not the basis of this pass.

## Exact domain and integral algebra

Write N for the complete 99-by-231 point-by-actual-triangle incidence, A for
the point adjacency, j for the 99-vector of ones, and c for the 231-vector of
ones. Every edge has exactly one triangle because adjacent common-neighbor
count is one. At each vertex the 14 incident edges are paired in seven
triangles. Hence there are 99*7/3=231 triangles, N c=7j, N^T j=3c,
and N N^T=A+7I. Nonedges share no triangle. These identities require all
actual triangles once, rather than an arbitrary selected triangle list.

The complete target identity is A^2=12I-A+2J. Therefore

    (A+7I)(6I-A)=42I-A-A^2=30I-2J.
    P=7N^T(6I-A)+2c j^T,
    N P=7(30I-2J)+14J=210I.

The coefficient is exactly 210=3*70, with 70 congruent to one modulo three.
This gives real and rational row rank 99 without a determinant computation.
Over Z localized at three, the image of N contains 3 times every vector.
Thus its local cokernel is annihilated by three; its nonunit three-primary
Smith factors, if expressed that way, have exponent exactly one. This is
rectangular equivalence data for N and is not a symmetric congruence claim
about N N^T. The Gram's possible factor nine is therefore no contradiction.

If N^T X is divisible by nine, then 210X=P^T N^T X is divisible by nine.
Cancelling the factor three gives 70X divisible by three, so X is divisible
by three. Every lift of a nonzero ternary x is excluded. The assertion does
not exclude vectors X=3v whose ternary residue is zero.

## An independent quotient construction of the perfect pairing

Let M=N reduced modulo three, L=ker(M^T), K=ker(M), and
C=F3^99/im(M). For u in K choose an integer lift U and define

    delta(u)=[N U/3] in C.

The quotient is integral because u is in K. Replacing U by U+3W changes
N U/3 by N W, whose residue lies in im(M), so delta is well-defined and
linear. This map is onto by an explicit construction: for any integer lift
Y of a point vector, take U=P Y. Then N U=210Y and

    delta(PY mod3)=[70Y mod3]=[Y mod3].

No rank assumption or Smith algorithm enters this surjectivity argument.
The ordinary point-coordinate pairing identifies C^* with L: a functional
represented by x annihilates im(M) exactly when M^T x=0. In particular
the evaluation pairing L times C is perfect. Composing with onto delta gives

    gamma(x,u)=x^T delta(u)=X^T N U/3 mod3.

It follows directly that the left radical is zero. Separate lift checks
also show the literal formula is well-defined: X->X+3v changes it by
v^T N U, U->U+3w changes it by X^T N w, and a simultaneous change adds
3v^T N w. Each is zero modulo three under the two kernel conditions.

For completeness, the candidate's alternative left-radical argument also
works. If z=N^T X/3 pairs to zero with all K, then z mod3 is in im(M^T).
Choose an integer v with z=N^T v mod3. The new lift X-3v satisfies
N^T(X-3v)=0 mod9, so the nonlifting result forces x=0. The image equality
K^perp=im(M^T) is ordinary finite-dimensional annihilator duality, not
ordinary-dot-product self-orthogonality of L.

## Exact integer right relations, dimensions and mod-nine lifts

An exact integer relation R with N R=0 reduces into K and has delta=0.
Conversely, if delta(u)=0, choose lifts U,v and integer w with

    N U/3=N v+3w.

Set

    R=70U-210v-3P w.
    N R=70N U-210N v-630w=0.
    R mod3=U mod3=u.

This verifies the coefficient cancellation and residue preservation
explicitly. Thus ker(delta) is precisely K_int, the reductions of exact
integer relations. K_int is a ternary subspace: sums and scalar multiples
come from sums and integer multiples of exact relations.

Write r=rank(M). Then dim K=231-r, dim C=99-r=dim L. Surjectivity of delta
and its identified kernel give dim K_int=132 and the exact sequence

    0 -> K_int -> K -> C -> 0.

Identifying C with L^* by evaluation gives precisely the stated sequence
and perfect pairing L times K/K_int. This explains why the integer-kernel
dimension is fixed while the quotient dimension depends on the ternary rank.
It does not assert that all ternary right dependencies lift.

The right mod-nine statement has the same condition. A replacement U+3W
has N(U+3W)=0 mod9 exactly when N U/3+N W=0 mod3, namely delta(u)=0.
That condition gives the exact relation constructed above. Thus a right
word has a mod-nine relation lift if and only if it has an exact integer
relation lift. This is asymmetric with the left nonlifting result.

## Constants and balanced implications

The nonzero j is in L, because N^T j=3c. For u in K,

    gamma(j,u)=j^T N U/3=c^T U=sum(u) mod3.

Since delta is onto and the evaluation pairing is perfect, this functional
is nonzero on K. There is an unbalanced right dependency. This recovers
the earlier affine/unbalanced consequence and does not discover a new
minimum circuit or improve the rank/circuit bounds.

If L=span(j), equivalently r=98, right-radical membership is exactly
vanishing of sum. Thus and only in that conditional case balanced words
are precisely the integer-liftable words. More generally liftable words
are always balanced: summing an exact relation gives 3 sum(R)=0 over Z.

If x in L is independent of j, left nondegeneracy makes gamma(x,.) and
sum independent functionals on K. Were gamma(x,.) zero on ker(sum), it
would factor through the one-dimensional quotient K/ker(sum) and be a
multiple of sum, a contradiction. Therefore some balanced u has
gamma(x,u) nonzero and does not lift. Conversely such a balanced
nonliftable word cannot exist when L=span(j). The claimed equivalence
between an additional left dependency and a balanced nonliftable word
is consequently correct. It supplies no reason that either must exist.

## Written falsification boundaries

For Q=J4-I4, Qj=3j and Q(-3I+J)=3I. Modulo three a null vector has all
coordinates equal to its sum, so both kernels are span(j); gamma(j,j)=4=1.
This independently confirms the one-dimensional nonlifting/perfect-pairing
example. For diag(Q,Q), x=(j,0) and u=(j,-j) give sum(u)=0 and gamma=4=1.
Balancedness alone fails with an extra left dependency. These binary
column-weight-three matrices are parameter analogues, not target graphs.

For diag(1,3) and diag(1,9), the reductions agree. With x=u=e2 their
pairings are respectively 3/3=1 and 9/3=0 modulo three. The latter has
a nonzero left lift modulo nine and no NP=210I identity: such an identity
would require its lower-right P entry to equal 210/9, not an integer.
This catches reliance on the mod-three rank alone.

An independent rectangular integer check is N=[3,6], P=[70,0]^T, so
NP=210. For U=[1,1]^T one has NU=9, delta=0, and the formula produces
R=[-140,70]^T. Its residues are [1,1] and N R=0 exactly. Here K is all
F3^2, K_int is span([1,1]), and L has dimension one. This checks a
nonzero integer correction and arbitrary coefficient growth; it is not
binary incidence and is not used as a target premise.

For rook9, the six triangle columns are three board rows and three board
columns. The four-corner point vector with entries 1,-1,-1,1 has each
integer row and column sum zero, so N^T X=0 exactly and its residue is
nonzero. Hence the target no-lift statement cannot be transferred to all
lambda-one/mu-two analogues. Rook incidence has real rank five and cannot
have NP=210I_9. No computation of a target or fixture matrix was run.

No integer lift in this proof preserves a selected support, coefficient
signs or the range {0,1,-1}. A balanced word supplied by a second left
functional need not be a circuit. The unbalanced minority-sign circuit
bounds therefore do not apply to it. All conclusions remain compatible
with constant-only L and unresolved target existence.

## Bounded archive comparison and exact scope

Whole-read comparisons were the candidate's eight pinned sources: the
mod-nine paper, divided-Gram/rank77 paper, old nonconstant-kernel design,
affine/unbalanced paper and external Wave168/170/171/191 derivations.
All eight exact pins matched. Wave168 supplies real row rank and rational
kernel dimension132; Wave170 supplies the historical ternary Gram rank55
and upper98; Wave171 supplies centered-code/star identities; Wave191's
rank<=82 uses its extra rank11 premise. The current divided-form floor77,
coloring moments and affine/unbalanced existence are overlap. None of
these compared texts states this exact NP/mod-nine/right-radical package.
This is a bounded textual observation, not an exhaustive novelty claim,
an external check, or approval of unrelated archival endpoints.

This pass is for the exact r1 statement and assumptions in raw6cdc43.
No previous rank result is a necessary theorem dependency: the direct
NP=210I argument derives all required algebra. Fixed17 count relaxations
do not supply the full N and cannot silently receive this test. No target
object, no nonconstant kernel, no target exclusion, no new numerical
workflow and no registered claim are asserted.

## Complete written-check inventory

The bound report counts the following 28 paper-only checks, with zero
executable controls, enumeration, formal or external checks.

| Check | Independently checked boundary |
| --- | --- |
| 1 | Complete triangle factorization and 231 columns |
| 2 | Exact target adjacency polynomial |
| 3 | P coefficients and NP=210I cancellation |
| 4 | Rational/real row rank99 from the right inverse |
| 5 | Local cokernel exponent and rectangular/Gram separation |
| 6 | Nonzero left residue cannot lift modulo nine |
| 7 | Left integer-lift change |
| 8 | Right integer-lift change |
| 9 | Simultaneous lift change |
| 10 | Quotient delta well-defined and linear |
| 11 | Explicit delta surjectivity via PY |
| 12 | Annihilator duality and zero left radical |
| 13 | Exact integer relation lies in right radical |
| 14 | Explicit reverse exact lift and residue preservation |
| 15 | K_int dimension132 |
| 16 | Perfect quotient pairing and exact sequence |
| 17 | Right modulo-nine iff exact integer lift |
| 18 | Constant vector and sum functional |
| 19 | Nonzero sum functional and prior affine overlap |
| 20 | Rank98 balanced iff liftable criterion |
| 21 | Extra-left iff balanced nonliftable consequence |
| 22 | J4-I4 positive pairing |
| 23 | Two-block balanced nonliftable example |
| 24 | Same-mod3 diag(1,3)/diag(1,9) corruption boundary |
| 25 | Rectangular [3,6] explicit integer correction |
| 26 | Rook9 exact left dependency excludes parameter transfer |
| 27 | Zero residue allowed and support/sign/circuit limits |
| 28 | Whole bounded archive overlap and no novelty/coverage inference |
