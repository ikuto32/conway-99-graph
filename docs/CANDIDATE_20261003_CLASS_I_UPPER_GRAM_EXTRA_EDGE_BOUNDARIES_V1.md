# Candidate: class-I extra-edge boundaries and a principal-Gram repair

Claim `C-SEVENTEEN-POINT-CLASS-I-UPPER-GRAM-EXTRA-EDGE-BOUNDARIES`, revision 1.
Basis DERIVED, status CANDIDATE, review NEEDS_RECHECK. Structural authored this
paper after Root proposed the weighted witness bound and a two-free-edge
repair. The derivation below independently reconstructs both proposals.
Agreement with Root is not different-author verification of this candidate.
No computational, numerical, formal-proof or external controls were executed.

## Exact objects and statement

Use precisely the class-I edge union from the frozen four-class paper,
`CANDIDATE_20261003_SEVENTEEN_POINT_FAMILY_FOUR_CLASSES_V1.md`, SHA256
`1faee8e574557fcbb75847e92dbfb6c8e5efd125a2f660b406641e4ed9104ed9`.
It has vertices s,t,x, ell,r, and Ai,Bi,Fi for i=1,2,3,4. Write
pi=(12)(34), with ell-side {1,2} and r-side {3,4}. Its neighbor sets are

    N(s)={t,x,A1,A2,A3,A4}; N(t)={s,x,B1,B2,B3,B4};
    N(x)={s,t,ell,r};
    N(Ai)={s,A_pi(i),Bi,Fi};
    N(Bi)={t,B_pi(i),Ai,Fi};
    N(Fi)={E(i),F_pi(i),Ai,Bi};
    N(ell)={r,x,F1,F2}; N(r)={ell,x,F3,F4},

where E(i)=ell on the first side and r on the second. Every existing edge has
one internal common neighbor, and every existing nonedge has at most two.
Let H+E be any simple graph on these same vertices that contains every H edge.
An eventual target containing this principal graph must satisfy these
necessary partial caps: its internal adjacent CN is at most one and its
internal nonadjacent CN is at most two. An added edge need not have its unique
target triangle neighbor inside these 17 vertices.

Let U(K)=3I17-K+J17/9. The following are the candidate conclusions:

1. Every added edge allowed by those partial caps is one of the 36 old-CN-zero
   pairs listed below; eight cross-side A-B pairs are further impossible.
2. Put r_E equal to the number of added row-to-row pairs and e_E equal to the
   number of added endpoint-to-row pairs. If U(H+E) is PSD, then
   2 r_E + e_E >= 3. This is a necessary condition only.
3. H* obtained by adding F1-F3 and F2-F4 satisfies all those partial caps and
   U(H*) is positive definite. Thus the upper principal Gram alone does not
   exclude all extra-edge extensions of this edge union.

There is no target completion, sufficiency, graph automorphism, induced
family coverage, actual triangle-family completeness or global exclusion
claim. In particular the two new edges of H* have internal CN zero; a target
would still need exterior vertices to complete their unique triangles.

## Complete old-CN-zero universe

The neighbor sets above directly give the following entire universe:

| Pair type | Exact zero-CN pairs | Count |
| --- | --- | --- |
| A-B | Ai-Bj with i,j on different sides | 8 |
| A-F | Ai-Fj with i,j on different sides | 8 |
| B-F | Bi-Fj with i,j on different sides | 8 |
| F-F | Fi-Fj with i,j on different sides, unordered | 4 |
| endpoint-row | ell-Aj,ell-Bj for j=3,4; r-Ai,r-Bi for i=1,2 | 8 |

These 36 pairs are not the 24 optional pairs previously obtained for a
different class-IV representative. They are derived afresh for class I.

For completeness, pairs omitted from the table can be checked in categories.
Any two A vertices have a common neighbor s, and any two B vertices have t.
The same-row A-B/A-F/B-F pairs are triangle edges with CN one; their pi-partner
nonedges have CN two. A center with any remaining nonneighbor has at least
one common neighbor; s with Bj and t with Ai have CN two. An endpoint with
its side's A/B vertices has its Fi neighbor in common; with opposite-side Fi
it has the other endpoint in common. Endpoints with centers have x in common.
Endpoint-Fi edges and same-side Fi-Fj edges have their triangle neighbor.
The displayed neighbor sets exhaust the remaining center-center and
endpoint-endpoint pairs. Therefore no additional CN-zero pair is omitted.

If an added pair u-v already had an old common neighbor z, then u-z is an
old edge with exactly one common neighbor. Adding u-v creates the second
common neighbor v for u-z, violating the partial adjacent cap. This proves
the CN-zero restriction even when several edges are added simultaneously.

Each cross-side Ai-Bj is forbidden independently: the old nonedge s-Bj has
the two common neighbors t and Aj. The added Ai-Bj would add a third, Ai.
This excludes those eight pairs without assuming support adjacency equals
actual target adjacency. Other simultaneous restrictions are not classified.

## Aligned short witness and its weighted necessity

Set chi1=chi2=+1 and chi3=chi4=-1. Use
w(s)=w(t)=w(x)=0, w(Ai)=w(Bi)=w(Fi)=2chi_i,
w(ell)=+1,w(r)=-1. The endpoint alignment is essential; the separate
append-only alignment correction preserves the earlier frozen paper.

This vector has sum zero, norm squared 50 and w^T U(H) w=-8. Its image is
zero at s,t,x, all Ai and Bi, ell and r, and is -chi_i at Fi. These images
follow directly from the displayed neighbor sets; for example a free row
has weighted neighbor sum 7chi_i while 3w(Fi)=6chi_i.

