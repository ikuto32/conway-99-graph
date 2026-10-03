# Independent written audit: ten ternary defects

Verifier: `/root/structural`; discovery producer: `/root`. Actual review
timestamp `2026-10-03T09:07:20+00:00`; source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. Reviewed immutable candidate:
`docs/CANDIDATE_20261003_TERNARY_TEN_DEFECT_NONREALIZABILITY_V1.md`, SHA256
`d4f981d99c13643becbcf621b7b7707825bd6f079ca06611a252c788f27beb72`.
The complete candidate was read. It was not edited. This is a different
author's exact written derivation and attempted falsification, not a formal
proof, external peer review, numerical result or executed graph fixture.

## Exact revision-1 statement checked

For every symmetric binary integer 99-by-99 matrix A with zero diagonal
and exactly 14 ones in each integer row, let
R=A^2+A-12I-2J and M=R modulo 3 over GF(3). The number F3 of unordered
off-diagonal pairs with M_uv nonzero cannot equal 10. This statement allows
M=0 and supplies no target resolution, incidence-rank bound, optimum,
realization of another defect count or exclusion of an arbitrary component
inside a larger residual support.

The candidate references the verifier's earlier discovery
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
That source relationship is disclosed. I do not treat its unregistered
claim or my authorship as a verification premise: the needed equal-pair
filter is derived fully below from the adjacency definitions. No prior
ledger theorem, subcubic classification, eigenvalue parity or finite
isomorphism catalogue is imported. ROOT's ten-defect discovery is separately
checked by Structural; the shared elementary subproof and integer/field
definitions are explicitly disclosed rather than claimed independently
invented twice.

## Deriving the complete-support and signed-budget filter

Write H for the whole nonzero off-diagonal support of M, S for its whole
nonisolated vertex set, T for its complement, m=|S| and e=|E(H)|. R is
symmetric. Its diagonal is 14-12-2=0 and its integer row sum is
196+14-12-198=0. Off-diagonal R_uv=CN(u,v)+A_uv-2 is at least -2.
If M_uv=0 this residual is a nonnegative multiple of three. A residue-1
entry has minimum -2 and a residue-2 entry has minimum -1.

For u, let c1,c2 count its nonzero residues and let d=c1+c2 be its support
degree. The maximum available negative budget is beta=2c1+c2. Since M1=0,
c1+2c2 is zero modulo three, so beta is also zero modulo three. Together
with beta<=2d this gives beta<=3 floor(2d/3), in particular beta<=6 for d<=4.
If a paired entry is good, its residual is at most beta. If it has residue
1 or 2, its residual is at most beta-2 or beta-1 respectively. These bounds
give every other bad entry its individual minimum and every other good
entry zero; a paired positive term is not counted as negative capacity.

A is symmetric and regular, so AJ=JA. Therefore AM=MA. M is zero outside
S and has zero diagonal, so it has block form diag(M_S,0). Commutation on
the (T,S) block gives A[T,S]M_S=0. Each outside row is an exactly binary
kernel word. No adjacency-program cache or sampled CN calculation is used.

If support vertices u,v have the same outside-S adjacency neighborhood,
of size t, their internal adjacency degrees are both d_A=14-t. The two
internal neighbor sets lie in S and have intersection of size at least
max(0,2d_A-m). Hence their full integer CN is at least

  14-d_A+max(0,2d_A-m) >= 14-floor(m/2).

For m<=11 this is at least 9 and R_uv is at least 7. A good R_uv is
therefore at least 9, exceeding beta<=6 at a support degree-at-most-4
endpoint. A bad R_uv is at least 7, exceeding the remaining budget at
most 5 at that endpoint. This proves that neither endpoint of such an
equal-outside pair can have support degree at most 4.

A support degree-2 row has opposite nonzero labels. Its binary outside
equation forces its two support neighbors to have equal outside adjacency
coordinates at every z in T. A support degree-3 row has three equal labels:
three nonzero elements of GF(3) sum to zero only when all three agree.
Its binary equation has coordinate sum 0 or 3, so its three neighbors
likewise have identical outside neighborhoods. Consequently, for m<=11,
the two neighbors of any degree-2 vertex and the three neighbors of any
degree-3 vertex all have support degree at least 5.

## Exhaustive degree deductions when e=10

A support vertex has degree at least 2: degree 1 violates its zero signed
row sum. Therefore m<=10. Since a simple graph on at most four vertices
has at most six edges, m>=5. The just-derived filter applies on this range.

A degree-3 vertex and its three distinct degree-at-least-5 neighbors
would require total degree at least 3+15+2(m-4)=2m+10. With total degree
20, this permits only m<=5, but m=5 has maximum degree 4. Thus there is
no degree-3 vertex.

If there is a degree-2 vertex, its two distinct neighbors have degree at
least 5, requiring 20>=10+2(m-2)=2m+6 and hence m<=7. The m=5 case cannot
contain the required high vertices. I checked the remaining m=6 and m=7
cases separately; no unlisted support or connectivity assumption is used.

At m=6, the two high vertices must have degree exactly 5 and be adjacent
to every other support vertex. Four remaining vertices have degree at
least 2. Their base contribution yields total 18, leaving excess 2.
Degree 3 is absent, so exactly one remaining vertex would have degree 4
and three would have degree 2; another degree-5 vertex would cost excess
3 and exceed the total. Each of the three degree-2 vertices already uses
both edges on the universal high vertices. They cannot connect to the
degree-4 vertex, which consequently has only its two universal edges.
This contradiction excludes m=6, without assuming an isomorphism list.

