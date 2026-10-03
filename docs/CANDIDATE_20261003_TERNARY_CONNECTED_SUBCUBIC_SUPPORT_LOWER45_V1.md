# Connected subcubic ternary support needs at least45 vertices

Producer: /root. Frozen version timestamp 2026-10-03T04:51:28+00:00.
Status: CANDIDATE pending independent written verification. No executable
calculation or target resolution is asserted.

## Exact statement

For every symmetric binary zero-diagonal 99-by-99 matrix A with integer
row degree14, put M=(A^2-12I+A-2J) modulo3. Let H be the simple support
graph of its nonzero unordered off-diagonal entries after discarding isolates.
Suppose H is nonempty, connected and has maximum degree at most3. Let m be
its vertex count. If H is bipartite, let p be its larger part's size; otherwise
let p=m. Then

 p*(48-m)<=72.

In particular m>=45, and if H is not bipartite, m>=47. No allowed support
is asserted realizable. No restriction on disconnected or higher-degree
supports and no existence or nonexistence conclusion for the target is claimed.
The support graph is not a prescribed induced adjacency subgraph.

## Complete exact derivation

Define D=A^2-12I+A-2J over the integers, and r_uv=D_uv for u!=v.
Its diagonal is0 and every complete row sums to196-12+14-198=0.
All r_uv>=-2, and a good pair (M_uv=0) has r_uv divisible by3, hence r_uv>=0.
Every nonisolated support vertex has degree at least2. Degree2 requires
opposite incident residues and degree3 requires three equal residues.

AJ=JA=14J implies AD=DA and AM=MA. For S=V(H) and z outside S, the z-row
of M vanishes; the outside row x=(A_zu:u in S) satisfies x*M_S,S=0.
At a degree2 column this equates the two binary support-neighbor coordinates.
At degree3 their sum is divisible by3; a sum of three binary entries is0 or3,
so all three coordinates agree. Thus x is constant along all even walks in H.
Connectedness gives one class if H has an odd cycle, or its two bipartition
classes otherwise. An odd closed walk changes the parity of a connecting walk;
in a bipartite graph an even walk connects precisely vertices in the same part.

Choose P=S in the nonbipartite case, or a larger bipartition class otherwise.
Every vertex of P has the same neighbors outside S. Write their common count
as t. Each vertex of P consequently has d=14-t neighbors within S. Define
a_w to be the number of neighbors of w in P for each w in S. Symmetry gives

 sum(w in S) a_w = p*d.

Counting common-neighbor contributions for unordered pairs within P gives
the exact identity

 sum(u<v in P) CN(u,v) = choose(p,2)*t + sum(w in S) choose(a_w,2).

All terms count literal graph vertices. No independence of neighborhoods,
internal adjacency pattern or automorphism is assumed. Cauchy's inequality
over the m integer values a_w gives sum a_w^2 >= p^2*d^2/m. Hence, for p>=2,

 sum(CN)/choose(p,2) >= t + (p*d^2/m-d)/(p-1)
                       = 14 + p*(d^2/m-d)/(p-1)
                       = 14 - p*m/(4*(p-1))
                         + p*(d-m/2)^2/(m*(p-1))
                       >= 14 - p*m/(4*(p-1)).                  (1)

These are exact rational inequalities; no numerical relaxation or optimality
claim is used. The square is explicitly nonnegative for every integer d.

For the upper bound, in the bipartite case all pairs within P are good.
Each vertex u in P has at most3 bad entries in its complete residual row.
Their total is at least-6, all good entries are nonnegative, and the whole
row sums to0. Thus sum(v in P, v!=u) r_uv<=6. Summing and dividing by2 gives

 sum(u<v in P) r_uv<=3*p.

In the nonbipartite case P=S. Every pair from S to its complement is good
and nonnegative, so the zero complete row instead gives the stronger bound
sum(v in S,v!=u)r_uv<=0. In particular the same upper bound3*p holds.
Since CN(u,v)=r_uv+2-A_uv and A_uv>=0, in either case

 sum(CN)/choose(p,2) <= 2 + 6/(p-1).                           (2)

Combining (1) and (2) and multiplying by the positive4*(p-1) gives
56*(p-1)-p*m <= 8*(p-1)+24, equivalently p*(48-m)<=72.

Minimum support degree2 implies a nonbipartite support has m>=3; a bipartite
one has m>=4, with p>=ceil(m/2). In the nonbipartite case m=3 gives
p*(48-m)=135>72. For every integer4<=m<=44, p>=m/2 and 48-m>0, so

 p*(48-m)>=m*(48-m)/2>=88>72.

The middle bound follows from the concave quadratic on the interval[4,44],
whose endpoint values are both88. This contradicts the necessary inequality
and proves m>=45. For the nonbipartite case p=m, values at m=45,46 are135,92,
both greater than72, so it additionally requires m>=47.

## Independent falsification requirements and scope

Reconstruct row sums, sign rules and the outside commutator equation. Challenge
the binary degree3 inference and even-walk classification. Check that P has
uniform outside degree t, that each internal degree is14-t, and that counting
common neighbors includes vertices in both S and its complement exactly once.
Re-derive the Cauchy bound and completed square over rationals. Check the
bipartite row budget and the separate nonbipartite bound without assuming all
internal pairs are good. Check all signs while multiplying inequalities and
the quadratic endpoint argument; p-1 and m are positive.

Degree4 does not have the binary degree3 propagation rule. Disconnected support
does not justify choosing one even-walk class with the same full S argument.
No assertion covers these cases. Outside neighborhood equality is a derived
property of residual support, not an assumed automorphism of A.

No prior claim is used as a premise: all identities and propagation are
reproduced here. The weaker candidate2fb3397f excluding connected subcubic
supports with at most12 vertices is preserved unchanged. The present broader
statement and exact inequality need a new claim, not a scope-widened revision.
Written controls only; executed fixture count0. External review, formalization,
novelty and realization of any allowed support remain unestablished.
Overall search coverage: UNKNOWN; no validated denominator.
