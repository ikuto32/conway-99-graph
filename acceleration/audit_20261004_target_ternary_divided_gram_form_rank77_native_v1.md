# Independent written audit: the target divided ternary Gram form

Native independently challenges Structural's frozen f07212fc paper and 29184b93 raw claim. Root supplied the direction before this review. This is a written conditional derivation, not agreement approval, a computational control, a new incidence matrix, a novelty claim or a target resolution. Historical spectrum/G55 and the earlier subsidiary determinant floor overlap are retained. No producer or checking code was imported, selected by AST, syntax-tested or executed. No solver, matrix program, Git, ledger or index operation ran.

## Exact premise and triangle factor

Assume exactly the simple SRG(99,14,1,2) identity over the integers and the complete incidence N whose columns are all actual triangles once. For an edge uv its unique common neighbor completes its unique triangle. Within N(u), every vertex has exactly one neighbor, since a second would give a second common neighbor of the edge to u. Hence N(u) is seven disjoint edges, every point has seven incident triangles, and the total number of triangles is 99*7/3=231. Distinct points occur together in a triangle precisely when adjacent, once. Consequently NN^t=H=A+7I, N^t j=3 j_231, and Nj_231=7j. A selected subset of triangles, repeated triangles or a merely lambda-one fixture cannot replace this full factorization and target premise.

The degree vector is Aj=14j. On j-perpendicular over Q, the SRG identity gives (A-3I)(A+4I)=0. The two distinct roots and symmetry give dimensions f+g=98, and trace A=0 gives 14+3f-4g=0. Thus f=54,g=44. H has exact eigenvalues 21,10^54,3^44, with nonzero determinant 21*10^54*3^44 of 3-adic valuation 45. These are determinant-polynomial/eigenspace statements over Q; no rational eigenbasis is reduced modulo3.

## The first rank layer without assuming modular diagonalizability

Use g=H mod3=A+I. Direct expansion gives g^2-g=2J, gj=0, gJ=Jg=0 and J^2=0. Put e=g^2=g-J. Then e^2=e, eJ=Je=0 and g=e+J. The characteristic polynomial of g is t^45(t-1)^54, by reduction of the integral characteristic polynomial of A. The annihilator g^2(g-I)=0 separates a zero primary space of dimension45 from the eigenvalue1 space of dimension54. On those spaces e is respectively0 and1. Therefore rank e=54; this does not diagonalize g's zero primary part.

The symmetric idempotent e splits the ambient space into im e and ker e. J vanishes on im e. Since J is a nonzero matrix on the entire coordinate space, its restriction to ker e remains rank1. g is identity on im e and equals J on ker e. Therefore rank g=54+1=55 and dim V=dim ker g=44. For y in V, the identity g^2-g=2J implies Jy=0, so the coordinate sum of y is0. j is nonzero even though 99=0 in F3, and j belongs to V.

## Lift independence, including local-rational lifts

For x,y in V, H times any integer lift of y is coordinatewise divisible by3. Thus beta(x,y)=xhat^t H yhat/3 modulo3 is defined. Changing xhat to xhat+3u adds u^t H yhat, which is0 modulo3. The analogous change of yhat is0 as well. Changing both adds those two terms and 3u^t H v, again0. This proves bilinearity and symmetry as well as all lift independence; beta is not the ordinary coordinate dot product.

The same argument is valid over R=Z_(3), reducing denominators prime to3 modulo3. Every R lift of a fixed residue differs from an integer lift by an element of3R. Therefore an R-congruence basis can be used to represent this very integer-defined beta. It does not define a different rational-lift form. This detail is needed when interpreting the local congruence below.

## Symmetric congruence justified independently

A nonzero symmetric matrix over R has a least entry valuation a. Divide the current block by3^a. If a diagonal entry is a unit, use it as an orthogonal pivot. If only an off-diagonal entry h_ij is a unit, e_i+e_j has unit norm h_ii+2h_ij+h_jj because 2 is invertible and both diagonal terms are divisible by3. The basis change is invertible. Subtracting the appropriate multiples of the pivot vector splits its orthogonal complement by a congruence over R, not by two unrelated row/column changes. Repeat on the remaining block. Since H is nonsingular this yields unit-congruence diagonal entries 3^{a_i}u_i with a_i>=0 and units u_i. A congruence changes the determinant by a squared unit, so the a_i sum to45.

