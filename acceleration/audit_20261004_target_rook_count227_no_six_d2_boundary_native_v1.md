# Independent written audit: the conditional R227 six-D2 boundary

Verification completed: **2026-10-04T19:59:30.5072716Z**.
Reviewer: Native (`/root/native_driver`). Mathematical producer: Structural.
Method: `independent_derivation`; no computational executor or worker.

## Frozen statement and review result

This audit independently reconstructs the whole V2 paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_NO_SIX_D2_BOUNDARY_V2.md`,
SHA256 `8355242189237d78409b9c84b1dc402267f5314135158d1ce3a8148a370def8a`,
and its exact r1 candidate
`acceleration/results/20261004_target_rook_count227_no_six_d2_boundary_candidate02.json`,
SHA256 `23dcd0cc23b59baa13b5da1b57544e8e0e4e15b8751929edbabe0b30448a3b15`.
The exact proposed identity is
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-NO-SIX-D2-BOUNDARY` r1.

For every complete finite simple SRG(99,14,1,2), let R count actual induced
nine-vertex rook subsets once by their vertex sets and put d_T=6-r_T for
each actual triangle, where r_T counts the rooks containing T. If R=227
and every d_T belongs to {0,1,2}, then it is impossible that exactly six
actual triangles have deficiency two. Equivalently, the positive family
cannot consist of twelve d1 and six d2 triangles, with every other d_T zero.
The maximum-deficiency-two condition is a literal hypothesis; other R227
populations and the target remain unresolved.

**PASS within that precise conditional scope.** The shared-root branch is
rejected by norm30>28 using five guaranteed neighbors and the wholly-S
sixth triangle. The disjoint-root branch is rejected by ordinary triangle
energy26>18. Neither rejection assumes induced selected support, an
equitable profile, an automorphism, or uniform triangle sums.

Dependencies are empty. Every mathematical premise below follows from
the complete target and the three literal assumptions in the raw candidate.
Earlier R227 and R228 proofs are bounded comparisons only. Root suggested
the support split and vetoed the old shared-neighbor step; Structural
derived this successor. Their shared discovery/challenge is disclosed
and does not supply this different-author verification.

## Actual triangles, local degrees and both fan injections

The induced graph on the fourteen neighbors of a vertex is a matching:
each of its vertices has exactly one neighbor there by lambda=1. Thus a
vertex belongs to seven triangles, and the total triangle count is231.
Different triangles share at most one vertex, since a shared edge has
only one triangle partner. Three actual triangles cannot intersect
pairwise at three distinct vertices: those vertices themselves make a
triangle and would give an edge another triangle partner.

Two triangles through v have four nonadjacent cross pairs between their
outer points. Each cross pair has v and one uniquely determined second
common neighbor. Any induced rook containing the two triangles must use
those four second neighbors, so there is at most one such rook.
Each rook through a triangle T gives, at each vertex v of T, exactly one
other rook triangle through v. These covered partners are distinct by
that uniqueness. Of the six other triangles through v, exactly r_T are
covered. The local graph of uncovered pairs therefore has degree d_T
at T, at every vertex of T. In particular d0 cannot be a defect partner.
Local handshake makes the number of incident d1 triangles even.

An induced rook has precisely six actual triangles, its rows and columns.
Counting triangle-rook incidences yields sum d_T=6(231-R)=24. Six D2
triangles consequently leave twelve D1 triangles and P=18 positive ones.

Fix a point with r1 D1 and r2 D2 triangles. Their outer points are distinct.
At the two outer points of a root of deficiency m, it needs m positive
defect partners not through the central point. An external actual
triangle meets at most one outer point of this whole fan. Two on the
same root violate linearity; two on different roots make the forbidden
three-distinct-intersection configuration with the two fan roots.
Thus the required partners are distinct and

    P >= (r1+r2) + 2r1 + 4r2 = 3r1+5r2.

There is also a separate injection for the selected twelve D1 triangles.
If selected multiplicity at a point is r, its 2r outer points each have
odd selected incidence from that fan root and need another selected
triangle by parity. Again each external selected triangle covers at
most one such point. Hence12>=r+2r=3r. Used multiplicities are even, so
they are2 or4. If k points have multiplicity4 and S is the used support,
36 selected incidences give |S|=18-k. The twelve actual selected
triangles contribute36 distinct actual edges inside S. Arbitrary extra
edges are retained; this does not assert an induced selected support.

