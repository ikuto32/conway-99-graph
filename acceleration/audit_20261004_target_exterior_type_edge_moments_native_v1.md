# Independent written audit: exterior profiles and directed edge moments

Native independently checks claim `C-TARGET-EXTERIOR-TYPE-NEIGHBOR-PROFILES-AND-EDGE-MOMENTS`, revision 1, against the complete paper SHA256 `cac608098a8bfee29487bce3c2b40ce86d8b2eb008cd5390b31c3a43b3d599c8` and raw candidate SHA256 `c875c558ba2692d2cdfabce23d344a77a31a56f9a16f32178ca3d398960d10d5`. Structural authored the discovery proof, with Root's earlier block/aggregate outline disclosed. My derivation uses direct common-neighbor counting first, rather than importing a producer computation or assuming agreement proves the statement. This is written exact mathematics, with zero executed mathematical fixtures, formal-proof executions or external reviews. No current integer witness or raw pair population is numerically replayed here.

The exact necessary theorem survives. One unqualified sentence in the rook example needs the qualifier stated below; this changes neither the theorem nor any endpoint bound. The frozen source paper and raw candidate remain unchanged.

## Independent cross-count derivation

Assume a finite simple undirected graph on 99 vertices, degree 14, with adjacent common-neighbor count 1 and nonadjacent common-neighbor count 2. Choose any actual vertex set S and its complement W. All edges on S belong to the induced matrix H. The S-to-W incidence columns form C, and X is the induced adjacency on W.

For u in S and x in W of exact type t_i, the pair u,x is distinct and has adjacency t_i(u). Its common-neighbor count is consequently 2-t_i(u). The common neighbors lying in S are exactly the entries counted by (H t_i)(u). Its common neighbors in W are exactly the outside neighbors z of x whose type contains u. Thus direct disjoint-union counting gives

    sum_{z in N(x) intersect W} t(z)(u)
        = 2-t_i(u)-(H t_i)(u).

This proves b_i=2*1-(H+I)t_i and C X=2J-(H+I)C, with correct dimensions and signs. As a separate consistency check, the entrywise target identity is A^2+A=12I+2J: its diagonal is 14=12+2 and its two off-diagonal cases are 1+1=2 and 2+0=2. Its S-by-W block gives the same equation. Merely using a selected union of edges in place of the actual induced H would omit common neighbors and invalidate this deduction.

There are |t_i| neighbors of x in S, so its outside degree is r_i=14-|t_i|. Partition its outside neighbors into the exact type classes W_j. The integers h_xj are nonnegative, sum to r_i, and have type-incidence sum b_i. When j=i, the actual vertex x is excluded exactly once. Therefore h_xj <= n_j-delta_ij. This is a per-copy equation, required only when n_i>0. An unused type, even one with negative b_i or negative r_i, requires no fictitious copy profile. The labelled universe must include every actual type; excluding types because an earlier numerical vector had zero weight is not permitted.

## Directed aggregation and bit rules

Define y_ij as the total of h_xj over x in W_i. Each edge between different classes contributes once to y_ij and once to y_ji. Therefore y_ij=y_ji off diagonal. Each edge inside W_i contributes twice to y_ii, so y_ii is even. Summing the per-copy equations gives row degree n_i*r_i and point-incidence n_i*b_i. Distinct classes have at most n_i*n_j possible pairs; a single class has n_i*(n_i-1) ordered distinct pairs. These prove the stated capacities, including zero-count and one-copy cases.

Separately justified symmetric allowed-bit sets apply to two distinct vertices. A forced zero gives zero aggregate and per-copy adjacency. A forced one gives every possible edge, hence n_i*n_j off diagonal and n_i*(n_i-1) on the directed diagonal. An empty set forbids distinct copies from coexisting: it forces n_i*n_j=0 for different types, or n_i<=1 for equal types. For a positive type with only one copy the equal-type empty rule has no pair to test. An allowed set {0,1} adds no zero/full condition. A permitted bit is not an existence certificate. In particular, an incompatibility cannot be translated into a unit count sum for arbitrary small, repeated types; the precise distinct-type condition is absence of joint positive multiplicity.

As a direct edge count, the outside degree sum is 14|W|-e(S,W), while e(S,W)=14|S|-2e(H). Hence sum_ij y_ij=14(99-2|S|)+2e(H). Its half is the number of outside edges. For a fixed induced H on 17 points with 36 edges this is (14*65+72)/2=491, conditional on actual occurrence of that induced H. At S empty this recovers all 693 target edges. At S=V the sum is zero, as it must be. Neither endpoint requires positive exterior types.

## Residual selection bounds

First enforce empty-bit coexistence rules. For a positive type i, its potential neighbors consist of literal distinct vertex slots, with a_j=n_j-delta_ij slots in type j. A forced-one class contributes all its slots; a forced-zero class contributes none. Subtract the forced degree f_i and vector g_i from r_i and b_i. Every actual remaining neighborhood is a subset of exactly d_i=r_i-f_i distinct free slots and has total incidence c_i=b_i-g_i.

