# Candidate: divided ternary Gram form and incidence rank at least 77

State: CANDIDATE, written derivation only. Author: `/root/structural`.
No computation, formal proof checker, external verification or registration was
performed. A different author must independently challenge this exact argument.
The target remains unresolved.

## Exact conditional statement

Let A be the adjacency matrix of a simple SRG(99,14,1,2), and let N be its
99-by-231 binary point-by-triangle incidence matrix containing every actual
triangle exactly once. Put H=A+7I over the integers and G=H mod 3=A+I over F3.
Let V=ker G. Then dim V=44. The expression

    beta(x,y) = (xhat^T H yhat)/3 mod 3,  x,y in V,

with arbitrary integer lifts xhat,yhat, is a well-defined symmetric bilinear
form of rank 43 and radical precisely the line spanned by the all-one vector j.
The space L=ker(N^T mod 3) contains j and is totally isotropic for beta.
Consequently dim L<=22 and 77<=rank_F3 N<=98.

These are necessary conditions for the complete target only. They do not force
a nonconstant vector in L, a particular small unbalanced right-kernel circuit,
rank N<=97, any fixed-support occurrence, or existence/nonexistence of A.

## Exact target identities and the already known first rank layer

Every edge lies in exactly one triangle because lambda=1. Each vertex lies in
seven triangles: its 14 neighbors are paired by their unique common-neighbor
edge. Thus N j_231=7 j and N^T j=3 j_231, and NN^T=A+7I=H.
The target identity A^2=12I-A+2J and Aj=14j gives over F3

    G^2-G=2J=-J, GJ=0, J^2=0.

Let E=G^2=G-J. Then E^2=E and G=E+J. The integer characteristic polynomial
of A is (t-14)(t-3)^54(t+4)^44. This follows from the nonprincipal roots 3,-4
of t^2+t-12 and trace A=0, together with the degree-14 principal root.
Hence the characteristic polynomial of G over F3 is t^45(t-1)^54.
Its nonzero generalized eigenspace has dimension 54, and E is identity there;
on the zero generalized eigenspace E is zero. Thus rank E=54.

Alternatively E being idempotent means its only eigenvalues are 0 and 1 and
it is diagonalizable; the displayed polynomial of G gives those dimensions.
The decomposition F3^99=im E direct-sum ker E is orthogonal because E is
symmetric. We have Ej=0 and EJ=JE=0. The restriction of G to im E is identity;
its restriction to ker E is the nonzero rank-one map J. It is nonzero there
because J annihilates im E and is nonzero on the whole space. Consequently
rank G=55 and dim V=44.

If Gx=0, then Ex=G^2x=0, whence Jx=(G-E)x=0. In particular sum x=0 over F3.
The nonzero vector j belongs to V since Hj=21j, and 99=0 over F3.
The E/G ranks are historical premises rather than a new novelty claim.

## The divided form is independent of every lift choice

For y in V, H yhat is divisible by 3 in every coordinate; hence the numerator
defining beta is divisible by 3. Replacing xhat by xhat+3u changes beta by
u^T H yhat mod 3, which is zero. Replacing yhat by yhat+3v is likewise harmless.
The simultaneous change includes 3u^T H v after division and is also zero.
Therefore beta is a bilinear symmetric form on V, not a lift-dependent
rational quotient or an ordinary Euclidean dot product.

## Local symmetric congruence, not unjustified Smith congruence

Work in the discrete valuation ring R=Z_(3), whose units have denominators and
numerators prime to 3. A change of basis by an invertible matrix over R induces
an invertible change of basis over F3. The following elementary symmetric
elimination justifies the needed congruence directly.

If a symmetric matrix over R has a unit diagonal entry, split that one
direction from its orthogonal complement by subtracting the appropriate unit
multiple of the pivot vector. This is an invertible congruence over R. If its
reduction is nonzero but every diagonal is divisible by 3, some off-diagonal
entry h_ij is a unit. The vector e_i+e_j has norm h_ii+2h_ij+h_jj, a unit since
2 is a unit. Replace one basis vector by e_i+e_j and then perform the same
orthogonal split. Repeating splits exactly rank(G)=55 unit directions, leaving
a 44-dimensional symmetric block all of whose entries are divisible by 3.
Thus H is congruent over R to U direct-sum 3D, with U of dimension 55 and
unit determinant, and D symmetric of dimension 44. This argument uses no
claim that an arbitrary Smith equivalence is a symmetric congruence.

The exact real eigenvalues of H are 21, 10 with multiplicity 54, and 3 with
multiplicity 44. Therefore

    det H = 21 * 10^54 * 3^44, v_3(det H)=45.

Congruence changes determinant by the square of a unit, so v_3(det D)=1.
Apply the same symmetric unit elimination to D. If rank(D mod 3)=r, the
remaining 44-r block is divisible by 3, which forces v_3(det D)>=44-r.
Thus r>=43. It cannot be 44 because det D is not a unit. Hence r=43.

