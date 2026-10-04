# Candidate: exterior neighbor profiles and directed edge moments

Claim `C-TARGET-EXTERIOR-TYPE-NEIGHBOR-PROFILES-AND-EDGE-MOMENTS`, revision1.
SOURCE_ONLY / CANDIDATE / NEEDS_RECHECK. ROOT proposed the block identity,
aggregate edge totals and next witness screen. Structural reconstructed the
proof, diagonal conventions, mandatory-copy capacity bounds and the conditional
two-point counterattack against equitable profiles. These shared origins are
explicit; agreement is not independent approval. No mathematical program,
count witness, solver, formal-proof execution or external review was performed.

## Complete conditional statement

Let G be any finite simple undirected graph with99 vertices, every degree14,
one common neighbor for an adjacent distinct pair and two for a nonadjacent
distinct pair. Let S be any subset of its vertices; W is its complement.
Use the actual complete induced adjacency H=A[S,S], the binary S-to-W
adjacency C, and the complete W-to-W adjacency X. In this order,

    A = [ H    C  ]
        [ C^T  X  ].

Label the distinct exact exterior types t_i in {0,1}^{|S|}, with vertex sets
W_i={x in W:C[:,x]=t_i} and integer multiplicities n_i=|W_i|. A larger labelled
type universe can include zero-count types, but must contain every actual
type; no omitted type or earlier zero LP weight is presumed absent. Put

    r_i = 14-|t_i|,
    b_i = 2*1-(H+I)t_i.

Then the following are necessary.

1. The exact cross block equation is CX=2J-(H+I)C. For each x in W_i, its
   integer neighbor profile h_{xj}=|N(x) intersect W_j| satisfies

       sum_j h_{xj}=r_i,
       sum_j t_j(u)h_{xj}=b_i(u)  for every u in S,
       0<=h_{xj}<=n_j-delta_ij.

   These per-copy statements are required only when n_i>0. An unused type
   with a negative b_i coordinate is not thereby a contradiction.

2. Define directed aggregate totals y_ij=sum_{x in W_i}h_{xj}. Then

       y_ij=y_ji for i!=j; y_ii is a nonnegative EVEN integer,
       sum_j y_ij=n_i*r_i,
       sum_j t_j(u)y_ij=n_i*b_i(u),
       0<=y_ij<=n_i*n_j for i!=j,
       0<=y_ii<=n_i*(n_i-1).

   An off-diagonal y_ij counts each W_i-to-W_j edge once. A diagonal y_ii
   counts each within-W_i edge twice. One must not halve the latter inside
   the row equations or double the former.

3. Suppose symmetric sets B_ij subset {0,1} are separately justified necessary
   adjacency-bit sets for distinct exterior vertices of types i,j, including
   equal types interpreted as TWO distinct vertices. Then B_ij={0} forces
   y_ij=0; B_ij={1} forces y_ij=n_i*n_j off diagonal and
   y_ii=n_i*(n_i-1) on diagonal. If B_ij is empty, coexistence is impossible:
   n_i*n_j=0 off diagonal and n_i*(n_i-1)=0 on diagonal. Set {0,1} imposes
   no additional zero/full rule. Every h_{xj} obeys the corresponding zero
   or full-copy rule. A mere allowed bit is never a sufficiency statement.

4. The residual mandatory/free copy bounds below hold for EVERY Q subset S,
   separately for each positive type i. Thus singleton/pair/triple/full-S
   subsets give cheap exact necessary screens on an integer count witness.
   These screens and the aggregate totals are not sufficient for a completion.

The statement is universal conditional necessary algebra, not a target
existence/nonexistence claim, a fixed17 enumeration or an assertion that any
integer vector satisfies the constraints. It does not impose a nontrivial
automorphism or a uniform/equitable partition by types.

## Direct proof of the block and profile identities

The target hypotheses give A^2+A-12I-2J=0 entry by entry. On the diagonal,
degree14 gives14-12-2=0. Off diagonal, an edge gives1+1-2=0 and a nonedge
gives2+0-2=0. The S-by-W block of this identity is HC+CX+C-2J=0, proving
the stated equation; the identity block has zero off-block entries.