## Labelled six-triangle concurrence and the fourfold split

At a D2 vertex outside S there is no D1. Local degree2 needs at least
three positive triangles, while18>=5r2 permits at most three. Such a
point therefore lies on exactly three of the six D2 triangles.
Let h count these outside triple points. Fix one p and its three roots
as the base fan. There are three other D2 roots. Another counted point
cannot contain two base roots by linearity. It either uses one base
and two external roots (attached), or all three external roots (detached).
Two attached points must use disjoint external pairs: a shared external
root and the same base root violate linearity; a shared external root
and different base roots make three distinct pair intersections, including p.
Only three external roots are available, so there is at most one attached
point. There is at most one detached point, and it cannot coexist with
an attached point: their external pair would meet twice. Thus h<=2.
This is a lemma about actual triangles, not arbitrary linear triples.

Write t_i for the number of outside-S points on D2 triangle i. Then
sum t_i=3h<=6. Its internal edges number C(3-t_i,2), all distinct from
one another and from selected edges by lambda=1. The complete integer
term table is

| t | Internal edges | Linear lower 2-t | Gap |
|---|---:|---:|---:|
| 0 | 3 | 2 | 1 |
| 1 | 1 | 1 | 0 |
| 2 | 0 | 0 | 0 |
| 3 | 0 | -1 | 1 |

There are at least12-3h>=6 D2 edges in S, and e(S)>=42.

From the SRG hypotheses, A^2+A=12I+2J and Aj=14j. On j-perp the
real symmetric A has roots3 and-4. Set Q=3I-A+J/9. Its eigenvalues
are0 on j,0 on the3 eigenspace and7 on the-4 eigenspace. Thus Q is PSD,
Qj=0 and Q^2=7Q. These are ordinary real/rational identities, not field
rank or code hypotheses. An indicator on n vertices satisfies

    chi^T Q chi = 3n+n^2/9-2e.

If k>=3 then n<=15, and even the36 selected edges give at most70-72<0.
For k1, n17 gives e<=floor(374/9)=41; for k2, n16 gives
e<=floor(344/9)=38. Both contradict e>=42. Hence k0, |S|=18, and
each S point belongs to exactly two selected triangles. At n18, PSD
gives e<=45. If h0, all six D2 are internal and e>=36+18=54.
If h1, sum t=3 and C(3-t,2)=3-2t+C(t,2) gives e>=48.
Both fail. Thus h2 with outside points p,q.

The two three-root sets share at most one root, since two shared roots
would intersect at both p and q. If shared, t=(2,1,1,1,1,0); if
disjoint, all six t=1. These exhaust the actual possibilities.

## Full99 integer norm: the corrected shared branch

Put y=Qchi_S. As |S|/9=2 this is an ordinary integer99-vector, with

    y_z = 5-deg_S(z) inside S,  2-deg_S(z) outside S,
    sum y=0,  ||y||^2=7(90-2e(S)).

In the shared branch the common root contains p,q and only one S point.
The other two roots at p have two S points each; likewise at q.
Linearity makes these five neighbors distinct. Therefore y_p,y_q<=-3,
with pair norm>=18. The D2 internal edges number seven, so e>=43.
If e>=44 the full norm is<=14, already impossible. Hence e43 and
||y||^2=28; the36 selected edges and seven D2 edges account for every
actual internal edge of S.

Each S point has four distinct selected neighbors. Let k_z>=0 be its
extra internal degree from those D2 edges. Then deg_S=4+k_z, y_z=1-k_z
and sum_S k_z=14. The sixth D2 root not through p or q is wholly in S;
it supplies increments at least2 at three distinct points. For integer
k>=0, k^2>=k, and at each of those points k^2-k>=2. Consequently

    sum_S k_z^2 >= 14+6=20,
    sum_S y_z^2 = 18-28+sum k_z^2 >=10,
    sum_S y_z =18-14=4.

There are81 outside points and79 after removing p,q. Their remaining
sum is -4-(y_p+y_q)>=2. Every signed integer z has z^2>=z, so that
remaining squared norm is at least2. The whole norm is at least
10+18+2=30, contradicting28. This proof neither counts six shared-fan
neighbors nor prescribes the remaining vector's locations or signs.

