# Target affine obstruction and a minimum unbalanced triangle circuit

Status: **CANDIDATE**, paper-only preparation 2026-10-03T13:05:11+00:00 by
`/root/structural`. The affine obstruction was proposed by `/root` in this
research conversation; the proof here and the minimum-support circuit argument
are independently reconstructed by `/root/structural`. This is a transparent
shared-origin discovery note, not a verification report or self-approval.
Source context `d0c0dd7db0d3de420b1d718b59122b069df01107`; observed ledger SHA256
`a0ed6dfb9716266e44dd8cdbef00620266190fa1bce0852a11bbabbf8d09416e`.
Zero mathematical execution, fixture enumeration, formal checking or external
review. Novelty is unknown. No ledger/index or historical source is changed.

## Quantified proposed consequence

Suppose A is the adjacency matrix of a simple degree-14 graph on 99 vertices
having adjacent CN=1 and nonadjacent CN=2. Let B be its binary point-by-triangle
incidence matrix, with every actual triangle included once. Then B has shape
99 by 231, row weight seven, column weight three, and BB^T=A+7I over the integers.

Over GF(3), there is no x satisfying B^T x=1_231. There is a vector z in ker(B)
with sum(z) nonzero. Choose such z with support cardinality minimum. Its selected
columns form a genuine GF(3) matroid circuit, its nonzero coordinates are +1 or
-1, and its number w of selected triangles satisfies w<=99. This statement
does not force an extra nonconstant vector in ker(B^T), or any upper bound of
72 on binary rank. It does not resolve target existence.

## 1. Reconstructing every required incidence premise

Every edge has exactly one triangle completion. Distinct actual triangles
cannot share an edge. Around a point, its fourteen neighbors are paired by
the seven triangles containing that point. Counting point-triangle incidences
gives 99*7/3=231 triangles. The diagonal of BB^T is seven; on an adjacent pair
it is one, and on a nonadjacent pair zero. These are integer identities.

Put N=A+I and P=A+I-J over GF(3), where J is the 99 by 99 all-ones matrix.
The target common-neighbor identity is A^2=12I-A+2J over the integers. Reducing
it gives

```
N^2=N-J=P,        NJ=JN=0,        J^2=0,
P^2=P,           P*1_99=0,
BB^T=N,          B*1_231=1_99,    B^T*1_99=0.
```

Here NJ=0 uses degree 14, so (A+I)J=15J; J^2=0 uses 99=0 over GF(3).
The projection P has the historical rank 54, whereas N has the historical
rank 55. Neither numerical rank is needed below. A prior conversational
rank-55 label for P was explicitly withdrawn by Root; it is not a premise.

## 2. The Root-origin affine obstruction

If B^T x=1_231, summing its coordinates gives

```
sum(x) = (B*1_231)^T x = sum(B^T x) = 231 = 0 over GF(3).
```

Also Nx=BB^T x=B*1_231=1_99, and Jx=0. Thus Px=1_99.
But P^2=P would imply P(Px)=Px=1_99, while P(Px)=P*1_99=0. This is a
contradiction. It excludes every nonzero constant affine right-hand side
as well, by multiplying x by the inverse of that constant.

The proof concerns a point potential whose sum on every actual triangle is
one. It is not a left-kernel dimension or coloring theorem.

## 3. Existence of a nonzero-sum right-kernel vector

The coordinate pairing on GF(3)^231 is nondegenerate. The orthogonal complement
of ker(B) is im(B^T): inclusion follows from (B^T x)^T z=x^T Bz, and equality
follows because both dimensions equal rank(B). Since 1_231 is not in im(B^T),
there exists z in ker(B) for which 1_231^T z is nonzero. Scaling normalizes
the sum to one if desired.

This uses a right kernel with triangle coordinates. It must not be confused
with the left kernel ker(B^T) with point coordinates. The constant point vector
is already in the latter, because every triangle has three points.

## 4. Minimum unbalanced support is a circuit

Choose z of minimum support among all right-kernel vectors with nonzero sum.
Suppose a proper subset of its support has a nonzero dependence h. If sum(h)
is nonzero, h is a smaller unbalanced vector, contradicting the choice of z.
If sum(h)=0, choose a coordinate i in supp(h) and put alpha=z_i/h_i.
Then z-alpha*h is still in ker(B), has the same nonzero sum as z, and has
strictly smaller support: coordinate i vanishes, and no coordinate outside
supp(z) can become nonzero. This is again a contradiction.

