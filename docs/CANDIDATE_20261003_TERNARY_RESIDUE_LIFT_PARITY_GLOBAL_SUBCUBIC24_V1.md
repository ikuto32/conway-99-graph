# Ternary residual lift parity and a global subcubic support bound

Producer: /root/structural. Status: CANDIDATE, pending an independent written derivation by a different verifier. No executable mathematical calculation, graph fixture, numerical solver, ledger/index mutation, realization, novelty or target resolution is asserted. This note is new working material outside the fixed371 publication cutoff.

## Exact proposed statements

Let A be a symmetric binary zero-diagonal 99-by-99 matrix with exactly14 ones in every integer row. Over GF(3), define M=A^2+A+J, where J is the all-one matrix. Equivalently M is the reduction of the complete integer residual D=A^2-12I+A-2J. Put E_0={0} and E_k=ker((M-I)^k) for every integer k>=1.

1. Every quotient E_k/E_(k-1) has even dimension over GF(3). Consequently every Jordan block size at eigenvalue1 has even multiplicity, dim ker(M-I) is even, and rank(M-I) is odd. No nonzero residual, nonzero kernel of the triangle incidence matrix, or rank upper bound on that incidence matrix follows.
2. Let H be the complete nonzero unordered off-diagonal support of M, with its isolated vertices discarded. If H is nonempty and has maximum degree at most3, then H has at least24 vertices and at least24 edges. Connectivity of H is not assumed. This is a necessary restriction only; no24-vertex support is asserted realizable. Equivalently any nonempty residual with fewer than24 support vertices or fewer than24 bad pairs must contain a support vertex of degree at least4.

The parity statement covers arbitrary support degrees. The24-vertex conclusion explicitly uses the subcubic premise. The earlier stronger connected-subcubic spanning99 theorem remains untouched; this extension addresses disconnected support through a general spectral lift mechanism rather than an F3=9 case classification.

## Complete residual arithmetic

Exact symmetry and degree give A1=14*1 and AJ=JA=14J. Thus AM=MA. The integer residual diagonal is14-12-2=0, and every complete residual row sums to196-12+14-198=0. For u!=v, write r_uv=(A^2)_uv+A_uv-2. It is at least-2. A good pair M_uv=0 has r_uv a multiple of3, so r_uv>=0. The matrix M is symmetric with zero diagonal and M1=0.

A nonisolated support row cannot have degree1. At degree2 its two labels are opposite nonzero residues. At degree3 all three labels agree, since the sum of three binary choices of residues1/2 is divisible by3 only when they are all equal. These are statements about the whole residual row.

## General lift parity proof

Let L=1^T. Since LM=0, L(M-I)^k=(-1)^k L. For x in E_k the left side applied to x is0; hence Lx=0 and Jx=0. Commutation makes E_k invariant under A, and E_(k-1) invariant as well. Also (M-I)x lies in E_(k-1).

On E_k/E_(k-1), the induced linear map T from A therefore satisfies

 T^2+T-I=0.

The degree2 polynomial f(t)=t^2+t-1 has values2,1,2 at t=0,1,2 respectively, so it has no GF(3) root and is irreducible. A vector space annihilated by this polynomial becomes a vector space over the field GF(3)[t]/(f), which has dimension2 over GF(3). Each quotient consequently has even GF(3) dimension.

The dimension difference dim E_k-dim E_(k-1) counts the Jordan blocks at eigenvalue1 of size at least k. All these differences are even; subtracting consecutive differences makes the number of blocks of each exact size even. Taking k=1 yields the asserted odd rank of M-I on99 coordinates. This argument uses the actual polynomial identity M=A^2+A+J, not only an arbitrary commuting signed matrix.

## Binary propagation outside the whole support

Write S=V(H), m=|S|. For z outside S, the entire z-row of M vanishes. Commutation gives x*M[S,S]=0 for the binary vector x_u=A_zu, u in S. In a component of H, a degree2 column forces the two support-neighbor coordinates equal. A degree3 column forces their three binary coordinates equal, since their sum divisible by3 is0 or3. Hence x is constant along every even walk of each component.

A connected bipartite component has its two parts as even-walk classes; a connected nonbipartite component has one class. For the latter, an odd closed walk changes the parity of a connecting walk. This applies only to vertices z outside the WHOLE support S. No equality of neighborhoods in a different support component is assumed.

Choose P as a larger part of a bipartite component, or as the whole vertex set of a nonbipartite component; put p=|P|. Its vertices have exactly the same outside-S neighbors, of some size t. Each has d=14-t neighbors inside S. For each w in S let a_w count its A-neighbors in P. Then sum a_w=pd and the exact common-neighbor sum is

 sum_(u<v in P) CN(u,v)=choose(p,2)*t + sum_(w in S) choose(a_w,2).

