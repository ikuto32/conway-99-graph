# Candidate: constant-only ternary kernel in the unrestricted 3-adic Gram relaxation

This is a source-only written candidate by Structural, frozen on 2026-10-04.
It has no independent verification gate and no execution. It does not construct
a graph, a binary incidence matrix, or an ordinary integer matrix with the
exact target Gram. It falsifies an attempted exclusion from the stated modular
and 3-adic equations alone.

## Exact statement

Write j for the all-one vector of length 99, q for the all-one vector of
length 231, and J=jj^T. Let H be a symmetric ordinary integer 99-by-99 matrix
with Hj=21j. Suppose its reduction G over F3 satisfies

```
Gj=0,       G^2-G=2J,       rank(G)=55.
```

Then there exists a matrix M over the 3-adic integers, of size 99-by-231,
such that

```
MM^T=H,       Mq=7j,       M^Tj=3q,       rank_F3(M)=98.
```

In particular ker_F3(M^T)=span(j). For every positive integer m there is
also an ordinary integer matrix M_m with exact margins M_m q=7j and
M_m^T j=3q, rank_F3(M_m)=98, and M_m M_m^T congruent to H modulo 3^m.
The matrices can be chosen coherently, M_(m+1) congruent to M_m modulo 3^m.
No entry bound, nonnegativity, binary condition, triangle support, or ordinary
integer exact-Gram factorization is asserted.

The target H=A+7I satisfies the assumptions conditional on existence of an
SRG(99,14,1,2). Thus the target Gram at every finite 3-adic precision, its exact
3-adic limit, and the specified incidence margins admit a constant-only left
kernel when entries are allowed to be arbitrary 3-adic integers. This supplies
no actual target incidence matrix and does not exclude a nonconstant kernel.

## 1. A ternary factor with the correct Gram and rank 98

All calculations in this section are over F3. Since J^2=0 and GJ=0,
G^3=G^2. Consequently E=G^2 is a symmetric idempotent and

```
G=E+J,       Ej=0,       rank(E)=54.
```

For the rank assertion, im(E) and span(j) are disjoint, G is the identity
on im(E), and for any coordinate vector e, z=(I-E)e has sum(z)=1 and Gz=j.
These facts show im(G)=im(E) direct_sum span(j).

The first 98 coordinate vectors form a complement to span(j). The restriction
D of G to this complement therefore has rank 55 and radical dimension 43.
Diagonalize the symmetric form D by congruence over F3. A short elementary
justification is available: a nonzero symmetric form in odd characteristic
has a vector of nonzero norm, since otherwise polarization makes the whole
form zero. Split off that vector and induct. The nonzero diagonal coefficients
are 1 or 2. Two coefficients 2,2 become 1,1 on replacing the corresponding
vectors by their sum and difference, because 2+2=1 and the cross product is
zero. Thus the nondegenerate 55-dimensional part has at most one coefficient 2.

Embed every coefficient 1 in one standard dot-product coordinate, and the
possible coefficient 2 in two coordinates using (1,1). Embed each of the 43
radical basis vectors separately as (1,1,1), of norm zero, on three fresh
coordinates. The resulting 98 row vectors are linearly independent, have the
required diagonal Gram, and use at most

```
56+3*43=185
```

coordinates. Undo the congruence, and pad by zero coordinates to length 231.
Let the resulting 98-by-231 matrix be B. Its rows are independent and BB^T=D.
Make a 99th row equal to minus the sum of the other rows, giving N0. Since
Gj=0 determines the missing last row and column of G from D,

```
N0 N0^T=G,       N0^Tj=0,       rank(N0)=98.
```

It remains to obtain Nq=j. Choose z=(I-E)e as above. The vector v=N0^T z
has norm z^T Gz=1. In two unused coordinates choose t=(1,1), so t has norm
2 and N0t=0. The nonzero vector w=v+t is isotropic and N0w=j. The vector q
is also nonzero isotropic, since 231=0 in F3.

