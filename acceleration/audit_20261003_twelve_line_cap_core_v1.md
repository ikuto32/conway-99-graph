# Independent written audit: the literal twelve-line cap core

Discovery producer `/root/structural`; independent mathematical verifier
`/root/checkpoint_audit`. This is a written derivation, with zero executed
mathematical commands, fixtures, support enumerations or formal checking.
Checkpoint's separate registrar/publication engineering authorship is disclosed
and supplies no mathematical premise. No ledger/index or candidate bytes change.

The complete candidate
`docs/CANDIDATE_20261003_TERNARY_TWELVE_LINE_CAP_CORE_COMPLETION_OBSTRUCTION_V1.md`
has SHA2569ba6929ec3ac6273e0ce56f06bab4e0da0f3e706f1a4be22054733209eeed702.
I also read the complete ROOT written review
`acceleration/audit_20261003_twelve_line_completion_core_v2_review.md`,
SHA2568a066bdc598a5bea4240690b35cf3a9eb97db92d7035466fcaaa4c5ca6caf0b3.
Its separate executed16384-subset result is not replayed or transferred here.
The proof below independently reconstructs the neighborhood classes, the
necessary extra-edge classification and the integer completion contradiction.

Two distinct results are established: the finite point graph refutes the
cap-only balanced-dependence inference, including the stated interlacing test;
the specified twelve triangles cannot embed even non-induced in any target
99/14 graph with adjacent CN1 and nonadjacent CN2. This does not force the
configuration in a target or decide unrestricted existence.

## Literal finite graph and complete pair classes

Work modulo4 with sixteen distinct vertices c_i=i, x_i=4+i, y_i=8+i,
z_i=12+i. The twelve triangles are, in this exact order,

    (0,1,4),(1,2,5),(2,3,6),(3,0,7),
    (0,8,12),(1,9,13),(2,10,14),(3,11,15),
    (4,10,15),(5,11,12),(6,8,13),(7,9,14).

Define G by the union of their unordered edges. The edge sets of distinct
triangles do not share a pair: the E family supplies center-center and
center-x edges; V supplies center-local-leaf and local y-z edges; T supplies
x-leaf and the other y-z edges. Thus there are exactly36 edges and the graph
is simple. Reading incident triangles gives

    N(c_i)={c_(i-1),c_(i+1),x_(i-1),x_i,y_i,z_i},
    N(x_i)={c_i,c_(i+1),y_(i+2),z_(i+3)},
    N(y_i)={c_i,x_(i+2),z_i,z_(i+1)},
    N(z_i)={c_i,x_(i+1),y_i,y_(i-1)}.

The four center degrees are6; all other degrees are4. To check every pair
without an executable enumeration, index translation reduces mixed pairs
to type(i),type(j=i+delta), delta0..3. Direct intersection of the four
displayed sets gives the following complete classes:

    c,x: [1,2,2,1], adjacent delta0,3
    c,y: [1,2,1,2], adjacent delta0
    c,z: [1,2,1,2], adjacent delta0
    x,y: [1,1,1,1], adjacent delta2
    x,z: [1,1,1,1], adjacent delta3
    y,z: [1,1,0,0], adjacent delta0,1.

Equal-type pairs use delta1,2,3:
c,c=[1,2,1] with adjacency1,3; x,x=y,y=z,z=[1,0,1] with
no adjacency. For example c_0,x_1 intersects in c_1,z_0; c_0,z_2
intersects only in x_3; y_0,z_1 intersects only in x_2; y_0,z_2 has
empty intersection. These representatives test the orientation of the
asymmetric mixed-index conventions. The classes cover16 pairs per mixed
type and6 per equal type, totaling6*16+4*6=120 unordered pairs.

Every adjacent pair has CN1, supplied by its stated triangle; every
nonadjacent pair has CN0/1/2. An additional actual triangle would complete
one of its edges a second way, which is impossible. Thus the twelve
triples are the complete actual triangle family, not merely a linear
hypergraph subfamily.

