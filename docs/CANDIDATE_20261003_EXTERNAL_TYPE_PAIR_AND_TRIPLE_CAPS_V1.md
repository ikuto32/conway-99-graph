# Outside type pair and triple caps — candidate v1

Written at 2026-10-03T20:07:36Z. Discovery producer and proof author:
`/root/checkpoint_audit`. ROOT proposed the pair/triple tightening direction;
the set-counting derivation below is written here. This is a source-only
candidate requiring a separate mathematical review by Native or ROOT. It has
no independent verification, ledger registration, executable fixtures or
target-resolution claim.

## Exact statement

Let G be any simple undirected graph of order 99, regular of degree 14, in
which distinct adjacent vertices have exactly one common neighbor and distinct
nonadjacent vertices have exactly two common neighbors. Let S be any subset of
V(G), and let X = V(G) \ S. For each x in X define its outside type
T(x) = N_G(x) intersect S. For each T subset S put

    n_T = |{x in X : T(x) = T}|.

These are actual nonnegative integer multiplicities. Then:

1. For distinct x,y in X, |T(x) intersect T(y)| <= 2. If xy is an edge,
   this intersection has size at most 1. If its size is 2, xy is a nonedge
   and x,y have no common neighbor outside S.
2. If |T| >= 3, n_T <= 1. If |T intersect U| >= 3, at most one outside
   vertex in total can have type T or U: for distinct T,U this says
   n_T + n_U <= 1, and for T=U it says n_T <= 1.
3. For every three-element subset Q of S,

       sum_{T subset S, Q subset T} n_T <= 1.

For |S|=17 there are exactly 17*16*15/6 = 680 such triple inequalities.
Every genuine target graph therefore satisfies them in addition to any valid
degree and first/second moment equations for its outside types. No particular
induced graph on S, residual-support condition or prior moment census is an
assumption of this statement.

## Derivation

For distinct exterior vertices x,y, the set of their common neighbors lying
in S is exactly

    N_G(x) intersect N_G(y) intersect S = T(x) intersect T(y).

It is a subset of their complete common-neighbor set. The target conditions
give size one for an edge and size two for a nonedge. This proves the two
upper bounds in item 1. If the intersection in S has size two, adjacency
would violate the edge bound; hence x,y are nonadjacent. Their two common
neighbors have already been counted in S, leaving none in X.

If two distinct outside vertices have the same type T of size at least three,
they have at least three common neighbors in S. This contradicts item 1.
Likewise, two distinct outside vertices of types T and U with an intersection
of size at least three would contradict item 1. This proves item 2, with
separate accounting for T=U so a multiplicity is never counted twice.

Fix a three-element Q subset S. The sum in item 3 counts the outside vertices
adjacent to all three members of Q, once each: the types partition X. If this
sum were at least two, select two distinct counted vertices x,y. All three
members of Q would be common neighbors of x,y, contradicting item 1. Thus
the sum is at most one. This proof uses actual vertex counting, not a
numerical optimizer or an assumption that fractional variables are vertices.

## Linear relaxation and limits

Each triple inequality is linear with integer coefficients 0 or 1 and right
hand side 1. It is valid for every actual integer type vector and hence for
every convex combination of such vectors. Adding these inequalities to a
necessary rational relaxation is consequently sound. It does not assert that
the resulting polyhedron is the convex hull of realizable graphs.

The triple inequalities imply n_T <= 1 for |T|>=3, since such a T contains
a Q and all multiplicities are nonnegative. They also imply n_T+n_U<=1 for
distinct T,U sharing a triple. Fractional points may still assign, for
example, n_T=n_U=1/2 to incompatible types; satisfying this linear inequality
does not assert that both types can be simultaneously realized as vertices.
Nor is every pairwise-conflict clique required to share a single triple.

Types of size zero, one or two are not capped at one by this lemma. An
intersection of size one does not determine adjacency, and an intersection
of size zero does not determine adjacency. The conclusion applies only to
distinct exterior vertices; setting x=y would incorrectly bound a vertex's
degree. A two-element common subset would give no analogous universal
at-most-one inequality because nonadjacent distinct vertices may share two
neighbors. None of these statements reconstructs the outside edges, proves
integrality of a moment vector, proves a graph completion, excludes the fixed
17-point family, or resolves Conway-99.

## Written boundary checks and provenance

Eight boundaries were checked in the proof: distinctness of x,y; both edge
and nonedge common-neighbor totals; overlap exactly two; same-type versus
distinct-type multiplicity; small types |T|<=2; Q of exactly three points;
arbitrary S without an induced-graph premise; and fractional relaxation versus
actual integer vertex counts. These are written logical checks, with zero
executed fixtures, zero graph realizations, zero formal-proof checks and zero
external reviews. No numerical or exact primal file was read for this lemma.

There are no `uses_result` dependencies: the target common-neighbor conditions
are reproduced as assumptions and the proof is direct. The proposed next
experiment would require a new model, new applicable controls, an independent
raw certificate checker and a separate per-invocation authorization. This
candidate grants none of those execution or ledger/index permissions.
