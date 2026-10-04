# Candidate: matching constraints for one exterior focal row

As of 2026-10-04T04:45:00+00:00. Discovery author: `/root`.
Status: CANDIDATE, pending a separate written derivation check. This is a
necessary-condition theorem proposal, not a computation or an exclusion.
No search is launched by this note. Historical eight-coordinate matching
experiments remain distinct; this proposed application fixes the new H17 and
the literal 82-copy count witness.

## Exact statement

Let G be any finite simple graph regular of degree k, with exactly one common
neighbor for adjacent vertices and exactly two for nonadjacent vertices. Fix
an induced support S and a vertex x outside S. Write T=N(x) intersect S and
assume that T is independent. For each vertex w outside S write
U_w=N(w) intersect S. Let W=N(x) minus S and s=|T|. Then:

1. Every w in W satisfies |T intersect U_w| in {0,1}. For each u in T,
   exactly one w in W has T intersect U_w={u}.
2. The set P={w in W: |T intersect U_w|=1} has s vertices. Every w in P
   has no neighbor in W. Its unique neighbor inside N(x) is the element
   of T intersect U_w.
3. R=W minus P has k-2s vertices, and G[R] is a perfect matching. All
   other edges among W are absent. In particular k-2s is nonnegative
   and even.
4. Distinct selected vertices w,z in W have |U_w intersect U_z|<=1.
   If that intersection has size one, they are nonadjacent. If they
   form an edge of the matching in R, the intersection is empty.
5. A type U of size at least two can occur at most once among W, even
   when multiple exterior copies of that type exist in the graph.

The conclusion is conditional on an actual target graph, the specified S/x,
and independence of T. It imposes neither an automorphism nor equal neighbor
profiles for vertices of the same exterior type.

## Proposed exact derivation

For every y in N(x), the number of neighbors of y inside N(x) is the common
neighbor count of x,y, hence one. Therefore G[N(x)] is a perfect matching.
Since T is independent, every u in T has its unique matching partner in W.
Two different u cannot have the same partner, because that partner would
have two neighbors inside N(x). No w can meet two elements of T for the
same reason. This proves the first two items. The remaining matching edges
pair the k-2s vertices of R, proving the third.

Any two different w,z in W already have common neighbor x, which is outside
S. Their common support vertices are additional common neighbors. Two or
more would give at least three common neighbors regardless of adjacency.
If there is one common support vertex, w,z cannot be adjacent, since their
common neighbor count would be at least two. A matched pair is adjacent,
so has no common support vertex. Equal types of size at least two have
intersection at least two, which proves the fifth item.

All counting is over the integers; no eigenvalue approximation is used.

## Proposed finite encoding and its limits

Use one binary selection variable q_w for every labeled exterior copy other
than x. The already proposed focal-row equations fix the outside degree and
the common-neighbor sums against every support vertex. A copy with focal
pair bits omitting 1 cannot be selected; a copy with sole bit 1 must be
selected. Such bits remain qualified necessary premises, not sufficient
adjacency decisions.

For copies with |T intersect U_w|=0, introduce a possible matching variable
m_wz only when both endpoints have this property, their support intersection
is empty, and their necessary pair bits permit 1. Impose m_wz=>q_w,q_z.
At most one incident matching variable is true at each endpoint, and
q_w=>at least one incident matching variable is true. These clauses express
exactly one selected matching partner; an empty incident list forces q_w=0.

For any two candidate copies whose support intersection has size at least
two, forbid simultaneous selection. If their necessary pair bits permit
only adjacency, simultaneous selection requires their matching edge. If
they cannot have such a matching edge, forbid simultaneous selection.
For all other selected pairs, the matching variables specify the only
possible edges inside the focal neighborhood. Selection counts for a type
of size at least two are therefore at most one.

A satisfying assignment establishes only a locally compatible selection
and perfect matching for this focal vertex. It need not extend to a
symmetric full exterior graph or satisfy the remaining common-neighbor
equalities. An UNSAT result would reject only this fixed support/count
profile and focal case, after separate encoding/proof verification. It
would not prove unrestricted Conway-99 nonexistence.

Before an application, a distinct reviewer must check this statement and
the proposed implications, falsify them on valid/corrupted fixtures, and
qualify any new implementation. This note does not transfer the old
eight-coordinate filter gates or the plain 18-equation profiler gate.