For the binary incidence matrix B_0 of these twelve columns, give all E
and V columns coefficient-1 and all T columns coefficient+1. A center
has three negative incidences and integer sum-3. Each x has one E and
one T, each y/z has one V and one T, with integer sum0. Consequently
B_0 z=0 over GF(3), but the column coefficient sum is-8+4=-4=2 mod3.
In particular B_0^T u=1 would imply0=z^T B_0^T u=z^T1=2, contradiction.
This explicitly refutes balance/affine-point conclusions from the local
caps and actual-triangle geometry alone. G is not14regular or a target.

## Independent exact interlacing calculation

The order-four shift acts on each of the four vertex types. Substitution
of a shift eigenvalue zeta into the above neighbor sets gives the Hermitian
four-by-four block displayed in the candidate. This is a direct graph
calculation, not an inference from computational eigenvalues.

At zeta1 the y-z antisymmetric coordinate has eigenvalue-2. On c,x and
the normalized y+z coordinate the block is

    [2,2,sqrt2; 2,0,sqrt2; sqrt2,sqrt2,2].

Its trace4, sum of principal two-by-two minors-4 and determinant-4 give
t^3-4t^2-4t+4. The values at-2,-1,0,1,4,5 are respectively
-12,3,4,-3,-12,9. Three disjoint sign-changing intervals
(-2,-1),(0,1),(4,5) exhaust this cubic's roots.

At zeta-1 the c/(y+z) block is[-2,sqrt2;sqrt2,0], with roots
-1+-sqrt3; the x/(y-z) block gives+-sqrt2. At zetai the six upper
edge weights are1-i,1,1,-1,-i,1+i. Their squared moduli sum8,
so trace(A^2)=16. The four triangle-product real parts are-1,-1,1,1,
giving trace(A^3)=0. Paired matching products are4,1,1; the three
four-cycle real parts are-2,-2,0. Thus the determinant is6-2*(-4)=14,
and trace0 gives t^4-8t^2+14. Its roots are
+-sqrt(4+sqrt2),+-sqrt(4-sqrt2); zeta-i conjugates this block.

All those roots other than the cubic's single(4,5) root are less than3
and greater than-3: sqrt3<2 and sqrt(4+sqrt2)<sqrt6<3 suffice.
Therefore lambda_2<3 and lambda_min>-3, satisfying the stated target
principal-submatrix caps lambda_2<=3 and lambda_min>=-4.
No implication of completion from passing these necessary tests is made.

## Extra edges: necessity without an induced hypothesis

Now assume a simple99-vertex14regular graph A with CN1 on edges and CN2
on nonedges contains the twelve literal triangles on a set S of16
distinct vertices. Let H=A[S]; G is a subgraph, not assumed induced.

If an original nonedge uv has a common neighbor w in G, it cannot become
an edge of H. The existing edge uw has its original triangle completion
q different from v; adding uv would give uw the extra common neighbor v.
This uses adjacent CN1 only. Thus added edges belong to the14 CN-zero
pairs:2 opposite x pairs,2 opposite y pairs,2 opposite z pairs, and
8 y_i z_j pairs with j-i=2 or3.

An opposite x edge x_i x_(i+2) gives the originally CN2 nonedge
c_i,x_(i+2) a new common neighbor x_i. That center-x pair cannot itself
become an edge by the previous argument. An edge y_i z_(i-1) similarly
gives the originally CN2 pair c_i,z_(i-1) a third common neighbor y_i.
Both kinds are forbidden by the nonadjacent CN2 requirement.

The remaining eight possibilities lie between L_0 and L_2 or L_1 and
L_3, where L_i={y_i,z_i}. In each K2,2 they must form a matching: if
one leaf meets both opposite leaves, their original local edge gains a
second common neighbor. Hence H=G plus f edges in two such matchings,
with0<=f<=4. Centers remain degree6, x vertices degree4, and exactly
2f leaf degrees rise4 to5.

This necessary classification is sufficient for the exclusion below;
it never requires an added edge to have its completion inside S.
For completeness, matching cases preserve the local caps by the same
pair-class accounting. Center-center and x-x CN are unchanged.
Center-leaf CN rises only for opposite leaves,1 to2. An x-leaf
nonedge gains at most one CN; an x-leaf edge gains none, because its
two original leaf neighbors belong to centers of opposite parity.
Local and delta1 y-z edges gain none. Near-center same-type leaf
nonedges gain at most one CN, while opposite-center and delta3 y-z
nonedges start at0 and gain at most two. Matching forbids both added
neighbors from coinciding. A newly added edge retains CN0 inside S,
which is permitted for a subgraph of a target with external completion.
The two K2,2 matching polynomials are1+4t+2t^2; their product gives
1,8,20,16,4 cases by f and49 total. This is a written class check,
not a new executed16384-subset audit.

