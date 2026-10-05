# Independent written challenge of rook deficiency and N3 square coverage

Audit writing began: 2026-10-04T16:25:24Z. The bound reports record the later
completed written verification/sealing time separately. Reviewer: Native
`/root/native_driver`; mathematical producer: Structural `/root/structural`.
Root proposed parts of the discovery outline and equality challenge. Those
discussions are shared discovery context, not an independent verification.
This audit is a separate set-incidence and spectral derivation. It executes no
graph, matrix, matching, code, census, solver or verification program.

The exact three source statements are retained in their original raw packets.
This audit finds no mathematical veto under their stated complete finite simple
SRG(99,14,1,2) hypotheses. It does not establish existence, exclude R229 or R231,
approve a cited Makhnev theorem, or assert a Hamming covering conclusion.

## Local dictionary independently reconstructed

Let A be the full adjacency matrix. For adjacent vertices exactly one common
neighbor completes their edge to a triangle. Every vertex belongs to seven
triangles: its fourteen neighbors split into seven adjacent pairs, since each
neighbor has exactly one neighbor within that local graph. Hence there are
231 actual triangles. Distinct triangles share at most one point. If three
distinct triangles met pairwise at three different points, those points would
be adjacent pairwise; an edge of one triangle would have its original third
point and the third intersection point as two common neighbors. This is
impossible. This prohibition is stronger than linearity of a triple system.

Two triangles through v have two non-v points each. These four cross pairs are
nonadjacent; otherwise a vertex outside a triangle would meet two of its points.
Each cross pair has v and a unique other common neighbor. In a proposed rook
these four other vertices are its opposite grid points. They fix the entire
nine-subset. Thus two triangles through v belong together to at most one rook.
A rook containing a fixed triangle T supplies a different companion triangle
at each of T's three points. At any such point, the six possible companions
therefore include exactly r_T covered ones and d_T=6-r_T uncovered ones.
In the defect graph on its seven incident triangles, T consequently has degree
d_T at each of its three points. In particular 0<=d_T<=6. Since a rook contains
six triangles, D=sum d_T=6*231-6R=6(231-R). These count actual subsets once.

At any point the sum of these defect degrees is even. Thus the parity of the
number of odd-deficiency incident triangles is even. This supplies no bound of
two on that number; four and six remain possible.

## Second-neighbor mass and equality, with no uniformity premise

Fix T={a,b,c} of deficiency m>0. At each of its points there are m defect
companions. The three lists are disjoint, because a different triangle cannot
meet T twice. Their union C has 3m members, of total deficiency K>=3m.

For U in the a-list, at each of its two outer points there are d_U defect
partners. The two sets of partners are disjoint by linearity. Any such partner
V avoids T altogether: meeting a would make it meet U twice, and meeting b or c
would make T,U,V the forbidden three-triangle configuration. V is also outside
C. A member of the a-list cannot meet U at an outer point; a member of another
list would again make that forbidden configuration. There are precisely 2K
ordered incidences from C to these further partners.

A further partner can meet at most one triangle of each of the a,b,c lists.
Meeting two in the same list makes those two and V meet pairwise at three
different points. Thus its contribution to the 2K incidences is at most three.
At least ceil(2K/3) distinct further triangles, each of positive deficiency,
are needed. The three disjoint sets T,C,further triangles imply

    D >= m+K+ceil(2K/3) >= m+3m+2m=6m.

If D=6m, the first inequality is sharp and K=3m. Every C member has deficiency
one. Exactly 2m further triangles each have deficiency one, each meets exactly
one C member in each list, and no other positive deficiency exists. Each C
member's two outer points belong to different further triangles, by linearity.
Outer points of two C members are all distinct, whether in one list (already
sharing its center) or different lists (forbidden configuration with T).
Thus there are exactly 6m outer points. The further triangles partition these
points into 2m triples, with one point in each list. There is no choice of
arbitrary matchings asserted: the three perfect matchings describe the actual
geometry if equality occurs.

Let H0 be the edge union of T, the 3m first companions and the 2m further
triangles. Let w be m on the three central points, one on the 6m outer points
and zero elsewhere. Its sum is 9m. H0*w is 4m at a center (two central weights
and 2m outer weights), and m+3 at an outer point (its center, matched outer
point and two same-further-triangle points).