Its column belonging to x of type t_i reads

    sum_{z in W} C[:,z] X[z,x] = b_i.

Since X is symmetric binary with zero diagonal, the left side counts the
S incidences of the exterior neighbors of x, once each. Its exterior degree
is14-|t_i|, since |t_i| neighbors lie in S. Partition these neighbors into
the exact type classes to obtain the profile equations. The own copy x must
be removed from its class pool, giving n_j-delta_ij rather than n_j.

Sum over x in W_i to obtain both aggregate moment equations. Symmetry pairs
the two directions of each cross-class edge. Every internal edge contributes
two directed incidences, proving even diagonal entries. The capacities count
all possible distinct cross pairs or all ordered internal pairs. Valid
bit-set rules apply to every such pair independently, so a forced edge bit
requires the entire corresponding complete bipartite graph or internal clique.
Empty sets force a zero population of relevant distinct pairs, even if one
equal-type vertex may still exist. No profile equality across copies was used.

As a consistency check,

    sum_ij y_ij=14|W|-sum_i n_i|t_i|=14(99-2|S|)+2e(H).

Its half is the number of outside edges. For a fixed17 edge union with36
internal edges this is491 outside edges, conditionally on an actual target
having that exact induced H. No target occurrence of this H is asserted.

## Mandatory-copy capacity bounds, without a solver

First enforce the empty-bit coexistence/multiplicity rules. Fix n_i>0 and
write a_j=n_j-delta_ij. Let F_i be the classes with B_ij={1}, and let L_i
be the classes with B_ij={0,1}. Classes with no allowed edge bit contribute
zero. All a_j vertices in each forced class are mandatory neighbors. Set

    f_i=sum_{j in F_i}a_j,
    g_i=sum_{j in F_i}a_j*t_j,
    d_i=r_i-f_i,   c_i=b_i-g_i.

Every free neighbor set must choose EXACTLY d_i distinct copies from the
free pool, in which type j occurs a_j times. In particular

    0<=d_i<=sum_{j in L_i}a_j,
    max(0,d_i-sum_{j in L_i}a_j*(1-t_j(u)))
        <=c_i(u)<=min(d_i,sum_{j in L_i}a_j*t_j(u)).

For arbitrary Q subset S, form the multiset containing a_j repetitions of
the integer |t_j intersect Q| for every free class j. Among all d_i-copy
selections from this multiset, the minimum overlap sum is the sum of its
d_i smallest entries and the maximum is the sum of its d_i largest entries.
Therefore sum_{u in Q}c_i(u) must lie in that CLOSED integer interval. For
d_i=0 both sums are0. If the free pool is too small, the degree bound fails
before any min/max sum is claimed. Duplicated type copies are distinct slots;
one never removes an entire type merely to exclude the particular copy x.

These inequalities follow by ordering integer slots, not by numerical
optimization or an assumption of independently selectable point incidences.
They are only necessary: different Q screens can be attained by incompatible
neighbor selections. A pass does not construct one common neighbor set.
For |S|=17, testing all nonempty Q of sizes1,2,3 and Q=S gives
17+136+680+1=834 subsets. This finite selection does not test all2^17 subsets.

## Written rook9 algebra check

This is a genuine small graph for hand algebra, not a99/14 target. Label its
vertices (row,column) with row,column in {0,1,2}; distinct vertices are
adjacent when they share a row or column. Every degree is4. Adjacent pairs
have the third point in their row/column as their sole common neighbor;
nonadjacent pairs have the two opposite corners as their common neighbors.
Thus A^2+A-2I-2J=0. Its cross-block identity is unchanged; only the profile
degree formula uses4 instead of14.

Take S to be the first row. H=J_3-I_3; the six exterior vertices have types
e_0,e_1,e_2 with two copies each. For each i,
b_i=2*1-(H+I)e_i=1 and exterior degree3. Each exterior vertex has one neighbor
of each type: one in its own column and one of each other type in its own row.
The aggregate y is the3-by-3 all2 matrix. Its diagonal2 equals twice one
internal edge; each off-diagonal2 represents two cross edges, below capacity4.
There are9 exterior edges, as half of the total18 directed incidences.
For Q consisting of two S points, the available free slot overlaps are
0,0,1,1,1; choosing3 has min1/max3 and required sum2. For Q=S, every slot is1,
so the min/max are both3, agreeing with the required sum3.