Every CN-zero row-row pair joins opposite chi signs, so its weight product
is -4. Every CN-zero endpoint-row pair has product -2. Adding an edge with
product p changes w^T U w by -2p, hence

    w^T U(H+E) w = -8 + 8 r_E + 4 e_E.

PSD therefore initially requires 2r_E+e_E>=2. Equality is impossible. For
(r_E,e_E)=(1,0), an endpoint Ai or Bi of the added edge has new image
2chi_i, and a free endpoint has new image chi_i; at least one is nonzero.
For (r_E,e_E)=(0,2), every added row endpoint is A or B and has new image
chi_i; no eligible endpoint-row pair attaches to Fi. Distinct added edges
cannot cancel those images. Thus U(H+E)w is nonzero in either equality case.
For any real PSD symmetric U, w^T U w=0 implies Uw=0: alternatively apply
nonnegativity to w+t v for both signs of sufficiently small t. The equality
cases are therefore excluded, proving 2r_E+e_E>=3.

This does not decide larger sets of extra edges. Negative-witness repair is
only one necessary test and must not be treated as a target construction.

## Two added free edges meet the necessary local caps

Add the cross matching mu=(13)(24) to the four free vertices. Their induced
graph changes from the two pi edges to a four-cycle. No new triangle is
created, so all old edges retain CN one and the two new edges have CN zero.

The common-neighbor changes can be exhausted without a graph program. Only
pairs incident to a free vertex can change. A free vertex Fi has two internal
free neighbors pi(i),mu(i). Its own endpoint remains adjacent with CN one;
its opposite endpoint gains the new cross-side free neighbor and changes
from CN one to two. Its pairs with s,t,x are unchanged with CN one. With a
row vertex Ai or Bi the old triangle CN one is unchanged; a pi-partner row
has CN two, a mu-partner row gains CN one from zero, and the remaining
cross-side row stays CN zero. For two free vertices the old pi edges keep
their endpoint CN one, the mu edges have CN zero, and the two remaining
nonedges have their two free neighbors in common, CN two. All pairs with no
free endpoint have unchanged neighbor sets. Thus every adjacent pair has
CN at most one and every nonadjacent pair has CN at most two.

All degrees remain at most six. This is a valid small necessary-cap example,
not a full target or a graph with local adjacent CN exactly one on every edge.
The selected twelve old triangles and their incidence word remain present;
the two added edges are outside that selected triangle edge union.

## Exact positive-definiteness of the repaired upper Gram

Use the same invariant decomposition as in the frozen upper-Gram candidate:
two three-dimensional nonconstant-character blocks, one four-dimensional
theta/endpoint block and the seven-dimensional common block. The two free
matchings pi and mu commute in the four-row Klein group, so these spaces
remain invariant. No automorphism of a hypothetical target is assumed.

On theta, pi has eigenvalue +1 and mu has -1. The free H diagonal changes
from 1 to 0. After eliminating endpoint diagonal 4, the three-dimensional
U block has A/B leading matrix [[2,-1],[-1,2]] and free diagonal 5/2. Its
last Schur scalar is 5/2-2=1/2, strictly positive.

For the other two nonconstant characters, the A/B leading matrix is
[[4,-1],[-1,4]]. The free U diagonal is respectively 3 or 5, since pi=-1
and mu is respectively +1 or -1. The inverse-entry sum of the leading
matrix is 2/3. The final scalars 3-2/3 and 5-2/3 are both positive.

The odd two-dimensional common block [[4,-2],[-2,3]] is unchanged and PD.
In the remaining common five-dimensional coordinates (c,z,e,p,f), the new
quadratic is y^T B' y+(j^T y)^2/9, where j=(2,1,2,8,4)^T and

    B'=[[4,-2,0,-8,0],[-2,3,-2,0,0],[0,-2,4,0,-4],
        [-8,0,0,8,-8],[0,0,-4,-8,4]].

It is the old B with its free/free entry decreased by four. Eliminate z with
pivot 3, then the PD c,e block (4/3)[[2,-1],[-1,2]]. The last p,f block is
[[-24,-16],[-16,-4]], determinant -160, so B' has inertia (4,1,0).
Direct row substitution gives

    B'^-1 j=(-1,-3/5,-2/5,-3/5,-3/5)^T,
    j^T B'^-1 j=-53/5.

The bordered matrix [[B',j],[j^T,-9]] therefore has the extra positive pivot
-9+53/5=8/5 and inertia (5,1,0). Eliminating -9 instead proves
B'+jj^T/9 has inertia (5,0,0). This common part is PD. Every block is now
PD, establishing U(H*) positive definite by exact written congruence.

## Provenance and boundaries

The historical target upper Gram G=27I-9A+J satisfies G^2=63G and is PSD.
The four-class construction is a separate accepted written premise. The
earlier candidate1750 supplies its explicit block basis, here reconstructed
with the two added edges; its witness orientation is corrected append-only.
Root proposed the weighted bound and free-matching repair after Structural
found that a cross-row A-F edge could pass necessary partial caps. Both
contributions are disclosed. No existing source gate or computational result
approves this new paper, and no ledger/index/Git mutation accompanies it.

Written falsification boundaries are the complete36 universe rather than a
class-IV24 universe, new-edge CN zero versus future target CN one, no creation
of old triangles, all free-incidence pair types, the aligned endpoint signs,
the zero-quadratic/nonzero-image implication, all17 invariant dimensions,
the last common determinant -160 and bordered sign +8/5. A larger added-edge
classification and any 99-vertex completion remain unresolved. Zero matrix
arithmetic programs, numerical eigenvalue calculations, formal controls and
external verification were executed. Different-author review is required.