The full SRG identity A^2=12I-A+2J gives eigenvalue 14 on j and roots 3,-4
on j-perp. Therefore Q=3I-A+J/9 is positive semidefinite. For H0 the displayed
weights give zero quadratic value. Any additional actual edge inside their
positive support decreases that value by 2*w_p*w_q>0. Positive semidefiniteness
prohibits every such edge. Consequently H0 is induced on S, with |S|=3+6m.
Extending w by zero gives w^T Q w=0 and hence Qw=0. Thus Aw=3w+mj in the
entire graph, not just on S.

Outside S a vertex meets at most one point of T. Writing a_v for its T-neighbor
count and b_v for its outer-neighbor count yields m*a_v+b_v=m, so (a_v,b_v)
is (1,0) or (0,m). Each center has 12-2m outside neighbors, and no two centers
can share such a vertex. There are 36-6m vertices of the first kind. Out of
96-6m total outside vertices, exactly sixty are of the second kind. These are
proved point incidences, not an assumed equitable partition. At R229, D12
permits under this non-strict screen either twelve d1 or one d2 with ten d1;
that wording is a necessary-screen allowance, not a realization claim.

## Square and N3 correspondence independently reconstructed

Take an induced square a-b-c-d-a. Write e,f,h,g for the triangle partners of
ab,dc,ad,bc. They lie outside the square and are distinct. An identification
with a corner adds a diagonal or gives an edge two triangle partners. Two
partners of incident edges cannot coincide, since it would meet two points of
the already existing triangle on the intervening edge; partners of opposite
edges cannot coincide for the same outside-a-triangle reason. A partner has
no unintended adjacency to the other two corners. For example if e meets c,
edge bc has its unique partner g and the additional common neighbor e;
these are distinct by the partner-distinctness argument. All other cases
follow by the square's dihedral relabeling.

The disjoint triangles abe and dcf have cross edges ad,bc and only the possible
third ef. Similarly adh and bcg have ab,dc and only possible hg. Cross edges
between disjoint triangles always form a matching, because an outside point
cannot meet two vertices of a triangle. A rook containing the square must
contain e,f,h,g; ef's unique triangle partner fixes its ninth point. Hence
square containment is unique.

Assume no induced N3. Then ef and hg are both present. Let i be the partner on
ef and j on hg. The nonintended partner adjacencies are absent: for instance
e-h would make edge ah have its partner d and the common point e. The same
argument excludes e-g,f-h,f-g. It also prevents i or j from coinciding with
any of the eight existing vertices. For example j=a would require a-g,
which is absent; j=e would require e-h, which is absent. There is no tacit
distinctness assumption.

Triangles abe and hgj have the two cross edges ah,bg. N3-freeness forces ej.
Triangles dcf and hgj similarly have dh,cg, so fj is forced. Therefore j is a
common neighbor of the edge ef, making i=j. The six triples

    abe, dcf, hgi;  adh, bcg, efi

are the rows and columns of a rook. Any extra edge between non-row/non-column
grid points has the two other grid corners as common neighbors, contradicting
lambda1 on that extra edge. The nine-subset is induced and was already unique.

Conversely an induced N3 formed by 012 and 345 with cross 03,14 has exactly
one square, 0-1-4-3-0. Its opposite edge partners 2 and5 must meet in any rook
covering it, but are nonadjacent in N3. The square is uncovered. Every induced
N3 maps to this unique square. For a fixed square, the opposite-edge choices
ab/dc and ad/bc fix the two possible pairs of partners uniquely; there is at
most one N3 subset for each choice. Thus the map is at most two-to-one and
n3<=2U. It is neither asserted injective nor asserted surjective. In particular
an uncovered square need not itself yield an N3 in either immediate direction;
N3-freeness is the global hypothesis used to complete its grid.

The target has 99*84/2=4158 nonedges. The two common neighbors of a nonedge
are nonadjacent, since otherwise their edge would have both original vertices
as common neighbors. This yields a square, counted twice through its opposite
pairs, for 2079 squares. A rook has nine squares. Their uniqueness makes the
covered-square sets disjoint, so U=2079-9R. It follows that R231 iff U0 iff
N3-free, and 0<=n3<=4158-18R. This local argument needs lambda1/mu2; the target
parameters supply only the displayed numerical coefficients.

