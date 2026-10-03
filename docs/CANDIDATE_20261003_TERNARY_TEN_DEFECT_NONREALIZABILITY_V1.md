# Candidate: ten ternary residual defects cannot occur

Discovery author: `/root`. Writing reviewed at the observed tool clock
`2026-10-03T09:04:23+00:00`; exact start-of-writing timestamp is unavailable.
Source context: `63437c9b9fc2dd58b3bdfb51fc347b880b397503`; this new
working file is not asserted to occur in that commit. Status **CANDIDATE**,
pending a separate author's complete exact derivation and counterattack.
No computation, graph fixture, formal proof, ledger change or target
resolution is claimed. The timestamp records the observed review clock,
not an invented exact file-creation time.

## Exact statement and dependency

For every symmetric binary integer 99-by-99 matrix A with zero diagonal
and all row sums 14, let

    R=A^2+A-12I-2J; M=R mod 3=A^2+A+J over GF(3).

Let H be the whole off-diagonal nonzero support of M, S its nonisolated
vertex set, m=|S| and e=|E(H)|. The claim is e != 10. Empty support is
allowed. This does not assert nonexistence of the target or realizability
of any other defect count; it does not alone exclude eight or nine.

The argument uses the equal-outside-neighborhood filter and its degree-2
and degree-3 consequences in
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
This is a pinned premise, not an approval of that discovery author's
statement. Its exact elementary ingredients are repeated below so a
verifier can rederive them. No incidence, automorphism, connectivity,
subcubic, spectral-parity or catalogue assumption is used.

## Equal-neighborhood restrictions

The integer R has zero diagonal and row sums. A good entry is a
nonnegative multiple of three; bad residues 1 and 2 have minima -2 and
-1. At a support vertex u with c1,c2 entries of these residues, define
beta_u=2c1+c2. The zero GF(3) row sum makes beta a multiple of three and
beta<=3 floor(2 deg_H(u)/3). An individual paired residual is at most
beta_u for a good pair, beta_u-2 for residue 1, beta_u-1 for residue 2.

Commutation AM=MA gives X M[S,S]=0 where X=A[outside S,S]. A degree-2
row has opposite nonzero labels, so its two neighbors have identical
binary outside-S neighborhoods. A degree-3 row has three equal labels;
the binary equation forces all three neighbors' outside neighborhoods
to be identical.

If u,v have identical outside neighborhoods of size t, their internal
degrees both equal d=14-t. Thus CN(u,v)>=14-d+max(0,2d-m), which is at
least 14-floor(m/2). When m<=11 this gives R_uv>=7. A good pair then
has R_uv>=9, whereas deg_H(u)<=4 gives beta_u<=6; a bad pair's available
budget is at most five. Therefore both endpoints of an identical
outside-neighborhood pair must have support degree at least five.

## Classifying the possible support when e=10

A nonisolated support vertex cannot have degree one, since its signed
row sum is zero. Hence every degree is at least two and m<=10. Since
four vertices have only six pairs, m>=5. The equal-pair filter applies.

If any vertex has degree three, its three distinct neighbors have
degree at least five. The total degree is then at least
3+3*5+2(m-4)=2m+10. Since the total is twenty, m<=5. But on five
vertices no degree can reach five. Thus degree three is impossible.

If a vertex has degree two, its two distinct neighbors have degree at
least five. Total degree is at least 2m+6, so m<=7. On m=5 there cannot
be a degree-five vertex.

For m=6 there are at least two degree-five vertices, both universal in
H. Their degrees contribute ten; the four remaining vertices each have
at least degree two. The remaining excess over this total eighteen is
two. There is no degree three, so exactly one remaining vertex would
need degree four, with the other three of degree two. Those three have
already used both edges on the universal vertices and cannot meet the
degree-four vertex; that vertex can therefore have only its two edges
to the universal vertices, a contradiction. A third degree-five vertex
would already require total degree at least twenty-one.

For m=7 the total lower bound is exactly twenty, so there are exactly
two degree-five vertices a,b and five degree-two vertices. Every low
vertex's two neighbors must have degree at least five and therefore
are a,b. Thus H is K2,5, with no a-b support edge.

If there are no degree-two vertices, the absence of degree three gives
minimum degree four. Then 20>=4m>=20 forces m=5 and every degree four:
H is K5. Thus only K2,5 and K5 remain, without enumerating isomorphisms.

## Excluding K2,5 by exact integer budgets

For each of its five low vertices w, M_wa+M_wb=0. Let c be the number
of residue-1 labels from a. The zero row sum at a gives
c+2(5-c)=10-c=0 mod 3, hence c=1 or 4. The two high vertices consequently
have beta values 5+c equal to six and nine in some order.

A degree-two low vertex forces a and b to have identical outside-S
neighborhoods. With m=7, CN(a,b)>=14-floor(7/2)=11, so R_ab>=9.
The pair a,b is good (it is not a support edge), so R_ab is a multiple
of three and at most either endpoint's beta. The smaller beta is six,
contradicting R_ab>=9. A_ab itself was never fixed.

## Excluding K5 using its complete binary kernel

Every degree-four zero signed row must contain exactly two labels 1 and
two labels 2: if c counts label 1 then c+2(4-c)=8-c=0 mod 3, so c=2.
The label-1 edges form a simple 2-regular graph on five vertices. Every
cycle has length at least three, so this graph must be C5; its complement
is another C5. Up to choosing an ordering for the proof, M_S has label 1
on the first cycle and label -1 on its complement. This relabeling is
not an assumed automorphism of A.

Over the integers this signed matrix squares to 5I-J: each diagonal is
four, and for either distance-one or distance-two pair the three
intermediate products sum to -1. In GF(3), M_S^2=2I-J. Therefore
M_S x=0 implies 2x=Jx, forcing every coordinate equal. Conversely M_S1=0,
so ker M_S is exactly the constant line. The same conclusion holds for
left kernels because M_S is symmetric.

Every binary outside word in X M_S=0 must consequently be all zero or
all one. All five support vertices have identical outside neighborhoods.
Their support degrees are four and m=5, contradicting the equal-pair
filter. This excludes the second and last possible support and proves
the candidate statement.

## Written falsification boundaries

* K2,5 can satisfy the field row equations with c=1 or 4. It is the
  integer lift and smaller endpoint budget that exclude it, not a false
  assertion that its signed support is impossible over GF(3).
* In the K5 case, 2-regularity on five simple vertices has no triangle
  plus 2-cycle option: a simple graph has no length-two cycle.
* Both classes of off-diagonal products of the signed C5 matrix must be
  checked. Ordinary diagonal four reduces to one, matching 2I-J.
* The constant field kernel contains the binary all-one word of weight
  five. That word is allowed by graph degree fourteen; it is equality
  of outside neighborhoods and the exact budget, not a weight veto,
  that yields the contradiction.
* The proof uses the complete support S. An isolated ten-edge component
  within a larger residual support does not satisfy the outside-zero
  premise and is not excluded by this statement.
* No unchanged heuristic driver or checker imports this candidate. No
  executable fixtures, formal proof, external review or graph realization
  have been supplied, and no target-wide coverage measure follows.

The verifier should derive every support degree case and both signed C5
product types independently, and try to construct a counterexample to
the intermediate signed-support claims. A discovery author must not
approve this claim.
