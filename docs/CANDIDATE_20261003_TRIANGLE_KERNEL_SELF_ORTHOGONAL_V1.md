# Candidate triangle-kernel containment from the integral derived incidence

Status: CANDIDATE exact written derivation, pending an independent checking path.
No calculation, optimizer, graph search, claim registration or mathematical
promotion is performed by this note. Quantifiers concern every complete99x99
symmetric binary zero-diagonal matrix A satisfying `A^2=12I-A+2J` over integers.
No target automorphism, prism absence, nonzero kernel or upper rank is assumed.
Novelty/external review are UNKNOWN.

This is a separate extension of the preserved candidate projection/hull note
`CANDIDATE_20261003_TRIANGLE_IMAGE_PROJECTION_HULL_V1.md`, SHA256
158bd3514bfdb087c7ad61ff907bb42e37db843bb9a4fde026d76377c0a3233c.
All triangle and matrix definitions below are explicit; the earlier note is
not treated as an independently VERIFIED premise.

## Exact integral identity and binary containment

Let B be the complete99x231 vertex-by-triangle incidence matrix. Every edge has
one common neighbor, so each vertex lies in seven triangles and
`BB^T=7I+A` over integers. Put `K=ker_F2(B^T)` and `D=im_F2(B)=K^perp`.
Reduction modulo2 gives `A^2=A` and `BB^T=I+A`; hence every u in K satisfies
`Au=u` over F2.

Define `Q=(A-2I)B` over integers. The entry for a triangle containing its row
vertex is0 after subtraction. For an external vertex, adjacency to two vertices
of a triangle would give their edge two common neighbors, so Q's entry is0 or1.
Thus Q is an actual binary matrix. Expanding the SRG identity gives

`A^3=13A-12I+26J`,
`QQ^T=(A-2I)^2(7I+A)=52I-14A+32J`.

Now take the0/1 integer lift of any u in K. Since
`Q^Tu=(B^T(A-2I))u=0` modulo2, the vector

`z=Q^Tu/2`

is integral. Therefore, over integers and then modulo2,

`Qz=(QQ^T/2)u=(26I-7A+16J)u`,
`Qz=Au=u` modulo2.

Consequently u belongs to im_F2(Q). This image is contained in D: indeed
modulo2, `Q=AB=B(I+B^TB)`, using `A=I+BB^T`. We obtain

`K subset im_F2(Q) subset D=K^perp`.

In particular K is self-orthogonal. This conclusion uses the exact integral
Gram identity and division by2; it does not follow from generic codomain
isotropy. It is compatible with K=0 and with rank_F2(B)=99. It therefore
establishes no nonzero kernel, rank upper bound or target contradiction.

## Possible finite code-enumerator screen, not launched

Let `A_w=|{u in K:wt(u)=w}|`, `M=|K|`, and
`K_j(w)=sum_s(-1)^s binom(w,s)binom(99-w,j-s)` with zero binomial convention.
Character orthogonality gives

`M*|{d in D:wt(d)=j}|=binom(99,j)+sum_(w>0)A_w K_j(w)`.

Since K is contained in D, a necessary additional condition is

`M*A_j <= binom(99,j)+sum_(w>0)A_w K_j(w)`

for every j. Its exact scope is the target-kernel enumerator, not a generic
binary code or complete graph construction. The independently checked earlier
weight36..60 and size<2^15 results, if explicitly reused, freeze possible sizes
M=2^k with0<=k<=14 and thirteen positive weight variables36,38,...,60. Fixing
one size gives literal linear inequalities plus `sum_(w>0)A_w=2^k-1`.

This suggests a cheap diagnostic at k=14 followed by separately declared
smaller sizes only if justified. It is not a promised improvement: the image
D has very high dimension, so these extra word-count inequalities may be weak.
Before any optimizer, a separate verifier must derive this containment and
character transform, calibrate positive/corrupted fixtures, and freeze the
full exact coefficients/size/scopes. Numerical output alone would establish
nothing; an exclusion needs a complete independently checked exact certificate.

Self-orthogonality also says that all pairwise kernel-word intersections are
even. It does not prove that every kernel weight is divisible by4. On a
self-orthogonal code, `wt(u)/2 mod2` is linear; its zero case and nonzero case
may be distinguished by independently derived shadow/enumerator constraints,
but no such extra restriction or computation is asserted here.