Cauchy gives sum a_w^2 >= p^2*d^2/m. As p>=2, dividing by choose(p,2) and completing the square gives

 average_P CN >= 14 - p*m/(4*(p-1))
                  + p*(d-m/2)^2/(m*(p-1))
               >= 14 - p*m/(4*(p-1)).                         (1)

The full S, rather than one component, is the denominator m. This preserves every possible internal adjacency contribution from other components.

## Component-class inequalities

For a nonbipartite component, choose P to be the entire component. Every pair from P to its complement is good and has nonnegative integer residual. Exact complete row sum0 implies each row's residual sum within P is at most0. Therefore average_P CN<=2, and (1) implies

 p*(48-m)<=48.                                               (2)

Such a signed support component has at least4 vertices: a3-vertex component would be a degree2 triangle, whose forced alternating labels are inconsistent. Thus (2) requires m>=36.

For a bipartite component, all pairs within the chosen part P are good. Each row has at most3 bad pairs, each residual at least-2; every other good residual is nonnegative. Its sum over P is at most6. Hence average_P CN<=2+6/(p-1), and (1) gives

 p*(48-m)<=72.                                               (3)

If p>=3, then m<24 makes the left side strictly greater than72. Thus any component with p>=3 requires m>=24.

If p=2, both parts have size2: the other part is no larger, and minimum degree2 forces at least2 vertices on each side. The component is an alternating C4. Its two bad residuals in each row have residues1 and2, whose individual lower bounds are-2 and-1; their sum is at least-3. Replacing the preceding budget6 by3 gives

 2*(48-m)<=60, so m>=18.                                    (4)

These alternatives prove that if m<24, EVERY component must be an alternating C4 and m>=18. As m is then a multiple of4, the only remaining value below24 is m=20, consisting of five C4 components.

## Spectral veto for the remaining global alternative

In cyclic order an alternating C4 block has labels s,-s,s,-s with s nonzero. Let p=(1,0,-1,0)^T and q=(0,1,0,-1)^T over GF(3). Its matrix is s*(p*q^T+q*p^T). The two vectors are orthogonal and each has squared norm2, so their span and its2-dimensional orthogonal complement form a direct sum. The block vanishes on that complement and maps p to2s*q and q to2s*p. It has one eigenvector each at1 and-1, and two at0, regardless of the choice of s.

The whole M is block diagonal across residual components and has additional zero rows on discarded isolates. For five C4 components, dim ker(M-I)=5, contradicting the general even-dimension theorem. Therefore m>=24. Minimum nonisolated support degree2 gives 2|E(H)|>=2m, proving |E(H)|>=24. For an all-C4 support, the number of components must in fact be even; the first value compatible with (4) is six components. This remains only a necessary condition.

## Written falsification boundaries and limits

1. M=0 satisfies every parity layer with dimension0 and rank(M-I)=99. The proof cannot force a nonzero defect or incidence kernel.
2. One alternating C4 has an odd1-eigenspace and is rejected by lift parity; this is a signed-matrix calculation, not an actual degree14 graph fixture.
3. Two C4 blocks satisfy parity but fail the global m>=18 Cauchy budget; parity alone is not sufficient for realization.
4. Five C4 blocks meet the m>=18 budget but violate parity. Six blocks pass these necessary tests; no adjacency realization is asserted.
5. A monochromatic K4 with residue1 has no1-eigenspace but fails the component size inequality when alone. With residue2 its1-eigenspace has dimension3, also failing parity when alone.
6. Taking A=0 and an independently prescribed alternating C4 matrix produces AM=MA and M1=0 while the1-eigenspace is odd. It refutes a commutation-only shortcut, because that prescribed M is not A^2+A+J and A does not have degree14.
7. At support degree4, incident labels1,2,1,2 sum to0, and a binary neighbor vector(1,1,0,0) has weighted sum0 without being constant. Therefore the subcubic propagation step must not be extended to degree4.
8. Every outside-neighborhood equality uses z outside whole S; no block relation for vertices in other support components was substituted.
9. The exact common-neighbor count includes witnesses inside S and outside S. No independence, uniformity of internal adjacency, automorphism or incidence decomposition was assumed.
10. All signed support controls and polynomial evaluations above are written calculations, with0 executed fixtures/commands. Independent verification, formalization, external review, novelty and allowed-support realizability remain unknown.

This note uses no ledger theorem as a material premise: all identities, propagation and inequalities are rederived. Previously checked connected-subcubic lower45/spanning99 and the seven/eight-defect notes were inspected to avoid repeating their connected or small-case scopes; their bytes and claims are unchanged. There is no rank upper bound for B, no binary/ternary field interchange, no F3 engine threshold change, no new search, and no Conway99 conclusion. Overall search coverage: UNKNOWN; no validated denominator.
Actual preparation timestamp: 2026-10-03T08:00:59.1761804+00:00. Source context: 63437c9b9fc2dd58b3bdfb51fc347b880b397503. This new working note is not claimed to have been included in that commit.