## Conditional target counterattack: equitable profiles would be wrong

Take S to be ONE actual edge uv of a hypothetical target. The unique common
neighbor w has type11. The type counts in order00,10,01,11 are exactly
72,12,12,1: each endpoint has13 exterior neighbors, one of them w.
The type11 column has b=0 and exterior degree12. Hence all12 exterior
neighbors of w have type00. Exactly12 of the72 type00 vertices have
h_{x,11}=1 and the other60 have h_{x,11}=0. Uniform integer profiles inside
the type00 class are impossible; y_{00,11}/72=12/72=1/6 is not an integer.
This is forced by the conditional target assumptions, not a constructed target.

For a type00 vertex, put nu=h_{x,11} in {0,1}. Its full profile is

    (h_00,h_10,h_01,h_11)=(10+nu,2-nu,2-nu,nu).

The type10 and01 vertices have profiles(11,1,1,0), and w has(12,0,0,0).
Consequently the directed aggregate is

        00   10  01  11
    00  732  132 132 12
    10  132   12  12  0
    01  132   12  12  0
    11   12    0   0  0.

Rows have totals1008,156,156,12, their sum is1332, and half is666 outside
edges. The full target693 edges minus the uv edge and26 S-to-W edges is
also666. All diagonal totals are even. This hand reconstruction falsifies
the shortcut of imposing one common integer h_i=y_i/n_i on every type;
it does not establish the existence of a matrix completing these counts.

## Usefulness, exact scope and limits

An independently checked integer count witness can first be screened using
the per-copy degree and834 subset intervals without a solver. Any exact
failure rules out ONLY completion of that particular count vector on the
fixed induced H and exact justified bit sets. If all pass, a subsequent
aggregate integer feasibility question uses at most82 positive type groups
for a fixed17 target complement. Using one variable per unordered group pair
requires at most82*83/2=3403 variables; a diagonal variable counts undirected
internal edges, so its coefficient is2 in every directed row equation.
For positive group i, there are at most18 row equations (degree plus17
point-incidence equations), symmetry is built into shared cross variables,
and the zero/full-edge capacities are explicit. These are dimension bounds,
not executed costs, feasibility results or a promise of cheap MIP convergence.

Passing aggregate feasibility does not prove individual-copy profiles,
simple-graph realization of blocks, exterior pair common-neighbor counts,
the W-by-W block X^2+X+C^TC=12I+2J, full Schur PSD/ranks or a99-vertex target.
A numerical infeasible result alone is not a mathematical veto: any later
negative computational conclusion needs a sound independently checked exact
certificate or exhaustive proof for its complete declared finite scope.

The main algebra and subset bounds are proved directly from assumptions and
have no uses_result dependency. Application to the actual fixed17/472 data
requires its independently accepted induced graph/type-universe and complete
pair-bit artifact. Those are APPLICATION premises, not newly approved here:
the pair report is ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218
and ROOT acceptance39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586.
The old pair/triple cap lemma and dual-Gram conditional theorem are compatible
sources of necessary bit restrictions; no pairwise sufficiency is inferred.
Existing moments/equitable special cases overlap historical research. A
limited written archive search found an equitable partition for a special
weight36 configuration, not a general permission to assume equitable types.
No novelty claim about block multiplication or graph edge bookkeeping is made.

Written falsification boundaries cover induced H versus selected edge union;
arbitrary/empty/full S; exact universe coverage; zero-count types; own-copy
removal; actual degree; cross-block signs; diagonal parity; off-diagonal
double-counting; all four bit sets; equal-type distinctness; forced/free slots;
empty pool/d=0; closed interval equality; simultaneous-Q insufficiency;
the rook9 degree4 distinction; target S=edge nonuniformity; and full outside
identity not checked by an aggregate witness. These are18 written boundaries,
zero executed fixtures, zero formal-proof executions and zero external reviews.
No ledger/index/publication packet or availability status is modified.
