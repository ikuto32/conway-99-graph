# Independent written audit: the whole K2,6 integer lift

Verifier `/root/structural`; discovery producer `/root`. Actual review
clock `2026-10-03T09:39:55+00:00`; source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. The complete immutable candidate
`docs/CANDIDATE_20261003_TERNARY_K2_6_INTEGER_LIFT_V1.md`, SHA256
`4efb2e1ffbcf4bf8c310c3521b175e570b93e1ed7ef18d20cbecaf05dea55260`,
was read and not changed. This is a separate exact written derivation and
falsification review, with zero mathematical computational commands,
executed fixtures or formal-prover checks. No external review or novelty
assertion is supplied.

## Exact revision-1 statement verified

For every symmetric binary integer 99-by-99 matrix A with zero diagonal
and exactly 14 ones in every integer row, set R=A^2+A-12I-2J and M=R modulo
3 over GF(3). The whole nonzero unordered off-diagonal support graph of M
cannot be isomorphic to K2,6. Empty support is permitted. This excludes
neither an arbitrary K2,6 component inside a larger support nor all
twelve-edge supports, and supplies no target resolution, incidence-rank
bound, optimum or realization of another defect count.

The material dependency is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`, ROOT report
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`,
and written audit `acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`,
SHA256 `0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`.
Structural authored the original filter discovery, source
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
This relationship is disclosed; the needed elementary filter identities
are rederived below. No defect-lower12, ten-defect result, spectral-parity
claim, matching catalogue or incidence lemma is used.

## Reconstructing the saturated integer residual

Integer R is symmetric, has diagonal zero and row sum
196+14-12-198=0. Its off-diagonal entries CN(u,v)+A_uv-2 are at least -2.
A good entry is a nonnegative multiple of 3. Residues 1 and 2 have minima
-2 and -1. Because A is symmetric and regular, AJ=JA, so A commutes with
R over the integers and with M over GF(3).

Let the whole support be K2,6, with high vertices a,b, lows L and whole
vertex set S of size 8. M is zero outside S. On the (outside,S) block,
commutation gives A[outside,S]M_S=0. Each low row has two opposite labels,
so each binary outside row has equal coordinates at a,b. Thus a,b have
identical outside neighborhoods. If that shared size is t, their internal
degrees are both d=14-t. The full CN is at least
14-d+max(0,2d-8), hence at least 10. Their M pair is zero, so R_ab is a
good multiple of 3, at least 9, regardless of A_ab.

Let c count residue-1 labels from a to the six lows. The signed high row
is c+2(6-c)=12-c, so c is exactly 0,3 or 6. The low rows make the b labels
opposite. Available negative budgets are beta_a=6+c and beta_b=12-c.
When c=0 or 6 one budget is 6, contradicting R_ab>=9. For c=3 both budgets
are 9. Their zero integer row sums bound the good R_ab above by 9, so
R_ab=9. Equality requires every one of the six high-low entries to attain
its individual minimum, three -2 and three -1 at each high, and every
other good high-row entry to be zero. This is an exact saturation argument,
not a choice of a convenient residual lift.

Every vertex outside S has only good R entries. They are nonnegative and
sum to zero, so its complete integer row is zero; symmetry also zeros
the corresponding columns. Each low has high residuals -2 and -1, summing
to -3. Its other entries are good nonnegative multiples of 3. Outside
entries are zero and its own diagonal is zero. Exactly one other low
therefore has residual 3, all others zero. Symmetry makes these six chosen
partners a perfect matching. No matching/sign incidence type is assumed.

Let P be its 6-by-6 adjacency matrix: P is symmetric, P1=1 and P^2=I.
Set s_i=1 when R_ai=-2 and s_i=-1 when R_ai=-1. Then s has three of each
sign, sum s=0 and squared norm 6. With lows ordered arbitrarily, the
complete nonzero block of the integer matrix R is forced to be

  R_S = [[0,9,C_a], [9,0,C_b], [C_a^T,C_b^T,3P]],
  C_a=-(3/2)1^T-(1/2)s^T,
  C_b=-(3/2)1^T+(1/2)s^T.

These fractions encode integer entries -2/-1 exactly. No relaxation or
field-to-integer label identification has been made.

## Exact simplicity certificate for eigenvalue 12

Work over the real numbers with this symmetric integer R. Let U consist
of vectors having the same value x at the two highs and the same value y
at the six lows. Its invariance follows from the high cross sums -9,
the low cross sums -3 and P1=1. On these constant coordinates the action is

  (x,y) -> (9x-9y,-3x+3y).

The quotient matrix has determinant 0 and trace 12; its two eigenvalues
are 0 and 12. The ordinary coordinate metric here has weights 2 and 6;
the quotient matrix's nonsymmetric appearance is not used as a Euclidean
operator-norm claim. An exact eigenvector for 12 is

  z=(-3,-3,1,1,1,1,1,1,0,...,0).