The standard nondegenerate dot space has an isometry taking w to q. This
does not require a classification theorem. If two nonzero isotropic vectors
u,v have u dot v nonzero, reflection in u-v takes u to v. If u dot v=0,
choose y with u dot y=v dot y=1 when they are independent. Then
h=y-(y dot y)/2*u is isotropic and has nonzero dot product with both. If
v is a nonzero multiple of u, choose u dot y=1 instead; the same h works.
Two reflections suffice in the zero-dot case. These reflections are defined
because their reflecting vector has nonzero norm and 2 is invertible in F3.

Apply the inverse isometry on the columns of N0. The resulting N satisfies

```
NN^T=G,       Nq=j,       N^Tj=0,       rank(N)=98.
```

## 2. The all-one column vector is outside the row image

The fact q is not in im(N^T) is needed for the lifting construction. If
N^T x=q, then Gx=Nq=j. The decomposition G=E+J forces Ex=0 and sum(x)=1.
But then

```
0=q dot q=x^T Gx=sum(x)=1,
```

a contradiction. This uses the row-margin residue Nq=j as well as the Gram;
it is not a general assertion about all rank-98 matrices.

## 3. Exact ordinary integer margins at the first level

Lift N entrywise to an ordinary integer matrix B0. Its row sums are congruent
to 7 and its column sums are congruent to 3 modulo 3. Therefore

```
alpha=(7j-B0q)/3,       beta=(3q-B0^Tj)/3
```

are integer vectors. Their totals agree, because 99*7=231*3=693.
For arbitrary integer row and column margins alpha,beta with equal totals,
an integer matrix S with Sq=alpha and S^Tj=beta exists. For example, put
alpha_i in the last column of each nonlast row, beta_a in the last row of
each nonlast column, and choose the last corner to give the last row sum.
Equal totals then give the final column sum too. Negative entries are allowed.

Set M_1=B0+3S. It has the exact required margins, reduces to N, and its Gram
is congruent to H modulo 3. This step neither preserves binary entries nor
claims that binary entries can be recovered later.

## 4. Lifting from precision 3^k to 3^(k+1)

Suppose M_k is ordinary integer, has the exact margins, reduces to N, and
M_k M_k^T is congruent to H modulo 3^k, with k at least 1. Define the integer
symmetric matrix

```
D_k=(H-M_k M_k^T)/3^k.
```

Its product with j is zero exactly: Hj=21j, while
M_k M_k^Tj=M_k(3q)=21j. Reduce D_k modulo 3 and call the result Dbar.

On im(N^T), prescribe a linear map T by

```
T(N^T x)=Dbar*x/2.
```

This is well-defined because ker(N^T)=span(j) and Dbar*j=0. Its values
lie in j-perp because Dbar is symmetric and annihilates j. Since q is outside
im(N^T), extend the prescription by Tq=0, then extend to all of F3^231
with image in j-perp. Thus

```
TN^T=Dbar/2,       Tq=0,       T^Tj=0.
```

Take any integer lift That of T and put B=M_k+3^k That. The quadratic
term 3^(2k) That That^T vanishes modulo 3^(k+1), because 2k>=k+1.
The two linear Gram terms sum to Dbar. Hence BB^T is congruent to H
modulo 3^(k+1). Its margins may differ from the desired margins, but those
differences are multiples of 3^(k+1), since Tq=T^Tj=0 modulo 3.

Use the same unrestricted integer-margin construction to add 3^(k+1) S_k
and restore both margins exactly. This last addition does not change the Gram
modulo 3^(k+1). The resulting M_(k+1) also agrees with M_k modulo 3^k.
This establishes the coherent finite-precision matrices by induction.

Their entrywise 3-adic limit M exists. Polynomial continuity gives the exact
Gram and exact margins. Its reduction remains N, so its left ternary kernel
is exactly span(j). This is a 3-adic construction, not a convergent sequence
of ordinary integer graph matrices.

## 5. What this retains for the actual target H

For the actual hypothetical target, A^2=12I-A+2J gives

```
H(6I-A)=30I-2J.
```

Consequently the matrix

```
P=7 M^T(6I-A)+2qj^T
```