## Disjoint branch and its complete scalar boundary

Here each D2 has one outside point and one internal edge. At p and q,
three roots give six distinct S neighbors. Pair norm>=32 excludes
e>=43 because then the full norm is<=28. Thus e42 and total norm42;
the36 selected and six D2 edges exhaust actual internal edges.

At z in S, let r_z count its incident D2 triangles. Since r1=2, the
positive fan bound6+5r_z<=18 makes r_z<=2. Each D2 now adds one
internal neighbor per S endpoint, so y_z=1-r_z and sum_S r_z=12.
Even before fixing the pair entries, sum_S y_z^2>=6, using r_z^2>=r_z.
If either outside pair entry were<=-5, total norm would be at least
6+25+16=47. Thus y_p=y_q=-4 without circular use of their values.

Let ell count S points with r_z=2. Counts r0,r1,r2 are
6+ell,12-2ell,ell. Internal y sum is6 and norm6+2ell. The remaining79
outside entries sum2 and have norm4-2ell. Integer norm>=signed sum
forces ell<=1. The full possibilities, not just a convenient subset, are

| ell | Inside r0/r1/r2 | Remaining nonzero entries | Remaining norm |
|---|---|---|---:|
| 1 | 7/10/1 | two +1 | 2 |
| 0 | 6/12/0 | one +2 | 4 |
| 0 | 6/12/0 | three +1 and one -1 | 4 |

For ell1, sum(z^2-z)=0 forces each entry0 or1. For ell0 that sum is2;
each integer gap is0,2 or at least6, so exactly one entry is2 or-1,
and all others0/1, giving precisely the two shown patterns. In particular
all other vertices have value<=2 and at most one has value+2. These
scalar patterns are not themselves contradictions and remain in the proof.

## Ordinary triangle energy rejects every scalar pattern

Let N be the ordinary actual99 by231 triangle-incidence matrix. Its
Gram has diagonal7 and off-diagonal1 exactly on edges, so NN^T=A+7I.
Also Qy=7y and sum y=0 imply Ay=-4y. Hence the sum of squared sums
over every actual triangle is

    sum_T (sum_{z in T} y_z)^2 = y^T(A+7I)y =3||y||^2=126.

The twelve D1 triangles count each S point twice, so their sums total12.
For every signed integer s, s^2>=s; their total squared energy is>=12,
including possible negative triangle sums. Each D2 has p or q with
value-4 and two S points with r_z>=1, hence y_z<=0. Its sum is<=-4;
the six D2 energy is>=96. All D0 triangle energy is therefore<=18.

Through each p,q are seven actual triangles, three D2 and no D1, leaving
four D0. If p and q are adjacent, their unique common triangle is D0,
since no D2 contains both. Its third point has value<=2 and its sum is
<=-6. Its square>=36 alone exceeds18; it is charged only once.

Otherwise the two four-triangle families are disjoint. At most one
triangle through p can use the unique possible+2 point: two would give
the edge from p to that point two triangle partners. Every other such
triangle has sum<=-4+1+1=-2 and energy>=4. The possible exception has
sum<=-4+2+1=-1 and energy>=1. Thus its four D0 triangles need>=13
energy (>=16 if no exception); the same holds at q. Their distinct
families need>=26>18. Sharing some other vertex would not merge actual
triangles and does not invalidate this triangle-energy sum. Both shared
and disjoint root branches have now been independently rejected.

## Explicit written check population

The44 proof checks are: (1) seven vertex triangles; (2) total231;
(3) linearity; (4) no loose triangle triple; (5) intersecting-rook uniqueness;
(6) local degree d_T; (7) selected parity; (8) D24/a12/b6/P18;
(9) positive fan injection; (10) 3r1+5r2 bound; (11) selected injection;
(12) multiplicities2/4 and |S|18-k; (13) selected36 distinct edges;
(14) outside D2 minimum three; (15) outside maximum three;
(16) base/attached/detached classification; (17) disjoint attached pairs;
(18) h<=2; (19) sum t=3h; (20) four integer edge terms;
(21) added edges>=6; (22) adjacency identity; (23) Q PSD/Q^2=7Q;
(24) k>=3 exclusion; (25) k1/k2 exact floors; (26) k0/h0/h1;
(27) exhaustive shared/disjoint root sets; (28) integer y/zero sum/norm;
(29) shared five neighbors/seven edges; (30) shared e43 edge exhaustion;
(31) wholly-S sixth root/internal norm10; (32) remaining signed norm2;
(33) disjoint six neighbors/e42; (34) internal norm6 before pair equality;
(35) r<=2/ell counts; (36) complete remaining scalar patterns;
(37) ordinary incidence Gram/eigenvector; (38) total triangle energy126;
(39) D1 signed sum/energy12; (40) D2 energy96/D0 budget18;
(41) shared p/q D0 energy36; (42) eight distinct D0 in nonadjacent case;
(43) at-most-one exception/energy13 each; (44) final26>18 and exact scope.