The labeling check is separate from existence: 012/345 with cross03,14 has
edges01,02,03,12,14,34,35,45. Relabeling vertices by(0,1,5,3,2,4) gives
01,03,05,12,15,23,24,34. With increasing lexicographic pairs as bits0..14,
the former sum is1+2+4+32+128+4096+8192+16384=28839; the latter is
1+4+16+32+256+512+1024+4096=5941. No computational canonicalization ran.

## Strict equality obstruction by a second, explicit pair classification

An uncovered square's two incident edge-triangles at any corner are a defect
pair. If they instead belonged together to a rook, the second common neighbor
of the adjacent corners would be that square's opposite corner, so the square
would be in that same rook. Thus every uncovered square corner lies on a
positive-deficiency triangle. Also U=2079-9R=3D/2.

In the equality support above label further triangles by nodes v=1..2m.
Write p_av,p_bv,p_cv for their three outer points, with centers a,b,c. Edges
are exactly: the central K3, each center to all its bucket points, the three
points at each node as a K3, and one perfect matching M_a,M_b,M_c within each
bucket. These are identities of the proved induced support, not hypothetical
completion assumptions.

For center a and a point p_bv or p_cv there are precisely two common neighbors
in S: the other center and p_av. This accounts for 3*4m=12m nonadjacent pairs.
Centers among themselves, a center and its own bucket points, same-node outer
points, and matched same-bucket points are adjacent. Unmatched same-bucket
points have just that center as a common neighbor. For p_av,p_bw with v!=w,
the only common neighbors are p_aw if M_a(v)=w and p_bv if M_b(w)=v.
Thus exactly two occur if {v,w} lies in both matchings; each shared edge
gives two such cross-bucket point pairs. All pairs are covered by these cases.

Dividing the total opposite-pair count by two gives

    C4(S)=6m+|M_a intersect M_b|+|M_a intersect M_c|+|M_b intersect M_c|<=9m.

Every uncovered square is in S, while equality requires U=9m. Hence each
matching intersection must have size m, so all three matchings coincide. An
edge of this common matching gives two further triangles and three bucket
triangles along with T: their nine points form an induced rook. This includes
T and a declared defect companion, a contradiction. Therefore D=6m is
impossible. Because D is divisible by six, D>6m implies D>=6m+6 and
d_T<=230-R when R<231. For d_T=0 this last bound follows from R<=230.
At R229 there are exactly twelve d1 triangles. Even point incidence permits
2,4,6 positive triangles per used point; no cubic dual or multiplicity-two
assumption is supplied or needed.

## Written falsification controls and exact scope

The ordinary rook9 has lambda1/mu2, R1,U0,n30 and checks the parameter-free
equivalence, but not the target2079 coefficients. Bare N3 has one square and
its opposite partners nonadjacent, but fails the global complete CN rules.
A triangular prism has three cross edges and no N3 on its two triangles;
the local matching distinction is essential. A merely linear triple family
can have three triangles meeting cyclically at three points and breaks the
second-neighbor capacity proof. These boundaries prevent false transfers.

At m1 the only three matchings coincide, yielding nine squares and the defect
contradiction. At m2 all identical gives common-sum6 and18 squares; exactly
two identical gives2 and14; all distinct gives0 and12. The required18 rules
out the latter two, and an actual rook rules out the first. This is a hand
matching classification, not an executed graph census. Inserting an extra
edge inside S changes the Gram quadratic value by a strictly negative amount;
passing the zero quadratic test does not construct a completion.

At R231 D0 there is no positive m and neither deficiency theorem excludes
the case. At R229 the strict theorem leaves the twelve-d1 case open. No theorem
about Makhnev's global exclusion, literature novelty, universal covering,
nonconstant code, or target resolution is verified here. The papers' cited
archive overlap is preserved as disclosure; this self-contained derivation
does not depend on or recompute archive gates. Formal/external checks and all
executed controls are zero.

There are 56 written checks: 20 for defect/mass/equality/outside incidences,
21 for square/N3/grid/normalization/counting, and15 for strict equality and
its hand boundaries. Their report lists each check explicitly. All are
written derivations under the exact hypotheses, never executable test results.