There are exactly55 exponents0 because the congruence is invertible after reduction and rank g=55. The remaining44 exponents are positive. Their sum is45, so precisely43 of them are1 and one is2. On the kernel of g only these last44 coordinates remain. In the divided form their diagonal coefficients become 3^{a_i-1}u_i modulo3: exactly43 units and one zero. Hence rank beta=43 and its radical has dimension1. This proves the valuation-to-form step directly; an arbitrary Smith equivalence is not assumed to be a symmetric congruence.

For y in V, beta(j,y)=j^t H yhat/3=7*sum(yhat)=0 modulo3. j is nonzero, so rad beta is exactly span(j). A Smith invariant description may summarize the valuations after this proof, but cannot substitute for the congruence/lift justification.

## Incidence left kernel and the dimension bound

Let L=ker(N^t mod3). For lifts of x,y in L write N^t xhat=3z and N^t yhat=3w. H=NN^t implies L is contained in V, and xhat^t H yhat=9 z^t w. Consequently beta vanishes on L times L. Also N^t j=3j_231 implies j belongs to L. Thus L/span(j) is totally isotropic in the nondegenerate 43-dimensional space V/span(j).

For a nondegenerate bilinear space of dimension43, any totally isotropic subspace W lies in W-perpendicular and dim W-perpendicular=43-dim W. Hence 2dim W<=43, dim W<=21. With W=L/span(j), dim L<=22 and rank_F3 N=99-dim L>=77. The constant left-kernel vector gives rank_F3 N<=98. No Witt type, existence of a 21-dimensional isotropic space, nonconstant member of L or equality case is assumed.

As a separate directional check, if rank_F3 N=r, a unit row change over R makes 99-r rows divisible by3. Every 99-column determinant is therefore divisible by3^{99-r}. Cauchy-Binet expresses det(NN^t) as a sum of their squares, so its valuation is at least2(99-r). Cancellation may raise this valuation, never lower the common divisor. Thus 2(99-r)<=45 again yields r>=77. This shorter check does not prove the beta/radical assertion and cannot give an upper bound on rank N or a small circuit.

## Hand falsification controls and limits

1. For H=diag(1,3,9), ker(H mod3) is span(e2,e3), and beta there is diag(1,0). Its determinant valuation3 consists of one unit direction, one valuation1 and one valuation2 direction, exactly matching the congruence reasoning. In particular V itself need not be beta-totally-isotropic.
2. This H has an integer Gram factor with rows (1,0,0,0,0), (0,1,1,1,0), (0,0,0,0,3). Its mod3 incidence-factor left kernel is span(e3), and beta vanishes there. This is a small integer-factor analogue, not a binary target or triangle fixture.
3. In the rook9 graph the complete point-by-six-lines incidence has singular Gram A+2I, with eigenvalues6,3^4,0^4. The target determinant valuation45 does not apply. The corner vector [[1,-1,0],[-1,1,0],[0,0,0]] has zero integer line sums, while its ordinary self-dot-product is4=1 modulo3. It therefore falsifies ordinary-dot-product self-orthogonality, while its incidence Gram pairing is exactly0.
4. Over characteristic2 the symmetric matrix [[0,1],[1,0]] has a unit off-diagonal but e1+e2 has norm2, not a unit. The odd-prime pivot step must not be transferred to2.
5. The integer diagonal example diag(3,9,9) has a three-dimensional mod3 kernel but divided-form rank1. Nonunit count alone does not imply radical dimension1; the target's exact excess valuation45-44=1 is essential.

The first-layer rank55 and determinant-only floor77 already occur in the bounded archive documents read here. This audit makes no novelty assertion and does not independently approve unrelated hollow-residual, circuit or coding claims. Rank77 is a lower bound, so it does not strengthen a minimum-circuit upper bound by reversing its direction. Rank98 and L=span(j) remain compatible. No forced fixed17 graph, nonconstant left-kernel word, target existence/nonexistence, executable gate, ledger registration or external/formal verification follows.

## Exact written scope

Twenty independent written boundaries are checked: full triangle factorization; exact rational spectrum; reduced polynomial rather than eigenbasis; g/e identities; first-layer rank55; constant/sum-zero vectors; first lift change; second lift change; joint lift change; local-rational lifts; odd-unit off-diagonal pivot; congruence determinant valuation; exact valuation multiplicities; rank/radical of beta; incidence isotropy; quotient dimension; Cauchy-Binet direction; diagonal-factor analogue; rook ordinary-dot/singular boundary; characteristic2 and excess-valuation limits. All checks are written only. There are zero computational fixture executions, mathematical programs, formal checks, external reviews or new target objects.