The12 boundary challenges were carried out by hand:

1. A shared fan can be labelled A={p,q,a}, B={p,b,c}, C={p,d,e},
   D={q,f,g}, E={q,h,i}, F={j,k,l}, with all other labels distinct.
   It gives exactly five S neighbors at p,q and internal terms0,1,1,1,1,3.
   This is a partial geometry control, not an asserted target extension.
2. Three roots at p and three at q with private outer points give the
   disjoint3+3 pattern, internal terms1 six times, and six neighbors each.
3. A negative D1 sum such as-1 still satisfies s^2>=s; nonnegative sums
   or equal D1 sums are never assumed.
4. Four selected roots through a point are allowed by the local selected
   bound12>=3*4; their rejection requires the actual support-size Q bound.
5. t3 has zero edges and linear lower-1. It remains in the complete table.
6. A merely linear six-root hypergraph can have four triple points:
   p:{A,B,C}, q:{A,U,V}, r:{B,U,W}, s:{C,V,W}, completing each root
   with a private third point. A,B,U meet pairwise at distinct p,q,r,
   so actual lambda1 rejects it. Linearity alone would not prove h<=2.
7. The h0/h1 counts give54/48 edges and fail Q45 before either h2 branch.
8. Shared pair norm18 fits28 by itself. Three k2, eight k1 and seven k0
   attain the scalar internal norm10/sum4; p,q=-3 need remaining sum2.
   This exposes exactly why the sixth-root and remaining-vector terms matter.
9. All three disjoint scalar patterns in the table fit norm42/sum0;
   they require the later actual triangle energy, not scalar dismissal.
10. Extra actual support edges are included in e and can only strengthen
    the early lower bounds; exhaustion is concluded only at e43/e42.
11. A shared p/q D0 triangle is counted once and already costs>=36;
    disjoint families can share a vertex but have eight different triangles.
12. Fractional Gram vectors lack the ordinary integer inequalities and
    do not refute this target theorem. No arbitrary even-twelve selection,
    other R227 population, nonzero left kernel, or target resolution follows.

There are56 written checks (44 proof,12 boundary), four integer term rows
and three scalar pattern rows. Executed/formal/external/solver checks: zero.

## Preserved failed outline, comparison and evidence limits

The unsealed V1 paper SHA
`8f2394b3932193fbf1dfb5f4d7c97383581fee03fc7519882ea88e2cfcb21d92`
and rejection receipt SHA
`61cad3090fa7c113d22b45155650e7808d24c7b42a0ad0ffa633bbed148d86ca`
are unchanged. Its shared-fan claim of six S neighbors was invalid, and
its84/82 outside counts belonged to a different support size. This review
uses81/79 for S18 and the new five-neighbor norm proof. The rejected
argument is not a theorem counterexample, and no V1 gate is transferred.

Bounded comparison read the relevant R228 four/five population and R227
single-D3 paragraphs: their triangle-linearity, fan and upper-Gram mechanisms
overlap, but their populations and contradictions differ. The seven-D2
paper is also comparison only. No earlier approval or registration is an
inherited logical premise, no archive completeness or novelty is claimed,
and no external theorem is needed here.

All mathematical checks were written derivations from frozen source text.
Only selected small metadata identities were hashed/read and new audit/report/
binding files saved. No scientific program, source import, AST/syntax check,
backend, census, solver, worker, ledger parse, Git/index/publication operation,
or protected-state edit occurred. Verification start/worker times remain null.
The exact new Root acceptance remains null at package creation. This result
is pending separate Root review and nextWave47 registration, outside the
closed Wave46 cutoff449. Target status remains UNKNOWN.