Consequently d_i must be an integer between zero and the free-pool size M. For a point u, let O be the number of free slots containing u and Z=M-O. Choosing d_i slots takes at least max(0,d_i-Z) and at most min(d_i,O) slots containing u. These are the literal singleton bounds in the paper, with no claim that their independent choices agree.

For any subset Q of S, attach integer weight |t_j intersect Q| to each free slot of type j. The actual Q-incidence c_i(Q) is the weight of a d_i-element slot subset. Sorting all M weights proves that its minimum is at least the sum of the d_i smallest weights and its maximum at most the sum of the d_i largest weights: replacing a chosen larger weight by an unchosen smaller one cannot increase the sum, and the reverse replacement cannot decrease it. The bounds are attained in the unconstrained slot-selection problem but only necessary in the simultaneous incidence problem. Equality is allowed. Empty Q or d_i=0 gives zero endpoints. If d_i<0 or d_i>M, one rejects on degree before claiming endpoints. Self-exclusion removes one slot, not all copies of that type.

For 17 points, sizes 1,2,3 and the full set give exactly 17+136+680+1=834 distinct subsets. This is not all 131072 subsets. Even checking every subset interval would not here establish a common selection or a completed exterior graph.

## Hand checks and attempts to falsify

The rook graph on a 3-by-3 grid has degree 4, adjacentCN1 and nonadjacentCN2. Take S to be its first row. The three unit-vector types each have two copies. For a copy of type e_i, there is one neighbor of each type: its column mate and the two other vertices in its outside row. Thus h=(1,1,1), b=(1,1,1), r=3, and the aggregate is the all2 matrix. Its diagonal 2 counts a single within-class edge twice; each off-diagonal 2 counts two distinct cross edges once. The directed sum 18 gives nine outside edges. This check uses degree 4, not the target degree 14.

The frozen paper's unqualified two-point-Q multiset needs a local qualifier. If Q contains point i of the current e_i type, the own-copy removal leaves overlaps [0,0,1,1,1]; choosing three gives min1/max3 and actual incidence2. If Q excludes i, the own-copy removal removes a zero instead, so the multiset is [0,1,1,1,1]; choosing three gives min2/max3 and the same actual incidence2. Both necessary bounds hold. For Q=S all five weights are1, so both endpoints are3. This is a corrected hand annotation, not an executed fixture or theorem rescope.

Now choose S to be one actual target edge u-v. There is exactly one type11 vertex w. Endpoint degree14 gives n10=n01=12, and the remaining type00 population is72. Type11 has b=0 and outside degree12, so all its 12 exterior neighbors have type00. Simplicity then gives precisely 12 of the 72 type00 copies adjacent to w, with the other 60 nonadjacent.

For type00 set nu=h_x,11 in {0,1}. The point equations give h10=h01=2-nu; the degree equation gives h00=10+nu. Types10 and01 have no neighbor of type11 by symmetry with w, so both have profile (11,1,1,0); w has profile (12,0,0,0). Summing the two type00 subclasses independently gives

    00 row: (60*10+12*11, 60*2+12*1, 60*2+12*1, 12)
          = (732,132,132,12)
    10 row: (132,12,12,0)
    01 row: (132,12,12,0)
    11 row: (12,0,0,0).

The row totals are1008,156,156,12 and the directed sum is1332; half is666. Independently, the target has693 edges, of which one lies in S and26 cross the cut, leaving666. All directed diagonal entries are even. The type00 average of neighbors of type11 is1/6, so a common integer profile for every copy of a type would contradict this conditional target calculation. This proves failure of the equitable shortcut under the target hypotheses, not existence of a target.

I also challenged zero-count types, own-type count1 with an empty allowed set, forced-one equal-type cliques, missing symmetric restrictions, d=0, insufficient pools, closed endpoint equality and selected-edge-union H. None supplies a counterexample within the stated hypotheses. A relaxed aggregate solution remains weaker than individual profiles: row totals and symmetry do not construct each actual neighborhood, and even realized profiles need not satisfy exterior pair common-neighbor counts. The unchecked W block is X^2+X+C^T C=12I+2J. No sufficiency, Schur/rank, fixed472 count-screen outcome or target resolution is asserted.

The maximum positive groups for a 17-point target complement is82 because every positive integer count consumes at least one of its82 vertices. There are at most82*83/2=3403 unordered group-pair variables. For a diagonal variable counting undirected internal edges, coefficient2 is required in its group's degree and incidence row. These are mathematical dimension bounds, not solver costs. No target automorphism, uniform profile, existing witness realization or novel theorem attribution is assumed.

The review covers 20 written boundaries: induced completeness; exact universe; unused types; own-copy removal; outside degree; directCN signs; aggregation symmetry; diagonal parity; all bit-set cases; equal-type distinctness; forced slots; free multiplicity; d=0/insufficient pool; singleton bounds; arbitraryQ exchange bounds; simultaneous-Q insufficiency; both rookQ/self cases; target-edge nonuniformity; empty/fullS; and outside-block insufficiency. Mathematical programs executed0, formal proofs executed0, external reviews0. The proof has no uses_result dependency: accepted fixed type and pair artifacts are future application premises only.