At m=7, the lower bound 2m+6 is exactly 20. The two high vertices have
degree 5 and the five other vertices degree 2. Every low vertex must join
the two high vertices, so the high vertices already have their five
incident edges and cannot join each other. The support is literally K2,5.

If there is no degree-2 vertex, all degrees are at least 4, since degree
3 was excluded. Then 20>=4m forces m=5 and all five degrees are 4. The
support is literally K5. In particular m=8,9,10 cannot conceal another
case: degrees 2 or 3 have already been excluded at those orders and the
minimum-4 total is too large. These are exhaustive degree arguments, not
executed graph enumeration or assumed automorphism equivalence of A.

## K2,5: field feasibility survives but the integer budget does not

Let a,b be the two high vertices. Every low row says M_wa=-M_wb.
If c labels from a are 1, its row sum is c+2(5-c)=10-c, so c=1 or 4.
Its beta is 2c+(5-c)=5+c, namely 6 or 9. The opposite labels from b
give beta_b=10-c, namely 9 or 6. For example labels (1,2,2,2,2) from a
and (2,1,1,1,1) from b give zero signed rows. Thus field feasibility is
not falsely rejected.

Every low degree-2 row forces a,b to have identical outside neighborhoods.
For m=7 their full CN is at least 14-floor(7/2)=11, so R_ab>=9 regardless
of the binary value A_ab. The pair is not a support edge, so its residual
is good and at most either endpoint's beta. One beta is 6, contradicting
9. The argument needs no fixed A_ab or global lambda-one property.

## K5: both product types and the complete field kernel

Each row has degree 4. If c labels are 1, its row sum is c+2(4-c)=8-c;
zero modulo three forces c=2. The positive edges therefore form a simple
2-regular graph on five vertices. A component is a cycle of length at
least 3. Five vertices cannot split into two such components, so it is
a single C5, and its complement is the negative C5. Choosing cyclic
labels 0,...,4 merely describes this signed matrix; it does not impose
an automorphism or labeling convention on the graph A.

Let B have +1 at cyclic distance 1 and -1 at cyclic distance 2. Its
diagonal square entries are four. I independently checked the two kinds
of off-diagonal pair over the integers:

  pair (0,1), intermediate vertices 2,3,4:
    B02*B21=-1, B03*B31=+1, B04*B41=-1, sum=-1;
  pair (0,2), intermediate vertices 1,3,4:
    B01*B12=+1, B03*B32=-1, B04*B42=-1, sum=-1.

Cyclic reindexing covers every pair within each type, so B^2=5I-J over
the integers, and B^2=2I-J over GF(3). If Bx=0, then 2x=Jx, whose right
side is constant; every coordinate of x is therefore equal. Conversely
B1=0, proving the entire kernel is exactly the constant line. Symmetry
also identifies the left kernel. Negating all labels exchanges the two
cycles and leaves the square and kernel unchanged; that sign choice is
not an omitted support case.

Thus every binary outside row of A[T,S] is zero or all one. All five
support vertices have identical outside neighborhoods, contradicting the
degree-4 endpoint filter. The binary all-one word has weight 5 and is
allowed by adjacency degree 14; the contradiction is the full integer
CN/negative budget, not a mistaken Hamming-weight veto.

## Twelve written falsification and boundary checks

1. Checked the complete 99/14 integer diagonal and row identities, and
   good-residue nonnegativity. A different order/degree needs a new proof.
2. Checked the distinct residue minima -2/-1 and removal of the paired
   positive entry from its available budget. beta is a multiple of 3.
3. At m=11 the good/bad lower residual bounds 9/7 exceed 6/5 respectively.
   At m=12 a coarse good residual 6 could meet budget 6; the general
   filter is not silently extended to that endpoint.
4. Checked that binary sums at a degree-3 row can only be 0 or 3. The
   ternary tuple (0,1,2) would invalidate equality and is not permitted.
5. The m=5 and no-low-degree alternatives are forced by simple degree
   counts; a degree-five vertex cannot occur at m=5.
6. The m=6 excess calculation and universal-neighbor constraints are
   complete. Neither two degree-3 vertices nor a third degree-5 vertex
   can be substituted for the impossible remaining degree-4 vertex.
7. The m=7 bound forces both high degrees exactly 5 and all lows 2; an
   extra high-high edge or another high vertex would exceed total 20.
8. K2,5 has an explicit zero-row signed assignment. Its exclusion really
   uses the beta-6 endpoint after the integer CN lift, not field failure.
9. A simple 2-regular graph on five vertices has no two-cycle component.
   Both signed C5 product types and both overall sign choices were checked.
10. The constant-only K5 kernel includes an allowed binary weight-5 word.
    Equality of outside neighborhoods, not constant-word absence, is used.
11. S is the whole residual support. No arbitrary ten-edge component in
    a larger support is excluded; M-support edges need not be A edges.
12. M=0 and other defect counts remain allowed by this statement. There
    is no target construction/nonexistence, incidence-rank, global optimum,
    algorithm gate, executable fixture or external-review assertion.

## Verdict and provenance limits

**PASS** for the exact revision-1 statement F3!=10 on the stated complete
domain. Every necessary subproof has been derived here, including the
previously discovered equal-neighborhood filter, and every remaining
support shape has been eliminated. This internal different-author written
verification is not a formal proof certificate or an executed finite test.
Mathematical commands and fixtures: zero; graph realizations tested: zero;
external review: absent; novelty: UNKNOWN; target resolution: NONE.

The source context does not assert that this audit or new report is already
committed. Files remain LOCAL_ONLY pending separate immutable publication.
No registry, index, Git state, frozen 371-claim document or heuristic source
was changed by this verification. No live computational-worker status is
inferred from this document or an earlier receipt.
