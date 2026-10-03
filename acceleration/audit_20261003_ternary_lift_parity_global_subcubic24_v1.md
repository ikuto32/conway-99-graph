# Independent written audit: ternary lift parity and disconnected subcubic support

Verifier: `/root`; discovery producer: `/root/structural`. The reviewed raw
candidate is `docs/CANDIDATE_20261003_TERNARY_RESIDUE_LIFT_PARITY_GLOBAL_SUBCUBIC24_V1.md`,
SHA256 `6189d5c4014974eac958d1993d6f852dfc6bc3209c207361db15724494af7a2b`.
This is an independently written exact derivation and falsification review,
with no executed mathematical fixtures, enumeration, numerical solver or
formal-prover check. It approves two separate necessary statements, neither
of which resolves the target. The proof imports no earlier ledger theorem.

Let A be any symmetric binary 99-by-99 matrix with zero diagonal and every
integer row sum 14. Write R=A^2+A-12I-2J over the integers and M=R modulo 3.
I independently obtain R1=(196+14-12-198)1=0 and R_uu=14-12-2=0. Symmetry
and regularity give AJ=JA, so AM=MA and M=A^2+A+J over GF(3). For an off-diagonal
good pair, R_uv is a multiple of 3 and at least -2, hence is nonnegative.
These facts use no triangle decomposition or lambda-one premise.

## Separate claim 1: even primary layers at eigenvalue 1

Set N=M-I and V_k=ker N^k, with V_0=0. Because 1^T M=0, multiplication on the
left gives 1^T N^k=(-1)^k 1^T. Thus v in V_k has 1^T v=0 and Jv=0. Since A
commutes with N, both V_k and V_(k-1) are A-invariant. On V_k/V_(k-1), N acts
as zero, so the induced A satisfies q(A)=0 for q(t)=t^2+t-1.

The values of q at 0,1,2 are respectively 2,1,2 in GF(3). Therefore q is an
irreducible quadratic. An annihilated quotient is a module over the field
GF(3)[t]/q, so its GF(3) dimension is twice an integer. Consequently every
dim V_k-dim V_(k-1) is even. These differences count eigenvalue-1 Jordan
blocks of size at least k; subtracting successive differences proves that
each exact block-size multiplicity is even. In particular dim ker(M-I) is
even and rank(M-I)=99-dim ker(M-I) is odd.

The characteristic-1 primary space alone is being considered. There is no
assumption that the whole matrix splits over GF(3), no assertion about any
other eigenvalue, and no conclusion about the rank of triangle incidence.

## Separate claim 2: whole nonempty subcubic support has at least 24 vertices and edges

Let S be the complete nonisolated off-diagonal support of M, with m=|S|.
Assume it is nonempty and has maximum support degree at most 3. Since M1=0,
a support row cannot have degree 1. At degree 2 its two nonzero labels are
opposites; at degree 3 they all agree. For z outside the whole S, commutation
gives A[z,S] M[S,S]=0. Binary coordinates at the two neighbors of a degree-2
support vertex are equal. The three binary coordinates at a degree-3 support
vertex are equal, since their unweighted sum is 0 or 3. Equality therefore
propagates along even walks in each component. It does not propagate through
vertices in other support components or through support degree 4.

Take P to be the whole vertex set of a nonbipartite component, or a larger
part of a bipartite component. Its p vertices have one common outside-S
neighborhood of size t. Each has d=14-t neighbors inside S. If a_w counts
the neighbors of w in P, then sum_(w in S) a_w=pd. Direct double counting
of witnesses gives the average common-neighbor count within P as

 t + [sum_(w in S) a_w^2 - pd]/[p(p-1)].

Using sum a_w^2 >= p^2 d^2/m and t=14-d yields exactly

 14 - pm/[4(p-1)] + p(d-m/2)^2/[m(p-1)]
 >= 14 - pm/[4(p-1)].

The denominator m is the size of the entire support; no internal witnesses
in other components are dropped. For a nonbipartite component, all residuals
to its complement are good and nonnegative, so its average internal residual
is at most zero. Its average CN is at most 2. The displayed bound implies
p(48-m)<=48. A triangle component is impossible: its degree-2 opposite signs
cannot alternate around an odd cycle. Thus p>=4 and this inequality forces
m>=36.

For a bipartite part P, internal pairs are good. Each row has at most three
bad residuals, each at least -2; its total good residual budget is at most 6.
Hence the average CN within P is at most 2+6/(p-1), giving p(48-m)<=72.
If p>=3 this forces m>=24. If p=2, minimum support degree 2 and the larger-part
choice force both parts to have size 2, so this component is a C4. Its two
opposite nonzero residues have integer lower bounds -2 and -1, giving good
budget at most 3. The sharper inequality is 2(48-m)<=60, or m>=18.

If m<24, every component must consequently be a C4. Its size is a multiple
of 4 and at least 18, so the sole remaining total is m=20, with five C4s.
An alternating C4 with sign s has matrix

 s * [[0,1,0,-1],[1,0,-1,0],[0,-1,0,1],[-1,0,1,0]].

For p=(1,0,-1,0), q=(0,1,0,-1), the block sends p to 2s q and q to 2s p.
Their orthogonal complement is a two-dimensional kernel because both norms
are 2 and their mutual inner product is 0. The block's characteristic
polynomial is t^2(t^2-1), so its 1-eigenspace has dimension exactly 1 for
either nonzero s. Five blocks and the zero isolated block give dim ker(M-I)=5,
contradicting separately derived claim 1. Thus m>=24. Minimum support degree
2 then gives |E(H)|>=m>=24. Connectivity was never assumed.

## Falsification and applicability checks

- M=0 gives V_k=0 for all k and rank(M-I)=99. It survives; neither claim can
  exclude a target solution or force a nonzero incidence kernel.
- An independently prescribed alternating C4 commutes with A=0 and has row
  sums zero but has an odd 1-eigenspace. It demonstrates why commutation and
  row sums alone cannot replace the actual polynomial lift.
- Two C4s satisfy parity but violate the necessary m>=18 budget. Five satisfy
  that budget but violate parity. Six satisfy these particular necessary tests;
  no graph realization or sufficiency is inferred.
- A balanced degree-4 row with labels (1,2,1,2) permits binary coordinates
  (1,1,0,0), so the equality argument cannot be extended to degree 4.
- The Cauchy formula retains every inside-S witness. The component upper
  bounds retain all good pairs outside the selected component or part.
- The conclusions concern the entire residual support. They cannot be used
  to reject a small component when another component contains degree 4.

Outcome: both exact statements pass independent written derivation. This is
not a formal proof certificate, external review, novelty finding, exhaustive
graph search, construction, or proof of target nonexistence. All signed-matrix
examples above are written calculations; executed graph fixtures and actual
graph realizations are both zero. Shared mathematical definitions and field
arithmetic are disclosed. The stronger prior connected-spanning-99 statement
is neither imported nor weakened. This audit and its candidate remain outside
the frozen 371-claim wave42 cutoff until a separate ledger registration.
