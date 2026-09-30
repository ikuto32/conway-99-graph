# Candidate ternary hollow residual completion

This is a new candidate derivation and bounded producer experiment. It is not
independent approval, a target construction, an exclusion, or a novelty claim.
All matrices in the completion criterion are over GF(3).

## What the nilpotent route already supplies

For a hypothetical target, A²+A=−J, AJ=−J and J²=0. Hence A(A+I)²=0.
The already checked characteristic polynomial is t^54(t+1)^45. Its zero primary
part is semisimple of dimension54. On the other45dimensions write A=−I+N.
Then N²=0 and A²+A=−N=−J, so N=J on this summand has rank1. Thus it has one
size2 block and43size1 blocks. In particular rank(A)=45 and rank(A+I)=55.
The current modular-rank audit already proves the first rank; pinned archive
Wave23 explicitly records the second. Wave171's triangle-block nilpotent code is
explicitly identified there with the existing centered code. These observations
are overlap, not newly found obstructions. No diagonalizability modulo3 is used.

The243 and rook9 fixtures have different parameters. For them A²+A=2I+2J
modulo3, so (A−I)²=2J and (A−I)³=0. They calibrate field arithmetic and graph
identities, not the target's distinct primary decomposition.

## A different linear question: symmetric zero-diagonal D

Let F,H be a×m matrices. A symmetric matrix D with FD=H exists if and only if

1. ker(Fᵀ) is contained in ker(Hᵀ); and
2. FHᵀ is symmetric.

Indeed on W=im(Fᵀ), define T(Fᵀx)=Hᵀx. The first condition makes T well-defined.
The second says uᵀTv=vᵀTu on W. Complete a basis of W to a basis P of the
ambient coordinate space; the specified columns of PᵀDP have a symmetric
specified upper-left block. Fill the remaining symmetric block arbitrarily.
This constructs a symmetric D0. Conversely either condition follows from such D.

Let K be any m×k matrix whose columns form a basis of ker(F), and let

    S(K) = span { K_i entrywise-multiplied by K_j : 1≤i≤j≤k }.

Every symmetric solution is D0+KSKᵀ with S symmetric. To prove completeness,
a symmetric difference N satisfying FN=0 has image inside im(K). With a left
inverse L of K, symmetry gives N=K(LNLᵀ)Kᵀ, whose middle matrix is symmetric.
Its attainable diagonals span exactly S(K): diagonal entries of S contribute
K_i², and off-diagonal entries contribute 2K_iK_j. Since2 is invertible in GF(3),
there is a symmetric **zero-diagonal** solution precisely when

    diag(D0) belongs to S(K).

The criterion is independent of the chosen basis and symmetric solution: their
changes produce exactly the same attainable diagonal subspace. If S(K) is the
whole GF(3)^m, zero diagonal adds no obstruction beyond symmetric consistency.
If it is proper, a vector in its annihilator can certify failure by having
nonzero pairing with diag(D0). This is an exact linear test; it still leaves
binary entries and the quadratic residual identity untested. Unlike the GF(2)
alternating result, symmetry alone does not settle the diagonal over GF(3).
For example F=[1,0], H=[1,0] is symmetrically completable but forces D11=1.
This is a generic field countercontrol, not a Gram factor or a target graph.

## Triangle consequences without an automorphism premise

Use the unrestricted triangle notation: three cells of size n, a cubic core C
with one neighbor in every cell, F with row sum n−2 and column sum2 in every
cell, prescribed Gram G=FFᵀ, and H=2J−(I+C)F. The exact core identities make
CG=GC. Consequently FHᵀ=2(n−2)J−G(I+C) is symmetric. Thus only kernel consistency
and the displayed diagonal condition are needed for symmetric hollow mixed
completion over GF(3); no equality among internal matchings or condition on P
is introduced.

For any cell indicator r, Fᵀr=2j and Cr=j. Multiplying FD=H on the left by rᵀ
gives 2jᵀD=(2n−8)jᵀ. Division by2 yields jᵀD=(n−4)jᵀ. If D is symmetric its
row sums are therefore also n−4. In particular the target residual degree8
modulo3 is automatic from the mixed equation and these margins. This statement
does not imply an integer degree8 binary matrix. The division argument is for
odd characteristic; it must not be transferred to GF(2).

The bounded experiment reconstructs the general criterion on all1×3 and2×2
ternary F/H pairs against exhaustive actual symmetric and hollow D images.
It also tests the genuine243 residual, degenerate rook9, and five raw12-cell
cores as core-only diagnostics. No99factor exists among these fixtures. Any
observed full square span on243 is a finite non-obstruction, not a universal
rank or all-factor theorem.