Its sum is zero, and direct row multiplication gives high values -36
and low values 12. The constant vector on S is the distinct zero
eigenvector, not another 12 eigenvector.

U's real orthogonal complement within S has vectors with highs (x,-x)
and low vector l satisfying sum l=0. Symmetry and U invariance make this
complement invariant. I independently expand its quadratic form and norm:

  Q=-18x^2-2x s^T l+3l^T P l,
  ||v||^2=2x^2+||l||^2.

The -18 term counts the two high-high products; the cross term includes
both symmetric copies of the high-low block, with C_a-C_b=-s. To check the
bound independently of a numerical spectrum or Cauchy estimate, there is
the exact sum-of-squares identity

  4||v||^2-Q
    =20x^2+||l+x s||^2+(3/2)||l-Pl||^2 >=0.

Indeed ||s||^2=6, P^T P=I and P=P^T, so the right side expands to
26x^2+4||l||^2+2x s^T l-3l^T P l, exactly the left side. The identity
actually holds for all l; the zero-sum restriction is only needed to
identify the invariant complement. Thus every eigenvalue on that
complement is at most 4, for every matching P and sign vector s as above.

The outside-S coordinate subspace has eigenvalue zero because its complete
integer rows/columns vanish. The direct orthogonal decomposition has
dimensions 2+6+91=99. Only U supplies eigenvalue 12 and supplies it once.
Therefore 12 is simple in the complete 99-by-99 matrix R. This addresses
the complete matrix, not only the support's quotient block.

## Integrality obstruction under the actual adjacency lift

A commutes with R and must preserve its one-dimensional real 12-eigenspace.
Hence Az=theta z. At any low coordinate z_i=1, theta=(Az)_i is an integer,
because A and z are integer. No rational-eigenvector normalization or
unproven incidence rank statement is required. Since Jz=0, the defining
integer polynomial gives

  12z=(A^2+A-12I-2J)z=(theta^2+theta-12)z,
  theta^2+theta-24=0.

The discriminant is 97, strictly between 81=9^2 and 100=10^2; it is not
an integer square. There is no integer theta, a contradiction. Equivalently
integer theta would make (2theta+1)^2=97. This independently confirms the
candidate whole-K2,6 nonrealizability statement.

## Fourteen written counterattacks and applicability checks

1. c=0,3,6 exhaust the signed high row; the unbalanced cases have a
   beta-6 endpoint and cannot be silently retained.
2. The high pair lower bound is rounded to 9 because it is good. Both
   saturation endpoints have upper bound 9; no residual value 12 fits.
3. Saturation forces all six minima and all other good high entries zero;
   it is not an arbitrarily chosen convenient integer lift.
4. Every outside integer row is zero by nonnegative good entries and zero
   row sum. This argument requires the whole support, not a component.
5. Each low's negative sum is exactly -3, so there is exactly one positive
   good entry of 3. Symmetry and zero diagonal force a perfect matching.
6. The half-integer block notation gives only the integers -2,-1. It does
   not replace integer R by its smaller field residues.
7. U invariance, eigenvalues 0/12 and weighted constant-coordinate metric
   were separately checked. The zero eigenvector does not duplicate 12.
8. The quadratic form's symmetric cross factor is -2x s^T l, and the
   high-difference norm is 2x^2. Either missing factor would spoil the bound.
9. The displayed exact sum-of-squares certificate uses no relation between
   P and s beyond matching orthogonality and ||s||^2=6; no matching type is
   omitted and no floating diagonalization is used.
10. The invariant complement and all 91 outside coordinates have been
    included, proving simplicity in the complete99 domain.
11. theta is integer at a coordinate equal to 1 and Jz=0. A failure of
    simplicity or nonzero Jz would invalidate the polynomial scalar step.
12. The discriminant97 and integer-square interval81..100 are exact; no
    eigenvalue approximation or assumed rational root is used.
13. The signed field-level K2,6 can have zero rows and nilpotent cube. This
    proof leaves that algebraic fact intact and rejects its actual integer
    adjacency lift; it does not reject all abstract signed matrices.
14. Other twelve-edge supports and a K2,6 component of a larger residual
    support are outside this statement. M=0 and a target solution remain
    allowed; no heuristic kernel/gate or fixed371 publication is changed.

## Verdict and verification limits

**PASS** by complete internal different-author written derivation for the
exact revision-1 statement above. Trusted mathematics is exact integer and
GF(3) arithmetic, real sum-of-squares inequalities and finite-dimensional
symmetric spectral decomposition. Mathematical executions, graph fixtures,
formal proof certificates and external review are zero or absent. Novelty:
UNKNOWN; target resolution: NONE; general twelve-defect coverage: not claimed.

The candidate and this audit are LOCAL_ONLY working artifacts, not asserted
present in the source context commit. No candidate, ledger, index, Git state,
heuristic source or frozen publication notice was modified. No live worker
state is inferred from this written timestamp or historical receipts.