In the congruence basis, V consists of the 44 last coordinates modulo 3,
and the divided form beta on V is represented by D mod 3. Therefore beta
has rank 43 and a one-dimensional radical. For y in V,

    beta(j,y)=21 sum(yhat)/3 = 7 sum(yhat)=0 mod 3.

Since j is nonzero, its span is exactly the radical. This proves the full
form statement with an explicit local diagonalization justification.

## The incidence left kernel is beta-isotropic

For x,y in L, choose integer lifts with N^T xhat=3z and N^T yhat=3w.
Then Hx=NN^T x=0 mod 3, so L is contained in V, and

    xhat^T H yhat = (N^T xhat)^T(N^T yhat)=9z^T w.

After division by 3 this is zero modulo 3. Thus beta vanishes on L times L.
Also j belongs to L because every incidence column has three ones.
The quotient V/<j> is nondegenerate of dimension 43. If ell=dim L, its
totally isotropic subspace L/<j> has dimension ell-1. A totally isotropic
subspace W of a nondegenerate bilinear space lies in its orthogonal
complement, so 2 dim W<=43. Therefore ell<=22, and rank N=99-ell>=77.
The constant left kernel supplies the upper bound rank N<=98.

There is also a shorter determinant-only rank bound: every 99-column minor
of N is divisible by 3^(99-r) if rank_F3 N=r. Cauchy-Binet expresses det H
as a sum of their squares, forcing 2(99-r)<=45 and r>=77. This floor appeared
as a subsidiary candidate observation in the earlier upper98 paper. The
present form argument additionally identifies the canonical 43-dimensional
quotient and the exact secondary isotropy constraint. It is not advertised
as a novel floor or as an approval of that earlier subsidiary observation.

## Hand falsification boundaries and useful limits

For the 3-by-3 rook graph, parameters are (9,4,1,2). Its incidence matrix has
nine rows and six triangle columns (three rows and three columns of the board).
Its row degree is 2, not 7. Here NN^T=A+2I has real eigenvalues 6,3^4,0^4
and is singular; its incidence rank over the reals is 5. Over F3 its Gram is
G_rook=A-I, with G_rook^2=2J and G_rook^3=0. The target determinant valuation
and rank-55 decomposition cannot be transferred to this parameter analogue.

The four-corner vector

    x = [[1,-1,0],[-1,1,0],[0,0,0]]

has exactly zero integer row/column sums, so N^T x=0, yet x^T x=4=1 mod 3.
This falsifies an ordinary-dot-product self-orthogonality shortcut. The divided
Gram form still vanishes on it, as the incidence factorization requires.

The target argument requires the full integer SRG identity and its complete
triangle factorization. Lambda-one regularity by itself does not provide the
determinant spectrum. The existing genuine 99-vertex lambda-one degree-14
fixture with ternary incidence rank 98 remains compatible with this floor and
does not supply an extra nonconstant kernel vector. Prime 3 and its odd-unit
congruence step are essential; no binary-rank claim follows here.

The strongest immediate unrestricted constraint is a canonical secondary
isotropy requirement on every proposed ternary incidence left kernel, with
dimension at most 22. It may challenge a future exact completion or coding
proposal. It supplies no automatic obstruction for the current fixed17
relaxation, no better universal small-right-circuit upper bound, and no theorem
that a circuit of weight12 must exist. Any numerical screen needs a separate
frozen criterion, bounded allocation and independent artifact verifier.

## Shared origin and bounded archive comparison

Root requested the G/E incidence attack and separately suggested the divided
form checks after my derivation. The complete local congruence and isotropy
argument above is Structural's discovery candidate; Root agreement is not its
verification. Existing target modular-rank and affine/upper98 proofs are
retained as historical exact work.

Compared in full on paper: current target modular-rank audit and GF3 hollow
residual derivation; current nonconstant-kernel design, Griesmer and upper98
candidates; historical external archive Wave170 block-profile ternary code,
Wave171 centered code, and Wave191 star-module proof. Wave170 already states
rank G=55. Wave191's rank<=82 endpoint depends on an extra centered-rank11
assumption and is not an unrestricted target bound. The earlier upper98
candidate contains the subsidiary determinant floor77. No current exact
registered floor77/divided-form claim was identified in this bounded review;
this is not an exhaustive novelty claim about the entire archive.

Written boundaries: lift changes separately and jointly; unit diagonal pivot;
unit off-diagonal pivot; exactly55 first unit directions; determinant valuation;
D rank43; constant radical; quotient isotropy dimension; ordinary-dot-product
rook counterexample; singular-rook determinant boundary; additional-left-kernel
nonimplication; no transfer between binary and ternary ranks. All are written
arguments, with zero executable controls/formal/external checks.