satisfies MP=210I exactly over the 3-adic integers. Since 210/3=70 is a
3-adic unit, the cokernel is killed by 3. With rank(M mod3)=98 its cokernel
is exactly one copy of F3. Thus the right-inverse/cokernel argument supplies
no contradiction to this formal factor.

It also has the same divided Gram form as H, since its Gram is exactly H.
The determinant valuation 45, radical-one divided form, and the isotropy of
span(j) cannot eliminate it at this level. These refer to the actual H from
the earlier proof, not to a newly calculated determinant.

A vector X modulo 9 in ker(M^T) must reduce to c*j. Write X=c*j+3z.
Then M^T X=3(c*q+N^T z) modulo 9. Because q is outside im(N^T), c=0.
Thus no nonzero left ternary vector lifts to a modulo-9 kernel, exactly as
in the prior nonlift theorem; this is compatible with L=span(j).

The old perfect divided pairing is likewise compatible. On L=span(j) it is
gamma(j,u)=sum(u) on the ternary right kernel. This functional is nonzero,
because otherwise q would lie in im(N^T). Its kernel has dimension 132.
The formal 3-adic right kernel reduces to precisely that balanced subspace:
unit-pivot elimination of M leaves 98 unit directions and one direction
divisible by 3 exactly once, since the cokernel is F3. The integral relation
module over Z3 is a direct summand of rank 132, and all its relations have
coordinate sum zero by M^Tj=3q. Therefore balanced integer-liftability and a
perfect one-dimensional divided pairing remain possible together.

## 6. Falsification checks and overlap

The following are written boundaries, not executed controls:

- All constructions use unrestricted entries. Positive/binary incidence is
  the missing condition, and an ordinary integer exact-Gram factor is not
  obtained by the finite-precision construction.
- Odd characteristic is essential to the diagonalization, reflections, and
  division by 2. No binary-code conclusion follows.
- The number 231 gives q dot q=0 and ample embedding coordinates; the bound
  185 comes from 55 nondegenerate and 43 radical directions. A short-column
  factor need not support this construction.
- Correct margins are essential both to excluding q from im(N^T) and to
  proving D_k j=0. Equal total 693 is checked before every margin repair.
- The k=1 quadratic term is already divisible by 9; later terms vanish at
  the required next precision as well.
- The rank-55 Gram does not force the factor rank to be 55. The construction
  has a 43-dimensional ordinary-dot radical in its 98-dimensional row image.
- The known binary Q=J4-I4 has a constant-only ternary left kernel and a
  nonzero divided pairing, but its dimensions and row degree differ. It is
  only the existing small boundary example, not a target construction.
- Rook9 has real-singular A+2I and different modular polynomial. The target
  right-inverse and rank-55 assumptions cannot be transferred to it.
- A general arbitrary integer lift can have the wrong Gram modulo 9. The
  linear correction is required; no arbitrary lift is treated as adequate.
- The exact target SRG identity and integer spectrum have not been refuted.
  They concern ordinary binary incidence, while M lives in Z3.

The earlier Structural reduced-Gram rank-98 design already supplied one
formal F3 countermodel. The present statement generalizes that boundary to
every prescribed G satisfying these assumptions, exact margins, and every
3-adic precision. It does not call the old example a new result. The accepted
mod9 nonlift/pairing and rank77 papers explicitly retained the constant-only
case. Archive Waves 170--172 were whole-read here; they contain the target
rank-55/block-code facts and conditional prism-free centered-code constraints,
not a constant-only contradiction. A bounded Markdown search for mod9,
prescribed Gram, and factorization terms found no exact statement of this
general construction; this is not an exhaustive novelty claim.

An earlier overbroad read-only search in this session accidentally included
large JSON evidence and produced truncated output. It was terminal before
the restricted Markdown checks. No mathematical computation, import,
enumeration, solver, source execution, or raw-result verification occurred.
No ledger, index, Git state, frozen artifact, or research status was changed.

The resulting next-attack boundary is precise: exclusion of L=span(j) must
use an additional property not implied by this unrestricted-entry 3-adic
Gram-and-margin relaxation, for example actual binary triangle supports or
ordinary integer exact incidence. The existence or nonexistence of a target
graph remains unknown.