## Target completion budget

Write t_v=|N_A(v) intersect S| for v outside S. The degree sum gives

    sum t_v = 16*14-2*(36+f)=152-2f.

The sum of internal CN over all pairs of S is also
sum_(s in S) binom(deg_H(s),2)=4*15+12*6+2f*(10-6)=132+8f.
The target total CN on those pairs is(36+f)+2*(84-f)=204-f.
Subtracting gives sum_outside binom(t_v,2)=72-9f.
In particular a newly added edge's outside completion is counted,
not wrongly set to zero.

Every center pair already exhausts its required CN. The four centers
therefore have disjoint outside neighborhoods of size14-6=8, yielding
32 distinct anchored outside vertices. For an anchored vertex meeting
c_i, all x and all local/adjacent-center leaves are forbidden by their
already saturated pair with c_i. Only L_(i+2) is available. It cannot
meet both leaves because their local edge already has its triangle
completion inside S.

Let f_i count matching edges between L_i and L_(i+2). Each added edge
is counted by its two opposite center indices, so sum f_i=2f.
Each c_i/opposite-leaf pair has one internal CN initially, and gains
one exactly when that leaf has a matching edge to L_i. Thus its
remaining deficits total2-f_i. The exact32 anchored vertices have
degree1 or2 into S, and exactly R=sum(2-f_i)=8-2f have degree2.
They contribute32+R=40-2f cut edges and R pair completions.

There are99-16-32=51 unanchored vertices left. Their exact budgets are

    E=(152-2f)-(40-2f)=112,
    Q=(72-9f)-(8-2f)=64-7f.

For every nonnegative integer t, binom(t,2)>=2t-3; subtracting gives
(t-2)(t-3)/2>=0, including t0/1 and equality at2/3.
Consequently Q>=2E-3*51=71. But64-7f<=64<71 for every f0..4.
The assumed embedding is impossible, allowing every arbitrary added
edge permitted by the target assumptions.

## Twenty written falsification boundaries and limits

1. Sixteen distinct labels and all twelve ordered columns are fixed.
2. Pair-class orientation is tested by c_0,x_1 and y_0,z_1.
3. The120-pair partition covers equal-type and mixed-type pairs once.
4. Actual triangles follow from edge CN1, not hypergraph linearity alone.
5. Center coefficient sums-3 and other sums0 are integer, not merely modular.
6. Coefficient sum-4 is2 mod3; signs are not interchanged.
7. The finite graph is not asserted14regular or99vertices.
8. Fourier blocks use the actual graph; necessary caps are not sufficient.
9. All14 CN-zero potential added edges are retained before eliminations.
10. A CN-positive nonedge cannot become an edge to evade a CN2 veto.
11. Opposite x and delta3 y-z additions violate fixed nonedge saturation.
12. Opposite leaf additions are matchings; no induced-copy assumption.
13. New edge CN0 inside is allowed, preserving the rejected V1 boundary.
14. Both matching components are independent; f spans0..4.
15. Internal two-walk sums include the2f degree4-to5 increments.
16. Target pair totals count added edges with CN1 rather than CN2.
17. All32 center anchors are distinct and each has at most one extra leaf.
18. Each extra edge consumes two center/opposite-leaf deficits, not one.
19. Remaining51 vertices keep E112 while Q=64-7f varies.
20. The integer tangent includes t0/1; no averaging over a smaller population.

The finite example and specified-configuration exclusion are distinct claims.
No assertion forces the configuration in a target, classifies all twelve-line
dependencies, excludes every cap-compatible core, resolves target existence,
or establishes a search percentage, optimum or computational performance.
No mathematical program, formal prover, external reviewer or new graph
fixture was used by this verifier. ROOT's separately executed V2 set checker
is disclosed supporting provenance; its failed V1 bytes and interpretation
remain preserved, and no old computational gate is transferred.