Thus every proper subset of the selected columns is independent and the
full selected set is dependent. It is a circuit, of column rank w-1. As
B^T*1_99=0 and 1_99 is nonzero, rank(B)<=98 over GF(3). Therefore

```
w-1 <= rank(B) <= 98,          w <= 99.
```

The space of dependencies on these w columns is one-dimensional; every
coordinate of its generator is nonzero and hence +1 or -1 over GF(3).
No bound compares GF(3) rank with binary or prime-seven rank.

## 5. Cheap exact geometry restrictions on any such word

Let S be the points used by the selected triangles and d_s the number of
selected triangles through s. Every d_s is at least two: a point incident
with just one selected column would have nonzero Bz coordinate. Also d_s<=7.
At a point, the possible counts of + and - selected coefficients are

| d_s | (+,-) possibilities |
| --- | --- |
| 2 | (1,1) |
| 3 | (3,0), (0,3) |
| 4 | (2,2) |
| 5 | (4,1), (1,4) |
| 6 | (3,3), (6,0), (0,6) |
| 7 | (5,2), (2,5) |

These exhaust the nonnegative integer pairs with sum d_s and difference
divisible by three. If p and q count + and - selected triangles, their
integer lift obeys B*z_tilde=3*t and
sum_s t_s=p-q. Nonzero coefficient sum means p-q is not divisible by three.
When all d_s=2, every point joins one + and one - triangle, and counting their
incidences gives 3p=3q. Thus an unbalanced word has a point with d_s>=3.

The selected triangle geometry is linear and has no three triangles whose
pairwise intersections are three distinct points. The latter configuration
would create a second actual triangle on an edge of one of the three original
triangles. Fix a selected point c of selected degree d. Its d triangles have
2d different outer points. Every other selected triangle contains at most
one of these outer points: two in the same c-triangle violate edge uniqueness;
two in different c-triangles create the forbidden three-triangle intersection.

Every outer point needs at least one other selected triangle. More exactly,

```
w-d >= sum_(u outer at c) (d_u-1),
w >= 3d,
sum_(u outer at c) (d_u-2) <= w-3d.
```

These inequalities count actual selected triangle roles and do not require
an induced graph on S. Together with the existence of d>=3 they give w>=9.
They do not by themselves exclude w=9,...,99. Any stronger support
classification requires its own complete derivation.

If the selected point graph is induced on S, it has 3w edges and degree 2d_s.
Writing n=|S|, its target cut and outside pair budgets would then be

```
V=14n-6w,        P=n*(n-1)-2*sum_s d_s^2.
```

The formula uses the actual induced graph. If other target edges join points
of S, their effects on q, degrees and internal CN must be included separately.
The preceding star inequality is unaffected by such added edges, because it
uses only the selected actual triangles and edge uniqueness.

## 6. Archive overlap and preserved countermodels

The following previously read sources are provenance context, not newly
verified claims or assumptions needed for the proof:

* `docs/DESIGN_20261003_TERNARY_INCIDENCE_NONCONSTANT_KERNEL_V1.md`, SHA256
  `45c27c5dcd2217c1f2b09252efa3fa5f9c0242494178c9a0fa4ee50a34b56f67`,
  already records ternary incidence Gram ranks and the coloring domain.
* `docs/DESIGN_20261003_TERNARY_REDUCED_GRAM_FULL_RANK_COUNTERMODEL_V1.md`, SHA256
  `5a5c564e052a46c4958b5e07c3d318d61e3a6fd6e84b86011866080ddc33d95a`,
  preserves a reduced-Gram rank-98 construction whose columns are not actual
  triangle incidences. Such identities alone cannot force extra left kernel.
* The archival Wave23 audit
  `external_conway99_research/verification/wave23-index-pranks/2026-07-23T192952Z-audit.md`,
  SHA256 `bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116`,
  section 7 already contains prime-seven full row rank. It is not a new result
  of this investigation. The external archive is pinned at
  `85e705cc6c2a14d123120c93a847e30aaab1789e`.

The bounded archive search did not identify an exact copy of the affine
obstruction or circuit formulation, but that is not a novelty assertion.
The historical binary rank<=72 generic implication remains rejected. The
authenticated non-target degree-14 lambda1 GF(3) rank-98 fixture remains a
counterexample to incidence-only extra-left-kernel inference. A target-specific
unbalanced right word is compatible with constant-only left kernel.

The separate twelve-line cap-core note demonstrates why local CN caps alone
cannot force all right-kernel words balanced. Its full-target completion veto
does not classify every possible circuit of the present statement. No forced
occurrence, symmetry, optimum, target exclusion or global nonexistence follows.
